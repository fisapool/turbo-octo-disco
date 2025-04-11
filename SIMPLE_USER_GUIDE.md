# HR Analytics Platform - User Guide

## Installation

1. Download the installer package
2. Run `installer.py` by double-clicking it or running from command line:
   ```
   python installer.py
   ```
3. Follow the on-screen instructions:

   ![Installer Screenshot](installer_screenshot.png)

4. The installer will:
   - Create installation folder (default: `C:\Users\[YourName]\HR Analytics`)
   - Install required components
   - Copy application files
   - Attempt to create a desktop shortcut

## Running the Application

You have two options:

### Option 1: Using Python
- **With shortcut**: Double-click the "HR Analytics" icon on your desktop
- **Without shortcut**: 
  1. Open File Explorer
  2. Navigate to your installation folder
  3. Double-click `activity_tracker.py`

### Option 2: Using Standalone Executable
1. Download the HR_Analytics_Tracker.zip package
2. Extract all files to a folder
3. Double-click `HR_Analytics_Tracker.exe`

The executable version doesn't require Python to be installed.

## First Run

When you first run the application:
1. It will create a default configuration file
2. The system tray icon will appear
3. Basic activity tracking will start automatically

## Troubleshooting

If you encounter issues:
- Check the `installer_log.txt` file for errors
- Make sure Python 3.8+ is installed
- Contact support if problems persist

## Frequently Asked Questions

**Q: The installer didn't create a desktop shortcut - how do I run the program?**
A: Navigate to your installation folder and double-click `activity_tracker.py`

**Q: Where are my activity logs stored?**
A: In the `logs` subfolder of your installation directory

**Q: How do I configure advanced features?**
A: Edit the `config.json` file in your installation folder
