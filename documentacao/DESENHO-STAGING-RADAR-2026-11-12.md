# Desenho: staging e CI/CD do RADAR JUDICIAL (Arquitetura, 12/Nov/2026)

Pedido do dono em `documentacao/PROMPT-STAGING-CICD-2026-11-12.md`, seção 2. Prioridade: **depois do lançamento na KR Law**.
Nada deste desenho é implementado antes do "pode" do dono. O padrão geral da plataforma (nomes, etiqueta, segredos por ambiente,
Definition of done com "testado em staging") é da conversa "(SolverONE) Fable diretrizes"; o que está aqui segue esse padrão e
se ajusta a ele onde divergir (em especial o nome do endereço: usamos `staging.judicial.solverone.com.br` como no pedido).

## 0. Como está hoje (conferido no código em 12/Nov)

- **Publicação** (`.github/workflows/publicar.yml`): disparo manual (versão + "publicar") ou tag; testes; empacota
  (`robo/ferramentas/empacotar_ci.py`); pede a assinatura ao Worker `assinatura.solverone.com.br` com a identidade OIDC do GitHub
  (sem segredo no repositório; o corpo é só versão e hash); confere; e **grava direto na `main`**: `docs/atualizacao/`
  (`versao.json` + zip de atualização), `docs/downloads/`, `releases/`, tag `vX.Y.Z`. Sem aprovação de ambiente.
- **Site e canal de atualização**: GitHub Pages, branch `main`, pasta `docs/`, domínio `judicial.solverone.com.br` (DNS no
  Cloudflare). O programa busca `config.atualizacao.url` (`https://judicial.solverone.com.br/atualizacao`, `config.py` 18) ou a
  subpasta `atualizacao` da pasta compartilhada; confere assinatura Ed25519 com a chave pública do pacote (`atualizar.py` 84-100).
  O instalador (`instalador/INSTALAR.bat` 10 e 14) tem o site e a `lex-conta` de produção fixos.
- **Nuvem**: um projeto Supabase (`solverone-app`, plano gratuito, sem branches), funções `lex-conta` (programa, público) e
  `lex-equipe` (RootifyONE, com login); segredos só nas funções (`SUPABASE_*`, `RESEND_API_KEY_LEX`). Nenhuma marcação de
  "licença de teste" no banco: a licença de teste do dono é produção, com aceite real (`ACE-000001`), eventos, avisos e retorno diário.
- **Lacunas para staging**: a URL da `lex-conta` está fixa em `conta.py` 21 e no instalador; a assinatura não sabe de canal; a
  automação publica sem portão; nada distingue ambiente na tela, no e-mail ou no banco.

## 1. Pacote, assinatura e canais (publicar.yml, atualizar.py)

**Dois canais com o mesmo artefato.** Staging em `https://staging.judicial.solverone.com.br/atualizacao/`; produção como hoje.

- `publicar.yml` ganha o input `destino` (`staging` ou `producao`; o booleano "publicar" vira "só testar") e dois GitHub
  **Environments**: `staging` (sem aprovação) e `producao` (**required reviewer = o dono**: ele aprova com um clique no celular,
  na página da execução, depois de ler o resumo em português que a automação escreve). O repositório é público, então Environments
  e minutos são gratuitos.
- **Staging**: testes, Bandit, Gitleaks, varredura de dependências (`pip-audit`; o robô é só biblioteca padrão, então o alvo são
  as ferramentas), empacota, assina (o Worker assina versão + hash; a assinatura é do arquivo, não do canal), confere, e grava
  `versao.json` + zips na branch `staging` (pasta `docs/atualizacao/`), que o site de staging serve. Guarda o pacote também como
  artefato da execução (90 dias). Depois roda o **teste de tela** (seção 7) e publica o resumo com prints.
- **Promoção** (`promover.yml`, input `versao`, Environment `producao`): copia **o mesmo zip e o mesmo `versao.json`** da branch
  `staging` para a `main` (`docs/atualizacao/`, `docs/downloads/`, `releases/`), confere que o SHA-256 e a assinatura são os que
  foram testados, cria a tag `vX.Y.Z`, roda `marca.py` e faz o commit "Promove a versão X (automação)". **Nada é recompilado.**
  O dono dispara com "promove a versão X" na conversa da Operação (que clica) ou aprova direto no GitHub.
- **Desfazer**: `promover.yml` com a versão anterior republica o manifesto e os zips anteriores (ficam em `releases/`). Para o
  programa já atualizado voltar, `atualizar.py` passa a aceitar um manifesto assinado com `substituir: true` mesmo quando a versão é
  menor que a instalada (hoje só instala versão maior, 69-72). Um passo só, com aprovação do dono.
