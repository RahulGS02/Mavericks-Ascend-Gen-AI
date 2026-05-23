"""
Fix: Rename 'metadata' column to 'notification_metadata' in requirement_notifications table

This migration fixes the mismatch between:
- Model: uses 'notification_metadata'
- Database: has 'metadata'

Run with: python migrations_python/fix_notification_metadata_column.py
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from app.database import engine

def fix_notification_metadata():
    """Rename metadata column to notification_metadata"""
    print("=" * 80)
    print("FIX: Rename 'metadata' to 'notification_metadata'")
    print("=" * 80)
    
    with engine.connect() as conn:
        try:
            # Check if the old column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'requirement_notifications' 
                AND column_name = 'metadata';
            """))
            
            if result.rowcount == 0:
                print("\n❌ Column 'metadata' not found.")
                print("✅ Checking if 'notification_metadata' already exists...")
                
                result2 = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'requirement_notifications' 
                    AND column_name = 'notification_metadata';
                """))
                
                if result2.rowcount > 0:
                    print("✅ Column 'notification_metadata' already exists. No migration needed!")
                else:
                    print("⚠️ Neither 'metadata' nor 'notification_metadata' found!")
                    print("   Creating 'notification_metadata' column...")
                    
                    conn.execute(text("""
                        ALTER TABLE requirement_notifications 
                        ADD COLUMN notification_metadata JSONB DEFAULT '{}';
                    """))
                    conn.commit()
                    print("✅ Column 'notification_metadata' created successfully!")
                
                return
            
            print("\n✅ Found column 'metadata' in requirement_notifications table")
            print("🔄 Renaming to 'notification_metadata'...")
            
            # Rename the column
            conn.execute(text("""
                ALTER TABLE requirement_notifications 
                RENAME COLUMN metadata TO notification_metadata;
            """))
            
            conn.commit()
            
            print("✅ Successfully renamed 'metadata' to 'notification_metadata'!")
            
            # Verify the change
            result = conn.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'requirement_notifications' 
                AND column_name = 'notification_metadata';
            """))
            
            row = result.fetchone()
            if row:
                print(f"✅ Verified: Column 'notification_metadata' exists (type: {row[1]})")
            
            print("\n" + "=" * 80)
            print("✅ MIGRATION COMPLETE!")
            print("=" * 80)
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    fix_notification_metadata()
