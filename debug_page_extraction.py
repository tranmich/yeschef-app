#!/usr/bin/env python3
"""
Debug Script - Test extraction on a specific page
"""

import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cookbook_processing.atk_25th_simplified_intelligent_extractor import ATK25thSimplifiedIntelligentExtractor

import PyPDF2

def test_page_extraction():
    """Test extraction on page 250 which we know has a complete recipe"""
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
    
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        page = reader.pages[249]  # Page 250
        text = page.extract_text()
        
        print("=== PAGE 250 CONTENT ===")
        print(text)
        print("\n=== TESTING EXTRACTION ===")
        
        # Create extractor
        extractor = ATK25thSimplifiedIntelligentExtractor(pdf_path)
        
        # Test recipe potential
        has_potential = extractor._has_recipe_potential(text)
        print(f"Has recipe potential: {has_potential}")
        
        if has_potential:
            # Test title extraction
            title = extractor._extract_title_intelligently(text)
            print(f"Extracted title: '{title}'")
            
            # Test ingredient extraction
            ingredients = extractor._extract_ingredients_directly(text)
            print(f"Extracted ingredients: {len(ingredients.split('\\n')) if ingredients else 0} lines")
            if ingredients:
                print(f"First few ingredients:")
                for line in ingredients.split('\\n')[:5]:
                    print(f"  {line}")
            
            # Test instruction extraction
            instructions = extractor._extract_instructions_directly(text)
            print(f"Extracted instructions: {len(instructions.split('\\n')) if instructions else 0} lines")
            if instructions:
                print(f"First few instructions:")
                for line in instructions.split('\\n')[:3]:
                    print(f"  {line}")
            
            # Test complete extraction
            if title and ingredients and instructions:
                print("\\n=== COMPLETE RECIPE EXTRACTED ===")
                recipe_data = {
                    'title': title,
                    'ingredients': ingredients,
                    'instructions': instructions
                }
                
                # Test semantic validation
                semantic_result = extractor.semantic_engine.validate_complete_recipe(recipe_data)
                print(f"Semantic validation:")
                print(f"  Is valid: {semantic_result.is_valid_recipe}")
                print(f"  Confidence: {semantic_result.confidence_score:.2f}")
                print(f"  Errors: {semantic_result.validation_errors}")
                print(f"  Warnings: {semantic_result.validation_warnings}")
            else:
                print("\\n=== INCOMPLETE EXTRACTION ===")
                print(f"Missing: {[item for item, value in [('title', title), ('ingredients', ingredients), ('instructions', instructions)] if not value]}")

if __name__ == "__main__":
    test_page_extraction()
