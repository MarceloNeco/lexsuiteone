# Pendências do robô LexSuiteONE (07/Nov/2026, depois da v0.7.0)

Lista viva. Quem continuar (qualquer modelo ou pessoa) lê este arquivo e o `ARQUITETURA.md` antes de mexer.

## Decisões do dono em 07/Nov (tarde)

- Endereço do produto: `judicial.solverone.com.br` (decisão final: mais fácil de falar e de lembrar). Marca: **LexSuiteONE**
  é a suíte jurídica da SolverONE; **JUDICIAL** é este produto, escrito em maiúsculas com o "IA" em latão; as frentes
  (Radar Trabalhista, Tributário, Cível e empresarial) vivem dentro dele. `lexsuiteone.solverone.com.br` não é usado.
- Frentes, nesta ordem: trabalhista (existe), tributário, depois cível e empresarial. Leandro: trabalhista e tributário.
- Cópia HTML estática no Drive: fica, como reserva. O caminho principal é o sistema (tela local hoje; site na 0.8).
- 0.8 confirmada: o robô envia a lista do dia para a nuvem da SolverONE (Supabase) e o site em judicial.solverone.com.br
  mostra, com login por link no e-mail e código de cliente. O Drive continua com a planilha editável.
- Zero impacto na KR Law quando o repositório mudar de dono: tudo que o cliente vê aponta para
  `judicial.solverone.com.br` (site, download, manual, atualização assinada), nunca para a conta do GitHub. Na
  transferência para a organização: mover o repositório, religar o Pages com o mesmo domínio, trocar o alvo do CNAME
  `judicial` para `solverone.github.io` (no Cloudflare, pelo conector), atualizar links do README. O GitHub redireciona
  os endereços antigos. A chave pública de assinatura não muda.
- E-mail: **feito em 08/Nov**. Recebimento no Cloudflare Email Routing, com Email Worker que responde automaticamente
  em `integracao@` e encaminha `contato@` e os demais apelidos. Texto da resposta, por decisão do
  dono: **"Este endereço é usado por sistemas da SolverONE e não é lido por pessoas. Esta mensagem não será
  respondida."** Sem indicar outro e-mail por enquanto; quando houver processo de atendimento, passa a indicar
  `contato@`. Mais tarde, triagem em `contato@` (problema, contato comum, comercial).
- Cara profissional em tudo que o cliente vê: nenhum contato pessoal do dono (e-mail, usuário pessoal do GitHub) em site,
  e-mail, repositório ou planilha. Organização `solverone` no GitHub e endereços: `judicial@` para dúvidas de qualquer produto da suíte LexSuiteONE (e `moneytrio@` etc. para as outras suítes;
  `contato@` é o genérico da SolverONE; no futuro, triagem por programa), `integracao@` só para sistemas (Drive;
  vira Conta Google; não é monitorado e deve responder automaticamente que não é caixa de atendimento).
- Envio de e-mail pelo Resend (anotado em 08/Nov): a mesma conta e o mesmo domínio `solverone.com.br` enviam o LexSuiteONE
  e o Vagas Nutri (outro projeto do dono, para outra pessoa). Decisão do dono: **mais tarde, separar o envio por
  subdomínio** (um por produto, cada um verificado no Resend), para que devolução ou reclamação de um projeto não afete a
  reputação do outro. Nada a fazer agora.

## Requisito novo (08/Nov): ficha de canais da empresa para o compliance

Apontado pelo Leandro como o diferencial do produto: para cada ação nova, **levantar e confirmar os canais de contato da
empresa processada**, para o time de compliance do escritório analisar e decidir se e como agir. **Nada é enviado a
ninguém** pelo JUDICIAL. Ainda não implementado; o desenho sai depois da visita de 12/Nov (prompts em `docs/VISITA-KR-LAW.md`)
e passa pela regra zero antes de virar código.

- Pode: dados da empresa (telefone geral, e-mail comercial, site, LinkedIn e Instagram da empresa, endereço, nomes e
  cargos públicos de sócios e administradores), sempre com fonte. Celular e e-mail de uma pessoa só se a própria
  empresa os publica como contato comercial. Nunca: dados do reclamante e de outras pessoas físicas.
