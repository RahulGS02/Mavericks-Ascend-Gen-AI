"""
Migration: Create Requirement Workflow Tables
Description: Creates tables for candidate suggestions, interviews, and workflow tracking
Date: 2026-05-16
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from apps/api/.env
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not found in environment variables!")
    print(f"Looked for .env file at: {env_path}")
    print("Please set DATABASE_URL in your .env file or environment.")
    sys.exit(1)

def upgrade():
    """Create workflow tables and add columns"""
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("=" * 80)
        print("Starting Migration: Create Requirement Workflow Tables")
        print("=" * 80)
        
        # 1. ALTER deployment_requests table
        print("\n[1/5] Adding columns to deployment_requests...")
        conn.execute(text("""
            ALTER TABLE deployment_requests 
            ADD COLUMN IF NOT EXISTS positions_count INTEGER DEFAULT 1;
        """))
        conn.execute(text("""
            ALTER TABLE deployment_requests 
            ADD COLUMN IF NOT EXISTS filled_count INTEGER DEFAULT 0;
        """))
        conn.execute(text("""
            ALTER TABLE deployment_requests 
            ADD COLUMN IF NOT EXISTS workflow_stage VARCHAR(50) DEFAULT 'PENDING';
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_deployment_requests_workflow_stage 
            ON deployment_requests(workflow_stage);
        """))
        conn.commit()
        print("✅ Columns added successfully")
        
        # 2. CREATE requirement_candidates table
        print("\n[2/5] Creating requirement_candidates table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS requirement_candidates (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                requirement_id UUID NOT NULL REFERENCES deployment_requests(id) ON DELETE CASCADE,
                maverick_id UUID NOT NULL REFERENCES mavericks(id) ON DELETE CASCADE,
                suggested_by UUID REFERENCES users(id) ON DELETE SET NULL,
                suggestion_date TIMESTAMP DEFAULT NOW(),
                match_score DECIMAL(5,2),
                status VARCHAR(50) DEFAULT 'SUGGESTED',
                shortlist_notes TEXT,
                rejection_reason TEXT,
                manager_notes TEXT,
                hr_notes TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                CONSTRAINT unique_requirement_maverick UNIQUE (requirement_id, maverick_id)
            );
        """))
        
        # Create indexes
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_requirement_candidates_requirement 
            ON requirement_candidates(requirement_id);
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_requirement_candidates_maverick 
            ON requirement_candidates(maverick_id);
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_requirement_candidates_status 
            ON requirement_candidates(status);
        """))
        conn.commit()
        print("✅ requirement_candidates table created")
        
        # 3. CREATE requirement_interviews table
        print("\n[3/5] Creating requirement_interviews table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS requirement_interviews (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                requirement_id UUID NOT NULL REFERENCES deployment_requests(id) ON DELETE CASCADE,
                candidate_id UUID NOT NULL REFERENCES requirement_candidates(id) ON DELETE CASCADE,
                maverick_id UUID NOT NULL REFERENCES mavericks(id) ON DELETE CASCADE,
                interview_type VARCHAR(20) DEFAULT 'ONLINE',
                interview_mode VARCHAR(50) DEFAULT 'VIDEO_CALL',
                interview_date DATE NOT NULL,
                interview_time TIME NOT NULL,
                duration_minutes INTEGER DEFAULT 60,
                location TEXT,
                video_link TEXT,
                interviewer_panel JSONB DEFAULT '[]',
                status VARCHAR(50) DEFAULT 'SCHEDULED',
                feedback TEXT,
                rating DECIMAL(2,1),
                technical_rating DECIMAL(2,1),
                communication_rating DECIMAL(2,1),
                cultural_fit_rating DECIMAL(2,1),
                scheduled_by UUID REFERENCES users(id) ON DELETE SET NULL,
                completed_by UUID REFERENCES users(id) ON DELETE SET NULL,
                completed_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
        """))
        
        # Create indexes
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_requirement_interviews_requirement 
            ON requirement_interviews(requirement_id);
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_requirement_interviews_candidate 
            ON requirement_interviews(candidate_id);
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_requirement_interviews_maverick 
            ON requirement_interviews(maverick_id);
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_requirement_interviews_status 
            ON requirement_interviews(status);
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_requirement_interviews_date 
            ON requirement_interviews(interview_date);
        """))
        conn.commit()
        print("✅ requirement_interviews table created")
        
        # 4. CREATE requirement_workflow_history table
        print("\n[4/5] Creating requirement_workflow_history table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS requirement_workflow_history (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                requirement_id UUID NOT NULL REFERENCES deployment_requests(id) ON DELETE CASCADE,
                from_stage VARCHAR(50),
                to_stage VARCHAR(50) NOT NULL,
                changed_by UUID REFERENCES users(id) ON DELETE SET NULL,
                change_reason TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_requirement_workflow_history_requirement 
            ON requirement_workflow_history(requirement_id);
        """))
        conn.commit()
        print("✅ requirement_workflow_history table created")

        # 5. CREATE requirement_notifications table
        print("\n[5/5] Creating requirement_notifications table...")
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS requirement_notifications (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                requirement_id UUID NOT NULL REFERENCES deployment_requests(id) ON DELETE CASCADE,
                user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                notification_type VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT FALSE,
                read_at TIMESTAMP,
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT NOW()
            );
        """))

        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_requirement_notifications_user
            ON requirement_notifications(user_id, is_read);
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_requirement_notifications_requirement
            ON requirement_notifications(requirement_id);
        """))
        conn.commit()
        print("✅ requirement_notifications table created")

        print("\n" + "=" * 80)
        print("✅ Migration completed successfully!")
        print("=" * 80)
        print("\nCreated:")
        print("  - requirement_candidates table")
        print("  - requirement_interviews table")
        print("  - requirement_workflow_history table")
        print("  - requirement_notifications table")
        print("  - 3 new columns in deployment_requests")
        print("  - 15+ indexes for performance")


