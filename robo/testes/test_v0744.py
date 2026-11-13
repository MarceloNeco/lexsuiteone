"""0.7.44 (dono, 13/Nov): conferência automática do CNJ com a tela aberta, aviso quando volta e faixa vermelha que diz
até que dia já foi lido."""

import datetime as dt
import os
import sys
import tempfile
import unittest
from unittest import mock

_ROBO_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROBO_)

from lexsuite import app, banco as bd, rede  # noqa: E402

with open(os.path.join(_ROBO_, "radar_modelo.html"), encoding="utf-8") as _f:
    HTML = _f.read()


class EstadoFalso:
    def __init__(self, erro_info=None, rodando=False):
        self.erro_info, self.rodando = erro_info, rodando


class ServidorFalso:
    def __init__(self, caminho_db, tribs=("TRT2", "TRT9"), erro_info=None):
        self.caminho_db, self.tribs = caminho_db, list(tribs)
        self.arquivo_andamento = os.path.join(os.path.dirname(caminho_db), "saida", "leitura.json")
        self.estado, self.cnj, self.leituras = EstadoFalso(erro_info), None, 0

    def config(self):
        return {"radar": {"tribunais": self.tribs}}

    def rodar(self, dias=None):
        self.leituras += 1
        return True


def meta_que(erro=None, chamadas=None):
    def meta(sigla, data, aviso=print, motivos=None, tentativas=5):
        if chamadas is not None:
            chamadas.append((sigla, data, tentativas))
        if erro:
            raise erro
        return {"versao": "1"}
    return meta


