import pytest
import pandas as pd
import numpy as np
from src.analytics import AnalyticsModule

@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    data = {
        'timestamp': pd.date_range(start='2023-01-01', periods=100, freq='H'),
        'feature1': np.random.normal(0, 1, 100),
        'feature2': np.random.normal(10, 2, 100),
        'feature3': np.random.normal(5, 1, 100)
    }
    return pd.DataFrame(data)

@pytest.fixture
def analytics_module():
    """Create an instance of AnalyticsModule."""
    return AnalyticsModule()

def test_preprocess_data(analytics_module, sample_data):
    """Test data preprocessing."""
    processed_data = analytics_module.preprocess_data(sample_data)
    assert isinstance(processed_data, pd.DataFrame)
    assert not processed_data.isnull().any().any()
    assert isinstance(processed_data['timestamp'].iloc[0], pd.Timestamp)

def test_calculate_basic_metrics(analytics_module, sample_data):
    """Test basic metrics calculation."""
    features = ['feature1', 'feature2', 'feature3']
    metrics = analytics_module.calculate_basic_metrics(sample_data[features])
    
    assert 'mean' in metrics
    assert 'std' in metrics
    assert 'min' in metrics
    assert 'max' in metrics
    assert 'median' in metrics
    
    for metric in metrics.values():
        assert all(feature in metric for feature in features)

def test_detect_anomalies(analytics_module, sample_data):
    """Test anomaly detection."""
    features = ['feature1', 'feature2', 'feature3']
    anomaly_results = analytics_module.detect_anomalies(sample_data, features)
    
    assert 'anomaly_scores' in anomaly_results
    assert 'predictions' in anomaly_results
    assert 'is_anomaly' in anomaly_results
    assert len(anomaly_results['anomaly_scores']) == len(sample_data)
    assert len(anomaly_results['predictions']) == len(sample_data)
    assert len(anomaly_results['is_anomaly']) == len(sample_data)

def test_generate_insights(analytics_module, sample_data):
    """Test insights generation."""
    features = ['feature1', 'feature2', 'feature3']
    insights = analytics_module.generate_insights(sample_data, features)
    
    assert 'metrics' in insights
    assert 'anomaly_detection' in insights
    assert 'recommendations' in insights
    assert 'anomaly_count' in insights['anomaly_detection']
    assert 'anomaly_percentage' in insights['anomaly_detection']
    assert isinstance(insights['recommendations'], list)

def test_error_handling(analytics_module):
    """Test error handling with invalid input."""
    with pytest.raises(Exception):
        analytics_module.preprocess_data(pd.DataFrame())
    
    with pytest.raises(Exception):
        analytics_module.calculate_basic_metrics(pd.DataFrame())
    
    with pytest.raises(Exception):
        analytics_module.detect_anomalies(pd.DataFrame(), [])
    
    with pytest.raises(Exception):
        analytics_module.generate_insights(pd.DataFrame(), []) 