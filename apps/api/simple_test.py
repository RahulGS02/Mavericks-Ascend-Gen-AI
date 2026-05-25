"""
Simple test: Send a prompt to Auggie SDK and get response
"""
import asyncio
from dotenv import load_dotenv

# Load .env
load_dotenv()

print("=" * 70)
print("🧪 Simple Auggie SDK Test")
print("=" * 70)

async def test_simple_prompt():
    print("\n1️⃣  Importing AI service...")
    from app.services.ai_service import ai_service
    
    print("✅ AI service imported")
    print(f"   Provider: {ai_service.provider}")
    print(f"   Context ready: {ai_service.context is not None}")
    
    # Test with simple prompt
    print("\n2️⃣  Sending your prompt to Auggie...")
    print("   Prompt: 'Tell me a fun fact about Python programming'")
    
    response = await ai_service._call_ai(
        prompt="Tell me a fun fact about Python programming in 2 sentences.",
        feature="test",
        max_tokens=100
    )
    
    print("\n3️⃣  Response received!")
    print("-" * 70)
    print(response)
    print("-" * 70)
    
    if response:
        print("\n✅ SUCCESS! Auggie SDK is working!")
    else:
        print("\n❌ No response received")

if __name__ == "__main__":
    print("\n🚀 Starting test...\n")
    asyncio.run(test_simple_prompt())
    print("\n" + "=" * 70)
    print("✅ Test complete!")
    print("=" * 70)
