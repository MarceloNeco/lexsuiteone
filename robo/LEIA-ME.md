# LexSuiteONE · RADAR JUDICIAL — robô v0.7.8 (frente trabalhista)

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
3. Na primeira vez a tela abre um **passo a passo de boas-vindas**: seu nome e seu papel no escritório (a tela e o
   manual passam a falar com você), o nome do escritório, a **pasta compartilhada** (a tela lista as pastas do Google
   Drive para computador e do OneDrive que achou; "Testar pasta" confirma) e a opção **rodar sozinho todo dia**
   (19:40 e 07:10, já marcada). "Começar a primeira rodada" salva tudo, cria a planilha `LexSuiteONE.xlsx` no Drive,
   agenda as rodadas e dispara a primeira. Tudo isso pode ser mudado depois em **Configuração**.
4. **Atualizar agora**: os 24 TRTs já vêm escolhidos (em **Tribunais** dá para mudar: por região, por estado, por
   ramo ou "Selecionar todos"). A primeira rodada baixa o diário do dia de cada tribunal (de 5 a 150 MB cada): os 24
   TRTs levam de 30 a 60 minutos; depois, só o que é novo. O computador precisa estar **no Brasil**.
5. No Drive, dê acesso de editor à subpasta `LexSuiteONE` para `integracao@solverone.com.br`, a conta de sistemas da
   SolverONE (botão direito, Compartilhar). É a única etapa que o robô não faz sozinho. Dúvidas de pessoas vão para
   `judicial@solverone.com.br`; `integracao@` não é lido por ninguém.

Tribunais estaduais publicam diários muito maiores (o TJSP sozinho pode passar de 1 GB) e a regra de "ação nova"
ainda não foi calibrada neles.

## A planilha no Drive

Uma só: `<pasta compartilhada>\LexSuiteONE\LexSuiteONE.xlsx`.

- **Radar** (o robô escreve a cada rodada): a lista do dia, com as mesmas colunas da tela.
- **Preferências** e **Exclusões** (o escritório edita; o robô lê antes de cada rodada e preserva): valor mínimo,
  mínimo de ações da mesma empresa e janela de dias, capital que indica jurídico próprio, esconder ou não; e a lista de
  clientes e empresas que não devem aparecer (nome ou CNPJ e o motivo).
- Abas ocultas, usadas pelo suporte: **Controle** (`ativo`, `validade`, `versao_minima`, `mensagem`, `suporte`),
  **Log** (cada rodada), **Saúde** (o que o robô percebeu: Diário fora do ar, formato mudou, Receita sem resposta) e
  **Sobre** (versão, computador, pasta).

Também fica ali a página `LexSuiteONE - Radar.html`, que abre em qualquer lugar. Para editar no Google Planilhas,
abra o `.xlsx` e edite direto (modo de compatibilidade com Office); o Drive leva a mudança de volta para o
computador. Se a planilha estiver aberta e travada na hora de uma rodada, o robô deixa como está e tenta na seguinte.

## A tela

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

- A opção "rodar sozinho" da Configuração cria duas tarefas no Agendador do Windows (19:40 e 07:10) que rodam o
  `RODAR.bat` com o computador ligado. `AGENDAR.bat` faz o mesmo à mão, se precisar. O DJEN libera o diário a partir das 19h.
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
