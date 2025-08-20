#!/usr/bin/env python3
"""
Test the complete extraction process step by step
"""

import sys
import os
import PyPDF2

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cookbook_processing.atk_25th_simplified_intelligent_extractor import ATK25thSimplifiedIntelligentExtractor

def test_complete_extraction():
    """Test the complete extraction process"""
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
    
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        page = reader.pages[249]  # Page 250
        text = page.extract_text()
        
        print("=== Complete Extraction Test ===")
        
        extractor = ATK25thSimplifiedIntelligentExtractor(pdf_path)
        
        # Call the direct extraction method
        recipe = extractor._extract_recipe_directly(text, 250)
        
        if recipe:
            print("✅ Recipe extracted successfully!")
            print(f"Title: {recipe['title']}")
            print(f"Ingredients: {len(recipe['ingredients'].split('•'))} items")
            print(f"Instructions: {len(recipe['instructions'].split('.'))} steps")
            print(f"Page: {recipe['page_number']}")
        else:
            print("❌ Recipe extraction failed")
            
        # Test direct extraction (bypass semantic validation)
        print("\n=== Direct Extraction (No Validation) ===")
        direct_recipe = extractor._extract_recipe_directly(text, 250)
        
        if direct_recipe:
            print("✅ Direct extraction successful!")
            print(f"Title: {direct_recipe['title']}")
            print(f"Ingredients: {len(direct_recipe['ingredients'].split('•'))} items")
            print(f"Instructions length: {len(direct_recipe['instructions'])} chars")
            
            # Now test semantic validation
            print("\n=== Testing Semantic Validation ===")
            validation_result = extractor.semantic_engine.validate_complete_recipe(direct_recipe)
            print(f"Valid: {validation_result.is_valid_recipe}")
            print(f"Confidence: {validation_result.confidence_score}")
            print(f"Errors: {validation_result.validation_errors}")
            print(f"Warnings: {validation_result.validation_warnings}")
        else:
            print("❌ Direct extraction failed")

if __name__ == "__main__":
    test_complete_extraction()
