from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
import logging
from datetime import datetime
import json
import os
from sqlalchemy.orm import Session
from app.models.feedback import Feedback, FeedbackData, FeedbackStorage
from app.core.notifications import send_feedback_notification
from app import get_db

router = APIRouter()
logger = logging.getLogger(__name__)
feedback_storage = FeedbackStorage()

class FeedbackRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    feedback_type: str
    input_data: Dict[str, Any]
    prediction: Dict[str, Any]
    corrected_label: Optional[str] = None
    confidence_score: Optional[float] = None
    comments: Optional[str] = None
    metadata: Dict[str, Any] = {}

@router.post("/feedback")
async def submit_feedback(
    feedback: FeedbackRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Submit user feedback or bug report"""
    try:
        # Create feedback data object
        feedback_data = FeedbackData(
            user_id=feedback.user_id,
            session_id=feedback.session_id,
            feedback_type=feedback.feedback_type,
            input_data=feedback.input_data,
            model_prediction=feedback.prediction,
            corrected_label=feedback.corrected_label,
            confidence_score=feedback.confidence_score,
            comments=feedback.comments,
            metadata=feedback.metadata
        )
        
        # Create database record
        db_feedback = Feedback(
            user_id=feedback.user_id,
            session_id=feedback.session_id,
            feedback_type=feedback.feedback_type,
            input_data=feedback.input_data,
            model_prediction=feedback.prediction,
            corrected_label=feedback.corrected_label,
            confidence_score=feedback.confidence_score,
            comments=feedback.comments,
            feedback_metadata=feedback.metadata
        )
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        
        # Update metrics
        feedback_id = feedback_storage.save_feedback(feedback_data)
        
        # Send notification in background
        background_tasks.add_task(
            send_feedback_notification,
            feedback_data,
            feedback_id
        )
        
        return {
            "status": "success",
            "message": "Feedback submitted successfully",
            "feedback_id": db_feedback.id
        }
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")

@router.get("/feedback/summary")
async def get_feedback_summary(db: Session = Depends(get_db)):
    """Get summary of all feedback"""
    try:
        metrics = feedback_storage._load_metrics()
        return {
            "total_feedback": metrics.get("total_feedback", 0),
            "feedback_types": metrics.get("feedback_types", {}),
            "top_contributors": dict(sorted(
                metrics.get("user_contributions", {}).items(),
                key=lambda x: x[1],
                reverse=True
            )[:10])
        }
        
    except Exception as e:
        logger.error(f"Error getting feedback summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get feedback summary")

@router.get("/feedback/user/{user_id}")
async def get_user_contributions(user_id: str, db: Session = Depends(get_db)):
    """Get contribution statistics for a specific user"""
    try:
        contributions = feedback_storage.get_user_contributions(user_id)
        return {
            "user_id": user_id,
            "contributions": contributions
        }
        
    except Exception as e:
        logger.error(f"Error getting user contributions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user contributions") 