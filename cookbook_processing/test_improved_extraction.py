#!/usr/bin/env python3
"""Test improved ingredient extraction on page 101"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import PyPDF2
from atk_teens_safe_extractor import ATKTeensExtractor, RecipeQualityValidator

def test_page_101():
    """Test the improved extraction on page 101"""
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\The Complete Cookbook for Teen - America's Test Kitchen Kids.pdf"
    
    # Extract page 101 content
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        page = reader.pages[100]  # 0-indexed, so page 101
        page_text = page.extract_text()
    
    print("=== PAGE 101 CONTENT ===")
    print(page_text[:500] + "...")
    print("\n" + "="*50 + "\n")
    
    # Create extractor and test ingredient extraction
    extractor = ATKTeensExtractor(pdf_path)
    
    # Test ingredient extraction
    print("=== TESTING INGREDIENT EXTRACTION ===")
    ingredients = extractor._extract_ingredients(page_text)
    print(f"Extracted ingredients:\n{ingredients}")
    print(f"\nIngredients length: {len(ingredients)}")
    print(f"Has ingredients: {bool(ingredients)}")
    
    # Test full recipe extraction
    print("\n=== TESTING FULL RECIPE EXTRACTION ===")
    recipe_data = extractor._extract_recipe_from_page(page_text, 101)
    
    if recipe_data:
        print(f"Recipe title: {recipe_data.get('title', 'NOT FOUND')}")
        print(f"Recipe category: {recipe_data.get('category', 'NOT FOUND')}")
        print(f"Ingredients found: {bool(recipe_data.get('ingredients', ''))}")
        print(f"Instructions found: {bool(recipe_data.get('instructions', ''))}")
        
        # Test validation
        print("\n=== TESTING VALIDATION ===")
        validation = RecipeQualityValidator.validate_recipe_data(recipe_data)
        print(f"Validation result: {validation}")
        
        if not validation['is_valid']:
            print("Validation failed! Reasons:")
            for issue in validation['issues']:
                print(f"  - {issue}")
    else:
        print("No recipe data extracted!")

if __name__ == "__main__":
    test_page_101()
