"""
Manager Talent Search API endpoints - Comprehensive Intelligent Search
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, or_, exists, distinct, case
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.maverick import Maverick, DeploymentStatus as MaverickDeploymentStatus, ProfileStatus
from app.models.maverick_skill import MaverickSkill, ProficiencyLevel
from app.models.assessment import AssessmentAttempt
from app.models.batch import Batch, BatchStatus
from app.models.progress import MaverickJobProgress, ProgressStatus
from app.models.deployment import Deployment, DeploymentStatus as DeploymentRecordStatus
from app.models.pipeline import PipelineJob, JobType
from app.utils.dependencies import get_manager_user

router = APIRouter()


# Comprehensive Training Status
class TrainingStatusFilter:
    """Meaningful training status categories based on actual data"""
    ALL = "ALL"
    NOT_STARTED = "NOT_STARTED"  # Approved, no batch assigned yet
    IN_TRAINING = "IN_TRAINING"  # Currently in active training batch
    TRAINING_COMPLETED = "TRAINING_COMPLETED"  # Completed all training jobs
    AVAILABLE = "AVAILABLE"  # Training done, ready to deploy
    DEPLOYED = "DEPLOYED"  # Currently deployed to a project

    @classmethod
    def choices(cls):
        return [cls.ALL, cls.NOT_STARTED, cls.IN_TRAINING, cls.TRAINING_COMPLETED, cls.AVAILABLE, cls.DEPLOYED]


def determine_training_status(maverick: Maverick, db: Session) -> Dict[str, Any]:
    """
    Determine comprehensive training status for a maverick
    Returns: {
        "status": str,
        "status_label": str,
        "batch_name": str or None,
        "progress_percentage": float,
        "is_available_for_deployment": bool
    }
    """
    # Check if deployed
    if maverick.deployment_status == MaverickDeploymentStatus.DEPLOYED:
        active_deployment = db.query(Deployment).filter(
            Deployment.maverick_id == maverick.id,
            Deployment.status == DeploymentRecordStatus.ACTIVE
        ).first()

        return {
            "status": TrainingStatusFilter.DEPLOYED,
            "status_label": "Currently Deployed",
            "batch_name": None,
            "project_name": active_deployment.project_name if active_deployment else "Unknown Project",
            "progress_percentage": 100.0,
            "is_available_for_deployment": False
        }

    # Check if in training (has current_batch_id)
    if maverick.current_batch_id:
        batch = db.query(Batch).filter(Batch.id == maverick.current_batch_id).first()

        if batch:
            # Get all jobs in the batch's pipeline
            pipeline_jobs = db.query(PipelineJob).filter(
                PipelineJob.pipeline_id == batch.pipeline_id,
                PipelineJob.job_type != JobType.DEPLOYMENT  # Exclude deployment job
            ).all()

            total_jobs = len(pipeline_jobs)

            if total_jobs > 0:
                # Count completed jobs
                completed_jobs = db.query(MaverickJobProgress).filter(
                    MaverickJobProgress.maverick_id == maverick.id,
                    MaverickJobProgress.batch_id == batch.id,
                    MaverickJobProgress.status == ProgressStatus.COMPLETED
                ).count()

                progress_pct = (completed_jobs / total_jobs) * 100

                # Check if training completed
                if completed_jobs == total_jobs:
                    return {
                        "status": TrainingStatusFilter.TRAINING_COMPLETED,
                        "status_label": "Training Completed - Ready to Deploy",
                        "batch_name": batch.name,
                        "progress_percentage": 100.0,
                        "is_available_for_deployment": True
                    }
                else:
                    return {
                        "status": TrainingStatusFilter.IN_TRAINING,
                        "status_label": f"In Training ({int(progress_pct)}% Complete)",
                        "batch_name": batch.name,
                        "progress_percentage": round(progress_pct, 1),
                        "is_available_for_deployment": False
                    }

    # Not in training - check if available
    if maverick.deployment_status == MaverickDeploymentStatus.AVAILABLE:
        # Check if they ever completed training
        has_completed_training = db.query(MaverickJobProgress).filter(
            MaverickJobProgress.maverick_id == maverick.id,
            MaverickJobProgress.status == ProgressStatus.COMPLETED
        ).count() > 0

        if has_completed_training:
            return {
                "status": TrainingStatusFilter.AVAILABLE,
                "status_label": "Available for Deployment",
                "batch_name": None,
                "progress_percentage": 100.0,
                "is_available_for_deployment": True
            }
        else:
            return {
                "status": TrainingStatusFilter.NOT_STARTED,
                "status_label": "Not Yet Started Training",
                "batch_name": None,
                "progress_percentage": 0.0,
                "is_available_for_deployment": False
            }

    # Default fallback
    return {
        "status": TrainingStatusFilter.NOT_STARTED,
        "status_label": "Status Unknown",
        "batch_name": None,
        "progress_percentage": 0.0,
        "is_available_for_deployment": False
    }


@router.get("/manager/search/talent")
async def search_talent(
    search_query: Optional[str] = Query(None, description="Search by name, email, college, or general text"),
    required_skills: Optional[str] = Query(None, description="Comma-separated MUST-HAVE skills"),
    preferred_skills: Optional[str] = Query(None, description="Comma-separated NICE-TO-HAVE skills"),
    training_status: Optional[str] = Query(TrainingStatusFilter.AVAILABLE, description="Training/Deployment status filter"),
    min_proficiency: Optional[str] = Query(None, description="Minimum proficiency level: BEGINNER, INTERMEDIATE, PROFICIENT"),
    min_average_score: Optional[float] = Query(None, ge=0, le=100, description="Minimum average assessment score"),
    graduation_year: Optional[int] = Query(None, description="Filter by graduation year"),
    min_cgpa: Optional[float] = Query(None, ge=0, le=10, description="Minimum CGPA"),
    degree: Optional[str] = Query(None, description="Filter by degree"),
    branch: Optional[str] = Query(None, description="Filter by branch"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_manager_user),
    db: Session = Depends(get_db)
):
    """
    🔍 COMPREHENSIVE INTELLIGENT TALENT SEARCH

    Search for mavericks with:
    - ✅ Skills matching (required + preferred with intelligent scoring)
    - ✅ Training status (not started, in training, completed, available, deployed)
    - ✅ Proficiency levels (beginner, intermediate, proficient)
    - ✅ Assessment scores
    - ✅ Education filters (degree, branch, CGPA, graduation year)
    - ✅ Text search (name, email, college)
    - ✅ AI-powered match scoring
    """

    # 1. BASE QUERY - Only approved profiles
    query = db.query(Maverick).filter(
        Maverick.profile_status == ProfileStatus.APPROVED
    )

    # 2. EDUCATION FILTERS
    if graduation_year:
        query = query.filter(Maverick.graduation_year == graduation_year)

    if min_cgpa:
        query = query.filter(Maverick.cgpa >= min_cgpa)

    if degree:
        query = query.filter(Maverick.degree.ilike(f"%{degree}%"))

    if branch:
        query = query.filter(Maverick.branch.ilike(f"%{branch}%"))

    # 3. TEXT SEARCH (name, email, college)
    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(
            or_(
                Maverick.name.ilike(search_term),
                Maverick.email.ilike(search_term),
                Maverick.college.ilike(search_term),
                Maverick.degree.ilike(search_term),
                Maverick.branch.ilike(search_term)
            )
        )

    # 4. GET ALL MATCHING MAVERICKS (before status filtering)
    all_mavericks = query.all()

    # 5. FILTER BY TRAINING STATUS & BUILD RESULTS
    # This must be done in Python since it requires complex logic
    filtered_results = []

    for mav in all_mavericks:
        # Determine training status
        status_info = determine_training_status(mav, db)

        # Apply training status filter
        if training_status and training_status != TrainingStatusFilter.ALL:
            if status_info["status"] != training_status:
                continue

        # Get average assessment score
        avg_score_result = db.query(
            func.avg(AssessmentAttempt.marks_obtained * 100.0 / AssessmentAttempt.max_marks)
        ).filter(
            AssessmentAttempt.maverick_id == mav.id,
            AssessmentAttempt.passed == True
        ).scalar()

        avg_score = float(avg_score_result) if avg_score_result else 0.0

        # Apply min_average_score filter
        if min_average_score and avg_score < min_average_score:
            continue

        filtered_results.append((mav, status_info, avg_score))

    # 6. TOTAL COUNT AFTER FILTERING
    total = len(filtered_results)

    # 7. PAGINATION
    offset = (page - 1) * page_size
    paginated_mavericks = filtered_results[offset:offset + page_size]

    # 8. BUILD DETAILED RESULTS WITH SKILL MATCHING
    results = []

    for mav, status_info, avg_score in paginated_mavericks:
        # Get maverick skills from database
        skills_data = db.query(MaverickSkill).filter(
            MaverickSkill.maverick_id == mav.id
        ).order_by(MaverickSkill.proficiency_score.desc()).all()

        # Apply proficiency filter
        if min_proficiency:
            try:
                min_prof_enum = ProficiencyLevel(min_proficiency.upper())
                proficiency_order = {
                    ProficiencyLevel.BEGINNER: 1,
                    ProficiencyLevel.INTERMEDIATE: 2,
                    ProficiencyLevel.PROFICIENT: 3
                }
                min_level = proficiency_order.get(min_prof_enum, 1)
                skills_data = [
                    s for s in skills_data
                    if s.proficiency_level and proficiency_order.get(ProficiencyLevel(s.proficiency_level), 0) >= min_level
                ]
            except (ValueError, KeyError):
                pass

        # Build skill list
        skill_list = [
            {
                "name": skill.skill_name,
                "proficiency": skill.proficiency_level or "BEGINNER",
                "score": round(float(skill.proficiency_score), 1) if skill.proficiency_score else 0.0,
                "category": skill.category
            }
            for skill in skills_data
        ]

        # INTELLIGENT SKILL MATCHING
        match_score = 100.0  # Default
        match_details = {
            "required_matches": 0,
            "required_total": 0,
            "preferred_matches": 0,
            "preferred_total": 0
        }

        if required_skills or preferred_skills:
            maverick_skill_names = [s["name"].lower() for s in skill_list]

            # Required skills matching
            if required_skills:
                required_list = [s.strip().lower() for s in required_skills.split(',') if s.strip()]
                required_matches = sum(1 for skill in required_list if any(skill in ms for ms in maverick_skill_names))
                match_details["required_matches"] = required_matches
                match_details["required_total"] = len(required_list)

                # Required skills are CRITICAL - 70% weight
                required_score = (required_matches / len(required_list)) * 70 if required_list else 70
            else:
                required_score = 70  # No required skills specified

            # Preferred skills matching
            if preferred_skills:
                preferred_list = [s.strip().lower() for s in preferred_skills.split(',') if s.strip()]
                preferred_matches = sum(1 for skill in preferred_list if any(skill in ms for ms in maverick_skill_names))
                match_details["preferred_matches"] = preferred_matches
                match_details["preferred_total"] = len(preferred_list)

                # Preferred skills are BONUS - 30% weight
                preferred_score = (preferred_matches / len(preferred_list)) * 30 if preferred_list else 0
            else:
                preferred_score = 0

            match_score = round(required_score + preferred_score, 1)

        # Build result
        results.append({
            "id": str(mav.id),
            "name": mav.name,
            "email": mav.email,
            "college": mav.college,
            "degree": mav.degree,
            "branch": mav.branch,
            "graduation_year": mav.graduation_year,
            "cgpa": float(mav.cgpa) if mav.cgpa else 0.0,

            # Training & Deployment Status
            "training_status": status_info["status"],
            "training_status_label": status_info["status_label"],
            "training_progress": status_info["progress_percentage"],
            "current_batch_name": status_info.get("batch_name"),
            "is_available_for_deployment": status_info["is_available_for_deployment"],

            # Skills & Matching
            "skills": skill_list[:15],  # Top 15 skills
            "total_skills": len(skill_list),
            "match_score": match_score,
            "match_details": match_details,

            # Scores
            "average_assessment_score": round(avg_score, 1),

            # Additional Info
            "ai_summary": mav.ai_summary,
            "github_url": mav.github_url,
            "linkedin_url": mav.linkedin_url,
        })

    # 9. SORT BY MATCH SCORE if skills provided
    if required_skills or preferred_skills:
        results.sort(key=lambda x: x["match_score"], reverse=True)

    return {
        "results": results,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "filters_applied": {
            "required_skills": required_skills,
            "preferred_skills": preferred_skills,
            "training_status": training_status,
            "min_proficiency": min_proficiency,
            "min_average_score": min_average_score,
            "graduation_year": graduation_year,
            "min_cgpa": min_cgpa
        }
    }
