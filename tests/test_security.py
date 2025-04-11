"""
Tests for the security module.
"""

import unittest
import json
import os
from pathlib import Path
from app.core.security import SecurityManager, AuditLog, SecurityMonitor

class TestSecurityManager(unittest.TestCase):
    def setUp(self):
        self.security_manager = SecurityManager()
        self.test_data = "This is a test message"
        
    def test_encryption_decryption(self):
        """Test that data can be encrypted and decrypted correctly."""
        encrypted = self.security_manager.encrypt_data(self.test_data)
        decrypted = self.security_manager.decrypt_data(encrypted)
        self.assertEqual(decrypted, self.test_data)
        
    def test_permission_checking(self):
        """Test role-based permission checking."""
        # Test admin permissions
        self.assertTrue(self.security_manager.check_permission("admin", "read:*"))
        self.assertTrue(self.security_manager.check_permission("admin", "write:*"))
        
        # Test user permissions
        self.assertTrue(self.security_manager.check_permission("user", "read:own_data"))
        self.assertFalse(self.security_manager.check_permission("user", "read:*"))
        
    def test_audit_logging(self):
        """Test audit logging functionality."""
        event_type = "test_event"
        user_id = "test_user"
        details = {"action": "test_action"}
        
        self.security_manager.log_audit_event(event_type, user_id, details)
        
        # Verify log file was created
        log_dir = Path("logs/audit")
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = log_dir / f"audit_{today}.log"
        self.assertTrue(log_file.exists())
        
        # Verify log content
        with open(log_file, 'r') as f:
            last_line = f.readlines()[-1]
            log_entry = json.loads(last_line)
            self.assertEqual(log_entry["event_type"], event_type)
            self.assertEqual(log_entry["user_id"], user_id)
            self.assertEqual(log_entry["details"], details)
            
    def test_security_monitoring(self):
        """Test security monitoring functionality."""
        event_type = "failed_logins"
        user_id = "test_user"
        details = {"attempts": 3}
        
        # Process multiple events to trigger alert
        for _ in range(6):  # Threshold is 5
            self.security_manager.monitor_security_event(event_type, user_id, details)
            
        # Verify alert was generated
        alerts = self.security_manager.security_monitor.get_alerts()
        self.assertTrue(len(alerts) > 0)
        self.assertEqual(alerts[0]["event_type"], event_type)
        self.assertEqual(alerts[0]["user_id"], user_id)
        
    def test_security_report(self):
        """Test security report generation."""
        report = self.security_manager.generate_security_report()
        
        # Verify report structure
        self.assertIn("audit_summary", report)
        self.assertIn("security_alerts", report)
        self.assertIn("encryption_status", report)
        self.assertIn("permission_audit", report)
        
        # Verify encryption status
        self.assertEqual(
            report["encryption_status"]["algorithm"],
            self.security_manager.config["encryption"]["algorithm"]
        )
        
    def test_require_permission_decorator(self):
        """Test the require_permission decorator."""
        @require_permission("read:data")
        def test_function():
            return "success"
            
        # TODO: Implement actual permission check in decorator
        result = test_function()
        self.assertEqual(result, "success")
        
    def test_log_security_event_decorator(self):
        """Test the log_security_event decorator."""
        @log_security_event("test_event")
        def test_function():
            return "success"
            
        # TODO: Implement actual event logging in decorator
        result = test_function()
        self.assertEqual(result, "success")
        
    def tearDown(self):
        # Clean up test files
        log_dir = Path("logs/audit")
        if log_dir.exists():
            for file in log_dir.glob("*.log"):
                file.unlink()
            log_dir.rmdir()

if __name__ == '__main__':
    unittest.main() 