"""Create test maverick user via API"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def create_test_maverick():
    print("\n" + "="*70)
    print("🚀 CREATING TEST MAVERICK USER VIA API")
    print("="*70)
    
    # Step 1: Try to login first to see if user exists
    print("\n1️⃣  Checking if user already exists...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "maverick@test.com",
            "password": "maverick123"
        }
    )
    
    if login_response.status_code == 200:
        print("   ✅ User already exists and can login!")
        print(f"\n📝 LOGIN CREDENTIALS:")
        print("-"*70)
        print(f"   Email:    maverick@test.com")
        print(f"   Password: maverick123")
        print("-"*70)
        return
    
    print("   ℹ️  User doesn't exist, creating...")
    
    # Step 2: Register via maverick registration endpoint
    print("\n2️⃣  Registering new maverick...")
    
    # Use the maverick self-registration endpoint
    register_data = {
        "name": "Test Maverick Student",
        "email": "maverick@test.com",
        "password": "maverick123",
        "phone": "9876543210",
        "college": "Test University",
        "degree": "B.Tech",
        "branch": "Computer Science",
        "graduation_year": 2024,
        "cgpa": 8.5,
        "skills": "Python, JavaScript, React, Node.js"
    }
    
    register_response = requests.post(
        f"{BASE_URL}/mavericks/register",
        data=register_data  # Using data (form-data) instead of json
    )
    
    if register_response.status_code == 201:
        result = register_response.json()
        print("   ✅ Maverick registered successfully!")
        print("\n" + "="*70)
        print("✅ TEST MAVERICK CREATED SUCCESSFULLY!")
        print("="*70)
        print(f"\n📝 LOGIN CREDENTIALS:")
        print("-"*70)
        print(f"   Email:    maverick@test.com")
        print(f"   Password: maverick123")
        print(f"   Role:     MAVERICK")
        print("-"*70)
        print(f"\n🎟️  Access Token: {result.get('access_token', 'N/A')[:50]}...")
        print(f"📋 Profile Status: {result.get('profile_status', 'N/A')}")
        print("\n🎉 You can now login with these credentials!")
        print("="*70 + "\n")
    else:
        print(f"   ❌ Registration failed!")
        print(f"   Status: {register_response.status_code}")
        print(f"   Error: {register_response.text}")
        
        # Try alternative: create via auth register endpoint (requires HR role)
        print("\n3️⃣  Alternative: Trying basic user registration...")
        print("   ℹ️  This requires creating as regular user first...")
        
        # First login as HR
        hr_login = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "hr@maverick.com",
                "password": "hr123"
            }
        )
        
        if hr_login.status_code == 200:
            hr_token = hr_login.json()["access_token"]
            print("   ✅ Logged in as HR")
            
            # Create user via auth register
            auth_register = requests.post(
                f"{BASE_URL}/auth/register",
                json={
                    "email": "maverick@test.com",
                    "password": "maverick123",
                    "name": "Test Maverick Student",
                    "role": "maverick"
                }
            )
            
            if auth_register.status_code == 201:
                print("   ✅ User account created!")
                print("\n💡 NOTE: You may need to create maverick profile separately")
                print(f"\n📝 LOGIN CREDENTIALS:")
                print("-"*70)
                print(f"   Email:    maverick@test.com")
                print(f"   Password: maverick123")
                print("-"*70)
            else:
                print(f"   ❌ Failed: {auth_register.status_code}")
                print(f"   Error: {auth_register.text}")
        else:
            print(f"   ❌ Couldn't login as HR")
            print("\n💡 SOLUTION: Use existing test users from seed data:")
            print("-"*70)
            print("   Email:    maverick1@example.com")
            print("   Password: maverick123")
            print("-"*70)

if __name__ == "__main__":
    try:
        create_test_maverick()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
