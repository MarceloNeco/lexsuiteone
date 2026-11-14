# O que a ferramenta devolve (protótipo; dados fictícios)

O RADAR aceita este texto colado na janela "Trazer dados da área logada" **ou** num arquivo `.md`/`.txt`/`.zip`. Ele procura todos os
blocos "RESPOSTA PARA O RADAR v1" (um por lote, em qualquer ordem, mesmo com conversa em volta) e ignora o resto.

Pronto. Percorri os 25 processos do lote 1. Segue o bloco pedido:

RESPOSTA PARA O RADAR v1 · lote 1 de 2
| processo | dado | valor | resultado | fonte | data | observação |
|---|---|---|---|---|---|---|
| 0000001-11.2026.5.02.0001 | valor_causa | 105000,00 | encontrado | PJe dados do processo | 2026-11-14 | |
| 0000001-11.2026.5.02.0001 | email | contato@exemplo-um.com.br | encontrado | PJe dados do processo | 2026-11-14 | |
| 0000001-11.2026.5.02.0001 | telefone | | nao_consta | PJe petição inicial | 2026-11-14 | só o telefone do advogado do reclamante, não anotado |
| 0000002-22.2026.5.02.0002 | valor_causa | 48250,50 | encontrado | PJe dados do processo | 2026-11-14 | |
| 0000002-22.2026.5.02.0002 | data_ajuizamento | 2026-10-30 | encontrado | PJe dados do processo | 2026-11-14 | |
| 0000002-22.2026.5.02.0002 | endereco | Rua Exemplo, 100, Centro, São Paulo - SP, 01000-000 | encontrado | PJe petição inicial | 2026-11-14 | a conferir |
| 0000003-33.2026.5.02.0003 | telefone | | tentar_depois | | 2026-11-14 | petição em PDF |
| 0000003-33.2026.5.02.0003 | email | | tentar_depois | | 2026-11-14 | petição em PDF |
| 0000003-33.2026.5.02.0003 | site | | tentar_depois | | 2026-11-14 | petição em PDF |

(… linhas dos outros 22 processos …)

## Como o RADAR lê (sem IA)

- Cada linha vira: completar valor/data na ficha (`banco.completar`), contato novo (`guardar_contato`) ou pendência (nao_consta /
  tentar_depois, para o próximo pedido só pedir o que ainda falta).
- Recusa na hora, com o motivo mostrado na tela: CPF em qualquer coluna; palavra reclamante/autor/testemunha/preposto/advogado na
  linha; processo que não está na lista pedida; canal desconhecido; valor fora do formato.
- "a conferir" entra na ficha com essa marca; o endereço do cadastro da parte tem prioridade se vier nos dois.

## Funciona em outras ferramentas?

Sim, por desenho. O pedido é texto comum (instruções + tabela) e a resposta é uma tabela Markdown: qualquer agente que navegue no
Chrome com a sessão do advogado (Claude in Chrome, Codex/Operator do OpenAI, Gemini no Chrome, Comet) consegue seguir e devolver.
O RADAR não sabe nem precisa saber qual ferramenta gerou o texto; os termos 1.0 (seção 5) já dizem "extensão de IA de qualquer
fornecedor". O que muda entre ferramentas é a disciplina com as proibições e a fidelidade ao formato; por isso o leitor recusa
linha por linha e nunca confia no que vem fora da tabela. Cada ferramenta nova é testada uma vez com 3 processos antes de liberar
para o escritório (a Operação registra no quadro qual passou).
