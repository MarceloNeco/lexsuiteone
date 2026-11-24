"""Radar SP: a lista do dia de ações novas contra empresas, qualificada sem IA.

Para cada tribunal do config (ex.: TRT2 e TRT15) o robô lê a lista de distribuição do dia
no DJEN, fica só com as ações contra pessoa jurídica, consulta a Receita quando há CNPJ e
monta uma linha por ação: empresa, porte, setor, cidade, valor (quando publicado ou digitado
por uma pessoa), vara e hora. O valor da causa que o Diário não traz fica atrás do captcha
do PJe: a página tem o botão "Abrir no PJe" e o campo para a pessoa digitar.
"""

import collections
import datetime as dt
import json
import os
import re
import threading
import time

from . import classificar as cl
from . import cnpj as receita
from . import compartilhar, config, conta, djen, monitor, prazos, preferencias, saidas, saude, tribunais


class Interrompida(Exception):
    """Alguém clicou em "Interromper": a leitura parou num ponto seguro (0.7.15). O que já foi gravado fica; o Diário
    interrompido não é marcado como lido, e a próxima leitura baixa de novo os Diários desta leitura."""


class RoboDesligado(Exception):
    """O suporte desligou o robô, a validade acabou ou a versão instalada é velha demais (aba Controle)."""
GRANDES_GRUPOS = [  # nomes que quase sempre têm jurídico próprio (ficam no fim da lista, não somem)
    "MERCADO LIVRE", "MERCADOLIVRE", "AMAZON", "MAGAZINE LUIZA", "MAGALU", "AMERICANAS", "CARREFOUR", "ATACADAO",
    "GRUPO PAO DE ACUCAR", "COMPANHIA BRASILEIRA DE DISTRIBUICAO", "ASSAI", "VIA VAREJO", "CASAS BAHIA", "SHOPEE",
    "ITAU", "BRADESCO", "SANTANDER", "BANCO DO BRASIL", "CAIXA ECONOMICA", "VALE S", "PETROBRAS", "AMBEV",
    "JBS", "BRF", "GERDAU", "VIVO", "TELEFONICA", "CLARO", "TIM S", "NATURA", "RAIA DROGASIL", "LOCALIZA",
    "UBER", "IFOOD", "99 TECNOLOGIA", "CORREIOS", "GOL LINHAS", "LATAM", "AZUL LINHAS",
]



def sinal_guardado(lead):
    """0.7.35 (dono): ações guardadas antes de o programa anotar o sinal (até a 0.7.18) ganham o sinal pelo texto que ficou
    guardado, na hora de mostrar (o banco não muda). Sem texto que mostre o sinal: '' (a tela mostra "Sem sinal registrado")."""
    from . import classificar as cl
    tipo = cl.sem_acento(str(lead.get("tipo") or "")).lower()
    texto = cl.sem_acento(str(lead.get("texto_curto") or "")).lower()
    # revisão da 0.7.35: na lista de distribuição o DJEN guarda o tipo do documento ("Notificação"); o aviso está no texto
    # ("Processo distribuído"), como em banco._reclassificar_0718
    if "distribui" in tipo or "processo distribuid" in texto or "lista de distribuic" in texto:
        return "lista de distribuição"
    return cl.sinal_inicio(lead.get("texto_curto") or "")

def link_pje(tribunal):
    return tribunais.link_pje(tribunal)


def gigante(empresa, nomes, teto_capital):
    """Empresa com jurídico próprio quase certo: capital social acima do teto ou nome de grande grupo."""
    capital = float((empresa or {}).get("capital_social") or 0)
    if teto_capital and capital >= teto_capital:
        return True
    chave = " " + cl.sem_acento(" ".join(nomes or [])).upper() + " "
    return any(g in chave for g in GRANDES_GRUPOS)


def porte_legivel(porte):
    p = cl.sem_acento(str(porte or "")).upper()
    if "MICRO" in p or p == "ME":
        return "Microempresa (até R$ 360 mil/ano)"
    if "PEQUENO" in p or p == "EPP":
        return "Pequena (até R$ 4,8 milhões/ano)"
    if p.startswith("DEMAIS"):
        return "Média ou grande (acima de R$ 4,8 milhões/ano)"
    return ""


def _contato_resumo(emp, extras, temcnpj, a_conferir):
    """Selo de contato do cartão: {tem, canais, motivo}. Motivo quando falta: sem_cnpj (o Diário não trouxe o CNPJ),
    cnpj_a_conferir, receita_sem (a Receita não tem telefone nem e-mail) ."""
    canais = sorted({c["canal"] for c in extras} | ({"telefone"} if emp.get("telefone") else set()) | ({"email"} if emp.get("email") else set()))
    if canais:
        return {"tem": True, "canais": canais, "motivo": ""}
    return {"tem": False, "canais": [], "motivo": "cnpj_a_conferir" if a_conferir and not temcnpj else ("receita_sem" if temcnpj else "sem_cnpj")}


def item_de_lead(lead, cfg_radar, contatos=None):
    """Uma linha da lista do dia a partir de um lead do DJEN (só o que pode sair; nenhuma pessoa física do processo)."""
    emp = lead.get("empresa_receita") or {}
    nomes = [cl.limpar_nome(x) for x in (lead.get("empresas") or [])]  # 0.7.11: sem "Intimação" no fim (vale para o já guardado)
    a_conferir = lead.get("cnpj_a_conferir") or ""
    nomes_rf = [x for x in (emp.get("razao_social") or "", emp.get("nome_fantasia") or "") if x]
    if emp and nomes and nomes_rf and not any(cl.nomes_batem(x, e) for x in nomes_rf for e in nomes):
        a_conferir, emp = emp.get("cnpj") or a_conferir, {}  # ficha de outra parte (guardada antes da 0.7.11): não mostra
    if not emp and not a_conferir:
        a_conferir = (lead.get("cnpjs") or [""])[0]
    teto = float(cfg_radar.get("teto_capital_gigante") or 0)
    from . import banco as _bd
    extras = [c for c in (contatos or {}).get(lead.get("processo"), []) if c.get("validacao") != "descartado"]
    extras.sort(key=lambda c: {"alta": 0, "media": 1, "baixa": 2}.get(c.get("confianca") or "media", 1))  # 0.7.45: o cadastro da parte primeiro
    return {
        "situacao": _bd.situacao_valida(lead.get("status")) or "novo", "motivo": lead.get("motivo") or "",
        "situacao_em": lead.get("status_em") or "", "frente": lead.get("frente") or "trabalhista",
        "resumido": bool(lead.get("resumido")), "primeira_vez": lead.get("primeira_vez") or "",
        "status_por": lead.get("status_por") or "", "status_em": lead.get("status_em") or "",  # 0.7.53 (decisão 65)
        "visto_por": lead.get("visto_por") or "", "visto_em": lead.get("visto_em") or "",
        "contato": _contato_resumo(emp, extras, bool(emp.get("cnpj")), a_conferir),
        "contatos": [{k: c[k] for k in ("canal", "valor", "fonte", "data", "confianca", "origem", "de_pessoa", "validacao")} for c in extras],
        "cnpj_a_conferir": a_conferir,
        "cnpj_inferido": lead.get("cnpj_inferido") or "",  # 0.7.50: CNPJ confirmado pelo escritório a partir de outros processos com o mesmo nome
        "id": lead.get("processo"),
        "hora": (lead.get("visto_em") or "")[11:16],
        "visto_em": lead.get("visto_em") or "",
        "rodada": lead.get("rodada") or "",  # 0.7.48: "Ver os N processos" (novos desta leitura)
        "fonte_leitura": lead.get("fonte_leitura") or "caderno", "caderno_pendente": bool(lead.get("caderno_pendente")),
        "tribunal": lead.get("tribunal"),
        "vara": lead.get("vara"),
        "sinal": lead.get("sinal") or sinal_guardado(lead),  # 0.7.19: como a ação nova foi reconhecida (gráfico para calibrar a regra com o escritório)
        "processo": lead.get("processo"),
        "classe": (lead.get("classe") or "").upper(),  # 0.7.16: o Diário às vezes traz "AçãO ... ORDINáRIO"
        "rito": lead.get("rito"),
        "distribuida_em": lead.get("ajuizada_em") or lead.get("data_publicacao") or "",
        # 0.7.51 (desenho das datas e fontes): ajuizamento (CNJ, Diário ou digitado), jornada e publicações; nada de partes
        "ajuizado": data_de_referencia(lead)[0], "ajuizado_fonte": data_de_referencia(lead)[1],
        "cnj": {k: v for k, v in (lead.get("cnj") or {}).items() if k in ("ajuizado", "classe", "assuntos", "orgao", "marcos", "pub1", "pubN",
                                                                           "dias_publicacao", "andamento", "atualizado_em")},
        "diario_hist": {k: v for k, v in (lead.get("diario_hist") or {}).items() if k in ("pub1", "pubN", "dias", "distribuicao", "consultado_em")},
        "diario_em": lead.get("data_publicacao") or "",
        "ajuizada_em": ((lead.get("manual") or {}).get("data_ajuizamento") or {}).get("valor") or lead.get("ajuizada_em") or "",
        "empresas": nomes,
        "empresa": {
            "cnpj": emp.get("cnpj") or "",
            "razao_social": emp.get("razao_social") or (nomes[0] if nomes else ""),
            "nome_fantasia": emp.get("nome_fantasia") or "",
            "porte": emp.get("porte") or "", "porte_legivel": porte_legivel(emp.get("porte")),
            "capital_social": emp.get("capital_social") or 0,
            "cnae": emp.get("cnae") or "", "atividade": emp.get("atividade") or "",
            "cnaes_secundarios": emp.get("cnaes_secundarios") or [],
            "municipio": emp.get("municipio") or "",
            "uf": emp.get("uf") or ((lead.get("manual") or {}).get("uf") or {}).get("valor") or "",  # 0.7.18: da área logada
            "telefone": emp.get("telefone") or "", "telefone2": emp.get("telefone2") or "", "email": emp.get("email") or "",
            "socios": emp.get("socios") or [], "simples": emp.get("simples"),
            "inicio_atividade": emp.get("inicio_atividade") or "",
            "logradouro": emp.get("logradouro") or "", "numero": emp.get("numero") or "", "complemento": emp.get("complemento") or "",
            "bairro": emp.get("bairro") or "", "cep": emp.get("cep") or "",
        },
        "setor": cl.setor(nomes if not emp.get("atividade") else [emp.get("atividade", "")] + nomes),
        "gigante": gigante(emp, nomes, teto),
        # 0.7.16: valor digitado no cartão ou trazido da área logada fica no programa (vale em outra tela e na planilha)
        "valor_causa": ((lead.get("manual") or {}).get("valor_causa") or {}).get("valor") or lead.get("valor_causa"),
        "valor_fonte": ((lead.get("manual") or {}).get("valor_causa") or {}).get("fonte") or ("djen" if lead.get("valor_causa") else ""),
        "link_djen": lead.get("link") or "",
        "link_pje": link_pje(lead.get("tribunal")),
    }


