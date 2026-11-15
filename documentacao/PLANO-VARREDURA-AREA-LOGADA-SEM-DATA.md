# Plano guardado (sem data): varredura pela área logada para completar o que o Diário não traz

Pedido do dono, 15/Nov/2026: "deixar planejado, ainda sem data, um novo prompt que, via área logada do Astrea e do PJe, vai atrás de
processos recentes que não têm o contato nem o valor da ação no Diário, e faz a varredura para achar esses dados mais completos".
Fica aqui para ser resgatado a qualquer momento. Não tem versão nem prazo; não entra na 0.7.48.

## 1. O que é

Hoje (0.7.46/0.7.47) a área logada é **a pedido**: a pessoa marca processos, o RADAR gera o pedido, a extensão de IA roda na sessão do
advogado, a pessoa cola a resposta. A **varredura** é a mesma coisa, só que **automática na escolha**: o RADAR separa sozinho os
processos recentes (por padrão, os últimos 30 dias) que estão sem valor da causa, sem endereço, sem e-mail ou sem telefone da ré, monta
o pedido em lotes de 25 e deixa pronto; a pessoa só executa na sessão logada e cola a resposta. O programa continua sem credencial.

## 2. Fontes e o que cada uma pode dar

| Fonte | O que pode completar | Condição | Estado do conhecimento |
|---|---|---|---|
| **PJe** (consulta processual, advogado logado) | valor da causa, data de distribuição, CNPJ, endereço e e-mail da ré | processos de terceiros: visibilidade **não confirmada** (teste de 5 min em `visita-kr-law/PROMPT-TESTE-GAP-PJE-2026-11-15.md`) | comparação em `COMPARACAO-DJEN-X-PJE-2026-11-15.md` |
| **Astrea** (sessão do escritório) | só o que o escritório já tem: clientes (CNPJ) para marcar como excluídas; contatos e processos já cadastrados | sem API; termos da Aurum vedam automação de terceiros sem autorização; a extensão na sessão do próprio advogado é zona cinzenta a decidir | dossiê em `DOSSIE-ASTREA-MCP-AI-2026-11-15.md` |
| Receita (já existe) | CNPJ, endereço, telefone e e-mail cadastrais | público | já no RADAR |

Para processos de terceiros, o Astrea **não tem** dado novo (ele só sabe dos processos do próprio escritório). A varredura no Astrea serve
para duas coisas: marcar clientes como excluídas e evitar propor empresa que já é cliente; e, no futuro, gravar lá a empresa escolhida.

## 3. Como seria no programa (quando for feito)

1. Lista → filtro "Área logada: ainda não pedido" já existe (0.7.46). Novo: botão **"Varrer os últimos 30 dias"** no menu ☰ → Área
   logada, que seleciona sozinho os processos sem valor, endereço, e-mail ou telefone e abre o passo 1 do pedido já preenchido.
2. Pedido em lotes de 25 (limite por pedido da 0.7.46), um pedido por sessão do PJe; o texto do pedido é o v2, só com o que falta.
3. Resposta colada ou em arquivo, mesmo leitor da 0.7.46; "o que mudou" por processo; fonte "PJe dados do processo" com prioridade
   sobre Receita; nunca apaga.
4. Opcional, mais tarde: agendar a varredura (toda segunda o RADAR deixa o pedido pronto e avisa na faixa "pedido pronto para rodar").
5. Astrea: passo separado, "Trazer clientes do Astrea" (lê a exportação de contatos, só a coluna CNPJ) e marca excluídas. Entrada no
   Astrea (contato PJ com etiqueta JUDICIAL) só por planilha, até a Aurum autorizar.

## 4. O que precisa acontecer antes

- Teste de 5 minutos no PJe (consulta de terceiros): define se endereço e e-mail vêm ou só valor e data.
- Decisão do dono sobre o Astrea (hoje: adiado; não procurar a Aurum).
- Termos: a seção 5 (área logada e ferramentas de terceiros) já cobre a varredura; sem mudança.

## 5. Prompt da varredura (rascunho, para quando for a hora)

O texto do pedido é o mesmo `visita-kr-law/PROMPT-PJE-AREA-LOGADA-V2.md` (roteiro do PJe, "lote N de M", formato RESPOSTA PARA O RADAR
v1), com a lista de processos montada pelo RADAR pelo critério "recentes sem dado". Não há prompt novo a escrever: o que muda é quem
escolhe os processos (o programa, não a pessoa).