- Formato: uma ficha por empresa, uma linha por canal, com **fonte, data da consulta e grau de confiança** (alta: canal
  oficial da empresa confirmado por mais uma fonte; média: uma fonte oficial; baixa: só terceiros ou divergente).

O que o robô já traz hoje (conferido no código da 0.7.5, `lexsuite/cnpj.py` e `lexsuite/radar.py`):

- Do cadastro público da Receita (BrasilAPI, com Minha Receita de reserva; cache de 30 dias): telefone 1 e telefone 2,
  e-mail, cidade/UF e até 8 sócios e administradores com nome e qualificação. Aparece na ficha da tela; na planilha
  Radar do Drive e no `radar.csv` vão telefone, e-mail e nomes dos sócios. O ajuste "Mostrar sócios e administradores"
  desliga os nomes.
- Só quando o Diário traz o CNPJ, o que acontece em cerca de 1% dos casos. Sem CNPJ, a ficha fica vazia.

O que falta para a ficha de canais:

1. Achar o CNPJ pelo nome da empresa (já pendente na v0.6.1): é o que destrava todo o resto.
2. Endereço completo da sede: o robô guarda só cidade/UF, embora a mesma consulta à Receita devolva logradouro,
   número, bairro e CEP.
3. Telefone 2 e a qualificação dos sócios não vão para a planilha nem para o CSV (só para a tela).
4. Fonte, data da consulta e grau de confiança por dado: a data existe no cache (`consultado_em`), mas não aparece.
5. Sinalizar "provável contato do contador" quando o e-mail da Receita for de outro domínio (comum no cadastro).
6. Contatos da ré na petição inicial e na citação do PJe: dependem do relatório do Prompt 1 (onde aparecem, se dá para
   extrair de forma repetível) e do login do advogado.
7. Site, LinkedIn, Instagram e ficha no Google: o robô não procura hoje. Decidir se fica como levantamento guiado pela
   pessoa (como o Prompt 2) ou se entra em versão futura, sempre sem raspagem em massa e sem contornar login.
8. Entrega no Astrea como contato pessoa jurídica (depende do relatório do Prompt 3).
9. **Pergunta ao dono:** empresário individual e MEI entram hoje como empresa (`classificar.py` reconhece "ME" e "MEI"),
   mas o telefone e o e-mail do cadastro deles costumam ser da própria pessoa. Tratar como pessoa física (fora da
   lista) ou mostrar sem os contatos?

## Site e nome (feedback do dono, 08/Nov)

- Nome por enquanto: **RADAR JUDICIAL**, sempre em maiúsculas (o "IA" segue em latão), sob a marca LexSuiteONE.
  Aplicado na página inicial do site e no e-mail de boas-vindas. Manual, página 404, tela do robô e pacote continuam
  "JUDICIAL" (só o Leandro vê o nome antigo na tela).
- No que o cliente lê, o programa é "o RADAR", não "o robô". Pastas e arquivos internos (`robo/`) não mudam.
- Ícone do site: martelo dourado sobre azul-marinho (balança como alternativa). Um ícone só, fixo: trocar a cada carga
  confunde quem procura a aba e o navegador guarda o ícone em cache.
- Onde roda: o site e o e-mail dizem que o RADAR lê nos horários escolhidos (padrão 20h e 8h), e o site oferece "Na
  nuvem, sob consulta" (judicial@). A versão na nuvem ainda não existe: é a 1.0 (coletor central), mais abaixo.
- OneDrive: "sob consulta" no site. A tela já aceita a pasta do OneDrive para a planilha, mas o compartilhamento com o
  suporte nunca foi testado lá (pediria uma conta Microsoft para `integracao@`).
- ~~Horário das rodadas ajustável pela tela~~: feito na 0.7.9 (dono, 08/Nov).
- Imagem de fundo da capa: o dono vai gerar no Higgsfield; a página já aceita uma imagem por trás do radar.

