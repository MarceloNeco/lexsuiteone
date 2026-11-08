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
echo  Abrindo o RADAR. A janela preta que vai abrir precisa ficar aberta enquanto voce usa a tela (pode minimizar).
start "LexSuiteONE" "%PY%" lexsuite_robo.py app
exit /b 0
