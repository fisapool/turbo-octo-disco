from flask import Flask, render_template_string, jsonify
import os
import json
import logging
from datetime import datetime
import threading
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/dashboard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('Dashboard')

# HTML template for the dashboard
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>HR Analytics Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <style>
        body { background-color: #f8f9fa; }
        .card { margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .status-indicator { width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 5px; }
        .status-active { background-color: #28a745; }
        .status-inactive { background-color: #dc3545; }
    </style>
</head>
<body>
    <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid">
            <span class="navbar-brand">HR Analytics Dashboard</span>
            <div class="d-flex">
                <span class="text-light me-3">
                    <span class="status-indicator" id="webcamStatus"></span>Webcam
                </span>
                <span class="text-light me-3">
                    <span class="status-indicator" id="keyboardStatus"></span>Keyboard
                </span>
                <span class="text-light">
                    <span class="status-indicator" id="mouseStatus"></span>Mouse
                </span>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <!-- Activity Overview -->
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5 class="card-title">Activity Overview</h5>
                    </div>
                    <div class="card-body">
                        <div id="activityChart"></div>
                    </div>
                </div>
            </div>

            <!-- Posture Analysis -->
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5 class="card-title">Posture Analysis</h5>
                    </div>
                    <div class="card-body">
                        <div id="postureChart"></div>
                    </div>
                </div>
            </div>
        </div>

        <div class="row">
            <!-- Focus Metrics -->
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5 class="card-title">Focus Metrics</h5>
                    </div>
                    <div class="card-body">
                        <div id="focusChart"></div>
                    </div>
                </div>
            </div>

            <!-- Recommendations -->
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5 class="card-title">Recommendations</h5>
                    </div>
                    <div class="card-body" id="recommendations">
                        <div class="alert alert-info">Loading recommendations...</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Initialize charts
        let activityChart = Plotly.newPlot('activityChart', [{
            y: [],
            type: 'line',
            name: 'Activity Level'
        }], {
            title: 'Activity Level Over Time',
            height: 300
        });

        let postureChart = Plotly.newPlot('postureChart', [{
            y: [],
            type: 'line',
            name: 'Posture Score'
        }], {
            title: 'Posture Score Over Time',
            height: 300
        });

        let focusChart = Plotly.newPlot('focusChart', [{
            y: [],
            type: 'bar',
            name: 'Focus Duration'
        }], {
            title: 'Focus Sessions',
            height: 300
        });

        // Update data periodically
        function updateDashboard() {
            // Update status indicators
            $.get('/status', function(data) {
                $('#webcamStatus').toggleClass('status-active', data.webcam);
                $('#keyboardStatus').toggleClass('status-active', data.keyboard);
                $('#mouseStatus').toggleClass('status-active', data.mouse);
            });

            // Update charts
            $.get('/metrics', function(data) {
                Plotly.extendTraces('activityChart', {
                    y: [[data.activity_level]]
                }, [0]);

                Plotly.extendTraces('postureChart', {
                    y: [[data.posture_score]]
                }, [0]);

                // Update focus chart
                if (data.focus_sessions) {
                    Plotly.update('focusChart', {
                        y: [data.focus_sessions]
                    });
                }
            });

            // Update recommendations
            $.get('/recommendations', function(data) {
                let html = '';
                data.forEach(function(rec) {
                    let alertClass = rec.priority === 'high' ? 'danger' : 'warning';
                    html += `<div class="alert alert-${alertClass}">${rec.message}</div>`;
                });
                $('#recommendations').html(html || '<div class="alert alert-success">No current recommendations</div>');
            });
        }

        // Update every 5 seconds
        setInterval(updateDashboard, 5000);
        updateDashboard();  // Initial update
    </script>
</body>
</html>
'''

class Dashboard:
    def __init__(self, config_path='config.json'):
        self.config = self._load_config(config_path)
        self.app = Flask(__name__)
        self.setup_routes()
        self.last_metrics = {
            'activity_level': 0,
            'posture_score': 0,
            'focus_sessions': []
        }
        self.component_status = {
            'webcam': False,
            'keyboard': False,
            'mouse': False
        }
        
        # Start status update thread
        self.is_running = True
        self.update_thread = threading.Thread(target=self._update_status)
        self.update_thread.start()
        
    def _load_config(self, config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return self._get_default_config()
            
    def _get_default_config(self):
        return {
            "ui": {
                "dashboard": {
                    "port": 5000,
                    "refresh_rate": 5
                }
            },
            "system": {
                "data_dir": "activity_data"
            }
        }
        
    def setup_routes(self):
        @self.app.route('/')
        def index():
            return render_template_string(DASHBOARD_TEMPLATE)
            
        @self.app.route('/status')
        def get_status():
            return jsonify(self.component_status)
            
        @self.app.route('/metrics')
        def get_metrics():
            self._update_metrics()
            return jsonify(self.last_metrics)
            
        @self.app.route('/recommendations')
        def get_recommendations():
            return jsonify(self._get_recommendations())
            
    def _update_status(self):
        """Update component status periodically"""
        while self.is_running:
            try:
                # Check for recent activity in data files
                analytics_dir = os.path.join(self.config['system']['data_dir'], 'analytics')
                recent_files = [f for f in os.listdir(analytics_dir) if f.endswith('.pkl')]
                
                if recent_files:
                    latest_file = max(recent_files, key=lambda x: os.path.getmtime(os.path.join(analytics_dir, x)))
                    latest_time = os.path.getmtime(os.path.join(analytics_dir, latest_file))
                    
                    # Consider components active if data is less than 10 seconds old
                    is_active = (time.time() - latest_time) < 10
                    self.component_status = {
                        'webcam': is_active,
                        'keyboard': is_active,
                        'mouse': is_active
                    }
                    
            except Exception as e:
                logger.error(f"Error updating status: {e}")
                
            time.sleep(5)
            
    def _update_metrics(self):
        """Update metrics from latest data"""
        try:
            reports_dir = os.path.join(self.config['system']['data_dir'], 'reports')
            recent_reports = sorted(
                [f for f in os.listdir(reports_dir) if f.endswith('.json')],
                key=lambda x: os.path.getmtime(os.path.join(reports_dir, x)),
                reverse=True
            )
            
            if recent_reports:
                latest_report = recent_reports[0]
                with open(os.path.join(reports_dir, latest_report), 'r') as f:
                    report_data = json.load(f)
                    
                # Update metrics from report
                if 'activity_analysis' in report_data:
                    self.last_metrics['activity_level'] = report_data['activity_analysis'].get('average_events_per_minute', 0)
                    
                if 'posture_analysis' in report_data:
                    self.last_metrics['posture_score'] = report_data['posture_analysis'].get('good_posture_percentage', 0)
                    
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
            
    def _get_recommendations(self):
        """Get latest recommendations"""
        try:
            reports_dir = os.path.join(self.config['system']['data_dir'], 'reports')
            recent_reports = sorted(
                [f for f in os.listdir(reports_dir) if f.endswith('.json')],
                key=lambda x: os.path.getmtime(os.path.join(reports_dir, x)),
                reverse=True
            )
            
            if recent_reports:
                latest_report = recent_reports[0]
                with open(os.path.join(reports_dir, latest_report), 'r') as f:
                    report_data = json.load(f)
                    return report_data.get('recommendations', [])
                    
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            
        return []
        
    def start(self):
        """Start the dashboard"""
        logger.info("Starting dashboard...")
        self.app.run(
            host='0.0.0.0',
            port=self.config['ui']['dashboard']['port'],
            debug=False
        )
        
    def stop(self):
        """Stop the dashboard"""
        self.is_running = False
        if self.update_thread:
            self.update_thread.join()
            
def main():
    dashboard = Dashboard()
    try:
        dashboard.start()
    except KeyboardInterrupt:
        dashboard.stop()
        
if __name__ == "__main__":
    main() 