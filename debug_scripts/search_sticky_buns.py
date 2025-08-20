#!/usr/bin/env python3
"""
Search for sticky buns recipe in teen cookbook
"""

import os
import PyPDF2
import re

def search_for_sticky_buns():
    """Search for sticky buns recipe in the teen cookbook"""
    
    pdf_path = 'The Complete Cookbook for Teen - America\'s Test Kitchen Kids.pdf'
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return
    
    print("🔍 SEARCHING FOR STICKY BUNS RECIPE")
    print("=" * 50)
    
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            page_text = page.extract_text()
            
            # Search for sticky buns references
            if 'sticky' in page_text.lower() or 'buns' in page_text.lower():
                print(f"\n📄 PAGE {page_num + 1} - Contains 'sticky' or 'buns'")
                print("-" * 40)
                
                # Look for recipe indicators
                indicators = {
                    'STICKY BUNS': 'STICKY BUNS' in page_text.upper(),
                    'BEGINNER/INTERMEDIATE/ADVANCED': bool(re.search(r'(BEGINNER|INTERMEDIATE|ADVANCED)', page_text)),
                    'SERVES/MAKES': bool(re.search(r'(SERVES|MAKES)\s+\d+', page_text)),
                    'PREPARE INGREDIENTS': 'PREPARE INGREDIENTS' in page_text,
                    'START COOKING!': 'START COOKING!' in page_text,
                    'BEFORE YOU BEGIN': 'BEFORE YOU BEGIN' in page_text,
                    'Time indicators': bool(re.search(r'\d+\s+(MINUTES?|HOURS?)', page_text)),
                    'Measurements': bool(re.search(r'\d+.*?(cup|tablespoon|teaspoon|pound|ounce)', page_text))
                }
                
                print("🎯 Content Indicators:")
                for indicator, found in indicators.items():
                    status = "✅" if found else "❌"
                    print(f"  {status} {indicator}")
                
                # Show first few lines for context
                lines = page_text.split('\n')[:10]
                print("\n📝 First 10 lines:")
                for i, line in enumerate(lines, 1):
                    if line.strip():
                        print(f"  {i:2d}. {line.strip()}")
                
                # Calculate confidence score
                confidence = sum([
                    indicators['BEGINNER/INTERMEDIATE/ADVANCED'] * 2.5,
                    indicators['SERVES/MAKES'] * 2.0,
                    indicators['PREPARE INGREDIENTS'] * 3.0,
                    indicators['START COOKING!'] * 3.0,
                    indicators['Time indicators'] * 1.0,
                    indicators['Measurements'] * 1.5
                ])
                
                print(f"\n📊 Visual Confidence Score: {confidence:.1f}")
                print(f"🎯 Recipe Page: {'YES' if confidence >= 4.0 else 'NO'}")

if __name__ == "__main__":
    search_for_sticky_buns()
