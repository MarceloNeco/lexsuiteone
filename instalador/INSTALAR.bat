@echo off
setlocal EnableExtensions DisableDelayedExpansion
title Instalacao do LexSuiteONE
rem Instalador de um arquivo so (fonte: instalador/INSTALAR.bat no repositorio lexsuiteone).
rem Baixa o pacote de judicial.solverone.com.br, confere a impressao digital (SHA-256) publicada, instala numa
rem pasta deste computador, prepara o que o programa precisa e cria o atalho. Nao pede senha de administrador.
rem Pode ser rodado de novo para atualizar ou consertar: configuracao, banco e lista ficam como estao.
rem Funciona aberto direto de dentro do .zip: nao depende de nenhum arquivo ao lado dele.
set "SITE=https://judicial.solverone.com.br"
set "CHAVE=d62d303a9f1361971d959e68a48e63d5c128d20b5874b08a6a7beeca825147ca"
set "CONTATO=judicial@solverone.com.br"
set "T=%TEMP%\LexSuiteONE-instalar"
echo.
echo  Instalando o LexSuiteONE neste computador
echo  -----------------------------------------
echo.

where curl.exe >nul 2>nul || goto sem_ferramentas
where tar.exe >nul 2>nul || goto sem_ferramentas
where certutil.exe >nul 2>nul || goto sem_ferramentas

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

if exist "%T%" rd /s /q "%T%"
mkdir "%T%" 2>nul

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
:sem_pasta
echo  Nao consegui criar a pasta do programa nem em C:\LexSuiteONE nem na pasta do usuario.
goto erro
:sem_internet
echo  Nao consegui baixar de judicial.solverone.com.br.
echo  Confira a internet ^(ou o proxy da empresa^) e rode o instalador de novo.
goto erro
:manifesto_ruim
echo  A informacao de versao baixada do site veio incompleta. Nada foi instalado.
goto erro
:hash_ruim
echo  O arquivo baixado nao confere com a impressao digital publicada. Nada foi instalado.
echo  Rode o instalador de novo; se repetir, avise o suporte.
goto erro
:falha_extrair
echo  Nao consegui descompactar o pacote em %DEST%.
goto erro
:sem_python
echo  Nao consegui preparar o que o programa precisa para funcionar.
echo  Confira a internet ^(o download vem do site oficial python.org^) e rode o instalador de novo.
goto erro
:erro
echo.
echo  Duvidas: %CONTATO%
rd /s /q "%T%" 2>nul
echo.
pause
exit /b 1
