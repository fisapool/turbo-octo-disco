@echo off
echo Starting Scheduled Recording Script...
REM Change directory to the folder containing your script.
cd /d "C:\Users\USER\Documents"

REM Run the Python script. If Python isn’t in your PATH, replace "python" with the full path to your Python executable.
python scheduled_recording_script.py

REM Pause so that any output or error messages are visible.
pause