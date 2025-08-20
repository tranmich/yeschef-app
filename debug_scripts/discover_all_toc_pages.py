#!/usr/bin/env python3

import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cookbook_processing'))

import PyPDF2
import re

def discover_all_toc_pages():
    """Discover all TOC pages for each category in the ATK 25th Anniversary cookbook"""
    
    pdf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                           'cookbook_processing', 
                           "America's Test Kitchen 25th Ann - America's Test Kitchen.pdf")
    
    print("🔍 DISCOVERING ALL CATEGORY TOC PAGES")
    print("=" * 60)
    
    # Expected categories from user
    expected_categories = [
        "Appetizers & Drinks",
        "Eggs & Breakfast", 
        "Soups & Stews",
        "Salads",
        "Pasta, Noodles & Dumplings",
        "Poultry",
        "Meat", 
        "Fish & Seafood",
        "Vegetarian",
        "Grilling",
        "Sides",
        "Bread & Pizza",
        "Cookies"
    ]
    
    category_tocs = {}
    total_recipes_found = 0
    
    try:
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            total_pages = len(reader.pages)
            
            print(f"📄 Scanning {total_pages} pages for category TOCs...")
            
            # Scan the entire book for TOC pages
            for page_idx in range(total_pages):
                try:
                    page = reader.pages[page_idx]
                    page_text = page.extract_text()
                    
                    # Check if this page contains a category TOC
                    category_found = None
                    for category in expected_categories:
                        # Look for category name in various forms
                        if category.lower() in page_text.lower():
                            # Additional validation - must have recipe-like content
                            if has_recipe_list_content(page_text):
                                category_found = category
                                break
                    
                    if category_found:
                        # Extract recipe titles from this TOC
                        recipe_titles = extract_recipes_from_toc_text(page_text)
                        
                        if len(recipe_titles) > 0:
                            category_tocs[category_found] = {
                                'page': page_idx + 1,
                                'recipes': recipe_titles,
                                'count': len(recipe_titles)
                            }
                            total_recipes_found += len(recipe_titles)
                            
                            print(f"\n✅ Found {category_found} TOC on page {page_idx + 1}")
                            print(f"   📝 {len(recipe_titles)} recipes found")
                            
                            # Show first few recipes as examples
                            for i, recipe in enumerate(recipe_titles[:5]):
                                print(f"      • {recipe}")
                            if len(recipe_titles) > 5:
                                print(f"      ... and {len(recipe_titles) - 5} more")
                
                except Exception as e:
                    continue
            
            print(f"\n📊 DISCOVERY SUMMARY:")
            print("=" * 40)
            print(f"📋 Categories found: {len(category_tocs)}")
            print(f"📝 Total recipes discovered: {total_recipes_found}")
            
            print(f"\n📍 CATEGORY TOC LOCATIONS:")
            print("-" * 40)
            for category, info in category_tocs.items():
                print(f"📄 {category}: Page {info['page']} ({info['count']} recipes)")
            
            # Check for missing categories
            missing = set(expected_categories) - set(category_tocs.keys())
            if missing:
                print(f"\n⚠️ MISSING CATEGORIES:")
                for cat in missing:
                    print(f"   ❌ {cat}")
            else:
                print(f"\n✅ ALL CATEGORIES FOUND!")
            
            return category_tocs
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return {}

def has_recipe_list_content(text: str) -> bool:
    """Check if text contains recipe list content"""
    
    # Look for recipe indicators
    recipe_indicators = [
        'chicken', 'beef', 'pork', 'fish', 'salmon', 'pasta', 'rice', 'bread',
        'soup', 'salad', 'sauce', 'roasted', 'grilled', 'baked', 'braised',
        'with', 'and', 'in', 'au', 'de', 'la', 'le', 'cookies', 'cake', 'pie'
    ]
    
    lines = text.split('\n')
    recipe_like_lines = 0
    
    for line in lines:
        line = line.strip()
        if 5 < len(line) < 100:  # Reasonable recipe title length
            if any(indicator in line.lower() for indicator in recipe_indicators):
                recipe_like_lines += 1
    
    # Must have at least 3 recipe-like lines to be considered a TOC
    return recipe_like_lines >= 3

def extract_recipes_from_toc_text(text: str) -> list:
    """Extract recipe titles from TOC text"""
    
    recipe_titles = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if 5 < len(line) < 100:  # Reasonable recipe title length
            # Filter out obvious non-recipes
            if not any(skip in line.lower() for skip in ['page', 'chapter', 'section', 'contents', 'acknowledgments', 'index']):
                # Look for recipe indicators
                if any(indicator in line.lower() for indicator in 
                      ['chicken', 'beef', 'pork', 'fish', 'salmon', 'pasta', 'rice', 'bread',
                       'soup', 'salad', 'sauce', 'roasted', 'grilled', 'baked', 'braised',
                       'with', 'and', 'in', 'au', 'de', 'la', 'le', 'cookies', 'cake', 'pie',
                       'chocolate', 'vanilla', 'lemon', 'garlic', 'herbs', 'spiced', 'glazed']):
                    recipe_titles.append(line)
    
    return recipe_titles

if __name__ == "__main__":
    discover_all_toc_pages()
