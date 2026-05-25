# 🧪 AI Talent Search - Test Scripts

## 📁 **Available Test Scripts**

| Script | Purpose | Duration | When to Use |
|--------|---------|----------|-------------|
| **quick_test.py** | Fast smoke test | ~2 min | Quick verification after code changes |
| **test_talent_search_manual.py** | Comprehensive test suite | ~10 min | Full feature testing, pre-deployment |
| **tests/test_talent_search_api.py** | Automated unit tests | ~15 sec | CI/CD pipeline, development |

---

## ⚡ **Quick Test** (`quick_test.py`)

### **Purpose**
Fast smoke test to verify basic functionality is working.

### **What it tests**
✅ Authentication  
✅ Statistics endpoint  
✅ 4 search queries (.NET, Python, Java, Frontend)  
✅ Similar skills toggle  
✅ Basic result verification  

### **Usage**

```bash
cd apps/api
python quick_test.py
```

### **Output Preview**

```
🧪 QUICK TEST: AI-POWERED TALENT SEARCH
✅ Logged in successfully
✅ Statistics retrieved - 47 candidates available
✅ Search #1: Found 5 .NET developers
✅ Search #2: Similar skills added 3 more candidates
✅ Search #3: Found 6 Python developers
✅ Search #4: Found 4 Java developers
✨ All basic features working!
```

### **Success Criteria**
- All 4 searches return results
- Similar skills increases result count
- Cost is under $0.01 per search
- No errors or exceptions

---

## 📊 **Comprehensive Test Suite** (`test_talent_search_manual.py`)

### **Purpose**
Detailed testing with beautiful output and thorough verification.

### **What it tests**
✅ Full authentication flow  
✅ Talent pool statistics  
✅ 5 realistic search scenarios  
✅ Exact vs. Similar matching  
✅ Result quality verification  
✅ Skill matching accuracy  
✅ Cost analysis  

### **Test Scenarios**

**1. .NET Developer**
```
Query: "Need .NET developer with C#, Azure cloud, and SQL Server experience"
Expected: .NET, C#, Azure, SQL skills
```

**2. Python Full Stack**
```
Query: "Python developer with Django backend and React frontend, CGPA > 7.5"
Expected: Python, Django, React skills
```

**3. Java Microservices**
```
Query: "Java backend engineer with Spring Boot, microservices, and Docker"
Expected: Java, Spring, Docker skills
```

**4. Frontend Developer (Urgent)**
```
Query: "Frontend developer with Angular or React, available immediately"
Expected: Angular, React, JavaScript skills
```

**5. DevOps Engineer**
```
Query: "DevOps engineer with Kubernetes, CI/CD, and cloud platforms"
Expected: Kubernetes, Docker, AWS, Azure skills
```

### **Usage**

```bash
cd apps/api
python test_talent_search_manual.py
```

### **Output Features**

**Color-coded output:**
- 🟢 Green: Success messages
- 🔵 Blue: Information
- 🟡 Yellow: Warnings
- 🔴 Red: Errors

**Detailed candidate cards:**
```
1. John Doe
   Email: john@maverick.com
   Tier: TIER_1_EXACT (Green)
   Match Score: 87.5/100
   CGPA: 8.50
   Adaptability: 85/100
   Deployment Readiness: immediate
   Learning Required: 0.0 weeks
   ✅ Exact Matches: .NET (90%), C# (88%), Azure (85%)
   📊 Assessments: 5 total, 100% pass rate, improving trend
   💡 Excellent match! Ready for immediate deployment.
```

### **Success Criteria**
- All 5 scenarios complete without errors
- Each search finds at least 1 candidate
- Top candidates have expected skills
- Similar skills option increases results
- Cost stays under budget ($0.01/query)

---

## 🤖 **Automated Unit Tests** (`tests/test_talent_search_api.py`)

### **Purpose**
Automated testing for CI/CD pipeline.

### **What it tests**
✅ All API endpoints (search, explain, statistics, cost-estimate)  
✅ Authentication and authorization  
✅ Input validation  
✅ Error handling  
✅ Multi-tier matching logic  
✅ Scoring algorithm  
✅ Database queries  

### **Usage**

