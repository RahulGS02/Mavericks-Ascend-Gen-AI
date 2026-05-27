"""
Azure AI Foundry -- Connection & Feature Test
=============================================
Run from: apps/api/
    python test_azure_connection.py

Root cause history:
  Attempt 1: wrong project path (/projects// -- name missing) -> 400
  Attempt 2: api-version wrong                                -> 400
  Fix:       project name = proj-default-ai, api-version = 2024-10-21
             v1 endpoint is OpenAI-compatible (no api-version needed for SDK)

Confirmed working pattern (from Azure analysis):
  client = OpenAI(
      api_key=KEY,
      base_url="https://mavericks-ai.services.ai.azure.com/api/projects/proj-default-ai/openai/v1/"
  )
  client.chat.completions.create(model="gpt-4.1-mini", ...)
"""

import asyncio
import json
import sys
import time
from decimal import Decimal

# Force UTF-8 on Windows terminal
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Credentials
# Project name: proj-default-ai  (from original Azure portal URL)
# ---------------------------------------------------------------------------
ENDPOINT  = "https://mavericks-ai.services.ai.azure.com/api/projects/proj-default-ai/openai/v1"
API_KEY   = __import__("os").environ.get("AZURE_AI_API_KEY", "")
MODEL       = "gpt-4.1-mini"
API_VERSION = "2024-10-21"   # latest stable GA; overridden if probe finds different

CANDIDATE_VERSIONS = [
    None,                    # try WITHOUT api-version first (v1 is OpenAI-compatible)
    "2024-10-21",            # latest stable GA
    "2025-03-01-preview",    # latest preview
    "2024-08-01-preview",
    "2024-06-01",
]

# Pricing  (gpt-4.1-mini)
COST_INPUT  = Decimal("0.40")   # $0.40 / 1M input tokens
COST_OUTPUT = Decimal("1.60")   # $1.60 / 1M output tokens

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
SEP = "-" * 70
total_input_tokens  = 0
total_output_tokens = 0
results: list[dict] = []


def _section(title: str) -> None:
    print(f"\n{SEP}")
    print(f"  {title}")
    print(SEP)


def _result(name: str, passed: bool, detail: str = "", tokens: tuple = (0, 0)) -> None:
    global total_input_tokens, total_output_tokens
    status = "[PASS]" if passed else "[FAIL]"
    in_t, out_t = tokens
    total_input_tokens  += in_t
    total_output_tokens += out_t
    tok_str = f"  [{in_t} -> {out_t} tok]" if in_t else ""
    print(f"  {status}  {name}{tok_str}")
    if detail:
        short = detail[:380].replace("\n", " ")
        print(f"         {short}{'...' if len(detail) > 380 else ''}")
    results.append({"test": name, "passed": passed})


