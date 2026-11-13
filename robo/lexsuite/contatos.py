"""Completar os contatos das empresas pela área logada do PJe (desenho dos contatos, Arquitetura 08/Nov; itens 40, 41 e 59).

1. "Preparar busca de contatos" gera um arquivo Markdown com as instruções e a tabela dos processos sem contato (no
   máximo N por dia, padrão 30: há tribunal que bloqueia quem abre muitos processos de terceiros).
2. O advogado, logado no PJe, entrega o arquivo ao Claude in Chrome (opcional: dá para preencher à mão).
3. "Trazer dados da área logada" (antes "Colar contatos encontrados") lê a tabela Markdown de 8 colunas, sem IA, linha a linha, e recusa o que não pode
   entrar (CPF, reclamante, canal desconhecido, processo que não está na lista).
"""

import datetime as dt
import os
import re

CANAIS = ("telefone", "email", "site", "endereco", "linkedin", "instagram", "outro")
FONTES = ("Receita", "PJe dados do processo", "PJe petição inicial", "PJe citação", "site da empresa", "outro")  # 0.7.45: "dados do processo" (Arquitetura)
COLUNAS = ("processo", "empresa", "canal", "valor", "de_pessoa", "fonte", "data", "observacao")
_CPF = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b|\bcpf\b", re.I)
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

## Formato da resposta (copie e cole de volta no {produto}: menu ☰, "Área logada" → "Trazer dados da área logada")

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


def _cpf_valido(d):
    if len(d) != 11 or d == d[0] * 11:
        return False
    for n in (9, 10):
        soma = sum(int(d[i]) * (n + 1 - i) for i in range(n))
        if (soma * 10 % 11) % 10 != int(d[n]):
            return False
    return True


def _tem_cpf_valido(cels, canal):
    """Sequência de 11 dígitos (com ou sem pontuação) que é um CPF válido. No canal telefone, o valor (celular com DDD
    também tem 11 dígitos) não é conferido; as outras colunas são."""
    for k, cel in enumerate(cels):
        if k == 3 and canal == "telefone":
            continue
        for m in re.finditer(r"\d[\d.\-\s]{9,16}\d", cel):
            d = re.sub(r"\D", "", m.group(0))
            if _cpf_valido(d):
                return True
    return False


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
        elif _CPF.search(" ".join(cels)) or _tem_cpf_valido(cels, canal):
            motivo = "tem CPF (não pode entrar)"
        elif any(re.search(r"\b" + re.escape(p) + r"\b", junto) for p in _PROIBIDO):
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


# --- 0.7.16: "RESPOSTA PARA O RADAR v1" (item 91; formato em docs/VISITA-KR-LAW.md) ----------------------------------
# A extensão de IA que o escritório usar (qualquer fornecedor) devolve este bloco; o RADAR lê sem IA, linha a linha.

CABECALHO_V1 = "RESPOSTA PARA O RADAR v1"
DADOS_V1 = ("valor_causa", "data_ajuizamento", "telefone", "email", "site", "endereco", "socio_contato", "outro")
RESULTADOS_V1 = ("encontrado", "nao_consta", "tentar_depois")
_CANAL_DO_DADO = {"telefone": "telefone", "email": "email", "site": "site", "endereco": "endereco", "socio_contato": "outro", "outro": "outro"}

