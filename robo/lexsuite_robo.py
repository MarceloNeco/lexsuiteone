"""LexSuiteONE · JUDICIAL — robô de linha de comando.

Exemplos (no PowerShell do Windows, dentro desta pasta):
  python lexsuite_robo.py varas --tribunal TRT2
  python lexsuite_robo.py vara  --tribunal TRT2 --vara "Vara do Trabalho de Cajamar"
  python lexsuite_robo.py djen  --tribunal TRT2 --vara "Vara do Trabalho de Cajamar" --dias 3
  python lexsuite_robo.py pauta --tribunal TRT2 --vara "Vara do Trabalho de Cajamar" --dias 10
  python lexsuite_robo.py tudo  --config config.json
  python lexsuite_robo.py monitor              (publicações dos processos do escritório; rodar à noite)
  python lexsuite_robo.py monitor --caderno    (varredura completa pelo caderno do dia; rodar de manhã)
  python lexsuite_robo.py app                  (tela no navegador: tribunais, rodar, lista)
  python lexsuite_robo.py radar                (uma rodada sem tela, para agendar)

Nada aqui usa IA: só dados públicos do CNJ e regras escritas. Não gasta token.
"""

import argparse
import collections
import datetime as dt
import json
import os
import re
import sys

from lexsuite import VERSAO, avisar, banco as bd, cnpj, classificar as cl, config, datajud, djen, monitor, pauta, prazos, radar, rede, saidas

AQUI = os.path.dirname(os.path.abspath(__file__))


CONFIG_PADRAO = config.PADRAO


def carregar_config(caminho):
    """Lê o config.json (cria na primeira vez). Ver lexsuite/config.py."""
    return config.carregar(caminho)


def pasta_saida(tribunal, vara):
    nome = re.sub(r"[^a-z0-9]+", "-", cl.sem_acento(f"{tribunal} {vara}").lower()).strip("-")
    caminho = os.path.join(AQUI, "saida", nome)
    os.makedirs(caminho, exist_ok=True)
    return caminho


def cmd_varas(a):
    fim = dt.date.today()
    inicio = fim - dt.timedelta(days=30 * a.meses)
    print(f"Varas do {a.tribunal} com mais ações distribuídas ({inicio:%d/%m/%Y} a {fim:%d/%m/%Y}, DataJud):")
    for nome, qtd in datajud.listar_varas(a.tribunal, inicio, fim, a.quantas):
        print(f"  {qtd:6d}  {nome}")


def estatistica_vara(tribunal, vara, meses, cache=None):
    """Baixa (ou lê do cache) os processos da vara e devolve o raio-x."""
    if cache and os.path.exists(cache):
        docs = json.load(open(cache, encoding="utf-8"))
    else:
        hoje = dt.date.today()
        docs = datajud.processos_da_vara(tribunal, vara, hoje - dt.timedelta(days=31 * (meses + 3)), hoje)
        if cache:
            json.dump(docs, open(cache, "w", encoding="utf-8"), ensure_ascii=False)
    if not docs:
        raise SystemExit(f"Nenhum processo achado para '{vara}' no {tribunal}. Confira o nome com o comando 'varas'.")
    # O DataJud chega atrasado: o período termina no último ajuizamento que já está na base.
    ultima = max(d for d in (datajud.ler_data(x.get("dataAjuizamento")) for x in docs) if d)
    inicio = dt.date(ultima.year, ultima.month, 1)
    for _ in range(meses - 1):
        inicio = (inicio - dt.timedelta(days=1)).replace(day=1)
    dentro = [x for x in docs if (datajud.ler_data(x.get("dataAjuizamento")) or ultima) >= inicio]
    mapa = {datajud.numero_cnj(x.get("numeroProcesso")): str(datajud.ler_data(x.get("dataAjuizamento")) or "")
            for x in docs}
    return datajud.estatisticas(dentro, tribunal, vara, inicio, ultima), mapa


def cmd_vara(a):
    print(f"Raio-x da {a.vara} ({a.tribunal}) pelo DataJud...")
    stats, mapa = estatistica_vara(a.tribunal, a.vara, a.meses, a.cache)
    pasta = pasta_saida(a.tribunal, a.vara)
    saidas.gravar_json(os.path.join(pasta, "vara_stats.json"), stats)
    # Guardado à parte (não vai para o painel): serve para dizer quando cada ação entrou.
    saidas.gravar_json(os.path.join(pasta, "ajuizamentos.json"), mapa)
    gerar_entregas(pasta, stats, None, {"pt": "A lista de ações ainda não rodou para esta vara.",
                                        "en": "The lawsuit list has not run for this court yet."})
    print(f"  {stats['total']} processos de {stats['periodo']['inicio']} a {stats['periodo']['fim']}.")
    print(f"  Pronto: {pasta}")


