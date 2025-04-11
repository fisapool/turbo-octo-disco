import json
import time
import threading
import psutil
import platform
import os
from datetime import datetime
from typing import Dict, List, Optional
import logging
from pynput import keyboard, mouse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HIDSystemIntegration:
    def __init__(self, config_path='config.json'):
        self.config = self._load_config(config_path)
        self.data_buffer = []
        self.last_save_time = time.time()
        self.is_running = False
        self.keyboard_listener = None
        self.mouse_listener = None
        self.system_monitor_thread = None
        
    def _load_config(self, config_path):
        default_config = {
            'data_save_interval': 300,  # seconds
            'output_dir': 'hid_system_data',
            'system_metrics_interval': 1,  # seconds
            'keyboard_sampling_rate': 0.1,  # seconds
            'mouse_sampling_rate': 0.1,  # seconds
            'max_buffer_size': 1000
        }
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                return {**default_config, **config}
        except FileNotFoundError:
            return default_config
            
    def start(self):
        """Start the HID and system monitoring"""
        if self.is_running:
            return
            
        # Create output directory if it doesn't exist
        os.makedirs(self.config['output_dir'], exist_ok=True)
        
        self.is_running = True
        
        # Start keyboard monitoring
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self.keyboard_listener.start()
        
        # Start mouse monitoring
        self.mouse_listener = mouse.Listener(
            on_move=self._on_mouse_move,
            on_click=self._on_mouse_click,
            on_scroll=self._on_mouse_scroll
        )
        self.mouse_listener.start()
        
        # Start system monitoring
        self.system_monitor_thread = threading.Thread(target=self._system_monitor_loop)
        self.system_monitor_thread.start()
        
        # Start data saving thread
        self.data_save_thread = threading.Thread(target=self._data_save_loop)
        self.data_save_thread.start()
        
    def stop(self):
        """Stop the HID and system monitoring"""
        if not self.is_running:
            return
            
        self.is_running = False
        
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            
        if self.mouse_listener:
            self.mouse_listener.stop()
            
        if self.system_monitor_thread:
            self.system_monitor_thread.join()
            
        if self.data_save_thread:
            self.data_save_thread.join()
            
        # Save any remaining data
        self._save_data()
        
    def _on_key_press(self, key):
        """Handle keyboard key press events"""
        try:
            key_data = {
                'timestamp': datetime.now().isoformat(),
                'type': 'keyboard',
                'event': 'press',
                'key': str(key),
                'system_state': self._get_system_state()
            }
            self._add_to_buffer(key_data)
        except Exception as e:
            logger.error(f"Error processing key press: {e}")
            
    def _on_key_release(self, key):
        """Handle keyboard key release events"""
        try:
            key_data = {
                'timestamp': datetime.now().isoformat(),
                'type': 'keyboard',
                'event': 'release',
                'key': str(key),
                'system_state': self._get_system_state()
            }
            self._add_to_buffer(key_data)
        except Exception as e:
            logger.error(f"Error processing key release: {e}")
            
    def _on_mouse_move(self, x, y):
        """Handle mouse movement events"""
        try:
            mouse_data = {
                'timestamp': datetime.now().isoformat(),
                'type': 'mouse',
                'event': 'move',
                'position': {'x': x, 'y': y},
                'system_state': self._get_system_state()
            }
            self._add_to_buffer(mouse_data)
        except Exception as e:
            logger.error(f"Error processing mouse move: {e}")
            
    def _on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click events"""
        try:
            mouse_data = {
                'timestamp': datetime.now().isoformat(),
                'type': 'mouse',
                'event': 'click',
                'button': str(button),
                'action': 'press' if pressed else 'release',
                'position': {'x': x, 'y': y},
                'system_state': self._get_system_state()
            }
            self._add_to_buffer(mouse_data)
        except Exception as e:
            logger.error(f"Error processing mouse click: {e}")
            
    def _on_mouse_scroll(self, x, y, dx, dy):
        """Handle mouse scroll events"""
        try:
            mouse_data = {
                'timestamp': datetime.now().isoformat(),
                'type': 'mouse',
                'event': 'scroll',
                'position': {'x': x, 'y': y},
                'scroll': {'dx': dx, 'dy': dy},
                'system_state': self._get_system_state()
            }
            self._add_to_buffer(mouse_data)
        except Exception as e:
            logger.error(f"Error processing mouse scroll: {e}")
            
    def _system_monitor_loop(self):
        """Monitor system metrics at regular intervals"""
        while self.is_running:
            try:
                system_data = {
                    'timestamp': datetime.now().isoformat(),
                    'type': 'system',
                    'metrics': self._get_system_metrics()
                }
                self._add_to_buffer(system_data)
                
                time.sleep(self.config['system_metrics_interval'])
            except Exception as e:
                logger.error(f"Error in system monitoring: {e}")
                time.sleep(1)  # Prevent tight loop on error
                
    def _data_save_loop(self):
        """Save collected data at regular intervals"""
        while self.is_running:
            try:
                current_time = time.time()
                if current_time - self.last_save_time >= self.config['data_save_interval']:
                    self._save_data()
                    self.last_save_time = current_time
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in data save loop: {e}")
                time.sleep(1)
                
    def _add_to_buffer(self, data):
        """Add data to buffer with size limit"""
        self.data_buffer.append(data)
        if len(self.data_buffer) >= self.config['max_buffer_size']:
            self._save_data()
            
    def _save_data(self):
        """Save collected data to JSON file"""
        if not self.data_buffer:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.config['output_dir'], f"data_{timestamp}.json")
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.data_buffer, f, indent=2)
            self.data_buffer = []
            logger.info(f"Saved data to {filename}")
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            
    def _get_system_metrics(self):
        """Get current system metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=None),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'network_io': {
                'bytes_sent': psutil.net_io_counters().bytes_sent,
                'bytes_recv': psutil.net_io_counters().bytes_recv
            },
            'process_count': len(psutil.pids()),
            'system_info': {
                'platform': platform.system(),
                'platform_version': platform.version(),
                'processor': platform.processor(),
                'python_version': platform.python_version()
            }
        }
        
    def _get_system_state(self):
        """Get current system state for correlation"""
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(interval=None),
            'memory_percent': psutil.virtual_memory().percent,
            'active_processes': len(psutil.pids())
        }

if __name__ == "__main__":
    integration = HIDSystemIntegration()
    integration.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        integration.stop() 