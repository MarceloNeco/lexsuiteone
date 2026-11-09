# LexSuiteONE · RADAR JUDICIAL — robô v0.7.15 (frente trabalhista)

Uma lista por dia: as ações novas contra empresas nos tribunais que você escolher (os 24 TRTs por padrão; também os
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
   Drive para computador que achou, ou outra pasta pelo "Escolher pasta…"; "Testar pasta" confirma) e a opção **rodar sozinho todo dia**
   (de início às 20h e às 8h, já marcada; os horários mudam em Configuração). "Começar a primeira rodada" salva tudo, cria a planilha `LexSuiteONE.xlsx` no Drive,
   agenda as rodadas e dispara a primeira. Cada campo do passo a passo fica guardado ao sair dele (fechar a tela no meio
   não perde o que foi digitado). Depois, quem usa (nome, e-mail, função, escritório) muda no **perfil** (as iniciais no
   alto da tela, um lápis ✏️ por dado; trocar o e-mail = outra pessoa usando o computador) e o código, a pasta e as
   leituras automáticas, em **Configuração**.
4. **Ler o Diário agora** (até a 0.7.10, "Atualizar agora"): os 24 TRTs já vêm escolhidos (em **Tribunais** dá para mudar: por região, por estado, por
   ramo ou "Selecionar todos"). A primeira rodada baixa o diário do dia de cada tribunal (de 5 a 150 MB cada): os 24
   TRTs levam de 30 a 60 minutos; depois, só o que é novo. O computador precisa estar **no Brasil**.
5. No Drive, dê acesso de editor à pasta da planilha (`RADAR JUDICIAL - planilha` nas instalações a partir da 0.7.10;
   `LexSuiteONE` nas anteriores; o fim do assistente mostra o nome e o passo a passo) para `integracao@solverone.com.br`, a conta de sistemas da
   SolverONE (botão direito, Compartilhar). É a única etapa que o robô não faz sozinho. Dúvidas de pessoas vão para
   `judicial@solverone.com.br`; `integracao@` não é lido por ninguém.

Tribunais estaduais publicam diários muito maiores (o TJSP sozinho pode passar de 1 GB) e a regra de "ação nova"
ainda não foi calibrada neles.

## A planilha no Drive

Uma só: `<pasta compartilhada>\LexSuiteONE\LexSuiteONE.xlsx`.

- **Radar** (o robô escreve a cada rodada): a lista do dia, com as mesmas colunas da tela. A partir da 0.7.12, com
  cabeçalho azul-marinho fixo, filtro em todas as colunas, valores em R$ e o valor da causa acima do mínimo em latão
  claro; abre igual no Excel e no Google Planilhas.
- **Como usar**: o passo a passo da planilha, em português e inglês.
- **Preferências** e **Exclusões** (o escritório edita; o robô lê antes de cada rodada e preserva): valor mínimo,
  mínimo de ações da mesma empresa e janela de dias, capital que indica jurídico próprio, esconder ou não; e a lista de
  clientes e empresas que não devem aparecer (nome ou CNPJ e o motivo).
- Abas ocultas, usadas pelo suporte: **Controle** (`ativo`, `validade`, `versao_minima`, `mensagem`, `suporte`),
  **Log** (cada rodada), **Saúde** (o que o robô percebeu: Diário fora do ar, formato mudou, Receita sem resposta) e
  **Sobre** (versão, computador, pasta).

Também fica ali a página `Retrato da última leitura.html` (antes `Lista para abrir no celular.html`), uma foto da lista na última leitura que abre em qualquer lugar. Para editar no Google Planilhas,
abra o `.xlsx` e edite direto (modo de compatibilidade com Office); o Drive leva a mudança de volta para o
computador. Se a planilha estiver aberta e travada na hora de uma rodada, o robô tenta de novo a cada 2 minutos e grava sozinho quando ela for fechada.

## A tela

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
  escolhidos (padrão 20h e 8h, até 6, todos os dias ou de segunda a sexta; se o computador estava desligado, roda quando
  ele ligar). Ela roda o `RODAR.bat`; ao terminar, um aviso no canto da tela diz quantas ações novas chegaram.
  `AGENDAR.bat` faz o mesmo à mão (botão direito, Executar como administrador), se precisar. O DJEN libera o diário a partir das 19h.
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