def coletar_djen(tribunal, dias, orgao_id, diagnostico, modo="caderno"):
    """Publicações do DJEN dos últimos `dias`. Caderno = 1 arquivo por dia útil (padrão, mais leve)."""
    hoje = dt.date.today()
    pasta_diag = os.path.join(AQUI, "diagnostico") if diagnostico else None
    if modo == "busca":
        return djen.buscar(tribunal, (hoje - dt.timedelta(days=dias)).isoformat(), hoje.isoformat(),
                           orgao_id, diagnostico=pasta_diag)
    pubs = []
    for i in range(dias, -1, -1):
        d = hoje - dt.timedelta(days=i)
        if d.weekday() < 5:
            pubs += djen.baixar_caderno(tribunal, d.isoformat(), pasta_diag) or []
    return pubs


def _quando(l):
    return l.get("data_publicacao") or (l.get("audiencia") or {}).get("data") or l.get("primeira_vez") or ""


def datar(leads, pasta):
    """Data de ajuizamento pelo DataJud; o que é mais novo que a base (atraso do CNJ) é marcado como recente."""
    caminho = os.path.join(pasta, "ajuizamentos.json")
    if not os.path.exists(caminho):
        return
    mapa = json.load(open(caminho, encoding="utf-8"))
    ultima = max(mapa.values()) if mapa else ""
    maior_seq = max((int(n[:7]) for n in mapa if n[9:13] == ultima[:4]), default=0) if ultima else 0
    for l in leads:
        if l["processo"] in mapa:
            l["ajuizada_em"] = mapa[l["processo"]]
        elif ultima and l["processo"][9:13] == ultima[:4] and int(l["processo"][:7]) > maior_seq:
            # número sequencial maior que o último da base = ação entrou depois dessa data
            l["ajuizada_em"] = "após " + ultima


def processar_leads(novos, vara, banco, enriquecer, carteira=None, so_carteira=False, pasta=None):
    """Guarda os novos, junta com os anteriores e recalcula carteira, recorrência e nota de todos."""
    for lead in novos:
        if enriquecer and lead.get("cnpjs"):
            lead["empresa_receita"] = cnpj.consultar(lead["cnpjs"][0], banco)
        banco.guardar_lead(lead, (lead.get("visto_em") or "")[:10] or None)
    todos = banco.todos_leads(vara)
    if pasta:
        datar(todos, pasta)
    monitor.pontuar(todos, carteira)
    if so_carteira:
        # Modo recomendado (OAB): só alertas de clientes atuais.
        todos = [l for l in todos if l["cliente"]]
    return todos


def gerar_entregas(pasta, stats, leads, situacao_djen):
    painel = {
        "versao": VERSAO,
        "gerado_em": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "vara_stats": stats,
        "leads": [saidas.lead_para_saida(l) for l in (leads or [])],
        "djen": situacao_djen,
    }
    saidas.gravar_painel(os.path.join(pasta, "painel.html"), painel)
    saidas.gravar_json(os.path.join(pasta, "dados.json"), painel)
    if stats:
        saidas.gravar_csv(os.path.join(pasta, "acoes_recentes_datajud.csv"), stats["recentes"], saidas.COLUNAS_RECENTES)
    if leads is not None:
        saidas.gravar_csv(os.path.join(pasta, "leads.csv"), painel["leads"], saidas.COLUNAS_LEADS)
    return painel


def cmd_djen(a, cfg_email=None):
    pasta = pasta_saida(a.tribunal, a.vara)
    banco = bd.Banco(os.path.join(AQUI, "lexsuite.db"))
    caminho_stats = os.path.join(pasta, "vara_stats.json")
    stats = json.load(open(caminho_stats, encoding="utf-8")) if os.path.exists(caminho_stats) else None
    try:
        pubs = coletar_djen(a.tribunal, a.dias, a.orgao_id, a.diagnostico, a.modo)
        hoje = dt.date.today()
        novos = djen.leads(pubs, vara=a.vara, ano_minimo=hoje.year - 1 if hoje.month <= 2 else hoje.year,
                           ja_vistos=banco.processos_vistos())
        leads = processar_leads(novos, a.vara, banco, not a.sem_cnpj, a.carteira, a.so_carteira, pasta)
        situacao = {"pt": f"Fonte: DJEN. {len(pubs)} publicações lidas, {len(novos)} ações novas contra empresas nesta rodada.",
                    "en": f"Source: DJEN. {len(pubs)} notices read, {len(novos)} new lawsuits against companies in this run."}
    except rede.BloqueadoForaDoBrasil as e:
        print("  " + str(e))
        leads = processar_leads([], a.vara, banco, False, a.carteira, a.so_carteira, pasta)
        situacao = {"pt": str(e), "en": "DJEN only answers computers in Brazil. Run the robot on a computer or server in Brazil.",
                    "bloqueado": True}
    situacao["carteira"] = bool(a.so_carteira)
    painel = gerar_entregas(pasta, stats, leads, situacao)
    banco.registrar("djen", {"vara": a.vara, "situacao": situacao})
    print("  " + situacao["pt"])
    print(f"  Pronto: {pasta}")
    if cfg_email:
        print("  " + avisar.enviar(cfg_email, f"LexSuiteONE: {len(painel['leads'])} leads — {a.vara}",
                                   avisar.resumo_html(painel), [os.path.join(pasta, "leads.csv")]))


