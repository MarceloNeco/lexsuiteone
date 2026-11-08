"""Nome do produto num lugar só.

A configuração é `docs/marca.json` (publicada no site, para o robô poder ler depois):

    {"nome": "RADAR JUDICIAL", "curto": "RADAR", "destaque": "IA"}

- nome: exatamente como deve aparecer, com maiúsculas e minúsculas (ex.: "RADAR JUDICIAL", "Lex One").
- curto: como o texto corrido chama o programa ("o RADAR"). Sem ele, vale a primeira palavra do nome.
- destaque: trecho da última palavra que fica em latão (ex.: "IA"). Vazio = nenhum.

As páginas do site são escritas em `paginas/` com as marcações {{marca.nome}}, {{marca.curto}} e {{marca.logo}};
este programa gera as versões publicadas em `docs/`. O e-mail de boas-vindas lê a mesma configuração ao ser
preenchido (`docs/email/preencher.py`).

Uso, na raiz do repositório:
    python ferramentas/marca.py              gera docs/ a partir de paginas/
    python ferramentas/marca.py --conferir   só confere se docs/ está em dia (usado pela automação do GitHub)

Só biblioteca padrão.
"""
import html
import json
import pathlib
import re
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CONFIG = RAIZ / "docs" / "marca.json"
PAGINAS = RAIZ / "paginas"
DESTINO = RAIZ / "docs"
AVISO = "<!-- Gerado por ferramentas/marca.py a partir de paginas/{arquivo} e docs/marca.json. Não edite aqui. -->\n"
PROIBIDOS = set('<>&"\'\\{}`')


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
            raise ValueError("marca.json: o campo %s não pode ter estes caracteres: < > & \" ' \\ { } `" % campo)
    if destaque and destaque not in nome.split(" ")[-1]:
        raise ValueError("marca.json: o destaque precisa estar dentro da última palavra do nome.")
    return {"nome": nome, "curto": curto, "destaque": destaque}


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


def aplicar(texto, m, campos_extras=None):
    campos = {"marca.nome": html.escape(m["nome"]), "marca.curto": html.escape(m["curto"]), "marca.logo": logo(m)}
    campos.update(campos_extras or {})
    for chave, valor in campos.items():
        texto = texto.replace("{{%s}}" % chave, valor)
    sobrou = re.findall(r"{{marca\.\w+}}", texto)
    if sobrou:
        raise ValueError("marcação desconhecida: %s" % ", ".join(sorted(set(sobrou))))
    return texto


def gerar(m):
    """{arquivo em docs/: conteúdo} para cada página de paginas/."""
    saida = {}
    for origem in sorted(PAGINAS.glob("*.html")):
        texto = aplicar(origem.read_text(encoding="utf-8"), m)
        primeira, _, resto = texto.partition("\n")
        saida[origem.name] = primeira + "\n" + AVISO.format(arquivo=origem.name) + resto
    return saida


def main(argv):
    m = carregar()
    paginas = gerar(m)
    if "--conferir" in argv:
        velhas = [n for n, t in paginas.items() if not (DESTINO / n).exists() or (DESTINO / n).read_text(encoding="utf-8") != t]
        if velhas:
            print("docs/ está desatualizado em relação a paginas/ e docs/marca.json: %s" % ", ".join(velhas))
            print("Rode: python ferramentas/marca.py")
            return 1
        print("docs/ em dia com a marca \"%s\"." % m["nome"])
        return 0
    for nome, texto in paginas.items():
        (DESTINO / nome).write_text(texto, encoding="utf-8")
        print("gerado: docs/%s" % nome)
    print("Marca aplicada: %s" % m["nome"])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
