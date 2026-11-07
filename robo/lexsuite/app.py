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

from . import VERSAO, agendar, assinatura, atualizar, banco as bd, compartilhar, config, preferencias, radar, rede, tribunais

PORTAS = range(8765, 8776)


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
                situacao = radar.executar(cfg, banco, self.estado.aviso, self.pasta, dias=dias, versao=VERSAO)
                self.estado.terminar(situacao)
            except (rede.BloqueadoForaDoBrasil, radar.RoboDesligado) as e:
                self.estado.aviso(str(e))
                self.estado.terminar(erro=str(e))
            except Exception as e:  # a tela precisa saber que parou, qualquer que seja o motivo
                self.estado.aviso(f"Erro: {e.__class__.__name__}: {e}")
                self.estado.terminar(erro=f"{e.__class__.__name__}: {e}")

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

    def _da_propria_pagina(self):
        host = self.headers.get("Host", "")
        origem = self.headers.get("Origin") or self.headers.get("Referer") or ""
        return self.headers.get("X-LexSuite") == "1" and (origem == "" or origem.startswith("http://" + host))

    def do_GET(self):
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
                "tribunais": tribunais.TRIBUNAIS, "ramos": tribunais.RAMOS, "regioes": tribunais.REGIOES, "ufs": tribunais.UFS,
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
            }
            return self._responder(pagina)
        if u.path == "/estado":
            return self._responder(s.estado.como_dict())
        if u.path == "/pastas":
            cfg = s.config()
            return self._responder({"candidatas": compartilhar.candidatas(), "atual": cfg["compartilhar"].get("pasta", "")})
        return self._responder({"erro": "não existe"}, status=404)

    def do_POST(self):
        caminho = urlparse(self.path).path
        if not self._da_propria_pagina():
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
            resposta = {"ok": True, "radar": r, "escritorio": cfg.get("escritorio", ""), "pasta": cfg["compartilhar"].get("pasta", "")}
            if "agendar" in corpo and agendar.disponivel():
                ok, msg = agendar.agendar(s.pasta) if corpo["agendar"] else agendar.desagendar()
                resposta.update({"agendado": agendar.agendado(), "agendar_msg": msg})
            return self._responder(resposta)
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
