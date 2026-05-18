"""
Database models for Maverick Ascend Platform
"""

from .user import User, UserRole
from .maverick import Maverick, ProfileStatus, DeploymentStatus
from .pipeline import Pipeline, PipelineJob, JobType
from .batch import Batch, BatchStatus
from .batch_trainer import BatchTrainer
from .batch_job_schedule import BatchJobSchedule, JobScheduleStatus
from .progress import MaverickJobProgress, JobProgressStatus
from .assessment import Assessment, AssessmentAttempt
from .deployment import Deployment, DeploymentRequest, DeploymentRequestStatus
from .training import TrainingSession
from .maverick_skill import MaverickSkill
from .ai_insights import AIInsight
from .audit import AuditLog
from .trainer_feedback import TrainerFeedback, FeedbackRating

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
    "BatchTrainer",
    "BatchJobSchedule",
    "JobScheduleStatus",

    # Progress
    "MaverickJobProgress",
    "JobProgressStatus",

    # Assessment
    "Assessment",
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

    # Trainer Feedback
    "TrainerFeedback",
    "FeedbackRating",

    # Skills
    "MaverickSkill",
]
