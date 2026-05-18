"""
Cleanup database - drop all tables and types
Run with: python scripts/cleanup_db.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, text
from app.config import settings

def cleanup_database():
    """Drop all tables and enum types"""
    
    print("🧹 Cleaning up database...")
    
    # Use autocommit mode to see all tables
    engine = create_engine(settings.DATABASE_URL, isolation_level="AUTOCOMMIT")

    try:
        with engine.connect() as conn:
            # Drop all tables (query them first)
            print("   Getting all tables...")
            result = conn.execute(text("""
                SELECT tablename FROM pg_tables
                WHERE schemaname = 'public'
            """))
            tables = [row[0] for row in result]

            if tables:
                print(f"   Found {len(tables)} tables: {', '.join(tables)}")
                print("   Dropping all tables...")
                # Drop in specific order to handle foreign keys
                for table in tables:
                    try:
                        conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                    except Exception as e:
                        print(f"      Warning: Could not drop {table}: {e}")
            else:
                print("   No tables found")
            
            # Drop all enum types (get list from database first)
            print("   Getting all enum types...")
            result = conn.execute(text("""
                SELECT typname FROM pg_type
                WHERE typtype = 'e'
                AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
            """))
            enum_types = [row[0] for row in result]

            if enum_types:
                print(f"   Found {len(enum_types)} enum types: {', '.join(enum_types)}")
                print("   Dropping all enum types...")
                for enum_type in enum_types:
                    try:
                        conn.execute(text(f"DROP TYPE IF EXISTS {enum_type} CASCADE"))
                    except Exception as e:
                        print(f"      Warning: Could not drop {enum_type}: {e}")
            else:
                print("   No enum types found")

            # No need to commit in AUTOCOMMIT mode
            print("✅ Database cleaned successfully!")
            
    except Exception as e:
        print(f"❌ Error cleaning database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    response = input("⚠️  This will DELETE ALL DATA! Continue? (yes/no): ")
    if response.lower() == 'yes':
        cleanup_database()
        print("\n✅ Now run:")
        print("   alembic upgrade head")
        print("   python scripts\\seed_data.py")
    else:
        print("Cancelled.")
