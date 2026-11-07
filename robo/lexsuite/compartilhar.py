"""A pasta compartilhada (Google Drive para computador, OneDrive, Dropbox): onde o robô deixa a planilha e a página
e de onde lê o controle e as atualizações. Nada de senha: é só uma pasta do computador que o Drive sincroniza."""

import os
import platform
import shutil

from . import planilha, preferencias

NOME_RADAR = preferencias.NOME_ARQUIVO  # uma planilha só: Radar + Preferências + Exclusões + (ocultas) Controle, Log, Saúde, Sobre
NOME_PAGINA = "LexSuiteONE - Radar.html"
SUBPASTA_ATUALIZACAO = "atualizacao"


def candidatas():
    """Pastas sincronizadas que existem neste computador, na ordem de probabilidade."""
    home = os.path.expanduser("~")
    opcoes = []
    for base in (home, os.path.join(home, "Google Drive")):
        for nome in ("Meu Drive", "My Drive", "Google Drive", "OneDrive", "Dropbox"):
            opcoes.append(os.path.join(base, nome))
    try:
        for nome in sorted(os.listdir(home)):
            if nome.lower().startswith("onedrive") and nome not in ("OneDrive",):
                opcoes.append(os.path.join(home, nome))
    except OSError:
        pass
    if os.name == "nt":
        for letra in "DEFGHIJKLMNOPQRSTUVWXYZ":
            for nome in ("Meu Drive", "My Drive"):
                opcoes.append(f"{letra}:\\{nome}")
    achadas = []
    for p in opcoes:
        if os.path.isdir(p) and p not in achadas:
            achadas.append(p)
    return achadas


def pasta_base(cfg):
    c = cfg.get("compartilhar") or {}
    return os.path.join(c["pasta"], c.get("subpasta") or "LexSuiteONE") if c.get("pasta") else ""


def pasta_atualizacao(cfg):
    base = pasta_base(cfg)
    return os.path.join(base, SUBPASTA_ATUALIZACAO) if base else ""


def testar(pasta, subpasta="LexSuiteONE"):
    """Confere se dá para criar a subpasta e gravar nela. Devolve (ok, mensagem)."""
    if not pasta or not os.path.isdir(pasta):
        return False, "Essa pasta não existe neste computador."
    alvo = os.path.join(pasta, subpasta)
    try:
        os.makedirs(alvo, exist_ok=True)
        prova = os.path.join(alvo, "teste-lexsuite.txt")
        with open(prova, "w", encoding="utf-8") as f:
            f.write("ok\n")
        os.remove(prova)
    except OSError as e:
        return False, f"Não consegui gravar em {alvo} ({e.__class__.__name__})."
    return True, f"Pronto: o robô vai gravar em {alvo}."


def _sobre(cfg, versao, chave_impressao, ultima):
    return [["Item", "Valor"],
            ["Produto", "LexSuiteONE · JUDICIAL (Radar Trabalhista)"], ["Versão", versao], ["Escritório", cfg.get("escritorio", "")],
            ["Computador", platform.node()], ["Sistema", f"{platform.system()} {platform.release()}"],
            ["Python", platform.python_version()], ["Pasta do robô", cfg.get("_pasta_robo", "")],
            ["Tribunais", ", ".join((cfg.get("radar") or {}).get("tribunais") or [])],
            ["Última rodada", ultima], ["Chave de atualização (impressão)", chave_impressao or "sem chave: atualização desligada"],
            ["Suporte", "integracao@solverone.com.br"]]


def _abas_editaveis(caminho, aviso=print):
    """Lê da planilha existente as abas que o escritório edita, para preservá-las. Devolve (abas, ok).
    ok=False quando o arquivo existe mas não pôde ser lido (em uso, corrompido): aí NÃO se regrava."""
    if not os.path.exists(caminho):
        return preferencias.abas_padrao(), True
    try:
        doc = planilha.ler_xlsx(caminho)
    except Exception as e:
        aviso(f"  Planilha em uso ou ilegível ({e.__class__.__name__}); deixo como está nesta rodada.")
        return [], False
    atuais = {a["nome"]: a for a in doc["abas"]}
    abas = []
    for padrao in preferencias.abas_padrao():
        existente = atuais.get(padrao["nome"])
        if existente and existente["linhas"]:
            abas.append({"nome": padrao["nome"], "linhas": existente["linhas"], "oculta": padrao.get("oculta", False), "larguras": padrao.get("larguras")})
        else:
            abas.append(padrao)
    return abas, True


