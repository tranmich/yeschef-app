#!/usr/bin/env python3
"""
Test the exact ingredients string from extraction
"""

import sys
import os
import PyPDF2

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cookbook_processing.atk_25th_simplified_intelligent_extractor import ATK25thSimplifiedIntelligentExtractor
from core_systems.semantic_recipe_engine import SemanticRecipeEngine

def test_exact_ingredients():
    """Test the exact ingredients string from extraction"""
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
    
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        page = reader.pages[249]  # Page 250
        text = page.extract_text()
        
        extractor = ATK25thSimplifiedIntelligentExtractor(pdf_path)
        
        # Get the exact extracted ingredients
        recipe = extractor._extract_recipe_directly(text, 250)
        
        if recipe:
            ingredients = recipe['ingredients']
            print("=== Exact Extracted Ingredients ===")
            print(repr(ingredients))
            print(f"\nLength: {len(ingredients)} chars")
            print(f"Lines: {len(ingredients.split('\n'))}")
            
            # Test classification
            engine = SemanticRecipeEngine()
            ing_type, ing_confidence = engine.classify_content_type(ingredients)
            
            print(f"\nClassification: {ing_type}")
            print(f"Confidence: {ing_confidence}")
            
            # Test the recipe validation specifically
            recipe_data = {'ingredients': ingredients}
            print(f"\n=== Testing recipe validation ingredients check ===")
            
            # This is the exact logic from validate_complete_recipe
            ingredients_check = recipe_data.get('ingredients', '').strip()
            if ingredients_check:
                ing_type_check, ing_confidence_check = engine.classify_content_type(ingredients_check)
                print(f"Type: {ing_type_check}")
                print(f"Confidence: {ing_confidence_check}")
                print(f"Is INGREDIENT_LIST? {ing_type_check == engine.ContentType.INGREDIENT_LIST}")
                
                if ing_type_check != engine.ContentType.INGREDIENT_LIST:
                    print(f"ERROR: Not classified as ingredient list!")
        else:
            print("No recipe extracted")

if __name__ == "__main__":
    test_exact_ingredients()
