"""Assinatura digital Ed25519 (RFC 8032, PureEdDSA) em Python puro.

Usada para verificar pacotes de atualização do robô. Só biblioteca padrão.
"""

import hashlib
import secrets

# Constantes da curva (RFC 8032, seção 5.1)
P = 2**255 - 19
L = 2**252 + 27742317777372353535851937790883648493
D = -121665 * pow(121666, P - 2, P) % P
RAIZ_MENOS_1 = pow(2, (P - 1) // 4, P)  # sqrt(-1) mod p


def _sha512(dados: bytes) -> bytes:
    return hashlib.sha512(dados).digest()


# Pontos em coordenadas estendidas (X, Y, Z, T), com x = X/Z, y = Y/Z, xy = T/Z.
def _somar(p1, p2):
    x1, y1, z1, t1 = p1
    x2, y2, z2, t2 = p2
    a = (y1 - x1) * (y2 - x2) % P
    b = (y1 + x1) * (y2 + x2) % P
    c = 2 * t1 * t2 * D % P
    d = 2 * z1 * z2 % P
    e, f, g, h = b - a, d - c, d + c, b + a
    return (e * f % P, g * h % P, f * g % P, e * h % P)


def _multiplicar(k: int, ponto):
    # Duplicação e soma (da esquerda para a direita)
    r = (0, 1, 1, 0)
    for bit in bin(k)[2:]:
        r = _somar(r, r)
        if bit == "1":
            r = _somar(r, ponto)
    return r


def _iguais(p1, p2) -> bool:
    if (p1[0] * p2[2] - p2[0] * p1[2]) % P:
        return False
    return (p1[1] * p2[2] - p2[1] * p1[2]) % P == 0


def _recuperar_x(y: int, sinal: int):
    """Recupera x a partir de y; devolve None se não houver ponto na curva."""
    if y >= P:
        return None
    x2 = (y * y - 1) * pow(D * y * y + 1, P - 2, P) % P
    if x2 == 0:
        return None if sinal else 0
    x = pow(x2, (P + 3) // 8, P)
    if (x * x - x2) % P:
        x = x * RAIZ_MENOS_1 % P
    if (x * x - x2) % P:
        return None
    if (x & 1) != sinal:
        x = P - x
    return x


_GY = 4 * pow(5, P - 2, P) % P
_GX = _recuperar_x(_GY, 0)
B = (_GX, _GY, 1, _GX * _GY % P)  # ponto base


def _comprimir(ponto) -> bytes:
    zinv = pow(ponto[2], P - 2, P)
    x = ponto[0] * zinv % P
    y = ponto[1] * zinv % P
    return (y | ((x & 1) << 255)).to_bytes(32, "little")


def _descomprimir(dados: bytes):
    """Decodifica um ponto de 32 bytes; None se inválido."""
    if len(dados) != 32:
        return None
    y = int.from_bytes(dados, "little")
    sinal = y >> 255
    y &= (1 << 255) - 1
    x = _recuperar_x(y, sinal)
    if x is None:
        return None
    return (x, y, 1, x * y % P)


def _expandir(semente: bytes):
    h = _sha512(semente)
    a = int.from_bytes(h[:32], "little")
    a &= (1 << 254) - 8
    a |= 1 << 254
    return a, h[32:]


def _semente(privada_hex: str) -> bytes:
    semente = bytes.fromhex(privada_hex)
    if len(semente) != 32:
        raise ValueError("chave privada deve ter 32 bytes")
    return semente


def gerar_chaves():
    """Devolve (privada_hex, publica_hex)."""
    semente = secrets.token_bytes(32)
    privada = semente.hex()
    return privada, publica_de(privada)


def publica_de(privada_hex: str) -> str:
    a, _ = _expandir(_semente(privada_hex))
    return _comprimir(_multiplicar(a, B)).hex()


def assinar(mensagem: bytes, privada_hex: str) -> str:
    semente = _semente(privada_hex)
    a, prefixo = _expandir(semente)
    publica = _comprimir(_multiplicar(a, B))
    r = int.from_bytes(_sha512(prefixo + mensagem), "little") % L
    r_ponto = _comprimir(_multiplicar(r, B))
    k = int.from_bytes(_sha512(r_ponto + publica + mensagem), "little") % L
    s = (r + k * a) % L
    return (r_ponto + s.to_bytes(32, "little")).hex()


def verificar(mensagem: bytes, assinatura_hex: str, publica_hex: str) -> bool:
    """True só se a assinatura for válida; nunca levanta exceção."""
    try:
        assinatura = bytes.fromhex(assinatura_hex)
        publica = bytes.fromhex(publica_hex)
        if len(assinatura) != 64 or len(publica) != 32:
            return False
        a_ponto = _descomprimir(publica)
        r_ponto = _descomprimir(assinatura[:32])
        if a_ponto is None or r_ponto is None:
            return False
        s = int.from_bytes(assinatura[32:], "little")
        if s >= L:  # não maleável
            return False
        k = int.from_bytes(_sha512(assinatura[:32] + publica + bytes(mensagem)), "little") % L
        # Confere [S]B == R + [k]A
        esquerda = _multiplicar(s, B)
        direita = _somar(r_ponto, _multiplicar(k, a_ponto))
        return _iguais(esquerda, direita)
    except Exception:
        return False


def impressao(publica_hex: str) -> str:
    """16 primeiros hex do SHA-256 da chave pública, em grupos de 4."""
    h = hashlib.sha256(bytes.fromhex(publica_hex)).hexdigest()[:16]
    return " ".join(h[i:i + 4] for i in range(0, 16, 4))
