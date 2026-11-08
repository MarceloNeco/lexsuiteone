# Retomar o projeto numa sessão nova (estado em 08/Nov/2026, noite)

Este arquivo existe para uma conversa nova do Claude Code começar sem reler o histórico. Leia junto `CLAUDE.md`,
`robo/PENDENCIAS.md`, `docs/DNS-SOLVERONE.md`, `docs/PUBLICAR.md` e `docs/VISITA-KR-LAW.md`. Confirme o estado por fora antes de agir: nada aqui substitui conferir. **Antes de qualquer tarefa, rode `git pull` e leia `docs/QUADRO.md`**: é onde as três sessões anotam o que estão fazendo.

## O que já existe e funciona

- Robô v0.7.10 (`robo/`), produto chamado **RADAR JUDICIAL** (nome é configuração em `docs/marca.json`), 95 testes verdes,
  pacote em `releases/` e `docs/downloads/`. Tela local em 127.0.0.1, planilha `LexSuiteONE.xlsx` no Drive do escritório,
  atualização assinada (chave só na nuvem), manual personalizado, revisão de segurança (risco baixo). Na 0.7.9: horários
  de leitura escolhidos pelo escritório e leitura perdida compensada. Na 0.7.10 (publicada em 08/Nov, 16:39 UTC): domingo e
  segunda leem a sexta, assistente novo de configuração (planilha, função, tribunais, compartilhamento), tela em janela
  própria, nomes inteiros em Tribunais e registro ao vivo na janela preta.
- Site https://judicial.solverone.com.br **no ar** (GitHub Pages, pasta `docs/`, HTTPS forçado). É gerado de `paginas/`
  por `python ferramentas/marca.py`: nunca edite `docs/index.html` nem `docs/404.html` à mão. Tem página inicial PT/EN
  com o carrossel "Como funciona" (quatro passos, passa com o dedo no celular; falta o dono confirmar num iPhone de
  verdade), manual, 404, requisito de Windows e "Mac sob consulta". Download do instalador em
  `/downloads/Instalar-LexSuiteONE.zip` (pacote completo em `/downloads/LexSuiteONE-RADAR.zip`), atualização assinada em
  `/atualizacao/`.
- **Conta e licença por escritório (base da 0.8, construída pela Produto em 08/Nov):** código de cliente `LEX-XXXX-XXXX`,
  licença na nuvem, cadastro de quem usa e avisos de erro técnico para a SolverONE. O instalador pede e confere o código
  antes de baixar. Detalhes e ressalvas na seção "Estado da nuvem" abaixo.
- Domínio `solverone.com.br` no Cloudflare (DNS + DNSSEC), e-mail de recebimento pelo Cloudflare Email Routing
  (`contato@`, `judicial@`, `admin@`, `privacidade@`, `suporte@`, `ceo@` encaminham; `integracao@` responde sozinho que é
  caixa de sistemas). Envio pelo Resend (`nao-responda@`). Detalhes em `docs/DNS-SOLVERONE.md`. Em 08/Nov os quatro
  endereços `judicial@`, `admin@`, `privacidade@` e `suporte@` foram testados e recebem.
- Assinatura das versões na nuvem: serviço `assinatura.solverone.com.br` (Cloudflare Worker); a automação `publicar.yml`
  assina e publica. Ninguém tem a chave privada: nem o dono, nem o PC dele. Roteiro em `docs/PUBLICAR.md`.
- E-mail de boas-vindas (`docs/email/`, lê o nome de `docs/marca.json` ao ser preenchido), remetente
  `LexSuiteONE <nao-responda@solverone.com.br>` pelo Resend, domínio já verificado. Teste entregue ao dono. Falta só o
  e-mail corporativo do Leandro para o envio real.
