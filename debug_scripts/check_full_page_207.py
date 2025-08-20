#!/usr/bin/env python3
import sys, os
sys.path.append('.')
import PyPDF2

pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
with open(pdf_path, 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    page = reader.pages[206]  # Page 207 (0-indexed)
    text = page.extract_text()
    print('=== FULL PAGE 207 CONTENT ===')
    print(text)
    print('=== END ===')
