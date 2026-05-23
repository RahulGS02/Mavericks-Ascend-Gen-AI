"""
Test Auggie SDK DirectContext initialization
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

# CRITICAL: Load .env file BEFORE importing any app modules
from dotenv import load_dotenv
load_dotenv()  # This loads the .env file

print("🧪 Testing Auggie SDK DirectContext")
print("="*70)

# IMPORTANT: Import ai_service first to apply SSL patches
print("\n0️⃣  Applying SSL patches...")
try:
    from app.services import ai_service
    print("✅ SSL patches applied from ai_service module")
except Exception as e:
    print(f"⚠️  Warning: Failed to import ai_service: {e}")
    print("   Applying manual SSL patches...")

    # Manual SSL patches
    import ssl
    import urllib3
    import requests

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    os.environ['CURL_CA_BUNDLE'] = ''
    os.environ['REQUESTS_CA_BUNDLE'] = ''

    _create_unverified_context = ssl._create_unverified_context
    ssl._create_default_https_context = _create_unverified_context

    _original_post = requests.post
    _original_get = requests.get
    _original_request = requests.request

    def _patched_post(url, **kwargs):
        kwargs['verify'] = False
        return _original_post(url, **kwargs)

    def _patched_get(url, **kwargs):
        kwargs['verify'] = False
        return _original_get(url, **kwargs)

    def _patched_request(method, url, **kwargs):
        kwargs['verify'] = False
        return _original_request(method, url, **kwargs)

    requests.post = _patched_post
    requests.get = _patched_get
    requests.request = _patched_request

    print("✅ Manual SSL patches applied")

# Test 1: Check if auggie-sdk is installed
print("\n1️⃣  Checking if auggie-sdk is installed...")
try:
    import auggie_sdk
    print(f"✅ auggie-sdk installed: {auggie_sdk.__version__ if hasattr(auggie_sdk, '__version__') else 'unknown version'}")
except ImportError as e:
    print(f"❌ auggie-sdk NOT installed: {e}")
    print("\nInstall with: pip install auggie-sdk")
    sys.exit(1)

# Test 2: Import DirectContext
print("\n2️⃣  Importing DirectContext...")
try:
    from auggie_sdk.context import DirectContext, File
    print("✅ DirectContext imported successfully")
except ImportError as e:
    print(f"❌ Failed to import DirectContext: {e}")
    sys.exit(1)

# Test 3: Load configuration
print("\n3️⃣  Loading configuration...")
try:
    from app.config import settings
    
    print(f"   AI_ENABLED: {settings.AI_ENABLED}")
    print(f"   AI_API_KEY: {settings.AI_API_KEY[:20]}..." if settings.AI_API_KEY else "   AI_API_KEY: NOT SET")
    print(f"   AI_MODEL: {settings.AI_MODEL}")
    
    if not settings.AI_API_KEY:
        print("\n❌ AI_API_KEY not set in .env")
        sys.exit(1)
    
    print("✅ Configuration loaded")
except Exception as e:
    print(f"❌ Failed to load configuration: {e}")
    sys.exit(1)

# Test 4: Initialize DirectContext
print("\n4️⃣  Initializing DirectContext...")
try:
    context = DirectContext.create(
        api_key=settings.AI_API_KEY,
        api_url="https://e7.api.augmentcode.com/",
        debug=True  # Enable debug mode to see detailed logs
    )
    print("✅ DirectContext created successfully")
except Exception as e:
    print(f"❌ Failed to create DirectContext: {e}")
    print(f"\nError type: {type(e).__name__}")
    print(f"Error details: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Initialize index
print("\n5️⃣  Initializing index with placeholder...")
try:
    context.add_to_index([
        File(path='_init.txt', contents='Initialization placeholder for DirectContext')
    ])
    print("✅ Index initialized")
except Exception as e:
    print(f"❌ Failed to initialize index: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 6: Make a simple AI call
print("\n6️⃣  Testing AI call with search_and_ask...")
try:
    # Correct signature: search_and_ask(search_query: str, prompt: Optional[str] = None)
    response = context.search_and_ask(
        search_query="test",  # Search query (can be empty or placeholder)
        prompt="Say 'Hello from Auggie!' and nothing else."
    )

    print("✅ AI call successful!")
    print(f"\nResponse type: {type(response)}")
    print(f"Response: {response}")

    # Try to extract answer
    if hasattr(response, 'answer'):
        print(f"\n📝 Answer: {response.answer}")
    elif hasattr(response, 'text'):
        print(f"\n📝 Text: {response.text}")
    elif isinstance(response, str):
        print(f"\n📝 Response text: {response}")
    else:
        print(f"\n📝 Response attributes: {dir(response)}")

except Exception as e:
    print(f"❌ AI call failed: {e}")
    import traceback
    traceback.print_exc()

    # Try to get help on the method
    print("\n🔍 Method signature:")
    import inspect
    print(inspect.signature(context.search_and_ask))
    sys.exit(1)

print("\n" + "="*70)
print("🎉 All tests passed! Auggie SDK is working correctly.")
print("="*70)
