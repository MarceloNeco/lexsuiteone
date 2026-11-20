"""0.7.51 (dono, 16 e 20/Nov): ressalvas da Operação (exclusão pelo CNPJ, CNPJ provável pelo nome exato, pré-filtro com acento),
Novidades até "Não mostrar novamente", período de cada leitura (faixa da mira e Rotina de leitura), primeira leitura na Lista e os
itens do feedback do teste da 0.7.50 que viraram tela. Dados FICTÍCIOS, sem internet."""

import datetime as dt
import json
import os
import sys
import tempfile
import unittest

_ROBO_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RAIZ_ = os.path.dirname(_ROBO_)
sys.path.insert(0, _ROBO_)

from lexsuite import banco as bd, preferencias, radar  # noqa: E402

with open(os.path.join(_ROBO_, "radar_modelo.html"), encoding="utf-8") as _f:
    HTML = _f.read()

HOJE = dt.date(2026, 11, 20)  # sexta-feira


def lead(b, proc, dia, nome, cnpj=""):
    emp = {"cnpj": cnpj, "razao_social": nome} if cnpj else {}
    b.guardar_lead({"processo": proc, "tribunal": "TRT2", "vara": "1ª Vara (fictícia)", "empresas": [nome], "data_publicacao": dia,
                    "cnpjs": [cnpj] if cnpj else [], "empresa_receita": emp}, dia)


class ExclusaoPeloCnpj(unittest.TestCase):
    """Ressalva 1 da Operação (dono: "a chave é o CNPJ"): exclusão gravada com CNPJ não tira homônimo de OUTRO CNPJ."""

    def item(self, nome, cnpj=""):
        return {"empresas": [nome], "empresa": {"cnpj": cnpj, "razao_social": nome} if cnpj else {}}

    def test_homonimo_de_outro_cnpj_fica(self):
        prefs = {"exclusoes": [{"nome": "Empresa Ficticia Alfa Ltda", "cnpj": "11222333000181", "motivo": "Excluída pelo agrupamento por empresa"}]}
        itens = [self.item("EMPRESA FICTICIA ALFA LTDA", "11222333000181"), self.item("Empresa Ficticia Alfa Ltda", "99888777000166"),
                 self.item("Empresa Fictícia Alfa Ltda")]
        preferencias.aplicar(itens, prefs)
        self.assertTrue(itens[0]["excluida"])          # o mesmo CNPJ sai
        self.assertEqual(itens[1]["excluida"], "")     # outro CNPJ, mesmo nome: é outra empresa
        self.assertTrue(itens[2]["excluida"])          # sem CNPJ, mesmo nome: não dá para saber; continua fora, como antes

    def test_exclusao_so_pelo_nome_continua_igual(self):
        prefs = {"exclusoes": [{"nome": "Empresa Ficticia Beta S.A.", "cnpj": None, "motivo": ""}]}
        itens = [self.item("EMPRESA FICTICIA BETA S.A.", "11222333000181"), self.item("Empresa Ficticia Beta Ltda", "99888777000166")]
        preferencias.aplicar(itens, prefs)
        self.assertTrue(itens[0]["excluida"])
        self.assertEqual(itens[1]["excluida"], "")  # "S.A." não exclui "Ltda" (0.7.41)


class CnpjProvavelNomeExato(unittest.TestCase):
    """Ressalvas 2 e 5: "X Ltda" e "X S.A." não se juntam; o pré-filtro acha o nome gravado com ou sem acento."""

    def setUp(self):
        self.b = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db"))
        self.addCleanup(self.b.con.close)

    def test_ltda_e_sa_nao_se_juntam(self):
        lead(self.b, "0001001-11.2026.5.02.0001", "2026-11-18", "Comercio Ficticio Gama Ltda", "11222333000181")
        lead(self.b, "0001002-11.2026.5.02.0001", "2026-11-18", "Comercio Ficticio Gama S.A.")
        self.assertEqual(radar.cnpj_provavel(self.b, "Comercio Ficticio Gama S.A."), {})
        self.assertEqual(radar.usar_cnpj(self.b, "Comercio Ficticio Gama S.A.", "11222333000181"), 1)  # grava só no nome exato
        d = json.loads(self.b.con.execute("SELECT dados FROM leads WHERE processo = ?", ("0001002-11.2026.5.02.0001",)).fetchone()[0])
        self.assertEqual(d.get("cnpj_inferido"), "11222333000181")

    def test_acento_gravado_de_qualquer_jeito(self):
        lead(self.b, "0002001-11.2026.5.02.0001", "2026-11-18", "Distribuição Fictícia Ômega Ltda", "11222333000181")
        lead(self.b, "0002002-11.2026.5.02.0001", "2026-11-18", "DISTRIBUICAO FICTICIA OMEGA LTDA")
        s = radar.cnpj_provavel(self.b, "Distribuicao Ficticia Omega Ltda")
        self.assertEqual(s.get("cnpj"), "11222333000181")


