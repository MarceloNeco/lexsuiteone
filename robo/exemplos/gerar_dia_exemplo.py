"""Gera exemplos/dia_exemplo.json: um dia FICTÍCIO de publicações em 3 tribunais, para a demonstração
da página "O dia nos tribunais" (python lexsuite_robo.py monitor --exemplo).

Nada aqui é real: empresas, números de processo e textos são inventados. As varas têm nomes reais
só para a demonstração parecer com o uso de verdade. Rodar: python exemplos/gerar_dia_exemplo.py
"""

import json
import os
import random

AQUI = os.path.dirname(os.path.abspath(__file__))
R = random.Random(2026)

VARAS = [
    {"tribunal": "TRT2", "vara": "Vara do Trabalho de Cajamar", "orgao_id": "9001", "tr": "02", "vt": "0221"},
    {"tribunal": "TRT2", "vara": "2ª Vara do Trabalho de Barueri", "orgao_id": "9002", "tr": "02", "vt": "0202"},
    {"tribunal": "TRT15", "vara": "3ª Vara do Trabalho de Jundiaí", "orgao_id": "9003", "tr": "15", "vt": "0097"},
    {"tribunal": "TRT3", "vara": "2ª Vara do Trabalho de Contagem", "orgao_id": "9004", "tr": "03", "vt": "0030"},
]

# (nome, setor "de verdade" só para variar os textos)
EMPRESAS = [
    "LOGISTICA SERRA AZUL LTDA", "TRANSPORTES ROTA NORTE LTDA", "ARMAZENS JAGUARI S.A.", "ENTREGAS VIA RAPIDA LTDA",
    "RH PRISMA TERCEIRIZACAO LTDA", "VERTICE MAO DE OBRA TEMPORARIA LTDA", "COOPERATIVA DE TRABALHO HORIZONTE",
    "SUPERMERCADOS HORIZONTE S.A.", "LOJAS MARILIA COMERCIO LTDA", "ATACADO VALE LTDA", "COMERCIAL BONS VENTOS LTDA",
    "HOSPITAL SANTA CLARA LTDA", "DROGARIA PEROLA LTDA", "GUARDIAO SEGURANCA E VIGILANCIA LTDA",
    "LIMPEZA TOTAL FACILITIES LTDA", "CONSTRUTORA VALE VERDE LTDA", "INCORPORADORA ALTO DA SERRA S.A.",
    "METALURGICA CONTAGEM INDUSTRIAL S.A.", "ALIMENTOS BOA MESA LTDA", "PLASTICOS JUNDIAI INDUSTRIA LTDA",
    "ESCOLA NOVO SABER LTDA", "CONDOMINIO PARQUE DAS ARVORES", "CALL CENTER ATENDE BEM LTDA",
    "TRANSPORTADORA CAMINHO DO SOL LTDA", "FRIGORIFICO BOM PASTO S.A.", "RESTAURANTE SABOR DA SERRA LTDA",
    "AUTO PECAS ROTA 300 LTDA", "FARMACIA VIDA NOVA LTDA", "TEXTIL ALGODAO DOCE INDUSTRIA LTDA",
    "CLINICA ODONTO SORRISO LTDA", "ENGENHARIA PONTE FIRME LTDA", "HOTEL JARDIM DAS PALMEIRAS LTDA",
    "GRAFICA IMPRESSAO RAPIDA LTDA", "DISTRIBUIDORA DE BEBIDAS GELADA LTDA", "ACADEMIA CORPO EM FORMA LTDA",
    "SERVICOS DE PORTARIA ATENTO LTDA", "EMBALAGENS PAPEL FORTE LTDA", "COOPERATIVA AGRICOLA DO VALE",
    "TELECOM CONECTA BRASIL S.A.", "BANCO FICTICIO DE CREDITO S.A.", "ESCOLA DE IDIOMAS FALA MAIS LTDA",
]
PARES_TERCEIRIZACAO = [
    ("RH PRISMA TERCEIRIZACAO LTDA", "SUPERMERCADOS HORIZONTE S.A."),
    ("GUARDIAO SEGURANCA E VIGILANCIA LTDA", "HOSPITAL SANTA CLARA LTDA"),
    ("VERTICE MAO DE OBRA TEMPORARIA LTDA", "METALURGICA CONTAGEM INDUSTRIAL S.A."),
    ("LIMPEZA TOTAL FACILITIES LTDA", "INCORPORADORA ALTO DA SERRA S.A."),
    ("COOPERATIVA DE TRABALHO HORIZONTE", "LOGISTICA SERRA AZUL LTDA"),
]
PESSOAS = ["PESSOA FICTICIA " + s for s in ("UM", "DOIS", "TRES", "QUATRO", "CINCO", "SEIS", "SETE", "OITO", "NOVE", "DEZ")]
ASSUNTOS = ["horas extras", "adicional de insalubridade", "verbas rescisórias", "dano moral", "adicional noturno",
            "equiparação salarial", "rescisão indireta", "intervalo intrajornada", "FGTS", "multa do art. 477 da CLT"]
