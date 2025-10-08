# 🔍 Current Infrastructure Review - Voice Recording Integration
**Date:** October 6, 2025  
**Purpose:** Understand existing architecture before implementing voice recipe recording  
**Status:** Complete system review

---

## 📊 **System Architecture Overview**

### **Three-Tier Application:**

```
┌─────────────────────────────────────────────────────────┐
│                  MOBILE APP (React Native)              │
│                  YesChefMobile/                         │
│  - Expo framework                                       │
│  - Navigation: Tab + Stack navigators                   │
│  - Offline-first with AsyncStorage                      │
│  - JWT authentication with SecureStore                  │
└─────────────────────────────────────────────────────────┘
                          ↕ HTTP/JSON
┌─────────────────────────────────────────────────────────┐
│              BACKEND API (Flask/Python)                 │
│              hungie_server.py (6112 lines)              │
│  - Flask web server                                     │
│  - PostgreSQL database (Railway)                        │
│  - OpenAI GPT-4 integration                            │
│  - JWT authentication                                   │
│  - CORS enabled for multiple origins                    │
└─────────────────────────────────────────────────────────┘
                          ↕ PostgreSQL
┌─────────────────────────────────────────────────────────┐
│           DATABASE (PostgreSQL on Railway)              │
│  - users table                                          │
│  - recipes table                                        │
│  - meal_plans, grocery_lists                           │
│  - community_cooking_tips (to be added)                │
└─────────────────────────────────────────────────────────┘
```

---

## 🗄️ **Database Schema (Current)**

### **Core Tables:**

**1. `users` table:**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**2. `recipes` table:**
```sql
CREATE TABLE recipes (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    ingredients TEXT,  -- Stored as TEXT (JSON string)
    instructions TEXT, -- Stored as TEXT (JSON string)
    category TEXT,
    servings TEXT,
    hands_on_time TEXT,
    total_time TEXT,
    url TEXT,
    source TEXT,
    image_url TEXT,
    flavor_profile TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Community Sharing
    is_community_shared BOOLEAN DEFAULT FALSE,
    shared_at TIMESTAMP NULL,
    community_title TEXT NULL,
    community_description TEXT NULL,
    community_background TEXT DEFAULT 'default',
    community_icon TEXT DEFAULT '🍽️',
    
    -- Additional fields...
    book_id INTEGER,
    page_number INTEGER,
    date_saved TEXT,
    why_this_works TEXT,
    chapter TEXT,
    chapter_number INTEGER
);
```

**IMPORTANT NOTES:**
- ✅ No explicit `user_id` foreign key in current schema
- ✅ Ingredients/instructions stored as TEXT (JSON strings)
- ✅ Community sharing features already in place
- ⚠️ Will need to add user_id column for voice recordings

---

## 🔐 **Authentication System**

### **Current Implementation:**

**Backend (Flask-JWT-Extended):**
```python
# auth_system.py
class AuthenticationSystem:
    - JWT token generation
    - Password hashing (bcrypt)
    - User registration
    - Login validation
    
# auth_routes.py
POST /api/auth/register
POST /api/auth/login
POST /api/auth/google
GET /api/auth/verify
```

**Mobile (Expo SecureStore):**
```javascript
// YesChefAPI.js
class YesChefAPI {
  - Token stored in SecureStore
  - Auto-included in headers via getAuthHeaders()
  - Google OAuth integration
  - Session persistence
}
```

**Authentication Flow:**
```
1. User logs in → JWT token generated
2. Token stored in SecureStore (mobile)
3. All API requests include: Authorization: Bearer {token}
4. Backend validates JWT on protected routes
5. check_authentication() extracts user_id from token
```

**Key Function (Backend):**
```python
def check_authentication():
    """
    Returns (user_id, error_response, status_code) tuple
    Extracts user_id from JWT token in Authorization header
    """
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]  # Extract "Bearer {token}"
    decoded = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
    user_id = decoded['sub']  # User ID from token
    return user_id, None, None
```

---

## 📡 **Existing API Endpoints**

### **Recipe Import System (Current):**

