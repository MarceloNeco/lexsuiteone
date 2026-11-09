"""Memória do robô (SQLite, um arquivo só: lexsuite.db).

Serve para: não avisar duas vezes o mesmo processo, guardar o andamento do
lead (novo, em análise, abordado, descartado) e não consultar o mesmo CNPJ
toda hora. Na fase SaaS, as mesmas tabelas vão para o banco da plataforma.
"""

import datetime as dt
import json
import os
import sqlite3

# 0.7.13: situações do processo para o escritório (decisão do dono, 09/Nov). A chave fica no banco; o texto, na tela.
SITUACOES = ("novo", "visto", "analise", "contato", "cliente", "descartado", "arquivado")
_SITUACAO_ANTIGA = {"novo": "novo", "nova": "novo", "visto": "visto", "lido": "visto", "em analise": "analise",
                    "em análise": "analise", "analise": "analise", "abordado": "contato", "em contato": "contato",
                    "contato": "contato", "cliente": "cliente", "virou cliente": "cliente", "contratado": "cliente",
                    "descartado": "descartado", "arquivado": "arquivado", "tratado": "arquivado"}
# Faixas de valor das Estatísticas e do filtro (limite superior aberto); "sem" = o Diário não trouxe o valor.
FAIXAS = ((10000, "ate10k"), (50000, "10k-50k"), (100000, "50k-100k"), (300000, "100k-300k"), (500000, "300k-500k"),
          (1000000, "500k-1mi"), (float("inf"), "1mi+"))
# O que fica de cada ação depois que o dado completo é limpo (sem o trecho do Diário, onde aparece o reclamante).
_RESUMO = ("processo", "tribunal", "vara", "classe", "rito", "data_publicacao", "ajuizada_em", "empresas", "cnpjs",
           "valor_causa", "fonte", "link", "visto_em", "rodada", "cnpj_a_conferir")
_RESUMO_RECEITA = ("cnpj", "razao_social", "nome_fantasia", "porte", "capital_social", "cnae", "atividade", "municipio",
                   "uf", "telefone", "telefone2", "email", "logradouro", "numero", "complemento", "bairro", "cep",
                   "situacao", "inicio_atividade", "simples", "socios", "consultado_em")


def situacao_valida(s):
    return _SITUACAO_ANTIGA.get(str(s or "").strip().lower(), "")


def faixa_valor(v):
    try:
        v = float(v)
    except (TypeError, ValueError):
        return "sem"
    if v <= 0:
        return "sem"
    for teto, nome in FAIXAS:
        if v < teto:
            return nome
    return "1mi+"


