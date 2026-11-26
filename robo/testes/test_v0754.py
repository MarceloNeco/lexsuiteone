"""0.7.54 (feedback do dono de 26/Nov, com a 0.7.53 em uso no escritório): desempenho da Lista, do Arquivo e da limpeza da
planilha com dezenas de milhares de processos (o "sinal" calculado uma vez por processo; a limpeza monta o Arquivo uma vez só);
o recorte de período feito na tela ("inicios"); "Visto por" sem apagar a hora em que o RADAR leu; inglês contextual.
Dados FICTÍCIOS, sem internet."""

import datetime as dt
import json
import os
import re
import sys
import tempfile
import time
import unittest
from unittest import mock

_ROBO_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROBO_)

from lexsuite import armazenamento, banco as bd, preferencias as pf, radar  # noqa: E402

HOJE = dt.date.today()
N_GRANDE = 50000  # como um escritório com dezenas de milhares de processos guardados
TEXTO = "Intimação FICTÍCIA. Fica a parte intimada da audiência inicial designada para o dia 10 de dezembro. " * 25


def _banco_grande(pasta, n):
    """`n` processos FICTÍCIOS de 120 dias, metade com o sinal já guardado e metade sem (como os lidos antes da 0.7.17)."""
    b = bd.Banco(os.path.join(pasta, "t.db"))
    linhas = []
    for k in range(n):
        d = (HOJE - dt.timedelta(days=k % 120)).isoformat()
        lead = {"processo": f"{k:07d}-11.2026.5.09.0001", "tribunal": "TRT9", "vara": "1ª Vara do Trabalho de Curitiba",
                "empresas": [f"Empresa Ficticia {k % 3000} Ltda"], "data_publicacao": d, "texto_curto": TEXTO, "tipo": "Intimação"}
        if k % 2:
            lead["sinal"] = "audiência inicial"
        linhas.append((lead["processo"], d, "TRT9", lead["vara"], json.dumps(lead, ensure_ascii=False), "novo", "trabalhista", d, "", ""))
    b.con.executemany("INSERT INTO leads (processo, primeira_vez, tribunal, vara, dados, status, frente, data, porte, faixa_valor) "
                      "VALUES (?,?,?,?,?,?,?,?,?,?)", linhas)
    b.con.commit()
    return b


def _cfg(pasta):
    return {"compartilhar": {"pasta": pasta}, "radar": {"tribunais": ["TRT9"], "dias_na_pagina": 15}}


_DISCO_OK = {"nivel": "ok", "livre": 10 ** 12, "total": 10 ** 12, "pct_livre": 90}


class TempoComMuitosProcessos(unittest.TestCase):
    """Dono (26/Nov): limpar a planilha levava mais de um minuto e a Lista travava nos filtros. Limites folgados (o Windows do
    escritório é mais lento que a máquina dos testes); antes da 0.7.54, a limpeza com 50 mil levava ~74 s na medição da Operação."""

    @classmethod
    def setUpClass(cls):
        cls.pasta = tempfile.mkdtemp()
        cls.b = _banco_grande(cls.pasta, N_GRANDE)
        cls.cfg = _cfg(cls.pasta)

    def test_lista_15_e_7_dias(self):
        for dias in (15, 7):
            t = time.time()
            d = radar.montar_radar(self.cfg, self.b, dias=dias, prefs=pf.padrao())
            gasto = time.time() - t
            self.assertTrue(d["itens"], dias)
            self.assertLess(gasto, 6, f"Lista de {dias} dias com {N_GRANDE} processos levou {gasto:.1f} s")

    def test_arquivo(self):
        t = time.time()
        d = radar.montar_radar(self.cfg, self.b, visao="arquivo")
        gasto = time.time() - t
        self.assertEqual(len(d["itens"]), N_GRANDE)
        self.assertLess(gasto, 25, f"Arquivo com {N_GRANDE} processos levou {gasto:.1f} s")

    def test_limpar_a_planilha(self):
        with mock.patch.object(armazenamento, "disco", return_value=_DISCO_OK):
            t = time.time()
            r = armazenamento.limpar(self.cfg, self.b, self.pasta, "0.7.54", aviso=lambda *a: None)
            gasto = time.time() - t
        self.assertTrue(r[0], r)
        self.assertLess(gasto, 40, f"Limpar a planilha com {N_GRANDE} processos levou {gasto:.1f} s")


