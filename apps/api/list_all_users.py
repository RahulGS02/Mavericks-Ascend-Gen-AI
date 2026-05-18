"""List all users in database"""
from app.database import SessionLocal
from app.models.user import User
from app.models.maverick import Maverick

db = SessionLocal()

print("=" * 80)
print("ALL USERS IN DATABASE")
print("=" * 80)

# Get all users
users = db.query(User).order_by(User.created_at.desc()).all()

print(f"\nTotal users: {len(users)}\n")

for i, user in enumerate(users, 1):
    print(f"{i}. {user.email}")
    print(f"   Name: {user.name}")
    print(f"   Role: {user.role.value}")
    print(f"   Active: {user.is_active}")
    print(f"   Created: {user.created_at}")
    
    # Check if maverick
    if user.role.value == 'maverick':
        mav = db.query(Maverick).filter(Maverick.user_id == user.id).first()
        if mav:
            print(f"   Maverick Profile: ✅ (ID: {mav.id})")
            print(f"   Profile Status: {mav.profile_status}")
        else:
            print(f"   Maverick Profile: ❌ MISSING")
    print()

db.close()

print("=" * 80)