CAB = "<p>PODER JUDICIÁRIO JUSTIÇA DO TRABALHO TRIBUNAL REGIONAL DO TRABALHO DA {reg}ª REGIÃO</p>"
REG = {"TRT2": "2", "TRT15": "15", "TRT3": "3"}
ADV = [{"advogado": {"nome": "ADVOGADA EXEMPLO", "numero_oab": "123456", "uf_oab": "SP"}}]
_seq = [1002000]


def numero_cnj(ano, tr, vt):
    _seq[0] += R.randint(3, 40)
    nnnnnnn = f"{_seq[0]:07d}"
    base = int(f"{nnnnnnn}{ano}5{tr}{vt}00")
    dd = 98 - (base % 97)
    return f"{nnnnnnn}-{dd:02d}.{ano}.5.{tr}.{vt}"


def item(ident, dias, vara, tipo_com, tipo_doc, classe, proc, texto, dest, advs=()):
    return {"id": ident, "dias_uteis_atras": dias, "siglaTribunal": vara["tribunal"], "tipoComunicacao": tipo_com,
            "tipoDocumento": tipo_doc, "nomeOrgao": vara["vara"], "idOrgao": vara["orgao_id"], "nomeClasse": classe,
            "numeroprocessocommascara": proc, "link": "https://comunica.pje.jus.br/", "texto": CAB.format(reg=REG[vara["tribunal"]]) + texto,
            "destinatarios": dest, "destinatarioadvogados": list(advs)}


def acao_nova(ident, dias, vara, empresas, rito="ord"):
    classe = "AÇÃO TRABALHISTA - RITO ORDINÁRIO" if rito == "ord" else "AÇÃO TRABALHISTA - RITO SUMARÍSSIMO"
    sigla = "ATOrd" if rito == "ord" else "ATSum"
    proc = numero_cnj(2026, vara["tr"], vara["vt"])
    reclamante = R.choice(PESSOAS)
    assuntos = ", ".join(R.sample(ASSUNTOS, R.randint(1, 3)))
    partes = "".join(f" RECLAMADO: {e}" for e in empresas)
    texto = (f"<p>Processo distribuído. {sigla} {proc} RECLAMANTE: {reclamante}{partes}</p>"
             f"<p>Assuntos: {assuntos}. Fica designada audiência inicial, a ser intimada oportunamente.</p>")
    dest = [{"nome": reclamante, "polo": "A"}] + [{"nome": e, "polo": "P"} for e in empresas]
    return item(ident, dias, vara, "Lista de distribuição", "Notificação", classe, proc, texto, dest)


def publicacao_nossa(ident, dias, vara, proc, tipo_doc, texto, cliente):
    classe = "AÇÃO TRABALHISTA - RITO ORDINÁRIO"
    dest = [{"nome": R.choice(PESSOAS), "polo": "A"}, {"nome": cliente, "polo": "P"}]
    return item(ident, dias, vara, "Intimação", tipo_doc, classe, proc, f"<p>ATOrd {proc} RECLAMADO: {cliente}</p>" + texto,
                dest, ADV)


CAJ, BAR, JUN, CON = VARAS
PROC_CLIENTE_1 = "1000123-45.2026.5.02.0221"
PROC_CLIENTE_2 = "1000456-78.2025.5.02.0221"
PROC_CLIENTE_3 = "1000789-10.2026.5.15.0097"
PROC_CLIENTE_4 = "1000555-66.2025.5.03.0030"
CLIENTE_1, CLIENTE_2 = "LOGISTICA SERRA AZUL LTDA", "SUPERMERCADOS HORIZONTE S.A."


_POOL = [e for e in EMPRESAS if e not in (CLIENTE_1, CLIENTE_2)]
R.shuffle(_POOL)
_PARES = [list(p) for p in PARES_TERCEIRIZACAO[1:4] for _ in (0, 1)]  # cada par no máximo 2 vezes
R.shuffle(_PARES)


def lote_acoes(ident0, dias, vara, quantas, forcar=()):
    saida, i = [], ident0
    escolhas = list(forcar)
    while len(escolhas) < quantas:
        if _PARES and R.random() < 0.14:
            escolhas.append(_PARES.pop())
        else:
            # cada empresa sai uma vez; repetição só quando forçada ou nos pares de terceirização
            escolhas.append([_POOL.pop() if _POOL else R.choice(EMPRESAS)])
    for emp in escolhas[:quantas]:
        saida.append(acao_nova(i, dias, vara, emp if isinstance(emp, list) else [emp], "ord" if R.random() < 0.55 else "sum"))
        i += 1
    return saida


