"""Tela local do Radar: um servidor pequeno só no próprio computador (127.0.0.1), biblioteca padrão.

A página escolhe os tribunais, manda rodar e mostra a lista. A tela não manda nada para fora; o programa fala
com o DJEN, a Receita e a SolverONE (licença, cadastro, totais por situação), como está em SEGURANCA.md. Só aceita pedidos do navegador desta máquina, vindos da
própria página (cabeçalho X-LexSuite); outro site aberto no navegador não consegue mandar rodar.
"""

import datetime as dt
import json
import os
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from . import VERSAO, agendar, armazenamento, assinatura, atualizar, banco as bd, cnpj, compartilhar, config, conta, preferencias, radar, rede, tribunais
from . import classificar as cl
from . import planilha as planilha_mod

PORTAS = range(8765, 8776)
PAPEIS = ("Sócio ou sócia", "Advogado ou advogada", "Estagiário ou estagiária", "Equipe administrativa")
SEM_PAPEL = "Prefiro não informar"


def papel_valido(corpo):
    """Função escolhida na tela: uma da lista, "Prefiro não informar" ou, com "Outra", o texto digitado (até 40)."""
    p = corpo.get("papel")
    if p in PAPEIS or p == SEM_PAPEL:
        return p
    if p == "Outra":
        texto = " ".join(str(corpo.get("papel_outro") or "").replace("<", "").replace(">", "").split())[:40]
        return texto
    return ""

# O manual fala com a pessoa pelo papel dela (texto curto; o manual inteiro continua valendo para todos).
PARA_VOCE = {
    "Sócio ou sócia": ["A lista é um catálogo de oportunidades, não uma recomendação: a regra separa ações novas contra empresas e deixa a triagem com você.",
                       "Para saber se o robô está rodando, basta a linha \"Última atualização\" no alto da tela ou a aba oculta Log da planilha.",
                       "O uso dos contatos das empresas e dos nomes de sócios é decisão sua e do compliance; o ajuste \"Mostrar sócios e administradores\" desliga esses nomes.",
                       "Nada aqui usa inteligência artificial nem tem custo por uso: o robô lê fontes públicas e roda no seu computador."],
    "Advogado ou advogada": ["Clique na linha e a ficha abre: vara, rito, data do Diário, empresa, atividade, porte, capital social e contatos do cadastro público.",
                             "O valor da causa fica atrás do captcha do PJe: \"Abrir consulta no PJe\", cole o número, veja o valor e digite na ficha. Ele sai na planilha exportada.",
                             "Use o status (visto, em contato, descartado) para não repassar a mesma empresa duas vezes; o filtro \"Acima de\" segue o valor mínimo dos Critérios da lista (Configurações).",
                             "Rito ordinário indica causa acima de 40 salários mínimos; sumaríssimo, até 40. É o primeiro corte de valor que o Diário permite."],
    "Estagiário ou estagiária": ["A rotina sugerida: de manhã, abrir a tela, conferir \"Última atualização\" e passar pela lista marcando o status de cada linha.",
                                 "Para as linhas com \"valor a conferir\", abrir a consulta no PJe, resolver o captcha e digitar o valor da causa na ficha.",
                                 "Cadastrar em Configurações → Critérios da lista as empresas que a equipe pedir para não aparecer (nome como está no Diário, ou CNPJ, e o motivo).",
                                 "Não é preciso mexer nas abas ocultas da planilha: elas são do suporte."],
    "Equipe administrativa": ["A planilha (LexSuiteONE - Trabalhista.xlsx, na pasta escolhida) é sua, para consultar. Os critérios (valor mínimo, clientes e empresas que não devem aparecer) se mudam em Configurações → Critérios da lista.",
                              "O RADAR lê sozinho nos dias e horários de Configurações (numa instalação nova, de segunda a sexta, às 20h e às 8h); se o computador estava desligado, a leitura acontece quando ele ligar.",
                              "Se a planilha estiver aberta e travada na hora de uma rodada, o robô grava na próxima. Nada se perde.",
                              "Avise o suporte quando a tela mostrar \"robô desligado\", \"precisa atualizar\" ou quando a lista vier vazia dois dias úteis seguidos."],
}


class Estado:
    """O que a tela pergunta a cada 2 segundos enquanto o robô roda."""

    def __init__(self, eco=None, arquivo=None, origem="botão"):
        self.lock = threading.Lock()
        self.eco = eco  # janela preta: cada passo da leitura aparece também ali, com a hora
        self.arquivo, self.origem = arquivo, origem  # 0.7.14: andamento em arquivo, para a tela ver a leitura agendada
        self.atrasada = ""  # 0.7.15: o horário perdido ("08:00") quando a leitura agendada roda depois da hora

        self.rodando = False
        self.progresso, self.total_trib, self.tribs_vistos = 0, 0, set()
        self.mensagens = []
        self.inicio = self.fim = None
        self.situacao = None
        self.erro = None
        self.erro_info = None  # 0.7.13: {causa, pt, en, detalhe}: a tela mostra o texto claro e esconde o técnico

    def arquivo_parar(self):
        return os.path.join(os.path.dirname(self.arquivo), "parar.json") if self.arquivo else ""

    def parar(self):
        """True se alguém pediu "Interromper" depois que esta leitura começou (vale para a tela e para a agendada)."""
        caminho = self.arquivo_parar()
        if not caminho or not self.rodando:
            return False
        try:
            with open(caminho, encoding="utf-8") as f:
                pedido = json.load(f)
            return str(pedido.get("quando") or "") >= str(self.inicio or "")
        except (OSError, ValueError, AttributeError):
            return False

    def aviso(self, msg):
        hora, texto = dt.datetime.now().strftime("%H:%M:%S"), str(msg).strip()
        with self.lock:
            self.mensagens.append({"hora": hora, "texto": texto})
            del self.mensagens[:-80]
            self._progredir(texto)
        self._eco(f"  {hora}  {texto}")
        self._gravar_andamento()

    def _gravar_andamento(self):
        """Grava saida/leitura.json (rodando, progresso, últimas mensagens, pid, origem, batida). Nunca derruba a leitura."""
        if not self.arquivo:
            return
        try:
            with self.lock:
                d = {"rodando": self.rodando, "progresso": self.progresso, "inicio": self.inicio, "fim": self.fim,
                     "mensagens": self.mensagens[-6:], "pid": os.getpid(), "origem": self.origem, "atrasada": self.atrasada,
                     "batida": dt.datetime.now().isoformat(timespec="seconds")}
            os.makedirs(os.path.dirname(self.arquivo), exist_ok=True)
            tmp = self.arquivo + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False)
            os.replace(tmp, self.arquivo)
        except (OSError, ValueError):
            pass

    def _progredir(self, texto):
        """Porcentagem estimada a partir dos passos que a leitura já informa: tribunais (5 a 60%), consultas à Receita
        (60 a 95%), gravação (95 a 99%). Não é tempo: o Diário e a Receita variam muito."""
        import re
        m = re.search(r"Radar: lista de distribuição de (.+?) \(", texto)
        if m:
            self.total_trib = max(1, len([x for x in m.group(1).split(",") if x.strip()]))
            self.tribs_vistos, self.progresso = set(), 5
            return
        m = re.search(r"[Cc]aderno (\S+) ", texto)
        if m and getattr(self, "total_trib", 0):
            self.tribs_vistos.add(m.group(1))
            self.progresso = max(self.progresso, 5 + int(55 * min(1, len(self.tribs_vistos) / self.total_trib)))
            return
        if texto.startswith("Consultando a Receita"):
            self.progresso = max(self.progresso, 60)
            return
        m = re.search(r"Receita: (\d+) de (\d+)", texto)
        if m and int(m.group(2)):
            self.progresso = max(self.progresso, 60 + int(35 * int(m.group(1)) / int(m.group(2))))
            return
        if "publicações lidas" in texto or "Planilha" in texto or "planilha" in texto:
            self.progresso = max(self.progresso, 95)

    def _eco(self, linha):
        if self.eco:
            try:
                self.eco(linha)
            except (OSError, ValueError, UnicodeError):  # a janela preta nunca derruba a leitura
                pass

    def como_dict(self):
        with self.lock:
            return {"rodando": self.rodando, "progresso": min(99, self.progresso) if self.rodando else (100 if self.fim else 0),
                    "mensagens": list(self.mensagens[-15:]), "inicio": self.inicio,
                    "fim": self.fim, "situacao": self.situacao, "erro": self.erro, "erro_info": self.erro_info,
                    "origem": self.origem, "atrasada": self.atrasada, "parando": self.parar() if self.rodando else False}

    def comecar(self):
        with self.lock:
            if self.rodando:
                return False
            self.rodando, self.mensagens, self.erro, self.erro_info = True, [], None, None
            self.progresso, self.total_trib, self.tribs_vistos = 1, 0, set()
            self.inicio, self.fim = dt.datetime.now().isoformat(timespec="seconds"), None
        try:  # um pedido de parada antigo não vale para esta leitura
            if self.arquivo_parar() and os.path.exists(self.arquivo_parar()):
                os.remove(self.arquivo_parar())
        except OSError:
            pass
        self._eco("")
        self._eco(f"  ===== Leitura começou às {dt.datetime.now():%H:%M} =====")
        self._gravar_andamento()
        return True

    def terminar(self, situacao=None, erro=None, info=None):
        with self.lock:
            self.rodando = False
            self.fim = dt.datetime.now().isoformat(timespec="seconds")
            if situacao:
                self.situacao = situacao
            self.erro = erro
            self.erro_info = info
        self._gravar_andamento()
        fim = f"  ===== Leitura terminou às {dt.datetime.now():%H:%M}"
        interrompida = (info or {}).get("causa") == "interrompida"
        self._eco(fim + (": interrompida a pedido =====" if interrompida else (f" com erro: {erro} =====" if erro else (f": {situacao.get('pt', '')} =====" if situacao else " ====="))))


def processo_vivo(pid):
    """True se o processo existe. No Windows usa OpenProcess (os.kill no Windows ENCERRARIA o processo)."""
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    if pid <= 0:
        return False
    if os.name == "nt":
        try:
            import ctypes
            k = ctypes.windll.kernel32
            h = k.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
            if not h:
                return False
            codigo = ctypes.c_ulong()
            k.GetExitCodeProcess(h, ctypes.byref(codigo))
            k.CloseHandle(h)
            return codigo.value == 259  # STILL_ACTIVE
        except Exception:  # noqa: BLE001 - na dúvida, considera vivo e deixa a batida decidir
            return True
    try:
        os.kill(pid, 0)  # nosec - sinal 0 só confere se existe (fora do Windows)
        return True
    except PermissionError:  # existe, mas é de outro usuário
        return True
    except OSError:
        return False


# --- 0.7.33: chamados pelo AssistONE (desenho da Arquitetura, seção 2) -----------------------------------------------
# Decisão do dono (12/Nov): o chamado fica implementado, mas ESCONDIDO na 0.7.33 (o escritório não abre chamado).
# Uma chave só: desligada, a tela não mostra o chamado, as rotas recusam e a fila não é enviada.
CHAMADO_LIGADO = False
_TRAVA_CHAMADOS = threading.Lock()
MOTIVOS_CHAMADO = {
    "limite": ("Limite de chamados de hoje atingido (5 por computador). Tente amanhã ou escreva para judicial@solverone.com.br.",
               "Today's ticket limit was reached (5 per computer). Try tomorrow or write to judicial@solverone.com.br."),
    "codigo_invalido": ("Para abrir um chamado, o código de cliente precisa estar conferido (Configurações → Licença e termos).",
                        "To open a ticket, the client code must be confirmed (Settings → Licence and terms)."),
    "desativado": ("A licença está desativada. Escreva para judicial@solverone.com.br.", "The licence is deactivated. Write to judicial@solverone.com.br."),
    "dados_invalidos": ("Pedido incompleto: escolha o assunto e escreva a mensagem.", "Incomplete request: choose the subject and write the message."),
}
MOTIVOS_CHAMADO["codigo_desconhecido"] = MOTIVOS_CHAMADO["codigo_invalido"]


