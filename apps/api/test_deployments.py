"""
Test script for Deployment Management APIs (Day 15)
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

# Test the Deployment Management APIs
def test_deployment_management():
    print("\n🧪 Testing Deployment Management APIs")
    print("="*70)
    
    # 1. Login as Manager (using current user)
    print_section("1️⃣  Logging in as Manager...")
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
    
    # 2. Get a maverick for deployment
    print_section("2️⃣  Getting mavericks...")
    response = requests.get(f"{BASE_URL}/mavericks/", headers=headers)
    
    if response.status_code == 200:
        mavericks = response.json().get("mavericks", [])
        if mavericks:
            # Find an available maverick
            available = [m for m in mavericks if m.get("deployment_status") != "DEPLOYED"]
            if available:
                maverick = available[0]
                maverick_id = maverick["id"]
                maverick_name = maverick["name"]
                print_result(True, f"Found available maverick: {maverick_name}")
            else:
                print_result(False, "No available mavericks (all deployed)")
                return
        else:
            print_result(False, "No mavericks found")
            return
    else:
        print_result(False, f"Failed: {response.status_code}")
        return
    
    # 3. Manager: Request deployment
    print_section("3️⃣  Requesting deployment...")
    request_data = {
        "maverick_id": maverick_id,
        "project_name": "ABC Banking Portal",
        "vertical": "Banking",
        "competency": "Full Stack Development",
        "justification": "Urgent requirement for banking domain expert"
    }
    
    response = requests.post(
        f"{BASE_URL}/deployments/requests",
        headers=headers,
        json=request_data
    )
    
    if response.status_code == 201:
        deployment_request = response.json()
        request_id = deployment_request["id"]
        print_result(True, "Deployment request created!", {
            "Request ID": request_id,
            "Status": deployment_request["status"]
        })
    else:
        print_result(False, f"Failed: {response.status_code} - {response.text}")
        return
    
    # 4. HR: List deployment requests
    print_section("4️⃣  Listing deployment requests...")
    response = requests.get(
        f"{BASE_URL}/deployments/requests",
        headers=headers,
        params={"status_filter": "PENDING"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_result(True, "Retrieved deployment requests!", {
            "Total Pending": data["total"]
        })
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    # 5. HR: Approve deployment request
    print_section("5️⃣  Approving deployment request...")
    response = requests.post(
        f"{BASE_URL}/deployments/requests/{request_id}/approve",
        headers=headers,
        json={"notes": "Approved - excellent candidate for banking domain"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print_result(True, f"Request approved!", {
            "Status": result["status"],
            "Approved At": result["approved_at"]
        })
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    # 6. HR: Deploy maverick
    print_section("6️⃣  Deploying maverick...")
    deployment_data = {
        "maverick_id": maverick_id,
        "project_name": "ABC Banking Portal",
        "vertical": "Banking",
        "competency": "Full Stack Development",
        "start_date": date.today().isoformat(),
        "end_date": (date.today() + timedelta(days=180)).isoformat(),
        "role": "Senior Full Stack Developer",
        "manager_name": "John Smith",
        "location": "Mumbai",
        "notes": "Deployed to banking project with high priority"
    }
    
    response = requests.post(
        f"{BASE_URL}/deployments/",
        headers=headers,
        json=deployment_data
    )
    
    if response.status_code == 201:
        deployment = response.json()
        deployment_id = deployment["id"]
        print_result(True, "Maverick deployed successfully!", {
            "Deployment ID": deployment_id,
            "Project": deployment["project_name"],
            "Vertical": deployment["vertical"],
            "Status": deployment["status"]
        })
    else:
        print_result(False, f"Failed: {response.status_code} - {response.text}")
        return
    
    # 7. Get deployment history
    print_section("7️⃣  Getting deployment history...")
    response = requests.get(
        f"{BASE_URL}/deployments/maverick/{maverick_id}/history",
        headers=headers
    )
    
    if response.status_code == 200:
        history = response.json()
        print_result(True, "Retrieved deployment history!", {
            "Total Deployments": history["total_deployments"],
            "Active Deployments": history["active_deployments"],
            "Completed Deployments": history["completed_deployments"]
        })
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    # 8. List all deployments
    print_section("8️⃣  Listing all deployments...")
    response = requests.get(
        f"{BASE_URL}/deployments/",
        headers=headers,
        params={"status_filter": "ACTIVE"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_result(True, "Retrieved deployments list!", {
            "Total Active": data["total"],
            "Page": f"{data['page']}/{data['total_pages']}"
        })
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    print("\n" + "="*70)
    print("🎉 Deployment Management tests completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_deployment_management()
