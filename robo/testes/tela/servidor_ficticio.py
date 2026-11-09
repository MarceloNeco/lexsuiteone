"""Servidor da tela com dados FICTÍCIOS (nada vai para a nuvem nem para o Diário), para o teste de larguras e prints.
Uso: python servidor_ficticio.py pronto   (porta pela variável PORTA, padrão 8781)."""
import json, os, shutil, sys, tempfile, threading
ROBO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROBO)
from lexsuite import app, conta

def verificar(cfg, versao, hoje=None, pedir=None, retorno=None):
    c = cfg.setdefault("conta", {})
    c.update({"resposta": "ok", "ok": True, "ultima_ok": "2026-11-08", "validade": "", "mensagem": "", "escritorio_licenca": "Escritório Fictício"})
    return c

def cadastrar(cfg, versao, email, nome, doc, papel="", pedir=None, doc_tipo="cnpj"):
    cfg["usuario"].update({"email": email, "nome": nome, "papel": papel})
    return True, ""

conta.verificar, conta.cadastrar = verificar, cadastrar
from lexsuite import atualizar
atualizar.atualizar = lambda *a, **k: {"ok": True, "disponivel": True, "versao": "0.7.12"} if not k.get("instalar_agora", True) else {"ok": False, "motivo": "simulado"}
app.abrir_no_windows = lambda caminho: True
from lexsuite import agendar
agendar.disponivel = lambda: True
agendar.agendado = lambda: True
agendar.agendar = lambda pasta, h=None, d="todos": (True, "Agendado: " + agendar.descricao(h or agendar.PADRAO, d) + ".")
agendar.notificar = lambda *a: True
agendar.migrar_antigas = lambda *a: ""
pasta = tempfile.mkdtemp()
for f in ("radar_modelo.html", "MANUAL-DO-ESCRITORIO.html", "marca.json"):
    if os.path.exists(os.path.join(ROBO, f)):
        shutil.copy(os.path.join(ROBO, f), pasta)
drive = tempfile.mkdtemp()
modo = sys.argv[1] if len(sys.argv) > 1 else "pronto"
if modo == "pronto":
    cfg = {"escritorio": "Escritório Fictício Advocacia", "conta": {"codigo": "LEX-AAAA-BBBB", "instalacao": "0123456789abcdef", "resposta": "ok", "ok": True, "ultima_ok": "2099-01-01"},
           "usuario": {"nome": "Ana Souza Lima", "email": "ana@example.com", "papel": "Advogado ou advogada"},
           "documento_escritorio": {"tipo": "cnpj", "numero": "12345678000195"}, "compartilhar": {"pasta": drive}}
    with open(os.path.join(pasta, "config.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f)
# FICTICIO_LEADS: lista fictícia para ver a tela
if modo == "pronto":
    from lexsuite import banco as bd
    import random, datetime as dt
    random.seed(3)
    b = bd.Banco(os.path.join(pasta, "lexsuite.db"))
    setores = ["Indústria", "Saúde e farmácia", "Serviços e outros", "Varejo e e-commerce"]
    portes = ["MICRO EMPRESA", "EMPRESA DE PEQUENO PORTE", "DEMAIS"]
    hoje = dt.datetime.now()
    for k in range(37):
        dia = (dt.date(2026, 11, 6) - dt.timedelta(days=[0, 1, 4][k % 3])).isoformat()
        lead = {"processo": f"0000{k:03d}-11.2026.5.02.0001", "tribunal": "TRT2", "vara": f"{k % 7 + 1}ª Vara do Trabalho de {'São Paulo' if k % 2 else 'Barueri'}",
                "empresas": [f"Empresa Fictícia {k} Ltda", f"Outra Fictícia {k} S.A."] if k % 3 == 0 else [f"Empresa Fictícia {k} Ltda"],
                "data_publicacao": dia, "visto_em": hoje.isoformat(timespec="seconds"), "valor_causa": None if k % 4 == 0 else random.randint(5, 400) * 1000,
                "classe": "ATOrd", "rito": "Ordinário", "cnpjs": ["11222333000181"],
                "empresa_receita": {"cnpj": "11222333000181", "razao_social": f"EMPRESA FICTICIA {k} LTDA", "porte": portes[k % 3], "municipio": "SAO PAULO" if k % 2 else "BARUERI", "uf": "SP", "atividade": "x"} if k % 5 else {}}
        if k % 5:
            lead["empresa_receita"].update({"telefone": "11 0000-0000" if k % 2 else "", "email": "", "logradouro": "Rua Fictícia", "numero": str(k), "bairro": "Centro", "cep": "01000000"})
        b.guardar_lead(lead, hoje.date().isoformat())
if modo == "pronto":
    b.mudar_situacao([f"0000{k:03d}-11.2026.5.02.0001" for k in (1, 2)], "em_analise")
    b.mudar_situacao(["0000003-11.2026.5.02.0001"], "virou_cliente")
    b.mudar_situacao(["0000004-11.2026.5.02.0001"], "arquivado", motivo="sem interesse")
    b.atualizar_estatisticas()
s = app.Servidor(("127.0.0.1", int(os.environ.get("PORTA", "8781"))), pasta)
print("pronto", s.server_address[1], flush=True)
s.serve_forever()
