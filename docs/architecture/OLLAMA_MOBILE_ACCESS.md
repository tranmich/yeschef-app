# 🏗️ Ollama Architecture - How Mobile App Accesses LLM
**Date:** October 9, 2025  
**Question:** How does mobile app access Ollama?  
**Answer:** Same way as spaCy - through your backend server!

---

## **📱 THE SHORT ANSWER:**

**Mobile app DOES NOT call Ollama directly!**

```
Mobile App → Backend Server → Ollama (local on server)
```

**Just like spaCy:**
```
Mobile App → Backend Server → spaCy (local on server)
```

**Mobile app only knows ONE endpoint:**
```javascript
YesChefAPI.generateGroceryListFromMealPlan(planId)
```

---

## **🔄 COMPLETE FLOW:**

### **Step 1: User Action**
```
User taps "Generate Grocery List" in mobile app
```

### **Step 2: Mobile App Makes API Call**
```javascript
// MealPlanScreen.js
const response = await YesChefAPI.generateGroceryListFromMealPlan(planId);

// This calls:
// http://192.168.1.72:5000/api/meal-plans/123/generate-grocery-list
```

### **Step 3: Backend Receives Request**
```python
# hungie_server.py (running on your server)
@app.route('/api/meal-plans/<plan_id>/generate-grocery-list', methods=['POST'])
def generate_grocery_list(plan_id):
    # Backend handles EVERYTHING here
```

### **Step 4: Backend Processes (ALL ON SERVER)**
```python
# 1. Get recipes from database
recipes = get_recipes_from_meal_plan(plan_id)

# 2. Extract ingredients
ingredients = extract_all_ingredients(recipes)  # 36 items

# 3. 🧠 Call spaCy (local - same server)
spacy_metadata = spacy_normalizer.extract_metadata(ingredients)
# Takes 1-2 seconds

# 4. 🤖 Call Ollama (local - same server)
ambiguous_cases = find_ambiguous_items(ingredients)
llm_decisions = ollama_advisor.analyze(ambiguous_cases)
# Takes 2-3 seconds, only for ambiguous cases

# 5. Combine everything
combined_items = combine_with_guidance(ingredients, spacy_metadata, llm_decisions)
# Now: 28 items (reduced from 36)

# 6. Save to database
grocery_list = save_grocery_list(combined_items)
```

### **Step 5: Backend Returns Result**
```python
return jsonify({
    'success': True,
    'grocery_list': {
        'items': combined_items,  # 28 items, already combined!
        'list_name': 'Grocery List - Oct 9'
    }
})
```

### **Step 6: Mobile Displays**
```javascript
// Mobile receives the FINAL result
// Doesn't know about spaCy or Ollama!
setGroceryItems(response.grocery_list.items);
```

---

## **🖥️ SERVER ARCHITECTURE:**

### **Your Backend Server:**

```
┌─────────────────────────────────────────────────────┐
│  Your Server (Railway / VPS / Local)               │
│                                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │  Flask App (Python)                          │ │
│  │  Port: 5000                                  │ │
│  │                                              │ │
│  │  Routes:                                     │ │
│  │  - /api/meal-plans/generate-grocery-list    │ │
│  │  - /api/grocery/extract-metadata (spaCy)    │ │
│  │  - /api/recipes/*                            │ │
│  │                                              │ │
│  │  Integrations:                               │ │
│  │  - spaCy (localhost)                         │ │
│  │  - Ollama (localhost:11434)                  │ │
│  │  - PostgreSQL (localhost:5432)               │ │
│  └──────────────────────────────────────────────┘ │
│                       ↓ calls                      │
│  ┌──────────────────────────────────────────────┐ │
│  │  Ollama Service                              │ │
│  │  Port: 11434                                 │ │
│  │                                              │ │
│  │  Models:                                     │ │
│  │  - llama3.2:3b (~2GB)                        │ │
│  │                                              │ │
│  │  API: http://localhost:11434/api/chat       │ │
│  └──────────────────────────────────────────────┘ │
│                                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │  PostgreSQL Database                         │ │
│  │  Port: 5432                                  │ │
│  └──────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
            ↑
            │ HTTP (Internet)
            │
┌───────────┴──────────┐
│   Mobile App         │
│   (User's Phone)     │
└──────────────────────┘
```

---

## **🔧 HOW BACKEND CALLS OLLAMA:**

### **Python Code (Backend):**

