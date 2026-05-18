"""
Test Auggie API connection directly
"""
import httpx
import asyncio
from app.config import settings

async def test_auggie_api():
    print("🧪 Testing Auggie API Connection")
    print("="*70)
    
    print(f"\n📋 Configuration:")
    print(f"   API Key: {settings.AI_API_KEY[:20]}..." if settings.AI_API_KEY else "   API Key: NOT SET")
    print(f"   Model: {settings.AI_MODEL}")
    print(f"   Base URL: https://e7.api.augmentcode.com")
    print(f"   SSL Verification: Disabled (self-signed cert)")
    
    if not settings.AI_API_KEY:
        print("\n❌ Error: AI_API_KEY not set in .env")
        return
    
    # Test 1: Try standard OpenAI-compatible format
    print("\n" + "="*70)
    print("Test 1: OpenAI-compatible format (Authorization: Bearer)")
    print("-"*70)
    
    try:
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            response = await client.post(
                "https://e7.api.augmentcode.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.AI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.AI_MODEL,
                    "messages": [
                        {"role": "user", "content": "Say 'Hello World' and nothing else."}
                    ],
                    "max_tokens": 50,
                    "temperature": 0.7
                }
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
            if response.status_code == 200:
                print("✅ SUCCESS! Standard format works.")
                result = response.json()
                print(f"\nAI Response: {result.get('choices', [{}])[0].get('message', {}).get('content', 'N/A')}")
            else:
                print(f"❌ Failed with status {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Try with X-API-Key header
    print("\n" + "="*70)
    print("Test 2: X-API-Key header format")
    print("-"*70)
    
    try:
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            response = await client.post(
                "https://e7.api.augmentcode.com/v1/chat/completions",
                headers={
                    "X-API-Key": settings.AI_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "model": settings.AI_MODEL,
                    "messages": [
                        {"role": "user", "content": "Say 'Hello World' and nothing else."}
                    ],
                    "max_tokens": 50,
                    "temperature": 0.7
                }
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
            if response.status_code == 200:
                print("✅ SUCCESS! X-API-Key format works.")
                result = response.json()
                print(f"\nAI Response: {result.get('choices', [{}])[0].get('message', {}).get('content', 'N/A')}")
            else:
                print(f"❌ Failed with status {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Try Anthropic Claude format
    print("\n" + "="*70)
    print("Test 3: Anthropic Claude format")
    print("-"*70)
    
    try:
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            response = await client.post(
                "https://e7.api.augmentcode.com/v1/messages",
                headers={
                    "x-api-key": settings.AI_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "claude-sonnet-4.5",
                    "messages": [
                        {"role": "user", "content": "Say 'Hello World' and nothing else."}
                    ],
                    "max_tokens": 50
                }
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
            if response.status_code == 200:
                print("✅ SUCCESS! Anthropic format works.")
                result = response.json()
                print(f"\nAI Response: {result.get('content', [{}])[0].get('text', 'N/A')}")
            else:
                print(f"❌ Failed with status {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*70)
    print("🏁 Connection test complete!")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(test_auggie_api())
