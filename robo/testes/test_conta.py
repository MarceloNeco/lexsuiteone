"""Licença do escritório: código de cliente conferido na nuvem da SolverONE (v0.7.7)."""
import datetime as dt
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexsuite import conta  # noqa: E402

HOJE = dt.date(2026, 11, 10)
CODIGO = "LEX-7K4M-2PQ9"


def resposta(r):
    return lambda url, corpo, **kw: r


def sem_internet(url, corpo, **kw):
    raise RuntimeError("Sem resposta")


class Codigo(unittest.TestCase):
    def test_formato(self):
        self.assertTrue(conta.valido(CODIGO))
        self.assertTrue(conta.valido("lex 7k4m 2pq9"))
        self.assertEqual(conta.normalizar("lex7k4m2pq9"), CODIGO)
        for ruim in ("", "LEX-0000-1111", "LEX-ABCD", "ABC-7K4M-2PQ9"):
            self.assertFalse(conta.valido(ruim), ruim)


class Licenca(unittest.TestCase):
    def test_sem_codigo_bloqueia(self):
        cfg = {}
        conta.verificar(cfg, "0.7.7", HOJE, pedir=resposta({"ok": True}))
        self.assertIn("código de cliente", conta.bloqueio(cfg, HOJE))

    def test_ativa_libera_e_registra_instalacao(self):
        enviado = {}
        cfg = {"conta": {"codigo": CODIGO}}
        conta.verificar(cfg, "0.7.7", HOJE, pedir=lambda url, corpo, **kw: (enviado.update(corpo), {"ok": True, "validade": "2027-01-31"})[1])
        self.assertEqual(conta.bloqueio(cfg, HOJE), "")
        self.assertEqual(set(enviado), {"codigo", "instalacao", "versao"})  # nada pessoal sai daqui
        self.assertEqual(len(cfg["conta"]["instalacao"]), 16)
        self.assertIn("até 2027-01-31", conta.situacao(cfg)["texto"])

    def test_desativada_bloqueia_com_contato(self):
        cfg = {"conta": {"codigo": CODIGO}}
        conta.verificar(cfg, "0.7.7", HOJE, pedir=resposta({"ok": False, "motivo": "desativado", "mensagem": "Fale com o financeiro."}))
        motivo = conta.bloqueio(cfg, HOJE)
        self.assertIn("desativada", motivo)
        self.assertIn("Fale com o financeiro.", motivo)
        self.assertIn("judicial@solverone.com.br", motivo)

    def test_codigo_desconhecido(self):
        cfg = {"conta": {"codigo": CODIGO}}
        conta.verificar(cfg, "0.7.7", HOJE, pedir=resposta({"ok": False, "motivo": "codigo_desconhecido"}))
        self.assertIn("não existe", conta.bloqueio(cfg, HOJE))

    def test_queda_da_solverone_nao_para_o_escritorio(self):
        cfg = {"conta": {"codigo": CODIGO}}
        conta.verificar(cfg, "0.7.7", HOJE, pedir=resposta({"ok": True}))
        dez_dias = HOJE + dt.timedelta(days=10)
        conta.verificar(cfg, "0.7.7", dez_dias, pedir=sem_internet)
        self.assertEqual(conta.bloqueio(cfg, dez_dias), "")
        tarde = HOJE + dt.timedelta(days=conta.DIAS_SEM_RESPOSTA + 1)
        conta.verificar(cfg, "0.7.7", tarde, pedir=sem_internet)
        self.assertIn("Faz mais de", conta.bloqueio(cfg, tarde))

    def test_nunca_confirmado_e_sem_internet_bloqueia(self):
        cfg = {"conta": {"codigo": CODIGO}}
        conta.verificar(cfg, "0.7.7", HOJE, pedir=sem_internet)
        self.assertIn("Ainda não consegui confirmar", conta.bloqueio(cfg, HOJE))

    def test_resposta_estranha_conta_como_sem_resposta(self):
        cfg = {"conta": {"codigo": CODIGO, "ultima_ok": HOJE.isoformat(), "resposta": "ok"}}
        conta.verificar(cfg, "0.7.7", HOJE, pedir=resposta(["nao", "e", "dict"]))
        self.assertEqual(cfg["conta"]["resposta"], "sem_resposta")
        self.assertEqual(conta.bloqueio(cfg, HOJE), "")


if __name__ == "__main__":
    unittest.main()
