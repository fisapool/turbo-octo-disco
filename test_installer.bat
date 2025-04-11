@echo off
echo Running HR Analytics Installer Tester...

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install required packages
echo Installing required packages...
pip install -r requirements.txt
pip install pywin32
pip install winshell

REM Run the test script
echo Running test script...
python test_installer.py

echo.
echo Test completed. Check test_installer_log.txt for details.
pause 