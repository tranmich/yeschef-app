#!/usr/bin/env python3
"""
🔍 ATK Teens Recipe Pattern Analyzer
==================================

Examines actual recipe pages to understand the true formatting patterns
"""

import PyPDF2
import re

def examine_recipe_pages(pdf_path):
    """Look at specific pages to understand recipe formatting"""
    print("🔍 Examining potential recipe pages...")
    
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Based on the book subtitle "70+ recipes", let's examine pages throughout
        # Skip intro pages (1-40) and examine main content
        sample_pages = [50, 60, 80, 100, 120, 140, 160, 180, 200, 250, 300, 350, 400]
        
        for page_num in sample_pages:
            if page_num < len(pdf_reader.pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                
                print(f"\n{'='*60}")
                print(f"PAGE {page_num + 1} ANALYSIS")
                print(f"{'='*60}")
                
                # Show first 1000 characters to see structure
                print("CONTENT SAMPLE:")
                print("-" * 40)
                print(text[:1000])
                
                # Check for recipe indicators
                indicators = analyze_page_for_recipes(text)
                print(f"\nRECIPE INDICATORS:")
                print("-" * 40)
                for key, value in indicators.items():
                    print(f"  {key}: {value}")
                
                # Look for titles
                potential_titles = find_potential_titles(text)
                if potential_titles:
                    print(f"\nPOTENTIAL RECIPE TITLES:")
                    print("-" * 40)
                    for title in potential_titles:
                        print(f"  • {title}")

def analyze_page_for_recipes(text):
    """Analyze a page for various recipe indicators"""
    return {
        'Has BEGINNER/INTERMEDIATE/ADVANCED': bool(re.search(r'(BEGINNER|INTERMEDIATE|ADVANCED)', text)),
        'Has START COOKING': 'START COOKING' in text,
        'Has SERVES/MAKES': bool(re.search(r'(SERVES|MAKES)\s+\d+', text)),
        'Has time indicators': bool(re.search(r'\d+\s+(MINUTES|HOURS)', text)),
        'Has measurements': bool(re.search(r'\d+\s*(cup|tablespoon|teaspoon|pound|ounce)', text, re.IGNORECASE)),
        'Has numbered steps': bool(re.search(r'^\d+\.\s+', text, re.MULTILINE)),
        'Has ingredients list': bool(re.search(r'(ingredients|INGREDIENTS)', text)),
        'Has instructions': bool(re.search(r'(instructions|INSTRUCTIONS)', text)),
        'Has PREPARE INGREDIENTS': 'PREPARE INGREDIENTS' in text,
        'Has cooking verbs': bool(re.search(r'(cook|bake|mix|stir|heat|add|combine)', text, re.IGNORECASE)),
    }

def find_potential_titles(text):
    """Find potential recipe titles on a page"""
    lines = text.split('\n')
    titles = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Look for titles in ALL CAPS that are reasonable length
        if line.isupper() and 3 < len(line) < 50 and not line.isdigit():
            # Filter out obvious non-recipe lines
            if not any(skip in line for skip in ['PAGE', 'CHAPTER', 'COPYRIGHT', 'AMERICA', 'TEST', 'KITCHEN']):
                titles.append(line)
    
    return titles[:5]  # Return first 5 to avoid spam

def main():
    pdf_path = 'The Complete Cookbook for Teen - America\'s Test Kitchen Kids.pdf'
    
    print("🚀 ATK TEENS RECIPE PATTERN ANALYZER")
    print("=" * 50)
    
    examine_recipe_pages(pdf_path)

if __name__ == "__main__":
    main()
