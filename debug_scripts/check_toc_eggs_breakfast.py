#!/usr/bin/env python3
import sys, os
sys.path.append('.')
import PyPDF2

pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
with open(pdf_path, 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    
    # Check around page 203 for table of contents
    for page_num in range(200, 210):
        page = reader.pages[page_num]
        text = page.extract_text()
        if 'Eggs & Breakfast' in text or 'eggs & breakfast' in text.lower():
            print(f"=== PAGE {page_num + 1} CONTENT ===")
            print(text[:1000])
            print("=== END ===\n")
