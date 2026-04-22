"""
Initialize the database with tables and seed data
Run with: python scripts/init_db.py
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import engine, Base
from app.models import *  # Import all models


def init_database():
    """Create all tables in the database"""
    print("🗄️  Creating database tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Print created tables
        print("\n📋 Created tables:")
        for table_name in Base.metadata.tables.keys():
            print(f"   - {table_name}")
            
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        sys.exit(1)


def drop_all_tables():
    """Drop all tables (use with caution!)"""
    response = input("⚠️  WARNING: This will delete ALL data. Are you sure? (yes/no): ")
    if response.lower() == "yes":
        print("🗑️  Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped!")
    else:
        print("❌ Operation cancelled")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database initialization script")
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop all tables before creating (DANGEROUS!)"
    )
    
    args = parser.parse_args()
    
    if args.drop:
        drop_all_tables()
    
    init_database()
    
    print("\n🎉 Database setup complete!")
    print("\nNext steps:")
    print("1. Run: alembic revision --autogenerate -m 'Initial schema'")
    print("2. Run: alembic upgrade head")
    print("3. Run seed script to add sample data")
