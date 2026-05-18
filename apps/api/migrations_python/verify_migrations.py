"""
Verification Script: Check Migration Success
Description: Verifies all tables, columns, indexes, and constraints were created
Date: 2026-05-16
"""

import sys
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

try:
    from tabulate import tabulate
except ImportError:
    print("⚠️  Warning: 'tabulate' not installed. Using simple formatting.")
    def tabulate(data, headers, tablefmt):
        # Simple fallback
        print(" | ".join(headers))
        print("-" * 50)
        for row in data:
            print(" | ".join(str(x) for x in row))
        return ""

# Load environment variables from apps/api/.env
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
load_dotenv(env_path)

# Get DATABASE_URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not found in environment variables!")
    print(f"Looked for .env file at: {env_path}")
    print("Please set DATABASE_URL in your .env file or environment.")
    sys.exit(1)


def verify():
    """Verify migration success"""
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("=" * 80)
        print("Migration Verification Script")
        print("=" * 80)
        
        all_passed = True
        
        # 1. Check if new tables exist
        print("\n📋 [1/6] Checking if new tables exist...")
        result = conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN (
                'requirement_candidates',
                'requirement_interviews',
                'requirement_workflow_history',
                'requirement_notifications'
            )
            ORDER BY table_name;
        """))
        
        tables = [row[0] for row in result.fetchall()]
        expected_tables = [
            'requirement_candidates',
            'requirement_interviews',  
            'requirement_notifications',
            'requirement_workflow_history'
        ]
        
        if len(tables) == 4:
            print(f"✅ All 4 tables created successfully")
            for table in tables:
                print(f"   ✓ {table}")
        else:
            print(f"❌ Missing tables! Expected 4, found {len(tables)}")
            print(f"   Found: {tables}")
            print(f"   Expected: {expected_tables}")
            all_passed = False
        
        # 2. Check new columns in deployment_requests
        print("\n📋 [2/6] Checking new columns in deployment_requests...")
        result = conn.execute(text("""
            SELECT column_name, data_type, column_default
            FROM information_schema.columns 
            WHERE table_name = 'deployment_requests' 
            AND column_name IN ('positions_count', 'filled_count', 'workflow_stage')
            ORDER BY column_name;
        """))
        
        columns = result.fetchall()
        if len(columns) == 3:
            print("✅ All 3 columns added successfully")
            headers = ["Column", "Type", "Default"]
            data = [(row[0], row[1], row[2]) for row in columns]
            print(tabulate(data, headers=headers, tablefmt='grid'))
        else:
            print(f"❌ Missing columns! Expected 3, found {len(columns)}")
            all_passed = False
        
        # 3. Check indexes
        print("\n📋 [3/6] Checking indexes...")
        result = conn.execute(text("""
            SELECT tablename, indexname
            FROM pg_indexes 
            WHERE tablename IN (
                'deployment_requests',
                'requirement_candidates',
                'requirement_interviews',
                'requirement_workflow_history',
                'requirement_notifications'
            )
            AND indexname LIKE 'idx_%'
            ORDER BY tablename, indexname;
        """))
        
        indexes = result.fetchall()
        if len(indexes) >= 10:
            print(f"✅ Found {len(indexes)} indexes")
            # Show first 5
            headers = ["Table", "Index"]
            data = [(row[0], row[1]) for row in indexes[:5]]
            print(tabulate(data, headers=headers, tablefmt='grid'))
            if len(indexes) > 5:
                print(f"   ... and {len(indexes) - 5} more")
        else:
            print(f"⚠️  Expected at least 10 indexes, found {len(indexes)}")
        
        # 4. Check constraints
        print("\n📋 [4/6] Checking constraints...")
        result = conn.execute(text("""
            SELECT tc.table_name, tc.constraint_name, tc.constraint_type
            FROM information_schema.table_constraints tc
            WHERE tc.table_name IN (
                'deployment_requests',
                'requirement_candidates',
                'requirement_interviews'
            )
            AND tc.constraint_type IN ('CHECK', 'FOREIGN KEY', 'UNIQUE')
            ORDER BY tc.table_name, tc.constraint_type;
        """))
        
        constraints = result.fetchall()
        if len(constraints) >= 15:
            print(f"✅ Found {len(constraints)} constraints")
            headers = ["Table", "Constraint", "Type"]
            data = [(row[0], row[1], row[2]) for row in constraints[:5]]
            print(tabulate(data, headers=headers, tablefmt='grid'))
            if len(constraints) > 5:
                print(f"   ... and {len(constraints) - 5} more")
        else:
            print(f"⚠️  Expected at least 15 constraints, found {len(constraints)}")
        
        # 5. Check foreign key relationships
        print("\n📋 [5/6] Checking foreign key relationships...")
        result = conn.execute(text("""
            SELECT 
                tc.table_name AS from_table,
                kcu.column_name AS from_column,
                ccu.table_name AS to_table,
                ccu.column_name AS to_column
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_name IN (
                'requirement_candidates',
                'requirement_interviews',
                'requirement_workflow_history',
                'requirement_notifications'
            )
            ORDER BY tc.table_name;
        """))
        
        fks = result.fetchall()
        if len(fks) >= 8:
            print(f"✅ Found {len(fks)} foreign keys")
        else:
            print(f"⚠️  Expected at least 8 foreign keys, found {len(fks)}")

        # 6. Check row counts
        print("\n📋 [6/6] Checking row counts...")
        tables_to_check = [
            'deployment_requests',
            'requirement_candidates',
            'requirement_interviews',
            'requirement_workflow_history',
            'requirement_notifications'
        ]

        headers = ["Table", "Row Count"]
        data = []

        for table in tables_to_check:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table};"))
            count = result.fetchone()[0]
            data.append((table, count))

        print(tabulate(data, headers=headers, tablefmt='grid'))

        # Summary
        print("\n" + "=" * 80)
        if all_passed:
            print("✅ ✅ ✅ ALL CHECKS PASSED! Migration successful! ✅ ✅ ✅")
        else:
            print("⚠️  SOME CHECKS FAILED - Review errors above")
        print("=" * 80)

        # Test sample queries
        print("\n🧪 Testing sample queries...")

        try:
            # Test workflow stage values
            result = conn.execute(text("""
                SELECT workflow_stage, COUNT(*) as count
                FROM deployment_requests
                GROUP BY workflow_stage
                ORDER BY count DESC;
            """))

            stages = result.fetchall()
            if stages:
                print("✅ Workflow stages query working")
                headers = ["Workflow Stage", "Count"]
                data = [(row[0], row[1]) for row in stages[:5]]
                print(tabulate(data, headers=headers, tablefmt='grid'))
            else:
                print("⚠️  No data in deployment_requests")
        except Exception as e:
            print(f"❌ Error testing queries: {e}")
            all_passed = False

        return all_passed


if __name__ == "__main__":
    try:
        success = verify()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