- Repositório `MarceloNeco/lexsuiteone` (público, MIT, CI com testes, Bandit, Gitleaks, Dependabot, ações fixadas por SHA,
  automação de publicação assinada). Os 12 primeiros commits da `main` têm o e-mail pessoal do dono como autor; a branch
  `limpo` é a mesma história com autoria anônima, congelada em 08/Nov/2026. **Trabalhe só na `main`.** Na mudança para a
  organização `solverone` (depois de 12/Nov), `limpo` será refeita com os commits novos da `main` e passará a ser a `main`
  do repositório novo. Decisão do dono: o piloto do Leandro sai do repositório pessoal mesmo.
- Documentos de referência também na pasta do Drive do dono (cópia de consulta; o GitHub é a fonte). A cópia do Drive está
  desatualizada (programa 0.7.1); atualizá-la espera o dono fechar o link aberto da pasta-mãe (ver o quadro).

## Decisões do dono que valem

- Nome (08/Nov): **RADAR JUDICIAL** é o produto, da suíte LexSuiteONE ("IA" em latão). É configuração em `docs/marca.json`
  e pode mudar sem mexer em código. Endereço `judicial.solverone.com.br`. A tela e o aviso do Windows já leem o nome de
  `marca.json` (`robo/lexsuite/app.py`); a planilha e o e-mail de aviso ainda não (ver "Nome do produto" em
  `robo/PENDENCIAS.md`, que está desatualizado nesse ponto).
- Frentes nesta ordem: trabalhista (existe), tributário, cível e empresarial.
- Cópia HTML estática no Drive fica como reserva; o caminho principal é o sistema (tela local hoje; site na 0.8).
- 0.8: o robô manda a lista do dia para a nuvem da SolverONE (Supabase) e o site mostra, com login por link no e-mail e
  código de cliente `LEX-XXXX-XXXX`. Desenho detalhado em `robo/PENDENCIAS.md`; o desenho próprio
  (`docs/DESENHO-0.8.md`) ainda não existe e a Arquitetura o escreve em cima do que já está no ar.
- Nada de contato pessoal do dono em nada que o cliente vê. Caixas: `judicial@` (contato de toda a suíte LexSuiteONE; no
  futuro `moneytrio@` etc. para outras suítes), `contato@` (genérico), `integracao@` (só sistemas: compartilhar Drive;
  responde sozinho, sem citar outro e-mail por ora), `nao-responda@` (só envia). `integracao@` é também uma Conta Google
  sem Gmail. ImprovMX fica de reserva até ser cancelado (~2 semanas).
- Repositório segue no GitHub pessoal até depois da visita; migração para a organização `solverone` sem impacto para o
  cliente (tudo que ele vê aponta para `judicial.solverone.com.br`). Roteiro em `robo/PENDENCIAS.md`.
- Instalação no cliente (KR Law) na quinta-feira 12/Nov, na casa do Leandro, pelo dono. O pacote de quinta é a última
  versão publicada (0.7.10 em 08/Nov). Roteiro da visita e quatro prompts (PJe, ficha de canais da empresa, Astrea, e-SAJ)
  em `docs/VISITA-KR-LAW.md`: rodam sozinhos, no Sonnet, na conta do escritório; param em login, token, certificado ou
  captcha e escrevem BLOQUEIO; o relatório final volta à sessão de Produto.
- Publicação de versão (08/Nov): só a Operação publica, e só depois do dono escrever "publica a versão X" na conversa da
  Operação. Produto e Arquitetura preparam a versão e anotam "pronta para publicar" no quadro.
- Envio de e-mail: o Resend serve mais de um projeto do dono pelo mesmo domínio; separar por subdomínio fica para depois
  (nota em `robo/PENDENCIAS.md`).

## O que só o dono faz (sem conector)

Registro.br, GitHub (organização, transferência, Pages, configurações de conta), ImprovMX (cancelar), Conta Google do
`integracao@`, DIAGNOSTICO.bat e testes no PC dele, visita à KR Law, **compartilhamento do Drive** (o conector não
altera: o link aberto da pasta-mãe "Estudos de Casos Juridicos" só o dono fecha, ou autoriza mover só a pasta do
projeto), conferir o carrossel num iPhone de verdade. Para esses passos ele usa a extensão Claude in Chrome (Sonnet para o
rotineiro): escreva o prompt completo, sem campo em aberto, dizendo site, modelo e o que confirmar.

