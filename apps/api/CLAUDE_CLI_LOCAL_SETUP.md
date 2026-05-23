# 🖥️ Claude CLI Setup for Local Testing

## 📋 Overview

Since you don't have Anthropic API access yet, we'll set up **Claude CLI (Claude Code)** for local testing. Claude CLI can run in **programmatic/headless mode** which allows your FastAPI backend to call it.

---

## 🚀 **Step 1: Install Claude CLI**

### **Windows (PowerShell - Run as Administrator)**

```powershell
# Open PowerShell as Administrator
# Run the installer
irm https://claude.ai/install.ps1 | iex
```

### **Verify Installation**

```powershell
# Check version
claude --version

# Should show something like: claude-code version 1.x.x
```

---

## 🔑 **Step 2: Authenticate Claude CLI**

### **Option A: Interactive Login (For Local Testing)**

```powershell
# Login with your Claude account
claude auth login

# This will:
# 1. Open your browser
# 2. Ask you to sign in to Claude.ai
# 3. Save credentials locally
```

### **Option B: Generate Long-Lived Token (For Automation)**

```powershell
# Generate a token that won't expire
claude setup-token

# Copy the output token
# You'll use this as CLAUDE_CODE_OAUTH_TOKEN
```

**Save this token!** You'll need it for the `.env` file.

---

## ⚙️ **Step 3: Configure Environment Variables**

Edit `apps/api/.env`:

```bash
# AI Configuration
AI_ENABLED=true
AI_PROVIDER=claude_cli

# Claude CLI Configuration (Local Testing Only)
CLAUDE_CLI_MODE=headless
CLAUDE_CODE_OAUTH_TOKEN=your-token-from-setup-token-command

# OR if you don't want to use token (will use login credentials)
# Leave CLAUDE_CODE_OAUTH_TOKEN empty

# AI Usage Limits
AI_DAILY_REQUEST_LIMIT=1000
AI_RATE_LIMIT_PER_MINUTE=60

# AI Feature Flags
AI_RESUME_PARSING_ENABLED=true
AI_SKILL_EXTRACTION_ENABLED=true
AI_PERFORMANCE_INSIGHTS_ENABLED=true

# Anthropic API (Commented out - not available yet)
# AI_PROVIDER=anthropic
# ANTHROPIC_API_KEY=sk-ant-...

# Auggie SDK (Commented out)
# AI_PROVIDER=auggie
# AI_API_KEY=...
```

---

## 🛠️ **Step 4: Update Config to Support Claude CLI**

The configuration has already been updated to support multiple providers. Now we need to add Claude CLI support.

---

## 📝 **Step 5: Test Claude CLI**

### **Test in Terminal First**

```powershell
# Test interactive mode
claude

# You should see Claude interface
# Type something and Claude should respond
# Press Ctrl+C to exit

# Test programmatic mode (headless)
claude -p "Say hello"

# Should print response without opening interactive mode
```

### **Test with File**

```powershell
# Create test file
echo "Hello Claude" > test.txt

# Ask Claude to read it
claude -p "Read test.txt and summarize it"
```

If this works, Claude CLI is ready! ✅

---

## 🔧 **Step 6: Understanding Claude CLI Modes**

### **Interactive Mode** (Default)
```powershell
claude
# Opens interactive chat interface
```

### **Programmatic Mode** (For Backend Integration)
```powershell
claude -p "your prompt here"
# Prints response and exits
# Perfect for backend automation
```

### **Bare Mode** (Headless/No Interactive Features)
```powershell
claude -p --bare "your prompt"
# Skips OAuth, uses ANTHROPIC_API_KEY or token
# Fastest for automation
```

---

## 📊 **How It Works with Your Backend**

```
Your FastAPI Backend
    ↓
AI Service (Claude CLI mode)
    ↓
Runs: subprocess.run(['claude', '-p', '--bare', 'prompt'])
    ↓
Claude CLI processes request
    ↓
Returns response as text
    ↓
Backend parses and returns to user
```

---

## 💰 **Claude CLI Subscription Requirements**

### **What You Need:**

Claude CLI requires ONE of:
- ✅ **Claude Pro subscription** ($20/month)
- ✅ **Claude Team subscription**  
- ✅ **Claude Enterprise subscription**

### **Free Tier:**

Claude CLI has a **free tier with limits**:
- Limited requests per day
- Good for testing
- May hit rate limits faster

**For production**, you'll eventually need the Anthropic API (which we already set up for later).

---

## ⚠️ **Important Limitations for Production**

### **Claude CLI is ONLY for Local Testing:**

| Feature | Claude CLI | Anthropic API |
|---------|-----------|---------------|
| **Local Testing** | ✅ Perfect | ✅ Works |
| **Production Deployment** | ❌ Not recommended | ✅ Perfect |
| **Scalability** | ❌ Limited | ✅ Unlimited |
| **Azure/AWS Deployment** | ❌ Difficult | ✅ Easy |
| **Concurrent Users** | ❌ Single process | ✅ Many users |
| **Cost** | Subscription-based | Pay-per-use |

**Our Strategy:**
1. **NOW:** Use Claude CLI for local testing ✅
2. **LATER:** Switch to Anthropic API for production ✅

The code is already set up to switch providers easily!

---

## 🧪 **Testing Checklist**

### **Before Starting Backend:**

- [ ] Claude CLI installed (`claude --version` works)
- [ ] Authenticated (`claude auth login` completed)
- [ ] Token generated (if using `setup-token`)
- [ ] `.env` updated with configuration
- [ ] Test command works: `claude -p "hello"`

### **After Starting Backend:**

- [ ] Server starts: `uvicorn app.main:app --reload`
- [ ] AI status shows available: `GET /api/v1/ai/status`
- [ ] Can parse resume (test endpoint)
- [ ] No errors in logs

---

## 📝 **Next Steps**

After testing locally with Claude CLI:

1. **Test all AI features** with CLI
2. **Verify everything works**
3. **When ready for production:**
   - Get Anthropic API key
   - Change `AI_PROVIDER=anthropic` in `.env`
   - Deploy to Azure/AWS
   - **No code changes needed!**

---

## 🎯 **Quick Commands Reference**

```powershell
# Install
irm https://claude.ai/install.ps1 | iex

# Login
claude auth login

# Generate token
claude setup-token

# Test
claude -p "Say hello"

# Check version
claude --version

# Logout
claude auth logout
```

---

**✅ You're set up for local testing with Claude CLI!**

**Later, when you have Anthropic API access, just update `.env` and everything switches automatically! 🎉**
