"""A pasta compartilhada (Google Drive para computador, OneDrive, Dropbox): onde o robô deixa a planilha e a página
e de onde lê o controle e as atualizações. Nada de senha: é só uma pasta do computador que o Drive sincroniza."""

import json
import os
import platform
import shutil

from . import planilha, preferencias

NOME_RADAR = preferencias.NOME_ARQUIVO  # uma planilha só: Radar + Preferências + Exclusões + (ocultas) Controle, Log, Saúde, Sobre
NOME_PAGINA = "Retrato da última leitura.html"  # cópia da tela (0.7.14; antes "Lista para abrir no celular.html")
NOMES_PAGINA_ANTIGOS = ("LexSuiteONE - Radar.html", "Lista para abrir no celular.html")
NOME_PAGINA_ANTIGO = NOMES_PAGINA_ANTIGOS[0]
NOME_HISTORICO = "Histórico de leituras"
AVISO_RADAR = ("ATENÇÃO: esta planilha é regravada pelo {produto} a cada leitura. Pode filtrar e ordenar à vontade; "
               "para anotar ou mexer, use \"Gerar uma cópia\" no programa (o que for digitado aqui se perde na próxima leitura).")
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
        doc = planilha.ler_xlsx(caminho, so_abas=preferencias.ABAS_EDITAVEIS)
    except Exception as e:
        aviso(f"  Planilha em uso ou ilegível ({e.__class__.__name__}); deixo como está nesta rodada.")
        return [], False
    atuais = {a["nome"]: a for a in doc["abas"]}
    abas = []
    for padrao in preferencias.abas_padrao():
        existente = atuais.get(padrao["nome"])
        if existente and existente["linhas"]:
            linhas = [list(l) for l in existente["linhas"]]
            if padrao["nome"] == "Preferências":  # 0.7.16: ajustes novos entram no fim, sem mexer no que o escritório editou
                tem = {str(l[0]).strip() for l in linhas if l}
                linhas += [list(l) for l in padrao["linhas"][1:] if l[0] not in tem]
            abas.append({"nome": padrao["nome"], "linhas": linhas, "oculta": padrao.get("oculta", False), "larguras": padrao.get("larguras")})
        else:
            abas.append(padrao)
    return abas, True


def criar_se_faltar(cfg, versao="", pasta_robo="", aviso=print):
    """Cria a planilha única com o Radar vazio e as abas editáveis padrão. Nunca sobrescreve a que existe."""
    base = pasta_base(cfg)
    if not base:
        return ""
    os.makedirs(base, exist_ok=True)
    preferencias.migrar_nome(base, aviso)
    os.makedirs(os.path.join(base, "Cópias de segurança"), exist_ok=True)
    caminho = os.path.join(base, NOME_RADAR)
    if os.path.exists(caminho):
        return caminho
    cabecalho = ["Hora", "Tribunal", "Vara", "Processo", "Rito", "Distribuída em", "Empresa(s)", "CNPJ"]
    planilha.escrever_xlsx(caminho, [{"nome": "Radar", "linhas": [cabecalho], "larguras": [8, 9, 34, 26, 12, 12, 40, 18]}]
                           + preferencias.abas_padrao()
                           + [{"nome": "Sobre", "linhas": _sobre(dict(cfg, _pasta_robo=pasta_robo), versao, "", ""), "oculta": True, "larguras": [30, 80]}])
    aviso(f"  Criei a planilha: {caminho}")
    return caminho


def _linhas_lista(itens, colunas, linha_csv):
    cabecalho = [titulo for titulo, _ in colunas] + ["Excluída (motivo)", "Ações na janela"]
    linhas = [cabecalho]
    for it in itens:
        l = linha_csv(it)
        linhas.append([_celula(l.get(chave)) for _, chave in colunas] + [it.get("excluida") or "", it.get("acoes_na_janela", "")])
    return linhas


