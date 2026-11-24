"""0.7.53 (decisões 59 a 67 do dono, 24/Nov): planilha só com os tribunais escolhidos e aba Estatística; amostras de formato
anonimizadas com fila silenciosa; VÁRIOS COMPUTADORES NA MESMA PASTA sem computador mestre (troca, junção, trava, vetor),
"Visto por". Inclui a simulação de acesso simultâneo pedida pelo dono: dois "computadores" (bancos e instalações diferentes)
na mesma pasta, em sequência, fora de ordem e em dois processos de verdade ao mesmo tempo. Dados FICTÍCIOS, sem internet."""

import datetime as dt
import gzip
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

_ROBO_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROBO_)

from lexsuite import amostras, armazenamento, banco as bd, compartilhar, planilha, preferencias as pf, radar, troca  # noqa: E402

HOJE = dt.date.today()


def _cfg(pasta, inst, nome, tribunais=("TRT9",)):
    return {"compartilhar": {"pasta": pasta}, "radar": {"tribunais": list(tribunais), "dias_na_pagina": 30},
            "conta": {"instalacao": inst, "codigo": "LEX-AAAA-BBBB"}, "usuario": {"nome": nome, "email": nome.lower() + "@exemplo.invalid"}}


def _lead(b, proc, trib="TRT9", dias=1):
    d = (HOJE - dt.timedelta(days=dias)).isoformat()
    b.guardar_lead({"processo": proc, "tribunal": trib, "vara": "1ª Vara (fictícia)", "empresas": ["Empresa Ficticia Ltda"],
                    "data_publicacao": d}, d)


def _contato(b, proc, valor, por):
    return b.guardar_contato({"processo": proc, "empresa": "Empresa Ficticia Ltda", "canal": "telefone", "valor": valor,
                              "fonte": "PJe dados do processo", "data": HOJE.isoformat(), "incluido_por": por})


def _estado(b):
    st = {r[0]: r[1] for r in b.con.execute("SELECT processo, status FROM leads")}
    ct = sorted((r[0], r[1]) for r in b.con.execute("SELECT processo, valor FROM contatos"))
    return st, ct