```python
import requests

class OllamaGroceryAdvisor:
    def __init__(self):
        self.base_url = "http://localhost:11434"  # Ollama running locally
    
    def analyze_combining(self, items):
        """
        Call Ollama to analyze if items should combine
        """
        prompt = f"""
        Should these grocery items be combined?
        
        Items:
        1. Chicken Thighs (meat)
        2. Chicken Broth (liquid)
        
        Answer: yes or no, and explain why.
        """
        
        # Call Ollama API (local on same server)
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": "llama3.2:3b",
                "messages": [{"role": "user", "content": prompt}],
                "stream": False
            }
        )
        
        # Get LLM response
        result = response.json()
        return result['message']['content']
```

**Key Point:** Backend calls Ollama at `localhost:11434` - no internet needed!

---

## **📊 TIMING BREAKDOWN:**

### **User Experience:**

```
User taps button
   ↓
"Generating grocery list..." (spinner shows)
   ↓ 3-5 seconds total
"List ready!" (28 items displayed)
```

### **What Happens on Server (User Doesn't See):**

```
1. Database query: 100ms
2. Extract ingredients: 50ms
3. spaCy analysis: 1500ms (1.5s)
4. Ollama LLM (only for ambiguous): 2000ms (2s)
5. Combine logic: 100ms
6. Save to database: 50ms
──────────────────────────────
Total: ~3.8 seconds
```

**Mobile app just waits for the final result!**

---

## **💰 DEPLOYMENT OPTIONS:**

### **Option 1: Railway (Current)**

**Pros:**
- ✅ Easy deployment
- ✅ Auto-scaling
- ✅ Free tier available

**Cons:**
- ⚠️ May need to upgrade for Ollama RAM (3-4GB needed)
- ⚠️ CPU limits might slow LLM

**Cost:** ~$10-20/month for adequate resources

---

### **Option 2: VPS (DigitalOcean, Linode, etc.)**

**Pros:**
- ✅ Full control
- ✅ Better performance
- ✅ Can add GPU later

**Cons:**
- ⚠️ More setup required
- ⚠️ Manual scaling

**Cost:** ~$12-24/month (4GB RAM droplet)

---

### **Option 3: Local Development (Current)**

**Pros:**
- ✅ Free!
- ✅ Full control
- ✅ Fast for testing

**Cons:**
- ❌ Only accessible on local network
- ❌ Not production-ready

**Cost:** Free

---

## **🎯 RECOMMENDED SETUP:**

### **Development (Now):**
```
Local Server (Your PC)
- Flask app
- Ollama + Llama 3.2 (3B)
- spaCy
- PostgreSQL

Mobile app connects to: http://192.168.1.72:5000
```

### **Production (Later):**
```
Cloud Server (Railway/VPS)
- Flask app
- Ollama + Llama 3.2 (3B)
- spaCy
- PostgreSQL

Mobile app connects to: https://yeschefapp.com
```

---

## **🔒 SECURITY:**

### **Mobile App:**
- ✅ Uses HTTPS in production
- ✅ Sends auth token
- ✅ Only knows about backend API

### **Backend:**
- ✅ Ollama runs locally (not exposed to internet)
- ✅ Only Flask app is public
- ✅ Flask handles auth, rate limiting

### **Ollama:**
- ✅ Only accessible from Flask app
- ✅ Not exposed to internet
- ✅ No API key needed (local)

---

## **📝 CONFIGURATION FILES:**

### **Backend knows where Ollama is:**

```python
# hungie_server.py or config.py
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
```

### **Mobile app only knows backend:**

```javascript
// YesChefAPI.js
this.baseURL = 'http://192.168.1.72:5000'; // Development
// or
this.baseURL = 'https://yeschefapp.com'; // Production
```

---

## **✅ KEY TAKEAWAYS:**

1. **Mobile app NEVER talks to Ollama directly**
   - Only talks to your backend

2. **Backend handles ALL intelligence**
   - spaCy analysis
   - LLM reasoning
   - Combining logic

3. **Ollama runs ON THE SERVER**
   - Not a separate cloud service
   - Local calls only (fast!)
   - No API keys needed

4. **Same pattern as spaCy**
   - You're already doing this!
   - Just add Ollama alongside spaCy

5. **User sees ONE loading state**
   - "Generating grocery list..."
   - 3-5 seconds
   - Gets perfect results

---

## **🚀 NEXT STEPS:**

1. **Install Ollama on your local server** ✅ (You're doing this now!)
2. **Test with local model** (Run test script)
3. **Integrate into Flask app** (Add new endpoint)
4. **Test with mobile app** (Same API, better results!)
5. **Deploy to production** (When ready)

---

**Bottom line:** It's just like spaCy - mobile app doesn't know or care! 🎯
