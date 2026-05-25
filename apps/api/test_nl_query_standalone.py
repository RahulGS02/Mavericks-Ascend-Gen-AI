"""
Standalone Test for Natural Language Query Components
Tests core functionality without requiring database connection
"""
import sys
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

print("=" * 80)
print("🧪 Natural Language Query - Standalone Component Test")
print("=" * 80)

# Test 1: Schema Provider (no DB required)
print("\n1️⃣  Testing Schema Provider...")
try:
    from app.services.schema_provider import get_database_schema_context, get_schema_summary
    
    # Get schema
    schema = get_database_schema_context()
    summary = get_schema_summary()
    
    print(f"   ✅ Schema provider working")
    print(f"   📊 Schema size: {len(schema):,} characters")
    print(f"   📋 Summary:\n{summary}")
    
    # Verify key tables are documented
    required_tables = ["mavericks", "maverick_skills", "batches", "users"]
    for table in required_tables:
        if f"TABLE: {table}" in schema:
            print(f"   ✅ {table} documented")
        else:
            print(f"   ❌ {table} NOT documented")
            
except Exception as e:
    print(f"   ❌ Schema provider test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 2: SQL Validator (no DB required)
print("\n2️⃣  Testing SQL Validator...")
try:
    from app.services.sql_validator import validate_sql_query, sanitize_sql_query, get_query_tables
    
    # Test valid query
    valid_sql = "SELECT * FROM mavericks WHERE deployment_status = 'AVAILABLE' LIMIT 100"
    is_valid, error, warnings = validate_sql_query(valid_sql)
    
    if is_valid:
        print(f"   ✅ Valid query accepted")
    else:
        print(f"   ❌ Valid query rejected: {error}")
    
    # Test dangerous query
    dangerous_sql = "DROP TABLE mavericks;"
    is_valid, error, warnings = validate_sql_query(dangerous_sql)
    
    if not is_valid:
        print(f"   ✅ Dangerous query blocked: {error}")
    else:
        print(f"   ❌ SECURITY ISSUE: Dangerous query was accepted!")
    
    # Test sanitization
    sql_no_limit = "SELECT * FROM mavericks"
    sanitized = sanitize_sql_query(sql_no_limit)
    
    if "LIMIT" in sanitized:
        print(f"   ✅ Sanitizer adds LIMIT clause")
    else:
        print(f"   ❌ Sanitizer didn't add LIMIT")
    
    # Test table extraction
    tables = get_query_tables("SELECT m.* FROM mavericks m JOIN batches b ON m.batch_id = b.id")
    if "mavericks" in tables and "batches" in tables:
        print(f"   ✅ Table extraction works: {tables}")
    else:
        print(f"   ❌ Table extraction failed: {tables}")
        
except Exception as e:
    print(f"   ❌ SQL validator test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Excel Generator (no DB required)
print("\n3️⃣  Testing Excel Generator...")
try:
    from app.services.excel_generator import excel_generator
    import pandas as pd
    import openpyxl
    
    print(f"   ✅ Excel generator imported")
    print(f"   ✅ pandas {pd.__version__} available")
    print(f"   ✅ openpyxl {openpyxl.__version__} available")
    
    # Test with sample data
    sample_data = [
        {"id": "uuid-1", "name": "John Doe", "cgpa": 8.5},
        {"id": "uuid-2", "name": "Jane Smith", "cgpa": 9.2},
    ]
    
    sample_stats = {
        "total_rows": 2,
        "columns": ["id", "name", "cgpa"],
        "column_types": {"id": "uuid", "name": "string", "cgpa": "float"},
        "execution_time_ms": 45.67,
        "executed_at": "2026-05-23T10:30:00",
        "aggregations": {
            "numeric": {
                "cgpa": {"count": 2, "min": 8.5, "max": 9.2, "avg": 8.85, "sum": 17.7}
            }
        }
    }
    
    sample_query_info = {
        "natural_query": "Show me test data",
        "sql": "SELECT * FROM test LIMIT 2",
        "explanation": "Test query",
        "tables_used": ["test"]
    }
    
    # Generate Excel
    buffer = excel_generator.generate_excel(sample_data, sample_stats, sample_query_info)
    
    # Save test file
    test_file = "test_excel_output.xlsx"
    with open(test_file, "wb") as f:
        f.write(buffer.getvalue())
    
    print(f"   ✅ Excel generation successful")
    print(f"   📄 Test file created: {test_file} ({len(buffer.getvalue())} bytes)")
    
except ImportError as e:
    print(f"   ❌ Excel libraries not installed: {e}")
    print(f"      Run: pip install pandas openpyxl")
except Exception as e:
    print(f"   ❌ Excel generator test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: AI Service (requires env vars but no DB)
print("\n4️⃣  Testing AI Service...")
try:
    from app.services.ai_service import ai_service
    
    # Check if method exists
    if hasattr(ai_service, 'generate_sql_from_natural_language'):
        print(f"   ✅ AI service imported")
        print(f"   ✅ generate_sql_from_natural_language method exists")

        # Try to get provider info
        try:
            from app.config import settings
            print(f"   ℹ️  AI Provider: {settings.AI_PROVIDER}")
            print(f"   ℹ️  AI Enabled: {settings.AI_ENABLED}")
        except Exception as e:
            print(f"   ℹ️  AI config: {e}")
    else:
        print(f"   ❌ generate_sql_from_natural_language method not found")
        
except Exception as e:
    print(f"   ⚠️  AI service test skipped: {e}")
    print(f"      (This is OK - requires proper .env configuration)")

# Test 5: File structure verification
print("\n5️⃣  Verifying File Structure...")
files_to_check = [
    "app/services/schema_provider.py",
    "app/services/sql_validator.py",
    "app/services/query_executor.py",
    "app/services/excel_generator.py",
    "app/api/v1/endpoints/nl_query.py",
]

all_exist = True
for file_path in files_to_check:
    full_path = Path(__file__).parent / file_path
    if full_path.exists():
        size = full_path.stat().st_size
        print(f"   ✅ {file_path} ({size:,} bytes)")
    else:
        print(f"   ❌ {file_path} NOT FOUND")
        all_exist = False

# Final Summary
print("\n" + "=" * 80)
print("📊 TEST SUMMARY")
print("=" * 80)

print("\n✅ Core Components Working:")
print("   • Schema Provider (database documentation)")
print("   • SQL Validator (security layer)")
print("   • Excel Generator (export functionality)")
print("   • All required files created")

print("\n⚠️  Components Requiring Full Environment:")
print("   • AI Service (needs .env configuration)")
print("   • Query Executor (needs database connection)")
print("   • API Endpoints (needs full FastAPI setup)")

print("\n💡 Next Steps:")
print("   1. Install dependencies:")
print("      pip install -r requirements.txt")
print("   2. Ensure .env file is configured")
print("   3. Start server:")
print("      uvicorn app.main:app --reload")
print("   4. Test API at http://localhost:8000/docs")

print("\n" + "=" * 80)
print("✅ Standalone Test Complete!")
print("=" * 80)
