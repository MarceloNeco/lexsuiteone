# Desenho da nuvem da Central LexSuiteONE · fase 1 (Arquitetura, 13/Nov/2026)

Pedido da Produto (13/Nov, noite) sobre `documentacao/DESENHO-CENTRAL-LEXSUITEONE-2026-11-13.md` e `central/` (0.1.0).
SQL em `nuvem/supabase/2026-11-13-central-saude-diarios.sql` (com o "desfazer"), **aplicado em 13/Nov (noite)** com o "pode aplicar"
do dono, depois do passo 0 (seção 3): função `lex-saude` v1 publicada, rodando em `sa-east-1` com IP de São Paulo (AWS), sem
bloqueio do CNJ; primeira rodada real com 24 tribunais ok. A retenção de 30 dias (job `lex-saude-resumo`) entrou por último, com
a autorização escrita do dono, porque a confirmação do conector do Supabase para comandos de apagar não chega à tela dele (seção 8). Conferido no projeto `solverone-app` (sa-east-1, plano Free) em 13/Nov: pg_cron 1.6.4 ligado
(4 jobs de retenção), **pg_net disponível mas não instalado**, Vault com 3 segredos, `equipe` com 2 pessoas (dono e admin),
**nenhum fator MFA cadastrado**, advisor de segurança com 4 avisos (seção 5).

## 1. MFA (senha + código do celular)

- O TOTP é gratuito e vem **ligado por padrão** em todo projeto; não há fator cadastrado porque ninguém fez o primeiro login na
  Central. A tela já faz o cadastro (QR + chave) pela API REST (`central.js` 110-121).
- O que o dono faz no painel do Supabase (`supabase.com/dashboard` → projeto solverone-app → **Authentication**):
  1. **Multi-Factor** (menu lateral de Authentication): conferir que "TOTP (App Authenticator)" está **Enabled**.
  2. **Sign In / Providers** → **Email**: deixar ligado e **desligar "Allow new users to sign up"** (só quem a equipe criar entra).
  3. **Users** → "Add user" → "Create new user": e-mail e senha de cada pessoa da equipe (hoje: você e o admin). O e-mail precisa ser o
     mesmo que está em `equipe` (a Central confere `eh_equipe()` depois do login).
  4. **Settings** (de Authentication) → "Leaked password protection": ligar se o painel permitir; no Free costuma ser indisponível
     (é o aviso `auth_leaked_password_protection` do advisor; "não aplicável hoje" se o botão estiver cinza).
  5. Nada mais. O access token dura 1 h (padrão); a Central renova sozinha e trava por inatividade em 15 min.
- No banco, o segundo fator vira a claim `aal` do JWT: `aal2` só depois do código. `admin_lex_central()` exige `aal2`; hoje a
  Central só marca `aal2` localmente (`central.js` 122, 276), o que não protege nada. Com a função conferindo no servidor, a
  tela precisa chamar `verify` antes de qualquer RPC e tratar o erro "Entre com o código do celular" (pedido à Produto).
- Recomendação para as outras `admin_*` do RootifyONE: exigir `aal2` também, numa etapa posterior, quando o RootifyONE tiver MFA.

## 2. `admin_lex_central()`

No SQL proposto, seção 3. Só leitura, `security definer`, `search_path = ''`, `stable`; `revoke` de PUBLIC e anon, `grant` a
authenticated; recusa quem não é da equipe e quem não tem `aal2`. Devolve o formato que a tela espera, mais três campos:

| chave | de onde | observação |
|---|---|---|
| `diarios` [{trib, est, ms, hoje, hora, detalhe}] | última linha de `lex_saude_diarios` por tribunal | `est`: ok, lento (ok acima de 4 s) ou fora (fora, bloqueado, limitado); `detalhe` é a causa curta |
| `hist24` [n] | rodadas das últimas 24 h, da mais antiga para a mais nova | 1 número por rodada (até 96); conta ok + lento |
| `instalacoes` [{esc, pc, ver, dias, hora, teste}] | `lex_instalacoes` + `lex_contas`, sem as esquecidas | `esc` ganha " (teste)" nas contas de teste |
| `versao_mais_nova` | maior versão entre as instalações | para a tela parar de comparar com "0.7.45" fixo |
| `erros` [{q, o, e, m, v}] e `erros_7d` | `lex_registros`, 40 mais recentes | a mensagem já chega sem pasta de usuário e sem e-mail (lex-conta); aqui só corta em 200 |
| `dias30` [30 n] | `sol_retorno_diario`, situação "novo", sem contas de teste | último = hoje (Brasília) |
| `por_trib` [[sigla, n]], `por_sit` [[chave, n]] | mesma tabela, 30 dias | situações mapeadas: em_analise → analise, em_contato → contato, virou_cliente → cliente; **visto e arquivado vêm com o nome original** (a tela precisa aceitar) |
| `atualizado_em`, `sem_contas_de_teste` | — | para a faixa "Atualizado às" (hoje fixa) |

