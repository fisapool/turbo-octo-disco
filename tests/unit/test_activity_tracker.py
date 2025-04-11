import pytest
from unittest.mock import Mock, patch
import json
import time
from datetime import datetime
from app.modules.activity_tracker import ActivityTracker, ActivityData

class TestActivityTracker:
    @pytest.fixture
    def activity_tracker(self):
        return ActivityTracker()

    def test_initialization(self, activity_tracker):
        assert activity_tracker.is_running is False
        assert activity_tracker.data_file is not None
        assert activity_tracker.inactivity_threshold == 300  # 5 minutes

    def test_start_stop(self, activity_tracker):
        activity_tracker.start()
        assert activity_tracker.is_running is True
        
        activity_tracker.stop()
        assert activity_tracker.is_running is False

    def test_keyboard_event_capture(self, activity_tracker):
        with patch('keyboard.is_pressed', return_value=True):
            activity_tracker.start()
            time.sleep(0.1)  # Allow time for event capture
            activity_tracker.stop()
            
            assert len(activity_tracker.activity_data) > 0
            assert 'keyboard' in activity_tracker.activity_data[0]['type']

    def test_mouse_event_capture(self, activity_tracker):
        with patch('mouse.get_position', return_value=(100, 100)):
            activity_tracker.start()
            time.sleep(0.1)
            activity_tracker.stop()
            
            assert len(activity_tracker.activity_data) > 0
            assert 'mouse' in activity_tracker.activity_data[0]['type']

    def test_inactivity_detection(self, activity_tracker):
        activity_tracker.inactivity_threshold = 1  # Set to 1 second for testing
        activity_tracker.start()
        time.sleep(1.5)  # Wait longer than threshold
        activity_tracker.stop()
        
        assert any('inactivity' in event['type'] for event in activity_tracker.activity_data)

    def test_data_saving(self, activity_tracker, tmp_path):
        test_data_file = tmp_path / "test_activity.json"
        activity_tracker.data_file = str(test_data_file)
        
        activity_tracker.start()
        time.sleep(0.1)
        activity_tracker.stop()
        activity_tracker.save_data()
        
        assert test_data_file.exists()
        with open(test_data_file, 'r') as f:
            saved_data = json.load(f)
            assert len(saved_data) > 0

    def test_data_validation(self, activity_tracker):
        activity_tracker.start()
        time.sleep(0.1)
        activity_tracker.stop()
        
        for event in activity_tracker.activity_data:
            assert 'timestamp' in event
            assert 'type' in event
            assert isinstance(event['timestamp'], str)
            assert isinstance(event['type'], str)

    def test_thread_safety(self, activity_tracker):
        activity_tracker.start()
        
        # Simulate concurrent access
        def modify_data():
            activity_tracker.activity_data.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'test'
            })
        
        import threading
        threads = [threading.Thread(target=modify_data) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
            
        activity_tracker.stop()
        assert len(activity_tracker.activity_data) >= 10

    def test_error_handling(self, activity_tracker):
        with patch('keyboard.is_pressed', side_effect=Exception("Test error")):
            activity_tracker.start()
            time.sleep(0.1)
            activity_tracker.stop()
            
            # Verify the tracker continues running despite errors
            assert activity_tracker.is_running is False

    def test_performance(self, activity_tracker):
        import timeit
        
        def test_operation():
            activity_tracker.start()
            time.sleep(0.1)
            activity_tracker.stop()
        
        execution_time = timeit.timeit(test_operation, number=100)
        assert execution_time < 20  # Should complete 100 operations in under 20 seconds 