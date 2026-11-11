"""Testes da 0.7.16: regra de "ação nova" mais estreita, planilha por frente, armazenamento e cópias de segurança.
Dados FICTÍCIOS."""

import datetime as dt
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexsuite import classificar as cl, djen  # noqa: E402
from testes.test_robo import ITEM_DJEN  # noqa: E402


def _pub(texto, tipo="Intimação", numero="1004000-11.2026.5.02.0221"):
    return djen.normalizar(dict(ITEM_DJEN, texto=texto, tipoComunicacao=tipo, numeroprocessocommascara=numero))


class TestAcaoNova(unittest.TestCase):
    EMPRESA = "<p>RECLAMADO: TRANSPORTADORA EXEMPLO LTDA</p>"

    def test_intimacao_comum_nao_e_acao_nova(self):
        for frase in ("Fica V. Sa. notificado para pagar as custas processuais.",
                      "Fica a parte intimada. Designada audiência de instrução para 10/12/2026.",
                      "Processo distribuído em 2026. Expeça-se mandado de citação para pagamento."):
            lead = djen.leads([_pub(self.EMPRESA + frase)], ano_minimo=2026)[0]
            self.assertFalse(lead["sinal_de_acao_nova"], frase)
            self.assertEqual(lead["sinal"], "")

    def test_sinais_de_comeco(self):
        casos = {"Fica V. Sa. notificado da audiência inicial designada.": "audiência inicial",
                 "Audiência UNA designada para 10/12/2026.": "audiência inicial",
                 "Notificação inicial da reclamada.": "notificação inicial"}
        for frase, sinal in casos.items():
            lead = djen.leads([_pub(self.EMPRESA + frase)], ano_minimo=2026)[0]
            self.assertTrue(lead["sinal_de_acao_nova"], frase)
            self.assertEqual(lead["sinal"], sinal)

    def test_lista_de_distribuicao_e_o_sinal_mais_forte(self):
        lead = djen.leads([_pub(self.EMPRESA + "Sem frase de começo.", tipo="Lista de distribuição")], ano_minimo=2026)[0]
        self.assertTrue(lead["sinal_de_acao_nova"])
        self.assertEqual(lead["sinal"], "lista de distribuição")
        self.assertEqual(cl.sinal_inicio("audiência inicial"), "audiência inicial")


def _banco_com(n, hoje=None, trib="TRT2", espalhar=10 ** 6):
    from lexsuite import banco as bd
    hoje = hoje or dt.date.today()
    b = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db"))
    for k in range(n):
        dia = (hoje - dt.timedelta(days=k % espalhar)).isoformat()
        b.guardar_lead({"processo": f"{k:07d}-11.2026.5.02.0001", "tribunal": trib, "vara": "1ª Vara",
                        "empresas": [f"Empresa Fictícia {k} Ltda"], "data_publicacao": dia, "classe": "ATOrd"}, dia)
    return b


