# 🚀 **AZURE DEPLOYMENT GUIDE - MAVERICK ASCEND**

## ✅ **WHY AZURE IS BETTER THAN RENDER:**

| Issue | Render | Azure |
|-------|--------|-------|
| **Python Version** | ❌ Python 3.14 (forced, too new) | ✅ **Python 3.11** (you choose!) |
| **Compatibility** | ❌ FastAPI fails with Pydantic v1 | ✅ **Works perfectly!** |
| **Control** | ❌ Limited | ✅ Full control |
| **Free Tier** | ✅ Limited (90 days DB) | ✅ $200 credit + permanent free tier |

---

## 📋 **PREREQUISITES:**

1. **Azure Account** - https://azure.microsoft.com/free
   - $200 free credit for 30 days
   - Free services for 12 months
   - Always-free services after that

2. **Azure CLI** - Install:
   ```powershell
   # Windows:
   winget install Microsoft.AzureCLI
   
   # Or download from:
   # https://aka.ms/installazurecliwindows
   ```

3. **Your GitHub Repo** - Already done! ✅

---

## 🎯 **DEPLOYMENT ARCHITECTURE:**

```
┌─────────────────────────────────────────┐
│           AZURE CLOUD                   │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │   App Service Plan (Free F1)     │  │
│  │                                  │  │
│  │  ┌────────────────────────────┐ │  │
│  │  │  Backend API (Python 3.11) │ │  │
│  │  │  FastAPI + Uvicorn         │ │  │
│  │  │  maverick-api.azurewebsites│ │  │
│  │  └────────────────────────────┘ │  │
│  │                                  │  │
│  │  ┌────────────────────────────┐ │  │
│  │  │  Frontend (Node 18)        │ │  │
│  │  │  Next.js                   │ │  │
│  │  │  maverick-web.azurewebsites│ │  │
│  │  └────────────────────────────┘ │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         SUPABASE (External)             │
│  PostgreSQL Database (Already Setup)    │
└─────────────────────────────────────────┘
```

---

## 🚀 **STEP-BY-STEP DEPLOYMENT:**

### **STEP 1: CREATE AZURE ACCOUNT (5 minutes)**

