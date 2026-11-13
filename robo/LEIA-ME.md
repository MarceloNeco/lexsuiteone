# LexSuiteONE · RADAR JUDICIAL — robô v0.7.37 (frente trabalhista)

Uma lista por dia: os processos novos contra empresas nos tribunais que você escolher (os 24 TRTs por padrão; também os
TJs, os TRFs, STJ e TST), uma por linha, com a ficha da empresa e do processo. Tudo roda no seu computador, sem
inteligência artificial e sem senha de ninguém. A planilha vai para a sua pasta do Google Drive.

## Instalar (Windows, dois cliques)

O caminho normal é o **instalador de um arquivo**: em judicial.solverone.com.br, "Baixar", abrir o arquivo e dois
cliques em `INSTALAR.bat`. Ele baixa este pacote do site, confere a impressão digital (SHA-256) publicada em
`atualizacao/instalar.txt`, instala em `C:\LexSuiteONE` (ou na pasta do usuário, se o Windows não deixar), prepara o
Python portátil, cria o atalho com o nome do produto na área de trabalho e no menu Iniciar e abre a tela. Rodar de novo
atualiza sem perder configuração nem lista. A fonte é `instalador/INSTALAR.bat` no repositório (não vem no pacote).

À mão, com o pacote completo:

1. Descompacte o `.zip` numa pasta fácil, por exemplo `C:\LexSuiteONE`. A pasta pode ter qualquer nome; mantenha tudo
   junto, porque o robô guarda ali o `config.json`, o banco `lexsuite.db` e a pasta `saida`.
2. Dois cliques em **`ABRIR.bat`**. Na primeira vez ele baixa o Python portátil oficial para dentro da pasta (11 MB,
   sem instalador, sem senha de administrador) e abre a tela no navegador. Uma janela "LexSuiteONE" fica aberta
   enquanto a tela é usada.
3. Na primeira vez a tela (numa janela própria, sem barra de endereço) abre um **passo a passo de boas-vindas** (0.7.10:
   código só para ler, função obrigatória, três opções para a planilha, tribunais escolhidos ali, onde a planilha fica e
   como compartilhar): seu nome e seu papel no escritório (a tela e o
   manual passam a falar com você), o nome do escritório, a **pasta compartilhada** (a tela lista as pastas do Google
   Drive para computador que achou, ou outra pasta pelo "Escolher pasta…"; "Testar pasta" confirma) e a opção **rodar sozinho**
   (de início de segunda a sexta, às 20h e às 8h, já marcada; dias e horários mudam em Configurações). "Começar a primeira rodada" salva tudo, cria a planilha `LexSuiteONE - Trabalhista.xlsx` na pasta escolhida,
   agenda as rodadas e dispara a primeira. Cada campo do passo a passo fica guardado ao sair dele (fechar a tela no meio
   não perde o que foi digitado). Depois, quem usa (nome, e-mail, função, escritório) muda no **perfil** (as iniciais no
   alto da tela, um lápis ✏️ por dado; trocar o e-mail = outra pessoa usando o computador) e o código, a pasta e as
   leituras automáticas, em **Configurações**.
4. **Ler o Diário agora** (até a 0.7.10, "Atualizar agora"): os 24 TRTs já vêm escolhidos (em **Tribunais** dá para mudar: por região, por estado, por
   ramo ou "Selecionar todos"). A primeira rodada baixa o diário do dia de cada tribunal (de 5 a 150 MB cada): os 24
   TRTs levam de 30 a 60 minutos; depois, só o que é novo. O computador precisa estar **no Brasil**.
5. Não é preciso compartilhar nada com a SolverONE (decisão do dono, 09/Nov; até a 0.7.15 o assistente pedia para
   compartilhar a pasta com `integracao@`). Dúvidas de pessoas vão para `judicial@solverone.com.br`.

Tribunais estaduais publicam diários muito maiores (o TJSP sozinho pode passar de 1 GB) e a regra de "ação nova"
ainda não foi calibrada neles.

## A planilha no Drive

Uma por frente (0.7.16), na mesma pasta: `<pasta escolhida>\<subpasta>\LexSuiteONE - Trabalhista.xlsx` (a
`LexSuiteONE.xlsx` antiga vira essa na primeira leitura, com as abas editadas). Ao lado, `Cópias` e `Cópias de segurança`.
A aba Arquivo mostra os últimos 90 dias e todo processo trabalhado; limite de 60 mil linhas por planilha, com aviso a
80% e limpeza com cópia sozinha a 100% (6 cópias guardadas). Configurações → Leitura do Diário → Armazenamento mostra planilhas, banco,
`saida/`, cópias e o espaço livre do disco.

