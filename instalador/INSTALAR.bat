@echo off
setlocal EnableExtensions DisableDelayedExpansion
title Instalacao do LexSuiteONE
rem Instalador de um arquivo so (fonte: instalador/INSTALAR.bat no repositorio lexsuiteone).
rem Baixa o pacote de judicial.solverone.com.br, confere a impressao digital (SHA-256) publicada, instala numa
rem pasta deste computador, prepara o que o programa precisa e cria o atalho. Nao pede senha de administrador.
rem Pode ser rodado de novo para atualizar ou consertar: configuracao, banco e lista ficam como estao.
rem Funciona aberto direto de dentro do .zip: nao depende de nenhum arquivo ao lado dele.
rem Se falhar, avisa a SolverONE (etapa, versao do Windows e detalhe tecnico; nada pessoal) para o diagnostico.
set "SITE=https://judicial.solverone.com.br"
set "CHAVE=d62d303a9f1361971d959e68a48e63d5c128d20b5874b08a6a7beeca825147ca"
set "CONTATO=judicial@solverone.com.br"
set "T=%TEMP%\LexSuiteONE-instalar"
set "REGISTRO=https://qvdvkqydhnadhewcidia.supabase.co/functions/v1/lex-conta"
set "ETAPA="
set "DETALHE="
set "WINVER="
for /f "tokens=2 delims=[]" %%v in ('ver') do set "WINVER=%%v"
echo.
echo  Instalando o LexSuiteONE neste computador
echo  -----------------------------------------
echo.

where curl.exe >nul 2>nul || goto sem_ferramentas
where tar.exe >nul 2>nul || goto sem_ferramentas
where certutil.exe >nul 2>nul || goto sem_ferramentas

if exist "%T%" rd /s /q "%T%"
mkdir "%T%" 2>nul

