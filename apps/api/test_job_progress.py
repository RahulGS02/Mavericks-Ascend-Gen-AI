"""
Test script for Job Progress Tracking APIs (Day 11)
"""
import requests
import json

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

# Test the Job Progress Tracking APIs
def test_job_progress():
    print("\n🧪 Testing Job Progress Tracking APIs")
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
    
    # 2. Get a batch with mavericks
    print_section("2️⃣  Getting batches...")
    response = requests.get(f"{BASE_URL}/batches/", headers=headers)
    
    if response.status_code == 200 and response.json()["batches"]:
        batch = response.json()["batches"][0]
        batch_id = batch["id"]
        print_result(True, f"Found batch: {batch['name']}")
    else:
        print_result(False, "No batches found. Run test_batches.py first.")
        return
    
    # 3. Get batch details to find mavericks
    print_section("3️⃣  Getting mavericks in batch...")
    response = requests.get(f"{BASE_URL}/batches/{batch_id}", headers=headers)
    
    if response.status_code == 200:
        batch_details = response.json()
        mavericks = batch_details.get("mavericks", [])
        if mavericks:
            maverick_id = mavericks[0]["id"]
            print_result(True, f"Found {len(mavericks)} mavericks", {
                "First Maverick": mavericks[0]["name"]
            })
        else:
            print_result(False, "No mavericks in batch. Assign mavericks first.")
            return
    else:
        print_result(False, f"Failed: {response.status_code}")
        return
    
    # 4. Initialize job progress
    print_section("4️⃣  Initializing job progress...")
    response = requests.post(
        f"{BASE_URL}/job-progress/initialize",
        headers=headers,
        json={
            "maverick_id": maverick_id,
            "batch_id": batch_id
        }
    )
    
    if response.status_code in [200, 201]:
        result = response.json()
        print_result(True, result["message"], {
            "Jobs Created": result["total_jobs_created"]
        })
    elif response.status_code == 400 and "already initialized" in response.text:
        print_result(True, "Progress already initialized (from previous run)")
    else:
        print_result(False, f"Failed: {response.status_code} - {response.text}")
    
    # 5. Get maverick progress
    print_section("5️⃣  Getting maverick progress...")
    response = requests.get(
        f"{BASE_URL}/job-progress/maverick/{maverick_id}/batch/{batch_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        progress = response.json()
        print_result(True, "Retrieved progress!", {
            "Total Jobs": progress["total_jobs"],
            "Completed": progress["completed_jobs"],
            "In Progress": progress["in_progress_jobs"],
            "Pending": progress["pending_jobs"],
            "Overall Completion": f"{progress['overall_completion']}%"
        })
        
        # Store first job progress ID for updates
        if progress["job_progress"]:
            progress_id = progress["job_progress"][0]["id"]
            job_name = progress["job_progress"][0]["job_name"]
    else:
        print_result(False, f"Failed: {response.status_code}")
        return
    
    # 6. Update job progress
    if progress_id:
        print_section("6️⃣  Updating job progress to IN_PROGRESS...")
        response = requests.patch(
            f"{BASE_URL}/job-progress/{progress_id}",
            headers=headers,
            json={
                "status": "IN_PROGRESS",
                "completion_percentage": 50,
                "notes": "Working on module 1"
            }
        )
        
        if response.status_code == 200:
            updated = response.json()
            print_result(True, f"Updated job: {job_name}", {
                "Status": updated["status"],
                "Completion": f"{updated['completion_percentage']}%"
            })
        else:
            print_result(False, f"Failed: {response.status_code}")
    
    # 7. Complete a job
    if progress_id:
        print_section("7️⃣  Marking job as COMPLETED...")
        response = requests.patch(
            f"{BASE_URL}/job-progress/{progress_id}",
            headers=headers,
            json={
                "status": "COMPLETED",
                "completion_percentage": 100,
                "score": 95.5,
                "notes": "Excellent performance!"
            }
        )
        
        if response.status_code == 200:
            updated = response.json()
            print_result(True, "Job completed!", {
                "Score": updated.get("score", "N/A")
            })
        else:
            print_result(False, f"Failed: {response.status_code}")
    
    # 8. Get batch progress
    print_section("8️⃣  Getting batch overall progress...")
    response = requests.get(
        f"{BASE_URL}/job-progress/batch/{batch_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        batch_progress = response.json()
        print_result(True, "Retrieved batch progress!", {
            "Total Mavericks": batch_progress["total_mavericks"],
            "Total Jobs": batch_progress["total_jobs"],
            "Overall Completion": f"{batch_progress['overall_completion']}%"
        })
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    print("\n" + "="*70)
    print("🎉 Job Progress Tracking tests completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_job_progress()
