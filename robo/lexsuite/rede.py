"""Pedidos à internet com paciência.

Os serviços públicos às vezes respondem "muitos pedidos" (429) ou ficam
instáveis (5xx). Em vez de desistir, esperamos e tentamos de novo,
cada vez esperando mais — e sempre com um intervalo mínimo entre pedidos,
para não sobrecarregar os sistemas do Judiciário.
"""

import json
import time
import urllib.error
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
    for tentativa in range(1, tentativas + 1):
        _respeitar_intervalo(intervalo_minimo)
        req = urllib.request.Request(_so_https(url), data=dados, headers=cab)
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
                pausa = int(e.headers.get("Retry-After") or espera)
                time.sleep(min(pausa, 120))
                espera *= 2
                continue
            raise RuntimeError(f"HTTP {e.code} em {url[:120]}: {texto[:300]}") from None
        except (urllib.error.URLError, TimeoutError) as e:
            if tentativa < tentativas:
                time.sleep(espera)
                espera *= 2
                continue
            raise RuntimeError(f"Sem resposta de {url[:120]}: {e}") from None
    raise RuntimeError("Tentativas esgotadas")


LIMITE_DOWNLOAD = 2 * 1024 * 1024 * 1024  # 2 GB: nenhum caderno chega perto; evita resposta sem fim


def pedir_bytes(url, tempo_limite=600, limite=LIMITE_DOWNLOAD):
    """Baixa um arquivo (ex.: o ZIP do caderno do DJEN, cujo link vale 5 minutos), em pedaços e com teto de tamanho."""
    req = urllib.request.Request(_so_https(url), headers={"User-Agent": AGENTE})
    partes, total = [], 0
    with urllib.request.urlopen(req, timeout=tempo_limite) as r:  # nosec B310 - esquema conferido em _so_https
        while True:
            pedaco = r.read(1024 * 1024)
            if not pedaco:
                break
            total += len(pedaco)
            if total > limite:
                raise ValueError(f"resposta maior que o limite de {limite // (1024 * 1024)} MB: {url[:60]}")
            partes.append(pedaco)
    return b"".join(partes)


def pedir_json(url, corpo=None, cabecalhos=None, **kw):
    return json.loads(pedir(url, corpo, cabecalhos, **kw))
