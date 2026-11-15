"""0.7.48 ("produto aprovado, pode codar a 0.7.48", 15/Nov): leitura pela consulta pública quando o caderno cai (desenho 1.3,
decisão 37), limpeza automática do banco (decisões 40 a 42), filtro de cidade, faixa com ações embaixo, 14 ajustes da área
logada e janelas arrastáveis. Dados FICTÍCIOS, sem internet."""

import datetime as dt
import http.client
import json
import os
import re
import sys
import tempfile
import threading
import unittest
import urllib.parse
from unittest import mock

_ROBO_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RAIZ_ = os.path.dirname(_ROBO_)
sys.path.insert(0, _ROBO_)

from lexsuite import VERSAO, app, banco as bd, conta, djen, monitor, radar, rede  # noqa: E402

with open(os.path.join(_ROBO_, "radar_modelo.html"), encoding="utf-8") as _f:
    HTML = _f.read()

HOJE = dt.date(2026, 11, 16)  # segunda-feira
DIA = dt.date(2026, 11, 13)   # sexta: o caderno caiu


def item(i, proc, vara="1ª Vara do Trabalho de Campinas (fictícia)", org="101", data=DIA):
    """Uma comunicação no formato da consulta pública (fictícia)."""
    return {"id": i, "siglaTribunal": "TRT15", "numeroprocessocommascara": proc, "nomeOrgao": vara, "idOrgao": org,
            "tipoComunicacao": "Lista de distribuição", "data_disponibilizacao": data.isoformat(),
            "nomeClasse": "AÇÃO TRABALHISTA - RITO ORDINÁRIO", "destinatarios": [{"nome": f"EMPRESA FICTICIA {i} LTDA", "polo": "P"}],
            "texto": "Distribuído", "link": ""}


def proc(k):
    return f"00100{k:02d}-11.2026.5.15.0001"


SONDA_OK = {"solverone": {"ok": True}, "consulta": {"ok": True}}


class Cenario:
    """Caderno do TRT15 com 503 no dia DIA (fase "fora") ou de volta (fase "ok"); a consulta pública responde 3 processos."""

    def __init__(self):
        self.fase, self.pedidos = "fora", []
        self.no_caderno = [proc(k) for k in range(1, 5)]   # o caderno tem 4 processos
        self.na_consulta = [proc(k) for k in range(1, 4)]  # a consulta trouxe 3

    def meta(self, sigla, data, aviso, motivos, tentativas=5):
        if data == HOJE.isoformat():
            motivos[data] = "nao_publicado"
            return None
        if self.fase == "fora" and data == DIA.isoformat():
            raise rede.ErroHTTP(503, "https://x/caderno", "Service Unavailable", {"ms": 1})
        return {"versao": "1", "url": "x"}

    def baixar(self, sigla, data, diag, aviso, meta=None):
        if data == DIA.isoformat():
            return [djen.normalizar(item(k + 1, p)) for k, p in enumerate(self.no_caderno)]
        return []

    def pedir(self, url):
        self.pedidos.append(url)
        q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        if int(q["pagina"][0]) > 1:
            return {"count": len(self.na_consulta), "items": []}
        return {"count": len(self.na_consulta), "items": [item(k + 1, p) for k, p in enumerate(self.na_consulta)]}


