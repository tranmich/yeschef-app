# 🍳 Me Hungie - Advanced Recipe Intelligence Platform

## 🎯 Project Overview
A sophisticated recipe platform featuring AI-powered search, advanced flavor profiling, and intelligent ingredient suggestions based on comprehensive culinary knowledge.

## 🔥 Key Features
- **Advanced FlavorProfile System**: 63 ingredients with 1,222+ expert pairings
- **Professional Culinary Intelligence**: Expert-level ingredient compatibility analysis
- **Enhanced Recipe Search**: AI-powered recipe discovery with context awareness
- **Chrome Extension**: Automated recipe collection from major cooking websites
- **React Frontend**: Modern, responsive user interface
- **Production Ready**: Deployed on Railway with comprehensive API

## 📁 Production Architecture

### Core Backend (`app.py`)
- Flask application with comprehensive API endpoints
- Advanced FlavorProfile System integration
- Enhanced search capabilities
- Recipe management and analysis

### FlavorProfile System (`production_flavor_system.py`)
- **63 ingredients** with **1,222+ expert pairings**
- Professional compatibility scoring (Essential 0.95+, Expert 0.90+, Professional 0.85+, Good 0.80+)
- Contextual analysis (cooking methods, seasonal appropriateness)
- Recipe harmony analysis with detailed pairing breakdowns

### Enhanced Search (`enhanced_search.py`)
- AI-powered semantic search
- Context-aware recipe discovery
- Advanced filtering and categorization

### Frontend (`frontend/`)
- React application with modern UI
- API integration for all backend services
- Responsive design for all devices

### Chrome Extension (`chrome-extension/`)
- Automated recipe scraping from 100+ websites
- Systematic category processing
- Direct database integration

### Culinary Database (`flavor_bible_data/`)
- Comprehensive culinary pairing data
- Expert-validated ingredient combinations
- Formatting-based strength classification

## 🚀 API Endpoints

### Recipe Management
- `GET /api/recipes/{id}` - Get specific recipe
- `GET /api/search?q={query}` - Search recipes
- `GET /api/categories` - Get recipe categories

### AI Intelligence
- `POST /api/smart-search` - AI-powered recipe search
- `POST /api/substitutions` - Ingredient substitutions
- `POST /api/substitutions/bulk` - Bulk substitutions

### Advanced FlavorProfile System
- `POST /api/flavor-profile/suggestions` - Get expert ingredient suggestions
- `POST /api/flavor-profile/compatibility` - Check ingredient compatibility
- `POST /api/flavor-profile/recipe-harmony` - Analyze recipe harmony
- `POST /api/flavor-profile/enhance-recipe` - Complete recipe enhancement

## 🎯 FlavorProfile System Capabilities

### Professional Analysis
- **Compatibility Scoring**: Precise numerical compatibility between ingredients
- **Strength Levels**: Essential, Expert, Professional, Good classification
- **Contextual Modifiers**: Cooking method and seasonal appropriateness
- **Coverage Analysis**: Database coverage reporting for ingredients

### Recipe Intelligence
- **Harmony Analysis**: Overall recipe compatibility scoring
- **Pairing Breakdown**: Detailed analysis of each ingredient combination
- **Enhancement Suggestions**: Professional-grade ingredient recommendations
- **Cooking Method Detection**: Automatic technique identification

### Expert Knowledge Integration
- **1,222+ Pairings**: Comprehensive professional culinary combinations
- **63 Core Ingredients**: Essential cooking components with full profiles
- **Formatting-Based Weights**: Bold+Caps (0.95), Bold (0.90), Caps (0.85), Plain (0.80)
- **Clean Data Processing**: Validated and filtered culinary intelligence

## 🔧 Development Setup

### Backend
```bash
cd "Me Hungie"
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python app.py
```

### Frontend
```bash
cd frontend
npm install
npm start
```

## 🚀 Deployment
- **Platform**: Railway
- **Backend**: Python Flask with Gunicorn
- **Frontend**: React build served statically
- **Database**: SQLite with recipe and culinary data
- **Configuration**: Environment-based with production overrides

## 📊 Performance Metrics
- **Database Coverage**: 60-75% for typical recipes
- **Response Times**: Sub-second API responses
- **Accuracy**: Expert-validated culinary pairings
- **Scalability**: Production-ready Flask architecture

## 🎯 Future Enhancements
- Machine learning-based preference adaptation
- Nutritional analysis integration
- Meal planning capabilities
- Social features and recipe sharing
- Advanced dietary restriction handling

---
*Built with comprehensive culinary intelligence and professional-grade flavor analysis*
