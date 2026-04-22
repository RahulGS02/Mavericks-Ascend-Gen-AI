# Maverick Talent Insights Platform

> AI-Powered Training Performance & Competency Tracking Dashboard

## 🎯 Overview

Maverick Talent Insights is a comprehensive platform designed to track and manage the journey of fresh graduates (Mavericks) from onboarding through training to final deployment. The platform leverages GenAI to provide intelligent insights, automated assessments, and optimal talent matching.

## 🏗️ Project Structure

```
maverick-insights/
├── apps/
│   ├── web/              # Next.js Frontend
│   └── api/              # FastAPI Backend
├── packages/
│   └── shared/           # Shared types and utilities
├── docs/                 # Documentation
└── README.md
```

## 👥 User Roles

1. **Maverick** - Fresh graduate trainees
2. **Trainer** - Conducts training and enters assessment marks
3. **HR** - Manages pipelines, batches, and deployments
4. **Manager** - Searches talent and requests deployments
5. **Super Admin** - Platform administration and analytics

## 🚀 Tech Stack

### Frontend
- Next.js 14+ (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui
- Zustand (State Management)
- Recharts (Data Visualization)

### Backend
- FastAPI (Python)
- PostgreSQL
- Supabase
- SQLAlchemy
- Alembic (Migrations)

### AI/ML
- OpenAI GPT-4o-mini
- OpenAI Embeddings API

## 📦 Getting Started

See individual README files in `/apps/web` and `/apps/api` for setup instructions.

## 📅 Development Timeline

- **Week 1**: Foundation & Setup
- **Week 2-3**: Core Features
- **Week 4-6**: AI Integration
- **Week 7-9**: Analytics & Polish
- **Week 10-11**: Testing & Deployment

## ✅ Project Status

- ✅ **Days 1-2**: Project Setup & Database (Complete)
- ✅ **Days 3-4**: Authentication & Frontend Foundation (Complete)
- ⏳ **Day 5+**: Feature Development (Next)

### What's Working Now

✅ **Authentication System**
- Login/Register with JWT
- Role-based access control (5 roles)
- Protected routes

✅ **Database**
- 12 tables in PostgreSQL/Supabase
- Migrations with Alembic
- Sample data loaded

✅ **Frontend**
- Responsive dashboard
- Role-based navigation
- Modern UI with Tailwind CSS

✅ **Backend API**
- FastAPI with auto-docs
- 7 authentication endpoints
- CORS configured

## 📄 License

Proprietary - All rights reserved

## 👨‍💻 Team

Developed for Company Designathon 2024
