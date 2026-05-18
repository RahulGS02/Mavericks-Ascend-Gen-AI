"""Find user MaverickOne@mail.com and test password"""
from app.database import SessionLocal
from app.models.user import User
from app.models.maverick import Maverick
from app.services.auth import verify_password

db = SessionLocal()

email = "MaverickOne@mail.com"
test_password = "MaverickOne@1"

print("=" * 80)
print(f"SEARCHING FOR USER: {email}")
print("=" * 80)

# Search exact match
print("\n1️⃣  Searching with exact match...")
user = db.query(User).filter(User.email == email).first()
if user:
    print(f"✅ FOUND (exact match)")
    print(f"   Email in DB: {user.email}")
else:
    print(f"❌ NOT FOUND (exact match)")

# Search case-insensitive
print("\n2️⃣  Searching with case-insensitive (ILIKE)...")
user = db.query(User).filter(User.email.ilike(email)).first()
if user:
    print(f"✅ FOUND (case-insensitive)")
    print(f"   Email in DB: {user.email}")
    print(f"   Name: {user.name}")
    print(f"   Role: {user.role.value}")
    print(f"   Active: {user.is_active}")
    print(f"   Created: {user.created_at}")
    
    # Check maverick profile
    mav = db.query(Maverick).filter(Maverick.user_id == user.id).first()
    if mav:
        print(f"\n   📋 Maverick Profile:")
        print(f"      Profile Status: {mav.profile_status}")
        print(f"      Deployment Status: {mav.deployment_status}")
        print(f"      Phone: {mav.phone}")
        print(f"      College: {mav.college}")
    
    # Test password
    print(f"\n3️⃣  Testing password '{test_password}'...")
    print(f"   Password hash: {user.password_hash[:60]}...")
    
    if verify_password(test_password, user.password_hash):
        print(f"   ✅ PASSWORD MATCHES!")
        print(f"\n   🎉 User can login with:")
        print(f"      Email: {user.email}")
        print(f"      Password: {test_password}")
    else:
        print(f"   ❌ PASSWORD DOES NOT MATCH")
        print(f"\n   ⚠️  The password stored is different from '{test_password}'")
        print(f"\n   💡 Possible reasons:")
        print(f"      1. User changed password after registration")
        print(f"      2. Registration used different password")
        print(f"      3. Password was hashed incorrectly")
        
        # Try common test passwords
        print(f"\n   🔍 Testing common passwords...")
        test_passwords = ["password123", "maverick123", "mav123", "test123", "MaverickOne@1"]
        for pwd in test_passwords:
            if verify_password(pwd, user.password_hash):
                print(f"      ✅ FOUND: '{pwd}' works!")
                break
        else:
            print(f"      ❌ None of the common passwords work")
else:
    print(f"❌ NOT FOUND (case-insensitive)")
    
    # Search for similar emails
    print(f"\n4️⃣  Searching for similar emails...")
    similar = db.query(User).filter(User.email.ilike('%maverick%')).filter(User.email.ilike('%mail%')).all()
    if similar:
        print(f"   Found {len(similar)} users with 'maverick' and 'mail':")
        for u in similar:
            print(f"      - {u.email} ({u.name})")
    else:
        print(f"   No similar emails found")
    
    # Show recent mavericks
    print(f"\n5️⃣  Recent maverick registrations:")
    recent = db.query(User).filter(User.role == 'maverick').order_by(User.created_at.desc()).limit(5).all()
    if recent:
        for u in recent:
            print(f"      - {u.email} ({u.name}) - {u.created_at}")
    else:
        print(f"   No mavericks found")

db.close()

print("\n" + "=" * 80)
print("SEARCH COMPLETE")
print("=" * 80)