def cmd_pauta(a):
    """Degustação/conferência: ações com primeira audiência marcada nos próximos dias úteis."""
    pasta = pasta_saida(a.tribunal, a.vara)
    banco = bd.Banco(os.path.join(AQUI, "lexsuite.db"))
    caminho_stats = os.path.join(pasta, "vara_stats.json")
    stats = json.load(open(caminho_stats, encoding="utf-8")) if os.path.exists(caminho_stats) else None
    print(f"Pauta pública de audiências da {a.vara} ({a.tribunal})...")
    novos = pauta.leads_da_pauta(a.tribunal, a.vara, a.dias)
    novos = [l for l in novos if l["processo"] not in banco.processos_vistos()]
    leads = processar_leads(novos, a.vara, banco, False, a.carteira, a.so_carteira, pasta)
    total = len(leads)
    situacao = {
        "pt": (f"Fonte desta lista: pauta pública de audiências do PJe. São {total} ações contra empresas com "
               f"audiência Una ou Inicial marcada nos próximos {a.dias} dias úteis; a coluna Quando mostra também "
               "a data de ajuizamento. Para receber a ação no dia em que entra, o robô lê o DJEN (roda no Brasil)."),
        "en": (f"Source of this list: the public PJe hearing schedule. {total} lawsuits against companies with a first "
               f"hearing in the next {a.dias} business days; the When column also shows the filing date. To get each "
               "lawsuit on the day it is filed, the robot reads DJEN (runs in Brazil)."),
    }
    situacao["carteira"] = bool(a.so_carteira)
    gerar_entregas(pasta, stats, leads, situacao)
    banco.registrar("pauta", {"vara": a.vara, "novos": len(novos)})
    print("  " + situacao["pt"])
    print(f"  Pronto: {pasta}")


def cmd_tudo(a):
    cfg = carregar_config(a.config)
    for alvo in cfg["alvos"]:
        args = argparse.Namespace(tribunal=alvo["tribunal"], vara=alvo["vara"], orgao_id=alvo.get("orgao_id"),
                                  dias=cfg.get("dias_djen", 3), meses=cfg.get("meses_estatistica", 12),
                                  cache=None, sem_cnpj=not cfg.get("enriquecer_cnpj", True), diagnostico=False,
                                  carteira=os.path.join(AQUI, cfg.get("carteira", "carteira.csv")),
                                  so_carteira=cfg.get("modo", "carteira") == "carteira",
                                  modo=cfg.get("djen_modo", "caderno"))
        stats_arq = os.path.join(pasta_saida(args.tribunal, args.vara), "vara_stats.json")
        velho = (not os.path.exists(stats_arq) or
                 (dt.datetime.now().timestamp() - os.path.getmtime(stats_arq)) / 86400 >= cfg.get("atualizar_estatistica_a_cada_dias", 7))
        if velho:
            cmd_vara(args)
        cmd_djen(args, cfg.get("email"))


def _dia_util_atras(n, base=None):
    """Data n dias úteis antes de hoje (0 = hoje, mesmo que seja fim de semana)."""
    d = base or dt.date.today()
    for _ in range(int(n)):
        d -= dt.timedelta(days=1)
        while not prazos.dia_util(d):
            d -= dt.timedelta(days=1)
    return d


def _carregar_exemplo():
    """Lê exemplos/dia_exemplo.json (gera, se faltar) e converte as datas relativas em datas reais."""
    caminho = os.path.join(AQUI, "exemplos", "dia_exemplo.json")
    if not os.path.exists(caminho):
        import runpy
        runpy.run_path(os.path.join(AQUI, "exemplos", "gerar_dia_exemplo.py"), run_name="__main__")
    with open(caminho, encoding="utf-8") as f:
        doc = json.load(f)
    for rod in doc["rodadas"]:
        dia = _dia_util_atras(rod.pop("dias_uteis_atras", 0))
        rod["quando"] = f"{dia.isoformat()}T{rod.pop('hora', '19:15')}"
        for it in rod["items"]:
            it["data_disponibilizacao"] = _dia_util_atras(it.pop("dias_uteis_atras", 0)).isoformat()
    return doc