def inicio_periodo(hoje, dias):
    """0.7.30 (dono): primeiro dia do período pela data do processo. 1 = "do último dia útil até agora" (numa segunda,
    a sexta; num dia comum, ontem); N = os últimos N dias corridos."""
    if int(dias) <= 1:
        # revisão da 0.7.30: pula também feriado nacional (Finados, Consciência Negra, Carnaval...), pela mesma tabela
        # dos prazos; no máximo 7 dias para trás (no recesso de fim de ano não se volta até 19/12)
        d = hoje - dt.timedelta(days=1)
        for _ in range(6):
            if prazos.dia_util(d):
                break
            d -= dt.timedelta(days=1)
        return d.isoformat()
    return (hoje - dt.timedelta(days=int(dias))).isoformat()


PRAZOS_LIMPEZA = {"resumir_meses": (6, 1, 120), "apagar_meses": (24, 0, 240)}  # padrão, mínimo, máximo (0 = nunca apagar)


def prazos_limpeza(r):
    """(resumir, apagar) do config.radar, com as regras: resumir >= 1; apagar 0 (nunca) ou >= 6 e >= resumir."""
    resumir = config.inteiro(r.get("resumir_meses", 6), 6, 1, 120)
    apagar = config.inteiro(r.get("apagar_meses", 24), 24, 0, 240)
    if apagar:
        apagar = max(apagar, 6, resumir)
    return resumir, apagar


def limpar_banco(banco, r, origem):
    """0.7.48: a limpeza com os prazos do config, registrada no Histórico de leituras (tipo "limpeza")."""
    resumir, apagar = prazos_limpeza(r or {})
    lp = banco.limpeza_automatica(resumir, apagar)
    banco.registrar("limpeza", dict(lp, origem=origem, quando_local=dt.datetime.now().astimezone().isoformat(timespec="seconds")))
    return lp


def itens_de(cfg, banco, processos):
    """0.7.48 (teste do dono, 15/Nov: "Gerar o pedido" demorava com 2 ou com 41 processos): só os itens destes processos,
    sem remontar o Arquivo inteiro. Devolve {processo: item} com o que a área logada precisa (valor, datas, contatos)."""
    r = cfg.get("radar") or {}
    lista = [str(p) for p in processos]
    por_processo = {}
    for c in (banco.contatos() if len(lista) > 300 else banco.contatos_de(lista)):
        por_processo.setdefault(c["processo"], []).append(c)
    saida = {}
    for lead in banco.todos_leads(processos=lista):
        item = item_de_lead(lead, r, por_processo)
        saida[item["processo"]] = item
    return saida


def montar_radar(cfg, banco, agora=None, exemplo=False, situacao=None, dias=None, prefs=None, visao="lista"):
    """Os dados da página: as ações guardadas nos últimos `dias` dias, dos tribunais escolhidos no config,
    com as preferências do escritório aplicadas (exclusões e mínimo de ações marcam, não apagam).
    0.7.14: visao="lista" esconde as arquivadas; visao="arquivo" traz tudo o que o RADAR já leu, de qualquer tribunal."""
    r = cfg.get("radar") or {}
    agora = agora or dt.datetime.now()
    dias = config.inteiro(dias if dias is not None else r.get("dias_na_pagina", 1), 1, 1, 90)  # 0.7.26: config escrito à mão
    desde = inicio_periodo(agora.date(), dias)  # 0.7.30 (dono): pela DATA DO PROCESSO no Diário, não por quando o programa o leu
    escolhidos = tribunais.validar(r.get("tribunais") or ["TRT2", "TRT15"])
    # 0.7.33: critérios desta pessoa, por área (criterios.json); `prefs` passado vale para todas as áreas (testes)
    base_c = compartilhar.pasta_base(cfg)
    por_area = {}
    def prefs_de(area):
        if prefs is not None:
            return prefs
        if area not in por_area:
            por_area[area] = preferencias.carregar(base_c, frente=area, banco=banco, cfg_radar=cfg.get("radar"))
        return por_area[area]
    p_trab = prefs_de("trabalhista")
    r = dict(r, teto_capital_gigante=p_trab.get("teto_capital_gigante") or r.get("teto_capital_gigante"))
    itens = []
    arquivo = visao == "arquivo"
    por_processo = {}
    for c in banco.contatos():
        por_processo.setdefault(c["processo"], []).append(c)
    area = banco.area_por_processo() if hasattr(banco, "area_por_processo") else {}  # 0.7.46: memória da área logada
    for lead in banco.todos_leads(desde_diario=None if arquivo else desde):
        if lead.get("fonte", "DJEN") != "DJEN":
            continue
        if cl.segundo_grau(lead.get("vara")) and (lead.get("status") or "novo") == "novo" and not lead.get("manual") \
                and not por_processo.get(lead.get("processo")):  # 0.7.17: turma (não é ação nova); trabalhado fica (revisão da 0.7.18)
            continue
        if not arquivo and ((lead.get("tribunal") or "").upper() not in escolhidos or lead.get("status") == "arquivado"):
            continue
        p_item = prefs_de(lead.get("frente") or "trabalhista")
        item = item_de_lead(lead, dict(r, teto_capital_gigante=p_item.get("teto_capital_gigante") or r.get("teto_capital_gigante")), por_processo)
        if not p_item.get("mostrar_socios", True):
            item["empresa"]["socios"] = []  # minimização: nomes de pessoas só se o escritório pedir
        # revisão da 0.7.33: esconder excluídas e jurídico próprio valem pela área de cada ação
        item["area"] = area.get(lead.get("processo")) or {}  # 0.7.46: {estado: com_dados|tentar|nada|pedido, em}
        item["novo"] = processo_novo(lead, agora.date(), p_item.get("dias_processo_novo") or 30)  # 0.7.51: True, False (antigo) ou None
        item["dias_novo"] = int(p_item.get("dias_processo_novo") or 30)
        item["esconder_exc"] = bool(p_item.get("esconder_excluidas", True))
        item["esconder_gig"] = bool(p_item.get("esconder_gigantes"))
        itens.append(item)
    # Quantas ações cada empresa teve na janela do "mínimo de ações" (conta processos distintos).
    grupos = collections.defaultdict(list)
    for it in itens:
        grupos[it.get("frente") or "trabalhista"].append(it)
    for area, itens_a in grupos.items():
        p_a = prefs_de(area)
        contagem = None
        if int(p_a.get("minimo_acoes") or 1) > 1:
            janela = (agora.date() - dt.timedelta(days=int(p_a.get("janela_dias") or 30))).isoformat()
            vistos = collections.defaultdict(set)
            for lead in banco.todos_leads(desde=janela):
                for nome in lead.get("empresas") or []:
                    vistos[cl.chave_nome(nome)].add(lead.get("processo"))
            contagem = {k: len(v) for k, v in vistos.items()}
        preferencias.aplicar(itens_a, p_a, contagem)
    fts = banco.fontes_de([i["processo"] for i in itens]) if hasattr(banco, "fontes_de") else {}  # 0.7.51: estado do CNJ e do histórico
    for it in itens:
        it["fontes"] = {f: {k: e.get(k) for k in ("estado", "causa", "ultima_em", "ok_em")} for f, e in (fts.get(it["processo"]) or {}).items()}
    itens.sort(key=lambda i: (-(i["valor_causa"] or 0), i["visto_em"]))
    dia = max([i["distribuida_em"][:10] for i in itens if i["distribuida_em"]] or [agora.date().isoformat()])
    return {
        "dia": dia, "gerado_em": agora.strftime("%Y-%m-%d %H:%M"), "exemplo": bool(exemplo), "dias": dias, "desde": str(desde)[:10],  # 0.7.50: início do período (anterior × fora dos filtros)
        "escritorio": cfg.get("escritorio", ""), "tribunais": escolhidos, "visao": visao,
        "valor_minimo": float(p_trab.get("valor_minimo") or 0),  # 0.7.33: 0 = sem mínimo
        "valor_minimo_area": {a: float(prefs_de(a).get("valor_minimo") or 0) for a in sorted(set(grupos) | {"trabalhista"})},
        "situacao": situacao or {}, "itens": itens,
        "excluidas": sum(1 for i in itens if i.get("excluida")),
        "prefs": {"esconder_excluidas": bool(p_trab.get("esconder_excluidas", True)),
                  "esconder_gigantes": any(bool(prefs_de(a).get("esconder_gigantes")) for a in sorted(set(grupos) | {"trabalhista"})),
                  "minimo_acoes": int(p_trab.get("minimo_acoes") or 1), "janela_dias": int(p_trab.get("janela_dias") or 30),
                  "origem": p_trab.get("origem", "padrão"), "erro": p_trab.get("erro", ""), "controle": p_trab.get("controle") or {}},
    }


def _antivirus(pasta_base):
    """0.7.47: o nome do antivírus deste computador (lido uma vez por dia pela tela), ou ""."""
    from . import computador
    try:
        return computador.principal(computador.guardado(pasta_base)) if pasta_base else ""
    except Exception:  # noqa: BLE001
        return ""


