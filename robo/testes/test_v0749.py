"""0.7.49 (decisões 43 a 48 do dono, 15/Nov): Modo no alto, filtros salvos (lista própria, descrição, período, 3 de fábrica),
Tribunal na primeira linha, Varas largas, lista aberta acompanha a rolagem, (?) animado, Agrupar por empresa com alcance.
Dados FICTÍCIOS, sem internet."""

import datetime as dt
import http.client
import json
import os
import re
import sys
import tempfile
import threading
import unittest

_ROBO_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RAIZ_ = os.path.dirname(_ROBO_)
sys.path.insert(0, _ROBO_)

from lexsuite import VERSAO, app, banco as bd, radar  # noqa: E402

with open(os.path.join(_ROBO_, "radar_modelo.html"), encoding="utf-8") as _f:
    HTML = _f.read()

HOJE = dt.date(2026, 11, 15)


def lead(b, proc, dia, nome, cnpj=""):
    b.guardar_lead({"processo": proc, "tribunal": "TRT2", "vara": "1ª Vara (fictícia)", "empresas": [nome], "data_publicacao": dia,
                    "cnpjs": [cnpj] if cnpj else [], "empresa_receita": {"cnpj": cnpj, "razao_social": nome} if cnpj else {}}, dia)


class ChaveEmpresa(unittest.TestCase):
    def test_raiz_do_cnpj_junta_matriz_e_filial(self):
        self.assertEqual(radar.chave_empresa("11.222.333/0001-81"), radar.chave_empresa("11222333000262"))
        self.assertEqual(radar.chave_empresa("11222333000181"), "c:11222333")

    def test_nome_sem_acento_e_sem_tipo_societario(self):
        self.assertEqual(radar.chave_empresa("", "Outra Fictícia S.A."), radar.chave_empresa("", "OUTRA FICTICIA SA"))
        self.assertEqual(radar.chave_empresa("", "Empresa Fictícia Ltda."), "n:empresa ficticia")
        self.assertEqual(radar.chave_empresa("", ""), "")

    def test_a_tela_usa_a_mesma_regra(self):
        self.assertIn('function chaveEmpresaTela(i)', HTML)
        self.assertIn("nomeParaCnpj_[k]", HTML)  # na tela, o processo sem CNPJ entra no bloco da mesma empresa com CNPJ
        self.assertIn('(ltda|s ?a|eireli|me|epp|limitada|sociedade anonima)', HTML)


class ProcessosDasEmpresas(unittest.TestCase):
    def setUp(self):
        self.b = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db"))
        self.addCleanup(self.b.con.close)
        for k in range(60):  # 60 processos da mesma empresa (fictícia) nos últimos ~5 meses e 5 antigos
            lead(self.b, f"0001{k:03d}-11.2026.5.02.0001", (HOJE - dt.timedelta(days=2 * k + 1)).isoformat(), "EMPRESA FICTICIA ABC LTDA", "11222333000181")
        for k in range(5):
            lead(self.b, f"0002{k:03d}-11.2025.5.02.0001", (HOJE - dt.timedelta(days=300 + k)).isoformat(), "Empresa Fictícia ABC Ltda", "11222333000262")
        lead(self.b, "0003000-11.2026.5.02.0001", (HOJE - dt.timedelta(days=3)).isoformat(), "Outra Fictícia S.A.")
        lead(self.b, "0003001-11.2026.5.02.0001", (HOJE - dt.timedelta(days=40)).isoformat(), "OUTRA FICTICIA SA")
        lead(self.b, "0003002-11.2026.5.02.0001", (HOJE - dt.timedelta(days=40)).isoformat(), "Outra Coisa Ltda")

    def pedir(self, alcance, quem):
        return radar.processos_das_empresas({"radar": {}}, self.b, quem, alcance, hoje=HOJE)

    def test_hibrido_ate_50_dos_ultimos_6_meses_com_o_total(self):
        r = self.pedir("hibrido", [{"cnpj": "11222333000181"}])["c:11222333"]
        self.assertEqual((r["total"], len(r["itens"])), (65, 50))
        datas = [i["diario_em"] for i in r["itens"]]
        self.assertEqual(datas, sorted(datas, reverse=True))  # do mais novo ao mais antigo

    def test_alcances(self):
        quem = [{"cnpj": "11222333000181"}]
        self.assertEqual(len(self.pedir("todos", quem)["c:11222333"]["itens"]), 65)
        self.assertEqual(len(self.pedir("10", quem)["c:11222333"]["itens"]), 10)
        self.assertEqual(len(self.pedir("6m", quem)["c:11222333"]["itens"]), 60)
        self.assertEqual(len(self.pedir("12m", quem)["c:11222333"]["itens"]), 65)
        self.assertEqual(len(self.pedir("30d", quem)["c:11222333"]["itens"]), 15)

    def test_mesma_empresa_com_e_sem_cnpj_num_bloco_so(self):
        lead(self.b, "0005000-11.2026.5.02.0001", (HOJE - dt.timedelta(days=5)).isoformat(), "Açúcar Fictício S/A", "55444333000122")
        lead(self.b, "0005001-11.2026.5.02.0001", (HOJE - dt.timedelta(days=9)).isoformat(), "AÇÚCAR FICTÍCIO SA")
        lead(self.b, "0005002-11.2026.5.02.0001", (HOJE - dt.timedelta(days=9)).isoformat(), "Açúcar Fictício S.A.", "77666555000199")  # homônimo, outro CNPJ
        r = self.pedir("todos", [{"chave": "c:55444333", "cnpj": "55444333000122", "nome": "Açúcar Fictício S/A"}])["c:55444333"]
        self.assertEqual(sorted(i["processo"] for i in r["itens"]), ["0005000-11.2026.5.02.0001", "0005001-11.2026.5.02.0001"])
        self.assertEqual((r["total"], r["sem_cnpj"]), (1, 1))  # a chave é o CNPJ: o sem CNPJ vem marcado e fora do total
        self.assertTrue(next(i for i in r["itens"] if i["processo"] == "0005001-11.2026.5.02.0001").get("so_nome"))
        self.assertFalse(next(i for i in r["itens"] if i["processo"] == "0005000-11.2026.5.02.0001").get("so_nome"))

    def test_sem_cnpj_pelo_nome_com_e_sem_acento(self):
        r = self.pedir("todos", [{"nome": "Outra Ficticia S/A"}])["n:outra ficticia"]
        self.assertEqual(sorted(i["processo"] for i in r["itens"]), ["0003000-11.2026.5.02.0001", "0003001-11.2026.5.02.0001"])


