#!/usr/bin/env python3

import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cookbook_processing'))

import PyPDF2
import re

def find_real_category_tocs():
    """Find the actual category TOC pages (not index or recipe pages)"""
    
    pdf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                           'cookbook_processing', 
                           "America's Test Kitchen 25th Ann - America's Test Kitchen.pdf")
    
    print("🔍 FINDING REAL CATEGORY TOC PAGES")
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
    
    try:
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            total_pages = len(reader.pages)
            
            print(f"📄 Scanning pages 50-1000 for real category TOCs...")
            
            # Scan a reasonable range for TOCs (not the index at the end)
            for page_idx in range(50, min(1000, total_pages)):
                try:
                    page = reader.pages[page_idx]
                    page_text = page.extract_text()
                    
                    # Check if this page is a real category TOC
                    for category in expected_categories:
                        if is_category_toc_page(page_text, category):
                            # Extract recipe titles from this TOC
                            recipe_titles = extract_clean_recipes_from_toc(page_text)
                            
                            if len(recipe_titles) >= 5:  # Must have at least 5 recipes to be a real TOC
                                category_tocs[category] = {
                                    'page': page_idx + 1,
                                    'recipes': recipe_titles,
                                    'count': len(recipe_titles)
                                }
                                
                                print(f"\n✅ Found {category} TOC on page {page_idx + 1}")
                                print(f"   📝 {len(recipe_titles)} recipes found")
                                
                                # Show first few recipes as examples
                                for i, recipe in enumerate(recipe_titles[:8]):
                                    print(f"      • {recipe}")
                                if len(recipe_titles) > 8:
                                    print(f"      ... and {len(recipe_titles) - 8} more")
                                
                                break  # Found this category, move to next page
                
                except Exception as e:
                    continue
            
            print(f"\n📊 REAL TOC DISCOVERY SUMMARY:")
            print("=" * 40)
            print(f"📋 Categories found: {len(category_tocs)}")
            total_recipes = sum(info['count'] for info in category_tocs.values())
            print(f"📝 Total recipes discovered: {total_recipes}")
            
            print(f"\n📍 REAL CATEGORY TOC LOCATIONS:")
            print("-" * 40)
            for category, info in category_tocs.items():
                print(f"📄 {category}: Page {info['page']} ({info['count']} recipes)")
            
            # Check for missing categories
            missing = set(expected_categories) - set(category_tocs.keys())
            if missing:
                print(f"\n⚠️ MISSING CATEGORIES:")
                for cat in missing:
                    print(f"   ❌ {cat}")
                    
                # Try manual search for missing categories
                print(f"\n🔍 MANUAL SEARCH FOR MISSING CATEGORIES:")
                for cat in missing:
                    found_pages = manual_search_category(reader, cat)
                    if found_pages:
                        print(f"   📄 {cat} mentions found on pages: {found_pages}")
            else:
                print(f"\n✅ ALL CATEGORIES FOUND!")
            
            return category_tocs
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return {}

def is_category_toc_page(text: str, category: str) -> bool:
    """Check if this page is a real TOC for the given category"""
    
    # Must contain the category name prominently
    if category.lower() not in text.lower():
        return False
    
    # Should NOT be a recipe page (no "Why This Recipe Works", "Serves", etc.)
    recipe_page_indicators = [
        "why this recipe works",
        "serves ",
        "total time:",
        "makes ",
        "ingredients:",
        "instructions:",
        "adjust oven rack",
        "heat oven to",
        "in large bowl",
        "in medium saucepan"
    ]
    
    text_lower = text.lower()
    if any(indicator in text_lower for indicator in recipe_page_indicators):
        return False
    
    # Should NOT be an index page (no page number references like "234-35")
    if re.search(r'\d{3,4}[-–]\d{2,4}', text):
        return False
    
    # Should NOT be extremely long (index pages are very long)
    if len(text) > 3000:
        return False
    
    # Should have multiple recipe-like titles
    lines = text.split('\n')
    recipe_like_count = 0
    
    for line in lines:
        line = line.strip()
        if 10 < len(line) < 80:  # Reasonable recipe title length
            if any(indicator in line.lower() for indicator in 
                  ['chicken', 'beef', 'pork', 'fish', 'pasta', 'rice', 'bread',
                   'soup', 'salad', 'sauce', 'roasted', 'grilled', 'baked',
                   'with', 'and', 'cookies', 'cake', 'pie']):
                recipe_like_count += 1
    
    # Must have at least 5 recipe-like lines
    return recipe_like_count >= 5

def extract_clean_recipes_from_toc(text: str) -> list:
    """Extract clean recipe titles from TOC text"""
    
    recipe_titles = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if 10 < len(line) < 80:  # Reasonable recipe title length
            # Filter out obvious non-recipes
            if not any(skip in line.lower() for skip in [
                'page', 'chapter', 'section', 'contents', 'acknowledgments', 
                'index', 'total time', 'serves', 'makes', 'why this recipe'
            ]):
                # Look for recipe indicators
                if any(indicator in line.lower() for indicator in 
                      ['chicken', 'beef', 'pork', 'fish', 'salmon', 'pasta', 'rice', 'bread',
                       'soup', 'salad', 'sauce', 'roasted', 'grilled', 'baked', 'braised',
                       'with', 'and', 'in', 'au', 'de', 'la', 'le', 'cookies', 'cake', 'pie',
                       'chocolate', 'vanilla', 'lemon', 'garlic', 'herbs', 'spiced', 'glazed']):
                    # Clean up the title
                    clean_title = re.sub(r'^\d+\.?\s*', '', line)  # Remove leading numbers
                    clean_title = re.sub(r'\s{2,}', ' ', clean_title)  # Normalize spaces
                    if len(clean_title) > 5:
                        recipe_titles.append(clean_title)
    
    return recipe_titles

def manual_search_category(reader, category: str) -> list:
    """Manually search for a category across the PDF"""
    
    found_pages = []
    total_pages = len(reader.pages)
    
    # Search in reasonable TOC range
    for page_idx in range(50, min(1000, total_pages)):
        try:
            page = reader.pages[page_idx]
            page_text = page.extract_text()
            
            if category.lower() in page_text.lower():
                # Quick check if it might be a TOC (not too long, has recipe-like content)
                if len(page_text) < 2000 and has_recipe_like_content(page_text):
                    found_pages.append(page_idx + 1)
        except Exception:
            continue
    
    return found_pages[:5]  # Return first 5 matches

def has_recipe_like_content(text: str) -> bool:
    """Check if text has recipe-like content"""
    
    recipe_words = ['chicken', 'beef', 'pork', 'fish', 'pasta', 'soup', 'salad', 'bread', 'cake']
    words_found = sum(1 for word in recipe_words if word in text.lower())
    return words_found >= 3

if __name__ == "__main__":
    find_real_category_tocs()
