#!/usr/bin/env python3

import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cookbook_processing'))

import PyPDF2
import re

def build_recipe_mapping():
    """Build recipe title to page mapping by combining TOC extraction with forward searching"""
    
    pdf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                           'cookbook_processing', 
                           "America's Test Kitchen 25th Ann - America's Test Kitchen.pdf")
    
    print("🔍 BUILDING RECIPE MAPPING")
    print("=" * 50)
    
    recipe_mapping = {}
    
    try:
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            
            # Step 1: Extract recipe titles from TOC page 738
            print("📋 Step 1: Extract recipe titles from TOC (page 738)")
            page_738 = reader.pages[737]  # 0-indexed
            toc_text = page_738.extract_text()
            
            # Extract recipe titles from TOC
            toc_lines = toc_text.split('\n')
            recipe_titles = []
            
            for line in toc_lines:
                line = line.strip()
                if len(line) > 5 and len(line) < 100:  # Reasonable recipe title length
                    # Filter out obvious non-recipes
                    if not any(skip in line.lower() for skip in ['page', 'chapter', 'section', 'contents']):
                        recipe_titles.append(line)
            
            print(f"📝 Found {len(recipe_titles)} potential recipe titles in TOC:")
            for title in recipe_titles[:10]:  # Show first 10
                print(f"  • {title}")
            
            # Step 2: Search for each recipe title in the PDF
            print(f"\n🔍 Step 2: Search for recipe titles starting from page 750")
            search_start = 750  # Start searching after TOC area
            search_end = min(len(reader.pages), 1000)  # Limit search range
            
            for title in recipe_titles[:5]:  # Test with first 5 recipes
                print(f"\n🔍 Searching for: '{title}'")
                
                for page_idx in range(search_start - 1, search_end):
                    try:
                        page = reader.pages[page_idx]
                        page_text = page.extract_text()
                        
                        # Look for the recipe title in various forms
                        if title in page_text:
                            print(f"✅ Found '{title}' on page {page_idx + 1}")
                            recipe_mapping[title.lower()] = page_idx + 1
                            break
                        
                        # Try without special characters
                        title_simple = re.sub(r'[^\w\s]', '', title)
                        if title_simple in page_text:
                            print(f"✅ Found '{title}' (simplified) on page {page_idx + 1}")
                            recipe_mapping[title.lower()] = page_idx + 1
                            break
                            
                    except Exception:
                        continue
                else:
                    print(f"❌ Could not find '{title}' in search range")
            
            print(f"\n📋 RECIPE MAPPING RESULTS:")
            print("=" * 40)
            for title, page_num in recipe_mapping.items():
                print(f"📝 '{title}' → Page {page_num}")
            
            # Test our specific case
            target_recipe = "Chicken in Mole-Poblano Sauce"
            if target_recipe.lower() in recipe_mapping:
                mapped_page = recipe_mapping[target_recipe.lower()]
                print(f"\n✅ SUCCESS: '{target_recipe}' mapped to page {mapped_page}")
            else:
                print(f"\n❌ Target recipe '{target_recipe}' not found in mapping")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    build_recipe_mapping()