class TestPlanilhaPorFrente(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.mkdtemp()
        self.base = os.path.join(self.pasta, "LexSuiteONE")
        os.makedirs(self.base)
        self.cfg = {"compartilhar": {"pasta": self.pasta}, "radar": {"tribunais": ["TRT2"], "dias_na_pagina": 1}}

    def tearDown(self):
        shutil.rmtree(self.pasta, ignore_errors=True)

    def test_planilha_antiga_vira_trabalhista_com_as_abas_editadas(self):
        from lexsuite import planilha, preferencias as pf, compartilhar
        abas = pf.abas_padrao()
        abas[0]["linhas"][1][1] = 250000
        abas[1]["linhas"].append(["Cliente Fictício Ltda", "cliente atual"])
        planilha.escrever_xlsx(os.path.join(self.base, "LexSuiteONE.xlsx"), [{"nome": "Radar", "linhas": [["x"]]}] + abas)
        recados = []
        self.assertTrue(pf.migrar_nome(self.base, recados.append))
        self.assertFalse(os.path.exists(os.path.join(self.base, "LexSuiteONE.xlsx")))
        prefs = pf.carregar(self.base)
        self.assertEqual(prefs["valor_minimo"], 250000)
        self.assertEqual(prefs["dias_arquivo"], 90)  # ajuste novo, com o padrão
        self.assertEqual([e["nome"] for e in prefs["exclusoes"]], ["Cliente Fictício Ltda"])
        # os ajustes novos entram no fim da aba Preferências, sem mexer no que foi editado
        editaveis, ok = compartilhar._abas_editaveis(pf.caminho(self.base), recados.append)
        nomes = [l[0] for l in editaveis[0]["linhas"]]
        self.assertIn("Dias na aba Arquivo", nomes)
        self.assertEqual(editaveis[0]["linhas"][1][1], 250000)

    def test_planilha_antiga_aberta_nao_perde_as_abas(self):
        """Revisão da 0.7.16: com a antiga aberta no Excel, a troca de nome falha; nada pode criar a nova sem as abas."""
        from lexsuite import planilha, preferencias as pf, compartilhar, radar
        abas = pf.abas_padrao()
        abas[1]["linhas"].append(["Cliente Fictício Ltda", "cliente atual"])
        antiga = os.path.join(self.base, "LexSuiteONE.xlsx")
        planilha.escrever_xlsx(antiga, [{"nome": "Radar", "linhas": [["x"]]}] + abas)
        orig = pf.os.replace
        def trava(*a, **k):
            raise PermissionError("aberta no Excel")
        pf.os.replace = trava
        try:
            prefs = pf.carregar(self.base)
            self.assertIn("Cliente Fictício Ltda", [e["nome"] for e in prefs["exclusoes"]])  # lê as abas da antiga
            recados = []
            b = _banco_com(2)
            self.assertFalse(radar.gravar_planilha(self.cfg, radar.montar_radar(self.cfg, b), b, "0.7.16", self.pasta, recados.append))
            self.assertIn("está aberta", " ".join(recados))
            self.assertEqual(compartilhar.criar_se_faltar(self.cfg), antiga)
            self.assertFalse(os.path.exists(os.path.join(self.base, pf.NOME_ARQUIVO)))
        finally:
            pf.os.replace = orig
        self.assertTrue(pf.migrar_nome(self.base))  # fechou o Excel: troca o nome com as abas
        self.assertIn("Cliente Fictício Ltda", [e["nome"] for e in pf.carregar(self.base)["exclusoes"]])

    def test_exclusoes_valem_em_todas_as_frentes(self):
        from lexsuite import planilha, preferencias as pf
        abas = pf.abas_padrao()
        abas[1]["linhas"].append(["Cliente Tributário Ltda", "cliente"])
        planilha.escrever_xlsx(os.path.join(self.base, pf.NOMES_FRENTE["tributario"]), [{"nome": "Radar", "linhas": [["x"]]}] + abas)
        prefs = pf.carregar(self.base, frente="trabalhista")
        self.assertIn("Cliente Tributário Ltda", [e["nome"] for e in prefs["exclusoes"]])

    def test_gravar_cria_trabalhista_e_pasta_de_copias(self):
        from lexsuite import radar, planilha
        b = _banco_com(5)
        pagina = radar.montar_radar(self.cfg, b)
        self.assertTrue(radar.gravar_planilha(self.cfg, pagina, b, "0.7.16", self.pasta, lambda *_: None))
        caminho = os.path.join(self.base, "LexSuiteONE - Trabalhista.xlsx")
        self.assertTrue(os.path.exists(caminho))
        self.assertTrue(os.path.isdir(os.path.join(self.base, "Cópias de segurança")))
        doc = planilha.ler_xlsx(caminho)
        abas = {a["nome"]: a["linhas"] for a in doc["abas"]}
        procs = lambda linhas: {l[5] for l in linhas[2:]}  # aviso + cabeçalho; a coluna 6 é o processo
        self.assertEqual(len(procs(abas["Radar"]) | procs(abas["Arquivo"])), 5)
        self.assertFalse(procs(abas["Radar"]) & procs(abas["Arquivo"]))  # o que está na Radar não se repete no Arquivo
        self.assertEqual(b.execucoes("planilha", 1)[0]["frente"], "trabalhista")


class TestArmazenamento(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.mkdtemp()
        self.base = os.path.join(self.pasta, "LexSuiteONE")
        self.cfg = {"compartilhar": {"pasta": self.pasta}, "radar": {"tribunais": ["TRT2"], "dias_na_pagina": 1}}

    def tearDown(self):
        shutil.rmtree(self.pasta, ignore_errors=True)

    def test_arquivo_ultimos_dias_mais_trabalhados(self):
        from lexsuite import armazenamento as ar
        hoje = dt.date(2026, 11, 9)
        itens = [{"processo": "a", "primeira_vez": "2026-11-01", "situacao": "novo"},
                 {"processo": "b", "primeira_vez": "2026-01-01", "situacao": "novo"},
                 {"processo": "c", "primeira_vez": "2025-12-01", "situacao": "em_contato"}]
        self.assertEqual([i["processo"] for i in ar.selecionar_arquivo(itens, 90, "", hoje)], ["a", "c"])
        self.assertEqual([i["processo"] for i in ar.selecionar_arquivo(itens, 90, "2026-11-05", hoje)], ["c"])

    def test_caber_corta_o_mais_antigo_nao_trabalhado(self):
        from lexsuite import armazenamento as ar
        radar_l = [{"processo": f"r{k}"} for k in range(900)]
        arq = [{"processo": f"a{k}", "primeira_vez": f"2026-10-{k % 28 + 1:02d}", "situacao": "novo"} for k in range(200)]
        arq.append({"processo": "trab", "primeira_vez": "2020-01-01", "situacao": "virou_cliente"})
        r, a, cortou = ar.caber(radar_l, arq, 1000)
        self.assertTrue(cortou)
        self.assertEqual(len(r) + len(a), 1000)
        self.assertIn("trab", [i["processo"] for i in a])
        self.assertEqual(ar.nivel_planilha(48000, 60000), (80, "grande"))
        self.assertIn("48.000 de 60.000", ar.aviso_tamanho("trabalhista", 48000, 60000))
        self.assertEqual(ar.aviso_tamanho("trabalhista", 100, 60000), "")

    def _disco(self, livre_gb, total_gb=500):
        import collections
        from lexsuite import armazenamento as ar
        orig = ar.shutil.disk_usage
        U = collections.namedtuple("U", "total used free")
        ar.shutil.disk_usage = lambda _p: U(total_gb * ar.GB, (total_gb - livre_gb) * ar.GB, livre_gb * ar.GB)
        self.addCleanup(setattr, ar.shutil, "disk_usage", orig)

    def test_disco(self):
        from lexsuite import armazenamento as ar
        self._disco(100)
        self.assertEqual(ar.disco(self.pasta)["nivel"], "ok")
        self._disco(4)
        self.assertEqual(ar.disco(self.pasta)["nivel"], "baixo")
        self.assertIn("não faz cópias", ar.texto_disco(ar.disco(self.pasta)))
        self._disco(0.5)
        self.assertEqual(ar.disco(self.pasta)["nivel"], "critico")

    def test_copia_de_seguranca_guarda_seis_e_recusa_com_disco_baixo(self):
        from lexsuite import armazenamento as ar, radar
        b = _banco_com(3)
        self.assertTrue(radar.gravar_planilha(self.cfg, radar.montar_radar(self.cfg, b), b, "0.7.16", self.pasta, lambda *_: None))
        for k in range(8):
            ok, onde = ar.copia_seguranca(self.cfg, b, "teste", lambda *_: None, agora=dt.datetime(2026, 11, 9, 10, k))
            self.assertTrue(ok, onde)
        lista = ar.copias(self.base)
        self.assertEqual(len(lista), 6)
        alheia = os.path.join(self.base, "Cópias de segurança", "2025-03-01 10h00m00 contratos do escritório")
        os.makedirs(alheia)
        ar._podar(self.base, lambda *_: None)
        self.assertTrue(os.path.isdir(alheia))  # pasta do escritório com nome parecido nunca é apagada
        self.assertTrue(lista[0]["nome"].startswith("2026-11-09 10h07"))
        arquivos = os.listdir(lista[0]["caminho"])
        self.assertIn("LexSuiteONE - Trabalhista.xlsx", arquivos)
        csvs = [a for a in arquivos if a.endswith(".csv")]
        with open(os.path.join(lista[0]["caminho"], csvs[0]), encoding="utf-8-sig") as f:
            self.assertEqual(len(f.read().strip().splitlines()), 4)  # cabeçalho + 3 ações
        self._disco(2)
        ok, motivo = ar.copia_seguranca(self.cfg, b, "teste", lambda *_: None)
        self.assertFalse(ok)
        self.assertIn("Pouco espaço", motivo)

    def test_limite_faz_limpeza_com_copia_sozinho(self):
        from lexsuite import armazenamento as ar, radar, planilha, preferencias as pf
        b = _banco_com(1200, espalhar=30)
        os.makedirs(self.base)
        abas = pf.abas_padrao()
        for l in abas[0]["linhas"]:
            if l[0] == "Limite de linhas da planilha":
                l[1] = 1000
        planilha.escrever_xlsx(os.path.join(self.base, pf.NOME_ARQUIVO), [{"nome": "Radar", "linhas": [["x"]]}] + abas)
        recados = []
        self.assertTrue(radar.gravar_planilha(self.cfg, radar.montar_radar(self.cfg, b), b, "0.7.16", self.pasta, recados.append))
        self.assertIn("chegou ao limite", " ".join(recados))
        self.assertEqual(len(ar.copias(self.base)), 1)
        reg = b.execucoes("planilha", 1)[0]
        self.assertLessEqual(reg["linhas"], 1000)
        sit = ar.situacao(self.cfg, b, self.pasta)
        self.assertEqual(sit["planilhas"][0]["nome"], "LexSuiteONE - Trabalhista.xlsx")
        self.assertEqual(sit["copias"]["n"], 1)
        self.assertIn(sit["disco"]["nivel"], ("ok", "baixo", "critico"))


class TestTelaEProcessos(unittest.TestCase):
    def test_janela_preta_fecha_sem_tela_e_espera_leitura(self):
        from lexsuite import app

        class Est:
            rodando = False

        class Srv:
            estado, ultimo_pedido, fechou = Est(), 0.0, False

            def shutdown(self):
                self.fechou = True
        relogio = {"t": 0.0}
        srv = Srv()
        def dormir(s):
            relogio["t"] += s
            srv.estado.rodando = relogio["t"] < 200  # leitura até 200 s: não fecha
        self.assertTrue(app.vigiar_tela(srv, lambda *_: None, limite_s=180, passo_s=15, relogio=lambda: relogio["t"], dormir=dormir))
        self.assertGreaterEqual(relogio["t"], 200 + 180)
        # o computador dormiu (relógio pulou): recomeça a contar em vez de fechar na hora
        srv2, rel2, passos = Srv(), {"t": 0.0}, iter([15, 3600, 15, 15])
        def dormir2(s):
            rel2["t"] += next(passos, 15)
        app.vigiar_tela(srv2, lambda *_: None, limite_s=180, passo_s=15, relogio=lambda: rel2["t"], dormir=dormir2)
        self.assertGreater(rel2["t"], 3600 + 180)

    def test_resposta_v1_e_pedido_so_do_que_falta(self):
        from lexsuite import contatos as ct
        proc = "0000001-00.2026.5.02.0001"
        item = {"processo": proc, "tribunal": "TRT2", "empresa": {"razao_social": "Empresa Fictícia Ltda", "cnpj": "", "logradouro": "Rua X"},
                "contato": {"canais": ["telefone"]}, "valor_causa": None, "ajuizada_em": ""}
        self.assertEqual(ct.faltando(item), ["valor_causa", "data_ajuizamento", "email"])
        pasta = tempfile.mkdtemp()
        caminho, n, texto = ct.preparar_v1([item], pasta, limite=30, hoje=dt.date(2026, 11, 12))
        self.assertEqual(n, 1)
        self.assertIn("RESPOSTA PARA O RADAR v1", texto)
        self.assertIn("valor_causa, data_ajuizamento, email", texto)
        resp = "\n".join([
            "RESPOSTA PARA O RADAR v1", "| processo | dado | valor | resultado | fonte | data | observação |", "|---|---|---|---|---|---|---|",
            f"| {proc} | valor_causa | R$ 150.000,00 | encontrado | PJe petição inicial | 2026-11-12 | |",
            f"| {proc} | data_ajuizamento | 05/11/2026 | encontrado | PJe petição inicial | 2026-11-12 | |",
            f"| {proc} | email | contato@empresaficticia.com.br | encontrado | PJe citação | 2026-11-12 | da empresa |",
            f"| {proc} | telefone | | nao_consta | PJe petição inicial | 2026-11-12 | |",
            f"| {proc} | endereco | | tentar_depois | | 2026-11-12 | sessão expirou |",
            f"| {proc} | email | 123.456.789-09 | encontrado | PJe | 2026-11-12 | |",
            f"| {proc} | telefone | (11) 3333-4444 | encontrado | PJe | 2026-11-12 | telefone da testemunha |"])
        r = ct.colar_v1(resp, {proc: "Empresa Fictícia Ltda"})
        self.assertEqual([(c["campo"], c["valor"]) for c in r["completar"]], [("valor_causa", 150000.0), ("data_ajuizamento", "2026-11-05")])
        self.assertEqual([c["canal"] for c in r["contatos"]], ["email"])
        self.assertEqual((len(r["nao_consta"]), len(r["tentar_depois"]), len(r["recusadas"])), (1, 1, 2))
        shutil.rmtree(pasta, ignore_errors=True)

    def test_valor_no_programa_vale_na_lista(self):
        from lexsuite import radar
        b = _banco_com(1)
        proc = "0000000-11.2026.5.02.0001"
        self.assertTrue(b.completar(proc, "valor_causa", 250000.0, "digitado", perfil="ana@example.com"))
        item = radar.montar_radar({"radar": {"tribunais": ["TRT2"], "dias_na_pagina": 5}}, b)["itens"][0]
        self.assertEqual((item["valor_causa"], item["valor_fonte"]), (250000.0, "digitado"))
        self.assertEqual(b.acoes(1)[0]["acao"], "completar:valor_causa")
        self.assertTrue(b.completar(proc, "valor_causa", None))
        self.assertIsNone(radar.montar_radar({"radar": {"tribunais": ["TRT2"], "dias_na_pagina": 5}}, b)["itens"][0]["valor_causa"])
        with self.assertRaises(ValueError):
            b.completar(proc, "cpf", "x")

    def test_nome_sem_e_outros_e_classe_em_maiusculas(self):
        from lexsuite import radar
        self.assertEqual(cl.limpar_nome("Fundacao do Abc e Outros (1)"), "Fundacao do Abc")
        self.assertEqual(cl.limpar_nome("EMPRESA FICTICIA LTDA E OUTROS"), "EMPRESA FICTICIA LTDA")
        item = radar.item_de_lead({"processo": "1", "classe": "AçãO TRABALHISTA - RITO ORDINáRIO", "empresas": ["X Ltda"]}, {})
        self.assertEqual(item["classe"], "AÇÃO TRABALHISTA - RITO ORDINÁRIO")

    def test_termos_das_duas_camadas_e_aceite_de_uso(self):
        from lexsuite import conta
        t = conta._termos({"escritorio": {"versao_vigente": "1.0", "link": "https://judicial.solverone.com.br/aceite.html", "aceito": True,
                                          "versao": "1.0", "nome": "Responsável Fictício"},
                           "pessoa": {"versao_vigente": "1.0", "link": "https://outro-site.example/aceite", "aceito": False}})
        self.assertEqual(t["escritorio"]["link"], "https://judicial.solverone.com.br/aceite.html")
        self.assertEqual(t["pessoa"]["link"], "")  # link fora da SolverONE não é seguido
        enviados = []
        def pedir(url, corpo, **k):
            enviados.append(corpo)
            return {"ok": True, "termos": {"pessoa": {"versao_vigente": "1.0", "aceito": True, "versao": "1.0"}}}
        cfg = {"conta": {"codigo": "LEX-AAAA-BBBB"}, "usuario": {}}
        ok, _ = conta.cadastrar(cfg, "0.7.16", "ana@example.com", "Ana Fictícia", "11222333000181", pedir=pedir,
                                aceite_uso={"versao": "1.0", "fuso": "America/Sao_Paulo"})
        self.assertTrue(ok)
        self.assertEqual(enviados[0]["aceite_uso"], {"versao": "1.0", "fuso": "America/Sao_Paulo"})
        self.assertNotIn("suporta_aceite_uso", enviados[0])  # a trava da pessoa ainda não é pedida (pergunta 13)
        self.assertTrue(cfg["conta"]["termos"]["pessoa"]["aceito"])

    def test_cmd_radar_interrompida_termina_com_aviso_suave(self):
        import argparse
        import json
        import lexsuite_robo as lr
        from lexsuite import radar
        pasta = tempfile.mkdtemp()
        orig_aqui, orig_exec = lr.AQUI, radar.executar
        lr.AQUI = pasta
        def interrompe(*a, **k):
            raise radar.Interrompida({"pt": "parcial"})
        radar.executar = interrompe
        try:
            cfgp = os.path.join(pasta, "config.json")
            with open(cfgp, "w", encoding="utf-8") as f:
                json.dump({"radar": {"tribunais": ["TRT2"]}}, f)
            lr.cmd_radar(argparse.Namespace(config=cfgp, diagnostico=False, dias=1, sem_cnpj=True, agendado=False))
            with open(os.path.join(pasta, "saida", "leitura.json"), encoding="utf-8") as f:
                andamento = json.load(f)
        finally:
            lr.AQUI, radar.executar = orig_aqui, orig_exec
            shutil.rmtree(pasta, ignore_errors=True)
        self.assertEqual(andamento.get("origem"), "à mão (RODAR.bat)")
        self.assertFalse(andamento.get("rodando"))


class V0717(unittest.TestCase):
    """0.7.17: turmas (2º grau) fora, banco grande resume só nunca abertos, limpeza só com cópia, data do critério."""

    def test_turma_de_recurso_nao_e_acao_nova(self):
        pub = djen.normalizar(dict(ITEM_DJEN, tipoComunicacao="Lista de distribuição", nomeOrgao="10ª Turma - Cadeira 3"))
        self.assertEqual(djen.leads([pub], ano_minimo=2026), [])
        self.assertTrue(cl.segundo_grau("Gabinete da Desembargadora Fictícia"))
        self.assertFalse(cl.segundo_grau("1ª Vara do Trabalho de São Paulo"))
        from lexsuite import radar
        b = _banco_com(2)
        b.guardar_lead({"processo": "9999999-11.2026.5.02.0001", "tribunal": "TRT2", "vara": "10ª Turma - Cadeira 3",
                        "empresas": ["Empresa Fictícia Recurso Ltda"]}, dt.date.today().isoformat())
        itens = radar.montar_radar({"radar": {"tribunais": ["TRT2"], "dias_na_pagina": 5}}, b)["itens"]
        self.assertNotIn("9999999-11.2026.5.02.0001", [i["processo"] for i in itens])

    def test_resumo_so_dos_nunca_abertos(self):
        b = _banco_com(3, hoje=dt.date.today() - dt.timedelta(days=400))
        b.mudar_situacao(["0000001-11.2026.5.02.0001"], "em_contato")
        self.assertEqual(b.limpar_detalhe(6, so_nunca_abertos=True), 2)
        resumidos = {l["processo"]: l["resumido"] for l in b.todos_leads()}
        self.assertFalse(resumidos["0000001-11.2026.5.02.0001"])

    def test_limpeza_automatica_sem_copia_nao_enxuga(self):
        from lexsuite import armazenamento as ar
        b = _banco_com(2)
        orig = ar.copia_seguranca
        ar.copia_seguranca = lambda *a, **k: (False, "Pouco espaço no disco.")
        try:
            ok, _ = ar.limpar({"compartilhar": {"pasta": tempfile.mkdtemp()}}, b, "", "0.7.17", lambda *_: None, automatico=True)
        finally:
            ar.copia_seguranca = orig
        self.assertFalse(ok)
        self.assertEqual(b.execucoes("limpeza_planilha", 5), [])


class V0717Revisao(unittest.TestCase):
    """Ressalvas da revisão da 0.7.16: limpeza automática não se repete; poda não apaga cópia feita à mão; aviso legível."""

    def test_limpeza_nao_repete_e_poda_poupa_as_feitas_a_mao(self):
        from lexsuite import armazenamento as ar, radar, planilha, preferencias as pf
        pasta = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, pasta, True)
        base = os.path.join(pasta, "LexSuiteONE")
        cfg = {"compartilhar": {"pasta": pasta}, "radar": {"tribunais": ["TRT2"], "dias_na_pagina": 30}}
        b = _banco_com(1100, espalhar=30)
        os.makedirs(base)
        abas = pf.abas_padrao()
        for l in abas[0]["linhas"]:
            if l[0] == "Limite de linhas da planilha":
                l[1] = 1000
        planilha.escrever_xlsx(os.path.join(base, pf.NOME_ARQUIVO), [{"nome": "Radar", "linhas": [["x"]]}] + abas)
        ok, _ = ar.copia_seguranca(cfg, b, "feita à mão", lambda *_: None, agora=dt.datetime(2026, 1, 1, 9, 0))
        self.assertTrue(ok)
        for _ in range(4):
            radar.gravar_planilha(cfg, radar.montar_radar(cfg, b), b, "0.7.17", pasta, lambda *_: None)
        nomes = [c["nome"] for c in ar.copias(base)]
        self.assertEqual(sum(1 for n in nomes if n.endswith("limpeza automática")), 1)  # uma só, não uma por gravação
        self.assertIn("2026-01-01 09h00m00 - feita à mão", nomes)
        self.assertNotIn(",", ar.aviso_tamanho("trabalhista", 900, 1000).split("linhas")[0].replace("(", ""))


class V0718(unittest.TestCase):
    """0.7.18: estatísticas dos meses anteriores (só totais), reclassificação única da lista antiga, UF no programa."""

    def test_estatisticas_antigas_so_totais(self):
        from lexsuite import banco as bd, historico as h
        b = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db"))
        self.assertEqual(h.pedir(b, 1, ["TRT2"], hoje=dt.date(2026, 11, 9)), 20)
        orig_meta, orig_baixar = djen.meta_caderno, djen.baixar_caderno
        pub = dict(ITEM_DJEN, tipoComunicacao="Lista de distribuição")
        djen.meta_caderno = lambda s_, d, *a, **k: None if d.endswith("-02") else {"url": "fictício"}
        djen.baixar_caderno = lambda s_, d, *a, **k: [djen.normalizar(dict(pub, numeroprocessocommascara="10%05d-11.2026.5.02.0221" % int(d[-2:])))]
        try:
            r = h.processar(b, limite=5, aviso=lambda *_: None, pausa=0)
        finally:
            djen.meta_caderno, djen.baixar_caderno = orig_meta, orig_baixar
        self.assertEqual(r["lidos"] + r["sem_diario"], 5)
        self.assertEqual(b.todos_leads(), [])  # nada entra na Lista nem no Arquivo
        self.assertEqual(sum(m["novas"] for m in h.por_mes(b)), r["novas"])
        self.assertEqual(h.situacao(b)["na_fila"], 15)

    def test_reclassificacao_unica_da_lista_antiga(self):
        import json
        import sqlite3
        from lexsuite import banco as bd
        caminho = os.path.join(tempfile.mkdtemp(), "antigo.db")
        b = bd.Banco(caminho)
        b.con.execute("PRAGMA user_version = 714")
        dados = lambda proc, txt, vara="1ª Vara do Trabalho de São Paulo": {"processo": proc, "tribunal": "TRT2", "vara": vara,
                                                                            "empresas": ["Empresa Fictícia Ltda"], "texto_curto": txt, "tipo": "Intimação"}
        for proc, txt, vara in (("a", "Fica V. Sa. notificado para pagar custas.", None), ("b", "Notificação inicial da reclamada.", None),
                                ("c", "Processo distribuído por sorteio.", None), ("d", "Lista", "10ª Turma - Cadeira 3"),
                                ("e", "Reclamante: pessoa física. Reclamada: Empresa Fictícia Ltda.", None)):
            b.guardar_lead(dados(proc, txt, vara or "1ª Vara do Trabalho de São Paulo"), "2026-11-06")
        b.con.execute("UPDATE leads SET fora_criterio = 0, vara = CASE processo WHEN 'd' THEN '10ª Turma - Cadeira 3' ELSE vara END")
        b.con.commit(); b.con.close()
        b2 = bd.Banco(caminho)
        self.assertEqual(sorted(l["processo"] for l in b2.todos_leads()), ["b", "c", "e"])  # sem sinal de intimação comum, fica
        self.assertEqual(len(sqlite3.connect(caminho).execute("SELECT * FROM leads").fetchall()), 5)  # nada é apagado
        _ = json


class V0718Revisao(unittest.TestCase):
    """Revisão da 0.7.18 (Operação): turma trabalhada fica; CNJ fora do ar para a fila sem marcar erro; dia de outro
    tribunal não perde a estatística antiga."""

    def test_turma_trabalhada_fica_na_lista(self):
        from lexsuite import radar
        b = _banco_com(1)
        b.guardar_lead({"processo": "8888888-11.2026.5.02.0001", "tribunal": "TRT2", "vara": "10ª Turma - Cadeira 3",
                        "empresas": ["Empresa Fictícia Cliente Ltda"]}, dt.date.today().isoformat())
        b.mudar_situacao(["8888888-11.2026.5.02.0001"], "em_contato")
        itens = radar.montar_radar({"radar": {"tribunais": ["TRT2"], "dias_na_pagina": 5}}, b)["itens"]
        self.assertIn("8888888-11.2026.5.02.0001", [i["processo"] for i in itens])

    def test_cnj_fora_do_ar_para_a_fila(self):
        from lexsuite import banco as bd, historico as h
        b = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db"))
        h.pedir(b, 1, ["TRT2"], hoje=dt.date(2026, 11, 9))
        orig = djen.meta_caderno
        def fora(*a, **k):
            raise RuntimeError("HTTP 503 em comunicaapi (fictício)")
        djen.meta_caderno = fora
        try:
            r = h.processar(b, limite=5, aviso=lambda *_: None, pausa=0)
        finally:
            djen.meta_caderno = orig
        self.assertIn("parou", r)  # 0.7.19: para depois de 3 Diários diferentes seguidos com o site fora
        self.assertEqual((h.situacao(b)["erros"], h.situacao(b)["na_fila"]), (3, 17))
        self.assertEqual(set(r["parou"]), {"pt", "en"})
        h.tentar_de_novo_os_erros(b)
        self.assertEqual(h.situacao(b)["na_fila"], 20)  # os erros voltam para a fila na próxima rodada

    def test_estatistica_antiga_de_outro_tribunal_fica(self):
        from lexsuite import banco as bd
        b = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db"))
        b.con.execute("INSERT INTO estatisticas_diarias VALUES ('2026-11-06','TRT3','1ª Vara','trabalhista','','',7,0,'x')")
        b.guardar_lead({"processo": "1", "tribunal": "TRT2", "vara": "1ª Vara", "empresas": ["X Fictícia Ltda"], "data_publicacao": "2026-11-06"}, "2026-11-06")
        b.atualizar_estatisticas()
        self.assertEqual(sum(e["novas"] for e in b.estatisticas() if e["tribunal"] == "TRT3"), 7)


class V0719(unittest.TestCase):
    """0.7.19: banco que passou pela 0.7.18 antes da correção devolve a turma trabalhada; cópia do banco com data."""

    def test_banco_718_devolve_trabalhada_e_copia_com_data(self):
        from lexsuite import banco as bd
        pasta = tempfile.mkdtemp()
        caminho = os.path.join(pasta, "lexsuite.db")
        b = bd.Banco(caminho)
        b.guardar_lead({"processo": "t1", "tribunal": "TRT2", "vara": "10ª Turma", "empresas": ["Empresa Fictícia Ltda"]}, "2026-11-06")
        b.mudar_situacao(["t1"], "virou_cliente")
        b.con.execute("UPDATE leads SET fora_criterio = 1")
        b.con.execute("PRAGMA user_version = 718")
        b.con.commit(); b.con.close()
        b2 = bd.Banco(caminho)
        self.assertEqual([l["processo"] for l in b2.todos_leads()], ["t1"])
        self.assertEqual(b2.con.execute("PRAGMA user_version").fetchone()[0], 719)
        # banco antigo (antes da 0.7.18) ganha cópia com data no nome, sem arquivo temporário sobrando
        c2 = os.path.join(pasta, "outro.db")
        b3 = bd.Banco(c2)
        b3.guardar_lead({"processo": "x", "tribunal": "TRT2", "vara": "1ª Vara", "empresas": ["X Fictícia Ltda"]}, "2026-11-06")
        b3.con.execute("PRAGMA user_version = 714"); b3.con.commit(); b3.con.close()
        bd.Banco(c2)
        copias = [n for n in os.listdir(pasta) if n.startswith("outro.db.antes-0.7.18-")]
        self.assertEqual(len(copias), 1)
        self.assertFalse([n for n in os.listdir(pasta) if n.endswith(".tmp")])


class V0719Tela(unittest.TestCase):
    """0.7.19: depois de reiniciar, a tela mostra a última leitura do banco (não "Ainda não leu neste computador")."""

    def test_ultima_leitura_vem_do_banco(self):
        from lexsuite import app, banco as bd
        pasta = tempfile.mkdtemp()
        srv = app.Servidor(("127.0.0.1", 0), pasta)
        try:
            self.assertFalse(srv.estado_atual().get("situacao"))
            bd.Banco(srv.caminho_db).registrar("radar", {"versao": "0.7.18", "tribunais": ["TRT2"], "lidas": 120, "novas": 7,
                                                         "com_cnpj": 3, "duracao": 9, "resultado": "ok", "erro": ""})
            sit = srv.estado_atual()["situacao"]
            self.assertIn("120", sit["pt"]); self.assertIn("7", sit["en"]); self.assertTrue(sit["quando"])
            self.assertIs(srv.ultima_do_banco(), srv.ultima_do_banco())  # guardada até o banco mudar
        finally:
            srv.server_close()


    def test_teste_leve_da_pasta_nao_grava(self):
        from lexsuite import compartilhar
        pasta = tempfile.mkdtemp()
        ok, msg = compartilhar.testar(pasta, "RADAR - planilha", leve=True)
        self.assertTrue(ok); self.assertIn("RADAR - planilha", msg)
        self.assertEqual(os.listdir(pasta), [])  # nada criado nem gravado
        self.assertFalse(compartilhar.testar(os.path.join(pasta, "nao-existe"), "x", leve=True)[0])


class V0720(unittest.TestCase):
    """0.7.20: interruptores do RootifyONE chegam pela conferência da licença (lex-conta v12) e ficam guardados."""

    def test_recursos_da_lex_conta(self):
        import datetime as dt
        from lexsuite import conta
        cfg = {"conta": {"codigo": "LEX-ABCD-EFGH", "instalacao": "teste"}}
        conta.verificar(cfg, "0.7.20", dt.date(2026, 11, 10), pedir=lambda *a, **k: {"ok": True, "recursos": {"assistone": False, "x" * 99: True, "lixo": "sim"}})
        self.assertEqual(cfg["conta"]["recursos"]["assistone"], False)
        self.assertNotIn("lixo", cfg["conta"]["recursos"])
        self.assertTrue(all(len(k) <= 60 for k in cfg["conta"]["recursos"]))
        self.assertEqual(conta.situacao(cfg)["recursos"]["assistone"], False)
        # sem o campo, mantém o último
        conta.verificar(cfg, "0.7.20", dt.date(2026, 11, 11), pedir=lambda *a, **k: {"ok": True})
        self.assertEqual(cfg["conta"]["recursos"]["assistone"], False)


    def test_erro_das_estatisticas_avisa_a_solverone(self):
        """B1 da revisão da 0.7.19: a mensagem diz "a SolverONE foi avisada"; então o registro técnico é enviado."""
        import json as _json, threading, time, http.client
        from unittest import mock
        from lexsuite import app, conta as _conta, historico as _h
        pasta = tempfile.mkdtemp()
        srv = app.Servidor(("127.0.0.1", 0), pasta)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            import sqlite3
            with mock.patch.object(_h, "processar", side_effect=sqlite3.OperationalError("database is locked")), \
                    mock.patch.object(_conta, "registrar_erro") as reg:
                c = http.client.HTTPConnection("127.0.0.1", srv.server_address[1], timeout=10)
                c.request("POST", "/estatisticas/ler", body="{}", headers={"X-LexSuite": "1", "Content-Type": "application/json"})
                c.getresponse().read(); c.close()
                for _ in range(100):
                    if reg.called and srv.hist.get("erro"):
                        break
                    time.sleep(0.05)
                time.sleep(0.1)
                self.assertEqual(reg.call_count, 1)
                self.assertEqual(reg.call_args[0][2], "estatisticas antigas")
                self.assertTrue(srv.hist.get("erro"))
            # 0.7.21: sem internet (aviso não chegou), o texto não promete que a SolverONE foi avisada
            srv.hist.clear()
            with mock.patch.object(_h, "processar", side_effect=sqlite3.OperationalError("database is locked")), \
                    mock.patch.object(_conta, "registrar_erro", return_value=False):
                c = http.client.HTTPConnection("127.0.0.1", srv.server_address[1], timeout=10)
                c.request("POST", "/estatisticas/ler", body="{}", headers={"X-LexSuite": "1", "Content-Type": "application/json"})
                c.getresponse().read(); c.close()
                for _ in range(100):
                    if srv.hist.get("erro"):
                        break
                    time.sleep(0.05)
                time.sleep(0.1)
                self.assertNotIn("avisad", srv.hist["erro"]["pt"])
                self.assertNotIn("notified", srv.hist["erro"]["en"])
        finally:
            srv.shutdown(); srv.server_close()

    def test_copia_tmp_pela_metade_nao_conta(self):
        from lexsuite import banco as bd
        pasta = tempfile.mkdtemp()
        caminho = os.path.join(pasta, "lexsuite.db")
        bd.Banco(caminho).con.close()
        open(caminho + ".antes-9.9.9-2026-11-09.tmp", "w").close()
        b = bd.Banco(caminho)
        b._copia_antes(caminho, "9.9.9")
        self.assertTrue([n for n in os.listdir(pasta) if n.startswith("lexsuite.db.antes-9.9.9-") and not n.endswith(".tmp")])

    def test_pagina_com_regra_de_seguranca(self):
        import threading, http.client
        from lexsuite import app
        pasta = tempfile.mkdtemp()
        shutil.copy(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "radar_modelo.html"), pasta)
        srv = app.Servidor(("127.0.0.1", 0), pasta)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            c = http.client.HTTPConnection("127.0.0.1", srv.server_address[1], timeout=10)
            c.request("GET", "/"); r = c.getresponse(); r.read(); c.close()
            csp = r.getheader("Content-Security-Policy") or ""
            for regra in ("connect-src 'self'", "form-action 'self'", "frame-ancestors 'none'", "img-src 'self' data:"):
                self.assertIn(regra, csp)
        finally:
            srv.shutdown(); srv.server_close()


    def test_envio_lento_nao_suja_a_leitura_seguinte(self):
        """0.7.21 (revisão): o aviso de erro de uma leitura antiga, demorado, não muda a leitura nova."""
        import threading, time, http.client, sqlite3
        from unittest import mock
        from lexsuite import app, conta as _conta, historico as _h
        pasta = tempfile.mkdtemp()
        srv = app.Servidor(("127.0.0.1", 0), pasta)
        threading.Thread(target=srv.serve_forever, daemon=True).start()

        def pedir_ler():
            c = http.client.HTTPConnection("127.0.0.1", srv.server_address[1], timeout=10)
            c.request("POST", "/estatisticas/ler", body="{}", headers={"X-LexSuite": "1", "Content-Type": "application/json"})
            r = c.getresponse().read(); c.close()
            return r
        chamadas = []

        def processar(*a, **k):
            chamadas.append(1)
            if len(chamadas) == 1:
                raise sqlite3.OperationalError("database is locked")
            time.sleep(1.0)
            return {"lidos": 0}
        try:
            with mock.patch.object(_h, "processar", side_effect=processar), \
                    mock.patch.object(_conta, "registrar_erro", side_effect=lambda *a, **k: (time.sleep(0.5), True)[1]):
                pedir_ler()
                for _ in range(100):
                    if not srv.hist.get("rodando"):
                        break
                    time.sleep(0.02)
                pedir_ler()  # leitura nova enquanto o aviso da antiga ainda está sendo enviado
                time.sleep(0.7)  # o envio antigo terminou
                self.assertTrue(srv.hist.get("rodando"))
                self.assertNotIn("erro", srv.hist)
                for _ in range(100):
                    if not srv.hist.get("rodando"):
                        break
                    time.sleep(0.05)
                self.assertEqual(srv.hist.get("ultimo"), {"lidos": 0})
        finally:
            srv.shutdown(); srv.server_close()


