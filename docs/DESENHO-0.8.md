# JUDICIAL 0.8 · Desenho da conta na nuvem (08/Nov/2026)

Documento de arquitetura, aprovado em partes pelo dono em 08/Nov/2026 (decisões D1 a D8 abaixo). **Leia a seção 0.1 antes das seções 3 a 7: elas precisam ser reescritas em cima do que a 0.7.9 já colocou na nuvem.** **Nenhum código, SQL
ou tela sai deste desenho antes de o dono aprovar o conjunto.** Nenhum SQL roda sem a revisão dele (regra C10 da
plataforma). Quem for implementar lê este arquivo, `robo/ARQUITETURA.md`, `robo/PENDENCIAS.md` e, no rootify-one,
`PLATAFORMA-DADOS.md` e a diretriz geral.

## 0. Em uma página

Hoje (0.7.5) o robô roda no computador do escritório, grava a planilha `LexSuiteONE.xlsx` no Drive e mostra a tela em
`127.0.0.1`. O suporte só enxerga o que o Drive carrega. Na 0.8:

1. Cada escritório ganha uma **conta** no banco da SolverONE (Supabase, projeto `solverone-app`, São Paulo) com um
   **código de cliente `LEX-XXXX-XXXX`**, criado pela equipe no RootifyONE e enviado no e-mail de boas-vindas.
2. Na instalação, a tela do robô pede o código e faz um **pareamento**: o robô mostra 6 dígitos, alguém aprova (o
   responsável do escritório pelo site, ou a equipe pelo RootifyONE) e o robô recebe a **credencial daquele
   computador**, guardada em `conta.json` na pasta do robô, revogável a qualquer hora.
3. A cada rodada o robô manda para a nuvem um **batimento** (versão, última rodada, contagens) e a **lista do dia**: só
   o que passou nas regras do escritório, só os campos que já saem hoje na planilha, sem sócios e sem o trecho do
   Diário. A nuvem guarda **45 dias**; a planilha do Drive continua com 365.
