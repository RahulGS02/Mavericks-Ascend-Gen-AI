"""
AI Service - Anthropic Claude API Integration
Supports both Auggie SDK and Anthropic Claude API
Provider can be switched via AI_PROVIDER environment variable
"""
import json
import logging
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal
from app.config import settings

logger = logging.getLogger(__name__)

# Try to import Anthropic SDK
try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_SDK_AVAILABLE = True
    logger.info("✅ Anthropic SDK imported successfully")
except ImportError as e:
    ANTHROPIC_SDK_AVAILABLE = False
    logger.warning(f"⚠️  Anthropic SDK not available: {e}")
    AsyncAnthropic = None

# Try to import Auggie SDK
try:
    from auggie_sdk.context import DirectContext, File
    AUGGIE_SDK_AVAILABLE = True
    logger.info("✅ Auggie SDK imported successfully")
except ImportError as e:
    AUGGIE_SDK_AVAILABLE = False
    logger.warning(f"⚠️  Auggie SDK not available: {e}")
    DirectContext = None
    File = None

# Anthropic Pricing (as of May 2024)
ANTHROPIC_COST_PER_1M_INPUT_TOKENS = Decimal("3.00")    # $3.00 per 1M input tokens
ANTHROPIC_COST_PER_1M_OUTPUT_TOKENS = Decimal("15.00")  # $15.00 per 1M output tokens

# Auggie/Augment Pricing
AUGGIE_COST_PER_1K_INPUT_TOKENS = Decimal("0.003")   # $0.003 per 1K input tokens
AUGGIE_COST_PER_1K_OUTPUT_TOKENS = Decimal("0.015")  # $0.015 per 1K output tokens


class AIUsageTracker:
    """Track AI usage for cost control with detailed metrics"""

    def __init__(self):
        self.request_count = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.total_cost = Decimal("0.00")
        self.last_reset = datetime.utcnow()
        self.rate_limit_timestamps = []
        self.error_count = 0
        self.retry_count = 0
        self.requests_by_feature = {}
        self.daily_costs = []

    def check_rate_limit(self) -> bool:
        """Check if rate limit is exceeded"""
        now = datetime.utcnow()
        one_minute_ago = now - timedelta(minutes=1)
        
        self.rate_limit_timestamps = [
            ts for ts in self.rate_limit_timestamps
            if ts > one_minute_ago
        ]
        
        if len(self.rate_limit_timestamps) >= settings.AI_RATE_LIMIT_PER_MINUTE:
            logger.warning("AI rate limit exceeded")
            return False
        
        self.rate_limit_timestamps.append(now)
        return True

    def check_daily_limit(self) -> bool:
        """Check if daily request limit is exceeded"""
        if self.request_count >= settings.AI_DAILY_REQUEST_LIMIT:
            logger.warning("AI daily limit exceeded")
            return False
        return True

    def reset_if_needed(self):
        """Reset counters if a day has passed"""
        now = datetime.utcnow()
        if (now - self.last_reset).days >= 1:
            logger.info("Resetting AI usage tracker (24 hours elapsed)")
            self.__init__()

    def increment(
        self,
        input_tokens: int = 0,
        output_tokens: int = 0,
        feature: str = "general",
        provider: str = "anthropic"
    ):
        """Increment usage counters with cost calculation"""
        self.request_count += 1
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens

        # Calculate cost based on provider
        if provider == "anthropic":
            input_cost = (Decimal(input_tokens) / 1_000_000) * ANTHROPIC_COST_PER_1M_INPUT_TOKENS
            output_cost = (Decimal(output_tokens) / 1_000_000) * ANTHROPIC_COST_PER_1M_OUTPUT_TOKENS
        else:  # auggie
            input_cost = (Decimal(input_tokens) / 1000) * AUGGIE_COST_PER_1K_INPUT_TOKENS
            output_cost = (Decimal(output_tokens) / 1000) * AUGGIE_COST_PER_1K_OUTPUT_TOKENS
        
        request_cost = input_cost + output_cost
        self.total_cost += request_cost

        # Track by feature
        if feature not in self.requests_by_feature:
            self.requests_by_feature[feature] = {
                "count": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "cost": Decimal("0.00")
            }

        self.requests_by_feature[feature]["count"] += 1
        self.requests_by_feature[feature]["input_tokens"] += input_tokens
        self.requests_by_feature[feature]["output_tokens"] += output_tokens
        self.requests_by_feature[feature]["cost"] += request_cost

        logger.info(
            f"AI request tracked - Provider: {provider}, Feature: {feature}, "
            f"Input: {input_tokens} tokens, Output: {output_tokens} tokens, "
            f"Cost: ${request_cost:.6f}"
        )

    def increment_error(self):
        """Increment error counter"""
        self.error_count += 1

    def increment_retry(self):
        """Increment retry counter"""
        self.retry_count += 1