### 0.7.7 (08/Nov, para antes da instalação de 12/Nov): licença, cadastro e tela nova

- **Licença por código de cliente** (`lexsuite/conta.py`): o código `LEX-XXXX-XXXX` vem no e-mail de boas-vindas e é
  pedido no primeiro passo; é conferido com a SolverONE ao abrir e antes de cada leitura (função `lex-conta` do
  Supabase, `nuvem/supabase/functions/lex-conta`; nenhuma chave no programa). Desativar ou vencer: na tabela
  `lex_contas` (Table Editor do Supabase; depois, tela no RootifyONE). Sem resposta da SolverONE, segue até 15 dias.
- **Cadastro de quem usa**: nome, e-mail (chave: um e-mail, um escritório) e função, e o CNPJ do escritório, nas
  tabelas `lex_usuarios` e `lex_instalacoes` (cada computador). Sem limite de pessoas; a SolverONE vê quantas são.
- **SQL para o dono revisar e rodar**: `nuvem/supabase/lex-licencas.sql`. Criar a licença: `select public.lex_criar_conta('KR Law');`.
- **Tela com a identidade do site**: cabeçalho azul, ícone e nome de `marca.json` (que agora vai no pacote), fonte
  embutida, fundo branco; boas-vindas formais e só até concluir; "Abrir a planilha"; "Baixar a lista (.csv)"; só os
  24 TRTs (TJs e TRFs voltam com as frentes deles).
- A "mira" do escritório (passo 1 do site, decisão do dono 08/Nov): em poucos cliques, frente, tribunais, valor mínimo e
  exclusões (existem); faltam **filtro por porte** (a Receita traz microempresa, pequena, média ou grande) e ~~horário
  ajustável das leituras~~ (feito na 0.7.9).
- **Mac (decisão do dono, 08/Nov):** o site trata Mac como "sob consulta" (requisito e mensagem com contato em
  judicial@), sem recusar o público. Para atender de verdade: o programa já é só Python padrão; faltam o instalador
  `.command` (ou `.pkg`), o agendamento pelo launchd no lugar do Agendador do Windows e a detecção da pasta do Google
  Drive no Mac. Alternativa: a versão na nuvem (1.0), que dispensa instalação.
- Falta depois: confirmação do e-mail por código (Resend); tela de licenças no RootifyONE; termos de uso e aviso de
  privacidade do cadastro; trocar a licença MIT antes de vender em escala (decisão do dono).

### Feito na 0.7.6 (08/Nov): contato do suporte e instalador de um arquivo

- Suporte é sempre `judicial@solverone.com.br`: manual, aba Sobre e linha "suporte" da aba Controle (planilha antiga com
  `integracao@` passa a `judicial@` sozinha). `integracao@` é só a conta de sistemas que recebe acesso à pasta do Drive.
- Instalador de um arquivo: `instalador/INSTALAR.bat`, servido em `docs/downloads/Instalar-LexSuiteONE.zip` (botão do
  site). Baixa o pacote, confere o SHA-256 publicado, instala sem administrador, cria o atalho com o nome de
  `marca.json` e abre a tela. Rodar de novo atualiza. O pacote completo continua no site como plano B.
- Manual único: `paginas/manual.html` gera o do site e o do pacote.
- **Falta testar no Windows** (não há Windows na sessão de produto): o dono roda o instalador no computador dele antes
  de 12/Nov. Limite conhecido: o Windows pode pedir confirmação para `.bat` baixado; tirar de vez pede instalador `.exe`
  assinado com certificado de código (pago).

### Manual em inglês

O manual do site (`paginas/manual.html`) está só em português. Traduzir junto com a próxima mudança de conteúdo.

### Nome do produto como configuração (decisão do dono, 08/Nov)

O nome é uma configuração, não texto fixo: o dono decide (com maiúsculas e minúsculas exatas: "RADAR JUDICIAL" hoje,
"Lex One" amanhã) e a troca vale em todo lugar. Hoje se troca editando um arquivo; no futuro, num ajuste do RootifyONE.

