"""
Database models for Maverick Talent Insights Platform
"""

from .user import User, UserRole
from .maverick import Maverick, ProfileStatus, DeploymentStatus
from .pipeline import Pipeline, PipelineJob, JobType
from .batch import Batch, BatchStatus
from .progress import MaverickJobProgress, JobProgressStatus
from .assessment import AssessmentAttempt
from .deployment import Deployment, DeploymentRequest, DeploymentRequestStatus
from .training import TrainingSession
from .ai_insights import AIInsight
from .audit import AuditLog

__all__ = [
    # User
    "User",
    "UserRole",

    # Maverick
    "Maverick",
    "ProfileStatus",
    "DeploymentStatus",

    # Pipeline
    "Pipeline",
    "PipelineJob",
    "JobType",

    # Batch
    "Batch",
    "BatchStatus",

    # Progress
    "MaverickJobProgress",
    "JobProgressStatus",

    # Assessment
    "AssessmentAttempt",

    # Deployment
    "Deployment",
    "DeploymentRequest",
    "DeploymentRequestStatus",

    # Training
    "TrainingSession",

    # AI
    "AIInsight",

    # Audit
    "AuditLog",
]
