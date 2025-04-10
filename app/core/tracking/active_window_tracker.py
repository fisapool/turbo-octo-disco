#!/usr/bin/env python3
"""
Active Window Tracker

This script logs the title of the currently active window each time it changes.
Logs are saved to a log file in your Documents folder (or you can adjust the path).

Requirements:
    - Python 3.x
    - pywin32 (install using: pip install pywin32)
    - licensing_module (local)

Usage:
    Run this script on your Windows machine.
    It will continuously check for the active window every second.
    When the active window changes, it logs the new window title and timestamp.
"""

import time
import win32gui
import logging
import os
from licensing_module import LicenseManager

# Initialize license manager
license_manager = LicenseManager()
if not license_manager.is_licensed():
    print("License validation failed. Please check your license key.")
    exit(1)

# ------------------------------------------------------------------------------
# Configuration: Set the folder and log file path.
# ------------------------------------------------------------------------------
LOG_DIR = r"C:\Users\USER\Documents\AppActivityLogs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
LOG_FILE = os.path.join(LOG_DIR, "active_window_log.txt")

# ------------------------------------------------------------------------------
# Logging Configuration: Log messages to console and file.
# ------------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def get_active_window_title():
    """
    Returns the title of the currently active (foreground) window.
    
    Returns:
        str: Active window title (or an empty string if not available).
    """
    window = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(window)

def track_active_window(poll_interval=1):
    """
    Continuously checks and logs the currently active window's title.
    
    Parameters:
        poll_interval (int): Interval in seconds between checks (default is 1 second).
    """
    last_window = None
    logging.info("Active window tracking has started. Press Ctrl+C to stop.")
    while True:
        try:
            active_window = get_active_window_title()
            if active_window != last_window:
                logging.info(f"Active window changed: {active_window}")
                last_window = active_window
            time.sleep(poll_interval)
        except KeyboardInterrupt:
            logging.info("Active window tracking stopped by user.")
            break

if __name__ == "__main__":
    track_active_window()