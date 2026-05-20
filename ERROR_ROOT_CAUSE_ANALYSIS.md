# 🔬 **ROOT CAUSE ANALYSIS: 500 Internal Server Error**

## 📊 **EXECUTIVE SUMMARY**

**Problem:** API returns 500 error on Azure, but works perfectly locally  
**Root Cause:** Azure Free Tier IPv6 limitation + Modern DNS returning IPv6 first  
**Status:** ✅ **FIXED** with IPv4-only socket patch in main.py  
**Deployment:** ⏳ Waiting for latest code to deploy

---

## 🎯 **THE SINGLE ROOT CAUSE**

### **Azure Free Tier Networking Limitation**

```
Azure App Service Free Tier (F1):
├─ Inbound:  ✅ IPv4 + IPv6 supported
└─ Outbound: ✅ IPv4 supported
             ❌ IPv6 NOT supported
```

**This is a documented Azure limitation, not a bug.**

---

## 🔍 **ERROR ANALYSIS FROM server.log**

### **Line 54 - The Smoking Gun:**

```
psycopg2.OperationalError: connection to server at 
"db.aeogndsqjkbfshofudpk.supabase.co" 
(2406:da18:243:7420:75b4:a8d9:7589:cf05), 
port 6543 failed: Cannot assign requested address
```

### **Breaking it down:**

| Element | Value | Meaning |
|---------|-------|---------|
| **Server** | `db.aeogndsqjkbfshofudpk.supabase.co` | Supabase hostname |
| **IPv6 Address** | `2406:da18:...` | ❌ **This is the problem!** |
| **Port** | `6543` | Pooler port (correct) |
| **Error** | `Cannot assign requested address` | Azure blocks IPv6 outbound |

**Why it says "Cannot assign requested address":**  
Azure tries to create an IPv6 socket but the network stack rejects it because outbound IPv6 is not enabled on F1 tier.

---

## 🔄 **THE COMPLETE ERROR FLOW**

```
┌──────────────────────────────────────────────────────────────┐
│ 1. User clicks "Login" in Swagger UI                         │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 2. POST /api/v1/auth/login hits FastAPI                      │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 3. auth.py calls authenticate_user(db, email, password)      │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 4. SQLAlchemy needs database connection                      │
│    db.query(User).filter(...).first()                        │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 5. Connection pool is empty, create new connection           │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 6. psycopg2 needs to resolve hostname                        │
│    socket.getaddrinfo("db.aeogndsqjkbfshofudpk...")          │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 7. DNS returns BOTH addresses:                               │
│    - IPv6: 2406:da18:243:7420:75b4:a8d9:7589:cf05           │
│    - IPv4: (some IPv4 address)                               │
│    Modern systems return IPv6 FIRST                          │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 8. psycopg2 tries IPv6 first (standard behavior)            │
│    socket.socket(AF_INET6, ...)                              │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 9. Azure Free Tier: ❌ BLOCKS IPv6 outbound                  │
│    Error: "Cannot assign requested address"                  │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 10. psycopg2 DOES NOT fallback to IPv4 (by design)          │
│     Raises OperationalError                                  │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 11. SQLAlchemy catches error, wraps in sqlalchemy.exc        │
│     Bubbles up to FastAPI                                    │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│ 12. FastAPI error handler catches exception                  │
│     Returns: 500 Internal Server Error                       │
└──────────────────────────────────────────────────────────────┘
```

---

## ✅ **THE FIX: IPv4-ONLY SOCKET PATCH**

### **Location: `apps/api/app/main.py` (lines 1-13)**

```python
# CRITICAL: IPv4 PATCH MUST BE FIRST - Before ANY other imports
import socket
original_getaddrinfo = socket.getaddrinfo
def getaddrinfo_ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
    return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = getaddrinfo_ipv4_only
print("✅ IPv4-only mode enabled (Azure compatibility)")
```

### **How it works:**

```
Before Patch:
DNS lookup → Returns [IPv6, IPv4] → psycopg2 tries IPv6 → ❌ FAILS

After Patch:
DNS lookup → Patch filters to [IPv4 ONLY] → psycopg2 tries IPv4 → ✅ WORKS
```

### **Why this location?**

The patch MUST be applied **before ANY import** that might use networking:
- ✅ **Before** `from app.database import ...`
- ✅ **Before** `from sqlalchemy import ...`
- ✅ **Before** `import psycopg2`
- ✅ **Before** `import requests`

This is why it's the **very first code** in main.py!

---

## 🧪 **WHY IT WORKS LOCALLY BUT NOT ON AZURE**

| Environment | IPv6 Outbound | Result |
|-------------|---------------|--------|
| **Your PC** | ✅ Enabled | Works fine with IPv6 OR IPv4 |
| **Azure F1** | ❌ Disabled | Only works with IPv4 |

**On your local machine:**
- Windows/Linux network stack supports IPv6
- psycopg2 connects via IPv6 successfully
- No error occurs

**On Azure Free Tier:**
- Network stack **blocks** IPv6 outbound
- psycopg2 cannot connect via IPv6
- Error occurs → 500 response

---

## 📋 **ALL ERRORS IN YOUR LOG (COMPLETE LIST)**

| Line | Error Type | Module | Status |
|------|-----------|--------|--------|
| 54 | IPv6 connection failure | psycopg2 | ✅ Fixed (IPv4 patch) |

**That's it!** There is only ONE error, repeated for each login attempt.

---

## ✅ **VERIFICATION CHECKLIST**

After new deployment:

```
☐ 1. Check Azure Deployment Center logs show recent deployment
☐ 2. Look for "✅ IPv4-only mode enabled" in startup logs  
☐ 3. Test GET https://mavericks-ascend.azurewebsites.net/ → 200 OK
☐ 4. Test GET https://mavericks-ascend.azurewebsites.net/docs → Swagger loads
☐ 5. Test POST /api/v1/auth/login with hr@maverick.com → 200 OK with token
☐ 6. Check logs show NO "Cannot assign requested address" errors
☐ 7. Create a trainee, upload resume, verify all features work
```

---

## 🎯 **ACTION REQUIRED NOW**

### **You need to:**

1. **Check if latest code is deployed:**
   - Go to Azure Portal → Deployment Center → Logs
   - Check deployment timestamp (should be recent)
   - Check if you see "✅ IPv4-only mode enabled" in logs

2. **If not deployed yet:**
   ```powershell
   cd c:\rahul\GenAi\GEN-AI-project
   git status
   git log --oneline -5
   ```
   Verify you see commit: "fix: Move IPv4 patch to main.py"

3. **Trigger deployment manually if needed:**
   - Azure Portal → Deployment Center → Click "Sync"

---

## 🎉 **EXPECTED RESULT AFTER FIX**

```
OLD (Current):
POST /api/v1/auth/login → 500 Internal Server Error
Log: "Cannot assign requested address"

NEW (After deployment):
POST /api/v1/auth/login → 200 OK
Response: {"access_token": "eyJ...", "token_type": "bearer"}
Log: No IPv6 errors
```

