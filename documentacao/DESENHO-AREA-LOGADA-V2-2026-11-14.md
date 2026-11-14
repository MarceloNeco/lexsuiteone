# Área logada v2: do filtro ao dado completado, sem o advogado abrir processo por processo (Arquitetura, 14/Nov/2026)

Pedido do dono (14/Nov): o advogado escolhe o que quer na lista do RADAR, o programa gera o "código de consulta" (prompt + lista),
ele copia, cola no Claude in Chrome logado no PJe, a extensão percorre os processos sozinha, e o RADAR lê a resposta, por texto
colado ou por arquivo, completando valor da causa, data, contatos da empresa e porte. Este desenho diz o que já existe, o que falta
e como a Produto fecha (0.7.46), com base nos relatórios da visita à KR Law (13/Nov) e no prompt v2 já escrito.

## 1. O que já existe no RADAR (desde a 0.7.16; conferido no código em 14/Nov)

| Passo do dono | Existe? | Onde |
|---|---|---|
| Escolher pelo filtro (ex.: últimos 50 do setor X, TRT Y) e marcar todos | sim: filtros da lista + caixa "selecionar todos" + barra de lote | `radar_modelo.html` 3914-3925 |
| Botão que gera o pedido só com o que falta em cada processo e **copia para a área de transferência** | sim: "Preparar busca" → `/contatos/preparar` → `contatos.preparar_v1` (arquivo em `saida/contatos/pedido-pje-<data>.md` + cópia no clipboard) | `app.py` 1058-1068; `contatos.py` 209 |
| Colar a resposta e o RADAR entender sem IA, linha a linha | sim: "Trazer dados da área logada" → `/contatos/colar` → `colar_v1` (valor, data, contatos; recusa CPF e pessoa) | `app.py` 1085-1109; `contatos.py` 269 |
| Dados entrarem na lista, na ficha e na planilha | sim: `banco.completar` + contatos + planilha regravada | `app.py` 1097-1104 |
| Porte, setor, capital | sim, pelo cadastro CNPJ (Receita), não pelo PJe | `cnpj.py` |

Ou seja: o circuito "filtro → código → Claude in Chrome → resposta → lista" **funciona hoje**. O que a visita mostrou é que o texto
do pedido era genérico demais ("abra o processo, leia a petição inicial"): sem o mapa real, a extensão perde tempo, abre o que não
deve (expediente, download) e devolve pouco. O prompt v2 (`documentacao/visita-kr-law/PROMPT-PJE-AREA-LOGADA-V2.md`) resolve isso
e já pode ser usado por cima do pedido atual, à mão, hoje.

## 2. O que falta (Produto, 0.7.46)

1. **Prompt v2 embutido** no texto que "Preparar busca" gera (`contatos.PEDIDO_V1`), no lugar do texto genérico: roteiro por processo
   sobre o mapa real do PJe (painel → número → `/pjekz/processo/<id>/detalhe` → cabeçalho → "Dados do processo" → petição inicial →
   notificação), proibições (login, downloads, expedientes, dado de pessoa) e o bloco de resposta. Um só texto, PT; a extensão
   entende. O tribunal da lista decide a variante: TRT (mapa "pjekz", igual para TRT2 e TRT15); outros tribunais recebem o roteiro
   genérico até serem mapeados.
2. **Lotes e tamanho**: o pedido sai em blocos de 25 processos, numerados ("Lote 1 de 3"); o prompt manda a extensão devolver
   **um bloco "RESPOSTA PARA O RADAR v1 · lote N de M" por lote**, terminando cada um antes de começar o próximo, e, se o texto
   ficar grande, salvar a resposta num arquivo `.md` ("Baixar"). O limite diário (`area_logada_por_dia`, hoje 30) passa a 100 por
   padrão, ajustável em Configuração (a regra de "tribunal bloqueia terceiros" vale para processos onde o advogado não atua; nos
   próprios autos não há limite conhecido).
3. **Entrada agnóstica**: a janela "Trazer dados da área logada" aceita (a) texto colado e (b) **arquivo** (`.md`, `.txt`, `.zip` com
   `.md`/`.txt` dentro; até 20 MB; o `.zip` é lido com `zipfile` da biblioteca padrão, sem executar nada). O leitor procura **todos** os
   blocos "RESPOSTA PARA O RADAR v1" no texto (um ou vários lotes, em qualquer ordem, com ou sem conversa em volta) e ignora o resto.
   Linhas repetidas entre lotes contam uma vez. O resultado mostra, por lote, aceitas, recusadas e o motivo.
4. **Fonte nova** aceita em `colar_v1`: "PJe dados do processo" (de onde saem valor, data, endereço e e-mail com rótulo fixo).
   Endereço vindo da petição entra marcado "a conferir"; o do cadastro da parte tem prioridade.
5. **Texto da tela**: "8 colunas" vira a tabela v1 de 7 colunas; a janela ganha o passo a passo em 3 linhas (copiar → colar no Claude
   in Chrome com o PJe aberto → colar ou subir a resposta aqui) e o (?) com o que nunca entra (CPF, autor, testemunhas, advogados).
6. **Porte** continua vindo da Receita; o prompt não pede porte ao PJe. Se a empresa não tem cadastro CNPJ lido ainda, a leitura
   normal do RADAR resolve; nada muda aqui.
7. Definição de pronto: manual (seção "Área logada"), AssistONE (ajuda, tour, busca: "área logada", "prompt", "colar resposta",
   "subir arquivo"), Novidades formais, termos sem mudança (seção 5 da 1.0 já descreve exatamente este fluxo), e-mail sem mudança.

## 3. O que o Astrea tem a ver com isso

Nada para **completar** a lista: o Astrea não tem dado de processo que o PJe não tenha. Ele entra em outro fluxo, já desenhado
(`visita-kr-law/resultados/2026-11-13-RESUMO-E-INTEGRACAO.md`, caminhos B e C): receber as empresas escolhidas como contato PJ
e devolver a lista de clientes como excluídas. Fica para depois do "pode" do dono.

## 4. Enquanto a 0.7.46 não sai (hoje, com a 0.7.45)

O Leandro já consegue rodar: marca os processos no RADAR → "Preparar busca" (o texto vai para a área de transferência) → no Claude in
Chrome, com o PJe aberto, cola **primeiro** o prompt v2 (`PROMPT-PJE-AREA-LOGADA-V2.md`) e **depois** o texto copiado → ao terminar,
copia o bloco "RESPOSTA PARA O RADAR v1" → RADAR, "Trazer dados da área logada", cola, "Ler a resposta". Limite de hoje: 30 por dia.

## 5. O que não falta

Nenhum insumo novo do dono ou do Leandro. Os relatórios da visita (texto) e os prints (nos zips do dono) foram lidos inteiros e
são a base deste desenho e do prompt v2. Nada aqui depende de nuvem nem de SQL.