class Base(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.mkdtemp()
        self.b = bd.Banco(os.path.join(self.pasta, "t.db"))
        self.addCleanup(self.b.con.close)
        self.c = Cenario()
        for alvo, f in (("meta_caderno", self.c.meta), ("baixar_caderno", self.c.baixar)):
            p = mock.patch.object(djen, alvo, f)
            p.start()
            self.addCleanup(p.stop)

    def ler(self, fora=False, sondas=SONDA_OK, tent=None):
        cons = {"fora": lambda: fora, "pedir": self.c.pedir}
        tent = [] if tent is None else tent
        pubs = monitor.coletar_caderno(["TRT15"], 1, self.b, aviso=lambda m: None, hoje=HOJE, tentativas=tent, consulta=cons,
                                       sondar=lambda: sondas)
        novos = radar.acoes_do_dia(pubs, 2026, self.b.processos_vistos())
        procs = set().union(*[x["processos"] for x in cons.get("lidos") or []]) if cons.get("lidos") else set()
        for n in novos:
            if n["processo"] in procs:
                n["fonte_leitura"], n["caderno_pendente"] = "consulta", True
            self.b.guardar_lead(n, HOJE.isoformat())
        return pubs, novos, cons, radar.registrar_consulta(self.b, cons, novos, dt.datetime(2026, 11, 16, 20, 9), "teste")


class LeituraPelaConsulta(Base):
    def test_caderno_fora_le_pela_consulta_e_marca_a_fonte(self):
        tent = []
        pubs, novos, _cons, info = self.ler(tent=tent)
        self.assertEqual(len(pubs), 3)
        self.assertEqual(info["consulta"]["novos"], 3)
        self.assertEqual(info["consulta"]["tribunais"], ["TRT15"])
        self.assertIn(DIA.isoformat(), self.b.cadernos_pendentes("TRT15"))  # o dia continua pendente: o caderno confere depois
        self.assertTrue(all(n["fonte_leitura"] == "consulta" and n["caderno_pendente"] for n in novos))
        self.assertIn("leu pela consulta pública (3 comunicações", tent[-1]["fez"])
        self.assertEqual(tent[-1]["consulta"], 3)
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.c.pedidos[0]).query)
        self.assertEqual((q["siglaTribunal"], q["itensPorPagina"], q["dataDisponibilizacaoInicio"], q["dataDisponibilizacaoFim"]),
                         (["TRT15"], ["100"], [DIA.isoformat()], [DIA.isoformat()]))
        h = [x for x in self.b.execucoes("consulta", 5)]
        self.assertEqual(h[0]["novos"], 3)

    def test_uma_vez_por_dia_pendente(self):
        self.ler()
        self.c.pedidos.clear()
        _pubs, _novos, cons, info = self.ler()
        self.assertEqual(self.c.pedidos, [])
        self.assertIsNone(cons.get("lidos"))
        self.assertNotIn("consulta", info)

    def test_caderno_volta_confere_sem_duplicar(self):
        self.ler()
        self.c.fase = "ok"
        _pubs, novos, _cons, info = self.ler()
        self.assertEqual([n["processo"] for n in novos], [proc(4)])  # só o que a consulta não trouxe
        self.assertEqual(info["conferencia"], {"hora": "20h09", "a_mais": 1, "tribunais": ["TRT15"]})
        self.assertNotIn(DIA.isoformat(), self.b.cadernos_pendentes("TRT15"))
        fontes = {p: json.loads(d).get("fonte_leitura") for p, d in self.b.con.execute("SELECT processo, dados FROM leads")}
        self.assertEqual([fontes[proc(k)] for k in (1, 2, 3)], ["caderno"] * 3)
        self.assertEqual(self.b.con.execute("SELECT count(*) FROM leads").fetchone()[0], 4)
        self.assertEqual(self.b.execucoes("conferencia", 1)[0]["a_mais"], 1)
        # a conferência acontece uma vez só
        self.b.con.execute("DELETE FROM cadernos")
        self.b.con.commit()
        _p, _n, _c, info2 = self.ler()
        self.assertNotIn("conferencia", info2)

    def test_conferencia_sem_falta(self):
        self.c.na_consulta = list(self.c.no_caderno)
        self.ler()
        self.c.fase = "ok"
        _p, novos, _c, info = self.ler()
        self.assertEqual(novos, [])
        self.assertEqual(info["conferencia"]["a_mais"], 0)

    def test_observador_ve_a_consulta_fora_nao_tenta(self):
        pubs, _n, _c, info = self.ler(fora=True)
        self.assertEqual(self.c.pedidos, [])
        self.assertEqual(info, {})
        self.assertIn(DIA.isoformat(), self.b.cadernos_pendentes("TRT15"))  # o caderno continua pendente

    def test_sonda_da_consulta_falhou_nao_tenta(self):
        pubs, _n, _c, info = self.ler(sondas={"solverone": {"ok": True}, "consulta": {"ok": False, "http": 500}})
        self.assertEqual(self.c.pedidos, [])
        self.assertEqual(pubs, [])
        self.assertEqual(info, {})

    def test_desligada_nao_tenta(self):
        monitor.coletar_caderno(["TRT15"], 1, self.b, aviso=lambda m: None, hoje=HOJE, tentativas=[], consulta=None, sondar=lambda: SONDA_OK)
        self.assertEqual(self.c.pedidos, [])

    def test_tudo_fora_mas_a_consulta_leu_nao_termina_em_erro(self):
        # todos os dias com 5xx: sem a consulta, a leitura terminaria em erro; com ela, devolve o que a consulta trouxe
        self.c.meta = lambda sigla, data, aviso, motivos, tentativas=5: (_ for _ in ()).throw(rede.ErroHTTP(503, "https://x", "x", {"ms": 1}))
        with mock.patch.object(djen, "meta_caderno", self.c.meta):
            pubs = monitor.coletar_caderno(["TRT15"], 1, self.b, aviso=lambda m: None, hoje=HOJE, tentativas=[],
                                           consulta={"fora": lambda: False, "pedir": self.c.pedir}, sondar=lambda: SONDA_OK)
        self.assertTrue(pubs)

    def test_interromper_no_meio_nao_marca_dia_como_lido(self):
        dias = [dt.date(2026, 11, 12), DIA]
        vez = []

        def consulta_dia(sigla, dia, **k):
            vez.append(dia)
            if len(vez) == 2:
                raise radar.Interrompida("interrompida")
            return [djen.normalizar(item(1, proc(1)))], {"pedidos": 1, "parcial": False, "varas": 0}
        with mock.patch.object(djen, "consulta_dia", consulta_dia), self.assertRaises(radar.Interrompida):
            monitor.ler_pela_consulta("TRT15", dias, self.b, {"fora": lambda: False}, lambda m: None, None, True)
        self.assertIsNone(self.b.consulta_do_dia("TRT15", DIA.isoformat()))  # nada marcado: a próxima leitura tenta de novo
        self.assertIsNone(self.b.consulta_do_dia("TRT15", "2026-11-12"))

    def test_dia_so_marcado_depois_de_gravar_e_sem_interromper(self):
        cons = {"fora": lambda: False, "pedir": self.c.pedir}
        monitor.coletar_caderno(["TRT15"], 1, self.b, aviso=lambda m: None, hoje=HOJE, tentativas=[], consulta=cons, sondar=lambda: SONDA_OK)
        self.assertTrue(cons.get("lidos"))
        self.assertIsNone(self.b.consulta_do_dia("TRT15", DIA.isoformat()))  # a coleta sozinha não marca
        radar.registrar_consulta(self.b, cons, [], dt.datetime(2026, 11, 16, 20, 0), "teste")
        self.assertIsNotNone(self.b.consulta_do_dia("TRT15", DIA.isoformat()))
        with open(os.path.join(_ROBO_, "lexsuite", "radar.py"), encoding="utf-8") as f:
            self.assertIn("registrar_consulta(banco, consulta, novos, agora, origem) if not interrompida else {}", f.read())

    def test_varas_guardadas_dos_cadernos(self):
        self.c.fase = "ok"
        self.ler()
        self.assertEqual(self.b.varas("TRT15"), [("101", "1ª Vara do Trabalho de Campinas (fictícia)")])


