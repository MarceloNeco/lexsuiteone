"""A pasta compartilhada (Google Drive para computador, OneDrive, Dropbox): onde o robô deixa a planilha e a página
e de onde lê o controle e as atualizações. Nada de senha: é só uma pasta do computador que o Drive sincroniza."""

import json
import os
import platform
import shutil

from . import planilha, preferencias

NOME_RADAR = preferencias.NOME_ARQUIVO  # uma planilha só: Radar + Preferências + Exclusões + (ocultas) Controle, Log, Saúde, Sobre
NOME_PAGINA = "Lista para abrir no celular.html"  # cópia da tela; até a 0.7.9 se chamava "LexSuiteONE - Radar.html"
NOME_PAGINA_ANTIGO = "LexSuiteONE - Radar.html"
SUBPASTA_ATUALIZACAO = "atualizacao"


def candidatas():
    """Pastas do Google Drive para computador que existem aqui ("Meu Drive" / "My Drive"), na ordem de probabilidade.
    OneDrive e Dropbox ficam de fora da lista (não testados; "sob consulta"); dá para escolher qualquer pasta à mão."""
    home = os.path.expanduser("~")
    opcoes = []
    for base in (home, os.path.join(home, "Google Drive")):
        for nome in ("Meu Drive", "My Drive"):
            opcoes.append(os.path.join(base, nome))
    if os.name == "nt":
        for letra in "DEFGHIJKLMNOPQRSTUVWXYZ":
            for nome in ("Meu Drive", "My Drive"):
                opcoes.append(f"{letra}:\\{nome}")
    achadas = []
    for p in opcoes:
        if os.path.isdir(p) and p not in achadas:
            achadas.append(p)
    return achadas


def no_google_drive(pasta):
    """True se a pasta fica dentro do Meu Drive / My Drive do Google Drive para computador."""
    partes = [x.lower() for x in os.path.normpath(str(pasta or "")).replace("\\", "/").split("/")]
    return "meu drive" in partes or "my drive" in partes


def subpasta_para(cfg, nome_produto="RADAR JUDICIAL"):
    """Nome da pasta da planilha. Quem já tinha pasta escolhida continua com a dela ("LexSuiteONE"); instalação nova
    usa "<produto> - planilha", para não confundir com a pasta do programa (C:\\LexSuiteONE)."""
    c = cfg.get("compartilhar") or {}
    if c.get("pasta"):
        return c.get("subpasta") or "LexSuiteONE"
    return f"{nome_produto} - planilha"


def pasta_base(cfg):
    c = cfg.get("compartilhar") or {}
    return os.path.join(c["pasta"], c.get("subpasta") or "LexSuiteONE") if c.get("pasta") else ""


def pasta_atualizacao(cfg):
    base = pasta_base(cfg)
    return os.path.join(base, SUBPASTA_ATUALIZACAO) if base else ""


def testar(pasta, subpasta="LexSuiteONE", criar=False):
    """Confere se dá para criar a subpasta e gravar nela (com criar=True, cria também a pasta escolhida).
    Devolve (ok, mensagem)."""
    if pasta and not os.path.isdir(pasta) and criar:
        try:
            os.makedirs(pasta, exist_ok=True)
        except OSError as e:
            return False, f"Não consegui criar a pasta {pasta} ({e.__class__.__name__})."
    if not pasta or not os.path.isdir(pasta):
        return False, "Essa pasta ainda não existe neste computador."
    alvo = os.path.join(pasta, subpasta)
    existia = os.path.isdir(alvo)
    try:
        os.makedirs(alvo, exist_ok=True)
        prova = os.path.join(alvo, "teste-lexsuite.txt")
        with open(prova, "w", encoding="utf-8") as f:
            f.write("ok\n")
        os.remove(prova)
        if not existia:
            os.rmdir(alvo)  # só testar não deixa pasta vazia para trás; ela nasce ao salvar
    except OSError as e:
        return False, f"Não consegui gravar em {alvo} ({e.__class__.__name__})."
    return True, f"Pronto: a planilha vai ficar em {alvo}."


