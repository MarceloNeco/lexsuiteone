"""DJEN — Diário de Justiça Eletrônico Nacional (CNJ).

É onde saem, todo dia útil, as intimações e notificações de todos os tribunais,
inclusive os 24 TRTs. É daqui que vêm os nomes das empresas processadas.

ATENÇÃO: a API do DJEN só responde a pedidos que saem do Brasil (fora daqui
ela devolve 403 "block access from your country"). O robô precisa rodar num
computador ou servidor no Brasil.

Os nomes dos campos foram escritos de forma tolerante (aceita as variações já
vistas na API). Se algo mudar, rode com --diagnostico: o robô guarda a resposta
bruta em diagnostico/ para conferirmos.
"""

import io
import json
import os
import re
import urllib.parse
import zipfile

from . import classificar as cl
from . import rede
from .config import data_curta as _dc

URL = "https://comunicaapi.pje.jus.br/api/v1/comunicacao"
URL_CADERNO = "https://comunicaapi.pje.jus.br/api/v1/caderno/{sigla}/{data}/D"
POR_PAGINA = 100


def _pega(d, *nomes, padrao=""):
    for n in nomes:
        if isinstance(d, dict) and d.get(n) not in (None, ""):
            return d[n]
    return padrao


def normalizar(item):
    """Uma publicação do DJEN no formato do robô (sem perder o texto original)."""
    destinatarios = []
    for d in item.get("destinatarios") or []:
        destinatarios.append({"nome": _pega(d, "nome", "nomeDestinatario"),
                              "polo": str(_pega(d, "polo", "tipoPolo")).upper()[:1]})
    advogados = []
    for a in item.get("destinatarioadvogados") or item.get("destinatarioAdvogados") or []:
        adv = a.get("advogado") if isinstance(a, dict) and isinstance(a.get("advogado"), dict) else a
        advogados.append({"nome": _pega(adv, "nome"), "oab": _pega(adv, "numero_oab", "numeroOab"),
                          "uf": _pega(adv, "uf_oab", "ufOab")})
    data = _pega(item, "data_disponibilizacao", "dataDisponibilizacao")
    if not data and _pega(item, "datadisponibilizacao"):
        dd, mm, aa = str(item["datadisponibilizacao"]).split("/")[:3]
        data = f"{aa[:4]}-{mm}-{dd}"
    return {
        "id": str(_pega(item, "id", "hash", "numeroComunicacao")),
        "data": str(data)[:10],
        "tribunal": _pega(item, "siglaTribunal", "sigla_tribunal"),
        "vara": _pega(item, "nomeOrgao", "nome_orgao", "orgao"),
        "id_orgao": str(_pega(item, "idOrgao", "id_orgao", "orgaoId")),
        "processo": _pega(item, "numeroprocessocommascara", "numeroProcessoComMascara",
                          "numero_processo", "numeroProcesso"),
        "classe": _pega(item, "nomeClasse", "nome_classe"),
        "tipo_comunicacao": _pega(item, "tipoComunicacao", "tipo_comunicacao"),
        "tipo_documento": _pega(item, "tipoDocumento", "tipo_documento"),
        "texto": cl.limpar_texto(_pega(item, "texto")),
        "link": _pega(item, "link", "url"),
        "destinatarios": destinatarios,
        "advogados": advogados,
    }


def buscar_filtrado(filtros, data_inicio, data_fim, diagnostico=None, aviso=print, rotulo=""):
    """Publicações do período que batem com os filtros da API (ex.: numeroOab+ufOab,
    numeroProcesso, nomeParte, siglaTribunal). Datas 'aaaa-mm-dd'."""
    pagina, total, saida = 1, None, []
    while True:
        params = dict(filtros, dataDisponibilizacaoInicio=data_inicio, dataDisponibilizacaoFim=data_fim,
                      pagina=pagina, itensPorPagina=POR_PAGINA)
        resp = rede.pedir_json(URL + "?" + urllib.parse.urlencode(params), intervalo_minimo=1.0)
        if diagnostico and pagina == 1:
            os.makedirs(diagnostico, exist_ok=True)
            nome = re.sub(r"[^A-Za-z0-9]+", "-", cl.sem_acento("_".join(str(v) for v in filtros.values())))[:60]
            with open(os.path.join(diagnostico, f"djen_{nome}_{data_inicio}_p1.json"), "w",
                      encoding="utf-8") as f:
                json.dump(resp, f, ensure_ascii=False, indent=1)
        itens = resp.get("items") or resp.get("itens") or resp.get("content") or []
        if total is None:
            total = resp.get("count") or resp.get("total") or len(itens)
            aviso(f"  DJEN {rotulo or filtros} {data_inicio}..{data_fim}: {total} publicações")
        saida += [normalizar(i) for i in itens]
        if not itens or len(itens) < POR_PAGINA or len(saida) >= int(total or 0):
            break
        pagina += 1
    return saida


