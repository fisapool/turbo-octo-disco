import cv2
import numpy as np
import mediapipe as mp
import time
from datetime import datetime
import json
import os
from pathlib import Path
import logging
from typing import Dict, List, Optional, Tuple
import threading
from mediapipe.python.solutions import pose as mp_pose
from mediapipe.python.solutions import face_detection as mp_face_detection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WebcamIntegration:
    def __init__(self, config_path='config.json'):
        self.camera = None
        self.is_recording = False
        self.recording_thread = None
        self.analysis_thread = None
        self.config = self._load_config(config_path)
        self.pose_analyzer = mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.face_detector = mp_face_detection.FaceDetection(
            min_detection_confidence=0.5
        )
        self.data_buffer = []
        self.last_save_time = time.time()
        
    def _load_config(self, config_path):
        default_config = {
            'recording_interval': 5,  # seconds
            'snapshot_interval': 30,  # seconds
            'data_save_interval': 300,  # seconds
            'output_dir': 'webcam_data',
            'max_recording_duration': 60,  # seconds
            'posture_threshold': 0.7,
            'face_detection_interval': 1  # seconds
        }
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                return {**default_config, **config}
        except FileNotFoundError:
            return default_config
            
    def start(self):
        """Initialize and start the webcam integration"""
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            raise Exception("Could not open webcam")
            
        # Create output directory if it doesn't exist
        os.makedirs(self.config['output_dir'], exist_ok=True)
        
        self.is_recording = True
        self.recording_thread = threading.Thread(target=self._recording_loop)
        self.analysis_thread = threading.Thread(target=self._analysis_loop)
        
        self.recording_thread.start()
        self.analysis_thread.start()
        
    def stop(self):
        """Stop the webcam integration"""
        self.is_recording = False
        if self.recording_thread:
            self.recording_thread.join()
        if self.analysis_thread:
            self.analysis_thread.join()
        if self.camera:
            self.camera.release()
            
    def _recording_loop(self):
        """Main recording loop for capturing video and snapshots"""
        last_snapshot_time = time.time()
        recording_start_time = None
        current_recording = []
        
        while self.is_recording:
            ret, frame = self.camera.read()
            if not ret:
                continue
                
            current_time = time.time()
            
            # Take snapshots at regular intervals
            if current_time - last_snapshot_time >= self.config['snapshot_interval']:
                self._save_snapshot(frame)
                last_snapshot_time = current_time
                
            # Record video clips
            if recording_start_time is None:
                recording_start_time = current_time
                
            current_recording.append(frame)
            
            # Save recording if duration reached
            if current_time - recording_start_time >= self.config['max_recording_duration']:
                self._save_recording(current_recording)
                current_recording = []
                recording_start_time = None
                
            # Save data periodically
            if current_time - self.last_save_time >= self.config['data_save_interval']:
                self._save_data()
                self.last_save_time = current_time
                
    def _analysis_loop(self):
        """Main analysis loop for posture and face detection"""
        last_face_detection_time = time.time()
        
        while self.is_recording:
            ret, frame = self.camera.read()
            if not ret:
                continue
                
            current_time = time.time()
            
            # Perform posture analysis
            posture_data = self._analyze_posture(frame)
            if posture_data:
                self.data_buffer.append({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'posture',
                    'data': posture_data
                })
                
            # Perform face detection at regular intervals
            if current_time - last_face_detection_time >= self.config['face_detection_interval']:
                face_data = self._detect_faces(frame)
                if face_data:
                    self.data_buffer.append({
                        'timestamp': datetime.now().isoformat(),
                        'type': 'face',
                        'data': face_data
                    })
                last_face_detection_time = current_time
                
    def _analyze_posture(self, frame):
        """Analyze posture using MediaPipe Pose"""
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process the frame
            results = self.pose_analyzer.process(rgb_frame)
            
            if results.pose_landmarks:
                # Calculate posture score based on key points
                landmarks = results.pose_landmarks.landmark
                
                # Example: Check if shoulders are level
                left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
                right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
                
                shoulder_level = abs(left_shoulder.y - right_shoulder.y)
                
                # Example: Check if back is straight
                left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
                right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]
                left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
                
                back_angle = self._calculate_angle(
                    [left_hip.x, left_hip.y],
                    [left_shoulder.x, left_shoulder.y],
                    [right_hip.x, right_hip.y]
                )
                
                return {
                    'shoulder_level': float(shoulder_level),
                    'back_angle': float(back_angle),
                    'posture_score': float(1.0 - min(shoulder_level, 1.0))
                }
                
        except Exception as e:
            print(f"Error in posture analysis: {e}")
            return None
            
    def _detect_faces(self, frame):
        """Detect faces using MediaPipe Face Detection"""
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process the frame
            results = self.face_detector.process(rgb_frame)
            
            if results.detections:
                faces = []
                for detection in results.detections:
                    bbox = detection.location_data.relative_bounding_box
                    faces.append({
                        'confidence': detection.score[0],
                        'bounding_box': {
                            'x': float(bbox.xmin),
                            'y': float(bbox.ymin),
                            'width': float(bbox.width),
                            'height': float(bbox.height)
                        }
                    })
                return faces
                
        except Exception as e:
            print(f"Error in face detection: {e}")
            return None
            
    def _calculate_angle(self, point1, point2, point3):
        """Calculate angle between three points"""
        v1 = np.array([point1[0] - point2[0], point1[1] - point2[1]])
        v2 = np.array([point3[0] - point2[0], point3[1] - point2[1]])
        
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
        
        return np.degrees(angle)
        
    def _save_snapshot(self, frame):
        """Save a snapshot of the current frame"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.config['output_dir'], f"snapshot_{timestamp}.jpg")
        cv2.imwrite(filename, frame)
        
    def _save_recording(self, frames):
        """Save a video recording"""
        if not frames:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.config['output_dir'], f"recording_{timestamp}.avi")
        
        height, width = frames[0].shape[:2]
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(filename, fourcc, 20.0, (width, height))
        
        for frame in frames:
            out.write(frame)
        out.release()
        
    def _save_data(self):
        """Save collected data to JSON file"""
        if not self.data_buffer:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.config['output_dir'], f"data_{timestamp}.json")
        
        with open(filename, 'w') as f:
            json.dump(self.data_buffer, f, indent=2)
            
        self.data_buffer = []

if __name__ == "__main__":
    integration = WebcamIntegration()
    integration.start() 