# Desenho: critérios por pessoa, chamados pelo AssistONE e CNPJ alfanumérico (Arquitetura, 12/Nov/2026)

Resposta ao pedido da Produto "Três pedidos do dono (12/Nov, teste da 0.7.31)" (`docs/QUADRO.md`, Pedidos entre sessões) e à
decisão do dono de 12/Nov ("Critérios da lista por pessoa, no computador (MVP), por área"). A Produto implementa na 0.7.33.
O que mexe na nuvem (`lex-conta` v17) é da Arquitetura e é consequência do pedido do dono (chamados): não precisa de novo "pode".

Mapa do código de hoje (HEAD `50334bf`), conferido antes de desenhar:

- Critérios e exclusões: `robo/lexsuite/preferencias.py` (padrões 21-33, planilha por frente 14-16, `carregar()` 223, `aplicar()`
  298-318, marca das abas 164); gravação pelo POST `/regras` (`app.py` 844-892 → `radar.regravar_planilha` → `compartilhar._abas_editaveis`
  123-150); tela "Critérios da lista" em `radar_modelo.html` 2074-2081 e 3528-3582. `config.json` repete `valor_minimo` e
  `teto_capital_gigante` (`config.py` 11-12). Não existe "área" no config; as frentes estão em `frentes.py` (`FRENTES`).
- CNPJ: `classificar.py` 25 (`_CNPJ` só dígitos), 70-88 (`cnpj_valido`, `extrair_cnpjs`), 235 (carteira); `cnpj.py` 14 (BrasilAPI, depois
  minhareceita); `preferencias.py` 301 (exclusão por CNPJ só dígitos); `conta.py` 233-250 **já valida o alfanumérico** (ASCII − 48),
  usado pela rota `/cnpj` (`app.py` 498-504); tela `radar_modelo.html` 2254 (`cnpjFmt` só dígitos), 4154-4175.
- AssistONE: `radar_modelo.html` 1264-1565 (balão 1299, opções 1454-1458, busca 1471, tour 1553); não há trilha de cliques; a página
  só fala com `127.0.0.1` (CSP `default-src 'self'`, `app.py` 407); a nuvem é falada só pelo servidor local (`conta.py`).
- Central de feedback do RootifyONE: tabelas `sol_feedback`, `sol_feedback_arquivos`, `sol_feedback_perguntas`, `sol_feedback_contador`
  e funções `sol_enviar_feedback(p jsonb)` e `sol_feedback_anexo(...)` (rootify-one, `entrega/solverone-app/supabase/2026-10-10-feedback-usuarios.sql`),
  aplicadas no projeto `solverone-app`; `radar-judicial` já está em `sol_apps`. Limites existentes: 6 envios por minuto por
  aparelho, 300 por minuto por app, 5 anexos de até 10 MB por envio, só imagem e vídeo, anexo só nas 24 h seguintes, bucket privado
  `sol-arquivos`. A ficha do admin (`rootify-feedback.js`) mostra app, tela, função, versão, trilha, aparelho e anexos por URL assinada.

## 1. Critérios da lista e empresas excluídas: por pessoa, no computador, por área

### 1.1 Decisão do dono (12/Nov) e o que ela muda

Valor mínimo, mínimo de ações e janela, jurídico próprio (teto de capital), esconder jurídico próprio, esconder excluídas, sócios,
dias na aba Arquivo, limite de linhas **e a lista de empresas excluídas** passam a ser **da pessoa, neste computador, por área**
(trabalhista, tributário, cível, empresarial). O programa **não lê nem grava** nada disso na planilha. Reverte "preferências por
planilha" e "exclusões somadas" da 0.7.16 (`documentacao/DESENHO-PLANILHA-GRANDE.md` 33-34). Depois, na nuvem, por e-mail.

Hoje o programa já liga um computador a uma pessoa (e-mail do cadastro, `config.usuario` e `lex_instalacoes`); "por pessoa" e
"por computador" são a mesma coisa no MVP. Quando duas pessoas usarem o mesmo computador, o critério é o de quem está cadastrado
ali; a nuvem resolve isso depois (item 1.6).

### 1.2 Onde fica: `criterios.json`, ao lado do `config.json`

