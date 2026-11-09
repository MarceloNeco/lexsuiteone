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
                             "Use o status (visto, em contato, descartado) para não repassar a mesma empresa duas vezes; o filtro \"Acima de\" segue o valor mínimo da aba Preferências.",
                             "Rito ordinário indica causa acima de 40 salários mínimos; sumaríssimo, até 40. É o primeiro corte de valor que o Diário permite."],
    "Estagiário ou estagiária": ["A rotina sugerida: de manhã, abrir a tela, conferir \"Última atualização\" e passar pela lista marcando o status de cada linha.",
                                 "Para as linhas com \"valor a conferir\", abrir a consulta no PJe, resolver o captcha e digitar o valor da causa na ficha.",
                                 "Cadastrar na aba Exclusões da planilha as empresas que a equipe pedir para não aparecer (nome como está no Diário, ou CNPJ, e o motivo).",
                                 "Não é preciso mexer nas abas ocultas da planilha: elas são do suporte."],
    "Equipe administrativa": ["A planilha LexSuiteONE.xlsx no Google Drive é sua: a aba Preferências ajusta a lista e a aba Exclusões guarda clientes e empresas que não devem aparecer.",
                              "O RADAR lê sozinho nos horários de Configuração (de início, 20h e 8h); se o computador estava desligado, a leitura acontece quando ele ligar.",
                              "Se a planilha estiver aberta e travada na hora de uma rodada, o robô grava na próxima. Nada se perde.",
                              "Avise o suporte quando a tela mostrar \"robô desligado\", \"precisa atualizar\" ou quando a lista vier vazia dois dias úteis seguidos."],
}


class Estado:
    """O que a tela pergunta a cada 2 segundos enquanto o robô roda."""

    def __init__(self, eco=None):
        self.lock = threading.Lock()
        self.eco = eco  # janela preta: cada passo da leitura aparece também ali, com a hora
        self.rodando = False
        self.progresso, self.total_trib, self.tribs_vistos = 0, 0, set()
        self.mensagens = []
        self.inicio = self.fim = None
        self.situacao = None
        self.erro = None
        self.erro_info = None  # 0.7.13: {causa, pt, en, detalhe}: a tela mostra o texto claro e esconde o técnico

    def aviso(self, msg):
        hora, texto = dt.datetime.now().strftime("%H:%M:%S"), str(msg).strip()
        with self.lock:
            self.mensagens.append({"hora": hora, "texto": texto})
            del self.mensagens[:-80]
            self._progredir(texto)
        self._eco(f"  {hora}  {texto}")

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
                    "fim": self.fim, "situacao": self.situacao, "erro": self.erro, "erro_info": self.erro_info}

    def comecar(self):
        with self.lock:
            if self.rodando:
                return False
            self.rodando, self.mensagens, self.erro, self.erro_info = True, [], None, None
            self.progresso, self.total_trib, self.tribs_vistos = 1, 0, set()
            self.inicio, self.fim = dt.datetime.now().isoformat(timespec="seconds"), None
        self._eco("")
        self._eco(f"  ===== Leitura começou às {dt.datetime.now():%H:%M} (não feche esta janela) =====")
        return True

    def terminar(self, situacao=None, erro=None, info=None):
        with self.lock:
            self.rodando = False
            self.fim = dt.datetime.now().isoformat(timespec="seconds")
            if situacao:
                self.situacao = situacao
            self.erro = erro
            self.erro_info = info
        fim = f"  ===== Leitura terminou às {dt.datetime.now():%H:%M}"
        self._eco(fim + (f" com erro: {erro} =====" if erro else (f": {situacao.get('pt', '')} =====" if situacao else " =====")))


