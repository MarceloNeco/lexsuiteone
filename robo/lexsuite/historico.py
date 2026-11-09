"""Estatísticas dos meses anteriores (0.7.18; itens 79 e 82; decisões 10 a 14 do dono, 09/Nov).

O escritório pede "estatísticas de N meses para trás" (padrão 3, ajustável) nos tribunais marcados. O RADAR lê os
Diários antigos aos poucos (30 por vez, com pausa entre eles), à noite depois da leitura agendada ou quando o escritório
clica em "Ler agora", e guarda os totais por dia, tribunal, vara, frente e faixa de valor em `estatisticas_diarias` e,
só neste computador, o número dos processos já contados (`historico_processos`, para não contar duas vezes). Não entra
nada na Lista, no Arquivo nem na planilha, e nada disso vai à SolverONE.
Se o CNJ não entregar um Diário antigo, o dia fica marcado "sem Diário" e a fila segue.
"""

import datetime as dt
import time

from . import djen, frentes

POR_VEZ = 30
PAUSA_S = 2.0
MESES_PADRAO = 3


def _dias_uteis_entre(inicio, fim):
    d, saida = fim, []
    while d >= inicio:
        if d.weekday() < 5:
            saida.append(d)
        d -= dt.timedelta(days=1)
    return saida  # do mais novo para o mais antigo


def pedir(banco, meses, tribunais, hoje=None, perfil=""):
    """Monta a fila: dias úteis de `meses` para trás, até ontem, em cada tribunal, menos os já lidos (pela leitura
    normal ou por esta). Devolve quantos Diários entraram na fila."""
    hoje = hoje or dt.date.today()
    meses = max(1, min(24, int(meses or MESES_PADRAO)))
    inicio = hoje - dt.timedelta(days=round(meses * 30.44))
    tribs = [str(t).upper() for t in tribunais or []]
    ja = {(t, d) for t, d in banco.con.execute("SELECT tribunal, data FROM historico")}
    ja |= {(t or "", d) for t, d in banco.con.execute("SELECT DISTINCT tribunal, data FROM leads WHERE data <> ''")}
    novos = []
    for d in _dias_uteis_entre(inicio, hoje - dt.timedelta(days=1)):
        for t in tribs:
            if (t, d.isoformat()) not in ja:
                novos.append((t, d.isoformat(), "fila", 0, ""))
    banco.con.executemany("INSERT OR IGNORE INTO historico VALUES (?,?,?,?,?)", novos)
    banco.registrar_acao(perfil, "estatisticas:pedir", ", ".join(tribs), "", f"{meses} meses", len(novos))
    banco.con.commit()
    banco.registrar("historico_pedido", {"meses": meses, "tribunais": tribs, "desde": inicio.isoformat(), "na_fila": len(novos)})
    return len(novos)


def situacao(banco):
    """{na_fila, lidos, sem_diario, erros, novas, desde, ate, pedido} para a tela."""
    r = dict(banco.con.execute("SELECT situacao, count(*) FROM historico GROUP BY situacao").fetchall())
    novas = banco.con.execute("SELECT coalesce(sum(novas), 0) FROM historico").fetchone()[0]
    faixa = banco.con.execute("SELECT min(data), max(data) FROM historico WHERE situacao = 'lido'").fetchone()
    ped = banco.execucoes("historico_pedido", 1)
    return {"na_fila": r.get("fila", 0) + r.get("lendo", 0), "lidos": r.get("lido", 0), "sem_diario": r.get("sem_diario", 0),
            "erros": r.get("erro", 0), "novas": int(novas or 0), "desde": faixa[0] or "", "ate": faixa[1] or "",
            "pedido": ped[0] if ped else {}}


def _ano_minimo(data):
    d = dt.date.fromisoformat(data)
    return d.year - 1 if d.month <= 2 else d.year


def _somar(banco, tribunal, data, novos):
    """Soma as ações novas do dia em estatisticas_diarias (o número dos processos fica só em historico_processos)."""
    from .banco import faixa_valor
    contagem = {}
    for n in novos:
        chave = (data, tribunal, n.get("vara") or "", frentes.frente(n), "", faixa_valor(n.get("valor_causa")))
        contagem[chave] = contagem.get(chave, 0) + 1
    quando = dt.datetime.now().isoformat(timespec="seconds")
    for chave, qtd in contagem.items():
        banco.con.execute("INSERT INTO estatisticas_diarias VALUES (?,?,?,?,?,?,?,0,?) ON CONFLICT(data, tribunal, vara, frente, porte, "
                          "faixa_valor) DO UPDATE SET novas = novas + excluded.novas, atualizado_em = excluded.atualizado_em",
                          chave + (qtd, quando))


def _causa(e):
    """(causa, {pt, en}) de uma falha ao baixar um Diário antigo. 403 que não é o das 3h vale como site fora (0.7.19)."""
    from . import causas
    causa = causas.classificar(e)
    if causa == "erro_do_programa" and any(c in str(e) for c in ("HTTP 403", "HTTP 429", "HTTP 5")):
        causa = "governo_fora"
    return causa, {"pt": causas.mensagem(causa), "en": causas.mensagem(causa, "en")}


