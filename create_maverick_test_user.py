"""Create maverick@test.com user via API"""
import requests

BASE_URL = "http://localhost:8000/api/v1"

def create_user():
    print("\n" + "="*70)
    print("🚀 CREATING MAVERICK@TEST.COM USER")
    print("="*70)
    
    # Try registration via maverick registration endpoint
    print("\n1️⃣  Registering maverick@test.com...")
    
    # Prepare form data
    form_data = {
        "name": "Test Maverick Student",
        "email": "maverick@test.com",
        "password": "maverick123",
        "phone": "9876543210",
        "college": "Test University",
        "degree": "B.Tech",
        "branch": "Computer Science",
        "graduation_year": "2024",
        "cgpa": "8.5",
        "skills": "Python, JavaScript, React, Node.js, SQL"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/mavericks/register",
            data=form_data
        )
        
        if response.status_code == 201:
            result = response.json()
            print("   ✅ SUCCESS! User created!")
            print("\n" + "="*70)
            print("✅ MAVERICK@TEST.COM CREATED!")
            print("="*70)
            print(f"\n📝 LOGIN CREDENTIALS:")
            print("-"*70)
            print(f"   Email:    maverick@test.com")
            print(f"   Password: maverick123")
            print(f"   Role:     MAVERICK")
            print("-"*70)
            print(f"\n🎟️  Access Token: {result.get('access_token', 'N/A')[:50]}...")
            print(f"👤 User ID: {result.get('user', {}).get('id', 'N/A')}")
            print(f"📋 Maverick ID: {result.get('maverick_id', 'N/A')}")
            print(f"📊 Profile Status: {result.get('profile_status', 'N/A')}")
            print("\n🎉 You can now login at http://localhost:3000/login")
            print("="*70 + "\n")
            return True
            
        elif response.status_code == 400:
            error_detail = response.json().get('detail', response.text)
            if "already registered" in error_detail.lower():
                print("   ℹ️  User already exists!")
                print("\n💡 The user exists but password might be wrong.")
                print("   Let me try to login to verify...")
                
                # Try login
                login_response = requests.post(
                    f"{BASE_URL}/auth/login",
                    json={
                        "email": "maverick@test.com",
                        "password": "maverick123"
                    }
                )
                
                if login_response.status_code == 200:
                    print("   ✅ Login successful! Password is correct.")
                    print(f"\n📝 Use these credentials:")
                    print("-"*70)
                    print(f"   Email:    maverick@test.com")
                    print(f"   Password: maverick123")
                    print("-"*70)
                    return True
                else:
                    print(f"   ❌ Login failed: {login_response.status_code}")
                    print(f"   Error: {login_response.text}")
                    print("\n💡 SOLUTION: User exists but password is different.")
                    print("   Use one of these instead:")
                    print("-"*70)
                    print(f"   Email:    maverick1@example.com")
                    print(f"   Password: maverick123")
                    print("-"*70)
                    return False
            else:
                print(f"   ❌ Registration failed: {error_detail}")
                return False
        else:
            print(f"   ❌ Registration failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("   ❌ ERROR: Cannot connect to backend!")
        print("\n💡 Make sure backend is running:")
        print("   cd apps/api")
        print("   uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = create_user()
    
    if not success:
        print("\n" + "="*70)
        print("❌ COULDN'T CREATE maverick@test.com")
        print("="*70)
        print("\n💡 ALTERNATIVE: Use existing test users")
        print("-"*70)
        print("   Email:    maverick1@example.com")
        print("   Password: maverick123")
        print("-"*70)
        print("\nor try:")
        print("-"*70)
        print("   Email:    hr@maverick.com")
        print("   Password: hr123")
        print("-"*70)
        print("\n")
