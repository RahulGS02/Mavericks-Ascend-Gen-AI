"""
End-to-End Test for Natural Language Query Feature
Tests complete flow: Login → Query → Get Results → Download Excel

Prerequisites:
1. Server must be running: uvicorn app.main:app --reload
2. Database must have a SuperAdmin user
3. .env must be configured
"""
import requests
import json
import sys
from pathlib import Path
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_VERSION = "/api/v1"

# SuperAdmin credentials (update these to match your database)
SUPERADMIN_EMAIL = "admin@maverick.com"  # Change this
SUPERADMIN_PASSWORD = "admin123"  # Change this

# Test queries to run
TEST_QUERIES = [
    {
        "name": "Available Mavericks",
        "query": "Show me all mavericks who are available for deployment",
        "max_rows": 50
    },
    {
        "name": "Active Batches",
        "query": "List all active batches",
        "max_rows": 20
    },
    {
        "name": "Top Students by CGPA",
        "query": "Show me the top 10 mavericks by CGPA",
        "max_rows": 10
    },
    {
        "name": "Deployment Statistics",
        "query": "Count how many mavericks are in each deployment status",
        "max_rows": 100
    }
]


def print_step(step_num, message):
    """Print formatted step message"""
    print(f"\n{'='*80}")
    print(f"STEP {step_num}: {message}")
    print('='*80)


def print_success(message):
    """Print success message"""
    print(f"✅ {message}")


def print_error(message):
    """Print error message"""
    print(f"❌ {message}")


def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")


def print_warning(message):
    """Print warning message"""
    print(f"⚠️  {message}")


