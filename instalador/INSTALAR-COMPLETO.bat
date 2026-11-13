@echo off
setlocal EnableExtensions DisableDelayedExpansion
title Instalacao do LexSuiteONE (pacote completo)
rem Pacote completo (0.7.40, pedido do dono): o mesmo instalador, mas o programa, o Python e o icone vem na pasta "dados"
rem ao lado deste arquivo; nada e baixado da internet (so a conferencia do codigo de cliente). Para computadores com
rem antivirus ou rede restrita. Fonte: instalador/INSTALAR-COMPLETO.bat (o pacote e montado por ferramentas/marca.py).
rem Confere a impressao digital (SHA-256) do programa, instala numa pasta deste computador e cria o atalho.
rem Nao pede senha de administrador. Pode ser rodado de novo para atualizar ou consertar: configuracao e banco ficam.
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

set "DADOS=%~dp0dados"
if not exist "%DADOS%\pacote.zip" goto extrair_antes
if not exist "%DADOS%\python.zip" goto extrair_antes
if not exist "%DADOS%\instalar.txt" goto extrair_antes

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

echo  1 de 5  Lendo a versao que veio no pacote...
copy /y "%DADOS%\instalar.txt" "%T%\instalar.txt" >nul || goto manifesto_ruim
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

echo  2 de 5  Conferindo o %nome% %versao% que veio no pacote...
copy /y "%DADOS%\pacote.zip" "%T%\pacote.zip" >nul || goto falha_extrair

set "H="
for /f "skip=1 delims=" %%h in ('certutil.exe -hashfile "%T%\pacote.zip" SHA256') do if not defined H set "H=%%h"
if not defined H goto hash_ruim
set "H=%H: =%"
if /i not "%H%"=="%sha256%" goto hash_ruim
echo          Impressao digital conferida.

echo  3 de 5  Instalando em %DEST%...
rem 0.7.41 (KR Law, 13/Nov: o antivirus barrou o tar.exe em C:\LexSuiteONE): tenta com o PowerShell e, numa instalacao
rem nova, na pasta do usuario, antes de desistir. Onde ja ha um programa instalado (lexsuite.db), nao muda de pasta.
set "TENTOU=%DEST%"
call :extrair_pacote
if "%EXTRAIU%"=="sim" goto extraiu
if /i "%DEST%"=="%LOCALAPPDATA%\LexSuiteONE" goto falha_extrair
if exist "%DEST%\lexsuite.db" goto falha_extrair
echo          O Windows nao deixou gravar os arquivos em %DEST% ^(o antivirus pode ter bloqueado^).
echo          Tentando na pasta do usuario: %LOCALAPPDATA%\LexSuiteONE
set "DEST=%LOCALAPPDATA%\LexSuiteONE"
set "TENTOU=%TENTOU% e %DEST%"
if not exist "%DEST%\" mkdir "%DEST%" 2>nul
call :extrair_pacote
if not "%EXTRAIU%"=="sim" goto falha_extrair
:extraiu
if exist "%DEST%\chave_publica.txt" goto chave_ok
>"%DEST%\chave_publica.txt" echo %CHAVE%
:chave_ok
rem O programa le este arquivo na primeira abertura: o codigo ja vem preenchido e a identificacao e a mesma.
>"%DEST%\conta-inicial.json" echo {"codigo":"%CODIGO_OK%","instalacao":"%INST%"}

echo  4 de 5  Preparando o que o programa precisa para funcionar (so na primeira vez)...
if exist "%DEST%\python\python.exe" goto python_ok
mkdir "%DEST%\python" 2>nul
tar.exe -xf "%DADOS%\python.zip" -C "%DEST%\python" 2>nul
if not exist "%DEST%\python\python.exe" powershell.exe -NoProfile -Command "Expand-Archive -LiteralPath (Join-Path $env:DADOS 'python.zip') -DestinationPath (Join-Path $env:DEST 'python') -Force" >nul 2>nul
if not exist "%DEST%\python\python.exe" goto sem_python
rem A pasta do programa entra no caminho de modulos do Python portatil (o ".." aponta para a pasta do programa).
for %%f in ("%DEST%\python\python*._pth") do (
  findstr /x /c:".." "%%~f" >nul || echo ..>> "%%~f"
)
:python_ok
if not exist "%DEST%\python\python.exe" goto sem_python

