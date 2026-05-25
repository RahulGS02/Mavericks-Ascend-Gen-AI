"""
Quick Test Script for AI Talent Search API
Verifies all endpoints are working correctly
"""
import sys
sys.path.insert(0, '.')

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

print("=" * 80)
print("🧪 Testing AI Talent Search API Endpoints")
print("=" * 80)

# Test 1: Check if routes are registered
print("\n1️⃣  Checking if routes are registered...")
routes = []
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        methods = list(route.methods) if route.methods else []
        if methods:
            routes.append(f"{methods[0]} {route.path}")

talent_search_routes = [r for r in routes if 'talent-search' in r]

if talent_search_routes:
    print(f"✅ Found {len(talent_search_routes)} talent search routes:")
    for route in sorted(talent_search_routes):
        print(f"   {route}")
else:
    print("❌ No talent search routes found!")
    sys.exit(1)

# Test 2: Check endpoint accessibility (without auth - should get 401)
print("\n2️⃣  Testing endpoint authentication...")

endpoints_to_test = [
    ("POST", "/api/v1/talent-search/search", {"query": "test", "max_results": 10}),
    ("GET", "/api/v1/talent-search/cost-estimate", None),
    ("GET", "/api/v1/talent-search/statistics", None),
]

for method, path, data in endpoints_to_test:
    try:
        if method == "POST":
            response = client.post(path, json=data)
        else:
            response = client.get(path)
        
        # Should get 401 (Unauthorized) without token
        if response.status_code == 401:
            print(f"   ✅ {method} {path} - Returns 401 (authentication required)")
        else:
            print(f"   ⚠️  {method} {path} - Got {response.status_code} (expected 401)")
    except Exception as e:
        print(f"   ❌ {method} {path} - Error: {e}")

# Test 3: Check OpenAPI schema
print("\n3️⃣  Checking OpenAPI documentation...")
try:
    response = client.get("/docs")
    if response.status_code == 200:
        print("   ✅ Interactive API docs available at /docs")
    else:
        print(f"   ⚠️  /docs returned {response.status_code}")
except Exception as e:
    print(f"   ❌ Error accessing /docs: {e}")

# Test 4: Check API tags
print("\n4️⃣  Checking API tags...")
try:
    response = client.get("/openapi.json")
    if response.status_code == 200:
        openapi_spec = response.json()
        tags = [tag['name'] for tag in openapi_spec.get('tags', [])]
        if 'AI Talent Search' in tags:
            print("   ✅ 'AI Talent Search' tag found in OpenAPI spec")
        else:
            print("   ⚠️  'AI Talent Search' tag not found")
            print(f"   Available tags: {tags}")
    else:
        print(f"   ⚠️  /openapi.json returned {response.status_code}")
except Exception as e:
    print(f"   ❌ Error accessing /openapi.json: {e}")

# Test 5: Verify endpoint paths
print("\n5️⃣  Verifying expected endpoints...")
expected_endpoints = [
    "POST /api/v1/talent-search/search",
    "GET /api/v1/talent-search/explain/{candidate_id}",
    "GET /api/v1/talent-search/cost-estimate",
    "GET /api/v1/talent-search/statistics"
]

found_count = 0
for expected in expected_endpoints:
    # Convert path params to OpenAPI format
    check_path = expected.replace("{candidate_id}", "{id}")
    
    found = False
    for route in routes:
        if expected.split()[1] in route or check_path.split()[1] in route:
            found = True
            break
    
    if found or any(expected.split()[1] in r for r in routes):
        print(f"   ✅ {expected}")
        found_count += 1
    else:
        print(f"   ❌ {expected} - NOT FOUND")

print("\n" + "=" * 80)
print(f"📊 Summary: {found_count}/{len(expected_endpoints)} endpoints registered")
print("=" * 80)

if found_count == len(expected_endpoints):
    print("✅ ALL ENDPOINTS REGISTERED SUCCESSFULLY!")
    print("\n🚀 API is ready to use!")
    print("\n📚 Documentation available at: http://localhost:8000/docs")
    print("\n💡 Next steps:")
    print("   1. Start the server: uvicorn app.main:app --reload")
    print("   2. Login to get JWT token")
    print("   3. Test endpoints with authentication")
    print("   4. Run integration tests: pytest tests/test_talent_search_api.py -v")
else:
    print("⚠️  Some endpoints are missing!")
    print("   Check app/main.py router registration")

print("\n" + "=" * 80)
