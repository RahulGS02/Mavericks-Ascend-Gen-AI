# 🧪 Test Scripts

## Overview

This folder contains automated Python test scripts for the Maverick Ascend platform.

---

## 📁 Test Scripts

### **1. test_complete_flow.py**

**Purpose:** Complete end-to-end workflow test

**What it tests:**
- ✅ User authentication (HR, Trainer, Maverick)
- ✅ Batch and pipeline discovery
- ✅ Maverick approval and assignment
- ✅ Training scheduling
- ✅ Assessment scheduling
- ✅ Attendance marking
- ✅ Assessment marks submission
- ✅ Trainer feedback
- ✅ Analytics validation

**Duration:** ~60 seconds

**Usage:**
```bash
cd apps/api
python tests\test_complete_flow.py
```

---

### **2. test_top_performers.py**

**Purpose:** Focused test for top performers endpoint

**What it tests:**
- ✅ `/batches/top-performers` API endpoint
- ✅ Batch performance metrics
- ✅ Top performer calculation
- ✅ Response structure validation

**Duration:** ~5 seconds

**Usage:**
```bash
cd apps/api
python tests\test_top_performers.py
```

**Use this when:**
- Debugging top performers feature
- Validating performance calculations
- Checking batch assessment data

---

## 🚀 Running Tests

### Prerequisites

```bash
# Start backend
cd apps/api
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

### Run All Tests

```bash
# Run complete flow
python tests\test_complete_flow.py

# Run top performers test
python tests\test_top_performers.py
```

---

## 📊 Output

### Terminal Output
- ✅ Color-coded results (green = pass, red = fail)
- ✅ Detailed progress for each step
- ✅ Error messages with debugging info
- ✅ Final summary with pass/fail counts

### JSON Output (complete flow only)
- File: `test_results_YYYYMMDD_HHMMSS.json`
- Contains: detailed results, timestamps, IDs used

---

## 🔧 Customization

### Change Test Credentials

Edit the configuration section at the top of each file:

```python
HR_EMAIL = "hr@maverick.com"
HR_PASSWORD = "hr123"
```

### Change Backend URL

```python
BASE_URL = "http://localhost:8000/api/v1"
```

---

## 📖 Documentation

For more details, see:
- **apps/api/TEST_SCRIPT_README.md** - Detailed script documentation
- **AUTOMATED_TEST_SUMMARY.md** - Quick reference guide
- **END_TO_END_TESTING_GUIDE.md** - Manual testing guide

---

## 🐛 Troubleshooting

### Backend not accessible
```bash
# Make sure backend is running
cd apps/api
uvicorn app.main:app --reload
```

### Import errors
```bash
# Install requests library
pip install requests
```

### Test failures
- Check error messages in terminal output
- Review JSON output file (complete flow only)
- Check backend logs for API errors
- Verify database has required test data

---

## ✅ Best Practices

1. **Run tests in order:**
   - First: `test_complete_flow.py` (creates test data)
   - Then: `test_top_performers.py` (validates specific feature)

2. **Review output:**
   - Check terminal for colored results
   - Read error messages carefully
   - Review JSON file for detailed analysis

3. **Clean test data:**
   - Tests create real database records
   - Consider cleaning test data periodically
   - Or use a separate test database

---

## 🎯 Adding New Tests

To add a new focused test script:

1. Create new file: `test_<feature_name>.py`
2. Follow the pattern from existing scripts
3. Include colored output and error handling
4. Update this README

Example template:
```python
"""
Test <Feature Name>

Description of what this test does
"""

import requests
from typing import Optional

BASE_URL = "http://localhost:8000/api/v1"

# Add your test functions here

if __name__ == "__main__":
    main()
```

---

**Happy Testing!** 🧪✨