def _avisar_monitor(cfg, novas):
    """Manda os avisos. Devolve (algum_canal_ligado, algum_aviso_saiu, recados)."""
    m = cfg.get("monitor") or {}
    com_trecho = m.get("trecho_no_aviso", True)
    canais, saiu, recados = 0, False, []
    tg = m.get("telegram") or {}
    if tg.get("ativo"):
        canais += 1
        enviadas, recado = avisar.telegram(tg, avisar.agrupar([avisar.texto_telegram(i, com_trecho) for i in novas]))
        saiu, recados = saiu or enviadas > 0, recados + [recado]
    email = cfg.get("email") or {}
    if email.get("ativo"):
        canais += 1
        urg = sum(1 for i in novas if i["urgencia"] == "Urgente")
        assunto = f"LexSuiteONE: {len(novas)} publicação(ões) nova(s)" + (f" — {urg} urgente(s)" if urg else "")
        try:
            recado = avisar.enviar(email, assunto, avisar.monitor_html(novas, com_trecho))
        except Exception as e:  # e-mail fora do ar não pode derrubar a rodada
            recado = f"E-mail não enviado ({e.__class__.__name__})."
        saiu, recados = saiu or recado.startswith("E-mail enviado"), recados + [recado]
    return canais > 0, saiu, recados


def _rodada(cfg, banco, a, carteira, processos, pasta_diag, exemplo_rodada=None):
    """Uma rodada completa: nossos processos + radar das varas + registro. Devolve a situação."""
    m = cfg.get("monitor") or {}
    agora = dt.datetime.fromisoformat(exemplo_rodada["quando"]) if exemplo_rodada else dt.datetime.now()
    rodada_id = agora.strftime("%Y-%m-%dT%H:%M")
    modo = exemplo_rodada["modo"] if exemplo_rodada else ("caderno" if a.caderno else "api")
    pubs_exemplo = [djen.normalizar(i) for i in exemplo_rodada["items"]] if exemplo_rodada else None
    print(f"Rodada {agora:%d/%m %H:%M} ({'caderno do dia' if modo == 'caderno' else 'busca filtrada'})"
          + (" — EXEMPLO FICTÍCIO" if exemplo_rodada else ""))

    # 1) Nossos processos (OAB, números, clientes)
    try:
        novas, situacao, cadernos = monitor.rodar(cfg, banco, modo, a.dias, pasta_diag, print, carteira, processos,
                                                  publicacoes=pubs_exemplo)
    except rede.BloqueadoForaDoBrasil as e:
        print("  " + str(e))
        return {"pt": str(e), "en": "DJEN only answers computers in Brazil.", "bloqueado": True}
    guardar = True
    if novas and not a.sem_aviso and not exemplo_rodada:
        ligado, saiu, recados = _avisar_monitor(cfg, novas)
        for r in recados:
            print("  " + r)
        if ligado and not saiu:
            print("  Nenhum aviso saiu; estas publicações serão avisadas na próxima rodada.")
            guardar = False
    if guardar:
        monitor.guardar(novas, banco, cadernos, rodada=rodada_id, visto_em=agora.isoformat(timespec="seconds"))

    # 2) Radar: ações novas contra empresas nas varas acompanhadas
    novos_acoes, conferidas_radar = [], 0
    if m.get("radar", True) and cfg.get("alvos") and modo != "caderno" or (exemplo_rodada and cfg.get("alvos")):
        varas = monitor.varas_alvo(cfg, AQUI)
        if pubs_exemplo is not None:
            pubs = pubs_exemplo
        else:
            hoje = agora.date()
            pubs = monitor.coletar_radar(varas, (hoje - dt.timedelta(days=int(m.get("dias_para_tras", 3)))).isoformat(),
                                         hoje.isoformat(), pasta_diag, print)
            conferidas_radar = len(pubs)
        ano_min = agora.year - 1 if agora.month <= 2 else agora.year
        novos_acoes = monitor.acoes_novas(pubs, varas, banco.processos_vistos(), ano_min)
        for n in novos_acoes:
            n["rodada"], n["visto_em"] = rodada_id, agora.isoformat(timespec="seconds")
        processar_leads(novos_acoes, None, banco, cfg.get("enriquecer_cnpj", True) and not a.sem_cnpj, carteira, False, None)

    # 3) Registro da rodada (é o que desenha a linha do tempo da página)
    detalhes = {}
    for n in novas:
        detalhes.setdefault(n.get("tribunal") or "?", {"processos": 0, "acoes": 0})["processos"] += 1
    for n in novos_acoes:
        detalhes.setdefault(n.get("tribunal") or "?", {"processos": 0, "acoes": 0})["acoes"] += 1
    conferidas = len(pubs_exemplo) if pubs_exemplo is not None else int(situacao.get("conferidas") or 0) + conferidas_radar
    banco.registrar_rodada({"id": rodada_id, "quando": agora.isoformat(timespec="minutes"), "modo": modo,
                            "conferidas": conferidas, "novas_processos": len(novas), "novas_acoes": len(novos_acoes),
                            "detalhes": detalhes})
    situacao = {"pt": f"{conferidas} publicações conferidas; {len(novas)} novas nos nossos processos; "
                      f"{len(novos_acoes)} ações novas nas varas acompanhadas.",
                "en": f"{conferidas} notices checked; {len(novas)} new in our cases; "
                      f"{len(novos_acoes)} new lawsuits in the watched courts."}
    print("  " + situacao["pt"])
    for i in novas[:8]:
        venc = f" · vence ~{i['vencimento']}" if i.get("vencimento") else ""
        print(f"   [{i['urgencia']}] {i['ato']} · {i['processo']} · {i.get('cliente') or ''}{venc}")
    return situacao


