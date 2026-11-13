"""0.7.38 (decisão do dono, pergunta 19, e ressalvas da revisão da 0.7.37): só leitura do código da tela."""

import os
import unittest

_ROBO_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(_ROBO_, "radar_modelo.html"), encoding="utf-8") as _f:
    HTML = _f.read()


class Tela0738(unittest.TestCase):
    def test_nao_couberam_em_dourado(self):
        self.assertIn('el("span", "txt-latao", " " + t("rg_copiar_limite"', HTML)
        self.assertNotIn('el("span", "erro", " " + t("rg_copiar_limite"', HTML)
        self.assertIn(".txt-latao { color: var(--latao-texto); font-weight: 700; }", HTML)

    def test_acrescentada_fica_ate_digitar(self):
        self.assertIn('aviso(t("rg_exc_ok", { n: nome_ }), "txt-verde ok-acr");', HTML)
        self.assertIn('if (!n) { if (!nMsg.querySelector(".ok-acr")) aviso(""); return Promise.resolve(); }', HTML)
        self.assertIn('if (nMsg.querySelector(".ok-acr")) aviso("");', HTML)

    def test_versao_e_novidades(self):
        from lexsuite import VERSAO
        self.assertEqual(VERSAO, "0.7.38")
        bloco = HTML[HTML.index('"0.7.38": {'):HTML.index('"0.7.37": {')]
        self.assertIn('pt: ["Melhorias no design e na navegação.", "Melhorias de acessibilidade e correções."]', " ".join(bloco.split()))
        self.assertIn('en: ["Design and navigation improvements.", "Accessibility improvements and fixes."]', " ".join(bloco.split()))

    def test_manual(self):
        with open(os.path.join(_ROBO_, "..", "paginas", "manual.html"), encoding="utf-8") as f:
            man = f.read()
        self.assertIn("o aviso sai em dourado", man)
        self.assertIn("fica até você digitar a próxima", man)
        self.assertIn("um filtro com uma opção só", man)


if __name__ == "__main__":
    unittest.main()
