"""
HR Dashboard Analytics API
Provides actionable metrics for HR to track and manage the platform
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from datetime import datetime, date, timedelta
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.maverick import Maverick, ProfileStatus, DeploymentStatus as MaverickDeploymentStatus
from app.models.batch import Batch, BatchStatus
from app.models.deployment import DeploymentRequest, DeploymentRequestStatus, Deployment
from app.models.assessment import AssessmentAttempt, Assessment
from app.models.progress import MaverickJobProgress, JobProgressStatus
from app.models.trainer_feedback import TrainerFeedback
from app.services.auth import get_hr_user

router = APIRouter()


@router.get("/stats")
async def get_hr_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Get comprehensive HR dashboard statistics
    
    Returns actionable metrics for daily HR tracking:
    - Pending profiles requiring review
    - Unassigned mavericks (no batch)
    - Pending deployment requests
    - Training success rate
    - Active batches
    """
    
    # 1. PENDING PROFILES - Profiles awaiting HR review
    pending_profiles_count = db.query(Maverick).filter(
        Maverick.profile_status == ProfileStatus.PENDING
    ).count()
    
    # 2. UNASSIGNED MAVERICKS - Approved but not in any batch (needs action!)
    unassigned_mavericks_count = db.query(Maverick).filter(
        and_(
            Maverick.profile_status == ProfileStatus.APPROVED,
            Maverick.current_batch_id.is_(None)
        )
    ).count()
    
    # 3. PENDING DEPLOYMENT REQUESTS - Requests from managers awaiting approval
    pending_deployment_requests = db.query(DeploymentRequest).filter(
        DeploymentRequest.status == DeploymentRequestStatus.PENDING
    ).count()
    
    # 4. ACTIVE BATCHES - Currently running training batches
    active_batches_count = db.query(Batch).filter(
        Batch.status == BatchStatus.ACTIVE
    ).count()
    
    # 5. TRAINING SUCCESS RATE - Percentage of mavericks passing assessments
    # Get all assessment attempts
    total_attempts = db.query(func.count(AssessmentAttempt.id)).scalar() or 0
    passed_attempts = db.query(func.count(AssessmentAttempt.id)).filter(
        AssessmentAttempt.passed == True
    ).scalar() or 0
    
    success_rate = round((passed_attempts / total_attempts * 100), 1) if total_attempts > 0 else 0
    
    # 6. MAVERICKS AT RISK - In training but failing assessments
    # Get mavericks with failed attempts in last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    at_risk_mavericks = db.query(func.count(func.distinct(AssessmentAttempt.maverick_id))).filter(
        and_(
            AssessmentAttempt.passed == False,
            AssessmentAttempt.evaluated_at >= thirty_days_ago
        )
    ).scalar() or 0
    
    # 7. TOTAL APPROVED MAVERICKS
    total_approved = db.query(Maverick).filter(
        Maverick.profile_status == ProfileStatus.APPROVED
    ).count() or 0

    # 8. DEPLOYMENT READY - Mavericks who completed training and ready for deployment
    # Mavericks with COMPLETED batch progress
    deployment_ready_count = db.query(func.count(func.distinct(MaverickJobProgress.maverick_id))).filter(
        MaverickJobProgress.status == JobProgressStatus.COMPLETED
    ).scalar() or 0

    # 9. DEPLOYMENT RATE - Percentage of training-complete mavericks who got deployed
    # Get mavericks who completed training (have COMPLETED job progress)
    training_complete_ids = db.query(MaverickJobProgress.maverick_id).filter(
        MaverickJobProgress.status == JobProgressStatus.COMPLETED
    ).distinct().all()

    training_complete_ids_list = [str(m[0]) for m in training_complete_ids]
    training_complete_count = len(training_complete_ids_list)

    # Get how many of them are deployed
    deployed_from_training_complete = db.query(Maverick).filter(
        and_(
            Maverick.id.in_(training_complete_ids_list),
            Maverick.deployment_status == MaverickDeploymentStatus.DEPLOYED
        )
    ).count() or 0

    deployment_rate = round((deployed_from_training_complete / training_complete_count * 100), 1) if training_complete_count > 0 else 0

    # 10. MAVERICK DISTRIBUTION FOR PIE CHART (Complete Pipeline View)
    # Include ALL maverick statuses so the pie chart matches sidebar total

    # a) Pending Review (not yet approved)
    pending_review_count = pending_profiles_count  # Already calculated above

    # b) Unassigned (approved but no batch)
    unassigned_count = unassigned_mavericks_count  # Already calculated above

    # c) In Training (assigned to active batch)
    in_training_count = db.query(func.count(Maverick.id)).filter(
        and_(
            Maverick.current_batch_id.isnot(None),
            Maverick.deployment_status != MaverickDeploymentStatus.DEPLOYED
        )
    ).scalar() or 0

    # d) Training Complete but Not Deployed
    training_complete_not_deployed = db.query(func.count(func.distinct(MaverickJobProgress.maverick_id))).filter(
        and_(
            MaverickJobProgress.status == JobProgressStatus.COMPLETED,
            MaverickJobProgress.maverick_id.notin_(
                db.query(Maverick.id).filter(Maverick.deployment_status == MaverickDeploymentStatus.DEPLOYED)
            )
        )
    ).scalar() or 0

    # e) Deployed
    deployed_count = db.query(Maverick).filter(
        Maverick.deployment_status == MaverickDeploymentStatus.DEPLOYED
    ).count() or 0

    return {
        "stats": [
            {
                "label": "Pending Profiles",
                "value": pending_profiles_count,
                "change": "Requires Review",
                "positive": False,
                "icon": "users",
                "actionable": True,
                "action_url": "/hr/pending",
                "description": "New maverick registrations awaiting your approval"
            },
            {
                "label": "Unassigned Mavericks",
                "value": unassigned_mavericks_count,
                "change": "Not in Training",
                "positive": False,
                "icon": "alert",
                "actionable": True,
                "action_url": "/dashboard/unassigned",
                "description": "Approved mavericks not assigned to any batch - needs immediate action"
            },
            {
                "label": "Pending Requests",
                "value": pending_deployment_requests,
                "change": "Deployment Queue",
                "positive": False,
                "icon": "inbox",
                "actionable": True,
                "action_url": "/dashboard/pending-requests",
                "description": "Manager deployment requests awaiting approval"
            },
            {
                "label": "Active Batches",
                "value": active_batches_count,
                "change": "In Progress",
                "positive": True,
                "icon": "book",
                "actionable": True,
                "action_url": "/dashboard/batches",
                "description": "Currently running training batches"
            },
            {
                "label": "Success Rate",
                "value": f"{success_rate}%",
                "change": f"{passed_attempts}/{total_attempts} passed",
                "positive": success_rate >= 70,
                "icon": "trending",
                "actionable": False,
                "description": "Percentage of mavericks passing assessments (target: 70%+)"
            },
            {
                "label": "At Risk",
                "value": at_risk_mavericks,
                "change": "Needs Support",
                "positive": False,
                "icon": "warning",
                "actionable": True,
                "action_url": "/dashboard/at-risk",
                "description": "Mavericks failing assessments - may need additional support"
            }
        ],
        "summary": {
            "total_mavericks": db.query(Maverick).count(),
            "total_approved": total_approved,
            "deployment_ready": deployment_ready_count,
            "success_rate": success_rate,
            "deployment_rate": deployment_rate
        },
        "pie_chart_data": {
            "pending_review": pending_review_count,
            "unassigned": unassigned_count,
            "in_training": in_training_count,
            "training_complete_not_deployed": training_complete_not_deployed,
            "deployed": deployed_count,
            "labels": ["Pending Review", "Unassigned", "In Training", "Training Complete", "Deployed"],
            "values": [pending_review_count, unassigned_count, in_training_count, training_complete_not_deployed, deployed_count],
            "colors": ["#ef4444", "#f59e0b", "#3b82f6", "#8b5cf6", "#10b981"]  # Red, Orange, Blue, Purple, Green
        }
    }


