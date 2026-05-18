"""
Test script to manually trigger deployment job auto-activation
Run this to debug why deployment isn't activating
"""
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.services.deployment_service import auto_activate_deployment_job
from app.models.batch import Batch
from app.models.batch_job_schedule import BatchJobSchedule
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_deployment_activation(batch_id: str):
    """Test deployment auto-activation for a specific batch"""
    db = SessionLocal()
    
    try:
        # Get batch
        batch = db.query(Batch).filter(Batch.id == batch_id).first()
        
        if not batch:
            logger.error(f"❌ Batch {batch_id} not found!")
            return
        
        logger.info(f"✅ Found batch: {batch.name}")
        logger.info(f"   Pipeline ID: {batch.pipeline_id}")
        
        # Get all schedules for this batch
        schedules = db.query(BatchJobSchedule).filter(
            BatchJobSchedule.batch_id == batch_id
        ).all()
        
        logger.info(f"\n📋 Current schedules for batch:")
        for schedule in schedules:
            logger.info(f"   - {schedule.pipeline_job.name} ({schedule.pipeline_job.job_type}): {schedule.status}")
        
        # Try to auto-activate
        logger.info(f"\n🚀 Attempting auto-activation...")
        result = auto_activate_deployment_job(db, batch.id, batch.pipeline_id)
        
        if result:
            logger.info(f"\n✅ SUCCESS! Deployment job was activated!")
        else:
            logger.info(f"\n❌ Deployment job was NOT activated - check logs above for reason")
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    # Your batch ID
    batch_id = "01354472-0b08-43fa-add8-20024ab1033b"
    
    logger.info("=" * 60)
    logger.info("DEPLOYMENT AUTO-ACTIVATION TEST")
    logger.info("=" * 60)
    
    test_deployment_activation(batch_id)
    
    logger.info("\n" + "=" * 60)
    logger.info("TEST COMPLETE")
    logger.info("=" * 60)
