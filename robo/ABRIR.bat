@echo off
setlocal
cd /d "%~dp0"
set "PY=python"
if exist "python\python.exe" set "PY=python\python.exe"
if not exist "python\python.exe" (
  where python >nul 2>nul || (
    echo  Falta o Python. De dois cliques em INSTALAR-PYTHON.bat primeiro.
    pause
    exit /b 1
  )
)
echo  Abrindo o LexSuiteONE no navegador. A janela "LexSuiteONE" que vai abrir precisa ficar aberta enquanto voce usa a tela.
start "LexSuiteONE" "%PY%" lexsuite_robo.py app
exit /b 0
