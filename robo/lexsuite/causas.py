"""Por que uma leitura não deu certo, em palavras que o escritório entende (0.7.13).

Cada tentativa de leitura recebe uma causa: ok, ainda_nao_liberado_3h, nao_publicado, governo_fora,
bloqueio_fora_do_brasil, sem_internet ou erro_do_programa. A causa vem da RESPOSTA do site, nunca do relógio do
computador.
"""

import json

from . import rede

CAUSAS = ("ok", "ainda_nao_liberado_3h", "nao_publicado", "governo_fora", "bloqueio_fora_do_brasil", "sem_internet",
          "erro_do_programa", "interrompida")

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
    if erro.__class__.__name__ == "Interrompida":
        return "interrompida"
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
        "pt": "O site do CNJ (Diário de Justiça Eletrônico) não respondeu ou está em manutenção. Não é problema do seu computador. Os Diários que faltaram são lidos sozinhos na próxima leitura.",
        "en": "The CNJ site (Electronic Justice Gazette) did not respond or is under maintenance. It is not a problem with your computer. The missing gazettes are read automatically in the next reading."},
    "bloqueio_fora_do_brasil": {
        "pt": "O Diário só responde a pedidos feitos do Brasil. Use o programa num computador no Brasil (sem VPN de fora).",
        "en": "The gazette only answers requests made from Brazil. Use the program on a computer in Brazil (no foreign VPN)."},
    "sem_internet": {
        "pt": "Este computador está sem internet (ou a rede bloqueou o acesso). Confira a conexão e tente de novo.",
        "en": "This computer has no internet (or the network blocked access). Check the connection and try again."},
    "interrompida": {
        "pt": "Leitura interrompida a pedido. Os processos já gravados ficam; o resto é lido na próxima leitura (os Diários desta leitura são baixados de novo).",
        "en": "Reading stopped on request. Lawsuits already saved stay; the rest is read in the next reading (this reading's gazettes are downloaded again)."},
    "erro_do_programa": {
        "pt": "O programa encontrou um problema e parou esta leitura. A SolverONE já foi avisada. Tente de novo; se repetir, fale com judicial@solverone.com.br.",
        "en": "The program hit a problem and stopped this reading. SolverONE has been notified. Try again; if it repeats, write to judicial@solverone.com.br."},
}


# ---------- 0.7.47: de onde veio a falha ("é do CNJ ou é daqui"), desenho "CNJ fora e antivírus", 1.1 ----------
ORIGENS = ("cnj_aplicacao", "cnj_borda", "caderno_fora", "sem_internet_local", "bloqueio_local", "fora_do_brasil")

MENSAGENS_ORIGEM = {
    "cnj_aplicacao": {
        "pt": "O servidor do CNJ respondeu erro (aplicação). Sua internet está normal. Não é problema deste computador.",
        "en": "The CNJ server answered with an error (application). Your internet is working. It is not a problem with this computer."},
    "cnj_borda": {
        "pt": "A rede do CNJ (borda) não alcançou o servidor do CNJ. A falha é geral, não é deste computador.",
        "en": "The CNJ network (edge) could not reach the CNJ server. The failure is general, not on this computer."},
    "caderno_fora": {
        "pt": "O serviço de caderno do CNJ está fora; a consulta do CNJ funciona. Sua internet está normal. Não é problema deste computador.",
        "en": "The CNJ gazette service is down; the CNJ search works. Your internet is working. It is not a problem with this computer."},
    "sem_internet_local": {
        "pt": "Este computador está sem internet ou com a rede bloqueada.",
        "en": "This computer has no internet or its network is blocked."},
    "bloqueio_local": {
        "pt": "Algo neste computador (antivírus, firewall ou proxy) está barrando só os nossos endereços. A internet funciona.",
        "en": "Something on this computer (antivirus, firewall or proxy) is blocking only our addresses. The internet works."},
    "fora_do_brasil": {
        "pt": "O CNJ bloqueia acesso de fora do Brasil. Se este computador usa VPN de outro país, desligue a VPN e tente de novo.",
        "en": "The CNJ blocks access from outside Brazil. If this computer uses a VPN from another country, turn it off and try again."},
}


def _da_cloudfront(erro):
    d = getattr(erro, "detalhe", None) or {}
    corpo = str(getattr(erro, "texto", "") or d.get("corpo") or "").lower()
    return "cloudfront" in corpo and ("<html" in corpo or "request id" in corpo or "error from cloudfront" in corpo)


def _veio_da_cloudfront(erro):
    """A resposta passou pela borda da Amazon (o CNJ usa a CloudFront): cabeçalho server/via/x-amz-cf-id."""
    cab = (getattr(erro, "detalhe", None) or {}).get("cabecalhos") or {}
    return "cloudfront" in (str(cab.get("server", "")) + str(cab.get("via", ""))).lower() or bool(cab.get("x-amz-cf-id"))


