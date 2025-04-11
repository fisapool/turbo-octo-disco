import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Dict, List, Optional, Any
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataCorrelator:
    def __init__(self, config: Dict = None):
        self.config = config or {
            'webcam_data_dir': 'webcam_data',
            'hid_data_dir': 'hid_system_data',
            'correlation_data_dir': 'correlation_data',
            'time_window': 300,  # 5 minutes in seconds
            'correlation_interval': 3600,  # 1 hour in seconds
            'correlation_methods': [
                'pearson',
                'spearman',
                'kendall',
                'dynamic_time_warping',
                'cross_correlation',
                'mutual_information',
                'granger_causality'
            ],
            'optimization': {
                'use_caching': True,
                'cache_size': 1000,
                'parallel_processing': True,
                'batch_size': 100,
                'use_gpu': False,
                'preprocessing': {
                    'normalize': True,
                    'detrend': True,
                    'remove_outliers': True
                }
            }
        }
        
        # Create directories
        self.webcam_dir = Path(self.config['webcam_data_dir'])
        self.hid_dir = Path(self.config['hid_data_dir'])
        self.correlation_dir = Path(self.config['correlation_data_dir'])
        self.correlation_dir.mkdir(exist_ok=True)
        
        # Initialize correlation cache
        self.correlation_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Initialize GPU if available
        self.gpu_available = False
        if self.config['optimization']['use_gpu']:
            try:
                import cupy as cp
                self.gpu_available = True
                self.cp = cp
            except ImportError:
                logger.warning("CuPy not available. Falling back to CPU processing.")
        
    def load_webcam_data(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Load webcam analysis data within the specified time range."""
        data = []
        
        # Load analysis files
        for file_path in self.webcam_dir.glob('analysis_*.json'):
            file_time = datetime.strptime(
                file_path.stem.split('_')[1],
                '%Y%m%d_%H%M%S'
            )
            
            if start_time <= file_time <= end_time:
                try:
                    with open(file_path, 'r') as f:
                        file_data = json.load(f)
                        data.append(file_data)
                except Exception as e:
                    logger.error(f"Error loading webcam data from {file_path}: {e}")
        
        return sorted(data, key=lambda x: x['timestamp'])
    
    def load_hid_data(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Load HID metrics data within the specified time range."""
        data = []
        
        # Load metrics files
        for file_path in self.hid_dir.glob('metrics_*.json'):
            file_time = datetime.strptime(
                file_path.stem.split('_')[1],
                '%Y%m%d_%H%M%S'
            )
            
            if start_time <= file_time <= end_time:
                try:
                    with open(file_path, 'r') as f:
                        file_data = json.load(f)
                        if isinstance(file_data, list):
                            data.extend(file_data)
                        else:
                            data.append(file_data)
                except Exception as e:
                    logger.error(f"Error loading HID data from {file_path}: {e}")
        
        return sorted(data, key=lambda x: x['timestamp'])
    
    def _calculate_dynamic_time_warping(self, series1: np.ndarray, series2: np.ndarray) -> float:
        """Calculate Dynamic Time Warping distance between two time series."""
        try:
            from dtw import dtw
            alignment = dtw(series1, series2)
            return alignment.distance
        except ImportError:
            logger.warning("DTW package not installed. Using Euclidean distance instead.")
            return np.linalg.norm(series1 - series2)
    
    def _preprocess_data(self, series: np.ndarray) -> np.ndarray:
        """Preprocess time series data for correlation analysis."""
        if self.config['optimization']['preprocessing']['normalize']:
            series = (series - np.mean(series)) / np.std(series)
        
        if self.config['optimization']['preprocessing']['detrend']:
            from scipy import signal
            series = signal.detrend(series)
        
        if self.config['optimization']['preprocessing']['remove_outliers']:
            q1 = np.percentile(series, 25)
            q3 = np.percentile(series, 75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            series = np.clip(series, lower_bound, upper_bound)
        
        return series
    
    def _calculate_mutual_information(self, series1: np.ndarray, series2: np.ndarray) -> float:
        """Calculate mutual information between two time series."""
        try:
            from sklearn.feature_selection import mutual_info_regression
            mi = mutual_info_regression(
                series1.reshape(-1, 1),
                series2,
                random_state=42
            )
            return float(mi[0])
        except Exception as e:
            logger.error(f"Error calculating mutual information: {str(e)}")
            return np.nan
    
    def _calculate_granger_causality(self, series1: np.ndarray, series2: np.ndarray) -> Dict[str, float]:
        """Calculate Granger causality between two time series."""
        try:
            from statsmodels.tsa.stattools import grangercausalitytests
            data = np.column_stack((series1, series2))
            results = grangercausalitytests(data, maxlag=5, verbose=False)
            
            causality = {}
            for lag in results:
                f_test = results[lag][0]['ssr_chi2test']
                causality[f'lag_{lag}'] = float(f_test[1])  # p-value
            
            return causality
        except Exception as e:
            logger.error(f"Error calculating Granger causality: {str(e)}")
            return {'error': np.nan}
    
    def _calculate_cross_correlation(self, series1: np.ndarray, series2: np.ndarray) -> Dict[str, float]:
        """Calculate cross-correlation between two time series."""
        try:
            from scipy import signal
            correlation = signal.correlate(series1, series2, mode='full')
            lags = signal.correlation_lags(len(series1), len(series2))
            
            # Find the lag with maximum correlation
            max_corr_idx = np.argmax(np.abs(correlation))
            max_corr = correlation[max_corr_idx]
            max_lag = lags[max_corr_idx]
            
            return {
                'max_correlation': float(max_corr),
                'max_lag': int(max_lag),
                'normalized_correlation': float(max_corr / (np.std(series1) * np.std(series2) * len(series1)))
            }
        except Exception as e:
            logger.error(f"Error calculating cross-correlation: {str(e)}")
            return {'error': np.nan}
    
    def _calculate_correlations(self, synced_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate correlations between different data streams with enhanced methods."""
        correlations = {}
        
        try:
            # Convert data to numeric arrays where possible
            numeric_data = {}
            for stream, data in synced_data.items():
                if isinstance(data, dict):
                    # Extract numeric values from dictionaries
                    numeric_values = [v for v in data.values() if isinstance(v, (int, float))]
                    if numeric_values:
                        numeric_data[stream] = np.array(numeric_values)
            
            # Calculate correlations between streams
            streams = list(numeric_data.keys())
            for i in range(len(streams)):
                for j in range(i + 1, len(streams)):
                    stream1, stream2 = streams[i], streams[j]
                    
                    # Preprocess data
                    series1 = self._preprocess_data(numeric_data[stream1])
                    series2 = self._preprocess_data(numeric_data[stream2])
                    
                    # Calculate various correlation metrics
                    correlations[f"{stream1}_{stream2}"] = {
                        'pearson': float(np.corrcoef(series1, series2)[0, 1]),
                        'spearman': float(spearmanr(series1, series2)[0]),
                        'kendall': float(kendalltau(series1, series2)[0]),
                        'dtw': float(self._calculate_dynamic_time_warping(series1, series2)),
                        'mutual_information': self._calculate_mutual_information(series1, series2),
                        'granger_causality': self._calculate_granger_causality(series1, series2),
                        'cross_correlation': self._calculate_cross_correlation(series1, series2)
                    }
        
        except Exception as e:
            logger.error(f"Error calculating correlations: {str(e)}")
        
        return correlations
    
    def _optimize_correlation_calculation(self, 
                                        webcam_df: pd.DataFrame, 
                                        hid_df: pd.DataFrame) -> Dict[str, Any]:
        """Optimize correlation calculation using caching and parallel processing."""
        correlations = {}
        cache_key = None
        
        if self.config['optimization']['use_caching']:
            # Create cache key from dataframes
            cache_key = hash(str(webcam_df.values.tobytes()) + str(hid_df.values.tobytes()))
            if cache_key in self.correlation_cache:
                self.cache_hits += 1
                return self.correlation_cache[cache_key]
            self.cache_misses += 1
        
        try:
            # Process in batches if parallel processing is enabled
            if self.config['optimization']['parallel_processing']:
                from concurrent.futures import ThreadPoolExecutor
                
                def process_batch(batch):
                    return self._calculate_correlations(batch)
                
                # Split data into batches
                batch_size = self.config['optimization']['batch_size']
                batches = []
                for i in range(0, len(webcam_df), batch_size):
                    batch = {
                        'webcam': webcam_df.iloc[i:i+batch_size],
                        'hid': hid_df.iloc[i:i+batch_size]
                    }
                    batches.append(batch)
                
                # Process batches in parallel
                with ThreadPoolExecutor() as executor:
                    batch_results = list(executor.map(process_batch, batches))
                
                # Combine results
                for result in batch_results:
                    for method, value in result.items():
                        if method not in correlations:
                            correlations[method] = []
                        correlations[method].append(value)
                
                # Average the results
                correlations = {method: np.nanmean(values) 
                              for method, values in correlations.items()}
            else:
                correlations = self._calculate_correlations(
                    {
                        'webcam': webcam_df.values,
                        'hid': hid_df.values
                    }
                )
            
            # Cache results if enabled
            if self.config['optimization']['use_caching']:
                self.correlation_cache[cache_key] = correlations
                # Maintain cache size
                if len(self.correlation_cache) > self.config['optimization']['cache_size']:
                    self.correlation_cache.pop(next(iter(self.correlation_cache)))
            
            return correlations
        except Exception as e:
            logger.error(f"Error in optimized correlation calculation: {str(e)}")
            return {method: np.nan for method in self.config['correlation_methods']}
    
    def correlate_data(self, start_time: Optional[datetime] = None) -> Dict:
        """Correlate webcam and HID data with advanced optimization."""
        end_time = datetime.now()
        if start_time is None:
            start_time = end_time - timedelta(seconds=self.config['correlation_interval'])
        
        # Load data
        webcam_data = self.load_webcam_data(start_time, end_time)
        hid_data = self.load_hid_data(start_time, end_time)
        
        # Convert to pandas DataFrames
        webcam_df = pd.DataFrame([
            {
                'timestamp': d['timestamp'],
                'posture_quality': d['posture']['posture_quality'],
                'shoulder_alignment': d['posture']['shoulder_alignment'],
                'back_straightness': d['posture']['back_straightness'],
                'head_position': d['posture']['head_position'],
                'face_count': len(d['faces'])
            }
            for d in webcam_data if 'posture' in d
        ])
        
        hid_df = pd.DataFrame([
            {
                'timestamp': d['timestamp'],
                'cpu_percent': d['system']['cpu_percent'],
                'memory_percent': d['system']['memory_percent'],
                'key_presses': d['hid']['keyboard_events']['key_presses'],
                'mouse_clicks': d['hid']['mouse_events']['clicks'],
                'active_window': d['hid']['active_window']
            }
            for d in hid_data
        ])
        
        if webcam_df.empty or hid_df.empty:
            logger.warning("Insufficient data for correlation analysis")
            return {}
        
        # Convert timestamps and set index
        webcam_df['timestamp'] = pd.to_datetime(webcam_df['timestamp'])
        hid_df['timestamp'] = pd.to_datetime(hid_df['timestamp'])
        webcam_df.set_index('timestamp', inplace=True)
        hid_df.set_index('timestamp', inplace=True)
        
        # Resample and align data
        webcam_resampled = webcam_df.resample('1T').mean()
        hid_resampled = hid_df.resample('1T').mean()
        
        # Merge dataframes
        merged_df = pd.merge(
            webcam_resampled,
            hid_resampled,
            left_index=True,
            right_index=True,
            how='outer'
        )
        
        # Calculate correlations with optimization
        correlations = {
            'posture_vs_activity': self._optimize_correlation_calculation(
                merged_df[['posture_quality']],
                merged_df[['key_presses', 'mouse_clicks']].mean(axis=1)
            ),
            'system_impact': self._optimize_correlation_calculation(
                merged_df[['posture_quality']],
                merged_df[['cpu_percent', 'memory_percent']].mean(axis=1)
            ),
            'time_patterns': self._analyze_time_patterns(merged_df),
            'environmental_factors': self._analyze_environmental_factors(merged_df),
            'performance_metrics': {
                'cache_hits': self.cache_hits,
                'cache_misses': self.cache_misses,
                'cache_hit_ratio': self.cache_hits / (self.cache_hits + self.cache_misses) 
                if (self.cache_hits + self.cache_misses) > 0 else 0
            }
        }
        
        # Save correlation results
        self._save_correlation_results(correlations)
        
        return correlations
    
    def _analyze_posture_activity_correlation(self, df: pd.DataFrame) -> Dict:
        """Analyze correlation between posture quality and user activity."""
        correlations = {}
        
        if not df.empty:
            # Correlation between posture quality and keyboard/mouse activity
            activity_corr = df['posture_quality'].corr(df['key_presses'] + df['mouse_clicks'])
            correlations['activity_impact'] = float(activity_corr) if not np.isnan(activity_corr) else 0
            
            # Average posture quality during high activity periods
            high_activity = df[df['key_presses'] + df['mouse_clicks'] > (df['key_presses'] + df['mouse_clicks']).median()]
            correlations['high_activity_posture'] = float(high_activity['posture_quality'].mean()) if not high_activity.empty else 0
        
        return correlations
    
    def _analyze_system_impact(self, df: pd.DataFrame) -> Dict:
        """Analyze correlation between system metrics and user behavior."""
        correlations = {}
        
        if not df.empty:
            # Correlation between system load and posture
            cpu_corr = df['posture_quality'].corr(df['cpu_percent'])
            correlations['cpu_impact'] = float(cpu_corr) if not np.isnan(cpu_corr) else 0
            
            # Correlation between system load and activity
            activity_cpu_corr = df['cpu_percent'].corr(df['key_presses'] + df['mouse_clicks'])
            correlations['activity_cpu_correlation'] = float(activity_cpu_corr) if not np.isnan(activity_cpu_corr) else 0
        
        return correlations
    
    def _analyze_time_patterns(self, df: pd.DataFrame) -> Dict:
        """Analyze temporal patterns in user behavior and posture."""
        patterns = {}
        
        if not df.empty:
            # Add hour of day
            df['hour'] = df.index.hour
            
            # Average posture quality by hour
            hourly_posture = df.groupby('hour')['posture_quality'].mean()
            patterns['hourly_posture'] = hourly_posture.to_dict()
            
            # Activity patterns by hour
            hourly_activity = df.groupby('hour')['key_presses'].mean()
            patterns['hourly_activity'] = hourly_activity.to_dict()
        
        return patterns
    
    def _analyze_environmental_factors(self, df: pd.DataFrame) -> Dict:
        """Analyze impact of environmental factors on user behavior."""
        factors = {}
        
        if not df.empty:
            # System resource impact
            factors['high_load_impact'] = {
                'posture_quality': float(df[df['cpu_percent'] > 80]['posture_quality'].mean()) if not df.empty else 0,
                'activity_level': float(df[df['cpu_percent'] > 80]['key_presses'].mean()) if not df.empty else 0
            }
            
            # Face detection impact
            factors['face_detection_impact'] = {
                'posture_quality': float(df[df['face_count'] > 0]['posture_quality'].mean()) if not df.empty else 0,
                'activity_level': float(df[df['face_count'] > 0]['key_presses'].mean()) if not df.empty else 0
            }
        
        return factors
    
    def _save_correlation_results(self, correlations: Dict) -> None:
        """Save correlation results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = self.correlation_dir / f"correlation_{timestamp}.json"
        
        with open(file_path, 'w') as f:
            json.dump(correlations, f, indent=2)
        
        logger.info(f"Saved correlation results to {file_path}")
    
    def get_latest_correlation(self) -> Optional[Dict]:
        """Get the most recent correlation results."""
        try:
            latest_file = max(self.correlation_dir.glob('correlation_*.json'))
            with open(latest_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading latest correlation: {e}")
            return None

if __name__ == "__main__":
    correlator = DataCorrelator()
    correlations = correlator.correlate_data()
    print(json.dumps(correlations, indent=2)) 