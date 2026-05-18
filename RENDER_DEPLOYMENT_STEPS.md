# 🚀 RENDER DEPLOYMENT - STEP BY STEP

## ✅ **YOU'VE COMPLETED: GITHUB PUSH**

Great! Now let's deploy to Render.

---

## ❌ **NO GITHUB SECRETS NEEDED!**

**Answer: NO, you do NOT need to configure secrets in GitHub.**

Why?
- ✅ Secrets are configured **directly in Render** dashboard
- ✅ GitHub only stores your code (no sensitive data)
- ✅ Your `.gitignore` already excludes `.env` files
- ✅ Render reads secrets from its own environment variables

**Your `.gitignore` protects:**
- ✅ `.env` files (secrets never pushed)
- ✅ `venv/` (Python dependencies)
- ✅ `node_modules/` (Node dependencies)
- ✅ `.next/` (build files)

---

## 🎯 **RENDER DEPLOYMENT - COMPLETE GUIDE**

### **OVERVIEW:**

You're deploying:
- ✅ **Backend API** → Render Web Service
- ✅ **Frontend** → Render Web Service
- ✅ **Database** → **Use your existing Supabase!** (Already configured)
- ✅ **Storage** → Supabase Storage (Already set up)

**Total Time:** ~10 minutes (simplified since database is ready!)

---

### **STEP 1: CREATE RENDER ACCOUNT (1 minute)**

1. **Go to:** https://render.com

2. **Click:** "Get Started for Free"

3. **Sign in with GitHub:**
   - Click "Continue with GitHub"
   - Authorize Render to access repositories
   - Select "All repositories" or just "maverick-ascend"

4. **You'll see Render Dashboard**

---

### **STEP 2: GET YOUR SUPABASE DATABASE URL (30 seconds)**

**You're already using Supabase - let's use it!**

1. **Go to Supabase Dashboard:**
   - https://supabase.com/dashboard

2. **Select Your Project:**
   - Click on your project

3. **Get Connection String:**
   - Go to "**Settings**" (left sidebar)
   - Click "**Database**"
   - Scroll to "**Connection String**"
   - Select "**URI**" tab
   - Copy the connection string (looks like):
     ```
     postgresql://postgres:CICDp@104400@db.aeogndsqjkbfshofudpk.supabase.co:5432/postgres
     ```
   - **This is your DATABASE_URL** - save it!

**Why use Supabase?**
- ✅ You already have it set up
- ✅ Your data is already there
- ✅ Free forever (not just 90 days)
- ✅ Better performance
- ✅ No migration needed!

---

### **STEP 3: DEPLOY BACKEND API (5 minutes)**

1. **In Render Dashboard:**
   - Click "**New +**" → "**Web Service**"

2. **Connect Repository:**
   - Click "**Configure account**" if needed
   - Select your GitHub repository
   - Click "**Connect**"

3. **Configure Service:**

   | Field | Value |
   |-------|-------|
   | **Name** | `maverick-ascend-api` |
   | **Region** | Singapore |
   | **Branch** | `main` |
   | **Root Directory** | *(leave empty)* |
   | **Runtime** | Python 3 |
   | **Build Command** | `cd apps/api && pip install --upgrade pip && pip install -r requirements.txt` |
   | **Start Command** | `cd apps/api && uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
   | **Instance Type** | **Free** ✅ |

4. **Add Environment Variables:**

   Click "**Advanced**" → "**Add Environment Variable**"

   **Add these one by one:**

   ```
   DATABASE_URL = postgresql://postgres:CICDp@104400@db.aeogndsqjkbfshofudpk.supabase.co:5432/postgres

   SUPABASE_URL = https://aeogndsqjkbfshofudpk.supabase.co

   SUPABASE_SERVICE_KEY = [Get from Supabase → Settings → API → service_role key]

   JWT_SECRET = maverick_ascend_super_secret_jwt_production_2024

   JWT_ALGORITHM = HS256

   ACCESS_TOKEN_EXPIRE_MINUTES = 1440

   ENVIRONMENT = production

   AI_ENABLED = false

   ALLOWED_ORIGINS = https://maverick-ascend-web.onrender.com

   MAX_UPLOAD_SIZE = 10485760

   MAX_RESUME_SIZE = 5242880

   MAX_EXCEL_SIZE = 10485760

   ALLOWED_RESUME_TYPES = application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document

   ALLOWED_EXCEL_TYPES = application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,text/csv
   ```

   **Important Notes:**
   - ✅ `DATABASE_URL` - Use your Supabase connection string (shown above)
   - ✅ `SUPABASE_SERVICE_KEY` - Get from Supabase Dashboard → Settings → API
   - ✅ `JWT_SECRET` - Use a strong random string (32+ characters)
   - ✅ **You're using the SAME database as your local development!**

5. **Click:** "Create Web Service"

6. **Wait ~5-7 minutes** for build and deployment

7. **Check Logs:**
   - Watch the "Logs" tab
   - Should see: "🚀 Maverick Ascend API starting..."
   - Should see: "Application startup complete"

8. **Copy Backend URL:**
   - Look at top of page
   - URL will be: `https://maverick-ascend-api.onrender.com`
   - **Save this** - you'll need it for frontend!

---

