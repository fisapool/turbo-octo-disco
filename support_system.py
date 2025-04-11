import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path
from dataclasses import dataclass, asdict
import requests
from prometheus_client import Counter, Histogram, Gauge
import yaml
import hashlib
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prometheus metrics
TICKET_CREATED = Counter('support_tickets_created_total', 'Total number of support tickets created')
TICKET_RESOLVED = Counter('support_tickets_resolved_total', 'Total number of support tickets resolved')
TICKET_RESPONSE_TIME = Histogram('ticket_response_time_seconds', 'Time taken to respond to tickets')
TICKET_AGE = Gauge('ticket_age_seconds', 'Age of open tickets in seconds')
TICKET_PRIORITY = Counter('ticket_priority_total', 'Number of tickets by priority', ['priority'])
TICKET_STATUS = Counter('ticket_status_total', 'Number of tickets by status', ['status'])

@dataclass
class SupportTicket:
    ticket_id: str
    user_id: str
    subject: str
    description: str
    priority: str
    status: str
    created_at: str
    updated_at: str
    assigned_to: Optional[str]
    resolution: Optional[str]
    metadata: Optional[Dict[str, Any]] = None
    compliance_tags: Optional[List[str]] = None

class SupportSystem:
    def __init__(self, api_key: str, api_url: str, storage_path: str = "support_tickets"):
        self.api_key = api_key
        self.api_url = api_url
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.alert_thresholds = self._load_alert_thresholds()
        self.compliance_rules = self._load_compliance_rules()
        
    def _load_alert_thresholds(self) -> Dict[str, Any]:
        """Load alert thresholds from configuration."""
        try:
            config_path = Path("config/alert_thresholds.yaml")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            return {
                "response_time": 3600,  # 1 hour
                "resolution_time": 86400,  # 24 hours
                "high_priority_age": 7200,  # 2 hours
                "ticket_volume": 100  # per hour
            }
        except Exception as e:
            logger.error(f"Error loading alert thresholds: {str(e)}")
            return {}
    
    def _load_compliance_rules(self) -> Dict[str, Any]:
        """Load compliance rules from configuration."""
        try:
            config_path = Path("config/compliance_rules.yaml")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            return {
                "data_retention": 365,  # days
                "audit_log_retention": 730,  # days
                "required_fields": ["user_id", "subject", "description"],
                "sensitive_data": ["password", "token", "key"]
            }
        except Exception as e:
            logger.error(f"Error loading compliance rules: {str(e)}")
            return {}
        
    def create_ticket(self, user_id: str, subject: str, description: str, priority: str = "medium") -> Optional[SupportTicket]:
        """Create a new support ticket."""
        try:
            # Generate ticket ID
            ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Validate compliance
            if not self._validate_compliance(user_id, subject, description):
                logger.error("Ticket creation failed compliance validation")
                return None
            
            # Create ticket object
            ticket = SupportTicket(
                ticket_id=ticket_id,
                user_id=user_id,
                subject=subject,
                description=description,
                priority=priority,
                status="open",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                assigned_to=None,
                resolution=None,
                metadata=self._generate_metadata(),
                compliance_tags=self._generate_compliance_tags(subject, description)
            )
            
            # Save ticket locally
            self._save_ticket(ticket)
            
            # Send to support system API
            response = self._send_to_api(ticket)
            if not response:
                logger.error(f"Failed to send ticket {ticket_id} to support system")
                return None
            
            # Update metrics
            TICKET_CREATED.inc()
            TICKET_PRIORITY.labels(priority=priority).inc()
            TICKET_STATUS.labels(status="open").inc()
            TICKET_AGE.set(0)
            
            # Check for alerts
            self._check_alerts()
            
            logger.info(f"Created support ticket {ticket_id}")
            return ticket
            
        except Exception as e:
            logger.error(f"Error creating support ticket: {str(e)}")
            return None
    
    def update_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing support ticket."""
        try:
            # Load ticket
            ticket = self._load_ticket(ticket_id)
            if not ticket:
                logger.error(f"Ticket {ticket_id} not found")
                return False
            
            # Validate compliance for updates
            if not self._validate_compliance_updates(updates):
                logger.error("Ticket update failed compliance validation")
                return False
            
            # Update fields
            for key, value in updates.items():
                if hasattr(ticket, key):
                    setattr(ticket, key, value)
            
            ticket.updated_at = datetime.now().isoformat()
            
            # Save updated ticket
            self._save_ticket(ticket)
            
            # Send update to API
            response = self._send_to_api(ticket)
            if not response:
                logger.error(f"Failed to update ticket {ticket_id} in support system")
                return False
            
            # Update metrics
            if updates.get('status') == 'resolved':
                TICKET_RESOLVED.inc()
                TICKET_STATUS.labels(status="resolved").inc()
                TICKET_AGE.set(0)
            elif 'status' in updates:
                TICKET_STATUS.labels(status=updates['status']).inc()
            
            # Check for alerts
            self._check_alerts()
            
            logger.info(f"Updated support ticket {ticket_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating support ticket: {str(e)}")
            return False
    
    def get_ticket(self, ticket_id: str) -> Optional[SupportTicket]:
        """Get a support ticket by ID."""
        try:
            return self._load_ticket(ticket_id)
        except Exception as e:
            logger.error(f"Error getting support ticket: {str(e)}")
            return None
    
    def get_user_tickets(self, user_id: str) -> List[SupportTicket]:
        """Get all tickets for a user."""
        try:
            tickets = []
            for ticket_file in self.storage_path.glob("*.json"):
                with open(ticket_file, 'r') as f:
                    ticket_data = json.load(f)
                    if ticket_data['user_id'] == user_id:
                        tickets.append(SupportTicket(**ticket_data))
            return tickets
        except Exception as e:
            logger.error(f"Error getting user tickets: {str(e)}")
            return []
    
    def _save_ticket(self, ticket: SupportTicket):
        """Save ticket to local storage."""
        try:
            filepath = self.storage_path / f"{ticket.ticket_id}.json"
            with open(filepath, 'w') as f:
                json.dump(asdict(ticket), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving ticket: {str(e)}")
    
    def _load_ticket(self, ticket_id: str) -> Optional[SupportTicket]:
        """Load ticket from local storage."""
        try:
            filepath = self.storage_path / f"{ticket_id}.json"
            if not filepath.exists():
                return None
            
            with open(filepath, 'r') as f:
                ticket_data = json.load(f)
                return SupportTicket(**ticket_data)
        except Exception as e:
            logger.error(f"Error loading ticket: {str(e)}")
            return None
    
    def _send_to_api(self, ticket: SupportTicket) -> bool:
        """Send ticket to support system API."""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.api_url}/tickets",
                headers=headers,
                json=asdict(ticket)
            )
            
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error sending ticket to API: {str(e)}")
            return False

    def _validate_compliance(self, user_id: str, subject: str, description: str) -> bool:
        """Validate ticket creation against compliance rules."""
        try:
            # Check required fields
            if not all([user_id, subject, description]):
                return False
            
            # Check for sensitive data
            for sensitive_field in self.compliance_rules.get('sensitive_data', []):
                if sensitive_field in description.lower():
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating compliance: {str(e)}")
            return False

    def _validate_compliance_updates(self, updates: Dict[str, Any]) -> bool:
        """Validate ticket updates against compliance rules."""
        try:
            # Check for sensitive data in updates
            for sensitive_field in self.compliance_rules.get('sensitive_data', []):
                for value in updates.values():
                    if isinstance(value, str) and sensitive_field in value.lower():
                        return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating compliance updates: {str(e)}")
            return False

    def _generate_metadata(self) -> Dict[str, Any]:
        """Generate metadata for the ticket."""
        return {
            "created_by": os.getenv('USER', 'system'),
            "environment": os.getenv('ENVIRONMENT', 'development'),
            "version": os.getenv('VERSION', '1.0.0'),
            "checksum": hashlib.md5(str(datetime.now()).encode()).hexdigest()
        }

    def _generate_compliance_tags(self, subject: str, description: str) -> List[str]:
        """Generate compliance tags based on ticket content."""
        tags = []
        
        # Add GDPR related tags
        if any(keyword in description.lower() for keyword in ['personal data', 'privacy', 'gdpr']):
            tags.append('gdpr')
        
        # Add security related tags
        if any(keyword in description.lower() for keyword in ['security', 'access', 'authentication']):
            tags.append('security')
        
        return tags

    def _check_alerts(self):
        """Check for alert conditions and trigger alerts if needed."""
        try:
            # Get all open tickets
            open_tickets = []
            for ticket_file in self.storage_path.glob("*.json"):
                with open(ticket_file, 'r') as f:
                    ticket_data = json.load(f)
                    if ticket_data['status'] == 'open':
                        open_tickets.append(SupportTicket(**ticket_data))
            
            # Check response time alerts
            for ticket in open_tickets:
                created_at = datetime.fromisoformat(ticket.created_at)
                age = (datetime.now() - created_at).total_seconds()
                TICKET_AGE.set(age)
                
                if age > self.alert_thresholds.get('response_time', 3600):
                    self._trigger_alert(f"Ticket {ticket.ticket_id} has exceeded response time threshold")
                
                if ticket.priority == 'high' and age > self.alert_thresholds.get('high_priority_age', 7200):
                    self._trigger_alert(f"High priority ticket {ticket.ticket_id} has exceeded age threshold")
            
            # Check ticket volume
            recent_tickets = [t for t in open_tickets 
                            if (datetime.now() - datetime.fromisoformat(t.created_at)).total_seconds() < 3600]
            if len(recent_tickets) > self.alert_thresholds.get('ticket_volume', 100):
                self._trigger_alert(f"High ticket volume detected: {len(recent_tickets)} tickets in the last hour")
                
        except Exception as e:
            logger.error(f"Error checking alerts: {str(e)}")

    def _trigger_alert(self, message: str):
        """Trigger an alert with the given message."""
        try:
            # Log the alert
            logger.warning(f"ALERT: {message}")
            
            # Send alert to monitoring system
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            alert_data = {
                'message': message,
                'severity': 'warning',
                'timestamp': datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.api_url}/alerts",
                headers=headers,
                json=alert_data
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to send alert: {response.text}")
                
        except Exception as e:
            logger.error(f"Error triggering alert: {str(e)}")

if __name__ == "__main__":
    # Example usage
    support = SupportSystem(
        api_key="your_api_key",
        api_url="https://api.support-system.com"
    )
    
    # Create a ticket
    ticket = support.create_ticket(
        user_id="user123",
        subject="Login Issue",
        description="Unable to log in to the system",
        priority="high"
    )
    
    if ticket:
        print(f"Created ticket: {ticket.ticket_id}")
        
        # Update ticket
        support.update_ticket(
            ticket.ticket_id,
            {
                "status": "in_progress",
                "assigned_to": "support_agent_1"
            }
        )
        
        # Get ticket
        updated_ticket = support.get_ticket(ticket.ticket_id)
        print(f"Ticket status: {updated_ticket.status}")
        
        # Get user tickets
        user_tickets = support.get_user_tickets("user123")
        print(f"User has {len(user_tickets)} tickets") 