class ConsultaDia(unittest.TestCase):
    def test_paginas_ate_a_curta(self):
        urls = []

        def pedir(url):
            urls.append(url)
            pg = int(urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["pagina"][0])
            return {"count": 250, "items": [item(f"{pg}-{k}", proc(1)) for k in range(100 if pg < 3 else 50)]}
        pubs, info = djen.consulta_dia("TRT15", DIA.isoformat(), pedir=pedir, aviso=lambda m: None)
        self.assertEqual((len(pubs), info["pedidos"], info["parcial"]), (250, 3, False))
        self.assertTrue(all(p["fonte_leitura"] == "consulta" for p in pubs))

    def test_pagina_vazia_no_meio_tenta_mais_uma(self):
        def pedir(url):
            pg = int(urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["pagina"][0])
            return {"count": 250, "items": [] if pg == 2 else [item(f"{pg}-{k}", proc(1)) for k in range(100 if pg < 4 else 50)]}
        pubs, info = djen.consulta_dia("TRT15", DIA.isoformat(), pedir=pedir, aviso=lambda m: None)
        self.assertEqual(len(pubs), 250)

    def test_sem_count_segue_ate_a_pagina_curta(self):
        def pedir(url):
            pg = int(urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["pagina"][0])
            return {"items": [item(f"{pg}-{k}", proc(1)) for k in range(100 if pg < 2 else 7)]}
        pubs, _info = djen.consulta_dia("TRT15", DIA.isoformat(), pedir=pedir, aviso=lambda m: None)
        self.assertEqual(len(pubs), 107)

    def test_acima_de_dez_mil_vai_vara_por_vara(self):
        urls = []

        def pedir(url):
            urls.append(url)
            q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
            if "orgaoId" not in q:
                return {"count": 12000, "items": [item(f"x{k}", proc(1)) for k in range(100)]}
            org = q["orgaoId"][0]
            return {"count": 2, "items": [item(f"{org}-a", proc(2), org=org), item("comum", proc(3), org=org)]}
        avisos = []
        pubs, info = djen.consulta_dia("TRT2", DIA.isoformat(), varas=[("1", "1ª Vara"), ("2", "2ª Vara")], pedir=pedir, aviso=avisos.append)
        self.assertEqual(sum(1 for u in urls if "orgaoId" not in u), 1)  # parou na 1ª página e foi por vara
        self.assertEqual((info["varas"], len(pubs)), (2, 3))  # sem duplicar a comunicação que veio nas duas varas
        self.assertTrue(any("vara 2 de 2" in a for a in avisos))

    def test_acima_de_dez_mil_sem_varas_fica_parcial(self):
        def pedir(url):
            return {"count": 12000, "items": [item(f"x{k}-{url[-3:]}", proc(1)) for k in range(100)]}
        _pubs, info = djen.consulta_dia("TRT2", DIA.isoformat(), varas=[], pedir=pedir, aviso=lambda m: None)
        self.assertTrue(info["parcial"])

    def test_tres_tempos_esgotados_seguidos_param(self):
        n = []

        def pedir(url):
            n.append(url)
            raise rede.SemResposta(url, "timed out")
        with self.assertRaises(djen.ConsultaParou):
            djen.consulta_dia("TRT15", DIA.isoformat(), pedir=pedir, aviso=lambda m: None)
        self.assertEqual(len(n), 3)

    def test_cinco_erros_do_servidor_seguidos_param(self):
        n = []

        def pedir(url):
            n.append(url)
            raise rede.ErroHTTP(500, url, "Server Error")
        with self.assertRaises(djen.ConsultaParou):
            djen.consulta_dia("TRT15", DIA.isoformat(), pedir=pedir, aviso=lambda m: None)
        self.assertEqual(len(n), 5)  # não percorre as 100 páginas

    def test_resposta_que_nao_e_json_perde_so_a_pagina(self):
        def pedir(url):
            pg = int(urllib.parse.parse_qs(urllib.parse.urlparse(url).query)["pagina"][0])
            if pg == 1:
                raise ValueError("não é JSON")
            return {"count": 150, "items": [item(f"{pg}-{k}", proc(1)) for k in range(100 if pg == 2 else 0)]}
        pubs, info = djen.consulta_dia("TRT15", DIA.isoformat(), pedir=pedir, aviso=lambda m: None)
        self.assertTrue(info["parcial"])
        self.assertEqual(len(pubs), 100)

    def test_recusa_do_cnj_para_tudo_inclusive_as_outras_varas(self):
        for cod in (401, 403, 429):
            n = []

            def pedir(url, cod=cod):
                n.append(url)
                q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
                if "orgaoId" not in q:
                    return {"count": 12000, "items": []}
                raise rede.ErroHTTP(cod, url, "recusado")
            with self.assertRaises(djen.ConsultaParou):
                djen.consulta_dia("TRT2", DIA.isoformat(), varas=[("1", "a"), ("2", "b"), ("3", "c")], pedir=pedir, aviso=lambda m: None)
            self.assertEqual(len(n), 2, cod)  # 1ª página + a 1ª vara; as outras varas não são pedidas

    def test_recusa_cem_por_pagina_passa_a_cinquenta(self):
        tamanhos = []

        def pedir(url):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
            tamanhos.append(q["itensPorPagina"][0])
            if q["itensPorPagina"][0] == "100":
                raise rede.ErroHTTP(400, url, "itensPorPagina inválido")
            return {"count": 3, "items": [item(k, proc(k)) for k in range(1, 4)]}
        pubs, info = djen.consulta_dia("TRT15", DIA.isoformat(), pedir=pedir, aviso=lambda m: None)
        self.assertEqual((tamanhos, len(pubs), info["por_pagina"], info["parcial"]), (["100", "50"], 3, 50, False))

    def test_padrao_um_pedido_por_segundo_quinze_segundos(self):
        with mock.patch.object(rede, "pedir_json", return_value={"count": 0, "items": []}) as pj:
            djen.consulta_dia("TRT15", DIA.isoformat(), aviso=lambda m: None)
        k = pj.call_args.kwargs
        self.assertEqual((k["tentativas"], k["intervalo_minimo"], k["tempo_limite"]), (2, 1.0, 15))

    def test_interromper_para_a_consulta(self):
        with self.assertRaises(radar.Interrompida):
            djen.consulta_dia("TRT15", DIA.isoformat(), pedir=lambda u: {"count": 0, "items": []}, parar=lambda: True, aviso=lambda m: None)