def registrar_tentativas(banco, tentativas, origem, versao, quando=None):
    """Histórico de leituras (0.7.13): uma linha por tribunal, com a hora local e o fuso, a origem, o que foi pedido,
    a resposta, a causa e o que o programa fez. Sem dado pessoal."""
    quando = quando or dt.datetime.now().astimezone().isoformat(timespec="seconds")
    for t in tentativas:
        banco.registrar("tentativa", dict(t, quando_local=quando, origem=origem, versao=versao))


PERIODOS = ("desde_ultima", "7dias", "ultimo_util")  # 0.7.51: período de cada leitura (faixa da mira e Rotina de leitura)


def ultima_leitura_ok(banco):
    """Data (AAAA-MM-DD) da última leitura do Diário que terminou bem (ou leu publicações); "" se nunca leu."""
    try:
        for x in banco.execucoes("radar", 30):
            if x.get("resultado") == "ok" or x.get("lidas"):
                return str(x.get("quando") or "")[:10]
    except Exception:  # noqa: BLE001 - sem histórico, vale o último dia útil
        pass
    return ""


def primeira_leitura(banco):
    """0.7.51 (dono, item 18): dia (AAAA-MM-DD) da primeira leitura do Diário neste computador; a Lista só tem processos daí em diante."""
    try:
        row = banco.con.execute("SELECT MIN(quando) FROM execucoes WHERE tipo = 'radar'").fetchone()
        return str((row or [""])[0] or "")[:10]
    except Exception:  # noqa: BLE001 - só texto da tela
        return ""


def dias_do_periodo(periodo, banco, hoje):
    """0.7.51: quantos dias úteis para trás a leitura volta (1 a 10; o programa só baixa o Diário que ainda não leu).
    - "ultimo_util": do último dia útil até hoje (1);
    - "7dias": os dias úteis dos últimos 7 dias (normalmente 5);
    - "desde_ultima": desde o dia da última leitura que deu certo (inclusive, porque o Diário daquele dia pode ter sido
      lido antes de terminar); sem leitura anterior, 1. Computador desligado 3 dias não perde os dias do meio."""
    if periodo == "7dias":
        return max(1, min(10, sum(1 for k in range(1, 8) if (hoje - dt.timedelta(days=k)).weekday() < 5)))
    if periodo == "desde_ultima":
        ult = ultima_leitura_ok(banco)
        try:
            d0 = dt.date.fromisoformat(ult)
        except ValueError:
            return 1
        n = sum(1 for k in range(1, (hoje - d0).days + 1) if (hoje - dt.timedelta(days=k)).weekday() < 5)
        return max(1, min(10, n))
    return 1


