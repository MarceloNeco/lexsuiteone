# Roteiro de instalação no cliente (quinta-feira) — LexSuiteONE v0.7.0

## Antes de sair de casa (uma vez)

1. Gerar o par de chaves da atualização **no seu computador** (não no do cliente):
   `python ferramentas\publicar.py gerar-chaves` (a pasta `ferramentas` está no pacote "só para desenvolvedor").
   Guarde `chave_privada.txt` fora do Drive (pen drive ou cofre de senhas). Copie `chave_publica.txt` para a pasta do
   robô que você vai levar. Anote a "impressão" que o comando mostra: ela aparece na tela do cliente e serve para conferir.
2. Testar o pacote inteiro em casa, do zero, numa pasta nova: `INSTALAR-PYTHON.bat`, `ABRIR.bat`, Configuração com a
   sua pasta do Drive, "Salvar e atualizar agora" com 2 TRTs. Conferir que apareceram `LexSuiteONE - Radar.xlsx` e
   `LexSuiteONE - Controle.xlsx` na pasta do Drive e que abrem no Google Planilhas.
3. **A planilha não precisa ser levada.** O robô cria a "LexSuiteONE - Controle.xlsx" quando você clica em Salvar na
   Configuração (no Drive de quem está instalando) e a "LexSuiteONE - Radar.xlsx" na primeira rodada. O seu teste em
   casa cria as suas, no seu Drive; no cliente nascem outras, no Drive dele.
4. Depois do teste em casa, dois cliques em **`PREPARAR-PARA-CLIENTE.bat`**: ele apaga o `config.json`, o banco e as
   saídas do seu teste e mantém o Python já instalado e a `chave_publica.txt`. Copie a pasta inteira para um pen drive:
   no cliente não precisa nem baixar o Python.

## No cliente (30 a 45 minutos, mais o tempo da primeira rodada)

Perguntas antes de começar:
- O computador tem o **Google Drive para computador** instalado? (Ícone na bandeja; pasta "Meu Drive" no Explorador.)
  Se não tiver, instale pelo site do Google Drive com a conta dele, ou use o OneDrive.
- Qual conta do Google é a do escritório? É nela que a planilha vai morar.
- O computador fica ligado às 19:40 e às 07:10? (Para o `AGENDAR.bat`.)

Passos:
1. Copiar a pasta do pen drive para `C:\LexSuiteONE` (ou descompactar o zip do Drive lá dentro).
2. Se a pasta `python` não veio junto: `INSTALAR-PYTHON.bat` → esperar "Pronto".
3. `ABRIR.bat` → a tela abre. Em **Configuração**: nome do escritório; pasta compartilhada = "Meu Drive" dele;
   "Testar pasta" → "Salvar".
4. No Explorador, dentro de "Meu Drive", botão direito na subpasta **LexSuiteONE** → Compartilhar → o seu e-mail de
   serviço (integracao@solverone.com.br, ou o seu Gmail até a conta existir) como **Editor**.
5. Tribunais: deixar os 24 TRTs (ou reduzir a 2 ou 3 para a primeira rodada ser rápida) → "Salvar e atualizar agora".
   Enquanto roda, mostrar a ficha, os filtros, a exportação e a planilha no Drive.
6. `AGENDAR.bat` (botão direito → Executar como administrador, se pedir).
7. Deixar anotado para ele: `ABRIR.bat` abre a tela; a janela "LexSuiteONE" pode ficar minimizada; a planilha de
   controle é dele para editar (Exclusões e Preferências); o suporte vê o Log pela pasta compartilhada.

## Depois, do seu lado

- Abrir a planilha compartilhada: aba Log (rodou? quantas?), aba Saúde (algum aviso?), aba Sobre (versão, impressão da chave).
- Para desligar, avisar ou exigir versão: editar a aba Controle da planilha de controle.
- Para publicar uma versão: `python ferramentas\publicar.py empacotar --versao 0.7.1 --chave <sua chave privada>` e
  copiar o zip e o `versao.json` para a subpasta `atualizacao` da pasta compartilhada do cliente. O robô instala na
  próxima abertura ou quando ele clicar em "Verificar atualização".
