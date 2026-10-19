@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Fotos do eventface

set "PY="
where py >nul 2>nul && set "PY=py"
if not defined PY (where python >nul 2>nul && set "PY=python")
if not defined PY goto sem_python

%PY% -c "import PIL" 2>nul
if errorlevel 1 (
  echo Instalando o Pillow, so na primeira vez...
  %PY% -m pip install --user --quiet pillow
)

if not "%~1"=="" goto com_argumentos
echo.
echo   1 - Conferir a foto de cada pessoa, sem ir ao site
echo   2 - Testar com uma pessoa
echo   3 - Rodar a lista toda
echo.
set "OP="
set /p "OP=Escolha 1, 2 ou 3: "
if "%OP%"=="1" goto conferir
if "%OP%"=="2" goto uma
if "%OP%"=="3" goto todas
goto fim

:conferir
%PY% baixar_fotos.py --conferir
goto fim

:uma
set "NOME="
set /p "NOME=Nome da pessoa, como esta no pessoas.csv: "
%PY% baixar_fotos.py --so "%NOME%"
goto fim

:todas
%PY% baixar_fotos.py
goto fim

:com_argumentos
%PY% baixar_fotos.py %*
goto fim

:sem_python
echo Nao achei o Python neste computador.
echo Instale em https://www.python.org/downloads/ marcando "Add python.exe to PATH" e rode de novo.

:fim
echo.
pause
