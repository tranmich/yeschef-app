#!/usr/bin/env python3
"""
🔍 Debug Page 101 Content
"""

import PyPDF2

def examine_page_101():
    """Look at the exact content of page 101"""
    pdf_path = 'The Complete Cookbook for Teen - America\'s Test Kitchen Kids.pdf'
    
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        page = pdf_reader.pages[100]  # Page 101 (0-based)
        text = page.extract_text()
        
        print("🔍 FULL PAGE 101 CONTENT")
        print("=" * 50)
        print(text)
        
        print("\n\n🔍 SEARCHING FOR PATTERNS")
        print("=" * 30)
        
        # Look for various ingredient patterns
        patterns = [
            r'PREPARE INGREDIENTS(.*?)START COOKING!',
            r'INGREDIENTS(.*?)INSTRUCTIONS',
            r'INGREDIENTS(.*?)START COOKING!',
            r'((?:\d+.*?(?:cup|tablespoon|teaspoon|pound|ounce).*?\n)+)',
        ]
        
        import re
        for i, pattern in enumerate(patterns, 1):
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                print(f"Pattern {i} MATCHED:")
                print(f"'{match.group(1)[:200]}...'")
            else:
                print(f"Pattern {i}: No match")

if __name__ == "__main__":
    examine_page_101()
