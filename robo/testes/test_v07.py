"""Testes da v0.7: planilha de controle, exclusões, atualização assinada e planilha compartilhada."""

import datetime as dt
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexsuite import assinatura, atualizar, banco as bd, compartilhar, planilha, preferencias, radar, saude  # noqa: E402
from lexsuite.atualizar import mensagem_assinada  # noqa: E402

ROBO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Preferencias(unittest.TestCase):
    def test_cria_le_bloqueia_e_aplica(self):
        pasta = tempfile.mkdtemp()
        cfg = {"compartilhar": {"pasta": pasta, "subpasta": "LexSuiteONE"}, "radar": {"tribunais": ["TRT2"]}}
        base = compartilhar.pasta_base(cfg)
        caminho = compartilhar.criar_se_faltar(cfg, "0.7.1", "", lambda *_: None)
        self.assertTrue(os.path.exists(caminho))
        tamanho = os.path.getsize(caminho)
        compartilhar.criar_se_faltar(cfg, "0.7.1", "", lambda *_: None)  # nunca sobrescreve
        self.assertEqual(os.path.getsize(caminho), tamanho)
        p = preferencias.carregar(base)
        self.assertEqual((p["valor_minimo"], p["minimo_acoes"], p["esconder_excluidas"], p["controle"]["ativo"]), (100000, 1, True, True))
        self.assertEqual(p["exclusoes"], [])  # a linha de exemplo não conta
        self.assertEqual(preferencias.bloqueio(p, "0.7.0"), "")
        # o escritório edita: exclui um cliente, pede mínimo de 2 ações e o suporte desliga com validade vencida
        planilha.escrever_xlsx(preferencias.caminho(base), [
            {"nome": "Radar", "linhas": [["Hora"]]},
            {"nome": "Preferências", "linhas": [["Ajuste", "Valor", "x"], ["Valor mínimo da causa (R$)", "R$ 150.000,00", ""],
                                                 ["Mínimo de ações da mesma empresa", 2, ""], ["Esconder jurídico próprio provável", "sim", ""]]},
            {"nome": "Exclusões", "linhas": [["Nome ou CNPJ", "Motivo"], ["Transportadora Exemplo LTDA", "cliente atual"], ["11.222.333/0001-81", ""]]},
            {"nome": "Controle", "linhas": [["Chave", "Valor"], ["ativo", "sim"], ["validade", "2020-01-01"], ["versao_minima", "0.9.0"], ["mensagem", "Fale com o suporte."]], "oculta": True},
        ])
        p = preferencias.carregar(base)
        self.assertEqual((p["valor_minimo"], p["minimo_acoes"], p["esconder_gigantes"]), (150000, 2, True))
        self.assertIn("validade terminou em 2020-01-01", preferencias.bloqueio(p, "0.7.0", dt.date(2026, 11, 12)))
        p["controle"]["validade"] = ""
        self.assertIn("0.9.0", preferencias.bloqueio(p, "0.7.0"))
        p["controle"]["versao_minima"] = ""
        self.assertEqual(preferencias.bloqueio(p, "0.7.0"), "")
        itens = [{"empresas": ["TRANSPORTADORA EXEMPLO LTDA"], "empresa": {}}, {"empresas": ["OUTRA S.A."], "empresa": {"cnpj": "11222333000181"}},
                 {"empresas": ["TERCEIRA LTDA"], "empresa": {}}, {"empresas": ["QUARTA LTDA"], "empresa": {}}]
        preferencias.aplicar(itens, p, {"TERCEIRA": 3, "QUARTA": 1})
        self.assertEqual([i["excluida"] for i in itens], ["Exclusão: cliente atual", "Exclusão: CNPJ na lista", "", "Menos de 2 ações em 30 dias"])


