"""Relatório de diagnóstico do Radar SP: o que o robô guardou, contado e com amostras mascaradas.

Serve para calibrar a regra de "ação nova" com dados reais sem mandar o banco inteiro. O texto sai sem nome de
pessoa física (reclamantes, advogados) e sem CPF: só o que é preciso para ajustar as regras.
"""

import collections
import datetime as dt
import random
import re

from . import classificar as cl

# Cada pista da regra atual, separada, para contar qual delas está puxando o número para cima.
PISTAS = [
    ("audiência inicial/una/conciliação", re.compile(r"audi[eê]ncia\s+(inicial|una|de\s+concilia)", re.I)),
    ("notificação inicial", re.compile(r"notifica[cç][aã]o\s+inicial", re.I)),
    ("designada audiência", re.compile(r"designad[ao]\s+audi[eê]ncia", re.I)),
    ("fica ... notificad", re.compile(r"fica\s+.{0,40}notificad", re.I)),
    ("distribuíd[oa]", re.compile(r"distribu[ií]d[ao]", re.I)),
    ("citação", re.compile(r"cita[cç][aã]o", re.I)),
    ("notifique-se a reclamada", re.compile(r"notifique-se\s+(a|as|o|os)\s+reclamad", re.I)),
    ("audiência + data marcada", re.compile(r"audi[eê]ncia.{0,120}\d{2}/\d{2}/\d{4}", re.I | re.S)),
]
# Regra estrita em teste: só pistas que falam do começo do processo.
ESTRITA = {"audiência inicial/una/conciliação", "notificação inicial", "designada audiência", "notifique-se a reclamada"}

_CPF = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
_ATIVO = re.compile(cl._ROT_ATIVO + r"\s*:\s*(.{3,160}?)" + cl._FIM_NOME)
_ADV = re.compile(r"(ADVOGAD[OA]S?)\s*:\s*(.{3,160}?)(?=\s+(?:" + cl._ROT_PASSIVO + r"|" + cl._ROT_ATIVO + r"|ADVOGAD|OAB|\n)|$)")


def mascarar(texto):
    """Tira nome de reclamante e de advogado e qualquer CPF do trecho. Empresas ficam."""
    t = texto or ""
    t = _ATIVO.sub(lambda m: m.group(0)[:m.start(1) - m.start(0)] + "[pessoa]", t)
    t = _ADV.sub(lambda m: m.group(1) + ": [advogado]", t)
    t = _CPF.sub("[cpf]", t)
    return t


def pistas_do_texto(texto, tipo=""):
    achadas = [nome for nome, rx in PISTAS if rx.search(texto or "")]
    if "distribui" in cl.sem_acento(tipo or "").lower():
        achadas.append("tipo: lista de distribuição")
    return achadas


def sequencial(processo):
    m = re.match(r"\s*(\d{7})", processo or "")
    return int(m.group(1)) if m else None


def relatorio_radar(leads, amostras=40, agora=None, semente=7):
    agora = agora or dt.datetime.now()
    leads = [l for l in leads if l.get("fonte", "DJEN") == "DJEN"]
    rnd = random.Random(semente)
    por_trib = collections.Counter((l.get("tribunal") or "?") for l in leads)
    por_tipo = collections.Counter((l.get("tipo") or "?") for l in leads)
    por_classe = collections.Counter((l.get("classe") or "?") for l in leads)
    por_qtd = collections.Counter(min(int(l.get("qtd_publicacoes") or 1), 3) for l in leads)
    por_pista = collections.Counter()
    estritos, frouxos = [], []
    for l in leads:
        p = pistas_do_texto(l.get("texto_curto", ""), l.get("tipo", ""))
        l["_pistas"] = p
        for nome in p:
            por_pista[nome] += 1
        (estritos if (set(p) & ESTRITA or "tipo: lista de distribuição" in p) else frouxos).append(l)
    varas = collections.defaultdict(list)
    for l in leads:
        varas[(l.get("tribunal"), l.get("vara") or "?")].append(sequencial(l.get("processo")) or 0)
    empresas = collections.Counter(e.upper() for l in leads for e in (l.get("empresas") or []))
    com_cnpj = sum(1 for l in leads if l.get("cnpjs"))
    datas = collections.Counter((l.get("data_publicacao") or "?")[:10] for l in leads)

    s = []
    w = s.append
    w(f"LexSuiteONE · diagnóstico do Radar SP · gerado em {agora:%d/%m/%Y %H:%M}")
    w("Sem dado de pessoa física: nomes de reclamantes e advogados e CPFs foram trocados por [pessoa], [advogado], [cpf].")
    w("")
    w(f"Leads guardados: {len(leads)} · " + " · ".join(f"{t}: {n}" for t, n in sorted(por_trib.items())))
    w(f"Com CNPJ no texto: {com_cnpj} · Datas: " + ", ".join(f"{d}: {n}" for d, n in sorted(datas.items())))
    w("")
    w("== Por tipo de publicação ==")
    for t, n in por_tipo.most_common(25):
        w(f"  {n:6d}  {t}")
    w("")
    w("== Por classe ==")
    for t, n in por_classe.most_common(25):
        w(f"  {n:6d}  {t}")
    w("")
    w("== Publicações do mesmo processo no dia ==")
    w("  " + " · ".join(f"{'3 ou mais' if k == 3 else k}: {por_qtd[k]}" for k in sorted(por_qtd)))
    w("")
    w("== Pistas de 'ação nova' (um lead pode ter várias) ==")
    for nome, _ in PISTAS:
        w(f"  {por_pista[nome]:6d}  {nome}" + ("   [estrita]" if nome in ESTRITA else ""))
    w(f"  {por_pista['tipo: lista de distribuição']:6d}  tipo: lista de distribuição   [estrita]")
    w("")
    w(f"== Regra estrita (só pistas marcadas): {len(estritos)} leads · só na regra atual: {len(frouxos)} ==")
    w("")
    w("== Varas com mais leads (número sequencial do processo: menor / mediana / maior) ==")
    for (trib, vara), seqs in sorted(varas.items(), key=lambda kv: -len(kv[1]))[:40]:
        seqs = sorted(x for x in seqs if x)
        if seqs:
            w(f"  {len(seqs):5d}  {trib} · {vara} · {seqs[0]} / {seqs[len(seqs) // 2]} / {seqs[-1]}")
        else:
            w(f"  {len(varas[(trib, vara)]):5d}  {trib} · {vara}")
    w("")
    w("== Empresas mais citadas ==")
    for nome, n in empresas.most_common(40):
        w(f"  {n:5d}  {nome}")
    w("")
    for titulo, grupo in (("AMOSTRAS · batem na regra estrita", estritos), ("AMOSTRAS · só na regra atual", frouxos)):
        w(f"== {titulo} ({min(amostras, len(grupo))} de {len(grupo)}) ==")
        for l in rnd.sample(grupo, min(amostras, len(grupo))):
            w(f"--- {l.get('tribunal')} · {l.get('vara')} · {l.get('processo')} · {l.get('classe')} · tipo: {l.get('tipo')}"
              f" · {l.get('qtd_publicacoes', 1)} publ. · pistas: {', '.join(l['_pistas']) or 'nenhuma'}")
            w("    empresas: " + "; ".join(l.get("empresas") or []))
            w("    " + mascarar(l.get("texto_curto", "")).replace("\n", " ⏎ "))
        w("")
    for l in leads:
        l.pop("_pistas", None)
    return "\n".join(s)