Arquivo próprio, na pasta de dados do programa (a mesma do `config.json` e do `lexsuite.db`, nunca na pasta compartilhada), e não
dentro do `config.json`: o config é regravado inteiro a cada "Salvar" da Configuração (a revisão da 0.7.32 já achou corrida nessa
gravação), tem outro dono de tela e não tem áreas; o arquivo separado também é o que vai subir para a nuvem como um bloco só.

```json
{"versao": 1, "atualizado_em": "2026-11-12T20:15:00-03:00", "origem": "planilha",
 "areas": {
   "trabalhista": {"valor_minimo": 100000, "minimo_acoes": 1, "janela_dias": 30, "teto_capital_gigante": 50000000,
                   "esconder_gigantes": false, "esconder_excluidas": true, "mostrar_socios": true,
                   "dias_arquivo": 90, "limite_linhas": 60000,
                   "exclusoes": [{"quem": "Empresa Exemplo Ltda", "cnpj": "12ABC34501DE35", "motivo": "cliente", "desde": "2026-11-12"}]},
   "tributario": {}, "civel": {}, "empresarial": {}}}
```

- Chaves e padrões são os de `preferencias.PADRAO` (nada muda de nome). Área ausente ou chave ausente = padrão. `exclusoes` até
  5 000 por área (`MAX_EXCLUSOES`, como hoje); `cnpj` guardado limpo (14 posições, maiúsculas, item 3) ou `null` quando a
  exclusão é por nome; `motivo` livre (cliente, conflito, parte contrária…), `desde` só informativo.
- Gravação atômica (arquivo temporário e `os.replace`), cópia `criterios.json.anterior` antes de cada gravação, mesmo padrão do
  `config.py`. Erro de leitura (JSON quebrado) = padrões, com aviso na tela e registro em `saude`, nunca trava a leitura do Diário.
- `preferencias.py` continua sendo o módulo dos critérios: `carregar(frente)` passa a ler do arquivo (um dicionário por área) e
  `aplicar(itens, prefs)` fica igual; some tudo que fala com a planilha: `marca_regras`, `linhas_regras`, a leitura das abas em
  `carregar()` 232-272 (menos a aba Controle, item 1.5) e `compartilhar._abas_editaveis`. O POST `/regras` grava o arquivo em vez da
  planilha e recebe a área; a "marca" de edição concorrente deixa de existir (o arquivo é só deste computador).
- `config.radar.valor_minimo` e `config.radar.teto_capital_gigante` deixam de valer: ficam no arquivo só para a migração (item 1.4)
  e a Configuração deixa de mostrá-los (um lugar só para cada coisa: "Critérios da lista").

### 1.3 Tela

- "Critérios da lista" ganha um seletor de área no alto (Trabalhista, Tributário, Cível, Empresarial), com a área da leitura atual
  selecionada; cada área tem seus valores e sua lista de excluídas. Botão "Copiar estes critérios para as outras áreas" (com
  confirmação), porque cliente costuma ser cliente em todas as frentes e o dono não quer digitar quatro vezes.
- Um (?) no título, PT e EN: "Estes critérios são seus, neste computador. Cada pessoa do escritório tem os dela; a planilha
  compartilhada não guarda critérios." A mesma frase no manual, no AssistONE (ajuda da tela e busca: "critérios", "excluir empresa",
  "por área", "só meus") e nas Novidades ("Critérios da lista e empresas excluídas por pessoa, neste computador, separados por área").
- O cartão de aviso "a planilha está só para leitura / Editar Preferências e Exclusões" e o `rg_mudou` ("alguém mudou as regras")
  somem, porque não há mais edição concorrente.

### 1.4 Migração do que está hoje nas abas Preferências e Exclusões

Uma vez só, na primeira abertura da 0.7.33 em cada computador, quando `criterios.json` não existe (`preferencias.migrar()`):

1. Para cada frente, se a planilha `LexSuiteONE - <Frente>.xlsx` existir na pasta compartilhada, ler as abas Preferências e Exclusões
   dela (é a **última** vez que o programa lê essas abas) e gravar na área correspondente. A aba Exclusões de cada frente vai só para a
   sua área (a soma das frentes da 0.7.16 acaba); como a tela só editava a planilha trabalhista (`app.py` 558-564), na prática as outras
   frentes têm os padrões ou a lista que a trabalhista gravou.
