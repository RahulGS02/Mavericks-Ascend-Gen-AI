"""
Migration: Create Workflow Constraints and Enums
Description: Adds check constraints and validation rules for workflow tables
Date: 2026-05-16
"""

import sys
import os
from sqlalchemy import create_engine, text
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
    """Add constraints and validation rules"""
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("=" * 80)
        print("Starting Migration: Create Workflow Constraints")
        print("=" * 80)
        
        # 1. Workflow Stage Constraint
        print("\n[1/8] Adding workflow_stage constraint...")
        conn.execute(text("""
            ALTER TABLE deployment_requests 
            DROP CONSTRAINT IF EXISTS chk_workflow_stage;
        """))
        conn.execute(text("""
            ALTER TABLE deployment_requests 
            ADD CONSTRAINT chk_workflow_stage 
            CHECK (workflow_stage IN (
                'PENDING',
                'UNDER_REVIEW',
                'CANDIDATES_SUGGESTED',
                'INTERVIEW_SCHEDULING',
                'INTERVIEWS_IN_PROGRESS',
                'SELECTION_IN_PROGRESS',
                'AWAITING_APPROVAL',
                'APPROVED',
                'COMPLETED',
                'CLOSED'
            ));
        """))
        conn.commit()
        print("✅ Workflow stage constraint added")
        
        # 2. Candidate Status Constraint
        print("\n[2/8] Adding candidate_status constraint...")
        conn.execute(text("""
            ALTER TABLE requirement_candidates 
            DROP CONSTRAINT IF EXISTS chk_candidate_status;
        """))
        conn.execute(text("""
            ALTER TABLE requirement_candidates 
            ADD CONSTRAINT chk_candidate_status 
            CHECK (status IN (
                'SUGGESTED',
                'SHORTLISTED',
                'REJECTED',
                'INTERVIEW_SCHEDULED',
                'INTERVIEWED',
                'SELECTED',
                'APPROVED',
                'DEPLOYED',
                'ON_HOLD'
            ));
        """))
        conn.commit()
        print("✅ Candidate status constraint added")
        
        # 3. Interview Type Constraint
        print("\n[3/8] Adding interview_type constraint...")
        conn.execute(text("""
            ALTER TABLE requirement_interviews 
            DROP CONSTRAINT IF EXISTS chk_interview_type;
        """))
        conn.execute(text("""
            ALTER TABLE requirement_interviews 
            ADD CONSTRAINT chk_interview_type 
            CHECK (interview_type IN ('ONLINE', 'OFFLINE'));
        """))
        conn.commit()
        print("✅ Interview type constraint added")
        
        # 4. Interview Mode Constraint
        print("\n[4/8] Adding interview_mode constraint...")
        conn.execute(text("""
            ALTER TABLE requirement_interviews 
            DROP CONSTRAINT IF EXISTS chk_interview_mode;
        """))
        conn.execute(text("""
            ALTER TABLE requirement_interviews 
            ADD CONSTRAINT chk_interview_mode 
            CHECK (interview_mode IN (
                'VIDEO_CALL',
                'PHONE_CALL',
                'IN_PERSON',
                'PANEL_INTERVIEW',
                'TECHNICAL_ROUND',
                'HR_ROUND',
                'MANAGERIAL_ROUND'
            ));
        """))
        conn.commit()
        print("✅ Interview mode constraint added")
        
        # 5. Interview Status Constraint
        print("\n[5/8] Adding interview_status constraint...")
        conn.execute(text("""
            ALTER TABLE requirement_interviews 
            DROP CONSTRAINT IF EXISTS chk_interview_status;
        """))
        conn.execute(text("""
            ALTER TABLE requirement_interviews 
            ADD CONSTRAINT chk_interview_status 
            CHECK (status IN (
                'SCHEDULED',
                'CONFIRMED',
                'IN_PROGRESS',
                'COMPLETED',
                'CANCELLED',
                'RESCHEDULED',
                'NO_SHOW'
            ));
        """))
        conn.commit()
        print("✅ Interview status constraint added")
        
        # 6. Rating Constraints
        print("\n[6/8] Adding rating range constraints...")
        conn.execute(text("""
            ALTER TABLE requirement_interviews 
            DROP CONSTRAINT IF EXISTS chk_rating_range;
        """))
        conn.execute(text("""
            ALTER TABLE requirement_interviews 
            ADD CONSTRAINT chk_rating_range 
            CHECK (rating IS NULL OR (rating >= 1.0 AND rating <= 5.0));
        """))
        
        conn.execute(text("""
            ALTER TABLE requirement_interviews 
            DROP CONSTRAINT IF EXISTS chk_technical_rating_range;
        """))
        conn.execute(text("""
            ALTER TABLE requirement_interviews
            ADD CONSTRAINT chk_technical_rating_range
            CHECK (technical_rating IS NULL OR (technical_rating >= 1.0 AND technical_rating <= 5.0));
        """))

        conn.execute(text("""
            ALTER TABLE requirement_interviews
            DROP CONSTRAINT IF EXISTS chk_communication_rating_range;
        """))
        conn.execute(text("""
            ALTER TABLE requirement_interviews
            ADD CONSTRAINT chk_communication_rating_range
            CHECK (communication_rating IS NULL OR (communication_rating >= 1.0 AND communication_rating <= 5.0));
        """))

        conn.execute(text("""
            ALTER TABLE requirement_interviews
            DROP CONSTRAINT IF EXISTS chk_cultural_fit_rating_range;
        """))
        conn.execute(text("""
            ALTER TABLE requirement_interviews
            ADD CONSTRAINT chk_cultural_fit_rating_range
            CHECK (cultural_fit_rating IS NULL OR (cultural_fit_rating >= 1.0 AND cultural_fit_rating <= 5.0));
        """))
        conn.commit()
        print("✅ Rating constraints added")

        # 7. Match Score Constraint
        print("\n[7/8] Adding match_score constraint...")
        conn.execute(text("""
            ALTER TABLE requirement_candidates
            DROP CONSTRAINT IF EXISTS chk_match_score_range;
        """))
        conn.execute(text("""
            ALTER TABLE requirement_candidates
            ADD CONSTRAINT chk_match_score_range
            CHECK (match_score IS NULL OR (match_score >= 0 AND match_score <= 100));
        """))
        conn.commit()
        print("✅ Match score constraint added")

        # 8. Positions Count Constraints
        print("\n[8/8] Adding positions_count constraints...")
        conn.execute(text("""
            ALTER TABLE deployment_requests
            DROP CONSTRAINT IF EXISTS chk_positions_count_positive;
        """))
        conn.execute(text("""
            ALTER TABLE deployment_requests
            ADD CONSTRAINT chk_positions_count_positive
            CHECK (positions_count > 0);
        """))

        conn.execute(text("""
            ALTER TABLE deployment_requests
            DROP CONSTRAINT IF EXISTS chk_filled_count_valid;
        """))
        conn.execute(text("""
            ALTER TABLE deployment_requests
            ADD CONSTRAINT chk_filled_count_valid
            CHECK (filled_count >= 0 AND filled_count <= positions_count);
        """))
        conn.commit()
        print("✅ Positions count constraints added")

        print("\n" + "=" * 80)
        print("✅ Migration completed successfully!")
        print("=" * 80)
        print("\nAdded constraints for:")
        print("  - Workflow stages (10 valid values)")
        print("  - Candidate status (9 valid values)")
        print("  - Interview type (2 valid values)")
        print("  - Interview mode (7 valid values)")
        print("  - Interview status (7 valid values)")
        print("  - Rating ranges (1.0 - 5.0)")
        print("  - Match scores (0 - 100)")
        print("  - Positions count validation")