def executar(cfg, banco, aviso=print, pasta_base=None, dias=None, sem_cnpj=False, pasta_diag=None, agora=None, versao="",
             caminho_config=None, origem="botão", parar=None):
    """Uma rodada do radar: confere o controle do escritório, baixa o caderno de cada tribunal escolhido, separa as
    ações novas contra empresa, consulta a Receita quando há CNPJ, guarda, avalia a saúde, registra no log e grava
    a saída local e a planilha compartilhada. Devolve a situação. Pode levantar RoboDesligado e rede.BloqueadoForaDoBrasil."""
    versao = versao or _versao()
    r = cfg.get("radar") or {}
    escolhidos = tribunais.validar(r.get("tribunais") or ["TRT2", "TRT15"])
    agora = agora or dt.datetime.now()
    if dias is None:  # 0.7.51 (dono, itens 22 e 26): o período escolhido na faixa (botão) ou na Rotina de leitura (automática)
        automatica = origem != "botão" and not str(origem).startswith("à mão")
        per_ = r.get("periodo_rotina" if automatica else "periodo_botao")
        if per_ in PERIODOS:
            dias = dias_do_periodo(per_, banco, agora.date())
    dias = config.inteiro(dias if dias is not None else r.get("dias_para_tras", 1), 1, 0, 10)
    inicio = time.perf_counter()
    base_compartilhada = compartilhar.pasta_base(cfg)
    if base_compartilhada:
        try:
            compartilhar.criar_se_faltar(cfg, versao, pasta_base or "", aviso)
        except OSError as e:
            aviso(f"  Não consegui criar a planilha ({e.__class__.__name__}); sigo com o padrão.")
    prefs = preferencias.carregar(base_compartilhada, banco=banco, cfg_radar=r)
    if prefs.get("erro"):
        aviso("  " + prefs["erro"])
    # Licença: pergunta à SolverONE e guarda a resposta; depois, o controle da planilha (aba Controle).
    try:
        tabela_retorno = banco.retorno()
    except Exception:  # noqa: BLE001 - o retorno nunca impede a leitura
        tabela_retorno = []
    conta.verificar(cfg, versao, agora.date(), retorno=tabela_retorno)
    if tabela_retorno and (cfg.get("conta") or {}).get("resposta") not in ("sem_resposta", "sem_codigo", "codigo_invalido"):
        banco.registrar("retorno", {"quando_local": agora.astimezone().isoformat(timespec="seconds"), "linhas": tabela_retorno,
                                    "resposta": (cfg.get("conta") or {}).get("retorno_resposta") or {}})
    if caminho_config:
        try:
            config.salvar(caminho_config, cfg)
        except OSError:
            pass
    motivo = conta.bloqueio(cfg, agora.date()) or preferencias.bloqueio(prefs, versao, agora.date())
    if motivo:
        banco.registrar("radar", {"versao": versao, "tribunais": escolhidos, "resultado": "não rodou", "erro": motivo})
        raise RoboDesligado(motivo)
    rodada_id = agora.strftime("%Y-%m-%dT%H:%M")
    aviso(f"Radar: lista de distribuição de {', '.join(escolhidos)} (últimos {dias} dia(s) úteis)")
    registro = {"versao": versao, "tribunais": escolhidos, "lidas": 0, "novas": 0, "com_cnpj": 0, "duracao": 0, "resultado": "", "erro": ""}
    tentativas = []
    # 0.7.48 (decisão 37): leitura pela consulta pública quando o caderno cai; ligada por padrão (Configurações → Leitura do Diário)
    consulta = {"fora": lambda: conta.consulta_fora(cfg, versao)} if r.get("consulta_publica", True) else None
    try:
        lidos = []
        try:
            pubs = monitor.coletar_caderno(escolhidos, dias, banco, pasta_diag, aviso, lidos=lidos, tentativas=tentativas, parar=parar,
                                           consulta=consulta)
        finally:
            try:
                registrar_tentativas(banco, tentativas, origem, versao)
            except Exception as e:  # noqa: BLE001 - o histórico nunca esconde o erro da leitura
                aviso(f"  Não consegui gravar o histórico de leituras ({e.__class__.__name__}).")
        ano_min = agora.year - 1 if agora.month <= 2 else agora.year
        if not banco.execucoes("criterio", 1):  # 0.7.17: data em que o critério de "ação nova" mudou (estatísticas antes e depois não se comparam)
            banco.registrar("criterio", {"desde": CRITERIO_DESDE, "versao": versao or _versao(), "regra": CRITERIO_REGRA})
        novos = acoes_do_dia(pubs, ano_min, banco.processos_vistos())
        lidos_c = (consulta or {}).get("lidos") or []
        procs_c = set().union(*[x["processos"] for x in lidos_c]) if lidos_c else set()
        for n in novos:  # 0.7.48: o que veio pela consulta pública fica marcado até o caderno conferir
            if n.get("processo") in procs_c:
                n["fonte_leitura"], n["caderno_pendente"] = "consulta", True
        if novos:  # 0.7.16: quantas entraram por cada sinal, para conferir a regra de "ação nova" com o escritório
            por_sinal = {}
            for n in novos:
                por_sinal[n.get("sinal") or "outro"] = por_sinal.get(n.get("sinal") or "outro", 0) + 1
            aviso("  Processos novos por sinal: " + "; ".join(f"{k}: {v}" for k, v in sorted(por_sinal.items(), key=lambda x: -x[1])) + ".")
        consultar = bool(r.get("receita", True)) and not sem_cnpj
        com_cnpj = sum(1 for n in novos if n.get("cnpjs"))
        if consultar and com_cnpj:
            aviso(f"  Consultando a Receita para {com_cnpj} empresa(s) com CNPJ no Diário...")
        feitas = falhas = 0
        interrompida = False
        todos_novos, novos_feitos = novos, []
        for n in todos_novos:
            if parar and parar():  # 0.7.15: para aqui; o que já foi gravado entra na contagem, nas estatísticas e na planilha
                interrompida = True
                aviso("  Leitura interrompida a pedido: fecho a rodada com o que já foi gravado.")
                break
            novos_feitos.append(n)
            n["rodada"], n["visto_em"] = rodada_id, agora.isoformat(timespec="seconds")
            if consultar and n.get("cnpjs"):
                # 0.7.11: o CNPJ só vale para a ficha se o nome na Receita bater com o da empresa processada (o texto
                # do Diário pode trazer o CNPJ de outra parte). Sem bater, fica "CNPJ a conferir".
                dados, respondeu = None, False
                for c in n["cnpjs"][:3]:
                    d = receita.consultar(c, banco)
                    feitas += 1
                    if not d:
                        continue
                    respondeu = True
                    if d.get("situacao") == "fonte_sem_suporte":
                        # 0.7.33: CNPJ novo (com letras) que as fontes públicas ainda não têm: fica o CNPJ, sem os dados
                        if len(n["cnpjs"]) == 1:
                            dados = d
                            break
                        continue
                    nomes_rf = [d.get("razao_social") or "", d.get("nome_fantasia") or ""]
                    if any(cl.nomes_batem(x, e) for x in nomes_rf if x for e in n.get("empresas") or []):
                        dados = d
                        break
                    n.setdefault("cnpj_a_conferir", c)
                if dados:
                    n["empresa_receita"] = dados
                    n.pop("cnpj_a_conferir", None)
                elif not respondeu:
                    falhas += 1  # falha é a Receita não responder; nome que não bate não é falha de consulta
                if feitas % 25 == 0:
                    aviso(f"  Receita: {feitas} de {com_cnpj}")
            banco.guardar_lead(n, agora.date().isoformat())
        novos = novos_feitos
        if not interrompida and r.get("fontes_publicas", True):  # 0.7.51 (decisão do dono): cada leitura completa com o CNJ e o histórico do Diário
            try:
                registro["fontes"] = completar_fontes(banco, agora, [n.get("processo") for n in novos], aviso, parar=parar)
            except Exception as e:  # noqa: BLE001 - as fontes extras nunca derrubam a leitura do Diário
                aviso(f"  Fontes públicas: não completei agora ({e.__class__.__name__}); a próxima leitura tenta de novo.")
        info_consulta = registrar_consulta(banco, consulta, novos, agora, origem) if not interrompida else {}
        if not interrompida:  # Diário interrompido não fica marcado como lido: a próxima leitura baixa de novo os Diários desta leitura
            monitor.guardar([], banco, lidos)
        detalhes = {}
        for n in novos:
            detalhes.setdefault(n.get("tribunal") or "?", {"processos": 0, "acoes": 0})["acoes"] += 1
        banco.registrar_rodada({"id": rodada_id, "quando": agora.isoformat(timespec="minutes"), "modo": "caderno",
                                "conferidas": len(pubs), "novas_processos": 0, "novas_acoes": len(novos), "detalhes": detalhes})
        if not interrompida:  # contagem parcial não serve para avaliar a saúde das fontes (daria falso alarme)
            ja = ja_conferidos_para_saude(tentativas)
            saude.registrar(banco, saude.avaliar(pubs, novos, feitas, falhas, agora.date(), ja_conferidos=ja), aviso)
        registro.update({"lidas": len(pubs), "novas": len(novos), "com_cnpj": com_cnpj, "resultado": "interrompida" if interrompida else "ok"})
        if interrompida:
            registro["causa"] = "interrompida"
        if tentativas and not pubs and not interrompida and all(t["causa"] in ("ok", "ainda_nao_liberado_3h", "nao_publicado") for t in tentativas):
            registro["nada_novo"] = True  # 0.7.36 (revisão 2): a tela, depois de reiniciar, só diz "Nada novo" quando a leitura marcou
    except Exception as e:
        from . import causas
        registro.update({"resultado": "interrompida" if isinstance(e, Interrompida) else "erro", "erro": f"{e.__class__.__name__}: {e}"[:300], "causa": causas.classificar(e),
                         "duracao": round(time.perf_counter() - inicio)})
        banco.registrar("radar", registro)
        raise
    registro["duracao"] = round(time.perf_counter() - inicio)
    banco.registrar("radar", registro)
    try:  # 0.7.53 (decisões 59 a 62): amostras e assinaturas de formato do que foi lido; envio em silêncio, com fila
        import sys as _sys
        from . import amostras
        amostras.descarregar(banco, aviso=aviso)
        if not ("unittest" in _sys.modules and not os.environ.get("LEXSUITE_REDE_NOS_TESTES")):
            amostras.enviar_pendentes(banco, cfg, _versao())
    except Exception:  # nosec B110 - amostra nunca derruba a leitura
        pass
    try:
        banco.atualizar_estatisticas()  # 0.7.14: totais diários que nunca se apagam
        banco.atualizar_estatisticas_leves(setor_do_lead)  # 0.7.53 (decisão 67): situação e setor por mês, de todos os tribunais
    except Exception as e:  # noqa: BLE001 - estatística nunca derruba a leitura
        aviso(f"  Não consegui atualizar as estatísticas ({e.__class__.__name__}).")
    try:  # 0.7.48 (decisões 40 a 42): limpeza automática depois de cada leitura, sempre depois das estatísticas
        aviso("  Limpando os dados do programa…")
        lp = limpar_banco(banco, r, "depois da leitura")
        if lp["resumidos"] or lp["apagados"]:
            aviso(f"  Limpeza: {lp['resumidos']} resumido(s), {lp['apagados']} apagado(s), {lp['mantidos']} mantido(s) por serem trabalhados.")
    except Exception as e:  # noqa: BLE001 - a limpeza nunca derruba a leitura
        aviso(f"  Não consegui limpar os dados do programa ({e.__class__.__name__}).")
    apagados = banco.limpar_antigos(int(r.get("guardar_dias") or 365))
    try:  # 0.7.17 (decisão 14): banco acima de 1 GB resume com 6 meses só os processos nunca abertos
        if banco.espaco()["bytes"] > 1024 ** 3:
            resumidos = banco.limpar_detalhe(6, perfil="automático", so_nunca_abertos=True)
            if resumidos:
                banco.compactar()
                aviso(f"  Os dados do programa passaram de 1 GB: {resumidos} processo(s) nunca aberto(s) com mais de 6 meses ficaram só com o resumo.")
                banco.registrar("saude", {"fonte": "Dados do programa", "situacao": "atenção", "detalhe": f"acima de 1 GB: {resumidos} resumidos (6 meses, nunca abertos)"})
    except Exception as e:  # noqa: BLE001 - a retenção nunca derruba a leitura
        aviso(f"  Não consegui resumir os dados do programa ({e.__class__.__name__}).")
    if apagados:
        aviso(f"  Retenção: {apagados} registro(s) com mais de {int(r.get('guardar_dias') or 365)} dias resumidos ou apagados (o detalhe sai; o resumo e as estatísticas ficam).")
    if interrompida:  # 0.7.16: depois de uma parada na Receita, conta só o que foi feito (antes misturava parcial e total)
        com_cnpj = sum(1 for n in novos_feitos if n.get("cnpjs"))
    parcial_pt, parcial_en = (" (leitura interrompida)", " (reading stopped)") if interrompida else ("", "")
    proc_pt = "1 processo novo" if len(novos) == 1 else f"{len(novos)} processos novos"
    proc_en = "1 new case" if len(novos) == 1 else f"{len(novos)} new cases"
    pubs_pt = "1 publicação lida" if len(pubs) == 1 else f"{len(pubs)} publicações lidas"
    pubs_en = "1 notice read" if len(pubs) == 1 else f"{len(pubs)} notices read"
    situacao = {"pt": f"{pubs_pt}; {proc_pt} contra empresas; {com_cnpj} com CNPJ no Diário{parcial_pt}.",
                "en": f"{pubs_en}; {proc_en} against companies; {com_cnpj} with a tax ID in the Court Journal{parcial_en}.",
                "quando": agora.isoformat(timespec="minutes"), "tribunais": escolhidos, "lidas": len(pubs), "novas": len(novos), "com_cnpj": com_cnpj}
    if tentativas and not pubs and not interrompida and all(t["causa"] in ("ok", "ainda_nao_liberado_3h", "nao_publicado") for t in tentativas):
        # 0.7.36 (dono): "0 publicações lidas" parecia falha; quando nada é novo, a tela diz por quê
        ate = max((str(t.get("leu_ate") or "")[:10] for t in tentativas), default="")
        ate_br, ate_en = (config.data_curta(ate, ano=False), config.data_curta(ate, ano=False, en=True)) if len(ate) == 10 else ("", "")
        # revisão da Operação: sem prometer horário (o DJEN libera o Diário de hoje em horários diferentes); a próxima leitura pega
        situacao["pt"] = (f"Nada novo: os cadernos até {ate_br} já tinham sido lidos." if ate_br else "Nada novo: os Diários já publicados tinham sido lidos.") + \
            " O Diário de hoje entra na próxima leitura, quando estiver liberado."
        situacao["en"] = (f"Nothing new: the issues up to {ate_en} had already been read." if ate_en else "Nothing new: the Court Journals already published had been read.") + \
            " Today's Court Journal comes in the next reading, once released."
        situacao["nada_novo"] = True
    from . import causas
    for t in tentativas:  # avisos que não são erro (Diário de hoje só às 3h) e tribunais que falharam
        if t["causa"] == "ok":
            continue
        situacao.setdefault("avisos", []).append({
            "tribunal": t["tribunal"], "causa": t["causa"], "aviso": causas.e_aviso(t["causa"]), "leu_ate": t.get("leu_ate", ""),
            "pt": f"{t['tribunal']}: {causas.mensagem(t['causa'], 'pt')}", "en": f"{t['tribunal']}: {causas.mensagem(t['causa'], 'en')}"})
    for t in tentativas:  # 0.7.47: "é do CNJ ou é daqui", uma frase por origem (vale também para o dia que o CNJ não entregou)
        if t.get("origem_falha"):
            av_ = _antivirus(pasta_base)
            o_ = situacao.setdefault("origens", {})[t["origem_falha"]] = {
                "pt": causas.mensagem_origem(t["origem_falha"], "pt", av_), "en": causas.mensagem_origem(t["origem_falha"], "en", av_)}
            if t["origem_falha"] == "bloqueio_local":
                from . import computador
                o_.update({"link": computador.link(av_, "pt"), "link_en": computador.link(av_, "en")})
    situacao.update(info_consulta)
    if info_consulta:
        situacao["rodada"] = rodada_id
    if info_consulta.get("consulta"):  # 0.7.48, cena 3
        c_ = info_consulta["consulta"]
        n_c = int(c_.get("novos") or 0)
        situacao["pt"] = ("Pela consulta pública (caderno do CNJ fora): " + ("1 processo novo" if n_c == 1 else f"{n_c} processos novos") + ". ") + situacao["pt"]
        situacao["en"] = ("Through the public search (CNJ Court Journal down): " + ("1 new case" if n_c == 1 else f"{n_c} new cases") + ". ") + situacao["en"]
        situacao.pop("nada_novo", None)
    aviso("  " + situacao["pt"])
    if pasta_base:
        pagina = gravar_saida(cfg, banco, os.path.join(pasta_base, "saida", "radar"), agora, situacao, aviso, versao)  # 0.7.33: critérios por área
        if base_compartilhada and (cfg.get("compartilhar") or {}).get("planilha", True):
            if not gravar_planilha(cfg, pagina, banco, versao, pasta_base, aviso):
                situacao["aviso_planilha"] = True
    if interrompida:  # tudo já foi fechado (contagem, estatísticas, planilha); avisa quem chamou que foi a pedido
        e = Interrompida("interrompida")
        e.situacao = situacao
        raise e
    return situacao


