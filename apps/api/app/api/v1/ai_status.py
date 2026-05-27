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
        model=settings.AI_MODEL_DISPLAY,
        features={
            "resume_parsing": settings.AI_RESUME_PARSING_ENABLED,
            "skill_extraction": settings.AI_SKILL_EXTRACTION_ENABLED,
            "performance_insights": settings.AI_PERFORMANCE_INSIGHTS_ENABLED
        },
        usage=ai_service.get_usage_stats() if ai_service else {}
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

    # Determine if the active provider has its key configured
    if settings.AI_PROVIDER == "azure":
        key_configured = bool(settings.AZURE_AI_API_KEY)
    elif settings.AI_PROVIDER == "anthropic":
        key_configured = bool(settings.ANTHROPIC_API_KEY)
    else:
        key_configured = bool(settings.AI_API_KEY)

    return AIConfigResponse(
        enabled=settings.AI_ENABLED,
        model=settings.AI_MODEL_DISPLAY,
        max_tokens=settings.AI_MAX_TOKENS,
        temperature=settings.AI_TEMPERATURE,
        daily_limit=settings.AI_DAILY_REQUEST_LIMIT,
        rate_limit_per_minute=settings.AI_RATE_LIMIT_PER_MINUTE,
        features={
            "resume_parsing": settings.AI_RESUME_PARSING_ENABLED,
            "skill_extraction": settings.AI_SKILL_EXTRACTION_ENABLED,
            "performance_insights": settings.AI_PERFORMANCE_INSIGHTS_ENABLED
        },
        api_key_configured=key_configured
    )


class AIDetailedStatsResponse(BaseModel):
    """Detailed AI statistics (Super Admin only)"""
    is_enabled: bool
    # Session stats (in-memory, resets on server restart)
    requests_today: int
    total_requests: int       # alias for requests_today — used by frontend
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
    # Lifetime DB-backed stats
    lifetime_requests: int
    lifetime_input_tokens: int
    lifetime_output_tokens: int
    lifetime_total_tokens: int
    lifetime_cost_usd: float
    # Per-feature DB breakdown
    lifetime_by_feature: Dict[str, Dict[str, Any]]
    # Daily usage (last 30 days from DB)
    daily_usage: Dict[str, int]


@router.get("/stats/detailed", response_model=AIDetailedStatsResponse)
async def get_detailed_ai_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get detailed AI usage statistics with cost breakdown

    **Required role**: Super Admin ONLY

    Returns comprehensive AI usage metrics including:
    - Session stats (in-memory since last server start)
    - Lifetime stats (from DB — persists across restarts)
    - Token usage by feature
    - Cost breakdown
    - Daily usage (last 30 days)
    """
    if current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admins can access detailed AI statistics"
        )

    if not ai_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not initialised"
        )

    # ── In-memory session stats ───────────────────────────────────────────────
    session = ai_service.get_detailed_stats()
    req = session.get("requests_today", 0)

    # ── DB lifetime stats ─────────────────────────────────────────────────────
    from app.models.ai_usage import AIUsageLog
    from datetime import date, timedelta

    db_total_requests = db.query(func.count(AIUsageLog.id)).scalar() or 0
    db_input_tokens   = db.query(func.sum(AIUsageLog.input_tokens)).scalar() or 0
    db_output_tokens  = db.query(func.sum(AIUsageLog.output_tokens)).scalar() or 0
    db_total_tokens   = db.query(func.sum(AIUsageLog.total_tokens)).scalar() or 0
    db_total_cost     = float(db.query(func.sum(AIUsageLog.cost_usd)).scalar() or 0)

    # Per-feature breakdown from DB
    feature_rows = db.query(
        AIUsageLog.feature,
        func.count(AIUsageLog.id).label("count"),
        func.sum(AIUsageLog.input_tokens).label("input_tokens"),
        func.sum(AIUsageLog.output_tokens).label("output_tokens"),
        func.sum(AIUsageLog.total_tokens).label("total_tokens"),
        func.sum(AIUsageLog.cost_usd).label("cost_usd"),
    ).group_by(AIUsageLog.feature).all()

    lifetime_by_feature = {
        row.feature: {
            "count":         row.count,
            "input_tokens":  int(row.input_tokens or 0),
            "output_tokens": int(row.output_tokens or 0),
            "total_tokens":  int(row.total_tokens or 0),
            "cost_usd":      float(row.cost_usd or 0),
        }
        for row in feature_rows
    }

    # Daily usage — last 30 days
    thirty_days_ago = date.today() - timedelta(days=29)
    daily_rows = db.query(
        func.date(AIUsageLog.created_at).label("day"),
        func.count(AIUsageLog.id).label("count"),
    ).filter(
        AIUsageLog.created_at >= thirty_days_ago
    ).group_by(func.date(AIUsageLog.created_at)).order_by("day").all()

    daily_usage = {str(row.day): row.count for row in daily_rows}

    return AIDetailedStatsResponse(
        is_enabled=settings.AI_ENABLED,
        requests_today=req,
        total_requests=req,          # alias — same value
        input_tokens=session.get("input_tokens", 0),
        output_tokens=session.get("output_tokens", 0),
        total_tokens=session.get("total_tokens", 0),
        total_cost_usd=session.get("total_cost_usd", 0.0),
        avg_tokens_per_request=session.get("avg_tokens_per_request", 0.0),
        error_count=session.get("error_count", 0),
        retry_count=session.get("retry_count", 0),
        error_rate_percentage=session.get("error_rate_percentage", 0.0),
        cost_per_request_usd=session.get("cost_per_request_usd", 0.0),
        cost_breakdown=session.get("cost_breakdown", {"input_cost_usd": 0.0, "output_cost_usd": 0.0}),
        requests_by_feature=session.get("requests_by_feature", {}),
        daily_limit=session.get("daily_limit", settings.AI_DAILY_REQUEST_LIMIT),
        rate_limit_per_minute=session.get("rate_limit_per_minute", settings.AI_RATE_LIMIT_PER_MINUTE),
        last_reset=session.get("last_reset", ""),
        lifetime_requests=db_total_requests,
        lifetime_input_tokens=int(db_input_tokens),
        lifetime_output_tokens=int(db_output_tokens),
        lifetime_total_tokens=int(db_total_tokens),
        lifetime_cost_usd=db_total_cost,
        lifetime_by_feature=lifetime_by_feature,
        daily_usage=daily_usage,
    )


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
