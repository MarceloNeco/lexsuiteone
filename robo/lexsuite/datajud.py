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
import time

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
_chave_falhou = [0.0]  # 0.7.52: quando a página da chave falhou (relógio monotônico); 0 = nunca
CHAVE_ESPERA = 600  # segundos sem tentar de novo depois de falhar


def chave_publica():
    if os.environ.get("DATAJUD_APIKEY"):
        return os.environ["DATAJUD_APIKEY"].strip()
    if _chave[0]:
        return _chave[0]
    # 0.7.52 (ressalva 1 da Operação): a página do CNJ fora não pode prender a leitura por minutos (antes: 5 tentativas de 120 s).
    # Duas tentativas curtas; se falhar, não tenta de novo por 10 minutos (a fila das fontes tenta depois).
    if _chave_falhou[0] and time.monotonic() - _chave_falhou[0] < CHAVE_ESPERA:
        raise RuntimeError("Chave pública do DataJud não lida há pouco; tento de novo mais tarde.")
    try:
        html = rede.pedir(WIKI_CHAVE, cabecalhos={"Accept": "text/html"}, tentativas=2, tempo_limite=20)
    except Exception:
        _chave_falhou[0] = time.monotonic()
        raise
    texto = re.sub(r"<[^>]+>", " ", html)
    achou = re.search(r"APIKey\s+([A-Za-z0-9+/]{30,}={0,2})", texto)
    if not achou:
        _chave_falhou[0] = time.monotonic()
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


# ---------- 0.7.51: datas e jornada do processo (desenho documentacao/DESENHO-DATAS-E-FONTES-0751.md) ----------
# Só funções puras e a consulta em lote; quem decide quando consultar é a leitura (depois do "pode" do dono).
# Do DataJud só entram códigos e nomes tabelados (classe, assuntos, órgão, movimentos); nunca partes nem texto livre.
MARCOS = {  # Tabela Processual Unificada (TPU/CNJ): o que vira marco na jornada do processo
    26: "distribuicao", 36: "redistribuicao", 12747: "aud_inicial", 12740: "aud_conciliacao", 12749: "aud_instrucao",
    12751: "aud_julgamento", 12752: "aud_una", 970: "audiencia", 785: "tutela", 466: "acordo", 219: "procedente",
    220: "improcedente", 221: "procedente_parte", 458: "extinto", 123: "remessa", 848: "transito", 11384: "liquidacao",
    11385: "execucao", 196: "execucao_extinta", 246: "arquivado", 245: "arquivado_prov", 22: "baixa"}
DISPONIBILIZACAO = 1061  # "disponibilização no DJE": vem em dobro no mesmo dia; conta-se o dia
SITUACOES = {"designada": "marcada", "realizada": "realizada", "cancelada": "cancelada", "redesignada": "remarcada",
             "nao-realizada": "nao_realizada", "não-realizada": "nao_realizada"}
CAMPOS = ["numeroProcesso", "grau", "dataAjuizamento", "classe", "assuntos", "orgaoJulgador", "movimentos.codigo", "movimentos.nome",
          "movimentos.dataHora", "movimentos.complementosTabelados", "dataHoraUltimaAtualizacao"]
LOTE = 40


class RespostaParcial(Exception):
    """O DataJud respondeu sem todos os pedaços (shards), com tempo esgotado ou recusou por excesso: nada desse lote é "não encontrado"."""


def classe_nao_e_nova(nome):
    """Cumprimento de sentença (provisório ou não) nasce de outro processo: não é ação nova contra a empresa."""
    c = re.sub(r"\s+", " ", str(nome or "")).strip().lower()
    return c.startswith("cumprimento") or "execução provisória" in c or "execucao provisoria" in c


def indice_do_numero(numero):
    """'1000910-15.2026.5.02.0714' → 'trt2' (Justiça do Trabalho, J=5). Outros ramos ainda não: ''."""
    n = re.sub(r"\D", "", str(numero or ""))
    if len(n) != 20 or n[13] != "5":
        return ""
    return f"trt{int(n[14:16])}"


def _iso(valor):
    d = ler_data(valor)
    return d.isoformat() if d else ""


def andamento(codigos):
    """'' (sem acordo nem sentença), 'acordo', 'sentenca', 'transito' ou 'arquivado', pelo que já aconteceu."""
    c = set(codigos)
    if c & {246, 22}:
        return "arquivado"
    if 848 in c:
        return "transito"
    if c & {219, 220, 221, 458}:
        return "sentenca"
    if 466 in c:
        return "acordo"
    return ""


