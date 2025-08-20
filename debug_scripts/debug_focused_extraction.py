#!/usr/bin/env python3
"""
Focused debug for Perfect Scrambled Eggs extraction
"""

import sys, os
sys.path.append('.')
import logging
from cookbook_processing.atk_25th_visual_semantic_extractor import ATK25thVisualSemanticExtractor

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def debug_perfect_scrambled_eggs_extraction():
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
    extractor = ATK25thVisualSemanticExtractor(pdf_path)
    
    print("=== FOCUSED DEBUG: PERFECT SCRAMBLED EGGS ===")
    recipes = extractor.extract_recipes(max_recipes=1, start_page=207, end_page=208)
    
    print(f"\nFound {len(recipes)} recipes")
    for recipe in recipes:
        print(f"- {recipe.get('title', 'Unknown')}")

if __name__ == "__main__":
    debug_perfect_scrambled_eggs_extraction()
