"""
Quick verification script for Auggie SDK setup
Verifies everything is ready to start building AI features
"""
import os
import sys
from dotenv import load_dotenv

print("=" * 70)
print("🔍 Auggie SDK Readiness Verification")
print("=" * 70)

# Load environment
load_dotenv()

# Test 1: Environment variables
print("\n" + "=" * 70)
print("Test 1: Configuration Check")
print("-" * 70)

ai_enabled = os.getenv("AI_ENABLED")
ai_provider = os.getenv("AI_PROVIDER")
ai_api_key = os.getenv("AI_API_KEY")

print(f"AI_ENABLED: {ai_enabled}")
print(f"AI_PROVIDER: {ai_provider}")
print(f"AI_API_KEY: {ai_api_key[:20] if ai_api_key else 'NOT SET'}...")

if ai_enabled == "true" and ai_provider == "auggie" and ai_api_key:
    print("✅ Configuration looks good!")
else:
    print("❌ Configuration issue detected")
    if ai_provider != "auggie":
        print(f"   Expected AI_PROVIDER=auggie, got: {ai_provider}")
    sys.exit(1)

# Test 2: Auggie SDK import
print("\n" + "=" * 70)
print("Test 2: Auggie SDK Import")
print("-" * 70)

try:
    from auggie_sdk.context import DirectContext, File
    print("✅ Auggie SDK imported successfully")
except ImportError as e:
    print(f"❌ Failed to import Auggie SDK: {e}")
    print("   Install with: pip install auggie-sdk")
    sys.exit(1)

# Test 3: AI Service import
print("\n" + "=" * 70)
print("Test 3: AI Service Import")
print("-" * 70)

try:
    from app.services.ai_service import ai_service, AUGGIE_SDK_AVAILABLE
    print(f"✅ AI Service imported")
    print(f"   AUGGIE_SDK_AVAILABLE: {AUGGIE_SDK_AVAILABLE}")
    print(f"   AI service context: {ai_service.context is not None}")
except Exception as e:
    print(f"❌ Failed to import AI service: {e}")
    sys.exit(1)

# Test 4: Configuration check
print("\n" + "=" * 70)
print("Test 4: Settings Verification")
print("-" * 70)

try:
    from app.config import settings
    print(f"✅ Settings loaded")
    print(f"   ai_features_enabled: {settings.ai_features_enabled}")
    print(f"   AI_PROVIDER: {settings.AI_PROVIDER}")
    print(f"   AI_MODEL: {settings.AI_MODEL}")
except Exception as e:
    print(f"❌ Settings error: {e}")
    sys.exit(1)

# Test 5: Check available features
print("\n" + "=" * 70)
print("Test 5: Available AI Features")
print("-" * 70)

features = {
    "Resume Parsing": settings.AI_RESUME_PARSING_ENABLED,
    "Skill Extraction": settings.AI_SKILL_EXTRACTION_ENABLED,
    "Performance Insights": settings.AI_PERFORMANCE_INSIGHTS_ENABLED,
}

for feature, enabled in features.items():
    status = "✅" if enabled else "❌"
    print(f"   {status} {feature}: {enabled}")

# Summary
print("\n" + "=" * 70)
print("📊 Readiness Summary")
print("=" * 70)

all_good = (
    ai_enabled == "true" and
    ai_provider == "auggie" and
    ai_api_key and
    AUGGIE_SDK_AVAILABLE and
    ai_service.context is not None and
    settings.ai_features_enabled
)

if all_good:
    print("\n🎉 ALL SYSTEMS GO!")
    print("\n✅ Auggie SDK is ready for development!")
    print("\n📝 Next Steps:")
    print("   1. Start server: uvicorn app.main:app --reload")
    print("   2. Visit: http://localhost:8000/docs")
    print("   3. Test: GET /api/v1/ai/status")
    print("   4. Build AI features!")
    print("\n📚 Documentation:")
    print("   - AUGGIE_SDK_DEVELOPMENT_GUIDE.md (Complete guide)")
    print("   - app/services/ai_service.py (AI service code)")
    print("\n🚀 Ready to build amazing AI features!")
else:
    print("\n⚠️  Some issues detected. Please check the errors above.")
    print("\n🔧 Troubleshooting:")
    print("   - Ensure .env has AI_PROVIDER=auggie")
    print("   - Verify AI_API_KEY is set")
    print("   - Check auggie-sdk is installed: pip list | grep auggie")

print("=" * 70)
