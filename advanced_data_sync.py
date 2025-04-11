import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import threading
from dataclasses import dataclass, asdict
import logging
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import signal
import time
from prometheus_client import Counter, Histogram, Gauge
from concurrent.futures import ThreadPoolExecutor
import zlib
import msgpack

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
SYNC_OPERATIONS = Counter('advanced_sync_operations_total', 'Total number of advanced synchronization operations')
SYNC_DURATION = Histogram('advanced_sync_duration_seconds', 'Time spent in advanced synchronization')
STREAM_COUNT = Gauge('advanced_active_streams', 'Number of active streams in advanced sync')
BUFFER_SIZE = Gauge('advanced_buffer_size_bytes', 'Size of advanced sync buffer in bytes')
CORRELATION_TIME = Histogram('correlation_calculation_seconds', 'Time spent calculating correlations')

@dataclass
class TimeSeriesPoint:
    timestamp: str
    value: float
    confidence: float
    metadata: Dict[str, Any]

@dataclass
class SynchronizedDataPoint:
    timestamp: str
    data_streams: Dict[str, TimeSeriesPoint]
    correlations: Dict[str, float]
    metadata: Dict[str, Any]
    performance_metrics: Dict[str, float]

class AdvancedDataSynchronizer:
    def __init__(self, 
                 sync_window_ms: int = 1000,
                 max_buffer_size: int = 1000,
                 correlation_window: int = 300,
                 optimization_config: Optional[Dict] = None):
        self.sync_window_ms = sync_window_ms
        self.max_buffer_size = max_buffer_size
        self.correlation_window = correlation_window
        self.optimization_config = optimization_config or {
            'use_caching': True,
            'cache_size': 1000,
            'parallel_processing': True,
            'batch_size': 100,
            'compression': {
                'enabled': True,
                'level': 6,
                'algorithm': 'gzip'
            }
        }
        
        self.data_buffer: Dict[str, List[Dict[str, Any]]] = {}
        self.time_series_data: Dict[str, List[TimeSeriesPoint]] = {}
        self.correlation_cache: Dict[str, Dict] = {}
        self.lock = threading.Lock()
        
        # Initialize metrics
        STREAM_COUNT.set(0)
        BUFFER_SIZE.set(0)
        
    def add_data_stream(self, stream_name: str, data: Dict[str, Any], timestamp: str) -> bool:
        """Add a new data stream with enhanced time series support."""
        start_time = time.time()
        try:
            with self.lock:
                if stream_name not in self.data_buffer:
                    self.data_buffer[stream_name] = []
                    self.time_series_data[stream_name] = []
                    STREAM_COUNT.inc()
                
                # Create time series point
                time_series_point = TimeSeriesPoint(
                    timestamp=timestamp,
                    value=self._extract_numeric_value(data),
                    confidence=self._calculate_confidence(data),
                    metadata=self._extract_metadata(data)
                )
                
                # Add to buffers
                self.data_buffer[stream_name].append({
                    'data': data,
                    'timestamp': timestamp
                })
                self.time_series_data[stream_name].append(time_series_point)
                
                # Maintain buffer size
                if len(self.data_buffer[stream_name]) > self.max_buffer_size:
                    self.data_buffer[stream_name] = self.data_buffer[stream_name][-self.max_buffer_size:]
                    self.time_series_data[stream_name] = self.time_series_data[stream_name][-self.max_buffer_size:]
                
                # Update metrics
                BUFFER_SIZE.set(self._calculate_buffer_size())
                
                return True
        except Exception as e:
            logger.error(f"Error adding data stream: {str(e)}")
            return False
        finally:
            duration = time.time() - start_time
            SYNC_DURATION.observe(duration)
    
    def synchronize_data(self) -> Optional[SynchronizedDataPoint]:
        """Synchronize data streams with advanced correlation."""
        start_time = time.time()
        try:
            with self.lock:
                if not self.data_buffer:
                    return None
                
                # Get latest timestamps
                latest_timestamps = {
                    stream: max(p['timestamp'] for p in points)
                    for stream, points in self.data_buffer.items()
                }
                
                # Find synchronization point
                sync_timestamp = min(latest_timestamps.values())
                
                # Collect synchronized data
                synced_data = {}
                for stream, points in self.data_buffer.items():
                    # Find closest point to sync timestamp
                    closest_point = min(
                        points,
                        key=lambda p: abs(
                            datetime.fromisoformat(p['timestamp']) - 
                            datetime.fromisoformat(sync_timestamp)
                        )
                    )
                    synced_data[stream] = closest_point['data']
                
                # Calculate correlations
                correlations = self._calculate_correlations(synced_data)
                
                # Create synchronized data point
                synchronized_point = SynchronizedDataPoint(
                    timestamp=sync_timestamp,
                    data_streams=synced_data,
                    correlations=correlations,
                    metadata=self._generate_metadata(),
                    performance_metrics=self._calculate_performance_metrics()
                )
                
                SYNC_OPERATIONS.inc()
                return synchronized_point
        except Exception as e:
            logger.error(f"Error synchronizing data: {str(e)}")
            return None
        finally:
            duration = time.time() - start_time
            SYNC_DURATION.observe(duration)
    
    def _calculate_correlations(self, synced_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate correlations between data streams with optimization."""
        start_time = time.time()
        try:
            correlations = {}
            
            # Convert data to numeric arrays
            numeric_data = {}
            for stream, data in synced_data.items():
                numeric_values = [v for v in data.values() if isinstance(v, (int, float))]
                if numeric_values:
                    numeric_data[stream] = np.array(numeric_values)
            
            # Calculate correlations between streams
            streams = list(numeric_data.keys())
            for i in range(len(streams)):
                for j in range(i + 1, len(streams)):
                    stream1, stream2 = streams[i], streams[j]
                    
                    # Check cache
                    cache_key = f"{stream1}_{stream2}"
                    if self.optimization_config['use_caching'] and cache_key in self.correlation_cache:
                        correlations[cache_key] = self.correlation_cache[cache_key]
                        continue
                    
                    # Calculate correlation
                    series1 = numeric_data[stream1]
                    series2 = numeric_data[stream2]
                    
                    # Preprocess data
                    series1 = self._preprocess_data(series1)
                    series2 = self._preprocess_data(series2)
                    
                    # Calculate correlation
                    correlation = self._calculate_advanced_correlation(series1, series2)
                    correlations[cache_key] = correlation
                    
                    # Update cache
                    if self.optimization_config['use_caching']:
                        self.correlation_cache[cache_key] = correlation
                        if len(self.correlation_cache) > self.optimization_config['cache_size']:
                            self.correlation_cache.pop(next(iter(self.correlation_cache)))
            
            return correlations
        except Exception as e:
            logger.error(f"Error calculating correlations: {str(e)}")
            return {}
        finally:
            duration = time.time() - start_time
            CORRELATION_TIME.observe(duration)
    
    def _calculate_advanced_correlation(self, series1: np.ndarray, series2: np.ndarray) -> float:
        """Calculate advanced correlation between two time series."""
        try:
            # Calculate multiple correlation metrics
            pearson = np.corrcoef(series1, series2)[0, 1]
            spearman = pd.Series(series1).corr(pd.Series(series2), method='spearman')
            
            # Calculate dynamic time warping distance
            from dtw import dtw
            dtw_distance = dtw(series1, series2).distance
            
            # Calculate cross-correlation
            cross_corr = signal.correlate(series1, series2, mode='full')
            max_cross_corr = np.max(np.abs(cross_corr))
            
            # Combine metrics with weights
            weights = {
                'pearson': 0.4,
                'spearman': 0.3,
                'dtw': 0.2,
                'cross_corr': 0.1
            }
            
            combined_score = (
                weights['pearson'] * pearson +
                weights['spearman'] * spearman +
                weights['dtw'] * (1 - dtw_distance / max(len(series1), len(series2))) +
                weights['cross_corr'] * (max_cross_corr / (np.std(series1) * np.std(series2) * len(series1)))
            )
            
            return float(combined_score)
        except Exception as e:
            logger.error(f"Error calculating advanced correlation: {str(e)}")
            return 0.0
    
    def _preprocess_data(self, series: np.ndarray) -> np.ndarray:
        """Preprocess time series data for correlation analysis."""
        try:
            # Normalize
            series = (series - np.mean(series)) / np.std(series)
            
            # Detrend
            series = signal.detrend(series)
            
            # Remove outliers
            q1 = np.percentile(series, 25)
            q3 = np.percentile(series, 75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            series = np.clip(series, lower_bound, upper_bound)
            
            return series
        except Exception as e:
            logger.error(f"Error preprocessing data: {str(e)}")
            return series
    
    def _extract_numeric_value(self, data: Dict[str, Any]) -> float:
        """Extract numeric value from data dictionary."""
        try:
            numeric_values = [v for v in data.values() if isinstance(v, (int, float))]
            return float(np.mean(numeric_values)) if numeric_values else 0.0
        except Exception as e:
            logger.error(f"Error extracting numeric value: {str(e)}")
            return 0.0
    
    def _calculate_confidence(self, data: Dict[str, Any]) -> float:
        """Calculate confidence score for data point."""
        try:
            # Basic confidence calculation based on data completeness
            total_fields = len(data)
            valid_fields = sum(1 for v in data.values() if v is not None)
            return float(valid_fields / total_fields) if total_fields > 0 else 0.0
        except Exception as e:
            logger.error(f"Error calculating confidence: {str(e)}")
            return 0.0
    
    def _extract_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from data dictionary."""
        try:
            return {
                k: v for k, v in data.items()
                if not isinstance(v, (int, float)) and v is not None
            }
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            return {}
    
    def _generate_metadata(self) -> Dict[str, Any]:
        """Generate system metadata for synchronized data point."""
        return {
            'system_version': '1.0.0',
            'sync_window_ms': self.sync_window_ms,
            'correlation_window': self.correlation_window,
            'optimization_config': self.optimization_config
        }
    
    def _calculate_performance_metrics(self) -> Dict[str, float]:
        """Calculate performance metrics for the synchronization process."""
        return {
            'buffer_size': self._calculate_buffer_size(),
            'stream_count': len(self.data_buffer),
            'average_correlation_time': CORRELATION_TIME._sum.get() / CORRELATION_TIME._count.get() if CORRELATION_TIME._count.get() > 0 else 0.0
        }
    
    def _calculate_buffer_size(self) -> int:
        """Calculate total buffer size in bytes."""
        try:
            total_size = 0
            for stream_data in self.data_buffer.values():
                for point in stream_data:
                    total_size += len(json.dumps(point).encode('utf-8'))
            return total_size
        except Exception as e:
            logger.error(f"Error calculating buffer size: {str(e)}")
            return 0
    
    def export_data(self, 
                   filename: str,
                   format: str = 'json',
                   compression: bool = True) -> bool:
        """Export synchronized data with advanced options."""
        try:
            # Get synchronized data
            synced_data = self.synchronize_data()
            if not synced_data:
                return False
            
            # Convert to dictionary
            data_dict = asdict(synced_data)
            
            # Serialize based on format
            if format.lower() == 'json':
                data_bytes = json.dumps(data_dict).encode('utf-8')
            elif format.lower() == 'msgpack':
                data_bytes = msgpack.packb(data_dict)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            # Apply compression if enabled
            if compression and self.optimization_config['compression']['enabled']:
                data_bytes = zlib.compress(
                    data_bytes,
                    level=self.optimization_config['compression']['level']
                )
            
            # Write to file
            with open(filename, 'wb') as f:
                f.write(data_bytes)
            
            return True
        except Exception as e:
            logger.error(f"Error exporting data: {str(e)}")
            return False 