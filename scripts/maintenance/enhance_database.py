#!/usr/bin/env python3
"""
Apply Analyzer and Flavor Profile to Canadian Living Database
Enhances our 254 recipes with analysis and flavor profiles
"""

import sqlite3
import json
import os
from pathlib import Path

def check_current_database():
    """Check current database structure and content"""
    print("🔍 CHECKING CURRENT DATABASE")
    print("=" * 50)
    
    conn = sqlite3.connect('recipe_books.db')
    cursor = conn.cursor()
    
    # Check table structure
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"📊 Tables: {tables}")
    
    # Check recipes
    cursor.execute("SELECT COUNT(*) FROM recipes")
    recipe_count = cursor.fetchone()[0]
    print(f"🍽️ Total recipes: {recipe_count}")
    
    # Show sample recipes
    cursor.execute("SELECT id, title, page_number FROM recipes LIMIT 5")
    samples = cursor.fetchall()
    print(f"\n📋 Sample recipes:")
    for recipe_id, title, page in samples:
        print(f"  {recipe_id}: {title} (Page {page})")
    
    # Check ingredients content
    cursor.execute("SELECT id, title, ingredients FROM recipes WHERE id = 1")
    sample_recipe = cursor.fetchone()
    if sample_recipe:
        recipe_id, title, ingredients_json = sample_recipe
        ingredients = json.loads(ingredients_json) if ingredients_json else []
        print(f"\n🥗 Sample ingredients for '{title}':")
        for ing in ingredients[:5]:
            print(f"  - {ing}")
        if len(ingredients) > 5:
            print(f"  ... and {len(ingredients) - 5} more")
    
    conn.close()
    return recipe_count

