#!/usr/bin/env python3
"""
Extract PDF bookmarks and navigation structure
"""

import PyPDF2
import os

def extract_pdf_bookmarks():
    """Extract PDF bookmarks and navigation structure"""
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return
    
    try:
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            
            print("📚 PDF BOOKMARKS AND NAVIGATION ANALYSIS")
            print("=" * 60)
            print(f"📄 Total pages: {len(reader.pages)}")
            
            # Check for bookmarks/outlines
            if reader.outline:
                print(f"📋 Bookmarks found: {len(reader.outline)} top-level items")
                print("\n🔗 BOOKMARK STRUCTURE:")
                print("-" * 40)
                
                def print_bookmarks(bookmarks, level=0):
                    """Recursively print bookmark structure"""
                    count = 0
                    for item in bookmarks:
                        if isinstance(item, list):
                            # Nested bookmarks
                            count += print_bookmarks(item, level + 1)
                        else:
                            # Single bookmark
                            indent = "  " * level
                            title = item.title
                            
                            # Get destination page
                            try:
                                if hasattr(item, 'page') and item.page:
                                    page_num = reader.pages.index(item.page) + 1
                                    print(f"{indent}📝 {title} → Page {page_num}")
                                else:
                                    print(f"{indent}📝 {title} → (No page reference)")
                            except:
                                print(f"{indent}📝 {title} → (Page reference error)")
                            
                            count += 1
                            
                            # Limit output for readability
                            if count > 50:
                                print(f"{indent}... and more ({len(bookmarks) - count} additional items)")
                                break
                    
                    return count
                
                total_bookmarks = print_bookmarks(reader.outline)
                print(f"\n📊 Total bookmarks found: {total_bookmarks}")
                
            else:
                print("❌ No bookmarks found in PDF")
            
            # Check for metadata
            if reader.metadata:
                print(f"\n📄 PDF METADATA:")
                print("-" * 20)
                for key, value in reader.metadata.items():
                    print(f"  {key}: {value}")
            
            # Check specific pages for content
            print(f"\n🔍 CHECKING SPECIFIC PAGES:")
            print("-" * 30)
            
            # Check page 738 (where TOC should show "Chicken in Mole-Poblano Sauce")
            if len(reader.pages) >= 738:
                page_738 = reader.pages[737]  # 0-indexed
                text_738 = page_738.extract_text()[:500]  # First 500 chars
                print(f"📄 Page 738 content sample:")
                print(f"   {repr(text_738)}")
                
                # Look for the recipe title
                if "Chicken in Mole-Poblano Sauce" in text_738:
                    print("✅ Found 'Chicken in Mole-Poblano Sauce' on page 738")
                else:
                    print("❌ 'Chicken in Mole-Poblano Sauce' not found on page 738")
            
            # Check page 810 (where recipe should be)
            if len(reader.pages) >= 810:
                page_810 = reader.pages[809]  # 0-indexed  
                text_810 = page_810.extract_text()[:500]  # First 500 chars
                print(f"\n📄 Page 810 content sample:")
                print(f"   {repr(text_810)}")
                
                # Look for the recipe title
                if "Chicken in Mole-Poblano Sauce" in text_810:
                    print("✅ Found 'Chicken in Mole-Poblano Sauce' on page 810")
                else:
                    print("❌ 'Chicken in Mole-Poblano Sauce' not found on page 810")
    
    except Exception as e:
        print(f"❌ Error analyzing PDF: {e}")

if __name__ == "__main__":
    extract_pdf_bookmarks()
