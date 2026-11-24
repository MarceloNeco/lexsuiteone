"""0.7.53 (decisões 59 a 62 do dono, 24/Nov): amostras e assinaturas de FORMATO de todas as fontes que o RADAR lê.

Para que serve: quando uma fonte (caderno do Diário, consulta pública, Receita, CNJ, resposta da área logada) muda de
formato, a SolverONE fica sabendo sem depender do relato do advogado, e ajusta o pedido e o leitor na versão seguinte.

O que é guardado e enviado (desenho `documentacao/DESENHO-AMOSTRA-E-PLANILHA-EM-REDE.md`, parte A):
- **Amostra anonimizada**: a resposta da fonte com TODO o conteúdo trocado caractere por caractere (letra por letra da mesma
  caixa, dígito por dígito, acento por acento), com o mesmo tamanho, os mesmos símbolos, quebras de linha e chaves do JSON.
  Ficam só as palavras fixas do protocolo e os valores tabelados das fontes (listas abaixo, no código). A troca é aleatória
  (`secrets`) e o mapa fica só na memória: não há como voltar ao original. Nunca sai CPF ou CNPJ com dígito verificador válido.
  Contato de sócio sai com o tamanho arredondado (decisão 61).
- **Assinatura de formato**: só a lista de campos, tipos e presença (nenhum conteúdo), com um hash. Hash novo numa fonte =
  "mudança de formato", registrada na Saúde do computador e enviada à SolverONE (RootifyONE).

Sempre ligado, sem chave nas Configurações (decisão 60). Nada aparece na tela: sem internet ou com a SolverONE fora, os envios
ficam numa fila no banco local e são tentados de novo mais tarde, em silêncio. O envio só começa quando a SolverONE liga o
recurso `amostras` da licença (lex-conta v21); antes disso a fila apenas guarda. Só biblioteca padrão; nada de IA."""

import base64
import collections
import datetime as dt
import gzip
import hashlib
import json
import re
import secrets
import threading

MAX_POR_FONTE = 20           # amostras guardadas por fonte (as mais recentes)
TAM_AMOSTRA = 64 * 1024      # caracteres por amostra (o resto é cortado e marcado)
TETO_FILA = 5 * 1024 * 1024  # bytes na fila de envio; acima disso saem as amostras mais velhas (mudanças ficam)
ESPERAS = (300, 1800, 7200, 43200, 86400)  # 5 min, 30 min, 2 h, 12 h, depois 1 por dia
ITENS_JSON = 5               # itens de uma lista grande que entram na amostra (a assinatura vê até 200)
SOCIO_MULTIPLO = 8           # decisão 61: contato de sócio com o tamanho arredondado

# Palavras que ficam como estão (vocabulário do protocolo e dos endereços, não dado de ninguém)
FIXAS = {"RESPOSTA", "PARA", "O", "RADAR", "v1", "lote", "de", "processo", "dado", "valor", "resultado", "fonte", "data",
         "observação", "observacao", "valor_causa", "data_ajuizamento", "telefone", "email", "site", "endereco", "socio_contato",
         "outro", "encontrado", "nao_consta", "tentar_depois", "http", "https", "www", "com", "br", "adv", "gov", "jus", "org",
         "net", "pje", "PJe", "Receita", "Federal", "Diário", "DJEN", "CNJ", "sessão", "expirou", "outro", "tribunal", "a", "conferir"}
# Valores tabelados das fontes públicas (ficam iguais dentro do JSON)
VALORES_FIXOS = {"Intimação", "Notificação", "Citação", "Edital", "Lista de distribuição", "Lista de Distribuição", "Pauta",
                 "ATIVA", "BAIXADA", "INAPTA", "SUSPENSA", "NULA", "Ativa", "Baixada", "Inapta", "Suspensa", "Nula", "G1", "G2",
                 "JE", "SUP", "TR", "MATRIZ", "FILIAL", "ME", "EPP", "DEMAIS", "MICRO EMPRESA", "EMPRESA DE PEQUENO PORTE",
                 "true", "false", "S", "N", "SIM", "NAO", "NÃO"}
_SIGLA = re.compile(r"(TRT|TRF|TJ|TRE|TST|STJ|STF|TJM)[A-Z]{0,2}\d{0,2}")  # sigla de tribunal é pública
_CHAVE_SOCIO = re.compile(r"socio|sócio|qsa|email|e_mail|telefone|ddd", re.I)

