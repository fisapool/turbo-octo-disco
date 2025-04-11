from flask import Blueprint, request, jsonify
from datetime import datetime
import pandas as pd
import numpy as np
from typing import Dict, Any
import logging
from .advanced_analytics import AdvancedAnalytics
from .model_monitor import ModelMonitor

# Initialize analytics and monitoring
analytics = AdvancedAnalytics()
monitor = ModelMonitor()

# Create API blueprint
api = Blueprint('analytics_api', __name__, url_prefix='/api/analytics')

@api.route('/health_risk', methods=['POST'])
def predict_health_risk():
    """
    Predict personalized health risks for a user.
    
    Request body:
    {
        "user_data": {
            "posture_score": float,
            "attention_level": float,
            "activity_level": float,
            "inactivity_duration": int,
            "stress_level": float
        }
    }
    """
    try:
        data = request.get_json()
        if not data or 'user_data' not in data:
            return jsonify({'error': 'Missing user_data in request'}), 400
        
        # Make prediction
        prediction = analytics.predict_health_risk(data['user_data'])
        
        # Log prediction for monitoring
        monitor.log_metrics(
            model_type='health_risk',
            y_true=np.array([data['user_data'].get('actual_risk', 0)]),
            y_pred=np.array([1 if prediction['risk_level'] > 0.5 else 0]),
            version='1.0',
            metadata={'user_id': data.get('user_id')}
        )
        
        return jsonify(prediction)
    except Exception as e:
        logging.error(f"Error predicting health risk: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/activity_forecast', methods=['POST'])
def forecast_activity():
    """
    Forecast future activity trends.
    
    Request body:
    {
        "historical_data": [
            {
                "timestamp": "ISO datetime",
                "activity_level": float,
                "posture_score": float,
                ...
            },
            ...
        ],
        "steps_ahead": int
    }
    """
    try:
        data = request.get_json()
        if not data or 'historical_data' not in data:
            return jsonify({'error': 'Missing historical_data in request'}), 400
        
        # Convert to DataFrame
        df = pd.DataFrame(data['historical_data'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # Make forecast
        forecast = analytics.forecast_activity_trends(
            df,
            steps_ahead=data.get('steps_ahead', 7)
        )
        
        return jsonify(forecast)
    except Exception as e:
        logging.error(f"Error forecasting activity: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/adjust_thresholds', methods=['POST'])
def adjust_thresholds():
    """
    Adjust model thresholds based on user feedback.
    
    Request body:
    {
        "feedback": {
            "posture_score": {"accuracy": float, "actual": float, "predicted": float},
            "attention_level": {"accuracy": float, "actual": float, "predicted": float},
            ...
        }
    }
    """
    try:
        data = request.get_json()
        if not data or 'feedback' not in data:
            return jsonify({'error': 'Missing feedback in request'}), 400
        
        # Adjust thresholds
        analytics.adjust_thresholds(data['feedback'])
        
        return jsonify({
            'message': 'Thresholds adjusted successfully',
            'new_thresholds': analytics.thresholds
        })
    except Exception as e:
        logging.error(f"Error adjusting thresholds: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/model_performance', methods=['GET'])
def get_model_performance():
    """
    Get model performance metrics and drift analysis.
    
    Query parameters:
    - model_type: Type of model to analyze
    - window_size: Number of recent evaluations to consider (default: 5)
    - threshold: Performance drop threshold (default: 0.05)
    """
    try:
        model_type = request.args.get('model_type')
        if not model_type:
            return jsonify({'error': 'Missing model_type parameter'}), 400
        
        window_size = int(request.args.get('window_size', 5))
        threshold = float(request.args.get('threshold', 0.05))
        
        # Check performance drift
        drift_analysis = monitor.check_performance_drift(
            model_type=model_type,
            window_size=window_size,
            threshold=threshold
        )
        
        # Generate performance report
        report_path = monitor.generate_performance_report(model_type)
        
        return jsonify({
            'drift_analysis': drift_analysis,
            'report_path': report_path
        })
    except Exception as e:
        logging.error(f"Error getting model performance: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/train_time_series', methods=['POST'])
def train_time_series_model():
    """
    Train time series forecasting model.
    
    Request body:
    {
        "data": [
            {
                "timestamp": "ISO datetime",
                "target": float,
                "feature1": float,
                ...
            },
            ...
        ],
        "target_col": str,
        "sequence_length": int
    }
    """
    try:
        data = request.get_json()
        if not data or 'data' not in data:
            return jsonify({'error': 'Missing data in request'}), 400
        
        # Convert to DataFrame
        df = pd.DataFrame(data['data'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # Train model
        history = analytics.train_time_series_model(
            df,
            target_col=data.get('target_col', 'target'),
            sequence_length=data.get('sequence_length', 24)
        )
        
        # Save trained model
        analytics.save_models()
        
        return jsonify({
            'message': 'Model trained successfully',
            'training_history': history
        })
    except Exception as e:
        logging.error(f"Error training time series model: {str(e)}")
        return jsonify({'error': str(e)}), 500 