def criar_se_faltar(cfg, versao="", pasta_robo="", aviso=print):
    """Cria a planilha única com o Radar vazio e as abas editáveis padrão. Nunca sobrescreve a que existe."""
    base = pasta_base(cfg)
    if not base:
        return ""
    caminho = os.path.join(base, NOME_RADAR)
    if os.path.exists(caminho):
        return caminho
    os.makedirs(base, exist_ok=True)
    cabecalho = ["Hora", "Tribunal", "Vara", "Processo", "Rito", "Distribuída em", "Empresa(s)", "CNPJ"]
    planilha.escrever_xlsx(caminho, [{"nome": "Radar", "linhas": [cabecalho], "larguras": [8, 9, 34, 26, 12, 12, 40, 18]}]
                           + preferencias.abas_padrao()
                           + [{"nome": "Sobre", "linhas": _sobre(dict(cfg, _pasta_robo=pasta_robo), versao, "", ""), "oculta": True, "larguras": [30, 80]}])
    aviso(f"  Criei a planilha: {caminho}")
    return caminho


def gravar_radar(cfg, pagina, banco, versao, colunas, linha_csv, chave_impressao="", pasta_robo="", aviso=print):
    """Regrava LexSuiteONE.xlsx: aba Radar (a lista), as abas editáveis preservadas (Preferências, Exclusões,
    Controle oculta) e as abas ocultas Log, Saúde e Sobre. Também copia a página HTML.
    Devolve o caminho da planilha, ou '' se não houver pasta ou se a planilha estiver em uso."""
    base = pasta_base(cfg)
    if not base:
        return ""
    os.makedirs(base, exist_ok=True)
    caminho = os.path.join(base, NOME_RADAR)
    editaveis, ok = _abas_editaveis(caminho, aviso)
    if not ok:
        return ""
    cabecalho = [titulo for titulo, _ in colunas] + ["Excluída (motivo)", "Ações na janela"]
    linhas = [cabecalho]
    for it in pagina.get("itens") or []:
        l = linha_csv(it)
        linhas.append([_celula(l.get(chave)) for _, chave in colunas] + [it.get("excluida") or "", it.get("acoes_na_janela", "")])
    log = [["Quando", "Versão", "Tribunais", "Publicações lidas", "Ações novas", "Com CNPJ", "Duração (s)", "Resultado", "Erro"]]
    for e in banco.execucoes("radar", 500):
        log.append([e.get("quando", ""), e.get("versao", ""), ", ".join(e.get("tribunais") or []), e.get("lidas", ""),
                    e.get("novas", ""), e.get("com_cnpj", ""), e.get("duracao", ""), e.get("resultado", ""), e.get("erro", "")])
    saude = [["Quando", "Fonte", "Situação", "Detalhe"]]
    for e in banco.execucoes("saude", 300):
        saude.append([e.get("quando", ""), e.get("fonte", ""), e.get("situacao", ""), e.get("detalhe", "")])
    ultima = log[1][0] if len(log) > 1 else ""
    planilha.escrever_xlsx(caminho, [
        {"nome": "Radar", "linhas": linhas, "larguras": [8, 9, 34, 26, 12, 12, 40, 18, 22, 16, 36, 20, 18, 16, 28, 40, 10, 14, 10, 30, 30, 30, 10]},
    ] + editaveis + [
        {"nome": "Log", "linhas": log, "oculta": True, "larguras": [20, 8, 40, 12, 12, 10, 10, 16, 60]},
        {"nome": "Saúde", "linhas": saude, "oculta": True, "larguras": [20, 18, 10, 80]},
        {"nome": "Sobre", "linhas": _sobre(dict(cfg, _pasta_robo=pasta_robo), versao, chave_impressao, ultima), "oculta": True, "larguras": [30, 80]},
    ])
    html = os.path.join(pasta_robo, "saida", "radar", "radar.html") if pasta_robo else ""
    if html and os.path.exists(html):
        shutil.copyfile(html, os.path.join(base, NOME_PAGINA))
    aviso(f"  Planilha compartilhada: {caminho}")
    return caminho


def _celula(v):
    if isinstance(v, list):
        return " | ".join(str(x) for x in v)
    if isinstance(v, bool):
        return "sim" if v else ""
    return "" if v is None else v
