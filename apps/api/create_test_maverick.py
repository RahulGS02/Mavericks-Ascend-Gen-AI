"""Create test maverick user: maverick@test.com"""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.models.maverick import Maverick, ProfileStatus, DeploymentStatus
from app.services.auth import get_password_hash

def create_test_maverick():
    db = SessionLocal()
    
    try:
        print("\n" + "="*70)
        print("🚀 CREATING TEST MAVERICK USER")
        print("="*70)
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == "maverick@test.com").first()
        
        if existing_user:
            print("\n✅ User already exists!")
            print(f"   Email: {existing_user.email}")
            print(f"   Role: {existing_user.role.value}")
            print(f"   Active: {existing_user.is_active}")
            print("\n💡 You can login with:")
            print(f"   Email: maverick@test.com")
            print(f"   Password: maverick123")
            db.close()
            return
        
        # Create User account
        print("\n1️⃣  Creating User account...")
        new_user = User(
            email="maverick@test.com",
            name="Test Maverick Student",
            password_hash=get_password_hash("maverick123"),
            role=UserRole.MAVERICK,
            is_active=True
        )
        db.add(new_user)
        db.flush()
        print(f"   ✓ User created: {new_user.email}")
        
        # Create Maverick profile
        print("\n2️⃣  Creating Maverick profile...")
        new_maverick = Maverick(
            user_id=new_user.id,
            name="Test Maverick Student",
            email="maverick@test.com",
            phone="+91-9876543210",
            college="Test University",
            degree="B.Tech",
            branch="Computer Science",
            graduation_year=2024,
            cgpa=8.5,
            skills=["Python", "JavaScript", "React", "Node.js"],
            profile_status=ProfileStatus.APPROVED,  # Pre-approved for testing
            deployment_status=DeploymentStatus.AVAILABLE
        )
        db.add(new_maverick)
        db.commit()
        print(f"   ✓ Maverick profile created: {new_maverick.name}")
        
        print("\n" + "="*70)
        print("✅ TEST MAVERICK CREATED SUCCESSFULLY!")
        print("="*70)
        print("\n📝 LOGIN CREDENTIALS:")
        print("-"*70)
        print(f"   Email:    maverick@test.com")
        print(f"   Password: maverick123")
        print(f"   Role:     MAVERICK")
        print("-"*70)
        print("\n🎉 You can now login with these credentials!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_maverick()
