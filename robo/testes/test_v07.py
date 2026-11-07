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
        self.assertTrue(ok and os.path.isdir(os.path.join(pasta, "LexSuiteONE")))
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
        self.assertEqual((len(d["app"]["tribunais"]), d["app"]["ramos"][0], d["app"]["config"]["pasta"], d["app"]["atualizacao"]["chave"]), (59, "Trabalhista", "", False))
        status, d = self.pedir("GET", "/pastas")
        self.assertIn("candidatas", d)
        status, r = self.pedir("POST", "/testar-pasta", {"pasta": "/nao/existe"})
        self.assertFalse(r["ok"])
        compartilhada = tempfile.mkdtemp()
        status, r = self.pedir("POST", "/config", {"escritorio": "  KR Law  ", "pasta": compartilhada})
        self.assertTrue(r["ok"], r)
        self.assertTrue(os.path.exists(os.path.join(compartilhada, "LexSuiteONE", preferencias.NOME_ARQUIVO)))
        status, d = self.pedir("GET", "/dados")
        self.assertEqual((d["app"]["config"]["escritorio"], d["app"]["config"]["pasta_ok"], bool(d["app"]["config"]["planilha"]), d["app"]["config"]["agendavel"]), ("KR Law", True, True, os.name == "nt"))
        self.assertEqual(d["prefs"]["controle"]["ativo"], True)
        status, r = self.pedir("POST", "/atualizar", {})
        self.assertFalse(r["disponivel"]) and self.assertIn("chave", r["motivo"])
        status, r = self.pedir("POST", "/config", {"pasta": "/nao/existe"})
        self.assertFalse(r["ok"])
