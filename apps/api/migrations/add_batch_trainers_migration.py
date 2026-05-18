"""
Migration: Add batch_trainers table for multiple trainers per batch
Run this script to create the junction table and migrate existing data
"""
import sys
import os
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.database import engine


def run_migration():
    """Run the migration to add batch_trainers table"""
    
    migration_sql = """
    -- Create batch_trainers junction table
    CREATE TABLE IF NOT EXISTS batch_trainers (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        batch_id UUID NOT NULL REFERENCES batches(id) ON DELETE CASCADE,
        trainer_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        is_lead_trainer BOOLEAN NOT NULL DEFAULT FALSE,
        assigned_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
        assigned_by UUID REFERENCES users(id),
        
        -- Ensure a trainer is not assigned to the same batch multiple times
        UNIQUE(batch_id, trainer_id)
    );

    -- Add indexes for better query performance
    CREATE INDEX IF NOT EXISTS idx_batch_trainers_batch_id ON batch_trainers(batch_id);
    CREATE INDEX IF NOT EXISTS idx_batch_trainers_trainer_id ON batch_trainers(trainer_id);
    CREATE INDEX IF NOT EXISTS idx_batch_trainers_lead ON batch_trainers(batch_id, is_lead_trainer);

    -- Migrate existing single trainer assignments to the new table
    INSERT INTO batch_trainers (batch_id, trainer_id, is_lead_trainer, assigned_at)
    SELECT 
        id as batch_id,
        trainer_id,
        TRUE as is_lead_trainer,  -- Mark existing trainers as lead
        created_at as assigned_at
    FROM batches
    WHERE trainer_id IS NOT NULL
    ON CONFLICT (batch_id, trainer_id) DO NOTHING;  -- Skip if already exists
    """
    
    print("🔄 Starting migration: Add batch_trainers table...")
    print("-" * 60)
    
    try:
        with engine.connect() as connection:
            # Execute the migration
            connection.execute(text(migration_sql))
            connection.commit()
            
            # Get count of migrated records
            result = connection.execute(text("SELECT COUNT(*) FROM batch_trainers"))
            count = result.scalar()
            
            print("✅ Migration completed successfully!")
            print(f"✅ Created batch_trainers table")
            print(f"✅ Added indexes")
            print(f"✅ Migrated {count} existing trainer assignments")
            print("-" * 60)
            print("🎉 Migration complete! You can now assign multiple trainers to batches.")
            
    except Exception as e:
        print("❌ Migration failed!")
        print(f"Error: {str(e)}")
        print("-" * 60)
        print("💡 Tips:")
        print("1. Make sure the database is running")
        print("2. Check your database connection in .env")
        print("3. Ensure you have the right permissions")
        sys.exit(1)


def rollback_migration():
    """Rollback the migration (drop the table)"""
    
    rollback_sql = """
    -- Drop the table and indexes
    DROP TABLE IF EXISTS batch_trainers CASCADE;
    """
    
    print("🔄 Rolling back migration: Removing batch_trainers table...")
    print("-" * 60)
    
    try:
        with engine.connect() as connection:
            connection.execute(text(rollback_sql))
            connection.commit()
            
            print("✅ Rollback completed successfully!")
            print("✅ Removed batch_trainers table")
            print("-" * 60)
            
    except Exception as e:
        print("❌ Rollback failed!")
        print(f"Error: {str(e)}")
        sys.exit(1)


def check_table_exists():
    """Check if the batch_trainers table already exists"""
    
    check_sql = """
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'batch_trainers'
    );
    """
    
    try:
        with engine.connect() as connection:
            result = connection.execute(text(check_sql))
            exists = result.scalar()
            return exists
    except Exception as e:
        print(f"❌ Error checking table existence: {str(e)}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch Trainers Migration Script")
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Rollback the migration (remove batch_trainers table)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force migration even if table exists"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("  BATCH TRAINERS MIGRATION")
    print("=" * 60)
    print()
    
    if args.rollback:
        confirm = input("⚠️  Are you sure you want to rollback? (yes/no): ")
        if confirm.lower() == "yes":
            rollback_migration()
        else:
            print("❌ Rollback cancelled.")
    else:
        # Check if table already exists
        if check_table_exists() and not args.force:
            print("ℹ️  Table 'batch_trainers' already exists!")
            print("   Use --force to run migration anyway")
            print("   Use --rollback to remove the table")
        else:
            run_migration()
    
    print()
    print("=" * 60)
