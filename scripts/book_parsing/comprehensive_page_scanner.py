"""
Comprehensive Page Scanner
Scan ALL pages to see what we're missing
"""

import pdfplumber
import re
from pathlib import Path

class ComprehensivePageScanner:
    """Scan all pages to find recipe patterns"""
    
    def scan_all_pages(self, pdf_path: str):
        """Scan every page and categorize content"""
        
        print(f"🔍 COMPREHENSIVE PAGE SCAN: {Path(pdf_path).name}")
        print("=" * 80)
        
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"📄 Total Pages: {total_pages}")
            
            recipe_pages = []
            content_pages = []
            toc_pages = []
            intro_pages = []
            other_pages = []
            
            for page_num in range(min(total_pages, 100)):  # Check first 100 pages
                page = pdf.pages[page_num]
                text = page.extract_text()
                
                if not text:
                    continue
                
                lines = text.split('\\n')
                page_type = self._categorize_page(lines, page_num + 1)
                
                if page_type == 'recipe':
                    recipe_pages.append(page_num + 1)
                elif page_type == 'content':
                    content_pages.append(page_num + 1)
                elif page_type == 'toc':
                    toc_pages.append(page_num + 1)
                elif page_type == 'intro':
                    intro_pages.append(page_num + 1)
                else:
                    other_pages.append(page_num + 1)
                
                # Show sample pages
                if page_num < 20 or page_num % 10 == 0:
                    print(f"\\n📄 Page {page_num + 1} ({page_type.upper()}):")
                    self._show_page_sample(lines)
        
        # Summary
        print("\\n" + "=" * 80)
        print("📊 PAGE CATEGORIZATION SUMMARY")
        print("=" * 80)
        print(f"🍳 Recipe Pages: {len(recipe_pages)} - {recipe_pages[:20]}{'...' if len(recipe_pages) > 20 else ''}")
        print(f"📝 Content Pages: {len(content_pages)} - {content_pages[:20]}{'...' if len(content_pages) > 20 else ''}")
        print(f"📑 Table of Contents: {len(toc_pages)} - {toc_pages}")
        print(f"📖 Introduction Pages: {len(intro_pages)} - {intro_pages}")
        print(f"❓ Other Pages: {len(other_pages)} - {other_pages[:20]}{'...' if len(other_pages) > 20 else ''}")
        
        return {
            'recipe_pages': recipe_pages,
            'content_pages': content_pages,
            'toc_pages': toc_pages,
            'intro_pages': intro_pages,
            'other_pages': other_pages
        }
    
    def _categorize_page(self, lines: list, page_num: int) -> str:
        """Categorize what type of page this is"""
        
        text_content = ' '.join(lines).upper()
        
        # Recipe indicators (multiple patterns)
        recipe_indicators = [
            'HANDS-ON TIME',
            'TOTAL TIME', 
            'PREP TIME',
            'COOK TIME',
            'COOKING TIME',
            'SERVINGS',
            'SERVES',
            'MAKES',
            'INGREDIENTS',
            'DIRECTIONS',
            'INSTRUCTIONS',
            'METHOD',
            'PREPARATION'
        ]
        
        # Table of contents indicators
        toc_indicators = [
            'CONTENTS',
            'TABLE OF CONTENTS',
            'INDEX',
            'CHAPTER'
        ]
        
        # Introduction indicators
        intro_indicators = [
            'INTRODUCTION',
            'FOREWORD',
            'PREFACE',
            'ABOUT THIS BOOK',
            'HOW TO USE'
        ]
        
        # Count recipe indicators
        recipe_score = sum(1 for indicator in recipe_indicators if indicator in text_content)
        
        # Strong recipe indicators
        strong_recipe_indicators = [
            'HANDS-ON TIME',
            'TOTAL TIME',
            'INGREDIENTS INGREDIENTS',  # Dual column
            'DIRECTIONS DIRECTIONS'     # Dual column
        ]
        
        has_strong_recipe = any(indicator in text_content for indicator in strong_recipe_indicators)
        
        # Categorize
        if has_strong_recipe or recipe_score >= 3:
            return 'recipe'
        elif any(indicator in text_content for indicator in toc_indicators):
            return 'toc'
        elif any(indicator in text_content for indicator in intro_indicators):
            return 'intro'
        elif recipe_score >= 1:
            return 'content'  # Might be recipe-related content
        else:
            return 'other'
    
    def _show_page_sample(self, lines: list):
        """Show sample of page content"""
        
        # Show non-empty lines
        content_lines = [line.strip() for line in lines if line.strip() and len(line.strip()) > 3]
        
        for i, line in enumerate(content_lines[:8]):  # First 8 meaningful lines
            print(f"      {i+1:2d}: {line[:60]}{'...' if len(line) > 60 else ''}")
        
        if len(content_lines) > 8:
            print(f"         ... and {len(content_lines) - 8} more lines")
    
    def find_recipe_patterns(self, pdf_path: str):
        """Find all different recipe title patterns"""
        
        print(f"\\n🔍 RECIPE PATTERN ANALYSIS")
        print("=" * 60)
        
        patterns_found = set()
        recipe_titles = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num in range(min(len(pdf.pages), 50)):
                page = pdf.pages[page_num]
                text = page.extract_text()
                
                if not text:
                    continue
                
                lines = text.split('\\n')
                
                # Look for potential recipe titles
                for i, line in enumerate(lines):
                    line_clean = line.strip().upper()
                    
                    # Skip header/footer
                    if any(skip in line_clean for skip in ['CANADIAN LIVING', 'ULTIMATE', 'COOKBOOK']):
                        continue
                    
                    # Look for title patterns
                    if (len(line_clean) > 5 and len(line_clean) < 50 and
                        not any(keyword in line_clean for keyword in ['HANDS-ON', 'TOTAL', 'MAKES', 'INGREDIENTS', 'DIRECTIONS']) and
                        not line_clean.isdigit()):
                        
                        # Check if followed by recipe indicators
                        next_lines = lines[i+1:i+5] if i+1 < len(lines) else []
                        next_text = ' '.join(next_lines).upper()
                        
                        if any(indicator in next_text for indicator in ['HANDS-ON', 'TOTAL', 'SERVINGS', 'INGREDIENTS']):
                            recipe_titles.append((page_num + 1, line_clean))
                            
                            # Extract pattern
                            pattern = self._extract_title_pattern(line_clean)
                            patterns_found.add(pattern)
        
        print(f"📋 Found {len(recipe_titles)} potential recipe titles:")
        for page, title in recipe_titles[:20]:
            print(f"   📄 Page {page:3d}: {title}")
        
        if len(recipe_titles) > 20:
            print(f"   ... and {len(recipe_titles) - 20} more")
        
        print(f"\\n🎯 Title Patterns Found:")
        for pattern in sorted(patterns_found):
            print(f"   - {pattern}")
        
        return recipe_titles, patterns_found
    
    def _extract_title_pattern(self, title: str) -> str:
        """Extract general pattern from title"""
        
        if re.match(r'^[A-Z\\s]+$', title):
            return "ALL CAPS"
        elif re.match(r'^[A-Z][a-z\\s]+$', title):
            return "Title Case"
        elif '&' in title:
            return "Contains &"
        elif 'AND' in title:
            return "Contains AND"
        else:
            return "Mixed Case"


def main():
    """Run comprehensive page scan"""
    
    pdf_path = "books_archive/Canadian-Living-The-Ultimate-Cookbook.pdf"
    
    scanner = ComprehensivePageScanner()
    
    # Scan all pages
    results = scanner.scan_all_pages(pdf_path)
    
    # Find recipe patterns
    titles, patterns = scanner.find_recipe_patterns(pdf_path)
    
    print(f"\\n🎯 CONCLUSION:")
    print(f"   📄 Total pages analyzed: ~100")
    print(f"   🍳 Potential recipe pages: {len(results['recipe_pages'])}")
    print(f"   📝 Recipe titles found: {len(titles)}")
    
    if len(titles) > 49:
        print(f"   ⚠️ We should have found {len(titles)} recipes, not just 49!")
        print(f"   🔧 Parser needs to be less strict in recipe detection")


if __name__ == "__main__":
    main()
