#!/usr/bin/env python3
"""
Debug: Analyze what's on page 738 causing all mappings
"""

import PyPDF2
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def analyze_page_738():
    """Analyze what's on page 738 that's causing all recipes to map there"""
    
    pdf_path = r"d:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
    
    try:
        with open(pdf_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            
            # Check page 738 (0-indexed 737)
            page = reader.pages[737]
            page_text = page.extract_text()
            
            logger.info("📄 CONTENT OF PAGE 738 (0-indexed 737):")
            logger.info("=" * 60)
            logger.info(page_text[:2000])  # First 2000 characters
            logger.info("=" * 60)
            
            # Count lines and analyze structure
            lines = page_text.split('\n')
            logger.info(f"📊 Page 738 has {len(lines)} lines")
            
            # Check for recipe-like content
            recipe_indicators = ['chicken', 'beef', 'pork', 'fish', 'salmon', 'pasta', 'rice', 'bread',
                               'soup', 'salad', 'sauce', 'roasted', 'grilled', 'baked', 'braised']
            
            recipe_lines = []
            for line in lines:
                line = line.strip()
                if 5 < len(line) < 100:
                    if any(indicator in line.lower() for indicator in recipe_indicators):
                        recipe_lines.append(line)
            
            logger.info(f"🍽️ Found {len(recipe_lines)} recipe-like lines on page 738:")
            for i, line in enumerate(recipe_lines[:20]):  # Show first 20
                logger.info(f"  {i+1}. {line}")
            
            if len(recipe_lines) > 20:
                logger.info(f"  ... and {len(recipe_lines) - 20} more")
                
    except Exception as e:
        logger.error(f"❌ Error analyzing page 738: {e}")

if __name__ == "__main__":
    analyze_page_738()
