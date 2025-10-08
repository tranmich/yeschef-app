# 🎥 YouTube Recipe Import - Detailed Implementation Plan

## 📋 Executive Summary

**Goal**: Add YouTube video recipe import to YesChef's existing recipe import system
**Rationale**: YouTube cooking videos have long-form content with detailed descriptions, timestamps, and captions - perfect for recipe extraction
**Integration Point**: Extends existing `UniversalRecipeImporter` system

---

## 🏗️ Current Architecture Analysis

### **Backend (Python/Flask)**
```
📦 Current Import Flow:
Mobile App → YesChefAPI.importRecipe(url)
           ↓
Flask: /api/recipes/import/url
           ↓
UniversalRecipeImporter.import_recipe()
           ↓
WebRecipeExtractor (BeautifulSoup + AI)
           ↓
AdaptiveRecipeExtractor
           ↓
PostgreSQL Storage
```

**Key Files:**
- `hungie_server.py` - Flask endpoint `/api/recipes/import/url`
- `core_systems/recipe_importer.py` - UniversalRecipeImporter class
- `core_systems/web_recipe_extractor.py` - WebRecipeExtractor class
- `cookbook_processing/adaptive_recipe_extractor.py` - Recipe parsing

### **Mobile App (React Native)**
```
📱 Current UI Flow:
RecipeCollectionScreen
  → Import URL Input
  → YesChefAPI.extractRecipeFromUrl(url)
  → RecipeImportReviewScreen (edit & save)
```

**Key Files:**
- `YesChefMobile/src/screens/RecipeCollectionScreen.js` - Import UI
- `YesChefMobile/src/screens/RecipeImportReviewScreen.js` - Review screen
- `YesChefMobile/src/services/YesChefAPI.js` - API service

---

## 🎯 YouTube Integration Strategy

### **Phase 1: Backend YouTube Extractor**

**Create new module:** `core_systems/youtube_recipe_extractor.py`

```python
"""
🎥 YouTube Recipe Extractor
Extracts recipe content from YouTube cooking videos using:
1. Video metadata (title, description)
2. Captions/transcripts
3. Comments (optional)
4. AI parsing to convert to recipe format
"""

import os
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
import requests
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

@dataclass
class YouTubeVideoData:
    """Structured YouTube video data"""
    video_id: str
    title: str
    description: str
    channel: str
    duration: int  # seconds
    view_count: int
    published_at: str
    transcript: Optional[str] = None
    captions_available: bool = False
    language: str = 'en'
    thumbnail_url: Optional[str] = None

class YouTubeRecipeExtractor:
    """
    Extract recipe information from YouTube cooking videos
    """
    
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.youtube = None
        
        if self.api_key:
            self.youtube = build('youtube', 'v3', developerKey=self.api_key)
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats
        
        Supported formats:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        - https://m.youtube.com/watch?v=VIDEO_ID
        """
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def get_video_metadata(self, video_id: str) -> Optional[YouTubeVideoData]:
        """
        Fetch video metadata using YouTube Data API
        
        Returns:
            YouTubeVideoData with title, description, channel, etc.
        """
        if not self.youtube:
            raise ValueError("YouTube API key not configured")
        
        try:
            # Request video details
            request = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=video_id
            )
            response = request.execute()
            
            if not response.get('items'):
                return None
            
            video = response['items'][0]
            snippet = video['snippet']
            
            return YouTubeVideoData(
                video_id=video_id,
                title=snippet['title'],
                description=snippet['description'],
                channel=snippet['channelTitle'],
                duration=self._parse_duration(video['contentDetails']['duration']),
                view_count=int(video['statistics'].get('viewCount', 0)),
                published_at=snippet['publishedAt'],
                thumbnail_url=snippet['thumbnails']['high']['url']
            )
            
        except Exception as e:
            print(f"Error fetching YouTube metadata: {e}")
            return None
    
    def get_transcript(self, video_id: str, languages=['en', 'en-US']) -> Optional[str]:
        """
        Get video transcript/captions using youtube-transcript-api
        
        Args:
            video_id: YouTube video ID
            languages: List of language codes to try
        
        Returns:
            Full transcript as single string, or None if unavailable
        """
        try:
            # Try to get transcript in preferred languages
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try each language in order
            for lang in languages:
                try:
                    transcript = transcript_list.find_transcript([lang])
                    entries = transcript.fetch()
                    
                    # Combine all text entries
                    full_text = ' '.join([entry['text'] for entry in entries])
                    return full_text
                    
                except Exception:
                    continue
            
            # If no exact match, try any auto-generated English transcript
            try:
                transcript = transcript_list.find_generated_transcript(['en'])
                entries = transcript.fetch()
                full_text = ' '.join([entry['text'] for entry in entries])
                return full_text
            except Exception:
                pass
                
        except Exception as e:
            print(f"Could not retrieve transcript: {e}")
        
        return None
    
    def extract_recipe_content(self, url: str) -> Dict:
        """
        Main extraction method - gets all available content from YouTube video
        
        Returns:
            Dict with video_data, transcript, and combined_text for AI parsing
        """
        # Extract video ID
        video_id = self.extract_video_id(url)
        if not video_id:
            return {
                'success': False,
                'error': 'Invalid YouTube URL'
            }
        
        # Get metadata
        video_data = self.get_video_metadata(video_id)
        if not video_data:
            return {
                'success': False,
                'error': 'Could not fetch video information'
            }
        
        # Get transcript
        transcript = self.get_transcript(video_id)
        video_data.transcript = transcript
        video_data.captions_available = transcript is not None
        
        # Combine all text sources for recipe extraction
        combined_text = self._combine_text_sources(video_data)
        
        return {
            'success': True,
            'video_data': video_data,
            'combined_text': combined_text,
            'source_url': url
        }
    
    def _combine_text_sources(self, video_data: YouTubeVideoData) -> str:
        """
        Intelligently combine title, description, and transcript
        """
        parts = []
        
        # Title (most important)
        parts.append(f"RECIPE TITLE: {video_data.title}")
        
        # Description (often has ingredients list)
        if video_data.description:
            parts.append(f"\\nVIDEO DESCRIPTION:\\n{video_data.description}")
        
        # Transcript (has cooking instructions)
        if video_data.transcript:
            parts.append(f"\\nVIDEO TRANSCRIPT:\\n{video_data.transcript}")
        
        return '\\n'.join(parts)
    
    def _parse_duration(self, iso_duration: str) -> int:
        """Convert ISO 8601 duration (PT1H2M3S) to seconds"""
        import isodate
        try:
            duration = isodate.parse_duration(iso_duration)
            return int(duration.total_seconds())
        except:
            return 0

```

