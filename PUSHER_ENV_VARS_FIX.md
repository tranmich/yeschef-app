# Pusher Environment Variables Fix

**Date:** November 19, 2025  
**Issue:** Pusher presence authentication failing with "app_id should be a string instead it is NoneType"

---

## 🔴 **Problem:**

Pusher environment variables are not set on Railway, causing presence channel authentication to fail.

**Error:**
```
POST /api/v2/pusher/auth 500 (Internal Server Error)
app_id should be a string instead it is a <class 'NoneType'>
```

**Console Logs:**
```
❌ Missing required Pusher environment variables: PUSHER_APP_ID, PUSHER_KEY, PUSHER_SECRET
ValueError: Missing required Pusher environment variables
```

---

## ✅ **Solution:**

### **Step 1: Get Pusher Credentials**

1. Login to [Pusher Dashboard](https://dashboard.pusher.com/)
2. Select your app or create new app
3. Go to "App Keys" tab
4. Copy the following:
   - **app_id** (e.g., `1234567`)
   - **key** (e.g., `abc123def456`)
   - **secret** (e.g., `xyz789abc123`)
   - **cluster** (e.g., `us2`)

### **Step 2: Add to Railway Environment Variables**

1. Go to [Railway Dashboard](https://railway.app/)
2. Select `yeschefapp-production` project
3. Click on your service
4. Go to **Variables** tab
5. Add the following variables:

```bash
PUSHER_APP_ID=your_app_id_here
PUSHER_KEY=your_key_here
PUSHER_SECRET=your_secret_here
PUSHER_CLUSTER=us2
```

**Example:**
```bash
PUSHER_APP_ID=1234567
PUSHER_KEY=abc123def456ghi789
PUSHER_SECRET=xyz789abc123def456
PUSHER_CLUSTER=us2
```

### **Step 3: Restart Railway Service**

After adding variables, Railway will automatically restart. If not:
1. Go to **Deployments** tab
2. Click **Redeploy**

---

## 🧪 **Testing After Fix:**

### **1. Check Server Logs**

Look for this on Railway startup:
```
✅ Pusher initialized - App ID: 123456***, Cluster: us2
```

### **2. Test Presence Channel in Browser**

Open browser console at `https://yeschefapp.io/app`:

**Before fix:**
```
POST /api/v2/pusher/auth 500 (Internal Server Error)
❌ Presence subscription error: {type: 'AuthError'}
```

**After fix:**
```
POST /api/v2/pusher/auth 200 (OK)
✅ Auth successful
👥 Subscribed to presence channel: presence-household-11
```

### **3. Verify Online Users Display**

1. Login as user 1 on one browser
2. Login as user 2 on another browser/device
3. Both should see each other in the presence bar
4. Avatars should show online users

---

## 🔍 **Backend Validation:**

The code now validates environment variables on startup:

```python
# app/services/pusher_service.py

def __init__(self):
    # Validate required Pusher environment variables
    app_id = os.getenv('PUSHER_APP_ID')
    key = os.getenv('PUSHER_KEY')
    secret = os.getenv('PUSHER_SECRET')
    
    missing_vars = []
    if not app_id:
        missing_vars.append('PUSHER_APP_ID')
    if not key:
        missing_vars.append('PUSHER_KEY')
    if not secret:
        missing_vars.append('PUSHER_SECRET')
    
    if missing_vars:
        error_msg = f"Missing required Pusher env vars: {', '.join(missing_vars)}"
        logger.error(f"❌ {error_msg}")
        raise ValueError(error_msg)
```

If any variables are missing, the server will log the error clearly.

---

## 📋 **Environment Variables Checklist:**

### **Required for Pusher:**
- [x] `PUSHER_APP_ID` - Your Pusher app ID
- [x] `PUSHER_KEY` - Your Pusher key
- [x] `PUSHER_SECRET` - Your Pusher secret
- [x] `PUSHER_CLUSTER` - Your Pusher cluster (default: us2)

### **Already Set (from previous deployment):**
- [x] `DATABASE_URL` - PostgreSQL connection string
- [x] `JWT_SECRET_KEY` - JWT token secret
- [x] `FRONTEND_URL` - Frontend domain for CORS
- [x] `ALLOWED_ORIGINS` - CORS whitelist

---

## 🎯 **Expected Results:**

After adding environment variables:

1. ✅ **Server starts successfully** - No Pusher initialization errors
2. ✅ **Presence auth works** - 200 response from `/api/v2/pusher/auth`
3. ✅ **Online users display** - Avatars show in presence bar
4. ✅ **Real-time updates work** - Comments, reactions sync instantly
5. ✅ **Multi-user collaboration** - See other users' cursors/activity

---

## 🔧 **Troubleshooting:**

### **Issue: Still getting 500 error after adding variables**
**Solution:** 
- Check variable names are EXACT (case-sensitive)
- Ensure no extra spaces in values
- Restart Railway service manually

### **Issue: Variables not showing in logs**
**Solution:**
- Wait 2-3 minutes for Railway restart
- Check **Deployments** tab for build status
- View logs in Railway dashboard

### **Issue: "Invalid credentials" error**
**Solution:**
- Double-check Pusher dashboard credentials
- Ensure you copied from correct app
- Verify cluster matches (us2, eu, ap3, etc.)

---

## 📊 **Security Notes:**

- ✅ All Pusher secrets are server-side only
- ✅ Frontend only has public Pusher key
- ✅ Auth endpoint validates JWT before allowing presence
- ✅ Household membership checked before channel access

---

**Status:** Ready to deploy  
**Priority:** HIGH - Blocks real-time collaboration  
**ETA:** 5 minutes (add vars + restart)
