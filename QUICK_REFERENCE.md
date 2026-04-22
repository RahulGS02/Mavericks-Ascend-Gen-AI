# Maverick Insights - Quick Reference Guide

## 🚀 Quick Start Commands

### Frontend (Next.js)
```bash
cd apps/web
npm install
npm run dev
# Opens: http://localhost:3000
```

### Backend (FastAPI)
```bash
cd apps/api
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
# Opens: http://localhost:8000/docs
```

## 🗄️ Database Setup

### One-Time Setup
```bash
cd apps/api

# 1. Configure environment
cp .env.example .env
# Edit .env with your database URL

# 2. Run migrations
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head

# 3. Seed sample data
python scripts/seed_data.py
```

### Common Database Commands
```bash
# Check migration status
alembic current

# Create new migration
alembic revision --autogenerate -m "Your message"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Reset database (CAREFUL!)
python scripts/init_db.py --drop
alembic upgrade head
python scripts/seed_data.py
```

## 🔐 Default Login Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@maverick.com | admin123 |
| HR | hr@maverick.com | hr123 |
| Trainer | trainer@maverick.com | trainer123 |
| Manager | manager@maverick.com | manager123 |
| Maverick | maverick1@example.com | maverick123 |

## 📊 Database Tables (12 Total)

1. **users** - Authentication (5 roles)
2. **mavericks** - Trainee profiles
3. **pipelines** - Training templates
4. **pipeline_jobs** - Pipeline stages
5. **batches** - Trainee groups
6. **maverick_job_progress** - Progress tracking
7. **assessment_attempts** - Test scores
8. **deployments** - Final deployments
9. **deployment_requests** - Manager requests
10. **training_sessions** - Training schedule
11. **ai_insights** - AI outputs
12. **audit_logs** - Audit trail

## 🌐 Important URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Next.js app |
| Backend API | http://localhost:8000 | FastAPI server |
| API Docs | http://localhost:8000/docs | Swagger UI |
| API ReDoc | http://localhost:8000/redoc | Alternative docs |

## 📁 Project Structure

```
maverick-insights/
├── apps/
│   ├── web/              # Next.js frontend
│   │   ├── src/
│   │   │   ├── app/      # Pages & routes
│   │   │   ├── components/
│   │   │   ├── lib/
│   │   │   └── store/
│   │   └── package.json
│   └── api/              # FastAPI backend
│       ├── app/
│       │   ├── models/   # Database models
│       │   ├── api/v1/   # API routes
│       │   └── services/ # Business logic
│       ├── alembic/      # Migrations
│       └── scripts/      # Utility scripts
├── packages/shared/      # Shared types
└── docs/                 # Documentation
```

## 🛠️ Tech Stack

**Frontend**: Next.js 14, TypeScript, Tailwind, shadcn/ui, Zustand  
**Backend**: FastAPI, SQLAlchemy, PostgreSQL, Alembic  
**AI**: OpenAI GPT-4o-mini  
**Database**: PostgreSQL (via Supabase)  
**Storage**: Supabase Storage  

## 📝 Environment Variables

### Frontend (.env.local)
```env
NEXT_PUBLIC_SUPABASE_URL=your_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (.env)
```env
DATABASE_URL=postgresql://...
SUPABASE_URL=https://...
SUPABASE_SERVICE_KEY=your_key
OPENAI_API_KEY=sk-...
JWT_SECRET=your_secret
ALLOWED_ORIGINS=http://localhost:3000
```

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Frontend (3000)
npm run dev -- -p 3001

# Backend (8000)
uvicorn app.main:app --reload --port 8001
```

### Database Connection Error
```bash
# Check .env file
# Verify DATABASE_URL is correct
# Test connection:
python -c "from app.database import engine; print(engine)"
```

### Migration Issues
```bash
# Reset migrations
alembic downgrade base
alembic upgrade head
```

## 📚 Documentation Links

- **Setup Guide**: `docs/SETUP.md`
- **Day 1 Complete**: `DAY1_COMPLETE.md`
- **Day 2 Complete**: `DAY2_COMPLETE.md`
- **Database Schema**: `docs/DATABASE_SCHEMA.md`
- **Quick Start**: `QUICKSTART.md`

## 🎯 Development Workflow

1. Start backend: `cd apps/api && uvicorn app.main:app --reload`
2. Start frontend: `cd apps/web && npm run dev`
3. Open browser: http://localhost:3000
4. View API docs: http://localhost:8000/docs
5. Make changes and test
6. Commit when working: `git add . && git commit -m "message"`

## 📊 Project Status

- ✅ Day 1: Project Initialization
- ✅ Day 2: Database Setup
- ⏳ Day 3: Authentication System (Next)

---

**Last Updated**: Day 2  
**Version**: 1.0.0  
**Status**: Development Ready 🚀
