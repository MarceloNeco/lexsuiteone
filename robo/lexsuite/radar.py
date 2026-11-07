"""Radar SP: a lista do dia de ações novas contra empresas, qualificada sem IA.

Para cada tribunal do config (ex.: TRT2 e TRT15) o robô lê a lista de distribuição do dia
no DJEN, fica só com as ações contra pessoa jurídica, consulta a Receita quando há CNPJ e
monta uma linha por ação: empresa, porte, setor, cidade, valor (quando publicado ou digitado
por uma pessoa), vara e hora. O valor da causa que o Diário não traz fica atrás do captcha
do PJe: a página tem o botão "Abrir no PJe" e o campo para a pessoa digitar.
"""

import collections
import datetime as dt
import os
import time

from . import classificar as cl
from . import cnpj as receita
from . import compartilhar, djen, monitor, preferencias, saidas, saude, tribunais


class RoboDesligado(Exception):
    """O suporte desligou o robô, a validade acabou ou a versão instalada é velha demais (aba Controle)."""
GRANDES_GRUPOS = [  # nomes que quase sempre têm jurídico próprio (ficam no fim da lista, não somem)
    "MERCADO LIVRE", "MERCADOLIVRE", "AMAZON", "MAGAZINE LUIZA", "MAGALU", "AMERICANAS", "CARREFOUR", "ATACADAO",
    "GRUPO PAO DE ACUCAR", "COMPANHIA BRASILEIRA DE DISTRIBUICAO", "ASSAI", "VIA VAREJO", "CASAS BAHIA", "SHOPEE",
    "ITAU", "BRADESCO", "SANTANDER", "BANCO DO BRASIL", "CAIXA ECONOMICA", "VALE S", "PETROBRAS", "AMBEV",
    "JBS", "BRF", "GERDAU", "VIVO", "TELEFONICA", "CLARO", "TIM S", "NATURA", "RAIA DROGASIL", "LOCALIZA",
    "UBER", "IFOOD", "99 TECNOLOGIA", "CORREIOS", "GOL LINHAS", "LATAM", "AZUL LINHAS",
]


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


def item_de_lead(lead, cfg_radar):
    """Uma linha da lista do dia a partir de um lead do DJEN (só o que pode sair; nenhuma pessoa física do processo)."""
    emp = lead.get("empresa_receita") or {}
    nomes = lead.get("empresas") or []
    teto = float(cfg_radar.get("teto_capital_gigante") or 0)
    return {
        "id": lead.get("processo"),
        "hora": (lead.get("visto_em") or "")[11:16],
        "visto_em": lead.get("visto_em") or "",
        "tribunal": lead.get("tribunal"),
        "vara": lead.get("vara"),
        "processo": lead.get("processo"),
        "classe": lead.get("classe"),
        "rito": lead.get("rito"),
        "distribuida_em": lead.get("ajuizada_em") or lead.get("data_publicacao") or "",
        "diario_em": lead.get("data_publicacao") or "",
        "ajuizada_em": lead.get("ajuizada_em") or "",
        "empresas": nomes,
        "empresa": {
            "cnpj": emp.get("cnpj") or (lead.get("cnpjs") or [""])[0],
            "razao_social": emp.get("razao_social") or (nomes[0] if nomes else ""),
            "nome_fantasia": emp.get("nome_fantasia") or "",
            "porte": emp.get("porte") or "", "porte_legivel": porte_legivel(emp.get("porte")),
            "capital_social": emp.get("capital_social") or 0,
            "cnae": emp.get("cnae") or "", "atividade": emp.get("atividade") or "",
            "cnaes_secundarios": emp.get("cnaes_secundarios") or [],
            "municipio": emp.get("municipio") or "", "uf": emp.get("uf") or "",
            "telefone": emp.get("telefone") or "", "telefone2": emp.get("telefone2") or "", "email": emp.get("email") or "",
            "socios": emp.get("socios") or [], "simples": emp.get("simples"),
            "inicio_atividade": emp.get("inicio_atividade") or "",
        },
        "setor": cl.setor(nomes if not emp.get("atividade") else [emp.get("atividade", "")] + nomes),
        "gigante": gigante(emp, nomes, teto),
        "valor_causa": lead.get("valor_causa"),
        "valor_fonte": "djen" if lead.get("valor_causa") else "",
        "link_djen": lead.get("link") or "",
        "link_pje": link_pje(lead.get("tribunal")),
    }


