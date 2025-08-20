#!/usr/bin/env python3
"""Simple analysis of rejected recipes"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atk_teens_safe_extractor import ATKTeensExtractor, RecipeQualityValidator
import PyPDF2

def simple_rejection_analysis():
    """Analyze a few specific pages to understand rejections"""
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\The Complete Cookbook for Teen - America's Test Kitchen Kids.pdf"
    extractor = ATKTeensExtractor(pdf_path)
    
    print("🔍 ANALYZING SPECIFIC REJECTED RECIPES")
    print("=" * 60)
    
    # Check some pages that might be rejected
    test_pages = [15, 25, 35, 45, 55, 65, 75, 85, 95, 105]  # Sample pages
    
    rejection_reasons = {}
    rejected_count = 0
    
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        
        for page_num in test_pages:
            if page_num >= len(reader.pages):
                continue
                
            try:
                page = reader.pages[page_num - 1]  # Convert to 0-indexed
                text = page.extract_text()
                
                # Check if it's detected as a recipe page
                is_recipe = extractor._is_recipe_page(text)
                print(f"\n📄 Page {page_num}: Recipe detected: {is_recipe}")
                
                if is_recipe:
                    recipe_data = extractor._extract_recipe_from_page(text, page_num)
                    
                    if recipe_data:
                        validation = RecipeQualityValidator.validate_recipe_data(recipe_data)
                        
                        print(f"   Title: '{recipe_data.get('title', 'NO TITLE')[:50]}...'")
                        print(f"   Valid: {validation['is_valid']} (Score: {validation['quality_score']}/8)")
                        
                        if not validation['is_valid']:
                            rejected_count += 1
                            print(f"   ❌ REJECTION DETAILS:")
                            
                            # Field analysis
                            field_scores = validation.get('field_scores', {})
                            ingredients_len = len(recipe_data.get('ingredients', ''))
                            instructions_len = len(recipe_data.get('instructions', ''))
                            
                            print(f"     • Title: {field_scores.get('title', 0)}/1")
                            print(f"     • Category: {field_scores.get('category', 0)}/1")
                            print(f"     • Ingredients: {field_scores.get('ingredients', 0)}/2 ({ingredients_len} chars)")
                            print(f"     • Instructions: {field_scores.get('instructions', 0)}/2 ({instructions_len} chars)")
                            
                            # Show issues
                            if validation['errors']:
                                print(f"     Errors: {validation['errors']}")
                            
                            # Sample content for debugging
                            if ingredients_len < 100:
                                print(f"     Ingredients sample: '{recipe_data.get('ingredients', '')}'")
                            if instructions_len < 100:
                                print(f"     Instructions sample: '{recipe_data.get('instructions', '')[:200]}...'")
                        else:
                            print(f"   ✅ ACCEPTED")
                            
            except Exception as e:
                print(f"   Error processing page {page_num}: {e}")
                continue
    
    # Now let's check the overall extraction to see total stats
    print(f"\n📊 RUNNING QUICK EXTRACTION FOR OVERALL STATS...")
    recipes = extractor.extract_recipes(max_recipes=20)  # Just get first 20
    stats = extractor.extraction_stats
    
    print(f"\n📈 SAMPLE EXTRACTION STATS (First 20 found):")
    print(f"  Pages processed: {stats['pages_processed']}")
    print(f"  Recipes found: {stats['recipes_found']}")
    print(f"  Recipes validated: {stats['recipes_validated']}")
    print(f"  Rejection rate: {((stats['recipes_found'] - stats['recipes_validated'])/stats['recipes_found'])*100:.1f}%")

if __name__ == "__main__":
    simple_rejection_analysis()
