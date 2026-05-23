"""
Super Admin Analytics API
Organization-wide analytics and insights
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta, timezone
from typing import Dict, List

from app.database import get_db
from app.models.user import User, UserRole
from app.models.maverick import Maverick, ProfileStatus, DeploymentStatus as MaverickDeploymentStatus
from app.models.batch import Batch, BatchStatus
from app.models.deployment import Deployment, DeploymentRequest, DeploymentRequestStatus
from app.models.assessment import AssessmentAttempt, Assessment
from app.models.training import TrainingSession
from app.models.progress import MaverickJobProgress, ProgressStatus
from app.models.trainer_feedback import TrainerFeedback
from app.utils.dependencies import get_super_admin


router = APIRouter(prefix="/admin/analytics", tags=["Super Admin - Analytics"])


def utc_now():
    """Get current UTC time as timezone-aware datetime"""
    return datetime.now(timezone.utc)


@router.get("/organization")
async def get_organization_analytics(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin)
):
    """
    Get comprehensive organization-wide analytics
    
    **Required role**: Super Admin ONLY
    
    Provides insights across:
    - Hiring & Onboarding Metrics
    - Training Effectiveness
    - Deployment Success Rate
    - Batch Performance
    - Assessment Trends
    - Skill Distribution
    - User Activity
    - Resource Utilization
    """
    try:
        cutoff_date = utc_now() - timedelta(days=days)
        
        # ========================================
        # 1. HIRING & ONBOARDING METRICS
        # ========================================
        total_mavericks = db.query(func.count(Maverick.id)).scalar() or 0
        
        # Mavericks registered in period
        new_registrations = db.query(func.count(Maverick.id)).filter(
            Maverick.created_at >= cutoff_date
        ).scalar() or 0
        
        # Approval rate
        approved_count = db.query(func.count(Maverick.id)).filter(
            Maverick.profile_status == ProfileStatus.APPROVED
        ).scalar() or 0
        
        pending_count = db.query(func.count(Maverick.id)).filter(
            Maverick.profile_status == ProfileStatus.PENDING
        ).scalar() or 0
        
        rejected_count = db.query(func.count(Maverick.id)).filter(
            Maverick.profile_status == ProfileStatus.REJECTED
        ).scalar() or 0
        
        approval_rate = round((approved_count / total_mavericks * 100), 1) if total_mavericks > 0 else 0
        
        # ========================================
        # 2. TRAINING EFFECTIVENESS
        # ========================================
        total_batches = db.query(func.count(Batch.id)).scalar() or 0
        active_batches = db.query(func.count(Batch.id)).filter(
            Batch.status == BatchStatus.ACTIVE
        ).scalar() or 0
        
        completed_batches = db.query(func.count(Batch.id)).filter(
            Batch.status == BatchStatus.COMPLETED
        ).scalar() or 0
        
        # Assessment success rate
        total_attempts = db.query(func.count(AssessmentAttempt.id)).filter(
            AssessmentAttempt.evaluated_at >= cutoff_date
        ).scalar() or 0
        
        passed_attempts = db.query(func.count(AssessmentAttempt.id)).filter(
            and_(
                AssessmentAttempt.passed == True,
                AssessmentAttempt.evaluated_at >= cutoff_date
            )
        ).scalar() or 0
        
        assessment_pass_rate = round((passed_attempts / total_attempts * 100), 1) if total_attempts > 0 else 0
        
        # Average assessment score
        avg_score = db.query(func.avg(AssessmentAttempt.marks_obtained)).filter(
            and_(
                AssessmentAttempt.evaluated_at >= cutoff_date,
                AssessmentAttempt.marks_obtained.isnot(None)
            )
        ).scalar() or 0
        
        # ========================================
        # 3. DEPLOYMENT METRICS
        # ========================================
        total_deployments = db.query(func.count(Deployment.id)).scalar() or 0
        
        active_deployments = db.query(func.count(Deployment.id)).filter(
            Deployment.status == "ACTIVE"
        ).scalar() or 0
        
        recent_deployments = db.query(func.count(Deployment.id)).filter(
            Deployment.deployed_at >= cutoff_date
        ).scalar() or 0
        
        # Deployment requests
        pending_requests = db.query(func.count(DeploymentRequest.id)).filter(
            DeploymentRequest.status == DeploymentRequestStatus.PENDING
        ).scalar() or 0
        
        # Deployment rate
        deployment_rate = round((total_deployments / approved_count * 100), 1) if approved_count > 0 else 0
        
        # Average time to deploy (days from approval to deployment)
        deployed_mavericks = db.query(Maverick).filter(
            Maverick.deployment_status == MaverickDeploymentStatus.DEPLOYED
        ).limit(100).all()  # Sample for performance
        
        total_days = 0
        count_with_data = 0
        for mav in deployed_mavericks:
            if mav.created_at:
                days_to_deploy = (utc_now() - mav.created_at).days
                if days_to_deploy > 0:
                    total_days += days_to_deploy
                    count_with_data += 1
        
        avg_time_to_deploy = round(total_days / count_with_data, 1) if count_with_data > 0 else 0

        # ========================================
        # 4. BATCH PERFORMANCE COMPARISON
        # ========================================
        batch_performance = []
        batches = db.query(Batch).limit(20).all()

        for batch in batches:
            enrolled = batch.current_enrollment or 0

            # Assessment pass rate for this batch
            batch_attempts = db.query(func.count(AssessmentAttempt.id)).filter(
                AssessmentAttempt.batch_id == batch.id
            ).scalar() or 0

            batch_passed = db.query(func.count(AssessmentAttempt.id)).filter(
                and_(
                    AssessmentAttempt.batch_id == batch.id,
                    AssessmentAttempt.passed == True
                )
            ).scalar() or 0

            pass_rate = round((batch_passed / batch_attempts * 100), 1) if batch_attempts > 0 else 0

            batch_performance.append({
                "batch_id": str(batch.id),
                "batch_name": batch.name,
                "enrolled": enrolled,
                "pass_rate": pass_rate,
                "status": batch.status.value if batch.status else "UNKNOWN"
            })

        # Sort by pass rate
        batch_performance.sort(key=lambda x: x['pass_rate'], reverse=True)

        # ========================================
        # 5. USER ACTIVITY METRICS
        # ========================================
        total_users = db.query(func.count(User.id)).scalar() or 0
        active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0

        # Users by role
        users_by_role = {}
        for role in UserRole:
            count = db.query(func.count(User.id)).filter(User.role == role).scalar() or 0
            users_by_role[role.value] = count

        # ========================================
        # 6. TRAINER EFFECTIVENESS
        # ========================================
        avg_trainer_rating = db.query(
            func.avg(
                (TrainerFeedback.subject_knowledge +
                 TrainerFeedback.communication_skills +
                 TrainerFeedback.session_quality +
                 TrainerFeedback.doubt_resolution) / 4.0
            )
        ).filter(TrainerFeedback.created_at >= cutoff_date).scalar() or 0

        total_feedback_count = db.query(func.count(TrainerFeedback.id)).filter(
            TrainerFeedback.created_at >= cutoff_date
        ).scalar() or 0

        # ========================================
        # 7. TREND DATA - Multiple metrics over time
        # ========================================
        trend_data = []
        # Determine optimal number of data points based on time range
        if days <= 30:
            num_points = days  # Daily for 30 days or less
        elif days <= 90:
            num_points = 30  # 30 points for 90 days (every 3 days)
        elif days <= 180:
            num_points = 30  # 30 points for 6 months (every ~6 days)
        elif days <= 365:
            num_points = 26  # 26 points for 1 year (bi-weekly)
        else:
            num_points = 24  # 24 points for 2 years (monthly)

        interval_days = max(1, days // num_points)

        for i in range(num_points, 0, -1):
            date_start = utc_now() - timedelta(days=i * interval_days)
            date_end = date_start + timedelta(days=interval_days)

            # Registrations
            registrations = db.query(func.count(Maverick.id)).filter(
                and_(
                    Maverick.created_at >= date_start,
                    Maverick.created_at < date_end
                )
            ).scalar() or 0

            # Deployments
            deployments = db.query(func.count(Deployment.id)).filter(
                and_(
                    Deployment.deployed_at >= date_start,
                    Deployment.deployed_at < date_end
                )
            ).scalar() or 0

            # Assessments
            assessments = db.query(func.count(AssessmentAttempt.id)).filter(
                and_(
                    AssessmentAttempt.evaluated_at >= date_start,
                    AssessmentAttempt.evaluated_at < date_end
                )
            ).scalar() or 0

            # Approvals
            approvals = db.query(func.count(Maverick.id)).filter(
                and_(
                    Maverick.profile_status == ProfileStatus.APPROVED,
                    Maverick.updated_at >= date_start,
                    Maverick.updated_at < date_end
                )
            ).scalar() or 0

            # Active batches (count at that time - simplified to current active)
            active_batches_count = db.query(func.count(Batch.id)).filter(
                Batch.status == BatchStatus.ACTIVE
            ).scalar() or 0

            trend_data.append({
                "date": date_start.strftime("%Y-%m-%d"),
                "registrations": registrations,
                "deployments": deployments,
                "assessments": assessments,
                "approvals": approvals,
                "active_batches": active_batches_count
            })

        # ========================================
        # 8. DEPLOYMENT BY VERTICAL
        # ========================================
        deployments_by_vertical = db.query(
            Deployment.vertical,
            func.count(Deployment.id).label('count')
        ).group_by(Deployment.vertical).all()

        vertical_distribution = [
            {"vertical": v or "Unknown", "count": c}
            for v, c in deployments_by_vertical
        ]

        # ========================================
        # RETURN COMPREHENSIVE ANALYTICS
        # ========================================
        return {
            "summary": {
                "total_mavericks": total_mavericks,
                "new_registrations": new_registrations,
                "total_batches": total_batches,
                "active_batches": active_batches,
                "total_deployments": total_deployments,
                "active_deployments": active_deployments
            },
            "hiring": {
                "total_registered": total_mavericks,
                "new_in_period": new_registrations,
                "approved": approved_count,
                "pending_review": pending_count,
                "rejected": rejected_count,
                "approval_rate": approval_rate
            },
            "training": {
                "total_batches": total_batches,
                "active_batches": active_batches,
                "completed_batches": completed_batches,
                "total_assessments": total_attempts,
                "passed_assessments": passed_attempts,
                "assessment_pass_rate": assessment_pass_rate,
                "avg_assessment_score": round(avg_score, 1) if avg_score else 0,
                "avg_trainer_rating": round(avg_trainer_rating, 1) if avg_trainer_rating else 0,
                "total_feedback_received": total_feedback_count
            },
            "deployment": {
                "total_deployments": total_deployments,
                "active_deployments": active_deployments,
                "recent_deployments": recent_deployments,
                "pending_requests": pending_requests,
                "deployment_rate": deployment_rate,
                "avg_time_to_deploy_days": avg_time_to_deploy,
                "by_vertical": vertical_distribution
            },
            "performance": {
                "batch_performance": batch_performance[:10],  # Top 10 batches
                "best_batch": batch_performance[0] if batch_performance else None,
                "worst_batch": batch_performance[-1] if batch_performance else None
            },
            "users": {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": total_users - active_users,
                "by_role": users_by_role
            },
            "trends": {
                "registrations": trend_data
            },
            "period": {
                "days": days,
                "start_date": cutoff_date.isoformat(),
                "end_date": utc_now().isoformat()
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate analytics: {str(e)}"
        )
