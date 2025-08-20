#!/usr/bin/env python3

import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cookbook_processing'))

import PyPDF2
import re

def test_toc_pages():
    """Test TOC extraction on multiple pages to find the one with page numbers"""
    
    pdf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                           'cookbook_processing', 
                           "America's Test Kitchen 25th Ann - America's Test Kitchen.pdf")
    
    print("🔍 TESTING TOC ON MULTIPLE PAGES")
    print("=" * 50)
    
    # Test pages that might contain TOC with page numbers
    test_pages = [43, 44, 45, 46, 47, 48, 735, 736, 737, 738, 739, 740]
    
    try:
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            
            for page_num in test_pages:
                print(f"\n📄 PAGE {page_num + 1} ANALYSIS:")
                print("-" * 30)
                
                page = reader.pages[page_num]
                page_text = page.extract_text()
                
                print(f"📄 Text length: {len(page_text)} characters")
                
                # Look for page number patterns
                page_patterns = [
                    r'(\w+.*?)\s+(\d{3,4})',  # Recipe name followed by 3-4 digit page number
                    r'(\w+.*?)\s+\.+\s*(\d{3,4})',  # Recipe with dots and page number
                ]
                
                lines = page_text.split('\n')
                toc_entries = []
                
                for line in lines:
                    line = line.strip()
                    if len(line) < 10:
                        continue
                        
                    for pattern in page_patterns:
                        match = re.search(pattern, line)
                        if match:
                            try:
                                recipe_name = match.group(1).strip()
                                page_num_found = int(match.group(2))
                                
                                # Check if this looks like a recipe entry
                                if page_num_found > 100 and len(recipe_name) > 5:
                                    toc_entries.append((recipe_name, page_num_found))
                            except (ValueError, IndexError):
                                continue
                
                if toc_entries:
                    print(f"📋 Found {len(toc_entries)} TOC entries:")
                    for recipe_name, page_ref in toc_entries[:5]:  # Show first 5
                        print(f"  📝 '{recipe_name}' → Page {page_ref}")
                        
                        # Check if this includes our target recipe
                        if "mole-poblano" in recipe_name.lower() or "chicken in mole" in recipe_name.lower():
                            print(f"      ✅ TARGET FOUND!")
                else:
                    print("❌ No TOC entries with page numbers found")
                
                # Look specifically for Chicken in Mole-Poblano Sauce
                if "Chicken in Mole-Poblano Sauce" in page_text:
                    print("✅ Contains 'Chicken in Mole-Poblano Sauce' (but maybe without page number)")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_toc_pages()
