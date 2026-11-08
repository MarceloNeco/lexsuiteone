# RADAR JUDICIAL 0.8 · Desenho da conta na nuvem (versão 2, 08/Nov/2026 à noite)

Documento de arquitetura. Versão 1 escrita em 08/Nov de manhã sobre a 0.7.5; **versão 2 reescrita em cima do que a
0.7.9 já colocou no Supabase** (licença por código de cliente, cadastro de pessoas, instalações, registros de erro,
função `lex-conta`, tela "Licenças do RADAR" no RootifyONE 0.18.13). Decisões do dono D1 a D8 (08/Nov) mantidas.
**Nenhum código, SQL ou tela sai deste desenho antes de o dono aprovar o conjunto; nenhum SQL roda sem a revisão dele.**
Quem for implementar lê este arquivo, `robo/ARQUITETURA.md`, `robo/PENDENCIAS.md`, `docs/QUADRO.md`,
`nuvem/supabase/*.sql`, `nuvem/supabase/functions/lex-conta/index.ts` e, no rootify-one, `PLATAFORMA-DADOS.md`,
`rootify-lex.js` e a diretriz geral. A revisão de segurança do que já está no ar está em
`documentacao/REVISAO-NUVEM-LICENCAS-2026-11-08.md`, com o SQL de correção em `nuvem/supabase/2026-11-08-lex-correcoes-seguranca.sql`.

## 0. Em uma página

Hoje (0.7.9) o programa roda no computador do escritório, confere a **licença** (código `LEX-XXXX-XXXX`) na nuvem a
cada abertura e antes de cada leitura, cadastra quem usa (nome, e-mail, função) e o CNPJ do escritório, manda erros
técnicos para diagnóstico, grava a planilha `LexSuiteONE.xlsx` no Drive e mostra a tela em `127.0.0.1`. A nuvem só
**recebe**; ninguém lê nada dela além da equipe, pela tela de licenças. Na 0.8:

1. **Endurecimento antes de qualquer leitura** (etapa 0, seção 10): limites de chamadas na `lex-conta`, teto de
   computadores por licença, resposta genérica para e-mail já cadastrado, acesso ao site separado do cadastro feito
   pelo programa, `search_path` fixo. Sem isso, a nuvem não passa a mostrar listas.
2. **Pareamento do computador**: na primeira abertura da 0.8 o programa mostra 6 dígitos; alguém aprova (o responsável
   do escritório pelo site ou a equipe pelo RootifyONE) e o programa recebe uma **credencial daquele computador**,
   guardada em `conta.json`, revogável. A licença continua sendo o código; a credencial é o que autoriza **enviar**.
3. A cada leitura o programa manda um **batimento** (versão, horário, contagens, saúde) e a **lista do dia**: só o que
   passou nas regras do escritório, só os campos que já saem na planilha, sem sócios e sem o trecho do Diário. A nuvem
   guarda **45 dias**; a planilha do Drive continua com 365.