_MAI, _MIN, _DIG = "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz", "0123456789"
_ACE_MIN, _ACE_MAI = "áàâãéêíóôõúç", "ÁÀÂÃÉÊÍÓÔÕÚÇ"

_trava = threading.Lock()
_buffer = collections.OrderedDict()  # fonte -> [(quando, tipo, dados)]; as funções de leitura só depositam aqui


# --- Troca irreversível ----------------------------------------------------------------------------------------------

def _trocar_char(c):
    if c in _DIG:
        return secrets.choice(_DIG)
    if c in _MAI:
        return secrets.choice(_MAI)
    if c in _MIN:
        return secrets.choice(_MIN)
    if c in _ACE_MIN:
        return secrets.choice(_ACE_MIN)
    if c in _ACE_MAI:
        return secrets.choice(_ACE_MAI)
    if c.isalpha():
        return secrets.choice(_MAI if c.isupper() else _MIN)
    return c


def _trocar_palavra(w, mapa):
    if w in FIXAS or not w:
        return w
    if w not in mapa:
        mapa[w] = "".join(_trocar_char(c) for c in w)
    return mapa[w]


def _dv_cpf(d):
    s1 = sum(int(d[i]) * (10 - i) for i in range(9)) * 10 % 11 % 10
    s2 = sum(int(d[i]) * (11 - i) for i in range(10)) * 10 % 11 % 10
    return d[9] == str(s1) and d[10] == str(s2)


def _dv_cnpj(d):
    def dv(base, pesos):
        r = sum(int(x) * p for x, p in zip(base, pesos)) % 11
        return "0" if r < 2 else str(11 - r)
    p1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    return d[12] == dv(d[:12], p1) and d[13] == dv(d[:13], [6] + p1)


def _sem_documento_valido(texto):
    """Nunca sai um CPF ou CNPJ válido: se a troca gerou um por acaso, o último dígito muda."""
    def corrige(m):
        bruto = m.group(0)
        dig = re.sub(r"\D", "", bruto)
        valido = (len(dig) == 11 and _dv_cpf(dig)) or (len(dig) == 14 and _dv_cnpj(dig))
        if not valido:
            return bruto
        ult = bruto.rstrip()[-1]
        return bruto[:len(bruto.rstrip()) - 1] + str((int(ult) + 1) % 10) + bruto[len(bruto.rstrip()):]
    return re.sub(r"\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}|\d{3}\.?\d{3}\.?\d{3}-?\d{2}", corrige, texto)


def trocar_texto(texto, mapa=None):
    """Troca palavra por palavra (a mesma palavra vira o mesmo sorteio dentro de uma amostra), mantendo separadores."""
    mapa = {} if mapa is None else mapa
    partes = re.split(r"([^\w]+)", str(texto))
    return _sem_documento_valido("".join(p if i % 2 else _trocar_palavra(p, mapa) for i, p in enumerate(partes)))


def _chave_de_esquema(k):
    """Chave de JSON que é nome de campo (fica): letras ASCII, dígito só no fim, sublinhado, até 40; o resto é tratado como dado."""
    return bool(re.fullmatch(r"[A-Za-z_][A-Za-z_]{0,37}\d{0,2}", str(k)))