class ConferenciaCNJ(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.db = os.path.join(self.tmp, "lexsuite.db")
        b = bd.Banco(self.db)
        b.con.close()
        self.hoje = dt.date(2026, 11, 13)  # sexta-feira

    def pendente(self, trib, dia):
        b = bd.Banco(self.db)
        try:
            b.marcar_caderno_pendente(trib, dia)
        finally:
            b.con.close()

    def test_sem_motivo_nao_pede_nada(self):
        s, ch = ServidorFalso(self.db), []
        self.assertIsNone(app.conferir_cnj(s, meta=meta_que(chamadas=ch), hoje=self.hoje))
        self.assertEqual(ch, [])

    def test_pendente_mais_antigo_um_pedido_com_uma_tentativa(self):
        self.pendente("TRT9", "2026-11-11")
        self.pendente("TRT2", "2026-11-10")
        s, ch = ServidorFalso(self.db), []
        app.conferir_cnj(s, meta=meta_que(rede.ErroHTTP(500, "https://x/caderno", "Server Error"), ch), hoje=self.hoje)
        self.assertEqual(ch, [("TRT2", "2026-11-10", 1)])
        self.assertEqual(s.cnj["situacao"], "fora")
        self.assertEqual(s.leituras, 0)  # fora: não lê

    def test_sem_pendente_mas_ultima_leitura_com_cnj_fora(self):
        s, ch = ServidorFalso(self.db, erro_info={"causa": "governo_fora"}), []
        app.conferir_cnj(s, meta=meta_que(rede.SemResposta("https://x", "tempo esgotado"), ch), hoje=self.hoje)
        self.assertEqual(ch, [("TRT2", "2026-11-12", 1)])  # o último dia útil antes de hoje
        self.assertEqual(s.cnj["situacao"], "fora")

    def test_404_e_429(self):
        self.pendente("TRT2", "2026-11-10")
        s = ServidorFalso(self.db)
        app.conferir_cnj(s, meta=meta_que(rede.ErroHTTP(429, "https://x", "")), hoje=self.hoje)
        self.assertEqual(s.cnj["situacao"], "fora")  # muitos pedidos: ainda não está bom
        app.conferir_cnj(s, meta=meta_que(rede.ErroHTTP(404, "https://x", "")), hoje=self.hoje)
        self.assertEqual(s.cnj["situacao"], "voltou")  # respondeu

    def test_volta_com_automatica_ligada_le(self):
        self.pendente("TRT2", "2026-11-10")
        s = ServidorFalso(self.db)
        app.conferir_cnj(s, meta=meta_que(rede.ErroHTTP(503, "https://x", "")), hoje=self.hoje)
        with mock.patch.object(app.agendar, "disponivel", return_value=True), mock.patch.object(app.agendar, "agendado", return_value=True):
            app.conferir_cnj(s, meta=meta_que(), hoje=self.hoje)
        self.assertEqual(s.cnj["situacao"], "voltou")
        self.assertTrue(s.cnj["lendo"])
        self.assertEqual(s.leituras, 1)
        with mock.patch.object(app.agendar, "disponivel", return_value=True), mock.patch.object(app.agendar, "agendado", return_value=True):
            app.conferir_cnj(s, meta=meta_que(), hoje=self.hoje)
        self.assertEqual(s.leituras, 1)  # só na volta (de fora para respondendo), não a cada conferência

    def test_volta_com_outra_leitura_tenta_de_novo(self):
        self.pendente("TRT2", "2026-11-10")
        s = ServidorFalso(self.db)
        app.conferir_cnj(s, meta=meta_que(rede.ErroHTTP(500, "https://x", "")), hoje=self.hoje)
        s.estado.rodando = True  # outra leitura rodando na hora da volta
        with mock.patch.object(app.agendar, "disponivel", return_value=True), mock.patch.object(app.agendar, "agendado", return_value=True):
            app.conferir_cnj(s, meta=meta_que(), hoje=self.hoje)
            self.assertEqual(s.leituras, 0)
            self.assertTrue(s.cnj["ler_pendente"])
            s.estado.rodando = False
            app.conferir_cnj(s, meta=meta_que(), hoje=self.hoje)
        self.assertEqual(s.leituras, 1)
        self.assertTrue(s.cnj["lendo"])

    def test_volta_sem_automatica_so_avisa(self):
        self.pendente("TRT2", "2026-11-10")
        s = ServidorFalso(self.db)
        app.conferir_cnj(s, meta=meta_que(rede.ErroHTTP(500, "https://x", "")), hoje=self.hoje)
        with mock.patch.object(app.agendar, "disponivel", return_value=True), mock.patch.object(app.agendar, "agendado", return_value=False):
            app.conferir_cnj(s, meta=meta_que(), hoje=self.hoje)
        self.assertEqual(s.cnj["situacao"], "voltou")
        self.assertFalse(s.cnj["lendo"])
        self.assertEqual(s.leituras, 0)

    def test_leitura_trouxe_o_que_faltava_some_o_aviso(self):
        self.pendente("TRT2", "2026-11-10")
        s = ServidorFalso(self.db)
        app.conferir_cnj(s, meta=meta_que(rede.ErroHTTP(500, "https://x", "")), hoje=self.hoje)
        b = bd.Banco(self.db)
        b.tirar_caderno_pendente("TRT2", "2026-11-10")
        b.con.close()
        self.assertIsNone(app.conferir_cnj(s, meta=meta_que(), hoje=self.hoje))

    def test_vigia_nao_derruba(self):
        s = ServidorFalso(self.db)
        s.config = mock.Mock(side_effect=RuntimeError("config quebrado"))
        app.vigiar_cnj(s, dormir=lambda _s: None, vezes=2)  # não levanta


class Tela0744(unittest.TestCase):
    def test_versao_e_novidades(self):
        import re
        from lexsuite import VERSAO
        self.assertGreaterEqual(tuple(int(x) for x in VERSAO.split(".")), (0, 7, 44))  # a versão sobe
        bloco = HTML[HTML.index('"0.7.44": {'):HTML.index('"0.7.43": {')]
        pt = re.findall(r'"((?:[^"\\]|\\.)+)"', bloco[bloco.index("pt: ["):bloco.index("en: [")])
        en = re.findall(r'"((?:[^"\\]|\\.)+)"', bloco[bloco.index("en: ["):])
        self.assertEqual(len(pt), 4); self.assertEqual(len(en), 4)

    def test_textos_pt_en(self):
        for k in ("falha_ok_ate:", "cnj_fora:", "cnj_voltou:", "cnj_voltou_lendo:"):
            self.assertEqual(HTML.count(k), 2, k)

    def test_batimento_le_a_conferencia(self):
        self.assertIn("if (e) avaliarCnj(e.cnj);", HTML)
        self.assertIn("if (c.lendo) vigiar();", HTML)

    def test_estado_leva_o_cnj(self):
        with open(os.path.join(_ROBO_, "lexsuite", "app.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn('d["cnj"] = dict(self.cnj)', src)
        self.assertIn('name="vigiar-cnj"', src)


if __name__ == "__main__":
    unittest.main()
