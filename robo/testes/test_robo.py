"""Testes das regras do robô (rodar: python -m unittest discover -s testes).

As publicações abaixo são FICTÍCIAS, no formato da API do DJEN, só para
conferir as regras: achar a empresa ré, descartar pessoa física, pontuar.
"""

import datetime as dt
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexsuite import avisar, banco as bd, classificar as cl, djen, monitor, prazos, radar  # noqa: E402

ITEM_DJEN = {
    "id": 991, "data_disponibilizacao": "2026-10-20", "siglaTribunal": "TRT2",
    "tipoComunicacao": "Intimação", "tipoDocumento": "Notificação",
    "nomeOrgao": "Vara do Trabalho de Cajamar", "nomeClasse": "AÇÃO TRABALHISTA - RITO ORDINÁRIO",
    "numeroprocessocommascara": "1004000-11.2026.5.02.0221", "link": "https://exemplo.invalido/doc",
    "texto": ("<p>PODER JUDICIÁRIO JUSTIÇA DO TRABALHO</p><p>ATOrd 1004000-11.2026.5.02.0221</p>"
              "<p>RECLAMANTE: FULANO DE TAL EXEMPLO</p><p>RECLAMADO: TRANSPORTADORA EXEMPLO LTDA</p>"
              "<p>RECLAMADO: ARMAZENS FICTICIOS S.A.</p><p>Fica V. Sa. notificado da audiência inicial "
              "designada. Valor da causa: R$ 152.300,45. CNPJ 11.222.333/0001-81</p>"),
    "destinatarios": [{"nome": "FULANO DE TAL EXEMPLO", "polo": "A"}],
    "destinatarioadvogados": [{"advogado": {"nome": "ADVOGADA EXEMPLO", "numero_oab": "1", "uf_oab": "SP"}}],
}


