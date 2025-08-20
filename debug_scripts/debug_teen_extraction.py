#!/usr/bin/env python3
"""
Debug script to see exactly what's being extracted from teen cookbook pages
"""

import os
import sys
import PyPDF2
import re

# Add core systems to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core_systems'))

from semantic_recipe_engine import SemanticRecipeEngine, ValidationLevel

def debug_teen_extraction(page_num=48):
    """Debug what's being extracted from a specific page"""
    
    pdf_path = os.path.join('cookbook_processing', 'The Complete Cookbook for Teen - America\'s Test Kitchen Kids.pdf')
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return
    
    print(f"🔍 DEBUGGING EXTRACTION FROM PAGE {page_num}")
    print("=" * 60)
    
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        page = reader.pages[page_num - 1]
        page_text = page.extract_text()
    
    print("📄 RAW PAGE TEXT:")
    print("-" * 30)
    print(page_text[:1000])
    print("..." if len(page_text) > 1000 else "")
    
    # Extract title
    lines = page_text.split('\n')
    title = None
    for line in lines[:20]:
        line = line.strip()
        if (line.isupper() and 5 <= len(line) <= 60 and 
            not re.search(r'(BEGINNER|INTERMEDIATE|ADVANCED|VEGETARIAN|SERVES|MAKES|PREPARE|START|BEFORE)', line) and
            not re.search(r'\d+.*?(cup|tablespoon|teaspoon)', line)):
            title = line.title()
            break
    
    print(f"\n📝 EXTRACTED TITLE: {title}")
    
    # Extract ingredients
    prepare_pos = page_text.find('PREPARE INGREDIENTS')
    if prepare_pos != -1:
        content_after_prepare = page_text[prepare_pos + len('PREPARE INGREDIENTS'):].strip()
        start_cooking_pos = content_after_prepare.find('START COOKING!')
        if start_cooking_pos != -1:
            ingredients_text = content_after_prepare[:start_cooking_pos].strip()
        else:
            ingredients_text = content_after_prepare[:1000].strip()
    else:
        ingredients_text = ""
    
    print(f"\n🥘 EXTRACTED INGREDIENTS:")
    print("-" * 30)
    print(ingredients_text[:500])
    print("..." if len(ingredients_text) > 500 else "")
    
    # Extract instructions
    instructions_match = re.search(r'START COOKING!(.*?)(?=\n[A-Z\s]{10,}|$)', page_text, re.DOTALL)
    if instructions_match:
        instructions_text = instructions_match.group(1).strip()
    else:
        instructions_text = ""
    
    print(f"\n👨‍🍳 EXTRACTED INSTRUCTIONS:")
    print("-" * 30)
    print(instructions_text[:500])
    print("..." if len(instructions_text) > 500 else "")
    
    # Test semantic validation
    if title and ingredients_text and instructions_text:
        print(f"\n🧠 TESTING SEMANTIC VALIDATION:")
        print("-" * 30)
        
        # Create cleaned recipe
        recipe_data = {
            'title': title,
            'ingredients': clean_text(ingredients_text),
            'instructions': clean_text(instructions_text)
        }
        
        print(f"Cleaned title: {recipe_data['title']}")
        print(f"Cleaned ingredients: {recipe_data['ingredients'][:200]}...")
        print(f"Cleaned instructions: {recipe_data['instructions'][:200]}...")
        
        # Test semantic validation with different levels
        for level in [ValidationLevel.PERMISSIVE, ValidationLevel.MODERATE, ValidationLevel.STRICT]:
            engine = SemanticRecipeEngine(validation_level=level)
            result = engine.validate_complete_recipe(recipe_data)
            
            print(f"\n{level.value.upper()} validation:")
            print(f"  Valid: {result.is_valid_recipe}")
            print(f"  Confidence: {result.confidence_score:.2f}")
            if result.validation_errors:
                print(f"  Errors: {result.validation_errors}")
            if result.validation_warnings:
                print(f"  Warnings: {result.validation_warnings}")

def clean_text(text):
    """Clean PDF extraction artifacts - Enhanced for Teen Cookbook"""
    
    # Teen cookbook specific PDF extraction fixes
    teen_fixes = [
        # Common broken words in teen cookbook
        (r'\bcock ed\b', 'cooked'),
        (r'\bsepar ately\b', 'separately'),
        (r'\bdr ained\b', 'drained'), 
        (r'\bsl iced\b', 'sliced'),
        (r'\bpeeled\b', 'peeled'),
        (r'\boar d\b', 'board'),
        (r'\bpi tas\b', 'pitas'),
        (r'\bpi ta\b', 'pita'),
        (r'\br ed\b', 'red'),
        (r'\bhal f\b', 'half'),
        (r'\blar ge\b', 'large'),
        (r'\bsmal l\b', 'small'),
        (r'\bf or\b', 'for'),
        (r'\bgar lic\b', 'garlic'),
        (r'\bsal t\b', 'salt'),
        (r'\bpepper\b', 'pepper'),
        (r'\bmeasur ed\b', 'measured'),
        (r'\bunsal ted\b', 'unsalted'),
        (r'\bbut ter\b', 'butter'),
        (r'\bmuf fins\b', 'muffins'),
        (r'\bEngl ish\b', 'English'),
        (r'\bspl it\b', 'split'),
        (r'\bv egetable\b', 'vegetable'),
        (r'\boi l\b', 'oil'),
        (r'\bcloves\b', 'cloves'),
        (r'\btablespoon\b', 'tablespoon'),
        (r'\bteaspoon\b', 'teaspoon'),
        (r'\br oasted\b', 'roasted'),
        (r'\btomator oes\b', 'tomatoes'),
        (r'\bmuhr ooms\b', 'mushrooms'),
        (r'\bchick en\b', 'chicken'),
        (r'\by olks\b', 'yolks'),
        (r'\bhal f-and-hal f\b', 'half-and-half'),
        (r'\bvegetabl es\b', 'vegetables'),
        (r'\bpot atoes\b', 'potatoes'),
        (r'\bsea soning\b', 'seasoning'),
        (r'\bingredient s\b', 'ingredients'),
        (r'\binstr uctions\b', 'instructions'),
        (r'\btemper ature\b', 'temperature'),
        (r'\brefrig erator\b', 'refrigerator'),
        
        # Teen cookbook specific issues
        (r'\b4slices\b', '4 slices'),
        (r'\b2large\b', '2 large'),
        (r'\b1pinch\b', '1 pinch'),
        (r'\b1tablespoon\b', '1 tablespoon'),
        (r'\b2rolls\b', '2 rolls'),
        (r'\b1teaspoon\b', '1 teaspoon'),
        (r'\b2slices\b', '2 slices'),
        (r'\b2smal l\b', '2 small'),
        (r'\bbowls \b', 'bowls '),
    ]
    
    for pattern, replacement in teen_fixes:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Additional spacing and formatting fixes
    text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
    text = re.sub(r' ,', ',', text)   # Space before comma
    text = re.sub(r' \.', '.', text)  # Space before period
    text = text.strip()
    
    # Remove PDF page references
    text = re.sub(r'\(see this page\s*\)', '', text)
    text = re.sub(r'\(this page\s*\)', '', text)
    
    return text

if __name__ == "__main__":
    debug_teen_extraction(48)
