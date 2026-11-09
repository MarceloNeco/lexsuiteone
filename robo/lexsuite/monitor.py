"""Monitor: avisa o escritório assim que sai algo no DJEN nos processos que ele acompanha.

O DJEN não tem webhook (não "empurra" nada). O robô pergunta de tempos em tempos,
compara com o que já viu e avisa só o que é novo — para quem recebe, funciona
como um aviso automático no celular.

Três jeitos de achar as publicações do escritório:
  1. OAB dos advogados (numeroOab + ufOab): pega toda intimação em que eles aparecem;
  2. número dos processos acompanhados (processos.csv), inclusive os que o escritório
     ainda não tem advogado cadastrado;
  3. nome dos clientes (carteira.csv e "partes" no config.json): pega ação nova contra eles.

Duas formas de consulta:
  - busca filtrada (padrão): poucos pedidos, rápida, para rodar várias vezes à noite;
  - caderno do dia (--caderno): baixa o diário inteiro do tribunal e confere tudo aqui,
    sem limite de quantidade. É a rede de segurança da manhã.
"""

import csv
import datetime as dt
import time
import hashlib
import json
import os
import re

from . import classificar as cl
from . import djen, prazos, rede

URGENCIAS = ("Urgente", "Alta", "Normal")


# --- O que acompanhar -------------------------------------------------------

def so_digitos(s):
    return re.sub(r"\D", "", str(s or ""))


def ler_processos(caminho):
    """processos.csv (separado por ;): processo;cliente;responsavel — um processo por linha."""
    saida = {}
    if not caminho or not os.path.exists(caminho):
        return saida
    with open(caminho, encoding="utf-8-sig") as f:
        for linha in csv.DictReader(f, delimiter=";"):
            num = so_digitos(linha.get("processo"))
            if len(num) == 20:
                saida[num] = {"processo": (linha.get("processo") or "").strip(),
                              "cliente": (linha.get("cliente") or "").strip(),
                              "responsavel": (linha.get("responsavel") or "").strip()}
    return saida


def montar_alvos(cfg_monitor, carteira_csv=None, processos_csv=None):
    oabs = []
    for o in cfg_monitor.get("oabs") or []:
        numero = so_digitos(o.get("numero")).lstrip("0")
        if numero:
            oabs.append({"numero": numero, "uf": (o.get("uf") or "").upper().strip(), "nome": o.get("nome", "")})
    partes = {}
    for nome in cfg_monitor.get("partes") or []:
        if cl.chave_nome(nome):
            partes[cl.chave_nome(nome)] = nome
    cnpjs = {}
    if cfg_monitor.get("partes_da_carteira", True):
        por_cnpj, por_nome = cl.ler_carteira(carteira_csv)
        partes.update(por_nome)
        cnpjs.update(por_cnpj)
    return {"oabs": oabs, "processos": ler_processos(processos_csv), "partes": partes, "cnpjs": cnpjs}


# --- Conferência ------------------------------------------------------------

def _oab_bate(adv, alvo):
    if so_digitos(adv.get("oab")).lstrip("0") != alvo["numero"]:
        return False
    uf = (adv.get("uf") or "").upper().strip()
    return not alvo["uf"] or not uf or uf == alvo["uf"]


def _nome_no_texto(chave, texto_chave):
    # Nome curto demais dá falso alarme; só procura no texto nomes com 2+ palavras e 10+ letras.
    return len(chave) >= 10 and " " in chave and f" {chave} " in f" {texto_chave} "


