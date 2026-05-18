"""
Test script for Assessment & Marks Entry APIs (Day 13)
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api/v1"

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

# Test the Assessment & Marks Entry APIs
def test_assessment_management():
    print("\n🧪 Testing Assessment & Marks Entry APIs")
    print("="*70)
    
    # 1. Login as HR
    print_section("1️⃣  Logging in as HR...")
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
    
    # 2. Get a batch with an ASSESSMENT job
    print_section("2️⃣  Getting batch and assessment job...")
    response = requests.get(f"{BASE_URL}/batches/", headers=headers)
    
    if response.status_code == 200 and response.json()["batches"]:
        batch = response.json()["batches"][0]
        batch_id = batch["id"]
        pipeline_id = batch["pipeline_id"]
        
        # Get pipeline jobs
        response = requests.get(f"{BASE_URL}/pipelines/{pipeline_id}", headers=headers)
        if response.status_code == 200:
            pipeline = response.json()
            # Find an ASSESSMENT type job
            assessment_jobs = [j for j in pipeline.get("jobs", []) if j.get("job_type") == "ASSESSMENT"]
            if assessment_jobs:
                job_id = assessment_jobs[0]["id"]
                job_name = assessment_jobs[0]["name"]
                print_result(True, f"Found assessment job: {job_name}")
            else:
                print_result(False, "No ASSESSMENT type jobs in pipeline")
                return
        else:
            print_result(False, "Failed to get pipeline")
            return
    else:
        print_result(False, "No batches found")
        return
    
    # 3. Create assessment job
    print_section("3️⃣  Creating assessment job...")
    assessment_data = {
        "job_id": job_id,
        "batch_id": batch_id,
        "title": "React Final Assessment",
        "description": "Comprehensive test on React concepts",
        "max_marks": 100,
        "passing_marks": 40,
        "duration_minutes": 120,
        "scheduled_date": (datetime.now() + timedelta(days=2)).isoformat()
    }
    
    response = requests.post(
        f"{BASE_URL}/assessments/",
        headers=headers,
        json=assessment_data
    )
    
    if response.status_code == 201:
        assessment = response.json()
        assessment_id = assessment["id"]
        print_result(True, "Assessment created!", {
            "Assessment ID": assessment_id,
            "Title": assessment["title"],
            "Max Marks": assessment["max_marks"],
            "Passing Marks": assessment["passing_marks"]
        })
    elif response.status_code == 400 and "already exists" in response.text:
        # Get existing assessment
        print_result(True, "Assessment already exists (from previous run)")
        # For now, we'll skip further tests as we need the assessment_id
        # In production, you'd query to get the existing assessment_id
        return
    else:
        print_result(False, f"Failed: {response.status_code} - {response.text}")
        return
    
    # 4. Get mavericks in the batch
    print_section("4️⃣  Getting mavericks in batch...")
    response = requests.get(f"{BASE_URL}/batches/{batch_id}", headers=headers)
    
    if response.status_code == 200:
        batch_details = response.json()
        mavericks = batch_details.get("mavericks", [])
        if mavericks:
            maverick_id = mavericks[0]["id"]
            maverick_name = mavericks[0]["name"]
            print_result(True, f"Found {len(mavericks)} mavericks")
        else:
            print_result(False, "No mavericks in batch")
            return
    else:
        print_result(False, f"Failed: {response.status_code}")
        return
    
    # 5. Enter marks manually (PASS case)
    print_section("5️⃣  Entering marks manually (PASS - 75/100)...")
    response = requests.post(
        f"{BASE_URL}/assessments/{assessment_id}/enter-marks",
        headers=headers,
        json={
            "maverick_id": maverick_id,
            "marks_obtained": 75,
            "feedback": "Excellent understanding of React hooks!",
            "auto_progress": True
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print_result(True, result["message"], {
            "Passed": result["passed"],
            "Progressed": result["progressed"]
        })
    else:
        print_result(False, f"Failed: {response.status_code} - {response.text}")
    
    # 6. Download marks template
    print_section("6️⃣  Downloading Excel marks template...")
    response = requests.get(
        f"{BASE_URL}/assessments/{assessment_id}/template/excel",
        headers=headers
    )
    
    if response.status_code == 200:
        with open("marks_template.xlsx", "wb") as f:
            f.write(response.content)
        print_result(True, "Excel template downloaded!", {
            "File": "marks_template.xlsx",
            "Size": f"{len(response.content)} bytes"
        })
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    # 7. Get assessment history
    print_section("7️⃣  Getting assessment history...")
    response = requests.get(
        f"{BASE_URL}/assessments/{assessment_id}/history",
        headers=headers
    )
    
    if response.status_code == 200:
        history = response.json()
        print_result(True, "Retrieved assessment history!", {
            "Total Attempts": history["total_attempts"],
            "Assessment": history["assessment_title"]
        })
        
        if history["attempts"]:
            first_attempt = history["attempts"][0]
            print(f"   Last Attempt:")
            print(f"      Student: {first_attempt['maverick_name']}")
            print(f"      Marks: {first_attempt['marks_obtained']}/{first_attempt['max_marks']}")
            print(f"      Result: {'PASS' if first_attempt['passed'] else 'FAIL'}")
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    print("\n" + "="*70)
    print("🎉 Assessment & Marks Entry tests completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_assessment_management()