class Observador(unittest.TestCase):
    def test_le_o_estado_da_consulta(self):
        self.assertTrue(conta.consulta_vista_fora({"ok": True, "estado": {"ok": 24, "fora": [], "consulta": {"tribunal": "TRT2", "estado": "fora"}}}))
        self.assertTrue(conta.consulta_vista_fora({"estado_cnj": {"consulta": {"estado": "fora"}}}))
        self.assertFalse(conta.consulta_vista_fora({"estado": {"consulta": {"estado": "lento"}}}))
        self.assertFalse(conta.consulta_vista_fora({"estado": {"consulta": None}}))
        self.assertFalse(conta.consulta_vista_fora(None))

    def test_sem_resposta_tenta(self):
        conta._ESTADO_CNJ.update({"em": None, "r": None, "consulta_fora": False})
        cfg = {"conta": {"codigo": "LEX-AAAA-BBBB", "instalacao": "x"}}
        with mock.patch.object(conta, "valido", return_value=True):
            self.assertFalse(conta.consulta_fora(cfg, VERSAO, pedir=lambda *a, **k: (_ for _ in ()).throw(OSError("sem internet"))))
        conta._ESTADO_CNJ.update({"em": None})
        with mock.patch.object(conta, "valido", return_value=True):
            self.assertTrue(conta.consulta_fora(cfg, VERSAO, pedir=lambda *a, **k: {"estado": {"ok": 24, "fora": [], "consulta": {"estado": "fora"}}}))
        conta._ESTADO_CNJ.update({"em": None, "r": None, "consulta_fora": False})

    def test_radar_liga_por_padrao_e_desliga_pela_opcao(self):
        vistos = []

        def coletar(*a, **k):
            vistos.append(k.get("consulta"))
            return []
        cfg = {"radar": {"tribunais": ["TRT2"]}, "conta": {}}
        b = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db"))
        self.addCleanup(b.con.close)
        with mock.patch.object(monitor, "coletar_caderno", coletar), mock.patch.object(conta, "verificar"), \
                mock.patch.object(conta, "bloqueio", return_value=""), mock.patch.object(radar.preferencias, "bloqueio", return_value=""):
            radar.executar(cfg, b, aviso=lambda m: None, versao=VERSAO)
            cfg["radar"]["consulta_publica"] = False
            radar.executar(cfg, b, aviso=lambda m: None, versao=VERSAO)
        self.assertTrue(callable(vistos[0]["fora"]))
        self.assertIsNone(vistos[1])


