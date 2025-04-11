from prometheus_client import start_http_server
import logging
from pathlib import Path
import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MonitoringConfig:
    def __init__(self, config_path: str = "monitoring_config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
    def _load_config(self) -> dict:
        """Load monitoring configuration from YAML file."""
        try:
            if not self.config_path.exists():
                # Create default configuration
                default_config = {
                    'prometheus': {
                        'port': 9090,
                        'metrics_path': '/metrics'
                    },
                    'grafana': {
                        'enabled': True,
                        'dashboard_path': 'grafana/dashboards'
                    },
                    'alerts': {
                        'enabled': True,
                        'thresholds': {
                            'cpu_usage': 80.0,
                            'memory_usage': 80.0,
                            'disk_usage': 80.0,
                            'response_time': 1000.0  # ms
                        }
                    },
                    'retention': {
                        'data_days': 30,
                        'logs_days': 7
                    }
                }
                
                # Save default configuration
                with open(self.config_path, 'w') as f:
                    yaml.dump(default_config, f, default_flow_style=False)
                
                logger.info(f"Created default monitoring configuration at {self.config_path}")
                return default_config
            
            # Load existing configuration
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            logger.info(f"Loaded monitoring configuration from {self.config_path}")
            return config
            
        except Exception as e:
            logger.error(f"Error loading monitoring configuration: {str(e)}")
            return {}
    
    def start_monitoring(self):
        """Start the monitoring server."""
        try:
            port = self.config.get('prometheus', {}).get('port', 9090)
            start_http_server(port)
            logger.info(f"Started monitoring server on port {port}")
        except Exception as e:
            logger.error(f"Error starting monitoring server: {str(e)}")
    
    def get_alert_thresholds(self) -> dict:
        """Get alert thresholds from configuration."""
        return self.config.get('alerts', {}).get('thresholds', {})
    
    def get_retention_periods(self) -> dict:
        """Get data retention periods from configuration."""
        return self.config.get('retention', {})
    
    def is_grafana_enabled(self) -> bool:
        """Check if Grafana integration is enabled."""
        return self.config.get('grafana', {}).get('enabled', False)
    
    def get_grafana_dashboard_path(self) -> str:
        """Get Grafana dashboard path."""
        return self.config.get('grafana', {}).get('dashboard_path', 'grafana/dashboards')

if __name__ == "__main__":
    # Example usage
    config = MonitoringConfig()
    config.start_monitoring()
    
    # Print configuration
    print("Alert Thresholds:", config.get_alert_thresholds())
    print("Retention Periods:", config.get_retention_periods())
    print("Grafana Enabled:", config.is_grafana_enabled())
    print("Grafana Dashboard Path:", config.get_grafana_dashboard_path()) 