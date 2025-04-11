import os
import time
import json
import logging
import pickle
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path
import threading
import queue
from collections import defaultdict
import tensorflow as tf

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/analytics_engine.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('AnalyticsEngine')

class AnalyticsEngine:
    def __init__(self, config_path='config.json'):
        self.config = self._load_config(config_path)
        self.is_running = False
        self.data_queue = queue.Queue()
        self.analysis_results = defaultdict(list)
        
        # Initialize ML model for pattern recognition
        if self.config['analytics']['pattern_recognition']:
            self._init_ml_model()
            
        # Create output directories
        Path(os.path.join(self.config['system']['data_dir'], 'reports')).mkdir(parents=True, exist_ok=True)
        
    def _load_config(self, config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return self._get_default_config()
            
    def _get_default_config(self):
        return {
            "analytics": {
                "real_time_processing": True,
                "pattern_recognition": True,
                "machine_learning": True
            },
            "system": {
                "data_dir": "activity_data"
            }
        }
        
    def _init_ml_model(self):
        """Initialize TensorFlow Lite model for pattern recognition"""
        try:
            # Simple model for demonstration
            self.model = tf.keras.Sequential([
                tf.keras.layers.Dense(64, activation='relu', input_shape=(10,)),
                tf.keras.layers.Dense(32, activation='relu'),
                tf.keras.layers.Dense(1, activation='sigmoid')
            ])
            self.model.compile(optimizer='adam', loss='binary_crossentropy')
        except Exception as e:
            logger.error(f"Failed to initialize ML model: {e}")
            self.config['analytics']['pattern_recognition'] = False
            
    def start(self):
        """Start the analytics engine"""
        logger.info("Starting analytics engine...")
        self.is_running = True
        
        # Start processing threads
        self.processing_thread = threading.Thread(target=self._process_data)
        self.analysis_thread = threading.Thread(target=self._analyze_patterns)
        self.report_thread = threading.Thread(target=self._generate_reports)
        
        self.processing_thread.start()
        self.analysis_thread.start()
        self.report_thread.start()
        
        logger.info("Analytics engine started successfully")
        
    def stop(self):
        """Stop the analytics engine"""
        logger.info("Stopping analytics engine...")
        self.is_running = False
        
        # Wait for threads to finish
        self.processing_thread.join()
        self.analysis_thread.join()
        self.report_thread.join()
        
        # Generate final reports
        self._generate_final_report()
        
        logger.info("Analytics engine stopped")
        
    def _process_data(self):
        """Process incoming data files"""
        while self.is_running:
            try:
                # Check for new data files
                analytics_dir = os.path.join(self.config['system']['data_dir'], 'analytics')
                for filename in os.listdir(analytics_dir):
                    if filename.endswith('.pkl') and not filename.startswith('processed_'):
                        self._process_data_file(os.path.join(analytics_dir, filename))
                        
                time.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"Error in data processing: {e}")
                
    def _process_data_file(self, filepath):
        """Process a single data file"""
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                
            # Process each data point
            for item in data:
                self.data_queue.put(item)
                
            # Mark file as processed
            processed_path = os.path.join(os.path.dirname(filepath), f"processed_{os.path.basename(filepath)}")
            os.rename(filepath, processed_path)
            
        except Exception as e:
            logger.error(f"Failed to process file {filepath}: {e}")
            
    def _analyze_patterns(self):
        """Analyze patterns in the data"""
        data_buffer = []
        
        while self.is_running:
            try:
                # Get data from queue
                try:
                    data = self.data_queue.get(timeout=1)
                    data_buffer.append(data)
                except queue.Empty:
                    continue
                    
                # Analyze when buffer is large enough
                if len(data_buffer) >= 100:
                    self._analyze_batch(data_buffer)
                    data_buffer = []
                    
            except Exception as e:
                logger.error(f"Error in pattern analysis: {e}")
                
    def _analyze_batch(self, data_buffer):
        """Analyze a batch of data"""
        try:
            # Group data by type
            grouped_data = defaultdict(list)
            for item in data_buffer:
                grouped_data[item['type']].append(item)
                
            # Analyze each type
            for data_type, items in grouped_data.items():
                if data_type == 'posture':
                    self._analyze_posture_patterns(items)
                elif data_type in ['keyboard', 'mouse_move', 'mouse_click']:
                    self._analyze_input_patterns(items)
                    
        except Exception as e:
            logger.error(f"Error in batch analysis: {e}")
            
    def _analyze_posture_patterns(self, items):
        """Analyze posture patterns"""
        try:
            # Calculate posture metrics
            posture_scores = [item['data']['is_good_posture'] for item in items]
            avg_score = sum(posture_scores) / len(posture_scores)
            
            self.analysis_results['posture'].append({
                'timestamp': datetime.now().isoformat(),
                'average_score': avg_score,
                'good_posture_percentage': sum(posture_scores) / len(posture_scores) * 100
            })
            
        except Exception as e:
            logger.error(f"Error in posture analysis: {e}")
            
    def _analyze_input_patterns(self, items):
        """Analyze input patterns"""
        try:
            # Calculate activity metrics
            activity_times = [datetime.fromisoformat(item['timestamp']) for item in items]
            time_diffs = np.diff([t.timestamp() for t in activity_times])
            
            self.analysis_results['activity'].append({
                'timestamp': datetime.now().isoformat(),
                'event_count': len(items),
                'average_interval': float(np.mean(time_diffs)) if len(time_diffs) > 0 else 0,
                'activity_duration': (max(activity_times) - min(activity_times)).total_seconds()
            })
            
        except Exception as e:
            logger.error(f"Error in input analysis: {e}")
            
    def _generate_reports(self):
        """Generate periodic reports"""
        last_report = time.time()
        report_interval = 300  # 5 minutes
        
        while self.is_running:
            current_time = time.time()
            if current_time - last_report >= report_interval:
                self._generate_report()
                last_report = current_time
                
            time.sleep(10)  # Check every 10 seconds
            
    def _generate_report(self):
        """Generate a single report"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = os.path.join(
                self.config['system']['data_dir'],
                'reports',
                f'report_{timestamp}.json'
            )
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'period': '5_minutes',
                'posture_analysis': self._summarize_posture_data(),
                'activity_analysis': self._summarize_activity_data(),
                'recommendations': self._generate_recommendations()
            }
            
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=4)
                
            logger.info(f"Generated report: {report_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            
    def _summarize_posture_data(self):
        """Summarize posture analysis data"""
        if not self.analysis_results['posture']:
            return None
            
        recent_data = self.analysis_results['posture'][-10:]  # Last 10 records
        return {
            'average_score': np.mean([d['average_score'] for d in recent_data]),
            'good_posture_percentage': np.mean([d['good_posture_percentage'] for d in recent_data])
        }
        
    def _summarize_activity_data(self):
        """Summarize activity analysis data"""
        if not self.analysis_results['activity']:
            return None
            
        recent_data = self.analysis_results['activity'][-10:]  # Last 10 records
        return {
            'average_events_per_minute': np.mean([d['event_count'] for d in recent_data]) / 5,
            'average_activity_duration': np.mean([d['activity_duration'] for d in recent_data])
        }
        
    def _generate_recommendations(self):
        """Generate recommendations based on analysis"""
        recommendations = []
        
        # Posture recommendations
        posture_data = self._summarize_posture_data()
        if posture_data and posture_data['good_posture_percentage'] < 70:
            recommendations.append({
                'type': 'posture',
                'priority': 'high',
                'message': 'Consider improving your posture. Try sitting up straight and keeping your shoulders level.'
            })
            
        # Activity recommendations
        activity_data = self._summarize_activity_data()
        if activity_data and activity_data['average_events_per_minute'] > 100:
            recommendations.append({
                'type': 'break',
                'priority': 'medium',
                'message': 'You have been very active. Consider taking a short break.'
            })
            
        return recommendations
        
    def _generate_final_report(self):
        """Generate final summary report"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = os.path.join(
                self.config['system']['data_dir'],
                'reports',
                f'final_report_{timestamp}.json'
            )
            
            report = {
                'timestamp': datetime.now().isoformat(),
                'session_duration': str(timedelta(seconds=int(time.time() - self.start_time))),
                'posture_summary': self._summarize_posture_data(),
                'activity_summary': self._summarize_activity_data(),
                'final_recommendations': self._generate_recommendations()
            }
            
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=4)
                
            logger.info(f"Generated final report: {report_path}")
            
        except Exception as e:
            logger.error(f"Failed to generate final report: {e}")
            
def main():
    engine = AnalyticsEngine()
    try:
        engine.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        engine.stop()
        
if __name__ == "__main__":
    main() 