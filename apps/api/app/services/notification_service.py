"""
Notification Service
Handles creating and managing notifications for requirement workflow
"""

from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from typing import Optional, List

from app.models.requirement_workflow import RequirementNotification
from app.models.user import User
from app.models.deployment import DeploymentRequest


class NotificationService:
    """Service for managing workflow notifications"""
    
    @staticmethod
    def create_notification(
        db: Session,
        user_id: UUID,
        requirement_id: UUID,
        notification_type: str,
        title: str,
        message: str,
        metadata: dict = None
    ) -> RequirementNotification:
        """Create a new notification"""
        notification = RequirementNotification(
            user_id=user_id,
            requirement_id=requirement_id,
            notification_type=notification_type,
            title=title,
            message=message,
            metadata=metadata or {},
            is_read=False
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification
    
    @staticmethod
    def notify_candidate_suggested(
        db: Session,
        requirement: DeploymentRequest,
        manager_id: UUID,
        candidate_name: str,
        suggested_by_name: str,
        match_score: Optional[float] = None
    ):
        """Notify manager when HR suggests a candidate"""
        score_text = f" with {match_score}% match" if match_score else ""
        
        NotificationService.create_notification(
            db=db,
            user_id=manager_id,
            requirement_id=requirement.id,
            notification_type="CANDIDATE_SUGGESTED",
            title="New Candidate Suggested",
            message=f"{suggested_by_name} suggested {candidate_name} for {requirement.role_title}{score_text}",
            metadata={
                "candidate_name": candidate_name,
                "match_score": float(match_score) if match_score else None,
                "requirement_title": requirement.role_title
            }
        )
    
    @staticmethod
    def notify_candidate_shortlisted(
        db: Session,
        requirement: DeploymentRequest,
        hr_users: List[User],
        candidate_name: str,
        manager_name: str
    ):
        """Notify HR when manager shortlists a candidate"""
        for hr_user in hr_users:
            NotificationService.create_notification(
                db=db,
                user_id=hr_user.id,
                requirement_id=requirement.id,
                notification_type="CANDIDATE_SHORTLISTED",
                title="Candidate Shortlisted",
                message=f"{manager_name} shortlisted {candidate_name} for {requirement.role_title}",
                metadata={
                    "candidate_name": candidate_name,
                    "manager_name": manager_name,
                    "requirement_title": requirement.role_title
                }
            )
    
    @staticmethod
    def notify_interview_scheduled(
        db: Session,
        requirement: DeploymentRequest,
        candidate_name: str,
        interview_date: str,
        interview_time: str,
        recipient_ids: List[UUID]
    ):
        """Notify relevant users when interview is scheduled"""
        for user_id in recipient_ids:
            NotificationService.create_notification(
                db=db,
                user_id=user_id,
                requirement_id=requirement.id,
                notification_type="INTERVIEW_SCHEDULED",
                title="Interview Scheduled",
                message=f"Interview scheduled for {candidate_name} on {interview_date} at {interview_time}",
                metadata={
                    "candidate_name": candidate_name,
                    "interview_date": interview_date,
                    "interview_time": interview_time,
                    "requirement_title": requirement.role_title
                }
            )
    
    @staticmethod
    def notify_interview_completed(
        db: Session,
        requirement: DeploymentRequest,
        candidate_name: str,
        rating: float,
        recipient_ids: List[UUID]
    ):
        """Notify relevant users when interview is completed"""
        for user_id in recipient_ids:
            NotificationService.create_notification(
                db=db,
                user_id=user_id,
                requirement_id=requirement.id,
                notification_type="INTERVIEW_COMPLETED",
                title="Interview Completed",
                message=f"Interview completed for {candidate_name}. Rating: {rating}/5.0",
                metadata={
                    "candidate_name": candidate_name,
                    "rating": float(rating),
                    "requirement_title": requirement.role_title
                }
            )
    
    @staticmethod
    def notify_candidate_rejected(
        db: Session,
        requirement: DeploymentRequest,
        hr_users: List[User],
        candidate_name: str,
        rejection_reason: str
    ):
        """Notify HR when candidate is rejected"""
        for hr_user in hr_users:
            NotificationService.create_notification(
                db=db,
                user_id=hr_user.id,
                requirement_id=requirement.id,
                notification_type="CANDIDATE_REJECTED",
                title="Candidate Rejected",
                message=f"{candidate_name} was rejected for {requirement.role_title}",
                metadata={
                    "candidate_name": candidate_name,
                    "rejection_reason": rejection_reason,
                    "requirement_title": requirement.role_title
                }
            )
