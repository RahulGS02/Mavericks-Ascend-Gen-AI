# Quick Run Commands

## 🚀 Run Test Data Script

### Option 1: From Project Root
```bash
cd apps/api
python test_scripts/create_test_data.py
```

### Option 2: From test_scripts Directory
```bash
cd apps/api/test_scripts
python create_test_data.py
```

### Option 3: Using Virtual Environment Explicitly (Windows)
```bash
cd apps/api
.\venv\Scripts\python.exe test_scripts\create_test_data.py
```

### Option 4: Using Virtual Environment Explicitly (Linux/Mac)
```bash
cd apps/api
./venv/bin/python test_scripts/create_test_data.py
```

---

## 📋 Expected Runtime

- **Duration**: 30-60 seconds
- **Creates**: 10 mavericks, 2 trainers, 1 batch, 5 jobs, progress, assessments
- **Deletes**: Any existing test data first

---

## 📁 Log File Location

After running, check:
```
apps/api/test_scripts/test_logs/test_data_YYYYMMDD_HHMMSS.log
```

Example:
```
apps/api/test_scripts/test_logs/test_data_20260506_153045.log
```

---

## ✅ Verification Commands

### Check if data was created:
```bash
# From apps/api directory, activate venv first
python -c "
from app.database import SessionLocal
from app.models.user import User
db = SessionLocal()
users = db.query(User).filter(User.email.like('%@test.com')).all()
print(f'Found {len(users)} test users')
for u in users:
    print(f'  - {u.email} ({u.role.value})')
db.close()
"
```

---

## 🔧 Troubleshooting Commands

### Check if database is accessible:
```bash
python -c "from app.database import engine; print('Database connected!' if engine else 'No connection')"
```

### Check virtual environment:
```bash
which python  # Linux/Mac
where python  # Windows
```

---

## 🎯 Full Workflow

```bash
# 1. Navigate to backend
cd apps/api

# 2. Activate virtual environment (if not already active)
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Run test data script
python test_scripts/create_test_data.py

# 4. Check the log file
cat test_scripts/test_logs/test_data_*.log  # Linux/Mac
type test_scripts\test_logs\test_data_*.log  # Windows

# 5. Start backend (in separate terminal)
uvicorn app.main:app --reload

# 6. Start frontend (in another terminal)
cd ../web
npm run dev

# 7. Test in browser
# Open http://localhost:3000
# Login: maverick1@test.com / mav123
```

---

## 🔑 Test Credentials

**Copy-paste ready:**

### Maverick (Student)
```
maverick1@test.com
mav123
```

### Trainer
```
sarah.trainer@maverick.com
trainer123
```

### HR
```
hr@maverick.com
hr123
```

---

## 📊 What to Test

1. **Login as maverick1@test.com**
2. **Click "My Batch"** in sidebar
3. **Verify:**
   - ✅ You see 10 students ranked
   - ✅ Your row is highlighted in blue
   - ✅ Top 3 have special badges (🏆 🥈 🥉)
   - ✅ No actual scores visible
   - ✅ Progress percentages shown
   - ✅ Assessment pass counts shown

---

## 🔄 Re-run Script

To create fresh data:
```bash
# Just run it again - old data is auto-deleted
python test_scripts/create_test_data.py
```

---

## 🐛 If Script Fails

1. **Check log file** for errors
2. **Verify database is running**:
   ```bash
   # Check PostgreSQL service
   # Windows: Check Services app
   # Linux: systemctl status postgresql
   ```
3. **Check .env file** has correct DB credentials
4. **Ensure migrations are applied**:
   ```bash
   alembic upgrade head
   ```

---

## 📝 Sample Log Output

```
2026-05-06 15:30:45 - INFO - 📁 Log file: test_logs/test_data_20260506_153045.log
2026-05-06 15:30:45 - INFO - ======================================================================
2026-05-06 15:30:45 - INFO - 🚀 MAVERICK ASCEND - TEST DATA CREATION
2026-05-06 15:30:45 - INFO - ======================================================================
2026-05-06 15:30:45 - INFO - 
🗑️  Cleaning up existing test data...
2026-05-06 15:30:46 - INFO - ✅ Deleted: 10 users, 10 mavericks, 1 batches, 1 pipelines
2026-05-06 15:30:46 - INFO - 
1️⃣  Getting HR user...
2026-05-06 15:30:46 - INFO -    ✓ HR: hr@maverick.com
...
```

---

**That's it! Run the script and start testing!** 🚀
