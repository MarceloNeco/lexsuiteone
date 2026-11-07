"""Pauta pública de audiências do PJe da Justiça do Trabalho (segunda fonte).

A pauta é pública (as audiências são públicas), não pede login nem captcha e
responde até de fora do Brasil. Ela traz o número do processo, o tipo da
audiência e os nomes das partes. A primeira audiência ("Una" ou "Inicial")
costuma ser marcada poucas semanas depois que a ação entra, então a pauta dos
próximos dias mostra as ações recém-chegadas na vara.

Uso aqui: demonstração e conferência cruzada com o DJEN. Pouquíssimos pedidos,
com intervalo entre eles. Nunca tentar abrir o detalhe do processo (lá há
captcha, e captcha não se contorna).
"""

import datetime as dt
import urllib.parse

from . import classificar as cl
from . import rede

BASE = "https://pje.trt{n}.jus.br/pje-consulta-api/api"
CABECALHO = {"X-Grau-Instancia": "1"}
PRIMEIRA_AUDIENCIA = ("una", "inicial", "concilia")


def _base(sigla):
    return BASE.format(n=int("".join(c for c in sigla if c.isdigit())))


def id_da_vara(sigla, vara):
    orgaos = rede.pedir_json(_base(sigla) + "/orgaosjulgadores?somenteOJCs=true", cabecalhos=CABECALHO,
                             intervalo_minimo=1.5)
    for o in orgaos:
        if cl.sem_acento(o.get("descricao", "")).strip().lower() == cl.sem_acento(vara).strip().lower():
            return o["id"]
    raise SystemExit(f"Vara '{vara}' não encontrada na lista do {sigla}.")


def audiencias(sigla, id_oj, data):
    saida, pagina = [], 1
    while True:
        q = urllib.parse.urlencode({"pagina": pagina, "tamanhoPagina": 100, "idOj": id_oj, "data": data})
        r = rede.pedir_json(_base(sigla) + "/audiencias?" + q, cabecalhos=CABECALHO, intervalo_minimo=1.5)
        saida += r.get("resultado") or []
        if pagina >= int(r.get("qtdPaginas") or 1):
            return saida
        pagina += 1


def dias_uteis(a_partir, quantos):
    d, lista = a_partir, []
    while len(lista) < quantos:
        if d.weekday() < 5:
            lista.append(d)
        d += dt.timedelta(days=1)
    return lista


def leads_da_pauta(sigla, vara, dias=10, a_partir=None, aviso=print):
    """Ações com primeira audiência marcada nos próximos dias úteis, em que a ré é empresa."""
    id_oj = id_da_vara(sigla, vara)
    hoje = a_partir or dt.date.today()
    ano_minimo = hoje.year - 1 if hoje.month <= 2 else hoje.year
    por_processo = {}
    for d in dias_uteis(hoje, dias):
        itens = audiencias(sigla, id_oj, d.isoformat())
        aviso(f"  Pauta {d:%d/%m}: {len(itens)} audiências")
        for a in itens:
            tipo = (a.get("tipo") or "").lower()
            if not any(p in cl.sem_acento(tipo) for p in PRIMEIRA_AUDIENCIA):
                continue
            if (a.get("classeProcesso") or "") not in ("ATOrd", "ATSum"):
                continue
            ano = cl.ano_do_processo(a.get("numeroProcesso"))
            if ano is None or ano < ano_minimo:
                continue
            # Só o polo passivo e só empresa: o reclamante (pessoa física) nem é lido.
            empresas = [p["nome"].strip() for p in a.get("poloPassivo") or [] if cl.eh_empresa(p.get("nome"))]
            if not empresas:
                continue
            por_processo.setdefault(a["numeroProcesso"], {
                "processo": a["numeroProcesso"], "tribunal": sigla.upper(), "vara": vara,
                "classe": a.get("classeProcesso"),
                "rito": "Sumaríssimo" if a.get("classeProcesso") == "ATSum" else "Ordinário",
                "empresas": empresas, "cnpjs": [], "valor_causa": None, "sinal_de_acao_nova": True,
                "fonte": "Pauta de audiências (PJe)", "data_publicacao": "",
                "audiencia": {"data": (a.get("data") or "")[:10], "tipo": a.get("tipo"),
                              "juizo_digital": bool(a.get("juizoDigital"))},
                "link": "", "texto_curto": "", "assuntos": [],
            })
    return list(por_processo.values())