def montar_radar(cfg, banco, agora=None, exemplo=False, situacao=None, dias=None, prefs=None):
    """Os dados da página: as ações guardadas nos últimos `dias` dias, dos tribunais escolhidos no config,
    com as preferências do escritório aplicadas (exclusões e mínimo de ações marcam, não apagam)."""
    r = cfg.get("radar") or {}
    agora = agora or dt.datetime.now()
    dias = int(dias if dias is not None else (r.get("dias_na_pagina") or 1))
    desde = (agora.date() - dt.timedelta(days=dias)).isoformat()
    escolhidos = tribunais.validar(r.get("tribunais") or ["TRT2", "TRT15"])
    prefs = prefs or preferencias.carregar(compartilhar.pasta_base(cfg))
    r = dict(r, teto_capital_gigante=prefs.get("teto_capital_gigante") or r.get("teto_capital_gigante"))
    itens = []
    for lead in banco.todos_leads(desde=desde):
        if lead.get("fonte", "DJEN") != "DJEN" or (lead.get("tribunal") or "").upper() not in escolhidos:
            continue
        item = item_de_lead(lead, r)
        if not prefs.get("mostrar_socios", True):
            item["empresa"]["socios"] = []  # minimização: nomes de pessoas só se o escritório pedir
        itens.append(item)
    # Quantas ações cada empresa teve na janela do "mínimo de ações" (conta processos distintos).
    contagem = None
    if int(prefs.get("minimo_acoes") or 1) > 1:
        janela = (agora.date() - dt.timedelta(days=int(prefs.get("janela_dias") or 30))).isoformat()
        vistos = collections.defaultdict(set)
        for lead in banco.todos_leads(desde=janela):
            for nome in lead.get("empresas") or []:
                vistos[cl.chave_nome(nome)].add(lead.get("processo"))
        contagem = {k: len(v) for k, v in vistos.items()}
    preferencias.aplicar(itens, prefs, contagem)
    itens.sort(key=lambda i: (-(i["valor_causa"] or 0), i["visto_em"]))
    dia = max([i["distribuida_em"][:10] for i in itens if i["distribuida_em"]] or [agora.date().isoformat()])
    return {
        "dia": dia, "gerado_em": agora.strftime("%Y-%m-%d %H:%M"), "exemplo": bool(exemplo), "dias": dias,
        "escritorio": cfg.get("escritorio", ""), "tribunais": escolhidos,
        "valor_minimo": float(prefs.get("valor_minimo") or r.get("valor_minimo") or 100000),
        "situacao": situacao or {}, "itens": itens,
        "excluidas": sum(1 for i in itens if i.get("excluida")),
        "prefs": {"esconder_excluidas": bool(prefs.get("esconder_excluidas", True)), "esconder_gigantes": bool(prefs.get("esconder_gigantes")),
                  "minimo_acoes": int(prefs.get("minimo_acoes") or 1), "janela_dias": int(prefs.get("janela_dias") or 30),
                  "origem": prefs.get("origem", "padrão"), "erro": prefs.get("erro", ""), "controle": prefs.get("controle") or {}},
    }