def test_server_connection():
    """Test if server is running"""
    print_step(1, "Testing Server Connection")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print_success(f"Server is running at {BASE_URL}")
            print_info(f"Response: {response.json()}")
            return True
        else:
            print_error(f"Server responded with status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to server at {BASE_URL}")
        print_info("Make sure the server is running:")
        print_info("  uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print_error(f"Error connecting to server: {e}")
        return False


def login_as_superadmin():
    """Login and get authentication token"""
    print_step(2, "Logging in as SuperAdmin")
    
    login_url = f"{BASE_URL}{API_VERSION}/auth/login"
    
    # Method 1: Try form-data login (most common)
    print_info(f"Attempting login to: {login_url}")
    print_info(f"Email: {SUPERADMIN_EMAIL}")
    
    try:
        # Try form-data format first
        response = requests.post(
            login_url,
            data={
                "username": SUPERADMIN_EMAIL,  # FastAPI OAuth2 uses 'username' field
                "password": SUPERADMIN_PASSWORD
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            user = data.get("user", {})
            
            if token:
                print_success("Login successful!")
                print_info(f"User: {user.get('name', 'N/A')} ({user.get('email', 'N/A')})")
                print_info(f"Role: {user.get('role', 'N/A')}")
                print_info(f"Token: {token[:20]}...")
                return token
            else:
                print_error("Login response missing access_token")
                print_info(f"Response: {json.dumps(data, indent=2)}")
                return None
        else:
            print_error(f"Login failed with status code: {response.status_code}")
            print_info(f"Response: {response.text}")
            
            # Try JSON format as alternative
            print_warning("Trying JSON format...")
            response = requests.post(
                login_url,
                json={
                    "email": SUPERADMIN_EMAIL,
                    "password": SUPERADMIN_PASSWORD
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                if token:
                    print_success("Login successful with JSON format!")
                    return token
            
            print_error("Both login formats failed")
            print_info("Please verify SuperAdmin credentials in the script")
            return None
            
    except Exception as e:
        print_error(f"Login error: {e}")
        return None


def test_nl_query_search(token, query_data):
    """Test natural language query search endpoint"""
    
    search_url = f"{BASE_URL}{API_VERSION}/nl-query/search"
    
    print_info(f"Query: \"{query_data['query']}\"")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": query_data['query'],
        "include_stats": True,
        "max_rows": query_data.get('max_rows', 100)
    }
    
    try:
        response = requests.post(
            search_url,
            headers=headers,
            json=payload,
            timeout=30  # AI queries may take time
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print_success("Query executed successfully!")
            print_info(f"  Query ID: {data.get('query_id', 'N/A')}")
            print_info(f"  Generated SQL: {data.get('generated_sql', 'N/A')[:100]}...")
            print_info(f"  Explanation: {data.get('explanation', 'N/A')}")
            print_info(f"  Tables Used: {', '.join(data.get('tables_used', []))}")
            print_info(f"  Rows Returned: {len(data.get('data', []))}")
            
            # Show statistics
            stats = data.get('statistics', {})
            print_info(f"  Total Rows: {stats.get('total_rows', 0)}")
            print_info(f"  Execution Time: {stats.get('execution_time_ms', 0):.2f}ms")
            
            # Show first few rows
            data_rows = data.get('data', [])
            if data_rows:
                print_info(f"\n  Sample Data (first 3 rows):")
                for i, row in enumerate(data_rows[:3], 1):
                    print(f"    Row {i}: {json.dumps(row, indent=6, default=str)[:150]}...")
            
            return True, data
        else:
            print_error(f"Query failed with status code: {response.status_code}")
            print_info(f"Response: {response.text}")
            return False, None
            
    except Exception as e:
        print_error(f"Query error: {e}")
        return False, None


def test_excel_download(token, query_data):
    """Test Excel download endpoint"""
    
    download_url = f"{BASE_URL}{API_VERSION}/nl-query/search/download"
    
    print_info(f"Downloading results for: \"{query_data['query']}\"")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "query": query_data['query'],
        "include_stats": True,
        "max_rows": query_data.get('max_rows', 100)
    }
    
    try:
        response = requests.post(
            download_url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            # Save Excel file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_download_{timestamp}.xlsx"

            with open(filename, 'wb') as f:
                f.write(response.content)

            file_size = len(response.content)
            print_success(f"Excel file downloaded!")
            print_info(f"  Filename: {filename}")
            print_info(f"  Size: {file_size:,} bytes")

            return True
        else:
            print_error(f"Download failed with status code: {response.status_code}")
            print_error(f"Response content: {response.text[:500]}")  # Show error details
            return False
            
    except Exception as e:
        print_error(f"Download error: {e}")
        return False


def main():
    """Main test execution"""
    
    print("\n" + "="*80)
    print("🧪 END-TO-END TEST: Natural Language Query Feature")
    print("="*80)
    print(f"\nBase URL: {BASE_URL}")
    print(f"SuperAdmin Email: {SUPERADMIN_EMAIL}")
    print(f"Test Queries: {len(TEST_QUERIES)}")
    
    # Step 1: Test server connection
    if not test_server_connection():
        print("\n" + "="*80)
        print("❌ TEST FAILED: Server is not running")
        print("="*80)
        sys.exit(1)
    
    # Step 2: Login
    token = login_as_superadmin()
    if not token:
        print("\n" + "="*80)
        print("❌ TEST FAILED: Login failed")
        print("="*80)
        print("\n💡 Action Required:")
        print("   1. Check SuperAdmin credentials in this script")
        print("   2. Ensure SuperAdmin user exists in database")
        print("   3. Verify password is correct")
        sys.exit(1)
    
    # Step 3: Test Natural Language Queries
    print_step(3, "Testing Natural Language Query Endpoint")
    
    successful_queries = 0
    failed_queries = 0
    
    for i, query_data in enumerate(TEST_QUERIES, 1):
        print(f"\n--- Test Query {i}/{len(TEST_QUERIES)}: {query_data['name']} ---")
        
        success, result = test_nl_query_search(token, query_data)
        
        if success:
            successful_queries += 1
        else:
            failed_queries += 1
    
    print(f"\n📊 Query Test Results:")
    print(f"   ✅ Successful: {successful_queries}")
    print(f"   ❌ Failed: {failed_queries}")
    
    # Step 4: Test Excel Download
    print_step(4, "Testing Excel Download")
    
    if TEST_QUERIES:
        download_success = test_excel_download(token, TEST_QUERIES[0])
    else:
        download_success = False
    
    # Final Summary
    print("\n" + "="*80)
    print("📊 FINAL TEST SUMMARY")
    print("="*80)
    
    results = {
        "Server Connection": "✅ PASS",
        "SuperAdmin Login": "✅ PASS",
        "Natural Language Queries": f"✅ {successful_queries}/{len(TEST_QUERIES)} PASS" if failed_queries == 0 else f"⚠️ {successful_queries}/{len(TEST_QUERIES)} PASS",
        "Excel Download": "✅ PASS" if download_success else "❌ FAIL"
    }
    
    print()
    for test_name, result in results.items():
        print(f"  {result:20} {test_name}")
    
    print("\n" + "="*80)
    
    if successful_queries == len(TEST_QUERIES) and download_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Natural Language Query feature is fully functional!")
        print("\n💡 Ready to build UI!")
        print("="*80)
        sys.exit(0)
    else:
        print("⚠️ SOME TESTS FAILED")
        print("Review the output above for details")
        print("="*80)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
