#!/usr/bin/env python3
"""
Activity Data Analyzer

Processes and analyzes data from:
- active_window_log.txt (window titles)
- activity_log.txt (keyboard/mouse events)

Generates insights about:
- Application usage patterns
- Productivity metrics
- Activity correlations
"""

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import re
import os

# Configuration
LOG_DIR = r"C:\Users\USER\Documents\AppActivityLogs"
WINDOW_LOG = os.path.join(LOG_DIR, "active_window_log.txt")
ACTIVITY_LOG = os.path.join(LOG_DIR, "activity_log.txt")
OUTPUT_DIR = os.path.join(LOG_DIR, "AnalysisResults")

def load_window_data():
    """Load and parse window activity log"""
    data = []
    with open(WINDOW_LOG, 'r') as f:
        for line in f:
            try:
                timestamp, title = line.strip().split(': ', 1)
                app = re.split(r' - | \| ', title)[0]  # Extract application name
                data.append({
                    'timestamp': datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'),
                    'window_title': title,
                    'application': app
                })
            except:
                continue
    return pd.DataFrame(data)

def load_activity_data():
    """Load and parse keyboard/mouse activity log"""
    data = []
    with open(ACTIVITY_LOG, 'r') as f:
        for line in f:
            try:
                parts = line.strip().split(' - ', 1)
                if len(parts) == 2:
                    timestamp, activity = parts
                    data.append({
                        'timestamp': datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'),
                        'activity': activity
                    })
            except:
                continue
    return pd.DataFrame(data)

def analyze_usage_patterns(window_df):
    """Analyze application usage patterns"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    # Hourly usage patterns
    window_df['hour'] = window_df['timestamp'].dt.hour
    hourly_usage = window_df.groupby(['hour', 'application']).size().unstack()
    hourly_usage.plot(kind='area', stacked=True, figsize=(12,6))
    plt.title('Hourly Application Usage')
    plt.ylabel('Seconds Active')
    plt.savefig(os.path.join(OUTPUT_DIR, 'hourly_usage.png'))
    
    # Top applications
    top_apps = window_df['application'].value_counts().head(10)
    top_apps.plot(kind='barh', figsize=(10,6))
    plt.title('Top 10 Applications by Usage Time')
    plt.savefig(os.path.join(OUTPUT_DIR, 'top_apps.png'))

def generate_report():
    """Generate comprehensive analysis report"""
    window_df = load_window_data()
    activity_df = load_activity_data()
    
    analyze_usage_patterns(window_df)
    # Additional analysis functions would be added here
    
    print(f"Analysis complete. Results saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    generate_report()
