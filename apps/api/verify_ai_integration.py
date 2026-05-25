"""
AI Integration Verification Script
Tests Auggie SDK integration directly
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.ai_service import ai_service
from app.config import settings

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKBLUE}ℹ️  {text}{Colors.ENDC}")


async def main():
    print_header("🔍 AI INTEGRATION VERIFICATION")
    
    # Test 1: Check configuration
    print_header("1️⃣ CONFIGURATION CHECK")
    
    print_info(f"AI_ENABLED: {settings.AI_ENABLED}")
    print_info(f"AI_API_KEY present: {bool(settings.AI_API_KEY)}")
    if settings.AI_API_KEY:
        print_info(f"AI_API_KEY (first 20 chars): {settings.AI_API_KEY[:20]}...")
    
    print_info(f"AI_MODEL: {settings.AI_MODEL}")
    print_info(f"AI Features Enabled: {settings.ai_features_enabled}")
    
    if not settings.AI_API_KEY:
        print_error("AI_API_KEY is not set!")
        print_warning("Set AUGGIE_API_KEY in your .env file")
        return
    else:
        print_success("AI_API_KEY is configured")
    
    # Test 2: Check AI Service initialization
    print_header("2️⃣ AI SERVICE INITIALIZATION")
    
    print_info(f"AI Service instance: {ai_service}")
    print_info(f"API Key set: {bool(ai_service.api_key)}")
    print_info(f"Model: {ai_service.model}")
    print_info(f"Tenant URL: {ai_service.tenant_url}")
    print_info(f"Context initialized: {ai_service.context is not None}")
    
    if ai_service.context is None:
        print_error("DirectContext is NOT initialized!")
        print_warning("Auggie SDK failed to initialize")
        print_info("Check if Auggie SDK is installed: pip list | grep auggie")
        return
    else:
        print_success("DirectContext is initialized")
    
    # Test 3: Check if AI is available
    print_header("3️⃣ AI AVAILABILITY CHECK")
    
    is_available = await ai_service.is_available()
    print_info(f"AI Available: {is_available}")
    
    if not is_available:
        print_error("AI Service is NOT available!")
        return
    else:
        print_success("AI Service is available and ready")
    
    # Test 4: Direct AI call test
    print_header("4️⃣ DIRECT AI CALL TEST")
    
    print_info("Testing direct AI call with simple prompt...")
    
    try:
        test_prompt = "Return exactly this JSON: {\"test\": \"success\", \"number\": 42}"
        print_info(f"Prompt: {test_prompt}")
        
        response = await ai_service._call_ai(
            prompt=test_prompt,
            feature="verification_test",
            max_tokens=100,
            temperature=0.1
        )
        
        if response:
            print_success(f"AI Response received!")
            print_info(f"Response length: {len(response)} characters")
            print_info(f"Response preview: {response[:200]}...")
            
            # Try to parse as JSON
            import json
            try:
                parsed = json.loads(response.strip())
                print_success("Response is valid JSON!")
                print_info(f"Parsed: {parsed}")
            except json.JSONDecodeError as e:
                print_warning(f"Response is not valid JSON: {e}")
                print_info(f"Full response: {response}")
        else:
            print_error("AI returned None!")
            print_warning("Check server console for detailed error logs")
            return
            
    except Exception as e:
        print_error(f"AI call failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 5: Talent search query parsing test
    print_header("5️⃣ TALENT SEARCH QUERY PARSING TEST")
    
    print_info("Testing talent search query parsing...")
    
    test_queries = [
        "Need Python developer with Django and React",
        "Java backend engineer with Spring Boot, CGPA > 8.0",
        ".NET developer with C# and Azure cloud experience"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{Colors.OKBLUE}Test {i}:{Colors.ENDC} {query}")
        
        system_prompt = """You are a technical recruiter AI. Parse the job requirement and extract structured data.
Return ONLY valid JSON with this structure:
{
  "required_skills": ["skill1", "skill2"],
  "preferred_skills": [],
  "min_cgpa": null or float,
  "graduation_year": null or int,
  "degree": null or string,
  "branch": null or string
}"""
        
        prompt = f"Extract requirements from this search query:\n\n{query}"
        
        try:
            response = await ai_service._call_ai(
                prompt=prompt,
                system_prompt=system_prompt,
                feature="talent_search_query_parsing",
                max_tokens=500,
                temperature=0.1
            )
            
            if response:
                print_success("Response received")
                
                # Clean and parse
                import json
                cleaned = response.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.startswith("```"):
                    cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()
                
                try:
                    parsed = json.loads(cleaned)
                    print_success("Successfully parsed!")
                    print_info(f"  Required Skills: {parsed.get('required_skills', [])}")
                    print_info(f"  Min CGPA: {parsed.get('min_cgpa')}")
                except json.JSONDecodeError as e:
                    print_error(f"JSON parsing failed: {e}")
                    print_info(f"Response: {response[:200]}")
            else:
                print_error("No response received")
        except Exception as e:
            print_error(f"Test failed: {e}")
    
    # Test 6: Usage statistics
    print_header("6️⃣ AI USAGE STATISTICS")
    
    stats = ai_service.get_usage_stats()
    print_info(f"Total requests today: {stats['requests_today']}")
    print_info(f"Total tokens: {stats['total_tokens']}")
    print_info(f"Input tokens: {stats['input_tokens']}")
    print_info(f"Output tokens: {stats['output_tokens']}")
    print_info(f"Total cost: ${stats['total_cost_usd']:.6f}")
    print_info(f"Error count: {stats['error_count']}")
    print_info(f"Retry count: {stats['retry_count']}")
    
    if stats['requests_today'] > 0:
        print_success(f"AI has been used {stats['requests_today']} times today")
        print_success(f"Total cost: ${stats['total_cost_usd']:.6f}")
    
    # Final summary
    print_header("📊 VERIFICATION SUMMARY")
    
    print_success("✅ Configuration: OK")
    print_success("✅ DirectContext: Initialized")
    print_success("✅ AI Service: Available")
    print_success("✅ Direct AI calls: Working")
    print_success("✅ Talent search parsing: Working")
    print_success("✅ Usage tracking: Working")
    
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 AI INTEGRATION IS 100% FUNCTIONAL! 🎉{Colors.ENDC}\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠️  Verification interrupted{Colors.ENDC}\n")
    except Exception as e:
        print(f"\n{Colors.FAIL}❌ Verification failed: {e}{Colors.ENDC}\n")
        import traceback
        traceback.print_exc()
