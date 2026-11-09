"""Por que uma leitura não deu certo, em palavras que o escritório entende (0.7.13).

Cada tentativa de leitura recebe uma causa: ok, ainda_nao_liberado_3h, nao_publicado, governo_fora,
bloqueio_fora_do_brasil, sem_internet ou erro_do_programa. A causa vem da RESPOSTA do site, nunca do relógio do
computador.
"""

import json

from . import rede

CAUSAS = ("ok", "ainda_nao_liberado_3h", "nao_publicado", "governo_fora", "bloqueio_fora_do_brasil", "sem_internet",
          "erro_do_programa")

# Texto que o DJEN devolve com o HTTP 403 entre 00:00 e 03:00 (o JSON vem com "ó": compara o texto já decodificado).
_LIBERA_3H = "podem ser acessados a partir das"


def _texto_da_resposta(texto):
    t = str(texto or "")
    try:
        d = json.loads(t)
        if isinstance(d, dict):
            t = " ".join(str(v) for v in d.values())
    except ValueError:
        pass
    return t.lower()


def ainda_nao_liberado(erro):
    """True para o 403 do DJEN "Os cadernos do dia atual só podem ser acessados a partir das 03:00"."""
    return isinstance(erro, rede.ErroHTTP) and erro.codigo == 403 and _LIBERA_3H in _texto_da_resposta(erro.texto)


def classificar(erro):
    if erro is None:
        return "ok"
    if isinstance(erro, rede.BloqueadoForaDoBrasil):
        return "bloqueio_fora_do_brasil"
    if ainda_nao_liberado(erro):
        return "ainda_nao_liberado_3h"
    if isinstance(erro, rede.ErroHTTP):
        if erro.codigo == 404:
            return "nao_publicado"
        if erro.codigo == 429 or erro.codigo >= 500:
            return "governo_fora"
        return "erro_do_programa"
    if isinstance(erro, rede.SemResposta):
        m = str(erro.motivo).lower()
        if any(x in m for x in ("getaddrinfo", "name or service not known", "nodename nor servname", "11001",
                                 "temporary failure in name resolution", "network is unreachable", "10051", "10065")):
            return "sem_internet"
        return "governo_fora"
    return "erro_do_programa"


MENSAGENS = {
    "ainda_nao_liberado_3h": {
        "pt": "O Diário de hoje só fica disponível a partir das 3h da manhã. Li até o último dia já publicado; nada a fazer.",
        "en": "Today's gazette is only available from 3 a.m. I read up to the last published day; nothing to do."},
    "nao_publicado": {
        "pt": "O tribunal ainda não publicou o Diário desse dia.",
        "en": "The court has not published the gazette for that day yet."},
    "governo_fora": {
        "pt": "O site do CNJ (Diário de Justiça Eletrônico) não respondeu ou está em manutenção. Não é problema do seu computador. Tente mais tarde.",
        "en": "The CNJ site (Electronic Justice Gazette) did not respond or is under maintenance. It is not a problem with your computer. Try again later."},
    "bloqueio_fora_do_brasil": {
        "pt": "O Diário só responde a pedidos feitos do Brasil. Use o programa num computador no Brasil (sem VPN de fora).",
        "en": "The gazette only answers requests made from Brazil. Use the program on a computer in Brazil (no foreign VPN)."},
    "sem_internet": {
        "pt": "Este computador está sem internet (ou a rede bloqueou o acesso). Confira a conexão e tente de novo.",
        "en": "This computer has no internet (or the network blocked access). Check the connection and try again."},
    "erro_do_programa": {
        "pt": "O programa encontrou um problema e parou esta leitura. A SolverONE já foi avisada. Tente de novo; se repetir, fale com judicial@solverone.com.br.",
        "en": "The program hit a problem and stopped this reading. SolverONE has been notified. Try again; if it repeats, write to judicial@solverone.com.br."},
}


def mensagem(causa, lang="pt"):
    m = MENSAGENS.get(causa) or MENSAGENS["erro_do_programa"]
    return m.get(lang) or m["pt"]


def e_aviso(causa):
    """Causas que não são erro (a leitura seguiu normalmente)."""
    return causa in ("ok", "ainda_nao_liberado_3h", "nao_publicado")
