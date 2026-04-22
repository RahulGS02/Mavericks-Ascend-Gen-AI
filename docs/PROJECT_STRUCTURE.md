# Maverick Talent Insights - Project Structure

## 📁 Complete Directory Tree

```
maverick-insights/
│
├── 📄 README.md                    # Main project documentation
├── 📄 QUICKSTART.md               # Quick installation guide
├── 📄 DAY1_COMPLETE.md            # Day 1 completion summary
├── 📄 package.json                # Root package.json with workspace config
├── 📄 .gitignore                  # Git ignore rules
├── 📄 .gitattributes              # Git line ending configuration
│
├── 📂 apps/                       # Application code
│   │
│   ├── 📂 web/                    # Frontend (Next.js)
│   │   ├── 📂 src/
│   │   │   ├── 📂 app/
│   │   │   │   ├── layout.tsx    # Root layout with providers
│   │   │   │   ├── page.tsx      # Landing page
│   │   │   │   └── globals.css   # Global styles + Tailwind
│   │   │   └── 📂 lib/
│   │   │       └── utils.ts      # Utility functions
│   │   ├── 📄 package.json       # Frontend dependencies
│   │   ├── 📄 next.config.js     # Next.js configuration
│   │   ├── 📄 tsconfig.json      # TypeScript configuration
│   │   ├── 📄 tailwind.config.ts # Tailwind CSS configuration
│   │   ├── 📄 postcss.config.js  # PostCSS configuration
│   │   ├── 📄 components.json    # shadcn/ui configuration
│   │   └── 📄 .env.local.example # Environment variables template
│   │
│   └── 📂 api/                    # Backend (FastAPI)
│       ├── 📂 app/
│       │   ├── __init__.py
│       │   ├── main.py           # FastAPI application entry
│       │   ├── 📂 models/        # SQLAlchemy models (Day 2)
│       │   ├── 📂 schemas/       # Pydantic schemas (Day 2)
│       │   ├── 📂 api/
│       │   │   └── 📂 v1/        # API v1 routes (Day 3+)
│       │   ├── 📂 services/      # Business logic (Day 3+)
│       │   └── 📂 utils/         # Utility functions (Day 3+)
│       ├── 📄 requirements.txt   # Python dependencies
│       ├── 📄 .env.example       # Environment variables template
│       └── 📄 README.md          # Backend documentation
│
├── 📂 packages/                   # Shared packages
│   └── 📂 shared/
│       └── types.ts              # Shared TypeScript types
│
├── 📂 scripts/                    # Automation scripts
│   └── setup.js                  # Project setup script
│
└── 📂 docs/                       # Documentation
    ├── SETUP.md                  # Detailed setup guide
    ├── DAY1_CHECKLIST.md         # Day 1 completion checklist
    └── PROJECT_STRUCTURE.md      # This file
```

## 🎨 Frontend Stack

### Core Framework
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS

### UI Components
- **shadcn/ui** - Accessible component library
- **Radix UI** - Primitive components
- **Lucide React** - Icons
- **Framer Motion** - Animations

### State & Data
- **Zustand** - State management
- **Axios** - HTTP client
- **React Hook Form** - Form handling
- **Zod** - Schema validation

### Visualization
- **Recharts** - Data visualization
- **Sonner** - Toast notifications

## 🐍 Backend Stack

### Core Framework
- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

### Database
- **SQLAlchemy** - ORM
- **PostgreSQL** - Database
- **Alembic** - Migrations

### Authentication
- **python-jose** - JWT tokens
- **passlib** - Password hashing

### AI/ML
- **OpenAI** - GPT-4o-mini API

### Data Processing
- **Pandas** - Data manipulation
- **openpyxl** - Excel files

### Testing
- **Pytest** - Testing framework
- **httpx** - Async HTTP client

## 🔧 Configuration Files

| File | Purpose |
|------|---------|
| `package.json` | NPM dependencies & scripts |
| `next.config.js` | Next.js configuration |
| `tsconfig.json` | TypeScript compiler options |
| `tailwind.config.ts` | Tailwind CSS theming |
| `components.json` | shadcn/ui setup |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment variables template |

## 🌐 Development URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | Next.js dev server |
| Backend | http://localhost:8000 | FastAPI server |
| API Docs | http://localhost:8000/docs | Swagger UI |
| API ReDoc | http://localhost:8000/redoc | Alternative docs |

## 📦 Key Dependencies

### Frontend (34 packages)
- next: ^14.2.18
- react: ^18
- typescript: ^5
- tailwindcss: ^3.4.1
- zustand: ^4.5.5
- axios: ^1.7.7
- recharts: ^2.12.7

### Backend (20 packages)
- fastapi: 0.115.4
- uvicorn: 0.32.0
- sqlalchemy: 2.0.36
- alembic: 1.14.0
- openai: 1.54.4
- pandas: 2.2.3

## 🎯 Next Steps

After Day 1 completion:
1. Install all dependencies
2. Set up environment variables
3. Test development servers
4. Proceed to **Day 2: Database Setup**

---

**Last Updated**: Day 1 - Project Initialization  
**Status**: ✅ Complete
