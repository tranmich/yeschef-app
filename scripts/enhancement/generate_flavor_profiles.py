import sqlite3
import json
from flavor_profile_system import FlavorProfileMatcher, enhance_recipe_analysis_with_flavor_profile

def generate_missing_flavor_profiles():
    """Generate flavor profiles for recipes that don't have them yet"""
    print("🎨 GENERATING MISSING FLAVOR PROFILES")
    print("=" * 50)
    
    # Initialize the flavor matcher
    print("🔄 Initializing FlavorProfile System...")
    try:
        matcher = FlavorProfileMatcher()
        print("✅ FlavorProfile System initialized")
    except Exception as e:
        print(f"❌ Error initializing FlavorProfile System: {e}")
        return
    
    # Connect to database
    conn = sqlite3.connect('hungie.db')
    cursor = conn.cursor()
    
    # Find recipes without flavor profiles
    cursor.execute("""
        SELECT r.id, r.title 
        FROM recipes r 
        LEFT JOIN recipe_flavor_profiles fp ON r.id = fp.recipe_id 
        WHERE fp.recipe_id IS NULL
        AND r.url LIKE '%bonappetit.com%'
    """)
    missing_recipes = cursor.fetchall()
    
    print(f"📊 Found {len(missing_recipes)} Bon Appétit recipes without flavor profiles")
    
    processed = 0
    for recipe_id, title in missing_recipes:
        try:
            # Get recipe data
            cursor.execute("""
                SELECT r.ingredients, r.instructions, r.title, r.description
                FROM recipes r 
                WHERE r.id = ?
            """, (recipe_id,))
            recipe_row = cursor.fetchone()
            
            if not recipe_row:
                continue
                
            ingredients_json, instructions_json, title, description = recipe_row
            
            # Parse JSON ingredients and instructions
            try:
                ingredients = json.loads(ingredients_json) if ingredients_json else []
                instructions = json.loads(instructions_json) if instructions_json else []
            except json.JSONDecodeError:
                # If not JSON, treat as plain text
                ingredients = [ingredients_json] if ingredients_json else []
                instructions = [instructions_json] if instructions_json else []
            
            # Create recipe data structure for analysis
            recipe_data = {
                'title': title,
                'ingredients': ingredients,
                'instructions': instructions,
                'description': description or ''
            }
            
            # Generate flavor profile analysis
            flavor_analysis = enhance_recipe_analysis_with_flavor_profile(recipe_data, matcher)
            
            # Extract flavor profile data
            flavor_harmony = flavor_analysis.get('flavor_harmony', {})
            harmony_score = flavor_harmony.get('harmony_score', 0.5)
            
            # Determine primary and secondary flavors from ingredients
            primary_flavors = []
            secondary_flavors = []
            
            # Simple flavor extraction based on common ingredients
            flavor_keywords = {
                'sweet': ['sugar', 'honey', 'maple', 'chocolate', 'vanilla', 'fruit', 'berry'],
                'savory': ['salt', 'cheese', 'meat', 'herbs', 'garlic', 'onion'],
                'spicy': ['pepper', 'chili', 'hot', 'spice', 'jalapeño'],
                'tangy': ['lemon', 'lime', 'vinegar', 'tomato', 'citrus'],
                'rich': ['butter', 'cream', 'oil', 'nuts', 'avocado']
            }
            
            for ingredient in ingredients:
                ingredient_lower = ingredient.lower()
                for flavor, keywords in flavor_keywords.items():
                    if any(keyword in ingredient_lower for keyword in keywords):
                        if flavor not in primary_flavors:
                            primary_flavors.append(flavor)
                        break
            
            # Default values if no flavors detected
            if not primary_flavors:
                primary_flavors = ['savory']
            
            # Determine intensity based on ingredient count and cooking methods
            instruction_text = ' '.join(instructions).lower()
            intensity = 'moderate'
            if any(word in instruction_text for word in ['roast', 'grill', 'fry', 'sear']):
                intensity = 'bold'
            elif any(word in instruction_text for word in ['steam', 'poach', 'simmer']):
                intensity = 'mild'
            
            # Determine cuisine style from recipe title and ingredients
            cuisine_style = 'american'
            title_lower = title.lower()
            if any(word in title_lower for word in ['pasta', 'italian', 'parmesan']):
                cuisine_style = 'italian'
            elif any(word in title_lower for word in ['curry', 'garam', 'masala']):
                cuisine_style = 'indian'
            elif any(word in title_lower for word in ['taco', 'mexican', 'jalapeño']):
                cuisine_style = 'mexican'
            elif any(word in title_lower for word in ['french', 'bourguignon', 'ratatouille']):
                cuisine_style = 'french'
            
            # Insert flavor profile
            cursor.execute("""
                INSERT OR REPLACE INTO recipe_flavor_profiles (
                    recipe_id, primary_flavors, secondary_flavors, intensity, 
                    cooking_methods, cuisine_style, season, dietary_tags, 
                    complexity_score, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                recipe_id,
                json.dumps(primary_flavors),
                json.dumps(secondary_flavors),
                intensity,
                json.dumps([]),  # cooking_methods
                cuisine_style,
                'all-season',  # season
                json.dumps([]),  # dietary_tags
                max(1, min(10, int(harmony_score * 10)))  # complexity_score (1-10)
            ))
            
            processed += 1
            if processed % 20 == 0:
                print(f"  ✓ Processed {processed}/{len(missing_recipes)} recipes...")
                
        except Exception as e:
            print(f"  ❌ Error processing {title}: {e}")
            continue
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print(f"\n✅ Flavor profile generation complete!")
    print(f"   Generated: {processed}/{len(missing_recipes)} profiles")

if __name__ == "__main__":
    generate_missing_flavor_profiles()
