# 🚀 Quick Start Guide

## Prerequisites
- Node.js 18+ and npm
- Python 3.10+
- Git

## Installation (5 minutes)

### 1. Install Frontend Dependencies
```bash
cd apps/web
npm install
```

This installs:
- Next.js 14
- TypeScript
- Tailwind CSS
- shadcn/ui components
- Zustand (state management)
- Recharts (data visualization)
- React Hook Form + Zod
- And more...

### 2. Install Backend Dependencies
```bash
cd apps/api

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

This installs:
- FastAPI
- SQLAlchemy + PostgreSQL driver
- Alembic (migrations)
- JWT authentication
- OpenAI SDK
- Pandas + openpyxl
- And more...

### 3. Environment Setup

**Frontend** (`apps/web/.env.local`):
```env
NEXT_PUBLIC_SUPABASE_URL=your_url_here
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_key_here
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend** (`apps/api/.env`):
```env
DATABASE_URL=postgresql://user:password@localhost:5432/maverick_insights_dev
OPENAI_API_KEY=your_openai_key_here
JWT_SECRET=your_secret_here
ALLOWED_ORIGINS=http://localhost:3000
```

### 4. Run Development Servers

**Terminal 1 - Frontend:**
```bash
cd apps/web
npm run dev
```
Opens at: http://localhost:3000

**Terminal 2 - Backend:**
```bash
cd apps/api
venv\Scripts\activate
python -m uvicorn app.main:app --reload
```
Opens at: http://localhost:8000
API Docs: http://localhost:8000/docs

## ✅ Verify Installation

1. Visit http://localhost:3000 - Should see landing page
2. Visit http://localhost:8000/health - Should return `{"status": "healthy"}`
3. Visit http://localhost:8000/docs - Should see API documentation

## 🎯 What's Next?

- **Day 2**: Database setup with PostgreSQL/Supabase
- **Day 3**: Authentication system
- **Day 4**: Core APIs

See `/docs/SETUP.md` for detailed documentation.

## 🐛 Troubleshooting

### Frontend Issues
- **Error**: Module not found
  - **Fix**: Run `npm install` again in `apps/web`

- **Error**: Port 3000 in use
  - **Fix**: Change port with `npm run dev -- -p 3001`

### Backend Issues
- **Error**: Module not found
  - **Fix**: Activate venv and run `pip install -r requirements.txt`

- **Error**: Port 8000 in use
  - **Fix**: Change port: `uvicorn app.main:app --reload --port 8001`

### Need Help?
Check `/docs/SETUP.md` for comprehensive setup guide.

## 📚 Project Structure

```
maverick-insights/
├── apps/
│   ├── web/              # Next.js frontend
│   └── api/              # FastAPI backend
├── packages/
│   └── shared/           # Shared types
├── docs/                 # Documentation
└── README.md
```

**Status: Day 1 Complete ✅**
