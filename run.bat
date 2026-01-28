@echo off
REM Fable Book Exporter - Windows Launcher
REM This script sets up and runs the Fable Book Exporter

echo.
echo ================================
echo   FABLE BOOK EXPORTER
echo   Windows Launcher
echo ================================
echo.

REM Check if uv is installed
uv --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: uv is not installed
    echo.
    echo Please install uv from https://docs.astral.sh/uv/getting-started/
    echo Or run: pip install uv
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv\" (
    echo Setting up Python environment with uv...
    echo.
    uv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
echo.
uv pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

REM Run the CLI
echo.
echo Starting Fable Book Exporter...
echo.
python cli.py

pause