- **Radar** (o robô escreve a cada rodada): a lista do dia, com as mesmas colunas da tela. A partir da 0.7.12, com
  cabeçalho azul-marinho fixo, filtro em todas as colunas, valores em R$ e o valor da causa acima do mínimo em latão
  claro; abre igual no Excel e no Google Planilhas.
- **Como usar**: o passo a passo da planilha, em português e inglês.
- **Critérios desta leitura** (0.7.33, só leitura): com que critérios a pessoa que gravou por último olhou a lista. As
  antigas abas **Preferências** e **Exclusões** saíram: os critérios e as empresas excluídas são de cada pessoa, no
  computador dela, por área (Configurações → Destaques e exclusões); a planilha fica completa, como registro do escritório.
- Abas ocultas, usadas pelo suporte: **Controle** (`ativo`, `validade`, `versao_minima`, `mensagem`, `suporte`),
  **Log** (cada rodada), **Saúde** (o que o robô percebeu: Diário fora do ar, formato mudou, Receita sem resposta) e
  **Sobre** (versão, computador, pasta).

Também fica ali a página `Retrato da última leitura.html` (antes `Lista para abrir no celular.html`), uma foto da lista na última leitura que abre em qualquer lugar. No Google Planilhas,
abra o `.xlsx` para consultar (modo de compatibilidade com Office). Os destaques e as exclusões (empresas excluídas, valor mínimo)
são de cada pessoa, neste computador, por área (0.7.33): Configurações → Destaques e exclusões. A planilha não guarda critérios. Se a planilha estiver aberta e travada na hora de uma rodada, o robô tenta de novo a cada 2 minutos e grava sozinho quando ela for fechada.

## A tela

- **0.7.37 (teste do dono na 0.7.36, 13/Nov):** no Painel, Situação (no alto) e Vara, Setor, Porte e Estado (em "Mais
  filtros") ficam sempre à vista: o que sai de um gráfico aparece no filtro correspondente, em vez de surgir do nada;
  Configurações sem o parágrafo de abertura e mais larga (1280 px); busca das empresas excluídas sem rótulo repetido; na
  faixa da leitura, sem a frase que anunciava o caminho do arquivo e, no celular, barra e Interromper fixos na primeira
  linha; "1 processo novo" e "1 notice read" também no inglês e na aba Saúde; o nome pelo CNPJ só diz "não encontrado"
  quando todas as fontes responderam; duplo clique em Acrescentar sem erro falso; "processos" no e-mail de aviso e nas
  mensagens da linha de comando.
- **0.7.36 (teste do dono na 0.7.35, 12/Nov):** Configurações em quatro seções com faixa (Processos, Leitura do Diário,
  Tela, Licença e termos); "Critérios da lista" vira "Destaques e exclusões" e "Leitura automática" vira "Rotina de
  leitura"; "processos" no lugar de "ações" nas telas; Licença e termos com o código, a situação ("ativa" em verde) e a
  validade numa linha, "Conferir agora" que mostra que está conferindo, termos numa linha e Sobre este computador sem
  repetir a licença ("Último envio", (?) na chave de atualização); verificar atualização em verde, azul ou vermelho;
  Pasta das planilhas com o caminho uma vez só, botões numa linha (Escolher pasta, Google Drive, OneDrive sem nome
  entre parênteses) e "Abrir a pasta no Windows" separado; empresas excluídas com o nome pelo CNPJ (cadastro público),
  busca separada que não esconde em silêncio, motivo de cada recusa e uma linha por empresa; copiar para outras áreas
  só com mais de uma área em uso, escolhendo áreas, partes e se soma ou substitui; barras de Processos por dia
  separadas por tribunal, situação, faixa de valor ou setor (Sazonalidade por tribunal), sem o dourado; pizza que se
  refaz com movimento e itens todos clicáveis; dicas (?) em blocos; Buscar estatísticas responde na hora; faixa da
  leitura numa linha, sem caminho de arquivo; "Nada novo" quando a leitura não traz publicação nova; Histórico de
  leituras fora das abas (Configurações → Sobre este computador, e faixa vermelha no Painel quando uma leitura falha);
  lupa vazia só orienta, acha pelo começo das palavras, sem repetidos e com Sair; ressalvas da Operação (Conferir agora
  durante a leitura, Trocar licença encadeado, avisos sem empilhar, texto em EN). Nas revisões da Operação: nome da empresa
  pelo CNPJ com o cache do banco, uma tentativa curta e limite de 10 s na tela ("sem internet ou fonte ocupada" separado de
  "não encontrado"); erro sempre em vermelho e botão desabilitado em cinza; avisos de abrir planilha ou pasta sem "A leitura
  parou"; textos do servidor e da planilha com "processos" e "Destaques e exclusões"; código que roda também no Python 3.11.
- **0.7.35 (dono, 12/Nov):** tela de abertura enquanto carrega; "Conferir agora" em Licença e termos; "Abrir a pasta no
  Windows" em Pasta das planilhas; "Continuar à noite" também com a busca parada; faixa da leitura numa linha (mensagens
  anteriores recolhidas); Novidades largas no computador; ao encerrar, a janela tenta se fechar e diz como abrir de novo.
