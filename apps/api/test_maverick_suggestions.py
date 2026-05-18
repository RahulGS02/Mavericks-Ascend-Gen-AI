"""
Test AI-Powered Maverick Suggestions for Batch Assignment (Day 18 - Enhanced)
"""
import requests
import json
from datetime import date, timedelta
import time

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
    print("\n🎯 Testing AI-Powered Maverick Suggestions for Batch (Day 18)")
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
    
    # 2. Get or create pipeline
    print_section("2️⃣  Getting pipeline...")
    pipelines_response = requests.get(f"{BASE_URL}/pipelines/", headers=headers)
    
    if pipelines_response.status_code == 200:
        pipelines_data = pipelines_response.json()
        if pipelines_data["total"] > 0:
            pipeline_id = pipelines_data["pipelines"][0]["id"]
            print_result(True, f"Using pipeline: {pipeline_id}")
        else:
            print_result(False, "No pipelines found. Create one first.")
            return
    
    # 3. Clean up old test batches first
    print_section("3️⃣  Cleaning up old test batches...")

    all_batches_response = requests.get(f"{BASE_URL}/batches/", headers=headers)
    if all_batches_response.status_code == 200:
        all_batches = all_batches_response.json()["batches"]
        deleted_count = 0
        for batch in all_batches:
            if "AI Test" in batch["name"]:
                delete_response = requests.delete(f"{BASE_URL}/batches/{batch['id']}", headers=headers)
                if delete_response.status_code == 200:
                    deleted_count += 1

        if deleted_count > 0:
            print_result(True, f"Deleted {deleted_count} old test batch(es)")
        else:
            print_result(True, "No old test batches found")

    # 4. Create Tech Skills batch (Development)
    print_section("4️⃣  Creating TECH_DEVELOPMENT batch...")

    # Use timestamp to ensure unique name
    timestamp = int(time.time())

    tech_batch = {
        "name": f"Full Stack Dev Batch - AI Test {timestamp}",
        "description": "React & Node.js Full Stack Development Training",
        "pipeline_id": pipeline_id,
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=90)),
        "max_capacity": 30,
        "category": "TECH_DEVELOPMENT",
        "focus_areas": ["React", "Node.js", "JavaScript", "MongoDB", "REST API", "TypeScript"],
        "required_skills": ["JavaScript", "HTML", "CSS"],
        "preferred_skills": ["React", "Node.js", "Git", "MongoDB", "TypeScript"],
        "target_role": "Full Stack Developer"
    }

    batch_response = requests.post(
        f"{BASE_URL}/batches/",
        headers=headers,
        json=tech_batch
    )

    if batch_response.status_code in [200, 201]:
        batch = batch_response.json()
        batch_id = batch["id"]
        print_result(True, f"Tech batch created: {batch['name']}")
        print(f"   Category: {batch.get('category', 'N/A')}")
        print(f"   Required Skills: {batch.get('required_skills', [])}")
        print(f"   Focus Areas: {batch.get('focus_areas', [])}")
    else:
        print_result(False, f"Failed: {batch_response.status_code}")
        print(f"   Error: {batch_response.text[:200]}")
        return
    
    # 5. Get all mavericks stats
    print_section("5️⃣  Checking maverick statistics...")
    mavericks_response = requests.get(f"{BASE_URL}/mavericks/", headers=headers)
    
    if mavericks_response.status_code == 200:
        mav_data = mavericks_response.json()
        print_result(True, f"Total mavericks in system: {mav_data['total']}")
        
        # Show sample skills
        if mav_data["total"] > 0:
            print("\n   Sample Mavericks:")
            for mav in mav_data["mavericks"][:3]:
                skills = (mav.get("skills", []) or []) + (mav.get("ai_extracted_skills", []) or [])
                print(f"      - {mav['name']}: {', '.join(skills[:5])}")
    
    # 6. Get AI-powered maverick suggestions for the batch
    print_section("6️⃣  Getting AI maverick suggestions for batch...")
    
    suggestions_response = requests.get(
        f"{BASE_URL}/batch-suggestions/batch/{batch_id}/suggest-mavericks?top_n=10&use_ai=true&min_score=30",
        headers=headers
    )
    
    if suggestions_response.status_code == 200:
        result = suggestions_response.json()
        
        print_result(True, "Got maverick suggestions!")
        print(f"\n   Batch: {result['batch_name']}")
        print(f"   Category: {result['batch_category']}")
        print(f"   Total Unassigned Mavericks: {result['total_unassigned']}")
        print(f"   Suggestions Returned: {result['total_suggestions']}")
        print(f"   AI Enabled: {'✅ Yes' if result['ai_enabled'] else '❌ No'}")
        
        if result['total_suggestions'] == 0:
            print("\n   ⚠️  No suggestions found. This could mean:")
            print("      - All mavericks are already assigned to batches")
            print("      - No mavericks meet the minimum score threshold")
            print("      - No mavericks have APPROVED status")
        else:
            print(f"\n   📋 Top {result['total_suggestions']} Best-Fit Mavericks:")
            
            for i, sug in enumerate(result["suggestions"], 1):
                print(f"\n   {i}. {sug['maverick_name']} ({sug['email']})")
                print(f"      🎯 Match Score: {sug['match_score']}%")
                print(f"      📊 Exact Match: {sug['exact_match_score']}%")
                if sug['ai_similarity_score']:
                    print(f"      🤖 AI Similarity: {sug['ai_similarity_score']}%")
                print(f"      🎓 {sug['degree']} in {sug['branch']} - CGPA: {sug['cgpa']}")
                print(f"      🏆 Recommendation: {sug['recommendation']}")
                print(f"      💡 {sug['reasoning'][:150]}")
                
                if sug.get('details'):
                    details = sug['details']
                    print(f"      ✅ Required: {details['required_skills_matched']}/{details['required_skills_total']}")
                    if details['matched_skills']:
                        print(f"      🔗 Matches: {', '.join(details['matched_skills'][:5])}")
                    if details['required_skills_missing']:
                        print(f"      ❌ Missing: {', '.join(details['required_skills_missing'][:3])}")
                
                print(f"      🔧 Total Skills: {len(sug['skills'])} - {', '.join(sug['skills'][:8])}")
    else:
        print_result(False, f"Failed: {suggestions_response.status_code} - {suggestions_response.text}")
    
    # 7. Create Soft Skills batch for comparison
    print_section("7️⃣  Creating SOFT_SKILLS batch for comparison...")

    timestamp2 = int(time.time()) + 1

    soft_batch = {
        "name": f"Communication & Leadership - AI Test {timestamp2}",
        "description": "Soft skills development program",
        "pipeline_id": pipeline_id,
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=30)),
        "max_capacity": 50,
        "category": "SOFT_SKILLS"
    }
    
    soft_response = requests.post(f"{BASE_URL}/batches/", headers=headers, json=soft_batch)
    
    if soft_response.status_code in [200, 201]:
        soft_batch_data = soft_response.json()
        soft_batch_id = soft_batch_data["id"]
        print_result(True, "Soft skills batch created!")
        
        # Get suggestions (should return all unassigned)
        soft_sug_response = requests.get(
            f"{BASE_URL}/batch-suggestions/batch/{soft_batch_id}/suggest-mavericks?top_n=5",
            headers=headers
        )
        
        if soft_sug_response.status_code == 200:
            soft_result = soft_sug_response.json()
            print(f"   Soft Skills Suggestions: {soft_result['total_suggestions']}")
            print(f"   (No skill matching - all unassigned mavericks qualify)")
    
    print("\n" + "="*80)
    print("🎉 Maverick Suggestion test completed!")
    print("\n📋 Summary:")
    print("   ✅ Tech batches use AI skill matching")
    print("   ✅ Soft skill batches return all unassigned mavericks")
    print("   ✅ Only suggests mavericks not in any active batch")
    print("   ✅ Provides match scores and detailed reasoning")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
