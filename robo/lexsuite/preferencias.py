"""Critérios da lista e controle do escritório.

0.7.33 (decisão do dono, 12/Nov; desenho da Arquitetura, documentacao/DESENHO-CRITERIOS-CHAMADOS-CNPJ-2026-11-12.md, seção 1):
os critérios da lista (valor mínimo, mínimo de ações, jurídico próprio, sócios, Arquivo, limite) e as empresas excluídas são
de cada pessoa, neste computador, por área (trabalhista, tributário, cível, empresarial), no arquivo `criterios.json` ao lado
do `config.json`. A planilha compartilhada não guarda nem é lida para isso; na primeira abertura da 0.7.33, as abas
Preferências e Exclusões das planilhas viram o `criterios.json` (uma vez só). A aba Controle (oculta) continua na planilha.
"""

import datetime as dt
import os
import re

from . import classificar as cl
from . import documento
from . import planilha

# 0.7.16: uma planilha por frente, na mesma pasta (decisão de 09/Nov, documentacao/DESENHO-PLANILHA-GRANDE.md). A frente
# trabalhista é a de hoje; as outras nascem sozinhas quando houver processos delas. A planilha única antiga
# (LexSuiteONE.xlsx) vira a trabalhista na primeira leitura, com as abas editadas.
NOMES_FRENTE = {"trabalhista": "LexSuiteONE - Trabalhista.xlsx", "tributario": "LexSuiteONE - Tributário.xlsx",
                "civel": "LexSuiteONE - Cível.xlsx", "empresarial": "LexSuiteONE - Empresarial.xlsx"}
NOME_ARQUIVO = NOMES_FRENTE["trabalhista"]
NOME_ANTIGO = "LexSuiteONE.xlsx"

PADRAO = {"valor_minimo": 100000, "minimo_acoes": 1, "janela_dias": 30, "teto_capital_gigante": 50000000,
          "esconder_gigantes": False, "esconder_excluidas": True, "mostrar_socios": True,
          "dias_arquivo": 90, "limite_linhas": 60000}
CHAVES = {
    "Valor mínimo da causa (R$)": "valor_minimo",
    "Mínimo de ações da mesma empresa": "minimo_acoes",
    "Janela do mínimo de ações (dias)": "janela_dias",
    "Capital social que indica jurídico próprio (R$)": "teto_capital_gigante",
    "Esconder jurídico próprio provável": "esconder_gigantes",
    "Esconder clientes e exclusões": "esconder_excluidas",
    "Mostrar sócios e administradores": "mostrar_socios",
    "Dias na aba Arquivo": "dias_arquivo",
    "Limite de linhas da planilha": "limite_linhas",
}
LINHAS_PREFERENCIAS = [
    ["Ajuste", "Valor", "Como usar"],
    ["Valor mínimo da causa (R$)", 100000, "Filtro \"Acima de\" na tela e na planilha. Ações abaixo continuam na lista."],
    ["Mínimo de ações da mesma empresa", 1, "Ex.: 3 = só destacar empresa com 3 ou mais ações novas na janela de dias. 1 = todas."],
    ["Janela do mínimo de ações (dias)", 30, "Quantos dias para trás contar as ações da mesma empresa."],
    ["Capital social que indica jurídico próprio (R$)", 50000000, "Acima disso a empresa é marcada \"jurídico próprio provável\" e vai para o fim da lista."],
    ["Esconder jurídico próprio provável", "não", "sim ou não."],
    ["Esconder clientes e exclusões", "sim", "sim ou não. A aba Exclusões lista quem não deve aparecer."],
    ["Mostrar sócios e administradores", "sim", "sim ou não. São nomes de pessoas do cadastro público da Receita; se o escritório não precisa, desligue."],
    ["Dias na aba Arquivo", 90, "A aba Arquivo mostra os últimos N dias e todo processo trabalhado (Em análise, Em contato, Virou cliente). O resto continua no programa e na tela Arquivo."],
    ["Limite de linhas da planilha", 60000, "Acima de 80% o RADAR avisa; a 100% guarda uma cópia de segurança e enxuga a aba Arquivo sozinho. Mais linhas deixam o Excel lento."],
]
LINHAS_EXCLUSOES = [
    ["Nome ou CNPJ", "Motivo"],
    ["(exemplo, pode apagar) Empresa Exemplo Ltda", "cliente atual"],
]
# Contato de atendimento do JUDICIAL. integracao@ é só para sistemas (compartilhamento do Drive), nunca para pessoas.
SUPORTE = "judicial@solverone.com.br"
SISTEMAS = "integracao@solverone.com.br"