class TestRegras(unittest.TestCase):
    def test_empresa_ou_pessoa(self):
        self.assertTrue(cl.eh_empresa("TRANSPORTADORA EXEMPLO LTDA"))
        self.assertTrue(cl.eh_empresa("Armazéns Fictícios S.A."))
        self.assertFalse(cl.eh_empresa("FULANO DE TAL EXEMPLO"))

    def test_cnpj(self):
        self.assertTrue(cl.cnpj_valido("11.222.333/0001-81"))
        self.assertFalse(cl.cnpj_valido("11.222.333/0001-82"))

    def test_lead_a_partir_da_publicacao(self):
        pub = djen.normalizar(ITEM_DJEN)
        self.assertEqual(pub["processo"], "1004000-11.2026.5.02.0221")
        leads = djen.leads([pub], vara="Vara do Trabalho de Cajamar", ano_minimo=2026)
        self.assertEqual(len(leads), 1)
        lead = leads[0]
        self.assertEqual(lead["empresas"], ["TRANSPORTADORA EXEMPLO LTDA", "ARMAZENS FICTICIOS S.A."])
        self.assertEqual(lead["cnpjs"], ["11222333000181"])
        self.assertAlmostEqual(lead["valor_causa"], 152300.45)
        self.assertEqual(lead["rito"], "Ordinário")
        self.assertTrue(lead["sinal_de_acao_nova"])
        # a pessoa física (reclamante) não pode aparecer em nenhum campo que sai na planilha
        from lexsuite import saidas
        saida = saidas.lead_para_saida(lead)
        self.assertNotIn("FULANO", str(saida))

    def test_processo_antigo_nao_e_lead(self):
        item = dict(ITEM_DJEN, numeroprocessocommascara="1000500-22.2019.5.02.0221")
        leads = djen.leads([djen.normalizar(item)], ano_minimo=2026)
        self.assertEqual(leads, [])

    def test_nota(self):
        pub = djen.normalizar(ITEM_DJEN)
        lead = djen.leads([pub], ano_minimo=2026)[0]
        lead["porte"] = "DEMAIS"
        nota, motivos = cl.nota(lead)
        self.assertGreaterEqual(nota, 70)
        self.assertEqual(cl.faixa(nota), "Alta")
        self.assertTrue(any("terceirização" in m for m in motivos))

    def test_carteira(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
            f.write("cnpj;nome\n;Transportadora Exemplo\n")
        carteira = cl.ler_carteira(f.name)
        lead = djen.leads([djen.normalizar(ITEM_DJEN)], ano_minimo=2026)[0]
        lead["cliente"] = cl.cliente_da_carteira(lead, carteira)
        self.assertEqual(lead["cliente"], "Transportadora Exemplo")
        self.assertEqual(cl.nota(lead)[0], 100)
        os.unlink(f.name)


class TestMonitor(unittest.TestCase):
    ALVOS = {"oabs": [{"numero": "123456", "uf": "SP", "nome": "Advogada Exemplo"}],
             "processos": {}, "partes": {}, "cnpjs": {}}

    def test_prazo_com_feriado(self):
        # Disponibilizada qui 22/10/2026 → publicação sex 23/10 → começa seg 26/10; 02/11 (Finados) não conta.
        r = prazos.calcular("2026-10-22", 8)
        self.assertEqual((r["publicacao"], r["inicio_prazo"], r["vencimento"]), ("2026-10-23", "2026-10-26", "2026-11-05"))

    def test_prazo_no_recesso(self):
        # Sexta 18/12: recesso forense até 06/01 e prazos suspensos até 20/01 (CLT 775-A).
        r = prazos.calcular("2026-12-18")
        self.assertEqual(r["publicacao"], "2027-01-07")
        self.assertEqual(r["inicio_prazo"], "2027-01-21")

    def test_prazo_no_texto(self):
        self.assertEqual(prazos.prazo_no_texto("manifeste-se no prazo de 5 (cinco) dias"), 5)
        self.assertEqual(prazos.prazo_no_texto("Prazo de 8 (oito) dias para recurso"), 8)
        self.assertIsNone(prazos.prazo_no_texto("no prazo legal"))

    def test_oab_com_zero_a_esquerda(self):
        pub = djen.normalizar(dict(ITEM_DJEN, destinatarioadvogados=[
            {"advogado": {"nome": "ADVOGADA EXEMPLO", "numero_oab": "0123456", "uf_oab": "SP"}}]))
        motivos, _, _ = monitor.casar(pub, self.ALVOS)
        self.assertTrue(motivos and motivos[0].startswith("OAB 123456/SP"))

    def test_nao_avisa_duas_vezes(self):
        import tempfile
        caminho = os.path.join(tempfile.mkdtemp(), "t.db")
        banco = bd.Banco(caminho)
        pub = djen.normalizar(dict(ITEM_DJEN, destinatarioadvogados=[
            {"advogado": {"nome": "X", "numero_oab": "123456", "uf_oab": "SP"}}]))
        novas = monitor.filtrar_novas([pub, pub], self.ALVOS, banco)
        self.assertEqual(len(novas), 1)
        monitor.guardar(novas, banco)
        self.assertEqual(monitor.filtrar_novas([pub], self.ALVOS, banco), [])

    def test_tipo_do_ato(self):
        sentenca = djen.normalizar(dict(ITEM_DJEN, tipoDocumento="Sentença", texto="SENTENÇA. JULGO PROCEDENTE."))
        self.assertEqual(monitor.classificar_ato(sentenca), ("Sentença", "Urgente"))
        despacho = djen.normalizar(dict(ITEM_DJEN, tipoDocumento="Despacho",
                                        texto="DESPACHO. Manifeste-se no prazo de 5 (cinco) dias."))
        item = monitor.preparar(despacho, ["teste"], "", "")
        self.assertEqual((item["ato"], item["urgencia"]), ("Despacho", "Alta"))

    def test_cliente_da_carteira_no_monitor(self):
        alvos = dict(self.ALVOS, oabs=[], partes={cl.chave_nome("Transportadora Exemplo Ltda"): "Transportadora Exemplo Ltda"})
        motivos, cliente, _ = monitor.casar(djen.normalizar(ITEM_DJEN), alvos)
        self.assertEqual(cliente, "Transportadora Exemplo Ltda")
        self.assertTrue(motivos)

    def test_mesma_publicacao_por_caminhos_diferentes(self):
        a = djen.normalizar(dict(ITEM_DJEN, id=1))
        b = djen.normalizar(dict(ITEM_DJEN, id=2, numeroprocessocommascara="10040001120265020221"))
        self.assertEqual(monitor.chave(a), monitor.chave(b))

    def test_agrupar_telegram(self):
        msgs = avisar.agrupar(["x" * 1000] * 9)
        self.assertEqual(len(msgs), 3)
        self.assertTrue(all(len(m) <= 3800 for m in msgs))

    def test_mapa_orgaos_e_varas_alvo(self):
        import json
        import tempfile
        pub = djen.normalizar(dict(ITEM_DJEN, idOrgao=9001))
        self.assertEqual(djen.mapa_orgaos([pub]), {"Vara do Trabalho de Cajamar": "9001"})
        pasta = tempfile.mkdtemp()
        json.dump({"Vara do Trabalho de Cajamar": "9001"}, open(os.path.join(pasta, "orgaos_TRT2.json"), "w"))
        cfg = {"alvos": [{"tribunal": "trt2", "vara": "vara do trabalho de cajamar"}, {"tribunal": "TRT15", "vara": "X", "orgao_id": 7}]}
        v = monitor.varas_alvo(cfg, pasta)
        self.assertEqual((v[0]["tribunal"], v[0]["orgao_id"], v[1]["orgao_id"]), ("TRT2", "9001", "7"))

    def test_acoes_novas_sem_repetir_processo(self):
        item = dict(ITEM_DJEN, tipoComunicacao="Lista de distribuição")
        pubs = [djen.normalizar(item), djen.normalizar(dict(item, id=2))]
        varas = [{"tribunal": "TRT2", "vara": "Vara do Trabalho de Cajamar", "orgao_id": "1"}]
        novos = monitor.acoes_novas(pubs, varas, set(), 2026)
        self.assertEqual(len(novos), 1)
        self.assertTrue(novos[0]["sinal_de_acao_nova"])

    def test_sinais_e_setor(self):
        acoes = [{"empresas": ["LOGISTICA X LTDA"], "tribunal": "TRT2", "cliente": "LOGISTICA X LTDA", "acoes_no_periodo": 3},
                 {"empresas": ["LOGISTICA X LTDA", "RH Y LTDA"], "tribunal": "TRT15", "cliente": "", "acoes_no_periodo": 3}]
        monitor.sinais_das_acoes(acoes)
        self.assertEqual(acoes[0]["sinais"], ["Cliente da carteira", "3 processos no período", "Em 2 tribunais"])
        self.assertIn("Terceirização", acoes[1]["sinais"])
        self.assertEqual(acoes[0]["setor"], "Logística e transporte")

    def test_pagina_do_dia(self):
        import tempfile
        banco = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db"))
        item = dict(ITEM_DJEN, tipoComunicacao="Lista de distribuição")
        lead = djen.leads([djen.normalizar(item)], ano_minimo=2026)[0]
        lead["rodada"], lead["visto_em"] = "2026-10-22T19:15", "2026-10-22T19:15:00"
        banco.guardar_lead(lead, "2026-10-22")
        banco.registrar_rodada({"id": "2026-10-22T19:15", "quando": "2026-10-22T19:15", "modo": "api", "conferidas": 1, "novas_acoes": 1})
        cfg = {"alvos": [{"tribunal": "TRT2", "vara": "Vara do Trabalho de Cajamar"}]}
        import datetime as dt
        pag = monitor.montar_pagina(cfg, banco, 7, agora=dt.datetime(2026, 10, 23, 7, 0))
        self.assertEqual(pag["dia"], "2026-10-20")  # dia do Diário = data de disponibilização
        self.assertEqual(len(pag["acoes"]), 1)
        self.assertEqual(pag["acoes"][0]["rodada"], "2026-10-22T19:15")
        self.assertGreaterEqual(pag["acoes"][0]["nota"], 45)  # duas rés, rito ordinário, valor publicado
        self.assertNotIn("FULANO", str(pag))

    def test_radar_item_e_gigante(self):
        item = dict(ITEM_DJEN, tipoComunicacao="Lista de distribuição")
        lead = djen.leads([djen.normalizar(item)], ano_minimo=2026)[0]
        lead["visto_em"] = "2026-10-22T19:12:00"
        lead["empresa_receita"] = {"cnpj": "11222333000181", "razao_social": "TRANSPORTADORA EXEMPLO LTDA", "porte": "DEMAIS",
                                   "capital_social": 80000000, "cnae": "4930202", "atividade": "Transporte rodoviário de carga",
                                   "municipio": "CAJAMAR", "uf": "SP", "telefone": "11 5555-0000", "email": "x@exemplo.com.br",
                                   "socios": [{"nome": "PESSOA FICTICIA", "qualificacao": "Administrador"}]}
        it = radar.item_de_lead(lead, {"teto_capital_gigante": 50000000})
        self.assertEqual((it["hora"], it["tribunal"], it["rito"]), ("19:12", "TRT2", "Ordinário"))
        self.assertTrue(it["gigante"])  # capital acima do teto
        self.assertEqual(it["empresa"]["porte_legivel"], "Média ou grande (acima de R$ 4,8 milhões/ano)")
        self.assertEqual(it["setor"], "Logística e transporte")
        self.assertAlmostEqual(it["valor_causa"], 152300.45)
        self.assertNotIn("FULANO", str(it))  # reclamante (pessoa física) nunca sai
        self.assertFalse(radar.gigante({"capital_social": 100000}, ["PADARIA EXEMPLO LTDA"], 50000000))
        self.assertTrue(radar.gigante({}, ["MERCADO LIVRE BRASIL LTDA"], 50000000))

    def test_radar_lista_do_dia(self):
        import datetime as dt
        import tempfile
        banco = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db"))
        item = dict(ITEM_DJEN, tipoComunicacao="Lista de distribuição")
        novos = radar.acoes_do_dia([djen.normalizar(item)], 2026, set())
        self.assertEqual(len(novos), 1)
        novos[0]["visto_em"] = "2026-10-22T19:12:00"
        banco.guardar_lead(novos[0], "2026-10-22")
        # 0.7.30 (dono): o período conta pela data do processo no Diário (20/10), não por quando o programa o viu (22/10)
        self.assertEqual(len(radar.montar_radar({"radar": {"tribunais": ["TRT2", "TRT15"]}}, banco, dt.datetime(2026, 10, 22, 21, 0))["itens"]), 0)
        pag = radar.montar_radar({"radar": {"tribunais": ["TRT2", "TRT15"]}}, banco, dt.datetime(2026, 10, 22, 21, 0), dias=3)
        self.assertEqual(len(pag["itens"]), 1)
        self.assertEqual(pag["dia"], "2026-10-20")
        self.assertEqual(pag["itens"][0]["link_pje"], "https://pje.trt2.jus.br/consultaprocessual/")

    def test_telegram_sem_token_nao_quebra(self):
        os.environ.pop("LEXSUITE_TELEGRAM_TOKEN", None)
        enviadas, recado = avisar.telegram({"ativo": True, "chat_id": "1"}, ["oi"])
        self.assertEqual(enviadas, 0)
        self.assertIn("LEXSUITE_TELEGRAM_TOKEN", recado)


class Diagnostico(unittest.TestCase):
    def test_mascara_pessoa_e_cpf_mas_deixa_empresa(self):
        from lexsuite import diagnostico as dg
        t = ("RECLAMANTE: MARIA DA SILVA SOUZA RECLAMADO: PADARIA BOM PAO LTDA ADVOGADO: JOAO PEREIRA "
             "Fica V. Sa. notificado. CPF 123.456.789-09.")
        m = dg.mascarar(t)
        self.assertNotIn("MARIA", m)
        self.assertNotIn("JOAO", m)
        self.assertNotIn("123.456.789-09", m)
        self.assertIn("PADARIA BOM PAO LTDA", m)
        self.assertIn("[pessoa]", m)

    def test_relatorio_conta_pistas_e_regra_estrita(self):
        from lexsuite import diagnostico as dg
        leads = [
            {"processo": "1000101-10.2026.5.02.0221", "tribunal": "TRT2", "vara": "Vara do Trabalho de Cajamar",
             "classe": "ATOrd", "tipo": "Intimação", "empresas": ["X LTDA"], "qtd_publicacoes": 1,
             "texto_curto": "Fica a reclamante intimada da audiência inicial designada para 10/11/2026."},
            {"processo": "1000050-10.2026.5.02.0221", "tribunal": "TRT2", "vara": "Vara do Trabalho de Cajamar",
             "classe": "ATOrd", "tipo": "Intimação", "empresas": ["Y S.A."], "qtd_publicacoes": 2,
             "texto_curto": "Fica V. Sa. notificado para pagar as custas processuais."},
        ]
        rel = dg.relatorio_radar(leads, amostras=5, agora=dt.datetime(2026, 10, 24, 10, 0))
        self.assertIn("Regra estrita (só pistas marcadas): 1 leads · só na regra atual: 1", rel)
        self.assertIn("1000050 / 1000101 / 1000101", rel)
        self.assertNotIn("_pistas", json.dumps(leads))


class Tribunais(unittest.TestCase):
    def test_tabela_dos_24(self):
        from lexsuite import tribunais as tb
        self.assertEqual((len(tb.TRTS), len(tb.TJS), len(tb.TRFS), len(tb.SUPERIORES), len(tb.TRIBUNAIS)), (24, 27, 6, 2, 59))
        self.assertEqual(len(tb.UFS), 27)
        self.assertEqual(sorted({u for x in tb.TRTS for u in x["ufs"]}), sorted(tb.UFS))
        self.assertTrue(all(x["regiao"] in tb.REGIOES and x["ramo"] in tb.RAMOS for x in tb.TRIBUNAIS))
        self.assertEqual(tb.validar(["trt15", "TRT2", "TRT99", "TRT2", "tjsp"]), ["TRT2", "TRT15", "TJSP"])
        self.assertEqual(tb.por_uf("sp"), ["TRT2", "TRT15", "TJSP", "TRF3"])
        self.assertEqual(tb.por_ramo("Superior"), ["STJ", "TST"])
        self.assertIn("TJDFT", tb.SIGLAS)
        self.assertEqual(tb.por_regiao("Sul", "Trabalhista"), ["TRT4", "TRT9", "TRT12"])
        self.assertEqual(tb.link_pje("TRT24"), "https://pje.trt24.jus.br/consultaprocessual/")


class Config(unittest.TestCase):
    def test_cria_le_e_grava(self):
        import tempfile
        from lexsuite import config
        pasta = tempfile.mkdtemp()
        caminho = os.path.join(pasta, "config.json")
        recados = []
        cfg = config.carregar(caminho, aviso=recados.append)
        self.assertTrue(os.path.exists(caminho) and recados)
        self.assertEqual(cfg["radar"]["tribunais"], [f"TRT{n}" for n in range(1, 25)])
        self.assertEqual(cfg["compartilhar"]["subpasta"], "LexSuiteONE")
        cfg["radar"]["tribunais"] = ["TRT1"]
        cfg["qualquer_outra_coisa"] = {"fica": True}
        config.salvar(caminho, cfg)
        de_novo = config.carregar(caminho, aviso=recados.append)
        self.assertEqual((de_novo["radar"]["tribunais"], de_novo["qualquer_outra_coisa"]), (["TRT1"], {"fica": True}))
        self.assertIn("porta", de_novo["radar"])  # chave nova entra pelo padrão


class RadarExecutar(unittest.TestCase):
    def test_rodada_completa_sem_internet(self):
        import tempfile
        import shutil
        from lexsuite import radar, monitor, cnpj, conta
        pasta = tempfile.mkdtemp()
        shutil.copy(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "radar_modelo.html"), pasta)
        banco = bd.Banco(os.path.join(pasta, "t.db"))
        pubs = [djen.normalizar(dict(ITEM_DJEN, tipoComunicacao="Lista de distribuição"))]
        original = (monitor.coletar_caderno, cnpj.consultar)
        verificar_original = conta.verificar
        conta.verificar = lambda cfg, versao, hoje=None, pedir=None, retorno=None: verificar_original(cfg, versao, hoje, pedir=lambda u, c, **k: {"ok": True}, retorno=retorno)
        monitor.coletar_caderno = lambda tribunais, dias, banco, diag, aviso, lidos=None, **k: (lidos.append(("TRT2", "2026-10-23", "1")), aviso("  Caderno TRT2: 1 publicações"), pubs)[2]
        cnpj.consultar = lambda c, banco=None, validade_dias=30: {"cnpj": c, "razao_social": "TRANSPORTADORA EXEMPLO LTDA", "porte": "ME", "capital_social": 1000}
        try:
            recados = []
            sit = radar.executar({"radar": {"tribunais": ["TRT2"]}, "conta": {"codigo": "LEX-7K4M-2PQ9"}}, banco, recados.append, pasta,
                                 agora=dt.datetime(2026, 10, 24, 19, 0))
            with self.assertRaises(radar.RoboDesligado):  # sem código de cliente, não lê
                radar.executar({"radar": {"tribunais": ["TRT2"]}}, banco, recados.append, pasta, agora=dt.datetime(2026, 10, 24, 19, 0))
        finally:
            monitor.coletar_caderno, cnpj.consultar = original
            conta.verificar = verificar_original
        self.assertEqual((sit["lidas"], sit["novas"], sit["com_cnpj"]), (1, 1, 1))
        self.assertTrue(os.path.exists(os.path.join(pasta, "saida", "radar", "radar.html")))
        self.assertTrue(os.path.exists(os.path.join(pasta, "saida", "radar", "radar.csv")))
        pagina = radar.montar_radar({"radar": {"tribunais": ["TRT2"]}}, banco, dt.datetime(2026, 10, 24, 20, 0), dias=7)  # Diário de 20/10
        self.assertEqual(len(pagina["itens"]), 1)
        self.assertEqual(pagina["itens"][0]["empresa"]["porte_legivel"], "Microempresa (até R$ 360 mil/ano)")
        self.assertEqual(pagina["itens"][0]["diario_em"], "2026-10-20")
        self.assertNotIn("FULANO", json.dumps(pagina))