def resumo_processo(src, limite_marcos=60):
    """Do documento do DataJud ao que o RADAR guarda (dados.cnj): ajuizamento, classe, assuntos, órgão, marcos
    [[data, código, situação]], dias de publicação no Diário (1ª e última), andamento e até quando o CNJ está atualizado."""
    mv = sorted([m for m in (src.get("movimentos") or []) if isinstance(m, dict)], key=lambda m: str(m.get("dataHora") or ""))
    dias_pub = sorted({str(m.get("dataHora") or "")[:10] for m in mv if m.get("codigo") == DISPONIBILIZACAO and m.get("dataHora")})
    marcos, vistos, aj = [], set(), _iso(src.get("dataAjuizamento"))
    for m in mv:
        cod = m.get("codigo")
        if cod not in MARCOS or not m.get("dataHora"):
            continue
        comp = m.get("complementosTabelados") or []
        if cod == 123 and any("outros motivos" in str(x.get("nome") or "").lower() for x in comp if isinstance(x, dict)):
            continue  # remessa por "outros motivos" no começo (ex.: ao CEJUSC) não é recurso
        sit = next((str(x.get("nome") or "").lower() for x in comp if isinstance(x, dict) and x.get("descricao") == "situacao_da_audiencia"), "")
        k = (str(m["dataHora"])[:10], cod, SITUACOES.get(sit, ""))
        if k in vistos:
            continue
        vistos.add(k)
        marcos.append(list(k))
    if not aj and marcos and marcos[0][1] == 26:
        aj = marcos[0][0]
    org = src.get("orgaoJulgador") or {}
    return {"ajuizado": aj, "ajuizado_hora": str(src.get("dataAjuizamento") or "")[8:14] if str(src.get("dataAjuizamento") or "").isdigit() else "",
            "classe": str((src.get("classe") or {}).get("nome") or "")[:120],
            "assuntos": list(dict.fromkeys(str(a.get("nome") or "").strip() for a in (src.get("assuntos") or []) if isinstance(a, dict) and a.get("nome")))[:5],
            "orgao": str(org.get("nome") or "")[:160], "marcos": marcos[-limite_marcos:],
            "pub1": dias_pub[0] if dias_pub else "", "pubN": dias_pub[-1] if dias_pub else "", "dias_publicacao": len(dias_pub),
            "andamento": andamento(m.get("codigo") for m in mv), "atualizado_em": _iso(src.get("dataHoraUltimaAtualizacao"))}


def _melhor(docs):
    """O mesmo número vem no 1º grau (G1) e no tribunal (G2): fica o G1 atualizado por último."""
    g1 = [d for d in docs if str(d.get("grau") or "").upper() == "G1"] or docs
    return max(g1, key=lambda d: str(d.get("dataHoraUltimaAtualizacao") or ""))


def consultar_lote(indice, numeros, pedir=None):
    """Um pedido ao DataJud com até 40 números (20 dígitos) do mesmo tribunal. Devolve {número: documento ou None}.
    Levanta RespostaParcial quando a resposta não é confiável (o lote todo fica "falhou", nunca "não encontrado")."""
    numeros = [re.sub(r"\D", "", str(n)) for n in numeros][:LOTE]
    corpo = {"size": 200, "_source": CAMPOS, "query": {"terms": {"numeroProcesso": numeros}}}
    if pedir is None:
        def pedir(url, c):
            # 0.7.52 (ressalva 3 da Operação): uma tentativa por lote; o 429 para o CNJ nesta leitura (radar.completar_fontes)
            return rede.pedir_json(url, c, {"Authorization": "APIKey " + chave_publica()}, tentativas=1, intervalo_minimo=1.0, tempo_limite=30)
    r = pedir(URL_TRIBUNAL.format(sigla=indice), corpo)
    if not isinstance(r, dict) or r.get("error") or r.get("timed_out") or ((r.get("_shards") or {}).get("failed") or 0) > 0:
        raise RespostaParcial(str((r or {}).get("error") or "resposta parcial")[:200] if isinstance(r, dict) else "resposta inválida")
    hits = [h.get("_source") or {} for h in ((r.get("hits") or {}).get("hits") or [])]
    total = ((r.get("hits") or {}).get("total") or {})
    if isinstance(total, dict) and int(total.get("value") or 0) > len(hits):
        raise RespostaParcial("total maior que os documentos recebidos")
    por = collections.defaultdict(list)
    for h in hits:
        por[re.sub(r"\D", "", str(h.get("numeroProcesso") or ""))].append(h)
    return {n: (_melhor(por[n]) if por.get(n) else None) for n in numeros}