- **Assinatura**: a mesma chave para os dois canais (o cliente confia na chave do pacote; o canal diz só de onde baixa). A conferir
  com o Worker: ele hoje aceita pedidos "a partir da `main` ou de tag" (`docs/PUBLICAR.md` 42); para assinar a partir da branch
  `staging`, a regra de OIDC do Worker precisa aceitar `ref = refs/heads/staging` deste repositório. Mudança pequena, da Arquitetura.
- `atualizar.py`: usa a URL do canal devolvida pela `lex-conta` (seção 2) quando existir; senão, `config.atualizacao.url`.

## 2. Licença com canal e etiqueta na tela (lex-conta, conta.py, RootifyONE)

- `lex_contas.canal` (`producao` | `staging`, padrão `producao`), na ficha do RootifyONE ("Canal de atualização"), com evento
  `licenca_alterada`. A `lex-conta` (`verificar`) devolve `canal` e `atualizacao_url`; `conta.py` guarda os dois na última resposta
  boa e `atualizar.py` usa a URL. Serve para dar a um escritório uma versão antes dos outros (beta) sem mexer no computador dele.
- A função devolve também `ambiente` (`producao` | `staging`), lido da variável `AMBIENTE` do projeto que respondeu. A tela mostra a
  etiqueta **"STAGING · ambiente de teste / test environment"** no cabeçalho (`radar_modelo.html`, `<header>` 673-680, ao lado do
  nome do escritório) quando `ambiente = staging` **ou** `canal = staging`; o dado vem do `/dados` (`conta.situacao`, `conta.py`
  198-215), nunca de texto fixo. Sem a etiqueta, a pessoa não sabe em que ambiente está; é o risco "cliente preso em staging".
- O que NÃO fica no programa: nenhum endereço de staging fixo. Uma instalação de staging nasce do **instalador de staging**
  (o `INSTALAR.bat` servido por `staging.judicial…`, com `SITE` e `REGISTRO` apontando para o staging), que grava em
  `conta-inicial.json` a URL da `lex-conta` de staging (`conta.url`, que `conta.py` já lê, 105). O instalador de produção continua
  igual. O manual ganha a frase "a etiqueta STAGING no alto da tela significa ambiente de teste; o escritório nunca a vê".

## 3. Nuvem em staging (Supabase, lex-conta, lex-equipe)

- **Projeto separado** `solverone-staging`, na mesma organização, **plano gratuito** (a organização está no Free, que permite 2
  projetos; branches do Supabase exigem plano pago e nascem sem dados). Custo: R$ 0. Limitação: o projeto gratuito **pausa depois de
  7 dias sem uso**; a automação faz um "ping" semanal (uma chamada `conferir` com código inválido) e, antes de cada teste, espera o
  projeto acordar (1 a 2 min). Se o staging virar uso diário, o Pro (US$ 25/mês) tira a pausa.
- **Esquema**: aplicar, em ordem, os arquivos de `nuvem/supabase/*.sql` (eles são o registro). É também a primeira prova de que o
  registro reproduz a produção; o que faltar vira arquivo novo. Reserva: `pg_dump --schema-only` da produção.
- **Funções**: o mesmo código de `lex-conta` e `lex-equipe` publicado nos dois projetos. O que muda vira variável de ambiente da
  função, nunca texto: `AMBIENTE`, `ORIGEM_SITE` (CORS: `https://staging.judicial…`), `LINK_ACEITE`, `DADOS` (interruptores do
  RootifyONE: pasta `staging/` do `solverone-dados`), `EMAILS_PERMITIDOS` e `RESEND_API_KEY_LEX` (chave própria de staging). Em
  produção, sem `AMBIENTE`, tudo fica como hoje.
- **Dados**: só fictícios ou de teste. `sol_apps`, `sol_termos`/`sol_termos_versoes` (mesmo texto 1.0), a licença de teste do dono
  (recriada lá) e dois escritórios fictícios com pessoas e computadores de mentira para os testes de tela. Nenhuma linha vem da
  produção; o **retorno diário** e os **chamados** de staging ficam em staging.
- **RootifyONE**: a conversa de lá desenha a troca de ambiente na tela (um seletor "produção | staging" com a etiqueta e a cor; a
  chave publicável e a URL do projeto por ambiente; as listas de licenças, aceites e chamados lidas do projeto escolhido).

## 4. E-mails em staging (boas-vindas, aceite, avisos)

