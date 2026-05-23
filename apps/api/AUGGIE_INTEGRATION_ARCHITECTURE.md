# 🏗️ Auggie SDK Integration Architecture

## 🎯 Single Provider Architecture

**We use ONLY Auggie SDK - No other AI providers!**

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                     YOUR APPLICATION                                │
│              (Mavericks Ascend Platform)                            │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  API Endpoints                                             │   │
│  │  • POST /resume/parse                                      │   │
│  │  • GET /batch-suggestions/*                                │   │
│  │  • GET /ai/status                                          │   │
│  └──────────────────────┬─────────────────────────────────────┘   │
│                         │                                          │
│                         ▼                                          │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  AIService Class                                           │   │
│  │  (apps/api/app/services/ai_service.py)                     │   │
│  │                                                             │   │
│  │  Methods:                                                   │   │
│  │  • parse_resume_comprehensive()                            │   │
│  │  • extract_skills_from_resume()                            │   │
│  │  • get_performance_insights()                              │   │
│  │                                                             │   │
│  │  All call ↓                                                 │   │
│  └──────────────────────┬─────────────────────────────────────┘   │
│                         │                                          │
│                         ▼                                          │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  _call_ai() - SINGLE AI METHOD                             │   │
│  │                                                             │   │
│  │  Uses ONLY:                                                 │   │
│  │  self.context.search_and_ask(                              │   │
│  │      search_query="",                                       │   │
│  │      prompt=full_prompt                                     │   │
│  │  )                                                          │   │
│  └──────────────────────┬─────────────────────────────────────┘   │
│                         │                                          │
└─────────────────────────┼──────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Auggie SDK (auggie-sdk)                          │
│                      DirectContext                                  │
│                                                                     │
│  • DirectContext.create()                                           │
│  • context.add_to_index()                                           │
│  • context.search_and_ask() ← ONLY METHOD USED                     │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       │ HTTPS
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│            Augment Code API (Tenant-Specific)                       │
│         https://e7.api.augmentcode.com/                             │
│                                                                     │
│  Endpoints used by SDK:                                             │
│  • /find-missing (index management)                                 │
│  • /agents/codebase-retrieval (search)                              │
│  • /chat-stream (AI responses)                                      │
│                                                                     │
│                 Claude Sonnet 4.5 Model                             │
└─────────────────────────────────────────────────────────────────────┘


        ❌ NO OTHER PROVIDERS USED ❌
        
        ✗ OpenAI API (not used)
        ✗ Anthropic Claude API (not used)
        ✗ Google AI (not used)
        ✗ Any other provider (not used)
```

## 🔄 Request Flow Diagram

```
User Action                   Backend Processing            Auggie SDK
───────────                   ──────────────────            ──────────

1. Upload Resume
   ↓
2. POST /resume/parse
   ↓
3. resume_parser.py
   ↓
4. AIService.parse_resume_comprehensive()
   ↓
5. AIService._call_ai(prompt="Parse this resume...")
   ↓
6. Check rate limits ✓
   ↓
7. self.context.search_and_ask()  ────────────────────→  DirectContext
   ↓                                                         ↓
   ↓                                                    POST /chat-stream
   ↓                                                         ↓
8. Response ← ──────────────────────────────────────  AI Response
   ↓
9. Parse JSON response
   ↓
10. Return structured data
```

## 📊 Code Structure

### File: `apps/api/app/services/ai_service.py`

```python
class AIService:
    def __init__(self):
        # Initialize Auggie SDK DirectContext
        if AUGGIE_SDK_AVAILABLE and self.api_key:
            self._initialize_direct_context()
    
    def _initialize_direct_context(self):
        # Create DirectContext (Auggie SDK)
        self.context = DirectContext.create(
            api_key=self.api_key,
            api_url="https://e7.api.augmentcode.com/",
            debug=False
        )
        
        # Required: Add placeholder to index
        self.context.add_to_index([
            File(path='_init.txt', contents='...')
        ])
    
    async def _call_ai(self, prompt: str, ...):
        # ONLY AI method - uses Auggie SDK ONLY
        response = await loop.run_in_executor(
            None,
            lambda: self.context.search_and_ask(
                search_query="",
                prompt=full_prompt
            )
        )
        return response
    
    # All AI features use _call_ai()
    async def parse_resume_comprehensive(self, text):
        return await self._call_ai(prompt=f"Parse: {text}...")
    
    async def extract_skills_from_resume(self, text):
        return await self._call_ai(prompt=f"Extract skills: {text}...")
    
    async def get_performance_insights(self, data):
        return await self._call_ai(prompt=f"Analyze: {data}...")
```

## 🎯 Key Points

### ✅ What We Use

1. **Auggie SDK Package**: `auggie-sdk==0.1.6`
2. **DirectContext Class**: `from auggie_sdk.context import DirectContext, File`
3. **Single Method**: `context.search_and_ask()`
4. **Tenant URL**: `https://e7.api.augmentcode.com/`
5. **API Key**: From `.env` → `AI_API_KEY`

### ❌ What We DON'T Use

1. ❌ OpenAI Python package
2. ❌ Anthropic Python package
3. ❌ Direct HTTP/REST API calls
4. ❌ Multiple AI providers
5. ❌ Provider switching logic
6. ❌ Fallback to other APIs

### 🔒 Why Single Provider?

**Benefits:**
- ✅ Simpler architecture
- ✅ Consistent API interface
- ✅ Single authentication method
- ✅ Unified cost tracking
- ✅ Less code complexity
- ✅ Easier maintenance

## 💰 Cost Tracking

All costs tracked are for **Auggie SDK usage ONLY**:

```python
# Auggie-specific pricing
COST_PER_1K_INPUT_TOKENS = Decimal("0.003")
COST_PER_1K_OUTPUT_TOKENS = Decimal("0.015")

# Track by feature
self.tracker.increment(
    input_tokens=len(prompt) // 4,
    output_tokens=len(response) // 4,
    feature="resume_parsing"  # or "skill_extraction", etc.
)
```

**Admin can monitor:** `GET /api/v1/admin/analytics/ai`

## 🧪 Test Confirmation

From your test log (`script.log`):

```
Test 2: Auggie SDK DirectContext Test
✅ DirectContext created successfully
✅ Index initialized
✅ AI call successful!

[DirectContext] Searching for: "test"
[ContextAPI] POST https://e7.api.augmentcode.com/chat-stream
[ContextAPI] Response: Hello from Auggie!

🎉 All tests passed!
```

**This proves:**
- Auggie SDK is installed ✅
- DirectContext works ✅
- AI calls succeed ✅
- Using Auggie API only ✅

## 🚀 Summary

**Your integration uses:**
- ✅ ONLY Auggie SDK
- ✅ ONLY DirectContext
- ✅ ONLY search_and_ask() method
- ✅ ONLY Auggie tenant URL

**No other AI providers are used anywhere in the codebase!**