rodadas = [
    {"dias_uteis_atras": 1, "hora": "19:15", "modo": "api", "items": (
        lote_acoes(100, 1, CAJ, 12, forcar=[[CLIENTE_1], ["RH PRISMA TERCEIRIZACAO LTDA", CLIENTE_2]]) +
        lote_acoes(200, 1, BAR, 8, forcar=[["ARMAZENS JAGUARI S.A."]]) + [
            publicacao_nossa(301, 1, CAJ, PROC_CLIENTE_1, "Sentença",
                             "<p>SENTENÇA. Vistos etc. Ante o exposto, JULGO PARCIALMENTE PROCEDENTES os pedidos para condenar a "
                             "reclamada ao pagamento de horas extras e reflexos. Prazo de 8 (oito) dias para recurso.</p>", CLIENTE_1),
            publicacao_nossa(302, 1, CAJ, PROC_CLIENTE_2, "Despacho",
                             "<p>DESPACHO. Fica redesignada a audiência de instrução para 10/12/2026 às 10h00, por videoconferência "
                             "(Juízo 100% Digital). Intimem-se as partes e testemunhas.</p>", CLIENTE_1),
            publicacao_nossa(303, 1, BAR, "1000321-09.2026.5.02.0202", "Decisão",
                             "<p>DECISÃO. Defiro o bloqueio de valores via SISBAJUD até o limite da execução. Efetivado o bloqueio, "
                             "intime-se a executada para, querendo, opor embargos no prazo de 5 (cinco) dias.</p>", CLIENTE_2),
        ])},
    {"dias_uteis_atras": 1, "hora": "19:45", "modo": "api", "items": (
        lote_acoes(400, 1, JUN, 10, forcar=[[CLIENTE_1], ["PLASTICOS JUNDIAI INDUSTRIA LTDA"], ["PLASTICOS JUNDIAI INDUSTRIA LTDA"],
                                            ["TRANSPORTES ROTA NORTE LTDA"]]) +
        lote_acoes(500, 1, CON, 7, forcar=[["VERTICE MAO DE OBRA TEMPORARIA LTDA", "METALURGICA CONTAGEM INDUSTRIAL S.A."]]) + [
            publicacao_nossa(601, 1, JUN, PROC_CLIENTE_3, "Despacho",
                             "<p>DESPACHO. Manifeste-se a reclamada sobre o laudo pericial, no prazo de 8 (oito) dias.</p>", CLIENTE_1),
            item(602, 1, {"tribunal": "TRT3", "vara": "5ª Turma - Gabinete Exemplo", "orgao_id": "9900"}, "Intimação", "Intimação",
                 "RECURSO ORDINÁRIO TRABALHISTA", PROC_CLIENTE_4,
                 f"<p>ROT {PROC_CLIENTE_4} RECORRENTE: {CLIENTE_2} RECORRIDO: PESSOA FICTICIA DEZ</p>"
                 "<p>Fica V. Sa. intimado de que o processo foi incluído em pauta de julgamento da sessão telepresencial.</p>",
                 [{"nome": CLIENTE_2, "polo": "A"}], ADV),
        ])},
    {"dias_uteis_atras": 1, "hora": "20:45", "modo": "api", "items": (
        lote_acoes(700, 1, CAJ, 2) + lote_acoes(750, 1, CON, 2, forcar=[["ALIMENTOS BOA MESA LTDA"]]) + [
            publicacao_nossa(801, 1, CAJ, PROC_CLIENTE_1, "Despacho",
                             "<p>DESPACHO. Homologo o acordo celebrado entre as partes para que produza seus efeitos. "
                             "Cumprido o acordo, arquivem-se.</p>", CLIENTE_1),
        ])},
    {"dias_uteis_atras": 0, "hora": "07:00", "modo": "caderno", "items": (
        lote_acoes(900, 1, BAR, 2) + lote_acoes(950, 1, JUN, 1) + [
            publicacao_nossa(1001, 1, CON, "1000900-12.2026.5.03.0030", "Despacho",
                             "<p>DESPACHO. Junte a reclamada os cartões de ponto do período contratual, no prazo de 10 (dez) dias, "
                             "sob as penas da lei.</p>", CLIENTE_2),
        ])},
]

doc = {
    "_leia": "Dia FICTÍCIO de publicações em 3 tribunais, só para demonstrar a página do dia. Nenhum dado real. "
             "Gerado por exemplos/gerar_dia_exemplo.py.",
    "config": {
        "escritorio": "KR Law",
        "alvos": [{k: v[k] for k in ("tribunal", "vara", "orgao_id")} for v in VARAS],
        "monitor": {"oabs": [{"numero": "123456", "uf": "SP", "nome": "Advogada Exemplo"}], "partes_da_carteira": True,
                    "tribunais": ["TRT2", "TRT15", "TRT3"], "dias_para_tras": 3, "radar": True, "dias_na_pagina": 7},
        "enriquecer_cnpj": False,
    },
    "carteira": [CLIENTE_1, CLIENTE_2],
    "processos": [[PROC_CLIENTE_1, CLIENTE_1, "Dra. Exemplo"], [PROC_CLIENTE_2, CLIENTE_1, "Dr. Exemplo"],
                  [PROC_CLIENTE_3, CLIENTE_1, "Dra. Exemplo"], [PROC_CLIENTE_4, CLIENTE_2, "Dr. Exemplo"]],
    "rodadas": rodadas,
}
with open(os.path.join(AQUI, "dia_exemplo.json"), "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=1)
total = sum(len(r["items"]) for r in rodadas)
print(f"dia_exemplo.json: {len(rodadas)} rodadas, {total} publicações")
