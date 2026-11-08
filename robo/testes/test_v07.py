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
        self.assertEqual(nomes, [("Radar", False), ("Preferências", False), ("Exclusões", False), ("Controle", True), ("Log", True), ("Saúde", True), ("Sobre", True)])
        col = doc["abas"][0]["linhas"][0].index("Excluída (motivo)")
        self.assertEqual(doc["abas"][0]["linhas"][1][col], "Exclusão: cliente")
        self.assertEqual(doc["abas"][4]["linhas"][1][3], 10)
        self.assertIn(["Escritório", "Escritório Teste"], doc["abas"][6]["linhas"])
        # o escritório edita Exclusões; a próxima regravação preserva
        abas = [{"nome": a["nome"], "linhas": a["linhas"], "oculta": a["oculta"]} for a in doc["abas"]]
        abas[2]["linhas"] = [["Nome ou CNPJ", "Motivo"], ["Cliente Preservado Ltda", "cliente"]]
        planilha.escrever_xlsx(caminho, abas)
        compartilhar.gravar_radar(cfg, pagina, banco, "0.7.0", radar.COLUNAS_RADAR, radar.linha_csv, "abcd", "", lambda *_: None)
        doc2 = planilha.ler_xlsx(caminho)
        self.assertEqual(doc2["abas"][2]["linhas"][1][0], "Cliente Preservado Ltda")
        self.assertEqual(preferencias.carregar(os.path.dirname(caminho))["exclusoes"][0]["nome"], "Cliente Preservado Ltda")
        # planilha corrompida (em uso): não regrava, não perde nada
        with open(caminho, "wb") as f:
            f.write(b"nao e um zip")
        self.assertEqual(compartilhar.gravar_radar(cfg, pagina, banco, "0.7.0", radar.COLUNAS_RADAR, radar.linha_csv, "", "", lambda *_: None), "")
        self.assertEqual(open(caminho, "rb").read(), b"nao e um zip")

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
        self.assertEqual(banco.limpar_antigos(365), 1)
        self.assertEqual([l["processo"] for l in banco.todos_leads()], ["2"])
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
        self.assertIn("Olá, Leandro. Este manual é do KR Law.", html)
        self.assertIn("Para você, advogado ou advogada", html)
        self.assertNotIn("<!--OLA-->", html)
        # papel inválido não entra; nome com HTML é escapado no manual
        status, r = self.pedir("POST", "/config", {"nome": "<b>x</b>", "papel": "Chefe"})
        status, d = self.pedir("GET", "/dados")
        self.assertEqual(d["app"]["usuario"]["papel"], "")
        c = http.client.HTTPConnection("127.0.0.1", self.porta, timeout=10)
        c.request("GET", "/manual"); html = c.getresponse().read().decode("utf-8"); c.close()
        self.assertIn("Olá, &lt;b&gt;x&lt;/b&gt;.", html)

    def test_perfil_manda_a_funcao_vazia_e_a_tela_tem_o_perfil(self):
        # 0.7.9: o perfil muda um dado por vez; tirar a função também precisa chegar à licença na nuvem.
        from lexsuite import conta
        chamadas = []
        original = conta.cadastrar
        def falso(cfg, versao, email, nome, doc, papel="", pedir=None, doc_tipo="cnpj"):
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
        self.assertEqual((c["horarios"], c["dias"], c["avisar_ao_terminar"], c["tem_noite"]), (["08:00", "20:00"], "todos", True, True))
        status, r = self.pedir("POST", "/config", {"horarios": ["07:30", "21:00", "lixo"], "dias": "uteis", "avisar_ao_terminar": False})
        self.assertTrue(r["ok"], r)
        status, d = self.pedir("GET", "/dados")
        c = d["app"]["config"]
        self.assertEqual((c["horarios"], c["dias"], c["avisar_ao_terminar"]), (["07:30", "21:00"], "uteis", False))
        with open(os.path.join(ROBO, "radar_modelo.html"), encoding="utf-8") as f:
            tela = f.read()
        for marca in ('id="c-horas"', 'id="c-hora-nova"', 'id="c-dias"', 'id="c-avisar"', "ag_noite", "quandoProxima"):
            self.assertIn(marca, tela)
