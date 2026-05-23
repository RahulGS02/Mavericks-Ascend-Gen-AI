# 🎯 Anthropic Claude API Setup Guide

## 📋 Overview

This guide covers setting up **Anthropic Claude API** for your Mavericks Ascend platform. Claude API is recommended for **both local development and production** environments.

---

## 🤔 **Claude CLI vs Claude API - Important Distinction**

### ❌ **Claude CLI** (NOT recommended for production backend)
- **Purpose:** Interactive coding assistant in your terminal/IDE
- **Authentication:** OAuth (browser-based) or API key
- **Use Case:** Personal development, code generation, chatting with AI
- **Platform:** Desktop application (Augment Desktop)
- **NOT suitable for:** Backend APIs, automated features, production servers

### ✅ **Claude API** (Anthropic API - RECOMMENDED)
- **Purpose:** Programmatic API access for applications
- **Authentication:** API Key from Anthropic Console
- **Use Case:** Production backends, API endpoints, automated AI features
- **Platform:** HTTPS REST API
- **Perfect for:** Your Mavericks Ascend platform's AI features

---

## 🚀 **Setup for Anthropic Claude API**

### **Step 1: Get Your API Key**

1. **Visit:** https://console.anthropic.com/
2. **Sign up/Login** with your credentials
3. **Navigate to:** API Keys section
4. **Create New Key:**
   - Click "Create Key"
   - Give it a name (e.g., "Mavericks Ascend Platform")
   - Copy the API key (starts with `sk-ant-...`)
   - **⚠️ IMPORTANT:** Save it securely - you won't see it again!

### **Step 2: Install Dependencies (Local Machine)**

#### **Windows (PowerShell)**
```powershell
# Navigate to project
cd C:\rahul\GenAi\GEN-AI-project\apps\api

# Install Python dependencies
pip install -r requirements.txt

# Or install Anthropic SDK specifically
pip install anthropic==0.25.2
```

#### **Linux/Mac**
```bash
# Navigate to project
cd /path/to/GEN-AI-project/apps/api

# Install dependencies
pip3 install -r requirements.txt

# Or install Anthropic SDK specifically
pip3 install anthropic==0.25.2
```

### **Step 3: Configure Environment Variables**

Edit your `.env` file:

```bash
# apps/api/.env

# AI Configuration
AI_ENABLED=true
AI_PROVIDER=anthropic

# Anthropic Claude API (Production & Local)
ANTHROPIC_API_KEY=sk-ant-your-actual-api-key-here
ANTHROPIC_MODEL=claude-sonnet-4-20250514
ANTHROPIC_MAX_TOKENS=4000
ANTHROPIC_TEMPERATURE=0.7

# Auggie SDK (Commented Out)
# AI_API_KEY=94fca94090d4fee5dc35227e2d5e5b21527b668dc0e8acafd567117aa3839968
# AI_MODEL=claude-sonnet-4.5

# AI Usage Limits
AI_DAILY_REQUEST_LIMIT=1000
AI_RATE_LIMIT_PER_MINUTE=60

# AI Feature Flags
AI_RESUME_PARSING_ENABLED=true
AI_SKILL_EXTRACTION_ENABLED=true
AI_PERFORMANCE_INSIGHTS_ENABLED=true
```

### **Step 4: Verify Installation**

Create a test script `test_anthropic_setup.py`:

```python
import asyncio
from anthropic import AsyncAnthropic
import os
from dotenv import load_dotenv

load_dotenv()

async def test_anthropic():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in .env")
        return
    
    print(f"✅ API Key found: {api_key[:20]}...")
    
    client = AsyncAnthropic(api_key=api_key)
    
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        messages=[{"role": "user", "content": "Say hello!"}]
    )
    
    print(f"✅ Response: {response.content[0].text}")
    print(f"✅ Tokens used: {response.usage.input_tokens} in, {response.usage.output_tokens} out")

if __name__ == "__main__":
    asyncio.run(test_anthropic())
```

Run the test:
```bash
python test_anthropic_setup.py
```

### **Step 5: Start the Application**

```bash
# Development server
uvicorn app.main:app --reload --port 8000

# Or using Python directly
python -m uvicorn app.main:app --reload
```

---

## 📦 **Complete Local Dependencies Checklist**

### **Python 3.11+ Required**

