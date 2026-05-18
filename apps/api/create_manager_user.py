"""
Script to create a manager test user
Run this to add manager@maverick.com / manager123
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models.user import User, UserRole
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_manager():
    db = SessionLocal()
    
    try:
        # Check if manager already exists
        existing = db.query(User).filter(User.email == "manager@maverick.com").first()
        
        if existing:
            print("✅ Manager user already exists!")
            print(f"   Email: manager@maverick.com")
            print(f"   Password: manager123")
            print(f"   Role: {existing.role.value}")
            return
        
        # Create manager user
        manager = User(
            email="manager@maverick.com",
            password_hash=pwd_context.hash("manager123"),
            name="Test Manager",
            role=UserRole.MANAGER,
            is_active=True
        )
        
        db.add(manager)
        db.commit()
        
        print("✅ Manager user created successfully!")
        print("")
        print("=" * 50)
        print("MANAGER LOGIN CREDENTIALS")
        print("=" * 50)
        print("Email: manager@maverick.com")
        print("Password: manager123")
        print("Role: MANAGER")
        print("=" * 50)
        print("")
        print("You can now login at: http://localhost:3000/login")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_manager()
