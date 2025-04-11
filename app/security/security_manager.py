"""
Advanced Security Management Module

This module provides comprehensive security features including:
- Advanced encryption methods
- Role-based access control
- Audit trail system
- Security monitoring
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union
from pathlib import Path
import hashlib
import hmac
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import jwt
from functools import wraps

logger = logging.getLogger(__name__)

class SecurityManager:
    def __init__(self, config_path: str = "config/security_config.json"):
        self.config = self._load_config(config_path)
        self.encryption_key = self._generate_encryption_key()
        self.audit_log_path = Path("logs/security/audit.log")
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        
    def _load_config(self, path: str) -> Dict:
        """Load security configuration from file."""
        try:
            with open(path) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error loading security config: {str(e)}")
            return self._get_default_config()
            
    def _get_default_config(self) -> Dict:
        """Get default security configuration."""
        return {
            "encryption": {
                "algorithm": "AES-256-GCM",
                "key_rotation_days": 90,
                "salt_length": 32
            },
            "rbac": {
                "roles": {
                    "admin": ["*"],
                    "manager": ["read", "write"],
                    "user": ["read"]
                }
            },
            "audit": {
                "retention_days": 365,
                "log_levels": ["INFO", "WARNING", "ERROR", "CRITICAL"]
            },
            "monitoring": {
                "failed_login_threshold": 5,
                "session_timeout_minutes": 30,
                "password_policy": {
                    "min_length": 12,
                    "require_uppercase": True,
                    "require_lowercase": True,
                    "require_numbers": True,
                    "require_special": True
                }
            }
        }
        
    def _generate_encryption_key(self) -> bytes:
        """Generate a secure encryption key using PBKDF2."""
        salt = os.urandom(32)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(os.urandom(32)))
        
    def encrypt_data(self, data: Union[str, bytes]) -> Dict[str, Union[str, bytes]]:
        """Encrypt data using AES-256-GCM."""
        if isinstance(data, str):
            data = data.encode()
            
        iv = os.urandom(12)
        cipher = Cipher(
            algorithms.AES(self.encryption_key),
            modes.GCM(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        return {
            "ciphertext": base64.b64encode(ciphertext),
            "iv": base64.b64encode(iv),
            "tag": base64.b64encode(encryptor.tag)
        }
        
    def decrypt_data(self, encrypted_data: Dict[str, Union[str, bytes]]) -> bytes:
        """Decrypt data using AES-256-GCM."""
        ciphertext = base64.b64decode(encrypted_data["ciphertext"])
        iv = base64.b64decode(encrypted_data["iv"])
        tag = base64.b64decode(encrypted_data["tag"])
        
        cipher = Cipher(
            algorithms.AES(self.encryption_key),
            modes.GCM(iv, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        
        return decryptor.update(ciphertext) + decryptor.finalize()
        
    def check_permission(self, user_role: str, required_permission: str) -> bool:
        """Check if a user role has the required permission."""
        roles = self.config["rbac"]["roles"]
        if user_role not in roles:
            return False
            
        user_permissions = roles[user_role]
        return "*" in user_permissions or required_permission in user_permissions
        
    def log_audit_event(
        self,
        event_type: str,
        user_id: str,
        details: Dict,
        severity: str = "INFO"
    ) -> None:
        """Log security audit event."""
        if severity not in self.config["audit"]["log_levels"]:
            return
            
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "details": details,
            "severity": severity
        }
        
        with open(self.audit_log_path, "a") as f:
            f.write(json.dumps(event) + "\n")
            
    def monitor_security_event(self, event_type: str, details: Dict) -> None:
        """Monitor and analyze security events."""
        if event_type == "failed_login":
            user_id = details.get("user_id")
            if self._check_failed_login_threshold(user_id):
                self.log_audit_event(
                    "suspicious_activity",
                    user_id,
                    details,
                    "WARNING"
                )
                
    def _check_failed_login_threshold(self, user_id: str) -> bool:
        """Check if failed login attempts exceed threshold."""
        # Implement failed login tracking logic
        return False
        
    def generate_jwt_token(self, user_id: str, roles: List[str]) -> str:
        """Generate JWT token for authentication."""
        payload = {
            "user_id": user_id,
            "roles": roles,
            "exp": datetime.now().timestamp() + 3600  # 1 hour expiration
        }
        return jwt.encode(
            payload,
            self.encryption_key,
            algorithm="HS256"
        )
        
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return payload if valid."""
        try:
            return jwt.decode(
                token,
                self.encryption_key,
                algorithms=["HS256"]
            )
        except jwt.PyJWTError:
            return None
            
    def hash_password(self, password: str) -> str:
        """Hash password using PBKDF2."""
        salt = os.urandom(32)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.b64encode(kdf.derive(password.encode()))
        return f"{base64.b64encode(salt).decode()}:{key.decode()}"
        
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hashed password."""
        salt, key = hashed_password.split(":")
        salt = base64.b64decode(salt)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return hmac.compare_digest(
            base64.b64encode(kdf.derive(password.encode())).decode(),
            key
        )
        
    def validate_password_policy(self, password: str) -> bool:
        """Validate password against security policy."""
        policy = self.config["monitoring"]["password_policy"]
        
        if len(password) < policy["min_length"]:
            return False
            
        if policy["require_uppercase"] and not any(c.isupper() for c in password):
            return False
            
        if policy["require_lowercase"] and not any(c.islower() for c in password):
            return False
            
        if policy["require_numbers"] and not any(c.isdigit() for c in password):
            return False
            
        if policy["require_special"] and not any(not c.isalnum() for c in password):
            return False
            
        return True 