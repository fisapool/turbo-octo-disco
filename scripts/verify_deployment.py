#!/usr/bin/env python3
"""
Deployment Verification Script

This script runs the deployment verification process to ensure all components
are properly configured before launch.
"""

import os
import sys
import logging
from pathlib import Path
from deployment_verifier import DeploymentVerifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('deployment_verification.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main function to run deployment verification."""
    try:
        # Get configuration path
        config_path = Path('config/deployment_config.yaml')
        if not config_path.exists():
            logger.error(f"Configuration file not found: {config_path}")
            sys.exit(1)

        # Initialize verifier
        verifier = DeploymentVerifier(config_path)
        
        # Run verification
        logger.info("Starting deployment verification...")
        result = verifier.verify_all()
        
        # Generate report
        report_path = verifier.generate_report(result)
        logger.info(f"Verification report generated: {report_path}")
        
        # Check results
        if result.failed > 0:
            logger.error(f"Deployment verification failed with {result.failed} errors")
            sys.exit(1)
        else:
            logger.info("Deployment verification completed successfully")
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Error during deployment verification: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 