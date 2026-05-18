"""
Test the registration endpoint directly
"""
import requests

url = "http://localhost:8000/api/v1/mavericks/register"

# Test data
data = {
    "name": "Test Maverick",
    "email": "test@example.com",
    "password": "test123",
    "phone": "+91 9876543210",
    "college": "Test College",
    "degree": "B.Tech",
    "branch": "Computer Science",
    "graduation_year": "2024",
    "cgpa": "8.5",
    "skills": "Python, Java, React"
}

print("Testing POST to:", url)
print("=" * 80)

try:
    response = requests.post(url, data=data)
    print(f"\nStatus Code: {response.status_code}")
    print(f"\nResponse Headers:")
    for key, value in response.headers.items():
        print(f"  {key}: {value}")
    
    print(f"\nResponse Body:")
    print(response.text)
    
    if response.status_code == 404:
        print("\n❌ ERROR: Endpoint not found!")
        print("\nDebugging info:")
        print("1. Check if backend server is running")
        print("2. Try accessing: http://localhost:8000/docs")
        print("3. Verify the endpoint exists in the Swagger docs")
    elif response.status_code == 201:
        print("\n✅ SUCCESS: Registration endpoint working!")
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Cannot connect to backend server!")
    print("Make sure the server is running on http://localhost:8000")
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
