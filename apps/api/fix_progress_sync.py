"""
One-time script to sync progress records for completed jobs
This creates missing maverick_job_progress records for jobs that are marked COMPLETED
but don't have corresponding progress records.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.models.batch import Batch
from app.models.batch_job_schedule import BatchJobSchedule, JobScheduleStatus
from app.models.maverick import Maverick
from app.models.progress import MaverickJobProgress, ProgressStatus
from datetime import datetime
from uuid import UUID

def sync_progress_for_batch(batch_id: str):
    """Sync progress records for a specific batch"""
    db = SessionLocal()
    
    try:
        batch_uuid = UUID(batch_id)
        
        # Get all completed jobs for this batch
        completed_jobs = db.query(BatchJobSchedule).filter(
            BatchJobSchedule.batch_id == batch_uuid,
            BatchJobSchedule.status == JobScheduleStatus.COMPLETED
        ).all()
        
        print(f"\n📊 Found {len(completed_jobs)} completed jobs for batch {batch_id}")
        
        if not completed_jobs:
            print("❌ No completed jobs found!")
            return
        
        # Get all mavericks in this batch
        mavericks = db.query(Maverick).filter(
            Maverick.current_batch_id == batch_uuid
        ).all()
        
        print(f"👥 Found {len(mavericks)} mavericks in batch")
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for job_schedule in completed_jobs:
            print(f"\n🔍 Processing job: {job_schedule.pipeline_job.name}")
            print(f"   Attendance count: {job_schedule.attendance_count}")
            
            # Check if attendance was tracked
            if job_schedule.attendance_count and job_schedule.attendance_count > 0:
                print(f"   ⚠️  Attendance was tracked. Need to identify who attended...")
                print(f"   ⚠️  For now, creating progress for ALL students (you may need to manually verify)")
            
            for maverick in mavericks:
                # Check if progress record exists
                progress = db.query(MaverickJobProgress).filter(
                    MaverickJobProgress.maverick_id == maverick.id,
                    MaverickJobProgress.batch_id == batch_uuid,
                    MaverickJobProgress.job_id == job_schedule.pipeline_job_id
                ).first()
                
                if progress:
                    # Update if not completed
                    if progress.status != ProgressStatus.COMPLETED:
                        progress.status = ProgressStatus.COMPLETED
                        progress.completion_percentage = 100
                        progress.completed_at = job_schedule.actual_end_date or datetime.utcnow()
                        updated_count += 1
                        print(f"      ✅ Updated {maverick.name}")
                    else:
                        skipped_count += 1
                else:
                    # Create new progress record
                    new_progress = MaverickJobProgress(
                        maverick_id=maverick.id,
                        batch_id=batch_uuid,
                        job_id=job_schedule.pipeline_job_id,
                        status=ProgressStatus.COMPLETED,
                        completion_percentage=100,
                        started_at=job_schedule.actual_start_date or job_schedule.scheduled_start_date or datetime.utcnow(),
                        completed_at=job_schedule.actual_end_date or datetime.utcnow()
                    )
                    db.add(new_progress)
                    created_count += 1
                    print(f"      ➕ Created for {maverick.name}")
        
        db.commit()
        
        print(f"\n✨ Sync complete!")
        print(f"   ➕ Created: {created_count}")
        print(f"   ✅ Updated: {updated_count}")
        print(f"   ⏭️  Skipped: {skipped_count}")
        print(f"   📊 Total: {created_count + updated_count + skipped_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    # Java FSD 2026 batch ID
    BATCH_ID = "01354472-0b08-43fa-add8-20024ab1033b"
    
    print("🚀 Starting progress sync...")
    print(f"📦 Batch ID: {BATCH_ID}")
    
    sync_progress_for_batch(BATCH_ID)
    
    print("\n✅ Done! Please refresh the UI to see updated progress.")
