"""
Quick test to verify all imports work correctly
"""
import sys
import os
from pathlib import Path

# Load environment variables first
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print("✅ Loaded .env file")
else:
    print("⚠️  No .env file found - some imports may fail")

print("=" * 80)
print("🧪 Testing Imports for Natural Language Query Feature")
print("=" * 80)

errors = []

# Test 1: Schema Provider
print("\n1️⃣  Testing schema_provider.py...")
try:
    from app.services.schema_provider import get_database_schema_context, get_schema_summary
    print("   ✅ schema_provider imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import schema_provider: {e}")
    errors.append(("schema_provider", e))

# Test 2: AI Service
print("\n2️⃣  Testing ai_service.py...")
try:
    from app.services.ai_service import ai_service
    print("   ✅ ai_service imported successfully")
    
    # Check if new method exists
    if hasattr(ai_service, 'generate_sql_from_natural_language'):
        print("   ✅ generate_sql_from_natural_language method exists")
    else:
        print("   ❌ generate_sql_from_natural_language method not found")
        errors.append(("ai_service", "Method not found"))
except Exception as e:
    print(f"   ❌ Failed to import ai_service: {e}")
    errors.append(("ai_service", e))

# Test 3: SQL Validator
print("\n3️⃣  Testing sql_validator.py...")
try:
    from app.services.sql_validator import validate_sql_query, sanitize_sql_query, get_query_tables
    print("   ✅ sql_validator imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import sql_validator: {e}")
    errors.append(("sql_validator", e))

# Test 4: Query Executor
print("\n4️⃣  Testing query_executor.py...")
try:
    from app.services.query_executor import execute_safe_query
    print("   ✅ query_executor imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import query_executor: {e}")
    errors.append(("query_executor", e))

# Test 5: Excel Generator
print("\n5️⃣  Testing excel_generator.py...")
try:
    from app.services.excel_generator import excel_generator
    print("   ✅ excel_generator imported successfully")
    
    # Check if pandas/openpyxl are available
    try:
        import pandas
        import openpyxl
        print("   ✅ pandas and openpyxl available")
    except ImportError as e:
        print(f"   ⚠️  Excel libraries not installed: {e}")
        print("      Run: pip install pandas openpyxl")
        errors.append(("excel_libraries", e))
except Exception as e:
    print(f"   ❌ Failed to import excel_generator: {e}")
    errors.append(("excel_generator", e))

# Test 6: API Endpoint
print("\n6️⃣  Testing nl_query API endpoint...")
try:
    from app.api.v1.endpoints.nl_query import router
    print("   ✅ nl_query router imported successfully")
except Exception as e:
    print(f"   ❌ Failed to import nl_query router: {e}")
    errors.append(("nl_query_router", e))

# Summary
print("\n" + "=" * 80)
print("📊 IMPORT TEST SUMMARY")
print("=" * 80)

if errors:
    print(f"\n❌ {len(errors)} error(s) found:\n")
    for module, error in errors:
        print(f"   - {module}: {error}")
    print("\n⚠️  Fix these errors before proceeding.")
    sys.exit(1)
else:
    print("\n✅ ALL IMPORTS SUCCESSFUL!")
    print("\n🎉 Natural Language Query feature is ready to use!")
    print("\nNext steps:")
    print("   1. Run: python test_nl_query_api.py")
    print("   2. Start server: uvicorn app.main:app --reload")
    print("   3. Visit: http://localhost:8000/docs")
    print("   4. Test: POST /api/v1/nl-query/search")
    sys.exit(0)