2. Se não houver planilha: `config.radar.valor_minimo` e `teto_capital_gigante`, se existirem, em todas as áreas; o resto, padrão.
3. Gravar `criterios.json` com `origem: "planilha"` ou `"config"` e registrar em `saude` ("critérios migrados: N exclusões por área").
4. Na próxima leitura do Diário, a planilha é regravada sem as duas abas (item 1.5). Quem tinha a planilha aberta no Excel não perde
   nada: a cópia de segurança de `armazenamento.py` 198 continua antes de regravar.

Cada computador do escritório migra a partir da mesma planilha: no dia seguinte, todos começam com os mesmos critérios e a mesma lista
de excluídas (o que o escritório tinha), e dali em diante cada um muda o seu. É o comportamento que o dono pediu, sem perder o que a
KR Law já cadastrou. Teste da Produto: planilha da 0.7.32 com valores e 3 exclusões → `criterios.json` com os mesmos valores na
área trabalhista; sem planilha → padrões; arquivo já existente → nada é relido.

### 1.5 O que a planilha passa a mostrar

- As abas **Preferências** e **Exclusões** saem. Entra uma aba só de leitura, **"Critérios desta leitura"**, com os valores usados
  pelo computador que gravou (área, valor mínimo, teto de jurídico próprio, quantidade de excluídas, nome da pessoa do `config.usuario`)
  e a frase "Os critérios são de cada pessoa, no computador dela: mude em Configuração → Critérios da lista. Esta aba não é lida pelo
  programa." Serve para quem abre a planilha de outra pessoa entender por que a lista está daquele jeito. Texto PT e EN, como hoje.
- A aba oculta **Controle** (ativo, validade, versão mínima, mensagem) não está na decisão e fica como está.
- Decisão da Arquitetura (12/Nov; o dono muda se discordar): a planilha de cada frente é **uma por escritório**
  na pasta compartilhada, mas agora cada computador a regrava com **os critérios da sua pessoa**. Os critérios que só marcam ou escondem
  (`excluida`, jurídico próprio, "esconder…") não tiram linhas da planilha, então a lista continua a mesma para todos e só a marcação
  muda. O que **tira linhas** é `valor_minimo` (resumo), `minimo_acoes`/`janela_dias` (`aplicar()`), `dias_arquivo` e `limite_linhas`: com
  pessoas de critérios diferentes, a planilha passa a refletir quem leu por último. Recomendação da Arquitetura: a planilha
  compartilhada é o **registro do escritório**, gravada com a lista completa (sem `valor_minimo` e `minimo_acoes`, com `dias_arquivo` e
  `limite_linhas` fixos nos padrões), e os critérios da pessoa valem na **tela** e no `saida/` dela, que é onde cada advogado trabalha.
  Assim ninguém apaga linha do colega sem querer. É o que vale, salvo o dono dizer o contrário.

### 1.6 Depois: nuvem

Mesmo JSON, por e-mail da pessoa, numa tabela `lex_criterios (codigo, email, area, criterios jsonb, atualizado_em)` via `lex-conta`
(ação `criterios`, ler e gravar, só para e-mail cadastrado e aprovado na licença). O computador manda o arquivo quando muda e lê ao
abrir; vence o `atualizado_em` mais novo. Nada disso entra na 0.7.33; o arquivo local já tem `versao` e `atualizado_em` para isso.

## 2. Chamados pelo AssistONE para a central de feedback do RootifyONE

### 2.1 Caminho

Página → servidor local → `lex-conta` → função `sol_enviar_feedback` do Supabase (a mesma central que os apps web usam). A página
continua sem nenhum pedido externo (CSP intacto): ela faz `POST /chamado` para `127.0.0.1`, como já faz com `/registro`. O servidor
(`conta.enviar_chamado`, ao lado de `registrar_erro`, `conta.py` 319) manda para a `lex-conta`, ação nova **`chamado`** (v17), com o
código da licença, a instalação e a versão. A `lex-conta` confere o código (ativo), aplica os limites por licença e por instalação
(`lex_contar_chamada`: 5 chamados por dia por instalação, 20 por dia por licença), e chama `sol_enviar_feedback` com a chave de serviço:

