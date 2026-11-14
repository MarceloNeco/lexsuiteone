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

# 0.7.45/0.7.46 (Arquitetura, mapa real do PJe do TRT2; o do TRT15 usa a mesma interface "pjekz"): o prompt v2, que a
# ferramenta de navegação (Claude in Chrome, Codex ou outra) segue na área logada do advogado. 0.7.46: em lotes de 25,
# um bloco de resposta por lote; roteiro dos TRTs (mapa pjekz) e roteiro genérico para os outros tribunais.
PEDIDO_V1 = """# Pedido de dados ao PJe ({data}) · {produto} · {lotes_txt}

Como usar: no Chrome, com o PJe do tribunal (1º grau) **já logado** pelo advogado (painel "Meu Painel - PJE"), abra a
ferramenta de navegação (Claude in Chrome, Codex ou outra) e cole este texto inteiro. Quando ela terminar, copie os blocos
"{cabecalho}" (ou salve o arquivo que ela gerar) e traga para o {produto}: menu ☰, "Área logada" → "Trazer resposta".

```
Você está na aba do PJe (1º grau) do tribunal dos processos abaixo, já logado como advogado (painel "Meu Painel - PJE").
Trabalhe SÓ nesta aba, SÓ LEITURA, nos {n} processos das tabelas "Processos" abaixo ({lotes_txt}), um de cada vez.
Se a lista tiver processos de mais de um tribunal, faça só os do tribunal desta aba e devolva os outros como tentar_depois,
observação "outro tribunal". Procure SÓ os dados da coluna "falta", SÓ da empresa ré indicada (confira pelo CNPJ).

NUNCA (cada um destes anula o trabalho):
- abrir a tela de login do PJe (endereço terminado em /primeirograu/login.seam) nem qualquer tela de login (derruba a sessão);
- clicar em "Baixar processo completo", "Baixar processo por instância" ou "Baixar documentos filtrados";
- abrir "Meus Expedientes", "Visualizar Expediente", "Detalhar Expediente" nem o ícone de envelope de uma intimação (pode
  registrar ciência e abrir prazo);
- clicar em Peticionar, Responder, Apresentação de Renúncia, Solicitação de Habilitação, Novo Processo ou em qualquer botão
  que grave, assine ou envie;
- anotar dado do reclamante, de testemunha, de perito, de preposto ou de advogado (de qualquer lado); anotar CPF; anotar
  dado de outra empresa que não a da lista.
{roteiro}
SE A TELA MOSTRAR "Acesso Negado", "É preciso logar" ou "SJT-004": pare. Devolva o que já tem e marque o resto como
tentar_depois, observação "sessão expirou".

RESPOSTA: termine um lote antes de começar o próximo. Ao terminar CADA lote, devolva SÓ o bloco dele, com o cabeçalho
"RESPOSTA PARA O RADAR v1 · lote N de {m}", uma linha para cada dado da coluna "falta" de cada processo do lote (nunca
invente; "nao_consta" quando leu o lugar certo e não havia). Se a sua ferramenta oferecer "baixar como arquivo", salve cada
bloco como resposta-radar-lote-N.md; senão, deixe os blocos inteiros na tela para copiar.

{cabecalho} · lote 1 de {m}
| processo | dado | valor | resultado | fonte | data | observação |
|---|---|---|---|---|---|---|

- dado: valor_causa, data_ajuizamento, telefone, email, site, endereco, socio_contato, outro
- resultado: encontrado, nao_consta ou tentar_depois
- fonte: PJe dados do processo, PJe petição inicial, PJe citação ou outro
- data: aaaa-mm-dd de hoje · valor_causa só números com vírgula (105000,00) · data_ajuizamento aaaa-mm-dd
```
{tabelas}"""

ROTEIRO_TRT = """
ROTEIRO POR PROCESSO (Justiça do Trabalho, PJe "pjekz"):
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
7. Volte ao painel pelo menu lateral "Meu Painel" (nunca pelo endereço de login) e passe ao próximo processo. Um processo
   por vez, sem abrir várias janelas.
"""

