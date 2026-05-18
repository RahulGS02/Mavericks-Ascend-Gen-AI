"""
Test Top Performers API Endpoint

Focused test to debug and validate the top-performers endpoint
"""

import requests
import json
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
HR_EMAIL = "hr@maverick.com"
HR_PASSWORD = "hr123"

# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 80}{Colors.END}\n")

def print_success(message: str):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message: str):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message: str):
    print(f"{Colors.CYAN}ℹ️  {message}{Colors.END}")

def print_data(label: str, data):
    print(f"{Colors.CYAN}{label}:{Colors.END} {data}")


def login(email: str, password: str) -> Optional[str]:
    """Login and return access token"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print_success(f"Logged in as {email}")
            return token
        else:
            print_error(f"Login failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Login error: {str(e)}")
        return None


def test_top_performers():
    """Test the top performers endpoint"""
    print_header("TEST: TOP PERFORMERS BY BATCH")
    
    # Step 1: Login
    print(f"\n{Colors.BOLD}Step 1: Login as HR{Colors.END}")
    token = login(HR_EMAIL, HR_PASSWORD)
    
    if not token:
        print_error("Failed to login. Aborting test.")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Test the endpoint
    print(f"\n{Colors.BOLD}Step 2: Call /batches/top-performers{Colors.END}")
    
    try:
        print_info(f"Making request to: {BASE_URL}/batches/top-performers")
        print_info(f"Parameters: limit=10")
        
        response = requests.get(
            f"{BASE_URL}/batches/top-performers",
            headers=headers,
            params={"limit": 10}
        )
        
        print_data("Status Code", response.status_code)
        
        if response.status_code == 200:
            print_success("Request successful!")
            
            # Parse response
            data = response.json()
            print_data("\nTotal Batches", data.get('total_batches', 0))
            
            # Display each batch
            batches = data.get('batches', [])
            
            if not batches:
                print_error("No batches found with top performers")
                print_info("This could mean:")
                print_info("  - No batches exist")
                print_info("  - No batches have assessment attempts")
                print_info("  - All batches have status other than ACTIVE/COMPLETED")
                return False
            
            print(f"\n{Colors.BOLD}Found {len(batches)} Batch(es) with Top Performers:{Colors.END}\n")
            
            for i, batch in enumerate(batches, 1):
                print(f"{Colors.YELLOW}{'─' * 80}{Colors.END}")
                print(f"{Colors.BOLD}Batch {i}: {batch['batch_name']}{Colors.END}")
                print(f"  Batch ID: {batch['batch_id']}")
                print(f"  Status: {batch['batch_status']}")
                print(f"  Enrolled: {batch['total_enrolled']}")
                print(f"  Start Date: {batch.get('start_date', 'N/A')}")
                print(f"  End Date: {batch.get('end_date', 'N/A')}")
                
                performer = batch.get('top_performer', {})
                if performer:
                    print(f"\n  {Colors.GREEN}🏆 Top Performer:{Colors.END}")
                    print(f"    Name: {performer.get('name')}")
                    print(f"    Email: {performer.get('email')}")
                    print(f"    Total Attempts: {performer.get('total_attempts')}")
                    print(f"    Passed Attempts: {performer.get('passed_attempts')}")
                    print(f"    Pass Rate: {performer.get('pass_rate')}%")
                    print(f"    Average Score: {performer.get('avg_score')}")
                    print(f"    Combined Score: {performer.get('combined_score')}")
                else:
                    print(f"  {Colors.RED}No performer data{Colors.END}")
                
                print()
            
            print(f"{Colors.YELLOW}{'─' * 80}{Colors.END}\n")
            print_success("Top Performers endpoint working correctly!")
            return True
            
        else:
            print_error(f"Request failed with status code: {response.status_code}")
            print_error(f"Response body: {response.text}")
            
            # Try to parse error details
            try:
                error_data = response.json()
                print_data("Error detail", error_data.get('detail', 'No detail provided'))
            except:
                pass
            
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Request error: {str(e)}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point"""
    print_header("TOP PERFORMERS ENDPOINT TEST")
    print_info(f"Backend URL: {BASE_URL}")
    print_info(f"Testing endpoint: /batches/top-performers")
    
    # Check backend availability
    try:
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/docs", timeout=5)
        if response.status_code != 200:
            print_error("Backend not accessible")
            return
    except:
        print_error("Cannot connect to backend. Please start it first.")
        return
    
    # Run test
    success = test_top_performers()
    
    # Summary
    print_header("TEST SUMMARY")
    if success:
        print_success("✅ Top Performers test PASSED")
    else:
        print_error("❌ Top Performers test FAILED")
    
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
