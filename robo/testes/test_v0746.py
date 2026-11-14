"""0.7.46 (dono, 14/Nov): Área logada v2 (desenho da Arquitetura, documentacao/DESENHO-AREA-LOGADA-V2-2026-11-14.md).
Lotes, limite por pedido, leitor de vários blocos e de arquivo (.md/.txt/.zip), pedido pendente que sobrevive a reiniciar,
memória por processo, fonte mais forte com histórico, relatório "o que mudou", filtro, selo e o interruptor por licença."""

import datetime as dt
import io
import json
import os
import re
import sys
import tempfile
import unittest
import zipfile

_ROBO_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RAIZ_ = os.path.dirname(_ROBO_)
sys.path.insert(0, _ROBO_)

from lexsuite import banco as bd, contatos as ct  # noqa: E402

with open(os.path.join(_ROBO_, "radar_modelo.html"), encoding="utf-8") as _f:
    HTML = _f.read()

A, B = "0001234-56.2026.5.09.0001", "0006543-21.2026.5.09.0002"
EMPRESAS = {A: "Empresa Fictícia A Ltda", B: "Empresa Fictícia B Ltda"}
CAB = "| processo | dado | valor | resultado | fonte | data | observação |\n|---|---|---|---|---|---|---|\n"


def simulada():
    """A resposta simulada da Arquitetura (documentacao/prototipos/area-logada/resposta-simulada-TESTE-0.7.45.md)."""
    with open(os.path.join(_RAIZ_, "documentacao", "prototipos", "area-logada", "resposta-simulada-TESTE-0.7.45.md"), encoding="utf-8") as f:
        t = f.read()
    return t.replace("AAAAAAA-AA.2026.5.09.0001", A).replace("BBBBBBB-BB.2026.5.09.0002", B)


class Pedido(unittest.TestCase):
    def test_48_processos_viram_2_lotes(self):
        itens = [{"processo": "%07d-11.2026.5.02.0001" % k, "tribunal": "TRT2", "empresas": ["Empresa %d" % k]} for k in range(48)]
        _, n, texto = ct.preparar_v1(itens, tempfile.mkdtemp(), limite=50)
        self.assertEqual(n, 48)
        self.assertEqual(ct.preparar_v1.ultimo["lotes"], 2)
        self.assertIn("## Processos · lote 1 de 2 (25 de 48)", texto)
        self.assertIn("## Processos · lote 2 de 2 (23 de 48)", texto)
        self.assertIn("RESPOSTA PARA O RADAR v1 · lote 1 de 2", texto)
        self.assertIn("termine um lote antes de começar o próximo", texto)

    def test_variante_por_tribunal(self):
        _, _, trt = ct.preparar_v1([{"processo": "1", "tribunal": "TRT15", "empresas": ["X"]}], tempfile.mkdtemp())
        _, _, tj = ct.preparar_v1([{"processo": "2", "tribunal": "TJSP", "empresas": ["Y"]}], tempfile.mkdtemp())
        self.assertIn("pjekz", trt); self.assertNotIn("outros tribunais; esta tela", trt)
        self.assertIn("outros tribunais; esta tela", tj); self.assertNotIn("pjekz", tj)
        for t in (trt, tj):
            for proibido in ("Baixar processo completo", "Meus Expedientes", "login.seam", "anotar CPF"):
                self.assertIn(proibido, t)

    def test_dados_escolhidos(self):
        self.assertEqual(ct.filtrar_falta(["valor_causa", "data_ajuizamento", "email"], {"valor": True, "data": False, "contato": False, "socio": True}),
                         ["valor_causa", "socio_contato"])
        self.assertEqual(ct.filtrar_falta(["email"], {"valor": True, "data": True, "contato": False, "socio": False}), [])

    def test_limite_por_pedido(self):
        from lexsuite import app
        self.assertEqual(app.limite_por_pedido({}), 25)
        self.assertEqual(app.limite_por_pedido({"area_logada_por_pedido": 80}), 50)
        self.assertEqual(app.limite_por_pedido({"area_logada_por_pedido": 10}), 10)


