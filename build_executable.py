import PyInstaller.__main__
import shutil
import os
from pathlib import Path

# Configuration
APP_NAME = "HR_Analytics_Tracker"
SCRIPT = "activity_tracker.py"
ICON = "app_icon.ico" if os.path.exists("app_icon.ico") else None
DIST_DIR = "dist"
BUILD_DIR = "build"

# Clean previous builds
for dir_path in [DIST_DIR, BUILD_DIR]:
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)

# PyInstaller arguments
args = [
    '--name=%s' % APP_NAME,
    '--onefile',
    '--windowed',  # Prevent console window
    '--add-data=config.json;.',  # Include config file
    '--add-data=dashboard.py;.',  # Include dashboard
    '--add-data=analytics_engine.py;.',  # Include analytics
    '--add-data=data_collection.py;.',  # Include data collection
]

if ICON:
    args.append('--icon=%s' % ICON)

args.append(SCRIPT)

# Run PyInstaller
PyInstaller.__main__.run(args)

print(f"\nExecutable created in {DIST_DIR} directory")
print(f"Copy all files from {DIST_DIR} to deployment location")