## Estado do Cloudflare (08/Nov, noite)

Zona `solverone.com.br` ativa no Cloudflare, DNSSEC ligado nos dois lados (Registro.br aponta para os servidores
`harlee`/`lennon` com o DS keytag 2371). Email Routing ativo, Worker `integracao-resposta` em `integracao@`, Worker
`assinatura-lexsuite` em `assinatura.solverone.com.br`. Tudo gerido pelo conector "Cloudflare" (API). Detalhes em
`docs/DNS-SOLVERONE.md`.

Worker `integracao-resposta`: encaminha tudo para a caixa do dono com o cabeçalho `X-Resposta` e responde uma vez, só a
pessoa. Quem escreve por um serviço de envio (Resend, Amazon SES) é só encaminhado, sem resposta: antes, a resposta ia
para o endereço de retorno do serviço e o Resend marcava o e-mail de origem como "bounced". Correção aplicada e testada
em 08/Nov (log do Email Routing: serviço de envio encaminhado sem resposta; Gmail encaminhado e respondido). A versão
anterior fica guardada na Cloudflare para voltar.

## Estado da nuvem (Supabase `solverone-app`, conferido em 08/Nov)

- Tabelas `lex_contas` (licença por escritório; 2 linhas), `lex_usuarios`, `lex_instalacoes`, `lex_registros` (erros
  técnicos sem dado pessoal) e `lex_eventos` (histórico por licença), todas com RLS. Migrações aplicadas em 08/Nov:
  `lex_licencas`, `lex_licencas_acesso_servico`, `lex_registros_erros`, `spatial_ref_sys_somente_leitura`,
  `lex_pessoas_ativas_eventos` e `lex_admin_rootify`.
- Função `lex-conta` (Edge Function) ativa, versão 3, sem verificação de JWT (o instalador a chama antes de ter conta);
  grava `lex_registros` com limite de 30 por hora.
- Onde está no repositório: `nuvem/supabase/lex-licencas.sql`, `nuvem/supabase/lex-admin.sql`,
  `nuvem/supabase/functions/lex-conta/index.ts`, `robo/lexsuite/conta.py`, `instalador/INSTALAR.bat`.
