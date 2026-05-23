"""
Test script for Claude CLI setup
Verifies that Claude CLI is properly installed and configured
"""
import subprocess
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 70)
print("🧪 Claude CLI Setup Test")
print("=" * 70)

# Test 1: Check if Claude CLI is installed
print("\n" + "=" * 70)
print("Test 1: Claude CLI Installation")
print("-" * 70)

try:
    result = subprocess.run(
        ['claude', '--version'],
        capture_output=True,
        text=True,
        timeout=5
    )
    
    if result.returncode == 0:
        version = result.stdout.strip()
        print(f"✅ Claude CLI installed: {version}")
    else:
        print(f"❌ Claude CLI not working properly")
        print(f"   Error: {result.stderr}")
        sys.exit(1)
        
except FileNotFoundError:
    print("❌ Claude CLI not found")
    print("\nInstall Claude CLI with:")
    print("   PowerShell: irm https://claude.ai/install.ps1 | iex")
    print("   Homebrew: brew install --cask claude-code")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error checking Claude CLI: {e}")
    sys.exit(1)

# Test 2: Check authentication
print("\n" + "=" * 70)
print("Test 2: Claude CLI Authentication")
print("-" * 70)

oauth_token = os.getenv("CLAUDE_CODE_OAUTH_TOKEN")

if oauth_token:
    print(f"✅ CLAUDE_CODE_OAUTH_TOKEN found: {oauth_token[:20]}...")
    print("   Will use token for authentication")
else:
    print("📝 No CLAUDE_CODE_OAUTH_TOKEN found")
    print("   Will use existing Claude CLI login credentials")
    print("\nTo generate a token, run:")
    print("   claude setup-token")

# Test 3: Test programmatic mode
print("\n" + "=" * 70)
print("Test 3: Claude CLI Programmatic Mode Test")
print("-" * 70)

try:
    print("📤 Sending test request to Claude CLI...")
    print("   Command: claude -p \"Say 'Hello from Claude CLI!' and nothing else.\"")
    
    # Set up environment
    env = os.environ.copy()
    if oauth_token:
        env["CLAUDE_CODE_OAUTH_TOKEN"] = oauth_token
    
    result = subprocess.run(
        ['claude', '-p', 'Say "Hello from Claude CLI!" and nothing else.'],
        capture_output=True,
        text=True,
        timeout=30,
        env=env
    )
    
    if result.returncode == 0:
        response = result.stdout.strip()
        print(f"✅ Claude CLI responded successfully!")
        print(f"\n📥 Response:")
        print(f"   {response}")
    else:
        error = result.stderr.strip() or result.stdout.strip()
        print(f"❌ Claude CLI failed")
        print(f"   Error: {error}")
        
        if "not authenticated" in error.lower() or "login" in error.lower():
            print("\n⚠️  You need to authenticate first:")
            print("   Run: claude auth login")
        
        sys.exit(1)
        
except subprocess.TimeoutExpired:
    print("❌ Request timed out (30 seconds)")
    print("   This might indicate Claude CLI is waiting for input")
    print("   Make sure you're authenticated: claude auth login")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error testing Claude CLI: {e}")
    sys.exit(1)

# Test 4: Test bare mode (headless)
print("\n" + "=" * 70)
print("Test 4: Claude CLI Bare Mode (Headless)")
print("-" * 70)

try:
    print("📤 Testing bare mode...")
    print("   Command: claude -p --bare \"Say hello\"")
    
    result = subprocess.run(
        ['claude', '-p', '--bare', 'Say "hello" in one word'],
        capture_output=True,
        text=True,
        timeout=30,
        env=env
    )
    
    if result.returncode == 0:
        response = result.stdout.strip()
        print(f"✅ Bare mode works!")
        print(f"   Response: {response}")
    else:
        error = result.stderr.strip() or result.stdout.strip()
        print(f"⚠️  Bare mode failed: {error}")
        print("   This is OK if you haven't set up token authentication")
        print("   Regular mode (-p without --bare) will work instead")
        
except Exception as e:
    print(f"⚠️  Bare mode test failed: {e}")
    print("   This is OK - will use regular programmatic mode")

# Test 5: Test AI service integration
print("\n" + "=" * 70)
print("Test 5: AI Service Integration Test")
print("-" * 70)

try:
    from app.services.ai_service_claude_cli import AIServiceClaudeCLI, CLAUDE_CLI_AVAILABLE
    
    print(f"✅ AI Service imported successfully")
    print(f"   CLAUDE_CLI_AVAILABLE: {CLAUDE_CLI_AVAILABLE}")
    
    # Create service instance
    service = AIServiceClaudeCLI()
    print(f"✅ AIServiceClaudeCLI initialized")
    print(f"   Provider: {service.provider}")
    print(f"   CLI available: {service.cli_available}")
    
except Exception as e:
    print(f"⚠️  Could not test AI service: {e}")

# Final summary
print("\n" + "=" * 70)
print("📊 Test Summary")
print("=" * 70)

print("\n🎉 Claude CLI is set up and working!")
print("\n✅ You can now:")
print("  1. Start your API server: uvicorn app.main:app --reload")
print("  2. Test AI endpoints: GET http://localhost:8000/api/v1/ai/status")
print("  3. Use AI features locally with Claude CLI")

print("\n📝 For production deployment:")
print("  - Get Anthropic API key from https://console.anthropic.com/")
print("  - Change AI_PROVIDER=anthropic in .env")
print("  - No code changes needed!")

print("\n💡 Tips:")
print("  - If authentication fails, run: claude auth login")
print("  - To generate a token for automation: claude setup-token")
print("  - Check Claude CLI docs: https://code.claude.com/docs")

print("=" * 70)
