import sqlite3

conn = sqlite3.connect('hungie.db')
cursor = conn.cursor()

# Count Bon Appetit recipes
cursor.execute('SELECT COUNT(*) FROM recipes WHERE url LIKE "%bonappetit.com%"')
total_ba = cursor.fetchone()[0]

# Count how many have analysis data
cursor.execute('''
    SELECT COUNT(*) FROM recipe_analysis 
    WHERE recipe_id IN (SELECT id FROM recipes WHERE url LIKE "%bonappetit.com%")
''')
analysis_count = cursor.fetchone()[0]

# Count how many have flavor profiles
cursor.execute('''
    SELECT COUNT(*) FROM recipe_flavor_profiles 
    WHERE recipe_id IN (SELECT id FROM recipes WHERE url LIKE "%bonappetit.com%")
''')
flavor_count = cursor.fetchone()[0]

print(f"📊 BON APPETIT RECIPE ANALYSIS STATUS")
print(f"=====================================")
print(f"Total Bon Appétit recipes: {total_ba}")
print(f"With analysis data: {analysis_count}")
print(f"With flavor profiles: {flavor_count}")

# Check specifically for our newly imported recipe
cursor.execute('''
    SELECT ra.difficulty_level, ra.cuisine_type, ra.main_protein, ra.technique_complexity
    FROM recipe_analysis ra
    JOIN recipes r ON ra.recipe_id = r.id
    WHERE r.title = "Overnight Oats"
''')
overnight_oats_analysis = cursor.fetchone()

if overnight_oats_analysis:
    print(f"\n✅ Sample: 'Overnight Oats' HAS analysis data:")
    print(f"  Difficulty: {overnight_oats_analysis[0]}")
    print(f"  Cuisine: {overnight_oats_analysis[1]}")
    print(f"  Main protein: {overnight_oats_analysis[2]}")
    print(f"  Complexity: {overnight_oats_analysis[3]}")
else:
    print(f"\n❌ Sample: 'Overnight Oats' has NO analysis data")

# Check flavor profile for the same recipe
cursor.execute('''
    SELECT fp.primary_flavors, fp.intensity, fp.cuisine_style, fp.complexity_score
    FROM recipe_flavor_profiles fp
    JOIN recipes r ON fp.recipe_id = r.id
    WHERE r.title = "Overnight Oats"
''')
overnight_oats_flavor = cursor.fetchone()

if overnight_oats_flavor:
    print(f"\n✅ Sample: 'Overnight Oats' HAS flavor profile:")
    print(f"  Primary flavors: {overnight_oats_flavor[0]}")
    print(f"  Intensity: {overnight_oats_flavor[1]}")
    print(f"  Cuisine style: {overnight_oats_flavor[2]}")
    print(f"  Complexity score: {overnight_oats_flavor[3]}")
else:
    print(f"\n❌ Sample: 'Overnight Oats' has NO flavor profile")

conn.close()
