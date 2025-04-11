from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path
from dataclasses import dataclass, asdict
from .data_integration import DataPoint, DataIntegrationEngine

logger = logging.getLogger(__name__)

@dataclass
class CorrelationResult:
    source1: str
    source2: str
    correlation_score: float
    time_window: timedelta
    metadata: Optional[Dict[str, Any]] = None

class DataProcessor:
    def __init__(self, integration_engine: DataIntegrationEngine):
        self.engine = integration_engine
        self.processed_data_path = Path("processed_data")
        self.processed_data_path.mkdir(exist_ok=True)

    def process_time_series(self, 
                          source: str,
                          data_type: str,
                          start_time: Optional[str] = None,
                          end_time: Optional[str] = None) -> Dict[str, Any]:
        """Process time series data from a specific source."""
        try:
            data_points = self.engine.get_data_points(
                source=source,
                data_type=data_type,
                start_time=start_time,
                end_time=end_time
            )
            
            if not data_points:
                return {"error": "No data points found"}
            
            # Basic time series analysis
            timestamps = [datetime.fromisoformat(dp.timestamp) for dp in data_points]
            time_diffs = [(t2 - t1).total_seconds() 
                         for t1, t2 in zip(timestamps[:-1], timestamps[1:])]
            
            result = {
                "source": source,
                "data_type": data_type,
                "total_points": len(data_points),
                "time_span": {
                    "start": timestamps[0].isoformat(),
                    "end": timestamps[-1].isoformat(),
                    "duration_seconds": (timestamps[-1] - timestamps[0]).total_seconds()
                },
                "statistics": {
                    "avg_time_between_points": sum(time_diffs) / len(time_diffs) if time_diffs else 0,
                    "min_time_between_points": min(time_diffs) if time_diffs else 0,
                    "max_time_between_points": max(time_diffs) if time_diffs else 0
                }
            }
            
            return result
        except Exception as e:
            logger.error(f"Error processing time series: {str(e)}")
            return {"error": str(e)}

    def correlate_sources(self,
                         source1: str,
                         source2: str,
                         time_window: timedelta = timedelta(seconds=1)) -> CorrelationResult:
        """Correlate data between two sources within a time window."""
        try:
            # Get data points from both sources
            points1 = self.engine.get_data_points(source=source1)
            points2 = self.engine.get_data_points(source=source2)
            
            if not points1 or not points2:
                return CorrelationResult(
                    source1=source1,
                    source2=source2,
                    correlation_score=0.0,
                    time_window=time_window,
                    metadata={"error": "Insufficient data points"}
                )
            
            # Calculate correlation
            correlation_score = self._calculate_correlation(points1, points2, time_window)
            
            return CorrelationResult(
                source1=source1,
                source2=source2,
                correlation_score=correlation_score,
                time_window=time_window,
                metadata={
                    "points_count": {
                        source1: len(points1),
                        source2: len(points2)
                    }
                }
            )
        except Exception as e:
            logger.error(f"Error correlating sources: {str(e)}")
            return CorrelationResult(
                source1=source1,
                source2=source2,
                correlation_score=0.0,
                time_window=time_window,
                metadata={"error": str(e)}
            )

    def _calculate_correlation(self, 
                             points1: List[DataPoint],
                             points2: List[DataPoint],
                             time_window: timedelta) -> float:
        """Calculate correlation score between two sets of data points."""
        # Simple correlation based on temporal proximity
        matches = 0
        total_checks = 0
        
        for p1 in points1:
            p1_time = datetime.fromisoformat(p1.timestamp)
            
            for p2 in points2:
                p2_time = datetime.fromisoformat(p2.timestamp)
                time_diff = abs(p1_time - p2_time)
                
                if time_diff <= time_window:
                    matches += 1
                total_checks += 1
        
        return matches / total_checks if total_checks > 0 else 0.0

    def generate_report(self,
                       sources: List[str],
                       start_time: Optional[str] = None,
                       end_time: Optional[str] = None) -> Dict[str, Any]:
        """Generate a comprehensive report of data processing results."""
        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "time_range": {
                    "start": start_time,
                    "end": end_time
                },
                "sources": {},
                "correlations": []
            }
            
            # Process each source
            for source in sources:
                source_data = self.process_time_series(
                    source=source,
                    start_time=start_time,
                    end_time=end_time
                )
                report["sources"][source] = source_data
            
            # Calculate correlations between sources
            for i, source1 in enumerate(sources):
                for source2 in sources[i+1:]:
                    correlation = self.correlate_sources(source1, source2)
                    report["correlations"].append(asdict(correlation))
            
            return report
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return {"error": str(e)}

    def save_processed_data(self, data: Dict[str, Any], filename: str):
        """Save processed data to a file."""
        try:
            filepath = self.processed_data_path / filename
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved processed data to {filepath}")
        except Exception as e:
            logger.error(f"Error saving processed data: {str(e)}")

if __name__ == "__main__":
    # Example usage
    engine = DataIntegrationEngine()
    processor = DataProcessor(engine)
    
    # Process time series data
    time_series_result = processor.process_time_series(
        source="activity_tracker",
        data_type="keyboard_event"
    )
    
    # Generate report
    report = processor.generate_report(
        sources=["activity_tracker", "webcam"],
        start_time=(datetime.now() - timedelta(hours=1)).isoformat(),
        end_time=datetime.now().isoformat()
    )
    
    # Save processed data
    processor.save_processed_data(report, "processing_report.json") 