class V0723(unittest.TestCase):
    """0.7.23: testes que faltavam (revisão da 0.7.22, item 7)."""

    def test_licenca_em_ingles(self):
        from lexsuite import conta
        cfg = {"conta": {"codigo": "LEX-ABCD-EFGH", "resposta": "vencido", "ultima_ok": "2026-11-01"}}
        sit = conta.situacao(cfg)
        self.assertFalse(sit["ok"]); self.assertIn("venceu", sit["texto"]); self.assertIn("expired", sit["texto_en"])
        cfg["conta"]["resposta"] = "ok"
        self.assertEqual(conta.situacao(cfg)["texto_en"], "Licence active.")
        cfg["conta"].update({"resposta": "sem_resposta", "ultima_ok": "lixo"})  # data inválida: PT e EN dizem a mesma coisa
        self.assertIn("Ainda não consegui", conta.bloqueio(cfg)); self.assertIn("could not confirm the client code", conta.bloqueio_en(cfg))

    def test_dias_para_tras_com_limite(self):
        from lexsuite import config, app
        for v, esperado in (("abc", 1), ([], 1), (float("inf"), 1), (1e400, 1), (99, 10), (-5, 0), (3, 3)):
            self.assertEqual(config.inteiro(v, 1, 0, 10), esperado, v)
            self.assertEqual(app._dias_para_tras({"dias_para_tras": v}), esperado, v)

    def test_marca_so_leitura_e_remarca_se_a_troca_falha(self):
        import stat
        from unittest import mock
        from lexsuite import planilha
        pasta = tempfile.mkdtemp(); caminho = os.path.join(pasta, "x.xlsx")
        planilha.escrever_xlsx(caminho, [{"nome": "A", "linhas": [["a"]]}], marcar=True)
        self.assertFalse(os.stat(caminho).st_mode & stat.S_IWRITE)
        planilha.liberar_escrita(caminho)
        self.assertTrue(os.stat(caminho).st_mode & stat.S_IWRITE)
        planilha.marcar_so_leitura(caminho)
        with mock.patch.object(planilha.os, "replace", side_effect=PermissionError("em uso")):
            with self.assertRaises(PermissionError):
                planilha.escrever_xlsx(caminho, [{"nome": "A", "linhas": [["b"]]}], marcar=True)
        self.assertFalse(os.stat(caminho).st_mode & stat.S_IWRITE)  # voltou a ficar só para leitura
        self.assertEqual([n for n in os.listdir(pasta) if n.endswith(".tmp")], [])

    def test_planilha_nova_ja_nasce_marcada(self):
        import stat
        from lexsuite import compartilhar
        pasta = tempfile.mkdtemp()
        cfg = {"compartilhar": {"pasta": pasta, "subpasta": "RADAR"}}
        caminho = compartilhar.criar_se_faltar(cfg, "0.7.23", "", lambda *_: None)
        self.assertFalse(os.stat(caminho).st_mode & stat.S_IWRITE)

    def test_nuvens_usa_a_lista_recebida(self):
        from lexsuite import compartilhar
        pasta = tempfile.mkdtemp()
        n = compartilhar.nuvens([pasta])
        self.assertEqual(n[0], {"tipo": "gdrive", "caminho": pasta})


