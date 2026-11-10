"""config.json: leitura com padrão, criação automática na primeira vez e gravação."""

import json
import os
import shutil

PADRAO = {
    "escritorio": "", "alvos": [], "carteira": "carteira.csv",
    # Quem usa a tela neste computador (saudação, manual personalizado e o cadastro na licença do escritório, na SolverONE).
    "usuario": {"nome": "", "papel": ""},
    "radar": {"tribunais": [f"TRT{n}" for n in range(1, 25)], "dias_para_tras": 1, "dias_na_pagina": 1,
              "valor_minimo": 100000, "teto_capital_gigante": 50000000, "receita": True, "porta": 8765, "guardar_dias": 365,
              # Leitura automática (Agendador do Windows): horários "HH:MM" e dias ("todos" ou "uteis").
              "horarios": ["20:00", "08:00"], "dias": "todos", "avisar_ao_terminar": True},
    # Pasta compartilhada (Google Drive para computador, OneDrive...): o robô grava ali a planilha e lê o controle.
    "compartilhar": {"pasta": "", "subpasta": "LexSuiteONE", "planilha": True},
    # Atualização assinada: pela subpasta "atualizacao" da pasta compartilhada e, se houver, por um endereço fixo.
    "atualizacao": {"url": "https://judicial.solverone.com.br/atualizacao", "verificar_ao_abrir": True},
    "monitor": {"oabs": [], "processos": "processos.csv", "partes_da_carteira": True, "tribunais": ["TRT2", "TRT15"],
                "dias_para_tras": 3, "radar": True, "dias_na_pagina": 7},
    "email": {"ativo": False},
}


MESES = ("JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ")


def data_curta(d, ano=True):
    """0.7.28 (dono): data com o mês em letras, para não confundir dia e mês: 10/NOV/2026 (ou 10/NOV). Aceita date,
    datetime ou texto ISO; o que não for data volta como veio."""
    import datetime as _dt
    if isinstance(d, str):
        try:
            d = _dt.date.fromisoformat(d[:10])
        except ValueError:
            return d
    try:
        return f"{d.day:02d}/{MESES[d.month - 1]}" + (f"/{d.year}" if ano else "")
    except (AttributeError, IndexError):
        return str(d)


def inteiro(valor, padrao, minimo, maximo):
    """0.7.23 (revisão): número do config.json com limite; texto, lista, Infinity ou 1e400 viram o padrão."""
    try:
        return max(minimo, min(maximo, int(valor)))
    except (TypeError, ValueError, OverflowError):
        return padrao


def carregar(caminho, aviso=print):
    """Lê o config.json. Se não existir, cria a partir do config.exemplo.json (ou do padrão) e segue."""
    if not os.path.exists(caminho):
        exemplo = os.path.join(os.path.dirname(caminho), "config.exemplo.json")
        if os.path.exists(exemplo):
            shutil.copyfile(exemplo, caminho)
            aviso(f"  Criei o {os.path.basename(caminho)} a partir do config.exemplo.json. Edite depois, se quiser.")
        else:
            salvar(caminho, json.loads(json.dumps(PADRAO)))
            aviso(f"  Criei o {os.path.basename(caminho)} com o padrão (os 24 TRTs). Edite depois, se quiser.")
    with open(caminho, encoding="utf-8") as f:
        cfg = json.load(f)
    for chave, valor in PADRAO.items():
        cfg.setdefault(chave, valor)
    for bloco in ("radar", "compartilhar", "atualizacao", "usuario"):
        if not isinstance(cfg.get(bloco), dict):
            cfg[bloco] = {}
        for chave, valor in PADRAO[bloco].items():
            cfg[bloco].setdefault(chave, valor)
    # O instalador deixa o código de cliente já conferido e a identificação desta instalação (conta-inicial.json).
    inicial = os.path.join(os.path.dirname(caminho), "conta-inicial.json")
    if os.path.exists(inicial):
        try:
            with open(inicial, encoding="utf-8-sig") as f:
                ini = json.load(f)
        except (OSError, ValueError):
            ini = {}
        if not isinstance(cfg.get("conta"), dict):
            cfg["conta"] = {}
        for chave in ("codigo", "instalacao"):
            valor = str((ini or {}).get(chave) or "").strip()
            if valor and not cfg["conta"].get(chave):
                cfg["conta"][chave] = valor
    return cfg


def salvar(caminho, cfg):
    """Grava bonito, em UTF-8, sem perder chaves que a tela não conhece."""
    temporario = caminho + ".tmp"
    with open(temporario, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(temporario, caminho)
