# 🚀 DEPLOYMENT GUIDE: V2 API TO RAILWAY

**Date:** October 20, 2025  
**Goal:** Deploy v2 API alongside existing app with ZERO downtime

---

## 📋 PRE-DEPLOYMENT CHECKLIST

```
[✅] Phase 1-4 completed
[✅] V2 routes integrated with hungie_server.py
[✅] Code pushed to refactor/shadow-implementation branch
[ ] Railway deployment configured
[ ] Environment variables verified
[ ] Deployment tested
[ ] Mobile app updated
```

---

## 🎯 DEPLOYMENT STRATEGY

**We're using a SAFE deployment approach:**

1. **Deploy to Railway from refactor branch**
2. **Test v2 endpoints live**
3. **If working:** Merge to main
4. **If broken:** Revert easily (just switch branch back)

**Why this is safe:**
- Old endpoints continue to work (`/api/recipes`)
- New endpoints added alongside (`/api/v2/recipes`)
- Can rollback instantly
- Zero downtime

---

## 📝 STEP-BY-STEP DEPLOYMENT

### **Step 1: Merge refactor branch to main**

```bash
# On your local machine:
cd "d:\Mik\Downloads\Me Hungie"

# Switch to main branch
git checkout main

# Merge the refactor branch
git merge refactor/shadow-implementation

# Push to GitHub
git push origin main
```

### **Step 2: Deploy to Railway**

**Option A: Automatic Deployment (if connected to GitHub)**
Railway will automatically deploy when you push to main!

**Option B: Manual Deployment**
1. Go to Railway dashboard
2. Select your YesChef project
3. Go to "Deployments"
4. Click "Deploy Now"
5. Wait for deployment to complete (~2-3 minutes)

### **Step 3: Verify Deployment**

Once deployed, test these endpoints:

```bash
# Replace YOUR_APP_URL with your Railway URL
# Example: https://yeschef-production.up.railway.app

# Test old endpoint (should still work!)
curl https://YOUR_APP_URL/api/direct-test

# Test v2 health check
curl https://YOUR_APP_URL/api/v2/health

# Test v2 users
curl https://YOUR_APP_URL/api/v2/users/11

# Test v2 recipes (THE STAR!)
curl https://YOUR_APP_URL/api/v2/recipes/user/11/stats
```

**Expected results:**
- All old endpoints: ✅ Still working
- All v2 endpoints: ✅ Working!

---

## 🔍 TESTING LIVE ENDPOINTS

### **Quick Test Script:**

```bash
# Set your Railway URL
$RAILWAY_URL = "https://yeschef-production.up.railway.app"

# Test old endpoint
Invoke-WebRequest "$RAILWAY_URL/api/direct-test"

# Test v2 health
Invoke-WebRequest "$RAILWAY_URL/api/v2/health"

# Test v2 users
Invoke-WebRequest "$RAILWAY_URL/api/v2/users/11"

# Test v2 recipes with stats
Invoke-WebRequest "$RAILWAY_URL/api/v2/recipes/user/11/stats"
```

### **What to Look For:**

✅ **Success indicators:**
- HTTP 200 status codes
- JSON responses
- `"success": true` in v2 responses
- Old endpoints still return data

❌ **Failure indicators:**
- 500 errors
- Connection refused
- Import errors in logs
- Missing database connection

---

## 🐛 TROUBLESHOOTING

### **Problem: v2 endpoints return 404**

**Solution:** Check Railway logs for import errors

```bash
# In Railway dashboard:
1. Go to your project
2. Click "View Logs"
3. Look for errors starting with "❌"
```

**Common issues:**
- Missing `app/` directory in deployment
- Import path errors
- Missing dependencies

**Fix:**
```bash
# Make sure all files are committed:
git status
git add .
git commit -m "Fix: Add missing files"
git push origin main
```

### **Problem: Database connection errors**

**Solution:** Verify environment variables in Railway

```bash
# In Railway dashboard:
1. Go to "Variables" tab
2. Verify DATABASE_URL is set
3. Verify all other env vars from .env
```

### **Problem: Old endpoints broken**

**Solution:** IMMEDIATE ROLLBACK!

```bash
# In Railway dashboard:
1. Go to "Deployments"
2. Find previous working deployment
3. Click "Redeploy"

# Then investigate the issue locally
```

---