class Leitor(unittest.TestCase):
    def test_resposta_simulada_aceita_e_recusa_o_previsto(self):
        r = ct.ler_resposta(simulada(), EMPRESAS)
        self.assertTrue(r["achou"])
        self.assertEqual([(l["lote"], l["de"]) for l in r["lotes"]], [(1, 2), (2, 2)])
        self.assertTrue(r["lotes"][1]["extras"])  # coluna a mais: aceita o reconhecível
        motivos = " | ".join(x["motivo"] for x in r["recusadas"])
        self.assertEqual(len(r["recusadas"]), 6, motivos)
        for m in ("CPF", "autor, de testemunha", "porte", "não está na sua lista", "fora do formato", "talvez"):
            self.assertIn(m, motivos)
        self.assertEqual(r["repetidas"], 1)  # o e-mail repetido conta uma vez
        self.assertEqual(r["nao_consta"], [{"processo": A, "dado": "site"}])
        self.assertEqual(sorted(x["dado"] for x in r["tentar_depois"]), ["email", "telefone"])
        canais_a = sorted(c["canal"] for c in r["contatos"] if c["processo"] == A)
        self.assertEqual(canais_a, ["email", "endereco", "outro", "telefone"])
        end_b = [c for c in r["contatos"] if c["processo"] == B and c["canal"] == "endereco"][0]
        self.assertEqual(end_b["confianca"], "baixa")  # da petição, "a conferir"
        campos = {(c["processo"], c["campo"]): c["valor"] for c in r["completar"]}
        self.assertEqual(campos[(A, "valor_causa")], 1234567.89)
        self.assertEqual(campos[(A, "data_ajuizamento")], "2026-11-13")
        self.assertEqual(campos[(A, "uf")], "PR")
        self.assertEqual(campos[(B, "valor_causa")], 48250.5)

    def test_dois_blocos_em_ordem_trocada(self):
        t = ("conversa\nRESPOSTA PARA O RADAR v1 · lote 2 de 2\n" + CAB + f"| {B} | valor_causa | 100,00 | encontrado | PJe dados do processo | 2026-11-14 | |\n"
             "mais conversa 😊\n### RESPOSTA PARA O RADAR v1 · lote 1 de 2\n" + CAB + f"| {A} | valor_causa | 200,00 | encontrado | PJe dados do processo | 2026-11-14 | |\nfim")
        r = ct.ler_resposta(t, EMPRESAS)
        self.assertEqual([l["lote"] for l in r["lotes"]], [1, 2])
        self.assertEqual(sorted(c["valor"] for c in r["completar"]), [100.0, 200.0])

    def test_sem_bloco(self):
        r = ct.ler_resposta("Olá!\nNão consegui entrar no PJe.\nTente de novo.\nquarta linha", EMPRESAS)
        self.assertFalse(r["achou"])
        self.assertEqual(r["inicio"], ["Olá!", "Não consegui entrar no PJe.", "Tente de novo."])

    def test_zip_com_dois_md(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("resposta-radar-lote-2.md", "RESPOSTA PARA O RADAR v1 · lote 2 de 2\n" + CAB + f"| {B} | valor_causa | 10,00 | encontrado | PJe dados do processo | 2026-11-14 | |\n")
            z.writestr("pasta/resposta-radar-lote-1.md", "RESPOSTA PARA O RADAR v1 · lote 1 de 2\n" + CAB + f"| {A} | valor_causa | 20,00 | encontrado | PJe dados do processo | 2026-11-14 | |\n")
            z.writestr("leia.exe", b"MZ nada")  # ignorado: só .md e .txt são lidos
        texto = ct.ler_arquivo("respostas.zip", buf.getvalue())
        r = ct.ler_resposta(texto, EMPRESAS)
        self.assertEqual(len(r["lotes"]), 2)
        self.assertEqual(len(r["completar"]), 2)

    def test_zip_danificado_vira_aviso(self):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("lote.md", "RESPOSTA PARA O RADAR v1\n" + CAB * 50)
        dados = bytearray(buf.getvalue())
        meio = dados.index(b"lote.md") + 40
        dados[meio:meio + 20] = b"\x00" * 20  # estraga o conteúdo comprimido (CRC ou compressão)
        with self.assertRaises(ValueError):
            ct.ler_arquivo("lote.zip", bytes(dados))

    def test_arquivo_recusado(self):
        with self.assertRaises(ValueError):
            ct.ler_arquivo("planilha.xlsx", b"x")
        with self.assertRaises(ValueError):
            ct.ler_arquivo("vazio.zip", b"nao e zip")
        self.assertIn("Áção", ct.ler_arquivo("a.txt", "Áção".encode("cp1252")))


class Banco0746(unittest.TestCase):
    def setUp(self):
        self.db = os.path.join(tempfile.mkdtemp(), "lexsuite.db")
        b = bd.Banco(self.db)
        for p in (A, B):
            b.con.execute("INSERT INTO leads (processo, dados) VALUES (?, ?)", (p, json.dumps({"processo": p})))
        b.con.commit(); b.con.close()

    def test_pedido_pendente_sobrevive_a_reiniciar(self):
        b = bd.Banco(self.db)
        b.area_registrar_pedido("P1", {A: ["valor_causa", "email"], B: ["email"]}, 1, "pedido.md", "claude")
        b.con.close()
        b2 = bd.Banco(self.db)  # "fechou e abriu o programa"
        p = b2.area_pedido()
        self.assertEqual((p["id"], p["processos"], p["estado"]), ("P1", 2, "pendente"))
        self.assertEqual(b2.area_por_processo()[A]["estado"], "pedido")
        b2.area_registrar_resposta([{"processo": A, "dado": "email", "resultado": "encontrado", "fonte": "PJe dados do processo"},
                                    {"processo": B, "dado": "email", "resultado": "tentar_depois", "fonte": ""}], "P1", [1])
        self.assertEqual(b2.area_pedido("P1")["estado"], "respondido")
        self.assertIsNone(b2.area_pedido())
        est = b2.area_por_processo()
        self.assertEqual((est[A]["estado"], est[B]["estado"]), ("com_dados", "tentar"))
        self.assertTrue(b2.area_tem_resposta())

    def test_lotes_em_dias_diferentes(self):
        b = bd.Banco(self.db)
        b.area_registrar_pedido("P2", {A: ["email"], B: ["email"]}, 2, "pedido.md")
        b.area_registrar_resposta([{"processo": A, "dado": "email", "resultado": "nao_consta", "fonte": ""}], "P2", [1])
        self.assertEqual(b.area_pedido("P2")["estado"], "pendente")  # falta o lote 2
        b.area_registrar_resposta([{"processo": B, "dado": "email", "resultado": "nao_consta", "fonte": ""}], "P2", [2])
        self.assertEqual(b.area_pedido("P2")["estado"], "respondido")

    def test_cancelar_volta_a_ainda_nao_pedido(self):
        b = bd.Banco(self.db)
        b.area_registrar_pedido("P3", {A: ["email"]}, 1, "pedido.md")
        b.area_cancelar("P3")
        self.assertIsNone(b.area_pedido())
        self.assertNotIn(A, b.area_por_processo())

    def test_pedido_substituido_libera_os_que_ficaram_de_fora(self):
        b = bd.Banco(self.db)
        b.area_registrar_pedido("V1", {A: ["email"], B: ["email"]}, 1, "p1.md")
        b.area_registrar_pedido("V2", {A: ["email"]}, 1, "p2.md")  # B ficou de fora do pedido novo
        self.assertEqual(b.area_pedido("V1")["estado"], "substituido")
        self.assertNotIn(B, b.area_por_processo())  # volta a "ainda não pedido" (o modo "próximos" o pega de novo)
        self.assertEqual(b.area_por_processo()[A]["estado"], "pedido")

    def test_nada_depois_nao_apaga_o_achado(self):
        b = bd.Banco(self.db)
        b.area_registrar_resposta([{"processo": A, "dado": "email", "resultado": "encontrado", "fonte": "PJe dados do processo"}])
        b.area_registrar_resposta([{"processo": A, "dado": "email", "resultado": "nao_consta", "fonte": ""}])
        self.assertEqual(b.area_por_processo()[A]["estado"], "com_dados")

    def test_fonte_mais_forte_e_historico(self):
        b = bd.Banco(self.db)
        self.assertEqual(b.completar_fonte(A, "valor_causa", 1000, "PJe citação", "2026-11-10")[0], "acrescentado")
        self.assertEqual(b.completar_fonte(A, "valor_causa", 900, "Receita", "2026-11-14")[0], "mantido")  # mais fraca: fica
        self.assertEqual(b.completar_fonte(A, "valor_causa", 1000, "PJe dados do processo", "2026-11-14")[0], "igual")
        sit, antes, depois = b.completar_fonte(A, "valor_causa", 1500, "PJe dados do processo", "2026-11-14")
        self.assertEqual((sit, antes, depois), ("alterado", "1000", "1500"))
        dados = json.loads(b.con.execute("SELECT dados FROM leads WHERE processo = ?", (A,)).fetchone()[0])
        self.assertEqual(dados["manual"]["valor_causa"]["valor"], 1500)
        self.assertEqual([h["valor"] for h in dados["manual_historico"]], [1000])  # o anterior fica no histórico
        self.assertEqual(b.completar_fonte(A, "valor_causa", "", "PJe dados do processo")[0], "")  # nunca apaga


class Relatorio(unittest.TestCase):
    """A rota inteira (ler_resposta_area): aplica sem apagar e devolve o "o que mudou"."""

    def test_o_que_mudou(self):
        from lexsuite import app
        pasta = tempfile.mkdtemp()
        db = os.path.join(pasta, "lexsuite.db")
        b = bd.Banco(db)
        b.con.execute("INSERT INTO leads (processo, dados) VALUES (?, ?)", (A, json.dumps({"processo": A, "empresas": ["Empresa A"],
                      "empresa_receita": {"razao_social": "Empresa A", "email": "contato@empresa-a.com.br", "telefone": "(41) 3333-0000"}})))
        b.con.commit()
        b.area_registrar_pedido("R1", {A: ["valor_causa", "email", "telefone", "site"]}, 1, "p.md")
        b.con.close()

        class S:
            caminho_db = db
            def config(self):
                return {"usuario": {"email": "teste@exemplo.com.br"}, "radar": {}}
            def planilha_depois(self):
                pass
        t = ("RESPOSTA PARA O RADAR v1 · lote 1 de 1\n" + CAB +
             f"| {A} | valor_causa | 5000,00 | encontrado | PJe dados do processo | 2026-11-14 | |\n"
             f"| {A} | email | CONTATO@empresa-a.com.br | encontrado | PJe dados do processo | 2026-11-14 | |\n"
             f"| {A} | telefone | (41) 99999-0000 | encontrado | PJe petição inicial | 2026-11-14 | |\n"
             f"| {A} | site | | nao_consta | PJe petição inicial | 2026-11-14 | |\n")
        r = app.ler_resposta_area(S(), t, "resposta.md")
        self.assertTrue(r["ok"])
        m = r["mudou"][A]
        self.assertEqual([x["dado"] for x in m["acrescentado"]], ["valor_causa"])
        self.assertEqual([x["dado"] for x in m["igual"]], ["email"])  # o mesmo e-mail da Receita não duplica
        self.assertEqual([x["dado"] for x in m["alterado"]], ["telefone"])  # telefone novo entra junto, com antes → depois
        self.assertIn("Receita", m["alterado"][0]["antes"])
        self.assertEqual(r["resumo"]["com_dado_novo"], 1)
        self.assertEqual(r["achados"]["site"], [0, 1])
        b2 = bd.Banco(db)
        self.assertEqual(b2.area_pedido("R1")["estado"], "respondido")
        self.assertEqual(len([c for c in b2.contatos(A) if c["canal"] == "telefone"]), 1)
        nada = app.ler_resposta_area(S(), "só conversa, sem tabela", "")
        self.assertEqual((nada["ok"], nada["nao_achou"]), (False, True))


class Tela0746(unittest.TestCase):
    def test_tres_lugares_com_interruptor(self):
        self.assertIn('bp.setAttribute("data-recurso", "area-logada")', HTML)  # barra de lote
        self.assertIn('bl.setAttribute("data-recurso", "area-logada")', HTML)  # botão do cartão
        self.assertIn('[t("al_gerar"), function () { areaLogada(', HTML)  # menu, escondido pelo 4º campo quando desligado
        self.assertIn('false, !alLigado()]', HTML)
        self.assertIn('.recurso-off-area-logada [data-recurso="area-logada"] { display: none !important; }', HTML)
        self.assertIn('window.SolverRecursos.ligado("area-logada", true)', HTML)  # até a nuvem: tudo ligado

    def test_filtro_e_selo(self):
        self.assertIn('"empresa", "area"]', HTML)
        self.assertIn('(k === "area" && !(D && D.area_logada && D.area_logada.tem_resposta) && !sel.length)', HTML)  # só depois do 1º resultado
        self.assertIn('t("al_selo", { d: dataCurta(ar_.em, true) })', HTML)
        for k in ("al_f_nao:", "al_f_com_dados:", "al_f_nada:", "al_f_tentar:", "al_faixa:", "al_trazer:", "al_cancelar_pedido:"):
            self.assertEqual(HTML.count(k), 2, k)

    def test_defeitos_da_0745(self):
        self.assertIn('q.classList.add("balao-fixo")', HTML)  # (?) da barra de lote parado e dentro da tela
        self.assertIn("if (!j.open) {", HTML)  # janela trocada, não reaberta
        self.assertIn('var cx = el("textarea", "al-pedido")', HTML)  # a caixa com o pedido
        self.assertNotIn("(8 colunas)", HTML)
        self.assertNotIn('post("/contatos/preparar"', HTML)  # a rota antiga abria a pasta

    def test_versao_e_novidades(self):
        from lexsuite import VERSAO
        self.assertGreaterEqual(tuple(int(x) for x in VERSAO.split(".")), (0, 7, 46))  # a versão sobe
        bloco = HTML[HTML.index('"0.7.46": {'):HTML.index('"0.7.45": {')]
        pt = re.findall(r'"((?:[^"\\]|\\.)+)"', bloco[bloco.index("pt: ["):bloco.index("en: [")])
        en = re.findall(r'"((?:[^"\\]|\\.)+)"', bloco[bloco.index("en: ["):])
        self.assertEqual(len(pt), 7); self.assertEqual(len(en), 7)


if __name__ == "__main__":
    unittest.main()
