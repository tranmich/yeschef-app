#!/usr/bin/env python3
"""Test extraction on page 95 (Acai Smoothie Bowls)"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import PyPDF2
from atk_teens_safe_extractor import ATKTeensExtractor, RecipeQualityValidator

def test_page_95():
    """Test the improved extraction on page 95"""
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\The Complete Cookbook for Teen - America's Test Kitchen Kids.pdf"
    
    # Extract page 95 content
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        page = reader.pages[94]  # 0-indexed, so page 95
        page_text = page.extract_text()
    
    print("=== PAGE 95 CONTENT ===")
    print(page_text[:300] + "...")
    print("\n" + "="*50 + "\n")
    
    # Create extractor and test ingredient extraction
    extractor = ATKTeensExtractor(pdf_path)
    
    # Test ingredient extraction
    print("=== TESTING INGREDIENT EXTRACTION ===")
    ingredients = extractor._extract_ingredients(page_text)
    print(f"Extracted ingredients:\n{ingredients}")
    print(f"\nIngredients length: {len(ingredients)}")
    print(f"Has ingredients: {bool(ingredients)}")
    
    # Test instruction extraction
    print("\n=== TESTING INSTRUCTION EXTRACTION ===")
    instructions = extractor._extract_instructions(page_text)
    print(f"Extracted instructions:\n{instructions}")
    print(f"\nInstructions length: {len(instructions)}")
    print(f"Has instructions: {bool(instructions)}")
    
    # Test full recipe extraction
    print("\n=== TESTING FULL RECIPE EXTRACTION ===")
    recipe_data = extractor._extract_recipe_from_page(page_text, 95)
    
    if recipe_data:
        print(f"Recipe title: {recipe_data.get('title', 'NOT FOUND')}")
        print(f"Recipe category: {recipe_data.get('category', 'NOT FOUND')}")
        print(f"Ingredients found: {bool(recipe_data.get('ingredients', ''))}")
        print(f"Instructions found: {bool(recipe_data.get('instructions', ''))}")
        
        # Test validation
        print("\n=== TESTING VALIDATION ===")
        validation = RecipeQualityValidator.validate_recipe_data(recipe_data)
        print(f"Validation result: {validation}")
        
        if validation['is_valid']:
            print("✅ SUCCESS! Recipe now passes validation!")
        else:
            print("❌ Still failing validation. Reasons:")
            for issue in validation['issues']:
                print(f"  - {issue}")
    else:
        print("No recipe data extracted!")

if __name__ == "__main__":
    test_page_95()