class Servidor(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, endereco, pasta):
        super().__init__(endereco, Tratador)
        self.pasta = pasta
        self.estado = Estado(eco=print)
        self.versao_cache = None
        self.caminho_config = os.path.join(pasta, "config.json")
        self.caminho_db = os.path.join(pasta, "lexsuite.db")
        self.modelo = os.path.join(pasta, "radar_modelo.html")

    def config(self):
        return config.carregar(self.caminho_config, aviso=lambda *_: None)

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
                if situacao.get("aviso_planilha"):
                    self.planilha_depois()
                if cfg["radar"].get("avisar_ao_terminar", True):
                    agendar.notificar(marca(self.pasta).get("nome", "RADAR JUDICIAL"), agendar.texto_aviso(situacao, marca(self.pasta).get("curto", "RADAR")))
            except radar.RoboDesligado as e:
                self.estado.aviso(str(e))
                self.estado.terminar(erro=str(e), info={"causa": "desligado", "pt": str(e), "en": str(e), "detalhe": ""})
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
            banco = bd.Banco(s.caminho_db)
            visao = "arquivo" if qs.get("visao", [""])[0] == "arquivo" else "lista"
            pagina = radar.montar_radar(cfg, banco, situacao=s.estado.situacao, dias=dias, visao=visao)
            pagina["versao"] = VERSAO
            pagina["espaco"] = banco.espaco()
            ultimo = banco.execucoes("retorno", 1)
            pagina["retorno"] = ultimo[0] if ultimo else {}
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
                           "valor_minimo": r.get("valor_minimo"), "dias_na_pagina": r.get("dias_na_pagina"),
                           "teto_capital_gigante": r.get("teto_capital_gigante"),
                           "pasta": comp.get("pasta", ""), "subpasta": comp.get("subpasta", "LexSuiteONE"), "pasta_base": base,
                           "pasta_ok": bool(base and os.path.isdir(base)),
                           "planilha": preferencias.caminho(base) if base and os.path.exists(preferencias.caminho(base)) else "",
                           "planilha_prevista": preferencias.caminho(base) if base else "", "no_drive": compartilhar.no_google_drive(comp.get("pasta", "")),
                           "agendavel": agendar.disponivel(), "agendado": agendado,
                           "horarios": horarios, "dias": dias, "tem_noite": agendar.tem_noite(horarios),
                           "proxima": proxima.isoformat(timespec="minutes") if (agendado and proxima) else "",
                           "avisar_ao_terminar": bool(r.get("avisar_ao_terminar", True)),
                           "area_logada_por_dia": int(r.get("area_logada_por_dia") or 30),
                           "guardar_meses": int(r.get("guardar_meses") or 12)},
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
        if u.path == "/historico":  # 0.7.13: as últimas tentativas de leitura, uma por tribunal
            try:
                banco = bd.Banco(self.server.caminho_db)
                return self._responder({"tentativas": banco.execucoes("tentativa", 120)})
            except Exception:  # noqa: BLE001 - banco ausente ou ilegível: lista vazia
                return self._responder({"tentativas": []})
        if u.path == "/estado":
            return self._responder(s.estado.como_dict())
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
        if u.path == "/pastas":
            cfg = s.config()
            cand = compartilhar.candidatas()
            return self._responder({"candidatas": cand, "atual": cfg["compartilhar"].get("pasta", ""), "drive": bool(cand),
                                    "pasta_programa": s.pasta, "subpasta": compartilhar.subpasta_para(cfg, marca(s.pasta)["nome"]),
                                    "escolher": os.name == "nt"})
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
                                             corpo.get("documento") or doc_atual.get("numero"),
                                             papel_valido(corpo) if "papel" in corpo else cfg["usuario"].get("papel"),
                                             doc_tipo=corpo.get("doc_tipo") or doc_atual.get("tipo") or "cnpj")
                if not ok:
                    return self._responder({"ok": False, "motivo": motivo, "conta": conta.situacao(cfg)})
            if "horarios" in corpo:
                r["horarios"] = agendar.validar(corpo["horarios"])
            if "dias" in corpo:
                r["dias"] = agendar.validar_dias(corpo["dias"])
            if "avisar_ao_terminar" in corpo:
                r["avisar_ao_terminar"] = bool(corpo["avisar_ao_terminar"])
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
                ok, msg = agendar.agendar(s.pasta, *agendar.do_config(cfg)) if ligar else agendar.desagendar()
                resposta.update({"agendado": agendar.agendado(), "agendar_msg": msg})
            return self._responder(resposta)
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
        if caminho == "/copia-planilha":
            cfg = s.config()
            ok, resultado = compartilhar.gerar_copia(cfg)
            if ok and corpo.get("abrir", True):
                abrir_no_windows(resultado)
            return self._responder({"ok": ok, "caminho" if ok else "motivo": resultado})
        if caminho == "/contatos/preparar":
            from . import contatos as ct
            cfg = s.config()
            pagina = radar.montar_radar(cfg, bd.Banco(s.caminho_db), dias=90)
            quero = {str(x) for x in (corpo.get("processos") or []) if isinstance(x, (str, int))}
            itens = [i for i in pagina["itens"] if not quero or i["processo"] in quero]
            caminho_md, n = ct.preparar(itens, s.pasta, marca(s.pasta)["nome"], int(cfg["radar"].get("area_logada_por_dia") or 30))
            abrir_no_windows(os.path.dirname(caminho_md))
            return self._responder({"ok": True, "caminho": caminho_md, "quantos": n})
        if caminho == "/contatos/colar":
            from . import contatos as ct
            banco = bd.Banco(s.caminho_db)
            empresas = {}
            for l in banco.todos_leads():
                emp = (l.get("empresa_receita") or {}).get("razao_social") or (l.get("empresas") or [""])[0]
                empresas[l["processo"]] = emp
            aceitas, recusadas = ct.colar(str(corpo.get("texto") or "")[:200000], empresas)
            novas = sum(1 for c in aceitas if banco.guardar_contato(c))
            banco.registrar_colagem(s.config()["usuario"].get("email", ""), str(corpo.get("arquivo") or "")[:120], novas, len(recusadas),
                                    "; ".join(f"linha {r['linha']}: {r['motivo']}" for r in recusadas)[:2000])
            s.planilha_depois()
            return self._responder({"ok": True, "aceitas": novas, "repetidas": len(aceitas) - novas, "recusadas": recusadas[:200]})
        if caminho == "/abrir":
            cfg = s.config()
            base = compartilhar.pasta_base(cfg)
            planilha = preferencias.caminho(base) if base else ""
            if corpo.get("o_que") == "pasta_mae":  # a pasta escolhida, onde aparece a pasta da planilha (para compartilhar)
                alvo = os.path.dirname(base) if base else ""
            else:
                alvo = planilha if corpo.get("o_que") in ("planilha", "editar") else (os.path.dirname(planilha) if planilha else "")
            if corpo.get("o_que") == "editar":  # Preferências e Exclusões: abre normal, para o escritório poder salvar
                alvo = planilha
            elif corpo.get("o_que") == "planilha" and abrir_so_leitura(alvo):
                return self._responder({"ok": True, "so_leitura": True})
            if abrir_no_windows(alvo):
                return self._responder({"ok": True})
            return self._responder({"ok": False, "motivo": "A planilha ainda não existe. Escolha a pasta do Google Drive em Configuração e faça uma leitura.",
                                    "caminho": planilha})
        if caminho == "/testar-pasta":
            cfg = s.config()
            pasta = str(corpo.get("pasta") or "").strip()
            ok, msg = compartilhar.testar(pasta, compartilhar.subpasta_para(cfg, marca(s.pasta)["nome"]), criar=bool(corpo.get("criar")))
            return self._responder({"ok": ok, "mensagem": msg, "nao_existe": bool(pasta) and not os.path.isdir(pasta),
                                    "no_drive": compartilhar.no_google_drive(pasta)})
        if caminho == "/gravar-planilha":
            if not compartilhar.pasta_base(s.config()):
                return self._responder({"ok": False, "motivo": "Escolha a pasta da planilha em Configuração."})
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


