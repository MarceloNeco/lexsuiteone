"""0.7.33: CNPJ alfanumérico, critérios por pessoa e por área, chamados pelo AssistONE (dados fictícios)."""

import os
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_ROBO_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from lexsuite import classificar as cl, cnpj, conta, documento, preferencias, rede  # noqa: E402

# Números fictícios: exemplo do Serpro (12ABC34501DE → DV 35) e um numérico de teste conhecido.
ALFA = "12ABC34501DE35"
NUM = "11222333000181"


class CnpjAlfanumerico(unittest.TestCase):
    def test_validacao(self):
        self.assertTrue(documento.valido(ALFA))
        self.assertFalse(documento.valido(ALFA[:-1] + "6"))
        self.assertTrue(documento.valido(NUM))
        self.assertTrue(documento.valido("11.222.333/0001-81"))
        self.assertFalse(documento.valido("AAAAAAAAAAAAAA"))
        self.assertFalse(documento.valido("12ABC34501DE3A"))  # DV é sempre número
        self.assertTrue(conta.cnpj_valido(ALFA)); self.assertTrue(cl.cnpj_valido(ALFA))

    def test_formatar_e_limpar(self):
        self.assertEqual(documento.formatar("12abc34501de35"), "12.ABC.345/01DE-35")
        self.assertEqual(documento.limpar("12.abc.345/01de-35"), ALFA)
        self.assertTrue(documento.eh_alfanumerico(ALFA)); self.assertFalse(documento.eh_alfanumerico(NUM))
        self.assertEqual(conta.documento("cnpj", "12.abc.345/01de-35"), ALFA)

    def test_extracao(self):
        self.assertEqual(cl.extrair_cnpjs("Reclamada: Empresa Exemplo Ltda, CNPJ 12.ABC.345/01DE-35"), [ALFA])
        self.assertEqual(cl.extrair_cnpjs("CNPJ 12ABC34501DE35"), [ALFA])
        self.assertEqual(cl.extrair_cnpjs("inscrita no cnpj nº 12.abc.345/01de-35"), [ALFA])
        self.assertEqual(cl.extrair_cnpjs("CNPJ 11.222.333/0001-81 e 11222333000181"), [NUM])
        self.assertEqual(cl.extrair_cnpjs("PROCESSO 12ABC34501DE35 AUTOS"), [])  # sem máscara e sem "CNPJ"
        self.assertEqual(cl.extrair_cnpjs("ABCDEFGHIJKLMN"), [])
        self.assertEqual(cl.extrair_cnpjs("CNPJ 12.ABC.345/01DE-36"), [])  # DV errado
        self.assertTrue(cl.eh_empresa("FULANO 12.ABC.345/01DE-35"))

    def test_exclusao_por_cnpj_alfanumerico_casa(self):
        itens = [{"empresas": ["Outra Ltda"], "empresa": {"cnpj": ALFA}}, {"empresas": ["Mais Uma Ltda"], "empresa": {"cnpj": NUM}}]
        preferencias.aplicar(itens, {"exclusoes": [{"nome": "12.abc.345/01de-35", "motivo": ""}]})
        self.assertTrue(itens[0]["excluida"]); self.assertFalse(itens[1]["excluida"])

    def test_cpf(self):
        self.assertTrue(documento.cpf_valido("529.982.247-25")); self.assertFalse(documento.cpf_valido("529.982.247-24"))
        self.assertEqual(documento.formatar_cpf("52998224725"), "529.982.247-25")

    def test_consulta_alfanumerico_sem_suporte_nao_e_inexistente(self):
        def recusa(url, *a, **k):
            raise rede.ErroHTTP(404, url, "não encontrado")
        with mock.patch.object(rede, "pedir_json", side_effect=recusa):
            d = cnpj.consultar(ALFA)
            self.assertEqual(d["situacao"], "fonte_sem_suporte"); self.assertEqual(d["cnpj"], ALFA)
            self.assertIsNone(cnpj.consultar(NUM))  # numérico que as fontes não acham continua "não achou"

    def test_consulta_manda_as_letras(self):
        urls = []
        def resp(url, *a, **k):
            urls.append(url); return {"razao_social": "EMPRESA EXEMPLO LTDA"}
        with mock.patch.object(rede, "pedir_json", side_effect=resp):
            d = cnpj.consultar("12.abc.345/01de-35")
        self.assertIn(ALFA, urls[0]); self.assertEqual(d["razao_social"], "EMPRESA EXEMPLO LTDA")

    def test_cache_sem_suporte_vale_7_dias(self):
        from lexsuite import banco as bd
        import datetime as dt
        with tempfile.TemporaryDirectory() as tmp:
            b = bd.Banco(os.path.join(tmp, "t.db"))
            b.guardar_cnpj(ALFA, {"cnpj": ALFA, "situacao": "fonte_sem_suporte"})
            b.con.execute("UPDATE cnpj SET quando = ?", ((dt.date.today() - dt.timedelta(days=8)).isoformat(),)); b.con.commit()
            with mock.patch.object(rede, "pedir_json", return_value={"razao_social": "EMPRESA EXEMPLO LTDA"}) as m:
                d = cnpj.consultar(ALFA, b)
            self.assertTrue(m.called); self.assertEqual(d["razao_social"], "EMPRESA EXEMPLO LTDA")

    def test_tela_formata_cnpj_com_letras(self):
        h = open(os.path.join(_ROBO_, "radar_modelo.html"), encoding="utf-8").read()
        self.assertIn('replace(/[^0-9A-Z]/g, "")', h); self.assertIn('e.situacao === "fonte_sem_suporte"', h)
        self.assertIn("cnpj_novo:", h)



