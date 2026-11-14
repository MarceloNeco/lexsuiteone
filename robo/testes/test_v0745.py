"""0.7.45 (dono, 13/Nov): a tela aberta lê sozinha quando a hora marcada passa sem leitura (antivírus impedindo a tarefa
do Windows) e os 5 ajustes da Arquitetura no "Trazer dados da área logada" (prompt v2 do PJe)."""

import datetime as dt
import os
import sys
import tempfile
import unittest
from unittest import mock

_ROBO_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROBO_)

from lexsuite import app, banco as bd, contatos, radar  # noqa: E402

with open(os.path.join(_ROBO_, "radar_modelo.html"), encoding="utf-8") as _f:
    HTML = _f.read()

CFG = {"radar": {"horarios": ["08:00", "20:00"], "dias": "uteis", "tribunais": ["TRT2"]}}
SEXTA_0830 = dt.datetime(2026, 11, 13, 8, 30)


class HorarioPerdido(unittest.TestCase):
    def test_hora_passou_sem_leitura(self):
        self.assertEqual(app.horario_perdido(CFG, "2026-11-12T20:01:10", SEXTA_0830), dt.datetime(2026, 11, 13, 8, 0))

    def test_leu_depois_da_hora(self):
        self.assertIsNone(app.horario_perdido(CFG, "2026-11-13T08:02:00", SEXTA_0830))

    def test_espera_a_folga_de_10_minutos(self):
        self.assertIsNone(app.horario_perdido(CFG, "2026-11-12T20:01:10", dt.datetime(2026, 11, 13, 8, 5)))

    def test_dia_sem_leitura_marcada(self):
        sabado = dt.datetime(2026, 11, 14, 9, 0)  # "uteis": sábado não tem; o das 20h de sexta já passou de 12 horas
        self.assertIsNone(app.horario_perdido(CFG, "2026-11-13T08:02:00", sabado))

    def test_vaga_de_ontem_a_noite(self):
        self.assertEqual(app.horario_perdido(CFG, "2026-11-12T08:01:00", dt.datetime(2026, 11, 13, 1, 0)), dt.datetime(2026, 11, 12, 20, 0))


class EstadoFalso:
    rodando = False


class ServidorFalso:
    def __init__(self, pasta, cfg):
        self.caminho_db = os.path.join(pasta, "lexsuite.db")
        self.arquivo_andamento = os.path.join(pasta, "saida", "leitura.json")
        self.estado, self.cfg, self.origens = EstadoFalso(), cfg, []
        bd.Banco(self.caminho_db).con.close()

    def config(self):
        return self.cfg

    def rodar(self, dias=None, origem="botão"):
        self.origens.append(origem)
        return True


