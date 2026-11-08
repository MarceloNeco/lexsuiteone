"""Regras (sem IA) que transformam publicações em leads.

Tudo aqui é regra escrita, explicável e barata:
  - quem é empresa (pessoa jurídica) e quem é pessoa física;
  - pessoa física NUNCA aparece no resultado (LGPD e Res. CNJ 121/2010: na
    Justiça do Trabalho não se monta lista de quem processou o patrão);
  - CNPJ e valor da causa, quando o próprio texto da publicação trouxer;
  - nota de prioridade de 0 a 100, sempre com os motivos escritos.
"""

import re
import unicodedata

# Palavras que indicam empresa/entidade no nome da parte.
_PJ = re.compile(
    r"\b(LTDA|S\.?\s?/?A\.?|EIRELI|EPP|ME|MEI|CIA|COMPANHIA|SOCIEDADE|COOPERATIVA|ASSOCIA[CÇ][AÃ]O|"
    r"FUNDA[CÇ][AÃ]O|INSTITUTO|CONDOM[IÍ]NIO|BANCO|HOSPITAL|CL[IÍ]NICA|ESCOLA|COL[EÉ]GIO|"
    r"IND[UÚ]STRIA|COM[EÉ]RCIO|SERVI[CÇ]OS|LOG[IÍ]STICA|TRANSPORTES?|DISTRIBUIDORA|ATACAD|"
    r"SUPERMERCADO|CONSTRUTORA|ENGENHARIA|EMPREENDIMENTOS|PARTICIPA[CÇ][OÕ]ES|HOLDING|GRUPO|"
    r"TECNOLOGIA|SOLU[CÇ][OÕ]ES|ALIMENTOS|FARM[AÁ]CIA|DROGARIA|MUNIC[IÍ]PIO|PREFEITURA|ESTADO DE|"
    r"UNI[AÃ]O FEDERAL|AUTARQUIA|EMPRESA|COMERCIAL|INDUSTRIAL|TERCEIRIZA|SEGURAN[CÇ]A|VIGIL[AÂ]NCIA|"
    r"LIMPEZA|FACILITIES|ADMINISTRADORA|INCORPORADORA|MINERA[CÇ][AÃ]O|AGROPECU[AÁ]RIA|RESTAURANTE|"
    r"HOTEL|EDUCACIONAL|SA)\b", re.I)

_CNPJ = re.compile(r"\b(\d{2})\.?(\d{3})\.?(\d{3})/?(\d{4})-?(\d{2})\b")
_VALOR = re.compile(r"valor\s+da\s+causa[^\dR]{0,40}R?\$?\s*([\d\.]{1,15},\d{2})", re.I)
_CNJ = re.compile(r"\b(\d{7})-?(\d{2})\.?(\d{4})\.?(\d)\.?(\d{2})\.?(\d{4})\b")

# Rótulos que, no cabeçalho das publicações da Justiça do Trabalho, vêm antes do nome das partes.
_ROT_PASSIVO = r"(?:RECLAMAD[OA]S?|R[EÉ]US?|R[EÉ]|REQUERID[OA]S?|EXECUTAD[OA]S?|IMPETRAD[OA]|RECORRID[OA]S?)"
_ROT_ATIVO = r"(?:RECLAMANTES?|AUTOR(?:A|ES|AS)?|REQUERENTES?|EXEQUENTES?|IMPETRANTES?|RECORRENTES?)"
_FIM_NOME = (r"(?=\s+(?:" + _ROT_PASSIVO + r"|" + _ROT_ATIVO + r"|ADVOGAD|PERIT|TERCEIR|CUSTOS|"
             r"INTIMA|NOTIFICA|CITA|Intima[cç][aã]o|Notifica[cç][aã]o|Cita[cç][aã]o|Edital|DESTINAT|PODER JUDICI|PROCESSO|FICA|FICAM|Fica|Ficam|DESPACHO|"
             r"DECIS|SENTEN|EDITAL|AUDI[EÊ]NCIA|ATOrd|ATSum)\b|\s*[\n;]|$)")
_PASSIVO = re.compile(_ROT_PASSIVO + r"\s*:\s*(.{3,160}?)" + _FIM_NOME)

# Pistas de que a publicação é do começo do processo (ação recém-distribuída).
_INICIO = re.compile(
    r"audi[eê]ncia\s+(inicial|una|de\s+concilia)|notifica[cç][aã]o\s+inicial|"
    r"designad[ao]\s+audi[eê]ncia|fica\s+.{0,40}notificad|distribu[ií]d[ao]|cita[cç][aã]o", re.I)

