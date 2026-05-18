"""Quick script to check existing users in database"""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models.user import User, UserRole

def check_users():
    db = SessionLocal()
    
    print("\n" + "="*70)
    print("🔍 CHECKING EXISTING USERS IN DATABASE")
    print("="*70)
    
    # Check all maverick users
    print("\n📋 MAVERICK USERS:")
    print("-"*70)
    mavericks = db.query(User).filter(User.role == UserRole.MAVERICK).all()
    if mavericks:
        for user in mavericks:
            print(f"  ✓ {user.email:<40} (Active: {user.is_active})")
    else:
        print("  ❌ No maverick users found!")
    
    # Check HR users
    print("\n📋 HR USERS:")
    print("-"*70)
    hr_users = db.query(User).filter(User.role == UserRole.HR).all()
    if hr_users:
        for user in hr_users:
            print(f"  ✓ {user.email:<40} (Active: {user.is_active})")
    else:
        print("  ❌ No HR users found!")
    
    # Check Trainer users
    print("\n📋 TRAINER USERS:")
    print("-"*70)
    trainers = db.query(User).filter(User.role == UserRole.TRAINER).all()
    if trainers:
        for user in trainers:
            print(f"  ✓ {user.email:<40} (Active: {user.is_active})")
    else:
        print("  ❌ No trainer users found!")
    
    # Check specific user
    print("\n🔍 CHECKING FOR maverick@test.com:")
    print("-"*70)
    test_user = db.query(User).filter(User.email == "maverick@test.com").first()
    if test_user:
        print(f"  ✅ FOUND: {test_user.email}")
        print(f"     Role: {test_user.role.value}")
        print(f"     Active: {test_user.is_active}")
        print(f"     Name: {test_user.name}")
    else:
        print("  ❌ NOT FOUND: maverick@test.com does not exist!")
        print("\n💡 SOLUTION: Use one of these emails instead:")
        if mavericks:
            print(f"     Email: {mavericks[0].email}")
            print(f"     Password: maverick123")
        else:
            print("     Run seed data script to create users!")
    
    print("\n" + "="*70)
    print("✅ CHECK COMPLETE")
    print("="*70 + "\n")
    
    db.close()

if __name__ == "__main__":
    try:
        check_users()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
