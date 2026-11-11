@echo off
setlocal
cd /d "%~dp0"
set "PY=python"
if exist "python\python.exe" set "PY=python\python.exe"
echo  Vou criar a leitura automatica no Agendador do Windows, com os horarios escolhidos na tela
echo  (Configuracao). Sem escolha, o padrao e de segunda a sexta as 20h00 e as 08h00. Se o computador estiver
echo  desligado na hora, a leitura acontece quando ele ligar.
echo.
"%PY%" lexsuite_robo.py agendar
if errorlevel 1 (
  echo.
  echo  Nao consegui criar a leitura automatica. Tente clicar com o botao direito neste arquivo e "Executar como administrador".
) else (
  echo.
  echo  Pronto. Para desligar: na tela, Configuracao, desmarque "Ler sozinho".
)
echo.
pause