class App(unittest.TestCase):
    def setUp(self):
        import tempfile
        import shutil
        from lexsuite import app
        self.pasta = tempfile.mkdtemp()
        shutil.copy(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "radar_modelo.html"), self.pasta)
        self.servidor = app.Servidor(("127.0.0.1", 0), self.pasta)
        import threading
        threading.Thread(target=self.servidor.serve_forever, daemon=True).start()
        self.porta = self.servidor.server_address[1]

    def tearDown(self):
        self.servidor.shutdown()
        self.servidor.server_close()

    def pedir(self, metodo, caminho, corpo=None, cabecalhos=None):
        import http.client
        c = http.client.HTTPConnection("127.0.0.1", self.porta, timeout=10)
        cab = {"Content-Type": "application/json"}
        cab.update(cabecalhos or {})
        c.request(metodo, caminho, body=json.dumps(corpo) if corpo is not None else None, headers=cab)
        r = c.getresponse()
        dados = r.read()
        c.close()
        return r.status, (json.loads(dados) if r.getheader("Content-Type", "").startswith("application/json") else dados)

    def test_pagina_dados_config_e_rodar(self):
        from lexsuite import radar
        status, html = self.pedir("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn(b"window.LEXSUITE_RADAR = null;", html)
        status, d = self.pedir("GET", "/dados?dias=3")
        self.assertEqual((status, d["dias"], len(d["app"]["tribunais"]), len(d["app"]["config"]["tribunais"])), (200, 3, 24, 24))
        # sem o cabeçalho da própria página, nenhum POST passa
        status, _ = self.pedir("POST", "/config", {"tribunais": ["TRT1"]})
        self.assertEqual(status, 403)
        status, r = self.pedir("POST", "/config", {"tribunais": ["trt9", "TRT4", "TRT4", "TRT99"], "dias_na_pagina": 400}, {"X-LexSuite": "1"})
        self.assertEqual((status, r["radar"]["tribunais"], r["radar"]["dias_na_pagina"]), (200, ["TRT4", "TRT9"], 90))
        original = radar.executar
        radar.executar = lambda cfg, banco, aviso, pasta, dias=None, **k: (aviso("rodou " + ",".join(cfg["radar"]["tribunais"])), {"pt": "ok", "en": "ok", "quando": "2026-10-24T19:00"})[1]
        try:
            status, r = self.pedir("POST", "/rodar", {}, {"X-LexSuite": "1"})
            self.assertTrue(r["ok"])
            import time
            for _ in range(50):
                if not self.servidor.estado.como_dict()["rodando"]:
                    break
                time.sleep(0.05)
        finally:
            radar.executar = original
        status, e = self.pedir("GET", "/estado")
        self.assertEqual((e["rodando"], e["situacao"]["pt"], e["mensagens"][-1]["texto"]), (False, "ok", "rodou TRT4,TRT9"))
        status, r = self.pedir("POST", "/outra", {}, {"X-LexSuite": "1"})
        self.assertEqual(status, 404)


if __name__ == "__main__":
    unittest.main()
