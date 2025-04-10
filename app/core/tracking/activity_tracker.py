#!/usr/bin/env python3
"""
Keyboard and Mouse Activity Tracker

Tracks and logs keyboard and mouse events including:
- Key presses
- Mouse clicks
- Mouse movement distance
- Active/inactive time

Requirements:
    - pynput (pip install pynput)
    - licensing_module (local)
"""

from pynput import keyboard, mouse
from licensing_module import LicenseManager
import time
import logging
import os
from datetime import datetime

# Initialize license manager
license_manager = LicenseManager()
if not license_manager.is_licensed():
    print("License validation failed. Please check your license key.")
    exit(1)

# Configuration
LOG_DIR = r"C:\Users\USER\Documents\AppActivityLogs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
LOG_FILE = os.path.join(LOG_DIR, "activity_log.txt")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()]
)

# Activity tracking variables
last_activity_time = time.time()
inactive_threshold = 300  # 5 minutes in seconds

def on_press(key):
    global last_activity_time
    last_activity_time = time.time()
    try:
        logging.info(f"Key pressed: {key.char}")
    except AttributeError:
        logging.info(f"Special key pressed: {key}")

def on_click(x, y, button, pressed):
    global last_activity_time
    last_activity_time = time.time()
    action = "Pressed" if pressed else "Released"
    logging.info(f"Mouse {action} at ({x}, {y}) with {button}")

def monitor_inactivity():
    """Checks for user inactivity periods"""
    while True:
        idle_time = time.time() - last_activity_time
        if idle_time > inactive_threshold:
            logging.warning(f"User inactive for {int(idle_time)} seconds")
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    # Set up listeners
    keyboard_listener = keyboard.Listener(on_press=on_press)
    mouse_listener = mouse.Listener(on_click=on_click)
    
    # Start monitoring
    keyboard_listener.start()
    mouse_listener.start()
    
    # Start inactivity monitor in separate thread
    import threading
    inactivity_thread = threading.Thread(target=monitor_inactivity, daemon=True)
    inactivity_thread.start()
    
    logging.info("Activity tracking started. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Activity tracking stopped")