def _sobre(cfg, versao, chave_impressao, ultima):
    return [["Item", "Valor"],
            ["Produto", "LexSuiteONE · JUDICIAL (Radar Trabalhista)"], ["Versão", versao], ["Escritório", cfg.get("escritorio", "")],
            ["Computador", platform.node()], ["Sistema", f"{platform.system()} {platform.release()}"],
            ["Python", platform.python_version()], ["Pasta do robô", cfg.get("_pasta_robo", "")],
            ["Tribunais", ", ".join((cfg.get("radar") or {}).get("tribunais") or [])],
            ["Última rodada", ultima], ["Chave de atualização (impressão)", chave_impressao or "sem chave: atualização desligada"],
            ["Suporte", preferencias.SUPORTE], ["Conta de sistemas (acesso à pasta)", preferencias.SISTEMAS]]


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
    # 0.7.13: a aba Log mostra o histórico de leituras, uma linha por tribunal e por tentativa, visível ao escritório.
    from . import causas
    rotulo = {"ok": "Lido", "ainda_nao_liberado_3h": "Diário de hoje só às 3h (não é erro)", "nao_publicado": "Ainda não publicado",
              "governo_fora": "Site do CNJ fora do ar", "bloqueio_fora_do_brasil": "Fora do Brasil", "sem_internet": "Sem internet",
              "erro_do_programa": "Erro do programa"}
    log = [["Quando (hora local e fuso)", "Origem", "Tribunal", "Dias pedidos", "Resposta do site", "Situação", "O que o programa fez",
            "Duração (s)", "Versão", "Explicação"]]
    for e in banco.execucoes("tentativa", 1000):
        c = e.get("causa", "")
        log.append([e.get("quando_local") or e.get("quando", ""), e.get("origem", ""), e.get("tribunal", ""), e.get("dias_pedidos", ""),
                    e.get("http", ""), rotulo.get(c, c), e.get("fez", ""), e.get("duracao", ""), e.get("versao", ""),
                    "" if c == "ok" else causas.mensagem(c)])
    for e in banco.execucoes("radar", 200):  # rodadas antigas (antes da 0.7.13) e o resumo de cada rodada
        log.append([e.get("quando", ""), "resumo da rodada", ", ".join(e.get("tribunais") or []), "", "",
                    "Lido" if e.get("resultado") == "ok" else (rotulo.get(e.get("causa", ""), "Parou")),
                    f"{e.get('lidas', '')} publicações, {e.get('novas', '')} ações novas, {e.get('com_cnpj', '')} com CNPJ",
                    e.get("duracao", ""), e.get("versao", ""), causas.mensagem(e["causa"]) if e.get("causa") else (e.get("erro") or "")])
    saude = [["Quando", "Fonte", "Situação", "Detalhe"]]
    for e in banco.execucoes("saude", 300):
        saude.append([e.get("quando", ""), e.get("fonte", ""), e.get("situacao", ""), e.get("detalhe", "")])
    ultima = log[1][0] if len(log) > 1 else ""
    chaves = [chave for _, chave in colunas]
    moeda = [chaves.index(k) for k in ("capital_social", "valor_causa") if k in chaves]
    destacar = set()
    if "valor_causa" in chaves:
        minimo = float(pagina.get("valor_minimo") or 0)
        j = chaves.index("valor_causa")
        destacar = {n for n, l in enumerate(linhas[1:], 1)
                    if isinstance(l[j], (int, float)) and not isinstance(l[j], bool) and minimo and l[j] >= minimo}
    planilha.escrever_xlsx(caminho, [
        {"nome": "Radar", "linhas": linhas, "visual": True, "filtro": True, "moeda": moeda, "destacar": destacar,
         "larguras": [8, 9, 34, 26, 12, 12, 40, 18, 22, 16, 36, 20, 18, 16, 28, 40, 15, 16, 12, 30, 30, 30, 10]},
    ] + [dict(a, visual=True) for a in editaveis] + [
        {"nome": NOME_COMO_USAR, "linhas": como_usar(_nome_produto(pasta_robo)), "visual": True, "larguras": [24, 70, 70]},
        {"nome": "Log", "linhas": log, "visual": True, "filtro": True, "larguras": [24, 16, 10, 22, 10, 26, 40, 10, 8, 60]},
        {"nome": "Saúde", "linhas": saude, "oculta": True, "larguras": [20, 18, 10, 80]},
        {"nome": "Sobre", "linhas": _sobre(dict(cfg, _pasta_robo=pasta_robo), versao, chave_impressao, ultima), "oculta": True, "larguras": [30, 80]},
    ])
    html = os.path.join(pasta_robo, "saida", "radar", "radar.html") if pasta_robo else ""
    if html and os.path.exists(html):
        shutil.copyfile(html, os.path.join(base, NOME_PAGINA))
        antiga = os.path.join(base, NOME_PAGINA_ANTIGO)
        if os.path.exists(antiga):
            try:
                os.remove(antiga)  # o nome antigo confundia (parecia uma segunda planilha)
            except OSError:
                pass
    aviso(f"  Planilha compartilhada: {caminho}")
    return caminho


