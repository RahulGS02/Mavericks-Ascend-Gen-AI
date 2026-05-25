# 🧪 End-to-End Test Guide - Natural Language Query Feature

## 📋 **Overview**

The `test_e2e_nl_query.py` script tests the complete Natural Language Query feature flow:

1. ✅ Connects to running API server
2. ✅ Logs in as SuperAdmin
3. ✅ Executes 4 natural language queries
4. ✅ Validates results and statistics
5. ✅ Downloads Excel file
6. ✅ Verifies all steps completed successfully

---

## 🚀 **Quick Start**

### **Step 1: Update SuperAdmin Credentials**

Edit `test_e2e_nl_query.py` and update these lines (around line 18-19):

```python
# SuperAdmin credentials (update these to match your database)
SUPERADMIN_EMAIL = "admin@example.com"  # ← Change this
SUPERADMIN_PASSWORD = "admin123"        # ← Change this
```

**How to find your SuperAdmin:**

```powershell
# Connect to your database
psql -U your_user -d your_database

# Find SuperAdmin
SELECT id, name, email, role FROM users WHERE role = 'super_admin';
```

---

### **Step 2: Start the API Server**

Open a **separate terminal** and start the server:

```powershell
cd C:\rahul\GenAi\GEN-AI-project\apps\api

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start server
uvicorn app.main:app --reload
```

**Wait for:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

**Leave this terminal running!**

---

### **Step 3: Run the Test**

In a **new terminal**, run the E2E test:

```powershell
cd C:\rahul\GenAi\GEN-AI-project\apps\api

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run test
python test_e2e_nl_query.py
```

---

## 📊 **Expected Output**

### **Successful Test Output:**

```
================================================================================
🧪 END-TO-END TEST: Natural Language Query Feature
================================================================================

Base URL: http://localhost:8000
SuperAdmin Email: admin@example.com
Test Queries: 4

================================================================================
STEP 1: Testing Server Connection
================================================================================
✅ Server is running at http://localhost:8000
ℹ️  Response: {'message': 'Maverick Ascend API', 'status': 'healthy'}

================================================================================
STEP 2: Logging in as SuperAdmin
================================================================================
ℹ️  Attempting login to: http://localhost:8000/api/v1/auth/login
ℹ️  Email: admin@example.com
✅ Login successful!
ℹ️  User: Admin User (admin@example.com)
ℹ️  Role: super_admin
ℹ️  Token: eyJhbGciOiJIUzI1NiIs...

================================================================================
STEP 3: Testing Natural Language Query Endpoint
================================================================================

--- Test Query 1/4: Available Mavericks ---
ℹ️  Query: "Show me all mavericks who are available for deployment"
✅ Query executed successfully!
ℹ️  Query ID: 550e8400-e29b-41d4-a716-446655440000
ℹ️  Generated SQL: SELECT * FROM mavericks WHERE deployment_status = 'AVAILABLE' AND profile_status = '...
ℹ️  Explanation: Returns all mavericks with AVAILABLE deployment status
ℹ️  Tables Used: mavericks
ℹ️  Rows Returned: 45
ℹ️  Total Rows: 45
ℹ️  Execution Time: 123.45ms

  Sample Data (first 3 rows):
    Row 1: {"id": "uuid-1", "name": "John Doe", "email": "john@ex.com"}...
    Row 2: {"id": "uuid-2", "name": "Jane Smith", "email": "jane@ex.com"}...
    Row 3: {"id": "uuid-3", "name": "Bob Wilson", "email": "bob@ex.com"}...

--- Test Query 2/4: Active Batches ---
ℹ️  Query: "List all active batches"
✅ Query executed successfully!
...

📊 Query Test Results:
   ✅ Successful: 4
   ❌ Failed: 0

================================================================================
STEP 4: Testing Excel Download
================================================================================
ℹ️  Downloading results for: "Show me all mavericks who are available for deployment"
✅ Excel file downloaded!
ℹ️  Filename: test_download_20260523_103045.xlsx
ℹ️  Size: 15,234 bytes

================================================================================
📊 FINAL TEST SUMMARY
================================================================================

  ✅ PASS               Server Connection
  ✅ PASS               SuperAdmin Login
  ✅ 4/4 PASS           Natural Language Queries
  ✅ PASS               Excel Download

================================================================================
🎉 ALL TESTS PASSED!
✅ Natural Language Query feature is fully functional!

💡 Ready to build UI!
================================================================================
```

