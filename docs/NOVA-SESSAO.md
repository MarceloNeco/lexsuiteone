# Retomar o projeto numa sessão nova (estado em 09/Nov/2026, noite)

Este arquivo existe para uma conversa nova do Claude Code começar sem reler o histórico. Leia junto `CLAUDE.md`,
`robo/PENDENCIAS.md`, `docs/DNS-SOLVERONE.md`, `docs/PUBLICAR.md` e `docs/VISITA-KR-LAW.md`. Confirme o estado por fora antes de agir: nada aqui substitui conferir. **Antes de qualquer tarefa, rode `git pull` e leia `docs/QUADRO.md`**: é onde as três sessões anotam o que estão fazendo.

## O que já existe e funciona

- Robô v0.7.38 (`robo/`, publicada em 13/Nov), produto chamado **RADAR JUDICIAL** (nome é configuração em `docs/marca.json`), 365 testes verdes,
  pacote em `releases/` e `docs/downloads/`. Tela local em 127.0.0.1, planilha `LexSuiteONE.xlsx` no Drive do escritório,
  atualização assinada (chave só na nuvem), manual personalizado, revisão de segurança (risco baixo). Na 0.7.9: horários
  de leitura escolhidos pelo escritório e leitura perdida compensada. Na 0.7.10 (publicada em 08/Nov, 16:39 UTC): domingo e
  segunda leem a sexta, assistente novo de configuração (planilha, função, tribunais, compartilhamento), tela em janela
  própria, nomes inteiros em Tribunais e registro ao vivo na janela preta. A 0.7.11 não foi publicada (decisão do dono):
  a 0.7.12 (publicada em 08/Nov, 20:43 UTC) contém tudo dela (dias com Diário, aviso de versão nova com reinício sozinho,
  uma tela só, Configuração na engrenagem, barra de progresso, CNPJ ligado ao nome da empresa, lista de 10 em 10 com
  filtros e cartões, aviso de planilha aberta), mais o Painel com números e gráficos e a planilha nova (cabeçalho
  azul-marinho, filtro, R$, destaque acima do mínimo e aba Como usar). A 0.7.13 (publicada em 09/Nov, 04:39 UTC) corrige
  o erro das 00h às 3h: o Diário de hoje ainda não liberado vira aviso e a leitura segue com os dias anteriores, cada
  tribunal à parte, mensagens claras em PT e EN, "Histórico de leituras" na tela e aba Log visível. A 0.7.14 (publicada em
  09/Nov, 13:01 UTC) é o pacote de tela e planilha: menu ☰, abas Painel · Lista · Arquivo · Histórico, situação no banco
  com lote e Desfazer, contatos, planilha com aviso e só para leitura, retorno de totais à SolverONE, aceite dos termos no
  programa e no instalador (só vale com `exigir_aceite` ligado na licença) e leitura agendada visível. A 0.7.15 (publicada
  em 09/Nov, 14:55 UTC) traz o botão Interromper (para num ponto seguro, também na leitura agendada), o aviso da leitura
  de horário perdido e a "próxima leitura" que se atualiza sozinha, mais os textos corrigidos sobre o que vai à
  SolverONE e o que fica guardado. A 0.7.16 (publicada em 09/Nov, 16:11 UTC) traz uma planilha por frente na mesma pasta
  (a `LexSuiteONE.xlsx` antiga vira `LexSuiteONE - Trabalhista.xlsx`, com as abas Preferências e Exclusões preservadas), a pasta
  `Cópias de segurança`, aviso e limite de armazenamento, regra de ação nova mais estreita e a Configuração reorganizada;
  o escritório não precisa mais compartilhar a pasta com a SolverONE. A 0.7.18 (publicada em 09/Nov, 19:11 UTC; a 0.7.17 não
  foi publicada e está dentro dela) traz filtros com várias opções, turmas de 2º grau fora da lista (ação já trabalhada fica),
  estatísticas dos meses anteriores no Painel (30 Diários por vez, só totais e, só no computador, o número dos processos já
  contados), engrenagem e perfil em janela, cópia do banco antes da reclassificação única e textos corrigidos sobre o que
  vai à SolverONE. A 0.7.20 (publicada em 09/Nov, 22:08 UTC; a 0.7.19 não foi publicada e está dentro dela) traz o menu em
  gaveta, a lupa de busca, o AssistONE embutido na tela (sem IA e sem nenhum pedido externo; liga e desliga na Configuração e
  também pela administração, no campo `recursos` da conferência da licença), as pastas explicadas com teste, a última leitura
  depois de reiniciar, o Interromper em vermelho, o link do aceite por `#` e o cabeçalho de proteção (CSP) nas páginas locais.
  A 0.7.22 (publicada em 10/Nov, 01:53 UTC; a 0.7.21 não foi publicada e está dentro dela) traz as pastas das planilhas em duas
  opções (com atalho para OneDrive e Google Drive), a planilha de consulta marcada **somente leitura** entre uma gravação e outra
  ("Editar Preferências e Exclusões" libera), o aviso por versão, o critério de "Ler o Diário agora", a validade da licença, o
  menu "Área logada" ("Trazer dados da área logada") e o AssistONE 1.1.1 (tour com balão que desliza). Sem mudança na regra de licença.
  A 0.7.23 (publicada em 10/Nov) acerta textos (sem Google Drive como padrão, falta de permissão, tour com "Área logada"), mostra o motivo
  de licença bloqueada em inglês quando a tela está em inglês, limita números ruins do `config.json` e deixa o nome do escritório sempre
  válido na cópia de trabalho. Sem mudança na regra de licença.
  A 0.7.24 (publicada em 10/Nov) traz o aviso de somente leitura também no link da última leitura, a planilha marcada ao ser aberta, a lupa
  com as partes da Configuração, o critério de "Ler o Diário agora" embaixo do botão e os nomes das opções de pasta. Sem mudança na regra de licença.
  A 0.7.25 (publicada em 10/Nov) só marca a planilha como somente leitura ao abri-la se ninguém a tem aberta para editar (senão avisa), limita
  números absurdos do `config.json` e do `/rodar`, e acerta foco, rolagem e textos da lupa e da Configuração. Sem mudança na regra de licença.
  A 0.7.26 (publicada em 10/Nov) faz a gravação da página e da planilha ao fim de toda leitura aguentar número absurdo no `config.json`, deixa o
  aviso de planilha em uso honesto (e na tela até a próxima ação), e a lupa da página offline só oferece o que funciona lá. Sem mudança na regra de licença.
  A 0.7.27 (publicada em 10/Nov) faz `Infinity` e `NaN` escritos à mão no `config.json` não quebrarem a tela, deixa um só aviso de planilha em uso
  (honesto também sem Excel) e a lupa da página offline só com Painel e Lista. Sem mudança na regra de licença.
  A 0.7.28 (publicada em 10/Nov à noite; a primeira revisão barrou um risco de apagar exclusões, corrigido) traz as "Regras do escritório" editadas na
  tela (Configuração): o programa grava as abas Preferências e Exclusões da planilha trabalhista, só se a tela leu a planilha e ela não mudou desde
  então, e com cópia de segurança "antes de salvar regras"; datas com o mês em letras (10/NOV/2026), filtros salvos e lembrados, ✕ e Cancelar em toda
  janela e o aviso do segundo clique no atalho. Sem mudança na regra de licença.
  A 0.7.29 (publicada em 11/Nov; a primeira revisão barrou um "Encerrar o RADAR" que podia encerrar processo alheio, corrigido) tira a janela preta:
  o atalho e a leitura automática usam `pythonw.exe` (sem console), o que ia para a janela vai para `saida/registro.txt` (Configuração → Ver registro),
  erro antes de abrir vira caixa do Windows, o `DIAGNOSTICO.bat` ganha "Encerrar o RADAR" e o `ABRIR.bat --ver` abre com janela (suporte); a janela
  fechada no X reabre pelo atalho; Painel com período e barras ou pizza, meses com letras e selo de licença. Sem mudança na regra de licença.
  A 0.7.30 (publicada em 11/Nov; a primeira revisão barrou 2 defeitos de tela, menu ☰ ilegível no modo escuro e rolagem lateral no celular com "Mais filtros", corrigidos) traz a tela em blocos (leitura, filtros fixos no alto, ordenação), a "Data do processo" pela data em que saiu no Diário ("último dia útil", pulando fim de semana e feriado, ou 3 a 90 dias), o Painel com período lembrado, botões por tribunal, barras e pizza, o modo escuro (Perfil: Igual ao sistema, Claro ou Escuro), impressão no claro, o selo de licença com o estado, a faixa de versão nova com a tela aberta (a cada 30 minutos, só pela rota local) e a rolagem da página de trás travada com janela aberta; o Esc fecha uma camada por vez. Sem mudança na regra de licença. Defeitos conhecidos da 0.7.30 (a 0.7.31 corrigiu o primeiro em parte): os botões da faixa de leitura iam para uma segunda linha; com o Perfil e a busca geral abertos, um Esc fecha as duas (continua).
  A 0.7.31 (publicada em 11/Nov, correções do teste do dono): faixa e janela do aceite curtas, código travado e mascarado quando a SolverONE o reconhece (editável se for inválido, desconhecido ou sem resposta), Termos e Sazonalidade com um botão, "Publicado no Diário", gráfico Situação, Novidades da versão (uma vez por versão), leitura automática desligável (tirar o último horário pergunta e remove a tarefa do Windows; a tela inicial avisa), Configuração e Perfil em janela, manual genérico com ícone embutido. Sem mudança na regra de licença. Pergunta aberta ao dono (nº 16 do quadro): as estatísticas da Sazonalidade devem respeitar a licença e o aceite? O instalador não mudou (hash `d468710485a1125a…`).
  A 0.7.32 (publicada em 12/Nov, madrugada; as três primeiras revisões barraram, a quarta liberou): leitura automática por dia da semana (Dom a Sáb; instalação nova começa de segunda a sexta, config antigo com horários e sem dias continua "todos"; nenhum dia desliga a leitura), Configuração reorganizada (A lista, Onde ficam as planilhas, Leitura, Tela, Licença e termos, Sobre este computador) com o menu ☰ "Configurações" na mesma ordem, "Regras do escritório" virou "Critérios da lista", "Trocar licença" (confere o código novo antes de trocar; a recusa não grava nada), gráficos do Painel interativos (filtros próprios, legenda que liga e desliga, "Mostrar todos", "Ver na lista", cores), lupa e AssistONE com as novidades, e o e-mail de boas-vindas avisa que o instalador pede o código. Regra de licença e texto dos termos sem mudança. O dono respondeu a pergunta 16 (11/Nov): as estatísticas da Sazonalidade ficam abertas por enquanto. O instalador não mudou (hash `d468710485a1125a…`). Ressalvas abertas para a 0.7.33 nos pedidos "Ressalvas da revisão da 0.7.32" (Produto) e "Termos e aceite: achados da revisão da 0.7.32" (Arquitetura).
  A 0.7.33 (publicada em 12/Nov, manhã; a primeira revisão barrou com 13 bloqueios, a segunda liberou): critérios da lista e empresas excluídas POR PESSOA, NESTE COMPUTADOR e POR ÁREA (`criterios.json` ao lado do `config.json`, com `.anterior`), migração única das abas Preferências e Exclusões da planilha (cada computador lê a planilha viva ou a cópia "LexSuiteONE - <Frente> - antes da 0.7.33.xlsx" em Cópias de segurança, e só grava depois de ler as 4 frentes), decisão do dono: o que a 0.7.32 aplicava a toda a lista passa a valer em CADA área; planilha compartilhada completa (90 dias e 60 mil linhas fixos), sem as abas Preferências e Exclusões, com a aba só de leitura "Critérios desta leitura"; CNPJ alfanumérico (`lexsuite/documento.py`, novo: 46 arquivos no download completo e 45 na atualização); Sazonalidade lê a fila inteira em lotes com barra, Pausar e Continuar à noite (a leitura da noite termina a fila, para às 07h ou depois de 3 h); Painel sem a busca e com o filtro ligado dentro de "Mais filtros"; menu ☰ Configurações e grupo Ajuda; um Salvar só. **O chamado pelo AssistONE está implementado e ESCONDIDO** (decisão do dono, 12/Nov; chave `app.CHAMADO_LIGADO = False`; `POST /chamado` devolve 403): o escritório não consegue abrir chamado; antes de ligar (0.7.34) a Arquitetura escreve os termos 1.1 (material, com novo aceite). Regra de licença e texto dos termos 1.0 sem mudança. O instalador não mudou (hash `d468710485a1125a…`). Ressalvas abertas para a 0.7.34 no pedido "Ressalvas da segunda revisão da 0.7.33" (Produto), a primeira delas a frota mista de três computadores.
  A 0.7.35 (publicada em 12/Nov, tarde, a tempo da visita à KR Law; inclui a 0.7.34, que não saiu sozinha; a primeira revisão da 0.7.35 barrou com 4 bloqueios, a segunda liberou): o programa reconhece o aceite dos termos sozinho (rota local `POST /conta/conferir`; a tela confere ao voltar para a janela, ao abrir com o aceite pendente, a cada 15 s por até 10 min depois de abrir a página de aceite e antes de "Ler o Diário agora"; botão "Já aceitei"; sem internet nada muda e a tela diz "Sem conexão…"); o SQLite espera até 30 s em vez de "database is locked"; "Conferir agora" em Licença e termos; "Trocar licença" com o mesmo código confere pela rota; tela de abertura; "Abrir a pasta no Windows"; "Continuar à noite" com a busca parada; faixa da leitura compacta; mensagem ao encerrar; sinal das ações antigas pelo texto guardado (`radar.sinal_guardado`: as "listas de distribuição" são reconhecidas pelo texto, com o limite conhecido de uma ação nova que cite "processo distribuído"); página de aceite com a dica no alto e a caixa travada que rola o texto (o texto jurídico dos termos 1.0 não mudou, mesmo sha256); e-mail de boas-vindas mais curto. O chamado segue implementado e ESCONDIDO. O instalador não mudou (hash `d468710485a1125a…`). Ressalvas abertas para a 0.7.36 no pedido "Ressalvas da segunda revisão da 0.7.35" (Produto), a primeira delas "Conferir agora" com leitura em andamento; e o item (10) da Arquitetura (jornada da página de aceite). Depois da visita à KR Law vem a iniciativa de staging e CI/CD (`documentacao/PROMPT-STAGING-CICD-2026-11-12.md` e o desenho `DESENHO-STAGING-RADAR-2026-11-12.md`): a automação "Publicar versão assinada" ganhará o destino staging e a promoção para produção; até lá nada muda no processo da Operação.
  **Falta o teste no Windows (só o dono pode fazer): ver "Preciso do dono" no quadro.**
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
  `LexSuiteONE <nao-responda@solverone.com.br>` pelo Resend, domínio já verificado. Teste entregue ao dono.