class ConferirAgenda(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.mkdtemp()

    def leitura_anterior(self, s):
        b = bd.Banco(s.caminho_db)
        try:
            b.con.execute("INSERT INTO execucoes VALUES (?,?,?)", ("2026-11-12T20:01:10", "radar", "{}"))
            b.con.commit()
        finally:
            b.con.close()

    def test_instalacao_nova_nao_le_ao_abrir(self):
        s = ServidorFalso(self.pasta, {"radar": dict(CFG["radar"], agendar_quer=True)})
        self.assertIsNone(app.conferir_agenda(s, SEXTA_0830))
        self.assertEqual(s.origens, [])

    def test_desligada_confere_o_windows_uma_vez_por_horario(self):
        s = ServidorFalso(self.pasta, {"radar": dict(CFG["radar"], agendar_quer=False)})
        self.leitura_anterior(s)
        with mock.patch.object(app.agendar, "disponivel", return_value=True), mock.patch.object(app.agendar, "agendado", return_value=False) as ag:
            app.conferir_agenda(s, SEXTA_0830)
            app.conferir_agenda(s, SEXTA_0830 + dt.timedelta(minutes=1))
        self.assertEqual(ag.call_count, 1)

    def test_le_uma_vez_por_horario_quando_ligada(self):
        cfg = {"radar": dict(CFG["radar"], agendar_quer=True)}
        s = ServidorFalso(self.pasta, cfg)
        self.leitura_anterior(s)
        with mock.patch.object(app.agendar, "disponivel", return_value=False):
            self.assertEqual(app.conferir_agenda(s, SEXTA_0830), dt.datetime(2026, 11, 13, 8, 0))
            self.assertIsNone(app.conferir_agenda(s, SEXTA_0830 + dt.timedelta(minutes=1)))  # o mesmo horário não lê de novo
        self.assertEqual(s.origens, ["tela (horário das 08:00)"])

    def test_desligada_nao_le(self):
        s = ServidorFalso(self.pasta, {"radar": dict(CFG["radar"], agendar_quer=False)})
        self.leitura_anterior(s)
        with mock.patch.object(app.agendar, "disponivel", return_value=True), mock.patch.object(app.agendar, "agendado", return_value=False):
            self.assertIsNone(app.conferir_agenda(s, SEXTA_0830))
        self.assertEqual(s.origens, [])

    def test_tarefa_do_windows_existe_conta_como_ligada(self):
        s = ServidorFalso(self.pasta, CFG)
        self.leitura_anterior(s)
        with mock.patch.object(app.agendar, "disponivel", return_value=True), mock.patch.object(app.agendar, "agendado", return_value=True):
            self.assertIsNotNone(app.conferir_agenda(s, SEXTA_0830))

    def test_com_leitura_rodando_nao_le(self):
        s = ServidorFalso(self.pasta, {"radar": dict(CFG["radar"], agendar_quer=True)})
        s.estado.rodando = True
        self.assertIsNone(app.conferir_agenda(s, SEXTA_0830))

    def test_vigia_nao_derruba(self):
        s = ServidorFalso(self.pasta, CFG)
        s.config = mock.Mock(side_effect=RuntimeError("quebrou"))
        app.vigiar_agenda(s, dormir=lambda _s: None, vezes=2)

    def test_origem_vai_para_o_historico(self):
        import inspect
        self.assertIn("origem", inspect.signature(radar.executar).parameters)
        with open(os.path.join(_ROBO_, "lexsuite", "app.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn("parar=self.estado.parar, origem=origem)", src)
        self.assertIn('r["agendar_quer"] = bool(corpo["agendar"])', src)
        self.assertIn('name="vigiar-agenda"', src)


class Versao0745(unittest.TestCase):
    def test_versao_e_novidades(self):
        import re
        from lexsuite import VERSAO
        self.assertGreaterEqual(tuple(int(x) for x in VERSAO.split(".")), (0, 7, 45))  # a versão sobe
        bloco = HTML[HTML.index('"0.7.45": {'):HTML.index('"0.7.44": {')]
        pt = re.findall(r'"((?:[^"\\]|\\.)+)"', bloco[bloco.index("pt: ["):bloco.index("en: [")])
        en = re.findall(r'"((?:[^"\\]|\\.)+)"', bloco[bloco.index("en: ["):])
        self.assertEqual(len(pt), 5); self.assertEqual(len(en), 5)


class AreaLogadaV2(unittest.TestCase):
    PROCS = {"0001111-22.2026.5.02.0001": "Empresa Fictícia Ltda"}

    def test_pedido_traz_o_prompt_v2_por_tribunal(self):
        itens = [{"processo": "2", "tribunal": "TRT9", "empresas": ["B"]}, {"processo": "1", "tribunal": "TRT15", "empresas": ["A"]},
                 {"processo": "3", "tribunal": "TRT2", "empresas": ["C"]}]
        _, n, texto = contatos.preparar_v1(itens, tempfile.mkdtemp())
        self.assertEqual(n, 3)
        for trecho in ("Baixar processo completo", "Meus Expedientes", "Polo Passivo", "PJe dados do processo", "SJT-004",
                       "RESPOSTA PARA O RADAR v1", "outro tribunal"):
            self.assertIn(trecho, texto)
        corpo = texto[texto.index("## Processos"):]
        self.assertLess(corpo.index("| TRT15 |"), corpo.index("| TRT2 |"))
        self.assertLess(corpo.index("| TRT2 |"), corpo.index("| TRT9 |"))

    def colar(self, linhas):
        cab = "RESPOSTA PARA O RADAR v1\n| processo | dado | valor | resultado | fonte | data | observação |\n|---|---|---|---|---|---|---|\n"
        return contatos.colar_v1(cab + "\n".join(linhas), self.PROCS, hoje=dt.date(2026, 11, 13))

    def test_fonte_dados_do_processo_e_prioridade(self):
        r = self.colar(["| 0001111-22.2026.5.02.0001 | endereco | Rua A, 10, São Paulo/SP | encontrado | PJe petição inicial | 2026-11-13 | a conferir |",
                        "| 0001111-22.2026.5.02.0001 | endereco | Av. B, 20, São Paulo/SP | encontrado | PJe dados do processo | 2026-11-13 | |",
                        "| 0001111-22.2026.5.02.0001 | email | contato@empresaficticia.com.br | encontrado | PJe dados do processo | 2026-11-13 | |"])
        self.assertEqual(r["recusadas"], [])
        conf = {c["valor"]: c["confianca"] for c in r["contatos"]}
        self.assertEqual(conf["Rua A, 10, São Paulo/SP"], "baixa")  # da petição, "a conferir"
        self.assertEqual(conf["Av. B, 20, São Paulo/SP"], "alta")  # cadastro da parte
        self.assertIn("PJe dados do processo", contatos.FONTES)

    def test_ficha_mostra_o_cadastro_primeiro(self):
        lead = {"processo": "P1", "empresas": ["X"]}
        ext = {"P1": [{"canal": "endereco", "valor": "Rua A", "fonte": "PJe petição inicial", "data": "2026-11-13", "confianca": "baixa",
                       "origem": "área logada", "de_pessoa": False, "validacao": ""},
                      {"canal": "endereco", "valor": "Av. B", "fonte": "PJe dados do processo", "data": "2026-11-13", "confianca": "alta",
                       "origem": "área logada", "de_pessoa": False, "validacao": ""}]}
        item = radar.item_de_lead(lead, {"teto_capital_gigante": 0}, ext)
        self.assertEqual([c["valor"] for c in item["contatos"]], ["Av. B", "Rua A"])

    def test_tela(self):
        # 0.7.46: a janela antiga de colar (com o texto das colunas) foi trocada pelos 4 passos da área logada
        self.assertNotIn("(8 colunas)", HTML)
        self.assertEqual(HTML.count("ct_a_conferir:"), 2)
        self.assertIn('(c.confianca === "baixa" ? ", " + t("ct_a_conferir") : "")', HTML)


if __name__ == "__main__":
    unittest.main()
