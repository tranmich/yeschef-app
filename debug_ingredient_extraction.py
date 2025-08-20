#!/usr/bin/env python3
"""
Debug the ingredient extraction step by step
"""

import sys
import os
import PyPDF2

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cookbook_processing.atk_25th_simplified_intelligent_extractor import ATK25thSimplifiedIntelligentExtractor

def debug_ingredient_extraction():
    """Debug ingredient extraction step by step"""
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
    
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        page = reader.pages[249]  # Page 250
        text = page.extract_text()
        
        extractor = ATK25thSimplifiedIntelligentExtractor(pdf_path)
        
        print("=== Raw Ingredient Extraction ===")
        raw_ingredients = extractor._extract_ingredients_directly(text)
        print(f"Raw ingredients:\n{repr(raw_ingredients)}")
        
        print(f"\n=== After Cleanup ===")
        if raw_ingredients:
            cleaned_ingredients = extractor._clean_pdf_text(raw_ingredients)
            print(f"Cleaned ingredients:\n{repr(cleaned_ingredients)}")
            
            print(f"\n=== Line Analysis ===")
            print(f"Raw lines: {len(raw_ingredients.split(chr(10)))}")
            print(f"Cleaned lines: {len(cleaned_ingredients.split(chr(10)))}")
            
            print(f"\nRaw ingredient lines:")
            for i, line in enumerate(raw_ingredients.split('\n')):
                print(f"{i}: '{line}'")
                
            print(f"\nCleaned ingredient lines:")
            for i, line in enumerate(cleaned_ingredients.split('\n')):
                print(f"{i}: '{line}'")

if __name__ == "__main__":
    debug_ingredient_extraction()
