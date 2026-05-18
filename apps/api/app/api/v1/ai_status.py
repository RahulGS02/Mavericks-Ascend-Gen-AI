"""
AI Status and Configuration API
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.config import settings
from app.models.user import User, UserRole
from app.models.ai_usage import AIUsageLog
from app.database import get_db
from app.services.auth import get_current_user, get_hr_user
from app.services.ai_service import ai_service


router = APIRouter()


class AIStatusResponse(BaseModel):
    """AI service status response"""
    enabled: bool
    available: bool
    environment: str
    model: str
    features: Dict[str, bool]
    usage: Dict[str, Any]


@router.get("/status", response_model=AIStatusResponse)
async def get_ai_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get AI service status and configuration
    
    **Required role**: Any authenticated user
    
    Returns current AI service status, enabled features, and usage statistics.
    """
    
    is_available = await ai_service.is_available()
    
    return AIStatusResponse(
        enabled=settings.AI_ENABLED,
        available=is_available,
        environment=settings.ENVIRONMENT,
        model=settings.AI_MODEL,
        features={
            "resume_parsing": settings.AI_RESUME_PARSING_ENABLED,
            "skill_extraction": settings.AI_SKILL_EXTRACTION_ENABLED,
            "performance_insights": settings.AI_PERFORMANCE_INSIGHTS_ENABLED
        },
        usage=ai_service.get_usage_stats()
    )


class AIConfigResponse(BaseModel):
    """AI configuration details (HR only)"""
    enabled: bool
    model: str
    max_tokens: int
    temperature: float
    daily_limit: int
    rate_limit_per_minute: int
    features: Dict[str, bool]
    api_key_configured: bool


@router.get("/config", response_model=AIConfigResponse)
async def get_ai_config(
    current_user: User = Depends(get_hr_user)
):
    """
    Get detailed AI configuration

    **Required role**: HR or Super Admin

    Returns detailed AI configuration for administrators.
    """

    return AIConfigResponse(
        enabled=settings.AI_ENABLED,
        model=settings.AI_MODEL,
        max_tokens=settings.AI_MAX_TOKENS,
        temperature=settings.AI_TEMPERATURE,
        daily_limit=settings.AI_DAILY_REQUEST_LIMIT,
        rate_limit_per_minute=settings.AI_RATE_LIMIT_PER_MINUTE,
        features={
            "resume_parsing": settings.AI_RESUME_PARSING_ENABLED,
            "skill_extraction": settings.AI_SKILL_EXTRACTION_ENABLED,
            "performance_insights": settings.AI_PERFORMANCE_INSIGHTS_ENABLED
        },
        api_key_configured=settings.AI_API_KEY is not None and len(settings.AI_API_KEY) > 0
    )


class AIDetailedStatsResponse(BaseModel):
    """Detailed AI statistics (Super Admin only)"""
    requests_today: int
    input_tokens: int
    output_tokens: int
    total_tokens: int
    total_cost_usd: float
    avg_tokens_per_request: float
    error_count: int
    retry_count: int
    error_rate_percentage: float
    cost_per_request_usd: float
    cost_breakdown: Dict[str, float]
    requests_by_feature: Dict[str, Dict[str, Any]]
    daily_limit: int
    rate_limit_per_minute: int
    last_reset: str


@router.get("/stats/detailed", response_model=AIDetailedStatsResponse)
async def get_detailed_ai_stats(
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed AI usage statistics with cost breakdown

    **Required role**: Super Admin ONLY

    Returns comprehensive AI usage metrics including:
    - Token usage by feature
    - Cost breakdown
    - Error rates
    - Performance metrics
    """
    # Verify user is super admin
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can access detailed AI statistics"
        )

    stats = ai_service.get_detailed_stats()

    return AIDetailedStatsResponse(**stats)


class AICostAnalyticsResponse(BaseModel):
    """AI cost analytics (Super Admin only)"""
    total_cost_all_time: float
    total_requests: int
    total_tokens: int
    avg_cost_per_request: float
    cost_by_feature: Dict[str, float]
    requests_by_day: Dict[str, int]


@router.get("/analytics/costs", response_model=AICostAnalyticsResponse)
async def get_ai_cost_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI cost analytics from database logs

    **Required role**: Super Admin ONLY

    Returns historical cost data and analytics.
    """
    # Verify user is super admin
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can access cost analytics"
        )

    # Get all-time statistics from database
    total_cost = db.query(func.sum(AIUsageLog.cost_usd)).scalar() or 0
    total_requests = db.query(func.count(AIUsageLog.id)).scalar() or 0
    total_tokens = db.query(func.sum(AIUsageLog.total_tokens)).scalar() or 0

    # Cost by feature
    feature_costs = db.query(
        AIUsageLog.feature,
        func.sum(AIUsageLog.cost_usd).label('cost')
    ).group_by(AIUsageLog.feature).all()

    cost_by_feature = {feature: float(cost) for feature, cost in feature_costs}

    # Requests by day (last 30 days)
    requests_by_day_data = db.query(
        func.date(AIUsageLog.created_at).label('date'),
        func.count(AIUsageLog.id).label('count')
    ).group_by(func.date(AIUsageLog.created_at)).limit(30).all()

    requests_by_day = {
        str(date): count for date, count in requests_by_day_data
    }

    avg_cost = float(total_cost / total_requests) if total_requests > 0 else 0

    return AICostAnalyticsResponse(
        total_cost_all_time=float(total_cost),
        total_requests=total_requests,
        total_tokens=total_tokens,
        avg_cost_per_request=avg_cost,
        cost_by_feature=cost_by_feature,
        requests_by_day=requests_by_day
    )
