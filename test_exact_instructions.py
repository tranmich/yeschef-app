#!/usr/bin/env python3
"""
Test the exact instructions string from extraction
"""

import sys
import os
import PyPDF2

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cookbook_processing.atk_25th_simplified_intelligent_extractor import ATK25thSimplifiedIntelligentExtractor
from core_systems.semantic_recipe_engine import SemanticRecipeEngine

def test_exact_instructions():
    """Test the exact instructions string from extraction"""
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
    
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        page = reader.pages[249]  # Page 250
        text = page.extract_text()
        
        extractor = ATK25thSimplifiedIntelligentExtractor(pdf_path)
        
        # Get the exact extracted instructions
        recipe = extractor._extract_recipe_directly(text, 250)
        
        if recipe:
            instructions = recipe['instructions']
            print("=== Exact Extracted Instructions ===")
            print(repr(instructions))
            print(f"\nLength: {len(instructions)} chars")
            print(f"Lines: {len(instructions.split(chr(10)))}")
            print(f"\nFormatted instructions:")
            print(instructions)
            
            # Test classification
            engine = SemanticRecipeEngine()
            inst_type, inst_confidence = engine.classify_content_type(instructions)
            
            print(f"\nClassification: {inst_type}")
            print(f"Confidence: {inst_confidence}")
            
            # Test individual checks
            print(f"\nIs instruction steps: {engine._is_instruction_steps(instructions)}")
            print(f"Is ingredient list: {engine._is_ingredient_list(instructions)}")
            print(f"Contains cooking words: {engine._contains_cooking_words(instructions)}")
        else:
            print("No recipe extracted")

if __name__ == "__main__":
    test_exact_instructions()