class Chamados(unittest.TestCase):
    """0.7.33: chamado pelo AssistONE → servidor local → lex-conta (ação chamado) → central de feedback do RootifyONE."""

    CFG = {"conta": {"codigo": "LEX-ABCD-EFGH", "instalacao": "0123456789abcdef"}, "usuario": {"email": "pessoa@exemplo.com.br"}}

    def test_enviar_monta_o_pedido_e_le_a_resposta(self):
        visto = {}
        def pedir(url, corpo, **k):
            visto.update(corpo); return {"ok": True, "numero": 42}
        r = conta.enviar_chamado(self.CFG, "0.7.33", {"categoria": "duvida", "texto": "Como filtro?", "pode_responder": True,
                                                      "trilha": [{"quando": "t", "alvo": "b-config"}] * 9}, pedir=pedir)
        self.assertEqual(r, {"ok": True, "numero": 42, "repetido": False})
        self.assertEqual(visto["acao"], "chamado"); self.assertEqual(visto["email"], "pessoa@exemplo.com.br")
        self.assertEqual(len(visto["trilha"]), 5)
        visto.clear()
        conta.enviar_chamado(self.CFG, "0.7.33", {"categoria": "duvida", "texto": "x", "pode_responder": False}, pedir=pedir)
        self.assertNotIn("email", visto)

    def test_limite_e_sem_internet(self):
        def limite(url, corpo, **k):
            raise rede.ErroHTTP(429, url, '{"ok": false, "motivo": "limite"}')
        self.assertEqual(conta.enviar_chamado(self.CFG, "0.7.33", {"categoria": "erro", "texto": "x"}, pedir=limite)["motivo"], "limite")
        def fora(url, corpo, **k):
            raise rede.SemResposta(url, OSError("rede"))
        r = conta.enviar_chamado(self.CFG, "0.7.33", {"categoria": "erro", "texto": "x"}, pedir=fora)
        self.assertTrue(r["sem_internet"]); self.assertFalse(r["ok"])

    def test_rota_com_fila_sem_internet_e_reenvio(self):
        import http.client, json as _j, threading
        from lexsuite import app
        pasta = tempfile.mkdtemp()
        with open(os.path.join(pasta, "config.json"), "w", encoding="utf-8") as f:
            _j.dump(dict(self.CFG, radar={"tribunais": ["TRT2"]}), f)
        srv = app.Servidor(("127.0.0.1", 0), pasta)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        liga = mock.patch.object(app, "CHAMADO_LIGADO", True); liga.start(); self.addCleanup(liga.stop)
        def pedir(metodo, rota, corpo=None):
            c = http.client.HTTPConnection("127.0.0.1", srv.server_address[1], timeout=20)
            c.request(metodo, rota, body=_j.dumps(corpo) if corpo is not None else None, headers={"X-LexSuite": "1", "Content-Type": "application/json"})
            r = c.getresponse(); d = _j.loads(r.read()); d["_status"] = r.status; c.close(); return d
        try:
            self.assertEqual(pedir("POST", "/chamado", {"categoria": "x", "texto": "a"})["_status"], 400)
            self.assertEqual(pedir("POST", "/chamado", {"categoria": "erro", "texto": " "})["_status"], 400)
            ids = []
            with mock.patch.object(conta, "enviar_chamado", side_effect=lambda c, v, d: ids.append(d["cliente_id"]) or {"ok": False, "motivo": "sem_internet", "sem_internet": True}):
                r = pedir("POST", "/chamado", {"categoria": "erro", "texto": "Não abre a planilha", "tela": "lista", "trilha": [{"quando": "t", "alvo": "b-planilha"}]})
            self.assertTrue(r["fila"]); self.assertIn("Sem internet", r["motivo"])
            with mock.patch.object(conta, "enviar_chamado", side_effect=lambda c, v, d: ids.append(d["cliente_id"]) or {"ok": True, "numero": 7}):
                d = pedir("GET", "/chamados")
            self.assertEqual(d["pendentes"], 0); self.assertEqual(d["chamados"][0]["numero"], 7)
            self.assertEqual(len(set(ids)), 1)  # o reenvio usa o mesmo cliente_id: a central não duplica
            with mock.patch.object(conta, "enviar_chamado", return_value={"ok": False, "motivo": "limite"}):
                r = pedir("POST", "/chamado", {"categoria": "duvida", "texto": "Outra"})
            self.assertFalse(r["ok"]); self.assertIn("Limite", r["motivo"]); self.assertTrue(r["motivo_en"])
        finally:
            srv.shutdown(); srv.server_close()

    def test_tela_tem_o_chamado_no_assistone_e_trilha_sem_texto(self):
        with open(os.path.join(_ROBO_, "radar_modelo.html"), encoding="utf-8") as f:
            h = f.read()
        self.assertIn("raiz.LEX_CHAMADO", h); self.assertIn('post("/chamado"', h)
        self.assertIn("aoneChamado:", h)
        i = h.index("function alvoTrilha("); trecho = h[i:i + 600]
        self.assertNotIn("textContent", trecho); self.assertNotIn("aria-label", trecho)  # nunca o texto da tela nem nomes


