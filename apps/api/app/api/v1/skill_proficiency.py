"""
Skill Proficiency API
AI-powered skill proficiency analysis and tracking
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models.maverick import Maverick
from app.models.maverick_skill import MaverickSkill
from app.services.auth import get_current_user, get_hr_user
from app.services.skill_proficiency_service import skill_proficiency_service


router = APIRouter()


class SkillDetail(BaseModel):
    """Individual skill details"""
    id: str
    skill_name: str
    category: Optional[str]
    proficiency_score: float
    proficiency_level: Optional[str]
    assessment_score: Optional[float]
    training_completion: Optional[float]
    ai_analyzed: Optional[float]
    assessment_count: int
    training_count: int
    ai_feedback: Optional[str]


class RadarChartData(BaseModel):
    """Radar chart visualization data"""
    labels: List[str]
    data: List[float]
    categories: List[str]
    colors: List[str] = []  # Default to empty list to handle cache issues


class SkillProficiencySummary(BaseModel):
    """Complete skill proficiency summary - 3 proficiency levels"""
    total_skills: int
    proficient_skills: int  # 80-100%
    intermediate_skills: int  # 60-79%
    beginner_skills: int  # 0-59%
    average_proficiency: float
    radar_chart: RadarChartData
    top_skills: List[Dict[str, Any]]
    skills_needing_improvement: List[Dict[str, Any]]


@router.get("/maverick/{maverick_id}/summary", response_model=SkillProficiencySummary)
async def get_skill_proficiency_summary(
    maverick_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Get AI-powered skill proficiency summary for a maverick
    
    **Required role**: HR or Super Admin
    
    Returns:
    - Proficiency breakdown by level (Beginner/Intermediate/Advanced/Expert)
    - Average proficiency score
    - Radar chart data for visualization
    - Top 5 strongest skills
    - Top 5 skills needing improvement
    """
    
    # Verify maverick exists
    maverick = db.query(Maverick).filter(Maverick.id == maverick_id).first()
    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maverick not found"
        )
    
    summary = skill_proficiency_service.get_skill_proficiency_summary(
        maverick_id=str(maverick_id),
        db=db
    )
    
    return summary


@router.get("/maverick/{maverick_id}/skills", response_model=List[SkillDetail])
async def get_maverick_skills(
    maverick_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Get detailed list of all skills for a maverick
    
    **Required role**: HR or Super Admin
    """
    
    maverick = db.query(Maverick).filter(Maverick.id == maverick_id).first()
    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maverick not found"
        )
    
    skills = db.query(MaverickSkill).filter(
        MaverickSkill.maverick_id == maverick_id
    ).order_by(MaverickSkill.proficiency_score.desc()).all()
    
    return [
        SkillDetail(
            id=str(skill.id),
            skill_name=skill.skill_name,
            category=skill.category,
            proficiency_score=skill.proficiency_score,
            proficiency_level=skill.proficiency_level,
            assessment_score=skill.assessment_score,
            training_completion=skill.training_completion,
            ai_analyzed=skill.ai_analyzed,
            assessment_count=skill.assessment_count or 0,
            training_count=skill.training_count or 0,
            ai_feedback=skill.ai_feedback
        )
        for skill in skills
    ]


@router.get("/my-skills/summary", response_model=SkillProficiencySummary)
async def get_my_skill_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get skill proficiency summary for current maverick
    
    **Required role**: Maverick (logged in user)
    
    Mavericks can view their own skill proficiency data.
    """
    
    # Get maverick profile
    maverick = db.query(Maverick).filter(Maverick.user_id == current_user.id).first()
    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maverick profile not found"
        )
    
    summary = skill_proficiency_service.get_skill_proficiency_summary(
        maverick_id=str(maverick.id),
        db=db
    )
    
    return summary


@router.get("/my-skills", response_model=List[SkillDetail])
async def get_my_skills(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed list of skills for current maverick
    
    **Required role**: Maverick (logged in user)
    """
    
    maverick = db.query(Maverick).filter(Maverick.user_id == current_user.id).first()
    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maverick profile not found"
        )
    
    skills = db.query(MaverickSkill).filter(
        MaverickSkill.maverick_id == maverick.id
    ).order_by(MaverickSkill.proficiency_score.desc()).all()
    
    return [
        SkillDetail(
            id=str(skill.id),
            skill_name=skill.skill_name,
            category=skill.category,
            proficiency_score=skill.proficiency_score,
            proficiency_level=skill.proficiency_level,
            assessment_score=skill.assessment_score,
            training_completion=skill.training_completion,
            ai_analyzed=skill.ai_analyzed,
            assessment_count=skill.assessment_count or 0,
            training_count=skill.training_count or 0,
            ai_feedback=skill.ai_feedback
        )
        for skill in skills
    ]