def _destacar(linhas, chaves, minimo):
    if "valor_causa" not in chaves or not minimo:
        return set()
    j = chaves.index("valor_causa")
    return {n for n, l in enumerate(linhas[1:], 1) if isinstance(l[j], (int, float)) and not isinstance(l[j], bool) and l[j] >= minimo}


def gravar_radar(cfg, pagina, banco, versao, colunas, linha_csv, chave_impressao="", pasta_robo="", aviso=print, arquivo=None,
                 frente="trabalhista", itens=None, aviso_tamanho="", processos=None):
    """Regrava a planilha da frente (0.7.16: uma por frente): aba Radar (a lista), Arquivo, Contatos, as abas editáveis
    preservadas (Preferências, Exclusões, Controle oculta) e as abas Histórico, Saúde e Sobre. Também copia a página HTML.
    `itens`: as linhas da aba Radar (padrão: as da página). `processos`: só os contatos desses processos.
    Devolve o caminho da planilha, ou '' se não houver pasta ou se a planilha estiver em uso."""
    base = pasta_base(cfg)
    if not base:
        return ""
    os.makedirs(base, exist_ok=True)
    os.makedirs(os.path.join(base, "Cópias de segurança"), exist_ok=True)
    preferencias.migrar_nome(base, aviso)
    caminho = os.path.join(base, preferencias.NOMES_FRENTE.get(frente) or NOME_RADAR)
    editaveis, ok = _abas_editaveis(caminho, aviso)
    if not ok:
        return ""
    linhas = _linhas_lista(pagina.get("itens") or [] if itens is None else itens, colunas, linha_csv)
    # 0.7.13: a aba Log mostra o histórico de leituras, uma linha por tribunal e por tentativa, visível ao escritório.
    from . import causas
    rotulo = {"ok": "Lido", "ainda_nao_liberado_3h": "Diário de hoje só às 3h (não é erro)", "nao_publicado": "Ainda não publicado",
              "governo_fora": "Site do CNJ fora do ar", "bloqueio_fora_do_brasil": "Fora do Brasil", "sem_internet": "Sem internet",
              "erro_do_programa": "Erro do programa", "interrompida": "Interrompida a pedido"}
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
    minimo = float(pagina.get("valor_minimo") or 0)
    produto = _nome_produto(pasta_robo)
    larguras = [14, 11, 8, 9, 34, 26, 12, 12, 40, 18, 22, 16, 36, 20, 18, 16, 28, 40, 15, 16, 12, 30, 40, 10, 40, 30, 30, 10]
    abas = [{"nome": "Radar", "linhas": linhas, "visual": True, "filtro": True, "moeda": moeda, "destacar": _destacar(linhas, chaves, minimo),
             "aviso": ((aviso_tamanho + " ") if aviso_tamanho else "") + AVISO_RADAR.format(produto=produto), "larguras": larguras}]
    if arquivo is not None:  # 0.7.16: últimos N dias + todo processo trabalhado; o resto fica no programa e nas cópias
        la = _linhas_lista(arquivo, colunas, linha_csv)
        abas.append({"nome": "Arquivo", "linhas": la, "visual": True, "filtro": True, "moeda": moeda, "destacar": _destacar(la, chaves, minimo),
                     "aviso": "Arquivo: o que não está na aba Radar, dos últimos dias, e todo processo trabalhado (Em análise, Em contato, "
                              "Virou cliente), inclusive arquivados. O resto continua no " + produto + " (tela Arquivo) e nas cópias de segurança. Só para consulta.",
                     "larguras": larguras})
    contatos = [["Processo", "Empresa", "Canal", "Contato", "De pessoa (sócio)", "Fonte", "Data", "Confiança", "Origem", "Validação", "Observação"]]
    for c in (banco.contatos() if hasattr(banco, "contatos") else []):
        if processos is not None and c["processo"] not in processos:
            continue
        contatos.append([c["processo"], c["empresa"], c["canal"], c["valor"], "sim" if c["de_pessoa"] else "", c["fonte"], c["data"],
                         c["confianca"], c["origem"], c["validacao"], c["observacao"]])
    abas.append({"nome": "Contatos", "linhas": contatos, "visual": True, "filtro": True,
                 "aviso": "Contatos encontrados (Receita, área logada ou digitados), sempre com a fonte e a data. Os da Receita também estão na aba Radar.",
                 "larguras": [26, 34, 11, 34, 10, 20, 11, 10, 12, 12, 40]})
    planilha.escrever_xlsx(caminho, abas + [dict(a, visual=True) for a in editaveis] + [
        {"nome": NOME_COMO_USAR, "linhas": como_usar(produto), "visual": True, "larguras": [24, 70, 70]},
        {"nome": NOME_HISTORICO, "linhas": log, "visual": True, "filtro": True, "larguras": [24, 16, 10, 22, 10, 26, 40, 10, 8, 60]},
        {"nome": "Saúde", "linhas": saude, "oculta": True, "larguras": [20, 18, 10, 80]},
        {"nome": "Sobre", "linhas": _sobre(dict(cfg, _pasta_robo=pasta_robo), versao, chave_impressao, ultima), "oculta": True, "larguras": [30, 80]},
    ], so_leitura_recomendado=True)
    html = os.path.join(pasta_robo, "saida", "radar", "radar.html") if pasta_robo else ""
    if html and os.path.exists(html):
        shutil.copyfile(html, os.path.join(base, NOME_PAGINA))
        for nome in NOMES_PAGINA_ANTIGOS:  # os nomes antigos confundiam (pareciam outra planilha)
            antiga = os.path.join(base, nome)
            if os.path.exists(antiga):
                try:
                    os.remove(antiga)
                except OSError:
                    pass
    aviso(f"  Planilha compartilhada: {caminho}")
    return caminho


