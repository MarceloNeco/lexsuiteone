"""0.7.53 (decisões 63 a 65 do dono, 24/Nov): vários computadores do escritório na mesma pasta, SEM computador "mestre".

Como funciona (desenho `documentacao/DESENHO-AMOSTRA-E-PLANILHA-EM-REDE.md`, parte B):
- Cada computador grava o que fez (processos lidos, situação, quem viu, valores e contatos trazidos) em arquivos PRÓPRIOS, na
  pasta `<pasta das planilhas>/_RADAR (não mexer)/troca/<instalação>/`. Arquivo gravado nunca é reescrito; ninguém escreve na
  pasta do outro. Por isso não há como um computador apagar o trabalho do outro, nem na pasta de rede nem no Google Drive.
- Ao abrir o programa, antes de gravar a planilha e no botão "Trazer do escritório", o computador JUNTA no próprio banco o que
  os outros fizeram. A junção não depende da ordem e pode rodar de novo sem mudar nada:
    processo novo entra (se não foi apagado aqui pela limpeza); situação: vale a mais recente; "Visto" nunca passa por cima de
    uma situação trabalhada; valores: a fonte mais forte (ou igual e mais nova), como na área logada; contatos: somam.
- A planilha é só um espelho: antes de gravar, uma trava curta na pasta (2 minutos) evita dois gravando ao mesmo tempo, e o
  "vetor" guardado na aba Sobre impede que ela volte a uma versão mais velha (quem ainda não recebeu o que outro já gravou
  espera os arquivos chegarem pela sincronização).
- O que vem da pasta não é confiável: passa pelos mesmos filtros do programa (CPF, reclamante, testemunha) e arquivo de outra
  licença, corrompido ou grande demais é ignorado. Critérios e exclusões continuam de cada pessoa (decisão de 12/Nov) e não vão.
Só biblioteca padrão."""

import contextlib
import datetime as dt
import gzip
import hashlib
import json
import os
import platform
import re
import threading
import time

PASTA = "_RADAR (não mexer)"
FORMATO = 1
TRAVA_SEG = 120              # validade da trava de gravação da planilha
MAX_ARQUIVO = 20 * 1024 * 1024
DIAS_LIDOS = 30              # processos lidos que vão para os outros: só os últimos 30 dias dos tribunais escolhidos
ESPERA_ATRASO_H = 2          # planilha mais nova que este computador: espera os arquivos chegarem por até 2 h
LEIA_ME = ("Esta pasta é do RADAR JUDICIAL. Cada computador do escritório grava aqui o que fez (processos, situações, contatos), "
           "para os outros juntarem. Não apague nem edite: os dados também ficam em cada computador, mas a troca entre eles para.\n")
_CPF = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b|\bcpf\b", re.I)
_PROIBIDO = ("reclamante", "testemunha", "preposto", "advogado da parte", "advogada da parte")
_TRAVA_EXPORTAR = threading.Lock()  # revisão: tela e leitura nunca exportam ao mesmo tempo (o mesmo número de arquivo)
MAX_PENDENTES = 20000


def _agora_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def instalacao(cfg):
    from . import conta
    return conta._bloco(cfg)["instalacao"]


def computador():
    return (platform.node() or "computador")[:40]


def quem(cfg):
    """Nome de quem usa este computador e o computador, para "Visto por" e "Incluído por" (fica só na pasta do escritório)."""
    nome = ((cfg or {}).get("usuario") or {}).get("nome") or ((cfg or {}).get("usuario") or {}).get("email") or "alguém"
    return f"{str(nome).strip()[:60]} ({computador()})"


def _licenca(cfg):
    from . import conta
    cod = conta.normalizar(((cfg or {}).get("conta") or {}).get("codigo"))
    return hashlib.sha256(cod.encode("utf-8")).hexdigest()[:16] if cod else ""  # o código em si não vai para a pasta


def pasta(cfg):
    from . import compartilhar
    base = compartilhar.pasta_base(cfg)
    return os.path.join(base, PASTA) if base else ""


