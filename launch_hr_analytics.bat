@echo off
title HR Analytics Platform
color 0A

echo ===================================================
echo             HR Analytics Platform
echo ===================================================
echo.

REM Check Python installation
python --version
if errorlevel 1 (
    echo Error: Python is not installed
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check system requirements
echo Checking system requirements...
powershell -Command "Get-WmiObject -Class Win32_ComputerSystem | Select-Object -ExpandProperty TotalPhysicalMemory" > memory.txt
set /p MEMORY=<memory.txt
del memory.txt

set MIN_MEMORY=4294967296
if %MEMORY% LSS %MIN_MEMORY% (
    echo Warning: System has less than 4GB RAM. 8GB is recommended.
    echo Current RAM: %MEMORY% bytes
    echo Minimum recommended: %MIN_MEMORY% bytes
    echo.
    echo Press any key to continue anyway...
    pause > nul
)

REM Install required packages
echo.
echo Installing required packages...
echo - opencv-python (webcam integration)
echo - mediapipe (posture analysis)
echo - psutil (system monitoring)
echo - pynput (input tracking)
echo - numpy (calculations)
echo - flask (dashboard)
echo - tensorflow-lite (machine learning)
echo.

pip install opencv-python numpy mediapipe psutil pynput flask tensorflow-lite
if errorlevel 1 (
    echo.
    echo Error: Failed to install required packages
    echo Please run the following command manually:
    echo pip install opencv-python numpy mediapipe psutil pynput flask tensorflow-lite
    pause
    exit /b 1
)

REM Create necessary directories
echo.
echo Setting up directory structure...
mkdir activity_data 2>nul
mkdir activity_data\analytics 2>nul
mkdir activity_data\snapshots 2>nul
mkdir activity_data\posture_data 2>nul
mkdir activity_data\input_activity 2>nul
mkdir activity_data\reports 2>nul
mkdir logs 2>nul

REM Start components
echo.
echo Starting HR Analytics Platform...
echo.
echo 1. Starting Data Collection Module...
start /B python data_collection.py
timeout /t 2 /nobreak > nul

echo 2. Starting Analytics Engine...
start /B python analytics_engine.py
timeout /t 2 /nobreak > nul

echo 3. Starting Dashboard...
start /B python dashboard.py
timeout /t 2 /nobreak > nul

echo.
echo HR Analytics Platform is running!
echo.
echo - Dashboard: http://localhost:5000
echo - Data is being collected and analyzed
echo - Check the dashboard for real-time insights
echo.
echo Press Ctrl+C in any window to stop the platform
echo.

REM Keep the window open
pause 