"""
Trainer Analytics API endpoints
Provides detailed analytics and insights for trainers
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case
from datetime import datetime, timedelta, date
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.models.user import User
from app.models.batch import Batch, BatchStatus
from app.models.batch_trainer import BatchTrainer
from app.models.pipeline import Pipeline, PipelineJob
from app.models.batch_job_schedule import BatchJobSchedule
from app.models.training import TrainingSession
from app.models.assessment import Assessment, AssessmentAttempt
from app.models.maverick import Maverick
from app.models.progress import MaverickJobProgress, ProgressStatus
from app.models.trainer_feedback import TrainerFeedback
from app.utils.dependencies import get_trainer_user

router = APIRouter(prefix="/trainer/analytics", tags=["trainer-analytics"])


def get_trainer_batch_ids(trainer_id: UUID, db: Session):
    """Helper to get all batch IDs assigned to trainer"""
    # Legacy single trainer
    legacy_batches = db.query(Batch.id).filter(Batch.trainer_id == trainer_id).all()
    # New multiple trainers
    junction_batches = db.query(BatchTrainer.batch_id).filter(
        BatchTrainer.trainer_id == trainer_id
    ).all()
    return set([b[0] for b in legacy_batches] + [b[0] for b in junction_batches])


@router.get("/overview")
async def get_trainer_analytics(
    days: int = Query(30, description="Number of days to analyze"),
    current_user: User = Depends(get_trainer_user),
    db: Session = Depends(get_db)
):
    """
    Comprehensive analytics for trainers
    
    Returns:
    - Performance metrics (completion rates, attendance, etc.)
    - Student progress insights
    - Assessment statistics
    - Training session analytics
    - Feedback trends
    - Batch performance comparison
    """
    
    trainer_id = current_user.id
    trainer_batch_ids = get_trainer_batch_ids(trainer_id, db)
    
    if not trainer_batch_ids:
        return {
            "message": "No batches assigned",
            "summary": {},
            "charts": {},
            "insights": []
        }
    
    # Date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # ========================================
    # 1. SUMMARY METRICS
    # ========================================
    
    total_students = db.query(Maverick).filter(
        Maverick.current_batch_id.in_(trainer_batch_ids)
    ).count()
    
    total_batches = len(trainer_batch_ids)
    
    active_batches = db.query(Batch).filter(
        Batch.id.in_(trainer_batch_ids),
        Batch.status == BatchStatus.ACTIVE
    ).count()
    
    # Total jobs (scheduled)
    total_jobs_scheduled = db.query(BatchJobSchedule).filter(
        BatchJobSchedule.batch_id.in_(trainer_batch_ids)
    ).count()
    
    # Completed jobs
    completed_jobs = db.query(BatchJobSchedule).filter(
        BatchJobSchedule.batch_id.in_(trainer_batch_ids),
        BatchJobSchedule.status == 'COMPLETED'
    ).count()
    
    # Completion rate
    completion_rate = round((completed_jobs / total_jobs_scheduled * 100), 1) if total_jobs_scheduled > 0 else 0
    
    # Average student progress
    all_students = db.query(Maverick).filter(
        Maverick.current_batch_id.in_(trainer_batch_ids)
    ).all()
    
    total_progress = 0
    for student in all_students:
        completed = db.query(MaverickJobProgress).filter(
            MaverickJobProgress.maverick_id == student.id,
            MaverickJobProgress.status == ProgressStatus.COMPLETED
        ).count()
        
        batch = db.query(Batch).filter(Batch.id == student.current_batch_id).first()
        if batch:
            total_pipeline_jobs = db.query(PipelineJob).filter(
                PipelineJob.pipeline_id == batch.pipeline_id
            ).count()
            
            if total_pipeline_jobs > 0:
                progress = (completed / total_pipeline_jobs) * 100
                total_progress += progress
    
    avg_student_progress = round(total_progress / len(all_students), 1) if all_students else 0
    
    # Training sessions conducted
    sessions_conducted = db.query(TrainingSession).filter(
        TrainingSession.batch_id.in_(trainer_batch_ids),
        TrainingSession.scheduled_date >= start_date,
        TrainingSession.scheduled_date <= end_date
    ).count()
    
    # Average trainer rating
    avg_rating_query = db.query(
        func.avg(
            (TrainerFeedback.subject_knowledge + 
             TrainerFeedback.communication_skills + 
             TrainerFeedback.session_quality + 
             TrainerFeedback.doubt_resolution) / 4.0
        )
    ).filter(TrainerFeedback.trainer_id == trainer_id).scalar()
    
    avg_rating = round(avg_rating_query, 2) if avg_rating_query else 0.0
    
    summary = {
        "total_students": total_students,
        "total_batches": total_batches,
        "active_batches": active_batches,
        "total_jobs_scheduled": total_jobs_scheduled,
        "completed_jobs": completed_jobs,
        "completion_rate": completion_rate,
        "avg_student_progress": avg_student_progress,
        "sessions_conducted": sessions_conducted,
        "avg_trainer_rating": avg_rating,
        "date_range_days": days
    }

    # ========================================
    # 2. ASSESSMENT PERFORMANCE
    # ========================================

    # Get all assessments for trainer's batches
    assessments = db.query(Assessment).filter(
        Assessment.batch_id.in_(trainer_batch_ids)
    ).all()

    assessment_ids = [a.id for a in assessments]

    # Total attempts
    total_attempts = db.query(AssessmentAttempt).filter(
        AssessmentAttempt.assessment_id.in_(assessment_ids)
    ).count()

    # Passed attempts (marks_obtained >= passing_marks)
    passed_attempts = 0
    failed_attempts = 0

    for attempt in db.query(AssessmentAttempt).filter(
        AssessmentAttempt.assessment_id.in_(assessment_ids)
    ).all():
        assessment = db.query(Assessment).filter(Assessment.id == attempt.assessment_id).first()
        if assessment and attempt.marks_obtained is not None:
            if attempt.marks_obtained >= assessment.passing_marks:
                passed_attempts += 1
            else:
                failed_attempts += 1

    pass_rate = round((passed_attempts / total_attempts * 100), 1) if total_attempts > 0 else 0

    # Average score
    avg_score_query = db.query(func.avg(AssessmentAttempt.marks_obtained)).filter(
        AssessmentAttempt.assessment_id.in_(assessment_ids),
        AssessmentAttempt.marks_obtained.isnot(None)
    ).scalar()

    avg_assessment_score = round(avg_score_query, 1) if avg_score_query else 0

    assessment_stats = {
        "total_assessments": len(assessments),
        "total_attempts": total_attempts,
        "passed_attempts": passed_attempts,
        "failed_attempts": failed_attempts,
        "pass_rate": pass_rate,
        "avg_score": avg_assessment_score
    }

    # ========================================
    # 3. STUDENT PROGRESS DISTRIBUTION
    # ========================================

    progress_distribution = {
        "0-25": 0,
        "26-50": 0,
        "51-75": 0,
        "76-100": 0
    }

    at_risk_students = []  # <30% progress

    for student in all_students:
        completed = db.query(MaverickJobProgress).filter(
            MaverickJobProgress.maverick_id == student.id,
            MaverickJobProgress.status == ProgressStatus.COMPLETED
        ).count()

        batch = db.query(Batch).filter(Batch.id == student.current_batch_id).first()
        if batch:
            total_pipeline_jobs = db.query(PipelineJob).filter(
                PipelineJob.pipeline_id == batch.pipeline_id
            ).count()

            if total_pipeline_jobs > 0:
                progress_pct = (completed / total_pipeline_jobs) * 100

                if progress_pct <= 25:
                    progress_distribution["0-25"] += 1
                elif progress_pct <= 50:
                    progress_distribution["26-50"] += 1
                elif progress_pct <= 75:
                    progress_distribution["51-75"] += 1
                else:
                    progress_distribution["76-100"] += 1

                if progress_pct < 30:
                    at_risk_students.append({
                        "name": student.name,
                        "email": student.email,
                        "progress": round(progress_pct, 1),
                        "batch_id": str(batch.id),
                        "batch_name": batch.name
                    })

    # ========================================
    # 4. BATCH PERFORMANCE COMPARISON
    # ========================================

    batch_performance = []
    for batch_id in trainer_batch_ids:
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        if not batch:
            continue

        # Students in batch
        batch_students = db.query(Maverick).filter(Maverick.current_batch_id == batch_id).count()

        # Jobs scheduled
        batch_jobs = db.query(BatchJobSchedule).filter(BatchJobSchedule.batch_id == batch_id).count()

        # Jobs completed
        batch_completed = db.query(BatchJobSchedule).filter(
            BatchJobSchedule.batch_id == batch_id,
            BatchJobSchedule.status == 'COMPLETED'
        ).count()

        batch_completion = round((batch_completed / batch_jobs * 100), 1) if batch_jobs > 0 else 0

        batch_performance.append({
            "batch_id": str(batch.id),
            "batch_name": batch.name,
            "students": batch_students,
            "jobs_scheduled": batch_jobs,
            "jobs_completed": batch_completed,
            "completion_rate": batch_completion,
            "status": batch.status.value
        })

    # Sort by completion rate
    batch_performance.sort(key=lambda x: x['completion_rate'], reverse=True)

    # ========================================
    # 5. WEEKLY ACTIVITY TREND (Last 7 days)
    # ========================================

    weekly_activity = []
    for i in range(7):
        day_date = end_date - timedelta(days=6-i)
        day_start = day_date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        sessions_count = db.query(TrainingSession).filter(
            TrainingSession.batch_id.in_(trainer_batch_ids),
            TrainingSession.scheduled_date >= day_start,
            TrainingSession.scheduled_date <= day_end
        ).count()

        assessments_count = db.query(AssessmentAttempt).join(
            Assessment, AssessmentAttempt.assessment_id == Assessment.id
        ).filter(
            Assessment.batch_id.in_(trainer_batch_ids),
            AssessmentAttempt.created_at >= day_start,
            AssessmentAttempt.created_at <= day_end
        ).count()

        weekly_activity.append({
            "date": day_date.strftime("%a %m/%d"),
            "sessions": sessions_count,
            "assessments": assessments_count
        })

    return {
        "trainer_name": current_user.name,
        "summary": summary,
        "assessment_stats": assessment_stats,
        "progress_distribution": progress_distribution,
        "at_risk_students": at_risk_students[:10],  # Top 10
        "batch_performance": batch_performance,
        "weekly_activity": weekly_activity
    }
