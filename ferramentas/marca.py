"""Nome do produto num lugar só, e tudo o que se gera a partir dele.

A configuração é `docs/marca.json` (publicada no site):

    {"nome": "RADAR JUDICIAL", "curto": "RADAR", "destaque": "IA"}

- nome: exatamente como deve aparecer, com maiúsculas e minúsculas (ex.: "RADAR JUDICIAL", "Lex One").
- curto: como o texto corrido chama o programa ("o RADAR"). Sem ele, vale a primeira palavra do nome.
- destaque: trecho da última palavra que fica em latão (ex.: "IA"). Vazio = nenhum.

O que este programa gera (nunca edite os gerados à mão; a automação do GitHub confere):
- `docs/*.html` a partir de `paginas/*.html` (marcações {{marca.nome}}, {{marca.curto}}, {{marca.logo}}, {{versao}});
- `robo/MANUAL-DO-ESCRITORIO.html` (o manual de dentro do programa) a partir de `paginas/manual.html`;
- `robo/marca.json`, a cópia que vai no pacote (a tela do programa lê o nome dali);
- `docs/atualizacao/instalar.txt`, que o instalador lê: versão, arquivo e SHA-256 publicados em
  `docs/atualizacao/versao.json`, mais o nome do produto (para o atalho);
- `docs/downloads/Instalar-LexSuiteONE.zip`, com um arquivo só: `instalador/INSTALAR.bat`.
O e-mail de boas-vindas lê a mesma configuração ao ser preenchido (`docs/email/preencher.py`).

Uso, na raiz do repositório:
    python ferramentas/marca.py              gera tudo
    python ferramentas/marca.py --conferir   só confere se está tudo em dia (usado pela automação do GitHub)

Só biblioteca padrão.
"""
import html
import io
import json
import pathlib
import re
import sys
import zipfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CONFIG = RAIZ / "docs" / "marca.json"
PAGINAS = RAIZ / "paginas"
DESTINO = RAIZ / "docs"
MANUAL_ROBO = RAIZ / "robo" / "MANUAL-DO-ESCRITORIO.html"
MARCA_ROBO = RAIZ / "robo" / "marca.json"
VERSAO_PY = RAIZ / "robo" / "lexsuite" / "__init__.py"
MANIFESTO = RAIZ / "docs" / "atualizacao" / "versao.json"
INSTALAR_TXT = RAIZ / "docs" / "atualizacao" / "instalar.txt"
INSTALADOR = RAIZ / "instalador" / "INSTALAR.bat"
INSTALADOR_ZIP = RAIZ / "docs" / "downloads" / "Instalar-LexSuiteONE.zip"
AVISO = "<!-- Gerado por ferramentas/marca.py a partir de paginas/{arquivo} e docs/marca.json. Não edite aqui. -->\n"
# Fora: o que quebra HTML, JavaScript, o Prompt de Comando do Windows (instalador) ou nome de arquivo (atalho).
PROIBIDOS = set('<>&"\'\\{}`()%!^|=/:*?')


def carregar(caminho=CONFIG):
    """Lê e confere a configuração. Devolve {'nome', 'curto', 'destaque'}."""
    dados = json.loads(pathlib.Path(caminho).read_text(encoding="utf-8"))
    nome = " ".join(str(dados.get("nome", "")).split())
    curto = " ".join(str(dados.get("curto", "")).split()) or nome.split(" ")[0]
    destaque = str(dados.get("destaque", "")).strip()
    if not 2 <= len(nome) <= 40:
        raise ValueError("marca.json: o nome precisa ter de 2 a 40 caracteres.")
    for campo, valor in (("nome", nome), ("curto", curto), ("destaque", destaque)):
        if PROIBIDOS & set(valor):
            raise ValueError("marca.json: o campo %s não pode ter estes caracteres: %s" % (campo, " ".join(sorted(PROIBIDOS))))
    if destaque and destaque not in nome.split(" ")[-1]:
        raise ValueError("marca.json: o destaque precisa estar dentro da última palavra do nome.")
    return {"nome": nome, "curto": curto, "destaque": destaque}


def versao():
    m = re.search(r'VERSAO\s*=\s*"([^"]+)"', VERSAO_PY.read_text(encoding="utf-8"))
    return m.group(1) if m else ""


def logo(m, estilo_destaque=None, estilo_forte=None):
    """O nome desenhado: palavras leves, a última forte e o destaque em latão.
    Sem estilos, usa classes (site); com estilos, usa style= (e-mail)."""
    partes = m["nome"].split(" ")
    leve, forte = " ".join(partes[:-1]), partes[-1]
    if m["destaque"]:
        a, _, b = forte.partition(m["destaque"])
        marca_b = '<b style="%s">' % estilo_destaque if estilo_destaque else "<b>"
        forte = html.escape(a) + marca_b + html.escape(m["destaque"]) + "</b>" + html.escape(b)
    else:
        forte = html.escape(forte)
    abre_forte = '<strong style="%s">' % estilo_forte if estilo_forte else "<strong>"
    if estilo_forte:
        return (html.escape(leve) + " " if leve else "") + abre_forte + forte + "</strong>"
    return ('<span class="marca-leve">%s</span> ' % html.escape(leve) if leve else "") + abre_forte + forte + "</strong>"