- **0.7.34 (dono, 12/Nov):** depois do aceite dos termos na página, o programa confere sozinho com a SolverONE ao voltar
  para a janela (e a cada 15 s por até 10 minutos depois de abrir a página), e "Ler o Diário agora" confere antes de mostrar o
  aviso; o aviso ganhou "Já aceitei". O banco espera até 30 s pela vez em vez de cair com "database is locked".
- **0.7.33 (dono, 12/Nov):** critérios da lista e empresas excluídas de cada pessoa, neste computador, por área
  (`criterios.json`; migração única das abas da planilha; "Copiar estes critérios para as outras áreas"; valor vazio = sem
  mínimo; números com ponto; CPF e CNPJ conferidos, inclusive o CNPJ com letras; um Salvar só); CNPJ com letras reconhecido
  nos Diários e na ficha; Painel sem
  busca e sem filtros repetidos, com etiqueta grande nos gráficos; sazonalidade lendo a fila inteira com barra por mês,
  Pausar e Continuar à noite; menu Configurações com os nomes da janela e grupo Ajuda; planilha completa com a aba
  "Critérios desta leitura". Pacote com 46/45 arquivos (novo `lexsuite/documento.py`).
- **0.7.32 (dono, 11/Nov):** gráficos do Painel com dica ao passar o mouse, item ligado e desligado pela legenda
  (apagado, "Mostrar todos"), "Ver na lista →" e cor escolhida ("Cores originais"); filtros do Painel separados dos da
  Lista; leitura automática por dias da semana (padrão de segunda a sexta; nenhum dia = desligada); Configuração
  reorganizada (A lista, Onde ficam as planilhas, Leitura, Tela, Licença e termos com "Trocar licença"), menu
  "Configurações" na mesma ordem, Aparência também na Configuração; ressalvas da revisão da 0.7.31.
- **0.7.31 (teste do dono na 0.7.30, 11/Nov):** termos e licença com textos curtos (sem o link por extenso nem o código),
  código travado e mascarado, Termos com um botão; Sazonalidade com um botão e "Últimos N meses"; "Publicado no Diário";
  Configuração da leitura mais baixa; setas que giram e painéis que abrem e fecham com movimento; Configuração e Perfil
  em janela e rolando com a roda do mouse; (?) na frente; desligar a leitura automática com confirmação e aviso na tela
  inicial; manual genérico, com o ícone embutido.
- **0.7.30, revisão da Operação (11/Nov):** menu ☰ legível no modo escuro; no celular, "Mais filtros" aberto não
  alarga a página; "último dia útil" pula feriado nacional; Esc fecha o Perfil; impressão sempre no claro; contraste
  mínimo em todo texto (claro e escuro), conferido pelo `larguras.js`.
