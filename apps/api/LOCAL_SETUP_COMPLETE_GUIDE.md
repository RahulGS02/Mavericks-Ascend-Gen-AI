# 🚀 Complete Local Setup Guide for Mavericks Ascend AI Integration

## 📋 **What You're Setting Up**

Integrating **Anthropic Claude API** into your Mavericks Ascend platform for AI-powered features:
- Resume parsing
- Skill extraction
- Performance insights
- Automated matching

This setup works for **BOTH local development AND production deployment**.

---

## 🛠️ **Prerequisites**

### **1. Software Installation**

#### **Python 3.11 or higher**
```powershell
# Check your Python version
python --version

# Should show: Python 3.11.x or higher
```

If you don't have Python 3.11+, download from: https://www.python.org/downloads/

#### **Git** (should already be installed)
```powershell
git --version
```

#### **PostgreSQL** (via Supabase - already set up)
- Your Supabase database is already configured
- No local installation needed

---

## 📦 **Step-by-Step Installation**

### **Step 1: Navigate to Project**

```powershell
# Open PowerShell
cd C:\rahul\GenAi\GEN-AI-project\apps\api
```

### **Step 2: Install Python Dependencies**

```powershell
# Install all required packages
pip install -r requirements.txt

# This installs:
# - anthropic (Claude API client)
# - fastapi (web framework)
# - all other dependencies
```

**Expected output:**
```
Successfully installed anthropic-0.25.2 fastapi-0.115.4 ...
```

### **Step 3: Get Your Anthropic API Key**

1. **Visit:** https://console.anthropic.com/
2. **Sign up** or **Log in** with your account
3. **Navigate to "API Keys"** in the dashboard
4. **Click "Create Key"**
   - Name: "Mavericks Ascend Local Dev"
   - Copy the key (starts with `sk-ant-...`)
5. **Save it securely** - you'll only see it once!

💡 **Free Tier:** Anthropic offers free credits for testing

### **Step 4: Configure Environment Variables**

Open `apps/api/.env` and update:

```bash
# Database (already configured)
DATABASE_URL=your_existing_database_url
SUPABASE_URL=your_existing_supabase_url
SUPABASE_SERVICE_KEY=your_existing_key

# JWT (already configured)
JWT_SECRET=your_existing_secret

# AI Configuration - ADD THESE
AI_ENABLED=true
AI_PROVIDER=anthropic

# Anthropic Claude API
ANTHROPIC_API_KEY=sk-ant-your-actual-api-key-paste-here
ANTHROPIC_MODEL=claude-sonnet-4-20250514
ANTHROPIC_MAX_TOKENS=4000
ANTHROPIC_TEMPERATURE=0.7

# AI Usage Limits
AI_DAILY_REQUEST_LIMIT=1000
AI_RATE_LIMIT_PER_MINUTE=60

# AI Feature Flags
AI_RESUME_PARSING_ENABLED=true
AI_SKILL_EXTRACTION_ENABLED=true
AI_PERFORMANCE_INSIGHTS_ENABLED=true

# Auggie SDK (Optional - Commented Out)
# AI_API_KEY=94fca94090d4fee5dc35227e2d5e5b21527b668dc0e8acafd567117aa3839968
# AI_MODEL=claude-sonnet-4.5
```

### **Step 5: Verify Installation**

```powershell
# Run the test script
python test_anthropic_setup.py
```

**Expected output:**
```
======================================================================
🧪 Anthropic Claude API Setup Test
======================================================================

Test 1: Environment Configuration
----------------------------------------------------------------------
AI_ENABLED: true
AI_PROVIDER: anthropic
✅ ANTHROPIC_API_KEY found: sk-ant-api01-wLxxx...

Test 2: Anthropic SDK Installation
----------------------------------------------------------------------
✅ anthropic SDK imported successfully
   Version: 0.25.2

Test 3: Anthropic API Connection Test
----------------------------------------------------------------------
✅ AsyncAnthropic client created successfully

📤 Sending test request to Anthropic API...
✅ API call successful!

📥 Response:
   Content: Hello from Anthropic!
   Model: claude-sonnet-4-20250514
   Input tokens: 10
   Output tokens: 5
   Cost: $0.000105

======================================================================
📊 Test Summary
======================================================================

🎉 All tests passed!

✅ Anthropic Claude API is properly configured and working!
```

