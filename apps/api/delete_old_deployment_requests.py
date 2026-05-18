"""
Delete old deployment requests that don't have role_title
Run this script to clean up old data before the migration
"""
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables from .env file in apps/api folder
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

def delete_old_deployment_requests():
    """Delete deployment requests that don't have role_title (created before migration)"""

    print("🔍 Connecting to database...")

    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')

    if not database_url:
        print("❌ Error: DATABASE_URL not found in environment variables!")
        print("   Make sure you have a .env file in the project root with DATABASE_URL")
        sys.exit(1)

    print(f"   Database: {database_url.split('@')[1] if '@' in database_url else 'localhost'}")

    # Create engine
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # First, check how many old records exist
        count_query = text("""
            SELECT COUNT(*) 
            FROM deployment_requests 
            WHERE role_title IS NULL
        """)
        
        result = session.execute(count_query)
        old_count = result.scalar()
        
        print(f"\n📊 Found {old_count} old deployment request(s) without role_title")
        
        if old_count == 0:
            print("✅ No old records to delete. Database is clean!")
            return
        
        # Show the old records
        print("\n📋 Old records to be deleted:")
        list_query = text("""
            SELECT id, project_name, status, created_at
            FROM deployment_requests 
            WHERE role_title IS NULL
            ORDER BY created_at DESC
        """)
        
        old_records = session.execute(list_query).fetchall()
        for record in old_records:
            print(f"   - ID: {record[0]}, Project: {record[1] or 'N/A'}, Status: {record[2]}, Created: {record[3]}")
        
        # Ask for confirmation
        print(f"\n⚠️  WARNING: This will DELETE {old_count} old deployment request(s)!")
        confirmation = input("Type 'yes' to confirm deletion: ")
        
        if confirmation.lower() != 'yes':
            print("❌ Deletion cancelled. No changes made.")
            return
        
        # Delete old records
        delete_query = text("""
            DELETE FROM deployment_requests 
            WHERE role_title IS NULL
        """)
        
        result = session.execute(delete_query)
        session.commit()
        
        deleted_count = result.rowcount
        print(f"\n✅ Successfully deleted {deleted_count} old deployment request(s)!")
        
        # Verify deletion
        verify_query = text("""
            SELECT COUNT(*) 
            FROM deployment_requests 
            WHERE role_title IS NULL
        """)
        
        verify_result = session.execute(verify_query)
        remaining = verify_result.scalar()
        
        if remaining == 0:
            print("✅ Verification: All old records have been removed!")
        else:
            print(f"⚠️  Warning: {remaining} old record(s) still remain")
        
        # Show total remaining records
        total_query = text("SELECT COUNT(*) FROM deployment_requests")
        total_result = session.execute(total_query)
        total = total_result.scalar()
        print(f"\n📊 Total deployment requests in database: {total}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        session.rollback()
        raise
    finally:
        session.close()
        engine.dispose()
        print("\n🔌 Database connection closed")

if __name__ == "__main__":
    print("=" * 60)
    print("  DELETE OLD DEPLOYMENT REQUESTS")
    print("  (Records created before role_title migration)")
    print("=" * 60)
    
    try:
        delete_old_deployment_requests()
        print("\n" + "=" * 60)
        print("✅ CLEANUP COMPLETE!")
        print("=" * 60)
        print("\n🎯 Next steps:")
        print("   1. Refresh your frontend at http://localhost:3000/deployments")
        print("   2. The 500 error should be gone!")
        print("   3. Click 'Create Requirement Card' to create your first card")
        print("\n🚀 Ready to go!\n")
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Failed to delete old records: {e}")
        sys.exit(1)
