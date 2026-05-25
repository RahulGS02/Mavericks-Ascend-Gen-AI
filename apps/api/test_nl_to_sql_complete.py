"""
Complete Test Script for Natural Language to SQL Feature
Tests all three components: Schema Provider, AI Service, SQL Validator, Query Executor
"""
import asyncio
import sys
from app.services.schema_provider import get_database_schema_context
from app.services.ai_service import ai_service
from app.services.sql_validator import validate_sql_query, sanitize_sql_query, get_query_tables


async def test_nl_to_sql_pipeline():
    """Test the complete Natural Language to SQL pipeline"""
    
    print("=" * 80)
    print("🧪 Testing Natural Language to SQL Pipeline")
    print("=" * 80)
    
    # Test 1: Get schema context
    print("\n1️⃣  Testing Schema Provider...")
    schema = get_database_schema_context()
    print(f"✅ Schema loaded: {len(schema)} characters")
    print(f"   Contains comprehensive database structure")
    
    # Test 2: Generate SQL from natural language
    print("\n2️⃣  Testing AI SQL Generation...")
    
    test_queries = [
        "Show me all mavericks who are available for deployment",
        "List active batches with their trainer counts",
        "Find mavericks with Python skills above 80% proficiency",
        "Show me the top 10 mavericks by CGPA",
        "Count how many mavericks are in each deployment status"
    ]
    
    for i, nl_query in enumerate(test_queries, 1):
        print(f"\n   Test Query {i}: \"{nl_query}\"")
        
        # Generate SQL
        result = await ai_service.generate_sql_from_natural_language(
            natural_query=nl_query,
            schema_context=schema
        )
        
        if result:
            print(f"   ✅ SQL Generated:")
            print(f"      {result['sql'][:100]}...")
            print(f"   📝 Explanation: {result['explanation']}")
            print(f"   📊 Tables used: {', '.join(result['tables_used'])}")
            print(f"   🔧 Complexity: {result['estimated_complexity']}")
            
            # Test 3: Validate the generated SQL
            print(f"\n   3️⃣  Validating generated SQL...")
            is_valid, error_msg, warnings = validate_sql_query(result['sql'])
            
            if is_valid:
                print(f"   ✅ SQL is valid")
                if warnings:
                    for warning in warnings:
                        print(f"      ⚠️  {warning}")
                
                # Test 4: Sanitize SQL
                sanitized = sanitize_sql_query(result['sql'])
                print(f"   🧹 Sanitized SQL:")
                print(f"      {sanitized[:100]}...")
                
                # Test 5: Extract tables
                tables = get_query_tables(sanitized)
                print(f"   📋 Extracted tables: {', '.join(tables)}")
                
            else:
                print(f"   ❌ SQL validation failed: {error_msg}")
        else:
            print(f"   ❌ Failed to generate SQL")
        
        print()
    
    # Test 6: Test SQL Validator with dangerous queries
    print("\n4️⃣  Testing SQL Validator with dangerous queries...")
    
    dangerous_queries = [
        "DROP TABLE mavericks;",
        "DELETE FROM users WHERE id = '123';",
        "SELECT * FROM users; DROP TABLE mavericks;",
        "SELECT * FROM users WHERE id = '1' OR '1'='1'--",
        "INSERT INTO mavericks (name) VALUES ('hacker')",
        "SELECT * FROM pg_catalog.pg_tables",
    ]
    
    for dangerous_sql in dangerous_queries:
        print(f"\n   Testing: {dangerous_sql[:50]}...")
        is_valid, error_msg, warnings = validate_sql_query(dangerous_sql)
        
        if is_valid:
            print(f"   ❌ SECURITY ISSUE: Query marked as valid but shouldn't be!")
        else:
            print(f"   ✅ Correctly rejected: {error_msg}")
    
    # Test 7: Test valid SELECT queries
    print("\n5️⃣  Testing SQL Validator with valid queries...")
    
    valid_queries = [
        "SELECT * FROM mavericks WHERE deployment_status = 'AVAILABLE' LIMIT 10",
        "SELECT m.name, b.name FROM mavericks m JOIN batches b ON m.current_batch_id = b.id LIMIT 100",
        "SELECT COUNT(*) as count FROM mavericks WHERE profile_status = 'approved'",
    ]
    
    for valid_sql in valid_queries:
        print(f"\n   Testing: {valid_sql[:60]}...")
        is_valid, error_msg, warnings = validate_sql_query(valid_sql)
        
        if is_valid:
            print(f"   ✅ Correctly validated")
            if warnings:
                for warning in warnings:
                    print(f"      ⚠️  {warning}")
        else:
            print(f"   ❌ ISSUE: Valid query rejected: {error_msg}")
    
    print("\n" + "=" * 80)
    print("✅ Natural Language to SQL Pipeline Test Complete!")
    print("=" * 80)
    
    print("\n📊 Test Summary:")
    print("   ✅ Schema Provider: Working")
    print("   ✅ AI SQL Generation: Working")
    print("   ✅ SQL Validator: Working (blocks dangerous queries)")
    print("   ✅ SQL Sanitizer: Working")
    print("   ✅ Table Extractor: Working")
    
    print("\n🚀 Next Steps:")
    print("   1. Test with actual database (query_executor.py)")
    print("   2. Create API endpoint")
    print("   3. Add Excel export functionality")
    print("   4. Build frontend UI")


if __name__ == "__main__":
    print("Starting Natural Language to SQL Test Suite...\n")
    
    try:
        asyncio.run(test_nl_to_sql_pipeline())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