- Repositório `MarceloNeco/lexsuiteone` (público, MIT, CI com testes, Bandit, Gitleaks, Dependabot, ações fixadas por SHA,
  automação de publicação assinada). Os 12 primeiros commits da `main` têm o e-mail pessoal do dono como autor; a branch
  `limpo` é a mesma história com autoria anônima, congelada em 08/Nov/2026. **Trabalhe só na `main`.** Na mudança para a
  organização `solverone` (depois de 12/Nov), `limpo` será refeita com os commits novos da `main` e passará a ser a `main`
  do repositório novo. Decisão do dono: o piloto do Leandro sai do repositório pessoal mesmo.
- Documentos de referência também na pasta do Drive do dono (cópia de consulta; o GitHub é a fonte). A cópia do Drive só se
  atualiza quando o dono pedir (decisão de 09/Nov noite, em `docs/QUADRO.md`).

## Decisões do dono que valem

- **Definition of done, regra zero de qualidade (11/Nov)**: toda mudança de feature, em qualquer aplicativo da SolverONE, só está pronta com manual (quando existe), AssistONE e Novidades da versão conferidos e atualizados, em PT e EN; lacuna é bloqueio e a Operação não publica (portão em `docs/PUBLICAR.md`). A redação da regra é da Arquitetura, no `CLAUDE.md` (o dono passou a regra a ela também).
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
  futuro `moneytrio@` etc. para outras suítes), `contato@` (genérico), `integracao@` (só sistemas; era a conta com quem o escritório
  compartilhava a pasta do Drive, o que a 0.7.16 dispensa; responde sozinho, sem citar outro e-mail por ora), `nao-responda@` (só envia). `integracao@` é também uma Conta Google
  sem Gmail. ImprovMX fica de reserva até ser cancelado (~2 semanas).
