"""0.7.50 (dono, 16/Nov): agrupamento (alcance no bloco, recolher, caixinha da empresa, sem CNPJ com CNPJ provável, copiar contato,
excluir empresa), notebook (filtros numa linha, rótulos curtos), barra de seleção com Aplicar, Configurações (rodapé, frase, consulta,
Rotina de limpeza, prazos gravados ao limpar, volta do Histórico), registro com envio ao suporte, conexão fechada pela tela, tour travado.
Dados FICTÍCIOS, sem internet."""

import datetime as dt
import http.client
import io
import json
import os
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

HOJE = dt.date(2026, 11, 16)


def lead(b, proc, dia, nome, cnpj="", fone=""):
    emp = {"cnpj": cnpj, "razao_social": nome} if cnpj else {}
    if fone:
        emp["telefone"] = fone
    b.guardar_lead({"processo": proc, "tribunal": "TRT2", "vara": "1ª Vara (fictícia)", "empresas": [nome], "data_publicacao": dia,
                    "cnpjs": [cnpj] if cnpj else [], "empresa_receita": emp}, dia)


def dia(n):
    return (HOJE - dt.timedelta(days=n)).isoformat()


class CnpjProvavel(unittest.TestCase):
    def setUp(self):
        self.b = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db"))
        self.addCleanup(self.b.con.close)

    def test_sugere_so_com_uma_raiz_e_prefere_a_matriz(self):
        lead(self.b, "0001001-11.2026.5.02.0001", dia(1), "EMPRESA FICTICIA DE CORREIO", "11222333000262")
        lead(self.b, "0001002-11.2026.5.02.0001", dia(2), "Empresa Fictícia de Correio", "11222333000181")
        lead(self.b, "0001003-11.2026.5.02.0001", dia(3), "EMPRESA FICTÍCIA DE CORREIO")
        lead(self.b, "0001004-11.2026.5.02.0001", dia(4), "Empresa Ficticia de Correio")
        s = radar.cnpj_provavel(self.b, "Empresa Fictícia de Correio")
        self.assertEqual(s, {"cnpj": "11222333000181", "com_cnpj": 2, "sem_cnpj": 2})
        self.assertEqual(radar.usar_cnpj(self.b, "Empresa Fictícia de Correio", s["cnpj"]), 2)
        self.assertEqual(radar.cnpj_provavel(self.b, "Empresa Fictícia de Correio"), {})  # nada mais sem CNPJ: não sugere de novo
        r = radar.processos_das_empresas({"radar": {}}, self.b, [{"chave": "c:11222333", "cnpj": "11222333000181"}], "todos", hoje=HOJE)
        self.assertEqual(len(r["c:11222333"]["itens"]), 4)  # os confirmados entram no mesmo bloco

    def test_homonimo_com_dois_cnpjs_nao_sugere(self):
        lead(self.b, "0002001-11.2026.5.02.0001", dia(1), "Padaria Ficticia Ltda", "11222333000181")
        lead(self.b, "0002002-11.2026.5.02.0001", dia(2), "Padaria Fictícia Ltda", "99888777000166")
        lead(self.b, "0002003-11.2026.5.02.0001", dia(3), "PADARIA FICTICIA LTDA")
        self.assertEqual(radar.cnpj_provavel(self.b, "Padaria Ficticia Ltda"), {})  # a chave é o CNPJ: na dúvida, não sugere

    def test_cnpj_invalido_nao_grava(self):
        lead(self.b, "0003001-11.2026.5.02.0001", dia(1), "Loja Ficticia Ltda")
        self.assertEqual(radar.usar_cnpj(self.b, "Loja Ficticia Ltda", "123"), 0)


