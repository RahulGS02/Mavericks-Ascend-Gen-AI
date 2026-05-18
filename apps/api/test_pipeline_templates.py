"""
Test script for Pipeline Cloning & Templates APIs (Day 9)
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

# Test the Pipeline Cloning & Templates APIs
def test_pipeline_templates():
    print("\n🧪 Testing Pipeline Cloning & Templates APIs")
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
    
    # 2. Get existing pipelines
    print_section("2️⃣  Getting existing pipelines...")
    response = requests.get(f"{BASE_URL}/pipelines/", headers=headers)
    
    if response.status_code == 200:
        pipelines = response.json()["pipelines"]
        if pipelines:
            source_pipeline_id = pipelines[0]["id"]
            print_result(True, f"Found {len(pipelines)} pipelines", {
                "Source Pipeline": pipelines[0]["name"]
            })
        else:
            print_result(False, "No pipelines found. Run test_pipelines.py first.")
            return
    else:
        print_result(False, f"Failed to get pipelines: {response.status_code}")
        return
    
    # 3. Clone a pipeline
    print_section("3️⃣  Cloning a pipeline...")
    response = requests.post(
        f"{BASE_URL}/pipelines/{source_pipeline_id}/clone",
        headers=headers,
        params={
            "new_name": "Cloned Full Stack Program",
            "include_jobs": True
        }
    )
    
    if response.status_code == 201:
        cloned = response.json()
        cloned_id = cloned["id"]
        print_result(True, "Pipeline cloned successfully!", {
            "Cloned ID": cloned_id,
            "Name": cloned["name"],
            "Jobs count": len(cloned.get("jobs", []))
        })
    else:
        print_result(False, f"Failed: {response.status_code} - {response.text}")
        return
    
    # 4. Mark pipeline as template
    print_section("4️⃣  Marking pipeline as template...")
    response = requests.patch(
        f"{BASE_URL}/pipelines/{source_pipeline_id}/mark-template",
        headers=headers,
        params={"is_template": True}
    )
    
    if response.status_code == 200:
        pipeline = response.json()
        print_result(True, "Pipeline marked as template!", {
            "Is Template": pipeline.get("is_template", False)
        })
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    # 5. List pipeline templates
    print_section("5️⃣  Listing all templates...")
    response = requests.get(
        f"{BASE_URL}/pipelines/templates",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_result(True, "Retrieved templates!", {
            "Total templates": data.get("total", 0),
            "Count": len(data.get("pipelines", []))
        })
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    # 6. Create pipeline from template
    print_section("6️⃣  Creating pipeline from template...")
    response = requests.post(
        f"{BASE_URL}/pipelines/templates/{source_pipeline_id}/create-from",
        headers=headers,
        params={
            "new_name": "Q2 2026 Full Stack Training",
            "description": "Full stack training for Q2 batch"
        }
    )
    
    if response.status_code == 201:
        pipeline = response.json()
        print_result(True, "Pipeline created from template!", {
            "Pipeline ID": pipeline["id"],
            "Name": pipeline["name"],
            "Jobs": len(pipeline.get("jobs", []))
        })
    else:
        print_result(False, f"Failed: {response.status_code} - {response.text}")
    
    # 7. Try to modify an ACTIVE pipeline (should warn)
    print_section("7️⃣  Checking if ACTIVE pipeline can be modified...")
    
    # First, update cloned pipeline to ACTIVE
    requests.patch(
        f"{BASE_URL}/pipelines/{cloned_id}",
        headers=headers,
        json={"status": "ACTIVE"}
    )
    
    # Try to modify without force
    response = requests.patch(
        f"{BASE_URL}/pipelines/{cloned_id}/modify-active",
        headers=headers,
        params={"force": False}
    )
    
    if response.status_code == 400:
        print_result(True, "Got expected warning for ACTIVE pipeline modification")
        detail = response.json().get("detail", {})
        if isinstance(detail, dict) and detail.get("warnings"):
            for warning in detail["warnings"]:
                print(f"   ⚠️  {warning}")
    elif response.status_code == 200:
        print_result(True, "Pipeline can be modified (not active)")
    else:
        print_result(False, f"Unexpected response: {response.status_code}")
    
    # 8. Force modify ACTIVE pipeline
    print_section("8️⃣  Force modifying ACTIVE pipeline...")
    response = requests.patch(
        f"{BASE_URL}/pipelines/{cloned_id}/modify-active",
        headers=headers,
        params={"force": True}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_result(True, "Force modification allowed!", {
            "Can modify": data.get("can_modify", False),
            "Message": data.get("message", "")
        })
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    # 9. Search templates
    print_section("9️⃣  Searching templates...")
    response = requests.get(
        f"{BASE_URL}/pipelines/templates?search=Full Stack",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_result(True, f"Search results: {data.get('total', 0)} templates found")
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    print("\n" + "="*70)
    print("🎉 Pipeline Cloning & Templates tests completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_pipeline_templates()
