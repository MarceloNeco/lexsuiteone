@echo off
setlocal EnableExtensions DisableDelayedExpansion
title Instalacao do LexSuiteONE (pacote completo)
rem Pacote completo (0.7.40, pedido do dono): o mesmo instalador, mas o programa, o Python e o icone vem na pasta "dados"
rem ao lado deste arquivo; nada e baixado da internet (so a conferencia do codigo de cliente). Para computadores com
rem antivirus ou rede restrita. Fonte: instalador/INSTALAR-COMPLETO.bat (o pacote e montado por ferramentas/marca.py).
rem Confere a impressao digital (SHA-256) do programa, instala numa pasta deste computador e cria o atalho.
rem Nao pede senha de administrador. Pode ser rodado de novo para atualizar ou consertar: configuracao e banco ficam.
rem Se falhar, avisa a SolverONE (etapa, versao do Windows e detalhe tecnico; nada pessoal) para o diagnostico.
set "SITE=https://judicial.solverone.com.br"
set "CHAVE=d62d303a9f1361971d959e68a48e63d5c128d20b5874b08a6a7beeca825147ca"
set "CONTATO=judicial@solverone.com.br"
set "T=%TEMP%\LexSuiteONE-instalar"
set "REGISTRO=https://qvdvkqydhnadhewcidia.supabase.co/functions/v1/lex-conta"
set "ETAPA="
set "DETALHE="
set "WINVER="
for /f "tokens=2 delims=[]" %%v in ('ver') do set "WINVER=%%v"
echo.
echo  Instalando o LexSuiteONE neste computador
echo  -----------------------------------------
echo.

rem 0.7.47 (desenho "CNJ fora e antivirus", 2.1): aberto de dentro do .zip, sem "Extrair tudo", o Windows poe este arquivo
rem sozinho numa pasta temporaria, e o antivirus costuma barrar o que roda dali. Pede para extrair antes.
set "AQUI=%~dp0"
set "NO_TEMP="
call set "SEM_T=%%AQUI:%TEMP%=%%"
if not "%SEM_T%"=="%AQUI%" set "NO_TEMP=1"
if not "%AQUI:\AppData\Local\Temp\=%"=="%AQUI%" set "NO_TEMP=1"
if defined NO_TEMP if not "%AQUI:.zip=%"=="%AQUI%" goto dentro_do_zip
set "AV="
set "AVON="
set "AVON_J="
set "SODEF="
set "FW="
set "SINAL="

set "DADOS=%~dp0dados"
if not exist "%DADOS%\pacote.zip" goto extrair_antes
if not exist "%DADOS%\python.zip" goto extrair_antes
if not exist "%DADOS%\instalar.txt" goto extrair_antes

where curl.exe >nul 2>nul || goto sem_ferramentas
where tar.exe >nul 2>nul || goto sem_ferramentas
where certutil.exe >nul 2>nul || goto sem_ferramentas

if exist "%T%" rd /s /q "%T%"
mkdir "%T%" 2>nul

