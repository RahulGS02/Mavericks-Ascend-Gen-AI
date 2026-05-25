# 📚 AI-Powered Talent Search API Documentation

## 🎯 Overview

The AI-Powered Talent Search API provides intelligent candidate search with natural language queries, multi-factor scoring, and learning timeline estimation.

**Base URL:** `/api/v1/talent-search`

**Authentication:** Bearer Token (JWT)

**Required Roles:** HR, Manager, Super Admin

---

## 🔐 Authentication

All endpoints require a valid JWT token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

### Getting a Token

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "hr@maverick.com",
  "password": "your_password"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "email": "hr@maverick.com",
    "role": "HR"
  }
}
```

---

## 📍 API Endpoints

### 1. **AI-Powered Search**

Search for candidates using natural language queries.

**Endpoint:** `POST /api/v1/talent-search/search`

**Required Role:** HR, Manager, Super Admin

#### Request Body

```json
{
  "query": "Need .NET developer with Azure experience and CGPA > 8",
  "max_results": 50,
  "include_similar": false,
  "urgency": "flexible"
}
```

**Parameters:**
- `query` (string, required): Natural language search query
- `max_results` (integer, optional): Max results to return (1-100, default: 50)
- `include_similar` (boolean, optional): Include similar skill candidates (default: false)
- `urgency` (string, optional): "immediate" or "flexible" (default: "flexible")

#### Example Queries

```
"Need .NET developer with Azure experience and CGPA > 8"
"Python developer with React skills, available immediately"
"Java backend engineer with microservices experience"
"Frontend developer proficient in Angular or React"
"Data scientist with machine learning and Python"
```

#### Response (200 OK)

```json
{
  "query": "Need .NET developer with Azure experience and CGPA > 8",
  "search_strategy": "exact_only",
  "parsed_requirements": {
    "required_skills": [".NET", "Azure"],
    "preferred_skills": [],
    "min_cgpa": 8.0,
    "graduation_year": null,
    "degree": null,
    "branch": null
  },
  "total_found": 5,
  "results": [
    {
      "id": "uuid-here",
      "name": "John Doe",
      "email": "john@maverick.com",
      "cgpa": 8.5,
      "deployment_status": "AVAILABLE",
      "profile_status": "approved",
      "final_score": 87.5,
      "tier": "TIER_1_EXACT",
      "exact_matches": [
        {
          "skill": ".NET",
          "proficiency_score": 90.0,
          "proficiency_level": "PROFICIENT",
          "assessment_validated": true,
          "points": 100.0
        },
        {
          "skill": "Azure",
          "proficiency_score": 85.0,
          "proficiency_level": "INTERMEDIATE",
          "assessment_validated": true,
          "points": 100.0
        }
      ],
      "similar_matches": [],
      "transferable_matches": [],
      "missing_skills": [],
      "assessment_performance": {
        "average_score": 82.5,
        "total_assessments": 5,
        "passed_assessments": 5,
        "pass_rate": 100.0,
        "trend": "improving",
        "recent_activity": 3
      },
      "adaptability_score": 85.0,
      "adaptability_interpretation": "strong_learner",
      "deployment_readiness": "immediate",
      "learning_weeks_required": 0.0,
      "training_plan": [],
      "match_reasoning": "✅ Excellent match! Has 2 exact skill matches. Strong learning ability (top 20%). Ready for immediate deployment."
    }
  ],
  "summary": {
    "total_found": 5,
    "exact_matches": 3,
    "similar_skill_candidates": 2,
    "transferable_skill_candidates": 0,
    "immediate_deployment": 3,
    "short_training_needed": 2,
    "longer_training_needed": 0,
    "show_similar_button": false,
    "similar_available": 2
  },
  "cost_analysis": {
    "query_parsing_tokens": 500,
    "query_parsing_cost": 0.0015,
    "ranking_tokens": 0,
    "ranking_cost": 0.0,
    "total_tokens": 500,
    "total_cost": 0.0015
  },
  "message": "Found 3 exact matches.",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Error Responses

**401 Unauthorized**
```json
{
  "detail": "Could not validate credentials"
}
```

**403 Forbidden**
```json
{
  "detail": "Access denied. Required roles: ['HR', 'SUPER_ADMIN']"
}
```

**500 Internal Server Error**
```json
{
  "detail": "An unexpected error occurred during search: <error_message>"
}
```

---

### 2. **Explain Candidate Match**

Get detailed explanation of why a candidate was suggested.

**Endpoint:** `GET /api/v1/talent-search/explain/{candidate_id}`

**Required Role:** HR, Manager, Super Admin

#### Parameters

- `candidate_id` (path, UUID): Candidate's ID
- `required_skills` (query, string): Comma-separated required skills

#### Example Request

```bash
GET /api/v1/talent-search/explain/550e8400-e29b-41d4-a716-446655440000?required_skills=.NET,Azure
Authorization: Bearer <token>
```

#### Response (200 OK)

```json
{
  "candidate_id": "550e8400-e29b-41d4-a716-446655440000",
  "candidate_name": "John Doe",
  "skill_gap_analysis": {
    "exact_matches": [
      {
        "skill": ".NET",
        "proficiency_score": 90.0,
        "proficiency_level": "PROFICIENT"
      }
    ],
    "similar_matches": [],
    "transferable_matches": [],
    "missing_skills": [],
    "total_score": 95.0,
    "match_type": "PERFECT_MATCH"
  },
  "learning_path": [],
  "adaptability_breakdown": {
    "score": 85.0,
    "interpretation": "strong_learner",
    "assessment_trend": "improving",
    "skill_count": 8,
    "recent_activity": 3,
    "pass_rate": 100.0
  },
  "timeline_estimate": {
    "total_weeks": 0.0,
    "deployment_readiness": "immediate",
    "message": "✅ Ready for immediate deployment"
  },
  "match_reasoning": "✅ Has 2 exact skill match(es). 🌟 Exceptional learner (adaptability: 85/100). ⚡ Ready for immediate deployment.",
  "recommendation": "🌟 STRONGLY RECOMMENDED - Ready for immediate deployment with exceptional learning ability"
}
```

---

### 3. **Get Cost Estimate**

Get estimated cost for AI-powered talent search.

**Endpoint:** `GET /api/v1/talent-search/cost-estimate`

**Required Role:** HR, Manager, Super Admin

#### Example Request

```bash
GET /api/v1/talent-search/cost-estimate
Authorization: Bearer <token>
```

#### Response (200 OK)

```json
{
  "per_query_cost": {
    "query_parsing": 0.0015,
    "candidate_scoring": 0.0,
    "total": 0.0015
  },
  "monthly_estimates": {
    "100_queries": 0.15,
    "500_queries": 0.75,
    "1000_queries": 1.50,
    "5000_queries": 7.50
  },
  "token_usage": {
    "per_query": 500,
    "provider": "Auggie SDK",
    "model": "Claude Sonnet 4.5"
  },
  "optimization": {
    "sql_pre_filtering": "Reduces AI processing by ~80%",
    "rules_based_scoring": "No AI tokens for scoring",
    "cost_target": "< $0.003 per query"
  }
}
```

---

### 4. **Get Talent Pool Statistics**

Get statistics about available candidates.

**Endpoint:** `GET /api/v1/talent-search/statistics`

**Required Role:** HR, Manager, Super Admin

#### Example Request

```bash
GET /api/v1/talent-search/statistics
Authorization: Bearer <token>
```

#### Response (200 OK)

```json
{
  "talent_pool": {
    "total_available": 47,
    "deployment_status": "AVAILABLE",
    "profile_status": "APPROVED"
  },
  "top_skills": [
    {
      "skill": "Python",
      "candidate_count": 23,
      "avg_proficiency": 82.5
    },
    {
      "skill": "React",
      "candidate_count": 18,
      "avg_proficiency": 78.3
    },
    {
      "skill": "JavaScript",
      "candidate_count": 15,
      "avg_proficiency": 85.1
    }
  ],
  "cgpa_stats": {
    "average": 7.8,
    "minimum": 6.5,
    "maximum": 9.5
  }
}
```

---

## 🎯 Key Features

### 1. **Natural Language Query Parsing**

The system uses AI to extract structured requirements from natural language:

```
Query: "Need .NET developer with Azure, CGPA > 8"

Parsed:
- required_skills: [".NET", "Azure"]
- min_cgpa: 8.0
```

### 2. **Multi-Tier Results**

Candidates are categorized into tiers:

- **TIER_1_EXACT**: Has exact skill matches (ready now or < 1 week)
- **TIER_2_SIMILAR**: Has similar skills (1-4 weeks training)
  - Example: C# developer for .NET role
- **TIER_3_TRANSFERABLE**: Has transferable skills (4-8 weeks training)
  - Example: Java developer for .NET role

### 3. **Composite Scoring Algorithm**

```
Final Score = (
  Skill Match * 50% +
  Adaptability * 25% +
  Assessment Avg * 15% +
  CGPA * 10%
) - Tier Penalty

Tier Penalties:
- TIER_1: -0 points
- TIER_2: -5 points
- TIER_3: -10 points
```

### 4. **Adaptability Scoring**

4-factor weighted algorithm:
- Assessment trend (improving/stable/declining): 40%
- Skill diversity (number of skills): 30%
- Recent activity (last 3 months): 20%
- Pass rate: 10%

### 5. **Learning Timeline Estimation**

Predicts weeks required to bridge skill gaps:
- Base timeline from skill mappings
- Adjusted by candidate's adaptability score
- Exceptional learners: 30% faster
- Strong learners: 20% faster
- Good learners: 10% faster

### 6. **Smart "Show Similar" Logic**

```python
if exact_matches <= 2:
    show_similar_button = True
    message = "Show {n} Similar Candidates"
```

---

## 💡 Usage Examples

### Example 1: Find .NET Developer (Immediate Need)

```bash
curl -X POST "http://localhost:8000/api/v1/talent-search/search" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Need .NET developer with Azure, available immediately",
    "max_results": 20,
    "urgency": "immediate"
  }'
```

### Example 2: Find Python Developer (Include Similar)

```bash
curl -X POST "http://localhost:8000/api/v1/talent-search/search" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Python developer with machine learning",
    "max_results": 50,
    "include_similar": true
  }'
```

### Example 3: Explain Why Candidate Was Suggested

```bash
curl -X GET "http://localhost:8000/api/v1/talent-search/explain/CANDIDATE_ID?required_skills=Python,React" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔍 Response Field Descriptions

### Candidate Match Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Candidate's unique identifier |
| `name` | string | Candidate's full name |
| `email` | string | Candidate's email address |
| `cgpa` | float | CGPA (0-10 scale) |
| `deployment_status` | string | AVAILABLE, DEPLOYED, etc. |
| `profile_status` | string | approved, pending, rejected |
| `final_score` | float | Composite score (0-100) |
| `tier` | string | TIER_1_EXACT, TIER_2_SIMILAR, TIER_3_TRANSFERABLE |
| `exact_matches` | array | Exact skill matches |
| `similar_matches` | array | Similar skill matches (70-95% similarity) |
| `transferable_matches` | array | Transferable skills (50-70% similarity) |
| `missing_skills` | array | Skills candidate doesn't have |
| `assessment_performance` | object | Past assessment summary |
| `adaptability_score` | float | Learning potential score (0-100) |
| `adaptability_interpretation` | string | exceptional, strong, good, average |
| `deployment_readiness` | string | immediate, short_term, medium_term, long_term |
| `learning_weeks_required` | float | Weeks to bridge skill gaps |
| `training_plan` | array | Structured learning phases |
| `match_reasoning` | string | Human-readable explanation |

---

## ⚡ Performance & Cost

### Performance Metrics

- **Average Response Time:** < 2 seconds
- **SQL Pre-filtering:** Reduces candidates by ~80%
- **Concurrent Requests:** Supports up to 100 concurrent searches

### Cost Analysis

- **Per Query:** ~$0.0015 (500 AI tokens for parsing)
- **Monthly (1000 queries):** ~$1.50
- **Yearly (12,000 queries):** ~$18

### Cost Optimization

1. **SQL Pre-filtering**: Only AVAILABLE + APPROVED candidates
2. **Rules-based Scoring**: No AI tokens for candidate scoring
3. **Cached Skill Mappings**: No AI calls for skill similarity
4. **Batch Processing**: Efficient database queries

---

## 🚨 Error Handling

### Common Errors

| Status Code | Error | Solution |
|-------------|-------|----------|
| 401 | Unauthorized | Provide valid JWT token |
| 403 | Forbidden | User must be HR/Manager/Admin |
| 404 | Candidate not found | Check candidate ID |
| 422 | Validation error | Check request body format |
| 500 | Internal server error | Check server logs |

### Example Error Response

```json
{
  "detail": "Could not validate credentials",
  "status_code": 401
}
```

---

## 🧪 Testing

See integration tests in `tests/test_talent_search_api.py` for comprehensive examples.

Run tests:
```bash
cd apps/api
pytest tests/test_talent_search_api.py -v
```

---

## 📞 Support

For issues or questions:
- Check `/docs` endpoint for interactive API documentation
- Review `AI_TALENT_SEARCH_IMPLEMENTATION.md` for technical details
- Contact: admin@maverick.com
