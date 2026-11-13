"""Entregas do robô: planilha (CSV que abre no Excel e no Google Planilhas),
painel (um HTML que abre no navegador, até sem internet) e dados.json.
"""

import csv
import json
import os
import re

AQUI = os.path.dirname(os.path.abspath(__file__))
MODELO_PAINEL = os.path.join(os.path.dirname(AQUI), "painel_modelo.html")
MODELO_MONITOR = os.path.join(os.path.dirname(AQUI), "monitor_modelo.html")
MODELO_RADAR = os.path.join(os.path.dirname(AQUI), "radar_modelo.html")

COLUNAS_LEADS = [
    ("Prioridade", "faixa"), ("Nota (0-100)", "nota"), ("Cliente da carteira", "cliente"), ("Por quê", "motivos"),
    ("Fonte", "fonte"), ("Data da publicação", "data_publicacao"), ("Audiência marcada", "audiencia_txt"), ("Ajuizada em", "ajuizada_em"), ("Tribunal", "tribunal"), ("Vara", "vara"),
    ("Processo", "processo"), ("Rito", "rito"), ("Empresa(s) ré(s)", "empresas"), ("CNPJ", "cnpjs"),
    ("Razão social (Receita)", "razao_social"), ("Porte", "porte"), ("Atividade", "atividade"),
    ("Cidade/UF", "cidade_uf"), ("Capital social", "capital_social"),
    ("Valor da causa (se publicado)", "valor_causa"), ("Ações novas da empresa no período", "acoes_no_periodo"),
    ("Link da publicação", "link"), ("Status", "status"), ("Responsável", "responsavel"), ("Observações", "obs"),
]

COLUNAS_RECENTES = [("Data do ajuizamento", "data"), ("Processo", "processo"), ("Rito", "rito"),
                    ("Assuntos", "assuntos"), ("Situação", "situacao")]


COLUNAS_MONITOR = [
    ("Urgência", "urgencia"), ("Ato", "ato"), ("Disponibilizada em", "data"), ("Publicação (estimada)", "publicacao"),
    ("Prazos começam (estimado)", "inicio_prazo"), ("Prazo (dias)", "dias_prazo"), ("Vencimento (estimado)", "vencimento"),
    ("Processo", "processo"), ("Tribunal", "tribunal"), ("Órgão", "orgao"), ("Cliente", "cliente"),
    ("Responsável", "responsavel"), ("Por que avisou", "motivos"), ("Trecho", "trecho"), ("Link", "link"),
    ("Visto pelo robô em", "visto_em"),
]


def _celula(v):
    if isinstance(v, list):
        return _sem_formula(" | ".join(str(x) for x in v))
    if isinstance(v, float):
        return f"{v:.2f}".replace(".", ",")
    return "" if v is None else _sem_formula(str(v)) if isinstance(v, str) else str(v)


def _sem_formula(t):
    """Texto vindo do Diário não pode virar fórmula ao abrir o CSV no Excel (injeção de fórmula)."""
    return ("'" + t) if t[:1] in ("=", "+", "-", "@", "\t", "\r") else t


def gravar_csv(caminho, linhas, colunas):
    # Ponto e vírgula + BOM: é o que o Excel em português abre certinho com dois cliques.
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow([titulo for titulo, _ in colunas])
        for l in linhas:
            w.writerow([_celula(l.get(chave)) for _, chave in colunas])


def lead_para_saida(lead):
    """Só os campos que podem sair (o trecho de texto usado na classificação fica de fora)."""
    emp = lead.get("empresa_receita") or {}
    return {
        "faixa": lead.get("faixa"), "nota": lead.get("nota"), "motivos": lead.get("motivos"),
        "cliente": lead.get("cliente", ""), "fonte": lead.get("fonte", "DJEN"),
        "audiencia": lead.get("audiencia"), "ajuizada_em": lead.get("ajuizada_em", ""),
        "audiencia_txt": (f"{lead['audiencia']['data']} ({lead['audiencia']['tipo']})" if lead.get("audiencia") else ""),
        "data_publicacao": lead.get("data_publicacao"), "tribunal": lead.get("tribunal"),
        "vara": lead.get("vara"), "processo": lead.get("processo"), "rito": lead.get("rito"),
        "empresas": lead.get("empresas"), "cnpjs": lead.get("cnpjs"),
        "razao_social": emp.get("razao_social", ""), "porte": emp.get("porte", ""),
        "atividade": emp.get("atividade", ""),
        "cidade_uf": f"{emp.get('municipio', '')}/{emp.get('uf', '')}" if emp else "",
        "capital_social": emp.get("capital_social", ""), "valor_causa": lead.get("valor_causa"),
        "acoes_no_periodo": lead.get("acoes_no_periodo", 1), "link": lead.get("link"),
        "status": lead.get("status", "Novo"), "responsavel": "", "obs": "",
    }


def _embutir(modelo_html, variavel, caminho, dados):
    with open(modelo_html, encoding="utf-8") as f:
        modelo = f.read()
    modelo = re.sub(r"/\*FUNDOS\*/.*?/\*/FUNDOS\*/", "", modelo, flags=re.S)  # 0.7.40: o retrato sai sem as imagens de fundo
    # "</" escapado para o JSON nunca fechar a tag <script> antes da hora.
    bloco = json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(modelo.replace(f"window.{variavel} = null;", f"window.{variavel} = " + bloco + ";", 1))


def gravar_painel(caminho, dados):
    _embutir(MODELO_PAINEL, "LEXSUITE_DADOS", caminho, dados)


def gravar_monitor(caminho, dados):
    """Caixa de publicações do monitor (abre no navegador, até sem internet)."""
    _embutir(MODELO_MONITOR, "LEXSUITE_MONITOR", caminho, dados)


def gravar_json(caminho, dados):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=1)


def gravar_radar(caminho, dados):
    """A lista do dia do Radar SP (abre no navegador, até sem internet)."""
    _embutir(MODELO_RADAR, "LEXSUITE_RADAR", caminho, dados)
