"""Pedidos à internet com paciência.

Os serviços públicos às vezes respondem "muitos pedidos" (429) ou ficam
instáveis (5xx). Em vez de desistir, esperamos e tentamos de novo,
cada vez esperando mais — e sempre com um intervalo mínimo entre pedidos,
para não sobrecarregar os sistemas do Judiciário.
"""

import datetime as dt
import json
import socket
import time
import urllib.error
import urllib.parse
import urllib.request

from . import VERSAO

AGENTE = f"LexSuiteONE-Robo/{VERSAO} (+https://solverone.com.br)"
_ultimo_pedido = [0.0]


def _so_https(url):
    """O robô só fala HTTPS: nada de file:, ftp: ou http: puro."""
    if not str(url).lower().startswith("https://"):
        raise ValueError(f"endereço recusado (só https): {str(url)[:60]}")
    return url


class BloqueadoForaDoBrasil(Exception):
    """O serviço recusou porque o pedido não saiu de um endereço do Brasil."""


def _sem_consulta(url):
    """Endereço sem a parte depois do "?" (o link do caderno vale 5 minutos e traz assinatura): não vai para registro."""
    return str(url).split("?", 1)[0][:120]


# 0.7.47 (desenho "CNJ fora e antivírus", 1.1): cabeçalhos que dizem de onde veio a resposta (a aplicação do CNJ, a borda
# da Amazon CloudFront, um proxy do escritório). Só estes; nada de cookie nem de autorização.
CABECALHOS_GUARDADOS = ("date", "server", "via", "x-cache", "x-amz-cf-pop", "x-amz-cf-id", "content-type", "retry-after")


def _ip_de(url):
    """O IP que o nome do site resolveu (para saber se o DNS respondeu e para onde), ou ""."""
    try:
        host = urllib.parse.urlsplit(str(url)).hostname or ""
        return socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)[0][4][0] if host else ""
    except (OSError, UnicodeError, IndexError, ValueError):
        return ""


def _falha_de_dns(e):
    """O nome nem resolveu: não adianta perguntar o IP de novo (só atrasaria)."""
    m = str(getattr(e, "reason", e)).lower()
    return any(x in m for x in ("getaddrinfo", "name or service not known", "nodename nor servname", "11001", "temporary failure in name resolution"))


def detalhe_da_falha(url, metodo="GET", cabecalhos=None, corpo="", ms=0, tentativas=1, ip=None):
    """O que se guarda de cada falha (0.7.47): hora UTC e de Brasília, endereço sem a consulta, método, cabeçalhos de
    origem, os 300 primeiros caracteres do corpo, tempo de resposta, tentativas e o IP resolvido."""
    agora = dt.datetime.now(dt.timezone.utc)
    cab = {}
    for k in CABECALHOS_GUARDADOS:
        v = (cabecalhos or {}).get(k) if hasattr(cabecalhos or {}, "get") else None
        if v:
            cab[k] = str(v)[:120]
    return {"hora_utc": agora.isoformat(timespec="seconds"),
            "hora_brasilia": (agora - dt.timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S"),
            "url": _sem_consulta(url), "metodo": metodo, "cabecalhos": cab, "corpo": str(corpo or "")[:300],
            "ms": int(ms or 0), "tentativas": int(tentativas or 1), "ip": _ip_de(url) if ip is None else str(ip)}


class ErroHTTP(RuntimeError):
    """O site respondeu com um código de erro (403, 404, 503...). Guarda o código e o texto da resposta, para o
    programa saber a causa (0.7.13: o 403 "só a partir das 03:00" do DJEN não é erro). 0.7.47: `detalhe` com
    cabeçalhos, tempo, tentativas e IP (vazio quando o erro não veio da rede de verdade, como nos testes)."""

    def __init__(self, codigo, url, texto, detalhe=None):
        self.codigo, self.url, self.texto = int(codigo), _sem_consulta(url), str(texto or "")[:2000]
        self.detalhe = detalhe or {}
        super().__init__(f"HTTP {self.codigo} em {self.url}: {self.texto[:300]}")


class SemResposta(RuntimeError):
    """O site não respondeu (tempo esgotado, sem internet, endereço não encontrado)."""

    def __init__(self, url, motivo, detalhe=None):
        self.url, self.motivo = _sem_consulta(url), str(motivo)
        self.detalhe = detalhe or {}
        super().__init__(f"Sem resposta de {self.url}: {self.motivo}")


def _respeitar_intervalo(minimo):
    espera = minimo - (time.time() - _ultimo_pedido[0])
    if espera > 0:
        time.sleep(espera)
    _ultimo_pedido[0] = time.time()


def pedir(url, corpo=None, cabecalhos=None, tentativas=5, intervalo_minimo=0.6, tempo_limite=120):
    """Devolve o texto da resposta. `corpo` (dict) vira JSON e o pedido vira POST."""
    cab = {"User-Agent": AGENTE, "Accept": "application/json"}
    cab.update(cabecalhos or {})
    dados = None
    if corpo is not None:
        dados = json.dumps(corpo).encode("utf-8")
        cab["Content-Type"] = "application/json"
    espera = 2
    metodo = "POST" if dados is not None else "GET"
    for tentativa in range(1, tentativas + 1):
        _respeitar_intervalo(intervalo_minimo)
        req = urllib.request.Request(_so_https(url), data=dados, headers=cab)
        t0 = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=tempo_limite) as r:  # nosec B310 - esquema conferido em _so_https
                return r.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            texto = e.read().decode("utf-8", errors="replace")[:2000]
            if e.code == 403 and "block access from your country" in texto:
                raise BloqueadoForaDoBrasil(
                    "O DJEN só responde a pedidos que saem do Brasil. "
                    "Rode o robô num computador ou servidor no Brasil.") from None
            if e.code in (429, 500, 502, 503, 504) and tentativa < tentativas:
                try:
                    pausa = int(e.headers.get("Retry-After") or espera)
                except (TypeError, ValueError):  # Retry-After em forma de data
                    pausa = espera
                time.sleep(min(pausa, 120))
                espera *= 2
                continue
            raise ErroHTTP(e.code, url, texto, detalhe_da_falha(url, metodo, e.headers, texto, (time.perf_counter() - t0) * 1000, tentativa)) from None
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if tentativa < tentativas:
                time.sleep(espera)
                espera *= 2
                continue
            raise SemResposta(url, e, detalhe_da_falha(url, metodo, None, "", (time.perf_counter() - t0) * 1000, tentativa,
                                                       ip="" if _falha_de_dns(e) else None)) from None
    raise RuntimeError("Tentativas esgotadas")


