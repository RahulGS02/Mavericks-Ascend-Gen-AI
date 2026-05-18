"""
Test script for Maverick Self-Service Profile Creation
"""
import requests
import io
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

# Use timestamp to create unique email
TIMESTAMP = datetime.now().strftime("%Y%m%d%H%M%S")
TEST_EMAIL = f"maverick.test.{TIMESTAMP}@example.com"

def print_section(title):
    print(f"\n{'='*70}")
    print(f"\n{title}")
    print(f"\n{'-'*70}")

def print_result(success, message, data=None):
    if success:
        print(f"✅ {message}")
        if data:
            for key, value in data.items():
                print(f"   {key}: {value}")
    else:
        print(f"❌ {message}")

def test_maverick_self_service():
    print("\n👤 Testing Maverick Self-Service Profile Creation")
    print("="*70)
    
    # 1. Register as Maverick
    print_section("1️⃣  Registering as new Maverick...")
    print(f"   Using email: {TEST_EMAIL}")

    register_response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": TEST_EMAIL,
            "password": "TestPass123!",
            "name": "Test Maverick Student",
            "role": "maverick"
        }
    )

    if register_response.status_code == 201:
        print_result(True, "Maverick registered successfully!")
    elif register_response.status_code == 400 and "already registered" in register_response.text:
        print_result(False, f"Email already registered. Try again with new timestamp.")
        return
    else:
        print_result(False, f"Registration failed: {register_response.status_code} - {register_response.text}")
        return

    # 2. Login as Maverick
    print_section("2️⃣  Logging in as Maverick...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": TEST_EMAIL,
            "password": "TestPass123!"
        }
    )
    
    if login_response.status_code != 200:
        print_result(False, f"Login failed! {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print_result(True, "Login successful!")
    
    # 3. Check AI Status
    print_section("3️⃣  Checking AI Status...")
    ai_response = requests.get(f"{BASE_URL}/ai/status", headers=headers)
    
    if ai_response.status_code == 200:
        ai_status = ai_response.json()
        print_result(True, "AI Status checked!", {
            "AI Enabled": ai_status["enabled"],
            "AI Available": ai_status["available"],
            "Skill Extraction": ai_status["features"]["skill_extraction"]
        })
    else:
        print_result(False, f"AI status check failed: {ai_response.status_code}")
    
    # 4. Create Profile with Resume
    print_section("4️⃣  Creating complete profile with resume...")

    # Create a minimal PDF file (simplified PDF structure for testing)
    # In production, use actual PDF files
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
>>
endobj
4 0 obj
<<
/Length 200
>>
stream
BT
/F1 12 Tf
50 750 Td
(TEST RESUME) Tj
0 -20 Td
(Name: Test Maverick Student) Tj
0 -20 Td
(Education: B.Tech Computer Science) Tj
0 -20 Td
(Skills: Python, React, Node.js, SQL, Docker, AWS) Tj
0 -20 Td
(CGPA: 8.5/10) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000317 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
566
%%EOF"""

    resume_file = ("resume.pdf", io.BytesIO(pdf_content), "application/pdf")
    
    profile_data = {
        "name": "Test Maverick Student",
        "email": TEST_EMAIL,
        "phone": "+91-9876543210",
        "college": "XYZ College of Engineering",
        "degree": "B.Tech",
        "branch": "Computer Science Engineering",
        "graduation_year": 2026,
        "cgpa": 8.5,
        "skills": "Python, React, Node.js, SQL, Docker, Kubernetes, AWS",
        "github_url": "https://github.com/testmaverick",
        "linkedin_url": "https://linkedin.com/in/testmaverick"
    }
    
    response = requests.post(
        f"{BASE_URL}/mavericks/my-profile",
        headers=headers,
        data=profile_data,
        files={"resume": resume_file}
    )
    
    if response.status_code == 201:
        maverick = response.json()
        maverick_id = maverick["id"]
        print_result(True, "Profile created successfully!", {
            "Maverick ID": maverick_id,
            "Name": maverick["name"],
            "College": maverick["college"],
            "Status": maverick["profile_status"],
            "Skills Count": len(maverick["skills"])
        })
        
        # Show AI enhancements if available
        if maverick.get("ai_extracted_skills"):
            print(f"\n   🤖 AI Extracted Skills: {', '.join(maverick['ai_extracted_skills'][:5])}")
        
        if maverick.get("ai_summary"):
            print(f"\n   🤖 AI Summary: {maverick['ai_summary'][:100]}...")
    
    elif response.status_code == 400 and "already exists" in response.text:
        print_result(True, "Profile already exists!")
        # Get existing profile
        get_response = requests.get(f"{BASE_URL}/mavericks/my-profile", headers=headers)
        if get_response.status_code == 200:
            maverick = get_response.json()
            maverick_id = maverick["id"]
            print(f"   Existing Profile ID: {maverick_id}")
    else:
        print_result(False, f"Failed: {response.status_code} - {response.text}")
        return
    
    # 5. Get My Profile
    print_section("5️⃣  Getting my profile...")
    response = requests.get(f"{BASE_URL}/mavericks/my-profile", headers=headers)
    
    if response.status_code == 200:
        profile = response.json()
        print_result(True, "Profile retrieved!", {
            "Name": profile["name"],
            "Email": profile["email"],
            "College": profile["college"],
            "CGPA": profile["cgpa"],
            "Status": profile["profile_status"],
            "Resume Uploaded": "✅" if profile["resume_url"] else "❌"
        })
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    # 6. Update Profile
    print_section("6️⃣  Updating profile...")
    update_data = {
        "phone": "+91-9999888877",
        "skills": "Python, React, Node.js, Docker, AWS, TypeScript, GraphQL",
        "github_url": "https://github.com/testmaverick-updated"
    }
    
    response = requests.patch(
        f"{BASE_URL}/mavericks/my-profile",
        headers=headers,
        data=update_data
    )
    
    if response.status_code == 200:
        updated = response.json()
        print_result(True, "Profile updated!", {
            "Updated Phone": updated["phone"],
            "Updated Skills Count": len(updated["skills"])
        })
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    print("\n" + "="*70)
    print("🎉 Maverick Self-Service test completed!")
    print("\n📋 Next Steps:")
    print("   1. HR logs in and reviews the profile")
    print("   2. HR approves the profile")
    print("   3. HR assigns maverick to a batch")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_maverick_self_service()
