# 🧪 AI Talent Search - Testing Guide

## 📋 **Overview**

This guide provides instructions for testing the AI-Powered Talent Search feature.

**Two test scripts are provided:**
1. **`quick_test.py`** - Fast smoke test (5 minutes)
2. **`test_talent_search_manual.py`** - Comprehensive test suite (10-15 minutes)

---

## 🚀 **Quick Start**

### **Prerequisites**

1. ✅ Backend API server running
2. ✅ Database populated with mavericks and skills
3. ✅ HR user account created
4. ✅ Python requests library installed

```bash
# Install required packages
pip install requests
```

---

## ⚡ **Option 1: Quick Test (5 minutes)**

### **What it tests:**
- Authentication
- Statistics endpoint
- 4 different search queries
- Similar skills toggle
- Result verification

### **Run the test:**

```bash
cd apps/api
python quick_test.py
```

### **Expected Output:**

```
================================================================================
🧪 QUICK TEST: AI-POWERED TALENT SEARCH
================================================================================

1️⃣ Logging in...
✅ Logged in successfully as hr@maverick.com

2️⃣ Getting talent pool statistics...
✅ Statistics retrieved
   📊 Available Candidates: 47
   📊 Average CGPA: 7.8
   📊 Top Skills: 15

3️⃣ TEST SEARCH #1: .NET Developer with C#, Azure, SQL
✅ Search completed
   📋 Total Found: 5
   📋 Exact Matches: 3
   💰 Cost: $0.001500

   🏆 Top Candidate:
      Name: John Doe
      Score: 87.5/100
      Tier: TIER_1_EXACT
      CGPA: 8.50
      ✅ Skills: .NET, C#, Azure, SQL Server

4️⃣ TEST SEARCH #2: Same query WITH similar skills
✅ Search completed
   📋 Total Found: 8
   📋 Similar Candidates: 3
   ✨ Including similar skills found 3 more candidates!

5️⃣ TEST SEARCH #3: Python Full Stack Developer
✅ Search completed
   📋 Total Found: 6
   🎯 Parsed Skills: Python, Django, React
   📊 Min CGPA: 7.5

   🏆 Top Candidate:
      Name: Jane Smith
      Score: 82.3/100
      Adaptability: 78/100
      Ready in: 0.0 weeks

6️⃣ TEST SEARCH #4: Java Microservices Developer
✅ Search completed
   📋 Total Found: 4
   ⚡ Immediate Ready: 2
   📚 Short Training: 2

================================================================================
✨ QUICK TEST COMPLETED!
================================================================================

✅ All basic features are working correctly!
💡 For detailed testing, run: python test_talent_search_manual.py
```

---

## 📊 **Option 2: Comprehensive Test Suite (15 minutes)**

### **What it tests:**
- Authentication flow
- Talent pool statistics
- 5 realistic search scenarios
- Exact vs. Similar skill matching
- Result verification
- Detailed output analysis

### **Test Scenarios:**

| # | Scenario | Query | Expected Skills |
|---|----------|-------|-----------------|
| 1 | .NET Developer | "Need .NET developer with C#, Azure cloud, and SQL Server experience" | .NET, C#, Azure, SQL |
| 2 | Python Full Stack | "Python developer with Django backend and React frontend skills, CGPA > 7.5" | Python, Django, React |
| 3 | Java Microservices | "Java backend engineer with Spring Boot, microservices, and Docker experience" | Java, Spring, Docker |
| 4 | Frontend Developer | "Frontend developer with Angular or React, available immediately" | Angular, React, JavaScript |
| 5 | DevOps Engineer | "DevOps engineer with Kubernetes, CI/CD, and cloud platforms" | Kubernetes, Docker, AWS, Azure |

### **Run the test:**

```bash
cd apps/api
python test_talent_search_manual.py
```

### **Expected Output:**