def origem(erro, sondas=None):
    """Um de ORIGENS, ou "" quando não dá para dizer (sem sondas, ou falha que não é de rede). Sondas: o que
    `rede.sondar()` devolveu ({"solverone": {"ok"}, "consulta": {"ok"}}), ou None quando não foram feitas."""
    if erro is None:
        return ""
    so = ((sondas or {}).get("solverone") or {}).get("ok")
    co = ((sondas or {}).get("consulta") or {}).get("ok")
    if isinstance(erro, rede.BloqueadoForaDoBrasil):
        return "fora_do_brasil"
    if isinstance(erro, rede.ErroHTTP):
        if erro.codigo == 403 and "block access" in str(erro.texto or "").lower():
            return "fora_do_brasil"
        if erro.codigo >= 500 or erro.codigo == 429:
            if _da_cloudfront(erro):
                return "cnj_borda"
            if co is True:
                return "caderno_fora"
            return "cnj_aplicacao"
        if erro.codigo == 403 and not ainda_nao_liberado(erro):
            if so is False:
                return "sem_internet_local"
            if so is True and not _veio_da_cloudfront(erro):
                return "bloqueio_local"  # um 403 que não veio da borda do CNJ: proxy ou filtro do escritório
        return ""
    if isinstance(erro, rede.SemResposta):  # DNS, tempo esgotado, conexão cortada, certificado
        if so is False:
            return "sem_internet_local"
        if so is True:
            return "caderno_fora" if co is True else "bloqueio_local"
    return ""


def mensagem_origem(cod, lang="pt", antivirus=""):
    """A frase da origem; com o nome do antivírus encontrado, `bloqueio_local` diz qual é."""
    m = MENSAGENS_ORIGEM.get(cod)
    if not m:
        return ""
    txt = m.get(lang) or m["pt"]
    if cod == "bloqueio_local" and antivirus:
        txt = txt.replace("(antivírus,", f"({antivirus},").replace("(antivirus,", f"({antivirus},")
    return txt


def sondas_cabem(erro):
    """Só vale sondar quando o erro veio da rede de verdade (tem detalhe) e é de um tipo em que a sonda muda o diagnóstico."""
    if not getattr(erro, "detalhe", None):
        return False
    if isinstance(erro, rede.SemResposta):
        return True
    return isinstance(erro, rede.ErroHTTP) and (erro.codigo >= 500 or erro.codigo == 429 or (erro.codigo == 403 and not ainda_nao_liberado(erro)))


def detalhe_tecnico(erro, sondas=None, cod=""):
    """O texto de "Detalhes técnicos": a linha do diagnóstico, a resposta (código, cabeçalhos, corpo, tempo, IP) e as sondas."""
    if erro is None:
        return ""
    d = getattr(erro, "detalhe", None) or {}
    linhas = []
    if cod:
        linhas.append("Diagnóstico: " + mensagem_origem(cod))
    linhas.append(f"{erro.__class__.__name__}: {erro}"[:300])
    if d:
        linhas.append(f"Quando: {d.get('hora_brasilia', '')} (Brasília) · {d.get('hora_utc', '')} · {d.get('metodo', '')} {d.get('url', '')}")
        cab = d.get("cabecalhos") or {}
        if cab:
            linhas.append("Cabeçalhos: " + "; ".join(f"{k}: {v}" for k, v in cab.items()))
        if d.get("corpo"):
            linhas.append("Corpo: " + " ".join(str(d["corpo"]).split())[:300])
        linhas.append(f"Tempo: {d.get('ms', 0)} ms · tentativas: {d.get('tentativas', 1)} · IP: {d.get('ip') or 'não resolvido'}")
    for nome, rot in (("solverone", "Sonda SolverONE"), ("consulta", "Sonda consulta do CNJ")):
        s = (sondas or {}).get(nome)
        if s:
            linhas.append(f"{rot}: {'ok' if s.get('ok') else 'falhou'} (HTTP {s.get('http', 0)}, {s.get('ms', 0)} ms)" + (f" · {s['erro']}" if s.get("erro") else ""))
    return "\n".join(linhas)[:1500]


def mensagem(causa, lang="pt"):
    m = MENSAGENS.get(causa) or MENSAGENS["erro_do_programa"]
    return m.get(lang) or m["pt"]


def e_aviso(causa):
    """Causas que não são erro (a leitura seguiu normalmente)."""
    return causa in ("ok", "ainda_nao_liberado_3h", "nao_publicado", "interrompida")
