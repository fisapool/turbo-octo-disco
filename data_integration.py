import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import threading
from dataclasses import dataclass, asdict
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class DataPoint:
    source: str
    type: str
    data: Dict[str, Any]
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None

class DataIntegrationEngine:
    def __init__(self, storage_path: str = "integrated_data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        self.data_points: List[DataPoint] = []
        self.lock = threading.Lock()
        self.sources: Dict[str, Any] = {}
        
        # Initialize data storage
        self._initialize_storage()
        
        # Export configuration
        self.export_config = {
            'formats': ['json', 'csv', 'parquet', 'hdf5'],
            'compression': {
                'enabled': True,
                'level': 6,
                'algorithm': 'gzip'
            },
            'batch_size': 1000,
            'max_file_size': 100 * 1024 * 1024  # 100MB
        }

    def _initialize_storage(self):
        """Initialize the data storage structure."""
        self.storage_path.mkdir(exist_ok=True)
        (self.storage_path / "raw").mkdir(exist_ok=True)
        (self.storage_path / "processed").mkdir(exist_ok=True)

    def register_source(self, source_name: str, source_handler: Any):
        """Register a new data source with its handler."""
        with self.lock:
            self.sources[source_name] = source_handler
            logger.info(f"Registered data source: {source_name}")

    def add_data_point(self, source: str, data_type: str, data: Dict[str, Any], 
                      metadata: Optional[Dict[str, Any]] = None):
        """Add a new data point to the integration engine."""
        try:
            data_point = DataPoint(
                source=source,
                type=data_type,
                data=data,
                timestamp=datetime.now().isoformat(),
                metadata=metadata
            )
            
            with self.lock:
                self.data_points.append(data_point)
            
            # Save raw data
            self._save_raw_data(data_point)
            
            logger.info(f"Added data point from {source} of type {data_type}")
            return True
        except Exception as e:
            logger.error(f"Error adding data point: {str(e)}")
            return False

    def _save_raw_data(self, data_point: DataPoint):
        """Save raw data to storage."""
        try:
            timestamp = datetime.fromisoformat(data_point.timestamp)
            date_str = timestamp.strftime("%Y-%m-%d")
            
            # Create daily directory
            daily_dir = self.storage_path / "raw" / date_str
            daily_dir.mkdir(exist_ok=True)
            
            # Save data point
            filename = f"{data_point.source}_{data_point.type}_{timestamp.strftime('%H%M%S')}.json"
            filepath = daily_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(asdict(data_point), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving raw data: {str(e)}")

    def get_data_points(self, 
                       source: Optional[str] = None,
                       data_type: Optional[str] = None,
                       start_time: Optional[str] = None,
                       end_time: Optional[str] = None) -> List[DataPoint]:
        """Retrieve data points with optional filtering."""
        with self.lock:
            filtered_points = self.data_points.copy()
            
            if source:
                filtered_points = [p for p in filtered_points if p.source == source]
            
            if data_type:
                filtered_points = [p for p in filtered_points if p.type == data_type]
            
            if start_time:
                start_dt = datetime.fromisoformat(start_time)
                filtered_points = [p for p in filtered_points 
                                 if datetime.fromisoformat(p.timestamp) >= start_dt]
            
            if end_time:
                end_dt = datetime.fromisoformat(end_time)
                filtered_points = [p for p in filtered_points 
                                 if datetime.fromisoformat(p.timestamp) <= end_dt]
            
            return filtered_points

    def process_data(self, processor_func):
        """Process data points using a custom processor function."""
        try:
            with self.lock:
                processed_data = processor_func(self.data_points)
                return processed_data
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            return None

    def export_data(self, 
                   filename: str, 
                   source: Optional[str] = None,
                   data_type: Optional[str] = None,
                   start_time: Optional[str] = None,
                   end_time: Optional[str] = None,
                   format: str = 'json',
                   compression: bool = True,
                   batch_size: Optional[int] = None) -> bool:
        """Export filtered data points to a file with advanced options."""
        try:
            data_points = self.get_data_points(source, data_type, start_time, end_time)
            
            if not data_points:
                logger.warning("No data points to export")
                return False
            
            # Determine file format
            file_format = format.lower()
            if file_format not in self.export_config['formats']:
                logger.warning(f"Unsupported format: {format}. Using JSON instead.")
                file_format = 'json'
            
            # Prepare export data
            export_data = {
                'metadata': {
                    'export_time': datetime.now().isoformat(),
                    'filters': {
                        'source': source,
                        'data_type': data_type,
                        'start_time': start_time,
                        'end_time': end_time
                    },
                    'format': file_format,
                    'compression': compression
                },
                'data_points': [asdict(dp) for dp in data_points]
            }
            
            # Export based on format
            if file_format == 'json':
                self._export_json(filename, export_data, compression)
            elif file_format == 'csv':
                self._export_csv(filename, export_data, compression)
            elif file_format == 'parquet':
                self._export_parquet(filename, export_data, compression)
            elif file_format == 'hdf5':
                self._export_hdf5(filename, export_data, compression)
            
            logger.info(f"Exported data to {filename} in {file_format} format")
            return True
        except Exception as e:
            logger.error(f"Error exporting data: {str(e)}")
            return False
    
    def _export_json(self, filename: str, data: Dict, compression: bool):
        """Export data to JSON format."""
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            if compression:
                import gzip
                with open(filename, 'rb') as f_in:
                    with gzip.open(f"{filename}.gz", 'wb', 
                                 compresslevel=self.export_config['compression']['level']) as f_out:
                        f_out.writelines(f_in)
                Path(filename).unlink()  # Remove uncompressed file
        except Exception as e:
            logger.error(f"Error exporting JSON: {str(e)}")
            raise
    
    def _export_csv(self, filename: str, data: Dict, compression: bool):
        """Export data to CSV format."""
        try:
            import pandas as pd
            
            # Convert data points to DataFrame
            df = pd.DataFrame(data['data_points'])
            
            # Flatten nested dictionaries
            for col in df.columns:
                if isinstance(df[col].iloc[0], dict):
                    df = pd.concat([
                        df.drop(col, axis=1),
                        pd.json_normalize(df[col])
                    ], axis=1)
            
            # Save to CSV
            df.to_csv(filename, index=False)
            
            if compression:
                import gzip
                with open(filename, 'rb') as f_in:
                    with gzip.open(f"{filename}.gz", 'wb', 
                                 compresslevel=self.export_config['compression']['level']) as f_out:
                        f_out.writelines(f_in)
                Path(filename).unlink()  # Remove uncompressed file
        except Exception as e:
            logger.error(f"Error exporting CSV: {str(e)}")
            raise
    
    def _export_parquet(self, filename: str, data: Dict, compression: bool):
        """Export data to Parquet format."""
        try:
            import pandas as pd
            import pyarrow as pa
            import pyarrow.parquet as pq
            
            # Convert data points to DataFrame
            df = pd.DataFrame(data['data_points'])
            
            # Flatten nested dictionaries
            for col in df.columns:
                if isinstance(df[col].iloc[0], dict):
                    df = pd.concat([
                        df.drop(col, axis=1),
                        pd.json_normalize(df[col])
                    ], axis=1)
            
            # Convert to PyArrow Table
            table = pa.Table.from_pandas(df)
            
            # Save to Parquet
            pq.write_table(
                table,
                filename,
                compression='gzip' if compression else None,
                compression_level=self.export_config['compression']['level'] if compression else None
            )
        except Exception as e:
            logger.error(f"Error exporting Parquet: {str(e)}")
            raise
    
    def _export_hdf5(self, filename: str, data: Dict, compression: bool):
        """Export data to HDF5 format."""
        try:
            import pandas as pd
            import h5py
            
            # Convert data points to DataFrame
            df = pd.DataFrame(data['data_points'])
            
            # Flatten nested dictionaries
            for col in df.columns:
                if isinstance(df[col].iloc[0], dict):
                    df = pd.concat([
                        df.drop(col, axis=1),
                        pd.json_normalize(df[col])
                    ], axis=1)
            
            # Save to HDF5
            with h5py.File(filename, 'w') as f:
                # Create dataset with compression if enabled
                if compression:
                    f.create_dataset(
                        'data',
                        data=df.to_records(index=False),
                        compression='gzip',
                        compression_opts=self.export_config['compression']['level']
                    )
                else:
                    f.create_dataset(
                        'data',
                        data=df.to_records(index=False)
                    )
                
                # Store metadata
                metadata = f.create_group('metadata')
                for key, value in data['metadata'].items():
                    if isinstance(value, (str, int, float, bool)):
                        metadata.attrs[key] = value
                    elif isinstance(value, dict):
                        for k, v in value.items():
                            metadata.attrs[f"{key}_{k}"] = v
        except Exception as e:
            logger.error(f"Error exporting HDF5: {str(e)}")
            raise
    
    def export_batch(self, 
                    base_filename: str,
                    source: Optional[str] = None,
                    data_type: Optional[str] = None,
                    start_time: Optional[str] = None,
                    end_time: Optional[str] = None,
                    format: str = 'json',
                    compression: bool = True,
                    batch_size: Optional[int] = None) -> List[str]:
        """Export data in batches to multiple files."""
        try:
            data_points = self.get_data_points(source, data_type, start_time, end_time)
            
            if not data_points:
                logger.warning("No data points to export")
                return []
            
            batch_size = batch_size or self.export_config['batch_size']
            exported_files = []
            
            for i in range(0, len(data_points), batch_size):
                batch = data_points[i:i + batch_size]
                batch_filename = f"{base_filename}_{i//batch_size + 1}.{format}"
                
                if self.export_data(
                    batch_filename,
                    source=source,
                    data_type=data_type,
                    start_time=start_time,
                    end_time=end_time,
                    format=format,
                    compression=compression
                ):
                    exported_files.append(batch_filename)
            
            return exported_files
        except Exception as e:
            logger.error(f"Error exporting batch: {str(e)}")
            return []

    def clear_data(self):
        """Clear all stored data points."""
        with self.lock:
            self.data_points.clear()
            logger.info("Cleared all data points")

if __name__ == "__main__":
    # Example usage
    engine = DataIntegrationEngine()
    
    # Example data point
    engine.add_data_point(
        source="activity_tracker",
        data_type="keyboard_event",
        data={
            "key": "a",
            "action": "press"
        },
        metadata={
            "user_id": "user123",
            "application": "text_editor"
        }
    )
    
    # Export data
    engine.export_data("exported_data.json") 