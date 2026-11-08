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
- E-mail de boas-vindas ao Leandro: pronto, fora do repositório (o código não entra no repositório, no quadro nem em
  conversa). Falta o endereço dele e o "pode" do dono para enviar.

### Arquivos em uso
- (nenhum)

### Feito (mais recente primeiro)
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
- E-mail corporativo do Leandro, até quarta (11/Nov): o e-mail de boas-vindas fica pronto; falta o endereço e o "pode"
  do dono para enviar.
- Drive: o dono restringe "Estudos de Casos Juridicos" (o conector não altera compartilhamento) e avisa "feito"; eu
  confiro as permissões e atualizo a pasta do Drive para a versão atual (0.7.9, pacote RADAR).

---

## Produto (Opus)

Dona de: `paginas/`, `docs/index.html` e `docs/404.html` (gerados), `docs/manual.html`, `docs/marca.json`,
`robo/MANUAL-DO-ESCRITORIO.html`, `robo/radar_modelo.html`, textos PT/EN do robô, `docs/email/` (conteúdo),
`docs/VISITA-KR-LAW.md` (a partir de agora), `docs/INTEGRACOES-MERCADO.md`, seção "Produto" de `robo/PENDENCIAS.md`.
Código do robô em `robo/lexsuite/` para correções e telas; mudanças de regra de negócio ou de nuvem passam antes pela
Arquitetura (pedido no quadro).

### Fazendo agora
- 0.7.12 (visual): painel com gráficos na tela e planilha com cores e filtros (itens 38 e 39 do feedback), com o
  "pode" do dono de 08/Nov. Contatos (40 e 41) esperam o desenho da Arquitetura.

### Arquivos em uso
- (nenhum)

### Feito (mais recente primeiro)
- 08/Nov: **0.7.11 na `main`, pronta para publicar** com o "pode" do dono (itens 19 a 37 do feedback e ressalvas b e
  c da revisão da 0.7.10). Falta a Operação publicar com o "publica a versão 0.7.11" do dono.
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
- Nada em andamento. Próximos (depois dos dois passos do dono): SQL da 0.8 (lex_batimentos, lex_listas, lex_itens,
  funções do site), pareamento com credencial na `lex-conta`, site `paginas/app/` (desenho para a Produto).

### Arquivos em uso
- `documentacao/DESENHO-0.8.md`, `documentacao/REVISAO-NUVEM-LICENCAS-2026-11-08.md`,
  `nuvem/supabase/2026-11-08-lex-correcoes-seguranca.sql`, `robo/PENDENCIAS.md` (seção 0.8), `robo/ARQUITETURA.md`
  (linha 1, pedido da Operação), esta seção.

### Feito (mais recente primeiro)
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
- Chave do Resend nos Secrets do Supabase como `RESEND_API_KEY` (passo a passo em `documentacao/DESENHO-LICENCA-EM-USO.md`);
  sem ela os avisos ficam "pendente", nada quebra. Na ficha da KR Law: e-mail de boas-vindas e domínio.
- Termo de tratamento de dados com a KR Law (bloqueante para a 0.8 entrar no ar).

---

## Fatos que toda sessão precisa saber (atualizar quando mudar)

| Fato | Estado em 08/Nov (tarde) | Quem sabe mais |
|---|---|---|
| Licença da KR Law | Criada no Supabase pela Produto (`lex_contas`). O código `LEX-…` **nunca** entra no repositório, no quadro ou em chat; quem precisar lê no RootifyONE ("Licenças do RADAR") ou no banco, só leitura. | Produto |
| Licença de teste do dono | Criada, zerada, para o ensaio da instalação. | Produto |
| SQL das licenças | Aplicado em 08/Nov pela Produto com aprovação do dono pelo aplicativo, sem leitura do texto. Não é violação a registrar. Daqui em diante: SQL vai para arquivo, anotado no quadro, e o dono roda depois de revisar. Segurança do que foi aplicado (cinco pontos, função sem JWT, limite de chamadas): pendência da Arquitetura. | Arquitetura |
| Instalador | Exige código de cliente válido antes de baixar. O e-mail de boas-vindas ao Leandro precisa levar o código. | Produto, Operação |
| Site | Carrossel novo publicado em 08/Nov com o "pode" do dono. Falta teste no iPhone (o dono). | Produto |
| Versão publicada | 0.7.10, publicada pela Operação em 08/Nov (16:39 UTC) com o "pode" do dono; hash e assinatura conferidos, site e downloads servem a 0.7.10, tag `v0.7.10`. Quem já tem a 0.7.9 recebe pela atualização assinada. | Operação |
| Worker `integracao-resposta` | Correção do segundo bounce aplicada e testada em 08/Nov (15:18 UTC): serviço de envio é só encaminhado; pessoa recebe a resposta. Versão anterior guardada na Cloudflare. | Operação |
| Documentos internos em `docs/` | Ficam públicos no site. Mudança para `documentacao/` aprovada pelo dono **para depois de quinta 12/Nov** (Arquitetura faz e ajusta os caminhos). Documentos internos novos já nascem em `documentacao/`. | Arquitetura |
| Desenho da 0.8 | Na branch `claude/friendly-einstein-li603e` (Arquitetura), seções 3 a 7 sendo reescritas em cima do que a Produto construiu. Entra na `main` em `documentacao/` quando ficar coerente. | Arquitetura |
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
| 08/Nov | Produto | Arquitetura | Contatos (itens 40 e 41 de `documentacao/FEEDBACK-TESTE-2026-11-08.md`): o dono quer todos os contatos disponíveis da empresa e dos sócios e, quando faltarem, um fluxo para completá-los pela área logada do PJe com o Claude in Chrome (o RADAR gera o arquivo de busca; a resposta em Markdown volta colada no RADAR e completa tela e planilha). Desenhar: o que pode ser guardado (dado pessoal de sócio só se publicado como contato comercial, com fonte e data), formato do arquivo e da resposta, onde fica o histórico (quem colou, quando, fuso), e o que o compliance valida. A Produto implementa a tela e a planilha depois do desenho | não |

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
| 08/Nov (noite) | Desenhos da 0.8 e da licença em uso aprovados ("Pode"): pessoa aguardando aprovação lê normalmente; avisos enviados pela função da nuvem com a chave do Resend nos Secrets do Supabase (só o dono cola); e-mail de boas-vindas devolvido só até a primeira pessoa se cadastrar. |
| 08/Nov | Partes com CNPJ em cadastro público (MEI, empresário individual, mesmo com nome de pessoa) aparecem no RADAR: é informação pública e identifica quem responde ao processo. Reclamante e pessoa sem CNPJ público continuam fora. Dado privado fica para a investigação dos prompts da visita. |
| 08/Nov | Auditoria em banco (quem, quando com fuso, antes/depois) para mudanças de configuração e controle, em todos os produtos; a planilha é controle extra. |
