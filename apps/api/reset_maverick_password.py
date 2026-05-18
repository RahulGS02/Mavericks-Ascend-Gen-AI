"""Reset password for MaverickOne@mail.com"""
from app.database import SessionLocal
from app.models.user import User
from app.services.auth import get_password_hash
import sys

db = SessionLocal()

# Search for user (case-insensitive)
email_variations = [
    "MaverickOne@mail.com",
    "maverickone@mail.com", 
    "MAVERICKONE@MAIL.COM"
]

user = None
for email in email_variations:
    user = db.query(User).filter(User.email.ilike(email)).first()
    if user:
        print(f"Found user with email: {user.email}")
        break

if not user:
    print("ERROR: User not found with any variation of MaverickOne@mail.com")
    print("\nSearching for similar emails...")
    similar = db.query(User).filter(User.email.ilike('%maverick%')).all()
    if similar:
        print("Found these users:")
        for u in similar:
            print(f"  - {u.email}")
    sys.exit(1)

# Reset password
new_password = "MaverickOne@1"
user.password_hash = get_password_hash(new_password)
db.commit()

print(f"\n✅ Password reset successful!")
print(f"\nLogin credentials:")
print(f"  Email: {user.email}")
print(f"  Password: {new_password}")
print(f"\nYou can now login with these credentials.")

db.close()
