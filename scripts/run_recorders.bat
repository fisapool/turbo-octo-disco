@echo off
echo Starting all productivity monitoring components...

REM Start the Activity Tracker
start "Activity Tracker" cmd /k python "C:\Users\USER\Documents\activity_tracker.py"

REM Start the Active Window Tracker
start "Active Window Tracker" cmd /k python "C:\Users\USER\Documents\active_window_tracker.py"

REM Start the Automated Screenshot Script
start "Automated Screenshot" cmd /k python "C:\Users\USER\Documents\automated_screenshot.py"

REM Start the Video Recording Script
start "Video Recorder" cmd /k python "C:\Users\USER\Documents\scheduled_recording_script.py"

echo All components started successfully.
pause
