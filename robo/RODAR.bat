@echo off
setlocal
cd /d "%~dp0"
set "PY=python"
if exist "python\python.exe" set "PY=python\python.exe"
set "PYW=%PY%"
if exist "python\pythonw.exe" set "PYW=python\pythonw.exe"
rem 0.7.29: a leitura automatica roda sem janela preta (tarefas antigas ainda chamam este arquivo ate o programa abrir)
if "%~1"=="--agendado" (
  start "" "%PYW%" lexsuite_robo.py radar --agendado
  exit /b 0
)
if "%~1"=="" (
  "%PY%" lexsuite_robo.py radar
) else (
  "%PY%" lexsuite_robo.py %*
)
if errorlevel 1 (
  echo.
  echo  Deu erro. Leia a mensagem acima. Se ela falar de "python", rode o INSTALAR-PYTHON.bat primeiro;
  echo  se falar de "Brasil", o computador precisa estar no Brasil para ler o Diario.
)
echo.
pause
