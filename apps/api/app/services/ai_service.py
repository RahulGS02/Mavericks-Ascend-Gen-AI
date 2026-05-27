"""
AI Service — Provider Router
============================
Single import point for the whole application.

All routers and services import:
    from app.services.ai_service import ai_service   # unchanged import

Provider is selected at startup via the AI_PROVIDER env var:

  AI_PROVIDER=azure       -> Azure AI Foundry  (gpt-4o-mini)  <- DEFAULT
  AI_PROVIDER=anthropic   -> Anthropic Claude API
  AI_PROVIDER=claude_cli  -> Claude CLI subprocess (local dev)
  AI_PROVIDER=auggie      -> Auggie SDK (legacy)
"""

import logging
from app.config import settings

logger = logging.getLogger(__name__)

_provider = settings.AI_PROVIDER.lower()
logger.info("AI provider selected: %s", _provider)

# -- Azure AI Foundry (primary) -----------------------------------------------
if _provider == "azure":
    try:
        from app.services.ai_service_azure import AIServiceAzure
        ai_service = AIServiceAzure()
        logger.info("Using Azure AI Foundry service (model: %s)", settings.AZURE_AI_MODEL)
    except Exception as exc:
        logger.error("Failed to load Azure AI service: %s -- falling back to stub", exc)
        ai_service = None

# -- Anthropic Claude API ------------------------------------------------------
elif _provider == "anthropic":
    try:
        from app.services.ai_service_anthropic import AIServiceMultiProvider
        ai_service = AIServiceMultiProvider()
        logger.info("Using Anthropic AI service (model: %s)", settings.ANTHROPIC_MODEL)
    except Exception as exc:
        logger.error("Failed to load Anthropic AI service: %s", exc)
        ai_service = None

# -- Claude CLI (local dev only) -----------------------------------------------
elif _provider == "claude_cli":
    try:
        from app.services.ai_service_claude_cli import AIServiceClaudeCLI
        ai_service = AIServiceClaudeCLI()
        logger.info("Using Claude CLI service")
    except Exception as exc:
        logger.error("Failed to load Claude CLI service: %s", exc)
        ai_service = None

# -- Auggie SDK (legacy) -------------------------------------------------------
elif _provider == "auggie":
    try:
        from app.services.ai_service_anthropic import AIServiceMultiProvider
        ai_service = AIServiceMultiProvider()
        logger.info("Using Auggie-compatible Anthropic multi-provider")
    except Exception as exc:
        logger.warning("Could not load any AI provider: %s", exc)
        ai_service = None

# -- Unknown provider ----------------------------------------------------------
else:
    logger.error(
        "Unknown AI_PROVIDER=%r. Valid: azure | anthropic | claude_cli | auggie",
        _provider,
    )
    ai_service = None

# -- Null-safety guard ---------------------------------------------------------
if ai_service is None:
    logger.warning(
        "ai_service is None -- all AI calls will be no-ops. "
        "Set AI_PROVIDER and credentials in .env to activate."
    )
