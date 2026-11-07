# LexSuiteONE · Radar Trabalhista — robô v0.7.0

Uma lista por dia: as ações novas contra empresas nos tribunais que você escolher (os 24 TRTs por padrão; também os
TJs, os TRFs, STJ e TST), uma por linha, com a ficha da empresa e do processo. Tudo roda no seu computador, sem
inteligência artificial e sem senha de ninguém. A planilha vai para a sua pasta do Google Drive.

## Instalar (Windows, sem instalar programa nenhum)

1. Descompacte o `.zip` numa pasta fácil, por exemplo `C:\LexSuiteONE`. A pasta pode ter qualquer nome; mantenha tudo
   junto, porque o robô guarda ali o `config.json`, o banco `lexsuite.db` e a pasta `saida`.
2. Dois cliques em **`INSTALAR-PYTHON.bat`** (só na primeira vez): baixa o Python portátil oficial para dentro da pasta.
3. Dois cliques em **`ABRIR.bat`**: abre a tela no navegador e uma janela "LexSuiteONE" que precisa ficar aberta.
4. Na primeira vez a tela abre em **Configuração**: digite o nome do escritório e escolha a **pasta compartilhada**
   (a tela lista as pastas do Google Drive para computador e do OneDrive que achou; "Testar pasta" confirma).
   **Salvar** cria a subpasta `LexSuiteONE` com a planilha de controle.
5. **Tribunais**: os 24 TRTs já vêm marcados. Dá para escolher por região, por estado, por ramo (Trabalhista,
   Estadual, Federal, Superior) ou "Selecionar todos". **Salvar e atualizar agora** começa a primeira rodada.

A primeira rodada baixa o diário do dia de cada tribunal escolhido (de 5 a 150 MB cada): os 24 TRTs levam de 30 a
60 minutos; depois, só o que é novo. O computador precisa estar **no Brasil**. Tribunais estaduais publicam diários
muito maiores (o TJSP sozinho pode passar de 1 GB) e a regra de "ação nova" ainda não foi calibrada neles.

## As duas planilhas na pasta compartilhada

Dentro de `<pasta compartilhada>\LexSuiteONE\`:

- **`LexSuiteONE - Radar.xlsx`**: o robô escreve a cada rodada. Aba **Radar** (a lista do dia, com as mesmas colunas
  da tela) e abas ocultas **Log** (cada rodada: quando, versão, tribunais, quantas publicações, quantas ações,
  erro), **Saúde** (o que o robô percebeu: Diário fora do ar, formato mudou, Receita sem resposta) e **Sobre**
  (versão, computador, pasta). Também fica ali a página `LexSuiteONE - Radar.html`, que abre em qualquer lugar.
- **`LexSuiteONE - Controle.xlsx`**: só gente escreve; o robô lê antes de cada rodada. Aba **Preferências** (valor
  mínimo, mínimo de ações da mesma empresa e janela de dias, capital que indica jurídico próprio, esconder ou não),
  aba **Exclusões** (clientes e empresas que não devem aparecer: nome ou CNPJ e o motivo) e aba oculta **Controle**
  (`ativo`, `validade`, `versao_minima`, `mensagem`, `suporte`), usada pelo suporte.

Compartilhe a subpasta `LexSuiteONE` com o suporte uma vez (botão direito na pasta, "Compartilhar", como editor).
Como o robô nunca grava na planilha de controle e as pessoas nunca gravam na do Radar, não há conflito de sincronização.
Para editar a planilha de controle no Google Planilhas, abra o `.xlsx` e edite direto (modo de compatibilidade com
Office); o Drive leva a mudança de volta para o computador.

## A tela

- **Uma linha por ação:** tribunal, empresa, setor, porte, cidade, vara e o valor da causa (ou "a conferir").
- **Clique na linha, a ficha abre:** cada dado numa linha própria, sempre presente; o que falta aparece como
  "não informado no cadastro" (a Receita não tem) ou "não capturado" (está no PJe, atrás do captcha).
- **Filtros:** acima do valor mínimo; sem jurídico próprio provável; mostrar excluídas; um tribunal ou todos.
  **Período:** último dia, 3, 7, 15 ou 30 dias. **Exportar planilha** gera um `.csv` com o que está na tela.
- **Valor da causa:** o Diário não traz; está na consulta pública do PJe atrás de um captcha. Botão "Abrir consulta no
  PJe", "Copiar número", e o campo para digitar o valor (fica no navegador e sai na planilha exportada).
- **Configuração:** escritório, pasta compartilhada, versão instalada, chave de atualização e o botão
  "Verificar atualização".

## Rodar sozinho

- **`AGENDAR.bat`**: cria duas tarefas no Agendador do Windows (19:40 e 07:10) que rodam o `RODAR.bat` com o
  computador ligado. O DJEN libera o diário a partir das 19h.
- **`RODAR.bat`**: uma rodada sem a tela, com os tribunais salvos. Também grava `saida\radar\radar.html`.
- **`DIAGNOSTICO.bat`**: relatório `diagnostico\radar-diagnostico.txt` do que o robô guardou, sem dado de pessoa física.

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
