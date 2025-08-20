#!/usr/bin/env python3
"""
Debug instruction parsing to see why steps are getting concatenated
"""

import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cookbook_processing.atk_25th_simplified_intelligent_extractor import ATK25thSimplifiedIntelligentExtractor

import PyPDF2

def debug_instruction_parsing():
    """Debug the instruction parsing step by step"""
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
    
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        page = reader.pages[249]  # Page 250
        text = page.extract_text()
        
        print("=== RAW PAGE TEXT ===")
        lines = text.split('\n')
        for i, line in enumerate(lines):
            print(f"{i:2d}: '{line}'")
        
        print("\n=== LOOKING FOR NUMBERED STEPS ===")
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            step_match = re.match(r'^(\d+)\.\s*(.+)', line_stripped)
            if step_match:
                step_num = int(step_match.group(1))
                step_text = step_match.group(2).strip()
                print(f"Found step {step_num}: '{step_text}'")
                
                # Look ahead for continuation
                print(f"  Looking ahead from line {i}...")
                for j in range(i + 1, min(i + 10, len(lines))):
                    next_line = lines[j].strip()
                    if not next_line:
                        continue
                    print(f"    Line {j}: '{next_line}'")
                    
                    # Stop if we hit the next numbered step
                    if re.match(r'^\d+\.\s', next_line):
                        print(f"    -> Found next step, stopping")
                        break
                    
                    # Stop if we hit ingredient-like content
                    if re.search(r'^\d+\s*(cup|tablespoon|teaspoon|pound|ounce)', next_line, re.IGNORECASE):
                        print(f"    -> Found ingredient, stopping")
                        break
                print()

if __name__ == "__main__":
    debug_instruction_parsing()