class AndamentoNaTela(unittest.TestCase):
    def test_estado_le_o_andamento_da_consulta(self):
        e = app.Estado()
        e.comecar()
        e.aviso("  Lendo pela consulta pública: TRT2 13/NOV (o caderno do CNJ está fora; 1 pedido por segundo)")
        e.aviso("  Consulta pública TRT2 13/NOV: vara 7 de 180")
        d = e.como_dict()["consulta"]
        self.assertEqual((d["tribunal"], d["dia"], d["vara"], d["varas"], d["fim"]), ("TRT2", "13/NOV", 7, 180, False))
        e.aviso("  Consulta pública TRT2 13/NOV: 2000 de 8120 comunicações")
        self.assertEqual((e.como_dict()["consulta"]["lidas"], e.como_dict()["consulta"]["total"]), (2000, 8120))
        e.aviso("  Consulta pública TRT2 13/NOV: 8120 comunicações em 82 pedidos")
        self.assertTrue(e.como_dict()["consulta"]["fim"])
        e.terminar()
        self.assertIsNone(e.como_dict()["consulta"])
        e.comecar()
        self.assertIsNone(e.como_dict()["consulta"])  # leitura nova começa sem o andamento da anterior


def _lead(b, k, primeira_vez, status="novo"):
    p = f"00200{k:02d}-11.2024.5.02.0001"
    b.guardar_lead({"processo": p, "tribunal": "TRT2", "vara": "1ª Vara (fictícia)", "empresas": [f"EMPRESA FICTICIA {k}"],
                    "data_publicacao": primeira_vez, "texto_curto": "texto do Diário fictício"}, primeira_vez)
    if status != "novo":
        b.mudar_situacao([p], status)
    return p


