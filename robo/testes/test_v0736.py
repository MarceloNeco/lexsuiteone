"""0.7.36 (teste do dono na 0.7.35 e ressalvas da Operação): dados fictícios, sem internet."""

import http.client
import json
import os
import re
import sys
import tempfile
import threading
import unittest
from unittest import mock

_ROBO_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROBO_)

from lexsuite import app, conta, radar  # noqa: E402


def ler(*partes):
    with open(os.path.join(_ROBO_, *partes), encoding="utf-8") as f:
        return f.read()


CFG = {"conta": {"codigo": "LEX-ABCD-EFGH", "instalacao": "0123456789abcdef", "resposta": "aceite_pendente",
                 "aceite": {"aceito": False, "link": "https://judicial.solverone.com.br/aceite.html#codigo=LEX-ABCD-EFGH"}},
       "radar": {"tribunais": ["TRT2"]}}


class Servidor(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.mkdtemp()
        with open(os.path.join(self.pasta, "config.json"), "w", encoding="utf-8") as f:
            json.dump(CFG, f)
        self.srv = app.Servidor(("127.0.0.1", 0), self.pasta)
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.addCleanup(self.srv.server_close)
        self.addCleanup(self.srv.shutdown)

    def pedir(self, rota, corpo=None):
        c = http.client.HTTPConnection("127.0.0.1", self.srv.server_address[1], timeout=20)
        c.request("POST", rota, body=json.dumps(corpo or {}), headers={"X-LexSuite": "1", "Content-Type": "application/json"})
        r = c.getresponse(); d = json.loads(r.read()); c.close(); return d


class ConferirOcupado(Servidor):
    """Ressalva (1) da Operação: com leitura em andamento, a rota diz "ocupado" e não vai à internet."""

    def test_durante_a_leitura_diz_ocupado_sem_rede(self):
        self.srv.estado.rodando = True
        self.addCleanup(setattr, self.srv.estado, "rodando", False)
        with mock.patch.object(conta.rede, "pedir_json") as rede_:
            d = self.pedir("/conta/conferir")
        rede_.assert_not_called()
        self.assertFalse(d["ok"]); self.assertTrue(d.get("ocupado")); self.assertNotIn("sem_internet", d)
        self.assertFalse(d["conta"]["ok"])
        with open(os.path.join(self.pasta, "config.json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["conta"]["resposta"], "aceite_pendente")

    def test_sem_leitura_nao_diz_ocupado(self):
        nuvem = lambda url, corpo, **k: {"ok": True, "aceite": {"aceito": True}}
        with mock.patch.object(conta.rede, "pedir_json", side_effect=nuvem):
            d = self.pedir("/conta/conferir")
        self.assertTrue(d["ok"]); self.assertNotIn("ocupado", d)


class SinalNoItem(unittest.TestCase):
    """Ressalva (2): o item que vai para a tela (/dados) leva o sinal pelo texto quando a ação não o tem anotado."""

    def test_item_sem_sinal_recebe_pelo_texto(self):
        lead = {"processo": "0000001-00.2026.5.02.0001", "tribunal": "TRT2", "data": "2026-11-10", "empresa": "Empresa Exemplo Ltda",
                "texto_curto": "Fica designada audiência inicial para 10/12", "sinal": ""}
        try:
            it = radar.item_de_lead(lead, {"valor_minimo": 0})
        except Exception as e:  # o formato do lead mudou: o teste precisa acompanhar
            self.fail(f"item_de_lead falhou com lead mínimo: {e!r}")
        self.assertEqual(it["sinal"], "audiência inicial")
        lead["sinal"] = "citação inicial"
        self.assertEqual(radar.item_de_lead(lead, {"valor_minimo": 0})["sinal"], "citação inicial")


class Tela0736A(unittest.TestCase):
    """Ressalvas (1), (3) a (6) da Operação, na tela."""

    def setUp(self):
        self.h = ler("radar_modelo.html")

    def test_quarto_estado_e_textos(self):
        self.assertIn('if (r.ocupado) return "ocupado";', self.h)
        self.assertIn('lic_ocupado: "Há uma leitura em andamento; ela confere a licença sozinha."', self.h)
        self.assertIn('lic_ocupado: "A reading is running; it checks the licence by itself."', self.h)

    def test_trocar_licenca_encadeado(self):
        self.assertIn("Promise.resolve(depois_).then(function () { return conferirConta(); })", self.h)

    def test_ler_o_diario_mostra_conferindo(self):
        self.assertIn('avisoRapidoApp(t("conferindo_lic"), "nota-g")', self.h)

    def test_avisos_nao_se_empilham(self):
        self.assertIn('if (v_.textContent === txt) v_.parentNode.removeChild(v_);', self.h)

    def test_menu_abrir_pasta_texto_proprio(self):
        self.assertIn('oque === "pasta" ? t("pasta_ainda_nao")', self.h)

    def test_conferir_agora_mostra_que_trabalha_e_ativa_em_verde(self):
        self.assertIn('b_.textContent = t("lic_conferindo_btn")', self.h)
        self.assertIn('el("b", "lic-ativa", t("lic_ativa"))', self.h)

    def test_novidades_sem_frase_de_efeito(self):
        self.assertIn('"Mensagem ao encerrar o programa."', self.h)
        self.assertNotIn("Mensagem clara quando", self.h)


if __name__ == "__main__":
    unittest.main()
