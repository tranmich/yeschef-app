import sqlite3
import json

def analyze_database():
    print("🔍 DATABASE ANALYSIS")
    print("=" * 40)
    
    try:
        conn = sqlite3.connect('hungie.db')
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"📊 Tables: {tables}")
        
        # Check recipe count
        cursor.execute('SELECT COUNT(*) FROM recipes')
        total_recipes = cursor.fetchone()[0]
        print(f"🍽️ Total recipes: {total_recipes}")
        
        # Check ingredient data
        cursor.execute('SELECT COUNT(*) FROM ingredients')
        total_ingredients = cursor.fetchone()[0]
        print(f"🥗 Total ingredients: {total_ingredients}")
        
        cursor.execute('SELECT COUNT(*) FROM recipe_ingredients')
        ingredient_links = cursor.fetchone()[0]
        print(f"🔗 Recipe-ingredient links: {ingredient_links}")
        
        # Check FlavorProfile data
        cursor.execute('SELECT COUNT(*) FROM recipe_flavor_profiles')
        enhanced_recipes = cursor.fetchone()[0]
        print(f"🔥 Enhanced recipes: {enhanced_recipes}")
        
        # Sample recipes
        cursor.execute('SELECT name, url FROM recipes WHERE url LIKE "%bonappetit%" LIMIT 5')
        ba_recipes = cursor.fetchall()
        print(f"\\n📋 Sample Bon Appétit recipes ({len(ba_recipes)}):")
        for name, url in ba_recipes:
            print(f"  - {name[:60]}...")
        
        # Check if recipes have ingredients
        cursor.execute('''
            SELECT r.name, COUNT(ri.ingredient_id) as ingredient_count
            FROM recipes r
            LEFT JOIN recipe_ingredients ri ON r.id = ri.recipe_id
            GROUP BY r.id
            HAVING ingredient_count = 0
            LIMIT 5
        ''')
        
        empty_recipes = cursor.fetchall()
        print(f"\\n❌ Recipes without ingredients ({len(empty_recipes)} shown):")
        for name, count in empty_recipes:
            print(f"  - {name[:60]}... ({count} ingredients)")
        
        # Check recipes WITH ingredients
        cursor.execute('''
            SELECT r.name, COUNT(ri.ingredient_id) as ingredient_count
            FROM recipes r
            LEFT JOIN recipe_ingredients ri ON r.id = ri.recipe_id
            GROUP BY r.id
            HAVING ingredient_count > 0
            LIMIT 5
        ''')
        
        good_recipes = cursor.fetchall()
        print(f"\\n✅ Recipes with ingredients ({len(good_recipes)} shown):")
        for name, count in good_recipes:
            print(f"  - {name[:60]}... ({count} ingredients)")
        
        # Overall stats
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN ingredient_count = 0 THEN 1 END) as empty,
                COUNT(CASE WHEN ingredient_count > 0 THEN 1 END) as with_ingredients
            FROM (
                SELECT r.id, COUNT(ri.ingredient_id) as ingredient_count
                FROM recipes r
                LEFT JOIN recipe_ingredients ri ON r.id = ri.recipe_id
                GROUP BY r.id
            )
        ''')
        
        empty_count, good_count = cursor.fetchone()
        print(f"\\n📊 SUMMARY:")
        print(f"  💔 Recipes without ingredients: {empty_count}")
        print(f"  ✅ Recipes with ingredients: {good_count}")
        print(f"  📈 Percentage with ingredients: {(good_count/total_recipes)*100:.1f}%")
        
        conn.close()
        
        # Recommendation
        print(f"\\n🎯 RECOMMENDATION:")
        if good_count < total_recipes * 0.5:
            print("  🚨 MAJORITY of recipes lack ingredients - START FRESH")
            print("  ✨ Build new database with proper ingredient extraction")
        else:
            print("  🔧 FIX existing database by re-importing with fixed scraper")
            print("  💡 Most recipes are salvageable")
            
    except Exception as e:
        print(f"❌ Database analysis failed: {e}")

if __name__ == "__main__":
    analyze_database()