# 0.7.45 (Arquitetura, 13/Nov, mapa real do PJe do TRT2; o do TRT15 usa a mesma interface "pjekz"): o prompt v2, que a
# extensão Claude in Chrome segue na área logada do advogado. Os processos vêm agrupados por tribunal.
PEDIDO_V1 = """# Pedido de dados ao PJe ({data}) · {produto}

Como usar: no Chrome, com o PJe do tribunal (1º grau) **já logado** pelo advogado (painel "Meu Painel - PJE"), abra o Claude
in Chrome e cole este arquivo inteiro. Quando terminar, copie o bloco "{cabecalho}" e cole no {produto}: menu ☰,
"Área logada" → "Trazer dados da área logada".

```
Você está na aba do PJe (1º grau) do tribunal dos processos abaixo, já logado como advogado (painel "Meu Painel - PJE").
Trabalhe SÓ nesta aba, SÓ LEITURA, no máximo {limite} processos nesta sessão, um de cada vez, e devolva no fim a tabela
"{cabecalho}". Se a lista tiver processos de mais de um tribunal, faça só os do tribunal desta aba e devolva os
outros como tentar_depois, observação "outro tribunal". Procure SÓ os dados da coluna "falta", SÓ da empresa ré indicada
(confira pelo CNPJ).

NUNCA (cada um destes anula o trabalho):
- abrir a tela de login do PJe (endereço terminado em /primeirograu/login.seam) nem qualquer tela de login (derruba a sessão);
- clicar em "Baixar processo completo", "Baixar processo por instância" ou "Baixar documentos filtrados";
- abrir "Meus Expedientes", "Visualizar Expediente", "Detalhar Expediente" nem o ícone de envelope de uma intimação (pode
  registrar ciência e abrir prazo);
- clicar em Peticionar, Responder, Apresentação de Renúncia, Solicitação de Habilitação, Novo Processo ou em qualquer botão
  que grave, assine ou envie;
- anotar dado do reclamante, de testemunha, de perito, de preposto ou de advogado (de qualquer lado); anotar CPF; anotar
  dado de outra empresa que não a da lista.

ROTEIRO POR PROCESSO:
1. No painel, campo "Entre com o número do processo para consulta": digite o número CNJ e Enter. Se a lista ficar vazia,
   o processo não está no acervo do advogado: devolva todas as linhas dele como tentar_depois, com observação "fora do
   acervo", e passe ao próximo (não use "Consulta Processos de Terceiros").
2. Clique no número do processo (abre o endereço .../pjekz/processo/<id>/detalhe). Pode abrir esse endereço nesta mesma
   aba. Nunca volte pelo histórico para a tela de login.
3. No cabeçalho do processo leia "Valor da causa:" (dado valor_causa; fonte "PJe dados do processo") e "Distribuído:"
   (dado data_ajuizamento, formato aaaa-mm-dd; mesma fonte).
4. Clique no número do processo no cabeçalho: abre "Dados do processo". Em "Polo Passivo", ache a empresa com o CNPJ da
   lista. Na linha depois do CNPJ está o endereço cadastrado (dado endereco) e, entre parênteses "(email: …)", o e-mail
   (dado email). Fonte: "PJe dados do processo". Ignore tudo em "Polo Ativo" e os blocos dos advogados. Feche a janela (×).
5. Se ainda faltar telefone, e-mail, site ou endereço: na linha do tempo, ative a ordenação ascendente (ícone de setas) e abra
   o PRIMEIRO documento, "Petição Inicial". Se ele abrir como texto (HTML), leia só o parágrafo que qualifica a empresa ré
   ("em face de … inscrita no CNPJ … requerendo seja notificada na …"): endereço, telefone, e-mail, site da EMPRESA
   (fonte "PJe petição inicial"; para endereço vindo daqui, observação "a conferir"). Se o documento abrir como PDF dentro da
   página e o texto não for selecionável, não baixe: devolva os dados que faltam como tentar_depois, observação "petição
   em PDF". Se a inicial citar sócio ou administrador DA EMPRESA com telefone ou e-mail, devolva como socio_contato
   (valor = "Nome do sócio: canal"); nunca CPF.
6. Se ainda faltar endereço: abra o segundo documento, "Notificação" (da ré), e leia o campo "DESTINATÁRIO:" (fonte "PJe
   citação"). Não clique no ícone de envelope "Visualizar Expedientes".
7. Volte ao painel pelo menu lateral "Meu Painel" (nunca pelo endereço de login) e passe ao próximo processo.

SE A TELA MOSTRAR "Acesso Negado", "É preciso logar" ou "SJT-004": pare. Devolva o que já tem e marque o resto como
tentar_depois, observação "sessão expirou".

RESPOSTA: no fim, devolva SÓ este bloco, uma linha para cada dado da coluna "falta" de cada processo (nunca invente;
"nao_consta" quando leu o lugar certo e não havia):

{cabecalho}
| processo | dado | valor | resultado | fonte | data | observação |
|---|---|---|---|---|---|---|

- dado: valor_causa, data_ajuizamento, telefone, email, site, endereco, socio_contato, outro
- resultado: encontrado, nao_consta ou tentar_depois
- fonte: PJe dados do processo, PJe petição inicial, PJe citação ou outro
- data: aaaa-mm-dd de hoje · valor_causa só números com vírgula (105000,00) · data_ajuizamento aaaa-mm-dd
```

## Processos ({n})

| processo | tribunal | empresa ré | CNPJ | falta |
|---|---|---|---|---|
{linhas}
"""


