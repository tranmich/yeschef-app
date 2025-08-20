#!/usr/bin/env python3
"""Check pages around 101 to find the recipe title"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import PyPDF2

def check_pages_around_101():
    """Check pages 99-103 to find the recipe title"""
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\The Complete Cookbook for Teen - America's Test Kitchen Kids.pdf"
    
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        for page_num in range(98, 104):  # Pages 99-104 (0-indexed)
            print(f"\n=== PAGE {page_num + 1} ===")
            if page_num < len(reader.pages):
                page = reader.pages[page_num]
                page_text = page.extract_text()
                
                # Show first 10 lines
                lines = page_text.split('\n')[:10]
                for i, line in enumerate(lines, 1):
                    line = line.strip()
                    if line:
                        print(f"{i:2d}: '{line}'")
            else:
                print("Page out of range")

if __name__ == "__main__":
    check_pages_around_101()
