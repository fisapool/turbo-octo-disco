import cv2
import numpy as np
from datetime import datetime
import os
import json
import threading
from typing import Dict, Any, Optional

class WebcamRecorder:
    def __init__(self, data_dir: str = "data/webcam"):
        self.data_dir = data_dir
        self.cap = None
        self.is_running = False
        self.frame_count = 0
        self.last_capture_time = None
        self.capture_interval = 5  # seconds
        self.lock = threading.Lock()
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize face cascade for basic posture detection
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

    def start(self):
        if not self.is_running:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                raise Exception("Could not open webcam")
            
            self.is_running = True
            self.capture_thread = threading.Thread(target=self._capture_loop)
            self.capture_thread.daemon = True
            self.capture_thread.start()

    def stop(self):
        if self.is_running:
            self.is_running = False
            if self.cap:
                self.cap.release()
            self.cap = None

    def _capture_loop(self):
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            current_time = datetime.now()
            
            # Check if it's time to capture a new frame
            if (self.last_capture_time is None or 
                (current_time - self.last_capture_time).total_seconds() >= self.capture_interval):
                
                # Analyze frame
                analysis = self._analyze_frame(frame)
                
                # Save frame and analysis
                self._save_frame(frame, analysis)
                
                self.last_capture_time = current_time
                self.frame_count += 1

    def _analyze_frame(self, frame) -> Dict[str, Any]:
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        # Basic posture analysis
        posture = "unknown"
        if len(faces) > 0:
            # Get the largest face
            largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
            x, y, w, h = largest_face
            
            # Simple posture estimation based on face position
            if y < frame.shape[0] * 0.3:
                posture = "leaning_forward"
            elif y > frame.shape[0] * 0.7:
                posture = "leaning_back"
            else:
                posture = "neutral"
        
        return {
            'timestamp': datetime.now().isoformat(),
            'posture': posture,
            'face_detected': len(faces) > 0,
            'face_count': len(faces)
        }

    def _save_frame(self, frame, analysis: Dict[str, Any]):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save image
        image_path = os.path.join(
            self.data_dir,
            f"frame_{timestamp}.jpg"
        )
        cv2.imwrite(image_path, frame)
        
        # Save analysis
        analysis_path = os.path.join(
            self.data_dir,
            f"analysis_{timestamp}.json"
        )
        with open(analysis_path, 'w') as f:
            json.dump(analysis, f, indent=2)

    def get_recent_analysis(self, limit: int = 10) -> list:
        analysis_files = sorted(
            [f for f in os.listdir(self.data_dir) if f.startswith('analysis_')],
            reverse=True
        )[:limit]
        
        results = []
        for file in analysis_files:
            with open(os.path.join(self.data_dir, file), 'r') as f:
                results.append(json.load(f))
        
        return results 