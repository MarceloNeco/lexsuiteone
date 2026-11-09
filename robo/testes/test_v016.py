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
        arquivo = [a for a in doc["abas"] if a["nome"] == "Arquivo"][0]["linhas"]
        self.assertEqual(len(arquivo) - 2, 5)  # aviso + cabeçalho + 5 ações
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


if __name__ == "__main__":
    unittest.main()
