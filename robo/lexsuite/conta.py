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
    "aceite_pendente": "Falta o aceite dos termos pelo responsável do escritório.",
}


def _aceite(a):
    """Bloco `aceite` da resposta da SolverONE (lex-conta v8): {aceito, versao, aceito_em, nome} ou {aceito: False, link}.
    O link só vale se for do site da SolverONE (https)."""
    if not isinstance(a, dict):
        return {}
    link = str(a.get("link") or "")
    if not re.match(r"^https://([a-z0-9-]+\.)*solverone\.com\.br/", link):
        link = ""
    return {"aceito": bool(a.get("aceito")), "versao": str(a.get("versao") or "")[:20], "aceito_em": str(a.get("aceito_em") or "")[:25],
            "nome": str(a.get("nome") or "")[:120], "link": link[:500]}
CONTATO = "judicial@solverone.com.br"


def _termos(t):
    """Bloco `termos` da lex-conta (v10+): {escritorio: {...}, pessoa: {...}} com a versão vigente, o link e o aceite.
    0.7.16: a Configuração mostra as duas camadas. A trava da pessoa ainda não é pedida (`suporta_aceite_uso` não é
    enviado): liga quando a página dos termos estiver publicada e o dono responder a pergunta 13 do quadro."""
    if not isinstance(t, dict):
        return {}
    saida = {}
    for camada in ("escritorio", "pessoa"):
        b = t.get(camada)
        if not isinstance(b, dict):
            continue
        link = str(b.get("link") or "")
        if not re.match(r"^https://([a-z0-9-]+\.)*solverone\.com\.br/", link):
            link = ""
        saida[camada] = {"versao_vigente": str(b.get("versao_vigente") or "")[:20], "link": link[:500],
                         "aceito": bool(b.get("aceito")), "versao": str(b.get("versao") or "")[:20],
                         "aceito_em": str(b.get("aceito_em") or "")[:25], "fuso": str(b.get("fuso") or "")[:40],
                         "nome": str(b.get("nome") or "")[:120], "precisa_aceitar": bool(b.get("precisa_aceitar"))}
    return saida


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


def verificar(cfg, versao, hoje=None, pedir=None, retorno=None):
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
        corpo = {"codigo": codigo, "instalacao": c["instalacao"], "versao": versao}
        if retorno:  # 0.7.14: só quantidades por situação (sem nome, processo, CNPJ ou contato); a Configuração mostra
            corpo["retorno"] = list(retorno)[:2000]
        r = pedir(c.get("url") or URL_PADRAO, corpo, tentativas=2, tempo_limite=20)
    except Exception as e:  # sem internet, serviço fora do ar, resposta estranha: decide pela última resposta boa
        c.update({"resposta": "sem_resposta", "erro": e.__class__.__name__})
        return c
    if not isinstance(r, dict):
        c.update({"resposta": "sem_resposta", "erro": "resposta inválida"})
        return c
    c.pop("erro", None)
    if retorno and isinstance(r.get("retorno"), dict):
        c["retorno_resposta"] = {"gravadas": int(r["retorno"].get("gravadas") or 0), "recusadas": int(r["retorno"].get("recusadas") or 0),
                                 "quando": hoje.isoformat()}
    c["ok"] = bool(r.get("ok"))
    c["resposta"] = "ok" if c["ok"] else str(r.get("motivo") or "desativado")[:40]
    c["escritorio_licenca"] = str(r.get("escritorio") or "")[:80]
    c["validade"] = str(r.get("validade") or "")[:10]
    c["mensagem"] = str(r.get("mensagem") or "")[:300]
    if "aceite" in r:
        c["aceite"] = _aceite(r.get("aceite"))
    if "termos" in r:
        c["termos"] = _termos(r.get("termos"))
    if isinstance(r.get("recursos"), dict):  # 0.7.20: interruptores do RootifyONE (Controle dos apps), pela lex-conta v12
        c["recursos"] = {str(k)[:60]: bool(v) for k, v in list(r["recursos"].items())[:50] if isinstance(v, (bool, int))}
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


MOTIVOS_EN = {
    "codigo_desconhecido": "This client code does not exist. Check the code in the welcome e-mail.",
    "desativado": "This firm\u2019s licence is deactivated.",
    "vencido": "This firm\u2019s licence has expired.",
    "codigo_invalido": "The client code has the format LEX-XXXX-XXXX (see the welcome e-mail).",
    "aceite_pendente": "The firm\u2019s representative still has to accept the terms.",
}


