"""
Maverick Dashboard API
Student-focused dashboard showing only personal learning data
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, distinct
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.models.maverick import Maverick
from app.models.batch import Batch
from app.models.progress import MaverickJobProgress, ProgressStatus
from app.models.pipeline import Pipeline, PipelineJob
from app.models.assessment import Assessment, AssessmentAttempt
from app.models.training import TrainingSession, SessionStatus
from app.models.batch_job_schedule import BatchJobSchedule, JobScheduleStatus
from app.models.maverick_skill import MaverickSkill
from app.services.auth import get_current_user


router = APIRouter()


def get_maverick_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Ensure current user is a maverick"""
    if current_user.role.value != 'maverick':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Maverick role required."
        )
    
    # Get maverick record
    maverick = db.query(Maverick).filter(Maverick.email == current_user.email).first()
    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maverick profile not found"
        )
    
    return maverick


@router.get("/overview")
async def get_maverick_dashboard_overview(
    maverick: Maverick = Depends(get_maverick_user),
    db: Session = Depends(get_db)
):
    """
    Student Dashboard Overview

    Returns personalized learning data:
    - Welcome message with batch info
    - Pipeline progress (visual stepper data)
    - Current job card
    - Assessment scores
    - Skill profile (for radar chart)
    - Upcoming training sessions
    """

    # 1. BATCH INFO - Welcome banner data
    batch_info = None
    pipeline_name = None
    trainer_name = None

    if not maverick.current_batch_id:
        return {
            "welcome": {
                "student_name": maverick.name,
                "message": "You are not assigned to any batch yet. Please contact HR.",
                "has_batch": False
            }
        }

    batch = db.query(Batch).filter(Batch.id == maverick.current_batch_id).first()
    if batch:
        pipeline = db.query(Pipeline).filter(Pipeline.id == batch.pipeline_id).first()
        pipeline_name = pipeline.name if pipeline else "Unknown Pipeline"

        if batch.trainer_id:
            trainer = db.query(User).filter(User.id == batch.trainer_id).first()
            trainer_name = trainer.name if trainer else "Not assigned"

        batch_info = {
            "batch_name": batch.name,
            "pipeline_name": pipeline_name,
            "trainer_name": trainer_name or "Not assigned",
            "start_date": batch.start_date.isoformat() if batch.start_date else None,
            "end_date": batch.end_date.isoformat() if batch.end_date else None,
            "enrolled_count": batch.current_enrollment
        }

    # 2. PIPELINE PROGRESS - For visual stepper
    pipeline_jobs = db.query(PipelineJob).filter(
        PipelineJob.pipeline_id == batch.pipeline_id
    ).order_by(PipelineJob.sequence_order).all()

    progress_records = db.query(MaverickJobProgress).filter(
        MaverickJobProgress.maverick_id == maverick.id,
        MaverickJobProgress.batch_id == maverick.current_batch_id
    ).all()

    progress_map = {str(p.job_id): p for p in progress_records}

    pipeline_steps = []
    current_job = None
    completed_count = 0
    total_completion = 0.0

    for idx, job in enumerate(pipeline_jobs):
        progress = progress_map.get(str(job.id))
        status = progress.status.value if progress else "PENDING"
        completion = float(progress.completion_percentage or 0) if progress else 0.0

        step = {
            "order": job.sequence_order,
            "job_id": str(job.id),
            "title": job.name,  # Changed from job.title to job.name
            "type": job.job_type.value,
            "is_optional": not job.is_mandatory,  # Changed from job.is_optional to not job.is_mandatory
            "status": status,
            "completion_percentage": completion,
            "score": float(progress.score) if progress and progress.score else None,
            "is_current": False
        }

        # Track current job (first not completed)
        if status == "COMPLETED":
            completed_count += 1
        elif not current_job:
            current_job = step.copy()
            step["is_current"] = True

        total_completion += completion
        pipeline_steps.append(step)

    overall_progress = (total_completion / len(pipeline_jobs)) if pipeline_jobs else 0.0

    # 3. CURRENT JOB CARD - Detailed info about what to do next
    current_job_detail = None
    if current_job:
        job_id = current_job["job_id"]
        job = db.query(PipelineJob).filter(PipelineJob.id == job_id).first()
        if job:
            current_job_detail = {
                "job_id": str(job.id),
                "title": job.name,  # Changed from job.title to job.name
                "description": job.description,
                "type": job.job_type.value,
                "is_optional": not job.is_mandatory,  # Changed from job.is_optional
                "duration_hours": job.duration_days * 8 if job.duration_days else 0,  # Convert days to hours (8h/day)
                "status": current_job["status"],
                "completion_percentage": current_job["completion_percentage"],
                "can_skip": (not job.is_mandatory) and current_job["status"] == "PENDING"
            }

    # 4. ASSESSMENT SCORES - Student's report card
    assessments = db.query(AssessmentAttempt).filter(
        AssessmentAttempt.maverick_id == maverick.id
    ).order_by(AssessmentAttempt.evaluated_at.desc()).all()

    assessment_scores = []
    # Group by assessment to get attempt numbers
    assessment_attempts_count = {}
    for attempt in assessments:
        assessment_id = str(attempt.assessment_id)
        if assessment_id not in assessment_attempts_count:
            assessment_attempts_count[assessment_id] = 0
        assessment_attempts_count[assessment_id] += 1

        score_pct = (float(attempt.marks_obtained) / float(attempt.max_marks) * 100) if attempt.max_marks > 0 else 0
        assessment_scores.append({
            "assessment_title": attempt.assessment.title if attempt.assessment else "Unknown",
            "score_percentage": round(score_pct, 1),
            "marks": f"{int(attempt.marks_obtained)}/{int(attempt.max_marks)}",
            "passed": attempt.passed,
            "attempt_number": assessment_attempts_count[assessment_id],  # Calculate attempt number
            "evaluated_at": attempt.evaluated_at.isoformat() if attempt.evaluated_at else None
        })

    avg_score = sum(a["score_percentage"] for a in assessment_scores) / len(assessment_scores) if assessment_scores else 0.0

    # 5. SKILL PROFILE - For radar chart
    skills = db.query(MaverickSkill).filter(
        MaverickSkill.maverick_id == maverick.id
    ).order_by(MaverickSkill.proficiency_score.desc()).all()

    skill_profile = []
    for skill in skills[:8]:  # Top 8 skills for radar chart
        # Determine primary source of proficiency
        sources = []
        if skill.assessment_score and skill.assessment_score > 0:
            sources.append(("ASSESSMENT", skill.assessment_score))
        if skill.training_completion and skill.training_completion > 0:
            sources.append(("TRAINING", skill.training_completion))
        if skill.ai_analyzed and skill.ai_analyzed > 0:
            sources.append(("RESUME", skill.ai_analyzed))
        if skill.self_declared and skill.self_declared > 0:
            sources.append(("SELF_DECLARED", skill.self_declared))

        # Use the source with highest score
        primary_source = max(sources, key=lambda x: x[1])[0] if sources else "UNKNOWN"

        skill_profile.append({
            "skill_name": skill.skill_name,
            "proficiency_level": float(skill.proficiency_score) if skill.proficiency_score else 0.0,
            "proficiency_label": skill.proficiency_level or "BEGINNER",
            "source": primary_source,
            "category": skill.category or "OTHER"
        })

    # 6. UPCOMING TRAINING SESSIONS - Student's class schedule
    _now = datetime.now(timezone.utc)
    upcoming_sessions = db.query(TrainingSession).filter(
        TrainingSession.batch_id == maverick.current_batch_id,
        TrainingSession.scheduled_date >= _now,
        TrainingSession.status.in_([
            SessionStatus.SCHEDULED,
            SessionStatus.IN_PROGRESS,
        ])
    ).order_by(TrainingSession.scheduled_date).limit(10).all()

    sessions_calendar = [
        {
            "id": str(session.id),
            "title": session.title,
            "session_date": session.scheduled_date.isoformat() if session.scheduled_date else None,  # Changed field name
            "duration_hours": round(session.duration_minutes / 60, 1) if session.duration_minutes else 0,  # Convert minutes to hours
            "location": session.location or session.meeting_link or "TBD",  # Use meeting_link if no location
            "mode": "ONLINE" if session.meeting_link else "OFFLINE",  # Determine mode from meeting_link
            "attendance_required": True,  # Default to true since field doesn't exist
            "description": session.description
        }
        for session in upcoming_sessions
    ]

    # 7. RETURN STUDENT DASHBOARD DATA
    return {
        "welcome": {
            "student_name": maverick.name,
            "message": f"Welcome back! You're making great progress in {batch_info['batch_name']}.",
            "has_batch": True,
            "batch": batch_info
        },
        "progress": {
            "overall_completion": round(overall_progress, 1),
            "completed_jobs": completed_count,
            "total_jobs": len(pipeline_jobs),
            "pipeline_name": pipeline_name,
            "steps": pipeline_steps
        },
        "current_job": current_job_detail,
        "assessments": {
            "average_score": round(avg_score, 1),
            "total_taken": len(assessment_scores),
            "passed_count": sum(1 for a in assessment_scores if a["passed"]),
            "scores": assessment_scores[:5]  # Last 5 assessments
        },
        "skills": skill_profile,
        "upcoming_sessions": sessions_calendar
    }


