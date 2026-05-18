"""
AI-Powered Batch Suggestion API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User, UserRole
from app.models.maverick import Maverick
from app.models.batch import Batch
from app.services.auth import get_current_user, get_hr_user
from app.services.batch_matcher import batch_matcher
from app.services.maverick_suggester import maverick_suggester


router = APIRouter()


class BatchSuggestionDetail(BaseModel):
    """Detailed match information"""
    required_skills_matched: int
    required_skills_total: int
    required_skills_missing: List[str]
    preferred_skills_matched: int
    focus_areas_matched: int
    matched_skills: List[str]
    total_maverick_skills: int
    total_batch_requirements: int


class BatchSuggestion(BaseModel):
    """Single batch suggestion"""
    batch_id: str
    batch_name: str
    batch_description: Optional[str]
    target_role: Optional[str]
    match_score: float
    exact_match_score: float
    ai_similarity_score: Optional[float]
    reasoning: str
    details: BatchSuggestionDetail
    recommendation: str


class BatchSuggestionsResponse(BaseModel):
    """Response with batch suggestions"""
    maverick_id: str
    maverick_name: str
    total_suggestions: int
    suggestions: List[BatchSuggestion]
    ai_enabled: bool


@router.get("/maverick/{maverick_id}", response_model=BatchSuggestionsResponse)
async def get_batch_suggestions_for_maverick(
    maverick_id: UUID,
    top_n: int = Query(3, ge=1, le=10, description="Number of top suggestions"),
    use_ai: bool = Query(True, description="Use AI for similarity matching"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Get AI-powered batch suggestions for a maverick
    
    **Required role**: HR or Super Admin
    
    Returns top N best-fit batches with:
    - Match score (0-100%)
    - Detailed skill analysis
    - AI-powered reasoning
    - Recommendation level
    """
    
    # Get maverick
    maverick = db.query(Maverick).filter(Maverick.id == maverick_id).first()
    
    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maverick not found"
        )
    
    # Get suggestions
    suggestions = await batch_matcher.suggest_best_batches(
        maverick=maverick,
        db=db,
        top_n=top_n,
        use_ai=use_ai
    )
    
    return BatchSuggestionsResponse(
        maverick_id=str(maverick.id),
        maverick_name=maverick.name,
        total_suggestions=len(suggestions),
        suggestions=suggestions,
        ai_enabled=use_ai
    )


@router.get("/my-suggestions", response_model=BatchSuggestionsResponse)
async def get_my_batch_suggestions(
    top_n: int = Query(3, ge=1, le=10, description="Number of top suggestions"),
    use_ai: bool = Query(True, description="Use AI for similarity matching"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-powered batch suggestions for current maverick
    
    **Required role**: Maverick (logged in user)
    
    Mavericks can see which batches are the best fit for their skills.
    """
    
    # Verify user is a maverick
    if current_user.role != UserRole.MAVERICK:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only mavericks can access their batch suggestions"
        )
    
    # Get maverick profile
    maverick = db.query(Maverick).filter(Maverick.user_id == current_user.id).first()
    
    if not maverick:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maverick profile not found. Please create your profile first."
        )
    
    # Get suggestions
    suggestions = await batch_matcher.suggest_best_batches(
        maverick=maverick,
        db=db,
        top_n=top_n,
        use_ai=use_ai
    )
    
    return BatchSuggestionsResponse(
        maverick_id=str(maverick.id),
        maverick_name=maverick.name,
        total_suggestions=len(suggestions),
        suggestions=suggestions,
        ai_enabled=use_ai
    )


# ==================== MAVERICK SUGGESTIONS FOR BATCH ====================


class MaverickSuggestionDetail(BaseModel):
    """Detailed maverick match information"""
    required_skills_matched: int
    required_skills_total: int
    required_skills_missing: List[str]
    preferred_skills_matched: int
    matched_skills: List[str]
    total_maverick_skills: int


class MaverickSuggestion(BaseModel):
    """Single maverick suggestion"""
    maverick_id: str
    maverick_name: str
    email: str
    college: str
    degree: Optional[str]
    branch: Optional[str]
    cgpa: Optional[float]
    graduation_year: Optional[int]
    skills: List[str]
    ai_summary: Optional[str]
    match_score: float
    exact_match_score: float
    ai_similarity_score: Optional[float]
    recommendation: str
    reasoning: str
    details: Optional[MaverickSuggestionDetail]


class MaverickSuggestionsResponse(BaseModel):
    """Response with maverick suggestions for a batch"""
    batch_id: str
    batch_name: str
    batch_category: str
    total_suggestions: int
    total_unassigned: int
    suggestions: List[MaverickSuggestion]
    ai_enabled: bool


@router.get("/batch/{batch_id}/suggest-mavericks", response_model=MaverickSuggestionsResponse)
async def suggest_mavericks_for_batch(
    batch_id: UUID,
    top_n: int = Query(10, ge=1, le=50, description="Number of top suggestions"),
    use_ai: bool = Query(True, description="Use AI for similarity matching"),
    min_score: float = Query(40.0, ge=0, le=100, description="Minimum match score"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Get AI-powered maverick suggestions for a batch

    **Required role**: HR or Super Admin

    **For Tech Skills Batches**:
    - Returns top N best-fit unassigned mavericks
    - Sorted by match score (0-100%)
    - With AI-powered reasoning and skill analysis

    **For Soft Skills Batches**:
    - Returns all unassigned mavericks
    - No skill matching required
    - HR can select anyone

    **Only suggests mavericks who are**:
    - Not assigned to any active/planned batch
    - Have APPROVED profile status
    """

    # Get batch
    batch = db.query(Batch).filter(Batch.id == batch_id).first()

    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch not found"
        )

    # Get total unassigned mavericks
    unassigned = maverick_suggester.get_unassigned_mavericks(db)
    total_unassigned = len(unassigned)

    # Get suggestions
    suggestions = await maverick_suggester.suggest_mavericks_for_batch(
        batch=batch,
        db=db,
        top_n=top_n,
        use_ai=use_ai,
        min_score=min_score
    )

    return MaverickSuggestionsResponse(
        batch_id=str(batch.id),
        batch_name=batch.name,
        batch_category=batch.category.value if batch.category else "MIXED",
        total_suggestions=len(suggestions),
        total_unassigned=total_unassigned,
        suggestions=suggestions,
        ai_enabled=use_ai
    )
