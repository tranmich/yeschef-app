#!/usr/bin/env python3
"""Debug the fallback logic step by step"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import PyPDF2
import re

def debug_fallback_logic():
    """Debug the fallback title detection"""
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\The Complete Cookbook for Teen - America's Test Kitchen Kids.pdf"
    
    # Extract page 101 content
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        page = reader.pages[100]  # 0-indexed, so page 101
        page_text = page.extract_text()
    
    lines = page_text.split('\n')
    
    print("=== DEBUGGING FALLBACK LOGIC ===")
    
    # Check first line
    first_line = lines[0].strip() if lines else ""
    print(f"First line: '{first_line}'")
    
    # Test the regex match
    match = re.match(r'^\d+.*?(cup|tablespoon|teaspoon|pound|ounce)', first_line, re.IGNORECASE)
    print(f"Regex match: {match}")
    if match:
        print(f"Match groups: {match.groups()}")
    
    # Look for section headers
    print("\nLooking for section headers:")
    sections = []
    for i, line in enumerate(lines[:15], 1):
        line = line.strip()
        if line.isupper() and 3 <= len(line) <= 12 and line not in ['VEGETARIAN', 'VEGETARI', 'AN']:
            # Check if it looks like a section header (not ingredient measurements)
            if not re.search(r'\d+.*?(cup|tablespoon|teaspoon|pound|ounce)', line, re.IGNORECASE):
                print(f"  Line {i}: '{line}' - SECTION HEADER")
                sections.append(line)
            else:
                print(f"  Line {i}: '{line}' - Contains measurements, skipped")
        elif line.isupper():
            print(f"  Line {i}: '{line}' - All caps but wrong length or excluded")
    
    print(f"\nFound sections: {sections}")
    
    if sections:
        title = f"Recipe with {', '.join(sections[:2]).title()}"
        print(f"Generated title: '{title}'")
    else:
        print("No sections found, would use 'Continuation Recipe'")

if __name__ == "__main__":
    debug_fallback_logic()