@router.post("/skip-job/{job_id}")
async def skip_optional_job(
    job_id: str,
    maverick: Maverick = Depends(get_maverick_user),
    db: Session = Depends(get_db)
):
    """
    Skip an optional job

    Allows students to skip optional training/assessment jobs
    Marks the job as SKIPPED in progress
    """
    # Verify job exists and is optional
    job = db.query(PipelineJob).filter(PipelineJob.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    if job.is_mandatory:  # Changed from not job.is_optional to job.is_mandatory
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot skip required jobs"
        )

    # Check if already has progress
    progress = db.query(MaverickJobProgress).filter(
        MaverickJobProgress.maverick_id == maverick.id,
        MaverickJobProgress.job_id == job_id,
        MaverickJobProgress.batch_id == maverick.current_batch_id
    ).first()

    if progress:
        if progress.status == ProgressStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job already completed"
            )
        # Update to skipped
        progress.status = ProgressStatus.SKIPPED
        progress.completion_percentage = 100  # Mark as 100% to count as complete
        progress.notes = "Skipped by student"
    else:
        # Create new progress record as skipped
        progress = MaverickJobProgress(
            maverick_id=maverick.id,
            batch_id=maverick.current_batch_id,
            job_id=job_id,
            status=ProgressStatus.SKIPPED,
            completion_percentage=100,
            notes="Skipped by student"
        )
        db.add(progress)

    db.commit()

    return {
        "success": True,
        "message": f"Successfully skipped optional job: {job.name}"  # Changed from job.title to job.name
    }