_ESCOLHER_PS = ("Add-Type -AssemblyName System.Windows.Forms; [Console]::OutputEncoding = [Text.Encoding]::UTF8; "
                "$f = New-Object System.Windows.Forms.Form; $f.TopMost = $true; "
                "$d = New-Object System.Windows.Forms.FolderBrowserDialog; $d.Description = $env:LEXSUITE_TITULO; "
                "$d.ShowNewFolderButton = $true; if ($env:LEXSUITE_INICIO) { $d.SelectedPath = $env:LEXSUITE_INICIO }; "
                "if ($d.ShowDialog($f) -eq 'OK') { [Console]::Out.Write($d.SelectedPath) }")


def escolher_pasta(inicio=""):
    """Abre a janela de pastas do Windows e devolve a pasta escolhida ("" se cancelou ou fora do Windows)."""
    if os.name != "nt":
        return ""
    import subprocess  # nosec B404 - só powershell, sem shell, comando fixo; o texto vai por variável de ambiente
    env = dict(os.environ, LEXSUITE_TITULO="Escolha a pasta da planilha (de preferência dentro do Meu Drive / My Drive)",
               LEXSUITE_INICIO=inicio if os.path.isdir(inicio) else "")
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-STA", "-Command", _ESCOLHER_PS],  # nosec B603 B607
                           capture_output=True, env=env, timeout=600, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
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


