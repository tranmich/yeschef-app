#!/usr/bin/env python3

import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cookbook_processing'))

import PyPDF2

def test_bookmark_extraction():
    """Test PDF bookmark extraction with detailed debugging"""
    
    pdf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                           'cookbook_processing', 
                           "America's Test Kitchen 25th Ann - America's Test Kitchen.pdf")
    
    print("🔍 TESTING BOOKMARK EXTRACTION")
    print("=" * 50)
    print(f"📄 PDF Path: {pdf_path}")
    
    try:
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            
            print(f"📄 Total pages: {len(reader.pages)}")
            
            if reader.outline:
                print("📋 Bookmarks found! Analyzing...")
                
                def test_parse_bookmarks(bookmarks, level=0):
                    count = 0
                    for item in bookmarks:
                        if isinstance(item, list):
                            count += test_parse_bookmarks(item, level + 1)
                        else:
                            count += 1
                            indent = "  " * level
                            title = item.title
                            
                            # Test page extraction methods
                            page_num = None
                            method_used = "none"
                            
                            # Method 1: Direct page access
                            try:
                                if hasattr(item, 'page') and item.page is not None:
                                    page_num = reader.pages.index(item.page) + 1
                                    method_used = "direct_page"
                            except Exception as e:
                                pass
                            
                            # Method 2: Destination access
                            if page_num is None:
                                try:
                                    if hasattr(item, 'destination') and item.destination:
                                        dest = item.destination
                                        # Try to resolve destination
                                        if isinstance(dest, list) and len(dest) > 0:
                                            page_ref = dest[0]
                                            # If it's an indirect reference, resolve it
                                            if hasattr(page_ref, 'idnum'):
                                                # Find the page index by iterating through pages
                                                for i, page in enumerate(reader.pages):
                                                    if hasattr(page, 'idnum') and page.idnum == page_ref.idnum:
                                                        page_num = i + 1
                                                        method_used = "destination_idnum"
                                                        break
                                            else:
                                                # Try direct page lookup
                                                try:
                                                    page_num = reader.pages.index(page_ref) + 1
                                                    method_used = "destination_direct"
                                                except ValueError:
                                                    pass
                                except Exception as e:
                                    pass
                            
                            # Method 3: Try named destinations
                            if page_num is None:
                                try:
                                    # Sometimes destinations are named or referenced differently
                                    if hasattr(reader, 'named_destinations'):
                                        for name, dest in reader.named_destinations.items():
                                            if name.lower() == title.lower().replace(' ', '_'):
                                                if isinstance(dest, list) and len(dest) > 0:
                                                    page_ref = dest[0]
                                                    page_num = reader.pages.index(page_ref) + 1
                                                    method_used = "named_destination"
                                                    break
                                except Exception as e:
                                    pass
                            
                            # Check if this is a recipe-like title
                            is_recipe = check_recipe_indicators(title, level)
                            
                            print(f"{indent}📝 '{title}' → Page {page_num} ({method_used}) - Recipe: {is_recipe}")
                            
                            if count >= 20:  # Limit output for debugging
                                break
                    
                    return count
                
                total = test_parse_bookmarks(reader.outline)
                print(f"\n📊 Processed {total} bookmarks")
                
            else:
                print("❌ No bookmarks found")
                
    except Exception as e:
        print(f"❌ Error: {e}")

def check_recipe_indicators(title: str, level: int) -> bool:
    """Check if title looks like a recipe"""
    
    # Skip obvious non-recipes
    non_recipe_titles = [
        'title page', 'copyright', 'contents', 'acknowledgments', 'welcome',
        'our story', 'appetizers & drinks', 'eggs & breakfast', 'soups & stews',
        'salads', 'pasta', 'vegetables', 'meat', 'poultry', 'seafood', 'desserts',
        'baking', 'index', 'about', 'introduction'
    ]
    
    title_lower = title.lower()
    
    # Skip chapter/section headers
    if any(non_recipe in title_lower for non_recipe in non_recipe_titles):
        return False
    
    # Skip very short titles
    if len(title) < 5:
        return False
    
    # Must be reasonable recipe title length
    if len(title) > 100:
        return False
    
    # Look for recipe indicators
    recipe_indicators = [
        'chicken', 'beef', 'pork', 'fish', 'salmon', 'pasta', 'rice', 'bread',
        'soup', 'salad', 'sauce', 'roasted', 'grilled', 'baked', 'braised',
        'cake', 'pie', 'cookies', 'chocolate', 'vanilla', 'lemon', 'garlic',
        'with', 'and', 'in', 'style', 'glazed', 'stuffed', 'perfect', 'easy'
    ]
    
    # Must contain recipe-like words
    return any(indicator in title_lower for indicator in recipe_indicators)

if __name__ == "__main__":
    test_bookmark_extraction()