**POST `/api/recipes/import/url`**
```python
# Input:
{
    "url": "https://youtube.com/watch?v=..."
}

# Process:
1. check_authentication() → get user_id
2. UniversalRecipeImporter.import_recipe()
3. Returns recipe_data (NOT saved yet)

# Output:
{
    "success": true,
    "recipe_id": null,  # Not saved yet
    "recipe_data": {
        "title": "...",
        "ingredients": [...],
        "instructions": [...],
        "source": "YouTube",
        "extraction_method": "youtube_transcript"
    },
    "confidence": 0.85,
    "needs_review": false,
    "processing_time": 15.2
}
```

**Key Pattern:** Preview-first, save later!

**POST `/api/recipes`** (Save after review)
```python
# Input: Full recipe object
{
    "title": "...",
    "ingredients": [...],  # Already JSON array
    "instructions": [...],
    "category": "dinner",
    "source": "Voice Recording",
    ... all other fields
}

# Process:
1. check_authentication() → get user_id
2. Insert into recipes table
3. Return recipe with ID

# Output:
{
    "success": true,
    "recipe": { id: 123, ... },
    "recipe_id": 123
}
```

---

## 📱 **Mobile App Architecture**

### **Navigation Structure:**

```javascript
App.js
├── NavigationContainer
│   ├── Tab Navigator (Bottom tabs with horizontal scroll)
│   │   ├── HomeStack (Community + Latest Updates)
│   │   │   ├── HomeMain
│   │   │   ├── Profile
│   │   │   └── CommunityRecipeDetail
│   │   ├── RecipeStack (My Recipes)
│   │   │   ├── RecipeCollection
│   │   │   ├── RecipeDetail (RecipeViewScreen)
│   │   │   └── RecipeImportReview ← WE'LL REUSE THIS!
│   │   ├── MealPlanStack
│   │   │   ├── MealPlanMain
│   │   │   └── RecipeDetail
│   │   ├── GroceryList
│   │   └── Friends
│   └── LoginScreen (if not authenticated)
```

**Key Screens We'll Integrate With:**

1. **RecipeCollectionScreen** - Add "Record Recipe" button here
2. **RecipeImportReviewScreen** - REUSE for voice recordings! ✅
3. **RecipeViewScreen** - Display final saved recipe

---

## 🔌 **YesChefAPI Service (Mobile)**

### **Existing Pattern:**

```javascript
// YesChefMobile/src/services/YesChefAPI.js

class YesChefAPI {
  baseURL = 'https://yeschefapp-production.up.railway.app';
  
  // Authentication
  getAuthHeaders() {
    return {
      'Authorization': `Bearer ${this.token}`,
      'Content-Type': 'application/json'
    };
  }
  
  // Debug logging
  log(message, data) { ... }
  
  // Network helper
  async debugFetch(url, options) { ... }
  
  // Example: Recipe import (YouTube)
  async importRecipe(url) {
    const response = await this.debugFetch('/api/recipes/import/url', {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ url })
    });
    
    const data = await response.json();
    
    return {
      success: data.success,
      recipe: data.recipe_data,
      recipe_id: data.recipe_id,
      confidence: data.confidence
    };
  }
  
  // Save after review
  async saveReviewedImportedRecipe(recipeData) {
    const response = await this.debugFetch('/api/recipes', {
      method: 'POST',
      headers: this.getAuthHeaders(),
      body: JSON.stringify(recipeData)
    });
    
    return await response.json();
  }
}
```

**Key Patterns to Follow:**
1. ✅ All requests use `getAuthHeaders()`
2. ✅ Use `debugFetch()` for logging
3. ✅ Preview → Review → Save workflow
4. ✅ Return `{ success, recipe, recipe_id }` format

---

## 🎨 **Existing UI Components (Mobile)**

### **Components We Can Reuse:**

**1. RecipeImportReviewScreen:**
```javascript
// Shows recipe preview with editing capability
- Title input
- Ingredients list (editable)
- Instructions list (editable)
- Category selector
- Save button
- Cancel button

// PERFECT for voice recording preview! ✅
```

**2. IconLibrary:**
```javascript
// Available icons we can use:
- microphone (for recording button)
- play (for playback)
- trash (for delete segment)
- check (for approval)
- x-circle (for cancel)
```

**3. Typography:**
```javascript
// Consistent fonts throughout app:
- Nunito-Regular
- Nunito-Bold
- Nunito-ExtraBold
```

---

## 🔧 **Core Systems (Backend)**

### **Existing Infrastructure:**

