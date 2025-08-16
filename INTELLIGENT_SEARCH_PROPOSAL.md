# Intelligent Search Architecture Proposal

## Current Problem
- Hardcoded limits (20/50) don't scale
- No pagination or session awareness in backend
- Frontend session memory is disconnected from backend search
- Users will hit limits as database grows to thousands of recipes
- Search feels basic and limited

## Proposed Solution: Backend Session-Aware Search

### 1. Backend Session Memory Integration
Move session tracking from frontend to backend:

```python
# New endpoint: /api/search/session-aware
@app.route('/api/search/session-aware', methods=['POST'])
def session_aware_search():
    data = request.get_json()
    query = data.get('query')
    session_id = data.get('session_id')  # From frontend
    exclude_shown = data.get('shown_recipe_ids', [])  # Already shown recipes
    page_size = data.get('page_size', 5)  # How many to show
    
    # Get ALL matching recipes but exclude already shown
    all_matches = enhanced_search_with_exclusions(query, exclude_shown)
    
    # Return next batch + metadata
    return {
        'recipes': all_matches[:page_size],
        'total_available': len(all_matches),
        'has_more': len(all_matches) > page_size,
        'session_id': session_id
    }
```

### 2. Enhanced Search with Exclusions
Modify the search engine to handle exclusions efficiently:

```python
def enhanced_search_with_exclusions(query, exclude_ids=None, sort_by='relevance'):
    """
    Intelligent search that:
    1. Uses semantic search for better matching
    2. Excludes already shown recipes
    3. Sorts by relevance, not just ID
    4. Returns ALL matches (no artificial limits)
    """
    exclude_clause = ""
    params = []
    
    if exclude_ids:
        placeholders = ','.join(['%s'] * len(exclude_ids))
        exclude_clause = f"AND r.id NOT IN ({placeholders})"
        params.extend(exclude_ids)
    
    # Enhanced query with multiple search strategies
    query_sql = f"""
    SELECT DISTINCT r.* FROM recipes r
    LEFT JOIN ingredients i ON r.id = i.recipe_id
    WHERE (
        LOWER(r.title) LIKE %s OR
        LOWER(r.description) LIKE %s OR
        LOWER(i.name) LIKE %s OR
        -- Add semantic search here later
        r.id IN (SELECT recipe_id FROM recipe_tags rt 
                 JOIN tags t ON rt.tag_id = t.id 
                 WHERE LOWER(t.name) LIKE %s)
    )
    {exclude_clause}
    ORDER BY {get_relevance_order(sort_by)}
    """
    
    search_term = f"%{query.lower()}%"
    params = [search_term, search_term, search_term, search_term] + params
    
    return execute_query(query_sql, params)
```

### 3. Frontend Session Integration
Update frontend to work with backend session:

```javascript
class IntelligentSessionManager {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.shownRecipeIds = new Set();
    }
    
    async searchRecipes(query) {
        const response = await fetch('/api/search/session-aware', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query,
                session_id: this.sessionId,
                shown_recipe_ids: Array.from(this.shownRecipeIds),
                page_size: 5
            })
        });
        
        const data = await response.json();
        
        // Track shown recipes
        data.recipes.forEach(recipe => {
            this.shownRecipeIds.add(recipe.id);
        });
        
        return data;
    }
}
```

### 4. Advanced Features

#### A. Relevance Scoring
```python
def calculate_relevance_score(recipe, query, user_preferences=None):
    """
    Calculate relevance based on:
    - Title match strength
    - Ingredient match count
    - User preference alignment
    - Recipe popularity/rating
    - Seasonal relevance
    """
    score = 0
    query_lower = query.lower()
    
    # Title matches (highest weight)
    if query_lower in recipe['title'].lower():
        score += 100
    
    # Ingredient matches
    ingredient_matches = count_ingredient_matches(recipe, query)
    score += ingredient_matches * 20
    
    # User preference alignment
    if user_preferences:
        score += calculate_preference_alignment(recipe, user_preferences)
    
    return score
```

