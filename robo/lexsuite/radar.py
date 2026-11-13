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
        "contato": _contato_resumo(emp, extras, bool(emp.get("cnpj")), a_conferir),
        "contatos": [{k: c[k] for k in ("canal", "valor", "fonte", "data", "confianca", "origem", "de_pessoa", "validacao")} for c in extras],
        "cnpj_a_conferir": a_conferir,
        "id": lead.get("processo"),
        "hora": (lead.get("visto_em") or "")[11:16],
        "visto_em": lead.get("visto_em") or "",
        "tribunal": lead.get("tribunal"),
        "vara": lead.get("vara"),
        "sinal": lead.get("sinal") or sinal_guardado(lead),  # 0.7.19: como a ação nova foi reconhecida (gráfico para calibrar a regra com o escritório)
        "processo": lead.get("processo"),
        "classe": (lead.get("classe") or "").upper(),  # 0.7.16: o Diário às vezes traz "AçãO ... ORDINáRIO"
        "rito": lead.get("rito"),
        "distribuida_em": lead.get("ajuizada_em") or lead.get("data_publicacao") or "",
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
    itens.sort(key=lambda i: (-(i["valor_causa"] or 0), i["visto_em"]))
    dia = max([i["distribuida_em"][:10] for i in itens if i["distribuida_em"]] or [agora.date().isoformat()])
    return {
        "dia": dia, "gerado_em": agora.strftime("%Y-%m-%d %H:%M"), "exemplo": bool(exemplo), "dias": dias,
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


def registrar_tentativas(banco, tentativas, origem, versao, quando=None):
    """Histórico de leituras (0.7.13): uma linha por tribunal, com a hora local e o fuso, a origem, o que foi pedido,
    a resposta, a causa e o que o programa fez. Sem dado pessoal."""
    quando = quando or dt.datetime.now().astimezone().isoformat(timespec="seconds")
    for t in tentativas:
        banco.registrar("tentativa", dict(t, quando_local=quando, origem=origem, versao=versao))


def executar(cfg, banco, aviso=print, pasta_base=None, dias=None, sem_cnpj=False, pasta_diag=None, agora=None, versao="",
             caminho_config=None, origem="botão", parar=None):
    """Uma rodada do radar: confere o controle do escritório, baixa o caderno de cada tribunal escolhido, separa as
    ações novas contra empresa, consulta a Receita quando há CNPJ, guarda, avalia a saúde, registra no log e grava
    a saída local e a planilha compartilhada. Devolve a situação. Pode levantar RoboDesligado e rede.BloqueadoForaDoBrasil."""
    versao = versao or _versao()
    r = cfg.get("radar") or {}
    escolhidos = tribunais.validar(r.get("tribunais") or ["TRT2", "TRT15"])
    dias = config.inteiro(dias if dias is not None else r.get("dias_para_tras", 1), 1, 0, 10)
    agora = agora or dt.datetime.now()
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
    try:
        lidos = []
        try:
            pubs = monitor.coletar_caderno(escolhidos, dias, banco, pasta_diag, aviso, lidos=lidos, tentativas=tentativas, parar=parar)
        finally:
            try:
                registrar_tentativas(banco, tentativas, origem, versao)
            except Exception as e:  # noqa: BLE001 - o histórico nunca esconde o erro da leitura
                aviso(f"  Não consegui gravar o histórico de leituras ({e.__class__.__name__}).")
        ano_min = agora.year - 1 if agora.month <= 2 else agora.year
        if not banco.execucoes("criterio", 1):  # 0.7.17: data em que o critério de "ação nova" mudou (estatísticas antes e depois não se comparam)
            banco.registrar("criterio", {"desde": CRITERIO_DESDE, "versao": versao or _versao(), "regra": CRITERIO_REGRA})
        novos = acoes_do_dia(pubs, ano_min, banco.processos_vistos())
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
    try:
        banco.atualizar_estatisticas()  # 0.7.14: totais diários que nunca se apagam
    except Exception as e:  # noqa: BLE001 - estatística nunca derruba a leitura
        aviso(f"  Não consegui atualizar as estatísticas ({e.__class__.__name__}).")
    apagados = banco.limpar_antigos(int(r.get("guardar_dias") or 365))
    try:  # 0.7.17 (decisão 14): banco acima de 1 GB resume com 6 meses só os processos nunca abertos
        if banco.espaco()["bytes"] > 1024 ** 3:
            resumidos = banco.limpar_detalhe(6, perfil="automático", so_nunca_abertos=True)
            if resumidos:
                banco.compactar()
                aviso(f"  O banco do programa passou de 1 GB: {resumidos} processo(s) nunca aberto(s) com mais de 6 meses ficaram só com o resumo.")
                banco.registrar("saude", {"fonte": "Banco do programa", "situacao": "atenção", "detalhe": f"acima de 1 GB: {resumidos} resumidos (6 meses, nunca abertos)"})
    except Exception as e:  # noqa: BLE001 - a retenção nunca derruba a leitura
        aviso(f"  Não consegui resumir o banco ({e.__class__.__name__}).")
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
                "en": f"{pubs_en}; {proc_en} against companies; {com_cnpj} with a tax ID in the gazette{parcial_en}.",
                "quando": agora.isoformat(timespec="minutes"), "tribunais": escolhidos, "lidas": len(pubs), "novas": len(novos), "com_cnpj": com_cnpj}
    if tentativas and not pubs and not interrompida and all(t["causa"] in ("ok", "ainda_nao_liberado_3h", "nao_publicado") for t in tentativas):
        # 0.7.36 (dono): "0 publicações lidas" parecia falha; quando nada é novo, a tela diz por quê
        ate = max((str(t.get("leu_ate") or "")[:10] for t in tentativas), default="")
        ate_br, ate_en = (config.data_curta(ate, ano=False), config.data_curta(ate, ano=False, en=True)) if len(ate) == 10 else ("", "")
        # revisão da Operação: sem prometer horário (o DJEN libera o Diário de hoje em horários diferentes); a próxima leitura pega
        situacao["pt"] = (f"Nada novo: os cadernos até {ate_br} já tinham sido lidos." if ate_br else "Nada novo: os Diários já publicados tinham sido lidos.") + \
            " O Diário de hoje entra na próxima leitura, quando estiver liberado."
        situacao["en"] = (f"Nothing new: the issues up to {ate_en} had already been read." if ate_en else "Nothing new: the gazettes already published had been read.") + \
            " Today's gazette comes in the next reading, once released."
        situacao["nada_novo"] = True
    from . import causas
    for t in tentativas:  # avisos que não são erro (Diário de hoje só às 3h) e tribunais que falharam
        if t["causa"] == "ok":
            continue
        situacao.setdefault("avisos", []).append({
            "tribunal": t["tribunal"], "causa": t["causa"], "aviso": causas.e_aviso(t["causa"]), "leu_ate": t.get("leu_ate", ""),
            "pt": f"{t['tribunal']}: {causas.mensagem(t['causa'], 'pt')}", "en": f"{t['tribunal']}: {causas.mensagem(t['causa'], 'en')}"})
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


