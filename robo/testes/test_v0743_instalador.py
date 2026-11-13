"""0.7.43 (Operação, 13/Nov, KR Law): instalador tenta o PowerShell e a pasta do usuário quando o tar.exe é barrado."""

import os
import unittest

_RAIZ_ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Instalador0743(unittest.TestCase):
    """Operação, 13/Nov (KR Law): o tar.exe foi barrado em C:\\LexSuiteONE; tenta o PowerShell e a pasta do usuário."""

    def test_tenta_powershell_e_pasta_do_usuario(self):
        for nome in ("INSTALAR.bat", "INSTALAR-COMPLETO.bat"):
            with open(os.path.join(_RAIZ_, "instalador", nome), "rb") as f:
                bruto = f.read()
            t = bruto.decode("ascii")
            self.assertEqual(t.count("\r\n"), t.count("\n"), nome)  # CRLF em todas as linhas
            self.assertEqual(t.count("call :extrair_pacote"), 2, nome)
            self.assertIn("Expand-Archive -LiteralPath (Join-Path $env:T 'pacote.zip') -DestinationPath $env:DEST", t)
            self.assertIn('if exist "%DEST%\\lexsuite.db" goto falha_extrair', t)  # instalação existente não muda de pasta
            self.assertLess(t.index('if exist "%DEST%\\lexsuite.db" goto falha_extrair'), t.index('set "DEST=%LOCALAPPDATA%\\LexSuiteONE"\r\nset "TENTOU='))
            self.assertIn("antivirus", t[t.index(":falha_extrair"):t.index(":sem_python")])
            # revisão: numa atualização, só conta o arquivo que veio agora (o antigo sai do caminho e volta se nada extrair)
            sub = t[t.index("\r\n:extrair_pacote\r\n"):]
            self.assertLess(sub.index('move /y "%DEST%\\lexsuite_robo.py" "%DEST%\\lexsuite_robo.py.antes"'), sub.index("tar.exe -xf"))
            self.assertIn('move /y "%DEST%\\lexsuite_robo.py.antes" "%DEST%\\lexsuite_robo.py"', sub)
            self.assertIn('if not "%EXTRAIU%"=="sim" goto falha_extrair', t)
            self.assertGreater(t.index("\r\n:extrair_pacote\r\n"), t.rindex("exit /b"))  # a sub-rotina fica depois do último exit


if __name__ == "__main__":
    unittest.main()