class SazonalidadeTudo(unittest.TestCase):
    """0.7.33 (dono): "Buscar estatísticas" lê a fila inteira (em lotes), com andamento por mês; erros não viram laço."""

    def test_le_a_fila_inteira_em_lotes_e_para_a_pedido(self):
        import datetime as dt
        from lexsuite import banco as bd, djen, historico as h
        with tempfile.TemporaryDirectory() as tmp:
            b = bd.Banco(os.path.join(tmp, "t.db"))
            n = h.pedir(b, 3, ["TRT2"], hoje=dt.date(2026, 11, 12))
            self.assertGreater(n, 40)
            passos = []
            with mock.patch.object(djen, "meta_caderno", side_effect=lambda t, d, *a, **k: None):
                r = h.processar_tudo(b, aviso=lambda *_: None, pausa=0, lote=7, andamento=lambda k, tot, tr, d: passos.append((k, tot)))
            self.assertEqual(r["sem_diario"], n); self.assertEqual(h.situacao(b)["na_fila"], 0)
            self.assertEqual(passos[-1], (n, n))  # andamento contado do começo ao fim, atravessando os lotes
            meses = h.situacao(b)["meses"]
            self.assertEqual([m["mes"] for m in meses], sorted([m["mes"] for m in meses], reverse=True))
            self.assertTrue(all(m["feitos"] == m["total"] for m in meses))

    def test_erro_sempre_nao_vira_laco_e_pausar_guarda_o_resto(self):
        import datetime as dt
        from lexsuite import banco as bd, djen, historico as h
        with tempfile.TemporaryDirectory() as tmp:
            b = bd.Banco(os.path.join(tmp, "t.db"))
            n = h.pedir(b, 1, ["TRT2"], hoje=dt.date(2026, 11, 12))
            def falha(*a, **k):
                raise ValueError("Diário com defeito")
            with mock.patch.object(djen, "meta_caderno", side_effect=falha):
                r = h.processar_tudo(b, aviso=lambda *_: None, pausa=0, lote=5)
            self.assertEqual(r["erros"], n)  # cada Diário tentado uma vez; o laço termina
            parar = {"v": False}
            def meta(t, d, *a, **k):
                parar["v"] = True; return None
            with mock.patch.object(djen, "meta_caderno", side_effect=meta):
                r = h.processar_tudo(b, aviso=lambda *_: None, pausa=0, lote=5, parar=lambda: parar["v"])
            self.assertEqual(r["sem_diario"], 1); self.assertEqual(h.situacao(b)["na_fila"], n - 1)

    def test_tela_tem_pausar_e_continuar_a_noite(self):
        with open(os.path.join(_ROBO_, "radar_modelo.html"), encoding="utf-8") as f:
            h = f.read()
        for k in ("saz_noite:", "saz_pausar_ler:", "saz_ocupado:", "function avisoBuscaEstatisticas", "desenharMeses(e.meses)"):
            self.assertIn(k, h)
        self.assertNotIn("mais 30 Diários", h)

