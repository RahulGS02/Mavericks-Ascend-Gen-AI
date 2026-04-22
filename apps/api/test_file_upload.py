"""
Test file upload endpoints
Run with: python test_file_upload.py
Make sure API server is running: uvicorn app.main:app --reload
"""
import requests
import os
from io import BytesIO

BASE_URL = "http://localhost:8000"

def create_test_pdf():
    """Create a simple test PDF file"""
    # Simple PDF header (minimal valid PDF)
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
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test Resume) Tj
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
407
%%EOF
"""
    return BytesIO(pdf_content)


def create_test_csv():
    """Create a simple test CSV file"""
    csv_content = b"""Name,Email,Skills,College
John Doe,john@example.com,"Python,JavaScript,React",MIT
Jane Smith,jane@example.com,"Java,Spring Boot,SQL",Stanford
Bob Wilson,bob@example.com,"Python,Django,PostgreSQL",Harvard
"""
    return BytesIO(csv_content)


def test_file_upload():
    """Test complete file upload flow"""
    
    print("🧪 Testing File Upload System\n")
    print("=" * 60)
    
    # Step 1: Login to get token
    print("\n1️⃣  Logging in to get auth token...")
    login_response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": "admin@maverick.com", "password": "admin123"}
    )
    
    if login_response.status_code != 200:
        print("❌ Login failed!")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful!")
    
    # Step 2: Test Resume Upload
    print("\n2️⃣  Testing resume upload (PDF)...")
    print("-" * 60)
    
    pdf_file = create_test_pdf()
    files = {
        "file": ("test_resume.pdf", pdf_file, "application/pdf")
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/files/upload/resume",
        headers=headers,
        files=files
    )
    
    if response.status_code == 200:
        print("✅ Resume upload successful!")
        data = response.json()
        print(f"   File Path: {data['file_path']}")
        print(f"   Public URL: {data['public_url']}")
        print(f"   File Size: {data['file_size']} bytes")
        print(f"   Bucket: {data['bucket']}")
        resume_file_path = data['file_path']
        resume_bucket = data['bucket']
    else:
        print(f"❌ Resume upload failed: {response.status_code}")
        print(f"   Error: {response.text}")
        resume_file_path = None
        resume_bucket = None
    
    # Step 3: Test Excel/CSV Upload
    print("\n3️⃣  Testing Excel/CSV upload...")
    print("-" * 60)
    
    csv_file = create_test_csv()
    files = {
        "file": ("test_data.csv", csv_file, "text/csv")
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/files/upload/excel",
        headers=headers,
        files=files
    )
    
    if response.status_code == 200:
        print("✅ CSV upload successful!")
        data = response.json()
        print(f"   File Path: {data['file_path']}")
        print(f"   Public URL: {data['public_url']}")
        print(f"   File Size: {data['file_size']} bytes")
        print(f"   Bucket: {data['bucket']}")
        excel_file_path = data['file_path']
        excel_bucket = data['bucket']
    else:
        print(f"❌ CSV upload failed: {response.status_code}")
        print(f"   Error: {response.text}")
        excel_file_path = None
        excel_bucket = None
    
    # Step 4: Test File Download
    if resume_file_path and resume_bucket:
        print("\n4️⃣  Testing file download...")
        print("-" * 60)
        
        response = requests.get(
            f"{BASE_URL}/api/v1/files/download/{resume_bucket}/{resume_file_path}",
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ File download successful!")
            print(f"   Downloaded {len(response.content)} bytes")
        else:
            print(f"❌ File download failed: {response.status_code}")
    
    # Step 5: Test File Size Validation
    print("\n5️⃣  Testing file size validation...")
    print("-" * 60)
    
    # Create a file that's too large (6MB for resume which has 5MB limit)
    large_file = BytesIO(b"x" * (6 * 1024 * 1024))
    files = {
        "file": ("large_resume.pdf", large_file, "application/pdf")
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/files/upload/resume",
        headers=headers,
        files=files
    )
    
    if response.status_code == 413:
        print("✅ File size validation working!")
        print(f"   Correctly rejected file > 5MB")
    else:
        print(f"⚠️  Unexpected response: {response.status_code}")
    
    # Step 6: Test File Type Validation
    print("\n6️⃣  Testing file type validation...")
    print("-" * 60)
    
    # Try to upload a text file as resume
    text_file = BytesIO(b"This is not a PDF")
    files = {
        "file": ("fake.pdf", text_file, "text/plain")
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/files/upload/resume",
        headers=headers,
        files=files
    )
    
    if response.status_code == 400:
        print("✅ File type validation working!")
        print(f"   Correctly rejected invalid file type")
    else:
        print(f"⚠️  Unexpected response: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎉 File upload tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_file_upload()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server")
        print("   Make sure the server is running:")
        print("   uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")