class Limpeza(unittest.TestCase):
    def setUp(self):
        self.b = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db"))
        self.addCleanup(self.b.con.close)

    def test_apaga_so_os_nao_trabalhados_antigos(self):
        velho, recente = (HOJE - dt.timedelta(days=800)).isoformat(), (HOJE - dt.timedelta(days=30)).isoformat()
        a = _lead(self.b, 1, velho)                     # novo, antigo: sai
        v = _lead(self.b, 2, velho, "visto")            # visto não conta como trabalhado: sai
        t = _lead(self.b, 3, velho, "em_analise")       # trabalhado: fica
        r = _lead(self.b, 4, recente)                   # recente: fica
        lp = self.b.limpeza_automatica(6, 24, hoje=HOJE)
        ficaram = {x[0] for x in self.b.con.execute("SELECT processo FROM leads")}
        self.assertEqual(ficaram, {t, r})
        self.assertEqual((lp["apagados"], lp["mantidos"]), (2, 1))
        self.assertTrue({a, v} <= self.b.processos_vistos())  # não voltam como novos
        self.assertEqual(self.b.con.execute("SELECT count(*) FROM processos_apagados").fetchone()[0], 2)

    def test_dado_digitado_na_ficha_nunca_sai(self):
        # bloqueio da revisão da Operação: lead antigo, Novo, sem contato nem motivo, só com o valor da causa digitado
        velho = (HOJE - dt.timedelta(days=800)).isoformat()
        p = _lead(self.b, 7, velho)
        self.b.completar(p, "valor_causa", 5000, "digitado")
        self.assertIn(p, self.b.trabalhados())
        lp = self.b.limpeza_automatica(6, 24, hoje=HOJE)  # resume (6 meses) e limpa (24) na mesma rodada
        self.assertEqual((lp["apagados"], lp["mantidos"]), (0, 1))
        d = json.loads(self.b.con.execute("SELECT dados FROM leads WHERE processo = ?", (p,)).fetchone()[0])
        self.assertEqual(str(d["manual"]["valor_causa"]["valor"]), "5000")  # o resumo guarda o digitado
        self.b.limpeza_automatica(6, 24, hoje=HOJE)  # e continua guardando nas limpezas seguintes
        self.assertEqual(self.b.con.execute("SELECT count(*) FROM leads WHERE processo = ?", (p,)).fetchone()[0], 1)

    def test_historico_do_digitado_fica_no_resumo(self):
        p = _lead(self.b, 8, (HOJE - dt.timedelta(days=400)).isoformat())
        self.b.completar(p, "valor_causa", 5000, "digitado")
        self.b.completar(p, "valor_causa", 7000, "digitado")
        ler = lambda: json.loads(self.b.con.execute("SELECT dados FROM leads WHERE processo = ?", (p,)).fetchone()[0])
        antes = ler()
        self.b.con.execute("UPDATE leads SET dados = ? WHERE processo = ?",  # garante um histórico, venha ou não da troca acima
                           (json.dumps(dict(antes, manual_historico=antes.get("manual_historico") or [{"campo": "valor_causa", "valor": 5000}])), p))
        self.b.con.commit()
        historico = ler()["manual_historico"]
        self.b.limpeza_automatica(6, 24, hoje=HOJE)
        d = ler()
        self.assertEqual(d.get("manual_historico"), historico)  # o resumo guarda o histórico do digitado
        self.assertEqual(str(d["manual"]["valor_causa"]["valor"]), "7000")

    def test_lead_sem_data_nao_e_apagado(self):
        p = _lead(self.b, 9, (HOJE - dt.timedelta(days=30)).isoformat())
        self.b.con.execute("UPDATE leads SET primeira_vez = '' WHERE processo = ?", (p,))
        self.b.con.commit()
        self.assertEqual(self.b.limpeza_automatica(6, 24, hoje=HOJE)["apagados"], 0)

    def test_apagar_zero_nunca_apaga(self):
        _lead(self.b, 1, (HOJE - dt.timedelta(days=900)).isoformat())
        lp = self.b.limpeza_automatica(6, 0, hoje=HOJE)
        self.assertEqual(lp["apagados"], 0)
        self.assertEqual(self.b.con.execute("SELECT count(*) FROM leads").fetchone()[0], 1)

    def test_prazos_com_as_regras(self):
        self.assertEqual(radar.prazos_limpeza({}), (6, 24))
        self.assertEqual(radar.prazos_limpeza({"resumir_meses": 0, "apagar_meses": 3}), (1, 6))
        self.assertEqual(radar.prazos_limpeza({"resumir_meses": 12, "apagar_meses": 8}), (12, 12))
        self.assertEqual(radar.prazos_limpeza({"apagar_meses": 0}), (6, 0))

    def test_registra_no_historico(self):
        radar.limpar_banco(self.b, {}, "depois da leitura")
        h = self.b.execucoes("limpeza", 1)[0]
        self.assertEqual((h["origem"], h["resumir_meses"], h["apagar_meses"]), ("depois da leitura", 6, 24))
        self.assertTrue(h["quando_local"])


