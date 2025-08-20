#!/usr/bin/env python3
"""
Test the text cleanup and semantic validation
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cookbook_processing.atk_25th_simplified_intelligent_extractor import ATK25thSimplifiedIntelligentExtractor
from core_systems.semantic_recipe_engine import SemanticRecipeEngine

def test_cleanup_and_validation():
    """Test text cleanup and semantic validation"""
    
    # Original broken instructions
    broken_instructions = """1. Process al l but 1 cup of beans wi th broth and sal t in food processor unti l smooth, about 15 seconds, scr aping down sides of workbowl wi th rubber spatula i f necessary . Add r emaining beans and pulse unti l slightly chunky , about 10 pulses.
2. Cook bacon in 12-inch nonstick ski llet over medium heat unti l bacon just begins to br own and most of f at has r ender ed, about 4 minutes. T ransfer to smal l bowl l ined wi th strainer; discar d bacon and add 1 tablespoon f at back to ski llet. Increase heat to medium- high; add onion, jalapeño , and cumin; and cook unti l softened and just starting to br own, 3 to 5 minutes. Stir in garl ic and cook unti l fragrant, about 30 seconds. R educe heat to medium, stir in pur eed beans, and cook unti l thick and cr eamy, 4 to 6 minutes. Of f heat, stir in cilantro and l ime juice."""

    print("=== Testing Text Cleanup ===")
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
    extractor = ATK25thSimplifiedIntelligentExtractor(pdf_path)
    
    # Test cleanup
    cleaned_instructions = extractor._clean_pdf_text(broken_instructions)
    
    print("BEFORE cleanup:")
    print(broken_instructions)
    print("\nAFTER cleanup:")
    print(cleaned_instructions)
    
    print("\n=== Word Count Analysis ===")
    broken_words = broken_instructions.split()
    cleaned_words = cleaned_instructions.split()
    print(f"Broken text: {len(broken_words)} words")
    print(f"Cleaned text: {len(cleaned_words)} words")
    
    # Look for remaining broken words
    import re
    broken_word_pattern = r'\b\w \w\b'  # Pattern for broken words like "al l" 
    broken_matches = re.findall(broken_word_pattern, cleaned_instructions)
    if broken_matches:
        print(f"Remaining broken words: {broken_matches}")
    else:
        print("No obvious broken words remaining")
    
    # Test semantic validation on cleaned text
    print("\n=== Testing Semantic Validation ===")
    engine = SemanticRecipeEngine()
    
    print("\nValidating BROKEN text:")
    broken_type, broken_conf = engine.classify_content_type(broken_instructions)
    print(f"Type: {broken_type}, confidence: {broken_conf}")
    
    print("\nValidating CLEANED text:")
    cleaned_type, cleaned_conf = engine.classify_content_type(cleaned_instructions)
    print(f"Type: {cleaned_type}, confidence: {cleaned_conf}")

if __name__ == "__main__":
    test_cleanup_and_validation()
