"""Licença do escritório: o código de cliente (LEX-XXXX-XXXX) conferido na nuvem da SolverONE.

Como funciona:
- O código vem no e-mail de boas-vindas e é pedido no primeiro passo da tela. Ele identifica o escritório; não é
  senha e não dá acesso a dado nenhum.
- A cada abertura da tela e antes de cada leitura, o programa pergunta à SolverONE se a licença continua ativa
  (função `lex-conta` do Supabase; nenhuma chave no programa). A resposta fica guardada no config.json.
- Bloqueia quando: não há código; a SolverONE respondeu que o código não existe, está desativado ou venceu; ou faz
  mais de DIAS_SEM_RESPOSTA dias que não há resposta da SolverONE (internet fora ou serviço fora do ar).
- Sem resposta por menos tempo, segue rodando com a última resposta boa: uma queda do nosso lado não para o
  escritório.
Limite honesto: quem controla o computador controla o programa; isto é controle de serviço, não trava contra
quem altera o código.
"""
import datetime as dt
import re
import secrets

from . import rede

URL_PADRAO = "https://qvdvkqydhnadhewcidia.supabase.co/functions/v1/lex-conta"
DIAS_SEM_RESPOSTA = 15
# Sem 0/O e 1/I, para não confundir ao digitar.
FORMATO = re.compile(r"^LEX-[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}$")
MOTIVOS = {
    "codigo_desconhecido": "Este código de cliente não existe. Confira o código no e-mail de boas-vindas.",
    "desativado": "A licença deste escritório está desativada.",
    "vencido": "A licença deste escritório venceu.",
    "codigo_invalido": "O código de cliente tem o formato LEX-XXXX-XXXX (veja o e-mail de boas-vindas).",
}
CONTATO = "judicial@solverone.com.br"


def normalizar(codigo):
    c = re.sub(r"[^A-Z0-9]", "", str(codigo or "").upper())
    return f"{c[:3]}-{c[3:7]}-{c[7:11]}" if len(c) == 11 and c.startswith("LEX") else str(codigo or "").strip().upper()


def valido(codigo):
    return bool(FORMATO.match(normalizar(codigo)))


def _bloco(cfg):
    c = cfg.setdefault("conta", {})
    if not isinstance(c, dict):
        cfg["conta"] = c = {}
    if not c.get("instalacao"):
        c["instalacao"] = secrets.token_hex(8)  # identifica esta instalação nos registros da SolverONE; nada pessoal
    return c


def verificar(cfg, versao, hoje=None, pedir=None):
    """Pergunta à SolverONE e guarda a resposta em cfg['conta']. Devolve o bloco atualizado.
    `pedir` existe para os testes; por padrão é rede.pedir_json."""
    c = _bloco(cfg)
    hoje = hoje or dt.date.today()
    codigo = normalizar(c.get("codigo"))
    c["codigo"] = codigo
    c["verificado_em"] = hoje.isoformat()
    if not valido(codigo):
        c.update({"resposta": "codigo_invalido" if codigo else "sem_codigo", "ok": False})
        return c
    pedir = pedir or rede.pedir_json
    try:
        r = pedir(c.get("url") or URL_PADRAO, {"codigo": codigo, "instalacao": c["instalacao"], "versao": versao},
                  tentativas=2, tempo_limite=20)
    except Exception as e:  # sem internet, serviço fora do ar, resposta estranha: decide pela última resposta boa
        c.update({"resposta": "sem_resposta", "erro": e.__class__.__name__})
        return c
    if not isinstance(r, dict):
        c.update({"resposta": "sem_resposta", "erro": "resposta inválida"})
        return c
    c.pop("erro", None)
    c["ok"] = bool(r.get("ok"))
    c["resposta"] = "ok" if c["ok"] else str(r.get("motivo") or "desativado")[:40]
    c["escritorio_licenca"] = str(r.get("escritorio") or "")[:80]
    c["validade"] = str(r.get("validade") or "")[:10]
    c["mensagem"] = str(r.get("mensagem") or "")[:300]
    if c["ok"]:
        c["ultima_ok"] = hoje.isoformat()
    return c