def cmd_monitor(a):
    if a.descobrir_chat:
        chats, erro = avisar.descobrir_chats()
        if chats is None:
            raise SystemExit("  " + erro)
        if not chats:
            print("  Nenhuma conversa ainda. Ponha o bot no grupo, mande /start no grupo e rode de novo.")
        for cid, nome in chats.items():
            print(f"  chat_id: {cid}   ({nome})")
        return

    exemplo = None
    if a.exemplo:
        exemplo = _carregar_exemplo()
        cfg = exemplo["config"]
        caminho_db = os.path.join(AQUI, "lexsuite_exemplo.db")
        if os.path.exists(caminho_db):
            os.remove(caminho_db)  # a demonstração sempre recomeça do zero
        banco = bd.Banco(caminho_db)
        pasta = os.path.join(AQUI, "saida", "dia-exemplo")
        os.makedirs(pasta, exist_ok=True)
        carteira = os.path.join(pasta, "carteira_exemplo.csv")
        processos = os.path.join(pasta, "processos_exemplo.csv")
        with open(carteira, "w", encoding="utf-8") as f:
            f.write("cnpj;nome\n" + "".join(f";{n}\n" for n in exemplo["carteira"]))
        with open(processos, "w", encoding="utf-8") as f:
            f.write("processo;cliente;responsavel\n" + "".join(";".join(l) + "\n" for l in exemplo["processos"]))
    else:
        cfg = carregar_config(a.config)
        banco = bd.Banco(os.path.join(AQUI, "lexsuite.db"))
        pasta = os.path.join(AQUI, "saida", "monitor")
        os.makedirs(pasta, exist_ok=True)
        m = cfg.get("monitor") or {}
        carteira = os.path.join(AQUI, cfg.get("carteira", "carteira.csv"))
        processos = os.path.join(AQUI, m.get("processos", "processos.csv"))

    if a.teste_aviso:
        modelo = _carregar_exemplo()["rodadas"][0]["items"][-1]
        item = monitor.preparar(djen.normalizar(modelo), ["Mensagem de teste"], "Cliente Exemplo", "")
        item["ato"] = "TESTE — " + item["ato"]
        ligado, saiu, recados = _avisar_monitor(cfg, [item])
        for r in recados or ["Nenhum aviso ligado no config.json (telegram.ativo ou email.ativo)."]:
            print("  " + r)
        return

    pasta_diag = os.path.join(AQUI, "diagnostico") if a.diagnostico else None
    situacao = None
    for rod in (exemplo["rodadas"] if exemplo else [None]):
        situacao = _rodada(cfg, banco, a, carteira, processos, pasta_diag, rod)

    agora = dt.datetime.fromisoformat(exemplo["rodadas"][-1]["quando"]) if exemplo else dt.datetime.now()
    pagina = monitor.montar_pagina(cfg, banco, int((cfg.get("monitor") or {}).get("dias_na_pagina", 7)), bool(exemplo),
                                   situacao, agora, cfg.get("escritorio", ""), carteira)
    pagina["versao"] = VERSAO
    saidas.gravar_monitor(os.path.join(pasta, "dia.html"), pagina)
    saidas.gravar_json(os.path.join(pasta, "dia.json"), pagina)
    saidas.gravar_csv(os.path.join(pasta, "publicacoes.csv"), pagina["processos"], saidas.COLUNAS_MONITOR)
    saidas.gravar_csv(os.path.join(pasta, "acoes_novas.csv"), pagina["acoes"], saidas.COLUNAS_LEADS)
    banco.registrar("monitor", {"situacao": situacao})
    print(f"  Página do dia: {os.path.join(pasta, 'dia.html')}")