rem 0.7.47 (2.2): passo 0, antes de baixar. Detectar, explicar e orientar; nunca contornar o antivirus.
echo  Conferindo este computador antes de instalar...
rem (b) antivirus e firewall pela Central de Seguranca do Windows (sem administrador); sem ela: "nao identificado"
set "IDENT=0"
powershell.exe -NoProfile -Command "$ErrorActionPreference='SilentlyContinue'; $a=$null; try { $a=@(Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct -ErrorAction Stop); 'IDENT=1' } catch { 'IDENT=0' }; function On($p) { (($p.productState -shr 8) -band 255) -in 16,17 }; $o=@($a | Where-Object { ($_.displayName -notmatch 'Defender|^Windows' -or $_.displayName -match 'Bitdefender') }); $p=@(@($o | Where-Object { On $_ }) + @($a | Where-Object { On $_ }) + $o + @($a) | Where-Object { $_ }) | Select-Object -First 1; if ($p) { 'AV=' + ($p.displayName -replace '[^A-Za-z0-9 .,+-]', ''); if (On $p) { 'AVON=sim' } else { 'AVON=nao' }; if ($p.displayName -match 'Defender|^Windows' -and $p.displayName -notmatch 'Bitdefender') { 'SODEF=1' } }; $f=$null; try { $f=@(Get-CimInstance -Namespace root/SecurityCenter2 -ClassName FirewallProduct -ErrorAction Stop) | Select-Object -First 1 } catch {}; if ($f) { 'FW=' + ($f.displayName -replace '[^A-Za-z0-9 .,+-]', '') }" > "%T%\av.txt" 2>nul
if exist "%T%\av.txt" for /f "usebackq tokens=1,* delims==" %%a in ("%T%\av.txt") do (
  if /i "%%a"=="IDENT" set "IDENT=%%b"
  if /i "%%a"=="AV" set "AV=%%b"
  if /i "%%a"=="AVON" set "AVON=%%b"
  if /i "%%a"=="SODEF" set "SODEF=%%b"
  if /i "%%a"=="FW" set "FW=%%b"
)
if "%AVON%"=="sim" set "AVON_J=sim"
if "%AVON%"=="nao" set "AVON_J=n\u00e3o"
rem aviso "fornecedor desconhecido" (SmartScreen): este arquivo veio da internet; nao e bloqueio
set "MARCA_INTERNET="
more < "%~f0:Zone.Identifier" >nul 2>&1 && set "MARCA_INTERNET=1"
rem (d) saida para os nossos enderecos (pedido leve, sem baixar nada)
set "NET_SITE=0"
set "NET_NUVEM=0"
set "NET_CNJ=0"
curl.exe -s -o nul -m 15 "%SITE%/" && set "NET_SITE=1"
curl.exe -s -o nul -m 15 "%REGISTRO%" && set "NET_NUVEM=1"
curl.exe -s -o nul -m 15 "https://comunicaapi.pje.jus.br/api/v1/comunicacao?itensPorPagina=5" && set "NET_CNJ=1"
if "%NET_SITE%%NET_NUVEM%%NET_CNJ%"=="000" goto sem_internet_antes
if not "%NET_SITE%%NET_NUVEM%"=="11" goto rede_recusada
if "%NET_CNJ%"=="0" echo  Aviso: o endereco do CNJ ^(comunicaapi.pje.jus.br^) nao respondeu agora. A instalacao continua;
if "%NET_CNJ%"=="0" echo  se continuar assim, peca a TI para liberar esse endereco ^(judicial.solverone.com.br/antivirus.html^).
rem (e) o aviso, antes de continuar
if not "%IDENT%"=="1" goto av_nao_ident
if not defined AV goto av_nenhum
if defined SODEF goto av_defender
echo.
echo  Antivirus encontrado: %AV%.
echo  Programas novos costumam ser barrados por ele. Antes de continuar, cadastre a excecao da pasta
echo  C:\LexSuiteONE ^(veja judicial.solverone.com.br/antivirus.html^) ou peca a TI.
call :passos_antivirus
echo.
set /p "PRONTO=  Depois aperte Enter para continuar... "
goto av_fim
:av_defender
echo  Antivirus encontrado: %AV%. Se aparecer um aviso do Windows, clique em "Mais informacoes" e em "Executar".
goto av_fim
:av_nao_ident
echo  Nao consegui identificar o antivirus deste computador ^(este Windows nao informa^).
echo  Se algum programa de protecao bloquear a instalacao, veja judicial.solverone.com.br/antivirus.html
goto av_fim
:av_nenhum
echo  O Windows nao informou nenhum antivirus. Se aparecer um aviso, clique em "Mais informacoes" e em "Executar".
:av_fim
if defined FW echo  Firewall: %FW%.
if defined MARCA_INTERNET if not defined SODEF echo  Se o Windows avisar "fornecedor desconhecido", clique em "Mais informacoes" e em "Executar": o programa ainda nao tem assinatura digital.
echo.

