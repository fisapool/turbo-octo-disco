import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from src.advanced_analytics import AdvancedAnalytics
from src.model_monitor import ModelMonitor

@pytest.fixture
def analytics():
    return AdvancedAnalytics()

@pytest.fixture
def monitor():
    return ModelMonitor()

@pytest.fixture
def sample_time_series_data():
    # Generate sample time series data
    dates = pd.date_range(start='2023-01-01', periods=100, freq='H')
    data = pd.DataFrame({
        'timestamp': dates,
        'activity_level': np.random.normal(0.5, 0.1, 100),
        'posture_score': np.random.normal(0.6, 0.1, 100),
        'attention_level': np.random.normal(0.7, 0.1, 100)
    })
    data.set_index('timestamp', inplace=True)
    return data

@pytest.fixture
def sample_user_data():
    return {
        'posture_score': 0.7,
        'attention_level': 0.8,
        'activity_level': 0.6,
        'inactivity_duration': 1800,
        'stress_level': 0.3
    }

@pytest.fixture
def sample_activity_data():
    # Generate sample activity data
    timestamps = pd.date_range(start='2024-01-01 09:00:00', periods=100, freq='1min')
    return [
        {
            'timestamp': ts.isoformat(),
            'activity_level': 0.8 if i % 10 < 7 else 0.2,  # High activity most of the time
            'attention_level': 0.9 if i % 10 < 8 else 0.3,  # High attention most of the time
            'stress_level': 0.2 if i % 10 < 6 else 0.7,     # Low stress most of the time
        }
        for i, ts in enumerate(timestamps)
    ]

def test_health_risk_prediction(analytics):
    """Test health risk prediction with various input scenarios."""
    # Test with good metrics
    good_metrics = {
        'posture_score': 0.9,
        'attention_level': 0.8,
        'activity_level': 0.7,
        'inactivity_duration': 300,
        'stress_level': 0.2
    }
    prediction = analytics.predict_health_risk(good_metrics)
    assert 'risk_level' in prediction
    assert 'confidence' in prediction
    assert 'timestamp' in prediction
    assert 0 <= prediction['risk_level'] <= 1
    assert 0 <= prediction['confidence'] <= 1
    
    # Test with poor metrics
    poor_metrics = {
        'posture_score': 0.3,
        'attention_level': 0.2,
        'activity_level': 0.1,
        'inactivity_duration': 3600,
        'stress_level': 0.8
    }
    prediction = analytics.predict_health_risk(poor_metrics)
    assert prediction['risk_level'] > 0.5  # Should indicate higher risk

def test_break_opportunities(analytics, sample_activity_data):
    """Test break opportunity identification."""
    opportunities = analytics.identify_break_opportunities(sample_activity_data)
    
    assert isinstance(opportunities, list)
    if opportunities:  # If any opportunities were found
        opportunity = opportunities[0]
        assert 'start_time' in opportunity
        assert 'end_time' in opportunity
        assert 'duration_minutes' in opportunity
        assert 'quality_score' in opportunity
        assert 'confidence' in opportunity
        
        # Verify quality score calculation
        assert 0 <= opportunity['quality_score'] <= 1
        assert 0 <= opportunity['confidence'] <= 1

def test_focus_time_analysis(analytics, sample_activity_data):
    """Test focus time analysis."""
    analysis = analytics.analyze_focus_time(sample_activity_data)
    
    assert isinstance(analysis, dict)
    assert 'total_time_minutes' in analysis
    assert 'focus_time_minutes' in analysis
    assert 'focus_percentage' in analysis
    assert 'focus_periods' in analysis
    assert 'avg_focus_score' in analysis
    assert 'timestamp' in analysis
    
    # Verify focus percentage calculation
    assert 0 <= analysis['focus_percentage'] <= 100
    assert analysis['focus_time_minutes'] <= analysis['total_time_minutes']
    
    # Verify focus periods
    if analysis['focus_periods']:
        period = analysis['focus_periods'][0]
        assert 'start_time' in period
        assert 'end_time' in period
        assert 'duration_minutes' in period
        assert 'focus_score' in period
        assert period['duration_minutes'] >= 5  # Minimum duration

