# AI Integration Guide

## Overview

This application uses AI services for intelligent features like resume parsing, skill extraction, and performance insights. The AI integration is designed with cost control and environment-based enabling/disabling.

## Current Configuration

- **Provider**: Auggie SDK
- **Model**: Claude Sonnet 4.5
- **Status**: Environment-controlled (disabled in production by default)

## Environment Variables

### Development (.env)
```env
# Enable AI in development
AI_ENABLED=true
AI_API_KEY=your_auggie_api_key_here
AI_MODEL=claude-sonnet-4.5
AI_MAX_TOKENS=4000
AI_TEMPERATURE=0.7

# Cost Control
AI_DAILY_REQUEST_LIMIT=1000
AI_RATE_LIMIT_PER_MINUTE=60

# Feature Flags
AI_RESUME_PARSING_ENABLED=true
AI_SKILL_EXTRACTION_ENABLED=true
AI_PERFORMANCE_INSIGHTS_ENABLED=true
```

### Production (.env.production)
```env
# Disable AI in production to save costs
AI_ENABLED=false
AI_API_KEY=your_production_key_here
AI_MODEL=claude-sonnet-4.5
AI_MAX_TOKENS=4000
AI_TEMPERATURE=0.7

# Strict limits for production
AI_DAILY_REQUEST_LIMIT=100
AI_RATE_LIMIT_PER_MINUTE=10

# Selective features
AI_RESUME_PARSING_ENABLED=true
AI_SKILL_EXTRACTION_ENABLED=true
AI_PERFORMANCE_INSIGHTS_ENABLED=false
```

## AI Features

### 1. Resume Parsing
Extracts structured data from resume text:
- Name, email, phone
- Education history
- Skills
- Experience
- Projects

**Feature Flag**: `AI_RESUME_PARSING_ENABLED`

### 2. Skill Extraction
Automatically identifies technical skills from resume content.

**Feature Flag**: `AI_SKILL_EXTRACTION_ENABLED`

### 3. Performance Insights
Generates insights and recommendations based on:
- Assessment scores
- Job progress
- Training completion

**Feature Flag**: `AI_PERFORMANCE_INSIGHTS_ENABLED`

## Cost Control Mechanisms

### 1. Environment-Based Toggle
- **Development**: AI enabled for testing
- **Production**: AI disabled by default
- Must set `AI_ENABLED=true` explicitly in production

### 2. Rate Limiting
- **Per Minute**: Default 60 requests/minute
- **Daily**: Default 1000 requests/day
- Configurable via `AI_RATE_LIMIT_PER_MINUTE` and `AI_DAILY_REQUEST_LIMIT`

### 3. Feature Flags
Disable individual features to control costs:
```env
AI_RESUME_PARSING_ENABLED=false  # Disable resume parsing
AI_SKILL_EXTRACTION_ENABLED=true  # Keep skill extraction
AI_PERFORMANCE_INSIGHTS_ENABLED=false  # Disable insights
```

### 4. Token Limits
Maximum tokens per request controlled via `AI_MAX_TOKENS`

## Monitoring AI Usage

### Get AI Status
```bash
curl -X GET "http://localhost:8000/api/v1/ai/status" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "enabled": true,
  "available": true,
  "environment": "development",
  "model": "claude-sonnet-4.5",
  "features": {
    "resume_parsing": true,
    "skill_extraction": true,
    "performance_insights": true
  },
  "usage": {
    "requests_today": 45,
    "tokens_used": 12500,
    "daily_limit": 1000,
    "rate_limit_per_minute": 60,
    "last_reset": "2026-04-23T10:00:00"
  }
}
```

### Get AI Config (HR/Admin only)
```bash
curl -X GET "http://localhost:8000/api/v1/ai/config" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## Switching AI Providers

To switch from Auggie to another provider (e.g., OpenAI, Anthropic):

1. **Update .env**:
```env
AI_API_KEY=your_new_provider_key
AI_MODEL=new-model-name
```

2. **Update API calls in `app/services/ai_service.py`**:
```python
# Modify the _call_ai method
async def _call_ai(self, prompt: str, ...):
    # Update base_url
    self.base_url = "https://api.newprovider.com/v1"
    
    # Update request format if needed
    response = await client.post(
        f"{self.base_url}/completions",  # Update endpoint
        headers={...},  # Update headers
        json={...}  # Update request body format
    )
    
    # Update response parsing if needed
    return response.json()["response_field"]
```

3. **No other code changes needed!**

All AI features will automatically use the new provider.

## Best Practices

1. **Development**: Test AI features freely with `AI_ENABLED=true`
2. **Staging**: Use lower limits for cost control
3. **Production**: Start with `AI_ENABLED=false`, enable gradually
4. **Monitor**: Check `/api/v1/ai/status` regularly
5. **Optimize**: Disable unused features to save costs

## Graceful Degradation

If AI is disabled or unavailable:
- Resume parsing returns empty data
- Skill extraction returns empty array
- Profile summaries are skipped
- **Application continues to work normally**

No errors or failures - AI features are optional enhancements.
