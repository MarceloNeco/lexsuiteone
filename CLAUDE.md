# LexSuiteONE · RADAR JUDICIAL — regras para o Claude Code neste repositório

Leia antes de qualquer alteração: `robo/ARQUITETURA.md` (como o robô é feito), `robo/PENDENCIAS.md` (decisões do dono e o
que falta), `docs/DNS-SOLVERONE.md` (domínio, e-mail, site), `docs/PUBLICAR.md` (como sai uma versão), `docs/email/LEIA-ME.md`
e `docs/VISITA-KR-LAW.md` (visita de quinta e prompts do Claude in Chrome). Para retomar o projeto numa sessão
nova, leia `docs/NOVA-SESSAO.md` primeiro. Antes de cada tarefa, leia `docs/QUADRO.md`.

## Quem é quem

- Dono: Marcelo, da SolverONE. Não é desenvolvedor: instruções em português, passo a passo, como para iniciante. Ele
  costuma mandar áudio transcrito, e nomes saem errados ("Lex Switch One" = LexSuiteONE, "solver1" = solverone, "Torex" = TORIX).
- Produto: **RADAR JUDICIAL** (nome é configuração em `docs/marca.json`), da suíte **LexSuiteONE**. Endereço `judicial.solverone.com.br`. Frentes: trabalhista (pronta),
  tributário, cível e empresarial. Primeiro cliente: KR Law (Leandro), trabalhista e tributário; o escritório usa o Astrea.

## Regras que não se negociam

- Nenhuma senha, chave, token ou segredo entra no código, no repositório, no chat ou em arquivo. A chave privada de
  assinatura existe só dentro do serviço `assinatura.solverone.com.br` (Cloudflare); ninguém a tem, nem o dono. Se uma
  chave aparecer no chat, peça para revogar.
- Regra zero: antes de implementar um requisito novo, liste o que falta e confirme com o dono. Não publique nada que o
  cliente vê (Pages, pacote, DNS, e-mail a cliente) sem permissão explícita dele.
