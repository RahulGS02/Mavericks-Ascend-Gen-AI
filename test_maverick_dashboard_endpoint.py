"""Test maverick dashboard endpoint"""
import requests

BASE_URL = "http://localhost:8000/api/v1"

def test_endpoint():
    print("\n" + "="*70)
    print("🧪 TESTING MAVERICK DASHBOARD ENDPOINT")
    print("="*70)
    
    # Step 1: Login as maverick
    print("\n1️⃣  Logging in as maverick1@example.com...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "maverick1@example.com",
            "password": "maverick123"
        }
    )
    
    if login_response.status_code != 200:
        print(f"   ❌ Login failed: {login_response.status_code}")
        print(f"   Error: {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    print(f"   ✅ Login successful!")
    print(f"   Token: {token[:50]}...")
    
    # Step 2: Test dashboard endpoint
    print("\n2️⃣  Testing /maverick/dashboard/overview endpoint...")
    headers = {"Authorization": f"Bearer {token}"}
    
    dashboard_response = requests.get(
        f"{BASE_URL}/maverick/dashboard/overview",
        headers=headers
    )
    
    print(f"   Status Code: {dashboard_response.status_code}")
    
    if dashboard_response.status_code == 200:
        print("   ✅ Dashboard endpoint working!")
        data = dashboard_response.json()
        print("\n📊 Response Structure:")
        print(f"   - Welcome: {data.get('welcome', {}).get('message', 'N/A')}")
        print(f"   - Has Batch: {data.get('welcome', {}).get('has_batch', False)}")
        print(f"   - Progress: {data.get('progress', {}).get('overall_completion', 0)}%")
        print(f"   - Total Jobs: {data.get('progress', {}).get('total_jobs', 0)}")
        print(f"   - Assessments: {data.get('assessments', {}).get('total_taken', 0)}")
    elif dashboard_response.status_code == 404:
        print("   ❌ 404 NOT FOUND!")
        print(f"   Error: {dashboard_response.text}")
        print("\n💡 This means the route is not registered correctly!")
    elif dashboard_response.status_code == 403:
        print("   ❌ 403 FORBIDDEN!")
        print(f"   Error: {dashboard_response.text}")
        print("\n💡 This means the user doesn't have permission!")
    else:
        print(f"   ❌ Unexpected error: {dashboard_response.status_code}")
        print(f"   Error: {dashboard_response.text}")
    
    # Step 3: List all available routes
    print("\n3️⃣  Checking available routes...")
    try:
        # Try to get OpenAPI docs
        docs_response = requests.get(f"http://localhost:8000/openapi.json")
        if docs_response.status_code == 200:
            openapi_data = docs_response.json()
            maverick_routes = [
                path for path in openapi_data.get("paths", {}).keys()
                if "maverick" in path.lower()
            ]
            print(f"   Found {len(maverick_routes)} maverick-related routes:")
            for route in maverick_routes:
                print(f"   - {route}")
        else:
            print("   ℹ️  OpenAPI docs not available")
    except Exception as e:
        print(f"   ⚠️  Could not fetch routes: {e}")
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETE")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        test_endpoint()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
