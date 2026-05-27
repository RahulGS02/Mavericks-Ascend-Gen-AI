"""
AI Chatbot Endpoint — role-specific personal assistant
Available to every authenticated user. Role is read from the JWT.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ....database import get_db
from ....models.user import User
from ....utils.dependencies import get_current_user
from ....services.ai_service import ai_service
from ....services.chatbot_service import (
    build_system_prompt,
    is_analytical_query,
    run_analytics_query,
    ROLE_SUGGESTIONS,
)

router = APIRouter()
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str    # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000,
                         description="User's current message")
    conversation_history: List[ChatMessage] = Field(
        default_factory=list,
        description="Previous turns (last 20 kept)",
    )


class ChatResponse(BaseModel):
    response: str                        = Field(..., description="AI reply")
    type: str                            = Field(..., description="guide | analytics | general")
    data: Optional[List[Dict[str, Any]]] = Field(None, description="DB rows for analytics")
    sql:  Optional[str]                  = Field(None, description="SQL run for analytics")
    data_count: Optional[int]            = Field(None, description="Row count for analytics")


class SuggestionsResponse(BaseModel):
    suggestions: List[str]
    role: str


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/message", response_model=ChatResponse)
async def chat_message(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Send a message to the role-specific AI assistant.

    - **Navigation / how-to questions** → answered from role knowledge base.
    - **Analytical questions** (HR & Super Admin only) → real database query,
      AI interprets and summarises the result.
    """
    if ai_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not configured. Set AI_PROVIDER=azure in .env.",
        )
    if not hasattr(ai_service, "chat_with_history"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Active AI provider does not support chatbot (chat_with_history missing).",
        )

    role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    system_prompt = build_system_prompt(role, current_user.name or current_user.email)

    # ── Keep last 20 turns ────────────────────────────────────────────────────
    history = [{"role": m.role, "content": m.content}
               for m in request.conversation_history[-20:]]

    # ── Analytical branch (HR / Super Admin) ──────────────────────────────────
    query_type  = "guide"
    data:  Optional[List[dict]] = None
    sql:   Optional[str]        = None
    data_count: Optional[int]   = None

    if is_analytical_query(request.message, role):
        query_type = "analytics"
        analytics = await run_analytics_query(request.message, db, role)

        if analytics:
            data       = analytics["data"]
            sql        = analytics["sql"]
            data_count = analytics["count"]

            # Inject compact data context into the conversation
            sample = data[:10]            # send at most 10 rows to the AI
            data_summary = json.dumps(sample, default=str)
            data_context = (
                f"\n\n[LIVE DATABASE RESULT]\n"
                f"Query returned {data_count} record(s).\n"
                f"Data (up to 10 rows): {data_summary}\n"
                f"SQL used: {sql}\n"
                f"Please interpret this data and answer the user's question clearly."
            )
            augmented_message = request.message + data_context
        else:
            # Analytics attempted but failed — fall back to guidance
            query_type = "guide"
            augmented_message = (
                request.message
                + "\n\n[Note: Unable to query live data for this question. "
                "Please guide the user to the Analytics page instead.]"
            )
    else:
        augmented_message = request.message

    # ── Build final messages list ─────────────────────────────────────────────
    messages = history + [{"role": "user", "content": augmented_message}]

    # ── Call AI ───────────────────────────────────────────────────────────────
    ai_response = await ai_service.chat_with_history(
        messages=messages,
        system_prompt=system_prompt,
        max_tokens=600,
        temperature=0.7,
        feature="chatbot",
    )

    if not ai_response:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI service returned no response. Please try again.",
        )

    logger.info(
        "Chatbot | user=%s | role=%s | type=%s | msg=%.80s",
        current_user.email, role, query_type, request.message,
    )

    return ChatResponse(
        response=ai_response,
        type=query_type,
        data=data,
        sql=sql,
        data_count=data_count,
    )


@router.get("/suggestions", response_model=SuggestionsResponse)
async def get_suggestions(
    current_user: User = Depends(get_current_user),
):
    """Return role-specific starter questions for the chatbot UI."""
    role = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    return SuggestionsResponse(
        suggestions=ROLE_SUGGESTIONS.get(role, []),
        role=role,
    )