def buscar(sigla, data_inicio, data_fim, orgao_id=None, diagnostico=None, aviso=print):
    """Todas as publicações do tribunal no período (datas 'aaaa-mm-dd')."""
    filtros = {"siglaTribunal": sigla.upper()}
    if orgao_id:
        filtros["orgaoId"] = orgao_id
    return buscar_filtrado(filtros, data_inicio, data_fim, diagnostico, aviso, rotulo=sigla.upper())


def meta_caderno(sigla, data, aviso=print, motivos=None, tentativas=5):
    """Ficha do caderno do dia (status, versão, link de 5 minutos). None se ainda não saiu (404) ou se ainda não foi
    liberado (403 "só a partir das 03:00", 0.7.13); nesses casos `motivos[data]` recebe a causa."""
    from . import causas
    try:
        return rede.pedir_json(URL_CADERNO.format(sigla=sigla.upper(), data=data), intervalo_minimo=1.0, tentativas=tentativas)
    except RuntimeError as e:
        if causas.ainda_nao_liberado(e):
            aviso(f"  Caderno {sigla} {_dc(data)}: o Diário de hoje só fica disponível a partir das 3h; leio até o dia anterior")
            if motivos is not None:
                motivos[data] = "ainda_nao_liberado_3h"
            return None
        if "HTTP 404" in str(e):
            aviso(f"  Caderno {sigla} {_dc(data)}: ainda não publicado")
            if motivos is not None:
                motivos[data] = "nao_publicado"
            return None
        raise


def baixar_caderno(sigla, data, diagnostico=None, aviso=print, meta=None):
    """O diário inteiro do tribunal num dia (um ZIP de JSONs). 1 pedido por TRT por dia:
    é o jeito mais leve para os sistemas do CNJ. Devolve None se o caderno ainda não saiu."""
    meta = meta or meta_caderno(sigla, data, aviso)
    if meta is None:
        return None
    if str(meta.get("status", "")).lower().startswith("sem comunica"):
        return []
    if not meta.get("url"):
        aviso(f"  Caderno {sigla} {_dc(data)}: {meta.get('status', 'sem link')}")
        return None
    bruto = rede.pedir_bytes(meta["url"], tempo_limite=600)
    itens = []
    with zipfile.ZipFile(io.BytesIO(bruto)) as z:
        # Arquivo baixado é entrada não confiável: limita o tamanho descompactado (zip bomb) e ignora o que não é JSON.
        if sum(i.file_size for i in z.infolist()) > rede.LIMITE_DOWNLOAD:
            raise ValueError(f"caderno {sigla} {data} grande demais ao descompactar")
        for nome in z.namelist():
            if nome.lower().endswith(".json"):
                dados = json.loads(z.read(nome).decode("utf-8"))
                itens += (dados.get("items") or []) if isinstance(dados, dict) else dados
    if diagnostico:
        os.makedirs(diagnostico, exist_ok=True)
        with open(os.path.join(diagnostico, f"caderno_{sigla}_{data}_amostra.json"), "w", encoding="utf-8") as f:
            json.dump({"meta": meta, "amostra": itens[:20]}, f, ensure_ascii=False, indent=1)
    aviso(f"  Caderno {sigla} {_dc(data)}: {len(itens)} publicações")
    return [normalizar(i) for i in itens]


def mapa_orgaos(publicacoes):
    """{nome da vara: idOrgao} a partir das publicações de um caderno (para a busca por vara)."""
    mapa = {}
    for p in publicacoes:
        if p.get("vara") and p.get("id_orgao") not in ("", "None", None):
            mapa.setdefault(p["vara"], p["id_orgao"])
    return dict(sorted(mapa.items()))


