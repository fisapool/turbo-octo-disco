import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsModule:
    def __init__(self):
        self.scaler = StandardScaler()
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.is_fitted = False

    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess the input data for analysis.
        
        Args:
            data: DataFrame containing the input data
            
        Returns:
            Preprocessed DataFrame
        """
        try:
            # Handle missing values
            data = data.fillna(method='ffill')
            
            # Convert timestamps if present
            if 'timestamp' in data.columns:
                data['timestamp'] = pd.to_datetime(data['timestamp'])
            
            return data
        except Exception as e:
            logger.error(f"Error in preprocessing data: {str(e)}")
            raise

    def detect_anomalies(self, data: pd.DataFrame, features: List[str]) -> Dict:
        """
        Detect anomalies in the input data using Isolation Forest.
        
        Args:
            data: DataFrame containing the input data
            features: List of feature columns to use for anomaly detection
            
        Returns:
            Dictionary containing anomaly scores and predictions
        """
        try:
            if not self.is_fitted:
                # Fit the scaler and anomaly detector
                X = self.scaler.fit_transform(data[features])
                self.anomaly_detector.fit(X)
                self.is_fitted = True
            
            # Transform and predict
            X = self.scaler.transform(data[features])
            anomaly_scores = self.anomaly_detector.decision_function(X)
            predictions = self.anomaly_detector.predict(X)
            
            return {
                'anomaly_scores': anomaly_scores,
                'predictions': predictions,
                'is_anomaly': predictions == -1
            }
        except Exception as e:
            logger.error(f"Error in anomaly detection: {str(e)}")
            raise

    def calculate_basic_metrics(self, data: pd.DataFrame) -> Dict:
        """
        Calculate basic statistical metrics for the input data.
        
        Args:
            data: DataFrame containing the input data
            
        Returns:
            Dictionary containing basic statistical metrics
        """
        try:
            metrics = {
                'mean': data.mean().to_dict(),
                'std': data.std().to_dict(),
                'min': data.min().to_dict(),
                'max': data.max().to_dict(),
                'median': data.median().to_dict()
            }
            return metrics
        except Exception as e:
            logger.error(f"Error in calculating basic metrics: {str(e)}")
            raise

    def generate_insights(self, data: pd.DataFrame, features: List[str]) -> Dict:
        """
        Generate insights from the input data.
        
        Args:
            data: DataFrame containing the input data
            features: List of feature columns to analyze
            
        Returns:
            Dictionary containing insights and recommendations
        """
        try:
            # Preprocess data
            processed_data = self.preprocess_data(data)
            
            # Calculate basic metrics
            metrics = self.calculate_basic_metrics(processed_data[features])
            
            # Detect anomalies
            anomaly_results = self.detect_anomalies(processed_data, features)
            
            # Generate insights
            insights = {
                'metrics': metrics,
                'anomaly_detection': {
                    'anomaly_count': sum(anomaly_results['is_anomaly']),
                    'anomaly_percentage': (sum(anomaly_results['is_anomaly']) / len(data)) * 100
                },
                'recommendations': self._generate_recommendations(metrics, anomaly_results)
            }
            
            return insights
        except Exception as e:
            logger.error(f"Error in generating insights: {str(e)}")
            raise

    def _generate_recommendations(self, metrics: Dict, anomaly_results: Dict) -> List[str]:
        """
        Generate recommendations based on metrics and anomaly detection results.
        
        Args:
            metrics: Dictionary containing basic statistical metrics
            anomaly_results: Dictionary containing anomaly detection results
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Check for high anomaly percentage
        if anomaly_results['anomaly_percentage'] > 20:
            recommendations.append("High number of anomalies detected. Consider investigating the data quality.")
        
        # Add more specific recommendations based on metrics
        for feature, values in metrics['mean'].items():
            if values > 100:  # Example threshold
                recommendations.append(f"High average value detected for {feature}. Consider reviewing the data collection process.")
        
        return recommendations 