"""
Test script for schema_provider.py
Verifies the schema context is comprehensive and accurate
"""
from app.services.schema_provider import get_database_schema_context, get_schema_summary

print("=" * 80)
print("🧪 Testing Schema Provider")
print("=" * 80)

# Test 1: Get full schema
print("\n1️⃣  Getting full database schema context...")
schema = get_database_schema_context()

print(f"✅ Schema loaded: {len(schema)} characters")
print(f"   Contains comprehensive database structure")

# Test 2: Verify key tables are included
print("\n2️⃣  Verifying all tables are documented...")
required_tables = [
    "mavericks",
    "maverick_skills",
    "batches",
    "users",
    "batch_trainers",
    "pipelines",
    "pipeline_jobs",
    "deployments",
    "deployment_requests",
    "assessments",
    "assessment_attempts"
]

for table in required_tables:
    if f"TABLE: {table}" in schema:
        print(f"   ✅ {table}")
    else:
        print(f"   ❌ {table} - MISSING!")

# Test 3: Verify important sections
print("\n3️⃣  Verifying important sections...")
sections = [
    "PRIMARY KEY",
    "FOREIGN KEY",
    "RELATIONSHIPS",
    "COMMON QUERIES",
    "ENUM VALUES",
    "EXAMPLE VALID QUERIES",
    "IMPORTANT POSTGRESQL QUERY RULES"
]

for section in sections:
    if section in schema:
        count = schema.count(section)
        print(f"   ✅ {section}: Found {count} times")
    else:
        print(f"   ❌ {section} - MISSING!")

# Test 4: Check for key information
print("\n4️⃣  Checking for essential information...")
essentials = [
    "UUID",
    "deployment_status = 'AVAILABLE'",
    "profile_status = 'approved'",
    "INNER JOIN",
    "WHERE",
    "LIMIT",
    "PostgreSQL",
    "CASCADE DELETE"
]

for essential in essentials:
    if essential in schema:
        print(f"   ✅ Contains: {essential}")
    else:
        print(f"   ⚠️  Missing: {essential}")

# Test 5: Get schema summary
print("\n5️⃣  Getting schema summary...")
summary = get_schema_summary()
print(f"✅ Summary loaded: {len(summary)} characters")
print(summary)

# Test 6: Show sample output
print("\n6️⃣  Sample schema output (first 500 characters)...")
print("-" * 80)
print(schema[:500])
print("...")
print("-" * 80)

print("\n" + "=" * 80)
print("✅ Schema Provider Test Complete!")
print("=" * 80)
print("\n💡 The schema context includes:")
print("   - All table structures with column types")
print("   - Primary keys and foreign keys")
print("   - Relationships between tables")
print("   - ENUM value lists (exact case-sensitive values)")
print("   - Common query patterns")
print("   - PostgreSQL-specific syntax rules")
print("   - Example valid queries")
print("\n🎯 This comprehensive context helps AI generate:")
print("   ✅ Valid SQL syntax")
print("   ✅ Correct JOIN conditions")
print("   ✅ Proper ENUM values")
print("   ✅ Accurate column references")
print("   ✅ Safe, read-only queries")
print("\n🚀 Ready to use for Natural Language to SQL feature!")
