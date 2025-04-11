"""
Advanced security module implementing encryption, RBAC, audit trail, and security monitoring.
"""

import os
import json
import logging
import hashlib
import hmac
import base64
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import jwt
from functools import wraps
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)

class SecurityManager:
    """Main security manager class handling encryption, RBAC, audit trails, and monitoring."""
    
    def __init__(self, config_path: str = "config/security_config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.encryption_key = self._generate_encryption_key()
        self.fernet = Fernet(self.encryption_key)
        self.roles = self._load_roles()
        self.audit_log = AuditLog()
        self.security_monitor = SecurityMonitor()
        self._lock = threading.Lock()
        
    def _load_config(self) -> Dict:
        """Load security configuration from file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading security config: {str(e)}")
            return self._get_default_config()
            
    def _get_default_config(self) -> Dict:
        """Return default security configuration."""
        return {
            "encryption": {
                "algorithm": "AES-256-GCM",
                "key_rotation_days": 90,
                "salt_length": 32
            },
            "rbac": {
                "default_role": "user",
                "admin_role": "admin"
            },
            "audit": {
                "retention_days": 365,
                "log_level": "INFO"
            },
            "monitoring": {
                "alert_thresholds": {
                    "failed_logins": 5,
                    "suspicious_activity": 3
                }
            }
        }
        
    def _generate_encryption_key(self) -> bytes:
        """Generate a secure encryption key."""
        salt = os.urandom(32)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(os.urandom(32)))
        
    def _load_roles(self) -> Dict[str, Set[str]]:
        """Load role definitions and permissions."""
        roles_path = Path("config/roles.json")
        if roles_path.exists():
            with open(roles_path, 'r') as f:
                return json.load(f)
        return self._get_default_roles()
        
    def _get_default_roles(self) -> Dict[str, Set[str]]:
        """Return default role definitions."""
        return {
            "admin": {
                "read:*",
                "write:*",
                "delete:*",
                "manage_users",
                "manage_roles",
                "view_audit_logs"
            },
            "manager": {
                "read:*",
                "write:reports",
                "view_analytics",
                "manage_team"
            },
            "user": {
                "read:own_data",
                "write:own_data",
                "view_own_reports"
            }
        }
        
    def encrypt_data(self, data: str) -> str:
        """Encrypt data using AES-256-GCM."""
        try:
            with self._lock:
                iv = os.urandom(12)
                cipher = Cipher(
                    algorithms.AES(self.encryption_key),
                    modes.GCM(iv),
                    backend=default_backend()
                )
                encryptor = cipher.encryptor()
                ciphertext = encryptor.update(data.encode()) + encryptor.finalize()
                return base64.b64encode(iv + encryptor.tag + ciphertext).decode()
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            raise
            
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data using AES-256-GCM."""
        try:
            with self._lock:
                data = base64.b64decode(encrypted_data)
                iv = data[:12]
                tag = data[12:28]
                ciphertext = data[28:]
                cipher = Cipher(
                    algorithms.AES(self.encryption_key),
                    modes.GCM(iv, tag),
                    backend=default_backend()
                )
                decryptor = cipher.decryptor()
                return decryptor.update(ciphertext) + decryptor.finalize()
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            raise
            
    def check_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has specific permission."""
        user_roles = self._get_user_roles(user_id)
        for role in user_roles:
            if permission in self.roles.get(role, set()):
                return True
        return False
        
    def _get_user_roles(self, user_id: str) -> Set[str]:
        """Get roles assigned to a user."""
        # TODO: Implement user-role mapping from database
        return {"user"}  # Default role
        
    def log_audit_event(self, event_type: str, user_id: str, details: Dict):
        """Log security audit event."""
        self.audit_log.log_event(event_type, user_id, details)
        
    def monitor_security_event(self, event_type: str, user_id: str, details: Dict):
        """Monitor and analyze security events."""
        self.security_monitor.process_event(event_type, user_id, details)
        
    def generate_security_report(self) -> Dict:
        """Generate security status report."""
        return {
            "audit_summary": self.audit_log.get_summary(),
            "security_alerts": self.security_monitor.get_alerts(),
            "encryption_status": self._get_encryption_status(),
            "permission_audit": self._audit_permissions()
        }
        
    def _get_encryption_status(self) -> Dict:
        """Get encryption system status."""
        return {
            "algorithm": self.config["encryption"]["algorithm"],
            "key_age_days": self._get_key_age_days(),
            "last_rotation": self._get_last_key_rotation()
        }
        
    def _get_key_age_days(self) -> int:
        """Calculate age of current encryption key in days."""
        # TODO: Implement key age tracking
        return 0
        
    def _get_last_key_rotation(self) -> str:
        """Get timestamp of last key rotation."""
        # TODO: Implement key rotation tracking
        return datetime.now().isoformat()
        
    def _audit_permissions(self) -> Dict:
        """Audit current permission assignments."""
        # TODO: Implement comprehensive permission audit
        return {
            "total_roles": len(self.roles),
            "total_permissions": sum(len(perms) for perms in self.roles.values())
        }

class AuditLog:
    """Handles security audit logging."""
    
    def __init__(self, log_dir: str = "logs/audit"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        
    def log_event(self, event_type: str, user_id: str, details: Dict):
        """Log an audit event."""
        try:
            with self._lock:
                event = {
                    "timestamp": datetime.now().isoformat(),
                    "event_type": event_type,
                    "user_id": user_id,
                    "details": details
                }
                
                log_file = self.log_dir / f"audit_{datetime.now().strftime('%Y-%m-%d')}.log"
                with open(log_file, 'a') as f:
                    f.write(json.dumps(event) + '\n')
                    
        except Exception as e:
            logger.error(f"Error logging audit event: {str(e)}")
            
    def get_summary(self) -> Dict:
        """Get summary of recent audit events."""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            log_file = self.log_dir / f"audit_{today}.log"
            
            if not log_file.exists():
                return {"total_events": 0, "event_types": {}}
                
            event_types = defaultdict(int)
            total_events = 0
            
            with open(log_file, 'r') as f:
                for line in f:
                    event = json.loads(line)
                    event_types[event["event_type"]] += 1
                    total_events += 1
                    
            return {
                "total_events": total_events,
                "event_types": dict(event_types)
            }
        except Exception as e:
            logger.error(f"Error getting audit summary: {str(e)}")
            return {"error": str(e)}

class SecurityMonitor:
    """Monitors and analyzes security events."""
    
    def __init__(self):
        self.alert_thresholds = {
            "failed_logins": 5,
            "suspicious_activity": 3
        }
        self.event_counts = defaultdict(int)
        self.alerts = []
        self._lock = threading.Lock()
        
    def process_event(self, event_type: str, user_id: str, details: Dict):
        """Process and analyze security event."""
        try:
            with self._lock:
                self.event_counts[event_type] += 1
                
                # Check for threshold violations
                if self.event_counts[event_type] >= self.alert_thresholds.get(event_type, float('inf')):
                    self._generate_alert(event_type, user_id, details)
                    
        except Exception as e:
            logger.error(f"Error processing security event: {str(e)}")
            
    def _generate_alert(self, event_type: str, user_id: str, details: Dict):
        """Generate security alert."""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "details": details,
            "severity": self._determine_severity(event_type)
        }
        self.alerts.append(alert)
        
    def _determine_severity(self, event_type: str) -> str:
        """Determine alert severity based on event type."""
        severity_map = {
            "failed_logins": "high",
            "suspicious_activity": "medium",
            "permission_change": "low"
        }
        return severity_map.get(event_type, "low")
        
    def get_alerts(self) -> List[Dict]:
        """Get current security alerts."""
        with self._lock:
            return self.alerts.copy()
            
    def clear_alerts(self):
        """Clear processed alerts."""
        with self._lock:
            self.alerts = []
            
    def get_event_stats(self) -> Dict:
        """Get statistics about security events."""
        with self._lock:
            return {
                "total_events": sum(self.event_counts.values()),
                "event_counts": dict(self.event_counts),
                "active_alerts": len(self.alerts)
            }

def require_permission(permission: str):
    """Decorator for requiring specific permission."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # TODO: Implement permission check
            return func(*args, **kwargs)
        return wrapper
    return decorator

def log_security_event(event_type: str):
    """Decorator for logging security events."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # TODO: Implement event logging
            return func(*args, **kwargs)
        return wrapper
    return decorator 