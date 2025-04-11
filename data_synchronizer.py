import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import threading
from dataclasses import dataclass, asdict
import logging
from pathlib import Path
import numpy as np
from scipy import signal
import pandas as pd
import time
from prometheus_client import Counter, Histogram, Gauge

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
SYNC_OPERATIONS = Counter('data_sync_operations_total', 'Total number of synchronization operations')
SYNC_DURATION = Histogram('data_sync_duration_seconds', 'Time spent synchronizing data')
STREAM_COUNT = Gauge('active_data_streams', 'Number of active data streams')
BUFFER_SIZE = Gauge('data_buffer_size', 'Size of data buffer in bytes')

@dataclass
class SynchronizedDataPoint:
    timestamp: str
    data_streams: Dict[str, Any]
    correlations: Dict[str, float]
    metadata: Dict[str, Any]
    performance_metrics: Dict[str, float]

@dataclass
class TimeSeriesData:
    """Advanced time series data structure with interpolation and alignment capabilities."""
    timestamps: List[datetime]
    values: Dict[str, List[float]]
    metadata: Dict[str, Any]
    interpolation_method: str = 'linear'
    time_unit: str = 'milliseconds'
    quality_metrics: Dict[str, float] = None
    
    def __post_init__(self):
        self._validate_data()
        if self.quality_metrics is None:
            self.quality_metrics = self._calculate_quality_metrics()
    
    def _validate_data(self):
        """Validate the time series data structure."""
        if not self.timestamps or not self.values:
            raise ValueError("Timestamps and values cannot be empty")
        
        if len(self.timestamps) != len(next(iter(self.values.values()))):
            raise ValueError("Timestamps and values must have the same length")
        
        # Check for monotonic timestamps
        if not all(self.timestamps[i] <= self.timestamps[i+1] for i in range(len(self.timestamps)-1)):
            raise ValueError("Timestamps must be monotonically increasing")
    
    def _calculate_quality_metrics(self) -> Dict[str, float]:
        """Calculate quality metrics for the time series."""
        metrics = {}
        
        try:
            # Calculate sampling rate consistency
            time_diffs = np.diff([t.timestamp() for t in self.timestamps])
            metrics['sampling_rate_std'] = float(np.std(time_diffs))
            metrics['sampling_rate_mean'] = float(np.mean(time_diffs))
            
            # Calculate data completeness
            total_points = len(self.timestamps)
            metrics['completeness'] = 1.0  # Will be updated if missing values are found
            
            # Calculate value statistics
            for key, values in self.values.items():
                metrics[f'{key}_mean'] = float(np.mean(values))
                metrics[f'{key}_std'] = float(np.std(values))
                metrics[f'{key}_min'] = float(np.min(values))
                metrics[f'{key}_max'] = float(np.max(values))
                
                # Detect outliers using IQR
                q1 = np.percentile(values, 25)
                q3 = np.percentile(values, 75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                outliers = np.sum((values < lower_bound) | (values > upper_bound))
                metrics[f'{key}_outlier_ratio'] = float(outliers / len(values))
            
            return metrics
        except Exception as e:
            logger.error(f"Error calculating quality metrics: {str(e)}")
            return {}
    
    def resample(self, target_frequency: str, method: str = 'mean') -> 'TimeSeriesData':
        """Resample the time series to a target frequency with multiple methods."""
        df = pd.DataFrame(self.values, index=self.timestamps)
        
        if method == 'mean':
            resampled = df.resample(target_frequency).mean()
        elif method == 'median':
            resampled = df.resample(target_frequency).median()
        elif method == 'sum':
            resampled = df.resample(target_frequency).sum()
        elif method == 'min':
            resampled = df.resample(target_frequency).min()
        elif method == 'max':
            resampled = df.resample(target_frequency).max()
        else:
            raise ValueError(f"Unsupported resampling method: {method}")
        
        return TimeSeriesData(
            timestamps=resampled.index.to_list(),
            values=resampled.to_dict('list'),
            metadata=self.metadata,
            interpolation_method=self.interpolation_method,
            time_unit=self.time_unit
        )
    
    def interpolate(self, method: Optional[str] = None, limit: Optional[int] = None) -> 'TimeSeriesData':
        """Interpolate missing values in the time series with configurable limits."""
        if method:
            self.interpolation_method = method
            
        df = pd.DataFrame(self.values, index=self.timestamps)
        interpolated = df.interpolate(
            method=self.interpolation_method,
            limit=limit,
            limit_direction='both'
        )
        
        # Update quality metrics after interpolation
        new_series = TimeSeriesData(
            timestamps=interpolated.index.to_list(),
            values=interpolated.to_dict('list'),
            metadata=self.metadata,
            interpolation_method=self.interpolation_method,
            time_unit=self.time_unit
        )
        
        return new_series
    
    def align_with(self, other: 'TimeSeriesData', tolerance: Optional[timedelta] = None) -> Tuple['TimeSeriesData', 'TimeSeriesData']:
        """Align two time series to common timestamps with configurable tolerance."""
        df1 = pd.DataFrame(self.values, index=self.timestamps)
        df2 = pd.DataFrame(other.values, index=other.timestamps)
        
        if tolerance is not None:
            # Use pandas merge_asof for approximate matching
            df1_reset = df1.reset_index()
            df2_reset = df2.reset_index()
            
            merged = pd.merge_asof(
                df1_reset,
                df2_reset,
                on='index',
                tolerance=tolerance.total_seconds(),
                direction='nearest'
            )
            
            aligned1 = TimeSeriesData(
                timestamps=merged['index'].to_list(),
                values=df1.loc[merged['index']].to_dict('list'),
                metadata=self.metadata,
                interpolation_method=self.interpolation_method,
                time_unit=self.time_unit
            )
            
            aligned2 = TimeSeriesData(
                timestamps=merged['index'].to_list(),
                values=df2.loc[merged['index']].to_dict('list'),
                metadata=other.metadata,
                interpolation_method=other.interpolation_method,
                time_unit=other.time_unit
            )
        else:
            # Exact matching as before
            common_index = df1.index.intersection(df2.index)
            
            aligned1 = TimeSeriesData(
                timestamps=common_index.to_list(),
                values=df1.loc[common_index].to_dict('list'),
                metadata=self.metadata,
                interpolation_method=self.interpolation_method,
                time_unit=self.time_unit
            )
            
            aligned2 = TimeSeriesData(
                timestamps=common_index.to_list(),
                values=df2.loc[common_index].to_dict('list'),
                metadata=other.metadata,
                interpolation_method=other.interpolation_method,
                time_unit=other.time_unit
            )
        
        return aligned1, aligned2
    
    def detect_anomalies(self, method: str = 'zscore', threshold: float = 3.0) -> Dict[str, List[int]]:
        """Detect anomalies in the time series using various methods."""
        anomalies = {}
        
        for key, values in self.values.items():
            if method == 'zscore':
                z_scores = np.abs((values - np.mean(values)) / np.std(values))
                anomalies[key] = np.where(z_scores > threshold)[0].tolist()
            elif method == 'iqr':
                q1 = np.percentile(values, 25)
                q3 = np.percentile(values, 75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                anomalies[key] = np.where((values < lower_bound) | (values > upper_bound))[0].tolist()
            elif method == 'rolling':
                window_size = min(10, len(values))
                rolling_mean = pd.Series(values).rolling(window=window_size).mean()
                rolling_std = pd.Series(values).rolling(window=window_size).std()
                anomalies[key] = np.where(
                    np.abs(values - rolling_mean) > threshold * rolling_std
                )[0].tolist()
        
        return anomalies
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert the time series to a pandas DataFrame."""
        return pd.DataFrame(self.values, index=self.timestamps)
    
    def plot(self, columns: Optional[List[str]] = None, **kwargs):
        """Plot the time series data."""
        try:
            import matplotlib.pyplot as plt
            
            df = self.to_dataframe()
            if columns:
                df = df[columns]
            
            df.plot(**kwargs)
            plt.show()
        except ImportError:
            logger.error("Matplotlib is not installed. Cannot plot time series.")
            raise

class DataSynchronizer:
    def __init__(self, sync_window_ms: int = 1000, max_buffer_size: int = 1000):
        self.sync_window_ms = sync_window_ms
        self.max_buffer_size = max_buffer_size
        self.data_buffer: Dict[str, List[Dict[str, Any]]] = {}
        self.lock = threading.Lock()
        self.correlation_threshold = 0.7
        self.last_cleanup_time = time.time()
        self.cleanup_interval = 60  # seconds
        self.time_series_data: Dict[str, TimeSeriesData] = {}
        
    def create_time_series(self, stream_name: str, data: Dict[str, Any], timestamp: str) -> TimeSeriesData:
        """Create a time series from stream data."""
        try:
            # Extract numeric values
            numeric_values = {k: v for k, v in data.items() if isinstance(v, (int, float))}
            
            if not numeric_values:
                raise ValueError(f"No numeric values found in stream {stream_name}")
            
            # Create time series
            time_series = TimeSeriesData(
                timestamps=[datetime.fromisoformat(timestamp)],
                values=numeric_values,
                metadata={
                    'stream_name': stream_name,
                    'original_data': data
                }
            )
            
            return time_series
        except Exception as e:
            logger.error(f"Error creating time series: {str(e)}")
            raise
    
    def add_data_stream(self, stream_name: str, data: Dict[str, Any], timestamp: str):
        """Add a new data stream to the synchronizer with time series support."""
        start_time = time.time()
        try:
            with self.lock:
                if stream_name not in self.data_buffer:
                    self.data_buffer[stream_name] = []
                    STREAM_COUNT.inc()
                
                # Check buffer size
                if len(self.data_buffer[stream_name]) >= self.max_buffer_size:
                    logger.warning(f"Buffer size limit reached for stream {stream_name}")
                    self.data_buffer[stream_name] = self.data_buffer[stream_name][-self.max_buffer_size:]
                
                # Add to buffer
                self.data_buffer[stream_name].append({
                    'data': data,
                    'timestamp': timestamp
                })
                
                # Update time series
                time_series = self.create_time_series(stream_name, data, timestamp)
                if stream_name in self.time_series_data:
                    # Merge with existing time series
                    existing = self.time_series_data[stream_name]
                    merged_values = {
                        k: existing.values[k] + time_series.values[k]
                        for k in existing.values.keys()
                    }
                    self.time_series_data[stream_name] = TimeSeriesData(
                        timestamps=existing.timestamps + time_series.timestamps,
                        values=merged_values,
                        metadata=existing.metadata,
                        interpolation_method=existing.interpolation_method,
                        time_unit=existing.time_unit
                    )
                else:
                    self.time_series_data[stream_name] = time_series
                
                # Update buffer size metric
                BUFFER_SIZE.set(self._calculate_buffer_size())
                
                # Periodic cleanup
                current_time = time.time()
                if current_time - self.last_cleanup_time > self.cleanup_interval:
                    self._cleanup_old_data()
                    self.last_cleanup_time = current_time
                
                logger.info(f"Added data to stream: {stream_name}")
                return True
        except Exception as e:
            logger.error(f"Error adding data stream: {str(e)}")
            return False
        finally:
            duration = time.time() - start_time
            SYNC_DURATION.observe(duration)

    def _calculate_buffer_size(self) -> int:
        """Calculate the total size of the data buffer in bytes."""
        try:
            return sum(
                len(json.dumps(point).encode('utf-8'))
                for stream in self.data_buffer.values()
                for point in stream
            )
        except Exception as e:
            logger.error(f"Error calculating buffer size: {str(e)}")
            return 0

    def _cleanup_old_data(self):
        """Remove data points older than the synchronization window."""
        current_time = datetime.now()
        window_start = current_time - timedelta(milliseconds=self.sync_window_ms)
        
        for stream in self.data_buffer:
            initial_count = len(self.data_buffer[stream])
            self.data_buffer[stream] = [
                point for point in self.data_buffer[stream]
                if datetime.fromisoformat(point['timestamp']) >= window_start
            ]
            if len(self.data_buffer[stream]) < initial_count:
                logger.info(f"Cleaned up {initial_count - len(self.data_buffer[stream])} old data points from {stream}")

    def synchronize_data(self) -> Optional[SynchronizedDataPoint]:
        """Synchronize data streams and calculate correlations."""
        start_time = time.time()
        try:
            with self.lock:
                SYNC_OPERATIONS.inc()
                
                if not self.data_buffer:
                    return None
                
                # Get the latest timestamp from all streams
                latest_timestamps = {
                    stream: max(
                        (datetime.fromisoformat(point['timestamp']) 
                         for point in points),
                        default=None
                    )
                    for stream, points in self.data_buffer.items()
                }
                
                if not all(latest_timestamps.values()):
                    return None
                
                # Find the most recent common timestamp
                sync_time = min(latest_timestamps.values())
                
                # Extract data points within sync window
                synced_data = {}
                for stream, points in self.data_buffer.items():
                    window_points = [
                        point for point in points
                        if abs((datetime.fromisoformat(point['timestamp']) - sync_time).total_seconds() * 1000) 
                        <= self.sync_window_ms
                    ]
                    if window_points:
                        synced_data[stream] = window_points[-1]['data']
                
                if not synced_data:
                    return None
                
                # Calculate correlations between streams
                correlations = self._calculate_correlations(synced_data)
                
                # Calculate performance metrics
                performance_metrics = {
                    'sync_duration_ms': (time.time() - start_time) * 1000,
                    'buffer_size_bytes': self._calculate_buffer_size(),
                    'stream_count': len(synced_data),
                    'correlation_count': len(correlations)
                }
                
                return SynchronizedDataPoint(
                    timestamp=sync_time.isoformat(),
                    data_streams=synced_data,
                    correlations=correlations,
                    metadata={
                        'sync_window_ms': self.sync_window_ms,
                        'stream_count': len(synced_data)
                    },
                    performance_metrics=performance_metrics
                )
        except Exception as e:
            logger.error(f"Error synchronizing data: {str(e)}")
            return None
        finally:
            duration = time.time() - start_time
            SYNC_DURATION.observe(duration)

    def _calculate_correlations(self, synced_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate correlations between different data streams."""
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
                    corr = np.corrcoef(numeric_data[stream1], numeric_data[stream2])[0, 1]
                    if not np.isnan(corr):
                        correlations[f"{stream1}_{stream2}"] = float(corr)
        
        except Exception as e:
            logger.error(f"Error calculating correlations: {str(e)}")
        
        return correlations

    def export_synced_data(self, filename: str):
        """Export synchronized data to a JSON file."""
        try:
            synced_point = self.synchronize_data()
            if synced_point:
                with open(filename, 'w') as f:
                    json.dump(asdict(synced_point), f, indent=2)
                logger.info(f"Exported synchronized data to {filename}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error exporting synchronized data: {str(e)}")
            return False

if __name__ == "__main__":
    # Example usage
    synchronizer = DataSynchronizer()
    
    # Example data streams
    synchronizer.add_data_stream(
        "activity",
        {"keyboard_events": 10, "mouse_clicks": 5},
        datetime.now().isoformat()
    )
    
    synchronizer.add_data_stream(
        "webcam",
        {"posture_score": 0.8, "attention_level": 0.9},
        datetime.now().isoformat()
    )
    
    # Synchronize and export data
    synchronizer.export_synced_data("synced_data.json") 