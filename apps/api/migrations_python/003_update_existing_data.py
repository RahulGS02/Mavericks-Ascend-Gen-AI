"""
Migration: Update Existing Deployment Requests
Description: Sets default values for new columns in existing records
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
    """Update existing records with default values"""
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("=" * 80)
        print("Starting Migration: Update Existing Data")
        print("=" * 80)
        
        # 1. Set default positions_count
        print("\n[1/4] Setting default positions_count...")
        result = conn.execute(text("""
            UPDATE deployment_requests
            SET positions_count = 1
            WHERE positions_count IS NULL;
        """))
        conn.commit()
        print(f"✅ Updated {result.rowcount} records")
        
        # 2. Set default filled_count
        print("\n[2/4] Setting default filled_count...")
        result = conn.execute(text("""
            UPDATE deployment_requests
            SET filled_count = 0
            WHERE filled_count IS NULL;
        """))
        conn.commit()
        print(f"✅ Updated {result.rowcount} records")
        
        # 3. Set workflow_stage based on current status
        print("\n[3/4] Setting workflow_stage based on current status...")
        result = conn.execute(text("""
            UPDATE deployment_requests
            SET workflow_stage = CASE 
                WHEN status = 'PENDING' THEN 'PENDING'
                WHEN status = 'APPROVED' THEN 'APPROVED'
                WHEN status = 'REJECTED' THEN 'CLOSED'
                ELSE 'PENDING'
            END
            WHERE workflow_stage IS NULL OR workflow_stage = 'PENDING';
        """))
        conn.commit()
        print(f"✅ Updated {result.rowcount} records")
        
        # 4. Count filled positions for APPROVED requests
        print("\n[4/4] Counting filled positions for approved requests...")
        result = conn.execute(text("""
            UPDATE deployment_requests dr
            SET filled_count = (
                SELECT COUNT(*)
                FROM deployments d
                WHERE d.maverick_id IN (
                    SELECT maverick_id 
                    FROM deployment_requests dr2 
                    WHERE dr2.id = dr.id 
                    AND dr2.maverick_id IS NOT NULL
                )
                AND d.status = 'ACTIVE'
            )
            WHERE dr.status = 'APPROVED' 
            AND dr.maverick_id IS NOT NULL;
        """))
        conn.commit()
        print(f"✅ Updated {result.rowcount} records")
        
        # Get summary
        result = conn.execute(text("""
            SELECT COUNT(*) as total FROM deployment_requests;
        """))
        total = result.fetchone()[0]
        
        print("\n" + "=" * 80)
        print("✅ Migration completed successfully!")
        print("=" * 80)
        print(f"\nUpdated {total} total deployment requests with:")
        print("  - Default positions_count (1)")
        print("  - Default filled_count (0)")
        print("  - Workflow_stage based on status")
        print("  - Actual filled_count for approved requests")


def downgrade():
    """Rollback: Reset new columns to NULL"""
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("=" * 80)
        print("ROLLING BACK: Resetting Data Updates")
        print("=" * 80)
        
        # Reset columns (optional - usually not needed)
        print("\nResetting workflow columns to defaults...")
        conn.execute(text("""
            UPDATE deployment_requests
            SET positions_count = 1,
                filled_count = 0,
                workflow_stage = 'PENDING';
        """))
        conn.commit()
        
        print("✅ Rollback completed!")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Update existing deployment requests')
    parser.add_argument('action', choices=['upgrade', 'downgrade'], 
                       help='upgrade: update data, downgrade: reset data')
    
    args = parser.parse_args()
    
    if args.action == 'upgrade':
        upgrade()
    elif args.action == 'downgrade':
        confirm = input("⚠️  This will reset workflow columns. Continue? (yes/no): ")
        if confirm.lower() == 'yes':
            downgrade()
        else:
            print("Rollback cancelled.")