LINHAS_CONTROLE = [
    ["Chave", "Valor", "O que faz"],
    ["ativo", "sim", "não = o robô não roda e mostra a mensagem abaixo."],
    ["validade", "", "aaaa-mm-dd. Depois dessa data o robô para e avisa."],
    ["versao_minima", "", "Se a versão instalada for menor, o robô pede atualização antes de rodar."],
    ["mensagem", "", "Texto mostrado na tela do escritório (avisos do suporte)."],
    ["suporte", SUPORTE, "Contato do suporte (atendimento a pessoas)."],
]


def caminho(pasta_base, frente="trabalhista"):
    """Caminho da planilha da frente. Antes, troca o nome da planilha única antiga, se for o caso."""
    if not pasta_base:
        return ""
    migrar_nome(pasta_base)
    if frente == "trabalhista" and nome_pendente(pasta_base):  # a antiga está aberta: continua valendo até trocar de nome
        return os.path.join(pasta_base, NOME_ANTIGO)
    return os.path.join(pasta_base, NOMES_FRENTE.get(frente) or NOME_ARQUIVO)


def nome_pendente(pasta_base):
    """True quando a planilha antiga ainda não pôde trocar de nome (aberta no Excel): nada pode criar a nova, senão as
    abas editadas pelo escritório ficariam na antiga, esquecida."""
    return bool(pasta_base) and os.path.exists(os.path.join(pasta_base, NOME_ANTIGO)) and not os.path.exists(os.path.join(pasta_base, NOME_ARQUIVO))


def migrar_nome(pasta_base, aviso=None):
    """LexSuiteONE.xlsx (até a 0.7.15) vira "LexSuiteONE - Trabalhista.xlsx". Se estiver aberta no Excel, fica para a
    próxima vez. Devolve True quando trocou."""
    antigo, novo = os.path.join(pasta_base, NOME_ANTIGO), os.path.join(pasta_base, NOME_ARQUIVO)
    if not os.path.exists(antigo) or os.path.exists(novo):
        return False
    try:  # 0.7.17: antes de trocar o nome, guarda uma cópia da antiga em "Cópias de segurança" (uma vez só)
        import shutil
        pasta_c = os.path.join(pasta_base, "Cópias de segurança", "antes da troca de nome")
        os.makedirs(pasta_c, exist_ok=True)
        if not os.path.exists(os.path.join(pasta_c, NOME_ANTIGO)):
            shutil.copy2(antigo, os.path.join(pasta_c, NOME_ANTIGO))
    except OSError:
        pass
    try:
        os.replace(antigo, novo)
    except OSError:
        if aviso:
            aviso(f"  A planilha {NOME_ANTIGO} está aberta: o novo nome ({NOME_ARQUIVO}) fica para a próxima leitura.")
        return False
    if aviso:
        aviso(f"  A planilha passou a se chamar {NOME_ARQUIVO} (uma por frente); as abas editadas foram mantidas.")
    return True


def planilhas_existentes(pasta_base):
    """[(frente, caminho)] das planilhas que já existem na pasta, na ordem das frentes."""
    if not pasta_base:
        return []
    migrar_nome(pasta_base)
    saida = [(f, os.path.join(pasta_base, n)) for f, n in NOMES_FRENTE.items() if os.path.exists(os.path.join(pasta_base, n))]
    if nome_pendente(pasta_base):
        saida.insert(0, ("trabalhista", os.path.join(pasta_base, NOME_ANTIGO)))
    return saida


ABAS_EDITAVEIS = ("Controle",)  # 0.7.33: Preferências e Exclusões saíram da planilha (critérios por pessoa)
ABAS_ANTIGAS = ("Preferências", "Exclusões")  # lidas uma vez só, na migração


def abas_padrao():
    """A aba Controle (oculta) como nasce na primeira vez. 0.7.33: as abas Preferências e Exclusões não existem mais."""
    return [{"nome": "Controle", "linhas": [list(l) for l in LINHAS_CONTROLE], "oculta": True, "larguras": [18, 36, 70]}]


