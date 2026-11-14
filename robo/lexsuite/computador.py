"""Este computador: antivírus e firewall encontrados (0.7.47, desenho "CNJ fora e antivírus", 2.4).

Detectar, explicar e orientar; nunca contornar o antivírus (regra do dono, 14/Nov). O Windows guarda o que está instalado
na Central de Segurança (`root/SecurityCenter2`), que qualquer usuário lê pelo PowerShell, sem administrador. No Windows
Server essa central não existe: "não identificado". Lido uma vez por dia (guardado em `saida/computador.json`).
Só o nome do produto sai daqui; nada da pessoa.
"""

import datetime as dt
import json
import os
import re
import subprocess  # nosec B404 - só o powershell, sem shell, com comando fixo

PAGINA = "https://judicial.solverone.com.br/antivirus.html"
# nome do produto (como o Windows mostra) → âncora da seção na página de antivírus (paginas/antivirus.html)
ANCORAS = (("bitdefender", "bitdefender"), ("defender", "defender"), ("windows security", "defender"),
           ("kaspersky", "kaspersky"), ("eset", "eset"), ("avast", "avast"), ("avg", "avg"), ("norton", "norton"),
           ("mcafee", "mcafee"), ("trend micro", "trend"), ("sophos", "sophos"), ("panda", "panda"),
           ("malwarebytes", "malwarebytes"), ("avira", "avira"))
SINAIS = ("zip_temp", "bloqueio_gravacao", "processo_morto", "tarefa_falhou", "rede_recusada", "smartscreen")

_PS = ("$ErrorActionPreference = 'Stop'; $r = @{}; foreach ($c in 'AntiVirusProduct', 'FirewallProduct') { "
       "try { $r[$c] = @(Get-CimInstance -Namespace root/SecurityCenter2 -ClassName $c | "
       "Select-Object displayName, productState) } catch { $r[$c] = $null } }; $r | ConvertTo-Json -Compress -Depth 3")


def ligado(estado):
    """O `productState` do Windows: o 2º byte 0x10 ou 0x11 = proteção ligada (0x41000 ligado; 0x40000 desligado).
    Leitura de comunidade, não documentada pela Microsoft; None quando não dá para dizer."""
    try:
        return ((int(estado) >> 8) & 0xFF) in (0x10, 0x11)
    except (TypeError, ValueError):
        return None


def _produtos(lista):
    if lista is None:
        return None
    if isinstance(lista, dict):
        lista = [lista]
    saida = []
    for p in lista if isinstance(lista, list) else []:
        if isinstance(p, dict) and p.get("displayName"):
            saida.append({"nome": str(p["displayName"])[:80], "ligado": ligado(p.get("productState"))})
    return saida


def ler_do_windows(rodar=None):
    """{"antivirus": [...], "firewall": [...], "identificado": bool}. Fora do Windows ou sem a Central de Segurança:
    listas vazias e identificado=False. Nunca levanta exceção."""
    vazio = {"antivirus": [], "firewall": [], "identificado": False}
    if os.name != "nt" and rodar is None:
        return vazio
    try:
        if rodar:
            bruto = rodar(_PS)
        else:
            r = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", _PS], capture_output=True,  # nosec B603 B607
                               text=True, timeout=25, stdin=subprocess.DEVNULL, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            bruto = r.stdout
        d = json.loads(bruto or "{}")
    except Exception:  # noqa: BLE001 - PowerShell bloqueado ou lento: "não identificado"
        return vazio
    av, fw = _produtos(d.get("AntiVirusProduct")), _produtos(d.get("FirewallProduct"))
    return {"antivirus": av or [], "firewall": fw or [], "identificado": av is not None}


def ler(pasta, hoje=None, rodar=None, forcar=False):
    """O que foi lido hoje (guardado em saida/computador.json); lê de novo uma vez por dia."""
    hoje = (hoje or dt.date.today()).isoformat()
    arq = os.path.join(pasta, "saida", "computador.json")
    try:
        with open(arq, encoding="utf-8") as f:
            guardado = json.load(f)
        if not forcar and guardado.get("lido_em") == hoje:
            return guardado
    except (OSError, ValueError, AttributeError):
        pass
    info = dict(ler_do_windows(rodar), lido_em=hoje)
    try:
        os.makedirs(os.path.dirname(arq), exist_ok=True)
        with open(arq, "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False)
    except OSError:
        pass
    return info


def guardado(pasta):
    """O que já foi lido (sem rodar o PowerShell): a tela usa este, para nunca esperar."""
    try:
        with open(os.path.join(pasta, "saida", "computador.json"), encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def vigiar(pasta, dormir=None, vezes=None):
    """Thread da tela aberta: lê ao abrir e confere de 6 em 6 horas (só lê de novo quando muda o dia)."""
    import time as _t
    dormir = dormir or _t.sleep
    n = 0
    while vezes is None or n < vezes:
        n += 1
        try:
            ler(pasta)
        except Exception:  # noqa: BLE001 - nunca derruba o programa
            pass
        dormir(6 * 3600)


def e_defender(nome):
    """O Microsoft Defender (o Windows o chama de "Windows Defender"); o Bitdefender NÃO é (o nome contém "defender")."""
    n = str(nome or "").lower()
    return "bitdefender" not in n and ("defender" in n or n.startswith("windows"))


def principal(info):
    """O antivírus que manda: o primeiro ligado que não é o Defender; senão o Defender; senão o primeiro; senão ""."""
    av = (info or {}).get("antivirus") or []
    outros = [p for p in av if not e_defender(p["nome"])]
    for grupo in ([p for p in outros if p.get("ligado")], [p for p in av if p.get("ligado")], outros, av):
        if grupo:
            return grupo[0]["nome"]
    return ""


def ligado_principal(info):
    nome = principal(info)
    for p in (info or {}).get("antivirus") or []:
        if p["nome"] == nome:
            return p.get("ligado")
    return None


def so_defender(info):
    """Só o Microsoft Defender (ou nada de outro fabricante): a orientação é só "se aparecer aviso, clique em Executar"."""
    nome = principal(info)
    return not nome or e_defender(nome)


def ancora(nome):
    n = str(nome or "").lower()
    for chave, a in ANCORAS:
        if chave in n:
            return a
    return ""


def link(nome, lang="pt"):
    """O link da página de antivírus, na seção daquele antivírus (ou na lista, se ele não tiver seção)."""
    a = ancora(nome)
    return f"{PAGINA}#{'pt' if lang == 'pt' else 'en'}-{a}" if a else f"{PAGINA}#{'pt-lista' if lang == 'pt' else 'en-list'}"


def nome_limpo(nome):
    """Só letras, números, espaço e pontuação simples (vai no registro técnico)."""
    return re.sub(r"[^\w .,()+&-]", "", str(nome or ""))[:80]


def para_tela(info, lang="pt"):
    """O que "Sobre este computador" mostra."""
    info = info or {}
    nome = principal(info)
    return {"identificado": bool(info.get("identificado")), "lido_em": info.get("lido_em", ""),
            "antivirus": info.get("antivirus") or [], "firewall": info.get("firewall") or [],
            "principal": nome, "link": link(nome, lang), "link_en": link(nome, "en")}
