@echo on
title Activity Tracker Dashboard
color 0A

REM Change to the directory where the batch file is located
cd /d "%~dp0"

echo ===================================================
echo        Activity Tracker Dashboard Launcher
echo ===================================================
echo.

REM Create a log file for errors
echo Log file created at %date% %time% > dashboard_error.log

REM Check if Python is installed
python --version >> dashboard_error.log 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    echo This error has been logged to dashboard_error.log
    pause
    exit /b 1
)

echo Python check passed... >> dashboard_error.log

REM Check if required packages are installed
echo Checking required packages...
python -c "import flask" >> dashboard_error.log 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install flask psutil >> dashboard_error.log 2>&1
    if errorlevel 1 (
        echo Error: Failed to install required packages
        echo Please check dashboard_error.log for details
        echo Try running: pip install flask psutil
        pause
        exit /b 1
    )
)

echo Flask check passed... >> dashboard_error.log

REM Check if simple_dashboard.py exists
if not exist "simple_dashboard.py" (
    echo.
    echo Error: simple_dashboard.py not found in current directory: %CD%
    echo This error has been logged to dashboard_error.log
    echo Current directory contents:
    dir
    echo.
    pause
    exit /b 1
)

echo Found simple_dashboard.py... >> dashboard_error.log

echo.
echo Starting Activity Tracker Dashboard...
echo.
echo The dashboard will be available at http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

REM Try to run the dashboard with error logging
python simple_dashboard.py >> dashboard_error.log 2>&1
if errorlevel 1 (
    echo.
    echo Error: Failed to start the dashboard
    echo Please check dashboard_error.log for details
    echo.
    type dashboard_error.log
    echo.
    pause
    exit /b 1
)

pause 