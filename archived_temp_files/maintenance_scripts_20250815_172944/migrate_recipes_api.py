#!/usr/bin/env python3
"""
Recipe Migration Script - API Version
Migrates recipes from local SQLite database to Railway PostgreSQL via REST API
"""
import sqlite3
import requests
import json
import time
from datetime import datetime

# Configuration
SQLITE_DB_PATH = 'hungie.db'
BACKEND_URL = 'https://yeschefapp-production.up.railway.app'
BATCH_SIZE = 10  # Upload recipes in batches to avoid overwhelming the server

def get_sqlite_recipes():
    """Get all recipes from local SQLite database"""
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        
        # Get all recipes
        cursor.execute("SELECT * FROM recipes")
        recipes = cursor.fetchall()
        
        conn.close()
        
        print(f"✅ Found {len(recipes)} recipes in SQLite database")
        return recipes
        
    except Exception as e:
        print(f"❌ Error reading SQLite database: {e}")
        return []

def upload_recipe_to_postgresql(recipe_data):
    """Upload a single recipe to PostgreSQL via API"""
    try:
        # Prepare recipe data for API
        api_data = {
            'title': recipe_data.get('title', ''),
            'description': recipe_data.get('description', ''),
            'ingredients': recipe_data.get('ingredients', ''),
            'instructions': recipe_data.get('instructions', ''),
            'image_url': recipe_data.get('image_url', ''),
            'source': recipe_data.get('source', ''),
            'category': recipe_data.get('category', ''),
            'flavor_profile': recipe_data.get('flavor_profile', '')
        }
        
        # Make API call to add recipe
        response = requests.post(
            f"{BACKEND_URL}/api/recipes",
            json=api_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 201:
            return True, "Success"
        else:
            return False, f"API Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return False, f"Upload error: {e}"

def migrate_recipes():
    """Main migration function"""
    print("🚀 Starting recipe migration from SQLite to PostgreSQL")
    print(f"📊 Source: {SQLITE_DB_PATH}")
    print(f"🎯 Target: {BACKEND_URL}")
    print("=" * 60)
    
    # Get recipes from SQLite
    recipes = get_sqlite_recipes()
    if not recipes:
        print("❌ No recipes found to migrate")
        return
    
    # Migration statistics
    total_recipes = len(recipes)
    successful = 0
    failed = 0
    failed_recipes = []
    
    print(f"📤 Starting upload of {total_recipes} recipes...")
    
    # Upload recipes in batches
    for i, recipe in enumerate(recipes, 1):
        print(f"📝 [{i}/{total_recipes}] Uploading: {recipe['title'][:50]}...")
        
        # Convert sqlite3.Row to dictionary
        recipe_dict = dict(recipe)
        
        success, message = upload_recipe_to_postgresql(recipe_dict)
        
        if success:
            successful += 1
            print(f"   ✅ Success")
        else:
            failed += 1
            failed_recipes.append({
                'title': recipe['title'],
                'error': message
            })
            print(f"   ❌ Failed: {message}")
        
        # Small delay to avoid overwhelming the server
        if i % BATCH_SIZE == 0:
            print(f"   ⏳ Processed {i} recipes, taking a brief pause...")
            time.sleep(1)
    
    # Migration summary
    print("=" * 60)
    print("📊 MIGRATION SUMMARY")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(successful/total_recipes)*100:.1f}%")
    
    if failed_recipes:
        print("\n❌ Failed recipes:")
        for failed in failed_recipes[:5]:  # Show first 5 failures
            print(f"   • {failed['title']}: {failed['error']}")
        if len(failed_recipes) > 5:
            print(f"   ... and {len(failed_recipes) - 5} more")
    
    print("🎉 Migration completed!")

if __name__ == "__main__":
    migrate_recipes()
