"""
Test script for HR Workflow APIs (Day 7)
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

# Test the HR workflow APIs
def test_hr_workflow():
    print("\n🧪 Testing HR Workflow APIs")
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
    
    # 2. Get pending profiles
    print_section("2️⃣  Getting pending profiles...")
    response = requests.get(
        f"{BASE_URL}/hr/pending-profiles?page=1&page_size=10",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_result(True, "Retrieved pending profiles!", {
            "Total pending": data.get("total", 0),
            "Page": f"{data.get('page', 0)}/{data.get('total_pages', 0)}",
            "Count": len(data.get("mavericks", []))
        })
        
        pending_mavericks = data.get("mavericks", [])
        maverick_ids = [m["id"] for m in pending_mavericks[:2]] if pending_mavericks else []
    else:
        print_result(False, f"Failed: {response.status_code}")
        return
    
    if not maverick_ids:
        print("\n⚠️  No pending mavericks found. Run seed script or create some mavericks first.")
        return
    
    # 3. Shortlist a maverick
    print_section("3️⃣  Shortlisting a maverick...")
    response = requests.post(
        f"{BASE_URL}/hr/shortlist/{maverick_ids[0]}",
        headers=headers,
        params={"notes": "Excellent candidate with strong skills"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_result(True, data["message"], {
            "Maverick ID": data["maverick_id"],
            "New Status": data["new_status"]
        })
    else:
        print_result(False, f"Failed: {response.status_code} - {response.text}")
    
    # 4. Bulk shortlist
    if len(maverick_ids) > 1:
        print_section("4️⃣  Bulk shortlisting mavericks...")
        response = requests.post(
            f"{BASE_URL}/hr/bulk-shortlist",
            headers=headers,
            json={
                "maverick_ids": maverick_ids[1:],
                "notes": "Bulk approved - good profiles"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Bulk shortlist completed!", {
                "Success": data["success_count"],
                "Failed": data["failed_count"]
            })
        else:
            print_result(False, f"Failed: {response.status_code}")
    
    # 5. Search pending profiles
    print_section("5️⃣  Searching pending profiles...")
    response = requests.get(
        f"{BASE_URL}/hr/pending-profiles?search=University",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print_result(True, f"Search results: {data.get('total', 0)} found")
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    # 6. Send notifications
    print_section("6️⃣  Sending notification emails...")
    response = requests.post(
        f"{BASE_URL}/hr/send-notifications",
        headers=headers,
        json={"status_filter": "approved"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_result(True, data["message"], {
            "Sent": data["sent_count"],
            "Failed": data["failed_count"]
        })
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    print("\n" + "="*70)
    print("🎉 HR Workflow tests completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_hr_workflow()