class Atualizacao(unittest.TestCase):
    def _robo_falso(self):
        pasta = tempfile.mkdtemp()
        os.makedirs(os.path.join(pasta, "lexsuite"))
        with open(os.path.join(pasta, "lexsuite_robo.py"), "w") as f:
            f.write("VELHO\n")
        with open(os.path.join(pasta, "lexsuite", "radar.py"), "w") as f:
            f.write("VELHO\n")
        with open(os.path.join(pasta, "config.json"), "w") as f:
            f.write("{}")
        return pasta

    def _pacote(self, pasta_atu, versao, privada, conteudo=b"NOVO\n", extra=None, sha_errado=False):
        nome = f"LEXSUITE-ONE-ROBO-{versao}.zip"
        caminho = os.path.join(pasta_atu, nome)
        with zipfile.ZipFile(caminho, "w") as z:
            z.writestr("lexsuite_robo.py", conteudo)
            z.writestr("lexsuite/radar.py", conteudo)
            z.writestr("LEIA-ME.md", "doc")
            if extra:
                z.writestr(extra, "x")
        with open(caminho, "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        sha_m = ("0" * 64) if sha_errado else sha
        m = {"versao": versao, "arquivo": nome, "sha256": sha_m, "assinatura": assinatura.assinar(mensagem_assinada(versao, sha_m), privada), "notas": "teste"}
        with open(os.path.join(pasta_atu, "versao.json"), "w", encoding="utf-8") as f:
            json.dump(m, f)
        return m

    def test_instala_so_pacote_assinado_e_permitido(self):
        robo = self._robo_falso()
        compartilhada = tempfile.mkdtemp()
        cfg = {"compartilhar": {"pasta": compartilhada, "subpasta": "LexSuiteONE"}, "atualizacao": {"url": ""}}
        pasta_atu = compartilhar.pasta_atualizacao(cfg)
        os.makedirs(pasta_atu)
        privada, publica = assinatura.gerar_chaves()
        recados = []
        # sem chave pública no robô: desligado
        r = atualizar.atualizar(robo, cfg, "0.7.0", recados.append)
        self.assertFalse(r["disponivel"]) and self.assertIn("chave_publica", r["motivo"])
        with open(os.path.join(robo, "chave_publica.txt"), "w") as f:
            f.write(publica + "\n")
        # versão igual: nada a fazer
        self._pacote(pasta_atu, "0.7.0", privada)
        self.assertFalse(atualizar.atualizar(robo, cfg, "0.7.0", recados.append)["disponivel"])
        # assinada por outra chave: recusada
        outra, _ = assinatura.gerar_chaves()
        self._pacote(pasta_atu, "0.7.1", outra)
        r = atualizar.atualizar(robo, cfg, "0.7.0", recados.append)
        self.assertFalse(r["ok"]) and self.assertIn("assinatura", r["motivo"])
        # conteúdo não bate com o manifesto: recusada
        self._pacote(pasta_atu, "0.7.1", privada, sha_errado=True)
        self.assertFalse(atualizar.atualizar(robo, cfg, "0.7.0", recados.append)["ok"])
        # arquivo proibido (fora da lista): recusada e nada muda
        self._pacote(pasta_atu, "0.7.1", privada, extra="lexsuite/x.dll")
        r = atualizar.atualizar(robo, cfg, "0.7.0", recados.append)
        self.assertFalse(r["ok"])
        self.assertEqual(open(os.path.join(robo, "lexsuite_robo.py")).read(), "VELHO\n")
        self._pacote(pasta_atu, "0.7.1", privada, extra="../fora.py")
        self.assertFalse(atualizar.atualizar(robo, cfg, "0.7.0", recados.append)["ok"])
        # pacote bom: instala, guarda o anterior, não toca no config.json
        self._pacote(pasta_atu, "0.7.1", privada)
        r = atualizar.atualizar(robo, cfg, "0.7.0", recados.append)
        self.assertTrue(r["ok"] and r["arquivos"] == 3, r)
        self.assertEqual(open(os.path.join(robo, "lexsuite", "radar.py")).read(), "NOVO\n")
        self.assertEqual(open(os.path.join(robo, "_anterior", "v0.7.0", "lexsuite_robo.py")).read(), "VELHO\n")
        self.assertEqual(open(os.path.join(robo, "config.json")).read(), "{}")
        self.assertTrue(os.path.exists(os.path.join(robo, "ultima_atualizacao.json")))

    def test_publicar_gera_pacote_que_o_robo_aceita(self):
        import runpy
        pasta = tempfile.mkdtemp()
        privada, publica = assinatura.gerar_chaves()
        with open(os.path.join(pasta, "chave_privada.txt"), "w") as f:
            f.write(privada)
        saida_antes = os.path.join(ROBO, "publicar", "9.9.9")
        try:
            sys.argv = ["publicar.py", "empacotar", "--versao", "9.9.9", "--chave", os.path.join(pasta, "chave_privada.txt"), "--robo", ROBO]
            import io, contextlib
            with contextlib.redirect_stdout(io.StringIO()):
                runpy.run_path(os.path.join(ROBO, "ferramentas", "publicar.py"), run_name="__main__")
            m = json.load(open(os.path.join(saida_antes, "versao.json"), encoding="utf-8"))
            info = {"manifesto": m, "zip_caminho": os.path.join(saida_antes, m["arquivo"]), "origem": "teste"}
            ok, motivo = atualizar.verificar(info, publica)
            self.assertTrue(ok, motivo)
            nomes = zipfile.ZipFile(info["zip_caminho"]).namelist()
            self.assertIn("lexsuite_robo.py", nomes) and self.assertIn("lexsuite/radar.py", nomes)
            self.assertFalse(any(n.startswith("testes") or n.endswith(".db") or n == "config.json" for n in nomes))
        finally:
            shutil.rmtree(saida_antes, ignore_errors=True)


class Compartilhada(unittest.TestCase):
    def test_testar_e_gravar_planilha(self):
        ok, msg = compartilhar.testar("/caminho/que/nao/existe")
        self.assertFalse(ok)
        pasta = tempfile.mkdtemp()
        ok, msg = compartilhar.testar(pasta)
        self.assertTrue(ok)
        self.assertFalse(os.path.isdir(os.path.join(pasta, "LexSuiteONE")))  # 0.7.10: só testar não deixa pasta vazia
        banco = bd.Banco(os.path.join(pasta, "t.db"))
        banco.registrar("radar", {"versao": "0.7.0", "tribunais": ["TRT2"], "lidas": 10, "novas": 2, "com_cnpj": 1, "duracao": 3, "resultado": "ok", "erro": ""})
        banco.registrar("saude", {"fonte": "DJEN", "situacao": "ok", "detalhe": "10 publicações"})
        cfg = {"escritorio": "Escritório Teste", "radar": {"tribunais": ["TRT2"]}, "compartilhar": {"pasta": pasta, "subpasta": "LexSuiteONE", "planilha": True}}
        pagina = {"itens": [{"id": "1", "hora": "19:00", "visto_em": "", "tribunal": "TRT2", "vara": "V", "processo": "1", "rito": "Ordinário", "distribuida_em": "2026-11-05",
                             "empresas": ["X LTDA"], "empresa": {"cnpj": "", "porte_legivel": "", "capital_social": 0, "atividade": "", "municipio": "", "uf": "", "telefone": "", "email": "", "socios": []},
                             "setor": "", "gigante": False, "valor_causa": None, "valor_fonte": "", "link_djen": "", "link_pje": "", "excluida": "Exclusão: cliente"}]}
        caminho = compartilhar.gravar_radar(cfg, pagina, banco, "0.7.0", radar.COLUNAS_RADAR, radar.linha_csv, "abcd", "", lambda *_: None)
        doc = planilha.ler_xlsx(caminho)
        nomes = [(a["nome"], a["oculta"]) for a in doc["abas"]]
        self.assertEqual(nomes, [("Radar", False), ("Contatos", False), ("Preferências", False), ("Exclusões", False), ("Controle", True), ("Como usar", False), ("Histórico de leituras", False), ("Saúde", True), ("Sobre", True)])
        self.assertIn("regravada", doc["abas"][0]["linhas"][0][0])  # 0.7.14: linha de aviso no topo; cabeçalho na 2
        col = doc["abas"][0]["linhas"][1].index("Excluída (motivo)")
        self.assertEqual(doc["abas"][0]["linhas"][2][col], "Exclusão: cliente")
        log = doc["abas"][6]["linhas"]  # 0.7.13: Log visível; a rodada antiga aparece como "resumo da rodada"
        self.assertTrue(any(l[1] == "resumo da rodada" and "10 publicações" in str(l[6]) for l in log[1:]))
        self.assertIn(["Escritório", "Escritório Teste"], doc["abas"][8]["linhas"])
        # o escritório edita Exclusões; a próxima regravação preserva
        abas = [{"nome": a["nome"], "linhas": a["linhas"], "oculta": a["oculta"]} for a in doc["abas"]]
        abas[3]["linhas"] = [["Nome ou CNPJ", "Motivo"], ["Cliente Preservado Ltda", "cliente"]]
        planilha.escrever_xlsx(caminho, abas)
        compartilhar.gravar_radar(cfg, pagina, banco, "0.7.0", radar.COLUNAS_RADAR, radar.linha_csv, "abcd", "", lambda *_: None)
        doc2 = planilha.ler_xlsx(caminho)
        self.assertEqual(doc2["abas"][3]["linhas"][1][0], "Cliente Preservado Ltda")
        self.assertEqual(preferencias.carregar(os.path.dirname(caminho))["exclusoes"][0]["nome"], "Cliente Preservado Ltda")
        # planilha corrompida (em uso): não regrava, não perde nada
        planilha.liberar_escrita(caminho)  # 0.7.21: a de consulta fica marcada somente leitura (usuário comum não grava)
        with open(caminho, "wb") as f:
            f.write(b"nao e um zip")
        self.assertEqual(compartilhar.gravar_radar(cfg, pagina, banco, "0.7.0", radar.COLUNAS_RADAR, radar.linha_csv, "", "", lambda *_: None), "")
        self.assertEqual(open(caminho, "rb").read(), b"nao e um zip")

    def test_planilha_visual(self):
        """0.7.12: cabeçalho azul-marinho, filtro em todas as colunas, valor em R$ e destaque acima do mínimo; abre no
        Excel e no Google Planilhas (o XML segue a ordem do padrão) e a leitura continua igual."""
        pasta = tempfile.mkdtemp()
        banco = bd.Banco(os.path.join(pasta, "t.db"))
        cfg = {"escritorio": "Escritório Teste", "compartilhar": {"pasta": pasta, "subpasta": "LexSuiteONE"}}
        emp = {"cnpj": "11222333000181", "porte_legivel": "Micro", "capital_social": 50000.0, "atividade": "", "municipio": "SAO PAULO", "uf": "SP", "telefone": "", "email": "", "socios": []}
        base = {"hora": "19:00", "visto_em": "", "tribunal": "TRT2", "vara": "V", "rito": "Ordinário", "distribuida_em": "2026-11-05", "empresas": ["X LTDA"],
                "empresa": emp, "setor": "", "gigante": False, "valor_fonte": "", "link_djen": "", "link_pje": ""}
        pagina = {"valor_minimo": 100000, "itens": [dict(base, id="1", processo="1", valor_causa=250000), dict(base, id="2", processo="2", valor_causa=30000),
                                                    dict(base, id="3", processo="3", valor_causa=None)]}
        caminho = compartilhar.gravar_radar(cfg, pagina, banco, "0.7.12", radar.COLUNAS_RADAR, radar.linha_csv, "", "", lambda *_: None)
        z = zipfile.ZipFile(caminho)
        folha = z.read("xl/worksheets/sheet1.xml").decode()
        estilos = z.read("xl/styles.xml").decode()
        wb = z.read("xl/workbook.xml").decode()
        ncol = len(radar.COLUNAS_RADAR) + 2
        ult = planilha._col(ncol - 1)
        self.assertIn(f'<autoFilter ref="A2:{ult}5"/>', folha)  # 0.7.14: aviso na linha 1, cabeçalho na 2
        self.assertLess(folha.index("</sheetData>"), folha.index("<autoFilter"))
        self.assertIn("_xlnm._FilterDatabase", wb)
        self.assertIn(f"'Radar'!$A$2:${ult}$5", wb)
        self.assertIn('<fileSharing readOnlyRecommended="1"/>', wb)
        self.assertNotIn("<sheetProtection", folha)  # sem proteção: o Excel não deixaria ordenar
        self.assertIn('<mergeCell ref="A1:', folha)
        self.assertLess(folha.index("<autoFilter"), folha.index("<mergeCells"))
        protegida = planilha._xml_aba({"nome": "P", "linhas": [["a"], ["b"]], "proteger": True, "filtro": True})  # a opção continua no gerador
        self.assertLess(protegida.index("<sheetProtection"), protegida.index("<autoFilter"))
        self.assertIn('FF0F1D33', estilos)
        self.assertIn('numFmtId="164"', estilos)
        self.assertIn('<cellXfs count="9">', estilos)  # 0.7.18: 8 = faixa verde da cópia de trabalho
        self.assertLess(estilos.index("<numFmts"), estilos.index("<fonts"))
        j = planilha._col([c for _, c in radar.COLUNAS_RADAR].index("valor_causa"))
        self.assertIn(f'<c r="{j}3" s="5"><v>250000</v></c>', folha)  # acima do mínimo: destacado
        self.assertIn(f'<c r="{j}4" s="4"><v>30000</v></c>', folha)   # abaixo: só o formato R$
        self.assertIn('<c r="A1" s="7"', folha)  # linha vermelha de aviso
        self.assertIn('<c r="A2" s="2"', folha)  # cabeçalho azul-marinho
        import xml.etree.ElementTree as ET
        for nome in z.namelist():
            if nome.endswith(".xml") or nome.endswith(".rels"):
                ET.fromstring(z.read(nome))  # todo XML é bem formado
        doc = planilha.ler_xlsx(caminho)
        self.assertEqual(doc["abas"][0]["linhas"][2][[c for _, c in radar.COLUNAS_RADAR].index("valor_causa")], 250000)
        como = [a for a in doc["abas"] if a["nome"] == "Como usar"][0]
        self.assertFalse(como["oculta"])
        self.assertTrue(any("Google" in " ".join(map(str, l)) for l in como["linhas"]))
        # aba sem "visual" continua como antes (cabeçalho em negrito, sem filtro)
        planilha.escrever_xlsx(os.path.join(pasta, "simples.xlsx"), [{"nome": "A", "linhas": [["x"], [1]]}])
        simples = zipfile.ZipFile(os.path.join(pasta, "simples.xlsx")).read("xl/worksheets/sheet1.xml").decode()
        self.assertIn('<c r="A1" s="1"', simples)
        self.assertNotIn("autoFilter", simples)

    def test_saude(self):
        pubs = [{"processo": "1", "texto": "x"}] * 100 + [{"processo": "", "texto": ""}] * 30
        a = saude.avaliar(pubs, [1] * 60, 10, 8, dt.date(2026, 11, 12))
        self.assertEqual([x["situacao"] for x in a], ["erro", "atenção", "erro"])
        a = saude.avaliar([], [], 0, 0, dt.date(2026, 11, 12))  # quinta-feira
        self.assertEqual(a[0]["situacao"], "atenção")


class AppV07(unittest.TestCase):
    def setUp(self):
        from lexsuite import app
        import threading
        self.pasta = tempfile.mkdtemp()
        shutil.copy(os.path.join(ROBO, "radar_modelo.html"), self.pasta)
        self.servidor = app.Servidor(("127.0.0.1", 0), self.pasta)
        threading.Thread(target=self.servidor.serve_forever, daemon=True).start()
        self.porta = self.servidor.server_address[1]

    def tearDown(self):
        self.servidor.shutdown()
        self.servidor.server_close()

    def pedir(self, metodo, caminho, corpo=None):
        import http.client
        c = http.client.HTTPConnection("127.0.0.1", self.porta, timeout=10)
        c.request(metodo, caminho, body=json.dumps(corpo) if corpo is not None else None, headers={"Content-Type": "application/json", "X-LexSuite": "1"})
        r = c.getresponse()
        dados = json.loads(r.read())
        c.close()
        return r.status, dados

    def test_configuracao_pasta_e_atualizacao(self):
        status, d = self.pedir("GET", "/dados")
        self.assertEqual((len(d["app"]["tribunais"]), d["app"]["ramos"][0], d["app"]["config"]["pasta"], d["app"]["atualizacao"]["chave"]), (24, "Trabalhista", "", False))
        status, d = self.pedir("GET", "/pastas")
        self.assertIn("candidatas", d)
        status, r = self.pedir("POST", "/testar-pasta", {"pasta": "/nao/existe"})
        self.assertFalse(r["ok"])
        compartilhada = tempfile.mkdtemp()
        status, r = self.pedir("POST", "/config", {"escritorio": "  KR Law  ", "pasta": compartilhada})
        self.assertTrue(r["ok"], r)
        # 0.7.10: instalação nova usa "<produto> - planilha" (não confunde com a pasta do programa, C:\\LexSuiteONE)
        self.assertTrue(os.path.exists(os.path.join(compartilhada, "RADAR JUDICIAL - planilha", preferencias.NOME_ARQUIVO)))
        status, d = self.pedir("GET", "/dados")
        self.assertEqual((d["app"]["config"]["escritorio"], d["app"]["config"]["pasta_ok"], bool(d["app"]["config"]["planilha"]), d["app"]["config"]["agendavel"]), ("KR Law", True, True, os.name == "nt"))
        self.assertEqual(d["prefs"]["controle"]["ativo"], True)
        status, r = self.pedir("POST", "/atualizar", {})
        self.assertFalse(r["disponivel"]) and self.assertIn("chave", r["motivo"])
        status, r = self.pedir("POST", "/config", {"pasta": "/nao/existe"})
        self.assertFalse(r["ok"])
        # quem já tinha pasta continua com a subpasta dela, mesmo trocando de pasta
        outra = tempfile.mkdtemp()
        status, r = self.pedir("POST", "/config", {"pasta": outra})
        self.assertTrue(os.path.isdir(os.path.join(outra, "RADAR JUDICIAL - planilha")), r)


class Pasta0710(AppV07.__bases__[0]):
    """0.7.10: pasta escolhida que não existe é criada com "criar"; só Google Drive na lista; função "Outra"."""

    def setUp(self):
        AppV07.setUp(self)

    def tearDown(self):
        AppV07.tearDown(self)

    pedir = AppV07.pedir

    def test_criar_pasta_e_listar(self):
        nova = os.path.join(tempfile.mkdtemp(), "testeradar")
        status, r = self.pedir("POST", "/testar-pasta", {"pasta": nova})
        self.assertEqual((r["ok"], r["nao_existe"]), (False, True))
        status, r = self.pedir("POST", "/testar-pasta", {"pasta": nova, "criar": True})
        self.assertTrue(r["ok"], r)
        self.assertIn("RADAR JUDICIAL - planilha", r["mensagem"])
        nova2 = os.path.join(tempfile.mkdtemp(), "outra")
        status, r = self.pedir("POST", "/config", {"pasta": nova2})
        self.assertEqual((r["ok"], r.get("nao_existe")), (False, True))
        status, r = self.pedir("POST", "/config", {"pasta": nova2, "criar": True})
        self.assertTrue(r["ok"], r)
        status, d = self.pedir("GET", "/pastas")
        self.assertTrue(all(("drive" in p.lower()) for p in d["candidatas"]), d)
        self.assertEqual(d["pasta_programa"], self.pasta)
        from lexsuite import compartilhar
        self.assertTrue(compartilhar.no_google_drive(r"G:\My Drive\x"))
        self.assertTrue(compartilhar.no_google_drive("/Users/a/Google Drive/Meu Drive"))
        self.assertFalse(compartilhar.no_google_drive(r"c:\testeradar"))

    def test_funcao_outra_e_prefiro_nao(self):
        status, r = self.pedir("POST", "/config", {"papel": "Outra", "papel_outro": " Sócio-<b>diretor</b> "})
        status, d = self.pedir("GET", "/dados")
        self.assertEqual(d["app"]["usuario"]["papel"], "Sócio-bdiretor/b")
        status, r = self.pedir("POST", "/config", {"papel": "Prefiro não informar"})
        status, d = self.pedir("GET", "/dados")
        self.assertEqual(d["app"]["usuario"]["papel"], "Prefiro não informar")


class DiasUteis0710(unittest.TestCase):
    def test_domingo_e_segunda_leem_a_sexta(self):
        from lexsuite.monitor import dias_uteis
        sexta, sab, dom, seg = (dt.date(2026, 11, d) for d in (6, 7, 8, 9))
        self.assertEqual(dias_uteis(sab, 1), [sexta])
        self.assertEqual(dias_uteis(dom, 1), [sexta])
        self.assertEqual(dias_uteis(seg, 1), [sexta, seg])
        self.assertEqual(dias_uteis(seg, 0), [seg])
        self.assertEqual(dias_uteis(dt.date(2026, 11, 10), 3), [dt.date(2026, 11, 5), sexta, seg, dt.date(2026, 11, 10)])


class SegurancaV071(unittest.TestCase):
    def test_csv_nao_vira_formula(self):
        from lexsuite import saidas
        pasta = tempfile.mkdtemp()
        caminho = os.path.join(pasta, "x.csv")
        saidas.gravar_csv(caminho, [{"a": "=HYPERLINK(\"http://x\")", "b": ["+1", "ok"], "c": -5.5}], [("A", "a"), ("B", "b"), ("C", "c")])
        texto = open(caminho, encoding="utf-8-sig").read()
        self.assertIn("'=HYPERLINK", texto)
        self.assertIn("'+1 | ok", texto)
        self.assertIn("-5,50", texto)  # número negativo continua número

    def test_retencao(self):
        banco = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db"))
        banco.guardar_lead({"processo": "1", "empresas": ["X"]}, "2020-01-01")
        banco.guardar_lead({"processo": "2", "empresas": ["Y"]}, dt.date.today().isoformat())
        banco.con.execute("UPDATE leads SET dados = ? WHERE processo = '1'", ('{"processo": "1", "empresas": ["X"], "texto_curto": "nome do reclamante"}',))
        self.assertEqual(banco.limpar_antigos(365), 1)
        # 0.7.13: a ação velha não some; o dado completo vira resumo (sem o trecho do Diário) e as estatísticas ficam
        leads = {l["processo"]: l for l in banco.todos_leads()}
        self.assertEqual(sorted(leads), ["1", "2"])
        self.assertTrue(leads["1"]["resumido"] and "texto_curto" not in leads["1"])
        self.assertFalse(leads["2"]["resumido"])
        self.assertEqual(banco.limpar_antigos(0), 0)

    def test_mostrar_socios_desligado(self):
        banco = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db"))
        banco.guardar_lead({"processo": "1", "tribunal": "TRT2", "empresas": ["X LTDA"], "visto_em": "2026-11-07T19:00:00",
                            "empresa_receita": {"cnpj": "11222333000181", "socios": [{"nome": "PESSOA", "qualificacao": "Sócio"}]}}, dt.date.today().isoformat())
        prefs = preferencias.padrao(); prefs["mostrar_socios"] = False
        pagina = radar.montar_radar({"radar": {"tribunais": ["TRT2"]}}, banco, prefs=prefs)
        self.assertEqual(pagina["itens"][0]["empresa"]["socios"], [])
        prefs["mostrar_socios"] = True
        self.assertEqual(len(radar.montar_radar({"radar": {"tribunais": ["TRT2"]}}, banco, prefs=prefs)["itens"][0]["empresa"]["socios"]), 1)


class HostLocal(AppV07):
    def test_host_estranho_recusado(self):
        import http.client
        c = http.client.HTTPConnection("127.0.0.1", self.porta, timeout=10)
        c.request("GET", "/dados", headers={"Host": "site-malicioso.com:" + str(self.porta)})
        r = c.getresponse(); r.read(); c.close()
        self.assertEqual(r.status, 403)
        status, d = self.pedir("GET", "/dados")
        self.assertEqual(status, 200)


class Wizard(AppV07):
    def test_nome_papel_e_manual_personalizado(self):
        status, d = self.pedir("GET", "/dados")
        self.assertEqual((d["app"]["usuario"]["nome"], len(d["app"]["papeis"])), ("", 4))
        shutil.copy(os.path.join(ROBO, "MANUAL-DO-ESCRITORIO.html"), self.pasta)
        status, r = self.pedir("POST", "/config", {"nome": " Leandro ", "papel": "Advogado ou advogada", "escritorio": "KR Law", "pasta": ""})
        self.assertTrue(r["ok"], r)
        status, d = self.pedir("GET", "/dados")
        self.assertEqual((d["app"]["usuario"]["nome"], d["app"]["usuario"]["papel"]), ("Leandro", "Advogado ou advogada"))
        import http.client
        c = http.client.HTTPConnection("127.0.0.1", self.porta, timeout=10)
        c.request("GET", "/manual"); r = c.getresponse(); html = r.read().decode("utf-8"); c.close()
        self.assertEqual(r.status, 200)
        self.assertNotIn("Leandro", html); self.assertNotIn("KR Law", html)  # teste do dono (0.7.30): manual genérico, sem nome
        self.assertIn("Para você, advogado ou advogada", html)
        self.assertNotIn("<!--OLA-->", html)
        # papel inválido não entra; nome com HTML é escapado no manual
        status, r = self.pedir("POST", "/config", {"nome": "<b>x</b>", "papel": "Chefe"})
        status, d = self.pedir("GET", "/dados")
        self.assertEqual(d["app"]["usuario"]["papel"], "")
        c = http.client.HTTPConnection("127.0.0.1", self.porta, timeout=10)
        c.request("GET", "/manual"); html = c.getresponse().read().decode("utf-8"); c.close()
        self.assertNotIn("<b>x</b>", html); self.assertNotIn("&lt;b&gt;x", html)

    def test_perfil_manda_a_funcao_vazia_e_a_tela_tem_o_perfil(self):
        # 0.7.9: o perfil muda um dado por vez; tirar a função também precisa chegar à licença na nuvem.
        from lexsuite import conta
        chamadas = []
        original = conta.cadastrar
        def falso(cfg, versao, email, nome, doc, papel="", pedir=None, doc_tipo="cnpj", aceite_uso=None):
            chamadas.append({"email": email, "nome": nome, "papel": papel})
            cfg["usuario"].update({"email": email, "nome": nome, "papel": papel})
            return True, ""
        conta.cadastrar = falso
        try:
            self.pedir("POST", "/config", {"nome": "Ana", "papel": "Advogado ou advogada"})
            status, r = self.pedir("POST", "/config", {"papel": "", "email": "ana@example.com"})
            self.assertTrue(r["ok"], r)
            self.assertEqual(chamadas[-1], {"email": "ana@example.com", "nome": "Ana", "papel": ""})
            status, r = self.pedir("POST", "/config", {"nome": "Ana Souza", "email": "ana@example.com"})
            self.assertEqual(chamadas[-1]["nome"], "Ana Souza")
        finally:
            conta.cadastrar = original
        with open(os.path.join(ROBO, "radar_modelo.html"), encoding="utf-8") as f:
            tela = f.read()
        for marca in ('id="b-perfil"', 'id="pf-lista"', "troca_aviso", "guardarCampo"):
            self.assertIn(marca, tela)
        for antigo in ('id="c-nome"', 'id="c-email"', 'id="ola"'):
            self.assertNotIn(antigo, tela)


class Agenda079(unittest.TestCase):
    """0.7.9: horários da leitura automática escolhidos pela pessoa (dono, 08/Nov)."""

    def test_validar_e_descrever(self):
        from lexsuite import agendar
        self.assertEqual(agendar.validar(None), ["20:00", "08:00"])
        self.assertEqual(agendar.validar(["8:05", "20:00", "20:00", "25:00", "x", " 07:30 "]), ["07:30", "08:05", "20:00"])
        self.assertEqual(len(agendar.validar([f"{h:02d}:00" for h in range(10)])), agendar.MAXIMO)
        self.assertEqual(agendar.validar_dias("fim"), "todos")
        self.assertEqual(agendar.descricao(["20:00", "08:00"]), "todo dia às 08h00 e 20h00")
        self.assertEqual(agendar.descricao(["21:30"], "uteis"), "de segunda a sexta às 21h30")
        self.assertTrue(agendar.tem_noite(["08:00", "19:30"]))
        self.assertFalse(agendar.tem_noite(["08:00", "12:00"]))

    def test_proxima(self):
        from lexsuite import agendar
        sexta = dt.datetime(2026, 11, 13, 21, 0)
        self.assertEqual(agendar.proxima(["20:00", "08:00"], "todos", sexta), dt.datetime(2026, 11, 14, 8, 0))
        self.assertEqual(agendar.proxima(["20:00", "08:00"], "uteis", sexta), dt.datetime(2026, 11, 16, 8, 0))
        self.assertEqual(agendar.proxima(["20:00"], "todos", dt.datetime(2026, 11, 13, 19, 59)), dt.datetime(2026, 11, 13, 20, 0))

    def test_xml_compensa_horario_perdido(self):
        from lexsuite import agendar
        import xml.etree.ElementTree as ET
        ns = {"t": "http://schemas.microsoft.com/windows/2004/02/mit/task"}
        x = agendar.xml_tarefa(r"C:\Lex & Cia\RODAR.bat", ["20:00", "08:00"], "uteis", dt.date(2026, 11, 8))
        raiz = ET.fromstring(x.split("\n", 1)[1])
        gat = raiz.findall("t:Triggers/t:CalendarTrigger", ns)
        self.assertEqual([g.find("t:StartBoundary", ns).text for g in gat], ["2026-11-08T08:00:00", "2026-11-08T20:00:00"])
        self.assertEqual(len(gat[0].findall("t:ScheduleByWeek/t:DaysOfWeek/*", ns)), 5)
        self.assertEqual(raiz.find("t:Settings/t:StartWhenAvailable", ns).text, "true")
        self.assertEqual(raiz.find("t:Settings/t:DisallowStartIfOnBatteries", ns).text, "false")
        self.assertEqual(raiz.find("t:Actions/t:Exec/t:Command", ns).text, r"C:\Lex & Cia\RODAR.bat")
        self.assertEqual(raiz.find("t:Actions/t:Exec/t:Arguments", ns).text, "--agendado")
        todos = ET.fromstring(agendar.xml_tarefa("C:\\L\\RODAR.bat", ["20:00"], "todos").split("\n", 1)[1])
        self.assertIsNotNone(todos.find("t:Triggers/t:CalendarTrigger/t:ScheduleByDay", ns))

    def test_aviso_e_fora_do_windows(self):
        from lexsuite import agendar
        self.assertIn("12 ações novas", agendar.texto_aviso({"novas": 12}, "RADAR"))
        self.assertIn("1 ação nova", agendar.texto_aviso({"novas": 1}))
        self.assertIn("nenhuma ação nova", agendar.texto_aviso({}))
        if os.name != "nt":
            self.assertFalse(agendar.notificar("t", "x"))
            self.assertEqual(agendar.agendar("/tmp")[0], False)
            self.assertEqual(agendar.migrar_antigas("/tmp", {}), "")


class AgendaTela079(AppV07):
    def test_config_guarda_horarios_e_dados_mostram(self):
        status, d = self.pedir("GET", "/dados")
        c = d["app"]["config"]
        self.assertEqual((c["horarios"], c["dias"], c["avisar_ao_terminar"], c["tem_noite"]), (["08:00", "20:00"], "uteis", True, True))  # 0.7.32 (dono): padrão de segunda a sexta
        status, r = self.pedir("POST", "/config", {"horarios": ["07:30", "21:00", "lixo"], "dias": "uteis", "avisar_ao_terminar": False})
        self.assertTrue(r["ok"], r)
        status, d = self.pedir("GET", "/dados")
        c = d["app"]["config"]
        self.assertEqual((c["horarios"], c["dias"], c["avisar_ao_terminar"]), (["07:30", "21:00"], "uteis", False))
        with open(os.path.join(ROBO, "radar_modelo.html"), encoding="utf-8") as f:
            tela = f.read()
        for marca in ('id="c-horas"', 'id="c-hora-nova"', 'id="c-dias"', 'id="c-avisar"', "ag_noite", "quandoProxima"):
            self.assertIn(marca, tela)


class V0711(unittest.TestCase):
    """0.7.11: dias com Diário (feriado), uma tela só por computador, aviso de versão nova."""

    def test_feriado_nao_esvazia_a_leitura(self):
        from lexsuite import monitor, djen, banco as bd
        pedidos = []
        def meta(sigla, data, aviso=print, motivos=None):
            pedidos.append(data)
            return None if data in ("2026-11-09", "2026-11-06") else {"versao": "1"}  # segunda e sexta sem Diário
        orig_meta, orig_baixar = djen.meta_caderno, djen.baixar_caderno
        djen.meta_caderno, djen.baixar_caderno = meta, (lambda *a, **k: [{"processo": a[1]}])
        try:
            b = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db"))
            pubs = monitor.coletar_caderno(["TRT2"], 1, b, aviso=lambda *_: None, hoje=dt.date(2026, 11, 10))
        finally:
            djen.meta_caderno, djen.baixar_caderno = orig_meta, orig_baixar
        # terça: lê terça (se houver) e o último dia útil anterior que teve Diário: quinta (pula segunda e sexta)
        self.assertEqual(sorted(p["processo"] for p in pubs), ["2026-11-05", "2026-11-10"])
        self.assertNotIn("2026-11-04", pedidos)

    def test_uma_tela_so_e_versao_nova(self):
        from lexsuite import app
        import threading
        pasta = tempfile.mkdtemp()
        shutil.copy(os.path.join(ROBO, "radar_modelo.html"), pasta)
        srv = app.Servidor(("127.0.0.1", 0), pasta)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            porta = srv.server_address[1]
            self.assertEqual(app.procurar_aberto([porta]), f"http://127.0.0.1:{porta}/")
            import http.client
            c = http.client.HTTPConnection("127.0.0.1", porta, timeout=10)
            c.request("GET", "/versao-nova", headers={"X-LexSuite": "1"})
            d = json.loads(c.getresponse().read()); c.close()
            self.assertEqual((d["disponivel"], d["atual"]), (False, app.VERSAO))  # sem chave_publica.txt: não oferece
        finally:
            srv.shutdown(); srv.server_close()
        self.assertEqual(app.procurar_aberto([porta]), "")


class Progresso0711(unittest.TestCase):
    def test_porcentagem_pelos_passos(self):
        from lexsuite import app
        e = app.Estado()
        e.comecar()
        e.aviso("Radar: lista de distribuição de TRT2, TRT15 (últimos 1 dia(s) úteis)")
        self.assertEqual(e.como_dict()["progresso"], 5)
        e.aviso("  Baixando o caderno TRT2 06/11 (pode levar alguns minutos)...")
        self.assertEqual(e.como_dict()["progresso"], 32)
        e.aviso("  Caderno TRT15 06/11: já conferido (versão 1)")
        self.assertEqual(e.como_dict()["progresso"], 60)
        e.aviso("Receita: 18 de 36")
        self.assertEqual(e.como_dict()["progresso"], 77)
        e.terminar({"pt": "ok"})
        self.assertEqual(e.como_dict()["progresso"], 100)


class Dados0711(unittest.TestCase):
    def test_intimacao_e_cnpj_de_outra_parte(self):
        from lexsuite import classificar as c
        self.assertEqual(c.limpar_nome("Polyexcel Industria e Comercio de Compostos Polimericos Ltda Intimação"), "Polyexcel Industria e Comercio de Compostos Polimericos Ltda")
        self.assertEqual(c.limpar_nome("Li Importes Ltda Notificação"), "Li Importes Ltda")
        self.assertTrue(c.nomes_batem("AUDITESTE CONSULTORIA LTDA", "Auditeste Consultoria Ltda"))
        self.assertTrue(c.nomes_batem("NPE NIPLAN SERVICE LTDA", "Npe Niplan Service Ltda - ME"))
        self.assertFalse(c.nomes_batem("RODRIGO APARECIDO DOS REIS 123", "Auditeste Consultoria Ltda"))
        self.assertFalse(c.nomes_batem("ALFA COMERCIO E SERVICOS LTDA", "Beta Comercio e Servicos Ltda"))
        for x, y in (("Alfa Auto Pecas Ltda", "Beta Auto Pecas Ltda"), ("Mercadinho Sao Jose", "Padaria Sao Jose"),
                     ("Silva Transportes Ltda", "Silva Engenharia Ltda"), ("Restaurante Sabor", "Sabor Brasil Alimentos"),
                     ("Unimed Paulistana Sociedade Cooperativa", "Unimed Rio"), ("SOL", "CONSOLE LTDA")):
            self.assertFalse(c.nomes_batem(x, y), (x, y))
        self.assertTrue(c.nomes_batem("X COMERCIO DE ALIMENTOS LTDA", "X Alimentos Ltda"))
        lead = {"processo": "1", "empresas": ["Auditeste Consultoria Ltda Intimação"], "cnpjs": ["11222333000181"],
                "empresa_receita": {"cnpj": "11222333000181", "razao_social": "RODRIGO APARECIDO DOS REIS 12345678900"}}
        it = radar.item_de_lead(lead, {})
        self.assertEqual((it["empresa"]["cnpj"], it["cnpj_a_conferir"], it["empresas"]), ("", "11222333000181", ["Auditeste Consultoria Ltda"]))
        lead["empresa_receita"]["razao_social"] = "AUDITESTE CONSULTORIA LTDA"
        it = radar.item_de_lead(lead, {})
        self.assertEqual((it["empresa"]["cnpj"], it["cnpj_a_conferir"]), ("11222333000181", ""))


class PlanilhaAberta0711(unittest.TestCase):
    def test_aviso_quando_o_excel_trava(self):
        from lexsuite import compartilhar
        banco = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db"))
        recados = []
        orig = compartilhar.gravar_radar
        def trava(*a, **k):
            raise PermissionError("arquivo em uso")
        compartilhar.gravar_radar = trava
        try:
            cfg = {"compartilhar": {"pasta": tempfile.mkdtemp()}}  # 0.7.16: sem pasta, nem tenta gravar
            self.assertFalse(radar.gravar_planilha(cfg, {"itens": []}, banco, "0.7.11", tempfile.mkdtemp(), recados.append))
        finally:
            compartilhar.gravar_radar = orig
        self.assertIn("aberta no Excel", " ".join(recados))


class V0713(unittest.TestCase):
    """0.7.13: o 403 "só a partir das 03:00" não é erro; um tribunal com problema não derruba os outros; mensagens
    claras em PT e EN; histórico de leituras com a causa de cada tentativa."""
    TEXTO_3H = '{"erro":"Os cadernos do dia atual s\\u00f3 podem ser acessados a partir das 03:00."}'

    def _coletar(self, resposta, tribunais=("TRT15",), hoje=dt.date(2026, 11, 9)):
        from lexsuite import monitor, djen, rede, banco as bd
        orig_pedir, orig_baixar = rede.pedir_json, djen.baixar_caderno
        rede.pedir_json = resposta
        djen.baixar_caderno = lambda *a, **k: [{"processo": a[0] + " " + a[1]}]
        tentativas = []
        try:
            b = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db"))
            pubs = monitor.coletar_caderno(list(tribunais), 1, b, aviso=lambda *_: None, hoje=hoje, tentativas=tentativas)
        finally:
            rede.pedir_json, djen.baixar_caderno = orig_pedir, orig_baixar
        return pubs, tentativas

    def test_403_das_3h_nao_e_erro(self):
        from lexsuite import rede
        hoje = "2026-11-09"
        def resposta(url, **kw):
            if hoje in url:
                raise rede.ErroHTTP(403, url, self.TEXTO_3H)
            return {"versao": "1", "url": "https://x"}
        pubs, tent = self._coletar(resposta)
        self.assertEqual([p["processo"] for p in pubs], ["TRT15 2026-11-06"])  # pulou segunda 00h e leu sexta
        self.assertEqual(tent[0]["causa"], "ainda_nao_liberado_3h")
        self.assertEqual(tent[0]["http"], "403")
        self.assertIn("pulou hoje", tent[0]["fez"])
        self.assertIn("06/NOV", tent[0]["fez"])  # 0.7.28: mês em letras

    def test_outros_403_e_bloqueio_continuam_erro(self):
        from lexsuite import rede, causas
        def fora(url, **kw):
            raise rede.BloqueadoForaDoBrasil("fora")
        with self.assertRaises(rede.BloqueadoForaDoBrasil):
            self._coletar(fora)
        def proibido(url, **kw):
            raise rede.ErroHTTP(403, url, '{"erro":"acesso negado"}')
        with self.assertRaises(rede.ErroHTTP):
            self._coletar(proibido)
        self.assertEqual(causas.classificar(rede.ErroHTTP(403, "u", "acesso negado")), "erro_do_programa")
        self.assertEqual(causas.classificar(rede.BloqueadoForaDoBrasil("x")), "bloqueio_fora_do_brasil")

    def test_governo_fora_nao_derruba_os_outros(self):
        from lexsuite import rede, causas
        def resposta(url, **kw):
            if "TRT2/" in url:
                raise rede.ErroHTTP(503, url, "Service Unavailable")
            return {"versao": "1", "url": "https://x"}
        pubs, tent = self._coletar(resposta, tribunais=("TRT2", "TRT15"), hoje=dt.date(2026, 11, 10))
        self.assertTrue(pubs and all(p["processo"].startswith("TRT15") for p in pubs))
        causas_ = {t["tribunal"]: t["causa"] for t in tent}
        self.assertEqual(causas_, {"TRT2": "governo_fora", "TRT15": "ok"})
        self.assertEqual(causas.classificar(rede.SemResposta("u", "timed out")), "governo_fora")
        self.assertEqual(causas.classificar(rede.SemResposta("u", "[Errno 11001] getaddrinfo failed")), "sem_internet")
        self.assertEqual(causas.classificar(rede.ErroHTTP(429, "u", "")), "governo_fora")
        def tudo_fora(url, **kw):
            raise rede.ErroHTTP(503, url, "")
        with self.assertRaises(rede.ErroHTTP):  # nenhum tribunal pôde ser lido: aí sim a rodada para
            self._coletar(tudo_fora, tribunais=("TRT2", "TRT15"))

    def test_historico_grava_a_causa(self):
        from lexsuite import radar, banco as bd
        b = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db"))
        radar.registrar_tentativas(b, [{"tribunal": "TRT15", "dias_pedidos": "2026-11-09", "http": "403", "causa": "ainda_nao_liberado_3h",
                                        "fez": "pulou hoje (só às 3h); leu até 06/11", "duracao": 1.2, "leu_ate": "06/11", "detalhe": ""}],
                                   "botão", "0.7.13", quando="2026-11-09T00:05:27-03:00")
        h = b.execucoes("tentativa")
        self.assertEqual(h[0]["causa"], "ainda_nao_liberado_3h")
        self.assertEqual(h[0]["origem"], "botão")
        self.assertEqual(h[0]["quando_local"], "2026-11-09T00:05:27-03:00")
        self.assertNotIn("processo", h[0])

    def test_mensagens_claras_em_pt_e_en(self):
        from lexsuite import causas, app
        for c in causas.CAUSAS[1:]:
            pt, en = causas.mensagem(c, "pt"), causas.mensagem(c, "en")
            self.assertTrue(pt and en and pt != en, c)
            for ruim in ("RuntimeError", "HTTP", "\\u00", "https://"):
                self.assertNotIn(ruim, pt + en, c)
        self.assertIn("3h", causas.mensagem("ainda_nao_liberado_3h", "pt"))
        self.assertIn("3 a.m.", causas.mensagem("ainda_nao_liberado_3h", "en"))
        self.assertIn("Não é problema do seu computador", causas.mensagem("governo_fora", "pt"))
        e = app.Estado(eco=None)
        e.comecar()
        e.terminar(erro="x", info={"causa": "governo_fora", "pt": "a", "en": "b", "detalhe": "HTTP 503"})
        self.assertEqual(e.como_dict()["erro_info"]["causa"], "governo_fora")



class V0714(unittest.TestCase):
    """0.7.14: situação no banco (lote, desfazer, migração), Arquivo, retorno de totais, contatos, cópia da planilha,
    frente. Dados fictícios."""

    def _banco(self):
        from lexsuite import banco as bd
        b = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db"))
        for k, trib in enumerate(["TRT2", "TRT15", "TRT15"]):
            b.guardar_lead({"processo": f"000{k}-11.2026.5.02.0001", "tribunal": trib, "vara": "1ª Vara", "empresas": [f"Empresa Fictícia {k} Ltda"],
                            "data_publicacao": "2026-11-06", "valor_causa": [None, 30000, 250000][k], "classe": "ATOrd"}, "2026-11-06")
        return b

    def test_situacao_lote_e_desfazer(self):
        from lexsuite import banco as bd
        b = self._banco()
        procs = ["0000-11.2026.5.02.0001", "0001-11.2026.5.02.0001"]
        r = b.mudar_situacao(procs, "arquivado", perfil="ana@example.com", motivo="sem interesse")
        self.assertEqual(r["quantos"], 2)
        self.assertEqual(set(r["antes"].values()), {"novo"})
        sit = {l["processo"]: l["status"] for l in b.todos_leads()}
        self.assertEqual(sit[procs[0]], "arquivado")
        self.assertEqual(b.acoes(1)[0]["quantos"], 2)  # quem, quando e quantos ficam registrados
        self.assertEqual(b.desfazer_situacao(r["antes"]), 2)
        self.assertEqual({l["status"] for l in b.todos_leads()}, {"novo"})
        with self.assertRaises(ValueError):
            b.mudar_situacao(procs, "qualquer")
        self.assertEqual(bd.situacao_valida("Em contato"), "em_contato")  # situações antigas viram as chaves novas
        self.assertEqual(bd.situacao_valida("Virou cliente"), "virou_cliente")

    def test_lista_esconde_arquivado_e_arquivo_mostra_tudo(self):
        from lexsuite import radar
        b = self._banco()
        b.mudar_situacao(["0002-11.2026.5.02.0001"], "arquivado")
        cfg = {"radar": {"tribunais": ["TRT15"], "dias_na_pagina": 30}}
        agora = dt.datetime(2026, 11, 9, 9, 0)
        lista = radar.montar_radar(cfg, b, agora=agora, prefs={}, dias=30)
        arquivo = radar.montar_radar(cfg, b, agora=agora, prefs={}, dias=30, visao="arquivo")
        self.assertEqual([i["processo"] for i in lista["itens"]], ["0001-11.2026.5.02.0001"])  # só TRT15 e não arquivado
        self.assertEqual(len(arquivo["itens"]), 3)  # TRT2 (desmarcado) e o arquivado continuam no Arquivo
        self.assertEqual({i["situacao"] for i in arquivo["itens"]}, {"novo", "arquivado"})
        self.assertEqual(lista["itens"][0]["frente"], "trabalhista")

    def test_retorno_so_quantidades(self):
        b = self._banco()
        b.mudar_situacao(["0001-11.2026.5.02.0001"], "virou_cliente")
        tabela = b.retorno(dias=3650)
        self.assertTrue(tabela)
        for linha in tabela:
            self.assertEqual(set(linha), {"data", "tribunal", "frente", "faixa_valor", "situacao", "qtd"})
            self.assertNotIn("Empresa", json.dumps(linha))
        self.assertIn("virou_cliente", {l["situacao"] for l in tabela})

    def test_retorno_vai_na_conferencia(self):
        from lexsuite import conta
        enviado = {}
        def pedir(url, corpo, **k):
            enviado.update(corpo)
            return {"ok": True, "retorno": {"gravadas": 1, "recusadas": 0}}
        cfg = {"conta": {"codigo": "LEX-7K4M-2PQ9", "instalacao": "0123456789abcdef"}}
        c = conta.verificar(cfg, "0.7.14", dt.date(2026, 11, 9), pedir=pedir,
                            retorno=[{"data": "2026-11-06", "tribunal": "TRT15", "frente": "trabalhista", "faixa_valor": "sem", "situacao": "novo", "qtd": 2}])
        self.assertEqual(enviado["retorno"][0]["qtd"], 2)
        self.assertEqual(c["retorno_resposta"]["gravadas"], 1)

    def test_contatos_colar_valida_linha_a_linha(self):
        from lexsuite import contatos
        empresas = {"0001-11.2026.5.02.0001": "Empresa Fictícia 1 Ltda"}
        texto = """| processo | empresa | canal | valor | de_pessoa | fonte | data | observação |
|---|---|---|---|---|---|---|---|
| 0001-11.2026.5.02.0001 | Empresa Fictícia 1 Ltda | telefone | (19) 3333-4444 | não | PJe petição inicial | 2026-11-09 | |
| 0001-11.2026.5.02.0001 | Empresa Fictícia 1 Ltda | e-mail | contato@ficticia.example | sim | PJe citação | 2026-11-09 | sócio |
| 0001-11.2026.5.02.0001 | Empresa Fictícia 1 Ltda | outro | CPF 123.456.789-09 | sim | outro | 2026-11-09 | |
| 0001-11.2026.5.02.0001 | Empresa Fictícia 1 Ltda | telefone | (19) 99999-0000 | sim | PJe petição inicial | 2026-11-09 | do reclamante |
| 9999-11.2026.5.02.0001 | Outra | telefone | (11) 3333-4444 | não | outro | 2026-11-09 | |
| 0001-11.2026.5.02.0001 | Empresa Fictícia 1 Ltda | fax | 123 | não | outro | 2026-11-09 | |"""
        aceitas, recusadas = contatos.colar(texto, empresas, hoje=dt.date(2026, 11, 9))
        self.assertEqual([a["canal"] for a in aceitas], ["telefone", "email"])
        self.assertTrue(aceitas[1]["de_pessoa"])
        motivos = " | ".join(r["motivo"] for r in recusadas)
        self.assertEqual(len(recusadas), 4)
        for trecho in ("CPF", "reclamante", "não está na sua lista", "canal desconhecido"):
            self.assertIn(trecho, motivos)

    def test_contatos_preparar_respeita_o_limite(self):
        from lexsuite import contatos
        itens = [{"processo": f"{k:04d}-11.2026.5.02.0001", "tribunal": "TRT15", "vara": "V", "empresa": {"razao_social": f"Empresa Fictícia {k}", "cnpj": ""},
                  "contato": {"tem": k == 0}} for k in range(50)]
        caminho, n = contatos.preparar(itens, tempfile.mkdtemp(), limite=30, hoje=dt.date(2026, 11, 9))
        self.assertEqual(n, 30)
        texto = open(caminho, encoding="utf-8").read()
        self.assertIn("Nunca** anote CPF", texto)
        self.assertNotIn("0000-11.2026", texto)  # quem já tem contato não entra

    def test_copia_da_planilha_sem_protecao(self):
        from lexsuite import compartilhar, radar, banco as bd
        pasta = tempfile.mkdtemp()
        b = self._banco()
        cfg = {"escritorio": "Escritório Teste", "compartilhar": {"pasta": pasta, "subpasta": "LexSuiteONE"}}
        pagina = radar.montar_radar({"radar": {"tribunais": ["TRT15"]}}, b, agora=dt.datetime(2026, 11, 9), prefs={}, dias=30)
        caminho = compartilhar.gravar_radar(cfg, pagina, b, "0.7.14", radar.COLUNAS_RADAR, radar.linha_csv, "", "", lambda *_: None, arquivo=[])
        self.assertIn("readOnlyRecommended", zipfile.ZipFile(caminho).read("xl/workbook.xml").decode())
        ok, copia = compartilhar.gerar_copia(cfg, agora=dt.datetime(2026, 11, 9, 10, 30))
        self.assertTrue(ok, copia)
        z = zipfile.ZipFile(copia)
        self.assertNotIn("sheetProtection", z.read("xl/worksheets/sheet1.xml").decode())
        self.assertNotIn("readOnlyRecommended", z.read("xl/workbook.xml").decode())
        self.assertIn("Cópia de trabalho gerada em 09/NOV/2026 às 10:30", z.read("xl/worksheets/sheet1.xml").decode())  # 0.7.18: texto e faixa verde
        self.assertIn("Cópias", copia)
        import stat
        self.assertIn("Este arquivo é do escritório Escritório Teste", z.read("xl/worksheets/sheet1.xml").decode())  # 0.7.21
        cfg_ruim = dict(cfg, escritorio="Escritório\x0b Ruim\x00\ufffe\uffff\ud800 & Cia <Ltda> 123")  # 0.7.21 (revisão): controle some, XML válido
        ok2, copia2 = compartilhar.gerar_copia(cfg_ruim, agora=dt.datetime(2026, 11, 9, 10, 31))
        self.assertTrue(ok2, copia2)
        import xml.dom.minidom
        xml.dom.minidom.parseString(zipfile.ZipFile(copia2).read("xl/worksheets/sheet1.xml"))
        self.assertFalse(os.stat(caminho).st_mode & stat.S_IWRITE)  # 0.7.21: a de consulta fica marcada "somente leitura"
        self.assertTrue(os.stat(copia).st_mode & stat.S_IWRITE)  # a cópia de trabalho, não
        compartilhar.gravar_radar(cfg, pagina, b, "0.7.14", radar.COLUNAS_RADAR, radar.linha_csv, "", "", lambda *_: None, arquivo=[])  # regrava
        self.assertFalse(os.stat(caminho).st_mode & stat.S_IWRITE)

    def test_frente_pela_regra(self):
        from lexsuite import frentes
        self.assertEqual(frentes.frente({"tribunal": "TRT15", "classe": "Execução Fiscal"}), "trabalhista")
        self.assertEqual(frentes.frente({"tribunal": "TJSP", "classe": "Execução Fiscal"}), "tributario")
        self.assertEqual(frentes.frente({"tribunal": "TJSP", "classe": "Recuperação Judicial"}), "empresarial")
        self.assertEqual(frentes.frente({"tribunal": "TJSP", "classe": "Procedimento Comum Cível"}), "civel")
        self.assertTrue(frentes.a_conferir({"tribunal": "TJSP", "classe": "Procedimento Comum Cível"}))


class V0714b(unittest.TestCase):
    """0.7.14 (ajustes da revisão da Operação): aceite dos termos, leitura agendada visível na tela, CPF sem pontuação,
    desfazer limpa o motivo, migração de um banco da 0.7.13, corte de 2.000 linhas no retorno. Dados fictícios."""

    def test_aceite_pendente(self):
        from lexsuite import conta
        cfg = {"conta": {"codigo": "LEX-7K4M-2PQ9", "instalacao": "0123456789abcdef"}}
        resp = {"ok": False, "motivo": "aceite_pendente", "mensagem": "Antes do primeiro uso, o responsável precisa aceitar os termos.",
                "aceite": {"aceito": False, "link": "https://judicial.solverone.com.br/aceite.html?codigo=LEX-7K4M-2PQ9"}}
        conta.verificar(cfg, "0.7.14", dt.date(2026, 11, 9), pedir=lambda u, c, **k: resp)
        sit = conta.situacao(cfg)
        self.assertFalse(sit["ok"])
        self.assertEqual(sit["texto"], "Falta aceitar os termos. Dúvidas: judicial@solverone.com.br.")  # teste do dono (0.7.30): curto, sem o link por extenso
        self.assertNotIn("http", sit["texto"] + sit["texto_en"]); self.assertEqual(sit["contato"], "judicial@solverone.com.br")
        self.assertTrue(sit["aceite_link"].startswith("https://judicial.solverone.com.br/"))
        resp["aceite"]["link"] = "https://exemplo-ruim.example/aceite"  # link de fora do site da SolverONE não vale
        conta.verificar(cfg, "0.7.14", dt.date(2026, 11, 9), pedir=lambda u, c, **k: resp)
        self.assertEqual(conta.situacao(cfg)["aceite_link"], "")
        ok = {"ok": True, "aceite": {"aceito": True, "versao": "1", "aceito_em": "2026-11-09T10:00:00Z", "nome": "Responsável Fictício"}}
        conta.verificar(cfg, "0.7.14", dt.date(2026, 11, 9), pedir=lambda u, c, **k: ok)
        self.assertTrue(conta.situacao(cfg)["ok"])
        self.assertTrue(conta.situacao(cfg)["aceite"]["aceito"])

    def test_leitura_em_outro_processo(self):
        from lexsuite import app
        pasta = tempfile.mkdtemp()
        arq = os.path.join(pasta, "saida", "leitura.json")
        e = app.Estado(eco=None, arquivo=arq, origem="agendamento")
        e.comecar()
        e.aviso("Radar: lista de distribuição de TRT2, TRT15 (últimos 1 dia(s) úteis)")
        d = json.load(open(arq, encoding="utf-8"))
        self.assertTrue(d["rodando"] and d["origem"] == "agendamento" and d["progresso"] >= 5)
        self.assertIsNone(app.leitura_em_outro_processo(arq))  # o próprio processo não conta
        d["pid"] = os.getppid()  # outro processo vivo (o pai deste teste)
        json.dump(d, open(arq, "w", encoding="utf-8"))
        self.assertIsNotNone(app.leitura_em_outro_processo(arq))
        d["pid"] = 999999999  # processo que não existe: leitura abandonada
        json.dump(d, open(arq, "w", encoding="utf-8"))
        self.assertIsNone(app.leitura_em_outro_processo(arq))
        e.terminar({"pt": "ok"})
        self.assertFalse(json.load(open(arq, encoding="utf-8"))["rodando"])

    def test_cpf_sem_pontuacao_recusado(self):
        from lexsuite import contatos
        emp = {"0001-11.2026.5.02.0001": "Empresa Fictícia 1 Ltda"}
        base = "| 0001-11.2026.5.02.0001 | Empresa Fictícia 1 Ltda | {c} | {v} | sim | PJe petição inicial | 2026-11-09 | {o} |"
        _, rec = contatos.colar(base.format(c="outro", v="documento 12345678909", o=""), emp)
        self.assertEqual(len(rec), 1)  # 123.456.789-09 sem pontuação é CPF válido: recusa
        ac, rec = contatos.colar(base.format(c="telefone", v="11987654321", o=""), emp)
        self.assertEqual((len(ac), len(rec)), (1, 0))  # celular com DDD no canal telefone passa
        ac, _ = contatos.colar(base.format(c="email", v="contato@ficticia.example", o="autorizada pela diretoria"), emp)
        self.assertEqual(len(ac), 1)  # "autorizada" não é "autor"

    def test_desfazer_limpa_motivo(self):
        from lexsuite import banco as bd
        b = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db"))
        b.guardar_lead({"processo": "1", "tribunal": "TRT2", "empresas": ["X Fictícia"]}, "2026-11-06")
        r = b.mudar_situacao(["1"], "descartado", motivo="sem interesse")
        b.desfazer_situacao(r["antes"])
        lead = b.todos_leads()[0]
        self.assertEqual((lead["status"], lead["motivo"]), ("novo", ""))

    def test_migracao_de_banco_da_0713(self):
        import sqlite3
        from lexsuite import banco as bd
        caminho = os.path.join(tempfile.mkdtemp(), "antigo.db")
        con = sqlite3.connect(caminho)
        con.execute("CREATE TABLE leads (processo TEXT PRIMARY KEY, primeira_vez TEXT, tribunal TEXT, vara TEXT, dados TEXT, status TEXT DEFAULT 'Novo')")
        for k, st in enumerate(["Novo", "Em contato", "Descartado", None, "visto"]):
            con.execute("INSERT INTO leads VALUES (?,?,?,?,?,?)", (str(k), "2026-11-0%d" % (k + 1), "TRT2", "V",
                        json.dumps({"processo": str(k), "data_publicacao": "2026-11-0%d" % (k + 1), "valor_causa": 150000}), st))
        con.execute("INSERT INTO leads VALUES ('quebrado', '2026-11-01', 'TRT2', 'V', 'não é json', 'Novo')")
        con.commit(); con.close()
        b = bd.Banco(caminho)
        st = {l[0]: l[1] for l in b.con.execute("SELECT processo, status FROM leads")}
        self.assertEqual([st[str(k)] for k in range(5)], ["novo", "em_contato", "descartado", "novo", "visto"])
        self.assertEqual(b.con.execute("SELECT faixa_valor FROM leads WHERE processo = '0'").fetchone()[0], "100k-300k")
        self.assertEqual(b.con.execute("PRAGMA user_version").fetchone()[0], 719)  # 0.7.19: reclassificação (corrigida) feita junto
        bd.Banco(caminho)  # abrir de novo não refaz nada nem dá erro

    def test_retorno_corta_em_2000(self):
        from lexsuite import banco as bd
        b = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db"))
        hoje = dt.date.today()
        for k in range(2100):
            d = (hoje - dt.timedelta(days=k % 50)).isoformat()
            b.guardar_lead({"processo": f"p{k}", "tribunal": f"TRT{k % 24 + 1}", "data_publicacao": d, "valor_causa": (k % 7) * 60000}, d)
        self.assertLessEqual(len(b.retorno(dias=60)), 2000)


class V0715(unittest.TestCase):
    """0.7.15: "Interromper" para num ponto seguro sem deixar nada pela metade; aviso do horário perdido."""

    def test_interromper_para_no_ponto_seguro(self):
        from lexsuite import monitor, djen, radar, banco as bd
        b = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db"))
        chamadas = []
        orig_meta, orig_baixar = djen.meta_caderno, djen.baixar_caderno
        djen.meta_caderno = lambda sigla, data, aviso=print, motivos=None: (chamadas.append((sigla, data)) or {"versao": "1"})
        djen.baixar_caderno = lambda *a, **k: [{"processo": a[0] + a[1]}]
        tent, lidos = [], []
        try:
            with self.assertRaises(radar.Interrompida):
                monitor.coletar_caderno(["TRT2", "TRT15"], 1, b, aviso=lambda *_: None, hoje=dt.date(2026, 11, 10),
                                        lidos=lidos, tentativas=tent, parar=lambda: len(chamadas) >= 2)
        finally:
            djen.meta_caderno, djen.baixar_caderno = orig_meta, orig_baixar
        self.assertEqual(len(chamadas), 2)  # parou antes do terceiro Diário
        self.assertEqual(tent[-1]["causa"], "interrompida")
        self.assertIsNone(b.versao_caderno("TRT2", "2026-11-10"))  # nada marcado como lido: a próxima leitura continua

    def test_estado_parar_vale_so_para_a_leitura_atual(self):
        from lexsuite import app
        pasta = tempfile.mkdtemp()
        e = app.Estado(eco=None, arquivo=os.path.join(pasta, "saida", "leitura.json"))
        self.assertFalse(e.parar())
        e.comecar()
        self.assertFalse(e.parar())
        with open(e.arquivo_parar(), "w", encoding="utf-8") as f:
            json.dump({"quando": dt.datetime.now().isoformat(timespec="seconds"), "quem": "ana@example.com"}, f)
        self.assertTrue(e.parar())
        e.terminar({"pt": "x"})
        e.comecar()  # leitura nova: o pedido antigo some
        self.assertFalse(e.parar())

    def test_horario_perdido(self):
        from lexsuite import agendar
        cfg = {"radar": {"horarios": ["08:00", "20:00"]}}
        self.assertEqual(agendar.horario_perdido(cfg, dt.datetime(2026, 11, 9, 9, 17)), "08:00")
        self.assertEqual(agendar.horario_perdido(cfg, dt.datetime(2026, 11, 9, 8, 5)), "")  # na hora: não é atraso
        self.assertEqual(agendar.horario_perdido(cfg, dt.datetime(2026, 11, 10, 7, 0)), "20:00")  # a de ontem à noite
        from lexsuite import causas
        self.assertTrue(causas.e_aviso("interrompida"))
        self.assertIn("lido na próxima leitura", causas.mensagem("interrompida"))
        # leitura das 20h já feita às 20h01: abrir às 22h não é "horário perdido"
        self.assertEqual(agendar.horario_perdido(cfg, dt.datetime(2026, 11, 9, 22, 0), ultima_leitura="2026-11-09T20:01:00"), "")
        self.assertEqual(agendar.horario_perdido(cfg, dt.datetime(2026, 11, 9, 22, 0), ultima_leitura="2026-11-09T08:02:00"), "20:00")


class V0715b(unittest.TestCase):
    def test_interromper_no_laco_da_receita_fecha_a_rodada(self):
        """Parada durante as consultas à Receita: o que já foi gravado entra na rodada, nas estatísticas e na planilha;
        os Diários não são marcados como lidos (a próxima leitura continua)."""
        from lexsuite import radar, monitor, conta, cnpj, banco as bd
        pasta = tempfile.mkdtemp()
        b = bd.Banco(os.path.join(pasta, "t.db"))
        novos = [{"processo": f"000{k}-11.2026.5.02.0001", "tribunal": "TRT2", "vara": "V", "empresas": [f"Empresa Fictícia {k} Ltda"],
                  "cnpjs": [], "data_publicacao": "2026-11-09", "fonte": "DJEN"} for k in range(5)]
        orig = (monitor.coletar_caderno, radar.acoes_do_dia, conta.verificar)
        def coletar(*a, **k):
            k["lidos"].append(("TRT2", "2026-11-09", "1"))
            return [{"x": 1}]
        monitor.coletar_caderno = coletar
        radar.acoes_do_dia = lambda pubs, ano, vistos: [dict(n) for n in novos]
        conta.verificar = lambda cfg, versao, hoje=None, pedir=None, retorno=None: cfg.setdefault("conta", {}).update({"ok": True, "resposta": "ok", "ultima_ok": hoje.isoformat(), "codigo": "LEX-7K4M-2PQ9"})
        cont = {"n": 0}
        def parar():
            cont["n"] += 1
            return cont["n"] > 3  # deixa gravar 3 ações e pede para parar
        try:
            with self.assertRaises(radar.Interrompida):
                radar.executar({"radar": {"tribunais": ["TRT2"]}, "conta": {"codigo": "LEX-7K4M-2PQ9"}}, b, lambda *_: None, pasta,
                               agora=dt.datetime(2026, 11, 9, 20, 0), parar=parar)
        finally:
            monitor.coletar_caderno, radar.acoes_do_dia, conta.verificar = orig
        self.assertEqual(len(b.todos_leads()), 3)
        self.assertEqual(b.rodadas()[0]["novas_acoes"], 3)  # a rodada parcial conta as 3 gravadas
        self.assertEqual(b.execucoes("radar", 1)[0]["resultado"], "interrompida")
        self.assertTrue(b.estatisticas())  # estatísticas atualizadas
        self.assertIsNone(b.versao_caderno("TRT2", "2026-11-09"))  # o Diário não ficou marcado como lido


class V0715c(AppV07):
    """Revisão da 0.7.15: /interromper não deixa o banco travado (outra conexão grava logo depois) e registra a ação."""

    def test_interromper_nao_trava_o_banco(self):
        from lexsuite import banco as bd
        bd.Banco(self.servidor.caminho_db).con.close()
        self.servidor.estado.comecar()
        status, r = self.pedir("POST", "/interromper", {})
        self.assertTrue(r["ok"])
        self.assertTrue(os.path.exists(os.path.join(self.pasta, "saida", "parar.json")))
        self.assertTrue(self.servidor.estado.parar())
        import sqlite3
        con = sqlite3.connect(self.servidor.caminho_db, timeout=0.5)
        con.execute("INSERT INTO acoes VALUES ('x','x','x','teste','','','',0)")  # daria "database is locked" antes
        con.commit()
        acoes = [a["acao"] for a in bd.Banco(self.servidor.caminho_db).acoes(10)]
        self.assertIn("interromper", acoes)
        con.close()
        self.servidor.estado.terminar({"pt": "x"})
        status, r = self.pedir("POST", "/interromper", {})
        self.assertFalse(r["ok"])  # sem leitura em andamento
