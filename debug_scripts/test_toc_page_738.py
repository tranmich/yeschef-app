#!/usr/bin/env python3

import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cookbook_processing'))

import PyPDF2
import re

def test_toc_page_738():
    """Test TOC extraction specifically on page 738"""
    
    pdf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                           'cookbook_processing', 
                           "America's Test Kitchen 25th Ann - America's Test Kitchen.pdf")
    
    print("🔍 TESTING TOC ON PAGE 738")
    print("=" * 50)
    print(f"📄 PDF Path: {pdf_path}")
    
    try:
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            
            # Get page 738 (0-indexed)
            page = reader.pages[737]
            page_text = page.extract_text()
            
            print(f"📄 Page 738 text length: {len(page_text)} characters")
            print("\n📄 FIRST 500 CHARACTERS:")
            print("-" * 30)
            print(page_text[:500])
            
            print("\n🔍 SEARCHING FOR 'CHICKEN IN MOLE-POBLANO SAUCE':")
            print("-" * 50)
            
            # Look for the specific recipe
            if "Chicken in Mole-Poblano Sauce" in page_text:
                print("✅ Found exact match: 'Chicken in Mole-Poblano Sauce'")
                
                # Find context around it
                lines = page_text.split('\n')
                for i, line in enumerate(lines):
                    if "Chicken in Mole-Poblano Sauce" in line:
                        print(f"📄 Line {i}: '{line.strip()}'")
                        
                        # Show surrounding lines for context
                        print("\n📝 CONTEXT (5 lines before and after):")
                        start = max(0, i-5)
                        end = min(len(lines), i+6)
                        for j in range(start, end):
                            marker = ">>> " if j == i else "    "
                            print(f"{marker}Line {j}: '{lines[j].strip()}'")
                        break
            else:
                print("❌ 'Chicken in Mole-Poblano Sauce' NOT found on page 738")
                
                # Look for variations
                variations = [
                    "chicken in mole-poblano sauce",
                    "chicken in mole poblano sauce", 
                    "mole-poblano",
                    "mole poblano",
                    "poblano"
                ]
                
                for variant in variations:
                    if variant.lower() in page_text.lower():
                        print(f"✅ Found variation: '{variant}'")
                        break
                else:
                    print("❌ No variations found either")
            
            print("\n🔍 LOOKING FOR PAGE NUMBER PATTERNS:")
            print("-" * 40)
            
            # Look for page number patterns that might indicate TOC entries
            page_patterns = [
                r'(\w+.*?)\s+(\d{3,4})',  # Recipe name followed by 3-4 digit page number
                r'(\w+.*?)\s+\.+\s*(\d{3,4})',  # Recipe with dots and page number
                r'(\w+.*?)\s+\d+\s*$'  # Recipe ending with page number
            ]
            
            lines = page_text.split('\n')
            toc_entries = []
            
            for line in lines:
                line = line.strip()
                if len(line) < 10:  # Skip very short lines
                    continue
                    
                for pattern in page_patterns:
                    match = re.search(pattern, line)
                    if match:
                        try:
                            recipe_name = match.group(1).strip()
                            page_num = int(match.group(2))
                            
                            # Check if this looks like a recipe entry
                            if page_num > 100 and len(recipe_name) > 5:  # Reasonable page number and recipe name
                                toc_entries.append((recipe_name, page_num, line))
                        except (ValueError, IndexError):
                            continue
            
            print(f"📋 Found {len(toc_entries)} potential TOC entries:")
            for recipe_name, page_num, full_line in toc_entries[:20]:  # Show first 20
                print(f"  📝 '{recipe_name}' → Page {page_num}")
                print(f"      Full line: '{full_line}'")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_toc_page_738()
