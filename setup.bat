@echo off
REM Setup script for LokEventUpdater
REM Checks Python installation and sets up virtual environment with dependencies

setlocal enabledelayedexpansion

REM Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    echo Make sure to add Python to PATH during installation
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Create virtual environment
echo Creating virtual environment...
if not exist venv (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
) else (
    echo Virtual environment already exists
)
echo.

REM Activate virtual environment and install dependencies
echo Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install required packages
echo Installing required packages...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt >nul 2>&1

if errorlevel 1 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)

echo.
echo ============================================
echo Setup completed successfully!
echo ============================================
echo.
echo Virtual environment location: %cd%\venv
echo.
echo To use this tool run the run.bat script.
echo.
pause