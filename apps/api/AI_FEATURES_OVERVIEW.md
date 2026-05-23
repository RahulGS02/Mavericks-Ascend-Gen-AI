# 🤖 AI Features Overview - Mavericks Ascend

## 🎯 AI Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                          │
│                 http://localhost:3000                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTP/REST API
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  FastAPI Backend                                │
│               http://localhost:8000                             │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Endpoints (/api/v1/*)                              │  │
│  │  • /ai/status                                           │  │
│  │  • /resume/parse                                        │  │
│  │  • /batch-suggestions/*                                 │  │
│  │  • /skill-proficiency/*                                 │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│                         │                                       │
│                         ▼                                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  AIService (app/services/ai_service.py)                 │  │
│  │  • DirectContext initialization                         │  │
│  │  • SSL patches                                          │  │
│  │  • Cost tracking (AIUsageTracker)                       │  │
│  │  • Rate limiting                                        │  │
│  │  • Retry logic                                          │  │
│  └──────────────────────┬───────────────────────────────────┘  │
│                         │                                       │
└─────────────────────────┼───────────────────────────────────────┘
                          │
                          │ DirectContext.search_and_ask()
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              Auggie SDK (auggie-sdk)                            │
│                 DirectContext                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTPS (SSL disabled)
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│         Augment AI API (Tenant-Specific)                        │
│      https://e7.api.augmentcode.com/                            │
│                                                                 │
│            Claude Sonnet 4.5 Model                              │
└─────────────────────────────────────────────────────────────────┘
```

## 🎨 AI Features Implemented

### 1️⃣ Resume Parsing 📄

**Purpose**: Extract structured information from resumes (PDF/DOCX)

**Endpoint**: `POST /api/v1/resume/parse`

**What it extracts**:
- Personal information (name, email, phone)
- Education history (degree, college, year, CGPA)
- Work experience (companies, roles, duration)
- Technical skills (programming, frameworks, tools)
- Projects
- AI-generated summary
- Total experience years

**Usage**:
```python
# API Call
POST /api/v1/resume/parse
Content-Type: multipart/form-data
file: [resume.pdf]

# Response
{
  "personal_info": {...},
  "education": [...],
  "skills": {...},
  "summary": "AI-generated summary"
}
```

### 2️⃣ Skill Extraction 🎯

**Purpose**: Identify technical skills from resume text

**Method**: `extract_skills_from_resume(resume_text)`

**Returns**: `["Python", "React", "Docker", "AWS", ...]`

**Used in**:
- Resume parsing workflow
- Maverick profile creation
- Skill matching for batches

### 3️⃣ Performance Insights 📊

**Purpose**: Analyze maverick performance and generate insights

**Method**: `get_performance_insights(maverick_data)`

**Analyzes**:
- Assessment scores over time
- Skill proficiency trends
- Job completion rates
- Identifies at-risk mavericks
- Generates recommendations

**Example Output**:
```
"Strong performance in Python and React assessments. 
Recommend advanced JavaScript training. 
On track for deployment readiness."
```

### 4️⃣ Batch Suggestions (AI Matching) 🔄

**Purpose**: Match mavericks to optimal batches using AI

**Endpoints**:
- `GET /batch-suggestions/maverick/{id}` - Find best batches for a maverick
- `GET /batch-suggestions/batch/{id}/suggest-mavericks` - Find best mavericks for a batch

**Algorithm**:
1. Extract skills from maverick profile
2. Compare with batch pipeline requirements
3. Calculate similarity scores
4. Rank by best fit
5. Return top 5 recommendations

**Response**:
```json
{
  "suggestions": [
    {
      "batch_id": 123,
      "batch_name": "Full Stack Q1 2024",
      "match_score": 0.87,
      "matching_skills": ["Python", "React", "PostgreSQL"],
      "reason": "Strong alignment with pipeline requirements"
    }
  ]
}
```

### 5️⃣ Skill Proficiency Tracking 📈

**Purpose**: Track skill development over time

**Endpoint**: `GET /skill-proficiency/maverick/{id}`

**Features**:
- Automatic skill level updates from assessments
- Proficiency levels: Beginner → Intermediate → Advanced → Expert
- Growth tracking over time
- Skill matrix visualization

**Data Structure**:
```json
{
  "skill": "Python",
  "proficiency_level": "Advanced",
  "current_score": 8.5,
  "assessments_count": 5,
  "first_assessed": "2024-01-15",
  "last_assessed": "2024-03-20",
  "growth": "+2.5 points"
}
```

## 💰 Cost Tracking & Control

### Usage Tracker (AIUsageTracker)

**Tracks**:
- Total requests
- Input tokens used
- Output tokens used
- Cost per request
- Cost by feature
- Error rate
- Retry count

**Cost Calculation**:
```
Input tokens:  $0.003 per 1K tokens
Output tokens: $0.015 per 1K tokens
Total cost = (input_tokens/1000 * $0.003) + (output_tokens/1000 * $0.015)
```

### Rate Limits

- **Per minute**: 60 requests
- **Per day**: 1,000 requests
- **Auto-blocking**: When limits exceeded

### Monitoring Endpoints

1. **User-level**: `GET /api/v1/ai/status`
   ```json
   {
     "enabled": true,
     "available": true,
     "usage": {
       "requests_today": 45,
       "total_cost_usd": 0.23
     }
   }
   ```

2. **Admin-level**: `GET /api/v1/admin/analytics/ai`
   ```json
   {
     "total_requests": 1234,
     "total_tokens": 456789,
     "total_cost": 12.34,
     "requests_by_feature": {
       "resume_parsing": {
         "count": 234,
         "cost_usd": 4.56
       }
     }
   }
   ```

## 🔧 Technical Implementation

### DirectContext Connection

```python
# Initialize DirectContext
context = DirectContext.create(
    api_key=settings.AI_API_KEY,
    api_url="https://e7.api.augmentcode.com/",
    debug=False
)

# Initialize index (required)
context.add_to_index([
    File(path='_init.txt', contents='Initialization placeholder')
])

# Make AI call
response = context.search_and_ask(
    search_query="",
    prompt="Your prompt here"
)
```

### SSL Patches

Self-signed certificates handled automatically:
```python
# SSL verification disabled
urllib3.disable_warnings()
ssl._create_default_https_context = ssl._create_unverified_context
```

### Retry Logic

```python
max_retries = 3
retry_delay = 5  # seconds

# Retries on transient errors:
# - timeout
# - connection errors
# - "ended prematurely"
```

## 📊 Feature Flags

Control which AI features are enabled:

```env
AI_RESUME_PARSING_ENABLED=true
AI_SKILL_EXTRACTION_ENABLED=true
AI_PERFORMANCE_INSIGHTS_ENABLED=true
```

Each feature checks its flag before executing:
```python
if not settings.AI_RESUME_PARSING_ENABLED:
    return {}  # Skip AI processing
```
