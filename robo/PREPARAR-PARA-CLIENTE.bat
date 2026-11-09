@echo off
setlocal
cd /d "%~dp0"
echo  Este passo limpa os dados do SEU teste para a pasta virar o pacote do cliente.
echo  Apaga: config.json, lexsuite.db (e as copias lexsuite.db.antes-*), lexsuite_exemplo.db, saida\, diagnostico\, _anterior\, ultima_atualizacao.json
echo  Mantem: o robo, a pasta python (ja instalada) e a chave_publica.txt
echo.
set /p OK="Digite SIM para continuar: "
if /i not "%OK%"=="SIM" (
  echo  Nada foi apagado.
  pause
  exit /b 0
)
del /q config.json 2>nul
del /q lexsuite.db lexsuite_exemplo.db ultima_atualizacao.json 2>nul
del /q lexsuite.db.antes-* 2>nul
rmdir /s /q saida 2>nul
rmdir /s /q diagnostico 2>nul
rmdir /s /q _anterior 2>nul
rmdir /s /q lexsuite\__pycache__ 2>nul
if exist chave_privada.txt (
  echo.
  echo  ATENCAO: existe uma chave_privada.txt nesta pasta. Ela NAO pode ir para o cliente. Mova-a para outro lugar.
)
echo.
echo  Pronto. Copie esta pasta inteira para o pen drive. No cliente: ABRIR.bat.
pause