```
================================================================================
       🚀 AI-POWERED TALENT SEARCH - MANUAL TEST SUITE
================================================================================

ℹ️  API Base URL: http://localhost:8000/api/v1
ℹ️  Test User: hr@maverick.com
ℹ️  Timestamp: 2024-01-15 10:30:00

================================================================================
                        🔐 STEP 1: AUTHENTICATION
================================================================================

✅ Successfully logged in as hr@maverick.com
ℹ️  Token received: eyJhbGciOiJIUzI1NiIs...

================================================================================
                    📊 STEP 2: TALENT POOL STATISTICS
================================================================================

✅ Statistics retrieved successfully
ℹ️  Total Available Candidates: 47
ℹ️  Average CGPA: 7.82
ℹ️  Top Skills (15):
   • Python: 23 candidates (avg: 82.5%)
   • React: 18 candidates (avg: 78.3%)
   • JavaScript: 15 candidates (avg: 85.1%)
   • .NET: 12 candidates (avg: 80.2%)
   • Java: 10 candidates (avg: 76.8%)

================================================================================
              🧪 TEST SCENARIO: 1. .NET Developer with C#, Cloud, SQL
================================================================================

ℹ️  Query: Need .NET developer with C#, Azure cloud, and SQL Server experience
ℹ️  Include Similar: False
ℹ️  Urgency: flexible
ℹ️  Max Results: 10
✅ Search completed successfully

────────────────────────────────────────────────────────────────────────────────
📋 SEARCH RESULTS
────────────────────────────────────────────────────────────────────────────────

📊 Summary:
   Total Found: 5
   Exact Matches: 3
   Similar Skill Candidates: 0
   Transferable Skill Candidates: 0
   Immediate Ready: 3
   Short Training: 2
   Longer Training: 0

💰 Cost Analysis:
   Total Tokens: 500
   Total Cost: $0.001500

🎯 Parsed Requirements:
   Required Skills: .NET, C#, Azure, SQL Server
   Min CGPA: None

👥 Top Candidates (5):

1. John Doe
   Email: john@maverick.com
   Tier: TIER_1_EXACT
   Match Score: 87.5/100
   CGPA: 8.50
   Adaptability: 85/100
   Deployment Readiness: immediate
   Learning Required: 0.0 weeks
   ✅ Exact Matches: .NET (90%), C# (88%), Azure (85%), SQL Server (80%)
   📊 Assessments: 5 total, 100% pass rate, trend: improving
   💡 ✅ Excellent match! Has 4 exact skill matches. Strong learning ability. Ready for immediate deployment.

2. Jane Smith
   Email: jane@maverick.com
   Tier: TIER_1_EXACT
   Match Score: 82.3/100
   CGPA: 8.20
   Adaptability: 78/100
   Deployment Readiness: immediate
   Learning Required: 0.0 weeks
   ✅ Exact Matches: .NET (85%), C# (90%), SQL Server (82%)
   🔷 Similar Skills: AWS (75%)
   📚 Needs Training: Azure
   📊 Assessments: 4 total, 100% pass rate, trend: stable
   💡 ✅ Good match! Has 3 exact skill matches. 1 week training for Azure. Strong performer.

...

✅ Found 5 candidates (expected at least 1)
✅ Top candidate has skill: .NET
✅ Top candidate has skill: C#
✅ Top candidate has skill: Azure
✅ Top candidate has skill: SQL

Search 2: Including similar skills
ℹ️  Query: Need .NET developer with C#, Azure cloud, and SQL Server experience
ℹ️  Include Similar: True
...
✅ Search completed successfully
   Total Found: 8
   Similar Skill Candidates: 3
✅ Including similar skills increased results: 5 → 8

────────────────────────────────────────────────────────────────────────────────

... (Additional scenarios follow same pattern) ...

================================================================================
                          📊 FINAL TEST SUMMARY
================================================================================

ℹ️  Total Scenarios: 5
✅ Passed: 5
✅ All scenarios completed!

✨ Test suite completed! ✨
```

---

## 🔧 **Configuration**

### **Update Credentials**

Edit the test scripts with your credentials:

**`quick_test.py`:**
```python
EMAIL = "hr@maverick.com"
PASSWORD = "your_password_here"
```

**`test_talent_search_manual.py`:**
```python
HR_EMAIL = "hr@maverick.com"
HR_PASSWORD = "your_password_here"
```

### **Update API URL (if needed)**

```python
API_BASE_URL = "http://localhost:8000/api/v1"
```

---

## ✅ **What to Verify**

### **1. Authentication**
- ✅ Login succeeds with valid credentials
- ✅ Token is returned
- ✅ Token works for subsequent requests

### **2. Statistics Endpoint**
- ✅ Returns total available candidates
- ✅ Shows average CGPA
- ✅ Lists top skills with counts

### **3. Search Functionality**
- ✅ Natural language query is parsed correctly
- ✅ Required skills are extracted
- ✅ CGPA filters are applied
- ✅ Results are returned

### **4. Result Quality**
- ✅ Candidates have matching skills
- ✅ Match scores are reasonable (0-100)
- ✅ Tier classification is correct
- ✅ Exact matches ranked higher than similar

### **5. Similar Skills Toggle**
- ✅ Disabled: Only exact matches returned
- ✅ Enabled: Similar skill candidates included
- ✅ Total results increase when enabled

