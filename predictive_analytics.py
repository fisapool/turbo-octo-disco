import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import logging
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Alert:
    type: str
    severity: str
    message: str
    timestamp: str
    metadata: Dict[str, Any]

class PredictiveAnalytics:
    def __init__(self):
        self.ergonomic_model = IsolationForest(contamination=0.1)
        self.stress_model = IsolationForest(contamination=0.1)
        self.scaler = StandardScaler()
        self.alert_history: List[Alert] = []
        
        # Thresholds for different metrics
        self.thresholds = {
            'posture_score': 0.6,
            'attention_level': 0.5,
            'activity_level': 0.3,
            'inactivity_duration': 3600,  # 1 hour in seconds
        }
        
        # Initialize models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize the machine learning models with some baseline data."""
        try:
            # Sample baseline data for initialization
            baseline_data = np.array([
                [0.8, 0.9, 0.7],  # Good posture, high attention, moderate activity
                [0.7, 0.8, 0.6],
                [0.6, 0.7, 0.5],
            ])
            
            # Fit the scaler and models
            scaled_data = self.scaler.fit_transform(baseline_data)
            self.ergonomic_model.fit(scaled_data)
            self.stress_model.fit(scaled_data)
            
            logger.info("Models initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing models: {str(e)}")
    
    def analyze_ergonomics(self, data: Dict[str, Any]) -> Optional[Alert]:
        """Analyze ergonomic data and generate alerts if needed."""
        try:
            # Extract relevant features
            features = np.array([
                data.get('posture_score', 0),
                data.get('attention_level', 0),
                data.get('activity_level', 0)
            ]).reshape(1, -1)
            
            # Scale features
            scaled_features = self.scaler.transform(features)
            
            # Predict anomaly score
            anomaly_score = self.ergonomic_model.score_samples(scaled_features)[0]
            
            # Generate alert if anomaly score is below threshold
            if anomaly_score < -0.5:  # Adjust threshold as needed
                alert = Alert(
                    type="ergonomic",
                    severity="warning",
                    message="Poor ergonomic conditions detected",
                    timestamp=datetime.now().isoformat(),
                    metadata={
                        'anomaly_score': float(anomaly_score),
                        'features': features.tolist()[0]
                    }
                )
                self.alert_history.append(alert)
                return alert
            
            return None
        except Exception as e:
            logger.error(f"Error analyzing ergonomics: {str(e)}")
            return None
    
    def analyze_stress(self, data: Dict[str, Any]) -> Optional[Alert]:
        """Analyze stress indicators and generate alerts if needed."""
        try:
            # Extract relevant features
            features = np.array([
                data.get('keyboard_events', 0),
                data.get('mouse_clicks', 0),
                data.get('inactivity_duration', 0)
            ]).reshape(1, -1)
            
            # Scale features
            scaled_features = self.scaler.transform(features)
            
            # Predict anomaly score
            anomaly_score = self.stress_model.score_samples(scaled_features)[0]
            
            # Generate alert if anomaly score is below threshold
            if anomaly_score < -0.5:  # Adjust threshold as needed
                alert = Alert(
                    type="stress",
                    severity="warning",
                    message="Potential stress indicators detected",
                    timestamp=datetime.now().isoformat(),
                    metadata={
                        'anomaly_score': float(anomaly_score),
                        'features': features.tolist()[0]
                    }
                )
                self.alert_history.append(alert)
                return alert
            
            return None
        except Exception as e:
            logger.error(f"Error analyzing stress: {str(e)}")
            return None
    
    def check_thresholds(self, data: Dict[str, Any]) -> List[Alert]:
        """Check if any metrics exceed predefined thresholds."""
        alerts = []
        
        try:
            # Check posture score
            if data.get('posture_score', 1) < self.thresholds['posture_score']:
                alerts.append(Alert(
                    type="posture",
                    severity="warning",
                    message="Poor posture detected",
                    timestamp=datetime.now().isoformat(),
                    metadata={'current_score': data.get('posture_score')}
                ))
            
            # Check attention level
            if data.get('attention_level', 1) < self.thresholds['attention_level']:
                alerts.append(Alert(
                    type="attention",
                    severity="info",
                    message="Low attention level detected",
                    timestamp=datetime.now().isoformat(),
                    metadata={'current_level': data.get('attention_level')}
                ))
            
            # Check inactivity duration
            if data.get('inactivity_duration', 0) > self.thresholds['inactivity_duration']:
                alerts.append(Alert(
                    type="inactivity",
                    severity="warning",
                    message="Prolonged inactivity detected",
                    timestamp=datetime.now().isoformat(),
                    metadata={'duration_seconds': data.get('inactivity_duration')}
                ))
            
            # Add alerts to history
            self.alert_history.extend(alerts)
            
            return alerts
        except Exception as e:
            logger.error(f"Error checking thresholds: {str(e)}")
            return []
    
    def get_alert_history(self, 
                         alert_type: Optional[str] = None,
                         start_time: Optional[str] = None,
                         end_time: Optional[str] = None) -> List[Alert]:
        """Retrieve alert history with optional filtering."""
        filtered_alerts = self.alert_history.copy()
        
        if alert_type:
            filtered_alerts = [a for a in filtered_alerts if a.type == alert_type]
        
        if start_time:
            start_dt = datetime.fromisoformat(start_time)
            filtered_alerts = [a for a in filtered_alerts 
                             if datetime.fromisoformat(a.timestamp) >= start_dt]
        
        if end_time:
            end_dt = datetime.fromisoformat(end_time)
            filtered_alerts = [a for a in filtered_alerts 
                             if datetime.fromisoformat(a.timestamp) <= end_dt]
        
        return filtered_alerts
    
    def export_alerts(self, filename: str):
        """Export alert history to a JSON file."""
        try:
            with open(filename, 'w') as f:
                json.dump([asdict(alert) for alert in self.alert_history], f, indent=2)
            logger.info(f"Exported alerts to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error exporting alerts: {str(e)}")
            return False

if __name__ == "__main__":
    # Example usage
    analytics = PredictiveAnalytics()
    
    # Example data
    sample_data = {
        'posture_score': 0.5,
        'attention_level': 0.4,
        'activity_level': 0.3,
        'keyboard_events': 100,
        'mouse_clicks': 50,
        'inactivity_duration': 4000
    }
    
    # Analyze data
    ergonomic_alert = analytics.analyze_ergonomics(sample_data)
    stress_alert = analytics.analyze_stress(sample_data)
    threshold_alerts = analytics.check_thresholds(sample_data)
    
    # Export alerts
    analytics.export_alerts("alerts.json") 