ALCANCES = {"hibrido": (183, 50), "30d": (30, None), "6m": (183, None), "12m": (366, None), "10": (None, 10), "50": (None, 50), "todos": (None, None)}


def chave_empresa(cnpj="", nome=""):
    """A mesma empresa: a raiz do CNPJ (8 dígitos, junta matriz e filiais) ou, sem CNPJ, o nome sem acento, pontuação e
    "LTDA"/"S.A."/"EIRELI"/"ME"/"EPP"."""
    raiz = re.sub(r"\D", "", str(cnpj or ""))[:8]
    if len(raiz) == 8:
        return "c:" + raiz
    n = re.sub(r"[^a-z0-9 ]", " ", cl.sem_acento(str(nome or "")).lower())
    n = re.sub(r"\b(ltda|s ?a|eireli|me|epp|limitada|sociedade anonima)\b", " ", n)
    n = " ".join(n.split())
    return "n:" + n if n else ""


def processos_das_empresas(cfg, banco, empresas, alcance="hibrido", hoje=None):
    """0.7.49: para cada empresa pedida ({chave, cnpj, nome}), os processos dela que o programa tem (Lista e Arquivo), do mais
    novo para o mais antigo, dentro do alcance (hibrido = até 50 dos últimos 6 meses). Devolve {chave: {total, sem_cnpj, itens}}.
    A chave é o CNPJ (dono, 15/Nov): homônimo com outro CNPJ nunca entra; processo sem CNPJ com o mesmo nome entra marcado
    `so_nome` ("confira") e fica fora do total da empresa.
    Uma passada só pelo banco para todas as empresas pedidas (com 60 mil processos, menos de 1 s para 10 empresas)."""
    dias, teto = ALCANCES.get(alcance, ALCANCES["hibrido"])
    hoje = hoje or dt.date.today()
    corte = (hoje - dt.timedelta(days=dias)).isoformat() if dias else ""
    chaves, pistas, aceitos = [], [], {}

    def pista_nome(chave_n):
        palavras = [w for w in chave_n[2:].split() if len(w) >= 3]
        p_ = max(palavras, key=len) if palavras else chave_n[2:]
        return re.sub(r"[aeiouc]", "_", p_)  # vogal (e ç) vale qualquer letra: "ficticia" acha "Fictícia"; quem decide é a conferência abaixo
    for e in empresas:
        chave = str(e.get("chave") or "") or chave_empresa(e.get("cnpj"), e.get("nome"))
        if not chave or chave in chaves:
            continue
        chaves.append(chave)
        ok = {chave}
        pistas.append(chave[2:] if chave.startswith("c:") else pista_nome(chave))
        n_ = chave_empresa("", e.get("nome")) if e.get("nome") else ""
        if chave.startswith("c:") and n_:  # revisão: a mesma empresa com e sem CNPJ vira um bloco só (o nome junta os sem CNPJ)
            ok.add(n_)
            pistas.append(pista_nome(n_))
        aceitos[chave] = ok
    if not chaves:
        return {}
    achados = {c: [] for c in chaves}
    onde = " OR ".join(["dados LIKE ?"] * len(pistas))
    for proc, data, dados in banco.con.execute(f"SELECT processo, coalesce(data, primeira_vez, ''), dados FROM leads WHERE {onde}",  # nosec B608 - só marcadores
                                               ["%" + p + "%" for p in pistas]):
        try:
            d = json.loads(dados or "{}")
        except ValueError:
            continue
        emp = d.get("empresa_receita") or {}
        cnpj_ = chave_empresa(emp.get("cnpj"), "") or next((chave_empresa(c, "") for c in (d.get("cnpjs") or [])[:1]), "") or chave_empresa(d.get("cnpj_inferido"), "")
        nomes_ = {chave_empresa("", n) for n in ([emp.get("razao_social") or ""] + list(d.get("empresas") or [])[:1]) if n}
        da_linha = ({cnpj_} if cnpj_ else set()) | nomes_
        for c in chaves:
            if not (da_linha & aceitos[c]):
                continue
            if cnpj_ and c.startswith("c:") and cnpj_ != c:
                continue  # homônimo com outro CNPJ: é outra empresa (dono, 15/Nov: "a chave é o CNPJ")
            achados[c].append((str(data or "")[:10], proc, bool(c.startswith("c:") and not cnpj_)))
    saida = {}
    for chave in chaves:
        lista = sorted(achados[chave], reverse=True)
        total = sum(1 for x in lista if not x[2])  # o total da empresa conta só o que tem o CNPJ dela
        so_nome = {x[1] for x in lista if x[2]}
        if corte:
            lista = [x for x in lista if x[0] >= corte]
        if teto:
            lista = lista[:teto]
        itens = itens_de(cfg, banco, [x[1] for x in lista])
        for p in so_nome:
            if p in itens:
                itens[p]["so_nome"] = True  # sem CNPJ no Diário, mesmo nome: a tela mostra "confira"
        saida[chave] = {"total": total, "sem_cnpj": len(so_nome), "itens": [itens[x[1]] for x in lista if x[1] in itens]}
    return saida


def cnpj_provavel(banco, nome):
    """0.7.50 (dono): para processos sem CNPJ, o CNPJ que outros processos com o MESMO nome já trazem. Só sugere se houver uma
    raiz só (a chave é o CNPJ); com duas ou mais, não sugere. Devolve {cnpj, com_cnpj, sem_cnpj} ou {}."""
    chave, exata = chave_empresa("", nome), cl.chave_exata(nome)
    if not chave or not exata:
        return {}
    palavras = [w for w in chave[2:].split() if len(w) >= 3]
    pista = re.sub(r"%+", "%", re.sub(r"[aeiouc]", "%", max(palavras, key=len) if palavras else chave[2:]))  # 0.7.51: acento gravado de qualquer jeito
    raizes, cnpjs, sem = {}, {}, 0
    for (dados,) in banco.con.execute("SELECT dados FROM leads WHERE dados LIKE ?", ("%" + pista + "%",)):
        try:
            d = json.loads(dados or "{}")
        except ValueError:
            continue
        emp = d.get("empresa_receita") or {}
        nomes = [emp.get("razao_social") or ""] + list(d.get("empresas") or [])[:1]
        if not any(cl.chave_exata(n) == exata for n in nomes if n):
            continue  # 0.7.51 (revisão da 0.7.50): nome escrito igual; "X Ltda" e "X S.A." são outras empresas
        c = re.sub(r"\D", "", str(emp.get("cnpj") or (d.get("cnpjs") or [""])[0] or ""))
        if len(c) == 14:
            raizes[c[:8]] = raizes.get(c[:8], 0) + 1
            cnpjs[c] = cnpjs.get(c, 0) + 1
        elif not d.get("cnpj_inferido"):
            sem += 1
    if len(raizes) != 1 or not sem:
        return {}
    melhor = max(cnpjs, key=lambda c: (c[8:12] == "0001", cnpjs[c]))  # a matriz, se houver; senão o mais comum
    return {"cnpj": melhor, "com_cnpj": sum(raizes.values()), "sem_cnpj": sem}


def usar_cnpj(banco, nome, cnpj, perfil=""):
    """Grava o CNPJ confirmado pelo escritório nos processos com o mesmo nome e sem CNPJ (marcado `cnpj_inferido`)."""
    chave, cnpj, exata = chave_empresa("", nome), re.sub(r"\D", "", str(cnpj or "")), cl.chave_exata(nome)
    if not chave or not exata or len(cnpj) != 14:
        return 0
    palavras = [w for w in chave[2:].split() if len(w) >= 3]
    pista = re.sub(r"%+", "%", re.sub(r"[aeiouc]", "%", max(palavras, key=len) if palavras else chave[2:]))  # 0.7.51: acento gravado de qualquer jeito
    mudar = []
    for proc, dados in banco.con.execute("SELECT processo, dados FROM leads WHERE dados LIKE ?", ("%" + pista + "%",)):
        try:
            d = json.loads(dados or "{}")
        except ValueError:
            continue
        emp = d.get("empresa_receita") or {}
        if emp.get("cnpj") or (d.get("cnpjs") or []) or d.get("cnpj_inferido"):
            continue
        if any(cl.chave_exata(n) == exata for n in ([emp.get("razao_social") or ""] + list(d.get("empresas") or [])[:1]) if n):
            d["cnpj_inferido"] = cnpj
            mudar.append((json.dumps(d, ensure_ascii=False), proc))
    banco.con.executemany("UPDATE leads SET dados = ? WHERE processo = ?", mudar)
    if mudar:
        banco.registrar_acao(perfil, "empresa:cnpj", cnpj, "", f"{len(mudar)} processos", len(mudar))
    banco.con.commit()
    return len(mudar)


def copiar_contato_empresa(cfg, banco, chave, dias=90, cnpj="", nome="", perfil="", hoje=None):
    """0.7.50 (decisão 51): o contato da empresa (do processo mais recente que tem contato) vai para os processos da mesma
    empresa, dos últimos `dias`, que estão sem contato. Devolve {copiados, processos, origem, ids}."""
    hoje = hoje or dt.date.today()
    r = processos_das_empresas(cfg, banco, [{"chave": chave, "cnpj": cnpj, "nome": nome}], "todos", hoje=hoje).get(chave) or {"itens": []}
    corte = (hoje - dt.timedelta(days=int(dias or 90))).isoformat()
    itens = [i for i in r["itens"] if not i.get("so_nome")]
    com = [i for i in itens if (i.get("contato") or {}).get("tem")]
    if not com:
        return {"copiados": 0, "processos": 0, "origem": "", "ids": []}
    origem = max(com, key=lambda i: i.get("diario_em") or "")
    e = origem.get("empresa") or {}
    extras = [("telefone", e.get("telefone")), ("telefone", e.get("telefone2")), ("email", e.get("email"))]
    destinos = [i["processo"] for i in itens if (i.get("diario_em") or "") >= corte and not (i.get("contato") or {}).get("tem")]
    nomes_ok = {chave_empresa("", n) for n in [e.get("razao_social") or ""] + list(origem.get("empresas") or []) if n}

    def da_empresa(c):  # revisão da 0.7.50: contato marcado com outra parte do mesmo processo não vai para esta empresa
        return not c.get("empresa") or chave_empresa("", c.get("empresa")) in nomes_ok
    ids = banco.copiar_contatos(origem["processo"], destinos, extras=extras, perfil=perfil, aceitar=da_empresa)
    return {"copiados": len(ids), "processos": len(destinos), "origem": origem["processo"], "ids": ids}


