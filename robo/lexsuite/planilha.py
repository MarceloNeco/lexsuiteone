"""Leitura e escrita de planilhas .xlsx (Office Open XML) só com a biblioteca padrão."""

import datetime as dt
import os
import re
import tempfile
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
LIMITE_BYTES = 50 * 1024 * 1024  # por parte lida
LIMITE_TOTAL = 1024 * 1024 * 1024  # do arquivo inteiro

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


# Estilos (0.7.12): 0 normal, 1 negrito (cabeçalho simples), 2 cabeçalho azul-marinho com letra branca, 3 texto com
# quebra de linha, 4 valor em R$, 5 valor em R$ destacado (fundo latão claro), 6 título grande.
_X_CAB, _X_TEXTO, _X_MOEDA, _X_MOEDA_DEST, _X_TITULO, _X_AVISO = 2, 3, 4, 5, 6, 7


def _celula(ref, v, estilo):
    est = (f' s="{int(estilo)}"' if estilo is not True else ' s="1"') if estilo else ""
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


def _ncols(aba):
    return max((len(l) for l in (aba.get("linhas") or [])), default=0)


def _linha_cab(aba):
    """Linha do cabeçalho: 2 quando a aba tem a linha de aviso no topo (0.7.14), senão 1."""
    return 2 if aba.get("aviso") else 1


def _estilo(aba, i, j):
    """Estilo da célula (linha i a partir de 1, coluna j a partir de 0). Aba com "visual": cabeçalho escuro, texto com
    quebra, colunas de dinheiro em R$ e linhas destacadas; sem "visual", como antes (só o cabeçalho em negrito)."""
    cab = _linha_cab(aba)
    if aba.get("aviso") and i == 1:
        return _X_AVISO
    if not aba.get("visual"):
        return i == cab
    if i == cab:
        return _X_CAB
    if j in (aba.get("moeda") or ()):
        return _X_MOEDA_DEST if (i - cab) in (aba.get("destacar") or ()) else _X_MOEDA
    return _X_TEXTO