- **Feito (site e e-mail):** `docs/marca.json` guarda `nome`, `curto` (como o texto chama o programa) e `destaque`
  (trecho em latão). Páginas em `paginas/` com marcações; `python ferramentas/marca.py` gera `docs/`; a automação do
  GitHub recusa `docs/` desatualizado. O `preencher.py` do e-mail lê o mesmo arquivo e mostra o assunto.
- **Feito no pacote (0.7.7 a 0.7.9):** o `marca.json` vai no pacote; a tela, o manual (gerado de `paginas/manual.html`),
  o atalho do instalador e o aviso do Windows ao fim da leitura leem dele; o manual já diz "o RADAR".
- **Falta (versão nova):** a planilha (aba Sobre, `compartilhar.py`) e o e-mail de aviso (`avisar.py`) ainda dizem
  "LexSuiteONE · JUDICIAL"; e a atualização ainda não traz o `marca.json` do site dentro do manifesto assinado (hoje o
  nome só muda nas instalações com uma versão nova).
- **Não mudam sozinhos:** nomes de arquivos e pastas (`LexSuiteONE-RADAR.zip`, `C:\LexSuiteONE`, `LexSuiteONE.xlsx`),
  porque trocar quebraria instalações. Se um dia for preciso, é uma migração à parte.
- **Futuro:** ajuste "Nome do produto" no RootifyONE que grava o mesmo `marca.json` (pelo GitHub), sem editar arquivo.

## Esperando o dono (Marcelo)

- Rodar `DIAGNOSTICO.bat` no computador no Brasil e mandar `diagnostico\radar-diagnostico.txt` (arrastar para o Drive).
  Sem ele a regra de "ação nova" fica frouxa: 6.816 ações num dia em TRT2+TRT15, esperado 1.500 a 2.000.
- Testar a v0.6.0: `INSTALAR-PYTHON.bat`, `ABRIR.bat`, escolher tribunais, "Salvar e atualizar agora", print da tela e da ficha.
- Rodar `teste-djen-supabase.sql` no SQL Editor do projeto solverone-app e mandar o resultado (decide se o coletor
  central pode viver no Supabase ou precisa de um servidor pequeno em São Paulo).
- Decidir o repositório público no GitHub (núcleo aberto, MIT ou Apache 2.0). Nada é criado sem esse sim.
- Criar a Conta Google `integracao@solverone.com.br` (sem Gmail; o apelido já existe no ImprovMX), para o cliente compartilhar o Drive.

## v0.6.1 (correções)

- Regra estrita de "ação nova" calibrada com o diagnóstico (pistas em `lexsuite/diagnostico.py`, `ESTRITA`).
- Achar o CNPJ pelo nome da empresa (o Diário traz CNPJ em ~1% dos casos): base pública da Receita no portal novo
  (SERPRO); índice compacto por UF para o robô local; tabela completa no SaaS.
- Ao apertar a regra, orientar: apagar `lexsuite.db` e rodar uma vez limpa.

## Feito na v0.7.0

- Tela com Configuração (escritório, pasta compartilhada detectada), 59 tribunais por ramo/região/estado, 24 TRTs por padrão.
- Planilha de controle (Preferências, Exclusões, Controle oculto) e planilha Radar (Log, Saúde, Sobre ocultas) na pasta do Drive.
- Atualização assinada (Ed25519 + SHA-256) pela pasta compartilhada ou endereço fixo; `ferramentas/publicar.py`.
- `AGENDAR.bat`, saúde sem IA, log de rodadas, `SEGURANCA.md`, `MANUTENCAO.md`, `ROTEIRO-INSTALACAO.md`.

## 0.7.13 (09/Nov, correção; pronta para publicar com o "pode")