4. O site **judicial.solverone.com.br/app/** mostra a lista. Entra-se por **link no e-mail** (Supabase Auth; e-mail
   enviado pelo Resend). A pessoa só vê a conta que inclui o e-mail dela. Sem biblioteca, sem script de terceiros,
   e a única conversa externa é com o endereço exato do nosso projeto no Supabase.
5. No **RootifyONE**, a aba Plataforma (Supabase) ganha a tela **LexSuiteONE · Contas**: criar conta e código,
   convidar e-mails, pausar, ver batimentos e computadores, aprovar e revogar computadores.
6. **Custo zero** no piloto. **Antes de entrar no ar: termo de tratamento de dados com a KR Law** (a SolverONE passa a
   ser operadora dos dados do escritório). Pendência bloqueante, ver seção 13.

### Decisões do dono (08/Nov/2026)

| # | Decisão |
|---|---|
| D1 | Exceção à regra "as páginas do produto não fazem pedido externo": **só** as páginas de login e do app, e **só** para o endereço exato do projeto no Supabase (`https://qvdvkqydhnadhewcidia.supabase.co`), **nunca** o curinga `*.supabase.co`. Página inicial, manual e 404 continuam sem nenhum pedido externo. |
| D2 | Sobe para a nuvem só o que **passa nas regras do escritório**, mais contagens. **Sócios e administradores não subem** na 0.8. |
| D3 | Retenção: **45 dias na nuvem**, 365 na planilha do Drive. |
| D4 | A credencial do computador fica no arquivo **`conta.json`** na pasta do robô, fora do Git, revogável no RootifyONE. |
| D5 | Computador novo é aprovado pelo **responsável do escritório pelo site ou pela equipe no RootifyONE**. No piloto, pelo dono. |
| D6 | Código do app `judicial`, prefixo `lex_`. **O dono está avaliando trocar o nome do produto e avisa antes de o SQL ser escrito.** Tudo que depende do nome está marcado com ⚠️NOME neste documento. |
| D7 | E-mail do link de entrada com remetente **"SolverONE <nao-responda@solverone.com.br>"**; se o modelo permitir, o assunto diz o produto. Para a 1.0: e-mail com a marca de cada suíte (seção 13). A chave SMTP é colada pelo dono no painel do Supabase, nunca no chat nem em arquivo. |
| D8 | Módulo comum da plataforma (`diretrizes.js`, AssistONE, interruptores) **fica para a 1.0**; o site da 0.8 é próprio. |

## 0.1 Alinhamento com o que já existe na nuvem (acrescentado em 08/Nov/2026, tarde)

Este desenho foi escrito de manhã a partir de uma cópia do repositório parada na 0.7.5. Entre a noite de 07/Nov e a
manhã de 08/Nov, outra sessão entregou as versões 0.7.6 a 0.7.9 e **já colocou no Supabase** um primeiro mecanismo de
licença (`nuvem/supabase/lex-licencas.sql`, `lex-admin.sql`, Edge Function `lex-conta` v3, tela "Licenças do RADAR" no
RootifyONE 0.18.13). Conferido no projeto em 08/Nov à tarde: tabelas `lex_contas` (2 linhas), `lex_usuarios`,
`lex_instalacoes`, `lex_registros`, `lex_eventos`, visão `lex_pessoas`, funções `admin_lex_*` e `lex_criar_conta`.
O robô 0.7.9 (`lexsuite/conta.py`) já confere o código LEX a cada abertura. **As seções 3 a 7 abaixo precisam ser
reescritas em cima disso, não do zero.** O que muda:

| Neste desenho | O que já existe | Decisão proposta |
|---|---|---|
| `lex_contas` com `id` uuid, `situacao`, `retencao_dias`, `frentes` | `lex_contas` com **`codigo` como chave**, `ativo`, `validade`, `max_pessoas`, `mensagem`, `documento` | manter a tabela existente; acrescentar `retencao_dias` e `frentes`; `situacao` vira `ativo` + `encerrada_em` |
| `lex_pessoas` (tabela de e-mails que entram no site, com `papel` e `situacao`) | `lex_usuarios` (e-mail chave, cadastrado pelo robô) e **visão** `lex_pessoas` | **renomear no desenho**: quem entra no site é `lex_usuarios` com uma coluna nova `acesso_site` (`nenhum` · `usuario` · `responsavel`), concedida pela equipe ou pelo responsável, **nunca pelo cadastro do robô** |
| `lex_computadores` com credencial | `lex_instalacoes` (id aleatório de 16 hex, sem credencial) | manter `lex_instalacoes`; acrescentar `credencial_hash`, `situacao` e o pareamento da seção 5 como **endurecimento** antes de a nuvem passar a receber listas |
| `lex_batimentos` | `lex_eventos` (`acesso` por dia) + `lex_instalacoes.ultima_vez` | `lex_batimentos` continua, porque guarda contagens e saúde da rodada; `lex_eventos` fica como está |
| `lex_log` | `lex_eventos` + `acesso_log` (funções `admin_lex_*` via `lab_registrar_log`) | não criar `lex_log`; ações do site e do robô entram em `lex_eventos` com tipos novos |
| funções `lex_*` via REST/RPC com credencial | Edge Function `lex-conta` com `verify_jwt = false` e chave de serviço dentro | **uma porta só para o robô**: a `lex-conta` ganha as ações `parear`, `batimento` e `lista`; as funções do site e da equipe ficam no banco (RPC), como desenhado |
| `admin_lex_criar_conta`, `admin_lex_atualizar_conta`… | `admin_lex_criar`, `admin_lex_salvar`, `admin_lex_listar`, `admin_lex_detalhe` | usar os nomes que existem; acrescentar só `admin_lex_convidar`, `admin_lex_aprovar_computador`, `admin_lex_revogar_computador`, `admin_lex_painel` |
| código LEX com dígito verificador | 8 símbolos aleatórios, sem verificador, já em uso | **não mudar o formato** (o robô 0.7.9 e o e-mail já o usam); o verificador fica fora |
| nome `judicial` em `sol_apps` | `docs/marca.json` diz **RADAR JUDICIAL** | código do app `radar-judicial`; o prefixo `lex_` fica |

Pontos de segurança do que já está no ar, para o dono decidir junto com a 0.8 (nada disso vaza dado hoje, porque a
nuvem ainda só **recebe** e nada **lê**; vira risco quando o site passar a mostrar listas):

1. Quem tem o código LEX e um id aleatório consegue, pela `lex-conta`, **cadastrar qualquer e-mail como pessoa do
   escritório** e registrar computadores sem aprovação de ninguém. Com o site da 0.8, isso daria leitura das listas a
   um estranho que soubesse o código. Por isso o acesso ao site não pode nascer do cadastro do robô (coluna
   `acesso_site`, acima) e o pareamento com credencial entra antes das listas.
2. A `lex-conta` só limita a ação `registro` (30 por hora). As demais aceitam chamadas sem limite e cada id novo cria
   uma linha em `lex_instalacoes`: dá para encher o banco grátis. Limite por conta e por id, e teto de computadores
   por conta (ex.: 20), antes da 0.8.
3. A resposta `email_em_outro_escritorio` confirma a um estranho que um e-mail existe em outra conta. Trocar por uma
   recusa genérica.
4. `lex_criar_conta` usa `search_path = public, extensions` em vez de `''`; `lex-licencas.sql` não tem o "desfazer" ao
   lado nem data no nome; o repositório não tem o verificador `teste/sql-grants.js`. Acertar num script novo datado,
   sem editar o aplicado (regra da diretriz).
5. Os scripts constam como aplicados no projeto em 08/Nov às 05h26 UTC. Confirmar com o dono se foi ele quem rodou,
   como pede a regra C10; se não foi, registrar a exceção no `PENDENCIAS.md`.

## 1. As peças e onde moram

| Peça | Onde | O que faz na 0.8 | Quem mexe |
|---|---|---|---|
| Robô (Python, só biblioteca padrão) | PC do escritório | pareia, manda batimento e lista do dia; segue gravando planilha e tela local | sessão de produto |
| Banco | Supabase `solverone-app`, `sa-east-1`, tabelas `lex_*` | contas, pessoas, computadores, listas, batimentos, log; funções que conferem tudo | SQL entregue; **o dono revisa e roda** |
| Site do produto | GitHub Pages, pasta `docs/`, domínio `judicial.solverone.com.br` | páginas novas `docs/app/` (entrar e lista); as de hoje não mudam | sessão de produto |
| RootifyONE | repositório `rootify-one` | tela LexSuiteONE · Contas na aba Plataforma (Supabase); entrada em `apps.json` | sessão de produto, PR no rootify-one |
| E-mail de entrada | Supabase Auth com SMTP do Resend | manda o link de entrada | **só o dono** configura (seção 11) |
| E-mail de boas-vindas | `docs/email/`, Resend | já existe; passa a levar o código LEX | sessão de operação |

O que **não** entra na 0.8: coletor central (DJEN lido pela nuvem), avisos por e-mail ou Telegram a partir da nuvem,
cobrança, módulo comum, app instalável. Tudo isso está na 1.0 do `robo/PENDENCIAS.md`.

## 2. Identidade do app na plataforma

Segue o contrato `PLATAFORMA-DADOS.md` (C3, C4, C8).

| Item | Valor |
|---|---|
| Código em `sol_apps` | `judicial` ⚠️NOME |
| Nome | LexSuiteONE · JUDICIAL ⚠️NOME |
| Prefixo das tabelas | `lex_` (nome da suíte; não muda se o produto mudar de nome) |
| Função de anonimização (C8) | `lex_anonimizar(uuid)` registrada em `sol_apps.funcao_anonimizar` |
| Endereço | `https://judicial.solverone.com.br/` ⚠️NOME |
| Uso por app (C4) | o site chama `sol_registrar_uso('judicial')` ao entrar |
| `solverone-dados/apps.json` | entrada com slug, nome PT/EN, URL e estado `beta` |

Diferença em relação aos apps de consumo: o JUDICIAL vive em **origem própria** (subdomínio), então **não** divide a
sessão `solverone.sessao.v1`, o cofre de IA nem o perfil do navegador com os apps de `solverone.com.br`. A conta é a
mesma (Supabase Auth do projeto), mas a sessão fica na chave própria `judicial.sessao.v1` da origem do produto. Isso é
proposital: dado de cliente B2B separado dos apps de família, como o MoneyTRIO.

Não usamos grupos (`sol_grupos`): o conceito do JUDICIAL é **escritório**, com regras próprias (pessoas por e-mail,
computadores pareados). `lex_contas` faz esse papel. Se um dia um escritório precisar de subgrupos (filiais), aí se
avalia `sol_grupos` com `governanca = 'judicial'`.

## 3. Modelo de dados

Todas as tabelas: RLS ligada, GRANT explícito por papel no mesmo arquivo, **nenhuma escrita direta** (só por função),
trigger que recusa DELETE nas tabelas de conta e log, `criado_em`/`atualizado_em` em UTC. Prefixo `lex_`.

### 3.1 `lex_contas` — o escritório

| Coluna | Tipo | Observação |
|---|---|---|
| `id` | uuid | chave |
| `codigo` | text único | `LEX-XXXX-XXXX` (seção 4); nunca muda |
| `nome` | text | razão social ou nome fantasia do escritório |
| `situacao` | text | `ativa` · `pausada` · `encerrada` (encerrada nunca volta a `ativa` sem registro no log) |
| `validade` | date, opcional | depois dela o robô para e avisa (mesmo papel da aba Controle) |
| `versao_minima` | text, opcional | robô mais antigo pede atualização antes de rodar |
| `mensagem` | text, opcional | aviso do suporte mostrado na tela do robô e no site |
| `retencao_dias` | smallint | padrão **45**; limite máximo 90 |
| `frentes` | text[] | `{'trabalhista'}` hoje; `tributario`, `civel`, `empresarial` depois |
| `criado_por`, `criado_em`, `atualizado_em` | | |

### 3.2 `lex_pessoas` — quem pode entrar no site

| Coluna | Tipo | Observação |
|---|---|---|
| `id` | uuid | |
| `conta_id` | uuid → `lex_contas` | |
| `email` | citext | e-mail convidado, em minúsculas |
| `user_id` | uuid → `auth.users`, opcional | preenchido no primeiro login daquele e-mail |
| `papel` | text | `responsavel` (aprova computadores, vê pessoas) · `usuario` (vê a lista) |
| `situacao` | text | `convidada` · `ativa` · `removida` |
| `convidada_por`, `convidada_em`, `primeiro_acesso_em`, `removida_em` | | |

Chave única `(conta_id, email)`. A mesma pessoa pode estar em mais de uma conta (contador que atende dois escritórios).
Remover = `situacao = 'removida'`; a linha fica para o histórico.

### 3.3 `lex_computadores` — cada PC com o robô

| Coluna | Tipo | Observação |
|---|---|---|
| `id` | uuid | o robô guarda este id em `conta.json` |
| `conta_id` | uuid → `lex_contas` | |
| `nome` | text | nome do computador informado pelo robô (até 60 caracteres, sem caminho de pasta) |
| `credencial_hash` | text | SHA-256 da credencial; **a credencial em claro nunca é gravada** |
| `situacao` | text | `pendente` · `ativo` · `revogado` |
| `pedido_codigo` | text, opcional | os 6 dígitos mostrados na tela do robô, só enquanto `pendente` |
| `pedido_segredo_hash` | text, opcional | hash do segredo que o robô gerou ao pedir (seção 5) |
| `pedido_expira_em` | timestamptz | 30 minutos |
| `aprovado_por` | uuid, opcional | pessoa do escritório ou equipe |
| `aprovado_via` | text | `site` · `rootify` |
| `aprovado_em`, `revogado_em`, `revogado_por`, `ultimo_batimento_em`, `versao_robo` | | |

### 3.4 `lex_batimentos` — "o robô está vivo?"

Uma linha por rodada que chega: `conta_id`, `computador_id`, `quando` (UTC), `versao_robo`, `modo` (`radar` ·
`monitor` · `abrir`), `rodada_inicio`, `rodada_fim`, `situacao_rodada` (`ok` · `erro` · `parcial`), `contagens`
(jsonb: tribunais lidos, ações lidas, ações que passaram, excluídas, erro resumido sem dado de pessoa), `saude`
(jsonb: a avaliação sem IA que já existe em `saude.py`). Retenção: 90 dias (independente da lista).

### 3.5 `lex_listas` e `lex_itens` — a lista do dia

`lex_listas`: `id`, `conta_id`, `computador_id`, `data` (dia da lista, data de Brasília), `enviada_em`, `versao_robo`,
`total_itens`, `total_lidas`, `total_excluidas`, `tribunais` (text[]), `substitui_id` (opcional: quando o mesmo dia é
reenviado, a lista nova substitui a anterior e a anterior fica marcada `substituida_em`). Chave única
`(conta_id, data, computador_id)` para o reenvio ser uma atualização, não uma duplicata.

`lex_itens`: uma linha por ação que passou nas regras. Colunas = **exatamente** os campos de `saidas.lead_para_saida`
hoje, sem sócios (D2) e sem nada que não esteja lá:

| Grupo | Colunas |
|---|---|
| chave | `id`, `lista_id`, `conta_id`, `chave_processo` (hash de tribunal + processo, para o site juntar o mesmo processo em dias diferentes) |
| ação | `tribunal`, `vara`, `processo`, `rito`, `fonte`, `data_publicacao`, `ajuizada_em`, `audiencia` (jsonb `{data, tipo}`), `link` |
| empresa | `empresas` (text[]), `cnpjs` (text[]), `razao_social`, `porte`, `atividade`, `cidade_uf`, `capital_social` |
| regra | `faixa`, `nota`, `motivos` (text[]), `cliente` (nome da carteira quando casa), `acoes_no_periodo` |
| escritório | `status` (`Novo` · `Em análise` · `Contato feito` · `Descartado`, editável pelo site), `responsavel`, `obs`, `valor_causa` (digitado pelo site), `atualizado_por`, `atualizado_em` |

O que **nunca** sobe: trecho da publicação, nome de reclamante ou de qualquer pessoa física, nome de advogado,
sócios e administradores (D2), telefone e e-mail da empresa (ficam na planilha; na nuvem só o que a tela do dia
precisa; reavaliar na 1.0), caminhos de pasta do PC, e-mail do escritório fora de `lex_pessoas`.

`status`, `responsavel`, `obs` e `valor_causa` são do escritório e **não** são sobrescritos quando a lista do dia é
reenviada: o reenvio atualiza só as colunas vindas do robô (casando por `chave_processo`).

### 3.6 `lex_log` — só inclusão

`quando` (UTC), `conta_id`, `quem` (uuid ou `computador:<id>`), `via` (`site` · `rootify` · `robo` · `banco`), `acao`,
`antes`, `depois` (jsonb). Grava: criação e alteração de conta, convite e remoção de pessoa, pedido, aprovação e
revogação de computador, mudança de status de item, limpeza por retenção. Lido pela equipe no RootifyONE e pelo
responsável do escritório (só a conta dele). Nenhum DELETE, nenhum UPDATE.

### 3.7 Retenção automática

Um job do `pg_cron` (já instalado no projeto) roda todo dia às 04:10 de Brasília: apaga `lex_itens` e `lex_listas`
com `data` mais antiga que `retencao_dias` da conta, e `lex_batimentos` com mais de 90 dias; grava uma linha em
`lex_log` com as contagens. É a **única** exceção à regra "nada se apaga", porque é a própria regra de retenção do
contrato com o escritório (LGPD, art. 15 e 16). Contas, pessoas, computadores e log nunca são apagados.

### 3.8 Tamanho esperado

| Hipótese | Valor |
|---|---|
| Ações por dia que passam nas regras, por escritório | 100 a 400 (depois da calibração da regra de "ação nova") |
| Bytes por item | ~1 KB |
| 45 dias, um escritório | ~5 a 20 MB |
| 10 escritórios | ~200 MB, dentro dos 500 MB do plano grátis |
| Batimentos | 2 a 4 por dia por computador, ~1 KB: desprezível |

## 4. O código de cliente `LEX-XXXX-XXXX`

- Alfabeto de **32 símbolos** sem `0`, `O`, `1`, `I`: `23456789ABCDEFGHJKLMNPQRSTUVWXYZ`. 8 símbolos.
- Os 7 primeiros são aleatórios (`gen_random_bytes`); o 8º é **dígito verificador** (soma ponderada módulo 32), para
  a tela do robô recusar na hora um código digitado errado, sem ir à nuvem. ~34 bilhões de combinações válidas.
- Gerado **só no banco**, pela função `admin_lex_criar_conta`, com repetição garantida única. Nunca gerado na tela.
- **Não é segredo e não dá acesso a nada sozinho**: serve para o robô dizer "sou do escritório X" ao pedir o
  pareamento, que ainda precisa de aprovação humana (seção 5). Pode ir no e-mail de boas-vindas (bloco já previsto em
  `docs/email/`), no manual e no telefone.
- Mostrado sempre com os hifens; aceito sem hifens, em minúsculas e com espaços; a tela normaliza.

## 5. Pareamento do computador (o robô nunca tem senha)

Problema a resolver: o robô precisa provar que fala em nome do escritório X, sem senha no código, sem chave secreta e
sem alguém ter de digitar uma chave longa. Solução: **aprovação humana uma vez, credencial do computador depois**,
no padrão que a plataforma já usa em `sol_aparelhos` e `sol_acesso_pedidos`.

```
Robô (tela local)                       Banco (funções)                     Quem aprova
---------------------                   ----------------------------        ---------------------------
1. pessoa digita LEX-…  ──────────────► lex_parear_pedir(codigo, nome_pc,
   robô gera SEGREDO aleatório            hash(SEGREDO))
   (32 bytes) e guarda na memória         → cria computador 'pendente' com
                                            6 dígitos, expira em 30 min
                        ◄──────────────   devolve {computador_id, codigo6}
2. tela mostra "Peça para o responsável
   aprovar o código 4 8 2 9 1 7"
3. a cada 5 s: lex_parear_conferir     ──► confere computador_id + hash(SEGREDO)
   (computador_id, SEGREDO)                 ainda 'pendente' → "aguardando"
                                                                            4a. site: Computadores → "Aprovar"
                                                                                digita os 6 dígitos
                                                                                → lex_aprovar_computador
                                                                            4b. RootifyONE: LexSuiteONE · Contas
                                                                                → admin_lex_aprovar_computador
                                           aprovado: gera CREDENCIAL (32 bytes),
                                           grava só SHA-256, marca 'ativo'
5. lex_parear_conferir devolve a       ◄── {credencial} UMA vez só; a função
   CREDENCIAL; robô grava conta.json       apaga a cópia temporária na mesma
                                           transação
```

Regras:

- Os 6 dígitos **não** autenticam o robô; servem para a pessoa que aprova ter certeza de que está aprovando **aquele**
  pedido (igual ao pareamento de uma TV). O que autentica o robô para **receber** a credencial é o SEGREDO que só ele
  tem, criado por ele e nunca mostrado na tela.
- A credencial em claro existe no banco só entre a aprovação e a primeira conferência bem-sucedida (coluna
  temporária, no máximo 30 minutos), depois só o hash. Nenhuma tela do site ou do RootifyONE a mostra.
- Pedido não aprovado em 30 minutos expira; a tela oferece "Pedir de novo". Máximo 5 pedidos pendentes por conta e
  10 por hora por conta.
- Revogar (site ou RootifyONE) marca `revogado`; o próximo batimento do robô recebe `revogado` e a tela diz
  "Este computador foi desligado da conta; peça um novo pareamento". O robô continua rodando local e gravando a
  planilha; só a nuvem para.
- Trocar de computador = parear de novo; o antigo é revogado pelo responsável. Reinstalar na mesma máquina com o
  `conta.json` preservado não precisa de novo pareamento.

### `conta.json` (D4)

```json
{ "codigo": "LEX-7K3M-9PQ2", "computador_id": "uuid", "credencial": "base64url de 32 bytes", "pareado_em": "2026-11-20T14:03:11Z", "pareado_via": "rootify" }
```

- Fica na pasta do robô ao lado de `config.json`; entra no `.gitignore` e na lista de "nunca compartilhar"; o
  `PREPARAR-PARA-CLIENTE.bat` apaga; o `DIAGNOSTICO.bat` não lê.
- É a credencial deste computador, como uma sessão: quem copia o arquivo consegue **enviar listas em nome daquele
  computador** até ele ser revogado. Não consegue ler nada da nuvem (as funções do robô só gravam) nem mexer na conta.
  Isso fica escrito no `SEGURANCA.md` e no manual do escritório.
- O robô grava o arquivo com permissão só do usuário (`os.open` com `0o600`; no Windows herda a pasta) e nunca o
  escreve em log, tela, planilha ou mensagem de erro (só "credencial: presente/ausente").

## 6. Robô → nuvem

### 6.1 Quando

| Momento | O que manda |
|---|---|
| Ao abrir a tela (`ABRIR.bat`), com internet | batimento `modo = 'abrir'` (versão, último sucesso); recebe a situação da conta |
| Fim de cada rodada do radar (`RODAR.bat`, agendador, "Atualizar agora") | batimento `modo = 'radar'` + lista do dia |
| Fim de rodada do monitor | batimento `modo = 'monitor'` com contagens; **a caixa do monitor não sobe na 0.8** (texto das publicações do escritório fica só local) |

### 6.2 Como

- Só biblioteca padrão (`urllib`, `json`, `hashlib`, `secrets`), só `https://`, só para a URL do projeto gravada em
  `config.json` → `nuvem.url` (padrão: a do `solverone-app`), com a `nuvem.chave_publica` (`sb_publishable_…`, pública
  por natureza; o robô **recusa** qualquer valor que comece com `sb_secret_` ou contenha `service_role`).
- Caminho: `POST <url>/rest/v1/rpc/<função>` com cabeçalhos `apikey` (chave pública) e `Content-Type: application/json`.
  A credencial do computador vai **no corpo**, como parâmetro da função, nunca na URL. Timeout 20 s, 3 tentativas
  com espera 5/15/45 s, respeitando `rede.py`.
- Corpo da lista: até **2 MB** e **5.000 itens**; acima disso o robô manda em partes (`parte 1/3`) e a função junta.
  Comprimido em gzip quando passar de 200 KB (`Content-Encoding: gzip`; o PostgREST aceita).
- Idempotente: reenviar o mesmo dia atualiza a mesma `lex_listas (conta, data, computador)`; itens casam por
  `chave_processo`; colunas do escritório não são tocadas (seção 3.5).

### 6.3 O que a nuvem responde ao batimento, e o que o robô faz

```json
{ "situacao": "ativa|pausada|encerrada|revogado", "validade": "2027-06-30", "versao_minima": "0.8.0",
  "mensagem": "…", "retencao_dias": 45, "agora": "2026-11-20T09:00:00Z" }
```

Ordem de precedência, já decidida no `PENDENCIAS.md` e mantida:

1. **Resposta da nuvem** vale e é gravada em `lexsuite.db` com a hora (`controle_nuvem`).
2. **Sem resposta** (sem internet, erro, timeout): vale a última resposta guardada se tiver menos de 30 dias; se não
   houver nenhuma, vale a **aba Controle** da planilha (mecanismo da 0.7, que continua existindo na 0.8).
3. **30 dias sem nuvem e sem planilha**: a tela avisa em amarelo e o robô **continua rodando**. Instalação local não
   trava por falta de nuvem.
4. `pausada`/`encerrada`/`revogado` ou validade vencida: o robô **não roda a rodada** e mostra a mensagem, igual ao
   que a aba Controle já faz hoje. `versao_minima` maior que a instalada: pede atualização pelo caminho assinado.

### 6.4 Falhas

- Lista não enviada fica marcada em `lexsuite.db` (`pendente_nuvem`) e é reenviada na próxima rodada, junto com a
  nova. Nada se perde; nada duplica.
- Erros 401/403 (credencial inválida ou revogada): a tela mostra o motivo em linguagem simples e o botão
  "Parear de novo". 429 (limite): espera e tenta na próxima rodada. 5xx: idem.
- Tela: linha "☁️ Nuvem: enviado às 07:12 · 318 ações · conta ativa" ou "☁️ Nuvem: sem resposta desde 18/Nov (a
  planilha continua sendo gravada)". Em PT e EN.

### 6.5 Limites no banco (por função, não por tela)

| Função | Limite |
|---|---|
| `lex_parear_pedir` | 10 por hora por conta; 5 pendentes por conta |
| `lex_parear_conferir` | 60 por hora por computador pendente |
| `lex_batimento` | 1 a cada 60 s por computador |
| `lex_enviar_lista` | 6 por hora por computador; 5.000 itens e 2 MB por chamada; campos de texto com tamanho máximo (ex.: `vara` 160, `obs` 2.000) |

## 7. Funções do banco (a interface de tudo)

Todas `SECURITY DEFINER`, `SET search_path = ''`, nomes qualificados, validação de todos os parâmetros, `REVOKE
EXECUTE … FROM public, anon` por padrão e `GRANT` só a quem chama. Ninguém lê ou grava tabela `lex_*` direto.

### 7.1 Chamadas pelo robô (papel `anon`, de propósito e anotado, como `sol_enviar_feedback`)

| Função | Faz |
|---|---|
| `lex_parear_pedir(codigo, nome_pc, segredo_hash)` → `{computador_id, codigo6, expira_em}` | confere dígito verificador e conta ativa; cria o pendente |
| `lex_parear_conferir(computador_id, segredo)` → `{estado}` ou `{estado:'aprovado', credencial}` | entrega a credencial uma vez |
| `lex_batimento(computador_id, credencial, p jsonb)` → situação da conta | grava batimento, atualiza `ultimo_batimento_em` e `versao_robo` |
| `lex_enviar_lista(computador_id, credencial, p jsonb)` → `{lista_id, itens, substituiu}` | valida, faz o upsert dos itens, grava batimento junto |

A conferência da credencial é `credencial_hash = encode(digest(credencial, 'sha256'), 'hex')` com comparação de tempo
constante, e só para computador `ativo` de conta `ativa` ou `pausada` (pausada aceita o batimento, para o robô saber
que está pausado, e recusa a lista).

### 7.2 Chamadas pelo site (papel `authenticated`; a pessoa precisa estar em `lex_pessoas` ativa)

| Função | Quem | Faz |
|---|---|---|
| `lex_minhas_contas()` | qualquer logado | contas em que o e-mail da pessoa está; vazio = "este e-mail não está ligado a nenhum escritório". Na primeira vez liga `user_id` e marca `primeiro_acesso_em` |
| `lex_dias(conta, de, ate)` | usuário | dias com lista e contagens |
| `lex_lista(conta, data)` | usuário | itens do dia |
| `lex_processo(conta, chave_processo)` | usuário | o mesmo processo em todos os dias guardados |
| `lex_atualizar_item(item, p)` | usuário | `status`, `responsavel`, `obs`, `valor_causa`; grava `lex_log` |
| `lex_computadores(conta)` | responsável | lista com situação e último batimento |
| `lex_aprovar_computador(conta, codigo6)` | responsável | aprova o pendente; log |
| `lex_revogar_computador(computador)` | responsável | revoga; log |
| `lex_pessoas(conta)` | responsável | lista (sem convidar: convidar fica na equipe na 0.8) |
| `lex_meu_log(conta, limite)` | responsável | log da própria conta |
| `lex_exportar(conta, de, ate)` | usuário | os itens do período em JSON para o site montar o CSV |

A RLS das tabelas confere `conta_id IN (contas da pessoa)` como segunda trava, mesmo sem GRANT de SELECT direto.

### 7.3 Chamadas pelo RootifyONE (papel `authenticated` **e** `eh_admin_equipe()`, com `acesso_log` como as `admin_*` de hoje)

| Função | Faz |
|---|---|
| `admin_lex_criar_conta(nome, email_responsavel, frentes, validade)` → `{conta, codigo}` | cria conta ativa, convida o responsável, gera o código |
| `admin_lex_atualizar_conta(conta, p)` | situação, validade, versão mínima, mensagem, retenção (≤ 90), frentes |
| `admin_lex_convidar_pessoa(conta, email, papel)` / `admin_lex_remover_pessoa(pessoa)` | |
| `admin_lex_listar_contas(filtro)` | contas com último batimento, computadores ativos, itens nos últimos 7 dias |
| `admin_lex_conta_detalhe(conta)` | pessoas, computadores, batimentos recentes, log |
| `admin_lex_aprovar_computador(computador, codigo6)` / `admin_lex_revogar_computador(computador)` | |
| `admin_lex_painel(dias)` | contagens por conta e por dia para o painel da equipe |

Nenhuma função da equipe devolve itens da lista de um escritório: **a equipe vê saúde e contagens, não o conteúdo**.
Suporte que precise ver a lista é convidado pelo escritório como `usuario` (fica no log do escritório).

### 7.4 LGPD

`lex_anonimizar(uid)`: troca o e-mail da pessoa em `lex_pessoas` por `anonimizado-<hash>`, marca `removida`, limpa
`responsavel`/`atualizado_por` que a apontem. Registrada em `sol_apps` e chamada por `admin_anonimizar_usuario`, como
os outros apps. Encerrar a conta do escritório não apaga nada: `situacao = 'encerrada'`, itens somem pela retenção
em 45 dias, e o escritório pode pedir exportação antes.

## 8. O site: `judicial.solverone.com.br/app/`

### 8.1 Arquivos e regra de pedidos externos (D1)

| Arquivo | O que é | Pedidos externos |
|---|---|---|
| `docs/index.html`, `docs/manual.html`, `docs/404.html` | as páginas de hoje | **nenhum** (não mudam) |
| `docs/app/index.html` | entrar e a tela da lista (uma página, telas trocadas por JavaScript) | só `https://qvdvkqydhnadhewcidia.supabase.co` |
| `docs/app/app.js`, `docs/app/app.css` | código e estilo próprios, sem biblioteca | idem |
| `docs/app/politica-de-privacidade.html` | a política da nuvem (seção 12) | nenhum |

CSP em `<meta>` nas páginas do app: `default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:;
connect-src https://qvdvkqydhnadhewcidia.supabase.co; form-action 'none'; base-uri 'none'; frame-ancestors 'none'`.
A URL do projeto fica em **um único lugar** (`app.js`, constante `NUVEM`), igual à do `config.json` do robô.

Sem `supabase-js`: duas ou três chamadas `fetch` (pedir link, trocar o token, chamar função), o mesmo padrão do
`rootify-supabase.js` e do módulo Plataforma. Sem fonte externa, sem ícone de fora, sem rastreador.

### 8.2 Entrar por link no e-mail

1. A pessoa digita o e-mail e toca **Enviar o link**. O site chama `POST /auth/v1/otp` com `{email, create_user:
   true, options: {email_redirect_to: 'https://judicial.solverone.com.br/app/'}}`. Antes, grava o marcador
   `judicial.pedidoEntrada` (e-mail e hora, vale 2 dias) no `localStorage` da origem.
2. O e-mail chega de `SolverONE <nao-responda@solverone.com.br>` (D7). O link volta para `/app/#access_token=…`.
3. Na volta, o site só aceita o token **se o marcador existir neste aparelho**; sem marcador pergunta "Este link quer
   conectar a conta x@y neste aparelho. Foi você?" (regra da diretriz contra link forjado). Aceito, guarda
   `judicial.sessao.v1` (`access_token`, `refresh_token`, `expira`, `email`) e limpa o `#` do endereço.
4. Chama `lex_minhas_contas()`. Vazio → tela "Este e-mail não está ligado a nenhum escritório. Peça ao responsável do
   seu escritório ou escreva para judicial@solverone.com.br". Uma conta → abre; mais de uma → escolher.
5. Chama `sol_registrar_uso('judicial')` e, ao sair, `POST /auth/v1/logout?scope=local` e apaga a chave.

Consequência aceita: qualquer pessoa consegue criar uma conta no Supabase por este formulário (o cadastro do projeto
é compartilhado com os apps de consumo), mas **não vê nada**: a trava é `lex_pessoas` + RLS, não o login. Limite de
pedidos de link por hora é do próprio Supabase Auth (configurável no painel; ver seção 11).

### 8.3 Telas (PT/EN, celular e computador, sem módulo comum na 0.8)

| Tela | O que tem |
|---|---|
| **Hoje** (inicial) | lista do último dia recebido: uma linha por ação (tribunal, vara, empresa, porte, faixa, nota, status), filtros por tribunal, faixa e status, busca por empresa; selo "recebido às 07:12 do computador ESCRITORIO-PC" |
| **Ficha** | a mesma ficha estruturada da tela local: cada dado numa linha; "Abrir consulta no PJe"; campos editáveis `status`, `responsável`, `obs`, `valor da causa`; histórico do mesmo processo nos 45 dias |
| **Dias** | calendário dos 45 dias com contagens; dia sem lista marcado "robô não rodou" |
| **Computadores** (só responsável) | lista, último batimento, versão do robô, **Aprovar** (digita os 6 dígitos), **Desligar** |
| **Pessoas** (só responsável) | quem pode entrar e o papel; convidar fica com a equipe na 0.8 |
| **Exportar** | CSV do período (mesmo formato da planilha, com a proteção contra fórmula já existente) |
| **Conta** | identidade sempre visível no topo (e-mail, escritório, papel, desde quando), Sair, link da política, versão do site |
| **Avisos** | `mensagem` da conta, validade próxima, robô sem batimento há mais de 2 dias |

Regras herdadas da diretriz que valem mesmo sem o módulo: identidade conectada sempre visível; janelas com três
saídas e trava de rolagem (copiar o jeito do `janela.js`, não o arquivo); Voltar do celular dentro do app; nada
editável dentro da tabela (✏️ abre a ficha); cabeçalho fixo da tabela; avisos de tela estreita; linguagem para leigo;
textos em PT e EN; contraste e alvos de toque. Tema visual: o do produto (azul-escuro e latão), não o dos apps.

### 8.4 Sem internet

O site é só leitura remota; sem internet mostra a última lista que ficou no `sessionStorage` com o selo "sem internet,
mostrando a cópia de há X min". Sem service worker na 0.8 (não há o que instalar; o PWA fica para a 1.0).

## 9. RootifyONE

- Tela **LexSuiteONE · Contas** ⚠️NOME dentro de Usuários → Plataforma (Supabase), ao lado de Contas e Feedback,
  usando `RF.Supa` (login da equipe já existente, token só em memória, chave pública). Permissão
  `lexsuite:ver | editar` para papéis Dono, Admin da plataforma e Suporte N2; Suporte N1 só vê a lista sem e-mails.
- Lista das contas (nome, código, situação, último batimento, computadores, itens nos 7 dias, validade) → ficha da
  conta (pessoas, computadores com Aprovar/Revogar, batimentos, log) → formulário "Nova conta" (nome, e-mail do
  responsável, frentes, validade) que mostra o código gerado e o botão **Copiar o bloco para o e-mail de boas-vindas**.
- Toda ação passa por `RF.mudar` (log encadeado local) **e** fica no `acesso_log`/`lex_log` do banco.
- `solverone-dados/apps.json`: entrada `judicial` ⚠️NOME com URL `https://judicial.solverone.com.br/`, estado `beta`,
  `versaoMinima` vazia. Interruptores (`recursos/judicial.json`, `recursos-do-app.json`) só na 1.0 (D8).
- O que a equipe **não** vê: itens das listas (seção 7.3).

## 10. Segurança

### 10.1 Ameaças e respostas

| Ameaça | Resposta |
|---|---|
| Alguém com a chave pública do Supabase tenta ler ou gravar `lex_*` | sem GRANT de tabela para `anon`/`authenticated`; RLS ligada; só funções, cada uma validando tudo |
| Código LEX vazado (e-mail, telefone) | não dá acesso: pareamento exige aprovação humana; limite de pedidos por conta; o responsável vê pedidos pendentes |
| Cópia do `conta.json` | só grava listas em nome daquele computador; revogável; nunca lê; o batimento mostra nome e versão do PC, que o responsável confere |
| Reenvio malicioso de lista para "sujar" a tela | só computador ativo da conta; itens casam por processo; `lex_log` registra |
| Link de entrada forjado no aparelho da vítima | marcador local "pedi este link" + pergunta "Foi você?" |
| Pessoa removida ainda com sessão | toda função confere `lex_pessoas` ativa a cada chamada, não só no login |
| Função `admin_lex_*` chamada por não-equipe | `eh_admin_equipe()` como as demais; `REVOKE … FROM public, anon`; verificador `teste/sql-grants.js` |
| Injeção pelo texto vindo do Diário | o site monta a tela por `textContent`, nunca `innerHTML` com dado; CSV com proteção de fórmula (já existe) |
| XSS por script de terceiros | CSP sem terceiros; só `connect-src` para o projeto exato (D1) |
| Pausa do projeto grátis | `sol_pulso` já resolve; o batimento diário do robô é mais um sinal |
| Segredo no repositório | nenhum: URL e chave pública são públicas; SMTP do Resend fica só no painel do Supabase (dono); Gitleaks na CI |
| Robô usando chave secreta por engano | recusa `sb_secret_`/`service_role` no `config.json` |

### 10.2 Regras de entrega do SQL

Um arquivo `supabase/2026-MM-DD-judicial-0.8.sql` ⚠️NOME neste repositório, com: cabeçalho explicando o que cria;
`CREATE` sempre seguido do `GRANT` e da RLS no mesmo bloco; funções com `REVOKE`/`GRANT`; triggers anti-DELETE; job do
`pg_cron`; `INSERT ... ON CONFLICT DO NOTHING` em `sol_apps`; conferência no fim; e, para cada bloco, o comando que
**desfaz**. Testado antes num Postgres local com o `stub-supabase.sql` do rootify-one e pelo `teste/sql-grants.js`.
Depois de o dono aplicar: rodar o advisor de segurança do Supabase e anotar o resultado no `PENDENCIAS.md`.

## 11. O que só o dono faz (passo a passo, quando chegar a hora)

Nada disso precisa ser feito agora. A ordem é a da implementação; cada passo tem um "como conferir".

1. **Resend → chave só de SMTP.** resend.com → API Keys → Create API Key → nome `supabase-auth-smtp`, permissão
   **Sending access**, domínio `solverone.com.br` → Create → copiar. Não colar em lugar nenhum além do passo 2.
2. **Supabase → SMTP próprio.** supabase.com → projeto `solverone-app` → Authentication → Emails → **SMTP Settings** →
   Enable Custom SMTP → Sender email `nao-responda@solverone.com.br`, Sender name `SolverONE`, Host
   `smtp.resend.com`, Port `465`, Username `resend`, Password = a chave do passo 1 → Save. Conferir: pedir um link de
   entrada e ver o e-mail chegar com esse remetente.
3. **Supabase → limite de e-mails.** Authentication → Rate Limits → e-mails por hora: 30 (cabe no Resend grátis,
   100 por dia). Conferir: a tela mostra 30.
4. **Supabase → endereços de volta.** Authentication → URL Configuration → Redirect URLs → Add
   `https://judicial.solverone.com.br/app/**` ⚠️NOME. Site URL não muda (continua a dos apps). Conferir: o link do
   e-mail volta para o app, não para `solverone.com.br`.
5. **Supabase → modelo do e-mail "Magic Link".** Authentication → Emails → Templates → Magic Link: assunto e texto em
   PT/EN entregues no pacote da 0.8. Se o modelo aceitar condição pelo endereço de volta, o assunto diz "JUDICIAL";
   se não aceitar, fica "Seu link para entrar · SolverONE" (D7). Conferir: receber um link e ler.
6. **Supabase → rodar o SQL.** Depois de revisar o arquivo: SQL Editor → New query → colar inteiro → Run → a
   conferência do fim do arquivo mostra tudo "ok". Depois: Advisors → Security → anotar.
7. **RootifyONE → criar a conta da KR Law.** Usuários → Plataforma (Supabase) → entrar com a conta da equipe →
   LexSuiteONE · Contas → Nova conta → copiar o código para o e-mail de boas-vindas.
8. **Termo de tratamento com a KR Law assinado** (seção 13) antes de ligar `situacao = 'ativa'`.

Chaves, senhas e tokens só nos painéis do Resend e do Supabase. Se algum aparecer no chat, revogar e criar outro.

## 12. LGPD: o que muda

- Até a 0.7, a SolverONE não tratava dado nenhum do escritório: tudo ficava no PC e no Drive dele. Na 0.8 a SolverONE
  passa a **guardar dados em nome do escritório** → é **operadora**; o escritório continua **controlador**. O Supabase é
  suboperador (São Paulo, sem transferência internacional).
- Dados que passam a existir na nuvem: e-mails profissionais das pessoas do escritório (`lex_pessoas`), nome do
  computador, números de processo, nomes e CNPJs de empresas (pessoa jurídica), notas e observações digitadas pelo
  escritório. **Nenhum nome de pessoa física** vindo do Diário (regra do robô, mantida), nenhum sócio (D2).
- Documentos antes de entrar no ar: **termo de tratamento de dados (contrato operador–controlador)** com a KR Law,
  **política de privacidade da nuvem** em `docs/app/politica-de-privacidade.html` (o que é guardado, por quê, onde,
  por quanto tempo, como pedir exportação e exclusão, contato `privacidade@solverone.com.br`), e registro das
  operações no `SEGURANCA.md`. Textos levam legislação e data de referência; **validar com advogado**.
- Direitos: exportar (tela Exportar e, a pedido, a equipe exporta a conta inteira); excluir (encerrar a conta +
  retenção de 45 dias; `lex_anonimizar` para a pessoa); retificar (`lex_atualizar_item`).
- Revisão de segurança e privacidade com a skill `seguranca-lgpd-gdpr` antes do pacote 0.8, como foi na 0.7.1.

## 13. Pendências criadas por este desenho

| # | Pendência | Situação |
|---|---|---|
| P1 | **Termo de tratamento de dados com a KR Law** assinado antes de a 0.8 entrar no ar (operadora–controlador; LGPD art. 39) | ⏸ aguardando o dono; **bloqueante** |
| P2 | Nome do produto: o dono avisa antes de o SQL ser escrito; tudo com ⚠️NOME muda junto (código em `sol_apps`, endereço, telas) | ⏸ aguardando o dono |
| P3 | E-mail de entrada com a marca de cada suíte (remetente "LexSuiteONE <nao-responda@…>" para o JUDICIAL, outro para o MoneyTRIO…): exige o **Send Email Hook** do Supabase Auth apontando para uma função nossa que escolhe a marca pelo endereço de volta | 🟡 1.0 |
| P4 | Módulo comum, interruptores do RootifyONE, feedback 💬 e `Fundo` no site do JUDICIAL | 🟡 1.0 (D8) |
| P5 | Caixa do monitor (publicações dos processos do escritório) na nuvem, com texto cifrado no PC antes de subir | 🟡 1.0, decidir se compensa |
| P6 | Telefone e e-mail da empresa na nuvem (hoje só na planilha) | 🟡 reavaliar na 1.0 |
| P7 | Convidar pessoas pelo próprio responsável no site (na 0.8 só a equipe convida) | 🟡 0.9 |
| P8 | Aposentar a aba Controle da planilha quando todos os escritórios estiverem na nuvem | 🟡 depois |
| P9 | Teste `teste-djen-supabase.sql` (pg_net) continua pendente: só importa para o coletor central da 1.0 | ⏸ aguardando o dono |
| P10 | Política de privacidade da nuvem e revisão de segurança 0.8 (seção 12) | 🟡 entra no pacote 0.8 |

## 14. Ordem de implementação (depois do "pode fazer")

| Etapa | Entrega | Depende de |
|---|---|---|
| 1 | SQL `judicial-0.8.sql` com testes locais e `sql-grants.js`; texto do e-mail Magic Link | D6 resolvida (nome) |
| 2 | Robô 0.8.0: `nuvem.py` (pareamento, batimento, lista), tela com código LEX e estado da nuvem, `conta.json`, testes, `SEGURANCA.md`, manual | SQL revisado (pode começar com o SQL em revisão, testando contra Postgres local) |
| 3 | Site `docs/app/` | SQL aplicado no projeto |
| 4 | RootifyONE: tela LexSuiteONE · Contas, `apps.json` | SQL aplicado; PR no rootify-one |
| 5 | Passos do dono (seção 11), conta da KR Law, termo (P1), revisão de segurança e LGPD | tudo acima |
| 6 | Publicar o robô 0.8.0 pela automação assinada; site vai junto com a `main` | aceite do dono com a KR Law avisada |

Pacote da 0.8 só é instalado na KR Law **depois** da instalação da 0.7.2 de 12/Nov assentar e com o dono presente ou
em contato, porque o pareamento precisa de alguém aprovando.

## 15. Custos e limites

| Item | Plano | Limite que importa | Quando vira custo |
|---|---|---|---|
| Supabase | grátis | 500 MB de banco, 2 projetos, pausa após 7 dias sem uso (já tratado), 50 mil usuários ativos/mês | > 500 MB ou mais de ~10 escritórios com 45 dias: Pro US$ 25/mês. Decisão do dono |
| Resend | grátis | 100 e-mails/dia, 3.000/mês (links de entrada + boas-vindas) | só com dezenas de escritórios entrando todo dia: US$ 20/mês |
| GitHub Pages | grátis | 100 GB/mês de tráfego, repositório público | repositório privado com Pages exige GitHub Team (regra: não agora) |
| Cloudflare DNS, Worker de assinatura, Email Routing | grátis | 100 mil pedidos/dia no Worker | não no horizonte |
| Robô no PC do escritório | R$ 0 | é do escritório | — |

Fase exploratória, custo zero, como a diretriz manda. Alarme de uso: a tela LexSuiteONE · Contas mostra o tamanho das
tabelas `lex_*` (função `admin_lex_painel`), e o `PENDENCIAS.md` ganha a nota quando passar de 250 MB.

## 16. O que ainda não está decidido e eu decidi provisoriamente

- Nome do computador: o robô manda `platform.node()` cortado em 60 caracteres. Se o dono preferir um apelido digitado
  na tela ("PC da recepção"), é um campo a mais; proposto como opcional.
- Status dos itens: lista fixa de 4 (`Novo`, `Em análise`, `Contato feito`, `Descartado`), igual à tela local de hoje.
  Lista editável por conta fica para depois.
- A lista que o site mostra é a **do último computador que enviou** no dia; dois PCs no mesmo escritório no mesmo dia
  aparecem como duas listas e o site avisa. Caso raro; não vale lógica de fusão agora.
- `retencao_dias` editável pela equipe até 90 dias por conta; acima disso é mudança de desenho (tamanho do banco).