LIMITE_DOWNLOAD = 2 * 1024 * 1024 * 1024  # 2 GB: nenhum caderno chega perto; evita resposta sem fim


def pedir_bytes(url, tempo_limite=600, limite=LIMITE_DOWNLOAD):
    """Baixa um arquivo (ex.: o ZIP do caderno do DJEN, cujo link vale 5 minutos), em pedaços e com teto de tamanho."""
    req = urllib.request.Request(_so_https(url), headers={"User-Agent": AGENTE})
    partes, total = [], 0
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=tempo_limite) as r:  # nosec B310 - esquema conferido em _so_https
            while True:
                pedaco = r.read(1024 * 1024)
                if not pedaco:
                    break
                total += len(pedaco)
                if total > limite:
                    raise ValueError(f"resposta maior que o limite de {limite // (1024 * 1024)} MB: {url[:60]}")
                partes.append(pedaco)
    except urllib.error.HTTPError as e:
        texto = e.read().decode("utf-8", errors="replace")[:2000]
        raise ErroHTTP(e.code, url, texto, detalhe_da_falha(url, "GET", e.headers, texto, (time.perf_counter() - t0) * 1000)) from None
    except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
        raise SemResposta(url, e, detalhe_da_falha(url, "GET", None, "", (time.perf_counter() - t0) * 1000, ip="" if _falha_de_dns(e) else None)) from None
    return b"".join(partes)


def pedir_json(url, corpo=None, cabecalhos=None, **kw):
    return json.loads(pedir(url, corpo, cabecalhos, **kw))


# ---------- 0.7.47: sondas de controle, quando o CNJ falha ----------
# Duas perguntas leves para separar "é do CNJ" de "é deste computador": o site da SolverONE (a internet do escritório
# funciona?) e outro serviço do CNJ, a consulta pública (o CNJ inteiro está fora ou só o caderno?).
SONDA_SOLVERONE = "https://judicial.solverone.com.br/atualizacao/versao.json"
SONDA_CONSULTA = "https://comunicaapi.pje.jus.br/api/v1/comunicacao?itensPorPagina=5"


def _sondar_um(url, tempo_limite):
    t0 = time.perf_counter()
    try:
        pedir(url, tentativas=1, intervalo_minimo=0, tempo_limite=tempo_limite)
        return {"ok": True, "http": 200, "ms": int((time.perf_counter() - t0) * 1000)}
    except BloqueadoForaDoBrasil:
        return {"ok": False, "http": 403, "ms": int((time.perf_counter() - t0) * 1000), "erro": "fora do Brasil"}
    except ErroHTTP as e:
        # respondeu: a rede chegou lá (a consulta devolve 4xx para pedido incompleto; isso ainda prova que ela está de pé)
        return {"ok": e.codigo < 500, "http": e.codigo, "ms": int((time.perf_counter() - t0) * 1000)}
    except Exception as e:  # noqa: BLE001 - sem resposta, DNS, certificado: a sonda falhou
        return {"ok": False, "http": 0, "ms": int((time.perf_counter() - t0) * 1000), "erro": str(e)[:160]}


def sondar(tempo_limite=10):
    """{"solverone": {ok, http, ms}, "consulta": {ok, http, ms}}. Nunca levanta exceção."""
    return {"solverone": _sondar_um(SONDA_SOLVERONE, tempo_limite), "consulta": _sondar_um(SONDA_CONSULTA, tempo_limite)}
