"""
AI Service - Auggie SDK Integration
Handles all AI operations with cost control and feature flags
Uses DirectContext for headless authentication
"""
import json
import logging
import asyncio
import ssl
import urllib3
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from decimal import Decimal
from app.config import settings

logger = logging.getLogger(__name__)

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Disable SSL verification globally
import os
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

# Monkey patch SSL context
_create_unverified_context = ssl._create_unverified_context
ssl._create_default_https_context = _create_unverified_context

# Monkey patch requests.post to always disable SSL verification
import requests
_original_post = requests.post
_original_get = requests.get
_original_request = requests.request

def _patched_post(url, **kwargs):
    kwargs['verify'] = False
    return _original_post(url, **kwargs)

def _patched_get(url, **kwargs):
    kwargs['verify'] = False
    return _original_get(url, **kwargs)

def _patched_request(method, url, **kwargs):
    kwargs['verify'] = False
    return _original_request(method, url, **kwargs)

requests.post = _patched_post
requests.get = _patched_get
requests.request = _patched_request

logger.info("✅ SSL verification disabled globally for requests library")

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

# Cost per 1K tokens (update based on Auggie pricing)
COST_PER_1K_INPUT_TOKENS = Decimal("0.003")  # $0.003 per 1K input tokens
COST_PER_1K_OUTPUT_TOKENS = Decimal("0.015")  # $0.015 per 1K output tokens


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

        # Detailed tracking
        self.requests_by_feature = {}
        self.daily_costs = []

    def check_rate_limit(self) -> bool:
        """Check if rate limit is exceeded"""
        now = datetime.utcnow()
        one_minute_ago = now - timedelta(minutes=1)

        # Remove old timestamps
        self.rate_limit_timestamps = [
            ts for ts in self.rate_limit_timestamps
            if ts > one_minute_ago
        ]

        # Check limit
        if len(self.rate_limit_timestamps) >= settings.AI_RATE_LIMIT_PER_MINUTE:
            logger.warning("AI rate limit exceeded")
            return False

        self.rate_limit_timestamps.append(now)
        return True

    def check_daily_limit(self) -> bool:
        """Check if daily limit is exceeded"""
        now = datetime.utcnow()

        # Reset daily counter if needed
        if (now - self.last_reset).days >= 1:
            self.request_count = 0
            self.input_tokens = 0
            self.output_tokens = 0
            self.last_reset = now

        if self.request_count >= settings.AI_DAILY_REQUEST_LIMIT:
            logger.warning("AI daily limit exceeded")
            return False

        return True

    def increment(
        self,
        input_tokens: int = 0,
        output_tokens: int = 0,
        feature: str = "general"
    ):
        """Increment usage counters with cost calculation"""
        self.request_count += 1
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens

        # Calculate cost
        input_cost = (Decimal(input_tokens) / 1000) * COST_PER_1K_INPUT_TOKENS
        output_cost = (Decimal(output_tokens) / 1000) * COST_PER_1K_OUTPUT_TOKENS
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
            f"AI request tracked - Feature: {feature}, "
            f"Input: {input_tokens} tokens, Output: {output_tokens} tokens, "
            f"Cost: ${request_cost:.6f}"
        )

    def increment_error(self):
        """Increment error counter"""
        self.error_count += 1

    def increment_retry(self):
        """Increment retry counter"""
        self.retry_count += 1


