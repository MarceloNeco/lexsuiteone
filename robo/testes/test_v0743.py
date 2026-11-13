"""0.7.43 (dono, 13/Nov): empresas excluídas pelo nome exato e pelo CPF, desempenho do Painel, AssistONE ao carregar."""

import importlib.util
import os
import re
import sys
import unittest

_ROBO_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RAIZ_ = os.path.dirname(_ROBO_)
sys.path.insert(0, _ROBO_)

from lexsuite import classificar, preferencias  # noqa: E402

with open(os.path.join(_ROBO_, "radar_modelo.html"), encoding="utf-8") as _f:
    HTML = _f.read()


def excluida(nomes, exclusoes, cnpj=None, razao=None):
    it = {"empresas": nomes}
    if cnpj or razao:
        it["empresa"] = {"cnpj": cnpj or "", "razao_social": razao or ""}
    return preferencias.aplicar([it], {"exclusoes": exclusoes})[0]["excluida"]


class Excluidas0743(unittest.TestCase):
    def test_nome_nao_exclui_outra_empresa(self):
        exc = [{"nome": "Bebidas Ltda", "motivo": ""}]
        self.assertTrue(excluida(["BEBIDAS LTDA"], exc))
        self.assertTrue(excluida(["Bebidas Ltda."], exc))  # pontuação não importa
        for outro in ("Bebidas S.A.", "Bebidas ME", "Cia Bebidas", "Bebidas"):
            self.assertEqual(excluida([outro], exc), "", outro)

    def test_nome_sem_acento_e_caixa(self):
        self.assertTrue(excluida(["CONSTRUÇÃO ÁGIL LTDA"], [{"nome": "construcao agil ltda", "motivo": ""}]))

    def test_cpf_exclui_o_mei_com_o_cpf_no_nome(self):
        exc = [{"nome": "529.982.247-25", "motivo": "cliente"}]
        self.assertEqual(excluida(["JOAO DA SILVA 52998224725"], exc), "Exclusão: cliente")
        self.assertEqual(excluida(["Outra Empresa"], exc, razao="JOAO DA SILVA 52998224725"), "Exclusão: cliente")
        self.assertEqual(excluida(["MARIA 12345678909"], exc), "")  # outro CPF
        self.assertEqual(excluida(["JOAO DA SILVA"], exc), "")  # sem o CPF no nome: não exclui
        self.assertEqual(excluida(["EMPRESA 529982247250"], exc), "")  # 12 dígitos não é o CPF

    def test_cnpj_continua_exato(self):
        exc = [{"nome": "Empresa X", "cnpj": "11222333000181", "motivo": ""}]
        self.assertEqual(excluida(["Nome Qualquer"], exc, cnpj="11222333000181"), "Exclusão: CNPJ na lista")
        self.assertEqual(excluida(["Nome Qualquer"], exc, cnpj="11222333000262"), "")

    def test_funcoes(self):
        self.assertEqual(classificar.chave_exata("Bebidas Ltda."), "BEBIDAS LTDA")
        self.assertEqual(classificar.cpfs_no_nome("JOAO 529.982.247-25"), {"52998224725"})

    def test_tela(self):
        self.assertEqual(HTML.count("rg_exc_cpf:"), 2); self.assertEqual(HTML.count("rg_exc_ajuda:"), 2)
        self.assertIn('aviso(cpfOk(n) ? t("rg_exc_cpf") : "", "nota-g")', HTML)


class Desempenho0743(unittest.TestCase):
    def test_painel_sem_ordenar_e_com_memoria(self):
        self.assertIn("desenharPainel(filtrados());", HTML)
        self.assertIn("function valorManual(id)", HTML)
        self.assertIn("if (i._fg !== memoF.g) { i._ff = avaliarFiltros(i, min, esconder, q); i._fg = memoF.g; }", HTML)
        self.assertIn("Promise.resolve().then(function () { memoF = null; });", HTML)  # a memória não passa do desenho

    def test_assistone_ao_carregar(self):
        self.assertIn('if ($("carregando") && !$("carregando").hidden) return "carregando";', HTML)
        self.assertIn("carregando: { titulo: { pt: \"Carregando\", en: \"Loading\" }", HTML)


class Configuracoes0743(unittest.TestCase):
    """Dono, 13/Nov: desmarcou sábado e domingo, salvou, reabriu e voltou o de antes (a carga antiga da lista sobrescrevia)."""

    def test_so_a_carga_mais_nova_vale(self):
        self.assertIn("meu_ = ++seqCarga", HTML)
        self.assertIn("if (meu_ !== seqCarga) return ultimaCarga;", HTML)

    def test_tela_fica_com_o_que_foi_salvo(self):
        self.assertIn('["horarios", "dias", "avisar_ao_terminar", "abrir_em_aba"].forEach(function (k) { if (k in r.radar) APP.config[k] = r.radar[k]; });', HTML)

    def test_salvar_gira_e_so_manda_o_que_mudou(self):
        self.assertIn('$("c-salvar").classList.add("salvando"); ocupadoLigar(t("c_salvando"));', HTML)
        self.assertEqual(HTML.count("c_salvando:"), 2)
        self.assertIn("if (cA_.pasta && corpo.pasta === cA_.pasta) { delete corpo.pasta; delete corpo.criar; }", HTML)

    def test_roteiro_de_tela_existe(self):
        with open(os.path.join(_ROBO_, "testes", "tela", "fluxos.js"), encoding="utf-8") as f:
            js = f.read()
        self.assertIn("reabrir logo depois de salvar mostra os dias salvos", js)


class Busca0743(unittest.TestCase):
    def test_busca_nao_trava(self):
        self.assertIn("if (q_.length === 1) { if (!F.busca) return; usa_ = \"\"; }", HTML)
        self.assertIn("i._ab.indexOf(q) < 0", HTML)  # o texto de busca de cada processo é preparado uma vez


class PacoteCompleto0743(unittest.TestCase):
    def test_completo_usa_o_instalar_txt_recebido(self):
        spec = importlib.util.spec_from_file_location("marca", os.path.join(_RAIZ_, "ferramentas", "marca.py"))
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        texto = m.INSTALAR_TXT.read_text(encoding="utf-8")
        import io
        import zipfile
        z = zipfile.ZipFile(io.BytesIO(m.completo_zip(texto)))
        self.assertEqual(z.read("dados/instalar.txt").decode("utf-8"), texto)


class Versao0743(unittest.TestCase):
    def test_versao_e_novidades(self):
        from lexsuite import VERSAO
        self.assertGreaterEqual(tuple(int(x) for x in VERSAO.split(".")), (0, 7, 43))  # a versão sobe
        bloco = HTML[HTML.index('"0.7.43": {'):HTML.index('"0.7.42": {')]
        pt = re.findall(r'"((?:[^"\\]|\\.)+)"', bloco[bloco.index("pt: ["):bloco.index("en: [")])
        en = re.findall(r'"((?:[^"\\]|\\.)+)"', bloco[bloco.index("en: ["):])
        self.assertEqual(len(pt), len(en)); self.assertEqual(len(pt), 9)


if __name__ == "__main__":
    unittest.main()