4. O site **judicial.solverone.com.br/app/** mostra a lista. Entra-se por **link no e-mail** (Supabase Auth, enviado pelo
   Resend). Só entra quem a equipe ou o responsável do escritório marcou com acesso ao site; o cadastro feito pela tela
   do programa **não** dá acesso. Sem biblioteca, sem script de terceiros, só o endereço exato do projeto no Supabase.
5. No **RootifyONE**, a tela "Licenças do RADAR" ganha: conceder e remover acesso ao site por pessoa, aprovar e revogar
   computadores, batimentos e tamanho das listas.
6. **Custo zero** no piloto. **Antes de entrar no ar: termo de tratamento de dados com a KR Law** (a SolverONE passa a
   guardar dados em nome do escritório). Pendência bloqueante, seção 13.

### Decisões do dono (08/Nov/2026)

| # | Decisão |
|---|---|
| D1 | Exceção à regra "as páginas do produto não fazem pedido externo": **só** as páginas de login e do app, e **só** para o endereço exato do projeto no Supabase (`https://qvdvkqydhnadhewcidia.supabase.co`), **nunca** o curinga `*.supabase.co`. Início, manual e 404 continuam sem nenhum pedido externo. |
| D2 | Sobe para a nuvem só o que **passa nas regras do escritório**, mais contagens. **Sócios e administradores não subem** na 0.8. |
| D3 | Retenção: **45 dias na nuvem**, 365 na planilha do Drive. |
| D4 | A credencial do computador fica no arquivo **`conta.json`** na pasta do programa, fora do Git, revogável no RootifyONE. |
| D5 | Computador novo é aprovado pelo **responsável do escritório pelo site ou pela equipe no RootifyONE**. No piloto, pelo dono. |
| D6 | Nome do produto: **RADAR JUDICIAL** (configuração em `docs/marca.json`). Código do app na plataforma `radar-judicial`; prefixo das tabelas `lex_` (já em uso). |
| D7 | E-mail do link de entrada com remetente **"SolverONE <nao-responda@solverone.com.br>"**; se o modelo permitir, o assunto diz o produto. Para a 1.0: e-mail com a marca de cada suíte (seção 13). A chave SMTP é colada pelo dono no painel do Supabase, nunca no chat nem em arquivo. |
| D8 | Módulo comum da plataforma (`diretrizes.js`, AssistONE, interruptores) **fica para a 1.0**; o site da 0.8 é próprio. |
| D9 (08/Nov, tarde) | O SQL das licenças foi aprovado pelo dono pelo aplicativo, sem leitura do texto; não é violação. Daqui em diante SQL vai para arquivo, o dono roda depois de revisar. A Arquitetura revisa a segurança do que foi aplicado e escreve o SQL de correção em arquivo. |

## 1. As peças e onde moram

| Peça | Onde | Hoje (0.7.9) | Na 0.8 | Quem mexe |
|---|---|---|---|---|
| Programa (Python, só biblioteca padrão) | PC do escritório | confere licença, cadastra pessoa, manda erros (`lexsuite/conta.py`) | pareia, manda batimento e lista do dia (`lexsuite/nuvem.py`, novo) | Produto implementa; Arquitetura desenha |
| Instalador de um arquivo | `instalador/INSTALAR.bat` | exige código válido, grava `conta-inicial.json` | igual; nada muda | Produto |
| Banco | Supabase `solverone-app`, `sa-east-1`, tabelas `lex_*` | `lex_contas`, `lex_usuarios`, `lex_instalacoes`, `lex_registros`, `lex_eventos`, visão `lex_pessoas` | colunas novas e `lex_batimentos`, `lex_listas`, `lex_itens`; funções do site; funções novas da equipe | SQL em arquivo (Arquitetura); **o dono revisa e roda** |
| Porta do programa | Edge Function `lex-conta` (`verify_jwt = false`, chave de serviço só lá dentro) | ações `verificar` (padrão), `cadastrar`, `registro` | mais `parear`, `conferir_pareamento`, `batimento`, `lista`; limites de chamadas | Arquitetura escreve, Produto testa no Windows |
| Site do produto | GitHub Pages, `paginas/` → `ferramentas/marca.py` → `docs/` | páginas públicas | `paginas/app/` novo (entrar e lista) | Produto implementa; Arquitetura desenha |
| RootifyONE | `rootify-one/rootify-lex.js` | Licenças do RADAR: lista, criar, ficha, pessoas, computadores, histórico, erros | acesso ao site por pessoa, aprovar/revogar computador, batimentos, tamanho | Arquitetura (PR no rootify-one) |
| E-mail de entrada | Supabase Auth com SMTP do Resend | não existe | link de entrada | **só o dono** configura (seção 11) |
| E-mail de boas-vindas | `docs/email/`, Resend | leva o código (obrigatório desde a 0.7.9) | igual | Operação envia |

Fora da 0.8: coletor central (DJEN lido pela nuvem), avisos por e-mail ou Telegram a partir da nuvem, cobrança, módulo
comum, app instalável, caixa do monitor na nuvem. Tudo na 1.0 do `robo/PENDENCIAS.md`.

## 2. Identidade do app na plataforma

Segue o contrato `PLATAFORMA-DADOS.md` (C3, C4, C8, C10).

| Item | Valor |
|---|---|
| Código em `sol_apps` | `radar-judicial` (D6) |
| Nome | RADAR JUDICIAL (LexSuiteONE) |
| Prefixo das tabelas | `lex_` (já em uso; não muda com o nome do produto) |
| Função de anonimização (C8) | `lex_anonimizar(uuid)` registrada em `sol_apps.funcao_anonimizar` |
| Endereço | `https://judicial.solverone.com.br/` |
| Uso por app (C4) | o site chama `sol_registrar_uso('radar-judicial')` ao entrar |
| `solverone-dados/apps.json` | entrada com slug, nome PT/EN, URL e estado `beta` |

O RADAR vive em **origem própria** (subdomínio): não divide a sessão `solverone.sessao.v1`, o cofre de IA nem o perfil
do navegador com os apps de `solverone.com.br`. A conta de login é a mesma do projeto (Supabase Auth), mas a sessão fica
na chave `radar.sessao.v1` da origem do produto. Dado de cliente B2B separado dos apps de família, como o MoneyTRIO.

Não usamos `sol_grupos`: o conceito é **escritório** = linha de `lex_contas`, com regras próprias (pessoas por e-mail,
computadores pareados). Se um escritório precisar de filiais, aí se avalia `sol_grupos` com `governanca = 'radar-judicial'`.

## 3. Modelo de dados (em cima do que existe)

Convenções de tudo que é novo: RLS ligada, GRANT explícito por papel no mesmo arquivo, **nenhuma escrita direta** dos
papéis `anon` e `authenticated` (só funções), `service_role` só no que a `lex-conta` precisa, trigger que recusa DELETE
onde nada se apaga, horários em UTC. O que já existe **não é editado**: toda mudança vai em script novo datado com o
"desfazer" ao lado (regra da diretriz).

### 3.1 `lex_contas` — a licença do escritório (existe)

Hoje: `codigo` (chave, `LEX-XXXX-XXXX`), `escritorio`, `doc_tipo`, `documento` (CNPJ/CPF/passaporte, só dígitos e
letras), `max_pessoas`, `ativo`, `validade`, `mensagem`, `criado_em`.

Acrescentar: `retencao_dias smallint not null default 45 check (between 7 and 90)`, `frentes text[] default '{trabalhista}'`,
`max_computadores smallint not null default 20`, `encerrada_em timestamptz` (encerrada = `ativo=false` + data; nunca
volta sem registro em `lex_eventos`), `atualizado_em`.

### 3.2 `lex_usuarios` — quem usa (existe) + quem entra no site (novo)

Hoje: `email` (chave, minúsculas), `codigo` → conta, `nome`, `papel` (função no escritório, texto livre), `ultima_vez`,
`criado_em`, `atualizado_em`. Preenchido pela ação `cadastrar` da `lex-conta` (a pessoa digita na tela do programa).
A visão `lex_pessoas` acrescenta `em_computador` e `ativa` (vista nos últimos 30 dias).

Acrescentar, **separando cadastro de acesso**: `acesso_site text not null default 'nenhum' check in ('nenhum',
'usuario', 'responsavel')`, `acesso_por text` (`equipe:<uuid>` ou `site:<email>`), `acesso_em`, `user_id uuid references
auth.users` (ligado no primeiro login), `primeiro_acesso_site_em`, `removido_em` (remover = marcar; a linha fica).

Regra: **a ação `cadastrar` do programa nunca mexe em `acesso_site`**. Quem concede é a equipe (`admin_lex_acesso`) ou
um `responsavel` da mesma conta pelo site (`lex_conceder_acesso`, só para `usuario`). Assim, quem souber o código LEX
consegue, no máximo, aparecer na lista de pessoas da equipe; não consegue ler nada.

### 3.3 `lex_instalacoes` — cada computador (existe) + credencial (novo)

Hoje: `instalacao` (chave, 16 hex aleatórios gerados pelo programa ou pelo instalador), `codigo` → conta, `email`
(pessoa deste computador agora), `versao`, `primeira_vez`, `ultima_vez`.

Acrescentar: `nome_pc text` (até 60 caracteres, `platform.node()` cortado, sem caminho), `situacao text not null
default 'sem_credencial' check in ('sem_credencial', 'pendente', 'ativa', 'revogada')`, `credencial_hash text` (SHA-256;
a credencial em claro nunca fica gravada), `pedido_codigo char(6)`, `pedido_segredo_hash text`, `pedido_expira_em`,
`credencial_temp text` (só entre a aprovação e a primeira conferência, no máximo 30 min), `aprovada_por text`
(`equipe:<uuid>` ou `site:<email>`), `aprovada_via text` (`site` · `rootify`), `aprovada_em`, `revogada_em`, `revogada_por`,
`ultimo_batimento_em`.

`sem_credencial` é o estado dos computadores da 0.7.9 (hoje nenhum; os da KR Law em 12/Nov nascem assim). Eles seguem
conferindo a licença normalmente. **Só `ativa` envia lista.** Um computador `revogada` continua podendo conferir a
licença (o programa segue rodando local), mas a resposta diz `revogado` e a tela pede novo pareamento.

### 3.4 `lex_registros` (existe, erros técnicos) e `lex_eventos` (existe, histórico)

`lex_registros` fica como está, com dois acertos no script de correção: retenção de 90 dias e teto de linhas por hora.
`lex_eventos` ganha tipos novos na restrição: `pareamento_pedido`, `pareamento_aprovado`, `pareamento_expirado`,
`revogacao`, `lista`, `acesso_concedido`, `acesso_removido`, `acesso_site`, `item_alterado`, `retencao`, `conta_alterada`.
É o **log único** do produto (não se cria `lex_log`); as funções da equipe continuam gravando também em `acesso_log`
via `lab_registrar_log`.

### 3.5 `lex_batimentos` — "o programa está vivo e saudável?" (novo)

Uma linha por leitura ou abertura: `id`, `codigo`, `instalacao`, `quando`, `versao`, `modo` (`abrir` · `leitura` ·
`monitor`), `inicio`, `fim`, `situacao` (`ok` · `erro` · `parcial`), `contagens jsonb` (tribunais lidos, ações lidas,
que passaram, excluídas; erro resumido sem dado de pessoa), `saude jsonb` (a avaliação sem IA de `saude.py`).
Retenção 90 dias. Diferença para `lex_eventos.acesso`: este guarda contagens e saúde; aquele só marca o dia.

### 3.6 `lex_listas` e `lex_itens` — a lista do dia (novo)

`lex_listas`: `id`, `codigo`, `instalacao`, `data` (dia da lista, Brasília), `enviada_em`, `versao`, `total_itens`,
`total_lidas`, `total_excluidas`, `tribunais text[]`, `substituida_em`. Chave única `(codigo, data, instalacao)`: reenviar
o mesmo dia **atualiza** a mesma lista.

`lex_itens`: uma linha por ação que passou nas regras. Colunas = **exatamente** os campos de `saidas.lead_para_saida`,
sem sócios (D2):

| Grupo | Colunas |
|---|---|
| chave | `id`, `lista_id`, `codigo`, `chave_processo` (hash de tribunal + processo, para juntar o mesmo processo em dias diferentes) |
| ação | `tribunal`, `vara`, `processo`, `rito`, `fonte`, `data_publicacao`, `ajuizada_em`, `audiencia jsonb {data, tipo}`, `link` |
| empresa | `empresas text[]`, `cnpjs text[]`, `razao_social`, `porte`, `atividade`, `cidade_uf`, `capital_social` |
| regra | `faixa`, `nota`, `motivos text[]`, `cliente` (nome da carteira quando casa), `acoes_no_periodo` |
| escritório | `status` (`Novo` · `Em análise` · `Contato feito` · `Descartado`), `responsavel`, `obs` (≤ 2.000), `valor_causa`, `atualizado_por`, `atualizado_em` |

O que **nunca** sobe: trecho da publicação, nome de reclamante ou de qualquer pessoa física, nome de advogado, sócios e
administradores, telefone e e-mail da empresa (ficam na planilha; reavaliar na 1.0), caminhos de pasta, e-mails fora de
`lex_usuarios`. As colunas do grupo "escritório" são do escritório e **não** são sobrescritas pelo reenvio da lista.

### 3.7 Retenção automática

Job do `pg_cron` (já instalado) todo dia às 04:10 de Brasília: apaga `lex_itens`/`lex_listas` com `data` mais antiga que
`retencao_dias` da conta, `lex_batimentos` e `lex_registros` com mais de 90 dias; grava um evento `retencao` com as
contagens. Única exceção à regra "nada se apaga", porque é a regra de retenção do contrato (LGPD art. 15 e 16).
Contas, pessoas, instalações e eventos nunca são apagados.

### 3.8 Tamanho esperado

| Hipótese | Valor |
|---|---|
| Ações por dia que passam nas regras, por escritório | 100 a 400 (depois da calibração da regra de "ação nova") |
| Bytes por item | ~1 KB |
| 45 dias, um escritório | ~5 a 20 MB |
| 10 escritórios | ~200 MB, dentro dos 500 MB do plano grátis |
| Batimentos e eventos | poucos KB por dia por computador: desprezível |

## 4. O código de cliente `LEX-XXXX-XXXX` (existe; não muda)

Gerado só no banco por `lex_criar_conta` (chamada por `admin_lex_criar`): 8 símbolos aleatórios do alfabeto sem
`0`, `O`, `1`, `I`. **Não é segredo e não dá acesso a nada sozinho**: identifica a licença. Com a 0.8 ele passa a valer
menos ainda: enviar lista exige credencial de computador aprovado; ler exige login por e-mail com acesso concedido.
O dígito verificador da versão 1 deste desenho **sai**: o formato já está no programa, no instalador e nos e-mails.
O código nunca entra no repositório, no quadro ou em conversa (fato registrado em `docs/QUADRO.md`).

## 5. Pareamento do computador (o programa nunca tem senha)

Hoje a `lex-conta` aceita qualquer `instalacao` de 16 hex com um código válido. Para a nuvem passar a **receber listas**
e o site a **mostrá-las**, é preciso saber que o envio veio de um computador que alguém do escritório reconheceu.
Padrão: aprovação humana uma vez, credencial do computador depois (como `sol_aparelhos` e `sol_acesso_pedidos` na
plataforma).

```
Programa (tela local)                    lex-conta (ações novas)                  Quem aprova
----------------------                   ------------------------------------     --------------------------------
1. já tem codigo + instalacao (0.7.9).   acao 'parear' {codigo, instalacao,
   Gera SEGREDO (32 bytes) em memória      versao, nome_pc, segredo_hash}
   e manda só o hash          ──────────► instalação vira 'pendente' com 6 dígitos,
                                           expira em 30 min; evento pareamento_pedido
                              ◄──────────  {codigo6, expira_em}
2. Tela: "Peça para o responsável
   aprovar o código 4 8 2 9 1 7"
3. A cada 5 s: acao 'conferir_pareamento'
   {instalacao, segredo}      ──────────► confere hash(segredo); 'pendente' → "aguardando"
                                                                                 4a. site → Computadores → Aprovar →
                                                                                     digita 6 dígitos → lex_aprovar_computador
                                                                                 4b. RootifyONE → ficha da licença →
                                                                                     admin_lex_aprovar_computador
                                           aprovado: gera CREDENCIAL (32 bytes),
                                           grava hash + credencial_temp, 'ativa'
5. recebe {credencial} UMA vez; grava   ◄── devolve e apaga credencial_temp na
   conta.json                               mesma transação; evento pareamento_aprovado
```

- Os 6 dígitos só servem para quem aprova ter certeza de **qual** pedido está aprovando. O que autentica o programa
  para receber a credencial é o SEGREDO, que só ele tem e nunca aparece na tela.
- Máximo 5 pedidos pendentes e 10 pedidos por hora por licença; `max_computadores` ativos por licença (padrão 20).
  Pedido não aprovado em 30 minutos expira (evento `pareamento_expirado`); a tela oferece "Pedir de novo".
- Revogar (site ou RootifyONE) marca `revogada`; a próxima chamada do programa recebe `revogado`; a tela diz "Este
  computador foi desligado da conta; peça um novo pareamento". O programa segue rodando local e gravando a planilha.
- Computador `sem_credencial` da 0.7.9 que atualiza para a 0.8: na primeira abertura a tela explica em uma frase e
  oferece "Conectar este computador" (o fluxo acima). Enquanto não parear, tudo funciona como na 0.7.9, só a lista
  não sobe.

### `conta.json` (D4)

Hoje o bloco `conta` do `config.json` guarda `codigo`, `instalacao`, `url` e a última resposta. Na 0.8 a **credencial**
vai para um arquivo separado `conta.json`, ao lado do `config.json`:

```json
{ "instalacao": "16 hex", "credencial": "base64url de 32 bytes", "pareado_em": "2026-11-20T14:03:11Z", "pareado_via": "rootify" }
```

Entra no `.gitignore` e na lista de "nunca compartilhar"; `PREPARAR-PARA-CLIENTE.bat` apaga; `DIAGNOSTICO.bat` não lê;
gravado com permissão só do usuário; nunca em log, tela, planilha ou mensagem de erro (só "credencial: presente/ausente").
Quem copia o arquivo consegue **enviar listas em nome daquele computador** até ele ser revogado; não consegue ler nada
nem mexer na licença. Fica escrito no `SEGURANCA.md` e no manual.

## 6. Programa → nuvem

### 6.1 Quando

| Momento | Hoje (0.7.9) | Na 0.8 |
|---|---|---|
| Abrir a tela | `verificar` (licença) | `batimento` com `modo = 'abrir'` (inclui a conferência da licença; a ação `verificar` continua existindo para a 0.7.9) |
| Antes de cada leitura | `verificar` | idem, `modo = 'leitura'`, antes de começar |
| Fim de cada leitura | — | `lista` (batimento final + lista do dia) |
| Fim de leitura do monitor | — | `batimento` com contagens; **a caixa do monitor não sobe** |
| Erro técnico | `registro` | igual |

### 6.2 Como

- Só biblioteca padrão (`urllib`, `json`, `hashlib`, `secrets`), só `https://`, só para a URL da `lex-conta` já gravada
  em `config.json` (`conta.url`, padrão a do `solverone-app`). Nenhuma chave no programa: a `lex-conta` tem
  `verify_jwt = false` de propósito e a chave de serviço fica só dentro dela. O programa **recusa** qualquer URL que não
  seja `https://` nem termine em `.supabase.co/functions/v1/lex-conta` (impede config apontando para outro lugar).
- Autenticação do envio: `{instalacao, credencial}` **no corpo**, nunca na URL. A `lex-conta` compara
  `sha256(credencial)` com `credencial_hash` em tempo constante e exige `situacao = 'ativa'` e licença `ativo` e não
  vencida (licença `ativo=false` aceita `batimento`, para o programa saber que está pausado, e recusa `lista`).
- Timeout 20 s, 3 tentativas com espera 5/15/45 s, respeitando `rede.py`. Corpo da lista até **2 MB** e **5.000 itens**;
  acima disso em partes (`parte n/N`); gzip quando passar de 200 KB.
- Idempotente: reenviar o mesmo dia atualiza `lex_listas (codigo, data, instalacao)`; itens casam por `chave_processo`;
  colunas do escritório não são tocadas.

### 6.3 O que a nuvem responde e o que o programa faz

```json
{ "ok": true, "motivo": "", "escritorio": "…", "validade": "2027-06-30", "mensagem": "…",
  "computador": "ativa|pendente|sem_credencial|revogada", "retencao_dias": 45, "agora": "2026-11-20T09:00:00Z" }
```

Precedência, mantida da 0.7.9 (`conta.bloqueio`): a resposta da nuvem vale e fica guardada; sem resposta, vale a última
boa por até **15 dias** (`DIAS_SEM_RESPOSTA`, já em uso; os 30 dias da versão 1 deste desenho saem); depois disso a tela
bloqueia a leitura e pede para conferir a internet, como hoje. A aba Controle da planilha continua existindo como
segunda fonte de `mensagem` e `versao_minima` até ser aposentada (pendência P8).

### 6.4 Falhas

Lista não enviada fica marcada em `lexsuite.db` (`pendente_nuvem`) e vai na próxima leitura; nada se perde nem duplica.
401/403 (credencial inválida ou revogada): tela explica e oferece "Conectar este computador". 429 (limite) e 5xx: tenta na
próxima leitura. Linha na tela: "☁️ Nuvem: enviado às 07:12 · 318 ações · licença ativa" ou "☁️ Nuvem: sem resposta
desde 18/Nov (a planilha continua sendo gravada)". PT e EN.

### 6.5 Limites na `lex-conta` (por ação)

| Ação | Limite |
|---|---|
| `verificar`, `batimento` | 1 por minuto por instalação; 120 por hora por licença |
| `cadastrar` | 10 por hora por instalação |
| `registro` | 30 por hora por instalação (existe) + 300 por hora no total sem instalação |
| `parear` | 10 por hora por licença; 5 pendentes por licença; `max_computadores` ativos |
| `conferir_pareamento` | 60 por hora por instalação pendente |
| `lista` | 6 por hora por instalação; 5.000 itens e 2 MB por chamada; tamanhos máximos por campo |
| instalação nova (qualquer ação) | só com código válido, e no máximo `max_computadores` + 5 linhas por licença (as excedentes são recusadas) |

Contagem pelas próprias tabelas (`lex_eventos`, `lex_batimentos`, `lex_registros`) com índice por `(instalacao, criado_em)`;
sem tabela extra de contadores.

## 7. Funções: a interface de tudo

### 7.1 Porta do programa: Edge Function `lex-conta` (papel: nenhum; chave de serviço dentro)

| Ação | Faz | Estado |
|---|---|---|
| (padrão) `verificar` | confere a licença, atualiza instalação, evento `acesso` 1× por dia | existe |
| `cadastrar` | nome, e-mail, função, documento do escritório; **não toca `acesso_site`** | existe; resposta `email_em_outro_escritorio` vira `dados_invalidos` genérico |
| `registro` | erro técnico | existe |
| `parear` / `conferir_pareamento` | seção 5 | novo |
| `batimento` | contagens e saúde; resposta da seção 6.3 | novo |
| `lista` | valida, upsert de `lex_listas`/`lex_itens`, batimento junto | novo |

Toda ação valida tamanho e formato de cada campo, aplica os limites da 6.5 e grava `lex_eventos` quando muda algo.
Resposta de erro nunca diz se um e-mail ou código existe em outra conta.

### 7.2 Site (papel `authenticated`; a pessoa precisa estar em `lex_usuarios` com `acesso_site <> 'nenhum'` e `removido_em` nulo)

| Função | Quem | Faz |
|---|---|---|
| `lex_minhas_contas()` | qualquer logado | licenças em que o e-mail da pessoa tem acesso; vazio = "este e-mail não está ligado a nenhum escritório". Na primeira vez liga `user_id` e marca `primeiro_acesso_site_em`; evento `acesso_site` 1× por dia |
| `lex_dias(codigo, de, ate)` | usuário | dias com lista e contagens |
| `lex_lista(codigo, data)` | usuário | itens do dia |
| `lex_processo(codigo, chave_processo)` | usuário | o mesmo processo nos dias guardados |
| `lex_atualizar_item(item, p)` | usuário | `status`, `responsavel`, `obs`, `valor_causa`; evento `item_alterado` |
| `lex_computadores(codigo)` | responsável | instalações com situação e último batimento |
| `lex_aprovar_computador(codigo, codigo6)` | responsável | aprova o pendente (seção 5) |
| `lex_revogar_computador(instalacao)` | responsável | revoga |
| `lex_pessoas_da_conta(codigo)` | responsável | pessoas, acesso ao site, última vez |
| `lex_conceder_acesso(codigo, email, nivel)` | responsável | só `usuario` ou `nenhum` para e-mail já cadastrado na conta; `responsavel` só pela equipe |
| `lex_meu_historico(codigo, limite)` | responsável | `lex_eventos` da própria licença |
| `lex_exportar(codigo, de, ate)` | usuário | itens do período para o site montar o CSV |

RLS como segunda trava: política de SELECT em `lex_listas`/`lex_itens` para `authenticated` com
`codigo in (select codigo from lex_usuarios where user_id = auth.uid() and acesso_site <> 'nenhum' and removido_em is null)`,
mesmo sem GRANT direto de tabela. Toda função confere o acesso **a cada chamada**, não só no login.

### 7.3 Equipe (papel `authenticated` **e** `eh_admin_equipe()`, log em `acesso_log` como as `admin_lex_*` de hoje)

| Função | Estado |
|---|---|
| `admin_lex_listar`, `admin_lex_detalhe`, `admin_lex_criar`, `admin_lex_salvar`, `admin_lex_erros_sem_codigo` | existem; `admin_lex_salvar` passa a aceitar `retencao_dias`, `frentes`, `max_computadores`; `admin_lex_detalhe` traz batimentos recentes e tamanho das listas |
| `admin_lex_convidar(codigo, email, nome, nivel)` | novo: cria a pessoa já com acesso ao site (quem ainda não passou pela tela do programa) |
| `admin_lex_acesso(email, nivel)` | novo: `nenhum` · `usuario` · `responsavel`; evento `acesso_concedido`/`acesso_removido` |
| `admin_lex_aprovar_computador(instalacao, codigo6)`, `admin_lex_revogar_computador(instalacao)` | novo |
| `admin_lex_painel(dias)` | novo: contagens por licença e por dia, tamanho das tabelas `lex_*` (alarme de uso) |

A equipe vê saúde, contagens e pessoas; **não vê itens das listas**. Suporte que precise ver uma lista é convidado pelo
escritório como `usuario` (fica no histórico do escritório).

### 7.4 LGPD

`lex_anonimizar(uid)`: para quem tem `user_id`, troca o e-mail em `lex_usuarios` por `anonimizado-<hash>`, zera nome e
função, marca `removido_em`, limpa `responsavel`/`atualizado_por` que a apontem em `lex_itens` e `email` em
`lex_instalacoes`/`lex_eventos`. Registrada em `sol_apps` e chamada por `admin_anonimizar_usuario`. Pessoa só cadastrada
pelo programa (sem login) é anonimizada pela equipe a pedido, com a mesma função por e-mail (`admin_lex_anonimizar_email`).
Encerrar a licença não apaga nada: `ativo=false` + `encerrada_em`; itens somem pela retenção em 45 dias; o escritório
pode pedir exportação antes.

## 8. O site: `judicial.solverone.com.br/app/`

### 8.1 Arquivos e regra de pedidos externos (D1)

| Arquivo | O que é | Pedidos externos |
|---|---|---|
| `paginas/index.html`, `paginas/manual.html`, `paginas/404.html` → `docs/` | as páginas de hoje | **nenhum** (não mudam) |
| `paginas/app/index.html` → `docs/app/index.html` | entrar e a tela da lista (uma página, telas trocadas por JavaScript) | só `https://qvdvkqydhnadhewcidia.supabase.co` |
| `paginas/app/app.js`, `app.css` | código e estilo próprios, sem biblioteca | idem |
| `paginas/app/privacidade.html` | a política da nuvem (seção 12) | nenhum |

CSP em `<meta>` nas páginas do app: `default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:;
connect-src https://qvdvkqydhnadhewcidia.supabase.co; form-action 'none'; base-uri 'none'; frame-ancestors 'none'`.
A URL do projeto fica em **um lugar** (`app.js`, constante `NUVEM`), a mesma do `conta.py` e do instalador. Sem
`supabase-js`: chamadas `fetch` diretas, como `rootify-supabase.js`. O nome vem de `marca.json` pelo `marca.py`.

### 8.2 Entrar por link no e-mail

1. A pessoa digita o e-mail e toca **Enviar o link**. O site chama `POST /auth/v1/otp` com `{email, create_user: true,
   options: {email_redirect_to: 'https://judicial.solverone.com.br/app/'}}` e grava o marcador `radar.pedidoEntrada`
   (e-mail e hora, vale 2 dias) no `localStorage` da origem.
2. O e-mail chega de `SolverONE <nao-responda@solverone.com.br>` (D7). O link volta para `/app/#access_token=…`.
3. Na volta, o site só aceita o token **se o marcador existir neste aparelho**; sem marcador pergunta "Este link quer
   conectar a conta x@y neste aparelho. Foi você?". Aceito, guarda `radar.sessao.v1` e limpa o `#`.
4. `lex_minhas_contas()`. Vazio → "Este e-mail não está ligado a nenhum escritório. Peça ao responsável do seu
   escritório ou escreva para judicial@solverone.com.br". Uma licença → abre; mais de uma → escolher.
5. `sol_registrar_uso('radar-judicial')`; ao sair, `POST /auth/v1/logout?scope=local` e apaga a chave.

Consequência aceita: qualquer pessoa consegue criar uma conta no Supabase por este formulário (o cadastro do projeto é
compartilhado com os apps de consumo), mas **não vê nada**: a trava é `acesso_site` + RLS. Limite de links por hora é do
Supabase Auth (seção 11).

### 8.3 Telas (PT/EN, celular e computador, sem módulo comum na 0.8)

| Tela | O que tem |
|---|---|
| **Hoje** | lista do último dia recebido: uma linha por ação (tribunal, vara, empresa, porte, faixa, nota, status), filtros por tribunal, faixa e status, busca por empresa; selo "recebido às 07:12 do computador ESCRITORIO-PC" |
| **Ficha** | a ficha estruturada da tela local; "Abrir consulta no PJe"; `status`, `responsável`, `obs`, `valor da causa` editáveis; histórico do processo nos 45 dias |
| **Dias** | calendário dos 45 dias com contagens; dia sem lista marcado "o RADAR não leu" |
| **Computadores** (responsável) | lista, último batimento, versão, **Aprovar** (6 dígitos), **Desligar** |
| **Pessoas** (responsável) | quem tem acesso ao site e quem só está cadastrado; dar/retirar acesso de usuário |
| **Exportar** | CSV do período (formato da planilha, com a proteção contra fórmula que já existe) |
| **Conta** | identidade sempre visível no topo (e-mail, escritório, nível, desde quando), Sair, política, versão |
| **Avisos** | `mensagem` da licença, validade próxima, computador sem batimento há mais de 2 dias |

Regras da diretriz que valem mesmo sem o módulo: identidade conectada visível; janelas com três saídas e trava de
rolagem (copiar o jeito do `janela.js`, não o arquivo); Voltar do celular dentro do app; nada editável dentro da tabela
(✏️ abre a ficha); cabeçalho fixo da tabela; avisos de tela estreita; linguagem para leigo; PT/EN; contraste e alvos de
toque. Visual: o do produto (azul-escuro e latão), não o dos apps de família.

### 8.4 Sem internet

Só leitura remota; sem internet mostra a última lista do `sessionStorage` com "sem internet, mostrando a cópia de há X
min". Sem service worker na 0.8.

## 9. RootifyONE (`rootify-lex.js`, existe)

- Ficha da licença ganha: **Acesso ao site** por pessoa (nenhum/usuário/responsável, `admin_lex_acesso`), **Convidar**
  (`admin_lex_convidar`), **Aprovar** e **Desligar** em cada computador, situação da credencial, **Batimentos** (últimos
  7 dias com contagens e saúde), **Listas** (dias, itens, tamanho), e os campos `retencao_dias`, `frentes`,
  `max_computadores` no formulário (`admin_lex_salvar`).
- Lista das licenças ganha "último batimento" e "itens 7 dias" (`admin_lex_listar`); painel com tamanho das tabelas
  `lex_*` (`admin_lex_painel`) e aviso quando passar de 250 MB.
- Permissões: as já existentes `licencas:ver | criar | editar`, mais `licencas:acesso` (conceder acesso ao site; Dono,
  Admin da plataforma e Suporte N2). Tudo por `RF.mudar` + `acesso_log`.
- `solverone-dados/apps.json`: entrada `radar-judicial`. Interruptores só na 1.0 (D8).
- A equipe **não vê itens das listas** (seção 7.3).

## 10. Segurança

### 10.1 Etapa 0: endurecer o que já está no ar (antes de qualquer lista)

Achados da revisão `documentacao/REVISAO-NUVEM-LICENCAS-2026-11-08.md`, resumidos:

| # | Achado | Correção | Onde |
|---|---|---|---|
| R1 | Quem tem o código consegue cadastrar qualquer e-mail como pessoa da licença | `acesso_site` separado do cadastro (3.2); a `lex-conta` nunca mexe nele | SQL 0.8 + `lex-conta` |
| R2 | Sem limite de chamadas fora de `registro`; cada id novo cria linha em `lex_instalacoes` | limites da 6.5; teto de instalações por licença (trigger no banco + checagem na função) | SQL de correção (trigger) + `lex-conta` |
| R3 | `email_em_outro_escritorio` confirma a um estranho que um e-mail existe | resposta genérica `dados_invalidos`; o texto certo só na tela do programa quando a pessoa é da licença | `lex-conta` |
| R4 | `lex_criar_conta` com `search_path = public, extensions`; scripts sem data e sem "desfazer"; sem `teste/sql-grants.js` | recriar a função com `search_path = ''`; scripts novos datados com o desfazer; copiar o verificador do rootify-one para `teste/` | SQL de correção |
| R5 | `lex_registros.mensagem` aceita 2.000 caracteres livres do instalador (pode trazer caminho com nome de usuário do Windows) | a `lex-conta` apaga `C:\Users\<nome>` e e-mails do texto antes de gravar; retenção 90 dias | `lex-conta` + SQL de correção |
| R6 | `verify_jwt = false` na `lex-conta` | **de propósito e aceito**: o programa não tem chave; o que protege é a validação e os limites. Anotado |
| R7 | Pessoa só cadastrada (sem login) sem caminho de anonimização | `admin_lex_anonimizar_email` | SQL 0.8 |

### 10.2 Ameaças e respostas (0.8 inteira)

| Ameaça | Resposta |
|---|---|
| Chave pública do Supabase usada para ler ou gravar `lex_*` | sem GRANT de tabela para `anon`/`authenticated`; RLS; só funções validando tudo |
| Código LEX vazado | só identifica; enviar exige credencial aprovada; ler exige acesso concedido; limites por licença |
| Cópia do `conta.json` | só envia listas em nome daquele computador; revogável; o responsável vê nome e versão do PC |
| Reenvio malicioso para "sujar" a tela | só instalação `ativa`; itens casam por processo; evento `lista` |
| Link de entrada forjado no aparelho da vítima | marcador local "pedi este link" + "Foi você?" |
| Pessoa removida com sessão viva | toda função confere `acesso_site` e `removido_em` a cada chamada |
| Função da equipe chamada por não-equipe | `eh_admin_equipe()`; `REVOKE … FROM public, anon`; verificador `teste/sql-grants.js` |
| Injeção pelo texto do Diário | tela monta por `textContent`; CSV com proteção de fórmula |
| Script de terceiros | CSP sem terceiros; `connect-src` só o projeto exato (D1) |
| Pausa do projeto grátis | `sol_pulso` + batimentos diários |
| Segredo no repositório | nenhum: URL pública; SMTP do Resend só no painel; Gitleaks na CI |
| Edge Function recebendo URL de outro projeto no `config.json` | programa recusa URL fora de `https://*.supabase.co/functions/v1/lex-conta` |

### 10.3 Regras de entrega do SQL

Scripts em `nuvem/supabase/`, nome `AAAA-MM-DD-<assunto>.sql`, cada bloco com o comando que **desfaz** ao lado; `CREATE`
seguido de GRANT e RLS; funções com `REVOKE`/`GRANT`; conferência no fim; testados num Postgres local com o
`stub-supabase.sql` do rootify-one e pelo `teste/sql-grants.js` (a copiar para este repositório). Script aplicado não se
edita. Depois de o dono aplicar: advisor de segurança do Supabase, resultado no `PENDENCIAS.md`.

## 11. O que só o dono faz (passo a passo, quando chegar a hora)

1. **Revisar e rodar o SQL de correção** `nuvem/supabase/2026-11-08-lex-correcoes-seguranca.sql`: supabase.com →
   projeto `solverone-app` → SQL Editor → New query → colar inteiro → Run → a conferência do fim mostra "ok".
2. **Resend → chave só de SMTP.** resend.com → API Keys → Create API Key → nome `supabase-auth-smtp`, permissão
   **Sending access**, domínio `solverone.com.br` → Create → copiar. Não colar em lugar nenhum além do passo 3.
3. **Supabase → SMTP próprio.** Authentication → Emails → SMTP Settings → Enable Custom SMTP → Sender email
   `nao-responda@solverone.com.br`, Sender name `SolverONE`, Host `smtp.resend.com`, Port `465`, Username `resend`,
   Password = a chave do passo 2 → Save. Conferir: pedir um link e ver o remetente.
4. **Supabase → limite de e-mails.** Authentication → Rate Limits → e-mails por hora: 30.
5. **Supabase → endereços de volta.** Authentication → URL Configuration → Redirect URLs → Add
   `https://judicial.solverone.com.br/app/**`. Site URL não muda.
6. **Supabase → modelo "Magic Link".** Authentication → Emails → Templates → Magic Link: assunto e texto PT/EN do pacote
   da 0.8. Se o modelo aceitar condição pelo endereço de volta, o assunto diz "RADAR JUDICIAL"; senão "Seu link para
   entrar · SolverONE" (D7).
7. **Revisar e rodar o SQL da 0.8** (quando existir), depois Advisors → Security.
8. **RootifyONE → licença da KR Law**: conceder acesso ao site ao Leandro (`responsavel`) e aprovar o computador quando
   o 6 dígitos aparecer na tela do programa.
9. **Termo de tratamento com a KR Law assinado** (seção 13) antes de conceder o primeiro acesso ao site.

Chaves, senhas e tokens só nos painéis do Resend e do Supabase. Se algum aparecer no chat, revogar e criar outro.

## 12. LGPD: o que muda

- Desde a 0.7.9 a SolverONE já guarda em nome do escritório: e-mails profissionais e nomes de quem usa, função, CNPJ do
  escritório, id de computador e erros técnicos. Na 0.8 entram números de processo, nomes e CNPJs de empresas (pessoa
  jurídica) e observações digitadas. A SolverONE é **operadora**; o escritório, **controlador**; o Supabase, suboperador
  em São Paulo, sem transferência internacional. **Nenhum nome de pessoa física vindo do Diário**, nenhum sócio (D2).
- Antes de entrar no ar: **termo de tratamento de dados** com a KR Law (operador–controlador, LGPD art. 39), **política
  de privacidade da nuvem** em `paginas/app/privacidade.html` (o que é guardado, por quê, onde, por quanto tempo,
  exportação e exclusão, contato `privacidade@solverone.com.br`), registro das operações no `SEGURANCA.md`. Textos com
  legislação e data de referência; **validar com advogado**. O cadastro da 0.7.9 já pede aviso de privacidade
  (pendência "termos de uso e aviso de privacidade do cadastro" do `PENDENCIAS.md`): o mesmo texto cobre os dois.
- Direitos: exportar (tela Exportar; a equipe exporta a licença inteira a pedido); excluir (encerrar + retenção de 45
  dias; `lex_anonimizar` e `admin_lex_anonimizar_email`); retificar (`lex_atualizar_item`, `cadastrar`).
- Revisão de segurança e privacidade com a skill `seguranca-lgpd-gdpr` antes do pacote 0.8, como na 0.7.1.

## 13. Pendências criadas por este desenho

| # | Pendência | Situação |
|---|---|---|
| P1 | **Termo de tratamento de dados com a KR Law** assinado antes de a 0.8 entrar no ar | ⏸ aguardando o dono; **bloqueante** |
| P2 | ~~Nome do produto~~ resolvido: RADAR JUDICIAL, código `radar-judicial` | ✅ 08/Nov |
| P3 | E-mail de entrada com a marca de cada suíte: **Send Email Hook** do Supabase Auth apontando para função nossa | 🟡 1.0 |
| P4 | Módulo comum, interruptores, feedback 💬 e `Fundo` no site | 🟡 1.0 (D8) |
| P5 | Caixa do monitor na nuvem, cifrada no PC antes de subir | 🟡 1.0, decidir se compensa |
| P6 | Telefone e e-mail da empresa na nuvem | 🟡 reavaliar na 1.0 |
| P7 | Responsável convidar pessoa que ainda não passou pela tela do programa (hoje só a equipe) | 🟡 0.9 |
| P8 | Aposentar a aba Controle da planilha | 🟡 depois |
| P9 | Teste `teste-djen-supabase.sql` (pg_net): só para o coletor da 1.0 | ⏸ aguardando o dono |
| P10 | Política de privacidade da nuvem e revisão de segurança 0.8 | 🟡 entra no pacote 0.8 |
| P11 | **Etapa 0 de segurança** (R1 a R7): SQL de correção escrito; o dono revisa e roda; `lex-conta` v4 depois do "pode" | 🟡 Arquitetura |
| P12 | Copiar `teste/sql-grants.js` do rootify-one para este repositório e ligar na CI | 🟡 Arquitetura |

## 14. Ordem de implementação (depois do "pode fazer")

| Etapa | Entrega | Quem | Depende de |
|---|---|---|---|
| 0 | SQL de correção (dono roda) + `lex-conta` v4 com limites, resposta genérica, limpeza de `mensagem` | Arquitetura | revisão do dono |
| 1 | SQL da 0.8: colunas novas, `lex_batimentos`, `lex_listas`, `lex_itens`, funções do site e da equipe, retenção, `sol_apps`; texto do e-mail Magic Link | Arquitetura | etapa 0 aplicada |
| 2 | `lex-conta` v5: `parear`, `conferir_pareamento`, `batimento`, `lista` | Arquitetura | SQL da 0.8 aplicado |
| 3 | Programa 0.8.0: `nuvem.py`, tela (conectar computador, estado da nuvem), `conta.json`, testes, `SEGURANCA.md`, manual | Produto, pelo desenho | etapa 2 |
| 4 | Site `paginas/app/` | Produto, pelo desenho | etapa 1 |
| 5 | RootifyONE: ficha da licença ampliada, `apps.json` | Arquitetura (PR no rootify-one) | etapa 1 |
| 6 | Passos do dono (seção 11), termo (P1), revisão de segurança e LGPD | dono, Arquitetura | tudo acima |
| 7 | Publicação do programa 0.8.0 pela Operação, com o "publica a versão" do dono; site vai junto | Operação | aceite do dono |

A 0.8 só entra na KR Law depois da instalação de 12/Nov assentar, com o dono presente ou em contato (o pareamento
precisa de alguém aprovando).

## 15. Custos e limites

| Item | Plano | Limite que importa | Quando vira custo |
|---|---|---|---|
| Supabase | grátis | 500 MB de banco, pausa após 7 dias sem uso (tratado), 500 mil chamadas de Edge Function por mês | > 500 MB ou mais de ~10 escritórios com 45 dias: Pro US$ 25/mês. Decisão do dono |
| Resend | grátis | 100 e-mails/dia, 3.000/mês | dezenas de escritórios entrando todo dia: US$ 20/mês |
| GitHub Pages | grátis | repositório público | repositório privado com Pages exige GitHub Team (regra: não agora) |
| Cloudflare | grátis | 100 mil pedidos/dia nos Workers | não no horizonte |
| Programa no PC do escritório | R$ 0 | | |

Chamadas da `lex-conta` por escritório e dia: ~2 aberturas + ~2 leituras × 2 ações + conferências ≈ 10 a 20. Mil
escritórios ainda caberiam no grátis. Alarme de uso: `admin_lex_painel` mostra o tamanho das tabelas `lex_*`.

## 16. Decidido provisoriamente (o dono pode mudar)

- Nome do computador: `platform.node()` cortado em 60 caracteres; apelido digitado é opcional.
- Status dos itens: lista fixa de 4, igual à tela local.
- Dois computadores do mesmo escritório no mesmo dia: duas listas, o site avisa. Sem lógica de fusão agora.
- `retencao_dias` entre 7 e 90 por licença; acima disso é mudança de desenho.
- `max_computadores` padrão 20; a equipe ajusta por licença.
