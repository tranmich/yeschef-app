#!/usr/bin/env python3
"""
Debug Page 48 Breakfast Sandwiches
=================================

Analyzes what's being extracted from page 48 that validates as a recipe.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import PyPDF2
from atk_teens_visual_semantic_extractor import TeenRecipeExtractor

def debug_page_48():
    """Debug page 48 breakfast sandwiches extraction"""
    
    cookbook_path = r"d:\Mik\Downloads\Me Hungie\cookbook_processing\The Complete Cookbook for Teen - America's Test Kitchen Kids.pdf"
    
    print("🔍 DEBUGGING PAGE 48 BREAKFAST SANDWICHES")
    print("=" * 50)
    
    extractor = TeenRecipeExtractor(cookbook_path)
    
    with open(cookbook_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        page_48 = reader.pages[47]  # 0-indexed
        page_text = page_48.extract_text()
        
        print("📄 PAGE 48 RAW TEXT:")
        print("-" * 30)
        print(page_text[:800])
        print("\n...")
        
        # Visual analysis
        visual_analysis = extractor.visual_detector.analyze_page_structure(page_text, 48)
        print(f"\n👁️ VISUAL ANALYSIS:")
        print(f"  Is recipe page: {visual_analysis['is_recipe_page']}")
        print(f"  Confidence: {visual_analysis['confidence_score']}")
        print(f"  Recipe structure keys: {list(visual_analysis.get('recipe_structure', {}).keys())}")
        
        # Show the recipe structure in detail
        recipe_structure = visual_analysis.get('recipe_structure', {})
        print(f"\n📊 RECIPE STRUCTURE DETAIL:")
        for key, value in recipe_structure.items():
            if isinstance(value, list) and value:
                print(f"  {key}: {len(value)} items")
                for i, item in enumerate(value[:2]):  # Show first 2 items
                    if isinstance(item, dict):
                        print(f"    [{i}]: {item}")
                    else:
                        print(f"    [{i}]: {repr(str(item)[:50])}...")
            elif isinstance(value, str) and value:
                print(f"  {key}: {repr(value[:100])}...")
            else:
                print(f"  {key}: {value}")
        
        # Try to extract recipe content
        recipe_data = extractor._extract_recipe_with_visual_guidance(visual_analysis, page_text)
        print(f"\n🍽️ RECIPE DATA EXTRACTION:")
        if recipe_data:
            for key, value in recipe_data.items():
                if isinstance(value, str) and value:
                    print(f"  {key}: {repr(value[:100])}...")
                else:
                    print(f"  {key}: {value}")
        else:
            print("  ❌ No recipe data extracted")

if __name__ == "__main__":
    debug_page_48()