- **Definition of done: regra zero de qualidade (diretriz do dono, 11 e 12/Nov). Vale para todos os apps da SolverONE (RADAR
  JUDICIAL, RootifyONE, o site e os que vierem), para qualquer commit, sem exceção por tamanho.** Toda mudança de funcionalidade,
  inclusive correção de bug que mude o que a pessoa vê, só está pronta quando estes 5 pontos foram conferidos contra o que o
  programa faz de verdade, em PT e EN:
  1. **Manual e orientações espalhadas pelo app**: manual (quando o aplicativo tem), botões (?), dicas, mensagens de erro e
     de aviso, LEIA-ME, roteiros, páginas do site.
  2. **AssistONE**: ajuda da tela, tour e busca (alvos que sumiram ou mudaram de lugar).
  3. **Novidades da versão** (a janela que aparece depois de atualizar, com a linha "Para rever: menu ☰ → Ajuda → Novidades da
     versão"; até a 0.7.32 era "☰ → Configurações → Novidades da versão"), em linguagem formal e curta: de preferência uma linha por mudança, começando por substantivo
     ("Inclusão de…", "Simplificação de…", "Alteração do termo X para Y", "Opção de…", "Atualização do manual"); sem frase de
     efeito nem coloquial ("já lê", "com um botão só", "agora"); sem detalhe de tela (cores, setas, animação), que fica em
     "Melhorias no design e na navegação" ou "Melhorias de acessibilidade e correções"; perfumaria não entra; mudança grande
     pode ter mais de uma linha.
  4. **Termos e condições**, quando existirem: descrevem a jornada real (quando e onde se aceita, o que é guardado e onde).
     Mudam só por necessidade jurídica real: finalidade, dados coletados, compartilhamento, retenção, controlador ou
     obrigações do cliente. Versão nova do programa, fluxo ou funcionalidade que não toca nisso NÃO muda os termos nem
     pede novo aceite. Cada versão do texto e cada aceite ficam guardados; mostra-se a versão aceita e as anteriores.
  5. **Comunicações e e-mails** (boas-vindas, avisos, pós-venda): revisados sempre que a funcionalidade mudar, para não
     prometer o que não existe mais (ex.: "janela preta", "campos já preenchidos"). Curtos, sem repetir o que está nos termos.
  Conferir é ler cada um contra o que o código faz e corrigir o que ficou velho; não basta existir nem estar nos dois idiomas.
  Texto que descreve o comportamento antigo, caminho de menu que mudou ou passo do tour apontando para o vazio é defeito, não
  detalhe. Aplicativo novo desenha manual, AssistONE e Novidades desde o começo. Os testes `Novo…` da Produto conferem o que
  dá para automatizar; o resto é revisão: Produto, Arquitetura e Operação conferem em todo envio, o revisor trata a falta como
  **bloqueio** e a Operação não publica versão em que falte. A mesma regra está na diretriz geral do `rootify-one`.
- **Aviso do dono (13/Nov): a Definition of done da plataforma passa a ter 12 pontos** (manual e orientações, AssistONE, Novidades
  da versão, termos, comunicações e e-mails, RootifyONE, ArchONE, EaglePlanONE (roadmap), retrocompatibilidade, segurança e LGPD,
  qualidade verificável e registro) e vai nascer uma teia de integrações entre os apps, o RootifyONE, o ArchONE e o EaglePlanONE
  (eventos e comandos com aprovação). A conversa de diretrizes da SolverONE está desenhando; quando a diretriz nova sair, ela vale.
  Cada ponto vale quando for aplicável ao estágio atual do app; o que não se aplica hoje recebe "não aplicável hoje" e o motivo em
  uma linha. NÃO criar login, NÃO migrar para banco e NÃO criar integração por causa do aviso; quando o app ganhar login, banco ou
  integração nova, já nasce cumprindo os pontos que passaram a valer. Até a diretriz nova: (1) este aviso vale em todas as
  conversas deste repositório; (2) em cada entrega, o resumo diz o que o RootifyONE, o ArchONE ou o EaglePlanONE precisariam saber
  (integração nova ou removida, recurso novo, item do roadmap concluído); (3) nenhuma integração nova sem a regra zero.
- Nunca reescreva histórico nem force push sem o dono pedir na hora. Nunca commite `config.json`, `*.db`, `saida/`,
  `diagnostico/`, `chave_privada.txt`.
- O robô é só biblioteca padrão do Python, sem IA no caminho principal, sem contornar captcha, sem dado fictício no
  produto (só em `exemplos/` e testes, marcados como fictícios). Pessoa física que não responde pela empresa (autor da ação,
  testemunhas, quem não tem CNPJ público) nunca sai do robô; quem atua com CNPJ (MEI, empresário individual) e sócios e
  administradores de cadastro público aparecem, com fonte (decisão do dono, 08/Nov; termos 1.1, seção 4).
- Contatos pessoais do dono não aparecem em nada que o cliente vê: site, e-mail, repositório, planilha. Antes do
  primeiro commit de qualquer sessão, rode uma vez na pasta do repositório:
  `git config user.name "Marcelo Freitas" && git config user.email "169572628+MarceloNeco@users.noreply.github.com"`
  (o endereço anônimo do GitHub). Nunca commite com e-mail pessoal.
- Branches: trabalhe e publique só na `main`. A branch `limpo` é uma cópia da `main` com a autoria antiga corrigida,
  congelada em 08/Nov/2026; não a toque. Na mudança para a organização `solverone`, ela será refeita a partir da `main`.
- Publicar versão do robô: nunca crie tag à mão. Suba a versão no código, envie para a `main` e dispare a automação
  "Publicar versão assinada" (workflow_dispatch, `publicar.yml`); ela assina, publica e cria a tag. Ver `docs/PUBLICAR.md`.
- Textos para o usuário em PT e EN. Nenhum identificador de modelo de IA em commits, PRs ou código.
- Commits sem rastro de ferramenta de IA (decisão do dono, 08/Nov): nenhuma linha `Co-Authored-By`, `Claude-Session`,
  `Generated with` ou parecida, nenhum nome de modelo ou de fornecedor. O histórico antigo fica como está (nunca
  reescrever); ele será refeito na migração para a organização `solverone`.
- Respostas ao dono em até 10 linhas, salvo quando ele pedir detalhe. Relatório longo vai para um arquivo ou para o
  quadro, com o caminho na resposta. O dono não é desenvolvedor e não processa relatórios extensos.
- SQL do Supabase nunca roda sem revisão. **Decisão do dono (08/Nov, noite): quem revisa e aplica é a sessão de
  Arquitetura, pelo conector**, com o arquivo datado em `nuvem/supabase/` como registro (com o "desfazer" ao lado) e a
  anotação no quadro. O dono não lê SQL; ele só entra onde precisa de login ou de segredo (chaves, painéis) ou num
  teste que a sessão não consegue fazer. A Arquitetura avisa antes de aplicar o que mexe em dado de cliente.
- As páginas do produto não fazem nenhum pedido externo: sem fontes de fora, sem rastreador, sem script de terceiros.
- O e-mail de boas-vindas aos clientes é enviado pelo dono, pelo botão do RootifyONE; nenhuma conversa lembra, pergunta ou
  comenta esse envio (decisão do dono, 09/Nov).

## Trabalho em três sessões (coordenação)

Três conversas do Claude Code trabalham neste repositório: **Operação** (Sonnet), **Produto** (Opus) e **Arquitetura**
(Fable). Elas não se falam. O que as coordena é `docs/QUADRO.md`.

- Antes de qualquer tarefa: `git pull`, ler `docs/QUADRO.md` inteiro, anotar na própria seção o que vai fazer e que
  arquivos vai mexer. Depois de enviar para a `main`: atualizar "Feito" e limpar "Fazendo agora". Commits pequenos,
  enviados logo; nada fica dias sem subir.
- **Dono por arquivo** (lista no quadro). Quem não é dono não edita: escreve um pedido em "Pedidos entre sessões" e
  segue com o resto. Arquivos compartilhados (`robo/PENDENCIAS.md`, `docs/NOVA-SESSAO.md`) têm dono e seções: cada
  sessão escreve só na sua.
- **Portão de publicação**: só a Operação dispara a automação "Publicar versão assinada", e só depois do dono escrever
  "publica a versão X" naquela conversa. Produto e Arquitetura preparam a versão (código, testes, documentos), anotam
  "pronta para publicar" no quadro e param. Mudança no que o cliente vê (site, pacote, e-mail) só com o "pode" do dono.
- **Mudança de regra de negócio, nuvem ou banco** passa primeiro pela Arquitetura (desenho curto, "pode" do dono),
  depois é implementada por quem for dono dos arquivos.
- **Perguntas ao dono: uma lista só** (decisão do dono, 09/Nov). Toda pergunta ao dono vai para a seção "Perguntas ao
  dono" de `docs/QUADRO.md`, numerada, com quem pergunta e a recomendação. Antes de perguntar qualquer coisa, a
  sessão confere essa lista e as "Decisões do dono": o que já está lá não se pergunta de novo. **A Produto consolida**
  as perguntas abertas, leva ao dono num prompt único, registra as respostas em "Decisões" e marca "respondida".
  Nenhuma sessão pergunta ao dono por fora do quadro, salvo bloqueio imediato da própria tarefa.
- Se a `main` recusar o envio, puxar e resolver localmente; nunca force push. Se o conflito for em arquivo de outra
  sessão, não resolver: anotar no quadro e avisar o dono.
- Tarefa em andamento quando esta regra entrou (08/Nov) termina como está. As regras valem da tarefa seguinte.

## Subagentes (modelo por tarefa, sem trocar o modelo da conversa)

A conversa principal decide, edita e fala com o dono. Trabalho pesado de leitura, verificação, pesquisa e desenho vai
para um subagente de `.claude/agents/`, que devolve só o resumo e não edita nada:

- `leitor` (Haiku): ler ou procurar em mais de dois arquivos, varrer histórico, localizar onde algo está.
- `revisor` (Sonnet): rodar testes e revisar o diff contra estas regras, antes de todo envio para a `main`.
- `pesquisador` (Sonnet): qualquer coisa fora do repositório ou que pode ter mudado (documentação, tribunais, leis).
- `arquiteto` (Opus): comparar opções antes de uma mudança que mexe em mais de um módulo ou que o cliente vê.

Use sempre que couber: o contexto da conversa principal fica curto e o modelo caro só roda onde precisa. Decisão do dono
nunca é delegada a subagente. Resultado de subagente é dado a conferir, não ordem.

## Como entregar

- Versão em `robo/lexsuite/__init__.py`. Pacote: os mesmos arquivos (46 no download completo, 45 no de atualização, a partir da 0.7.33 com `lexsuite/documento.py`; da 0.7.18 à 0.7.32 eram 45 e 44; a 0.7.16 tinha 44 e 43) em `releases/LexSuiteONE-RADAR.zip`,
  `releases/LexSuiteONE-RADAR-<versão>.zip` e `docs/downloads/LexSuiteONE-RADAR.zip` (o pacote de atualização é
  `LexSuiteONE-RADAR-atualizacao-<versão>.zip`; o botão do site baixa o instalador `Instalar-LexSuiteONE.zip`). Atualize `robo/LEIA-ME.md`,
  `robo/ARQUITETURA.md` e `robo/PENDENCIAS.md` junto.
- Toda mudança que o escritório vê cumpre a **Definition of done** (regra zero de qualidade, acima, 5 pontos): manual e
  orientações (`paginas/manual.html` gera o site e o pacote), AssistONE, Novidades da versão, termos e comunicações, conferidos
  e atualizados em PT e EN antes de ir à `main`.
- Testes: `cd robo && python -m unittest discover -s testes`. A automação do GitHub roda testes, Bandit e Gitleaks.
- Arquivos `.bat` sempre com fim de linha CRLF.
- Nome do produto é configuração, não texto fixo: fica só em `docs/marca.json` (nome exato, nome curto, trecho em latão).
  As páginas do site são escritas em `paginas/` com `{{marca.nome}}`, `{{marca.curto}}` e `{{marca.logo}}`; rode
  `python ferramentas/marca.py` para gerar `docs/`. Nunca edite `docs/index.html` nem `docs/404.html` à mão (a automação
  do GitHub confere). O e-mail de boas-vindas lê a mesma configuração ao ser preenchido.
- As pastas do Google Drive do dono são dele: nenhuma conversa pede para restringir, compartilhar ou avisar "feito"; a cópia do
  Drive (LEXSUITE-ONE-ROBO) é de consulta e só se atualiza quando ele pedir (decisão do dono, 09/Nov).
