import unittest
from unittest.mock import MagicMock, patch
import numpy as np
from webcam_integration import WebcamAnalyzer
import cv2
import os
import tempfile
import time

class TestWebcamAnalyzer(unittest.TestCase):
    def setUp(self):
        self.config = {
            'snapshot_interval': 5,
            'recording_duration': 30,
            'data_dir': 'test_webcam_data',
            'posture_threshold': 0.7,
            'max_frame_size': (1920, 1080),
            'min_frame_size': (640, 480)
        }
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        # Clean up temporary files
        if os.path.exists(self.temp_dir):
            for file in os.listdir(self.temp_dir):
                os.remove(os.path.join(self.temp_dir, file))
            os.rmdir(self.temp_dir)
            
    @patch('cv2.VideoCapture')
    def test_initialization(self, mock_video_capture):
        """Test WebcamAnalyzer initialization."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_video_capture.return_value = mock_cap
        
        analyzer = WebcamAnalyzer(self.config)
        
        self.assertEqual(analyzer.config, self.config)
        self.assertFalse(analyzer.is_recording)
        self.assertEqual(analyzer.last_snapshot_time, 0)
        
    @patch('cv2.VideoCapture')
    def test_posture_analysis(self, mock_video_capture):
        """Test posture analysis functionality."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_video_capture.return_value = mock_cap
        
        analyzer = WebcamAnalyzer(self.config)
        
        # Create a mock frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Mock MediaPipe pose detection
        with patch.object(analyzer.pose, 'process') as mock_process:
            mock_landmarks = MagicMock()
            mock_landmarks.landmark = {
                analyzer.mp_pose.PoseLandmark.LEFT_SHOULDER: MagicMock(y=0.5),
                analyzer.mp_pose.PoseLandmark.RIGHT_SHOULDER: MagicMock(y=0.5),
                analyzer.mp_pose.PoseLandmark.NOSE: MagicMock(x=0.5),
                analyzer.mp_pose.PoseLandmark.MID_HIP: MagicMock(x=0.5),
                analyzer.mp_pose.PoseLandmark.NECK: MagicMock(x=0.5)
            }
            mock_process.return_value.pose_landmarks = mock_landmarks
            
            analysis = analyzer.analyze_posture(frame)
            
            self.assertTrue(analysis['detected'])
            self.assertIn('posture_quality', analysis)
            self.assertIn('shoulder_alignment', analysis)
            self.assertIn('back_straightness', analysis)
            self.assertIn('head_position', analysis)
            
    @patch('cv2.VideoCapture')
    def test_recording_control(self, mock_video_capture):
        """Test recording start/stop functionality."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_video_capture.return_value = mock_cap
        
        analyzer = WebcamAnalyzer(self.config)
        
        # Test start recording
        analyzer.start_recording()
        self.assertTrue(analyzer.is_recording)
        
        # Test stop recording
        analyzer.stop_recording()
        self.assertFalse(analyzer.is_recording)
        
    @patch('cv2.VideoCapture')
    def test_snapshot_capture(self, mock_video_capture):
        """Test snapshot capture functionality."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_video_capture.return_value = mock_cap
        
        analyzer = WebcamAnalyzer(self.config)
        
        with patch.object(analyzer, 'analyze_posture') as mock_analyze:
            mock_analyze.return_value = {'posture_quality': 0.8, 'detected': True}
            
            analysis = analyzer.capture_snapshot()
            
            self.assertIsNotNone(analysis)
            self.assertEqual(analysis['posture_quality'], 0.8)
            
    @patch('cv2.VideoCapture')
    def test_camera_not_available(self, mock_video_capture):
        """Test behavior when camera is not available."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_video_capture.return_value = mock_cap
        
        with self.assertRaises(RuntimeError):
            WebcamAnalyzer(self.config)
            
    @patch('cv2.VideoCapture')
    def test_frame_size_validation(self, mock_video_capture):
        """Test frame size validation."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, np.zeros((1080, 1920, 3), dtype=np.uint8))
        mock_video_capture.return_value = mock_cap
        
        analyzer = WebcamAnalyzer(self.config)
        
        # Test frame too large
        with self.assertRaises(ValueError):
            analyzer.validate_frame_size(np.zeros((2160, 3840, 3), dtype=np.uint8))
            
        # Test frame too small
        with self.assertRaises(ValueError):
            analyzer.validate_frame_size(np.zeros((320, 240, 3), dtype=np.uint8))
            
    @patch('cv2.VideoCapture')
    def test_data_saving(self, mock_video_capture):
        """Test data saving functionality."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_video_capture.return_value = mock_cap
        
        analyzer = WebcamAnalyzer(self.config)
        analyzer.data_dir = self.temp_dir
        
        # Test saving analysis data
        analysis_data = {
            'timestamp': '2024-04-10T12:00:00',
            'posture_quality': 0.8,
            'detected': True
        }
        
        analyzer.save_analysis_data(analysis_data)
        
        # Verify file was created
        files = os.listdir(self.temp_dir)
        self.assertTrue(any(f.endswith('.json') for f in files))
        
    @patch('cv2.VideoCapture')
    def test_error_handling(self, mock_video_capture):
        """Test error handling in various scenarios."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_video_capture.return_value = mock_cap
        
        analyzer = WebcamAnalyzer(self.config)
        
        # Test invalid frame
        with self.assertRaises(ValueError):
            analyzer.analyze_posture(None)
            
        # Test recording when already recording
        analyzer.start_recording()
        with self.assertRaises(RuntimeError):
            analyzer.start_recording()
            
        # Test stopping when not recording
        analyzer.stop_recording()
        with self.assertRaises(RuntimeError):
            analyzer.stop_recording()
            
    @patch('cv2.VideoCapture')
    def test_performance_metrics(self, mock_video_capture):
        """Test performance metrics collection."""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.read.return_value = (True, np.zeros((480, 640, 3), dtype=np.uint8))
        mock_video_capture.return_value = mock_cap
        
        analyzer = WebcamAnalyzer(self.config)
        
        # Test frame processing time
        start_time = time.time()
        analyzer.process_frame(np.zeros((480, 640, 3), dtype=np.uint8))
        processing_time = time.time() - start_time
        
        self.assertLess(processing_time, 0.1)  # Should process frame in less than 100ms
        
        # Test memory usage
        import psutil
        process = psutil.Process()
        memory_usage = process.memory_info().rss / 1024 / 1024  # MB
        self.assertLess(memory_usage, 500)  # Should use less than 500MB
        
if __name__ == '__main__':
    unittest.main() 