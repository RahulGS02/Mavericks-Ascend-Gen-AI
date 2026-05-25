# 🚀 AI-Powered Intelligent Talent Search

> **Status:** ✅ Phases 1-3 Complete (Backend 100%)  
> **Next:** Phase 4 - Frontend Integration

---

## 📖 **What is This?**

An AI-powered talent search system that finds the best candidates using natural language queries, intelligent skill matching, and learning timeline estimation.

**Example:**
```
Query: "Need .NET developer with Azure, CGPA > 8"

Results:
✅ 3 exact matches (ready now)
🔄 12 similar candidates (C# developers, 1-4 weeks training)
🎯 8 transferable candidates (Java/Python developers, 4-8 weeks)
```

---

## 🎯 **Key Features**

1. **Natural Language Search** - Just type what you need
2. **Multi-Tier Results** - Exact, similar, and transferable matches
3. **Adaptability Scoring** - Identifies fast learners
4. **Learning Timelines** - Predicts weeks to proficiency
5. **Training Plans** - Structured learning phases
6. **Cost-Optimized** - ~$0.0015 per search

---

## ⚡ **Quick Start**

### **1. Installation**

```bash
cd apps/api
pip install -r requirements.txt
```

### **2. Environment Setup**

Create `.env` file:
```env
# Testing mode (bypasses production requirements)
TESTING=true

# Database (optional in test mode)
DATABASE_URL=postgresql://user:pass@localhost/db

# AI (optional - falls back to basic parsing if unavailable)
AI_ENABLED=true
AI_API_KEY=your_auggie_key_here
```

### **3. Start Server**

```bash
uvicorn app.main:app --reload
```

Server starts at: `http://localhost:8000`

### **4. View Documentation**

Open: `http://localhost:8000/docs`

---

## 🧪 **Run Tests**

### **Unit Tests (Foundation Layer)**

```bash
python run_tests.py
```

Expected output:
```
26 passed ✅
```

### **Integration Tests (API Layer)**

```bash
pytest tests/test_talent_search_api.py -v
```

Expected output:
```
10 passed ✅
```

### **Quick Verification**

```bash
python test_talent_search_quick.py
```

---

## 📍 **API Endpoints**

### **Base URL:** `/api/v1/talent-search`

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/search` | AI-powered talent search |
| GET | `/explain/{id}` | Explain candidate match |
| GET | `/cost-estimate` | Get cost estimates |
| GET | `/statistics` | Talent pool statistics |

**Authentication Required:** JWT Bearer Token (HR/Manager/Admin roles)

---

## 💡 **Usage Example**

### **Step 1: Login**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "hr@maverick.com",
    "password": "your_password"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

### **Step 2: Search for Candidates**

```bash
curl -X POST "http://localhost:8000/api/v1/talent-search/search" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Need .NET developer with Azure experience",
    "max_results": 20
  }'
```

**Response:**
```json
{
  "query": "Need .NET developer with Azure experience",
  "total_found": 15,
  "results": [
    {
      "name": "John Doe",
      "final_score": 87.5,
      "tier": "TIER_1_EXACT",
      "exact_matches": [".NET", "Azure"],
      "adaptability_score": 85.0,
      "deployment_readiness": "immediate",
      "match_reasoning": "✅ Excellent match! Has 2 exact skill matches..."
    }
  ],
  "summary": {
    "exact_matches": 3,
    "similar_skill_candidates": 12,
    "show_similar_button": false
  },
  "cost_analysis": {
    "total_cost": 0.0015
  }
}
```

---

## 📚 **Documentation**

| Document | Purpose |
|----------|---------|
| [API_DOCUMENTATION.md](AI_TALENT_SEARCH_API_DOCUMENTATION.md) | Complete API reference |
| [IMPLEMENTATION.md](AI_TALENT_SEARCH_IMPLEMENTATION.md) | Technical implementation details |
| [PHASE_1_2_3_SUMMARY.md](PHASE_1_2_3_COMPLETE_SUMMARY.md) | Overall project summary |

---

## 🏗️ **Architecture**

```
Frontend (Phase 4)
    ↓
API Layer (Phase 3) ✅
    ├─ 4 RESTful endpoints
    ├─ JWT authentication
    └─ Role-based authorization
    ↓
Business Logic (Phase 2) ✅
    ├─ TalentSearchService
    ├─ AI query parsing
    ├─ SQL pre-filtering
    └─ Multi-factor scoring
    ↓
Core Engine (Phase 1) ✅
    ├─ SkillSimilarityEngine
    ├─ Skill mappings (25+ techs)
    ├─ Adaptability scoring
    └─ Timeline estimation
    ↓
Database (PostgreSQL)
```

---

## 🎓 **Technical Highlights**

- **Language:** Python 3.12
- **Framework:** FastAPI
- **Database:** PostgreSQL (SQLAlchemy ORM)
- **AI:** Auggie SDK (Claude Sonnet 4.5)
- **Authentication:** JWT (jose)
- **Validation:** Pydantic
- **Testing:** pytest

---

## 📊 **Project Stats**

- **Production Code:** 3,958 lines
- **Documentation:** 1,535 lines
- **Tests:** 36 (100% passing)
- **Files Created:** 9
- **API Endpoints:** 4
- **Skill Mappings:** 25+ technologies
- **Cost per Search:** ~$0.0015

---

## 🚀 **What's Next?**

### **Phase 4: Frontend Integration**

1. Create search interface component
2. Display tiered results
3. Show learning paths and training plans
4. Implement "Show Similar" button
5. Add match explanation modal

**Estimated Effort:** 3-4 days

---

## ❓ **FAQ**

**Q: Do I need AI enabled to use this?**  
A: No, the system falls back to basic parsing if AI is unavailable. However, AI provides better query understanding.

**Q: What roles can access this?**  
A: HR, Manager, and Super Admin roles only.

**Q: How much does it cost per search?**  
A: ~$0.0015 per search (AI parsing only). Scoring is rules-based (free).

**Q: Can I customize skill mappings?**  
A: Yes, edit `skill_mappings.py` to add/modify technologies.

---

## 📞 **Support**

- **Interactive Docs:** `http://localhost:8000/docs`
- **Issues:** Create issue in repository
- **Email:** admin@maverick.com

---

**Built with ❤️ for Maverick Ascend Platform**
