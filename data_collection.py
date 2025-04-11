import cv2
import numpy as np
import time
import os
from datetime import datetime
import threading
import json
import logging
from pathlib import Path
import mediapipe as mp
import psutil
from pynput import mouse, keyboard
import queue
import pickle

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/data_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('DataCollection')

class DataCollectionModule:
    def __init__(self, config_path='config.json'):
        self.config = self._load_config(config_path)
        self.is_running = False
        self.data_queue = queue.Queue()
        
        # Initialize components based on config
        self.components = {
            'keyboard': self.config['data_collection']['keyboard'],
            'mouse': self.config['data_collection']['mouse'],
            'webcam': self.config['data_collection']['webcam']
        }
        
        # Initialize MediaPipe for posture analysis
        if self.components['webcam']:
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
        # Create output directories
        for dir_name in ['snapshots', 'analytics', 'posture_data', 'input_activity']:
            Path(os.path.join(self.config['system']['data_dir'], dir_name)).mkdir(parents=True, exist_ok=True)
            
    def _load_config(self, config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return self._get_default_config()
            
    def _get_default_config(self):
        return {
            "data_collection": {
                "keyboard": True,
                "mouse": True,
                "webcam": True,
                "interval": 5
            },
            "system": {
                "data_dir": "activity_data"
            }
        }
        
    def start(self):
        """Start all data collection components"""
        logger.info("Starting data collection module...")
        self.is_running = True
        
        # Start components
        if self.components['keyboard'] or self.components['mouse']:
            self._start_input_monitoring()
            
        if self.components['webcam']:
            self._start_webcam_monitoring()
            
        # Start data processing thread
        self.processing_thread = threading.Thread(target=self._process_data)
        self.processing_thread.start()
        
        logger.info("Data collection module started successfully")
        
    def stop(self):
        """Stop all data collection components"""
        logger.info("Stopping data collection module...")
        self.is_running = False
        
        # Stop all threads and release resources
        if hasattr(self, 'webcam') and self.webcam:
            self.webcam.release()
        
        if hasattr(self, 'keyboard_listener'):
            self.keyboard_listener.stop()
            
        if hasattr(self, 'mouse_listener'):
            self.mouse_listener.stop()
            
        # Wait for processing thread
        if hasattr(self, 'processing_thread'):
            self.processing_thread.join()
            
        logger.info("Data collection module stopped")
        
    def _start_input_monitoring(self):
        """Start keyboard and mouse monitoring"""
        def on_activity(event_type, event):
            timestamp = datetime.now().isoformat()
            self.data_queue.put({
                'type': event_type,
                'timestamp': timestamp,
                'data': str(event)
            })
            
        if self.components['keyboard']:
            self.keyboard_listener = keyboard.Listener(
                on_press=lambda event: on_activity('keyboard', event)
            )
            self.keyboard_listener.start()
            logger.info("Keyboard monitoring started")
            
        if self.components['mouse']:
            self.mouse_listener = mouse.Listener(
                on_move=lambda x, y: on_activity('mouse_move', (x, y)),
                on_click=lambda x, y, button, pressed: on_activity('mouse_click', (x, y, button, pressed))
            )
            self.mouse_listener.start()
            logger.info("Mouse monitoring started")
            
    def _start_webcam_monitoring(self):
        """Start webcam monitoring"""
        try:
            self.webcam = cv2.VideoCapture(0)
            if not self.webcam.isOpened():
                logger.error("Could not open webcam")
                self.components['webcam'] = False
                return
                
            self.webcam_thread = threading.Thread(target=self._webcam_loop)
            self.webcam_thread.start()
            logger.info("Webcam monitoring started")
            
        except Exception as e:
            logger.error(f"Failed to start webcam monitoring: {e}")
            self.components['webcam'] = False
            
    def _webcam_loop(self):
        """Main webcam monitoring loop"""
        last_snapshot = time.time()
        interval = self.config['data_collection']['interval']
        
        while self.is_running:
            ret, frame = self.webcam.read()
            if not ret:
                continue
                
            current_time = time.time()
            
            # Process frame for posture analysis
            if current_time - last_snapshot >= interval:
                try:
                    # Convert to RGB for MediaPipe
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = self.pose.process(rgb_frame)
                    
                    if results.pose_landmarks:
                        # Extract posture data
                        posture_data = self._analyze_posture(results.pose_landmarks)
                        
                        # Save data
                        self.data_queue.put({
                            'type': 'posture',
                            'timestamp': datetime.now().isoformat(),
                            'data': posture_data
                        })
                        
                        # Save snapshot if configured
                        if self.config['data_collection'].get('save_snapshots', True):
                            self._save_snapshot(frame)
                            
                    last_snapshot = current_time
                    
                except Exception as e:
                    logger.error(f"Error in posture analysis: {e}")
                    
            time.sleep(0.1)  # Prevent high CPU usage
            
    def _analyze_posture(self, landmarks):
        """Analyze posture from landmarks"""
        # Extract key points
        shoulder_left = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        shoulder_right = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        hip_left = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP]
        hip_right = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_HIP]
        
        # Calculate metrics
        shoulder_alignment = abs(shoulder_left.y - shoulder_right.y)
        posture_angle = self._calculate_angle(
            [shoulder_left.x, shoulder_left.y],
            [(hip_left.x + hip_right.x)/2, (hip_left.y + hip_right.y)/2],
            [shoulder_right.x, shoulder_right.y]
        )
        
        return {
            'shoulder_alignment': shoulder_alignment,
            'posture_angle': posture_angle,
            'is_good_posture': shoulder_alignment < 0.1 and 80 < posture_angle < 100
        }
        
    def _calculate_angle(self, p1, p2, p3):
        """Calculate angle between three points"""
        import numpy as np
        
        v1 = np.array([p1[0] - p2[0], p1[1] - p2[1]])
        v2 = np.array([p3[0] - p2[0], p3[1] - p2[1]])
        
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
        
        return np.degrees(angle)
        
    def _save_snapshot(self, frame):
        """Save webcam snapshot"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(
                self.config['system']['data_dir'],
                'snapshots',
                f'snapshot_{timestamp}.jpg'
            )
            cv2.imwrite(filename, frame)
        except Exception as e:
            logger.error(f"Failed to save snapshot: {e}")
            
    def _process_data(self):
        """Process and save collected data"""
        data_buffer = []
        last_save = time.time()
        
        while self.is_running or not self.data_queue.empty():
            try:
                # Get data from queue
                try:
                    data = self.data_queue.get(timeout=1)
                    data_buffer.append(data)
                except queue.Empty:
                    continue
                    
                # Save data periodically
                current_time = time.time()
                if current_time - last_save >= 60 or len(data_buffer) >= 1000:
                    self._save_data_buffer(data_buffer)
                    data_buffer = []
                    last_save = current_time
                    
            except Exception as e:
                logger.error(f"Error in data processing: {e}")
                
        # Save remaining data
        if data_buffer:
            self._save_data_buffer(data_buffer)
            
    def _save_data_buffer(self, buffer):
        """Save data buffer to file"""
        if not buffer:
            return
            
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(
                self.config['system']['data_dir'],
                'analytics',
                f'data_{timestamp}.pkl'
            )
            
            with open(filename, 'wb') as f:
                pickle.dump(buffer, f)
                
            logger.info(f"Saved {len(buffer)} data points to {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save data buffer: {e}")
            
def main():
    collector = DataCollectionModule()
    try:
        collector.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        collector.stop()
        
if __name__ == "__main__":
    main() 