if __name__ == "__main__":
    unittest.main()


def _abas_032(valor=None, socios="sim", excluidas=()):
    """Planilha como era na 0.7.32 (dados fictícios): Preferências, Exclusões e Controle."""
    from lexsuite import preferencias as pf
    pref = [list(l) for l in pf.LINHAS_PREFERENCIAS]
    for l in pref:
        if valor is not None and l[0] == "Valor mínimo da causa (R$)":
            l[1] = valor
        if l[0] == "Mostrar sócios e administradores":
            l[1] = socios
    exc = [["Nome ou CNPJ", "Motivo"]] + [[n, "cliente"] for n in excluidas]
    return [{"nome": "Radar", "linhas": [["x"]]}, {"nome": "Preferências", "linhas": pref}, {"nome": "Exclusões", "linhas": exc}] + pf.abas_padrao()


class Revisao0733(unittest.TestCase):
    """Revisão da 0.7.33 (Operação, partes A e B): migração segura, todas as áreas, arquivo danificado, critérios por área,
    chamado escondido e o que as mutações mostraram."""

    def setUp(self):
        self.pasta = tempfile.mkdtemp(); self.base = os.path.join(self.pasta, "LexSuiteONE"); os.makedirs(self.base)
        self.cfg = {"compartilhar": {"pasta": self.pasta}, "radar": {"tribunais": ["TRT2"], "dias_na_pagina": 30}}

    def _planilha(self, frente="trabalhista", **kw):
        from lexsuite import planilha, preferencias as pf
        planilha.escrever_xlsx(pf.caminho(self.base, frente), _abas_032(**kw))

    def test_dois_computadores_comecam_iguais_pela_copia_antes_da_0733(self):
        from lexsuite import planilha, preferencias as pf, radar, banco as bd
        self._planilha(valor=250000, socios="não", excluidas=["A Fictícia Ltda", "B Fictícia Ltda"])
        pc_a, pc_b = tempfile.mkdtemp(), tempfile.mkdtemp()
        self.assertTrue(pf.migrar(pc_a, self.base))
        b = bd.Banco(os.path.join(pc_a, "lexsuite.db"))
        self.assertTrue(radar.gravar_planilha(self.cfg, radar.montar_radar(self.cfg, b), b, "0.7.33", self.pasta, lambda *_: None))
        abas = [a["nome"] for a in planilha.ler_xlsx(pf.caminho(self.base, "trabalhista"))["abas"]]
        self.assertNotIn("Preferências", abas); self.assertIn("Critérios desta leitura", abas)
        self.assertTrue(os.path.exists(pf.copia_antes_0733(self.base, "trabalhista")))  # a cópia de antes ficou guardada
        self.assertTrue(pf.migrar(pc_b, self.base))  # o segundo computador migra da cópia
        for pc in (pc_a, pc_b):
            p = pf.carregar(self.base, pasta=pc)
            self.assertEqual((p["valor_minimo"], p["mostrar_socios"], len(p["exclusoes"])), (250000, False, 2))

    def test_copia_que_falha_impede_regravar(self):
        import shutil
        from lexsuite import planilha, preferencias as pf, radar, banco as bd
        self._planilha(excluidas=["A Fictícia Ltda"])
        b = bd.Banco(os.path.join(tempfile.mkdtemp(), "t.db")); recados = []
        with mock.patch.object(shutil, "copyfile", side_effect=OSError("disco cheio")):
            self.assertFalse(radar.gravar_planilha(self.cfg, radar.montar_radar(self.cfg, b, prefs=pf.padrao()), b, "0.7.33", self.pasta, recados.append))
        self.assertIn("antes da 0.7.33", " ".join(recados))
        self.assertIn("Exclusões", [a["nome"] for a in planilha.ler_xlsx(pf.caminho(self.base, "trabalhista"))["abas"]])

    def test_migracao_adiada_sem_pasta_ou_com_planilha_ilegivel(self):
        from lexsuite import preferencias as pf
        dados = tempfile.mkdtemp()
        self.assertIsNone(pf.migrar(dados, os.path.join(self.pasta, "nao-montado")))
        self.assertFalse(os.path.exists(pf.caminho_criterios(dados)))
        with open(pf.caminho(self.base, "trabalhista"), "wb") as f:
            f.write(b"nao e um xlsx")
        self.assertIsNone(pf.migrar(dados, self.base)); self.assertFalse(os.path.exists(pf.caminho_criterios(dados)))
        self._planilha(valor=300000)
        self.assertTrue(pf.migrar(dados, self.base) is not None)  # na próxima abertura, com a planilha boa, migra
        self.assertEqual(pf.carregar(self.base, pasta=dados)["valor_minimo"], 300000)

    def test_todas_as_areas_recebem_valores_da_trabalhista_e_a_soma_das_exclusoes(self):
        from lexsuite import preferencias as pf
        self._planilha(valor=250000, socios="não", excluidas=["A Fictícia Ltda"])
        self._planilha("tributario", valor=5, excluidas=["T Fictícia Ltda"])
        dados = tempfile.mkdtemp(); pf.migrar(dados, self.base)
        for area in pf.AREAS:
            p = pf.carregar(self.base, frente=area, pasta=dados)
            self.assertEqual((p["valor_minimo"], p["mostrar_socios"]), (250000, False), area)
            self.assertEqual(sorted(e["nome"] for e in p["exclusoes"]), ["A Fictícia Ltda", "T Fictícia Ltda"], area)

    def test_arquivo_danificado_usa_o_anterior_e_nao_o_estraga(self):
        from lexsuite import preferencias as pf
        dados = tempfile.mkdtemp()
        pf.salvar_area(dados, "trabalhista", {"valor_minimo": 111}, [])
        pf.salvar_area(dados, "trabalhista", {"valor_minimo": 222}, [])  # agora o .anterior tem 111
        with open(pf.caminho_criterios(dados), "w", encoding="utf-8") as f:
            f.write("lixo")
        self.assertEqual(pf.criterios_da_area(dados, "trabalhista")[0]["valor_minimo"], 111)  # usa o .anterior
        pf.salvar_area(dados, "civel", {"valor_minimo": 333}, [])
        self.assertEqual(pf.criterios_da_area(dados, "trabalhista")[0]["valor_minimo"], 111)  # a área não salva veio do .anterior
        with open(pf.caminho_criterios(dados) + ".anterior", encoding="utf-8") as f:
            self.assertNotIn("lixo", f.read())  # o ilegível nunca passa por cima do .anterior
        outro = tempfile.mkdtemp()
        with open(pf.caminho_criterios(outro), "w", encoding="utf-8") as f:
            f.write("[]")
        with self.assertRaises(ValueError):
            pf.salvar_area(outro, "trabalhista", {}, [])

    def test_criterios_de_cada_area_na_lista(self):
        from lexsuite import preferencias as pf, radar, banco as bd
        pasta_pc = tempfile.mkdtemp(); b = bd.Banco(os.path.join(pasta_pc, "lexsuite.db"))
        import datetime as dt
        hoje = dt.date.today().isoformat()
        cfg = dict(self.cfg, radar={"tribunais": ["TRT2", "TJSP"], "dias_na_pagina": 30})
        for k, (trib, classe) in enumerate((("TRT2", "ATOrd"), ("TJSP", "Execução Fiscal"))):
            b.guardar_lead({"processo": f"000000{k}-11.2026.5.02.0001", "tribunal": trib, "vara": "1ª Vara",
                            "empresas": ["Cliente Comum Ltda"], "data_publicacao": hoje, "classe": classe}, hoje)
        pf.gravar_criterios(pasta_pc, {"areas": {"trabalhista": {"exclusoes": [{"nome": "Cliente Comum Ltda"}], "mostrar_socios": False},
                                                 "tributario": {"esconder_excluidas": False}}})
        itens = {i["frente"]: i for i in radar.montar_radar(cfg, b)["itens"]}
        self.assertTrue(itens["trabalhista"]["excluida"]); self.assertFalse(itens["tributario"]["excluida"])
        self.assertTrue(itens["trabalhista"]["esconder_exc"]); self.assertFalse(itens["tributario"]["esconder_exc"])

    def test_chamado_escondido(self):
        import http.client, json as _j, threading
        from lexsuite import app
        self.assertFalse(app.CHAMADO_LIGADO)
        srv = app.Servidor(("127.0.0.1", 0), tempfile.mkdtemp())
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            with mock.patch.object(conta, "enviar_chamado") as env:
                c = http.client.HTTPConnection("127.0.0.1", srv.server_address[1], timeout=10)
                c.request("POST", "/chamado", body=_j.dumps({"categoria": "erro", "texto": "x"}), headers={"X-LexSuite": "1", "Content-Type": "application/json"})
                r = c.getresponse(); d = _j.loads(r.read()); c.close()
                self.assertEqual(r.status, 403); self.assertTrue(d["desligado"]); self.assertFalse(env.called)
        finally:
            srv.shutdown(); srv.server_close()
        with open(os.path.join(_ROBO_, "radar_modelo.html"), encoding="utf-8") as f:
            h = f.read()
        self.assertIn("if (chamadoLigado()) window.LEX_CHAMADO = abrirChamado;", h)
        i = h.index('"0.7.33": {'); self.assertNotIn("chamado", h[i:h.index('"0.7.32": {')].lower())
        with open(os.path.join(_ROBO_, "..", "paginas", "manual.html"), encoding="utf-8") as f:
            self.assertNotIn("Abrir um chamado", f.read())

    def test_mutacoes_que_sobreviviam(self):
        from lexsuite import preferencias as pf
        for codigo in (400, 404):  # 400 e 404 das duas fontes, não só 404
            def recusa(url, *a, codigo=codigo, **k):
                raise rede.ErroHTTP(codigo, url, "x")
            with mock.patch.object(rede, "pedir_json", side_effect=recusa):
                self.assertEqual(cnpj.consultar(ALFA)["situacao"], "fonte_sem_suporte")
        visto = {}
        conta.enviar_chamado({"conta": {"codigo": "LEX-ABCD-EFGH"}}, "0.7.33", {"categoria": "erro", "texto": "x", "extra": "nao vai"},
                             pedir=lambda u, c, **k: visto.update(c) or {"ok": True})
        self.assertNotIn("extra", visto)
        self.assertEqual(set(visto) - {"acao", "codigo", "instalacao", "versao", "categoria", "texto", "trilha", "windows", "python", "pode_responder"}, set())
        dados = tempfile.mkdtemp()
        pf.salvar_area(dados, "trabalhista", {}, []); pf.salvar_area(dados, "trabalhista", {}, [])
        self.assertTrue(os.path.exists(pf.caminho_criterios(dados) + ".anterior"))
        self.assertEqual(pf.linhas_criterios(pf.padrao())[1][0], "Área / Area")

    def test_fila_limpa_depois_de_enviar(self):
        from lexsuite import app
        pasta = tempfile.mkdtemp(); arq = os.path.join(pasta, "saida", "chamados-pendentes.json")
        app._gravar_lista_json(arq, [{"categoria": "erro", "texto": "a", "cliente_id": "1"}, {"categoria": "erro", "texto": "b", "cliente_id": "2"}])
        self.assertEqual(app.enviar_pendentes(pasta, {}, enviar=lambda c, v, d: {"ok": True, "numero": 1}), 0)
        self.assertEqual(app._lista_json(arq), [])
        self.assertEqual(len(app._lista_json(os.path.join(pasta, "saida", "chamados.json"))), 2)
