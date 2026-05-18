"""
Test script for AI Service Integration
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

def test_ai_service():
    print("\n🤖 Testing AI Service Integration")
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
    
    # 2. Check AI Status
    print_section("2️⃣  Checking AI Status...")
    response = requests.get(f"{BASE_URL}/ai/status", headers=headers)
    
    if response.status_code == 200:
        status = response.json()
        print_result(True, "AI Status retrieved!", {
            "Enabled": status["enabled"],
            "Available": status["available"],
            "Environment": status["environment"],
            "Model": status["model"]
        })
        
        print("\n   Features:")
        for feature, enabled in status["features"].items():
            print(f"      {feature}: {'✅' if enabled else '❌'}")
        
        print("\n   Usage:")
        for metric, value in status["usage"].items():
            if metric != "last_reset":
                print(f"      {metric}: {value}")
        
        ai_available = status["available"]
    else:
        print_result(False, f"Failed: {response.status_code}")
        ai_available = False
    
    # 3. Get AI Config (HR only)
    print_section("3️⃣  Getting AI Configuration (HR)...")
    response = requests.get(f"{BASE_URL}/ai/config", headers=headers)
    
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
    
    # 4. Test AI Features (if available)
    if ai_available:
        print_section("4️⃣  AI Features are ENABLED ✅")
        print("   You can now test:")
        print("   - Resume parsing during maverick creation")
        print("   - Skill extraction from resumes")
        print("   - Performance insights generation")
    else:
        print_section("4️⃣  AI Features are DISABLED ⚠️")
        print("   To enable AI:")
        print("   1. Set AI_ENABLED=true in .env")
        print("   2. Add your Auggie API key to AI_API_KEY")
        print("   3. Restart the server")
        print("\n   The application works normally without AI!")
        print("   AI features are optional enhancements.")
    
    print("\n" + "="*70)
    print("🎉 AI Service test completed!")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_ai_service()