class AIService:
    """
    AI Service using Auggie SDK DirectContext

    Uses DirectContext for headless authentication (CI/CD compatible)
    Falls back to None if SDK unavailable or initialization fails
    """

    def __init__(self):
        self.api_key = settings.AI_API_KEY
        self.model = settings.AI_MODEL
        self.tenant_url = "https://e7.api.augmentcode.com/"  # Auggie tenant URL
        self.tracker = AIUsageTracker()
        self.context = None

        # Initialize DirectContext if SDK is available
        if AUGGIE_SDK_AVAILABLE and self.api_key:
            self._initialize_direct_context()

    def _initialize_direct_context(self):
        """Initialize Auggie DirectContext for headless authentication"""
        try:
            logger.info("Initializing DirectContext for headless authentication...")
            logger.info(f"API URL: {self.tenant_url}")
            logger.info(f"API Key: {self.api_key[:20]}...")

            # Create DirectContext with SSL verification disabled
            try:
                # Try with verify parameter if supported
                self.context = DirectContext.create(
                    api_key=self.api_key,
                    api_url=self.tenant_url,
                    debug=False,
                    verify=False  # Disable SSL verification
                )
            except TypeError:
                # If verify parameter not supported, try without it
                logger.info("DirectContext doesn't support verify parameter, using global SSL settings")
                self.context = DirectContext.create(
                    api_key=self.api_key,
                    api_url=self.tenant_url,
                    debug=False
                )

            logger.info("DirectContext created successfully")

            # Initialize index with placeholder (required before using search_and_ask)
            logger.info("Initializing index with placeholder...")
            self.context.add_to_index([
                File(path='_init.txt', contents='Initialization placeholder for DirectContext')
            ])

            logger.info("✅ DirectContext initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize DirectContext: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            logger.warning("AI service will be unavailable")
            self.context = None
    
    async def is_available(self) -> bool:
        """Check if AI service is available"""
        if not settings.ai_features_enabled:
            logger.info("AI features are disabled")
            return False

        if not self.api_key:
            logger.warning("AI API key not configured")
            return False

        if not AUGGIE_SDK_AVAILABLE:
            logger.warning("Auggie SDK not available")
            return False

        if not self.context:
            logger.warning("DirectContext not initialized")
            return False

        return True
    
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
        Call AI using Auggie SDK DirectContext

        Uses search_and_ask method with DirectContext for headless authentication
        """

        # Check rate limits
        if not self.tracker.check_rate_limit():
            logger.error("Rate limit exceeded, AI request blocked")
            return None

        if not self.tracker.check_daily_limit():
            logger.error("Daily limit exceeded, AI request blocked")
            return None

        if not self.context:
            logger.error("DirectContext not initialized")
            return None

        retry_count = 0
        last_error = None

        while retry_count < max_retries:
            try:
                logger.info(f"AI request - Feature: {feature}, Attempt: {retry_count + 1}/{max_retries}")

                # Combine system prompt and user prompt
                full_prompt = prompt
                if system_prompt:
                    full_prompt = f"{system_prompt}\n\n{prompt}"

                # Use search_and_ask (synchronous method from Auggie SDK)
                # Signature: search_and_ask(search_query: str, prompt: Optional[str] = None)
                # Run in executor to not block async
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.context.search_and_ask(
                        search_query="",  # Empty search query - we just want LLM response
                        prompt=full_prompt
                    )
                )

                # Extract text from response
                if hasattr(response, 'answer'):
                    result_text = response.answer
                elif isinstance(response, str):
                    result_text = response
                else:
                    result_text = str(response)

                # Estimate token usage (rough estimation: 1 token ≈ 4 characters)
                input_tokens = len(full_prompt) // 4
                output_tokens = len(result_text) // 4

                # Track usage
                self.tracker.increment(
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    feature=feature
                )

                logger.info(f"✅ AI response received ({output_tokens} tokens)")
                return result_text

            except Exception as e:
                last_error = e
                retry_count += 1
                self.tracker.increment_retry()

                logger.error(f"AI request error: {e}")

                if retry_count < max_retries:
                    wait_time = 2 ** retry_count  # Exponential backoff
                    logger.warning(
                        f"Retrying in {wait_time}s... (attempt {retry_count}/{max_retries})"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"AI request failed after {max_retries} retries")
                    self.tracker.increment_error()

        # All retries exhausted
        logger.error(f"AI request failed after {max_retries} attempts. Last error: {last_error}")
        return None

    async def extract_skills_from_resume(self, resume_text: str) -> List[str]:
        """
        Extract technical skills from resume text

        Feature Flag: AI_SKILL_EXTRACTION_ENABLED
        """
        if not await self.is_available():
            logger.info("AI not available, skipping skill extraction")
            return []

        if not settings.AI_SKILL_EXTRACTION_ENABLED:
            logger.info("Skill extraction feature is disabled")
            return []

        prompt = f"""
Extract all technical skills from the following resume text.
Return ONLY a valid JSON array of skill strings, nothing else.

Example output: ["Python", "React", "SQL", "Docker"]

Resume Text:
{resume_text[:3000]}

Skills (JSON array only):
"""

        system_prompt = "You are a technical recruiter expert at identifying skills from resumes. Always return valid JSON."

        result = await self._call_ai(
            prompt=prompt,
            max_tokens=500,
            temperature=0.3,
            system_prompt=system_prompt,
            feature="skill_extraction"
        )

        if not result:
            return []

        try:
            # Parse JSON response
            skills = json.loads(result.strip())
            if isinstance(skills, list):
                return [str(skill).strip() for skill in skills if skill]
            return []
        except json.JSONDecodeError:
            logger.error(f"Failed to parse AI response as JSON: {result}")
            return []

    async def generate_profile_summary(self, profile_data: Dict[str, Any]) -> Optional[str]:
        """
        Generate a professional summary for a maverick profile

        Feature Flag: AI_PERFORMANCE_INSIGHTS_ENABLED
        """
        if not await self.is_available():
            logger.info("AI not available, skipping profile summary")
            return None

        if not settings.AI_PERFORMANCE_INSIGHTS_ENABLED:
            logger.info("Profile summary feature is disabled")
            return None

        prompt = f"""
Create a concise, professional 2-3 sentence summary for this candidate profile.
Focus on their strengths, educational background, and potential.

Candidate Details:
- Name: {profile_data.get('name', 'Unknown')}
- Education: {profile_data.get('degree', '')} in {profile_data.get('branch', '')}
- College: {profile_data.get('college', '')}
- CGPA: {profile_data.get('cgpa', 'N/A')}
- Skills: {', '.join(profile_data.get('skills', [])[:10])}
- Graduation Year: {profile_data.get('graduation_year', '')}

Professional Summary:
"""

        system_prompt = "You are a professional HR recruiter writing candidate summaries. Keep it concise and positive."

        return await self._call_ai(
            prompt=prompt,
            max_tokens=200,
            temperature=0.7,
            system_prompt=system_prompt,
            feature="profile_summary"
        )

    async def parse_resume_comprehensive(self, resume_text: str) -> Dict[str, Any]:
        """
        Comprehensive resume parsing with all details

        Feature Flag: AI_RESUME_PARSING_ENABLED

        Returns:
            {
                "personal_info": {...},
                "education": [...],
                "experience": [...],
                "skills": {...},
                "projects": [...],
                "summary": str,
                "total_experience_years": float
            }
        """
        if not await self.is_available():
            logger.info("AI not available, skipping resume parsing")
            return {}

        if not settings.AI_RESUME_PARSING_ENABLED:
            logger.info("Resume parsing feature is disabled")
            return {}

        prompt = f"""
You are an expert resume parser. Extract ALL information from this resume and return ONLY valid JSON.

Resume Text:
{resume_text[:6000]}

Return this exact JSON structure:
{{
  "personal_info": {{
    "name": "string",
    "email": "string or null",
    "phone": "string or null",
    "location": "string or null",
    "linkedin": "string or null",
    "github": "string or null",
    "portfolio": "string or null"
  }},
  "education": [
    {{
      "degree": "string (B.Tech, M.Tech, etc.)",
      "branch": "string (CSE, IT, etc.)",
      "college": "string",
      "university": "string or null",
      "year": "int (graduation year)",
      "cgpa": "float or null",
      "percentage": "float or null"
    }}
  ],
  "experience": [
    {{
      "company": "string",
      "role": "string",
      "duration": "string (e.g., Jan 2020 - Dec 2021)",
      "years": "float (duration in years)",
      "location": "string or null",
      "description": "string",
      "technologies": ["array of strings"]
    }}
  ],
  "skills": {{
    "technical": ["array of technical skills"],
    "soft_skills": ["array of soft skills"],
    "languages": ["programming languages"],
    "frameworks": ["frameworks and libraries"],
    "tools": ["tools and platforms"],
    "databases": ["databases"]
  }},
  "projects": [
    {{
      "name": "string",
      "description": "string",
      "technologies": ["array of strings"],
      "role": "string or null",
      "duration": "string or null",
      "url": "string or null"
    }}
  ],
  "certifications": [
    {{
      "name": "string",
      "issuer": "string or null",
      "year": "int or null"
    }}
  ],
  "total_experience_years": "float (total years of professional experience)",
  "summary": "string (2-3 sentence professional summary)"
}}

Important:
- Extract ALL information present in the resume
- Return valid JSON only, no markdown or extra text
- Use null for missing information
- Calculate total experience years from all work experience
- Identify and categorize skills properly
"""

        system_prompt = "You are an expert resume parser. Always return valid, complete JSON with all extracted information."

        result = await self._call_ai(
            prompt=prompt,
            max_tokens=2000,
            temperature=0.2,
            system_prompt=system_prompt,
            feature="resume_parsing"
        )

        if not result:
            return {}

        try:
            # Clean the result (remove markdown code blocks if present)
            cleaned_result = result.strip()
            if cleaned_result.startswith("```json"):
                cleaned_result = cleaned_result[7:]
            if cleaned_result.startswith("```"):
                cleaned_result = cleaned_result[3:]
            if cleaned_result.endswith("```"):
                cleaned_result = cleaned_result[:-3]

            parsed_data = json.loads(cleaned_result.strip())

            # Validate structure
            if isinstance(parsed_data, dict):
                logger.info("Successfully parsed resume with comprehensive details")
                return parsed_data
            else:
                logger.error("Parsed data is not a dictionary")
                return {}

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse resume data as JSON: {e}")
            logger.error(f"Result was: {result[:200]}")
            return {}

    async def get_performance_insights(
        self,
        assessment_data: Dict[str, Any],
        job_progress: Dict[str, Any]
    ) -> Optional[str]:
        """
        Generate performance insights for a maverick

        Feature Flag: AI_PERFORMANCE_INSIGHTS_ENABLED
        """
        if not await self.is_available():
            logger.info("AI not available, skipping performance insights")
            return None

        if not settings.AI_PERFORMANCE_INSIGHTS_ENABLED:
            logger.info("Performance insights feature is disabled")
            return None

        prompt = f"""
Analyze this candidate's performance and provide actionable insights and recommendations.

Assessment Data:
- Total Assessments: {assessment_data.get('total_assessments', 0)}
- Passed: {assessment_data.get('passed', 0)}
- Average Score: {assessment_data.get('average_score', 0)}%
- Strengths: {', '.join(assessment_data.get('strengths', []))}
- Areas for Improvement: {', '.join(assessment_data.get('weaknesses', []))}

Job Progress:
- Completed Jobs: {job_progress.get('completed', 0)}/{job_progress.get('total', 0)}
- Overall Completion: {job_progress.get('completion_percentage', 0)}%
- Current Status: {job_progress.get('status', 'Unknown')}

Provide:
1. Overall performance summary (2-3 sentences)
2. Top 3 strengths
3. Top 3 areas for improvement
4. 2-3 actionable recommendations

Insights:
"""

        system_prompt = "You are an experienced training manager providing constructive performance feedback."

        return await self._call_ai(
            prompt=prompt,
            max_tokens=800,
            temperature=0.7,
            system_prompt=system_prompt,
            feature="performance_insights"
        )

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current AI usage statistics"""
        return {
            "requests_today": self.tracker.request_count,
            "input_tokens": self.tracker.input_tokens,
            "output_tokens": self.tracker.output_tokens,
            "total_tokens": self.tracker.input_tokens + self.tracker.output_tokens,
            "total_cost_usd": float(self.tracker.total_cost),
            "daily_limit": settings.AI_DAILY_REQUEST_LIMIT,
            "rate_limit_per_minute": settings.AI_RATE_LIMIT_PER_MINUTE,
            "error_count": self.tracker.error_count,
            "retry_count": self.tracker.retry_count,
            "last_reset": self.tracker.last_reset.isoformat(),
            "requests_by_feature": {
                feature: {
                    "count": stats["count"],
                    "input_tokens": stats["input_tokens"],
                    "output_tokens": stats["output_tokens"],
                    "total_tokens": stats["input_tokens"] + stats["output_tokens"],
                    "cost_usd": float(stats["cost"])
                }
                for feature, stats in self.tracker.requests_by_feature.items()
            }
        }

    def get_detailed_stats(self) -> Dict[str, Any]:
        """Get detailed AI statistics for super admin"""
        basic_stats = self.get_usage_stats()

        # Calculate additional metrics
        total_tokens = basic_stats["total_tokens"]
        avg_tokens_per_request = (
            total_tokens / basic_stats["requests_today"]
            if basic_stats["requests_today"] > 0
            else 0
        )

        error_rate = (
            (basic_stats["error_count"] / basic_stats["requests_today"] * 100)
            if basic_stats["requests_today"] > 0
            else 0
        )

        return {
            **basic_stats,
            "avg_tokens_per_request": round(avg_tokens_per_request, 2),
            "error_rate_percentage": round(error_rate, 2),
            "cost_per_request_usd": (
                float(self.tracker.total_cost / self.tracker.request_count)
                if self.tracker.request_count > 0
                else 0
            ),
            "cost_breakdown": {
                "input_cost_usd": float(
                    (Decimal(self.tracker.input_tokens) / 1000) * COST_PER_1K_INPUT_TOKENS
                ),
                "output_cost_usd": float(
                    (Decimal(self.tracker.output_tokens) / 1000) * COST_PER_1K_OUTPUT_TOKENS
                )
            }
        }


# Global AI service instance
ai_service = AIService()