def executar(cfg, banco, aviso=print, pasta_base=None, dias=None, sem_cnpj=False, pasta_diag=None, agora=None, versao=""):
    """Uma rodada do radar: confere o controle do escritório, baixa o caderno de cada tribunal escolhido, separa as
    ações novas contra empresa, consulta a Receita quando há CNPJ, guarda, avalia a saúde, registra no log e grava
    a saída local e a planilha compartilhada. Devolve a situação. Pode levantar RoboDesligado e rede.BloqueadoForaDoBrasil."""
    versao = versao or _versao()
    r = cfg.get("radar") or {}
    escolhidos = tribunais.validar(r.get("tribunais") or ["TRT2", "TRT15"])
    dias = int(dias if dias is not None else r.get("dias_para_tras", 1))
    agora = agora or dt.datetime.now()
    inicio = time.perf_counter()
    base_compartilhada = compartilhar.pasta_base(cfg)
    if base_compartilhada:
        try:
            compartilhar.criar_se_faltar(cfg, versao, pasta_base or "", aviso)
        except OSError as e:
            aviso(f"  Não consegui criar a planilha ({e.__class__.__name__}); sigo com o padrão.")
    prefs = preferencias.carregar(base_compartilhada)
    if prefs.get("erro"):
        aviso("  " + prefs["erro"])
    motivo = preferencias.bloqueio(prefs, versao, agora.date())
    if motivo:
        banco.registrar("radar", {"versao": versao, "tribunais": escolhidos, "resultado": "não rodou", "erro": motivo})
        raise RoboDesligado(motivo)
    rodada_id = agora.strftime("%Y-%m-%dT%H:%M")
    aviso(f"Radar: lista de distribuição de {', '.join(escolhidos)} (últimos {dias} dia(s) úteis)")
    registro = {"versao": versao, "tribunais": escolhidos, "lidas": 0, "novas": 0, "com_cnpj": 0, "duracao": 0, "resultado": "", "erro": ""}
    try:
        lidos = []
        pubs = monitor.coletar_caderno(escolhidos, dias, banco, pasta_diag, aviso, lidos=lidos)
        ano_min = agora.year - 1 if agora.month <= 2 else agora.year
        novos = acoes_do_dia(pubs, ano_min, banco.processos_vistos())
        consultar = bool(r.get("receita", True)) and not sem_cnpj
        com_cnpj = sum(1 for n in novos if n.get("cnpjs"))
        if consultar and com_cnpj:
            aviso(f"  Consultando a Receita para {com_cnpj} empresa(s) com CNPJ no Diário...")
        feitas = falhas = 0
        for n in novos:
            n["rodada"], n["visto_em"] = rodada_id, agora.isoformat(timespec="seconds")
            if consultar and n.get("cnpjs"):
                dados = receita.consultar(n["cnpjs"][0], banco)
                feitas += 1
                if dados:
                    n["empresa_receita"] = dados
                else:
                    falhas += 1
                if feitas % 25 == 0:
                    aviso(f"  Receita: {feitas} de {com_cnpj}")
            banco.guardar_lead(n, agora.date().isoformat())
        monitor.guardar([], banco, lidos)
        detalhes = {}
        for n in novos:
            detalhes.setdefault(n.get("tribunal") or "?", {"processos": 0, "acoes": 0})["acoes"] += 1
        banco.registrar_rodada({"id": rodada_id, "quando": agora.isoformat(timespec="minutes"), "modo": "caderno",
                                "conferidas": len(pubs), "novas_processos": 0, "novas_acoes": len(novos), "detalhes": detalhes})
        saude.registrar(banco, saude.avaliar(pubs, novos, feitas, falhas, agora.date()), aviso)
        registro.update({"lidas": len(pubs), "novas": len(novos), "com_cnpj": com_cnpj, "resultado": "ok"})
    except Exception as e:
        registro.update({"resultado": "erro", "erro": f"{e.__class__.__name__}: {e}"[:300], "duracao": round(time.perf_counter() - inicio)})
        banco.registrar("radar", registro)
        raise
    registro["duracao"] = round(time.perf_counter() - inicio)
    banco.registrar("radar", registro)
    apagados = banco.limpar_antigos(int(r.get("guardar_dias") or 365))
    if apagados:
        aviso(f"  Retenção: {apagados} registro(s) com mais de {int(r.get('guardar_dias') or 365)} dias apagados.")
    situacao = {"pt": f"{len(pubs)} publicações lidas; {len(novos)} ações novas contra empresas; {com_cnpj} com CNPJ no Diário.",
                "en": f"{len(pubs)} notices read; {len(novos)} new lawsuits against companies; {com_cnpj} with a tax ID in the gazette.",
                "quando": agora.isoformat(timespec="minutes"), "tribunais": escolhidos, "lidas": len(pubs), "novas": len(novos), "com_cnpj": com_cnpj}
    aviso("  " + situacao["pt"])
    if pasta_base:
        pagina = gravar_saida(cfg, banco, os.path.join(pasta_base, "saida", "radar"), agora, situacao, aviso, versao, prefs)
        if base_compartilhada and (cfg.get("compartilhar") or {}).get("planilha", True):
            try:
                from . import atualizar, assinatura
                chave = atualizar.chave_publica(pasta_base)
                compartilhar.gravar_radar(cfg, pagina, banco, versao, COLUNAS_RADAR, linha_csv,
                                          assinatura.impressao(chave) if chave else "", pasta_base, aviso)
            except Exception as e:  # a pasta pode estar fora do ar (Drive pausado); a rodada em si deu certo
                aviso(f"  Não consegui gravar a planilha compartilhada ({e.__class__.__name__}: {e}).")
                banco.registrar("saude", {"fonte": "Pasta compartilhada", "situacao": "erro", "detalhe": f"{e.__class__.__name__}: {e}"[:200]})
    return situacao


