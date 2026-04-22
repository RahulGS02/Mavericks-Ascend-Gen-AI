"""
Test authentication endpoints
Run with: python test_auth.py
Make sure the API server is running: uvicorn app.main:app --reload
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_authentication():
    """Test complete authentication flow"""
    
    print("🧪 Testing Authentication System\n")
    print("=" * 60)
    
    # Test 1: Login with existing user (from seed data)
    print("\n1️⃣ Test: Login with existing user")
    print("-" * 60)
    
    login_data = {
        "email": "admin@maverick.com",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    
    if response.status_code == 200:
        print("✅ Login successful!")
        token_data = response.json()
        access_token = token_data["access_token"]
        print(f"   Token: {access_token[:50]}...")
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return
    
    # Test 2: Get current user info
    print("\n2️⃣ Test: Get current user info")
    print("-" * 60)
    
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
    
    if response.status_code == 200:
        print("✅ Retrieved user info successfully!")
        user_data = response.json()
        print(f"   User: {user_data['name']} ({user_data['email']})")
        print(f"   Role: {user_data['role']}")
        print(f"   Active: {user_data['is_active']}")
    else:
        print(f"❌ Failed to get user info: {response.status_code}")
        print(f"   Error: {response.text}")
    
    # Test 3: Register new user
    print("\n3️⃣ Test: Register new user")
    print("-" * 60)
    
    new_user_data = {
        "email": "testuser@example.com",
        "password": "test12345",
        "name": "Test User",
        "role": "maverick"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=new_user_data)
    
    if response.status_code == 201:
        print("✅ User registered successfully!")
        user_data = response.json()
        print(f"   User ID: {user_data['id']}")
        print(f"   Name: {user_data['name']}")
        print(f"   Email: {user_data['email']}")
        print(f"   Role: {user_data['role']}")
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(f"   Error: {response.text}")
    
    # Test 4: Login with wrong password
    print("\n4️⃣ Test: Login with wrong password")
    print("-" * 60)
    
    wrong_login = {
        "email": "admin@maverick.com",
        "password": "wrongpassword"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=wrong_login)
    
    if response.status_code == 401:
        print("✅ Correctly rejected wrong password!")
    else:
        print(f"❌ Unexpected response: {response.status_code}")
    
    # Test 5: Access protected route without token
    print("\n5️⃣ Test: Access protected route without token")
    print("-" * 60)
    
    response = requests.get(f"{BASE_URL}/api/v1/auth/me")
    
    if response.status_code == 403:
        print("✅ Correctly blocked access without token!")
    else:
        print(f"⚠️  Response: {response.status_code}")
    
    # Test 6: Test all role logins
    print("\n6️⃣ Test: Login with different roles")
    print("-" * 60)
    
    test_users = [
        {"email": "hr@maverick.com", "password": "hr123", "role": "HR"},
        {"email": "trainer@maverick.com", "password": "trainer123", "role": "Trainer"},
        {"email": "manager@maverick.com", "password": "manager123", "role": "Manager"},
        {"email": "maverick1@example.com", "password": "maverick123", "role": "Maverick"},
    ]
    
    for user in test_users:
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json={
            "email": user["email"],
            "password": user["password"]
        })
        if response.status_code == 200:
            print(f"   ✅ {user['role']}: Login successful")
        else:
            print(f"   ❌ {user['role']}: Login failed")
    
    print("\n" + "=" * 60)
    print("🎉 Authentication tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_authentication()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server")
        print("   Make sure the server is running:")
        print("   uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")