rem Codigo de cliente, antes de tudo: sem codigo valido nada e instalado, e todo aviso de erro deste computador
rem chega a SolverONE com o codigo do escritorio e a identificacao (aleatoria) desta instalacao.
set "INST="
set "CODIGO_OK="
for /f "usebackq delims=" %%g in (`powershell.exe -NoProfile -Command "[guid]::NewGuid().ToString('N').Substring(0,16)"`) do set "INST=%%g"
echo  Digite o codigo de cliente que veio no e-mail de boas-vindas (exemplo: LEX-ABCD-2345).
echo  Para colar, clique com o botao direito dentro desta janela.
echo.
set "TENTATIVAS=0"
:pedir_codigo
set "CODIGO="
set /p "CODIGO=  Codigo de cliente: "
if not defined CODIGO goto pedir_codigo
set "CODIGO=%CODIGO: =%"
echo(%CODIGO%| findstr /r /i /x /c:"LEX-[A-Z0-9][A-Z0-9][A-Z0-9][A-Z0-9]-[A-Z0-9][A-Z0-9][A-Z0-9][A-Z0-9]" >nul || goto codigo_formato
set "CODIGO_OK=%CODIGO%"
curl.exe -s -m 20 -o "%T%\conta.txt" -X POST "%REGISTRO%" -H "Content-Type: application/json" -d "{\"codigo\":\"%CODIGO_OK%\",\"instalacao\":\"%INST%\",\"versao\":\"instalador\"}" || goto sem_internet
findstr /r /c:"ok.:true" "%T%\conta.txt" >nul && goto codigo_ok
findstr /c:"aceite_pendente" "%T%\conta.txt" >nul && goto aceite_pendente
findstr /c:"codigo_desconhecido" "%T%\conta.txt" >nul && goto codigo_desconhecido
findstr /c:"desativado" "%T%\conta.txt" >nul && goto licenca_inativa
findstr /c:"vencido" "%T%\conta.txt" >nul && goto licenca_inativa
goto sem_internet
:codigo_formato
echo  O codigo tem o formato LEX-XXXX-XXXX. Tente de novo.
goto mais_uma
:codigo_desconhecido
echo  Este codigo nao existe. Confira no e-mail de boas-vindas e tente de novo.
:mais_uma
set /a TENTATIVAS+=1
if %TENTATIVAS% GEQ 3 goto codigo_esgotado
goto pedir_codigo
:aceite_pendente
echo  Codigo confirmado. Falta o aceite dos termos pelo responsavel do escritorio:
echo  abra o link "Aceitar os termos" do e-mail de boas-vindas. A instalacao continua;
echo  o programa so le o Diario depois do aceite (a tela mostra o link).
echo.
goto destino_inicio
:codigo_ok
echo  Codigo confirmado.
echo.

:destino_inicio
rem Pasta de destino: C:\LexSuiteONE; se o Windows nao deixar, a pasta do usuario.
set "DEST=C:\LexSuiteONE"
if exist "%LOCALAPPDATA%\LexSuiteONE\lexsuite_robo.py" if not exist "C:\LexSuiteONE\lexsuite_robo.py" set "DEST=%LOCALAPPDATA%\LexSuiteONE"
if not exist "%DEST%\" mkdir "%DEST%" 2>nul
(type nul > "%DEST%\.teste-escrita") 2>nul
if exist "%DEST%\.teste-escrita" goto destino_ok
set "DEST=%LOCALAPPDATA%\LexSuiteONE"
if not exist "%DEST%\" mkdir "%DEST%" 2>nul
(type nul > "%DEST%\.teste-escrita") 2>nul
if not exist "%DEST%\.teste-escrita" goto sem_pasta
:destino_ok
del "%DEST%\.teste-escrita" 2>nul

echo  1 de 6  Lendo a versao que veio no pacote...
copy /y "%DADOS%\instalar.txt" "%T%\instalar.txt" >nul || goto manifesto_ruim
set "versao="
set "arquivo="
set "sha256="
set "nome="
for /f "usebackq tokens=1,* delims==" %%a in ("%T%\instalar.txt") do (
  if /i "%%a"=="versao" set "versao=%%b"
  if /i "%%a"=="arquivo" set "arquivo=%%b"
  if /i "%%a"=="sha256" set "sha256=%%b"
  if /i "%%a"=="nome" set "nome=%%b"
)
if not defined arquivo goto manifesto_ruim
if not defined sha256 goto manifesto_ruim
if not defined nome set "nome=LexSuiteONE"
echo(%arquivo%| findstr /r /x /c:"LexSuiteONE-RADAR-atualizacao-[0-9][0-9.]*\.zip" /c:"LEXSUITE-ONE-ROBO-[0-9][0-9.]*\.zip" >nul || goto manifesto_ruim

echo  2 de 6  Conferindo o %nome% %versao% que veio no pacote...
copy /y "%DADOS%\pacote.zip" "%T%\pacote.zip" >nul || goto falha_extrair

set "H="
for /f "skip=1 delims=" %%h in ('certutil.exe -hashfile "%T%\pacote.zip" SHA256') do if not defined H set "H=%%h"
if not defined H goto hash_ruim
set "H=%H: =%"
if /i not "%H%"=="%sha256%" goto hash_ruim
echo          Impressao digital conferida.

echo  3 de 6  Instalando em %DEST%...
rem 0.7.41 (KR Law, 13/Nov: o antivirus barrou o tar.exe em C:\LexSuiteONE): tenta com o PowerShell e, numa instalacao
rem nova, na pasta do usuario, antes de desistir. Onde ja ha um programa instalado (lexsuite.db), nao muda de pasta.
set "TENTOU=%DEST%"
call :extrair_pacote
if "%EXTRAIU%"=="sim" goto extraiu
if /i "%DEST%"=="%LOCALAPPDATA%\LexSuiteONE" goto falha_extrair
if exist "%DEST%\lexsuite.db" goto falha_extrair
echo          O Windows nao deixou gravar os arquivos em %DEST% ^(o antivirus pode ter bloqueado^).
echo          Tentando na pasta do usuario: %LOCALAPPDATA%\LexSuiteONE
set "DEST=%LOCALAPPDATA%\LexSuiteONE"
set "TENTOU=%TENTOU% e %DEST%"
if not exist "%DEST%\" mkdir "%DEST%" 2>nul
call :extrair_pacote
if not "%EXTRAIU%"=="sim" goto falha_extrair
:extraiu
if exist "%DEST%\chave_publica.txt" goto chave_ok
>"%DEST%\chave_publica.txt" echo %CHAVE%
:chave_ok
rem O programa le este arquivo na primeira abertura: o codigo ja vem preenchido e a identificacao e a mesma.
>"%DEST%\conta-inicial.json" echo {"codigo":"%CODIGO_OK%","instalacao":"%INST%"}

echo  4 de 6  Preparando o que o programa precisa para funcionar (so na primeira vez)...
if exist "%DEST%\python\python.exe" goto python_ok
mkdir "%DEST%\python" 2>nul
tar.exe -xf "%DADOS%\python.zip" -C "%DEST%\python" 2>nul
if not exist "%DEST%\python\python.exe" powershell.exe -NoProfile -Command "Expand-Archive -LiteralPath (Join-Path $env:DADOS 'python.zip') -DestinationPath (Join-Path $env:DEST 'python') -Force" >nul 2>nul
if not exist "%DEST%\python\python.exe" goto sem_python
rem A pasta do programa entra no caminho de modulos do Python portatil (o ".." aponta para a pasta do programa).
for %%f in ("%DEST%\python\python*._pth") do (
  findstr /x /c:".." "%%~f" >nul || echo ..>> "%%~f"
)
:python_ok
if not exist "%DEST%\python\python.exe" goto sem_python

echo  5 de 6  Agora vou criar a leitura automatica ^(tarefa "LexSuiteONE Radar" no Agendador do Windows^)...
call :criar_tarefa
echo  6 de 6  Criando o atalho "%nome%" na area de trabalho e no menu Iniciar...
if exist "%DADOS%\radar.ico" copy /y "%DADOS%\radar.ico" "%DEST%\radar.ico" >nul
set "ICONE=%DEST%\radar.ico"
if not exist "%ICONE%" set "ICONE=%SystemRoot%\System32\shell32.dll,13"
powershell.exe -NoProfile -Command "$w = New-Object -ComObject WScript.Shell; foreach ($p in @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'))) { $s = $w.CreateShortcut((Join-Path $p '%nome%.lnk')); $s.TargetPath = '%DEST%\ABRIR.bat'; $s.WorkingDirectory = '%DEST%'; $s.IconLocation = '%ICONE%'; $s.Description = 'Abre o %nome%'; $s.WindowStyle = 7; $s.Save() }"
if errorlevel 1 echo          Nao consegui criar o atalho. Abra pelo ABRIR.bat em %DEST%.

rd /s /q "%T%" 2>nul
echo.
echo  Pronto. Daqui em diante, abra pelo atalho "%nome%" na area de trabalho.
echo  A tela vai abrir agora no navegador.
echo.
call "%DEST%\ABRIR.bat" >nul
rem 0.7.47 (2.1): o programa precisa estar rodando 5 segundos depois de abrir; senao, o antivirus pode te-lo encerrado
timeout /t 5 /nobreak >nul
tasklist /fi "imagename eq pythonw.exe" 2>nul | find /i "pythonw.exe" >nul && goto programa_aberto
tasklist /fi "imagename eq python.exe" 2>nul | find /i "python.exe" >nul && goto programa_aberto
goto processo_morto
:programa_aberto
timeout /t 20
exit /b 0

:dentro_do_zip
set "ETAPA=aberto de dentro do zip"
set "SINAL=zip_temp"
echo  Este instalador foi aberto de dentro do arquivo .zip, sem extrair. Assim o Windows o coloca
echo  sozinho numa pasta temporaria, e o antivirus costuma barrar o que roda dali.
echo.
echo  Faca assim:
echo    1. Feche esta janela.
echo    2. Clique com o botao direito no arquivo .zip que voce baixou e escolha "Extrair tudo".
echo    3. Na pasta que abrir, de dois cliques em INSTALAR.bat.
goto erro
:sem_internet_antes
set "ETAPA=sem internet"
echo  Este computador nao alcancou nenhum dos enderecos do programa.
echo  Confira a internet ^(ou o proxy da empresa^) e rode o instalador de novo.
goto erro
:rede_recusada
set "ETAPA=rede recusada"
set "SINAL=rede_recusada"
set "DETALHE=site=%NET_SITE% nuvem=%NET_NUVEM% cnj=%NET_CNJ%"
echo  A internet funciona, mas a protecao de rede do antivirus ou o firewall esta barrando os enderecos do programa:
if "%NET_SITE%"=="0" echo    - judicial.solverone.com.br nao respondeu
if "%NET_NUVEM%"=="0" echo    - qvdvkqydhnadhewcidia.supabase.co nao respondeu
call :orientar
goto erro
:processo_morto
set "ETAPA=abrir o programa"
set "SINAL=processo_morto"
echo  O programa foi instalado, mas fechou logo ao abrir: o antivirus pode te-lo encerrado.
call :orientar
goto erro

:extrair_antes
echo  Este instalador precisa da pasta "dados" que vem junto dele no pacote completo.
echo.
echo  Faca assim:
echo    1. Feche esta janela.
echo    2. Clique com o botao direito no arquivo Instalar-LexSuiteONE-completo.zip e escolha "Extrair tudo".
echo    3. Na pasta que abrir, de dois cliques em INSTALAR.bat e, se o Windows perguntar, clique em Executar.
echo.
pause
exit /b 1
:sem_ferramentas
echo  Este Windows nao tem as ferramentas basicas que o instalador usa ^(curl, tar e certutil^).
echo  Ele precisa de Windows 10 atualizado ou Windows 11.
goto erro
:codigo_esgotado
set "ETAPA=codigo de cliente"
set "DETALHE=3 tentativas sem codigo valido"
echo  Nao foi possivel confirmar o codigo de cliente.
goto erro
:licenca_inativa
set "ETAPA=licenca inativa"
echo  A licenca deste escritorio nao esta ativa.
goto erro
:sem_pasta
set "ETAPA=pasta de destino"
echo  Nao consegui criar a pasta do programa nem em C:\LexSuiteONE nem na pasta do usuario.
goto erro
:sem_internet
set "ETAPA=download"
echo  Nao consegui falar com judicial.solverone.com.br para conferir o codigo de cliente.
echo  Confira a internet ^(ou peca a TI para liberar judicial.solverone.com.br e qvdvkqydhnadhewcidia.supabase.co^).
goto erro
:manifesto_ruim
set "ETAPA=manifesto instalar.txt"
set "DETALHE=arquivo=%arquivo% versao=%versao%"
echo  A informacao de versao do pacote veio incompleta. Nada foi instalado. Baixe o pacote completo de novo.
goto erro
:hash_ruim
set "ETAPA=impressao digital"
set "DETALHE=esperado=%sha256% obtido=%H%"
echo  O programa do pacote nao confere com a impressao digital. Nada foi instalado.
echo  Baixe o pacote completo de novo; se repetir, avise o suporte.
goto erro
:falha_extrair
set "ETAPA=descompactar"
set "SINAL=bloqueio_gravacao"
set "DETALHE=errorlevel=%errorlevel% tar e powershell"
echo  Nao consegui descompactar o pacote ^(tentei em %TENTOU%^).
echo  O mais provavel e o antivirus ter bloqueado a criacao dos arquivos do programa.
echo  Peca para liberar a pasta C:\LexSuiteONE ^(e %LOCALAPPDATA%\LexSuiteONE^) no antivirus e rode o instalador de novo.
call :orientar
goto erro
:sem_python
set "ETAPA=preparar python"
if exist "%DEST%\lexsuite_robo.py" set "SINAL=bloqueio_gravacao"
echo  Nao consegui preparar o que o programa precisa para funcionar ^(descompactar o Python que veio no pacote^).
echo  Se o antivirus bloqueou, peca para liberar a pasta %DEST% e rode o instalador de novo.
echo  Se o antivirus apagou o python.exe, restaure o item da quarentena.
call :orientar
goto erro
:erro
if defined ETAPA (
  curl.exe -s -m 15 -X POST "%REGISTRO%" -H "Content-Type: application/json" -d "{\"acao\":\"registro\",\"origem\":\"instalador\",\"etapa\":\"%ETAPA%\",\"versao\":\"%versao%\",\"windows\":\"%WINVER%\",\"mensagem\":\"%DETALHE%\",\"codigo\":\"%CODIGO_OK%\",\"instalacao\":\"%INST%\",\"antivirus\":\"%AV%\",\"antivirus_ligado\":\"%AVON_J%\",\"sinal\":\"%SINAL%\"}" >nul 2>&1
  echo.
  echo  A SolverONE recebeu um aviso tecnico deste erro ^(sem dados pessoais^).
)
echo.
echo  Duvidas: %CONTATO%
rd /s /q "%T%" 2>nul
echo.
pause
exit /b 1

:extrair_pacote
rem 1o o tar.exe do Windows; se o arquivo principal nao apareceu, o Expand-Archive do PowerShell (le T e DEST do ambiente).
rem Numa atualizacao, o arquivo principal antigo sai do caminho antes (e volta se nada extrair): so conta o que veio agora.
set "EXTRAIU=nao"
if exist "%DEST%\lexsuite_robo.py" move /y "%DEST%\lexsuite_robo.py" "%DEST%\lexsuite_robo.py.antes" >nul 2>nul
tar.exe -xf "%T%\pacote.zip" -C "%DEST%" 2>nul
if exist "%DEST%\lexsuite_robo.py" goto extrair_ok
powershell.exe -NoProfile -Command "Expand-Archive -LiteralPath (Join-Path $env:T 'pacote.zip') -DestinationPath $env:DEST -Force" >nul 2>nul
if exist "%DEST%\lexsuite_robo.py" goto extrair_ok
if exist "%DEST%\lexsuite_robo.py.antes" move /y "%DEST%\lexsuite_robo.py.antes" "%DEST%\lexsuite_robo.py" >nul 2>nul
goto :eof
:extrair_ok
del /q "%DEST%\lexsuite_robo.py.antes" 2>nul
set "EXTRAIU=sim"
goto :eof

:criar_tarefa
rem 0.7.47 (2.6.1): a leitura automatica criada aqui, as claras, nesta janela, pelo XML que o programa grava na pasta dele
rem ^(tarefa.xml, com autor e descricao da SolverONE^), nunca na pasta temporaria.
set "TAR_MODO="
"%DEST%\python\python.exe" "%DEST%\lexsuite_robo.py" tarefa > "%T%\tarefa.txt" 2>nul
if exist "%T%\tarefa.txt" for /f "usebackq tokens=1,* delims==" %%a in ("%T%\tarefa.txt") do (
  if /i "%%a"=="MODO" set "TAR_MODO=%%b"
)
if /i "%TAR_MODO%"=="desligada" goto tarefa_desligada
if /i "%TAR_MODO%"=="nenhum" goto tarefa_desligada
if /i "%TAR_MODO%"=="xml" schtasks.exe /create /f /tn "LexSuiteONE Radar" /xml "%DEST%\tarefa.xml" >nul 2>&1
if /i not "%TAR_MODO%"=="xml" goto tarefa_depois
schtasks.exe /query /tn "LexSuiteONE Radar" >nul 2>&1 || goto tarefa_falhou
echo          Leitura automatica criada ^(pode ser mudada em Configuracoes, Leitura do Diario^).
goto :eof
:tarefa_desligada
echo          A leitura automatica esta desligada nas Configuracoes; nao criei.
goto :eof
:tarefa_depois
echo          Nao consegui preparar a leitura automatica agora. Com a tela aberta, o programa le sozinho;
echo          para criar depois: Configuracoes, Leitura do Diario, Salvar.
goto :eof
:tarefa_falhou
set "SINAL=tarefa_falhou"
set "ETAPA=leitura automatica"
echo          Nao consegui criar a leitura automatica: o antivirus pode ter impedido.
echo          Com a tela aberta, o programa le sozinho; depois de liberar, Configuracoes, Leitura do Diario, Salvar.
call :orientar
call :registrar_aviso
set "SINAL="
set "ETAPA="
echo.
set /p "PRONTO=  Aperte Enter para continuar a instalacao... "
goto :eof

:registrar_aviso
curl.exe -s -m 15 -X POST "%REGISTRO%" -H "Content-Type: application/json" -d "{\"acao\":\"registro\",\"origem\":\"instalador\",\"etapa\":\"%ETAPA%\",\"versao\":\"%versao%\",\"windows\":\"%WINVER%\",\"mensagem\":\"%DETALHE%\",\"codigo\":\"%CODIGO_OK%\",\"instalacao\":\"%INST%\",\"antivirus\":\"%AV%\",\"antivirus_ligado\":\"%AVON_J%\",\"sinal\":\"%SINAL%\"}" >nul 2>&1
goto :eof

:orientar
rem 0.7.47 (2.1): o que aconteceu ja foi dito; aqui, o antivirus encontrado, os passos e o texto para a TI. Nunca pede para tirar a protecao.
echo.
if not defined AV echo  Antivirus deste computador: nao identificado.
if defined AV echo  Antivirus encontrado: %AV%.
call :passos_antivirus
call :texto_ti
echo  Nao e preciso desligar o antivirus: basta a excecao. Depois, rode este instalador de novo.
goto :eof

:passos_antivirus
rem Bitdefender e Microsoft Defender por extenso ^(os mesmos de judicial.solverone.com.br/antivirus.html^); os demais, a pagina
echo(%AV%| findstr /i /c:"bitdefender" >nul && goto passos_bitdefender
echo(%AV%| findstr /i /c:"defender" /c:"windows" >nul && goto passos_defender
echo  Passo a passo do seu antivirus, com a fonte oficial do fabricante: judicial.solverone.com.br/antivirus.html
goto :eof
:passos_bitdefender
echo  No Bitdefender:
echo    1. Protecao, Defesa contra Ameacas, Configuracoes, Administrar excecoes, Adicionar uma excecao.
echo    2. Digite C:\LexSuiteONE\ ^(sem asterisco no fim^).
echo    3. Ligue Antivirus ^(Verificacao ao acessar, Analise a pedido, Scripts incorporados^) e Defesa contra Ameacas.
echo    4. Clique em Salvar. Se ja houve bloqueio: Notificacoes, Reiniciar, antes de instalar de novo.
echo  Passos com imagens e fonte oficial: judicial.solverone.com.br/antivirus.html
goto :eof
:passos_defender
echo  No Microsoft Defender:
echo    1. Seguranca do Windows, Protecao contra virus e ameacas, Gerenciar configuracoes, Exclusoes.
echo    2. Adicionar uma exclusao, Pasta, e escolha C:\LexSuiteONE.
echo    3. Se "Acesso controlado a pastas" estiver ligado: Permitir um aplicativo, e escolha
echo       C:\LexSuiteONE\python\python.exe e C:\LexSuiteONE\python\pythonw.exe.
echo  Passos com a fonte oficial: judicial.solverone.com.br/antivirus.html
goto :eof

:texto_ti
echo.
echo  Texto pronto para a TI ^(o mesmo da pagina judicial.solverone.com.br/antivirus.html, com o botao Copiar^):
echo  -----
echo  Pedido de excecao no antivirus para o LexSuiteONE ^(SolverONE^), leitor do Diario de Justica Eletronico Nacional.
echo  Codigo publico; atualizacoes assinadas; sem acesso a area logada; nao envia dados do escritorio para fora.
echo  Por favor, adicione as excecoes ^(protecao em tempo real e protecao por comportamento^):
echo  - Pasta, com subpastas: C:\LexSuiteONE
echo  - Processos: C:\LexSuiteONE\python\pythonw.exe e C:\LexSuiteONE\python\python.exe
echo  - O programa cria uma tarefa no Agendador de Tarefas do Windows chamada "LexSuiteONE Radar" ^(schtasks^),
echo    que roda o pythonw.exe nos horarios configurados pelo escritorio.
echo  - Enderecos: judicial.solverone.com.br, comunicaapi.pje.jus.br, qvdvkqydhnadhewcidia.supabase.co,
echo    brasilapi.com.br e minhareceita.org
echo  Se algum item foi para a quarentena, favor restaurar. Nao e necessario desligar a protecao.
echo  Duvidas: judicial@solverone.com.br
echo  -----
goto :eof
