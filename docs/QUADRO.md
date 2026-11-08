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
- (vazio)

### Arquivos em uso
- (nenhum)

### Feito (mais recente primeiro)
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

Dona de: desenho da 0.8 (`docs/DESENHO-0.8.md`), SQL do Supabase (`sql/` ou onde for combinado), integração com o
RootifyONE, seção "0.8 e nuvem" de `robo/PENDENCIAS.md`, `SECURITY.md`, revisões de segurança, migração para a
organização `solverone`, e as regras deste repositório (`CLAUDE.md`, `.claude/`).

### Fazendo agora
- (preencher)

### Arquivos em uso
- (preencher)

### Feito (mais recente primeiro)
- 08/Nov: plano da 0.8 apresentado ao dono com as decisões D1 a D8. Antes de escrever o desenho, ler o que a Produto já
  construiu (código de cliente, licenças, `lex_registros`) e desenhar em cima, não do zero.

### Preciso do dono
- Confirmação das decisões D1 a D8 (o dono tem o texto pronto).

---

## Fatos que toda sessão precisa saber (atualizar quando mudar)

| Fato | Estado em 08/Nov (tarde) | Quem sabe mais |
|---|---|---|
| Licença da KR Law | Criada no Supabase pela Produto (`lex_contas`). O código `LEX-…` **nunca** entra no repositório, no quadro ou em chat; quem precisar lê no RootifyONE ("Licenças do RADAR") ou no banco, só leitura. | Produto |
| Licença de teste do dono | Criada, zerada, para o ensaio da instalação. | Produto |
| SQL das licenças | Aplicado em 08/Nov pela Produto com aprovação do dono pelo aplicativo, sem leitura do texto. Não é violação a registrar. Daqui em diante: SQL vai para arquivo, anotado no quadro, e o dono roda depois de revisar. Segurança do que foi aplicado (cinco pontos, função sem JWT, limite de chamadas): pendência da Arquitetura. | Arquitetura |
| Instalador | Exige código de cliente válido antes de baixar. O e-mail de boas-vindas ao Leandro precisa levar o código. | Produto, Operação |
| Site | Carrossel novo publicado em 08/Nov com o "pode" do dono. Falta teste no iPhone (o dono). | Produto |
| Worker `integracao-resposta` | Correção do segundo bounce aplicada e testada em 08/Nov (15:18 UTC): serviço de envio é só encaminhado; pessoa recebe a resposta. Versão anterior guardada na Cloudflare. | Operação |
| Documentos internos em `docs/` | Ficam públicos no site. Mudança para `documentacao/` aprovada pelo dono **para depois de quinta 12/Nov** (Arquitetura faz e ajusta os caminhos). Documentos internos novos já nascem em `documentacao/`. | Arquitetura |
| Desenho da 0.8 | Na branch `claude/friendly-einstein-li603e` (Arquitetura), seções 3 a 7 sendo reescritas em cima do que a Produto construiu. Entra na `main` em `documentacao/` quando ficar coerente. | Arquitetura |
| Subagentes `.claude/agents/` | Carregam em conversa nova. Conversa já aberta usa agente equivalente com o mesmo modelo. | todas |

## Pedidos entre sessões