rem Codigo de cliente, antes de tudo: sem codigo valido nada e instalado, e todo aviso de erro deste computador
rem chega a SolverONE com o codigo do escritorio e a identificacao (aleatoria) desta instalacao.
set "INST="
set "CODIGO_OK="
for /f "usebackq delims=" %%g in (`powershell.exe -NoProfile -Command "[guid]::NewGuid().ToString('N').Substring(0,16)"`) do set "INST=%%g"
echo  Digite o codigo de cliente que veio no e-mail de boas-vindas (exemplo: LEX-ABCD-2345).
echo  Para colar, clique com o botao direito dentro desta janela.
echo.
set "TENTATIVAS=0"
:pedir_codigo
set "CODIGO="
set /p "CODIGO=  Codigo de cliente: "
if not defined CODIGO goto pedir_codigo
set "CODIGO=%CODIGO: =%"
echo(%CODIGO%| findstr /r /i /x /c:"LEX-[A-Z0-9][A-Z0-9][A-Z0-9][A-Z0-9]-[A-Z0-9][A-Z0-9][A-Z0-9][A-Z0-9]" >nul || goto codigo_formato
set "CODIGO_OK=%CODIGO%"
curl.exe -s -m 20 -o "%T%\conta.txt" -X POST "%REGISTRO%" -H "Content-Type: application/json" -d "{\"codigo\":\"%CODIGO_OK%\",\"instalacao\":\"%INST%\",\"versao\":\"instalador\"}" || goto sem_internet
findstr /r /c:"ok.:true" "%T%\conta.txt" >nul && goto codigo_ok
findstr /c:"aceite_pendente" "%T%\conta.txt" >nul && goto aceite_pendente
findstr /c:"codigo_desconhecido" "%T%\conta.txt" >nul && goto codigo_desconhecido
findstr /c:"desativado" "%T%\conta.txt" >nul && goto licenca_inativa
findstr /c:"vencido" "%T%\conta.txt" >nul && goto licenca_inativa
goto sem_internet
:codigo_formato
echo  O codigo tem o formato LEX-XXXX-XXXX. Tente de novo.
goto mais_uma
:codigo_desconhecido
echo  Este codigo nao existe. Confira no e-mail de boas-vindas e tente de novo.
:mais_uma
set /a TENTATIVAS+=1
if %TENTATIVAS% GEQ 3 goto codigo_esgotado
goto pedir_codigo
:aceite_pendente
echo  Codigo confirmado. Falta o aceite dos termos pelo responsavel do escritorio:
echo  abra o link "Aceitar os termos" do e-mail de boas-vindas. A instalacao continua;
echo  o programa so le o Diario depois do aceite (a tela mostra o link).
echo.
goto destino_inicio
:codigo_ok
echo  Codigo confirmado.
echo.

:destino_inicio
rem Pasta de destino: C:\LexSuiteONE; se o Windows nao deixar, a pasta do usuario.
set "DEST=C:\LexSuiteONE"
if exist "%LOCALAPPDATA%\LexSuiteONE\lexsuite_robo.py" if not exist "C:\LexSuiteONE\lexsuite_robo.py" set "DEST=%LOCALAPPDATA%\LexSuiteONE"
if not exist "%DEST%\" mkdir "%DEST%" 2>nul
(type nul > "%DEST%\.teste-escrita") 2>nul
if exist "%DEST%\.teste-escrita" goto destino_ok
set "DEST=%LOCALAPPDATA%\LexSuiteONE"
if not exist "%DEST%\" mkdir "%DEST%" 2>nul
(type nul > "%DEST%\.teste-escrita") 2>nul
if not exist "%DEST%\.teste-escrita" goto sem_pasta
:destino_ok
del "%DEST%\.teste-escrita" 2>nul

echo  1 de 5  Consultando a versao mais nova...
curl.exe -fsSL --retry 3 -o "%T%\instalar.txt" "%SITE%/atualizacao/instalar.txt" || goto sem_internet
set "versao="
set "arquivo="
set "sha256="
set "nome="
for /f "usebackq tokens=1,* delims==" %%a in ("%T%\instalar.txt") do (
  if /i "%%a"=="versao" set "versao=%%b"
  if /i "%%a"=="arquivo" set "arquivo=%%b"
  if /i "%%a"=="sha256" set "sha256=%%b"
  if /i "%%a"=="nome" set "nome=%%b"
)
if not defined arquivo goto manifesto_ruim
if not defined sha256 goto manifesto_ruim
if not defined nome set "nome=LexSuiteONE"
echo(%arquivo%| findstr /r /x /c:"LexSuiteONE-RADAR-atualizacao-[0-9][0-9.]*\.zip" /c:"LEXSUITE-ONE-ROBO-[0-9][0-9.]*\.zip" >nul || goto manifesto_ruim

echo  2 de 5  Baixando o %nome% %versao%...
curl.exe -fL --retry 3 -o "%T%\pacote.zip" "%SITE%/atualizacao/%arquivo%" || goto sem_internet

set "H="
for /f "skip=1 delims=" %%h in ('certutil.exe -hashfile "%T%\pacote.zip" SHA256') do if not defined H set "H=%%h"
if not defined H goto hash_ruim
set "H=%H: =%"
if /i not "%H%"=="%sha256%" goto hash_ruim
echo          Impressao digital conferida.

echo  3 de 5  Instalando em %DEST%...
tar.exe -xf "%T%\pacote.zip" -C "%DEST%" || goto falha_extrair
if not exist "%DEST%\lexsuite_robo.py" goto falha_extrair
if exist "%DEST%\chave_publica.txt" goto chave_ok
>"%DEST%\chave_publica.txt" echo %CHAVE%
:chave_ok
rem O programa le este arquivo na primeira abertura: o codigo ja vem preenchido e a identificacao e a mesma.
>"%DEST%\conta-inicial.json" echo {"codigo":"%CODIGO_OK%","instalacao":"%INST%"}

echo  4 de 5  Preparando o que o programa precisa para funcionar (11 MB, so na primeira vez)...
call "%DEST%\INSTALAR-PYTHON.bat" --silencioso >nul
if not exist "%DEST%\python\python.exe" goto sem_python

echo  5 de 5  Criando o atalho "%nome%" na area de trabalho e no menu Iniciar...
curl.exe -fsSL -o "%DEST%\radar.ico" "%SITE%/radar.ico" 2>nul
set "ICONE=%DEST%\radar.ico"
if not exist "%ICONE%" set "ICONE=%SystemRoot%\System32\shell32.dll,13"
powershell.exe -NoProfile -Command "$w = New-Object -ComObject WScript.Shell; foreach ($p in @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'))) { $s = $w.CreateShortcut((Join-Path $p '%nome%.lnk')); $s.TargetPath = '%DEST%\ABRIR.bat'; $s.WorkingDirectory = '%DEST%'; $s.IconLocation = '%ICONE%'; $s.Description = 'Abre o %nome%'; $s.WindowStyle = 7; $s.Save() }"
if errorlevel 1 echo          Nao consegui criar o atalho. Abra pelo ABRIR.bat em %DEST%.

rd /s /q "%T%" 2>nul
echo.
echo  Pronto. Daqui em diante, abra pelo atalho "%nome%" na area de trabalho.
echo  A tela vai abrir agora no navegador.
echo.
call "%DEST%\ABRIR.bat" >nul
timeout /t 20
exit /b 0

:sem_ferramentas
echo  Este Windows nao tem as ferramentas basicas que o instalador usa ^(curl, tar e certutil^).
echo  Ele precisa de Windows 10 atualizado ou Windows 11.
goto erro
:codigo_esgotado
set "ETAPA=codigo de cliente"
set "DETALHE=3 tentativas sem codigo valido"
echo  Nao foi possivel confirmar o codigo de cliente.
goto erro
:licenca_inativa
set "ETAPA=licenca inativa"
echo  A licenca deste escritorio nao esta ativa.
goto erro
:sem_pasta
set "ETAPA=pasta de destino"
echo  Nao consegui criar a pasta do programa nem em C:\LexSuiteONE nem na pasta do usuario.
goto erro
:sem_internet
set "ETAPA=download"
echo  Nao consegui baixar de judicial.solverone.com.br.
echo  Confira a internet ^(ou o proxy da empresa^) e rode o instalador de novo.
goto erro
:manifesto_ruim
set "ETAPA=manifesto instalar.txt"
set "DETALHE=arquivo=%arquivo% versao=%versao%"
echo  A informacao de versao baixada do site veio incompleta. Nada foi instalado.
goto erro
:hash_ruim
set "ETAPA=impressao digital"
set "DETALHE=esperado=%sha256% obtido=%H%"
echo  O arquivo baixado nao confere com a impressao digital publicada. Nada foi instalado.
echo  Rode o instalador de novo; se repetir, avise o suporte.
goto erro
:falha_extrair
set "ETAPA=descompactar"
set "DETALHE=errorlevel=%errorlevel%"
echo  Nao consegui descompactar o pacote em %DEST%.
goto erro
:sem_python
set "ETAPA=preparar python"
echo  Nao consegui preparar o que o programa precisa para funcionar.
echo  Confira a internet ^(o download vem do site oficial python.org^) e rode o instalador de novo.
goto erro
:erro
if defined ETAPA (
  curl.exe -s -m 15 -X POST "%REGISTRO%" -H "Content-Type: application/json" -d "{\"acao\":\"registro\",\"origem\":\"instalador\",\"etapa\":\"%ETAPA%\",\"versao\":\"%versao%\",\"windows\":\"%WINVER%\",\"mensagem\":\"%DETALHE%\",\"codigo\":\"%CODIGO_OK%\",\"instalacao\":\"%INST%\"}" >nul 2>&1
  echo.
  echo  A SolverONE recebeu um aviso tecnico deste erro ^(sem dados pessoais^).
)
echo.
echo  Duvidas: %CONTATO%
rd /s /q "%T%" 2>nul
echo.
pause
exit /b 1
