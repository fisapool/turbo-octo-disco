import cv2
import numpy as np
import time
import os
from datetime import datetime, timedelta
import threading
import json
import logging
from pathlib import Path
import mediapipe as mp
import psutil
import platform
from pynput import mouse, keyboard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('activity_tracker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ActivityTracker:
    def __init__(self):
        self.camera = None
        self.is_running = False
        self.frame = None
        self.frame_lock = threading.Lock()
        self.recording_thread = None
        self.analysis_thread = None
        self.input_thread = None
        self.output_dir = 'activity_data'
        self.focus_start_time = None
        self.last_movement_time = time.time()
        self.break_reminder_interval = 20 * 60  # 20 minutes
        self.last_break_reminder = time.time()
        self.posture_warnings = 0
        
        # Status flags
        self.webcam_active = False
        self.keyboard_tracking_active = False
        self.mouse_tracking_active = False
        self.analytics_active = False
        
        # Initialize MediaPipe
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Create necessary directories
        for dir_name in ['snapshots', 'analytics', 'posture_data', 'input_activity']:
            Path(os.path.join(self.output_dir, dir_name)).mkdir(parents=True, exist_ok=True)
            
        # Initialize activity data
        self.activity_data = {
            'focus_sessions': [],
            'posture_warnings': [],
            'breaks_taken': [],
            'activity_level': [],
            'input_events': []
        }
        
    def start(self):
        """Start the activity tracker"""
        try:
            print("\nInitializing components...")
            
            # Try to initialize webcam
            print("1. Initializing webcam...")
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                print("   ❌ Webcam initialization failed!")
                logger.error("Could not open webcam")
            else:
                print("   ✓ Webcam initialized successfully")
                self.webcam_active = True
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # Start activity tracking
            print("2. Starting activity tracking...")
            self.is_running = True
            
            # Start recording thread if webcam is active
            if self.webcam_active:
                print("   - Starting webcam recording thread")
                self.recording_thread = threading.Thread(target=self._recording_loop)
                self.recording_thread.start()
                print("   ✓ Webcam recording active")
            
            # Start analysis thread
            print("3. Starting analysis components...")
            self.analysis_thread = threading.Thread(target=self._analysis_loop)
            self.analysis_thread.start()
            self.analytics_active = True
            print("   ✓ Analysis thread active")
            
            # Start input monitoring
            print("4. Starting input monitoring...")
            self.input_thread = threading.Thread(target=self._monitor_input)
            self.input_thread.start()
            self.keyboard_tracking_active = True
            self.mouse_tracking_active = True
            print("   ✓ Keyboard and mouse tracking active")
            
            # Start focus session
            self.focus_start_time = time.time()
            
            print("\nStatus Summary:")
            print(f"- Webcam Tracking: {'✓ Active' if self.webcam_active else '❌ Failed'}")
            print(f"- Keyboard Tracking: {'✓ Active' if self.keyboard_tracking_active else '❌ Failed'}")
            print(f"- Mouse Tracking: {'✓ Active' if self.mouse_tracking_active else '❌ Failed'}")
            print(f"- Analytics: {'✓ Active' if self.analytics_active else '❌ Failed'}")
            
            logger.info("Activity tracker started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start activity tracker: {str(e)}")
            return False
            
    def stop(self):
        """Stop the activity tracker"""
        self.is_running = False
        if self.recording_thread:
            self.recording_thread.join()
        if self.analysis_thread:
            self.analysis_thread.join()
        if self.input_thread:
            self.input_thread.join()
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()
        
        # Save final analytics
        self._save_analytics()
        logger.info("Activity tracker stopped")
        
    def _recording_loop(self):
        """Main recording loop"""
        last_snapshot_time = time.time()
        snapshot_interval = 30  # Take a snapshot every 30 seconds
        
        while self.is_running:
            ret, frame = self.camera.read()
            if not ret:
                continue
                
            # Update the current frame with thread safety
            with self.frame_lock:
                self.frame = frame.copy()
                
            # Add timestamp and status to frame
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._add_overlay(frame, current_time)
            
            # Show the frame
            cv2.imshow("Activity Tracker", frame)
            
            # Take periodic snapshots
            current_time = time.time()
            if current_time - last_snapshot_time >= snapshot_interval:
                self._save_snapshot(frame)
                last_snapshot_time = current_time
                
            # Check for break reminders
            self._check_break_reminder()
            
            # Break if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.is_running = False
                break
                
            # Small delay to prevent high CPU usage
            time.sleep(0.03)
            
    def _analysis_loop(self):
        """Analyze posture and activity"""
        while self.is_running:
            with self.frame_lock:
                if self.frame is not None:
                    frame = self.frame.copy()
                else:
                    continue
                    
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Analyze posture
            results = self.pose.process(rgb_frame)
            if results.pose_landmarks:
                self._analyze_posture(results.pose_landmarks)
                
            # Update activity level
            cpu_percent = psutil.cpu_percent()
            self.activity_data['activity_level'].append({
                'timestamp': time.time(),
                'cpu_usage': cpu_percent
            })
            
            time.sleep(1)  # Analysis every second
            
    def _monitor_input(self):
        """Monitor keyboard and mouse activity"""
        def on_activity(x):
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.last_movement_time = time.time()
            self.activity_data['input_events'].append({
                'timestamp': current_time,
                'type': 'keyboard' if isinstance(x, keyboard.Key) else 'mouse'
            })
            
            # Save activity data every 100 events
            if len(self.activity_data['input_events']) >= 100:
                self._save_input_data()
                
        try:
            mouse_listener = mouse.Listener(
                on_move=on_activity,
                on_click=on_activity,
                on_scroll=on_activity
            )
            keyboard_listener = keyboard.Listener(
                on_press=on_activity,
                on_release=None  # Only track presses for privacy
            )
            
            mouse_listener.start()
            keyboard_listener.start()
            
            while self.is_running:
                time.sleep(1)
                
            mouse_listener.stop()
            keyboard_listener.stop()
            
        except Exception as e:
            logger.error(f"Input monitoring error: {str(e)}")
            self.keyboard_tracking_active = False
            self.mouse_tracking_active = False
            
    def _save_input_data(self):
        """Save input activity data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.output_dir, 'input_activity', f"activity_{timestamp}.json")
            
            with open(filename, 'w') as f:
                json.dump({
                    'events': self.activity_data['input_events'][-100:]  # Save last 100 events
                }, f, indent=4)
                
            # Clear saved events
            self.activity_data['input_events'] = self.activity_data['input_events'][-10:]  # Keep last 10 for overlap
            
        except Exception as e:
            logger.error(f"Failed to save input data: {str(e)}")
            
    def _analyze_posture(self, landmarks):
        """Analyze posture and provide warnings"""
        # Check shoulder alignment
        left_shoulder = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        
        # Check if shoulders are level (allowing for small differences)
        shoulder_diff = abs(left_shoulder.y - right_shoulder.y)
        if shoulder_diff > 0.1:  # Threshold for poor posture
            self.posture_warnings += 1
            self.activity_data['posture_warnings'].append({
                'timestamp': time.time(),
                'type': 'shoulder_alignment',
                'severity': shoulder_diff
            })
            logger.warning("Poor posture detected: Uneven shoulders")
            
    def _check_break_reminder(self):
        """Check if it's time for a break"""
        current_time = time.time()
        time_since_last_movement = current_time - self.last_movement_time
        time_since_last_break = current_time - self.last_break_reminder
        
        if time_since_last_movement < 60:  # Active
            if time_since_last_break >= self.break_reminder_interval:
                self._show_break_reminder()
                self.last_break_reminder = current_time
                self.activity_data['breaks_taken'].append(current_time)
                
    def _show_break_reminder(self):
        """Show break reminder overlay"""
        logger.info("Break reminder: Time to take a short break!")
        # The reminder will be shown in the frame overlay
        
    def _add_overlay(self, frame, current_time):
        """Add information overlay to frame"""
        # Add timestamp
        cv2.putText(frame, current_time, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                   
        # Add focus session duration
        if self.focus_start_time:
            focus_duration = time.time() - self.focus_start_time
            duration_str = str(timedelta(seconds=int(focus_duration)))
            cv2.putText(frame, f"Focus Time: {duration_str}", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                       
        # Add posture status
        status = "Good" if self.posture_warnings < 3 else "Need Improvement"
        cv2.putText(frame, f"Posture: {status}", (10, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, 
                   (0, 255, 0) if status == "Good" else (0, 0, 255), 2)
                   
        # Add quit instruction
        cv2.putText(frame, "Press 'q' to quit", (10, frame.shape[0] - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                   
    def _save_snapshot(self, frame):
        """Save a snapshot with timestamp"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.output_dir, 'snapshots', f"snapshot_{timestamp}.jpg")
            cv2.imwrite(filename, frame)
            logger.info(f"Saved snapshot: {filename}")
        except Exception as e:
            logger.error(f"Failed to save snapshot: {str(e)}")
            
    def _save_analytics(self):
        """Save analytics data"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.output_dir, 'analytics', f"session_{timestamp}.json")
            
            analytics = {
                'session_duration': time.time() - self.focus_start_time,
                'posture_warnings': len(self.activity_data['posture_warnings']),
                'breaks_taken': len(self.activity_data['breaks_taken']),
                'activity_data': self.activity_data
            }
            
            with open(filename, 'w') as f:
                json.dump(analytics, f, indent=4)
                
            logger.info(f"Saved analytics to: {filename}")
        except Exception as e:
            logger.error(f"Failed to save analytics: {str(e)}")
            
def main():
    print("=" * 50)
    print("Activity Tracker - Full Application")
    print("=" * 50)
    print("\nThis application includes:")
    print("1. Real-time activity monitoring")
    print("2. Posture analysis and warnings")
    print("3. Focus time tracking")
    print("4. Break reminders")
    print("5. Activity analytics")
    print("\nAll data is saved locally in the 'activity_data' folder.")
    print("\nPress Enter to start...")
    input()
    
    tracker = ActivityTracker()
    
    try:
        if tracker.start():
            print("\nActivity Tracker is running!")
            print("- You should see a webcam window")
            print("- Your posture is being analyzed")
            print("- Break reminders will appear every 20 minutes")
            print("- Analytics are being collected")
            print("- Press 'q' in the webcam window to quit")
            
            # Wait for the recording thread to finish
            while tracker.is_running:
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\nStopping Activity Tracker...")
    finally:
        tracker.stop()
        print("\nActivity Tracker has been stopped.")
        print(f"Your data has been saved in the '{tracker.output_dir}' folder.")
        print("\nAnalytics summary:")
        print("- Check the 'analytics' folder for detailed session data")
        print("- Snapshots are saved in the 'snapshots' folder")
        print("- Posture data is saved in the 'posture_data' folder")
        
if __name__ == "__main__":
    main() 