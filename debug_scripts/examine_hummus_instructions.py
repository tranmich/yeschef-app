#!/usr/bin/env python3
"""
Check what instruction-like content exists on the hummus page
"""

import sys
import os
import PyPDF2

def examine_hummus_page():
    """Look for any instruction-like content"""
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
    
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        
        # Check page 90 and 91 for hummus instructions
        for page_num in [90, 91]:
            print(f"\n📄 PAGE {page_num}:")
            print("=" * 50)
            
            page = reader.pages[page_num - 1]
            text = page.extract_text()
            
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            # Look for instruction indicators
            instruction_indicators = [
                'heat', 'cook', 'process', 'combine', 'add', 'stir', 'transfer',
                'place', 'remove', 'drain', 'rinse', 'simmer', 'boil'
            ]
            
            for i, line in enumerate(lines):
                line_lower = line.lower()
                
                # Check for numbered steps
                if line.startswith(('1.', '2.', '3.', '4.', '5.')):
                    print(f"  {i:2d}: NUMBERED STEP: '{line}'")
                
                # Check for instruction-like sentences
                elif any(indicator in line_lower for indicator in instruction_indicators):
                    if len(line) > 30:  # Substantial instruction
                        print(f"  {i:2d}: INSTRUCTION-LIKE: '{line[:80]}...'")
                
                # Check for capitalized action words at start
                elif line.startswith(('Heat', 'Cook', 'Process', 'Combine', 'Add', 'Stir', 'Transfer', 'Place', 'Remove', 'Drain')):
                    print(f"  {i:2d}: ACTION START: '{line[:80]}...'")

if __name__ == "__main__":
    examine_hummus_page()
