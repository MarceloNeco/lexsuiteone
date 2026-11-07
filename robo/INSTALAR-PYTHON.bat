@echo off
setlocal
cd /d "%~dp0"
echo.
echo  LexSuiteONE - Python portatil (sem instalador, sem senha de administrador)
echo.
if exist "python\python.exe" (
  echo  O Python portatil ja esta nesta pasta. Nada a fazer. Pode dar dois cliques em ABRIR.bat.
  goto fim
)
set "URL=https://www.python.org/ftp/python/3.13.9/python-3.13.9-embed-amd64.zip"
echo  Baixando o Python 3.13 portatil (11 MB) do site oficial python.org...
where curl.exe >nul 2>nul
if %errorlevel%==0 (
  curl.exe -L --fail --retry 3 -o python-embed.zip "%URL%"
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol='Tls12'; Invoke-WebRequest -Uri '%URL%' -OutFile 'python-embed.zip'"
)
if not exist "python-embed.zip" (
  echo.
  echo  Nao consegui baixar. Confira a internet ^(ou o proxy da empresa^) e tente de novo.
  echo  Se nao der, baixe este arquivo no navegador e ponha nesta pasta com o nome python-embed.zip:
  echo  %URL%
  goto fim
)
mkdir python 2>nul
where tar.exe >nul 2>nul
if %errorlevel%==0 (
  tar.exe -xf python-embed.zip -C python
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -Path 'python-embed.zip' -DestinationPath 'python' -Force"
)
del python-embed.zip 2>nul
rem A pasta do robo entra no caminho de modulos do Python portatil (o ".." aponta para esta pasta).
for %%f in (python\python*._pth) do (
  findstr /x /c:".." "%%f" >nul || echo ..>> "%%f"
)
if exist "python\python.exe" (
  echo.
  echo  Pronto. Agora de dois cliques em ABRIR.bat.
) else (
  echo.
  echo  Algo deu errado ao descompactar. Apague a pasta "python" e rode este arquivo de novo.
)
:fim
echo.
if /i "%~1"=="--silencioso" exit /b 0
pause
