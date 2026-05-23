"""
Test if .env file is loading correctly
"""
import os
from dotenv import load_dotenv

print("🧪 Testing .env File Loading")
print("="*70)

# Test 1: Check if .env file exists
print("\n1️⃣  Checking if .env file exists...")
env_file = ".env"
if os.path.exists(env_file):
    print(f"✅ .env file found at: {os.path.abspath(env_file)}")
else:
    print(f"❌ .env file NOT found at: {os.path.abspath(env_file)}")
    print("\nSearching in current directory...")
    files = [f for f in os.listdir('.') if f.startswith('.env')]
    print(f"Found files: {files}")

# Test 2: Load .env file
print("\n2️⃣  Loading .env file...")
result = load_dotenv()
print(f"   load_dotenv() returned: {result}")

# Test 3: Check required variables
print("\n3️⃣  Checking environment variables...")
required_vars = [
    "DATABASE_URL",
    "SUPABASE_URL", 
    "SUPABASE_SERVICE_KEY",
    "JWT_SECRET",
    "AI_ENABLED",
    "AI_API_KEY",
    "AI_MODEL"
]

all_present = True
for var in required_vars:
    value = os.getenv(var)
    if value:
        # Hide sensitive values
        if "KEY" in var or "SECRET" in var or "URL" in var:
            display_value = f"{value[:20]}..." if len(value) > 20 else value
        else:
            display_value = value
        print(f"   ✅ {var}: {display_value}")
    else:
        print(f"   ❌ {var}: NOT SET")
        all_present = False

# Test 4: Try importing app.config
print("\n4️⃣  Testing app.config import...")
try:
    from app.config import settings
    print("✅ app.config imported successfully")
    print(f"   AI_ENABLED: {settings.AI_ENABLED}")
    print(f"   AI_MODEL: {settings.AI_MODEL}")
    print(f"   DATABASE_URL: {settings.DATABASE_URL[:30]}...")
except Exception as e:
    print(f"❌ Failed to import app.config: {e}")

print("\n" + "="*70)
if all_present:
    print("🎉 All environment variables loaded successfully!")
else:
    print("⚠️  Some environment variables are missing")
print("="*70)