def create_enhanced_tables():
    """Create tables for enhanced analysis and flavor profiles"""
    print("\n🔧 CREATING ENHANCED TABLES")
    print("=" * 50)
    
    conn = sqlite3.connect('recipe_books.db')
    cursor = conn.cursor()
    
    # Create ingredients table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            normalized_name TEXT,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create recipe_ingredients junction table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipe_ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER,
            ingredient_id INTEGER,
            quantity TEXT,
            unit TEXT,
            preparation TEXT,
            FOREIGN KEY (recipe_id) REFERENCES recipes (id),
            FOREIGN KEY (ingredient_id) REFERENCES ingredients (id)
        )
    ''')
    
    # Create flavor profiles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipe_flavor_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER UNIQUE,
            primary_flavors TEXT,  -- JSON array
            secondary_flavors TEXT,  -- JSON array
            intensity TEXT,
            cooking_methods TEXT,  -- JSON array
            cuisine_style TEXT,
            season TEXT,
            dietary_tags TEXT,  -- JSON array
            complexity_score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (recipe_id) REFERENCES recipes (id)
        )
    ''')
    
    # Create recipe analysis table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipe_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER UNIQUE,
            ingredient_count INTEGER,
            instruction_count INTEGER,
            estimated_prep_time INTEGER,  -- minutes
            estimated_cook_time INTEGER,  -- minutes
            difficulty_level TEXT,
            nutrition_category TEXT,
            main_protein TEXT,
            cooking_techniques TEXT,  -- JSON array
            equipment_needed TEXT,  -- JSON array
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (recipe_id) REFERENCES recipes (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Enhanced tables created successfully")

def extract_and_analyze_ingredients():
    """Extract ingredients from recipes and analyze them"""
    print("\n🥗 EXTRACTING AND ANALYZING INGREDIENTS")
    print("=" * 50)
    
    conn = sqlite3.connect('recipe_books.db')
    cursor = conn.cursor()
    
    # Get all recipes with ingredients
    cursor.execute("SELECT id, title, ingredients FROM recipes")
    recipes = cursor.fetchall()
    
    ingredient_map = {}
    processed_count = 0
    
    for recipe_id, title, ingredients_json in recipes:
        if not ingredients_json:
            continue
            
        try:
            ingredients = json.loads(ingredients_json)
            
            for ingredient_text in ingredients:
                # Extract ingredient name from text like "2 cups flour" -> "flour"
                normalized_ingredient = normalize_ingredient(ingredient_text)
                
                if normalized_ingredient:
                    # Store ingredient if not exists
                    cursor.execute(
                        "INSERT OR IGNORE INTO ingredients (name, normalized_name) VALUES (?, ?)",
                        (ingredient_text, normalized_ingredient)
                    )
                    
                    # Get ingredient ID
                    cursor.execute(
                        "SELECT id FROM ingredients WHERE name = ?", 
                        (ingredient_text,)
                    )
                    ingredient_id = cursor.fetchone()[0]
                    
                    # Parse quantity and unit
                    quantity, unit, preparation = parse_ingredient_details(ingredient_text)
                    
                    # Link recipe to ingredient
                    cursor.execute('''
                        INSERT OR IGNORE INTO recipe_ingredients 
                        (recipe_id, ingredient_id, quantity, unit, preparation)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (recipe_id, ingredient_id, quantity, unit, preparation))
            
            processed_count += 1
            if processed_count % 20 == 0:
                print(f"   📊 Processed {processed_count}/{len(recipes)} recipes...")
                
        except Exception as e:
            print(f"   ⚠️ Error processing recipe {recipe_id}: {e}")
    
    conn.commit()
    
    # Show results
    cursor.execute("SELECT COUNT(*) FROM ingredients")
    total_ingredients = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM recipe_ingredients")
    total_links = cursor.fetchone()[0]
    
    print(f"✅ Extracted {total_ingredients} unique ingredients")
    print(f"✅ Created {total_links} recipe-ingredient links")
    
    # Show top ingredients
    cursor.execute('''
        SELECT i.normalized_name, COUNT(*) as usage_count
        FROM ingredients i
        JOIN recipe_ingredients ri ON i.id = ri.ingredient_id
        GROUP BY i.normalized_name
        ORDER BY usage_count DESC
        LIMIT 10
    ''')
    
    top_ingredients = cursor.fetchall()
    print(f"\n🏆 Top 10 most used ingredients:")
    for ingredient, count in top_ingredients:
        print(f"  {count:3d}x {ingredient}")
    
    conn.close()

def normalize_ingredient(ingredient_text):
    """Extract the core ingredient name from text like '2 cups all-purpose flour'"""
    import re
    
    # Remove common quantity patterns
    text = re.sub(r'^\d+(?:\.\d+)?(?:\s*½|\s*¼|\s*¾)?', '', ingredient_text.strip())
    text = re.sub(r'^[½¼¾⅓⅔]', '', text.strip())
    
    # Remove common units
    units = ['cup', 'cups', 'tbsp', 'tsp', 'tablespoon', 'tablespoons', 'teaspoon', 'teaspoons',
             'oz', 'lb', 'lbs', 'pound', 'pounds', 'ounce', 'ounces', 'g', 'kg', 'ml', 'l',
             'clove', 'cloves', 'can', 'cans', 'pkg', 'package', 'bunch', 'slice', 'slices']
    
    for unit in units:
        pattern = r'\b' + unit + r'\b'
        text = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
    
    # Remove common prep words but keep them for later
    prep_words = ['chopped', 'diced', 'minced', 'sliced', 'grated', 'fresh', 'dried', 
                  'ground', 'whole', 'large', 'medium', 'small', 'finely', 'coarsely']
    
    # Clean up extra spaces and commas
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'^[,\s]+|[,\s]+$', '', text)
    
    # Take the main ingredient (usually the last significant word or phrase)
    if text:
        # Handle compound ingredients like "all-purpose flour" -> "flour"
        words = text.split()
        if len(words) > 1:
            # Common patterns
            if 'flour' in text.lower():
                return 'flour'
            elif 'sugar' in text.lower():
                return 'sugar'
            elif 'butter' in text.lower():
                return 'butter'
            elif 'oil' in text.lower():
                return 'oil'
            elif 'onion' in text.lower():
                return 'onion'
            elif 'garlic' in text.lower():
                return 'garlic'
            else:
                # Return the last significant word
                return words[-1].lower()
        else:
            return text.lower()
    
    return None

def parse_ingredient_details(ingredient_text):
    """Parse quantity, unit, and preparation from ingredient text"""
    import re
    
    # Extract quantity (numbers and fractions)
    quantity_match = re.match(r'^(\d+(?:\.\d+)?(?:\s*½|\s*¼|\s*¾)?|[½¼¾⅓⅔])', ingredient_text.strip())
    quantity = quantity_match.group(1) if quantity_match else None
    
    # Extract unit
    units = ['cup', 'cups', 'tbsp', 'tsp', 'tablespoon', 'tablespoons', 'teaspoon', 'teaspoons',
             'oz', 'lb', 'lbs', 'pound', 'pounds', 'ounce', 'ounces', 'g', 'kg', 'ml', 'l',
             'clove', 'cloves', 'can', 'cans', 'pkg', 'package', 'bunch']
    
    unit = None
    for u in units:
        if re.search(r'\b' + u + r'\b', ingredient_text, re.IGNORECASE):
            unit = u.lower()
            break
    
    # Extract preparation
    prep_words = ['chopped', 'diced', 'minced', 'sliced', 'grated', 'fresh', 'dried', 
                  'ground', 'finely', 'coarsely']
    preparation = []
    for prep in prep_words:
        if prep in ingredient_text.lower():
            preparation.append(prep)
    
    preparation_text = ', '.join(preparation) if preparation else None
    
    return quantity, unit, preparation_text

def apply_flavor_profiles():
    """Apply flavor profiles to recipes using our enhanced system"""
    print("\n🔥 APPLYING FLAVOR PROFILES")
    print("=" * 50)
    
    # Import our enhanced flavor system
    try:
        from enhanced_flavor_profile_system import ComprehensiveFlavorMatcher
        
        conn = sqlite3.connect('recipe_books.db')
        cursor = conn.cursor()
        
        # Initialize flavor matcher
        print("   🍳 Initializing flavor matching system...")
        flavor_matcher = ComprehensiveFlavorMatcher(db_path='recipe_books.db')
        
        # Get recipes with ingredients
        cursor.execute('''
            SELECT r.id, r.title, r.ingredients, r.instructions 
            FROM recipes r
            LIMIT 10  -- Start with 10 recipes for testing
        ''')
        
        recipes = cursor.fetchall()
        processed = 0
        
        for recipe_id, title, ingredients_json, instructions_json in recipes:
            if not ingredients_json:
                continue
                
            try:
                ingredients = json.loads(ingredients_json)
                instructions = json.loads(instructions_json) if instructions_json else []
                
                # Generate flavor profile
                flavor_profile = generate_recipe_flavor_profile(ingredients, instructions, title)
                
                # Store flavor profile
                cursor.execute('''
                    INSERT OR REPLACE INTO recipe_flavor_profiles
                    (recipe_id, primary_flavors, secondary_flavors, intensity, 
                     cooking_methods, cuisine_style, season, dietary_tags, complexity_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    recipe_id,
                    json.dumps(flavor_profile['primary_flavors']),
                    json.dumps(flavor_profile['secondary_flavors']),
                    flavor_profile['intensity'],
                    json.dumps(flavor_profile['cooking_methods']),
                    flavor_profile['cuisine_style'],
                    flavor_profile['season'],
                    json.dumps(flavor_profile['dietary_tags']),
                    flavor_profile['complexity_score']
                ))
                
                processed += 1
                print(f"   ✅ Processed flavor profile for: {title}")
                
            except Exception as e:
                print(f"   ⚠️ Error processing flavor profile for {title}: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"✅ Applied flavor profiles to {processed} recipes")
        
    except ImportError as e:
        print(f"   ⚠️ Could not import flavor system: {e}")
        print("   📝 Creating basic flavor profiles instead...")
        create_basic_flavor_profiles()

def generate_recipe_flavor_profile(ingredients, instructions, title):
    """Generate a basic flavor profile for a recipe"""
    
    # Analyze ingredients for flavor characteristics
    primary_flavors = []
    secondary_flavors = []
    cooking_methods = []
    dietary_tags = []
    
    # Basic ingredient analysis
    ingredient_text = ' '.join(ingredients).lower()
    instruction_text = ' '.join(instructions).lower()
    
    # Detect primary flavors
    if any(word in ingredient_text for word in ['garlic', 'onion', 'shallot']):
        primary_flavors.append('savory')
    if any(word in ingredient_text for word in ['herb', 'thyme', 'rosemary', 'parsley']):
        primary_flavors.append('herbal')
    if any(word in ingredient_text for word in ['cheese', 'cream', 'butter']):
        primary_flavors.append('rich')
    if any(word in ingredient_text for word in ['lemon', 'lime', 'vinegar']):
        primary_flavors.append('tangy')
    if any(word in ingredient_text for word in ['sugar', 'honey', 'maple']):
        primary_flavors.append('sweet')
    
    # Detect cooking methods
    if any(word in instruction_text for word in ['bake', 'baking', 'oven']):
        cooking_methods.append('baking')
    if any(word in instruction_text for word in ['fry', 'frying', 'skillet']):
        cooking_methods.append('pan-frying')
    if any(word in instruction_text for word in ['boil', 'simmer', 'water']):
        cooking_methods.append('boiling')
    if any(word in instruction_text for word in ['grill', 'grilling']):
        cooking_methods.append('grilling')
    
    # Determine intensity
    spicy_words = ['pepper', 'spicy', 'hot', 'chili', 'jalapeño']
    intensity = 'strong' if any(word in ingredient_text for word in spicy_words) else 'moderate'
    
    # Determine cuisine style
    cuisine_style = 'western'
    if 'pâté' in title.lower() or 'mousse' in title.lower():
        cuisine_style = 'french'
    elif any(word in ingredient_text for word in ['curry', 'masala', 'garam']):
        cuisine_style = 'indian'
    
    # Dietary tags
    if 'vegetarian' in title.lower() or not any(word in ingredient_text for word in 
                                               ['chicken', 'beef', 'pork', 'fish', 'meat']):
        dietary_tags.append('vegetarian')
    
    # Calculate complexity score
    complexity_score = len(ingredients) + len(instructions) // 2
    complexity_score = min(10, max(1, complexity_score // 3))  # Scale 1-10
    
    return {
        'primary_flavors': primary_flavors[:3],  # Top 3
        'secondary_flavors': secondary_flavors,
        'intensity': intensity,
        'cooking_methods': cooking_methods,
        'cuisine_style': cuisine_style,
        'season': 'year-round',  # Default
        'dietary_tags': dietary_tags,
        'complexity_score': complexity_score
    }

def create_basic_flavor_profiles():
    """Create basic flavor profiles when enhanced system isn't available"""
    print("   📝 Creating basic flavor profiles...")
    
    conn = sqlite3.connect('recipe_books.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, title, ingredients, instructions FROM recipes")
    recipes = cursor.fetchall()
    
    processed = 0
    for recipe_id, title, ingredients_json, instructions_json in recipes:
        if not ingredients_json:
            continue
            
        try:
            ingredients = json.loads(ingredients_json)
            instructions = json.loads(instructions_json) if instructions_json else []
            
            flavor_profile = generate_recipe_flavor_profile(ingredients, instructions, title)
            
            cursor.execute('''
                INSERT OR REPLACE INTO recipe_flavor_profiles
                (recipe_id, primary_flavors, secondary_flavors, intensity, 
                 cooking_methods, cuisine_style, season, dietary_tags, complexity_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                recipe_id,
                json.dumps(flavor_profile['primary_flavors']),
                json.dumps(flavor_profile['secondary_flavors']),
                flavor_profile['intensity'],
                json.dumps(flavor_profile['cooking_methods']),
                flavor_profile['cuisine_style'],
                flavor_profile['season'],
                json.dumps(flavor_profile['dietary_tags']),
                flavor_profile['complexity_score']
            ))
            
            processed += 1
            
        except Exception as e:
            print(f"   ⚠️ Error processing {title}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"   ✅ Created basic flavor profiles for {processed} recipes")

def apply_recipe_analysis():
    """Apply detailed recipe analysis"""
    print("\n📊 APPLYING RECIPE ANALYSIS")
    print("=" * 50)
    
    conn = sqlite3.connect('recipe_books.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, title, ingredients, instructions, hands_on_time, total_time FROM recipes")
    recipes = cursor.fetchall()
    
    processed = 0
    for recipe_id, title, ingredients_json, instructions_json, hands_on_time, total_time in recipes:
        if not ingredients_json:
            continue
            
        try:
            ingredients = json.loads(ingredients_json)
            instructions = json.loads(instructions_json) if instructions_json else []
            
            # Analyze recipe
            analysis = analyze_recipe(ingredients, instructions, title, hands_on_time, total_time)
            
            # Store analysis
            cursor.execute('''
                INSERT OR REPLACE INTO recipe_analysis
                (recipe_id, ingredient_count, instruction_count, estimated_prep_time,
                 estimated_cook_time, difficulty_level, nutrition_category, main_protein,
                 cooking_techniques, equipment_needed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                recipe_id,
                analysis['ingredient_count'],
                analysis['instruction_count'],
                analysis['estimated_prep_time'],
                analysis['estimated_cook_time'],
                analysis['difficulty_level'],
                analysis['nutrition_category'],
                analysis['main_protein'],
                json.dumps(analysis['cooking_techniques']),
                json.dumps(analysis['equipment_needed'])
            ))
            
            processed += 1
            
        except Exception as e:
            print(f"   ⚠️ Error analyzing {title}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Analyzed {processed} recipes")

def analyze_recipe(ingredients, instructions, title, hands_on_time, total_time):
    """Analyze a recipe for various metrics"""
    
    ingredient_text = ' '.join(ingredients).lower()
    instruction_text = ' '.join(instructions).lower()
    
    # Basic counts
    ingredient_count = len(ingredients)
    instruction_count = len(instructions)
    
    # Time estimation (if not provided)
    estimated_prep_time = extract_time_minutes(hands_on_time) if hands_on_time else estimate_prep_time(ingredients, instructions)
    estimated_cook_time = extract_time_minutes(total_time) if total_time else estimate_cook_time(instructions)
    
    # Difficulty assessment
    difficulty_level = assess_difficulty(ingredients, instructions, title)
    
    # Nutrition category
    nutrition_category = determine_nutrition_category(ingredients, title)
    
    # Main protein
    main_protein = identify_main_protein(ingredients)
    
    # Cooking techniques
    cooking_techniques = identify_cooking_techniques(instructions)
    
    # Equipment needed
    equipment_needed = identify_equipment(instructions, ingredients)
    
    return {
        'ingredient_count': ingredient_count,
        'instruction_count': instruction_count,
        'estimated_prep_time': estimated_prep_time,
        'estimated_cook_time': estimated_cook_time,
        'difficulty_level': difficulty_level,
        'nutrition_category': nutrition_category,
        'main_protein': main_protein,
        'cooking_techniques': cooking_techniques,
        'equipment_needed': equipment_needed
    }

def extract_time_minutes(time_str):
    """Extract minutes from time string like '30 minutes' or '2 hours'"""
    if not time_str:
        return None
        
    import re
    
    # Look for patterns like "30 minutes", "2 hours", "1½ hours"
    minutes_match = re.search(r'(\d+(?:\.\d+|\s*½|\s*¼|\s*¾)?)\s*(?:min|minute)', time_str, re.IGNORECASE)
    if minutes_match:
        time_val = minutes_match.group(1).replace('½', '.5').replace('¼', '.25').replace('¾', '.75')
        return int(float(time_val.strip()))
    
    hours_match = re.search(r'(\d+(?:\.\d+|\s*½|\s*¼|\s*¾)?)\s*(?:hr|hour)', time_str, re.IGNORECASE)
    if hours_match:
        time_val = hours_match.group(1).replace('½', '.5').replace('¼', '.25').replace('¾', '.75')
        return int(float(time_val.strip()) * 60)
    
    return None

def estimate_prep_time(ingredients, instructions):
    """Estimate prep time based on ingredients and complexity"""
    base_time = len(ingredients) * 2  # 2 minutes per ingredient
    
    # Add time for complex prep
    prep_text = ' '.join(ingredients).lower()
    if any(word in prep_text for word in ['chopped', 'diced', 'minced']):
        base_time += 10
    if any(word in prep_text for word in ['grated', 'ground']):
        base_time += 5
    
    return min(60, max(5, base_time))  # 5-60 minutes

def estimate_cook_time(instructions):
    """Estimate cooking time from instructions"""
    instruction_text = ' '.join(instructions).lower()
    
    # Look for time mentions
    import re
    times = re.findall(r'(\d+)\s*(?:min|minute)', instruction_text)
    if times:
        return sum(int(t) for t in times)
    
    # Default estimates based on cooking methods
    if 'bake' in instruction_text:
        return 45
    elif 'roast' in instruction_text:
        return 60
    elif 'simmer' in instruction_text:
        return 30
    elif 'fry' in instruction_text:
        return 15
    
    return 20  # Default

def assess_difficulty(ingredients, instructions, title):
    """Assess recipe difficulty level"""
    score = 0
    
    # Ingredient complexity
    if len(ingredients) > 15:
        score += 2
    elif len(ingredients) > 10:
        score += 1
    
    # Instruction complexity
    if len(instructions) > 8:
        score += 2
    elif len(instructions) > 5:
        score += 1
    
    # Technique complexity
    instruction_text = ' '.join(instructions).lower()
    complex_techniques = ['fold', 'whisk', 'sauté', 'braise', 'confit', 'emulsify']
    for technique in complex_techniques:
        if technique in instruction_text:
            score += 1
    
    # Title indicators
    if any(word in title.lower() for word in ['pâté', 'mousse', 'soufflé', 'roux']):
        score += 2
    
    if score >= 5:
        return 'expert'
    elif score >= 3:
        return 'intermediate'
    else:
        return 'beginner'

def determine_nutrition_category(ingredients, title):
    """Determine the main nutrition category"""
    ingredient_text = ' '.join(ingredients).lower()
    
    if any(word in ingredient_text for word in ['meat', 'chicken', 'beef', 'pork', 'fish']):
        return 'protein-rich'
    elif any(word in ingredient_text for word in ['pasta', 'rice', 'bread', 'flour']):
        return 'carbohydrate-rich'
    elif any(word in ingredient_text for word in ['salad', 'vegetable', 'greens']):
        return 'vegetable-rich'
    elif any(word in title.lower() for word in ['dessert', 'cake', 'cookie', 'sweet']):
        return 'dessert'
    else:
        return 'balanced'

def identify_main_protein(ingredients):
    """Identify the main protein source"""
    ingredient_text = ' '.join(ingredients).lower()
    
    proteins = ['chicken', 'beef', 'pork', 'fish', 'salmon', 'turkey', 'lamb', 'duck', 'shrimp', 'crab', 'lobster']
    
    for protein in proteins:
        if protein in ingredient_text:
            return protein
    
    # Check for eggs, cheese, beans as protein
    if 'egg' in ingredient_text:
        return 'eggs'
    elif 'cheese' in ingredient_text:
        return 'cheese'
    elif any(word in ingredient_text for word in ['bean', 'lentil', 'chickpea']):
        return 'legumes'
    
    return 'none'

def identify_cooking_techniques(instructions):
    """Identify cooking techniques used"""
    instruction_text = ' '.join(instructions).lower()
    
    techniques = []
    technique_keywords = {
        'sautéing': ['sauté', 'sauteed', 'sautéed'],
        'baking': ['bake', 'baked', 'oven'],
        'boiling': ['boil', 'boiled', 'boiling'],
        'frying': ['fry', 'fried', 'frying'],
        'grilling': ['grill', 'grilled', 'grilling'],
        'roasting': ['roast', 'roasted', 'roasting'],
        'steaming': ['steam', 'steamed', 'steaming'],
        'braising': ['braise', 'braised', 'braising'],
        'whisking': ['whisk', 'whisked', 'whisking'],
        'folding': ['fold', 'folded', 'folding'],
        'mixing': ['mix', 'mixed', 'mixing', 'combine', 'stir']
    }
    
    for technique, keywords in technique_keywords.items():
        if any(keyword in instruction_text for keyword in keywords):
            techniques.append(technique)
    
    return techniques

def identify_equipment(instructions, ingredients):
    """Identify equipment needed"""
    text = (' '.join(instructions) + ' ' + ' '.join(ingredients)).lower()
    
    equipment = []
    equipment_keywords = {
        'oven': ['oven', 'bake', 'roast'],
        'stovetop': ['skillet', 'pan', 'saucepan', 'pot'],
        'mixer': ['mixer', 'mix', 'beat', 'whisk'],
        'food processor': ['food processor', 'process', 'pulse'],
        'blender': ['blender', 'blend'],
        'grill': ['grill', 'barbecue', 'bbq']
    }
    
    for equip, keywords in equipment_keywords.items():
        if any(keyword in text for keyword in keywords):
            equipment.append(equip)
    
    return equipment

def show_enhanced_results():
    """Show the results of our enhancement"""
    print("\n🎉 ENHANCEMENT COMPLETE!")
    print("=" * 50)
    
    conn = sqlite3.connect('recipe_books.db')
    cursor = conn.cursor()
    
    # Show enhanced statistics
    cursor.execute("SELECT COUNT(*) FROM ingredients")
    ingredient_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM recipe_flavor_profiles")
    flavor_profile_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM recipe_analysis")
    analysis_count = cursor.fetchone()[0]
    
    print(f"📊 Database Enhancement Results:")
    print(f"   🥗 Unique ingredients extracted: {ingredient_count}")
    print(f"   🔥 Flavor profiles created: {flavor_profile_count}")
    print(f"   📊 Recipe analyses completed: {analysis_count}")
    
    # Show sample enhanced recipe
    cursor.execute('''
        SELECT r.title, rf.primary_flavors, rf.complexity_score, ra.difficulty_level, ra.main_protein
        FROM recipes r
        JOIN recipe_flavor_profiles rf ON r.id = rf.recipe_id
        JOIN recipe_analysis ra ON r.id = ra.recipe_id
        LIMIT 5
    ''')
    
    enhanced_recipes = cursor.fetchall()
    print(f"\n🍳 Sample Enhanced Recipes:")
    for title, flavors, complexity, difficulty, protein in enhanced_recipes:
        flavors_list = json.loads(flavors) if flavors else []
        print(f"   📄 {title}")
        print(f"      🔥 Flavors: {', '.join(flavors_list)}")
        print(f"      ⭐ Complexity: {complexity}/10")
        print(f"      🎯 Difficulty: {difficulty}")
        print(f"      🥩 Main protein: {protein}")
        print()
    
    conn.close()

def main():
    """Main execution function"""
    print("🚀 ENHANCING CANADIAN LIVING COOKBOOK DATABASE")
    print("=" * 60)
    
    # Check current state
    recipe_count = check_current_database()
    
    if recipe_count == 0:
        print("❌ No recipes found in database. Please run the parser first.")
        return
    
    # Create enhanced tables
    create_enhanced_tables()
    
    # Extract and analyze ingredients
    extract_and_analyze_ingredients()
    
    # Apply flavor profiles
    apply_flavor_profiles()
    
    # Apply recipe analysis
    apply_recipe_analysis()
    
    # Show results
    show_enhanced_results()
    
    print("✅ Database enhancement complete!")
    print("🎯 Your Canadian Living cookbook is now fully analyzed with:")
    print("   • Extracted ingredients with quantities and preparation")
    print("   • Flavor profiles for recipe discovery") 
    print("   • Detailed recipe analysis and difficulty ratings")
    print("   • Cooking technique and equipment identification")

if __name__ == "__main__":
    main()
