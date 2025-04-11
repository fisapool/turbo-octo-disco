import unittest
from datetime import datetime, timedelta
import numpy as np
from advanced_data_sync import AdvancedDataSynchronizer, TimeSeriesPoint, SynchronizedDataPoint

class TestAdvancedDataSynchronizer(unittest.TestCase):
    def setUp(self):
        self.synchronizer = AdvancedDataSynchronizer(
            sync_window_ms=1000,
            max_buffer_size=1000,
            correlation_window=300,
            optimization_config={
                'use_caching': True,
                'cache_size': 1000,
                'parallel_processing': True,
                'batch_size': 100,
                'compression': {
                    'enabled': True,
                    'level': 6,
                    'algorithm': 'gzip'
                }
            }
        )
        
        # Create test data
        self.test_data = {
            'stream1': {
                'value': 10.5,
                'confidence': 0.9,
                'metadata': {'source': 'sensor1'}
            },
            'stream2': {
                'value': 20.3,
                'confidence': 0.8,
                'metadata': {'source': 'sensor2'}
            }
        }
    
    def test_add_data_stream(self):
        """Test adding data streams."""
        timestamp = datetime.now().isoformat()
        
        # Add first stream
        result = self.synchronizer.add_data_stream(
            'stream1',
            self.test_data['stream1'],
            timestamp
        )
        self.assertTrue(result)
        
        # Add second stream
        result = self.synchronizer.add_data_stream(
            'stream2',
            self.test_data['stream2'],
            timestamp
        )
        self.assertTrue(result)
        
        # Verify stream count
        self.assertEqual(len(self.synchronizer.data_buffer), 2)
    
    def test_synchronize_data(self):
        """Test data synchronization."""
        timestamp = datetime.now().isoformat()
        
        # Add data streams
        self.synchronizer.add_data_stream(
            'stream1',
            self.test_data['stream1'],
            timestamp
        )
        self.synchronizer.add_data_stream(
            'stream2',
            self.test_data['stream2'],
            timestamp
        )
        
        # Synchronize data
        synced_data = self.synchronizer.synchronize_data()
        
        # Verify synchronization
        self.assertIsNotNone(synced_data)
        self.assertIsInstance(synced_data, SynchronizedDataPoint)
        self.assertEqual(synced_data.timestamp, timestamp)
        self.assertEqual(len(synced_data.data_streams), 2)
        self.assertIn('stream1', synced_data.data_streams)
        self.assertIn('stream2', synced_data.data_streams)
    
    def test_correlation_calculation(self):
        """Test correlation calculation."""
        # Create correlated time series
        timestamps = []
        for i in range(100):
            timestamp = (datetime.now() + timedelta(seconds=i)).isoformat()
            timestamps.append(timestamp)
            
            # Create correlated data
            value1 = np.sin(i * 0.1) + np.random.normal(0, 0.1)
            value2 = np.sin(i * 0.1 + 0.5) + np.random.normal(0, 0.1)
            
            self.synchronizer.add_data_stream(
                'stream1',
                {'value': value1, 'confidence': 0.9},
                timestamp
            )
            self.synchronizer.add_data_stream(
                'stream2',
                {'value': value2, 'confidence': 0.9},
                timestamp
            )
        
        # Synchronize and get correlations
        synced_data = self.synchronizer.synchronize_data()
        
        # Verify correlations
        self.assertIsNotNone(synced_data)
        correlations = synced_data.correlations
        self.assertIn('stream1_stream2', correlations)
        self.assertGreater(correlations['stream1_stream2'], 0.5)  # Should be highly correlated
    
    def test_data_export(self):
        """Test data export functionality."""
        timestamp = datetime.now().isoformat()
        
        # Add test data
        self.synchronizer.add_data_stream(
            'stream1',
            self.test_data['stream1'],
            timestamp
        )
        
        # Export to JSON
        json_result = self.synchronizer.export_data(
            'test_export.json',
            format='json',
            compression=True
        )
        self.assertTrue(json_result)
        
        # Export to MessagePack
        msgpack_result = self.synchronizer.export_data(
            'test_export.msgpack',
            format='msgpack',
            compression=True
        )
        self.assertTrue(msgpack_result)
    
    def test_performance_metrics(self):
        """Test performance metrics calculation."""
        timestamp = datetime.now().isoformat()
        
        # Add test data
        self.synchronizer.add_data_stream(
            'stream1',
            self.test_data['stream1'],
            timestamp
        )
        
        # Synchronize data
        synced_data = self.synchronizer.synchronize_data()
        
        # Verify performance metrics
        metrics = synced_data.performance_metrics
        self.assertIn('buffer_size', metrics)
        self.assertIn('stream_count', metrics)
        self.assertIn('average_correlation_time', metrics)
        self.assertGreater(metrics['stream_count'], 0)
    
    def test_data_preprocessing(self):
        """Test data preprocessing functionality."""
        # Create test data with outliers
        test_series = np.array([1, 2, 3, 100, 4, 5, 6, 200, 7, 8, 9])
        
        # Preprocess data
        processed_series = self.synchronizer._preprocess_data(test_series)
        
        # Verify preprocessing
        self.assertLess(np.max(processed_series), 100)  # Outliers should be removed
        self.assertAlmostEqual(np.mean(processed_series), 0, delta=0.1)  # Should be normalized
        self.assertAlmostEqual(np.std(processed_series), 1, delta=0.1)  # Should be standardized
    
    def test_confidence_calculation(self):
        """Test confidence score calculation."""
        # Test complete data
        complete_data = {
            'value': 10.5,
            'confidence': 0.9,
            'metadata': {'source': 'sensor1'}
        }
        confidence = self.synchronizer._calculate_confidence(complete_data)
        self.assertAlmostEqual(confidence, 1.0, delta=0.1)
        
        # Test incomplete data
        incomplete_data = {
            'value': 10.5,
            'confidence': None,
            'metadata': {'source': 'sensor1'}
        }
        confidence = self.synchronizer._calculate_confidence(incomplete_data)
        self.assertLess(confidence, 1.0)

if __name__ == '__main__':
    unittest.main() 