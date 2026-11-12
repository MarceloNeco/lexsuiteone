"""0.7.36 (teste do dono na 0.7.35 e ressalvas da Operação): dados fictícios, sem internet."""

import http.client
import json
import os
import re
import sys
import tempfile
import threading
import unittest
from unittest import mock

_ROBO_ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROBO_)

from lexsuite import app, conta, radar  # noqa: E402


def ler(*partes):
    with open(os.path.join(_ROBO_, *partes), encoding="utf-8") as f:
        return f.read()


CFG = {"conta": {"codigo": "LEX-ABCD-EFGH", "instalacao": "0123456789abcdef", "resposta": "aceite_pendente",
                 "aceite": {"aceito": False, "link": "https://judicial.solverone.com.br/aceite.html#codigo=LEX-ABCD-EFGH"}},
       "radar": {"tribunais": ["TRT2"]}}


class Servidor(unittest.TestCase):
    def setUp(self):
        self.pasta = tempfile.mkdtemp()
        with open(os.path.join(self.pasta, "config.json"), "w", encoding="utf-8") as f:
            json.dump(CFG, f)
        self.srv = app.Servidor(("127.0.0.1", 0), self.pasta)
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.addCleanup(self.srv.server_close)
        self.addCleanup(self.srv.shutdown)

    def pedir(self, rota, corpo=None):
        c = http.client.HTTPConnection("127.0.0.1", self.srv.server_address[1], timeout=20)
        c.request("POST", rota, body=json.dumps(corpo or {}), headers={"X-LexSuite": "1", "Content-Type": "application/json"})
        r = c.getresponse(); d = json.loads(r.read()); c.close(); return d