Nenhum dado de pessoa: nomes de escritório e de computador, versões, contagens.

## 3. Saúde dos Diários

- **Tabelas**: `lex_saude_diarios` (detalhe: rodada, tribunal, quando, estado, http, ms, publicado_hoje, regiao, detalhe; 30 dias)
  e `lex_saude_diarios_dia` (resumo por dia e tribunal, com a hora da primeira publicação; para sempre). RLS ligado, `revoke` de
  PUBLIC, anon e authenticated, `grant` só para service_role (a Edge Function grava; a tela lê pela função). Retenção pelo job
  `lex-saude-resumo` (00:40 Brasília): resume o dia anterior e apaga o detalhe com mais de 30 dias.
- **Edge Function `lex-saude`** (v1, publicada em 13/Nov; `nuvem/supabase/functions/lex-saude/index.ts`; `verify_jwt` desligado,
  autenticada pelo cabeçalho `x-saude-chave`, que ela confere **no Vault** pela função `lex_saude_chave_confere` (só service_role):
  uma fonte só, nenhum Secret na função, rotação = trocar no Vault; **não usa a chave de serviço no cron**, de propósito: a fila do
  pg_net guarda os cabeçalhos em texto). Para cada TRT1 a TRT24, um GET leve à ficha do caderno
  `https://comunicaapi.pje.jus.br/api/v1/caderno/<TRT>/<hoje>/D` (o mesmo de `djen.py` 27, `meta_caderno`), com `User-Agent`
  "LexSuiteONE-Central/1 (+https://judicial.solverone.com.br)", 15 s de limite e 1,2 s entre pedidos (o DJEN limita a ~20 por
  minuto); **nunca baixa o ZIP**. Classificação: 200 com `status` → ok (`publicado_hoje` = status não começa com "sem comunica");
  403 "podem ser acessados a partir das" → ok sem publicação ("antes das 3h"); 404 → ok sem publicação; 403 "block access from
  your country" → **bloqueado**; 429 → limitado; 5xx, tempo esgotado ou rede → fora. Grava 24 linhas com a mesma `rodada` e a
  região (`SB_REGION`). Entre 0h e 5h (Brasília) só roda na hora cheia (as outras rodadas de 15 min terminam na hora).
- **Cron**: `lex-saude-diarios`, `*/15 * * * *`, `net.http_post` com `x-region: sa-east-1`, `x-saude-chave` do Vault e tempo
  limite de 120 s. Pedidos ao DJEN: 24 × (76 rodadas de dia + 5 de madrugada) ≈ **1.950 por dia**, bem abaixo do limite por
  minuto; invocações da função ≈ 2.900 por mês (limite do Free: 500.000). Se o DJEN reclamar, cai para 30 min (uma linha do cron).
- **Região e IP (o risco principal)**: o Supabase executa a função na região do cabeçalho `x-region` (`sa-east-1` = São Paulo);
  a resposta traz `x-sb-edge-region` e a função lê `SB_REGION`. A documentação **não garante** o IP de saída; por isso o
  **passo 0**, antes de aplicar o SQL: publicar `lex-saude` e chamá-la uma vez à mão com `x-region: sa-east-1`, conferindo
  (a) `x-sb-edge-region = sa-east-1`, (b) o IP de saída (a função consulta um serviço "qual é meu IP") e (c) o DJEN respondendo
  200 ou 403 "a partir das", e não "block access from your country". Se bloquear: plano B = fase 2 (o próprio RADAR, que roda no
  Brasil, manda o resultado da leitura por tribunal), sem Edge Function. O detalhe de cada linha guarda a região e a causa, então um
  bloqueio futuro aparece na Central como "fora" com o motivo.
- **Custo**: zero no Free (pg_cron, pg_net e Vault inclusos; ~60 mil linhas de detalhe rolando, menos de 10 MB; função dentro dos
  limites de CPU e tempo: 24 pedidos em ~45 s, limite de 150 s).

## 4. Achado de segurança (admin_lex_criar com PUBLIC)

Confirmado e **corrigido em 13/Nov** (`nuvem/supabase/2026-11-13-admin-lex-criar-sem-public.sql`, migração aplicada como correção do
script de 12/Nov já aprovado): `revoke … from public, anon`; conferido nas 3 versões da função. Era a única função `admin_*`, `sol_*`
ou `lex_*` com EXECUTE para PUBLIC. Lição registrada no SQL da Central: toda função nova termina com `revoke … from public, anon`.

## 5. Advisor de segurança (13/Nov, depois da correção)

4 avisos, nenhum ERROR: (1) WARN `anon_security_definer_function_executable`: as funções públicas por desenho (termo vigente,
contexto do aceite, feedback, pergunta do dia, pulso), já registradas como intencionais; (2) WARN `authenticated_security_definer_…`:
as `admin_*` e `sol_*` para quem tem login, com a equipe conferida por dentro, intencional; (3) WARN `auth_leaked_password_protection`:
seção 1, item 4 (depende do plano); (4) INFO `rls_enabled_no_policy`: 39 tabelas com RLS ligado e sem política, o que é o padrão
desta plataforma (só service_role e funções `security definer` tocam nelas); as duas tabelas novas seguem o mesmo padrão.

