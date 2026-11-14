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

## 2b. Correções do dono no teste da 0.7.45 (14/Nov, 0h) e o que muda no desenho

Defeitos vistos na 0.7.45 (Produto corrige na 0.7.46, junto com o resto):
- O (?) da barra de lote abre fora da área visível no monitor do notebook e rola junto com a lista; tem de abrir para cima, dentro
  da tela, fixo enquanto a lista rola (como os outros balões de ajuda).
- A janela "Pedido pronto e copiado" aparece mais de uma vez por clique e não mostra o texto: passa a ter uma caixa com o pedido
  (rolável, pequena) e o botão "Copiar de novo"; sem abrir a pasta sozinha.
- O texto "8 colunas" na janela de colar.

Mudanças de regra, a partir do que o dono viu no PJe:
1. **Não existe "100 por dia"**. A sessão do PJe expira em pouco tempo e o login exige token físico (USB) com MFA, então cada pedido é
   **uma sessão**: limite **por pedido** (padrão 25, máximo 50, em lotes de 25), sem promessa diária. A terceira opção do passo 1 vira
   "os próximos N da lista filtrada que ainda não foram ao PJe".
2. **Memória do que já foi pedido**: cada processo guarda "pedido em / respondido em / resultado" por dado. A lista ganha o filtro
   **"Área logada: ainda não pedido · com dados · nada no processo · tentar depois"** e o selo "área logada · <data>" no cartão. O
   filtro só aparece depois do primeiro pedido respondido.
3. **Dado que já existia**: nunca se apaga nada. Valor e data novos substituem o antigo só se a fonte for mais forte (cadastro da
   parte > petição > Receita > digitado) ou mais nova; o anterior fica no histórico da ficha. Contato novo é acrescentado; contato
   igual não duplica. Tudo isso aparece no relatório como "acrescentado / alterado (antes → depois) / igual".
4. **Relatório do resultado** (passo 4): totais (pedidos, com dado novo, nada no processo, tentar depois, recusadas), achados por
   tipo de dado, tabela "o que mudou" por processo com antes → depois ao passar o mouse, e os botões "Ver na lista" e "Novo pedido
   só com o que faltou". Se o texto não tiver nenhum bloco reconhecível: "Não achei a tabela RESPOSTA PARA O RADAR v1 neste texto",
   com as 3 primeiras linhas do que chegou, para a pessoa ver se colou a coisa certa. Se o formato vier parecido mas diferente
   (coluna a mais, cabeçalho mudado), o leitor aceita o que der para reconhecer e lista o resto como recusado com o motivo, nunca
   trava.
5. **Menu ☰ → Área logada** oferece as duas coisas: "Gerar pedido…" (abre o passo 1 com a lista atual) e "Trazer resposta…" (passo 3).
6. **Arquivo**: além do texto colado, subir `.md`, `.txt` ou `.zip` (ferramentas que entregam artefato em vez de texto).
7. **Nada trava a tela**: os passos são uma janela comum, não um túnel. Depois de copiar o pedido (passo 2), "Fechar e voltar quando
   tiver a resposta" fecha a janela e deixa uma faixa "pedido de <data> (<n> processos) aguardando resposta" no alto da lista, com
   "Trazer resposta" (passo 3) e "Cancelar pedido". A pessoa usa o programa normalmente enquanto a ferramenta roda em outra aba. O
   pedido pendente fica gravado (arquivo do pedido + marca "pedido em" nos processos) e sobrevive a fechar e abrir o programa; o
   menu ☰ → Área logada → "Trazer resposta" leva ao mesmo passo 3. Lotes podem chegar em dias diferentes.

## 2c. Interruptor por licença (feature flag) no RootifyONE

Viável e barato: a `lex-conta` já devolve `recursos` {id: ligado} dos arquivos master do RootifyONE e o programa já esconde o que
tem `data-recurso` desligado (interruptor do AssistONE). Falta o **nível por licença**: coluna `lex_contas.recursos` (jsonb), ficha do
RootifyONE com o interruptor "Área logada", `lex-conta` v19 aplicando a licença por cima do global, e o programa marcando a barra,
o menu e o botão do cartão com `data-recurso="area-logada"` (conferido a cada abertura, na verificação da licença, como hoje).
Padrão inicial: **desligado na KR Law**, ligado na licença de teste, até o dono ligar pela ficha. SQL proposto em
`nuvem/supabase/2026-11-14-lex-recursos-por-licenca.sql` (não aplicado; entra com o "pode aplicar"). Serve para qualquer recurso
futuro (chamados, exportação para o Astrea), não só para este.

## 2d. Como o liga e desliga chega ao RADAR (pergunta do dono, 14/Nov)

- **Onde se liga**: RootifyONE → Licenças do RADAR → ficha → bloco "Recursos desta licença" → interruptor "Área logada" (três
  estados: segue o global, ligado nesta licença, desligado nesta licença). Grava em `lex_contas.recursos` por `admin_lex_salvar`, com
  evento no histórico. O global (Controle dos apps) continua valendo para quem não tem exceção.
- **Como o programa fica sabendo** (hoje): a licença é conferida na `lex-conta` ao abrir o programa, antes de cada leitura, ao clicar
  em "conferir"/"Trocar licença" e, só enquanto há aceite pendente, ao voltar o foco. A resposta traz `recursos` e o programa guarda
  em `config.json` (`conta.recursos`) e esconde na hora o que está desligado (`data-recurso`).
- **O que muda na 0.7.47 (Produto)**: conferência leve também **a cada 30 minutos com a tela aberta**, ao **voltar o foco** se a
  última foi há mais de 30 min, e no **F5/Atualizar**; a resposta atualiza `recursos` e a tela se ajusta sem reabrir. É a "atualização
  de recursos" que o dono pediu: não é versão nova, é o estado da licença. Custo: 1 pedido a cada 30 min por computador (a
  `lex-conta` já limita por instalação). **Sem internet**: vale o último estado conhecido; nunca "abre" um recurso que estava
  desligado só porque a nuvem não respondeu. Primeira instalação sem resposta: o recurso fica como o padrão do pacote
  (`recursos-do-app.json`, "area-logada": desligado até a licença dizer o contrário).
- **Onde a pessoa vê**: Configuração → Este computador → "Recursos da licença: Área logada ligada pela SolverONE em 14/11 (conferido
  há 12 min)". Quando desligado, os três lugares (barra de lote, menu, botão do cartão) simplesmente não aparecem; o manual diz
  "este recurso é ligado pela SolverONE por escritório; fale com o seu contato".
- **Quem faz o quê** (para não haver sobreposição com o que o dono perguntou à Produto): Produto = `data-recurso` nos 3 lugares, a
  conferência de 30 min/foco/F5 e a linha em Configuração; Arquitetura = coluna `lex_contas.recursos`, `lex-conta` v19 (licença por
  cima do global), `recursos-do-app.json` com `area-logada`, padrão desligado na KR Law; RootifyONE = a ficha (prompt
  `documentacao/PROMPT-ROOTIFYONE-RECURSOS-POR-LICENCA-2026-11-14.md`).

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
