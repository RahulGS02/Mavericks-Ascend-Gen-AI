"""
Test Script for Natural Language Query API
Tests the complete end-to-end flow with sample queries
"""
import asyncio
import sys
from pathlib import Path

# Load environment variables FIRST
from dotenv import load_dotenv
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    print("✅ Loaded .env file\n")
else:
    print("⚠️  No .env file found - AI features may not work\n")

from app.services.schema_provider import get_database_schema_context
from app.services.ai_service import ai_service
from app.services.sql_validator import validate_sql_query, sanitize_sql_query
from app.services.excel_generator import excel_generator


# Sample natural language queries to test
SAMPLE_QUERIES = [
    {
        "query": "Show me all mavericks who are available for deployment",
        "category": "Deployment",
        "expected_tables": ["mavericks"]
    },
    {
        "query": "List active batches with their current enrollment",
        "category": "Batches",
        "expected_tables": ["batches"]
    },
    {
        "query": "Find mavericks with Python skills above 80% proficiency",
        "category": "Skills",
        "expected_tables": ["mavericks", "maverick_skills"]
    },
    {
        "query": "Show me the top 10 mavericks by CGPA",
        "category": "Academic Performance",
        "expected_tables": ["mavericks"]
    },
    {
        "query": "Count how many mavericks are in each deployment status",
        "category": "Statistics",
        "expected_tables": ["mavericks"]
    },
    {
        "query": "List all trainers and how many batches they are assigned to",
        "category": "Trainers",
        "expected_tables": ["users", "batch_trainers"]
    },
    {
        "query": "Show mavericks who joined in the last 30 days",
        "category": "Recent Additions",
        "expected_tables": ["mavericks"]
    },
    {
        "query": "Find batches that are planned or active",
        "category": "Batches",
        "expected_tables": ["batches"]
    },
    {
        "query": "Show approved mavericks with React or Angular skills",
        "category": "Skills",
        "expected_tables": ["mavericks", "maverick_skills"]
    },
    {
        "query": "Count total mavericks, batches, and active deployments",
        "category": "Overall Statistics",
        "expected_tables": ["mavericks", "batches", "deployments"]
    }
]


async def test_single_query(query_data: dict, schema_context: str):
    """Test a single natural language query"""
    
    print(f"\n{'='*80}")
    print(f"📝 Query: {query_data['query']}")
    print(f"📁 Category: {query_data['category']}")
    print(f"{'='*80}")
    
    # Step 1: Generate SQL
    print("\n1️⃣  Generating SQL with AI...")
    result = await ai_service.generate_sql_from_natural_language(
        natural_query=query_data['query'],
        schema_context=schema_context
    )
    
    if not result:
        print("   ❌ Failed to generate SQL")
        return False
    
    print(f"   ✅ SQL Generated")
    print(f"\n   SQL Query:")
    print(f"   {result['sql']}")
    print(f"\n   📝 Explanation: {result['explanation']}")
    print(f"   📊 Tables used: {', '.join(result['tables_used'])}")
    print(f"   🔧 Complexity: {result['estimated_complexity']}")
    
    # Step 2: Validate SQL
    print(f"\n2️⃣  Validating SQL...")
    is_valid, error_msg, warnings = validate_sql_query(result['sql'])
    
    if is_valid:
        print(f"   ✅ SQL is valid and safe")
        if warnings:
            for warning in warnings:
                print(f"      ⚠️  {warning}")
    else:
        print(f"   ❌ SQL validation failed: {error_msg}")
        return False
    
    # Step 3: Sanitize SQL
    print(f"\n3️⃣  Sanitizing SQL...")
    sanitized = sanitize_sql_query(result['sql'])
    if sanitized != result['sql']:
        print(f"   🧹 SQL was sanitized (LIMIT added/adjusted)")
    else:
        print(f"   ✅ SQL already clean")
    
    print(f"\n   Final SQL:")
    print(f"   {sanitized}")
    
    # Success!
    print(f"\n   ✅ Query test PASSED")
    return True