- **0.7.30 (teste do dono, 11/Nov):** tela em três blocos: "Configuração da leitura" numa faixa baixa (o que o programa
  lê, "Alterar configuração", "Ler o Diário agora", que salva e lê os tribunais marcados), "Filtros" numa linha só no
  computador, fixos no alto ao rolar (busca, Data do processo, Situação, Valor, "Mais filtros" com todos os outros,
  filtros salvos sempre à vista com "★ Salvar", ✕ em cada filtro ligado, "Marcar todos", "Limpar filtros (N)" em
  pílula vermelha) e a ordenação com "Baixar a lista (.csv)" em dourado. **Data do processo** conta pela data no
  Diário (1 = do último dia útil até hoje; até 90 dias); o filtro de tribunais mostra só o que está na lista; a
  Configuração diz os tribunais lidos com atalho para a mira. Painel: faixa com de quando são os números e o período
  (troca na hora quando já carregado, com círculo girando quando carrega), tribunal à vista, "Separar por tribunal"
  nas barras por dia (lembrado), "Ver como: Barras | Pizza", meses com letras, "Buscar estatísticas" responde ali.
  Abas com destaque e barrinha deslizando; modo escuro sóbrio no Perfil (Claro, Escuro, Igual ao sistema); "Licença:
  ✓ ativa" com cor por estado; sem licença ativa, "Ler o Diário agora" explica e leva aos termos; a faixa de versão
  nova aparece também com a tela aberta (confere a cada 30 minutos); com janela aberta a página de trás não rola;
  janela fechada no X e novo clique no atalho reabrem a tela. Ressalvas da segunda revisão da 0.7.29 feitas.
- **0.7.29 (dono): sem janela preta.** A tela e a leitura automática rodam sem janela de prompt de comando
  (`pythonw.exe` do Python portátil): o atalho abre o programa direto, a tarefa do Windows é recriada sozinha para chamar
  o Python sem janela, e o que aparecia na janela preta fica em `saida/registro.txt` (Configuração → **Ver registro**).
  Erro antes de a tela abrir: caixa de aviso do Windows; leitura que para com erro: aviso no canto da tela. Sair: ☰ →
  Sair, ou sozinho 3 minutos depois de fechar a tela; se travar: `DIAGNOSTICO.bat`, opção 2. Suporte: `ABRIR.bat --ver`.
  Também: "Salvar regras" recusado durante uma leitura (ela regravaria as regras antigas), "Salvar" da Configuração
  pergunta pelas regras não salvas, Esc com mudança pergunta, nome digitado entra junto ao salvar, cópias "antes de
  salvar regras" no mesmo segundo não se sobrescrevem, números inteiros onde só cabe inteiro, Saúde sem falso alarme
  quando os Diários já tinham sido conferidos, mês em inglês no histórico em inglês, manual sem "edite a planilha à mão".
  Teste do dono (11/Nov): sem "Ver a lista" e "Abrir a planilha" debaixo da última leitura (a lista está logo abaixo e
  a planilha tem o botão no alto); o painel da mira mostra as 4 fases do RADAR, com a 1ª em destaque.
- **0.7.28 (teste do dono no Windows):** datas com o mês em letras em todo o programa (10/NOV/2026) e fuso ao lado
  da hora, como "(Brasília)"; critério do "Ler o Diário agora" curto, com o atalho "alterar"; filtros em azul-marinho e
  ordenação em dourado, com "Limpar filtros" sempre ao lado (apagado quando não há filtro); a lista lembra os últimos
  filtros; toda janela tem ✕, Cancelar e fecha ao clicar fora; filtros salvos em ordem alfabética, com renomear,
  arquivar e apagar nas Configurações (ficam neste computador por enquanto); **Regras do escritório** (desde a 0.7.32, **Critérios da lista**; desde a 0.7.36, **Destaques e exclusões**) nas Configurações
  (valor mínimo, jurídico próprio, sócios, arquivo, limite e empresas excluídas) editadas na tela e gravadas pelo RADAR
  nas abas Preferências e Exclusões da planilha (sem editar Excel à mão; entram na cópia de segurança); clicar de novo
  no atalho com a tela aberta não abre outra janela: a tela aberta avisa "O RADAR já estava aberto aqui".
- **0.7.28:** ressalvas da revisão da 0.7.27: limite de área logada por dia e meses guardados com `Infinity`, `NaN` ou
  texto no `config.json` não derrubam a tela; a lupa do retrato salvo mostra o exemplo certo; o servidor de teste com
  dados fictícios não sai para a internet em nenhuma rota.
- **0.7.27:** ressalvas da revisão da 0.7.26: `Infinity`/`NaN` escritos à mão em valor mínimo, dias na página e teto de
  capital não impedem mais a tela de abrir; o aviso de planilha em uso não se repete e diz a verdade também sem Excel;
  a lupa do retrato salvo oferece só Painel e Lista; o servidor de teste com dados fictícios não faz a leitura do Diário.
