"""Dados públicos da empresa pelo CNPJ (Receita Federal, via BrasilAPI e Minha Receita).

Guarda o cadastro público da EMPRESA: razão social, porte, capital social, CNAE
(principal e secundários), cidade, telefone e e-mail cadastrados e o quadro de
sócios e administradores (nome e qualificação, como constam no cadastro público).
O uso desses contatos é decisão do escritório (compliance); o robô só os lê da Receita.
"""

import json
import time

from . import documento, rede

FONTES = ["https://brasilapi.com.br/api/cnpj/v1/{cnpj}", "https://minhareceita.org/{cnpj}"]


def _telefone(bruto):
    """'1121212121' → '11 2121-2121' (ou vazio)."""
    import re
    d = re.sub(r"\D", "", str(bruto or ""))
    if len(d) < 10:
        return ""
    return f"{d[:2]} {d[2:-4]}-{d[-4:]}"


SEM_SUPORTE_DIAS = 7  # 0.7.33: CNPJ com letras que as fontes ainda não conhecem é tentado de novo depois de 7 dias


def consultar(cnpj, banco=None, validade_dias=30, rapido=False):
    cnpj = documento.limpar(cnpj)  # 0.7.33: os 14 caracteres, com as letras (CNPJ alfanumérico)
    if banco:
        guardado = banco.cnpj_em_cache(cnpj, validade_dias)
        if guardado and guardado.get("situacao") == "fonte_sem_suporte" and not banco.cnpj_em_cache(cnpj, SEM_SUPORTE_DIAS):
            guardado = None
        if guardado:
            return guardado
    recusas, sem_rede = 0, 0
    for fonte in FONTES:
        try:
            # revisão (0.7.36): a tela (empresas excluídas) pede uma tentativa só, com tempo curto, para não travar o Salvar
            d = rede.pedir_json(fonte.format(cnpj=cnpj), intervalo_minimo=1.2, tentativas=1 if rapido else 3, tempo_limite=6 if rapido else 120)
        except rede.ErroHTTP as e:
            recusas += e.codigo in (400, 404)
            sem_rede += e.codigo == 429 or e.codigo >= 500  # revisão: fonte ocupada ou fora do ar não é "não encontrado"
            continue
        except (RuntimeError, OSError):
            sem_rede += 1
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
            # 0.7.14: endereço completo da empresa (cadastro público); vale também para MEI (decisão do dono, 09/Nov)
            "logradouro": " ".join(x for x in (d.get("descricao_tipo_de_logradouro") or "", d.get("logradouro") or "") if x).strip(),
            "numero": str(d.get("numero") or ""), "complemento": d.get("complemento") or "",
            "bairro": d.get("bairro") or "", "cep": str(d.get("cep") or ""),
            "socios": [{"nome": q.get("nome_socio") or q.get("nome") or "", "qualificacao": q.get("qualificacao_socio") or q.get("qualificacao") or ""}
                       for q in (d.get("qsa") or []) if isinstance(q, dict)][:8],
            "simples": (d.get("opcao_pelo_simples") if d.get("opcao_pelo_simples") is not None else None),
            "consultado_em": time.strftime("%Y-%m-%d"),
        }
        if banco:
            banco.guardar_cnpj(cnpj, resumo)
        return resumo
    if recusas == len(FONTES) and documento.eh_alfanumerico(cnpj):
        # 0.7.33 (desenho da Arquitetura, 3.4): CNPJ novo que as fontes públicas ainda não aceitam não é "não existe";
        # a ação segue com o CNPJ, marcada "CNPJ novo (dados da Receita indisponíveis)", sem porte, setor nem capital
        resumo = {"cnpj": cnpj, "situacao": "fonte_sem_suporte", "razao_social": "", "nome_fantasia": "", "porte": "",
                  "capital_social": 0, "consultado_em": time.strftime("%Y-%m-%d")}
        if banco:
            banco.guardar_cnpj(cnpj, resumo)
        return resumo
    if rapido and sem_rede == len(FONTES):
        return {"cnpj": cnpj, "situacao": "sem_resposta", "razao_social": ""}  # sem internet: a tela diz isso (não é "não encontrado")
    return None
