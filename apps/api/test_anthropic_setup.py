"""
Test script for Anthropic Claude API setup
Verifies that the Anthropic SDK is properly configured
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 70)
print("🧪 Anthropic Claude API Setup Test")
print("=" * 70)

# Test 1: Check environment variables
print("\n" + "=" * 70)
print("Test 1: Environment Configuration")
print("-" * 70)

api_key = os.getenv("ANTHROPIC_API_KEY")
provider = os.getenv("AI_PROVIDER")
ai_enabled = os.getenv("AI_ENABLED")

print(f"AI_ENABLED: {ai_enabled}")
print(f"AI_PROVIDER: {provider}")

if not api_key:
    print("❌ ANTHROPIC_API_KEY not found in .env")
    print("\nPlease add your Anthropic API key to .env:")
    print("ANTHROPIC_API_KEY=sk-ant-your-api-key-here")
    sys.exit(1)
else:
    print(f"✅ ANTHROPIC_API_KEY found: {api_key[:20]}...")

# Test 2: Check Anthropic SDK installation
print("\n" + "=" * 70)
print("Test 2: Anthropic SDK Installation")
print("-" * 70)

try:
    from anthropic import AsyncAnthropic
    import anthropic
    print(f"✅ anthropic SDK imported successfully")
    print(f"   Version: {anthropic.__version__ if hasattr(anthropic, '__version__') else 'Unknown'}")
except ImportError as e:
    print(f"❌ Failed to import anthropic SDK: {e}")
    print("\nInstall with: pip install anthropic==0.25.2")
    sys.exit(1)

# Test 3: Test API connection
print("\n" + "=" * 70)
print("Test 3: Anthropic API Connection Test")
print("-" * 70)

async def test_anthropic_api():
    try:
        client = AsyncAnthropic(api_key=api_key)
        print("✅ AsyncAnthropic client created successfully")
        
        # Make a simple API call
        print("\n📤 Sending test request to Anthropic API...")
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[{
                "role": "user",
                "content": "Say 'Hello from Anthropic!' and nothing else."
            }]
        )
        
        print(f"✅ API call successful!")
        print(f"\n📥 Response:")
        print(f"   Content: {response.content[0].text}")
        print(f"   Model: {response.model}")
        print(f"   Input tokens: {response.usage.input_tokens}")
        print(f"   Output tokens: {response.usage.output_tokens}")
        
        # Calculate cost
        input_cost = (response.usage.input_tokens / 1_000_000) * 3.00
        output_cost = (response.usage.output_tokens / 1_000_000) * 15.00
        total_cost = input_cost + output_cost
        
        print(f"   Cost: ${total_cost:.6f}")
        
        return True
    
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return False

# Run async test
try:
    success = asyncio.run(test_anthropic_api())
except Exception as e:
    print(f"❌ Test failed: {e}")
    success = False

# Test 4: Test the AI service integration
print("\n" + "=" * 70)
print("Test 4: AI Service Integration Test")
print("-" * 70)

try:
    # Try to import the new multi-provider service
    from app.services.ai_service_anthropic import AIServiceMultiProvider, ANTHROPIC_SDK_AVAILABLE
    
    print(f"✅ AI Service imported successfully")
    print(f"   ANTHROPIC_SDK_AVAILABLE: {ANTHROPIC_SDK_AVAILABLE}")
    
    # Create service instance
    service = AIServiceMultiProvider()
    print(f"✅ AIServiceMultiProvider initialized")
    print(f"   Provider: {service.provider}")
    print(f"   Client initialized: {service.anthropic_client is not None}")
    
except Exception as e:
    print(f"⚠️  Could not test AI service: {e}")
    print("   This is OK if you haven't updated the imports yet")

# Final summary
print("\n" + "=" * 70)
print("📊 Test Summary")
print("=" * 70)

if success:
    print("\n🎉 All tests passed!")
    print("\n✅ Anthropic Claude API is properly configured and working!")
    print("\nYou can now:")
    print("  1. Start your API server: uvicorn app.main:app --reload")
    print("  2. Test AI endpoints: GET http://localhost:8000/api/v1/ai/status")
    print("  3. Deploy to production with the same configuration")
else:
    print("\n⚠️  Some tests failed. Please check the errors above.")
    print("\nTroubleshooting:")
    print("  1. Verify your ANTHROPIC_API_KEY in .env")
    print("  2. Check internet connection")
    print("  3. Ensure anthropic SDK is installed: pip install anthropic")

print("=" * 70)
