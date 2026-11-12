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

if __name__ == "__main__":
    unittest.main()
