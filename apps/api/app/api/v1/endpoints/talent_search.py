"""
AI-Powered Talent Search API Endpoints
Intelligent candidate search with skill matching and learning timeline estimation
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from ....database import get_db
from ....models.user import User
from ....utils.dependencies import get_hr_user, get_manager_user, get_current_user
from ....services.talent_search_service import talent_search_service
from ....schemas.talent_search import (
    TalentSearchRequest,
    TalentSearchResponse,
    ExplainRequest,
    ExplanationResponse
)
from ....models.maverick import Maverick
from ....models.maverick_skill import MaverickSkill

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/search", response_model=TalentSearchResponse)
async def ai_powered_talent_search(
    request: TalentSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    AI-Powered Intelligent Talent Search
    
    **Required role**: HR or Super Admin
    
    **Features:**
    - Natural language query parsing
    - Intelligent skill matching (exact/similar/transferable)
    - Multi-factor candidate scoring
    - Adaptability-based learning timelines
    - Training plan generation
    - Cost-optimized search (< $0.003 per query)
    
    **Example Queries:**
    - "Need .NET developer with Azure experience and CGPA > 8"
    - "Python developer with React skills, available immediately"
    - "Java backend engineer with microservices experience"
    - "Frontend developer proficient in Angular or React"
    
    **Process:**
    1. Parse natural language query using AI
    2. SQL pre-filter: AVAILABLE + APPROVED candidates
    3. Score each candidate (skill match + adaptability + performance + CGPA)
    4. Tier candidates: TIER_1_EXACT, TIER_2_SIMILAR, TIER_3_TRANSFERABLE
    5. Generate training plans for skill gaps
    6. Return top matches with "Show Similar" button if exact ≤ 2
    
    **Response Includes:**
    - Ranked candidates with final scores
    - Skill match details (exact/similar/transferable)
    - Adaptability scores and learning timelines
    - Training plans with structured phases
    - Match reasoning for each candidate
    - Cost analysis (AI token usage)
    - Search summary statistics
    """
    try:
        logger.info(f"AI talent search from {current_user.email}: {request.query}")
        
        # Execute search using TalentSearchService
        result = await talent_search_service.search(
            request=request,
            db=db
        )
        
        logger.info(f"Search complete: {result.total_found} candidates found")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in talent search: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during search: {str(e)}"
        )