@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Get recent platform activity for HR dashboard
    
    Returns recent:
    - Profile submissions
    - Batch completions
    - Assessment results
    """
    
    # Recent profile submissions (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    recent_profiles = db.query(Maverick).filter(
        Maverick.created_at >= seven_days_ago
    ).order_by(Maverick.created_at.desc()).limit(limit).all()
    
    return {
        "recent_profiles": [
            {
                "id": str(m.id),
                "name": m.name,
                "email": m.email,
                "status": m.profile_status.value,
                "created_at": m.created_at.isoformat()
            }
            for m in recent_profiles
        ]
    }


@router.get("/trainer-feedback")
async def get_trainer_feedback_summary(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Get recent trainer feedback for HR dashboard

    Returns recent feedback submitted by mavericks about trainers,
    including ratings and comments for HR to review trainer performance.
    """

    # Get recent feedback with trainer and maverick details
    recent_feedback = db.query(TrainerFeedback).order_by(
        TrainerFeedback.created_at.desc()
    ).limit(limit).all()

    feedback_list = []
    for feedback in recent_feedback:
        # Get trainer name
        trainer = db.query(User).filter(User.id == feedback.trainer_id).first()
        # Get maverick name
        maverick = db.query(Maverick).filter(Maverick.id == feedback.maverick_id).first()
        # Get batch name
        batch = db.query(Batch).filter(Batch.id == feedback.batch_id).first()

        feedback_list.append({
            "id": str(feedback.id),
            "trainer_name": trainer.name if trainer else "Unknown",
            "trainer_id": str(feedback.trainer_id),
            "maverick_name": maverick.name if maverick else "Unknown",
            "maverick_email": maverick.email if maverick else "Unknown",
            "batch_name": batch.name if batch else "Unknown",
            "rating": feedback.rating.value,
            "subject_knowledge": feedback.subject_knowledge,
            "communication_skills": feedback.communication_skills,
            "session_quality": feedback.session_quality,
            "doubt_resolution": feedback.doubt_resolution,
            "positive_feedback": feedback.positive_feedback,
            "areas_for_improvement": feedback.areas_for_improvement,
            "additional_comments": feedback.additional_comments,
            "created_at": feedback.created_at.isoformat()
        })

    # Calculate average ratings per trainer
    from sqlalchemy import func as sql_func
    trainer_stats = db.query(
        TrainerFeedback.trainer_id,
        sql_func.count(TrainerFeedback.id).label('total_feedback'),
        sql_func.avg(TrainerFeedback.subject_knowledge).label('avg_subject_knowledge'),
        sql_func.avg(TrainerFeedback.communication_skills).label('avg_communication'),
        sql_func.avg(TrainerFeedback.session_quality).label('avg_session_quality'),
        sql_func.avg(TrainerFeedback.doubt_resolution).label('avg_doubt_resolution')
    ).group_by(TrainerFeedback.trainer_id).all()

    trainer_summary = []
    for stat in trainer_stats:
        trainer = db.query(User).filter(User.id == stat.trainer_id).first()
        overall_avg = (
            (stat.avg_subject_knowledge or 0) +
            (stat.avg_communication or 0) +
            (stat.avg_session_quality or 0) +
            (stat.avg_doubt_resolution or 0)
        ) / 4.0

        trainer_summary.append({
            "trainer_id": str(stat.trainer_id),
            "trainer_name": trainer.name if trainer else "Unknown",
            "total_feedback": stat.total_feedback,
            "avg_subject_knowledge": round(stat.avg_subject_knowledge or 0, 1),
            "avg_communication": round(stat.avg_communication or 0, 1),
            "avg_session_quality": round(stat.avg_session_quality or 0, 1),
            "avg_doubt_resolution": round(stat.avg_doubt_resolution or 0, 1),
            "overall_rating": round(overall_avg, 1)
        })

    return {
        "recent_feedback": feedback_list,
        "trainer_summary": trainer_summary
    }


