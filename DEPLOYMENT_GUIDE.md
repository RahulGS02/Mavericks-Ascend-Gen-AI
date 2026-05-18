# 🚀 DEPLOYMENT GUIDE: MAVERICK ASCEND TO RENDER

## 📋 **PRE-DEPLOYMENT CHECKLIST**

### ✅ **Step 1: Commit All Changes to Git**

```powershell
# Navigate to project root
cd c:\rahul\GenAi\GEN-AI-project

# Check git status
git status

# Add all files
git add .

# Commit with message
git commit -m "feat: Add assessment endpoints, fix backend errors, prepare for deployment"

# Check if remote exists
git remote -v
```

**If no remote repository exists:**

```powershell
# Create a new repo on GitHub: https://github.com/new
# Then add remote (replace YOUR_USERNAME and YOUR_REPO):
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## 🌐 **STEP 2: CREATE RENDER ACCOUNT**

1. Go to **https://render.com**
2. Click "**Get Started**"
3. Sign up with **GitHub** (easiest option)
4. Authorize Render to access your GitHub repositories

---

## 🎯 **STEP 3: DEPLOY TO RENDER**

### **Option A: Deploy via Blueprint (Recommended)**

1. **In Render Dashboard:**
   - Click "**New +**" → "**Blueprint**"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`
   - Click "**Apply**"

2. **Wait for services to deploy:**
   - ✅ `maverick-postgres` (Database) - ~2 min
   - ✅ `maverick-ascend-api` (Backend) - ~5-7 min
   - ✅ `maverick-ascend-web` (Frontend) - ~5-7 min

### **Option B: Manual Deployment**

#### **1. Create PostgreSQL Database**
- Dashboard → "**New +**" → "**PostgreSQL**"
- Name: `maverick-postgres`
- Database: `maverick_db`
- User: `maverick_user`
- Region: **Singapore** (or closest to you)
- Plan: **Free**
- Click "**Create Database**"

#### **2. Deploy Backend API**
- Dashboard → "**New +**" → "**Web Service**"
- Connect repository → Select `GEN-AI-project`
- Settings:
  - **Name:** `maverick-ascend-api`
  - **Region:** Singapore
  - **Branch:** main
  - **Root Directory:** ` ` (leave empty)
  - **Runtime:** Python 3
  - **Build Command:**
    ```bash
    cd apps/api && pip install --upgrade pip && pip install -r requirements.txt
    ```
  - **Start Command:**
    ```bash
    cd apps/api && uvicorn app.main:app --host 0.0.0.0 --port $PORT
    ```
  - **Plan:** Free

- **Environment Variables** (click "Advanced"):
  ```
  DATABASE_URL = [Copy from maverick-postgres "External Database URL"]
  SUPABASE_URL = [Your Supabase URL]
  SUPABASE_SERVICE_KEY = [Your Supabase Service Key]
  JWT_SECRET = [Generate random 32+ char string]
  JWT_ALGORITHM = HS256
  ACCESS_TOKEN_EXPIRE_MINUTES = 1440
  ENVIRONMENT = production
  AI_ENABLED = false
  ALLOWED_ORIGINS = https://maverick-ascend-web.onrender.com
  MAX_UPLOAD_SIZE = 10485760
  ```

#### **3. Deploy Frontend**
- Dashboard → "**New +**" → "**Web Service**"
- Connect repository
- Settings:
  - **Name:** `maverick-ascend-web`
  - **Region:** Singapore
  - **Branch:** main
  - **Root Directory:** ` ` (leave empty)
  - **Runtime:** Node
  - **Build Command:**
    ```bash
    cd apps/web && npm install && npm run build
    ```
  - **Start Command:**
    ```bash
    cd apps/web && npm start
    ```
  - **Plan:** Free

- **Environment Variables:**
  ```
  NEXT_PUBLIC_API_URL = https://maverick-ascend-api.onrender.com/api/v1
  NEXT_PUBLIC_ENVIRONMENT = production
  ```

---