CFG = {"conta": {"codigo": "LEX-ABCD-EFGH", "instalacao": "0123456789abcdef", "resposta": "ok", "ok": True, "ultima_ok": "2099-01-01"},
       "radar": {"tribunais": ["TRT2"]}}


class Rota(unittest.TestCase):
    def test_empresas_processos(self):
        pasta = tempfile.mkdtemp()
        with open(os.path.join(pasta, "config.json"), "w", encoding="utf-8") as f:
            json.dump(CFG, f)
        srv = app.Servidor(("127.0.0.1", 0), pasta)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.addCleanup(srv.server_close)
        self.addCleanup(srv.shutdown)
        b = bd.Banco(srv.caminho_db)
        lead(b, "0004000-11.2026.5.02.0001", (dt.date.today() - dt.timedelta(days=2)).isoformat(), "EMPRESA FICTICIA XYZ LTDA", "99888777000166")
        b.con.close()
        c = http.client.HTTPConnection("127.0.0.1", srv.server_address[1], timeout=20)
        c.request("POST", "/empresas/processos", body=json.dumps({"alcance": "hibrido", "empresas": [{"chave": "c:99888777"}]}),
                  headers={"X-LexSuite": "1", "Content-Type": "application/json"})
        d = json.loads(c.getresponse().read())
        c.close()
        self.assertTrue(d["ok"])
        self.assertEqual(d["empresas"]["c:99888777"]["total"], 1)


class Tela(unittest.TestCase):
    def test_versao_e_novidades(self):
        self.assertEqual(VERSAO, "0.7.49")
        self.assertIn('"0.7.49": {', HTML)

    def test_chaves_em_pt_e_en(self):
        for k in ("agr_so_nome", "agr_n_so_nome", "modo_rot", "modo_sem_licenca", "modo_fale", "modo_tributario", "modo_penal", "salvos_n", "salvos_organizar", "salvar_desc_q",
                  "fab1_n", "fab1_d", "fab2_n", "fab2_d", "fab3_n", "fab3_d", "agr_nada", "agr_empresa", "agr_desliga", "alc_hibrido", "alc_todos",
                  "agr_mostrando", "agr_anterior", "agr_fora", "agr_mostrando_emp", "ord_ajuda", "m_cab_n", "m_cab_vara", "w4_pronto"):
            self.assertEqual(len(re.findall(r"\b" + k + r': "', HTML)), 2, k)

    def test_modo_no_lugar_da_planilha(self):
        self.assertIn('id="b-modo"', HTML)
        self.assertIn('$("b-planilha").hidden = true;', HTML)
        self.assertIn('modo_sem_licenca: "Não incluído na sua licença"', HTML)
        self.assertIn('planilha_abrir: "Abrir a planilha oficial (só leitura)"', HTML)

    def test_tribunal_na_primeira_linha(self):
        i_per, i_trib, i_sit = HTML.index('<select id="periodo">'), HTML.index('id="f-trib"'), HTML.index('id="f-sit"')
        self.assertTrue(i_per < i_trib < i_sit)
        self.assertNotIn('"cnpj", "trib", "data"', HTML)  # fora da contagem de "Mais filtros"

    def test_lista_acompanha_a_rolagem(self):
        self.assertIn('window.addEventListener("scroll", function () { if (ancora_) ancora_.pos(); }, true);', HTML)

    def test_ajuda_animada_e_na_cor_de_link(self):
        self.assertIn("@keyframes balao-cresce", HTML)
        self.assertIn("prefers-reduced-motion: reduce) { .balao { animation: none; }", HTML)
        self.assertIn(".ajuda:not(.aberta) { color: var(--barra);", HTML)

    def test_filtros_salvos_de_fabrica(self):
        self.assertIn('localStorage.getItem("lexsuite:filtros-fabrica") === "1"', HTML)
        self.assertIn('agrupar: "empresa", alcance: "hibrido"', HTML)
        self.assertIn("periodo: periodo, agrupar: agrupar, alcance: alcance, desc:", HTML)

    def test_busca_do_assistone(self):
        for termo in ('"agrupar"', '"filtros prontos"', '"modo"', '"especialidade"'):
            self.assertIn(termo, HTML, termo)
        self.assertIn('seletor: "#b-modo"', HTML)

    def test_manual(self):
        with open(os.path.join(_RAIZ_, "paginas", "manual.html"), encoding="utf-8") as f:
            m = f.read()
        for trecho in ("<b>Modo</b>", "Não incluído na sua licença", "Abrir a planilha oficial (só leitura)", "<b>Agrupar por empresa</b>",
                       "até 50 dos últimos 6 meses", "Para contatar (7 dias)", "<b>Primeiro acesso.</b>", "fora dos filtros"):
            self.assertIn(trecho, m, trecho)
        self.assertNotIn("<b>Abrir a planilha</b>, no alto", m)


if __name__ == "__main__":
    unittest.main()
