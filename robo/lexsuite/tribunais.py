"""Os tribunais que publicam no DJEN e que o robô sabe ler: sigla do DJEN, nome, estados, região e ramo.

Ramos: Trabalhista (24 TRTs), Estadual (27 TJs), Federal (6 TRFs) e Superior (STJ, TST). A leitura do Diário
é a mesma para todos (o DJEN é nacional); a regra de "ação nova" foi calibrada no trabalhista e fica marcada
como "a calibrar" nos demais.
"""

REGIOES = ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte", "Nacional"]
RAMOS = ["Trabalhista", "Estadual", "Federal", "Superior"]

UFS = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal",
    "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul",
    "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná", "PE": "Pernambuco", "PI": "Piauí",
    "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte", "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima",
    "SC": "Santa Catarina", "SP": "São Paulo", "SE": "Sergipe", "TO": "Tocantins",
}

_REGIAO_UF = {
    "Sudeste": ["SP", "RJ", "MG", "ES"], "Sul": ["RS", "PR", "SC"],
    "Nordeste": ["BA", "PE", "CE", "PB", "MA", "AL", "SE", "RN", "PI"],
    "Centro-Oeste": ["DF", "GO", "MT", "MS"], "Norte": ["PA", "AP", "AM", "RR", "RO", "AC", "TO"],
}


def _regiao(uf):
    return next(r for r, ufs in _REGIAO_UF.items() if uf in ufs)


TRTS = [
    {"sigla": "TRT1", "nome": "Rio de Janeiro", "ufs": ["RJ"], "regiao": "Sudeste"},
    {"sigla": "TRT2", "nome": "São Paulo: capital, Grande SP e Baixada", "ufs": ["SP"], "regiao": "Sudeste"},
    {"sigla": "TRT3", "nome": "Minas Gerais", "ufs": ["MG"], "regiao": "Sudeste"},
    {"sigla": "TRT4", "nome": "Rio Grande do Sul", "ufs": ["RS"], "regiao": "Sul"},
    {"sigla": "TRT5", "nome": "Bahia", "ufs": ["BA"], "regiao": "Nordeste"},
    {"sigla": "TRT6", "nome": "Pernambuco", "ufs": ["PE"], "regiao": "Nordeste"},
    {"sigla": "TRT7", "nome": "Ceará", "ufs": ["CE"], "regiao": "Nordeste"},
    {"sigla": "TRT8", "nome": "Pará e Amapá", "ufs": ["PA", "AP"], "regiao": "Norte"},
    {"sigla": "TRT9", "nome": "Paraná", "ufs": ["PR"], "regiao": "Sul"},
    {"sigla": "TRT10", "nome": "Distrito Federal e Tocantins", "ufs": ["DF", "TO"], "regiao": "Centro-Oeste"},
    {"sigla": "TRT11", "nome": "Amazonas e Roraima", "ufs": ["AM", "RR"], "regiao": "Norte"},
    {"sigla": "TRT12", "nome": "Santa Catarina", "ufs": ["SC"], "regiao": "Sul"},
    {"sigla": "TRT13", "nome": "Paraíba", "ufs": ["PB"], "regiao": "Nordeste"},
    {"sigla": "TRT14", "nome": "Rondônia e Acre", "ufs": ["RO", "AC"], "regiao": "Norte"},
    {"sigla": "TRT15", "nome": "São Paulo: interior (sede em Campinas)", "ufs": ["SP"], "regiao": "Sudeste"},
    {"sigla": "TRT16", "nome": "Maranhão", "ufs": ["MA"], "regiao": "Nordeste"},
    {"sigla": "TRT17", "nome": "Espírito Santo", "ufs": ["ES"], "regiao": "Sudeste"},
    {"sigla": "TRT18", "nome": "Goiás", "ufs": ["GO"], "regiao": "Centro-Oeste"},
    {"sigla": "TRT19", "nome": "Alagoas", "ufs": ["AL"], "regiao": "Nordeste"},
    {"sigla": "TRT20", "nome": "Sergipe", "ufs": ["SE"], "regiao": "Nordeste"},
    {"sigla": "TRT21", "nome": "Rio Grande do Norte", "ufs": ["RN"], "regiao": "Nordeste"},
    {"sigla": "TRT22", "nome": "Piauí", "ufs": ["PI"], "regiao": "Nordeste"},
    {"sigla": "TRT23", "nome": "Mato Grosso", "ufs": ["MT"], "regiao": "Centro-Oeste"},
    {"sigla": "TRT24", "nome": "Mato Grosso do Sul", "ufs": ["MS"], "regiao": "Centro-Oeste"},
]
for _t in TRTS:
    _t["ramo"] = "Trabalhista"