class TelaSemComentarioQueEngoleCodigo(unittest.TestCase):
    """0.7.24/0.7.25: um comentário // no meio da linha já engoliu código três vezes (o node não acusa, porque continua
    válido). Procura, depois de //, qualquer coisa com cara de comando: chamada seguida de ";", var/let/const/if/for/while/
    return, ou atribuição seguida de ";" (revisão da 0.7.24: um comando só também conta)."""
    PADROES = (r"[A-Za-z_$][\w$.]*\([^)]*\)\s*(;|$)", r"\b(var|let|const|if|for|while|return)\b[^;]*[;{]", r"[\w$.\]]+\s*=[^=>][^;]*;",
               r"[\w$\]]\s*(\+\+|--)\s*;", r"[\w$.\]]+\s*[+\-*/]=", r"\b(break|continue)\s*;",
               r"\}\s*(catch|finally|else)\b", r"\}\s*\)?\s*;?\s*$", r"\.then\s*\(", r"\{\s*headers\s*:")  # 0.7.30: ".then(" e "{ headers:" depois de //  # 0.7.26; revisão da 0.7.28: "} catch (e) {}" e "}" no fim: i++, z += 1, a.f(c) sem ";", break

    @classmethod
    def ruins(cls, texto):
        import re
        out = []
        for linha in texto.split("\n"):
            if "base64," in linha:
                continue
            for m in re.finditer(r"(?<![:\\])//(?!/)", linha):  # 0.7.26: também "x"// (depois de aspas)
                if any(re.search(p, linha[m.end():]) for p in cls.PADROES):
                    out.append(linha.strip()[:120])
                    break
        return out

    def test_nenhum_comentario_no_meio_da_linha(self):
        s = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "radar_modelo.html"), encoding="utf-8").read()
        i = s.index('<script id="assistone-master">'); j = s.index("</script>", i)
        self.assertEqual(self.ruins(s[:i] + s[j:]), [])

    def test_o_teste_pega_o_erro(self):
        for ex in ("a.appendChild(b); // nota  a.appendChild(c);", "x(); // nota  if (x) { y(); }",
                   "x(); // nota  var z = 1;", "x(); // nota  z = 1;", "x(); // nota i++;", "x(); // nota z += 1;",
                   "x(); // nota a.f(c)", "x(); // nota break;", 'var s = "x"// nota z = 1;',
                   "try { x(); // nota } catch (e) {}", "if (a) { x(); // nota }",
                   'return fetch("/x")  // nota .then(function (r) {'):
            self.assertTrue(self.ruins(ex), ex)
        self.assertFalse(self.ruins("x(); // nota em prosa (com parênteses); e ponto e vírgula"))

