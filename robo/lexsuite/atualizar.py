"""Atualização assinada do robô.

Onde procurar: a subpasta "atualizacao" da pasta compartilhada (o suporte solta o pacote lá e o Drive leva) e,
se configurado, um endereço fixo na internet. O pacote só é instalado se (1) a assinatura Ed25519 do manifesto
bater com a chave pública que está em chave_publica.txt ao lado do robô, (2) o SHA-256 do zip bater com o
manifesto e (3) o zip só trouxer arquivos permitidos. config.json, lexsuite.db, python/ e saida/ nunca são tocados.
A chave privada fica só com o suporte; sem chave_publica.txt a atualização fica desligada.
"""

import datetime as dt
import hashlib
import io
import json
import os
import posixpath
import shutil
import zipfile

from . import assinatura, compartilhar, rede
from .preferencias import versao_tupla

ARQUIVO_CHAVE = "chave_publica.txt"
MANIFESTO = "versao.json"
RAIZ_PERMITIDA = {"lexsuite_robo.py", "radar_modelo.html", "config.exemplo.json", "LEIA-ME.md", "ROTEIRO-INSTALACAO.md", "SEGURANCA.md", "MANUAL-DO-ESCRITORIO.html",
                  "ABRIR.bat", "RODAR.bat", "DIAGNOSTICO.bat", "INSTALAR-PYTHON.bat", "AGENDAR.bat", "PREPARAR-PARA-CLIENTE.bat"}
LIMITE_BYTES = 50 * 1024 * 1024
LIMITE_ARQUIVOS = 500


def chave_publica(pasta_robo):
    caminho = os.path.join(pasta_robo, ARQUIVO_CHAVE)
    if not os.path.exists(caminho):
        return ""
    with open(caminho, encoding="utf-8") as f:
        chave = "".join(f.read().split()).lower()
    return chave if len(chave) == 64 and all(c in "0123456789abcdef" for c in chave) else ""


def mensagem_assinada(versao, sha256):
    return f"{versao}\n{sha256}\n".encode("utf-8")


def _manifesto_valido(m):
    return (isinstance(m, dict) and all(isinstance(m.get(k), str) and m.get(k) for k in ("versao", "arquivo", "sha256", "assinatura"))
            and len(m["sha256"]) == 64 and "/" not in m["arquivo"] and "\\" not in m["arquivo"])


def procurar(pasta_robo, cfg, versao_atual, aviso=print):
    """Olha a pasta compartilhada e o endereço fixo. Devolve a versão mais nova que a instalada, ou None."""
    achados = []
    pasta = compartilhar.pasta_atualizacao(cfg)
    if pasta and os.path.isfile(os.path.join(pasta, MANIFESTO)):
        try:
            with open(os.path.join(pasta, MANIFESTO), encoding="utf-8") as f:
                m = json.load(f)
            if _manifesto_valido(m) and os.path.isfile(os.path.join(pasta, m["arquivo"])):
                achados.append({"origem": "pasta compartilhada", "manifesto": m, "zip_caminho": os.path.join(pasta, m["arquivo"])})
        except (OSError, ValueError) as e:
            aviso(f"  Atualização: manifesto da pasta compartilhada ilegível ({e.__class__.__name__}).")
    url = (cfg.get("atualizacao") or {}).get("url") or ""
    if url.startswith("https://"):
        try:
            m = json.loads(rede.pedir_bytes(url.rstrip("/") + "/" + MANIFESTO, tempo_limite=30).decode("utf-8"))
            if _manifesto_valido(m):
                achados.append({"origem": "internet", "manifesto": m, "zip_url": url.rstrip("/") + "/" + m["arquivo"]})
        except Exception as e:  # sem internet ou endereço fora do ar: não é erro do robô
            aviso(f"  Atualização: endereço na internet não respondeu ({e.__class__.__name__}).")
    novos = [a for a in achados if versao_tupla(a["manifesto"]["versao"]) > versao_tupla(versao_atual)]
    if not novos:
        return None
    return max(novos, key=lambda a: versao_tupla(a["manifesto"]["versao"]))


def _ler_zip(info):
    if info.get("zip_caminho"):
        if os.path.getsize(info["zip_caminho"]) > LIMITE_BYTES:
            raise ValueError("pacote grande demais")
        with open(info["zip_caminho"], "rb") as f:
            return f.read()
    return rede.pedir_bytes(info["zip_url"], tempo_limite=300)


def verificar(info, chave_hex):
    """(ok, motivo). Assinatura do manifesto e SHA-256 do zip."""
    m = info["manifesto"]
    if not chave_hex:
        return False, "sem chave_publica.txt: a atualização está desligada neste computador"
    if not assinatura.verificar(mensagem_assinada(m["versao"], m["sha256"].lower()), m["assinatura"], chave_hex):
        return False, "assinatura do pacote não confere com a chave do suporte"
    try:
        dados = _ler_zip(info)
    except Exception as e:
        return False, f"não consegui ler o pacote ({e.__class__.__name__})"
    if len(dados) > LIMITE_BYTES:
        return False, "pacote grande demais"
    if hashlib.sha256(dados).hexdigest() != m["sha256"].lower():
        return False, "o conteúdo do pacote não bate com o manifesto"
    info["zip_bytes"] = dados
    return True, ""


