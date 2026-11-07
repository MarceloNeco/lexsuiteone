"""Ferramenta do suporte (não vai para o cliente): gera o par de chaves e empacota uma versão assinada.

  python ferramentas/publicar.py gerar-chaves
      Cria chave_privada.txt (GUARDE fora do Drive e do repositório) e chave_publica.txt (vai na pasta do robô).
  python ferramentas/publicar.py empacotar --versao 0.7.1 --chave C:\\caminho\\chave_privada.txt [--robo pasta] [--notas "texto"]
      Gera publicar/<versao>/LEXSUITE-ONE-ROBO-<versao>.zip e versao.json. Copie os dois para docs/atualizacao/ do
      repositório (vira https://judicial.solverone.com.br/atualizacao/) e/ou para a subpasta "atualizacao" do Drive do cliente.
"""

import argparse
import hashlib
import json
import os
import sys
import zipfile

AQUI = os.path.dirname(os.path.abspath(__file__))
ROBO = os.path.dirname(AQUI)
sys.path.insert(0, ROBO)

from lexsuite import assinatura  # noqa: E402
from lexsuite.atualizar import RAIZ_PERMITIDA, mensagem_assinada  # noqa: E402


def gerar_chaves(pasta):
    privada, publica = assinatura.gerar_chaves()
    caminho_priv = os.path.join(pasta, "chave_privada.txt")
    if os.path.exists(caminho_priv):
        raise SystemExit(f"Já existe {caminho_priv}. Apague de propósito se quiser outra.")
    with open(caminho_priv, "w", encoding="utf-8") as f:
        f.write(privada + "\n")
    with open(os.path.join(pasta, "chave_publica.txt"), "w", encoding="utf-8") as f:
        f.write(publica + "\n")
    print(f"Chave privada: {caminho_priv}  (guarde fora do Drive; quem tem esta chave assina atualizações)")
    print(f"Chave pública: {os.path.join(pasta, 'chave_publica.txt')}  (copie para a pasta do robô no cliente)")
    print(f"Impressão da chave pública (para conferir por telefone): {assinatura.impressao(publica)}")


def empacotar(versao, caminho_chave, pasta_robo, notas):
    with open(caminho_chave, encoding="utf-8") as f:
        privada = "".join(f.read().split())
    saida = os.path.join(ROBO, "publicar", versao)
    os.makedirs(saida, exist_ok=True)
    nome_zip = f"LEXSUITE-ONE-ROBO-{versao}.zip"
    caminho_zip = os.path.join(saida, nome_zip)
    arquivos = []
    for nome in sorted(RAIZ_PERMITIDA):
        if os.path.exists(os.path.join(pasta_robo, nome)):
            arquivos.append(nome)
    for nome in sorted(os.listdir(os.path.join(pasta_robo, "lexsuite"))):
        if nome.endswith(".py"):
            arquivos.append("lexsuite/" + nome)
    with zipfile.ZipFile(caminho_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for a in arquivos:
            z.write(os.path.join(pasta_robo, *a.split("/")), a)
    with open(caminho_zip, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    manifesto = {"versao": versao, "arquivo": nome_zip, "sha256": sha,
                 "assinatura": assinatura.assinar(mensagem_assinada(versao, sha), privada), "notas": notas or ""}
    with open(os.path.join(saida, "versao.json"), "w", encoding="utf-8") as f:
        json.dump(manifesto, f, ensure_ascii=False, indent=1)
    print(f"Pacote: {caminho_zip} ({len(arquivos)} arquivos)")
    print(f"Manifesto: {os.path.join(saida, 'versao.json')}")
    print("Copie os dois para a subpasta 'atualizacao' da pasta compartilhada do cliente.")


def main():
    p = argparse.ArgumentParser(description="Publicação assinada do LexSuiteONE")
    sub = p.add_subparsers(dest="comando", required=True)
    s = sub.add_parser("gerar-chaves"); s.add_argument("--pasta", default=os.getcwd())
    s = sub.add_parser("empacotar")
    s.add_argument("--versao", required=True); s.add_argument("--chave", required=True)
    s.add_argument("--robo", default=ROBO); s.add_argument("--notas", default="")
    a = p.parse_args()
    if a.comando == "gerar-chaves":
        gerar_chaves(a.pasta)
    else:
        empacotar(a.versao, a.chave, a.robo, a.notas)


if __name__ == "__main__":
    main()
