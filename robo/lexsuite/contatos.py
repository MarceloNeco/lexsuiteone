"""Completar os contatos das empresas pela área logada do PJe (desenho dos contatos, Arquitetura 08/Nov; itens 40, 41 e 59).

1. "Preparar busca de contatos" gera um arquivo Markdown com as instruções e a tabela dos processos sem contato (no
   máximo N por dia, padrão 30: há tribunal que bloqueia quem abre muitos processos de terceiros).
2. O advogado, logado no PJe, entrega o arquivo ao Claude in Chrome (opcional: dá para preencher à mão).
3. "Colar contatos encontrados" lê a tabela Markdown de 8 colunas, sem IA, linha a linha, e recusa o que não pode
   entrar (CPF, reclamante, canal desconhecido, processo que não está na lista).
"""

import datetime as dt
import os
import re

CANAIS = ("telefone", "email", "site", "endereco", "linkedin", "instagram", "outro")
FONTES = ("Receita", "PJe petição inicial", "PJe citação", "site da empresa", "outro")
COLUNAS = ("processo", "empresa", "canal", "valor", "de_pessoa", "fonte", "data", "observacao")
_CPF = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
_CNPJ = re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")
_PROIBIDO = ("reclamante", "autor", "autora", "testemunha", "preposto", "advogado da parte", "advogada da parte")
_ALIAS_CANAL = {"e-mail": "email", "mail": "email", "fone": "telefone", "tel": "telefone", "celular": "telefone",
                "whatsapp": "telefone", "endereço": "endereco", "outros": "outro", "web": "site", "linkedIn": "linkedin"}

INSTRUCOES = """# Busca de contatos na área logada do PJe ({data})

Arquivo gerado pelo {produto}. Quem abre os processos é o advogado, logado no PJe com a credencial dele. Abra no
máximo {limite} processos por dia (há tribunal que bloqueia quem abre muitos processos de terceiros).

## O que fazer (Claude in Chrome ou à mão)

Para cada processo da tabela abaixo, na aba do PJe já logada:
1. Abra o processo pelo número.
2. Leia **só** a petição inicial e, se houver, a certidão de citação.
3. Anote os canais de contato da **empresa ré** (a da coluna "empresa") e dos sócios ou administradores dela:
   telefone, e-mail, site, endereço, LinkedIn, Instagram ou outro canal.
4. **Nunca** anote dado do reclamante, de testemunha, de preposto ou de advogado da outra parte. **Nunca** anote CPF.
5. Só leitura: não clique em nada que peticione, assine ou altere o processo.

## Formato da resposta (copie e cole de volta no {produto}, em "Colar contatos encontrados")

Responda **só** com uma tabela Markdown com estas 8 colunas, uma linha por canal encontrado:

| processo | empresa | canal | valor | de_pessoa | fonte | data | observação |
|---|---|---|---|---|---|---|---|
| 0000000-00.2026.5.15.0000 | Empresa Exemplo Ltda | telefone | (19) 0000-0000 | não | PJe petição inicial | {hoje} | exemplo fictício |

- canal: telefone, email, site, endereco, linkedin, instagram ou outro
- de_pessoa: "sim" quando o contato é de um sócio ou administrador; "não" quando é da empresa
- fonte: PJe petição inicial, PJe citação, site da empresa ou outro
- data: o dia em que você consultou (aaaa-mm-dd)
- Se não achar nada para um processo, não escreva linha para ele.

## Processos ({n})

| processo | tribunal | vara | empresa | CNPJ |
|---|---|---|---|---|
{linhas}
"""


def _cel(x):
    return str(x or "").replace("|", "/").replace("\n", " ").strip()