If you see this, **you're all set!** ✅

---

## 🚀 **Running the Application Locally**

### **Start the Development Server**

```powershell
# Option 1: Using uvicorn directly
uvicorn app.main:app --reload --port 8000

# Option 2: Using Python module
python -m uvicorn app.main:app --reload --port 8000
```

**You should see:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### **Access the API**

- **API Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

---

## 🧪 **Testing AI Features**

### **Test 1: Check AI Status**

```powershell
# Using curl (if installed)
curl http://localhost:8000/api/v1/ai/status

# Or open in browser:
# http://localhost:8000/api/v1/ai/status
```

**Expected response:**
```json
{
  "enabled": true,
  "available": true,
  "provider": "anthropic",
  "model": "claude-sonnet-4-20250514"
}
```

### **Test 2: Parse a Resume** (requires authentication)

1. First, create a test user and login via the API docs
2. Get your JWT token
3. Test the resume parsing endpoint

**Or use the interactive API docs:**
- Go to http://localhost:8000/docs
- Try the `/api/v1/ai/status` endpoint
- Explore all AI-powered endpoints

---

## 📊 **Local Dependencies Summary**

Here's everything installed on your local machine:

### **Core Python Packages**
```
✅ anthropic==0.25.2          # Claude API client
✅ fastapi==0.115.4           # Web framework
✅ uvicorn==0.27.1            # ASGI server
✅ pydantic==2.8.2            # Data validation
✅ sqlalchemy==2.0.23         # Database ORM
✅ psycopg2-binary==2.9.9     # PostgreSQL driver
✅ python-dotenv==1.0.0       # Environment variables
✅ httpx                      # Async HTTP client
✅ python-jose                # JWT tokens
✅ passlib                    # Password hashing
✅ python-multipart           # File uploads
✅ PyPDF2                     # PDF processing
✅ python-docx                # Word document processing
✅ pandas                     # Data processing
✅ openpyxl                   # Excel processing
```

### **Optional Packages**
```
⚪ auggie-sdk                 # Alternative AI provider (commented out)
⚪ pytest                     # Testing (for development)
```

All packages are listed in `requirements.txt` and installed with one command!

---

## 🔧 **Configuration Files**

### **Files You Need to Edit:**

1. **`.env`** - Environment variables
   - ✅ Add your `ANTHROPIC_API_KEY`
   - ✅ Set `AI_PROVIDER=anthropic`
   - ✅ Keep existing database/auth settings

2. **`requirements.txt`** - Already updated ✅
3. **`app/config.py`** - Already updated ✅
4. **`app/services/ai_service_anthropic.py`** - New multi-provider service ✅

---

## 🌐 **Production Deployment**

Good news! **The same setup works in production!**

### **On Azure App Service / AWS / Any Cloud:**

1. **Set Environment Variables:**
   ```
   AI_ENABLED=true
   AI_PROVIDER=anthropic
   ANTHROPIC_API_KEY=sk-ant-your-production-key
   ```

2. **Deploy your code** (same codebase)

3. **That's it!** No special configuration needed

---

## 🐛 **Troubleshooting**

### **Problem: "ModuleNotFoundError: No module named 'anthropic'"**

**Solution:**
```powershell
pip install anthropic==0.25.2
```

### **Problem: "ANTHROPIC_API_KEY not found"**

**Solution:**
1. Check `.env` file has the key
2. Make sure key starts with `sk-ant-`
3. Restart the server after adding the key