# ---------------------------------------------------------------------------
# TEST 1 -- Raw HTTP  (auto-probes api-version + auth header)
# ---------------------------------------------------------------------------
def test_1_raw_http() -> bool:
    global API_VERSION
    _section("TEST 1 -- Raw HTTP  (auto-probe: version x auth header)")
    base_url = f"{ENDPOINT}/chat/completions"
    print(f"  Endpoint : {base_url}")
    print(f"  Probing  : {len(CANDIDATE_VERSIONS)} version candidates x 2 auth headers\n")

    body = {
        "model":       MODEL,
        "messages":    [{"role": "user", "content": "Reply with: PONG"}],
        "max_tokens":  10,
        "temperature": 0,
    }

    import httpx

    for ver in CANDIDATE_VERSIONS:
        url = base_url if ver is None else f"{base_url}?api-version={ver}"
        ver_label = "no-version" if ver is None else ver

        for hdr_name, headers in [
            ("api-key", {"api-key": API_KEY, "Content-Type": "application/json"}),
            ("Bearer",  {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}),
        ]:
            try:
                r = httpx.post(url, headers=headers, json=body, timeout=15)
                err_msg = ""
                if r.status_code != 200:
                    try:
                        err_msg = r.json().get("error", {}).get("message", r.text[:80])
                    except Exception:
                        err_msg = r.text[:80]

                status_str = f"api-version={ver_label:<22}  header={hdr_name:<7}  HTTP {r.status_code}"
                if r.status_code == 200:
                    text = r.json()["choices"][0]["message"]["content"].strip()
                    API_VERSION = ver if ver else "none"
                    print(f"  [FOUND]  {status_str}  -> '{text}'")
                    _result("Raw HTTP POST /chat/completions", True,
                            f"WORKING: api-version={ver_label}  header={hdr_name}  reply='{text}'")
                    return True
                else:
                    print(f"  [ skip]  {status_str}  -- {err_msg}")

            except Exception as exc:
                print(f"  [ err ]  api-version={ver_label}  header={hdr_name}  -- {exc}")

    print()
    print("  All combinations failed. Check:")
    print(f"  1. Project name in URL -- current: {ENDPOINT}")
    print(f"     Go to ai.azure.com -> project -> Settings -> Keys and Endpoint")
    print(f"  2. API key correct: {API_KEY[:20]}...")
    _result("Raw HTTP POST /chat/completions", False, "No version/header combination succeeded.")
    return False


# ---------------------------------------------------------------------------
# TEST 2 -- AsyncOpenAI SDK
# ---------------------------------------------------------------------------
async def test_2_sdk_ping() -> tuple[bool, object]:
    _section("TEST 2 -- AsyncOpenAI SDK ping")
    ver_label = API_VERSION if API_VERSION != "none" else "none (v1 no-version)"
    print(f"  base_url    : {ENDPOINT}/")
    print(f"  model       : {MODEL}")
    print(f"  api-version : {ver_label}  (from TEST 1 probe)")

    try:
        from openai import AsyncOpenAI
    except ImportError:
        _result("SDK ping", False, "pip install openai>=1.60.0")
        return False, None

    # Build client -- only add api-version query param if one was found
    client_kwargs: dict = {
        "base_url": ENDPOINT + "/",
        "api_key":  API_KEY,
    }
    if API_VERSION and API_VERSION != "none":
        client_kwargs["default_query"] = {"api-version": API_VERSION}

    client = AsyncOpenAI(**client_kwargs)

    try:
        t0   = time.time()
        resp = await client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": "Reply with exactly: CONNECTED"}],
            max_tokens=10,
            temperature=0,
        )
        ms      = int((time.time() - t0) * 1000)
        text    = resp.choices[0].message.content.strip()
        in_tok  = resp.usage.prompt_tokens
        out_tok = resp.usage.completion_tokens

        _result("SDK chat.completions.create()", True,
                f"Latency {ms}ms -- '{text}'  model='{resp.model}'",
                (in_tok, out_tok))
        return True, client

    except Exception as exc:
        _result("SDK chat.completions.create()", False, str(exc))
        return False, None


# ---------------------------------------------------------------------------
# TEST 3 -- Model list
# ---------------------------------------------------------------------------
async def test_3_models(client) -> None:
    _section("TEST 3 -- Available deployments")
    try:
        models = await client.models.list()
        names  = [m.id for m in models.data]
        _result("List models", True, "Available: " + ", ".join(names[:15]))
    except Exception as exc:
        _result("List models", False, f"{exc}  (non-critical)")