def _xml_aba(aba):
    linhas = aba.get("linhas") or []
    cab = _linha_cab(aba)
    if aba.get("aviso"):
        linhas = [[aba["aviso"]]] + list(linhas)
    larguras = aba.get("larguras")
    congelar = aba.get("congelar_cabecalho", True)
    fixar_col = int(aba.get("fixar_colunas") or 0)
    ncols = max((len(l) for l in linhas[cab - 1:]), default=0)
    ult = f"{_col(max(ncols, 1) - 1)}{max(len(linhas), 1)}"
    p = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n',
         f'<worksheet xmlns="{NS}" xmlns:r="{NS_R}">',
         f'<dimension ref="A1:{ult}"/>']
    if congelar and linhas and fixar_col:
        p.append(f'<sheetViews><sheetView workbookViewId="0"><pane xSplit="{fixar_col}" ySplit="{cab}" '
                 f'topLeftCell="{_col(fixar_col)}{cab + 1}" activePane="bottomRight" state="frozen"/></sheetView></sheetViews>')
    elif congelar and linhas:
        p.append(f'<sheetViews><sheetView workbookViewId="0"><pane ySplit="{cab}" topLeftCell="A{cab + 1}" '
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
        cels = "".join(_celula(f"{_col(j)}{i}", v, _estilo(aba, i, j)) for j, v in enumerate(linha))
        altura = ' ht="36" customHeight="1"' if (aba.get("aviso") and i == 1) else (' ht="30" customHeight="1"' if (aba.get("visual") and i == cab) else "")
        p.append(f'<row r="{i}"{altura}>{cels}</row>')
    p.append("</sheetData>")
    if aba.get("proteger"):  # sem senha: é cautela, não trava; filtro, ordenação e largura de coluna continuam livres
        p.append('<sheetProtection sheet="1" objects="1" scenarios="1" formatColumns="0" formatRows="0" sort="0" autoFilter="0"/>')
    if aba.get("filtro") and len(linhas) >= cab and ncols:
        p.append(f'<autoFilter ref="A{cab}:{ult}"/>')
    if aba.get("aviso") and ncols > 1:
        p.append(f'<mergeCells count="1"><mergeCell ref="A1:{_col(ncols - 1)}1"/></mergeCells>')
    p.append("</worksheet>")
    return "".join(p)


def liberar_escrita(caminho):
    """0.7.21: tira a marca "somente leitura" do Windows (a planilha de consulta fica marcada entre uma gravação e outra)."""
    import stat
    try:
        if os.path.exists(caminho) and not (os.stat(caminho).st_mode & stat.S_IWRITE):  # bit, não os.access (root)
            os.chmod(caminho, stat.S_IREAD | stat.S_IWRITE)
    except OSError:
        pass


def marcar_so_leitura(caminho):
    """0.7.21 (decisão do dono): a planilha de consulta abre só para leitura para todo mundo, inclusive com dois cliques no
    Explorer ou no Drive. O RADAR tira a marca no instante de regravar e põe de volta."""
    import stat
    try:
        os.chmod(caminho, stat.S_IREAD)
    except OSError:
        pass


def marcar_se_livre(caminho):
    """0.7.25 (revisão): marca "somente leitura" só se ninguém estiver com a planilha aberta para editar (o Excel trava a
    escrita; marcar por baixo dele faria o Salvar falhar). Devolve False quando ela estava em uso; já marcada conta como livre."""
    import stat
    try:
        if not (os.stat(caminho).st_mode & stat.S_IWRITE):
            return True
        with open(caminho, "r+b"):
            pass
    except OSError:
        return False
    marcar_so_leitura(caminho)
    return True


def escrever_xlsx(caminho, abas, so_leitura_recomendado=False, marcar=False):
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
    # Filtro automático: o Excel e o Google Planilhas esperam o nome oculto _xlnm._FilterDatabase de cada aba filtrada.
    nomes = "".join(
        f'<definedName name="_xlnm._FilterDatabase" localSheetId="{i}" hidden="1">'
        f"'{_texto_xml(a['nome']).replace(chr(39), chr(39) * 2)}'!$A${_linha_cab(a)}:${_col(_ncols(a) - 1)}${len(a['linhas']) + _linha_cab(a) - 1}"
        "</definedName>"
        for i, a in enumerate(abas) if a.get("filtro") and a.get("linhas") and _ncols(a))
    wb = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
          f'<workbook xmlns="{NS}" xmlns:r="{NS_R}">'
          + ('<fileSharing readOnlyRecommended="1"/>' if so_leitura_recomendado else '')
          + '<bookViews><workbookView activeTab="0"/></bookViews>'
          f'<sheets>{folhas}</sheets>'
          + (f"<definedNames>{nomes}</definedNames>" if nomes else "") + '</workbook>')
    wbrels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
              f'<Relationships xmlns="{NS_PKG_REL}">'
              + "".join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>' for i in range(1, n + 1))
              + f'<Relationship Id="rId{n + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
              '</Relationships>')
    estilos = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
               f'<styleSheet xmlns="{NS}">'
               '<numFmts count="1"><numFmt numFmtId="164" formatCode="&quot;R$&quot; #,##0"/></numFmts>'
               '<fonts count="4"><font><sz val="11"/><name val="Calibri"/></font>'
               '<font><b/><sz val="11"/><name val="Calibri"/></font>'
               '<font><b/><sz val="11"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>'
               '<font><b/><sz val="14"/><color rgb="FF0F1D33"/><name val="Calibri"/></font></fonts>'
               '<fills count="6"><fill><patternFill patternType="none"/></fill>'
               '<fill><patternFill patternType="gray125"/></fill>'
               '<fill><patternFill patternType="solid"><fgColor rgb="FF0F1D33"/><bgColor indexed="64"/></patternFill></fill>'
               '<fill><patternFill patternType="solid"><fgColor rgb="FFF7F0E1"/><bgColor indexed="64"/></patternFill></fill>'
               '<fill><patternFill patternType="solid"><fgColor rgb="FFB42F2F"/><bgColor indexed="64"/></patternFill></fill>'
               '<fill><patternFill patternType="solid"><fgColor rgb="FF1E6B45"/><bgColor indexed="64"/></patternFill></fill></fills>'
               '<borders count="2"><border><left/><right/><top/><bottom/><diagonal/></border>'
               '<border><left/><right/><top/><bottom style="thin"><color rgb="FFD9DEE7"/></bottom><diagonal/></border></borders>'
               '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
               '<cellXfs count="9"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
               '<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>'
               '<xf numFmtId="0" fontId="2" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1" applyAlignment="1">'
               '<alignment vertical="center" wrapText="1"/></xf>'
               '<xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyBorder="1" applyAlignment="1">'
               '<alignment vertical="top" wrapText="1"/></xf>'
               '<xf numFmtId="164" fontId="0" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyBorder="1" applyAlignment="1">'
               '<alignment vertical="top"/></xf>'
               '<xf numFmtId="164" fontId="1" fillId="3" borderId="1" xfId="0" applyNumberFormat="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">'
               '<alignment vertical="top"/></xf>'
               '<xf numFmtId="0" fontId="3" fillId="0" borderId="0" xfId="0" applyFont="1"/>'
               '<xf numFmtId="0" fontId="2" fillId="4" borderId="0" xfId="0" applyFont="1" applyFill="1" applyAlignment="1">'
               '<alignment vertical="center" wrapText="1"/></xf>'
               '<xf numFmtId="0" fontId="2" fillId="5" borderId="0" xfId="0" applyFont="1" applyFill="1" applyAlignment="1">'
               '<alignment vertical="center" wrapText="1"/></xf></cellXfs>'
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
        liberar_escrita(caminho)  # no Windows, trocar um arquivo marcado "somente leitura" falha
        try:
            os.replace(tmp, caminho)
        except PermissionError:  # 0.7.24: a tela pode ter marcado de novo no mesmo instante ("Abrir a planilha"); mais uma vez
            liberar_escrita(caminho)
            os.replace(tmp, caminho)
        if marcar:
            marcar_so_leitura(caminho)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        if marcar and os.path.exists(caminho):
            marcar_so_leitura(caminho)  # 0.7.21 (revisão): troca falhou, a planilha antiga volta a ficar só para leitura
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
    # Cada parte lida tem teto (protege contra arquivo zip que se expande demais); as abas não lidas não contam. O texto
    # compartilhado (o Excel guarda ali os textos de todas as abas) tem teto maior: com 60 mil linhas passa de 50 MB.
    if z.getinfo(nome).file_size > (LIMITE_BYTES * 4 if nome.endswith("sharedStrings.xml") else LIMITE_BYTES):
        raise ValueError(f"Parte grande demais (acima de 50 MB descompactado): {nome}")
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


def _nome_aba(n):
    return unicodedata.normalize("NFKD", str(n or "")).encode("ascii", "ignore").decode().strip().lower()


def ler_xlsx(caminho, so_abas=None):
    """Lê um .xlsx e devolve {"abas": [{"nome", "oculta", "linhas"}]}.
    `so_abas`: nomes das abas a ler (as outras vêm com linhas vazias, sem abrir o XML delas). Com a lista de processos
    grande (20 mil linhas no TRT2), ler só as abas editáveis é rápido e não esbarra no limite de tamanho (0.7.16)."""
    quero = {_nome_aba(n) for n in so_abas} if so_abas else None
    with zipfile.ZipFile(caminho) as z:
        infos = {i.filename: i.file_size for i in z.infolist()}
        if sum(infos.values()) > LIMITE_TOTAL:
            raise ValueError("Arquivo grande demais (acima de 1 GB descompactado).")
        nomes = set(infos)
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
            if parte in nomes and (quero is None or _nome_aba(s.get("name")) in quero):
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