def gravar_planilha(cfg, pagina, banco, versao, pasta_base, aviso=print):
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
        todos = [i for i in montar_radar(cfg, banco, visao="arquivo")["itens"] if (i.get("primeira_vez") or "9") >= doze]
        lista = pagina.get("itens") or []
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
                                                processos=processos, criterios=prefs)
            if not caminho:  # planilha em uso ou ilegível: gravar_radar já avisou e não regravou nada
                tudo_ok = False
                continue
            try:
                tamanho = os.path.getsize(caminho)
            except OSError:
                tamanho = 0
            banco.registrar("planilha", {"frente": frente, "linhas": linhas, "limite": limite, "bytes": tamanho,
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
    ("Distribuída em", "distribuida_em"), ("Empresa(s)", "empresas"), ("CNPJ", "cnpj"), ("Porte", "porte_legivel"),
    ("Capital social", "capital_social"), ("CNAE", "atividade"), ("Setor", "setor"), ("Cidade/UF", "cidade_uf"),
    ("Telefone", "telefone"), ("E-mail", "email"), ("Endereço", "endereco"), ("CEP", "cep"), ("Outros contatos", "outros_contatos"), ("Sócios/administradores", "socios"), ("Provável jurídico próprio", "gigante"),
    ("Valor da causa", "valor_causa"), ("Origem do valor", "valor_fonte"), ("Link DJEN", "link_djen"), ("Consulta PJe", "link_pje"),
]


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
    }


SITUACAO_LEGIVEL = {"novo": "Novo", "visto": "Visto", "em_analise": "Em análise", "em_contato": "Em contato",
                    "virou_cliente": "Virou cliente", "descartado": "Descartado", "arquivado": "Arquivado"}
FRENTE_LEGIVEL = {"trabalhista": "Trabalhista", "tributario": "Tributário", "civel": "Cível", "empresarial": "Empresarial"}


def endereco(e):
    rua = ", ".join(x for x in (e.get("logradouro", ""), e.get("numero", "")) if x)
    partes = [rua + (f" {e['complemento']}" if e.get("complemento") else ""), e.get("bairro", ""),
              "/".join(x for x in (e.get("municipio", ""), e.get("uf", "")) if x)]
    return " - ".join(x for x in partes if x)