def cmd_radar(a):
    """Radar sem tela: uma rodada nos tribunais do config.json (serve para o Agendador de Tarefas)."""
    cfg = carregar_config(a.config)
    banco = bd.Banco(os.path.join(AQUI, "lexsuite.db"))
    pasta_diag = os.path.join(AQUI, "diagnostico") if a.diagnostico else None
    from lexsuite import agendar as _ag, app as _app
    arquivo = os.path.join(AQUI, "saida", "leitura.json")
    if _app.leitura_em_outro_processo(arquivo):  # 0.7.14: não roda duas leituras ao mesmo tempo
        print("  Já há uma leitura em andamento neste computador (pela tela ou agendada). Esta não roda.", flush=True)
        return
    origem = _ag.origem_da_leitura(cfg) if getattr(a, "agendado", False) else "à mão (RODAR.bat)"
    estado = _app.Estado(eco=lambda linha: print(linha, flush=True), arquivo=arquivo, origem=origem)
    if estado.origem == "fora do horário":  # 0.7.15: qual horário foi perdido (computador desligado ou em repouso)
        ultimas = [x for x in banco.execucoes("radar", 20) if x.get("resultado") != "não rodou"]  # tentativa barrada não conta
        estado.atrasada = _ag.horario_perdido(cfg, ultima_leitura=ultimas[0]["quando"] if ultimas else "")
        if estado.atrasada:
            print(f"  Fazendo agora a leitura das {estado.atrasada}, que não rodou na hora (computador desligado ou em repouso).", flush=True)
    estado.comecar()
    try:
        com_hora = estado.aviso  # janela preta com a hora e andamento para a tela (barra de progresso)
        situacao = radar.executar(cfg, banco, com_hora, AQUI, dias=a.dias, sem_cnpj=a.sem_cnpj, pasta_diag=pasta_diag, versao=VERSAO,
                                  caminho_config=a.config, origem=estado.origem, parar=estado.parar)
        if getattr(a, "agendado", False):  # 0.7.18: à noite, depois da leitura agendada, até 30 Diários antigos (só totais)
            try:  # antes de terminar o estado: a tela vê a leitura "rodando" e não inicia outra ao mesmo tempo (revisão)
                from lexsuite import historico
                hora = dt.datetime.now().hour
                sit_h = historico.situacao(banco)
                if (hora >= 18 or hora < 7) and (sit_h["na_fila"] or sit_h["erros"]):
                    historico.processar(banco, limite=int(cfg["radar"].get("estatisticas_por_vez") or historico.POR_VEZ),
                                        aviso=estado.aviso, parar=estado.parar)  # estado.aviso mantém a batida de leitura.json
            except Exception as e:  # noqa: BLE001 - as estatísticas antigas nunca atrapalham a leitura
                print(f"  Estatísticas antigas: não deu certo agora ({e.__class__.__name__}); tento na próxima noite. / Will retry next night.", flush=True)
        estado.terminar(situacao)
        if cfg["radar"].get("avisar_ao_terminar", True):
            from lexsuite import agendar, app
            m = app.marca(AQUI)
            agendar.notificar(m.get("nome", "RADAR JUDICIAL"), agendar.texto_aviso(situacao, m.get("curto", "RADAR")))
    except radar.RoboDesligado as e:
        estado.terminar(erro=str(e))
        raise SystemExit("  " + str(e))
    except radar.Interrompida as e:
        from lexsuite import causas
        estado.terminar(getattr(e, "situacao", None), erro=causas.mensagem("interrompida"), info={"causa": "interrompida", "pt": causas.mensagem("interrompida"),
                                                                    "en": causas.mensagem("interrompida", "en"), "detalhe": ""})
        print("  " + causas.mensagem("interrompida"), flush=True)
        return
    except Exception as e:  # leitura agendada: mensagem clara; avisa a SolverONE só quando é defeito do programa
        import traceback
        from lexsuite import causas, conta
        causa = causas.classificar(e)
        estado.terminar(erro=causas.mensagem(causa), info={"causa": causa, "pt": causas.mensagem(causa), "en": causas.mensagem(causa, "en"),
                                                          "detalhe": f"{e.__class__.__name__}: {e}"[:600]})
        if causa in ("erro_do_programa", "bloqueio_fora_do_brasil"):
            conta.registrar_erro(cfg, VERSAO, "leitura agendada", traceback.format_exc()[-1800:])
        raise SystemExit("  " + causas.mensagem(causa) + "\n  (detalhe: " + f"{e.__class__.__name__}: {e}"[:300] + ")")


def cmd_atualizar(a):
    """Procura uma versão nova assinada (pasta compartilhada ou endereço fixo) e instala."""
    from lexsuite import atualizar
    cfg = carregar_config(os.path.join(AQUI, "config.json"))
    r = atualizar.atualizar(AQUI, cfg, VERSAO, print, instalar_agora=not a.so_verificar)
    print("  " + (r.get("motivo") or (f"Versão {r.get('versao')} disponível em {r.get('origem')}" if r.get("disponivel") and not r.get("arquivos") else "")))


