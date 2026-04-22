# 🚀 Maverick Insights - Complete Setup & Development Guide

## 📋 Table of Contents
1. [Quick Start (3 Steps)](#quick-start)
2. [Database Setup](#database-setup)
3. [Test Credentials](#test-credentials)
4. [Features Available](#features-available)
5. [API Documentation](#api-documentation)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Step 1: Start Backend API (Terminal 1)

```bash
cd apps/api
venv\Scripts\activate
uvicorn app.main:app --reload
```

✅ Backend runs on: **http://localhost:8000**
✅ API Docs: **http://localhost:8000/docs**

### Step 2: Start Frontend (Terminal 2)

```bash
cd apps/web
npm run dev
```

✅ Frontend runs on: **http://localhost:3000**

### Step 3: Open Browser

Visit: **http://localhost:3000**

---

## 🔐 Test Login Credentials

| Role | Email | Password | Access Level |
|------|-------|----------|--------------|
| **Super Admin** | admin@maverick.com | admin123 | Full access |
| **HR** | hr@maverick.com | hr123 | Hiring & Training |
| **Trainer** | trainer@maverick.com | trainer123 | Training & Assessment |
| **Manager** | manager@maverick.com | manager123 | Deployment |
| **Maverick** | maverick1@example.com | maverick123 | Trainee view |

---

## ✅ Quick Test

1. Click **"Sign In"**
2. Login with: `admin@maverick.com` / `admin123`
3. You should see:
   - ✅ Dashboard with stats
   - ✅ Sidebar with navigation
   - ✅ Welcome message

---

## 📋 What's Available

### ✅ Working Features (Day 1-3)

- 🔐 **Authentication** - Login, Register, Logout
- 👤 **User Management** - JWT tokens, role-based access
- 📊 **Dashboard** - Overview with mock stats
- 🎨 **UI/UX** - Responsive design, modern interface
- 🛡️ **Security** - Protected routes, token management

### ⏳ Coming Soon (Day 4+)

- 👥 **Mavericks** - List, create, manage trainees
- 📚 **Pipelines** - Training workflows
- 🎓 **Batches** - Group management
- 📝 **Assessments** - Testing & scoring
- 🚀 **Deployments** - Project assignments
- 🤖 **AI Features** - Resume parsing, skill extraction

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Reinstall dependencies
cd apps/api
pip install -r requirements.txt
```

### Frontend won't start
```bash
# Reinstall dependencies
cd apps/web
npm install
```

### "Cannot connect to server"
Make sure backend is running on port 8000

### "CORS Error"
Already configured! Ensure ports are 8000 (backend) and 3000 (frontend)

---

## 📁 Project Structure

```
maverick-insights/
├── apps/
│   ├── web/              # Next.js Frontend (Port 3000)
│   │   ├── src/
│   │   │   ├── app/      # Pages (login, register, dashboard)
│   │   │   ├── components/  # React components
│   │   │   ├── lib/      # API client
│   │   │   └── store/    # State management
│   │   └── package.json
│   └── api/              # FastAPI Backend (Port 8000)
│       ├── app/
│       │   ├── api/v1/   # API routes
│       │   ├── models/   # Database models (12 tables)
│       │   ├── schemas/  # Request/response schemas
│       │   └── services/ # Business logic
│       └── requirements.txt
└── docs/                 # Documentation
```

---

## 📊 Database

**12 Tables Created:**
1. users - Authentication
2. mavericks - Trainee profiles
3. pipelines - Training workflows
4. pipeline_jobs - Workflow stages
5. batches - Trainee groups
6. maverick_job_progress - Progress tracking
7. assessment_attempts - Test scores
8. deployments - Project assignments
9. deployment_requests - Manager requests
10. training_sessions - Schedule
11. ai_insights - AI outputs
12. audit_logs - Audit trail

**Database**: PostgreSQL via Supabase
**ORM**: SQLAlchemy
**Migrations**: Alembic

---

## 🛠️ Tech Stack

**Frontend:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Zustand (State)
- Axios (HTTP)

**Backend:**
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- JWT Authentication
- Python 3.12

---

---

## API Documentation

### Swagger UI (Interactive)

Visit: **http://localhost:8000/docs**

Try all endpoints directly in browser:
1. Click on endpoint (e.g., `/api/v1/auth/login`)
2. Click "Try it out"
3. Enter data
4. Click "Execute"
5. See response

### Authentication Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/auth/register` | POST | No | Register new user |
| `/api/v1/auth/login` | POST | No | Login & get JWT |
| `/api/v1/auth/me` | GET | Yes | Get current user |
| `/api/v1/auth/change-password` | POST | Yes | Change password |
| `/api/v1/auth/logout` | POST | Yes | Logout |

### How to Use Protected Endpoints

1. Login to get token
2. Click "Authorize" button in Swagger
3. Enter: `Bearer YOUR_TOKEN_HERE`
4. Now you can call protected endpoints

---

## 📚 Documentation Files

Essential docs (only 3 files):
- `README.md` - Project overview & features
- `QUICK_START.md` - This file (setup & reference)
- `QUICK_REFERENCE.md` - Quick command reference

---

---

## Database Setup

### First Time Setup

If database is not set up yet:

```bash
cd apps/api
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Seed sample data
python scripts\seed_data.py
```

### Database Configuration

**File**: `apps/api/.env`

```env
DATABASE_URL=postgresql://postgres.aeogndsqjkbfshofudpk:CICDp%40104400@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres
SUPABASE_URL=https://aeogndsqjkbfshofudpk.supabase.co
JWT_SECRET=maverick_insights_super_secret_jwt_key_2024
```

**Tables Created** (12 total):
- users, mavericks, pipelines, pipeline_jobs, batches
- maverick_job_progress, assessment_attempts, deployments
- deployment_requests, training_sessions, ai_insights, audit_logs

---

---

## File Upload Setup (Day 5)

### Install Supabase Storage Dependencies

```bash
cd apps/api
venv\Scripts\activate
pip install supabase storage3
```

### Setup Storage Buckets in Supabase

**Important**: You need to add your Supabase Service Key to `.env` first!

1. Go to https://supabase.com/dashboard/project/aeogndsqjkbfshofudpk/settings/api
2. Copy the **service_role key** (not anon key!)
3. Update `apps/api/.env`:
   ```
   SUPABASE_SERVICE_KEY=your_service_role_key_here
   ```

4. Run setup script:
   ```bash
   python scripts/setup_storage.py
   ```

This creates 3 storage buckets:
- **resumes** - For resume files (PDF, DOC, DOCX) - 5MB limit
- **excel-files** - For Excel/CSV files - 10MB limit
- **uploads** - General uploads - 10MB limit

### Test File Upload

```bash
python test_file_upload.py
```

This tests:
- ✅ Resume upload (PDF)
- ✅ Excel/CSV upload
- ✅ File download
- ✅ File size validation
- ✅ File type validation

---

## 🎯 Project Status

- ✅ **Foundation Complete** - Auth, Database, Dashboard, File Upload
- ⏳ **Next**: Maverick Management with Resume Upload

---

## 🎉 You're All Set!

If you can:
- ✅ See the login page
- ✅ Login successfully
- ✅ See the dashboard
- ✅ Navigate the sidebar

**Then you're ready to build features!** 🚀

---

---

**Status**: ✅ Foundation Complete | **Next**: Feature Development
**Last Updated**: Days 1-4 Complete

---

**Happy Coding! 🎨**
