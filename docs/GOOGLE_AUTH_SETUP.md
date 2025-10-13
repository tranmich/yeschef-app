# 🔐 Google Authentication Setup Guide

## Overview
This guide walks you through setting up Google OAuth 2.0 authentication for the YesChef mobile app.

---

## 📋 Prerequisites

1. Google Cloud Platform account
2. YesChef backend running (hungie_server.py)
3. YesChef mobile app configured

---

## 🚀 Step 1: Create Google Cloud Project

### 1.1 Go to Google Cloud Console
- Visit: https://console.cloud.google.com/
- Sign in with your Google account

### 1.2 Create New Project
1. Click the project dropdown (top left)
2. Click "New Project"
3. Name: `YesChef Mobile`
4. Click "Create"

---

## 🔧 Step 2: Enable Google+ API

### 2.1 Navigate to APIs & Services
1. In the left sidebar, click "APIs & Services" → "Library"
2. Search for "Google+ API"
3. Click on it and click "Enable"

### 2.2 Enable Other Required APIs
Also enable these if not already enabled:
- Google OAuth2 API
- Google People API (for profile info)

---

## 🔑 Step 3: Create OAuth 2.0 Credentials

### 3.1 Go to Credentials
1. Left sidebar → "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"

### 3.2 Configure OAuth Consent Screen (if prompted)
1. Choose "External" (for testing) or "Internal" (for organization)
2. Fill in:
   - **App name:** YesChef
   - **User support email:** your-email@example.com
   - **Developer contact:** your-email@example.com
3. Click "Save and Continue"
4. Add scopes:
   - `openid`
   - `email`
   - `profile`
5. Add test users (your email) if using External
6. Click "Save and Continue"

### 3.3 Create Web Application Credentials
1. Application type: **Web application**
2. Name: `YesChef Backend`
3. **Authorized redirect URIs:**
   ```
   http://localhost:5000/api/auth/google-mobile/callback
   https://your-railway-domain.up.railway.app/api/auth/google-mobile/callback
   ```
4. Click "Create"
5. **Copy the Client ID and Client Secret** - you'll need these!

---

## 📱 Step 4: Configure Mobile App Deep Links

### 4.1 Android Configuration (app.json)
Already configured in your `app.json`:
```json
{
  "expo": {
    "scheme": "yeschef",
    "android": {
      "intentFilters": [
        {
          "action": "VIEW",
          "data": [
            {
              "scheme": "yeschef",
              "host": "google-auth"
            }
          ],
          "category": ["BROWSABLE", "DEFAULT"]
        }
      ]
    }
  }
}
```

### 4.2 iOS Configuration (app.json)
Already configured in your `app.json`:
```json
{
  "expo": {
    "scheme": "yeschef",
    "ios": {
      "bundleIdentifier": "com.yeschef.mobile"
    }
  }
}
```

---

## 🔐 Step 5: Configure Backend Environment Variables

### 5.1 Update `.env` File
Add these to your `.env` file in the project root:

```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here

# JWT Secret (for access tokens)
JWT_SECRET_KEY=your-very-secure-random-key-here

# Optional: Override base URL for production
# BASE_URL=https://your-railway-domain.up.railway.app
```

### 5.2 Generate JWT Secret Key
Run this in Python terminal:
```python
import secrets
print(secrets.token_hex(32))
```

### 5.3 Add to Flask App Configuration
The backend should already load these from `.env`, but verify in `hungie_server.py`:

```python
# In hungie_server.py (should already exist)
app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')
app.secret_key = os.getenv('JWT_SECRET_KEY', 'fallback-key')
```

---

## ✅ Step 6: Test the Setup

### 6.1 Start Backend
```bash
cd "D:\Mik\Downloads\Me Hungie"
venv\Scripts\activate
python hungie_server.py
```

### 6.2 Test in Mobile App
1. Open YesChef mobile app
2. Tap "Continue with Google"
3. Browser opens with Google sign-in
4. Sign in with your Google account
5. App should redirect back and log you in!

---

## 🐛 Troubleshooting

### Issue: "redirect_uri_mismatch" Error

**Solution:** Make sure your redirect URI EXACTLY matches what's in Google Console:
```
http://localhost:5000/api/auth/google-mobile/callback
```

### Issue: "access_denied" Error

**Solution:** 
1. Check that your email is added as a test user in OAuth consent screen
2. Make sure scopes (email, profile, openid) are enabled

### Issue: App Doesn't Redirect Back

**Solution:**
1. Check that `yeschef://` scheme is configured in app.json
2. Rebuild the app after changing app.json
3. Check deep link is working: `yeschef://google-auth-success`

### Issue: "Invalid client" Error

**Solution:**
1. Double-check GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in `.env`
2. Restart the backend server after updating `.env`
3. Make sure there are no extra spaces or quotes in the values

---

## 🚀 Production Deployment (Railway)

### Update Railway Environment Variables
1. Go to Railway project
2. Navigate to Variables tab
3. Add:
   ```
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   JWT_SECRET_KEY=your-jwt-secret
   ```
4. Update redirect URI in Google Console to include Railway URL:
   ```
   https://your-app.up.railway.app/api/auth/google-mobile/callback
   ```

---

## 📝 Current Implementation Status

✅ **Backend:**
- Google OAuth routes configured (`/api/auth/google-mobile`)
- Callback handler implemented
- User creation/linking logic ready
- JWT token generation working

✅ **Mobile App:**
- Deep link listener configured
- Google Sign-In button UI ready
- Token storage implemented
- Auto-login after OAuth success

🔧 **Needs Configuration:**
- [ ] Add Google Client ID and Secret to `.env`
- [ ] Update redirect URIs in Google Console
- [ ] Test end-to-end flow
- [ ] Deploy to Railway with environment variables

---

## 🎯 Next Steps

1. **Copy your Google credentials** from Google Cloud Console
2. **Add to `.env`** file
3. **Restart backend** server
4. **Test** Google sign-in in mobile app
5. **Deploy to Railway** when ready

---

## 📚 Additional Resources

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Expo Deep Linking Guide](https://docs.expo.dev/guides/linking/)
- [Flask OAuth Documentation](https://flask-oauthlib.readthedocs.io/)

---

**Questions?** Check the troubleshooting section or reach out for help!
