@echo off
rem Sobe o app. O cd garante a raiz do projeto, que e de onde o Python acha os
rem pacotes core\, plugins\ e visual\.
cd /d "%~dp0"

set "VENV=C:\envs\venv-nuvem_palavras"

if not exist "%VENV%\Scripts\activate.bat" (
    echo Ambiente virtual nao encontrado em "%VENV%".
    echo Crie com: uv venv "%VENV%" --python 3.13
    echo E instale com: uv pip install --python "%VENV%\Scripts\python.exe" -r requirements.txt
    pause
    exit /b 1
)

call "%VENV%\Scripts\activate.bat"
streamlit run app.py

pause