class AIServiceMultiProvider:
    """
    AI Service supporting multiple providers:
    - Anthropic Claude API (Recommended for production)
    - Auggie SDK (Alternative)

    Provider selection via AI_PROVIDER environment variable
    """

    def __init__(self):
        self.provider = settings.AI_PROVIDER
        self.tracker = AIUsageTracker()
        self.anthropic_client = None
        self.auggie_context = None

        logger.info(f"Initializing AI Service with provider: {self.provider}")

        # Initialize based on provider
        if self.provider == "anthropic":
            self._initialize_anthropic()
        elif self.provider == "auggie":
            self._initialize_auggie()
        else:
            logger.error(f"Unknown AI provider: {self.provider}")

    def _initialize_anthropic(self):
        """Initialize Anthropic Claude API client"""
        if not ANTHROPIC_SDK_AVAILABLE:
            logger.error("Anthropic SDK not available. Install with: pip install anthropic")
            return

        if not settings.ANTHROPIC_API_KEY:
            logger.error("ANTHROPIC_API_KEY not configured")
            return

        try:
            self.anthropic_client = AsyncAnthropic(
                api_key=settings.ANTHROPIC_API_KEY
            )
            logger.info("✅ Anthropic Claude API client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
            self.anthropic_client = None

    def _initialize_auggie(self):
        """Initialize Auggie SDK DirectContext"""
        if not AUGGIE_SDK_AVAILABLE:
            logger.error("Auggie SDK not available. Install with: pip install auggie-sdk")
            return

        if not settings.AI_API_KEY:
            logger.error("AI_API_KEY not configured for Auggie")
            return

        try:
            import ssl
            import urllib3
            import os

            # Disable SSL warnings
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            os.environ['CURL_CA_BUNDLE'] = ''
            os.environ['REQUESTS_CA_BUNDLE'] = ''
            _create_unverified_context = ssl._create_unverified_context
            ssl._create_default_https_context = _create_unverified_context

            self.auggie_context = DirectContext.create(
                api_key=settings.AI_API_KEY,
                api_url="https://e7.api.augmentcode.com/",
                debug=False
            )

            # Initialize index
            self.auggie_context.add_to_index([
                File(path='_init.txt', contents='Initialization placeholder')
            ])

            logger.info("✅ Auggie SDK DirectContext initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Auggie context: {e}")
            self.auggie_context = None

    async def is_available(self) -> bool:
        """Check if AI service is available"""
        if not settings.ai_features_enabled:
            return False

        if self.provider == "anthropic":
            return self.anthropic_client is not None
        elif self.provider == "auggie":
            return self.auggie_context is not None

        return False

    async def _call_ai(
        self,
        prompt: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None,
        feature: str = "general",
        max_retries: int = 3
    ) -> Optional[str]:
        """
        Call AI using configured provider
        """
        # Check rate limits
        if not self.tracker.check_rate_limit():
            logger.error("Rate limit exceeded")
            return None

        if not self.tracker.check_daily_limit():
            logger.error("Daily limit exceeded")
            return None

        # Route to appropriate provider
        if self.provider == "anthropic":
            return await self._call_anthropic(
                prompt, max_tokens, temperature, system_prompt, feature, max_retries
            )
        elif self.provider == "auggie":
            return await self._call_auggie(
                prompt, max_tokens, temperature, system_prompt, feature, max_retries
            )

        logger.error(f"Unknown provider: {self.provider}")
        return None

    async def _call_anthropic(
        self,
        prompt: str,
        max_tokens: Optional[int],
        temperature: Optional[float],
        system_prompt: Optional[str],
        feature: str,
        max_retries: int
    ) -> Optional[str]:
        """Call Anthropic Claude API"""
        if not self.anthropic_client:
            logger.error("Anthropic client not initialized")
            return None

        retry_count = 0
        last_error = None

        # Set defaults
        max_tokens = max_tokens or settings.ANTHROPIC_MAX_TOKENS
        temperature = temperature or settings.ANTHROPIC_TEMPERATURE

        while retry_count < max_retries:
            try:
                logger.info(f"Anthropic API call - Feature: {feature}, Attempt: {retry_count + 1}/{max_retries}")

                # Prepare messages
                messages = [{"role": "user", "content": prompt}]

                # Call Anthropic API
                response = await self.anthropic_client.messages.create(
                    model=settings.ANTHROPIC_MODEL,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt if system_prompt else "You are a helpful AI assistant.",
                    messages=messages
                )

                # Extract response text
                result_text = response.content[0].text

                # Track usage
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens

                self.tracker.increment(
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    feature=feature,
                    provider="anthropic"
                )

                logger.info(f"✅ Anthropic response received ({output_tokens} tokens)")
                return result_text

            except Exception as e:
                last_error = e
                retry_count += 1
                self.tracker.increment_retry()

                logger.error(f"Anthropic API error: {e}")

                if retry_count < max_retries:
                    wait_time = 2 ** retry_count
                    logger.warning(f"Retrying in {wait_time}s... (attempt {retry_count}/{max_retries})")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Anthropic API failed after {max_retries} retries")
                    self.tracker.increment_error()

        logger.error(f"Anthropic API failed after {max_retries} attempts. Last error: {last_error}")
        return None

    async def _call_auggie(
        self,
        prompt: str,
        max_tokens: Optional[int],
        temperature: Optional[float],
        system_prompt: Optional[str],
        feature: str,
        max_retries: int
    ) -> Optional[str]:
        """Call Auggie SDK DirectContext"""
        if not self.auggie_context:
            logger.error("Auggie context not initialized")
            return None

        retry_count = 0
        last_error = None

        # Combine system and user prompts
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        while retry_count < max_retries:
            try:
                logger.info(f"Auggie SDK call - Feature: {feature}, Attempt: {retry_count + 1}/{max_retries}")

                # Run in executor to avoid blocking
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.auggie_context.search_and_ask(
                        search_query="",
                        prompt=full_prompt
                    )
                )

                # Convert response to string if needed
                result_text = response if isinstance(response, str) else str(response)

                # Estimate token usage (approximate)
                input_tokens = len(full_prompt) // 4
                output_tokens = len(result_text) // 4

                self.tracker.increment(
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    feature=feature,
                    provider="auggie"
                )

                logger.info(f"✅ Auggie response received (~{output_tokens} tokens)")
                return result_text

            except Exception as e:
                last_error = e
                retry_count += 1
                self.tracker.increment_retry()

                logger.error(f"Auggie SDK error: {e}")

                if retry_count < max_retries:
                    wait_time = 2 ** retry_count
                    logger.warning(f"Retrying in {wait_time}s... (attempt {retry_count}/{max_retries})")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Auggie SDK failed after {max_retries} retries")
                    self.tracker.increment_error()

        logger.error(f"Auggie SDK failed after {max_retries} attempts. Last error: {last_error}")
        return None

    async def parse_resume_comprehensive(
        self,
        resume_text: str
    ) -> Optional[Dict[str, Any]]:
        """Parse resume and extract comprehensive information"""
        if not settings.AI_RESUME_PARSING_ENABLED:
            logger.warning("Resume parsing is disabled")
            return None

        system_prompt = """You are an expert resume parser. Extract structured information from resumes.
Return ONLY valid JSON with this exact structure:
{
    "personal_info": {"name": "...", "email": "...", "phone": "...", "location": "..."},
    "summary": "...",
    "experience": [{"title": "...", "company": "...", "duration": "...", "description": "..."}],
    "education": [{"degree": "...", "institution": "...", "year": "...", "gpa": "..."}],
    "skills": {"technical": [...], "soft": [...], "tools": [...]},
    "certifications": [...],
    "languages": [...]
}"""

        prompt = f"Parse this resume and extract all relevant information:\n\n{resume_text}"

        response = await self._call_ai(
            prompt=prompt,
            system_prompt=system_prompt,
            feature="resume_parsing",
            max_tokens=2000
        )

        if not response:
            return None

        try:
            # Parse JSON response
            parsed_data = json.loads(response)
            return parsed_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.debug(f"Response was: {response[:500]}")
            return None

    async def extract_skills_from_resume(
        self,
        resume_text: str
    ) -> Optional[List[Dict[str, Any]]]:
        """Extract skills with proficiency levels from resume"""
        if not settings.AI_SKILL_EXTRACTION_ENABLED:
            logger.warning("Skill extraction is disabled")
            return None

        system_prompt = """You are a skill extraction expert. Identify technical skills and estimate proficiency.
Return ONLY valid JSON array:
[
    {"name": "Python", "category": "Programming Language", "proficiency": 85, "years_experience": 3},
    {"name": "React", "category": "Framework", "proficiency": 70, "years_experience": 2}
]
Proficiency: 0-100 scale based on context clues."""

        prompt = f"Extract all skills with proficiency estimates:\n\n{resume_text}"

        response = await self._call_ai(
            prompt=prompt,
            system_prompt=system_prompt,
            feature="skill_extraction",
            max_tokens=1500
        )

        if not response:
            return None

        try:
            skills_data = json.loads(response)
            return skills_data if isinstance(skills_data, list) else []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse skills JSON: {e}")
            return []

    async def get_performance_insights(
        self,
        maverick_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate performance insights and recommendations"""
        if not settings.AI_PERFORMANCE_INSIGHTS_ENABLED:
            logger.warning("Performance insights are disabled")
            return None

        system_prompt = """You are a training performance analyst. Analyze trainee data and provide insights.
Return ONLY valid JSON:
{
    "overall_assessment": "...",
    "strengths": [...],
    "areas_for_improvement": [...],
    "recommendations": [...],
    "predicted_success_rate": 85,
    "suggested_projects": [...]
}"""

        prompt = f"Analyze this trainee's performance data:\n\n{json.dumps(maverick_data, indent=2)}"

        response = await self._call_ai(
            prompt=prompt,
            system_prompt=system_prompt,
            feature="performance_insights",
            max_tokens=1500
        )

        if not response:
            return None

        try:
            insights_data = json.loads(response)
            return insights_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse insights JSON: {e}")
            return None

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get detailed usage statistics"""
        self.tracker.reset_if_needed()

        return {
            "provider": self.provider,
            "request_count": self.tracker.request_count,
            "input_tokens": self.tracker.input_tokens,
            "output_tokens": self.tracker.output_tokens,
            "total_cost": float(self.tracker.total_cost),
            "error_count": self.tracker.error_count,
            "retry_count": self.tracker.retry_count,
            "last_reset": self.tracker.last_reset.isoformat(),
            "requests_by_feature": {
                feature: {
                    "count": stats["count"],
                    "input_tokens": stats["input_tokens"],
                    "output_tokens": stats["output_tokens"],
                    "cost": float(stats["cost"])
                }
                for feature, stats in self.tracker.requests_by_feature.items()
            }
        }


# Global instance
ai_service = AIServiceMultiProvider()
