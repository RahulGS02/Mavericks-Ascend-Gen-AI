"""
Test script for Training Management APIs (Day 12)
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

# Test the Training Management APIs
def test_training_management():
    print("\n🧪 Testing Training Management APIs")
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
    
    # 2. Get a batch
    print_section("2️⃣  Getting batches...")
    response = requests.get(f"{BASE_URL}/batches/", headers=headers)
    
    if response.status_code == 200 and response.json()["batches"]:
        batch = response.json()["batches"][0]
        batch_id = batch["id"]
        pipeline_id = batch["pipeline_id"]
        print_result(True, f"Found batch: {batch['name']}")
    else:
        print_result(False, "No batches found. Run test_batches.py first.")
        return
    
    # 3. Get a job from the pipeline
    print_section("3️⃣  Getting pipeline jobs...")
    response = requests.get(f"{BASE_URL}/pipelines/{pipeline_id}", headers=headers)
    
    if response.status_code == 200:
        pipeline = response.json()
        if pipeline.get("jobs"):
            job_id = pipeline["jobs"][0]["id"]
            job_name = pipeline["jobs"][0]["name"]
            print_result(True, f"Found job: {job_name}")
        else:
            print_result(False, "No jobs in pipeline")
            return
    else:
        print_result(False, f"Failed: {response.status_code}")
        return
    
    # 4. Get trainer
    print_section("4️⃣  Getting trainer user...")
    # Assuming trainer exists from seed data
    trainer_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "trainer@maverick.com", "password": "trainer123"}
    )
    if trainer_response.status_code == 200:
        trainer_token = trainer_response.json()["access_token"]
        trainer_headers = {"Authorization": f"Bearer {trainer_token}"}
        print_result(True, "Trainer login successful!")
        # Get trainer ID from their profile (we'll use a workaround - assign without trainer first)
        has_trainer = True
    else:
        has_trainer = False
        print_result(True, "No trainer available, will create session without trainer")
    
    # 5. Schedule a training session
    print_section("5️⃣  Scheduling training session...")
    scheduled_time = datetime.now() + timedelta(days=3, hours=2)
    
    session_data = {
        "batch_id": batch_id,
        "job_id": job_id,
        "title": "React Fundamentals Workshop",
        "description": "Comprehensive introduction to React components and hooks",
        "scheduled_date": scheduled_time.isoformat(),
        "duration_minutes": 180,
        "location": "Online",
        "meeting_link": "https://meet.google.com/abc-defg-hij"
    }
    
    response = requests.post(
        f"{BASE_URL}/training/",
        headers=headers,
        json=session_data
    )
    
    if response.status_code == 201:
        session = response.json()
        session_id = session["id"]
        print_result(True, "Training session scheduled!", {
            "Session ID": session_id,
            "Title": session["title"],
            "Date": session["scheduled_date"],
            "Duration": f"{session['duration_minutes']} min"
        })
    else:
        print_result(False, f"Failed: {response.status_code} - {response.text}")
        return
    
    # 6. List training sessions by batch
    print_section("6️⃣  Listing training sessions for batch...")
    response = requests.get(
        f"{BASE_URL}/training/batch/{batch_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_result(True, "Retrieved training sessions!", {
            "Total Sessions": data["total"],
            "Sessions on page": len(data["sessions"])
        })
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    # 7. Mark training as complete (as trainer)
    if has_trainer:
        print_section("7️⃣  Marking training as complete (as trainer)...")
        response = requests.post(
            f"{BASE_URL}/training/{session_id}/complete",
            headers=trainer_headers,
            json={
                "completion_notes": "Great session! All topics covered.",
                "attendance_count": 15,
                "actual_duration_minutes": 175
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print_result(True, result["message"])
        else:
            print_result(False, f"Failed: {response.status_code} - {response.text}")
    else:
        print_section("7️⃣  Skipping mark complete (no trainer)")
        print_result(True, "Skipped - no trainer available")
    
    # 8. Get training calendar
    print_section("8️⃣  Getting training calendar...")
    now = datetime.now()
    response = requests.get(
        f"{BASE_URL}/training/calendar",
        headers=headers,
        params={
            "year": now.year,
            "month": now.month,
            "batch_id": batch_id
        }
    )
    
    if response.status_code == 200:
        calendar = response.json()
        print_result(True, "Retrieved training calendar!", {
            "Month": f"{calendar['month']}/{calendar['year']}",
            "Total Sessions": calendar["total_sessions"],
            "Days with sessions": len(calendar["days"])
        })
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    print("\n" + "="*70)
    print("🎉 Training Management tests completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_training_management()
