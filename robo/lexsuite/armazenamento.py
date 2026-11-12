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
    return [i for i in itens if i.get("situacao") in TRABALHADOS or (i.get("primeira_vez") or "") >= desde]


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
    nome = FRENTE_LEGIVEL.get(frente, frente)
    n1, n2 = f"{linhas:,}".replace(",", "."), f"{int(limite):,}".replace(",", ".")
    return (f"PLANILHA {nome.upper()} GRANDE: {n1} de {n2} linhas ({pct}%). Recomendamos \"Limpar a planilha "
            f"(com cópia)\" no programa: antes, o RADAR guarda uma cópia completa. / Spreadsheet is getting large: use "
            f"\"Clean up (with backup)\".")


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
    nome = f"{agora:%Y-%m-%d %Hh%Mm%S}" + (f" - {re.sub(r'[^\w ]+', '', motivo)[:40].strip()}" if motivo else "")
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
    aviso(f"  Cópia de segurança gravada: {destino} ({copiadas} planilha(s) e {n} ações em CSV).")
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
    if not automatico:  # na automática, quem chamou já está gravando a planilha
        radar.regravar_planilha(cfg, banco, pasta_robo, versao, aviso)
    return True, "Planilha limpa. Cópia completa em: " + onde


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
        mensagens.append("O banco do programa passou de 1 GB: os processos nunca abertos com mais de 6 meses ficam só com o resumo. "
                         "/ The program database is over 1 GB: never-opened lawsuits older than 6 months keep only the summary.")
    return {"planilhas": planilhas, "banco": {"bytes": esp.get("bytes", 0), "acoes": esp.get("acoes", 0)},
            "saida": {"bytes": _tamanho(os.path.join(pasta_robo, "saida")) if pasta_robo else 0},
            "copias": {"n": len(lista_copias), "bytes": sum(c["bytes"] for c in lista_copias), "guardadas": COPIAS_GUARDADAS,
                       "pasta": pasta_copias(base), "lista": lista_copias[:COPIAS_GUARDADAS]},
            "disco": d, "nivel": nivel, "mensagens": [m for m in mensagens if m]}
