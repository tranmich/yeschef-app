# 🚀 Production Deployment Checklist - Vercel

## ✅ **Pre-Deployment Verification**

### **1. Environment Configuration**
- ✅ `.env.production` configured with production API URL
- ✅ `vercel.json` has correct environment variables
- ✅ All API utilities use `getApiUrl()` from `api.js`
- ✅ Backend URL: `https://yeschefapp-production.up.railway.app`

### **2. API Endpoints Verified**
- ✅ `frontend/src/utils/api.js` - Uses env vars with fallback
- ✅ `frontend/src/utils/householdAPI.js` - Imports getApiUrl
- ✅ All components use proper API utilities

### **3. Features Ready**
- ✅ Grocery List Sharing (Phase 2)
- ✅ Meal Plan Sharing (Phase 3)
- ✅ Mobile compatibility fixes
- ✅ Household collaboration system

---

## 📋 **Environment Variables Set**

### **In `.env.production`:**
```bash
REACT_APP_API_URL=https://yeschefapp-production.up.railway.app
REACT_APP_ENVIRONMENT=production
REACT_APP_GA_TRACKING_ID=G-XXXXXXXXXX
```

### **In `vercel.json`:**
```json
{
  "env": {
    "REACT_APP_API_URL": "https://yeschefapp-production.up.railway.app",
    "REACT_APP_ENVIRONMENT": "production",
    "CI": "false",
    "DISABLE_ESLINT_PLUGIN": "true"
  }
}
```

---

## 🔧 **Build Configuration**

### **package.json scripts:**
```json
{
  "scripts": {
    "start": "react-scripts start",
    "build": "set DISABLE_ESLINT_PLUGIN=true && react-scripts build",
    "test": "react-scripts test"
  }
}
```

### **vercel.json settings:**
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "build",
  "framework": "create-react-app"
}
```

---

## 🚀 **Deployment Steps**

### **Step 1: Local Build Test**
```powershell
cd "D:\Mik\Downloads\Me Hungie\frontend"
npm run build
```
✅ Verify build completes without errors

### **Step 2: Commit Changes**
```powershell
cd "D:\Mik\Downloads\Me Hungie"

# Check status
git status

# Add all new files
git add frontend/src/components/ShareResourceModal.js
git add frontend/src/components/ShareResourceModal.css
git add frontend/src/utils/householdAPI.js
git add frontend/src/components/GroceryManagerWorkspace.js
git add frontend/src/components/GroceryManagerWorkspace.css
git add frontend/src/components/MealPlannerView.js
git add frontend/src/components/MealPlannerView.css
git add YesChefMobile/src/services/MobileMealPlanAdapter.js

# Add documentation
git add frontend/PHASE_2_COMPLETE.md
git add frontend/PHASE_3_COMPLETE.md
git add YesChefMobile/MEAL_PLAN_ADAPTER_FIX.md

# Commit
git commit -m "feat: Add household collaboration and sharing features

- Add ShareResourceModal component for grocery lists and meal plans
- Integrate household sharing APIs
- Add Share buttons to grocery lists and meal plans
- Fix mobile meal plan adapter for cross-platform compatibility
- Update production environment configuration
- Phases 2 & 3 complete: Grocery List and Meal Plan sharing"

# Push to main
git push origin main
```

### **Step 3: Deploy to Vercel**

#### **Option A: Automatic Deployment (if connected)**
- Push to GitHub triggers automatic deployment
- Monitor at: https://vercel.com/your-username/yeschef-frontend

#### **Option B: Manual Deployment**
```powershell
# Install Vercel CLI (if not installed)
npm install -g vercel

# Login to Vercel
vercel login

# Deploy to production
cd frontend
vercel --prod
```

### **Step 4: Verify Deployment**
1. ✅ Visit deployed URL
2. ✅ Test login functionality
3. ✅ Create/load grocery list
4. ✅ Test Share button on grocery list
5. ✅ Create/load meal plan
6. ✅ Test Share button on meal plan
7. ✅ Verify API calls go to production backend
8. ✅ Check browser console for errors
9. ✅ Test on mobile device

---

## 🔍 **Post-Deployment Verification**

### **Check API Connections:**
Open browser DevTools → Console and verify:
```javascript
📡 Final API URL: https://yeschefapp-production.up.railway.app
```

### **Test Critical Flows:**
- [ ] Login/Register
- [ ] Create grocery list
- [ ] Save grocery list
- [ ] Share grocery list with household
- [ ] Create meal plan
- [ ] Save meal plan  
- [ ] Share meal plan with household
- [ ] Load shared resources on mobile
- [ ] Verify collaboration works

---

## 🌐 **URLs**

- **Production Frontend:** https://yeschef-app.vercel.app (or your domain)
- **Production Backend:** https://yeschefapp-production.up.railway.app
- **Vercel Dashboard:** https://vercel.com/dashboard
- **GitHub Repo:** https://github.com/tranmich/yeschef-app

---

## 🐛 **Common Issues & Solutions**

### **Issue: API calls fail in production**
**Solution:** Check browser console for CORS errors. Backend must allow your Vercel domain.

### **Issue: Environment variables not working**
**Solution:** 
1. Check Vercel dashboard → Settings → Environment Variables
2. Redeploy after adding variables

### **Issue: Build fails**
**Solution:**
1. Check for ESLint errors: `DISABLE_ESLINT_PLUGIN=true` in env
2. Remove `node_modules` and reinstall: `rm -rf node_modules && npm install`
3. Clear cache: `npm cache clean --force`

### **Issue: Household APIs 404**
**Solution:** Verify backend routes are deployed and accessible:
```bash
curl https://yeschefapp-production.up.railway.app/api/households/list
```

---

## 📊 **New Features Deployed**

### **Phase 2: Grocery List Sharing** ✅
- ShareResourceModal component
- Share button in grocery workspace
- Household selection and permissions
- Collaboration API integration

### **Phase 3: Meal Plan Sharing** ✅
- Share button in meal planner
- Reused ShareResourceModal
- Permission levels (Editor/Viewer)
- Cross-platform compatibility

### **Bonus: Mobile Compatibility** ✅
- Fixed meal plan adapter
- Web → Mobile data conversion
- Simplified format support

---

## 🎯 **Expected Results**

After deployment, users should be able to:
- ✅ Create and share grocery lists with households
- ✅ Create and share meal plans with households
- ✅ Choose Editor or Viewer permissions
- ✅ Collaborate across web and mobile
- ✅ See shared resources from household members

---

## 📝 **Rollback Plan**

If issues arise:
```powershell
# Rollback to previous deployment in Vercel dashboard
# OR revert git commit
git revert HEAD
git push origin main
```

---

## 🎉 **Success Criteria**

- ✅ Build completes successfully
- ✅ No console errors on load
- ✅ API calls reach production backend
- ✅ Share buttons work on grocery lists
- ✅ Share buttons work on meal plans
- ✅ Household selection modal opens
- ✅ Sharing creates collaborations
- ✅ Mobile compatibility maintained

---

**Ready for deployment!** Follow the steps above to go live! 🚀
