#!/usr/bin/env python3
import sys, os
sys.path.append('.')
import PyPDF2

pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
with open(pdf_path, 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    
    # Check around page 321 for section end
    for page_num in range(318, 325):
        if page_num < len(reader.pages):
            page = reader.pages[page_num]
            text = page.extract_text()
            print(f"=== PAGE {page_num + 1} CONTENT ===")
            print(text[:300])
            print("=== END ===\n")
