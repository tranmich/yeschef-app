#!/usr/bin/env python3
"""
Enhanced Recipe Search Intelligence System
Implements intelligent ingredient-based search with recipe type classification
and conversation flow management
"""

import sqlite3
import json
import re
from collections import defaultdict, Counter
from datetime import datetime

class EnhancedRecipeSearchEngine:
    def __init__(self, db_path='hungie.db'):
        self.db_path = db_path
        self.ingredient_network = {}
        self.recipe_types = {}
        self.user_searches = defaultdict(list)
        
        # Recipe type classification keywords
        self.recipe_type_keywords = {
            'one_pot': ['one pot', 'one-pot', 'single pot', 'skillet', 'casserole', 'slow cooker'],
            'quick': ['quick', 'fast', '15 minute', '20 minute', '30 minute', 'rapid'],
            'easy': ['easy', 'simple', 'basic', 'beginner', 'no-fuss'],
            'challenging': ['advanced', 'complex', 'difficult', 'technique', 'chef'],
            'low_prep': ['no prep', 'minimal prep', 'dump and go', 'throw together'],
            'slow_cook': ['slow cook', 'slow cooker', 'crock pot', 'braised', 'stewed', 'hours']
        }
        
        # Enhanced ingredient keywords with synonyms
        self.enhanced_ingredient_keywords = {
            'sweet_potato': ['sweet potato', 'sweet potatoes', 'yam', 'yams'],
            'chicken': ['chicken', 'poultry', 'fowl', 'hen'],
            'beef': ['beef', 'steak', 'ground beef', 'roast', 'brisket', 'chuck'],
            'pork': ['pork', 'bacon', 'ham', 'sausage', 'ribs', 'tenderloin'],
            'fish': ['fish', 'salmon', 'tuna', 'cod', 'seafood', 'halibut'],
            'potato': ['potato', 'potatoes', 'russet', 'yukon'],
            'rice': ['rice', 'jasmine rice', 'basmati', 'brown rice'],
            'pasta': ['pasta', 'spaghetti', 'noodles', 'macaroni', 'linguine'],
            'tomato': ['tomato', 'tomatoes', 'tomato sauce', 'diced tomatoes'],
            'cheese': ['cheese', 'cheddar', 'mozzarella', 'parmesan', 'swiss'],
            'onion': ['onion', 'onions', 'yellow onion', 'white onion', 'red onion'],
            'garlic': ['garlic', 'garlic clove', 'garlic powder', 'minced garlic']
        }
        
        # Cuisine flow patterns for conversation
        self.cuisine_flow = {
            'chicken': {
                'asian': ['soy sauce', 'ginger', 'sesame', 'stir fry'],
                'italian': ['parmesan', 'herbs', 'tomato', 'basil'],
                'mexican': ['cumin', 'chili', 'lime', 'cilantro'],
                'american': ['bbq', 'herbs', 'comfort', 'classic']
            }
        }
    
    def classify_recipe_types(self, recipe_title, recipe_instructions):
        """Classify recipe into types based on title and instructions"""
        text_to_analyze = f"{recipe_title} {recipe_instructions}".lower()
        types = []
        
        for recipe_type, keywords in self.recipe_type_keywords.items():
            if any(keyword in text_to_analyze for keyword in keywords):
                types.append(recipe_type)
        
        # Time-based classification from instructions
        if re.search(r'\b(15|20|30)\s*minute', text_to_analyze):
            types.append('quick')
        if re.search(r'\b(2|3|4)\s*hour', text_to_analyze):
            types.append('slow_cook')
            
        return types
    
    def extract_main_ingredient(self, query):
        """Extract main ingredient from user query"""
        query_lower = query.lower()
        
        for ingredient, synonyms in self.enhanced_ingredient_keywords.items():
            if any(synonym in query_lower for synonym in synonyms):
                return ingredient
        
        # If no predefined ingredient found, extract potential ingredient
        # Look for food-related words
        food_words = re.findall(r'\b[a-z]+\b', query_lower)
        food_words = [word for word in food_words if len(word) > 3]
        
        if food_words:
            return food_words[0]  # Return first potential ingredient
        
        return None
    
    def intelligent_search(self, query, user_id="default", limit=20, exclude_ids=None):
        """Enhanced search with ingredient intelligence and conversation flow"""
        
        # Log user search
        self.user_searches[user_id].append({
            'query': query,
            'timestamp': datetime.now().isoformat()
        })
        
        # Extract main ingredient
        main_ingredient = self.extract_main_ingredient(query)
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build search query with intelligent ingredient matching
        search_conditions = []
        search_params = []
        
        if main_ingredient:
            # Get all synonyms for the ingredient
            synonyms = self.enhanced_ingredient_keywords.get(main_ingredient, [main_ingredient])
            
            # Create search conditions for each synonym
            synonym_conditions = []
            for synonym in synonyms:
                synonym_conditions.append("(r.title LIKE ? OR r.ingredients LIKE ?)")
                search_params.extend([f"%{synonym}%", f"%{synonym}%"])
            
            search_conditions.append(f"({' OR '.join(synonym_conditions)})")
        else:
            # Fallback to general search
            search_conditions.append("(r.title LIKE ? OR r.ingredients LIKE ?)")
            search_params.extend([f"%{query}%", f"%{query}%"])
        
        # Exclude already shown recipes
        if exclude_ids:
            placeholders = ','.join('?' * len(exclude_ids))
            search_conditions.append(f"r.id NOT IN ({placeholders})")
            search_params.extend(exclude_ids)
        
        # Build final query
        where_clause = " AND ".join(search_conditions)
        
        search_query = f"""
            SELECT DISTINCT r.id, r.title, r.description, r.servings, 
                   r.hands_on_time, r.total_time, r.ingredients, r.instructions,
                   r.book_id, r.page_number
            FROM recipes r
            WHERE {where_clause}
            ORDER BY r.title
            LIMIT ?
        """
        
        search_params.append(limit)
        
        cursor.execute(search_query, search_params)
        recipes = []
        
        for row in cursor.fetchall():
            # Classify recipe types
            recipe_types = self.classify_recipe_types(row['title'], row['instructions'] or '')
            
            recipe = {
                'id': row['id'],
                'title': row['title'],
                'name': row['title'],
                'description': row['description'] or '',
                'servings': row['servings'] or '4 servings',
                'prep_time': row['hands_on_time'] or '',
                'cook_time': row['total_time'] or '',
                'ingredients': row['ingredients'] or '',
                'instructions': row['instructions'] or '',
                'book_id': row['book_id'],
                'page_number': row['page_number'],
                'recipe_types': recipe_types,
                'main_ingredient': main_ingredient
            }
            recipes.append(recipe)
        
        conn.close()
        
        return {
            'recipes': recipes,
            'main_ingredient': main_ingredient,
            'total_found': len(recipes),
            'search_metadata': {
                'query': query,
                'user_id': user_id,
                'exclude_count': len(exclude_ids) if exclude_ids else 0
            }
        }
    
    def get_conversation_suggestions(self, main_ingredient, current_recipes):
        """Generate conversation flow suggestions based on ingredient and current recipes"""
        suggestions = {
            'cuisine_options': [],
            'cooking_methods': [],
            'recipe_types': [],
            'related_ingredients': []
        }
        
        if main_ingredient in self.cuisine_flow:
            suggestions['cuisine_options'] = list(self.cuisine_flow[main_ingredient].keys())
        
        # Analyze current recipes for patterns
        all_types = []
        for recipe in current_recipes:
            all_types.extend(recipe.get('recipe_types', []))
        
        type_counts = Counter(all_types)
        
        # Suggest underrepresented types
        for recipe_type in ['one_pot', 'quick', 'easy', 'slow_cook']:
            if type_counts.get(recipe_type, 0) < 2:  # If less than 2 recipes of this type
                suggestions['recipe_types'].append(recipe_type)
        
        return suggestions
    
    def search_by_conversation_flow(self, base_ingredient, cuisine=None, recipe_type=None, 
                                  exclude_ids=None, limit=5):
        """Search recipes following conversation flow pattern"""
        
        query_parts = [base_ingredient]
        
        if cuisine and base_ingredient in self.cuisine_flow:
            cuisine_keywords = self.cuisine_flow[base_ingredient].get(cuisine, [])
            query_parts.extend(cuisine_keywords)
        
        if recipe_type:
            type_keywords = self.recipe_type_keywords.get(recipe_type, [])
            query_parts.extend(type_keywords[:2])  # Use first 2 keywords
        
        search_query = ' '.join(query_parts)
        return self.intelligent_search(search_query, exclude_ids=exclude_ids, limit=limit)
    
    def get_user_search_history(self, user_id="default", limit=10):
        """Get user's recent search history"""
        return self.user_searches[user_id][-limit:]

