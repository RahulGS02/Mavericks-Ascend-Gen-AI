"""Test maverick registration endpoint"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

print("=" * 70)
print("TESTING MAVERICK REGISTRATION")
print("=" * 70)

# Test data
test_data = {
    "name": "Test Maverick",
    "email": "testmav@example.com",
    "password": "testpass123",
    "phone": "1234567890",
    "college": "Test College",
    "degree": "B.Tech",
    "branch": "Computer Science",
    "graduation_year": 2024,
    "cgpa": 8.5,
    "skills": "Python, JavaScript, SQL",
    "github_url": "https://github.com/testuser",
    "linkedin_url": "https://linkedin.com/in/testuser"
}

print("\n📝 Registration data:")
for key, value in test_data.items():
    if key != "password":
        print(f"   {key}: {value}")
    else:
        print(f"   {key}: ******")

print("\n🔄 Sending registration request...")

try:
    response = requests.post(
        f"{BASE_URL}/mavericks/register",
        data=test_data,  # Use data instead of json for FormData
        timeout=10
    )
    
    print(f"\n📊 Response Status: {response.status_code}")
    print(f"📊 Response Headers: {dict(response.headers)}")
    
    if response.status_code == 201:
        print("\n✅ REGISTRATION SUCCESSFUL!")
        result = response.json()
        print(f"\n📋 Response Data:")
        print(json.dumps(result, indent=2))
        
        print(f"\n🎫 Access Token: {result.get('access_token', 'N/A')[:50]}...")
        print(f"👤 User ID: {result.get('user', {}).get('id', 'N/A')}")
        print(f"📧 Email: {result.get('user', {}).get('email', 'N/A')}")
        print(f"🆔 Maverick ID: {result.get('maverick_id', 'N/A')}")
        
        # Try to login
        print("\n" + "=" * 70)
        print("TESTING LOGIN")
        print("=" * 70)
        
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": test_data["email"],
                "password": test_data["password"]
            }
        )
        
        if login_response.status_code == 200:
            print("\n✅ LOGIN SUCCESSFUL!")
            login_result = login_response.json()
            print(f"🎫 Login Token: {login_result.get('access_token', 'N/A')[:50]}...")
        else:
            print(f"\n❌ LOGIN FAILED: {login_response.status_code}")
            print(f"Error: {login_response.text}")
            
    elif response.status_code == 400:
        print("\n⚠️  REGISTRATION FAILED - Bad Request")
        print(f"Error: {response.text}")
        
        try:
            error_data = response.json()
            print(f"\nDetail: {error_data.get('detail', 'N/A')}")
        except:
            pass
            
    elif response.status_code == 500:
        print("\n❌ REGISTRATION FAILED - Server Error")
        print(f"Error: {response.text}")
        
        try:
            error_data = response.json()
            print(f"\nDetail: {error_data.get('detail', 'N/A')}")
        except:
            pass
            
    else:
        print(f"\n❌ UNEXPECTED STATUS CODE: {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Could not connect to backend!")
    print("   Make sure backend is running on http://localhost:8000")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
