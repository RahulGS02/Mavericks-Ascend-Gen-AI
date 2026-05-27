"""
AI Service — Azure AI Foundry via OpenAI-compatible SDK
========================================================

Endpoint (project name = proj-default-ai):
  base_url = "https://mavericks-ai.services.ai.azure.com/api/projects/proj-default-ai/openai/v1/"

SDK pattern (exactly as Azure sample shows):
  client = OpenAI(base_url=endpoint, api_key=api_key)
  client.chat.completions.create(model="gpt-4.1-mini", messages=[...])

Uses AsyncOpenAI (async version of the sample's OpenAI) with base_url.
No AzureOpenAI, no api_version, no custom headers needed.

Pricing (gpt-4.1-mini, Azure AI Foundry, 2025):
  $0.40 / 1M input tokens
  $1.60 / 1M output tokens

Supported features (same public interface as old Auggie service):
  is_available()                  -> bool
  _call_ai(prompt, ...)           -> Optional[str]
  parse_resume_comprehensive()    -> Dict
  extract_skills_from_resume()    -> List[str]
  get_performance_insights()      -> Optional[str]
  generate_profile_summary()      -> Optional[str]
  get_usage_stats()               -> Dict
  get_detailed_stats()            -> Dict
"""

from __future__ import annotations

import json
import logging
import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from app.config import settings

logger = logging.getLogger(__name__)

# ── OpenAI SDK ──────────────────────────────────────────────────────────────
try:
    from openai import AsyncOpenAI, APIConnectionError, APIStatusError, RateLimitError
    OPENAI_SDK_AVAILABLE = True
    logger.info("openai SDK imported successfully")
except ImportError:
    OPENAI_SDK_AVAILABLE = False
    AsyncOpenAI = None          # type: ignore[assignment,misc]
    APIConnectionError = APIStatusError = RateLimitError = Exception  # type: ignore[misc]
    logger.warning("openai package not installed. Run: pip install openai>=1.60.0")

# ── Pricing (gpt-4.1-mini) ───────────────────────────────────────────────────
_COST_PER_1M_INPUT  = Decimal("0.40")   # $0.40 / 1M input tokens
_COST_PER_1M_OUTPUT = Decimal("1.60")   # $1.60 / 1M output tokens


def _base_url(raw: str) -> str:
    """
    Ensure the endpoint ends with a trailing slash for the openai SDK.
    The SDK appends /chat/completions; it needs the slash to resolve correctly.

    "https://mavericks-ai.services.ai.azure.com/openai/v1"
      -> "https://mavericks-ai.services.ai.azure.com/openai/v1/"
    """
    return raw.rstrip("/") + "/"


# ── Usage tracker ─────────────────────────────────────────────────────────────

class _UsageTracker:
    def __init__(self) -> None:
        self.request_count: int = 0
        self.input_tokens: int = 0
        self.output_tokens: int = 0
        self.total_cost: Decimal = Decimal("0.00")
        self.last_reset: datetime = datetime.utcnow()
        self._rate_ts: List[datetime] = []
        self.error_count: int = 0
        self.retry_count: int = 0
        self.by_feature: Dict[str, Dict[str, Any]] = {}

    def check_rate_limit(self) -> bool:
        now = datetime.utcnow()
        self._rate_ts = [t for t in self._rate_ts if t > now - timedelta(minutes=1)]
        if len(self._rate_ts) >= settings.AI_RATE_LIMIT_PER_MINUTE:
            logger.warning("AI rate limit exceeded (%d/min)", settings.AI_RATE_LIMIT_PER_MINUTE)
            return False
        self._rate_ts.append(now)
        return True

    def check_daily_limit(self) -> bool:
        if (datetime.utcnow() - self.last_reset).days >= 1:
            self.__init__()
        if self.request_count >= settings.AI_DAILY_REQUEST_LIMIT:
            logger.warning("AI daily request limit exceeded")
            return False
        return True

    def record(self, in_tok: int, out_tok: int, feature: str) -> None:
        self.request_count += 1
        self.input_tokens  += in_tok
        self.output_tokens += out_tok
        cost = (
            (Decimal(in_tok)  / 1_000_000) * _COST_PER_1M_INPUT
          + (Decimal(out_tok) / 1_000_000) * _COST_PER_1M_OUTPUT
        )
        self.total_cost += cost
        b = self.by_feature.setdefault(
            feature,
            {"count": 0, "input_tokens": 0, "output_tokens": 0, "cost": Decimal("0.00")},
        )
        b["count"]         += 1
        b["input_tokens"]  += in_tok
        b["output_tokens"] += out_tok
        b["cost"]          += cost
        logger.info(
            "Azure AI -- feature=%-22s  in=%5d  out=%4d  $%.6f",
            feature, in_tok, out_tok, cost,
        )


