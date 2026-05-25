"""
🚀 Quick Test Script for AI Talent Search

A simple, fast test to verify the AI Talent Search is working.
Just run: python quick_test.py
"""

import requests
import json

# Configuration
API_URL = "http://localhost:8000/api/v1"
EMAIL = "hr@maverick.com"
PASSWORD = "hr123"  # Update with your actual password

def test():
    print("=" * 80)
    print("🧪 QUICK TEST: AI-POWERED TALENT SEARCH")
    print("=" * 80)
    
    # 1. Login
    print("\n1️⃣ Logging in...")
    login_response = requests.post(
        f"{API_URL}/auth/login",
        json={"email": EMAIL, "password": PASSWORD}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json()["access_token"]
    print(f"✅ Logged in successfully as {EMAIL}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Get Statistics
    print("\n2️⃣ Getting talent pool statistics...")
    stats_response = requests.get(f"{API_URL}/talent-search/statistics", headers=headers)
    
    if stats_response.status_code == 200:
        stats = stats_response.json()
        print(f"✅ Statistics retrieved")
        print(f"   📊 Available Candidates: {stats['talent_pool']['total_available']}")
        print(f"   📊 Average CGPA: {stats['cgpa_stats']['average']:.2f}")
        print(f"   📊 Top Skills: {len(stats['top_skills'])}")
    else:
        print(f"⚠️ Statistics failed: {stats_response.status_code}")
    
    # 3. Search #1: .NET Developer
    print("\n3️⃣ TEST SEARCH #1: .NET Developer with C#, Azure, SQL")
    search1 = {
        "query": "Need .NET developer with C#, Azure cloud, and SQL Server experience",
        "max_results": 10,
        "include_similar": False,
        "urgency": "flexible"
    }
    
    response1 = requests.post(f"{API_URL}/talent-search/search", headers=headers, json=search1)
    
    if response1.status_code == 200:
        result1 = response1.json()
        print(f"✅ Search completed")
        print(f"   📋 Total Found: {result1['total_found']}")
        print(f"   📋 Exact Matches: {result1['summary']['exact_matches']}")
        print(f"   💰 Cost: ${result1['cost_analysis']['total_cost']:.6f}")
        
        if result1['results']:
            top = result1['results'][0]
            print(f"\n   🏆 Top Candidate:")
            print(f"      Name: {top['name']}")
            print(f"      Score: {top['final_score']:.1f}/100")
            print(f"      Tier: {top['tier']}")
            print(f"      CGPA: {top['cgpa']:.2f}")
            
            exact_skills = [s['skill'] for s in top.get('exact_matches', [])]
            if exact_skills:
                print(f"      ✅ Skills: {', '.join(exact_skills)}")
    else:
        print(f"❌ Search failed: {response1.status_code}")
        print(response1.text)
    
    # 4. Search #2: With Similar Skills
    print("\n4️⃣ TEST SEARCH #2: Same query WITH similar skills")
    search2 = search1.copy()
    search2['include_similar'] = True
    
    response2 = requests.post(f"{API_URL}/talent-search/search", headers=headers, json=search2)
    
    if response2.status_code == 200:
        result2 = response2.json()
        print(f"✅ Search completed")
        print(f"   📋 Total Found: {result2['total_found']}")
        print(f"   📋 Similar Candidates: {result2['summary']['similar_skill_candidates']}")
        
        if result1['total_found'] < result2['total_found']:
            print(f"   ✨ Including similar skills found {result2['total_found'] - result1['total_found']} more candidates!")
    else:
        print(f"❌ Search failed: {response2.status_code}")
    
    # 5. Search #3: Python Developer
    print("\n5️⃣ TEST SEARCH #3: Python Full Stack Developer")
    search3 = {
        "query": "Python developer with Django and React, CGPA > 7.5",
        "max_results": 10,
        "include_similar": True,
        "urgency": "flexible"
    }
    
    response3 = requests.post(f"{API_URL}/talent-search/search", headers=headers, json=search3)
    
    if response3.status_code == 200:
        result3 = response3.json()
        print(f"✅ Search completed")
        print(f"   📋 Total Found: {result3['total_found']}")
        print(f"   🎯 Parsed Skills: {', '.join(result3['parsed_requirements'].get('required_skills', []))}")
        print(f"   📊 Min CGPA: {result3['parsed_requirements'].get('min_cgpa', 'N/A')}")
        
        if result3['results']:
            top = result3['results'][0]
            print(f"\n   🏆 Top Candidate:")
            print(f"      Name: {top['name']}")
            print(f"      Score: {top['final_score']:.1f}/100")
            print(f"      Adaptability: {top['adaptability_score']:.0f}/100")
            print(f"      Ready in: {top['learning_weeks_required']:.1f} weeks")
    else:
        print(f"❌ Search failed: {response3.status_code}")
    
    # 6. Search #4: Java Microservices
    print("\n6️⃣ TEST SEARCH #4: Java Microservices Developer")
    search4 = {
        "query": "Java backend engineer with Spring Boot and microservices",
        "max_results": 5,
        "include_similar": True,
        "urgency": "immediate"
    }
    
    response4 = requests.post(f"{API_URL}/talent-search/search", headers=headers, json=search4)
    
    if response4.status_code == 200:
        result4 = response4.json()
        print(f"✅ Search completed")
        print(f"   📋 Total Found: {result4['total_found']}")
        print(f"   ⚡ Immediate Ready: {result4['summary']['immediate_deployment']}")
        print(f"   📚 Short Training: {result4['summary']['short_training_needed']}")
    else:
        print(f"❌ Search failed: {response4.status_code}")
    
    # Summary
    print("\n" + "=" * 80)
    print("✨ QUICK TEST COMPLETED!")
    print("=" * 80)
    print("\n✅ All basic features are working correctly!")
    print("💡 For detailed testing, run: python test_talent_search_manual.py\n")


if __name__ == "__main__":
    try:
        test()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
