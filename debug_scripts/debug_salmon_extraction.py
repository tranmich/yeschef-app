#!/usr/bin/env python3
"""
Debug script to analyze why Oven-Roasted Salmon failed semantic validation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cookbook_processing.atk_teens_visual_semantic_extractor import TeenRecipeExtractor
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

def debug_salmon_extraction():
    """Debug the Oven-Roasted Salmon extraction process"""
    
    extractor = TeenRecipeExtractor()
    
    print("🐟 DEBUGGING OVEN-ROASTED SALMON EXTRACTION")
    print("=" * 60)
    
    # First, check what visual structure is detected on page 299
    print("\n1. VISUAL STRUCTURE ANALYSIS - Page 299:")
    visual_data_299 = extractor._extract_visual_data(299)
    print(f"   Title candidates: {visual_data_299.get('title_candidates', [])}")
    print(f"   Ingredient sections: {len(visual_data_299.get('ingredient_sections', []))}")
    print(f"   Instruction sections: {len(visual_data_299.get('instruction_sections', []))}")
    
    # Check page 300 too
    print("\n2. VISUAL STRUCTURE ANALYSIS - Page 300:")
    visual_data_300 = extractor._extract_visual_data(300)
    print(f"   Title candidates: {visual_data_300.get('title_candidates', [])}")
    print(f"   Ingredient sections: {len(visual_data_300.get('ingredient_sections', []))}")
    print(f"   Instruction sections: {len(visual_data_300.get('instruction_sections', []))}")
    
    # Now let's see what the multi-page extraction captures
    print("\n3. MULTI-PAGE EXTRACTION:")
    
    # Start the multi-page recipe from page 299
    title = "Oven-Roasted Salmon"
    start_page = 299
    
    # Get the visual data for the starting page
    visual_data = visual_data_299
    
    # Extract the recipe using multi-page logic
    recipe_content = {
        'title': title,
        'ingredients': [],
        'instructions': [],
        'page_range': [start_page]
    }
    
    # Add ingredients from starting page
    for section in visual_data.get('ingredient_sections', []):
        recipe_content['ingredients'].extend(section.get('items', []))
    
    # Add instructions from starting page  
    for section in visual_data.get('instruction_sections', []):
        recipe_content['instructions'].extend(section.get('items', []))
    
    # Check continuation pages (300, 301)
    for page_num in [300, 301]:
        visual_data_cont = extractor._extract_visual_data(page_num)
        
        # Add ingredients if found
        for section in visual_data_cont.get('ingredient_sections', []):
            if section.get('items'):
                recipe_content['ingredients'].extend(section.get('items', []))
                recipe_content['page_range'].append(page_num)
                print(f"   📝 Added ingredients from page {page_num}")
        
        # Add instructions if found
        for section in visual_data_cont.get('instruction_sections', []):
            if section.get('items'):
                recipe_content['instructions'].extend(section.get('items', []))
                if page_num not in recipe_content['page_range']:
                    recipe_content['page_range'].append(page_num)
                print(f"   📋 Added instructions from page {page_num}")
    
    print(f"\n4. EXTRACTED CONTENT:")
    print(f"   Title: {recipe_content['title']}")
    print(f"   Page range: {recipe_content['page_range']}")
    print(f"   Ingredients count: {len(recipe_content['ingredients'])}")
    print(f"   Instructions count: {len(recipe_content['instructions'])}")
    
    # Show first few ingredients and instructions
    print(f"\n   First 3 ingredients:")
    for i, ingredient in enumerate(recipe_content['ingredients'][:3]):
        print(f"     {i+1}. {ingredient}")
    
    print(f"\n   First 3 instructions:")
    for i, instruction in enumerate(recipe_content['instructions'][:3]):
        print(f"     {i+1}. {instruction}")
    
    # Now test semantic validation
    print(f"\n5. SEMANTIC VALIDATION TEST:")
    
    # Create the recipe object for semantic validation
    recipe = {
        'title': recipe_content['title'],
        'ingredients': '\n'.join(recipe_content['ingredients']),
        'instructions': '\n'.join(recipe_content['instructions']),
        'source': 'ATK Teen Cookbook',
        'page_number': recipe_content['page_range'][0],
        'visual_confidence': 12  # Multi-page default
    }
    
    # Test semantic validation
    semantic_score = extractor._calculate_semantic_score(recipe)
    print(f"   Semantic score: {semantic_score}")
    
    # Check if it would pass different thresholds
    print(f"   Would pass 0.60 threshold: {semantic_score >= 0.60}")
    print(f"   Would pass 0.65 threshold: {semantic_score >= 0.65}")
    print(f"   Would pass 0.70 threshold: {semantic_score >= 0.70}")
    
    # Test teen cookbook override
    teen_override_passed = extractor._teen_cookbook_semantic_override(recipe, semantic_score)
    print(f"   Teen cookbook override: {teen_override_passed}")
    
    # Show what the semantic analyzer thinks about the content
    print(f"\n6. SEMANTIC ANALYSIS DETAILS:")
    
    # Check ingredients quality
    ingredients_text = recipe['ingredients']
    instructions_text = recipe['instructions']
    
    print(f"   Ingredients length: {len(ingredients_text)} characters")
    print(f"   Instructions length: {len(instructions_text)} characters")
    
    # Check for cooking keywords in instructions
    cooking_keywords = ['cook', 'bake', 'heat', 'add', 'mix', 'stir', 'pour', 'place', 'remove', 'serve']
    found_keywords = [word for word in cooking_keywords if word.lower() in instructions_text.lower()]
    print(f"   Cooking keywords found: {found_keywords}")
    
    # Check ingredient format
    ingredient_lines = [line.strip() for line in ingredients_text.split('\n') if line.strip()]
    print(f"   Ingredient lines: {len(ingredient_lines)}")
    
    if ingredient_lines:
        print(f"   Sample ingredients:")
        for i, ing in enumerate(ingredient_lines[:3]):
            print(f"     - {ing}")

if __name__ == "__main__":
    debug_salmon_extraction()
