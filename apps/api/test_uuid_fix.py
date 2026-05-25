"""
Quick test to verify UUID → GUID migration works with SQLite
"""
import sys
import os

# Set testing mode
os.environ["TESTING"] = "true"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.models.maverick import Maverick
from app.database import Base

print("=" * 70)
print("🧪 Testing UUID → GUID Migration")
print("=" * 70)

# Create in-memory SQLite database
print("\n1️⃣ Creating SQLite in-memory database...")
engine = create_engine("sqlite:///:memory:", echo=False)

# Try to create tables
print("2️⃣ Creating tables with GUID columns...")
try:
    Base.metadata.create_all(bind=engine)
    print("   ✅ SUCCESS! Tables created without errors")
    
    # List created tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\n3️⃣ Created {len(tables)} tables:")
    for table in sorted(tables):
        print(f"   ✅ {table}")
    
    # Test inserting a user
    print("\n4️⃣ Testing user insertion...")
    Session = sessionmaker(bind=engine)
    session = Session()
    
    from app.models.user import UserRole
    import uuid
    
    test_user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        password_hash="test_hash",
        name="Test User",
        role=UserRole.HR,
        is_active=True
    )
    
    session.add(test_user)
    session.commit()
    print(f"   ✅ User created: {test_user.email}")
    
    # Retrieve user
    retrieved = session.query(User).filter_by(email="test@example.com").first()
    print(f"   ✅ User retrieved: {retrieved.name}")
    print(f"   ✅ ID type: {type(retrieved.id)}")
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED! UUID → GUID migration successful")
    print("=" * 70)
    print("\n💡 You can now run integration tests:")
    print("   pytest tests/test_talent_search_api.py -v")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\n" + "=" * 70)
    print("⚠️ GUID migration incomplete - see error above")
    print("=" * 70)
    import traceback
    traceback.print_exc()
    sys.exit(1)
