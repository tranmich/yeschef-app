/**
 * 🎥 VIDEO RECIPE IMPORTER - Implementation Plan
 * Extracts recipes from YouTube, Instagram, TikTok videos
 */

// ============================================================================
// PHASE 1: YouTube Recipe Import (RECOMMENDED START)
// ============================================================================

/**
 * 1. USER FLOW IN MOBILE APP
 * 
 * HomeScreen → "+" Button → "Import from Video"
 *   ↓
 * Paste URL → Detect Platform
 *   ↓
 * Show Loading: "Analyzing video..."
 *   ↓
 * Extract & Parse with AI
 *   ↓
 * Recipe Review Screen (editable)
 *   ↓
 * Save to Collection
 */

// ============================================================================
// TECHNICAL IMPLEMENTATION
// ============================================================================

/**
 * Backend Endpoint: /api/import/video
 * 
 * POST /api/import/video
 * Body: { url: "https://youtube.com/watch?v=..." }
 * 
 * Response: {
 *   success: true,
 *   recipe: {
 *     title: "Amazing Pasta Recipe",
 *     servings: 4,
 *     cookTime: 30,
 *     difficulty: "easy",
 *     ingredients: [...],
 *     instructions: [...],
 *     sourceType: "youtube",
 *     sourceUrl: "...",
 *     thumbnailUrl: "..."
 *   }
 * }
 */

// ============================================================================
// PLATFORM DETECTION
// ============================================================================

const PLATFORM_PATTERNS = {
  youtube: [
    /youtube\.com\/watch\?v=/,
    /youtu\.be\//,
    /youtube\.com\/shorts\//
  ],
  instagram: [
    /instagram\.com\/p\//,
    /instagram\.com\/reel\//,
    /instagr\.am\/p\//
  ],
  tiktok: [
    /tiktok\.com\/@.*\/video\//,
    /vm\.tiktok\.com\//
  ]
};

function detectPlatform(url) {
  for (const [platform, patterns] of Object.entries(PLATFORM_PATTERNS)) {
    if (patterns.some(pattern => pattern.test(url))) {
      return platform;
    }
  }
  return null;
}

// ============================================================================
// YOUTUBE EXTRACTOR (Phase 1)
// ============================================================================

/**
 * YouTube Data API v3
 * - Free tier: 10,000 quota units/day
 * - Each video query: ~3 quota units
 * - Can handle ~3,000 imports/day for free
 */

async function extractYouTubeRecipe(videoUrl) {
  // 1. Extract video ID
  const videoId = extractYouTubeVideoId(videoUrl);
  
  // 2. Get video metadata (title, description, thumbnail)
  const videoData = await getYouTubeVideoData(videoId);
  
  // 3. Get captions/transcript (most important!)
  const transcript = await getYouTubeCaptions(videoId);
  
  // 4. Combine all text content
  const contentText = `
Video Title: ${videoData.title}
Description: ${videoData.description}
Transcript/Captions: ${transcript}
  `.trim();
  
  // 5. Send to AI for recipe extraction
  const recipe = await parseRecipeWithAI(contentText, 'YouTube');
  
  // 6. Add video thumbnail
  recipe.thumbnailUrl = videoData.thumbnail;
  recipe.sourceUrl = videoUrl;
  
  return recipe;
}

// ============================================================================
// AI RECIPE PARSER (Core Logic)
// ============================================================================

/**
 * Uses OpenAI GPT-4 or Claude to convert unstructured text into recipe format
 * Cost: ~$0.01-0.03 per recipe
 */

async function parseRecipeWithAI(contentText, platform) {
  const systemPrompt = `You are an expert recipe extraction AI. Extract recipe information from video content (captions, descriptions, transcripts) and format it precisely for a recipe app.

IMPORTANT RULES:
1. Extract ONLY recipe-related information
2. If measurements are vague, keep them vague (e.g., "a handful of")
3. Preserve the creator's voice in instructions
4. If critical info is missing, mark as null (don't guess)
5. Separate ingredients from instructions clearly`;

  const userPrompt = `Extract a recipe from this ${platform} video content:

${contentText}

Return a JSON object with this EXACT structure:
{
  "title": "Recipe name from video",
  "description": "Brief description if mentioned",
  "servings": "number or null",
  "cookTime": "total minutes as number or null",
  "prepTime": "prep minutes as number or null", 
  "difficulty": "easy|medium|hard or null",
  "ingredients": [
    "1 cup flour",
    "2 eggs",
    "..."
  ],
  "instructions": [
    "Step 1: Detailed instruction",
    "Step 2: Next step",
    "..."
  ],
  "tips": ["optional cooking tips mentioned"],
  "tags": ["relevant tags like 'quick', 'vegetarian', etc"],
  "equipment": ["tools needed if mentioned"]
}`;

  const response = await openai.chat.completions.create({
    model: "gpt-4-turbo-preview",
    messages: [
      { role: "system", content: systemPrompt },
      { role: "user", content: userPrompt }
    ],
    response_format: { type: "json_object" },
    temperature: 0.3 // Lower temp for more consistent extraction
  });

  return JSON.parse(response.choices[0].message.content);
}

