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
        self.assertIn("parou", r)
        self.assertEqual(h.situacao(b)["erros"], 0)
        self.assertEqual(h.situacao(b)["na_fila"], 20)

    def test_estatistica_antiga_de_outro_tribunal_fica(self):
        from lexsuite import banco as bd
        b = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db"))
        b.con.execute("INSERT INTO estatisticas_diarias VALUES ('2026-11-06','TRT3','1ª Vara','trabalhista','','',7,0,'x')")
        b.guardar_lead({"processo": "1", "tribunal": "TRT2", "vara": "1ª Vara", "empresas": ["X Fictícia Ltda"], "data_publicacao": "2026-11-06"}, "2026-11-06")
        b.atualizar_estatisticas()
        self.assertEqual(sum(e["novas"] for e in b.estatisticas() if e["tribunal"] == "TRT3"), 7)


if __name__ == "__main__":
    unittest.main()