class CopiarContato(unittest.TestCase):
    def setUp(self):
        self.b = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db"))
        self.addCleanup(self.b.con.close)
        for k, d in enumerate((2, 10, 40, 120)):  # a mesma empresa (fictícia), sem telefone na Receita
            lead(self.b, f"0004{k:03d}-11.2026.5.02.0001", dia(d), "EMPRESA FICTICIA ABC LTDA", "55444333000122")
        self.b.guardar_contato({"processo": "0004001-11.2026.5.02.0001", "canal": "telefone", "valor": "(11) 0000-0001",
                                "fonte": "PJe (cadastro da parte)", "origem": "area_logada"})
        self.b.guardar_contato({"processo": "0004001-11.2026.5.02.0001", "canal": "email", "valor": "advogado@ficticio.example",
                                "fonte": "petição (advogado da empresa)", "origem": "area_logada"})
        self.b.guardar_contato({"processo": "0004001-11.2026.5.02.0001", "canal": "telefone", "valor": "(11) 0000-0002",
                                "fonte": "PJe", "origem": "area_logada", "de_pessoa": True})

    def copiar(self, dias):
        return radar.copiar_contato_empresa({"radar": {}}, self.b, "c:55444333", dias, "55444333000122", "", "ana@example.com", hoje=HOJE)

    def test_so_o_contato_da_empresa_nos_sem_contato_do_periodo(self):
        r = self.copiar(90)
        self.assertEqual((r["origem"], r["processos"], r["copiados"]), ("0004001-11.2026.5.02.0001", 2, 2))  # 2 e 40 dias; 120 fica fora
        cop = [c for c in self.b.contatos() if c.get("origem") == "copiado"]
        self.assertEqual(sorted(c["processo"] for c in cop), ["0004000-11.2026.5.02.0001", "0004002-11.2026.5.02.0001"])
        self.assertTrue(all(c["valor"] == "(11) 0000-0001" for c in cop))  # nunca o do advogado nem o de pessoa física
        self.assertTrue(all("copiado de 0004001-11.2026.5.02.0001" in c["observacao"] and c["confianca"] == "baixa" for c in cop))

    def test_desfazer_apaga_so_os_copiados(self):
        r = self.copiar(365)
        self.assertEqual(r["copiados"], 3)
        self.b.desfazer_copia(r["ids"] + [1])  # o id 1 é um contato de verdade: não sai
        self.assertFalse([c for c in self.b.contatos() if c.get("origem") == "copiado"])
        self.assertEqual(len(self.b.contatos("0004001-11.2026.5.02.0001")), 3)

    def test_contato_de_outra_parte_do_processo_nao_vai(self):  # revisão da 0.7.50
        self.b.guardar_contato({"processo": "0004001-11.2026.5.02.0001", "empresa": "Outra Fictícia S.A.", "canal": "telefone",
                                "valor": "(11) 0000-0009", "fonte": "PJe", "origem": "area_logada"})
        self.copiar(90)
        self.assertFalse([c for c in self.b.contatos() if c.get("origem") == "copiado" and c["valor"] == "(11) 0000-0009"])

    def test_sem_contato_nenhum_nao_copia(self):
        self.b.con.execute("DELETE FROM contatos")
        self.b.con.commit()
        self.assertEqual(self.copiar(90)["copiados"], 0)


CFG = {"conta": {"codigo": "LEX-ABCD-EFGH", "instalacao": "0123456789abcdef", "resposta": "ok", "ok": True, "ultima_ok": "2099-01-01"},
       "radar": {"tribunais": ["TRT2"], "resumir_meses": 6, "apagar_meses": 24}, "usuario": {"email": "ana@example.com"}, "escritorio": "Escritório Fictício"}