**1. Universal Recipe Importer:**
```python
# core_systems/recipe_importer.py

class UniversalRecipeImporter:
    def import_recipe(self, import_request):
        # Handles: YouTube, Web URLs, Text
        # Returns: ImportResult with recipe_data
        
class ImportRequest:
    source_type: str  # 'url', 'text', 'youtube'
    source_data: str  # URL or text content
    user_id: int
    metadata: dict

class ImportResult:
    success: bool
    recipe_data: dict
    confidence: float
    extraction_method: str
    processing_time: float
```

**2. AI Recipe Parser:**
```python
# core_systems/ai_recipe_parser.py (assumed to exist)

class AIRecipeParser:
    def parse_with_prompt(self, prompt):
        # Uses GPT-4 to parse text → structured recipe
        # Returns: { title, ingredients[], instructions[], ... }
```

**3. YouTube Recipe Extractor:**
```python
# core_systems/youtube_recipe_extractor.py

class YouTubeRecipeExtractor:
    def extract(self, youtube_url):
        # Gets video metadata + transcript
        # Returns combined text for AI parsing
```

---

## 🚀 **Where Voice Recording Fits**

### **Integration Points:**

**1. Backend - New Endpoints:**
```python
POST /api/recipes/voice/session/process
- Input: Multiple audio segments + metadata
- Process: Transcribe → Combine → Auto-edit
- Output: Combined transcript for approval

POST /api/recipes/voice/generate
- Input: Approved transcript + metadata
- Process: GPT-4 recipe generation
- Output: Structured recipe_data (same as YouTube!)
```

**2. Backend - New Modules:**
```python
core_systems/
├── voice_session_processor.py (NEW)
│   ├── VoiceSessionProcessor
│   ├── transcribe_segments()
│   ├── combine_transcripts()
│   └── generate_recipe_from_transcript()
│
└── language_matcher.py (NEW)
    ├── Language database
    ├── Fuzzy search
    └── Whisper config generation
```

**3. Mobile - New Screens:**
```javascript
YesChefMobile/src/screens/
├── VoiceRecipeRecorder.js (NEW)
│   ├── Session management
│   ├── Multi-segment recording
│   └── Local storage (AsyncStorage)
│
├── TranscriptApprovalScreen.js (NEW)
│   ├── Show combined transcript
│   ├── Allow editing
│   └── Submit for recipe generation
│
└── RecipeImportReviewScreen.js (EXISTING - REUSE!)
    └── Already perfect for showing generated recipe!
```

**4. Mobile - API Service:**
```javascript
// YesChefMobile/src/services/YesChefAPI.js

// Add these methods:
async processVoiceSession(session) { ... }
async generateRecipeFromTranscript(transcript, metadata) { ... }
```

---

## 📦 **Dependencies (Current)**

### **Backend (Python):**
```txt
Flask==3.0.0
flask-cors==4.0.0
flask-jwt-extended==4.5.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
openai>=1.0.0
bcrypt==4.0.1

# For YouTube (already installed):
google-api-python-client==2.184.0
youtube-transcript-api==1.2.2
isodate==0.7.2

# NEED TO ADD for voice:
# (none! Will use OpenAI Whisper API - already have openai package)
```

### **Mobile (React Native/Expo):**
```json
{
  "expo": "~51.0.0",
  "expo-av": "~14.0.0",  // Audio recording - NEED TO ADD
  "expo-secure-store": "*",  // Already installed
  "@react-navigation/native": "*",  // Already installed
  "@react-navigation/bottom-tabs": "*",
  "@react-navigation/stack": "*",
  "react-native-gesture-handler": "*"
}
```

---

## ✅ **What Works Well (Keep These Patterns)**

### **1. Preview-First Workflow:**
```
Import → Preview → Edit → Save
(YouTube currently, voice will follow same pattern)
```

### **2. Authentication Flow:**
```
JWT token → Stored securely → Auto-included in requests
```

### **3. Error Handling:**
```javascript
try {
  const response = await api.method();
  if (response.success) {
    // Handle success
  } else {
    Alert.alert('Error', response.error);
  }
} catch (error) {
  Alert.alert('Network Error', 'Check connection');
}
```

### **4. Loading States:**
```javascript
const [isLoading, setIsLoading] = useState(false);

// Show spinner during processing
{isLoading && <ActivityIndicator />}
```