## 🗄️ **STEP 4: INITIALIZE DATABASE**

After backend is deployed:

1. **Go to Render Dashboard → `maverick-ascend-api` → Shell**

2. **Run database migrations:**
```bash
cd apps/api
alembic upgrade head
```

3. **Seed initial data:**
```bash
python scripts/seed_data.py
```

---

## ✅ **STEP 5: TEST DEPLOYMENT**

### **Your Live URLs:**
- **Frontend:** https://maverick-ascend-web.onrender.com
- **Backend API:** https://maverick-ascend-api.onrender.com
- **API Docs:** https://maverick-ascend-api.onrender.com/docs

### **Test Login:**
1. Go to frontend URL
2. Login with:
   - **HR:** `hr@maverick.com` / `hr123`
   - **Trainer:** `john@mail.com` / `trainer123`

---

## ⚠️ **IMPORTANT NOTES**

### **Free Tier Limitations:**
- ✅ **Render Free Plan:**
  - Spins down after 15 min of inactivity
  - First request after spin-down takes ~30-60 seconds
  - 750 hours/month free (enough for 1 service 24/7)

- ✅ **PostgreSQL Free Plan:**
  - 90 days free trial
  - 1 GB storage
  - After 90 days, upgrade or migrate to Supabase

### **Performance Tips:**
- Use **Supabase** for database (free forever)
- Keep services in same region
- Enable caching where possible

---

## 🔧 **STEP 6: UPDATE CORS SETTINGS**

After deployment, update backend CORS:

1. Go to **Render Dashboard** → `maverick-ascend-api` → Environment
2. Update `ALLOWED_ORIGINS`:
   ```
   https://maverick-ascend-web.onrender.com
   ```
3. Click "**Save Changes**" (will trigger redeploy)

---

## 📊 **MONITORING**

### **Check Logs:**
- Render Dashboard → Service → **Logs** tab
- Real-time logs for debugging

### **Check Metrics:**
- Render Dashboard → Service → **Metrics** tab
- CPU, Memory, Request stats

---

## 🐛 **TROUBLESHOOTING**

### **Issue: Build Fails**
```bash
# Check build logs in Render Dashboard
# Common fixes:
# 1. Check requirements.txt is in apps/api/
# 2. Check package.json is in apps/web/
# 3. Verify build commands have correct paths
```

### **Issue: Database Connection Error**
```bash
# Verify DATABASE_URL is correct
# Format: postgresql://user:password@host:port/database
# Get from: Render Dashboard → Database → "Connection" tab
```

### **Issue: Frontend Can't Connect to Backend**
```bash
# 1. Check NEXT_PUBLIC_API_URL is correct
# 2. Check ALLOWED_ORIGINS includes frontend URL
# 3. Check both services are running
```

---

## 💰 **COST ESTIMATE**

### **Free Tier (Current Setup):**
- ✅ Frontend Web Service: **FREE**
- ✅ Backend API Service: **FREE**
- ✅ PostgreSQL (90 days): **FREE**
- **Total: $0/month for 90 days**

### **After 90 Days:**
- Option 1: Migrate to **Supabase** (free forever)
- Option 2: Upgrade Render PostgreSQL (~$7/month)

---

## 🎉 **NEXT STEPS**

After successful deployment:
1. ✅ Share live URL with users
2. ✅ Set up custom domain (optional)
3. ✅ Enable HTTPS (auto-enabled on Render)
4. ✅ Monitor usage and logs
5. ✅ Plan for database migration after 90 days

---

## 📝 **DEPLOYMENT COMMANDS SUMMARY**

```powershell
# 1. Commit and push
git add .
git commit -m "Deploy to Render"
git push origin main

# 2. In Render:
# - Create services via Blueprint or manually
# - Set environment variables
# - Deploy

# 3. Initialize database (in Render Shell):
cd apps/api
alembic upgrade head
python scripts/seed_data.py

# 4. Test:
# Visit: https://maverick-ascend-web.onrender.com
```

---

**🚀 Your platform will be live and accessible from anywhere!**
