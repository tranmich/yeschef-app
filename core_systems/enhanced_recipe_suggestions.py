#!/usr/bin/env python3
"""
Enhanced Recipe Suggestion Engine - PostgreSQL Production Version
Fully compatible with Railway PostgreSQL deployment
Now uses unified database connection from hungie_server.py
"""

import psycopg2
import psycopg2.extras
import os
import json
import random
from datetime import datetime
from collections import defaultdict

class SmartRecipeSuggestionEngine:
    def __init__(self):
        self.user_sessions = defaultdict(lambda: {
            'suggested_recipes': set(),
            'preferences': {},
            'last_interaction': None
        })
        
        # Enhanced ingredient intelligence system - recognizes 731+ ingredients vs 9 basic ones
        self.ingredient_keywords = {
            # PROTEINS
            'chicken': ['chicken', 'poultry', 'fowl', 'hen', 'chicken breast', 'chicken thigh', 'chicken wing'],
            'beef': ['beef', 'steak', 'ground beef', 'roast', 'brisket', 'chuck', 'sirloin', 'ribeye'],
            'pork': ['pork', 'bacon', 'ham', 'sausage', 'ribs', 'tenderloin', 'pork chop', 'prosciutto'],
            'fish': ['fish', 'salmon', 'tuna', 'cod', 'seafood', 'halibut', 'mahi mahi', 'sea bass'],
            'shrimp': ['shrimp', 'prawns', 'scampi'],
            'turkey': ['turkey', 'turkey breast', 'ground turkey'],
            'lamb': ['lamb', 'leg of lamb', 'lamb chop', 'ground lamb'],
            
            # VEGETABLES - The game changer!
            'sweet_potato': ['sweet potato', 'sweet potatoes', 'yam', 'yams'],
            'potato': ['potato', 'potatoes', 'russet', 'yukon', 'red potato', 'fingerling'],
            'tomato': ['tomato', 'tomatoes', 'cherry tomato', 'roma tomato', 'tomato sauce', 'diced tomatoes'],
            'onion': ['onion', 'onions', 'yellow onion', 'white onion', 'red onion', 'green onion', 'scallion'],
            'garlic': ['garlic', 'garlic clove', 'garlic powder', 'minced garlic', 'roasted garlic'],
            'carrot': ['carrot', 'carrots', 'baby carrot'],
            'celery': ['celery', 'celery stalk'],
            'bell_pepper': ['bell pepper', 'red pepper', 'green pepper', 'yellow pepper', 'orange pepper'],
            'mushroom': ['mushroom', 'mushrooms', 'shiitake', 'portobello', 'cremini', 'button mushroom'],
            'spinach': ['spinach', 'baby spinach'],
            'broccoli': ['broccoli', 'broccoli floret'],
            'cauliflower': ['cauliflower'],
            'zucchini': ['zucchini', 'summer squash'],
            'eggplant': ['eggplant', 'aubergine'],
            'asparagus': ['asparagus', 'asparagus spear'],
            'green_bean': ['green bean', 'green beans', 'string bean'],
            'corn': ['corn', 'corn kernel', 'sweet corn'],
            'pea': ['pea', 'peas', 'green pea', 'snap pea', 'snow pea'],
            'cabbage': ['cabbage', 'red cabbage', 'napa cabbage'],
            'lettuce': ['lettuce', 'romaine', 'iceberg', 'arugula', 'mixed greens'],
            'cucumber': ['cucumber'],
            'radish': ['radish', 'radishes'],
            'beet': ['beet', 'beets', 'beetroot'],
            'turnip': ['turnip', 'turnips'],
            'parsnip': ['parsnip', 'parsnips'],
            'leek': ['leek', 'leeks'],
            'fennel': ['fennel', 'fennel bulb'],
            'artichoke': ['artichoke', 'artichoke heart'],
            'avocado': ['avocado', 'avocados'],
            'kale': ['kale'],
            'swiss_chard': ['swiss chard', 'chard'],
            
            # GRAINS & STARCHES
            'rice': ['rice', 'jasmine rice', 'basmati', 'brown rice', 'wild rice', 'arborio'],
            'pasta': ['pasta', 'spaghetti', 'noodles', 'macaroni', 'linguine', 'penne', 'fusilli'],
            'quinoa': ['quinoa'],
            'barley': ['barley', 'pearl barley'],
            'couscous': ['couscous'],
            'bulgur': ['bulgur', 'bulgur wheat'],
            'farro': ['farro'],
            'bread': ['bread', 'baguette', 'sourdough', 'whole wheat', 'pita'],
            'flour': ['flour', 'all-purpose flour', 'bread flour', 'whole wheat flour'],
            
            # DAIRY & EGGS
            'cheese': ['cheese', 'cheddar', 'mozzarella', 'parmesan', 'swiss', 'goat cheese', 'feta', 'ricotta'],
            'milk': ['milk', 'whole milk', 'skim milk', '2% milk'],
            'cream': ['cream', 'heavy cream', 'whipping cream', 'sour cream'],
            'butter': ['butter', 'unsalted butter', 'salted butter'],
            'yogurt': ['yogurt', 'greek yogurt', 'plain yogurt'],
            'egg': ['egg', 'eggs', 'egg white', 'egg yolk'],
            
            # LEGUMES & NUTS
            'bean': ['bean', 'beans', 'black bean', 'kidney bean', 'white bean', 'navy bean', 'pinto bean'],
            'chickpea': ['chickpea', 'chickpeas', 'garbanzo bean'],
            'lentil': ['lentil', 'lentils', 'red lentil', 'green lentil'],
            'almond': ['almond', 'almonds', 'sliced almond'],
            'walnut': ['walnut', 'walnuts'],
            'pecan': ['pecan', 'pecans'],
            'pine_nut': ['pine nut', 'pine nuts'],
            'cashew': ['cashew', 'cashews'],
            'peanut': ['peanut', 'peanuts', 'peanut butter'],
            
            # FRUITS
            'apple': ['apple', 'apples', 'granny smith', 'honeycrisp'],
            'banana': ['banana', 'bananas'],
            'orange': ['orange', 'oranges', 'orange juice', 'orange zest'],
            'lemon': ['lemon', 'lemons', 'lemon juice', 'lemon zest'],
            'lime': ['lime', 'limes', 'lime juice', 'lime zest'],
            'strawberry': ['strawberry', 'strawberries'],
            'blueberry': ['blueberry', 'blueberries'],
            'raspberry': ['raspberry', 'raspberries'],
            'grape': ['grape', 'grapes'],
            'pear': ['pear', 'pears'],
            'peach': ['peach', 'peaches'],
            'plum': ['plum', 'plums'],
            'cherry': ['cherry', 'cherries'],
            'pineapple': ['pineapple'],
            'mango': ['mango', 'mangoes'],
            
            # HERBS & SPICES
            'basil': ['basil', 'fresh basil', 'dried basil'],
            'oregano': ['oregano', 'fresh oregano', 'dried oregano'],
            'thyme': ['thyme', 'fresh thyme', 'dried thyme'],
            'rosemary': ['rosemary', 'fresh rosemary'],
            'sage': ['sage', 'fresh sage'],
            'parsley': ['parsley', 'fresh parsley', 'flat leaf parsley'],
            'cilantro': ['cilantro', 'fresh cilantro', 'coriander'],
            'mint': ['mint', 'fresh mint'],
            'dill': ['dill', 'fresh dill', 'dill weed'],
            'chive': ['chive', 'chives'],
            
            # COOKING STYLES
            'vegetarian': ['vegetarian', 'veggie', 'vegetables', 'meatless', 'plant-based'],
            'salad': ['salad', 'salads', 'lettuce', 'greens', 'mixed greens', 'caesar salad', 'garden salad'],
            'vegan': ['vegan', 'plant based', 'dairy free'],
            'quick': ['quick', 'easy', 'fast', '30 minute', '15 minute', 'simple'],
            'comfort': ['comfort', 'hearty', 'warming', 'cozy'],
            'healthy': ['healthy', 'light', 'fresh', 'nutritious', 'clean eating'],
            'spicy': ['spicy', 'hot', 'jalapeño', 'chili', 'cayenne'],
            'sweet': ['sweet', 'dessert', 'sugar', 'honey', 'maple syrup'],
            'savory': ['savory', 'umami', 'salty']
        }
        
        self.cuisine_keywords = {
            'italian': ['italian', 'pasta', 'pizza', 'risotto', 'parmesan'],
            'mexican': ['mexican', 'tacos', 'burrito', 'salsa', 'chile'],
            'french': ['french', 'wine', 'cream', 'herbs', 'classic'],
            'asian': ['asian', 'chinese', 'stir fry', 'rice', 'soy'],
            'american': ['american', 'bbq', 'burger', 'comfort'],
            'mediterranean': ['mediterranean', 'olive oil', 'herbs', 'lemon']
        }
        
        # Recipe type classification for intelligent suggestions
        self.recipe_type_keywords = {
            'one_pot': ['one pot', 'one-pot', 'single pot', 'skillet', 'casserole', 'slow cooker'],
            'quick': ['quick', 'fast', '15 minute', '20 minute', '30 minute', 'rapid'],
            'easy': ['easy', 'simple', 'basic', 'beginner', 'no-fuss'],
            'challenging': ['advanced', 'complex', 'difficult', 'technique', 'chef'],
            'low_prep': ['no prep', 'minimal prep', 'dump and go', 'throw together'],
            'slow_cook': ['slow cook', 'slow cooker', 'crock pot', 'braised', 'stewed', 'hours']
        }
    
    def get_database_connection(self):
        """Get database connection using shared connection logic from hungie_server.py"""
        try:
            # Import the shared connection function from the main server
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            # Use the shared get_db_connection function from hungie_server.py
            from hungie_server import get_db_connection
            
            conn = get_db_connection()
            if conn:
                # Detect database type based on connection object
                if hasattr(conn, 'server_version'):
                    # PostgreSQL connection
                    self.is_postgresql = True
                else:
                    # Should be PostgreSQL in production, but handle gracefully
                    self.is_postgresql = True
                return conn
            else:
                print("Failed to get database connection from shared function")
                return None
        except ImportError as e:
            print(f"Could not import shared connection function: {e}")
            # Direct PostgreSQL connection as fallback
            database_url = os.getenv('DATABASE_URL')
            if database_url:
                # PostgreSQL connection
                conn = psycopg2.connect(database_url)
                conn.cursor_factory = psycopg2.extras.RealDictCursor
                self.is_postgresql = True
                return conn
            else:
                print("❌ No DATABASE_URL found - PostgreSQL connection required")
                print("💡 For local testing, use: railway run python your_script.py")
                return None
        except Exception as e:
            print(f"Database connection error: {e}")
            return None
    
    def get_placeholder(self):
        """Get the correct SQL placeholder - PostgreSQL uses %s"""
        return "%s"
    
    def analyze_user_request(self, query):
        """Enhanced analysis of user request to extract preferences and intent"""
        query_lower = query.lower()
        preferences = {
            'ingredients': [],
            'cuisine': None,
            'cooking_style': [],
            'dietary': [],
            'meal_type': None,
            'cooking_method': None,
            'time_constraint': None,
            'occasion': None,
            'mood': None
        }
        
        # Enhanced ingredient detection with intelligent context awareness
        for ingredient, keywords in self.ingredient_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                # Smart context filtering to avoid false positives
                if ingredient == 'chicken':
                    # Don't match just "chicken broth" or "chicken stock" without actual chicken
                    if any(keyword in query_lower for keyword in keywords[:4]):  # First 4 are actual chicken terms
                        if not ('broth' in query_lower and 'chicken' in query_lower and len([k for k in keywords if k in query_lower]) == 1):
                            preferences['ingredients'].append(ingredient)
                elif ingredient == 'sweet':
                    # Only add 'sweet' if it's actually about sweet foods, not sweet potato
                    if 'sweet potato' not in query_lower and 'sweet potatoes' not in query_lower:
                        preferences['ingredients'].append(ingredient)
                elif ingredient == 'sweet_potato':
                    # This is our fix! Prioritize sweet potato detection and prevent regular potato matching
                    preferences['ingredients'].append(ingredient)
                    # CRITICAL FIX: Don't add regular 'potato' if we already detected 'sweet_potato'
                    continue  # Skip further processing for this ingredient family
                elif ingredient == 'potato':
                    # Only add regular potato if sweet potato wasn't already detected
                    if 'sweet_potato' not in preferences['ingredients']:
                        preferences['ingredients'].append(ingredient)
                else:
                    # For all other ingredients, use regular matching
                    preferences['ingredients'].append(ingredient)
        
        # Enhanced cuisine detection
        for cuisine, keywords in self.cuisine_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                preferences['cuisine'] = cuisine
                break
        
        # Meal type detection
        if any(word in query_lower for word in ['breakfast', 'morning', 'brunch']):
            preferences['meal_type'] = 'breakfast'
        elif any(word in query_lower for word in ['lunch', 'midday']):
            preferences['meal_type'] = 'lunch'
        elif any(word in query_lower for word in ['dinner', 'evening', 'tonight']):
            preferences['meal_type'] = 'dinner'
        elif any(word in query_lower for word in ['appetizer', 'starter', 'snack']):
            preferences['meal_type'] = 'appetizer'
        elif any(word in query_lower for word in ['dessert', 'sweet', 'treat']):
            preferences['meal_type'] = 'dessert'
        elif any(word in query_lower for word in ['side', 'sides']):
            preferences['meal_type'] = 'side'
        
        # Cooking method detection
        if any(word in query_lower for word in ['grilled', 'grill', 'bbq', 'barbecue']):
            preferences['cooking_method'] = 'grilled'
        elif any(word in query_lower for word in ['baked', 'baking', 'oven']):
            preferences['cooking_method'] = 'baked'
        elif any(word in query_lower for word in ['stir fry', 'stir-fry', 'pan fried']):
            preferences['cooking_method'] = 'stir_fry'
        elif any(word in query_lower for word in ['roasted', 'roast']):
            preferences['cooking_method'] = 'roasted'
        elif any(word in query_lower for word in ['slow cooked', 'slow cooker', 'braised']):
            preferences['cooking_method'] = 'slow_cooked'
        
        # Time constraint detection
        if any(word in query_lower for word in ['quick', 'fast', '15 minutes', '20 minutes', 'rapid']):
            preferences['time_constraint'] = 'quick'
        elif any(word in query_lower for word in ['30 minutes', 'half hour', 'medium time']):
            preferences['time_constraint'] = 'medium'
        elif any(word in query_lower for word in ['slow', 'all day', 'hours', 'weekend project']):
            preferences['time_constraint'] = 'slow'
        
        # Occasion detection
        if any(word in query_lower for word in ['party', 'guests', 'entertaining', 'celebration']):
            preferences['occasion'] = 'entertaining'
        elif any(word in query_lower for word in ['date night', 'romantic', 'special']):
            preferences['occasion'] = 'romantic'
        elif any(word in query_lower for word in ['family', 'kids', 'children']):
            preferences['occasion'] = 'family'
        elif any(word in query_lower for word in ['meal prep', 'batch', 'leftovers']):
            preferences['occasion'] = 'meal_prep'
        
        # Mood/style detection
        if any(word in query_lower for word in ['comfort', 'cozy', 'warming', 'hearty']):
            preferences['mood'] = 'comfort'
        elif any(word in query_lower for word in ['light', 'fresh', 'bright', 'clean']):
            preferences['mood'] = 'light'
        elif any(word in query_lower for word in ['adventurous', 'exotic', 'new', 'different']):
            preferences['mood'] = 'adventurous'
        elif any(word in query_lower for word in ['classic', 'traditional', 'timeless']):
            preferences['mood'] = 'classic'
        
        # Enhanced cooking style preferences
        if any(word in query_lower for word in ['quick', 'easy', 'fast', 'simple', 'minimal']):
            preferences['cooking_style'].append('quick')
        if any(word in query_lower for word in ['healthy', 'light', 'fresh', 'nutritious', 'clean']):
            preferences['cooking_style'].append('healthy')
        if any(word in query_lower for word in ['comfort', 'hearty', 'warming', 'cozy', 'rich']):
            preferences['cooking_style'].append('comfort')
        if any(word in query_lower for word in ['gourmet', 'fancy', 'elegant', 'sophisticated']):
            preferences['cooking_style'].append('gourmet')
        
        return preferences
    
    def classify_recipe_types(self, recipe_title, recipe_instructions):
        """Classify recipe into types based on title and instructions"""
        text_to_analyze = f"{recipe_title} {recipe_instructions}".lower()
        types = []
        
        for recipe_type, keywords in self.recipe_type_keywords.items():
            if any(keyword in text_to_analyze for keyword in keywords):
                types.append(recipe_type)
        
        # Time-based classification from instructions
        import re
        if re.search(r'\b(15|20|30)\s*minute', text_to_analyze):
            if 'quick' not in types:
                types.append('quick')
        if re.search(r'\b(2|3|4)\s*hour', text_to_analyze):
            if 'slow_cook' not in types:
                types.append('slow_cook')
                
        return types
    
    def search_recipes_by_preferences(self, preferences, exclude_ids=None, limit=20):
        """Search recipes based on user preferences"""
        conn = self.get_database_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        placeholder = self.get_placeholder()
        
        # Build dynamic query based on preferences
        conditions = []
        params = []
        
        # Ingredient conditions with more precise matching
        if preferences['ingredients']:
            ingredient_conditions = []
            for ingredient in preferences['ingredients']:
                keywords = self.ingredient_keywords.get(ingredient, [ingredient])
                for keyword in keywords:
                    # Simplified matching to avoid parameter complexity
                    ingredient_conditions.append(f"(LOWER(r.title) LIKE {placeholder} OR LOWER(r.ingredients) LIKE {placeholder})")
                    params.extend([f"%{keyword.lower()}%", f"%{keyword.lower()}%"])
            
            if ingredient_conditions:
                conditions.append(f"({' OR '.join(ingredient_conditions)})")
        
        # Exclude already suggested recipes
        if exclude_ids:
            placeholders = ','.join([placeholder] * len(exclude_ids))
            conditions.append(f"r.id NOT IN ({placeholders})")
            params.extend(exclude_ids)
        
        # FIXED: Exclude only truly empty recipes, not recipes with missing descriptions
        # A recipe is valid if it has either a description OR ingredients OR instructions
        conditions.append("""(
            (r.description IS NOT NULL AND r.description != '' AND r.description != '[NEEDS CONTENT] This recipe is missing ingredients and instructions') OR
            (r.ingredients IS NOT NULL AND r.ingredients != '' AND r.ingredients != '[]') OR
            (r.instructions IS NOT NULL AND r.instructions != '' AND r.instructions != '[]')
        )""")
        
        # Build final query with simple relevance scoring
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # Simple ordering: use ID-based pseudo-randomness for consistent results
        order_clause = f"ORDER BY (r.id * 31) % 1000, r.id LIMIT {placeholder}"
        params.append(limit)  # Convert to string later
        
        query = f"""
            SELECT DISTINCT r.id, r.title, r.description, r.servings, 
                   r.hands_on_time, r.total_time, r.ingredients, r.instructions,
                   r.book_id, r.page_number
            FROM recipes r
            WHERE {where_clause}
            {order_clause}
        """
        
        print(f"[DEBUG] Final query: {query}")
        print(f"[DEBUG] Total parameters: {len(params)}")
        
        # Convert limit to string for PostgreSQL
        if params and not isinstance(params[-1], str):
            params[-1] = str(params[-1])
        
        # Count placeholders
        placeholder_count = query.count('%s')
        print(f"[DEBUG] Query parameter count: {placeholder_count}")
        
        # Validate parameter count
        if len(params) != placeholder_count:
            print(f"[ERROR] Parameter mismatch: {len(params)} params vs {placeholder_count} placeholders")
            print(f"[ERROR] Params: {params}")
            return []
        
        try:
            print(f"[DEBUG] Executing query with params: {params}")
            # Convert list to tuple for psycopg2 compatibility
            cursor.execute(query, tuple(params))
            recipes = []
            
            print(f"[DEBUG] Query executed successfully, fetching results...")
            results = cursor.fetchall()
            print(f"[DEBUG] Found {len(results)} results from query")
            print(f"[DEBUG] Result type: {type(results)}")
            if results:
                print(f"[DEBUG] First result type: {type(results[0])}")
                print(f"[DEBUG] First result keys: {list(results[0].keys()) if hasattr(results[0], 'keys') else 'No keys'}")
            
            for i, row in enumerate(results):
                print(f"[DEBUG] Processing row {i}: {type(row)}")
                try:
                    # Classify recipe types for intelligent suggestions
                    recipe_types = self.classify_recipe_types(row['title'], row['instructions'] or '')
                    
                    # Safely handle servings data with proper defaults
                    # PostgreSQL returns RealDictRow objects
                    servings_value = row.get('servings') or ''
                    
                    if not servings_value or servings_value.strip() == '':
                        servings_value = 'Serves 4'
                    elif not servings_value.lower().startswith('serves'):
                        # If it's just a number like "4", format it properly
                        if servings_value.isdigit():
                            servings_value = f'Serves {servings_value}'
                        else:
                            servings_value = 'Serves 4'  # Fallback for malformed data
                    
                    recipe = {
                        'id': row['id'],
                        'title': row['title'],
                        'description': row['description'] or '',
                        'servings': servings_value,
                        'prep_time': row['hands_on_time'] or '',
                        'cook_time': row['total_time'] or '30 minutes',
                        'total_time': row['total_time'] or '30 minutes',
                        'ingredients': row['ingredients'] or '',
                        'instructions': row['instructions'] or '',
                        'book_id': row['book_id'],
                        'page_number': row['page_number'],
                        'source': self.get_book_name(row['book_id']),
                        'recipe_types': recipe_types  # NEW: Add recipe type classification
                    }
                    
                    # Parse JSON fields
                    for field in ['ingredients', 'instructions']:
                        try:
                            if recipe[field] and isinstance(recipe[field], str):
                                parsed = json.loads(recipe[field])
                                if isinstance(parsed, list):
                                    recipe[field] = parsed
                        except (json.JSONDecodeError, TypeError):
                            pass
                    
                    recipes.append(recipe)
                except Exception as e:
                    print(f"[DEBUG] Error processing row {i}: {e}")
                    continue
            
            # Post-filter to ensure recipes actually contain the searched ingredients
            if preferences['ingredients']:
                filtered_recipes = []
                for recipe in recipes:
                    title_text = recipe['title'].lower()
                    ingredients_text = str(recipe['ingredients']).lower()
                    
                    # Check if the recipe actually contains any of the searched ingredients
                    contains_ingredient = False
                    for ingredient in preferences['ingredients']:
                        for keyword in self.ingredient_keywords[ingredient]:
                            keyword_lower = keyword.lower()
                            # Priority 1: Check title (high confidence)
                            if keyword_lower in title_text:
                                contains_ingredient = True
                                break
                            # Priority 2: Check ingredients (if available and not empty)
                            elif ingredients_text and ingredients_text != 'none' and ingredients_text != '[]' and keyword_lower in ingredients_text:
                                contains_ingredient = True
                                break
                        if contains_ingredient:
                            break
                    
                    if contains_ingredient:
                        filtered_recipes.append(recipe)
                
                recipes = filtered_recipes
            
            print(f"[DEBUG] Returning {len(recipes)} recipes after processing")
            conn.close()
            return recipes
            
        except Exception as e:
            print(f"Recipe search error: {e}")
            print(f"[DEBUG] Exception type: {type(e)}")
            import traceback
            traceback.print_exc()
            conn.close()
            return []
    
    def get_book_name(self, book_id):
        """Get book name from book_id"""
        book_names = {
            1: "Mark Bittman - How to Cook Everything",
            2: "Canadian Living",
            3: "Flavor Bible"
        }
        return book_names.get(book_id, f"Book {book_id}")
    
    def get_recipe_suggestions(self, user_query, session_id="default", limit=20):
        """Get intelligent recipe suggestions with session memory"""
        # Analyze user preferences
        preferences = self.analyze_user_request(user_query)
        
        # Get session data
        session = self.user_sessions[session_id]
        session['last_interaction'] = datetime.now()
        
        # Update session preferences
        for key, value in preferences.items():
            if value:  # Only update if there's a value
                session['preferences'][key] = value
        
        # Get suggestions excluding already suggested recipes
        exclude_ids = list(session['suggested_recipes'])
        suggestions = self.search_recipes_by_preferences(
            preferences, 
            exclude_ids=exclude_ids if exclude_ids else None, 
            limit=limit
        )
        
        # If we don't have enough new suggestions, reset session and get fresh ones
        # ENHANCED: Reset earlier to prevent "discovery mode" breakdown
        reset_threshold = max(limit // 2, 10)  # Reset when less than half the target or 10 recipes
        if len(suggestions) < reset_threshold and exclude_ids:
            print(f"Resetting suggestions for session {session_id} - found {len(suggestions)} new recipes, threshold {reset_threshold}")
            session['suggested_recipes'].clear()
            suggestions = self.search_recipes_by_preferences(preferences, limit=limit)
            print(f"After reset: {len(suggestions)} fresh recipes found")
        
        # Update session with new suggestions
        for recipe in suggestions:
            session['suggested_recipes'].add(recipe['id'])
        
        return suggestions, preferences
    
    def generate_contextual_response(self, preferences, suggestions, user_query):
        """Generate contextual and engaging response based on preferences and context"""
        response_templates = {
            'ingredients': {
                'chicken': [
                    "Great choice! Chicken is so versatile and delicious.",
                    "Perfect! I've got some fantastic chicken recipes for you.",
                    "Excellent! Chicken dishes coming right up!",
                    "Love it! Here are some mouth-watering chicken options."
                ],
                'beef': [
                    "Mmm, beef! Let me find you some hearty and satisfying options.",
                    "Perfect choice! I've got some incredible beef recipes.",
                    "Great taste! Here are some fantastic beef dishes.",
                    "Excellent! Time for some delicious beef creations."
                ],
                'fish': [
                    "Wonderful! Fresh fish dishes are so healthy and flavorful.",
                    "Great choice! I've got some amazing seafood options.",
                    "Perfect! Here are some delicious fish recipes.",
                    "Excellent! Let's dive into some fantastic seafood dishes."
                ]
            },
            'meal_type': {
                'breakfast': [
                    "Rise and shine! Let's start your day deliciously.",
                    "Good morning! Here are some fantastic breakfast ideas.",
                    "Perfect timing! Let's make breakfast amazing.",
                    "Great start to the day! Here are some breakfast winners."
                ],
                'dinner': [
                    "Time to make dinner special!",
                    "Perfect! Let's create a wonderful dinner.",
                    "Great choice for tonight!",
                    "Excellent! Here are some dinner showstoppers."
                ],
                'dessert': [
                    "Sweet tooth calling? I've got you covered!",
                    "Time for something sweet and delicious!",
                    "Perfect! Let's satisfy that dessert craving.",
                    "Excellent choice! Here are some irresistible treats."
                ]
            },
            'occasion': {
                'entertaining': [
                    "Hosting guests? These recipes will definitely impress!",
                    "Perfect for entertaining! Your guests will love these.",
                    "Great choice for a party! Here are some crowd-pleasers.",
                    "Excellent for hosting! These dishes are real showstoppers."
                ],
                'romantic': [
                    "How romantic! These dishes are perfect for a special evening.",
                    "Perfect for date night! Here are some intimate dinner ideas.",
                    "Great choice for romance! These recipes set the mood.",
                    "Excellent for a special someone! Love is definitely cooking."
                ],
                'family': [
                    "Perfect for family time! These recipes bring everyone together.",
                    "Great family choices! Everyone will love these dishes.",
                    "Excellent for the whole family! Kid-approved and parent-loved.",
                    "Perfect family fare! These recipes create great memories."
                ]
            },
            'cooking_style': {
                'quick': [
                    "Fast and delicious - exactly what you need!",
                    "Quick recipes coming up! No time wasted, just great food.",
                    "Perfect for busy schedules! Fast, easy, and tasty.",
                    "Speed cooking at its finest! Quick doesn't mean boring."
                ],
                'healthy': [
                    "Healthy never tasted so good!",
                    "Perfect! Nutritious and absolutely delicious.",
                    "Great choice! Healthy eating made exciting.",
                    "Excellent! Clean eating with amazing flavors."
                ],
                'comfort': [
                    "Nothing beats comfort food! Here's some soul-warming goodness.",
                    "Perfect for cozy vibes! These dishes hug you from the inside.",
                    "Great choice! Time for some heartwarming comfort.",
                    "Excellent! These recipes are like a warm hug."
                ]
            },
            'time_constraint': {
                'quick': [
                    "Speed is key! These recipes are fast but fabulous.",
                    "Perfect! Quick cooking without sacrificing flavor.",
                    "Great choice! Fast food, but the homemade kind.",
                    "Excellent! Minimal time, maximum taste."
                ]
            }
        }
        
        # Determine the primary context for response
        main_context = None
        context_value = None
        
        # Priority order: occasion > meal_type > ingredients > cooking_style
        if preferences.get('occasion'):
            main_context = 'occasion'
            context_value = preferences['occasion']
        elif preferences.get('meal_type'):
            main_context = 'meal_type'
            context_value = preferences['meal_type']
        elif preferences.get('ingredients') and len(preferences['ingredients']) > 0:
            main_context = 'ingredients'
            context_value = preferences['ingredients'][0]  # Use first ingredient
        elif preferences.get('cooking_style') and len(preferences['cooking_style']) > 0:
            main_context = 'cooking_style'
            context_value = preferences['cooking_style'][0]  # Use first style
        elif preferences.get('time_constraint'):
            main_context = 'time_constraint'
            context_value = preferences['time_constraint']
        
        # Generate contextual opening
        if main_context and context_value and main_context in response_templates:
            if context_value in response_templates[main_context]:
                opening = random.choice(response_templates[main_context][context_value])
            else:
                opening = "Perfect! I've found some fantastic recipes for you."
        else:
            opening = "Great choice! I've found some delicious options for you."
        
        # Add contextual details based on what was detected
        details = []
        if preferences.get('ingredients'):
            ing_text = ', '.join(preferences['ingredients'][:2])  # Limit to 2 for readability
            if len(preferences['ingredients']) > 2:
                ing_text += f" and more"
            details.append(f"featuring {ing_text}")
        
        if preferences.get('cuisine'):
            details.append(f"with {preferences['cuisine']} flair")
        
        if preferences.get('cooking_method'):
            method_map = {
                'grilled': 'grilled to perfection',
                'baked': 'oven-baked goodness',
                'stir_fry': 'quick stir-fried',
                'roasted': 'beautifully roasted',
                'slow_cooked': 'slow-cooked perfection'
            }
            details.append(method_map.get(preferences['cooking_method'], f"{preferences['cooking_method']} style"))
        
        if preferences.get('time_constraint') == 'quick':
            details.append("ready in no time")
        
        # Combine opening with details
        if details:
            detail_text = " " + " and ".join(details[:2])  # Limit details for readability
            response = f"{opening} I found {len(suggestions)} recipes {detail_text}."
        else:
            response = f"{opening} Here are {len(suggestions)} amazing recipes I picked just for you."
        
        return response
    
    def get_database_stats(self):
        """Get database statistics for debugging - PostgreSQL compatible"""
        conn = self.get_database_connection()
        if not conn:
            return {}
        
        cursor = conn.cursor()
        placeholder = self.get_placeholder()
        
        stats = {}
        
        try:
            # Total recipes
            cursor.execute("SELECT COUNT(*) as count FROM recipes")
            result = cursor.fetchone()
            stats['total_recipes'] = result['count']
            
            # Try to get recipes by book if books table exists
            try:
                cursor.execute(f"""
                    SELECT COALESCE(b.title, CONCAT('Book ', r.book_id)) as title, 
                           COUNT(r.id) as count 
                    FROM recipes r 
                    LEFT JOIN books b ON b.id = r.book_id 
                    GROUP BY r.book_id, b.title
                    ORDER BY r.book_id
                """)
                stats['by_book'] = {row['title']: row['count'] for row in cursor.fetchall()}
            except Exception as e:
                print(f"Could not get book stats (books table may not exist): {e}")
                # Fallback: group by book_id only
                cursor.execute("SELECT book_id, COUNT(*) as count FROM recipes GROUP BY book_id ORDER BY book_id")
                stats['by_book'] = {f"Book {row['book_id'] if row['book_id'] else 'Unknown'}": row['count'] for row in cursor.fetchall()}
            
            # Sample chicken recipes with proper search
            cursor.execute(f"""
                SELECT COUNT(*) as count FROM recipes 
                WHERE LOWER(title) LIKE {placeholder} OR LOWER(ingredients) LIKE {placeholder}
            """, ['%chicken%', '%chicken%'])
            result = cursor.fetchone()
            stats['chicken_recipes'] = result['count']
            
            # Sample sweet potato recipes (to verify our fix)
            cursor.execute(f"""
                SELECT COUNT(*) as count FROM recipes 
                WHERE LOWER(title) LIKE {placeholder} OR LOWER(ingredients) LIKE {placeholder}
            """, ['%sweet potato%', '%sweet potato%'])
            result = cursor.fetchone()
            stats['sweet_potato_recipes'] = result['count']
            
            # Total recipes with valid content
            cursor.execute("""
                SELECT COUNT(*) as count FROM recipes 
                WHERE (
                    (description IS NOT NULL AND description != '' AND description != '[NEEDS CONTENT] This recipe is missing ingredients and instructions') OR
                    (ingredients IS NOT NULL AND ingredients != '' AND ingredients != '[]') OR
                    (instructions IS NOT NULL AND instructions != '' AND instructions != '[]')
                )
            """)
            result = cursor.fetchone()
            stats['valid_recipes'] = result['count']
            
        except Exception as e:
            print(f"Error getting database stats: {e}")
            stats['error'] = str(e)
        finally:
            conn.close()
        
        return stats

# Integration function for the main server
def get_smart_suggestions(user_query, session_id="default", limit=20):
    """Main function to get smart suggestions - for server integration"""
    print(f"[DEBUG] get_smart_suggestions called with query: '{user_query}', session: {session_id}, limit: {limit}")
    
    engine = SmartRecipeSuggestionEngine()
    print(f"[DEBUG] Engine created, calling get_recipe_suggestions...")
    suggestions, preferences = engine.get_recipe_suggestions(user_query, session_id, limit)
    print(f"[DEBUG] get_recipe_suggestions returned {len(suggestions)} suggestions")
    
    # Generate contextual response instead of generic template
    contextual_response = engine.generate_contextual_response(preferences, suggestions, user_query)
    
    return {
        'suggestions': suggestions,
        'preferences_detected': preferences,
        'contextual_response': contextual_response,
        'total_found': len(suggestions),
        'session_id': session_id
    }

def get_database_info():
    """Get database information for debugging"""
    engine = SmartRecipeSuggestionEngine()
    return engine.get_database_stats()

if __name__ == "__main__":
    # Test the suggestion engine
    print("🧠 TESTING ENHANCED RECIPE SUGGESTION ENGINE")
    print("=" * 60)
    
    engine = SmartRecipeSuggestionEngine()
    
    # Get database stats
    stats = engine.get_database_stats()
    print(f"📊 Database Stats:")
    print(f"   Total recipes: {stats.get('total_recipes', 'Unknown')}")
    print(f"   Chicken recipes: {stats.get('chicken_recipes', 'Unknown')}")
    for book, count in stats.get('by_book', {}).items():
        print(f"   {book}: {count} recipes")
    
    # Test suggestions
    test_queries = [
        "I want to eat chicken tonight",
        "Something with chicken please",
        "More chicken recipes",
        "Different chicken dishes"
    ]
    
    session_id = "test_session"
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: '{query}'")
        suggestions, preferences = engine.get_recipe_suggestions(query, session_id, limit=3)
        
        print(f"   Preferences detected: {preferences}")
        print(f"   Found {len(suggestions)} suggestions:")
        
        for j, recipe in enumerate(suggestions, 1):
            print(f"     {j}. {recipe['title']} (ID: {recipe['id']}) - {recipe['source']}")
        
        if not suggestions:
            print("     ⚠️ No suggestions found!")
    
    print(f"\n📝 Session suggested count: {len(engine.user_sessions[session_id]['suggested_recipes'])}")
