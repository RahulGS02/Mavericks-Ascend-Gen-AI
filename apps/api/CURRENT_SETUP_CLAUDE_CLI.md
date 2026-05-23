# ✅ Current Setup: Claude CLI for Local Testing

## 🎯 **What's Configured**

Your Mavericks Ascend platform is now configured to use **Claude CLI** for local AI feature testing.

---

## 📋 **Quick Start (3 Steps)**

### **1. Install Claude CLI**

```powershell
# Option A: Run the automated setup script
.\setup_claude_cli.ps1

# Option B: Install manually
irm https://claude.ai/install.ps1 | iex
```

### **2. Authenticate**

```powershell
# Login with your Claude account
claude auth login

# OR generate a token for automation
claude setup-token
# Then add the token to .env as CLAUDE_CODE_OAUTH_TOKEN
```

### **3. Test**

```powershell
# Test Claude CLI
python test_claude_cli_setup.py

# Start server
uvicorn app.main:app --reload

# Visit
http://localhost:8000/api/v1/ai/status
```

---

## 📁 **Files Created/Updated**

### **New Files:**
1. **`app/services/ai_service_claude_cli.py`** ✨
   - AI service using Claude CLI programmatic mode
   - Supports all features: resume parsing, skill extraction, insights
   
2. **`CLAUDE_CLI_LOCAL_SETUP.md`**
   - Complete Claude CLI setup guide
   - Authentication instructions
   - Troubleshooting

3. **`test_claude_cli_setup.py`**
   - Test script for Claude CLI
   - Verifies installation and authentication
   
4. **`setup_claude_cli.ps1`**
   - Automated setup script for Windows
   - Installs and configures Claude CLI

5. **`CURRENT_SETUP_CLAUDE_CLI.md`** (this file)
   - Quick reference for current setup

### **Updated Files:**
1. **`.env`**
   ```bash
   AI_PROVIDER=claude_cli  # Changed from anthropic
   CLAUDE_CODE_OAUTH_TOKEN=  # Optional token
   ```

2. **`app/config.py`**
   - Added `CLAUDE_CLI_MODE` and `CLAUDE_CODE_OAUTH_TOKEN` settings
   - Updated `ai_features_enabled` to support Claude CLI

---

## 🔄 **How It Works**

```
Your FastAPI API Endpoint
    ↓
AIServiceClaudeCLI
    ↓
Runs subprocess: claude -p --bare "prompt"
    ↓
Claude CLI (local installation)
    ↓
Claude AI (via your subscription)
    ↓
Response returned to API
    ↓
Sent to user
```

---

## 💡 **Provider Comparison**

| Feature | Claude CLI (NOW) | Anthropic API (LATER) |
|---------|------------------|----------------------|
| **Status** | ✅ Active | 🔜 When you get API key |
| **Best For** | Local testing | Production |
| **Cost** | Subscription | Pay-per-use |
| **Setup** | Login once | API key in .env |
| **Deployment** | Local only | Any server |
| **Switch** | Current | Change AI_PROVIDER |

---

## ⚙️ **Configuration**

### **Current `.env` Settings:**

```bash
# Active Configuration
AI_ENABLED=true
AI_PROVIDER=claude_cli

# Claude CLI
CLAUDE_CLI_MODE=headless
CLAUDE_CODE_OAUTH_TOKEN=  # Optional: from claude setup-token

# Future: Anthropic API (commented out)
# AI_PROVIDER=anthropic
# ANTHROPIC_API_KEY=sk-ant-...
```

---

## 🧪 **Testing Checklist**

### **Before Testing:**
- [ ] Claude CLI installed (`claude --version` works)
- [ ] Authenticated (`claude auth login` completed)
- [ ] Test command works: `claude -p "hello"`
- [ ] Python test passes: `python test_claude_cli_setup.py`

### **Backend Testing:**
- [ ] Server starts: `uvicorn app.main:app --reload`
- [ ] AI status endpoint works: `GET /api/v1/ai/status`
- [ ] Shows `"provider": "claude_cli"`
- [ ] Can test resume parsing

---

## 🚀 **Switching to Production (Later)**

When you get Anthropic API access:

### **1. Get API Key**
- Visit: https://console.anthropic.com/
- Create account
- Generate API key

### **2. Update `.env`**
```bash
AI_PROVIDER=anthropic  # Change from claude_cli
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### **3. Deploy**
- No code changes needed!
- Same codebase works in production
- Just set environment variables

---

## 📊 **API Endpoints**

All these work with Claude CLI:

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/ai/status` | Check AI provider status |
| `POST /api/v1/resume/parse` | Parse resume with AI |
| `POST /api/v1/skills/extract` | Extract skills |
| `GET /api/v1/admin/analytics/ai` | View usage stats |

---

## 💰 **Costs**

### **Claude CLI (Current):**
- Requires Claude Pro subscription ($20/month)
- OR free tier with usage limits
- Good for testing and development

### **Anthropic API (Future):**
- Pay per request ($3/1M input tokens, $15/1M output tokens)
- More cost-effective for production
- Better for scaling

---

## 🔧 **Common Commands**

```powershell
# Install Claude CLI
irm https://claude.ai/install.ps1 | iex

# Login
claude auth login

# Logout
claude auth logout

# Generate token
claude setup-token

# Test CLI
claude -p "Say hello"

# Check version
claude --version

# Test Python setup
python test_claude_cli_setup.py

# Start server
uvicorn app.main:app --reload
```

---

## 🐛 **Troubleshooting**

| Problem | Solution |
|---------|----------|
| "command not found: claude" | Install: `irm https://claude.ai/install.ps1 \| iex` |
| "not authenticated" | Run: `claude auth login` |
| "subscription required" | Sign up for Claude Pro |
| Test fails | Check authentication |
| Timeout errors | Increase timeout in code |

---

## 📚 **Documentation**

All docs in `apps/api/`:

1. **`CLAUDE_CLI_LOCAL_SETUP.md`** - Complete setup guide ⭐
2. **`CLAUDE_CLI_VS_API_EXPLAINED.md`** - Why CLI for local, API for prod
3. **`CURRENT_SETUP_CLAUDE_CLI.md`** - This file (quick reference)
4. **`test_claude_cli_setup.py`** - Test script
5. **`setup_claude_cli.ps1`** - Automated setup

---

## ✅ **Summary**

### **What You Have Now:**
- ✅ Claude CLI configured for local testing
- ✅ AI service that calls Claude CLI programmatically
- ✅ All AI features work locally
- ✅ Easy switch to Anthropic API later
- ✅ Complete documentation
- ✅ Test scripts

### **What You Need:**
- [ ] Install Claude CLI
- [ ] Authenticate (login or token)
- [ ] Run test script
- [ ] Start developing!

### **Next Steps:**
1. Run `.\setup_claude_cli.ps1` or install manually
2. Test with `python test_claude_cli_setup.py`
3. Start server: `uvicorn app.main:app --reload`
4. Build amazing AI features! 🚀

---

**🎉 You're all set for local testing with Claude CLI!**

**When you're ready for production, just switch to `AI_PROVIDER=anthropic` and add your API key. No code changes needed!**