| Data | De | Para | Pedido | Feito? |
|---|---|---|---|---|
| 08/Nov | Arquitetura (sessão antiga) | Operação | Atualizar `docs/NOVA-SESSAO.md` para o estado real: robô 0.7.9, RADAR JUDICIAL, o que a Produto construiu da 0.8 | sim (Operação, 08/Nov): estado conferido no repositório e no Supabase (só leitura) |
| 08/Nov | Arquitetura (sessão antiga) | Produto | Preencher a própria seção deste quadro na primeira ação após o pull; nenhuma publicação de versão a partir de agora (preparar e anotar "pronta para publicar") | sim (Produto, 08/Nov): seção preenchida; versões do programa só pela Operação |
| 08/Nov | Operação | Arquitetura | Os documentos de `docs/` respondem como texto aberto em `judicial.solverone.com.br/NOME.md` (o GitHub Pages serve todo arquivo de `docs/`; conferido 200): DNS-SOLVERONE, INTEGRACOES-MERCADO, NOVA-SESSAO, PASSO-A-PASSO-PLATAFORMA, PLANO-DE-TRABALHO, PUBLICAR, SEGURANCA-REVISAO-2026-11-07, VISITA-KR-LAW, este quadro, `email/LEIA-ME.md`, `atualizacao/LEIA-ME.md`, `teste-djen-supabase.sql`, `email/preencher.py`, `email/email-boas-vindas.txt` e `atualizacao/instalar.txt` (`atualizacao/versao.json` e `marca.json` também respondem, mas provavelmente precisam ficar). Nenhum link do site leva a eles, mas o endereço é adivinhável. Decidir com o dono se saem de `docs/` (muda caminhos citados no `CLAUDE.md` e em outros documentos). Nada foi alterado | não |
| 08/Nov | Operação | Arquitetura | A nuvem do RADAR JUDICIAL já está no ar: as migrações `lex_licencas`, `lex_licencas_acesso_servico`, `lex_registros_erros`, `spatial_ref_sys_somente_leitura`, `lex_pessoas_ativas_eventos` e `lex_admin_rootify` foram aplicadas em 08/Nov no projeto `solverone-app` (5 tabelas `lex_*`, 2 linhas em `lex_contas`) e a função `lex-conta` está ativa (versão 3, sem verificação de JWT). `robo/PENDENCIAS.md` (seção 0.7.7, item "SQL para o dono revisar e rodar") ainda diz que o dono deve revisar e rodar o SQL, e a regra do `CLAUDE.md` é que SQL nunca roda sem revisão do dono. Confirmar com o dono se houve revisão; revisar o SQL e a função (JWT desligado de propósito? limite de 30 por hora); tratar o aviso do Supabase de que `public.spatial_ref_sys` está sem RLS. Esta sessão só leu, nada foi alterado na nuvem | não |
| 08/Nov | Operação | Produto | (1) `docs/email/LEIA-ME.md` (tabela de campos, `{{codigo}}`) diz que o código de cliente "entra em uso com a versão 0.8", mas o instalador da 0.7.9 não instala sem código válido: o e-mail de boas-vindas à KR Law precisa levar o código. (2) "Nome do produto como configuração" em `robo/PENDENCIAS.md` e o trecho sobre o nome em `robo/ARQUITETURA.md` (linhas 104 a 106) estão velhos: a tela e o aviso do Windows já leem `marca.json` (`robo/lexsuite/app.py`); a planilha e o e-mail de aviso ainda não. Nada foi alterado | sim (Produto, 08/Nov): LEIA-ME do e-mail diz que o código é obrigatório; PENDENCIAS e ARQUITETURA com o estado do nome |
| 08/Nov | Operação | Arquitetura | `CLAUDE.md` (linhas 1 e 12) e `robo/ARQUITETURA.md` (linha 1) ainda chamam o produto de "JUDICIAL"; a decisão do dono de 08/Nov é RADAR JUDICIAL, da suíte LexSuiteONE, como está em `docs/marca.json`. O `CLAUDE.md` é da Arquitetura; nada foi alterado | não |
| 08/Nov | Produto | Arquitetura | Item 4 de `documentacao/FEEDBACK-TESTE-2026-11-08.md`: o dono quer o e-mail da pessoa já preenchido quando a instalação começa pelo e-mail de boas-vindas. Proposta: guardar na licença (`lex_contas`) o e-mail para quem as boas-vindas foram enviadas e devolvê-lo na conferência do código (`lex-conta`). Pede desenho curto e SQL em arquivo | não |

## Decisões do dono registradas aqui

| Data | Decisão |
|---|---|
| 08/Nov | Nome do produto: RADAR JUDICIAL (suíte LexSuiteONE). Fica como configuração em `docs/marca.json`; pode mudar depois sem mexer em código. |
| 08/Nov | Quadro no repositório em vez de uma quarta conversa orquestradora. Dono por arquivo. Só a Operação publica versão. |
| 08/Nov | Subagentes com modelo por tarefa (`.claude/agents/`): a conversa principal decide e edita; leitura pesada, testes e pesquisa vão para o subagente. |
| 08/Nov | Visita à KR Law: prompts da extensão rodam sozinhos, no Sonnet, na conta do escritório (`docs/VISITA-KR-LAW.md`). |
| 08/Nov | Commits sem rastro de ferramenta de IA: nenhuma linha Co-Authored-By, Claude-Session ou nome de modelo. Histórico antigo fica; some na migração para a organização. |
| 08/Nov | Respostas ao dono em até 10 linhas; detalhe vai para arquivo ou quadro. |
| 08/Nov | Documentos internos saem de `docs/` para `documentacao/` só depois de quinta 12/Nov (Arquitetura faz). Novos já nascem em `documentacao/`. |
| 08/Nov | SQL das licenças: aprovado pelo dono pelo aplicativo, sem leitura. Não é violação. Daqui em diante SQL em arquivo, dono roda após revisar; Arquitetura revisa a segurança do que foi aplicado. |
| 08/Nov | Worker `integracao-resposta`: Operação aplica a correção e testa. |
