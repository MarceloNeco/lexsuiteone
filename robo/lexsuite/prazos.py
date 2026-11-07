"""Datas do DJEN e prazos em dias úteis (estimativa para conferência, sem IA).

Regra do DJEN (Lei 11.419/2006, art. 4º, e Res. CNJ 455/2022):
  disponibilização no dia D (a partir das 19h)
  → publicação = 1º dia útil depois de D
  → o prazo começa no 1º dia útil depois da publicação.
Na Justiça do Trabalho os prazos contam em dias úteis (CLT, art. 775) e ficam
suspensos de 20/12 a 20/01 (CLT, art. 775-A).

Dias sem expediente considerados aqui: sábados, domingos, feriados nacionais e
os feriados da Justiça Federal/do Trabalho (Lei 5.010/1966, art. 62: 20/12 a
06/01, quarta a domingo da Semana Santa, segunda e terça de Carnaval, 11/08,
01/11, 02/11 e 08/12). Feriado municipal ou estadual e suspensão decidida pelo
tribunal NÃO entram sozinhos: ponha em "feriados_extras" no config.json.
"""

import datetime as dt
import re

_FIXOS = [(1, 1), (4, 21), (5, 1), (8, 11), (9, 7), (10, 12), (11, 1), (11, 2), (11, 15), (11, 20),
          (12, 8), (12, 25)]


def pascoa(ano):
    """Domingo de Páscoa (algoritmo de Meeus/Jones/Butcher)."""
    a, b, c = ano % 19, ano // 100, ano % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = (h + l - 7 * m + 114) % 31 + 1
    return dt.date(ano, mes, dia)


def feriados(ano, extras=()):
    p = pascoa(ano)
    dias = {dt.date(ano, m, d) for m, d in _FIXOS}
    dias |= {p - dt.timedelta(days=n) for n in (48, 47)}           # Carnaval (segunda e terça)
    dias |= {p - dt.timedelta(days=n) for n in range(0, 5)}        # quarta-feira santa a domingo de Páscoa
    dias.add(p + dt.timedelta(days=60))                            # Corpus Christi
    dias |= {dt.date(ano, 12, d) for d in range(20, 32)}           # recesso forense
    dias |= {dt.date(ano, 1, d) for d in range(1, 7)}
    for x in extras:
        try:
            dias.add(dt.date.fromisoformat(str(x)))
        except ValueError:
            pass
    return dias


def dia_util(d, extras=()):
    return d.weekday() < 5 and d not in feriados(d.year, extras)


def proximo_dia_util(d, extras=()):
    d += dt.timedelta(days=1)
    while not dia_util(d, extras):
        d += dt.timedelta(days=1)
    return d


def _suspenso(d):
    # CLT art. 775-A: prazos suspensos de 20/12 a 20/01 (inclusive).
    return (d.month == 12 and d.day >= 20) or (d.month == 1 and d.day <= 20)


def dia_de_prazo(d, extras=()):
    return dia_util(d, extras) and not _suspenso(d)


def proximo_dia_de_prazo(d, extras=()):
    d += dt.timedelta(days=1)
    while not dia_de_prazo(d, extras):
        d += dt.timedelta(days=1)
    return d


_PRAZO = re.compile(r"prazo\s+(?:legal\s+)?(?:comum\s+)?(?:sucessivo\s+)?(?:de\s+)?(\d{1,2})\s*(?:\([^)]{2,20}\)\s*)?dias?"
                    r"|(\d{1,2})\s*(?:\([^)]{2,20}\)\s*)?dias?\s+(?:[uú]teis\s+)?(?:para|a\s+fim)", re.I)


def prazo_no_texto(texto):
    """Primeiro 'prazo de N dias' escrito na publicação (ou None)."""
    m = _PRAZO.search(texto or "")
    if not m:
        return None
    n = int(m.group(1) or m.group(2))
    return n if 1 <= n <= 60 else None


def calcular(data_disponibilizacao, dias_prazo=None, extras=()):
    """Devolve as datas de publicação, início e (se houver prazo no texto) o vencimento estimado."""
    try:
        d = dt.date.fromisoformat(str(data_disponibilizacao)[:10])
    except ValueError:
        return {}
    publicacao = proximo_dia_util(d, extras)
    inicio = proximo_dia_util(publicacao, extras)
    if _suspenso(inicio) or not dia_de_prazo(inicio, extras):
        inicio = proximo_dia_de_prazo(inicio, extras)
    saida = {"publicacao": publicacao.isoformat(), "inicio_prazo": inicio.isoformat()}
    if dias_prazo:
        fim = inicio
        for _ in range(dias_prazo - 1):
            fim = proximo_dia_de_prazo(fim, extras)
        saida["dias_prazo"] = dias_prazo
        saida["vencimento"] = fim.isoformat()
    return saida
