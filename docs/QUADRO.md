# Quadro das sessões (ler antes de agir, atualizar antes e depois de cada tarefa)

Três conversas do Claude Code trabalham neste repositório ao mesmo tempo: **Operação** (Sonnet), **Produto** (Opus) e
**Arquitetura** (Fable). Elas não se falam. Este arquivo é o único lugar onde uma vê o que a outra está fazendo. O dono
pede "resumo do quadro" à Operação quando quer saber o estado geral.

Regras rápidas (o detalhe está no `CLAUDE.md`, seção "Trabalho em três sessões"):

1. Antes de qualquer tarefa: `git pull`, ler este arquivo inteiro, anotar na própria seção o que vai fazer e que arquivos
   vai mexer. Depois de enviar para a `main`: atualizar "Feito" e limpar "Fazendo agora".
2. Cada arquivo tem uma sessão dona. Quem não é dono não edita: escreve um pedido em "Pedidos entre sessões".
3. Só a Operação publica versão, e só com o "publica a versão X" do dono naquela conversa.
4. Tarefa em andamento quando este quadro foi criado (08/Nov, tarde) termina como está. As regras valem da tarefa seguinte.

---

## Operação (Sonnet)

Dona de: `docs/NOVA-SESSAO.md`, `docs/QUADRO.md` (este arquivo, exceto as seções das outras sessões), `docs/DNS-SOLVERONE.md`,
`docs/PUBLICAR.md`, `releases/`, `docs/downloads/`, `docs/atualizacao/`, `.github/`, `docs/email/` (envio), pasta do Drive,
Cloudflare, Resend, publicação de versões.

### Fazendo agora
- Drive: esperando o dono restringir "Estudos de Casos Juridicos" e avisar "feito"; então confiro e atualizo a pasta.
- E-mail de boas-vindas ao Leandro: **em espera, e a Operação não envia mais**. Decisão do dono (09/Nov): o envio sai pelo
  botão do RootifyONE, com prévia; o clique dele depois da prévia é a autorização, e ele não vai escrever "pode enviar"
  em conversa. Até o botão existir, nada é enviado ao Leandro. O roteiro da visita supõe o e-mail enviado até quarta,
  11/Nov: se o botão não ficar pronto a tempo, o dono decide a alternativa (pedido à Arquitetura, abaixo).
- Botão no RootifyONE para enviar os e-mails de boas-vindas: requisito novo do dono, registrado como pedido à
  Arquitetura (abaixo). Nada implementado.
- Ficha da KR Law no RootifyONE (e-mail de boas-vindas e domínio): **já preenchida pelo dono**, que a fez antes. Esta
  conversa não enxerga o RootifyONE nem o banco e por isso não consegue conferir; nada a fazer pela Operação.

### Arquivos em uso
- (nenhum)

### Feito (mais recente primeiro)
- 09/Nov: **0.7.13 publicada** (04:39 UTC) com o "publica a versão 0.7.13" do dono (correção do erro das 3h, que a Operação
  tinha pedido à Produto). Revisor aprovou sem bloqueio (106 testes, Bandit limpo; Gitleaks só por busca manual). Automação
  da `main` verde, versão em `e2160cd`, publicada pela automação em `30b6a02`, tag `v0.7.13`. Conferido por fora: hash e
  assinatura batem com a chave do download; **41 arquivos no download completo e 40 no pacote de atualização** (um a mais
  que na 0.7.12, por causa do módulo novo `causas.py`); versão dentro dos dois é 0.7.13; nenhum arquivo proibido nem código
  de cliente real; o site serve `versao.json`, o pacote de atualização e o download completo com o mesmo hash do repositório,
  e o instalador responde. O banco do pacote 0.7.14 não foi junto (revertido antes). Ressalvas do revisor viram pedido
  à Produto (continuação, 09/Nov). Não conferi a tela nem o agendador do Windows: o primeiro teste real é o computador do dono.
- 09/Nov: erro que o dono viu ao clicar em "Ler o Diário agora" às 00:05 analisado (prints dele): não é site fora nem
  problema de domingo, é o programa pedindo o caderno de hoje antes das 03:00; causa lida em `monitor.py` e `djen.py`.
  Pedido de correção à Produto na tabela de pedidos (continuação, 09/Nov). Nada alterado no código.
- 09/Nov: o dono repetiu o pedido de publicar a 0.7.12, que **já estava publicada** desde 08/Nov (20:43 UTC): tag `v0.7.12` e
  `versao.json` do site conferidos de novo. Não disparei a automação outra vez: a `main` já tem a 0.7.13 em andamento com o
  número ainda em 0.7.12, e republicar levaria código não revisado sob o mesmo número.
- 08/Nov: **0.7.12 publicada** (20:43 UTC) com o "publica a versão 0.7.12" do dono, pulando a 0.7.11 (a 0.7.12 contém tudo
  dela): Painel com números e gráficos ao lado da Lista; planilha com cabeçalho azul-marinho, filtro, R$, destaque e aba
  "Como usar". Revisor aprovou sem bloqueio (101 testes, Bandit limpo); automação da `main` verde em `8759f27`; versão no
  commit `68e2679` (tag `v0.7.12`; sobre o `8759f27` só acrescentou documentos), publicada pela automação em `a593a95`. Conferido por fora:
  hash e assinatura batem com a chave do download; **40 arquivos no download completo e 39 no pacote de atualização**;
  versão dentro dos dois é 0.7.12; nenhum arquivo proibido nem código de cliente real; o site serve `versao.json`, o
  instalador e o pacote (mesmo hash do repositório). Ressalvas do revisor viram pedido à Produto.
- 08/Nov: **0.7.10 publicada** (16:39 UTC) com o "pode" do dono: revisor aprovou, automação da `main` verde, versão no commit `dc609bc` (tag
  `v0.7.10`), publicada pela automação em `eef4306`. Conferido por fora: hash e assinatura do pacote batem com a chave que vai no download, a versão dentro dos dois
  pacotes é 0.7.10, nenhum arquivo proibido nem código de cliente real, o site serve `versao.json` e os downloads.
  Ressalvas do revisor (textos desatualizados) registradas como pedidos abaixo.
- 08/Nov: Worker `integracao-resposta` corrigido e testado (15:18 UTC): e-mail de serviço de envio (Resend) é encaminhado sem
  resposta e sem "bounced"; e-mail de pessoa (Gmail) é encaminhado e recebe a resposta; confirmado no log do Email
  Routing. Versão anterior guardada na Cloudflare. Registrado em `docs/DNS-SOLVERONE.md` e `docs/NOVA-SESSAO.md`. E-mail de
  boas-vindas da KR Law preparado fora do repositório; e-mail de teste com a licença de teste enviado ao dono (a licença
  de teste não tem e-mail cadastrado no banco; o dono escolheu o destino).
- 08/Nov: `docs/NOVA-SESSAO.md` atualizado para o estado real (pedido da Arquitetura): robô 0.7.9, RADAR JUDICIAL, conta e
  licença na nuvem (conferidas no Supabase, só leitura), Worker, Drive e as regras do quadro. Achado para a Arquitetura na
  tabela de pedidos: o SQL `lex_*` já está aplicado, mas as pendências ainda pedem ao dono para rodá-lo.
- 08/Nov: lixeira dos "_ANTIGO" (v0.5.0 e v0.6.0) e 6 documentos velhos movidos para "_antigos do robô" no Drive. Worker
  `integracao-resposta` lido: o segundo e-mail foi respondido uma vez e encaminhado (log do Email Routing); o "bounced"
  no Resend vem da resposta automática enviada ao endereço de retorno do próprio Resend (causa provável, não provada por
  log do Resend). Testes de entrega de `judicial@`, `admin@`, `privacidade@` e `suporte@`: os quatro chegaram.
