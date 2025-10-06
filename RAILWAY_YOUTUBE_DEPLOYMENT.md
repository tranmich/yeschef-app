# 🚀 Deploy YouTube Import to Railway

## ❌ Current Issue
Your mobile app connects to Railway, but Railway doesn't have the required environment variables for YouTube import.

## ✅ Solution: Add Environment Variables to Railway

### Step 1: Add Variables to Railway

1. Go to [Railway Dashboard](https://railway.app/)
2. Select your **YesChef project**
3. Click on the **Variables** tab
4. Add these two variables:

```bash
YOUTUBE_API_KEY=AIzaSyCS2EYGr7M1EuHG5JKRPpcboFPuV_J00K4
```bash
DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-proj-... (your actual key)
JWT_SECRET_KEY=your-secret-key
```
```

### Step 2: Update requirements.txt (if needed)

Make sure Railway installs the YouTube packages. Check if these are in `requirements.txt`:

```txt
google-api-python-client==2.184.0
youtube-transcript-api==1.2.2
isodate==0.7.2
openai>=1.0.0
```

### Step 3: Deploy to Railway

After adding environment variables:
1. Railway will automatically redeploy
2. Wait 2-3 minutes for deployment to complete
3. Test YouTube import from mobile app!

---

## 🧪 Alternative: Test Locally First

### Option A: Use Local Server Temporarily

1. **Find your local IP address:**
   ```powershell
   ipconfig
   ```
   Look for "IPv4 Address" (e.g., `192.168.1.100`)

2. **Update mobile app to use local server:**
   
   File: `YesChefMobile/src/services/YesChefAPI.js`
   ```javascript
   // Temporarily comment out Railway URL
   // this.baseURL = 'https://yeschefapp-production.up.railway.app';
   this.baseURL = 'http://192.168.1.100:5000'; // Your local IP
   ```

3. **Make sure Flask is running:**
   ```bash
   python hungie_server.py
   ```

4. **Test YouTube import** in Expo Go

5. **Revert when done:**
   ```javascript
   this.baseURL = 'https://yeschefapp-production.up.railway.app';
   // this.baseURL = 'http://192.168.1.100:5000';
   ```

---

## 📊 Verify Railway Deployment

After adding variables to Railway, verify they're set:

1. **Check Railway logs:**
   - Go to Railway dashboard
   - Click "Deployments"
   - View latest deployment logs
   - Look for: `✅ YouTubeRecipeExtractor initialized`

2. **Test via API:**
   ```bash
   curl https://yeschefapp-production.up.railway.app/api/health
   ```
   
   Should show:
   ```json
   {
     "capabilities": {
       "recipe_import": true,
       ...
     }
   }
   ```

---

## ✅ Testing Checklist

After Railway is updated:

- [ ] Environment variables added to Railway
- [ ] Railway deployment completed successfully
- [ ] Flask logs show YouTube extractor initialized
- [ ] Mobile app connects to Railway URL
- [ ] Import YouTube URL in mobile app
- [ ] See ingredients and instructions in preview
- [ ] Save recipe successfully

---

## 🎯 Expected Result

When working correctly:

1. **User pastes YouTube URL** in mobile app
2. **Backend detects** it's a YouTube URL
3. **YouTube API extracts** video metadata + transcript
4. **OpenAI GPT-4 parses** into structured recipe
5. **Mobile app shows** complete recipe with:
   - ✅ Title
   - ✅ Description
   - ✅ 14 ingredients with quantities
   - ✅ 8 cooking steps
   - ✅ Source attribution (YouTube channel)

---

## 💰 Costs

- **YouTube API**: FREE (10,000 videos/day)
- **OpenAI GPT-4**: ~$0.02 per video
- **Railway**: No additional cost

---

## 🐛 Troubleshooting

### Issue: "extraction_method": "adaptive_fallback"
**Cause**: YouTube extractor not initialized
**Fix**: Add `YOUTUBE_API_KEY` to Railway variables

### Issue: Empty ingredients/instructions
**Cause**: OpenAI API key missing
**Fix**: Add `OPENAI_API_KEY` to Railway variables

### Issue: "YouTube extraction not available"
**Cause**: Missing Python packages
**Fix**: Ensure `requirements.txt` has all YouTube packages

---

## 📝 Next Steps

1. **Add variables to Railway** (5 minutes)
2. **Wait for deployment** (2-3 minutes)  
3. **Test YouTube import** in mobile app
4. **Enjoy! 🎉**

Once working, you can import recipes from any YouTube cooking video!
