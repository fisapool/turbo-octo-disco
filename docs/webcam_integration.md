# Webcam Integration Module Documentation

## Overview
The Webcam Integration Module provides real-time posture analysis using computer vision and machine learning. It captures webcam footage, analyzes posture using MediaPipe, and provides feedback on posture quality.

## Features
- Real-time posture analysis
- Automatic recording of poor posture
- Periodic snapshots
- Posture quality metrics:
  - Shoulder alignment
  - Back straightness
  - Head position
- Data storage and analysis

## Installation
1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure you have a working webcam connected to your system.

## Usage
```python
from webcam_integration import WebcamAnalyzer

# Initialize with default configuration
analyzer = WebcamAnalyzer()

# Or with custom configuration
config = {
    'snapshot_interval': 5,  # seconds
    'recording_duration': 30,  # seconds
    'data_dir': 'custom_data_dir',
    'posture_threshold': 0.7
}
analyzer = WebcamAnalyzer(config)

# Start monitoring
analyzer.run()
```

## Configuration Options
- `snapshot_interval`: Time between snapshots (seconds)
- `recording_duration`: Maximum duration of posture recordings (seconds)
- `data_dir`: Directory to store captured data
- `posture_threshold`: Quality threshold for triggering recordings (0-1)

## Data Storage
The module stores two types of data:
1. Snapshots: JPEG images captured at regular intervals
2. Analysis: JSON files containing posture metrics

File naming convention:
- Snapshots: `snapshot_YYYYMMDD_HHMMSS.jpg`
- Analysis: `analysis_YYYYMMDD_HHMMSS.json`

## Posture Metrics
The module calculates three main metrics:
1. Shoulder Alignment (0-1)
   - Measures horizontal alignment of shoulders
   - Higher values indicate better alignment

2. Back Straightness (0-1)
   - Measures vertical alignment of spine
   - Higher values indicate straighter posture

3. Head Position (0-1)
   - Measures head tilt
   - Higher values indicate better head position

## Troubleshooting
1. Webcam not detected:
   - Check webcam connection
   - Verify webcam permissions
   - Try different webcam index (0, 1, etc.)

2. Poor posture detection:
   - Adjust lighting conditions
   - Ensure clear view of upper body
   - Adjust `posture_threshold` if needed

## Security Considerations
- All data is stored locally
- No data is transmitted externally
- Webcam access is required only during runtime

## Development
To contribute to the module:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Testing
Run unit tests:
```bash
python -m unittest tests/test_webcam_integration.py
```

## License
This module is licensed under the MIT License. 