def casar(pub, alvos):
    """Por que esta publicação interessa ao escritório (lista vazia = não interessa)."""
    motivos, cliente, responsavel = [], "", ""
    for alvo in alvos["oabs"]:
        if any(_oab_bate(a, alvo) for a in pub.get("advogados") or []):
            motivos.append(f"OAB {alvo['numero']}/{alvo['uf']}" + (f" ({alvo['nome']})" if alvo["nome"] else ""))
    acomp = alvos["processos"].get(so_digitos(pub.get("processo")))
    if acomp:
        motivos.append("Processo acompanhado")
        cliente, responsavel = acomp["cliente"], acomp["responsavel"]
    nomes = [d.get("nome", "") for d in pub.get("destinatarios") or []] + cl.reclamadas_no_texto(pub.get("texto", ""))
    texto_chave = cl.chave_nome(pub.get("texto", "")[:3000])
    for chave, nome in alvos["partes"].items():
        if any(cl.chave_nome(n) == chave for n in nomes) or _nome_no_texto(chave, texto_chave):
            motivos.append(f"Parte: {nome}")
            cliente = cliente or nome
            break
    for c in cl.extrair_cnpjs(pub.get("texto", "")):
        if c in alvos["cnpjs"]:
            if not cliente:
                motivos.append(f"CNPJ do cliente {alvos['cnpjs'][c]}")
            cliente = cliente or alvos["cnpjs"][c]
            break
    if not motivos and pub.get("_via"):
        # Veio da busca filtrada do próprio DJEN (ex.: nome do cliente escrito de outro jeito).
        motivos.append(f"Busca no DJEN: {pub['_via']}")
        cliente = cliente or pub.get("_cliente", "")
    return motivos, cliente, responsavel


# Ordem importa: a primeira regra que bater define o tipo do ato.
_REGRAS_ATO = [
    (r"bloqueio|penhora|sisbajud|renajud|infojud|constri[cç]", "Penhora / bloqueio", "Urgente"),
    (r"lista de distribui", "Ação nova distribuída", "Urgente"),
    (r"\bcita[cç][aã]o\b|\bcite-se\b", "Citação", "Urgente"),
    (r"\bsenten[cç]a\b|\bjulgo\s+(?:procedente|improcedente|parcialmente)", "Sentença", "Urgente"),
    (r"\bac[oó]rd[aã]o\b", "Acórdão", "Urgente"),
    (r"tutela\s+(?:de\s+urg|antecipad|provis)|\bliminar\b", "Decisão (tutela / liminar)", "Urgente"),
    (r"audi[eê]ncia.{0,80}(?:designad|redesignad|adiad|cancelad|antecipad|remarcad)|"
     r"(?:designo|redesigno|designad[ao]|redesignad[ao]).{0,80}audi[eê]ncia", "Audiência", "Alta"),
    (r"pauta\s+de\s+julgamento|inclu[ií]do\s+em\s+pauta|sess[aã]o\s+de\s+julgamento", "Pauta de julgamento", "Alta"),
    (r"homologo\s+o\s+acordo|acordo\s+homologado", "Acordo homologado", "Alta"),
    (r"alvar[aá]", "Alvará", "Alta"),
    (r"\bdecis[aã]o\b|\bdecido\b", "Decisão", "Alta"),
    (r"\bdespacho\b", "Despacho", "Normal"),
    (r"\bedital\b", "Edital", "Normal"),
]


def classificar_ato(pub):
    base = cl.sem_acento(" ".join([pub.get("tipo_comunicacao", ""), pub.get("tipo_documento", ""),
                                   (pub.get("texto") or "")[:2500]])).lower()
    for padrao, tipo, urgencia in _REGRAS_ATO:
        if re.search(cl.sem_acento(padrao), base):
            return tipo, urgencia
    return (pub.get("tipo_documento") or pub.get("tipo_comunicacao") or "Intimação"), "Normal"


def chave(pub):
    """Identidade da publicação, pelo conteúdo: a mesma publicação vinda da busca ou do caderno
    tem a mesma chave, e o escritório nunca recebe o mesmo aviso duas vezes."""
    texto = re.sub(r"\s+", " ", pub.get("texto") or "").strip()[:1500]
    if not texto:
        return f"id:{pub.get('id')}"
    base = f"{so_digitos(pub.get('processo'))}|{pub.get('data')}|{texto}"
    return "c:" + hashlib.sha256(base.encode("utf-8")).hexdigest()[:32]


def trecho(texto, tamanho=420):
    """Pedaço do texto depois do cabeçalho (onde costuma estar o que o juiz decidiu)."""
    t = re.sub(r"\s+", " ", texto or "").strip()
    t = re.sub(r"^PODER JUDICI[AÁ]RIO.{0,160}?REGI[AÃ]O\s*", "", t)  # cabeçalho padrão dos TRTs
    m = re.search(r"(?:DESPACHO|DECIS[AÃ]O|SENTEN[CÇ]A|INTIMA[CÇ][AÃ]O|NOTIFICA[CÇ][AÃ]O|Vistos|Fica|Ficam|Intime-se)",
                  t)
    if m and m.start() < len(t) - 80:
        t = t[m.start():]
    return t[:tamanho] + ("…" if len(t) > tamanho else "")


