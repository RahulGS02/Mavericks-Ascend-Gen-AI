"""
Quick test to check if the register endpoint exists
"""
import sys
sys.path.insert(0, '.')

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

print("Testing /api/v1/mavericks/register endpoint...")
print("=" * 60)

# List all routes
routes = []
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        routes.append(f"{list(route.methods)[0] if route.methods else 'N/A'} {route.path}")

# Filter maverick routes
maverick_routes = [r for r in routes if 'maverick' in r.lower()]

print("\nAll Maverick Routes:")
print("-" * 60)
for route in sorted(maverick_routes):
    print(route)

print("\n" + "=" * 60)

# Check if register endpoint exists
register_exists = any('/mavericks/register' in r and 'POST' in r for r in maverick_routes)
print(f"\nPOST /api/v1/mavericks/register exists: {register_exists}")

if not register_exists:
    print("\n❌ ERROR: Register endpoint NOT FOUND!")
    print("\nExpected: POST /api/v1/mavericks/register")
    print("\nPossible issues:")
    print("1. Server needs to be restarted")
    print("2. File changes not saved")
    print("3. Import error in mavericks.py")
else:
    print("\n✅ SUCCESS: Register endpoint found!")