class ConferirOcupado(Servidor):
    """Ressalva (1) da Operação: com leitura em andamento, a rota diz "ocupado" e não vai à internet."""

    def test_durante_a_leitura_diz_ocupado_sem_rede(self):
        self.srv.estado.rodando = True
        self.addCleanup(setattr, self.srv.estado, "rodando", False)
        with mock.patch.object(conta.rede, "pedir_json") as rede_:
            d = self.pedir("/conta/conferir")
        rede_.assert_not_called()
        self.assertFalse(d["ok"]); self.assertTrue(d.get("ocupado")); self.assertNotIn("sem_internet", d)
        self.assertFalse(d["conta"]["ok"])
        with open(os.path.join(self.pasta, "config.json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f)["conta"]["resposta"], "aceite_pendente")

    def test_sem_leitura_nao_diz_ocupado(self):
        nuvem = lambda url, corpo, **k: {"ok": True, "aceite": {"aceito": True}}
        with mock.patch.object(conta.rede, "pedir_json", side_effect=nuvem):
            d = self.pedir("/conta/conferir")
        self.assertTrue(d["ok"]); self.assertNotIn("ocupado", d)


class SinalNoItem(unittest.TestCase):
    """Ressalva (2): o item que vai para a tela (/dados) leva o sinal pelo texto quando a ação não o tem anotado."""

    def test_item_sem_sinal_recebe_pelo_texto(self):
        lead = {"processo": "0000001-00.2026.5.02.0001", "tribunal": "TRT2", "data": "2026-11-10", "empresa": "Empresa Exemplo Ltda",
                "texto_curto": "Fica designada audiência inicial para 10/12", "sinal": ""}
        try:
            it = radar.item_de_lead(lead, {"valor_minimo": 0})
        except Exception as e:  # o formato do lead mudou: o teste precisa acompanhar
            self.fail(f"item_de_lead falhou com lead mínimo: {e!r}")
        self.assertEqual(it["sinal"], "audiência inicial")
        lead["sinal"] = "citação inicial"
        self.assertEqual(radar.item_de_lead(lead, {"valor_minimo": 0})["sinal"], "citação inicial")


class Tela0736A(unittest.TestCase):
    """Ressalvas (1), (3) a (6) da Operação, na tela."""

    def setUp(self):
        self.h = ler("radar_modelo.html")

    def test_quarto_estado_e_textos(self):
        self.assertIn('if (r.ocupado) return "ocupado";', self.h)
        self.assertIn('lic_ocupado: "Há uma leitura em andamento; ela confere a licença sozinha."', self.h)
        self.assertIn('lic_ocupado: "A reading is running; it checks the licence by itself."', self.h)

    def test_trocar_licenca_encadeado(self):
        self.assertIn("Promise.resolve(depois_).then(function () { return conferirConta(); })", self.h)

    def test_ler_o_diario_mostra_conferindo(self):
        self.assertIn('avisoRapidoApp(t("conferindo_lic"), "nota-g")', self.h)

    def test_avisos_nao_se_empilham(self):
        self.assertIn('if (v_.textContent === txt) v_.parentNode.removeChild(v_);', self.h)

    def test_menu_abrir_pasta_texto_proprio(self):
        self.assertIn('oque === "pasta" ? t("pasta_ainda_nao")', self.h)

    def test_conferir_agora_mostra_que_trabalha_e_ativa_em_verde(self):
        self.assertIn('b_.textContent = t("lic_conferindo_btn")', self.h)
        self.assertIn('el("b", "lic-ativa", t("lic_ativa"))', self.h)

    def test_novidades_sem_frase_de_efeito(self):
        self.assertIn('"Mensagem ao encerrar o programa."', self.h)
        self.assertNotIn("Mensagem clara quando", self.h)


class Configuracoes0736(unittest.TestCase):
    """Teste do dono (itens 2 a 6, 8 a 11 e 17) e Histórico fora das abas (4b)."""

    def setUp(self):
        self.h = ler("radar_modelo.html")

    def test_nomes_decididos(self):
        for k in ('c_s_lista: "Processos"', 'c_s_leitura: "Leitura do Diário"', 'rg_titulo: "Destaques e exclusões"', 'ag_titulo: "Rotina de leitura"',
                  'c_s_lista: "Cases"', 'rg_titulo: "Highlights and exclusions"', 'ag_titulo: "Reading routine"'):
            self.assertIn(k, self.h)
        self.assertNotIn('"Critérios da lista"', self.h)

    def test_ordem_das_secoes(self):
        ordem = ['id="c-s-lista"', 'id="c-regras-wrap"', 'id="c-filtros-wrap"', 'id="c-pasta-wrap"', 'id="c-s-leitura"', 'id="c-agendar-wrap"',
                 'id="c-arm-wrap"', 'id="c-s-tela"', 'id="c-s-licenca"', 'id="c-lic-wrap"', 'id="c-termos-wrap"', 'id="c-sobre-wrap"']
        pos = [self.h.index(x) for x in ordem]
        self.assertEqual(pos, sorted(pos))

    def test_licenca_sem_repetir(self):
        self.assertIn("function estadoLicConfig()", self.h)
        corpo = self.h[self.h.index("  function infoConfig() {"):][:900]
        self.assertNotIn('par(t("licenca")', corpo); self.assertNotIn('par(t("lic_validade")', corpo)
        self.assertIn('$("c-codigo-nota").hidden = true;', self.h)

    def test_termos_numa_linha_e_ultimo_envio(self):
        self.assertIn('termos_linha: "Versão {v}, aceitos por {n} em {d}."', self.h)
        self.assertIn('ret_quando: "Último envio ({q}): {n} linha(s)."', self.h)
        self.assertIn('t("c_chave_ajuda")', self.h)

    def test_cores_da_atualizacao_e_rodape(self):
        self.assertIn('el("span", "txt-verde", t("atu_nada"', self.h); self.assertIn('el("span", "txt-azul", t("atu_ok"', self.h)
        self.assertIn('c_dica: "Cada área do direito tem a sua planilha (exemplo:', self.h)
        self.assertNotIn("Trabalhista.xlsx agora", self.h)

    def test_historico_fora_das_abas(self):
        self.assertIn('if (v === "historico") { abrirHistorico(false); return; }', self.h)
        self.assertIn('b.hidden = v === "historico"', self.h)
        self.assertIn('[["painel", "v_painel"], ["lista", "v_lista"], ["arquivo", "v_arquivo"]].map(', self.h)
        self.assertIn('#config.ver-hist > :not(.conf-cab):not(#c-hist)', self.h)
        self.assertIn('id="c-historico"', self.h); self.assertIn('id="c-hist-voltar"', self.h)
        self.assertIn('"faixa-falha"', self.h)


class Pasta0736(unittest.TestCase):
    """Itens 18 a 22: conferência numa linha própria, recado de abrir que some, um botão por serviço, cartões claros."""

    def setUp(self):
        self.h = ler("radar_modelo.html")

    def test_conferencia_e_recado_separados(self):
        self.assertIn('id="c-abrir-msg"', self.h); self.assertIn('var tx_ = $("c-abrir-msg");', self.h)
        self.assertIn('class="pasta-conferida" id="c-teste-txt"', self.h)

    def test_um_botao_por_servico_sem_parenteses(self):
        self.assertIn('["gdrive", "onedrive"].forEach(function (tipo) {', self.h)
        self.assertNotIn('(nm_ ? " (" + nm_ + ")" : "")', self.h)
        self.assertIn('nuvem_de: "OneDrive de {o}"', self.h); self.assertIn('nuvem_pessoal: "OneDrive pessoal"', self.h)

    def test_escolher_primeiro_e_abrir_diferente(self):
        bloco = self.h[self.h.index('id="c-nuvens-wrap"'):][:400]
        self.assertLess(bloco.index('id="c-escolher"'), bloco.index('id="c-nuvens"'))
        self.assertIn('class="btn-txt abrir-pasta-link" id="c-abrir-pasta"', self.h)

    def test_cartoes_claros_sem_caminho_repetido(self):
        self.assertIn('c_nenhuma: "Pasta padrão (recomendada)"', self.h)
        self.assertIn('pasta_outra_x: "Rede, OneDrive ou Google Drive para computador. Só as planilhas vão para lá; o programa continua em {p}."', self.h)
        self.assertNotIn('var cam_ = outra_ ? ($("c-outra").value || "") : o.value;', self.h)
        self.assertIn('pasta_sub: "(o {c} cria a subpasta', self.h)


class Exclusoes0736(unittest.TestCase):
    """Itens 12 a 16: nome pelo CNPJ guardado junto do CNPJ, sem repetir; cópia para as áreas escolhidas, somando ou trocando."""

    def setUp(self):
        from lexsuite import preferencias
        self.p = preferencias; self.pasta = tempfile.mkdtemp()

    def test_nome_e_cnpj_juntos_sem_repetir(self):
        ex = self.p.exclusoes_validas([{"nome": "Empresa Exemplo Ltda", "cnpj": "11.222.333/0001-81", "motivo": "cliente"},
                                       {"nome": "11222333000181"}, {"nome": "Empresa Exemplo Ltda"}, {"nome": "Outra Exemplo SA"}])
        self.assertEqual([e["nome"] for e in ex], ["Empresa Exemplo Ltda", "Outra Exemplo SA"])
        self.assertEqual(ex[0]["cnpj"], "11222333000181")

    def test_exclusao_vale_pelo_nome_e_pelo_cnpj(self):
        prefs = {"exclusoes": self.p.exclusoes_validas([{"nome": "Empresa Exemplo Ltda", "cnpj": "11222333000181"}])}
        a = {"empresas": ["Outro Nome Qualquer"], "empresa": {"cnpj": "11.222.333/0001-81"}}
        b = {"empresas": ["EMPRESA EXEMPLO LTDA"], "empresa": {}}
        self.p.aplicar([a, b], prefs)
        self.assertTrue(a["excluida"]); self.assertTrue(b["excluida"])

    def test_copiar_acrescentando_sem_repetir(self):
        self.p.salvar_area(self.pasta, "trabalhista", {"valor_minimo": 5000}, [{"nome": "Empresa A Exemplo", "cnpj": "11222333000181"}])
        self.p.salvar_area(self.pasta, "tributario", {"valor_minimo": 9}, [{"nome": "11.222.333/0001-81"}, {"nome": "Empresa B Exemplo"}])
        self.p.copiar_area(self.pasta, "trabalhista", ["tributario"], modo="acrescentar", partes=["exclusoes"])
        v, ex = self.p.criterios_da_area(self.pasta, "tributario")
        self.assertEqual(len(ex), 2); self.assertEqual(v["valor_minimo"], 9)

    def test_copiar_substituindo_limites_e_empresas(self):
        self.p.salvar_area(self.pasta, "trabalhista", {"valor_minimo": 5000}, [{"nome": "Empresa A Exemplo"}])
        self.p.salvar_area(self.pasta, "civel", {"valor_minimo": 9}, [{"nome": "Empresa B Exemplo"}])
        self.p.copiar_area(self.pasta, "trabalhista", ["civel", "empresarial"], modo="substituir", partes=["valores", "exclusoes"])
        for a in ("civel", "empresarial"):
            v, ex = self.p.criterios_da_area(self.pasta, a)
            self.assertEqual(v["valor_minimo"], 5000); self.assertEqual([e["nome"] for e in ex], ["Empresa A Exemplo"])

    def test_tela(self):
        h = ler("radar_modelo.html")
        self.assertIn('busca.value = ""; desenharExc();', h)  # acrescentar limpa a busca
        self.assertIn('rg_busca_nada: "Nenhuma excluída com', h); self.assertIn('rg_exc_sem_doc: "Sem CNPJ: a exclusão vale só para esse nome, escrito igual."', h)
        self.assertIn('fetch("/cnpj?n=" + encodeURIComponent(n)', h)
        self.assertIn("if (emUso_.length > 1) box.appendChild(seg);", h); self.assertIn("if (emUso_.length > 1) { acoes.appendChild(bc);", h)
        self.assertIn('rg_copiado_para: "✓ Critérios copiados para {a}."', h)
        self.assertNotIn("rg_copiar_q", h)


class Graficos0736(unittest.TestCase):
    """LISTA 2 e itens 23 a 30: barras empilhadas com escolha, pizza que se refaz, dicas em blocos, retorno do Buscar estatísticas."""

    def setUp(self):
        self.h = ler("radar_modelo.html")

    def test_barras_empilhadas_com_escolha(self):
        self.assertIn('seletorSeparar("lexsuite:graf-separar", ["nada", "trib", "sit", "faixa", "setor"], dim)', self.h)
        self.assertIn('seletorSeparar("lexsuite:saz-separar", ["nada", "trib"], dimS)', self.h)
        self.assertIn('g_dica_pilha: "{r}: {n} — {p}"', self.h)
        self.assertNotIn('el("div", "col" + (m === pico ? " pico" : ""))', self.h)  # sem o dourado nas barras

    def test_pizza_se_refaz_e_tudo_clicavel(self):
        self.assertIn("var ligado = function (l) { return !desligadaNoGrafico(opc, l) && !ocultos[chaveF(l)]; };", self.h)
        self.assertIn("transition: stroke-dasharray .55s ease", self.h); self.assertIn("prefers-reduced-motion: reduce) { .anel circle { transition: none; } }", self.h)
        self.assertIn('item.title = t("g_some_so_aqui")', self.h)

    def test_dicas_em_blocos(self):
        self.assertIn("function emBlocos(txt)", self.h)
        self.assertIn('saz_ajuda: "**Para que serve**', self.h); self.assertIn('g_dia_ajuda: "**Para que serve**', self.h)
        self.assertIn('emBlocos(t("g_dia_ajuda"))', self.h)

    def test_buscar_estatisticas_responde_na_hora(self):
        self.assertIn('saz_em_dia: "✓ As estatísticas já estão em dia: {p}."', self.h)
        self.assertIn('el("span", "txt-azul", t("saz_em_dia", { p: perSaz_ }))', self.h)
        self.assertIn('var msgH = el("span", "nota-g saz-retorno")', self.h)

    def test_faixa_da_leitura_numa_linha_sem_caminho(self):
        self.assertIn(".estado .rodando-linha { display: flex; flex-wrap: nowrap;", self.h)
        self.assertNotIn("ações na lista. Página:", ler("lexsuite", "radar.py"))

    def test_nada_novo(self):
        self.assertIn('"Nada novo: os cadernos até', ler("lexsuite", "radar.py"))
        self.assertIn('"Nada novo" in texto', ler("lexsuite", "app.py"))


class SazonalPorTribunal(unittest.TestCase):
    def test_por_mes_traz_cada_tribunal(self):
        from lexsuite import historico
        class B:
            def estatisticas(self):
                return [{"data": "2026-10-01", "tribunal": "TRT2", "novas": 3}, {"data": "2026-10-02", "tribunal": "TRT15", "novas": 2},
                        {"data": "2026-11-01", "tribunal": "TRT2", "novas": 1}]
        m = historico.por_mes(B())
        self.assertEqual(m[0], {"mes": "2026-10", "novas": 5, "por_tribunal": {"TRT2": 3, "TRT15": 2}})


class UltimaTentativa(Servidor):
    def test_regras_dizem_as_areas_em_uso_e_copiam_para_as_escolhidas(self):
        c = http.client.HTTPConnection("127.0.0.1", self.srv.server_address[1], timeout=20)
        c.request("GET", "/regras?area=trabalhista", headers={"X-LexSuite": "1"}); d = json.loads(c.getresponse().read()); c.close()
        self.assertEqual(d["areas_em_uso"], ["trabalhista"])
        r = self.pedir("/regras", {"area": "trabalhista", "valores": d["valores"], "exclusoes": [{"nome": "Empresa A Exemplo"}],
                                   "destinos": ["civel"], "modo": "acrescentar", "partes": ["exclusoes"]})
        self.assertTrue(r["ok"])
        from lexsuite import preferencias
        self.assertEqual([e["nome"] for e in preferencias.criterios_da_area(self.pasta, "civel")[1]], ["Empresa A Exemplo"])
        self.assertEqual(preferencias.criterios_da_area(self.pasta, "tributario")[1], [])

    def test_dados_trazem_a_ultima_tentativa(self):
        c = http.client.HTTPConnection("127.0.0.1", self.srv.server_address[1], timeout=20)
        c.request("GET", "/dados", headers={"X-LexSuite": "1"}); d = json.loads(c.getresponse().read()); c.close()
        self.assertIn("ultima_tentativa", d)


if __name__ == "__main__":
    unittest.main()
