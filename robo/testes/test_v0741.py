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
        def meta(sigla, data, aviso=print, motivos=None):
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
