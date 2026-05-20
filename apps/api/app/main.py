# ============================================================
# CRITICAL: IPv4 PATCH MUST BE FIRST - Before ANY other imports!
# Azure Free Tier doesn't support outbound IPv6 connections.
# This MUST be imported before fastapi, sqlalchemy, or any networking code.
# ============================================================
import sys
import socket

# Store original getaddrinfo
_original_getaddrinfo = socket.getaddrinfo

def _ipv4_only_getaddrinfo(host, port, family=0, socktype=0, proto=0, flags=0):
    """Force IPv4 for Azure Free Tier compatibility"""
    return _original_getaddrinfo(host, port, socket.AF_INET, socktype, proto, flags)

# Apply patch BEFORE any other imports
socket.getaddrinfo = _ipv4_only_getaddrinfo
sys.stdout.write("🔧 IPv4-only patch applied for Azure compatibility\n")
sys.stdout.flush()
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from app.api.v1 import auth, files, mavericks, hr_workflow, hr_dashboard, maverick_dashboard, trainer_dashboard, trainer_analytics, pipelines, batches, batch_schedule, job_progress, training, assessments, reattempts, deployments, ai_status, resume_parser, batch_suggestions, skill_proficiency, trainer_feedback_api, analytics, trainers, manager_dashboard, manager_search, requirement_workflow, notifications

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Maverick Ascend API starting...")
    yield
    # Shutdown
    print("👋 Shutting down...")

app = FastAPI(
    title="Maverick Ascend API",
    description="AI-Powered Training Performance & Competency Tracking Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Maverick Talent Insights API",
        "status": "operational",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(files.router, prefix="/api/v1/files", tags=["File Upload"])
app.include_router(mavericks.router, prefix="/api/v1/mavericks", tags=["Mavericks"])
app.include_router(hr_workflow.router, prefix="/api/v1/hr", tags=["HR Workflow"])
app.include_router(hr_dashboard.router, prefix="/api/v1/hr/dashboard", tags=["HR Dashboard"])
app.include_router(maverick_dashboard.router, prefix="/api/v1/maverick/dashboard", tags=["Maverick Dashboard"])
app.include_router(trainer_dashboard.router, prefix="/api/v1", tags=["Trainer Dashboard"])
app.include_router(trainer_analytics.router, prefix="/api/v1", tags=["Trainer Analytics"])
app.include_router(pipelines.router, prefix="/api/v1/pipelines", tags=["Pipelines"])
app.include_router(batches.router, prefix="/api/v1/batches", tags=["Batches"])
app.include_router(batch_schedule.router, prefix="/api/v1/batches", tags=["Batch Schedule & Timeline"])
app.include_router(job_progress.router, prefix="/api/v1/job-progress", tags=["Job Progress"])
app.include_router(training.router, prefix="/api/v1/training", tags=["Training"])
app.include_router(assessments.router, prefix="/api/v1/assessments", tags=["Assessments"])
app.include_router(reattempts.router, prefix="/api/v1/reattempts", tags=["Reattempts"])
app.include_router(deployments.router, prefix="/api/v1/deployments", tags=["Deployments"])
app.include_router(ai_status.router, prefix="/api/v1/ai", tags=["AI Service"])
app.include_router(resume_parser.router, prefix="/api/v1/resume", tags=["Resume Parser"])
app.include_router(batch_suggestions.router, prefix="/api/v1/batch-suggestions", tags=["Batch Suggestions"])
app.include_router(skill_proficiency.router, prefix="/api/v1/skill-proficiency", tags=["Skill Proficiency"])
app.include_router(trainer_feedback_api.router, prefix="/api/v1/feedback", tags=["Trainer Feedback"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics & Reports"])
app.include_router(trainers.router, prefix="/api/v1/trainers", tags=["Trainers"])
app.include_router(manager_dashboard.router, prefix="/api/v1", tags=["Manager Dashboard"])
app.include_router(manager_search.router, prefix="/api/v1", tags=["Manager Search"])
app.include_router(requirement_workflow.router, prefix="/api/v1/workflow", tags=["Requirement Workflow"])
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
