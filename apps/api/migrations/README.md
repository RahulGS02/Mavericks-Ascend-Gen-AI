# 🗄️ Database Migrations - Requirement Workflow

## 📋 Overview

This directory contains SQL migration scripts for the **Requirement Card Workflow** feature, which enables a complete talent acquisition process from requirement creation to candidate deployment.

---

## 🎯 What Gets Created

### **New Tables:**
1. **`requirement_candidates`** - Stores suggested/shortlisted candidates for each requirement
2. **`requirement_interviews`** - Manages interview scheduling, feedback, and ratings
3. **`requirement_workflow_history`** - Audit trail for workflow stage transitions
4. **`requirement_notifications`** - Notifications for workflow events

### **Modified Tables:**
- **`deployment_requests`** - Added 3 new columns:
  - `positions_count` - Number of positions to fill
  - `filled_count` - Number of positions filled
  - `workflow_stage` - Current workflow stage

---

## 📦 Migration Files

| File | Description | Order |
|------|-------------|-------|
| `001_create_requirement_workflow_tables.sql` | Creates all new tables and adds columns | 1️⃣ **RUN FIRST** |
| `002_create_workflow_enums.sql` | Adds check constraints for valid values | 2️⃣ |
| `003_update_existing_deployment_requests.sql` | Updates existing records with defaults | 3️⃣ |
| `004_seed_workflow_test_data.sql` | Optional test data (skip in production) | 4️⃣ (Optional) |
| `001_rollback_requirement_workflow_tables.sql` | Rollback script (emergency only) | ⚠️ Destructive |

---

## 🚀 How to Run Migrations

### **Method 1: Using psql (Recommended)**

```bash
# Navigate to migrations directory
cd apps/api/migrations

# Connect to your database and run migrations in order
psql -U your_username -d your_database_name -f 001_create_requirement_workflow_tables.sql
psql -U your_username -d your_database_name -f 002_create_workflow_enums.sql
psql -U your_username -d your_database_name -f 003_update_existing_deployment_requests.sql

# Optional: Test data (SKIP in production)
# psql -U your_username -d your_database_name -f 004_seed_workflow_test_data.sql
```

### **Method 2: Using pgAdmin**

1. Open pgAdmin
2. Connect to your database
3. Open Query Tool
4. Open each migration file in order
5. Execute (F5)
6. Verify success messages

### **Method 3: Using DBeaver**

1. Open DBeaver
2. Connect to your PostgreSQL database
3. Right-click database → SQL Editor → Open SQL Script
4. Open `001_create_requirement_workflow_tables.sql`
5. Execute (Ctrl+Enter)
6. Repeat for each file in order

### **Method 4: Copy-Paste**

```bash
# Copy the content of migration files and paste into your database client
# Run in this order:
# 1. 001_create_requirement_workflow_tables.sql
# 2. 002_create_workflow_enums.sql
# 3. 003_update_existing_deployment_requests.sql
```

---

## ✅ Verification

After running migrations, verify tables were created:

```sql
-- Check if tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'requirement_candidates',
    'requirement_interviews',
    'requirement_workflow_history',
    'requirement_notifications'
);

-- Check if columns were added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'deployment_requests' 
AND column_name IN ('positions_count', 'filled_count', 'workflow_stage');

-- Check constraints
SELECT constraint_name, constraint_type 
FROM information_schema.table_constraints 
WHERE table_name IN ('requirement_candidates', 'requirement_interviews')
ORDER BY table_name;
```

Expected result: 4 tables + 3 new columns + multiple constraints

---

## 🔄 Rollback (Emergency Only)

⚠️ **WARNING**: This will DELETE all workflow data!

```bash
psql -U your_username -d your_database_name -f 001_rollback_requirement_workflow_tables.sql
```

---

## 📊 Database Schema Overview

```
deployment_requests (MODIFIED)
├── positions_count (NEW)
├── filled_count (NEW)
└── workflow_stage (NEW)

requirement_candidates (NEW)
├── id
├── requirement_id → deployment_requests
├── maverick_id → mavericks
├── suggested_by → users
├── match_score
├── status
├── shortlist_notes
└── rejection_reason

requirement_interviews (NEW)
├── id
├── requirement_id → deployment_requests
├── candidate_id → requirement_candidates
├── maverick_id → mavericks
├── interview_date
├── interview_time
├── interview_type
├── interview_mode
├── location
├── video_link
├── interviewer_panel (JSONB)
├── status
├── feedback
└── rating

requirement_workflow_history (NEW)
├── id
├── requirement_id → deployment_requests
├── from_stage
├── to_stage
└── changed_by → users

requirement_notifications (NEW)
├── id
├── requirement_id → deployment_requests
├── user_id → users
├── notification_type
├── title
├── message
└── is_read
```

---

## 🎯 Next Steps

After running migrations successfully:

1. ✅ Verify all tables and columns exist
2. ✅ Check constraints are applied
3. ✅ Backend models need to be created (Python)
4. ✅ API endpoints need to be implemented
5. ✅ Frontend pages need to be built

---

## 📝 Notes

- All migrations use `IF NOT EXISTS` to prevent errors on re-run
- Constraints ensure data integrity
- Indexes added for query performance
- Foreign keys use `ON DELETE CASCADE` for cleanup
- JSONB used for flexible data (interviewer panel, metadata)

---

## 🆘 Troubleshooting

### Migration fails with "column already exists"
- Safe to ignore if using `IF NOT EXISTS`
- Or run rollback script first

### Foreign key constraint error
- Ensure parent tables have data
- Check UUID references are valid

### Permission denied
- Ensure your database user has CREATE/ALTER privileges
- Use superuser or database owner account

---

## 📧 Support

For issues or questions about migrations, check:
- PostgreSQL error logs
- Database constraints
- Foreign key relationships
