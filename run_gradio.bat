@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion
title FormosaFit AI - One-Click Setup and Launch
color 0A

echo.
echo  +--------------------------------------------------+
echo  ^|     FormosaFit AI - Smart Fashion Recommender    ^|
echo  ^|         One-Click Setup and Launch               ^|
echo  +--------------------------------------------------+
echo.

cd /d "%~dp0"

REM ==========================================
REM Step 1: Check Python
REM ==========================================
echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do echo       Found Python %%v
echo.

REM ==========================================
REM Step 2: Check / Install Ollama + Models
REM ==========================================
echo [2/5] Checking Ollama...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo       Ollama not found. Attempting to install...
    echo       Downloading Ollama installer...
    powershell -Command "Invoke-WebRequest -Uri 'https://ollama.com/download/OllamaSetup.exe' -OutFile '%TEMP%\OllamaSetup.exe'"
    if exist "%TEMP%\OllamaSetup.exe" (
        echo       Running Ollama installer...
        start /wait "" "%TEMP%\OllamaSetup.exe" /SILENT
        del "%TEMP%\OllamaSetup.exe" >nul 2>&1
        REM Refresh PATH
        set "PATH=%LOCALAPPDATA%\Programs\Ollama;%PATH%"
    ) else (
        echo       WARNING: Could not download Ollama.
        echo       Please install manually from https://ollama.com
        echo       Then re-run this script.
        echo.
        set "OLLAMA_AVAILABLE=0"
        goto :skip_ollama
    )
)

set "OLLAMA_AVAILABLE=1"
echo       Ollama is available.

REM Make sure Ollama server is running
echo       Ensuring Ollama server is running...
tasklist /FI "IMAGENAME eq ollama.exe" 2>nul | find /I "ollama.exe" >nul
if errorlevel 1 (
    start "" ollama serve
    timeout /t 3 >nul
)

REM Pull VLM model (moondream) if not already present
echo       Checking if VLM model (moondream) is available...
ollama list | findstr /i "moondream" >nul
if errorlevel 1 (
    echo.
    echo       Pulling VLM model: moondream, 1.7GB...
    echo       This may take a few minutes on first run.
    ollama pull moondream
    echo.
) else (
    echo       VLM model moondream is already pulled.
)

REM Pull LLM model (llama3.2:3b) if not already present
echo       Checking if LLM model (llama3.2) is available...
ollama list | findstr /i "llama3.2" >nul
if errorlevel 1 (
    echo.
    echo       Pulling LLM model: llama3.2:3b, 2GB...
    echo       This may take a few minutes on first run.
    ollama pull llama3.2:3b
    echo.
) else (
    echo       LLM model llama3.2 is already pulled.
)

:skip_ollama

REM ==========================================
REM Step 3: Create venv if needed
REM ==========================================
echo [3/5] Setting up Python environment...
if not exist ".venv" (
    echo       Creating virtual environment...
    python -m venv .venv
)
call .venv\Scripts\activate.bat
echo       Virtual environment activated.
echo.

REM ==========================================
REM Step 4: Install Python dependencies
REM ==========================================
echo [4/5] Installing Python dependencies...
if not exist ".venv\installed.tag" (
    echo       Installing requirements...
    pip install -q --upgrade pip >nul 2>&1
    pip install -r requirements_gradio.txt
    if !errorlevel! equ 0 (
        echo tag > ".venv\installed.tag"
        echo       Dependencies successfully installed.
    ) else (
        echo       ERROR: Failed to install Python dependencies.
        pause
        exit /b 1
    )
) else (
    echo       Dependencies already installed. Skipping pip check.
)
echo.

REM ==========================================
REM Step 5: Launch FormosaFit
REM ==========================================
echo [5/5] Launching FormosaFit AI...
echo.
echo  +--------------------------------------------------+
echo  ^|   FormosaFit AI is starting!                     ^|
echo  ^|   Open your browser at: http://localhost:7860    ^|
echo  +--------------------------------------------------+
echo.

if "!OLLAMA_AVAILABLE!"=="0" (
    echo  WARNING: Ollama was not found. Local models won't work.
    echo  You can still use cloud APIs like OpenAI or Gemini via Settings.
    echo.
)

REM Automatically open browser
start "" "http://localhost:7860"

python app_gradio.py

echo.
echo FormosaFit AI has stopped.
pause
