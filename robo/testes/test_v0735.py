"""0.7.35 (teste do dono na 0.7.33, 12/Nov): tela de abertura, Conferir agora, pasta, sazonalidade, faixa da leitura, e-mail."""

import os
import re
import unittest

_ROBO_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_RAIZ_ = os.path.dirname(_ROBO_)


def ler(*p):
    with open(os.path.join(*p), encoding="utf-8") as f:
        return f.read()


class Tela0735(unittest.TestCase):
    def setUp(self):
        self.h = ler(_ROBO_, "radar_modelo.html")

    def test_abertura_visivel_e_some_nos_dois_modos(self):
        tag = re.search(r'<div class="carregando abertura" id="carregando"[^>]*>', self.h).group(0)
        self.assertNotIn("hidden", tag)
        self.assertIn("RADAR JUDICIAL", self.h[self.h.index(tag):self.h.index(tag) + 300])
        self.assertIn("aplicarDados(d); fimAbertura();", self.h)
        self.assertIn("carregandoPer = 0; fimAbertura();", self.h)  # erro na carga também tira a abertura
        self.assertIn("else { tudo(); fimAbertura(); }", self.h)   # página da pasta saida (sem programa)

    def test_licenca_conferir_agora_e_trocar_com_o_mesmo_codigo(self):
        self.assertIn('id="c-conferir-lic"', self.h)
        self.assertIn('$("c-conferir-lic").addEventListener("click"', self.h)
        self.assertIn("(trocandoLic || !(APP && APP.conta && APP.conta.codigo === cod))", self.h)
        self.assertIn("trocandoLic = false; $(\"config\").hidden = true;", self.h)

    def test_pasta_abrir_no_windows_e_titulo_unico(self):
        self.assertIn('id="c-abrir-pasta"', self.h)
        self.assertIn('class="campo-conf so-campo"><span id="c-l-pasta" class="so-leitor">', self.h)

    def test_continuar_a_noite_parada(self):
        self.assertIn("bx.hidden = true; bn.hidden = !(h.na_fila > 0);", self.h)

    def test_faixa_da_leitura_compacta(self):
        self.assertIn('el("div", "rodando-linha")', self.h)
        self.assertIn('el("details", "log-det")', self.h)
        self.assertNotIn('.forEach(function (m) { box.appendChild(el("span", "log"', self.h)

    def test_janelas_largas_e_textos(self):
        self.assertIn('$("janela").classList.add("larga")', self.h)
        self.assertIn('j.classList.remove("larga")', self.h)
        for k in ("lic_conferir", "lic_conferida_ok", "abrir_pasta_win", "ver_mensagens"):
            self.assertEqual(len(re.findall(r"\b%s: \"" % k, self.h)), 2, k)
        self.assertNotIn("A tela ficou fechada ou escondida", self.h)
        self.assertIn('"0.7.35": {', self.h)


class Email0735(unittest.TestCase):
    def test_aceite_em_uma_frase_e_nao_responde_em_linha_propria(self):
        h = ler(_RAIZ_, "docs", "email", "email-boas-vindas.html")
        t = ler(_RAIZ_, "docs", "email", "email-boas-vindas.txt")
        for x in (h, t):
            self.assertNotIn("o programa mostra o mesmo link", x)
            self.assertIn("Você pode aceitar agora ou depois de instalar:", x)
        self.assertIn("</a>.<br>Este e-mail saiu de um endereço automático e <b>não</b> recebe respostas.", h)
        self.assertIn("{{contato}}.\nEste e-mail saiu de um endereço automático e NÃO recebe respostas.", t)


if __name__ == "__main__":
    unittest.main()


class SinalGuardado(unittest.TestCase):
    """0.7.35 (dono): ações antigas sem o sinal anotado ganham o sinal pelo texto guardado; o rótulo não cita versão."""

    def test_sinal_pelo_texto(self):
        import sys
        sys.path.insert(0, _ROBO_)
        from lexsuite import radar
        self.assertEqual(radar.sinal_guardado({"tipo": "Lista de Distribuição"}), "lista de distribuição")
        self.assertEqual(radar.sinal_guardado({"texto_curto": "Fica designada audiência inicial para 10/12"}), "audiência inicial")
        self.assertEqual(radar.sinal_guardado({"texto_curto": "Intimação para manifestação"}), "")
        self.assertEqual(radar.sinal_guardado({}), "")
        h = ler(_ROBO_, "radar_modelo.html")
        self.assertNotIn("antes da 0.7.16", h); self.assertIn('sinal_antigo: "Sem sinal registrado"', h)