def leads(publicacoes, vara=None, ano_minimo=None, ja_vistos=()):
    """Agrupa as publicações por processo e monta um lead por ação nova contra empresa."""
    por_processo = {}
    for p in publicacoes:
        if vara and cl.sem_acento(vara).lower() not in cl.sem_acento(p["vara"]).lower():
            continue
        if cl.segundo_grau(p.get("vara")):  # 0.7.17: recurso distribuído a turma não é ação nova
            continue
        if cl.sem_acento(str(p.get("classe") or "")).strip().lower().startswith("cumprimento"):
            continue  # 0.7.51 (desenho das datas e fontes): cumprimento de sentença nasce de outro processo; não é ação nova
        ano = cl.ano_do_processo(p["processo"])
        if ano_minimo and (ano is None or ano < ano_minimo):
            continue  # processo antigo: não é ação nova
        por_processo.setdefault(p["processo"], []).append(p)

    resultado = []
    for processo, pubs in por_processo.items():
        if processo in ja_vistos:
            continue
        empresas, cnpjs, valor, inicio, sinal = [], [], None, False, ""
        for p in pubs:
            candidatos = [d["nome"] for d in p["destinatarios"] if d["polo"] == "P"]
            candidatos += cl.reclamadas_no_texto(p["texto"])
            for nome in (cl.limpar_nome(x) for x in candidatos):
                # Só empresa entra; pessoa física é descartada aqui mesmo.
                if cl.eh_empresa(nome) and nome.upper() not in (e.upper() for e in empresas):
                    empresas.append(nome)
            for c in cl.extrair_cnpjs(p["texto"]):
                if c not in cnpjs:
                    cnpjs.append(c)
            valor = valor or cl.extrair_valor_causa(p["texto"])
            # "Lista de distribuição" é o próprio aviso de ação nova (Ato Conjunto CSJT 77/2023).
            if "distribui" in cl.sem_acento(p["tipo_comunicacao"]).lower():
                inicio, sinal = True, "lista de distribuição"
            elif not inicio and cl.parece_inicio(p["texto"]):
                inicio, sinal = True, cl.sinal_inicio(p["texto"])
        if not empresas:
            continue
        primeira = min(pubs, key=lambda x: x["data"])
        resultado.append({
            "processo": processo,
            "data_publicacao": primeira["data"],
            "tribunal": primeira["tribunal"],
            "vara": primeira["vara"],
            "classe": primeira["classe"],
            "rito": "Sumaríssimo" if "SUMAR" in cl.sem_acento(primeira["classe"]).upper()
                    else "Ordinário" if "ORDIN" in cl.sem_acento(primeira["classe"]).upper() else "Outros",
            "empresas": empresas,
            "cnpjs": cnpjs,
            "valor_causa": valor,
            "sinal_de_acao_nova": inicio,
            "sinal": sinal,
            "tipo": primeira["tipo_documento"] or primeira["tipo_comunicacao"],
            "fonte": "DJEN",
            "id_orgao": primeira.get("id_orgao", ""),
            "link": primeira["link"],
            "qtd_publicacoes": len(pubs),
            # Trecho curto só para classificar assuntos; o texto inteiro não vai para a planilha.
            "texto_curto": primeira["texto"][:600],
        })
    return resultado


# ---------- 0.7.48: leitura pela consulta pública quando o caderno cai (desenho "CNJ fora e antivírus", 1.3; decisão 37) ----------
CONSULTA_POR_PAGINA = 100
CONSULTA_TETO = 10000  # a consulta não passa disso por pedido: acima, divide por vara (orgaoId)
CONSULTA_TEMPO = 15


class ConsultaParou(RuntimeError):
    """Três tempos esgotados seguidos: a consulta pública também está fora; para sem insistir."""