def _lista_json(arq):
    try:
        with open(arq, encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, list) else []
    except (OSError, ValueError):
        return []


def _gravar_lista_json(arq, lista):
    os.makedirs(os.path.dirname(arq), exist_ok=True)
    tmp = arq + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(lista[-200:], f, ensure_ascii=False, indent=1)
    os.replace(tmp, arq)


def guardar_chamado(pasta, dados, numero):
    """Meus chamados: número, data, assunto e o começo do texto, só neste computador (saida/chamados.json)."""
    arq = os.path.join(pasta, "saida", "chamados.json")
    lista = _lista_json(arq)
    lista.append({"numero": numero, "quando": dt.datetime.now().astimezone().isoformat(timespec="minutes"),
                  "categoria": dados.get("categoria", ""), "resumo": str(dados.get("texto", ""))[:80]})
    _gravar_lista_json(arq, lista)


def enviar_pendentes(pasta, cfg, enviar=None):
    """Chamados que ficaram sem internet saem quando houver conexão, com o mesmo cliente_id (nunca duplicam).
    Devolve quantos ainda faltam."""
    arq = os.path.join(pasta, "saida", "chamados-pendentes.json")
    with _TRAVA_CHAMADOS:
        fila = _lista_json(arq)
        if not fila:
            return 0
        resto = []
        for i, dados in enumerate(fila):
            r = (enviar or conta.enviar_chamado)(cfg, VERSAO, dados)
            if r.get("ok"):
                guardar_chamado(pasta, dados, r.get("numero"))
            elif r.get("sem_internet"):
                resto = fila[i:]
                break
            # recusado (limite, licença): sai da fila; a pessoa vê o motivo ao abrir outro chamado
        _gravar_lista_json(arq, resto)
        return len(resto)


