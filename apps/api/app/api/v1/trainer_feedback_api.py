"""
Trainer Feedback API
Endpoints for mavericks to submit feedback about trainers after completing training
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.maverick import Maverick
from app.models.batch import Batch
from app.models.trainer_feedback import TrainerFeedback, FeedbackRating
from app.services.auth import get_current_user

router = APIRouter()


class TrainerFeedbackCreate(BaseModel):
    """Schema for creating trainer feedback"""
    trainer_id: str = Field(..., description="UUID of the trainer")
    batch_id: str = Field(..., description="UUID of the batch")
    rating: str = Field(..., description="Overall rating: excellent, good, average, poor, very_poor")
    subject_knowledge: int = Field(..., ge=1, le=5, description="Subject knowledge rating (1-5)")
    communication_skills: int = Field(..., ge=1, le=5, description="Communication skills rating (1-5)")
    session_quality: int = Field(..., ge=1, le=5, description="Session quality rating (1-5)")
    doubt_resolution: int = Field(..., ge=1, le=5, description="Doubt resolution rating (1-5)")
    positive_feedback: Optional[str] = Field(None, description="What went well")
    areas_for_improvement: Optional[str] = Field(None, description="What can be improved")
    additional_comments: Optional[str] = Field(None, description="Any other comments")


@router.post("/submit")
async def submit_trainer_feedback(
    feedback_data: TrainerFeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit feedback about a trainer after completing training
    
    **Required role**: Maverick (any authenticated user with maverick profile)
    """
    
    # Get maverick profile
    maverick = db.query(Maverick).filter(Maverick.user_id == current_user.id).first()
    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maverick profile not found"
        )
    
    # Verify trainer exists
    trainer = db.query(User).filter(User.id == feedback_data.trainer_id).first()
    if not trainer or trainer.role != "trainer":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainer not found"
        )
    
    # Verify batch exists
    batch = db.query(Batch).filter(Batch.id == feedback_data.batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )
    
    # Check if maverick was in this batch
    if str(maverick.current_batch_id) != feedback_data.batch_id:
        # Allow if maverick completed this batch (even if moved to another batch)
        pass  # For now, allow any maverick to give feedback
    
    # Check if feedback already exists (prevent duplicate)
    existing_feedback = db.query(TrainerFeedback).filter(
        TrainerFeedback.maverick_id == maverick.id,
        TrainerFeedback.trainer_id == feedback_data.trainer_id,
        TrainerFeedback.batch_id == feedback_data.batch_id
    ).first()
    
    if existing_feedback:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already submitted feedback for this trainer in this batch"
        )
    
    # Create feedback
    try:
        rating_enum = FeedbackRating(feedback_data.rating)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid rating. Must be one of: excellent, good, average, poor, very_poor"
        )
    
    feedback = TrainerFeedback(
        maverick_id=maverick.id,
        trainer_id=feedback_data.trainer_id,
        batch_id=feedback_data.batch_id,
        rating=rating_enum,
        subject_knowledge=feedback_data.subject_knowledge,
        communication_skills=feedback_data.communication_skills,
        session_quality=feedback_data.session_quality,
        doubt_resolution=feedback_data.doubt_resolution,
        positive_feedback=feedback_data.positive_feedback,
        areas_for_improvement=feedback_data.areas_for_improvement,
        additional_comments=feedback_data.additional_comments
    )
    
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    return {
        "success": True,
        "message": "Trainer feedback submitted successfully",
        "feedback_id": str(feedback.id)
    }


@router.get("/my-feedback")
async def get_my_submitted_feedback(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all feedback submitted by the current maverick
    """
    
    # Get maverick profile
    maverick = db.query(Maverick).filter(Maverick.user_id == current_user.id).first()
    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maverick profile not found"
        )
    
    # Get all feedback submitted by this maverick
    feedbacks = db.query(TrainerFeedback).filter(
        TrainerFeedback.maverick_id == maverick.id
    ).order_by(TrainerFeedback.created_at.desc()).all()
    
    return {
        "feedbacks": [feedback.to_dict() for feedback in feedbacks]
    }