class V0725(unittest.TestCase):
    """0.7.25: testes que faltavam (revisões da 0.7.23 e da 0.7.24)."""

    def _post(self, srv, rota, corpo):
        import http.client, json as _j
        c = http.client.HTTPConnection("127.0.0.1", srv.server_address[1], timeout=10)
        c.request("POST", rota, body=_j.dumps(corpo), headers={"X-LexSuite": "1", "Content-Type": "application/json"})
        r = _j.loads(c.getresponse().read()); c.close()
        return r

    def test_rodar_e_config_com_valores_absurdos(self):
        """0.7.26 (revisão): cada correção da 0.7.25 é exercitada de verdade (desfazer qualquer uma faz o teste falhar)."""
        import threading, http.client, json as _j
        from unittest import mock
        from lexsuite import app
        pasta = tempfile.mkdtemp()
        with open(os.path.join(pasta, "config.json"), "w", encoding="utf-8") as f:  # Infinity literal, escrito à mão
            f.write('{"radar": {"tribunais": ["TRT2"], "dias_na_pagina": Infinity}}')
        srv = app.Servidor(("127.0.0.1", 0), pasta)
        recebidos = []
        srv.rodar = lambda dias=None: (recebidos.append(dias), True)[1]
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            c = http.client.HTTPConnection("127.0.0.1", srv.server_address[1], timeout=10)
            c.request("GET", "/dados", headers={"X-LexSuite": "1"}); self.assertEqual(c.getresponse().status, 200); c.close()
            for dias, esperado in ((None, None), (1e400, None), (0, 0), (99, 10), (3, 3)):
                r = self._post(srv, "/rodar", {"dias": dias})
                self.assertTrue(r["ok"]); self.assertEqual(recebidos[-1], esperado, dias)
            self.assertIn("ok", self._post(srv, "/config", {"dias_na_pagina": 1e400}))
        finally:
            srv.shutdown(); srv.server_close()

    def test_montar_radar_com_dias_absurdos(self):
        import datetime as _dt
        from lexsuite import radar, banco as bd
        b = bd.Banco(os.path.join(tempfile.mkdtemp(), "x.db"))
        for v in (float("inf"), 1e400, "abc", [1], 10 ** 400):
            pagina = radar.montar_radar({"radar": {"tribunais": ["TRT2"], "dias_na_pagina": v}}, b, agora=_dt.datetime(2026, 11, 10), prefs={})
            self.assertIn("itens", pagina)

    def test_marcar_se_livre(self):
        import stat, threading
        from unittest import mock
        from lexsuite import planilha, app, compartilhar, preferencias
        pasta = tempfile.mkdtemp(); caminho = os.path.join(pasta, "x.xlsx")
        planilha.escrever_xlsx(caminho, [{"nome": "A", "linhas": [["a"]]}])
        real_open = open
        def aberto_no_excel(arq, modo="r", *a, **k):  # o Excel trava a escrita: abrir "r+b" falha
            if str(arq) == caminho and "+" in modo:
                raise PermissionError("em uso")
            return real_open(arq, modo, *a, **k)
        with mock.patch("builtins.open", aberto_no_excel):
            self.assertFalse(planilha.marcar_se_livre(caminho))
        self.assertTrue(os.stat(caminho).st_mode & stat.S_IWRITE)  # em uso: não marcou
        self.assertTrue(planilha.marcar_se_livre(caminho))
        self.assertFalse(os.stat(caminho).st_mode & stat.S_IWRITE)
        self.assertTrue(planilha.marcar_se_livre(caminho))  # já marcada conta como livre
        # a rota /abrir devolve em_uso para a tela
        srv = app.Servidor(("127.0.0.1", 0), pasta)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            with mock.patch.object(compartilhar, "pasta_base", return_value=pasta), \
                    mock.patch.object(preferencias, "caminho", return_value=caminho), \
                    mock.patch.object(planilha, "marcar_se_livre", return_value=False), \
                    mock.patch.object(app, "abrir_so_leitura", return_value=True):
                r = self._post(srv, "/abrir", {"o_que": "planilha"})
            self.assertTrue(r["ok"]); self.assertTrue(r["em_uso"])
            with mock.patch.object(compartilhar, "pasta_base", return_value=pasta), \
                    mock.patch.object(preferencias, "caminho", return_value=caminho), \
                    mock.patch.object(planilha, "marcar_se_livre", return_value=False), \
                    mock.patch.object(app, "abrir_so_leitura", return_value=False), \
                    mock.patch.object(app, "abrir_no_windows", return_value=True):
                r = self._post(srv, "/abrir", {"o_que": "planilha"})
            self.assertTrue(r["ok"]); self.assertTrue(r["em_uso"]); self.assertNotIn("so_leitura", r)  # sem Excel: a tela usa o outro texto
        finally:
            srv.shutdown(); srv.server_close()

class V0727(unittest.TestCase):
    """0.7.27: revisão da 0.7.26."""

    def test_dados_com_infinity_e_nan_no_config_dao_json_valido(self):
        import threading, http.client, json as _j
        from lexsuite import app
        pasta = tempfile.mkdtemp()
        with open(os.path.join(pasta, "config.json"), "w", encoding="utf-8") as f:
            f.write('{"radar": {"tribunais": ["TRT2"], "valor_minimo": Infinity, "dias_na_pagina": NaN, "teto_capital_gigante": -Infinity}}')
        srv = app.Servidor(("127.0.0.1", 0), pasta)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            c = http.client.HTTPConnection("127.0.0.1", srv.server_address[1], timeout=10)
            c.request("GET", "/dados", headers={"X-LexSuite": "1"}); r = c.getresponse(); corpo = r.read(); c.close()
            self.assertEqual(r.status, 200)
            def recusa(x):
                raise ValueError(x)
            d = _j.loads(corpo, parse_constant=recusa)  # o navegador recusa Infinity e NaN; aqui também
            self.assertIsNone(d["app"]["config"]["valor_minimo"]); self.assertEqual(d["app"]["config"]["dias_na_pagina"], 1)
        finally:
            srv.shutdown(); srv.server_close()

    def test_textos_de_planilha_em_uso_com_marca(self):
        import re
        s = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "radar_modelo.html"), encoding="utf-8").read()
        for chave in ("planilha_em_uso", "planilha_em_uso_sem_excel"):
            textos = re.findall(r"\b" + chave + r': "([^"]*)"', s)
            self.assertEqual(len(textos), 2, chave)  # PT e EN
            self.assertTrue(all("{c}" in x and "RADAR" not in x for x in textos), chave)
        self.assertRegex(s, r'\.so_leitura \? "planilha_em_uso" : "planilha_em_uso_sem_excel"')


