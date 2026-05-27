"""
NL Query Debug Test Script
==========================
Tests "Top 10 students by CGPA" end-to-end against the running backend.

Logs every layer of the pipeline so we can pinpoint exactly which
layer is failing to enforce the limit.

Run from the api directory:
    python test_nl_query_debug.py
"""

import sys
import io
import json
import re
import requests

# Force UTF-8 output on Windows so the script never crashes on encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ─── CONFIG ───────────────────────────────────────────────────────────────────
BASE_URL   = "http://127.0.0.1:8000"
LOGIN_URL  = f"{BASE_URL}/api/v1/auth/login"
QUERY_URL  = f"{BASE_URL}/api/v1/nl-query/search"

# Super-admin credentials (from .env / known test account)
EMAIL    = "admin@maverick.com"
PASSWORD = "admin123"

TEST_QUERY   = "Top 10 students by CGPA"
EXPECTED_ROW = 10

# ─── HELPERS ─────────────────────────────────────────────────────────────────

PASS = "✅ PASS"
FAIL = "❌ FAIL"
WARN = "⚠️  WARN"
INFO = "ℹ️  INFO"

def sep(title=""):
    line = "─" * 70
    print(f"\n{line}")
    if title:
        print(f"  {title}")
        print(line)


def check(label, condition, detail=""):
    status = PASS if condition else FAIL
    msg = f"  {status}  {label}"
    if detail:
        msg += f"\n         {detail}"
    print(msg)
    return condition


# ─── LAYER 0: extract_limit_from_query (local re-implementation) ──────────────

def local_extract_limit(query: str):
    """Mirror of extract_limit_from_query() in nl_query.py."""
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


def local_find_limit_in_sql(sql: str):
    """Return all LIMIT N values found in the SQL string."""
    matches = re.findall(r'\bLIMIT\s+(\d+)', sql, re.IGNORECASE)
    return [int(m) for m in matches]


# ─── MAIN TEST ────────────────────────────────────────────────────────────────

