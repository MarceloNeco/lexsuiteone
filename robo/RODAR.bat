@echo off
setlocal
cd /d "%~dp0"
set "PY=python"
if exist "python\python.exe" set "PY=python\python.exe"
if "%~1"=="--agendado" (
  "%PY%" lexsuite_robo.py radar
  exit /b %errorlevel%
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
