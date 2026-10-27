@echo off
rem Instalar o Python e o pygame-ce num Windows.
rem
rem Uma vez por computador, dentro da pasta clube-de-codigo-2627:
rem
rem   - Botao direito > "Executar como administrador": instala para TODOS
rem     os utilizadores do computador. E o recomendado na sala.
rem   - Duplo clique normal: instala so para a conta atual.
rem
rem Se o Python ainda nao existir, descarrega-o do python.org e instala-o
rem sem perguntas. Pode correr-se outra vez sem estragar nada.
rem
rem Este ficheiro tem de ficar com fins de linha CRLF (ver .gitattributes).

setlocal
cd /d "%~dp0"
set "PIP_DISABLE_PIP_VERSION_CHECK=1"

set "VERSAO=3.12.10"
set "ARQ=amd64"
if /i "%PROCESSOR_ARCHITECTURE%"=="ARM64" set "ARQ=arm64"

rem "net session" so funciona como administrador.
net session >nul 2>&1
if errorlevel 1 goto :conta_atual
set "TODOS=1"
set "DESTINO=%ProgramFiles%\Python312"
echo ==^> Modo administrador: instala para todos os utilizadores.
goto :procurar
:conta_atual
set "TODOS=0"
set "DESTINO=%LOCALAPPDATA%\Programs\Python\Python312"
echo ==^> Sem administrador: instala so para esta conta.

:procurar
echo ==^> 1/3  Procurar o Python
if exist "%DESTINO%\python.exe" goto :usar_destino
py -3 -c "import sys; sys.exit(sys.version_info < (3, 10))" >nul 2>&1
if errorlevel 1 goto :instalar
rem Como administrador, um Python so da conta do administrador nao serve
rem aos outros utilizadores: nesse caso instala-se um para todos.
if "%TODOS%"=="0" goto :usar_py
py -3 -c "import os, sys; sys.exit(sys.prefix.lower().startswith(os.environ['USERPROFILE'].lower()))" >nul 2>&1
if errorlevel 1 goto :instalar
:usar_py
set "PY=py -3"
goto :pygame

:instalar
set "INSTALADOR=%TEMP%\python-%VERSAO%-%ARQ%.exe"
set "URL=https://www.python.org/ftp/python/%VERSAO%/python-%VERSAO%-%ARQ%.exe"
echo     Nao ha Python que sirva. A descarregar o Python %VERSAO%...
curl -L --fail -o "%INSTALADOR%" "%URL%"
if not errorlevel 1 goto :correr_instalador
powershell -NoProfile -Command "Invoke-WebRequest -UseBasicParsing -Uri '%URL%' -OutFile '%INSTALADOR%'"
if errorlevel 1 goto :erro_download
:correr_instalador
echo     A instalar o Python %VERSAO% em %DESTINO% ...
"%INSTALADOR%" /quiet InstallAllUsers=%TODOS% InstallLauncherAllUsers=%TODOS% Include_launcher=1 PrependPath=1 Include_test=0 TargetDir="%DESTINO%"
if errorlevel 1 goto :erro_python
del "%INSTALADOR%" >nul 2>&1
if not exist "%DESTINO%\python.exe" goto :erro_python
:usar_destino
set PY="%DESTINO%\python.exe"

:pygame
echo ==^> 2/3  pygame-ce
rem Se nao houver "wheel" da versao fixa para este Python, instala a mais
rem recente (ver requirements.txt).
%PY% -m pip install -r requirements.txt
if errorlevel 1 %PY% -m pip install pygame-ce
if errorlevel 1 goto :erro_pip

echo ==^> 3/3  Confirmar
%PY% -c "import sys, pygame; print('Python', sys.version.split()[0], '| pygame-ce', pygame.version.ver)"
if errorlevel 1 goto :erro_pip

echo.
echo Pronto. Abre um terminal NOVO dentro desta pasta e corre, por exemplo:
echo.
echo     py halloween\noite-dos-doces.py
echo.
pause
exit /b 0

:erro_download
echo.
echo ERRO: nao foi possivel descarregar o Python. Ha internet?
echo Alternativa: instala-o a mao em https://python.org/downloads
echo marcando "Add python.exe to PATH", e corre este ficheiro outra vez.
goto :fim_erro
:erro_python
echo.
echo ERRO: a instalacao do Python falhou.
echo Se o computador for da escola, pode ser preciso "Executar como administrador".
goto :fim_erro
:erro_pip
echo.
echo ERRO: a instalacao do pygame-ce falhou. Ha internet? Le as mensagens acima.
:fim_erro
echo.
pause
exit /b 1