### **STEP 4: VERIFY DATABASE (Optional - 30 seconds)**

**Your Supabase database already has everything!**

Since you've been running locally with Supabase:
- ✅ Tables already created
- ✅ Users already seeded (HR, Trainer, etc.)
- ✅ Batches and data already exist
- ✅ **No initialization needed!**

**Optional Check (if you want to verify):**

1. **In Backend Service Page:**
   - Click "**Shell**" tab (top right)
   - Wait for shell to connect

2. **Test Connection:**
   ```bash
   cd apps/api
   python -c "from app.database import engine; print('✅ Connected!' if engine else '❌ Failed')"
   ```

**That's it! Your production backend will use the same database as your local development.**

---

### **STEP 5: DEPLOY FRONTEND (5 minutes)**

1. **In Render Dashboard:**
   - Click "**New +**" → "**Web Service**"

2. **Connect Same Repository**

3. **Configure Service:**

   | Field | Value |
   |-------|-------|
   | **Name** | `maverick-ascend-web` |
   | **Region** | Singapore |
   | **Branch** | `main` |
   | **Root Directory** | *(leave empty)* |
   | **Runtime** | Node |
   | **Build Command** | `cd apps/web && npm install && npm run build` |
   | **Start Command** | `cd apps/web && npm start` |
   | **Instance Type** | **Free** ✅ |

4. **Add Environment Variables:**

   ```
   NEXT_PUBLIC_API_URL = https://maverick-ascend-api.onrender.com/api/v1
   
   NEXT_PUBLIC_ENVIRONMENT = production
   
   NODE_VERSION = 18.17.0
   ```

   **Important:**
   - ✅ Replace the URL with YOUR backend URL from Step 3
   - ✅ Make sure it ends with `/api/v1`

5. **Click:** "Create Web Service"

6. **Wait ~5-7 minutes** for build

7. **Your Frontend URL:**
   - Will be: `https://maverick-ascend-web.onrender.com`

---

### **STEP 6: UPDATE BACKEND CORS (1 minute)**

**After frontend is deployed:**

1. **Go to Backend Service:**
   - Dashboard → `maverick-ascend-api`

2. **Click "Environment" tab (left sidebar)**

3. **Update `ALLOWED_ORIGINS`:**
   - Find the `ALLOWED_ORIGINS` variable
   - Change to your actual frontend URL:
     ```
     https://maverick-ascend-web.onrender.com
     ```
   - Click "Save Changes"

4. **Service will auto-redeploy** (~2 minutes)

---

## ✅ **STEP 7: TEST YOUR LIVE PLATFORM!**

### **Visit Your Platform:**
```
https://maverick-ascend-web.onrender.com
```

### **Test Login:**

**HR User:**
- Email: `hr@maverick.com`
- Password: `hr123`

**Trainer:**
- Email: `john@mail.com`
- Password: `trainer123`

### **Test Features:**
- ✅ Login works
- ✅ Dashboard loads
- ✅ Can view mavericks
- ✅ Can view batches
- ✅ Can enter marks
- ✅ All pages work

---

## 🎉 **YOU'RE LIVE!**

### **Your URLs:**

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | https://maverick-ascend-web.onrender.com | Main app |
| **Backend API** | https://maverick-ascend-api.onrender.com | API server |
| **API Docs** | https://maverick-ascend-api.onrender.com/docs | Swagger UI |
| **Database** | (Internal only) | PostgreSQL |

---

## 📊 **MONITORING YOUR SERVICES**

### **Check Status:**
- Dashboard → Each service shows:
  - ✅ Green dot = Running
  - 🟡 Yellow = Deploying
  - 🔴 Red = Error

### **View Logs:**
- Click service → "Logs" tab
- Real-time logs for debugging

### **View Metrics:**
- Click service → "Metrics" tab
- CPU, Memory, Requests

---

## ⚠️ **IMPORTANT: FREE TIER BEHAVIOR**

### **Services "Spin Down" after 15 minutes of inactivity:**

**What happens:**
- ✅ First visit after idle: ~30-60 seconds to wake up
- ✅ Subsequent visits: Normal speed
- ✅ No data loss (database stays active)

**Fix (if needed):**
- Upgrade to paid plan ($7/month/service for always-on)

---

## 🔧 **TROUBLESHOOTING**

### **Issue: "Application Error" on Frontend**

**Fix:**
1. Check backend is running (green dot)
2. Check `NEXT_PUBLIC_API_URL` is correct
3. Check backend logs for errors

### **Issue: "Cannot connect to API"**

**Fix:**
1. Check `ALLOWED_ORIGINS` in backend includes frontend URL
2. Make sure both services are in same region
3. Check backend logs

### **Issue: "Database connection error"**

**Fix:**
1. Verify `DATABASE_URL` is correct
2. Check database is running (green dot)
3. Make sure you ran `alembic upgrade head`

---

## 🎯 **NEXT STEPS**

After successful deployment:

1. ✅ **Share the link** with users
2. ✅ **Test all features** thoroughly
3. ✅ **Monitor usage** in first few days
4. ✅ **Plan database migration** (after 90 days free tier ends)
5. ✅ **Set up custom domain** (optional)

---

**🚀 YOUR PLATFORM IS NOW LIVE AND ACCESSIBLE WORLDWIDE!**
