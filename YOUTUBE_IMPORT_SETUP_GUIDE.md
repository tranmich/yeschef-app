# 🎥 YouTube Recipe Import - Setup Guide

## 📋 Quick Start Checklist

- [ ] Install Python dependencies
- [ ] Get YouTube Data API key
- [ ] Configure environment variables
- [ ] Test YouTube extractor
- [ ] Deploy to Railway

---

## 1️⃣ Install Dependencies

### **Local Development:**
```bash
cd "d:\Mik\Downloads\Me Hungie"
pip install -r requirements.txt
```

### **What gets installed:**
- `google-api-python-client` - YouTube Data API v3 client
- `youtube-transcript-api` - Transcript/caption fetching
- `isodate` - ISO 8601 duration parsing
- `openai` - Already installed (for recipe parsing)

---

## 2️⃣ Get YouTube Data API Key (5 minutes)

### **Step-by-Step:**

1. **Go to Google Cloud Console:**
   - Visit: https://console.cloud.google.com/

2. **Create a new project:**
   ```
   Click "Select a project" → "New Project"
   Project name: "YesChef Recipe Import"
   Click "Create"
   ```

3. **Enable YouTube Data API v3:**
   ```
   Search for "YouTube Data API v3" in the search bar
   Click "YouTube Data API v3"
   Click "Enable"
   ```

4. **Create API credentials:**
   ```
   Go to: APIs & Services → Credentials
   Click "+ CREATE CREDENTIALS" → "API Key"
   Copy the API key
   ```

5. **Restrict the API key (recommended):**
   ```
   Click on the created API key
   Under "API restrictions":
   - Select "Restrict key"
   - Check "YouTube Data API v3"
   - Click "Save"
   ```

### **Cost & Limits:**
- ✅ **FREE** - No credit card required
- ✅ **10,000 quota/day** (free tier)
- ✅ Each video import costs ~3 quota = ~3,300 videos/day possible

---

## 3️⃣ Configure Environment Variables

### **Local Development (.env file):**

Add to your `.env` file:
```bash
# YouTube Data API v3
YOUTUBE_API_KEY=your_youtube_api_key_here

# OpenAI (you should already have this)
OPENAI_API_KEY=your_openai_key_here
```

### **Railway Production:**

1. **Go to Railway Dashboard:**
   - https://railway.app/dashboard

2. **Select your YesChef project**

3. **Go to Variables tab**

4. **Add new variable:**
   ```
   Variable: YOUTUBE_API_KEY
   Value: your_youtube_api_key_here
   ```

5. **Click "Add" and redeploy**

---

## 4️⃣ Test YouTube Extractor Locally

### **Quick Test Script:**

```bash
# Test the YouTube extractor standalone
python core_systems/youtube_recipe_extractor.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### **Example Test URLs:**
```python
# Binging with Babish (usually has great descriptions + captions)
https://www.youtube.com/watch?v=3AAdKl1UYZs

# Gordon Ramsay (professional, clear instructions)
https://youtu.be/GkAmq8xdDcA

# J. Kenji López-Alt (detailed, technical)
https://www.youtube.com/watch?v=hpiIWMWWVco
```

### **Expected Output:**
```
🎥 Testing YouTube Recipe Extractor
URL: https://www.youtube.com/watch?v=abc123

✅ Extraction successful!

Video Data:
  Title: Perfect Scrambled Eggs
  Channel: Gordon Ramsay
  Duration: 273s
  Has Transcript: True

Combined Text Preview (first 500 chars):
=== VIDEO TITLE ===
Perfect Scrambled Eggs

=== CHANNEL ===
Gordon Ramsay

=== VIDEO DESCRIPTION ===
Ingredients:
- 3 eggs
- 1 tablespoon butter
...
```

---

## 5️⃣ Test Full Import Flow

### **Test via Python:**

```python
import os
os.environ['YOUTUBE_API_KEY'] = 'your_key_here'
os.environ['OPENAI_API_KEY'] = 'your_key_here'

from core_systems.recipe_importer import UniversalRecipeImporter, ImportRequest

# Create importer
importer = UniversalRecipeImporter()

# Test YouTube import
request = ImportRequest(
    source_type='url',
    source_data='https://www.youtube.com/watch?v=abc123',
    user_id=1  # Your test user ID
)

result = importer.import_recipe(request)

if result.success:
    print("✅ Recipe imported successfully!")
    print(f"Title: {result.recipe_data['title']}")
    print(f"Ingredients: {len(result.recipe_data['ingredients'])} items")
    print(f"Instructions: {len(result.recipe_data['instructions'])} steps")
