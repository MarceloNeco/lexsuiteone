"""Preenche o e-mail de boas-vindas do LexSuiteONE.

O nome do produto vem da configuração `docs/marca.json` (ver `ferramentas/marca.py`): nada de nome fixo no modelo.

Uso (na pasta docs/email):
    python preencher.py --nome Leandro --contato judicial@solverone.com.br --drive integracao@solverone.com.br
    python preencher.py --nome Leandro --codigo LEX-7K4M-2PQ9 ...   (inclui o bloco do código)

Gera `saida/boas-vindas-<nome>.html` e `.txt`, prontos para enviar, e mostra o assunto. Sem código, o bloco do código é removido.
Só biblioteca padrão; nenhum envio acontece aqui.
"""
import argparse
import html
import importlib.util
import pathlib
import re

AQUI = pathlib.Path(__file__).resolve().parent
ASSUNTO = "Bem-vindo ao {nome}: seu pacote de instalação"


def campos_da_marca():
    """Os campos {{marca.*}} a partir de docs/marca.json, pela mesma ferramenta que gera o site."""
    caminho = AQUI.parent.parent / "ferramentas" / "marca.py"
    spec = importlib.util.spec_from_file_location("marca", caminho)
    marca = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(marca)
    m = marca.carregar()
    return m, {"marca.nome": html.escape(m["nome"]), "marca.curto": html.escape(m["curto"]),
               "marca.logo_email": marca.logo(m, estilo_destaque="color:#d4ab6a;font-weight:800;", estilo_forte="font-weight:800;")}


def preencher(texto, campos, codigo):
    if codigo:
        texto = re.sub(r"<!--CODIGO-INICIO-->|<!--CODIGO-FIM-->|\[CODIGO-INICIO\]\n|\[CODIGO-FIM\]\n", "", texto)
        texto = texto.replace("{{codigo}}", codigo)
    else:
        texto = re.sub(r"<!--CODIGO-INICIO-->.*?<!--CODIGO-FIM-->\n?", "", texto, flags=re.S)
        texto = re.sub(r"\[CODIGO-INICIO\]\n.*?\[CODIGO-FIM\]\n", "", texto, flags=re.S)
    for chave, valor in campos.items():
        texto = texto.replace("{{%s}}" % chave, valor)
    sobrou = re.findall(r"{{[\w.]+}}", texto)
    if sobrou:
        raise SystemExit("Campos sem valor: %s" % ", ".join(sorted(set(sobrou))))
    return texto


def main():
    p = argparse.ArgumentParser(description="Preenche o e-mail de boas-vindas.")
    p.add_argument("--nome", required=True, help="primeiro nome de quem recebe")
    p.add_argument("--contato", default="judicial@solverone.com.br", help="e-mail para dúvidas (contato da suíte LexSuiteONE)")
    p.add_argument("--drive", default="integracao@solverone.com.br", help="conta Google com quem compartilhar a pasta")
    p.add_argument("--codigo", default="", help="código de cliente (LEX-XXXX-XXXX); sem ele o bloco sai")
    a = p.parse_args()
    m, campos = campos_da_marca()
    campos.update({"nome": a.nome.strip(), "contato": a.contato.strip(), "drive": a.drive.strip()})
    saida = AQUI / "saida"
    saida.mkdir(exist_ok=True)
    seguro = re.sub(r"[^A-Za-z0-9_-]+", "-", a.nome.strip()).strip("-") or "cliente"
    for ext in ("html", "txt"):
        modelo = (AQUI / ("email-boas-vindas.%s" % ext)).read_text(encoding="utf-8")
        destino = saida / ("boas-vindas-%s.%s" % (seguro, ext))
        destino.write_text(preencher(modelo, campos, a.codigo.strip().upper()), encoding="utf-8")
        print("gerado:", destino)
    print("assunto:", ASSUNTO.format(nome=m["nome"]))


if __name__ == "__main__":
    main()
