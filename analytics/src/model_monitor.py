import pandas as pd
import numpy as np
from datetime import datetime
import os
import json
import logging
from typing import Dict, List, Optional, Any
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelMonitor:
    def __init__(self, metrics_dir: str = 'reports/model_metrics'):
        self.metrics_dir = metrics_dir
        os.makedirs(metrics_dir, exist_ok=True)
        
        # Initialize metrics history file
        self.metrics_file = os.path.join(metrics_dir, 'metrics_history.csv')
        if not os.path.exists(self.metrics_file):
            pd.DataFrame(columns=[
                'timestamp',
                'model_type',
                'accuracy',
                'precision',
                'recall',
                'f1_score',
                'num_samples',
                'version'
            ]).to_csv(self.metrics_file, index=False)
    
    def log_metrics(self, 
                   model_type: str,
                   y_true: np.ndarray,
                   y_pred: np.ndarray,
                   version: str,
                   metadata: Optional[Dict] = None):
        """
        Log model performance metrics.
        
        Args:
            model_type: Type of model (e.g., 'lstm', 'random_forest')
            y_true: True labels
            y_pred: Predicted labels
            version: Model version
            metadata: Additional metadata to store
        """
        try:
            # Calculate metrics
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'model_type': model_type,
                'accuracy': accuracy_score(y_true, y_pred),
                'precision': precision_score(y_true, y_pred, average='weighted'),
                'recall': recall_score(y_true, y_pred, average='weighted'),
                'f1_score': f1_score(y_true, y_pred, average='weighted'),
                'num_samples': len(y_true),
                'version': version
            }
            
            # Add metadata if provided
            if metadata:
                metrics.update(metadata)
            
            # Append to metrics history
            pd.DataFrame([metrics]).to_csv(
                self.metrics_file,
                mode='a',
                header=False,
                index=False
            )
            
            logger.info(f"Logged metrics for {model_type} model version {version}")
        except Exception as e:
            logger.error(f"Error logging metrics: {str(e)}")
            raise
    
    def check_performance_drift(self, 
                              model_type: str,
                              window_size: int = 5,
                              threshold: float = 0.05) -> Dict[str, Any]:
        """
        Check for performance drift in model metrics.
        
        Args:
            model_type: Type of model to check
            window_size: Number of recent evaluations to consider
            threshold: Performance drop threshold to trigger alert
            
        Returns:
            Dictionary containing drift analysis results
        """
        try:
            # Load metrics history
            df = pd.read_csv(self.metrics_file)
            model_metrics = df[df['model_type'] == model_type]
            
            if len(model_metrics) < window_size:
                return {'status': 'insufficient_data'}
            
            # Get recent and baseline metrics
            recent = model_metrics.tail(window_size)
            baseline = model_metrics.iloc[-(window_size*2):-window_size]
            
            # Calculate average metrics
            recent_avg = recent[['accuracy', 'precision', 'recall', 'f1_score']].mean()
            baseline_avg = baseline[['accuracy', 'precision', 'recall', 'f1_score']].mean()
            
            # Calculate performance drops
            drops = {
                metric: baseline_avg[metric] - recent_avg[metric]
                for metric in ['accuracy', 'precision', 'recall', 'f1_score']
            }
            
            # Check for significant drops
            significant_drops = {
                metric: drop
                for metric, drop in drops.items()
                if drop > threshold
            }
            
            return {
                'status': 'drift_detected' if significant_drops else 'stable',
                'recent_metrics': recent_avg.to_dict(),
                'baseline_metrics': baseline_avg.to_dict(),
                'performance_drops': drops,
                'significant_drops': significant_drops
            }
        except Exception as e:
            logger.error(f"Error checking performance drift: {str(e)}")
            raise
    
    def generate_performance_report(self, 
                                  model_type: str,
                                  output_dir: Optional[str] = None) -> str:
        """
        Generate a comprehensive performance report for a model.
        
        Args:
            model_type: Type of model to generate report for
            output_dir: Directory to save report (defaults to metrics_dir)
            
        Returns:
            Path to the generated report
        """
        try:
            if output_dir is None:
                output_dir = self.metrics_dir
            
            # Load metrics history
            df = pd.read_csv(self.metrics_file)
            model_metrics = df[df['model_type'] == model_type]
            
            if len(model_metrics) == 0:
                raise ValueError(f"No metrics found for model type: {model_type}")
            
            # Create report directory
            report_dir = os.path.join(output_dir, 'reports', model_type)
            os.makedirs(report_dir, exist_ok=True)
            
            # Generate plots
            self._generate_metrics_plots(model_metrics, report_dir)
            
            # Calculate summary statistics
            summary = {
                'total_evaluations': len(model_metrics),
                'latest_metrics': model_metrics.iloc[-1].to_dict(),
                'average_metrics': model_metrics[['accuracy', 'precision', 'recall', 'f1_score']].mean().to_dict(),
                'performance_trend': self._calculate_performance_trend(model_metrics)
            }
            
            # Save summary
            summary_file = os.path.join(report_dir, 'summary.json')
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"Generated performance report for {model_type}")
            return report_dir
        except Exception as e:
            logger.error(f"Error generating performance report: {str(e)}")
            raise
    
    def _generate_metrics_plots(self, metrics: pd.DataFrame, output_dir: str):
        """Generate visualization plots for model metrics."""
        try:
            # Plot metrics over time
            plt.figure(figsize=(12, 8))
            
            for metric in ['accuracy', 'precision', 'recall', 'f1_score']:
                plt.plot(metrics['timestamp'], metrics[metric], label=metric)
            
            plt.title('Model Performance Metrics Over Time')
            plt.xlabel('Timestamp')
            plt.ylabel('Score')
            plt.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'metrics_trend.png'))
            plt.close()
            
            # Plot correlation heatmap
            plt.figure(figsize=(10, 8))
            sns.heatmap(
                metrics[['accuracy', 'precision', 'recall', 'f1_score']].corr(),
                annot=True,
                cmap='coolwarm'
            )
            plt.title('Metrics Correlation Heatmap')
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, 'metrics_correlation.png'))
            plt.close()
        except Exception as e:
            logger.error(f"Error generating metrics plots: {str(e)}")
            raise
    
    def _calculate_performance_trend(self, metrics: pd.DataFrame) -> Dict[str, float]:
        """Calculate performance trends over time."""
        try:
            trend = {}
            for metric in ['accuracy', 'precision', 'recall', 'f1_score']:
                # Calculate slope using linear regression
                x = np.arange(len(metrics))
                y = metrics[metric].values
                slope = np.polyfit(x, y, 1)[0]
                trend[metric] = slope
            
            return trend
        except Exception as e:
            logger.error(f"Error calculating performance trend: {str(e)}")
            raise 