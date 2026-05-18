"""
Test Resume Parser with REAL PDF/DOCX files
Place your resume files in: apps/api/test_resumes/
"""
import requests
import os
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"
TEST_RESUMES_DIR = Path("test_resumes")

def print_section(title):
    print(f"\n{'='*70}")
    print(f"\n{title}")
    print(f"\n{'-'*70}")

def print_result(success, message, data=None):
    if success:
        print(f"✅ {message}")
        if data:
            for key, value in data.items():
                if isinstance(value, dict):
                    print(f"   {key}:")
                    for k, v in value.items():
                        if isinstance(v, list):
                            print(f"      {k}: {len(v)} items")
                            if len(v) > 0 and len(v) <= 3:
                                for item in v:
                                    print(f"         - {item}")
                        else:
                            print(f"      {k}: {v}")
                elif isinstance(value, list):
                    print(f"   {key}: {len(value)} items")
                    if len(value) > 0 and len(value) <= 5:
                        for item in value:
                            if isinstance(item, dict):
                                print(f"      - {item}")
                            else:
                                print(f"      - {item}")
                else:
                    print(f"   {key}: {value}")
    else:
        print(f"❌ {message}")


def test_resume_file(filepath: Path, headers: dict):
    """Test parsing a single resume file"""
    print_section(f"Testing: {filepath.name}")
    
    # Read file
    with open(filepath, 'rb') as f:
        file_content = f.read()
    
    # Determine content type
    if filepath.suffix.lower() == '.pdf':
        content_type = 'application/pdf'
    elif filepath.suffix.lower() in ['.docx', '.doc']:
        content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    else:
        print(f"⚠️  Unsupported file type: {filepath.suffix}")
        return
    
    # Parse resume
    response = requests.post(
        f"{BASE_URL}/resume/parse",
        headers=headers,
        files={"resume": (filepath.name, file_content, content_type)}
    )
    
    if response.status_code == 200:
        result = response.json()
        
        if result["success"]:
            print_result(True, result["message"])
            
            if result["parsed_data"]:
                data = result["parsed_data"]
                
                # Personal Info
                if data.get("personal_info"):
                    print("\n   👤 Personal Info:")
                    for k, v in data["personal_info"].items():
                        if v:
                            print(f"      {k}: {v}")
                
                # Education
                if data.get("education"):
                    print(f"\n   🎓 Education: {len(data['education'])} entries")
                    for edu in data["education"]:
                        print(f"      - {edu.get('degree')} in {edu.get('branch')} from {edu.get('college')}")
                        if edu.get('cgpa'):
                            print(f"        CGPA: {edu['cgpa']}")
                
                # Experience
                if data.get("experience"):
                    print(f"\n   💼 Work Experience: {len(data['experience'])} entries")
                    total_years = data.get('total_experience_years', 0)
                    print(f"      Total Experience: {total_years} years")
                    for exp in data["experience"]:
                        print(f"      - {exp.get('role')} at {exp.get('company')}")
                        print(f"        Duration: {exp.get('duration')}")
                        if exp.get('technologies'):
                            print(f"        Tech: {', '.join(exp['technologies'][:5])}")
                
                # Skills
                if data.get("skills"):
                    print(f"\n   🔧 Skills:")
                    skills = data["skills"]
                    if skills.get("technical"):
                        print(f"      Technical: {', '.join(skills['technical'][:10])}")
                    if skills.get("languages"):
                        print(f"      Languages: {', '.join(skills['languages'][:10])}")
                    if skills.get("frameworks"):
                        print(f"      Frameworks: {', '.join(skills['frameworks'][:10])}")
                    if skills.get("tools"):
                        print(f"      Tools: {', '.join(skills['tools'][:10])}")
                
                # Projects
                if data.get("projects"):
                    print(f"\n   📁 Projects: {len(data['projects'])} projects")
                    for proj in data["projects"][:3]:
                        print(f"      - {proj.get('name')}")
                        if proj.get('technologies'):
                            print(f"        Tech: {', '.join(proj['technologies'])}")
                
                # Certifications
                if data.get("certifications"):
                    print(f"\n   🏆 Certifications: {len(data['certifications'])} certifications")
                    for cert in data["certifications"][:3]:
                        print(f"      - {cert.get('name')}")
                
                # Summary
                if data.get("summary"):
                    print(f"\n   📝 AI Summary:")
                    print(f"      {data['summary']}")
        else:
            print_result(False, result["message"])
    else:
        print_result(False, f"Failed: {response.status_code} - {response.text}")


def main():
    print("\n📄 Testing Resume Parser with REAL FILES")
    print("="*70)
    
    # Create test_resumes directory if it doesn't exist
    TEST_RESUMES_DIR.mkdir(exist_ok=True)
    
    # Check for resume files
    resume_files = list(TEST_RESUMES_DIR.glob("*.pdf")) + list(TEST_RESUMES_DIR.glob("*.docx")) + list(TEST_RESUMES_DIR.glob("*.doc"))
    
    if not resume_files:
        print("\n⚠️  No resume files found!")
        print(f"\n📋 Instructions:")
        print(f"   1. Create a folder: {TEST_RESUMES_DIR.absolute()}")
        print(f"   2. Add your PDF/DOCX resume files to that folder")
        print(f"   3. Run this script again")
        print(f"\n   Example files to add:")
        print(f"      - john_doe_resume.pdf")
        print(f"      - jane_smith_cv.docx")
        print(f"      - my_resume.pdf")
        return
    
    print(f"\n✅ Found {len(resume_files)} resume file(s):")
    for f in resume_files:
        print(f"   - {f.name}")
    
    # Login
    print_section("Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "hr@maverick.com", "password": "hr123"}
    )
    
    if login_response.status_code != 200:
        print_result(False, f"Login failed! {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print_result(True, "Login successful!")
    
    # Test each resume file
    for resume_file in resume_files:
        test_resume_file(resume_file, headers)
    
    print("\n" + "="*70)
    print("🎉 Resume parser testing completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
