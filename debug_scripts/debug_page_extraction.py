#!/usr/bin/env python3
"""
Debug specific page extraction to see what's happening
"""

import sys
import os
import re
import PyPDF2

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_systems.semantic_recipe_engine import SemanticRecipeEngine, ValidationLevel

def debug_page_extraction(page_num: int = 90):
    """Debug extraction on a specific page"""
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
    semantic_engine = SemanticRecipeEngine(ValidationLevel.STRICT)
    
    print(f"🔍 DEBUGGING PAGE {page_num} EXTRACTION")
    print("=" * 60)
    
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        page = reader.pages[page_num - 1]
        text = page.extract_text()
        
        print(f"Page text length: {len(text)} characters")
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        print(f"Total lines: {len(lines)}")
        
        # Show first 25 lines
        print("\nFirst 25 lines:")
        for i, line in enumerate(lines[:25]):
            print(f"  {i:2d}: '{line}'")
        
        # Check for specific title
        hummus_line = None
        for i, line in enumerate(lines):
            if 'hummus' in line.lower():
                print(f"\nFound hummus on line {i}: '{line}'")
                hummus_line = line
                break
        
        if hummus_line:
            print(f"\n🔍 Testing '{hummus_line}' as title:")
            
            # Test if it would be found as potential title
            food_indicators = [
                'soup', 'salad', 'chicken', 'beef', 'pork', 'fish', 'pasta', 'rice',
                'bread', 'cake', 'pie', 'cookie', 'sauce', 'beans', 'vegetables',
                'roast', 'grilled', 'baked', 'fried', 'steamed', 'braised',
                'hummus', 'eggs', 'topping', 'walnut', 'spiced', 'curry', 'deviled',
                'cheese', 'cream', 'butter', 'chocolate', 'vanilla', 'lemon',
                'garlic', 'onion', 'mushroom', 'tomato', 'potato', 'carrot'
            ]
            
            # Check extraction conditions
            line_lower = hummus_line.lower()
            
            print(f"  Length: {len(hummus_line)} (valid: {3 < len(hummus_line) < 80})")
            print(f"  Contains food indicator: {any(indicator in line_lower for indicator in food_indicators)}")
            print(f"  Starts with ingredients/method: {line_lower.startswith(('ingredients', 'method', 'serves', 'makes', 'prep time', 'total time'))}")
            print(f"  Is numbered instruction: {bool(re.match(r'^[0-9]+\.', hummus_line))}")
            print(f"  Is measurement: {bool(re.match(r'^\d+\s*(cup|tablespoon|teaspoon|pound|ounce)', hummus_line))}")
            
            # Test semantic validation
            test_result = semantic_engine.validate_complete_recipe({
                'title': hummus_line,
                'ingredients': "",
                'instructions': ""
            })
            
            print(f"  Semantic validation: {test_result.is_valid_recipe}")
            print(f"  Confidence: {test_result.confidence_score:.2f}")
            print(f"  Errors: {test_result.validation_errors}")

if __name__ == "__main__":
    debug_page_extraction(90)