### **Core Dependencies**
- ✅ `anthropic==0.25.2` - Anthropic Claude API client
- ✅ `fastapi==0.115.4` - Web framework
- ✅ `uvicorn==0.27.1` - ASGI server
- ✅ `pydantic==2.8.2` - Data validation
- ✅ `python-dotenv==1.0.0` - Environment variables
- ✅ `httpx` - Async HTTP client (used by Anthropic SDK)

### **Optional (if switching back to Auggie)**
- ⚪ `auggie-sdk` - Auggie SDK

### **Database & Other Services**
- ✅ PostgreSQL (via Supabase or local)
- ✅ All dependencies from `requirements.txt`

---

## 🔧 **Configuration Options**

### **Switch Between Providers**

In `.env`, change `AI_PROVIDER`:

```bash
# Use Anthropic Claude API (Recommended)
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key

# OR Use Auggie SDK
AI_PROVIDER=auggie
AI_API_KEY=your-auggie-key
```

The system will automatically route to the correct provider!

---

## 🌐 **Production Deployment**

### **Environment Variables for Production**

On your hosting platform (Azure, AWS, Vercel, etc.), set:

```
AI_ENABLED=true
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-production-key
ANTHROPIC_MODEL=claude-sonnet-4-20250514
```

### **Why Anthropic API is Better for Production**

| Feature | Claude CLI | Claude API |
|---------|-----------|-----------|
| **Authentication** | OAuth/Browser | API Key |
| **Deployment** | Desktop only | Any server |
| **Automation** | ❌ Not suitable | ✅ Perfect |
| **Scalability** | Single user | Unlimited |
| **Cost Control** | N/A | Token-based pricing |
| **Production Ready** | ❌ No | ✅ Yes |

---

## 💰 **Pricing (Anthropic Claude Sonnet 4)**

- **Input:** $3.00 per 1M tokens
- **Output:** $15.00 per 1M tokens

**Example costs:**
- Resume parsing (500 words): ~$0.003
- 1000 resumes/day: ~$3.00/day
- Much cheaper than manual processing!

---

## 📊 **Monitoring Usage**

### **API Endpoint**

```bash
GET http://localhost:8000/api/v1/ai/status
```

Response:
```json
{
  "enabled": true,
  "available": true,
  "provider": "anthropic",
  "model": "claude-sonnet-4-20250514",
  "usage": {
    "request_count": 150,
    "input_tokens": 45000,
    "output_tokens": 12000,
    "total_cost": 0.315
  }
}
```

---

## 🧪 **Testing Locally**

### **Test Resume Parsing**

```bash
curl -X POST http://localhost:8000/api/v1/resume/parse \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "resume_text": "John Doe\nSoftware Engineer\n5 years Python experience..."
  }'
```

### **Test Skill Extraction**

```bash
curl -X POST http://localhost:8000/api/v1/skills/extract \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "text": "Expert in Python, React, PostgreSQL..."
  }'
```

---

## ❓ **FAQs**

### **Q: Can I use Claude CLI for the backend?**
**A:** No. Claude CLI is a desktop tool for interactive coding. For automated backend features, use the **Anthropic Claude API**.

### **Q: Does Claude API work in production?**
**A:** Yes! It's specifically designed for production applications. Just set your API key in production environment variables.

### **Q: Can I switch back to Auggie SDK?**
**A:** Yes! Just change `AI_PROVIDER=auggie` in your `.env` file. Both providers are supported.

### **Q: Which provider should I use?**
**A:**
- **Anthropic Claude API:** Best for production, well-documented, stable
- **Auggie SDK:** Good if you already have an Auggie subscription

### **Q: Is OAuth needed for Claude API?**
**A:** No. Claude API uses simple API key authentication. OAuth is only for Claude CLI (desktop app).

---

## ✅ **Quick Start Checklist**

- [ ] Install Python 3.11+
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Get Anthropic API key from https://console.anthropic.com/
- [ ] Add `ANTHROPIC_API_KEY` to `.env` file
- [ ] Set `AI_PROVIDER=anthropic` in `.env`
- [ ] Run test: `python test_anthropic_setup.py`
- [ ] Start server: `uvicorn app.main:app --reload`
- [ ] Test endpoint: `GET http://localhost:8000/api/v1/ai/status`
- [ ] Deploy to production with environment variables

---

## 📚 **Additional Resources**

- **Anthropic Console:** https://console.anthropic.com/
- **API Documentation:** https://docs.anthropic.com/
- **Pricing:** https://www.anthropic.com/pricing
- **Python SDK:** https://github.com/anthropics/anthropic-sdk-python

---

**🎉 You're all set! Your platform now supports both local development and production deployment with Anthropic Claude API!**
