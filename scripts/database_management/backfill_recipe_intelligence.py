#!/usr/bin/env python3
"""
Recipe Intelligence Backfill Script
Processes existing 750 recipes to add intelligence fields based on research-driven scoring
Implements the 15-point "Easy" scoring system and meal role classification from DATA_ENHANCEMENT_GUIDE.md

Usage:
    python backfill_recipe_intelligence.py

Created: August 17, 2025
"""

import psycopg2
import psycopg2.extras
import os
import re
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_database_connection():
    """Get PostgreSQL database connection"""
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL environment variable not set!")
            print("💡 Run with: railway run python backfill_recipe_intelligence.py")
            return None
        
        conn = psycopg2.connect(database_url)
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        print("✅ Connected to PostgreSQL database")
        return conn
        
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return None

def parse_time_minutes(time_str):
    """Parse time string to minutes"""
    if not time_str:
        return None
    
    time_str = time_str.lower().strip()
    minutes = 0
    
    # Extract hours and minutes
    hour_match = re.search(r'(\d+)\s*h', time_str)
    minute_match = re.search(r'(\d+)\s*m', time_str)
    
    if hour_match:
        minutes += int(hour_match.group(1)) * 60
    if minute_match:
        minutes += int(minute_match.group(1))
    
    # If no specific format, try to extract just numbers
    if minutes == 0:
        number_match = re.search(r'(\d+)', time_str)
        if number_match:
            num = int(number_match.group(1))
            # Assume minutes if under 10, hours if over
            minutes = num if num > 10 else num * 60
    
    return minutes if minutes > 0 else None

def count_steps(instructions):
    """Count preparation steps in instructions"""
    if not instructions:
        return 0
    
    # Split by common step indicators
    steps = re.split(r'[.\n]\s*\d+[.\)\s]|Step \d+|^\d+[.\)\s]', instructions, flags=re.MULTILINE)
    # Filter out empty steps
    steps = [step.strip() for step in steps if step.strip() and len(step.strip()) > 10]
    
    return len(steps)

def analyze_equipment_complexity(instructions, ingredients):
    """Analyze equipment complexity for one-pot detection"""
    if not instructions:
        return 1
    
    text = f"{instructions} {ingredients}".lower()
    
    # Equipment indicators
    equipment_words = [
        'pan', 'pot', 'skillet', 'saucepan', 'stockpot', 'dutch oven',
        'baking sheet', 'casserole dish', 'bowl', 'oven', 'stovetop'
    ]
    
    equipment_count = 0
    for equipment in equipment_words:
        if equipment in text:
            equipment_count += 1
    
    # Cap at reasonable number
    return min(equipment_count, 5) if equipment_count > 0 else 1