echo  5 de 5  Criando o atalho "%nome%" na area de trabalho e no menu Iniciar...
if exist "%DADOS%\radar.ico" copy /y "%DADOS%\radar.ico" "%DEST%\radar.ico" >nul
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

:extrair_antes
echo  Este instalador precisa da pasta "dados" que vem junto dele no pacote completo.
echo.
echo  Faca assim:
echo    1. Feche esta janela.
echo    2. Clique com o botao direito no arquivo Instalar-LexSuiteONE-completo.zip e escolha "Extrair tudo".
echo    3. Na pasta que abrir, de dois cliques em INSTALAR.bat e, se o Windows perguntar, clique em Executar.
echo.
pause
exit /b 1
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
echo  Nao consegui falar com judicial.solverone.com.br para conferir o codigo de cliente.
echo  Confira a internet ^(ou peca a TI para liberar judicial.solverone.com.br e qvdvkqydhnadhewcidia.supabase.co^).
goto erro
:manifesto_ruim
set "ETAPA=manifesto instalar.txt"
set "DETALHE=arquivo=%arquivo% versao=%versao%"
echo  A informacao de versao do pacote veio incompleta. Nada foi instalado. Baixe o pacote completo de novo.
goto erro
:hash_ruim
set "ETAPA=impressao digital"
set "DETALHE=esperado=%sha256% obtido=%H%"
echo  O programa do pacote nao confere com a impressao digital. Nada foi instalado.
echo  Baixe o pacote completo de novo; se repetir, avise o suporte.
goto erro
:falha_extrair
set "ETAPA=descompactar"
set "DETALHE=errorlevel=%errorlevel% tar e powershell"
echo  Nao consegui descompactar o pacote ^(tentei em %TENTOU%^).
echo  O mais provavel e o antivirus ter bloqueado a criacao dos arquivos do programa.
echo  Peca para liberar a pasta C:\LexSuiteONE ^(e %LOCALAPPDATA%\LexSuiteONE^) no antivirus e rode o instalador de novo.
goto erro
:sem_python
set "ETAPA=preparar python"
echo  Nao consegui preparar o que o programa precisa para funcionar ^(descompactar o Python que veio no pacote^).
echo  Se o antivirus bloqueou, peca para liberar a pasta %DEST% e rode o instalador de novo.
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

:extrair_pacote
rem 1o o tar.exe do Windows; se o arquivo principal nao apareceu, o Expand-Archive do PowerShell (le T e DEST do ambiente).
rem Numa atualizacao, o arquivo principal antigo sai do caminho antes (e volta se nada extrair): so conta o que veio agora.
set "EXTRAIU=nao"
if exist "%DEST%\lexsuite_robo.py" move /y "%DEST%\lexsuite_robo.py" "%DEST%\lexsuite_robo.py.antes" >nul 2>nul
tar.exe -xf "%T%\pacote.zip" -C "%DEST%" 2>nul
if exist "%DEST%\lexsuite_robo.py" goto extrair_ok
powershell.exe -NoProfile -Command "Expand-Archive -LiteralPath (Join-Path $env:T 'pacote.zip') -DestinationPath $env:DEST -Force" >nul 2>nul
if exist "%DEST%\lexsuite_robo.py" goto extrair_ok
if exist "%DEST%\lexsuite_robo.py.antes" move /y "%DEST%\lexsuite_robo.py.antes" "%DEST%\lexsuite_robo.py" >nul 2>nul
goto :eof
:extrair_ok
del /q "%DEST%\lexsuite_robo.py.antes" 2>nul
set "EXTRAIU=sim"
goto :eof