def bloqueio_en(cfg, hoje=None):
    """0.7.23 (revisão): o mesmo motivo de `bloqueio`, em inglês, para a tela em EN. A mensagem da SolverONE vai como veio."""
    if not bloqueio(cfg, hoje):
        return ""
    c = cfg.get("conta") or {}
    msg = (" " + c["mensagem"]) if c.get("mensagem") else ""
    fale = f" Contact {CONTATO}."
    codigo = normalizar(c.get("codigo"))
    if not codigo:
        return "The client code is missing (it is in the welcome e-mail). Enter it in Settings."
    if not valido(codigo):
        return MOTIVOS_EN["codigo_invalido"]
    resposta = c.get("resposta") or ""
    if resposta not in ("", "ok", "sem_resposta"):
        return (MOTIVOS_EN.get(resposta, "This firm\u2019s licence is not active.") + msg + fale).strip()
    if not c.get("ultima_ok"):
        return ("I could not confirm the client code with SolverONE yet. Check the internet and try again." + fale).strip()
    return (f"For more than {DIAS_SEM_RESPOSTA} days I could not confirm the licence with SolverONE. Check the internet and try again." + fale).strip()


def situacao(cfg):
    """Para a tela: {'codigo', 'ok', 'texto'}."""
    c = cfg.get("conta") or {}
    motivo = bloqueio(cfg)
    if motivo:
        pend = c.get("resposta") == "aceite_pendente"
        return {"codigo": c.get("codigo", ""), "ok": False, "texto": motivo, "texto_en": bloqueio_en(cfg) or motivo,
                "aceite": c.get("aceite") or {},
                "aceite_link": ((c.get("aceite") or {}).get("link") or "") if pend else "", "termos": c.get("termos") or {},
                "escritorio": c.get("escritorio_licenca", ""), "validade": c.get("validade", ""), "recursos": c.get("recursos") or {}}
    texto, texto_en = "Licença ativa.", "Licence active."  # 0.7.21: a validade aparece em linha própria na tela, no idioma escolhido
    if c.get("resposta") == "sem_resposta":
        texto = f"Licença confirmada pela última vez em {c.get('ultima_ok')}; sem resposta da SolverONE agora."
        texto_en = f"Licence last confirmed on {c.get('ultima_ok')}; no answer from SolverONE right now."
    return {"codigo": c.get("codigo", ""), "ok": True, "texto": texto, "texto_en": texto_en, "aceite": c.get("aceite") or {}, "aceite_link": "",
            "termos": c.get("termos") or {}, "escritorio": c.get("escritorio_licenca", ""), "validade": c.get("validade", ""),
            "recursos": c.get("recursos") or {}}


# ---------- cadastro de quem usa (nome, e-mail, função) e do escritório (CNPJ) ----------
# O e-mail é a chave: um e-mail pertence a um escritório só. A mesma pessoa em outro computador do mesmo
# escritório reaproveita o cadastro. Os dados servem para a SolverONE falar com quem usa sobre o serviço.
MOTIVOS.update({
    "email_em_outro_escritorio": "Este e-mail já está cadastrado em outro escritório. Use o e-mail do escritório ou fale com " + CONTATO + ".",
    "dados_invalidos": "Confira o documento do escritório (CNPJ, CPF ou passaporte), o seu nome e o seu e-mail.",
    "limite_de_pessoas": "Esta licença já tem o número máximo de pessoas cadastradas. Fale com " + CONTATO + ".",
})
_EMAIL = re.compile(r"^[^@\s]{1,64}@[^@\s]+\.[^@\s]{2,}$")


def so_digitos(texto):
    return re.sub(r"\D", "", str(texto or ""))


def _dv_cnpj(base):
    """Dígito verificador do CNPJ, numérico ou alfanumérico (Receita, a partir de jul/2026): valor = código ASCII - 48."""
    pesos = list(range(len(base) - 7, 1, -1)) + list(range(9, 1, -1))
    resto = sum((ord(c) - 48) * p for c, p in zip(base, pesos)) % 11
    return "0" if resto < 2 else str(11 - resto)


def limpar_cnpj(cnpj):
    return re.sub(r"[^0-9A-Z]", "", str(cnpj or "").upper())


def cnpj_valido(cnpj):
    """CNPJ com 14 posições: as 12 primeiras com números ou letras (formato novo), as 2 últimas números (dígitos)."""
    d = limpar_cnpj(cnpj)
    if not re.fullmatch(r"[0-9A-Z]{12}[0-9]{2}", d) or d == d[0] * 14:
        return False
    return d[12] == _dv_cnpj(d[:12]) and d[13] == _dv_cnpj(d[:13])


