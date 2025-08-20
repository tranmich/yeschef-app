#!/usr/bin/env python3
"""
📚 Quick PDF TOC Extractor for ATK Teens Cookbook
===============================================

Simple and focused extraction of table of contents to count recipes
"""

import PyPDF2
import re

def extract_toc_content(pdf_path):
    """Extract content from first 20 pages where TOC is likely located"""
    print("📖 Extracting table of contents...")
    
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Check first 20 pages for TOC
        for page_num in range(min(20, len(pdf_reader.pages))):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            
            print(f"\n=== PAGE {page_num + 1} ===")
            print(text[:1000] + "..." if len(text) > 1000 else text)
            
            # Look for clear TOC indicators
            if any(indicator in text.lower() for indicator in ['contents', 'chapter']):
                print(f"\n🎯 POTENTIAL TOC FOUND ON PAGE {page_num + 1}")
                
                # Extract potential recipe entries
                lines = text.split('\n')
                recipes = []
                
                for line in lines:
                    line = line.strip()
                    # Look for lines with page numbers at the end
                    if re.search(r'.*\d{1,3}$', line) and len(line) > 5:
                        # Check if it looks like a recipe (not chapter headings)
                        if not re.match(r'(chapter|introduction|index|appendix)', line.lower()):
                            recipes.append(line)
                
                if recipes:
                    print(f"\n📝 POTENTIAL RECIPES FOUND:")
                    for i, recipe in enumerate(recipes[:20], 1):  # Show first 20
                        print(f"{i:2d}. {recipe}")
                    
                    if len(recipes) > 20:
                        print(f"... and {len(recipes) - 20} more")
                        
                    print(f"\n📊 Total potential recipes: {len(recipes)}")

def sample_recipe_pages(pdf_path):
    """Sample some pages throughout the book to verify recipe content"""
    print("\n\n🔍 SAMPLING RECIPE PAGES THROUGHOUT BOOK")
    print("=" * 50)
    
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        total_pages = len(pdf_reader.pages)
        
        # Sample pages at intervals
        sample_pages = [50, 100, 150, 200, 250, 300, 350, 400, 450]
        
        for page_num in sample_pages:
            if page_num < total_pages:
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                
                print(f"\n--- PAGE {page_num + 1} SAMPLE ---")
                # Look for recipe titles (often in caps or title case)
                lines = text.split('\n')[:15]  # First 15 lines
                
                for line in lines:
                    line = line.strip()
                    if line and (len(line) < 60):  # Potential title length
                        # Check if looks like a recipe title
                        if any(indicator in line.lower() for indicator in ['cake', 'bread', 'soup', 'sauce', 'chicken', 'pasta', 'salad', 'cookie', 'pie']):
                            print(f"  🍽️  {line}")
                        elif line.isupper() and 3 < len(line) < 50:
                            print(f"  📝 {line}")

def main():
    pdf_path = 'The Complete Cookbook for Teen - America\'s Test Kitchen Kids.pdf'
    
    print("🚀 QUICK ATK TEENS TOC ANALYZER")
    print("=" * 40)
    
    # Extract TOC
    extract_toc_content(pdf_path)
    
    # Sample recipe pages
    sample_recipe_pages(pdf_path)

if __name__ == "__main__":
    main()
