"""
Quick script to apply the batch_job_schedules migration
"""
import sys
import os

# Add the app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from alembic.config import Config
from alembic import command

def run_migration():
    """Run alembic upgrade to apply pending migrations"""
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        alembic_ini = os.path.join(script_dir, 'alembic.ini')
        
        # Create Alembic configuration
        alembic_cfg = Config(alembic_ini)
        
        # Run upgrade to head
        print("🔄 Running alembic upgrade head...")
        command.upgrade(alembic_cfg, "head")
        print("✅ Migration completed successfully!")
        
        # Show current revision
        print("\n📊 Current database revision:")
        command.current(alembic_cfg)
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    run_migration()