def faltando(item):
    """O que falta num processo da lista, na ordem em que vale procurar."""
    e = item.get("empresa") or {}
    falta = []
    if not item.get("valor_causa"):
        falta.append("valor_causa")
    if not item.get("ajuizada_em"):
        falta.append("data_ajuizamento")
    canais = set((item.get("contato") or {}).get("canais") or [])
    for d in ("telefone", "email", "endereco"):
        if d not in canais and not (d == "endereco" and e.get("logradouro")):
            falta.append(d)
    return falta


def preparar_v1(itens, pasta, produto="RADAR JUDICIAL", limite=30, hoje=None):
    """Grava saida/contatos/pedido-pje-AAAA-MM-DD.md com até `limite` processos e, em cada um, só o que falta."""
    hoje = hoje or dt.date.today()
    escolhidos = [(i, faltando(i)) for i in itens]
    escolhidos = [(i, f) for i, f in escolhidos if f][: max(1, int(limite))]
    escolhidos.sort(key=lambda x: str(x[0].get("tribunal") or ""))  # 0.7.45: um tribunal de cada vez (uma aba do PJe por tribunal)
    linhas = "\n".join(
        f"| {_cel(i.get('processo'))} | {_cel(i.get('tribunal'))} | "
        f"{_cel((i.get('empresa') or {}).get('razao_social') or (i.get('empresas') or [''])[0])} | "
        f"{_cel((i.get('empresa') or {}).get('cnpj') or i.get('cnpj_a_conferir'))} | {', '.join(f)} |" for i, f in escolhidos)
    texto = PEDIDO_V1.format(data=hoje.strftime("%d/%m/%Y"), produto=produto, limite=int(limite), cabecalho=CABECALHO_V1,
                             n=len(escolhidos), linhas=linhas or "| (nenhum processo com dado faltando) | | | | |")
    destino = os.path.join(pasta, "saida", "contatos")
    os.makedirs(destino, exist_ok=True)
    caminho = os.path.join(destino, f"pedido-pje-{hoje.isoformat()}.md")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)
    return caminho, len(escolhidos), texto


def _valor_v1(dado, valor):
    """Valor normalizado do dado, ou None se estiver fora do formato."""
    v = valor.strip()
    if dado == "valor_causa":
        t = re.sub(r"[R$\s]", "", v)
        if "," in t:
            t = t.replace(".", "").replace(",", ".")
        try:
            n = float(t)
        except ValueError:
            return None
        return n if 0 < n < 1e11 else None
    if dado == "data_ajuizamento":
        m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", v) or re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", v)
        if not m:
            return None
        a, b, c = m.groups()
        iso = f"{a}-{b}-{c}" if len(a) == 4 else f"{c}-{b}-{a}"
        try:
            dt.date.fromisoformat(iso)
        except ValueError:
            return None
        return iso
    canal = _CANAL_DO_DADO[dado]
    return v if v and _valor_ok(canal, v) else None


_UFS = ("AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ",
        "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO")


def uf_do_endereco(endereco):
    """0.7.18: a UF no fim de um endereço ("... São Paulo/SP", "... - SP, 01001-000", "..., SP"), ou ''."""
    achadas = re.findall(r"(?:^|[\s/,\-–(])(" + "|".join(_UFS) + r")(?=$|[\s,.;)\-–/]|\d)", str(endereco or "").upper())
    return achadas[-1] if achadas else ""


def e_resposta_v1(texto):
    return CABECALHO_V1.lower() in str(texto or "").lower()


