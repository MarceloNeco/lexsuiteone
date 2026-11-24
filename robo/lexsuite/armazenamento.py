"""Planilha grande e armazenamento no computador do escritório (0.7.16; documentacao/DESENHO-PLANILHA-GRANDE.md).

A planilha é a vitrine; o arquivo completo fica no banco do computador. Aqui ficam:
- a escolha das linhas da aba Arquivo (últimos N dias + todo processo trabalhado, depois do corte da última limpeza);
- o limite de linhas por planilha, com aviso a 80% e limpeza com cópia sozinha a 100%;
- as cópias de segurança (planilhas + Arquivo completo em CSV) em "<pasta>/Cópias de segurança/", 6 guardadas;
- o retrato do armazenamento para a Configuração (planilhas, banco, saida/, cópias e espaço livre no disco).

O RADAR só olha os arquivos dele e o espaço livre do disco (o Windows informa); não abre arquivo de ninguém.
"""

import csv
import datetime as dt
import os
import re
import shutil

from . import preferencias

TRABALHADOS = ("em_analise", "em_contato", "virou_cliente")
PASTA_COPIAS = "Cópias de segurança"
COPIAS_GUARDADAS = 6
AVISO_PCT = 80
DIAS_DEPOIS_DE_LIMPAR = 30
GB = 1024 ** 3
DISCO_BAIXO_GB, DISCO_BAIXO_PCT, DISCO_CRITICO_GB = 5, 10, 1
_NOME_COPIA = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}h\d{2}m\d{2}( - (antes de limpar|limpeza automática|feita à mão|exportação|teste|antes de salvar regras))?$")

FRENTE_LEGIVEL = {"trabalhista": "Trabalhista", "tributario": "Tributário", "civel": "Cível", "empresarial": "Empresarial"}
FRENTE_EN = {"trabalhista": "Labour", "tributario": "Tax", "civel": "Civil", "empresarial": "Corporate"}  # 0.7.52: avisos em inglês inteiros


def frente_do(item):
    return item.get("frente") or "trabalhista"


# --- Aba Arquivo e limite ------------------------------------------------------------------------------------------

def corte(banco, frente):
    """Data a partir da qual a aba Arquivo mostra o que não foi trabalhado (definida pela última limpeza), ou ''."""
    for e in banco.execucoes("limpeza_planilha", 50):
        if frente in (e.get("frentes") or [frente]):
            return e.get("corte", "")
    return ""


def selecionar_arquivo(itens, dias, corte_data="", hoje=None):
    """Linhas da aba Arquivo: todo processo trabalhado, de qualquer idade, e os outros dos últimos `dias` dias (ou
    desde o corte da última limpeza, o que for mais recente)."""
    hoje = hoje or dt.date.today()
    desde = (hoje - dt.timedelta(days=max(1, int(dias or 90)))).isoformat()
    if corte_data and corte_data > desde:
        desde = corte_data
    # 0.7.53 (decisão 67): pela data do processo no Diário (antes, pela data em que o RADAR leu: os 24 TRTs lidos uma vez ficavam inteiros)
    return [i for i in itens if i.get("situacao") in TRABALHADOS or _data_diario(i) >= desde]


def _data_diario(item):
    return str(item.get("diario_em") or item.get("primeira_vez") or "")[:10]


RADAR_DIAS_PLANILHA = 30  # 0.7.53 (decisão 67): a aba Radar da planilha tem no máximo 30 dias, pela data no Diário


def so_escolhidos(itens, escolhidos):
    """0.7.53 (decisão 67): a planilha fica só com os tribunais escolhidos hoje; trabalhados de qualquer tribunal ficam (são do
    escritório). O resto continua no programa (tela Arquivo) e entra na aba Estatística, só em números."""
    esc = {str(t).upper() for t in escolhidos or []}
    return [i for i in itens if (i.get("tribunal") or "").upper() in esc or i.get("situacao") in TRABALHADOS]


def radar_ate_30_dias(itens, hoje=None):
    """Aba Radar: só os últimos RADAR_DIAS_PLANILHA dias pela data no Diário; o mais velho vai para a aba Arquivo."""
    hoje = hoje or dt.date.today()
    desde = (hoje - dt.timedelta(days=RADAR_DIAS_PLANILHA)).isoformat()
    return [i for i in itens if _data_diario(i) >= desde], [i for i in itens if _data_diario(i) < desde]