class V0728(unittest.TestCase):
    """0.7.28: revisão da 0.7.27."""

    def test_area_logada_e_guardar_meses_absurdos(self):
        import threading, http.client, json as _j
        from lexsuite import app
        pasta = tempfile.mkdtemp()
        with open(os.path.join(pasta, "config.json"), "w", encoding="utf-8") as f:
            f.write('{"radar": {"tribunais": ["TRT2"], "area_logada_por_dia": Infinity, "guardar_meses": "abc"}}')
        srv = app.Servidor(("127.0.0.1", 0), pasta)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            c = http.client.HTTPConnection("127.0.0.1", srv.server_address[1], timeout=10)
            c.request("GET", "/dados", headers={"X-LexSuite": "1"}); r = c.getresponse(); corpo = r.read(); c.close()
            self.assertEqual(r.status, 200)
            d = _j.loads(corpo)
            self.assertEqual(d["app"]["config"]["area_logada_por_dia"], 30); self.assertEqual(d["app"]["config"]["guardar_meses"], 12)
        finally:
            srv.shutdown(); srv.server_close()

    def test_servidor_ficticio_sem_internet(self):
        texto = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tela", "servidor_ficticio.py"), encoding="utf-8").read()
        self.assertIn("_rede.pedir = _rede.pedir_bytes = _rede.pedir_json = _sem_internet", texto)


class Regras0728(unittest.TestCase):
    """0.7.28 (dono): as regras do escritório se editam na tela e o RADAR grava nas abas da planilha.
    Revisão da 0.7.28: nunca grava por cima do que a tela não leu; cópia antes; pedido ruim não derruba."""

    def setUp(self):
        import threading, json as _j
        from lexsuite import app
        self.pasta = tempfile.mkdtemp(); planilhas = tempfile.mkdtemp()
        with open(os.path.join(self.pasta, "config.json"), "w", encoding="utf-8") as f:
            _j.dump({"radar": {"tribunais": ["TRT2"]}, "compartilhar": {"pasta": planilhas}}, f)
        self.srv = app.Servidor(("127.0.0.1", 0), self.pasta)
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def tearDown(self):
        self.srv.shutdown(); self.srv.server_close()

    def pedir(self, metodo, rota, corpo=None, cru=None):
        import http.client, json as _j
        c = http.client.HTTPConnection("127.0.0.1", self.srv.server_address[1], timeout=20)
        c.request(metodo, rota, body=cru if cru is not None else (_j.dumps(corpo) if corpo is not None else None),
                  headers={"X-LexSuite": "1", "Content-Type": "application/json"})
        r = c.getresponse(); d = _j.loads(r.read()); d["_status"] = r.status; c.close(); return d

    def base(self):
        from lexsuite import compartilhar
        return compartilhar.pasta_base(self.srv.config())

    def arquivo(self):
        from lexsuite import preferencias
        return preferencias.caminho(self.base(), "trabalhista")

    def exclusoes_no_disco(self):
        from lexsuite import preferencias
        return [e["nome"] for e in preferencias.carregar(self.base(), doc=__import__("lexsuite.planilha", fromlist=["x"]).ler_xlsx(self.arquivo(), so_abas=preferencias.ABAS_EDITAVEIS))["exclusoes"]]

    def salvar(self, valores=None, exclusoes=None, marca=None):
        if marca is None:
            marca = self.pedir("GET", "/regras")["marca"]
        return self.pedir("POST", "/regras", {"valores": valores or {}, "exclusoes": exclusoes or [], "marca": marca})

    def test_salvar_e_ler_as_regras(self):
        from lexsuite import preferencias, planilha
        d0 = self.pedir("GET", "/regras"); self.assertTrue(d0["ok"]); self.assertEqual(d0["marca"], "nova")
        r = self.salvar({"valor_minimo": 250000, "esconder_gigantes": True, "mostrar_socios": False, "limite_linhas": 1e400},
                        [{"nome": "Empresa Fictícia Cliente Ltda", "motivo": "cliente atual"}, {"nome": ""},
                         {"nome": "empresa fictícia cliente ltda", "motivo": "repetida"}, 7, "texto", None], marca="nova")
        self.assertTrue(r["ok"], r); self.assertEqual(r["exclusoes"], 1)
        d = self.pedir("GET", "/regras")
        self.assertEqual(d["valores"]["valor_minimo"], 250000); self.assertTrue(d["valores"]["esconder_gigantes"])
        self.assertFalse(d["valores"]["mostrar_socios"]); self.assertEqual(d["valores"]["limite_linhas"], preferencias.PADRAO["limite_linhas"])
        self.assertEqual([e["nome"] for e in d["exclusoes"]], ["Empresa Fictícia Cliente Ltda"])
        self.assertEqual(d["marca"], r["marca"])
        # a tela mostra só as exclusões da planilha que ela regrava (a de outra frente não volta depois de tirar)
        planilha.escrever_xlsx(os.path.join(self.base(), preferencias.NOMES_FRENTE["tributario"]),
                               [{"nome": "Exclusões", "linhas": [["Nome", "Motivo"], ["Outra Empresa Fictícia SA", "tributário"]]}])
        self.assertEqual([e["nome"] for e in self.pedir("GET", "/regras")["exclusoes"]], ["Empresa Fictícia Cliente Ltda"])
        # ...mas, na leitura e na aba Radar, as das outras frentes continuam valendo junto com as novas (trocar=)
        p = preferencias.carregar(self.base(), trocar={"Preferências": preferencias.linhas_regras({}, [])[0],
                                                       "Exclusões": [["Nome", "Motivo"], ["Nova Fictícia Ltda", ""]]})
        self.assertEqual(sorted(e["nome"] for e in p["exclusoes"]), ["Nova Fictícia Ltda", "Outra Empresa Fictícia SA"])
        self.assertTrue(self.salvar({}, [])["ok"])
        self.assertEqual(self.pedir("GET", "/regras")["exclusoes"], [])

    def test_planilha_ilegivel_nao_mostra_formulario_nem_grava_por_cima(self):
        """Bloqueio da revisão: planilha com 3 exclusões, ilegível ao abrir a tela, legível ao salvar: nada se perde."""
        import shutil as _sh
        r = self.salvar({"valor_minimo": 250000}, [{"nome": f"Empresa Fictícia {n} Ltda"} for n in (1, 2, 3)], marca="nova")
        self.assertTrue(r["ok"], r)
        from lexsuite import planilha
        boa = self.arquivo() + ".boa"; _sh.copyfile(self.arquivo(), boa)
        planilha.liberar_escrita(self.arquivo())  # a consulta fica "somente leitura" (sem root não se escreve por cima)
        with open(self.arquivo(), "wb") as f:
            f.write(b"isto nao e um xlsx")  # corrompida / sincronizando
        d = self.pedir("GET", "/regras")
        self.assertFalse(d["ok"]); self.assertNotIn("valores", d); self.assertNotIn("exclusoes", d); self.assertTrue(d["motivo_en"])
        self.assertFalse(self.salvar({}, [], marca="")["ok"])  # ainda ilegível: recusa
        planilha.liberar_escrita(self.arquivo()); _sh.copyfile(boa, self.arquivo())  # o Drive terminou de sincronizar
        for marca in ("", "nova", "qualquer"):  # a tela não tinha lido: qualquer marca que não seja a de agora é recusada
            self.assertFalse(self.salvar({}, [], marca=marca)["ok"])
        self.assertEqual(len(self.exclusoes_no_disco()), 3)

    def test_planilha_mudou_depois_de_abrir(self):
        r = self.salvar({}, [{"nome": "Empresa Fictícia A Ltda"}], marca="nova"); self.assertTrue(r["ok"])
        marca_tela = self.pedir("GET", "/regras")["marca"]
        self.assertTrue(self.salvar({}, [{"nome": "Empresa Fictícia A Ltda"}, {"nome": "Empresa Fictícia B Ltda"}])["ok"])  # outro computador
        r = self.salvar({}, [], marca=marca_tela)
        self.assertFalse(r["ok"]); self.assertTrue(r.get("mudou"))
        self.assertEqual(len(self.exclusoes_no_disco()), 2)

    def test_copia_antes_de_salvar(self):
        from lexsuite import armazenamento
        self.assertTrue(self.salvar({}, [{"nome": "Empresa Fictícia A Ltda"}], marca="nova")["ok"])
        r = self.salvar({}, [])
        self.assertTrue(r["ok"]); self.assertTrue(r["copia"].endswith(armazenamento.REGRAS))
        pasta = os.path.join(armazenamento.pasta_copias(self.base()), r["copia"])
        self.assertTrue(any(n.endswith(".xlsx") for n in os.listdir(pasta)))
        self.assertIn(r["copia"], [c["nome"] for c in armazenamento.copias(self.base())])

    def test_pedidos_ruins_nao_derrubam(self):
        marca = self.pedir("GET", "/regras")["marca"]
        for cru in ("{}", "null", "[]", "", '{"valores": {}}', '{"exclusoes": []}', '{"valores": [], "exclusoes": [], "marca": "nova"}',
                    '{"valores": {}, "exclusoes": {}, "marca": "nova"}', '{"valores": {}, "exclusoes": [], "marca": 3}'):
            d = self.pedir("POST", "/regras", cru=cru)
            self.assertFalse(d.get("ok"), cru); self.assertIn(d["_status"], (400,), cru)
        for v in ("1e400", "Infinity", "-1e999", "inf", "NaN", "abc", None, [], {}):
            d = self.salvar({"valor_minimo": v, "minimo_acoes": v, "janela_dias": v}, [], marca=marca)
            self.assertTrue(d["ok"], (v, d)); marca = d["marca"]
        d = self.salvar({}, [{"nome": f"Fictícia {n}"} for n in range(5001)], marca=marca)
        self.assertFalse(d["ok"]); self.assertIn("5000", d["motivo"])

    def test_regras_sem_pasta(self):
        import threading, http.client, json as _j
        from lexsuite import app
        srv = app.Servidor(("127.0.0.1", 0), tempfile.mkdtemp())
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            c = http.client.HTTPConnection("127.0.0.1", srv.server_address[1], timeout=10)
            c.request("POST", "/regras", body="{}", headers={"X-LexSuite": "1", "Content-Type": "application/json"})
            r = _j.loads(c.getresponse().read()); c.close()
            self.assertFalse(r["ok"]); self.assertTrue(r["motivo_en"])
        finally:
            srv.shutdown(); srv.server_close()

    def test_regras_nao_diz_salvo_sem_planilha(self):
        from unittest import mock
        from lexsuite import compartilhar
        with mock.patch.object(compartilhar, "criar_se_faltar", return_value=None):  # a criação falhou sem erro
            r = self.salvar({}, [{"nome": "Empresa Fictícia Ltda"}], marca="nova")
        self.assertFalse(r["ok"])

    def test_datas_vazias(self):
        from lexsuite import config, avisar
        self.assertEqual(config.data_curta(None), ""); self.assertEqual(config.data_curta(""), "")
        self.assertEqual(avisar._data_br(None), ""); self.assertEqual(avisar._data_br("abc"), "")
        self.assertEqual(avisar._data_br("2026-11-06"), "06/NOV/2026")
        import datetime as _d
        self.assertEqual(config.data_curta(_d.date(999, 1, 2)), "02/JAN/0999")

