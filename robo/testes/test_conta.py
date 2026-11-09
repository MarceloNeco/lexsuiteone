"""Licença do escritório: código de cliente conferido na nuvem da SolverONE (v0.7.7)."""
import datetime as dt
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexsuite import conta  # noqa: E402

HOJE = dt.date(2026, 11, 10)
CODIGO = "LEX-7K4M-2PQ9"


def resposta(r):
    return lambda url, corpo, **kw: r


def sem_internet(url, corpo, **kw):
    raise RuntimeError("Sem resposta")


class Codigo(unittest.TestCase):
    def test_formato(self):
        self.assertTrue(conta.valido(CODIGO))
        self.assertTrue(conta.valido("lex 7k4m 2pq9"))
        self.assertEqual(conta.normalizar("lex7k4m2pq9"), CODIGO)
        for ruim in ("", "LEX-0000-1111", "LEX-ABCD", "ABC-7K4M-2PQ9"):
            self.assertFalse(conta.valido(ruim), ruim)


class Licenca(unittest.TestCase):
    def test_sem_codigo_bloqueia(self):
        cfg = {}
        conta.verificar(cfg, "0.7.7", HOJE, pedir=resposta({"ok": True}))
        self.assertIn("código de cliente", conta.bloqueio(cfg, HOJE))

    def test_ativa_libera_e_registra_instalacao(self):
        enviado = {}
        cfg = {"conta": {"codigo": CODIGO}}
        conta.verificar(cfg, "0.7.7", HOJE, pedir=lambda url, corpo, **kw: (enviado.update(corpo), {"ok": True, "validade": "2027-01-31"})[1])
        self.assertEqual(conta.bloqueio(cfg, HOJE), "")
        self.assertEqual(set(enviado), {"codigo", "instalacao", "versao"})  # nada pessoal sai daqui
        self.assertEqual(len(cfg["conta"]["instalacao"]), 16)
        self.assertEqual(conta.situacao(cfg)["validade"], "2027-01-31")  # 0.7.21: a validade vai em linha própria na tela

    def test_desativada_bloqueia_com_contato(self):
        cfg = {"conta": {"codigo": CODIGO}}
        conta.verificar(cfg, "0.7.7", HOJE, pedir=resposta({"ok": False, "motivo": "desativado", "mensagem": "Fale com o financeiro."}))
        motivo = conta.bloqueio(cfg, HOJE)
        self.assertIn("desativada", motivo)
        self.assertIn("Fale com o financeiro.", motivo)
        self.assertIn("judicial@solverone.com.br", motivo)

    def test_codigo_desconhecido(self):
        cfg = {"conta": {"codigo": CODIGO}}
        conta.verificar(cfg, "0.7.7", HOJE, pedir=resposta({"ok": False, "motivo": "codigo_desconhecido"}))
        self.assertIn("não existe", conta.bloqueio(cfg, HOJE))

    def test_queda_da_solverone_nao_para_o_escritorio(self):
        cfg = {"conta": {"codigo": CODIGO}}
        conta.verificar(cfg, "0.7.7", HOJE, pedir=resposta({"ok": True}))
        dez_dias = HOJE + dt.timedelta(days=10)
        conta.verificar(cfg, "0.7.7", dez_dias, pedir=sem_internet)
        self.assertEqual(conta.bloqueio(cfg, dez_dias), "")
        tarde = HOJE + dt.timedelta(days=conta.DIAS_SEM_RESPOSTA + 1)
        conta.verificar(cfg, "0.7.7", tarde, pedir=sem_internet)
        self.assertIn("Faz mais de", conta.bloqueio(cfg, tarde))

    def test_nunca_confirmado_e_sem_internet_bloqueia(self):
        cfg = {"conta": {"codigo": CODIGO}}
        conta.verificar(cfg, "0.7.7", HOJE, pedir=sem_internet)
        self.assertIn("Ainda não consegui confirmar", conta.bloqueio(cfg, HOJE))

    def test_resposta_estranha_conta_como_sem_resposta(self):
        cfg = {"conta": {"codigo": CODIGO, "ultima_ok": HOJE.isoformat(), "resposta": "ok"}}
        conta.verificar(cfg, "0.7.7", HOJE, pedir=resposta(["nao", "e", "dict"]))
        self.assertEqual(cfg["conta"]["resposta"], "sem_resposta")
        self.assertEqual(conta.bloqueio(cfg, HOJE), "")