// ============================================================================
// INSTAGRAM EXTRACTOR (Phase 2)
// ============================================================================

/**
 * Option A: Instagram Basic Display API (requires app review)
 * Option B: Web scraping (simpler but against ToS)
 * 
 * Recommendation: Start with Option B for MVP, get official API later
 */

async function extractInstagramRecipe(postUrl) {
  // Backend endpoint to avoid CORS
  // Scrapes caption from Instagram's public HTML
  const response = await fetch(`${API_URL}/scrape/instagram`, {
    method: 'POST',
    body: JSON.stringify({ url: postUrl })
  });
  
  const { caption, username } = await response.json();
  
  // Parse caption for recipe info
  const recipe = await parseRecipeWithAI(caption, 'Instagram');
  recipe.sourceUrl = postUrl;
  recipe.author = username;
  
  return recipe;
}

// ============================================================================
// TIKTOK EXTRACTOR (Phase 3)
// ============================================================================

async function extractTikTokRecipe(videoUrl) {
  // Similar to Instagram - backend scraping or API
  const response = await fetch(`${API_URL}/scrape/tiktok`, {
    method: 'POST',
    body: JSON.stringify({ url: videoUrl })
  });
  
  const { caption, username } = await response.json();
  
  const recipe = await parseRecipeWithAI(caption, 'TikTok');
  recipe.sourceUrl = videoUrl;
  recipe.author = username;
  
  return recipe;
}

// ============================================================================
// ADVANCED: SPEECH-TO-TEXT (Phase 4)
// ============================================================================

/**
 * For videos without captions, download audio and transcribe
 * Uses OpenAI Whisper API
 * Cost: ~$0.006/minute of audio
 */

async function extractRecipeWithSpeechToText(videoUrl) {
  // 1. Download video audio (backend)
  const audioFile = await downloadVideoAudio(videoUrl);
  
  // 2. Transcribe with Whisper
  const transcript = await openai.audio.transcriptions.create({
    file: audioFile,
    model: "whisper-1",
    language: "en"
  });
  
  // 3. Parse transcript with AI
  return await parseRecipeWithAI(transcript.text, 'Video');
}

// ============================================================================
// SUCCESS RATE ESTIMATES
// ============================================================================

/**
 * Expected Success Rates:
 * 
 * YouTube:
 * - With captions/transcript: 90-95% ✅
 * - Description only: 60-70% 🟡
 * - Speech-to-text: 85-90% ✅
 * 
 * Instagram:
 * - Good caption: 70-80% 🟡
 * - Minimal caption: 30-40% ❌
 * - Reels with voiceover: 50-60% 🟡
 * 
 * TikTok:
 * - Text overlay + caption: 75-85% ✅
 * - Caption only: 50-60% 🟡
 * - No text: 20-30% ❌
 * 
 * Overall: YouTube is the best starting point!
 */

// ============================================================================
// MOBILE APP INTEGRATION
// ============================================================================

/**
 * New Screen: VideoRecipeImportScreen.js
 * 
 * Features:
 * 1. URL input with paste button
 * 2. Platform detection badge
 * 3. Loading animation during extraction
 * 4. Recipe review/edit screen
 * 5. Save to collection
 * 
 * User can:
 * - Edit any field before saving
 * - Add missing information
 * - Change serving sizes
 * - Add photos
 */

// ============================================================================
// BACKEND REQUIREMENTS
// ============================================================================

/**
 * New Dependencies:
 * - openai (for GPT-4 and Whisper)
 * - google-auth-library (for YouTube API)
 * - yt-dlp or youtube-dl (for downloading if needed)
 * 
 * New Environment Variables:
 * - OPENAI_API_KEY
 * - YOUTUBE_API_KEY
 * - (optional) INSTAGRAM_ACCESS_TOKEN
 * - (optional) TIKTOK_API_KEY
 * 
 * New Endpoints:
 * - POST /api/import/video
 * - POST /api/scrape/instagram (internal)
 * - POST /api/scrape/tiktok (internal)
 */

// ============================================================================
// COST ESTIMATION
// ============================================================================

/**
 * Per 1,000 recipe imports:
 * 
 * YouTube:
 * - API calls: Free (within quota)
 * - AI parsing: $10-30 (GPT-4)
 * - Total: $10-30
 * 
 * With Speech-to-Text:
 * - Audio transcription: $6-12 (Whisper)
 * - AI parsing: $10-30 (GPT-4)
 * - Total: $16-42
 * 
 * Very affordable! Even with 10,000 imports/month:
 * - YouTube only: $100-300/month
 * - With speech-to-text: $160-420/month
 */

export {
  detectPlatform,
  extractYouTubeRecipe,
  extractInstagramRecipe,
  extractTikTokRecipe,
  parseRecipeWithAI
};