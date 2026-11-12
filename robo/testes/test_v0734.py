"""0.7.34 (dono): depois do aceite dos termos, o programa confere na hora e libera (dados fictícios, sem internet)."""

import http.client
import json
import os
import re
import sqlite3
import sys
import tempfile
import threading
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_ROBO_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from lexsuite import app, banco, conta  # noqa: E402

CFG = {"conta": {"codigo": "LEX-ABCD-EFGH", "instalacao": "0123456789abcdef", "resposta": "aceite_pendente",
                 "aceite": {"aceito": False, "link": "https://judicial.solverone.com.br/aceite.html#codigo=LEX-ABCD-EFGH"}},
       "radar": {"tribunais": ["TRT2"]}}


class ConferirConta(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.mkdtemp()
        with open(os.path.join(self.pasta, "config.json"), "w", encoding="utf-8") as f:
            json.dump(CFG, f)
        self.srv = app.Servidor(("127.0.0.1", 0), self.pasta)
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.addCleanup(self.srv.shutdown)

    def pedir(self, rota, corpo=None):
        c = http.client.HTTPConnection("127.0.0.1", self.srv.server_address[1], timeout=20)
        c.request("POST", rota, body=json.dumps(corpo or {}), headers={"X-LexSuite": "1", "Content-Type": "application/json"})
        r = c.getresponse(); d = json.loads(r.read()); c.close(); return d

    def test_aceite_feito_libera_e_grava(self):
        nuvem = lambda url, corpo, **k: {"ok": True, "escritorio": "Escritório Exemplo", "aceite": {"aceito": True}}
        with mock.patch.object(conta.rede, "pedir_json", side_effect=nuvem):
            d = self.pedir("/conta/conferir")
        self.assertTrue(d["ok"]); self.assertTrue(d["conta"]["ok"])
        with open(os.path.join(self.pasta, "config.json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["conta"]["resposta"], "ok")  # gravado: a próxima abertura já vem liberada

    def test_ainda_pendente_continua_bloqueado(self):
        nuvem = lambda url, corpo, **k: {"ok": False, "motivo": "aceite_pendente", "aceite": {"aceito": False, "link": "x"}}
        with mock.patch.object(conta.rede, "pedir_json", side_effect=nuvem):
            d = self.pedir("/conta/conferir")
        self.assertFalse(d["conta"]["ok"]); self.assertEqual(d["conta"]["estado"], "aceite_pendente")

    def test_sem_internet_nao_destrava(self):
        with mock.patch.object(conta.rede, "pedir_json", side_effect=OSError("rede")):
            d = self.pedir("/conta/conferir")
        self.assertFalse(d["ok"]); self.assertTrue(d["sem_internet"]); self.assertFalse(d["conta"]["ok"])
        with open(os.path.join(self.pasta, "config.json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["conta"]["resposta"], "aceite_pendente")

    def test_durante_a_leitura_nao_vai_a_internet(self):
        self.srv.estado.rodando = True
        self.addCleanup(setattr, self.srv.estado, "rodando", False)
        with mock.patch.object(conta.rede, "pedir_json", side_effect=AssertionError("não devia chamar")):
            d = self.pedir("/conta/conferir")
        self.assertFalse(d["ok"])

    def test_grava_so_a_licenca_sobre_o_config_de_agora(self):
        caminho = os.path.join(self.pasta, "config.json")
        def nuvem(url, corpo, **k):  # enquanto confere, outra parte do programa grava o config
            with open(caminho, encoding="utf-8") as f:
                cfg = json.load(f)
            cfg["escritorio"] = "Mudado durante a conferência"
            with open(caminho, "w", encoding="utf-8") as f:
                json.dump(cfg, f)
            return {"ok": True, "aceite": {"aceito": True}}
        with mock.patch.object(conta.rede, "pedir_json", side_effect=nuvem):
            self.assertTrue(self.pedir("/conta/conferir")["conta"]["ok"])
        with open(caminho, encoding="utf-8") as f:
            cfg = json.load(f)
        self.assertEqual(cfg["escritorio"], "Mudado durante a conferência")
        self.assertEqual(cfg["conta"]["resposta"], "ok")

    def test_sem_codigo_nao_vai_a_internet(self):
        with open(os.path.join(self.pasta, "config.json"), "w", encoding="utf-8") as f:
            json.dump({"radar": {"tribunais": ["TRT2"]}}, f)
        with mock.patch.object(conta.rede, "pedir_json", side_effect=AssertionError("não devia chamar")):
            self.assertFalse(self.pedir("/conta/conferir")["ok"])


class Tela0734(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(_ROBO_, "radar_modelo.html"), encoding="utf-8") as f:
            self.h = f.read()

    def test_ler_o_diario_confere_antes_do_aviso(self):
        corpo = self.h[self.h.index("function rodar()"):]
        corpo = corpo[:corpo.index("function avisoBuscaEstatisticas")]
        self.assertIn("conferirConta().then", corpo)
        self.assertNotRegex(corpo, r"!APP\.conta\.ok\) \{ avisoLicenca\(\); return; \}")

    def test_volta_para_a_janela_e_vigia(self):
        self.assertIn('window.addEventListener("focus"', self.h)
        self.assertIn('"/conta/conferir"', self.h)
        self.assertGreaterEqual(self.h.count("vigiarAceite()"), 2)  # janela de aviso e Configurações
        for k in ("aceite_ok", "aceite_ja", "aceite_ainda"):
            self.assertEqual(len(re.findall(r"\b%s: \"" % k, self.h)), 2, k)  # PT e EN


class BancoEspera(unittest.TestCase):
    def test_timeout_maior(self):
        cam = os.path.join(tempfile.mkdtemp(), "t.db")
        with mock.patch.object(banco.sqlite3, "connect", wraps=sqlite3.connect) as c:
            banco.Banco(cam).con.close()
        self.assertEqual(c.call_args.kwargs.get("timeout"), 30)


if __name__ == "__main__":
    unittest.main()