def cpf_valido(cpf):
    d = so_digitos(cpf)
    if len(d) != 11 or d == d[0] * 11:
        return False
    for n in (9, 10):
        resto = sum(int(d[i]) * (n + 1 - i) for i in range(n)) * 10 % 11
        if str(resto % 10) != d[n]:
            return False
    return True


def documento(tipo, valor):
    """Documento do titular da licença, normalizado, ou '' se inválido. tipo: cnpj, cpf (sem CNPJ) ou passaporte."""
    if tipo == "cnpj":
        return limpar_cnpj(valor) if cnpj_valido(valor) else ""
    if tipo == "cpf":
        return so_digitos(valor) if cpf_valido(valor) else ""
    if tipo == "passaporte":
        p = re.sub(r"[^0-9A-Z]", "", str(valor or "").upper())
        return p if 5 <= len(p) <= 20 else ""
    return ""


def email_valido(email):
    return bool(_EMAIL.match(str(email or "").strip())) and len(str(email).strip()) <= 120


def cadastrar(cfg, versao, email, nome, doc, papel="", pedir=None, doc_tipo="cnpj", aceite_uso=None):
    """Registra quem usa esta instalação na licença do escritório. Devolve (ok, motivo)."""
    c = _bloco(cfg)
    email = str(email or "").strip().lower()
    nome = " ".join(str(nome or "").split())[:60]
    doc_tipo = doc_tipo if doc_tipo in ("cnpj", "cpf", "passaporte") else "cnpj"
    doc = documento(doc_tipo, doc)
    if not (email_valido(email) and nome and doc):
        return False, MOTIVOS["dados_invalidos"]
    pedir = pedir or rede.pedir_json
    corpo = {"acao": "cadastrar", "codigo": normalizar(c.get("codigo")), "instalacao": c["instalacao"], "versao": versao,
             "email": email, "nome": nome, "papel": str(papel or "")[:40], "doc_tipo": doc_tipo, "documento": doc}
    if isinstance(aceite_uso, dict) and aceite_uso.get("versao"):  # 0.7.16: a caixa "Li e aceito os termos de uso" marcada
        corpo["aceite_uso"] = {"versao": str(aceite_uso["versao"])[:20], "fuso": str(aceite_uso.get("fuso") or "")[:40]}
    try:
        r = pedir(c.get("url") or URL_PADRAO, corpo, tentativas=2, tempo_limite=20)
    except Exception:
        return False, "Não consegui falar com a SolverONE para registrar o cadastro. Confira a internet e tente de novo."
    if not isinstance(r, dict) or not r.get("ok"):
        motivo = str((r or {}).get("motivo") or "") if isinstance(r, dict) else ""
        return False, MOTIVOS.get(motivo, "A SolverONE recusou o cadastro.") + ("" if motivo in MOTIVOS else f" Fale com {CONTATO}.")
    cfg.setdefault("usuario", {}).update({"email": email, "nome": nome, "papel": str(papel or "")[:40]})
    cfg["documento_escritorio"] = {"tipo": doc_tipo, "numero": doc}
    c["cadastrado"] = email
    if "termos" in r:
        c["termos"] = _termos(r.get("termos"))
    return True, ""


# ---------- registro técnico de erro, para diagnóstico ----------
def _sem_caminho_pessoal(texto):
    """Tira do texto a pasta do usuário do Windows (que traz o nome da pessoa)."""
    import os
    t = str(texto or "")
    for pasta in {os.path.expanduser("~"), os.environ.get("USERPROFILE", ""), os.environ.get("LOCALAPPDATA", "")}:
        if pasta and len(pasta) > 3:
            t = t.replace(pasta, "~").replace(pasta.replace("\\", "/"), "~")
    return re.sub(r"(?i)([a-z]:[\\/]+users[\\/]+)[^\\/\"']+", r"\1~", t)


def registrar_erro(cfg, versao, etapa, mensagem, pedir=None):
    """Envia à SolverONE um registro técnico de erro (etapa, versão, Windows, mensagem sem caminhos pessoais).
    Nunca levanta exceção e nunca atrasa o programa mais que alguns segundos."""
    import platform
    c = (cfg or {}).get("conta") or {}
    corpo = {"acao": "registro", "origem": "programa", "etapa": str(etapa)[:60], "versao": str(versao)[:20],
             "mensagem": _sem_caminho_pessoal(mensagem)[:2000], "windows": f"{platform.system()} {platform.release()} {platform.version()}"[:80],
             "instalacao": c.get("instalacao", ""), "codigo": normalizar(c.get("codigo"))}
    try:
        (pedir or rede.pedir_json)(c.get("url") or URL_PADRAO, corpo, tentativas=1, tempo_limite=10)
        return True
    except Exception:
        return False