def _tabela(con):
    con.execute("CREATE TABLE IF NOT EXISTS troca (chave TEXT PRIMARY KEY, valor TEXT)")
    # revisão da Operação (B1): cada arquivo lido fica marcado por número (a ordem de chegada não importa); erro de leitura não
    # marca: o arquivo é tentado de novo (pode estar sincronizando) e só é dado por ruim depois de várias tentativas num dia
    con.execute("CREATE TABLE IF NOT EXISTS troca_lidos (instalacao TEXT, seq INTEGER, ignorado INTEGER DEFAULT 0, PRIMARY KEY (instalacao, seq))")
    con.execute("CREATE TABLE IF NOT EXISTS troca_falhas (instalacao TEXT, seq INTEGER, tentativas INTEGER DEFAULT 0, primeira_em TEXT, "
                "PRIMARY KEY (instalacao, seq))")


def _ler(con, chave, padrao=""):
    _tabela(con)
    r = con.execute("SELECT valor FROM troca WHERE chave = ?", (chave,)).fetchone()
    return r[0] if r else padrao


def _gravar(con, chave, valor):
    con.execute("INSERT OR REPLACE INTO troca VALUES (?,?)", (chave, str(valor)))


def _limpo(valor):
    """True se nada do item tem cara de pessoa física que não responde pela empresa (mesmos filtros do leitor)."""
    texto = json.dumps(valor, ensure_ascii=False).lower()
    return not _CPF.search(texto) and not any(p in texto for p in _PROIBIDO)


# --- Exportar o que este computador fez ---------------------------------------------------------------------------------

def exportar(banco, cfg, agora=None):
    """Grava um arquivo novo com o que mudou aqui desde a última vez (nada, se nada mudou). Devolve quantos itens foram."""
    with _TRAVA_EXPORTAR:
        return _exportar(banco, cfg, agora)


