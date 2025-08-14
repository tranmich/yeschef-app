"""
Deep Recipe Page Analysis
Examine specific recipe pages to understand the EXACT text structure
"""

import pdfplumber
import re
from typing import List

class DeepRecipeAnalysis:
    """Analyze specific recipe pages in detail"""
    
    def analyze_specific_pages(self, pdf_path: str, page_numbers: List[int]):
        """Analyze specific pages in detail"""
        
        print(f"🔬 DEEP ANALYSIS OF RECIPE PAGES")
        print("=" * 80)
        
        with pdfplumber.open(pdf_path) as pdf:
            
            for page_num in page_numbers:
                if page_num <= len(pdf.pages):
                    print(f"\\n" + "="*60)
                    print(f"📄 PAGE {page_num} DETAILED ANALYSIS")
                    print("="*60)
                    
                    page = pdf.pages[page_num - 1]  # 0-indexed
                    text = page.extract_text()
                    
                    if text:
                        lines = text.split('\\n')
                        
                        print(f"📝 Total Lines: {len(lines)}")
                        print(f"\\n🔍 COMPLETE TEXT CONTENT:")
                        print("-" * 40)
                        
                        for i, line in enumerate(lines, 1):
                            # Show line number and content
                            print(f"{i:3d}: '{line}'")
                        
                        print("-" * 40)
                        
                        # Analyze patterns
                        self._analyze_patterns(lines, page_num)
                    else:
                        print("❌ No text extracted from this page")
    
    def _analyze_patterns(self, lines: List[str], page_num: int):
        """Analyze text patterns on the page"""
        
        print(f"\\n🎯 PATTERN ANALYSIS:")
        
        # Look for potential recipe titles
        potential_titles = []
        timing_lines = []
        ingredient_lines = []
        direction_lines = []
        
        for i, line in enumerate(lines):
            line_clean = line.strip()
            line_upper = line_clean.upper()
            
            # Recipe title candidates
            if (5 <= len(line_clean) <= 60 and
                not any(skip in line_upper for skip in ['ULTIMATE', 'CANADIAN', 'COOKBOOK', 'CHAPTER']) and
                not line_clean.isdigit() and
                len(line_clean.split()) <= 8):
                potential_titles.append((i+1, line_clean))
            
            # Timing information
            if any(keyword in line_upper for keyword in ['HANDS-ON', 'TOTAL', 'PREP', 'COOK', 'TIME']):
                timing_lines.append((i+1, line_clean))
            
            # Ingredient indicators
            if 'INGREDIENTS' in line_upper:
                ingredient_lines.append((i+1, line_clean))
            
            # Direction indicators
            if any(keyword in line_upper for keyword in ['DIRECTIONS', 'INSTRUCTIONS', 'METHOD']):
                direction_lines.append((i+1, line_clean))
        
        print(f"\\n📝 Potential Titles ({len(potential_titles)}):")
        for line_num, title in potential_titles:
            print(f"   Line {line_num}: '{title}'")
        
        print(f"\\n⏰ Timing Lines ({len(timing_lines)}):")
        for line_num, timing in timing_lines:
            print(f"   Line {line_num}: '{timing}'")
        
        print(f"\\n🥕 Ingredient Lines ({len(ingredient_lines)}):")
        for line_num, ingredient in ingredient_lines:
            print(f"   Line {line_num}: '{ingredient}'")
        
        print(f"\\n📋 Direction Lines ({len(direction_lines)}):")
        for line_num, direction in direction_lines:
            print(f"   Line {line_num}: '{direction}'")
        
        # Recipe structure assessment
        has_titles = len(potential_titles) > 0
        has_timing = len(timing_lines) > 0
        has_ingredients = len(ingredient_lines) > 0
        has_directions = len(direction_lines) > 0
        
        recipe_score = sum([has_titles, has_timing, has_ingredients, has_directions])
        
        print(f"\\n🎯 RECIPE STRUCTURE SCORE: {recipe_score}/4")
        print(f"   ✅ Has Titles: {has_titles}")
        print(f"   ✅ Has Timing: {has_timing}")
        print(f"   ✅ Has Ingredients: {has_ingredients}")
        print(f"   ✅ Has Directions: {has_directions}")
        
        if recipe_score >= 2:
            print(f"   🟢 LIKELY CONTAINS RECIPES")
        else:
            print(f"   🔴 UNLIKELY TO CONTAIN RECIPES")


def main():
    """Analyze specific recipe pages"""
    
    pdf_path = "books_archive/Canadian-Living-The-Ultimate-Cookbook.pdf"
    
    # Analyze pages we know should have recipes
    recipe_pages = [11, 13, 14, 15, 18, 19, 20, 22, 23, 24]
    
    analyzer = DeepRecipeAnalysis()
    analyzer.analyze_specific_pages(pdf_path, recipe_pages)


if __name__ == "__main__":
    main()
