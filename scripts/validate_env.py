#!/usr/bin/env python3
"""
Environment variable validation script.
This script checks for required environment variables and validates their values.
"""

import os
import sys
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class EnvironmentValidator:
    def __init__(self):
        self.required_vars = {
            # Critical Production Settings
            "SECRET_KEY": {
                "description": "Application secret key",
                "validation": lambda x: len(x) >= 32,
                "error_msg": "SECRET_KEY must be at least 32 characters long"
            },
            
            # Database Configuration
            "DATABASE_URL": {
                "description": "Database connection URL",
                "validation": lambda x: x.startswith(("sqlite:///", "postgresql://")),
                "error_msg": "DATABASE_URL must start with sqlite:/// or postgresql://"
            },
            
            # Cache Configuration
            "REDIS_URL": {
                "description": "Redis connection URL",
                "validation": lambda x: x.startswith("redis://"),
                "error_msg": "REDIS_URL must start with redis://"
            },
            
            # Application Settings
            "FLASK_ENV": {
                "description": "Flask environment",
                "validation": lambda x: x in ["development", "production", "testing"],
                "error_msg": "FLASK_ENV must be one of: development, production, testing"
            },
            "PORT": {
                "description": "Application port",
                "validation": lambda x: x.isdigit() and 1 <= int(x) <= 65535,
                "error_msg": "PORT must be a number between 1 and 65535"
            },
            "HOST": {
                "description": "Application host",
                "validation": lambda x: x in ["0.0.0.0", "127.0.0.1", "localhost"],
                "error_msg": "HOST must be one of: 0.0.0.0, 127.0.0.1, localhost"
            }
        }
        
        self.optional_vars = {
            # Analytics
            "ANALYTICS_ID": {
                "description": "Analytics service ID",
                "validation": lambda x: len(x) > 0 if x else True,
                "error_msg": "ANALYTICS_ID cannot be empty if provided"
            },
            
            # Error Tracking
            "ERROR_TRACKING_DSN": {
                "description": "Error tracking service DSN",
                "validation": lambda x: len(x) > 0 if x else True,
                "error_msg": "ERROR_TRACKING_DSN cannot be empty if provided"
            }
        }

    def validate_variable(self, var_name: str, var_config: Dict) -> Optional[str]:
        """Validate a single environment variable."""
        value = os.getenv(var_name)
        
        if value is None and var_name in self.required_vars:
            return f"Missing required environment variable: {var_name}"
            
        if value is not None and not var_config["validation"](value):
            return f"Invalid value for {var_name}: {var_config['error_msg']}"
            
        return None

    def validate_all(self) -> List[str]:
        """Validate all environment variables."""
        errors = []
        
        # Validate required variables
        for var_name, var_config in self.required_vars.items():
            error = self.validate_variable(var_name, var_config)
            if error:
                errors.append(error)
                
        # Validate optional variables if they exist
        for var_name, var_config in self.optional_vars.items():
            if os.getenv(var_name):
                error = self.validate_variable(var_name, var_config)
                if error:
                    errors.append(error)
                    
        return errors

    def print_validation_report(self, errors: List[str]) -> None:
        """Print validation results."""
        if not errors:
            print("✅ All environment variables are valid!")
            return
            
        print("❌ Environment validation failed:")
        for error in errors:
            print(f"  - {error}")
            
        print("\nRequired environment variables:")
        for var_name, var_config in self.required_vars.items():
            print(f"  - {var_name}: {var_config['description']}")
            
        print("\nOptional environment variables:")
        for var_name, var_config in self.optional_vars.items():
            print(f"  - {var_name}: {var_config['description']}")

def main():
    validator = EnvironmentValidator()
    errors = validator.validate_all()
    validator.print_validation_report(errors)
    
    if errors:
        sys.exit(1)

if __name__ == "__main__":
    main() 