class SinalUmaVez(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.mkdtemp()
        self.b = _banco_grande(self.pasta, 300)
        self.cfg = _cfg(self.pasta)

    def test_o_sinal_guardado_vale_e_o_calculado_e_feito_uma_vez_por_processo(self):
        orig = radar.sinal_guardado
        with mock.patch.object(radar, "sinal_guardado", side_effect=orig) as m:
            d = radar.montar_radar(self.cfg, self.b, visao="arquivo")
        self.assertEqual(len(d["itens"]), 300)
        self.assertLessEqual(m.call_count, 150, "só os processos sem o sinal guardado; e uma vez cada")
        self.assertTrue(all(i.get("sinal") for i in d["itens"]))

    def test_mesmo_resultado_que_antes(self):
        lead = {"tipo": "Lista de distribuição", "texto_curto": "qualquer"}
        self.assertEqual(radar.sinal_guardado(lead), "lista de distribuição")
        lead = {"tipo": "Intimação", "texto_curto": "Processo distribuído por sorteio"}
        self.assertEqual(radar.sinal_guardado(lead), "lista de distribuição")
        self.assertEqual(radar.sinal_de({"sinal": "audiência inicial"}), "audiência inicial")

    def test_a_marca_interna_nao_vai_para_o_banco(self):
        lead = {"processo": "0000001-11.2026.5.09.0001", "tribunal": "TRT9", "empresas": ["Fictícia Ltda"], "texto_curto": TEXTO,
                "data_publicacao": HOJE.isoformat(), "_sinal_calc": "x"}
        self.b.guardar_lead(lead, HOJE.isoformat())
        dados = self.b.con.execute("SELECT dados FROM leads WHERE processo = ?", (lead["processo"],)).fetchone()[0]
        self.assertNotIn("_sinal_calc", dados)

    def test_limpar_monta_o_arquivo_uma_vez(self):
        orig = radar._montar_radar
        with mock.patch.object(armazenamento, "disco", return_value=_DISCO_OK), \
                mock.patch.object(radar, "_montar_radar", side_effect=orig) as m:
            r = armazenamento.limpar(self.cfg, self.b, self.pasta, "0.7.54", aviso=lambda *a: None)
        self.assertTrue(r[0], r)
        arq = [c for c in m.call_args_list if c.kwargs.get("visao") == "arquivo"]
        self.assertLessEqual(len(arq), 1, "a limpeza reaproveita a mesma lista do Arquivo")


class InicioDoPeriodoNaTela(unittest.TestCase):
    """A tela corta um período menor do maior que já tem (de 15 para 7 dias), com o mesmo início que o programa usaria."""

    def test_inicios_iguais_ao_programa(self):
        pasta = tempfile.mkdtemp()
        b = _banco_grande(pasta, 200)
        d = radar.montar_radar(_cfg(pasta), b, dias=15, prefs=pf.padrao())
        self.assertEqual(set(d["inicios"]), {"1", "3", "7", "15"})
        for k, v in d["inicios"].items():
            self.assertEqual(v, radar.inicio_periodo(dt.datetime.now().date(), int(k)))
        d7 = radar.montar_radar(_cfg(pasta), b, dias=7, prefs=pf.padrao())
        corte = d["inicios"]["7"]
        na_tela = [i for i in d["itens"] if (i.get("diario_em") or i.get("primeira_vez") or "")[:10] >= corte]
        self.assertEqual(sorted(i["processo"] for i in na_tela), sorted(i["processo"] for i in d7["itens"]))


class VistoPor(unittest.TestCase):
    def test_visto_por_nao_apaga_a_hora_em_que_o_radar_leu(self):
        pasta = tempfile.mkdtemp()
        b = bd.Banco(os.path.join(pasta, "t.db"))
        proc, lido = "0000001-11.2026.5.09.0001", "2026-11-20T08:15:00"
        b.guardar_lead({"processo": proc, "tribunal": "TRT9", "empresas": ["Fictícia Ltda"], "data_publicacao": HOJE.isoformat(),
                        "visto_em": lido}, HOJE.isoformat())
        b.mudar_situacao([proc], "visto", por="Ana (fictícia)")
        lead = b.todos_leads(processos=[proc])[0]
        self.assertEqual(lead.get("visto_em"), lido)
        self.assertEqual(lead.get("visto_por"), "Ana (fictícia)")
        self.assertTrue(lead.get("visto_por_em"))


class InglesContextual(unittest.TestCase):
    """Dono (26/Nov): traduzir pelo sentido jurídico brasileiro, não ao pé da letra; "Federal Revenue" não aparece mais."""

    def setUp(self):
        with open(os.path.join(_ROBO_, "radar_modelo.html"), encoding="utf-8") as f:
            self.html = f.read()

    def test_receita_federal(self):
        self.assertIn('fonte_receita: "Tax registry"', self.html)
        historico = "the name written the same as at the Federal Revenue.\","  # Novidades de versões antigas: registro, não se reescreve
        self.assertNotIn("Federal Revenue", self.html.replace(historico, ""))
        self.assertGreaterEqual(self.html.count("federal tax registry (Receita Federal)"), 10)
        self.assertIn("revenue up to R$ 360k/year", self.html)  # o porte (faturamento) fica como está

    def test_ordenar_mais_antigos(self):
        self.assertIn('ord_ajuizado_asc: "Mais antigos primeiro (ajuizados)"', self.html)
        self.assertIn('ord_ajuizado_asc: "Oldest first (filed)"', self.html)
        self.assertTrue(re.search(r'\["ajuizado", t\("ord_ajuizado"\)\], \["ajuizado_asc"', self.html), "logo abaixo de Mais novos")
        # revisão: "sem data de ajuizamento" é o mesmo que na planilha (só CNJ, Diário ou digitado contam); vão para o fim
        self.assertIn('if (o === "ajuizado_asc") return function (a, b) { var x_ = ajuizadoReal(a), y_ = ajuizadoReal(b); if (!x_ !== !y_) return x_ ? -1 : 1;', self.html)
        self.assertIn('["cnj", "diario", "digitado"].indexOf(i.ajuizado_fonte) >= 0', self.html)
        with open(os.path.join(_ROBO_, "lexsuite", "radar.py"), encoding="utf-8") as f:
            self.assertIn('item.get("ajuizado_fonte") in ("cnj", "diario", "digitado")', f.read())


if __name__ == "__main__":
    unittest.main()