@router.get("/batch/leaderboard")
async def get_batch_leaderboard(
    maverick: Maverick = Depends(get_maverick_user),
    db: Session = Depends(get_db)
):
    """
    Get batch leaderboard - Rankings of all mavericks in the batch

    Shows fellow batch mates ranked by performance (assessments + progress)
    No actual scores shown, only rankings
    """

    # Check if maverick is assigned to a batch
    if not maverick.current_batch_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not assigned to any batch"
        )

    # Get batch information
    batch = db.query(Batch).filter(Batch.id == maverick.current_batch_id).first()
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )

    # Get pipeline info
    pipeline = db.query(Pipeline).filter(Pipeline.id == batch.pipeline_id).first()
    pipeline_name = pipeline.name if pipeline else "Unknown Pipeline"

    # Get trainer info
    trainer = db.query(User).filter(User.id == batch.trainer_id).first() if batch.trainer_id else None
    trainer_name = trainer.name if trainer else "No Trainer Assigned"

    # Get all mavericks in this batch
    batch_mavericks = db.query(Maverick).filter(
        Maverick.current_batch_id == maverick.current_batch_id
    ).all()

    # Calculate performance metrics for each maverick
    performance_data = []

    for mate in batch_mavericks:
        # Calculate average assessment score
        assessments = db.query(AssessmentAttempt).filter(
            AssessmentAttempt.maverick_id == mate.id,
            AssessmentAttempt.batch_id == maverick.current_batch_id
        ).all()

        if assessments:
            total_score = sum(
                (float(a.marks_obtained) / float(a.max_marks) * 100)
                for a in assessments if a.max_marks > 0
            )
            avg_score = total_score / len(assessments)
            passed_count = sum(1 for a in assessments if a.passed)
            total_assessments = len(assessments)
        else:
            avg_score = 0
            passed_count = 0
            total_assessments = 0

        # Calculate overall progress
        progress_records = db.query(MaverickJobProgress).filter(
            MaverickJobProgress.maverick_id == mate.id,
            MaverickJobProgress.batch_id == maverick.current_batch_id
        ).all()

        if progress_records:
            total_progress = sum(float(p.completion_percentage or 0) for p in progress_records)
            avg_progress = total_progress / len(progress_records)
        else:
            avg_progress = 0

        # Calculate combined score for ranking (70% assessments + 30% progress)
        combined_score = (avg_score * 0.7) + (avg_progress * 0.3)

        performance_data.append({
            "id": str(mate.id),
            "name": mate.name,
            "email": mate.email,
            "average_score": round(avg_score, 2),
            "total_assessments": total_assessments,
            "passed_count": passed_count,
            "overall_progress": round(avg_progress, 2),
            "combined_score": combined_score,
            "is_current_user": mate.id == maverick.id
        })

    # Sort by combined score (descending) and assign ranks
    performance_data.sort(key=lambda x: x["combined_score"], reverse=True)

    for rank, data in enumerate(performance_data, 1):
        data["rank"] = rank
        # Remove combined_score from response (internal use only)
        del data["combined_score"]

    return {
        "batch_id": str(batch.id),
        "batch_name": batch.name,
        "pipeline_name": pipeline_name,
        "trainer_name": trainer_name,
        "start_date": batch.start_date.isoformat() if batch.start_date else None,
        "total_students": len(batch_mavericks),
        "batch_mates": performance_data
    }

    # Get assessment statistics
    assessment_attempts = db.query(AssessmentAttempt).filter(
        AssessmentAttempt.maverick_id == maverick.id
    ).order_by(AssessmentAttempt.evaluated_at.desc()).all()

    total_assessments = len(assessment_attempts)
    passed_assessments = sum(1 for a in assessment_attempts if a.passed)
    avg_score = 0.0
    if assessment_attempts:
        scores = [(a.marks_obtained / a.max_marks * 100) for a in assessment_attempts if a.max_marks > 0]
        avg_score = sum(scores) / len(scores) if scores else 0.0

    recent_assessments = [
        {
            "id": str(a.id),
            "job_title": a.assessment.title if a.assessment else "Unknown",
            "score": round((a.marks_obtained / a.max_marks * 100), 1) if a.max_marks > 0 else 0,
            "marks": f"{a.marks_obtained}/{a.max_marks}",
            "passed": a.passed,
            "evaluated_at": a.evaluated_at.isoformat() if a.evaluated_at else None,
            "attempt_number": a.attempt_number
        }
        for a in assessment_attempts[:5]  # Last 5 assessments
    ]

    # Get upcoming training sessions
    upcoming_sessions = []
    if maverick.current_batch_id:
        sessions = db.query(TrainingSession).filter(
            TrainingSession.batch_id == maverick.current_batch_id,
            TrainingSession.session_date >= datetime.utcnow(),
            TrainingSession.status.in_([
                TrainingSessionStatus.SCHEDULED,
                TrainingSessionStatus.IN_PROGRESS
            ])
        ).order_by(TrainingSession.session_date).limit(5).all()

        upcoming_sessions = [
            {
                "id": str(s.id),
                "title": s.title,
                "session_date": s.session_date.isoformat() if s.session_date else None,
                "duration_hours": s.duration_hours,
                "location": s.location,
                "mode": s.mode,
                "attendance_required": s.attendance_required,
                "status": s.status.value
            }
            for s in sessions
        ]

    # Build metric cards
    stats = [
        {
            "label": "Overall Progress",
            "value": f"{round(overall_completion, 1)}%",
            "change": f"{completed_jobs}/{total_jobs} jobs",
            "positive": overall_completion >= 70,
            "icon": "trending-up",
            "description": "Your overall completion in the training pipeline"
        },
        {
            "label": "Assessment Score",
            "value": f"{round(avg_score, 1)}%",
            "change": f"{passed_assessments}/{total_assessments} passed",
            "positive": avg_score >= 60,
            "icon": "award",
            "description": "Average score across all assessments"
        },
        {
            "label": "Completed Jobs",
            "value": completed_jobs,
            "change": "Training & Assessments",
            "positive": True,
            "icon": "check-circle",
            "description": "Number of pipeline jobs you've completed"
        },
        {
            "label": "In Progress",
            "value": in_progress_jobs,
            "change": "Active Jobs",
            "positive": in_progress_jobs > 0,
            "icon": "activity",
            "description": "Jobs currently in progress"
        },
        {
            "label": "Upcoming Sessions",
            "value": len(upcoming_sessions),
            "change": "Scheduled",
            "positive": True,
            "icon": "calendar",
            "description": "Training sessions coming up"
        },
        {
            "label": "Pending Jobs",
            "value": pending_jobs,
            "change": "To Complete",
            "positive": pending_jobs == 0,
            "icon": "clock",
            "description": "Jobs waiting to be started"
        }
    ]

    return {
        "stats": stats,
        "batch": batch_info,
        "pipeline": {
            "name": pipeline.name if pipeline else None,
            "total_jobs": total_jobs,
            "completed": completed_jobs,
            "in_progress": in_progress_jobs,
            "pending": pending_jobs,
            "overall_completion": round(overall_completion, 2)
        },
        "current_job": current_job,
        "job_progress": job_progress_list,
        "assessments": {
            "total": total_assessments,
            "passed": passed_assessments,
            "average_score": round(avg_score, 1),
            "recent": recent_assessments
        },
        "upcoming_sessions": upcoming_sessions
    }