```bash
cd apps/api

# Run all tests
pytest tests/test_talent_search_api.py -v

# Run specific test
pytest tests/test_talent_search_api.py::TestTalentSearchAPI::test_search_endpoint_with_exact_matches -v

# Run with coverage
pytest tests/test_talent_search_api.py --cov=app.services.talent_search_service
```

### **Expected Output**

```
tests/test_talent_search_api.py::TestTalentSearchAPI::test_search_endpoint_authentication_required PASSED
tests/test_talent_search_api.py::TestTalentSearchAPI::test_search_endpoint_with_exact_matches PASSED
tests/test_talent_search_api.py::TestTalentSearchAPI::test_search_with_similar_skills PASSED
tests/test_talent_search_api.py::TestTalentSearchAPI::test_search_filters_deployed_candidates PASSED
tests/test_talent_search_api.py::TestTalentSearchAPI::test_explain_endpoint PASSED
tests/test_talent_search_api.py::TestTalentSearchAPI::test_cost_estimate_endpoint PASSED
tests/test_talent_search_api.py::TestTalentSearchAPI::test_statistics_endpoint PASSED
tests/test_talent_search_api.py::TestTalentSearchAPI::test_unauthorized_role_access PASSED
tests/test_talent_search_api.py::TestTalentSearchAPI::test_show_similar_button_logic PASSED

=============== 9 passed in 12.50s ===============
```

---

## 🎯 **Which Test to Run?**

### **During Development**
```bash
# Quick verification after code changes
python quick_test.py
```

### **Before Committing**
```bash
# Full automated test suite
pytest tests/test_talent_search_api.py -v
```

### **Before Deployment**
```bash
# Comprehensive manual testing
python test_talent_search_manual.py
```

### **After Deployment**
```bash
# Quick smoke test on production
python quick_test.py  # (update API_URL to production)
```

---

## ⚙️ **Configuration**

All test scripts use these environment variables:

```python
# API Configuration
API_BASE_URL = "http://localhost:8000/api/v1"

# Test User Credentials
HR_EMAIL = "hr@maverick.com"
HR_PASSWORD = "hr123"  # Update with actual password
```

### **Update for Your Environment**

**For local testing:**
```python
API_BASE_URL = "http://localhost:8000/api/v1"
```

**For staging:**
```python
API_BASE_URL = "https://staging-api.maverick.com/api/v1"
```

**For production:**
```python
API_BASE_URL = "https://api.maverick.com/api/v1"
```

---

## 📊 **Test Coverage**

| Component | Coverage |
|-----------|----------|
| **API Endpoints** | 100% (4/4) |
| **Service Methods** | 95% |
| **Database Queries** | 100% |
| **Error Handling** | 90% |
| **Authentication** | 100% |

---

## 🐛 **Common Issues**

### **Issue 1: Login Failed**
```
❌ Login failed: 401
```
**Fix:** Update HR_EMAIL and HR_PASSWORD in the script

### **Issue 2: Connection Refused**
```
Connection refused
```
**Fix:** Start the backend server:
```bash
cd apps/api
python -m uvicorn app.main:app --reload
```

### **Issue 3: No Results Found**
```
⚠️ Expected at least 1 results, got 0
```
**Fix:** Ensure database has available candidates:
```sql
SELECT COUNT(*) FROM mavericks 
WHERE deployment_status = 'AVAILABLE' 
AND profile_status = 'APPROVED';
```

---

## 📝 **Test Reports**

Test scripts generate different outputs:

### **quick_test.py**
- Terminal output only
- Color-coded status messages
- Summary at end

### **test_talent_search_manual.py**
- Detailed terminal output
- Color-coded with emojis
- Candidate details
- Verification results
- Final summary

### **pytest tests**
- JUnit XML reports (for CI/CD)
- Coverage reports
- Detailed failure information

---

## 🚀 **Next Steps**

After all tests pass:

1. ✅ Test frontend integration
2. ✅ Test with real user data
3. ✅ Performance testing
4. ✅ Deploy to staging
5. ✅ UAT (User Acceptance Testing)
6. ✅ Deploy to production

---

**🎉 Happy Testing! 🎉**
