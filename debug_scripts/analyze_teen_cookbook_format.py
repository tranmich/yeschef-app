#!/usr/bin/env python3
"""
Debug script to examine ATK Teen cookbook pages and understand format
"""

import os
import sys
import PyPDF2
import re

def analyze_teen_cookbook_pages(start_page=45, end_page=55):
    """Analyze specific pages to understand teen cookbook format"""
    
    pdf_path = 'The Complete Cookbook for Teen - America\'s Test Kitchen Kids.pdf'
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return
    
    print("🔍 ANALYZING ATK TEEN COOKBOOK PAGES")
    print("=" * 50)
    
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        
        for page_num in range(start_page - 1, min(end_page, len(reader.pages))):
            page = reader.pages[page_num]
            page_text = page.extract_text()
            
            print(f"\n📄 PAGE {page_num + 1}")
            print("-" * 30)
            
            # Check for recipe indicators
            indicators = {
                'BEGINNER/INTERMEDIATE/ADVANCED': bool(re.search(r'(BEGINNER|INTERMEDIATE|ADVANCED)', page_text)),
                'SERVES/MAKES': bool(re.search(r'(SERVES|MAKES)\s+\d+', page_text)),
                'PREPARE INGREDIENTS': 'PREPARE INGREDIENTS' in page_text,
                'START COOKING!': 'START COOKING!' in page_text,
                'BEFORE YOU BEGIN': 'BEFORE YOU BEGIN' in page_text,
                'VEGETARIAN': 'VEGETARIAN' in page_text,
                'Time indicators': bool(re.search(r'\d+\s+(MINUTES?|HOURS?)', page_text)),
                'Measurements': bool(re.search(r'\d+.*?(cup|tablespoon|teaspoon|pound|ounce)', page_text))
            }
            
            print("🎯 Recipe Indicators:")
            for indicator, found in indicators.items():
                status = "✅" if found else "❌"
                print(f"  {status} {indicator}")
            
            # Look for potential titles
            lines = page_text.split('\n')
            potential_titles = []
            for i, line in enumerate(lines[:20]):
                line = line.strip()
                if (line.isupper() and 5 <= len(line) <= 60 and 
                    not re.search(r'(BEGINNER|INTERMEDIATE|ADVANCED|VEGETARIAN|SERVES|MAKES|PREPARE|START|BEFORE)', line) and
                    not re.search(r'\d+.*?(cup|tablespoon|teaspoon)', line)):
                    potential_titles.append(f"Line {i+1}: {line}")
            
            if potential_titles:
                print("\n📝 Potential Titles:")
                for title in potential_titles[:3]:
                    print(f"  • {title}")
            
            # Check content sections
            has_prepare = 'PREPARE INGREDIENTS' in page_text
            has_cooking = 'START COOKING!' in page_text
            
            if has_prepare:
                print("\n🥘 PREPARE INGREDIENTS Section Found")
                prepare_pos = page_text.find('PREPARE INGREDIENTS')
                if has_cooking:
                    cooking_pos = page_text.find('START COOKING!')
                    ingredients_section = page_text[prepare_pos:cooking_pos]
                else:
                    ingredients_section = page_text[prepare_pos:prepare_pos+500]
                
                ingredient_lines = [line.strip() for line in ingredients_section.split('\n') if line.strip()][:10]
                print("  Sample ingredients:")
                for line in ingredient_lines[1:6]:  # Skip header
                    if line:
                        print(f"    • {line}")
            
            if has_cooking:
                print("\n👨‍🍳 START COOKING! Section Found")
                cooking_pos = page_text.find('START COOKING!')
                instructions_section = page_text[cooking_pos:cooking_pos+800]
                instruction_lines = [line.strip() for line in instructions_section.split('\n') if line.strip()][:8]
                print("  Sample instructions:")
                for line in instruction_lines[1:5]:  # Skip header
                    if line:
                        print(f"    • {line}")
            
            # Show confidence score for this page
            confidence_indicators = sum([
                indicators['BEGINNER/INTERMEDIATE/ADVANCED'] * 2.5,
                indicators['SERVES/MAKES'] * 2.0,
                indicators['PREPARE INGREDIENTS'] * 3.0,
                indicators['START COOKING!'] * 3.0,
                indicators['Time indicators'] * 1.0,
                indicators['Measurements'] * 1.5
            ])
            
            print(f"\n📊 Visual Confidence Score: {confidence_indicators:.1f}")
            print(f"🎯 Recipe Page: {'YES' if confidence_indicators >= 4.0 else 'NO'}")

if __name__ == "__main__":
    analyze_teen_cookbook_pages(45, 55)
