"""0.7.41 (instalação na KR Law, 13/Nov): o CNJ respondeu 500 para o caderno do dia de hoje e a leitura inteira parou.
O dia de hoje com erro 5xx conta como "ainda não publicado"; os dias anteriores são lidos. Erro 5xx em dia anterior
continua sendo falha do tribunal."""
import datetime as dt
import unittest
from unittest import mock

from lexsuite import monitor, rede


class BancoFalso:
    def versao_caderno(self, sigla, data):
        return None


class CadernoDeHojeCom500(unittest.TestCase):
    def setUp(self):
        self.hoje = dt.date(2026, 11, 13)  # sexta-feira
        self.ontem = dt.date(2026, 11, 12)

    def _meta(self, falha_em):
        def meta(sigla, data, aviso=print, motivos=None, **_kw):
            if data == falha_em:
                raise rede.ErroHTTP(500, "https://comunicaapi.pje.jus.br/api/v1/caderno/TRT9/" + data + "/D", '{"message": "Server Error"}')
            return {"versao": "1", "url": "x"} if data == self.ontem.isoformat() else None
        return meta

    def test_hoje_com_500_pula_e_le_ontem(self):
        tent = []
        with mock.patch.object(monitor.djen, "meta_caderno", side_effect=self._meta(self.hoje.isoformat())), \
             mock.patch.object(monitor.djen, "baixar_caderno", return_value=[{"id": 1}]):
            pubs = monitor.coletar_caderno(["TRT9"], 1, BancoFalso(), aviso=lambda *_: None, hoje=self.hoje, tentativas=tent)
        self.assertEqual(pubs, [{"id": 1}])
        self.assertEqual(tent[-1]["causa"], "ok")
        self.assertEqual(tent[-1]["leu_ate"], self.ontem.isoformat())

    def test_500_em_dia_anterior_continua_falha(self):
        tent = []
        with mock.patch.object(monitor.djen, "meta_caderno", side_effect=self._meta(self.ontem.isoformat())), \
             mock.patch.object(monitor.djen, "baixar_caderno", return_value=[]):
            with self.assertRaises(Exception):
                monitor.coletar_caderno(["TRT9"], 1, BancoFalso(), aviso=lambda *_: None, hoje=self.hoje, tentativas=tent)
        self.assertEqual(tent[-1]["causa"], "governo_fora")


if __name__ == "__main__":
    unittest.main()


class DiasComErroDoCNJ(unittest.TestCase):
    """0.7.42 (dono, 13/Nov): Diário com erro 5xx não interrompe a leitura; a leitura volta mais dias e o dia fica pendente,
    lido sozinho nas próximas leituras. Três Diários seguidos com erro: o CNJ está fora, não insiste."""
    def setUp(self):
        import tempfile, os
        from lexsuite import banco as bd
        self.dir = tempfile.mkdtemp()
        self.banco = bd.Banco(os.path.join(self.dir, "t.db"))
        self.hoje = dt.date(2026, 11, 13)

    def _rodar(self, ruins, bons, dias=1, hoje=None):
        pedidos = []
        def meta(sigla, data, aviso=print, motivos=None, tentativas=5):
            pedidos.append((data, tentativas))
            if data in ruins:
                raise rede.ErroHTTP(500, "https://comunicaapi.pje.jus.br/api/v1/caderno/" + sigla + "/" + data + "/D", '{"message": "Server Error"}')
            return {"versao": "1", "url": "x"} if data in bons else None
        tent = []
        with mock.patch.object(monitor.djen, "meta_caderno", side_effect=meta), \
             mock.patch.object(monitor.djen, "baixar_caderno", side_effect=lambda s, d, *a, **k: [{"id": d}]):
            pubs = monitor.coletar_caderno(["TRT9"], dias, self.banco, aviso=lambda *_: None, hoje=hoje or self.hoje, tentativas=tent)
        return pubs, tent, pedidos

    def test_pula_dia_com_erro_le_o_anterior_e_anota_pendente(self):
        pubs, tent, pedidos = self._rodar({"2026-11-13", "2026-11-12"}, {"2026-11-11"})
        self.assertEqual([p["id"] for p in pubs], ["2026-11-11"])
        self.assertEqual(tent[-1]["causa"], "ok")
        self.assertIn("12/NOV", tent[-1]["fez"])
        self.assertEqual(self.banco.cadernos_pendentes("TRT9"), {"2026-11-12"})
        self.assertEqual(pedidos[0][1], 5)
        self.assertTrue(all(t == 2 for _, t in pedidos[1:]))  # depois do primeiro erro, menos tentativas

    def test_pendente_e_lido_quando_o_cnj_volta(self):
        self._rodar({"2026-11-13", "2026-11-12"}, {"2026-11-11"})
        pubs, tent, _ = self._rodar(set(), {"2026-11-16", "2026-11-13", "2026-11-12", "2026-11-11"}, hoje=dt.date(2026, 11, 16))
        ids = [p["id"] for p in pubs]
        self.assertIn("2026-11-13", ids)
        self.assertIn("2026-11-12", ids)  # o pendente entra mesmo além do período de 1 dia
        self.assertNotIn("2026-11-10", ids)
        self.assertEqual(self.banco.cadernos_pendentes("TRT9"), set())

    def test_tres_seguidos_com_erro_para_e_falha(self):
        with self.assertRaises(rede.ErroHTTP):
            self._rodar({"2026-11-13", "2026-11-12", "2026-11-11", "2026-11-10", "2026-11-09"}, set())
        self.assertEqual(self.banco.cadernos_pendentes("TRT9"), {"2026-11-12", "2026-11-11"})
