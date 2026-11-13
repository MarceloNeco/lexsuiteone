# Central LexSuiteONE: painel da equipe para os softwares jurídicos (desenho, 13/Nov/2026)

Pedido do dono, 13/Nov: um aplicativo web (PWA) separado, com login seguro, só para a administração da SolverONE.
Ele deve mostrar estatísticas, testar se os Diários (DJEN/CNJ) estão funcionando, conferir a integridade das
instalações e ser um painel gerencial do estado das coisas. Começa pelo RADAR JUDICIAL e depois serve a todos os
produtos jurídicos da LexSuiteONE. O RADAR continua standalone e sem senha; isto é outro aplicativo.

Protótipo navegável, com dados fictícios e sem login de verdade:
`documentacao/prototipos/central-lexsuiteone/index.html`. Basta abrir o arquivo no navegador.

## 1. O que o painel mostra (desenho da Produto)

| Aba | O que mostra | De onde vem | Existe hoje? |
|---|---|---|---|
| Visão geral | 6 quadros clicáveis: Diários do CNJ (23/24), computadores ativos, versão atual, erros em 24 h, processos novos hoje, licenças | resumo das abas abaixo | parte |
| Saúde dos Diários | 24 TRTs em verde, amarelo ou vermelho; tempo de resposta; se o Diário de hoje já saiu; histórico de 24 h | **conferência pela nuvem de 15 em 15 minutos** (nova) | **não** |
| Escritórios e computadores | escritório, computador, versão, última conferência, "parado há N dias", "versão antiga" | `lex_instalacoes` + `lex_contas` | sim (dados) |
| Leituras dos escritórios | por tribunal: leituras ok, CNJ fora, erro (só contagens) | **resumo novo mandado pelo RADAR** | **não** |
| Erros | instalador e programa: etapa, mensagem, versão, Windows | `lex_registros` | sim (dados) |
| Estatísticas | processos novos por dia, por tribunal, por situação (todos os escritórios) | `sol_retorno_diario` | sim (dados) |
| Licenças | resumo, com atalho para o RootifyONE | `lex_contas` | sim (dados) |

Cadastro, ativar e pausar, e-mails, termos e CRM continuam no RootifyONE (B2B → LexSuiteONE), conforme a decisão de
09/Nov. A Central não duplica essas telas; mostra o resumo e um atalho.

## 2. O que falta construir

1. **Login da equipe.** Supabase Auth, com cadastro público desligado. Entra só quem está na tabela `equipe`, que já
   existe e tem o dono. Sem login com Google, porque a diretriz proíbe login social na administração. Senha mais
   **código de verificação** (MFA TOTP do Supabase, sessão `aal2`). As funções de leitura recusam sessão sem MFA.
2. **Funções de leitura `admin_lex_*`.** São `security definer`, conferem `meu_papel_equipe()` e o `aal2`, têm
   `search_path` fixo e `revoke` de `anon` e `PUBLIC` (verificador `teste/sql-grants.js`). Devolvem só os resumos
   acima.
3. **Saúde dos Diários (nuvem).**
   - Uma tabela nova, `lex_saude_diarios` (tribunal, quando, situação, código HTTP, ms, Diário de hoje publicado).
   - Uma Edge Function chamada pelo `pg_cron` de 15 em 15 minutos, que faz **um pedido leve por tribunal** à ficha
     do caderno (o mesmo `caderno/<TRT>/<dia>/D` que o RADAR usa, sem baixar o ZIP).
   - Isso dá 24 pedidos a cada 15 minutos (2.304 por dia). Se for muito, a conferência passa a ser de 30 em 30
     minutos.
   - **Risco:** o CNJ bloqueia endereço de fora do Brasil (`BloqueadoForaDoBrasil`). A Edge Function tem de rodar em
     São Paulo (`sa-east-1`); a Arquitetura confere.
4. **Resumo das leituras dos escritórios.** Depois de cada leitura, o RADAR mandaria, por tribunal, só contagens e a
   causa: ok, CNJ fora, ainda não publicado, erro. Isso muda o que vai à SolverONE, então os termos (seção dos dados
   enviados) e o manual precisam de revisão (Definition of done, ponto 4). Por isso fica na fase 2, com o "pode" do
   dono.
5. **O próprio aplicativo (PWA).**
   - HTML, CSS e JS puros, sem build e sem script de terceiros.
   - Manifest, service worker e ícone; PT/EN; claro e escuro; AssistONE e (?) nos campos.
   - Sem nenhum pedido externo além do Supabase da SolverONE.
   - Alertas por e-mail (por exemplo, "TRT9 fora há 1 hora") ficam para a fase 3.

## 3. Onde o aplicativo mora (decisão do dono)

| Opção | Prós | Contras |
|---|---|---|
| **A. Repositório novo e subdomínio próprio** (ex.: `central.solverone.com.br`). Recomendada | Origem separada do site do cliente e dos apps: um defeito no site não alcança a sessão da administração; nasce pronto para servir a todos os produtos jurídicos | Criar repositório pede permissão; mais um DNS (Cloudflare) |
| B. Pasta dentro do `lexsuiteone` (`judicial.solverone.com.br/central`) | Nada novo para criar | Mistura a administração com o site que o cliente vê; mesma origem do site público |
| C. Dentro do RootifyONE (abas B2B) | Já tem login de equipe e as abas Estatísticas e Erros desenhadas | O dono quer um aplicativo à parte, e o RootifyONE é de outra conversa |

## 4. Fases

1. **Fase 1** (sem mudar o RADAR):
   - login com código de verificação;
   - Saúde dos Diários pela nuvem;
   - escritórios e computadores, erros, estatísticas e licenças com os dados que já existem.
2. **Fase 2:** resumo das leituras dos escritórios, que pede uma versão nova do RADAR, termos e manual.
3. **Fase 3:** alertas por e-mail; os outros produtos (tributário, cível) entram como seletor de produto no título,
   como no RootifyONE.

## 5. Quem faz o quê

- **Arquitetura.** Fecha o desenho de nuvem: tabela, Edge Function em São Paulo, `pg_cron`, funções `admin_lex_*`,
  MFA e RLS. Aplica o SQL pelo conector, com o arquivo datado em `nuvem/supabase/` e o "desfazer" ao lado.
- **Produto.** Faz o aplicativo (telas, textos PT/EN, manual curto, AssistONE) e, na fase 2, a mudança no RADAR.
- **Operação.** Faz o DNS do subdomínio e revisa antes de publicar.
- **RootifyONE.** Recebe um pedido para registrar o produto "Central" e, se o dono quiser, mostrar um atalho.

## 6. O que o RootifyONE, o ArchONE e o EaglePlanONE precisam saber

- Aplicativo novo da plataforma, de administração, com login da equipe pelo Supabase.
- Integração nova (leitura) com `lex_*` e `sol_retorno_diario` e, na fase 1, uma conferência automática ao CNJ.
- Item novo de roadmap: "Central LexSuiteONE, fases 1 a 3".
