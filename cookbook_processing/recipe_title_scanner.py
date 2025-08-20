#!/usr/bin/env python3
"""
🔍 Recipe Scanner for ATK Teens Cookbook
=======================================

Scans the entire book for actual recipe titles and counts them
"""

import PyPDF2
import re

def find_recipe_titles(pdf_path):
    """Scan entire PDF for recipe titles based on patterns"""
    print("🔍 Scanning entire PDF for recipe titles...")
    
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        total_pages = len(pdf_reader.pages)
        
        recipes_found = []
        
        for page_num in range(total_pages):
            if page_num % 50 == 0:
                print(f"  📄 Processing page {page_num + 1}/{total_pages}...")
            
            try:
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                
                # Look for recipe patterns
                recipes_on_page = extract_recipes_from_page(text, page_num + 1)
                recipes_found.extend(recipes_on_page)
                
            except Exception as e:
                continue
        
        return recipes_found

def extract_recipes_from_page(text, page_num):
    """Extract recipe titles from a single page"""
    recipes = []
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Look for recipe title patterns
        if is_likely_recipe_title(line, lines, i):
            # Clean up the title
            clean_title = clean_recipe_title(line)
            if clean_title and len(clean_title) > 3:
                recipes.append({
                    'title': clean_title,
                    'page': page_num,
                    'raw_line': line
                })
    
    return recipes

def is_likely_recipe_title(line, all_lines, line_index):
    """Determine if a line is likely a recipe title"""
    
    # Skip obvious non-recipes
    skip_patterns = [
        r'^chapter\s*\d+',
        r'^introduction',
        r'^contents',
        r'^index',
        r'^page\s*\d+',
        r'^\d+$',
        r'^preparation time',
        r'^cook time',
        r'^serves',
        r'^makes',
        r'^ingredients',
        r'^instructions',
        r'^before you begin',
        r'^prepare ingredients',
        r'^make recipe',
        r'^beginner$',
        r'^intermediate$',
        r'^advanced$',
        r'^vegetarian$',
        r'^\d+\s*minutes?$',
        r'^\d+\s*hours?$',
        r'^step\s*\d+',
        r'^america.*test.*kitchen',
        r'^copyright',
        r'^all rights reserved',
    ]
    
    line_lower = line.lower().strip()
    
    for pattern in skip_patterns:
        if re.match(pattern, line_lower):
            return False
    
    # Recipe titles are often:
    # 1. In ALL CAPS (but not single words)
    # 2. Title Case with food words
    # 3. Reasonable length (5-60 characters)
    # 4. Not just numbers or symbols
    
    if len(line) < 5 or len(line) > 60:
        return False
    
    # Check if it's in ALL CAPS and has multiple words
    if line.isupper() and len(line.split()) >= 2:
        return True
    
    # Check if it contains food-related words and is in Title Case
    food_words = [
        'cake', 'bread', 'soup', 'sauce', 'chicken', 'beef', 'pork', 'fish',
        'pasta', 'salad', 'pizza', 'burger', 'sandwich', 'cookie', 'pie',
        'muffin', 'pancake', 'waffle', 'eggs', 'omelet', 'frittata',
        'rice', 'quinoa', 'beans', 'lentils', 'cheese', 'cream', 'butter',
        'roasted', 'grilled', 'baked', 'fried', 'steamed', 'braised',
        'stir-fry', 'casserole', 'curry', 'stew', 'chili', 'tacos',
        'burrito', 'quesadilla', 'smoothie', 'juice', 'tea', 'coffee',
        'chocolate', 'vanilla', 'strawberry', 'banana', 'apple', 'orange',
        'garlic', 'herb', 'spice', 'honey', 'maple', 'caramel', 'fudge'
    ]
    
    if any(word in line_lower for word in food_words):
        # Check if next few lines contain recipe indicators
        next_lines = all_lines[line_index:line_index+5]
        next_text = ' '.join(next_lines).lower()
        
        recipe_indicators = ['serves', 'minutes', 'ingredients', 'instructions', 'prepare', 'cook', 'bake']
        if any(indicator in next_text for indicator in recipe_indicators):
            return True
    
    return False

def clean_recipe_title(title):
    """Clean up recipe title"""
    # Remove common prefixes/suffixes that aren't part of the title
    title = re.sub(r'^(recipe|test kitchen|america.*test.*kitchen)', '', title, flags=re.IGNORECASE)
    title = re.sub(r'(page \d+|serves \d+|\d+ minutes).*$', '', title, flags=re.IGNORECASE)
    
    return title.strip()

def analyze_recipes(recipes):
    """Analyze and categorize found recipes"""
    print(f"\n📊 RECIPE ANALYSIS")
    print("=" * 40)
    print(f"Total recipes found: {len(recipes)}")
    
    # Group by characteristics
    all_caps = [r for r in recipes if r['title'].isupper()]
    title_case = [r for r in recipes if r['title'].istitle()]
    
    print(f"All caps titles: {len(all_caps)}")
    print(f"Title case titles: {len(title_case)}")
    
    # Show some examples
    print(f"\n📝 SAMPLE RECIPES FOUND:")
    print("-" * 30)
    
    for i, recipe in enumerate(recipes[:30], 1):
        print(f"{i:2d}. {recipe['title']} (page {recipe['page']})")
    
    if len(recipes) > 30:
        print(f"... and {len(recipes) - 30} more recipes")
    
    return recipes

def main():
    pdf_path = 'The Complete Cookbook for Teen - America\'s Test Kitchen Kids.pdf'
    
    print("🚀 RECIPE TITLE SCANNER")
    print("=" * 30)
    
    # Find all recipes
    recipes = find_recipe_titles(pdf_path)
    
    # Analyze results
    final_recipes = analyze_recipes(recipes)
    
    print(f"\n🎯 CONCLUSION:")
    print(f"Expected recipes from title: 70+")
    print(f"Actually found: {len(final_recipes)}")
    print(f"Previous extraction found: 57")
    print(f"Difference: {len(final_recipes) - 57} recipes missed")

if __name__ == "__main__":
    main()