# ---------------------------------------------------------------------------
# Sample resume for tests 4-9
# ---------------------------------------------------------------------------
SAMPLE_RESUME = """
Rahul Kumar
Email: rahul.kumar@gmail.com | Phone: +91-9876543210
LinkedIn: linkedin.com/in/rahulkumar | GitHub: github.com/rahulkumar

EDUCATION
B.Tech Computer Science Engineering -- VIT University, Vellore
CGPA: 8.7 / 10  |  Graduated: 2024

SKILLS
Python, FastAPI, React, Next.js, TypeScript, PostgreSQL, Docker, Redis,
AWS (EC2, S3, Lambda), Git, REST APIs, SQLAlchemy, Pydantic

EXPERIENCE
Software Engineering Intern -- TechCorp Pvt Ltd  (Jan 2024 - Jun 2024)
* Built REST APIs with FastAPI serving 50K requests/day
* Migrated MySQL to PostgreSQL, reducing query time by 40%

PROJECTS
E-Commerce Platform (6 months)
* Next.js + FastAPI + PostgreSQL, JWT auth, Stripe payments, AWS deployment

CERTIFICATIONS
AWS Cloud Practitioner -- Amazon Web Services, 2023
"""


# ---------------------------------------------------------------------------
# TEST 4 -- Resume parsing
# ---------------------------------------------------------------------------
async def test_4_resume_parsing(client) -> None:
    _section("TEST 4 -- Resume parsing (structured JSON)")
    prompt = f"""Extract ALL information from this resume and return as JSON.

Resume:
{SAMPLE_RESUME}

Return:
{{
  "personal_info": {{"name":"","email":"","phone":"","linkedin":"","github":""}},
  "education": [{{"degree":"","branch":"","college":"","year":0,"cgpa":0.0}}],
  "skills": {{"technical":[],"frameworks":[],"databases":[],"tools":[]}},
  "projects": [{{"name":"","description":"","technologies":[]}}],
  "certifications": [{{"name":"","issuer":"","year":0}}],
  "total_experience_years": 0.5,
  "summary": "..."
}}
Return ONLY valid JSON, no markdown."""
    try:
        t0   = time.time()
        resp = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Expert resume parser. Return ONLY valid JSON."},
                {"role": "user",   "content": prompt},
            ],
            max_tokens=1500, temperature=0.2,
        )
        ms      = int((time.time() - t0) * 1000)
        text    = resp.choices[0].message.content.strip()
        in_tok  = resp.usage.prompt_tokens
        out_tok = resp.usage.completion_tokens

        if text.startswith("```"): text = text[text.index("\n")+1:]
        if text.endswith("```"):   text = text[:-3]

        parsed = json.loads(text.strip())
        name   = parsed.get("personal_info", {}).get("name", "?")
        skills = parsed.get("skills", {}).get("technical", [])
        _result("Resume parsing", True,
                f"Latency {ms}ms -- name='{name}'  tech_skills={len(skills)}: {', '.join(skills[:7])}",
                (in_tok, out_tok))
    except json.JSONDecodeError as exc:
        _result("Resume parsing", False, f"JSON decode error: {exc}")
    except Exception as exc:
        _result("Resume parsing", False, str(exc))


# ---------------------------------------------------------------------------
# TEST 5 -- Skill extraction
# ---------------------------------------------------------------------------
async def test_5_skill_extraction(client) -> None:
    _section("TEST 5 -- Skill extraction (flat list)")
    try:
        t0   = time.time()
        resp = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Return ONLY a valid JSON array of skill strings."},
                {"role": "user",   "content": f"Extract all tech skills:\n{SAMPLE_RESUME[:1500]}"},
            ],
            max_tokens=400, temperature=0.3,
        )
        ms      = int((time.time() - t0) * 1000)
        text    = resp.choices[0].message.content.strip()
        in_tok  = resp.usage.prompt_tokens
        out_tok = resp.usage.completion_tokens

        if text.startswith("```"): text = text[text.index("\n")+1:]
        if text.endswith("```"):   text = text[:-3]

        skills = json.loads(text.strip())
        _result("Skill extraction",
                isinstance(skills, list) and len(skills) > 0,
                f"Latency {ms}ms -- {len(skills)} skills: {', '.join(skills[:10])}",
                (in_tok, out_tok))
    except Exception as exc:
        _result("Skill extraction", False, str(exc))


