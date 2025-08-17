#!/usr/bin/env python3
"""
Fixed intelligence migration that processes ALL 728 recipes
Direct PostgreSQL approach to bypass any application limitations
"""
import psycopg2
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_full_intelligence_migration():
    database_url = "postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway"
    
    print("🚀 FULL INTELLIGENCE MIGRATION - ALL 728 RECIPES")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        print("✅ Connected to PostgreSQL database")
        
        # Get ALL recipes that don't have intelligence data yet
        cursor.execute("""
            SELECT id, title, description, total_time, servings, ingredients 
            FROM recipes 
            WHERE meal_role IS NULL 
            ORDER BY id
        """)
        unprocessed_recipes = cursor.fetchall()
        
        print(f"📊 Found {len(unprocessed_recipes)} recipes without intelligence data")
        
        if len(unprocessed_recipes) == 0:
            print("🎉 All recipes already have intelligence data!")
            return
        
        updated_count = 0
        
        for recipe in unprocessed_recipes:
            try:
                recipe_id = recipe[0]
                title = recipe[1] or ''
                description = recipe[2] or ''
                total_time = recipe[3] or ''
                servings = recipe[4] or 0
                ingredients = recipe[5] or ''
                
                # Progress logging every 50 recipes
                if updated_count % 50 == 0:
                    print(f"🔄 Processing recipe {updated_count + 1}/{len(unprocessed_recipes)}: ID {recipe_id}")
                
                # Simple meal role classification
                text = f"{title} {description}".lower()
                meal_role = "dinner"  # Default
                confidence = 50
                
                if any(word in text for word in ['breakfast', 'pancake', 'oatmeal', 'morning', 'cereal']):
                    meal_role = "breakfast"
                    confidence = 80
                elif any(word in text for word in ['dessert', 'cake', 'cookie', 'sweet', 'chocolate', 'pie']):
                    meal_role = "dessert"
                    confidence = 90
                elif any(word in text for word in ['sauce', 'dressing', 'marinade', 'dip']):
                    meal_role = "sauce"
                    confidence = 85
                elif any(word in text for word in ['lunch', 'sandwich', 'salad', 'soup']):
                    meal_role = "lunch"
                    confidence = 75
                
                # Time estimation
                time_min = 30  # Default
                if total_time:
                    # Extract numbers from total_time string
                    import re
                    time_match = re.search(r'(\d+)', str(total_time))
                    if time_match:
                        time_min = int(time_match.group(1))
                
                # Complexity analysis
                steps_count = 5  # Default
                if ingredients:
                    # Estimate based on ingredient count
                    ingredient_list = str(ingredients).split(',')
                    steps_count = min(len(ingredient_list), 10)
                
                # Binary classifications
                is_easy = (time_min <= 30 and steps_count <= 5)
                is_one_pot = any(word in text for word in ['one pot', 'skillet', 'pan'])
                
                # Safe servings conversion for leftover_friendly
                try:
                    servings_int = int(servings) if servings else 2
                except (ValueError, TypeError):
                    servings_int = 2
                    
                leftover_friendly = meal_role in ['dinner', 'lunch'] and servings_int > 2
                kid_friendly = any(word in text for word in ['kid', 'child', 'family', 'simple'])
                
                # Update recipe with intelligence data
                cursor.execute("""
                    UPDATE recipes SET
                        meal_role = %s,
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
                    meal_role, confidence, time_min, steps_count, 1,
                    is_easy, is_one_pot, leftover_friendly, kid_friendly,
                    recipe_id
                ))
                
                updated_count += 1
                
            except Exception as e:
                logger.error(f"Error processing recipe {recipe_id}: {e}")
                continue
        
        # Commit all changes
        conn.commit()
        print(f"✅ Committed {updated_count} recipe updates to database")
        
        # Final verification
        cursor.execute("SELECT COUNT(*) FROM recipes WHERE meal_role IS NOT NULL")
        total_classified = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM recipes")
        total_recipes = cursor.fetchone()[0]
        
        print(f"\n🎯 FINAL RESULTS:")
        print(f"   📊 Total recipes in database: {total_recipes}")
        print(f"   🧠 Recipes with intelligence: {total_classified}")
        print(f"   🎯 Completion rate: {(total_classified/total_recipes)*100:.1f}%")
        
        if total_classified == total_recipes:
            print(f"\n🎉 PERFECT SUCCESS! All {total_recipes} recipes now have intelligence data!")
        
        conn.close()
        
    except Exception as e:
        logger.error(f"❌ Migration error: {e}")

if __name__ == "__main__":
    run_full_intelligence_migration()