def processar(banco, limite=None, aviso=print, parar=None, pausa=PAUSA_S, andamento=None):
    """Lê até `limite` Diários da fila (do mais novo para o mais antigo). Devolve {lidos, sem_diario, erros, novas, parou?}.
    0.7.19 (revisão da Operação): cada Diário é reservado ("lendo") antes de ler, para dois leitores nunca contarem o
    mesmo Diário; reservas com mais de 1 hora voltam para a fila; site fora do ar para a fila só depois de 3 Diários
    diferentes seguidos falharem (o que falhou vai para "erro" e volta na próxima rodada)."""
    limite = int(limite or POR_VEZ)
    feitos = {"lidos": 0, "sem_diario": 0, "erros": 0, "novas": 0}
    agora_ = dt.datetime.now()
    banco.con.execute("UPDATE historico SET situacao = 'fila' WHERE situacao = 'lendo' AND (quando IS NULL OR quando < ?)",
                      ((agora_ - dt.timedelta(hours=1)).isoformat(timespec="seconds"),))
    tentar_de_novo_os_erros(banco)  # o que deu erro volta para a fila a cada nova rodada
    fila = banco.con.execute("SELECT tribunal, data FROM historico WHERE situacao = 'fila' ORDER BY data DESC, tribunal LIMIT ?",
                             (limite,)).fetchall()
    vistos = banco.processos_vistos() | {p for (p,) in banco.con.execute("SELECT processo FROM historico_processos")}
    falhas_seguidas = 0
    for k, (trib, data) in enumerate(fila, 1):
        if parar and parar():
            aviso("  Estatísticas antigas: parada a pedido; o resto fica na fila. / Stopped on request; the rest stays queued.")
            break
        quando = dt.datetime.now().isoformat(timespec="seconds")
        r = banco.con.execute("UPDATE historico SET situacao = 'lendo', quando = ? WHERE tribunal = ? AND data = ? AND situacao = 'fila'",
                              (quando, trib, data))
        banco.con.commit()
        if r.rowcount == 0:  # outro leitor já pegou este Diário
            continue
        if andamento:
            andamento(k, len(fila), trib, data)
        try:
            meta = djen.meta_caderno(trib, data, lambda *_: None)
            if meta is None:
                banco.con.execute("UPDATE historico SET situacao = 'sem_diario', quando = ? WHERE tribunal = ? AND data = ?", (quando, trib, data))
                feitos["sem_diario"] += 1
            else:
                aviso(f"  Estatísticas antigas: Diário {trib} {data}...")
                pubs = djen.baixar_caderno(trib, data, None, lambda *_: None, meta=meta) or []
                novos = [n for n in djen.leads(pubs, ano_minimo=_ano_minimo(data), ja_vistos=vistos) if n.get("sinal_de_acao_nova")]
                for n in novos:
                    vistos.add(n["processo"])
                banco.con.executemany("INSERT OR IGNORE INTO historico_processos VALUES (?)", [(n["processo"],) for n in novos])
                _somar(banco, trib, data, novos)
                banco.con.execute("UPDATE historico SET situacao = 'lido', novas = ?, quando = ? WHERE tribunal = ? AND data = ?",
                                  (len(novos), quando, trib, data))
                feitos["lidos"] += 1
                feitos["novas"] += len(novos)
            falhas_seguidas = 0
        except Exception as e:  # noqa: BLE001 - um Diário com problema não para a fila
            if e.__class__.__name__ == "BloqueadoForaDoBrasil":
                banco.con.execute("UPDATE historico SET situacao = 'fila' WHERE tribunal = ? AND data = ?", (trib, data))
                banco.con.commit()
                raise
            causa, msg = _causa(e)
            banco.con.execute("UPDATE historico SET situacao = 'erro', quando = ? WHERE tribunal = ? AND data = ?", (quando, trib, data))
            feitos["erros"] += 1
            falhas_seguidas += 1
            if causa in ("governo_fora", "sem_internet", "ainda_nao_liberado_3h") and falhas_seguidas >= 3:
                feitos["parou"] = msg
                aviso(f"  Estatísticas antigas: parei ({msg['pt']}). O resto fica na fila para a próxima vez. / Stopped ({msg['en']}).")
                banco.con.commit()
                break
            aviso(f"  Estatísticas antigas: {trib} {data} não deu certo ({e.__class__.__name__}); tento de novo na próxima vez. "
                  f"/ Will retry next time.")
        banco.con.commit()
        if pausa and k < len(fila):
            time.sleep(pausa)
    if fila:
        aviso(f"  Estatísticas antigas: {feitos['lidos']} Diário(s) lido(s), {feitos['sem_diario']} sem Diário, "
              f"{feitos['novas']} ações novas contadas. / {feitos['lidos']} gazette(s) read, {feitos['novas']} new lawsuits counted.")
    return feitos


def tentar_de_novo_os_erros(banco):
    banco.con.execute("UPDATE historico SET situacao = 'fila' WHERE situacao = 'erro'")
    banco.con.commit()


def por_mes(banco, tribunais=None):
    """Totais por mês (todas as fontes: leitura normal e meses anteriores), para o gráfico de sazonalidade."""
    tribs = [t.upper() for t in tribunais or []]
    saida = {}
    for e in banco.estatisticas():
        if tribs and (e["tribunal"] or "").upper() not in tribs:
            continue
        mes = e["data"][:7]
        saida[mes] = saida.get(mes, 0) + int(e["novas"] or 0)
    return [{"mes": m, "novas": n} for m, n in sorted(saida.items())]


def por_dia_da_semana(banco, tribunais=None):
    tribs = [t.upper() for t in tribunais or []]
    saida = [0] * 7
    for e in banco.estatisticas():
        if tribs and (e["tribunal"] or "").upper() not in tribs:
            continue
        try:
            saida[dt.date.fromisoformat(e["data"][:10]).weekday()] += int(e["novas"] or 0)
        except ValueError:
            continue
    return saida

