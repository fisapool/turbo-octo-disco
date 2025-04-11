# Analytics & Predictive Module

This module provides data analysis and predictive capabilities for the HR analytics platform. It includes features for data preprocessing, anomaly detection, and generating insights from multimodal data.

## Features

- Data preprocessing and cleaning
- Basic statistical metrics calculation
- Anomaly detection using Isolation Forest
- Insight generation and recommendations
- Comprehensive error handling and logging

## Installation

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```python
from src.analytics import AnalyticsModule
import pandas as pd

# Initialize the analytics module
analytics = AnalyticsModule()

# Load your data
data = pd.DataFrame({
    'timestamp': [...],
    'feature1': [...],
    'feature2': [...],
    'feature3': [...]
})

# Generate insights
features = ['feature1', 'feature2', 'feature3']
insights = analytics.generate_insights(data, features)

# Access the results
print(insights['metrics'])
print(insights['anomaly_detection'])
print(insights['recommendations'])
```

## Testing

Run the test suite:
```bash
pytest tests/
```

## Components

### AnalyticsModule

The main class that provides the following functionality:

- `preprocess_data(data)`: Preprocesses input data
- `calculate_basic_metrics(data)`: Calculates statistical metrics
- `detect_anomalies(data, features)`: Detects anomalies in the data
- `generate_insights(data, features)`: Generates comprehensive insights
- `_generate_recommendations(metrics, anomaly_results)`: Generates recommendations based on analysis

## Error Handling

The module includes comprehensive error handling and logging. All major functions are wrapped in try-except blocks and log errors appropriately.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 