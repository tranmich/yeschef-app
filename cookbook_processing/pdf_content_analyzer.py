#!/usr/bin/env python3
"""
📚 PDF Content Analyzer for ATK Teens Cookbook
==============================================

Analyzes the complete PDF to:
1. Extract and display table of contents
2. Count total recipes available
3. Identify recipe patterns and locations
4. Validate extraction accuracy
"""

import PyPDF2
import re
import json
from collections import defaultdict

class ATKTeensPDFAnalyzer:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.all_text = ""
        self.toc_pages = []
        self.recipe_locations = []
        
    def extract_all_text(self):
        """Extract all text from PDF for analysis"""
        print("📖 Extracting all text from PDF...")
        
        with open(self.pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            total_pages = len(pdf_reader.pages)
            
            print(f"📄 Total pages: {total_pages}")
            
            for page_num in range(total_pages):
                try:
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    self.all_text += f"\n--- PAGE {page_num + 1} ---\n{text}\n"
                    
                    # Check if this looks like a table of contents page
                    if self.is_toc_page(text):
                        self.toc_pages.append((page_num + 1, text))
                    
                    # Look for recipe indicators
                    if self.has_recipe_content(text):
                        self.recipe_locations.append(page_num + 1)
                        
                    if (page_num + 1) % 50 == 0:
                        print(f"  📊 Processed {page_num + 1}/{total_pages} pages...")
                        
                except Exception as e:
                    print(f"⚠️  Error on page {page_num + 1}: {e}")
                    continue
                    
        print(f"✅ Text extraction complete!")
        return self.all_text
    
    def is_toc_page(self, text):
        """Check if page looks like table of contents"""
        toc_indicators = [
            'table of contents',
            'contents',
            'chapter',
            'page',
            r'\d+\s*\.\s*[A-Z]',  # Numbered chapters
            r'\.{3,}',  # Dotted lines
        ]
        
        text_lower = text.lower()
        for indicator in toc_indicators:
            if re.search(indicator, text_lower):
                return True
        return False
    
    def has_recipe_content(self, text):
        """Check if page has recipe content"""
        recipe_indicators = [
            'ingredients',
            'instructions',
            'serves',
            'servings',
            'prep time',
            'cook time',
            'total time',
            'makes',
            'yield',
            'cups',
            'tablespoons',
            'teaspoons',
            'ounces',
            'pounds',
            'degrees',
            'fahrenheit',
            'celsius',
            'bake',
            'cook',
            'heat',
            'mix',
            'stir',
            'add',
            'combine'
        ]
        
        text_lower = text.lower()
        indicator_count = sum(1 for indicator in recipe_indicators if indicator in text_lower)
        
        # If we have multiple recipe indicators, likely a recipe page
        return indicator_count >= 3
    
    def analyze_table_of_contents(self):
        """Extract and analyze table of contents"""
        print("\n📋 ANALYZING TABLE OF CONTENTS")
        print("=" * 50)
        
        if not self.toc_pages:
            print("❌ No clear table of contents pages found")
            return []
        
        all_recipes = []
        
        for page_num, toc_text in self.toc_pages:
            print(f"\n📄 Table of Contents on page {page_num}:")
            print("-" * 30)
            
            # Look for recipe titles and page numbers
            lines = toc_text.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Look for patterns like "Recipe Name ... 123" or "Recipe Name 123"
                page_match = re.search(r'.*?(\d{1,3})$', line)
                if page_match and len(line) > 10:  # Reasonable recipe title length
                    recipe_title = line[:page_match.start()].strip()
                    page_ref = int(page_match.group(1))
                    
                    # Filter out obvious non-recipes
                    if not self.is_recipe_title(recipe_title):
                        continue
                        
                    recipe_info = {
                        'title': recipe_title,
                        'page': page_ref,
                        'toc_page': page_num
                    }
                    all_recipes.append(recipe_info)
                    print(f"  📝 {recipe_title} (page {page_ref})")
        
        return all_recipes
    
    def is_recipe_title(self, title):
        """Check if title looks like a recipe"""
        # Remove common TOC noise
        title_lower = title.lower().strip()
        
        # Skip if it's clearly not a recipe
        skip_patterns = [
            r'^chapter\s*\d+',
            r'^introduction',
            r'^index',
            r'^appendix',
            r'^glossary',
            r'^acknowledgments',
            r'^contents',
            r'^table of contents',
            r'^\d+$',  # Just numbers
            r'^page\s*\d+',
            r'^\.{3,}',  # Just dots
        ]
        
        for pattern in skip_patterns:
            if re.match(pattern, title_lower):
                return False
        
        # Must have reasonable length
        if len(title) < 3 or len(title) > 80:
            return False
            
        return True
    
    def find_all_recipes_by_pattern(self):
        """Find recipes by searching for common patterns throughout the PDF"""
        print("\n🔍 SCANNING ALL PAGES FOR RECIPE PATTERNS")
        print("=" * 50)
        
        pages = self.all_text.split('--- PAGE')
        recipe_patterns = []
        
        for i, page_content in enumerate(pages[1:], 1):  # Skip empty first split
            if not page_content.strip():
                continue
                
            # Look for recipe title patterns
            lines = page_content.split('\n')
            potential_titles = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Recipe titles are often in ALL CAPS or Title Case
                if (line.isupper() and 5 < len(line) < 50) or \
                   (line.istitle() and 5 < len(line) < 50):
                    # Check if it's followed by recipe content
                    if self.has_recipe_following(lines, lines.index(line)):
                        potential_titles.append({
                            'title': line,
                            'page': i,
                            'confidence': 'high'
                        })
            
            if potential_titles:
                recipe_patterns.extend(potential_titles)
                print(f"  📄 Page {i}: Found {len(potential_titles)} potential recipes")
        
        return recipe_patterns
    
    def has_recipe_following(self, lines, title_index):
        """Check if recipe content follows a potential title"""
        # Look at next 10-20 lines for recipe indicators
        check_lines = lines[title_index:title_index + 20]
        content = ' '.join(check_lines).lower()
        
        recipe_markers = [
            'ingredients',
            'instructions',
            'serves',
            'prep time',
            'cook time',
            'cups',
            'tablespoons',
            'teaspoons'
        ]
        
        markers_found = sum(1 for marker in recipe_markers if marker in content)
        return markers_found >= 2
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        print("\n📊 GENERATING COMPREHENSIVE ANALYSIS REPORT")
        print("=" * 60)
        
        # Extract all text
        self.extract_all_text()
        
        # Analyze TOC
        toc_recipes = self.analyze_table_of_contents()
        
        # Pattern-based search
        pattern_recipes = self.find_all_recipes_by_pattern()
        
        # Summary
        print(f"\n📈 ANALYSIS SUMMARY")
        print("=" * 30)
        print(f"📄 Total pages analyzed: {len(self.all_text.split('--- PAGE')) - 1}")
        print(f"📋 Table of Contents pages: {len(self.toc_pages)}")
        print(f"📝 Recipes found in TOC: {len(toc_recipes)}")
        print(f"🔍 Recipes found by pattern: {len(pattern_recipes)}")
        print(f"📍 Pages with recipe content: {len(self.recipe_locations)}")
        
        # Detailed recipe list
        if toc_recipes:
            print(f"\n📋 RECIPES FROM TABLE OF CONTENTS:")
            print("-" * 40)
            for i, recipe in enumerate(toc_recipes, 1):
                print(f"{i:3d}. {recipe['title']} (page {recipe['page']})")
        
        return {
            'total_pages': len(self.all_text.split('--- PAGE')) - 1,
            'toc_pages': len(self.toc_pages),
            'toc_recipes': toc_recipes,
            'pattern_recipes': pattern_recipes,
            'recipe_content_pages': self.recipe_locations,
            'estimated_total_recipes': max(len(toc_recipes), len(pattern_recipes))
        }

def main():
    pdf_path = 'The Complete Cookbook for Teen - America\'s Test Kitchen Kids.pdf'
    
    print("🚀 ATK TEENS COOKBOOK CONTENT ANALYZER")
    print("=" * 50)
    
    analyzer = ATKTeensPDFAnalyzer(pdf_path)
    report = analyzer.generate_report()
    
    print(f"\n🎯 FINAL ASSESSMENT:")
    print(f"  Estimated total recipes: {report['estimated_total_recipes']}")
    print(f"  Previous extraction found: 57 recipes")
    print(f"  Extraction accuracy: {57/report['estimated_total_recipes']*100:.1f}%" if report['estimated_total_recipes'] > 0 else "Unknown")

if __name__ == "__main__":
    main()
