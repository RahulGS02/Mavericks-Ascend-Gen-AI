# 🔧 Setup and Troubleshooting Guide

## ❌ Common Errors and Solutions

### **Error 1: "No module named 'sqlalchemy'"**

**Cause:** Dependencies not installed in the virtual environment

**Solution:**
```powershell
cd C:\rahul\GenAi\GEN-AI-project\apps\api

# Option 1: Install all dependencies
pip install -r requirements.txt

# Option 2: Install specific missing packages
pip install sqlalchemy psycopg2-binary pandas openpyxl
```

---

### **Error 2: "4 validation errors for Settings - DATABASE_URL field required"**

**Cause:** `.env` file not loaded or missing required variables

**Solution:**

1. **Check if `.env` file exists:**
   ```powershell
   dir .env
   ```

2. **Ensure `.env` has required variables:**
   ```env
   # Database
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   
   # Supabase
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_KEY=your-service-key
   
   # JWT
   JWT_SECRET=your-secret-key
   
   # AI
   AI_ENABLED=true
   AI_PROVIDER=auggie
   AI_API_KEY=your-auggie-api-key
   ```

3. **For testing without database, use standalone test:**
   ```powershell
   python test_nl_query_standalone.py
   ```

---

## ✅ Step-by-Step Setup

### **Step 1: Verify Virtual Environment**

```powershell
cd C:\rahul\GenAi\GEN-AI-project\apps\api

# Check if venv is activated (you should see (venv) in prompt)
# If not, activate it:
.\venv\Scripts\Activate.ps1

# Or on Command Prompt:
venv\Scripts\activate.bat
```

---

### **Step 2: Install Dependencies**

```powershell
# Check what's installed
pip list

# Install all requirements
pip install -r requirements.txt

# Verify installation
python check_dependencies.py
```

---

### **Step 3: Verify Environment Variables**

```powershell
# Check if .env exists
type .env

# If missing, copy from example
copy .env.example .env

# Edit .env with your values
notepad .env
```

---

### **Step 4: Run Tests (in order)**

```powershell
# Test 1: Check dependencies
python check_dependencies.py

# Test 2: Standalone test (no DB required)
python test_nl_query_standalone.py

# Test 3: Full import test (requires .env)
python test_imports.py

# Test 4: API test with sample queries (requires AI)
python test_nl_query_api.py
```

---

## 🧪 **Testing Without Database**

If you don't have the database set up yet, you can still test the core components:

```powershell
# This test works WITHOUT database connection
python test_nl_query_standalone.py
```

**What it tests:**
- ✅ Schema Provider (no DB needed)
- ✅ SQL Validator (no DB needed)
- ✅ Excel Generator (no DB needed)
- ✅ File structure verification

---

## 🚀 **Running the API Server**

Once dependencies are installed and `.env` is configured:

```powershell
# Start the server
uvicorn app.main:app --reload

# Server will start at:
# http://localhost:8000

# API Documentation:
# http://localhost:8000/docs
```

---

## 📊 **Testing the API Endpoints**

### **Method 1: Using Swagger UI**

1. Open: `http://localhost:8000/docs`
2. Find: `POST /api/v1/nl-query/search`
3. Click "Try it out"
4. Login as SuperAdmin
5. Enter request body:
   ```json
   {
     "query": "Show me available mavericks",
     "include_stats": true,
     "max_rows": 100
   }
   ```
6. Click "Execute"

### **Method 2: Using curl**

```powershell
# First, login to get token
curl -X POST "http://localhost:8000/api/v1/auth/login" `
  -H "Content-Type: application/json" `
  -d '{"email":"admin@example.com","password":"password"}'

# Then use the token
curl -X POST "http://localhost:8000/api/v1/nl-query/search" `
  -H "Authorization: Bearer YOUR_TOKEN_HERE" `
  -H "Content-Type: application/json" `
  -d '{"query":"Show me available mavericks","include_stats":true}'
```

---

## 🐛 **Troubleshooting Tips**

### **Issue: Import errors in test scripts**

**Cause:** Python can't find the `app` module

**Solution:**
```powershell
# Make sure you're in the correct directory
cd C:\rahul\GenAi\GEN-AI-project\apps\api

# Set PYTHONPATH (if needed)
$env:PYTHONPATH = "."
```

---

### **Issue: AI service not working**

**Check:**
```powershell
# Verify AI configuration
python -c "from app.config import settings; print(f'AI Enabled: {settings.AI_ENABLED}'); print(f'AI Provider: {settings.AI_PROVIDER}')"
```

**Ensure `.env` has:**
```env
AI_ENABLED=true
AI_PROVIDER=auggie
AI_API_KEY=94fca94090d4fee5dc35227e2d5e5b21527b668dc0e8acafd567117aa3839968
AUGGIE_TENANT_URL=https://e7.api.augmentcode.com/
```

---

### **Issue: Excel generation fails**

**Solution:**
```powershell
pip install pandas openpyxl --upgrade
```

---

## ✅ **Quick Validation Checklist**

Run these commands to verify everything is set up:

```powershell
cd C:\rahul\GenAi\GEN-AI-project\apps\api

# 1. Check dependencies
python check_dependencies.py

# 2. Test core components
python test_nl_query_standalone.py

# 3. If all good, start server
uvicorn app.main:app --reload
```

---

## 📝 **Summary of Test Scripts**

| Script | Purpose | Requires DB | Requires AI |
|--------|---------|-------------|-------------|
| `check_dependencies.py` | Check if packages installed | ❌ | ❌ |
| `test_nl_query_standalone.py` | Test core components | ❌ | ❌ |
| `test_imports.py` | Test all imports | ⚠️ | ⚠️ |
| `test_nl_query_api.py` | Full AI pipeline test | ❌ | ✅ |

**Legend:**
- ❌ = Not required
- ⚠️ = Needs .env but not active connection
- ✅ = Required

---

## 🎯 **Recommended Testing Order**

1. ✅ `check_dependencies.py` - Verify packages
2. ✅ `test_nl_query_standalone.py` - Test core logic
3. ⚠️  Configure `.env` file properly
4. ✅ `test_nl_query_api.py` - Test with AI
5. ✅ Start server and test via API docs

---

## 💡 **Need Help?**

**Error in script.log shows:**
- SQLAlchemy not found → Run: `pip install -r requirements.txt`
- Pydantic validation errors → Check `.env` file has all required fields

**All components are ready to use once dependencies are installed!** 🚀