def run_test():
    all_passed = True

    # ── Layer 0: local regex check ─────────────────────────────────────────────
    sep("LAYER 0 — extract_limit_from_query (local check)")
    extracted = local_extract_limit(TEST_QUERY)
    ok = check(
        f"Regex extracts limit from '{TEST_QUERY}'",
        extracted == EXPECTED_ROW,
        f"Got: {extracted}  Expected: {EXPECTED_ROW}",
    )
    all_passed = all_passed and ok
    print(f"  {INFO}  Pattern matched: {extracted}")

    # ── Login ──────────────────────────────────────────────────────────────────
    sep("AUTHENTICATION")
    print(f"  Logging in as {EMAIL} ...")
    try:
        login_resp = requests.post(
            LOGIN_URL,
            json={"email": EMAIL, "password": PASSWORD},
            timeout=15,
        )
    except requests.exceptions.ConnectionError:
        print(f"\n  {FAIL}  Cannot connect to {BASE_URL}")
        print("  Make sure the backend server is running:")
        print("    cd apps/api && uvicorn app.main:app --reload")
        sys.exit(1)

    ok = check(
        "Login returns HTTP 200",
        login_resp.status_code == 200,
        f"Status: {login_resp.status_code}  Body: {login_resp.text[:200]}",
    )
    all_passed = all_passed and ok
    if not ok:
        print("\n  Cannot continue — login failed. Check credentials.")
        sys.exit(1)

    token = login_resp.json().get("access_token")
    ok = check("access_token present in login response", bool(token))
    all_passed = all_passed and ok
    if not ok:
        sys.exit(1)
    print(f"  {INFO}  Token: {token[:40]}...")

    headers = {"Authorization": f"Bearer {token}"}

    # ── PROOF TEST: simulate the broken frontend (max_rows=100 overrides NL) ──
    sep("PROOF — broken frontend behaviour (max_rows=100 override)")
    print(f"  Sending: query='{TEST_QUERY}'  max_rows=100  (like the OLD frontend did)")
    broken_payload = {"query": TEST_QUERY, "include_stats": True, "max_rows": 100}
    broken_resp = requests.post(QUERY_URL, json=broken_payload, headers=headers, timeout=60)
    if broken_resp.status_code == 200:
        broken_body = broken_resp.json()
        broken_intended = broken_body.get("intended_limit")
        broken_count   = len(broken_body.get("data", []))
        broken_note    = broken_body.get("result_note")
        print(f"  {INFO}  intended_limit returned : {broken_intended}  (should be 100, not 10)")
        print(f"  {INFO}  row count returned       : {broken_count}  (shows all students, not 10)")
        print(f"  {INFO}  result_note              : {broken_note}")
        check(
            "max_rows=100 overrides NL extraction (intended_limit != 10)",
            broken_intended != EXPECTED_ROW,
            f"intended_limit={broken_intended} — proves max_rows wins over NL text",
        )
        check(
            "max_rows=100 returns > 10 rows (all students)",
            broken_count > EXPECTED_ROW,
            f"Got {broken_count} rows — this was the UI bug",
        )
        print(f"\n  ROOT CAUSE CONFIRMED: the frontend was calling nlQueryAPI.search(query, 100)")
        print(f"  which sent max_rows=100 and overrode the 'Top 10' in the query text.")
        print(f"  Fix: call nlQueryAPI.search(query) with NO max_rows argument.")
    else:
        print(f"  {WARN}  Proof test skipped (HTTP {broken_resp.status_code})")

    # ── NL Query call — CORRECT (no max_rows override) ────────────────────────
    sep(f"CORRECT CALL — '{TEST_QUERY}'  (no max_rows — auto-detect from text)")
    print(f"  Calling {QUERY_URL} ...")
    payload = {
        "query": TEST_QUERY,
        "include_stats": True,
        # max_rows intentionally omitted — same as fixed frontend
    }

    try:
        nl_resp = requests.post(
            QUERY_URL,
            json=payload,
            headers=headers,
            timeout=60,        # AI call can be slow
        )
    except requests.exceptions.ReadTimeout:
        print(f"\n  {FAIL}  Request timed out after 60s — AI service may be down")
        sys.exit(1)

    ok = check(
        "NL query returns HTTP 200",
        nl_resp.status_code == 200,
        f"Status: {nl_resp.status_code}",
    )
    all_passed = all_passed and ok

    if not ok:
        print(f"\n  Response body:\n{nl_resp.text[:1000]}")
        print(f"\n  {FAIL}  Cannot analyse layers — query failed at HTTP level.")
        sys.exit(1)

    body = nl_resp.json()

    # ── Layer 0: intended_limit in response ─────────────────────────────────
    sep("LAYER 0 RESULT — intended_limit extracted by server")
    server_intended = body.get("intended_limit")
    ok = check(
        "Server extracted intended_limit == 10",
        server_intended == EXPECTED_ROW,
        f"Server got: {server_intended}  Expected: {EXPECTED_ROW}",
    )
    all_passed = all_passed and ok

    if server_intended is None:
        print(f"\n  {FAIL}  SERVER DID NOT EXTRACT A LIMIT from the query text.")
        print("  Root cause: extract_limit_from_query() returned None.")
        print("  Fix: add the matching pattern to extract_limit_from_query() in nl_query.py")

    # ── Layer 1/2: generated_sql LIMIT value ───────────────────────────────
    sep("LAYER 1+2 RESULT — generated_sql LIMIT clause")
    sql = body.get("generated_sql", "")
    print(f"\n  Generated SQL:\n  {sql}\n")

    limits_in_sql = local_find_limit_in_sql(sql)
    print(f"  {INFO}  LIMIT values found in SQL: {limits_in_sql}")

    if limits_in_sql:
        outermost_limit = limits_in_sql[-1]   # last LIMIT = outermost query
        ok = check(
            f"Outermost LIMIT in generated_sql == {EXPECTED_ROW}",
            outermost_limit == EXPECTED_ROW,
            f"Outermost LIMIT is {outermost_limit}, expected {EXPECTED_ROW}",
        )
        all_passed = all_passed and ok

        if outermost_limit != EXPECTED_ROW:
            if server_intended is None:
                print(f"  Root cause: intended_limit was None → enforce_outermost_limit() was not called with 10")
            else:
                print(f"  Root cause: AI ignored the LIMIT instruction OR enforce_outermost_limit() failed")
    else:
        print(f"  {WARN}  No LIMIT found in generated_sql — sanitize added LIMIT 1000")
        ok = check(
            "SQL has at least some LIMIT (1000 safety cap)",
            "LIMIT" in sql.upper(),
            "No LIMIT at all — sanitize_sql_query may have failed",
        )
        all_passed = all_passed and ok

    # ── Layer 3: actual row count in response ──────────────────────────────
    sep("LAYER 3 RESULT — actual rows returned")
    data = body.get("data", [])
    stats = body.get("statistics", {})
    result_note = body.get("result_note")
    row_count = len(data)
    stats_rows = stats.get("total_rows", "N/A")

    print(f"  {INFO}  len(data)                 = {row_count}")
    print(f"  {INFO}  statistics.total_rows     = {stats_rows}")
    print(f"  {INFO}  result_note               = {result_note}")

    ok = check(
        f"Row count == {EXPECTED_ROW}",
        row_count == EXPECTED_ROW,
        f"Got {row_count} rows, expected {EXPECTED_ROW}",
    )
    all_passed = all_passed and ok

    if row_count != EXPECTED_ROW:
        # Diagnose which layer failed
        print()
        if server_intended is None:
            print(f"  ROOT CAUSE → LAYER 0 FAILED")
            print(f"    extract_limit_from_query('{TEST_QUERY}') returned None")
            print(f"    So intended_limit was None → no limit enforcement at all")
        elif row_count > EXPECTED_ROW:
            if limits_in_sql and limits_in_sql[-1] != EXPECTED_ROW:
                print(f"  ROOT CAUSE → LAYER 2 FAILED")
                print(f"    enforce_outermost_limit() did not set LIMIT {EXPECTED_ROW}")
                print(f"    SQL has LIMIT {limits_in_sql[-1]} instead of {EXPECTED_ROW}")
            else:
                print(f"  ROOT CAUSE → LAYER 3 FAILED")
                print(f"    apply_intended_limit() did not slice to {EXPECTED_ROW}")
                print(f"    Or apply_intended_limit() was never called")
        else:
            print(f"  {WARN}  Fewer rows than expected — DB has fewer than {EXPECTED_ROW} records")

    # ── Sample of first 3 rows ────────────────────────────────────────────
    sep("DATA SAMPLE — first 3 rows returned")
    for i, row in enumerate(data[:3]):
        print(f"  Row {i+1}: {json.dumps(row, default=str)[:120]}")
    if row_count > 3:
        print(f"  ... ({row_count - 3} more rows)")

    # ── Tables used ───────────────────────────────────────────────────────
    sep("METADATA")
    print(f"  tables_used   : {body.get('tables_used')}")
    print(f"  intended_limit: {body.get('intended_limit')}")
    print(f"  result_note   : {body.get('result_note')}")
    print(f"  executed_at   : {body.get('executed_at')}")

    # ── Final verdict ─────────────────────────────────────────────────────
    sep("FINAL VERDICT")
    if all_passed:
        print(f"  {PASS}  ALL CHECKS PASSED — NL query limit enforcement is working correctly.")
    else:
        print(f"  {FAIL}  ONE OR MORE CHECKS FAILED — see ROOT CAUSE notes above.")
    print()


if __name__ == "__main__":
    run_test()