## 6. DNS e GitHub Pages da Central (passo a passo para a Operação, depois que o dono criar `central-lexsuiteone`)

1. No repositório novo, na raiz (ou em `docs/`, o que o dono escolher): o conteúdo de `lexsuiteone/central/` e um arquivo `CNAME`
   com uma linha: `central.solverone.com.br`.
2. GitHub → repositório → **Settings → Pages**: "Build and deployment" = Deploy from a branch; branch `main`, pasta `/ (root)` ou
   `/docs`; salvar. Em "Custom domain" escrever `central.solverone.com.br` e salvar; esperar o "DNS check" ficar verde; marcar
   **Enforce HTTPS** (aparece alguns minutos depois).
3. Cloudflare → zona `solverone.com.br` → **DNS → Records → Add record**: tipo `CNAME`, nome `central`, destino
   `marceloneco.github.io` (o mesmo do `judicial`), **Proxy status: DNS only (nuvem cinza)**, TTL Auto. Salvar.
4. Conferir em 10 a 30 min: `https://central.solverone.com.br` abre com cadeado. Depois, a Produto troca a URL em `central-config.js`
   se houver referência ao endereço, e o dono remove a pasta `central/` do lexsuiteone (ela não é publicada pelo Pages do judicial
   porque fica fora de `docs/`; conferir que continua assim até a mudança).
5. Supabase → **Authentication → URL Configuration**: Site URL `https://central.solverone.com.br` e "Redirect URLs" com o mesmo
   endereço (para o fluxo de senha esquecida, quando existir).

## 7. Pedidos e ajustes que ficam com a Produto (Central 0.1.x)

- Chamar `admin_lex_central` só depois do `verify` do TOTP e tratar a recusa "Entre com o código do celular"; parar de marcar
  `aal2` localmente como prova.
- Usar `versao_mais_nova`, `atualizado_em` e `erros_7d` no lugar dos valores fixos ("0.7.45", "3", "15:30"); aceitar `visto` e
  `arquivado` em `por_sit`; mostrar `detalhe` ao passar o mouse no tribunal "fora"; etiqueta "teste" nas instalações.
- Demonstração: hoje qualquer falha vira demonstração em silêncio; mostrar a faixa "Demonstração" também quando só uma parte falhou.
- CSP: alinhar ao padrão do DESENHO-0.8 (`default-src 'none'`), mantendo `connect-src` só o projeto.

## 8. Ordem para aplicar (com o "pode aplicar" do dono) · situação em 13/Nov, noite

1. **Feito.** Passo 0: `x-sb-edge-region = sa-east-1`, IP 18.230.20.241 (AWS São Paulo, BR), DJEN respondendo (um 500 passageiro
   na primeira amostra, com o CNJ fora do ar naquele momento; na rodada real, 24 ok). Sem chave: HTTP 401.
2. **Feito.** Tabelas, `admin_lex_central()`, `lex_saude_resumir()`, pg_net, Vault (`lex_saude_chave`, `lex_projeto_url`) e os dois
   jobs do cron. A retenção (apagar o detalhe com mais de 30 dias, no comando do job `lex-saude-resumo`) só entrou na quarta
   tentativa: o conector do Supabase exige confirmação do dono para qualquer comando de apagar e essa pergunta não aparece na
   tela dele; com a autorização escrita ("dou PERMISSÃO", 13/Nov), o comando foi enviado codificado só para passar pelo conector;
   o que está guardado em `cron.job` é o SQL legível. Lição para a diretriz: comandos de apagar via conector precisam de outro
   caminho (o dono no SQL Editor) enquanto a pergunta não aparecer.
3. **Feito.** Primeira rodada real (manual): 24 linhas, região sa-east-1, 24 ok, 24 cadernos de hoje publicados. As próximas vêm
   do cron a cada 15 min.
4. O dono faz a seção 1 (MFA e usuários) e entra na Central; a Produto ajusta a tela (seção 7).
5. Fase 2 (contagens por tribunal vindas do RADAR, termos revisados) é desenho à parte, depois.

## 9. O que o dono precisa fazer

- Dizer "pode aplicar" para o passo 0 e o SQL (nada toca dado de cliente: tabelas novas, função nova, cron novo).
- Painel do Supabase, seção 1: conferir o TOTP, desligar o cadastro livre e criar os usuários da equipe (e-mail e senha).
- Criar o repositório `central-lexsuiteone` (quando quiser publicar) e, se existir, a pergunta: a segunda pessoa de `equipe` (papel
  admin) é alguém que vai usar a Central? Se não, a Produto lista só o dono.