def versao_publicada():
    """A versão que o site oferece (docs/atualizacao/versao.json); pode estar atrás da versão do código."""
    try:
        return json.loads(MANIFESTO.read_text(encoding="utf-8")).get("versao") or versao()
    except (OSError, ValueError):
        return versao()


def aplicar(texto, m, campos_extras=None, versao_doc=None):
    campos = {"marca.nome": html.escape(m["nome"]), "marca.curto": html.escape(m["curto"]), "marca.logo": logo(m),
              "versao": html.escape(versao_doc or versao())}
    campos.update(campos_extras or {})
    for chave, valor in campos.items():
        texto = texto.replace("{{%s}}" % chave, valor)
    sobrou = re.findall(r"{{(?:marca\.\w+|versao)}}", texto)
    if sobrou:
        raise ValueError("marcação desconhecida: %s" % ", ".join(sorted(set(sobrou))))
    return texto


def instalar_txt(m):
    """O que o instalador lê: só chave=valor, uma por linha, com fim de linha do Windows."""
    v = json.loads(MANIFESTO.read_text(encoding="utf-8"))
    linhas = ["versao=%s" % v["versao"], "arquivo=%s" % v["arquivo"], "sha256=%s" % v["sha256"].lower(), "nome=%s" % m["nome"]]
    return "\r\n".join(linhas) + "\r\n"


def instalador_zip():
    """Um .zip com um arquivo só, sempre com os mesmos bytes para o mesmo INSTALAR.bat (data fixa)."""
    info = zipfile.ZipInfo("INSTALAR.bat", date_time=(2026, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(info, INSTALADOR.read_bytes())
    return buf.getvalue()


def manual_sem_arquivos(texto):
    """Teste do dono (0.7.30): o manual de dentro do programa não tem o favicon.svg ao lado (o pacote não leva imagens);
    o ícone e o logo vão embutidos no próprio HTML, como na tela."""
    from urllib.parse import quote
    svg = (DESTINO / "favicon.svg").read_text(encoding="utf-8").strip()
    uri = "data:image/svg+xml," + quote(svg, safe=" :/=")
    texto = texto.replace('<link rel="icon" href="/favicon-32.png" type="image/png" sizes="32x32">\n', "")
    texto = texto.replace('<link rel="apple-touch-icon" href="/apple-touch-icon.png">\n', "")  # revisão da 0.7.31: o pacote não leva esse arquivo
    texto = texto.replace('<link rel="preload" href="fontes/figtree.woff2" as="font" type="font/woff2" crossorigin>\n', "")
    texto = texto.replace('@font-face { font-family: "Figtree"; src: url("fontes/figtree.woff2") format("woff2"); font-weight: 300 900; font-style: normal; font-display: swap; }\n', "")  # a fonte do site não vai no pacote
    return texto.replace('href="/favicon.svg"', f'href="{uri}"').replace('src="favicon.svg"', f'src="{uri}"')


def gerar(m):
    """{caminho: conteúdo (str ou bytes)} de tudo o que é gerado."""
    saida = {}
    def gerar_pagina(origem, versao_doc):
        texto = aplicar(origem.read_text(encoding="utf-8"), m, versao_doc=versao_doc)
        primeira, _, resto = texto.partition("\n")
        return primeira + "\n" + AVISO.format(arquivo=origem.name) + resto
    for origem in sorted(PAGINAS.glob("*.html")):
        # O site mostra a versão publicada; o manual que vai no pacote, a versão do código.
        saida[DESTINO / origem.name] = gerar_pagina(origem, versao_publicada())
    saida[MANUAL_ROBO] = manual_sem_arquivos(gerar_pagina(PAGINAS / "manual.html", versao()))
    saida[MARCA_ROBO] = json.dumps(m, ensure_ascii=False, indent=1) + "\n"
    saida[INSTALAR_TXT] = instalar_txt(m)
    saida[INSTALADOR_ZIP] = instalador_zip()
    return saida


def _atual(caminho, conteudo):
    if not caminho.exists():
        return False
    if isinstance(conteudo, bytes):
        return caminho.read_bytes() == conteudo
    return caminho.read_bytes() == conteudo.encode("utf-8")


def main(argv):
    m = carregar()
    gerados = gerar(m)
    if "--conferir" in argv:
        velhos = [str(c.relative_to(RAIZ)) for c, t in gerados.items() if not _atual(c, t)]
        if velhos:
            print("Desatualizado em relação a paginas/, instalador/, docs/marca.json e docs/atualizacao/versao.json:")
            print("  " + "\n  ".join(velhos))
            print("Rode: python ferramentas/marca.py")
            return 1
        print("Tudo em dia com a marca \"%s\" e a versão publicada." % m["nome"])
        return 0
    for caminho, conteudo in gerados.items():
        caminho.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(conteudo, bytes):
            caminho.write_bytes(conteudo)
        else:
            caminho.write_bytes(conteudo.encode("utf-8"))
        print("gerado: %s" % caminho.relative_to(RAIZ))
    print("Marca aplicada: %s" % m["nome"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
