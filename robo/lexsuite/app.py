"""Tela local do Radar: um servidor pequeno só no próprio computador (127.0.0.1), biblioteca padrão.

A página escolhe os tribunais, manda rodar e mostra a lista. Nada sai do computador além do que o
robô já fazia (ler o DJEN e a Receita). Só aceita pedidos do navegador desta máquina, vindos da
própria página (cabeçalho X-LexSuite); outro site aberto no navegador não consegue mandar rodar.
"""

import datetime as dt
import json
import os
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from . import VERSAO, agendar, assinatura, atualizar, banco as bd, cnpj, compartilhar, config, conta, preferencias, radar, rede, tribunais

PORTAS = range(8765, 8776)
PAPEIS = ("Sócio ou sócia", "Advogado ou advogada", "Estagiário ou estagiária", "Equipe administrativa")

# O manual fala com a pessoa pelo papel dela (texto curto; o manual inteiro continua valendo para todos).
PARA_VOCE = {
    "Sócio ou sócia": ["A lista é um catálogo de oportunidades, não uma recomendação: a regra separa ações novas contra empresas e deixa a triagem com você.",
                       "Para saber se o robô está rodando, basta a linha \"Última atualização\" no alto da tela ou a aba oculta Log da planilha.",
                       "O uso dos contatos das empresas e dos nomes de sócios é decisão sua e do compliance; o ajuste \"Mostrar sócios e administradores\" desliga esses nomes.",
                       "Nada aqui usa inteligência artificial nem tem custo por uso: o robô lê fontes públicas e roda no seu computador."],
    "Advogado ou advogada": ["Clique na linha e a ficha abre: vara, rito, data do Diário, empresa, atividade, porte, capital social e contatos do cadastro público.",
                             "O valor da causa fica atrás do captcha do PJe: \"Abrir consulta no PJe\", cole o número, veja o valor e digite na ficha. Ele sai na planilha exportada.",
                             "Use o status (visto, em contato, descartado) para não repassar a mesma empresa duas vezes; o filtro \"Acima de\" segue o valor mínimo da aba Preferências.",
                             "Rito ordinário indica causa acima de 40 salários mínimos; sumaríssimo, até 40. É o primeiro corte de valor que o Diário permite."],
    "Estagiário ou estagiária": ["A rotina sugerida: de manhã, abrir a tela, conferir \"Última atualização\" e passar pela lista marcando o status de cada linha.",
                                 "Para as linhas com \"valor a conferir\", abrir a consulta no PJe, resolver o captcha e digitar o valor da causa na ficha.",
                                 "Cadastrar na aba Exclusões da planilha as empresas que a equipe pedir para não aparecer (nome como está no Diário, ou CNPJ, e o motivo).",
                                 "Não é preciso mexer nas abas ocultas da planilha: elas são do suporte."],
    "Equipe administrativa": ["A planilha LexSuiteONE.xlsx no Google Drive é sua: a aba Preferências ajusta a lista e a aba Exclusões guarda clientes e empresas que não devem aparecer.",
                              "O robô roda sozinho às 19:40 e às 07:10 com o computador ligado; se o computador ficou desligado, a próxima rodada compensa.",
                              "Se a planilha estiver aberta e travada na hora de uma rodada, o robô grava na próxima. Nada se perde.",
                              "Avise o suporte quando a tela mostrar \"robô desligado\", \"precisa atualizar\" ou quando a lista vier vazia dois dias úteis seguidos."],
}


class Estado:
    """O que a tela pergunta a cada 2 segundos enquanto o robô roda."""

    def __init__(self):
        self.lock = threading.Lock()
        self.rodando = False
        self.mensagens = []
        self.inicio = self.fim = None
        self.situacao = None
        self.erro = None

    def aviso(self, msg):
        with self.lock:
            self.mensagens.append({"hora": dt.datetime.now().strftime("%H:%M:%S"), "texto": str(msg).strip()})
            del self.mensagens[:-80]

    def como_dict(self):
        with self.lock:
            return {"rodando": self.rodando, "mensagens": list(self.mensagens[-15:]), "inicio": self.inicio,
                    "fim": self.fim, "situacao": self.situacao, "erro": self.erro}

    def comecar(self):
        with self.lock:
            if self.rodando:
                return False
            self.rodando, self.mensagens, self.erro = True, [], None
            self.inicio, self.fim = dt.datetime.now().isoformat(timespec="seconds"), None
            return True

    def terminar(self, situacao=None, erro=None):
        with self.lock:
            self.rodando = False
            self.fim = dt.datetime.now().isoformat(timespec="seconds")
            if situacao:
                self.situacao = situacao
            self.erro = erro


