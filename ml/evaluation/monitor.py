"""
monitor.py

Tracks model performance metrics over time and alerts on degradation.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
from sklearn.metrics import accuracy_score, f1_score
from screenshot_classifier import classify_screenshot

class ModelMonitor:
    def __init__(self):
        self.metrics_file = 'reports/model_metrics_history.csv'
        self.drift_threshold = 0.05  # 5% performance drop
        os.makedirs('reports', exist_ok=True)
        
        # Initialize metrics file if it doesn't exist
        if not os.path.exists(self.metrics_file):
            pd.DataFrame(columns=[
                'timestamp',
                'accuracy',
                'f1_score',
                'num_samples',
                'version'
            ]).to_csv(self.metrics_file, index=False)

    def evaluate_batch(self, images, labels, model_version):
        """Evaluate model on a batch of new data"""
        preds = [classify_screenshot(img) for img in images]
        
        # Calculate metrics
        accuracy = accuracy_score(labels, preds)
        f1 = f1_score(labels, preds, average='weighted')
        
        # Save metrics
        new_row = pd.DataFrame([{
            'timestamp': datetime.now().isoformat(),
            'accuracy': accuracy,
            'f1_score': f1,
            'num_samples': len(images),
            'version': model_version
        }])
        
        new_row.to_csv(self.metrics_file, mode='a', header=False, index=False)
        
        # Check for performance drift
        self.check_for_drift()
        
        return accuracy, f1

    def check_for_drift(self):
        """Check if model performance has degraded significantly"""
        df = pd.read_csv(self.metrics_file)
        if len(df) < 2:
            return False
            
        # Get rolling average of last 3 evaluations
        recent = df.tail(3)
        baseline = df.iloc[-4:-1] if len(df) >=4 else df.head(3)
        
        recent_avg = recent[['accuracy', 'f1_score']].mean()
        baseline_avg = baseline[['accuracy', 'f1_score']].mean()
        
        # Calculate performance drop
        accuracy_drop = baseline_avg['accuracy'] - recent_avg['accuracy']
        f1_drop = baseline_avg['f1_score'] - recent_avg['f1_score']
        
        if accuracy_drop > self.drift_threshold or f1_drop > self.drift_threshold:
            self.alert_performance_drop(accuracy_drop, f1_drop)
            return True
        return False

    def alert_performance_drop(self, accuracy_drop, f1_drop):
        """Trigger alert for performance degradation"""
        print(f"WARNING: Model performance degradation detected!")
        print(f"Accuracy drop: {accuracy_drop:.2%}")
        print(f"F1 score drop: {f1_drop:.2%}")
        # TODO: Add email/slack alerts in production

    def plot_performance_trends(self):
        """Generate performance trend visualization"""
        df = pd.read_csv(self.metrics_file)
        if len(df) < 2:
            print("Not enough data to plot trends")
            return
            
        plt.figure(figsize=(12, 6))
        
        # Plot accuracy
        plt.subplot(1, 2, 1)
        plt.plot(df['timestamp'], df['accuracy'], label='Accuracy')
        plt.title('Accuracy Over Time')
        plt.xticks(rotation=45)
        plt.ylim(0, 1)
        
        # Plot F1 score
        plt.subplot(1, 2, 2)
        plt.plot(df['timestamp'], df['f1_score'], label='F1 Score', color='orange')
        plt.title('F1 Score Over Time')
        plt.xticks(rotation=45)
        plt.ylim(0, 1)
        
        plt.tight_layout()
        plt.savefig('reports/performance_trends.png')
        plt.close()

if __name__ == '__main__':
    # Example usage
    monitor = ModelMonitor()
    
    # Simulate evaluation
    test_images = ['sample1.png', 'sample2.png']  # Replace with actual images
    test_labels = ['code', 'document']           # Replace with actual labels
    
    accuracy, f1 = monitor.evaluate_batch(test_images, test_labels, '1.0')
    print(f"Batch evaluation - Accuracy: {accuracy:.2%}, F1: {f1:.2%}")
    
    monitor.plot_performance_trends()
