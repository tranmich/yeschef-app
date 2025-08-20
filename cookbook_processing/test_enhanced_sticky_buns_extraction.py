#!/usr/bin/env python3
"""
Test Enhanced Sticky Buns Multi-Page Extraction
==============================================

Tests the improved multi-page recipe detection specifically for the Sticky Buns recipe
that spans pages 100-107 in the ATK Teen cookbook.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from atk_teens_visual_semantic_extractor import TeenRecipeExtractor
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_sticky_buns_extraction():
    """Test the enhanced extraction on the specific sticky buns pages"""
    
    cookbook_path = r"d:\Mik\Downloads\Me Hungie\cookbook_processing\The Complete Cookbook for Teen - America's Test Kitchen Kids.pdf"
    
    print("🧪 Testing Enhanced Sticky Buns Multi-Page Extraction")
    print("=" * 60)
    
    # Initialize extractor
    extractor = TeenRecipeExtractor(cookbook_path)
    
    # Extract specifically from pages 100-107 (sticky buns range)
    print(f"📖 Extracting from Sticky Buns pages: 100-107")
    
    recipes = extractor.extract_from_page_range(
        start_page=100,
        end_page=107,
        max_recipes=5,  # Should find 1 multi-page recipe
        dry_run=False
    )
    
    print(f"\n📊 EXTRACTION RESULTS")
    print(f"   Recipes found: {len(recipes)}")
    print(f"   Pages processed: {extractor.stats['pages_processed']}")
    print(f"   Multi-page recipes in progress: {len(extractor.multi_page_recipes)}")
    
    # Analyze results
    if recipes:
        for i, recipe in enumerate(recipes, 1):
            print(f"\n🍞 RECIPE {i}: {recipe['title']}")
            print(f"   📄 Page(s): {recipe.get('page_number', 'Unknown')}")
            print(f"   📊 Visual confidence: {recipe.get('visual_confidence', 'N/A')}")
            print(f"   🧠 Semantic confidence: {recipe.get('semantic_confidence', 'N/A')}")
            print(f"   🔧 Extraction method: {recipe.get('extraction_method', 'N/A')}")
            
            if recipe.get('ingredients'):
                ingredient_lines = recipe['ingredients'].split('\n')
                print(f"   🥚 Ingredients ({len(ingredient_lines)} lines):")
                for line in ingredient_lines[:3]:  # Show first 3 lines
                    print(f"      • {line.strip()}")
                if len(ingredient_lines) > 3:
                    print(f"      ... and {len(ingredient_lines) - 3} more")
            
            if recipe.get('instructions'):
                instruction_lines = recipe['instructions'].split('\n')
                instruction_lines = [line.strip() for line in instruction_lines if line.strip()]
                print(f"   📝 Instructions ({len(instruction_lines)} lines):")
                for line in instruction_lines[:2]:  # Show first 2 lines
                    print(f"      • {line[:80]}{'...' if len(line) > 80 else ''}")
                if len(instruction_lines) > 2:
                    print(f"      ... and {len(instruction_lines) - 2} more steps")
    
    else:
        print("❌ No recipes found in the sticky buns range!")
        print("\n🔍 Checking multi-page recipes in progress:")
        for page_key, recipe_info in extractor.multi_page_recipes.items():
            print(f"   {page_key}: Pages {recipe_info.get('page_start', 'Unknown')}-{recipe_info.get('last_page', 'Unknown')}")
            print(f"      Title: {recipe_info['recipe_data'].get('title', 'No title')}")
            print(f"      Waiting for completion: {recipe_info.get('waiting_for_completion', 'Unknown')}")
    
    # Show extraction statistics
    print(f"\n📈 EXTRACTION STATISTICS")
    print(f"   Pages processed: {extractor.stats['pages_processed']}")
    print(f"   Recipe candidates found: {extractor.stats['recipe_candidates_found']}")
    print(f"   Pages with visual structure: {extractor.stats['pages_with_visual_structure']}")
    print(f"   Visual validations: {extractor.stats['visual_validations']}")
    print(f"   Semantic validations: {extractor.stats['semantic_validations']}")
    print(f"   Recipes validated: {extractor.stats['recipes_validated']}")
    
    # Show rejection reasons
    print(f"\n❌ REJECTION REASONS")
    for reason, count in extractor.rejection_reasons.items():
        if count > 0:
            print(f"   {reason}: {count}")
    
    return recipes

def analyze_page_by_page():
    """Analyze each page in the sticky buns range individually"""
    
    cookbook_path = r"d:\Mik\Downloads\Me Hungie\cookbook_processing\The Complete Cookbook for Teen - America's Test Kitchen Kids.pdf"
    
    print("\n🔍 PAGE-BY-PAGE ANALYSIS")
    print("=" * 40)
    
    extractor = TeenRecipeExtractor(cookbook_path)
    
    for page in range(100, 108):  # Pages 100-107
        print(f"\n📄 ANALYZING PAGE {page}")
        
        # Extract just this page
        recipes = extractor.extract_from_page_range(
            start_page=page,
            end_page=page,
            max_recipes=1,
            dry_run=True  # Don't save, just analyze
        )
        
        print(f"   Visual confidence: {extractor.visual_detector.last_confidence if hasattr(extractor.visual_detector, 'last_confidence') else 'Unknown'}")
        print(f"   Recipe candidates: {extractor.stats['recipe_candidates_found']}")
        print(f"   Is recipe page: {'Yes' if extractor.stats['pages_with_visual_structure'] > 0 else 'No'}")
        
        # Reset stats for next page
        extractor.stats = {
            'pages_processed': 0,
            'recipe_candidates_found': 0,
            'pages_with_visual_structure': 0,
            'visual_validations': 0,
            'semantic_validations': 0,
            'recipes_validated': 0
        }

if __name__ == "__main__":
    try:
        # Test main extraction
        recipes = test_sticky_buns_extraction()
        
        # Individual page analysis
        analyze_page_by_page()
        
        if recipes:
            print(f"\n✅ SUCCESS: Found {len(recipes)} recipe(s) in sticky buns range!")
        else:
            print(f"\n⚠️  ISSUE: No recipes found in sticky buns range. Check multi-page logic.")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
