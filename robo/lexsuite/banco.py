"""Memória do robô (SQLite, um arquivo só: lexsuite.db).

Serve para: não avisar duas vezes o mesmo processo, guardar o andamento do
lead (novo, em análise, abordado, descartado) e não consultar o mesmo CNPJ
toda hora. Na fase SaaS, as mesmas tabelas vão para o banco da plataforma.
"""

import datetime as dt
import json
import sqlite3


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
        """)

    def processos_vistos(self):
        return {r[0] for r in self.con.execute("SELECT processo FROM leads")}

    def guardar_lead(self, lead, primeira_vez=None):
        self.con.execute(
            "INSERT OR IGNORE INTO leads (processo, primeira_vez, tribunal, vara, dados) VALUES (?,?,?,?,?)",
            (lead["processo"], primeira_vez or dt.date.today().isoformat(), lead.get("tribunal"), lead.get("vara"),
             json.dumps(lead, ensure_ascii=False)))
        self.con.commit()

    def todos_leads(self, vara=None, desde=None):
        sql, args = "SELECT dados, status, primeira_vez FROM leads WHERE 1=1", ()
        if vara:
            sql, args = sql + " AND vara = ?", args + (vara,)
        if desde:
            sql, args = sql + " AND primeira_vez >= ?", args + (desde,)
        saida = []
        for dados, status, quando in self.con.execute(sql + " ORDER BY primeira_vez DESC", args):
            lead = json.loads(dados)
            lead["status"], lead["primeira_vez"] = status, quando
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
        """Retenção: apaga ações, publicações e execuções mais velhas que `dias` (LGPD: não acumular texto sem necessidade)."""
        if not dias or int(dias) <= 0:
            return 0
        limite = (dt.date.today() - dt.timedelta(days=int(dias))).isoformat()
        total = 0
        for sql in ("DELETE FROM leads WHERE primeira_vez < ?", "DELETE FROM publicacoes WHERE visto_em < ?",
                    "DELETE FROM execucoes WHERE quando < ?"):
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