# Assuntos que costumam pesar no valor da condenação (pista, não regra jurídica).
ASSUNTOS_PESO = {
    "doença ocupacional": 8, "acidente de trabalho": 8, "assédio moral": 6, "dano moral": 5,
    "rescisão indireta": 5, "insalubridade": 4, "periculosidade": 4, "horas extras": 3,
    "equiparação salarial": 4, "vínculo": 4, "responsabilidade solidária": 6, "subsidiária": 6,
    "estabilidade": 5, "reintegração": 5,
}


def sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s or "") if unicodedata.category(c) != "Mn")


def limpar_texto(html):
    t = re.sub(r"<br\s*/?>|</p>|</div>|</tr>", "\n", html or "", flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = t.replace("&nbsp;", " ").replace("&amp;", "&").replace("&quot;", '"')
    return re.sub(r"[ \t\r\f\v]+", " ", t).strip()


def eh_empresa(nome):
    return bool(nome) and (bool(_PJ.search(sem_acento(nome))) or bool(_CNPJ.search(nome)))


def cnpj_valido(digitos):
    d = re.sub(r"\D", "", digitos)
    if len(d) != 14 or d == d[0] * 14:
        return False
    def dv(base, pesos):
        s = sum(int(a) * b for a, b in zip(base, pesos)) % 11
        return "0" if s < 2 else str(11 - s)
    p1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    p2 = [6] + p1
    return d[12] == dv(d[:12], p1) and d[13] == dv(d[:13], p2)


def extrair_cnpjs(texto):
    achados = []
    for m in _CNPJ.finditer(texto or ""):
        d = "".join(m.groups())
        if cnpj_valido(d) and d not in achados:
            achados.append(d)
    return achados


def extrair_valor_causa(texto):
    m = _VALOR.search(texto or "")
    if not m:
        return None
    try:
        return float(m.group(1).replace(".", "").replace(",", "."))
    except ValueError:
        return None


def ano_do_processo(numero):
    m = _CNJ.search(numero or "")
    return int(m.group(3)) if m else None


def reclamadas_no_texto(texto):
    nomes = []
    for m in _PASSIVO.finditer(texto or ""):
        nome = re.sub(r"\s+", " ", m.group(1)).strip(" -–,:;")
        if nome.endswith(".") and not re.search(r"\b[A-Za-z]\.[A-Za-z]\.$", nome):
            nome = nome[:-1]  # ponto final da frase sai; o de "S.A." fica
        if nome and nome.upper() not in (n.upper() for n in nomes):
            nomes.append(nome)
    return nomes


def parece_inicio(texto):
    return bool(_INICIO.search(texto or ""))


def nota(lead, rito_ordinario_desde=40):
    """Nota de 0 a 100 com os motivos. Pesos são ponto de partida: o escritório ajusta."""
    pontos, motivos = 0, []
    if lead.get("cliente"):
        # Cliente atual processado: é o alerta mais importante e o uso que a OAB não questiona.
        return 100, ["cliente atual da carteira"]
    if lead.get("empresas"):
        pontos += 30
        motivos.append("ré é empresa")
    if len(lead.get("empresas") or []) > 1:
        pontos += 10
        motivos.append(f"{len(lead['empresas'])} empresas no polo passivo (possível terceirização)")
    if lead.get("rito") == "Ordinário":
        pontos += 15
        motivos.append(f"rito ordinário (causa acima de {rito_ordinario_desde} salários mínimos)")
    if lead.get("valor_causa"):
        v = lead["valor_causa"]
        extra = 15 if v >= 200000 else 10 if v >= 80000 else 5
        pontos += extra
        motivos.append(f"valor da causa R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    peso = 0
    texto_assuntos = " ".join(lead.get("assuntos") or []).lower() + " " + (lead.get("texto_curto") or "").lower()
    for chave, p in ASSUNTOS_PESO.items():
        if chave in texto_assuntos:
            peso += p
    if peso:
        pontos += min(peso, 20)
        motivos.append("assuntos de maior impacto")
    porte = (lead.get("porte") or "").upper()
    if "DEMAIS" in porte or "GRANDE" in porte:
        pontos += 10
        motivos.append("empresa de médio/grande porte")
    elif "PEQUENO" in porte or "EPP" in porte:
        pontos += 5
        motivos.append("empresa de pequeno porte")
    if lead.get("acoes_no_periodo", 1) >= 2:
        pontos += 10
        motivos.append(f"{lead['acoes_no_periodo']} ações contra a mesma empresa em 30 dias")
    return min(pontos, 100), motivos


_SUFIXOS = re.compile(r"\b(LTDA|S\.?/?A\.?|EIRELI|EPP|ME|CIA|COMPANHIA|SOCIEDADE ANONIMA)\b\.?", re.I)


# Palavras de cabeçalho do Diário que às vezes grudam no fim do nome da parte (0.7.11).
_RABO = re.compile(r"(?:\s+(?:intima[cç][aã]o|notifica[cç][aã]o|cita[cç][aã]o|edital|despacho|senten[cç]a|decis[aã]o|"
                   r"ac[oó]rd[aã]o|ata de audi[eê]ncia|pauta))+\s*$", re.I)


def limpar_nome(nome):
    """Tira do fim do nome as palavras de cabeçalho do Diário ("... Ltda Intimação" vira "... Ltda")."""
    return _RABO.sub("", re.sub(r"\s+", " ", nome or "").strip()).strip(" -–,:;")


_LIGACOES = {"DE", "DA", "DO", "DAS", "DOS", "E", "EM", "A", "O", "S"}


def nomes_batem(a, b):
    """True se dois nomes de empresa parecem a mesma (0.7.11): um está contido no outro palavra por palavra, ou os dois
    começam pela mesma palavra e dividem a maior parte das palavras. Liga o CNPJ achado no Diário à empresa processada;
    na dúvida, não liga (a ficha fica "CNPJ a conferir")."""
    ta = [x for x in chave_nome(a).split() if x not in _LIGACOES]
    tb = [x for x in chave_nome(b).split() if x not in _LIGACOES]
    if not ta or not tb:
        return False
    sa, sb = set(ta), set(tb)
    if sa <= sb or sb <= sa:
        return True
    return ta[0] == tb[0] and len(sa & sb) / max(len(sa), len(sb)) >= 0.6


def chave_nome(nome):
    """Nome comparável: sem acento, sem pontuação e sem LTDA/S.A., para achar o cliente da carteira."""
    n = _SUFIXOS.sub(" ", sem_acento(nome or "").upper())
    return re.sub(r"[^A-Z0-9]+", " ", n).strip()


def ler_carteira(caminho):
    """carteira.csv (separado por ;) com as colunas cnpj;nome — os clientes atuais do escritório."""
    import csv
    import os
    if not caminho or not os.path.exists(caminho):
        return {}, {}
    por_cnpj, por_nome = {}, {}
    with open(caminho, encoding="utf-8-sig") as f:
        for linha in csv.DictReader(f, delimiter=";"):
            nome = (linha.get("nome") or "").strip()
            cnpj = re.sub(r"\D", "", linha.get("cnpj") or "")
            if cnpj:
                por_cnpj[cnpj] = nome or cnpj
            if nome:
                por_nome[chave_nome(nome)] = nome
    return por_cnpj, por_nome


def cliente_da_carteira(lead, carteira):
    por_cnpj, por_nome = carteira
    for c in lead.get("cnpjs") or []:
        if c in por_cnpj:
            return por_cnpj[c]
    for e in lead.get("empresas") or []:
        if chave_nome(e) in por_nome:
            return por_nome[chave_nome(e)]
    return ""


# Setor da empresa pelo nome (mesmas palavras-chave do painel). Pista, não cadastro.
SETORES = [
    ("RH e terceirização", r"RH\b|RECURSOS HUMANOS|TERCEIRIZA|MAO DE OBRA|SERVICOS TEMPOR|COOPERATIVA DE TRABALHO|GESTAO DE PESSOAS|OUTSOURCING"),
    ("Logística e transporte", r"LOGISTIC|TRANSPORT|ENTREGA|CARGAS?\b|ARMAZEN|DISTRIBUI|FRETE|CORREIO|MOTORISTA|ENCOMENDA"),
    ("Varejo e e-commerce", r"MERCADO LIVRE|MAGAZINE|LOJAS?\b|VAREJO|SUPERMERCAD|ATACAD|COMERCIO|COMERCIAL\b|E-?COMMERCE|AMAZON|SHOPEE"),
    ("Saúde e farmácia", r"HOSPITAL|CLINIC|SAUDE|FARMAC|DROGARIA|LABORATORIO|MEDIC"),
    ("Segurança, limpeza e facilities", r"SEGURANCA|VIGILANCIA|LIMPEZA|CONSERVACAO|FACILITIES|PORTARIA|ZELADORIA"),
    ("Construção e imóveis", r"CONSTRU|ENGENHARIA|INCORPORA|IMOBILIAR|EMPREENDIMENTO|OBRAS"),
    ("Indústria", r"INDUSTRI|FABRICA|METALURG|QUIMIC|ALIMENTOS|PLASTIC|TEXTIL|AUTOMOTIV|EMBALAGE|PAPEL"),
]


def setor(nomes):
    """Primeiro setor cujo padrão aparece no nome de alguma das empresas."""
    texto = sem_acento(" ".join(nomes if isinstance(nomes, (list, tuple)) else [nomes or ""])).upper()
    for nome, padrao in SETORES:
        if re.search(padrao, texto):
            return nome
    return "Serviços e outros"


def faixa(pontos):
    return "Alta" if pontos >= 70 else "Média" if pontos >= 45 else "Baixa"