else:
    print(f"❌ Import failed: {result.errors}")
```

### **Test via Mobile App:**

1. Open YesChef mobile app
2. Go to Recipe Collection screen
3. Tap import URL field
4. Paste: `https://www.youtube.com/watch?v=abc123`
5. Tap "Import Recipe"
6. Wait 5-15 seconds
7. Review screen should appear with extracted recipe

---

## 6️⃣ Deploy to Railway

### **Option A: Automatic (Git push):**

```bash
git add .
git commit -m "Add YouTube recipe import support"
git push origin main
```

Railway will automatically:
- Install new dependencies from requirements.txt
- Restart with new code
- Use YOUTUBE_API_KEY from environment

### **Option B: Manual Deploy:**

1. Go to Railway dashboard
2. Click "Deploy"
3. Wait for deployment to complete
4. Check logs for: `✅ YouTubeRecipeExtractor initialized`

---

## 7️⃣ Verify Production

### **Check Backend Logs:**

In Railway logs, you should see:
```
✅ AdaptiveRecipeExtractor initialized
✅ IngredientIntelligenceEngine initialized
✅ UniversalSearchEngine initialized
✅ WebRecipeExtractor initialized
✅ YouTubeRecipeExtractor initialized  <-- New!
```

### **Test Production Import:**

1. Open mobile app (production build)
2. Import a YouTube URL
3. Check Railway logs for:
   ```
   🎥 Detected YouTube URL - using YouTube extractor
   ✅ Extracted YouTube content
   🤖 Parsing recipe with OpenAI...
   ✅ OpenAI successfully parsed recipe
   ```

---

## 🐛 Troubleshooting

### **"YouTube API key not configured"**
- Check .env file has `YOUTUBE_API_KEY=...`
- Check Railway environment variables
- Verify API key is valid (test in browser)

### **"Could not retrieve transcript"**
- Video may not have captions enabled
- Try a different video with auto-generated captions
- Check video is public (not private/unlisted)

### **"OpenAI API error"**
- Check `OPENAI_API_KEY` is set
- Verify OpenAI account has credits
- Check API key permissions

### **"YouTube API quota exceeded"**
- You've hit 10,000 daily quota
- Wait until midnight Pacific Time for reset
- Or upgrade to paid quota

### **Import takes too long (>30 seconds)**
- Video might be very long (>20 minutes)
- Transcript might be huge
- Try a shorter cooking video (5-10 minutes ideal)

---

## 📊 Monitoring & Costs

### **YouTube API Usage:**

Check quota usage:
1. Go to Google Cloud Console
2. APIs & Services → Dashboard
3. Click "YouTube Data API v3"
4. View quota usage graph

### **OpenAI Costs:**

Each YouTube import uses:
- Input tokens: ~2,000-5,000 ($0.01-0.025)
- Output tokens: ~500-1,000 ($0.015-0.03)
- **Total: ~$0.02-0.05 per video**

**Budget estimate:**
- 100 imports/month = $2-5/month
- 1,000 imports/month = $20-50/month

---

## ✅ Success Criteria

Your YouTube import is working correctly when:

1. ✅ Backend logs show `YouTubeRecipeExtractor initialized`
2. ✅ Can import YouTube URL from mobile app
3. ✅ Recipe appears in review screen with:
   - Accurate title
   - Complete ingredients list
   - Clear step-by-step instructions
   - Source attribution to YouTube video
4. ✅ User can edit and save to collection
5. ✅ Thumbnail from video displays in app

---

## 🎯 Next Steps

Once basic YouTube import is working:

1. **Add visual feedback** in mobile app when YouTube URL detected
2. **Implement caching** to avoid re-processing same video
3. **Add timestamp links** to connect instructions with video moments
4. **Support playlists** for batch imports
5. **Add channel following** to auto-import new videos

---

## 📚 API Documentation

- **YouTube Data API v3:** https://developers.google.com/youtube/v3
- **youtube-transcript-api:** https://github.com/jdepoix/youtube-transcript-api
- **OpenAI API:** https://platform.openai.com/docs

---

## 🆘 Need Help?

**Common issues:**
- API key setup
- Transcript availability
- OpenAI parsing quality
- Mobile app testing

**Debug checklist:**
1. Check environment variables are set
2. Test extractor standalone first
3. Check Railway logs for errors
4. Verify API quotas not exceeded
5. Try different test videos