CFG = {"conta": {"codigo": "LEX-ABCD-EFGH", "instalacao": "0123456789abcdef", "resposta": "ok", "ok": True, "ultima_ok": "2099-01-01"},
       "radar": {"tribunais": ["TRT2"]}}


class Rotas(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.mkdtemp()
        with open(os.path.join(self.pasta, "config.json"), "w", encoding="utf-8") as f:
            json.dump(CFG, f)
        self.srv = app.Servidor(("127.0.0.1", 0), self.pasta)
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.addCleanup(self.srv.server_close)
        self.addCleanup(self.srv.shutdown)

    def pedir(self, rota, corpo=None, metodo="POST"):
        c = http.client.HTTPConnection("127.0.0.1", self.srv.server_address[1], timeout=20)
        c.request(metodo, rota, body=json.dumps(corpo or {}) if metodo == "POST" else None, headers={"X-LexSuite": "1", "Content-Type": "application/json"})
        r = c.getresponse()
        d = json.loads(r.read())
        c.close()
        return d

    def cfg(self):
        with open(os.path.join(self.pasta, "config.json"), encoding="utf-8") as f:
            return json.load(f)

    def test_prazos_da_limpeza_validados(self):
        self.assertFalse(self.pedir("/config", {"resumir_meses": 12, "apagar_meses": 8})["ok"])
        self.assertFalse(self.pedir("/config", {"resumir_meses": 0})["ok"])
        self.assertFalse(self.pedir("/config", {"apagar_meses": 300})["ok"])
        self.assertTrue(self.pedir("/config", {"resumir_meses": 3, "apagar_meses": 0})["ok"])
        self.assertEqual((self.cfg()["radar"]["resumir_meses"], self.cfg()["radar"]["apagar_meses"]), (3, 0))

    def test_opcao_da_consulta_publica(self):
        self.assertTrue(self.pedir("/config", {"consulta_publica": False})["ok"])
        self.assertIs(self.cfg()["radar"]["consulta_publica"], False)

    def test_historico_com_limpeza_consulta_e_conferencia(self):
        b = bd.Banco(self.srv.caminho_db)
        b.registrar("limpeza", {"quando_local": "2026-11-14T20:40:00-03:00", "resumidos": 1, "apagados": 2})
        b.registrar("consulta", {"quando_local": "2026-11-14T20:09:00-03:00", "novos": 37, "tribunais": ["TRT2"]})
        b.registrar("conferencia", {"quando_local": "2026-11-15T20:31:00-03:00", "a_mais": 0, "tribunais": ["TRT2"]})
        b.con.close()
        tipos = [h.get("tipo") for h in self.pedir("/historico", metodo="GET")["tentativas"]]
        self.assertEqual(tipos, ["conferencia", "limpeza", "consulta"])  # na ordem do tempo, a mais recente primeiro

    def test_limpar_o_banco_agora_em_segundo_plano(self):
        d = self.pedir("/limpeza/agora")
        self.assertTrue(d.get("ok"), d)
        for _ in range(100):
            e = self.pedir("/limpeza/estado")
            if not e["rodando"]:
                break
            threading.Event().wait(0.05)
        self.assertIn("resumidos", e["resultado"])
        self.srv.estado.rodando = True
        self.addCleanup(setattr, self.srv.estado, "rodando", False)
        self.assertFalse(self.pedir("/limpeza/agora")["ok"])  # durante a leitura, não começa outra

    def test_dados_mostram_os_prazos_e_a_opcao(self):
        c = self.pedir("/dados", metodo="GET")["app"]["config"]
        self.assertEqual((c["resumir_meses"], c["apagar_meses"], c["consulta_publica"]), (6, 24, True))


class Tela(unittest.TestCase):
    def test_versao(self):
        self.assertEqual(VERSAO, "0.7.48")
        self.assertIn('"0.7.48": {', HTML)

    def test_chaves_em_pt_e_en(self):
        for k in ("cena2_t", "cena2_t_varas", "cena3_t", "cena3_ver", "cena4_0", "cena4_n", "m_rodada", "ag_consulta", "ag_consulta_x",
                  "selo_consulta", "hist_consulta_x", "hist_conferencia_x0", "hist_conferencia_xn", "lp_t", "lp_agora", "lp_confirma",
                  "f_todas_cidades", "f_sem_cidade", "f_cidade_limpa", "bg_cidade", "al_md_ajuda", "al_p1_pend", "ag_avisar_cnj_sem"):
            self.assertEqual(len(re.findall(r"\b" + k + r': "', HTML)), 2, k)

    def test_cidade_logo_depois_do_estado(self):
        self.assertIn('"porte", "uf", "cidade", "sinal"', HTML)
        self.assertIn("cidade: []", HTML)

    def test_novos_desta_leitura(self):
        self.assertIn("if (F.rodada && i.rodada !== F.rodada) return false;", HTML)
        self.assertIn('rodada: "" });', HTML)

    def test_busca_do_assistone(self):
        for termo in ('"limpeza"', '"apagar"', '"cidade"', '"consulta pública"', '"caderno pendente"'):
            self.assertIn(termo, HTML, termo)

    def test_textos_da_faixa_e_da_area_logada(self):
        self.assertIn("Tudo certo: planilha abaixo de 80 % do limite e espaço no disco.", HTML)
        self.assertIn('al_ja_tenho: "Colar a resposta agora"', HTML)
        self.assertIn('al_fechar_volto: "Fechar (trago a resposta depois)"', HTML)
        self.assertNotIn("Não achei a tabela", HTML)
        self.assertIn("socio: true", HTML)
        self.assertRegex(HTML, r"\.janela\s*\{[^}]*resize:\s*both")  # janelas mudam de tamanho pelo canto
        self.assertIn("janela.movida", HTML)  # e se movem pelo título

    def test_manual_fala_das_novidades(self):
        with open(os.path.join(_RAIZ_, "paginas", "manual.html"), encoding="utf-8") as f:
            m = f.read()
        for trecho in ("Resumir depois de 6 meses", "Apagar depois de 24 meses", "O que nunca sai", "Limpar o banco agora",
                       "Lendo pela consulta pública do CNJ (vara por vara)", "caderno pendente", "Sem cidade", "volta ao centro e ao tamanho padrão",
                       "Colar a resposta agora", "Não encontrei a resposta da ferramenta"):
            self.assertIn(trecho, m, trecho)
        self.assertNotIn("Não achei a tabela", m)

    def test_termos_nao_mudam(self):
        with open(os.path.join(_RAIZ_, "paginas", "aceite.html"), encoding="utf-8") as f:
            self.assertNotIn("0.7.48", f.read())


if __name__ == "__main__":
    unittest.main()
