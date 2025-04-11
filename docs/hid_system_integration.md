# HID & System Integration Module Documentation

## Overview
The HID & System Integration Module provides real-time monitoring of human interface devices (HID) and system metrics. It collects data about keyboard and mouse activity, active windows, and system performance metrics.

## Features
- Real-time HID monitoring:
  - Keyboard activity tracking
  - Mouse movement and click tracking
  - Active window detection
- System metrics collection:
  - CPU usage
  - Memory usage
  - Disk usage
  - Process information
- Threaded data collection
- Configurable polling intervals
- Automatic data persistence
- Cross-platform support (Windows, Linux, macOS)

## Installation
1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Additional platform-specific requirements:
   - Windows: No additional requirements
   - Linux: Install xdotool (`sudo apt-get install xdotool`)
   - macOS: No additional requirements

## Usage
```python
from hid_system_integration import HIDSystemMonitor

# Initialize with default configuration
monitor = HIDSystemMonitor()

# Or with custom configuration
config = {
    'poll_interval': 1.0,  # seconds
    'data_dir': 'custom_data_dir',
    'max_queue_size': 1000
}
monitor = HIDSystemMonitor(config)

# Start monitoring
monitor.start_monitoring()

# Get current metrics
current_metrics = monitor.get_current_metrics()

# Stop monitoring
monitor.stop_monitoring()
```

## Configuration Options
- `poll_interval`: Time between metric collections (seconds)
- `data_dir`: Directory to store collected data
- `max_queue_size`: Maximum size of the data queue before auto-saving

## Data Storage
The module stores data in JSON format with the following structure:
```json
{
    "system": {
        "timestamp": "2024-04-10T12:00:00",
        "cpu_percent": 45.2,
        "memory_percent": 65.8,
        "disk_percent": 72.1,
        "process_count": 120,
        "system_info": {
            "platform": "Windows",
            "platform_version": "10.0.19045",
            "processor": "Intel64 Family 6",
            "python_version": "3.9.7"
        }
    },
    "hid": {
        "timestamp": "2024-04-10T12:00:00",
        "keyboard_events": {
            "key_presses": 120,
            "key_releases": 120,
            "typing_speed": 60
        },
        "mouse_events": {
            "clicks": 45,
            "movement": 1000,
            "scroll_events": 15
        },
        "active_window": "Visual Studio Code"
    }
}
```

## Metrics Collected

### System Metrics
1. CPU Usage
   - Overall CPU utilization percentage
   - Updated every polling interval

2. Memory Usage
   - Total memory utilization percentage
   - Virtual memory statistics

3. Disk Usage
   - Disk space utilization percentage
   - Monitored for the system drive

4. Process Information
   - Number of running processes
   - System information

### HID Metrics
1. Keyboard Activity
   - Key press count
   - Key release count
   - Typing speed estimation

2. Mouse Activity
   - Click count
   - Movement distance
   - Scroll event count

3. Window Information
   - Currently active window title
   - Application focus tracking

## Data Analysis
The collected data can be used for:
1. Productivity analysis
2. Ergonomic assessment
3. System performance monitoring
4. User behavior analysis

## Security Considerations
- All data is stored locally
- No keylogging of actual keystrokes
- Only aggregate metrics are collected
- No sensitive window content is recorded

## Error Handling
The module includes robust error handling for:
- Device access issues
- System permission problems
- Storage capacity limitations
- Cross-platform compatibility

## Development
To contribute to the module:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Testing
Run unit tests:
```bash
python -m unittest tests/test_hid_system_integration.py
```

## Troubleshooting
1. Permission Issues:
   - Ensure appropriate system permissions
   - Run with elevated privileges if needed

2. Data Collection Issues:
   - Check device connectivity
   - Verify system access rights
   - Monitor storage capacity

3. Platform-Specific Issues:
   - Windows: Verify pywin32 installation
   - Linux: Check xdotool availability
   - macOS: Ensure accessibility permissions

## License
This module is licensed under the MIT License. 