def _exportar(banco, cfg, agora=None):
    from . import banco as _bd, tribunais
    raiz = pasta(cfg)
    if not raiz:
        return 0
    con, inst = banco.con, instalacao(cfg)
    _tabela(con)
    agora = agora or _agora_utc()
    wm_lead, wm_cont = int(_ler(con, "wm_lead", "0")), int(_ler(con, "wm_contato", "0"))
    wm_acao = int(_ler(con, "wm_acao", "0"))
    escolhidos = {t.upper() for t in tribunais.validar(((cfg or {}).get("radar") or {}).get("tribunais") or ["TRT2", "TRT15"])}
    desde = (dt.date.today() - dt.timedelta(days=DIAS_LIDOS)).isoformat()
    itens, max_lead, max_cont, max_acao = [], wm_lead, wm_cont, wm_acao
    for rowid, proc, dados, trib in con.execute("SELECT rowid, processo, dados, tribunal FROM leads WHERE rowid > ? "
                                                 "AND coalesce(fora_criterio, 0) = 0 ORDER BY rowid", (wm_lead,)):
        max_lead = max(max_lead, rowid)
        d = json.loads(dados)
        if (trib or "").upper() not in escolhidos or str(d.get("data_publicacao") or "")[:10] < desde:
            continue
        resumo = {k: d[k] for k in _bd._RESUMO if k in d and k not in ("manual_historico",)}
        if d.get("empresa_receita"):
            resumo["empresa_receita"] = {k: v for k, v in d["empresa_receita"].items() if k in _bd._RESUMO_RECEITA and k != "socios"}
        itens.append({"t": "lead", "p": proc, "d": resumo})
    # revisão: as situações mudadas AQUI ficam numa fila (troca_sujos), sem depender do relógio nem do que veio de fora
    sujos = con.execute("SELECT id, processo FROM troca_sujos ORDER BY id").fetchall()
    max_sujo = sujos[-1][0] if sujos else 0
    for proc in sorted({p for _i, p in sujos}):
        r = con.execute("SELECT status, motivo, status_em, status_por, visto_por, visto_em FROM leads WHERE processo = ?", (proc,)).fetchone()
        if r:
            itens.append({"t": "sit", "p": proc, "s": r[0], "m": r[1] or "", "q": r[2] or "", "por": r[3] or "", "vp": r[4] or "", "vq": r[5] or ""})
    for rowid, alvo, acao in con.execute("SELECT rowid, alvo, acao FROM acoes WHERE rowid > ? AND acao LIKE 'completar:%' ORDER BY rowid", (wm_acao,)):
        max_acao = max(max_acao, rowid)
        campo = acao.split(":", 1)[1]
        r = con.execute("SELECT dados FROM leads WHERE processo = ?", (alvo,)).fetchone()
        m = ((json.loads(r[0]).get("manual") or {}).get(campo) or {}) if r else {}
        if m.get("valor") not in (None, ""):
            itens.append({"t": "campo", "p": alvo, "c": campo, "v": m.get("valor"), "f": m.get("fonte", ""), "dt": m.get("data", "")})
    max_acao = max(max_acao, con.execute("SELECT max(rowid) FROM acoes").fetchone()[0] or 0)
    for c in banco.contatos():
        if c["id"] > wm_cont:
            max_cont = max(max_cont, c["id"])
            itens.append({"t": "contato", **{k: c[k] for k in ("processo", "empresa", "canal", "valor", "de_pessoa", "fonte", "data",
                                                              "confianca", "origem", "observacao", "criado_em", "incluido_por", "computador")}})
    itens = [i for i in itens if _limpo(i)]
    if itens:
        destino = os.path.join(raiz, "troca", inst)
        os.makedirs(destino, exist_ok=True)
        # revisão da Operação (B2): banco recriado ou restaurado não volta a numerar do 1: parte do maior número que já existe na
        # pasta deste computador, e nunca grava por cima de um arquivo que os outros já possam ter lido
        na_pasta = [int(m.group(1)) for m in (_NOME.match(n) for n in os.listdir(destino)) if m]
        seq = max([int(_ler(con, "seq", "0"))] + na_pasta) + 1
        while any(n.startswith(f"{seq:08d}-") for n in os.listdir(destino)):
            seq += 1
        _leia_me(raiz)
        corpo = {"formato": FORMATO, "instalacao": inst, "licenca": _licenca(cfg), "seq": seq, "quem": quem(cfg),
                 "criado_em": agora, "itens": itens}
        nome = os.path.join(destino, f"{seq:08d}-{len(itens)}.json.gz")
        tmp = nome + ".parcial"
        with gzip.open(tmp, "wt", encoding="utf-8") as f:
            json.dump(corpo, f, ensure_ascii=False)
        if os.path.exists(nome):  # nunca por cima (não deveria acontecer: o número acima já é livre)
            os.remove(tmp)
            raise FileExistsError(nome)
        os.replace(tmp, nome)  # nasce inteiro: quem lê nunca vê arquivo pela metade
        _gravar(con, "seq", seq)
    _gravar(con, "wm_lead", max_lead); _gravar(con, "wm_contato", max_cont); _gravar(con, "wm_acao", max_acao)
    con.execute("DELETE FROM troca_sujos WHERE id <= ?", (max_sujo,))
    con.commit()
    _estado(cfg, banco)
    return len(itens)


def _leia_me(raiz):
    try:
        caminho = os.path.join(raiz, "LEIA-ME.txt")
        if not os.path.exists(caminho):
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(LEIA_ME)
    except OSError:
        pass