def _sim(v):
    return cl.sem_acento(str(v if v is not None else "")).strip().lower() in ("sim", "s", "yes", "true", "1", "x", "verdadeiro")


def _numero(v, padrao):
    if isinstance(v, bool):
        return padrao
    if isinstance(v, (int, float)):
        return v
    t = str(v or "").strip().replace("R$", "").replace(" ", "")
    if not t:
        return padrao
    if "," in t:  # formato brasileiro: 1.234,56
        t = t.replace(".", "").replace(",", ".")
    elif t.count(".") > 1:  # 1.234.567 sem centavos
        t = t.replace(".", "")
    try:
        n = float(t)
        return int(n) if n == int(n) else n
    except (ValueError, OverflowError):  # revisão da 0.7.28: "1e400", "inf" e "NaN" voltam ao padrão
        return padrao


def versao_tupla(v):
    return tuple(int(x) for x in re.findall(r"\d+", str(v or ""))[:3]) or (0,)


LIMITES = {"valor_minimo": (0, 1e12), "minimo_acoes": (1, 100), "janela_dias": (1, 365), "teto_capital_gigante": (0, 1e15),
           "dias_arquivo": (7, 3650), "limite_linhas": (1000, 1000000)}


MAX_EXCLUSOES = 5000
INTEIROS = ("minimo_acoes", "janela_dias", "dias_arquivo", "limite_linhas")


AREAS = tuple(NOMES_FRENTE)  # trabalhista, tributario, civel, empresarial
ARQUIVO_CRITERIOS = "criterios.json"


def valores_validos(valores):
    """Os critérios como a tela os manda (ou como estão no arquivo), dentro dos limites; fora do limite volta ao padrão.
    0.7.33: valor mínimo vazio ou 0 = sem mínimo (antes virava 100 mil)."""
    saida = {}
    for chave, pad in PADRAO.items():
        v = (valores or {}).get(chave, pad)
        if chave.startswith(("esconder", "mostrar")):
            saida[chave] = v is True or (not isinstance(v, bool) and _sim(v))
            continue
        if chave == "valor_minimo" and (v is None or str(v).strip() == ""):
            saida[chave] = 0
            continue
        n = _numero(v, pad)
        mn, mx = LIMITES.get(chave, (0, 1e15))
        try:
            n = n if mn <= float(n) <= mx else pad
            if chave in INTEIROS and n != int(n):  # 0.7.29: 2,5 ações ou 2,5 dias não existem
                n = pad
        except (TypeError, ValueError, OverflowError):
            n = pad
        saida[chave] = int(n) if isinstance(n, float) and n == int(n) else n
    return saida


def e_documento(texto):
    """O texto parece um CPF ou CNPJ digitado (e não um nome): sem espaço, só números, letras e . / -, com 8 ou mais números."""
    t = str(texto or "").strip()
    if not re.fullmatch(r"[0-9A-Za-z./\-]+", t):
        return False
    limpo = re.sub(r"[^0-9A-Za-z]", "", t)
    # só números (CPF, CNPJ), ou 14 caracteres com os 2 últimos números (CNPJ com letras); "ACME12345678" é nome
    return limpo.isdigit() and len(limpo) >= 8 or (len(limpo) == 14 and limpo[-2:].isdigit() and sum(c.isdigit() for c in limpo) >= 6)


def exclusao_valida(nome):
    """0.7.33 (dono): nome é livre; CPF ou CNPJ (inclusive o alfanumérico) tem de ser válido. Devolve (nome, cnpj) ou None."""
    nome = str(nome or "").strip()[:160]
    if not nome:
        return None
    if not e_documento(nome):
        return nome, None
    if documento.valido(nome):
        return documento.formatar(nome), documento.limpar(nome)
    if documento.cpf_valido(nome):
        return documento.formatar_cpf(nome), None
    return None


