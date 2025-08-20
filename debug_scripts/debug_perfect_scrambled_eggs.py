#!/usr/bin/env python3
"""
Debug Perfect Scrambled Eggs extraction
"""

import sys, os
sys.path.append('.')
import re
from cookbook_processing.atk_25th_visual_semantic_extractor import ATK25thVisualSemanticExtractor

def debug_perfect_scrambled_eggs():
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
    extractor = ATK25thVisualSemanticExtractor(pdf_path)
    
    # Get the actual page text
    import PyPDF2
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        page_207_text = reader.pages[206].extract_text()
        page_208_text = reader.pages[207].extract_text()
    
    print("=== DEBUGGING PAGE 207 ===")
    structure_207 = extractor.visual_detector.analyze_page_structure(page_207_text)
    print(f"Visual confidence: {structure_207['confidence_score']}")
    print(f"Has recipe: {structure_207['has_recipe']}")
    print(f"Title candidates: {[c['text'] for c in structure_207['title_candidates']]}")
    
    # Try to extract ingredients
    ingredients_207 = extractor._extract_ingredients_from_end(page_207_text)
    print(f"Ingredients from end: '{ingredients_207}'")
    
    # Try title extraction
    title_207 = extractor._extract_title_with_visual_cues(page_207_text, structure_207)
    print(f"Title extracted: '{title_207}'")
    
    print("\n=== DEBUGGING PAGE 208 ===")
    structure_208 = extractor.visual_detector.analyze_page_structure(page_208_text)
    print(f"Visual confidence: {structure_208['confidence_score']}")
    print(f"Has recipe: {structure_208['has_recipe']}")
    
    # Try to extract ingredients
    ingredients_208 = extractor._extract_ingredients_by_patterns(page_208_text)
    print(f"Ingredients patterns: '{ingredients_208}'")
    
    # Try to extract instructions
    instructions_208 = extractor._extract_numbered_steps(page_208_text)
    print(f"Instructions (cleaned): '{instructions_208}'")
    
    print("\n=== COMBINED INGREDIENTS ===")
    combined = ingredients_207 + '\n' + ingredients_208 if ingredients_207 and ingredients_208 else (ingredients_207 or ingredients_208)
    print(f"Combined: '{combined}'")
    
    # Test semantic validation
    if title_207 and combined and instructions_208:
        semantic_result = extractor.semantic_engine.validate_complete_recipe({
            'title': title_207,
            'ingredients': combined,
            'instructions': instructions_208
        })
        print(f"\n=== SEMANTIC VALIDATION ===")
        print(f"Valid: {semantic_result.is_valid_recipe}")
        print(f"Confidence: {semantic_result.confidence_score}")
        print(f"Errors: {semantic_result.validation_errors}")

if __name__ == "__main__":
    debug_perfect_scrambled_eggs()