---

### **Phase 2: Integrate with UniversalRecipeImporter**

**Modify:** `core_systems/recipe_importer.py`

```python
class UniversalRecipeImporter:
    def __init__(self):
        # ... existing initialization ...
        
        # Add YouTube extractor
        try:
            from core_systems.youtube_recipe_extractor import YouTubeRecipeExtractor
            self.youtube_extractor = YouTubeRecipeExtractor()
            logger.info("✅ YouTubeRecipeExtractor initialized")
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize YouTubeRecipeExtractor: {e}")
            self.youtube_extractor = None
    
    def import_recipe(self, request: ImportRequest) -> ImportResult:
        """Enhanced to detect and handle YouTube URLs"""
        start_time = datetime.now()
        
        try:
            # Route to appropriate extractor based on source type
            if request.source_type == 'url':
                url = request.source_data
                
                # Check if it's a YouTube URL
                if self._is_youtube_url(url):
                    logger.info(f"🎥 Detected YouTube URL: {url}")
                    return self._import_from_youtube(url, request.user_id, start_time)
                else:
                    # Existing web recipe extraction
                    return self._import_from_url(url, request.user_id, start_time)
            
            # ... rest of existing logic ...
    
    def _is_youtube_url(self, url: str) -> bool:
        """Check if URL is from YouTube"""
        youtube_domains = ['youtube.com', 'youtu.be', 'm.youtube.com']
        return any(domain in url.lower() for domain in youtube_domains)
    
    def _import_from_youtube(self, url: str, user_id: int, start_time) -> ImportResult:
        """
        Import recipe from YouTube video
        
        Flow:
        1. Extract video content (metadata + transcript)
        2. Send to AI for recipe parsing
        3. Process ingredients with IngredientIntelligenceEngine
        4. Save to database
        """
        if not self.youtube_extractor:
            return ImportResult(
                success=False,
                errors=['YouTube extraction not available - missing API key or dependencies']
            )
        
        try:
            # Extract video content
            logger.info(f"🎥 Extracting YouTube video content...")
            extraction_result = self.youtube_extractor.extract_recipe_content(url)
            
            if not extraction_result['success']:
                return ImportResult(
                    success=False,
                    errors=[extraction_result.get('error', 'YouTube extraction failed')]
                )
            
            video_data = extraction_result['video_data']
            combined_text = extraction_result['combined_text']
            
            logger.info(f"✅ Extracted: {video_data.title} ({len(combined_text)} chars)")
            
            # Parse recipe using AI
            logger.info(f"🤖 Parsing recipe with AI...")
            recipe_data = self._parse_recipe_with_ai(combined_text, 'YouTube', url)
            
            if not recipe_data:
                return ImportResult(
                    success=False,
                    errors=['AI recipe parsing failed'],
                    warnings=['Could not extract recipe from video content']
                )
            
            # Enhance with video metadata
            recipe_data['source'] = 'YouTube'
            recipe_data['source_url'] = url
            recipe_data['source_title'] = video_data.title
            recipe_data['source_channel'] = video_data.channel
            recipe_data['thumbnail_url'] = video_data.thumbnail_url
            
            # Process ingredients with existing intelligence
            if self.ingredient_engine and recipe_data.get('ingredients'):
                logger.info(f"🧠 Processing ingredients with IngredientIntelligenceEngine...")
                processed_ingredients = self._process_ingredients(recipe_data['ingredients'])
                recipe_data['ingredients'] = processed_ingredients
            
            # Save to database
            recipe_id = self._save_recipe_to_database(recipe_data, user_id)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ImportResult(
                success=True,
                recipe_id=recipe_id,
                recipe_data=recipe_data,
                confidence=0.85,  # YouTube videos generally have good structure
                needs_review=True,  # Always review AI-extracted recipes
                extraction_method='youtube_ai',
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"❌ YouTube import failed: {e}")
            return ImportResult(
                success=False,
                errors=[f'YouTube import error: {str(e)}']
            )
    
    def _parse_recipe_with_ai(self, text: str, source: str, url: str) -> Optional[Dict]:
        """
        Use OpenAI/Claude to parse recipe from text
        
        This is the magic that converts video content → recipe format
        """
        import openai
        
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        if not openai.api_key:
            logger.error("OpenAI API key not configured")
            return None
        
        prompt = f"""
You are a recipe extraction expert. Extract recipe information from this {source} content and format it as JSON.

Source URL: {url}

Content:
{text}

Extract and return in this EXACT JSON format:
{{
  "title": "Recipe name from video",
  "servings": "number or range (e.g., '4', '4-6')",
  "prep_time": "preparation time in minutes (number only)",
  "cook_time": "cooking time in minutes (number only)",
  "total_time": "total time in minutes (number only)",
  "difficulty": "easy, medium, or hard",
  "ingredients": [
    "ingredient with quantity (e.g., '2 cups flour')",
    "ingredient with quantity",
    ...
  ],
  "instructions": [
    "Step 1: detailed instruction",
    "Step 2: detailed instruction",
    ...
  ],
  "tips": [
    "Optional cooking tip",
    ...
  ],
  "description": "Brief 1-2 sentence description of the recipe",
  "tags": ["tag1", "tag2", "tag3"]
}}

IMPORTANT RULES:
1. Extract ALL ingredients mentioned with their quantities
2. Preserve exact measurements (cups, tablespoons, grams, etc.)
3. Keep instruction steps in order
4. If times aren't mentioned, estimate based on recipe complexity
5. Include any special techniques or equipment mentioned
6. If information is unclear or missing, use your best judgment
7. Return ONLY valid JSON, no markdown or explanations

Focus on accuracy and completeness. This recipe will be reviewed by a user before saving.
"""
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a recipe extraction expert. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3  # Lower temperature for more consistent results
            )
            
            recipe_json = response.choices[0].message.content
            recipe_data = json.loads(recipe_json)
            
            logger.info(f"✅ AI parsed recipe: {recipe_data.get('title', 'Unknown')}")
            return recipe_data
            
        except Exception as e:
            logger.error(f"AI parsing failed: {e}")
            return None
```

