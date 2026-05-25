"""
Interactive test: Chat with Auggie SDK
Type your prompts and get responses
"""
import asyncio
from dotenv import load_dotenv

# Load .env
load_dotenv()

print("=" * 70)
print("💬 Interactive Auggie SDK Chat")
print("=" * 70)
print("\nType your prompts and press Enter to get AI responses.")
print("Type 'exit' or 'quit' to stop.\n")

async def chat():
    # Import AI service
    from app.services.ai_service import ai_service
    
    print(f"✅ Connected to Auggie SDK")
    print(f"   Model: {ai_service.model}")
    print(f"   Tenant: {ai_service.tenant_url}")
    print()
    
    while True:
        # Get user input
        prompt = input("You: ")
        
        # Check for exit
        if prompt.lower() in ['exit', 'quit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if not prompt.strip():
            continue
        
        # Send to Auggie
        print("\n🤖 Auggie: ", end="", flush=True)
        
        try:
            response = await ai_service._call_ai(
                prompt=prompt,
                feature="interactive_test",
                max_tokens=500
            )
            
            if response:
                print(response)
            else:
                print("❌ No response received")
        
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    try:
        asyncio.run(chat())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
