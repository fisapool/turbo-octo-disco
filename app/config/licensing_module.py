#!/usr/bin/env python3
"""
Hardware-bound License Management

Features:
- Generates hardware fingerprint
- Validates license keys
- Online activation checks
- Grace period handling
"""

import hashlib
import uuid
import json
import requests
import time
from datetime import datetime, timedelta

class LicenseManager:
    def __init__(self, config_path="config.json"):
        self.config = self._load_config(config_path)
        self.grace_period = 7  # Days
        self.activation_url = self.config.get("license", {}).get("validation_url", "")
        
    def _load_config(self, path):
        try:
            with open(path) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def get_hardware_fingerprint(self):
        """Generate unique hardware fingerprint"""
        components = [
            str(uuid.getnode()),  # MAC address
            # Add other hardware identifiers as needed
        ]
        fingerprint = hashlib.sha256("".join(components).encode()).hexdigest()
        return fingerprint

    def validate_license(self, license_key):
        """Validate license key against hardware fingerprint"""
        if not license_key:
            return False
            
        # Online validation
        if self.activation_url:
            try:
                response = requests.post(
                    self.activation_url,
                    json={
                        "license_key": license_key,
                        "fingerprint": self.get_hardware_fingerprint()
                    },
                    timeout=5
                )
                return response.status_code == 200
            except requests.RequestException:
                return False
        # Offline validation fallback
        return license_key.startswith("LIC-") and len(license_key) == 20

    def check_grace_period(self, first_run_file=".first_run"):
        """Check if still within grace period"""
        try:
            with open(first_run_file) as f:
                first_run = datetime.fromisoformat(f.read())
                return datetime.now() < first_run + timedelta(days=self.grace_period)
        except FileNotFoundError:
            with open(first_run_file, "w") as f:
                f.write(datetime.now().isoformat())
            return True

    def is_licensed(self):
        """Check if system is properly licensed"""
        license_key = self.config.get("license", {}).get("key", "")
        return self.validate_license(license_key) or self.check_grace_period()

if __name__ == "__main__":
    # Test the license manager
    manager = LicenseManager()
    print(f"Hardware Fingerprint: {manager.get_hardware_fingerprint()}")
    print(f"License Valid: {manager.is_licensed()}")
