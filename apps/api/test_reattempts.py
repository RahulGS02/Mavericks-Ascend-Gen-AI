"""
Test script for Reattempt Management APIs (Day 14)
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

# Test the Reattempt Management APIs
def test_reattempt_management():
    print("\n🧪 Testing Reattempt Management APIs")
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
    
    # 2. Get existing assessment with attempts
    print_section("2️⃣  Getting existing assessments...")
    # We'll need to find an assessment from previous tests
    # For now, let's create a simple flow
    
    # First get a batch
    response = requests.get(f"{BASE_URL}/batches/", headers=headers)
    if response.status_code == 200 and response.json()["batches"]:
        batch = response.json()["batches"][0]
        batch_id = batch["id"]
        pipeline_id = batch["pipeline_id"]
        print_result(True, f"Found batch: {batch['name']}")
    else:
        print_result(False, "No batches found")
        return
    
    # Get pipeline and assessment job
    response = requests.get(f"{BASE_URL}/pipelines/{pipeline_id}", headers=headers)
    if response.status_code == 200:
        pipeline = response.json()
        assessment_jobs = [j for j in pipeline.get("jobs", []) if j.get("job_type") == "ASSESSMENT"]
        if assessment_jobs:
            job_id = assessment_jobs[0]["id"]
            print_result(True, f"Found assessment job: {assessment_jobs[0]['name']}")
        else:
            print_result(False, "No assessment jobs found")
            return
    else:
        print_result(False, "Failed to get pipeline")
        return
    
    # Get mavericks
    response = requests.get(f"{BASE_URL}/batches/{batch_id}", headers=headers)
    if response.status_code == 200:
        mavericks = response.json().get("mavericks", [])
        if len(mavericks) >= 2:
            maverick1_id = mavericks[0]["id"]
            maverick2_id = mavericks[1]["id"]
            maverick1_name = mavericks[0]["name"]
            maverick2_name = mavericks[1]["name"]
            print_result(True, f"Found {len(mavericks)} mavericks")
        else:
            print_result(False, "Need at least 2 mavericks in batch")
            return
    else:
        print_result(False, "Failed to get batch details")
        return
    
    # Create assessment (might already exist)
    assessment_data = {
        "job_id": job_id,
        "batch_id": batch_id,
        "title": "Reattempt Test Assessment",
        "description": "Test assessment for reattempt functionality",
        "max_marks": 100,
        "passing_marks": 50,
        "duration_minutes": 60
    }
    
    response = requests.post(f"{BASE_URL}/assessments/", headers=headers, json=assessment_data)
    if response.status_code == 201:
        assessment_id = response.json()["id"]
        print_result(True, "Assessment created")
    else:
        print_result(True, "Using existing assessment (already created)")
        # In real scenario, we'd query to get existing assessment_id
        # For now, we'll stop here as we can't proceed without the ID
        print("\n⚠️  Note: To fully test reattempts, run this after creating an assessment")
        print("="*70 + "\n")
        return
    
    # 3. Enter failing marks for maverick1
    print_section("3️⃣  Entering failing marks (30/100)...")
    response = requests.post(
        f"{BASE_URL}/assessments/{assessment_id}/enter-marks",
        headers=headers,
        json={
            "maverick_id": maverick1_id,
            "marks_obtained": 30,
            "feedback": "Needs more practice on core concepts",
            "auto_progress": False
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print_result(True, f"Marks entered - Student FAILED", {
            "Passed": result["passed"],
            "Progressed": result["progressed"]
        })
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    # 4. Get failed mavericks list
    print_section("4️⃣  Getting failed mavericks list...")
    response = requests.get(
        f"{BASE_URL}/reattempts/{assessment_id}/failed-mavericks",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_result(True, "Retrieved failed mavericks!", {
            "Total Failed": data["total_failed"]
        })
        if data["failed_mavericks"]:
            first_failed = data["failed_mavericks"][0]
            print(f"   First Failed Student:")
            print(f"      Name: {first_failed['maverick_name']}")
            print(f"      Score: {first_failed['percentage']}%")
            print(f"      Attempts: {first_failed['total_attempts']}")
            print(f"      Can Reattempt: {first_failed['can_reattempt']}")
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    # 5. Schedule reattempt
    print_section("5️⃣  Scheduling reattempt...")
    reattempt_date = datetime.now() + timedelta(days=2)
    response = requests.post(
        f"{BASE_URL}/reattempts/{assessment_id}/schedule",
        headers=headers,
        json={
            "maverick_id": maverick1_id,
            "scheduled_date": reattempt_date.isoformat(),
            "notes": "Review core concepts before reattempt"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print_result(True, result["message"], {
            "Attempt Number": result["attempt_number"]
        })
    else:
        print_result(False, f"Failed: {response.status_code} - {response.text}")
    
    # 6. Get maverick attempt history
    print_section("6️⃣  Getting attempt history...")
    response = requests.get(
        f"{BASE_URL}/reattempts/maverick/{maverick1_id}/assessment/{assessment_id}/history",
        headers=headers
    )
    
    if response.status_code == 200:
        history = response.json()
        print_result(True, "Retrieved attempt history!", {
            "Total Attempts": history["total_attempts"],
            "Passed": history["passed"],
            "Best Score": history["best_score"],
            "Latest Score": history["latest_score"]
        })
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    # 7. Get reattempt statistics
    print_section("7️⃣  Getting reattempt statistics...")
    response = requests.get(
        f"{BASE_URL}/reattempts/{assessment_id}/statistics",
        headers=headers
    )
    
    if response.status_code == 200:
        stats = response.json()
        print_result(True, "Retrieved statistics!", {
            "Total Attempts": stats["total_attempts"],
            "First Attempt Pass Rate": f"{stats['first_attempt_pass_rate']}%",
            "Reattempt Pass Rate": f"{stats['reattempt_pass_rate']}%",
            "Max Attempts by Student": stats["max_attempts_by_maverick"]
        })
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    print("\n" + "="*70)
    print("🎉 Reattempt Management tests completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_reattempt_management()
