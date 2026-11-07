"""Gera exemplos/radar_exemplo.json: um dia FICTÍCIO do Radar SP (TRT2 + TRT15), já no formato da página.

Nada é real: empresas, CNPJs, valores, telefones, e-mails e sócios são inventados. As varas e os
códigos CNAE são reais só para a amostra parecer com o uso de verdade. Rodar: python exemplos/gerar_radar_exemplo.py
"""

import json
import os
import random

AQUI = os.path.dirname(os.path.abspath(__file__))
R = random.Random(15)

VARAS = {
    "TRT2": [("Vara do Trabalho de Cajamar", "0221"), ("2ª Vara do Trabalho de Barueri", "0202"),
             ("5ª Vara do Trabalho de Guarulhos", "0315"), ("3ª Vara do Trabalho de Osasco", "0383"),
             ("1ª Vara do Trabalho de Santos", "0441"), ("12ª Vara do Trabalho de São Paulo", "0012")],
    "TRT15": [("3ª Vara do Trabalho de Jundiaí", "0097"), ("2ª Vara do Trabalho de Campinas", "0032"),
              ("4ª Vara do Trabalho de Sorocaba", "0109"), ("1ª Vara do Trabalho de Piracicaba", "0022"),
              ("2ª Vara do Trabalho de Ribeirão Preto", "0067")],
}
# (razão social fictícia, porte, capital social, CNAE, descrição, município, setor)
EMPRESAS = [
    ("LOGISTICA SERRA AZUL LTDA", "DEMAIS", 8500000, "5211701", "Armazéns gerais - emissão de warrant", "Cajamar", "Logística e transporte"),
    ("TRANSPORTES ROTA NORTE LTDA", "EPP", 1200000, "4930202", "Transporte rodoviário de carga, exceto produtos perigosos e mudanças, intermunicipal, interestadual e internacional", "Guarulhos", "Logística e transporte"),
    ("RH PRISMA TERCEIRIZACAO LTDA", "DEMAIS", 2300000, "7820500", "Locação de mão de obra temporária", "Barueri", "RH e terceirização"),
    ("SUPERMERCADOS HORIZONTE S.A.", "DEMAIS", 45000000, "4711302", "Comércio varejista de mercadorias em geral, com predominância de produtos alimentícios - supermercados", "Osasco", "Varejo e e-commerce"),
    ("HOSPITAL SANTA CLARA LTDA", "DEMAIS", 12000000, "8610101", "Atividades de atendimento hospitalar, exceto pronto-socorro e unidades para atendimento a urgências", "Santos", "Saúde e farmácia"),
    ("GUARDIAO SEGURANCA E VIGILANCIA LTDA", "DEMAIS", 3100000, "8011101", "Atividades de vigilância e segurança privada", "São Paulo", "Segurança, limpeza e facilities"),
    ("CONSTRUTORA VALE VERDE LTDA", "EPP", 900000, "4120400", "Construção de edifícios", "Jundiaí", "Construção e imóveis"),
    ("METALURGICA CAMPINAS INDUSTRIAL S.A.", "DEMAIS", 27000000, "2512800", "Fabricação de esquadrias de metal", "Campinas", "Indústria"),
    ("ALIMENTOS BOA MESA LTDA", "DEMAIS", 6400000, "1091101", "Fabricação de produtos de panificação industrial", "Sorocaba", "Indústria"),
    ("PLASTICOS JUNDIAI INDUSTRIA LTDA", "EPP", 2000000, "2222600", "Fabricação de embalagens de material plástico", "Jundiaí", "Indústria"),
    ("CALL CENTER ATENDE BEM LTDA", "DEMAIS", 5000000, "8220200", "Atividades de teleatendimento", "Barueri", "Serviços e outros"),
    ("FRIGORIFICO BOM PASTO S.A.", "DEMAIS", 38000000, "1011201", "Frigorífico - abate de bovinos", "Piracicaba", "Indústria"),
    ("AUTO PECAS ROTA 300 LTDA", "ME", 150000, "4530703", "Comércio a varejo de peças e acessórios novos para veículos automotores", "Sorocaba", "Varejo e e-commerce"),
    ("CONCESSIONARIA VIA PAULISTA VEICULOS LTDA", "DEMAIS", 9800000, "4511101", "Comércio a varejo de automóveis, camionetas e utilitários novos", "Campinas", "Varejo e e-commerce"),
    ("CLINICA ODONTO SORRISO LTDA", "ME", 80000, "8630504", "Atividade odontológica", "Osasco", "Saúde e farmácia"),
    ("ENGENHARIA PONTE FIRME LTDA", "EPP", 1500000, "4211101", "Construção de rodovias e ferrovias", "Ribeirão Preto", "Construção e imóveis"),
    ("HOTEL JARDIM DAS PALMEIRAS LTDA", "EPP", 700000, "5510801", "Hotéis", "Santos", "Serviços e outros"),
    ("DISTRIBUIDORA DE BEBIDAS GELADA LTDA", "DEMAIS", 4900000, "4635499", "Comércio atacadista de bebidas não especificadas anteriormente", "Guarulhos", "Logística e transporte"),
    ("ACADEMIA CORPO EM FORMA LTDA", "ME", 60000, "9313100", "Atividades de condicionamento físico", "São Paulo", "Serviços e outros"),
    ("EMBALAGENS PAPEL FORTE LTDA", "DEMAIS", 7200000, "1731400", "Fabricação de embalagens de papel", "Piracicaba", "Indústria"),
    ("TELECOM CONECTA BRASIL S.A.", "DEMAIS", 310000000, "6110801", "Serviços de telefonia fixa comutada - STFC", "São Paulo", "Serviços e outros"),
    ("VAREJO NACIONAL EXEMPLO S.A.", "DEMAIS", 2800000000, "4713004", "Lojas de departamentos ou magazines, exceto lojas francas (Duty free)", "São Paulo", "Varejo e e-commerce"),
    ("GRAFICA IMPRESSAO RAPIDA LTDA", "ME", 120000, "1813099", "Impressão de material para outros usos", "Ribeirão Preto", "Serviços e outros"),
    ("ESCOLA NOVO SABER LTDA", "EPP", 400000, "8513900", "Ensino fundamental", "Cajamar", "Serviços e outros"),
    ("LIMPEZA TOTAL FACILITIES LTDA", "DEMAIS", 2600000, "8121400", "Limpeza em prédios e em domicílios", "Barueri", "Segurança, limpeza e facilities"),
    ("COOPERATIVA AGRICOLA DO VALE", "DEMAIS", 15000000, "0113000", "Cultivo de cana-de-açúcar", "Piracicaba", "Indústria"),
    ("FARMACIA VIDA NOVA LTDA", "ME", 90000, "4771701", "Comércio varejista de produtos farmacêuticos, sem manipulação de fórmulas", "Campinas", "Saúde e farmácia"),
    ("TEXTIL ALGODAO DOCE INDUSTRIA LTDA", "EPP", 1800000, "1311100", "Preparação e fiação de fibras de algodão", "Sorocaba", "Indústria"),
]
PESSOAS = ["Pessoa Fictícia " + n for n in ("Alfa", "Beta", "Gama", "Delta", "Épsilon", "Zeta", "Eta", "Teta")]
_seq = [1003000]