def consulta_dia(sigla, data, varas=None, aviso=print, parar=None, pedir=None, progresso=None):
    """As comunicações de um tribunal num dia pela consulta pública (o mesmo formato do caderno). 1 pedido por segundo, 15 s
    de limite, 1 nova tentativa só em tempo esgotado e 5xx, parar depois de 3 tempos esgotados seguidos. Se `count` chegar a
    10.000, divide por vara (`varas`: [(id_orgao, nome)], montada dos cadernos já lidos). Devolve (publicações, info) com info =
    {count, pedidos, parcial, varas}. Levanta ConsultaParou (3 tempos esgotados) e a Interrompida de quem chama (parar)."""
    pedir = pedir or (lambda url: rede.pedir_json(url, tentativas=2, intervalo_minimo=1.0, tempo_limite=CONSULTA_TEMPO))
    info = {"count": 0, "pedidos": 0, "parcial": False, "varas": 0, "por_pagina": CONSULTA_POR_PAGINA}
    seguidos, erros5 = [0], [0]
    por = [CONSULTA_POR_PAGINA]  # se a consulta recusar 100 por página (400/422), passa a 50 (desenho 1.3: "50 ou 100")

    def um(params):
        if parar and parar():
            from .radar import Interrompida
            raise Interrompida("interrompida")
        url = URL + "?" + urllib.parse.urlencode(params)
        info["pedidos"] += 1
        try:
            r = pedir(url)
        except rede.SemResposta:
            seguidos[0] += 1
            if seguidos[0] >= 3:
                raise ConsultaParou(f"consulta pública sem resposta 3 vezes seguidas ({sigla} {data})") from None
            info["parcial"] = True
            return None
        except rede.ErroHTTP as e:
            info["parcial"] = True  # 5xx depois da nova tentativa: perde esta página, segue com as outras
            if e.codigo < 500:
                raise
            erros5[0] += 1
            if erros5[0] >= 5:  # revisão: a consulta respondendo só 5xx também para (não percorre 100 páginas)
                raise ConsultaParou(f"consulta pública com erro do servidor 5 vezes seguidas ({sigla} {data})") from None
            return None
        except ValueError:  # resposta que não é JSON: perde a página, como um 5xx
            info["parcial"] = True
            return None
        seguidos[0] = erros5[0] = 0
        return r if isinstance(r, dict) else {}

    def paginas(filtros, dividir=False):
        """Todas as páginas de um filtro. Com `dividir`, para logo na 1ª página se `count` chegar ao teto (vai por vara)."""
        saida, pagina, vazias, total = [], 1, 0, None
        while pagina <= CONSULTA_TETO // por[0]:
            try:
                r = um(dict(filtros, dataDisponibilizacaoInicio=data, dataDisponibilizacaoFim=data, pagina=pagina, itensPorPagina=por[0]))
            except rede.ErroHTTP as e:
                if e.codigo in (400, 422) and por[0] > 50 and pagina == 1:
                    por[0] = info["por_pagina"] = 50
                    info["parcial"] = False
                    continue
                if e.codigo in (401, 403, 429):  # revisão da Operação: o CNJ recusou; nem a próxima vara insiste
                    raise ConsultaParou(f"a consulta pública recusou o pedido (HTTP {e.codigo}) ({sigla} {data})") from None
                break  # outro 4xx: este filtro não tem mais o que dar; não insiste
            if r is None:
                pagina += 1
                continue
            itens = r.get("items") or r.get("itens") or r.get("content") or []
            if total is None:
                try:
                    total = int(r.get("count") if r.get("count") is not None else r.get("total"))
                except (TypeError, ValueError):
                    total = 0  # sem `count` na resposta: segue até uma página curta
                if dividir and total >= CONSULTA_TETO:
                    return saida, total, True
            saida += [normalizar(i) for i in itens]
            if progresso:
                progresso(len(saida), max(total, len(saida)))
            if not itens:
                vazias += 1  # página vazia no meio: tenta mais uma antes de parar
                if vazias >= 2 or (total and len(saida) >= total):
                    break
            else:
                vazias = 0
                if len(itens) < por[0] or (total and len(saida) >= total):
                    break
            pagina += 1
        return saida, max(total or 0, len(saida)), False

    base = {"siglaTribunal": sigla.upper()}
    pubs, total, cortou = paginas(base, dividir=bool(varas))
    info["count"] = total
    if cortou:  # 10.000 ou mais: vara por vara (a lista vem dos cadernos já lidos)
        pubs, vistos = [], set()
        info["varas"] = len(varas)
        for k, (orgao, _nome) in enumerate(varas, 1):
            aviso(f"  Consulta pública {sigla} {_dc(data, False)}: vara {k} de {len(varas)}")
            parte, _, _ = paginas(dict(base, orgaoId=orgao))
            for p in parte:
                if p["id"] not in vistos:
                    vistos.add(p["id"])
                    pubs.append(p)
    elif total >= CONSULTA_TETO:
        info["parcial"] = True  # sem a lista de varas (nenhum caderno lido ainda), fica com os primeiros 10.000
    for p in pubs:
        p["fonte_leitura"] = "consulta"
    return pubs, info


def historico_por_numero(numero, desde, ate, buscar=None, aviso=lambda *_: None):
    """0.7.51 (desenho das datas e fontes): todas as publicações de um processo no DJEN, do ano do número até hoje. Guarda só datas e
    tipos (o texto e os destinatários, onde aparecem pessoas, ficam só na memória e se descartam: Res. CNJ 121/2010 e regra do produto).
    Devolve {pub1, pubN, dias, tipos, distribuicao} — distribuicao = 1ª publicação da lista de distribuição, quando houver."""
    buscar = buscar or buscar_filtrado
    pubs = buscar({"numeroProcesso": re.sub(r"\D", "", str(numero or ""))}, desde, ate, None, aviso, rotulo="histórico")
    dias, tipos, dist = set(), set(), []
    for p in pubs:
        d = str(p.get("data") or "")[:10]
        if not re.match(r"\d{4}-\d{2}-\d{2}$", d):
            continue
        dias.add(d)
        tp = " ".join(str(p.get(k) or "") for k in ("tipo_documento", "tipo_comunicacao")).strip()
        if tp:
            tipos.add(tp[:60])
        texto = cl.sem_acento(str(p.get("texto") or "")[:600]).lower()
        if "distribui" in cl.sem_acento(tp).lower() or "processo distribuid" in texto or "lista de distribuic" in texto:
            dist.append(d)
    ds = sorted(dias)
    return {"pub1": ds[0] if ds else "", "pubN": ds[-1] if ds else "", "dias": len(ds), "tipos": sorted(tipos)[:8],
            "distribuicao": min(dist) if dist else ""}
