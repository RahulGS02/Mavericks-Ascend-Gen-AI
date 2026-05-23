# ⚡ Quick Reference Card - AI Integration

## 🎯 **One-Minute Setup**

```powershell
# 1. Install
pip install -r requirements.txt

# 2. Get API key from https://console.anthropic.com/

# 3. Edit .env
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key

# 4. Test
python test_anthropic_setup.py

# 5. Run
uvicorn app.main:app --reload

# 6. Visit
http://localhost:8000/docs
```

---

## 🔑 **Key Concepts**

| Concept | Explanation |
|---------|-------------|
| **Claude CLI** | Desktop app for coding (NOT for production) |
| **Claude API** | REST API for applications (PERFECT for production) |
| **OAuth** | Browser login (for humans, not servers) |
| **API Key** | Token for automation (for servers) |
| **Anthropic** | Company that makes Claude |
| **Auggie SDK** | Alternative AI provider |

---

## 📁 **Important Files**

```
apps/api/
├── .env                          ← ADD YOUR API KEY HERE
├── app/config.py                 ← Updated for multi-provider
├── app/services/
│   ├── ai_service.py             ← Original (Auggie only)
│   └── ai_service_anthropic.py   ← NEW (Multi-provider)
├── requirements.txt              ← Updated with anthropic
│
├── CLAUDE_CLI_VS_API_EXPLAINED.md    ← Read this! Answers your questions
├── LOCAL_SETUP_COMPLETE_GUIDE.md     ← Complete setup guide
├── ANTHROPIC_CLAUDE_SETUP.md         ← Anthropic details
├── AI_MIGRATION_SUMMARY.md           ← What changed
└── test_anthropic_setup.py           ← Test script
```

---

## 🔄 **Switch Providers**

### **Use Anthropic (Recommended)**
```bash
# .env
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-key
```

### **Use Auggie**
```bash
# .env
AI_PROVIDER=auggie
AI_API_KEY=your-auggie-key
```

---

## 🧪 **Testing Commands**

```powershell
# Test Anthropic setup
python test_anthropic_setup.py

# Start server
uvicorn app.main:app --reload

# Check AI status
curl http://localhost:8000/api/v1/ai/status

# Or visit in browser
http://localhost:8000/api/v1/ai/status
```

---

## 💡 **Environment Variables**

### **Required for Anthropic**
```bash
AI_ENABLED=true
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-actual-key
```

### **Optional Settings**
```bash
ANTHROPIC_MODEL=claude-sonnet-4-20250514
ANTHROPIC_MAX_TOKENS=4000
ANTHROPIC_TEMPERATURE=0.7
AI_DAILY_REQUEST_LIMIT=1000
AI_RATE_LIMIT_PER_MINUTE=60
```

---

## 📊 **API Endpoints**

| Endpoint | Purpose |
|----------|---------|
| `GET /api/v1/ai/status` | Check AI availability |
| `POST /api/v1/resume/parse` | Parse resume with AI |
| `POST /api/v1/skills/extract` | Extract skills |
| `GET /api/v1/admin/analytics/ai` | View usage stats |

---

## 💰 **Costs**

**Anthropic Claude Sonnet 4:**
- Input: $3 per 1M tokens
- Output: $15 per 1M tokens
- ~$0.003 per resume parse

**Very affordable!**

---

## 🐛 **Quick Troubleshooting**

| Problem | Solution |
|---------|----------|
| Module not found | `pip install anthropic` |
| API key not found | Add to `.env` file |
| 401 Unauthorized | Check API key is correct |
| Port in use | Use `--port 8001` |
| Import error | Restart server |

---

## 📚 **Read These Docs**

### **Start Here:**
1. **CLAUDE_CLI_VS_API_EXPLAINED.md** - Understand CLI vs API
2. **LOCAL_SETUP_COMPLETE_GUIDE.md** - Follow step-by-step

### **Reference:**
3. **ANTHROPIC_CLAUDE_SETUP.md** - Detailed Anthropic info
4. **AI_MIGRATION_SUMMARY.md** - What changed

---

## ✅ **Checklist**

Quick checklist for setup:

- [ ] Python 3.11+ installed
- [ ] `pip install -r requirements.txt` done
- [ ] Anthropic account created
- [ ] API key copied
- [ ] Added to `.env` file
- [ ] Test script passed
- [ ] Server starts successfully
- [ ] Can access API docs

---

## 🚀 **Production Deployment**

**Same setup works in production!**

On Azure/AWS, just set environment variables:
```
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-production-key
```

**Deploy and go!**

---

## 🎓 **Key Takeaway**

**For your backend AI features:**
- ✅ Use **Claude API** (Anthropic API)
- ❌ Don't use Claude CLI

**Claude API:**
- Works locally ✅
- Works in production ✅
- Simple API key ✅
- No browser needed ✅
- 24/7 automation ✅

---

## 📞 **Links**

- **Anthropic Console:** https://console.anthropic.com/
- **API Docs:** https://docs.anthropic.com/
- **Pricing:** https://www.anthropic.com/pricing
- **Local API:** http://localhost:8000/docs

---

**🎉 You're ready to go!**
