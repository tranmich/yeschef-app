#!/usr/bin/env python3
"""Check page 95 (Acai Smoothie) content to understand format"""

import PyPDF2

def analyze_page_95():
    """Analyze the full content of page 95 to understand format"""
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\The Complete Cookbook for Teen - America's Test Kitchen Kids.pdf"
    
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        page = reader.pages[94]  # Page 95, 0-indexed
        text = page.extract_text()
    
    print("📄 COMPLETE PAGE 95 CONTENT")
    print("=" * 60)
    
    lines = text.split('\n')
    for i, line in enumerate(lines, 1):
        if line.strip():
            print(f"{i:3d}: {line}")
    
    print(f"\n📊 PAGE STATS:")
    print(f"  Total lines: {len(lines)}")
    print(f"  Total characters: {len(text)}")
    print(f"  Has 'PREPARE INGREDIENTS': {'PREPARE INGREDIENTS' in text}")
    print(f"  Has 'START COOKING!': {'START COOKING!' in text}")

if __name__ == "__main__":
    analyze_page_95()
