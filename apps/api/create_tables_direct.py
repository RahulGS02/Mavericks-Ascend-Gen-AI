"""
Direct table creation script (alternative to Alembic)
Run with: python create_tables_direct.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import engine, Base
from app import models

print("🗄️  Creating database tables directly...")
print(f"📍 Connecting to: {engine.url}")

try:
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("\n✅ All tables created successfully!")
    
    # Print created tables
    print("\n📋 Created tables:")
    for table_name in sorted(Base.metadata.tables.keys()):
        print(f"   ✓ {table_name}")
    
    print("\n🎉 Database setup complete!")
    print("\nNext step: Run seed script")
    print("  python scripts\\seed_data.py")
    
except Exception as e:
    print(f"\n❌ Error creating tables: {e}")
    print("\nPlease check:")
    print("1. Your Supabase project is active")
    print("2. Database URL in .env is correct")
    print("3. Your internet connection")
    print("4. Firewall settings")
    sys.exit(1)
