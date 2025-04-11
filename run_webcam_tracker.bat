@echo off
title Webcam Activity Tracker - Launcher
color 0A

echo ===================================================
echo        Webcam Activity Tracker - Launcher
echo ===================================================
echo.
echo Please choose an option:
echo.
echo 1. Run Simple Webcam Test
echo 2. Run Full Activity Tracker
echo 3. View User Guide
echo 4. Run Dashboard
echo 5. Exit
echo.
echo ===================================================
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo Starting Simple Webcam Test...
    echo.
    python simple_webcam_test.py
    goto :end
)

if "%choice%"=="2" (
    echo.
    echo Starting Full Activity Tracker...
    echo.
    python test_webcam.py
    goto :end
)

if "%choice%"=="3" (
    echo.
    echo Opening User Guide...
    echo.
    start notepad USER_GUIDE.md
    goto :end
)

if "%choice%"=="4" (
    echo.
    echo Starting Dashboard...
    echo.
    python simple_dashboard.py
    goto :end
)

if "%choice%"=="5" (
    echo.
    echo Exiting...
    echo.
    goto :end
)

echo.
echo Invalid choice. Please try again.
echo.
goto :end

:end 