@router.get("/batches")
async def get_my_batches(
    maverick: Maverick = Depends(get_maverick_user),
    db: Session = Depends(get_db)
):
    """
    List all batches the maverick is enrolled in.
    Discovers batches via job progress records AND current_batch_id.
    """
    # Collect all batch IDs from progress records
    rows = db.query(distinct(MaverickJobProgress.batch_id)).filter(
        MaverickJobProgress.maverick_id == maverick.id
    ).all()
    batch_ids = set(str(row[0]) for row in rows)

    # Always include current_batch_id even if no progress records yet
    if maverick.current_batch_id:
        batch_ids.add(str(maverick.current_batch_id))

    result = []
    for bid in batch_ids:
        batch = db.query(Batch).filter(Batch.id == bid).first()
        if not batch:
            continue

        pipeline = db.query(Pipeline).filter(Pipeline.id == batch.pipeline_id).first()
        total_jobs = db.query(PipelineJob).filter(
            PipelineJob.pipeline_id == batch.pipeline_id
        ).count()

        progress_records = db.query(MaverickJobProgress).filter(
            MaverickJobProgress.maverick_id == maverick.id,
            MaverickJobProgress.batch_id == bid
        ).all()

        completed_jobs = sum(1 for p in progress_records if p.status.value == "COMPLETED")
        overall = (
            sum(float(p.completion_percentage or 0) for p in progress_records) / total_jobs
        ) if total_jobs else 0.0

        result.append({
            "batch_id": str(batch.id),
            "batch_name": batch.name,
            "pipeline_name": pipeline.name if pipeline else "Unknown",
            "status": batch.status.value,
            "start_date": batch.start_date.isoformat() if batch.start_date else None,
            "end_date": batch.end_date.isoformat() if batch.end_date else None,
            "overall_progress": round(overall, 1),
            "completed_jobs": completed_jobs,
            "total_jobs": total_jobs,
            "is_current": str(maverick.current_batch_id) == bid,
        })

    # Current batch first, then alphabetical
    result.sort(key=lambda x: (not x["is_current"], x["batch_name"]))
    return {"batches": result}