### **5. Data Flow:**
```
Mobile → API → Backend → Database → API → Mobile
All communication via JSON over HTTPS
```

---

## ⚠️ **Potential Issues to Address**

### **1. Database Schema - Missing user_id:**
```sql
-- recipes table currently has NO user_id column!
-- This could be why recipes are global

-- NEED TO ADD:
ALTER TABLE recipes ADD COLUMN user_id INTEGER REFERENCES users(id);
```

### **2. Recipe Ownership:**
```python
# Current: Anyone can see all recipes?
# Need to filter by user_id in queries:
SELECT * FROM recipes WHERE user_id = %s
```

### **3. File Upload Support:**
```python
# Current: Only JSON payloads
# Voice needs: multipart/form-data for audio files

# Backend already handles this for images:
request.files.get('image')

# Just need to add for audio:
request.files.get('audio') or request.files.getlist('segments')
```

---

## 🎯 **Integration Strategy**

### **Phase 1: Backend Foundation (This Week)**

**Step 1: Add Database Columns**
```sql
ALTER TABLE recipes ADD COLUMN IF NOT EXISTS user_id INTEGER;
ALTER TABLE recipes ADD COLUMN IF NOT EXISTS audio_url TEXT;
ALTER TABLE recipes ADD COLUMN IF NOT EXISTS recorded_by VARCHAR(255);
ALTER TABLE recipes ADD COLUMN IF NOT EXISTS transcript TEXT;
```

**Step 2: Create Voice Processor Module**
```python
core_systems/voice_session_processor.py
- VoiceSessionProcessor class
- Whisper API integration
- GPT-4 recipe generation
```

**Step 3: Add API Endpoints**
```python
@app.route('/api/recipes/voice/session/process', methods=['POST'])
@app.route('/api/recipes/voice/generate', methods=['POST'])
```

**Step 4: Test with Postman/curl**
```bash
# Upload audio → Get transcript
# Approve transcript → Get recipe
```

### **Phase 2: Mobile Integration (Week 2)**

**Step 1: Add Recording UI**
```javascript
VoiceRecipeRecorder.js
- expo-av for audio
- AsyncStorage for session
```

**Step 2: Add API Methods**
```javascript
YesChefAPI.processVoiceSession()
YesChefAPI.generateRecipeFromTranscript()
```

**Step 3: Wire Navigation**
```javascript
RecipeStack.Navigator:
  - RecipeCollection (add "Record" button)
  - VoiceRecipeRecorder (new)
  - TranscriptApproval (new)
  - RecipeImportReview (existing! reuse!)
```

**Step 4: Test End-to-End**
```
Record → Transcribe → Approve → Generate → Review → Save
```

---

## 📝 **Key Takeaways**

### **What's Already Perfect:**
✅ Authentication system (JWT) - just use it  
✅ RecipeImportReviewScreen - reuse for voice!  
✅ Database connection (Railway PostgreSQL)  
✅ OpenAI integration (GPT-4 already configured)  
✅ API service patterns (YesChefAPI.js)  
✅ Preview-first workflow (YouTube model)  

### **What We Need to Add:**
🆕 Voice recording UI (expo-av)  
🆕 Audio upload endpoints (multipart/form-data)  
🆕 Whisper API integration (OpenAI)  
🆕 Voice session processor (backend module)  
🆕 Transcript approval screen (mobile)  
🆕 Language selection component (mobile)  
🆕 Community tips database (optional, Phase 2)  

### **What Needs Fixing:**
⚠️ Add user_id to recipes table  
⚠️ Filter recipes by user ownership  
⚠️ Ensure JSON serialization for ingredients/instructions  

---

## 🚀 **Ready to Start Implementation**

**Next Steps:**
1. ✅ Review complete
2. ⏭️ Start with backend infrastructure
3. ⏭️ Add database columns
4. ⏭️ Create voice_session_processor.py
5. ⏭️ Add API endpoints
6. ⏭️ Test with audio files
7. ⏭️ Build mobile UI
8. ⏭️ Connect everything
9. ⏭️ Test end-to-end
10. ⏭️ Deploy to Railway

**Timeline:** 2-3 weeks for complete MVP

---

**System review complete! Ready to proceed with backend implementation? 🎤**