def preparar(pub, motivos, cliente, responsavel, feriados_extras=()):
    tipo, urgencia = classificar_ato(pub)
    dias = prazos.prazo_no_texto(pub.get("texto"))
    datas = prazos.calcular(pub.get("data"), dias, feriados_extras)
    if dias and dias <= 5 and urgencia == "Normal":
        urgencia = "Alta"
    return {
        "chave": chave(pub), "data": pub.get("data"), "tribunal": pub.get("tribunal"), "orgao": pub.get("vara"),
        "processo": pub.get("processo"), "classe": pub.get("classe"), "ato": tipo, "urgencia": urgencia,
        "tipo_comunicacao": pub.get("tipo_comunicacao"), "tipo_documento": pub.get("tipo_documento"),
        "publicacao": datas.get("publicacao", ""), "inicio_prazo": datas.get("inicio_prazo", ""),
        "dias_prazo": datas.get("dias_prazo"), "vencimento": datas.get("vencimento", ""),
        "cliente": cliente, "responsavel": responsavel, "motivos": motivos,
        "trecho": trecho(pub.get("texto")), "link": pub.get("link"),
    }


# --- Coleta -----------------------------------------------------------------

def consultas_da_api(alvos, limite):
    """Lista de filtros para a busca da API, dentro do limite de pedidos por rodada."""
    filtros = [({"numeroOab": o["numero"], **({"ufOab": o["uf"]} if o["uf"] else {})},
                f"OAB {o['numero']}/{o['uf']}", "") for o in alvos["oabs"]]
    filtros += [({"nomeParte": nome}, f"parte {nome[:40]}", nome) for nome in alvos["partes"].values()]
    filtros += [({"numeroProcesso": num}, f"processo {p['processo'] or num}", p["cliente"])
                for num, p in alvos["processos"].items()]
    return filtros[:limite], filtros[limite:]


def coletar_api(alvos, inicio, fim, limite, diagnostico=None, aviso=print):
    feitas, sobra = consultas_da_api(alvos, limite)
    if sobra:
        aviso(f"  {len(sobra)} consultas passam do limite desta rodada; ficam para a varredura do caderno (--caderno).")
    pubs = []
    for filtros, rotulo, cliente in feitas:
        try:
            lote = djen.buscar_filtrado(filtros, inicio, fim, diagnostico, aviso, rotulo=rotulo)
        except RuntimeError as e:
            if "HTTP 403" in str(e):
                raise
            aviso(f"  {rotulo}: sem resposta agora ({str(e)[:80]}); fica para a próxima rodada.")
            continue
        for pub in lote:
            pub["_via"], pub["_cliente"] = rotulo, cliente
            pubs.append(pub)
    return pubs


def dias_uteis(hoje, dias):
    """Datas a ler, da mais antiga para a mais nova: hoje (se for dia útil) e os `dias` dias úteis anteriores.
    Assim, no sábado e no domingo lê a sexta, e na segunda de manhã não pula a sexta."""
    datas, d = [], hoje
    if d.weekday() < 5:
        datas.append(d)
    while len([x for x in datas if x != hoje]) < max(0, int(dias)):
        d -= dt.timedelta(days=1)
        if d.weekday() < 5:
            datas.append(d)
    return sorted(datas)


