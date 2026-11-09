# Revisão de segurança da nuvem das licenças (RADAR JUDICIAL 0.7.9) — 08/Nov/2026

Pedido do dono (08/Nov, tarde): revisar o que a Produto aplicou no Supabase em 08/Nov de manhã (aprovado pelo dono
pelo aplicativo, sem leitura do texto; não é violação) e dizer o que corrigir. O SQL de correção está em
`nuvem/supabase/2026-11-08-lex-correcoes-seguranca.sql`; **o dono revisa e roda**. O que é código da função `lex-conta`
fica para a versão 4 dela, depois do "pode" (desenho em `documentacao/DESENHO-0.8.md`, seção 10.1).

## O que foi lido

- `nuvem/supabase/lex-licencas.sql`, `nuvem/supabase/lex-admin.sql`, `nuvem/supabase/functions/lex-conta/index.ts`,
  `robo/lexsuite/conta.py`, `instalador/INSTALAR.bat`, `rootify-one/rootify-lex.js`.
- No projeto `solverone-app`, só leitura: tabelas `lex_*` (5, RLS ligada, 0 políticas, GRANT só para `service_role`),
  funções `admin_lex_*` (5, só `authenticated`) e `lex_criar_conta` (nenhum papel), Edge Function `lex-conta` v3 com
  `verify_jwt = false`, 2 licenças, 0 instalações, 0 pessoas. Advisor de segurança: nenhum erro novo; só o já conhecido
  da `spatial_ref_sys` (tabela do PostGIS, sem dado de pessoa; a migração `spatial_ref_sys_somente_leitura` já tratou o
  acesso, e o aviso continua porque a RLS não é ligada em tabela de extensão).

## Veredito

**Hoje não há vazamento possível**: a nuvem só recebe, ninguém de fora lê, as tabelas não têm acesso para `anon` nem
`authenticated`, e a equipe só chega pelas funções `admin_lex_*` com `eh_admin_equipe()`. Os pontos abaixo são de
**robustez** (encher o banco grátis, confundir a lista de pessoas) e de **preparo para a 0.8**, quando a nuvem passar a
ser lida pelo site. Nota geral: **Baixo** hoje; **Médio** se a 0.8 entrar sem a etapa 0.

## Achados

| # | Severidade | Onde | O que é | Correção | Como |
|---|---|---|---|---|---|
| R1 | Médio (na 0.8) | `lex-conta`, ação `cadastrar` | Quem tem o código LEX e um id de 16 hex cadastra qualquer e-mail como pessoa da licença, sem aprovação | Acesso ao site em coluna própria (`acesso_site`), concedida só pela equipe ou por um responsável; a `lex-conta` nunca mexe nela | SQL da 0.8 + `lex-conta` v5 |
| R2 | Médio | `lex-conta`, todas as ações menos `registro` | Sem limite de chamadas; cada `instalacao` nova cria uma linha em `lex_instalacoes`; com um laço simples enche o banco grátis | Teto de instalações por licença no banco (trigger, `max_computadores` + 5) agora; limites por ação na função v4 | **SQL de correção** + `lex-conta` v4 |
| R3 | Baixo | `lex-conta`, `cadastrar` | Resposta `email_em_outro_escritorio` confirma a um estranho que um e-mail existe em outra licença | Resposta genérica `dados_invalidos`; o texto certo só na tela quando a pessoa já é da licença | `lex-conta` v4 |
| R4 | Baixo | `lex_criar_conta` | `set search_path = public, extensions` em vez de `''` com nomes qualificados (regra C10); scripts sem data no nome e sem "desfazer"; o repositório não tem `teste/sql-grants.js` | Recriar a função com `search_path = ''`; scripts novos datados com o desfazer; copiar o verificador | **SQL de correção**; pendência P12 |
| R5 | Baixo | `lex_registros.mensagem` | Até 2.000 caracteres livres vindos do instalador; um erro do Windows pode trazer `C:\Users\<nome da pessoa>` | Função apaga `C:\Users\<x>` e e-mails antes de gravar; retenção de 90 dias; teto de linhas por hora | `lex-conta` v4 + **SQL de correção** |
| R6 | Info | `lex-conta` | `verify_jwt = false` | **De propósito e aceito**: o programa não tem chave nenhuma (regra do repositório); o que protege é validar tudo e limitar. Anotado aqui para não ser "corrigido" por engano | — |
| R7 | Baixo | LGPD | Pessoa só cadastrada pela tela (sem login) não tem caminho de anonimização | `admin_lex_anonimizar_email` | SQL da 0.8 |
| R8 | Info | `lex-conta`, `cadastrar` | O primeiro cadastro grava o CNPJ da licença se estiver vazio; um estranho com o código poderia gravar um documento errado antes do escritório | Com R2 e com a equipe preenchendo o documento ao criar a licença, deixa de importar; `admin_lex_criar` passa a aceitar `documento` | SQL da 0.8 |
| R9 | Info | `lex_registros` | `codigo` gravado sem chave estrangeira (de propósito: erro antes do código) | nada a fazer; a tela "Erros sem código" já existe | — |

