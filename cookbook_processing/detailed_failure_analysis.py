#!/usr/bin/env python3
"""Detailed analysis of failed extractions"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atk_teens_safe_extractor import ATKTeensExtractor, RecipeQualityValidator
import PyPDF2

def detailed_failure_analysis():
    """Analyze specific failing pages in detail"""
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\The Complete Cookbook for Teen - America's Test Kitchen Kids.pdf"
    extractor = ATKTeensExtractor(pdf_path)
    
    print("🔍 DETAILED FAILURE ANALYSIS")
    print("=" * 60)
    
    # Check page 95 which we know fails
    test_pages = [95, 90, 85, 80, 110, 115, 120]
    
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        
        for page_num in test_pages:
            if page_num >= len(reader.pages):
                continue
                
            print(f"\n{'='*50}")
            print(f"📄 ANALYZING PAGE {page_num}")
            print(f"{'='*50}")
            
            try:
                page = reader.pages[page_num - 1]  # Convert to 0-indexed
                text = page.extract_text()
                
                # Show first few lines of the page
                lines = text.split('\n')[:10]
                print(f"📋 Page content preview:")
                for i, line in enumerate(lines, 1):
                    if line.strip():
                        print(f"  {i:2d}: '{line.strip()[:60]}{'...' if len(line.strip()) > 60 else ''}'")
                
                # Check if it's detected as a recipe page
                is_recipe = extractor._is_recipe_page(text)
                print(f"\n🔍 Recipe detection: {is_recipe}")
                
                if is_recipe:
                    recipe_data = extractor._extract_recipe_from_page(text, page_num)
                    
                    if recipe_data:
                        print(f"\n📊 Extracted data:")
                        print(f"  Title: '{recipe_data.get('title', 'NO TITLE')}'")
                        print(f"  Category: '{recipe_data.get('category', 'NO CATEGORY')}'")
                        
                        # Test ingredients extraction step by step
                        print(f"\n🧪 Ingredients extraction test:")
                        has_start_cooking = 'START COOKING!' in text
                        print(f"  Has 'START COOKING!' marker: {has_start_cooking}")
                        
                        if has_start_cooking:
                            start_pos = text.find('START COOKING!')
                            content_before = text[:start_pos]
                            print(f"  Content before 'START COOKING!': {len(content_before)} characters")
                            
                            has_prepare = 'PREPARE INGREDIENTS' in content_before
                            print(f"  Has 'PREPARE INGREDIENTS': {has_prepare}")
                            
                            if not has_prepare:
                                # Check last 200 chars before START COOKING!
                                sample = content_before[-200:] if len(content_before) > 200 else content_before
                                print(f"  Sample content before START COOKING!:")
                                print(f"    '{sample}'")
                        
                        ingredients = recipe_data.get('ingredients', '')
                        instructions = recipe_data.get('instructions', '')
                        
                        print(f"\n📏 Final extracted content:")
                        print(f"  Ingredients: {len(ingredients)} chars")
                        if len(ingredients) < 200:
                            print(f"    Content: '{ingredients}'")
                        else:
                            print(f"    Sample: '{ingredients[:200]}...'")
                            
                        print(f"  Instructions: {len(instructions)} chars")
                        if len(instructions) < 200:
                            print(f"    Content: '{instructions}'")
                        else:
                            print(f"    Sample: '{instructions[:200]}...'")
                        
                        # Validation
                        validation = RecipeQualityValidator.validate_recipe_data(recipe_data)
                        print(f"\n✅ Validation: {validation['is_valid']} (Score: {validation['quality_score']}/8)")
                        
                        if not validation['is_valid']:
                            print(f"❌ Issues:")
                            for error in validation['errors']:
                                print(f"  • {error}")
                else:
                    print("❌ Not detected as recipe page")
                    
            except Exception as e:
                print(f"Error processing page {page_num}: {e}")
                
    print(f"\n{'='*60}")
    print("🎯 SUMMARY: This analysis helps identify why recipes are failing extraction")

if __name__ == "__main__":
    detailed_failure_analysis()