# Justiça estadual: um TJ por estado; o do Distrito Federal e Territórios é TJDFT.
TJS = [{"sigla": "TJDFT" if uf == "DF" else "TJ" + uf, "nome": nome, "ufs": [uf], "regiao": _regiao(uf), "ramo": "Estadual"}
       for uf, nome in sorted(UFS.items(), key=lambda kv: kv[1])]

TRFS = [
    {"sigla": "TRF1", "nome": "1ª Região (Brasília): Norte, parte do Nordeste e do Centro-Oeste", "ufs": ["DF", "AC", "AM", "AP", "BA", "GO", "MA", "MT", "PA", "PI", "RO", "RR", "TO"], "regiao": "Centro-Oeste", "ramo": "Federal"},
    {"sigla": "TRF2", "nome": "2ª Região (Rio de Janeiro): RJ e ES", "ufs": ["RJ", "ES"], "regiao": "Sudeste", "ramo": "Federal"},
    {"sigla": "TRF3", "nome": "3ª Região (São Paulo): SP e MS", "ufs": ["SP", "MS"], "regiao": "Sudeste", "ramo": "Federal"},
    {"sigla": "TRF4", "nome": "4ª Região (Porto Alegre): RS, SC e PR", "ufs": ["RS", "SC", "PR"], "regiao": "Sul", "ramo": "Federal"},
    {"sigla": "TRF5", "nome": "5ª Região (Recife): PE, AL, CE, PB, RN e SE", "ufs": ["PE", "AL", "CE", "PB", "RN", "SE"], "regiao": "Nordeste", "ramo": "Federal"},
    {"sigla": "TRF6", "nome": "6ª Região (Belo Horizonte): MG", "ufs": ["MG"], "regiao": "Sudeste", "ramo": "Federal"},
]

SUPERIORES = [
    {"sigla": "STJ", "nome": "Superior Tribunal de Justiça", "ufs": [], "regiao": "Nacional", "ramo": "Superior"},
    {"sigla": "TST", "nome": "Tribunal Superior do Trabalho", "ufs": [], "regiao": "Nacional", "ramo": "Superior"},
]

TRIBUNAIS = TRTS + TJS + TRFS + SUPERIORES
SIGLAS = [t["sigla"] for t in TRIBUNAIS]
_POR_SIGLA = {t["sigla"]: t for t in TRIBUNAIS}


def info(sigla):
    return _POR_SIGLA.get(str(sigla or "").upper().replace(" ", ""))


def validar(siglas):
    """Só siglas que existem, em maiúsculas, sem repetir e na ordem da tabela (TRTs, TJs, TRFs, superiores)."""
    pedidas = {str(s).upper().replace(" ", "") for s in (siglas or [])}
    return [s for s in SIGLAS if s in pedidas]


def por_uf(uf):
    uf = str(uf or "").upper()
    return [t["sigla"] for t in TRIBUNAIS if uf in t["ufs"]]


def por_regiao(regiao, ramo=None):
    return [t["sigla"] for t in TRIBUNAIS if t["regiao"] == regiao and (ramo is None or t["ramo"] == ramo)]


def por_ramo(ramo):
    return [t["sigla"] for t in TRIBUNAIS if t["ramo"] == ramo]


def link_pje(sigla):
    """Consulta pública conhecida: PJe dos TRTs. Nos demais tribunais a página usa o link do Diário."""
    t = info(sigla)
    if t and t["ramo"] == "Trabalhista":
        return f"https://pje.{t['sigla'].lower()}.jus.br/consultaprocessual/"
    return ""
