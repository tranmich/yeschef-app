#!/usr/bin/env python3
"""
Debug full recipe extraction process step by step
"""

import sys
import os
import re
import PyPDF2

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cookbook_processing.atk_25th_simplified_intelligent_extractor import ATK25thSimplifiedIntelligentExtractor

def debug_full_extraction(page_num: int = 90):
    """Debug the complete extraction process"""
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
    extractor = ATK25thSimplifiedIntelligentExtractor(pdf_path)
    
    print(f"🔍 DEBUGGING FULL EXTRACTION PROCESS - PAGE {page_num}")
    print("=" * 70)
    
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        page = reader.pages[page_num - 1]
        text = page.extract_text()
        
        print(f"Page text length: {len(text)} characters")
        
        # Test title extraction
        print("\n1. TITLE EXTRACTION:")
        title = extractor._extract_title_intelligently(text)
        print(f"   Extracted title: '{title}'")
        
        if not title:
            print("   ❌ Title extraction failed - stopping here")
            return
        
        # Test ingredient extraction
        print("\n2. INGREDIENT EXTRACTION:")
        ingredients = extractor._extract_ingredients_directly(text)
        print(f"   Raw ingredients: {ingredients[:200] if ingredients else 'None'}...")
        
        if ingredients:
            cleaned_ingredients = extractor._clean_pdf_text(ingredients)
            print(f"   Cleaned ingredients: {cleaned_ingredients[:200] if cleaned_ingredients else 'None'}...")
        
        if not ingredients:
            print("   ❌ Ingredient extraction failed")
            
            # Debug why
            lines = text.split('\n')
            print("\n   Debugging ingredient patterns:")
            
            measurement_patterns = [
                r'^\d+\s*\(\d+.*?ounce\)',  # 2(15-ounce) cans
                r'^\d+\s*(cup|tablespoon|teaspoon|pound|ounce|tbsp|tsp|lb|oz)\s',
                r'^\d+.*?(large|medium|small|whole)\s',
                r'^\d+.*?(chopped|diced|minced|sliced|grated|stemmed|seeded)',
                r'^(\d+/\d+|\d+\.\d+)\s*(cup|tablespoon|teaspoon)',
                r'^\d+\s*(cloves?|cans?|packages?|pounds?|ounces?|slices?)\s',
                r'^[¾½¼⅓⅔⅛]',  # Fraction symbols
            ]
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line or len(line) < 3:
                    continue
                
                is_ingredient = False
                for pattern in measurement_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        is_ingredient = True
                        break
                
                if is_ingredient:
                    print(f"     Line {i}: '{line}' - MATCHES ingredient pattern")
                elif any(word in line.lower() for word in ['cup', 'tablespoon', 'teaspoon', 'ounce', 'pound']):
                    print(f"     Line {i}: '{line}' - Contains measurements but doesn't match pattern")
            
            return
        
        # Test instruction extraction
        print("\n3. INSTRUCTION EXTRACTION:")
        instructions = extractor._extract_instructions_directly(text)
        print(f"   Raw instructions: {instructions[:200] if instructions else 'None'}...")
        
        if instructions:
            cleaned_instructions = extractor._clean_pdf_text(instructions)
            print(f"   Cleaned instructions: {cleaned_instructions[:200] if cleaned_instructions else 'None'}...")
        
        if not instructions:
            print("   ❌ Instruction extraction failed")
            
            # Debug why
            lines = text.split('\n')
            print("\n   Debugging instruction patterns:")
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                step_match = re.match(r'^(\d+)\.\s*(.+)', line)
                if step_match:
                    print(f"     Line {i}: '{line}' - MATCHES instruction pattern")
            
            return
        
        # Test complete recipe validation
        print("\n4. COMPLETE RECIPE VALIDATION:")
        recipe_data = {
            'title': title,
            'ingredients': cleaned_ingredients if ingredients else ingredients,
            'instructions': cleaned_instructions if instructions else instructions
        }
        
        validation_result = extractor.semantic_engine.validate_complete_recipe(recipe_data)
        print(f"   Is valid recipe: {validation_result.is_valid_recipe}")
        print(f"   Confidence: {validation_result.confidence_score:.2f}")
        if validation_result.validation_errors:
            print(f"   Errors: {validation_result.validation_errors}")

if __name__ == "__main__":
    debug_full_extraction(90)