def cnpj_ficticio(i):
    base = f"{11000000 + i * 7919:08d}0001"
    def dv(nums, pesos):
        s = sum(int(a) * b for a, b in zip(nums, pesos)) % 11
        return "0" if s < 2 else str(11 - s)
    d1 = dv(base, [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    d2 = dv(base + d1, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    return base + d1 + d2


def numero_cnj(ano, tr, vt):
    _seq[0] += R.randint(3, 60)
    n = f"{_seq[0]:07d}"
    dd = 98 - (int(f"{n}{ano}5{tr}{vt}00") % 97)
    return f"{n}-{dd:02d}.{ano}.5.{tr}.{vt}"


def fmt(m):
    return f"{m:,.0f}".replace(",", ".")


itens = []
ordem = list(range(len(EMPRESAS)))
R.shuffle(ordem)
for k, idx in enumerate(ordem):
    razao, porte, capital, cnae, cnae_desc, cidade, setor = EMPRESAS[idx]
    trib = "TRT2" if cidade in ("Cajamar", "Guarulhos", "Barueri", "Osasco", "Santos", "São Paulo") else "TRT15"
    vara, vt = R.choice([v for v in VARAS[trib] if cidade.split()[-1] in v[0]] or VARAS[trib])
    tr = "02" if trib == "TRT2" else "15"
    rito = "Ordinário" if R.random() < 0.6 or capital > 5000000 else "Sumaríssimo"
    hora = R.choice(["19:12", "19:12", "19:12", "19:41", "19:41", "20:35"]) if trib == "TRT2" else R.choice(["19:41", "19:41", "20:35"])
    valor = None
    if rito == "Ordinário" and R.random() < 0.6:
        valor = R.choice([68000, 84500, 97200, 112000, 128400, 143750, 158000, 176300, 190000, 215000, 248000, 275900, 312000, 356000, 418000, 480000])
    elif rito == "Sumaríssimo" and R.random() < 0.5:
        valor = R.choice([21000, 28500, 33200, 38900, 44000, 52300, 58700])
    socios = [{"nome": R.choice(PESSOAS), "qualificacao": "Administrador"}, {"nome": R.choice(PESSOAS), "qualificacao": "Sócio"}]
    itens.append({
        "id": numero_cnj(2026, tr, vt), "hora": hora, "visto_em": f"2026-10-22T{hora}:00", "tribunal": trib, "vara": vara,
        "processo": None, "classe": "AÇÃO TRABALHISTA - RITO " + ("ORDINÁRIO" if rito == "Ordinário" else "SUMARÍSSIMO"),
        "rito": rito, "distribuida_em": "2026-10-22", "empresas": [razao],
        "empresa": {"cnpj": cnpj_ficticio(idx), "razao_social": razao, "nome_fantasia": "", "porte": porte,
                    "porte_legivel": {"ME": "Microempresa (até R$ 360 mil/ano)", "EPP": "Pequena (até R$ 4,8 milhões/ano)",
                                      "DEMAIS": "Média ou grande (acima de R$ 4,8 milhões/ano)"}[porte],
                    "capital_social": capital, "cnae": cnae, "atividade": cnae_desc, "cnaes_secundarios": [],
                    "municipio": cidade, "uf": "SP", "telefone": f"11 5555-{R.randint(1000, 9999)}" if trib == "TRT2" else f"19 5555-{R.randint(1000, 9999)}",
                    "telefone2": "", "email": "contato@" + razao.split()[0].lower() + ".exemplo.com.br",
                    "socios": socios, "simples": porte in ("ME", "EPP"), "inicio_atividade": f"{R.randint(1995, 2021)}-0{R.randint(1, 9)}-15"},
        "setor": setor, "gigante": capital >= 50000000,
        "valor_causa": valor, "valor_fonte": "djen" if valor else "",
        "link_djen": "https://comunica.pje.jus.br/", "link_pje": f"https://pje.{trib.lower()}.jus.br/consultaprocessual/",
    })
for it in itens:
    it["processo"] = it["id"]
# um par de terceirização, como acontece de verdade
itens[3]["empresas"] = [itens[3]["empresas"][0], "RH PRISMA TERCEIRIZACAO LTDA"]
itens.sort(key=lambda i: (-(i["valor_causa"] or 0), i["visto_em"]))
doc = {
    "_leia": "Dia FICTÍCIO do Radar SP, só para demonstrar a página. Nenhum dado real. Gerado por exemplos/gerar_radar_exemplo.py.",
    "dia": "2026-10-22", "gerado_em": "2026-10-22 20:40", "exemplo": True, "escritorio": "KR Law",
    "tribunais": ["TRT2", "TRT15"], "valor_minimo": 100000,
    "situacao": {"pt": "Lista de distribuição do DJEN lida às 19:12, 19:41 e 20:35. Receita consultada para todas as empresas.",
                 "en": "DJEN distribution lists read at 19:12, 19:41 and 20:35. Federal registry checked for every company."},
    "itens": itens,
}
with open(os.path.join(AQUI, "radar_exemplo.json"), "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=1)
print(f"radar_exemplo.json: {len(itens)} ações, {sum(1 for i in itens if (i['valor_causa'] or 0) >= 100000)} acima de R$ 100 mil")
