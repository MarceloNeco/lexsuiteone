"""Decisão do dono (15/Nov/2026): a versão do código só passa com a folha da Definition of done preenchida
(`documentacao/dod/<versão>.md`, modelo em `documentacao/dod/LEIA-ME.md`). Cada um dos 13 pontos diz "conferido: …" ou
"não se aplica: …", com o porquê. Falha aqui = a versão não está pronta (o revisor e a Operação tratam como bloqueio)."""

import os
import re
import sys
import unittest

_ROBO_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RAIZ_ = os.path.dirname(_ROBO_)
sys.path.insert(0, _ROBO_)

from lexsuite import VERSAO  # noqa: E402

PONTOS = ("1. Manual e orientações", "2. AssistONE: ajuda de cada tela", "3. AssistONE: tour", "4. AssistONE: busca",
          "5. Wizard (primeiro acesso)", "6. Novidades da versão", "7. Termos e condições",
          "8. E-mail de boas-vindas e comunicações", "9. RootifyONE, ArchONE e EaglePlanONE", "10. Retrocompatibilidade",
          "11. Segurança e LGPD", "12. Qualidade verificável", "13. Registro")
PASTA = os.path.join(_RAIZ_, "documentacao", "dod")


def ler_folha(versao):
    with open(os.path.join(PASTA, versao + ".md"), encoding="utf-8") as f:
        return f.read()


def faltas(texto):
    """Os pontos que faltam ou estão em branco (sem "conferido:"/"não se aplica:" seguido de pelo menos 15 caracteres)."""
    saida = []
    for p in PONTOS:
        linha = next((l for l in texto.splitlines() if l.startswith("- **" + p + "**")), None)
        if linha is None:
            saida.append(p + " (falta)")
            continue
        m = re.search(r"(conferido|não se aplica):\s*(.*)$", linha)
        if not m or len(m.group(2).strip(" .…")) < 15:
            saida.append(p + " (em branco)")
    return saida


class FolhaDaVersao(unittest.TestCase):
    def test_a_versao_do_codigo_tem_folha(self):
        self.assertTrue(os.path.exists(os.path.join(PASTA, VERSAO + ".md")),
                        f"Falta documentacao/dod/{VERSAO}.md (modelo em documentacao/dod/LEIA-ME.md)")

    def test_os_13_pontos_preenchidos(self):
        self.assertEqual(faltas(ler_folha(VERSAO)), [])

    def test_o_modelo_tem_os_13_pontos(self):
        with open(os.path.join(PASTA, "LEIA-ME.md"), encoding="utf-8") as f:
            m = f.read()
        for p in PONTOS:
            self.assertIn("- **" + p + "**", m, p)

    def test_folha_em_branco_nao_passa(self):
        with open(os.path.join(PASTA, "LEIA-ME.md"), encoding="utf-8") as f:
            modelo = f.read()
        self.assertEqual(len(faltas(modelo)), 13)  # o modelo, só com "conferido: …", conta como em branco


if __name__ == "__main__":
    unittest.main()
