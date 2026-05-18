# 🐍 Python Database Migrations - Requirement Workflow

## 📋 Overview

Python scripts for database migrations to implement the **Requirement Card Workflow** feature. These scripts use SQLAlchemy to execute SQL migrations programmatically.

---

## 📦 Migration Files

| File | Description | Run Order |
|------|-------------|-----------|
| `run_migrations.py` | **Main script** - Run this to execute all migrations | ⭐ START HERE |
| `001_create_requirement_workflow_tables.py` | Creates 4 new tables + adds 3 columns | 1️⃣ |
| `002_create_workflow_constraints.py` | Adds validation constraints | 2️⃣ |
| `003_update_existing_data.py` | Updates existing records | 3️⃣ |
| `verify_migrations.py` | Verifies migration success | ✅ After running |
| `README.md` | This file | 📖 |

---

## 🚀 Quick Start (3 Steps)

### **Method 1: Interactive Menu (Recommended)**

```bash
# Navigate to migrations directory
cd apps/api/migrations_python

# Run the master script
python run_migrations.py

# Select option:
#   1. Run all migrations (upgrade)
#   4. Run migrations + verify (recommended!)
```

### **Method 2: Command Line**

```bash
# Navigate to directory
cd apps/api/migrations_python

# Run all migrations
python 001_create_requirement_workflow_tables.py upgrade
python 002_create_workflow_constraints.py upgrade
python 003_update_existing_data.py upgrade

# Verify
python verify_migrations.py
```

### **Method 3: Individual Scripts**

```bash
# Run specific migration
python 001_create_requirement_workflow_tables.py upgrade

# Rollback specific migration
python 001_create_requirement_workflow_tables.py downgrade
```

---

## 🎯 What Gets Created

### **New Tables (4):**

1. **`requirement_candidates`**
   - Stores HR suggestions and manager shortlists
   - Links requirements → candidates → mavericks
   - Match scoring and status tracking

2. **`requirement_interviews`**
   - Interview scheduling (online/offline)
   - Video links, locations, interviewer panels
   - Feedback and ratings (1-5 stars)

3. **`requirement_workflow_history`**
   - Complete audit trail
   - Tracks workflow stage changes

4. **`requirement_notifications`**
   - In-app notifications
   - User and requirement specific

### **Modified Tables (1):**

- **`deployment_requests`** - Added 3 columns:
  - `positions_count` (default: 1)
  - `filled_count` (default: 0)
  - `workflow_stage` (default: 'PENDING')

---

## ✅ Features of Python Migrations

- ✅ **Interactive Menu** - Easy to use interface
- ✅ **Error Handling** - Graceful error recovery
- ✅ **Transaction Safety** - All-or-nothing commits
- ✅ **Verification Built-in** - Automated checks
- ✅ **Rollback Support** - Easy to undo
- ✅ **Progress Tracking** - Shows what's happening
- ✅ **Confirmation Prompts** - Prevents accidents

---

## 📊 Migration Details

### **Migration 001: Create Tables**
- Creates 4 new tables
- Adds 3 columns to `deployment_requests`
- Creates 15+ indexes
- Establishes foreign keys

**Runtime:** ~2-3 seconds

### **Migration 002: Add Constraints**
- Adds 12+ check constraints
- Validates enum values
- Enforces data integrity

**Runtime:** ~1-2 seconds

### **Migration 003: Update Data**
- Sets defaults for existing records
- Maps old status to new workflow_stage
- Counts filled positions

**Runtime:** ~1 second (depends on data volume)

---

## 🔍 Verification

After running migrations, the verification script checks:

- ✅ All 4 tables created
- ✅ All 3 columns added
- ✅ 15+ indexes created
- ✅ 15+ constraints applied
- ✅ 8+ foreign keys established
- ✅ Sample queries working

**Expected output:**
```
✅ ✅ ✅ ALL CHECKS PASSED! Migration successful! ✅ ✅ ✅
```

---

## ⚠️ Prerequisites

### **Python Requirements:**

```bash
# Install dependencies (if not already installed)
pip install sqlalchemy psycopg2-binary tabulate
```

### **Database Access:**

Ensure your `app/database.py` has correct `DATABASE_URL`:

```python
DATABASE_URL = "postgresql://user:password@localhost:5432/dbname"
```

---

## 🔄 Rollback

### **Rollback All Migrations:**

```bash
python run_migrations.py
# Select option 2: Rollback all migrations
```

### **Rollback Individual Migration:**

```bash
python 001_create_requirement_workflow_tables.py downgrade
```

⚠️ **WARNING**: Rollback will DELETE all workflow data!

---

## 🆘 Troubleshooting

### **Error: "No module named 'app.database'"**

```bash
# Make sure you're in the correct directory
cd apps/api/migrations_python

# Check that app/database.py exists
ls ../app/database.py
```

### **Error: "Permission denied"**

Your database user needs:
- CREATE TABLE
- ALTER TABLE
- CREATE INDEX

### **Error: "Table already exists"**

Safe to ignore - scripts use `IF NOT EXISTS`

Or rollback and re-run:
```bash
python run_migrations.py
# Choose option 2 (rollback), then option 1 (upgrade)
```

### **Error: "Foreign key violation"**

Ensure these tables exist:
```sql
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM mavericks;
SELECT COUNT(*) FROM deployment_requests;
```

---

## 📝 Example Usage

### **Full Migration + Verification:**

```bash
cd apps/api/migrations_python
python run_migrations.py

# In the menu:
Select option (1-5): 4  # Run migrations + verify

# Output:
✅ Migration 1/3 completed
✅ Migration 2/3 completed  
✅ Migration 3/3 completed
✅ Verification passed
```

### **Check Status Without Changes:**

```bash
python verify_migrations.py
```

---

## 🔒 Safety Features

1. **Confirmation Prompts** - Asks before destructive operations
2. **Transaction Rollback** - Auto-rollback on errors
3. **IF NOT EXISTS** - Safe to re-run
4. **Error Recovery** - Option to continue on errors
5. **Data Preservation** - Existing data untouched

---

## 📊 Expected Results

### **Before Migration:**
```
deployment_requests: 5 columns
(no workflow tables)
```

### **After Migration:**
```
deployment_requests: 8 columns
requirement_candidates: ✅ Created
requirement_interviews: ✅ Created
requirement_workflow_history: ✅ Created
requirement_notifications: ✅ Created
```

---

## 🎯 Next Steps

After successful migration:

1. ✅ Verify with `python verify_migrations.py`
2. ✅ Create Python models (SQLAlchemy)
3. ✅ Implement API endpoints
4. ✅ Build frontend UI
5. ✅ Test complete workflow

---

## 📧 Support

### **Common Issues:**

| Issue | Solution |
|-------|----------|
| Module not found | Check Python path and directory |
| Permission denied | Grant database privileges |
| Connection error | Check DATABASE_URL in app/database.py |
| Table exists | Safe to ignore or rollback first |

---

## ✅ Success Checklist

- [ ] All migrations run without errors
- [ ] Verification script passes
- [ ] 4 new tables visible in database
- [ ] 3 new columns in deployment_requests
- [ ] Sample queries working

---

**Ready to run! Use `python run_migrations.py` to get started!** 🚀