class DoisComputadores(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.pasta, True)
        self.ca, self.cb = _cfg(self.pasta, "aaaa1111aaaa1111", "Maria"), _cfg(self.pasta, "bbbb2222bbbb2222", "João")
        self.a, self.b = bd.Banco(os.path.join(tempfile.mkdtemp(), "a.db")), bd.Banco(os.path.join(tempfile.mkdtemp(), "b.db"))
        self.addCleanup(self.a.con.close); self.addCleanup(self.b.con.close)

    def test_a_le_o_diario_e_b_traz_contatos_nada_se_perde(self):
        for k in range(5):
            _lead(self.a, f"00000{k:02d}-11.2026.5.09.0001")
        self.assertGreater(troca.exportar(self.a, self.ca), 0)
        self.assertEqual(troca.pendentes(self.b, self.cb)["n"], 5)
        self.assertEqual(troca.juntar(self.b, self.cb), 5)  # B recebe os processos que A leu, sem ler o Diário
        self.b.mudar_situacao(["0000001-11.2026.5.09.0001"], "em_contato", por="João (PC-B)")
        _contato(self.b, "0000001-11.2026.5.09.0001", "(41) 3333-0000", "João (PC-B)")
        troca.exportar(self.b, self.cb)
        troca.juntar(self.a, self.ca)
        self.assertEqual(_estado(self.a), _estado(self.b))
        st = self.a.con.execute("SELECT status, status_por FROM leads WHERE processo = '0000001-11.2026.5.09.0001'").fetchone()
        self.assertEqual(st, ("em_contato", "João (PC-B)"))
        self.assertEqual(troca.juntar(self.a, self.ca), 0)  # juntar de novo não muda nada
        # quem gravar a planilha por último, ela tem tudo (é espelho do banco)
        for b_, c_ in ((self.a, self.ca), (self.b, self.cb)):
            self.assertTrue(radar.gravar_planilha(c_, radar.montar_radar(c_, b_, prefs=pf.padrao()), b_, "0.7.53", self.pasta, lambda *_: None))
            abas = {x["nome"]: x for x in planilha.ler_xlsx(pf.caminho(compartilhar.pasta_base(c_), "trabalhista"))["abas"]}
            self.assertIn("(41) 3333-0000", json.dumps(abas["Contatos"]["linhas"], ensure_ascii=False))
            self.assertIn("João (PC-B)", json.dumps(abas["Contatos"]["linhas"], ensure_ascii=False))

    def test_visto_nunca_passa_por_cima_e_os_dois_terminam_iguais(self):
        for b_ in (self.a, self.b):
            _lead(b_, "0000009-11.2026.5.09.0001")
        self.b.mudar_situacao(["0000009-11.2026.5.09.0001"], "em_contato", por="João (PC-B)")
        self.a.mudar_situacao(["0000009-11.2026.5.09.0001"], "visto", por="Maria (PC-A)")  # depois, sem saber do outro
        troca.exportar(self.a, self.ca); troca.exportar(self.b, self.cb)
        troca.juntar(self.a, self.ca); troca.juntar(self.b, self.cb)
        for b_ in (self.a, self.b):
            st, vp = b_.con.execute("SELECT status, visto_por FROM leads").fetchone()
            self.assertEqual(st, "em_contato"); self.assertEqual(vp, "Maria (PC-A)")  # quem viu continua registrado

    def test_ordem_dos_arquivos_nao_importa(self):
        _lead(self.a, "0000001-11.2026.5.09.0001"); troca.exportar(self.a, self.ca)
        self.a.mudar_situacao(["0000001-11.2026.5.09.0001"], "em_analise", por="Maria"); troca.exportar(self.a, self.ca)
        _contato(self.a, "0000001-11.2026.5.09.0001", "(41) 3333-1111", "Maria"); troca.exportar(self.a, self.ca)
        arquivos = sorted(os.listdir(os.path.join(self.pasta, "LexSuiteONE", troca.PASTA, "troca", "aaaa1111aaaa1111")))
        self.assertEqual(len(arquivos), 3)
        # o Drive entrega o 3º antes do 1º: B junta o que tem (o contato fica esperando o processo) e depois o resto
        escondido = os.path.join(self.pasta, "esconde"); os.makedirs(escondido)
        base = os.path.join(self.pasta, "LexSuiteONE", troca.PASTA, "troca", "aaaa1111aaaa1111")
        for n in arquivos[:2]:
            shutil.move(os.path.join(base, n), os.path.join(escondido, n))
        troca.juntar(self.b, self.cb)
        self.assertEqual(troca.vetor(self.b, self.cb)["aaaa1111aaaa1111"], 0)  # tem o 3, mas falta o 1: o vetor não pula
        for n in arquivos[:2]:
            shutil.move(os.path.join(escondido, n), os.path.join(base, n))
        # revisão da Operação (B1): os que chegaram depois NÃO são dados por lidos: entram na próxima junção
        self.assertGreater(troca.pendentes(self.b, self.cb)["n"], 0)
        troca.juntar(self.b, self.cb)
        self.assertEqual(_estado(self.b), _estado(self.a))
        self.assertEqual(troca.vetor(self.b, self.cb)["aaaa1111aaaa1111"], 3)

    def test_revisao_arquivo_sincronizando_e_lido_quando_completa(self):
        _lead(self.a, "0000001-11.2026.5.09.0001"); troca.exportar(self.a, self.ca)
        base = os.path.join(self.pasta, "LexSuiteONE", troca.PASTA, "troca", "aaaa1111aaaa1111")
        nome = os.path.join(base, os.listdir(base)[0])
        with open(nome, "rb") as f:
            inteiro = f.read()
        with open(nome, "wb") as f:
            f.write(inteiro[:len(inteiro) // 2])  # o Drive ainda está baixando
        self.assertEqual(troca.juntar(self.b, self.cb), 0)
        with open(nome, "wb") as f:
            f.write(inteiro)  # terminou de sincronizar
        self.assertEqual(troca.juntar(self.b, self.cb), 1)
        self.assertEqual(_estado(self.b), _estado(self.a))

    def test_revisao_banco_recriado_nao_sobrescreve_arquivo_ja_lido(self):
        _lead(self.a, "0000001-11.2026.5.09.0001"); troca.exportar(self.a, self.ca)
        troca.juntar(self.b, self.cb)
        novo = bd.Banco(os.path.join(tempfile.mkdtemp(), "a2.db")); self.addCleanup(novo.con.close)  # reinstalado, mesma instalação
        _lead(novo, "0000002-11.2026.5.09.0001"); troca.exportar(novo, self.ca)
        base = os.path.join(self.pasta, "LexSuiteONE", troca.PASTA, "troca", "aaaa1111aaaa1111")
        self.assertEqual(sorted(n[:8] for n in os.listdir(base)), ["00000001", "00000002"])  # o 1 ficou; o novo é o 2
        troca.juntar(self.b, self.cb)
        self.assertEqual(self.b.con.execute("SELECT count(*) FROM leads").fetchone()[0], 2)

    def test_planilha_nunca_volta_atras(self):
        _lead(self.a, "0000001-11.2026.5.09.0001")
        self.assertTrue(radar.gravar_planilha(self.ca, radar.montar_radar(self.ca, self.a, prefs=pf.padrao()), self.a, "0.7.53", self.pasta, lambda *_: None))
        caminho = pf.caminho(compartilhar.pasta_base(self.ca), "trabalhista")
        self.assertEqual(compartilhar.ler_vetor(caminho), troca.vetor(self.a, self.ca))
        # o arquivo de A ainda não chegou ao B (sincronização atrasada): B não grava por cima
        base = os.path.join(self.pasta, "LexSuiteONE", troca.PASTA, "troca", "aaaa1111aaaa1111")
        escondido = tempfile.mkdtemp(); [shutil.move(os.path.join(base, n), os.path.join(escondido, n)) for n in os.listdir(base)]
        avisos = []
        self.assertFalse(radar.gravar_planilha(self.cb, radar.montar_radar(self.cb, self.b, prefs=pf.padrao()), self.b, "0.7.53", self.pasta, avisos.append))
        self.assertTrue(any("ainda não chegaram" in x for x in avisos))
        [shutil.move(os.path.join(escondido, n), os.path.join(base, n)) for n in os.listdir(escondido)]
        self.assertTrue(radar.gravar_planilha(self.cb, radar.montar_radar(self.cb, self.b, prefs=pf.padrao()), self.b, "0.7.53", self.pasta, lambda *_: None))
        self.assertIn("0000001-11.2026.5.09.0001", json.dumps(planilha.ler_xlsx(caminho)["abas"][0]["linhas"]))

    def test_trava_de_outro_computador_e_trava_vencida(self):
        raiz = troca.pasta(self.ca); os.makedirs(raiz, exist_ok=True)
        trava = os.path.join(raiz, "gravando.trava")
        with open(trava, "w", encoding="utf-8") as f:
            json.dump({"instalacao": "bbbb2222bbbb2222", "quem": "João", "quando": dt.datetime.now(dt.timezone.utc).timestamp()}, f)
        avisos = []
        self.assertFalse(radar.gravar_planilha(self.ca, radar.montar_radar(self.ca, self.a, prefs=pf.padrao()), self.a, "0.7.53", self.pasta, avisos.append))
        self.assertTrue(any("Outro computador está gravando" in x for x in avisos))
        with open(trava, "w", encoding="utf-8") as f:  # o outro caiu no meio: a trava vence em 2 min
            json.dump({"instalacao": "bbbb2222bbbb2222", "quando": dt.datetime.now(dt.timezone.utc).timestamp() - 300}, f)
        self.assertTrue(radar.gravar_planilha(self.ca, radar.montar_radar(self.ca, self.a, prefs=pf.padrao()), self.a, "0.7.53", self.pasta, lambda *_: None))
        self.assertFalse(os.path.exists(trava))  # quem gravou soltou a trava

    def test_arquivo_ruim_e_ignorado_e_pessoa_fisica_nao_entra(self):
        base = os.path.join(self.pasta, "LexSuiteONE", troca.PASTA, "troca", "dddd4444dddd4444"); os.makedirs(base)
        _lead(self.b, "0000001-11.2026.5.09.0001")
        bom = {"formato": 1, "instalacao": "dddd4444dddd4444", "licenca": troca._licenca(self.cb), "seq": 1, "quem": "X", "itens": [
            {"t": "contato", "processo": "0000001-11.2026.5.09.0001", "canal": "telefone", "valor": "reclamante (41) 9999-0000"},
            {"t": "contato", "processo": "0000001-11.2026.5.09.0001", "canal": "email", "valor": "cpf 123.456.789-09"},
            {"t": "contato", "processo": "0000001-11.2026.5.09.0001", "canal": "telefone", "valor": "(41) 3333-2222"}]}
        with gzip.open(os.path.join(base, "00000001-3.json.gz"), "wt", encoding="utf-8") as f:
            json.dump(bom, f)
        with open(os.path.join(base, "00000002-1.json.gz"), "wb") as f:
            f.write(b"isto nao e gzip")
        outra = dict(bom, licenca="0" * 16, seq=3)
        with gzip.open(os.path.join(base, "00000003-3.json.gz"), "wt", encoding="utf-8") as f:
            json.dump(outra, f)
        self.assertEqual(troca.juntar(self.b, self.cb), 1)
        self.assertEqual([c["valor"] for c in self.b.contatos()], ["(41) 3333-2222"])
        self.assertTrue(any("outra licença" in e.get("detalhe", "") for e in self.b.execucoes("saude", 10)))  # de outra licença: na hora
        # o que não abre pode estar sincronizando: continua sendo tentado; só é dado por ruim depois de 10 tentativas e 24 h
        self.assertEqual(troca.pendentes(self.b, self.cb)["n"], 1)
        for _ in range(troca.FALHA_TENTATIVAS):
            troca.juntar(self.b, self.cb)
        self.assertEqual(troca.pendentes(self.b, self.cb)["n"], 1)  # ainda dentro das 24 h
        self.b.con.execute("UPDATE troca_falhas SET primeira_em = '2020-01-01T00:00:00'"); self.b.con.commit()
        troca.juntar(self.b, self.cb)
        self.assertEqual(troca.pendentes(self.b, self.cb)["n"], 0)

    def test_revisao_arquivo_corrompido_ou_estranho_nao_trava_a_gravacao(self):
        base = os.path.join(self.pasta, "LexSuiteONE", troca.PASTA, "troca", "dddd4444dddd4444"); os.makedirs(base)
        bom = gzip.compress(json.dumps({"formato": 1, "instalacao": "dddd4444dddd4444", "itens": []}).encode())
        with open(os.path.join(base, "00000001-1.json.gz"), "wb") as f:
            f.write(bom[:12] + b"\x00" * 20 + bom[32:])  # gzip com bytes trocados no meio (zlib.error)
        with gzip.open(os.path.join(base, "00000002-1.json.gz"), "wt", encoding="utf-8") as f:
            json.dump([1, 2, 3], f)  # JSON válido que não é objeto
        _lead(self.b, "0000001-11.2026.5.09.0001")
        self.assertEqual(troca.juntar(self.b, self.cb), 0)
        self.assertEqual(troca.pendentes(self.b, self.cb)["n"], 1)  # o corrompido fica para tentar de novo; o JSON estranho sai na hora
        self.assertTrue(radar.gravar_planilha(self.cb, radar.montar_radar(self.cb, self.b, prefs=pf.padrao()), self.b, "0.7.53", self.pasta, lambda *_: None))

    def test_revisao_pasta_fora_do_ar_nao_derruba_a_leitura(self):
        from unittest import mock
        with mock.patch.object(troca.os, "makedirs", side_effect=PermissionError("pasta de rede fora")):
            with troca.trava(self.ca) as t:
                self.assertEqual(t, "sem pasta")

    def test_revisao_situacao_marcada_aqui_sai_mesmo_com_relogio_atrasado(self):
        _lead(self.a, "0000001-11.2026.5.09.0001"); _lead(self.b, "0000001-11.2026.5.09.0001")
        # o outro computador está com o relógio adiantado: a situação dele chega "do futuro"
        self.a.con.execute("UPDATE leads SET status = 'descartado', status_em = '2099-01-01T00:00:00+00:00'"); self.a.con.commit()
        self.a.con.execute("INSERT INTO troca_sujos (processo) VALUES ('0000001-11.2026.5.09.0001')"); self.a.con.commit()
        troca.exportar(self.a, self.ca); troca.juntar(self.b, self.cb)
        self.b.mudar_situacao(["0000001-11.2026.5.09.0001"], "virou_cliente", por="João")  # marcado aqui, com o relógio certo
        self.assertGreater(troca.exportar(self.b, self.cb), 0)  # sai, mesmo mais "velho" que o que veio de fora
        self.assertEqual(troca.exportar(self.b, self.cb), 0)  # e não sai de novo

    def test_revisao_mudanca_que_chega_antes_do_processo_espera_por_ele(self):
        _lead(self.a, "0000001-11.2026.5.09.0001", dias=60)  # fora dos 30 dias: o processo não vai na troca
        self.a.mudar_situacao(["0000001-11.2026.5.09.0001"], "em_analise", por="Maria")
        troca.exportar(self.a, self.ca)
        troca.juntar(self.b, self.cb)
        _lead(self.b, "0000001-11.2026.5.09.0001", dias=60)  # o B lê o mesmo processo depois
        troca.juntar(self.b, self.cb)
        self.assertEqual(self.b.con.execute("SELECT status FROM leads").fetchone()[0], "em_analise")

    def test_processo_apagado_pela_limpeza_nao_volta(self):
        _lead(self.a, "0000001-11.2026.5.09.0001"); troca.exportar(self.a, self.ca)
        self.b.con.execute("INSERT INTO processos_apagados VALUES ('0000001-11.2026.5.09.0001', '2026-11-01', '2026-01-01')"); self.b.con.commit()
        troca.juntar(self.b, self.cb)
        self.assertEqual(self.b.con.execute("SELECT count(*) FROM leads").fetchone()[0], 0)


_SCRIPT = textwrap.dedent('''
    import datetime as dt, json, os, sys, time
    sys.path.insert(0, {robo!r})
    from lexsuite import banco as bd, preferencias as pf, radar, troca
    pasta, inst, nome, db, n = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
    cfg = {{"compartilhar": {{"pasta": pasta}}, "radar": {{"tribunais": ["TRT9"], "dias_na_pagina": 30}},
           "conta": {{"instalacao": inst, "codigo": "LEX-AAAA-BBBB"}}, "usuario": {{"nome": nome}}}}
    b = bd.Banco(db)
    hoje = dt.date.today().isoformat()
    gravou = 0
    for k in range(n):
        proc = "%07d-11.2026.5.09.%04d" % (k, 1 if inst.startswith("a") else 2)
        b.guardar_lead({{"processo": proc, "tribunal": "TRT9", "vara": "1a Vara (ficticia)", "empresas": ["Empresa Ficticia"], "data_publicacao": hoje}}, hoje)
        b.guardar_contato({{"processo": proc, "canal": "telefone", "valor": "(41) 3000-%04d %s" % (k, inst[:4]), "fonte": "PJe", "incluido_por": nome}})
        troca.exportar(b, cfg)
        troca.juntar(b, cfg)
        if radar.gravar_planilha(cfg, radar.montar_radar(cfg, b, prefs=pf.padrao()), b, "0.7.53", pasta, lambda *_: None):
            gravou += 1
    print(json.dumps({{"gravou": gravou}}))
''')


class AcessoSimultaneo(unittest.TestCase):
    """Dois processos de verdade, ao mesmo tempo, na mesma pasta: cada um lê, traz contatos, troca e grava a planilha várias
    vezes. No fim, nenhum dado se perde, a planilha é válida e tem o trabalho dos dois, e não sobra trava nem arquivo pela metade."""

    def test_dois_computadores_gravando_ao_mesmo_tempo(self):
        pasta = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, pasta, True)
        script = os.path.join(pasta, "computador.py")
        with open(script, "w", encoding="utf-8") as f:
            f.write(_SCRIPT.format(robo=_ROBO_))
        dbs = {"aaaa1111aaaa1111": os.path.join(pasta, "a.db"), "bbbb2222bbbb2222": os.path.join(pasta, "b.db")}
        procs = [subprocess.Popen([sys.executable, "-I", script, pasta, inst, nome, dbs[inst], "8"], stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True) for inst, nome in (("aaaa1111aaaa1111", "Maria"), ("bbbb2222bbbb2222", "João"))]
        saidas = [p.communicate(timeout=300) for p in procs]
        for p, (out, err) in zip(procs, saidas):
            self.assertEqual(p.returncode, 0, err[-2000:])
        gravou = sum(json.loads(out.strip().splitlines()[-1])["gravou"] for out, _ in saidas)
        self.assertGreater(gravou, 0)
        # mais uma rodada de troca em cada um (o que o outro gravou por último) e uma gravação final
        bancos = {}
        for inst, nome in (("aaaa1111aaaa1111", "Maria"), ("bbbb2222bbbb2222", "João")):
            b = bd.Banco(dbs[inst]); self.addCleanup(b.con.close); bancos[inst] = (b, _cfg(pasta, inst, nome))
            troca.juntar(b, bancos[inst][1]); troca.exportar(b, bancos[inst][1])
        for b, c in bancos.values():
            troca.juntar(b, c)
        (ba, ca), (bb, cb) = bancos.values()
        self.assertEqual(_estado(ba), _estado(bb))
        self.assertEqual(len(ba.contatos()), 16)  # 8 de cada um, nenhum perdido
        self.assertTrue(radar.gravar_planilha(ca, radar.montar_radar(ca, ba, prefs=pf.padrao()), ba, "0.7.53", pasta, lambda *_: None))
        linhas = json.dumps(planilha.ler_xlsx(pf.caminho(compartilhar.pasta_base(ca), "trabalhista"))["abas"], ensure_ascii=False)
        self.assertIn("aaaa", linhas); self.assertIn("bbbb", linhas)
        raiz = troca.pasta(ca)
        self.assertFalse(os.path.exists(os.path.join(raiz, "gravando.trava")))
        restos = [n for _r, _d, fs in os.walk(os.path.dirname(raiz)) for n in fs if n.endswith(".parcial") or n.endswith(".tmp")]
        self.assertEqual(restos, [])


class PlanilhaEnxuta(unittest.TestCase):
    def test_so_escolhidos_radar_30_dias_arquivo_pela_data_e_estatistica_de_todos(self):
        pasta = tempfile.mkdtemp(); self.addCleanup(shutil.rmtree, pasta, True)
        cfg = {"compartilhar": {"pasta": pasta}, "radar": {"tribunais": ["TRT9"], "dias_na_pagina": 90}}
        b = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db")); self.addCleanup(b.con.close)
        for k in range(10):
            _lead(b, f"00000{k:02d}-11.2026.5.09.0001", "TRT9", k * 10)  # 0 a 90 dias
        for k in range(5):
            _lead(b, f"00001{k:02d}-11.2026.5.03.0001", "TRT3", 2)  # tribunal lido antes, não escolhido hoje
        b.atualizar_estatisticas(); b.atualizar_estatisticas_leves(radar.setor_do_lead)
        self.assertTrue(radar.gravar_planilha(cfg, radar.montar_radar(cfg, b, prefs=pf.padrao()), b, "0.7.53", pasta, lambda *_: None))
        abas = {a["nome"]: a["linhas"] for a in planilha.ler_xlsx(pf.caminho(compartilhar.pasta_base(cfg), "trabalhista"))["abas"]}
        radar_ = [l for l in abas["Radar"] if len(l) > 5 and str(l[5]).startswith("00")]
        self.assertEqual(len(radar_), 4)  # 0, 10, 20 e 30 dias
        self.assertNotIn("TRT3", json.dumps(abas["Radar"]) + json.dumps(abas["Arquivo"]))
        self.assertIn("TRT3", json.dumps(abas["Estatística"]))  # só em números
        self.assertTrue(os.path.isdir(os.path.join(compartilhar.pasta_base(cfg), "Cópias de segurança", "antes da 0.7.53")))

    def test_arquivo_conta_pela_data_do_diario(self):
        velho = {"situacao": "novo", "diario_em": "2026-01-01", "primeira_vez": HOJE.isoformat()}
        self.assertEqual(armazenamento.selecionar_arquivo([velho], 90), [])

    def test_aba_estatistica_tem_situacao_e_setor(self):
        b = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db")); self.addCleanup(b.con.close)
        _lead(b, "0000001-11.2026.5.02.0001", "TRT2", 3)
        b.mudar_situacao(["0000001-11.2026.5.02.0001"], "em_contato")
        b.atualizar_estatisticas(); b.atualizar_estatisticas_leves(radar.setor_do_lead)
        linhas = armazenamento.linhas_estatistica(b)
        dims = {l[3] for l in linhas[1:]}
        self.assertTrue({"Total", "Situação", "Setor"} <= dims, dims)
        self.assertIn("Em contato", [l[4] for l in linhas])


class AmostrasDeFormato(unittest.TestCase):
    def setUp(self):
        amostras._buffer.clear()

    def test_troca_irreversivel_com_o_mesmo_formato(self):
        orig = {"items": [{"id": 123, "siglaTribunal": "TRT9", "tipoComunicacao": "Intimação", "texto": "Empresa Ficticia Ltda x Fulano",
                           "destinatarios": [{"nome": "NOME FICTICIO", "polo": "A"}], "valor": 1234.5}]}
        t = amostras.trocar_json(orig)
        self.assertEqual(amostras.assinatura_json(t), amostras.assinatura_json(orig))
        txt = json.dumps(t, ensure_ascii=False)
        self.assertNotIn("Ficticia", txt); self.assertNotIn("FICTICIO", txt)
        self.assertIn("TRT9", txt); self.assertIn("Intimação", txt)  # sigla e valor tabelado são públicos
        self.assertEqual(len(t["items"][0]["texto"]), len(orig["items"][0]["texto"]))
        self.assertNotEqual(amostras.trocar_json(orig), amostras.trocar_json(orig))  # sorteio novo a cada vez

    def test_nunca_sai_documento_valido(self):
        self.assertEqual(amostras._sem_documento_valido("11.222.333/0001-81"), "11.222.333/0001-82")
        self.assertEqual(amostras._sem_documento_valido("529.982.247-25"), "529.982.247-26")

    def test_resposta_da_area_logada_mantem_o_protocolo(self):
        txt = ("RESPOSTA PARA O RADAR v1 · lote 1 de 2\n| processo | dado | valor | resultado | fonte | data | observação |\n"
               "|---|---|---|---|---|---|---|\n| 0001234-11.2026.5.02.0001 | telefone | (11) 3333-4444 | encontrado | PJe | 2026-11-20 | |\n")
        x = amostras.trocar_resposta_area(txt)
        self.assertTrue(x.startswith("RESPOSTA PARA O RADAR v1 · lote 1 de 2"))
        self.assertNotIn("3333-4444", x); self.assertNotIn("0001234", x)
        self.assertEqual(amostras.assinatura_area(x), amostras.assinatura_area(txt))

    def test_mudanca_de_formato_fica_registrada_e_vai_na_fila(self):
        b = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db")); self.addCleanup(b.con.close)
        amostras.observar("djen_caderno:TRT9", {"items": [{"id": 1, "valor": 10}]}); amostras.descarregar(b)
        amostras.observar("djen_caderno:TRT9", {"items": [{"id": 2, "valorCausa": 10}]}); mud = amostras.descarregar(b)
        self.assertEqual(len(mud), 1)
        self.assertIn("items[].valorCausa:num", mud[0]["diferenca"]["novos"])
        self.assertTrue(any("Formato de djen_caderno:TRT9" == e.get("fonte") for e in b.execucoes("saude", 5)))
        tipos = [r[0] for r in b.con.execute("SELECT tipo FROM envios")]
        self.assertIn("formato", tipos); self.assertIn("amostra", tipos)
        self.assertEqual(amostras.previa(b)["fontes"][0]["fonte"], "djen_caderno:TRT9")

    def test_envio_silencioso_fica_na_fila_e_tenta_depois(self):
        b = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db")); self.addCleanup(b.con.close)
        amostras.observar("receita:brasilapi", {"razao_social": "EMPRESA FICTICIA", "qsa": [{"nome_socio": "NOME FICTICIO"}]}); amostras.descarregar(b)
        cfg = {"conta": {"codigo": "LEX-AAAA-BBBB", "instalacao": "abc"}}
        nada = []
        self.assertEqual(amostras.enviar_pendentes(b, cfg, "0.7.53", pedir=lambda *a, **k: nada.append(1) or {"ok": True}), 0)
        self.assertEqual(nada, [])  # revisão: sem o recurso `amostras` ligado pela SolverONE, nada sai
        cfg["conta"]["recursos"] = {"amostras": True}
        def fora(*a, **k):
            raise OSError("sem internet")
        agora = dt.datetime(2026, 11, 24, 10)
        self.assertEqual(amostras.enviar_pendentes(b, cfg, "0.7.53", pedir=fora, agora=agora), 0)
        prox = b.con.execute("SELECT min(proxima_em) FROM envios WHERE tentativas > 0").fetchone()[0]
        self.assertGreater(prox, agora.isoformat())
        enviados = []
        def ok(url, corpo, **k):
            enviados.append(corpo); return {"ok": True}
        self.assertEqual(amostras.enviar_pendentes(b, cfg, "0.7.53", pedir=ok, agora=agora), 0)  # ainda não venceu
        self.assertGreater(amostras.enviar_pendentes(b, cfg, "0.7.53", pedir=ok, agora=agora + dt.timedelta(days=2)), 0)
        self.assertTrue(all(c["acao"] in ("formato", "amostra") for c in enviados))
        self.assertNotIn("FICTICIO", json.dumps(enviados))
        self.assertNotIn("codigo_cliente", json.dumps(enviados))

    def test_amostra_nunca_atrapalha_a_leitura(self):
        amostras.observar("x", object())  # algo que nem vira JSON
        b = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db")); self.addCleanup(b.con.close)
        self.assertEqual(amostras.descarregar(b), [])


class Tela0753(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(_ROBO_, "radar_modelo.html"), encoding="utf-8") as f:
            cls.h = f.read()

    def test_botao_do_escritorio_visto_por_e_amostras(self):
        for trecho in ('id="b-escritorio"', 'fetch("/troca/estado"', 'post("/troca/juntar"', "setInterval(verEscritorio, 120000)",
                       't("visto_por"', 'esc_trazer: "Bring from the office ({n})"', 'am_ver: "Ver as amostras de formato ({n} fontes)"',
                       "saz_parcial", "saz_outros"):
            self.assertIn(trecho, self.h, trecho)

    def test_versao_e_novidades_sucintas(self):
        import re
        from lexsuite import VERSAO
        self.assertTrue(VERSAO >= "0.7.53")
        i = self.h.index('"0.7.53": {'); bloco = self.h[i:self.h.index('"0.7.52": {')]
        pt = re.findall(r'"([^"]+)"', bloco[bloco.index("pt: ["):bloco.index("en: [")])
        en = re.findall(r'"([^"]+)"', bloco[bloco.index("en: ["):])
        self.assertEqual(len(pt), len(en)); self.assertTrue(4 <= len(pt) <= 8)
        for linha in pt:
            self.assertNotRegex(linha, r"\b(agora|já lê|caixinha)\b")
        for linha in en:
            self.assertNotRegex(linha, r"\bnow\b")

    def test_colunas_de_autoria_na_planilha(self):
        titulos = [t for t, _ in radar.COLUNAS_RADAR]
        self.assertEqual(titulos[-2:], ["Visto por", "Situação marcada por"])


if __name__ == "__main__":
    unittest.main()
