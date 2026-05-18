"""Check if MaverickOne@mail.com user exists"""
import sys
from app.database import SessionLocal
from app.models.user import User
from app.models.maverick import Maverick

db = SessionLocal()

print("=" * 70)
print("CHECKING FOR MaverickOne@mail.com")
print("=" * 70)

# Check exact match
user = db.query(User).filter(User.email == 'MaverickOne@mail.com').first()
if user:
    print(f"\n✅ FOUND (exact match):")
    print(f"   Email: {user.email}")
    print(f"   Name: {user.name}")
    print(f"   Role: {user.role.value}")
    print(f"   Active: {user.is_active}")
    print(f"   Created: {user.created_at}")
    print(f"   Password hash: {user.password_hash[:50]}...")
    
    # Check maverick profile
    mav = db.query(Maverick).filter(Maverick.user_id == user.id).first()
    if mav:
        print(f"\n   Maverick Profile:")
        print(f"   - Phone: {mav.phone}")
        print(f"   - College: {mav.college}")
        print(f"   - Status: {mav.profile_status}")
else:
    print(f"\n❌ NOT FOUND (exact match)")

# Check case-insensitive
user2 = db.query(User).filter(User.email.ilike('MaverickOne@mail.com')).first()
if user2 and not user:
    print(f"\n✅ FOUND (case-insensitive):")
    print(f"   Email: {user2.email}")
    print(f"   ⚠️  Email case mismatch! User registered with different case.")
elif not user2:
    print(f"\n❌ NOT FOUND (case-insensitive either)")

# Show recent maverick registrations
print("\n" + "=" * 70)
print("RECENT MAVERICK REGISTRATIONS (last 5):")
print("=" * 70)

recent = db.query(User).filter(User.role == 'maverick').order_by(User.created_at.desc()).limit(5).all()
if recent:
    for u in recent:
        print(f"\n  Email: {u.email}")
        print(f"  Name: {u.name}")
        print(f"  Created: {u.created_at}")
        print(f"  Active: {u.is_active}")
else:
    print("\n  No recent mavericks found")

# Check for similar emails
print("\n" + "=" * 70)
print("EMAILS CONTAINING 'maverick':")
print("=" * 70)

similar = db.query(User).filter(User.email.ilike('%maverick%')).all()
if similar:
    for u in similar:
        print(f"\n  {u.email} - {u.name} ({u.role.value})")
else:
    print("\n  No emails containing 'maverick'")

db.close()

print("\n" + "=" * 70)
print("CHECK COMPLETE")
print("=" * 70)
