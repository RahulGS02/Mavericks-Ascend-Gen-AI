# Filter Tabs Fix - AI Talent Search

## Problem

When searching for "Python developer with SQL skills", you saw:
- All Results (3) ✅
- Exact Match (3) ✅  
- Currently in Training (0) ❌
- Can Be Trained (0) ❌

## Root Cause

### 1. Backend Only Returns AVAILABLE Candidates
The talent search API pre-filters to only show:
```python
deployment_status == DeploymentStatus.AVAILABLE
profile_status == ProfileStatus.APPROVED
```

So **NO** candidates with `IN_TRAINING` status will ever appear in search results.

### 2. Deployment Status Enum
The database enum for `deployment_status` is:
```python
class DeploymentStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"    # Not deployed yet
    DEPLOYED = "DEPLOYED"      # Currently deployed
    ON_LEAVE = "ON_LEAVE"      # On leave
    TERMINATED = "TERMINATED"  # No longer with company
```

**There is NO `IN_TRAINING` status!**

### 3. All Your Candidates Match Exactly
When you search for "Python developer with SQL", all 3 candidates have:
- Exact Python skills
- Exact SQL skills
- Tier: `TIER_1_EXACT`

So there are NO `TIER_2_SIMILAR` or `TIER_3_TRANSFERABLE` candidates.

## Solution Applied

### Changed Filter Logic:
Instead of filtering by `deployment_status` (which doesn't exist), now filtering by **TIER** (skill match level):

**Old Filters (Wrong):**
- Exact Match → TIER_1_EXACT + AVAILABLE
- In Training → IN_TRAINING status (doesn't exist!)
- Can Be Trained → TIER_2/3 + AVAILABLE

**New Filters (Correct):**
- **Ready Now - Exact Match** → TIER_1_EXACT (has all required skills)
- **Short Training - Similar Skills** → TIER_2_SIMILAR (has similar skills, 1-4 weeks training)
- **Can Be Trained** → TIER_3_TRANSFERABLE (has transferable skills, longer training)

### What Each Tier Means:

**TIER_1_EXACT:**
- Has ALL required skills
- Ready for immediate deployment
- No training needed
- Example: You need Python + SQL, candidate has Python + SQL

**TIER_2_SIMILAR:**
- Has SIMILAR skills (70-95% similarity)
- Needs short training (1-4 weeks typically)
- Example: You need React, candidate has Angular
- Example: You need Java, candidate has C#

**TIER_3_TRANSFERABLE:**
- Has TRANSFERABLE skills (50-70% similarity)
- Needs longer training (1-3 months typically)
- Example: You need Java, candidate has Python
- Example: You need frontend (React), candidate has backend (Node.js)

## Why You See (3, 0, 0)

When you search "Python developer with SQL":

1. **All 3 candidates** have exact Python and SQL skills
2. So all are `TIER_1_EXACT`
3. Therefore:
   - Ready Now: **3 candidates** ✅
   - Short Training: **0 candidates** (none have similar skills)
   - Can Be Trained: **0 candidates** (none have only transferable skills)

## To See Different Results

### Test Search 1: Ask for Skills Your Candidates Don't Have
```
Search: "Java developer with Spring Boot"
```
If your candidates don't have Java:
- Ready Now: 0
- Short Training: Maybe some (if they have C# or similar)
- Can Be Trained: Maybe some (if they have Python or other languages)

### Test Search 2: Mix of Exact and Non-Exact
```
Search: "Python developer with Django and React"
```
If some candidates have Python + Django but not React:
- Ready Now: Those with all 3
- Short Training: Those with Python + Django + Angular (React similar)
- Can Be Trained: Those with Python only

### Test Search 3: See Transferable Skills
```
Search: "Frontend developer with Angular and TypeScript"
```
If your candidates have React instead:
- Ready Now: 0
- Short Training: Candidates with React (similar to Angular)
- Can Be Trained: Candidates with Vue.js or other frameworks

## How to Add More Candidates with Different Skills

To see all filters working, add mavericks with different skill levels:

### Add a Similar Skills Candidate:
```sql
-- Has React instead of Angular (similar skill)
INSERT INTO maverick_skills (skill_name, proficiency_score)
VALUES ('React', 85.0);
```

### Add a Transferable Skills Candidate:
```sql
-- Has Python when you need Java (transferable)
INSERT INTO maverick_skills (skill_name, proficiency_score)
VALUES ('Python', 90.0);
```

## Summary

**The filters now correctly show:**
1. **Ready Now** - Candidates who match exactly (current: 3)
2. **Short Training** - Candidates with similar skills (current: 0 because all match exactly)
3. **Can Be Trained** - Candidates with transferable skills (current: 0 because all match exactly)

This is **working correctly**! Your search found 3 perfect matches, so there are no candidates needing training.

To see the other filters populate, you need to:
1. Search for skills your candidates don't have exactly, OR
2. Add more mavericks with different skills to the database