_ROBO_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import json  # noqa: E402


class JaAberto0728(unittest.TestCase):
    """0.7.28 (dono): segundo clique no atalho não abre outra janela; a tela aberta avisa."""

    def test_segundo_clique_chama_a_tela_aberta(self):
        import threading, time, http.client
        from unittest import mock
        from lexsuite import app
        pasta = tempfile.mkdtemp()
        shutil.copy(os.path.join(_ROBO_, "radar_modelo.html"), pasta)
        srv = app.Servidor(("127.0.0.1", 0), pasta)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            porta = srv.server_address[1]
            srv.ultimo_pedido = time.monotonic() - 999  # ninguém olhando a tela
            self.assertEqual(app.procurar_aberto([porta], detalhe=True), (f"http://127.0.0.1:{porta}/", False))
            self.assertLess(srv.ultimo_pedido, time.monotonic() - 900)  # a sonda não conta como tela aberta
            def estado():
                c = http.client.HTTPConnection("127.0.0.1", porta, timeout=10)
                c.request("GET", "/estado", headers={"X-LexSuite": "1"})
                d = json.loads(c.getresponse().read()); c.close(); return d
            estado()  # a tela pergunta: agora está ativa
            self.assertTrue(app.procurar_aberto([porta], detalhe=True)[1])
            with mock.patch.object(app, "procurar_aberto", return_value=(f"http://127.0.0.1:{porta}/", True)), \
                    mock.patch.object(app, "tela_atendeu", return_value=True), \
                    mock.patch.object(app, "abrir_janela") as abrir, mock.patch("time.sleep"):
                ditos = []
                app.servir(pasta, aviso=ditos.append)
            abrir.assert_not_called()
            self.assertIn("já está aberto", " ".join(ditos))
            self.assertTrue(estado().get("chamado"))   # a tela recebe o aviso uma vez
            self.assertFalse(estado().get("chamado"))
            # 0.7.29 (dono): janela fechada no X: ninguém atende o chamado, e o segundo clique abre a tela de novo
            url = f"http://127.0.0.1:{porta}/"
            self.assertTrue(app.chamar_tela(url))
            self.assertFalse(app.tela_atendeu(url, espera_s=0.5, dormir=lambda s_: None))
            pare = threading.Event()
            def tela_viva():
                while not pare.is_set():
                    estado(); pare.wait(0.05)
            th = threading.Thread(target=tela_viva); th.start()
            try:
                self.assertTrue(app.tela_atendeu(url, espera_s=3, dormir=time.sleep if not isinstance(time.sleep, mock.Mock) else None))
            finally:
                pare.set(); th.join()
            c = http.client.HTTPConnection("127.0.0.1", porta, timeout=10)  # pagehide: a tela avisa que fechou
            c.request("POST", "/tela-fechada", body="{}", headers={"X-LexSuite": "1", "Content-Type": "application/json"})
            c.getresponse().read(); c.close()
            self.assertFalse(app.procurar_aberto([porta], detalhe=True)[1])
        finally:
            srv.shutdown(); srv.server_close()

    def test_tela_avisa(self):
        h = open(os.path.join(_ROBO_, "radar_modelo.html"), encoding="utf-8").read()
        self.assertIn("e.chamado", h)
        self.assertEqual(h.count("ja_aberto:"), 2)


def _regras_util(nome):
    return getattr(Regras0728, nome)


class V0729(unittest.TestCase):
    """0.7.29 (dono: sem janela preta) e ressalvas da segunda revisão da 0.7.28."""
    setUp = _regras_util("setUp"); tearDown = _regras_util("tearDown"); pedir = _regras_util("pedir")
    base = _regras_util("base"); arquivo = _regras_util("arquivo"); salvar = _regras_util("salvar")
    exclusoes_no_disco = _regras_util("exclusoes_no_disco")

    # --- sem janela preta ---
    def test_registro_grava_e_gira(self):
        import lexsuite_robo as lr
        from unittest import mock
        d = tempfile.mkdtemp(); arq = os.path.join(d, "saida", "registro.txt")
        with mock.patch.object(lr, "REGISTRO_MAX", 50):
            r = lr.Registro(arq, None)
            for i in range(30):
                r.write(f"linha {i:02d} da leitura\n")
        self.assertTrue(os.path.exists(arq)); self.assertTrue(os.path.exists(arq[:-4] + "-1.txt"))
        self.assertFalse(os.path.exists(arq[:-4] + "-3.txt"))  # no máximo 3 arquivos
        self.assertIn("linha 29", lr.ultimas_linhas_registro(5, arq))

    def test_erro_vai_para_o_registro_e_para_a_caixa(self):
        import lexsuite_robo as lr
        from unittest import mock
        from lexsuite import agendar
        d = tempfile.mkdtemp(); arq = os.path.join(d, "registro.txt")
        velho_out, velho_err = sys.stdout, sys.stderr
        try:
            with mock.patch.object(lr, "REGISTRO", arq), mock.patch.object(lr, "cmd_app", side_effect=RuntimeError("porta presa")), \
                    mock.patch.object(lr, "sem_console", return_value=True), mock.patch.object(agendar, "caixa_erro") as caixa:
                self.assertEqual(lr.main(["app"]), 1)
        finally:
            sys.stdout, sys.stderr = velho_out, velho_err
        texto = open(arq, encoding="utf-8").read()
        self.assertIn("RuntimeError: porta presa", texto); self.assertIn("· app · versão", texto)
        caixa.assert_called_once(); self.assertIn("registro.txt", caixa.call_args[0][1])

    def test_tarefa_chama_o_pythonw_sem_bat(self):
        from lexsuite import agendar
        pasta = tempfile.mkdtemp(); os.makedirs(os.path.join(pasta, "python"))
        bat = os.path.join(pasta, "RODAR.bat")
        self.assertIsNone(agendar.acao_oculta(pasta))
        self.assertIn(f"<Command>{bat}</Command><Arguments>--agendado</Arguments>", agendar.xml_tarefa(bat, ["20:00"]))
        open(os.path.join(pasta, "python", "pythonw.exe"), "wb").close()
        oc = agendar.acao_oculta(pasta)
        x = agendar.xml_tarefa(bat, ["20:00"], oculta=oc)
        self.assertIn("pythonw.exe</Command>", x); self.assertIn("lexsuite_robo.py&quot; radar --agendado</Arguments>", x)
        self.assertNotIn("RODAR.bat", x)
        self.assertTrue(agendar.comando_da_tarefa(agendar.xml_tarefa(bat, ["20:00"])).endswith("RODAR.bat"))
        self.assertTrue(agendar.comando_da_tarefa(x).endswith("pythonw.exe"))

    def test_migra_a_tarefa_antiga_pelo_xml(self):
        """Revisão: o XML do schtasks é igual em qualquer idioma do Windows (e vem em UTF-16)."""
        from unittest import mock
        from types import SimpleNamespace
        from lexsuite import agendar
        pasta = tempfile.mkdtemp(); os.makedirs(os.path.join(pasta, "python"))
        open(os.path.join(pasta, "python", "pythonw.exe"), "wb").close()
        bat = os.path.join(pasta, "RODAR.bat")
        velha = agendar.xml_tarefa(bat, ["20:00", "08:00"]).encode("utf-16")
        nova = agendar.xml_tarefa(bat, ["20:00"], oculta=agendar.acao_oculta(pasta)).encode("utf-16")
        lista = '"\\LexSuiteONE Radar","11/11/2026 20:00:00","Pronto"\r\n"\\Outra","N/A","Pronto"\r\n'.encode("cp850")
        def rodar_falso(xml):
            def f(args, **k):
                return SimpleNamespace(returncode=0, stdout=xml if "/xml" in args else lista, stderr=b"")
            return f
        with mock.patch.object(agendar, "disponivel", return_value=True), mock.patch.object(agendar.subprocess, "run", side_effect=rodar_falso(velha)), \
                mock.patch.object(agendar, "agendar", return_value=(True, "Agendado")) as ag:
            self.assertEqual(agendar.migrar_para_oculta(pasta, {"radar": {"horarios": ["20:00"]}}), "Agendado")
        ag.assert_called_once()
        with mock.patch.object(agendar, "disponivel", return_value=True), mock.patch.object(agendar.subprocess, "run", side_effect=rodar_falso(nova)), \
                mock.patch.object(agendar, "agendar", return_value=(True, "Agendado")) as ag:
            self.assertEqual(agendar.migrar_para_oculta(pasta, {}), "")
        ag.assert_not_called()

    def test_bats_sem_janela(self):
        def ler(n):
            b = open(os.path.join(_ROBO_, n), "rb").read(); self.assertNotIn(b"\n", b.replace(b"\r\n", b"")); return b.decode()
        a, r, d = ler("ABRIR.bat"), ler("RODAR.bat"), ler("DIAGNOSTICO.bat")
        self.assertIn('start "" "%PYW%" lexsuite_robo.py app', a); self.assertIn('"--ver"', a)
        self.assertIn('start "" "%PYW%" lexsuite_robo.py radar --agendado', r)
        self.assertIn("lexsuite_robo.py parar", d)

    def test_encerrar_a_tela_aberta(self):
        import threading as _th
        from lexsuite import app
        porta = self.srv.server_address[1]
        app.gravar_pid(self.pasta, porta)
        ditos = []
        import time as _tm
        self.assertTrue(app.encerrar_aberto(self.pasta, aviso=ditos.append, dormir=lambda s: _tm.sleep(min(s, 0.3)), portas=[porta]))
        import time as _t
        for _ in range(40):
            if not app.procurar_aberto([porta]):
                break
            _t.sleep(0.1)
        self.assertEqual(app.procurar_aberto([porta]), "")
        self.assertIn("encerrada", " ".join(ditos))

    def test_ver_registro(self):
        os.makedirs(os.path.join(self.pasta, "saida"), exist_ok=True)
        with open(os.path.join(self.pasta, "saida", "registro.txt"), "w", encoding="utf-8") as f:
            f.write("20:39:36  Radar: lista de distribuição\n")
        d = self.pedir("GET", "/registro")
        self.assertIn("Radar: lista", d["texto"]); self.assertTrue(d["caminho"].endswith("registro.txt"))

    # --- ressalvas da segunda revisão da 0.7.28 ---
    def test_regras_recusadas_durante_a_leitura(self):
        marca = self.pedir("GET", "/regras")["marca"]
        self.assertTrue(self.srv.estado.comecar())
        try:
            r = self.salvar({}, [{"nome": "Empresa Fictícia Ltda"}], marca=marca)
        finally:
            self.srv.estado.terminar({"lidas": 0, "novas": 0})
        self.assertFalse(r["ok"]); self.assertTrue(r.get("lendo")); self.assertTrue(r["motivo_en"])
        self.assertTrue(self.salvar({}, [{"nome": "Empresa Fictícia Ltda"}], marca=marca)["ok"])

    def test_leitura_espera_as_regras(self):
        import threading as _th
        from lexsuite import app, radar
        self.assertIs(app._TRAVA_REGRAS, radar.TRAVA_REGRAVAR)
        tomou, soltar = _th.Event(), _th.Event()
        def outra():  # outra thread gravando a planilha (Salvar regras, Gravar a planilha agora, limpeza)
            with radar.TRAVA_REGRAVAR:
                tomou.set(); soltar.wait(10)
        th = _th.Thread(target=outra); th.start(); tomou.wait(5)
        try:
            self.assertFalse(self.srv.rodar())
            r = self.pedir("POST", "/rodar", {})
            self.assertFalse(r["ok"]); self.assertIn("gravad", r["motivo"])
        finally:
            soltar.set(); th.join()

    def test_copia_que_falha_ou_planilha_que_muda_durante_a_copia(self):
        from unittest import mock
        from lexsuite import armazenamento, planilha
        self.assertTrue(self.salvar({}, [{"nome": "Empresa Fictícia A Ltda"}], marca="nova")["ok"])
        with mock.patch.object(armazenamento, "copia_antes_das_regras", return_value=(False, "Disco cheio.")):
            r = self.salvar({}, [])
        self.assertFalse(r["ok"]); self.assertEqual(self.exclusoes_no_disco(), ["Empresa Fictícia A Ltda"])
        marca = self.pedir("GET", "/regras")["marca"]
        real = armazenamento.copia_antes_das_regras
        def copia_e_outro_pc_salva(base, *a, **k):
            ok = real(base, *a, **k)
            planilha.liberar_escrita(self.arquivo())
            from lexsuite import compartilhar
            compartilhar.gravar_radar  # noqa: B018 - só para lembrar: outro computador regravou as abas
            from lexsuite import preferencias
            pref, exc = preferencias.linhas_regras({}, [{"nome": "Empresa Fictícia B Ltda"}])
            doc = planilha.ler_xlsx(self.arquivo())
            for aba in doc["abas"]:
                if aba["nome"] == "Exclusões":
                    aba["linhas"] = exc
            planilha.escrever_xlsx(self.arquivo(), doc["abas"])
            return ok
        with mock.patch.object(armazenamento, "copia_antes_das_regras", side_effect=copia_e_outro_pc_salva):
            r = self.salvar({}, [], marca=marca)
        self.assertFalse(r["ok"]); self.assertTrue(r.get("mudou"))
        self.assertEqual(self.exclusoes_no_disco(), ["Empresa Fictícia B Ltda"])

    def test_poda_e_copias_no_mesmo_segundo(self):
        import datetime as _d
        from lexsuite import armazenamento
        self.assertTrue(self.salvar({}, [], marca="nova")["ok"])
        base = self.base()
        outra = os.path.join(armazenamento.pasta_copias(base), "2026-01-01 10h00m00 - antes de limpar"); os.makedirs(outra)
        t = _d.datetime(2026, 11, 11, 9, 0, 0)
        nomes = [os.path.basename(armazenamento.copia_antes_das_regras(base, aviso=lambda *_: None, agora=t)[1]) for _ in range(8)]
        self.assertEqual(len(set(nomes[:6])), 6)  # o mesmo segundo não sobrescreve (depois da 6ª, a poda libera o nome mais velho)
        regras = [c["nome"] for c in armazenamento.copias(base) if c["nome"].endswith(armazenamento.REGRAS)]
        self.assertEqual(len(regras), armazenamento.COPIAS_GUARDADAS)
        self.assertTrue(os.path.isdir(outra))  # as das regras não empurram as outras

    def test_inteiros_e_saude_e_mes_em_ingles(self):
        from lexsuite import preferencias, saude, config
        pref, _ = preferencias.linhas_regras({"minimo_acoes": 2.5, "janela_dias": 10, "valor_minimo": 150500.5}, [])
        v = {preferencias.CHAVES[l[0]]: l[1] for l in pref[1:]}
        self.assertEqual(v["minimo_acoes"], preferencias.PADRAO["minimo_acoes"]); self.assertEqual(v["janela_dias"], 10)
        self.assertEqual(v["valor_minimo"], 150500.5)
        r = saude.avaliar([], [], hoje=__import__("datetime").date(2026, 11, 10), ja_conferidos=4)
        self.assertEqual(r[0]["situacao"], "ok")
        self.assertEqual(saude.avaliar([], [], hoje=__import__("datetime").date(2026, 11, 10))[0]["situacao"], "atenção")
        self.assertEqual(config.data_curta("2026-02-03", False, en=True), "03/FEB")

    def test_tela_0729(self):
        h = open(os.path.join(_ROBO_, "radar_modelo.html"), encoding="utf-8").read()
        self.assertNotIn("janela preta", h.split('<script id="assistone-master">')[0].lower().replace("sem janela preta", ""))
        self.assertEqual(h.count("ver_registro:"), 2)
        self.assertIn("snapC = estadoConfig(); fecharConfig();", h)
        self.assertIn("if (nNome.value.trim()) bAdd.click();", h)
        import re
        self.assertFalse(re.search(r"\n[ \t]+\n[ \t]+[a-z_0-9]+: \"", h))