- Chave do Resend **só de envio e restrita ao domínio**, separada da de produção, no projeto de staging.
- Regra no código das duas funções, ligada por `AMBIENTE = staging`: destinatário fora de `EMAILS_PERMITIDOS` (os e-mails do dono,
  inclusive os com "+") **não é enviado** (fica em `lex_avisos` como "bloqueado: staging"); assunto com prefixo `[STAGING]`; remetente
  `SolverONE STAGING <nao-responda@solverone.com.br>`. Nenhum e-mail de staging chega a cliente, mesmo que alguém cadastre um
  e-mail real por engano.

## 5. Site e página de aceite em staging

- `staging.judicial.solverone.com.br` servido pelo **Cloudflare Pages** (o DNS já está no Cloudflare), ligado ao repositório,
  branch `staging`, pasta `docs/`; a produção **não muda** (GitHub Pages, `main`). Proteção: **Cloudflare Access** (gratuito até 50
  pessoas): só entra quem fizer login por código no e-mail, com os e-mails do dono na lista; cabeçalho `X-Robots-Tag: noindex`;
  sem link em lugar nenhum da produção. A página de aceite e o manual de staging mostram a etiqueta.
- `ferramentas/marca.py` passa a ler `AMBIENTE` e gravar em `docs/marca-ambiente.json` (ou no próprio `marca.json`): a etiqueta,
  a URL e a chave publicável do projeto (`paginas/aceite.html` ganha `{{nuvem.url}}` e `{{nuvem.chave}}` no lugar dos valores
  fixos). A automação da branch `staging` gera com `AMBIENTE=staging`; a `main`, sem. **Promoção = o mesmo commit** (a `main` recebe
  o commit testado na `staging`, por merge sem recompilar o pacote; só o `docs/` é regenerado sem a etiqueta, por configuração).

## 6. Dados de teste fora da produção (depois, com cópia e "pode")

Inventário na produção hoje: a licença "Teste Marcelo (SolverONE)" e o que ela gerou (pessoa, instalações, eventos, avisos, retorno
diário, aceite `ACE-000001`, contadores de chamadas) e nenhum chamado de RADAR. A KR Law não é tocada. Plano, só depois do staging
no ar com a licença de teste recriada lá: (1) arquivo SQL datado com os `SELECT` do que sai, guardado pelo dono fora do repositório
(tem dado pessoal), como "desfazer"; (2) apagar o que é apagável; (3) o que é imutável por desenho (`sol_aceites`, versões dos
termos) fica, com a licença de teste marcada `ativo = false` e nome "(teste; migrada para staging)"; (4) o RootifyONE perde a opção
"limpar os dados de teste" em produção. A Arquitetura avisa antes, como manda o `CLAUDE.md`.

## 7. Windows de teste

- **Na automação, gratuito**: a execução de staging roda um job em `windows-latest` do GitHub Actions (sem custo em repositório
  público, máquina nova a cada vez): baixa o `INSTALAR.bat` do site de staging, instala com um código de licença de staging (secret
  do Environment), abre o programa, confere o Agendador (`schtasks /query`), percorre a tela com o Playwright (cadastro, trava do
  aceite, "Ler o Diário agora" contra um Diário de mentira, Configuração) e gera os prints que o dono vê no resumo. Serve para 90 %
  do que hoje "precisa do dono".
- **Sob demanda, pago**: uma VM Windows pequena no Azure (B2s, ~US$ 0,05 por hora ligada, mais ~US$ 5 a 10 por mês de disco parado),
  ligada pela Operação só para o que a automação não cobre (Excel real, Google Drive para computador, OneDrive, aviso de atualização
  com janela aberta) e desligada depois; o dono olha por área remota, sem rodar nada no notebook. Estimativa: menos de US$ 10 por mês.
  Windows 365 (~US$ 28 por mês) só se o uso virar diário.

## 7b. Executor brasileiro na Oracle Cloud (ideia do dono, 13/Nov)

O dono tem uma conta Oracle Cloud "Always Free" com região no Brasil. Uma máquina Linux grátis dessa conta, com IP brasileiro, pode
ser registrada como executor do GitHub Actions ("self-hosted runner") e receber só os passos que precisam sair do Brasil (DJEN,
BrasilAPI, Minha Receita, testes de tela com Playwright a partir do país); o resto da automação segue no GitHub. Serve também de
plano B da conferência dos Diários (hoje na Edge Function em sa-east-1). Cuidados: Windows não entra no grátis; máquina nossa para
manter (atualizações, chave SSH, firewall); a Oracle recolhe máquinas grátis ociosas e às vezes não tem vaga; em repositório público
o executor só roda trabalhos da `main` e de disparo manual, nunca de fork, e de preferência como executor efêmero. Entra na fase 3,
quando o dono disser "pode".

## 8. O que muda, onde, e quem faz