def _estado(cfg, banco):
    """`estado/<instalação>.json`: quem é este computador e até onde gravou (para os outros mostrarem "de Maria, até 10:32")."""
    from . import VERSAO
    raiz = pasta(cfg)
    try:
        os.makedirs(os.path.join(raiz, "estado"), exist_ok=True)
        dados = {"instalacao": instalacao(cfg), "quem": quem(cfg), "versao": VERSAO, "seq": int(_ler(banco.con, "seq", "0")),
                 "atualizado_em": _agora_utc(), "licenca": _licenca(cfg)}
        caminho = os.path.join(raiz, "estado", instalacao(cfg) + ".json")
        with open(caminho + ".parcial", "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False)
        os.replace(caminho + ".parcial", caminho)
    except OSError:
        pass


# --- Juntar o que os outros fizeram -------------------------------------------------------------------------------------

_NOME = re.compile(r"^(\d{8})-(\d+)\.json\.gz$")


def _arquivos_novos(cfg, banco):
    """[(instalação, seq, n, caminho)] dos outros computadores, ainda não juntados aqui, em ordem."""
    raiz = pasta(cfg)
    base = os.path.join(raiz, "troca") if raiz else ""
    if not base or not os.path.isdir(base):
        return []
    eu, saida = instalacao(cfg), []
    for inst in sorted(os.listdir(base)):
        if inst == eu or not re.fullmatch(r"[0-9a-f]{6,40}", inst):
            continue
        _tabela(banco.con)
        lidos = {r[0] for r in banco.con.execute("SELECT seq FROM troca_lidos WHERE instalacao = ?", (inst,))}
        try:
            nomes = sorted(os.listdir(os.path.join(base, inst)))
        except OSError:
            continue
        for nome in nomes:
            m = _NOME.match(nome)
            if m and int(m.group(1)) not in lidos:
                saida.append((inst, int(m.group(1)), int(m.group(2)), os.path.join(base, inst, nome)))
    return saida


def pendentes(banco, cfg):
    """Para o botão "Trazer do escritório (N)": quantos itens de outros computadores ainda não foram juntados aqui, e de quem."""
    novos = _arquivos_novos(cfg, banco)
    de, ate = [], ""
    raiz = pasta(cfg)
    for inst in sorted({a[0] for a in novos}):
        try:
            with open(os.path.join(raiz, "estado", inst + ".json"), encoding="utf-8") as f:
                e = json.load(f)
            de.append(str(e.get("quem") or "")[:80])
            ate = max(ate, str(e.get("atualizado_em") or ""))
        except (OSError, ValueError):
            de.append("")
    return {"n": sum(a[2] for a in novos), "de": [d for d in de if d], "ate": ate}


def juntar(banco, cfg, aviso=None):
    """Junta no banco deste computador o que os outros gravaram. Devolve quantos itens mudaram algo aqui."""
    lic, mudou = _licenca(cfg), 0
    apagados = {r[0] for r in banco.con.execute("SELECT processo FROM processos_apagados")} if _tem_tabela(banco.con, "processos_apagados") else set()
    for inst, seq, _n, caminho in _arquivos_novos(cfg, banco):
        try:
            if os.path.getsize(caminho) > MAX_ARQUIVO:
                raise _Definitivo("grande demais")
            with gzip.open(caminho, "rt", encoding="utf-8") as f:
                corpo = json.load(f)
            if not isinstance(corpo, dict) or corpo.get("formato") != FORMATO or corpo.get("instalacao") != inst \
                    or (lic and corpo.get("licenca") != lic):
                raise _Definitivo("de outra licença ou formato desconhecido")
            for item in corpo.get("itens") or []:
                if isinstance(item, dict) and _limpo(item):
                    try:
                        mudou += _aplicar(banco, item, apagados, str(corpo.get("quem") or ""))
                    except Exception:  # noqa: BLE001 - item estranho não para a junção dos outros
                        continue
        except _Definitivo as e:  # de outra licença ou formato desconhecido: não adianta tentar de novo
            _ignorar(banco, inst, seq, caminho, str(e), aviso)
            continue
        except Exception as e:  # noqa: BLE001 - pode estar sincronizando (incompleto, em uso): tenta de novo depois
            con = banco.con
            con.execute("INSERT INTO troca_falhas VALUES (?,?,1,?) ON CONFLICT(instalacao, seq) DO UPDATE SET tentativas = tentativas + 1",
                        (inst, seq, dt.datetime.now().isoformat(timespec="seconds")))
            t, desde = con.execute("SELECT tentativas, primeira_em FROM troca_falhas WHERE instalacao = ? AND seq = ?", (inst, seq)).fetchone()
            velho = (dt.datetime.now() - dt.datetime.fromisoformat(desde)).total_seconds() > FALHA_DESISTE_H * 3600
            if t >= FALHA_TENTATIVAS and velho:
                _ignorar(banco, inst, seq, caminho, e.__class__.__name__, aviso)
            con.commit()
            continue
        banco.con.execute("INSERT OR IGNORE INTO troca_lidos (instalacao, seq) VALUES (?,?)", (inst, seq))
        banco.con.execute("DELETE FROM troca_falhas WHERE instalacao = ? AND seq = ?", (inst, seq))
        banco.con.commit()
    mudou += _aplicar_pendentes(banco, apagados)
    if mudou:
        banco.registrar_acao(quem(cfg), "troca", "", "", f"{mudou} itens de outros computadores", mudou)
        banco.con.commit()
    return mudou


class _Definitivo(ValueError):
    """Arquivo que nunca vai servir aqui (outra licença, formato desconhecido, grande demais)."""


FALHA_TENTATIVAS = 10   # arquivo que não abre: tenta de novo nas próximas junções...
FALHA_DESISTE_H = 24    # ...e só é dado por ruim depois de 10 tentativas E 24 horas (tempo de sobra para a sincronização)


def _ignorar(banco, inst, seq, caminho, motivo, aviso=None):
    if aviso:
        aviso(f"  Arquivo de outro computador ignorado ({os.path.basename(caminho)}: {motivo}).")
    banco.registrar("saude", {"fonte": "Troca entre computadores", "situacao": "atenção",
                              "detalhe": f"arquivo ignorado: {os.path.basename(caminho)} ({motivo})"[:200]})
    banco.con.execute("INSERT OR IGNORE INTO troca_lidos (instalacao, seq, ignorado) VALUES (?,?,1)", (inst, seq))
    banco.con.execute("DELETE FROM troca_falhas WHERE instalacao = ? AND seq = ?", (inst, seq))
    banco.con.commit()


def _aplicar_pendentes(banco, apagados):
    """Itens que chegaram antes do processo (situação, valor ou contato de um processo que este computador ainda não tinha)."""
    con, n = banco.con, 0
    for rowid, proc, item, origem in con.execute("SELECT rowid, processo, item, origem FROM troca_pendentes WHERE processo IN "
                                                 "(SELECT processo FROM leads)").fetchall():
        try:
            n += _aplicar(banco, json.loads(item), apagados, origem or "")
        except Exception:  # noqa: BLE001
            pass
        con.execute("DELETE FROM troca_pendentes WHERE rowid = ?", (rowid,))
    con.commit()
    return n


def _tem_tabela(con, nome):
    return bool(con.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (nome,)).fetchone())


