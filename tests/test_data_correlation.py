import unittest
from unittest.mock import MagicMock, patch
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from data_correlation import DataCorrelator

class TestDataCorrelator(unittest.TestCase):
    def setUp(self):
        self.config = {
            'webcam_data_dir': 'test_webcam_data',
            'hid_data_dir': 'test_hid_data',
            'correlation_data_dir': 'test_correlation_data',
            'time_window': 300,
            'correlation_interval': 3600
        }
        self.correlator = DataCorrelator(self.config)
        
        # Create test directories
        Path(self.config['webcam_data_dir']).mkdir(exist_ok=True)
        Path(self.config['hid_data_dir']).mkdir(exist_ok=True)
        Path(self.config['correlation_data_dir']).mkdir(exist_ok=True)
    
    def tearDown(self):
        # Clean up test files
        for path in [
            Path(self.config['webcam_data_dir']),
            Path(self.config['hid_data_dir']),
            Path(self.config['correlation_data_dir'])
        ]:
            if path.exists():
                for file in path.glob('*'):
                    file.unlink()
                path.rmdir()
    
    def create_test_webcam_data(self, timestamp: datetime) -> None:
        """Create test webcam data file."""
        data = {
            'timestamp': timestamp.isoformat(),
            'posture': {
                'posture_quality': 0.8,
                'shoulder_alignment': 0.9,
                'back_straightness': 0.7,
                'head_position': 0.8,
                'detected': True
            },
            'faces': [
                {
                    'confidence': 0.95,
                    'bounding_box': {'x': 100, 'y': 100, 'width': 200, 'height': 200}
                }
            ]
        }
        
        file_path = Path(self.config['webcam_data_dir']) / f"analysis_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        with open(file_path, 'w') as f:
            json.dump(data, f)
    
    def create_test_hid_data(self, timestamp: datetime) -> None:
        """Create test HID data file."""
        data = {
            'timestamp': timestamp.isoformat(),
            'system': {
                'cpu_percent': 50.0,
                'memory_percent': 60.0,
                'disk_percent': 70.0,
                'process_count': 100
            },
            'hid': {
                'keyboard_events': {
                    'key_presses': 100,
                    'key_releases': 100,
                    'typing_speed': 60
                },
                'mouse_events': {
                    'clicks': 50,
                    'movement': 1000,
                    'scroll_events': 20
                },
                'active_window': 'Test Window'
            }
        }
        
        file_path = Path(self.config['hid_data_dir']) / f"metrics_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        with open(file_path, 'w') as f:
            json.dump(data, f)
    
    def test_load_webcam_data(self):
        """Test loading webcam data."""
        now = datetime.now()
        self.create_test_webcam_data(now)
        
        data = self.correlator.load_webcam_data(
            now - timedelta(hours=1),
            now + timedelta(hours=1)
        )
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['posture']['posture_quality'], 0.8)
    
    def test_load_hid_data(self):
        """Test loading HID data."""
        now = datetime.now()
        self.create_test_hid_data(now)
        
        data = self.correlator.load_hid_data(
            now - timedelta(hours=1),
            now + timedelta(hours=1)
        )
        
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['system']['cpu_percent'], 50.0)
    
    def test_correlate_data(self):
        """Test data correlation."""
        now = datetime.now()
        
        # Create test data for the last hour
        for minutes in range(0, 60, 5):
            timestamp = now - timedelta(minutes=minutes)
            self.create_test_webcam_data(timestamp)
            self.create_test_hid_data(timestamp)
        
        correlations = self.correlator.correlate_data(now - timedelta(hours=1))
        
        self.assertIn('posture_vs_activity', correlations)
        self.assertIn('system_impact', correlations)
        self.assertIn('time_patterns', correlations)
        self.assertIn('environmental_factors', correlations)
    
    def test_analyze_posture_activity_correlation(self):
        """Test posture and activity correlation analysis."""
        df = pd.DataFrame({
            'posture_quality': [0.8, 0.7, 0.6],
            'key_presses': [100, 200, 300],
            'mouse_clicks': [50, 100, 150]
        })
        
        correlations = self.correlator._analyze_posture_activity_correlation(df)
        
        self.assertIn('activity_impact', correlations)
        self.assertIn('high_activity_posture', correlations)
    
    def test_analyze_system_impact(self):
        """Test system impact analysis."""
        df = pd.DataFrame({
            'posture_quality': [0.8, 0.7, 0.6],
            'cpu_percent': [50, 60, 70],
            'key_presses': [100, 200, 300],
            'mouse_clicks': [50, 100, 150]
        })
        
        correlations = self.correlator._analyze_system_impact(df)
        
        self.assertIn('cpu_impact', correlations)
        self.assertIn('activity_cpu_correlation', correlations)
    
    def test_analyze_environmental_factors(self):
        """Test environmental factors analysis."""
        df = pd.DataFrame({
            'posture_quality': [0.8, 0.7, 0.6],
            'cpu_percent': [50, 85, 90],
            'key_presses': [100, 200, 300],
            'face_count': [1, 1, 0]
        })
        
        factors = self.correlator._analyze_environmental_factors(df)
        
        self.assertIn('high_load_impact', factors)
        self.assertIn('face_detection_impact', factors)
    
    def test_get_latest_correlation(self):
        """Test retrieving latest correlation results."""
        test_data = {'test': 'data'}
        timestamp = datetime.now()
        
        file_path = Path(self.config['correlation_data_dir']) / f"correlation_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        with open(file_path, 'w') as f:
            json.dump(test_data, f)
        
        latest = self.correlator.get_latest_correlation()
        self.assertEqual(latest, test_data)

if __name__ == '__main__':
    unittest.main() 