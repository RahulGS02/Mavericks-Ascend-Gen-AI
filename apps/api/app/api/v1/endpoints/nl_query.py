"""
Natural Language Query API Endpoints
Allows SuperAdmins to query database using natural language
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
import logging
import re
import uuid as uuid_lib

from ....database import get_db
from ....models.user import User
from ....utils.dependencies import get_super_admin
from ....services.schema_provider import get_database_schema_context
from ....services.ai_service import ai_service
from ....services.sql_validator import validate_sql_query, sanitize_sql_query, get_query_tables
from ....services.query_executor import execute_safe_query
from ....services.excel_generator import excel_generator
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def extract_limit_from_query(query: str) -> Optional[int]:
    """
    Extract the intended row count from a natural-language query.

    Matches patterns like:
        "Top 10 students by CGPA"       → 10
        "Show the first 5 mavericks"    → 5
        "List 20 available candidates"  → 20
        "Find top 3 performers"         → 3
        "Give me 50 records"            → 50
        "2 mavericks"                   → 2
    """
    patterns = [
        r'\btop\s+(\d+)\b',
        r'\bfirst\s+(\d+)\b',
        r'\bbest\s+(\d+)\b',
        r'\bhighest\s+(\d+)\b',
        r'\blowest\s+(\d+)\b',
        r'\b(\d+)\s+(?:top|best|highest|lowest)\b',
        r'\b(\d+)\s+(?:students?|mavericks?|candidates?|trainees?|records?|results?|rows?|users?|people|entries)\b',
        r'\bshow\s+(?:me\s+)?(?:the\s+)?(\d+)\b',
        r'\bget\s+(?:me\s+)?(?:the\s+)?(\d+)\b',
        r'\bfetch\s+(?:me\s+)?(?:the\s+)?(\d+)\b',
        r'\blist\s+(\d+)\b',
        r'\blimit\s+(?:to\s+)?(\d+)\b',
    ]
    for pattern in patterns:
        m = re.search(pattern, query, re.IGNORECASE)
        if m:
            limit = int(m.group(1))
            if 1 <= limit <= 1000:
                return limit
    return None


def enforce_outermost_limit(sql: str, limit: int) -> str:
    """
    Replace the outermost LIMIT in an SQL string with *limit*.

    The outermost LIMIT is always the **last** LIMIT keyword in valid SQL
    (inner / subquery LIMITs appear earlier in the string).
    If no LIMIT clause exists, one is appended.
    """
    matches = list(re.finditer(r'\bLIMIT\s+\d+', sql, re.IGNORECASE))
    if not matches:
        return f"{sql.rstrip()} LIMIT {limit}"
    last = matches[-1]
    return sql[: last.start()] + f"LIMIT {limit}" + sql[last.end():]


def apply_intended_limit(
    data: List[dict],
    intended_limit: int,
    raw_sql_count: int,
) -> tuple[List[dict], str]:
    """
    Enforce *intended_limit* on the result set in two passes:

    Pass 1 – Smart deduplication:
        If an ``id`` or ``maverick_id`` column exists, walk the rows in order
        and keep only the first occurrence of each id.  This fixes JOIN
        inflation (e.g. one student × 4 skills = 4 rows → 1 unique student).
        Stops as soon as *intended_limit* unique rows are collected.

    Pass 2 – Hard slice (unconditional backstop):
        ``data[:intended_limit]`` is applied regardless of what Pass 1 did.
        This is the absolute guarantee — no matter what the AI or DB returned,
        the caller gets at most *intended_limit* rows.

    Returns (final_data, result_note).
    """
    if not data:
        return data, f"No records found (requested {intended_limit})."

    # ── Pass 1: deduplication by id ──────────────────────────────────────
    first_row = data[0]
    id_key = next(
        (k for k in ("id", "maverick_id") if k in first_row),
        None,
    )

    join_inflation = False
    if id_key is not None:
        # Count how many unique ids are in the full result
        unique_ids = {r.get(id_key) for r in data}
        join_inflation = len(unique_ids) < len(data)   # true = duplicate ids = JOIN inflation

        if join_inflation or len(data) > intended_limit:
            seen: set = set()
            deduped: List[dict] = []
            for row in data:
                row_id = row.get(id_key)
                if row_id not in seen:
                    seen.add(row_id)
                    deduped.append(row)
                    if len(deduped) >= intended_limit:
                        break
            data = deduped

    # ── Pass 2: absolute hard slice ───────────────────────────────────────
    data = data[:intended_limit]

    # ── Build result_note ─────────────────────────────────────────────────
    final_count = len(data)

    if join_inflation:
        note = (
            f"JOIN inflation detected: the SQL returned {raw_sql_count} rows "
            f"(multiple rows per student due to skill JOIN). "
            f"Deduplicated and limited to {final_count} unique records as requested."
        )
    elif raw_sql_count > intended_limit:
        note = (
            f"Query returned {raw_sql_count} rows in total. "
            f"Limited to the top {final_count} as requested."
        )
    elif final_count == intended_limit:
        note = f"Returned exactly {intended_limit} rows as requested."
    else:
        note = (
            f"Requested top {intended_limit}, but only {final_count} "
            f"matching records exist in the database."
        )

    return data, note


def _check_ai_service(operation: str) -> None:
    """Raise HTTP 503 if the AI service is missing or lacks NL-to-SQL."""
    if ai_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not configured. Set AI_PROVIDER=azure in .env.",
        )
    if not hasattr(ai_service, "generate_sql_from_natural_language"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"The active AI provider ({type(ai_service).__name__}) does not "
                f"support {operation}. Set AI_PROVIDER=azure in .env."
            ),
        )


# ─────────────────────────────────────────────────────────────────────────────
# Shared pipeline
# ─────────────────────────────────────────────────────────────────────────────

async def _run_nl_query_pipeline(
    natural_query: str,
    max_rows: Optional[int],
    db: Session,
    user_email: str,
) -> dict:
    """
    Execute the full NL → SQL → DB → limit-enforce pipeline.

    Two modes depending on whether the user specified a row count:

    ── Explicit count mode ("Top 10 students") ────────────────────────────────
      Layer 1 — AI prompt:        AI is told "CRITICAL: use LIMIT 10 exactly".
      Layer 2 — SQL rewrite:      enforce_outermost_limit(sql, 10) runs after
                                  sanitisation — guarantees LIMIT is 10.
      Layer 3 — Post-execution:   apply_intended_limit() deduplicates JOIN-
                                  inflated rows, then data[:10] unconditionally.
      Result: always exactly N rows (or fewer if the DB has fewer).

    ── Generic mode ("Show all students with CGPA > 8") ───────────────────────
      Layer 1 — AI prompt:        AI is told "do NOT add an arbitrary LIMIT".
      Layer 2 — SQL rewrite:      enforce_outermost_limit(sql, 1000) — overrides
                                  any LIMIT the AI may have added, ensuring the
                                  user gets all matching records up to the 1000
                                  safety cap.
      Layer 3 — Not applied:      apply_intended_limit() is skipped; user gets
                                  all matching records returned by the DB.
      Result: all matching records (up to 1000 safety cap).

    Returns a dict with keys: data, stats, generated_sql, explanation,
                              tables_used, intended_limit, result_note.
    """
    logger.info("NL query | user=%s | query=%s", user_email, natural_query)

    # ── Layer 0: extract intended limit from query text ───────────────────────
    # Priority: explicit max_rows (from API request) > number in query text.
    intended_limit: Optional[int] = max_rows or extract_limit_from_query(natural_query)
    logger.info("Intended limit: %s", intended_limit)

    # ── Layer 1: AI generates SQL with intended_limit hint ───────────────────
    schema_context = get_database_schema_context()
    ai_result = await ai_service.generate_sql_from_natural_language(
        natural_query=natural_query,
        schema_context=schema_context,
        intended_limit=intended_limit,
    )
    if not ai_result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate SQL. AI service may be unavailable.",
        )

    generated_sql = ai_result["sql"]
    explanation   = ai_result.get("explanation", "SQL generated from natural language")
    tables_used   = ai_result.get("tables_used", [])
    logger.info("AI SQL: %s", generated_sql[:300])

    # ── Security validation ───────────────────────────────────────────────────
    is_valid, error_msg, warnings = validate_sql_query(generated_sql)
    if not is_valid:
        logger.error("SQL validation failed: %s", error_msg)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Generated SQL failed security check: {error_msg}",
        )
    for w in warnings:
        logger.warning("SQL warning: %s", w)

    # ── Sanitise (strip comments, ensure LIMIT ≤ 1000) ───────────────────────
    sanitized_sql = sanitize_sql_query(generated_sql)

    # ── Layer 2: LIMIT enforcement ───────────────────────────────────────────
    if intended_limit:
        # User specified an exact count — hard-set the outermost LIMIT to that value.
        sanitized_sql = enforce_outermost_limit(sanitized_sql, intended_limit)
        logger.info("Explicit limit enforced (%d): %s", intended_limit, sanitized_sql[:300])
    else:
        # No specific count requested — user wants ALL matching records.
        # The AI might have added an arbitrary LIMIT (e.g. LIMIT 10) despite our
        # instructions. Override it with the full 1000 safety cap so the user
        # gets everything available (up to the safety maximum).
        sanitized_sql = enforce_outermost_limit(sanitized_sql, 1000)
        logger.info("Generic query — safety cap of 1000 applied: %s", sanitized_sql[:300])

    # ── Execute ───────────────────────────────────────────────────────────────
    try:
        data, stats = await execute_safe_query(db, sanitized_sql)
    except Exception as exc:
        logger.error("Query execution error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query execution failed: {str(exc)}",
        )

    if not tables_used:
        tables_used = get_query_tables(sanitized_sql)

    raw_sql_count = len(data)   # rows returned by the DB before any post-processing

    # ── Layer 3: post-execution limit enforcement (unconditional) ────────────
    result_note: Optional[str] = None

    if intended_limit:
        data, result_note = apply_intended_limit(data, intended_limit, raw_sql_count)
        stats["total_rows"] = len(data)     # keep stats consistent with trimmed data
        logger.info(
            "Limit applied | raw=%d | final=%d | note=%s",
            raw_sql_count, len(data), result_note,
        )

    logger.info(
        "✅ NL query done | rows=%d | time=%.1fms",
        stats.get("total_rows", len(data)),
        stats.get("execution_time_ms", 0),
    )

    return {
        "data":          data,
        "stats":         stats,
        "generated_sql": sanitized_sql,
        "explanation":   explanation,
        "tables_used":   tables_used,
        "intended_limit": intended_limit,
        "result_note":   result_note,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Request / Response models
# ─────────────────────────────────────────────────────────────────────────────

class NaturalLanguageQueryRequest(BaseModel):
    query: str = Field(
        ..., min_length=5, max_length=500,
        description="Natural language query",
    )
    include_stats: bool = Field(True, description="Include statistical aggregations")
    max_rows: Optional[int] = Field(
        None, ge=1, le=1000,
        description=(
            "Hard override for row count. Overrides any number found in the "
            "query text (e.g. 'top 10'). Leave empty to auto-detect."
        ),
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Top 10 students by CGPA",
                "include_stats": True,
                "max_rows": None,
            }
        }


class QueryResult(BaseModel):
    query_id:        str           = Field(..., description="Unique query id")
    natural_query:   str           = Field(..., description="Original query")
    generated_sql:   str           = Field(..., description="Final SQL executed")
    explanation:     str           = Field(..., description="AI explanation")
    tables_used:     List[str]     = Field(..., description="Tables referenced")
    intended_limit:  Optional[int] = Field(None, description="Row limit detected from query")
    data:            List[dict]    = Field(..., description="Result rows")
    statistics:      dict          = Field(..., description="Execution statistics")
    result_note:     Optional[str] = Field(None, description="Explains any limit/dedup adjustments")
    executed_at:     str           = Field(..., description="Timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "query_id": "uuid",
                "natural_query": "Top 10 students by CGPA",
                "generated_sql": "SELECT id, name, cgpa FROM mavericks ORDER BY cgpa DESC LIMIT 10",
                "explanation": "Returns the 10 students with the highest CGPA.",
                "tables_used": ["mavericks"],
                "intended_limit": 10,
                "data": [{"id": "uuid-1", "name": "Alice", "cgpa": 9.8}],
                "statistics": {"total_rows": 10, "execution_time_ms": 45.2},
                "result_note": "Returned exactly 10 rows as requested.",
                "executed_at": "2026-05-25T20:00:00",
            }
        }


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/search", response_model=QueryResult)
async def search_with_natural_language(
    request: NaturalLanguageQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin),
):
    """
    Execute a natural-language query and return results.

    **Only SuperAdmins can use this endpoint.**

    **With a specific count** ("Top 10 students", "Show 5 mavericks"):
    - AI generates SQL with that exact LIMIT
    - SQL is rewritten to enforce the limit before execution
    - Result set is hard-sliced after execution (JOIN-inflation safe)
    - You get **exactly N rows**. Always.

    **Without a specific count** ("List all students with CGPA > 8"):
    - AI generates SQL without an arbitrary LIMIT
    - System applies a 1000-row safety cap
    - You get **all matching records** (up to 1000)
    """
    _check_ai_service("natural language query")

    try:
        result = await _run_nl_query_pipeline(
            natural_query=request.query,
            max_rows=request.max_rows,
            db=db,
            user_email=current_user.email,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Unexpected error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(exc)}",
        )

    data = result["data"]
    if not request.include_stats:
        data = data[:100]

    return QueryResult(
        query_id=str(uuid_lib.uuid4()),
        natural_query=request.query,
        generated_sql=result["generated_sql"],
        explanation=result["explanation"],
        tables_used=result["tables_used"],
        intended_limit=result["intended_limit"],
        data=data,
        statistics=result["stats"],
        result_note=result["result_note"],
        executed_at=datetime.now().isoformat(),
    )


@router.post("/search/download")
async def download_query_results_excel(
    request: NaturalLanguageQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin),
):
    """
    Execute a natural-language query and download results as Excel.

    **Only SuperAdmins can use this endpoint.**
    Same three-layer limit guarantee as /search.
    """
    _check_ai_service("Excel download")

    try:
        result = await _run_nl_query_pipeline(
            natural_query=request.query,
            max_rows=request.max_rows,
            db=db,
            user_email=current_user.email,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Unexpected error (download): %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(exc)}",
        )

    query_info = {
        "natural_query":  request.query,
        "sql":            result["generated_sql"],
        "explanation":    result["explanation"],
        "tables_used":    result["tables_used"],
        "intended_limit": result["intended_limit"],
        "result_note":    result["result_note"] or "No adjustments needed.",
    }

    try:
        logger.info("Generating Excel — %d rows", len(result["data"]))
        excel_buffer = excel_generator.generate_excel(
            result["data"], result["stats"], query_info,
        )
        excel_buffer.seek(0)
    except Exception as exc:
        logger.error("Excel generation failed: %s", exc)
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Excel generation failed: {str(exc)}",
        )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"query_results_{timestamp}.xlsx"
    logger.info("✅ Excel ready: %s (%d rows)", filename, len(result["data"]))

    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
