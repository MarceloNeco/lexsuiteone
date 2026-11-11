@echo off
setlocal
cd /d "%~dp0"
set "PY=python"
if exist "python\python.exe" set "PY=python\python.exe"
echo.
echo  1 = Gerar o relatorio de diagnostico (sem dado de pessoa fisica)
echo  2 = Encerrar o RADAR (se a tela travou; interrompe uma leitura em andamento)
choice /c 12 /n /m "  Digite 1 ou 2: "
if errorlevel 2 goto encerrar
echo  Gerando o relatorio de diagnostico, sem dado de pessoa fisica...
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
exit /b 0

:encerrar
"%PY%" lexsuite_robo.py parar
echo.
echo  Pronto. Para abrir de novo, use o atalho do RADAR.
pause
exit /b 0
