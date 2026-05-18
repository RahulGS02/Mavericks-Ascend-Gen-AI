"""
Quick script to check HR dashboard data and verify database has records
"""
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Database connection
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/maverick_insights"

def check_data():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("=" * 60)
    print("HR DASHBOARD DATA CHECK")
    print("=" * 60)
    print()
    
    try:
        # Check mavericks
        result = session.execute(text("SELECT COUNT(*) FROM mavericks"))
        total_mavericks = result.scalar()
        print(f"✓ Total Mavericks: {total_mavericks}")
        
        # Check pending
        result = session.execute(text("SELECT COUNT(*) FROM mavericks WHERE profile_status = 'pending'"))
        pending = result.scalar()
        print(f"  - Pending Profiles: {pending}")
        
        # Check approved
        result = session.execute(text("SELECT COUNT(*) FROM mavericks WHERE profile_status = 'approved'"))
        approved = result.scalar()
        print(f"  - Approved: {approved}")
        
        # Check unassigned
        result = session.execute(text("SELECT COUNT(*) FROM mavericks WHERE profile_status = 'approved' AND current_batch_id IS NULL"))
        unassigned = result.scalar()
        print(f"  - Unassigned (approved but no batch): {unassigned}")
        
        # Check deployed
        result = session.execute(text("SELECT COUNT(*) FROM mavericks WHERE deployment_status = 'deployed'"))
        deployed = result.scalar()
        print(f"  - Deployed: {deployed}")
        
        print()
        
        # Check batches
        result = session.execute(text("SELECT COUNT(*) FROM batches"))
        total_batches = result.scalar()
        print(f"✓ Total Batches: {total_batches}")
        
        # Check active batches
        result = session.execute(text("SELECT COUNT(*) FROM batches WHERE status = 'active'"))
        active_batches = result.scalar()
        print(f"  - Active Batches: {active_batches}")
        
        print()
        
        # Check assessments
        result = session.execute(text("SELECT COUNT(*) FROM assessment_attempts"))
        total_attempts = result.scalar()
        print(f"✓ Total Assessment Attempts: {total_attempts}")
        
        if total_attempts > 0:
            result = session.execute(text("SELECT COUNT(*) FROM assessment_attempts WHERE passed = true"))
            passed = result.scalar()
            success_rate = (passed / total_attempts * 100) if total_attempts > 0 else 0
            print(f"  - Passed: {passed}")
            print(f"  - Success Rate: {success_rate:.1f}%")
        
        print()
        
        # Check deployment requests
        result = session.execute(text("SELECT COUNT(*) FROM deployment_requests"))
        total_requests = result.scalar()
        print(f"✓ Total Deployment Requests: {total_requests}")
        
        if total_requests > 0:
            result = session.execute(text("SELECT COUNT(*) FROM deployment_requests WHERE status = 'pending'"))
            pending_requests = result.scalar()
            print(f"  - Pending Requests: {pending_requests}")
        
        print()
        
        # Check trainer feedback
        result = session.execute(text("SELECT COUNT(*) FROM trainer_feedback"))
        total_feedback = result.scalar()
        print(f"✓ Total Trainer Feedback: {total_feedback}")
        
        print()
        print("=" * 60)
        
        # Check if we need seed data
        if total_mavericks == 0:
            print("⚠️  WARNING: No data found in database!")
            print("   Run: python seed_data.py")
        elif pending == 0 and approved == 0:
            print("⚠️  WARNING: No approved or pending mavericks!")
        else:
            print("✓ Database has data - dashboard should work!")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error checking data: {e}")
        print()
        print("Make sure:")
        print("1. PostgreSQL is running")
        print("2. Database 'maverick_insights' exists")
        print("3. Migrations have been run: alembic upgrade head")
    finally:
        session.close()

if __name__ == "__main__":
    check_data()
