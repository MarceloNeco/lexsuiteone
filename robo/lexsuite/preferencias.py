"""Preferências e controle do escritório: as abas Preferências, Exclusões e Controle (oculta) da planilha única
<pasta compartilhada>/LexSuiteONE/LexSuiteONE.xlsx. O escritório edita essas abas; o robô lê antes de cada rodada
e as preserva quando regrava a planilha (ver compartilhar.gravar_radar).
"""

import datetime as dt
import os
import re

from . import classificar as cl
from . import planilha

NOME_ARQUIVO = "LexSuiteONE.xlsx"

PADRAO = {"valor_minimo": 100000, "minimo_acoes": 1, "janela_dias": 30, "teto_capital_gigante": 50000000,
          "esconder_gigantes": False, "esconder_excluidas": True, "mostrar_socios": True}
CHAVES = {
    "Valor mínimo da causa (R$)": "valor_minimo",
    "Mínimo de ações da mesma empresa": "minimo_acoes",
    "Janela do mínimo de ações (dias)": "janela_dias",
    "Capital social que indica jurídico próprio (R$)": "teto_capital_gigante",
    "Esconder jurídico próprio provável": "esconder_gigantes",
    "Esconder clientes e exclusões": "esconder_excluidas",
    "Mostrar sócios e administradores": "mostrar_socios",
}
LINHAS_PREFERENCIAS = [
    ["Ajuste", "Valor", "Como usar"],
    ["Valor mínimo da causa (R$)", 100000, "Filtro \"Acima de\" na tela e na planilha. Ações abaixo continuam na lista."],
    ["Mínimo de ações da mesma empresa", 1, "Ex.: 3 = só destacar empresa com 3 ou mais ações novas na janela de dias. 1 = todas."],
    ["Janela do mínimo de ações (dias)", 30, "Quantos dias para trás contar as ações da mesma empresa."],
    ["Capital social que indica jurídico próprio (R$)", 50000000, "Acima disso a empresa é marcada \"jurídico próprio provável\" e vai para o fim da lista."],
    ["Esconder jurídico próprio provável", "não", "sim ou não."],
    ["Esconder clientes e exclusões", "sim", "sim ou não. A aba Exclusões lista quem não deve aparecer."],
    ["Mostrar sócios e administradores", "sim", "sim ou não. São nomes de pessoas do cadastro público da Receita; se o escritório não precisa, desligue."],
]
LINHAS_EXCLUSOES = [
    ["Nome ou CNPJ", "Motivo"],
    ["(exemplo, pode apagar) Empresa Exemplo Ltda", "cliente atual"],
]
# Contato de atendimento do JUDICIAL. integracao@ é só para sistemas (compartilhamento do Drive), nunca para pessoas.
SUPORTE = "judicial@solverone.com.br"
SISTEMAS = "integracao@solverone.com.br"

LINHAS_CONTROLE = [
    ["Chave", "Valor", "O que faz"],
    ["ativo", "sim", "não = o robô não roda e mostra a mensagem abaixo."],
    ["validade", "", "aaaa-mm-dd. Depois dessa data o robô para e avisa."],
    ["versao_minima", "", "Se a versão instalada for menor, o robô pede atualização antes de rodar."],
    ["mensagem", "", "Texto mostrado na tela do escritório (avisos do suporte)."],
    ["suporte", SUPORTE, "Contato do suporte (atendimento a pessoas)."],
]


def caminho(pasta_base):
    return os.path.join(pasta_base, NOME_ARQUIVO) if pasta_base else ""


ABAS_EDITAVEIS = ("Preferências", "Exclusões", "Controle")


def abas_padrao():
    """As três abas como nascem na primeira vez (o escritório edita depois)."""
    return [
        {"nome": "Preferências", "linhas": [list(l) for l in LINHAS_PREFERENCIAS], "larguras": [46, 16, 80]},
        {"nome": "Exclusões", "linhas": [list(l) for l in LINHAS_EXCLUSOES], "larguras": [48, 50]},
        {"nome": "Controle", "linhas": [list(l) for l in LINHAS_CONTROLE], "oculta": True, "larguras": [18, 36, 70]},
    ]


def _sim(v):
    return cl.sem_acento(str(v if v is not None else "")).strip().lower() in ("sim", "s", "yes", "true", "1", "x", "verdadeiro")


def _numero(v, padrao):
    if isinstance(v, bool):
        return padrao
    if isinstance(v, (int, float)):
        return v
    t = str(v or "").strip().replace("R$", "").replace(" ", "")
    if not t:
        return padrao
    if "," in t:  # formato brasileiro: 1.234,56
        t = t.replace(".", "").replace(",", ".")
    elif t.count(".") > 1:  # 1.234.567 sem centavos
        t = t.replace(".", "")
    try:
        n = float(t)
        return int(n) if n == int(n) else n
    except ValueError:
        return padrao


def versao_tupla(v):
    return tuple(int(x) for x in re.findall(r"\d+", str(v or ""))[:3]) or (0,)


