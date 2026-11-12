"""CNPJ (numérico e alfanumérico) e CPF: limpar, validar, formatar e achar num texto (0.7.33).

CNPJ alfanumérico (IN RFB 2.229/2024, emitido desde 31/Jul/2026): 14 posições, as 12 primeiras com números ou letras
maiúsculas (A-Z), as 2 últimas (dígitos verificadores) sempre números. O cálculo é o mesmo módulo 11 de sempre, com o valor
de cada caractere = código ASCII - 48 (0-9 valem 0-9; A vale 17 ... Z vale 42); para o CNPJ só numérico o resultado é o de
sempre. Desenho: documentacao/DESENHO-CRITERIOS-CHAMADOS-CNPJ-2026-11-12.md, seção 3. Só biblioteca padrão; não importa
nada do programa.
"""

import re

_CANDIDATO = re.compile(r"(?<![0-9A-Z])([0-9A-Z]{2})(\.?)([0-9A-Z]{3})(\.?)([0-9A-Z]{3})(/?)([0-9A-Z]{4})(-?)([0-9]{2})(?![0-9A-Z])")
_CONTEXTO = re.compile(r"CNPJ.{0,12}$", re.S)


def limpar(texto):
    """Maiúsculas e só [0-9A-Z]."""
    return re.sub(r"[^0-9A-Z]", "", str(texto or "").upper())


def _dv(base):
    pesos = list(range(len(base) - 7, 1, -1)) + list(range(9, 1, -1))
    resto = sum((ord(c) - 48) * p for c, p in zip(base, pesos)) % 11
    return "0" if resto < 2 else str(11 - resto)


def valido(cnpj):
    """CNPJ com 14 posições, numérico ou alfanumérico, com os dígitos verificadores certos."""
    d = limpar(cnpj)
    if not re.fullmatch(r"[0-9A-Z]{12}[0-9]{2}", d) or d == d[0] * 14:
        return False
    return d[12] == _dv(d[:12]) and d[13] == _dv(d[:13])


def eh_alfanumerico(cnpj):
    """Tem letra nas 12 primeiras posições (CNPJ do formato novo)."""
    return bool(re.search(r"[A-Z]", limpar(cnpj)[:12]))


def formatar(cnpj):
    """XX.XXX.XXX/XXXX-XX (com letras, se houver); devolve o texto como veio se não tiver 14 posições."""
    d = limpar(cnpj)
    if len(d) != 14:
        return str(cnpj or "")
    return f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}"


def cpf_valido(cpf):
    d = re.sub(r"\D", "", str(cpf or ""))
    if len(d) != 11 or d == d[0] * 11:
        return False
    for n in (9, 10):
        resto = sum(int(d[i]) * (n + 1 - i) for i in range(n)) * 10 % 11
        if str(resto % 10) != d[n]:
            return False
    return True


def formatar_cpf(cpf):
    d = re.sub(r"\D", "", str(cpf or ""))
    return f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}" if len(d) == 11 else str(cpf or "")


def extrair(texto):
    """CNPJs válidos de um texto, limpos (14 posições, maiúsculas), sem repetir, na ordem em que aparecem.

    Um candidato só vale com o dígito verificador certo e: só números (regra de sempre), ou com a máscara (pontos e barra),
    ou com a palavra CNPJ até 12 caracteres antes. Assim 14 letras e números colados num texto jurídico não viram CNPJ."""
    t = str(texto or "").upper()
    achados = []
    for m in _CANDIDATO.finditer(t):
        g = m.groups()
        d = g[0] + g[2] + g[4] + g[6] + g[8]
        if not valido(d) or d in achados:
            continue
        mascara = g[1] == "." and g[3] == "." and g[5] == "/"
        if d.isdigit() or mascara or _CONTEXTO.search(t[max(0, m.start() - 20):m.start()]):
            achados.append(d)
    return achados


def parece_cnpj(texto):
    """Há um CNPJ válido no texto (para reconhecer empresa pelo nome com CNPJ)."""
    return bool(extrair(texto))