- **0.7.26:** ressalvas da revisão da 0.7.25: `dias_na_pagina` absurdo no `config.json` não impede mais gravar a página e a
  planilha no fim da leitura; o aviso de planilha em uso diz a verdade (pode ser Excel aberto ou falta de permissão) e
  fica na tela até a próxima ação; a lupa do retrato salvo só oferece o que funciona offline; testes que de fato falham
  se as correções forem desfeitas.
- **0.7.25:** ressalvas das revisões da 0.7.23 e da 0.7.24: "Abrir a planilha" não marca "somente leitura" se ela
  estiver aberta para edição em outro lugar (e avisa); valores absurdos no config ou nos pedidos não derrubam a tela;
  título da janela de pastas sem "Meu Drive"; lupa sem as partes da Configuração no retrato salvo e sem repetir itens;
  fechar a lupa pelo ✕ devolve o foco; o alvo da Configuração não some sob o cabeçalho; teste contra comentário que
  engole código mais rigoroso.
- **0.7.24 (teste do dono no Windows da 0.7.23):** o link "Abrir a planilha" da última leitura também mostra o aviso de
  "só para leitura"; a planilha de consulta fica marcada "somente leitura" já ao abrir; a lupa acha as partes da
  Configuração ("Onde ficam as planilhas", horários, armazenamento, termos, AssistONE); o critério de "Ler o Diário
  agora" fica embaixo do botão; as opções de pasta chamam "Pasta padrão do RADAR" e "Outra pasta".
- **0.7.23:** ressalvas da revisão da 0.7.22: textos sem "Google Drive" como padrão, aviso de planilha que fala também
  de falta de permissão, passo do tour com "Área logada", motivos da licença em inglês na tela em EN, números do
  `config.json` com limite (texto ou valor absurdo não derrubam a tela nem a leitura), nome do escritório sempre válido
  na cópia de trabalho e testes que faltavam.
- **0.7.22:** AssistONE 1.1.1 (master do RootifyONE): no tour, o balão desliza de um passo ao outro, o personagem não
  some (só se cobrir o que está sendo mostrado) e o "Próximo ›" cabe numa linha.