1. Go to: https://azure.microsoft.com/free
2. Click "**Start free**"
3. Sign in with Microsoft account (or create one)
4. Fill in details:
   - Phone verification
   - Credit card (for verification only, won't be charged)
5. Click "Sign up"
6. You get **$200 free credit**!

---

### **STEP 2: INSTALL AZURE CLI (2 minutes)**

```powershell
# Install Azure CLI
winget install Microsoft.AzureCLI

# Login to Azure
az login

# It will open browser, login there
```

---

### **STEP 3: CREATE RESOURCE GROUP (30 seconds)**

```powershell
# Create resource group
az group create --name maverick-rg --location eastus
```

---

### **STEP 4: CREATE APP SERVICE PLAN (1 minute)**

```powershell
# Create FREE App Service Plan
az appservice plan create \
  --name maverick-plan \
  --resource-group maverick-rg \
  --sku F1 \
  --is-linux

# F1 = Free tier (1 GB RAM, 60 min/day compute)
```

---

### **STEP 5: DEPLOY BACKEND API (5 minutes)**

```powershell
# Create web app for backend
az webapp create \
  --resource-group maverick-rg \
  --plan maverick-plan \
  --name maverick-api-YOUR_NAME \
  --runtime "PYTHON:3.11" \
  --deployment-source-url https://github.com/YOUR_USERNAME/Mavericks-Ascend-Gen-AI \
  --deployment-source-branch master

# Configure startup command
az webapp config set \
  --resource-group maverick-rg \
  --name maverick-api-YOUR_NAME \
  --startup-file "cd apps/api && pip install -r requirements.txt && uvicorn app.main:app --host 0.0.0.0 --port 8000"

# Add environment variables
az webapp config appsettings set \
  --resource-group maverick-rg \
  --name maverick-api-YOUR_NAME \
  --settings \
    DATABASE_URL="postgresql://postgres:CICDp@104400@db.aeogndsqjkbfshofudpk.supabase.co:5432/postgres" \
    SUPABASE_URL="https://aeogndsqjkbfshofudpk.supabase.co" \
    SUPABASE_SERVICE_KEY="YOUR_SUPABASE_KEY" \
    JWT_SECRET="maverick_prod_jwt_2024_xyz" \
    JWT_ALGORITHM="HS256" \
    ACCESS_TOKEN_EXPIRE_MINUTES="1440" \
    ENVIRONMENT="production" \
    AI_ENABLED="false" \
    ALLOWED_ORIGINS="https://maverick-web-YOUR_NAME.azurewebsites.net"
```

**Your API URL:** `https://maverick-api-YOUR_NAME.azurewebsites.net`

---

### **STEP 6: DEPLOY FRONTEND (5 minutes)**

```powershell
# Create web app for frontend
az webapp create \
  --resource-group maverick-rg \
  --plan maverick-plan \
  --name maverick-web-YOUR_NAME \
  --runtime "NODE:18-lts" \
  --deployment-source-url https://github.com/YOUR_USERNAME/Mavericks-Ascend-Gen-AI \
  --deployment-source-branch master

# Configure startup
az webapp config set \
  --resource-group maverick-rg \
  --name maverick-web-YOUR_NAME \
  --startup-file "cd apps/web && npm install && npm run build && npm start"

# Add environment variables
az webapp config appsettings set \
  --resource-group maverick-rg \
  --name maverick-web-YOUR_NAME \
  --settings \
    NEXT_PUBLIC_API_URL="https://maverick-api-YOUR_NAME.azurewebsites.net/api/v1" \
    NEXT_PUBLIC_ENVIRONMENT="production"
```

**Your Frontend URL:** `https://maverick-web-YOUR_NAME.azurewebsites.net`

---

## ✅ **EXPECTED RESULT:**

After 10-15 minutes:
- ✅ Backend API live at: `https://maverick-api-YOUR_NAME.azurewebsites.net`
- ✅ Frontend live at: `https://maverick-web-YOUR_NAME.azurewebsites.net`
- ✅ Using **Python 3.11** (compatible!)
- ✅ All features working!

---

## 💰 **COST BREAKDOWN:**

### **Free Tier (What You Get):**
- ✅ **First 30 days**: $200 credit (free)
- ✅ **After 30 days**: F1 App Service Plan = **FREE** (limited hours)
- ✅ **Database**: Supabase = **FREE** (already using)
- ✅ **Total**: **$0/month!**

### **If You Need More (Optional):**
- B1 Plan: $13/month (always on, no limits)
- Supabase Pro: $25/month (optional)

---

## 🔧 **AZURE VS RENDER:**

| Feature | Render | Azure |
|---------|--------|-------|
| **Python Version** | 3.14 (too new) | ✅ 3.11 (perfect!) |
| **Free Tier** | 750 hrs/month | ✅ Free F1 plan |
| **Database** | 90 days free | ✅ Use Supabase |
| **Control** | Limited | ✅ Full control |
| **Compatibility** | ❌ Fails | ✅ Works! |

---

## 📝 **QUICK START COMMANDS:**

```powershell
# 1. Login
az login

# 2. Create resource group
az group create --name maverick-rg --location eastus

# 3. Create app service plan
az appservice plan create --name maverick-plan --resource-group maverick-rg --sku F1 --is-linux

# 4. Deploy (use Portal for easier setup)
```

---

## 🌐 **ALTERNATIVE: AZURE PORTAL (EASIER!)**

Instead of CLI, use Azure Portal (GUI):

1. Go to: https://portal.azure.com
2. Click "**Create a resource**"
3. Search "**Web App**"
4. Fill in:
   - Name: `maverick-api`
   - Runtime: **Python 3.11**
   - Region: East US
   - Pricing: **F1 (Free)**
5. Click "**Review + Create**"
6. Configure GitHub deployment in "Deployment Center"

**Much easier than CLI!**

---

## 🎯 **NEXT STEPS:**

1. ✅ Create Azure account (get $200 credit)
2. ✅ Use Azure Portal (easier than CLI)
3. ✅ Deploy backend with **Python 3.11**
4. ✅ Deploy frontend
5. ✅ Test and enjoy!

---

**🎉 AZURE WILL WORK - YOU CAN CHOOSE PYTHON 3.11!** ✅
