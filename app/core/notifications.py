import logging
import json
import os
from datetime import datetime

logger = logging.getLogger(__name__)

def send_feedback_notification(feedback_data, feedback_id):
    """Send notification about new feedback"""
    try:
        notification = {
            "timestamp": datetime.utcnow().isoformat(),
            "feedback_id": feedback_id,
            "feedback_type": feedback_data.feedback_type,
            "user_id": feedback_data.user_id
        }
        
        # Save notification to file (in a real app, this would send to a notification service)
        notifications_dir = "data/notifications"
        os.makedirs(notifications_dir, exist_ok=True)
        
        notification_file = os.path.join(
            notifications_dir,
            f"notification_{feedback_id}.json"
        )
        
        with open(notification_file, 'w') as f:
            json.dump(notification, f)
            
        logger.info(f"Sent notification for feedback {feedback_id}")
        
    except Exception as e:
        logger.error(f"Failed to send notification: {str(e)}")
        # Don't raise the exception - this is a background task 