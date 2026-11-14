"""0.7.47: os instaladores novos (passo 0, os seis sinais, a tarefa às claras). Vai junto com instalador/*.bat: os dois só
entram na main quando a Operação publicar a 0.7.47 (o site serve o instalador na hora)."""

import os
import unittest

_ROBO_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RAIZ_ = os.path.dirname(_ROBO_)


class Instalador(unittest.TestCase):
    def setUp(self):
        self.bats = {}
        for n in ("INSTALAR.bat", "INSTALAR-COMPLETO.bat"):
            with open(os.path.join(_RAIZ_, "instalador", n), "rb") as f:
                self.bats[n] = f.read().decode("ascii")

    def test_passo_0_antes_de_baixar(self):
        for n, t in self.bats.items():
            i0 = t.index("Conferindo este computador antes de instalar")
            self.assertLess(i0, t.index('set /p "CODIGO='), n)
            self.assertLess(t.index("goto dentro_do_zip"), t.index("where curl.exe"), n)
            for trecho in ("Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct", "FirewallProduct",
                           "'IDENT=0'", 'curl.exe -s -o nul -m 15 "%SITE%/', '&& set "NET_NUVEM=1"', "goto rede_recusada",
                           "Antivirus encontrado: %AV%.", "Programas novos costumam ser barrados por ele. Antes de continuar, cadastre a excecao da pasta",
                           "C:\\LexSuiteONE ^(veja judicial.solverone.com.br/antivirus.html^) ou peca a TI.", 'set /p "PRONTO=  Depois aperte Enter'):
                self.assertIn(trecho, t, n)

    def test_seis_sinais_viram_mensagem(self):
        for n, t in self.bats.items():
            self.assertIn("-replace '[^A-Za-z0-9 .,+-]', ''", t)  # sem parênteses no nome do antivírus (quebrariam o bloco de :erro)
            for s in ("zip_temp", "bloqueio_gravacao", "processo_morto", "tarefa_falhou", "rede_recusada"):
                self.assertIn(f'set "SINAL={s}"', t, (n, s))
            self.assertIn('more < "%~f0:Zone.Identifier"', t)  # smartscreen: não é bloqueio, só orienta
            self.assertIn("o programa ainda nao tem assinatura digital", t)
            self.assertIn('\\"antivirus\\":\\"%AV%\\",\\"antivirus_ligado\\":\\"%AVON_J%\\",\\"sinal\\":\\"%SINAL%\\"', t)
            for rotulo in (":orientar", ":passos_bitdefender", ":passos_defender", ":texto_ti"):
                self.assertIn("\r\n" + rotulo + "\r\n", t, (n, rotulo))
            self.assertGreaterEqual(t.count("call :orientar"), 4, n)

    def test_nunca_manda_desligar(self):
        for n, t in self.bats.items():
            for linha in t.lower().splitlines():
                if "deslig" in linha and "antivirus" in linha:
                    self.assertRegex(linha, r"nao e (preciso|necessario) desligar", (n, linha))

    def test_texto_para_a_ti_e_o_da_pagina(self):
        with open(os.path.join(_RAIZ_, "paginas", "antivirus.html"), encoding="utf-8") as f:
            pagina = f.read()
        for item in ("C:\\LexSuiteONE\\python\\pythonw.exe", "LexSuiteONE Radar", "Se algum item foi para a quarentena"):
            self.assertIn(item, pagina)
            for n, t in self.bats.items():
                self.assertIn(item.replace("á", "a"), t, (n, item))

    def test_cria_a_tarefa_as_claras_e_confere(self):
        for n, t in self.bats.items():
            self.assertIn("Agora vou criar a leitura automatica", t)
            self.assertIn('"%DEST%\\lexsuite_robo.py" tarefa > "%T%\\tarefa.txt"', t)
            self.assertNotIn("/sc daily", t)  # revisão: sempre o XML da pasta do programa (bateria e horário perdido)
            self.assertIn('schtasks.exe /create /f /tn "LexSuiteONE Radar" /xml "%DEST%\\tarefa.xml"', t)
            self.assertNotIn("%TEMP%\\tarefa", t); self.assertNotIn('%T%\\tarefa.xml', t)
            self.assertIn('schtasks.exe /query /tn "LexSuiteONE Radar" >nul 2>&1 || goto tarefa_falhou', t)
            self.assertLess(t.index("5 de 6  Agora vou criar"), t.index("6 de 6  Criando o atalho"))
            self.assertIn('tasklist /fi "imagename eq pythonw.exe"', t)  # processo morto


if __name__ == "__main__":
    unittest.main()
