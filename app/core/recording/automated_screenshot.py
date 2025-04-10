#!/usr/bin/env python3
"""
Automated Screenshot Script with Classification

This script takes screenshots of the active window whenever it changes.
Screenshots are classified and saved in category-specific folders.

Requirements:
    - Python 3.x
    - pyautogui (install using: pip install pyautogui)
    - pygetwindow (install using: pip install PyGetWindow)
    - tensorflow (for screenshot classification)
    - licensing_module (local)

Usage:
    Run the script, and it will monitor the active window and take screenshots whenever it changes.
    Use Ctrl+C to stop the script.
"""

import pyautogui
import win32gui
import pygetwindow as gw
import time
import os
from datetime import datetime
from licensing_module import LicenseManager
from screenshot_classifier import classify_screenshot

# Initialize license manager
license_manager = LicenseManager()
if not license_manager.is_licensed():
    print("License validation failed. Please check your license key.")
    exit(1)

# ------------------------------------------------------------------------------
# Configuration: Set the base folder where screenshots are saved.
# Screenshots will be organized in subfolders by classification category.
# ------------------------------------------------------------------------------
BASE_SAVE_DIR = r"C:\Users\USER\Documents\ActiveWindowScreenshots"
CLASSES = ['code', 'document', 'web']  # Must match classifier categories

# Initialize save directories
for category in CLASSES:
    os.makedirs(os.path.join(BASE_SAVE_DIR, category), exist_ok=True)

# ------------------------------------------------------------------------------
# Function: Get the active window's title and dimensions.
# ------------------------------------------------------------------------------
def get_active_window_info():
    """
    Retrieves the active window's title, position, and size.
    
    Returns:
        tuple: (title, left, top, width, height), or (None, 0, 0, 0, 0) if no active window.
    """
    try:
        # Get the active window's title
        window = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(window)

        # Get the active window's geometry using pygetwindow
        window_obj = gw.getWindowsWithTitle(title)[0]  # Get the first matching window
        left, top, right, bottom = window_obj.left, window_obj.top, window_obj.right, window_obj.bottom
        width, height = right - left, bottom - top

        return title, left, top, width, height
    except (IndexError, AttributeError):
        return None, 0, 0, 0, 0

# ------------------------------------------------------------------------------
# Function: Take a screenshot of the active window and save it.
# ------------------------------------------------------------------------------
def take_active_window_screenshot(base_dir, title, left, top, width, height):
    """
    Captures a screenshot of the active window, classifies it, and saves it in the appropriate category folder.
    
    Parameters:
        base_dir (str): Path to the base save directory.
        title (str): Title of the active window.
        left (int): Left position of the window.
        top (int): Top position of the window.
        width (int): Width of the window.
        height (int): Height of the window.
    """
    if width > 0 and height > 0:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Sanitize the window title for the file name
        sanitized_title = "".join(c if c.isalnum() or c in (" ", "-", "_") else "_" for c in title)
        
        # Take the screenshot
        screenshot = pyautogui.screenshot(region=(left, top, width, height))
        
        # Save temporarily for classification
        temp_path = os.path.join(base_dir, f"temp_{timestamp}.png")
        screenshot.save(temp_path)
        
        try:
            # Classify the screenshot
            category = classify_screenshot(temp_path)
            os.remove(temp_path)  # Remove temp file
            
            # Save to categorized folder
            save_dir = os.path.join(base_dir, category)
            filename = os.path.join(save_dir, f"screenshot_{timestamp}_{category}_{sanitized_title}.png")
            screenshot.save(filename)
            print(f"Screenshot classified as {category} and saved: {filename}")
        except Exception as e:
            print(f"Classification failed: {str(e)}. Saving to uncategorized folder.")
            save_dir = os.path.join(base_dir, "uncategorized")
            os.makedirs(save_dir, exist_ok=True)
            filename = os.path.join(save_dir, f"screenshot_{timestamp}_{sanitized_title}.png")
            screenshot.save(filename)
    else:
        print("Unable to capture the active window.")

# ------------------------------------------------------------------------------
# Main Execution: Monitor active window and take screenshots on change.
# ------------------------------------------------------------------------------
def monitor_and_capture_active_window(save_dir):
    """
    Continuously monitors the active window and takes a screenshot when it changes.
    
    Parameters:
        save_dir (str): Path to the save directory.
    """
    last_window_title = None
    print("Monitoring active windows and taking screenshots of the active window...")
    try:
        while True:
            # Get the active window's info
            title, left, top, width, height = get_active_window_info()
            if title != last_window_title and title.strip():  # Ensure valid title
                print(f"Active window changed: {title}")
                take_active_window_screenshot(save_dir, title, left, top, width, height)
                last_window_title = title
            time.sleep(1)  # Check every second
    except KeyboardInterrupt:
        print("Stopped monitoring active windows.")

if __name__ == "__main__":
    monitor_and_capture_active_window(BASE_SAVE_DIR)
