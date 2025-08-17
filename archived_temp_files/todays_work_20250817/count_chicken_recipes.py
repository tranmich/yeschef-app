import sqlite3

# Connect to the database
conn = sqlite3.connect('hungie.db')
cursor = conn.cursor()

# Count all recipes
cursor.execute("SELECT COUNT(*) FROM recipes")
total_recipes = cursor.fetchone()[0]

# Count chicken recipes (case insensitive)
cursor.execute("SELECT COUNT(*) FROM recipes WHERE LOWER(title) LIKE '%chicken%'")
chicken_recipes = cursor.fetchone()[0]

# Get a few sample chicken recipe titles
cursor.execute("SELECT title FROM recipes WHERE LOWER(title) LIKE '%chicken%' LIMIT 10")
sample_titles = cursor.fetchall()

print(f"Total recipes in database: {total_recipes}")
print(f"Chicken recipes in database: {chicken_recipes}")
print(f"\nSample chicken recipe titles:")
for title in sample_titles:
    print(f"  - {title[0]}")

conn.close()
