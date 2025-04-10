import json
import os
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any
import shutil
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FeedbackProcessor:
    """Processes feedback data for model retraining"""
    
    def __init__(self):
        self.feedback_dir = "data/feedback"
        self.training_data_dir = "data/training"
        self.processed_dir = "data/processed_feedback"
        
        # Create necessary directories
        os.makedirs(self.training_data_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        
    def process_feedback(self, days: int = 7):
        """Process feedback from the last N days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        feedback_file = os.path.join(self.feedback_dir, "feedback_log.jsonl")
        
        if not os.path.exists(feedback_file):
            logger.warning("No feedback file found")
            return
            
        processed_feedback = []
        with open(feedback_file, "r") as f:
            for line in f:
                feedback = json.loads(line)
                feedback_date = datetime.fromisoformat(feedback["timestamp"])
                
                if feedback_date >= cutoff_date:
                    processed_feedback.append(feedback)
                    
        if not processed_feedback:
            logger.info("No new feedback to process")
            return
            
        # Group feedback by type
        feedback_by_type = self._group_feedback_by_type(processed_feedback)
        
        # Process each feedback type
        for feedback_type, feedback_list in feedback_by_type.items():
            self._process_feedback_type(feedback_type, feedback_list)
            
        # Archive processed feedback
        self._archive_processed_feedback(processed_feedback)
        
    def _group_feedback_by_type(self, feedback_list: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group feedback by type"""
        grouped = {}
        for feedback in feedback_list:
            feedback_type = feedback["feedback_type"]
            if feedback_type not in grouped:
                grouped[feedback_type] = []
            grouped[feedback_type].append(feedback)
        return grouped
        
    def _process_feedback_type(self, feedback_type: str, feedback_list: List[Dict[str, Any]]):
        """Process feedback of a specific type"""
        if feedback_type == "correction":
            self._process_corrections(feedback_list)
        elif feedback_type == "low_confidence":
            self._process_low_confidence(feedback_list)
            
    def _process_corrections(self, feedback_list: List[Dict[str, Any]]):
        """Process correction feedback"""
        corrections_file = os.path.join(self.training_data_dir, "corrections.jsonl")
        
        with open(corrections_file, "a") as f:
            for feedback in feedback_list:
                correction_data = {
                    "original_input": feedback["input_data"],
                    "original_prediction": feedback["model_prediction"],
                    "corrected_label": feedback["corrected_label"],
                    "timestamp": feedback["timestamp"],
                    "user_id": feedback["user_id"]
                }
                f.write(json.dumps(correction_data) + "\n")
                
        logger.info(f"Processed {len(feedback_list)} corrections")
        
    def _process_low_confidence(self, feedback_list: List[Dict[str, Any]]):
        """Process low confidence feedback"""
        low_confidence_file = os.path.join(self.training_data_dir, "low_confidence.jsonl")
        
        with open(low_confidence_file, "a") as f:
            for feedback in feedback_list:
                low_confidence_data = {
                    "input_data": feedback["input_data"],
                    "prediction": feedback["model_prediction"],
                    "confidence_score": feedback["confidence_score"],
                    "timestamp": feedback["timestamp"]
                }
                f.write(json.dumps(low_confidence_data) + "\n")
                
        logger.info(f"Processed {len(feedback_list)} low confidence cases")
        
    def _archive_processed_feedback(self, feedback_list: List[Dict[str, Any]]):
        """Archive processed feedback"""
        archive_file = os.path.join(
            self.processed_dir,
            f"processed_{datetime.utcnow().strftime('%Y%m%d')}.jsonl"
        )
        
        with open(archive_file, "w") as f:
            for feedback in feedback_list:
                f.write(json.dumps(feedback) + "\n")
                
        logger.info(f"Archived {len(feedback_list)} feedback entries")

if __name__ == "__main__":
    processor = FeedbackProcessor()
    processor.process_feedback() 