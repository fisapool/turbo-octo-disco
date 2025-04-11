@echo off
echo Creating HR Analytics Platform Installer...

REM Create virtual environment
python -m venv venv
call venv\Scripts\activate

REM Install required packages
pip install -r requirements.txt
pip install pyinstaller==5.13.2
pip install pywin32==306
pip install winshell==0.6.1

REM Create a simple icon if it doesn't exist
if not exist "static\icon.ico" (
    echo Creating default icon...
    mkdir static 2>nul
    copy NUL static\icon.ico >nul
)

REM Create the executable with better error handling and all dependencies
pyinstaller --clean ^
    --onefile ^
    --windowed ^
    --icon=static\icon.ico ^
    --add-binary "%VIRTUAL_ENV%\Lib\site-packages\win32\win32api.pyd;win32" ^
    --add-binary "%VIRTUAL_ENV%\Lib\site-packages\win32\win32gui.pyd;win32" ^
    --add-binary "%VIRTUAL_ENV%\Lib\site-packages\pythoncom39.dll;." ^
    --add-binary "%VIRTUAL_ENV%\Lib\site-packages\win32\win32com.shell.shell.pyd;win32" ^
    --add-data "docs\SIMPLE_USER_GUIDE.md;docs" ^
    --add-data "config.json;." ^
    --add-data "static;static" ^
    --add-data "activity_tracker.py;." ^
    --add-data "dashboard.py;." ^
    --add-data "analytics_engine.py;." ^
    --add-data "data_collection.py;." ^
    --hidden-import win32com.client ^
    --hidden-import win32gui ^
    --hidden-import win32con ^
    --hidden-import win32com.shell ^
    --name "HR Analytics Setup" ^
    installer.py

REM Create dist directory if it doesn't exist
if not exist "dist" mkdir dist

REM Copy additional files
if not exist "dist\docs" mkdir dist\docs
copy "docs\SIMPLE_USER_GUIDE.md" "dist\docs\" 2>nul
copy "config.json" "dist\" 2>nul
xcopy /E /I "static" "dist\static" 2>nul

REM Create a simple README file
echo HR Analytics Platform > "dist\README.txt"
echo ===================== >> "dist\README.txt"
echo. >> "dist\README.txt"
echo To install the application: >> "dist\README.txt"
echo 1. Double-click "HR Analytics Setup.exe" >> "dist\README.txt"
echo 2. Follow the installation wizard >> "dist\README.txt"
echo 3. After installation, a shortcut will be created on your desktop >> "dist\README.txt"
echo. >> "dist\README.txt"
echo If you encounter any issues, please check the installer_log.txt file >> "dist\README.txt"

echo Installer created successfully!
echo The installer is located in the 'dist' folder.
echo.
echo Please test the installer by running "dist\HR Analytics Setup.exe"

REM Clean up virtual environment
deactivate
rmdir /s /q venv

pause 