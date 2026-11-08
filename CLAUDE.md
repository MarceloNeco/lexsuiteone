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
- Nunca reescreva histórico nem force push sem o dono pedir na hora. Nunca commite `config.json`, `*.db`, `saida/`,
  `diagnostico/`, `chave_privada.txt`.
- O robô é só biblioteca padrão do Python, sem IA no caminho principal, sem contornar captcha, sem dado fictício no
  produto (só em `exemplos/` e testes, marcados como fictícios). Pessoa física nunca sai do robô.
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
- SQL do Supabase nunca roda sem revisão: o dono roda depois de revisar.
- As páginas do produto não fazem nenhum pedido externo: sem fontes de fora, sem rastreador, sem script de terceiros.

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

- Versão em `robo/lexsuite/__init__.py`. Pacote: os mesmos arquivos (40 no download completo, 39 no de atualização, conferido na 0.7.10) em `releases/LexSuiteONE-RADAR.zip`,
  `releases/LexSuiteONE-RADAR-<versão>.zip` e `docs/downloads/LexSuiteONE-RADAR.zip` (o pacote de atualização é
  `LexSuiteONE-RADAR-atualizacao-<versão>.zip`; o botão do site baixa o instalador `Instalar-LexSuiteONE.zip`). Atualize `robo/LEIA-ME.md`,
  `robo/ARQUITETURA.md` e `robo/PENDENCIAS.md` junto.
- Testes: `cd robo && python -m unittest discover -s testes`. A automação do GitHub roda testes, Bandit e Gitleaks.
- Arquivos `.bat` sempre com fim de linha CRLF.
- Nome do produto é configuração, não texto fixo: fica só em `docs/marca.json` (nome exato, nome curto, trecho em latão).
  As páginas do site são escritas em `paginas/` com `{{marca.nome}}`, `{{marca.curto}}` e `{{marca.logo}}`; rode
  `python ferramentas/marca.py` para gerar `docs/`. Nunca edite `docs/index.html` nem `docs/404.html` à mão (a automação
  do GitHub confere). O e-mail de boas-vindas lê a mesma configuração ao ser preenchido.
- A pasta do Drive do dono (LEXSUITE-ONE-ROBO) é cópia de consulta: só atualize quando ele pedir.