def exclusoes_validas(lista, limite=None):
    """Lista de exclusões limpa: sem repetidas, sem documento inválido, até MAX_EXCLUSOES."""
    saida, vistos = [], set()
    for e in (lista or []):  # revisão da Operação: deduplica antes de cortar no limite
        if len(saida) >= (limite or MAX_EXCLUSOES):
            break
        if not isinstance(e, dict):  # revisão da 0.7.28: item que não é {nome, motivo} é ignorado
            continue
        ok = exclusao_valida(e.get("nome"))
        cj = e.get("cnpj")
        if ok and ok[1] is None and cj and documento.valido(cj):  # 0.7.36 (dono): nome vindo da consulta + CNPJ, os dois valem
            ok = (ok[0], documento.limpar(cj))
        if not ok:
            continue
        # revisão da 0.7.36: com CNPJ, repete só o mesmo CNPJ (filial com o mesmo nome e outro CNPJ fica); sem CNPJ, só o
        # mesmo nome escrito igual (sem ignorar LTDA ou S.A., para não juntar duas razões sociais diferentes)
        nome_k = ("nome", ok[0].strip().lower())
        if (ok[1] and ("cnpj", ok[1]) in vistos) or (not ok[1] and nome_k in vistos):
            continue
        vistos.add(("cnpj", ok[1]) if ok[1] else nome_k); vistos.add(nome_k)
        saida.append({"nome": ok[0], "cnpj": ok[1], "motivo": str(e.get("motivo") or "").strip()[:200],
                      "desde": str(e.get("desde") or dt.date.today().isoformat())[:10]})
    return saida


def pasta_dados(banco):
    """A pasta do programa (a do config.json e do lexsuite.db), pelo banco; '' se o banco é só em memória."""
    c = getattr(banco, "caminho", "") or ""
    if not c or c == ":memory:" or c.startswith("file:"):
        return ""
    return os.path.dirname(os.path.abspath(c))


def caminho_criterios(pasta):
    return os.path.join(pasta, ARQUIVO_CRITERIOS) if pasta else ""


def _ler_json_criterios(c):
    import json
    with open(c, encoding="utf-8") as f:
        d = json.load(f)
    if not isinstance(d, dict) or not isinstance(d.get("areas"), dict):
        raise ValueError("formato")
    return d


def ler_criterios(pasta):
    """O criterios.json desta pessoa ({"versao", "areas": {...}}), None se não existe. Revisão da 0.7.33: ilegível (vazio,
    lixo, sem "areas") usa o criterios.json.anterior, se ele estiver bom ("restaurado"); senão, padrões e "erro"."""
    c = caminho_criterios(pasta)
    if not c or not os.path.exists(c):
        return None
    try:
        return _ler_json_criterios(c)
    except (OSError, ValueError) as e:
        try:
            d = _ler_json_criterios(c + ".anterior")
            d["restaurado"] = True
            return d
        except (OSError, ValueError):
            return {"versao": 1, "areas": {}, "erro": e.__class__.__name__}


def gravar_criterios(pasta, dados):
    """Grava o criterios.json de forma atômica. A cópia criterios.json.anterior só é renovada quando o atual está bom
    (revisão da 0.7.33: um arquivo ilegível nunca passa por cima do .anterior bom)."""
    import json
    import shutil
    c = caminho_criterios(pasta)
    if not c:
        return False
    dados = {"versao": 1, "atualizado_em": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
             "origem": dados.get("origem", "tela"), "areas": dados.get("areas") or {}}
    if os.path.exists(c):
        try:
            _ler_json_criterios(c)
            shutil.copy2(c, c + ".anterior")
        except (OSError, ValueError):
            pass
    tmp = c + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=1)
    os.replace(tmp, c)
    return True


def criterios_da_area(pasta, area):
    """(valores, exclusoes) desta pessoa para a área; o que falta vem do padrão."""
    d = ler_criterios(pasta) or {"areas": {}}
    a = (d.get("areas") or {}).get(area if area in AREAS else "trabalhista") or {}
    return valores_validos(a), exclusoes_validas(a.get("exclusoes") or [])


def salvar_area(pasta, area, valores, exclusoes, todas=False):
    """Grava os critérios de uma área (ou de todas, com "Copiar para as outras áreas")."""
    d = ler_criterios(pasta) or {"areas": {}}
    if d.get("erro"):  # revisão da 0.7.33: arquivo ilegível e sem .anterior bom: não grava só uma área por cima
        raise ValueError("criterios_ilegivel")
    areas = dict(d.get("areas") or {})
    bloco = dict(valores_validos(valores), exclusoes=exclusoes_validas(exclusoes))
    for a in (AREAS if todas else (area if area in AREAS else "trabalhista",)):
        areas[a] = dict(bloco, exclusoes=[dict(e) for e in bloco["exclusoes"]])
    return gravar_criterios(pasta, {"origem": "tela", "areas": areas})


