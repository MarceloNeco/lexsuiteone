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
        self.assertIn("mesmoCod_ = !!(trocandoLic && APP && APP.conta && APP.conta.codigo === cod)", self.h)
        self.assertIn("if (mesmoCod_) Promise.resolve(depois_).then(function () { return conferirConta(); })", self.h)  # 0.7.36: encadeado depois do carregar  # revisão: o mesmo código confere pela rota, sem /config
        b_ = self.h[self.h.index('$("c-conferir-lic").addEventListener("click"'):][:1400]
        self.assertIn("conferirConta().then", b_)  # revisão: o botão chama a conferência de verdade
        self.assertIn('ok === "sem" ? t("lic_sem_internet")', b_)  # e não diz "ativa" sem conexão
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



class SinalGuardado(unittest.TestCase):
    """0.7.35 (dono): ações antigas sem o sinal anotado ganham o sinal pelo texto guardado; o rótulo não cita versão."""

    def test_sinal_pelo_texto(self):
        import sys
        sys.path.insert(0, _ROBO_)
        from lexsuite import radar
        self.assertEqual(radar.sinal_guardado({"tipo": "Lista de Distribuição"}), "lista de distribuição")
        self.assertEqual(radar.sinal_guardado({"tipo": "Notificação", "texto_curto": "Processo distribuído. ATSum 1002019"}), "lista de distribuição")
        self.assertEqual(radar.sinal_guardado({"texto_curto": "Fica designada audiência inicial para 10/12"}), "audiência inicial")
        self.assertEqual(radar.sinal_guardado({"texto_curto": "Intimação para manifestação"}), "")
        self.assertEqual(radar.sinal_guardado({}), "")
        h = ler(_ROBO_, "radar_modelo.html")
        self.assertNotIn("antes da 0.7.16", h); self.assertIn('sinal_antigo: "Sem sinal registrado"', h)


class SinalComExemplos(unittest.TestCase):
    """Revisão da 0.7.35: pelo caminho real (DJEN → leads), o sinal derivado é igual ao gravado nos exemplos."""

    def test_exemplos_do_repositorio(self):
        import json
        import sys
        sys.path.insert(0, _ROBO_)
        from lexsuite import djen, radar
        d = json.loads(ler(_ROBO_, "exemplos", "dia_exemplo.json"))
        total = 0
        for rod in d["rodadas"]:
            for lead in djen.leads([djen.normalizar(i) for i in rod.get("items", [])]):
                original = lead.get("sinal") or ""
                sem = dict(lead); sem.pop("sinal", None)
                self.assertEqual(radar.sinal_guardado(sem), original, lead.get("processo"))
                total += 1
        self.assertGreater(total, 20)


class Novidades0735(unittest.TestCase):
    def test_traz_as_linhas_da_0734(self):
        h = ler(_ROBO_, "radar_modelo.html")
        bloco = h[h.index('"0.7.35": {'):h.index('"0.7.34": {')]
        for x in ("Reconhecimento automático do aceite", "Já aceitei", "Automatic recognition of the terms", "I have accepted"):
            self.assertIn(x, bloco)
        self.assertNotIn("Melhorias de acessibilidade e correções.", h[h.index('"0.7.34": {'):h.index('"0.7.33": {')])


if __name__ == "__main__":
    unittest.main()
