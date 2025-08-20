#!/usr/bin/env python3
"""Analyze rejected recipes to understand validation failures"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atk_teens_safe_extractor import ATKTeensExtractor, RecipeQualityValidator
import PyPDF2

def analyze_rejected_recipes():
    """Analyze recipes that were found but rejected during validation"""
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\The Complete Cookbook for Teen - America's Test Kitchen Kids.pdf"
    extractor = ATKTeensExtractor(pdf_path)
    
    print("🔍 ANALYZING REJECTED RECIPES")
    print("=" * 60)
    
    # Extract recipes but analyze all of them
    recipes = extractor.extract_recipes(max_recipes=None, analyze_rejected=True)
    
    # Get extraction stats
    stats = extractor.extraction_stats
    total_found = stats['recipes_found']
    validated = stats['recipes_validated']
    rejected = total_found - validated
    
    print(f"\n📊 SUMMARY:")
    print(f"  Total recipes found: {total_found}")
    print(f"  Successfully validated: {validated}")
    print(f"  Rejected recipes: {rejected}")
    print(f"  Rejection rate: {(rejected/total_found)*100:.1f}%")
    
    # Analyze rejection reasons
    rejection_reasons = {}
    
    # Re-run extraction to get detailed rejection analysis
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        
        rejected_count = 0
        print(f"\n🔍 DETAILED REJECTION ANALYSIS:")
        print("=" * 60)
        
        for page_num in range(len(reader.pages)):
            if rejected_count >= 20:  # Limit to first 20 rejections for readability
                break
                
            try:
                page = reader.pages[page_num]
                text = page.extract_text()
                
                if extractor._is_recipe_page(text):
                    recipe_data = extractor._extract_recipe_from_page(text, page_num + 1)
                    
                    if recipe_data:
                        validation = RecipeQualityValidator.validate_recipe_data(recipe_data)
                        
                        if not validation['is_valid']:
                            rejected_count += 1
                            print(f"\n❌ REJECTED RECIPE #{rejected_count} (Page {page_num + 1})")
                            print(f"   Title: '{recipe_data.get('title', 'NO TITLE')}'")
                            print(f"   Category: '{recipe_data.get('category', 'NO CATEGORY')}'")
                            print(f"   Quality Score: {validation['quality_score']}/8")
                            
                            # Analyze specific issues
                            print(f"   📋 Field Analysis:")
                            field_scores = validation.get('field_scores', {})
                            print(f"     • Title: {field_scores.get('title', 0)}/1 {'✅' if field_scores.get('title', 0) > 0 else '❌'}")
                            print(f"     • Category: {field_scores.get('category', 0)}/1 {'✅' if field_scores.get('category', 0) > 0 else '❌'}")
                            print(f"     • Ingredients: {field_scores.get('ingredients', 0)}/2 {'✅' if field_scores.get('ingredients', 0) > 0 else '❌'}")
                            print(f"     • Instructions: {field_scores.get('instructions', 0)}/2 {'✅' if field_scores.get('instructions', 0) > 0 else '❌'}")
                            
                            # Show actual content lengths
                            ingredients_len = len(recipe_data.get('ingredients', ''))
                            instructions_len = len(recipe_data.get('instructions', ''))
                            print(f"   📏 Content Lengths:")
                            print(f"     • Ingredients: {ingredients_len} characters")
                            print(f"     • Instructions: {instructions_len} characters")
                            
                            # Track rejection reasons
                            if validation['errors']:
                                for error in validation['errors']:
                                    reason = error.split(':')[0] if ':' in error else error
                                    rejection_reasons[reason] = rejection_reasons.get(reason, 0) + 1
                            
                            # Show sample content if very short
                            if ingredients_len < 50:
                                print(f"   🔍 Ingredients sample: '{recipe_data.get('ingredients', '')[:100]}...'")
                            if instructions_len < 50:
                                print(f"   🔍 Instructions sample: '{recipe_data.get('instructions', '')[:100]}...'")
                            
            except Exception as e:
                continue
    
    # Summary of rejection reasons
    print(f"\n📊 REJECTION REASONS SUMMARY:")
    print("=" * 40)
    for reason, count in sorted(rejection_reasons.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / rejected) * 100 if rejected > 0 else 0
        print(f"  {reason}: {count} times ({percentage:.1f}%)")

if __name__ == "__main__":
    analyze_rejected_recipes()