# ---------------------------------------------------------------------------
# TEST 6 -- Profile summary
# ---------------------------------------------------------------------------
async def test_6_profile_summary(client) -> None:
    _section("TEST 6 -- Profile summary generation")
    try:
        t0   = time.time()
        resp = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "HR recruiter. Write concise 2-3 sentence summaries."},
                {"role": "user",   "content": (
                    "Write a professional summary:\n"
                    "Name: Rahul Kumar | Education: B.Tech CSE, VIT, CGPA 8.7\n"
                    "Skills: Python, FastAPI, React, PostgreSQL, Docker, AWS | Graduation: 2024"
                )},
            ],
            max_tokens=200, temperature=0.7,
        )
        ms      = int((time.time() - t0) * 1000)
        summary = resp.choices[0].message.content.strip()
        in_tok  = resp.usage.prompt_tokens
        out_tok = resp.usage.completion_tokens
        _result("Profile summary", len(summary) > 30,
                f"Latency {ms}ms -- '{summary}'", (in_tok, out_tok))
    except Exception as exc:
        _result("Profile summary", False, str(exc))


# ---------------------------------------------------------------------------
# TEST 7 -- Performance insights
# ---------------------------------------------------------------------------
async def test_7_performance_insights(client) -> None:
    _section("TEST 7 -- Performance insights (JSON)")
    try:
        t0   = time.time()
        resp = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Training manager. Return ONLY valid JSON."},
                {"role": "user",   "content": (
                    "Analyse trainee: 5 assessments, 4 passed, avg 78%\n"
                    "Strengths: Python, FastAPI | Weaknesses: Docker, AWS\n"
                    "Jobs: 8/10 done\n\n"
                    'Return: {"overall_assessment":"...","strengths":[],'
                    '"areas_for_improvement":[],"recommendations":[],"predicted_success_rate":85}'
                )},
            ],
            max_tokens=600, temperature=0.5,
        )
        ms      = int((time.time() - t0) * 1000)
        text    = resp.choices[0].message.content.strip()
        in_tok  = resp.usage.prompt_tokens
        out_tok = resp.usage.completion_tokens

        if text.startswith("```"): text = text[text.index("\n")+1:]
        if text.endswith("```"):   text = text[:-3]

        data  = json.loads(text.strip())
        score = data.get("predicted_success_rate", "?")
        _result("Performance insights", True,
                f"Latency {ms}ms -- predicted_success={score}%", (in_tok, out_tok))
    except Exception as exc:
        _result("Performance insights", False, str(exc))


# ---------------------------------------------------------------------------
# TEST 8 -- Batch match scoring
# ---------------------------------------------------------------------------
async def test_8_batch_match(client) -> None:
    _section("TEST 8 -- Batch match scoring")
    try:
        t0   = time.time()
        resp = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Expert recruiter. Return ONLY valid JSON."},
                {"role": "user",   "content": (
                    "Rate candidate fit 0-100:\n"
                    "Candidate: Python, FastAPI, React, PostgreSQL, Docker | B.Tech CSE 8.7\n"
                    "Batch: Full Stack Dev | Required: Python, React, SQL | Preferred: Docker, AWS\n"
                    'Return: {"score": 85, "reasoning": "..."}'
                )},
            ],
            max_tokens=300, temperature=0.3,
        )
        ms      = int((time.time() - t0) * 1000)
        text    = resp.choices[0].message.content.strip()
        in_tok  = resp.usage.prompt_tokens
        out_tok = resp.usage.completion_tokens

        if text.startswith("```"): text = text[text.index("\n")+1:]
        if text.endswith("```"):   text = text[:-3]

        data  = json.loads(text.strip())
        score = data.get("score", 0)
        _result("Batch match scoring",
                isinstance(score, (int, float)) and 0 <= score <= 100,
                f"Latency {ms}ms -- score={score}/100", (in_tok, out_tok))
    except Exception as exc:
        _result("Batch match scoring", False, str(exc))


