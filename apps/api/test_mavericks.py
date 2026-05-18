"""
Test Maverick Management APIs
Run with: python test_mavericks.py
Make sure API server is running: uvicorn app.main:app --reload
"""
import requests
from io import BytesIO

BASE_URL = "http://localhost:8000"

def create_test_resume():
    """Create a simple test PDF resume"""
    pdf_content = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R>>endobj
4 0 obj<</Length 44>>stream
BT /F1 12 Tf 100 700 Td (John Doe Resume) Tj ET
endstream endobj
xref
0 5
trailer<</Size 5/Root 1 0 R>>
startxref
200
%%EOF"""
    return BytesIO(pdf_content)


def test_maverick_apis():
    """Test complete maverick management flow"""
    
    print("🧪 Testing Maverick Management APIs\n")
    print("=" * 70)
    
    # Step 1: Login
    print("\n1️⃣  Logging in as HR...")
    login_response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": "hr@maverick.com", "password": "hr123"}
    )
    
    if login_response.status_code != 200:
        print("❌ Login failed!")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful!")
    
    # Step 2: Create Maverick (without resume)
    print("\n2️⃣  Creating maverick without resume...")
    print("-" * 70)
    
    # Use timestamp to ensure unique emails
    import time
    timestamp = int(time.time())

    maverick_data = {
        "name": "Alice Johnson",
        "email": f"alice.johnson.{timestamp}@example.com",
        "phone": "+1234567890",
        "college": "MIT",
        "degree": "B.Tech",
        "branch": "Computer Science",
        "graduation_year": 2024,
        "cgpa": 8.5,
        "skills": ["Python", "JavaScript", "React", "Node.js"],
        "github_url": "https://github.com/alicejohnson",
        "linkedin_url": "https://linkedin.com/in/alicejohnson"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/mavericks/",
        headers=headers,
        json=maverick_data
    )
    
    if response.status_code == 201:
        print("✅ Maverick created successfully!")
        maverick1 = response.json()
        maverick1_id = maverick1['id']
        print(f"   ID: {maverick1_id}")
        print(f"   Name: {maverick1['name']}")
        print(f"   Email: {maverick1['email']}")
        print(f"   Status: {maverick1['profile_status']}")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        maverick1_id = None
    
    # Step 3: Create Maverick with Resume
    print("\n3️⃣  Creating maverick with resume upload...")
    print("-" * 70)
    
    resume_file = create_test_resume()
    files = {"resume": ("bob_resume.pdf", resume_file, "application/pdf")}
    data = {
        "name": "Bob Smith",
        "email": f"bob.smith.{timestamp}@example.com",
        "phone": "+1987654321",
        "college": "Stanford",
        "degree": "B.Tech",
        "branch": "Software Engineering",
        "graduation_year": 2024,
        "cgpa": 9.0,
        "github_url": "https://github.com/bobsmith"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/mavericks/with-resume",
        headers=headers,
        files=files,
        data=data
    )
    
    if response.status_code == 201:
        print("✅ Maverick with resume created successfully!")
        maverick2 = response.json()
        maverick2_id = maverick2['id']
        print(f"   ID: {maverick2_id}")
        print(f"   Name: {maverick2['name']}")
        print(f"   Resume URL: {maverick2['resume_url'][:60]}...")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
        maverick2_id = None
    
    # Step 4: Get All Mavericks
    print("\n4️⃣  Getting list of mavericks...")
    print("-" * 70)
    
    response = requests.get(
        f"{BASE_URL}/api/v1/mavericks/",
        headers=headers,
        params={"page": 1, "page_size": 10}
    )
    
    if response.status_code == 200:
        print("✅ Retrieved mavericks list!")
        data = response.json()
        print(f"   Total: {data['total']}")
        print(f"   Page: {data['page']}/{data['total_pages']}")
        print(f"   Showing {len(data['mavericks'])} mavericks")
    else:
        print(f"❌ Failed: {response.status_code}")
    
    # Step 5: Get Maverick by ID
    if maverick1_id:
        print("\n5️⃣  Getting maverick by ID...")
        print("-" * 70)
        
        response = requests.get(
            f"{BASE_URL}/api/v1/mavericks/{maverick1_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Retrieved maverick details!")
            maverick = response.json()
            print(f"   Name: {maverick['name']}")
            print(f"   College: {maverick['college']}")
            print(f"   CGPA: {maverick['cgpa']}")
            print(f"   Skills: {', '.join(maverick['skills'])}")
        else:
            print(f"❌ Failed: {response.status_code}")
    
    # Step 6: Update Maverick Profile
    if maverick1_id:
        print("\n6️⃣  Updating maverick profile...")
        print("-" * 70)
        
        update_data = {
            "cgpa": 8.8,
            "skills": ["Python", "JavaScript", "React", "Node.js", "Docker"]
        }
        
        response = requests.put(
            f"{BASE_URL}/api/v1/mavericks/{maverick1_id}",
            headers=headers,
            json=update_data
        )
        
        if response.status_code == 200:
            print("✅ Profile updated successfully!")
            maverick = response.json()
            print(f"   New CGPA: {maverick['cgpa']}")
            print(f"   New Skills: {', '.join(maverick['skills'])}")
        else:
            print(f"❌ Failed: {response.status_code}")
    
    # Step 7: Approve Maverick
    if maverick2_id:
        print("\n7️⃣  Approving maverick profile...")
        print("-" * 70)
        
        response = requests.patch(
            f"{BASE_URL}/api/v1/mavericks/{maverick2_id}/profile-status",
            headers=headers,
            json={
                "profile_status": "approved",
                "review_notes": "Excellent profile with strong background"
            }
        )
        
        if response.status_code == 200:
            print("✅ Profile approved!")
            maverick = response.json()
            print(f"   Status: {maverick['profile_status']}")
            print(f"   Notes: {maverick['review_notes']}")
        else:
            print(f"❌ Failed: {response.status_code}")
    
    # Step 8: Search Mavericks
    print("\n8️⃣  Searching mavericks...")
    print("-" * 70)
    
    response = requests.get(
        f"{BASE_URL}/api/v1/mavericks/",
        headers=headers,
        params={"search": "MIT"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Search results for 'MIT': {data['total']} found")
    else:
        print(f"❌ Failed: {response.status_code}")
    
    print("\n" + "=" * 70)
    print("🎉 Maverick Management tests completed!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        test_maverick_apis()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server")
        print("   Make sure the server is running:")
        print("   uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")