def registrar_consulta(banco, consulta, novos, agora, origem):
    """0.7.48: grava no Histórico a leitura pela consulta pública e a conferência pelo caderno; devolve o que a faixa mostra
    ({consulta: {novos, tribunais, pedidos, minutos, parcial}, conferencia: {hora, a_mais, tribunais}})."""
    saida = {}
    if not consulta:
        return saida
    quando = agora.astimezone().isoformat(timespec="seconds")
    lidos_c = consulta.get("lidos") or []
    for x in lidos_c:  # os processos já estão gravados: só agora o dia conta como lido pela consulta (uma vez por dia pendente)
        banco.registrar_consulta_dia(x["tribunal"], x["data"], x["publicacoes"], x["pedidos"], x["parcial"], x["processos"])
    if lidos_c:
        procs = set().union(*[x["processos"] for x in lidos_c])
        n_novos = sum(1 for n in novos if n.get("processo") in procs)
        info = {"quando_local": quando, "origem": origem, "novos": n_novos,
                "tribunais": sorted({x["tribunal"] for x in lidos_c}), "dias": sorted({x["data"] for x in lidos_c}),
                "publicacoes": sum(x["publicacoes"] for x in lidos_c), "pedidos": sum(x["pedidos"] for x in lidos_c),
                "minutos": max(1, round(sum(x["segundos"] for x in lidos_c) / 60)), "parcial": any(x["parcial"] for x in lidos_c)}
        banco.registrar("consulta", info)
        saida["consulta"] = {k: info[k] for k in ("novos", "tribunais", "dias", "pedidos", "minutos", "parcial")}
    conferir = consulta.get("conferir") or []
    if conferir:
        a_mais_total, tribs = 0, set()
        for c in conferir:
            a_mais = sum(1 for n in novos if n.get("processo") in c["processos"])
            if banco.conferir_consulta_dia(c["tribunal"], c["data"], a_mais) is not None:
                a_mais_total += a_mais
                tribs.add(c["tribunal"])
        if tribs:
            info = {"quando_local": quando, "origem": origem, "a_mais": a_mais_total, "tribunais": sorted(tribs),
                    "dias": sorted({c["data"] for c in conferir if c["tribunal"] in tribs})}
            banco.registrar("conferencia", info)
            saida["conferencia"] = {"hora": agora.strftime("%Hh%M"), "a_mais": a_mais_total, "tribunais": sorted(tribs)}
    return saida


def gravar_planilha(cfg, pagina, banco, versao, pasta_base, aviso=print):
    """0.7.53 (decisões 63 a 65): antes de gravar, junta o que os outros computadores da mesma pasta fizeram, grava o que este
    fez, e só grava a planilha com a trava curta da pasta e se ela não for voltar atrás (vetor da aba Sobre). Nada se perde: a
    planilha é espelho do banco de cada computador e dos arquivos de troca."""
    from . import troca
    if not compartilhar.pasta_base(cfg):
        return _gravar_planilha(cfg, pagina, banco, versao, pasta_base, aviso)
    with troca.trava(cfg) as t:
        if t is None:
            aviso("  Outro computador está gravando a planilha agora; ela é regravada daqui a pouco. A lista está salva.")
            return False
        try:
            if troca.juntar(banco, cfg, aviso):
                pagina = montar_radar(cfg, banco, None, False, pagina.get("situacao"))
            troca.exportar(banco, cfg)
        except OSError as e:  # pasta fora do ar: a planilha deste computador continua valendo
            aviso(f"  Troca com os outros computadores não feita agora ({e.__class__.__name__}).")
        caminho = preferencias.caminho(compartilhar.pasta_base(cfg), "trabalhista")
        atras = troca.atrasado(banco, cfg, compartilhar.ler_vetor(caminho))
        if atras:
            primeira = next((e.get("desde") for e in banco.execucoes("troca_espera", 1) if e.get("de") == atras), "")
            if not primeira:
                banco.registrar("troca_espera", {"de": atras, "desde": dt.datetime.now().isoformat(timespec="seconds")})
            elif (dt.datetime.now() - dt.datetime.fromisoformat(primeira)).total_seconds() > troca.ESPERA_ATRASO_H * 3600:
                banco.registrar("saude", {"fonte": "Troca entre computadores", "situacao": "atenção",
                                          "detalhe": "planilha regravada sem os arquivos de outro computador (não chegaram em 2 h)"})
                atras = []
            if atras:
                aviso("  A planilha já tem dados de outro computador que ainda não chegaram aqui; ela é regravada quando chegarem.")
                return False
        return _gravar_planilha(cfg, pagina, banco, versao, pasta_base, aviso, vetor=troca.vetor(banco, cfg))


def _gravar_planilha(cfg, pagina, banco, versao, pasta_base, aviso=print, vetor=None):
    """Grava as planilhas (0.7.16: uma por frente). Se uma estiver aberta no Excel (o Windows trava o arquivo), avisa com
    clareza: nada se perde, a lista está no computador e a planilha é regravada depois. Antes, confere o disco e o
    tamanho: a 80% do limite avisa; a 100% faz a cópia de segurança e enxuga a aba Arquivo sozinho. Devolve True se
    gravou todas."""
    try:
        from . import atualizar, assinatura, armazenamento
        base = compartilhar.pasta_base(cfg)
        if not base:
            return False
        d = armazenamento.disco(base)
        if d["nivel"] == "critico":
            aviso("  " + armazenamento.texto_disco(d))
            banco.registrar("saude", {"fonte": "Disco", "situacao": "erro", "detalhe": armazenamento.texto_disco(d)[:200]})
            return False
        if d["nivel"] == "baixo":
            aviso("  " + armazenamento.texto_disco(d))
        chave = atualizar.chave_publica(pasta_base)
        impressao = assinatura.impressao(chave) if chave else ""
        doze = (dt.date.today() - dt.timedelta(days=366)).isoformat()
        # 0.7.53 (decisão 67): só os tribunais escolhidos hoje (o resto fica no programa e na aba Estatística, em números);
        # aba Radar com no máximo 30 dias pela data no Diário; antes da primeira gravação enxuta, uma cópia de como era
        escolhidos = tribunais.validar((cfg.get("radar") or {}).get("tribunais") or ["TRT2", "TRT15"])
        armazenamento.copia_antes_da_0753(cfg, banco, aviso)
        todos = armazenamento.so_escolhidos([i for i in montar_radar(cfg, banco, visao="arquivo")["itens"]
                                             if (i.get("primeira_vez") or "9") >= doze], escolhidos)
        lista, _mais_velhos = armazenamento.radar_ate_30_dias(armazenamento.so_escolhidos(pagina.get("itens") or [], escolhidos))
        estatistica = armazenamento.linhas_estatistica(banco)
        frentes = {armazenamento.frente_do(i) for i in lista + todos} | {f for f, _ in preferencias.planilhas_existentes(base)}
        ordem = [f for f in preferencias.NOMES_FRENTE if f in frentes] or ["trabalhista"]
        tudo_ok, limpou = True, False
        for frente in ordem:
            prefs = preferencias.carregar(base, frente=frente, banco=banco, cfg_radar=cfg.get("radar"))
            # 0.7.33 (decisão de 12/Nov): a planilha compartilhada é o registro do escritório, completa; dias do Arquivo e
            # limite de linhas são os padrões, e os critérios de cada pessoa valem na tela e no saida/ dela
            limite = int(preferencias.PADRAO["limite_linhas"])
            radar_f = [i for i in lista if armazenamento.frente_do(i) == frente]
            todos_f = [i for i in todos if armazenamento.frente_do(i) == frente]
            na_lista = {i.get("processo") for i in radar_f}  # o que já está na aba Radar não se repete no Arquivo
            arquivo = [i for i in armazenamento.selecionar_arquivo(todos_f, preferencias.PADRAO["dias_arquivo"], armazenamento.corte(banco, frente))
                       if i.get("processo") not in na_lista]
            if len(radar_f) + len(arquivo) >= limite and not limpou and not armazenamento.limpeza_recente(banco):
                aviso(f"  A planilha {armazenamento.FRENTE_LEGIVEL.get(frente, frente)} chegou ao limite de {limite} linhas: "
                      "guardo uma cópia de segurança e enxugo a aba Arquivo (nada sai do programa).")
                armazenamento.limpar(cfg, banco, pasta_base, versao, aviso, automatico=True)
                limpou = True
                arquivo = [i for i in armazenamento.selecionar_arquivo(todos_f, preferencias.PADRAO["dias_arquivo"], armazenamento.corte(banco, frente))
                           if i.get("processo") not in na_lista]
            radar_f, arquivo, cortou = armazenamento.caber(radar_f, arquivo, limite)
            if cortou:
                aviso(f"  A planilha ficou só com as {limite} linhas mais recentes; o resto está no programa (tela Arquivo).")
            linhas = len(radar_f) + len(arquivo)
            texto = armazenamento.aviso_tamanho(frente, linhas, limite)
            if texto:
                aviso("  " + texto)
            processos = {i.get("processo") for i in radar_f + arquivo} if len(ordem) > 1 else None
            caminho = compartilhar.gravar_radar(cfg, pagina, banco, versao, COLUNAS_RADAR, linha_csv, impressao, pasta_base,
                                                aviso, arquivo=arquivo, frente=frente, itens=radar_f, aviso_tamanho=texto,
                                                processos=processos, criterios=prefs,
                                                estatistica=[estatistica[0]] + [l for l in estatistica[1:] if l[2] == armazenamento.FRENTE_LEGIVEL.get(frente, frente)], vetor=vetor)
            if not caminho:  # planilha em uso ou ilegível: gravar_radar já avisou e não regravou nada
                tudo_ok = False
                continue
            try:
                tamanho = os.path.getsize(caminho)
            except OSError:
                tamanho = 0
            banco.registrar("planilha", {"frente": frente, "linhas": linhas, "limite": limite, "bytes": tamanho, "radar": len(radar_f),
                                         "nome": os.path.basename(caminho)})
        return tudo_ok
    except PermissionError:
        aviso("  A planilha está aberta no Excel (ou em outro programa), ou falta permissão para gravar nesta pasta ou arquivo: "
              "feche-a ou confira a pasta para ela ser atualizada. A lista está salva. / The spreadsheet is open or the folder is not writable; the list is saved.")
        banco.registrar("saude", {"fonte": "Pasta compartilhada", "situacao": "atenção",
                                  "detalhe": "planilha aberta em outro programa ou sem permissão para gravar na pasta"})
    except Exception as e:  # a pasta pode estar fora do ar (Drive pausado); a rodada em si deu certo
        aviso(f"  Não consegui gravar a planilha compartilhada ({e.__class__.__name__}: {e}).")
        banco.registrar("saude", {"fonte": "Pasta compartilhada", "situacao": "erro", "detalhe": f"{e.__class__.__name__}: {e}"[:200]})
    return False


