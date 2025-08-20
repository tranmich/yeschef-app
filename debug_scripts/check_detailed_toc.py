#!/usr/bin/env python3
import sys, os
sys.path.append('.')
import PyPDF2

pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
with open(pdf_path, 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    
    # Check table of contents at beginning of book
    for page_num in range(5, 15):
        page = reader.pages[page_num]
        text = page.extract_text()
        if 'Eggs & Breakfast' in text:
            print(f"=== TABLE OF CONTENTS PAGE {page_num + 1} ===")
            # Look for the section and count recipes
            lines = text.split('\n')
            in_eggs_section = False
            for line in lines:
                if 'Eggs & Breakfast' in line:
                    in_eggs_section = True
                    print(f"FOUND: {line}")
                elif in_eggs_section and line.strip():
                    if any(section in line for section in ['Soups', 'Salads', 'Vegetables', 'Main']):
                        break
                    print(line)
            print("=== END ===\n")