| campo de `sol_feedback` | de onde vem |
|---|---|
| `app` | `radar-judicial` |
| `tipo` | pela categoria: erro → `problema`; sugestão → `ideia`; o resto → `opiniao` |
| `categoria` | uma das fixas (item 2.2), como slug |
| `texto` | o que a pessoa escreveu (até 4 000 letras) |
| `tela`, `titulo_tela`, `funcao` | seção da tela aberta (id e título) e o id do último botão clicado |
| `trilha` | os últimos 5 cliques: `{quando, id ou aria-label do elemento}`, **nunca** o texto do elemento nem da linha |
| `versao_app`, `idioma`, `fuso`, `online`, `quando_cliente` | do programa |
| `aparelho` | `{windows, python, licenca: LEX-…, escritorio, instalacao}` (a ficha do admin mostra o JSON) |
| `anon_id` | id da instalação (16 hex; a função aceita 16 a 64) |
| `email_contato`, `pode_responder` | e-mail do `config.usuario` se a pessoa marcar "Podem me responder por e-mail" |
| `cliente_id` | UUID gerado pelo programa, para a fila sem internet não duplicar |

Por que pela `lex-conta` e não direto no Supabase com a chave publicável: o programa continua falando com um endereço só, sem chave
nenhuma dentro dele; a licença é conferida (um chamado só sai de uma instalação com código ativo, o que corta o spam anônimo); o
escritório e o código entram na ficha; e os limites por licença ficam no mesmo lugar dos outros. A `lex-conta` já tem a chave de serviço.

### 2.2 Tela (balão do AssistONE)

- Opção **"Abrir um chamado"** no balão (ao lado de Ajuda e Tour). Abre um formulário curto, PT e EN: categoria (Erro, Dúvida,
  Sugestão, Licença e acesso, Planilha e pasta, Leitura do Diário, **Outros**), texto, caixa "Podem me responder por e-mail (e-mail)".
- Abaixo, **prévia do que vai junto**, visível e com "não enviar" em cada item: tela e último clique, versão, Windows, código da
  licença e escritório. Regra do dono: nenhum dado de processo vai sem a pessoa ver. O programa **não coleta** nome de parte, número
  de processo nem CNPJ: a trilha guarda só ids de elementos e `aria-label`; se a pessoa quiser mandar um caso, ela digita no texto.
- Enviado: "Chamado nº 123 aberto. Guarde o número." (o `numero` vem de `sol_feedback_contador`). O número e a data ficam em
  `saida/chamados.json` e aparecem em "Meus chamados" (lista local, sem consulta à nuvem no MVP).