def coletar_caderno(tribunais, dias, banco, diagnostico=None, aviso=print, hoje=None, lidos=None, tentativas=None, parar=None):
    """Cadernos dos últimos dias úteis. Só baixa de novo se o CNJ reprocessou (versão mudou).
    Os cadernos lidos vão para `lidos`; quem marca como conferido é `guardar`, no fim da rodada.
    0.7.13: cada tribunal é uma tentativa à parte (vai para `tentativas`, com a causa); um tribunal com problema não
    derruba os outros. Só levanta erro se nenhum tribunal pôde ser lido (ou se o pedido saiu de fora do Brasil)."""
    from . import causas
    hoje = hoje or dt.date.today()
    pubs = []
    tentativas = tentativas if tentativas is not None else []
    primeiro_erro = None
    # Dias com Diário (0.7.11): volta dia útil a dia útil, até 10, e só conta os dias em que o tribunal publicou o
    # caderno. Assim feriado (nacional, estadual) e recesso não fazem a leitura sair vazia.
    candidatas = dias_uteis(hoje, 10)[::-1]
    for sigla in tribunais:
        contados, motivos, lidos_trib, inicio = 0, {}, [], time.perf_counter()
        pedidas, http, erro = [], "200", None
        try:
            for d in candidatas:
                if parar and parar():  # 0.7.15: "Interromper" pedido: para antes do próximo Diário (ponto seguro)
                    from .radar import Interrompida
                    raise Interrompida("interrompida")
                if d != hoje and contados >= max(0, int(dias)):
                    break
                pedidas.append(d.isoformat())
                meta = djen.meta_caderno(sigla, d.isoformat(), aviso, motivos)
                if meta is None:
                    continue
                if d != hoje:
                    contados += 1
                versao = str(meta.get("versao", ""))
                if versao and banco.versao_caderno(sigla, d.isoformat()) == versao:
                    aviso(f"  Caderno {sigla} {d:%d/%m}: já conferido (versão {versao})")
                    lidos_trib.append(d)
                    continue
                aviso(f"  Baixando o caderno {sigla} {d:%d/%m} (pode levar alguns minutos)...")
                lote = djen.baixar_caderno(sigla, d.isoformat(), diagnostico, aviso, meta=meta)
                if lote is None:
                    continue
                pubs += lote
                lidos_trib.append(d)
                if lidos is not None:
                    lidos.append((sigla, d.isoformat(), versao or "?"))
        except rede.BloqueadoForaDoBrasil:
            raise
        except Exception as e:  # um tribunal com problema não derruba os outros
            if e.__class__.__name__ == "Interrompida":  # 0.7.15: parada pedida; registra e sobe (não é erro do tribunal)
                tentativas.append({"tribunal": sigla, "dias_pedidos": ", ".join(sorted(set(pedidas))), "http": "-", "causa": "interrompida",
                                   "fez": "interrompida a pedido; este Diário é lido de novo na próxima leitura", "fez_en": "stopped on request; this gazette is read again next time",
                                   "duracao": round(time.perf_counter() - inicio, 1), "leu_ate": "", "detalhe": ""})
                raise
            erro = e
            primeiro_erro = primeiro_erro or e
            http = str(getattr(e, "codigo", "") or "-")
            aviso(f"  {sigla}: {causas.mensagem(causas.classificar(e))}")
        causa = causas.classificar(erro) if erro else (
            "ainda_nao_liberado_3h" if hoje.isoformat() in motivos and motivos[hoje.isoformat()] == "ainda_nao_liberado_3h" else "ok")
        if erro is None and causa == "ainda_nao_liberado_3h":
            http = "403"
        ate = max(lidos_trib).strftime("%d/%m") if lidos_trib else ""
        if erro is not None:
            fez = f"parou neste tribunal; leu até {ate}" if ate else "não leu este tribunal; seguiu com os outros"
        elif causa == "ainda_nao_liberado_3h":
            fez = f"pulou hoje (só às 3h); leu até {ate}" if ate else "pulou hoje (só às 3h)"
        else:
            fez = f"leu até {ate}" if ate else "nenhum caderno novo"
        fez_en = (f"stopped on this court; read up to {ate}" if ate else "could not read this court; went on with the others") if erro is not None else (
            (f"skipped today (only after 3 a.m.); read up to {ate}" if ate else "skipped today (only after 3 a.m.)") if causa == "ainda_nao_liberado_3h"
            else (f"read up to {ate}" if ate else "no new gazette"))
        tentativas.append({"tribunal": sigla, "dias_pedidos": ", ".join(sorted(set(pedidas))), "http": http, "causa": causa,
                           "fez": fez, "fez_en": fez_en, "duracao": round(time.perf_counter() - inicio, 1), "leu_ate": ate,
                           "detalhe": f"{erro.__class__.__name__}: {erro}"[:300] if erro else ""})
    if primeiro_erro is not None and all(t["causa"] not in ("ok", "ainda_nao_liberado_3h") for t in tentativas[-len(tribunais):]):
        raise primeiro_erro
    return pubs