# ---------------------------------------------------------------------------
# TEST 9 -- Skill feedback
# ---------------------------------------------------------------------------
async def test_9_skill_feedback(client) -> None:
    _section("TEST 9 -- Skill feedback (technical advice)")
    try:
        t0   = time.time()
        resp = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Python expert. Be specific and concise."},
                {"role": "user",   "content": (
                    "Skill: Python | Score: 72/100 | Band: Intermediate\n"
                    "Give 3-4 sentences: what's working, 1 gap, 1 concrete next step."
                )},
            ],
            max_tokens=200, temperature=0.3,
        )
        ms      = int((time.time() - t0) * 1000)
        text    = resp.choices[0].message.content.strip()
        in_tok  = resp.usage.prompt_tokens
        out_tok = resp.usage.completion_tokens
        _result("Skill feedback", len(text) > 50,
                f"Latency {ms}ms -- '{text[:200]}'", (in_tok, out_tok))
    except Exception as exc:
        _result("Skill feedback", False, str(exc))


# ---------------------------------------------------------------------------
# TEST 10 -- Cost summary
# ---------------------------------------------------------------------------
def test_10_cost_summary() -> None:
    _section("TEST 10 -- Token usage & estimated cost")
    cost = (
        (Decimal(total_input_tokens)  / 1_000_000) * COST_INPUT
      + (Decimal(total_output_tokens) / 1_000_000) * COST_OUTPUT
    )
    n_ai = 7
    print(f"  Model         : {MODEL}")
    print(f"  Input  tokens : {total_input_tokens:,}")
    print(f"  Output tokens : {total_output_tokens:,}")
    print(f"  Total  tokens : {total_input_tokens + total_output_tokens:,}")
    print(f"  Estimated cost: ${cost:.6f}  ({n_ai} AI calls)")
    if total_input_tokens:
        print(f"  At 1000 req/day: ~${float(cost) * 1000 / n_ai:.4f}/day")
    _result("Cost summary", True, f"${cost:.6f} for this test run")


# ---------------------------------------------------------------------------
# Final report
# ---------------------------------------------------------------------------
def _final_report() -> None:
    _section("FINAL REPORT")
    passed = sum(1 for r in results if r["passed"])
    total  = len(results)
    print(f"  Passed : {passed}/{total}")
    print(f"  Failed : {total - passed}/{total}")
    print()
    for r in results:
        icon = "[OK]" if r["passed"] else "[XX]"
        print(f"  {icon}  {r['test']}")
    print()
    if passed == total:
        print("  All tests passed! gpt-4.1-mini is fully connected.")
        print("  All 6 AI features are ready to wire up.")
    elif passed >= total - 2:
        print("  Core connection working. Check failed tests above.")
    else:
        print("  Connection failed -- see TEST 1 probe output for details.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
async def main() -> None:
    print()
    print("=" * 70)
    print("  Mavericks Ascend -- Azure AI Foundry Connection Test")
    print("=" * 70)
    print(f"  Endpoint    : {ENDPOINT}")
    print(f"  Model       : {MODEL}")
    print(f"  Key prefix  : {API_KEY[:20]}...")
    print("=" * 70)

    # TEST 1 -- discover working version + auth header
    http_ok = test_1_raw_http()

    # TEST 2 -- SDK (uses winning API_VERSION from test 1)
    sdk_ok, client = await test_2_sdk_ping()
    if not sdk_ok or client is None:
        _final_report()
        return

    # TESTS 3-9
    await test_3_models(client)
    await test_4_resume_parsing(client)
    await test_5_skill_extraction(client)
    await test_6_profile_summary(client)
    await test_7_performance_insights(client)
    await test_8_batch_match(client)
    await test_9_skill_feedback(client)

    # TEST 10
    test_10_cost_summary()
    _final_report()
    await client.close()


if __name__ == "__main__":
    missing = []
    for pkg in ["openai", "httpx"]:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"Missing: {', '.join(missing)}  -- run: pip install {' '.join(missing)}")
        sys.exit(1)
    asyncio.run(main())