Defeito achado pelo dono às 00:05 de segunda: o DJEN só libera o Diário do dia a partir das 3h e responde HTTP 403 antes
disso; o programa tratava como erro e parava a leitura inteira, com "RuntimeError" e endereço técnico na tela. Agora:
esse 403 é reconhecido pelo texto da resposta e vira aviso ("o Diário de hoje só sai às 3h; li até o último dia
publicado"); cada tribunal é tentado à parte e o que foi lido é salvo; as mensagens dizem a causa em PT e EN (site do
CNJ fora do ar, sem internet, fora do Brasil, erro do programa), com o detalhe técnico recolhido; histórico de leituras
na tela e na aba Log da planilha (visível), uma linha por tribunal, com hora local e fuso, origem, resposta, causa e o
que o programa fez. O pacote grande (situações, lote, Arquivo, Estatísticas, contatos) sai na 0.7.14.

## 0.7.12 (08/Nov, visual; publicada)

Itens 38 e 39 de `documentacao/FEEDBACK-TESTE-2026-11-08.md`, com o "pode pra tudo" do dono: a tela ganha o Painel
(o desenho antigo de Cajamar: cartões de números, ações por dia, faixas de valor, setores, empresas, porte, tribunais
e estados, nas cores marinho e latão), agnóstico de frente e com os mesmos filtros da Lista; a planilha ganha
cabeçalho azul-marinho fixo, filtro em todas as colunas, R$, destaque do valor acima do mínimo e a aba "Como usar".
Testada no LibreOffice e no openpyxl; falta abrir no Excel e no Google Planilhas de verdade. Contatos (itens 40 e 41)
esperam o desenho da Arquitetura.

## 0.7.11 (08/Nov, feedback do teste do dono; publicada ou a publicar pela Operação)

Itens 19 a 26 de `documentacao/FEEDBACK-TESTE-2026-11-08.md`: leitura conta os dias que tiveram Diário (feriado e
recesso); faixa de versão nova ao abrir, atualizar com um clique e reinício sozinho; uma tela só por computador (o
atalho traz a aberta); código só para ler em Configuração; Configuração na engrenagem do alto; "Ler o Diário agora";
aviso ao abrir a planilha; barra de progresso da leitura e atalhos no fim; versão no alto e na dica do atalho; textos velhos do pacote (ressalvas b e c da revisão
da 0.7.10). Também (itens 29 a 37): CNPJ só vale para a ficha se o nome na Receita bater com o da empresa
processada ("CNPJ a conferir" quando não bate, inclusive no que já estava guardado); "Intimação" e afins saem do fim do
nome; MEI aparece (decisão do dono); tela larga com duas colunas, lista de 10 em 10, filtros e ordens novas, data
"SEG, 06 NOV 2026" e cartões novos; aviso e "Gravar a planilha agora" quando o Excel trava a planilha; manual com o
Google Planilhas.

## 0.7.10 (08/Nov, feedback do teste de instalação do dono; publicada)

Detalhe item a item em `documentacao/FEEDBACK-TESTE-2026-11-08.md`. Feito:
- **Defeito corrigido:** a leitura conta dias úteis (`monitor.dias_uteis`): sábado e domingo leem a sexta; segunda de
  manhã não pula mais a sexta.