def bloqueio(cfg, hoje=None):
    """Motivo para não rodar, ou '' quando pode. Usa só o que já está guardado (não vai à internet)."""
    c = cfg.get("conta") or {}
    hoje = hoje or dt.date.today()
    msg = (" " + c["mensagem"]) if c.get("mensagem") else ""
    fale = f" Fale com {CONTATO}."
    codigo = normalizar(c.get("codigo"))
    if not codigo:
        return "Falta o código de cliente (está no e-mail de boas-vindas). Informe em Configuração."
    if not valido(codigo):
        return MOTIVOS["codigo_invalido"]
    resposta = c.get("resposta") or ""
    if resposta not in ("", "ok", "sem_resposta"):
        return (MOTIVOS.get(resposta, "A licença deste escritório não está ativa.") + msg + fale).strip()
    if resposta == "ok":
        return ""
    try:
        ultima = dt.date.fromisoformat(str(c.get("ultima_ok") or "")[:10])
    except ValueError:
        ultima = None
    if ultima is None:
        return ("Ainda não consegui confirmar o código de cliente com a SolverONE. Confira a internet e tente de novo."
                + fale).strip()
    if (hoje - ultima).days > DIAS_SEM_RESPOSTA:
        return (f"Faz mais de {DIAS_SEM_RESPOSTA} dias que não consigo confirmar a licença com a SolverONE."
                " Confira a internet e tente de novo." + fale).strip()
    return ""


def situacao(cfg):
    """Para a tela: {'codigo', 'ok', 'texto'}."""
    c = cfg.get("conta") or {}
    motivo = bloqueio(cfg)
    if motivo:
        return {"codigo": c.get("codigo", ""), "ok": False, "texto": motivo}
    texto = "Licença ativa" + (f" até {c['validade']}" if c.get("validade") else "") + "."
    if c.get("resposta") == "sem_resposta":
        texto = f"Licença confirmada pela última vez em {c.get('ultima_ok')}; sem resposta da SolverONE agora."
    return {"codigo": c.get("codigo", ""), "ok": True, "texto": texto}


# ---------- cadastro de quem usa (nome, e-mail, função) e do escritório (CNPJ) ----------
# O e-mail é a chave: um e-mail pertence a um escritório só. A mesma pessoa em outro computador do mesmo
# escritório reaproveita o cadastro. Os dados servem para a SolverONE falar com quem usa sobre o serviço.
MOTIVOS.update({
    "email_em_outro_escritorio": "Este e-mail já está cadastrado em outro escritório. Use o e-mail do escritório ou fale com " + CONTATO + ".",
    "dados_invalidos": "Confira o CNPJ do escritório, o seu nome e o seu e-mail.",
})
_EMAIL = re.compile(r"^[^@\s]{1,64}@[^@\s]+\.[^@\s]{2,}$")


def so_digitos(texto):
    return re.sub(r"\D", "", str(texto or ""))


def cnpj_valido(cnpj):
    d = so_digitos(cnpj)
    if len(d) != 14 or d == d[0] * 14:
        return False
    def dv(base, pesos):
        resto = sum(int(a) * b for a, b in zip(base, pesos)) % 11
        return "0" if resto < 2 else str(11 - resto)
    p1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    return d[12] == dv(d[:12], p1) and d[13] == dv(d[:13], [6] + p1)


def email_valido(email):
    return bool(_EMAIL.match(str(email or "").strip())) and len(str(email).strip()) <= 120


def cadastrar(cfg, versao, email, nome, cnpj, papel="", pedir=None):
    """Registra quem usa esta instalação na licença do escritório. Devolve (ok, motivo)."""
    c = _bloco(cfg)
    email = str(email or "").strip().lower()
    nome = " ".join(str(nome or "").split())[:60]
    if not (email_valido(email) and nome and cnpj_valido(cnpj)):
        return False, MOTIVOS["dados_invalidos"]
    pedir = pedir or rede.pedir_json
    corpo = {"acao": "cadastrar", "codigo": normalizar(c.get("codigo")), "instalacao": c["instalacao"], "versao": versao,
             "email": email, "nome": nome, "papel": str(papel or "")[:40], "cnpj": so_digitos(cnpj)}
    try:
        r = pedir(c.get("url") or URL_PADRAO, corpo, tentativas=2, tempo_limite=20)
    except Exception:
        return False, "Não consegui falar com a SolverONE para registrar o cadastro. Confira a internet e tente de novo."
    if not isinstance(r, dict) or not r.get("ok"):
        motivo = str((r or {}).get("motivo") or "") if isinstance(r, dict) else ""
        return False, MOTIVOS.get(motivo, "A SolverONE recusou o cadastro.") + ("" if motivo in MOTIVOS else f" Fale com {CONTATO}.")
    cfg.setdefault("usuario", {}).update({"email": email, "nome": nome, "papel": str(papel or "")[:40]})
    cfg["cnpj_escritorio"] = so_digitos(cnpj)
    c["cadastrado"] = email
    return True, ""