def cmd_agendar(a):
    """Cria a leitura automática com os horários do config.json (o AGENDAR.bat chama isto, como administrador)."""
    from lexsuite import agendar
    cfg = carregar_config(os.path.join(AQUI, "config.json"))
    ok, msg = agendar.agendar(AQUI, *agendar.do_config(cfg))
    print("  " + msg)
    if not ok:
        raise SystemExit(1)


def cmd_app(a):
    """Tela local no navegador: escolher os tribunais, rodar e ver a lista (ABRIR.bat)."""
    from lexsuite import app
    cfg = carregar_config(os.path.join(AQUI, "config.json"))
    app.servir(AQUI, a.porta or cfg["radar"].get("porta"), abrir=not a.sem_navegador, espera=a.espera)


def cmd_orgaos(a):
    """Descobre o idOrgao de cada vara do tribunal (1 download do caderno) e guarda em orgaos_<TRT>.json."""
    pasta_diag = os.path.join(AQUI, "diagnostico") if a.diagnostico else None
    dia = dt.date.fromisoformat(a.data) if a.data else _dia_util_atras(1)
    pubs = None
    for _ in range(6):
        try:
            pubs = djen.baixar_caderno(a.tribunal, dia.isoformat(), pasta_diag)
        except rede.BloqueadoForaDoBrasil as e:
            raise SystemExit("  " + str(e))
        if pubs:
            break
        dia = _dia_util_atras(1, dia)
    if not pubs:
        raise SystemExit("  Nenhum caderno encontrado nos últimos dias úteis. Tente de novo mais tarde.")
    mapa = djen.mapa_orgaos(pubs)
    caminho = os.path.join(AQUI, f"orgaos_{a.tribunal.upper()}.json")
    saidas.gravar_json(caminho, mapa)
    print(f"  {len(mapa)} órgãos do {a.tribunal.upper()} em {caminho}")
    cfg_path = os.path.join(AQUI, "config.json")
    if os.path.exists(cfg_path):
        for v in monitor.varas_alvo(json.load(open(cfg_path, encoding="utf-8")), AQUI):
            if v["tribunal"] == a.tribunal.upper():
                print(f"   {v['vara']}: idOrgao {v['orgao_id'] or 'NÃO ACHADO (confira o nome da vara)'}")


def cmd_diagnostico(a):
    """Relatório curto do que o radar guardou (contagens + amostras sem dado de pessoa física), para calibrar a regra."""
    try:
        from lexsuite import diagnostico as dg
    except ImportError:
        raise SystemExit("  Falta o arquivo lexsuite\\diagnostico.py: baixe-o da subpasta lexsuite do Drive para a subpasta lexsuite daqui.")
    banco = bd.Banco(os.path.join(AQUI, "lexsuite.db"))
    pasta = os.path.join(AQUI, "diagnostico")
    os.makedirs(pasta, exist_ok=True)
    caminho = os.path.join(pasta, "radar-diagnostico.txt")
    leads = banco.todos_leads()
    if not leads:
        raise SystemExit("  O banco ainda não tem ações guardadas. Rode o RODAR.bat (radar) primeiro.")
    texto = dg.relatorio_radar(leads, amostras=a.amostras)
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)
    print(f"  {len(leads)} ações analisadas. Relatório: {caminho} ({os.path.getsize(caminho) // 1024} KB).")
    print("  Pode mandar esse arquivo: não tem senha, CPF nem nome de pessoa física.")


