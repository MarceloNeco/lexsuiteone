@echo off
setlocal
cd /d "%~dp0"
echo  Vou criar duas tarefas no Agendador do Windows para o robo rodar sozinho:
echo   - LexSuiteONE Radar (noite): todo dia as 19:40
echo   - LexSuiteONE Radar (manha): todo dia as 07:10
echo  Elas rodam o RODAR.bat desta pasta, so com o computador ligado.
echo.
schtasks /create /f /tn "LexSuiteONE Radar (noite)" /sc daily /st 19:40 /tr "\"%~dp0RODAR.bat\" --agendado"
schtasks /create /f /tn "LexSuiteONE Radar (manha)" /sc daily /st 07:10 /tr "\"%~dp0RODAR.bat\" --agendado"
if errorlevel 1 (
  echo.
  echo  Nao consegui criar as tarefas. Tente clicar com o botao direito neste arquivo e "Executar como administrador".
) else (
  echo.
  echo  Pronto. Para desfazer: abra o Agendador de Tarefas do Windows e apague as duas tarefas "LexSuiteONE Radar".
)
echo.
pause
