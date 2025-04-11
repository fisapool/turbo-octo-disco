@echo on
title Activity Tracker
color 0A

echo ===================================================
echo             Activity Tracker Launcher
echo ===================================================
echo.

REM Check if Python is installed
python --version
if errorlevel 1 (
    echo Error: Python is not installed
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Install required packages
echo.
echo Installing required packages...
echo - opencv-python (for webcam)
echo - mediapipe (for posture analysis)
echo - psutil (for system monitoring)
echo - pynput (for input tracking)
echo - numpy (for calculations)
echo.

pip install opencv-python numpy mediapipe psutil pynput
if errorlevel 1 (
    echo.
    echo Error: Failed to install required packages
    echo Please run the following command manually:
    echo pip install opencv-python numpy mediapipe psutil pynput
    pause
    exit /b 1
)

echo.
echo Packages installed successfully!
echo.
echo Starting Activity Tracker...
echo.
echo Note: You will see detailed status information below.
echo If the webcam window doesn't appear, check the status messages.
echo.

python activity_tracker_app.py

echo.
echo Activity Tracker has stopped.
echo Check the activity_data folder for your session data.
pause 