- Repositório segue no GitHub pessoal até depois da visita; migração para a organização `solverone` sem impacto para o
  cliente (tudo que ele vê aponta para `judicial.solverone.com.br`). Roteiro em `robo/PENDENCIAS.md`.
- Instalação no cliente (KR Law) na quinta-feira 12/Nov, na casa do Leandro, pelo dono. O pacote de quinta é a última
  versão publicada (0.7.35 em 12/Nov). Roteiro da visita e quatro prompts (PJe, ficha de canais da empresa, Astrea, e-SAJ)
  em `docs/VISITA-KR-LAW.md`: rodam sozinhos, no Sonnet, na conta do escritório; param em login, token, certificado ou
  captcha e escrevem BLOQUEIO; o relatório final volta à sessão de Produto.
- Publicação de versão (08/Nov): só a Operação publica, e só depois do dono escrever "publica a versão X" na conversa da
  Operação. Produto e Arquitetura preparam a versão e anotam "pronta para publicar" no quadro.
- Envio de e-mail: o Resend serve mais de um projeto do dono pelo mesmo domínio; separar por subdomínio fica para depois
  (nota em `robo/PENDENCIAS.md`).

## O que só o dono faz (sem conector)

Registro.br, GitHub (organização, transferência, Pages, configurações de conta), ImprovMX (cancelar), Conta Google do
`integracao@`, DIAGNOSTICO.bat e testes no PC dele, visita à KR Law, conferir o carrossel num iPhone de verdade. Para esses passos ele usa a extensão Claude in Chrome (Sonnet para o
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

Regra do dono (09/Nov, `CLAUDE.md`): o envio do e-mail de boas-vindas é do dono, pelo botão do RootifyONE; nenhuma conversa o
lembra, pergunta ou comenta.

A infraestrutura está no ar. Falta:

1. **Antes de quinta, no PC do dono**: ensaio da instalação com a segunda conta Google, `DIAGNOSTICO.bat`, rodada real
   nos 24 TRTs, e testar o instalador no Windows (falta, ver `robo/PENDENCIAS.md`). Roteiro em `robo/ROTEIRO-INSTALACAO.md`.
2. **Quinta (12/Nov)**: instalação na KR Law e os prompts de `docs/VISITA-KR-LAW.md` (relatórios vão para a sessão de
   Produto).
3. **Documentos internos abertos no site** (pedido à Arquitetura no quadro): os `.md` de `docs/` respondem em
   `judicial.solverone.com.br/NOME.md`. O dono decide se saem de `docs/`.
4. **Depois de quinta**: organização `solverone` no GitHub (refazer `limpo` como nova `main`, Pages, CNAME para
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
