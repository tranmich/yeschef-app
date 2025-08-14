import sqlite3

conn = sqlite3.connect('hungie.db')
cursor = conn.cursor()

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]

print("ALL TABLES IN DATABASE:")
for table in sorted(tables):
    print(f"  - {table}")

# Check if there are any flavor/analysis related tables
analysis_tables = [t for t in tables if any(keyword in t.lower() for keyword in ['flavor', 'analysis', 'profile', 'enhanced'])]
print(f"\nANALYSIS/FLAVOR RELATED TABLES:")
if analysis_tables:
    for table in analysis_tables:
        print(f"  - {table}")
        # Show table structure
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        for col in columns:
            print(f"    {col[1]} ({col[2]})")
else:
    print("  None found")

# Check if new Bon Appetit recipes have any analysis data
cursor.execute("""
    SELECT id, title 
    FROM recipes 
    WHERE url LIKE '%bonappetit.com%' 
    AND id = '305817e3e19fc796edf89022084b9d7b'
    LIMIT 1
""")
sample_recipe = cursor.fetchone()

if sample_recipe:
    recipe_id, title = sample_recipe
    print(f"\nSAMPLE RECIPE: {title} (ID: {recipe_id})")
    
    # Check what data this recipe has
    cursor.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
    recipe_data = cursor.fetchone()
    print(f"  Has URL: {recipe_data[10] if len(recipe_data) > 10 else 'No'}")
    print(f"  Has description: {'Yes' if recipe_data[9] else 'No'}")

conn.close()
