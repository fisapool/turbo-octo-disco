import json
import time
import logging
from webcam_integration import WebcamIntegration
from hid_system_integration import HIDSystemIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MultimodalIntegration:
    def __init__(self, config_path='config.json'):
        self.config = self._load_config(config_path)
        self.webcam = WebcamIntegration(config_path)
        self.hid_system = HIDSystemIntegration(config_path)
        self.is_running = False
        
    def _load_config(self, config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            raise
            
    def start(self):
        """Start both webcam and HID system monitoring"""
        if self.is_running:
            return
            
        try:
            logger.info("Starting multimodal integration...")
            
            # Start webcam integration
            self.webcam.start()
            logger.info("Webcam integration started")
            
            # Start HID system integration
            self.hid_system.start()
            logger.info("HID system integration started")
            
            self.is_running = True
            logger.info("Multimodal integration started successfully")
            
        except Exception as e:
            logger.error(f"Error starting multimodal integration: {e}")
            self.stop()
            raise
            
    def stop(self):
        """Stop both webcam and HID system monitoring"""
        if not self.is_running:
            return
            
        try:
            logger.info("Stopping multimodal integration...")
            
            # Stop webcam integration
            self.webcam.stop()
            logger.info("Webcam integration stopped")
            
            # Stop HID system integration
            self.hid_system.stop()
            logger.info("HID system integration stopped")
            
            self.is_running = False
            logger.info("Multimodal integration stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping multimodal integration: {e}")
            raise

def main():
    try:
        # Initialize and start the multimodal integration
        integration = MultimodalIntegration()
        integration.start()
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, stopping...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        integration.stop()

if __name__ == "__main__":
    main() 