@router.get("/at-risk-mavericks")
async def get_at_risk_mavericks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Get detailed list of at-risk mavericks

    Returns mavericks who are failing assessments and need support
    Includes:
    - Maverick details (name, email, batch)
    - Failed assessment count
    - Recent failed assessments with scores
    - Risk level (HIGH/MEDIUM/LOW)
    """

    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    # Get all mavericks with failed attempts in last 30 days
    failed_attempts_query = db.query(
        AssessmentAttempt.maverick_id,
        func.count(AssessmentAttempt.id).label('failed_count')
    ).filter(
        and_(
            AssessmentAttempt.passed == False,
            AssessmentAttempt.evaluated_at >= thirty_days_ago
        )
    ).group_by(AssessmentAttempt.maverick_id).subquery()

    # Get mavericks with failures
    at_risk_query = db.query(
        Maverick,
        failed_attempts_query.c.failed_count
    ).join(
        failed_attempts_query,
        Maverick.id == failed_attempts_query.c.maverick_id
    ).filter(
        failed_attempts_query.c.failed_count >= 1  # At least 1 failure
    ).all()

    at_risk_list = []

    for maverick, failed_count in at_risk_query:
        # Get batch info
        batch = db.query(Batch).filter(Batch.id == maverick.current_batch_id).first() if maverick.current_batch_id else None

        # Get total assessments for this maverick
        total_assessments = db.query(func.count(AssessmentAttempt.id)).filter(
            AssessmentAttempt.maverick_id == maverick.id
        ).scalar() or 0

        # Get recent failed assessments (last 5) with assessment details
        recent_failures_query = db.query(
            AssessmentAttempt,
            Assessment.title
        ).join(
            Assessment,
            AssessmentAttempt.assessment_id == Assessment.id
        ).filter(
            and_(
                AssessmentAttempt.maverick_id == maverick.id,
                AssessmentAttempt.passed == False,
                AssessmentAttempt.evaluated_at >= thirty_days_ago
            )
        ).order_by(desc(AssessmentAttempt.evaluated_at)).limit(5).all()

        recent_failures = []
        for attempt, assessment_title in recent_failures_query:
            recent_failures.append({
                "assessment_name": assessment_title or "Assessment",
                "marks_obtained": float(attempt.marks_obtained) if attempt.marks_obtained else 0,
                "max_marks": float(attempt.max_marks) if attempt.max_marks else 100,
                "evaluated_at": attempt.evaluated_at.isoformat() if attempt.evaluated_at else None,
                "feedback": attempt.feedback
            })

        # Calculate risk level
        failure_rate = (failed_count / total_assessments * 100) if total_assessments > 0 else 0
        if failure_rate >= 60 or failed_count >= 3:
            risk_level = "HIGH"
        elif failure_rate >= 40 or failed_count >= 2:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        at_risk_list.append({
            "id": str(maverick.id),
            "name": maverick.name,
            "email": maverick.email,
            "phone": maverick.phone,
            "current_batch_id": str(maverick.current_batch_id) if maverick.current_batch_id else None,
            "batch_name": batch.name if batch else None,
            "failed_assessments": int(failed_count),
            "total_assessments": total_assessments,
            "recent_failures": recent_failures,
            "risk_level": risk_level
        })

    # Sort by risk level (HIGH first) and then by failed count
    risk_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    at_risk_list.sort(key=lambda x: (risk_order[x["risk_level"]], -x["failed_assessments"]))

    return {
        "at_risk_mavericks": at_risk_list,
        "total_count": len(at_risk_list)
    }