## 📱 UPDATING MOBILE APP

Once v2 API is deployed and tested, update your mobile app:

### **Step 1: Create API config file**

```javascript
// YesChefMobile/src/config/api.js
export const API_CONFIG = {
  USE_V2_API: false, // Start with false!
  V1_BASE_URL: 'https://yeschef-production.up.railway.app/api',
  V2_BASE_URL: 'https://yeschef-production.up.railway.app/api/v2'
};

export function getApiUrl(endpoint) {
  const baseUrl = API_CONFIG.USE_V2_API 
    ? API_CONFIG.V2_BASE_URL 
    : API_CONFIG.V1_BASE_URL;
  return `${baseUrl}${endpoint}`;
}
```

### **Step 2: Update ONE screen to test**

```javascript
// YesChefMobile/src/screens/RecipeListScreen.js
import { API_CONFIG, getApiUrl } from '../config/api';

async function loadRecipes(userId) {
  if (API_CONFIG.USE_V2_API) {
    // Use new v2 endpoint
    const response = await fetch(
      `${API_CONFIG.V2_BASE_URL}/recipes/user/${userId}/stats`
    );
    const result = await response.json();
    
    if (result.success) {
      return {
        recipes: result.data.recipes,
        stats: result.data.stats
      };
    }
  } else {
    // Use old endpoint
    const response = await fetch(
      `${API_CONFIG.V1_BASE_URL}/recipes/${userId}`
    );
    return await response.json();
  }
}
```

### **Step 3: Test with feature flag**

1. Set `USE_V2_API: true`
2. Test on your device
3. If works: Great! Migrate next screen
4. If breaks: Set back to `false`, investigate

---

## ✅ SUCCESS CRITERIA

**You know deployment succeeded when:**

✅ Old endpoints still work (`/api/recipes`)  
✅ New endpoints work (`/api/v2/recipes/user/11/stats`)  
✅ Mobile app can fetch data from v2  
✅ No errors in Railway logs  
✅ Database queries working  
✅ Response times reasonable (<500ms)  

---

## 📊 MONITORING

### **After deployment, monitor:**

1. **Railway logs** - Watch for errors
2. **Response times** - Should be fast (~100-300ms)
3. **Mobile app** - Test all features
4. **User feedback** - Check with your 6 testers

### **Success metrics:**

```
Old API (/api/*):
  - Still working ✅
  - Same response times ✅
  - No errors ✅

New API (/api/v2/*):
  - Working ✅
  - Faster (1 call vs 3) ✅
  - Duplicate detection working ✅
```

---

## 🎉 POST-DEPLOYMENT

Once v2 API is deployed and tested:

1. **Update documentation** with new endpoints
2. **Migrate mobile app** screen by screen
3. **Monitor performance** for first few days
4. **Collect feedback** from test users
5. **Plan next features** (meal plans, grocery lists)

---

## 🔄 ROLLBACK PLAN

**If something goes wrong:**

### **Immediate Rollback (< 1 minute):**

1. Go to Railway dashboard
2. Click "Deployments"
3. Find last working deployment
4. Click "Redeploy"
5. Done! ✅

### **Code Rollback:**

```bash
# Local machine:
git checkout main
git revert HEAD
git push origin main
# Railway will auto-deploy the revert
```

---

## 📞 GETTING HELP

**If you run into issues:**

1. Check Railway logs first
2. Test endpoints with curl/Postman
3. Verify environment variables
4. Check GitHub issues (if any)
5. Roll back if needed

**Common questions:**
- **"v2 endpoints return 500"** → Check database connection
- **"Import errors"** → Verify all files committed
- **"Old endpoints broken"** → ROLLBACK IMMEDIATELY!

---

## 🎯 NEXT STEPS

After successful deployment:

**Phase 6: Mobile App Integration**
- Update React Native app to use v2 API
- Implement feature flags
- Test with 6 users
- Collect feedback

**Phase 7: Additional Features**
- Add MealPlanRepository/Service/API
- Add GroceryListRepository/Service/API
- Add authentication/JWT

**Phase 8: Optimization**
- Add caching
- Performance monitoring
- Scale as needed

---

**Ready to deploy?** 🚀

**Recommended order:**
1. Merge to main
2. Deploy to Railway
3. Test live endpoints
4. If works → Update mobile app
5. If breaks → Rollback and debug locally