def agora_utc_e_fuso():
    """(quando em UTC, fuso do computador como '-03:00') para o registro de quem fez o quê."""
    agora = dt.datetime.now(dt.timezone.utc)
    off = dt.datetime.now().astimezone().utcoffset() or dt.timedelta(0)
    m = int(off.total_seconds() // 60)
    return agora.isoformat(timespec="seconds"), f"{'+' if m >= 0 else '-'}{abs(m) // 60:02d}:{abs(m) % 60:02d}"


class Banco:
    def __init__(self, caminho="lexsuite.db"):
        self.con = sqlite3.connect(caminho)
        self.con.executescript("""
            CREATE TABLE IF NOT EXISTS leads (
                processo TEXT PRIMARY KEY, primeira_vez TEXT, tribunal TEXT, vara TEXT,
                dados TEXT, status TEXT DEFAULT 'Novo');
            CREATE TABLE IF NOT EXISTS cnpj (cnpj TEXT PRIMARY KEY, quando TEXT, dados TEXT);
            CREATE TABLE IF NOT EXISTS execucoes (quando TEXT, tipo TEXT, resumo TEXT);
            CREATE TABLE IF NOT EXISTS publicacoes (
                chave TEXT PRIMARY KEY, visto_em TEXT, data TEXT, processo TEXT,
                dados TEXT, status TEXT DEFAULT 'Nova');
            CREATE TABLE IF NOT EXISTS cadernos (tribunal TEXT, data TEXT, versao TEXT, quando TEXT,
                PRIMARY KEY (tribunal, data));
            CREATE TABLE IF NOT EXISTS rodadas (id TEXT PRIMARY KEY, quando TEXT, modo TEXT,
                conferidas INTEGER, novas_processos INTEGER, novas_acoes INTEGER, detalhes TEXT);
            CREATE TABLE IF NOT EXISTS acoes (quando_utc TEXT, fuso TEXT, perfil TEXT, acao TEXT, alvo TEXT,
                antes TEXT, depois TEXT, quantos INTEGER);
            CREATE TABLE IF NOT EXISTS contatos (id INTEGER PRIMARY KEY AUTOINCREMENT, processo TEXT, empresa TEXT,
                canal TEXT, valor TEXT, de_pessoa INTEGER DEFAULT 0, fonte TEXT, data TEXT, confianca TEXT, origem TEXT,
                observacao TEXT, arquivo TEXT, validacao TEXT DEFAULT '', validado_por TEXT DEFAULT '',
                validado_em TEXT DEFAULT '', criado_em TEXT, UNIQUE (processo, canal, valor));
            CREATE TABLE IF NOT EXISTS contatos_historico (quando_utc TEXT, fuso TEXT, perfil TEXT, arquivo TEXT,
                aceitas INTEGER, recusadas INTEGER, detalhe TEXT);
            CREATE TABLE IF NOT EXISTS estatisticas_diarias (data TEXT, tribunal TEXT, vara TEXT, frente TEXT,
                porte TEXT, faixa_valor TEXT, novas INTEGER DEFAULT 0, encerradas INTEGER DEFAULT 0, atualizado_em TEXT,
                PRIMARY KEY (data, tribunal, vara, frente, porte, faixa_valor));
        """)
        colunas = {r[1] for r in self.con.execute("PRAGMA table_info(leads)")}
        for nome, tipo in (("frente", "TEXT DEFAULT ''"), ("motivo", "TEXT DEFAULT ''"), ("status_em", "TEXT DEFAULT ''"),
                           ("bruto_limpo", "INTEGER DEFAULT 0"), ("data", "TEXT DEFAULT ''"), ("porte", "TEXT DEFAULT ''"),
                           ("faixa_valor", "TEXT DEFAULT ''")):
            if nome not in colunas:
                self.con.execute(f"ALTER TABLE leads ADD COLUMN {nome} {tipo}")  # nosec B608 - nomes fixos acima
        # Situações antigas (Novo, Visto, Em contato, Descartado) passam para as chaves novas, uma vez.
        for antigo, novo in _SITUACAO_ANTIGA.items():
            self.con.execute("UPDATE leads SET status = ? WHERE lower(status) = ? AND status <> ?", (novo, antigo, novo))
        self.con.execute("UPDATE leads SET status = 'novo' WHERE status IS NULL OR status = ''")
        self._preencher_resumo()
        self.con.commit()
        self.caminho = caminho

    def _preencher_resumo(self):
        """Ações guardadas antes da 0.7.13: preenche data, frente, porte e faixa de valor (uma vez)."""
        from . import frentes
        faltam = self.con.execute("SELECT processo, dados, primeira_vez FROM leads WHERE data = '' OR data IS NULL").fetchall()
        for proc, dados, quando in faltam:
            try:
                d = json.loads(dados or "{}")
            except ValueError:
                d = {}
            emp = d.get("empresa_receita") or {}
            self.con.execute("UPDATE leads SET data = ?, frente = ?, porte = ?, faixa_valor = ? WHERE processo = ?",
                             ((d.get("data_publicacao") or quando or "")[:10], frentes.frente(d), emp.get("porte") or "",
                              faixa_valor(d.get("valor_causa")), proc))

    def processos_vistos(self):
        return {r[0] for r in self.con.execute("SELECT processo FROM leads")}

    def guardar_lead(self, lead, primeira_vez=None):
        from . import frentes
        quando = primeira_vez or dt.date.today().isoformat()
        emp = lead.get("empresa_receita") or {}
        self.con.execute(
            "INSERT OR IGNORE INTO leads (processo, primeira_vez, tribunal, vara, dados, status, frente, data, porte, faixa_valor) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            (lead["processo"], quando, lead.get("tribunal"), lead.get("vara"), json.dumps(lead, ensure_ascii=False), "novo",
             frentes.frente(lead), (lead.get("data_publicacao") or quando)[:10], emp.get("porte") or "",
             faixa_valor(lead.get("valor_causa"))))
        self.con.commit()

    # --- Situação do processo (0.7.13) ---

    def mudar_situacao(self, processos, situacao, perfil="", motivo=""):
        """Muda a situação de um ou muitos processos. Devolve {quantos, antes: {processo: situação}} (para desfazer).
        Registra quem, quando (UTC e fuso), o quê e quantos na tabela `acoes`."""
        situacao = situacao_valida(situacao)
        if not situacao:
            raise ValueError("Situação desconhecida.")
        processos = [str(p) for p in (processos or []) if p][:20000]
        antes = {}
        for i in range(0, len(processos), 500):
            parte = processos[i:i + 500]
            marcas = ",".join("?" * len(parte))
            for proc, st in self.con.execute(f"SELECT processo, status FROM leads WHERE processo IN ({marcas})", parte):  # nosec B608
                antes[proc] = st or "novo"
        quando, fuso = agora_utc_e_fuso()
        self.con.executemany("UPDATE leads SET status = ?, motivo = ?, status_em = ? WHERE processo = ?",
                             [(situacao, (motivo or "")[:80] if situacao in ("descartado", "arquivado") else "", quando, p) for p in antes])
        self.registrar_acao(perfil, "situacao", ",".join(list(antes)[:50]), json.dumps(_contar(antes.values())), situacao, len(antes))
        self.con.commit()
        return {"quantos": len(antes), "antes": antes}

    def desfazer_situacao(self, antes, perfil=""):
        """Volta cada processo para a situação que tinha (o 'antes' devolvido por mudar_situacao)."""
        quando, fuso = agora_utc_e_fuso()
        pares = [(situacao_valida(st) or "novo", quando, str(p)) for p, st in (antes or {}).items()][:20000]
        self.con.executemany("UPDATE leads SET status = ?, status_em = ? WHERE processo = ?", pares)
        self.registrar_acao(perfil, "desfazer", "", "", json.dumps(_contar(st for st, _, _ in pares)), len(pares))
        self.con.commit()
        return len(pares)

    def registrar_acao(self, perfil, acao, alvo, antes, depois, quantos):
        quando, fuso = agora_utc_e_fuso()
        self.con.execute("INSERT INTO acoes VALUES (?,?,?,?,?,?,?,?)",
                         (quando, fuso, (perfil or "")[:120], acao, (alvo or "")[:2000], antes or "", depois or "", int(quantos or 0)))

    def acoes(self, limite=500):
        cols = ("quando_utc", "fuso", "perfil", "acao", "alvo", "antes", "depois", "quantos")
        return [dict(zip(cols, r)) for r in self.con.execute("SELECT * FROM acoes ORDER BY quando_utc DESC LIMIT ?", (int(limite),))]

    def totais_por_situacao(self):
        return dict(self.con.execute("SELECT status, count(*) FROM leads GROUP BY status").fetchall())

    # --- Estatísticas que não se apagam ---

    def atualizar_estatisticas(self):
        """Recalcula os totais dos dias que ainda estão no Arquivo e guarda em `estatisticas_diarias`. Os dias que já não
        estão no Arquivo ficam como estavam (a tabela nunca é apagada pela limpeza)."""
        quando = dt.datetime.now().isoformat(timespec="seconds")
        linhas = self.con.execute(
            "SELECT data, coalesce(tribunal,''), coalesce(vara,''), coalesce(frente,''), coalesce(porte,''), "
            "coalesce(faixa_valor,''), count(*) FROM leads WHERE data <> '' GROUP BY 1,2,3,4,5,6").fetchall()
        dias = sorted({l[0] for l in linhas})
        for d in dias:
            self.con.execute("DELETE FROM estatisticas_diarias WHERE data = ?", (d,))
        self.con.executemany("INSERT OR REPLACE INTO estatisticas_diarias VALUES (?,?,?,?,?,?,?,0,?)",
                             [l + (quando,) for l in linhas])
        self.con.commit()
        return len(linhas)

    def estatisticas(self, desde=None):
        cols = ("data", "tribunal", "vara", "frente", "porte", "faixa_valor", "novas", "encerradas")
        sql, args = "SELECT data, tribunal, vara, frente, porte, faixa_valor, novas, encerradas FROM estatisticas_diarias", ()
        if desde:
            sql, args = sql + " WHERE data >= ?", (desde,)
        return [dict(zip(cols, r)) for r in self.con.execute(sql + " ORDER BY data", args)]

    # --- Espaço e limpeza do dado completo ---

    def espaco(self):
        try:
            tamanho = os.path.getsize(self.caminho) if self.caminho and os.path.exists(self.caminho) else 0
        except OSError:
            tamanho = 0
        r = self.con.execute("SELECT count(*), sum(CASE WHEN bruto_limpo = 0 THEN 1 ELSE 0 END), min(data), max(data) FROM leads").fetchone()
        return {"bytes": tamanho, "acoes": r[0] or 0, "com_detalhe": r[1] or 0, "desde": r[2] or "", "ate": r[3] or "",
                "estatisticas_dias": self.con.execute("SELECT count(DISTINCT data) FROM estatisticas_diarias").fetchone()[0] or 0}

    def limpar_detalhe(self, meses=12, perfil=""):
        """Apaga só o dado completo (trecho do Diário etc.) das ações mais velhas que `meses`; fica o resumo e as
        estatísticas. Devolve quantas ações foram resumidas."""
        meses = int(meses or 0)
        if meses <= 0:
            return 0
        self.atualizar_estatisticas()
        limite = (dt.date.today() - dt.timedelta(days=round(meses * 30.44))).isoformat()
        feitas = 0
        for proc, dados in self.con.execute("SELECT processo, dados FROM leads WHERE bruto_limpo = 0 AND primeira_vez < ?", (limite,)).fetchall():
            try:
                d = json.loads(dados or "{}")
            except ValueError:
                d = {}
            r = {k: d[k] for k in _RESUMO if k in d}
            if isinstance(d.get("empresa_receita"), dict):
                r["empresa_receita"] = {k: d["empresa_receita"][k] for k in _RESUMO_RECEITA if k in d["empresa_receita"]}
            self.con.execute("UPDATE leads SET dados = ?, bruto_limpo = 1 WHERE processo = ?", (json.dumps(r, ensure_ascii=False), proc))
            feitas += 1
        if feitas:
            self.registrar_acao(perfil, "limpeza", f"mais de {meses} meses", "", "", feitas)
        self.con.commit()
        return feitas

    def compactar(self):
        self.con.commit()
        self.con.execute("VACUUM")

    def todos_leads(self, vara=None, desde=None):
        sql, args = "SELECT dados, status, primeira_vez, motivo, frente, bruto_limpo, status_em FROM leads WHERE 1=1", ()
        if vara:
            sql, args = sql + " AND vara = ?", args + (vara,)
        if desde:
            sql, args = sql + " AND primeira_vez >= ?", args + (desde,)
        saida = []
        for dados, status, quando, motivo, frente, limpo, status_em in self.con.execute(sql + " ORDER BY primeira_vez DESC", args):
            lead = json.loads(dados)
            lead["status"], lead["primeira_vez"] = situacao_valida(status) or "novo", quando
            lead["motivo"], lead["frente"], lead["resumido"], lead["status_em"] = motivo or "", frente or "", bool(limpo), status_em or ""
            saida.append(lead)
        return saida

    def cnpj_em_cache(self, cnpj, validade_dias):
        r = self.con.execute("SELECT quando, dados FROM cnpj WHERE cnpj = ?", (cnpj,)).fetchone()
        if r and (dt.date.today() - dt.date.fromisoformat(r[0])).days <= validade_dias:
            return json.loads(r[1])
        return None

    def guardar_cnpj(self, cnpj, dados):
        self.con.execute("INSERT OR REPLACE INTO cnpj VALUES (?,?,?)",
                         (cnpj, dt.date.today().isoformat(), json.dumps(dados, ensure_ascii=False)))
        self.con.commit()

    def registrar(self, tipo, resumo):
        self.con.execute("INSERT INTO execucoes VALUES (?,?,?)",
                         (dt.datetime.now().isoformat(timespec="seconds"), tipo, json.dumps(resumo, ensure_ascii=False)))
        self.con.commit()

    def limpar_antigos(self, dias=365):
        """Retenção: publicações do monitor e execuções mais velhas que `dias` são apagadas. As ações do Radar não são
        apagadas (0.7.13): o dado completo vira resumo (limpar_detalhe) e as estatísticas ficam para sempre."""
        if not dias or int(dias) <= 0:
            return 0
        limite = (dt.date.today() - dt.timedelta(days=int(dias))).isoformat()
        total = self.limpar_detalhe(max(1, round(int(dias) / 30.44)))
        for sql in ("DELETE FROM publicacoes WHERE visto_em < ?", "DELETE FROM execucoes WHERE quando < ?"):
            total += self.con.execute(sql, (limite,)).rowcount
        self.con.commit()
        return total

    def execucoes(self, tipo=None, limite=500):
        """As últimas execuções registradas (mais recentes primeiro): [{quando, tipo, ...resumo}]."""
        sql, args = "SELECT quando, tipo, resumo FROM execucoes", ()
        if tipo:
            sql, args = sql + " WHERE tipo = ?", (tipo,)
        saida = []
        for quando, t, resumo in self.con.execute(sql + " ORDER BY quando DESC LIMIT ?", args + (int(limite),)):
            try:
                dados = json.loads(resumo or "{}")
            except ValueError:
                dados = {"texto": resumo}
            saida.append({"quando": quando, "tipo": t, **(dados if isinstance(dados, dict) else {"dados": dados})})
        return saida

    # --- Monitor (acompanhamento dos processos do escritório) ---

    def publicacao_vista(self, chave):
        return self.con.execute("SELECT 1 FROM publicacoes WHERE chave = ?", (chave,)).fetchone() is not None

    def guardar_publicacao(self, chave, pub, visto_em=None):
        self.con.execute(
            "INSERT OR IGNORE INTO publicacoes (chave, visto_em, data, processo, dados) VALUES (?,?,?,?,?)",
            (chave, visto_em or dt.datetime.now().isoformat(timespec="seconds"), pub.get("data"), pub.get("processo"),
             json.dumps(pub, ensure_ascii=False)))
        self.con.commit()

    def publicacoes(self, limite=1000):
        saida = []
        for dados, status, visto in self.con.execute(
                "SELECT dados, status, visto_em FROM publicacoes ORDER BY data DESC, visto_em DESC LIMIT ?", (limite,)):
            pub = json.loads(dados)
            pub["status"], pub["visto_em"] = status, visto
            saida.append(pub)
        return saida

    def versao_caderno(self, tribunal, data):
        r = self.con.execute("SELECT versao FROM cadernos WHERE tribunal = ? AND data = ?", (tribunal, data)).fetchone()
        return r[0] if r else None

    def guardar_caderno(self, tribunal, data, versao):
        self.con.execute("INSERT OR REPLACE INTO cadernos VALUES (?,?,?,?)",
                         (tribunal, data, str(versao), dt.datetime.now().isoformat(timespec="seconds")))
        self.con.commit()

    # --- Rodadas (cada vez que o monitor roda) ---

    def registrar_rodada(self, rodada):
        self.con.execute(
            "INSERT OR REPLACE INTO rodadas VALUES (?,?,?,?,?,?,?)",
            (rodada["id"], rodada["quando"], rodada.get("modo", ""), int(rodada.get("conferidas") or 0),
             int(rodada.get("novas_processos") or 0), int(rodada.get("novas_acoes") or 0),
             json.dumps(rodada.get("detalhes") or {}, ensure_ascii=False)))
        self.con.commit()

    def rodadas(self, desde=None, limite=200):
        sql, args = "SELECT id, quando, modo, conferidas, novas_processos, novas_acoes, detalhes FROM rodadas", ()
        if desde:
            sql, args = sql + " WHERE quando >= ?", (desde,)
        saida = []
        for r in self.con.execute(sql + " ORDER BY quando DESC LIMIT ?", args + (limite,)):
            saida.append({"id": r[0], "quando": r[1], "modo": r[2], "conferidas": r[3], "novas_processos": r[4],
                          "novas_acoes": r[5], "detalhes": json.loads(r[6] or "{}")})
        return saida

    def publicacoes_desde(self, desde):
        return [p for p in self.publicacoes(5000) if (p.get("visto_em") or "") >= desde]


def _contar(valores):
    c = {}
    for v in valores:
        c[v] = c.get(v, 0) + 1
    return c