---

### **Phase 3: Mobile App Integration**

**No changes needed!** The existing mobile import flow will automatically work:

```javascript
// RecipeCollectionScreen.js - Already supports any URL
const importRecipeFromUrl = async () => {
  if (!importUrl.trim()) {
    Alert.alert('Error', 'Please enter a URL');
    return;
  }

  setIsImporting(true);
  try {
    // This already works for YouTube URLs!
    const result = await YesChefAPI.extractRecipeFromUrl(importUrl.trim());
    
    if (result.success) {
      setImportUrl('');
      navigation.navigate('RecipeImportReview', { 
        importResult: result 
      });
    }
  } catch (error) {
    Alert.alert('Import Failed', error.message);
  } finally {
    setIsImporting(false);
  }
};
```

**Optional Enhancement**: Add YouTube icon detection

```javascript
// Add visual feedback when YouTube URL is detected
const isYouTubeUrl = (url) => {
  return url.includes('youtube.com') || url.includes('youtu.be');
};

// In UI:
{importUrl && isYouTubeUrl(importUrl) && (
  <View style={styles.youtubeIndicator}>
    <Text style={styles.youtubeIcon}>🎥</Text>
    <Text style={styles.youtubeText}>YouTube video detected</Text>
  </View>
)}
```

---

## 🔧 Setup Requirements

### **1. Python Dependencies**