class Servidor(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, endereco, pasta):
        super().__init__(endereco, Tratador)
        self.pasta = pasta
        self.estado = Estado()
        self.caminho_config = os.path.join(pasta, "config.json")
        self.caminho_db = os.path.join(pasta, "lexsuite.db")
        self.modelo = os.path.join(pasta, "radar_modelo.html")

    def config(self):
        return config.carregar(self.caminho_config, aviso=lambda *_: None)

    def rodar(self, dias=None):
        """Começa uma rodada numa thread. Devolve False se já há uma rodando."""
        if not self.estado.comecar():
            return False

        def alvo():
            try:
                cfg = self.config()
                banco = bd.Banco(self.caminho_db)
                situacao = radar.executar(cfg, banco, self.estado.aviso, self.pasta, dias=dias, versao=VERSAO,
                                          caminho_config=self.caminho_config)
                self.estado.terminar(situacao)
            except radar.RoboDesligado as e:
                self.estado.aviso(str(e))
                self.estado.terminar(erro=str(e))
            except rede.BloqueadoForaDoBrasil as e:
                self.estado.aviso(str(e))
                self.estado.terminar(erro=str(e))
                conta.registrar_erro(self.config(), VERSAO, "leitura: fora do Brasil", str(e))
            except Exception as e:  # a tela precisa saber que parou, qualquer que seja o motivo
                self.estado.aviso(f"Erro: {e.__class__.__name__}: {e}")
                self.estado.terminar(erro=f"{e.__class__.__name__}: {e}")
                import traceback
                conta.registrar_erro(self.config(), VERSAO, "leitura pela tela", traceback.format_exc()[-1800:])

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
        u = urlparse(self.path)
        qs = parse_qs(u.query)
        s = self.server
        if u.path in ("/", "/index.html"):
            with open(s.modelo, "rb") as f:
                return self._responder(f.read(), "text/html; charset=utf-8")
        if u.path == "/dados":
            cfg = s.config()
            r = cfg["radar"]
            try:
                dias = max(1, min(90, int(qs.get("dias", [r.get("dias_na_pagina", 1)])[0])))
            except (TypeError, ValueError):
                dias = 1
            pagina = radar.montar_radar(cfg, bd.Banco(s.caminho_db), situacao=s.estado.situacao, dias=dias)
            pagina["versao"] = VERSAO
            comp = cfg["compartilhar"]
            base = compartilhar.pasta_base(cfg)
            chave = atualizar.chave_publica(s.pasta)
            pagina["app"] = {
                "usuario": {"nome": cfg["usuario"].get("nome", ""), "papel": cfg["usuario"].get("papel", ""), "email": cfg["usuario"].get("email", "")},
                "papeis": list(PAPEIS), "documento_escritorio": cfg.get("documento_escritorio") or {},
                "tribunais": [x for x in tribunais.TRIBUNAIS if x["ramo"] in FRENTES], "ramos": [r for r in tribunais.RAMOS if r in FRENTES], "regioes": tribunais.REGIOES, "ufs": tribunais.UFS,
                "config": {"tribunais": tribunais.validar(r.get("tribunais")), "escritorio": cfg.get("escritorio", ""),
                           "valor_minimo": r.get("valor_minimo"), "dias_na_pagina": r.get("dias_na_pagina"),
                           "teto_capital_gigante": r.get("teto_capital_gigante"),
                           "pasta": comp.get("pasta", ""), "subpasta": comp.get("subpasta", "LexSuiteONE"), "pasta_base": base,
                           "pasta_ok": bool(base and os.path.isdir(base)),
                           "planilha": preferencias.caminho(base) if base and os.path.exists(preferencias.caminho(base)) else "",
                           "agendavel": agendar.disponivel(), "agendado": agendar.agendado()},
                "atualizacao": {"chave": bool(chave), "impressao": assinatura.impressao(chave) if chave else "",
                                "url": cfg["atualizacao"].get("url", ""), "pasta": compartilhar.pasta_atualizacao(cfg)},
                "versao": VERSAO, "estado": s.estado.como_dict(), "pasta_robo": s.pasta,
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
        if u.path == "/estado":
            return self._responder(s.estado.como_dict())
        if u.path == "/manual":
            manual = os.path.join(s.pasta, "MANUAL-DO-ESCRITORIO.html")
            if not os.path.exists(manual):
                return self._responder({"erro": "manual não encontrado"}, status=404)
            with open(manual, encoding="utf-8") as f:
                html = f.read()
            return self._responder(personalizar_manual(html, s.config()).encode("utf-8"), "text/html; charset=utf-8")
        if u.path == "/pastas":
            cfg = s.config()
            return self._responder({"candidatas": compartilhar.candidatas(), "atual": cfg["compartilhar"].get("pasta", "")})
        return self._responder({"erro": "não existe"}, status=404)

    def do_POST(self):
        caminho = urlparse(self.path).path
        if not self._host_local() or not self._da_propria_pagina():
            return self._responder({"erro": "pedido recusado"}, status=403)
        try:
            tamanho = int(self.headers.get("Content-Length") or 0)
            corpo = json.loads(self.rfile.read(tamanho) or b"{}")
        except ValueError:
            return self._responder({"erro": "JSON inválido"}, status=400)
        if not isinstance(corpo, dict):
            corpo = {}
        s = self.server
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
                    except (TypeError, ValueError):
                        pass
            if "escritorio" in corpo:
                cfg["escritorio"] = str(corpo["escritorio"] or "").strip()[:80]
            if "codigo" in corpo:
                # Código de cliente: confere na hora com a SolverONE; código errado não é salvo.
                cfg.setdefault("conta", {})["codigo"] = conta.normalizar(corpo["codigo"])
                c = conta.verificar(cfg, VERSAO)
                if c.get("resposta") not in ("ok", "sem_resposta"):
                    return self._responder({"ok": False, "motivo": conta.bloqueio(cfg), "conta": conta.situacao(cfg)})
                if c.get("resposta") == "sem_resposta" and not c.get("ultima_ok"):
                    return self._responder({"ok": False, "motivo": "Não consegui falar com a SolverONE para confirmar o código. "
                                                                    "Confira a internet e tente de novo.", "conta": conta.situacao(cfg)})
                if c.get("escritorio_licenca") and not cfg.get("escritorio"):
                    cfg["escritorio"] = c["escritorio_licenca"]
            if "email" in corpo:
                # Cadastro de quem usa: o e-mail é a chave (um e-mail, um escritório). Vai para a licença na SolverONE.
                if "escritorio" in corpo:
                    cfg["escritorio"] = str(corpo["escritorio"] or "").strip()[:80]
                doc_atual = cfg.get("documento_escritorio") or {}
                ok, motivo = conta.cadastrar(cfg, VERSAO, corpo.get("email"), corpo.get("nome") or cfg["usuario"].get("nome"),
                                             corpo.get("documento") or doc_atual.get("numero"), corpo.get("papel") or cfg["usuario"].get("papel"),
                                             doc_tipo=corpo.get("doc_tipo") or doc_atual.get("tipo") or "cnpj")
                if not ok:
                    return self._responder({"ok": False, "motivo": motivo, "conta": conta.situacao(cfg)})
            if "nome" in corpo:
                cfg["usuario"]["nome"] = str(corpo["nome"] or "").strip()[:60]
            if "papel" in corpo:
                cfg["usuario"]["papel"] = corpo["papel"] if corpo["papel"] in PAPEIS else ""
            if "pasta" in corpo:
                pasta = str(corpo["pasta"] or "").strip()
                if pasta and not os.path.isdir(pasta):
                    return self._responder({"ok": False, "motivo": "Essa pasta não existe neste computador."})
                cfg["compartilhar"]["pasta"] = pasta
                if pasta:
                    ok, msg = compartilhar.testar(pasta, cfg["compartilhar"].get("subpasta") or "LexSuiteONE")
                    if not ok:
                        return self._responder({"ok": False, "motivo": msg})
                    try:
                        compartilhar.criar_se_faltar(cfg, VERSAO, s.pasta, s.estado.aviso)
                    except Exception as e:
                        return self._responder({"ok": False, "motivo": f"Não consegui criar a planilha ({e.__class__.__name__})."})
            config.salvar(s.caminho_config, cfg)
            resposta = {"ok": True, "radar": r, "escritorio": cfg.get("escritorio", ""), "pasta": cfg["compartilhar"].get("pasta", ""),
                        "conta": conta.situacao(cfg)}
            if "agendar" in corpo and agendar.disponivel():
                ok, msg = agendar.agendar(s.pasta) if corpo["agendar"] else agendar.desagendar()
                resposta.update({"agendado": agendar.agendado(), "agendar_msg": msg})
            return self._responder(resposta)
        if caminho == "/abrir":
            cfg = s.config()
            base = compartilhar.pasta_base(cfg)
            planilha = preferencias.caminho(base) if base else ""
            alvo = planilha if corpo.get("o_que") == "planilha" else (os.path.dirname(planilha) if planilha else "")
            if abrir_no_windows(alvo):
                return self._responder({"ok": True})
            return self._responder({"ok": False, "motivo": "A planilha ainda não existe. Escolha a pasta do Google Drive em Configuração e faça uma leitura.",
                                    "caminho": planilha})
        if caminho == "/testar-pasta":
            ok, msg = compartilhar.testar(str(corpo.get("pasta") or "").strip(), s.config()["compartilhar"].get("subpasta") or "LexSuiteONE")
            return self._responder({"ok": ok, "mensagem": msg})
        if caminho == "/atualizar":
            if s.estado.como_dict()["rodando"]:
                return self._responder({"ok": False, "motivo": "espere a rodada terminar"})
            recados = []
            resultado = atualizar.atualizar(s.pasta, s.config(), VERSAO, recados.append, instalar_agora=bool(corpo.get("instalar", True)))
            resultado["recados"] = recados
            return self._responder(resultado)
        if caminho == "/rodar":
            if not tribunais.validar(s.config()["radar"].get("tribunais")):
                return self._responder({"ok": False, "motivo": "nenhum tribunal escolhido"})
            try:
                dias = int(corpo["dias"]) if corpo.get("dias") is not None else None
            except (TypeError, ValueError):
                dias = None
            comecou = s.rodar(dias)
            return self._responder({"ok": comecou, "motivo": "" if comecou else "já está rodando"})
        return self._responder({"erro": "não existe"}, status=404)


# Ramos oferecidos na tela: só a frente trabalhista por enquanto (os TJs e TRFs são de outras frentes).
FRENTES = ("Trabalhista",)
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


def abrir_no_windows(caminho):
    """Abre um arquivo ou pasta com o programa padrão do Windows (Excel, Explorador). Só caminhos que o próprio
    programa conhece: a planilha e a pasta dela."""
    if os.name != "nt" or not caminho or not os.path.exists(caminho):
        return False
    os.startfile(caminho)  # nosec B606 - caminho vem do config (planilha do próprio programa), nunca do pedido
    return True


def personalizar_manual(html, cfg):
    """Troca os marcadores do manual pela saudação e pelo bloco do papel da pessoa (texto escapado)."""
    import html as h
    u = cfg.get("usuario") or {}
    nome, papel, escritorio = u.get("nome", ""), u.get("papel", ""), cfg.get("escritorio", "")
    ola = ""
    if nome:
        ola = f"<p class=\"ola\">Olá, {h.escape(nome)}." + (f" Este manual é do {h.escape(escritorio)}." if escritorio else "") + "</p>"
    bloco = ""
    if papel in PARA_VOCE:
        itens = "".join(f"<li>{h.escape(t)}</li>" for t in PARA_VOCE[papel])
        bloco = f"<div class=\"caixa\"><b>Para você, {h.escape(papel.lower())}</b><ul>{itens}</ul></div>"
    return html.replace("<!--OLA-->", ola, 1).replace("<!--PARA_VOCE-->", bloco, 1)


def criar(pasta, porta=None):
    for p in ([int(porta)] if porta else list(PORTAS)):
        try:
            return Servidor(("127.0.0.1", p), pasta)
        except OSError:
            continue
    raise SystemExit("  Nenhuma porta livre entre 8765 e 8775. Feche outra janela do LexSuiteONE e tente de novo.")


def servir(pasta, porta=None, abrir=True, aviso=print):
    servidor = criar(pasta, porta)
    url = f"http://127.0.0.1:{servidor.server_address[1]}/"
    aviso(f"  LexSuiteONE aberto em {url}")
    aviso("  Deixe esta janela aberta enquanto usa a tela. Para encerrar, feche a janela (ou Ctrl+C).")
    if abrir:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()
