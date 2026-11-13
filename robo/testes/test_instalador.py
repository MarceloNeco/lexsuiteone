"""Contato do suporte, instalador de um arquivo e arquivos gerados a partir da marca (v0.7.6)."""
import os
import re
import subprocess  # nosec B404 - só para rodar a conferência da marca, com argumentos fixos
import sys
import unittest

ROBO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAIZ = os.path.dirname(ROBO)
sys.path.insert(0, ROBO)

from lexsuite import preferencias  # noqa: E402

INSTALADOR = os.path.join(RAIZ, "instalador", "INSTALAR.bat")


class Suporte(unittest.TestCase):
    def test_padrao_e_judicial(self):
        self.assertEqual(preferencias.SUPORTE, "judicial@solverone.com.br")
        self.assertEqual(preferencias.padrao()["controle"]["suporte"], "judicial@solverone.com.br")
        linha = [l for l in preferencias.LINHAS_CONTROLE if l[0] == "suporte"][0]
        self.assertEqual(linha[1], "judicial@solverone.com.br")

    def test_integracao_nunca_e_suporte(self):
        for codigo in ("lexsuite/preferencias.py", "lexsuite/compartilhar.py", "MANUAL-DO-ESCRITORIO.html"):
            with open(os.path.join(ROBO, codigo), encoding="utf-8") as f:
                texto = f.read()
            self.assertNotRegex(texto, r"[Ss]uporte[^\n]{0,40}integracao@", codigo)


@unittest.skipUnless(os.path.exists(INSTALADOR), "instalador fora do pacote")
class Instalador(unittest.TestCase):
    def setUp(self):
        with open(INSTALADOR, "rb") as f:
            self.bruto = f.read()
        self.texto = self.bruto.decode("ascii")

    def test_formato_windows(self):
        self.assertNotIn(b"\n", self.bruto.replace(b"\r\n", b""), "fim de linha precisa ser CRLF")
        self.assertTrue(all(b < 128 for b in self.bruto), "só ASCII: acento quebra no Prompt de Comando")

    def test_chave_publica_e_a_do_pacote(self):
        with open(os.path.join(ROBO, "chave_publica.txt"), encoding="utf-8") as f:
            chave = "".join(f.read().split()).lower()
        self.assertIn('set "CHAVE=%s"' % chave, self.texto)

    def test_confere_antes_de_instalar(self):
        ordem = [self.texto.index(t) for t in ("instalar.txt", "certutil.exe -hashfile", "call :extrair_pacote", "INSTALAR-PYTHON.bat", "CreateShortcut", "ABRIR.bat")]
        self.assertEqual(ordem, sorted(ordem))
        self.assertIn('if /i not "%H%"=="%sha256%" goto hash_ruim', self.texto)

    def test_pede_e_confere_o_codigo_antes_de_baixar(self):
        self.assertLess(self.texto.index('set /p "CODIGO='), self.texto.index("instalar.txt"))
        self.assertLess(self.texto.index('"versao\\":\\"instalador'), self.texto.index("call :extrair_pacote"))
        self.assertIn("conta-inicial.json", self.texto)
        self.assertIn('\\"codigo\\":\\"%CODIGO_OK%\\",\\"instalacao\\":\\"%INST%\\"}', self.texto)  # todo aviso de erro diz a origem

    def test_programa_le_o_codigo_do_instalador(self):
        import json, tempfile
        from lexsuite import config
        pasta = tempfile.mkdtemp()
        with open(os.path.join(pasta, "conta-inicial.json"), "w", encoding="utf-8") as f:
            json.dump({"codigo": "LEX-7K4M-2PQ9", "instalacao": "0123456789abcdef"}, f)
        cfg = config.carregar(os.path.join(pasta, "config.json"), aviso=lambda *_: None)
        self.assertEqual((cfg["conta"]["codigo"], cfg["conta"]["instalacao"]), ("LEX-7K4M-2PQ9", "0123456789abcdef"))

    def test_nao_aceita_qualquer_variavel_do_site(self):
        self.assertNotRegex(self.texto, r'set "%%a=%%b"')
        self.assertIn('findstr /r /x /c:"LexSuiteONE-RADAR-atualizacao-', self.texto)

    def test_gerados_em_dia(self):
        r = subprocess.run([sys.executable, os.path.join(RAIZ, "ferramentas", "marca.py"), "--conferir"],
                           capture_output=True, text=True, timeout=60)  # nosec B603
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