def filtrar_novas(pubs, alvos, banco, feriados_extras=()):
    """Só o que interessa ao escritório e ainda não foi avisado (quem grava é `guardar`, depois do aviso).
    Não filtra por tribunal: a OAB e o processo valem em qualquer tribunal (TRT, TST, STF...)."""
    novas, vistas = [], set()
    for pub in pubs:
        k = chave(pub)
        if k in vistas or banco.publicacao_vista(k):
            continue
        motivos, cliente, responsavel = casar(pub, alvos)
        if not motivos:
            continue
        vistas.add(k)
        novas.append(preparar(pub, motivos, cliente, responsavel, feriados_extras))
    ordem = {u: i for i, u in enumerate(URGENCIAS)}
    novas.sort(key=lambda x: (ordem.get(x["urgencia"], 9), x.get("vencimento") or "9999", x.get("data") or ""))
    return novas


def guardar(novas, banco, cadernos_lidos=(), rodada=None, visto_em=None):
    for item in novas:
        if rodada:
            item["rodada"] = rodada
        banco.guardar_publicacao(item["chave"], item, visto_em)
    for sigla, data, versao in cadernos_lidos:
        banco.guardar_caderno(sigla, data, versao)


def rodar(cfg, banco, modo="api", dias=None, diagnostico=None, aviso=print, carteira_csv=None,
          processos_csv=None, publicacoes=None):
    """Uma rodada do monitor. Devolve (novas, situacao, cadernos_lidos)."""
    m = cfg.get("monitor") or {}
    alvos = montar_alvos(m, carteira_csv, processos_csv)
    if not (alvos["oabs"] or alvos["processos"] or alvos["partes"]):
        return [], {"pt": "Nada para acompanhar: preencha as OABs no config.json ou o processos.csv.",
                    "en": "Nothing to watch: fill in the bar numbers in config.json or processos.csv."}, []
    dias = dias if dias is not None else int(m.get("dias_para_tras", 3))
    tribunais = [t.upper() for t in m.get("tribunais") or []]
    hoje = dt.date.today()
    extras = m.get("feriados_extras") or []
    lidos = []
    if publicacoes is not None:  # modo exemplo / testes
        pubs = publicacoes
    elif modo == "caderno":
        pubs = coletar_caderno(tribunais or ["TRT2"], dias, banco, diagnostico, aviso, lidos=lidos)
    else:
        try:
            # Fim da janela alguns dias à frente: a data de disponibilização pode ser o próximo dia útil.
            pubs = coletar_api(alvos, (hoje - dt.timedelta(days=dias)).isoformat(),
                               (hoje + dt.timedelta(days=4)).isoformat(),
                               int(m.get("max_consultas_por_rodada", 30)), diagnostico, aviso)
        except rede.BloqueadoForaDoBrasil:
            raise
        except RuntimeError as e:
            if "HTTP 403" not in str(e) or not tribunais:
                raise
            # Proteção anti-robô na busca filtrada: o caderno do dia continua sendo o caminho oficial.
            aviso("  A busca filtrada foi recusada (HTTP 403). Usando o caderno do dia.")
            pubs = coletar_caderno(tribunais, min(dias, 2), banco, diagnostico, aviso, lidos=lidos)
    novas = filtrar_novas(pubs, alvos, banco, extras)
    urgentes = sum(1 for n in novas if n["urgencia"] == "Urgente")
    situacao = {"pt": f"{len(pubs)} publicações conferidas; {len(novas)} novas para o escritório ({urgentes} urgentes).",
                "en": f"{len(pubs)} notices checked; {len(novas)} new for the firm ({urgentes} urgent).",
                "conferidas": len(pubs)}
    return novas, situacao, lidos


# --- Radar: ações novas nas varas acompanhadas (potenciais clientes) ----------

