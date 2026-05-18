"""
Test script for Batch Management APIs (Day 10)
"""
import requests
import json
from datetime import date, timedelta

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

# Test the Batch Management APIs
def test_batch_management():
    print("\n🧪 Testing Batch Management APIs")
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
    
    # 2. Get a pipeline for the batch
    print_section("2️⃣  Getting available pipelines...")
    response = requests.get(f"{BASE_URL}/pipelines/", headers=headers)
    
    if response.status_code == 200 and response.json()["pipelines"]:
        pipeline_id = response.json()["pipelines"][0]["id"]
        print_result(True, f"Found pipeline: {response.json()['pipelines'][0]['name']}")
    else:
        print_result(False, "No pipelines found. Run test_pipelines.py first.")
        return
    
    # 3. Create a batch
    print_section("3️⃣  Creating a new batch...")
    start_date = date.today() + timedelta(days=7)
    end_date = start_date + timedelta(days=90)

    # Use timestamp to ensure unique name
    import time
    timestamp = int(time.time())

    batch_data = {
        "name": f"Q2 2026 Full Stack Batch {timestamp}",
        "description": "Full stack development training batch for Q2",
        "pipeline_id": pipeline_id,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "max_capacity": 20
    }
    
    response = requests.post(
        f"{BASE_URL}/batches/",
        headers=headers,
        json=batch_data
    )
    
    if response.status_code == 201:
        batch = response.json()
        batch_id = batch["id"]
        print_result(True, "Batch created successfully!", {
            "Batch ID": batch_id,
            "Name": batch["name"],
            "Status": batch["status"],
            "Max Capacity": batch["max_capacity"]
        })
    else:
        print_result(False, f"Failed: {response.status_code} - {response.text}")
        return
    
    # 4. List all batches
    print_section("4️⃣  Listing all batches...")
    response = requests.get(f"{BASE_URL}/batches/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print_result(True, "Retrieved batches list!", {
            "Total": data.get("total", 0),
            "Page": f"{data.get('page', 0)}/{data.get('total_pages', 0)}"
        })
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    # 5. Get batch details
    print_section("5️⃣  Getting batch details...")
    response = requests.get(f"{BASE_URL}/batches/{batch_id}", headers=headers)
    
    if response.status_code == 200:
        batch = response.json()
        print_result(True, "Retrieved batch details!", {
            "Name": batch["name"],
            "Enrollment": batch["current_enrollment"],
            "Mavericks": len(batch.get("mavericks", []))
        })
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    # 6. Get available mavericks to assign (only unassigned ones)
    print_section("6️⃣  Getting available mavericks...")
    response = requests.get(
        f"{BASE_URL}/mavericks/?page=1&page_size=10",
        headers=headers
    )

    if response.status_code == 200:
        all_mavericks = response.json().get("mavericks", [])
        # Filter for mavericks without batch assignment
        available_mavericks = [m for m in all_mavericks if m.get("current_batch_id") is None]

        if available_mavericks:
            maverick_ids = [m["id"] for m in available_mavericks[:3]]
            print_result(True, f"Found {len(available_mavericks)} available mavericks")
        else:
            print_result(False, "No available mavericks found (all already assigned)")
            # Still continue the test to show other features
            maverick_ids = []
    else:
        print_result(False, f"Failed: {response.status_code}")
        return
    
    # 7. Assign single maverick
    if maverick_ids and len(maverick_ids) > 0:
        print_section("7️⃣  Assigning single maverick to batch...")
        response = requests.post(
            f"{BASE_URL}/batches/{batch_id}/assign",
            headers=headers,
            json={"maverick_id": maverick_ids[0]}
        )

        if response.status_code == 200:
            result = response.json()
            print_result(True, result["message"])
        else:
            print_result(False, f"Failed: {response.status_code} - {response.text}")
    else:
        print_section("7️⃣  Skipping single assignment (no available mavericks)")
        print_result(True, "Skipped - all mavericks already assigned")

    # 8. Bulk assign mavericks
    if maverick_ids and len(maverick_ids) > 1:
        print_section("8️⃣  Bulk assigning mavericks...")
        response = requests.post(
            f"{BASE_URL}/batches/{batch_id}/bulk-assign",
            headers=headers,
            json={"maverick_ids": maverick_ids[1:]}
        )

        if response.status_code == 200:
            result = response.json()
            print_result(True, "Bulk assignment completed!", {
                "Success": result["success_count"],
                "Failed": result["failed_count"]
            })
        else:
            print_result(False, f"Failed: {response.status_code}")
    else:
        print_section("8️⃣  Skipping bulk assignment (not enough available mavericks)")
        print_result(True, "Skipped - need at least 2 unassigned mavericks")
    
    # 9. Download Excel template
    print_section("9️⃣  Downloading Excel template...")
    response = requests.get(
        f"{BASE_URL}/batches/{batch_id}/template/excel",
        headers=headers
    )
    
    if response.status_code == 200:
        with open("batch_assignment_template.xlsx", "wb") as f:
            f.write(response.content)
        print_result(True, "Excel template downloaded!", {
            "File": "batch_assignment_template.xlsx",
            "Size": f"{len(response.content)} bytes"
        })
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    # 10. Update batch
    print_section("🔟 Updating batch status...")
    response = requests.patch(
        f"{BASE_URL}/batches/{batch_id}",
        headers=headers,
        json={"status": "ACTIVE"}
    )
    
    if response.status_code == 200:
        batch = response.json()
        print_result(True, "Batch updated!", {
            "New Status": batch["status"]
        })
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    print("\n" + "="*70)
    print("🎉 Batch Management tests completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_batch_management()