def preparar(itens, pasta, produto="RADAR JUDICIAL", limite=30, hoje=None):
    """Grava saida/contatos/buscar-contatos-AAAA-MM-DD.md com até `limite` processos sem contato. Devolve (caminho, n)."""
    hoje = hoje or dt.date.today()
    escolhidos = [i for i in itens if not (i.get("contato") or {}).get("tem")][: max(1, int(limite))]
    linhas = "\n".join(
        f"| {_cel(i.get('processo'))} | {_cel(i.get('tribunal'))} | {_cel(i.get('vara'))} | "
        f"{_cel((i.get('empresa') or {}).get('razao_social') or (i.get('empresas') or [''])[0])} | "
        f"{_cel((i.get('empresa') or {}).get('cnpj') or i.get('cnpj_a_conferir'))} |" for i in escolhidos)
    texto = INSTRUCOES.format(data=hoje.strftime("%d/%m/%Y"), produto=produto, limite=int(limite), hoje=hoje.isoformat(),
                              n=len(escolhidos), linhas=linhas or "| (nenhum processo sem contato) | | | | |")
    destino = os.path.join(pasta, "saida", "contatos")
    os.makedirs(destino, exist_ok=True)
    caminho = os.path.join(destino, f"buscar-contatos-{hoje.isoformat()}.md")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)
    return caminho, len(escolhidos)


def _valor_ok(canal, valor):
    v = valor.strip()
    if canal == "telefone":
        return len(re.sub(r"\D", "", v)) >= 10
    if canal == "email":
        return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", v) is not None
    if canal in ("site", "linkedin", "instagram"):
        return re.search(r"[a-z0-9-]+\.[a-z]{2,}", v.lower()) is not None or v.startswith("@")
    return len(v) >= 3


def colar(texto, empresas_por_processo, hoje=None):
    """Lê a tabela Markdown colada. Devolve (aceitas, recusadas): aceitas = [contato], recusadas = [{linha, motivo}].
    `empresas_por_processo`: {processo: nome da empresa} dos processos que o escritório tem na lista."""
    from . import classificar as cl
    hoje = hoje or dt.date.today()
    aceitas, recusadas = [], []
    for n, bruta in enumerate(str(texto or "").splitlines()[:2000], 1):
        linha = bruta.strip()
        if not linha.startswith("|"):
            continue
        cels = [c.strip() for c in linha.strip("|").split("|")]
        if len(cels) < 7 or set("".join(cels)) <= set("-: ") or cels[0].lower() == "processo":
            continue
        cels = (cels + [""] * 8)[:8]
        reg = dict(zip(COLUNAS, cels))
        motivo = ""
        canal = _ALIAS_CANAL.get(reg["canal"].lower(), reg["canal"].lower())
        proc = re.sub(r"[^\d.\-]", "", reg["processo"])
        junto = " ".join(cels).lower()
        if proc not in empresas_por_processo:
            motivo = "processo que não está na sua lista"
        elif _CPF.search(" ".join(cels)) and not _CNPJ.search(" ".join(cels)):
            motivo = "tem CPF (não pode entrar)"
        elif any(p in junto for p in _PROIBIDO):
            motivo = "parece dado de reclamante, testemunha, preposto ou advogado da outra parte"
        elif canal not in CANAIS:
            motivo = f"canal desconhecido: {reg['canal'][:30]}"
        elif not reg["valor"] or not _valor_ok(canal, reg["valor"]):
            motivo = "valor vazio ou fora do formato"
        elif reg["de_pessoa"].lower() in ("sim", "s", "yes") and not reg["fonte"]:
            motivo = "contato de pessoa sem a fonte"
        if motivo:
            recusadas.append({"linha": n, "motivo": motivo, "texto": linha[:160]})
            continue
        empresa = empresas_por_processo[proc]
        aviso = "" if not reg["empresa"] or cl.nomes_batem(reg["empresa"], empresa) else f" (empresa na resposta: {reg['empresa'][:60]})"
        data = reg["data"] if re.fullmatch(r"\d{4}-\d{2}-\d{2}", reg["data"]) else hoje.isoformat()
        aceitas.append({"processo": proc, "empresa": empresa, "canal": canal, "valor": reg["valor"].strip()[:300],
                        "de_pessoa": reg["de_pessoa"].lower() in ("sim", "s", "yes"), "fonte": reg["fonte"][:80] or "outro",
                        "data": data, "confianca": "media", "origem": "área logada", "observacao": (reg["observacao"] + aviso)[:300]})
    return aceitas, recusadas