def main():
    """Test the enhanced search system"""
    print("🧠 Testing Enhanced Recipe Search Intelligence")
    print("=" * 50)
    
    engine = EnhancedRecipeSearchEngine()
    
    # Test 1: Sweet potato search
    print("\n🍠 Test 1: Sweet potato search")
    results = engine.intelligent_search("sweet potato", limit=10)
    print(f"Found {results['total_found']} recipes for '{results['main_ingredient']}'")
    
    for recipe in results['recipes'][:3]:
        print(f"  - {recipe['title']} (Types: {recipe['recipe_types']})")
    
    # Test 2: Conversation flow
    print(f"\n💬 Test 2: Conversation suggestions for {results['main_ingredient']}")
    suggestions = engine.get_conversation_suggestions(results['main_ingredient'], results['recipes'])
    print(f"Cuisine options: {suggestions['cuisine_options']}")
    print(f"Recipe types to explore: {suggestions['recipe_types']}")
    
    # Test 3: Refined search
    if results['recipes']:
        exclude_ids = [r['id'] for r in results['recipes'][:5]]
        print(f"\n🔄 Test 3: More sweet potato recipes (excluding {len(exclude_ids)} shown)")
        more_results = engine.intelligent_search("sweet potato", exclude_ids=exclude_ids, limit=5)
        print(f"Found {more_results['total_found']} additional recipes")
        
        for recipe in more_results['recipes'][:3]:
            print(f"  - {recipe['title']}")

if __name__ == "__main__":
    main()