def colar_v1(texto, empresas_por_processo, hoje=None):
    """Lê o bloco "RESPOSTA PARA O RADAR v1". Devolve {contatos, completar, nao_consta, tentar_depois, recusadas}:
    contatos = no formato de colar(); completar = [{processo, campo, valor, fonte, data}] (valor da causa e data de
    ajuizamento); nao_consta e tentar_depois = [{processo, dado}]; recusadas = [{linha, motivo, texto}]."""
    hoje = hoje or dt.date.today()
    saida = {"contatos": [], "completar": [], "nao_consta": [], "tentar_depois": [], "recusadas": []}
    for n, bruta in enumerate(str(texto or "").splitlines()[:3000], 1):
        linha = bruta.strip()
        if not linha.startswith("|"):
            continue
        cels = [c.strip() for c in linha.strip("|").split("|")]
        if len(cels) < 4 or set("".join(cels)) <= set("-: ") or cels[0].lower() == "processo":
            continue
        cels = (cels + [""] * 7)[:7]
        proc, dado, valor, resultado, fonte, data, obs = cels
        proc = re.sub(r"[^\d.\-]", "", proc)
        dado = cl_sem_acento(dado).lower().replace("-", "_").replace(" ", "_")
        resultado = cl_sem_acento(resultado).lower().replace(" ", "_").replace("-", "_")
        data = data if re.fullmatch(r"\d{4}-\d{2}-\d{2}", data) else hoje.isoformat()
        junto = " ".join(cels).lower()
        motivo = ""
        if proc not in empresas_por_processo:
            motivo = "processo que não está na sua lista / lawsuit not in your list"
        elif dado not in DADOS_V1:
            motivo = f"dado desconhecido / unknown field: {dado[:30]}"
        elif resultado not in RESULTADOS_V1:
            motivo = f"resultado desconhecido / unknown result: {resultado[:30]}"
        elif _CPF.search(" ".join(cels)) or _tem_cpf_valido([proc, "", "", valor if dado != "telefone" else "", fonte, data, obs], "outro"):
            motivo = "tem CPF (não pode entrar) / contains a personal tax ID"
        elif any(re.search(r"\b" + re.escape(p) + r"\b", junto) for p in _PROIBIDO):
            motivo = "parece dado do autor, de testemunha ou de advogado da outra parte / looks like data about the plaintiff or a witness"
        if not motivo and resultado == "encontrado":
            normal = _valor_v1(dado, valor)
            if normal is None:
                motivo = "valor vazio ou fora do formato / empty or malformed value"
            elif not fonte:
                motivo = "falta a fonte / source missing"
        if motivo:
            saida["recusadas"].append({"linha": n, "motivo": motivo, "texto": linha[:160]})
            continue
        if resultado != "encontrado":
            saida[resultado].append({"processo": proc, "dado": dado})
            continue
        if dado in ("valor_causa", "data_ajuizamento"):
            saida["completar"].append({"processo": proc, "campo": dado, "valor": normal, "fonte": fonte[:80], "data": data})
            continue
        if dado == "endereco" and uf_do_endereco(normal):  # o painel e os filtros passam a ter o estado da empresa
            saida["completar"].append({"processo": proc, "campo": "uf", "valor": uf_do_endereco(normal), "fonte": fonte[:80], "data": data})
        # 0.7.45 (Arquitetura): o cadastro da parte ("PJe dados do processo") vale mais; endereço "a conferir" (da petição)
        # entra marcado assim
        conf = "alta" if cl_sem_acento(fonte).lower().startswith("pje dados do processo") else "media"
        if dado == "endereco" and "a conferir" in cl_sem_acento(obs).lower():
            conf = "baixa"
        saida["contatos"].append({"processo": proc, "empresa": empresas_por_processo[proc], "canal": _CANAL_DO_DADO[dado],
                                  "valor": str(normal)[:300], "de_pessoa": dado == "socio_contato", "fonte": fonte[:80],
                                  "data": data, "confianca": conf, "origem": "área logada", "observacao": obs[:300]})
    return saida


def cl_sem_acento(s):
    from . import classificar as cl
    return cl.sem_acento(str(s or ""))
