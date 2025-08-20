#!/usr/bin/env python3
"""
Simple debug script to check Oven-Roasted Salmon pages
"""

import fitz  # PyMuPDF
import os

def debug_salmon_pages():
    """Check the actual content on pages 299-301"""
    
    pdf_path = r"d:\Mik\Downloads\Me Hungie\cookbook_processing\The Complete Cookbook for Teen - America's Test Kitchen Kids.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return
    
    print("🐟 DEBUGGING OVEN-ROASTED SALMON PAGES")
    print("=" * 60)
    
    try:
        doc = fitz.open(pdf_path)
        
        for page_num in [299, 300, 301]:
            print(f"\n📄 PAGE {page_num}:")
            print("-" * 40)
            
            if page_num <= len(doc):
                page = doc[page_num - 1]  # fitz uses 0-based indexing
                text = page.get_text()
                
                # Show first 500 characters
                print(f"First 500 characters:")
                print(text[:500])
                print("...")
                
                # Look for key recipe indicators
                print(f"\n🔍 Recipe indicators:")
                
                # Check for "Oven-Roasted Salmon"
                if "oven-roasted salmon" in text.lower() or "salmon" in text.lower():
                    print(f"   ✅ Contains 'salmon'")
                else:
                    print(f"   ❌ No 'salmon' found")
                
                # Check for ingredients patterns
                ingredient_patterns = [
                    r'\d+.*(?:pound|cup|tablespoon|teaspoon|slice)',
                    r'salmon',
                    r'oil',
                    r'salt',
                    r'pepper'
                ]
                
                ingredients_found = []
                for pattern in ingredient_patterns:
                    import re
                    if re.search(pattern, text, re.IGNORECASE):
                        ingredients_found.append(pattern)
                
                if ingredients_found:
                    print(f"   ✅ Ingredient patterns found: {ingredients_found}")
                else:
                    print(f"   ❌ No ingredient patterns found")
                
                # Check for instruction patterns
                instruction_patterns = [
                    r'cook|bake|heat|place|remove|serve',
                    r'\d+\s*minute',
                    r'oven',
                    r'temperature|degree'
                ]
                
                instructions_found = []
                for pattern in instruction_patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        instructions_found.append(pattern)
                
                if instructions_found:
                    print(f"   ✅ Instruction patterns found: {instructions_found}")
                else:
                    print(f"   ❌ No instruction patterns found")
                
                # Check text length
                print(f"   📏 Total text length: {len(text)} characters")
                
                # Look for specific lines that contain recipe content
                lines = text.split('\n')
                recipe_lines = []
                for line in lines:
                    line = line.strip()
                    if line and (
                        any(word in line.lower() for word in ['salmon', 'oil', 'salt', 'pepper', 'oven', 'cook', 'bake', 'serve']) or
                        re.search(r'\d+.*(?:minute|degree|pound|cup)', line, re.IGNORECASE)
                    ):
                        recipe_lines.append(line)
                
                if recipe_lines:
                    print(f"   📝 Recipe-related lines found: {len(recipe_lines)}")
                    print(f"   Sample lines:")
                    for line in recipe_lines[:3]:
                        print(f"     - {line}")
                else:
                    print(f"   ❌ No obvious recipe lines found")
            else:
                print(f"   ❌ Page {page_num} not found in PDF")
        
        doc.close()
        
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")

if __name__ == "__main__":
    debug_salmon_pages()
