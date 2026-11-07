"""Dados públicos da empresa pelo CNPJ (Receita Federal, via BrasilAPI e Minha Receita).

Guarda o cadastro público da EMPRESA: razão social, porte, capital social, CNAE
(principal e secundários), cidade, telefone e e-mail cadastrados e o quadro de
sócios e administradores (nome e qualificação, como constam no cadastro público).
O uso desses contatos é decisão do escritório (compliance); o robô só os lê da Receita.
"""

import json
import time

from . import rede

FONTES = ["https://brasilapi.com.br/api/cnpj/v1/{cnpj}", "https://minhareceita.org/{cnpj}"]


def _telefone(bruto):
    """'1121212121' → '11 2121-2121' (ou vazio)."""
    import re
    d = re.sub(r"\D", "", str(bruto or ""))
    if len(d) < 10:
        return ""
    return f"{d[:2]} {d[2:-4]}-{d[-4:]}"


def consultar(cnpj, banco=None, validade_dias=30):
    if banco:
        guardado = banco.cnpj_em_cache(cnpj, validade_dias)
        if guardado:
            return guardado
    for fonte in FONTES:
        try:
            d = rede.pedir_json(fonte.format(cnpj=cnpj), intervalo_minimo=1.2, tentativas=3)
        except RuntimeError:
            continue
        resumo = {
            "cnpj": cnpj,
            "razao_social": d.get("razao_social") or "",
            "nome_fantasia": d.get("nome_fantasia") or "",
            "porte": d.get("porte") or d.get("descricao_porte") or "",
            "cnae": str(d.get("cnae_fiscal") or ""),
            "atividade": d.get("cnae_fiscal_descricao") or "",
            "cnaes_secundarios": [c.get("descricao", "") for c in (d.get("cnaes_secundarios") or []) if isinstance(c, dict)][:6],
            "municipio": d.get("municipio") or "",
            "uf": d.get("uf") or "",
            "capital_social": d.get("capital_social") or 0,
            "situacao": d.get("descricao_situacao_cadastral") or "",
            "inicio_atividade": d.get("data_inicio_atividade") or "",
            "telefone": _telefone(d.get("ddd_telefone_1")),
            "telefone2": _telefone(d.get("ddd_telefone_2")),
            "email": (d.get("email") or "").lower(),
            "socios": [{"nome": q.get("nome_socio") or q.get("nome") or "", "qualificacao": q.get("qualificacao_socio") or q.get("qualificacao") or ""}
                       for q in (d.get("qsa") or []) if isinstance(q, dict)][:8],
            "simples": (d.get("opcao_pelo_simples") if d.get("opcao_pelo_simples") is not None else None),
            "consultado_em": time.strftime("%Y-%m-%d"),
        }
        if banco:
            banco.guardar_cnpj(cnpj, resumo)
        return resumo
    return None
