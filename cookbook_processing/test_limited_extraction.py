#!/usr/bin/env python3
"""Test the improved extractor on first 20 recipes"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atk_teens_safe_extractor import ATKTeensExtractor

def test_limited_extraction():
    """Test the improved extraction on first 20 recipes found"""
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\The Complete Cookbook for Teen - America's Test Kitchen Kids.pdf"
    
    # Create extractor
    extractor = ATKTeensExtractor(pdf_path)
    
    print("🧪 TESTING IMPROVED EXTRACTION - LIMITED TO 20 RECIPES")
    print("=" * 60)
    
    # Extract first 20 recipes found
    recipes = extractor.extract_recipes(max_recipes=20)
    
    print(f"\n📊 EXTRACTION RESULTS:")
    print(f"  📄 Pages processed: {extractor.extraction_stats['pages_processed']}")
    print(f"  🔍 Recipe candidates found: {extractor.extraction_stats['recipes_found']}")
    print(f"  ✅ Recipes validated: {extractor.extraction_stats['recipes_validated']}")
    print(f"  🔄 Duplicates found: {extractor.extraction_stats['duplicates_found']}")
    print(f"  ❌ Errors: {extractor.extraction_stats['errors_encountered']}")
    
    print(f"\n📝 EXTRACTED RECIPES:")
    for i, recipe in enumerate(recipes, 1):
        print(f"  {i:2d}. {recipe['title']} (Page {recipe['page_number']})")
        print(f"      Category: {recipe['category']}")
        print(f"      Ingredients: {len(recipe['ingredients'])} chars")
        print(f"      Instructions: {len(recipe['instructions'])} chars")
        print(f"      Valid: {recipe['validation']['is_valid']}")
        print()

if __name__ == "__main__":
    test_limited_extraction()