O que está **certo** e vale manter: chave de serviço só dentro da Edge Function; tabelas sem acesso para `anon` e
`authenticated`; funções da equipe com `eh_admin_equipe()`, `search_path = ''` e log em `acesso_log`; código LEX gerado
só no banco; o programa guarda a última resposta boa e não trava por queda da nuvem; `lex_registros` sem dado pessoal
por desenho; id de instalação aleatório, nada do PC.

## O que o SQL de correção faz (e só isso)

1. Recria `lex_criar_conta` com `search_path = ''` e nomes qualificados. Mesmo comportamento.
2. Acrescenta `lex_contas.max_computadores` (padrão 20) e um trigger em `lex_instalacoes` que recusa a linha quando a
   licença já tem `max_computadores + 5` instalações. As 5 a mais são folga para reinstalação.
3. Trigger em `lex_registros` que recusa quando já houver 600 registros na última hora (freio de emergência; a função
   continua com os 30 por hora por instalação).
4. Índices para os limites por chamada: `lex_instalacoes (codigo)`, `lex_eventos (instalacao, criado_em)`,
   `lex_registros (instalacao, criado_em)`.
5. Job do `pg_cron` às 07:10 UTC (04:10 Brasília) que apaga `lex_registros` com mais de 90 dias. Só erros técnicos;
   nada de licença, pessoa ou evento.
6. Conferência no fim. Cada bloco tem o comando que desfaz.

O que **não** faz: não mexe em dado, não altera `lex-conta`, não cria acesso novo, não toca `spatial_ref_sys`.

## Como o dono aplica

1. Ler o arquivo `nuvem/supabase/2026-11-08-lex-correcoes-seguranca.sql` (os comentários explicam bloco a bloco).
2. supabase.com → projeto `solverone-app` → SQL Editor → New query → colar o arquivo inteiro → Run.
3. A última consulta mostra uma linha com `ok` em todas as colunas. Se alguma vier `false`, me mandar o resultado.
4. Depois: Advisors → Security → "Rerun linter"; me dizer se apareceu algo novo.

Testado em 08/Nov num Postgres 16 local com o `stub-supabase.sql` do rootify-one (resultado na conversa da Arquitetura).

## Lição registrada (08/Nov, noite)

Pedi ao dono uma chave do Resend com o nome `RESEND_API_KEY`, que já existia nos Secrets do projeto desde 23/Out para
outra função da plataforma. Substituir teria trocado a chave daquela função. Regra daqui em diante: **antes de pedir
segredo novo, ler o código das Edge Functions do projeto e listar os nomes de segredo que elas já usam**; segredo de uma
função nova leva o sufixo da função (`RESEND_API_KEY_LEX`). O dono percebeu o aviso do painel e criou o nome novo.