def copia_antes_da_0753(cfg, banco, aviso=print):
    """Uma vez só: guarda as planilhas como eram antes da primeira gravação enxuta (decisão 67), em
    "Cópias de segurança/antes da 0.7.53/". Nada é apagado. Devolve True se já existia ou se copiou."""
    from . import compartilhar
    if any(True for _ in banco.execucoes("copia_0753", 1)):
        return True
    base = compartilhar.pasta_base(cfg)
    if not base:
        return False
    destino = os.path.join(base, "Cópias de segurança", "antes da 0.7.53")
    try:
        os.makedirs(destino, exist_ok=True)
        for _frente, caminho in preferencias.planilhas_existentes(base):
            alvo = os.path.join(destino, os.path.basename(caminho))
            if os.path.exists(caminho) and not os.path.exists(alvo):
                shutil.copy2(caminho, alvo)
    except OSError as e:  # planilha aberta ou pasta sem permissão: tenta na próxima gravação
        aviso(f"  Cópia das planilhas de antes da 0.7.53 não feita agora ({e.__class__.__name__}); tento na próxima gravação.")
        return False
    banco.registrar("copia_0753", {"pasta": "Cópias de segurança/antes da 0.7.53"})
    return True


def caber(radar, arquivo, limite):
    """Corta para caber no limite: primeiro o que não foi trabalhado e é mais antigo no Arquivo; a aba Radar só é
    cortada se sozinha passar do limite. Devolve (radar, arquivo, cortou)."""
    limite = max(1000, int(limite or 60000))
    if len(radar) > limite:
        return radar[:limite], [], True
    sobra = limite - len(radar)
    if len(arquivo) <= sobra:
        return radar, arquivo, False
    trab = [i for i in arquivo if i.get("situacao") in TRABALHADOS]
    resto = sorted((i for i in arquivo if i.get("situacao") not in TRABALHADOS), key=lambda i: i.get("primeira_vez") or "", reverse=True)
    manter = set(map(id, (trab + resto)[:sobra]))
    return radar, [i for i in arquivo if id(i) in manter], True


def nivel_planilha(linhas, limite):
    pct = int(round(100 * linhas / max(1, int(limite or 60000))))
    return pct, ("cheia" if pct >= 100 else "grande" if pct >= AVISO_PCT else "ok")


def aviso_tamanho(frente, linhas, limite):
    """Texto do aviso (PT / EN) quando a planilha passa de 80% do limite, ou ''."""
    pct, nivel = nivel_planilha(linhas, limite)
    if nivel == "ok":
        return ""
    nome, nome_en = FRENTE_LEGIVEL.get(frente, frente), FRENTE_EN.get(frente, frente)
    n1, n2 = f"{linhas:,}".replace(",", "."), f"{int(limite):,}".replace(",", ".")
    return (f"PLANILHA {nome.upper()} GRANDE: {n1} de {n2} linhas ({pct}%). Recomendamos \"Limpar a planilha "
            f"(com cópia)\" no programa: antes, o RADAR guarda uma cópia completa. / {nome_en.upper()} SPREADSHEET IS LARGE: "
            f"{linhas:,} of {int(limite):,} rows ({pct}%). We recommend \"Clean up the spreadsheet (with backup)\" in the program: "
            f"RADAR first keeps a full backup.")


def limpeza_recente(banco, horas=24):
    """True se houve limpeza da planilha nas últimas `horas` (0.7.17: a limpeza automática não se repete a cada gravação)."""
    for e in banco.execucoes("limpeza_planilha", 1):
        try:
            quando = dt.datetime.fromisoformat(str(e.get("quando", ""))[:19])
        except ValueError:
            return False
        return dt.datetime.now() - quando < dt.timedelta(hours=horas)
    return False


# --- Disco ---------------------------------------------------------------------------------------------------------

def disco(caminho):
    """Espaço do disco onde fica `caminho`: {livre, total, pct_livre, nivel: ok|baixo|critico}. O Windows informa o
    espaço livre sem o RADAR abrir arquivo nenhum."""
    alvo = caminho
    while alvo and not os.path.exists(alvo):
        pai = os.path.dirname(alvo)
        if pai == alvo:
            break
        alvo = pai
    try:
        u = shutil.disk_usage(alvo or ".")
    except OSError:
        return {"livre": 0, "total": 0, "pct_livre": 0, "nivel": "desconhecido"}
    pct = int(100 * u.free / u.total) if u.total else 0
    nivel = ("critico" if u.free < DISCO_CRITICO_GB * GB
             else "baixo" if u.free < DISCO_BAIXO_GB * GB or pct < DISCO_BAIXO_PCT else "ok")
    return {"livre": u.free, "total": u.total, "pct_livre": pct, "nivel": nivel}


