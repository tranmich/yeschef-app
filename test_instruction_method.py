#!/usr/bin/env python3
"""
Simple test of just the instruction extraction method
"""

import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cookbook_processing.atk_25th_simplified_intelligent_extractor import ATK25thSimplifiedIntelligentExtractor

import PyPDF2

def test_instruction_extraction_only():
    """Test only the instruction extraction method"""
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
    
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        page = reader.pages[249]  # Page 250
        text = page.extract_text()
        
        extractor = ATK25thSimplifiedIntelligentExtractor(pdf_path)
        
        print("=== Testing _extract_instructions_directly method ===")
        instructions = extractor._extract_instructions_directly(text)
        
        if instructions:
            print("Instructions extracted:")
            print(repr(instructions))
            print("\nInstructions formatted:")
            print(instructions)
            instruction_steps = instructions.split('\n')
            print(f"\nNumber of instruction steps: {len(instruction_steps)}")
            for i, step in enumerate(instruction_steps):
                print(f"Step {i+1}: {step[:100]}...")  # First 100 chars of each step
        else:
            print("No instructions extracted")

if __name__ == "__main__":
    test_instruction_extraction_only()
