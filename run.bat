@echo off
REM Run the LokEventUpdater tool
REM Make sure to run setup.bat first to set up the environment
REM Check if virtual environment exists
if not exist venv (
    echo ERROR: Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)
REM Activate virtual environment
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
REM Change to scripts directory and run the main script
cd scripts
python main.py
if errorlevel 1 (
    echo ERROR: Failed to run the tool
    pause
    exit /b 1
)

pause