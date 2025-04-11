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
import threading
import json
from typing import Dict, Any, Callable, Optional
from pynput.keyboard import Key
from pynput.mouse import Button

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

class ActivityTracker:
    def __init__(self, data_dir: str = "data/activity"):
        self.data_dir = data_dir
        self.keyboard_listener = None
        self.mouse_listener = None
        self.is_running = False
        self.events = []
        self.lock = threading.Lock()
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)

    def on_key_press(self, key):
        try:
            key_char = key.char
        except AttributeError:
            key_char = str(key)
        
        event = {
            'type': 'keyboard',
            'action': 'press',
            'key': key_char,
            'timestamp': datetime.now().isoformat()
        }
        
        with self.lock:
            self.events.append(event)

    def on_key_release(self, key):
        try:
            key_char = key.char
        except AttributeError:
            key_char = str(key)
        
        event = {
            'type': 'keyboard',
            'action': 'release',
            'key': key_char,
            'timestamp': datetime.now().isoformat()
        }
        
        with self.lock:
            self.events.append(event)

    def on_mouse_move(self, x, y):
        event = {
            'type': 'mouse',
            'action': 'move',
            'x': x,
            'y': y,
            'timestamp': datetime.now().isoformat()
        }
        
        with self.lock:
            self.events.append(event)

    def on_mouse_click(self, x, y, button, pressed):
        event = {
            'type': 'mouse',
            'action': 'click',
            'button': str(button),
            'pressed': pressed,
            'x': x,
            'y': y,
            'timestamp': datetime.now().isoformat()
        }
        
        with self.lock:
            self.events.append(event)

    def start(self):
        if not self.is_running:
            self.is_running = True
            
            # Start keyboard listener
            self.keyboard_listener = keyboard.Listener(
                on_press=self.on_key_press,
                on_release=self.on_key_release
            )
            self.keyboard_listener.start()
            
            # Start mouse listener
            self.mouse_listener = mouse.Listener(
                on_move=self.on_mouse_move,
                on_click=self.on_mouse_click
            )
            self.mouse_listener.start()
            
            # Start periodic save thread
            self.save_thread = threading.Thread(target=self._periodic_save)
            self.save_thread.daemon = True
            self.save_thread.start()

    def stop(self):
        if self.is_running:
            self.is_running = False
            if self.keyboard_listener:
                self.keyboard_listener.stop()
            if self.mouse_listener:
                self.mouse_listener.stop()
            self._save_events()

    def _periodic_save(self):
        while self.is_running:
            self._save_events()
            threading.Event().wait(60)  # Save every minute

    def _save_events(self):
        with self.lock:
            if not self.events:
                return
            
            # Create filename with current date
            filename = os.path.join(
                self.data_dir,
                f"activity_{datetime.now().strftime('%Y%m%d')}.json"
            )
            
            # Load existing events if file exists
            existing_events = []
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    try:
                        existing_events = json.load(f)
                    except json.JSONDecodeError:
                        pass
            
            # Append new events
            existing_events.extend(self.events)
            
            # Save all events
            with open(filename, 'w') as f:
                json.dump(existing_events, f, indent=2)
            
            # Clear events after saving
            self.events = []

    def get_recent_events(self, limit: int = 100) -> list:
        with self.lock:
            return self.events[-limit:] if self.events else []

def monitor_inactivity():
    """Checks for user inactivity periods"""
    while True:
        idle_time = time.time() - last_activity_time
        if idle_time > inactive_threshold:
            logging.warning(f"User inactive for {int(idle_time)} seconds")
        time.sleep(60)  # Check every minute

def on_press(key):
    """Handle key press events"""
    pass

def on_click(x, y, button, pressed):
    """Handle mouse click events"""
    pass

if __name__ == "__main__":
    # Set up listeners
    keyboard_listener = keyboard.Listener(on_press=on_press)
    mouse_listener = mouse.Listener(on_click=on_click)
    
    # Start monitoring
    keyboard_listener.start()
    mouse_listener.start()
    
    # Start inactivity monitor in separate thread
    inactivity_thread = threading.Thread(target=monitor_inactivity, daemon=True)
    inactivity_thread.start()
    
    logging.info("Activity tracking started. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Activity tracking stopped")