def test_time_series_model_training(analytics):
    """Test LSTM model training functionality."""
    # Create sample time series data
    timestamps = pd.date_range(start='2024-01-01', periods=100, freq='H')
    data = pd.DataFrame({
        'timestamp': timestamps,
        'activity_level': [0.8 if i % 24 < 12 else 0.2 for i in range(100)],
        'attention_level': [0.9 if i % 24 < 14 else 0.3 for i in range(100)],
        'stress_level': [0.2 if i % 24 < 16 else 0.7 for i in range(100)],
        'posture_score': [0.9 if i % 24 < 18 else 0.4 for i in range(100)],
        'target': [1 if i % 24 < 12 else 0 for i in range(100)]  # Binary target
    })
    
    # Train model
    history = analytics.train_time_series_model(data, 'target')
    
    assert isinstance(history, dict)
    assert 'loss' in history
    assert 'accuracy' in history
    assert 'val_loss' in history
    assert 'val_accuracy' in history

def test_time_series_forecasting(analytics, sample_time_series_data):
    """Test time series forecasting."""
    # Train model
    history = analytics.train_time_series_model(
        sample_time_series_data,
        target_col='activity_level',
        sequence_length=24
    )
    
    assert isinstance(history, dict)
    assert 'loss' in history
    assert 'mae' in history
    
    # Make forecast
    forecast = analytics.forecast_activity_trends(
        sample_time_series_data,
        steps_ahead=7
    )
    
    assert 'forecast' in forecast
    assert 'timestamps' in forecast
    assert len(forecast['forecast']) == 7
    assert len(forecast['timestamps']) == 7

def test_threshold_adjustment(analytics):
    """Test adaptive threshold adjustment."""
    initial_thresholds = analytics.thresholds.copy()
    
    # Provide feedback
    feedback = {
        'posture_score': {'accuracy': 0.8, 'actual': 0.7, 'predicted': 0.6},
        'attention_level': {'accuracy': 0.9, 'actual': 0.8, 'predicted': 0.7}
    }
    
    analytics.adjust_thresholds(feedback)
    
    # Check if thresholds were adjusted
    assert analytics.thresholds != initial_thresholds
    for metric in feedback:
        assert metric in analytics.thresholds

def test_model_performance_monitoring(monitor):
    """Test model performance monitoring."""
    # Log some metrics
    y_true = np.array([1, 0, 1, 0, 1])
    y_pred = np.array([1, 0, 1, 1, 1])
    
    monitor.log_metrics(
        model_type='test_model',
        y_true=y_true,
        y_pred=y_pred,
        version='1.0'
    )
    
    # Check performance drift
    drift_analysis = monitor.check_performance_drift(
        model_type='test_model',
        window_size=3
    )
    
    assert 'status' in drift_analysis
    assert 'recent_metrics' in drift_analysis
    assert 'baseline_metrics' in drift_analysis
    
    # Generate performance report
    report_path = monitor.generate_performance_report('test_model')
    assert report_path is not None

def test_model_saving_and_loading(analytics):
    """Test model saving and loading."""
    # Save models
    analytics.save_models()
    
    # Create new instance and load models
    new_analytics = AdvancedAnalytics()
    
    assert new_analytics.rf_classifier is not None
    assert new_analytics.rf_regressor is not None
    assert new_analytics.lstm_model is None  # LSTM model not trained yet

def test_error_handling(analytics, monitor):
    """Test error handling in various scenarios."""
    # Test with empty activity data
    assert analytics.identify_break_opportunities([]) == []
    assert analytics.analyze_focus_time([]) == {}
    
    # Test with invalid input data
    with pytest.raises(Exception):
        analytics.predict_health_risk({})
    
    # Test with insufficient data for time series training
    with pytest.raises(Exception):
        analytics.train_time_series_model(
            pd.DataFrame({'timestamp': [datetime.now()]}),
            'target'
        )
    
    # Test with invalid feedback for threshold adjustment
    with pytest.raises(Exception):
        analytics.adjust_thresholds({'invalid_metric': {}})
    
    # Test with non-existent model type for performance monitoring
    with pytest.raises(Exception):
        monitor.generate_performance_report('non_existent_model') 