class Documento(unittest.TestCase):
    def test_cnpj_numerico_e_com_letras(self):
        self.assertTrue(conta.cnpj_valido("11.222.333/0001-81"))
        self.assertTrue(conta.cnpj_valido("12.ABC.345/01DE-35"))  # exemplo da Receita para o formato de jul/2026
        for ruim in ("11.222.333/0001-82", "00.000.000/0000-00", "12.ABC.345/01DE-36", "123"):
            self.assertFalse(conta.cnpj_valido(ruim), ruim)

    def test_cpf_e_passaporte(self):
        self.assertTrue(conta.cpf_valido("529.982.247-25"))
        self.assertFalse(conta.cpf_valido("529.982.247-26"))
        self.assertFalse(conta.cpf_valido("111.111.111-11"))
        self.assertEqual(conta.documento("passaporte", "fd 123456"), "FD123456")
        self.assertEqual(conta.documento("passaporte", "12"), "")
        self.assertEqual(conta.documento("cpf", "529.982.247-25"), "52998224725")


class Cadastro(unittest.TestCase):
    def test_envia_e_guarda(self):
        enviado = {}
        cfg = {"conta": {"codigo": CODIGO}}
        ok, motivo = conta.cadastrar(cfg, "0.7.7", "Ana@Escritorio.com.br", "Ana Lima", "11.222.333/0001-81", "Sócio ou sócia",
                                     pedir=lambda u, c, **k: (enviado.update(c), {"ok": True})[1])
        self.assertEqual((ok, motivo), (True, ""))
        self.assertEqual((enviado["acao"], enviado["email"], enviado["doc_tipo"], enviado["documento"]), ("cadastrar", "ana@escritorio.com.br", "cnpj", "11222333000181"))
        self.assertEqual(cfg["usuario"]["email"], "ana@escritorio.com.br")

    def test_recusas(self):
        cfg = {"conta": {"codigo": CODIGO}}
        self.assertFalse(conta.cadastrar(cfg, "0.7.7", "sem-arroba", "Ana", "11.222.333/0001-81")[0])
        self.assertFalse(conta.cadastrar(cfg, "0.7.7", "a@b.com", "Ana", "11.222.333/0001-82")[0])
        ok, motivo = conta.cadastrar(cfg, "0.7.7", "a@b.com", "Ana", "529.982.247-25", doc_tipo="cpf",
                                     pedir=resposta({"ok": False, "motivo": "email_em_outro_escritorio"}))
        self.assertFalse(ok)
        self.assertIn("outro escritório", motivo)
        ok, motivo = conta.cadastrar(cfg, "0.7.7", "b@b.com", "Bia", "529.982.247-25", doc_tipo="cpf",
                                     pedir=resposta({"ok": False, "motivo": "limite_de_pessoas"}))
        self.assertIn("número máximo", motivo)



class RegistroDeErro(unittest.TestCase):
    def test_tira_o_nome_da_pasta_do_usuario(self):
        t = conta._sem_caminho_pessoal('File "C:\\Users\\Fulano de Tal\\AppData\\x.py", c:/users/ana/b.txt')
        self.assertNotIn("Fulano", t)
        self.assertNotIn("ana/", t)

    def test_envia_sem_travar(self):
        enviado = {}
        self.assertTrue(conta.registrar_erro({"conta": {"codigo": CODIGO, "instalacao": "0123456789abcdef"}}, "0.7.7", "leitura", "erro X",
                                             pedir=lambda u, c, **k: enviado.update(c)))
        self.assertEqual((enviado["acao"], enviado["origem"], enviado["codigo"]), ("registro", "programa", CODIGO))
        self.assertFalse(conta.registrar_erro({}, "0.7.7", "leitura", "erro", pedir=sem_internet))


if __name__ == "__main__":
    unittest.main()
