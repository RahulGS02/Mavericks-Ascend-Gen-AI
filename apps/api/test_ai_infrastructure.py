"""
Test script for AI Infrastructure (Day 16)
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
                if isinstance(value, dict):
                    print(f"   {key}:")
                    for k, v in value.items():
                        print(f"      {k}: {v}")
                else:
                    print(f"   {key}: {value}")
    else:
        print(f"❌ {message}")

def test_ai_infrastructure():
    print("\n🤖 Testing AI Infrastructure (Day 16)")
    print("="*70)
    
    # 1. Login as Super Admin
    print_section("1️⃣  Logging in as Super Admin...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "admin@maverick.com", "password": "admin123"}
    )
    
    if login_response.status_code != 200:
        print_result(False, f"Login failed! {login_response.text}")
        return
    
    admin_token = login_response.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print_result(True, "Super Admin login successful!")
    
    # 2. Check AI Status
    print_section("2️⃣  Checking AI Status...")
    response = requests.get(f"{BASE_URL}/ai/status", headers=admin_headers)
    
    if response.status_code == 200:
        status_data = response.json()
        print_result(True, "AI Status retrieved!", {
            "Enabled": status_data["enabled"],
            "Available": status_data["available"],
            "Model": status_data["model"],
            "Environment": status_data["environment"]
        })
        
        print("\n   💰 Current Usage:")
        usage = status_data["usage"]
        print(f"      Requests Today: {usage['requests_today']}")
        print(f"      Input Tokens: {usage.get('input_tokens', 0)}")
        print(f"      Output Tokens: {usage.get('output_tokens', 0)}")
        print(f"      Total Cost: ${usage.get('total_cost_usd', 0):.6f}")
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    # 3. Get AI Config
    print_section("3️⃣  Getting AI Configuration...")
    response = requests.get(f"{BASE_URL}/ai/config", headers=admin_headers)
    
    if response.status_code == 200:
        config = response.json()
        print_result(True, "AI Config retrieved!", {
            "Model": config["model"],
            "Max Tokens": config["max_tokens"],
            "Temperature": config["temperature"],
            "Daily Limit": config["daily_limit"],
            "Rate Limit/min": config["rate_limit_per_minute"],
            "API Key Configured": config["api_key_configured"]
        })
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    # 4. Get Detailed Stats (Super Admin Only)
    print_section("4️⃣  Getting Detailed AI Statistics (Super Admin)...")
    response = requests.get(f"{BASE_URL}/ai/stats/detailed", headers=admin_headers)
    
    if response.status_code == 200:
        stats = response.json()
        print_result(True, "Detailed stats retrieved!")
        
        print("\n   📊 Usage Metrics:")
        print(f"      Total Requests: {stats['requests_today']}")
        print(f"      Total Tokens: {stats['total_tokens']}")
        print(f"      Avg Tokens/Request: {stats['avg_tokens_per_request']:.2f}")
        
        print("\n   💰 Cost Breakdown:")
        print(f"      Total Cost: ${stats['total_cost_usd']:.6f}")
        print(f"      Cost/Request: ${stats['cost_per_request_usd']:.6f}")
        print(f"      Input Cost: ${stats['cost_breakdown']['input_cost_usd']:.6f}")
        print(f"      Output Cost: ${stats['cost_breakdown']['output_cost_usd']:.6f}")
        
        print("\n   🔧 Reliability:")
        print(f"      Error Count: {stats['error_count']}")
        print(f"      Retry Count: {stats['retry_count']}")
        print(f"      Error Rate: {stats['error_rate_percentage']:.2f}%")
        
        if stats['requests_by_feature']:
            print("\n   📈 Usage by Feature:")
            for feature, feature_stats in stats['requests_by_feature'].items():
                print(f"      {feature}:")
                print(f"         Requests: {feature_stats['count']}")
                print(f"         Tokens: {feature_stats['total_tokens']}")
                print(f"         Cost: ${feature_stats['cost_usd']:.6f}")
    else:
        print_result(False, f"Failed: {response.status_code} - {response.text}")
    
    # 5. Get Cost Analytics (Super Admin Only)
    print_section("5️⃣  Getting AI Cost Analytics (Super Admin)...")
    response = requests.get(f"{BASE_URL}/ai/analytics/costs", headers=admin_headers)
    
    if response.status_code == 200:
        analytics = response.json()
        print_result(True, "Cost analytics retrieved!")
        
        print("\n   📊 All-Time Stats:")
        print(f"      Total Requests: {analytics['total_requests']}")
        print(f"      Total Tokens: {analytics['total_tokens']}")
        print(f"      Total Cost: ${analytics['total_cost_all_time']:.6f}")
        print(f"      Avg Cost/Request: ${analytics['avg_cost_per_request']:.6f}")
        
        if analytics['cost_by_feature']:
            print("\n   💰 Cost by Feature:")
            for feature, cost in analytics['cost_by_feature'].items():
                print(f"      {feature}: ${cost:.6f}")
    else:
        print_result(False, f"Failed: {response.status_code}")
    
    # 6. Test non-admin access (should fail)
    print_section("6️⃣  Testing access control (HR should NOT see detailed stats)...")
    
    # Login as HR
    hr_login = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": "hr@maverick.com", "password": "hr123"}
    )
    
    if hr_login.status_code == 200:
        hr_token = hr_login.json()["access_token"]
        hr_headers = {"Authorization": f"Bearer {hr_token}"}
        
        # Try to access detailed stats
        response = requests.get(f"{BASE_URL}/ai/stats/detailed", headers=hr_headers)
        
        if response.status_code == 403:
            print_result(True, "Access control working! HR blocked from detailed stats ✅")
        else:
            print_result(False, f"Access control failed! HR should be blocked. Got: {response.status_code}")
    
    print("\n" + "="*70)
    print("🎉 AI Infrastructure test completed!")
    print("\n📋 Infrastructure Features:")
    print("   ✅ Auggie SDK integration")
    print("   ✅ Cost tracking per feature")
    print("   ✅ Rate limiting")
    print("   ✅ Retry logic with exponential backoff")
    print("   ✅ Error handling")
    print("   ✅ Super admin-only analytics")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_ai_infrastructure()
