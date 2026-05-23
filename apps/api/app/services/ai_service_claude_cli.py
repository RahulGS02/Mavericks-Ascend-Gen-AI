"""
AI Service - Claude CLI Integration for Local Testing
Supports Claude CLI programmatic mode for local development
When ready for production, switch to Anthropic API by changing AI_PROVIDER
"""
import json
import logging
import asyncio
import subprocess
import os
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal
from app.config import settings

logger = logging.getLogger(__name__)

# Check if Claude CLI is available
def check_claude_cli_available() -> bool:
    """Check if claude CLI is installed and accessible"""
    try:
        result = subprocess.run(
            ['claude', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

CLAUDE_CLI_AVAILABLE = check_claude_cli_available()
if CLAUDE_CLI_AVAILABLE:
    logger.info("✅ Claude CLI is available")
else:
    logger.warning("⚠️  Claude CLI not found. Install with: irm https://claude.ai/install.ps1 | iex")

# Claude CLI approximate costs (based on Pro subscription)
CLAUDE_CLI_COST_ESTIMATE = Decimal("0.005")  # ~$0.005 per request (rough estimate)


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
        provider: str = "claude_cli"
    ):
        """Increment usage counters with cost calculation"""
        self.request_count += 1
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens

        # For Claude CLI, use flat rate estimate per request
        request_cost = CLAUDE_CLI_COST_ESTIMATE
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


class AIServiceClaudeCLI:
    """
    AI Service using Claude CLI for local testing
    Uses programmatic mode (claude -p) for automation
    """

    def __init__(self):
        self.provider = "claude_cli"
        self.tracker = AIUsageTracker()
        self.cli_available = CLAUDE_CLI_AVAILABLE
        
        logger.info(f"Initializing AI Service with Claude CLI")
        logger.info(f"Claude CLI available: {self.cli_available}")
        
        # Set up environment for Claude CLI
        self._setup_environment()

    def _setup_environment(self):
        """Set up environment variables for Claude CLI"""
        # If token is provided, set it
        oauth_token = os.getenv("CLAUDE_CODE_OAUTH_TOKEN")
        if oauth_token:
            os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = oauth_token
            logger.info("✅ Using CLAUDE_CODE_OAUTH_TOKEN for authentication")
        else:
            logger.info("📝 Will use existing Claude CLI login credentials")

    async def is_available(self) -> bool:
        """Check if AI service is available"""
        if not settings.ai_features_enabled:
            return False
        return self.cli_available

    async def _call_claude_cli(
        self,
        prompt: str,
        max_retries: int = 3
    ) -> Optional[str]:
        """
        Call Claude CLI in programmatic mode
        Uses: claude -p --bare "prompt"
        """
        if not self.cli_available:
            logger.error("Claude CLI not available")
            return None

        retry_count = 0
        last_error = None

        while retry_count < max_retries:
            try:
                logger.info(f"Claude CLI call - Attempt: {retry_count + 1}/{max_retries}")

                # Prepare command
                # Use --bare mode for headless operation
                cmd = ['claude', '-p', '--bare', prompt]

                # Run Claude CLI
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=60,  # 60 second timeout
                        env=os.environ.copy()
                    )
                )

                if result.returncode != 0:
                    error_msg = result.stderr or result.stdout
                    logger.error(f"Claude CLI error: {error_msg}")
                    raise Exception(f"Claude CLI failed: {error_msg}")

                response_text = result.stdout.strip()

                if not response_text:
                    raise Exception("Empty response from Claude CLI")

                logger.info(f"✅ Claude CLI response received ({len(response_text)} chars)")
                return response_text

            except subprocess.TimeoutExpired:
                last_error = "Claude CLI timeout"
                retry_count += 1
                self.tracker.increment_retry()
                logger.error("Claude CLI timed out")

                if retry_count < max_retries:
                    logger.warning(f"Retrying... (attempt {retry_count}/{max_retries})")
                    await asyncio.sleep(2)

            except Exception as e:
                last_error = str(e)
                retry_count += 1
                self.tracker.increment_retry()
                logger.error(f"Claude CLI error: {e}")

                if retry_count < max_retries:
                    wait_time = 2 ** retry_count
                    logger.warning(f"Retrying in {wait_time}s... (attempt {retry_count}/{max_retries})")
                    await asyncio.sleep(wait_time)
                else:
                    self.tracker.increment_error()

        logger.error(f"Claude CLI failed after {max_retries} attempts. Last error: {last_error}")
        return None

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
        Main AI call method
        """
        # Check rate limits
        if not self.tracker.check_rate_limit():
            logger.error("Rate limit exceeded")
            return None

        if not self.tracker.check_daily_limit():
            logger.error("Daily limit exceeded")
            return None

        # Combine system and user prompts
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

        # Call Claude CLI
        response = await self._call_claude_cli(full_prompt, max_retries)

        if response:
            # Estimate token usage (approximate: 4 chars = 1 token)
            input_tokens = len(full_prompt) // 4
            output_tokens = len(response) // 4

            self.tracker.increment(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                feature=feature,
                provider="claude_cli"
            )

        return response

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
            feature="resume_parsing"
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
            feature="skill_extraction"
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
            feature="performance_insights"
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
ai_service = AIServiceClaudeCLI()