def downgrade():
    """Rollback: Remove all constraints"""

    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        print("=" * 80)
        print("ROLLING BACK: Removing Workflow Constraints")
        print("=" * 80)

        # Remove all constraints
        constraints = [
            ("deployment_requests", "chk_workflow_stage"),
            ("deployment_requests", "chk_positions_count_positive"),
            ("deployment_requests", "chk_filled_count_valid"),
            ("requirement_candidates", "chk_candidate_status"),
            ("requirement_candidates", "chk_match_score_range"),
            ("requirement_interviews", "chk_interview_type"),
            ("requirement_interviews", "chk_interview_mode"),
            ("requirement_interviews", "chk_interview_status"),
            ("requirement_interviews", "chk_rating_range"),
            ("requirement_interviews", "chk_technical_rating_range"),
            ("requirement_interviews", "chk_communication_rating_range"),
            ("requirement_interviews", "chk_cultural_fit_rating_range"),
        ]

        for table, constraint in constraints:
            conn.execute(text(f"""
                ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {constraint};
            """))
            print(f"✅ Dropped constraint: {constraint}")

        conn.commit()
        print("\n✅ Rollback completed successfully!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Run constraint migration')
    parser.add_argument('action', choices=['upgrade', 'downgrade'],
                       help='upgrade: apply migration, downgrade: rollback migration')

    args = parser.parse_args()

    if args.action == 'upgrade':
        upgrade()
    elif args.action == 'downgrade':
        confirm = input("⚠️  This will remove all validation constraints. Continue? (yes/no): ")
        if confirm.lower() == 'yes':
            downgrade()
        else:
            print("Rollback cancelled.")
