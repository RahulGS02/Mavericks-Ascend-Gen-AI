# 🎨 **FRONTEND AI TALENT SEARCH - TESTING GUIDE**

## 📋 **Overview**

This guide shows you how to test the AI-Powered Talent Search feature in the React frontend.

---

## 🚀 **STEP 1: Start the Frontend**

```bash
# Navigate to web directory
cd apps/web

# Install dependencies (if not done)
npm install

# Start development server
npm run dev
```

**Expected output:**
```
  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
  - Network:      http://192.168.x.x:3000

✓ Ready in Xms
```

---

## 🔑 **STEP 2: Login as HR**

### **Open Browser:**
```
http://localhost:3000
```

### **Login Credentials:**
- **Email:** `hr@maverick.com`
- **Password:** (your HR password)

**Alternative (SuperAdmin):**
- **Email:** `admin@maverick.com`
- **Password:** (your admin password)

---

## 🔍 **STEP 3: Navigate to Talent Search**

### **Two ways to access:**

**Method 1: Direct URL**
```
http://localhost:3000/hr/talent-search
```

**Method 2: Through Menu**
1. Click "HR" or "Dashboard" in navigation
2. Look for "Talent Search" or "AI Talent Search" menu item
3. Click to open

---

## 🧪 **STEP 4: Test the AI Feature**

### **Test 1: Simple Search**

**Enter this query in the search box:**
```
Python developer with Django
```

**Click "Search" button**

**What to look for:**
- ✅ Search results appear
- ✅ "Parsed Requirements" section shows extracted skills: `Python`, `Django`
- ✅ Candidates are categorized into tiers:
  - **TIER_1_EXACT** - Has exact skills
  - **TIER_2_SIMILAR** - Has similar skills
  - **TIER_3_TRANSFERABLE** - Has transferable skills
- ✅ Each candidate shows:
  - Match score (0-100)
  - Skill matches (exact, similar, transferable)
  - CGPA
  - Adaptability score
  - Learning weeks required
  - Deployment readiness

---

### **Test 2: Search with CGPA Filter**

**Enter:**
```
.NET developer with C# and Azure, CGPA > 8.0
```

**What to look for:**
- ✅ Parsed requirements show: `Required Skills: .NET, C#, Azure`
- ✅ Parsed requirements show: `Min CGPA: 8.0`
- ✅ All results have CGPA >= 8.0
- ✅ Cost displayed (should be ~$0.0015)

---

### **Test 3: Complex Multi-Skill Search**

**Enter:**
```
Need Java backend engineer with Spring Boot, microservices, Docker, and Kubernetes
```

**What to look for:**
- ✅ AI extracts all 4 skills: `Java`, `Spring Boot`, `microservices`, `Docker`, `Kubernetes`
- ✅ Results show skill matching for each:
  - Green checkmark (✅) = Exact match
  - Blue diamond (🔷) = Similar skill
  - Orange square (🔶) = Transferable skill
- ✅ Training plan shown for missing skills
- ✅ Learning timeline estimated

---

### **Test 4: Include Similar Skills**

**Steps:**
1. Enter any search query (e.g., "React developer")
2. Check the **"Include candidates with similar skills"** checkbox
3. Click "Search"

**What to look for:**
- ✅ More results returned
- ✅ TIER_2 and TIER_3 candidates appear
- ✅ Each candidate shows which similar/transferable skills they have
- ✅ Learning weeks required is calculated

---

### **Test 5: Frontend Developer - Urgent**

**Enter:**
```
Frontend developer needed urgently - React, Angular, TypeScript
```

**What to look for:**
- ✅ All three skills extracted
- ✅ Results sorted by deployment readiness:
  - "immediate" at the top
  - "short_term" next
  - "medium_term" / "long_term" at bottom
- ✅ "Deployment Readiness" badge shows color:
  - Green = immediate
  - Blue = short_term
  - Yellow = medium_term
  - Red = long_term

---

## 📊 **STEP 5: Verify AI Indicators**

### **Look for these UI elements:**

1. **🤖 AI-Powered Badge**
   - Should appear near search box
   - Indicates AI is active

2. **💰 Cost Indicator**
   - Shows at bottom of results
   - Format: "Search cost: $0.0015"
   - Should be < $0.03

3. **🎯 Parsed Requirements Panel**
   - Shows extracted skills in tags/chips
   - Shows extracted CGPA if mentioned
   - Shows extracted graduation year if mentioned

