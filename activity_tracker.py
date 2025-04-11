import time
from datetime import datetime
from pynput import keyboard, mouse
import threading
import json
from typing import Dict, List, Optional

class ActivityTracker:
    def __init__(self):
        self.keyboard_events: List[Dict] = []
        self.mouse_events: List[Dict] = []
        self.is_running = False
        self.keyboard_listener: Optional[keyboard.Listener] = None
        self.mouse_listener: Optional[mouse.Listener] = None
        self.lock = threading.Lock()

    def _on_key_press(self, key):
        try:
            key_char = key.char
        except AttributeError:
            key_char = str(key)
        
        event = {
            'type': 'key_press',
            'key': key_char,
            'timestamp': datetime.now().isoformat()
        }
        
        with self.lock:
            self.keyboard_events.append(event)

    def _on_key_release(self, key):
        try:
            key_char = key.char
        except AttributeError:
            key_char = str(key)
        
        event = {
            'type': 'key_release',
            'key': key_char,
            'timestamp': datetime.now().isoformat()
        }
        
        with self.lock:
            self.keyboard_events.append(event)

    def _on_mouse_move(self, x, y):
        event = {
            'type': 'mouse_move',
            'x': x,
            'y': y,
            'timestamp': datetime.now().isoformat()
        }
        
        with self.lock:
            self.mouse_events.append(event)

    def _on_mouse_click(self, x, y, button, pressed):
        event = {
            'type': 'mouse_click',
            'x': x,
            'y': y,
            'button': str(button),
            'pressed': pressed,
            'timestamp': datetime.now().isoformat()
        }
        
        with self.lock:
            self.mouse_events.append(event)

    def start(self):
        if not self.is_running:
            self.is_running = True
            
            # Start keyboard listener
            self.keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self.keyboard_listener.start()
            
            # Start mouse listener
            self.mouse_listener = mouse.Listener(
                on_move=self._on_mouse_move,
                on_click=self._on_mouse_click
            )
            self.mouse_listener.start()

    def stop(self):
        if self.is_running:
            self.is_running = False
            if self.keyboard_listener:
                self.keyboard_listener.stop()
            if self.mouse_listener:
                self.mouse_listener.stop()

    def get_events(self) -> Dict:
        with self.lock:
            return {
                'keyboard_events': self.keyboard_events.copy(),
                'mouse_events': self.mouse_events.copy()
            }

    def clear_events(self):
        with self.lock:
            self.keyboard_events.clear()
            self.mouse_events.clear()

    def save_events(self, filename: str):
        events = self.get_events()
        with open(filename, 'w') as f:
            json.dump(events, f, indent=2)

if __name__ == "__main__":
    # Example usage
    tracker = ActivityTracker()
    tracker.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        tracker.stop()
        tracker.save_events('activity_log.json') 