def varas_alvo(cfg, pasta_orgaos=None):
    """As varas do config.json com o idOrgao (do próprio config ou de orgaos_<TRT>.json, feito por `orgaos`)."""
    saida = []
    for alvo in cfg.get("alvos") or []:
        sigla, vara = str(alvo.get("tribunal", "")).upper(), alvo.get("vara", "")
        orgao_id = str(alvo.get("orgao_id") or "")
        if not orgao_id and pasta_orgaos:
            caminho = os.path.join(pasta_orgaos, f"orgaos_{sigla}.json")
            if os.path.exists(caminho):
                with open(caminho, encoding="utf-8") as f:
                    mapa = json.load(f)
                alvo_chave = cl.sem_acento(vara).lower()
                for nome, ident in mapa.items():
                    if alvo_chave in cl.sem_acento(nome).lower():
                        orgao_id = str(ident)
                        break
        saida.append({"tribunal": sigla, "vara": vara, "orgao_id": orgao_id})
    return saida


def coletar_radar(varas, inicio, fim, diagnostico=None, aviso=print):
    """Publicações das varas acompanhadas no período: uma consulta leve por vara (só texto, só o período)."""
    pubs, sem_id = [], []
    for v in varas:
        if not v["orgao_id"]:
            sem_id.append(v)
            continue
        try:
            lote = djen.buscar(v["tribunal"], inicio, fim, v["orgao_id"], diagnostico, aviso)
        except RuntimeError as e:
            if "HTTP 403" in str(e):
                raise
            aviso(f"  {v['tribunal']} {v['vara']}: sem resposta agora ({str(e)[:80]}); fica para a próxima rodada.")
            continue
        chave_vara = cl.sem_acento(v["vara"]).lower()
        dentro = [p for p in lote if chave_vara in cl.sem_acento(p.get("vara", "")).lower()]
        if lote and not dentro:
            aviso(f"  Atenção: o idOrgao {v['orgao_id']} devolveu outra vara ({lote[0].get('vara')}). Rode `orgaos` de novo.")
        pubs += dentro
    if sem_id:
        aviso("  Sem idOrgao para: " + "; ".join(f"{v['tribunal']} {v['vara']}" for v in sem_id) +
              ". Rode `python lexsuite_robo.py orgaos --tribunal <TRT>` uma vez.")
    return pubs


def acoes_novas(pubs, varas, ja_vistos, ano_minimo):
    """Ações novas contra empresas nas varas acompanhadas (uma por processo)."""
    vistos, saida = set(), []
    for v in varas:
        for n in djen.leads(pubs, vara=v["vara"], ano_minimo=ano_minimo, ja_vistos=ja_vistos):
            if n["processo"] not in vistos:
                vistos.add(n["processo"])
                saida.append(n)
    return saida


def pontuar(leads, carteira_csv=None, hoje=None):
    """Carteira, recorrência (30 dias), porte e nota de um conjunto de ações. Mesma regra no CLI e na página."""
    import collections
    hoje = hoje or dt.date.today()
    lista_clientes = cl.ler_carteira(carteira_csv)
    for l in leads:
        l["cliente"] = cl.cliente_da_carteira(l, lista_clientes)
    limite = (hoje - dt.timedelta(days=30)).isoformat()

    def quando(l):
        return l.get("data_publicacao") or (l.get("audiencia") or {}).get("data") or l.get("primeira_vez") or ""
    contagem = collections.Counter(cl.chave_nome(e) for l in leads if quando(l) >= limite for e in l.get("empresas") or [])
    for l in leads:
        l["acoes_no_periodo"] = max((contagem.get(cl.chave_nome(e), 1) for e in l.get("empresas") or []), default=1)
        l["porte"] = (l.get("empresa_receita") or {}).get("porte", "")
        l["nota"], l["motivos"] = cl.nota(l)
        l["faixa"] = cl.faixa(l["nota"])
    leads.sort(key=lambda l: (l["nota"], quando(l)), reverse=True)
    return leads


# --- A página do dia ----------------------------------------------------------

