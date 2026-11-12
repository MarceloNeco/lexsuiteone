"""Servidor da tela com dados FICTÍCIOS para o roteiro aviso_e_lupa.sh (aviso de planilha em uso, lupa offline, /dados com Infinity e NaN).
Uso: python servidor_aviso.py ROBO TRAB PORTA (o aviso_e_lupa.sh sobe vários, cada um na sua porta).
Variáveis: EM_USO=1 (a planilha parece aberta em outro lugar), SEM_EXCEL=1 (sem Excel), CURTO=ZETA (outra marca),
RADAR_RAW='"valor_minimo": Infinity, ...' (trecho do config.json a mão), SAIDA=1 (grava saida/radar/radar.html, a página offline)."""
import os, sys, json, shutil, stat, subprocess, datetime as dt
sys.dont_write_bytecode = True
ROBO, W, porta = sys.argv[1], sys.argv[2], int(sys.argv[3])
sys.path.insert(0, ROBO)
from lexsuite import app, atualizar, agendar, conta, compartilhar, banco as bd, radar, VERSAO
atualizar.atualizar = lambda *a, **k: {"ok": True, "disponivel": False, "versao": VERSAO}
agendar.disponivel = lambda: True; agendar.agendado = lambda: True
agendar.agendar = lambda pasta, h=None, d="todos": (True, "Agendado.")
agendar.notificar = lambda *a: True; agendar.migrar_antigas = lambda *a: ""
def verificar(cfg, versao, hoje=None, pedir=None, retorno=None):
    c = cfg.setdefault("conta", {}); c.update({"resposta": "ok", "ok": True, "ultima_ok": "2026-11-10", "validade": "", "mensagem": "", "escritorio_licenca": "Escritório Fictício"}); return c
conta.verificar = verificar
if os.environ.get('EM_USO'):
    from lexsuite import planilha as _pl
    _pl.marcar_se_livre = lambda c: False
compartilhar.candidatas = lambda: [os.path.join(W, 'Meu Drive')]
LOG = os.path.join(W, f"abrir_{porta}.log")
def ro(p): return not (os.stat(p).st_mode & stat.S_IWUSR)
def start(c):
    open(LOG, "a").write(json.dumps({"fn": "startfile", "caminho": c, "existe": os.path.exists(c)}) + "\n"); return os.path.exists(c)
app.abrir_no_windows = start
app.excel_exe = (lambda: "") if os.environ.get("SEM_EXCEL") else (lambda: "/bin/true")
subprocess.Popen = lambda args, **k: open(LOG, "a").write(json.dumps({"fn": "excel", "args": list(args)[1:]}) + "\n") and None
pasta = os.path.join(W, f"prog_{porta}"); os.makedirs(pasta, exist_ok=True)
drive = os.path.join(W, f"drive_{porta}"); os.makedirs(drive, exist_ok=True)
raw = os.environ.get("RADAR_RAW", '"dias_para_tras": 1')
txt = ('{"escritorio": "Escritório Fictício Advocacia", "conta": {"codigo": "LEX-AAAA-BBBB", "instalacao": "0123456789abcdef", "resposta": "ok", "ok": true, "ultima_ok": "2099-01-01"},'
       ' "usuario": {"nome": "Ana Souza Lima", "email": "ana@example.com", "papel": "Advogado ou advogada"}, "documento_escritorio": {"tipo": "cnpj", "numero": "12345678000195"},'
       ' "compartilhar": {"pasta": %s}, "radar": {"tribunais": ["TRT2", "TRT15"], %s}}') % (json.dumps(drive), raw)
open(os.path.join(pasta, "config.json"), "w", encoding="utf-8").write(txt)
for f in ("radar_modelo.html", "MANUAL-DO-ESCRITORIO.html", "marca.json"):
    if os.path.exists(os.path.join(ROBO, f)): shutil.copy(os.path.join(ROBO, f), pasta)
if os.environ.get("CURTO"):
    json.dump({"nome": "ZETA JUDICIAL", "curto": os.environ["CURTO"], "destaque": "IA"}, open(os.path.join(pasta, "marca.json"), "w"))
b = bd.Banco(os.path.join(pasta, "lexsuite.db"))
hoje = dt.datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)  # revisão da 0.7.32: relativo a hoje (o período conta pela data do Diário)
for k in range(12):
    lead = {"processo": f"0000{k:03d}-11.2026.5.02.0001", "tribunal": "TRT2", "vara": f"{k % 7 + 1}ª Vara do Trabalho de São Paulo", "empresas": [f"Empresa Fictícia {k} Ltda"],
            "data_publicacao": hoje.date().isoformat(), "visto_em": hoje.isoformat(timespec="seconds"), "valor_causa": 50000 + k * 10000, "classe": "ATOrd", "rito": "Ordinário", "cnpjs": ["11222333000181"], "empresa_receita": {}}
    b.guardar_lead(lead, hoje.date().isoformat())
c2 = json.loads(open(os.path.join(pasta, "config.json"), encoding="utf-8").read().replace("Infinity", "0").replace("NaN", "0"))
compartilhar.criar_se_faltar(c2, VERSAO, ROBO, lambda *a: None)
if os.environ.get("SAIDA"):
    c3 = json.loads(open(os.path.join(pasta, "config.json"), encoding="utf-8").read())
    radar.gravar_saida(c3, b, os.path.join(pasta, "saida", "radar"), hoje, {"pt": "x", "en": "x"}, lambda *a: None, VERSAO)
s = app.Servidor(("127.0.0.1", porta), pasta)
s.estado.situacao = {"pt": "3 ações novas contra empresas", "en": "3 new lawsuits against companies", "quando": "2026-11-10T07:10:00", "lidas": 120, "novas": 3}
print("pronto", porta, flush=True)
s.serve_forever()
