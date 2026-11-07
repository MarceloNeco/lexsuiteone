"""DataJud (CNJ): estatística das varas.

O DataJud é a base nacional de metadados dos processos. É pública e responde
de qualquer lugar do mundo, mas:
  - NÃO traz nome das partes nem valor da causa;
  - chega com atraso (em out/2026, o TRT2 estava ~7 semanas atrás).
Por isso ele serve para o "raio-x" da vara (volume, assuntos, desfechos,
tempo até o fim), e o DJEN é quem traz as ações novas do dia.

A chave de acesso é pública e o CNJ a troca de tempos em tempos: em vez de
gravar a chave aqui (regra da SolverONE: nenhuma chave no código), o robô lê a
chave atual na página oficial do CNJ toda vez que roda. Se a página mudar, dá
para informar a chave pela variável de ambiente DATAJUD_APIKEY.
"""

import collections
import datetime as dt
import os
import re
import statistics

from . import rede

WIKI_CHAVE = "https://datajud-wiki.cnj.jus.br/api-publica/acesso/"
URL_TRIBUNAL = "https://api-publica.datajud.cnj.jus.br/api_publica_{sigla}/_search"

# Movimentos da Tabela Processual Unificada (TPU/CNJ) que encerram a fase de
# conhecimento. Conferidos nos dados reais do TRT2 (out/2026).
DESFECHOS = {
    466: "Acordo homologado",
    219: "Procedente",
    221: "Procedente em parte",
    220: "Improcedente",
    473: "Arquivado: reclamante faltou",
    463: "Desistência",
    454: "Inicial indeferida",
    459: "Extinto sem julgar o mérito",
    460: "Extinto sem julgar o mérito",
    461: "Extinto sem julgar o mérito",
    472: "Extinto sem julgar o mérito",
    371: "Enviado a outro juízo",
    941: "Enviado a outro juízo",
}
JULGADOS = {219, 220, 221}
JUIZO_100_DIGITAL = 14736
GRATUIDADE = 787

_chave = [None]


def chave_publica():
    if os.environ.get("DATAJUD_APIKEY"):
        return os.environ["DATAJUD_APIKEY"].strip()
    if _chave[0]:
        return _chave[0]
    html = rede.pedir(WIKI_CHAVE, cabecalhos={"Accept": "text/html"})
    texto = re.sub(r"<[^>]+>", " ", html)
    achou = re.search(r"APIKey\s+([A-Za-z0-9+/]{30,}={0,2})", texto)
    if not achou:
        raise RuntimeError(
            "Não achei a chave pública do DataJud na página do CNJ. Abra "
            f"{WIKI_CHAVE}, copie a chave e rode de novo com a variável DATAJUD_APIKEY.")
    _chave[0] = achou.group(1)
    return _chave[0]


def _buscar(sigla, corpo):
    url = URL_TRIBUNAL.format(sigla=sigla.lower())
    return rede.pedir_json(url, corpo, {"Authorization": "APIKey " + chave_publica()},
                           intervalo_minimo=0.3, tempo_limite=180)


def _data_num(d):
    """O DataJud guarda a data como número 'aaaammddhhmmss'; filtramos do mesmo jeito."""
    return int(d.strftime("%Y%m%d%H%M%S"))


def ler_data(valor):
    """Aceita '20260831235836', '2026-08-31T23:58:36Z' e variações."""
    if not valor:
        return None
    s = str(valor)
    if s.isdigit() and len(s) >= 8:
        return dt.date(int(s[:4]), int(s[4:6]), int(s[6:8]))
    try:
        return dt.date.fromisoformat(s[:10])
    except ValueError:
        return None


def numero_cnj(n):
    """'10036307620265020221' -> '1003630-76.2026.5.02.0221'."""
    n = re.sub(r"\D", "", str(n))
    if len(n) != 20:
        return str(n)
    return f"{n[:7]}-{n[7:9]}.{n[9:13]}.{n[13]}.{n[14:16]}.{n[16:]}"


def rito(classe_nome):
    c = (classe_nome or "").lower()
    if "sumaríssimo" in c or "sumarissimo" in c:
        return "Sumaríssimo"
    if "ordinário" in c or "ordinario" in c:
        return "Ordinário"
    return "Outros"


def listar_varas(sigla, inicio, fim, quantas=30):
    """Ranking das varas de 1º grau com mais ações distribuídas no período."""
    corpo = {"size": 0, "track_total_hits": True,
             "query": {"bool": {"filter": [
                 {"match": {"grau": "G1"}},
                 {"range": {"dataAjuizamento": {"gte": _data_num(inicio), "lte": _data_num(fim)}}}]}},
             "aggs": {"varas": {"terms": {"field": "orgaoJulgador.nome.keyword", "size": quantas}}}}
    r = _buscar(sigla, corpo)
    return [(b["key"], b["doc_count"]) for b in r["aggregations"]["varas"]["buckets"]]


def processos_da_vara(sigla, vara, inicio, fim, aviso=print):
    """Todos os processos de 1º grau ajuizados na vara entre `inicio` e `fim`."""
    campos = ["numeroProcesso", "dataAjuizamento", "classe.nome", "assuntos.nome",
              "orgaoJulgador.nome", "movimentos.codigo", "movimentos.dataHora"]
    corpo = {"size": 1000, "track_total_hits": True, "_source": campos,
             "query": {"bool": {"filter": [
                 {"match": {"grau": "G1"}},
                 {"match_phrase": {"orgaoJulgador.nome": vara}},
                 {"range": {"dataAjuizamento": {"gte": _data_num(inicio), "lte": _data_num(fim)}}}]}},
             "sort": [{"dataAjuizamento": "asc"}, {"numeroProcesso.keyword": "asc"}]}
    saida = []
    while True:
        r = _buscar(sigla, corpo)
        hits = r["hits"]["hits"]
        if not saida:
            aviso(f"  DataJud: {r['hits']['total']['value']} processos encontrados; baixando...")
        # match_phrase também acharia "1ª Vara..." dentro de "11ª Vara...": conferimos o nome exato.
        saida += [h["_source"] for h in hits
                  if (h["_source"].get("orgaoJulgador") or {}).get("nome", "").strip() == vara.strip()]
        if len(hits) < corpo["size"]:
            break
        corpo["search_after"] = hits[-1]["sort"]
    return saida


