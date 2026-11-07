@echo off
setlocal
cd /d "%~dp0.."
echo LexSuiteONE - kit do suporte: gerar o par de chaves de assinatura (uma vez so).
if not exist "python\python.exe" (
  echo.
  echo Falta o Python portatil. Rode o ABRIR.bat desta pasta uma vez e tente de novo.
  pause
  exit /b 1
)
set "DESTINO=%USERPROFILE%\Documents\SolverONE-chaves"
if exist "%DESTINO%\chave_privada.txt" (
  echo.
  echo Ja existe uma chave privada em "%DESTINO%". Nao vou sobrescrever.
  echo Se quiser gerar outra, mova a antiga para outro lugar antes.
  pause
  exit /b 1
)
mkdir "%DESTINO%" 2>nul
"python\python.exe" "ferramentas\publicar.py" gerar-chaves --pasta "%DESTINO%"
echo.
echo Pronto.
echo  - chave_privada.txt ficou em "%DESTINO%". NUNCA copie para o Drive, para o chat ou para o pacote.
echo    Guarde uma copia do conteudo no seu cofre de senhas.
echo  - chave_publica.txt esta na mesma pasta. Abra no Bloco de Notas e cole o conteudo no chat do Claude.
start "" "%DESTINO%"
pause