def classify_meal_role(title, description, time_min=None, servings=None):
    """Auto-classify meal role based on recipe content"""
    
    MEAL_KEYWORDS = {
        "breakfast": ["breakfast", "pancake", "oatmeal", "omelet", "omelette", "frittata",
                     "hash browns", "granola", "french toast", "waffle", "porridge",
                     "smoothie bowl", "bagel", "scramble", "overnight oats"],
        
        "lunch": ["sandwich", "wrap", "panini", "grain bowl", "bento", "poke bowl",
                 "lunch", "no-cook", "meal prep bowl", "salad"],
        
        "dinner": ["dinner", "stew", "roast", "curry", "bake", "casserole", "sheet-pan",
                  "braise", "pot roast", "pasta bake", "one-pot pasta", "main course"],
        
        "snack": ["snack", "energy balls", "trail mix", "dip", "hummus", "quesadilla",
                 "toast", "popcorn", "chips", "nuts mix", "appetizer"],
        
        "dessert": ["dessert", "cake", "cookie", "brownie", "pie", "tart", "ice cream",
                   "pudding", "custard", "cheesecake", "frosting", "sorbet", "crumble", "mousse"],
        
        "side": ["side", "side salad", "coleslaw", "garlic bread", "roasted vegetables",
                "mashed potatoes", "fries", "cornbread", "rice pilaf", "steamed"],
        
        "sauce": ["sauce", "dressing", "pesto", "chimichurri", "aioli", "tahini sauce",
                 "vinaigrette", "gravy", "marinade", "syrup", "condiment"],
        
        "drink": ["smoothie", "latte", "juice", "shake", "cocktail", "mocktail",
                 "lemonade", "tea", "coffee", "spritzer", "beverage"]
    }
    
    text = f"{title} {description or ''}".lower()
    scores = {role: 0 for role in MEAL_KEYWORDS.keys()}
    
    # Keyword scoring
    for role, keywords in MEAL_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                # High confidence for specialized categories
                if role in ["dessert", "sauce", "drink"]:
                    scores[role] += 60
                # Medium confidence for time-specific meals
                elif role in ["breakfast", "snack"]:
                    scores[role] += 40
                # Standard confidence for main meals
                else:
                    scores[role] += 30
    
    # Time-based hints
    if time_min:
        if time_min <= 20:
            scores["breakfast"] += 15
            scores["lunch"] += 10
            scores["snack"] += 10
        elif time_min >= 45:
            scores["dinner"] += 10
    
    # Serving size hints
    if servings:
        try:
            serving_num = int(re.search(r'\d+', str(servings)).group())
            if serving_num >= 4:
                scores["dinner"] += 10
        except:
            pass
    
    # Special case logic
    if "side" in text or ("salad" in text and "chicken" not in text and "main" not in text):
        scores["side"] += 25
    
    # Determine winner
    top_role = max(scores, key=scores.get)
    confidence = min(100, scores[top_role])
    
    # Create candidates list
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    candidates = [f"{role}:{score}" for role, score in sorted_scores[:3] if score > 0]
    
    # Tiebreaker logic for high-confidence categories
    if len(sorted_scores) > 1 and sorted_scores[0][1] - sorted_scores[1][1] <= 10:
        if scores["dessert"] >= 60:
            top_role = "dessert"
        elif scores["sauce"] >= 60:
            top_role = "sauce"
        elif scores["drink"] >= 60:
            top_role = "drink"
        elif scores["dinner"] >= 30:
            top_role = "dinner"
    
    # Default to dinner if no clear winner
    if confidence < 20:
        top_role = "dinner"
        confidence = 25
    
    return top_role, confidence, candidates

def calculate_easy_score(time_min, steps_count, ingredient_count, equipment_count, instructions):
    """Calculate 15-point easy score as defined in DATA_ENHANCEMENT_GUIDE.md"""
    
    score = 0
    
    # Time scoring (0-3 points)
    if time_min:
        if time_min <= 20:
            score += 3
        elif time_min <= 30:
            score += 2
        elif time_min <= 45:
            score += 1
    
    # Steps scoring (0-3 points)
    if steps_count <= 5:
        score += 3
    elif steps_count <= 7:
        score += 2
    elif steps_count <= 10:
        score += 1
    
    # Ingredients scoring (0-3 points) - need to count from ingredients text
    if ingredient_count <= 7:
        score += 3
    elif ingredient_count <= 10:
        score += 2
    elif ingredient_count <= 14:
        score += 1
    
    # Equipment scoring (0-3 points)
    if equipment_count == 1:
        score += 3
    elif equipment_count == 2:
        score += 2
    elif equipment_count == 3:
        score += 1
    
    # Technique scoring (0-3 points) - analyze instructions for complexity
    if instructions:
        text = instructions.lower()
        advanced_techniques = ['tempering', 'emulsify', 'julienne', 'brunoise', 'confit', 'sous vide']
        basic_techniques = ['chop', 'dice', 'slice', 'mix', 'stir', 'bake', 'boil', 'fry']
        
        has_advanced = any(technique in text for technique in advanced_techniques)
        has_basic = any(technique in text for technique in basic_techniques)
        
        if has_advanced:
            score += 0  # Advanced techniques = 0 points
        elif has_basic and not has_advanced:
            score += 3  # Basic only = 3 points
        else:
            score += 1  # Mixed or unclear = 1 point
    
    return score

