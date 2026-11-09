"""Frente de cada ação (trabalhista, tributário, cível, empresarial) por uma regra escrita, sem IA.

Desenho da Arquitetura (documentacao/DESENHO-ARQUIVO-ESTATISTICAS.md, seção 5), aprovado pelo dono em 09/Nov:
TRT e TST são trabalhistas; nos outros tribunais, pela classe e pelo assunto publicados no Diário. O que a regra não
reconhece fica "civel" com a marca "a conferir" (frente_a_conferir).
"""

from . import classificar as cl

FRENTES = ("trabalhista", "tributario", "civel", "empresarial")

# Palavras (sem acento, em maiúsculas) procuradas na classe e no assunto. A ordem importa: a primeira que bate vale.
PALAVRAS = (
    ("tributario", ("EXECUCAO FISCAL", "EMBARGOS A EXECUCAO FISCAL", "TRIBUT", "ICMS", "ISS ", "IPTU", "PIS", "COFINS",
                    "IMPOSTO", "CREDITO TRIBUTARIO", "DIVIDA ATIVA", "ANULATORIA DE DEBITO FISCAL")),
    ("empresarial", ("RECUPERACAO JUDICIAL", "RECUPERACAO EXTRAJUDICIAL", "FALENCIA", "DISSOLUCAO DE SOCIEDADE",
                     "DISSOLUCAO PARCIAL", "APURACAO DE HAVERES", "SOCIETAR", "RECUPERACAO DE EMPRESA")),
)


def _texto(lead):
    return " " + cl.sem_acento(" ".join(str(lead.get(k) or "") for k in ("classe", "assunto", "tipo"))).upper() + " "


def frente(lead):
    """'trabalhista', 'tributario', 'empresarial' ou 'civel'."""
    trib = str(lead.get("tribunal") or "").upper()
    if trib.startswith("TRT") or trib == "TST":
        return "trabalhista"
    texto = _texto(lead)
    for nome, palavras in PALAVRAS:
        if any(p in texto for p in palavras):
            return nome
    return "civel"


def a_conferir(lead):
    """True quando a frente saiu do padrão (nenhuma palavra reconhecida fora da Justiça do Trabalho)."""
    trib = str(lead.get("tribunal") or "").upper()
    if trib.startswith("TRT") or trib == "TST":
        return False
    texto = _texto(lead)
    return not any(p in texto for _, ps in PALAVRAS for p in ps)
