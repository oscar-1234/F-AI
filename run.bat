@echo off
echo ========================================
echo  Fabbrica Elfi AI - Avvio
echo ========================================
echo.

REM Attiva virtual environment
if not exist venv (
    echo Virtual environment non trovato!
    echo Esegui prima: setup.bat
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

REM Controlla .env
if not exist .env (
    echo File .env non trovato!
    echo Copia .env.example in .env e configura le API keys
    pause
    exit /b 1
)

echo Avvio Streamlit...
echo.
echo L'app si aprira' automaticamente nel browser
echo URL: http://localhost:8501
echo.
echo Per fermare: Ctrl+C
echo.

streamlit run app/main.py
