@echo on
title Full Activity Tracker Application
color 0A

REM Change to the directory where the batch file is located
cd /d "%~dp0"

echo ===================================================
echo        Full Activity Tracker Application
echo ===================================================
echo.

REM Create a log file for errors
echo Log file created at %date% %time% > activity_tracker_error.log

REM Check if Python is installed
python --version >> activity_tracker_error.log 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    echo This error has been logged to activity_tracker_error.log
    pause
    exit /b 1
)

echo Python check passed... >> activity_tracker_error.log

REM Check if required packages are installed
echo Checking required packages...
python -c "import cv2" >> activity_tracker_error.log 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install opencv-python numpy pynput psutil flask >> activity_tracker_error.log 2>&1
    if errorlevel 1 (
        echo Error: Failed to install required packages
        echo Please check activity_tracker_error.log for details
        echo Try running: pip install opencv-python numpy pynput psutil flask
        pause
        exit /b 1
    )
)

echo OpenCV check passed... >> activity_tracker_error.log

REM Check if main application file exists
if not exist "test_webcam.py" (
    echo.
    echo Error: test_webcam.py not found in current directory: %CD%
    echo This error has been logged to activity_tracker_error.log
    echo Current directory contents:
    dir
    echo.
    pause
    exit /b 1
)

echo Found test_webcam.py... >> activity_tracker_error.log

echo.
echo Starting Full Activity Tracker Application...
echo.
echo The application will start in a moment...
echo A webcam window should appear shortly...
echo.

REM Try to run the full application with error logging
python test_webcam.py >> activity_tracker_error.log 2>&1
if errorlevel 1 (
    echo.
    echo Error: Failed to start the application
    echo Please check activity_tracker_error.log for details
    echo.
    type activity_tracker_error.log
    echo.
    pause
    exit /b 1
)

pause 