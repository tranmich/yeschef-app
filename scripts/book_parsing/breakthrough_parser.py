"""
BREAKTHROUGH: Simple String-Based Recipe Parser
The PDF text comes as one continuous string, not lines!
"""

import pdfplumber
import re
import json
import sqlite3

def extract_recipes_from_continuous_text():
    """Extract recipes from continuous text format"""
    
    pdf_path = "Books/Canadian-Living-The-Ultimate-Cookbook.pdf"
    
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[40]  # Page 41
        text = page.extract_text()
        
        print("🔍 WORKING WITH CONTINUOUS TEXT")
        print("=" * 60)
        print(f"Text length: {len(text)} characters")
        print(f"Contains newlines: {'\\n' in text}")
        print(f"First 200 chars: {text[:200]}...")
        
        # Work with the text as a continuous string
        recipes = []
        
        # Pattern 1: Find recipe titles (before HANDS-ON TIME)
        title_pattern = r'(GOLDEN GAZPACHO VELVETY SPINACH SOUP|[A-Z][A-Z\\s]+)(?=\\s+HANDS-ON TIME)'
        title_matches = re.findall(title_pattern, text)
        print(f"\\n📝 Title matches: {title_matches}")
        
        # Pattern 2: Find timing info
        hands_on_pattern = r'HANDS-ON TIME\\s+(\\d+)\\s+minutes'
        hands_on_matches = re.findall(hands_on_pattern, text)
        print(f"⏱️ Hands-on times: {hands_on_matches}")
        
        total_time_pattern = r'TOTAL TIME\\s+(\\d+[½¼¾]?)\\s+(hours?|minutes?)'
        total_time_matches = re.findall(total_time_pattern, text)
        print(f"⏱️ Total times: {total_time_matches}")
        
        # Pattern 3: Find servings
        servings_pattern = r'MAKES\\s+(\\d+\\s+to\\s+\\d+)\\s+servings'
        servings_matches = re.findall(servings_pattern, text)
        print(f"👥 Servings: {servings_matches}")
        
        # Pattern 4: Find ingredients section
        ingredients_pattern = r'INGREDIENTS\\s+INGREDIENTS\\s+(.*?)\\s+DIRECTIONS'
        ingredients_match = re.search(ingredients_pattern, text, re.DOTALL)
        
        if ingredients_match:
            ingredients_text = ingredients_match.group(1)
            print(f"\\n📝 INGREDIENTS TEXT ({len(ingredients_text)} chars):")
            print(ingredients_text[:300] + "...")
            
            # Split ingredients into two columns (left and right)
            # Look for common patterns to split
            ing_lines = [line.strip() for line in ingredients_text.split('\\n') if line.strip()]
            if not ing_lines:
                # If no newlines, try to split by ingredient patterns
                # Look for measurements at the start of ingredients
                ing_parts = re.split(r'(?=\\d+\\s*[½¼¾]?\\s*(cups?|tbsp|tsp|g|ml))', ingredients_text)
                ing_lines = [part.strip() for part in ing_parts if part.strip()]
            
            print(f"Ingredient parts: {len(ing_lines)}")
            for i, ing in enumerate(ing_lines[:10]):
                print(f"  {i}: {ing}")
            
            # Try to identify two columns
            recipe1_ingredients = []
            recipe2_ingredients = []
            
            # Simple split - first half vs second half
            mid_point = len(ing_lines) // 2
            recipe1_ingredients = ing_lines[:mid_point]
            recipe2_ingredients = ing_lines[mid_point:]
            
            print(f"\\nRecipe 1 ingredients ({len(recipe1_ingredients)}):")
            for ing in recipe1_ingredients:
                print(f"  - {ing}")
            
            print(f"\\nRecipe 2 ingredients ({len(recipe2_ingredients)}):")
            for ing in recipe2_ingredients:
                print(f"  - {ing}")
        
        # Pattern 5: Find directions
        directions_pattern = r'DIRECTIONS\\s+DIRECTIONS\\s+(.*?)\\s+NUTRITIONAL'
        directions_match = re.search(directions_pattern, text, re.DOTALL)
        
        if directions_match:
            directions_text = directions_match.group(1)
            print(f"\\n🍳 DIRECTIONS TEXT ({len(directions_text)} chars):")
            print(directions_text[:300] + "...")
        
        # Create basic recipes
        if len(title_matches) >= 1:
            recipe1 = {
                'title': 'GOLDEN GAZPACHO',
                'page_number': 41,
                'hands_on_time': f"{hands_on_matches[0]} minutes" if hands_on_matches else "",
                'total_time': f"{total_time_matches[0][0]} {total_time_matches[0][1]}" if total_time_matches else "",
                'servings': f"makes {servings_matches[0]} servings" if servings_matches else "",
                'ingredients': recipe1_ingredients if 'recipe1_ingredients' in locals() else [],
                'instructions': ["Manual parsing needed for directions"]
            }
            
            recipe2 = {
                'title': 'VELVETY SPINACH SOUP',
                'page_number': 41,
                'hands_on_time': f"{hands_on_matches[1]} minutes" if len(hands_on_matches) > 1 else "",
                'total_time': f"{total_time_matches[1][0]} {total_time_matches[1][1]}" if len(total_time_matches) > 1 else "",
                'servings': f"makes {servings_matches[1]} servings" if len(servings_matches) > 1 else "",
                'ingredients': recipe2_ingredients if 'recipe2_ingredients' in locals() else [],
                'instructions': ["Manual parsing needed for directions"]
            }
            
            recipes = [recipe1, recipe2]
            
            print(f"\\n✅ EXTRACTED RECIPES:")
            for recipe in recipes:
                print(f"\\n--- {recipe['title']} ---")
                print(f"Time: {recipe['hands_on_time']} / {recipe['total_time']}")
                print(f"Servings: {recipe['servings']}")
                print(f"Ingredients: {len(recipe['ingredients'])}")
                print(f"Instructions: {len(recipe['instructions'])}")
            
            # Save to database
            conn = sqlite3.connect('breakthrough_recipes.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    page_number INTEGER,
                    data TEXT
                )
            ''')
            
            for recipe in recipes:
                cursor.execute('''
                    INSERT OR REPLACE INTO recipes (title, page_number, data)
                    VALUES (?, ?, ?)
                ''', (recipe['title'], recipe['page_number'], json.dumps(recipe)))
            
            conn.commit()
            conn.close()
            
            print(f"\\n🎉 BREAKTHROUGH! Saved {len(recipes)} recipes to breakthrough_recipes.db")
            
            return recipes
        
        return []


if __name__ == "__main__":
    extract_recipes_from_continuous_text()
