# 🎓 Me Hungie Learning Resources

**Purpose:** Help you understand the tech stack and make better development decisions

## 🏗️ **Architecture Overview**

### 🚀 **Backend (Python/Flask)**
- **`hungie_server.py`**: Main server handling all API requests
- **SQLite Database**: `hungie.db` stores 642+ recipes with enhanced data
- **OpenAI Integration**: Powers AI chat and recipe analysis
- **Search System**: `enhanced_search.py` for finding recipes
- **Flavor System**: `production_flavor_system.py` for ingredient pairing

### ⚛️ **Frontend (React)**
- **React Components**: UI elements in `frontend/src/`
- **API Calls**: Frontend talks to backend via HTTP requests
- **State Management**: React hooks for managing app state

### 🔗 **How They Connect**
```
User Interface (React) 
    ↓ HTTP Requests
Backend Server (Flask) 
    ↓ SQL Queries  
Database (SQLite)
    ↓ API Calls
OpenAI (AI Features)
```

## 🛠️ **Key Concepts to Learn**

### 📊 **Database Concepts:**
- **Tables**: Like spreadsheets (recipes, categories, ingredients)
- **Queries**: How we search/filter data ("find all chicken recipes")
- **Relationships**: How tables connect (recipe → ingredients)

### 🌐 **API Concepts:**
- **Endpoints**: URLs that do specific things (/api/search, /api/chat)
- **HTTP Methods**: GET (retrieve), POST (send data), PUT (update)
- **JSON**: Data format for sending info between frontend/backend

### 🎯 **When Planning New Features, Ask:**
1. **Where does the data come from?** (Database, user input, AI?)
2. **What does the user see?** (Frontend components needed)
3. **What processing happens?** (Backend logic required)
4. **How do they connect?** (API endpoints needed)

## 📚 **Feature Planning Template**

When you want to add something like **Pantry Management**:

### 🤔 **Questions to Explore:**
- What data do we need to store? (ingredients, quantities, expiration dates?)
- How does user interact with it? (add/remove items, view pantry?)
- How does it connect to recipes? (suggest recipes based on pantry?)
- What new API endpoints do we need?

### 📁 **File Organization Planning:**
- **Database changes**: Scripts in `scripts/database_management/`
- **API endpoints**: Add to `hungie_server.py` or new `pantry_api.py`
- **Frontend components**: New React components in `frontend/src/`
- **Tests**: Pantry-specific tests in `tests/pantry/`

## 💡 **Learning By Doing**

### 🔍 **When We Debug Together:**
- I'll explain what each error means
- Show you how to read logs and error messages  
- Walk through the code path from frontend to backend

### 🏗️ **When We Build Features:**
- Break down complex features into simple steps
- Show you the decision process for file organization
- Explain why we choose certain technical approaches

### 📖 **Questions You Can Always Ask:**
- "How does this work?"
- "Why did we put this file here?"
- "What happens when the user clicks this?"
- "How does the data flow through the system?"
- "What would break if we changed this?"

## 🎯 **Your Growing Understanding Will Help:**
- **Better feature requests**: You'll know what's possible/easy vs complex
- **Smarter organization**: You'll see why structure matters
- **Faster debugging**: You'll understand where problems likely occur
- **Better collaboration**: We'll speak the same technical language

**Remember:** Every expert was once a beginner. Ask questions, experiment, and learn! 🚀
