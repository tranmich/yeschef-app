#!/usr/bin/env python3
"""
Quick check of local SQLite recipes
"""
import sqlite3

conn = sqlite3.connect('hungie.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get total count
cursor.execute('SELECT COUNT(*) as count FROM recipes')
total = cursor.fetchone()['count']
print(f"📊 Total recipes in local SQLite: {total}")

# Get sample recipes
cursor.execute('SELECT title, servings, category FROM recipes LIMIT 10')
recipes = cursor.fetchall()

print("\n📋 Sample local recipes:")
for recipe in recipes:
    title = recipe['title'] or "No title"
    servings = recipe['servings'] or "No servings"
    category = recipe['category'] or "No category"
    print(f"- {title} | {servings} | {category}")

# Check servings data
cursor.execute('SELECT COUNT(*) as count FROM recipes WHERE servings IS NOT NULL AND servings != ""')
with_servings = cursor.fetchone()['count']
print(f"\n🍽️  Recipes with servings data: {with_servings}")

conn.close()