def _aplicar(banco, item, apagados, origem):
    from . import banco as _bd
    con, t, proc = banco.con, item.get("t"), str(item.get("p") or item.get("processo") or "")
    if not proc or proc in apagados:
        return 0
    existe = con.execute("SELECT status, status_em FROM leads WHERE processo = ?", (proc,)).fetchone()
    if t == "lead":
        if existe:
            return 0
        d = dict(item.get("d") or {}, processo=proc)
        if not d.get("tribunal"):
            return 0
        banco.guardar_lead(d, str(d.get("data_publicacao") or "")[:10] or None)
        return 1
    if not existe:  # processo que este computador ainda não tem: guarda o item e aplica quando o processo chegar
        if con.execute("SELECT count(*) FROM troca_pendentes").fetchone()[0] < MAX_PENDENTES:
            con.execute("INSERT INTO troca_pendentes VALUES (?,?,?)", (proc, json.dumps(item, ensure_ascii=False), origem[:120]))
        return 0
    if t == "sit":
        st, em = _bd.situacao_valida(item.get("s")) or "novo", str(item.get("q") or "")
        atual, atual_em = existe[0] or "novo", existe[1] or ""
        vp, vq = str(item.get("vp") or "")[:120], str(item.get("vq") or "")
        if vp:  # quem viu vale sempre (é informação, não situação)
            con.execute("UPDATE leads SET visto_por = ?, visto_em = ? WHERE processo = ? AND (coalesce(visto_em, '') < ?)", (vp, vq, proc, vq))
        if st == atual:
            return 0
        leves = ("novo", "visto")
        if st in leves and atual not in leves:  # "Visto" (ou "Novo") nunca passa por cima de uma situação trabalhada
            return 0
        # situação trabalhada vence "Novo"/"Visto" mesmo se marcada antes; entre as demais, vale a mais recente. Assim os dois
        # computadores terminam iguais, qualquer que seja a ordem em que os arquivos chegam
        if not (atual in leves and st not in leves) and em <= atual_em:
            return 0
        con.execute("UPDATE leads SET status = ?, motivo = ?, status_em = ?, status_por = ? WHERE processo = ?",
                    (st, str(item.get("m") or "")[:80], em, str(item.get("por") or "")[:120], proc))
        banco.registrar_acao(str(item.get("por") or origem)[:120], "situacao:troca", proc, atual, st, 1)
        return 1
    if t == "campo":
        r = banco.completar_fonte(proc, item.get("c"), item.get("v"), item.get("f") or "outro computador", item.get("dt") or "",
                                  perfil=origem)
        return 1 if r[0] in ("acrescentado", "alterado") else 0
    if t == "contato":
        c = {k: item.get(k) or "" for k in ("processo", "empresa", "canal", "valor", "fonte", "data", "confianca", "origem",
                                            "observacao", "criado_em", "incluido_por", "computador")}
        c["processo"], c["de_pessoa"] = proc, bool(item.get("de_pessoa"))
        if not c["canal"] or not c["valor"]:
            return 0
        c["incluido_por"] = c["incluido_por"] or origem
        return 1 if banco.guardar_contato(c) else 0
    return 0