def copiar_area(pasta, origem, destinos, modo="substituir", partes=("valores", "exclusoes")):
    """0.7.36 (dono): copia os limites e opções ("valores") e/ou as empresas excluídas da área de origem para as áreas
    escolhidas. "substituir" troca o que havia; "acrescentar" soma as empresas, sem repetir o mesmo CNPJ ou o mesmo nome
    (os limites e opções, quando escolhidos, são sempre trocados)."""
    d = ler_criterios(pasta) or {"areas": {}}
    if d.get("erro"):
        raise ValueError("criterios_ilegivel")
    areas = dict(d.get("areas") or {})
    o_ = areas.get(origem if origem in AREAS else "trabalhista") or {}
    val_o, exc_o = valores_validos(o_), exclusoes_validas(o_.get("exclusoes") or [])
    cortadas = 0
    for a in destinos:
        if a not in AREAS or a == origem:
            continue
        atual = areas.get(a) or {}
        novo = dict(valores_validos(atual), exclusoes=exclusoes_validas(atual.get("exclusoes") or []))
        if "valores" in partes:
            novo.update(val_o)
        if "exclusoes" in partes:
            juntas = (novo["exclusoes"] + exc_o) if modo == "acrescentar" else exc_o
            novo["exclusoes"] = exclusoes_validas(juntas)
            cortadas = max(cortadas, len(exclusoes_validas(juntas, limite=10 ** 6)) - len(novo["exclusoes"]))
        areas[a] = novo
    gravar_criterios(pasta, {"origem": "tela", "areas": areas})
    return cortadas  # revisão da 0.7.36: quantas não couberam no limite (a tela avisa)


PASTA_ANTES_0733 = "antes da 0.7.33"  # dentro de "Cópias de segurança": a planilha como era antes de perder as abas antigas


def _ler_abas_antigas(caminho_planilha):
    """Preferências e Exclusões de uma planilha da 0.7.32 ou anterior: (valores, exclusoes, tinha_abas)."""
    doc = planilha.ler_xlsx(caminho_planilha, so_abas=ABAS_ANTIGAS)
    abas = {cl.sem_acento(a["nome"]).strip().lower(): a["linhas"] for a in doc["abas"]}
    valores, exc = {}, []
    for linha in abas.get("preferencias", [])[1:]:
        if len(linha) >= 2 and str(linha[0]).strip() in CHAVES:
            chave = CHAVES[str(linha[0]).strip()]
            valores[chave] = _sim(linha[1]) if chave.startswith(("esconder", "mostrar")) else _numero(linha[1], PADRAO[chave])
    for linha in abas.get("exclusoes", [])[1:]:
        nome = str(linha[0] if linha else "").strip()
        if nome and not nome.lower().startswith("(exemplo"):
            exc.append({"nome": nome, "motivo": str(linha[1]).strip() if len(linha) > 1 else ""})
    return valores, exc, ("preferencias" in abas or "exclusoes" in abas)


def copia_antes_0733(pasta_base, frente):
    """Caminho da cópia "antes da 0.7.33" da planilha da frente, em Cópias de segurança (pode não existir)."""
    nome = os.path.splitext(os.path.basename(caminho(pasta_base, frente)))[0] if pasta_base else ""
    # desenho da Arquitetura (12/Nov, 1.4): "LexSuiteONE - <Frente> - antes da 0.7.33.xlsx", solta em Cópias de segurança
    # (a limpeza automática só mexe nas pastas datadas, então esta cópia fica)
    return os.path.join(pasta_base, "Cópias de segurança", f"{nome} - {PASTA_ANTES_0733}.xlsx") if nome else ""


