"""Quick cleanup - no prompts"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models.user import User
from app.models.maverick import Maverick
from app.models.pipeline import Pipeline, PipelineJob
from app.models.batch import Batch
from app.models.progress import MaverickJobProgress
from app.models.assessment import Assessment, AssessmentAttempt
from app.models.training import TrainingSession

print("=" * 70, flush=True)
print("CLEANUP STARTING...", flush=True)
print("=" * 70, flush=True)

db = SessionLocal()

print("\n🗑️  Deleting test users...", flush=True)

# Delete test users
test_emails = [f"maverick{i}@test.com" for i in range(1, 11)]
test_emails.extend(["sarah.trainer@maverick.com", "david.trainer@maverick.com"])

deleted_count = 0
for email in test_emails:
    user = db.query(User).filter(User.email == email).first()
    if user:
        mav = db.query(Maverick).filter(Maverick.user_id == user.id).first()
        if mav:
            prog_count = db.query(MaverickJobProgress).filter(MaverickJobProgress.maverick_id == mav.id).count()
            att_count = db.query(AssessmentAttempt).filter(AssessmentAttempt.maverick_id == mav.id).count()
            db.query(MaverickJobProgress).filter(MaverickJobProgress.maverick_id == mav.id).delete()
            db.query(AssessmentAttempt).filter(AssessmentAttempt.maverick_id == mav.id).delete()
            db.delete(mav)
            print(f"   ✓ {email} (progress: {prog_count}, attempts: {att_count})", flush=True)
        else:
            print(f"   ✓ {email}", flush=True)
        db.delete(user)
        deleted_count += 1

print(f"\n   Total users deleted: {deleted_count}", flush=True)

# Delete batch
print("\n🗑️  Deleting batch...", flush=True)
batch = db.query(Batch).filter(Batch.name == "SQL Advanced Batch - Q2 2026").first()
if batch:
    ass_count = db.query(Assessment).filter(Assessment.batch_id == batch.id).count()
    sess_count = db.query(TrainingSession).filter(TrainingSession.batch_id == batch.id).count()
    db.query(Assessment).filter(Assessment.batch_id == batch.id).delete()
    db.query(TrainingSession).filter(TrainingSession.batch_id == batch.id).delete()
    db.delete(batch)
    print(f"   ✓ Deleted batch (assessments: {ass_count}, sessions: {sess_count})", flush=True)
else:
    print("   ℹ️  No batch found", flush=True)

# Delete pipeline
print("\n🗑️  Deleting pipeline...", flush=True)
pipeline = db.query(Pipeline).filter(Pipeline.name == "SQL Advanced Training").first()
if pipeline:
    job_count = db.query(PipelineJob).filter(PipelineJob.pipeline_id == pipeline.id).count()
    db.query(PipelineJob).filter(PipelineJob.pipeline_id == pipeline.id).delete()
    db.delete(pipeline)
    print(f"   ✓ Deleted pipeline (jobs: {job_count})", flush=True)
else:
    print("   ℹ️  No pipeline found", flush=True)

print("\n💾 Committing changes...", flush=True)
db.commit()
db.close()

print("\n" + "=" * 70, flush=True)
print("✅ CLEANUP COMPLETE!", flush=True)
print("=" * 70, flush=True)
