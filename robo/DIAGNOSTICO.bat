@echo off
setlocal
cd /d "%~dp0"
set "PY=python"
if exist "python\python.exe" set "PY=python\python.exe"
echo  Gerando o relatorio de diagnostico do Radar SP, sem dado de pessoa fisica...
"%PY%" lexsuite_robo.py diagnostico
if errorlevel 1 (
  echo.
  echo  Deu erro. Leia a mensagem acima. Se falar de "python", rode o INSTALAR-PYTHON.bat primeiro;
  echo  se falar de "diagnostico.py", baixe esse arquivo da subpasta lexsuite do Drive para a subpasta lexsuite daqui.
  pause
  exit /b 1
)
echo.
echo  Pronto. Vou abrir a pasta "diagnostico": arraste o radar-diagnostico.txt para a pasta do Drive do projeto.
start "" "diagnostico"
pause