NOME_COMO_USAR = "Como usar"


def gerar_copia(cfg, agora=None):
    """0.7.14: cópia da planilha para o escritório trabalhar (anotar, mexer), na subpasta "Cópias", sem a proteção, sem
    a marca de somente leitura e com o aviso trocado. O RADAR nunca mexe nas cópias. Devolve (ok, caminho ou motivo)."""
    import datetime as _dt
    import re as _re
    import zipfile as _zip
    base = pasta_base(cfg)
    origem = preferencias.caminho(base) if base else ""
    if not origem or not os.path.exists(origem):
        return False, "A planilha ainda não existe: faça uma leitura primeiro."
    agora = agora or _dt.datetime.now()
    destino_pasta = os.path.join(base, "Cópias")
    os.makedirs(destino_pasta, exist_ok=True)
    destino = os.path.join(destino_pasta, f"{os.path.splitext(NOME_RADAR)[0]} - cópia {agora:%Y-%m-%d %Hh%Mm%S}.xlsx")
    marca_copia = f"Cópia de {agora:%d/%m/%Y %H:%M}: pode anotar e mexer à vontade. O RADAR não altera as cópias."
    try:
        with _zip.ZipFile(origem) as zin, _zip.ZipFile(destino, "w", _zip.ZIP_DEFLATED) as zout:
            for info in zin.infolist():
                dados = zin.read(info.filename)
                if info.filename.startswith("xl/worksheets/") or info.filename == "xl/workbook.xml":
                    t = dados.decode("utf-8")
                    t = _re.sub(r"<sheetProtection[^>]*/>", "", t)
                    t = _re.sub(r"<fileSharing[^>]*/>", "", t)
                    t = _re.sub(r"(<c r=\"A1\" s=\"7\" t=\"inlineStr\"><is><t[^>]*>)[^<]*(</t>)", lambda m: m.group(1) + marca_copia + m.group(2), t)
                    dados = t.encode("utf-8")
                zout.writestr(info, dados)
    except (OSError, _zip.BadZipFile) as e:
        return False, f"Não consegui copiar a planilha ({e.__class__.__name__})."
    return True, destino


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