def ja_conferidos_para_saude(tentativas):
    """0.7.29: Diários já lidos antes não são alarme; mas, se algum tribunal falhou, a Saúde continua alarmando (0)."""
    if not all(t.get("causa") in ("ok", "ainda_nao_liberado_3h") for t in tentativas or []):
        return 0
    return sum(int(t.get("ja_conferidos") or 0) for t in tentativas or [])


TRAVA_REGRAVAR = threading.RLock()  # revisão da 0.7.29: "Salvar regras", "Gravar a planilha agora", a regravação depois
# da planilha aberta e a limpeza nunca se cruzam (uma leria as abas antes da outra gravar e desfaria a mudança)


def setor_do_lead(lead):
    """O mesmo setor que o cartão mostra (item_de_lead), a partir do lead guardado."""
    emp = lead.get("empresa_receita") or {}
    nomes = lead.get("empresas") or []
    return cl.setor(nomes if not emp.get("atividade") else [emp.get("atividade", "")] + nomes)


def regravar_planilha(cfg, banco, pasta_base, versao, aviso=print):
    with TRAVA_REGRAVAR:
        return _regravar_planilha(cfg, banco, pasta_base, versao, aviso)


def _regravar_planilha(cfg, banco, pasta_base, versao, aviso=print):
    """Botão "Gravar a planilha agora" (depois de fechar o Excel): grava a lista atual sem ler o Diário de novo."""
    pagina = montar_radar(cfg, banco, None, False, None)
    return gravar_planilha(cfg, pagina, banco, versao, pasta_base, aviso)


def gravar_saida(cfg, banco, pasta, agora, situacao, aviso=print, versao="", prefs=None):
    """radar.html (abre sem internet), radar.json e radar.csv com a lista atual."""
    os.makedirs(pasta, exist_ok=True)
    pagina = montar_radar(cfg, banco, agora, False, situacao, prefs=prefs)
    pagina["versao"] = versao or _versao()
    saidas.gravar_radar(os.path.join(pasta, "radar.html"), pagina)
    saidas.gravar_json(os.path.join(pasta, "radar.json"), pagina)
    saidas.gravar_csv(os.path.join(pasta, "radar.csv"), [linha_csv(i) for i in pagina["itens"]], COLUNAS_RADAR)
    aviso(f"  Montando a lista: {len(pagina['itens'])} processos.")  # 0.7.36 (dono): sem caminho de arquivo na tela
    return pagina


def _versao():
    from . import VERSAO
    return VERSAO


CRITERIO_DESDE = "2026-11-09"  # a regra mais estreita entrou na 0.7.16 (publicada em 09/11/2026)
CRITERIO_REGRA = ("ação nova = lista de distribuição, audiência inicial, una ou de conciliação, notificação inicial, "
                  "\"notifique-se a reclamada\" ou citação inicial, só em varas de 1º grau")


def acoes_do_dia(pubs, ano_minimo, ja_vistos):
    """Ações novas contra empresa em todas as varas das publicações (lista de distribuição ou notificação inicial)."""
    return [l for l in djen.leads(pubs, vara=None, ano_minimo=ano_minimo, ja_vistos=ja_vistos) if l.get("sinal_de_acao_nova")]


COLUNAS_RADAR = [
    ("Situação", "situacao_legivel"), ("Frente", "frente_legivel"), ("Hora", "hora"), ("Tribunal", "tribunal"), ("Vara", "vara"), ("Processo", "processo"), ("Rito", "rito"),
    ("Ajuizado em", "ajuizado_planilha"),  # 0.7.51: só a data real do ajuizamento (antes saía a da publicação)
    ("Empresa(s)", "empresas"), ("CNPJ", "cnpj"), ("Porte", "porte_legivel"),
    ("Capital social", "capital_social"), ("CNAE", "atividade"), ("Setor", "setor"), ("Cidade/UF", "cidade_uf"),
    ("Telefone", "telefone"), ("E-mail", "email"), ("Endereço", "endereco"), ("CEP", "cep"), ("Outros contatos", "outros_contatos"), ("Sócios/administradores", "socios"), ("Provável jurídico próprio", "gigante"),
    ("Valor da causa", "valor_causa"), ("Origem do valor", "valor_fonte"), ("Link DJEN", "link_djen"), ("Consulta PJe", "link_pje"),
    # 0.7.51 (desenho das datas e fontes): datas e andamento, no fim, para não mudar o lugar das colunas de sempre
    ("Fonte do ajuizamento", "ajuizado_fonte_legivel"), ("Processo novo ou antigo", "novo_legivel"), ("1ª publicação no Diário", "pub1"),
    ("Última publicação no Diário", "pubN"), ("Encontrado pelo RADAR em", "primeira_vez"), ("Andamento", "andamento_legivel"),
    ("Classe (CNJ)", "classe_cnj"), ("Assuntos (CNJ)", "assuntos_cnj"),
    # 0.7.53 (decisão 65): quem viu e quem marcou a situação, de qualquer computador do escritório
    ("Visto por", "visto_por"), ("Situação marcada por", "status_por"),
]
FONTE_AJ_LEGIVEL = {"cnj": "CNJ", "diario": "Diário (lista de distribuição)", "digitado": "Digitado ou área logada", "aproximada": ""}
ANDAMENTO_LEGIVEL = {"": "Sem acordo nem sentença", "acordo": "Com acordo", "sentenca": "Com sentença", "transito": "Trânsito em julgado",
                     "arquivado": "Arquivado"}


def linha_csv(item):
    e = item["empresa"]
    return {
        **item, "cnpj": e["cnpj"], "porte_legivel": e["porte_legivel"], "capital_social": e["capital_social"],
        "atividade": e["atividade"], "cidade_uf": f"{e['municipio']}/{e['uf']}" if e["municipio"] else "",
        "telefone": e["telefone"], "email": e["email"], "socios": [s.get("nome", "") for s in e["socios"]],
        "gigante": "sim" if item["gigante"] else "",
        "situacao_legivel": SITUACAO_LEGIVEL.get(item.get("situacao"), "Novo") + (f" ({item['motivo']})" if item.get("motivo") else ""),
        "frente_legivel": FRENTE_LEGIVEL.get(item.get("frente"), ""),
        "endereco": endereco(e), "cep": e.get("cep", ""),
        "outros_contatos": [f"{c['canal']}: {c['valor']} ({c['fonte']}, {c['data']})" for c in item.get("contatos") or []],
        "ajuizado_planilha": item.get("ajuizado") if item.get("ajuizado_fonte") in ("cnj", "diario", "digitado") else "",
        "ajuizado_fonte_legivel": FONTE_AJ_LEGIVEL.get(item.get("ajuizado_fonte") or "", ""),
        "novo_legivel": {True: "Novo", False: "Antigo"}.get(item.get("novo"), ""),
        "pub1": min([x for x in ((item.get("cnj") or {}).get("pub1"), (item.get("diario_hist") or {}).get("pub1")) if x] or [""]),
        "pubN": max([x for x in ((item.get("cnj") or {}).get("pubN"), (item.get("diario_hist") or {}).get("pubN")) if x] or [""]),
        "andamento_legivel": ANDAMENTO_LEGIVEL.get((item.get("cnj") or {}).get("andamento") or "", "") if (item.get("cnj") or {}).get("ajuizado") else "",
        "classe_cnj": (item.get("cnj") or {}).get("classe") or "", "assuntos_cnj": list((item.get("cnj") or {}).get("assuntos") or []),
    }


SITUACAO_LEGIVEL = {"novo": "Novo", "visto": "Visto", "em_analise": "Em análise", "em_contato": "Em contato",
                    "virou_cliente": "Virou cliente", "descartado": "Descartado", "arquivado": "Arquivado"}
FRENTE_LEGIVEL = {"trabalhista": "Trabalhista", "tributario": "Tributário", "civel": "Cível", "empresarial": "Empresarial"}


def endereco(e):
    rua = ", ".join(x for x in (e.get("logradouro", ""), e.get("numero", "")) if x)
    partes = [rua + (f" {e['complemento']}" if e.get("complemento") else ""), e.get("bairro", ""),
              "/".join(x for x in (e.get("municipio", ""), e.get("uf", "")) if x)]
    return " - ".join(x for x in partes if x)


# ---------- 0.7.51: completar cada processo com as fontes públicas (desenho documentacao/DESENHO-DATAS-E-FONTES-0751.md) ----------
ESPERA_CNJ = (30 * 60, 2 * 3600, 6 * 3600, 24 * 3600)  # novas tentativas: 30 min, 2 h, 6 h, 24 h
AGUARDANDO_DIAS = 15  # o CNJ atrasa: até 15 dias depois de o RADAR ver o processo, não achar no CNJ não é falha
HIST_MAX = 120  # pedidos ao histórico do Diário por leitura (1 por segundo)


