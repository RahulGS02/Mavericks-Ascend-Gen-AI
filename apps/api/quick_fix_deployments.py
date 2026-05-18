"""
Quick fix for old deployment requests - no confirmation needed
This will UPDATE old records with default values instead of deleting them
"""
import sys
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

def fix_old_deployments():
    """Update old deployment requests with default values"""
    
    print("=" * 60)
    print("  QUICK FIX FOR OLD DEPLOYMENT REQUESTS")
    print("=" * 60)
    print("\n🔍 Connecting to database...")
    
    # Get database URL
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ Error: DATABASE_URL not found!")
        sys.exit(1)
    
    # Create engine and connection
    engine = create_engine(database_url)
    
    try:
        with engine.connect() as conn:
            # Check how many old records exist
            count_result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM deployment_requests 
                WHERE role_title IS NULL
            """))
            old_count = count_result.scalar()
            
            print(f"\n📊 Found {old_count} old deployment request(s) without role_title")
            
            if old_count == 0:
                print("✅ No old records found. Database is clean!")
                return
            
            # Update old records with default values
            print(f"\n🔧 Updating {old_count} old record(s) with default values...")
            
            update_result = conn.execute(text("""
                UPDATE deployment_requests 
                SET 
                    role_title = COALESCE(project_name, 'Legacy Deployment Request'),
                    required_skills = '[]',
                    preferred_skills = '[]',
                    role_description = COALESCE(
                        'Project: ' || project_name, 
                        'Legacy deployment request migrated from old system'
                    )
                WHERE role_title IS NULL
            """))
            
            conn.commit()
            
            updated_count = update_result.rowcount
            print(f"✅ Successfully updated {updated_count} record(s)!")
            
            # Verify the fix
            verify_result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM deployment_requests 
                WHERE role_title IS NULL
            """))
            remaining = verify_result.scalar()
            
            if remaining == 0:
                print("✅ Verification: All records now have role_title!")
            else:
                print(f"⚠️  Warning: {remaining} record(s) still missing role_title")
            
            # Show the updated records
            print("\n📋 Updated records:")
            show_result = conn.execute(text("""
                SELECT id, role_title, maverick_id, status, created_at
                FROM deployment_requests
                ORDER BY created_at DESC
                LIMIT 5
            """))
            
            for row in show_result:
                maverick_status = "No maverick" if row[2] is None else f"Maverick: {row[2]}"
                print(f"   - {row[1]} | {maverick_status} | Status: {row[3]}")
            
            # Show total count
            total_result = conn.execute(text("""
                SELECT COUNT(*) FROM deployment_requests
            """))
            total = total_result.scalar()
            print(f"\n📊 Total deployment requests: {total}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        engine.dispose()
    
    print("\n" + "=" * 60)
    print("✅ FIX COMPLETE!")
    print("=" * 60)
    print("\n🎯 Next steps:")
    print("   1. Restart the backend server (Ctrl+C and restart)")
    print("   2. Refresh http://localhost:3000/deployments")
    print("   3. The 500 error should be GONE!")
    print("   4. Create your first requirement card! 🚀\n")

if __name__ == "__main__":
    try:
        fix_old_deployments()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Failed: {e}")
        sys.exit(1)
