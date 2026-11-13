"""0.7.37 (teste do dono na 0.7.36 e ressalvas da Operação): dados fictícios, sem internet."""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

_ROBO_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROBO_)

from lexsuite import app, cnpj, rede, saude  # noqa: E402
from lexsuite import banco as bd  # noqa: E402


def ler(*partes):
    with open(os.path.join(_ROBO_, *partes), encoding="utf-8") as f:
        return f.read()


HTML = ler("radar_modelo.html")


class Tela0737(unittest.TestCase):
    def test_painel_mostra_os_filtros_dos_graficos(self):
        regra = re.search(r"\.barra-lista\.no-painel #f-busca[^{]*\{ display: none !important; \}", HTML).group(0)
        for id_ in ("f-sit", "f-vara", "f-setor", "f-porte", "f-uf"):
            self.assertNotIn("#" + id_, regra)
        self.assertNotIn(".multi.multi-vazio", regra)
        self.assertIn("#f-trib.multi-vazio", regra); self.assertIn("#f-data.multi-vazio", regra)

    def test_configuracoes_sem_paragrafo_e_mais_larga(self):
        self.assertNotIn('id="c-mira"', HTML); self.assertNotIn("mira_conf", HTML)
        self.assertIn("width: min(1280px, 96vw)", HTML)
        self.assertIn("#config .conf-cab + h4.conf-sec { margin-top: 0; }", HTML)

    def test_busca_das_excluidas_sem_rotulo_visivel(self):
        self.assertIn('buscaRot.appendChild(el("span", "so-leitor", t("rg_busca_rot")));', HTML)

    def test_andamento_sem_a_frase_do_caminho(self):
        if not shutil.which("node"):
            self.skipTest("sem node")
        linha = next(x for x in HTML.splitlines() if "ultima = String(ultima" in x)
        js = ("var ultima;\nfunction limpa(x) { ultima = x;\n" + linha + "\nreturn ultima; }\n"
              "var casos = [['Gravando em C:\\\\Users\\\\Fulano\\\\OneDrive - Escritorio\\\\x.xlsx', ''],"
              "['Lidas 30 publicações. Gravando em C:\\\\a b\\\\c.xlsx', 'Lidas 30 publicações.'],"
              "['Planilha: \\\\\\\\servidor\\\\pasta\\\\x.xlsx', ''],"
              "['Montando a lista: 30 processos.', 'Montando a lista: 30 processos.'],"
              "['TRT2 06/11: 120 publicações. Página: 3', 'TRT2 06/11: 120 publicações.']];\n"
              "casos.forEach(function (c) { var r = limpa(c[0]); if (r !== c[1]) { console.log('ERRO ' + JSON.stringify(r)); process.exit(1); } });\n")
        r = subprocess.run(["node", "-e", js], capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_faixa_da_leitura_no_celular_em_grade(self):
        m = re.search(r"@media \(max-width: 600px\) \{ \.estado \.rodando-linha \{ display: grid;[^\n]*", HTML)
        self.assertIsNotNone(m)
        self.assertIn(".estado .rodando-linha > button, .estado .rodando-linha > .aviso-leve { grid-column: 2; grid-row: 1; }", m.group(0))
        self.assertIn(".estado .rodando-linha .andando { grid-column: 1 / -1; grid-row: 2;", m.group(0))

    def test_duplo_clique_em_acrescentar(self):
        self.assertIn("if (!nNome.value.trim() && Date.now() - (bAdd._ultimaOk || 0) < 1500) return;", HTML)
        self.assertIn("bAdd._ultimaOk = Date.now();", HTML)

    def test_assistone_e_manual_com_os_filtros_do_painel(self):
        self.assertIn("o gráfico e o filtro são a mesma escolha", HTML)
        self.assertNotIn("dentro de Mais filtros, tem ✕", HTML)
        man = ler("..", "paginas", "manual.html")
        self.assertIn("O gráfico e o filtro são a mesma escolha", man)
        self.assertNotIn("mostra no alto só os que não têm gráfico", man)
        self.assertNotIn("trecho do Diário de cada ação", man)
        self.assertIn("só é liberado às 3h da manhã", man)


class Robo0737(unittest.TestCase):
    def ultima(self, lidas, novas):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        b = bd.Banco(os.path.join(d, "lexsuite.db"))
        b.registrar("radar", {"resultado": "ok", "lidas": lidas, "novas": novas})
        b.con.close()
        falso = types.SimpleNamespace(caminho_db=os.path.join(d, "lexsuite.db"), _ultima_cache=None)
        return app.Servidor.ultima_do_banco(falso)

    def test_ultima_atualizacao_no_singular_em_ingles(self):
        u = self.ultima(1, 1)
        self.assertEqual(u["en"], "1 notice read; 1 new case against companies.")
        self.assertEqual(u["pt"], "1 publicação lida; 1 processo novo contra empresas.")
        u = self.ultima(5, 2)
        self.assertEqual(u["en"], "5 notices read; 2 new cases against companies.")

    def test_saude_no_singular(self):
        r = saude.avaliar([{"x": 1}] * 10, [{"y": 1}])
        det = [x["detalhe"] for x in r if x["fonte"] == "Regra de processo novo"]
        self.assertIn("1 processo novo em 10 publicações.", det)

    def test_cnpj_uma_fonte_fora_e_outra_404_nao_e_nao_encontrado(self):
        for codigos in ((500, 404), (404, 503), (404, None)):
            def pedir(url, **k):
                c = codigos[0] if "brasilapi" in url else codigos[1]
                if c is None:
                    raise OSError("tempo esgotado")
                raise rede.ErroHTTP(c, url, "")
            with mock.patch.object(cnpj.rede, "pedir_json", side_effect=pedir):
                r = cnpj.consultar("11222333000181", rapido=True)
            self.assertEqual((r or {}).get("situacao"), "sem_resposta", codigos)

    def test_cnpj_as_duas_404_e_nao_encontrado(self):
        with mock.patch.object(cnpj.rede, "pedir_json", side_effect=lambda url, **k: (_ for _ in ()).throw(rede.ErroHTTP(404, url, ""))):
            self.assertIsNone(cnpj.consultar("11222333000181", rapido=True))

    def test_consulta_rapida_uma_tentativa_e_tempo_curto(self):
        with mock.patch.object(cnpj.rede, "pedir_json", side_effect=OSError("x")) as p_:
            cnpj.consultar("11222333000181", rapido=True)
        for chamada in p_.call_args_list:
            self.assertEqual(chamada.kwargs["tentativas"], 1); self.assertEqual(chamada.kwargs["tempo_limite"], 6)

    def test_textos_sem_acoes_novas(self):
        for arq in (("lexsuite", "avisar.py"), ("lexsuite_robo.py",), ("lexsuite", "preferencias.py")):
            t_ = ler(*arq)
            self.assertNotIn("ações novas contra empresas", t_, arq)
        self.assertNotIn("list criteria", ler("lexsuite", "preferencias.py"))

    def test_versao_e_novidades(self):
        from lexsuite import VERSAO
        self.assertGreaterEqual(tuple(int(x) for x in VERSAO.split(".")), (0, 7, 37))
        bloco = HTML[HTML.index('"0.7.37": {'):HTML.index('"0.7.36": {')]
        self.assertIn("Inclusão dos filtros Situação, Vara, Setor, Porte e Estado no Painel, ligados aos gráficos.", bloco)
        self.assertIn("Status, Court unit, Sector, Size and State filters on the Dashboard, linked to the charts.", bloco)


if __name__ == "__main__":
    unittest.main()