def _causa_fonte(e):
    from . import rede
    if isinstance(e, rede.BloqueadoForaDoBrasil):
        return "o Diário só responde a pedidos de dentro do Brasil"
    nome = e.__class__.__name__
    if nome == "RespostaParcial":
        return "o CNJ respondeu pela metade (ocupado)"
    if isinstance(e, RuntimeError) and "chave" in str(e).lower():
        return "chave pública do CNJ não lida"
    if isinstance(e, rede.ErroHTTP) and getattr(e, "codigo", 0) == 429:
        return "o CNJ pediu para esperar (muitos pedidos)"
    if isinstance(e, rede.ErroHTTP):
        return f"o servidor respondeu {getattr(e, 'codigo', '')}".strip()
    return "sem resposta (rede ou servidor fora)"


def completar_fontes(banco, agora=None, novos=(), aviso=print, parar=None, tempo_max=240, consultar=None, historico=None):
    """Depois da leitura do Diário: para cada processo da Lista (últimos 12 meses), busca no CNJ (DataJud, em lotes de 40) a data de
    ajuizamento, a classe, os assuntos e a jornada, e no Diário o histórico de publicações dos que entraram por sinal fraco. Grava o
    estado de cada fonte (ok, aguardando, não encontrado, falhou) para o "Tentar de novo" e para a próxima leitura repetir o que faltou.
    Nunca derruba a leitura. Devolve um resumo para o registro."""
    from . import datajud
    import sys as _sys
    # nos testes automáticos, só as fontes simuladas rodam (nenhum pedido sai do computador); no programa, "unittest" nunca está carregado
    sem_rede = "unittest" in _sys.modules and not os.environ.get("LEXSUITE_REDE_NOS_TESTES")
    if sem_rede and consultar is None and historico is None:
        return {}
    agora = agora or dt.datetime.now()
    t0, est = time.monotonic(), {"cnj_ok": 0, "cnj_aguardando": 0, "cnj_nao_encontrado": 0, "cnj_falhou": 0, "cnj_parou": "",
                                  "hist_ok": 0, "hist_falhou": 0, "hist_parou": "", "fora_classe": 0}
    pular_cnj, pular_hist = sem_rede and consultar is None, sem_rede and historico is None
    consultar = consultar or datajud.consultar_lote
    espera = lambda tent: (agora + dt.timedelta(seconds=ESPERA_CNJ[min(max(tent, 1), len(ESPERA_CNJ)) - 1])).isoformat(timespec="seconds")
    amanha = (agora + dt.timedelta(days=1)).isoformat(timespec="seconds")
    cedo = lambda: (parar and parar()) or time.monotonic() - t0 > tempo_max
    # 1) CNJ
    por_ind, cands = {}, ([] if pular_cnj else banco.candidatos_fonte("cnj", agora, novos))
    for proc, prim, _d in cands:
        ind = datajud.indice_do_numero(proc)
        if ind:
            por_ind.setdefault(ind, []).append((proc, prim))
        else:  # revisão: ramo da Justiça que esta versão ainda não consulta; sai da fila (não ocupa o limite de cada leitura)
            banco.marcar_fonte(proc, "cnj", "ok", agora, causa="não se aplica", commit=False)
    falhas, total_cnj, feitos_cnj = 0, sum(len(v) for v in por_ind.values()), 0
    from . import rede as _rede
    for ind, lista in por_ind.items():
        for i in range(0, len(lista), datajud.LOTE):
            if cedo() or falhas >= 3:
                est["cnj_parou"] = est["cnj_parou"] or ("três falhas seguidas" if falhas >= 3 else "tempo esgotado ou leitura interrompida")
                break
            lote = lista[i:i + datajud.LOTE]
            feitos_cnj += len(lote)
            aviso(f"  Consultando o CNJ: {feitos_cnj} de {total_cnj}…")  # 0.7.52 (ressalva 2 da Operação): andamento por lote
            try:
                resp = consultar(ind, [p for p, _ in lote])
                falhas = 0
            except Exception as e:  # noqa: BLE001 - CNJ fora, ocupado ou sem chave: fica "falhou" com a causa e tenta depois
                falhas += 1
                # 0.7.52 (ressalvas 1 e 3 da Operação): CNJ pedindo para esperar (429) ou sem a chave pública: para o CNJ
                # nesta leitura no primeiro aviso, em vez de insistir mais duas vezes; a fila tenta de novo mais tarde
                if (isinstance(e, _rede.ErroHTTP) and e.codigo == 429) or (isinstance(e, RuntimeError) and "chave" in str(e).lower()):
                    falhas = 3
                causa = _causa_fonte(e)
                for p, _ in lote:
                    banco.marcar_fonte(p, "cnj", "falhou", agora, proxima_em=espera, causa=causa, commit=False)
                    est["cnj_falhou"] += 1
                banco.con.commit()
                continue
            for p, prim in lote:
                doc = resp.get(re.sub(r"\D", "", p))
                if doc:
                    res = datajud.resumo_processo(doc)
                    banco.gravar_no_lead(p, "cnj", res, commit=False)
                    banco.marcar_fonte(p, "cnj", "ok", agora, commit=False)
                    est["cnj_ok"] += 1
                    if datajud.classe_nao_e_nova(res.get("classe")):  # cumprimento de sentença não é ação nova (só se ninguém mexeu nele)
                        n = banco.con.execute("UPDATE leads SET fora_criterio = 1 WHERE processo = ? AND coalesce(status, 'novo') = 'novo' "
                                              "AND dados NOT LIKE '%\"manual\"%' AND processo NOT IN (SELECT processo FROM contatos)", (p,)).rowcount
                        if n:
                            est["fora_classe"] += 1
                            banco.registrar_acao("RADAR", "fora_criterio", p, "", "classe: " + res.get("classe", "")[:60], 1)
                    continue
                try:
                    idade = (agora.date() - dt.date.fromisoformat(str(prim)[:10])).days
                except ValueError:
                    idade = 0
                estado = "aguardando" if idade <= AGUARDANDO_DIAS else "nao_encontrado"
                prox = amanha if idade <= 60 else (agora + dt.timedelta(days=30)).isoformat(timespec="seconds")
                banco.marcar_fonte(p, "cnj", estado, agora, proxima_em=prox, commit=False)
                est["cnj_" + estado] += 1
            banco.con.commit()
    # 2) histórico do Diário pelo número, só para quem entrou por sinal fraco (audiência, notificação) e ainda não tem o ajuizamento
    hist = historico or djen.historico_por_numero
    feitos = 0
    for proc, prim, d in ([] if pular_hist else banco.candidatos_fonte("diario_hist", agora, novos)):
        if feitos >= HIST_MAX or cedo():
            est["hist_parou"] = est["hist_parou"] or "limite desta leitura"
            break
        if sinal_guardado(d) == "lista de distribuição" or (d.get("cnj") or {}).get("ajuizado"):
            banco.marcar_fonte(proc, "diario_hist", "ok", agora, causa="não precisa", commit=False)  # a data já é conhecida
            continue
        if feitos % 10 == 0:
            aviso(f"  Histórico do Diário: {feitos + 1} de até {HIST_MAX}…")
        dig = re.sub(r"\D", "", proc)
        ano = dig[9:13] if len(dig) == 20 else str(agora.year)
        feitos += 1
        try:
            h = hist(proc, f"{ano}-01-01", agora.date().isoformat())
        except Exception as e:  # noqa: BLE001
            banco.marcar_fonte(proc, "diario_hist", "falhou", agora, proxima_em=espera, causa=_causa_fonte(e), commit=False)
            est["hist_falhou"] += 1
            from . import rede
            if isinstance(e, rede.BloqueadoForaDoBrasil):
                est["hist_parou"] = "fora do Brasil"
                break
            continue
        banco.gravar_no_lead(proc, "diario_hist", dict(h, consultado_em=agora.date().isoformat()), commit=False)
        banco.marcar_fonte(proc, "diario_hist", "ok", agora, commit=False)
        est["hist_ok"] += 1
    banco.con.commit()
    if any(est[k] for k in ("cnj_ok", "cnj_falhou", "hist_ok", "hist_falhou")):
        aviso(f"  Fontes públicas: CNJ {est['cnj_ok']} ok, {est['cnj_aguardando']} aguardando, {est['cnj_falhou']} sem resposta; "
              f"histórico do Diário {est['hist_ok']} ok, {est['hist_falhou']} sem resposta.")
    return est


def data_de_referencia(lead):
    """0.7.51 (decisão do dono): a data que diz se o processo é novo é o ajuizamento. Ordem: digitado ou da área logada; CNJ; lista
    de distribuição do Diário (a publicação sai logo depois da distribuição). Sem nenhum deles, a 1ª publicação conhecida (aproximada).
    Devolve (data AAAA-MM-DD, fonte: 'digitado' | 'cnj' | 'diario' | 'aproximada')."""
    man = ((lead.get("manual") or {}).get("data_ajuizamento") or {}).get("valor") or lead.get("ajuizada_em") or ""
    if re.match(r"\d{4}-\d{2}-\d{2}", str(man)):
        return str(man)[:10], "digitado"
    aj = (lead.get("cnj") or {}).get("ajuizado") or ""
    if aj:
        return aj[:10], "cnj"
    hist = lead.get("diario_hist") or {}
    if hist.get("distribuicao"):
        return hist["distribuicao"][:10], "diario"
    if sinal_guardado(lead) == "lista de distribuição" and lead.get("data_publicacao"):
        return str(lead["data_publicacao"])[:10], "diario"
    datas = [x for x in (hist.get("pub1"), (lead.get("cnj") or {}).get("pub1"), lead.get("data_publicacao")) if x]
    return (min(datas)[:10], "aproximada") if datas else ("", "")


def processo_novo(lead, hoje, limite_dias=30):
    """True = ajuizado há até `limite_dias` (decisão do dono: 30, o escritório muda em Destaques e exclusões); False = antigo;
    None = sem data nenhuma."""
    ref, _f = data_de_referencia(lead)
    if not ref:
        return None
    try:
        return (hoje - dt.date.fromisoformat(ref)).days <= int(limite_dias or 30)
    except ValueError:
        return None