class V0729Revisao(unittest.TestCase):
    """Revisão da Operação da 0.7.29 (bloqueio: encerrar processo alheio) e itens 2 a 13; 0.7.30: pizza no Painel."""

    def test_leitura_noutro_processo_nao_e_encerrada_a_forca(self):
        import subprocess as sp, json as _j, datetime as _d
        from lexsuite import app
        pasta = tempfile.mkdtemp(); os.makedirs(os.path.join(pasta, "saida"))
        alheio = sp.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            with open(os.path.join(pasta, "saida", "leitura.json"), "w", encoding="utf-8") as f:
                _j.dump({"rodando": True, "pid": alheio.pid, "batida": _d.datetime.now().isoformat()}, f)
            ditos = []
            self.assertTrue(app.encerrar_aberto(pasta, aviso=ditos.append, dormir=lambda s: None, portas=[1]))
            self.assertIsNone(alheio.poll())  # o processo alheio continua vivo
            self.assertTrue(os.path.exists(os.path.join(pasta, "saida", "parar.json")))  # só o pedido de parada
            self.assertIn("ponto seguro", " ".join(ditos))
        finally:
            alheio.kill(); alheio.wait()

    def test_programa_pid_de_processo_alheio_nao_e_encerrado(self):
        import subprocess as sp, json as _j
        from lexsuite import app
        pasta = tempfile.mkdtemp(); os.makedirs(os.path.join(pasta, "saida"))
        alheio = sp.Popen(["sleep", "30"]) if shutil.which("sleep") else sp.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            with open(os.path.join(pasta, "saida", "programa.pid"), "w", encoding="utf-8") as f:
                _j.dump({"pid": alheio.pid, "porta": 1}, f)
            ditos = []
            app.encerrar_aberto(pasta, aviso=ditos.append, dormir=lambda s: None, portas=[1])
            self.assertIsNone(alheio.poll())
        finally:
            alheio.kill(); alheio.wait()

    def test_saude_com_tribunal_fora_do_ar_continua_alarmando(self):
        import datetime as _d
        from lexsuite import radar, saude
        ruim = [{"tribunal": "TRT2", "causa": "fora_do_ar", "ja_conferidos": 0}, {"tribunal": "TRT4", "causa": "ok", "ja_conferidos": 2}]
        bom = [{"tribunal": "TRT2", "causa": "ok", "ja_conferidos": 1}, {"tribunal": "TRT4", "causa": "ainda_nao_liberado_3h", "ja_conferidos": 2}]
        self.assertEqual(radar.ja_conferidos_para_saude(ruim), 0); self.assertEqual(radar.ja_conferidos_para_saude(bom), 3)
        hoje = _d.date(2026, 11, 10)
        self.assertEqual(saude.avaliar([], [], hoje=hoje, ja_conferidos=radar.ja_conferidos_para_saude(ruim))[0]["situacao"], "atenção")
        self.assertEqual(saude.avaliar([], [], hoje=hoje, ja_conferidos=radar.ja_conferidos_para_saude(bom))[0]["situacao"], "ok")

    def test_agendar_cria_a_tarefa_com_o_pythonw(self):
        from unittest import mock
        from lexsuite import agendar
        pasta = tempfile.mkdtemp(); os.makedirs(os.path.join(pasta, "python"))
        open(os.path.join(pasta, "python", "pythonw.exe"), "wb").close(); open(os.path.join(pasta, "RODAR.bat"), "w").close()
        vistos = []
        def rodar(args):
            if "/xml" in args:
                vistos.append(open(args[args.index("/xml") + 1], encoding="utf-16").read())
            return True, ""
        with mock.patch.object(agendar, "disponivel", return_value=True), mock.patch.object(agendar, "_apagar_tudo"), \
                mock.patch.object(agendar, "_rodar", side_effect=rodar):
            self.assertTrue(agendar.agendar(pasta, ["20:00"], "todos")[0])
        self.assertIn("pythonw.exe</Command>", vistos[0]); self.assertNotIn("RODAR.bat", vistos[0])

    def test_registro_aceita_bytes_e_mascara_o_diagnostico(self):
        import lexsuite_robo as lr
        d = tempfile.mkdtemp(); arq = os.path.join(d, "registro.txt")
        r = lr.Registro(arq, None); r.write(b"linha em bytes\n")
        self.assertIn("linha em bytes", open(arq, encoding="utf-8").read())
        m = lr.mascarar_registro(r"Página: C:\Users\Fulano de Tal\LexSuiteONE\saida e fulano@exemplo.com.br")
        self.assertNotIn("Fulano", m); self.assertNotIn("@", m)

    def test_painel_barras_ou_pizza(self):
        h = open(os.path.join(_ROBO_, "radar_modelo.html"), encoding="utf-8").read()
        self.assertIn("function grafPizza(", h); self.assertIn("lexsuite:graf-tipo", h)
        self.assertEqual(h.count("g_pizza:"), 2); self.assertEqual(h.count("grade.appendChild(grafLinhas("), 8)
        self.assertIn("function mesCurto(", h); self.assertNotIn('m.mes.slice(5) + "/"', h)
        self.assertIn("pizza", open(os.path.join(_ROBO_, "testes", "tela", "larguras.js"), encoding="utf-8").read())
