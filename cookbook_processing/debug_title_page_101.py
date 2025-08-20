#!/usr/bin/env python3
"""Debug title extraction on page 101"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import PyPDF2
from atk_teens_safe_extractor import ATKTeensExtractor

def debug_title_extraction():
    """Debug the title extraction process"""
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\The Complete Cookbook for Teen - America's Test Kitchen Kids.pdf"
    
    # Extract page 101 content
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        page = reader.pages[100]  # 0-indexed, so page 101
        page_text = page.extract_text()
    
    print("=== FIRST 20 LINES OF PAGE 101 ===")
    lines = page_text.split('\n')
    for i, line in enumerate(lines[:20], 1):
        print(f"{i:2d}: '{line.strip()}'")
    
    print("\n" + "="*50)
    
    # Create extractor and test header extraction
    extractor = ATKTeensExtractor(pdf_path)
    
    print("\n=== TESTING HEADER EXTRACTION ===")
    header_info = extractor._extract_header_info(page_text)
    print(f"Header info: {header_info}")
    
    print("\n=== TESTING TITLE DETECTION ON EACH LINE ===")
    for i, line in enumerate(lines[:15], 1):
        line = line.strip()
        if line:
            is_title = extractor._is_recipe_title_line(line)
            print(f"{i:2d}: {is_title} | '{line}'")

if __name__ == "__main__":
    debug_title_extraction()
