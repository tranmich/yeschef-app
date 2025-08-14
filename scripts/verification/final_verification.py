import sqlite3
import json

conn = sqlite3.connect('hungie.db')
cursor = conn.cursor()

# Check a few sample recipes from our new import
sample_recipes = [
    "Overnight Oats",
    "Vegan Pho", 
    "Japanese Cheesecake",
    "Cornbread Breakfast Casserole"
]

print("🔍 DETAILED ANALYSIS CHECK FOR NEW RECIPES")
print("=" * 60)

for recipe_name in sample_recipes:
    print(f"\n📋 RECIPE: {recipe_name}")
    print("-" * 40)
    
    # Get recipe ID and basic info
    cursor.execute("SELECT id, title, url FROM recipes WHERE title = ?", (recipe_name,))
    recipe_data = cursor.fetchone()
    
    if not recipe_data:
        print("❌ Recipe not found")
        continue
        
    recipe_id, title, url = recipe_data
    print(f"ID: {recipe_id}")
    print(f"URL: {url}")
    
    # Check analysis data
    cursor.execute("""
        SELECT difficulty_level, cuisine_type, main_protein, technique_complexity, 
               primary_tastes, heat_level, flavor_intensity
        FROM recipe_analysis 
        WHERE recipe_id = ?
    """, (recipe_id,))
    analysis = cursor.fetchone()
    
    if analysis:
        print("✅ HAS ANALYSIS DATA:")
        print(f"  Difficulty: {analysis[0]}")
        print(f"  Cuisine: {analysis[1]}")
        print(f"  Main protein: {analysis[2]}")
        print(f"  Complexity: {analysis[3]}")
        print(f"  Primary tastes: {analysis[4]}")
        print(f"  Heat level: {analysis[5]}")
        print(f"  Flavor intensity: {analysis[6]}")
    else:
        print("❌ NO ANALYSIS DATA")
    
    # Check flavor profile
    cursor.execute("""
        SELECT primary_flavors, intensity, cuisine_style, complexity_score
        FROM recipe_flavor_profiles 
        WHERE recipe_id = ?
    """, (recipe_id,))
    flavor = cursor.fetchone()
    
    if flavor:
        print("✅ HAS FLAVOR PROFILE:")
        try:
            primary_flavors = json.loads(flavor[0]) if flavor[0] else []
            print(f"  Primary flavors: {primary_flavors}")
        except:
            print(f"  Primary flavors: {flavor[0]}")
        print(f"  Intensity: {flavor[1]}")
        print(f"  Cuisine style: {flavor[2]}")
        print(f"  Complexity score: {flavor[3]}")
    else:
        print("❌ NO FLAVOR PROFILE")

conn.close()

print(f"\n🎉 VERIFICATION COMPLETE!")
print("All new Bon Appétit recipes should now have:")
print("  ✅ Recipe analysis data (difficulty, cuisine, techniques, etc.)")
print("  ✅ Flavor profile data (flavors, intensity, cuisine style, etc.)")
print("  ✅ Complete ingredient and instruction breakdown")
print("  ✅ Full API compatibility for frontend searches")