### **6. Result Details**
- ✅ Each candidate has:
  - Name, email
  - Match score
  - Tier (TIER_1, TIER_2, TIER_3)
  - CGPA
  - Adaptability score
  - Deployment readiness
  - Learning weeks required
  - Skill breakdowns (exact/similar/transferable/missing)
  - Assessment performance
  - Match reasoning

### **7. Cost Analysis**
- ✅ Token count is reported
- ✅ Cost is calculated
- ✅ Cost is under $0.01 per query

---

## 🐛 **Troubleshooting**

### **Problem: Login fails**

```
❌ Login failed: 401
```

**Solution:**
1. Check credentials are correct
2. Verify HR user exists in database
3. Check password is correct

```bash
# Create HR user if needed
python manage.py create_hr_user
```

---

### **Problem: No candidates found**

```
⚠️ Expected at least 1 results, got 0
```

**Solution:**
1. Check database has mavericks with AVAILABLE status
2. Verify mavericks have skills in maverick_skills table
3. Check deployment_status = 'AVAILABLE' and profile_status = 'APPROVED'

```sql
-- Check available candidates
SELECT COUNT(*) FROM mavericks
WHERE deployment_status = 'AVAILABLE'
AND profile_status = 'APPROVED';

-- Check skills
SELECT skill_name, COUNT(*)
FROM maverick_skills
GROUP BY skill_name
ORDER BY COUNT(*) DESC;
```

---

### **Problem: Connection refused**

```
Connection refused
```

**Solution:**
1. Verify backend server is running
2. Check port 8000 is correct
3. Ensure no firewall blocking

```bash
# Start backend server
cd apps/api
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

### **Problem: AI parsing fails**

```
❌ Search failed: 500
Error: AI query parsing failed
```

**Solution:**
1. Check Auggie SDK configuration
2. Verify API keys are set
3. Check internet connection

```bash
# Check environment variables
echo $AUGGIE_API_KEY
```

---

## 📊 **Sample Test Data**

### **Create Test Mavericks (if needed)**

Run the database seed script:

```bash
cd apps/api
python seed_test_data.py
```

This creates:
- 10+ test mavericks
- Various skill combinations (.NET, Python, Java, React, etc.)
- Different CGPA levels
- Assessment history
- Deployment statuses

---

## 🎯 **Success Criteria**

### **✅ All tests should:**

1. **Authentication**: Login succeeds
2. **Statistics**: Show realistic numbers (>0 candidates)
3. **Search #1** (.NET): Find 1+ candidates with .NET skills
4. **Search #2** (Similar): Find more results than Search #1
5. **Search #3** (Python): Find 1+ Python developers
6. **Search #4** (Java): Find 1+ Java developers
7. **Search #5** (DevOps): Find 1+ DevOps candidates
8. **Cost**: Every search costs < $0.01
9. **Performance**: Each search completes in < 5 seconds

---

## 🔍 **Manual Verification**

### **Check Individual Results**

Look for these quality indicators:

1. **Tier Accuracy**:
   - TIER_1: Has exact skill matches
   - TIER_2: Has similar skills (e.g., C# for .NET)
   - TIER_3: Has transferable skills (e.g., Java for .NET)

2. **Score Ranges**:
   - TIER_1: 70-100
   - TIER_2: 60-85
   - TIER_3: 50-75

3. **Deployment Readiness**:
   - "immediate": 0 weeks training
   - "short_training": 1-4 weeks
   - "longer_training": 4-8 weeks

4. **Match Reasoning**:
   - Explains why candidate matched
   - Mentions key skills
   - Notes adaptability
   - States readiness

---

## 🚀 **Next Steps**

After successful testing:

1. ✅ **Run Unit Tests**:
   ```bash
   cd apps/api
   pytest tests/test_talent_search_api.py -v
   ```

2. ✅ **Test Frontend Integration**:
   ```bash
   cd apps/web
   npm run dev
   # Visit http://localhost:3000/hr/talent-search
   ```

3. ✅ **Load Testing** (optional):
   ```bash
   python load_test.py  # Run 100 concurrent searches
   ```

4. ✅ **Deploy to Staging**

---

## 📞 **Support**

If tests fail or you encounter issues:

1. Check logs: `apps/api/logs/app.log`
2. Check server.log: `apps/api/server.log`
3. Check script.log: `apps/api/script.log`
4. Review API documentation: `AI_TALENT_SEARCH_API_DOCUMENTATION.md`

---

**🎉 Happy Testing! 🎉**
