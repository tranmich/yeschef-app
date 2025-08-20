#!/usr/bin/env python3
"""
Debug Page 101 Content Extraction
=================================

Tests what happens when we try to extract content from page 101 specifically.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import PyPDF2
from atk_teens_visual_semantic_extractor import TeenRecipeExtractor

def debug_page_101():
    """Debug page 101 content extraction"""
    
    cookbook_path = r"d:\Mik\Downloads\Me Hungie\cookbook_processing\The Complete Cookbook for Teen - America's Test Kitchen Kids.pdf"
    
    print("🔍 DEBUGGING PAGE 101 CONTENT EXTRACTION")
    print("=" * 50)
    
    extractor = TeenRecipeExtractor(cookbook_path)
    
    with open(cookbook_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        page_101 = reader.pages[100]  # 0-indexed
        page_text = page_101.extract_text()
        
        print("📄 PAGE 101 RAW TEXT:")
        print("-" * 30)
        print(page_text[:500])
        print("\n...")
        
        # Visual analysis
        visual_analysis = extractor.visual_detector.analyze_page_structure(page_text, 101)
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
        
        # Try the multi-page continuation check
        print(f"\n🔄 MULTI-PAGE CONTINUATION CHECK:")
        
        # Simulate having a multi-page recipe from page 100
        extractor.multi_page_recipes = {
            'page_100': {
                'recipe_data': {'title': 'Sticky Buns', 'ingredients': '', 'instructions': ''},
                'page_start': 100,
                'waiting_for_completion': True,
                'last_page': 100
            }
        }
        
        print(f"  Multi-page recipes before: {list(extractor.multi_page_recipes.keys())}")
        
        # Check continuation
        extractor._check_multi_page_continuation(page_text, 101)
        
        print(f"  Multi-page recipes after: {list(extractor.multi_page_recipes.keys())}")
        
        # Show the updated recipe data
        if 'page_100' in extractor.multi_page_recipes:
            updated_recipe = extractor.multi_page_recipes['page_100']['recipe_data']
            print(f"\n📝 UPDATED RECIPE DATA:")
            for key, value in updated_recipe.items():
                if isinstance(value, str) and value:
                    print(f"  {key}: {repr(value[:100])}...")
                else:
                    print(f"  {key}: {value}")

if __name__ == "__main__":
    debug_page_101()
