@echo off
echo Running HR Analytics Installer in Debug Mode...
echo.

REM Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/downloads/
    echo.
    echo Press any key to exit...
    pause
    exit /b 1
)

REM Create logs directory if it doesn't exist
if not exist logs mkdir logs

REM Run the installer in debug mode and redirect output to a log file
echo Starting installer in debug mode...
echo Log files will be created in the logs directory.
echo.
echo If the installer closes immediately, please check:
echo 1. logs\installer_output.log - For general installation output
echo 2. logs\installer_debug.log - For detailed debug information
echo.

python installer_debug.py --debug > logs\installer_output.log 2>&1

if errorlevel 1 (
    echo.
    echo Installation failed! Please check the log files:
    echo - logs\installer_output.log
    echo - logs\installer_debug.log
    echo.
    echo You can also try running the installer as administrator.
    echo.
    echo Press any key to view the log file...
    pause
    type logs\installer_output.log
    echo.
    echo Press any key to exit...
    pause
) else (
    echo.
    echo Installation completed. Check logs for details.
    echo.
    echo Press any key to exit...
    pause
) 