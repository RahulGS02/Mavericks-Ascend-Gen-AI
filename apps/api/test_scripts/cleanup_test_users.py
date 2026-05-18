"""
Manual Cleanup Utility - Delete Test Users by Email Pattern
Use this ONLY when tracking file is missing but test users exist
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models.user import User
from app.models.maverick import Maverick, ProfileStatus
from app.models.pipeline import Pipeline, PipelineJob
from app.models.batch import Batch
from app.models.progress import MaverickJobProgress
from app.models.assessment import Assessment, AssessmentAttempt
from app.models.training import TrainingSession


def cleanup_test_users():
    """Delete test users by email pattern"""
    db = SessionLocal()
    
    print("\n" + "="*70)
    print("⚠️  MANUAL TEST USER CLEANUP")
    print("="*70)
    print("\nThis will delete:")
    print("  - maverick1@test.com through maverick10@test.com")
    print("  - sarah.trainer@maverick.com")
    print("  - david.trainer@maverick.com")
    print("  - SQL Advanced Batch - Q2 2026")
    print("  - SQL Advanced Training pipeline")
    print("\n⚠️  WARNING: This is a one-time cleanup for when tracking file is missing!")
    
    confirm = input("\nType 'YES' to proceed: ")
    if confirm != "YES":
        print("Cancelled.")
        return
    
    try:
        deleted = {"users": 0, "mavericks": 0, "batches": 0, "pipelines": 0}
        
        # Test email patterns
        test_emails = [f"maverick{i}@test.com" for i in range(1, 11)]
        test_emails.extend(["sarah.trainer@maverick.com", "david.trainer@maverick.com"])
        
        print("\n🗑️  Deleting test users...")
        
        # Delete users and mavericks
        for email in test_emails:
            user = db.query(User).filter(User.email == email).first()
            if user:
                print(f"   Deleting user: {email}")
                
                # Delete related maverick profile
                maverick = db.query(Maverick).filter(Maverick.user_id == user.id).first()
                if maverick:
                    # Delete progress records
                    progress_count = db.query(MaverickJobProgress).filter(
                        MaverickJobProgress.maverick_id == maverick.id
                    ).delete()
                    
                    # Delete assessment attempts
                    attempt_count = db.query(AssessmentAttempt).filter(
                        AssessmentAttempt.maverick_id == maverick.id
                    ).delete()
                    
                    db.delete(maverick)
                    deleted["mavericks"] += 1
                    print(f"      ✓ Deleted maverick profile, {progress_count} progress, {attempt_count} attempts")
                
                db.delete(user)
                deleted["users"] += 1
        
        # Delete test batch
        print("\n🗑️  Deleting test batch...")
        batch = db.query(Batch).filter(Batch.name == "SQL Advanced Batch - Q2 2026").first()
        if batch:
            # Delete related data
            db.query(Assessment).filter(Assessment.batch_id == batch.id).delete()
            db.query(TrainingSession).filter(TrainingSession.batch_id == batch.id).delete()
            db.delete(batch)
            deleted["batches"] += 1
            print(f"   ✓ Deleted batch: {batch.name}")
        
        # Delete test pipeline
        print("\n🗑️  Deleting test pipeline...")
        pipeline = db.query(Pipeline).filter(Pipeline.name == "SQL Advanced Training").first()
        if pipeline:
            db.query(PipelineJob).filter(PipelineJob.pipeline_id == pipeline.id).delete()
            db.delete(pipeline)
            deleted["pipelines"] += 1
            print(f"   ✓ Deleted pipeline: {pipeline.name}")
        
        db.commit()
        
        print("\n" + "="*70)
        print("✅ CLEANUP COMPLETE!")
        print("="*70)
        print(f"\n📊 Summary:")
        print(f"   • Deleted {deleted['users']} users")
        print(f"   • Deleted {deleted['mavericks']} mavericks")
        print(f"   • Deleted {deleted['batches']} batches")
        print(f"   • Deleted {deleted['pipelines']} pipelines")
        print("\n✅ You can now run create_test_data.py successfully!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    cleanup_test_users()