Add to `requirements.txt`:
```
google-api-python-client==2.108.0
youtube-transcript-api==0.6.1
isodate==0.6.1
openai==1.3.0
```

### **2. Environment Variables**

Add to `.env` and Railway:
```bash
# YouTube Data API v3 key (free, 10,000 requests/day)
YOUTUBE_API_KEY=your_youtube_api_key_here

# OpenAI for recipe parsing (already have this)
OPENAI_API_KEY=your_openai_key_here
```

### **3. Get YouTube API Key** (5 minutes)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "YesChef Recipe Import"
3. Enable YouTube Data API v3
4. Create credentials → API Key
5. Restrict key to YouTube Data API v3
6. Copy key to Railway environment variables

**Cost**: FREE (10,000 quota/day = ~10,000 videos/day)

---

## 📊 Expected Results

### **Success Metrics:**
- ✅ **Extraction Success Rate**: 85-95% for cooking videos with captions
- ✅ **Processing Time**: 5-15 seconds per video
- ✅ **Ingredient Accuracy**: 90%+ with captions
- ✅ **Instruction Quality**: High (AI understands cooking context)

### **Limitations:**
- ⚠️ Requires captions/transcripts (80% of cooking videos have them)
- ⚠️ AI parsing may need user review (intentional design)
- ⚠️ Short videos (<2 min) may lack recipe details

### **Example Flow:**
```
User Input: https://www.youtube.com/watch?v=abc123
              ↓
Backend: Detects YouTube URL
              ↓
YouTube API: Gets metadata + transcript
              ↓
OpenAI: Parses → {title, ingredients, instructions}
              ↓
Database: Saves temporary recipe
              ↓
Mobile: Shows RecipeImportReviewScreen
              ↓
User: Reviews/edits → Saves to collection
```

---

## 🚀 Implementation Timeline

### **Week 1: Backend Foundation**
- Day 1-2: Create YouTubeRecipeExtractor class
- Day 3: Integrate with UniversalRecipeImporter
- Day 4: Test with various YouTube cooking videos
- Day 5: Deploy to Railway with YouTube API key

### **Week 2: Testing & Polish**
- Day 1-2: Mobile testing with real YouTube URLs
- Day 3: Fix edge cases and improve AI prompts
- Day 4: Performance optimization
- Day 5: Documentation and user testing

---

## 🧪 Testing Plan

### **Test Cases:**
1. **Popular Cooking Channel** (Binging with Babish, Tasty)
   - Expected: High accuracy, detailed instructions
2. **Quick Recipe Video** (< 2 minutes)
   - Expected: Basic recipe, may need manual enhancement
3. **Long Tutorial** (>20 minutes)
   - Expected: Comprehensive recipe, possibly multiple recipes
4. **Non-English Video**
   - Expected: Graceful failure or translation
5. **No Captions Available**
   - Expected: Use description only, lower confidence

### **Test URLs for Development:**
```
- https://www.youtube.com/watch?v=3AAdKl1UYZs (Basics with Babish)
- https://youtu.be/GkAmq8xdDcA (Gordon Ramsay)
- https://www.youtube.com/watch?v=hpiIWMWWVco (J. Kenji López-Alt)
```

---

## 💡 Future Enhancements

### **Phase 2 Features:**
1. **Timestamp Integration**: Link instructions to video timestamps
2. **Multi-Recipe Detection**: Extract multiple recipes from one video
3. **Ingredient Images**: Screenshot ingredients from video frames
4. **Chef Profile**: Save channel info as recipe source
5. **Playlist Import**: Batch import from cooking playlists

### **Phase 3 Features:**
1. **Live Video Processing**: Watch video while cooking
2. **Voice Commands**: "Next step" integration with video
3. **Smart Recommendations**: "People who made this also watched..."

---

## ✅ Success Criteria

**MVP is complete when:**
1. ✅ User can paste YouTube URL in mobile app
2. ✅ Backend extracts video content and generates recipe
3. ✅ Recipe appears in RecipeImportReviewScreen for editing
4. ✅ User can save to their collection
5. ✅ Source attribution links back to original video

**Quality Metrics:**
- 80%+ of cooking videos successfully extract
- Processing time < 20 seconds
- User satisfaction > 4/5 stars
- Less than 20% require significant manual editing

---

## 🎯 Next Steps

**Ready to implement?** Here's what we'll do:

1. **Create YouTubeRecipeExtractor** module
2. **Modify UniversalRecipeImporter** to detect YouTube
3. **Add YouTube API key** to Railway
4. **Install dependencies** 
5. **Test with real videos**
6. **Deploy and validate**

**Estimated Time**: 2-3 days for full implementation
**Cost**: ~$0.01-0.03 per video (OpenAI API)
**Value**: Massive content unlock for users!

Let me know if you want me to start building this! 🚀