- **Sem internet**: aviso claro na hora ("Sem internet: o chamado não foi enviado. Ele fica guardado e sai sozinho quando o RADAR
  abrir com internet.") e fila local em `saida/chamados-pendentes.json`; o reenvio usa o mesmo `cliente_id`, então nunca duplica.
  Se a Produto preferir só o aviso no MVP, o `cliente_id` já deixa a fila para depois.
- Resposta do admin: no MVP chega por e-mail (campo `pode_responder`), pelo RootifyONE. "Ver resposta no programa" fica para a nuvem.

### 2.3 Anexo: só por URL assinada, com limite; sem Drive

- Print da tela: a página não tem como capturar (sem biblioteca de terceiros) e o Python padrão não tira print; a pessoa anexa um
  arquivo (Windows: Win+Shift+S e colar numa pasta, ou "Anexar arquivo…"). Fica para a **0.7.34**, depois do chamado sem anexo.
- Como: o programa pede à `lex-conta` (ação **`chamado_anexo`**: número do chamado, nome, tipo, tamanho) e ela, depois de validar,
  chama `sol_feedback_anexo` (que registra e devolve o caminho) e devolve uma **URL assinada de envio** do bucket `sol-arquivos`
  (válida 2 horas, caminho fixo, só PUT). O arquivo sobe direto do computador para o Storage, sem passar pela função.
- Limites (além dos que a central já tem): só PNG, JPEG e WebP (sem vídeo no RADAR); **2 anexos por chamado**, **5 MB** cada; só nas 2 h
  seguintes à abertura; contados nos 5 chamados por dia da instalação. O spam fica contido: anexo só existe para chamado aberto por
  licença ativa, dentro de cota, e a URL só serve para aquele caminho.
- **Drive não**: `judicial@solverone.com.br` é encaminhamento do Cloudflare, não Conta Google; um arquivo "compartilhado" com ele não
  abre, e o link público de Drive exporia o print do escritório. Nada de link de Drive no chamado.

### 2.4 O que cabe a quem

- Produto (0.7.33): balão, formulário, prévia, trilha de ids, `POST /chamado`, `conta.enviar_chamado`, fila, "Meus chamados", manual,
  AssistONE (ajuda, tour, busca: "chamado", "suporte", "falar com a SolverONE"), Novidades ("Abertura de chamado pelo AssistONE…").
- Arquitetura: `lex-conta` v17 (`chamado` e `chamado_anexo`) **publicada em 12/Nov** e testada (código desconhecido → `codigo_desconhecido`); contrato de resposta
  `{ok, numero, motivo}` com motivos `limite`, `codigo_desconhecido`, `desativado`, `dados_invalidos`, `erro`.
- Conversa do RootifyONE (pedido pelo prompt, item 3f): aceitar as categorias do RADAR na ficha (`rootify-feedback.js` 26-29 tem lista
  fixa) e mostrar `aparelho.licenca` e `aparelho.escritorio` como "Licença" e "Escritório".

## 3. CNPJ alfanumérico (IN RFB 2.229/2024)

### 3.1 O que é (pesquisa de 12/Nov, fontes no fim)

14 posições: as 12 primeiras (raiz e ordem) aceitam dígitos e letras maiúsculas A-Z; as 2 últimas (dígitos verificadores) são sempre
numéricas. Máscara igual à de hoje: `12.ABC.345/01DE-35`. O cálculo do DV é o mesmo módulo 11 com o valor de cada caractere =
**código ASCII − 48** (0-9 → 0-9, A → 17 … Z → 42); para CNPJ só numérico dá o mesmo resultado de sempre (retrocompatível). Os CNPJs
antigos continuam válidos. Emissão desde 31/Jul/2026, gradual; a Receita continua emitindo numéricos. Exemplo oficial (Serpro):
`12ABC34501DE` → DVs `35`. Não há regra oficial excluindo letras (I, O, Q, F aparecem como recomendação de emissão em blog, não como
regra): a validação aceita A-Z inteiro. Não achamos orientação do CNJ ou dos tribunais sobre como o CNPJ novo sai nos Diários:
tratar com e sem máscara e normalizar para maiúsculas. Suporte das consultas públicas: BrasilAPI e minhareceita **sem confirmação**
(serviços pagos já aceitam); por isso a consulta é desenhada para falhar de forma suave (3.4).

### 3.2 Um módulo só: `lexsuite/documento.py`

Hoje há duas validações: `conta.py` 233-250 (já alfanumérica) e `classificar.py` 70-79 (só dígitos). Passa a existir um módulo
`documento.py` (só biblioteca padrão, sem importar nada do programa), e `conta.py`, `classificar.py`, `preferencias.py`, `cnpj.py`
e `app.py` usam ele:

- `limpar(texto)`: maiúsculas e só `[0-9A-Z]`.
- `valido(cnpj)`: 14 posições, `[0-9A-Z]{12}[0-9]{2}`, não todos iguais, DVs pelo ASCII − 48 (o `_dv_cnpj` de hoje).
- `formatar(cnpj)`: `XX.XXX.XXX/XXXX-XX` com letras; vale também para a tela (`cnpjFmt`, `radar_modelo.html` 2254, hoje só dígitos).
- `extrair(texto)`: devolve os CNPJs válidos de um texto (3.3).
- `eh_alfanumerico(cnpj)`: tem letra nas 12 primeiras (para a tela marcar "CNPJ novo" e para a consulta, 3.4).

### 3.3 Extração nos Diários

Sobre o texto em maiúsculas (os Diários já saem assim; o `.upper()` só garante):

```
(?<![0-9A-Z])([0-9A-Z]{2})\.?([0-9A-Z]{3})\.?([0-9A-Z]{3})/?([0-9A-Z]{4})-?([0-9]{2})(?![0-9A-Z])
```

Um candidato só vale quando (a) o DV confere e (b) **ou** veio com a máscara (ao menos os pontos e a barra), **ou** é só numérico (regra
de hoje), **ou** a palavra "CNPJ" aparece até 12 caracteres antes. Sem isso, 14 letras e números colados num texto jurídico ("PROCESSO
N 00123…") viram falso positivo; com DV e máscara ou contexto, a chance cai a quase zero. O CNPJ é guardado limpo (14 posições,
maiúsculas), como hoje; `banco.cnpj`, carteira (`classificar.py` 235), exclusões (`preferencias.py` 301) e a comparação da tela passam
a comparar pelo `limpar()` dos dois lados, então uma exclusão digitada como `12.abc.345/01DE-35` casa com a ação.

Testes (a Produto escreve, com números fictícios do simulador oficial da Receita): `12ABC34501DE35` válido e `…36` inválido; os
numéricos de hoje continuam válidos; extração de "CNPJ 12.ABC.345/01DE-35", "CNPJ 12ABC34501DE35" e "12.abc.345/01de-35" (minúsculas);
"ABCDEFGHIJKLMN" e um texto com 14 caracteres sem máscara e sem "CNPJ" não extraem; exclusão por CNPJ alfanumérico casa.

### 3.4 Consulta (`cnpj.py`)

- Mandar os 14 caracteres limpos na URL, como hoje (`brasilapi…/cnpj/v1/{cnpj}`, depois `minhareceita.org/{cnpj}`), sem tirar letras.
- Para CNPJ alfanumérico, resposta 400 ou 404 das duas fontes não é "não existe": grava no cache `{"situacao": "fonte_sem_suporte"}`
  com validade de **7 dias** (não 30) para tentar de novo depois, e a ação segue normal: aparece com o CNPJ, marca "CNPJ novo
  (dados da Receita indisponíveis)", sem porte, setor nem capital; "jurídico próprio provável" não se aplica (capital desconhecido);
  o cartão "com CNPJ confirmado" conta pelo DV, não pela consulta.
- Quando uma fonte responder, nada muda: os campos são os mesmos. A Operação confere o suporte real das duas fontes quando aparecer o
  primeiro CNPJ alfanumérico num Diário (não dá para testar antes: o simulador da Receita gera números fictícios, que as fontes não têm).
- Fontes: Serpro 23/Jul/2026 (serpro.gov.br/menu/noticias/noticias-2026/cnpj-alfanumerico-o-que-muda); PDF do cálculo do DV
  (serpro.gov.br/menu/noticias/videos/calculodvcnpjalfanaumerico.pdf); FAQ da Receita
  (gov.br/receitafederal/.../perguntas-e-respostas/cnpj/cnpj-alfanumerico.pdf); Fazenda, primeiro CNPJ alfanumérico (gov.br/fazenda, jul/2026);
  simulador oficial (gov.br/pt-br/servicos/simulador-cnpj-alfanumerico).

## 4. Ordem sugerida para a 0.7.33 e o que falta do dono

1. CNPJ alfanumérico (3): só robô, sem nuvem, risco baixo, já atrasado em relação à Receita.
2. Critérios por pessoa (1): robô e tela; planilha completa (decisão da Arquitetura, 1.5).
3. Chamados (2): tela e robô na 0.7.33; `lex-conta` v17 já publicada; anexo na 0.7.34. Prompt para a Produto: `documentacao/PROMPT-PRODUTO-0.7.33-2026-11-12.md`.

Definição de pronto (5 pontos) para os três: manual e (?) ("critérios são seus, neste computador"; "abrir um chamado"; "CNPJ novo"),
AssistONE (ajuda, tour, busca), Novidades formais e curtas, termos **sem mudança** (o chamado manda só o que a pessoa vê e aprova; o
texto 1.0 já cobre suporte e dados de contato), e-mail de boas-vindas sem mudança.