# --- Trava curta e vetor da planilha ------------------------------------------------------------------------------------

@contextlib.contextmanager
def trava(cfg, agora=None):
    """Só um computador junta e grava a planilha por vez (segundos). Trava vencida (2 min) é tomada. Dá `None` se ocupada
    (e quem está com ela), senão o caminho da trava."""
    raiz = pasta(cfg)
    if not raiz:
        yield "sem pasta"
        return
    caminho, meu = os.path.join(raiz, "gravando.trava"), {"instalacao": instalacao(cfg), "quem": quem(cfg),
                                                           "quando": (agora or dt.datetime.now(dt.timezone.utc)).timestamp()}
    pegou = False
    try:
        os.makedirs(raiz, exist_ok=True)
    except OSError:  # revisão: pasta de rede ou Drive fora do ar: segue sem trava (a gravação avisa como antes)
        yield "sem pasta"
        return
    for _ in range(2):
        try:
            fd = os.open(caminho, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(meu, f)
            pegou = True
            break
        except FileExistsError:
            try:
                with open(caminho, encoding="utf-8") as f:
                    outro = json.load(f)
            except (OSError, ValueError):
                outro = {"quando": 0}
            if meu["quando"] - float(outro.get("quando") or 0) > TRAVA_SEG:
                with contextlib.suppress(OSError):
                    os.remove(caminho)  # vencida: o outro caiu no meio
                continue
            break
        except OSError:  # sem permissão ou pasta caiu agora: segue sem trava
            yield "sem pasta"
            return
    if pegou:  # revisão: dois tomando a mesma trava vencida ao mesmo tempo; confere depois de um instante se ainda é a nossa
        time.sleep(0.05)
        try:
            with open(caminho, encoding="utf-8") as f:
                pegou = json.load(f).get("quando") == meu["quando"]
        except (OSError, ValueError):
            pegou = False
    try:
        yield caminho if pegou else None
    finally:
        if pegou:
            with contextlib.suppress(OSError, ValueError):
                with open(caminho, encoding="utf-8") as f:
                    dono = json.load(f)
                if dono.get("instalacao") == meu["instalacao"] and dono.get("quando") == meu["quando"]:
                    os.remove(caminho)


def _meus_numeros(cfg):
    raiz = pasta(cfg)
    try:
        return [int(m.group(1)) for m in (_NOME.match(n) for n in os.listdir(os.path.join(raiz, "troca", instalacao(cfg)))) if m]
    except OSError:
        return []


def vetor(banco, cfg):
    """O que esta planilha vai conter de cada computador: {instalação: seq}."""
    _tabela(banco.con)
    v = {instalacao(cfg): max([int(_ler(banco.con, "seq", "0"))] + _meus_numeros(cfg))}  # revisão: banco recriado não fica "atrasado"
    por = {}
    for inst, seq in banco.con.execute("SELECT instalacao, seq FROM troca_lidos"):
        por.setdefault(inst, set()).add(seq)
    for inst, seqs in por.items():  # até onde está tudo lido, sem buraco (arquivo que ainda não chegou não conta)
        n = 0
        while n + 1 in seqs:
            n += 1
        v[inst] = n
    return v


def atrasado(banco, cfg, vetor_planilha):
    """Instalações das quais a planilha já tem mais do que este computador juntou (gravar agora a faria voltar atrás)."""
    meu = vetor(banco, cfg)
    return sorted(i for i, s in (vetor_planilha or {}).items() if int(s or 0) > meu.get(i, 0))
