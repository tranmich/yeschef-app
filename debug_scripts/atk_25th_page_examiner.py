#!/usr/bin/env python3
"""
Quick test to examine what the ATK 25th extractor is finding
"""

import sys
import os
import PyPDF2
import re

def examine_sample_pages():
    """Examine a few sample pages to understand the format"""
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
    
    try:
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            
            # Check a few recipe pages found by our analyzer
            sample_pages = [500, 512, 516, 520, 522]
            
            for page_num in sample_pages:
                if page_num < len(reader.pages):
                    page = reader.pages[page_num]
                    text = page.extract_text()
                    
                    print(f"\n🔍 PAGE {page_num + 1} ANALYSIS:")
                    print("=" * 50)
                    
                    lines = text.split('\n')
                    print(f"Total lines: {len(lines)}")
                    print(f"Total characters: {len(text)}")
                    
                    # Show first 20 lines
                    print("\nFirst 20 lines:")
                    for i, line in enumerate(lines[:20]):
                        if line.strip():
                            print(f"  {i+1:2}: {line.strip()}")
                    
                    # Look for specific patterns
                    print(f"\nPattern Analysis:")
                    print(f"  Contains 'INGREDIENTS': {'INGREDIENTS' in text.upper()}")
                    print(f"  Contains 'METHOD': {'METHOD' in text.upper()}")
                    print(f"  Contains 'FOR THE': {'FOR THE' in text.upper()}")
                    print(f"  Contains numbered steps: {bool(re.search(r'^\\d+\\.\\s+', text, re.MULTILINE))}")
                    print(f"  Contains measurements: {bool(re.search(r'\\d+\\s*(cup|tablespoon|teaspoon)', text, re.IGNORECASE))}")
                    
                    if page_num == 516:  # The one our analyzer found patterns on
                        print(f"\n📖 DETAILED VIEW OF PAGE 517 (PATTERN PAGE):")
                        print(text[:1000] + "..." if len(text) > 1000 else text)
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    examine_sample_pages()