4. **📈 Match Score**
   - Each candidate has a score 0-100
   - Higher score = better match
   - Color coded (green = high, yellow = medium, red = low)

5. **🏆 Tier Badges**
   - TIER_1_EXACT (gold/green)
   - TIER_2_SIMILAR (blue)
   - TIER_3_TRANSFERABLE (orange)

6. **📚 Training Plan**
   - Click "View Training Plan" on any candidate
   - Shows step-by-step learning path
   - Shows estimated weeks per skill
   - Shows difficulty level

---

## 🐛 **STEP 6: Check Browser Console**

### **Open Developer Tools:**
- **Chrome/Edge:** Press `F12` or `Ctrl+Shift+I`
- **Firefox:** Press `F12`
- **Safari:** Press `Cmd+Option+I`

### **Go to Console tab**

### **Look for:**

**✅ GOOD (No errors):**
```
GET /api/v1/talent-search/search?query=... 200 OK
Response: { total_found: 3, results: [...], cost_analysis: {...} }
```

**❌ BAD (Errors to report):**
```
GET /api/v1/talent-search/search 500 Internal Server Error
TypeError: Cannot read property 'skill' of undefined
```

---

## 🎯 **STEP 7: Test Edge Cases**

### **Test 1: Empty Search**
- Leave search box empty
- Click "Search"
- **Expected:** Error message or validation prompt

### **Test 2: No Results**
- Search for: "Quantum Computing Expert with 20 years experience"
- **Expected:** "No candidates found" message

### **Test 3: Very Long Query**
- Enter a paragraph-length query
- **Expected:** AI should still extract skills correctly

### **Test 4: Typos**
- Search for: "Pyhton develper"
- **Expected:** AI should correct to "Python developer"

---

## 📸 **WHAT THE UI SHOULD LOOK LIKE:**

### **Search Box Area:**
```
┌─────────────────────────────────────────────────────┐
│ 🔍  Search for candidates...                       │
│     e.g., "Python developer with Django, CGPA > 8" │
│                                                     │
│ ☑ Include candidates with similar skills           │
│                                          [Search]   │
└─────────────────────────────────────────────────────┘
```

### **Results Area:**
```
🎯 Parsed Requirements:
   Required Skills: [Python] [Django] [React]
   Min CGPA: 7.5
   
💰 Cost: $0.0015  |  📊 Found: 3 candidates

┌─────────────────────────────────────────────────────┐
│ 👤 John Doe                           🥇 TIER_1     │
│ 📧 john@example.com     CGPA: 8.5                   │
│ Match Score: 85/100 ████████████░░░░░               │
│                                                     │
│ ✅ Exact: Python (90%), Django (85%)                │
│ 🔷 Similar: React → Angular (75%)                   │
│                                                     │
│ 🎯 Adaptability: 82/100                             │
│ ⏱ Learning Required: 2.5 weeks                      │
│ 🚀 Deployment: short_term                           │
│                                      [View Details] │
└─────────────────────────────────────────────────────┘
```

---

## 🎊 **SUCCESS CRITERIA:**

Your AI feature is working if:

- ✅ Search completes without errors
- ✅ Parsed requirements show extracted skills
- ✅ Results are categorized into tiers
- ✅ Match scores are calculated
- ✅ Cost is displayed and < $0.03
- ✅ Training plans are generated
- ✅ UI is responsive and looks good

---

## 🔧 **TROUBLESHOOTING:**

### **Issue: "Failed to fetch results"**
**Solution:** Check backend is running on `http://localhost:8000`

### **Issue: "No AI results, showing all candidates"**
**Solution:**
1. Check `server.log` or dedicated `ai_service_*.log`
2. Run `python test_auggie_direct.py` to verify AI
3. Check `AUGGIE_API_KEY` in `.env`

### **Issue: "Parsed requirements are empty"**
**Solution:** AI parsing failed, check logs in `apps/api/logs/ai_service_*.log`

### **Issue: "All candidates show same tier"**
**Solution:** Skill matching not working, check skill data in database

---

## 📝 **NEXT STEPS:**

After frontend testing:
1. ✅ Take screenshots of working feature
2. ✅ Test on different browsers (Chrome, Firefox, Safari)
3. ✅ Test on mobile (responsive design)
4. ✅ Share with team for feedback
5. ✅ Deploy to staging/production

---

**🎉 Enjoy your AI-Powered Talent Search! 🎉**