def main(argv=None):
    p = argparse.ArgumentParser(description=f"LexSuiteONE · JUDICIAL v{VERSAO}")
    sub = p.add_subparsers(dest="comando", required=True)
    s = sub.add_parser("varas", help="ranking das varas com mais ações novas (DataJud)")
    s.add_argument("--tribunal", default="TRT2"); s.add_argument("--meses", type=int, default=3)
    s.add_argument("--quantas", type=int, default=30); s.set_defaults(f=cmd_varas)
    s = sub.add_parser("vara", help="raio-x de uma vara (DataJud) + painel")
    s.add_argument("--tribunal", default="TRT2"); s.add_argument("--vara", required=True)
    s.add_argument("--meses", type=int, default=12); s.add_argument("--cache")
    s.set_defaults(f=cmd_vara)
    s = sub.add_parser("djen", help="ações novas do dia (DJEN, precisa rodar no Brasil) + planilha + painel")
    s.add_argument("--tribunal", default="TRT2"); s.add_argument("--vara", required=True)
    s.add_argument("--dias", type=int, default=3); s.add_argument("--orgao-id", dest="orgao_id")
    s.add_argument("--sem-cnpj", action="store_true"); s.add_argument("--diagnostico", action="store_true")
    s.add_argument("--carteira", default=os.path.join(AQUI, "carteira.csv"), help="CSV cnpj;nome dos clientes atuais")
    s.add_argument("--so-carteira", action="store_true", help="mostrar só ações contra clientes da carteira")
    s.add_argument("--modo", choices=["caderno", "busca"], default="caderno",
                   help="caderno = diário inteiro do dia (padrão); busca = API paginada")
    s.set_defaults(f=cmd_djen)
    s = sub.add_parser("pauta", help="ações com 1ª audiência marcada (pauta pública do PJe; roda de qualquer lugar)")
    s.add_argument("--tribunal", default="TRT2"); s.add_argument("--vara", required=True)
    s.add_argument("--dias", type=int, default=10)
    s.add_argument("--carteira", default=os.path.join(AQUI, "carteira.csv"))
    s.add_argument("--so-carteira", action="store_true")
    s.set_defaults(f=cmd_pauta)
    s = sub.add_parser("tudo", help="roda tudo o que está no config.json (uso diário/agendado)")
    s.add_argument("--config", default=os.path.join(AQUI, "config.json")); s.set_defaults(f=cmd_tudo)
    s = sub.add_parser("monitor", help="publicações do DJEN nos processos do escritório + aviso na hora")
    s.add_argument("--config", default=os.path.join(AQUI, "config.json"))
    s.add_argument("--caderno", action="store_true", help="varredura completa pelo caderno do dia (rodar de manhã)")
    s.add_argument("--dias", type=int, help="quantos dias para trás conferir (padrão: o do config.json)")
    s.add_argument("--sem-aviso", action="store_true", help="não manda Telegram nem e-mail nesta rodada")
    s.add_argument("--teste-aviso", action="store_true", help="manda uma mensagem de teste e para")
    s.add_argument("--descobrir-chat", action="store_true", help="mostra o chat_id do grupo do Telegram e para")
    s.add_argument("--exemplo", action="store_true", help="demonstração com um dia fictício em 3 tribunais (não manda aviso)")
    s.add_argument("--sem-cnpj", action="store_true")
    s.add_argument("--diagnostico", action="store_true")
    s.set_defaults(f=cmd_monitor)
    s = sub.add_parser("radar", help="uma rodada do Radar sem tela: ações novas contra empresas nos tribunais do config (precisa rodar no Brasil)")
    s.add_argument("--config", default=os.path.join(AQUI, "config.json"))
    s.add_argument("--dias", type=int, help="dias úteis para trás (padrão: o do config.json)")
    s.add_argument("--sem-cnpj", action="store_true", help="não consultar a Receita")
    s.add_argument("--diagnostico", action="store_true")
    s.add_argument("--agendado", action="store_true", help="leitura disparada pela tarefa do Windows (mostra o aviso de horário perdido)")
    s.set_defaults(f=cmd_radar)
    s = sub.add_parser("app", help="abre a tela do Radar no navegador (escolher tribunais, rodar, ver a lista)")
    s.add_argument("--porta", type=int, help="porta local (padrão: a do config.json ou 8765)")
    s.add_argument("--sem-navegador", action="store_true", help="não abrir o navegador sozinho")
    s.add_argument("--espera", action="store_true", help="reinício depois de atualizar: espera a porta liberar e não procura outra tela aberta")
    s.set_defaults(f=cmd_app)
    s = sub.add_parser("agendar", help="cria a leitura automática no Agendador do Windows com os horários do config.json")
    s.set_defaults(f=cmd_agendar)
    s = sub.add_parser("orgaos", help="descobre o código (idOrgao) das varas de um tribunal, uma vez (precisa rodar no Brasil)")
    s.add_argument("--tribunal", default="TRT2"); s.add_argument("--data", help="aaaa-mm-dd (padrão: último dia útil)")
    s.add_argument("--diagnostico", action="store_true"); s.set_defaults(f=cmd_orgaos)
    s = sub.add_parser("atualizar", help="procura uma versão nova assinada e instala (pasta compartilhada ou endereço fixo)")
    s.add_argument("--so-verificar", action="store_true", help="só dizer se há versão nova, sem instalar")
    s.set_defaults(f=cmd_atualizar)
    s = sub.add_parser("diagnostico", help="relatório do que o radar guardou, sem dado pessoal (para calibrar a regra de ação nova)")
    s.add_argument("--amostras", type=int, default=40, help="quantos trechos de exemplo por grupo (padrão 40)")
    s.set_defaults(f=cmd_diagnostico)
    a = p.parse_args(argv)
    a.f(a)


if __name__ == "__main__":
    sys.exit(main())
