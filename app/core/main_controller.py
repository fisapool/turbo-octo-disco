#!/usr/bin/env python3
"""
Unified Controller for Productivity Analytics System

Features:
- Manages all tracking components (window, activity, screenshots, recordings)
- Provides web-based dashboard interface
- Handles configuration and license management
"""

import json
import os
import threading
import time
from flask import Flask, render_template, jsonify
from licensing_module import LicenseManager
import subprocess
from typing import Dict, Any
from datetime import datetime

from .tracking.activity_tracker import ActivityTracker
from .recording.webcam import WebcamRecorder
from .analysis.advanced_analytics import AdvancedAnalytics

# Load configuration
with open('config.json') as f:
    config = json.load(f)

# Initialize Flask app for dashboard
app = Flask(__name__)

# Track running processes
processes = {
    'window_tracker': None,
    'activity_tracker': None,
    'screenshot': None,
    'recording': None
}

# Status tracking
status = {
    'running': False,
    'components': {
        'window_tracker': False,
        'activity_tracker': False,
        'screenshot': False,
        'recording': False
    }
}

def start_component(component):
    """Start a tracking component"""
    if component == 'window_tracker':
        processes[component] = subprocess.Popen(['python', 'active_window_tracker.py'])
    elif component == 'activity_tracker':
        processes[component] = subprocess.Popen(['python', 'activity_tracker.py'])
    elif component == 'screenshot':
        processes[component] = subprocess.Popen(['python', 'automated_screenshot.py'])
    elif component == 'recording':
        processes[component] = subprocess.Popen(['python', 'scheduled_recording_script.py'])
    
    status['components'][component] = True
    status['running'] = any(status['components'].values())

def stop_component(component):
    """Stop a tracking component"""
    if processes[component]:
        processes[component].terminate()
        processes[component] = None
    
    status['components'][component] = False
    status['running'] = any(status['components'].values())

@app.route('/')
def dashboard():
    """Render main dashboard"""
    return render_template('dashboard.html', status=status, config=config)

@app.route('/start', methods=['POST'])
def start_tracking():
    """Start all tracking components"""
    for component in processes:
        start_component(component)
    return jsonify({'status': 'success'})

@app.route('/stop', methods=['POST'])
def stop_tracking():
    """Stop all tracking components"""
    for component in processes:
        stop_component(component)
    return jsonify({'status': 'success'})

@app.route('/status')
def get_status():
    """Get current system status"""
    return jsonify(status)

def run_dashboard():
    """Run the Flask dashboard"""
    app.run(host='0.0.0.0', port=5000, threaded=True)