def downgrade():
    """Rollback: Drop all created tables and columns"""

    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        print("=" * 80)
        print("ROLLING BACK: Dropping Requirement Workflow Tables")
        print("⚠️  WARNING: This will DELETE all workflow data!")
        print("=" * 80)

        # Drop tables in reverse order
        conn.execute(text("DROP TABLE IF EXISTS requirement_notifications CASCADE;"))
        print("✅ Dropped requirement_notifications")

        conn.execute(text("DROP TABLE IF EXISTS requirement_workflow_history CASCADE;"))
        print("✅ Dropped requirement_workflow_history")

        conn.execute(text("DROP TABLE IF EXISTS requirement_interviews CASCADE;"))
        print("✅ Dropped requirement_interviews")

        conn.execute(text("DROP TABLE IF EXISTS requirement_candidates CASCADE;"))
        print("✅ Dropped requirement_candidates")

        # Drop index
        conn.execute(text("DROP INDEX IF EXISTS idx_deployment_requests_workflow_stage;"))

        # Remove columns from deployment_requests
        conn.execute(text("ALTER TABLE deployment_requests DROP COLUMN IF EXISTS positions_count;"))
        conn.execute(text("ALTER TABLE deployment_requests DROP COLUMN IF EXISTS filled_count;"))
        conn.execute(text("ALTER TABLE deployment_requests DROP COLUMN IF EXISTS workflow_stage;"))
        print("✅ Removed columns from deployment_requests")

        conn.commit()
        print("\n✅ Rollback completed successfully!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Run database migration')
    parser.add_argument('action', choices=['upgrade', 'downgrade'],
                       help='upgrade: apply migration, downgrade: rollback migration')

    args = parser.parse_args()

    if args.action == 'upgrade':
        upgrade()
    elif args.action == 'downgrade':
        confirm = input("⚠️  This will DELETE all workflow data. Are you sure? (yes/no): ")
        if confirm.lower() == 'yes':
            downgrade()
        else:
            print("Rollback cancelled.")
            sys.exit(0)