#### B. Intelligent Query Expansion
```python
def expand_search_query(query):
    """
    Expand user queries intelligently:
    - "chicken" → ["chicken", "poultry", "hen"]
    - "quick dinner" → ["quick", "easy", "30 minutes", "weeknight"]
    - "healthy" → ["low fat", "vegetarian", "fresh", "nutritious"]
    """
    expansions = {
        'chicken': ['chicken', 'poultry', 'hen', 'fowl'],
        'quick': ['quick', 'easy', 'fast', '30 minutes', 'weeknight'],
        'healthy': ['healthy', 'low fat', 'nutritious', 'fresh', 'light'],
        # ... more expansions
    }
    
    expanded_terms = [query]  # Always include original
    for term, alternatives in expansions.items():
        if term in query.lower():
            expanded_terms.extend(alternatives)
    
    return expanded_terms
```

#### C. Seasonal & Contextual Intelligence
```python
def add_contextual_intelligence(recipes, current_time=None):
    """
    Add contextual ranking based on:
    - Time of day (breakfast/lunch/dinner)
    - Season (summer salads, winter stews)
    - Day of week (quick weeknight vs weekend projects)
    """
    if not current_time:
        current_time = datetime.now()
    
    hour = current_time.hour
    month = current_time.month
    
    for recipe in recipes:
        # Time-based boosting
        if 6 <= hour <= 10 and 'breakfast' in recipe['title'].lower():
            recipe['relevance_score'] += 30
        elif 11 <= hour <= 14 and 'lunch' in recipe['title'].lower():
            recipe['relevance_score'] += 30
        elif hour >= 17 and 'dinner' in recipe['title'].lower():
            recipe['relevance_score'] += 30
        
        # Seasonal boosting
        if month in [6, 7, 8] and any(term in recipe['title'].lower() 
                                     for term in ['salad', 'cold', 'fresh', 'grilled']):
            recipe['relevance_score'] += 20
    
    return sorted(recipes, key=lambda r: r.get('relevance_score', 0), reverse=True)
```

## Implementation Plan

### Phase 1: Backend Session Awareness (1-2 days)
1. Create session-aware search endpoint
2. Modify enhanced search to handle exclusions
3. Add relevance scoring

### Phase 2: Frontend Integration (1 day)  
1. Update RecipeDetail.js to use new endpoint
2. Implement IntelligentSessionManager
3. Add "Show more recipes" functionality

### Phase 3: Advanced Intelligence (2-3 days)
1. Query expansion system
2. Contextual/seasonal intelligence
3. User preference learning

### Phase 4: Performance Optimization (1-2 days)
1. Database indexing for search performance
2. Caching frequently searched terms
3. Pagination optimization

## Benefits
- ✅ Scales to unlimited recipes
- ✅ Truly intelligent search experience
- ✅ No arbitrary limits
- ✅ Better user experience with contextual results
- ✅ Foundation for machine learning improvements
- ✅ Session persistence across page reloads

## Database Changes Needed
```sql
-- Add search performance indexes
CREATE INDEX idx_recipes_title_search ON recipes USING gin(to_tsvector('english', title));
CREATE INDEX idx_ingredients_name_search ON ingredients USING gin(to_tsvector('english', name));
CREATE INDEX idx_recipes_description_search ON recipes USING gin(to_tsvector('english', description));

-- Add relevance tracking table
CREATE TABLE search_analytics (
    id SERIAL PRIMARY KEY,
    query TEXT,
    recipe_id INTEGER REFERENCES recipes(id),
    clicked BOOLEAN DEFAULT FALSE,
    session_id VARCHAR(255),
    search_timestamp TIMESTAMP DEFAULT NOW()
);
```

This architecture transforms the search from "basic database query with limits" into "intelligent recipe discovery engine" that can grow with the user base and data.
