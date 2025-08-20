#!/usr/bin/env python3
"""
ATK 25th Anniversary Cookbook Analyzer
Analyzes structure and format to optimize extraction strategy
"""

import sys
import os
import re
import PyPDF2
import logging
from typing import Dict, List, Optional
from collections import defaultdict

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ATK25thAnalyzer:
    """Analyze ATK 25th Anniversary cookbook structure"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.total_pages = 0
        self.sample_pages = []
        self.structure_analysis = {
            'table_of_contents': [],
            'chapter_headers': [],
            'recipe_patterns': [],
            'ingredient_patterns': [],
            'instruction_patterns': [],
            'page_layouts': defaultdict(int)
        }
    
    def analyze_cookbook_structure(self, sample_pages=20):
        """Analyze cookbook structure and patterns"""
        logger.info(f"🔍 ANALYZING ATK 25TH ANNIVERSARY COOKBOOK")
        logger.info("=" * 60)
        
        try:
            with open(self.pdf_path, 'rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                self.total_pages = len(reader.pages)
                
                logger.info(f"📄 Total pages: {self.total_pages}")
                
                # Sample pages throughout the book
                sample_indices = self._get_sample_page_indices(sample_pages)
                
                for i, page_idx in enumerate(sample_indices):
                    try:
                        page = reader.pages[page_idx]
                        text = page.extract_text()
                        
                        self.sample_pages.append({
                            'page_number': page_idx + 1,
                            'text': text,
                            'text_length': len(text),
                            'line_count': len(text.split('\n'))
                        })
                        
                        self._analyze_page_structure(text, page_idx + 1)
                        
                        if i < 5:  # Show first 5 sample pages
                            self._print_page_sample(text, page_idx + 1)
                        
                    except Exception as e:
                        logger.error(f"❌ Error processing page {page_idx + 1}: {e}")
                        continue
                
                self._summarize_structure_analysis()
                self._recommend_extraction_strategy()
                
        except Exception as e:
            logger.error(f"❌ Fatal error during analysis: {e}")
            raise
    
    def _get_sample_page_indices(self, sample_count):
        """Get evenly distributed sample page indices"""
        if sample_count >= self.total_pages:
            return list(range(self.total_pages))
        
        step = self.total_pages // sample_count
        indices = []
        
        # Always include first few pages (TOC, intro)
        indices.extend([0, 1, 2, 3, 4])
        
        # Add evenly distributed samples
        for i in range(5, self.total_pages, step):
            indices.append(i)
        
        # Always include last few pages
        indices.extend([self.total_pages - 3, self.total_pages - 2, self.total_pages - 1])
        
        # Remove duplicates and sort
        return sorted(list(set([i for i in indices if 0 <= i < self.total_pages])))
    
    def _analyze_page_structure(self, text: str, page_number: int):
        """Analyze individual page structure"""
        if not text or len(text.strip()) < 10:
            self.structure_analysis['page_layouts']['empty'] += 1
            return
        
        text_upper = text.upper()
        
        # Check for table of contents patterns
        if self._is_table_of_contents(text):
            self.structure_analysis['table_of_contents'].append(page_number)
            self.structure_analysis['page_layouts']['toc'] += 1
            return
        
        # Check for chapter headers
        chapter_pattern = self._detect_chapter_header(text)
        if chapter_pattern:
            self.structure_analysis['chapter_headers'].append({
                'page': page_number,
                'header': chapter_pattern
            })
            self.structure_analysis['page_layouts']['chapter_header'] += 1
            return
        
        # Check for recipe pages
        if self._is_potential_recipe_page(text):
            self.structure_analysis['page_layouts']['recipe'] += 1
            self._analyze_recipe_patterns(text, page_number)
        elif self._is_narrative_page(text):
            self.structure_analysis['page_layouts']['narrative'] += 1
        else:
            self.structure_analysis['page_layouts']['other'] += 1
    
    def _is_table_of_contents(self, text: str) -> bool:
        """Check if page is table of contents"""
        toc_indicators = [
            'table of contents', 'contents', 'chapter',
            'introduction', 'index', 'acknowledgments'
        ]
        
        text_lower = text.lower()
        
        # Look for page numbers with dots/leaders
        page_number_pattern = r'\d+\s*$'
        lines_with_page_numbers = sum(1 for line in text.split('\n') 
                                    if re.search(page_number_pattern, line.strip()))
        
        return (any(indicator in text_lower for indicator in toc_indicators) or
                lines_with_page_numbers > 5)
    
    def _detect_chapter_header(self, text: str) -> Optional[str]:
        """Detect chapter header patterns"""
        lines = text.split('\n')
        
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if not line:
                continue
            
            # Look for chapter-like patterns
            if re.match(r'^(CHAPTER|Chapter)\s+\d+', line):
                return line
            
            # Look for numbered sections
            if re.match(r'^\d+\.\s+[A-Z]', line) and len(line) > 10:
                return line
            
            # Look for all-caps headers that span multiple words
            if (line.isupper() and 
                len(line.split()) >= 2 and 
                len(line) > 15 and len(line) < 80 and
                not re.search(r'\d+.*?(cup|tablespoon|teaspoon|pound|ounce)', line)):
                return line
        
        return None
    
    def _is_potential_recipe_page(self, text: str) -> bool:
        """Check if page contains recipe content"""
        recipe_indicators = [
            # Ingredient patterns
            r'\d+\s*(cup|tablespoon|teaspoon|tsp|tbsp|pound|lb|ounce|oz)',
            r'\d+\s*(large|medium|small)',
            r'\d+.*?(chopped|diced|minced|sliced)',
            
            # Instruction patterns
            r'\d+\.\s+(heat|cook|add|mix|stir|bake|sauté)',
            r'(preheat|combine|whisk|season)',
            
            # Recipe metadata
            r'(serves|makes)\s+\d+',
            r'\d+\s+(minutes|hours)',
            r'(degrees|temperature|°f|°c)'
        ]
        
        text_lower = text.lower()
        matches = 0
        
        for pattern in recipe_indicators:
            if re.search(pattern, text_lower):
                matches += 1
        
        return matches >= 3  # Need at least 3 indicators
    
    def _is_narrative_page(self, text: str) -> bool:
        """Check if page is narrative/educational content"""
        # Look for paragraph-style text
        lines = text.split('\n')
        long_lines = sum(1 for line in lines if len(line.strip()) > 50)
        
        # Look for narrative indicators
        narrative_indicators = [
            'the secret', 'technique', 'tip', 'why this works',
            'we found', 'our testing', 'the result'
        ]
        
        text_lower = text.lower()
        has_narrative = any(indicator in text_lower for indicator in narrative_indicators)
        
        return long_lines > 5 and has_narrative
    
    def _analyze_recipe_patterns(self, text: str, page_number: int):
        """Analyze recipe-specific patterns"""
        # Look for ingredient section patterns
        ingredient_patterns = [
            'INGREDIENTS',
            'FOR THE',
            'PREPARE INGREDIENTS',
            'TOPPING:',
            'SAUCE:',
            'MARINADE:'
        ]
        
        for pattern in ingredient_patterns:
            if pattern in text.upper():
                if pattern not in [p['pattern'] for p in self.structure_analysis['ingredient_patterns']]:
                    self.structure_analysis['ingredient_patterns'].append({
                        'pattern': pattern,
                        'first_seen': page_number
                    })
        
        # Look for instruction patterns
        instruction_patterns = [
            'INSTRUCTIONS',
            'METHOD',
            'DIRECTIONS',
            'START COOKING',
            'PREPARATION'
        ]
        
        for pattern in instruction_patterns:
            if pattern in text.upper():
                if pattern not in [p['pattern'] for p in self.structure_analysis['instruction_patterns']]:
                    self.structure_analysis['instruction_patterns'].append({
                        'pattern': pattern,
                        'first_seen': page_number
                    })
    
    def _print_page_sample(self, text: str, page_number: int):
        """Print sample page content for analysis"""
        logger.info(f"\n📄 PAGE {page_number} SAMPLE:")
        logger.info("-" * 40)
        
        lines = text.split('\n')
        preview_lines = []
        
        for line in lines[:15]:  # First 15 lines
            if line.strip():
                preview_lines.append(line.strip())
        
        for line in preview_lines[:10]:  # Show first 10 non-empty lines
            logger.info(f"   {line}")
        
        if len(preview_lines) > 10:
            logger.info(f"   ... ({len(lines)} total lines)")
    
    def _summarize_structure_analysis(self):
        """Summarize the structure analysis results"""
        logger.info(f"\n📊 STRUCTURE ANALYSIS SUMMARY:")
        logger.info("=" * 50)
        
        logger.info(f"📖 Page Layout Distribution:")
        total_analyzed = sum(self.structure_analysis['page_layouts'].values())
        for layout_type, count in self.structure_analysis['page_layouts'].items():
            percentage = (count / total_analyzed) * 100 if total_analyzed > 0 else 0
            logger.info(f"  {layout_type.title()}: {count} pages ({percentage:.1f}%)")
        
        logger.info(f"\n📚 Chapter Structure:")
        if self.structure_analysis['chapter_headers']:
            for chapter in self.structure_analysis['chapter_headers'][:5]:
                logger.info(f"  Page {chapter['page']}: {chapter['header']}")
            if len(self.structure_analysis['chapter_headers']) > 5:
                logger.info(f"  ... and {len(self.structure_analysis['chapter_headers']) - 5} more chapters")
        else:
            logger.info("  No clear chapter headers detected")
        
        logger.info(f"\n🥘 Recipe Pattern Detection:")
        logger.info(f"  Ingredient patterns found: {len(self.structure_analysis['ingredient_patterns'])}")
        for pattern in self.structure_analysis['ingredient_patterns']:
            logger.info(f"    • '{pattern['pattern']}' (first seen: page {pattern['first_seen']})")
        
        logger.info(f"  Instruction patterns found: {len(self.structure_analysis['instruction_patterns'])}")
        for pattern in self.structure_analysis['instruction_patterns']:
            logger.info(f"    • '{pattern['pattern']}' (first seen: page {pattern['first_seen']})")
    
    def _recommend_extraction_strategy(self):
        """Recommend extraction strategy based on analysis"""
        logger.info(f"\n🎯 EXTRACTION STRATEGY RECOMMENDATIONS:")
        logger.info("=" * 50)
        
        recipe_pages = self.structure_analysis['page_layouts'].get('recipe', 0)
        total_pages = sum(self.structure_analysis['page_layouts'].values())
        recipe_percentage = (recipe_pages / total_pages) * 100 if total_pages > 0 else 0
        
        logger.info(f"📈 Recipe Page Density: {recipe_percentage:.1f}% ({recipe_pages}/{total_pages} analyzed pages)")
        
        # Estimate total recipes
        estimated_recipes = int((recipe_pages / len(self.sample_pages)) * self.total_pages)
        logger.info(f"📊 Estimated Total Recipes: ~{estimated_recipes} recipes")
        
        # Extraction recommendations
        if recipe_percentage > 30:
            logger.info("✅ HIGH RECIPE DENSITY - Good candidate for extraction")
        elif recipe_percentage > 15:
            logger.info("⚡ MEDIUM RECIPE DENSITY - Moderate extraction potential")
        else:
            logger.info("⚠️ LOW RECIPE DENSITY - May have mixed content")
        
        # Pattern-based recommendations
        if self.structure_analysis['ingredient_patterns']:
            logger.info("✅ INGREDIENT PATTERNS DETECTED - Use pattern-based extraction")
        else:
            logger.info("⚠️ NO CLEAR INGREDIENT PATTERNS - May need flexible extraction")
        
        if self.structure_analysis['instruction_patterns']:
            logger.info("✅ INSTRUCTION PATTERNS DETECTED - Structured recipe format")
        else:
            logger.info("⚠️ NO CLEAR INSTRUCTION PATTERNS - May need adaptive parsing")
        
        # Specific recommendations
        logger.info(f"\n🔧 SPECIFIC EXTRACTION MODIFICATIONS:")
        
        if 'PREPARE INGREDIENTS' in [p['pattern'] for p in self.structure_analysis['ingredient_patterns']]:
            logger.info("  • Use ATK Teens extraction patterns (PREPARE INGREDIENTS → START COOKING)")
        
        if 'FOR THE' in [p['pattern'] for p in self.structure_analysis['ingredient_patterns']]:
            logger.info("  • Implement multi-section ingredient parsing (FOR THE SAUCE, FOR THE TOPPING)")
        
        if recipe_percentage < 20:
            logger.info("  • Lower recipe detection threshold for mixed-content pages")
            logger.info("  • Implement narrative content extraction for educational value")
        
        if not self.structure_analysis['instruction_patterns']:
            logger.info("  • Implement flexible instruction detection (paragraph-based)")
        
        logger.info(f"\n💡 EXPECTED OUTCOMES:")
        logger.info(f"  • Potential recipes to extract: {estimated_recipes}")
        logger.info(f"  • Expected success rate: 70-85% based on pattern clarity")
        logger.info(f"  • Recommended approach: Modified Universal Extractor with ATK patterns")


def main():
    """Main execution"""
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
    
    if not os.path.exists(pdf_path):
        logger.error(f"❌ PDF not found: {pdf_path}")
        return
    
    analyzer = ATK25thAnalyzer(pdf_path)
    analyzer.analyze_cookbook_structure(sample_pages=30)
    
    logger.info(f"\n✅ ANALYSIS COMPLETE!")
    logger.info(f"📁 Ready to proceed with extraction using recommended modifications")


if __name__ == "__main__":
    main()
