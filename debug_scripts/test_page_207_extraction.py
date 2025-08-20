#!/usr/bin/env python3
"""
Simple test to see what's extracted from page 207
"""

import sys, os
sys.path.append('.')
import PyPDF2
from cookbook_processing.atk_25th_visual_semantic_extractor import ATK25thVisualSemanticExtractor

def test_page_207_extraction():
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
    extractor = ATK25thVisualSemanticExtractor(pdf_path)
    
    # Get page 207 text
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        page_207_text = reader.pages[206].extract_text()
    
    # Analyze structure
    structure = extractor.visual_detector.analyze_page_structure(page_207_text)
    print(f"Visual confidence: {structure['confidence_score']}")
    print(f"Has recipe: {structure['has_recipe']}")
    
    # Try to extract recipe
    recipe_candidate = extractor._extract_recipe_visually(page_207_text, 207, structure)
    
    if recipe_candidate:
        print(f"\n=== RECIPE EXTRACTED ===")
        print(f"Title: {recipe_candidate.get('title', 'None')}")
        print(f"Has ingredients: {bool(recipe_candidate.get('ingredients'))}")
        print(f"Has instructions: {bool(recipe_candidate.get('instructions'))}")
        
        if recipe_candidate.get('instructions'):
            print(f"Instructions preview: {recipe_candidate['instructions'][:200]}...")
            
            # Test instruction classification
            instruction_class = extractor.semantic_engine.classify_content_type(recipe_candidate['instructions'])
            print(f"Instruction classification: {instruction_class}")
    else:
        print("No recipe candidate extracted")

if __name__ == "__main__":
    test_page_207_extraction()
