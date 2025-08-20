#!/usr/bin/env python3
"""
🔍 Debug Validation - Check why recipes are failing validation
"""

import PyPDF2
import re
import sys
import os

# Add the parent directory to the path so we can import from the extractor
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from atk_teens_safe_extractor import ATKTeensExtractor, RecipeQualityValidator

def debug_specific_pages():
    """Debug specific pages to see validation details"""
    pdf_path = 'The Complete Cookbook for Teen - America\'s Test Kitchen Kids.pdf'
    
    # Test specific pages that should have recipes
    test_pages = [61, 101, 351]  # Pages we saw had good recipe content
    
    print("🔍 DEBUGGING RECIPE VALIDATION")
    print("=" * 50)
    
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        for page_num in test_pages:
            if page_num <= len(pdf_reader.pages):
                print(f"\n📄 ANALYZING PAGE {page_num}")
                print("-" * 30)
                
                page = pdf_reader.pages[page_num - 1]  # Convert to 0-based index
                text = page.extract_text()
                
                # Create extractor instance
                extractor = ATKTeensExtractor(pdf_path)
                
                # Check if page is detected as recipe page
                is_recipe = extractor._is_recipe_page(text)
                print(f"Recipe page detected: {is_recipe}")
                
                if is_recipe:
                    # Extract recipe data
                    recipe_data = extractor._extract_recipe_from_page(text, page_num)
                    
                    if recipe_data:
                        print(f"\n📝 EXTRACTED RECIPE DATA:")
                        print(f"Title: '{recipe_data.get('title', 'MISSING')}'")
                        print(f"Category: '{recipe_data.get('category', 'MISSING')}'")
                        print(f"Ingredients length: {len(recipe_data.get('ingredients', ''))}")
                        print(f"Instructions length: {len(recipe_data.get('instructions', ''))}")
                        
                        if recipe_data.get('ingredients'):
                            print(f"Ingredients preview: {recipe_data['ingredients'][:100]}...")
                        
                        if recipe_data.get('instructions'):
                            print(f"Instructions preview: {recipe_data['instructions'][:100]}...")
                        
                        # Validate recipe
                        validation = RecipeQualityValidator.validate_recipe_data(recipe_data)
                        
                        print(f"\n🔍 VALIDATION RESULTS:")
                        print(f"Is valid: {validation['is_valid']}")
                        print(f"Quality score: {validation['quality_score']}")
                        print(f"Errors: {validation['errors']}")
                        print(f"Warnings: {validation['warnings']}")
                        print(f"Field scores: {validation['field_scores']}")
                    else:
                        print("❌ Failed to extract recipe data")
                else:
                    print("❌ Page not detected as recipe page")

def main():
    debug_specific_pages()

if __name__ == "__main__":
    main()