def _assuntos(doc):
    vistos, lista = set(), []
    for a in doc.get("assuntos") or []:
        if isinstance(a, list):  # alguns tribunais mandam lista dentro de lista
            a = a[0] if a else {}
        nome = re.sub(r"\s+", " ", (a or {}).get("nome") or "").strip()
        if nome and nome.lower() not in vistos:
            vistos.add(nome.lower())
            lista.append(nome)
    return lista


def desfecho(doc):
    """Primeiro movimento que encerra a fase de conhecimento: (rótulo, código, data) ou None."""
    melhor = None
    for m in doc.get("movimentos") or []:
        cod = m.get("codigo")
        if cod in DESFECHOS:
            quando = ler_data(m.get("dataHora"))
            if quando and (melhor is None or quando < melhor[2]):
                melhor = (DESFECHOS[cod], cod, quando)
    return melhor


def estatisticas(docs, sigla, vara, inicio, fim, recentes=60):
    """Transforma a lista de processos no raio-x da vara (só números, sem dado de pessoa)."""
    por_mes = collections.OrderedDict()
    d = dt.date(inicio.year, inicio.month, 1)
    while d <= fim:
        por_mes[d.strftime("%Y-%m")] = {"Ordinário": 0, "Sumaríssimo": 0, "Outros": 0}
        d = (d.replace(day=28) + dt.timedelta(days=4)).replace(day=1)

    assuntos = collections.Counter()
    finais = collections.Counter()
    dias_ate = collections.defaultdict(list)
    ritos = collections.Counter()
    digital = gratuidade = 0
    linhas = []
    for doc in docs:
        data = ler_data(doc.get("dataAjuizamento"))
        r = rito((doc.get("classe") or {}).get("nome"))
        ritos[r] += 1
        if data and data.strftime("%Y-%m") in por_mes:
            por_mes[data.strftime("%Y-%m")][r] += 1
        lista = _assuntos(doc)
        assuntos.update(lista)
        codigos = {m.get("codigo") for m in doc.get("movimentos") or []}
        digital += JUIZO_100_DIGITAL in codigos
        gratuidade += GRATUIDADE in codigos
        fim_proc = desfecho(doc)
        if fim_proc:
            finais[fim_proc[0]] += 1
            if data:
                dias_ate[fim_proc[0]].append((fim_proc[2] - data).days)
        linhas.append({
            "processo": numero_cnj(doc.get("numeroProcesso")),
            "data": data.isoformat() if data else "",
            "rito": r,
            "classe": (doc.get("classe") or {}).get("nome", ""),
            "assuntos": lista,
            "situacao": fim_proc[0] if fim_proc else "Em andamento",
        })

    total = len(docs)
    acoes = ritos["Ordinário"] + ritos["Sumaríssimo"]
    decididos = sum(v for k, v in finais.items() if k != "Enviado a outro juízo")
    julgados = sum(finais[DESFECHOS[c]] for c in (219, 221)) + finais[DESFECHOS[220]]
    procedentes = finais[DESFECHOS[219]] + finais[DESFECHOS[221]]
    meses = max(1, len(por_mes))
    todos_dias = [x for k, v in dias_ate.items() if k != "Enviado a outro juízo" for x in v]

    def pct(parte, todo):
        return round(100.0 * parte / todo, 1) if todo else 0.0

    def tem(*trechos):
        return sum(1 for l in linhas if any(t in a.lower() for a in l["assuntos"] for t in trechos))

    linhas.sort(key=lambda l: (l["data"], l["processo"]), reverse=True)
    return {
        "tribunal": sigla.upper(),
        "vara": vara,
        "periodo": {"inicio": inicio.isoformat(), "fim": fim.isoformat()},
        "ultimo_ajuizamento_na_base": linhas[0]["data"] if linhas else "",
        "total": total,
        "acoes_trabalhistas": acoes,
        "media_mes": round(total / meses, 1),
        "media_dia_util": round(total / (meses * 21), 1),
        "pct_ordinario": pct(ritos["Ordinário"], acoes),
        "pct_dano_moral": pct(tem("dano moral"), total),
        "pct_responsabilidade_subsidiaria": pct(tem("responsabilidade solid", "subsidiária"), total),
        "pct_doenca_acidente": pct(tem("doença ocupacional", "acidente de trabalho"), total),
        "pct_juizo_100_digital": pct(digital, total),
        "pct_gratuidade": pct(gratuidade, total),
        "decididos": decididos,
        "pct_acordo": pct(finais["Acordo homologado"], decididos),
        "pct_procedencia_julgados": pct(procedentes, julgados),
        "mediana_dias_desfecho": int(statistics.median(todos_dias)) if todos_dias else None,
        "por_mes": [{"mes": k, **v} for k, v in por_mes.items()],
        "assuntos_top": [{"assunto": a, "qtd": q, "pct": pct(q, total)} for a, q in assuntos.most_common(12)],
        "desfechos": [{"desfecho": k, "qtd": v, "pct": pct(v, sum(finais.values())),
                       "mediana_dias": int(statistics.median(dias_ate[k])) if dias_ate[k] else None}
                      for k, v in finais.most_common()],
        "recentes": linhas[:recentes],
    }
