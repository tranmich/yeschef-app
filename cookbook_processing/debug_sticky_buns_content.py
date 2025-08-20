#!/usr/bin/env python3
"""
Debug Sticky Buns Page Content
=============================

Shows exactly what content is being extracted from each page in the sticky buns range.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import PyPDF2
from atk_teens_visual_semantic_extractor import VisualStructureDetector

def debug_page_content():
    """Debug what content is extracted from each sticky buns page"""
    
    cookbook_path = r"d:\Mik\Downloads\Me Hungie\cookbook_processing\The Complete Cookbook for Teen - America's Test Kitchen Kids.pdf"
    
    print("🔍 DEBUGGING STICKY BUNS PAGE CONTENT")
    print("=" * 50)
    
    visual_detector = VisualStructureDetector()
    
    with open(cookbook_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        for page_num in range(99, 107):  # Pages 100-107 (0-indexed)
            try:
                page = reader.pages[page_num]
                page_text = page.extract_text()
                
                print(f"\n📄 PAGE {page_num + 1}")
                print("-" * 30)
                
                # Show first 300 characters of raw text
                print(f"RAW TEXT (first 300 chars):")
                print(repr(page_text[:300]))
                
                # Visual analysis
                visual_analysis = visual_detector.analyze_page_structure(page_text, page_num + 1)
                print(f"\nVISUAL ANALYSIS:")
                print(f"  Is recipe page: {visual_analysis['is_recipe_page']}")
                print(f"  Confidence: {visual_analysis['confidence_score']}")
                print(f"  Structure indicators: {visual_analysis.get('structure_indicators', {})}")
                
                # Recipe structure if it's a recipe page
                if visual_analysis['is_recipe_page']:
                    recipe_structure = visual_analysis.get('recipe_structure', {})
                    print(f"\nRECIPE STRUCTURE:")
                    for key, value in recipe_structure.items():
                        if isinstance(value, str) and value:
                            print(f"  {key}: {repr(value[:100])}...")
                        elif isinstance(value, list) and value:
                            first_item = str(value[0]) if value else ""
                            print(f"  {key}: {len(value)} items - {repr(first_item[:50])}...")
                        else:
                            print(f"  {key}: {value}")
                
            except Exception as e:
                print(f"❌ Error processing page {page_num + 1}: {e}")

if __name__ == "__main__":
    debug_page_content()