@router.get("/batch/{batch_id}")
async def get_batch_detail(
    batch_id: str,
    maverick: Maverick = Depends(get_maverick_user),
    db: Session = Depends(get_db)
):
    """
    Detailed view of a single batch: maverick's own progress steps + full leaderboard.
    """
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found")

    # Verify the maverick belongs to this batch
    enrolled = str(maverick.current_batch_id) == batch_id or db.query(
        MaverickJobProgress
    ).filter(
        MaverickJobProgress.maverick_id == maverick.id,
        MaverickJobProgress.batch_id == batch_id
    ).first() is not None

    if not enrolled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not enrolled in this batch"
        )

    pipeline = db.query(Pipeline).filter(Pipeline.id == batch.pipeline_id).first()
    trainer = db.query(User).filter(User.id == batch.trainer_id).first() if batch.trainer_id else None

    # ── My Progress ──────────────────────────────────────────────────────────
    pipeline_jobs = db.query(PipelineJob).filter(
        PipelineJob.pipeline_id == batch.pipeline_id
    ).order_by(PipelineJob.sequence_order).all()

    progress_records = db.query(MaverickJobProgress).filter(
        MaverickJobProgress.maverick_id == maverick.id,
        MaverickJobProgress.batch_id == batch_id
    ).all()
    progress_map = {str(p.job_id): p for p in progress_records}

    pipeline_steps = []
    completed_count = 0
    total_completion = 0.0
    found_current = False

    for job in pipeline_jobs:
        prog = progress_map.get(str(job.id))
        st = prog.status.value if prog else "PENDING"
        completion = float(prog.completion_percentage or 0) if prog else 0.0

        step = {
            "order": job.sequence_order,
            "job_id": str(job.id),
            "title": job.name,
            "type": job.job_type.value,
            "is_optional": not job.is_mandatory,
            "status": st,
            "completion_percentage": completion,
            "score": float(prog.score) if prog and prog.score else None,
            "is_current": False,
        }

        if st == "COMPLETED":
            completed_count += 1
        elif not found_current:
            step["is_current"] = True
            found_current = True

        total_completion += completion
        pipeline_steps.append(step)

    overall_progress = (total_completion / len(pipeline_jobs)) if pipeline_jobs else 0.0

    # ── Leaderboard ──────────────────────────────────────────────────────────
    batch_mavericks = db.query(Maverick).filter(
        Maverick.current_batch_id == batch_id
    ).all()

    leaderboard = []
    for mate in batch_mavericks:
        attempts = db.query(AssessmentAttempt).filter(
            AssessmentAttempt.maverick_id == mate.id,
            AssessmentAttempt.batch_id == batch_id
        ).all()

        avg_score = 0.0
        passed_count = 0
        if attempts:
            total = sum(
                (float(a.marks_obtained) / float(a.max_marks) * 100)
                for a in attempts if a.max_marks > 0
            )
            avg_score = total / len(attempts)
            passed_count = sum(1 for a in attempts if a.passed)

        mate_progress = db.query(MaverickJobProgress).filter(
            MaverickJobProgress.maverick_id == mate.id,
            MaverickJobProgress.batch_id == batch_id
        ).all()
        avg_progress = (
            sum(float(p.completion_percentage or 0) for p in mate_progress) / len(pipeline_jobs)
        ) if pipeline_jobs and mate_progress else 0.0

        combined = (avg_score * 0.7) + (avg_progress * 0.3)
        leaderboard.append({
            "id": str(mate.id),
            "name": mate.name,
            "average_score": round(avg_score, 2),
            "total_assessments": len(attempts),
            "passed_count": passed_count,
            "overall_progress": round(avg_progress, 2),
            "combined_score": combined,
            "is_current_user": mate.id == maverick.id,
        })

    leaderboard.sort(key=lambda x: x["combined_score"], reverse=True)
    for rank, item in enumerate(leaderboard, 1):
        item["rank"] = rank
        del item["combined_score"]

    return {
        "batch_id": str(batch.id),
        "batch_name": batch.name,
        "pipeline_name": pipeline.name if pipeline else "Unknown",
        "trainer_name": trainer.name if trainer else "No Trainer Assigned",
        "status": batch.status.value,
        "start_date": batch.start_date.isoformat() if batch.start_date else None,
        "end_date": batch.end_date.isoformat() if batch.end_date else None,
        "total_students": len(batch_mavericks),
        "my_progress": {
            "overall_completion": round(overall_progress, 1),
            "completed_jobs": completed_count,
            "total_jobs": len(pipeline_jobs),
            "steps": pipeline_steps,
        },
        "leaderboard": leaderboard,
    }