def texto_disco(d):
    livre = f"{d['livre'] / GB:.1f} GB".replace(".", ",")
    if d["nivel"] == "critico":
        return (f"Disco quase cheio ({livre} livres): o RADAR guarda só no programa e não grava a planilha até liberar espaço. "
                f"/ Disk almost full ({livre} free): the spreadsheet is not written until space is freed.")
    if d["nivel"] == "baixo":
        return (f"Pouco espaço no disco ({livre} livres, {d['pct_livre']}%): o RADAR não faz cópias de segurança novas. "
                f"Libere espaço ou peça ajuda. / Low disk space ({livre} free): no new backups.")
    return ""


# --- Cópias de segurança -------------------------------------------------------------------------------------------

def _tamanho(caminho):
    if os.path.isfile(caminho):
        try:
            return os.path.getsize(caminho)
        except OSError:
            return 0
    total = 0
    for raiz, _dirs, arquivos in os.walk(caminho):
        for a in arquivos:
            try:
                total += os.path.getsize(os.path.join(raiz, a))
            except OSError:
                pass
    return total


def pasta_copias(base):
    return os.path.join(base, PASTA_COPIAS) if base else ""


def copias(base):
    """[{nome, caminho, bytes}] das cópias de segurança, da mais nova para a mais antiga."""
    pasta = pasta_copias(base)
    if not pasta or not os.path.isdir(pasta):
        return []
    nomes = sorted((n for n in os.listdir(pasta) if _NOME_COPIA.match(n) and os.path.isdir(os.path.join(pasta, n))), reverse=True)
    return [{"nome": n, "caminho": os.path.join(pasta, n), "bytes": _tamanho(os.path.join(pasta, n))} for n in nomes]


def _podar(base, aviso):
    """Deixa as COPIAS_GUARDADAS mais novas entre as que o RADAR fez sozinho ou antes de limpar; as feitas à mão e as
    exportações nunca são apagadas pelo programa (0.7.17). Só apaga pastas com o nome das cópias do RADAR."""
    apagadas = []
    todas = copias(base)
    automaticas = [c for c in todas if not c["nome"].endswith((" - feita à mão", " - exportação", REGRAS))]
    regras = [c for c in todas if c["nome"].endswith(REGRAS)]  # revisão da 0.7.28: contam à parte, não empurram as outras
    for c in automaticas[COPIAS_GUARDADAS:] + regras[COPIAS_GUARDADAS:]:
        try:
            shutil.rmtree(c["caminho"])
            apagadas.append(c["nome"])
        except OSError:
            pass
    if apagadas:
        aviso(f"  Cópias de segurança antigas apagadas (ficam as {COPIAS_GUARDADAS} mais novas): {', '.join(apagadas)}.")
    return apagadas


