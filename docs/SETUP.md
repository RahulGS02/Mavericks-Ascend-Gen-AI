# Project Setup Guide - Day 1

## Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- Git
- PostgreSQL (or Supabase account)

## Step-by-Step Setup

### 1. Clone and Initialize

```bash
cd c:\rahul\GenAi\GEN-AI-project
git init
npm install
```

### 2. Setup Frontend (Next.js)

```bash
cd apps/web

# Create Next.js app (if not already created)
npx create-next-app@latest . --typescript --tailwind --app --src-dir --import-alias "@/*"

# Install core dependencies
npm install @supabase/supabase-js zustand date-fns clsx
npm install lucide-react framer-motion
npm install recharts
npm install react-hook-form zod @hookform/resolvers
npm install sonner axios

# Install shadcn/ui
npx shadcn-ui@latest init

# Add UI components
npx shadcn-ui@latest add button card input label
npx shadcn-ui@latest add select textarea checkbox
npx shadcn-ui@latest add dialog dropdown-menu
npx shadcn-ui@latest add table badge avatar
npx shadcn-ui@latest add alert progress separator
npx shadcn-ui@latest add calendar popover
```

### 3. Setup Backend (FastAPI)

```bash
cd apps/api

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn[standard]
pip install sqlalchemy psycopg2-binary alembic
pip install pydantic pydantic-settings
pip install python-jose[cryptography] passlib[bcrypt]
pip install python-multipart
pip install openai
pip install pandas openpyxl
pip install pytest pytest-asyncio httpx
pip install python-dotenv

# Save requirements
pip freeze > requirements.txt
```

### 4. Environment Variables

Create `.env` files:

**apps/web/.env.local:**
```env
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**apps/api/.env:**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/maverick_insights_dev
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key
OPENAI_API_KEY=your_openai_key
JWT_SECRET=your_jwt_secret_here
ENVIRONMENT=development
```

### 5. Verify Setup

```bash
# Test frontend
cd apps/web
npm run dev
# Should run on http://localhost:3000

# Test backend
cd apps/api
uvicorn main:app --reload
# Should run on http://localhost:8000
```

## Project Structure

```
maverick-insights/
├── apps/
│   ├── web/              # Next.js Frontend
│   │   ├── src/
│   │   │   ├── app/      # App router pages
│   │   │   ├── components/
│   │   │   ├── lib/
│   │   │   ├── hooks/
│   │   │   └── store/
│   │   └── package.json
│   └── api/              # FastAPI Backend
│       ├── app/
│       │   ├── models/
│       │   ├── schemas/
│       │   ├── api/
│       │   ├── services/
│       │   └── utils/
│       ├── alembic/
│       └── requirements.txt
├── packages/
│   └── shared/           # Shared types
├── docs/                 # Documentation
└── package.json          # Root package.json
```

## Next Steps

Proceed to Day 2: Database Setup