@router.get("/schedule")
async def get_my_schedule(
    maverick: Maverick = Depends(get_maverick_user),
    db: Session = Depends(get_db),
):
    """
    Full training schedule for the maverick across ALL enrolled batches.
    Merges TrainingSession records + Assessment scheduled dates + BatchJobSchedule
    entries so nothing is ever missing regardless of which model the trainer used.
    Shows all items (past and future) so the maverick can see the complete picture.
    """
    # ── 1. Collect all batch IDs ──────────────────────────────────────────────
    rows = db.query(distinct(MaverickJobProgress.batch_id)).filter(
        MaverickJobProgress.maverick_id == maverick.id
    ).all()
    batch_ids = set(str(r[0]) for r in rows)
    if maverick.current_batch_id:
        batch_ids.add(str(maverick.current_batch_id))

    if not batch_ids:
        return {"schedule": [], "total": 0}

    # Pre-fetch batch name map
    batches = db.query(Batch).filter(Batch.id.in_(batch_ids)).all()
    batch_name_map = {str(b.id): b.name for b in batches}

    items = []

    # ── 2. TrainingSession records ────────────────────────────────────────────
    training_sessions = db.query(TrainingSession).filter(
        TrainingSession.batch_id.in_(batch_ids),
        TrainingSession.status != SessionStatus.CANCELLED,
    ).order_by(TrainingSession.scheduled_date).all()

    for s in training_sessions:
        items.append({
            "id": str(s.id),
            "type": "TRAINING",
            "title": s.title,
            "description": s.description or "",
            "batch_name": batch_name_map.get(str(s.batch_id), ""),
            "scheduled_date": s.scheduled_date.isoformat() if s.scheduled_date else None,
            "duration_minutes": s.duration_minutes or 0,
            "duration_hours": round((s.duration_minutes or 0) / 60, 1),
            "location": s.location or "",
            "link": s.meeting_link or "",
            "link_label": "Join Meeting" if s.meeting_link else "",
            "status": s.status.value,
            "is_online": bool(s.meeting_link),
        })

    # ── 3. Assessment records with a scheduled date ───────────────────────────
    assessments = db.query(Assessment).filter(
        Assessment.batch_id.in_(batch_ids),
        Assessment.scheduled_date.isnot(None),
    ).order_by(Assessment.scheduled_date).all()

    for a in assessments:
        items.append({
            "id": str(a.id),
            "type": "ASSESSMENT",
            "title": a.title,
            "description": a.description or "",
            "batch_name": batch_name_map.get(str(a.batch_id), ""),
            "scheduled_date": a.scheduled_date.isoformat() if a.scheduled_date else None,
            "duration_minutes": a.duration_minutes or 0,
            "duration_hours": round((a.duration_minutes or 0) / 60, 1),
            "location": "",
            "link": a.assessment_link or "",
            "link_label": "Open Assessment" if a.assessment_link else "",
            "status": "SCHEDULED",
            "is_online": True,
            "max_marks": float(a.max_marks),
            "passing_marks": float(a.passing_marks),
        })

    # ── 4. BatchJobSchedule records (published, with a meeting/assessment link) ─
    bjs_records = db.query(BatchJobSchedule).filter(
        BatchJobSchedule.batch_id.in_(batch_ids),
        BatchJobSchedule.is_published == True,
        BatchJobSchedule.status.notin_([
            JobScheduleStatus.NOT_SCHEDULED,
            JobScheduleStatus.CANCELLED,
        ]),
    ).all()

    # Collect IDs already covered by the above two queries to avoid duplicates
    seen_assessment_ids = {str(a.id) for a in assessments}

    for bjs in bjs_records:
        job = db.query(PipelineJob).filter(PipelineJob.id == bjs.pipeline_job_id).first()
        if not job:
            continue

        job_type = job.job_type.value if job.job_type else "TRAINING"
        scheduled_date = bjs.scheduled_start_date

        # Skip assessment entries already captured from Assessment table
        if job_type == "ASSESSMENT" and bjs.assessment_id and str(bjs.assessment_id) in seen_assessment_ids:
            continue

        link = ""
        link_label = ""
        description = bjs.trainer_notes or job.description or ""
        max_marks = None
        passing_marks = None

        if job_type == "ASSESSMENT" and bjs.assessment_id:
            linked_assessment = db.query(Assessment).filter(
                Assessment.id == bjs.assessment_id
            ).first()
            if linked_assessment:
                if not scheduled_date:
                    scheduled_date = linked_assessment.scheduled_date
                link = linked_assessment.assessment_link or ""
                link_label = "Open Assessment" if link else ""
                description = description or linked_assessment.description or ""
                max_marks = float(linked_assessment.max_marks)
                passing_marks = float(linked_assessment.passing_marks)
        elif job_type == "TRAINING":
            link = bjs.meeting_link or ""
            link_label = "Join Meeting" if link else ""

        entry = {
            "id": f"bjs-{str(bjs.id)}",
            "type": job_type,
            "title": job.name,
            "description": description,
            "batch_name": batch_name_map.get(str(bjs.batch_id), ""),
            "scheduled_date": scheduled_date.isoformat() if scheduled_date else None,
            "duration_minutes": 0,
            "duration_hours": 0,
            "location": "",
            "link": link,
            "link_label": link_label,
            "status": bjs.status.value,
            "is_online": bool(link),
        }
        if max_marks is not None:
            entry["max_marks"] = max_marks
            entry["passing_marks"] = passing_marks

        items.append(entry)

    # ── 5. Sort by scheduled_date (nulls last) ────────────────────────────────
    items.sort(key=lambda x: (x["scheduled_date"] is None, x["scheduled_date"] or ""))

    return {"schedule": items, "total": len(items)}