def leitura_em_outro_processo(arquivo, minutos=45):
    """A leitura que está rodando em OUTRO processo (a agendada pelo Windows, por exemplo), ou None."""
    try:
        with open(arquivo, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return None
    if not isinstance(d, dict) or not d.get("rodando") or int(d.get("pid") or 0) == os.getpid():
        return None
    try:
        batida = dt.datetime.fromisoformat(str(d.get("batida")))
    except ValueError:
        return None
    if (dt.datetime.now() - batida).total_seconds() > minutos * 60 or not processo_vivo(d.get("pid")):
        return None
    return d


_TRAVA_REGRAS = radar.TRAVA_REGRAVAR  # revisão da 0.7.29: a mesma trava de toda regravação da planilha (RLock)


class Servidor(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, endereco, pasta):
        super().__init__(endereco, Tratador)
        self.pasta = pasta
        self.arquivo_andamento = os.path.join(pasta, "saida", "leitura.json")
        self.estado = Estado(eco=print, arquivo=self.arquivo_andamento, origem="botão")
        self.versao_cache = None
        self.caminho_config = os.path.join(pasta, "config.json")
        self.caminho_db = os.path.join(pasta, "lexsuite.db")
        self.modelo = os.path.join(pasta, "radar_modelo.html")
        self.hist = {}  # 0.7.18: andamento das estatísticas dos meses anteriores
        self._ultima_cache = None  # 0.7.19: (data do arquivo do banco, última leitura) para a tela
        self.hist_trava = threading.Lock()
        import time as _t
        self.ultimo_pedido = _t.monotonic()  # 0.7.16: a janela preta fecha sozinha quando a tela some (ver vigiar_tela)

    def config(self):
        return config.carregar(self.caminho_config, aviso=lambda *_: None)

    def estado_atual(self):
        """O estado desta tela; se ela não está lendo, mas há leitura agendada (ou outra janela) rodando agora noutro
        processo, mostra essa leitura (a tela exibe a barra e desliga "Ler o Diário agora")."""
        d = self.estado.como_dict()
        if not d["rodando"]:
            fora = leitura_em_outro_processo(self.arquivo_andamento)
            if fora:
                d.update({"rodando": True, "externa": True, "origem": fora.get("origem", ""), "inicio": fora.get("inicio"),
                          "atrasada": fora.get("atrasada", ""), "parando": os.path.exists(os.path.join(os.path.dirname(self.arquivo_andamento), "parar.json")),
                          "progresso": min(99, int(fora.get("progresso") or 1)), "mensagens": fora.get("mensagens") or []})
        if not d["rodando"] and not d.get("situacao") and not d.get("erro"):
            ult = self.ultima_do_banco()
            if ult:
                d["situacao"] = ult
        return d

    def ultima_do_banco(self):
        """0.7.19: depois de reiniciar (atualização), a última leitura vem do banco, não "Ainda não leu". Consulta só
        leitura, guardada até o banco mudar (a tela pergunta o estado a cada poucos segundos)."""
        import pathlib
        import sqlite3
        try:
            marca_ = os.path.getmtime(self.caminho_db)
        except OSError:
            return None
        if self._ultima_cache and self._ultima_cache[0] == marca_:
            return self._ultima_cache[1]
        sql = "SELECT quando, resumo FROM execucoes WHERE tipo = 'radar' ORDER BY quando DESC LIMIT 10"
        linhas = None
        # 1º só leitura pela URI (caminho com # ou ? vai codificado); 0.7.21: pasta em rede (\\servidor\...) não vira URI
        # que o SQLite aceite, então tenta o jeito comum (o arquivo já existe, nada é criado)
        for abrir in (lambda: sqlite3.connect(pathlib.Path(self.caminho_db).resolve().as_uri() + "?mode=ro", uri=True, timeout=1),
                      lambda: sqlite3.connect(self.caminho_db, timeout=1)):
            try:
                con = abrir()
                try:
                    linhas = con.execute(sql).fetchall()
                finally:
                    con.close()
                break
            except (sqlite3.Error, ValueError, OSError):
                continue
        if linhas is None:
            return None
        achou = None
        for quando, dados in linhas:
            try:
                e = json.loads(dados or "{}")
            except ValueError:
                continue
            if e.get("resultado") == "ok" or e.get("lidas"):
                achou = {"quando": quando or "", "pt": f"{e.get('lidas', 0)} publicações lidas; {e.get('novas', 0)} ações novas contra empresas.",
                         "en": f"{e.get('lidas', 0)} notices read; {e.get('novas', 0)} new lawsuits against companies."}
                break
        self._ultima_cache = (marca_, achou)
        return achou

    def planilha_depois(self, intervalo=120, limite_s=7200, primeira=5):
        """0.7.14: regrava a planilha em segundo plano; se ela estiver aberta (travada), tenta de novo a cada 2 minutos
        por até 2 horas e grava sozinho quando o Excel fechar. Uma tentativa por vez."""
        if getattr(self, "_planilha_tentando", False) or not compartilhar.pasta_base(self.config()):
            return False
        self._planilha_tentando = True

        def alvo():
            import time as _t
            inicio = _t.time()
            _t.sleep(primeira)
            try:
                while _t.time() - inicio < limite_s:
                    try:
                        if self.estado.rodando:  # a leitura em andamento grava a planilha no fim
                            _t.sleep(intervalo)
                            continue
                        if radar.regravar_planilha(self.config(), bd.Banco(self.caminho_db), self.pasta, VERSAO, lambda *_: None):
                            if self.estado.situacao:
                                self.estado.situacao.pop("aviso_planilha", None)
                                self.estado.situacao["planilha_gravada_em"] = dt.datetime.now().isoformat(timespec="minutes")
                            return
                    except Exception:  # noqa: BLE001 - tenta de novo no próximo intervalo
                        pass
                    _t.sleep(intervalo)
            finally:
                self._planilha_tentando = False

        threading.Thread(target=alvo, daemon=True, name="planilha").start()
        return True

    def rodar(self, dias=None):
        """Começa uma rodada numa thread. Devolve False se já há uma rodando (aqui ou agendada, em outro processo)."""
        if not _TRAVA_REGRAS.acquire(blocking=False):  # 0.7.29: não começa enquanto as regras estão sendo gravadas
            return False
        try:  # dentro da trava: o "Salvar regras" não pode passar entre a conferência e o começo da leitura
            if leitura_em_outro_processo(self.arquivo_andamento) or not self.estado.comecar():
                return False
        finally:
            _TRAVA_REGRAS.release()

        def alvo():
            try:
                cfg = self.config()
                banco = bd.Banco(self.caminho_db)
                situacao = radar.executar(cfg, banco, self.estado.aviso, self.pasta, dias=dias, versao=VERSAO,
                                          caminho_config=self.caminho_config, parar=self.estado.parar)
                self.estado.terminar(situacao)
                if situacao.get("aviso_planilha"):
                    self.planilha_depois()
                if cfg["radar"].get("avisar_ao_terminar", True):
                    agendar.notificar(marca(self.pasta).get("nome", "RADAR JUDICIAL"), agendar.texto_aviso(situacao, marca(self.pasta).get("curto", "RADAR")))
            except radar.RoboDesligado as e:
                self.estado.aviso(str(e))
                self.estado.terminar(erro=str(e), info={"causa": "desligado", "pt": str(e), "en": str(e), "detalhe": ""})
            except radar.Interrompida as e:
                from . import causas
                self.estado.aviso(causas.mensagem("interrompida"))
                sit = getattr(e, "situacao", None)
                self.estado.terminar(sit, erro=causas.mensagem("interrompida"), info={"causa": "interrompida", "pt": causas.mensagem("interrompida"),
                                                                                     "en": causas.mensagem("interrompida", "en"), "detalhe": ""})
                if sit and sit.get("aviso_planilha"):
                    self.planilha_depois()
            except Exception as e:  # a tela precisa saber que parou, qualquer que seja o motivo; em palavras claras
                from . import causas
                causa = causas.classificar(e)
                info = {"causa": causa, "pt": causas.mensagem(causa, "pt"), "en": causas.mensagem(causa, "en"),
                        "detalhe": f"{e.__class__.__name__}: {e}"[:600]}
                self.estado.aviso(info["pt"])
                self.estado.terminar(erro=info["pt"], info=info)
                if causa in ("erro_do_programa", "bloqueio_fora_do_brasil"):  # site do governo fora não é defeito nosso
                    import traceback
                    conta.registrar_erro(self.config(), VERSAO, "leitura pela tela" if causa == "erro_do_programa" else "leitura: fora do Brasil",
                                         traceback.format_exc()[-1800:])

        threading.Thread(target=alvo, daemon=True, name="radar").start()
        return True


class Tratador(BaseHTTPRequestHandler):
    server_version = "LexSuiteONE"

    def log_message(self, *args):  # a janela preta fica só com as mensagens do robô
        pass

    def _responder(self, corpo, tipo="application/json; charset=utf-8", status=200):
        if isinstance(corpo, (dict, list)):
            corpo = json.dumps(corpo, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if tipo.startswith("text/html"):  # 0.7.20 (sugestão da revisão): o navegador impõe "nenhum pedido externo"
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; "
                             "img-src 'self' data:; font-src 'self' data:; connect-src 'self'; frame-src 'none'; object-src 'none'; base-uri 'none'; "
                             "form-action 'self'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(corpo)

    def _host_local(self):
        """Só 127.0.0.1 ou localhost nesta porta: um site malicioso com DNS rebinding não passa."""
        host = self.headers.get("Host", "").lower()
        porta = self.server.server_address[1]
        return host in {f"127.0.0.1:{porta}", f"localhost:{porta}", "127.0.0.1", "localhost"}

    def _da_propria_pagina(self):
        host = self.headers.get("Host", "")
        origem = self.headers.get("Origin") or self.headers.get("Referer") or ""
        return self.headers.get("X-LexSuite") == "1" and (origem == "" or origem.startswith("http://" + host))

    def do_GET(self):
        if not self._host_local():
            return self._responder({"erro": "pedido recusado"}, status=403)
        import time as _t
        if self.headers.get("X-LexSuite-Sonda") != "1":  # 0.7.28: a sonda do segundo clique não conta como tela aberta
            self.server.ultimo_pedido = _t.monotonic()
        u = urlparse(self.path)
        qs = parse_qs(u.query)
        s = self.server
        if u.path in ("/", "/index.html"):
            with open(s.modelo, "rb") as f:
                return self._responder(f.read(), "text/html; charset=utf-8")
        if u.path == "/dados":
            cfg = s.config()
            r = cfg["radar"]
            dias = config.inteiro(qs.get("dias", [r.get("dias_na_pagina", 1)])[0], 1, 1, 90)  # 0.7.25: Infinity não derruba
            banco = bd.Banco(s.caminho_db)
            visao = "arquivo" if qs.get("visao", [""])[0] == "arquivo" else "lista"
            pagina = radar.montar_radar(cfg, banco, situacao=s.estado.situacao, dias=dias, visao=visao)
            if visao == "arquivo":  # 0.7.16: com dezenas de milhares de ações, a tela recebe as 5 mil mais recentes; a busca vai ao programa
                q = cl.sem_acento(str(qs.get("q", [""])[0] or "")).lower().strip()[:80]
                if q:
                    pagina["itens"] = [i for i in pagina["itens"] if q in cl.sem_acento(" ".join(str(x) for x in (
                        i.get("processo"), i.get("vara"), " ".join(i.get("empresas") or []), (i.get("empresa") or {}).get("cnpj"),
                        (i.get("empresa") or {}).get("razao_social"), (i.get("empresa") or {}).get("municipio")))).lower()]
                pagina["arquivo_total"], pagina["arquivo_busca"] = len(pagina["itens"]), q
                pagina["itens"] = pagina["itens"][:ARQUIVO_NA_TELA]
            pagina["versao"] = VERSAO
            try:
                sit = armazenamento.situacao(cfg, banco, s.pasta)
                pagina["armazenamento"] = sit
            except Exception:  # noqa: BLE001 - o retrato do armazenamento nunca derruba a tela
                pagina["armazenamento"] = {}
            pagina["espaco"] = banco.espaco()
            from . import historico as _hist  # 0.7.18: estatísticas dos meses anteriores (sazonalidade)
            hs = _hist.situacao(banco)
            hs.update({"por_mes": _hist.por_mes(banco, tribunais.validar(r.get("tribunais"))),
                       "por_semana": _hist.por_dia_da_semana(banco, tribunais.validar(r.get("tribunais"))),
                       "rodando": dict(s.hist) if s.hist.get("rodando") else {}})
            pagina["historico"] = hs
            crit = banco.execucoes("criterio", 1)
            pagina["criterio"] = crit[0] if crit else {}
            ultimo = banco.execucoes("retorno", 1)
            pagina["retorno"] = ultimo[0] if ultimo else {}
            tent = banco.execucoes("tentativa", 1)  # 0.7.36 (dono): a faixa do Painel avisa quando a última leitura falhou
            pagina["ultima_tentativa"] = tent[0] if tent else {}
            comp = cfg["compartilhar"]
            base = compartilhar.pasta_base(cfg)
            chave = atualizar.chave_publica(s.pasta)
            horarios, dias = agendar.do_config(cfg)
            agendado, proxima = agendar.agendado(), agendar.proxima(horarios, dias)
            pagina["app"] = {
                "usuario": {"nome": cfg["usuario"].get("nome", ""), "papel": cfg["usuario"].get("papel", ""), "email": cfg["usuario"].get("email", "")},
                "papeis": list(PAPEIS), "documento_escritorio": cfg.get("documento_escritorio") or {},
                "tribunais": [x for x in tribunais.TRIBUNAIS if x["ramo"] in FRENTES], "ramos": [r for r in tribunais.RAMOS if r in FRENTES], "regioes": tribunais.REGIOES, "ufs": tribunais.UFS,
                "config": {"tribunais": tribunais.validar(r.get("tribunais")), "escritorio": cfg.get("escritorio", ""),
                           "valor_minimo": _finito(r.get("valor_minimo")), "dias_na_pagina": config.inteiro(r.get("dias_na_pagina", 1), 1, 1, 90),
                           "dias_para_tras": _dias_para_tras(r),
                           "teto_capital_gigante": _finito(r.get("teto_capital_gigante")),  # 0.7.27: Infinity/NaN não quebram o JSON
                           "pasta": comp.get("pasta", ""), "subpasta": comp.get("subpasta", "LexSuiteONE"), "pasta_base": base,
                           "pasta_ok": bool(base and os.path.isdir(base)),
                           "planilha": preferencias.caminho(base) if base and os.path.exists(preferencias.caminho(base)) else "",
                           "planilha_prevista": preferencias.caminho(base) if base else "", "no_drive": compartilhar.no_google_drive(comp.get("pasta", "")),
                           "agendavel": agendar.disponivel(), "chamado": CHAMADO_LIGADO, "agendado": agendado,
                           "horarios": horarios, "dias": dias, "tem_noite": agendar.tem_noite(horarios),
                           "proxima": proxima.isoformat(timespec="minutes") if (agendado and proxima) else "",
                           "avisar_ao_terminar": bool(r.get("avisar_ao_terminar", True)),
                           "area_logada_por_dia": config.inteiro(r.get("area_logada_por_dia", 30), 30, 1, 365),
                           "abrir_em_aba": bool(r.get("abrir_em_aba")),
                           "guardar_meses": config.inteiro(r.get("guardar_meses", 12), 12, 1, 120)},
                "atualizacao": {"chave": bool(chave), "impressao": assinatura.impressao(chave) if chave else "",
                                "url": cfg["atualizacao"].get("url", ""), "pasta": compartilhar.pasta_atualizacao(cfg)},
                "versao": VERSAO, "estado": s.estado_atual(), "pasta_robo": s.pasta,
                "conta": conta.situacao(cfg), "marca": marca(s.pasta),
            }
            return self._responder(pagina)
        if u.path == "/cnpj":
            # Preenche o nome do escritório pelo CNPJ (cadastro público da Receita, pelas mesmas fontes da ficha).
            numero = conta.limpar_cnpj((qs.get("n") or [""])[0])
            if not conta.cnpj_valido(numero):
                return self._responder({"ok": False, "motivo": "cnpj_invalido"})
            try:
                d = cnpj.consultar(numero)
            except Exception:
                d = None
            if not d or not d.get("razao_social"):
                return self._responder({"ok": False, "motivo": "nao_encontrado"})
            return self._responder({"ok": True, "razao_social": d.get("razao_social", ""), "nome_fantasia": d.get("nome_fantasia", ""),
                                    "situacao": d.get("situacao", ""), "municipio": d.get("municipio", ""), "uf": d.get("uf", "")})
        if u.path == "/historico":  # 0.7.13: as últimas tentativas de leitura, uma por tribunal
            try:
                banco = bd.Banco(self.server.caminho_db)
                return self._responder({"tentativas": banco.execucoes("tentativa", 120)})
            except Exception:  # noqa: BLE001 - banco ausente ou ilegível: lista vazia
                return self._responder({"tentativas": []})
        if u.path == "/estatisticas":  # 0.7.18: andamento das estatísticas dos meses anteriores
            from . import historico as _hist
            try:
                sit = _hist.situacao(bd.Banco(s.caminho_db))
            except Exception:  # noqa: BLE001
                sit = {}
            sit["rodando"] = dict(s.hist) if s.hist.get("rodando") else {}
            sit["ultimo"] = s.hist.get("ultimo") or {}
            sit["erro"] = s.hist.get("erro", "")
            return self._responder(sit)
        if u.path == "/estado":
            d = s.estado_atual()
            d["tela_ativa"] = _t.monotonic() - s.ultimo_pedido < 25  # a tela pergunta a cada 10 s
            if self.headers.get("X-LexSuite-Sonda") == "1":
                d["pid"] = os.getpid()  # 0.7.29: o "Encerrar o RADAR" só encerra o processo que respondeu por esta porta
                d["pasta"] = s.pasta  # ...e só o desta pasta (outra instalação no mesmo computador fica)
                d["chamado_pendente"] = bool(getattr(s, "chamado", 0))  # 0.7.29: a tela ainda não atendeu o "já estava aberto"
            if self.headers.get("X-LexSuite-Sonda") != "1" and getattr(s, "chamado", 0):
                d["chamado"] = True; s.chamado = 0  # 0.7.28: alguém clicou no atalho de novo; a tela avisa e vem para a frente
            return self._responder(d)
        if u.path == "/chamar" and self.headers.get("X-LexSuite-Sonda") == "1":
            s.chamado = 0 if "cancelar" in (u.query or "") else _t.monotonic()  # revisão da 0.7.29: chamado sem tela não fica pendente
            return self._responder({"ok": True})
        if u.path == "/manual":
            manual = os.path.join(s.pasta, "MANUAL-DO-ESCRITORIO.html")
            if not os.path.exists(manual):
                return self._responder({"erro": "manual não encontrado"}, status=404)
            with open(manual, encoding="utf-8") as f:
                html = f.read()
            return self._responder(personalizar_manual(html, s.config()).encode("utf-8"), "text/html; charset=utf-8")
        if u.path == "/versao-nova":
            # Ao abrir a tela: há versão nova no site? (só pergunta; instalar é com o botão). Guarda por 30 minutos.
            import time
            if not s.versao_cache or time.monotonic() - s.versao_cache[0] > 1800:
                try:
                    r = atualizar.atualizar(s.pasta, s.config(), VERSAO, lambda *_: None, instalar_agora=False)
                except Exception:  # sem internet ou site fora: a tela segue sem o aviso
                    r = {"ok": False, "disponivel": False}
                s.versao_cache = (time.monotonic(), {"disponivel": bool(r.get("disponivel") and r.get("ok")), "versao": r.get("versao", ""),
                                                     "atual": VERSAO})
            return self._responder(s.versao_cache[1])
        if u.path == "/regras":  # 0.7.33 (dono): critérios desta pessoa, neste computador, por área (criterios.json)
            cfg = s.config()
            area = ((parse_qs(u.query).get("area") or [""])[0] or "").strip()
            if area not in preferencias.AREAS:
                area = "trabalhista"
            if not os.path.exists(preferencias.caminho_criterios(s.pasta)):
                preferencias.migrar(s.pasta, compartilhar.pasta_base(cfg), cfg.get("radar"), banco=bd.Banco(s.caminho_db))
            erro = (preferencias.ler_criterios(s.pasta) or {}).get("erro", "")
            valores, exc = preferencias.criterios_da_area(s.pasta, area)
            return self._responder({"ok": True, "area": area, "areas": list(preferencias.AREAS), "valores": valores, "exclusoes": exc,
                                    "limites": preferencias.LIMITES, "max_exclusoes": preferencias.MAX_EXCLUSOES, "erro_leitura": erro})
        if u.path == "/chamados":  # 0.7.33: Meus chamados (lista local) e envio dos que ficaram sem internet
            if not CHAMADO_LIGADO:
                return self._responder({"ok": False, "desligado": True, "chamados": [], "pendentes": 0})
            faltam = enviar_pendentes(s.pasta, s.config())
            return self._responder({"ok": True, "chamados": list(reversed(_lista_json(os.path.join(s.pasta, "saida", "chamados.json"))))[:30],
                                    "pendentes": faltam})
        if u.path == "/registro":  # 0.7.29 (sem janela preta): o que ia para a janela preta, na Configuração → Ver registro
            arq = os.path.join(s.pasta, "saida", "registro.txt")
            try:
                with open(arq, "rb") as f:
                    f.seek(max(0, os.path.getsize(arq) - 60000))
                    texto = f.read().decode("utf-8", "replace")
            except OSError:
                texto = ""
            return self._responder({"ok": True, "texto": "\n".join(texto.splitlines()[-400:]), "caminho": arq})
        if u.path == "/pastas":
            cfg = s.config()
            cand = compartilhar.candidatas()
            return self._responder({"candidatas": cand, "nuvens": compartilhar.nuvens(cand), "atual": cfg["compartilhar"].get("pasta", ""), "drive": bool(cand),
                                    "pasta_programa": s.pasta, "subpasta": compartilhar.subpasta_para(cfg, marca(s.pasta)["nome"]),
                                    "escolher": os.name == "nt"})
        return self._responder({"erro": "não existe"}, status=404)

    def do_POST(self):
        caminho = urlparse(self.path).path
        if not self._host_local() or not self._da_propria_pagina():
            return self._responder({"erro": "pedido recusado"}, status=403)
        import time as _t
        if caminho == "/tela-fechada":  # 0.7.29 (dono): fechou a janela no X; o próximo clique no atalho abre a tela de novo
            self.server.ultimo_pedido = min(self.server.ultimo_pedido, _t.monotonic() - 30)
            return self._responder({"ok": True})
        self.server.ultimo_pedido = _t.monotonic()
        if caminho == "/sair":  # 0.7.16: "Sair do RADAR" fecha a tela e a janela preta (se não houver leitura nesta janela)
            if self.server.estado.rodando or self.server.hist.get("rodando"):
                return self._responder({"ok": False, "motivo": "Há uma leitura em andamento: espere terminar ou clique em Interromper. "
                                                                "/ A reading is in progress."})
            self._responder({"ok": True})
            threading.Timer(0.5, self.server.shutdown).start()
            return None
        try:
            tamanho = int(self.headers.get("Content-Length") or 0)
            corpo = json.loads(self.rfile.read(tamanho) or b"{}")
        except ValueError:
            return self._responder({"erro": "JSON inválido"}, status=400)
        if not isinstance(corpo, dict):
            corpo = {}
        s = self.server
        if caminho == "/conta/conferir":  # 0.7.34 (dono): depois do aceite dos termos a tela confere na hora, sem esperar a leitura
            cfg = s.config()
            if not conta.valido(conta.normalizar((cfg.get("conta") or {}).get("codigo"))):
                return self._responder({"ok": False, "conta": conta.situacao(cfg)})
            if s.estado.rodando:  # 0.7.36 (revisão da Operação): a leitura em andamento confere sozinha; a tela diz isso
                return self._responder({"ok": False, "ocupado": True, "conta": conta.situacao(cfg)})
            import copy as _copy
            antes_conta = _copy.deepcopy(cfg.get("conta") or {})
            c = conta.verificar(cfg, VERSAO)
            if c.get("resposta") == "sem_resposta":  # sem internet: nada muda (não troca "falta aceitar" por "última confirmação")
                cfg["conta"] = antes_conta
                return self._responder({"ok": False, "sem_internet": True, "conta": conta.situacao(cfg)})
            novo = s.config()  # revisão: a conferência pode levar segundos; grava só a licença sobre o config de agora
            novo["conta"] = cfg["conta"]
            if not s.estado.rodando:
                try:
                    config.salvar(s.caminho_config, novo)
                except OSError:
                    pass
            return self._responder({"ok": True, "conta": conta.situacao(novo)})
        if caminho == "/config":
            cfg = s.config()
            r = cfg["radar"]
            if "tribunais" in corpo:
                r["tribunais"] = tribunais.validar(corpo["tribunais"])
            limites = (("valor_minimo", float, 0, 1e12), ("dias_na_pagina", int, 1, 90),
                       ("teto_capital_gigante", float, 0, 1e15), ("dias_para_tras", int, 0, 10))
            for chave, tipo, minimo, maximo in limites:
                if chave in corpo:
                    try:
                        r[chave] = min(maximo, max(minimo, tipo(corpo[chave])))
                    except (TypeError, ValueError, OverflowError):
                        pass
            if "escritorio" in corpo:
                cfg["escritorio"] = str(corpo["escritorio"] or "").strip()[:80]
            if "codigo" in corpo:
                # Código de cliente: confere na hora com a SolverONE; código errado não é salvo.
                import copy as _copy
                antes_conta = _copy.deepcopy(cfg.get("conta") or {})
                novo_cod = conta.normalizar(corpo["codigo"])
                mudou_cod = novo_cod != conta.normalizar(antes_conta.get("codigo"))
                cfg.setdefault("conta", {})["codigo"] = novo_cod
                if mudou_cod:  # revisão da 0.7.32 ("Trocar licença"): a confirmação do código antigo não vale para o novo
                    for k_ in ("ultima_ok", "resposta", "mensagem", "aceite", "termos", "escritorio_licenca", "validade"):
                        cfg["conta"].pop(k_, None)
                c = conta.verificar(cfg, VERSAO)
                if c.get("resposta") not in ("ok", "sem_resposta"):
                    resp_ = {"ok": False, "motivo": conta.bloqueio(cfg), "motivo_en": conta.bloqueio_en(cfg), "conta": conta.situacao(cfg)}
                    if mudou_cod and antes_conta.get("codigo"):
                        cfg["conta"] = antes_conta  # o código bom continua (o disco não foi tocado: cada pedido relê o config)
                        resp_["conta"] = conta.situacao(cfg)
                    return self._responder(resp_)
                if c.get("resposta") == "sem_resposta" and not c.get("ultima_ok"):
                    if mudou_cod and antes_conta.get("codigo"):
                        cfg["conta"] = antes_conta
                    return self._responder({"ok": False, "motivo": "Não consegui falar com a SolverONE para confirmar o código. "
                                                                    "Confira a internet e tente de novo.",
                                            "motivo_en": "I could not reach SolverONE to confirm the code. Check the internet and try again.",
                                            "conta": conta.situacao(cfg)})
                if c.get("escritorio_licenca") and not cfg.get("escritorio"):
                    cfg["escritorio"] = c["escritorio_licenca"]
            if "email" in corpo:
                # Cadastro de quem usa: o e-mail é a chave (um e-mail, um escritório). Vai para a licença na SolverONE.
                if "escritorio" in corpo:
                    cfg["escritorio"] = str(corpo["escritorio"] or "").strip()[:80]
                doc_atual = cfg.get("documento_escritorio") or {}
                ok, motivo = conta.cadastrar(cfg, VERSAO, corpo.get("email"), corpo.get("nome") or cfg["usuario"].get("nome"),
                                             corpo.get("documento") or doc_atual.get("numero"),
                                             papel_valido(corpo) if "papel" in corpo else cfg["usuario"].get("papel"),
                                             doc_tipo=corpo.get("doc_tipo") or doc_atual.get("tipo") or "cnpj",
                                             aceite_uso=corpo.get("aceite_uso") if isinstance(corpo.get("aceite_uso"), dict) else None)
                if not ok:
                    return self._responder({"ok": False, "motivo": motivo, "conta": conta.situacao(cfg)})
            if "horarios" in corpo and corpo["horarios"]:  # revisão da 0.7.31: lista vazia não troca os horários pelo padrão
                r["horarios"] = agendar.validar(corpo["horarios"])
            if "dias" in corpo:
                r["dias"] = agendar.validar_dias(corpo["dias"])
            if "avisar_ao_terminar" in corpo:
                r["avisar_ao_terminar"] = bool(corpo["avisar_ao_terminar"])
            if "abrir_em_aba" in corpo:
                r["abrir_em_aba"] = bool(corpo["abrir_em_aba"])
            if "nome" in corpo:
                cfg["usuario"]["nome"] = str(corpo["nome"] or "").strip()[:60]
            if "papel" in corpo:
                cfg["usuario"]["papel"] = papel_valido(corpo)
            if "pasta" in corpo:
                pasta = str(corpo["pasta"] or "").strip()
                if pasta and not os.path.isdir(pasta) and corpo.get("criar"):
                    try:
                        os.makedirs(pasta, exist_ok=True)
                    except OSError as e:
                        return self._responder({"ok": False, "motivo": f"Não consegui criar a pasta ({e.__class__.__name__})."})
                if pasta and not os.path.isdir(pasta):
                    return self._responder({"ok": False, "motivo": "Essa pasta ainda não existe neste computador.", "nao_existe": True})
                cfg["compartilhar"]["subpasta"] = compartilhar.subpasta_para(cfg, marca(s.pasta)["nome"])
                cfg["compartilhar"]["pasta"] = pasta
                if pasta:
                    ok, msg = compartilhar.testar(pasta, cfg["compartilhar"]["subpasta"])
                    if not ok:
                        return self._responder({"ok": False, "motivo": msg})
                    try:
                        compartilhar.criar_se_faltar(cfg, VERSAO, s.pasta, s.estado.aviso)
                    except Exception as e:
                        return self._responder({"ok": False, "motivo": f"Não consegui criar a planilha ({e.__class__.__name__})."})
            config.salvar(s.caminho_config, cfg)
            base_nova = compartilhar.pasta_base(cfg)
            resposta = {"ok": True, "radar": r, "escritorio": cfg.get("escritorio", ""), "pasta": cfg["compartilhar"].get("pasta", ""),
                        "planilha": preferencias.caminho(base_nova) if base_nova else "", "subpasta": cfg["compartilhar"].get("subpasta", ""),
                        "no_drive": compartilhar.no_google_drive(cfg["compartilhar"].get("pasta", "")),
                        "conta": conta.situacao(cfg)}
            mudou_horario = "horarios" in corpo or "dias" in corpo
            if agendar.disponivel() and ("agendar" in corpo or (mudou_horario and agendar.agendado())):
                ligar = corpo["agendar"] if "agendar" in corpo else True
                ligar = ligar and bool(agendar.dias_da_semana(r.get("dias")))  # 0.7.32 (dono): nenhum dia marcado = desligada
                ok, msg = agendar.agendar(s.pasta, *agendar.do_config(cfg)) if ligar else agendar.desagendar()
                resposta.update({"agendado": agendar.agendado(), "agendar_msg": msg, "agendar_ok": bool(ok)})  # 0.7.36: a tela em EN traduz pelo estado
            return self._responder(resposta)
        if caminho == "/interromper":  # 0.7.15: pede para a leitura (desta tela ou a agendada) parar no próximo ponto seguro
            if not (s.estado.rodando or leitura_em_outro_processo(s.arquivo_andamento)):
                return self._responder({"ok": False, "motivo": "Nenhuma leitura em andamento."})
            os.makedirs(os.path.dirname(s.arquivo_andamento), exist_ok=True)
            with open(os.path.join(os.path.dirname(s.arquivo_andamento), "parar.json"), "w", encoding="utf-8") as f:
                json.dump({"quando": dt.datetime.now().isoformat(timespec="seconds"), "quem": s.config()["usuario"].get("email", "")}, f)
            try:
                b = bd.Banco(s.caminho_db)
                try:
                    b.registrar_acao(s.config()["usuario"].get("email", ""), "interromper", "leitura", "", "", 1)
                    b.con.commit()
                finally:
                    b.con.close()  # nunca deixar a trava de escrita presa (a leitura em andamento precisa gravar)
            except Exception:  # noqa: BLE001 - o registro é extra; o pedido de parada já está no parar.json
                pass
            return self._responder({"ok": True})
        if caminho == "/abrir-em-aba":  # 0.7.14: a mesma tela numa aba comum do navegador (junto das outras abas)
            webbrowser.open(f"http://127.0.0.1:{s.server_address[1]}/")
            return self._responder({"ok": True})
        if caminho == "/situacao":  # 0.7.14: muda a situação de um ou muitos processos (lote); devolve o "antes" para desfazer
            try:
                r = bd.Banco(s.caminho_db).mudar_situacao(corpo.get("processos") or [], corpo.get("situacao"),
                                                          perfil=s.config()["usuario"].get("email", ""), motivo=str(corpo.get("motivo") or ""))
            except ValueError as e:
                return self._responder({"ok": False, "motivo": str(e)}, status=400)
            s.planilha_depois()
            return self._responder({"ok": True, **r})
        if caminho == "/desfazer":
            n = bd.Banco(s.caminho_db).desfazer_situacao(corpo.get("antes") or {}, perfil=s.config()["usuario"].get("email", ""))
            s.planilha_depois()
            return self._responder({"ok": True, "quantos": n})
        if caminho == "/migrar-situacoes":  # uma vez: o que estava guardado no navegador vai para o banco do computador
            banco = bd.Banco(s.caminho_db)
            atuais = {l["processo"]: l["status"] for l in banco.todos_leads()}
            grupos = {}
            itens = corpo.get("itens") if isinstance(corpo.get("itens"), dict) else {}
            for proc, st in list(itens.items())[:20000]:
                st = bd.situacao_valida(st)
                if st and atuais.get(proc) == "novo" and st != "novo":
                    grupos.setdefault(st, []).append(proc)
            levados = 0
            for st, procs in grupos.items():  # uma mudança (e um registro) por situação, não por processo
                levados += banco.mudar_situacao(procs, st, perfil="migração do navegador")["quantos"]
            return self._responder({"ok": True, "levados": levados})
        if caminho == "/limpar":
            banco = bd.Banco(s.caminho_db)
            try:
                meses = max(1, min(120, int(corpo.get("meses") or 12)))
            except (TypeError, ValueError):
                return self._responder({"ok": False, "motivo": "meses inválido"}, status=400)
            feitas = banco.limpar_detalhe(meses, perfil=s.config()["usuario"].get("email", ""))
            banco.compactar()
            return self._responder({"ok": True, "resumidas": feitas, "espaco": banco.espaco()})
        if caminho in ("/armazenamento/limpar", "/armazenamento/copia", "/armazenamento/exportar"):  # 0.7.16
            if s.estado.como_dict()["rodando"] or leitura_em_outro_processo(s.arquivo_andamento):
                return self._responder({"ok": False, "motivo": "Espere a leitura terminar. / Wait for the reading to finish."})
            cfg, banco, recados = s.config(), bd.Banco(s.caminho_db), []
            if caminho.endswith("limpar"):
                ok, msg = armazenamento.limpar(cfg, banco, s.pasta, VERSAO, recados.append)
            else:
                ok, msg = armazenamento.copia_seguranca(cfg, banco, "exportação" if caminho.endswith("exportar") else "feita à mão",
                                                        recados.append, so_csv=caminho.endswith("exportar"))
                if ok:
                    abrir_no_windows(msg)
            return self._responder({"ok": ok, "mensagem" if ok else "motivo": msg, "armazenamento": armazenamento.situacao(cfg, banco, s.pasta)})
        if caminho in ("/estatisticas/pedir", "/estatisticas/ler", "/estatisticas/parar"):  # 0.7.18
            from . import historico as _hist
            if caminho.endswith("parar"):
                s.hist["parar"] = True
                return self._responder({"ok": True})
            with s.hist_trava:  # 0.7.18 (revisão): dois cliques não abrem duas leituras de estatísticas
                if s.estado.rodando or leitura_em_outro_processo(s.arquivo_andamento) or s.hist.get("rodando"):
                    return self._responder({"ok": False, "motivo": "Espere a leitura em andamento terminar. / Wait for the reading in progress."})
            try:
                cfg, banco = s.config(), bd.Banco(s.caminho_db)
            except Exception as e:  # noqa: BLE001 - revisão da 0.7.18 (4.4): nunca deixa a marca "rodando" presa
                return self._responder({"ok": False, "motivo": f"Não consegui abrir os dados do programa ({e.__class__.__name__}). / Could not open the program data."})
            if caminho.endswith("ler"):
                with s.hist_trava:
                    if s.hist.get("rodando"):
                        return self._responder({"ok": False, "motivo": "Espere a leitura em andamento terminar. / Wait for the reading in progress."})
                    s.hist.clear()
                    s.hist_n = getattr(s, "hist_n", 0) + 1  # 0.7.21: cada leitura tem número; a antiga não mexe na nova
                    s.hist.update({"rodando": True, "k": 0, "total": 0, "tribunal": "", "data": "", "n": s.hist_n})
            if caminho.endswith("pedir"):
                try:
                    meses = max(1, min(24, int(corpo.get("meses") or _hist.MESES_PADRAO)))
                except (TypeError, ValueError):
                    return self._responder({"ok": False, "motivo": "meses inválido"}, status=400)
                n = _hist.pedir(banco, meses, tribunais.validar(cfg["radar"].get("tribunais")), perfil=cfg["usuario"].get("email", ""))
                return self._responder({"ok": True, "na_fila": n, "historico": _hist.situacao(banco)})

            meu_n = s.hist.get("n")

            def minha():  # esta leitura ainda é a da tela? (um envio de erro lento não pode sujar a leitura seguinte)
                return s.hist.get("n") == meu_n

            def ler():
                try:
                    b2 = bd.Banco(s.caminho_db)
                    def andamento(k, total, trib, data):
                        if minha():
                            s.hist.update({"k": k, "total": total, "tribunal": trib, "data": data})
                    # 0.7.33 (dono): lê a fila inteira (em lotes, com a pausa entre Diários); Pausar para e guarda o resto
                    por_vez = int((cfg.get("radar") or {}).get("estatisticas_por_vez") or _hist.POR_VEZ)
                    r_ = _hist.processar_tudo(b2, aviso=print, parar=lambda: bool(minha() and s.hist.get("parar")), andamento=andamento, lote=por_vez)
                    if minha():
                        s.hist.update({"ultimo": r_})
                except Exception as e:  # noqa: BLE001 - a tela mostra a mensagem certa, no idioma dela (4.1)
                    causa_, msg = _hist._causa(e)
                    if causa_ == "erro_do_programa":
                        # 0.7.21 (revisão da 0.7.20): a tela recebe na hora um texto sem promessa; só depois de o aviso
                        # técnico chegar à SolverONE o texto passa a dizer que ela foi avisada (sem internet, não diz)
                        import traceback
                        detalhe = traceback.format_exc()[-1800:]
                        with s.hist_trava:
                            if minha():
                                s.hist.update({"erro": dict(_ERRO_HIST_NEUTRO), "rodando": False})
                                s.hist.pop("parar", None)
                        enviado = conta.registrar_erro(cfg, VERSAO, "estatisticas antigas", detalhe)
                        with s.hist_trava:
                            if enviado and minha():
                                s.hist.update({"erro": msg})
                    elif minha():
                        s.hist.update({"erro": msg})
                finally:
                    with s.hist_trava:
                        if minha():
                            s.hist["rodando"] = False
                            s.hist.pop("parar", None)
            threading.Thread(target=ler, daemon=True, name="estatisticas-antigas").start()
            return self._responder({"ok": True})
        if caminho == "/regras":  # 0.7.33 (dono): grava os critérios desta pessoa (criterios.json), por área
            area, valores, exc, todas = corpo.get("area") or "trabalhista", corpo.get("valores"), corpo.get("exclusoes"), bool(corpo.get("todas"))
            if not isinstance(valores, dict) or not isinstance(exc, list) or area not in preferencias.AREAS:
                return self._responder({"ok": False, "motivo": "Pedido incompleto: abra os critérios de novo.",
                                        "motivo_en": "Incomplete request: open the criteria again."}, status=400)
            if len(exc) > preferencias.MAX_EXCLUSOES:
                return self._responder({"ok": False, "motivo": f"São {len(exc)} empresas excluídas; o limite é {preferencias.MAX_EXCLUSOES}. Tire algumas e salve de novo.",
                                        "motivo_en": f"There are {len(exc)} excluded companies; the limit is {preferencias.MAX_EXCLUSOES}. Remove some and save again."})
            ruins = [str(e.get("nome") or "") for e in exc if isinstance(e, dict) and str(e.get("nome") or "").strip()
                     and not preferencias.exclusao_valida(e.get("nome"))]
            if ruins:  # 0.7.33 (dono): CPF ou CNPJ digitado tem de ser válido
                return self._responder({"ok": False, "motivo": "CPF ou CNPJ inválido: " + ", ".join(ruins[:3]) + ". Confira os números e salve de novo.",
                                        "motivo_en": "Invalid CPF or CNPJ: " + ", ".join(ruins[:3]) + ". Check the numbers and save again."})
            with _TRAVA_REGRAS:
                try:
                    preferencias.salvar_area(s.pasta, area, valores, exc, todas=todas)
                except ValueError:  # revisão da 0.7.33: criterios.json ilegível e sem cópia boa: não grava uma área por cima
                    return self._responder({"ok": False, "motivo": "O arquivo dos critérios deste computador está danificado e não há cópia boa. Escreva para judicial@solverone.com.br antes de salvar.",
                                            "motivo_en": "This computer's criteria file is damaged and there is no good copy. Write to judicial@solverone.com.br before saving."})
                except OSError:
                    return self._responder({"ok": False, "motivo": "Não consegui gravar os critérios neste computador (pasta do programa sem permissão).",
                                            "motivo_en": "Could not save the criteria on this computer (no permission in the program folder)."})
            return self._responder({"ok": True, "area": area, "todas": todas})
        if caminho == "/chamado":  # 0.7.33 (dono): chamado pelo AssistONE, para a central de feedback do RootifyONE
            if not CHAMADO_LIGADO:
                return self._responder({"ok": False, "desligado": True, "motivo": "O chamado pelo programa ainda não está disponível. Escreva para judicial@solverone.com.br.",
                                        "motivo_en": "Tickets from the program are not available yet. Write to judicial@solverone.com.br."}, status=403)
            import uuid
            cat, texto = str(corpo.get("categoria") or ""), str(corpo.get("texto") or "").strip()
            if cat not in conta.CATEGORIAS_CHAMADO or not texto:
                m_ = MOTIVOS_CHAMADO["dados_invalidos"]
                return self._responder({"ok": False, "motivo": m_[0], "motivo_en": m_[1]}, status=400)
            trilha = corpo.get("trilha") if isinstance(corpo.get("trilha"), list) else []
            dados = {"categoria": cat, "texto": texto[:4000], "pode_responder": bool(corpo.get("pode_responder")),
                     "com_sistema": corpo.get("com_sistema", True) is not False, "trilha": trilha if corpo.get("com_tela", True) is not False else [],
                     "cliente_id": uuid.uuid4().hex, "quando_cliente": dt.datetime.now().astimezone().isoformat(timespec="seconds")}
            for k in ("tela", "titulo_tela", "funcao", "idioma", "fuso"):
                if corpo.get("com_tela", True) is not False or k in ("idioma", "fuso"):
                    dados[k] = str(corpo.get(k) or "")[:200]
            r = conta.enviar_chamado(s.config(), VERSAO, dados)
            if not r.get("sem_internet"):  # com internet, os que ficaram na fila saem junto (sem internet, não espera duas vezes)
                enviar_pendentes(s.pasta, s.config())
            if r.get("ok"):
                guardar_chamado(s.pasta, dados, r.get("numero"))
                return self._responder({"ok": True, "numero": r.get("numero")})
            if r.get("sem_internet"):
                with _TRAVA_CHAMADOS:
                    arq = os.path.join(s.pasta, "saida", "chamados-pendentes.json")
                    _gravar_lista_json(arq, _lista_json(arq) + [dados])
                return self._responder({"ok": False, "fila": True,
                                        "motivo": "Sem internet: o chamado não foi enviado. Ele fica guardado e sai sozinho quando o programa abrir com internet.",
                                        "motivo_en": "No internet: the ticket was not sent. It is kept and goes out by itself when the program opens with internet."})
            m_ = MOTIVOS_CHAMADO.get(r.get("motivo"), ("A SolverONE não respondeu agora. Tente de novo em alguns minutos.",
                                                      "SolverONE did not answer now. Try again in a few minutes."))
            return self._responder({"ok": False, "motivo": m_[0], "motivo_en": m_[1]})
        if caminho == "/copia-planilha":
            cfg = s.config()
            ok, resultado = compartilhar.gerar_copia(cfg)
            if ok:
                s.ultima_copia = resultado  # 0.7.18: a tela oferece "Abrir a cópia" e "Abrir a pasta"
            if ok and corpo.get("abrir", False):
                abrir_no_windows(resultado)
            return self._responder({"ok": ok, "caminho" if ok else "motivo": resultado})
        if caminho == "/contatos/preparar":
            from . import contatos as ct
            cfg = s.config()
            pagina = radar.montar_radar(cfg, bd.Banco(s.caminho_db), dias=90)
            quero = {str(x) for x in (corpo.get("processos") or []) if isinstance(x, (str, int))}
            itens = [i for i in pagina["itens"] if not quero or i["processo"] in quero]
            # 0.7.16: o pedido traz, em cada processo, só o que falta, e pede a "RESPOSTA PARA O RADAR v1" (qualquer extensão de IA)
            caminho_md, n, texto = ct.preparar_v1(itens, s.pasta, marca(s.pasta)["nome"], config.inteiro(cfg["radar"].get("area_logada_por_dia", 30), 30, 1, 365))
            if corpo.get("abrir_pasta", not quero):
                abrir_no_windows(os.path.dirname(caminho_md))
            return self._responder({"ok": True, "caminho": caminho_md, "quantos": n, "texto": texto})
        if caminho == "/valor":  # 0.7.16: valor da causa digitado no cartão fica no programa (antes, só no navegador)
            banco = bd.Banco(s.caminho_db)
            proc = str(corpo.get("processo") or "")[:40]
            bruto = str(corpo.get("valor") if corpo.get("valor") is not None else "").strip()
            valor = None
            if bruto:
                try:
                    valor = float(bruto.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")) if "," in bruto else float(bruto)
                except ValueError:
                    return self._responder({"ok": False, "motivo": "Valor fora do formato. / Invalid value."}, status=400)
                if not 0 < valor < 1e11:
                    return self._responder({"ok": False, "motivo": "Valor fora do formato. / Invalid value."}, status=400)
            ok = banco.completar(proc, "valor_causa", valor, "digitado", perfil=s.config()["usuario"].get("email", ""))
            if ok:
                s.planilha_depois()
            return self._responder({"ok": ok, "valor": valor})
        if caminho == "/contatos/colar":
            from . import contatos as ct
            banco = bd.Banco(s.caminho_db)
            empresas = {}
            for l in banco.todos_leads():
                emp = (l.get("empresa_receita") or {}).get("razao_social") or (l.get("empresas") or [""])[0]
                empresas[l["processo"]] = emp
            texto = str(corpo.get("texto") or "")[:200000]
            extra = {}
            if ct.e_resposta_v1(texto):  # 0.7.16: a resposta padronizada da área logada
                r1 = ct.colar_v1(texto, empresas)
                aceitas, recusadas = r1["contatos"], r1["recusadas"]
                perfil = s.config()["usuario"].get("email", "")
                completados = sum(1 for c in r1["completar"] if banco.completar(c["processo"], c["campo"], c["valor"], c["fonte"], c["data"], perfil))
                extra = {"completados": completados, "nao_consta": len(r1["nao_consta"]), "tentar_depois": len(r1["tentar_depois"])}
            else:
                aceitas, recusadas = ct.colar(texto, empresas)
            novas = sum(1 for c in aceitas if banco.guardar_contato(c))
            banco.registrar_colagem(s.config()["usuario"].get("email", ""), str(corpo.get("arquivo") or "")[:120], novas, len(recusadas),
                                    "; ".join(f"linha {r['linha']}: {r['motivo']}" for r in recusadas)[:2000])
            s.planilha_depois()
            return self._responder(dict({"ok": True, "aceitas": novas, "repetidas": len(aceitas) - novas, "recusadas": recusadas[:200]}, **extra))
        if caminho == "/abrir":
            cfg = s.config()
            base = compartilhar.pasta_base(cfg)
            planilha = preferencias.caminho(base) if base else ""
            if corpo.get("o_que") == "pasta_mae":  # a pasta escolhida, onde aparece a pasta da planilha (para compartilhar)
                alvo = os.path.dirname(base) if base else ""
            elif corpo.get("o_que") == "ultima_copia":  # 0.7.18: a cópia que acabou de ser gerada (só ela)
                alvo = getattr(s, "ultima_copia", "") or ""
            elif corpo.get("o_que") == "pasta_copias":
                alvo = os.path.dirname(getattr(s, "ultima_copia", "") or "") or (os.path.join(base, compartilhar.PASTA_COPIAS_TRABALHO) if base else "")
            elif corpo.get("o_que") == "registro":  # 0.7.29: o arquivo do registro (abre no Bloco de Notas)
                alvo = os.path.join(s.pasta, "saida", "registro.txt")
                if not os.path.exists(alvo):
                    return self._responder({"ok": False, "motivo": "Ainda não há registro.", "motivo_en": "There is no log yet."})
            elif corpo.get("o_que") == "copias":  # 0.7.16: a pasta das cópias de segurança
                alvo = armazenamento.pasta_copias(base)
                if alvo:
                    os.makedirs(alvo, exist_ok=True)
            else:
                alvo = planilha if corpo.get("o_que") == "planilha" else (os.path.dirname(planilha) if planilha else "")
            em_uso = False
            if corpo.get("o_que") == "planilha" and alvo and os.path.exists(alvo):
                em_uso = not planilha_mod.marcar_se_livre(alvo)  # 0.7.25: aberta para editar noutro lugar? não marca agora
                if abrir_so_leitura(alvo):
                    return self._responder({"ok": True, "so_leitura": True, "em_uso": em_uso})
            if abrir_no_windows(alvo):
                return self._responder({"ok": True, "em_uso": em_uso})
            return self._responder({"ok": False, "motivo": "A planilha ainda não existe. Confira a pasta das planilhas em Configurações e faça uma leitura. / The spreadsheet does not exist yet.",
                                    "caminho": planilha})
        if caminho == "/testar-pasta":
            cfg = s.config()
            pasta = str(corpo.get("pasta") or "").strip()
            sub_ = compartilhar.subpasta_para(cfg, marca(s.pasta)["nome"])
            ok, msg = compartilhar.testar(pasta, sub_, criar=bool(corpo.get("criar")), leve=bool(corpo.get("leve")))
            return self._responder({"ok": ok, "mensagem": msg, "nao_existe": bool(pasta) and not os.path.isdir(pasta),
                                    "alvo": os.path.join(pasta, sub_) if pasta else "",
                                    "no_drive": compartilhar.no_google_drive(pasta)})
        if caminho == "/gravar-planilha":
            if not compartilhar.pasta_base(s.config()):
                return self._responder({"ok": False, "motivo": "Escolha a pasta da planilha em Configurações."})
            recados = []
            ok = radar.regravar_planilha(s.config(), bd.Banco(s.caminho_db), s.pasta, VERSAO, recados.append)
            if not ok:
                s.planilha_depois()
            if ok and s.estado.situacao:
                s.estado.situacao.pop("aviso_planilha", None)
            return self._responder({"ok": ok, "motivo": " ".join(x.strip() for x in recados)[-300:]})
        if caminho == "/reiniciar":
            return self._responder({"ok": reiniciar_depois(s, s.pasta)})
        if caminho == "/escolher-pasta":
            pasta = escolher_pasta(str(corpo.get("inicio") or ""))
            return self._responder({"ok": bool(pasta), "pasta": pasta})
        if caminho == "/atualizar":
            if s.estado.como_dict()["rodando"]:
                return self._responder({"ok": False, "motivo": "espere a rodada terminar"})
            recados = []
            resultado = atualizar.atualizar(s.pasta, s.config(), VERSAO, recados.append, instalar_agora=bool(corpo.get("instalar", True)))
            resultado["recados"] = recados
            return self._responder(resultado)
        if caminho == "/rodar":
            if s.hist.get("rodando"):  # 0.7.18 (revisão): não lê o Diário de hoje com as estatísticas antigas baixando
                return self._responder({"ok": False, "motivo": "As estatísticas dos meses anteriores estão sendo lidas: clique em Parar no Painel "
                                                                "ou espere terminar. / Previous months' statistics are being read: stop them or wait."})
            if not tribunais.validar(s.config()["radar"].get("tribunais")):
                return self._responder({"ok": False, "motivo": "nenhum tribunal escolhido", "motivo_en": "no court chosen"})
            try:
                dias = config.inteiro(corpo["dias"], None, 0, 10) if corpo.get("dias") is not None else None
            except (TypeError, ValueError, OverflowError):
                dias = None
            if not _TRAVA_REGRAS.acquire(blocking=False):  # 0.7.29: o motivo certo, em vez de "já está rodando"
                return self._responder({"ok": False, "motivo": "A planilha está sendo gravada agora: tente de novo em instantes.",
                                        "motivo_en": "The spreadsheet is being saved right now: try again in a moment."})
            _TRAVA_REGRAS.release()
            comecou = s.rodar(dias)
            return self._responder({"ok": comecou, "motivo": "" if comecou else "já está rodando", "motivo_en": "" if comecou else "already running"})
        return self._responder({"erro": "não existe"}, status=404)


# Ramos oferecidos na tela: só a frente trabalhista por enquanto (os TJs e TRFs são de outras frentes).
FRENTES = ("Trabalhista",)
ARQUIVO_NA_TELA = 5000  # 0.7.16: quantas ações do Arquivo vão à tela de uma vez (a busca vai ao programa)
MARCA_PADRAO = {"nome": "RADAR JUDICIAL", "curto": "RADAR", "destaque": "IA"}


def marca(pasta):
    """Nome do produto (marca.json do pacote, gerado de docs/marca.json): exatamente como o dono escreveu."""
    try:
        with open(os.path.join(pasta, "marca.json"), encoding="utf-8") as f:
            m = json.load(f)
        nome = " ".join(str(m.get("nome") or "").split())[:40]
        if nome:
            return {"nome": nome, "curto": " ".join(str(m.get("curto") or "").split())[:40] or nome.split(" ")[0],
                    "destaque": str(m.get("destaque") or "")[:10]}
    except (OSError, ValueError, AttributeError):
        pass
    return dict(MARCA_PADRAO)


def excel_exe():
    """Caminho do Excel pelo registro do Windows (App Paths), ou ''."""
    if os.name != "nt":
        return ""
    try:
        import winreg
        for raiz in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
            try:
                with winreg.OpenKey(raiz, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\excel.exe") as k:
                    valor = winreg.QueryValue(k, None)
                    if valor and os.path.exists(valor.strip('"')):
                        return valor.strip('"')
            except OSError:
                continue
    except ImportError:
        pass
    return ""


def abrir_so_leitura(caminho):
    """0.7.14: abre a planilha no Excel em modo somente leitura (/r), para quem olha não travar a gravação do robô.
    Sem Excel (ou fora do Windows), devolve False e quem chamou abre do jeito normal."""
    exe = excel_exe()
    if not exe or not caminho or not os.path.exists(caminho):
        return False
    import subprocess  # nosec B404 - só abre o Excel do próprio Windows com a planilha do programa
    subprocess.Popen([exe, "/r", caminho], close_fds=True)  # nosec B603 - lista fixa, sem shell
    return True


def abrir_no_windows(caminho):
    """Abre um arquivo ou pasta com o programa padrão do Windows (Excel, Explorador). Só caminhos que o próprio
    programa conhece: a planilha e a pasta dela."""
    if os.name != "nt" or not caminho or not os.path.exists(caminho):
        return False
    os.startfile(caminho)  # nosec B606 - caminho vem do config (planilha do próprio programa), nunca do pedido
    return True


def personalizar_manual(html, cfg):
    """Troca os marcadores do manual pelo bloco do papel da pessoa (texto escapado); sem saudação com nome."""
    import html as h
    u = cfg.get("usuario") or {}
    papel = u.get("papel", "")
    ola = ""  # teste do dono (0.7.30): o manual é genérico, sem o nome da pessoa nem do escritório
    bloco = ""
    if papel in PARA_VOCE:
        itens = "".join(f"<li>{h.escape(t)}</li>" for t in PARA_VOCE[papel])
        bloco = f"<div class=\"caixa\"><b>Para você, {h.escape(papel.lower())}</b><ul>{itens}</ul></div>"
    return html.replace("<!--OLA-->", ola, 1).replace("<!--PARA_VOCE-->", bloco, 1)


def _finito(v):
    """0.7.27 (revisão): número finito ou None (Infinity e NaN escritos à mão no config.json gerariam JSON inválido)."""
    import math
    try:
        f = float(v)
    except (TypeError, ValueError, OverflowError):
        return None
    return v if math.isfinite(f) and not isinstance(v, bool) else None


def _dias_para_tras(r):
    """0.7.21 (revisão): o mesmo limite do POST /config (0 a 10); texto ou lista no config.json não derruba a tela."""
    return config.inteiro(r.get("dias_para_tras", 1), 1, 0, 10)


# 0.7.21: texto do erro das estatísticas antigas antes de o aviso técnico chegar à SolverONE (sem promessa de aviso)
_ERRO_HIST_NEUTRO = {"pt": "As estatísticas dos meses anteriores pararam por um problema no programa. O que já foi lido ficou guardado; "
                           "tente de novo mais tarde e, se continuar, fale com judicial@solverone.com.br.",
                     "en": "Previous months statistics stopped because of a program problem. What was already read is saved; "
                           "try again later and, if it persists, contact judicial@solverone.com.br."}

_ESCOLHER_PS = ("Add-Type -AssemblyName System.Windows.Forms; [Console]::OutputEncoding = [Text.Encoding]::UTF8; "
                "$f = New-Object System.Windows.Forms.Form; $f.TopMost = $true; $f.ShowInTaskbar = $true; $f.Opacity = 0; "
                "$f.StartPosition = 'CenterScreen'; $f.Text = $env:LEXSUITE_TITULO; $f.Show(); $f.Activate(); $f.BringToFront(); "
                "$d = New-Object System.Windows.Forms.FolderBrowserDialog; $d.Description = $env:LEXSUITE_TITULO; "
                "$d.ShowNewFolderButton = $true; if ($env:LEXSUITE_INICIO) { $d.SelectedPath = $env:LEXSUITE_INICIO }; "
                "if ($d.ShowDialog($f) -eq 'OK') { [Console]::Out.Write($d.SelectedPath) }; $f.Close()")


def escolher_pasta(inicio=""):
    """Abre a janela de pastas do Windows e devolve a pasta escolhida ("" se cancelou ou fora do Windows)."""
    if os.name != "nt":
        return ""
    import subprocess  # nosec B404 - só powershell, sem shell, comando fixo; o texto vai por variável de ambiente
    env = dict(os.environ, LEXSUITE_TITULO="Escolha a pasta das planilhas / Choose the spreadsheet folder",
               LEXSUITE_INICIO=inicio if os.path.isdir(inicio) else "")
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-STA", "-Command", _ESCOLHER_PS],  # nosec B603 B607
                           capture_output=True, stdin=subprocess.DEVNULL, env=env, timeout=600, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        pasta = r.stdout.decode("utf-8", "replace").strip()
    except (OSError, subprocess.SubprocessError):
        return ""
    return pasta if pasta and os.path.isdir(pasta) else ""


def titulo_janela(texto):
    """Título da janela preta no Windows (lembra que ela precisa ficar aberta)."""
    if os.name == "nt":
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleTitleW(str(texto)[:80])
        except (OSError, AttributeError):
            pass


def navegador_app():
    """Chrome ou Edge deste computador, para abrir a tela como janela de aplicativo (sem barra de endereço)."""
    if os.name != "nt":
        return ""
    bases = [os.environ.get(v, "") for v in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA")]
    for rel in (r"Google\Chrome\Application\chrome.exe", r"Microsoft\Edge\Application\msedge.exe"):
        for b in bases:
            exe = os.path.join(b, rel) if b else ""
            if exe and os.path.isfile(exe):
                return exe
    return ""


def abrir_janela(url, aba=False):
    """Abre a tela numa janela própria, com o nome e o ícone do produto e sem o endereço 127.0.0.1 à vista.
    Sem Chrome nem Edge, abre no navegador padrão. 0.7.14: aba=True abre numa aba comum do navegador (opção do escritório)."""
    if aba:
        webbrowser.open(url)
        return True
    exe = navegador_app()
    if exe:
        try:
            import subprocess  # nosec B404 - só o navegador, sem shell, argumentos fixos
            subprocess.Popen([exe, f"--app={url}", "--window-size=1320,900"], close_fds=True)  # nosec B603
            return True
        except OSError:
            pass
    webbrowser.open(url)
    return False


_ATALHO_PS = ("$w = New-Object -ComObject WScript.Shell; "
              "foreach ($p in @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'))) { "
              "$f = Join-Path $p ($env:LEXSUITE_NOME + '.lnk'); if (Test-Path $f) { $s = $w.CreateShortcut($f); "
              "$s.Description = $env:LEXSUITE_DESC; "
              # 0.7.29 (dono: sem janela preta): o atalho DESTA pasta passa a abrir o pythonw direto, sem o ABRIR.bat
              "if ($env:LEXSUITE_ALVO -and ($s.WorkingDirectory -eq $env:LEXSUITE_PASTA -or $s.TargetPath -like ($env:LEXSUITE_PASTA + '\\*'))) { "
              "$s.TargetPath = $env:LEXSUITE_ALVO; $s.Arguments = $env:LEXSUITE_ARGS; $s.WorkingDirectory = $env:LEXSUITE_PASTA; $s.WindowStyle = 1 }; "
              "$s.Save() } }")


def atualizar_atalho(pasta):
    """Dica do atalho (ao passar o mouse) com o nome e a versão: "RADAR JUDICIAL 0.7.11". O nome do atalho não muda, para
    não deixar atalhos velhos na área de trabalho a cada versão."""
    if os.name != "nt":
        return False
    import subprocess  # nosec B404 - só powershell, sem shell, comando fixo; nome e versão vão por variável de ambiente
    m = marca(pasta)
    oculto = agendar.executavel_oculto(pasta) if os.path.isfile(os.path.join(pasta, "python", "pythonw.exe")) else ""
    env = dict(os.environ, LEXSUITE_NOME=m["nome"], LEXSUITE_DESC=f"{m['nome']} {VERSAO} - LexSuiteONE",
               LEXSUITE_ALVO=oculto, LEXSUITE_ARGS=f'"{os.path.join(pasta, "lexsuite_robo.py")}" app', LEXSUITE_PASTA=os.path.normpath(pasta))
    try:
        subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", _ATALHO_PS], env=env, timeout=30,  # nosec B603 B607
                       capture_output=True, stdin=subprocess.DEVNULL, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return True
    except (OSError, subprocess.SubprocessError):
        return False


def tela_atendeu(url, espera_s=13, dormir=None):
    """0.7.29 (dono): a tela pergunta a cada 10 s; se em 13 s ninguém atendeu o "já estava aberto", a janela foi fechada
    (no X, sem "Sair") e quem chamou abre a tela de novo."""
    import time as _t
    dormir = dormir or _t.sleep
    try:
        p = int(url.rstrip("/").rsplit(":", 1)[1])
    except (ValueError, IndexError):
        return False
    for _ in range(int(espera_s * 2)):
        dormir(0.5)
        if not _estado_sonda(p).get("chamado_pendente", True):
            return True
    return False


def chamar_tela(url, cancelar=False):
    """0.7.28: pede à tela já aberta que mostre "O RADAR já estava aberto aqui" e venha para a frente. Com `cancelar`,
    desfaz o pedido (a tela tinha sido fechada no X; a janela nova não deve dizer "já estava aberto")."""
    import http.client
    try:
        p = int(url.rstrip("/").rsplit(":", 1)[1])
        c = http.client.HTTPConnection("127.0.0.1", p, timeout=1)
        c.request("GET", "/chamar?cancelar=1" if cancelar else "/chamar", headers={"X-LexSuite": "1", "X-LexSuite-Sonda": "1", "Host": f"127.0.0.1:{p}"})
        c.getresponse().read(); c.close()
        return True
    except (OSError, ValueError, IndexError):
        return False


def procurar_aberto(portas=None, detalhe=False):
    """Endereço de uma tela do RADAR que já está aberta neste computador ("" se nenhuma). Evita a segunda janela preta
    quando a pessoa clica de novo no atalho."""
    import http.client
    for p in portas or PORTAS:
        try:
            c = http.client.HTTPConnection("127.0.0.1", p, timeout=0.6)
            c.request("GET", "/estado", headers={"X-LexSuite": "1", "X-LexSuite-Sonda": "1", "Host": f"127.0.0.1:{p}"})
            r = c.getresponse()
            d = json.loads(r.read() or b"{}")
            ok = r.status == 200 and "LexSuiteONE" in (r.getheader("Server") or "") and "rodando" in d
            c.close()
            if ok:
                return (f"http://127.0.0.1:{p}/", bool(d.get("tela_ativa"))) if detalhe else f"http://127.0.0.1:{p}/"
        except (OSError, ValueError):
            continue
    return ("", False) if detalhe else ""


def _arquivo_pid(pasta):
    return os.path.join(pasta, "saida", "programa.pid")


def gravar_pid(pasta, porta):
    """0.7.29: sem janela preta, o "Encerrar o RADAR" precisa saber qual processo é a tela (se ela travar)."""
    try:
        os.makedirs(os.path.join(pasta, "saida"), exist_ok=True)
        with open(_arquivo_pid(pasta), "w", encoding="utf-8") as f:
            json.dump({"pid": os.getpid(), "porta": int(porta), "pasta": os.path.abspath(pasta)}, f)  # 0.7.30: e de qual pasta
    except OSError:
        pass


def apagar_pid(pasta, porta):
    try:
        with open(_arquivo_pid(pasta), encoding="utf-8") as f:
            d = json.load(f)
        if int(d.get("pid") or 0) == os.getpid() and int(d.get("porta") or 0) == int(porta):
            os.remove(_arquivo_pid(pasta))
    except (OSError, ValueError, TypeError, AttributeError):
        pass


def _pedir_local(porta, rota, metodo="POST"):
    import http.client
    try:
        c = http.client.HTTPConnection("127.0.0.1", int(porta), timeout=5)
        c.request(metodo, rota, body="{}" if metodo == "POST" else None,
                  headers={"X-LexSuite": "1", "Host": f"127.0.0.1:{porta}", "Content-Type": "application/json"})
        d = json.loads(c.getresponse().read() or b"{}"); c.close()
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return None


def _pid_na_porta(porta):
    import http.client
    try:
        c = http.client.HTTPConnection("127.0.0.1", int(porta), timeout=2)
        c.request("GET", "/estado", headers={"X-LexSuite": "1", "X-LexSuite-Sonda": "1", "Host": f"127.0.0.1:{porta}"})
        d = json.loads(c.getresponse().read() or b"{}"); c.close()
        return int(d.get("pid") or 0) if isinstance(d, dict) else 0
    except (OSError, ValueError, TypeError):
        return 0


def _encerrar_processo(pid):
    import signal
    try:
        if int(pid) in (0, os.getpid()):  # nunca a si mesmo
            return False
        os.kill(int(pid), signal.SIGTERM)  # no Windows: TerminateProcess
        return True
    except (OSError, ValueError, TypeError):
        return False


def _imagem_do_processo(pid):
    """Caminho do executável do processo (Windows: QueryFullProcessImageNameW; Linux: /proc), ou "" se não souber."""
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return ""
    if os.name == "nt":
        try:
            import ctypes
            from ctypes import wintypes
            k = ctypes.windll.kernel32
            h = k.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
            if not h:
                return ""
            try:
                buf, n = ctypes.create_unicode_buffer(1024), wintypes.DWORD(1024)
                return buf.value if k.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(n)) else ""
            finally:
                k.CloseHandle(h)
        except (OSError, AttributeError, ValueError):
            return ""
    try:
        return os.path.realpath(f"/proc/{pid}/exe")
    except OSError:
        return ""


def _e_python(pid):
    """Revisão da 0.7.29 (bloqueio): só se encerra à força um processo cujo executável é o Python."""
    nome = str(_imagem_do_processo(pid) or "").replace("\\", "/").rsplit("/", 1)[-1].lower()  # caminho do Windows ou não
    return nome in ("python.exe", "pythonw.exe") or (os.name != "nt" and nome.startswith("python"))


def _dono_da_porta(porta):
    """Windows: o pid que escuta em 127.0.0.1:porta (netstat -ano), ou 0. Serve para a tela travada que não responde."""
    if os.name != "nt":
        return 0
    import subprocess  # nosec B404 - só o netstat do Windows, lista fixa, sem shell
    try:
        r = subprocess.run(["netstat", "-ano", "-p", "TCP"], capture_output=True, timeout=20, shell=False,  # nosec B603 B607
                           stdin=subprocess.DEVNULL, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except (OSError, subprocess.SubprocessError):
        return 0
    return pid_no_netstat((r.stdout or b"").decode("ascii", "replace"), porta)


def pid_no_netstat(texto, porta):
    """O pid que escuta em 127.0.0.1:porta na saída do `netstat -ano` (igual em qualquer idioma: só números e endereços)."""
    for linha in str(texto or "").splitlines():
        partes = linha.split()
        if len(partes) >= 5 and partes[1] == f"127.0.0.1:{int(porta)}" and partes[2] in ("0.0.0.0:0", "*:*"):
            try:
                return int(partes[-1])
            except ValueError:
                return 0
    return 0


def _ler_pid(pasta):
    try:
        with open(_arquivo_pid(pasta), encoding="utf-8") as f:
            d = json.load(f)
        if d.get("pasta") and not _mesma_pasta(d["pasta"], pasta):  # revisão da 0.7.29: programa.pid copiado de outra pasta
            return 0, 0
        return int(d.get("pid") or 0), int(d.get("porta") or 0)
    except (OSError, ValueError, TypeError, AttributeError):
        return 0, 0


def _mesma_pasta(a, b):
    return os.path.normcase(os.path.abspath(str(a or ""))) == os.path.normcase(os.path.abspath(str(b or "")))


def encerrar_aberto(pasta, aviso=print, espera_s=15, dormir=None, portas=None):
    """0.7.29 (dono: sem janela preta): "Encerrar o RADAR" do DIAGNOSTICO.bat. Pede à tela DESTA pasta para interromper
    a leitura e sair; se ela não sair, encerra à força só o processo que a própria tela informou, que é o do
    programa.pid e é o Python. A tela travada (não responde) só é encerrada se o Windows confirmar que é ela quem
    escuta na porta do programa.pid. Leitura agendada noutro processo: pede para parar (parar.json) e espera; nunca é
    encerrada à força (o número do processo pode ter sido reaproveitado pelo Windows). Devolve True se havia algo."""
    import time as _t
    dormir = dormir or _t.sleep
    achou = False
    pid_arq, porta_arq = _ler_pid(pasta)
    url = procurar_aberto(portas or ([porta_arq] + [p for p in PORTAS if p != porta_arq] if porta_arq else None))
    porta = int(url.rstrip("/").rsplit(":", 1)[1]) if url else 0
    pasta_tela = _estado_sonda(porta).get("pasta") if url else ""
    if url and not (pasta_tela and _mesma_pasta(pasta_tela, pasta)):
        url = ""  # é o RADAR de outra pasta (ou não disse qual): não é este que se pediu para encerrar
    if url:
        achou = True
        _pedir_local(porta, "/interromper")
        for _ in range(int(espera_s)):
            r = _pedir_local(porta, "/sair")
            if r is None or r.get("ok"):
                break
            dormir(1)
        saiu = False
        for _ in range(12):  # o programa sai meio segundo depois de responder ao /sair
            dormir(0.5)
            saiu = not procurar_aberto([porta])
            if saiu:
                break
        if not saiu:
            pid_tela = _pid_na_porta(porta)
            if pid_tela and pid_tela == pid_arq and porta == porta_arq and processo_vivo(pid_tela) and _e_python(pid_tela):
                saiu = _encerrar_processo(pid_tela)
        aviso("  Tela do RADAR encerrada. / RADAR screen closed." if saiu else MSG_NAO_ENCERROU)
    elif pid_arq and processo_vivo(pid_arq) and _e_python(pid_arq) and not _estado_sonda(porta_arq):  # tela travada (não responde)
        achou = True
        if porta_arq and _dono_da_porta(porta_arq) == pid_arq and _encerrar_processo(pid_arq):
            aviso("  Tela do RADAR (travada) encerrada. / Stuck RADAR screen closed.")
        else:
            aviso(MSG_NAO_ENCERROU)
    outra = leitura_em_outro_processo(os.path.join(pasta, "saida", "leitura.json"))
    if outra and int(outra.get("pid") or 0) != os.getpid():
        achou = True
        try:
            os.makedirs(os.path.join(pasta, "saida"), exist_ok=True)
            with open(os.path.join(pasta, "saida", "parar.json"), "w", encoding="utf-8") as f:
                json.dump({"quando": dt.datetime.now().isoformat(timespec="seconds"), "quem": "encerrar"}, f)
        except OSError:
            pass
        parou = False
        for _ in range(30):
            dormir(1)
            if not leitura_em_outro_processo(os.path.join(pasta, "saida", "leitura.json")):
                parou = True
                break
        aviso("  Leitura em andamento interrompida. / Reading in progress stopped." if parou else
              "  Pedi para a leitura parar: ela para no próximo ponto seguro (pode levar alguns minutos). / The reading will stop at the next safe point.")
    return achou


MSG_NAO_ENCERROU = ("  Não consegui encerrar o RADAR por aqui. Abra o Gerenciador de Tarefas (Ctrl+Shift+Esc), procure \"Python\" "
                    "e clique em Finalizar tarefa; ou reinicie o computador. / Could not close RADAR: end \"Python\" in Task Manager.")


def _estado_sonda(porta):
    import http.client
    try:
        c = http.client.HTTPConnection("127.0.0.1", int(porta), timeout=2)
        c.request("GET", "/estado", headers={"X-LexSuite": "1", "X-LexSuite-Sonda": "1", "Host": f"127.0.0.1:{porta}"})
        d = json.loads(c.getresponse().read() or b"{}"); c.close()
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def reiniciar_depois(servidor, pasta):
    """Depois de atualizar: abre o programa novo (outra janela preta, sem abrir outra tela) e encerra este. A tela
    aberta no navegador espera o novo responder e recarrega sozinha."""
    import subprocess  # nosec B404 - só o próprio programa, sem shell, argumentos fixos
    import sys
    porta = servidor.server_address[1]
    exe = agendar.executavel_oculto(pasta) or sys.executable  # 0.7.29: o programa novo também sem janela preta
    args = [exe, os.path.join(pasta, "lexsuite_robo.py"), "app", "--sem-navegador", "--espera", "--porta", str(porta)]
    sem_janela = os.path.basename(exe).lower().startswith("pythonw")
    try:
        subprocess.Popen(args, cwd=pasta, close_fds=True,  # nosec B603
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW" if sem_janela else "CREATE_NEW_CONSOLE", 0))
    except OSError:
        return False
    threading.Timer(0.8, servidor.shutdown).start()
    return True


def criar(pasta, porta=None, espera=0):
    import time
    limite = time.monotonic() + espera
    while True:
        for p in ([int(porta)] if porta else list(PORTAS)):
            try:
                return Servidor(("127.0.0.1", p), pasta)
            except OSError:
                continue
        if time.monotonic() >= limite:
            break
        time.sleep(0.5)  # reinício depois de atualizar: espera o programa antigo liberar a porta
    raise SystemExit("  Nenhuma porta livre entre 8765 e 8775. Feche outra janela do LexSuiteONE e tente de novo.")


def _prefere_aba(pasta):
    try:
        return bool(config.carregar(os.path.join(pasta, "config.json"), aviso=lambda *_: None)["radar"].get("abrir_em_aba"))
    except Exception:  # noqa: BLE001 - na dúvida, a janela própria de sempre
        return False


FECHAR_SEM_TELA_S = 180  # 0.7.16: a tela pergunta o estado a cada 30 s; sem pergunta por 3 minutos, ela foi fechada


def vigiar_tela(servidor, aviso=print, limite_s=FECHAR_SEM_TELA_S, passo_s=15, relogio=None, dormir=None):
    """Fecha a janela preta quando a tela foi fechada (nenhum pedido por `limite_s`) e não há leitura nem planilha à
    espera nesta janela. Se o computador dormiu (o relógio pulou), recomeça a contar."""
    import time as _t
    relogio, dormir = relogio or _t.monotonic, dormir or _t.sleep
    anterior = relogio()
    while True:
        dormir(passo_s)
        agora = relogio()
        if agora - anterior > max(60, passo_s * 4):  # acordou de repouso: dá tempo de a tela voltar a falar
            servidor.ultimo_pedido = agora
        anterior = agora
        ocupado = servidor.estado.rodando or getattr(servidor, "_planilha_tentando", False) or (getattr(servidor, "hist", {}) or {}).get("rodando")
        if ocupado:
            servidor.ultimo_pedido = agora
            continue
        if agora - servidor.ultimo_pedido > limite_s:
            aviso("  A tela foi fechada: encerro o programa (a leitura automática continua marcada no Windows).")
            servidor.shutdown()
            return True


def servir(pasta, porta=None, abrir=True, aviso=print, espera=False):
    if not espera:
        ja, ativa = procurar_aberto(detalhe=True)
        if ja:
            import time
            atendeu = ativa and chamar_tela(ja) and tela_atendeu(ja)
            if ativa and not atendeu:
                chamar_tela(ja, cancelar=True)
            if atendeu:  # 0.7.28 (dono): a tela já está aberta; não abre outra, ela avisa e vem para a frente
                m_ = marca(pasta)  # revisão da 0.7.28: o nome vem da marca, não fixo
                aviso(f"  O {m_['curto']} já está aberto neste computador. Procure a janela \"{m_['nome']}\" na barra de tarefas;")
                aviso(f"  ela mostra o aviso \"O {m_['curto']} já estava aberto aqui\". Esta janela fecha sozinha.")
                aviso(f"  / {m_['curto']} is already open: look for the {m_['nome']} window on the taskbar.")
                time.sleep(6)
                return
            aviso("  O RADAR já está aberto neste computador: trazendo a tela. Esta janela fecha sozinha.")
            if abrir:
                abrir_janela(ja, aba=_prefere_aba(pasta))
            time.sleep(3)
            return
    servidor = criar(pasta, porta, espera=20 if espera else 0)
    url = f"http://127.0.0.1:{servidor.server_address[1]}/"
    aviso(f"  LexSuiteONE aberto em {url}")
    aviso("  Para encerrar: menu ☰ → Sair (ou feche a tela: o programa se encerra sozinho 3 minutos depois).")
    titulo_janela(f"{marca(pasta).get('nome', 'RADAR JUDICIAL')} - LexSuiteONE")  # só aparece com ABRIR.bat --ver
    gravar_pid(pasta, servidor.server_address[1])
    if abrir:
        threading.Timer(0.6, lambda: abrir_janela(url, aba=_prefere_aba(pasta))).start()

    def migrar():
        try:
            msg = agendar.migrar_antigas(pasta, servidor.config()) or agendar.migrar_para_oculta(pasta, servidor.config())
            if msg:
                aviso("  " + msg)
            atualizar_atalho(pasta)
        except Exception:  # migrar a leitura automática nunca impede a tela de abrir
            pass
    threading.Thread(target=migrar, daemon=True, name="migrar-agenda").start()
    threading.Thread(target=vigiar_tela, args=(servidor, aviso), daemon=True, name="vigiar-tela").start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()
        apagar_pid(pasta, servidor.server_address[1])
