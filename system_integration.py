import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import threading
import logging
from pathlib import Path
import time
from prometheus_client import Counter, Histogram, Gauge
from dataclasses import dataclass, asdict

from data_synchronizer import DataSynchronizer
from predictive_analytics import PredictiveAnalytics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
PROCESSED_STREAMS = Counter('processed_data_streams_total', 'Total number of processed data streams')
PROCESSING_DURATION = Histogram('data_processing_duration_seconds', 'Time spent processing data streams')
ALERT_COUNT = Counter('alerts_generated_total', 'Total number of alerts generated')
REPORT_COUNT = Counter('reports_generated_total', 'Total number of reports generated')
STORAGE_USAGE = Gauge('storage_usage_bytes', 'Total storage usage in bytes')

class SystemIntegration:
    def __init__(self, storage_path: str = "integrated_data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Initialize components
        self.data_synchronizer = DataSynchronizer()
        self.predictive_analytics = PredictiveAnalytics()
        
        # Initialize data storage
        self._initialize_storage()
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Performance monitoring
        self.last_cleanup_time = time.time()
        self.cleanup_interval = 3600  # 1 hour
    
    def _initialize_storage(self):
        """Initialize the data storage structure."""
        try:
            self.storage_path.mkdir(exist_ok=True)
            (self.storage_path / "synced_data").mkdir(exist_ok=True)
            (self.storage_path / "alerts").mkdir(exist_ok=True)
            (self.storage_path / "reports").mkdir(exist_ok=True)
            
            # Set initial storage usage
            STORAGE_USAGE.set(self._calculate_storage_usage())
        except Exception as e:
            logger.error(f"Error initializing storage: {str(e)}")
            raise
    
    def _calculate_storage_usage(self) -> int:
        """Calculate total storage usage in bytes."""
        try:
            total_size = 0
            for path in self.storage_path.rglob('*'):
                if path.is_file():
                    total_size += path.stat().st_size
            return total_size
        except Exception as e:
            logger.error(f"Error calculating storage usage: {str(e)}")
            return 0
    
    def process_data_stream(self, stream_name: str, data: Dict[str, Any], timestamp: str):
        """Process a new data stream through the system."""
        start_time = time.time()
        try:
            PROCESSED_STREAMS.inc()
            
            # Add data to synchronizer
            if not self.data_synchronizer.add_data_stream(stream_name, data, timestamp):
                logger.error(f"Failed to add data to stream: {stream_name}")
                return False
            
            # Synchronize data
            synced_data = self.data_synchronizer.synchronize_data()
            if synced_data:
                # Save synchronized data
                if not self._save_synced_data(synced_data):
                    logger.error("Failed to save synchronized data")
                    return False
                
                # Analyze data for alerts
                self._analyze_data(synced_data)
            
            # Periodic cleanup
            current_time = time.time()
            if current_time - self.last_cleanup_time > self.cleanup_interval:
                self._cleanup_old_data()
                self.last_cleanup_time = current_time
                STORAGE_USAGE.set(self._calculate_storage_usage())
            
            return True
        except Exception as e:
            logger.error(f"Error processing data stream: {str(e)}")
            return False
        finally:
            duration = time.time() - start_time
            PROCESSING_DURATION.observe(duration)
    
    def _cleanup_old_data(self):
        """Clean up old data based on retention policy."""
        try:
            retention_days = 30  # Keep data for 30 days
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            for data_type in ["synced_data", "alerts", "reports"]:
                data_dir = self.storage_path / data_type
                if not data_dir.exists():
                    continue
                
                for date_dir in data_dir.iterdir():
                    if not date_dir.is_dir():
                        continue
                    
                    try:
                        dir_date = datetime.strptime(date_dir.name, "%Y-%m-%d")
                        if dir_date < cutoff_date:
                            # Remove old directory
                            for file in date_dir.glob('*'):
                                file.unlink()
                            date_dir.rmdir()
                            logger.info(f"Cleaned up old data from {date_dir}")
                    except ValueError:
                        continue
        except Exception as e:
            logger.error(f"Error cleaning up old data: {str(e)}")
    
    def _save_synced_data(self, synced_data: Any):
        """Save synchronized data to storage."""
        try:
            timestamp = datetime.fromisoformat(synced_data.timestamp)
            date_str = timestamp.strftime("%Y-%m-%d")
            
            # Create daily directory
            daily_dir = self.storage_path / "synced_data" / date_str
            daily_dir.mkdir(exist_ok=True)
            
            # Save data
            filename = f"synced_{timestamp.strftime('%H%M%S')}.json"
            filepath = daily_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(asdict(synced_data), f, indent=2)
            
            logger.info(f"Saved synchronized data to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving synchronized data: {str(e)}")
            return False
    
    def _analyze_data(self, synced_data: Any):
        """Analyze synchronized data for alerts."""
        try:
            # Analyze ergonomics
            ergonomic_alert = self.predictive_analytics.analyze_ergonomics(
                synced_data.data_streams
            )
            
            # Analyze stress
            stress_alert = self.predictive_analytics.analyze_stress(
                synced_data.data_streams
            )
            
            # Check thresholds
            threshold_alerts = self.predictive_analytics.check_thresholds(
                synced_data.data_streams
            )
            
            # Save alerts if any
            alerts = [a for a in [ergonomic_alert, stress_alert] if a is not None]
            alerts.extend(threshold_alerts)
            
            if alerts:
                ALERT_COUNT.inc(len(alerts))
                self._save_alerts(alerts)
        except Exception as e:
            logger.error(f"Error analyzing data: {str(e)}")
    
    def _save_alerts(self, alerts: List[Any]):
        """Save alerts to storage."""
        try:
            timestamp = datetime.now()
            date_str = timestamp.strftime("%Y-%m-%d")
            
            # Create daily directory
            daily_dir = self.storage_path / "alerts" / date_str
            daily_dir.mkdir(exist_ok=True)
            
            # Save alerts
            filename = f"alerts_{timestamp.strftime('%H%M%S')}.json"
            filepath = daily_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump([asdict(alert) for alert in alerts], f, indent=2)
            
            logger.info(f"Saved alerts to {filepath}")
        except Exception as e:
            logger.error(f"Error saving alerts: {str(e)}")
    
    def generate_report(self, start_time: str, end_time: str) -> Dict[str, Any]:
        """Generate a report for the specified time period."""
        start_time = time.time()
        try:
            REPORT_COUNT.inc()
            
            # Get alerts for the period
            alerts = self.predictive_analytics.get_alert_history(
                start_time=start_time,
                end_time=end_time
            )
            
            # Calculate statistics
            alert_counts = {}
            for alert in alerts:
                alert_counts[alert.type] = alert_counts.get(alert.type, 0) + 1
            
            # Generate report
            report = {
                'period': {
                    'start': start_time,
                    'end': end_time
                },
                'alert_summary': alert_counts,
                'total_alerts': len(alerts),
                'alerts': [asdict(alert) for alert in alerts],
                'performance_metrics': {
                    'processing_time_ms': (time.time() - start_time) * 1000,
                    'storage_usage_bytes': self._calculate_storage_usage()
                }
            }
            
            # Save report
            self._save_report(report)
            
            return report
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return {}
    
    def _save_report(self, report: Dict[str, Any]):
        """Save report to storage."""
        try:
            timestamp = datetime.now()
            date_str = timestamp.strftime("%Y-%m-%d")
            
            # Create daily directory
            daily_dir = self.storage_path / "reports" / date_str
            daily_dir.mkdir(exist_ok=True)
            
            # Save report
            filename = f"report_{timestamp.strftime('%H%M%S')}.json"
            filepath = daily_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Saved report to {filepath}")
        except Exception as e:
            logger.error(f"Error saving report: {str(e)}")

if __name__ == "__main__":
    # Example usage
    system = SystemIntegration()
    
    # Example data streams
    system.process_data_stream(
        "activity",
        {
            "keyboard_events": 10,
            "mouse_clicks": 5,
            "inactivity_duration": 300
        },
        datetime.now().isoformat()
    )
    
    system.process_data_stream(
        "webcam",
        {
            "posture_score": 0.8,
            "attention_level": 0.9
        },
        datetime.now().isoformat()
    )
    
    # Generate report
    start_time = (datetime.now() - timedelta(hours=1)).isoformat()
    end_time = datetime.now().isoformat()
    report = system.generate_report(start_time, end_time)
    
    print(json.dumps(report, indent=2)) 