- **SQL já aplicado:** as migrações acima foram aplicadas em 08/Nov pela Produto, com aprovação do dono pelo aplicativo e
  sem leitura do texto (não é violação a registrar; ver "Fatos" no quadro). `robo/PENDENCIAS.md` (seção 0.7.7, item "SQL
  para o dono revisar e rodar") ainda diz o contrário. Daqui em diante, SQL vai para arquivo, anotado no quadro, e o dono
  roda depois de revisar. A segurança do que foi aplicado (função sem JWT, limite de chamadas, tabela do sistema sem RLS)
  é pendência da Arquitetura. Esta sessão só leu a nuvem.
- Ainda não existe: `lex_batimentos`, login por e-mail e o aviso ao terminar a leitura (0.8).

## O que falta, na ordem (estado em 08/Nov à noite)

A infraestrutura está no ar. Falta:

1. **E-mail de boas-vindas ao Leandro** (sessão de operação), pelo Resend. A licença da KR Law já existe e está ativa
   (a Produto a criou). O instalador não instala sem o código de cliente, então o e-mail leva o código. O e-mail já está
   preenchido, fora do repositório; o código nunca entra no repositório, no quadro nem em conversa (se o arquivo
   temporário se perder, refazer com `python docs/email/preencher.py --nome "Leandro" --codigo <código> ...`, lendo o
   código no RootifyONE, "Licenças do RADAR", ou no banco, só leitura). Um teste com a licença de teste do dono foi
   enviado em 08/Nov. Falta o endereço corporativo do Leandro (até quarta, 11/Nov) e o "pode" do dono para enviar.
2. **Drive**: o dono fecha o link aberto da pasta-mãe (ou autoriza mover só a pasta do projeto); depois a Operação
   atualiza a pasta "LEXSUITE-ONE-ROBO" para a versão atual e coloca as cópias de referência.
3. **Antes de quinta, no PC do dono**: ensaio da instalação com a segunda conta Google, `DIAGNOSTICO.bat`, rodada real
   nos 24 TRTs, e testar o instalador no Windows (falta, ver `robo/PENDENCIAS.md`). Roteiro em `robo/ROTEIRO-INSTALACAO.md`.
4. **Quinta (12/Nov)**: instalação na KR Law e os prompts de `docs/VISITA-KR-LAW.md` (relatórios vão para a sessão de
   Produto).
5. **Documentos internos abertos no site** (pedido à Arquitetura no quadro): os `.md` de `docs/` respondem em
   `judicial.solverone.com.br/NOME.md`. O dono decide se saem de `docs/`.
6. **Depois de quinta**: organização `solverone` no GitHub (refazer `limpo` como nova `main`, Pages, CNAME para
   `solverone.github.io`), triagem de e-mail por Worker, calibração da regra com o diagnóstico, desenho da 0.8 e da
   frente tributária, ficha de canais da empresa, cancelar ImprovMX.

## Sessões (três conversas do Claude Code, coordenadas por `docs/QUADRO.md`)

- **Operação** (Sonnet; repositório `lexsuiteone`): DNS, e-mails (boas-vindas, Resend), Drive, Cloudflare, documentos
  que lhe pertencem (`NOVA-SESSAO.md`, `DNS-SOLVERONE.md`, `PUBLICAR.md`), publicar versão pela automação, ajustes
  pequenos. Não muda regra de negócio.
- **Produto** (Opus; repositório `lexsuiteone`): site e manual (feedbacks do dono sobre a página vão aqui), textos PT/EN,
  frente tributária, relatórios da visita virando desenho de integração, correções do robô. Não mexe no pacote de
  quinta sem o dono aprovar. Mudança de regra de negócio, nuvem ou banco passa antes pela Arquitetura.
- **Arquitetura** (Fable; `lexsuiteone`, `rootify-one`, `solverone-app`, `solverone-dados`): desenho da 0.8 (conta na
  nuvem, lista no site, código de cliente, SQL para o dono revisar), migração para a organização `solverone`, integração
  com o RootifyONE, segurança, e as regras do repositório (`CLAUDE.md`, `.claude/`). Desenha a 0.8 em cima do que a
  Produto já construiu (seção "Estado da nuvem").
- As sessões não se falam. Cada arquivo tem uma sessão dona; quem não é dono escreve um pedido em "Pedidos entre
  sessões" do quadro. Subagentes por tarefa ficam em `.claude/agents/` (leitor, revisor, pesquisador, arquiteto): uma
  conversa já aberta antes de eles existirem não os enxerga e usa um agente comum com a mesma instrução.
- A conversa que montou tudo isso até 08/Nov foi renomeada "old" e não recebe mais tarefas.

## Prompt sugerido para abrir uma sessão nova

> Você está retomando o projeto LexSuiteONE · RADAR JUDICIAL, da SolverONE, como a sessão de [Operação | Produto | Arquitetura].
> Rode `git pull`, leia `docs/QUADRO.md`, depois `CLAUDE.md` e `docs/NOVA-SESSAO.md` deste repositório e siga o que está
> lá. Confira o estado real por fora (repositório, DNS, Pages, Resend) antes de agir. Depois me diga, em até dez linhas,
> o que entendeu do estado atual e qual é o primeiro passo da sua sessão. O que só eu posso fazer, me guie passo a
> passo, em português, como para iniciante, com prompts completos para a extensão Claude in Chrome quando for o caso.
