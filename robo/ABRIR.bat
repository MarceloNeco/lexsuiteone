@echo off
setlocal
cd /d "%~dp0"
set "PY=python"
if exist "python\python.exe" set "PY=python\python.exe"
if not exist "python\python.exe" (
  where python >nul 2>nul
  if errorlevel 1 (
    echo  Primeira vez: instalando o Python portatil dentro desta pasta...
    call INSTALAR-PYTHON.bat --silencioso
    if exist "python\python.exe" set "PY=python\python.exe"
  )
)
if not exist "python\python.exe" (
  where python >nul 2>nul || (
    echo  Nao consegui preparar o Python. Rode o INSTALAR-PYTHON.bat e leia a mensagem.
    pause
    exit /b 1
  )
)
rem 0.7.29 (dono): sem janela preta. A tela abre sozinha; para sair, menu Sair na tela.
rem Suporte: ABRIR.bat --ver abre com a janela preta, como antes.
if /i "%~1"=="--ver" (
  echo  Abrindo o RADAR com a janela preta (modo suporte^). Deixe esta janela aberta enquanto usa a tela.
  start "LexSuiteONE" "%PY%" lexsuite_robo.py app
  exit /b 0
)
set "PYW=%PY%"
if exist "python\pythonw.exe" set "PYW=python\pythonw.exe"
if not exist "python\pythonw.exe" (
  where pythonw >nul 2>nul && set "PYW=pythonw"
)
start "" "%PYW%" lexsuite_robo.py app
exit /b 0