def count_ingredients(ingredients_text):
    """Count ingredients from ingredients text"""
    if not ingredients_text:
        return 0
    
    # Split by common separators and count non-empty items
    ingredients = re.split(r'[,\n•\-\*]', ingredients_text)
    ingredients = [ing.strip() for ing in ingredients if ing.strip()]
    
    return len(ingredients)

def analyze_leftover_friendly(title, description, instructions, servings):
    """Analyze if recipe is leftover-friendly"""
    
    text = f"{title} {description or ''} {instructions or ''}".lower()
    
    # Positive indicators
    leftover_positive = [
        'stew', 'soup', 'casserole', 'curry', 'chili', 'pasta bake',
        'lasagna', 'pot roast', 'braised', 'slow cook', 'one pot'
    ]
    
    # Negative indicators (doesn't reheat well)
    leftover_negative = [
        'fried', 'crispy', 'crunchy', 'fresh salad', 'sushi', 'tempura'
    ]
    
    positive_score = sum(1 for keyword in leftover_positive if keyword in text)
    negative_score = sum(1 for keyword in leftover_negative if keyword in text)
    
    # Check servings
    serving_bonus = 0
    if servings:
        try:
            serving_num = int(re.search(r'\d+', str(servings)).group())
            if serving_num >= 4:
                serving_bonus = 1
        except:
            pass
    
    return (positive_score + serving_bonus) > negative_score

def analyze_kid_friendly(title, description, ingredients):
    """Analyze if recipe is kid-friendly"""
    
    text = f"{title} {description or ''} {ingredients or ''}".lower()
    
    # Kid-friendly indicators
    kid_positive = [
        'chicken nuggets', 'mac and cheese', 'pizza', 'pasta', 'meatballs',
        'grilled cheese', 'pancakes', 'muffins', 'smoothie', 'mild'
    ]
    
    # Kid-unfriendly indicators
    kid_negative = [
        'spicy', 'hot sauce', 'chili pepper', 'jalapeño', 'wasabi',
        'blue cheese', 'anchovies', 'liver', 'very hot'
    ]
    
    positive_score = sum(1 for keyword in kid_positive if keyword in text)
    negative_score = sum(1 for keyword in kid_negative if keyword in text)
    
    return positive_score > negative_score

