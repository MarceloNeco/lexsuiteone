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


def meta_caderno(sigla, data, aviso=print, motivos=None):
    """Ficha do caderno do dia (status, versão, link de 5 minutos). None se ainda não saiu (404) ou se ainda não foi
    liberado (403 "só a partir das 03:00", 0.7.13); nesses casos `motivos[data]` recebe a causa."""
    from . import causas
    try:
        return rede.pedir_json(URL_CADERNO.format(sigla=sigla.upper(), data=data), intervalo_minimo=1.0)
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
