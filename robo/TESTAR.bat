@echo off
setlocal
cd /d "%~dp0"
set "PY=python"
if exist "python\python.exe" set "PY=python\python.exe"
"%PY%" -m unittest discover -s testes
echo.
pause