def gravar_saida(cfg, banco, pasta, agora, situacao, aviso=print, versao="", prefs=None):
    """radar.html (abre sem internet), radar.json e radar.csv com a lista atual."""
    os.makedirs(pasta, exist_ok=True)
    pagina = montar_radar(cfg, banco, agora, False, situacao, prefs=prefs)
    pagina["versao"] = versao or _versao()
    saidas.gravar_radar(os.path.join(pasta, "radar.html"), pagina)
    saidas.gravar_json(os.path.join(pasta, "radar.json"), pagina)
    saidas.gravar_csv(os.path.join(pasta, "radar.csv"), [linha_csv(i) for i in pagina["itens"]], COLUNAS_RADAR)
    aviso(f"  {len(pagina['itens'])} ações na lista. Página: {os.path.join(pasta, 'radar.html')}")
    return pagina


def _versao():
    from . import VERSAO
    return VERSAO


def acoes_do_dia(pubs, ano_minimo, ja_vistos):
    """Ações novas contra empresa em todas as varas das publicações (lista de distribuição ou notificação inicial)."""
    return [l for l in djen.leads(pubs, vara=None, ano_minimo=ano_minimo, ja_vistos=ja_vistos) if l.get("sinal_de_acao_nova")]


COLUNAS_RADAR = [
    ("Hora", "hora"), ("Tribunal", "tribunal"), ("Vara", "vara"), ("Processo", "processo"), ("Rito", "rito"),
    ("Distribuída em", "distribuida_em"), ("Empresa(s)", "empresas"), ("CNPJ", "cnpj"), ("Porte", "porte_legivel"),
    ("Capital social", "capital_social"), ("CNAE", "atividade"), ("Setor", "setor"), ("Cidade/UF", "cidade_uf"),
    ("Telefone", "telefone"), ("E-mail", "email"), ("Sócios/administradores", "socios"), ("Provável jurídico próprio", "gigante"),
    ("Valor da causa", "valor_causa"), ("Origem do valor", "valor_fonte"), ("Link DJEN", "link_djen"), ("Consulta PJe", "link_pje"),
]


def linha_csv(item):
    e = item["empresa"]
    return {
        **item, "cnpj": e["cnpj"], "porte_legivel": e["porte_legivel"], "capital_social": e["capital_social"],
        "atividade": e["atividade"], "cidade_uf": f"{e['municipio']}/{e['uf']}" if e["municipio"] else "",
        "telefone": e["telefone"], "email": e["email"], "socios": [s.get("nome", "") for s in e["socios"]],
        "gigante": "sim" if item["gigante"] else "",
    }