---

## 🐛 **Troubleshooting**

### **Error: "Cannot connect to server"**

**Problem:** Server is not running

**Solution:**
```powershell
# Start server in separate terminal
uvicorn app.main:app --reload
```

---

### **Error: "Login failed"**

**Problem:** SuperAdmin credentials incorrect

**Solutions:**

1. **Check credentials in database:**
   ```sql
   SELECT email, role FROM users WHERE role = 'super_admin';
   ```

2. **Create SuperAdmin if missing:**
   ```sql
   INSERT INTO users (id, name, email, password_hash, role)
   VALUES (
     gen_random_uuid(),
     'Super Admin',
     'admin@example.com',
     '$2b$12$hashed_password_here',  -- Use proper hash
     'super_admin'
   );
   ```

3. **Reset password via API:**
   - Use password reset endpoint
   - Or update directly in database (with proper hash)

---

### **Error: "Query execution failed"**

**Possible Causes:**

1. **AI service not configured:**
   - Check `.env` has `AI_ENABLED=true`
   - Check `AI_API_KEY` is set

2. **Database connection issue:**
   - Check `DATABASE_URL` in `.env`
   - Ensure database is running

3. **Timeout:**
   - AI queries can take 10-30 seconds
   - Script has 30 second timeout
   - Check server logs for errors

---

### **Error: "Excel download failed"**

**Possible Causes:**

1. **pandas/openpyxl not installed:**
   ```powershell
   pip install pandas openpyxl
   ```

2. **Query returned no data:**
   - Check if database has data
   - Try simpler query first

---

## 🎯 **What the Test Validates**

### **Backend Functionality:**
- ✅ API server is running
- ✅ Authentication works (SuperAdmin login)
- ✅ Natural language → SQL conversion
- ✅ SQL validation and security
- ✅ Query execution
- ✅ Result formatting
- ✅ Statistics generation
- ✅ Excel file generation

### **Security:**
- ✅ JWT authentication required
- ✅ SuperAdmin role enforcement
- ✅ SQL injection protection
- ✅ Query validation

### **Data Quality:**
- ✅ Results returned in JSON format
- ✅ Statistics calculated correctly
- ✅ Excel files are valid
- ✅ Query execution times tracked

---

## 📝 **Test Queries Included**

The test runs 4 different query types:

| Query | Purpose | Tests |
|-------|---------|-------|
| "Show me all mavericks who are available for deployment" | Simple filtering | WHERE clauses, ENUMs |
| "List all active batches" | Status filtering | ENUM values, aggregation |
| "Show me the top 10 mavericks by CGPA" | Sorting & limiting | ORDER BY, LIMIT |
| "Count how many mavericks are in each deployment status" | Aggregation | GROUP BY, COUNT |

---

## ✏️ **Customizing the Test**

### **Add Your Own Queries:**

Edit `test_e2e_nl_query.py` around line 21:

```python
TEST_QUERIES = [
    {
        "name": "Your Query Name",
        "query": "Your natural language query here",
        "max_rows": 100
    },
    # Add more queries...
]
```

### **Change Server URL:**

If running on different port or host:

```python
BASE_URL = "http://localhost:8000"  # Change this
```

---

## 🎉 **After Tests Pass**

Once all tests pass, you're ready for:

1. ✅ **Frontend Development** - Build the UI
2. ✅ **User Acceptance Testing** - Let SuperAdmins test
3. ✅ **Production Deployment** - Deploy to live environment

---

## 📊 **Success Criteria**

Tests are successful when:

- ✅ Server connection: Status 200
- ✅ Login: Token received
- ✅ All 4 queries: Valid SQL generated
- ✅ All 4 queries: Results returned
- ✅ All 4 queries: Execution < 30 seconds
- ✅ Excel download: File created with size > 0
- ✅ No security warnings
- ✅ No SQL errors

---

## 💡 **Next Steps**

After successful test:

```powershell
# Stop the test server (Ctrl+C in server terminal)

# Review test results
cat test_download_*.xlsx  # Check Excel files

# Ready for UI development!
# See: FRONTEND_DEVELOPMENT_GUIDE.md (to be created)
```

---

**All tests passing = Backend is production-ready! 🚀**