- 08/Nov: contagem do pacote corrigida no `CLAUDE.md`; nota sobre separar o envio por subdomínio em `PENDENCIAS.md`.
- 08/Nov: conferência de Resend e Drive (relatório ao dono).

### Preciso do dono
- E-mail ao Leandro: nada a escrever em conversa. Quando o botão do RootifyONE existir (desenho da Arquitetura, com
  prévia), o dono envia por ele. Se o botão não estiver pronto até quarta (11/Nov), decidir a alternativa.
- Drive: o dono restringe "Estudos de Casos Juridicos" (o conector não altera compartilhamento) e avisa "feito"; eu
  confiro as permissões e atualizo a pasta do Drive para a versão atual (0.7.13, pacote RADAR).

---

## Produto (Opus)

Dona de: `paginas/`, `docs/index.html` e `docs/404.html` (gerados), `docs/manual.html`, `docs/marca.json`,
`robo/MANUAL-DO-ESCRITORIO.html`, `robo/radar_modelo.html`, textos PT/EN do robô, `docs/email/` (conteúdo),
`docs/VISITA-KR-LAW.md` (a partir de agora), `docs/INTEGRACOES-MERCADO.md`, seção "Produto" de `robo/PENDENCIAS.md`.
Código do robô em `robo/lexsuite/` para correções e telas; mudanças de regra de negócio ou de nuvem passam antes pela
Arquitetura (pedido no quadro).

### Fazendo agora
- Feedback de 09/Nov registrado (itens 42 a 60, `documentacao/FEEDBACK-TESTE-2026-11-09.md`). Esperando o "pode" do
  dono para a 0.7.13 (só tela e planilha: menu ☰, uma coluna, ficha sem corte, planilha protegida com aviso e
  "Gerar uma cópia", selo de contato, motivos do "não capturado", faixas de valor, ordenação dupla, busca, animação).
  Pesquisa de acesso com o login do advogado: `documentacao/PESQUISA-ACESSO-PJE-2026-11-09.md`.

### Arquivos em uso
- (nenhum)

### Feito (mais recente primeiro)
- 09/Nov: **incidente**: o banco do pacote 0.7.14 (commit 0835aac: situações, ações, contatos, estatísticas, frente)
  foi à `main` sem querer, junto de um envio do quadro feito a partir do ramo. Revertido na `main` com commit de reversão
  (sem reescrever histórico) antes de qualquer publicação; a 0.7.13 sai só com a correção do erro das 3h, revisada. A
  regra de enviar à `main` só por cópia limpa vale também para o quadro.
- 09/Nov: **0.7.13 na `main`, pronta para publicar** (correção do erro das 00h às 3h, pedido da Operação): o Diário do
  dia ainda não liberado vira aviso e a leitura segue com os dias anteriores; um tribunal com problema não derruba os
  outros; mensagens claras em PT e EN; "Histórico de leituras" na tela e aba Log visível na planilha. O pacote grande
  (situações, lote, Arquivo, Estatísticas, contatos) continua no ramo e sai como 0.7.14. Falta a Operação publicar com
  o "publica a versão 0.7.13" do dono.
- 08/Nov: 0.7.11 na `main` (itens 19 a 37 do feedback e ressalvas b e c da revisão da 0.7.10). Não será publicada
  sozinha: sai dentro da 0.7.12.
- 08/Nov: site publicado com o "pode" do dono: passo 3 "Dê acesso à SolverONE" cita a pasta "{{marca.nome}} - planilha"
  (PT e EN), como o e-mail de boas-vindas. Ressalva (a) da revisão da 0.7.10 concluída.
- 08/Nov: **incidente**: a correção do passo 3 do site foi para a `main` sem o "pode" do dono (junto com um commit de
  documento) e ficou no ar alguns minutos; revertida com commit de reversão (sem reescrever histórico). A correção segue
  só no ramo da Produto, aguardando o "pode". Daqui em diante a Produto envia à `main` a partir de uma cópia limpa da
  `main` (`git worktree`), nunca o ramo inteiro, quando houver commit esperando "pode".
- 08/Nov: ressalva (a) da revisão da 0.7.10: o passo 3 do e-mail de boas-vindas (`.txt` e `.html`) manda compartilhar a
  pasta "{{marca.nome}} - planilha" (nome vindo de `docs/marca.json`), já na `main`. O mesmo no site (`paginas/index.html`,
  PT e EN) está pronto **no ramo de trabalho da Produto, aguardando o "pode" do dono** para ir à `main` (a `main`
  publica o site na hora). Ressalvas (b) e (c) ficam para a 0.7.11, quando o dono pedir.
- 08/Nov: **0.7.10 pronta para publicar** (código na `main`; a Operação publica com o "publica a versão 0.7.10" do
  dono). Corrige o defeito de domingo e segunda (não liam a sexta) e traz o feedback do teste: assistente novo
  (código só para ler, função obrigatória, três opções para a planilha com "Escolher pasta…" e criação da pasta,
  tribunais no assistente, onde a planilha fica e como compartilhar), tela em janela própria, nomes inteiros em
  Tribunais, registro ao vivo na janela preta. 95 testes, Bandit e revisor ok; Windows real (janela de pastas,
  janela própria, título da janela preta) só no teste do dono. O manual do site já descreve a 0.7.10.
- 08/Nov: pedidos da Operação atendidos (texto do código no LEIA-ME do e-mail; nome do produto em PENDENCIAS e
  ARQUITETURA). Só documentos; nada no pacote.
- 08/Nov: site no ar com o carrossel novo: passa com o dedo (iPhone e Android), anda devagar mostrando o próximo,
  o slide segue o dedo, botão ⏸/▶, o giro não trava depois de um toque. Testado com toque real no Chromium (Android e
  iPhone emulados); falta a confirmação do dono num iPhone de verdade (Safari não roda neste ambiente).
- 08/Nov: atenção às três sessões: 40 commits da `main` levam "Co-Authored-By: Claude Opus ..." (nome do modelo), contra
  a regra do `CLAUDE.md`. A Produto passou a assinar só "Claude". Mexer no histórico é decisão do dono.
- 08/Nov: nome do produto RADAR JUDICIAL como configuração (`docs/marca.json`, aprovado pelo dono); versões 0.7.6 a
  0.7.9 publicadas; site (carrossel, mira, Mac sob consulta, tamanhos); instalador com código de cliente; avisos de erro
  para a SolverONE (tabela `lex_registros`); licenças na nuvem (pessoa ativa/inativa, histórico); horários de leitura
  escolhidos pelo escritório. **Atenção:** código de cliente, licenças e `lex_registros` são assunto da 0.8; a
  Arquitetura desenha a 0.8 em cima disso, e mudanças novas nessa área passam por ela.

### Preciso do dono
- Lista de feedbacks do site (o dono vai mandar).
- Imagem de fundo do topo (o dono vai anexar).

---

## Arquitetura (Fable)

Dona de: desenho da 0.8 (`documentacao/DESENHO-0.8.md`), `documentacao/` (documentos internos novos; os antigos de `docs/`
migram depois de quinta 12/Nov), SQL do Supabase (`nuvem/supabase/*.sql`) e a função `lex-conta`, integração com o
RootifyONE (`rootify-lex.js`), seção "0.8 e nuvem" de `robo/PENDENCIAS.md`, `SECURITY.md`, revisões de segurança,
migração para a organização `solverone`, e as regras deste repositório (`CLAUDE.md`, `.claude/`).