def _nome_seguro(n):
    """Caminho relativo e limpo: sem '..', sem raiz, sem letra de unidade."""
    return bool(n) and not (n.endswith("/") or n.startswith("/") or ".." in n.split("/") or ":" in n or posixpath.normpath(n) != n)


def _nome_permitido(nome):
    """Só caminhos seguros na raiz permitida ou dentro de lexsuite/ (apenas .py)."""
    n = nome.replace("\\", "/")
    if not _nome_seguro(n):
        return False
    partes = n.split("/")
    if len(partes) == 1:
        return partes[0] in RAIZ_PERMITIDA
    return len(partes) == 2 and partes[0] == "lexsuite" and partes[1].endswith(".py") and partes[1] != "__init__.pyc"


def instalar(pasta_robo, info, versao_atual, aviso=print):
    """Copia os arquivos do pacote verificado por cima do robô, guardando a versão anterior em _anterior/<versão>/."""
    m = info["manifesto"]
    try:
        z = zipfile.ZipFile(io.BytesIO(info["zip_bytes"]))
    except zipfile.BadZipFile:
        return {"ok": False, "motivo": "pacote corrompido"}
    membros = [i for i in z.infolist() if not i.is_dir()]
    if len(membros) > LIMITE_ARQUIVOS or sum(i.file_size for i in membros) > LIMITE_BYTES:
        return {"ok": False, "motivo": "pacote com arquivos demais ou grande demais"}
    # Aceita um zip com ou sem a pasta raiz (ex.: "LEXSUITE-ONE-ROBO v0.7.1/lexsuite_robo.py")
    raiz = ""
    nomes = [i.filename.replace("\\", "/") for i in membros]
    if not any(n == "lexsuite_robo.py" for n in nomes):
        primeiras = {n.split("/")[0] for n in nomes if "/" in n}
        if len(primeiras) == 1 and any(n == next(iter(primeiras)) + "/lexsuite_robo.py" for n in nomes):
            raiz = next(iter(primeiras)) + "/"
    arquivos = []
    for i in membros:
        n = i.filename.replace("\\", "/")
        if raiz and n.startswith(raiz):
            n = n[len(raiz):]
        if not _nome_seguro(n):
            return {"ok": False, "motivo": f"caminho suspeito no pacote: {n}"}
        if not _nome_permitido(n):
            if n.startswith("lexsuite/") or n in RAIZ_PERMITIDA:
                return {"ok": False, "motivo": f"arquivo não permitido no pacote: {n}"}
            continue  # extras (docs, testes) são ignorados
        arquivos.append((n, i))
    if not any(n == "lexsuite_robo.py" for n, _ in arquivos):
        return {"ok": False, "motivo": "o pacote não contém o robô (lexsuite_robo.py)"}
    anterior = os.path.join(pasta_robo, "_anterior", f"v{versao_atual}")
    os.makedirs(anterior, exist_ok=True)
    for n, i in arquivos:
        destino = os.path.join(pasta_robo, *n.split("/"))
        if os.path.exists(destino):
            copia = os.path.join(anterior, *n.split("/"))
            os.makedirs(os.path.dirname(copia), exist_ok=True)
            shutil.copyfile(destino, copia)
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        temporario = destino + ".novo"
        with open(temporario, "wb") as f:
            f.write(z.read(i))
        os.replace(temporario, destino)
    with open(os.path.join(pasta_robo, "ultima_atualizacao.json"), "w", encoding="utf-8") as f:
        json.dump({"de": versao_atual, "para": m["versao"], "quando": dt.datetime.now().isoformat(timespec="seconds"),
                   "origem": info.get("origem", ""), "arquivos": [n for n, _ in arquivos], "notas": m.get("notas", "")}, f, ensure_ascii=False, indent=1)
    aviso(f"  Atualizado da versão {versao_atual} para a {m['versao']} ({len(arquivos)} arquivos). Feche e abra o robô de novo.")
    return {"ok": True, "versao": m["versao"], "arquivos": len(arquivos), "notas": m.get("notas", "")}


def atualizar(pasta_robo, cfg, versao_atual, aviso=print, instalar_agora=True):
    """Procura, verifica e (se pedido) instala. Devolve um dicionário que a tela mostra."""
    chave = chave_publica(pasta_robo)
    if not chave:
        return {"ok": True, "disponivel": False, "motivo": "sem chave_publica.txt: atualização desligada neste computador"}
    info = procurar(pasta_robo, cfg, versao_atual, aviso)
    if not info:
        return {"ok": True, "disponivel": False, "motivo": f"nenhuma versão mais nova que a {versao_atual}"}
    ok, motivo = verificar(info, chave)
    if not ok:
        aviso(f"  Atualização {info['manifesto']['versao']} recusada: {motivo}.")
        return {"ok": False, "disponivel": True, "versao": info["manifesto"]["versao"], "motivo": motivo}
    if not instalar_agora:
        return {"ok": True, "disponivel": True, "versao": info["manifesto"]["versao"], "origem": info["origem"], "notas": info["manifesto"].get("notas", "")}
    resultado = instalar(pasta_robo, info, versao_atual, aviso)
    resultado.update({"disponivel": True, "origem": info["origem"]})
    return resultado
