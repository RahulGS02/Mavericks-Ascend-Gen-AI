"""
Test AI-Powered Batch Suggestions (Day 18)
"""
import requests
import json
from datetime import date, timedelta

BASE_URL = "http://localhost:8000/api/v1"

def print_section(title):
    print(f"\n{'='*80}")
    print(f"\n{title}")
    print(f"\n{'-'*80}")

def print_result(success, message):
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")


def main():
    print("\n🎯 Testing AI-Powered Batch Suggestions (Day 18)")
    print("="*80)
    
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
    
    # 2. Create Pipeline (if not exists)
    print_section("2️⃣  Creating test pipeline...")
    pipeline_response = requests.post(
        f"{BASE_URL}/pipelines/",
        headers=headers,
        json={
            "name": "Full Stack Development Pipeline",
            "description": "Complete full stack developer training"
        }
    )
    
    if pipeline_response.status_code in [200, 201]:
        pipeline_id = pipeline_response.json()["id"]
        print_result(True, f"Pipeline created: {pipeline_id}")
    elif pipeline_response.status_code == 400 and "already exists" in pipeline_response.text:
        # Get existing pipeline
        pipelines = requests.get(f"{BASE_URL}/pipelines/", headers=headers).json()
        pipeline_id = pipelines["pipelines"][0]["id"]
        print_result(True, f"Using existing pipeline: {pipeline_id}")
    else:
        print_result(False, f"Pipeline creation failed: {pipeline_response.text}")
        return
    
    # 3. First, clean up old test batches if they exist
    print_section("3️⃣  Cleaning up old test batches...")
    all_batches_response = requests.get(f"{BASE_URL}/batches/", headers=headers)
    if all_batches_response.status_code == 200:
        all_batches = all_batches_response.json()["batches"]
        for batch in all_batches:
            if batch["name"].startswith("Full Stack - React") or \
               batch["name"].startswith("Python Data Science") or \
               batch["name"].startswith("DevOps Engineering"):
                # Delete old test batch
                requests.delete(f"{BASE_URL}/batches/{batch['id']}", headers=headers)
                print(f"   Deleted old batch: {batch['name']}")

    # 4. Create batches with focus areas
    print_section("4️⃣  Creating batches with AI matching fields...")

    batches_to_create = [
        {
            "name": "Full Stack - React & Node.js Batch",
            "description": "Intensive training for React and Node.js developers",
            "pipeline_id": pipeline_id,
            "start_date": str(date.today()),
            "end_date": str(date.today() + timedelta(days=90)),
            "max_capacity": 30,
            "focus_areas": ["React", "Node.js", "JavaScript", "MongoDB", "REST API"],
            "required_skills": ["JavaScript", "HTML", "CSS"],
            "preferred_skills": ["React", "Node.js", "Git", "MongoDB"],
            "target_role": "Full Stack Developer"
        },
        {
            "name": "Python Data Science Batch",
            "description": "Advanced data science training with Python",
            "pipeline_id": pipeline_id,
            "start_date": str(date.today()),
            "end_date": str(date.today() + timedelta(days=90)),
            "max_capacity": 25,
            "focus_areas": ["Python", "Machine Learning", "Data Analysis", "TensorFlow", "Pandas"],
            "required_skills": ["Python", "Statistics", "SQL"],
            "preferred_skills": ["Machine Learning", "TensorFlow", "Pandas", "NumPy"],
            "target_role": "Data Scientist"
        },
        {
            "name": "DevOps Engineering Batch",
            "description": "DevOps and cloud infrastructure training",
            "pipeline_id": pipeline_id,
            "start_date": str(date.today()),
            "end_date": str(date.today() + timedelta(days=90)),
            "max_capacity": 20,
            "focus_areas": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux"],
            "required_skills": ["Linux", "Networking", "Scripting"],
            "preferred_skills": ["Docker", "Kubernetes", "AWS", "Jenkins"],
            "target_role": "DevOps Engineer"
        }
    ]
    
    created_batches = []
    for batch_data in batches_to_create:
        response = requests.post(
            f"{BASE_URL}/batches/",
            headers=headers,
            json=batch_data
        )
        
        if response.status_code in [200, 201]:
            batch = response.json()
            created_batches.append(batch)
            print_result(True, f"Created batch: {batch['name']}")
        elif "already exists" in response.text:
            print_result(True, f"Batch already exists: {batch_data['name']}")
        else:
            print_result(False, f"Failed to create {batch_data['name']}: {response.text}")

    # Verify batches were created with proper fields
    print_section("5️⃣  Verifying batch fields...")
    verify_response = requests.get(f"{BASE_URL}/batches/", headers=headers)
    if verify_response.status_code == 200:
        all_batches = verify_response.json()["batches"]
        for batch in all_batches:
            if batch["name"] in [b["name"] for b in batches_to_create]:
                print(f"\n   ✅ {batch['name']}")
                print(f"      Focus Areas: {batch.get('focus_areas', 'NOT SET')}")
                print(f"      Required Skills: {batch.get('required_skills', 'NOT SET')}")
                print(f"      Target Role: {batch.get('target_role', 'NOT SET')}")

    # 6. Get a maverick to test
    print_section("6️⃣  Getting test maverick...")
    mavericks_response = requests.get(f"{BASE_URL}/mavericks/", headers=headers)
    
    if mavericks_response.status_code == 200:
        mavericks_data = mavericks_response.json()
        if mavericks_data["total"] > 0:
            test_maverick = mavericks_data["mavericks"][0]
            maverick_id = test_maverick["id"]
            maverick_name = test_maverick["name"]
            maverick_skills = test_maverick.get("skills", []) + test_maverick.get("ai_extracted_skills", [])
            
            print_result(True, f"Testing with maverick: {maverick_name}")
            print(f"   Skills: {', '.join(maverick_skills[:10])}")
        else:
            print_result(False, "No mavericks found. Create a maverick profile first.")
            return
    else:
        print_result(False, "Failed to get mavericks")
        return

    # 7. Get AI batch suggestions
    print_section("7️⃣  Getting AI batch suggestions...")
    suggestions_response = requests.get(
        f"{BASE_URL}/batch-suggestions/maverick/{maverick_id}?top_n=3&use_ai=true",
        headers=headers
    )
    
    if suggestions_response.status_code == 200:
        result = suggestions_response.json()
        print_result(True, f"Got {result['total_suggestions']} suggestions for {result['maverick_name']}")
        
        print(f"\n   AI Enabled: {'✅ Yes' if result['ai_enabled'] else '❌ No'}")
        
        for i, suggestion in enumerate(result["suggestions"], 1):
            print(f"\n   {i}. {suggestion['batch_name']}")
            print(f"      🎯 Match Score: {suggestion['match_score']}%")
            print(f"      📊 Exact Match: {suggestion['exact_match_score']}%")
            if suggestion['ai_similarity_score']:
                print(f"      🤖 AI Similarity: {suggestion['ai_similarity_score']}%")
            print(f"      🎓 Target Role: {suggestion['target_role'] or 'N/A'}")
            print(f"      💡 Recommendation: {suggestion['recommendation']}")
            print(f"      📝 Reasoning: {suggestion['reasoning'][:200]}")
            
            details = suggestion['details']
            print(f"      ✅ Required Skills: {details['required_skills_matched']}/{details['required_skills_total']}")
            if details['required_skills_missing']:
                print(f"      ❌ Missing: {', '.join(details['required_skills_missing'][:5])}")
            if details['matched_skills']:
                print(f"      🔗 Matched: {', '.join(details['matched_skills'][:5])}")
    else:
        print_result(False, f"Failed: {suggestions_response.status_code} - {suggestions_response.text}")
    
    print("\n" + "="*80)
    print("🎉 Batch Suggestion test completed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
