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
