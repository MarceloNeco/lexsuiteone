"""Leitura e escrita de planilhas .xlsx (Office Open XML) só com a biblioteca padrão."""

import datetime as dt
import os
import re
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
LIMITE_BYTES = 50 * 1024 * 1024

# Caracteres inválidos em XML 1.0
_INVALIDOS = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f￾￿\ud800-\udfff]")
_NOME_RUIM = re.compile(r"[\[\]:*?/\\]")


def _limpa(txt):
    return _INVALIDOS.sub("", txt)


def _col(n):
    """Número da coluna (0 = A) -> letras."""
    s = ""
    n += 1
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def _texto_xml(txt):
    return escape(_limpa(txt), {'"': "&quot;"})


def _celula(ref, v, estilo):
    est = ' s="1"' if estilo else ""
    if v is None:
        return f'<c r="{ref}"{est}/>' if estilo else ""
    if isinstance(v, bool):
        return f'<c r="{ref}"{est} t="b"><v>{int(v)}</v></c>'
    if isinstance(v, (int, float)):
        if isinstance(v, float) and (v != v or v in (float("inf"), float("-inf"))):
            v = str(v)
        else:
            return f'<c r="{ref}"{est}><v>{repr(v)}</v></c>'
    if isinstance(v, dt.datetime):
        v = v.strftime("%Y-%m-%d %H:%M")
    elif isinstance(v, dt.date):
        v = v.strftime("%Y-%m-%d")
    elif not isinstance(v, str):
        v = str(v)
    t = _texto_xml(v)
    pres = ' xml:space="preserve"' if v != v.strip() or "\n" in v else ""
    return f'<c r="{ref}"{est} t="inlineStr"><is><t{pres}>{t}</t></is></c>'


def _xml_aba(aba):
    linhas = aba.get("linhas") or []
    larguras = aba.get("larguras")
    congelar = aba.get("congelar_cabecalho", True)
    ncols = max((len(l) for l in linhas), default=0)
    ult = f"{_col(max(ncols, 1) - 1)}{max(len(linhas), 1)}"
    p = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n',
         f'<worksheet xmlns="{NS}" xmlns:r="{NS_R}">',
         f'<dimension ref="A1:{ult}"/>']
    if congelar and linhas:
        p.append('<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" '
                 'activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>')
    else:
        p.append('<sheetViews><sheetView workbookViewId="0"/></sheetViews>')
    p.append('<sheetFormatPr defaultRowHeight="15"/>')
    if larguras:
        p.append("<cols>")
        for i, w in enumerate(larguras, 1):
            p.append(f'<col min="{i}" max="{i}" width="{float(w)}" customWidth="1"/>')
        p.append("</cols>")
    p.append("<sheetData>")
    for i, linha in enumerate(linhas, 1):
        cels = "".join(_celula(f"{_col(j)}{i}", v, i == 1) for j, v in enumerate(linha))
        p.append(f'<row r="{i}">{cels}</row>')
    p.append("</sheetData></worksheet>")
    return "".join(p)


def escrever_xlsx(caminho, abas):
    """Grava um .xlsx de forma atômica. Levanta ValueError se as abas forem inválidas."""
    if not abas:
        raise ValueError("É preciso ao menos uma aba.")
    vistos = set()
    for a in abas:
        nome = a.get("nome")
        if not isinstance(nome, str) or not nome or len(nome) > 31 or _NOME_RUIM.search(nome):
            raise ValueError(f"Nome de aba inválido: {nome!r}")
        if nome.lower() in vistos:
            raise ValueError(f"Nome de aba duplicado: {nome!r}")
        vistos.add(nome.lower())
    if abas[0].get("oculta"):
        raise ValueError("A primeira aba não pode ser oculta.")

    n = len(abas)
    tipos = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
             '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
             '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
             '<Default Extension="xml" ContentType="application/xml"/>'
             '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
             + "".join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>' for i in range(1, n + 1))
             + '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
             '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
             '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
             '</Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            f'<Relationships xmlns="{NS_PKG_REL}">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
            '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
            '</Relationships>')
    oculto = ' state="hidden"'
    folhas = "".join(
        f'<sheet name="{_texto_xml(a["nome"])}" sheetId="{i}"'
        f'{oculto if a.get("oculta") else ""} r:id="rId{i}"/>'
        for i, a in enumerate(abas, 1))
    wb = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
          f'<workbook xmlns="{NS}" xmlns:r="{NS_R}">'
          '<bookViews><workbookView activeTab="0"/></bookViews>'
          f'<sheets>{folhas}</sheets></workbook>')
    wbrels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
              f'<Relationships xmlns="{NS_PKG_REL}">'
              + "".join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>' for i in range(1, n + 1))
              + f'<Relationship Id="rId{n + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
              '</Relationships>')
    estilos = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
               f'<styleSheet xmlns="{NS}">'
               '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font>'
               '<font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'
               '<fills count="2"><fill><patternFill patternType="none"/></fill>'
               '<fill><patternFill patternType="gray125"/></fill></fills>'
               '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
               '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
               '<cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
               '<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/></cellXfs>'
               '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
               '</styleSheet>')
    agora = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    core = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:creator>LexSuite</dc:creator>'
            f'<dcterms:created xsi:type="dcterms:W3CDTF">{agora}</dcterms:created>'
            f'<dcterms:modified xsi:type="dcterms:W3CDTF">{agora}</dcterms:modified></cp:coreProperties>')
    app = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
           '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
           '<Application>LexSuite</Application></Properties>')

    pasta = os.path.dirname(os.path.abspath(caminho))
    fd, tmp = tempfile.mkstemp(suffix=".tmp", dir=pasta)
    os.close(fd)
    try:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", tipos)
            z.writestr("_rels/.rels", rels)
            z.writestr("docProps/core.xml", core)
            z.writestr("docProps/app.xml", app)
            z.writestr("xl/workbook.xml", wb)
            z.writestr("xl/_rels/workbook.xml.rels", wbrels)
            z.writestr("xl/styles.xml", estilos)
            for i, a in enumerate(abas, 1):
                z.writestr(f"xl/worksheets/sheet{i}.xml", _xml_aba(a))
        os.replace(tmp, caminho)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


