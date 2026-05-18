"""
Test script for Pipeline Management APIs (Day 8)
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

# Test the Pipeline APIs
def test_pipeline_management():
    print("\n🧪 Testing Pipeline Management APIs")
    print("="*70)
    
    # 1. Login as HR (pipelines are created by HR)
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
    
    # 2. Create a pipeline
    print_section("2️⃣  Creating a new pipeline...")
    pipeline_data = {
        "name": "Full Stack Development Program",
        "description": "Complete training pipeline for full-stack developers",
        "status": "DRAFT",
        "jobs": [
            {
                "name": "Frontend Training",
                "description": "React, HTML, CSS training",
                "job_type": "TRAINING",
                "sequence_order": 1,
                "duration_days": 14
            },
            {
                "name": "Backend Training",
                "description": "Node.js, Express, PostgreSQL",
                "job_type": "TRAINING",
                "sequence_order": 2,
                "duration_days": 21
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/pipelines/",
        headers=headers,
        json=pipeline_data
    )
    
    if response.status_code == 201:
        pipeline = response.json()
        pipeline_id = pipeline["id"]
        print_result(True, "Pipeline created!", {
            "Pipeline ID": pipeline_id,
            "Name": pipeline["name"],
            "Status": pipeline["status"],
            "Jobs": len(pipeline.get("jobs", []))
        })
    else:
        print_result(False, f"Failed: {response.status_code} - {response.text}")
        return
    
    # 3. List all pipelines
    print_section("3️⃣  Listing all pipelines...")
    response = requests.get(
        f"{BASE_URL}/pipelines/?page=1&page_size=10",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_result(True, "Retrieved pipelines list!", {
            "Total": data.get("total", 0),
            "Page": f"{data.get('page', 0)}/{data.get('total_pages', 0)}",
            "Count": len(data.get("pipelines", []))
        })
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    # 4. Get pipeline by ID
    print_section("4️⃣  Getting pipeline details...")
    response = requests.get(
        f"{BASE_URL}/pipelines/{pipeline_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        pipeline = response.json()
        print_result(True, "Retrieved pipeline details!", {
            "Name": pipeline["name"],
            "Status": pipeline["status"],
            "Jobs count": len(pipeline.get("jobs", []))
        })
        
        # Store first job ID for later tests
        job_id = pipeline["jobs"][0]["id"] if pipeline.get("jobs") else None
    else:
        print_result(False, f"Failed: {response.status_code}")
        return
    
    # 5. Add a new job
    print_section("5️⃣  Adding a new job to pipeline...")
    job_data = {
        "name": "Final Assessment",
        "description": "Comprehensive assessment covering all topics",
        "job_type": "ASSESSMENT",
        "sequence_order": 3,
        "duration_days": 2
    }
    
    response = requests.post(
        f"{BASE_URL}/pipelines/{pipeline_id}/jobs",
        headers=headers,
        json=job_data
    )
    
    if response.status_code == 201:
        job = response.json()
        print_result(True, "Job added!", {
            "Job ID": job["id"],
            "Name": job["name"],
            "Type": job["job_type"],
            "Order": job["sequence_order"]
        })
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    # 6. Update pipeline status
    print_section("6️⃣  Updating pipeline to ACTIVE...")
    response = requests.patch(
        f"{BASE_URL}/pipelines/{pipeline_id}",
        headers=headers,
        json={"status": "ACTIVE"}
    )
    
    if response.status_code == 200:
        pipeline = response.json()
        print_result(True, "Pipeline updated!", {
            "New Status": pipeline["status"]
        })
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    # 7. Update a job
    if job_id:
        print_section("7️⃣  Updating a job...")
        response = requests.patch(
            f"{BASE_URL}/pipelines/{pipeline_id}/jobs/{job_id}",
            headers=headers,
            json={"duration_days": 20, "description": "Updated frontend training"}
        )
        
        if response.status_code == 200:
            print_result(True, "Job updated successfully!")
        else:
            print_result(False, f"Failed: {response.status_code}")
    
    # 8. Search pipelines
    print_section("8️⃣  Searching pipelines...")
    response = requests.get(
        f"{BASE_URL}/pipelines/?search=Full Stack",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_result(True, f"Search results: {data.get('total', 0)} found")
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    print("\n" + "="*70)
    print("🎉 Pipeline Management tests completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_pipeline_management()