class PeriodoDaLeitura(unittest.TestCase):
    """Itens 22 e 26: "Desde a última leitura", "Últimos 7 dias" e "Do último dia útil até hoje"."""

    def setUp(self):
        self.b = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db"))
        self.addCleanup(self.b.con.close)

    def leitura(self, quando, resultado="ok"):
        self.b.con.execute("INSERT INTO execucoes (quando, tipo, resumo) VALUES (?, 'radar', ?)", (quando, json.dumps({"resultado": resultado, "lidas": 3})))
        self.b.con.commit()

    def test_ultimo_dia_util_e_7_dias(self):
        self.assertEqual(radar.dias_do_periodo("ultimo_util", self.b, HOJE), 1)
        self.assertEqual(radar.dias_do_periodo("7dias", self.b, HOJE), 5)  # 13 a 19/11: 5 dias úteis

    def test_desde_a_ultima_leitura_recupera_dias_desligados(self):
        self.assertEqual(radar.dias_do_periodo("desde_ultima", self.b, HOJE), 1)  # nunca leu: só o último dia útil
        self.leitura("2026-11-16T20:00:00")  # segunda; o computador ficou desligado até sexta
        self.assertEqual(radar.dias_do_periodo("desde_ultima", self.b, HOJE), 4)  # 16, 17, 18 e 19/11
        self.leitura("2026-11-19T20:00:00")
        self.assertEqual(radar.dias_do_periodo("desde_ultima", self.b, HOJE), 1)
        self.leitura("2026-10-01T20:00:00")  # leitura mais antiga não muda a última
        self.assertEqual(radar.dias_do_periodo("desde_ultima", self.b, HOJE), 1)

    def test_limite_de_10_dias_uteis(self):
        self.leitura("2026-09-01T20:00:00")
        self.assertEqual(radar.dias_do_periodo("desde_ultima", self.b, HOJE), 10)

    def test_primeira_leitura(self):
        self.assertEqual(radar.primeira_leitura(self.b), "")
        self.leitura("2026-11-09T08:00:00"); self.leitura("2026-11-19T08:00:00")
        self.assertEqual(radar.primeira_leitura(self.b), "2026-11-09")

    def test_config_aceita_so_os_tres_periodos(self):
        self.assertEqual(radar.PERIODOS, ("desde_ultima", "7dias", "ultimo_util"))
        with open(os.path.join(_ROBO_, "lexsuite", "app.py"), encoding="utf-8") as f:
            a = f.read()
        self.assertIn('for chave_ in ("periodo_botao", "periodo_rotina"):', a)
        self.assertIn("if corpo.get(chave_) in radar.PERIODOS:", a)


class Tela0751(unittest.TestCase):
    def test_novidades_ate_nao_mostrar(self):
        self.assertIn('nov_nao_mostrar: "Não mostrar novamente"', HTML)
        self.assertIn('nov_nao_mostrar: "Don\\u2019t show again"', HTML)
        self.assertIn('if (!sempre && (!n_ || ls_("novidades-ocultas") === v_)) return;', HTML)
        self.assertNotIn("Inclusão da caixinha", HTML)       # ressalva 3: sem coloquial
        self.assertNotIn("Grouping range now applies", HTML)

    def test_periodo_na_faixa_e_na_rotina(self):
        for k in ('id="p-per"', 'id="c-per"', 'per_desde: "Desde a última leitura"', 'per_7: "Últimos 7 dias"',
                  'per_util: "Do último dia útil até hoje"', 'per_desde: "Since the last reading"', "function avisoLonga(seguir)",
                  'nao_salvo_t: "Você não salvou as mudanças"', "periodo_botao: perLeitura", "corpo.periodo_rotina = $(\"c-per\").value;"):
            self.assertIn(k, HTML, k)

    def test_itens_do_feedback(self):
        for k in ('etq-fora', 'agr_cnpj_nao: "CNPJ não capturado"', '"ge-busc"', 'class="gira-fino"', "function varaBonita(v)",
                  "function procFmt(p)", "function comCopiar(texto, valor)", "function telFmt(x)", 'reg_gmail: "Abrir no Gmail"',
                  'reg_windows: "Abrir no e-mail do Windows"', 'c_voltar: "← Voltar às Configurações"', "dgo-aone-topicos",
                  'id="lista-carregando"', "montarFicha = function ()", 'lidos_desde: "Processos lidos a partir de {d}'):
            self.assertIn(k, HTML, k)
        self.assertNotIn('t("copiar")); bc.type = "button";', HTML)  # item 12: sem "Copiar número" na ficha
        self.assertIn('avisoRapidoApp(t("ultimo_mes_off", { d: d }), "erro");', HTML)  # item 14: em vermelho

    def test_troca_de_periodo_durante_a_carga_vale(self):  # item 16
        self.assertIn("++seqCarga; if (carregandoPer) { carregandoPer = 0; ocupadoDesligar(); }", HTML)
        self.assertIn("if (pedido_ && d.app && d.app.config) d.app.config.dias_na_pagina = pedido_;", HTML)

    def test_vara_bonita_regra(self):
        import re
        m = re.search(r"function varaBonita\(v\) \{.*?\n  \}", HTML, re.S)
        self.assertIsNotNone(m)
        self.assertIn('/^(de|da|do|das|dos|e|del)$/', m.group(0))


if __name__ == "__main__":
    unittest.main()