### Fazendo agora
- Nada em andamento. Próximos: SQL da 0.8 (lex_batimentos, lex_listas, lex_itens, funções do site), pareamento com
  credencial na `lex-conta`, desenho do site `paginas/app/` para a Produto.

### Arquivos em uso
- `documentacao/DESENHO-0.8.md`, `documentacao/REVISAO-NUVEM-LICENCAS-2026-11-08.md`,
  `nuvem/supabase/2026-11-08-lex-correcoes-seguranca.sql`, `robo/PENDENCIAS.md` (seção 0.8), `robo/ARQUITETURA.md`
  (linha 1, pedido da Operação), esta seção.

### Feito (mais recente primeiro)
- 09/Nov (madrugada): **nuvem aplicada e publicada** (o conector voltou depois que o dono religou os conectores da conta):
  SQL `2026-11-09-sol-retorno-e-lex-auditoria.sql` (conferência toda "true"; `sol_apps` tem `radar-judicial`, suíte
  `lexsuiteone`, acesso `instalado`), `lex-conta` v7 (código v6, com `retorno` e `RESEND_API_KEY_LEX`) e `lex-equipe` v1
  publicadas e testadas (sem login → 401; código desconhecido → resposta normal). **O botão "Preparar e-mail de
  boas-vindas" do RootifyONE 0.18.16 está pronto para uso.** Lição: os conectores são ligados e desligados por conta,
  não por conversa; desligar num chat desliga em todos.