| Peça | Mudança | Quem |
|---|---|---|
| `publicar.yml`, novo `promover.yml`, Environments `staging`/`producao` | destino, portão de aprovação do dono, promoção sem recompilar, desfazer, resumo em português com prints, job Windows | Arquitetura (desenho e automação); Operação opera |
| Worker de assinatura | aceitar OIDC da branch `staging` | Arquitetura |
| `atualizar.py` | URL do canal vinda da licença; manifesto com `substituir` para desfazer | Produto (dona do robô), com o contrato da Arquitetura |
| `conta.py`, `radar_modelo.html`, manual, AssistONE, Novidades | guardar `canal`/`ambiente`; etiqueta STAGING; textos | Produto |
| `lex-conta`, `lex-equipe` | `AMBIENTE`, `ORIGEM_SITE`, `EMAILS_PERMITIDOS`, prefixo `[STAGING]`, `canal` e `atualizacao_url` na resposta | Arquitetura |
| Supabase | projeto `solverone-staging`, esquema pelos SQL do repositório, dados fictícios, `lex_contas.canal` (SQL datado) | Arquitetura |
| Cloudflare | Pages do `staging`, Access, DNS `staging.judicial`, Worker | Arquitetura desenha; o dono faz o que exige login |
| Resend | chave de staging só de envio | o dono cria e cola no Secret do projeto de staging (nunca no chat) |
| RootifyONE | seletor de ambiente, ficha com "Canal de atualização", listas por ambiente | conversa do RootifyONE (pedido pelo prompt) |
| `docs/PUBLICAR.md`, `ARQUITETURA.md`, `CLAUDE.md`, diretriz geral | "nada vai a produção sem staging"; DoD com "testado em staging" | Arquitetura (aqui) e diretrizes (geral) |

## 9. Fases, o que o dono vê e custo

1. **Nuvem de staging** (1 sessão): projeto, esquema, funções, dados fictícios, e-mail bloqueado. O dono vê: um e-mail `[STAGING]`
   chegando só no e-mail dele. Custo: R$ 0.
2. **Site e instalador de staging** (1 sessão): Pages + Access + página de aceite com etiqueta. O dono vê: entra com o código do
   e-mail, vê a faixa STAGING, faz um aceite de mentira. Custo: R$ 0.
3. **Pacote e canal** (1 a 2 sessões): `publicar.yml` com destino, `promover.yml`, Environments, `atualizar.py`/`conta.py`, etiqueta
   no programa, job Windows com prints. O dono vê: um resumo em português com prints e o botão de aprovar; a promoção com um clique.
   Custo: R$ 0 (repositório público).
4. **Inversão do fluxo**: regra escrita (`CLAUDE.md`, `PUBLICAR.md`, diretriz geral): só a promoção publica em produção. Custo: R$ 0.
5. **Limpeza da produção** (seção 6), com cópia e "pode". Custo: R$ 0.
6. Opcional: VM Windows sob demanda (< US$ 10 por mês) e Supabase Pro (US$ 25 por mês) se a pausa de 7 dias atrapalhar.

## 10. Riscos e como evitar

- **Cliente preso em staging**: a etiqueta vem da nuvem que respondeu; o instalador de produção não conhece o staging; a ficha da
  KR Law fica `canal = producao`; o teste de tela confere que o pacote promovido sem etiqueta aponta para a produção.
- **E-mail de teste para cliente**: lista permitida no código de staging, não em configuração editável; prefixo `[STAGING]`.
- **Segredo vazado**: chaves por projeto, só em Secrets (GitHub Environment e Supabase); nenhuma no repositório, no quadro ou no chat;
  Gitleaks em toda execução; a chave de assinatura continua só no Worker.
- **Banco divergente**: o esquema de staging nasce dos SQL do repositório e a automação compara `pg_dump --schema-only` dos dois
  projetos a cada promoção; diferença é bloqueio.
- **Promoção recompilada por engano**: `promover.yml` não roda `empacotar`; confere hash e assinatura contra o manifesto testado.
- **Projeto gratuito pausado na hora do teste**: ping semanal e espera de acordar na automação.

## 11. O que o dono decide (em linguagem simples)

1. Aprovar este desenho como a parte do RADAR, sujeito ao padrão geral da conversa de diretrizes.
2. Aceitar que o staging da nuvem fique no plano gratuito (pausa após 7 dias sem uso, com o "despertador" da automação) ou pagar
   US$ 25 por mês pelo plano Pro para não pausar.
3. Querer a máquina Windows sob demanda (< US$ 10 por mês) ou só os testes automáticos gratuitos.
4. Onde o dono entra (tudo com login dele): criar a chave de staging do Resend, aprovar as execuções no GitHub, entrar no Cloudflare
   Access na primeira vez. Nada de comando.
