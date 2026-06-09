@echo off
setlocal EnableDelayedExpansion
title FormosaFit AI - Pre-download Resources
color 0B

echo.
echo  +==================================================+
echo  ^|     FormosaFit AI - Resource Downloader        ^|
echo  ^|          (Without Starting Servers)            ^|
echo  +==================================================+
echo.

cd /d "%~dp0"

rem ------------------------------------------
rem Step 1: Python environment setup and install dependencies
rem ------------------------------------------
echo [1/2] Setting up Python dependencies...
python --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Python is not installed or not in PATH. Skipping Python packages setup.
    goto :step2
)

if not exist ".venv" (
    echo       Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat
echo       Upgrading pip...
python -m pip install -q --upgrade pip >nul 2>&1
echo       Installing dependencies from requirements_gradio.txt...
pip install -q -r requirements_gradio.txt
echo       Python dependencies installed successfully.
echo.

:step2
rem ------------------------------------------
rem Step 2: Ollama Models Pull
rem ------------------------------------------
echo [2/2] Checking Ollama and downloading models...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: Ollama is not installed or not in PATH.
    echo Please install Ollama from https://ollama.com to use local models.
    goto :end
)

echo       Ensuring Ollama server is running...
tasklist /FI "IMAGENAME eq ollama.exe" 2>nul | find /I "ollama.exe" >nul
if errorlevel 1 (
    echo       Ollama is not running. Starting Ollama server...
    start "" ollama serve
    timeout /t 5 >nul
)

echo       Pulling VLM model (moondream: ~1.7GB)...
ollama pull moondream

echo       Pulling LLM model (llama3.2:3b: ~2.0GB)...
ollama pull llama3.2:3b

echo       Ollama models download complete.
echo.

:end
echo +==================================================+
echo ^| All requested resources have been downloaded!     ^|
echo +==================================================+
echo.
pause
