# 🧪 Automated Test Scripts

## 📋 Overview

**Location:** `apps/api/tests/`

This folder contains automated Python test scripts for testing various features of the Maverick Ascend platform.

### **Available Test Scripts:**

1. **`test_complete_flow.py`** - Complete end-to-end workflow test
   - User authentication (HR, Trainer, Maverick)
   - Maverick approval and batch assignment
   - Training and assessment scheduling
   - Attendance marking
   - Assessment marks submission
   - Trainer feedback
   - Analytics validation

2. **`test_top_performers.py`** - Focused test for top performers endpoint
   - Tests `/batches/top-performers` API
   - Detailed debugging output
   - Validates batch performance metrics

---

## 🚀 Quick Start

### **1. Prerequisites**

```bash
# Make sure backend is running
cd C:\rahul\GenAi\GEN-AI-project\apps\api
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

### **2. Run Complete Flow Test**

```bash
# From apps/api directory
python tests\test_complete_flow.py
```

### **3. Run Top Performers Test**

```bash
# From apps/api directory
python tests\test_top_performers.py
```

### **4. View Results**

The scripts will:
- ✅ Print colored output showing each test step
- ✅ Display real-time progress
- ✅ Save results to `test_results_YYYYMMDD_HHMMSS.json` (complete flow only)
- ✅ Show final summary with pass/fail counts
- ✅ Show detailed error messages for debugging

---

## 📊 What It Tests

### **Phase 1: Setup & Login** ⏱️ ~5 seconds
```
✅ Login as HR
✅ Login as Trainer  
✅ Login as Maverick
```

### **Phase 2: Find Batch & Pipeline** ⏱️ ~5 seconds
```
✅ Find Q3 React Developer Batch
✅ Get React Developer Pipeline
✅ Identify training and assessment jobs
```

### **Phase 3: Approve Maverick** ⏱️ ~5 seconds
```
✅ Find pending maverick profile
✅ Approve maverick
✅ Assign to Q3 React batch
```

### **Phase 4: Schedule Training** ⏱️ ~5 seconds
```
✅ Schedule React Fundamentals training
✅ Set meeting link
✅ Enable attendance tracking
```

### **Phase 5: Schedule Assessment** ⏱️ ~5 seconds
```
✅ Schedule React assessment
✅ Set Google Form link
✅ Configure marks (100 max, 50 passing)
```

### **Phase 6: Mark Attendance** ⏱️ ~3 seconds
```
✅ Mark attendance for training
✅ Record 3 present, 1 absent
```

### **Phase 7: Submit Marks** ⏱️ ~5 seconds
```
✅ Submit assessment scores
✅ Calculate pass/fail (3 pass, 1 fail)
```

### **Phase 8: Trainer Feedback** ⏱️ ~3 seconds
```
✅ Submit 5-star feedback
✅ Add positive comments
```

### **Phase 9: Validate Analytics** ⏱️ ~10 seconds
```
✅ Check dashboard stats
✅ Verify analytics overview
✅ Validate top performers
```

**Total Duration:** ~45-60 seconds

---

## 🎨 Sample Output

```
================================================================================
            MAVERICK ASCEND - COMPLETE END-TO-END TEST SUITE
================================================================================

ℹ️  Backend URL: http://localhost:8000/api/v1
ℹ️  Test Start Time: 2024-06-01 10:30:00

================================================================================
                         PHASE 1: SETUP & LOGIN
================================================================================

1.1: Login as HR
✅ Logged in as hr@maverick.com
✅ HR Login

1.2: Login as Trainer
✅ Logged in as trainer@maverick.com
✅ Trainer Login

1.3: Login as Maverick
✅ Logged in as maverick1@example.com
✅ Maverick Login

================================================================================
                    PHASE 2: FIND BATCH & PIPELINE
================================================================================

2.1: Find Q3 React Developer Batch
Batch ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
Batch Name: Q3 React Developer Batch
Pipeline ID: b2c3d4e5-f6g7-8901-bcde-f12345678901
✅ Find Q3 React Batch

2.2: Get Pipeline Jobs
Total Jobs: 4
ℹ️  - React Fundamentals (TRAINING)
ℹ️  - React Assessment (ASSESSMENT)
ℹ️  - Advanced React (TRAINING)
ℹ️  - Final Project (DEPLOYMENT)
✅ Get Pipeline Jobs

... (continues for all phases)

