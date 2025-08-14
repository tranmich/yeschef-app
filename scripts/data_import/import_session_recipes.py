#!/usr/bin/env python3
"""
Updated script to properly handle session files from Chrome extension
"""
import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

def check_session_file_structure(filepath):
    """Analyze the structure of a session file"""
    print(f"🔍 ANALYZING SESSION FILE STRUCTURE: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"📋 Top-level keys: {list(data.keys())}")
    
    if 'sessionInfo' in data:
        session_info = data['sessionInfo']
        print(f"📊 Session Info:")
        print(f"   Collection Date: {session_info.get('collectionDate')}")
        print(f"   Recipes Collected: {session_info.get('recipesCollected')}")
        print(f"   Runtime: {session_info.get('runtimeFormatted')}")
        print(f"   Categories: {session_info.get('categoriesTargeted')}")
    
    if 'recipes' in data:
        recipes = data['recipes']
        print(f"📄 Recipes array: {len(recipes)} recipes")
        
        if recipes:
            sample_recipe = recipes[0]
            print(f"🔍 Sample recipe structure:")
            print(f"   Keys: {list(sample_recipe.keys())}")
            print(f"   Name: {sample_recipe.get('name', 'NO NAME FIELD')}")
            print(f"   Description: {sample_recipe.get('description', 'NO DESCRIPTION')[:100]}...")
            print(f"   Ingredients: {len(sample_recipe.get('ingredients', []))} items")
            print(f"   Instructions: {len(sample_recipe.get('instructions', []))} steps")
    
    return data

def import_session_recipes_properly():
    """Import session recipes with correct parsing"""
    print("🚀 PROPERLY IMPORTING SESSION RECIPES")
    print("=" * 60)
    
    # Get session files from data folder
    data_path = Path('data')
    session_files = [f for f in data_path.iterdir() if 'session_' in f.name and f.suffix == '.json']
    
    print(f"📁 Found {len(session_files)} session files:")
    for f in session_files:
        print(f"   📄 {f.name}")
    
    total_imported = 0
    
    for session_file in session_files:
        print(f"\n{'='*60}")
        
        # Analyze structure first
        data = check_session_file_structure(session_file)
        
        # Extract recipes properly
        recipes = data.get('recipes', [])
        
        if not recipes:
            print(f"❌ No recipes found in {session_file.name}")
            continue
        
        print(f"\n📥 IMPORTING {len(recipes)} RECIPES FROM {session_file.name}")
        
        # Connect to database
        conn = sqlite3.connect('hungie.db')
        cursor = conn.cursor()
        
        # Get existing recipes to avoid duplicates
        cursor.execute('SELECT name FROM recipes')
        existing_names = {row[0] for row in cursor.fetchall()}
        
        imported_count = 0
        skipped_count = 0
        
        for i, recipe in enumerate(recipes):
            recipe_name = recipe.get('name', f'Session Recipe {i+1}')
            
            # Skip if already exists
            if recipe_name in existing_names:
                skipped_count += 1
                continue
            
            # Generate unique ID
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            recipe_id = f"session_{timestamp}_{imported_count:04d}"
            
            try:
                # Insert recipe
                cursor.execute('''
                    INSERT OR IGNORE INTO recipes 
                    (id, name, description, prep_time, cook_time, total_time, servings, url, date_saved)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    recipe_id,
                    recipe_name,
                    recipe.get('description', ''),
                    recipe.get('prep_time', recipe.get('prepTime', '')),
                    recipe.get('cook_time', recipe.get('cookTime', '')),
                    recipe.get('total_time', recipe.get('totalTime', '')),
                    recipe.get('servings', 4),
                    recipe.get('url', ''),
                    datetime.now().isoformat()
                ))
                
                if cursor.rowcount > 0:
                    imported_count += 1
                    
                    # Process ingredients
                    ingredients = recipe.get('ingredients', [])
                    for ingredient in ingredients:
                        if isinstance(ingredient, dict):
                            ingredient_text = ingredient.get('text', ingredient.get('original', str(ingredient)))
                        else:
                            ingredient_text = str(ingredient)
                        
                        # Clean up ingredient text (remove comments/reviews)
                        if len(ingredient_text) > 500:  # Likely a comment, skip
                            continue
                        
                        if ingredient_text.strip():
                            # Insert ingredient
                            cursor.execute('INSERT OR IGNORE INTO ingredients (name) VALUES (?)', (ingredient_text,))
                            cursor.execute('SELECT id FROM ingredients WHERE name = ?', (ingredient_text,))
                            result = cursor.fetchone()
                            if result:
                                ingredient_id = result[0]
                                
                                # Link to recipe
                                cursor.execute('''
                                    INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit)
                                    VALUES (?, ?, ?, ?)
                                ''', (recipe_id, ingredient_id, '', ''))
                    
                    # Process instructions
                    instructions = recipe.get('instructions', [])
                    for j, instruction in enumerate(instructions):
                        if isinstance(instruction, dict):
                            step_number = instruction.get('step', j + 1)
                            instruction_text = instruction.get('text', str(instruction))
                        else:
                            step_number = j + 1
                            instruction_text = str(instruction)
                        
                        if instruction_text.strip():
                            cursor.execute('''
                                INSERT OR IGNORE INTO instructions (recipe_id, step_number, instruction)
                                VALUES (?, ?, ?)
                            ''', (recipe_id, step_number, instruction_text))
                    
                    print(f"✅ Imported: {recipe_name[:50]}...")
                    
            except Exception as e:
                print(f"❌ Failed to import {recipe_name}: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"📊 {session_file.name} Summary:")
        print(f"   ✅ Imported: {imported_count} new recipes")
        print(f"   ⏭️ Skipped: {skipped_count} existing recipes")
        
        total_imported += imported_count
    
    return total_imported

def analyze_imported_recipes():
    """Run analyzer ONLY on newly imported recipes"""
    print(f"\n🧠 ANALYZING NEWLY IMPORTED RECIPES")
    print("=" * 50)
    
    try:
        from recipe_analyzer import RecipeAnalyzer
        
        analyzer = RecipeAnalyzer()
        result = analyzer.analyze_new_recipes_only()
        
        if isinstance(result, dict):
            print(f"✅ Analysis complete!")
            print(f"   📊 Total analyzed: {result.get('total_analyzed', 'unknown')}")
            print(f"   🆕 New analyses: {result.get('new_analyses', 'unknown')}")
            print(f"   📈 Coverage: {result.get('coverage', 0):.1f}%")
        else:
            print(f"✅ Analysis complete!")
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return False

def main():
    """Main process to properly import session files"""
    print("🚀 SESSION FILE IMPORT - CORRECTED VERSION")
    print("=" * 70)
    
    # Check current state
    conn = sqlite3.connect('hungie.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM recipes')
    initial_count = cursor.fetchone()[0]
    conn.close()
    
    print(f"📊 Initial recipe count: {initial_count}")
    
    # Import session recipes properly
    imported = import_session_recipes_properly()
    
    if imported > 0:
        print(f"\n⏳ Analyzing {imported} new recipes...")
        analyze_imported_recipes()
        
        # Final count
        conn = sqlite3.connect('hungie.db')
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM recipes')
        final_count = cursor.fetchone()[0]
        conn.close()
        
        print(f"\n✅ SESSION IMPORT COMPLETE!")
        print(f"📊 Final Summary:")
        print(f"   Before: {initial_count} recipes")
        print(f"   After: {final_count} recipes")
        print(f"   Newly imported: {imported} recipes")
    else:
        print("ℹ️ No new recipes to import")

if __name__ == "__main__":
    main()
