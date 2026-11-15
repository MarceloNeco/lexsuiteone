# Dossiê: Astrea (Aurum) × RADAR JUDICIAL, com o servidor MCP do mcp.ai (Arquitetura, 15/Nov/2026)

Fontes: (A) relatório da navegação no Astrea da KR Law em 13/Nov (`visita-kr-law/resultados/2026-11-13-Astrea-prompt-3-relatorio.md`,
55 ações, só leitura); (B) leitura do site mcp.ai em 15/Nov pelo pesquisador (páginas resumidas; trechos literais a conferir antes
de citar ao cliente); (C) termos de uso do Astrea e "instruções para IA" da Aurum, lidos em 15/Nov. Lacunas no fim.

## 1. O que já sabemos do Astrea (fonte A)

- Não há API pública, webhooks nem importação de contatos por planilha. Administração → Integrações só tem WhatsApp (desabilitada);
  boletos via Asaas. Carga em massa é serviço pago da Aurum ("Migrações de dados").
- Saída de dados: "Exportar os dados do Astrea" (arquivo único por e-mail), Exportar contatos, Excel nas listas.
- Contato PJ: Empresa* (único obrigatório), Nome fantasia, Perfil (Contato/Cliente), Etiquetas, telefones (tipo WhatsApp), e-mails,
  sites, endereço, CNPJ (aba Documentação), Comentários. "Origem do cliente" só com Perfil = Cliente. Duplicado avisado por CNPJ.
- Processo: Clientes* + Qualificação, Título*, Responsável*, Número CNJ, Juízo, Ação, Valor da causa, Distribuído em, Etiqueta.
- Publicações já vêm do DJEN para os nomes cadastrados (5 nomes no plano; captura instável no dia).

## 2. O que o mcp.ai oferece (fonte B, 15/Nov)

| Item | O que diz o site |
|---|---|
| O que é | Intermediário (DL WEB LTDA, CNPJ 20.873.739/0001-15, Campo Grande/MS) que publica servidores MCP; o "Astrea (Aurum)" usa a **API interna** do Astrea ("sem API pública oficial"). |
| Ferramentas de leitura | agenda (audiências, reuniões, prazos, tarefas), processos (buscar, listar, contar, por cliente, novos por mês), andamentos, etiquetas, kanban, modelos, honorários/despesas por processo, **clientes paginados**, plano. |
| Ferramentas de escrita | criar/editar/excluir audiências, compromissos, tarefas e prazos; criar processo e caso; editar objeto e valor de condenação; **encerrar em lote**; lançar andamento; gerar e subir documento; mover tarefa; **aplicar e remover etiquetas em lote**. **Não consta criar contato nem criar cliente.** |
| Autenticação | **usuário e senha do Astrea** (recomenda usuário dedicado) + OAuth do mcp.ai nos clientes com navegador; agentes sem navegador recebem um token Bearer por link. A política de privacidade diz não guardar senhas; não explica como autentica no Astrea. Onde a senha fica: **não informado**. |
| Chamada por programa | Sim: REST em `api.mcp.ai/api/astrea`, Bearer com chave de workspace (`sk_live_…`). Formato dos corpos e limites: não lidos. |
| Preço e limites | não informados (/pricing dá 404; termos citam valor pago em 12 meses; Stripe é subprocessador). |
| Privacidade | TLS, credenciais criptografadas, conteúdo "não armazenado nem usado para treino" (alegação); subprocessadores Composio, Google, Stripe, hospedagem e e-mail, alguns no exterior (LGPD art. 33); logs 90 dias; sem DPA visto; sem SOC 2/ISO informado; responsabilidade limitada a R$ 1.000 ou o pago em 12 meses. |
| Clientes | Claude (web/desktop, conector), ChatGPT (modo desenvolvedor), Cursor, agentes MCP. Manus: não lido. |

## 3. O que a Aurum diz (fonte C, 15/Nov)

- "Instruções para IA" da Aurum: o Astrea **não tem API pública**; integrações oficiais são Asaas e WhatsApp.
- Termos de uso do Astrea: o cliente não pode "utilizar automatizações e/ou integrações próprias ou de terceiros **sem a autorização
  expressa da AURUM**"; senha "pessoal e intransferível", proibido compartilhar; integrações não oficiais são "por conta e risco
  exclusivo do CLIENTE"; a Aurum pode suspender o acesso em caso de violação. (Texto sem data; pode haver versão mais nova. Não é
  parecer jurídico.)

## 4. Leitura da Arquitetura

1. **O achado prova que a integração é tecnicamente viável** (o Astrea tem uma API interna completa, inclusive escrita) e que já
   existe quem a use por LLM.
2. **Não dá para usar o mcp.ai com a conta da KR Law hoje**: (a) viola os termos do Astrea sem autorização expressa da Aurum, com
   risco de suspensão da conta do escritório; (b) a senha do escritório e dados de processos passam por um terceiro sem contrato de
   operador, sem preço público e com subprocessadores no exterior; (c) API interna muda sem aviso.
3. **O que o mcp.ai não faz** é justamente a primeira coisa que o RADAR precisaria: **criar contato PJ**. Faz etiqueta em lote,
   processo e cliente paginado (serviria para a integração C: ler os clientes e marcar como excluídas).
4. O RADAR fica no domínio do escritório, como o dono lembrou; mas o mcp.ai não fica: é um servidor de terceiro no meio. A única
   forma de a integração ficar "nos domínios do escritório" é direta (RADAR → Astrea), o que exige a autorização da Aurum.

## 5. Caminhos possíveis, do mais seguro ao menos

| Caminho | Precisa de | Para quê serve | Quando |
|---|---|---|---|
| **P1. Planilha pronta do RADAR** (contato PJ no formato do Astrea; etiqueta JUDICIAL; CNJ nos Comentários) | nada | integração B (entrada) digitada pela equipe ou pelo serviço de migração da Aurum | já (0.7.4x, Produto) |
| **P2. Exportação do Astrea lida pelo RADAR** (só a coluna CNPJ do "Exportar contatos") | o escritório exportar quando quiser | integração C (clientes como excluídas) | já (0.7.4x) |
| **P3. Extensão na sessão do advogado** (Claude in Chrome digitando o contato PJ pelo mapa de telas da fonte A) | aceite do escritório; sem senha para ninguém | B sem digitação manual | depois do P1, se o escritório quiser |
| **P4. Integração direta autorizada** (RADAR → Astrea, API interna ou oficial) | **autorização expressa da Aurum**, por escrito | B e C automáticos | só com a resposta da Aurum |
| **P5. mcp.ai** | tudo acima + contrato com a DL WEB, conta dedicada, preço | B parcial (sem criar contato) e C | não recomendado |

## 6. Próximo passo recomendado

Escrever à Aurum (produto@aurum.com.br ou o canal comercial), em nome da SolverONE e com o escritório em cópia se ele quiser:
apresentar o RADAR, pedir a **autorização expressa** para integração (ou a API oficial, se existir para parceiros) e perguntar o que
os termos permitem para automação na sessão do próprio advogado. Isso substitui a pergunta 25 ao Leandro e é coisa que a SolverONE
pode fazer sozinha. Enquanto não houver resposta: P1 e P2.

## 7. Lacunas

- mcp.ai: preços, docs REST detalhadas (`/_endpoints`), seção Manus, "sobre", status, DPA; como a senha do Astrea é guardada.
- Termos do Astrea sem data; conferir versão vigente. CNPJ da DL WEB não conferido na Receita.
- Os resumos de (B) e (C) foram feitos por modelo; antes de citar ao cliente ou à Aurum, ler o trecho literal.