def abrir_janela(url):
    """Abre a tela numa janela própria, com o nome e o ícone do produto e sem o endereço 127.0.0.1 à vista.
    Sem Chrome nem Edge, abre no navegador padrão."""
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
              "$s.Description = $env:LEXSUITE_DESC; $s.Save() } }")


def atualizar_atalho(pasta):
    """Dica do atalho (ao passar o mouse) com o nome e a versão: "RADAR JUDICIAL 0.7.11". O nome do atalho não muda, para
    não deixar atalhos velhos na área de trabalho a cada versão."""
    if os.name != "nt":
        return False
    import subprocess  # nosec B404 - só powershell, sem shell, comando fixo; nome e versão vão por variável de ambiente
    m = marca(pasta)
    env = dict(os.environ, LEXSUITE_NOME=m["nome"], LEXSUITE_DESC=f"{m['nome']} {VERSAO} - LexSuiteONE")
    try:
        subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", _ATALHO_PS], env=env, timeout=30,  # nosec B603 B607
                       capture_output=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return True
    except (OSError, subprocess.SubprocessError):
        return False


def procurar_aberto(portas=None):
    """Endereço de uma tela do RADAR que já está aberta neste computador ("" se nenhuma). Evita a segunda janela preta
    quando a pessoa clica de novo no atalho."""
    import http.client
    for p in portas or PORTAS:
        try:
            c = http.client.HTTPConnection("127.0.0.1", p, timeout=0.6)
            c.request("GET", "/estado", headers={"X-LexSuite": "1", "Host": f"127.0.0.1:{p}"})
            r = c.getresponse()
            ok = r.status == 200 and "LexSuiteONE" in (r.getheader("Server") or "") and "rodando" in json.loads(r.read() or b"{}")
            c.close()
            if ok:
                return f"http://127.0.0.1:{p}/"
        except (OSError, ValueError):
            continue
    return ""


def reiniciar_depois(servidor, pasta):
    """Depois de atualizar: abre o programa novo (outra janela preta, sem abrir outra tela) e encerra este. A tela
    aberta no navegador espera o novo responder e recarrega sozinha."""
    import subprocess  # nosec B404 - só o próprio programa, sem shell, argumentos fixos
    import sys
    porta = servidor.server_address[1]
    args = [sys.executable, os.path.join(pasta, "lexsuite_robo.py"), "app", "--sem-navegador", "--espera", "--porta", str(porta)]
    try:
        subprocess.Popen(args, cwd=pasta, close_fds=True,  # nosec B603
                         creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0))
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


def servir(pasta, porta=None, abrir=True, aviso=print, espera=False):
    if not espera:
        ja = procurar_aberto()
        if ja:
            aviso("  O RADAR já está aberto neste computador: trazendo a tela. Esta janela fecha sozinha.")
            if abrir:
                abrir_janela(ja)
            import time
            time.sleep(3)
            return
    servidor = criar(pasta, porta, espera=20 if espera else 0)
    url = f"http://127.0.0.1:{servidor.server_address[1]}/"
    aviso(f"  LexSuiteONE aberto em {url}")
    aviso("  Deixe esta janela aberta enquanto usa a tela. Para encerrar, feche a janela (ou Ctrl+C).")
    titulo_janela(f"{marca(pasta).get('nome', 'RADAR JUDICIAL')} - não feche esta janela")
    if abrir:
        threading.Timer(0.6, lambda: abrir_janela(url)).start()

    def migrar():
        try:
            msg = agendar.migrar_antigas(pasta, servidor.config())
            if msg:
                aviso("  " + msg)
            atualizar_atalho(pasta)
        except Exception:  # migrar a leitura automática nunca impede a tela de abrir
            pass
    threading.Thread(target=migrar, daemon=True, name="migrar-agenda").start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()