def migrar(pasta, pasta_base, cfg_radar=None, aviso=None, banco=None):
    """Uma vez só por computador (0.7.33): sem criterios.json, o que a 0.7.32 aplicava a toda a lista vira os critérios
    desta pessoa em TODAS as áreas (decisão do dono, 12/Nov): os valores da planilha trabalhista (ou, sem ela, os do
    config.json) e a soma das Exclusões de todas as planilhas. Cada planilha é lida dela mesma ou, se já perdeu as abas
    (outro computador já gravou na 0.7.33), da cópia "antes da 0.7.33" (escolha (ii) da revisão). Revisão da 0.7.33: se a
    pasta das planilhas não está acessível ou alguma planilha não abre, NÃO grava (tenta de novo na próxima abertura) e
    devolve None. Devolve {área: exclusões} quando gravou."""
    if not pasta or os.path.exists(caminho_criterios(pasta)):
        return None
    if pasta_base and not os.path.isdir(pasta_base):  # Drive não montado, rede fora: tenta depois
        return None
    r = cfg_radar or {}
    valores = {k: r[k] for k in ("valor_minimo", "teto_capital_gigante") if r.get(k) not in (None, "")}
    exc, origem, lidas = [], "config" if valores else "padrão", 0
    for frente, c in planilhas_existentes(pasta_base):
        fontes = [c, copia_antes_0733(pasta_base, frente)]
        achou = False
        for f_ in fontes:
            if not f_ or not os.path.exists(f_):
                continue
            try:
                v_, e_, tinha = _ler_abas_antigas(f_)
            except Exception:  # noqa: BLE001 - planilha ilegível (em uso, sincronizando): não grava, tenta depois
                return None
            if not tinha:
                continue
            if frente == "trabalhista" or not lidas:
                valores.update(v_)
            exc += e_
            achou, origem = True, "planilha"
            break
        lidas += 1 if achou else 0
    bloco = dict(valores_validos(valores), exclusoes=exclusoes_validas(exc))
    areas = {a: dict(bloco, exclusoes=[dict(e) for e in bloco["exclusoes"]]) for a in AREAS}
    try:
        gravar_criterios(pasta, {"origem": origem, "areas": areas})
    except OSError:
        return None
    contagem = {a: len(bloco["exclusoes"]) for a in AREAS}
    texto = (f"critérios da lista migrados para este computador ({origem}): {len(bloco['exclusoes'])} empresa(s) excluída(s), "
             "iguais nas quatro áreas")
    if aviso:
        aviso("  " + texto[0].upper() + texto[1:] + ".")
    if banco is not None:
        try:
            banco.registrar("saude", {"fonte": "Critérios da lista", "situacao": "ok", "detalhe": texto[:200]})
        except Exception:  # noqa: BLE001 - o registro nunca impede a migração
            pass
    return contagem


def padrao():
    p = dict(PADRAO)
    p.update({"exclusoes": [], "controle": {"ativo": True, "validade": "", "versao_minima": "", "mensagem": "",
                                            "suporte": SUPORTE}, "origem": "padrão", "erro": "", "area": "trabalhista"})
    return p


def carregar(pasta_base, frente="trabalhista", pasta=None, banco=None, cfg_radar=None):
    """Os critérios desta pessoa para a área (criterios.json; na primeira vez, migrados da planilha) e a aba Controle da
    planilha da área. Sem arquivo e sem pasta do programa, o padrão."""
    prefs = padrao()
    prefs["area"] = frente if frente in AREAS else "trabalhista"
    pasta = pasta if pasta is not None else pasta_dados(banco)
    if pasta:
        if not os.path.exists(caminho_criterios(pasta)):
            migrar(pasta, pasta_base, cfg_radar, banco=banco)
        d = ler_criterios(pasta)
        if d is not None:
            if d.get("erro"):
                prefs["erro"] = ("Não consegui ler os critérios da lista deste computador (criterios.json); nesta leitura valem os "
                                 "padrões. / Could not read this computer's list criteria; defaults apply this time.")
            valores, exc = criterios_da_area(pasta, prefs["area"])
            prefs.update(valores)
            prefs["exclusoes"] = exc
            prefs["origem"] = "computador"
    c = caminho(pasta_base, frente) if pasta_base else ""
    if c and not os.path.exists(c) and frente != "trabalhista":
        c = caminho(pasta_base, "trabalhista")
    if c and os.path.exists(c):
        try:
            doc = planilha.ler_xlsx(c, so_abas=ABAS_EDITAVEIS)
        except Exception:  # noqa: BLE001 - planilha em uso ou corrompida: o controle fica no padrão
            doc = {"abas": []}
        for a in doc["abas"]:
            if cl.sem_acento(a["nome"]).strip().lower() != "controle":
                continue
            for linha in a["linhas"][1:]:
                chave = cl.sem_acento(str(linha[0] if linha else "")).strip().lower()
                valor = linha[1] if len(linha) > 1 else ""
                if chave == "ativo":
                    prefs["controle"]["ativo"] = _sim(valor) if str(valor).strip() else True
                elif chave in ("validade", "versao_minima", "mensagem", "suporte"):
                    prefs["controle"][chave] = str(valor if valor is not None else "").strip()
    # integracao@ é só para sistemas (não é lido por pessoas); planilhas antigas que o trazem como suporte passam a judicial@.
    if prefs["controle"].get("suporte", "").strip().lower() in ("", SISTEMAS):
        prefs["controle"]["suporte"] = SUPORTE
    return prefs