# ── Main service ──────────────────────────────────────────────────────────────

class AIServiceAzure:
    """
    Azure AI Foundry service — drop-in replacement for the Auggie SDK service.
    Same public interface; zero changes needed in callers.
    """

    def __init__(self) -> None:
        self._tracker     = _UsageTracker()
        self._client: Optional[AsyncOpenAI] = None
        self._base_url    = _base_url(settings.AZURE_AI_ENDPOINT)
        self._model       = settings.AZURE_AI_MODEL        # gpt-4.1-mini
        self._api_version = settings.AZURE_AI_API_VERSION  # 2025-01-01-preview
        self._max_tok     = settings.AZURE_AI_MAX_TOKENS
        self._temp        = settings.AZURE_AI_TEMPERATURE

        logger.info(
            "Azure AI Foundry -- base_url=%s  model=%s  api_version=%s",
            self._base_url, self._model, self._api_version,
        )

        if OPENAI_SDK_AVAILABLE and settings.AZURE_AI_API_KEY:
            self._init_client()
        else:
            logger.warning(
                "Azure AI client NOT initialised -- "
                "AZURE_AI_API_KEY missing or openai SDK not installed"
            )

    def _init_client(self) -> None:
        try:
            # Confirmed by test probe:
            # - No api-version query param needed (v1 project endpoint is OpenAI-compatible)
            # - Auth: api-key header (set via default_headers)
            self._client = AsyncOpenAI(
                base_url=self._base_url,
                api_key=settings.AZURE_AI_API_KEY,
                default_headers={"api-key": settings.AZURE_AI_API_KEY},
            )
            logger.info("Azure AI client ready (base_url=%s)", self._base_url)
        except Exception as exc:
            logger.error("Failed to create AsyncOpenAI client: %s", exc)
            self._client = None

    # ── health ────────────────────────────────────────────────────────────────

    async def is_available(self) -> bool:
        if not settings.ai_features_enabled:
            return False
        if not OPENAI_SDK_AVAILABLE:
            logger.warning("openai SDK not installed")
            return False
        if self._client is None:
            logger.warning("Azure AI client not initialised")
            return False
        return True

    # ── core LLM call ─────────────────────────────────────────────────────────

    async def _call_ai(
        self,
        prompt: str,
        *,
        max_tokens: Optional[int]    = None,
        temperature: Optional[float] = None,
        system_prompt: Optional[str] = None,
        feature: str                 = "general",
        max_retries: int             = 3,
    ) -> Optional[str]:
        if not await self.is_available():
            logger.error("AI not available -- skipping call (feature=%s)", feature)
            return None
        if not self._tracker.check_rate_limit():
            return None
        if not self._tracker.check_daily_limit():
            return None

        _max = max_tokens  if max_tokens  is not None else self._max_tok
        _tmp = temperature if temperature is not None else self._temp

        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(
                    "Azure AI call -- feature=%s  attempt=%d/%d",
                    feature, attempt, max_retries,
                )
                resp = await self._client.chat.completions.create(
                    model=self._model,
                    messages=messages,
                    temperature=_tmp,
                    max_tokens=_max,
                )
                text    = resp.choices[0].message.content or ""
                in_tok  = resp.usage.prompt_tokens
                out_tok = resp.usage.completion_tokens
                self._tracker.record(in_tok, out_tok, feature)
                self._log_to_db(in_tok, out_tok, feature, "SUCCESS")
                logger.info("Azure AI response -- out_tokens=%d", out_tok)
                return text

            except RateLimitError:
                self._tracker.retry_count += 1
                wait = 2 ** attempt
                logger.warning("Rate limit -- retrying in %ds (%d/%d)", wait, attempt, max_retries)
                if attempt < max_retries:
                    await asyncio.sleep(wait)
                else:
                    self._tracker.error_count += 1

            except APIStatusError as exc:
                self._tracker.retry_count += 1
                logger.error(
                    "Azure AI API error %d: %s (%d/%d)",
                    exc.status_code, exc.message, attempt, max_retries,
                )
                if attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)
                else:
                    self._tracker.error_count += 1

            except APIConnectionError as exc:
                self._tracker.retry_count += 1
                logger.error("Azure AI connection error: %s (%d/%d)", exc, attempt, max_retries)
                if attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)
                else:
                    self._tracker.error_count += 1

            except Exception as exc:
                self._tracker.retry_count += 1
                logger.error("Unexpected AI error: %s (%d/%d)", exc, attempt, max_retries)
                if attempt < max_retries:
                    await asyncio.sleep(2 ** attempt)
                else:
                    self._tracker.error_count += 1

        return None

    # ── Feature: chatbot (multi-turn conversation) ────────────────────────────

    async def chat_with_history(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        max_tokens: int = 800,
        temperature: float = 0.7,
        feature: str = "chatbot",
    ) -> Optional[str]:
        """
        Multi-turn chat: accepts a full conversation history as a list of
        {"role": "user"|"assistant", "content": "..."} dicts.
        The system_prompt is prepended as the first system message.
        """
        if not await self.is_available():
            return None
        if not self._tracker.check_rate_limit():
            return None
        if not self._tracker.check_daily_limit():
            return None

        full_messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            *messages,
        ]

        for attempt in range(1, 4):
            try:
                resp = await self._client.chat.completions.create(
                    model=self._model,
                    messages=full_messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                text    = resp.choices[0].message.content or ""
                in_tok  = resp.usage.prompt_tokens
                out_tok = resp.usage.completion_tokens
                self._tracker.record(in_tok, out_tok, feature)
                self._log_to_db(in_tok, out_tok, feature, "SUCCESS")
                return text
            except (RateLimitError, APIStatusError, APIConnectionError, Exception) as exc:
                self._tracker.retry_count += 1
                logger.warning("chat_with_history attempt %d failed: %s", attempt, exc)
                if attempt < 3:
                    import asyncio
                    await asyncio.sleep(2 ** attempt)
                else:
                    self._tracker.error_count += 1
                    self._log_to_db(0, 0, feature, "ERROR", str(exc)[:500])
        return None

    # ── Feature: resume parsing ───────────────────────────────────────────────

    async def parse_resume_comprehensive(self, resume_text: str) -> Dict[str, Any]:
        if not settings.AI_RESUME_PARSING_ENABLED:
            return {}
        prompt = f"""Extract ALL information from this resume. Return ONLY valid JSON.

Resume Text:
{resume_text[:6000]}

Return this exact JSON structure (use null for missing fields):
{{
  "personal_info": {{
    "name": "string", "email": "string or null", "phone": "string or null",
    "location": "string or null", "linkedin": "string or null",
    "github": "string or null", "portfolio": "string or null"
  }},
  "education": [{{
    "degree": "string", "branch": "string", "college": "string",
    "university": "string or null", "year": "int", "cgpa": "float or null",
    "percentage": "float or null"
  }}],
  "experience": [{{
    "company": "string", "role": "string", "duration": "string",
    "years": "float", "location": "string or null",
    "description": "string", "technologies": ["array"]
  }}],
  "skills": {{
    "technical": ["array"], "soft_skills": ["array"],
    "languages": ["array"], "frameworks": ["array"],
    "tools": ["array"], "databases": ["array"]
  }},
  "projects": [{{
    "name": "string", "description": "string", "technologies": ["array"],
    "role": "string or null", "duration": "string or null", "url": "string or null"
  }}],
  "certifications": [{{"name": "string", "issuer": "string or null", "year": "int or null"}}],
  "total_experience_years": "float",
  "summary": "2-3 sentence professional summary"
}}"""
        result = await self._call_ai(
            prompt=prompt,
            system_prompt="You are an expert resume parser. Return ONLY valid JSON -- no markdown fences, no explanation.",
            max_tokens=2000,
            temperature=0.2,
            feature="resume_parsing",
        )
        return self._parse_json(result, feature="resume_parsing") or {}

    # ── Feature: skill extraction ─────────────────────────────────────────────

    async def extract_skills_from_resume(self, resume_text: str) -> List[str]:
        if not settings.AI_SKILL_EXTRACTION_ENABLED:
            return []
        prompt = f"""Extract all technical skills from this resume.
Return ONLY a JSON array of strings -- e.g. ["Python", "React", "SQL", "Docker"]

Resume:
{resume_text[:3000]}"""
        result = await self._call_ai(
            prompt=prompt,
            system_prompt="You are a technical recruiter. Return ONLY a valid JSON array of skill strings.",
            max_tokens=500,
            temperature=0.3,
            feature="skill_extraction",
        )
        if not result:
            return []
        parsed = self._parse_json(result, feature="skill_extraction")
        if isinstance(parsed, list):
            return [str(s).strip() for s in parsed if s]
        return []

    # ── Feature: profile summary ──────────────────────────────────────────────

    async def generate_profile_summary(self, profile_data: Dict[str, Any]) -> Optional[str]:
        if not settings.AI_PERFORMANCE_INSIGHTS_ENABLED:
            return None
        prompt = f"""Write a concise 2-3 sentence professional summary for this candidate.

Name: {profile_data.get('name', 'Unknown')}
Education: {profile_data.get('degree', '')} in {profile_data.get('branch', '')} from {profile_data.get('college', '')}
CGPA: {profile_data.get('cgpa', 'N/A')}
Skills: {', '.join(profile_data.get('skills', [])[:10])}
Graduation Year: {profile_data.get('graduation_year', '')}

Professional Summary:"""
        return await self._call_ai(
            prompt=prompt,
            system_prompt="You are a professional HR recruiter writing candidate summaries. Be concise and positive.",
            max_tokens=200,
            temperature=0.7,
            feature="profile_summary",
        )

    # ── Feature: natural language → SQL ──────────────────────────────────────

    async def generate_sql_from_natural_language(
        self,
        natural_query: str,
        schema_context: str,
        intended_limit: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Convert a natural language query into a safe PostgreSQL SELECT statement.

        Args:
            natural_query:  Human-readable query description.
            schema_context: Full DB schema context string from schema_provider.
            intended_limit: Row count extracted from the natural language
                            (e.g. 10 for "Top 10 students"). When provided the
                            AI is explicitly told to use LIMIT <intended_limit>.

        Returns:
            Dict with keys ``sql``, ``explanation``, ``tables_used``,
            or None if the AI call fails or the service is unavailable.
        """
        if intended_limit:
            # User explicitly asked for a specific count — enforce it hard
            limit_instruction = (
                f"CRITICAL: The user asked for exactly {intended_limit} rows. "
                f"You MUST use LIMIT {intended_limit} in the outermost SELECT. "
                f"Do NOT use a higher LIMIT."
            )
            limit_rule4 = (
                f"4. The outermost SELECT MUST end with LIMIT {intended_limit} — "
                f"exactly the count the user requested. No other LIMIT value is acceptable.\n"
            )
        else:
            # No specific count requested — return ALL matching records.
            # The system will add a safety cap of 1000 automatically via sanitize_sql_query().
            limit_instruction = (
                "The user did NOT specify a row limit. "
                "Do NOT add an arbitrary LIMIT clause to the SQL. "
                "Return ALL records that satisfy the query conditions. "
                "The system will enforce a maximum safety cap of 1000 rows automatically."
            )
            limit_rule4 = (
                "4. Do NOT add an arbitrary LIMIT clause. "
                "Only include LIMIT when the user explicitly asked for a specific number of rows. "
                "The system handles result-set capping automatically.\n"
            )

        system_prompt = (
            "You are an expert PostgreSQL database analyst. "
            "Convert natural language to valid, safe PostgreSQL SELECT statements.\n\n"
            "STRICT RULES — follow every one:\n"
            "1. Return ONLY valid JSON — no markdown fences, no prose outside JSON.\n"
            "2. ONLY generate SELECT statements. NEVER INSERT/UPDATE/DELETE/DROP/TRUNCATE.\n"
            "3. NEVER include SQL comments (-- or /* */) inside the SQL string.\n"
            + limit_rule4 +
            "5. AVOID JOIN INFLATION: when the question is about 'students', 'mavericks', "
            "   or 'candidates' (one row per person), do NOT JOIN maverick_skills — instead "
            "   use the `skills` JSONB column (e.g. skills @> '[\"Python\"]'::jsonb) or "
            "   jsonb_array_length(). Only JOIN maverick_skills when the question explicitly "
            "   asks for per-skill detail like proficiency scores.\n"
            "6. If you must JOIN a table that produces multiple rows per student, use "
            "   SELECT DISTINCT or GROUP BY to guarantee one row per student.\n"
            f"7. {limit_instruction}"
        )

        sql_example = (
            f'"sql": "SELECT ... FROM ... ORDER BY ... LIMIT {intended_limit}",'
            if intended_limit
            else '"sql": "SELECT ... FROM ... WHERE ... ORDER BY ...",'
        )

        prompt = (
            f"Database Schema:\n{schema_context}\n\n"
            f"Natural Language Query: {natural_query}\n"
            + (f"Required row count: {intended_limit}\n" if intended_limit else "Return all matching records.\n")
            + "\nGenerate a PostgreSQL SELECT query for this request.\n"
            "Return ONLY this JSON (no markdown fences, no extra keys):\n"
            "{\n"
            f"  {sql_example}\n"
            '  "explanation": "One sentence: what this query returns and why",\n'
            '  "tables_used": ["table1", "table2"]\n'
            "}"
        )

        result = await self._call_ai(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=1200,
            temperature=0.0,          # deterministic — accuracy matters more than creativity
            feature="nl_to_sql",
        )

        if not result:
            logger.error("NL-to-SQL: AI returned no result for query: %s", natural_query[:100])
            return None

        parsed = self._parse_json(result, feature="nl_to_sql")
        if not parsed or "sql" not in parsed:
            logger.error("NL-to-SQL: Could not parse JSON from AI response: %s", (result or "")[:200])
            return None

        sql = parsed["sql"]
        sql = self._strip_sql_comments(sql)

        return {
            "sql": sql.strip(),
            "explanation": parsed.get("explanation", "SQL generated from natural language query"),
            "tables_used": parsed.get("tables_used", []),
        }

    @staticmethod
    def _strip_sql_comments(sql: str) -> str:
        """Remove -- line comments and /* block comments */ from SQL."""
        import re
        sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
        sql = re.sub(r"--[^\n]*", " ", sql)
        sql = re.sub(r"\n{3,}", "\n\n", sql)
        return sql.strip()

    # ── Feature: performance insights ────────────────────────────────────────

    async def get_performance_insights(
        self,
        assessment_data: Dict[str, Any],
        job_progress: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        if not settings.AI_PERFORMANCE_INSIGHTS_ENABLED:
            return None
        if job_progress is not None:
            context = f"""Assessment Data:
- Total: {assessment_data.get('total_assessments', 0)}
- Passed: {assessment_data.get('passed', 0)}
- Average: {assessment_data.get('average_score', 0)}%
- Strengths: {', '.join(assessment_data.get('strengths', []))}
- Weaknesses: {', '.join(assessment_data.get('weaknesses', []))}

Job Progress:
- Completed: {job_progress.get('completed', 0)}/{job_progress.get('total', 0)}
- Completion: {job_progress.get('completion_percentage', 0)}%
- Status: {job_progress.get('status', 'Unknown')}"""
        else:
            context = json.dumps(assessment_data, indent=2, default=str)

        prompt = f"""Analyse this trainee's performance and return ONLY valid JSON.

{context}

{{
  "overall_assessment": "2-3 sentence summary",
  "strengths": ["top 3"],
  "areas_for_improvement": ["top 3"],
  "recommendations": ["2-3 actionable steps"],
  "predicted_success_rate": 85
}}"""
        return await self._call_ai(
            prompt=prompt,
            system_prompt="You are an experienced training manager. Return only valid JSON.",
            max_tokens=800,
            temperature=0.5,
            feature="performance_insights",
        )

    # ── Usage stats ───────────────────────────────────────────────────────────

    def get_usage_stats(self) -> Dict[str, Any]:
        t = self._tracker
        return {
            "provider":              "azure",
            "model":                 f"azure/{self._model}",
            "requests_today":        t.request_count,
            "input_tokens":          t.input_tokens,
            "output_tokens":         t.output_tokens,
            "total_tokens":          t.input_tokens + t.output_tokens,
            "total_cost_usd":        float(t.total_cost),
            "daily_limit":           settings.AI_DAILY_REQUEST_LIMIT,
            "rate_limit_per_minute": settings.AI_RATE_LIMIT_PER_MINUTE,
            "error_count":           t.error_count,
            "retry_count":           t.retry_count,
            "last_reset":            t.last_reset.isoformat(),
            "requests_by_feature": {
                feat: {
                    "count":         b["count"],
                    "input_tokens":  b["input_tokens"],
                    "output_tokens": b["output_tokens"],
                    "total_tokens":  b["input_tokens"] + b["output_tokens"],
                    "cost_usd":      float(b["cost"]),
                }
                for feat, b in t.by_feature.items()
            },
        }

    def get_detailed_stats(self) -> Dict[str, Any]:
        s   = self.get_usage_stats()
        req = s["requests_today"]
        return {
            **s,
            "avg_tokens_per_request": round(s["total_tokens"] / req, 2) if req else 0,
            "error_rate_percentage":  round(s["error_count"] / req * 100, 2) if req else 0,
            "cost_per_request_usd":   round(float(self._tracker.total_cost / req), 6) if req else 0,
            "cost_breakdown": {
                "input_cost_usd":  float((Decimal(self._tracker.input_tokens)  / 1_000_000) * _COST_PER_1M_INPUT),
                "output_cost_usd": float((Decimal(self._tracker.output_tokens) / 1_000_000) * _COST_PER_1M_OUTPUT),
            },
        }

    # ── DB logging (fire-and-forget) ──────────────────────────────────────────

    def _log_to_db(
        self,
        in_tok: int,
        out_tok: int,
        feature: str,
        success: str,
        error_message: Optional[str] = None,
    ) -> None:
        """
        Persist this AI call to ai_usage_logs so the analytics page has
        accurate lifetime totals even after server restarts.
        Runs synchronously inside a short-lived DB session; failures are
        swallowed so they never interrupt the actual AI response.
        """
        try:
            from app.database import SessionLocal
            from app.models.ai_usage import AIUsageLog
            from decimal import Decimal

            cost = (
                (Decimal(in_tok)  / 1_000_000) * _COST_PER_1M_INPUT
              + (Decimal(out_tok) / 1_000_000) * _COST_PER_1M_OUTPUT
            )
            db = SessionLocal()
            try:
                log = AIUsageLog(
                    feature=feature,
                    model=self._model,
                    input_tokens=in_tok,
                    output_tokens=out_tok,
                    total_tokens=in_tok + out_tok,
                    cost_usd=float(cost),
                    success=success,
                    error_message=error_message,
                )
                db.add(log)
                db.commit()
            finally:
                db.close()
        except Exception as exc:
            logger.debug("AI DB log skipped: %s", exc)

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _parse_json(text: Optional[str], *, feature: str = "") -> Any:
        if not text:
            return None
        s = text.strip()
        if s.startswith("```json"):
            s = s[7:]
        elif s.startswith("```"):
            s = s[3:]
        if s.endswith("```"):
            s = s[:-3]
        s = s.strip()
        try:
            return json.loads(s)
        except json.JSONDecodeError as exc:
            logger.error("JSON parse [%s]: %s -- first 200: %s", feature, exc, s[:200])
            return None
