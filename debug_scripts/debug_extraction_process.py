#!/usr/bin/env python3
"""
Debug version of extractor that shows what's being rejected and why
"""

import sys
import os
import re
import PyPDF2
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_systems.semantic_recipe_engine import SemanticRecipeEngine, ValidationLevel

def debug_extraction_process(pdf_path: str, start_page: int = 1, end_page: int = 10):
    """Debug what's happening during extraction"""
    
    semantic_engine = SemanticRecipeEngine(ValidationLevel.STRICT)
    
    print(f"🔍 DEBUGGING EXTRACTION PROCESS")
    print("=" * 60)
    print(f"📄 Analyzing pages {start_page} to {end_page}")
    
    try:
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            total_pages = len(reader.pages)
            
            start_idx = start_page - 1
            end_idx = min(end_page, total_pages)
            
            for page_num in range(start_idx, end_idx):
                page = reader.pages[page_num]
                text = page.extract_text()
                
                if not text or len(text.strip()) < 50:
                    print(f"\nPage {page_num + 1}: ❌ SKIPPED - No content ({len(text)} chars)")
                    continue
                
                print(f"\nPage {page_num + 1}: Processing ({len(text)} chars)")
                print("-" * 40)
                
                # Analyze potential titles
                lines = [line.strip() for line in text.split('\n') if line.strip()]
                potential_titles = []
                
                for i, line in enumerate(lines[:20]):  # Check first 20 lines
                    if len(line) < 3 or len(line) > 80:
                        continue
                    
                    # Skip obvious non-titles
                    if line.lower().startswith(('ingredients', 'method', 'serves', 'makes')):
                        continue
                    
                    if re.match(r'^[0-9]+\.', line):
                        continue
                    
                    potential_titles.append((i, line))
                
                print(f"Potential titles found: {len(potential_titles)}")
                
                for i, title in potential_titles[:5]:  # Show first 5
                    print(f"  Line {i}: '{title}'")
                    
                    # Test title validation
                    is_valid = semantic_engine._is_recipe_title(title)
                    content_type, confidence = semantic_engine.classify_content_type(title)
                    
                    print(f"    Valid title: {is_valid}")
                    print(f"    Content type: {content_type}")
                    print(f"    Confidence: {confidence:.2f}")
                    
                    if not is_valid:
                        # Analyze why it was rejected
                        reasons = []
                        title_lower = title.lower()
                        
                        if len(title) < 3 or len(title) > 100:
                            reasons.append("length")
                        if re.search(r'\d+\s*(cup|tablespoon|teaspoon|pound|ounce)', title_lower):
                            reasons.append("measurements")
                        if len(title.split()) == 1:
                            reasons.append("single_word")
                        if not title[0].isupper():
                            reasons.append("no_capital")
                        if any(indicator in title_lower for indicator in ['saucepan', 'skillet', 'transfer', 'bake', 'heat']):
                            reasons.append("instruction_words")
                        if not semantic_engine._contains_food_words(title) and not semantic_engine._contains_cooking_words(title):
                            reasons.append("no_food_words")
                        
                        print(f"    Rejection reasons: {', '.join(reasons) if reasons else 'unknown'}")
                
                # Quick ingredient/instruction check
                has_potential_ingredients = False
                has_potential_instructions = False
                
                for line in lines:
                    if re.search(r'^\d+\s*(cup|tablespoon|teaspoon|pound|ounce)', line, re.IGNORECASE):
                        has_potential_ingredients = True
                    if re.match(r'^\d+\.\s', line):
                        has_potential_instructions = True
                
                print(f"Has potential ingredients: {has_potential_ingredients}")
                print(f"Has potential instructions: {has_potential_instructions}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        return
    
    # Debug a sample of pages
    debug_extraction_process(pdf_path, start_page=90, end_page=95)

if __name__ == "__main__":
    main()
