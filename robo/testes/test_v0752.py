"""0.7.52 (dono, 24/Nov): inglês sem sobras de português (faixas, mensagens da leitura, setor, porte, tipos de publicação),
"Court Journal" no lugar de "gazette", "Manual de uso / User guide", termos em inglês com seletor (texto em português inalterado),
limpeza da planilha com andamento e resultado, rodapé enxuto e as ressalvas 1 a 4 da Operação sobre a 0.7.51. Dados FICTÍCIOS,
sem internet."""

import datetime as dt
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

_ROBO_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RAIZ_ = os.path.dirname(_ROBO_)
sys.path.insert(0, _ROBO_)

from lexsuite import armazenamento, banco as bd, classificar, compartilhar, datajud, radar, rede  # noqa: E402

with open(os.path.join(_ROBO_, "radar_modelo.html"), encoding="utf-8") as _f:
    HTML = _f.read()


def _ler(*partes):
    with open(os.path.join(_RAIZ_, *partes), encoding="utf-8") as f:
        return f.read()


def _js_entre(inicio, fim):
    i = HTML.index(inicio)
    return HTML[i:HTML.index(fim, i)]


class InglesSemSobras(unittest.TestCase):
    def test_gazette_saiu_de_tudo(self):
        sem_novidades = HTML.replace("\u201cgazette\u201d", "")  # a linha das Novidades que conta a troca
        for nome, txt in (("tela", sem_novidades), ("site", _ler("paginas", "index.html")), ("antivírus", _ler("paginas", "antivirus.html")),
                          ("monitor", _ler("robo", "monitor_modelo.html")), ("painel", _ler("robo", "painel_modelo.html"))):
            self.assertNotRegex(txt, re.compile(r"\bgazettes?\b", re.I), nome)
        for mod in ("monitor", "causas", "radar", "historico", "app"):
            self.assertNotRegex(_ler("robo", "lexsuite", mod + ".py"), re.compile(r"\bgazettes?\b", re.I), mod)

    def test_manual_de_uso_e_user_guide(self):
        self.assertIn('link_manual: "Manual de uso"', HTML)
        self.assertIn('link_manual: "User guide"', HTML)

    def test_setores_portes_e_tipos_de_publicacao_tem_ingles(self):
        bloco = _js_entre("var VAL_EN = {", "function trVal")
        for nome, _ in classificar.SETORES:
            self.assertIn('"' + nome + '"', bloco, nome)
        self.assertIn('"Serviços e outros"', bloco)
        for p in ("ME", "EPP", "DEMAIS"):
            legivel = radar.porte_legivel(p)
            self.assertIn('"' + legivel + '"', bloco, legivel)
            self.assertIn('"' + legivel.split(" (")[0] + '"', bloco)
        for s in ("lista de distribuição", "audiência inicial", "notificação inicial", "citação inicial", "notifique-se a reclamada"):
            self.assertIn('"' + s + '"', bloco, s)
        self.assertIn('"Micro business (ME)"', bloco)

    def test_mensagens_da_leitura_e_texto_bilingue(self):
        if not shutil.which("node"):
            self.skipTest("sem node")
        js = ("var lang = 'en';\n" + _js_entre("function noIdioma(txt)", "\n  }\n") + "\n  }\n"
              + _js_entre("  var MSG_EN = [", "  var novaVista") + r"""
var casos = [
 ["  Caderno TRT9 23/NOV: já conferido (versão 1)", "  Court Journal TRT9 23/NOV: already checked (version 1)"],
 ["  Baixando o caderno TRT2 21/OUT (pode levar alguns minutos)...", "  Downloading Court Journal TRT2 21/OCT (may take a few minutes)..."],
 ["  Consultando o CNJ: 40 de 120…", "  Checking the CNJ: 40 of 120…"],
 ["  Receita: 10 de 40", "  Federal Revenue: 10 of 40"],
 ["Espere a leitura terminar. / Wait for the reading to finish.", "Wait for the reading to finish."],
 ["Empresa Ficticia Ltda", "Empresa Ficticia Ltda"]];
casos.forEach(function (c) { var r = msgIdioma(c[0]); if (r !== c[1]) { console.log("ERRO " + JSON.stringify([c[0], r])); process.exit(1); } });
lang = "pt"; if (msgIdioma("Espere. / Wait.") !== "Espere.") { console.log("ERRO pt"); process.exit(1); }
""")
        r = subprocess.run(["node", "-e", js], capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_faixas_e_avisos_passam_pelo_idioma(self):
        self.assertIn("(sit.mensagens || []).map(noIdioma)", HTML)
        self.assertIn("ultima = msgIdioma(String(ultima", HTML)
        self.assertIn("datasNoTexto(msgIdioma(m.texto))", HTML)
        self.assertIn('j.motivo = noIdioma(j.motivo)', HTML)
        self.assertIn("function textoVersaoNova()", HTML)

    def test_aviso_de_planilha_grande_inteiro_em_ingles(self):
        txt = armazenamento.aviso_tamanho("trabalhista", 51330, 60000)
        pt, en = txt.rsplit(" / ", 1)
        self.assertIn("51.330 de 60.000", pt)
        self.assertIn("LABOUR SPREADSHEET IS LARGE: 51,330 of 60,000 rows (86%)", en)
        self.assertNotRegex(en, r"[ãçõ]|Planilha|linhas")

    def test_espaco_antes_de_ainda_nao_salvo(self):
        self.assertRegex(HTML, r"\.rodar-criterio \.rc-nao-salvo \{[^}]*margin-left")


class TermosEmIngles(unittest.TestCase):
    def setUp(self):
        self.pag = _ler("paginas", "aceite.html")

    def test_secoes_em_portugues_iguais_ao_texto_aceito(self):
        """Trocar o idioma não muda a versão: o texto em português é o mesmo da 1.0 guardada (nenhum aceite novo)."""
        def secoes(txt):
            return {m.group(1): re.sub(r"\s+", " ", re.sub("<[^>]+>", "", m.group(2))).strip()
                    for m in re.finditer(r'<section id="(s\d+)"[^>]*>(.*?)</section>', txt, re.S)}
        atual, guardado = secoes(_ler("docs", "aceite.html")), secoes(_ler("docs", "termos", "v1.0.html"))
        self.assertEqual(len(atual), 11)
        self.assertEqual(atual, guardado)

    def test_ingles_completo_com_seletor_e_aviso_do_portugues(self):
        for i in range(1, 12):
            self.assertIn(f'<section id="s{i}" data-l="pt">', self.pag)
            self.assertIn(f'<section id="e{i}" data-l="en" lang="en" hidden>', self.pag)
        self.assertIn('id="b-pt"', self.pag); self.assertIn('id="b-en"', self.pag)
        self.assertIn("the Portuguese version prevails", self.pag)
        self.assertIn('q.get("idioma")', self.pag)

    def test_programa_abre_os_termos_no_idioma_da_tela(self):
        self.assertIn('"&idioma=" + lang', HTML)
        self.assertIn('"?ler=1&idioma=" + lang', HTML)


class LimpezaDaPlanilha(unittest.TestCase):
    def test_nao_diz_limpa_se_nao_regravou(self):
        b = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db")); self.addCleanup(b.con.close)
        with mock.patch.object(armazenamento, "copia_seguranca", return_value=(True, "/tmp/copia-ficticia")), \
                mock.patch.object(radar, "regravar_planilha", return_value=False):
            ok, msg = armazenamento.limpar({}, b, tempfile.mkdtemp(), "0.7.52", aviso=lambda *a: None)
        self.assertFalse(ok)
        self.assertIn("aberta no Excel", msg); self.assertIn("open in Excel", msg)

    def test_resultado_com_linhas_antes_e_depois_e_o_porque(self):
        txt = armazenamento.resumo_limpeza({"trabalhista": {"linhas": 51330, "limite": 60000}},
                                           {"trabalhista": {"linhas": 49000, "limite": 60000, "radar": 47000}})
        pt, en = txt.split(" / ")
        self.assertIn("Trabalhista: 51.330 → 49.000 linhas.", pt)
        self.assertIn("aba Radar tem 47.000 processos", pt)
        self.assertIn("Labour: 51,330 → 49,000 rows.", en)
        self.assertNotIn("Continua grande", armazenamento.resumo_limpeza({}, {"trabalhista": {"linhas": 20000, "limite": 60000, "radar": 15000}}))

    def test_faixa_mostra_andamento_resultado_e_fecha(self):
        bloco = _js_entre("function limparPlanilha()", "function desenharTermosConfig")
        for trecho in ('"gira-fino"', "x1.disabled = armLimpando", '"arm-x"', 'armRes.ok ? "✓"', 't("arm_limpando")'):
            self.assertIn(trecho, bloco, trecho)
        self.assertIn('arm_limpando: "Saving the backup and cleaning up the spreadsheet…"', HTML)


class RessalvasDaOperacao(unittest.TestCase):
    def setUp(self):
        self.b = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db")); self.addCleanup(self.b.con.close)
        for k in range(130):
            self.b.guardar_lead({"processo": f"99{k:05d}-11.2026.5.02.0001", "tribunal": "TRT2", "vara": "1ª Vara (fictícia)",
                                 "empresas": ["Empresa Ficticia Ltda"], "data_publicacao": "2026-11-19", "texto_curto": "x"}, "2026-11-19")

    def test_429_para_o_cnj_no_primeiro_aviso(self):
        chamadas, avisos = [], []

        def ocupado(ind, nums):
            chamadas.append(len(nums)); raise rede.ErroHTTP(429, "https://exemplo.invalid/", "muitos pedidos")
        est = radar.completar_fontes(self.b, dt.datetime(2026, 11, 20, 9), aviso=avisos.append, consultar=ocupado, historico=lambda *a: {})
        self.assertEqual(len(chamadas), 1)
        self.assertTrue(est["cnj_parou"])
        self.assertIn("  Consultando o CNJ: 40 de 130…", avisos)
        f = self.b.fontes_de(["9900000-11.2026.5.02.0001"])["9900000-11.2026.5.02.0001"]["cnj"]
        self.assertEqual(f["causa"], "o CNJ pediu para esperar (muitos pedidos)")

    def test_chave_do_cnj_curta_e_lembrada(self):
        chamadas = []

        def fora(*a, **kw):
            chamadas.append(kw); raise OSError("sem rede")
        with mock.patch.dict(os.environ, {}, clear=False), mock.patch.object(datajud, "_chave", [None]), \
                mock.patch.object(datajud, "_chave_falhou", [0.0]), mock.patch.object(datajud.rede, "pedir", fora):
            os.environ.pop("DATAJUD_APIKEY", None)
            with self.assertRaises(OSError):
                datajud.chave_publica()
            with self.assertRaises(RuntimeError):  # logo depois: nem tenta (10 minutos)
                datajud.chave_publica()
        self.assertEqual(len(chamadas), 1)
        self.assertEqual(chamadas[0].get("tentativas"), 2); self.assertLessEqual(chamadas[0].get("tempo_limite"), 20)

    def test_planilha_nova_ja_diz_ajuizado(self):
        self.assertNotIn("Distribuída em", _ler("robo", "lexsuite", "compartilhar.py"))

    def test_novidades_fecham_de_qualquer_jeito_respeitando_a_caixa(self):
        # ressalva 5: Esc ou clique fora fecham pela mesma função que o botão (aoFechar), que guarda "Não mostrar novamente"
        self.assertIn("j._aoFechar = aoFechar || null;  // revisão da 0.7.28: roda ao fechar de qualquer jeito", HTML)
        self.assertIn('function () { if (cx_ && cx_.checked) ls_("novidades-ocultas", v_); }', HTML)


class RodapeEVersao(unittest.TestCase):
    def test_rodape_curto_e_com_o_datajud(self):
        self.assertIn('rodape1: "Fontes: Diário de Justiça Eletrônico (DJEN), DataJud (CNJ)', HTML)
        self.assertIn('rodape1: "Sources: Electronic Court Journal (DJEN), DataJud (CNJ)', HTML)
        self.assertRegex(HTML, r"\.fim-lista \{[^}]*font-size: \.8rem; margin: 6px 0 12px; \}")

    def test_versao_e_novidades(self):
        from lexsuite import VERSAO
        self.assertTrue(VERSAO >= "0.7.52")
        i = HTML.index('"0.7.52": {'); bloco = HTML[i:HTML.index('"0.7.51": {')]
        pt = re.findall(r'"([^"]+)"', bloco[bloco.index("pt: ["):bloco.index("en: [")])
        en = re.findall(r'"([^"]+)"', bloco[bloco.index("en: ["):])
        self.assertEqual(len(pt), len(en)); self.assertTrue(4 <= len(pt) <= 8, len(pt))  # dono, 24/Nov: sucintas
        for linha in pt:
            self.assertNotRegex(linha, r"\b(agora|já lê|com um botão só|caixinha)\b")
        for linha in en:
            self.assertNotRegex(linha, r"\bnow\b")
        self.assertIn("0.7.52", _ler("paginas", "versoes.html"))


if __name__ == "__main__":
    unittest.main()