NOMES_TRT = {
    "TRT1": "Rio de Janeiro", "TRT2": "São Paulo (capital e região)", "TRT3": "Minas Gerais", "TRT4": "Rio Grande do Sul",
    "TRT5": "Bahia", "TRT6": "Pernambuco", "TRT7": "Ceará", "TRT8": "Pará e Amapá", "TRT9": "Paraná",
    "TRT10": "Distrito Federal e Tocantins", "TRT11": "Amazonas e Roraima", "TRT12": "Santa Catarina", "TRT13": "Paraíba",
    "TRT14": "Rondônia e Acre", "TRT15": "São Paulo (interior)", "TRT16": "Maranhão", "TRT17": "Espírito Santo",
    "TRT18": "Goiás", "TRT19": "Alagoas", "TRT20": "Sergipe", "TRT21": "Rio Grande do Norte", "TRT22": "Piauí",
    "TRT23": "Mato Grosso", "TRT24": "Mato Grosso do Sul", "TST": "Tribunal Superior do Trabalho",
}


def sinais_das_acoes(acoes):
    """Sinais que fazem uma ação valer o olhar (calculados sobre o conjunto do período)."""
    tribunais_por_empresa = {}
    for a in acoes:
        for e in a.get("empresas") or []:
            tribunais_por_empresa.setdefault(cl.chave_nome(e), set()).add(a.get("tribunal"))
    for a in acoes:
        s = []
        if a.get("cliente"):
            s.append("Cliente da carteira")
        n = int(a.get("acoes_no_periodo") or 1)
        if n >= 2:
            s.append(f"{n} ações no período")
        tribs = max((len(tribunais_por_empresa.get(cl.chave_nome(e), ())) for e in a.get("empresas") or []), default=0)
        if tribs >= 2:
            s.append(f"Em {tribs} tribunais")
        if len(a.get("empresas") or []) >= 2:
            s.append("Terceirização")
        a["sinais"] = s
        a["setor"] = cl.setor(a.get("empresas") or [])
    return acoes


def montar_pagina(cfg, banco, dias=7, exemplo=False, situacao=None, agora=None, escritorio="", carteira_csv=None):
    """Tudo o que a página do dia precisa: rodadas, publicações dos nossos processos e ações novas."""
    from . import saidas
    agora = agora or dt.datetime.now()
    desde = (agora.date() - dt.timedelta(days=dias)).isoformat()
    rodadas = sorted(banco.rodadas(desde), key=lambda r: r["quando"])
    processos = banco.publicacoes_desde(desde)
    # A nota considera os últimos 30 dias (recorrência), mesmo que a página mostre menos dias.
    todos = [l for l in banco.todos_leads(desde=(agora.date() - dt.timedelta(days=30)).isoformat())
             if l.get("fonte", "DJEN") == "DJEN"]
    pontuar(todos, carteira_csv, agora.date())
    acoes = []
    for l in todos:
        if (l.get("primeira_vez") or "") < desde:
            continue
        item = saidas.lead_para_saida(l)
        item.update({"chave": l.get("processo"), "rodada": l.get("rodada", ""), "visto_em": l.get("visto_em", ""),
                     "primeira_vez": l.get("primeira_vez", ""), "classe": l.get("classe", "")})
        acoes.append(item)
    sinais_das_acoes(acoes)
    acoes.sort(key=lambda a: (a.get("visto_em") or a.get("primeira_vez") or ""), reverse=True)
    tribunais = {}
    for v in varas_alvo(cfg):
        t = tribunais.setdefault(v["tribunal"], {"sigla": v["tribunal"], "nome": NOMES_TRT.get(v["tribunal"], v["tribunal"]),
                                                 "varas": []})
        if v["vara"] and v["vara"] not in t["varas"]:
            t["varas"].append(v["vara"])
    for a in acoes + processos:
        sg = a.get("tribunal")
        if sg and sg not in tribunais:
            tribunais[sg] = {"sigla": sg, "nome": NOMES_TRT.get(sg, sg), "varas": []}
    # O "dia" da página é o dia do Diário (data de disponibilização mais recente), não o dia em que o robô rodou.
    datas = [a.get("data_publicacao") or "" for a in acoes] + [p.get("data") or "" for p in processos]
    dia = max([d for d in datas if d] or [agora.date().isoformat()])
    return {
        "gerado_em": agora.strftime("%Y-%m-%d %H:%M"), "dia": dia,
        "exemplo": bool(exemplo), "escritorio": escritorio, "situacao": situacao or {},
        "tribunais": list(tribunais.values()), "rodadas": rodadas, "processos": processos, "acoes": acoes,
    }