### **Problem: "API call failed: 401 Unauthorized"**

**Solution:**
1. Verify your API key is correct
2. Check key hasn't been revoked in Anthropic Console
3. Ensure key has sufficient credits

### **Problem: "Rate limit exceeded"**

**Solution:**
1. Check your usage in Anthropic Console
2. Increase `AI_RATE_LIMIT_PER_MINUTE` in `.env`
3. Implement request queuing

### **Problem: Server won't start**

**Solution:**
```powershell
# Check for port conflicts
netstat -ano | findstr :8000

# If port is in use, kill the process or use different port
uvicorn app.main:app --reload --port 8001
```

---

## ✅ **Complete Setup Checklist**

### **Initial Setup**
- [ ] Python 3.11+ installed
- [ ] Git installed
- [ ] Project cloned to local machine

### **Dependencies**
- [ ] Navigated to `apps/api` directory
- [ ] Ran `pip install -r requirements.txt`
- [ ] Verified all packages installed successfully

### **API Key**
- [ ] Created Anthropic account
- [ ] Generated API key from console
- [ ] Copied API key (starts with `sk-ant-`)

### **Configuration**
- [ ] Opened `apps/api/.env` file
- [ ] Added `ANTHROPIC_API_KEY=sk-ant-...`
- [ ] Set `AI_PROVIDER=anthropic`
- [ ] Set `AI_ENABLED=true`
- [ ] Saved the file

### **Testing**
- [ ] Ran `python test_anthropic_setup.py`
- [ ] Saw "All tests passed!" message
- [ ] Verified API connection works

### **Server**
- [ ] Started server with `uvicorn app.main:app --reload`
- [ ] Saw "Application startup complete" message
- [ ] Opened http://localhost:8000/docs in browser
- [ ] Tested `/api/v1/ai/status` endpoint

### **Production Ready**
- [ ] Understand how to deploy to production
- [ ] Know where to set environment variables
- [ ] Ready to develop AI features!

---

## 📚 **Additional Documentation**

Created for you:
- ✅ `ANTHROPIC_CLAUDE_SETUP.md` - Detailed Anthropic setup
- ✅ `CLAUDE_CLI_VS_API_EXPLAINED.md` - CLI vs API explanation
- ✅ `LOCAL_SETUP_COMPLETE_GUIDE.md` - This file
- ✅ `test_anthropic_setup.py` - Test script

Existing documentation:
- 📄 `AI_INTEGRATION.md` - AI architecture overview
- 📄 `PROJECT_STRUCTURE.md` - Project layout
- 📄 `SETUP.md` - General setup guide

---

## 🎯 **What's Next?**

Now that your local environment is set up:

1. **Start Development:**
   - Modify AI prompts in `ai_service_anthropic.py`
   - Add new AI features
   - Test with local API

2. **Test Features:**
   - Upload test resumes
   - Extract skills
   - Generate insights

3. **Deploy to Production:**
   - Same code, same configuration
   - Just set environment variables
   - Deploy and go!

---

## 💡 **Quick Reference**

### **Start Server**
```powershell
uvicorn app.main:app --reload
```

### **Test AI**
```powershell
python test_anthropic_setup.py
```

### **Check Logs**
Server logs appear in terminal where uvicorn is running

### **API Documentation**
http://localhost:8000/docs

---

## 🎉 **Congratulations!**

You now have:
- ✅ Anthropic Claude API integrated
- ✅ Local development environment ready
- ✅ Production-ready configuration
- ✅ Multi-provider AI support (Anthropic + Auggie)
- ✅ All dependencies installed
- ✅ Complete documentation

**You're ready to build amazing AI-powered features!** 🚀

---

## 📞 **Need Help?**

- **Anthropic Docs:** https://docs.anthropic.com/
- **Anthropic Console:** https://console.anthropic.com/
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Your Documentation:** See all the `.md` files in `apps/api/`

**Happy Coding! 🎊**
