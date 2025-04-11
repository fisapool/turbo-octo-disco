import unittest
from unittest.mock import MagicMock, patch
import time
from hid_system_integration import HIDSystemMonitor

class TestHIDSystemMonitor(unittest.TestCase):
    def setUp(self):
        self.config = {
            'poll_interval': 0.1,  # Faster for testing
            'data_dir': 'test_hid_system_data',
            'max_queue_size': 100
        }
        self.monitor = HIDSystemMonitor(self.config)
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_collect_system_metrics(self, mock_disk, mock_mem, mock_cpu):
        """Test system metrics collection."""
        # Mock system metrics
        mock_cpu.return_value = 50.0
        mock_mem.return_value = MagicMock(percent=75.0)
        mock_disk.return_value = MagicMock(percent=60.0)
        
        metrics = self.monitor.collect_system_metrics()
        
        self.assertIn('timestamp', metrics)
        self.assertEqual(metrics['cpu_percent'], 50.0)
        self.assertEqual(metrics['memory_percent'], 75.0)
        self.assertEqual(metrics['disk_percent'], 60.0)
        self.assertIn('system_info', metrics)
    
    @patch('hid_system_integration.HIDSystemMonitor._get_keyboard_events')
    @patch('hid_system_integration.HIDSystemMonitor._get_mouse_events')
    @patch('hid_system_integration.HIDSystemMonitor._get_active_window')
    def test_collect_hid_metrics(self, mock_window, mock_mouse, mock_keyboard):
        """Test HID metrics collection."""
        # Mock HID metrics
        mock_keyboard.return_value = {
            'key_presses': 10,
            'key_releases': 10,
            'typing_speed': 60
        }
        mock_mouse.return_value = {
            'clicks': 5,
            'movement': 100,
            'scroll_events': 2
        }
        mock_window.return_value = "Test Window"
        
        metrics = self.monitor.collect_hid_metrics()
        
        self.assertIn('timestamp', metrics)
        self.assertIn('keyboard_events', metrics)
        self.assertIn('mouse_events', metrics)
        self.assertEqual(metrics['active_window'], "Test Window")
    
    def test_monitoring_control(self):
        """Test start/stop monitoring functionality."""
        # Start monitoring
        self.monitor.start_monitoring()
        self.assertTrue(self.monitor.is_monitoring)
        
        # Let it run for a short time
        time.sleep(0.2)
        
        # Stop monitoring
        self.monitor.stop_monitoring()
        self.assertFalse(self.monitor.is_monitoring)
    
    def test_data_queue(self):
        """Test data queue functionality."""
        # Start monitoring
        self.monitor.start_monitoring()
        
        # Let it collect some data
        time.sleep(0.3)
        
        # Stop monitoring
        self.monitor.stop_monitoring()
        
        # Check if data was collected
        self.assertGreater(self.monitor.data_queue.qsize(), 0)
    
    @patch('hid_system_integration.HIDSystemMonitor.save_queued_data')
    def test_queue_size_limit(self, mock_save):
        """Test queue size limit and auto-save."""
        # Fill the queue
        for _ in range(self.config['max_queue_size'] + 10):
            self.monitor.data_queue.put({'test': 'data'})
        
        # Check if save was called
        mock_save.assert_called()
    
    def test_get_current_metrics(self):
        """Test getting current metrics."""
        # Add some test data
        test_data = {'test': 'data'}
        self.monitor.data_queue.put(test_data)
        
        # Get current metrics
        metrics = self.monitor.get_current_metrics()
        
        self.assertEqual(metrics, test_data)

if __name__ == '__main__':
    unittest.main() 