ROTEIRO_GENERICO = """
ROTEIRO POR PROCESSO (outros tribunais; esta tela ainda não foi mapeada pela SolverONE):
1. Use a busca do painel do advogado pelo número CNJ (nunca a consulta de processos de terceiros). Processo que não aparece
   no acervo do advogado: devolva as linhas dele como tentar_depois, observação "fora do acervo".
2. Nos dados do processo (cabeçalho ou "Dados do processo"): valor da causa e data de distribuição/ajuizamento; nas partes,
   SÓ a empresa ré com o CNPJ da lista: endereço e e-mail cadastrados. Fonte "PJe dados do processo".
3. Se ainda faltar contato da empresa: a petição inicial, só se abrir como texto, só o parágrafo que qualifica a empresa ré
   (fonte "PJe petição inicial"; endereço daqui com observação "a conferir"). PDF sem texto: tentar_depois, "petição em PDF".
4. Nunca baixe documentos, nunca abra intimação/expediente, nunca clique em botão que grave ou envie.
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
    for d in ("telefone", "email", "endereco", "site"):  # 0.7.46: site também (a petição às vezes traz)
        if d not in canais and not (d == "endereco" and e.get("logradouro")) and not (d == "telefone" and e.get("telefone")) \
                and not (d == "email" and e.get("email")):
            falta.append(d)
    return falta


def lotes_de(n, tam=25):
    return max(1, -(-int(n) // int(tam))) if n else 0


def preparar_v1(itens, pasta, produto="RADAR JUDICIAL", limite=25, hoje=None, dados=None, faltas=None, ident=None):
    """Grava saida/contatos/pedido-pje-AAAA-MM-DD[-id].md com até `limite` processos (lotes de 25) e, em cada um, só o que
    falta (ou `faltas` {processo: [dados]} já calculadas). `dados`: quais tipos pedir (valor, data, contato, socio; None =
    o padrão). Devolve (caminho, n, texto); a lista final e as faltas ficam em preparar_v1.ultimo."""
    hoje = hoje or dt.date.today()
    if faltas is None:
        escolhidos = [(i, filtrar_falta(faltando(i), dados)) for i in itens]
    else:
        escolhidos = [(i, list(faltas.get(i.get("processo"), []))) for i in itens]
    escolhidos = [(i, f) for i, f in escolhidos if f][: max(1, int(limite))]
    escolhidos.sort(key=lambda x: (str(x[0].get("tribunal") or ""), str(x[0].get("processo") or "")))  # um tribunal de cada vez
    m = lotes_de(len(escolhidos))
    def linha(i, f):
        return (f"| {_cel(i.get('processo'))} | {_cel(i.get('tribunal'))} | "
                f"{_cel((i.get('empresa') or {}).get('razao_social') or (i.get('empresas') or [''])[0])} | "
                f"{_cel((i.get('empresa') or {}).get('cnpj') or i.get('cnpj_a_conferir'))} | {', '.join(f)} |")
    tabelas = []
    for k in range(m):
        parte = escolhidos[k * LOTE_TAM:(k + 1) * LOTE_TAM]
        tabelas.append(f"\n## Processos · lote {k + 1} de {m} ({len(parte)} de {len(escolhidos)})\n\n"
                       "| processo | tribunal | empresa ré | CNPJ | falta |\n|---|---|---|---|---|\n" + "\n".join(linha(i, f) for i, f in parte))
    if not escolhidos:
        tabelas.append("\n## Processos (0)\n\n| processo | tribunal | empresa ré | CNPJ | falta |\n|---|---|---|---|---|\n| (nenhum processo com dado faltando) | | | | |")
    tribs = {str(i.get("tribunal") or "").upper() for i, _ in escolhidos}
    roteiro = (ROTEIRO_TRT if any(t.startswith("TRT") for t in tribs) or not tribs else "") + \
              (ROTEIRO_GENERICO if any(t and not t.startswith("TRT") for t in tribs) else "")
    lotes_txt = "lote único" if m <= 1 else f"{m} lotes de até {LOTE_TAM}"
    texto = PEDIDO_V1.format(data=hoje.strftime("%d/%m/%Y"), produto=produto, cabecalho=CABECALHO_V1, n=len(escolhidos),
                             m=max(1, m), lotes_txt=lotes_txt, roteiro=roteiro, tabelas="\n".join(tabelas) + "\n")
    destino = os.path.join(pasta, "saida", "contatos")
    os.makedirs(destino, exist_ok=True)
    caminho = os.path.join(destino, f"pedido-pje-{hoje.isoformat()}" + (f"-{ident}" if ident else "") + ".md")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)
    preparar_v1.ultimo = {"processos": [i.get("processo") for i, _ in escolhidos], "faltas": {i.get("processo"): f for i, f in escolhidos}, "lotes": m}
    return caminho, len(escolhidos), texto


DADOS_GRUPOS = {"valor": ("valor_causa",), "data": ("data_ajuizamento",), "contato": ("telefone", "email", "endereco", "site"),
                "socio": ("socio_contato",)}


def filtrar_falta(falta, dados=None):
    """0.7.46: só os tipos de dado escolhidos no passo 1 (padrão: valor, data e contatos; sócio só se pedido)."""
    dados = dados if dados is not None else {"valor": True, "data": True, "contato": True, "socio": False}
    quero = {d for g, on in dados.items() if on for d in DADOS_GRUPOS.get(g, ())}
    saida = [d for d in falta if d in quero]
    if dados.get("socio") and saida and "socio_contato" not in saida:
        saida.append("socio_contato")  # sócio só junto de outro dado que falta (não abre processo só para isso)
    return saida


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

# --- 0.7.46 (Área logada v2, Arquitetura 14/Nov): vários blocos, lotes, arquivo, colunas pelo nome -------------------------

LOTE_TAM = 25  # processos por lote do pedido
LIMITE_PEDIDO = (25, 50)  # padrão e máximo por pedido (cada pedido é uma sessão do PJe; não há limite por dia)
ARQ_MAX = 20 * 1024 * 1024
_CAB_V1 = re.compile(r"resposta\s+para\s+o\s+radar\s+v1(?:\W+lote\s+(\d+)\s+de\s+(\d+))?", re.I)
_NOMES_COL = {"processo": "processo", "dado": "dado", "valor": "valor", "resultado": "resultado", "fonte": "fonte", "data": "data",
              "observacao": "obs", "observação": "obs", "obs": "obs"}


def ler_arquivo(nome, conteudo):
    """Texto de um arquivo enviado: .md/.txt, ou .zip com .md/.txt dentro (só lido em memória, nada é extraído nem executado).
    Levanta ValueError com o motivo em PT/EN."""
    import io
    import zipfile
    nome = str(nome or "").lower()
    if len(conteudo or b"") > ARQ_MAX:
        raise ValueError("Arquivo maior que 20 MB. / File larger than 20 MB.")
    def texto_de(b):
        for cod in ("utf-8-sig", "cp1252", "latin-1"):
            try:
                return b.decode(cod)
            except UnicodeDecodeError:
                continue
        return b.decode("utf-8", "replace")
    if nome.endswith((".md", ".txt", ".markdown")):
        return texto_de(conteudo)
    if nome.endswith(".zip"):
        try:
            z = zipfile.ZipFile(io.BytesIO(conteudo))
        except zipfile.BadZipFile:
            raise ValueError("O .zip está corrompido. / The .zip is corrupted.")
        partes, total = [], 0
        membros = sorted((i for i in z.infolist() if not i.is_dir() and i.filename.lower().endswith((".md", ".txt", ".markdown"))),
                         key=lambda i: i.filename)
        if not membros:
            raise ValueError("O .zip não tem arquivo .md nem .txt. / The .zip has no .md or .txt file.")
        import zlib
        for i in membros[:50]:
            total += i.file_size
            if total > ARQ_MAX:  # zip-bomba: confere o tamanho descompactado antes de ler
                raise ValueError("O conteúdo do .zip passa de 20 MB. / The .zip content exceeds 20 MB.")
            try:
                with z.open(i) as f:
                    partes.append(texto_de(f.read(ARQ_MAX + 1)))
            except (RuntimeError, NotImplementedError, zlib.error, OSError, zipfile.BadZipFile, EOFError):
                # revisão: zip com senha, compressão que a biblioteca padrão não lê ou arquivo danificado
                raise ValueError("O .zip não pôde ser lido (senha, formato ou arquivo danificado). / The .zip could not be read.")
        return "\n\n".join(partes)
    raise ValueError("Use um arquivo .md, .txt ou .zip. / Use a .md, .txt or .zip file.")


def blocos_v1(texto):
    """Todos os blocos "RESPOSTA PARA O RADAR v1" do texto, em qualquer ordem e com qualquer conversa em volta.
    Cada bloco: {lote, de, linhas: [(nº da linha no texto, {coluna: valor}, texto da linha)], extras: bool}. A tabela do bloco
    acaba na primeira linha que não começa com "|" depois de ela ter começado. As colunas são lidas pelo NOME do cabeçalho
    (coluna a mais é ignorada); sem cabeçalho reconhecível, pela posição."""
    linhas = str(texto or "").splitlines()[:20000]
    blocos, atual = [], None
    for n, bruta in enumerate(linhas, 1):
        linha = bruta.strip()
        m = _CAB_V1.search(linha) if not linha.startswith("|") else None
        if m:
            atual = {"lote": int(m.group(1)) if m.group(1) else None, "de": int(m.group(2)) if m.group(2) else None,
                     "linhas": [], "mapa": None, "extras": False, "comecou": False}
            blocos.append(atual)
            continue
        if atual is None:
            continue
        if not linha.startswith("|"):
            if atual["comecou"]:
                atual = None  # a tabela terminou: o resto até o próximo cabeçalho é conversa
            continue
        atual["comecou"] = True
        cels = [c.strip() for c in linha.strip("|").split("|")]
        if set("".join(cels)) <= set("-: "):
            continue
        normal = [cl_sem_acento(c).lower().strip() for c in cels]
        if atual["mapa"] is None and "processo" in normal and "dado" in normal:
            atual["mapa"] = {k: _NOMES_COL[c] for k, c in enumerate(normal) if c in _NOMES_COL}
            atual["extras"] = len(atual["mapa"]) < len(cels)
            continue
        mapa = atual["mapa"] or {0: "processo", 1: "dado", 2: "valor", 3: "resultado", 4: "fonte", 5: "data", 6: "obs"}
        reg = {v: (cels[k] if k < len(cels) else "") for k, v in mapa.items()}
        atual["linhas"].append((n, reg, linha))
    for b in blocos:
        b.pop("mapa", None); b.pop("comecou", None)
    return blocos


def inicio_do_texto(texto, n=3):
    """As primeiras linhas não vazias, para a pessoa conferir se colou a coisa certa."""
    return [l.strip()[:160] for l in str(texto or "").splitlines() if l.strip()][:n]


def ler_resposta(texto, empresas_por_processo, hoje=None):
    """0.7.46: lê TODOS os blocos v1 (lotes em qualquer ordem), linha a linha, sem IA. Mesmo resultado de colar_v1 e mais:
    `lotes` [{lote, de, aceitas, recusadas, repetidas, extras}], `linhas` (cada linha válida: processo, dado, resultado, fonte,
    valor normalizado), `achou` (algum bloco) e `inicio` (3 primeiras linhas, quando não achou). Linha igual em dois lotes
    conta uma vez."""
    hoje = hoje or dt.date.today()
    saida = {"contatos": [], "completar": [], "nao_consta": [], "tentar_depois": [], "recusadas": [], "lotes": [], "linhas": [],
             "repetidas": 0, "achou": False, "inicio": []}
    blocos = blocos_v1(texto)
    if not blocos:
        saida["inicio"] = inicio_do_texto(texto)
        return saida
    saida["achou"] = True
    vistos = set()
    for b in sorted(blocos, key=lambda x: (x["lote"] or 0)):
        st = {"lote": b["lote"], "de": b["de"], "aceitas": 0, "recusadas": 0, "repetidas": 0, "extras": b["extras"]}
        for n, reg, linha in b["linhas"]:
            cels = [reg.get(k, "") for k in ("processo", "dado", "valor", "resultado", "fonte", "data", "obs")]
            if not any(cels):
                continue
            r = colar_v1("RESPOSTA PARA O RADAR v1\n| " + " | ".join(c.replace("|", "/") for c in cels) + " |", empresas_por_processo, hoje)
            if r["recusadas"]:
                for x in r["recusadas"]:
                    x["linha"], x["texto"], x["lote"] = n, linha[:160], b["lote"]
                    saida["recusadas"].append(x)
                st["recusadas"] += 1
                continue
            chave = (re.sub(r"[^\d.\-]", "", cels[0]), cl_sem_acento(cels[1]).lower(), re.sub(r"\s+", " ", cels[2].strip().lower()), cl_sem_acento(cels[3]).lower())
            if chave in vistos:
                st["repetidas"] += 1; saida["repetidas"] += 1
                continue
            vistos.add(chave)
            st["aceitas"] += 1
            for k in ("contatos", "completar", "nao_consta", "tentar_depois"):
                saida[k].extend(r[k])
            dado = chave[1].replace("-", "_").replace(" ", "_")
            res = chave[3].replace(" ", "_").replace("-", "_")
            saida["linhas"].append({"processo": chave[0], "dado": dado, "resultado": res, "fonte": cels[4][:80], "obs": cels[6][:120], "lote": b["lote"]})
        saida["lotes"].append(st)
    return saida

