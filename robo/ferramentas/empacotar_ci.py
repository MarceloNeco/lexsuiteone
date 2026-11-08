"""Empacota uma versão para publicação. Usado pela automação do GitHub (publicar.yml); também roda à mão.

  python ferramentas/empacotar_ci.py preparar --versao 0.7.5 --saida publicar/0.7.5
      Gera LexSuiteONE-RADAR-atualizacao-0.7.6.zip (pacote de atualização, sem pasta de topo, só os arquivos permitidos) e
      LexSuiteONE-RADAR.zip (download completo, com a pasta LexSuiteONE/ e chave_publica.txt). Imprime o SHA-256 do
      pacote de atualização, que é o que o serviço de assinatura assina junto com a versão.
  python ferramentas/empacotar_ci.py manifesto --versao 0.7.5 --sha256 ... --assinatura ... --saida publicar/0.7.5
      Escreve versao.json no formato que o robô instalado lê (igual ao do publicar.py).

A chave privada não existe neste repositório nem em computador nenhum: a assinatura é pedida ao serviço
https://assinatura.solverone.com.br, que só aceita pedidos da automação deste repositório para uma tag v<versão>.
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

from lexsuite import VERSAO  # noqa: E402
from lexsuite.atualizar import ARQUIVO_CHAVE, RAIZ_PERMITIDA  # noqa: E402


def arquivos(pasta_robo):
    lista = [n for n in sorted(RAIZ_PERMITIDA) if os.path.exists(os.path.join(pasta_robo, n))]
    lista += ["lexsuite/" + n for n in sorted(os.listdir(os.path.join(pasta_robo, "lexsuite"))) if n.endswith(".py")]
    return lista


def preparar(versao, saida, pasta_robo):
    if versao != VERSAO:
        raise SystemExit(f"a versão pedida ({versao}) não bate com lexsuite/__init__.py ({VERSAO})")
    if not os.path.exists(os.path.join(pasta_robo, ARQUIVO_CHAVE)):
        raise SystemExit(f"falta {ARQUIVO_CHAVE} na pasta do robô")
    os.makedirs(saida, exist_ok=True)
    lista = arquivos(pasta_robo)
    atualizacao = os.path.join(saida, f"LexSuiteONE-RADAR-atualizacao-{versao}.zip")
    with zipfile.ZipFile(atualizacao, "w", zipfile.ZIP_DEFLATED) as z:
        for a in lista:
            z.write(os.path.join(pasta_robo, *a.split("/")), a)
    download = os.path.join(saida, "LexSuiteONE-RADAR.zip")
    with zipfile.ZipFile(download, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(zipfile.ZipInfo("LexSuiteONE/"), b"")
        z.writestr(zipfile.ZipInfo("LexSuiteONE/lexsuite/"), b"")
        for a in lista + [ARQUIVO_CHAVE]:
            z.write(os.path.join(pasta_robo, *a.split("/")), "LexSuiteONE/" + a)
    with open(atualizacao, "rb") as f:
        sha = hashlib.sha256(f.read()).hexdigest()
    print(sha)
    return sha


def manifesto(versao, sha256, assinatura, saida, notas):
    m = {"versao": versao, "arquivo": f"LexSuiteONE-RADAR-atualizacao-{versao}.zip", "sha256": sha256.lower(),
         "assinatura": assinatura.lower(), "notas": notas or ""}
    caminho = os.path.join(saida, "versao.json")
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=1)
    print(caminho)


def main():
    p = argparse.ArgumentParser(description="Empacotamento para publicação assinada do LexSuiteONE")
    sub = p.add_subparsers(dest="comando", required=True)
    s = sub.add_parser("preparar"); s.add_argument("--versao", required=True); s.add_argument("--saida", required=True); s.add_argument("--robo", default=ROBO)
    s = sub.add_parser("manifesto"); s.add_argument("--versao", required=True); s.add_argument("--sha256", required=True)
    s.add_argument("--assinatura", required=True); s.add_argument("--saida", required=True); s.add_argument("--notas", default="")
    a = p.parse_args()
    if a.comando == "preparar":
        preparar(a.versao, a.saida, a.robo)
    else:
        manifesto(a.versao, a.sha256, a.assinatura, a.saida, a.notas)


if __name__ == "__main__":
    main()