def _csv_arquivo(caminho, cfg, banco):
    from . import radar
    itens = radar.montar_radar(cfg, banco, visao="arquivo")["itens"]
    titulos = [t for t, _ in radar.COLUNAS_RADAR]
    with open(caminho, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(titulos)
        for it in itens:
            linha = radar.linha_csv(it)
            w.writerow([" | ".join(map(str, v)) if isinstance(v, list) else ("" if v is None else v)
                        for v in (linha.get(k) for _, k in radar.COLUNAS_RADAR)])
    return len(itens)


REGRAS = " - antes de salvar regras"


def copia_antes_das_regras(base, aviso=print, agora=None):
    """Revisão da 0.7.28 (sem uso desde a 0.7.33, quando os critérios saíram da planilha): antes de a tela regravar as abas Preferências e Exclusões, a planilha da frente trabalhista vai
    para "Cópias de segurança/AAAA-MM-DD HHhMMmSS - antes de salvar regras/" (ficam as 6 mais novas dessas). Sem planilha,
    nada a copiar. Devolve (ok, pasta ou motivo)."""
    origem = preferencias.caminho(base, "trabalhista")
    if not origem or not os.path.exists(origem):
        return True, ""
    agora = agora or dt.datetime.now()
    destino = os.path.join(pasta_copias(base), f"{agora:%Y-%m-%d %Hh%Mm%S}{REGRAS}")
    while os.path.exists(destino):  # 0.7.29: dois salvamentos no mesmo segundo não se sobrescrevem (o 2º vai para o segundo seguinte)
        agora += dt.timedelta(seconds=1)
        destino = os.path.join(pasta_copias(base), f"{agora:%Y-%m-%d %Hh%Mm%S}{REGRAS}")
    try:
        os.makedirs(destino)  # nova: se falhar adiante, só ela é apagada
        shutil.copyfile(origem, os.path.join(destino, os.path.basename(origem)))
    except OSError as e:
        shutil.rmtree(destino, ignore_errors=True)
        return False, f"Não consegui gravar a cópia de segurança antes de salvar ({e.__class__.__name__})."
    _podar(base, aviso)
    return True, destino


def copia_seguranca(cfg, banco, motivo="", aviso=print, agora=None, so_csv=False):
    """Grava em "<pasta>/Cópias de segurança/AAAA-MM-DD HHhMMmSS - motivo/" as planilhas (Excel) e o Arquivo completo do
    programa em CSV (abre no Excel). Recusa com disco baixo. Devolve (ok, pasta ou motivo)."""
    from . import compartilhar
    base = compartilhar.pasta_base(cfg)
    if not base:
        return False, "Escolha antes a pasta da planilha (Configurações)."
    d = disco(base)
    if d["nivel"] in ("baixo", "critico"):
        return False, texto_disco(d)
    agora = agora or dt.datetime.now()
    motivo_limpo = re.sub(r"[^\w ]+", "", motivo or "")[:40].strip()  # 0.7.36: fora da f-string, para rodar também no Python 3.11
    nome = f"{agora:%Y-%m-%d %Hh%Mm%S}" + (f" - {motivo_limpo}" if motivo else "")
    destino = os.path.join(pasta_copias(base), nome)
    try:
        os.makedirs(destino, exist_ok=True)
        copiadas = 0
        if not so_csv:
            for _frente, origem in preferencias.planilhas_existentes(base):
                shutil.copyfile(origem, os.path.join(destino, os.path.basename(origem)))  # 0.7.21: sem a marca "somente leitura" (a poda apaga)
                copiadas += 1
        n = _csv_arquivo(os.path.join(destino, "Arquivo completo (todas as ações guardadas no programa).csv"), cfg, banco)
    except Exception as e:  # noqa: BLE001 - revisão da 0.7.18: qualquer falha (disco, banco) apaga a cópia pela metade
        shutil.rmtree(destino, ignore_errors=True)  # cópia pela metade não fica contando entre as guardadas
        return False, f"Não consegui gravar a cópia de segurança ({e.__class__.__name__})."
    banco.registrar("copia_seguranca", {"pasta": nome, "motivo": motivo, "planilhas": copiadas, "linhas_csv": n,
                                        "bytes": _tamanho(destino)})
    aviso(f"  Cópia de segurança gravada: {destino} ({copiadas} planilha(s) e {n} processos em CSV).")
    _podar(base, aviso)
    return True, destino


def limpar(cfg, banco, pasta_robo, versao, aviso=print, automatico=False, hoje=None):
    """"Limpar a planilha (com cópia)": cópia de segurança e, depois, a aba Arquivo passa a mostrar só os últimos 30 dias
    e os processos trabalhados. Nada sai do programa. Devolve (ok, mensagem)."""
    from . import radar
    hoje = hoje or dt.date.today()
    ok, onde = copia_seguranca(cfg, banco, "limpeza automática" if automatico else "antes de limpar", aviso)
    if not ok:  # 0.7.17 (revisão da Arquitetura): sem cópia bem-sucedida, não enxuga
        if automatico:
            aviso(f"  Sem cópia de segurança ({onde}): a aba Arquivo não foi enxugada; a planilha fica só com as linhas mais recentes até o limite.")
        return False, onde + " A limpeza não foi feita."
    corte_data = (hoje - dt.timedelta(days=DIAS_DEPOIS_DE_LIMPAR)).isoformat()
    banco.registrar("limpeza_planilha", {"corte": corte_data, "automatica": bool(automatico), "copia": onde if ok else "",
                                         "frentes": list(preferencias.NOMES_FRENTE)})
    if automatico:  # na automática, quem chamou já está gravando a planilha
        return True, "Planilha limpa. Cópia completa em: " + onde
    antes = _linhas_por_frente(banco)
    if not radar.regravar_planilha(cfg, banco, pasta_robo, versao, aviso):
        # 0.7.52 (dono, 24/Nov): antes dizia "limpa" mesmo sem conseguir regravar (planilha aberta no Excel)
        return False, ("A cópia de segurança foi feita, mas a planilha não foi regravada: ela está aberta no Excel (ou a pasta não "
                       "deixa gravar). Feche a planilha e clique de novo. / The backup was saved, but the spreadsheet was not "
                       "rewritten: it is open in Excel (or the folder is read-only). Close it and click again.")
    return True, resumo_limpeza(antes, _linhas_por_frente(banco))


def _linhas_por_frente(banco):
    """Última gravação de cada planilha: {frente: {"linhas", "limite", "radar"}} (0.7.52: para dizer o antes e o depois)."""
    ult = {}
    for e in banco.execucoes("planilha", 50):
        ult.setdefault(e.get("frente"), {"linhas": int(e.get("linhas") or 0), "limite": int(e.get("limite") or 60000),
                                          "radar": e.get("radar")})
    return ult


def resumo_limpeza(antes, depois):
    """Mensagem PT / EN do fim da limpeza: linhas antes e depois e, se continuar grande, por quê (a aba Radar é a Lista)."""
    pt, en = ["Planilha limpa; a cópia completa está em Cópias de segurança."], ["Spreadsheet cleaned up; the full backup is in the Backups folder."]
    for frente, d in sorted(depois.items(), key=lambda x: str(x[0])):
        a = (antes.get(frente) or {}).get("linhas", d["linhas"])
        nome, nome_en = FRENTE_LEGIVEL.get(frente, frente), FRENTE_EN.get(frente, frente)
        pt.append(f"{nome}: " + f"{a:,} → {d['linhas']:,}".replace(",", ".") + " linhas.")
        en.append(f"{nome_en}: {a:,} → {d['linhas']:,} rows.")
        if nivel_planilha(d["linhas"], d["limite"])[1] != "ok" and d.get("radar") is not None:
            r = int(d["radar"])
            rp = f"{r:,}".replace(",", ".")
            pt.append(f"Continua grande porque a aba Radar tem {rp} processos da Lista (a limpeza enxuga só a aba Arquivo). "
                      "Para diminuir, arquive na Lista o que não interessa ou leia menos tribunais.")
            en.append(f"It is still large because the Radar sheet has {r:,} cases from the List (the cleanup only trims the "
                      "Archive sheet). To reduce it, archive what does not matter in the List or read fewer courts.")
    return " ".join(pt) + " / " + " ".join(en)


# --- Retrato para a Configuração -----------------------------------------------------------------------------------

def situacao(cfg, banco, pasta_robo):
    """Tudo o que a seção Armazenamento mostra."""
    from . import compartilhar
    base = compartilhar.pasta_base(cfg)
    ultimas = {}
    for e in banco.execucoes("planilha", 50):
        ultimas.setdefault(e.get("frente"), e)
    planilhas = []
    for frente, caminho in preferencias.planilhas_existentes(base):
        e = ultimas.get(frente) or {}
        linhas, limite = int(e.get("linhas") or 0), int(e.get("limite") or 60000)
        pct, nivel = nivel_planilha(linhas, limite)
        planilhas.append({"frente": frente, "frente_legivel": FRENTE_LEGIVEL.get(frente, frente), "nome": os.path.basename(caminho),
                          "bytes": _tamanho(caminho), "linhas": linhas, "limite": limite, "pct": pct, "nivel": nivel})
    try:
        esp = banco.espaco()
    except Exception:  # noqa: BLE001
        esp = {"bytes": 0, "acoes": 0}
    lista_copias = copias(base)
    d = disco(base or pasta_robo)
    nivel = "critico" if d["nivel"] == "critico" else "atencao" if (d["nivel"] == "baixo" or any(p["nivel"] != "ok" for p in planilhas)) else "ok"
    mensagens = [aviso_tamanho(p["frente"], p["linhas"], p["limite"]) for p in planilhas if p["nivel"] != "ok"] + [texto_disco(d)]
    if esp.get("bytes", 0) > 1024 ** 3:  # 0.7.18 (revisão): o aviso do banco grande também aparece na tela, não só na janela preta
        mensagens.append("Os dados do programa passaram de 1 GB: os processos nunca abertos com mais de 6 meses ficam só com o resumo. "
                         "/ The program data is over 1 GB: never-opened lawsuits older than 6 months keep only the summary.")
    return {"planilhas": planilhas, "banco": {"bytes": esp.get("bytes", 0), "acoes": esp.get("acoes", 0)},
            "saida": {"bytes": _tamanho(os.path.join(pasta_robo, "saida")) if pasta_robo else 0},
            "copias": {"n": len(lista_copias), "bytes": sum(c["bytes"] for c in lista_copias), "guardadas": COPIAS_GUARDADAS,
                       "pasta": pasta_copias(base), "lista": lista_copias[:COPIAS_GUARDADAS]},
            "disco": d, "nivel": nivel, "mensagens": [m for m in mensagens if m]}


# --- 0.7.53 (decisão 67): aba Estatística da planilha ----------------------------------------------------------------

SITUACAO_LEGIVEL = {"novo": "Novo", "visto": "Visto", "em_analise": "Em análise", "em_contato": "Em contato",
                    "virou_cliente": "Virou cliente", "descartado": "Descartado", "arquivado": "Arquivado"}
FAIXA_LEGIVEL = {"sem": "sem valor", "ate10k": "até R$ 10 mil", "10k-50k": "R$ 10 mil a 50 mil", "50k-100k": "R$ 50 mil a 100 mil",
                 "100k-300k": "R$ 100 mil a 300 mil", "300k-500k": "R$ 300 mil a 500 mil", "500k-1mi": "R$ 500 mil a 1 milhão",
                 "1mi+": "acima de R$ 1 milhão"}
DIMENSAO_LEGIVEL = {"total": "Total", "porte": "Porte", "faixa": "Faixa de valor", "situacao": "Situação", "setor": "Setor"}


def linhas_estatistica(banco, hoje=None):
    """Linhas da aba Estatística (formato longo, fácil de filtrar): por mês e tribunal, o total de processos novos, o porte e a
    faixa de valor (de `estatisticas_diarias`, que nunca se apaga), a situação e o setor (de `estatisticas_leves`), e os dias
    com dados; por dia, só o total dos últimos 31 dias. Todos os tribunais lidos, não só os escolhidos."""
    hoje = hoje or dt.date.today()
    cab = ["Período", "Tribunal", "Área", "Dimensão", "Valor", "Processos", "Dias com dados"]
    por_mes, dias_mes, por_dia = {}, {}, {}
    desde_dia = (hoje - dt.timedelta(days=31)).isoformat()
    for e in banco.estatisticas():
        d, trib, frente, n = str(e.get("data") or "")[:10], e.get("tribunal") or "", e.get("frente") or "", int(e.get("novas") or 0)
        if len(d) != 10 or not trib:
            continue
        mes = d[:7]
        dias_mes.setdefault((mes, trib, frente), set()).add(d)
        for dim, val in (("total", ""), ("porte", e.get("porte") or "sem porte (sem CNPJ)"), ("faixa", FAIXA_LEGIVEL.get(e.get("faixa_valor") or "sem", e.get("faixa_valor")))):
            k = (mes, trib, frente, dim, val)
            por_mes[k] = por_mes.get(k, 0) + n
        if d >= desde_dia:
            por_dia[(d, trib, frente)] = por_dia.get((d, trib, frente), 0) + n
    for e in banco.estatisticas_leves():
        k = (e["mes"], e["tribunal"], e["frente"], e["dimensao"],
             SITUACAO_LEGIVEL.get(e["valor"], e["valor"]) if e["dimensao"] == "situacao" else (e["valor"] or "sem setor"))
        por_mes[k] = por_mes.get(k, 0) + int(e["n"] or 0)
    linhas = [cab]
    for (mes, trib, frente, dim, val), n in sorted(por_mes.items(), key=lambda x: (x[0][0], x[0][1], x[0][3] != "total", x[0][3], -x[1])):
        linhas.append([mes, trib, FRENTE_LEGIVEL.get(frente, frente), DIMENSAO_LEGIVEL.get(dim, dim), val, n,
                       len(dias_mes.get((mes, trib, frente), ())) if dim == "total" else ""])
    for (d, trib, frente), n in sorted(por_dia.items()):
        linhas.append([d, trib, FRENTE_LEGIVEL.get(frente, frente), "Total do dia", "", n, ""])
    return linhas

