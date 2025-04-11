import os
import json
import time
from datetime import datetime
from flask import Flask, render_template, jsonify, request
import threading
from webcam_integration import WebcamIntegration
from hid_system_integration import HIDSystemIntegration

# Initialize Flask app
app = Flask(__name__)

# Create necessary directories
os.makedirs('webcam_data', exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)

# Initialize tracking components
webcam_tracker = None
hid_tracker = None
tracking_active = False

def create_html_template():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Activity Tracker Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .header {
                background-color: #333;
                color: white;
                padding: 20px;
                border-radius: 5px;
                margin-bottom: 20px;
            }
            .controls {
                margin-bottom: 20px;
            }
            .button {
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin-right: 10px;
            }
            .start {
                background-color: #4CAF50;
                color: white;
            }
            .stop {
                background-color: #f44336;
                color: white;
            }
            .data-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            .data-card {
                background-color: white;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .data-card h3 {
                margin-top: 0;
                color: #333;
            }
            .chart {
                width: 100%;
                height: 200px;
                margin-top: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Activity Tracker Dashboard</h1>
            </div>
            <div class="controls">
                <button class="button start" onclick="startTracking()">Start Tracking</button>
                <button class="button stop" onclick="stopTracking()">Stop Tracking</button>
            </div>
            <div class="data-container">
                <div class="data-card">
                    <h3>Webcam Activity</h3>
                    <div id="webcamChart" class="chart"></div>
                </div>
                <div class="data-card">
                    <h3>Keyboard & Mouse Activity</h3>
                    <div id="hidChart" class="chart"></div>
                </div>
                <div class="data-card">
                    <h3>System Metrics</h3>
                    <div id="systemChart" class="chart"></div>
                </div>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
            let webcamChart, hidChart, systemChart;
            let updateInterval;

            function initCharts() {
                const chartOptions = {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                };

                webcamChart = new Chart(document.getElementById('webcamChart'), {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'Activity Level',
                            data: [],
                            borderColor: '#4CAF50',
                            tension: 0.1
                        }]
                    },
                    options: chartOptions
                });

                hidChart = new Chart(document.getElementById('hidChart'), {
                    type: 'bar',
                    data: {
                        labels: ['Keyboard', 'Mouse'],
                        datasets: [{
                            label: 'Events',
                            data: [0, 0],
                            backgroundColor: ['#2196F3', '#FFC107']
                        }]
                    },
                    options: chartOptions
                });

                systemChart = new Chart(document.getElementById('systemChart'), {
                    type: 'line',
                    data: {
                        labels: [],
                        datasets: [{
                            label: 'CPU Usage',
                            data: [],
                            borderColor: '#f44336',
                            tension: 0.1
                        }]
                    },
                    options: chartOptions
                });
            }

            function updateCharts() {
                fetch('/api/data')
                    .then(response => response.json())
                    .then(data => {
                        // Update webcam chart
                        if (data.webcam) {
                            webcamChart.data.labels.push(new Date().toLocaleTimeString());
                            webcamChart.data.datasets[0].data.push(data.webcam.activity_level);
                            if (webcamChart.data.labels.length > 10) {
                                webcamChart.data.labels.shift();
                                webcamChart.data.datasets[0].data.shift();
                            }
                            webcamChart.update();
                        }

                        // Update HID chart
                        if (data.hid) {
                            hidChart.data.datasets[0].data = [
                                data.hid.keyboard_events,
                                data.hid.mouse_events
                            ];
                            hidChart.update();
                        }

                        // Update system chart
                        if (data.system) {
                            systemChart.data.labels.push(new Date().toLocaleTimeString());
                            systemChart.data.datasets[0].data.push(data.system.cpu_usage);
                            if (systemChart.data.labels.length > 10) {
                                systemChart.data.labels.shift();
                                systemChart.data.datasets[0].data.shift();
                            }
                            systemChart.update();
                        }
                    });
            }

            function startTracking() {
                fetch('/api/start', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            updateInterval = setInterval(updateCharts, 1000);
                        }
                    });
            }

            function stopTracking() {
                fetch('/api/stop', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            clearInterval(updateInterval);
                        }
                    });
            }

            // Initialize charts when page loads
            document.addEventListener('DOMContentLoaded', initCharts);
        </script>
    </body>
    </html>
    """
    with open('templates/index.html', 'w') as f:
        f.write(html_content)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start', methods=['POST'])
def start_tracking():
    global webcam_tracker, hid_tracker, tracking_active
    
    if not tracking_active:
        try:
            webcam_tracker = WebcamIntegration()
            hid_tracker = HIDSystemIntegration()
            
            webcam_tracker.start()
            hid_tracker.start()
            
            tracking_active = True
            return jsonify({'status': 'success', 'message': 'Tracking started'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    
    return jsonify({'status': 'error', 'message': 'Tracking already active'})

@app.route('/api/stop', methods=['POST'])
def stop_tracking():
    global webcam_tracker, hid_tracker, tracking_active
    
    if tracking_active:
        try:
            webcam_tracker.stop()
            hid_tracker.stop()
            
            tracking_active = False
            return jsonify({'status': 'success', 'message': 'Tracking stopped'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    
    return jsonify({'status': 'error', 'message': 'Tracking not active'})

@app.route('/api/data')
def get_data():
    data = {
        'webcam': {
            'activity_level': 0
        },
        'hid': {
            'keyboard_events': 0,
            'mouse_events': 0
        },
        'system': {
            'cpu_usage': 0
        }
    }
    
    if tracking_active:
        try:
            # Get webcam data
            if webcam_tracker:
                data['webcam']['activity_level'] = webcam_tracker.get_activity_level()
            
            # Get HID data
            if hid_tracker:
                data['hid']['keyboard_events'] = hid_tracker.keyboard_events
                data['hid']['mouse_events'] = hid_tracker.mouse_events
                data['system']['cpu_usage'] = hid_tracker.get_system_metrics()['cpu_percent']
        except Exception as e:
            print(f"Error getting data: {str(e)}")
    
    return jsonify(data)

if __name__ == '__main__':
    create_html_template()
    app.run(host='0.0.0.0', port=5000, debug=True) 