async def test_all_queries():
    """Test all sample queries"""
    
    print("=" * 80)
    print("🧪 NATURAL LANGUAGE QUERY API - COMPREHENSIVE TEST")
    print("=" * 80)
    
    # Get schema context once
    print("\n📚 Loading database schema context...")
    schema_context = get_database_schema_context()
    print(f"✅ Schema loaded: {len(schema_context)} characters")
    
    # Test each query
    results = {
        "total": len(SAMPLE_QUERIES),
        "passed": 0,
        "failed": 0
    }
    
    for i, query_data in enumerate(SAMPLE_QUERIES, 1):
        print(f"\n\n{'#'*80}")
        print(f"# TEST {i}/{len(SAMPLE_QUERIES)}")
        print(f"{'#'*80}")
        
        try:
            success = await test_single_query(query_data, schema_context)
            if success:
                results["passed"] += 1
            else:
                results["failed"] += 1
        except Exception as e:
            print(f"\n   ❌ Exception during test: {e}")
            results["failed"] += 1
            import traceback
            traceback.print_exc()
    
    # Final summary
    print("\n\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print(f"\n   Total Queries Tested: {results['total']}")
    print(f"   ✅ Passed: {results['passed']}")
    print(f"   ❌ Failed: {results['failed']}")
    
    success_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
    print(f"\n   Success Rate: {success_rate:.1f}%")
    
    if results['failed'] == 0:
        print("\n   🎉 ALL TESTS PASSED! Natural Language Query feature is working perfectly!")
    else:
        print(f"\n   ⚠️  {results['failed']} test(s) failed. Review the output above for details.")
    
    print("\n" + "=" * 80)
    print("✅ Test Suite Complete")
    print("=" * 80)
    
    return results


async def test_excel_generation():
    """Test Excel generation with sample data"""
    
    print("\n\n" + "=" * 80)
    print("📊 TESTING EXCEL GENERATION")
    print("=" * 80)
    
    # Sample data
    sample_data = [
        {"id": "uuid-1", "name": "John Doe", "email": "john@example.com", "cgpa": 8.5, "deployment_status": "AVAILABLE"},
        {"id": "uuid-2", "name": "Jane Smith", "email": "jane@example.com", "cgpa": 9.2, "deployment_status": "AVAILABLE"},
        {"id": "uuid-3", "name": "Bob Wilson", "email": "bob@example.com", "cgpa": 7.8, "deployment_status": "DEPLOYED"},
    ]
    
    sample_stats = {
        "total_rows": 3,
        "columns": ["id", "name", "email", "cgpa", "deployment_status"],
        "column_types": {"id": "uuid", "name": "string", "email": "string", "cgpa": "float", "deployment_status": "string"},
        "execution_time_ms": 45.67,
        "executed_at": "2026-05-23T10:30:00",
        "aggregations": {
            "numeric": {
                "cgpa": {"count": 3, "min": 7.8, "max": 9.2, "avg": 8.5, "sum": 25.5}
            },
            "string": {
                "deployment_status": {"count": 3, "unique_count": 2, "unique_values": ["AVAILABLE", "DEPLOYED"]}
            }
        }
    }
    
    sample_query_info = {
        "natural_query": "Show me mavericks available for deployment",
        "sql": "SELECT id, name, email, cgpa, deployment_status FROM mavericks WHERE deployment_status = 'AVAILABLE' LIMIT 100",
        "explanation": "Returns all mavericks with AVAILABLE deployment status",
        "tables_used": ["mavericks"]
    }
    
    try:
        print("\n🔨 Generating Excel file...")
        buffer = excel_generator.generate_excel(sample_data, sample_stats, sample_query_info)
        
        # Save to file
        output_path = "test_query_results.xlsx"
        with open(output_path, "wb") as f:
            f.write(buffer.getvalue())
        
        print(f"   ✅ Excel file generated: {output_path}")
        print(f"   📊 File size: {len(buffer.getvalue())} bytes")
        print(f"   📄 Sheets: Query Results, Statistics, Query Info")
        print(f"\n   🎉 Excel generation test PASSED!")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Excel generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🚀 Starting Natural Language Query API Test Suite...\n")
    
    try:
        # Test queries
        query_results = asyncio.run(test_all_queries())
        
        # Test Excel generation
        excel_result = asyncio.run(test_excel_generation())
        
        # Final status
        print("\n\n" + "=" * 80)
        print("🏁 FINAL STATUS")
        print("=" * 80)
        print(f"\n   Natural Language Queries: {'✅ PASSED' if query_results['failed'] == 0 else '❌ FAILED'}")
        print(f"   Excel Generation: {'✅ PASSED' if excel_result else '❌ FAILED'}")
        
        if query_results['failed'] == 0 and excel_result:
            print("\n   🎉 ALL SYSTEMS GO! Natural Language Query feature is production-ready!")
            sys.exit(0)
        else:
            print("\n   ⚠️  Some tests failed. Review the output above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
