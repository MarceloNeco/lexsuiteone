"""0.7.39 (teste do dono na 0.7.38): só leitura do código da tela e um caso em node para a data de Brasília."""

import os
import re
import shutil
import subprocess
import unittest

_ROBO_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(_ROBO_, "radar_modelo.html"), encoding="utf-8") as _f:
    HTML = _f.read()


class Tela0739(unittest.TestCase):
    def test_tracejado_no_periodo_em_andamento(self):
        self.assertIn(".col.em-andamento .pe { outline: 2px dashed var(--latao);", HTML)
        self.assertIn('if (d.k === (porMes ? hojeBR().slice(0, 7) : hojeBR())) { marcarAndamento(col, rot, porMes); andamento_ = true; }', HTML)
        self.assertIn("if (m.mes === hojeBR().slice(0, 7)) { marcarAndamento(col, rot, true); andS_ = true; }", HTML)
        for k in ("g_andamento_dia", "g_andamento_mes", "g_andamento_dia_d", "g_andamento_mes_d"):
            self.assertEqual(HTML.count(k + ":"), 2, k)

    def test_hoje_pela_data_de_brasilia(self):
        if not shutil.which("node"):
            self.skipTest("sem node")
        corpo = re.search(r"  function hojeBR\(\) \{\n(.*?)\n  \}\n", HTML, re.S).group(1)
        js = "function hojeBR() {\n" + corpo + "\n}\nconsole.log(hojeBR());"
        r = subprocess.run(["node", "-e", js], capture_output=True, text=True, timeout=30, env=dict(os.environ, TZ="UTC"))
        self.assertRegex(r.stdout.strip(), r"^\d{4}-\d{2}-\d{2}$")
        js2 = js.replace("new Date()", "new Date('2026-11-14T02:30:00Z')")  # 23h30 de 13/11 em Brasília
        r2 = subprocess.run(["node", "-e", js2], capture_output=True, text=True, timeout=30, env=dict(os.environ, TZ="UTC"))
        self.assertEqual(r2.stdout.strip(), "2026-11-13")

    def test_titulo_estatisticas_com_ajuda(self):
        self.assertIn('hE = el("h3", null, t("g_estat"))', HTML)
        self.assertEqual(HTML.count("g_estat_ajuda:"), 2)
        self.assertIn('g_estat: "Estatísticas"', HTML); self.assertIn('g_estat: "Statistics"', HTML)

    def test_limpar_filtros_conta_e_desfaz_as_pizzas(self):
        self.assertIn("var nf = filtrosLigados() + riscosPizza(), b = $(\"b-limpar-filtros\");", HTML)
        self.assertIn('if (visao === "painel") Object.keys(pizzaOculta).forEach(function (k) { pizzaOculta[k] = {}; });', HTML)

    def test_ver_na_lista_e_primeiras(self):
        self.assertIn("verLista: verFaixas", HTML)
        self.assertIn('return filtrarPor("empresa", vis_.map(function (l) { return l.ek; }));', HTML)  # 0.7.40: todas as mostradas
        self.assertIn('localStorage.setItem("lexsuite:emp-top", String(n_))', HTML)
        self.assertIn("var lim = opc.topN ? opc.topN : Math.min(opc.max || 8, 6)", HTML)

    def test_excluidas(self):
        self.assertIn('rg_exc_tirar: "Remover"', HTML)
        self.assertIn("#config fieldset { min-width: 0; grid-template-columns: minmax(0, 1fr); }", HTML)
        self.assertIn("function medirMotivos()", HTML)
        self.assertIn('var lapis = el("button", "rg-exc-lapis", "✎");', HTML)

    def test_faixa_da_leitura_numa_linha(self):
        self.assertIn('grid-template-areas: "cab txt txt" ". est bot";', HTML)  # 0.7.40: a 1ª linha usa a largura toda

    def test_versao_e_novidades(self):
        import sys
        sys.path.insert(0, _ROBO_)
        from lexsuite import VERSAO
        self.assertGreaterEqual(tuple(int(x) for x in VERSAO.split(".")), (0, 7, 39))
        bloco = HTML[HTML.index('"0.7.39": {'):HTML.index('"0.7.38": {')]
        pt = re.findall(r'"((?:[^"\\]|\\.)+)"', bloco[bloco.index("pt: ["):bloco.index("en: [")])
        en = re.findall(r'"((?:[^"\\]|\\.)+)"', bloco[bloco.index("en: ["):])
        self.assertEqual(len(pt), len(en)); self.assertEqual(len(pt), 9)


if __name__ == "__main__":
    unittest.main()