def linhas_criterios(prefs, pessoa=""):
    """0.7.33: aba só de leitura "Critérios desta leitura" (quem gravou e com que critérios), PT e EN. Não é lida pelo
    programa."""
    return [["Critério / Criterion", "Valor / Value"],
            ["Área / Area", prefs.get("area", "")], ["Gravada por / Saved by", pessoa or "este computador / this computer"],
            ["Valor mínimo da causa para destaque (R$) / Minimum claim value to highlight", prefs.get("valor_minimo") or "sem mínimo / no minimum"],
            ["Capital social que indica jurídico próprio (R$) / Share capital suggesting in-house counsel", prefs.get("teto_capital_gigante")],
            ["Empresas excluídas (quantidade) / Excluded companies (count)", len(prefs.get("exclusoes") or [])],
            ["", ""],
            ["Os critérios são de cada pessoa, no computador dela: mude em Configurações → Destaques e exclusões. Esta aba não é lida pelo programa.", ""],
            ["Criteria belong to each person, on their computer: change them in Settings → Highlights and exclusions. The program does not read this tab.", ""]]


def bloqueio(prefs, versao_atual, hoje=None):
    """Motivo para o robô não rodar, ou '' quando pode."""
    c = prefs.get("controle") or {}
    msg = (" " + c["mensagem"]) if c.get("mensagem") else ""
    if not c.get("ativo", True):
        return ("O programa está pausado pela SolverONE (aba Controle)." + msg).strip()
    if c.get("validade"):
        try:
            if (hoje or dt.date.today()) > dt.date.fromisoformat(c["validade"][:10]):
                return (f"A validade terminou em {c['validade'][:10]}." + msg).strip()
        except ValueError:
            pass
    if c.get("versao_minima") and versao_tupla(c["versao_minima"]) > versao_tupla(versao_atual):
        return (f"Precisa atualizar para a versão {c['versao_minima']} ou mais nova (instalada: {versao_atual})." + msg).strip()
    return ""


def aplicar(itens, prefs, acoes_por_empresa=None):
    """Marca item['excluida'] com o motivo (exclusão da planilha ou mínimo de ações). Não remove nada da lista."""
    por_nome = {cl.chave_nome(e["nome"]): e for e in prefs.get("exclusoes") or [] if cl.chave_nome(e["nome"])}
    cnpjs = {documento.limpar(e.get("cnpj") or e["nome"]) for e in prefs.get("exclusoes") or [] if documento.valido(e.get("cnpj") or e["nome"])}  # 0.7.33: CNPJ com letras também
    minimo = int(prefs.get("minimo_acoes") or 1)
    for it in itens:
        motivo = ""
        nomes = it.get("empresas") or []
        cnpj = documento.limpar((it.get("empresa") or {}).get("cnpj"))
        for n in nomes:
            e = por_nome.get(cl.chave_nome(n))
            if e:
                motivo = "Exclusão: " + (e["motivo"] or e["nome"])
                break
        if not motivo and cnpj and cnpj in cnpjs:
            motivo = "Exclusão: CNPJ na lista"
        if not motivo and minimo > 1 and acoes_por_empresa is not None:
            qtd = max((acoes_por_empresa.get(cl.chave_nome(n), 0) for n in nomes), default=0)
            it["acoes_na_janela"] = qtd
            if qtd < minimo:
                motivo = f"Menos de {minimo} processos em {int(prefs.get('janela_dias') or 30)} dias"
        it["excluida"] = motivo
    return itens
