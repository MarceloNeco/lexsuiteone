"""0.7.40 (teste do dono na 0.7.39): dados fictícios, sem internet."""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
import zipfile

_ROBO_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RAIZ_ = os.path.dirname(_ROBO_)
sys.path.insert(0, _ROBO_)

from lexsuite import app, classificar, saidas  # noqa: E402
from lexsuite import banco as bd  # noqa: E402

with open(os.path.join(_ROBO_, "radar_modelo.html"), encoding="utf-8") as _f:
    HTML = _f.read()


class Robo0740(unittest.TestCase):
    def test_nome_sem_aspas_soltas(self):
        self.assertEqual(classificar.limpar_nome('" Escola Crista Modelo Alpha Ltda - Me'), "Escola Crista Modelo Alpha Ltda - Me")
        self.assertEqual(classificar.limpar_nome('"alves & Batista Alarmes Ltda'), "alves & Batista Alarmes Ltda")
        self.assertEqual(classificar.limpar_nome("Empresa X S.A."), "Empresa X S.A.")
        self.assertEqual(classificar.limpar_nome("“Banco Y S/A”"), "Banco Y S/A")

    def test_totais_por_dia(self):
        d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, d, True)
        b = bd.Banco(os.path.join(d, "x.db"))
        import datetime as dt
        hoje = dt.date.today().isoformat(); velho = (dt.date.today() - dt.timedelta(days=200)).isoformat()
        b.con.executemany("INSERT INTO estatisticas_diarias VALUES (?,?,?,?,?,?,?,0,'')",
                          [(hoje, "TRT2", "v1", "", "", "", 3), (hoje, "TRT2", "v2", "", "", "", 2), (hoje, "TRT15", "v1", "", "", "", 4), (velho, "TRT2", "v", "", "", "", 9)])
        b.con.commit()
        t = app.totais_por_dia(b, 90)
        self.assertEqual(t, {hoje: {"TRT2": 5, "TRT15": 4}})

    def test_retrato_sem_imagens_de_fundo(self):
        d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, d, True)
        destino = os.path.join(d, "retrato.html")
        saidas._embutir(saidas.MODELO_RADAR, "LEXSUITE_RADAR", destino, {"itens": []})
        with open(destino, encoding="utf-8") as f:
            r = f.read()
        self.assertIn("window.LEX_FUNDOS = [];", r)
        self.assertEqual(r.count("data:image/webp;base64"), HTML.count("data:image/webp;base64") - 4)  # só os 4 fundos saem


class Tela0740(unittest.TestCase):
    def test_ultimo_mes(self):
        self.assertIn('role="switch" id="b-ultimo-mes"', HTML)
        self.assertIn('return localStorage.getItem("lexsuite:ultimo-mes") !== "0";', HTML)  # ligado por padrão
        self.assertIn('"?max=" + ULTIMO_MES', HTML)
        self.assertIn("if (ultimoMes && d > ULTIMO_MES) { ultimoMes = false;", HTML)
        self.assertIn("if (tot90) return grafDiasTotais(tot90);", HTML)

    def test_fundos(self):
        m = re.search(r"window\.LEX_FUNDOS = \[/\*FUNDOS\*/(.*?)/\*/FUNDOS\*/\];", HTML, re.S)
        self.assertIsNotNone(m); self.assertEqual(m.group(1).count("data:image/webp;base64,"), 4)
        self.assertIn("if (window.lexSortearFundo) window.lexSortearFundo();", HTML)
        self.assertIn("rgba(15,29,51,.72)", HTML)

    def test_riscar_redesenha_so_o_cartao(self):
        self.assertIn("redesenharCartao(g, tit, linhas, opc, kf);", HTML)
        self.assertIn('ocp.hidden = false; document.body.classList.add("ocupado");', HTML)

    def test_empresas_e_tipo_de_publicacao(self):
        self.assertIn('var MULTI = ["sit", "frente", "trib", "data", "vara", "setor", "porte", "uf", "sinal", "empresa"];', HTML)
        self.assertIn('if (ocultos["__outros__"] && !opc.topN) lim += 6;', HTML)
        self.assertIn('return filtrarPor("empresa", vis_.map(function (l) { return l.ek; }));', HTML)
        self.assertIn('{ campo: "sinal", max: 8 }', HTML)
        self.assertIn('g_sinal: "Tipo de publicação"', HTML); self.assertIn('g_sinal: "Notice type"', HTML)

    def test_busca_e_textos(self):
        self.assertIn('el("mark", "achou", nm_)', HTML)
        self.assertIn("return pr.concat(ou);", HTML)
        self.assertIn('.balao { position: absolute; z-index: 90; max-width: min(760px, 92vw);', HTML)
        self.assertIn('g_dica_pilha: "{r}: {n}\\n{p}"', HTML)
        self.assertIn('mira_trib: "Escolha os tribunais. Valor mínimo e empresas excluídas: [[regras]]; leitura automática: [[agenda]] (em [[config]]).",', HTML)

    def test_sintaxe_da_pagina(self):
        if not shutil.which("node"):
            self.skipTest("sem node")
        for i, bloco in enumerate(re.findall(r"<script>(.*?)</script>", HTML, re.S)):
            if "AssistONE.configurar({ app: 'meu-app'" in bloco and len(bloco) < 60000:
                continue  # exemplo de uso dentro de um comentário
            d = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, d, True)
            f = os.path.join(d, "b.js")
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(bloco)
            r = subprocess.run(["node", "--check", f], capture_output=True, text=True, timeout=60)
            self.assertEqual(r.returncode, 0, f"bloco {i}: {r.stderr[:300]}")

    def test_versao_e_novidades(self):
        from lexsuite import VERSAO
        self.assertGreaterEqual(tuple(int(x) for x in VERSAO.split(".")), (0, 7, 40))  # 0.7.41: a versão sobe
        bloco = HTML[HTML.index('"0.7.40": {'):HTML.index('"0.7.39": {')]
        pt = re.findall(r'"((?:[^"\\]|\\.)+)"', bloco[bloco.index("pt: ["):bloco.index("en: [")])
        en = re.findall(r'"((?:[^"\\]|\\.)+)"', bloco[bloco.index("en: ["):])
        self.assertEqual(len(pt), len(en)); self.assertEqual(len(pt), 10)


class PacoteCompleto(unittest.TestCase):
    def test_pacote_completo(self):
        z = zipfile.ZipFile(os.path.join(_RAIZ_, "docs", "downloads", "Instalar-LexSuiteONE-completo.zip"))
        nomes = sorted(z.namelist())
        self.assertEqual(nomes, ["INSTALAR.bat", "LEIA-ME.txt", "dados/instalar.txt", "dados/pacote.zip", "dados/python.zip", "dados/radar.ico"])
        import hashlib
        campos = dict(l.split("=", 1) for l in z.read("dados/instalar.txt").decode().splitlines() if "=" in l)
        self.assertEqual(hashlib.sha256(z.read("dados/pacote.zip")).hexdigest(), campos["sha256"].strip())
        bat = z.read("INSTALAR.bat").decode()
        self.assertIn("\r\n", bat); self.assertIn('goto extrair_antes', bat)
        self.assertNotIn('"%SITE%/atualizacao/', bat)  # não baixa o programa
        self.assertNotIn("INSTALAR-PYTHON.bat", bat)  # nem o Python


if __name__ == "__main__":
    unittest.main()