@router.get("/explain/{candidate_id}")
async def explain_candidate_match(
    candidate_id: UUID,
    required_skills: str = Query(..., description="Comma-separated required skills"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Explain why a candidate was suggested
    
    **Required role**: HR or Super Admin
    
    Provides detailed breakdown:
    - Skill gap analysis (what they have vs. what's needed)
    - Learning path with timelines
    - Adaptability breakdown (assessment trend, skill diversity, etc.)
    - Timeline estimates with phases
    - Match reasoning
    - Deployment recommendation
    
    **Use case:**
    When user clicks "Why was this candidate suggested?" button
    """
    try:
        # Parse skills
        skills_list = [s.strip() for s in required_skills.split(",") if s.strip()]
        
        # Get candidate
        maverick = db.query(Maverick).filter(Maverick.id == candidate_id).first()
        if not maverick:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found"
            )
        
        # Get candidate skills
        candidate_skills = db.query(MaverickSkill).filter(
            MaverickSkill.maverick_id == candidate_id
        ).all()
        
        # Use SkillSimilarityEngine to analyze
        from ....services.skill_similarity_engine import SkillSimilarityEngine
        engine = SkillSimilarityEngine()
        
        # Skill match analysis
        skill_match = engine.calculate_skill_match_score(
            candidate_skills=candidate_skills,
            required_skills=skills_list
        )
        
        # Adaptability analysis
        adaptability = engine.calculate_adaptability_score(
            maverick=maverick,
            db=db
        )
        
        # Timeline estimation
        timeline = engine.estimate_learning_timeline(
            candidate_skills=candidate_skills,
            missing_skills=skill_match["missing_skills"],
            adaptability_score=adaptability["adaptability_score"],
            skill_match_details=skill_match
        )
        
        # Build detailed explanation
        explanation = {
            "candidate_id": candidate_id,
            "candidate_name": maverick.name,
            "skill_gap_analysis": {
                "exact_matches": skill_match.get("exact_matches", []),
                "similar_matches": skill_match.get("similar_matches", []),
                "transferable_matches": skill_match.get("transferable_matches", []),
                "missing_skills": skill_match.get("missing_skills", []),
                "total_score": skill_match["total_score"],
                "match_type": skill_match["match_type"]
            },
            "learning_path": timeline.get("skill_timelines", []),
            "adaptability_breakdown": {
                "score": adaptability["adaptability_score"],
                "interpretation": adaptability.get("interpretation", "average"),
                "assessment_trend": adaptability.get("assessment_trend", "no_data"),
                "skill_count": adaptability.get("skill_count", 0),
                "recent_activity": adaptability.get("recent_activity_count", 0),
                "pass_rate": adaptability.get("pass_rate", 0)
            },
            "timeline_estimate": {
                "total_weeks": timeline["total_weeks"],
                "deployment_readiness": timeline["deployment_readiness"],
                "message": timeline["message"]
            },
            "match_reasoning": _generate_detailed_reasoning(skill_match, adaptability, timeline),
            "recommendation": _generate_recommendation(timeline["deployment_readiness"], adaptability["adaptability_score"])
        }
        
        return explanation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error explaining candidate match: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate explanation: {str(e)}"
        )


@router.get("/cost-estimate")
async def get_search_cost_estimate(
    current_user: User = Depends(get_hr_user)
):
    """
    Get estimated cost for AI-powered talent search

    **Required role**: HR or Super Admin

    Returns:
    - Per-query cost breakdown
    - Monthly cost estimates
    - Token usage estimates
    """
    return {
        "per_query_cost": {
            "query_parsing": 0.00044,  # ~500 input + ~150 output tokens @ gpt-4.1-mini pricing
            "candidate_scoring": 0.0000,  # Rules-based, no AI
            "total": 0.00044
        },
        "monthly_estimates": {
            "100_queries": 0.044,
            "500_queries": 0.22,
            "1000_queries": 0.44,
            "5000_queries": 2.20
        },
        "token_usage": {
            "input_per_query": 500,
            "output_per_query": 150,
            "provider": "Azure AI Foundry",
            "model": "gpt-4.1-mini",
            "pricing_input_per_1m": 0.40,
            "pricing_output_per_1m": 1.60
        },
        "optimization": {
            "sql_pre_filtering": "Reduces AI processing by ~80%",
            "rules_based_scoring": "No AI tokens for scoring",
            "cost_target": "< $0.001 per query"
        }
    }


@router.get("/statistics")
async def get_talent_pool_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_hr_user)
):
    """
    Get talent pool statistics for search planning

    **Required role**: HR or Super Admin

    Returns:
    - Total AVAILABLE + APPROVED candidates
    - Skill distribution
    - CGPA distribution
    - Deployment readiness breakdown
    """
    from ....models.maverick import DeploymentStatus, ProfileStatus
    from sqlalchemy import func

    # Get available candidates count
    available_count = db.query(Maverick).filter(
        Maverick.deployment_status == DeploymentStatus.AVAILABLE,
        Maverick.profile_status == ProfileStatus.APPROVED
    ).count()

    # Get skill distribution (top 10 skills)
    skill_distribution = db.query(
        MaverickSkill.skill_name,
        func.count(MaverickSkill.id).label('count'),
        func.avg(MaverickSkill.proficiency_score).label('avg_proficiency')
    ).join(Maverick).filter(
        Maverick.deployment_status == DeploymentStatus.AVAILABLE,
        Maverick.profile_status == ProfileStatus.APPROVED
    ).group_by(
        MaverickSkill.skill_name
    ).order_by(
        func.count(MaverickSkill.id).desc()
    ).limit(10).all()

    # CGPA distribution
    cgpa_stats = db.query(
        func.avg(Maverick.cgpa).label('average'),
        func.min(Maverick.cgpa).label('minimum'),
        func.max(Maverick.cgpa).label('maximum')
    ).filter(
        Maverick.deployment_status == DeploymentStatus.AVAILABLE,
        Maverick.profile_status == ProfileStatus.APPROVED,
        Maverick.cgpa.isnot(None)
    ).first()

    return {
        "talent_pool": {
            "total_available": available_count,
            "deployment_status": "AVAILABLE",
            "profile_status": "APPROVED"
        },
        "top_skills": [
            {
                "skill": skill[0],
                "candidate_count": skill[1],
                "avg_proficiency": round(float(skill[2]), 2) if skill[2] else 0
            }
            for skill in skill_distribution
        ],
        "cgpa_stats": {
            "average": round(float(cgpa_stats[0]), 2) if cgpa_stats and cgpa_stats[0] else 0,
            "minimum": round(float(cgpa_stats[1]), 2) if cgpa_stats and cgpa_stats[1] else 0,
            "maximum": round(float(cgpa_stats[2]), 2) if cgpa_stats and cgpa_stats[2] else 0
        } if cgpa_stats else None
    }


# Helper functions

def _generate_detailed_reasoning(skill_match: dict, adaptability: dict, timeline: dict) -> str:
    """Generate detailed match reasoning"""
    reasoning_parts = []

    # Skill match analysis
    exact_count = len(skill_match.get("exact_matches", []))
    similar_count = len(skill_match.get("similar_matches", []))
    transferable_count = len(skill_match.get("transferable_matches", []))

    if exact_count > 0:
        reasoning_parts.append(f"✅ Has {exact_count} exact skill match(es)")

    if similar_count > 0:
        reasoning_parts.append(f"🔄 Has {similar_count} similar skill(s) that can be leveraged")

    if transferable_count > 0:
        reasoning_parts.append(f"🎯 Has {transferable_count} transferable skill(s)")

    # Adaptability
    adapt_score = adaptability["adaptability_score"]
    if adapt_score >= 80:
        reasoning_parts.append(f"🌟 Exceptional learner (adaptability: {adapt_score:.0f}/100)")
    elif adapt_score >= 70:
        reasoning_parts.append(f"💪 Strong learner (adaptability: {adapt_score:.0f}/100)")
    elif adapt_score >= 60:
        reasoning_parts.append(f"👍 Good learner (adaptability: {adapt_score:.0f}/100)")
    else:
        reasoning_parts.append(f"📚 Average learner (adaptability: {adapt_score:.0f}/100)")

    # Timeline
    weeks = timeline["total_weeks"]
    readiness = timeline["deployment_readiness"]

    if readiness == "immediate":
        reasoning_parts.append("⚡ Ready for immediate deployment")
    elif weeks <= 2:
        reasoning_parts.append(f"⏱️ Can be ready in {weeks:.1f} week(s)")
    elif weeks <= 4:
        reasoning_parts.append(f"📅 Short training needed ({weeks:.1f} weeks)")
    else:
        reasoning_parts.append(f"🎓 Medium-term training required ({weeks:.1f} weeks)")

    return ". ".join(reasoning_parts) + "."


def _generate_recommendation(deployment_readiness: str, adaptability_score: float) -> str:
    """Generate hiring recommendation"""
    if deployment_readiness == "immediate":
        if adaptability_score >= 80:
            return "🌟 STRONGLY RECOMMENDED - Ready for immediate deployment with exceptional learning ability"
        else:
            return "✅ RECOMMENDED - Ready for immediate deployment"

    elif deployment_readiness == "short_term":
        if adaptability_score >= 75:
            return "👍 RECOMMENDED - Short training period with strong learning potential"
        else:
            return "✓ CONSIDER - Short training needed, average learning pace"

    elif deployment_readiness == "medium_term":
        if adaptability_score >= 70:
            return "⚠️ CONSIDER - Medium training required, but good learner"
        else:
            return "⏸️ EVALUATE - Significant training needed, assess urgency"

    else:
        return "❌ NOT RECOMMENDED - Long training period required"