def backfill_recipe_intelligence():
    """Main backfill function - process all existing recipes"""
    
    print("🧠 RECIPE INTELLIGENCE BACKFILL SCRIPT")
    print("=" * 60)
    print("📅 Started:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    
    # Connect to database
    conn = get_database_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # First, run the migration to add columns
        print("🔧 Adding intelligence columns to recipes table...")
        migration_sql = """
        -- Add intelligence fields to existing recipes table
        ALTER TABLE recipes 
        ADD COLUMN IF NOT EXISTS meal_role TEXT,
        ADD COLUMN IF NOT EXISTS meal_role_confidence INTEGER DEFAULT 0,
        ADD COLUMN IF NOT EXISTS time_min INTEGER,
        ADD COLUMN IF NOT EXISTS steps_count INTEGER,
        ADD COLUMN IF NOT EXISTS pots_pans_count INTEGER DEFAULT 1,
        ADD COLUMN IF NOT EXISTS is_easy BOOLEAN DEFAULT FALSE,
        ADD COLUMN IF NOT EXISTS is_one_pot BOOLEAN DEFAULT FALSE,
        ADD COLUMN IF NOT EXISTS leftover_friendly BOOLEAN DEFAULT FALSE,
        ADD COLUMN IF NOT EXISTS kid_friendly BOOLEAN DEFAULT FALSE;

        -- Performance index for intelligent filtering
        CREATE INDEX IF NOT EXISTS idx_recipes_intelligence 
        ON recipes(meal_role, is_easy, is_one_pot, time_min);

        -- Index for pantry-first searches (future enhancement)
        CREATE INDEX IF NOT EXISTS idx_recipes_time_difficulty 
        ON recipes(time_min, is_easy) WHERE time_min IS NOT NULL;
        """
        cursor.execute(migration_sql)
        conn.commit()
        print("✅ Migration completed successfully")
        print()
        
        # Get all recipes
        cursor.execute("SELECT * FROM recipes ORDER BY id")
        recipes = cursor.fetchall()
        
        print(f"📊 Processing {len(recipes)} recipes...")
        print()
        
        processed_count = 0
        updated_count = 0
        
        for recipe in recipes:
            try:
                # Extract recipe data
                recipe_id = recipe['id']
                title = recipe.get('title', '')
                description = recipe.get('description', '')
                ingredients = recipe.get('ingredients', '')
                instructions = recipe.get('instructions', '')
                total_time = recipe.get('total_time', '')
                servings = recipe.get('servings', '')
                
                # Parse and analyze
                time_min = parse_time_minutes(total_time)
                steps_count = count_steps(instructions)
                ingredient_count = count_ingredients(ingredients)
                equipment_count = analyze_equipment_complexity(instructions, ingredients)
                
                # Classify meal role
                meal_role, meal_role_confidence, candidates = classify_meal_role(
                    title, description, time_min, servings
                )
                
                # Calculate easy score
                easy_score = calculate_easy_score(
                    time_min, steps_count, ingredient_count, equipment_count, instructions
                )
                is_easy = easy_score >= 10
                
                # One-pot detection
                is_one_pot = equipment_count <= 1
                
                # Other flags
                leftover_friendly = analyze_leftover_friendly(title, description, instructions, servings)
                kid_friendly = analyze_kid_friendly(title, description, ingredients)
                
                # Update database
                cursor.execute("""
                    UPDATE recipes 
                    SET meal_role = %s, 
                        meal_role_confidence = %s,
                        time_min = %s, 
                        steps_count = %s, 
                        pots_pans_count = %s,
                        is_easy = %s, 
                        is_one_pot = %s, 
                        leftover_friendly = %s,
                        kid_friendly = %s
                    WHERE id = %s
                """, (
                    meal_role, meal_role_confidence, time_min, steps_count, equipment_count,
                    is_easy, is_one_pot, leftover_friendly, kid_friendly, recipe_id
                ))
                
                updated_count += 1
                
                # Progress indicator
                if processed_count % 50 == 0:
                    print(f"   📈 Processed {processed_count}/{len(recipes)} recipes...")
                
                processed_count += 1
                
            except Exception as e:
                print(f"   ⚠️ Error processing recipe {recipe.get('id', 'unknown')}: {e}")
                continue
        
        # Commit all changes
        conn.commit()
        
        print()
        print("🎉 BACKFILL COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"📊 Total recipes processed: {processed_count}")
        print(f"✅ Successfully updated: {updated_count}")
        print(f"📅 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show some statistics
        cursor.execute("""
            SELECT 
                meal_role,
                COUNT(*) as count,
                AVG(meal_role_confidence) as avg_confidence
            FROM recipes 
            WHERE meal_role IS NOT NULL
            GROUP BY meal_role 
            ORDER BY count DESC
        """)
        
        meal_stats = cursor.fetchall()
        
        print()
        print("📈 MEAL ROLE STATISTICS:")
        for stat in meal_stats:
            print(f"   {stat['meal_role']}: {stat['count']} recipes (avg confidence: {stat['avg_confidence']:.1f}%)")
        
        # Easy recipe statistics
        cursor.execute("SELECT COUNT(*) FROM recipes WHERE is_easy = true")
        easy_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM recipes WHERE is_one_pot = true")
        one_pot_count = cursor.fetchone()[0]
        
        print()
        print("🎯 RECIPE INTELLIGENCE STATISTICS:")
        print(f"   ⚡ Easy recipes: {easy_count}")
        print(f"   🍲 One-pot recipes: {one_pot_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Backfill error: {e}")
        conn.rollback()
        return False
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    success = backfill_recipe_intelligence()
    if success:
        print("\n🚀 Ready for next phase: Enhanced recipe suggestions!")
    else:
        print("\n❌ Backfill failed - check errors above")
    
    sys.exit(0 if success else 1)
