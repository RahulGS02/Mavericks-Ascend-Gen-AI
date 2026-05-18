# Test Scripts Directory

This directory contains test data generation scripts for **Maverick Ascend**.

---

## 📁 Directory Structure

```
test_scripts/
├── create_test_data.py          # Main test data creation script
├── test_logs/                   # Auto-generated log files
│   ├── test_data_YYYYMMDD_HHMMSS.log  # Timestamped logs
│   └── last_run_data.json       # Tracking file (auto-created)
├── README.md                    # This file
└── RUN_COMMANDS.md              # Quick command reference
```

---

## 🚀 Running the Test Data Script

### Prerequisites
- PostgreSQL database running
- Backend virtual environment activated
- Database migrations applied

### Command

```bash
# From the project root
cd apps/api
python test_scripts/create_test_data.py
```

**OR from the test_scripts directory:**

```bash
cd apps/api/test_scripts
python create_test_data.py
```

---

## 📊 What Gets Created

### Users
- **10 Mavericks** (maverick1@test.com through maverick10@test.com)
- **2 Trainers** (sarah.trainer@maverick.com, david.trainer@maverick.com)
- **HR account** (uses existing hr@maverick.com)

### Batch Setup
- **1 Pipeline**: SQL Advanced Training (5 jobs)
- **1 Active Batch**: SQL Advanced Batch - Q2 2026
- **3 Training Sessions** (2 completed, 1 upcoming)
- **2 Assessments** (SQL Basics & SQL Advanced)

### Progress Data
- Progress records for all mavericks across all jobs
- Assessment attempts with varied scores
- Different edge cases (passed, failed, in-progress, just started)

---

## 🧹 Smart Cleanup (Tracking-Based)

The script uses a **tracking file** to remember what it created and only deletes that data:
- ✅ Tracks all created IDs in `test_logs/last_run_data.json`
- ✅ On next run, deletes ONLY tracked data (from previous script run)
- ✅ **Does NOT delete** any other existing data (production data, manual test data)
- ✅ **Safe to use** in environments with existing data

**First Run:**
- No tracking file exists → Creates fresh data
- Saves all created IDs to tracking file

**Subsequent Runs:**
- Reads tracking file → Deletes only those specific IDs
- Creates fresh data
- Updates tracking file with new IDs

**This ensures you never accidentally delete production or manual test data!**

---

## 📝 Logging

Every run creates a new log file with timestamp:
```
test_logs/test_data_20260506_153045.log
```

**Log contains:**
- Detailed creation steps
- All data created
- Error messages (if any)
- Full credentials list
- Verification steps

**Log files are never deleted** - keep them for debugging!

---

## 🎯 Test Scenarios Included

### 1. Top Performers (Mavericks 1 & 10)
- Basic: 95+/100
- Advanced: 90+/100
- Progress: 90-100%
- Status: **DEPLOYED**

### 2. Good Students (Mavericks 2-5)
- Basic: 60-90/100 (PASS)
- Advanced: 70-88/100 (PASS)
- Progress: Varying levels

### 3. Failed Students (Mavericks 6-7)
- Maverick 6: Failed advanced (65/100)
- Maverick 7: Failed both
- Status: Not ready for deployment

### 4. In-Progress (Maverick 8)
- Completed basic assessment only
- Not yet taken advanced
- Progress: 50% on advanced training

### 5. Just Started (Maverick 9)
- Completed basic training only
- No assessments taken
- Progress: Early stage

---

## 🔑 Default Credentials

### HR
```
Email:    hr@maverick.com
Password: hr123
```

### Trainers
```
Email:    sarah.trainer@maverick.com
Password: trainer123

Email:    david.trainer@maverick.com
Password: trainer123
```

### Mavericks
```
Email:    maverick1@test.com through maverick10@test.com
Password: mav123 (all same)
```

---

## ✅ Verification Steps

After running the script:

1. **Start Backend**
   ```bash
   cd apps/api
   uvicorn app.main:app --reload
   ```

2. **Start Frontend**
   ```bash
   cd apps/web
   npm run dev
   ```

3. **Login as Maverick**
   - Email: `maverick1@test.com`
   - Password: `mav123`

4. **Test Features**
   - ✅ Dashboard overview
   - ✅ My Progress
   - ✅ **My Batch (Leaderboard)**
   - ✅ My Assessments
   - ✅ Training Schedule
   - ✅ My Profile

5. **Verify Leaderboard**
   - Rankings in correct order
   - Top 3 have special badges
   - Your rank is highlighted
   - No actual scores shown (privacy)

---

## 🐛 Debugging

If the script fails:

1. **Check the log file** in `test_logs/`
2. **Look for error messages** near the end
3. **Common issues:**
   - Database not running
   - Wrong database credentials in `.env`
   - Virtual environment not activated
   - Database migrations not applied

---

## 🔄 Re-running the Script

You can run the script **multiple times safely**:
- Old test data is automatically deleted
- Fresh data is created each time
- Log files are preserved for history

---

## 📋 Expected Output

```
======================================================================
🚀 MAVERICK ASCEND - TEST DATA CREATION
======================================================================

🗑️  Cleaning up existing test data...
✅ Deleted: 10 users, 10 mavericks, 1 batches, 1 pipelines

1️⃣  Getting HR user...
   ✓ HR: hr@maverick.com

2️⃣  Creating 10 Mavericks...
   ✓ Rahul Kumar
   ✓ Priya Sharma
   ...
   ✅ Created 10 mavericks

3️⃣  Creating 2 Trainers...
   ...

[... more steps ...]

======================================================================
✅ TEST DATA CREATION COMPLETE!
======================================================================
```

---

## 🎓 Testing Different User Roles

### As Maverick (Student)
```
Login: maverick1@test.com / mav123
Test: All student features, leaderboard
```

### As Trainer
```
Login: sarah.trainer@maverick.com / trainer123
Test: View batch, assessments, sessions
```

### As HR
```
Login: hr@maverick.com / hr123
Test: View mavericks, batches, deployment status
```

---

## 📈 Expected Leaderboard Rankings

Based on weighted formula: `(avg_score × 0.7) + (progress × 0.3)`

**Expected Top 5:**
1. Divya Nair (Maverick 10) - 98/95, 100% progress
2. Rahul Kumar (Maverick 1) - 95/92, 95% progress
3. Priya Sharma (Maverick 2) - 90/88, 93% progress
4. Amit Patel (Maverick 3) - 85/75, 90% progress
5. Sneha Reddy (Maverick 4) - 78/72, 85% progress

---

## 💡 Tips

- **Always check logs** for detailed information
- **Logs are timestamped** - easy to track different runs
- **Script is idempotent** - safe to run multiple times
- **Test edge cases** with different maverick logins

---

**Happy Testing! 🚀**
