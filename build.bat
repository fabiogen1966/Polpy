@echo off
REM ============================================================
REM Polpy - Script di build per creare l'eseguibile
REM ============================================================
REM Prerequisito: Python 3.8.10 installato
REM Se installato altrove, modifica la variabile qui sotto:
REM Percorso tipico: C:\Users\<UTENTE>\AppData\Local\Programs\Python\Python38\python.exe
SET PYTHON38=C:\Python38\python.exe

echo.
echo ============================================================
echo  Polpy - Build eseguibile
echo ============================================================
echo.

REM Verifica che Python 3.8 esista
IF NOT EXIST "%PYTHON38%" (
    echo ERRORE: Python 3.8 non trovato in %PYTHON38%
    echo Scarica l'installer da:
    echo https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe
    echo.
    echo Installalo in C:\Python38 oppure modifica la variabile
    echo PYTHON38 in questo script.
    pause
    exit /b 1
)

echo [1/5] Verifico versione Python...
"%PYTHON38%" --version

echo.
echo [2/5] Creo virtual environment di build...
IF EXIST ".venv38" rmdir /s /q .venv38
"%PYTHON38%" -m venv .venv38

echo.
echo [3/5] Installo dipendenze di build...
call .venv38\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements-build.txt

echo.
echo [4/5] Eseguo PyInstaller...
pyinstaller polpy.spec --clean --noconfirm

echo.
echo [5/5] Copio file aggiuntivi nella distribuzione...
IF NOT EXIST "dist\Polpy\input" mkdir "dist\Polpy\input"
IF NOT EXIST "dist\Polpy\output" mkdir "dist\Polpy\output"

echo.
echo ============================================================
echo  BUILD COMPLETATA!
echo ============================================================
echo.
echo L'eseguibile si trova in: dist\Polpy\Polpy.exe
echo.
echo Per distribuire su Win7, copia l'intera cartella dist\Polpy\
echo sulla macchina target.
echo.
pause