NOME_COMO_USAR = "Como usar"


def _nome_produto(pasta_robo):
    try:
        with open(os.path.join(pasta_robo, "marca.json"), encoding="utf-8") as f:
            return " ".join(str(json.load(f).get("nome") or "").split())[:40] or "RADAR JUDICIAL"
    except (OSError, ValueError, AttributeError, TypeError):
        return "RADAR JUDICIAL"


def como_usar(produto="RADAR JUDICIAL"):
    """Aba visível com o passo a passo da planilha, em português e inglês. Não tem dado de cliente."""
    return [
        ["Assunto / Topic", "Como fazer", "How to"],
        ["O que é esta planilha", f"O {produto} grava aqui, sozinho, a lista de ações novas a cada leitura. Não precisa "
         "copiar nem compartilhar nada: a planilha se atualiza no lugar.",
         f"{produto} writes the list of new lawsuits here by itself after every reading. Nothing to copy or share: "
         "the file updates in place."],
        ["Filtrar", "Clique na setinha do cabeçalho (Tribunal, Setor, Porte, Cidade/UF...) e marque o que quer ver.",
         "Click the small arrow in the header (Court, Sector, Size, City...) and tick what you want to see."],
        ["Ordenar pelo valor", "Na setinha de \"Valor da causa\", escolha \"Classificar do maior para o menor\".",
         "On the \"Valor da causa\" arrow, choose \"Sort largest to smallest\"."],
        ["Destaque em latão", "O valor da causa com fundo latão claro está acima do valor mínimo escolhido na Configuração.",
         "A claim value with a light brass background is above the minimum value set in Settings."],
        ["Excluir uma empresa", "Na aba Exclusões, escreva o nome ou o CNPJ e o motivo. Na próxima leitura ela some da lista.",
         "In the Exclusões tab, type the name or CNPJ and the reason. It leaves the list on the next reading."],
        ["Planilha aberta", "Se a planilha estiver aberta no Excel na hora da leitura, o programa avisa e grava depois. "
         "Feche e use o botão \"Gravar a planilha agora\".",
         "If the file is open in Excel during a reading, the program warns you and writes it later. Close it and use "
         "the \"Write the spreadsheet now\" button."],
        ["Google Planilhas", "Funciona também: abra pelo Google Drive. Os filtros e as cores vêm junto.",
         "It also works in Google Sheets: open it from Google Drive. Filters and colours come along."],
    ]


def _celula(v):
    if isinstance(v, list):
        return " | ".join(str(x) for x in v)
    if isinstance(v, bool):
        return "sim" if v else ""
    return "" if v is None else v