def _arredondar(s):
    n = len(s)
    alvo = ((n + SOCIO_MULTIPLO - 1) // SOCIO_MULTIPLO) * SOCIO_MULTIPLO
    return s + "".join(secrets.choice(_MIN) for _ in range(alvo - n))


def trocar_json(obj, mapa=None, chave=""):
    mapa = {} if mapa is None else mapa
    if isinstance(obj, dict):
        saida = {}
        for k, v in obj.items():
            k2 = k if _chave_de_esquema(k) else trocar_texto(k, mapa)  # chave que parece dado (número, nome, espaço) também é trocada
            saida[k2] = trocar_json(v, mapa, str(k))
        return saida
    if isinstance(obj, list):
        return [trocar_json(v, mapa, chave) for v in obj[:ITENS_JSON]]
    if isinstance(obj, bool) or obj is None:
        return obj
    if isinstance(obj, (int, float)):
        s = str(obj)
        t = "".join(secrets.choice(_DIG) if c.isdigit() else c for c in s)
        t = _sem_documento_valido(t)  # revisão: número de 11 ou 14 dígitos nunca vira CPF ou CNPJ válido
        try:
            return type(obj)(t) if t.strip("-.") else obj
        except ValueError:
            return obj
    s = str(obj)
    if s in VALORES_FIXOS or _SIGLA.fullmatch(s):
        return s
    t = trocar_texto(s, mapa)
    return _arredondar(t) if _CHAVE_SOCIO.search(chave or "") else t


def trocar_resposta_area(texto, mapa=None):
    """Texto colado da área logada: troca tudo, menos o protocolo; a célula "valor" da linha socio_contato sai arredondada."""
    mapa = {} if mapa is None else mapa
    linhas = []
    for linha in str(texto).splitlines(keepends=True):
        if "RESPOSTA PARA O RADAR" in linha.upper() and len(linha) < 120:  # o cabeçalho do protocolo fica igual (lote N de M)
            linhas.append(linha)
            continue
        t = trocar_texto(linha, mapa)
        if "socio_contato" in linha and linha.lstrip().startswith("|"):
            cel = t.split("|")
            if len(cel) > 4:
                cel[3] = _arredondar(cel[3].rstrip()) + " "
            t = "|".join(cel)
        linhas.append(t)
    return "".join(linhas)


# --- Assinatura de formato (nenhum conteúdo) ---------------------------------------------------------------------------

def _tipo(v):
    return "nulo" if v is None else "bool" if isinstance(v, bool) else "num" if isinstance(v, (int, float)) else \
        "lista" if isinstance(v, list) else "obj" if isinstance(v, dict) else "str"


def assinatura_json(obj):
    """Caminhos com tipo e presença, ex.: 'items[].valor:num 40%'. Listas: até 200 elementos."""
    cont, total = collections.Counter(), collections.Counter()

    def anda(v, caminho):
        if isinstance(v, dict):
            total[caminho] += 1
            for k, x in v.items():
                chave = str(k) if _chave_de_esquema(k) else "#"
                cont[(caminho + "." + chave if caminho else chave, _tipo(x))] += 1
                anda(x, caminho + "." + chave if caminho else chave)
        elif isinstance(v, list):
            for x in v[:200]:
                anda(x, caminho + "[]")
    anda(obj, "")
    linhas = []
    for (cam, tipo), n in sorted(cont.items()):
        pai = cam.rsplit(".", 1)[0] if "." in cam else ""
        pct = round(100 * n / max(1, total.get(pai, 1)))
        linhas.append(f"{cam}:{tipo} {min(pct, 100)}%")
    return linhas


def assinatura_area(texto):
    """Resposta da área logada: cabeçalho do protocolo (números trocados por N), títulos das colunas e valores de dado/resultado."""
    sai = set()
    for linha in str(texto).splitlines():
        s = linha.strip()
        if "RESPOSTA PARA O RADAR" in s.upper():
            sai.add("cab:" + re.sub(r"\d+", "N", s.upper()))
        elif s.startswith("|") and not re.match(r"^\|[\s:\-|]+\|?$", s):
            cel = [c.strip().lower() for c in s.strip("|").split("|")]
            if "processo" in cel and "dado" in cel:
                sai.add("colunas:" + "|".join(cel))
            else:
                for c in cel:
                    if c in ("valor_causa", "data_ajuizamento", "telefone", "email", "site", "endereco", "socio_contato", "outro",
                             "encontrado", "nao_consta", "tentar_depois"):
                        sai.add("valor:" + c)
    return sorted(sai) or ["formato não reconhecido"]


def hash_de(assinatura):
    return hashlib.sha256("\n".join(assinatura).encode("utf-8")).hexdigest()


def diferenca(antes, depois):
    """O que mudou entre duas assinaturas: campos novos e campos que sumiram (com o tipo)."""
    a = {l.split(" ")[0] for l in antes or []}
    d = {l.split(" ")[0] for l in depois or []}
    return {"novos": sorted(d - a)[:50], "sumiram": sorted(a - d)[:50]}


# --- Coleta (as funções de leitura chamam `observar`; ninguém espera por isso) ------------------------------------------

def observar(fonte, dados, tipo="json"):
    """Deposita a resposta de uma fonte para virar amostra. Nunca levanta exceção e nunca atrasa a leitura: só guarda na
    memória (até 3 por fonte); `descarregar` faz o resto no fim da leitura. `tipo`: "json" ou "texto" (área logada)."""
    try:
        if not fonte or dados is None:
            return
        with _trava:
            lst = _buffer.setdefault(str(fonte)[:60], [])
            lst.append((dt.datetime.now().isoformat(timespec="seconds"), tipo, dados))
            del lst[:-3]
            while len(_buffer) > 120:
                _buffer.popitem(last=False)
    except Exception:  # nosec B110 - amostra nunca atrapalha a leitura
        pass


def criar_tabelas(con):
    con.executescript("""
        CREATE TABLE IF NOT EXISTS amostras (id INTEGER PRIMARY KEY AUTOINCREMENT, fonte TEXT, quando TEXT, hash TEXT, conteudo TEXT);
        CREATE TABLE IF NOT EXISTS formatos (fonte TEXT, hash TEXT, assinatura TEXT, primeira_vez TEXT, ultima_vez TEXT,
            vezes INTEGER DEFAULT 0, PRIMARY KEY (fonte, hash));
        CREATE TABLE IF NOT EXISTS envios (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT, corpo TEXT, criado_em TEXT,
            tentativas INTEGER DEFAULT 0, proxima_em TEXT DEFAULT '');
    """)


def _amostra_texto(tipo, dados):
    if tipo == "texto":
        bruto = str(dados)
        corte = len(bruto) - TAM_AMOSTRA
        txt = trocar_resposta_area(bruto[:TAM_AMOSTRA])
        return txt + (f"\n[cortado: {corte} caracteres]" if corte > 0 else "")
    txt = json.dumps(trocar_json(dados), ensure_ascii=False)
    return txt[:TAM_AMOSTRA]


def descarregar(banco, agora=None, aviso=None):
    """Grava no banco o que foi observado: assinatura (e a mudança, se o hash for novo), a amostra anonimizada (20 por fonte)
    e o que vai para a fila de envio (a mudança sempre; uma amostra por fonte por dia). Devolve as mudanças achadas."""
    agora = agora or dt.datetime.now()
    with _trava:
        lote = [(f, list(v)) for f, v in _buffer.items()]
        _buffer.clear()
    if not lote:
        return []
    con, quando, mudancas = banco.con, agora.isoformat(timespec="seconds"), []
    criar_tabelas(con)
    for fonte, obs in lote:
        for _q, tipo, dados in obs:
            try:
                assin = assinatura_area(dados) if tipo == "texto" else assinatura_json(dados)
                h = hash_de(assin)
                ja, mud = con.execute("SELECT 1 FROM formatos WHERE fonte = ? AND hash = ?", (fonte, h)).fetchone(), None
                ant = con.execute("SELECT hash, assinatura FROM formatos WHERE fonte = ? ORDER BY ultima_vez DESC LIMIT 1", (fonte,)).fetchone()
                if ja:
                    con.execute("UPDATE formatos SET ultima_vez = ?, vezes = vezes + 1 WHERE fonte = ? AND hash = ?", (quando, fonte, h))
                else:
                    con.execute("INSERT INTO formatos VALUES (?,?,?,?,?,1)", (fonte, h, json.dumps(assin, ensure_ascii=False), quando, quando))
                    if ant:  # a fonte já tinha outro formato: mudança
                        dif = diferenca(json.loads(ant[1]), assin)
                        mud = {"fonte": fonte, "quando": quando, "hash_antes": ant[0], "hash_depois": h, "diferenca": dif}
                        mudancas.append(mud)
                        banco.registrar("saude", {"fonte": "Formato de " + fonte, "situacao": "atenção",
                                                  "detalhe": ("mudou: " + ", ".join(dif["novos"][:3] + ["-" + x for x in dif["sumiram"][:3]]))[:200]})
                    _enfileirar(con, "formato", {"fonte": fonte, "hash": h, "assinatura": assin[:400],
                                                 "mudanca": mud if ant else None}, quando)
                conteudo = _amostra_texto(tipo, dados)
                con.execute("INSERT INTO amostras (fonte, quando, hash, conteudo) VALUES (?,?,?,?)", (fonte, quando, h, conteudo))
                con.execute("DELETE FROM amostras WHERE fonte = ? AND id NOT IN (SELECT id FROM amostras WHERE fonte = ? "
                            "ORDER BY id DESC LIMIT ?)", (fonte, fonte, MAX_POR_FONTE))
                hoje = quando[:10]
                ja_hoje = con.execute("SELECT 1 FROM envios WHERE tipo = 'amostra' AND corpo LIKE ? AND criado_em >= ?",
                                      ('%"fonte": ' + json.dumps(fonte, ensure_ascii=False) + "%", hoje)).fetchone()
                if not ja_hoje or not ja:
                    _enfileirar(con, "amostra", {"fonte": fonte, "hash": h, "conteudo_gz": base64.b64encode(
                        gzip.compress(conteudo.encode("utf-8"))).decode("ascii")}, quando)
            except Exception as e:  # noqa: BLE001 - amostra nunca derruba nada
                if aviso:
                    aviso(f"  Amostra de formato de {fonte} não guardada ({e.__class__.__name__}).")
    _podar_fila(con)
    con.commit()
    return mudancas


def _enfileirar(con, tipo, corpo, quando):
    con.execute("INSERT INTO envios (tipo, corpo, criado_em, proxima_em) VALUES (?,?,?,?)",
                (tipo, json.dumps(corpo, ensure_ascii=False), quando, ""))


def _podar_fila(con):
    total = con.execute("SELECT coalesce(sum(length(corpo)), 0) FROM envios").fetchone()[0] or 0
    while total > TETO_FILA:
        r = con.execute("SELECT id, length(corpo) FROM envios WHERE tipo = 'amostra' ORDER BY id LIMIT 1").fetchone()
        if not r:
            break
        con.execute("DELETE FROM envios WHERE id = ?", (r[0],))
        total -= r[1] or 0


# --- Envio silencioso --------------------------------------------------------------------------------------------------

def enviar_pendentes(banco, cfg, versao, pedir=None, agora=None, maximo=20):
    """Manda à SolverONE (lex-conta, ações `formato` e `amostra`) o que está na fila e venceu. Nada vai para a tela: o que não
    foi aceito (sem internet, SolverONE fora, ação ainda desconhecida da nuvem) volta para a fila com nova tentativa mais
    tarde (5 min, 30 min, 2 h, 12 h, depois 1 por dia). Devolve quantos foram aceitos."""
    from . import conta, rede
    agora = agora or dt.datetime.now()
    con = banco.con
    criar_tabelas(con)
    c = (cfg or {}).get("conta") or {}
    if not c.get("codigo"):
        return 0
    # revisão da Operação: nada sai antes de a SolverONE estar pronta para receber (lex-conta v21) e ligar o recurso `amostras` da
    # licença no RootifyONE; até lá a fila só guarda (com teto). Assim o envio começa junto com a nuvem, com o "pode" do dono.
    if not ((c.get("recursos") or {}).get("amostras") is True):
        return 0
    agora_s, aceitos = agora.isoformat(timespec="seconds"), 0
    for id_, tipo, corpo, tent in con.execute("SELECT id, tipo, corpo, tentativas FROM envios WHERE proxima_em <= ? "
                                              "ORDER BY tipo = 'amostra', id LIMIT ?", (agora_s, maximo)).fetchall():
        envio = {"acao": tipo, "codigo": conta.normalizar(c.get("codigo")), "instalacao": c.get("instalacao", ""),
                 "versao": str(versao)[:20]}
        envio.update(json.loads(corpo))
        ok = False
        try:
            r = (pedir or rede.pedir_json)(c.get("url") or conta.URL_PADRAO, envio, tentativas=1, tempo_limite=15)
            ok = isinstance(r, dict) and r.get("ok") is True
        except Exception:  # nosec B110 - silencioso por decisão do dono (60); fica na fila
            ok = False
        if ok:
            con.execute("DELETE FROM envios WHERE id = ?", (id_,))
            aceitos += 1
        else:
            espera = ESPERAS[min(tent, len(ESPERAS) - 1)]
            # sem internet ou nuvem fora: este e os outros que já venceram esperam juntos (não insiste agora)
            con.execute("UPDATE envios SET tentativas = tentativas + 1, proxima_em = ? WHERE id = ? OR proxima_em <= ?",
                        ((agora + dt.timedelta(seconds=espera)).isoformat(timespec="seconds"), id_, agora_s))
            break
    con.commit()
    return aceitos


def previa(banco):
    """Para "O que a SolverONE recebe": a última amostra de cada fonte, exatamente como é (ou foi) enviada, e quando."""
    criar_tabelas(banco.con)
    saida = []
    for fonte, quando, conteudo in banco.con.execute(
            "SELECT fonte, quando, conteudo FROM amostras WHERE id IN (SELECT max(id) FROM amostras GROUP BY fonte) ORDER BY fonte"):
        saida.append({"fonte": fonte, "quando": quando, "conteudo": conteudo[:4000]})
    pend = banco.con.execute("SELECT count(*) FROM envios").fetchone()[0]
    return {"fontes": saida, "na_fila": pend}
