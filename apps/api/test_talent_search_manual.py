"""
🧪 Manual Test Script for AI-Powered Talent Search

This script tests the AI Talent Search feature with realistic scenarios:
1. .NET Developer with C#, Azure, SQL
2. Python Developer with Django, React
3. Full Stack Developer with multiple skills

Run this script to verify the backend is working correctly.
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Any

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
HR_EMAIL = "hr@maverick.com"
HR_PASSWORD = "hr123"  # Update with your actual password

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Print colored header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def get_auth_token() -> str:
    """Login and get authentication token"""
    print_header("🔐 STEP 1: AUTHENTICATION")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"email": HR_EMAIL, "password": HR_PASSWORD}
        )
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print_success(f"Successfully logged in as {HR_EMAIL}")
            print_info(f"Token received: {token[:20]}...")
            return token
        else:
            print_error(f"Login failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Login error: {str(e)}")
        return None


def get_statistics(token: str) -> Dict:
    """Get talent pool statistics"""
    print_header("📊 STEP 2: TALENT POOL STATISTICS")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/talent-search/statistics",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            stats = response.json()
            print_success("Statistics retrieved successfully")
            print_info(f"Total Available Candidates: {stats['talent_pool']['total_available']}")
            print_info(f"Average CGPA: {stats['cgpa_stats']['average']:.2f}")
            print_info(f"Top Skills ({len(stats['top_skills'])}):")
            
            for skill in stats['top_skills'][:5]:
                print(f"   • {skill['skill']}: {skill['candidate_count']} candidates (avg: {skill['avg_proficiency']:.1f}%)")
            
            return stats
        else:
            print_error(f"Failed to get statistics: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Statistics error: {str(e)}")
        return None


def search_talent(token: str, query: str, include_similar: bool = False, urgency: str = "flexible", max_results: int = 10) -> Dict:
    """Perform talent search"""
    search_params = {
        "query": query,
        "max_results": max_results,
        "include_similar": include_similar,
        "urgency": urgency
    }
    
    print_info(f"Query: {query}")
    print_info(f"Include Similar: {include_similar}")
    print_info(f"Urgency: {urgency}")
    print_info(f"Max Results: {max_results}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/talent-search/search",
            headers={"Authorization": f"Bearer {token}"},
            json=search_params
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"Search completed successfully")
            return result
        else:
            print_error(f"Search failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Search error: {str(e)}")
        return None


def display_search_results(result: Dict):
    """Display search results in a readable format"""
    if not result:
        return

    print(f"\n{Colors.BOLD}{'─'*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}📋 SEARCH RESULTS{Colors.ENDC}")
    print(f"{Colors.BOLD}{'─'*80}{Colors.ENDC}")

    # Summary
    summary = result.get('summary', {})
    cost = result.get('cost_analysis', {})
    parsed = result.get('parsed_requirements', {})

    print(f"\n{Colors.OKCYAN}📊 Summary:{Colors.ENDC}")
    print(f"   Total Found: {result.get('total_found', 0)}")
    print(f"   Exact Matches: {summary.get('exact_matches', 0)}")
    print(f"   Similar Skill Candidates: {summary.get('similar_skill_candidates', 0)}")
    print(f"   Transferable Skill Candidates: {summary.get('transferable_skill_candidates', 0)}")
    print(f"   Immediate Ready: {summary.get('immediate_deployment', 0)}")
    print(f"   Short Training: {summary.get('short_training_needed', 0)}")
    print(f"   Longer Training: {summary.get('longer_training_needed', 0)}")

    print(f"\n{Colors.OKCYAN}💰 Cost Analysis:{Colors.ENDC}")
    print(f"   Total Tokens: {cost.get('total_tokens', 0)}")
    print(f"   Total Cost: ${cost.get('total_cost', 0):.6f}")

    print(f"\n{Colors.OKCYAN}🎯 Parsed Requirements:{Colors.ENDC}")
    print(f"   Required Skills: {', '.join(parsed.get('required_skills', []))}")
    if parsed.get('preferred_skills'):
        print(f"   Preferred Skills: {', '.join(parsed.get('preferred_skills', []))}")
    if parsed.get('min_cgpa'):
        print(f"   Min CGPA: {parsed.get('min_cgpa')}")

    # Candidates
    candidates = result.get('results', [])
    print(f"\n{Colors.OKCYAN}👥 Top Candidates ({len(candidates)}):{Colors.ENDC}\n")

    for i, candidate in enumerate(candidates[:5], 1):
        tier = candidate.get('tier', 'UNKNOWN')
        tier_color = Colors.OKGREEN if 'TIER_1' in tier else Colors.OKBLUE if 'TIER_2' in tier else Colors.WARNING

        print(f"{Colors.BOLD}{i}. {candidate.get('name', 'Unknown')}{Colors.ENDC}")
        print(f"   Email: {candidate.get('email', 'N/A')}")
        print(f"   {tier_color}Tier: {tier}{Colors.ENDC}")
        print(f"   Match Score: {Colors.BOLD}{candidate.get('final_score', 0):.1f}/100{Colors.ENDC}")
        print(f"   CGPA: {candidate.get('cgpa', 0):.2f}")
        print(f"   Adaptability: {candidate.get('adaptability_score', 0):.0f}/100")
        print(f"   Deployment Readiness: {candidate.get('deployment_readiness', 'N/A')}")
        print(f"   Learning Required: {candidate.get('learning_weeks_required', 0):.1f} weeks")

        # Skills
        exact = candidate.get('exact_matches', [])
        similar = candidate.get('similar_matches', [])
        transferable = candidate.get('transferable_matches', [])
        missing = candidate.get('missing_skills', [])

        if exact:
            # SkillMatch has 'skill' field
            exact_str = ', '.join([f"{s['skill']} ({s['proficiency_score']:.0f}%)" for s in exact])
            print(f"   {Colors.OKGREEN}✅ Exact Matches:{Colors.ENDC} {exact_str}")
        if similar:
            # SimilarSkillMatch has 'required_skill' and 'candidate_has' (not 'skill')
            similar_str = ', '.join([f"{s['required_skill']}→{s['candidate_has']} ({s['similarity_score']}%, prof:{s['proficiency_score']:.0f}%)" for s in similar])
            print(f"   {Colors.OKBLUE}🔷 Similar Skills:{Colors.ENDC} {similar_str}")
        if transferable:
            # TransferableSkillMatch has 'required_skill' and 'candidate_has' (not 'skill')
            transferable_str = ', '.join([f"{s['required_skill']}→{s['candidate_has']}" for s in transferable])
            print(f"   {Colors.WARNING}🔶 Transferable:{Colors.ENDC} {transferable_str}")
        if missing:
            print(f"   📚 Needs Training: {', '.join(missing)}")

        # Assessment performance
        assessment = candidate.get('assessment_performance', {})
        if assessment:
            print(f"   📊 Assessments: {assessment.get('total_assessments', 0)} total, "
                  f"{assessment.get('pass_rate', 0):.0f}% pass rate, "
                  f"trend: {assessment.get('trend', 'N/A')}")

        # Reasoning
        reasoning = candidate.get('match_reasoning', '')
        if reasoning:
            print(f"   💡 {reasoning}")

        print()


def verify_search_results(result: Dict, expected_skills: List[str], min_results: int = 1) -> bool:
    """Verify search results meet expectations"""
    if not result:
        print_error("No results returned")
        return False

    total_found = result.get('total_found', 0)
    candidates = result.get('results', [])

    success = True

    # Check if we have results
    if total_found < min_results:
        print_warning(f"Expected at least {min_results} results, got {total_found}")
        success = False
    else:
        print_success(f"Found {total_found} candidates (expected at least {min_results})")

    # Check if top candidates have expected skills
    if candidates:
        top_candidate = candidates[0]

        # Collect all skills from different match types
        candidate_skills = []

        # Exact matches use 'skill' field
        for match in top_candidate.get('exact_matches', []):
            candidate_skills.append(match['skill'].lower())

        # Similar matches use 'required_skill' and 'candidate_has' fields
        for match in top_candidate.get('similar_matches', []):
            candidate_skills.append(match['required_skill'].lower())
            candidate_skills.append(match['candidate_has'].lower())

        # Transferable matches also use 'required_skill' and 'candidate_has'
        for match in top_candidate.get('transferable_matches', []):
            candidate_skills.append(match['required_skill'].lower())
            candidate_skills.append(match['candidate_has'].lower())

        for skill in expected_skills:
            if any(skill.lower() in cs for cs in candidate_skills):
                print_success(f"Top candidate has skill: {skill}")
            else:
                print_warning(f"Top candidate missing expected skill: {skill}")

    return success


def run_test_scenario(token: str, scenario_name: str, query: str, expected_skills: List[str],
                     include_similar: bool = False, min_results: int = 1):
    """Run a single test scenario"""
    print_header(f"🧪 TEST SCENARIO: {scenario_name}")

    # Search without similar skills
    print(f"\n{Colors.BOLD}Search 1: Exact matches only{Colors.ENDC}")
    result1 = search_talent(token, query, include_similar=False, max_results=10)
    if result1:
        display_search_results(result1)
        verify_search_results(result1, expected_skills, min_results)

    # Search with similar skills
    if include_similar:
        print(f"\n{Colors.BOLD}Search 2: Including similar skills{Colors.ENDC}")
        result2 = search_talent(token, query, include_similar=True, max_results=10)
        if result2:
            display_search_results(result2)

            # Compare results
            count1 = result1.get('total_found', 0) if result1 else 0
            count2 = result2.get('total_found', 0) if result2 else 0

            if count2 >= count1:
                print_success(f"Including similar skills increased results: {count1} → {count2}")
            else:
                print_warning(f"Similar skills didn't increase results: {count1} → {count2}")

    print(f"\n{Colors.BOLD}{'─'*80}{Colors.ENDC}\n")


def main():
    """Main test execution"""
    print_header("🚀 AI-POWERED TALENT SEARCH - MANUAL TEST SUITE")
    print_info(f"API Base URL: {API_BASE_URL}")
    print_info(f"Test User: {HR_EMAIL}")
    print_info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Step 1: Authentication
    token = get_auth_token()
    if not token:
        print_error("Authentication failed. Exiting.")
        return

    # Step 2: Get Statistics
    stats = get_statistics(token)
    if not stats:
        print_warning("Could not retrieve statistics, but continuing with tests...")

    # Step 3: Run Test Scenarios
    test_scenarios = [
        {
            "name": ".NET Developer with C#, Cloud, SQL",
            "query": "Need .NET developer with C#, Azure cloud, and SQL Server experience",
            "expected_skills": [".NET", "C#", "Azure", "SQL"],
            "include_similar": True,
            "min_results": 1
        },
        {
            "name": "Python Full Stack Developer",
            "query": "Python developer with Django backend and React frontend skills, CGPA > 7.5",
            "expected_skills": ["Python", "Django", "React"],
            "include_similar": True,
            "min_results": 1
        },
        {
            "name": "Java Microservices Developer",
            "query": "Java backend engineer with Spring Boot, microservices, and Docker experience",
            "expected_skills": ["Java", "Spring", "Docker"],
            "include_similar": True,
            "min_results": 1
        },
        {
            "name": "Frontend Developer - Urgent",
            "query": "Frontend developer with Angular or React, available immediately",
            "expected_skills": ["Angular", "React", "JavaScript"],
            "include_similar": True,
            "min_results": 1
        },
        {
            "name": "DevOps Engineer",
            "query": "DevOps engineer with Kubernetes, CI/CD, and cloud platforms",
            "expected_skills": ["Kubernetes", "Docker", "AWS", "Azure"],
            "include_similar": True,
            "min_results": 1
        }
    ]

    passed = 0
    failed = 0

    for i, scenario in enumerate(test_scenarios, 1):
        try:
            run_test_scenario(
                token=token,
                scenario_name=f"{i}. {scenario['name']}",
                query=scenario['query'],
                expected_skills=scenario['expected_skills'],
                include_similar=scenario['include_similar'],
                min_results=scenario['min_results']
            )
            passed += 1
        except Exception as e:
            print_error(f"Scenario failed with error: {str(e)}")
            failed += 1

    # Final Summary
    print_header("📊 FINAL TEST SUMMARY")
    print_info(f"Total Scenarios: {len(test_scenarios)}")
    print_success(f"Passed: {passed}")
    if failed > 0:
        print_error(f"Failed: {failed}")
    else:
        print_success("All scenarios completed!")

    print(f"\n{Colors.OKGREEN}{Colors.BOLD}✨ Test suite completed! ✨{Colors.ENDC}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}⚠️  Test interrupted by user{Colors.ENDC}\n")
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
