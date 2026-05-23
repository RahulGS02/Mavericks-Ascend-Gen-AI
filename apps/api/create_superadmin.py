"""
Create Super Admin User
Run this script to create a super admin account for testing
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.services.auth import get_password_hash

def create_superadmin():
    """Create super admin user"""
    db = SessionLocal()
    
    try:
        # Check if super admin already exists
        existing = db.query(User).filter(
            User.email == "admin@maverick.com"
        ).first()
        
        if existing:
            print("✅ Super Admin user already exists!")
            print(f"   Email: admin@maverick.com")
            print(f"   Password: admin123")
            print(f"   Role: {existing.role.value}")
            print(f"   Active: {existing.is_active}")
            return
        
        # Create super admin user
        admin = User(
            email="admin@maverick.com",
            password_hash=get_password_hash("admin123"),
            name="Super Admin",
            role=UserRole.SUPER_ADMIN,
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("\n" + "="*60)
        print("🎉 SUCCESS! Super Admin User Created")
        print("="*60)
        print(f"\n📧 Email:    admin@maverick.com")
        print(f"🔐 Password: admin123")
        print(f"👤 Role:     super_admin")
        print(f"✅ Status:   Active")
        print(f"\n🔗 Login URL: http://localhost:3000/login")
        print(f"🔗 Admin Dashboard: http://localhost:3000/admin/dashboard")
        print("\n" + "="*60)
        print("⚠️  IMPORTANT: Change the password after first login!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error creating super admin: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_superadmin()