class MainController:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.activity_tracker = ActivityTracker(os.path.join(data_dir, "activity"))
        self.webcam_recorder = WebcamRecorder(os.path.join(data_dir, "webcam"))
        self.advanced_analytics = AdvancedAnalytics(os.path.join(data_dir, "analysis"))
        self.is_running = False
        self.analysis_thread = None
        self.last_analysis_time = None
        self.analysis_interval = 300  # 5 minutes
        self.insights = {}

    def start(self):
        if not self.is_running:
            self.is_running = True
            
            # Start activity tracker
            self.activity_tracker.start()
            
            # Start webcam recorder
            self.webcam_recorder.start()
            
            # Start analysis thread
            self.analysis_thread = threading.Thread(target=self._analysis_loop)
            self.analysis_thread.daemon = True
            self.analysis_thread.start()

    def stop(self):
        if self.is_running:
            self.is_running = False
            
            # Stop activity tracker
            self.activity_tracker.stop()
            
            # Stop webcam recorder
            self.webcam_recorder.stop()
            
            # Wait for analysis thread to finish
            if self.analysis_thread:
                self.analysis_thread.join()

    def _analysis_loop(self):
        while self.is_running:
            current_time = time.time()
            
            # Check if it's time to perform analysis
            if (self.last_analysis_time is None or 
                current_time - self.last_analysis_time >= self.analysis_interval):
                
                # Perform analysis
                self._perform_analysis()
                
                self.last_analysis_time = current_time
            
            time.sleep(1)  # Sleep to prevent high CPU usage

    def _perform_analysis(self):
        # Get recent activity data
        activity_data = self.activity_tracker.get_recent_events(limit=1000)
        
        # Get recent webcam analysis
        webcam_data = self.webcam_recorder.get_recent_analysis(limit=100)
        
        # Calculate basic metrics
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'activity_level': self._calculate_activity_level(activity_data),
            'posture_quality': self._calculate_posture_quality(webcam_data),
            'focus_time': self._calculate_focus_time(activity_data),
            'break_opportunities': self._identify_break_opportunities(activity_data)
        }
        
        # Perform advanced analytics
        health_risk = self.advanced_analytics.predict_health_risk({
            'posture_score': metrics['posture_quality'],
            'attention_level': metrics['focus_time']['avg_focus_score'],
            'activity_level': metrics['activity_level'],
            'inactivity_duration': self._calculate_inactivity_duration(activity_data),
            'stress_level': self._calculate_stress_level(activity_data, webcam_data)
        })
        
        break_opportunities = self.advanced_analytics.identify_break_opportunities(activity_data)
        focus_analysis = self.advanced_analytics.analyze_focus_time(activity_data)
        
        # Combine all insights
        self.insights = {
            **metrics,
            'health_risk': health_risk,
            'break_opportunities': break_opportunities,
            'focus_analysis': focus_analysis
        }
        
        # Save analysis results
        self._save_analysis(self.insights)

    def _calculate_activity_level(self, activity_data: list) -> float:
        if not activity_data:
            return 0.0
        
        # Count keyboard and mouse events in the last hour
        recent_events = [
            event for event in activity_data
            if (datetime.now() - datetime.fromisoformat(event['timestamp'])).total_seconds() <= 3600
        ]
        
        return len(recent_events) / 1000.0  # Normalize to a scale of 0-1

    def _calculate_posture_quality(self, webcam_data: list) -> float:
        if not webcam_data:
            return 0.5  # Neutral if no data
        
        # Calculate percentage of time in good posture
        good_posture_count = sum(
            1 for data in webcam_data
            if data['posture'] == 'neutral'
        )
        
        return good_posture_count / len(webcam_data)

    def _calculate_focus_time(self, activity_data: list) -> int:
        if not activity_data:
            return 0
        
        # Calculate continuous activity periods
        focus_periods = []
        current_period = 0
        
        for i in range(1, len(activity_data)):
            prev_time = datetime.fromisoformat(activity_data[i-1]['timestamp'])
            curr_time = datetime.fromisoformat(activity_data[i]['timestamp'])
            
            time_diff = (curr_time - prev_time).total_seconds()
            
            if time_diff <= 300:  # 5 minutes
                current_period += time_diff
            else:
                if current_period > 0:
                    focus_periods.append(current_period)
                current_period = 0
        
        if current_period > 0:
            focus_periods.append(current_period)
        
        return int(sum(focus_periods) / 60)  # Convert to minutes

    def _identify_break_opportunities(self, activity_data: list) -> list:
        if not activity_data:
            return []
        
        break_opportunities = []
        last_activity_time = None
        
        for event in activity_data:
            event_time = datetime.fromisoformat(event['timestamp'])
            
            if last_activity_time:
                time_diff = (event_time - last_activity_time).total_seconds()
                
                # If there's a gap of more than 5 minutes, it's a potential break opportunity
                if time_diff >= 300:
                    break_opportunities.append({
                        'start_time': last_activity_time.isoformat(),
                        'end_time': event_time.isoformat(),
                        'duration_minutes': int(time_diff / 60)
                    })
            
            last_activity_time = event_time
        
        return break_opportunities

    def _calculate_stress_level(self, activity_data: list, webcam_data: list) -> float:
        """Calculate stress level based on activity patterns and webcam analysis."""
        if not activity_data or not webcam_data:
            return 0.0
        
        # Calculate activity-based stress indicators
        activity_stress = 0.0
        if len(activity_data) >= 2:
            # Look for rapid changes in activity level
            activity_changes = []
            for i in range(1, len(activity_data)):
                prev_level = activity_data[i-1].get('activity_level', 0)
                curr_level = activity_data[i].get('activity_level', 0)
                activity_changes.append(abs(curr_level - prev_level))
            
            # High variance in activity levels indicates potential stress
            activity_stress = min(1.0, sum(activity_changes) / len(activity_changes) * 2)
        
        # Calculate webcam-based stress indicators
        webcam_stress = 0.0
        if webcam_data:
            # Look for facial expressions and posture changes
            stress_scores = [d.get('stress_score', 0) for d in webcam_data]
            webcam_stress = sum(stress_scores) / len(stress_scores)
        
        # Combine both indicators with weights
        return 0.6 * activity_stress + 0.4 * webcam_stress

    def _calculate_inactivity_duration(self, activity_data: list) -> int:
        """Calculate the duration of current inactivity period."""
        if not activity_data:
            return 0
        
        last_activity = activity_data[-1]
        last_time = datetime.fromisoformat(last_activity['timestamp'])
        current_time = datetime.now()
        
        return int((current_time - last_time).total_seconds())

    def _save_analysis(self, insights: Dict[str, Any]):
        # Create analysis directory if it doesn't exist
        analysis_dir = os.path.join(self.data_dir, "analysis")
        os.makedirs(analysis_dir, exist_ok=True)
        
        # Save insights
        filename = os.path.join(
            analysis_dir,
            f"insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(filename, 'w') as f:
            json.dump(insights, f, indent=2)

    def get_current_metrics(self) -> Dict[str, Any]:
        return self.insights

if __name__ == '__main__':
    # Verify license first
    license_manager = LicenseManager()
    if not license_manager.is_licensed():
        print("License validation failed. Please check your license key.")
        exit(1)

    # Start dashboard in separate thread
    dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
    dashboard_thread.start()

    print("Productivity Analytics System started. Access dashboard at http://localhost:5000")
    print("Press Ctrl+C to stop the system.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping all components...")
        for component in processes:
            stop_component(component)
        print("System stopped.")