================================================================================
                            TEST SUMMARY
================================================================================

Total Tests: 15
✅ Passed: 15
❌ Failed: 0
Pass Rate: 100.0%
Duration: 47.32 seconds

Detailed Results:

 1. ✅ PASS - HR Login
 2. ✅ PASS - Trainer Login
 3. ✅ PASS - Maverick Login
 4. ✅ PASS - Find Q3 React Batch
     Batch ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
 5. ✅ PASS - Get Pipeline Jobs
     Found 4 jobs
 6. ✅ PASS - Find Pending Maverick
 7. ✅ PASS - Approve & Assign Maverick
 8. ✅ PASS - Schedule Training
 9. ✅ PASS - Schedule Assessment
10. ✅ PASS - Mark Attendance
     Simulated - 3/4 present
11. ✅ PASS - Submit Assessment Marks
     4 submissions: 3 passed, 1 failed
12. ✅ PASS - Submit Trainer Feedback
     5-star rating submitted
13. ✅ PASS - Get Dashboard Stats
14. ✅ PASS - Get Analytics Overview
15. ✅ PASS - Get Top Performers
     10 batches

================================================================================
                        ALL TESTS PASSED! 🎉
================================================================================

ℹ️  Results saved to: test_results_20240601_103047.json
```

---

## 📁 Output Files

### **test_results_YYYYMMDD_HHMMSS.json**

Example:
```json
{
  "timestamp": "2024-06-01T10:30:47.123456",
  "total_tests": 15,
  "passed": 15,
  "failed": 0,
  "pass_rate": 100.0,
  "tests": [
    {
      "test": "HR Login",
      "passed": true,
      "details": "",
      "timestamp": "2024-06-01T10:30:02.456789"
    },
    ...
  ],
  "batch_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "pipeline_id": "b2c3d4e5-f6g7-8901-bcde-f12345678901",
  "maverick_id": "c3d4e5f6-g7h8-9012-cdef-g23456789012"
}
```

---

## 🔧 Customization

### **Change Test Credentials**

Edit these lines in `test_complete_flow.py`:
```python
HR_EMAIL = "hr@maverick.com"
HR_PASSWORD = "hr123"
TRAINER_EMAIL = "trainer@maverick.com"
TRAINER_PASSWORD = "trainer123"
MAVERICK_EMAIL = "maverick1@example.com"
MAVERICK_PASSWORD = "maverick123"
```

### **Change Backend URL**

```python
BASE_URL = "http://localhost:8000/api/v1"
```

### **Add More Test Cases**

Add new methods following the pattern:
```python
def phase_X_test_something(self):
    """Phase X: Description"""
    print_header("PHASE X: TEST SOMETHING")
    
    print_step("X.1: First Step")
    # Your test code here
    
    self.record_test("Test Name", success_boolean, "optional details")
    return True
```

---

## 🐛 Troubleshooting

### **Issue: "Cannot connect to backend"**

**Solution:**
```bash
# Start backend first
cd apps/api
uvicorn app.main:app --reload
```

### **Issue: "Batch not found"**

**Solution:**
- Make sure Q3 React Developer batch exists
- Or update the search term in Phase 2

### **Issue: "Login failed"**

**Solution:**
- Verify credentials are correct
- Check if users exist in database
- Run seed script if needed

### **Issue: "Some tests failed"**

**Solution:**
- Check the detailed error messages
- Review the JSON output file
- Check backend logs for API errors

---

## 📊 Integration with CI/CD

### **GitHub Actions Example**

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install requests
      - name: Start backend
        run: |
          cd apps/api
          uvicorn app.main:app &
          sleep 10
      - name: Run tests
        run: |
          cd apps/api
          python test_complete_flow.py
```

---

## 📝 Notes

- **⚠️ Test Data:** This script creates real data in your database
- **🔄 Idempotent:** Can be run multiple times (will create new records each time)
- **⏱️ Duration:** Approximately 45-60 seconds
- **📊 Output:** Colored terminal output + JSON file
- **✅ Exit Code:** 0 if all pass, 1 if any fail

---

## 🎯 Next Steps

After running the test:

1. **Review JSON output** for detailed results
2. **Check frontend** to verify UI updates
3. **Validate analytics** page shows correct data
4. **Check database** for created records

---

## 🚀 Ready to Run!

```bash
cd apps/api
python test_complete_flow.py
```

**Happy Testing!** 🧪✨