class Rotas(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.mkdtemp()
        with open(os.path.join(self.pasta, "config.json"), "w", encoding="utf-8") as f:
            json.dump(CFG, f)
        self.srv = app.Servidor(("127.0.0.1", 0), self.pasta)
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.addCleanup(self.srv.server_close)
        self.addCleanup(self.srv.shutdown)

    def pedir(self, caminho, corpo=None, metodo="POST"):
        c = http.client.HTTPConnection("127.0.0.1", self.srv.server_address[1], timeout=30)
        c.request(metodo, caminho, body=json.dumps(corpo or {}) if metodo == "POST" else None, headers={"X-LexSuite": "1", "Content-Type": "application/json"})
        d = json.loads(c.getresponse().read())
        c.close()
        return d

    def test_usar_cnpj_recusa_cnpj_invalido(self):
        d = self.pedir("/empresas/usar-cnpj", {"nome": "Loja Ficticia Ltda", "cnpj": "11222333000180"})
        self.assertFalse(d["ok"])

    def test_limpar_com_prazos_novos_grava_os_prazos(self):
        d = self.pedir("/limpeza/agora", {"resumir_meses": 7, "apagar_meses": 30, "salvar_prazos": True})
        self.assertTrue(d["ok"])
        self.assertEqual(d["prazos_salvos"], [7, 30])
        with open(os.path.join(self.pasta, "config.json"), encoding="utf-8") as f:
            r = json.load(f)["radar"]
        self.assertEqual((r["resumir_meses"], r["apagar_meses"]), (7, 30))

    def test_prazo_fora_da_regra_nao_limpa_nem_grava(self):
        d = self.pedir("/limpeza/agora", {"resumir_meses": 12, "apagar_meses": 3, "salvar_prazos": True})
        self.assertFalse(d["ok"])
        with open(os.path.join(self.pasta, "config.json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["radar"]["apagar_meses"], 24)

    def test_registro_para_o_suporte_sem_a_licenca_inteira_nem_a_pasta_do_usuario(self):
        os.makedirs(os.path.join(self.pasta, "saida"), exist_ok=True)
        casa = os.path.expanduser("~")
        with open(os.path.join(self.pasta, "saida", "registro.txt"), "w", encoding="utf-8") as f:
            f.write(f"linha 1\nabri {casa}{os.sep}Documentos{os.sep}x.txt\nC:\\Users\\Fulano\\AppData\\y\n")
        d = self.pedir("/registro", metodo="GET")
        sp = d["suporte"]
        self.assertEqual(sp["licenca"], "LEX-••••-EFGH")
        self.assertNotIn("ABCD", json.dumps(sp))
        self.assertEqual((sp["email"], sp["escritorio"], sp["versao"], sp["endereco"]), ("ana@example.com", "Escritório Fictício", VERSAO, "judicial@solverone.com.br"))
        self.assertNotIn(casa, d["texto_suporte"])
        self.assertNotIn("Fulano", d["texto_suporte"])

    def test_excluir_uma_empresa_pelo_nome_tira_do_radar(self):
        d = self.pedir("/regras/excluir-uma", {"area": "trabalhista", "nome": "Empresa Ficticia de Correio", "cnpj": ""})
        self.assertTrue(d.get("ok"), d)


class ConexaoFechada(unittest.TestCase):
    def test_10053_sem_rastro(self):
        class Falha(io.BytesIO):
            def write(self, *_):
                raise ConnectionAbortedError(10053, "fechada pela tela")
        t = app.Tratador.__new__(app.Tratador)
        t.wfile, t.request_version, t.requestline, t.command = Falha(), "HTTP/1.1", "GET / HTTP/1.1", "GET"
        t.client_address, t.close_connection, t._headers_buffer = ("127.0.0.1", 0), False, []
        t.log_request = lambda *a, **k: None
        t._responder({"ok": True})  # não levanta
        self.assertTrue(t.close_connection)


class Tela(unittest.TestCase):
    def test_versao_e_novidades(self):
        self.assertTrue(VERSAO >= "0.7.50")
        self.assertIn('"0.7.50": {', HTML)

    def test_chaves_em_pt_e_en(self):
        for k in ("agr_expandir", "agr_recolher", "agr_marcar", "agr_sem_cnpj_x", "cp_link", "cp_x", "cc_link", "cc_x", "cc_feito_1", "ex_link", "ex_x",
                  "frc_trib", "frs_trib", "frc_sit", "frs_cidade", "busca_curta", "limpar_curto", "mais_curto", "feito_1", "aplicar", "arquivar", "lp_nao_confirmar",
                  "lp_prazos_novos", "ag_consulta_ajuda", "reg_enviar", "reg_copiar_ic", "reg_enviado"):
            self.assertEqual(HTML.count(" " + k + ": \""), 2, k)

    def test_textos_do_dono(self):
        self.assertIn('ag_salvar_dica: "As alterações desta janela passam a valer depois de Salvar."', HTML)
        self.assertIn('ag_salvar_dica: "Changes in this window take effect after Save."', HTML)
        self.assertIn('ag_consulta: "Usar a consulta pública do CNJ quando o caderno falhar"', HTML)
        self.assertIn('lp_t: "Rotina de limpeza"', HTML)
        self.assertIn('frs_trib: "Tribunais selecionados"', HTML)
        self.assertIn('fr_trib: "Tributário · em breve"', HTML)  # a chave antiga da frente continua (sem colisão)
        self.assertNotIn("Ligada por padrão. Se o caderno", HTML)
        self.assertNotIn("Não tenta se a SolverONE", HTML)
        self.assertNotIn('"Limpar o banco agora"', HTML)
        self.assertNotIn("processo(s) agora em", HTML)
        self.assertNotIn('arquivar_n: "Arquivar {n}"', HTML)

    def test_rotina_de_limpeza_entre_leitura_e_armazenamento(self):
        a, l, m = HTML.index('id="c-agendar-wrap"'), HTML.index('id="c-limpeza-wrap"'), HTML.index('id="c-arm-wrap"')
        self.assertTrue(a < l < m)
        self.assertIn('[t("lp_t"), function () { abrirConfig(true, "c-limpeza-wrap"); }]', HTML)  # menu ☰ → Configurações na mesma ordem

    def test_tour_trava_a_rolagem(self):
        self.assertIn("travarRolagem: function (ligar)", HTML)
        self.assertIn("Assistente.travarRolagem(false);", HTML)

    def test_manual_e_novidades(self):
        with open(os.path.join(_RAIZ_, "paginas", "manual.html"), encoding="utf-8") as f:
            m = f.read()
        for trecho in ("Rotina de limpeza", "Não confirmar", "Copiar o contato para os sem contato", "Excluir esta empresa", "CNPJ provável",
                       "Enviar ao suporte", "Tribunais selecionados", "\"Aplicar\"", "Usar a consulta pública do CNJ quando o caderno falhar"):
            self.assertIn(trecho, m, trecho)
        self.assertNotIn("Limpar o banco agora", m)
        self.assertNotIn("Ler pela consulta pública quando o caderno do CNJ cair", m)

    def test_termos_nao_mudam(self):
        with open(os.path.join(_RAIZ_, "paginas", "aceite.html"), encoding="utf-8") as f:
            self.assertNotIn("0.7.50", f.read())


if __name__ == "__main__":
    unittest.main()
