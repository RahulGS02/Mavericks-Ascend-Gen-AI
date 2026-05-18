"""
Trainer Dashboard API endpoints
Provides statistics, batch info, and analytics for trainers
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from typing import List, Optional
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
from app.utils.dependencies import get_current_user, get_trainer_user

router = APIRouter(prefix="/trainer/dashboard", tags=["trainer-dashboard"])


@router.get("/overview")
async def get_trainer_dashboard_overview(
    current_user: User = Depends(get_trainer_user),
    db: Session = Depends(get_db)
):
    """
    Trainer Dashboard Overview
    
    Returns:
    - Statistics cards (total batches, students, avg ratings, upcoming sessions)
    - Assigned batches list with progress
    - Recent training sessions
    - Upcoming scheduled sessions (calendar data)
    - Quick action items
    """
    
    trainer_id = current_user.id

    # ===== STATISTICS CARDS =====

    # Helper function to get all batches assigned to this trainer
    # Checks BOTH trainer_id field (legacy) AND batch_trainers table (new multi-trainer support)
    def get_trainer_batch_ids():
        # Get batches via legacy trainer_id field
        legacy_batches = db.query(Batch.id).filter(Batch.trainer_id == trainer_id).all()

        # Get batches via batch_trainers junction table
        junction_batches = db.query(BatchTrainer.batch_id).filter(
            BatchTrainer.trainer_id == trainer_id
        ).all()

        # Combine and return unique batch IDs
        all_batch_ids = set([b[0] for b in legacy_batches] + [b[0] for b in junction_batches])
        return all_batch_ids

    trainer_batch_ids = get_trainer_batch_ids()

    # 1. Total batches assigned
    total_batches = len(trainer_batch_ids)

    # Active batches: status is ACTIVE OR has scheduled jobs in progress
    # A batch is active if:
    # 1. Status is explicitly ACTIVE, OR
    # 2. Has scheduled jobs that have started (scheduled_start_date <= now) and not completed
    today = datetime.now()

    # Get batches with explicit ACTIVE status
    explicit_active = db.query(Batch.id).filter(
        Batch.id.in_(trainer_batch_ids),
        Batch.status == BatchStatus.ACTIVE
    ).all()

    # Get batches with jobs in progress (scheduled_start_date <= now, status != COMPLETED)
    batches_with_active_jobs = db.query(BatchJobSchedule.batch_id).distinct().filter(
        BatchJobSchedule.batch_id.in_(trainer_batch_ids),
        BatchJobSchedule.scheduled_start_date <= today,
        BatchJobSchedule.status != 'COMPLETED'
    ).all()

    # Combine and count unique batch IDs
    active_batch_ids = set([b[0] for b in explicit_active] + [b[0] for b in batches_with_active_jobs])
    active_batches = len(active_batch_ids)
    
    # 2. Total students across all batches
    total_students = db.query(Maverick).filter(
        Maverick.current_batch_id.in_(trainer_batch_ids)
    ).count()

    # 3. Jobs in Progress (scheduled but not completed)
    jobs_in_progress = db.query(BatchJobSchedule).filter(
        BatchJobSchedule.batch_id.in_(trainer_batch_ids),
        BatchJobSchedule.scheduled_start_date <= today,
        BatchJobSchedule.status.in_(['SCHEDULED', 'IN_PROGRESS']),
        BatchJobSchedule.is_published == True
    ).count()

    # 4. Upcoming sessions (next 7 days)
    next_week = today.date() + timedelta(days=7)

    upcoming_sessions_count = db.query(BatchJobSchedule).filter(
        BatchJobSchedule.batch_id.in_(trainer_batch_ids),
        BatchJobSchedule.scheduled_start_date >= datetime.now(),
        BatchJobSchedule.scheduled_start_date <= datetime.combine(next_week, datetime.max.time()),
        BatchJobSchedule.is_published == True
    ).count()
    
    stats = [
        {
            "label": "Active Batches",
            "value": active_batches,
            "total": total_batches,
            "change": f"{total_batches} total",
            "positive": True,
            "icon": "book-open",
            "description": "Currently running training batches"
        },
        {
            "label": "Total Students",
            "value": total_students,
            "change": "Across all batches",
            "positive": True,
            "icon": "users",
            "description": "Students enrolled in your batches"
        },
        {
            "label": "Jobs In Progress",
            "value": jobs_in_progress,
            "change": "Active sessions & tasks",
            "positive": True,
            "icon": "clipboard-check",
            "description": "Scheduled jobs currently in progress"
        },
        {
            "label": "Upcoming Sessions",
            "value": upcoming_sessions_count,
            "change": "Next 7 days",
            "positive": True,
            "icon": "calendar",
            "description": "Scheduled training sessions this week"
        }
    ]
    
    # ===== ASSIGNED BATCHES (GRID VIEW) =====

    assigned_batches = db.query(Batch).filter(
        Batch.id.in_(trainer_batch_ids)
    ).order_by(Batch.created_at.desc()).all()
    
    batches_data = []
    for batch in assigned_batches:
        # Get pipeline info
        pipeline = db.query(Pipeline).filter(Pipeline.id == batch.pipeline_id).first()
        
        # Calculate batch progress (average of all students)
        batch_mavericks = db.query(Maverick).filter(
            Maverick.current_batch_id == batch.id
        ).all()
        
        if batch_mavericks:
            total_progress = 0
            for mav in batch_mavericks:
                # FIX: Must filter by batch_id to get progress for THIS batch only
                completed = db.query(MaverickJobProgress).filter(
                    MaverickJobProgress.maverick_id == mav.id,
                    MaverickJobProgress.batch_id == batch.id,  # Added batch filter!
                    MaverickJobProgress.status == ProgressStatus.COMPLETED
                ).count()

                total_jobs = db.query(PipelineJob).filter(
                    PipelineJob.pipeline_id == batch.pipeline_id
                ).count()

                progress = (completed / total_jobs * 100) if total_jobs > 0 else 0
                total_progress += progress

            avg_progress = round(total_progress / len(batch_mavericks), 1)
        else:
            avg_progress = 0.0
        
        batches_data.append({
            "id": str(batch.id),
            "name": batch.name,
            "description": batch.description,
            "pipeline_name": pipeline.name if pipeline else "Unknown",
            "status": batch.status.value,
            "current_enrollment": batch.current_enrollment,
            "max_capacity": batch.max_capacity,
            "start_date": batch.start_date.isoformat() if batch.start_date else None,
            "end_date": batch.end_date.isoformat() if batch.end_date else None,
            "average_progress": avg_progress,  # Fixed: was progress_percentage
            "category": batch.category.value if batch.category else None
        })

    # ===== TRAINING CALENDAR (UPCOMING SESSIONS) =====

    upcoming_sessions = db.query(BatchJobSchedule).join(
        Batch, BatchJobSchedule.batch_id == Batch.id
    ).join(
        PipelineJob, BatchJobSchedule.pipeline_job_id == PipelineJob.id
    ).filter(
        Batch.trainer_id == trainer_id,
        BatchJobSchedule.scheduled_start_date >= datetime.now(),
        BatchJobSchedule.is_published == True
    ).order_by(BatchJobSchedule.scheduled_start_date).limit(10).all()

    calendar_sessions = []
    for session in upcoming_sessions:
        batch = db.query(Batch).filter(Batch.id == session.batch_id).first()
        job = db.query(PipelineJob).filter(PipelineJob.id == session.pipeline_job_id).first()

        calendar_sessions.append({
            "id": str(session.id),
            "title": job.name if job else "Training Session",
            "batch_name": batch.name if batch else "Unknown",
            "batch_id": str(session.batch_id),
            "job_type": job.job_type.value if job else "TRAINING",
            "scheduled_start": session.scheduled_start_date.isoformat(),
            "scheduled_end": session.scheduled_end_date.isoformat() if session.scheduled_end_date else None,
            "meeting_link": session.meeting_link,
            "attendance_required": session.attendance_required,
            "status": session.status.value if hasattr(session, 'status') else "SCHEDULED"
        })

    # ===== QUICK ACTIONS =====

    # Pending assessment evaluations
    # Note: Since all assessment attempts have evaluated_at filled,
    # we count assessments that might need re-evaluation or review
    # For now, counting total attempts in trainer's batches
    pending_evaluations = 0  # All attempts are auto-evaluated upon creation

    # Students needing attention (low progress)
    students_at_risk = 0
    for batch in assigned_batches:
        batch_mavericks = db.query(Maverick).filter(
            Maverick.current_batch_id == batch.id
        ).all()

        for mav in batch_mavericks:
            completed = db.query(MaverickJobProgress).filter(
                MaverickJobProgress.maverick_id == mav.id,
                MaverickJobProgress.status == ProgressStatus.COMPLETED
            ).count()

            total = db.query(PipelineJob).filter(
                PipelineJob.pipeline_id == batch.pipeline_id
            ).count()

            progress = (completed / total * 100) if total > 0 else 0
            if progress < 30:  # Less than 30% progress
                students_at_risk += 1

    # Unscheduled jobs
    unscheduled_jobs = 0
    for batch in assigned_batches:
        pipeline_jobs = db.query(PipelineJob).filter(
            PipelineJob.pipeline_id == batch.pipeline_id
        ).all()

        scheduled_job_ids = db.query(BatchJobSchedule.pipeline_job_id).filter(
            BatchJobSchedule.batch_id == batch.id
        ).all()
        scheduled_ids = [str(sid[0]) for sid in scheduled_job_ids]

        for job in pipeline_jobs:
            if str(job.id) not in scheduled_ids:
                unscheduled_jobs += 1

    quick_actions = [
        {
            "label": "Pending Evaluations",
            "count": pending_evaluations,
            "action": "Evaluate Assessments",
            "link": "/trainer/assessments",
            "icon": "clipboard-check",
            "urgent": pending_evaluations > 0
        },
        {
            "label": "Students At Risk",
            "count": students_at_risk,
            "action": "Review Progress",
            "link": "/trainer/batches",
            "icon": "alert-triangle",
            "urgent": students_at_risk > 0
        },
        {
            "label": "Unscheduled Jobs",
            "count": unscheduled_jobs,
            "action": "Schedule Sessions",
            "link": "/trainer/batches",
            "icon": "calendar-plus",
            "urgent": unscheduled_jobs > 5
        }
    ]

    # ===== RECENT ACTIVITY =====

    recent_sessions = db.query(TrainingSession).join(
        Batch, TrainingSession.batch_id == Batch.id
    ).filter(
        Batch.trainer_id == trainer_id
    ).order_by(TrainingSession.scheduled_date.desc()).limit(5).all()

    recent_activity = []
    for session in recent_sessions:
        batch = db.query(Batch).filter(Batch.id == session.batch_id).first()

        recent_activity.append({
            "id": str(session.id),
            "type": "training_session",
            "title": session.title or "Training Session",
            "batch_name": batch.name if batch else "Unknown",
            "date": session.scheduled_date.isoformat(),
            "duration_hours": round(session.duration_minutes / 60, 1),
            "attendance_count": session.attendance_count or 0
        })

    return {
        "trainer_name": current_user.name,
        "trainer_email": current_user.email,
        "stats": stats,
        "batches": batches_data,
        "calendar": calendar_sessions,
        "quick_actions": quick_actions,
        "recent_activity": recent_activity
    }


@router.get("/batches")
async def get_trainer_batches(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_trainer_user),
    db: Session = Depends(get_db)
):
    """
    Get list of batches assigned to the trainer

    Query params:
    - status_filter: Filter by batch status (PLANNED, ACTIVE, COMPLETED, CANCELLED)
    """

    # Get all batches assigned to this trainer (both legacy and junction table)
    legacy_batch_ids = db.query(Batch.id).filter(Batch.trainer_id == current_user.id).all()
    junction_batch_ids = db.query(BatchTrainer.batch_id).filter(
        BatchTrainer.trainer_id == current_user.id
    ).all()

    trainer_batch_ids = set([b[0] for b in legacy_batch_ids] + [b[0] for b in junction_batch_ids])

    query = db.query(Batch).filter(Batch.id.in_(trainer_batch_ids))

    if status_filter:
        query = query.filter(Batch.status == status_filter)

    batches = query.order_by(Batch.created_at.desc()).all()

    result = []
    for batch in batches:
        pipeline = db.query(Pipeline).filter(Pipeline.id == batch.pipeline_id).first()

        # Calculate batch progress (average of all students) - ADDED!
        batch_mavericks = db.query(Maverick).filter(
            Maverick.current_batch_id == batch.id
        ).all()

        if batch_mavericks:
            total_progress = 0
            for mav in batch_mavericks:
                # Count completed jobs for THIS batch only
                completed = db.query(MaverickJobProgress).filter(
                    MaverickJobProgress.maverick_id == mav.id,
                    MaverickJobProgress.batch_id == batch.id,
                    MaverickJobProgress.status == ProgressStatus.COMPLETED
                ).count()

                total_jobs = db.query(PipelineJob).filter(
                    PipelineJob.pipeline_id == batch.pipeline_id
                ).count()

                progress = (completed / total_jobs * 100) if total_jobs > 0 else 0
                total_progress += progress

            avg_progress = round(total_progress / len(batch_mavericks), 1)
        else:
            avg_progress = 0.0

        result.append({
            "id": str(batch.id),
            "name": batch.name,
            "description": batch.description,
            "pipeline_name": pipeline.name if pipeline else "Unknown",
            "status": batch.status.value,
            "start_date": batch.start_date.isoformat() if batch.start_date else None,
            "end_date": batch.end_date.isoformat() if batch.end_date else None,
            "current_enrollment": batch.current_enrollment,
            "max_capacity": batch.max_capacity,
            "average_progress": avg_progress  # ADDED!
        })

    return {
        "batches": result,
        "total": len(result)
    }