# ---------------------------------------------------------------- leitura

def _q(tag):
    return f"{{{NS}}}{tag}"


def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _texto_si(el):
    """Texto de <si>/<is>: junta <t> ignorando fonéticos (<rPh>)."""
    partes = []
    for filho in el:
        nome = _local(filho.tag)
        if nome == "t":
            partes.append(filho.text or "")
        elif nome == "r":
            for t in filho:
                if _local(t.tag) == "t":
                    partes.append(t.text or "")
    return "".join(partes)


def _num(txt):
    txt = (txt or "").strip()
    if not txt:
        return ""
    try:
        return int(txt)
    except ValueError:
        pass
    try:
        f = float(txt)
    except ValueError:
        return txt
    if f == f and abs(f) < 1e15 and f == int(f):
        return int(f)
    return f


def _indice_col(ref):
    letras = re.match(r"([A-Za-z]+)", ref or "")
    if not letras:
        return None
    n = 0
    for c in letras.group(1).upper():
        n = n * 26 + ord(c) - 64
    return n - 1


def _caminho_parte(destino):
    if destino.startswith("/"):
        return destino.lstrip("/")
    partes = ["xl"]
    for p in destino.split("/"):
        if p == "..":
            if partes:
                partes.pop()
        elif p and p != ".":
            partes.append(p)
    return "/".join(partes)


def _ler_xml(z, nome):
    dados = z.read(nome)
    # Planilha é entrada não confiável: nenhuma DTD ou entidade é aceita (evita XML bomb e entidade externa).
    if b"<!DOCTYPE" in dados or b"<!ENTITY" in dados:
        raise ValueError(f"XML com DTD não é aceito ({nome})")
    return ET.fromstring(dados)  # nosec B314 - sem DTD/entidades (checado acima); ElementTree não resolve entidades externas


def _valor(c, compart):
    t = c.get("t")
    if t == "inlineStr":
        is_ = c.find(_q("is"))
        return _texto_si(is_) if is_ is not None else ""
    v = c.find(_q("v"))
    txt = v.text if v is not None and v.text is not None else ""
    if t == "s":
        try:
            return compart[int(txt)]
        except (ValueError, IndexError):
            return ""
    if t == "b":
        return txt.strip() in ("1", "true")
    if t in ("str", "e"):
        return txt
    if t == "d":
        return txt
    return _num(txt)


def ler_xlsx(caminho):
    """Lê um .xlsx e devolve {"abas": [{"nome", "oculta", "linhas"}]}."""
    with zipfile.ZipFile(caminho) as z:
        if sum(i.file_size for i in z.infolist()) > LIMITE_BYTES:
            raise ValueError("Arquivo grande demais (acima de 50 MB descompactado).")
        nomes = set(z.namelist())
        wb = _ler_xml(z, "xl/workbook.xml")
        alvos = {}
        if "xl/_rels/workbook.xml.rels" in nomes:
            for r in _ler_xml(z, "xl/_rels/workbook.xml.rels"):
                alvos[r.get("Id")] = _caminho_parte(r.get("Target", ""))
        compart = []
        if "xl/sharedStrings.xml" in nomes:
            for si in _ler_xml(z, "xl/sharedStrings.xml").iter(_q("si")):
                compart.append(_texto_si(si))
        abas = []
        folhas = wb.find(_q("sheets"))
        for n, s in enumerate(folhas if folhas is not None else [], 1):
            rid = s.get(f"{{{NS_R}}}id")
            parte = alvos.get(rid) or f"xl/worksheets/sheet{n}.xml"
            linhas = []
            if parte in nomes:
                dados = _ler_xml(z, parte).find(_q("sheetData"))
                for row in (dados if dados is not None else []):
                    atual = []
                    seq = 0
                    for c in row.findall(_q("c")):
                        pos = _indice_col(c.get("r"))
                        if pos is None:
                            pos = seq
                        while len(atual) < pos:
                            atual.append("")
                        val = _valor(c, compart)
                        if pos < len(atual):
                            atual[pos] = val
                        else:
                            atual.append(val)
                        seq = pos + 1
                    while atual and atual[-1] == "":
                        atual.pop()
                    linhas.append(atual)
            abas.append({"nome": s.get("name", ""),
                         "oculta": s.get("state") in ("hidden", "veryHidden"),
                         "linhas": linhas})
    return {"abas": abas}