def padrao():
    p = dict(PADRAO)
    p.update({"exclusoes": [], "controle": {"ativo": True, "validade": "", "versao_minima": "", "mensagem": "",
                                            "suporte": SUPORTE}, "origem": "padrão", "erro": ""})
    return p


def carregar(pasta_base, doc=None):
    """Lê as abas editáveis da planilha. Sem pasta ou sem arquivo, devolve o padrão; se não conseguir ler, diz o erro.
    `doc` pode ser a planilha já lida (evita ler duas vezes)."""
    prefs = padrao()
    c = caminho(pasta_base)
    if doc is None:
        if not c or not os.path.exists(c):
            return prefs
        try:
            doc = planilha.ler_xlsx(c, so_abas=ABAS_EDITAVEIS)
        except Exception as e:  # planilha corrompida ou em uso: o robô segue com o padrão e avisa
            prefs["erro"] = (f"Não consegui ler as abas Preferências e Exclusões de {NOME_ARQUIVO} (arquivo corrompido ou bloqueado). "
                             "Nesta leitura valem as preferências padrão. / Could not read the Preferences and Exclusions tabs; "
                             f"default preferences apply this time. ({e.__class__.__name__})")
            return prefs
    abas = {cl.sem_acento(a["nome"]).strip().lower(): a["linhas"] for a in doc["abas"]}
    for linha in abas.get("preferencias", [])[1:]:
        if len(linha) >= 2 and str(linha[0]).strip() in CHAVES:
            chave = CHAVES[str(linha[0]).strip()]
            prefs[chave] = _sim(linha[1]) if chave.startswith(("esconder", "mostrar")) else _numero(linha[1], PADRAO[chave])
    for linha in abas.get("exclusoes", [])[1:]:
        nome = str(linha[0] if linha else "").strip()
        if nome and not nome.lower().startswith("(exemplo"):
            prefs["exclusoes"].append({"nome": nome, "motivo": str(linha[1]).strip() if len(linha) > 1 else ""})
    for linha in abas.get("controle", [])[1:]:
        chave = cl.sem_acento(str(linha[0] if linha else "")).strip().lower()
        valor = linha[1] if len(linha) > 1 else ""
        if chave == "ativo":
            prefs["controle"]["ativo"] = _sim(valor) if str(valor).strip() else True
        elif chave in ("validade", "versao_minima", "mensagem", "suporte"):
            prefs["controle"][chave] = str(valor if valor is not None else "").strip()
    # integracao@ é só para sistemas (não é lido por pessoas); planilhas antigas que o trazem como suporte passam a judicial@.
    if prefs["controle"].get("suporte", "").strip().lower() in ("", SISTEMAS):
        prefs["controle"]["suporte"] = SUPORTE
    prefs["origem"] = c
    return prefs


def bloqueio(prefs, versao_atual, hoje=None):
    """Motivo para o robô não rodar, ou '' quando pode."""
    c = prefs.get("controle") or {}
    msg = (" " + c["mensagem"]) if c.get("mensagem") else ""
    if not c.get("ativo", True):
        return ("O programa está pausado pela SolverONE (aba Controle)." + msg).strip()
    if c.get("validade"):
        try:
            if (hoje or dt.date.today()) > dt.date.fromisoformat(c["validade"][:10]):
                return (f"A validade terminou em {c['validade'][:10]}." + msg).strip()
        except ValueError:
            pass
    if c.get("versao_minima") and versao_tupla(c["versao_minima"]) > versao_tupla(versao_atual):
        return (f"Precisa atualizar para a versão {c['versao_minima']} ou mais nova (instalada: {versao_atual})." + msg).strip()
    return ""


def aplicar(itens, prefs, acoes_por_empresa=None):
    """Marca item['excluida'] com o motivo (exclusão da planilha ou mínimo de ações). Não remove nada da lista."""
    por_nome = {cl.chave_nome(e["nome"]): e for e in prefs.get("exclusoes") or [] if cl.chave_nome(e["nome"])}
    cnpjs = {re.sub(r"\D", "", e["nome"]) for e in prefs.get("exclusoes") or [] if len(re.sub(r"\D", "", e["nome"])) == 14}
    minimo = int(prefs.get("minimo_acoes") or 1)
    for it in itens:
        motivo = ""
        nomes = it.get("empresas") or []
        cnpj = re.sub(r"\D", "", str((it.get("empresa") or {}).get("cnpj") or ""))
        for n in nomes:
            e = por_nome.get(cl.chave_nome(n))
            if e:
                motivo = "Exclusão: " + (e["motivo"] or e["nome"])
                break
        if not motivo and cnpj and cnpj in cnpjs:
            motivo = "Exclusão: CNPJ na lista"
        if not motivo and minimo > 1 and acoes_por_empresa is not None:
            qtd = max((acoes_por_empresa.get(cl.chave_nome(n), 0) for n in nomes), default=0)
            it["acoes_na_janela"] = qtd
            if qtd < minimo:
                motivo = f"Menos de {minimo} ações em {int(prefs.get('janela_dias') or 30)} dias"
        it["excluida"] = motivo
    return itens