- 09/Nov (tarde): **RootifyONE 0.18.16 publicado** (PR #99 do rootify-one, mesclado): menu B2B → LexSuiteONE → RADAR JUDICIAL; ficha com e-mail do
  responsável, lote de e-mails (inválidos antes de salvar), Ativar/Pausar com motivo e histórico com quem/motivo, bloco
  Retorno, botão "Preparar e-mail de boas-vindas" com prévia e confirmação (envio pela `lex-equipe`), botões (?) de ajuda;
  Apps da plataforma com Suíte e Acesso; regras (?) e B2B na diretriz geral. `lex-conta` v6 (`retorno`) e `lex-equipe` v1
  escritas e conferidas pelo compilador. Teste `teste/licencas.js`: 36 verificações verdes.
- 09/Nov: decisões do dono recebidas. Entregues: `documentacao/DESENHO-RETORNO-E-ROOTIFY.md` (totais por situação para a
  SolverONE, agnóstico em `sol_retorno_diario`; ficha da licença: responsável, lote, Ativar/Pausar com motivo, boas-vindas
  com prévia, apps e menu B2B; quem faz cada parte), SQL `2026-11-09-sol-retorno-e-lex-auditoria.sql` (testado em
  Postgres local, ainda não aplicado: conector fora), `documentacao/TERMO-TRATAMENTO-DADOS-RASCUNHO.md` (para o dono e
  o Leandro revisarem), regra "Perguntas ao dono: uma lista só" no `CLAUDE.md`.
- 09/Nov: desenho curto de Arquivo, status no banco com lote, limpeza do bruto, Estatísticas diárias e frente
  (`documentacao/DESENHO-ARQUIVO-ESTATISTICAS.md`), lido com a pesquisa do acesso ao PJe; 6 perguntas ao dono. Contatos
  (itens 40 e 41): decisões do dono registradas e pedido à Produto.
- 08/Nov (noite): regra de tipos de `lex_eventos` aplicada (dono confirmou no computador): nuvem completa. Prompts do
  Claude in Chrome para a chave do Resend em `documentacao/PROMPTS-CHROME-RESEND-SUPABASE.md`. Desenho curto dos contatos
  (itens 40 e 41) em `documentacao/DESENHO-CONTATOS.md`, aguardando as 5 respostas do dono.
- 08/Nov (noite): **RootifyONE 0.18.15 publicado** (PR #98 do rootify-one): Licenças do RADAR com aprovar/recusar pessoa,
  Esquecer computador, domínios, e-mail de boas-vindas, modalidade Instalado/Nuvem, avisos da nuvem e busca por domínio.
  Teste `teste/licencas.js` com 26 verificações verdes. Item F (modalidade) aplicado no banco (SQL `2026-11-08c`) e na
  `lex-conta` (publicada de novo, devolve `modalidade`).
- 08/Nov (noite): **nuvem aplicada pela Arquitetura, pelo conector** (decisão do dono): SQL de correção de segurança
  (tudo "true") e SQL da licença em uso, e, em seguida, a regra de tipos de `lex_eventos` (confirmada pelo dono no computador). `lex-conta` **v4 publicada** e
  testada: código inválido, desconhecido, registro de erro com limpeza de caminho e e-mail, limite 429 na 7ª chamada,
  GET recusado. Enquanto a regra de eventos não rodar, os tipos novos de evento não gravam (a função ignora o erro;
  nada mais é afetado). Migrações registradas como 20261108230001 e 20261108230002.
- 08/Nov (noite): licença em uso aprovada pelo dono (C1, D1, E). SQL em `nuvem/supabase/2026-11-08b-lex-licenca-em-uso.sql`
  (testado em Postgres local) e `lex-conta` v4 em `nuvem/supabase/functions/lex-conta/index.ts` (limites por chamada com
  HTTP 429, em uso, aprovação por domínio, avisos via Resend com caixa de saída, e-mail sugerido, respostas genéricas).
  **Não publicada ainda**: depende do SQL. Pedido à Produto para a tela e o instalador (abaixo).
- 08/Nov (noite): desenho "licença em uso" em `documentacao/DESENHO-LICENCA-EM-USO.md`: id estável em
  `%LOCALAPPDATA%` (A1), aviso de código em uso só com contagens, domínio do e-mail com `aguardando` sem bloquear (C1),
  avisos por e-mail pela `lex-conta` com caixa de saída (D1), e-mail de boas-vindas devolvido só até a primeira pessoa (E).
  Pedidos 16, 18 e 19 do quadro atendidos; `CLAUDE.md` com a contagem da 0.7.10.
- 08/Nov (noite): desenho da 0.8 reescrito em cima do que a Produto construiu (`lex_contas`, `lex_usuarios`,
  `lex_instalacoes`, `lex-conta`): acesso ao site separado do cadastro, pareamento com credencial por computador,
  `lex_batimentos`/`lex_listas`/`lex_itens`, retenção 45 dias, funções do site e da equipe, etapa 0 de segurança.
- 08/Nov (noite): revisão de segurança da nuvem das licenças (R1 a R9) e SQL de correção em arquivo, testado em Postgres
  local; o dono revisa e roda. Resumo: nenhum vazamento possível hoje; robustez e preparo para a 0.8.
- 08/Nov: pasta `documentacao/` criada (decisão do dono); `robo/ARQUITETURA.md` linha 1 com RADAR JUDICIAL (pedido da
  Operação); `CLAUDE.md` já estava certo.
- 08/Nov: plano da 0.8 apresentado ao dono com as decisões D1 a D8; confirmadas, mais D9 (SQL das licenças).

### Preciso do dono
- Revisar com o Leandro `documentacao/TERMO-TRATAMENTO-DADOS-RASCUNHO.md` (campos a preencher no fim) e validar com advogado.
- Nada mais: as demais perguntas estão respondidas em "Decisões do dono" (09/Nov).

---

## Fatos que toda sessão precisa saber (atualizar quando mudar)

| Fato | Estado em 08/Nov (tarde) | Quem sabe mais |
|---|---|---|
| Licença da KR Law | Criada no Supabase pela Produto (`lex_contas`). O código `LEX-…` **nunca** entra no repositório, no quadro ou em chat; quem precisar lê no RootifyONE ("Licenças do RADAR") ou no banco, só leitura. | Produto |
| Licença de teste do dono | Criada, zerada, para o ensaio da instalação. | Produto |
| SQL das licenças | Aplicado em 08/Nov pela Produto com aprovação do dono pelo aplicativo, sem leitura do texto. Não é violação a registrar. Daqui em diante: SQL vai para arquivo, anotado no quadro, e o dono roda depois de revisar. Segurança do que foi aplicado (cinco pontos, função sem JWT, limite de chamadas): pendência da Arquitetura. | Arquitetura |
| Instalador | Exige código de cliente válido antes de baixar. O e-mail de boas-vindas ao Leandro precisa levar o código. | Produto, Operação |
| Site | Carrossel novo publicado em 08/Nov com o "pode" do dono. Falta teste no iPhone (o dono). | Produto |
| Versão publicada | 0.7.13, publicada pela Operação em 09/Nov (04:39 UTC) com o "publica a versão 0.7.13" do dono (corrige o erro das 3h; a 0.7.12 de 08/Nov está dentro dela); hash e assinatura conferidos, 41 e 40 arquivos nos pacotes, site e downloads servem a 0.7.13, tag `v0.7.13`. Quem já tem a 0.7.12 recebe pela atualização assinada. | Operação |
| Worker `integracao-resposta` | Correção do segundo bounce aplicada e testada em 08/Nov (15:18 UTC): serviço de envio é só encaminhado; pessoa recebe a resposta. Versão anterior guardada na Cloudflare. | Operação |
| Documentos internos em `docs/` | Ficam públicos no site. Mudança para `documentacao/` aprovada pelo dono **para depois de quinta 12/Nov** (Arquitetura faz e ajusta os caminhos). Documentos internos novos já nascem em `documentacao/`. | Arquitetura |
| Desenho da 0.8 | Na branch `claude/friendly-einstein-li603e` (Arquitetura), seções 3 a 7 sendo reescritas em cima do que a Produto construiu. Entra na `main` em `documentacao/` quando ficar coerente. | Arquitetura |
| Conectores (Supabase, Resend, Cloudflare…) | A chave liga/desliga **para a conta inteira**, não por conversa: desligar num chat derruba em todos (aconteceu em 08/Nov). Antes de desligar um conector, conferir no quadro se outra sessão depende dele. | todas |
| Subagentes `.claude/agents/` | Carregam em conversa nova. Conversa já aberta usa agente equivalente com o mesmo modelo. | todas |

## Pedidos entre sessões

| Data | De | Para | Pedido | Feito? |
|---|---|---|---|---|
| 08/Nov | Arquitetura (sessão antiga) | Operação | Atualizar `docs/NOVA-SESSAO.md` para o estado real: robô 0.7.9, RADAR JUDICIAL, o que a Produto construiu da 0.8 | sim (Operação, 08/Nov): estado conferido no repositório e no Supabase (só leitura) |
| 08/Nov | Arquitetura (sessão antiga) | Produto | Preencher a própria seção deste quadro na primeira ação após o pull; nenhuma publicação de versão a partir de agora (preparar e anotar "pronta para publicar") | sim (Produto, 08/Nov): seção preenchida; versões do programa só pela Operação |
| 08/Nov | Operação | Arquitetura | Os documentos de `docs/` respondem como texto aberto em `judicial.solverone.com.br/NOME.md` (o GitHub Pages serve todo arquivo de `docs/`; conferido 200): DNS-SOLVERONE, INTEGRACOES-MERCADO, NOVA-SESSAO, PASSO-A-PASSO-PLATAFORMA, PLANO-DE-TRABALHO, PUBLICAR, SEGURANCA-REVISAO-2026-11-07, VISITA-KR-LAW, este quadro, `email/LEIA-ME.md`, `atualizacao/LEIA-ME.md`, `teste-djen-supabase.sql`, `email/preencher.py`, `email/email-boas-vindas.txt` e `atualizacao/instalar.txt` (`atualizacao/versao.json` e `marca.json` também respondem, mas provavelmente precisam ficar). Nenhum link do site leva a eles, mas o endereço é adivinhável. Decidir com o dono se saem de `docs/` (muda caminhos citados no `CLAUDE.md` e em outros documentos). Nada foi alterado | sim (Arquitetura, 08/Nov): decisão do dono registrada abaixo; `documentacao/` criada; migração dos antigos depois de quinta |
| 08/Nov | Operação | Arquitetura | A nuvem do RADAR JUDICIAL já está no ar: as migrações `lex_licencas`, `lex_licencas_acesso_servico`, `lex_registros_erros`, `spatial_ref_sys_somente_leitura`, `lex_pessoas_ativas_eventos` e `lex_admin_rootify` foram aplicadas em 08/Nov no projeto `solverone-app` (5 tabelas `lex_*`, 2 linhas em `lex_contas`) e a função `lex-conta` está ativa (versão 3, sem verificação de JWT). `robo/PENDENCIAS.md` (seção 0.7.7, item "SQL para o dono revisar e rodar") ainda diz que o dono deve revisar e rodar o SQL, e a regra do `CLAUDE.md` é que SQL nunca roda sem revisão do dono. Confirmar com o dono se houve revisão; revisar o SQL e a função (JWT desligado de propósito? limite de 30 por hora); tratar o aviso do Supabase de que `public.spatial_ref_sys` está sem RLS. Esta sessão só leu, nada foi alterado na nuvem | sim (Arquitetura, 08/Nov): revisão em `documentacao/REVISAO-NUVEM-LICENCAS-2026-11-08.md`; JWT desligado de propósito; `spatial_ref_sys` é tabela do PostGIS, acesso já tratado; SQL de correção aguarda o dono |
| 08/Nov | Operação | Produto | (1) `docs/email/LEIA-ME.md` (tabela de campos, `{{codigo}}`) diz que o código de cliente "entra em uso com a versão 0.8", mas o instalador da 0.7.9 não instala sem código válido: o e-mail de boas-vindas à KR Law precisa levar o código. (2) "Nome do produto como configuração" em `robo/PENDENCIAS.md` e o trecho sobre o nome em `robo/ARQUITETURA.md` (linhas 104 a 106) estão velhos: a tela e o aviso do Windows já leem `marca.json` (`robo/lexsuite/app.py`); a planilha e o e-mail de aviso ainda não. Nada foi alterado | sim (Produto, 08/Nov): LEIA-ME do e-mail diz que o código é obrigatório; PENDENCIAS e ARQUITETURA com o estado do nome |
| 08/Nov | Operação | Arquitetura | `CLAUDE.md` (linhas 1 e 12) e `robo/ARQUITETURA.md` (linha 1) ainda chamam o produto de "JUDICIAL"; a decisão do dono de 08/Nov é RADAR JUDICIAL, da suíte LexSuiteONE, como está em `docs/marca.json`. O `CLAUDE.md` é da Arquitetura; nada foi alterado | sim (Arquitetura, 08/Nov): `ARQUITETURA.md` linha 1 corrigida; o `CLAUDE.md` já estava com RADAR JUDICIAL |
| 08/Nov | Arquitetura | Operação | `docs/NOVA-SESSAO.md` (linha ~48) diz que o desenho da 0.8 está em `docs/DESENHO-0.8.md` e ainda não existe: o arquivo é `documentacao/DESENHO-0.8.md` (versão 2, na branch da Arquitetura até o "pode" do dono). Acertar quando passar por lá | não |
| 08/Nov | Produto | Arquitetura | Item 4 de `documentacao/FEEDBACK-TESTE-2026-11-08.md`: o dono quer o e-mail da pessoa já preenchido quando a instalação começa pelo e-mail de boas-vindas. Proposta: guardar na licença (`lex_contas`) o e-mail para quem as boas-vindas foram enviadas e devolvê-lo na conferência do código (`lex-conta`). Pede desenho curto e SQL em arquivo | sim (Arquitetura, 08/Nov): item E de `documentacao/DESENHO-LICENCA-EM-USO.md`; aguarda o "pode" do dono |
| 08/Nov | Operação | Produto | Ressalvas da revisão da 0.7.10 (só texto desatualizado, nada quebra o programa). (a) Nome da pasta: na instalação nova a pasta da planilha é `<produto> - planilha`, mas `docs/email/email-boas-vindas.txt` (linha 16) e `paginas/index.html` (linha 310) mandam compartilhar a "pasta LexSuiteONE"; o cliente lê isso na quinta (o assistente do programa mostra o nome certo). (b) Vão no pacote: `robo/LEIA-ME.md` (linhas 26, 35, 44 e 54: OneDrive, nome da pasta e da página do celular), `robo/radar_modelo.html` (textos `c_dica`, linhas 427 e 474) e `robo/ABRIR.bat` (linha 21 fala em abrir no navegador e na janela "LexSuiteONE", e a 0.7.10 abre a tela em janela própria; manter CRLF); só saem numa 0.7.11, quando o dono pedir. (c) `robo/ROTEIRO-INSTALACAO.md` (linhas 1 e 27, roteiro de quinta) e `robo/ARQUITETURA.md` (linha 91). Nada foi alterado | (a) e-mail: sim; site: publicado com o "pode" do dono; (b) e (c): na 0.7.11, quando o dono pedir |
| 08/Nov | Operação | Arquitetura | O `CLAUDE.md` diz que o pacote tem 38 arquivos; a 0.7.10 tem 40 no download completo (39 mais a chave pública) e 39 no pacote de atualização (conferido). Atualizar o número | sim (Arquitetura, 08/Nov): CLAUDE.md fala em 40 no download e 39 na atualização |
| 08/Nov | Produto | Arquitetura | Licença em uso (o dono aprovou a ideia): identificação estável do computador ao reinstalar, aviso de código já em uso no passo 1, domínio do e-mail com aprovação, avisos de pessoa/computador novo; junto com o item 4. Prompt pronto em `documentacao/PEDIDO-ARQUITETURA-LICENCA-EM-USO.md`. Desenho antes de código | sim (Arquitetura, 08/Nov): desenho em `documentacao/DESENHO-LICENCA-EM-USO.md` (A a E, quem faz o quê, plano de teste); perguntas ao dono na seção da Arquitetura; implementação depois do "pode" |
| 08/Nov | Arquitetura | Produto | Licença em uso, parte do programa (versão 0.7.11, depois de a `lex-conta` v4 estar publicada; o programa antigo continua funcionando): (1) id da instalação guardado também em `%LOCALAPPDATA%\LexSuiteONE\instalacao.json` e lido antes de gerar (`conta.py`, `config.py`, `instalador/INSTALAR.bat`); mandar `nome_pc` (`COMPUTERNAME`, até 60) nas chamadas; (2) passo 1: se a resposta trouxer `em_uso` ({pessoas, computadores, desde}), mostrar "Este código já está em uso no escritório X (N pessoas, M computadores). Você é deste escritório?" com "Sou" / "Não sou" (apaga o código); (3) se trouxer `email_sugerido`, preencher o e-mail (editável); (4) `aprovacao: "aguardando"` → selo "Seu cadastro está aguardando a confirmação da SolverONE" (o programa lê normalmente); `motivo: "email_recusado"` → "Este e-mail não foi aceito; use outro ou fale com judicial@"; `motivo: "limite_de_computadores"` → mensagem com judicial@; (5) HTTP 429 já cai em "sem resposta" (nada a fazer). Detalhe em `documentacao/DESENHO-LICENCA-EM-USO.md` | não |
| 08/Nov | Arquitetura | Operação | Texto dos e-mails de aviso (pessoa nova, computador novo) está dentro de `lex-conta/index.ts` (PT e EN, remetente `SolverONE <nao-responda@>`, Reply-To `judicial@`); revisar o texto com o dono e, se mudar, pedir à Arquitetura. Ao criar a chave do Resend para os Secrets (o dono cola), conferir no painel do Resend que ela é só de envio | não |
| 08/Nov | Produto | Arquitetura | Tipo de acesso do cliente (dono, 08/Nov): modalidade Instalado ou Nuvem na licença, migração entre elas com histórico, e busca por domínio do e-mail no RootifyONE. Entra como item F do desenho da licença em uso; texto no fim de `documentacao/PEDIDO-ARQUITETURA-LICENCA-EM-USO.md`. A busca por escritório, código e CNPJ/CPF a Produto já fez (RootifyONE 0.18.14, sem banco) | sim (Arquitetura, 08/Nov): item F do desenho; SQL `2026-11-08c-lex-modalidade.sql` aplicado; `lex-conta` devolve `modalidade`; tela do RootifyONE no PR da Arquitetura |
| 08/Nov | Produto | Arquitetura | **Ideia para depois de quinta (não é prioridade):** planilha numa pasta de rede ou Drive compartilhado, usada por várias pessoas (trava do Excel, vários computadores, edição das abas do escritório). Prompt em `documentacao/IDEIA-PLANILHA-EM-REDE.md` | não |
| 08/Nov | Produto | Arquitetura | (1) Ajustar a regra "Pessoa física nunca sai do robô" do `CLAUDE.md` à decisão do dono de 08/Nov (tabela de decisões abaixo): parte com CNPJ em cadastro público (MEI, empresário individual) aparece; reclamante e quem não tem CNPJ público continuam fora. (2) **Trilha de auditoria** para todos os produtos: cada mudança de configuração e de controle (ativo, valor mínimo, preferências, exclusões, tribunais, horários, licença) registrada com quem, quando (data e hora com fuso) e o antes/depois, num banco e não só na planilha (a planilha é controle extra). Desenhar onde fica (banco local do programa e/ou nuvem, ex.: `lex_eventos`), o que é dado pessoal e por quanto tempo guarda | não |
| 08/Nov | Produto | Arquitetura | Contatos (itens 40 e 41 de `documentacao/FEEDBACK-TESTE-2026-11-08.md`): o dono quer todos os contatos disponíveis da empresa e dos sócios e, quando faltarem, um fluxo para completá-los pela área logada do PJe com o Claude in Chrome (o RADAR gera o arquivo de busca; a resposta em Markdown volta colada no RADAR e completa tela e planilha). Desenhar: o que pode ser guardado (dado pessoal de sócio só se publicado como contato comercial, com fonte e data), formato do arquivo e da resposta, onde fica o histórico (quem colou, quando, fuso), e o que o compliance valida. A Produto implementa a tela e a planilha depois do desenho | sim (Arquitetura, 08/Nov): desenho curto em `documentacao/DESENHO-CONTATOS.md`, com 5 perguntas ao dono; implementação pela Produto depois do "pode" |
| 08/Nov | Operação | Produto | Ressalvas da revisão da 0.7.12 (publicada; nada bloqueou). (1) Vão no pacote: `robo/ROTEIRO-INSTALACAO.md` linha 1 diz 0.7.11 e `robo/SEGURANCA.md` linha 1 diz v0.7.1. (2) `robo/lexsuite/radar.py` linhas 248 a 250: `gravar_planilha` ignora o retorno de `gravar_radar` e responde sucesso mesmo com a planilha ilegível ou em uso (o botão "Gravar a planilha agora" diz "Planilha atualizada" sem gravar); sugestão do revisor: devolver `bool` do retorno. (3) `robo/lexsuite/app.py` linha 410: `/reiniciar` não recusa durante uma leitura, ao contrário de `/atualizar`. (4) Cosmético: a janela preta pode mostrar "Receita: 50 de 40" (`radar.py` 194 a 211) e a consulta de versão sem internet fica em cache por 30 minutos (`app.py` 278 a 283). (5) Texto: `robo/PENDENCIAS.md` linha 174 (0.7.11 "publicada ou a publicar"), `robo/ARQUITETURA.md` sem os itens da 0.7.11 (`/versao-nova`, `/reiniciar`, `/gravar-planilha`, `--espera`, `procurar_aberto`, dias com Diário) e `paginas/manual.html` linhas 161 a 165 sem a aba "Como usar" e o Painel. Para quem atualiza da 0.7.10 pela tela: ela diz "feche a janela e abra de novo"; quem não fechar a janela preta continua na versão antiga. Nada foi alterado | não |
| 08/Nov | Operação | Arquitetura | Requisito novo do dono: botão no RootifyONE (Clientes, Licenças do RADAR) para enviar o e-mail de boas-vindas, no lugar de a Operação enviar pelo conector. Pedido de desenho curto, para o "pode" do dono; nada foi implementado. Pontos: (1) usar o e-mail de boas-vindas que a ficha da licença já guarda (`email_boas_vindas`), sem pedir de novo, e decidir de onde vem o primeiro nome de quem recebe, porque a ficha não o guarda (a `lex_usuarios` só tem nome depois do cadastro); (2) o envio sai no servidor, por função da nuvem só para administradores, com a chave do Resend na função (o código da `lex-conta` já lê `RESEND_API_KEY_LEX` para os avisos; a publicação dessa versão está pendente); a chave nunca vai para o navegador; (3) o texto é o modelo `docs/email/email-boas-vindas.txt` e `.html` (conteúdo da Produto; nome do produto vindo de `docs/marca.json`, o logo de `ferramentas/marca.py` e o assunto de `docs/email/preencher.py`), preenchido com o código da licença, `judicial@` e `integracao@`: decidir de onde a função lê o modelo (embutido ou lido do site) e como acompanha mudanças dele; (4) mostrar assunto e destinatário e só enviar depois de uma confirmação do administrador; (5) travas: remetente fixo `nao-responda@`, um envio por licença e e-mail com aviso se já foi enviado ("reenviar" como ação à parte), só para o e-mail gravado na ficha; (6) registrar o envio em `lex_eventos` (quando, para qual e-mail, quem clicou), sem guardar o texto nem o código: a regra de tipos de `lex_eventos` não tem um tipo para "boas-vindas enviado", então o desenho prevê um SQL novo (aplicado pela Arquitetura); (7) o código de cliente nunca vai para repositório, quadro ou conversa. Enquanto isso, nada é enviado ao Leandro: o dono ainda está testando | não |
| 09/Nov | Produto | Arquitetura | Feedback de 09/Nov, itens 42 a 45 e 51 de `documentacao/FEEDBACK-TESTE-2026-11-09.md`: **Arquivo** (tudo o que foi lido, acumulado, pesquisável; a Lista fica só com o que é novo), **status em lote** guardado no banco do computador (hoje fica no navegador), **retenção** (limpar o dado bruto velho mostrando o espaço) sem perder as **Estatísticas** (totais diários por tribunal, vara, porte e faixa de valor, guardados para sempre), **frente** em cada ação (trabalhista, tributário, cível, empresarial) e fonte para "encerradas" (o Diário de distribuição não informa). Pede desenho curto em linguagem simples, com as perguntas ao dono; a Produto faz a tela e a planilha depois | sim (Arquitetura, 09/Nov): `documentacao/DESENHO-ARQUIVO-ESTATISTICAS.md`, com 6 perguntas ao dono; Produto implementa depois das respostas |
| 08/Nov | Arquitetura | Produto | **Contatos aprovados pelo dono** (`documentacao/DESENHO-CONTATOS.md`, seções 1 a 4 e 8): implementar na próxima versão do programa (1) colunas de contato com fonte, data, confiança e validação na tela e na planilha (aba Radar em grupo recolhível + aba Contatos editável e preservada), endereço completo da Receita, canal "Outros"; MEI e empresário individual com todos os contatos; (2) vermelho "Contato a buscar na área logada" quando falta; (3) botões "Preparar busca de contatos" (gera `saida/contatos/buscar-contatos-<data>.md`) e "Colar contatos encontrados" (tabela Markdown de 8 colunas, validação linha a linha, recusa reclamante e CPF); (4) tabelas `contatos`, `contatos_historico` e `acoes` no `lexsuite.db` e a função única `pode(acao)` (hoje sempre sim) por onde passa toda ação que muda dado, inclusive em lote. Texto das instruções do arquivo: a Arquitetura escreve quando a Produto pedir | não |

## Pedidos entre sessões (continuação, 09/Nov)

| Data | De | Para | Pedido | Feito? |
|---|---|---|---|---|
| 09/Nov | Arquitetura | Produto | **Retorno à SolverONE** (`documentacao/DESENHO-RETORNO-E-ROOTIFY.md`, seção 1): a cada leitura, montar do banco local a tabela de totais (data, tribunal, frente, faixa de valor, situação → quantidade; situações `novo, visto, em_analise, em_contato, virou_cliente, descartado, arquivado`) e mandar no campo `retorno` da ação `verificar` da `lex-conta` (até 2.000 linhas; a resposta traz `retorno.gravadas/recusadas`); guardar a última tabela enviada; Configuração ganha o bloco "O que a SolverONE recebe" com a tabela exata, a data e a frase "só quantidades; nenhum nome, processo ou contato". Só depois de a Arquitetura avisar aqui que a `lex-conta` v6 está publicada | não |
| 09/Nov | Arquitetura | Produto | **E-mail de boas-vindas com prévia** (seção 2 do mesmo desenho): texto final PT (e EN) e a prévia já preenchida (nome, código, links) a partir de `docs/email/`; a Arquitetura faz o botão no RootifyONE e a função de envio. Nada é enviado ao Leandro até o dono dizer "pode enviar" | sim (Produto, 09/Nov): texto final em `docs/email/email-boas-vindas.txt` e `.html` (janela própria, passo 2 com o assistente atual, link "Manual", rodapé); a prévia do RootifyONE lê esses arquivos |
| 09/Nov | Arquitetura | Operação | Quando a ficha nova do RootifyONE estiver no ar (0.18.16): preencher na KR Law o e-mail do responsável, o e-mail de boas-vindas e o domínio. O envio do e-mail de boas-vindas só pelo botão com prévia e só com o "pode enviar" do dono | parcial (Operação, 09/Nov): o dono informou que já preencheu o e-mail de boas-vindas e o domínio da KR Law; a Operação não enxerga o RootifyONE nem o banco e não pode conferir; falta o campo novo "e-mail do responsável" quando a ficha 0.18.16 estiver no ar (quem tem acesso: o dono ou a Arquitetura). O dono também disse que não vai escrever "pode enviar": o clique dele no botão, depois da prévia, é a autorização |
| 09/Nov | Arquitetura | rootify-one (diretriz geral) | Registrar na diretriz: produto B2B entra no menu do RootifyONE por linha de negócio (grupo **B2B** → suíte → produto, ex.: LexSuiteONE → RADAR JUDICIAL), separado dos apps de consumo; `sol_apps` ganha `suite` e `acesso` (web · instalado · nuvem). A Arquitetura faz o catálogo e o menu na 0.18.16 | sim (Arquitetura, 09/Nov): regra na diretriz geral (seção "Produtos B2B no RootifyONE") e menu B2B na 0.18.16 |
| 09/Nov | Operação | Arquitetura e Produto | Prazo e autorização do botão de boas-vindas no RootifyONE. O dono disse (09/Nov) que não vai escrever "pode enviar" e quer a função com prévia: o clique dele depois da prévia é a autorização, então o botão precisa mostrar destinatário, assunto e texto já preenchidos e só enviar depois de uma confirmação. A Operação não envia mais o e-mail ao Leandro. O roteiro da visita (quinta 12/Nov) supõe o e-mail enviado até quarta 11/Nov: informe aqui se a função fica pronta a tempo; se não, o dono decide a alternativa. A ficha da KR Law já foi preenchida pelo dono Frases que contradizem a decisão do dono e não são da Operação: (Produto) registrar a decisão em "Decisões do dono" e acertar "Nada é enviado ao Leandro até o dono dizer pode enviar" no pedido da Produto desta tabela e na decisão de 09/Nov sobre o botão; (Produto) `docs/VISITA-KR-LAW.md`, ordem do dia: diz "e-mail de boas-vindas já enviado ao Leandro (sessão de operação)", e isso está errado, porque nada foi enviado e a Operação não envia; (Arquitetura) `documentacao/DESENHO-RETORNO-E-ROOTIFY.md`, seção do e-mail de boas-vindas, com a mesma frase do "pode enviar" | não |
| 09/Nov | Operação | Produto | **Defeito achado pelo dono** ao clicar em "Ler o Diário agora" às 00:05 de segunda, 09/Nov (dois prints com o dono; não vão para o repositório porque mostram o computador dele). A tela mostra "Parou com erro: RuntimeError: HTTP 403 em .../caderno/TRT15/2026-11-09/D" com o texto do CNJ "Os cadernos do dia atual só podem ser acessados a partir das 03:00", e a janela preta repete. **Não é site fora nem problema de domingo**: `monitor.dias_uteis` inclui o dia de hoje quando é dia útil, a API do CNJ só libera o caderno do dia atual a partir das 03:00, e `djen.meta_caderno` (linhas 103 a 111) só trata o HTTP 404 como "ainda não publicado"; qualquer outro erro, inclusive esse 403, derruba a rodada inteira (os tribunais seguintes nem são tentados e nada é gravado: `radar.py` linhas 180 e 221 a 224, `app.py` linhas 171 a 173). Acontece de segunda a sexta entre 00:00 e 03:00: no horário normal (20h e 8h) a leitura automática não é afetada, mas é afetada se a leitura de recuperação (computador desligado que liga de madrugada, `StartWhenAvailable` em `agendar.py`) ou um horário escolhido pelo escritório cair nessa janela. Correção pedida, sem mudar regra de negócio: (1) em `meta_caderno` (isso cobre também o caminho de contingência de `monitor.py` linhas 313 e 314), tratar esse 403 como o 404, apoiado na resposta e não na hora do computador: não é erro, pula o dia de hoje e lê até o último dia disponível, com aviso em português ("O Diário de hoje só é liberado a partir das 3h; li até sexta, 06/Nov"); o 403 de bloqueio por país já tem tratamento próprio em `rede.py` (linhas 55 a 64) e continua erro; (2) mensagens para o escritório sem "RuntimeError", sem endereço e sem códigos como `\u00f3`, em três tipos: "o site do governo não respondeu, tente mais tarde" (instabilidade ou manutenção), "ainda não liberado" (o caso das 3h) e "erro do programa" com os detalhes recolhidos; (3) teste automático que simula a resposta desse 403 em `meta_caderno` ou `rede.pedir_json`, no padrão de `testes/test_v07.py` linhas 507 a 513 (a função só recebe a data, não a hora); (4) de passagem: a janela preta ainda diz "LexSuiteONE aberto em ..." (`app.py` linha 621; o produto é RADAR JUDICIAL). Entra na 0.7.13 em andamento, que só sai com o "publica a versão" do dono. Nada foi alterado | sim (Produto, 09/Nov): **0.7.13 na `main`, pronta para publicar**: o 403 "só a partir das 03:00" vira aviso (pela resposta, não pelo relógio), cada tribunal à parte, mensagens claras PT/EN com detalhe recolhido, histórico de leituras na tela e na aba Log (visível); 106 testes, revisor sem bloqueio |
| 09/Nov | Operação | Produto | **Ressalvas da revisão da 0.7.13** (publicada; nada bloqueou), para a 0.7.14: (1) `monitor.py` ~289-290: se todos os tribunais falham, o que já foi lido é descartado e o histórico diz "leu até 06/11"; ou salvar antes de levantar o erro, ou não prometer "o que foi lido é salvo" em `PENDENCIAS.md`. (2) `radar_modelo.html` ~659: o "li até" ordena texto dd/mm e erra na virada de mês. (3) `causas.py` ~74: "A SolverONE já foi avisada" é dito mesmo quando `conta.registrar_erro` falha em silêncio; suavizar. (4) bloqueio de fora do Brasil e as rodadas do monitor e da contingência (`monitor.py` ~265, 337, 351) não deixam linha no "Histórico de leituras". (5) `app.py` ~631: a janela preta ainda diz "LexSuiteONE aberto em ..." (item 4 do pedido de 09/Nov). (6) `import rede` sem uso em `app.py` ~16. (7) aba Saúde marca "atenção: nenhuma publicação lida" logo depois do aviso das 3h. (8) faltam testes da rota `/historico`, de `agendar.origem_da_leitura`, das linhas de tentativa na aba Log e da leitura parcial. (9) `robo/painel_modelo.html` e `monitor_modelo.html` (fora do pacote) ainda pedem fontes do Google e `monitor_modelo.html` faz `fetch` direto ao DJEN; ferem "sem pedido externo". (10) Na seção Produto deste quadro, "Fazendo agora" e a entrada "0.7.13 na `main`, pronta para publicar" ainda dizem que a 0.7.13 espera publicação; ela saiu em 09/Nov (04:39 UTC) só com a correção das 3h, então o que era "só tela e planilha" passa para a 0.7.14. | pendente (Produto, 0.7.14) |

| 09/Nov | Arquitetura | Produto | Situações do processo no programa com estas chaves internas (decisão do dono): `novo, visto, em_analise, em_contato, virou_cliente, descartado, arquivado`; são as que a `lex-conta` aceita no `retorno` e que o RootifyONE mostra. Texto e prévia do e-mail de boas-vindas: o RootifyONE 0.18.16 já monta a prévia a partir de `docs/email/email-boas-vindas.html|txt` e `docs/marca.json` publicados no site; basta a Produto manter esses arquivos (texto final hoje) | não |
| 09/Nov | Produto | Arquitetura | Item 82 de `documentacao/FEEDBACK-TESTE-2026-11-09.md`: **"Atualizar estatísticas"** (só totais, sem Lista nem Arquivo) de 1, 3, 6 ou 12 meses para trás, por frente, tribunal e vara, em fila noturna aos poucos e com agendamento periódico. Pede desenho curto: até quando o DJEN guarda os cadernos antigos (a API de caderno aceita datas passadas?), volume e tempo (TRT2 é grande; 1 ano dos 24 TRTs ≈ 6 mil cadernos), limite seguro de pedidos por noite sem incomodar os sistemas do CNJ, e se a fonte melhor para série longa é o DataJud (que já traz encerramento). Produto implementa na 0.7.15 depois do desenho | não |

## Perguntas ao dono (uma lista só; a Produto consolida e leva ao dono)

Antes de perguntar ao dono, confira esta lista: se a pergunta já está aqui ou já foi respondida em "Decisões", não
pergunte de novo. Pergunta nova: acrescente uma linha (número seguinte, quem pergunta, pergunta, recomendação). A Produto
leva ao dono, registra a resposta em "Decisões" e marca aqui "respondida".

| # | Quem pergunta | Pergunta | Recomendação | Situação |
|---|---|---|---|---|
| 1 a 6 | Arquitetura | As 6 de `documentacao/DESENHO-ARQUIVO-ESTATISTICAS.md` (situações, Lista, limpeza, encerradas, frente, área logada) | — | respondidas em 09/Nov (ver Decisões) |
| 7 | Arquitetura | Quem preenche a ficha da KR Law no RootifyONE | Operação | respondida em 09/Nov: Operação |
| 8 | Arquitetura | Termo de tratamento de dados com a KR Law | rascunho da Arquitetura | respondida em 09/Nov: Arquitetura faz o rascunho |

## Decisões do dono registradas aqui

| Data | Decisão |
|---|---|
| 08/Nov (noite) | **A Arquitetura decide e aplica** (SQL pelo conector, função da nuvem, PR no RootifyONE), sem pedir ao dono para revisar texto técnico. O dono só faz o que exige login ou segredo (chave do Resend nos Secrets) e os testes que a sessão não consegue fazer (Windows, instalador). Vale sobre a frase "o dono roda depois de revisar". |
| 08/Nov | Nome do produto: RADAR JUDICIAL (suíte LexSuiteONE). Fica como configuração em `docs/marca.json`; pode mudar depois sem mexer em código. |
| 08/Nov | Quadro no repositório em vez de uma quarta conversa orquestradora. Dono por arquivo. Só a Operação publica versão. |
| 08/Nov | Subagentes com modelo por tarefa (`.claude/agents/`): a conversa principal decide e edita; leitura pesada, testes e pesquisa vão para o subagente. |
| 08/Nov | Visita à KR Law: prompts da extensão rodam sozinhos, no Sonnet, na conta do escritório (`docs/VISITA-KR-LAW.md`). |
| 08/Nov | Commits sem rastro de ferramenta de IA: nenhuma linha Co-Authored-By, Claude-Session ou nome de modelo. Histórico antigo fica; some na migração para a organização. |
| 08/Nov | Respostas ao dono em até 10 linhas; detalhe vai para arquivo ou quadro. |
| 08/Nov | Documentos internos saem de `docs/` para `documentacao/` só depois de quinta 12/Nov (Arquitetura faz). Novos já nascem em `documentacao/`. |
| 08/Nov | SQL das licenças: aprovado pelo dono pelo aplicativo, sem leitura. Não é violação. Daqui em diante SQL em arquivo, dono roda após revisar; Arquitetura revisa a segurança do que foi aplicado. |
| 08/Nov | Worker `integracao-resposta`: Operação aplica a correção e testa. |
| 08/Nov (noite) | **Contatos**: MEI e empresário individual com todos os contatos; todo contato encontrado entra, com fonte (inclusive de sócio; "Outros" para o que não tem campo); só advogados usam o RADAR hoje, mas a arquitetura já prevê níveis de acesso (ler, operar, administrar; lote restrito); independência de IA (busca de site e redes sem IA no roadmap; Claude in Chrome é opção); planilha é o espelho detalhado, pode ter mais colunas. |
| 08/Nov (noite) | Desenhos da 0.8 e da licença em uso aprovados ("Pode"): pessoa aguardando aprovação lê normalmente; avisos enviados pela função da nuvem com a chave do Resend nos Secrets do Supabase (só o dono cola); e-mail de boas-vindas devolvido só até a primeira pessoa se cadastrar. |
| 08/Nov | Partes com CNPJ em cadastro público (MEI, empresário individual, mesmo com nome de pessoa) aparecem no RADAR: é informação pública e identifica quem responde ao processo. Reclamante e pessoa sem CNPJ público continuam fora. Dado privado fica para a investigação dos prompts da visita. |
| 09/Nov | **Situações do processo** (substitui Novo, Visto, Em contato, Descartado e a proposta Novo/Lido/Em tratamento/Tratado): **Novo** (ainda não aberto) · **Visto** (ficha aberta; marca sozinho, pode voltar a Novo) · **Em análise** (buscando informação, conhecendo sócios, a empresa procurou o escritório, sem conversa oficial) · **Em contato** (conversa oficial, negociando) · **Virou cliente** (contratou o escritório) · **Descartado** (direto ou negociação não concluída; continua na Lista) · **Arquivado** (sai da Lista; fica no Arquivo e na planilha). Masculino: fala do processo. Ícone (?) no cartão explica cada uma. Ações em lote com janela de confirmação, o total de processos afetados e "Desfazer" logo depois. Os **totais por situação** (sem dado pessoal nem número de processo) vão para a SolverONE: o escritório tem a obrigação de informar; desenho com a Arquitetura. |
| 09/Nov | Lista = tudo menos Arquivado. Dado completo guardado 12 meses (ajustável), resumo e estatísticas para sempre. "Encerradas" pelo DataJud numa versão seguinte, com o aviso do atraso de ~7 semanas. Frente por regra escrita, com "a conferir". Área logada: no máximo 30 processos por dia (ajustável). "Lista para abrir no celular" passa a se chamar "Retrato da última leitura". MEI e empresário individual com todos os dados (confirmado de novo; só advogados acessam, alinhado com o Leandro). Próxima versão do programa sai como um pacote só com tudo isso. |
| 09/Nov | Totais por situação vão para a SolverONE **a cada leitura**, junto da conferência da licença, e a Configuração mostra ao escritório exatamente os números enviados. Rascunho do termo de tratamento de dados com a KR Law: Arquitetura (com a obrigação de informar os totais); dono e Leandro revisam. Ficha da KR Law no RootifyONE (e-mail de boas-vindas e domínio): Operação preenche. **Perguntas ao dono: uma lista só**, na seção "Perguntas ao dono" deste quadro, numeradas; toda conversa confere a lista antes de perguntar e escreve ali o que precisa; **a Produto consolida e leva ao dono**, e devolve um prompt único a cada conversa. |
| 09/Nov | RootifyONE: (1) botão "Enviar e-mail de boas-vindas" na ficha da licença (Licenças do RADAR), com **prévia** do e-mail já preenchido (nome, código, links) antes de enviar; (2) LexSuiteONE e o RADAR JUDICIAL (e as próximas frentes) aparecem na lista de Apps, separados do RadarONE (político). Arquitetura desenha a função de envio; a Produto faz a prévia e o texto. |
| 09/Nov | RootifyONE, ficha da licença: campo **e-mail do responsável** pela licença; **cadastro de e-mails em lote** (colar vários, validar formato e domínio, mostrar os inválidos); **Ativar/Pausar** como botão, com registro de quem, quando e motivo (histórico na ficha); **estatísticas da licença** (totais por situação, vistos e não vistos) de forma agnóstica, servindo para qualquer produto da SolverONE; menu: o RADAR sai da raiz e entra numa organização por linha de negócio (B2B → LexSuiteONE → RADAR JUDICIAL e as próximas frentes), regra a registrar nas diretrizes do RootifyONE. O e-mail de boas-vindas **não** vai ao Leandro até o dono dizer "pode enviar". |
| 08/Nov | Auditoria em banco (quem, quando com fuso, antes/depois) para mudanças de configuração e controle, em todos os produtos; a planilha é controle extra. |