- **0.7.21 (teste do dono no Windows):** pastas em duas opções (Neste computador, padrão, ou Pasta compartilhada:
  rede, OneDrive ou Google Drive para computador, com atalho quando estão instalados) e explicação antes de mudar;
  planilha de consulta marcada "somente leitura" no Windows (abre só para leitura até com dois cliques; "Editar
  Preferências e Exclusões" tira a marca); aviso "planilha só para leitura" volta a cada versão, licença ou pessoa nova;
  (?) ao lado de "Abrir a planilha"; cópia de trabalho com o nome do escritório; embaixo de "Ler o Diário agora", o que
  ele vai ler; validade da licença ("válida até …" ou "sem data de vencimento"); menu "Área logada → Trazer dados da
  área logada". Também as ressalvas da revisão da 0.7.20: regra de segurança da página também para formulários e molduras; erro das
  estatísticas antigas aparece na hora e só diz "a SolverONE foi avisada" depois de o aviso chegar; "última leitura"
  também com o programa em pasta de rede; AssistONE diz o que vai à SolverONE (Configuração e Primeiro acesso) e o
  "Próximo ›" do tour cabe numa linha.
- **0.7.20:** a SolverONE pode desligar o AssistONE pelo RootifyONE (Controle dos apps): o aviso chega na conferência
  da licença, sem a tela fazer pedido à internet; desligado assim, o cartão da Configuração diz "Desligado pela
  administração da SolverONE". O link "Aceitar em nome do escritório" leva código, e-mail e nome depois do `#`, que não
  vai ao servidor nem fica em registro dele.
- **0.7.19:** menu ☰ em gaveta que desliza, com cabeçalhos de grupo (não clicáveis), itens recuados com seta e "Sair"
  separado em vermelho; **lupa** ao lado da engrenagem, que procura empresa, processo, CNPJ, cidade, opção do programa
  e assunto do manual; engrenagem centrada; "Interromper" virou botão vermelho; depois de reiniciar, a tela mostra a
  última leitura guardada (não "Ainda não leu"); Configuração → pasta com três opções explicadas (Google Drive,
  só neste computador, outra pasta), o caminho inteiro e o teste automático (sem botão "Testar"); a janela de pastas
  do Windows abre na frente; termos com um link só para ler e, se faltar, "Aceitar em nome do escritório" já com
  código, nome e e-mail; código de cliente mascarado no perfil e na Configuração; motivo da parada das estatísticas
  fica na tela, em PT ou EN; gráfico "Como a ação nova foi reconhecida". Antes de mudar o banco, a atualização guarda
  uma cópia `lexsuite.db.antes-<versão>-<data>` na pasta do programa (fica só neste computador; o
  `PREPARAR-PARA-CLIENTE.bat` a apaga). **AssistONE**, o assistente de todos os apps da SolverONE, no canto inferior
  direito: explica a tela onde a pessoa está, faz um tour rápido, dá uma dica por tela e procura funções; liga e
  desliga em Configuração → AssistONE. Sem IA e sem internet (só ajuda; as escolhas ficam neste navegador).
- **0.7.18:** **estatísticas dos meses anteriores** no Painel ("Sazonalidade": ações novas por mês e por dia da
  semana, mês de pico): o escritório escolhe quantos meses (padrão 3), o RADAR lê os Diários antigos (desde a 0.7.33, a fila inteira, com pausa, barra por mês, Pausar e Continuar à
  noite), e guarda os totais e, só neste computador, o número dos processos já contados; engrenagem ⚙ ao lado do perfil (abre a
  Configuração numa janela por cima); perfil na mesma janela, com a licença do escritório, e-mail e escritório fixos
  e "Outra pessoa vai usar este computador"; pelo menu ☰, Configuração e perfil abrem como página com "Voltar";
  "Gerar uma cópia" com "Abrir a cópia" e "Abrir a pasta"; o estado (UF) da empresa vem do endereço trazido da área
  logada; limpeza única do que a regra antiga guardou e não é ação nova (fica no banco, fora da lista).
- **0.7.17:** filtros com várias opções (caixas de marcar), contagem de cada opção que segue os outros filtros (o que
  daria zero some), "Limpar filtros" sempre que houver filtro ligado; turmas e gabinetes (2º grau) fora da lista; banco
  acima de 1 GB resume com 6 meses só os processos nunca abertos; limpeza automática só com cópia; data da mudança do
  critério de "ação nova" no Painel.
- **0.7.16:** regra de "ação nova" mais estreita (antes, "fica notificado" e "citação" de qualquer processo do ano
  entravam: dois TRTs davam 20 mil "novos"); uma planilha por frente; cópias de segurança e armazenamento; leitura só
  das abas editáveis (a planilha grande dava "ValueError"); Configuração em janela própria com ✕ e Salvar; "Buscar na
  área logada" com a resposta padronizada `RESPOSTA PARA O RADAR v1` (qualquer extensão de IA); valor da causa e data
  de ajuizamento guardados no programa; ✓ ao salvar; "Sair do RADAR" e encerramento sozinho 3 minutos depois de fechar a tela (desde a 0.7.29 sem janela preta)
  da tela; carregamento ao atualizar; termos das duas camadas na Configuração; nada é compartilhado com a SolverONE.
- **0.7.15:** botão **Interromper** durante a leitura (para num ponto seguro; as ações já gravadas ficam) e aviso de
  "leitura das 08h00 feita agora" quando o computador estava desligado na hora marcada.
- **0.7.14:** menu ☰ (Configuração, planilha, contatos), abas Painel · Lista · Arquivo · Histórico de leituras, um
  processo por linha com a **situação** (Novo, Visto, Em análise, Em contato, Virou cliente, Descartado, Arquivado) e o
  selo de contato, seleção de vários com "Desfazer", busca, filtros novos e filtros salvos. A planilha abre só para
  leitura; "Gerar uma cópia" cria uma cópia para trabalhar.

- **Leitura entre meia-noite e 3h (0.7.13):** o Diário do dia só sai às 3h; o programa avisa e lê até o último dia
  publicado. Se o site do CNJ estiver fora do ar, a tela diz isso (não é problema do computador) e lê os outros
  tribunais. **Histórico de leituras** (abaixo do estado) e a aba **Log** da planilha mostram cada tentativa.

- **Painel e Lista (0.7.12):** o Painel mostra os números do período (ações, acima do valor mínimo, valor somado, com
  CNPJ, empresas, sem valor), ações por dia, faixas de valor, setores, empresas com mais ações, porte, tribunais e
  estados. Os filtros valem para os dois; clicar numa barra abre a Lista já filtrada. A tela lembra a última aba.
- **Uma linha por ação:** tribunal, empresa, setor, porte, cidade, vara e o valor da causa (ou "a conferir").
- **Clique na linha, a ficha abre:** cada dado numa linha própria, sempre presente; o que falta aparece como
  "não informado no cadastro" (a Receita não tem) ou "não capturado" (está no PJe, atrás do captcha).
- **Filtros:** acima do valor mínimo; sem jurídico próprio provável; mostrar excluídas; um tribunal ou todos.
  **Período:** último dia, 3, 7, 15 ou 30 dias. **Exportar planilha** gera um `.csv` com o que está na tela.
- **Valor da causa:** o Diário não traz; está na consulta pública do PJe atrás de um captcha. Botão "Abrir consulta no
  PJe", "Copiar número", e o campo para digitar o valor (fica no navegador e sai na planilha exportada).
- **Configuração:** seu nome e papel, escritório, pasta compartilhada, rodar sozinho, versão instalada, chave de
  atualização e o botão "Verificar atualização". **Manual do escritório** no rodapé, personalizado para o seu papel.

## Rodar sozinho

- A opção "Ler sozinho" da Configuração cria a tarefa "LexSuiteONE Radar" no Agendador do Windows, com os horários
  escolhidos (padrão 20h e 8h, até 6, nos dias da semana marcados, de início de segunda a sexta; se o computador estava desligado, roda quando
  ele ligar). Ela roda o `RODAR.bat`; ao terminar, um aviso no canto da tela diz quantas ações novas chegaram.
  `AGENDAR.bat` faz o mesmo à mão (botão direito, Executar como administrador), se precisar. O DJEN termina de publicar o Diário do dia à noite (por volta das 19h); de madrugada, o Diário do dia novo só aparece depois das 3h.
- **`RODAR.bat`**: uma rodada sem a tela, com os tribunais salvos. Também grava `saida\radar\radar.html`.
- **`DIAGNOSTICO.bat`**: relatório `diagnostico\radar-diagnostico.txt` do que o robô guardou, sem dado de pessoa física.

- **`PREPARAR-PARA-CLIENTE.bat`**: depois de testar numa pasta, apaga config, banco e saídas e deixa a pasta pronta para
  copiar para outro computador (o Python já instalado vai junto).

## Atualização assinada

O suporte publica versões novas na subpasta `atualizacao` da pasta compartilhada (o Drive leva até o computador)
ou num endereço fixo. O robô só instala se a assinatura digital do pacote bater com a chave pública que está em
`chave_publica.txt`, ao lado deste arquivo, e se o conteúdo bater com o resumo criptográfico do manifesto. Sem
`chave_publica.txt`, a atualização fica desligada. O `config.json`, o banco, a pasta `python` e a pasta `saida`
nunca são tocados; a versão anterior fica guardada em `_anterior\`.

## O que é automático e o que fica com gente

| Dado | Como chega |
|---|---|
| Ação nova, partes (empresas), vara, rito, data do Diário | automático, pelo Diário (DJEN) |
| CNPJ | automático quando está no texto do Diário; senão, do clique no PJe |
| Porte, capital, CNAE, cidade, telefone, e-mail, sócios | automático, pela Receita, quando há CNPJ |
| Valor da causa e data de distribuição | pessoa, no PJe (captcha), digitado na página |
| Faturamento | não é público; o porte dá a faixa (micro até R$ 360 mil; pequena até R$ 4,8 milhões; demais acima) |

## Cuidados

- Poucos pedidos, com intervalo. Não aumente a velocidade nem rode várias cópias ao mesmo tempo.
- A tela só responde ao navegador deste computador (endereço 127.0.0.1). Nada é publicado na internet.
- O robô não burla captcha nem usa senha ou certificado de ninguém. Pessoas físicas nunca aparecem.
- O "desligar pelo suporte" (aba Controle) é uma chave de cortesia, não uma trava: quem tem o computador pode
  alterar a planilha. Ele serve para pausar, avisar e pedir atualização, não para impedir uso.