- **Assistente:** código vindo do instalador só para ler; função obrigatória com "Outra" (texto) e "Prefiro não
  informar", e a dica (i); passo 2 com três opções explicadas (Google Drive deste computador, outra pasta com
  "Escolher pasta…" do Windows e criação da pasta, só neste computador), só o Google Drive na lista (OneDrive "sob
  consulta"); passo 3 com a frente (Tributário e Cível "em breve") e a escolha dos tribunais ali mesmo; passo 4 mostra
  onde a planilha fica e, se estiver no Drive, o passo a passo para compartilhar com `integracao@`.
- **Planilha:** instalação nova usa a pasta "<produto> - planilha" (as antigas continuam "LexSuiteONE"); a cópia da tela
  se chama "Lista para abrir no celular.html"; "Testar pasta" não deixa pasta vazia para trás.
- **Tela:** abre numa janela própria do Chrome ou do Edge (sem barra de endereço); painel Tribunais com o nome inteiro
  (duas colunas, sem "…", nome completo ao passar o mouse).
- **Janela preta:** título "<produto> - não feche esta janela" e cada passo da leitura com a hora (pela tela e na
  leitura automática).
- **Fica para depois:** e-mail já preenchido vindo do e-mail de boas-vindas (item 4; nuvem, desenho da Arquitetura).

## Feito em 08/Nov (a, b, c do dono)

- **A (nuvem, já aplicado):** pessoa ativa ou inativa, última vez, histórico (cadastro, troca de pessoa, alteração,
  acesso por dia) e limite contando só pessoas ativas (`lex-conta` v3, `lex-licencas.sql`, `lex-admin.sql`).
- **B (programa 0.7.9, publicar só com o "pode" do dono):** perfil pelas iniciais no alto da tela, com um lápis ✏️ por
  dado (nome, e-mail, função, escritório); trocar o e-mail avisa que outra pessoa vai usar o computador; o topo não
  mostra mais o nome do escritório nem "Olá"; Configuração fica com código, pasta e leituras automáticas; no passo a
  passo, cada campo é guardado ao sair dele, e ele volta enquanto o cadastro (e-mail) não estiver feito.
- **Horário de leitura ajustável (0.7.9, pedido do dono 08/Nov):** em Configuração, Leitura automática: horários em
  pílulas (tirar ×, acrescentar até 6), "Todos os dias" ou "De segunda a sexta"; padrão novo **20h e 8h** (o Diário sai
  a partir das 19h; às 8h pega o que entrou tarde da noite); leitura perdida acontece quando o computador ligar; aviso
  se não houver horário depois das 19h; "Próxima leitura automática" na tela; aviso no canto da tela do Windows ao
  terminar (dá para desligar). "Atualizar agora" continua sendo o executar na hora.
- **Depois (0.8): e-mail ao terminar** a leitura para quem está cadastrado (dono, 08/Nov: não é imprescindível).
- **C (RootifyONE 0.18.13):** Clientes → Licenças do RADAR: lista, Criar licença (código para escritório novo), ficha
  com ativar/desativar, validade, limite e mensagem, pessoas, computadores, histórico e erros; aba "Erros sem código".

## v0.7.x (ainda do robô local)

- Privacidade: trocar o trecho de 600 caracteres guardado no banco por rótulos (assunto, rito), eliminando o único
  dado sensível possível; pre-commit com gitleaks e bandit; plano de incidente de uma página (ver SEGURANCA-REVISAO).
- GitHub: proteção do ramo `main`, Dependabot, 2FA, ações da CI fixadas por SHA.

- Preferências que faltam: porte, CNAE e valor da causa como filtros (dependem do CNPJ pelo nome e do valor digitado).
- Avisos por Telegram e e-mail só do que passa nas regras (reaproveitar `avisar.py`).
- Regra de "ação nova" nos TJs e TRFs (hoje marcada "a calibrar"); classe "execução fiscal" para a frente tributária.
- Endereço fixo de atualização (precisa do repositório público no GitHub).
- Integração de saída: webhook JSON (um POST por ação, com HMAC) e CSV importável; começar por EasyJur e ADVBOX (APIs
  documentadas) e pelo Astrea quando houver API; ver `docs/INTEGRACOES-MERCADO.md`.
- Wizard de um arquivo (`INSTALAR-LEXSUITE.bat`, para WhatsApp): cria a pasta, baixa pacote e Python, abre a tela.
  Depende de um endereço público de download (Drive "qualquer pessoa com o link" ou GitHub).
- Tela: mostrar a hora da próxima rodada agendada; botão "Abrir pasta de saída".

## v0.8 (cliente-servidor e conta na nuvem)

**Desenho completo em `documentacao/DESENHO-0.8.md` (versão 2, 08/Nov/2026, reescrita em cima da licença da 0.7.9),
com as decisões D1 a D9 do dono.** Nada de código antes de ele aprovar o conjunto; nenhum SQL roda sem a revisão dele.
Pendências da Arquitetura (lista inteira na seção 13 do desenho):

- **Bloqueante:** termo de tratamento de dados com a KR Law (a SolverONE guarda dados em nome do escritório) assinado
  antes de a 0.8 entrar no ar. ⏸ Aguardando o dono.
- **Revisão de segurança da nuvem das licenças** (`documentacao/REVISAO-NUVEM-LICENCAS-2026-11-08.md`): nota Baixo hoje,
  Médio se a 0.8 entrar sem a etapa 0. SQL de correção em `nuvem/supabase/2026-11-08-lex-correcoes-seguranca.sql`
  ⏸ aguardando o dono revisar e rodar; `lex-conta` v4 (limites, resposta genérica, limpeza de `mensagem`) 🟡 depois do "pode".
- Copiar `teste/sql-grants.js` do rootify-one para este repositório e ligar na CI. 🟡 Arquitetura.
- Para a 1.0: e-mail de entrada com a marca de cada suíte (Send Email Hook do Supabase Auth); na 0.8 o remetente é
  "SolverONE <nao-responda@solverone.com.br>".

Os itens abaixo são o texto original da 0.8 (07/Nov) e ficam como histórico; o que vale é o desenho.

- Conta na nuvem (`judicial.solverone.com.br`): o robô, se tiver internet, pergunta a cada abertura se a conta do
  escritório continua ativa e registra um batimento (versão, última rodada, contagens). Gestão no RootifyONE.
  Regra de queda: sem resposta da nuvem, vale a aba Controle da planilha; sem nenhuma das duas por 30 dias, avisa
  e continua (não trava, por ser instalação local). Tabelas `lex_contas` e `lex_batimentos` no Supabase (SQL
  entregue para revisão e execução pelo dono, regra C10); chave publicável no `config.json`, nunca secreta.
- Código de cliente: formato `LEX-XXXX-XXXX` (letras e números, sem 0/O/1/I para não confundir), gerado no
  RootifyONE, enviado no e-mail de boas-vindas (bloco opcional já previsto no modelo em `docs/email/`) e pedido
  pelo passo a passo na instalação. Identifica a conta; não é senha e não dá acesso a nada sozinho.
- Endereço fixo de atualização: `judicial.solverone.com.br/atualizacao/` (site do produto). Assinatura na nuvem desde 08/Nov
  (serviço `assinatura.solverone.com.br`; publicação por tag `vX.Y.Z`, ver `docs/PUBLICAR.md`).

- Log de cada rodada numa aba oculta de uma planilha Google do cliente (via Apps Script publicado na conta da SolverONE;
  o robô só faz POST com biblioteca padrão; chave por cliente no `config.json`, nunca no código).
- Aba "Radar" com o incremento do dia e aba "Preferências" editável pelos advogados (as mesmas regras da v0.7).
- Painel de auditoria do fornecedor: leitura das abas de log pelo conector do Drive.

## 1.0 (SaaS no RootifyONE)

- Coletor central no Brasil (Supabase pg_cron + pg_net para a consulta leve; servidor pequeno para o caderno de 150 MB),
  lendo cada TRT uma vez para todos os escritórios. Tabelas `lex_publicacoes`, `lex_acoes`, `lex_regras`, `lex_eventos`.
- Fila de eventos: cada ação que passa nas regras de um escritório vira evento; entrega por e-mail, WhatsApp,
  notificação no app (PWA) e webhook de saída para o sistema do escritório.
- Interruptores do RootifyONE (`data-recurso`, `recursos-do-app.json`), PT/EN, feedback 💬, trabalho em `Fundo`.
- Bandit e Gitleaks no GitHub Actions (sem IA). Revisão de segurança e LGPD trimestral com a skill existente.

## Ideias registradas (portfólio)

- Monitor de publicações dos processos do escritório (já existe em `monitor.py`; virar produto).
- Jurimetria da vara e do juiz (DataJud); raio-x trabalhista de um CNPJ (para empresas); radar cível nos TJs
  (o DJEN cobre todos os tribunais).
- IA opcional e trocável (resumo, peças) com chave do próprio escritório, nunca no caminho principal.
