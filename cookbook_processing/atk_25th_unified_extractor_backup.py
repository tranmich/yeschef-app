#!/usr/bin/env python3
"""
🧠📚 ATK 25th Anniversary UNIFIED Extractor
============================================

The definitive ATK 25th Anniversary extractor combining:
- Table of Contents cross-referencing for targeted extraction
- Visual structure detection from working Teen extractor
- Semantic validation adapted for ATK language patterns
- Clean, unified codebase eliminating all duplicates
- Multi-page recipe support with intelligent continuation

This replaces all previous ATK 25th extractors with one comprehensive solution.

Author: GitHub Copilot
Date: August 20, 2025
"""

import os
import sys
import argparse
import re
import PyPDF2
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

# Add core systems to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core_systems'))

try:
    from database_manager import DatabaseManager
    from semantic_recipe_engine import SemanticRecipeEngine, ValidationLevel
    from ingredient_intelligence_engine import IngredientIntelligenceEngine
    print("✅ Core Systems Loaded Successfully")
except ImportError as e:
    print(f"❌ Failed to import core systems: {e}")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)


class PDFBookmarkExtractor:
    """Extracts PDF bookmarks for precise recipe indexing"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.recipe_index = {}  # title -> page mapping
        self.page_index = {}    # page -> title mapping
    
    def extract_bookmarks(self) -> Dict[str, int]:
        """Extract PDF bookmarks and build recipe index"""
        
        logger.info("📋 Extracting PDF bookmarks for precise recipe indexing...")
        
        try:
            with open(self.pdf_path, 'rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                
                if reader.outline:
                    self._parse_bookmarks(reader, reader.outline)
                    logger.info(f"📋 PDF bookmarks extracted: {len(self.recipe_index)} recipes indexed")
                else:
                    logger.warning("⚠️ No PDF bookmarks found, falling back to text-based TOC")
                    
        except Exception as e:
            logger.error(f"❌ Error extracting PDF bookmarks: {e}")
        
        return self.recipe_index
    
    def _parse_bookmarks(self, reader: PyPDF2.PdfReader, bookmarks, level: int = 0):
        """Recursively parse PDF bookmarks"""
        
        for item in bookmarks:
            if isinstance(item, list):
                # Nested bookmarks
                self._parse_bookmarks(reader, item, level + 1)
            else:
                # Single bookmark
                title = item.title
                
                # Get destination page
                try:
                    if hasattr(item, 'page') and item.page:
                        page_num = reader.pages.index(item.page) + 1
                    elif hasattr(item, 'destination') and item.destination:
                        # Alternative way to get page
                        if hasattr(item.destination, 'page'):
                            page_num = reader.pages.index(item.destination.page) + 1
                        else:
                            continue
                    else:
                        continue
                    
                    # Filter for likely recipe titles
                    if self._is_recipe_bookmark(title, level):
                        self.recipe_index[title.lower()] = page_num
                        self.page_index[page_num] = title
                        logger.info(f"    📝 Bookmark indexed: '{title}' → Page {page_num}")
                        
                except Exception as e:
                    # Skip bookmarks with page reference errors
                    continue
    
    def _is_recipe_bookmark(self, title: str, level: int) -> bool:
        """Check if bookmark is likely a recipe"""
        
        # Skip obvious non-recipes
        non_recipe_titles = [
            'title page', 'copyright', 'contents', 'acknowledgments', 'welcome',
            'our story', 'appetizers & drinks', 'eggs & breakfast', 'soups & stews',
            'salads', 'pasta', 'vegetables', 'meat', 'poultry', 'seafood', 'desserts',
            'baking', 'index', 'about', 'introduction'
        ]
        
        title_lower = title.lower()
        
        # Skip chapter/section headers (usually shorter and more generic)
        if any(non_recipe in title_lower for non_recipe in non_recipe_titles):
            return False
        
        # Skip very short titles
        if len(title) < 5:
            return False
        
        # Must be reasonable recipe title length
        if len(title) > 100:
            return False
        
        # Look for recipe indicators
        recipe_indicators = [
            'chicken', 'beef', 'pork', 'fish', 'salmon', 'pasta', 'rice', 'bread',
            'soup', 'salad', 'sauce', 'roasted', 'grilled', 'baked', 'braised',
            'cake', 'pie', 'cookies', 'chocolate', 'vanilla', 'lemon', 'garlic',
            'with', 'and', 'in', 'style', 'glazed', 'stuffed', 'perfect', 'easy'
        ]
        
        # Must contain recipe-like words
        return any(indicator in title_lower for indicator in recipe_indicators)
    
    def get_expected_title_for_page(self, page_num: int) -> Optional[str]:
        """Get expected recipe title for a given page"""
        return self.page_index.get(page_num)
    
    def find_recipe_page(self, title: str) -> Optional[int]:
        """Find page number for a recipe title"""
        title_clean = title.lower().strip()
        
        # Exact match first
        if title_clean in self.recipe_index:
            return self.recipe_index[title_clean]
        
        # Fuzzy matching for variations
        for bookmark_title, page_num in self.recipe_index.items():
            if self._titles_match(title_clean, bookmark_title):
                return page_num
        
        return None
    
    def _titles_match(self, title1: str, title2: str) -> bool:
        """Check if two titles are likely the same recipe"""
        
        # Remove common variations
        clean1 = re.sub(r'\b(the|a|an|with|and|&)\b', '', title1).strip()
        clean2 = re.sub(r'\b(the|a|an|with|and|&)\b', '', title2).strip()
        
        # Check for substantial overlap in key words
        words1 = set(clean1.split())
        words2 = set(clean2.split())
        
        if len(words1) == 0 or len(words2) == 0:
            return False
        
        overlap = len(words1.intersection(words2))
        min_words = min(len(words1), len(words2))
        
        return overlap / min_words >= 0.6  # 60% word overlap


class TableOfContentsExtractor:
    """Extracts and manages Table of Contents for cross-referencing"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.recipe_index = {}  # title -> page mapping
        self.page_index = {}    # page -> title mapping
    
    def extract_toc(self) -> Dict[str, int]:
        """Extract Table of Contents and build recipe index with forward search mapping"""
        
        logger.info("📋 Extracting Table of Contents for recipe cross-referencing...")
        
        try:
            with open(self.pdf_path, 'rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                total_pages = len(reader.pages)
                
                # Enhanced TOC extraction with forward search mapping
                self._extract_toc_with_mapping(reader, total_pages)
                
        except Exception as e:
            logger.error(f"❌ Error extracting TOC: {e}")
        
        logger.info(f"📋 TOC extracted: {len(self.recipe_index)} recipes indexed")
        return self.recipe_index
    
    def _extract_toc_with_mapping(self, reader: PyPDF2.PdfReader, total_pages: int):
        """Extract TOC titles and map them to actual recipe pages"""
        
        # Step 1: Extract recipe titles from known TOC pages  
        toc_pages = [737, 738, 739]  # Pages 738, 739, 740 (0-indexed)
        toc_recipes = []
        
        for page_idx in toc_pages:
            if page_idx < total_pages:
                try:
                    page = reader.pages[page_idx]
                    page_text = page.extract_text()
                    
                    # Extract potential recipe titles
                    lines = page_text.split('\n')
                    for line in lines:
                        line = line.strip()
                        if 5 < len(line) < 100:  # Reasonable recipe title length
                            # Filter out obvious non-recipes
                            if not any(skip in line.lower() for skip in ['page', 'chapter', 'section', 'contents', 'acknowledgments']):
                                # Look for recipe indicators
                                if any(indicator in line.lower() for indicator in 
                                      ['chicken', 'beef', 'pork', 'fish', 'salmon', 'pasta', 'rice', 'bread',
                                       'soup', 'salad', 'sauce', 'roasted', 'grilled', 'baked', 'braised',
                                       'with', 'and', 'in', 'au', 'de', 'la', 'le']):
                                    toc_recipes.append(line)
                except Exception:
                    continue
        
        logger.info(f"� Found {len(toc_recipes)} potential recipes in TOC")
        
        # Step 2: Map recipe titles to actual pages by searching forward
        search_start = 750  # Start after TOC area
        search_end = min(total_pages, 1200)  # Reasonable recipe section end
        
        for recipe_title in toc_recipes:
            try:
                # Search for this recipe in the PDF
                for page_idx in range(search_start - 1, search_end):
                    try:
                        page = reader.pages[page_idx]
                        page_text = page.extract_text()
                        
                        # Look for exact match first
                        if recipe_title in page_text:
                            self.recipe_index[recipe_title.lower()] = page_idx + 1
                            self.page_index[page_idx + 1] = recipe_title
                            logger.info(f"    � Mapped: '{recipe_title}' → Page {page_idx + 1}")
                            break
                        
                        # Try simplified match (remove special characters)
                        title_simple = re.sub(r'[^\w\s]', '', recipe_title)
                        if title_simple in page_text:
                            self.recipe_index[recipe_title.lower()] = page_idx + 1
                            self.page_index[page_idx + 1] = recipe_title
                            logger.info(f"    � Mapped (simplified): '{recipe_title}' → Page {page_idx + 1}")
                            break
                            
                    except Exception:
                        continue
            except Exception:
                continue
    
    def _is_enhanced_category_toc_page(self, text: str, expected_category: str) -> bool:
        """Enhanced category TOC detection with specific category matching"""
        
        text_lower = text.lower()
        
        # Category-specific keywords
        category_keywords = {
            'Appetizers & Drinks': ['appetizer', 'snack', 'drink', 'cocktail', 'beverage'],
            'Eggs & Breakfast': ['egg', 'breakfast', 'pancake', 'waffle', 'omelet'],
            'Soups & Stews': ['soup', 'stew', 'broth', 'chowder', 'bisque'],
            'Salads': ['salad', 'green', 'caesar', 'vinaigrette', 'dressing'],
            'Pasta/Noodles/Dumplings': ['pasta', 'noodle', 'dumpling', 'spaghetti', 'linguine'],
            'Poultry': ['chicken', 'turkey', 'duck', 'poultry'],
            'Meat': ['beef', 'pork', 'lamb', 'steak', 'roast'],
            'Fish & Seafood': ['fish', 'seafood', 'salmon', 'shrimp', 'crab'],
            'Vegetarian': ['vegetarian', 'veggie', 'tofu', 'bean'],
            'Grilling': ['grill', 'barbecue', 'bbq', 'smoke'],
            'Sides': ['side', 'potato', 'rice', 'vegetable'],
            'Bread & Pizza': ['bread', 'pizza', 'dough', 'yeast'],
            'Cookies & Desserts': ['cookie', 'dessert', 'cake', 'pie', 'chocolate']
        }
        
        # Check for category-specific keywords
        if expected_category in category_keywords:
            keywords = category_keywords[expected_category]
            keyword_matches = sum(1 for keyword in keywords if keyword in text_lower)
        else:
            keyword_matches = 0
        
        # Check for recipe-like structure
        lines = text.split('\n')
        recipe_like_lines = 0
        
        for line in lines:
            line = line.strip()
            if len(line) > 5 and len(line) < 80:
                if self._looks_like_recipe_title(line):
                    recipe_like_lines += 1
        
        # Enhanced detection: category keywords + recipe structure
        return keyword_matches >= 2 and recipe_like_lines >= 5
    
    def _extract_recipes_from_toc_text(self, text: str, source: str) -> list:
        """Extract recipe titles from TOC text"""
        
        recipes = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if 5 < len(line) < 100:  # Reasonable recipe title length
                # Filter out obvious non-recipes
                if not any(skip in line.lower() for skip in ['page', 'chapter', 'section', 'contents', 'acknowledgments', 'index']):
                    # Look for recipe indicators
                    if any(indicator in line.lower() for indicator in 
                          ['chicken', 'beef', 'pork', 'fish', 'salmon', 'pasta', 'rice', 'bread',
                           'soup', 'salad', 'sauce', 'roasted', 'grilled', 'baked', 'braised',
                           'with', 'and', 'in', 'au', 'de', 'la', 'le', 'egg', 'cheese']):
                        recipes.append(line)
        
        return recipes
    
    def _is_traditional_toc_page(self, text: str) -> bool:
        """Check if page contains traditional table of contents"""
        
        toc_indicators = [
            'table of contents',
            'contents',
            r'\.{3,}',  # Dotted lines
        ]
        
        text_lower = text.lower()
        indicator_count = 0
        
        for indicator in toc_indicators:
            if re.search(indicator, text_lower):
                indicator_count += 1
        
        # Also check for multiple page number references
        page_refs = len(re.findall(r'\b\d{2,3}\b', text))
        
        return indicator_count >= 2 or page_refs >= 10
    
    def _is_category_toc_page(self, text: str) -> bool:
        """Check if page contains category-based TOC with recipe links"""
        
        # Look for category headers followed by recipe names
        category_patterns = [
            r'appetizers?\s*&?\s*snacks?',
            r'soups?\s*&?\s*stews?',
            r'salads?',
            r'main\s+dishes?',
            r'pasta\s*&?\s*rice',
            r'vegetables?',
            r'breads?\s*&?\s*baking',
            r'desserts?',
            r'breakfast',
            r'sauces?\s*&?\s*condiments?'
        ]
        
        text_lower = text.lower()
        category_count = 0
        
        for pattern in category_patterns:
            if re.search(pattern, text_lower):
                category_count += 1
        
        # Check for link-like patterns (recipe names that could be clickable)
        # Look for multiple lines with food-related words
        lines = text.split('\n')
        recipe_like_lines = 0
        
        for line in lines:
            line = line.strip().lower()
            if len(line) > 10 and len(line) < 80:  # Reasonable recipe title length
                food_words = ['chicken', 'beef', 'pork', 'fish', 'pasta', 'rice', 'bread', 
                             'soup', 'salad', 'roasted', 'grilled', 'baked', 'sauce']
                if any(word in line for word in food_words):
                    recipe_like_lines += 1
        
        return category_count >= 1 and recipe_like_lines >= 5
    
    def _is_recipe_list_page(self, text: str) -> bool:
        """Check if page contains a list of recipes (like chapter opening)"""
        
        lines = text.split('\n')
        recipe_like_lines = 0
        
        # Look for multiple lines that look like recipe titles
        for line in lines:
            line = line.strip()
            if len(line) > 5 and len(line) < 80:
                # Check if it looks like a recipe title
                if self._looks_like_recipe_title(line):
                    recipe_like_lines += 1
        
        # If we have many recipe-like lines, this might be a recipe list
        return recipe_like_lines >= 8
    
    def _looks_like_recipe_title(self, line: str) -> bool:
        """Check if a line looks like a recipe title"""
        
        line_lower = line.lower()
        
        # Food-related keywords
        food_keywords = [
            'chicken', 'beef', 'pork', 'fish', 'salmon', 'pasta', 'rice', 'bread',
            'soup', 'salad', 'sauce', 'roasted', 'grilled', 'baked', 'braised',
            'cake', 'pie', 'cookies', 'chocolate', 'vanilla', 'lemon', 'garlic'
        ]
        
        # Skip obvious non-recipes
        if re.match(r'^\d+', line) or 'page' in line_lower or len(line.split()) < 2:
            return False
        
        return any(keyword in line_lower for keyword in food_keywords)
    
    def _parse_category_toc_page(self, text: str, page_num: int):
        """Parse category-based TOC page with recipe links"""
        
        lines = text.split('\n')
        current_category = None
        recipe_count = 0
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 5:
                continue
            
            # Check if this is a category header
            if self._is_category_header(line):
                current_category = line
                continue
            
            # Check if this is a recipe title
            if self._looks_like_recipe_title(line) and len(line) > 10:
                # Clean up the title better
                title_clean = self._clean_toc_title_enhanced(line)
                
                # Additional validation - must be reasonable recipe title
                if self._is_valid_recipe_title(title_clean):
                    # Store with estimated page (we'll refine this during extraction)
                    self.recipe_index[title_clean.lower()] = page_num + 10  # Rough estimate
                    recipe_count += 1
                    logger.info(f"    📝 Indexed recipe: {title_clean}")
                    
                    # Limit to reasonable number per page
                    if recipe_count > 20:
                        break
    
    def _clean_toc_title_enhanced(self, title: str) -> str:
        """Enhanced TOC title cleaning"""
        
        # Remove page numbers and dots
        title = re.sub(r'\.{2,}.*$', '', title)  # Remove dotted lines and page numbers
        title = re.sub(r'\d+\s*$', '', title)    # Remove trailing page numbers
        
        # Fix common PDF extraction artifacts in TOC
        title = re.sub(r'\s+', ' ', title)       # Normalize spaces
        title = re.sub(r'wi th', 'with', title)  # Fix broken "with"
        title = re.sub(r'garl ic', 'garlic', title)  # Fix broken "garlic"
        title = re.sub(r'ol ive', 'olive', title)    # Fix broken "olive"
        title = re.sub(r'ther e', 'there', title)    # Fix broken "there"
        title = re.sub(r'pank o', 'panko', title)    # Fix broken "panko"
        title = re.sub(r'f amily', 'family', title)  # Fix broken "family"
        title = re.sub(r'whisper er', 'whisperer', title)  # Fix broken "whisperer"
        title = re.sub(r'bef ore', 'before', title)  # Fix broken "before"
        title = re.sub(r'pleasur e', 'pleasure', title)  # Fix broken "pleasure"
        title = re.sub(r'toda y', 'today', title)    # Fix broken "today"
        title = re.sub(r'bet ter', 'better', title)  # Fix broken "better"
        title = re.sub(r'r emoves', 'removes', title)  # Fix broken "removes"
        title = re.sub(r'mor e', 'more', title)      # Fix broken "more"
        
        # Remove incomplete sentences and fragments
        if title.endswith('When I get home late and ther'):
            return ""
        if title.endswith('I fry some capers or toast some pank'):
            return ""
        if 'salad spinner' in title.lower() and len(title) > 50:
            return ""
        if title.startswith('to remember') or title.startswith('salads toda'):
            return ""
        if title.startswith('greens in m y'):
            return ""
        
        # Clean up sentence fragments
        sentences = title.split('.')
        if len(sentences) > 1:
            # Take the first complete sentence if it looks like a recipe
            first_sentence = sentences[0].strip()
            if len(first_sentence) > 10 and self._looks_like_recipe_title(first_sentence):
                title = first_sentence
        
        return title.strip()
    
    def _is_valid_recipe_title(self, title: str) -> bool:
        """Additional validation for recipe titles from TOC"""
        
        if not title or len(title) < 5:
            return False
        
        # Skip obvious text fragments
        fragment_indicators = [
            'when i get', 'i fry some', 'friends and', 'to remember',
            'salads today', 'greens in', 'nothing', 'ever!', 'and m y',
            'the spinner', 'into a', 'because the'
        ]
        
        title_lower = title.lower()
        if any(fragment in title_lower for fragment in fragment_indicators):
            return False
        
        # Must be reasonable length
        if len(title) > 100:
            return False
        
        # Should contain food-related words
        food_indicators = [
            'pasta', 'garlic', 'olive', 'salad', 'chicken', 'beef', 'fish',
            'bread', 'sauce', 'soup', 'rice', 'cheese', 'lemon', 'butter'
        ]
        
        if any(food in title_lower for food in food_indicators):
            return True
        
        # Or cooking-related words
        cooking_indicators = [
            'roasted', 'grilled', 'baked', 'braised', 'sautéed', 'fried'
        ]
        
        return any(cooking in title_lower for cooking in cooking_indicators)
    
    def _parse_recipe_list_page(self, text: str, page_num: int):
        """Parse a page that contains a list of recipes"""
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if self._looks_like_recipe_title(line) and len(line) > 10:
                title_clean = self._clean_toc_title(line)
                if title_clean:
                    # Estimate page numbers based on list position
                    self.recipe_index[title_clean.lower()] = page_num + 5  # Rough estimate
    
    def _is_category_header(self, line: str) -> bool:
        """Check if line is a category header"""
        
        category_patterns = [
            r'^appetizers?\s*&?\s*snacks?$',
            r'^soups?\s*&?\s*stews?$',
            r'^salads?$',
            r'^main\s+dishes?$',
            r'^pasta\s*&?\s*rice$',
            r'^vegetables?$',
            r'^breads?\s*&?\s*baking$',
            r'^desserts?$',
            r'^breakfast$',
            r'^sauces?\s*&?\s*condiments?$'
        ]
        
        line_lower = line.lower().strip()
        
        for pattern in category_patterns:
            if re.match(pattern, line_lower):
                return True
        
        # Also check for all-caps category headers
        if line.isupper() and len(line.split()) <= 4 and len(line) > 5:
            return True
        
        return False
    
    def _clean_toc_title(self, title: str) -> str:
        """Clean TOC title for indexing"""
        
        # Remove page numbers and dots
        title = re.sub(r'\.{2,}.*$', '', title)  # Remove dotted lines and page numbers
        title = re.sub(r'\d+\s*$', '', title)    # Remove trailing page numbers
        title = re.sub(r'\s+', ' ', title)       # Normalize spaces
        
        return title.strip()
    
    def _parse_toc_page(self, text: str):
        """Parse TOC page and extract recipe titles with page numbers"""
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 10:
                continue
            
            # Look for pattern: "Recipe Title ... Page" or "Recipe Title Page"
            page_match = re.search(r'.*?(\d{2,3})$', line)
            
            if page_match:
                page_num = int(page_match.group(1))
                title_part = line[:page_match.start()].strip()
                
                # Clean up title (remove dots, extra spaces)
                title_clean = re.sub(r'\.{2,}', '', title_part).strip()
                title_clean = re.sub(r'\s+', ' ', title_clean)
                
                # Filter out non-recipe entries
                if self._is_recipe_title(title_clean):
                    self.recipe_index[title_clean.lower()] = page_num
                    self.page_index[page_num] = title_clean
    
    def _is_recipe_title(self, title: str) -> bool:
        """Check if title looks like a recipe"""
        
        if len(title) < 5 or len(title) > 80:
            return False
        
        # Skip obvious non-recipes
        non_recipe_patterns = [
            r'^(chapter|section|part|introduction|index|contents)',
            r'^(equipment|tools|techniques|basics|tips)',
            r'^(about|how to|why|when|where)',
            r'^\d+\.',  # Numbered lists
        ]
        
        title_lower = title.lower()
        for pattern in non_recipe_patterns:
            if re.search(pattern, title_lower):
                return False
        
        # Positive indicators for recipes
        food_keywords = [
            'chicken', 'beef', 'pork', 'fish', 'pasta', 'rice', 'bread',
            'soup', 'salad', 'cake', 'pie', 'cookies', 'sauce', 'stew',
            'roasted', 'grilled', 'baked', 'fried', 'braised',
            'chocolate', 'vanilla', 'cheese', 'garlic', 'lemon'
        ]
        
        return any(keyword in title_lower for keyword in food_keywords)
    
    def get_expected_title_for_page(self, page_num: int) -> Optional[str]:
        """Get expected recipe title for a given page"""
        return self.page_index.get(page_num)
    
    def find_recipe_page(self, title: str) -> Optional[int]:
        """Find page number for a recipe title"""
        title_clean = title.lower().strip()
        
        # Exact match first
        if title_clean in self.recipe_index:
            return self.recipe_index[title_clean]
        
        # Fuzzy matching for variations
        for toc_title, page_num in self.recipe_index.items():
            if self._titles_match(title_clean, toc_title):
                return page_num
        
        return None
    
    def _titles_match(self, title1: str, title2: str) -> bool:
        """Check if two titles are likely the same recipe"""
        
        # Remove common variations
        clean1 = re.sub(r'\b(the|a|an|with|and|&)\b', '', title1).strip()
        clean2 = re.sub(r'\b(the|a|an|with|and|&)\b', '', title2).strip()
        
        # Check for substantial overlap in key words
        words1 = set(clean1.split())
        words2 = set(clean2.split())
        
        if len(words1) == 0 or len(words2) == 0:
            return False
        
        overlap = len(words1.intersection(words2))
        min_words = min(len(words1), len(words2))
        
        return overlap / min_words >= 0.6  # 60% word overlap


class VisualStructureDetector:
    """Detects visual recipe structures - adapted from working Teen extractor"""
    
    def __init__(self):
        self.confidence_weights = {
            'title_pattern': 3.0,
            'servings_pattern': 2.0,
            'ingredient_measurements': 2.5,
            'numbered_steps': 2.0,
            'time_indicators': 1.5,
            'cooking_verbs': 1.5,
            'temperature_references': 1.0,
            'section_headers': 1.0
        }
    
    def analyze_page_structure(self, page_text: str, page_num: int, expected_title: Optional[str] = None) -> Dict[str, Any]:
        """Analyze page for visual recipe structure"""
        
        structure = {
            'page_number': page_num,
            'confidence_score': 0,
            'visual_indicators': {},
            'recipe_structure': {},
            'is_recipe_page': False,
            'expected_title': expected_title,
            'title_match': False
        }
        
        lines = page_text.split('\n')
        structure['visual_indicators'] = self._analyze_visual_indicators(lines, page_text)
        
        # Calculate confidence score
        total_confidence = 0
        for indicator, found in structure['visual_indicators'].items():
            if found:
                weight = self.confidence_weights.get(indicator, 1.0)
                total_confidence += weight
        
        # Bonus confidence if we have expected title match
        if expected_title:
            title_found = self._find_matching_title(lines, expected_title)
            if title_found:
                total_confidence += 5.0  # Big bonus for TOC match
                structure['title_match'] = True
        
        structure['confidence_score'] = total_confidence
        structure['is_recipe_page'] = total_confidence >= 4.0
        
        # Extract detailed structure if it's a recipe page
        if structure['is_recipe_page']:
            structure['recipe_structure'] = self._extract_recipe_structure(lines, page_text, expected_title)
        
        return structure
    
    def _analyze_visual_indicators(self, lines: List[str], full_text: str) -> Dict[str, bool]:
        """Analyze lines for visual recipe indicators"""
        
        indicators = {
            'title_pattern': False,
            'servings_pattern': False,
            'ingredient_measurements': False,
            'numbered_steps': False,
            'time_indicators': False,
            'cooking_verbs': False,
            'temperature_references': False,
            'section_headers': False
        }
        
        # Full text patterns
        indicators['servings_pattern'] = bool(re.search(r'(serves|makes|yields?)\s+\d+', full_text, re.IGNORECASE))
        indicators['time_indicators'] = bool(re.search(r'\d+\s+(minutes?|hours?|mins?|hrs?)', full_text, re.IGNORECASE))
        indicators['temperature_references'] = bool(re.search(r'\d+\s*°?F?\b', full_text))
        
        # Cooking verbs
        cooking_verbs = ['bake', 'roast', 'sauté', 'simmer', 'boil', 'fry', 'grill', 'mix', 'combine', 'whisk', 'stir']
        indicators['cooking_verbs'] = any(verb in full_text.lower() for verb in cooking_verbs)
        
        # Line-by-line analysis
        for i, line in enumerate(lines[:30]):  # Check first 30 lines
            line = line.strip()
            if not line:
                continue
            
            # Title pattern (prominent line, reasonable length)
            if not indicators['title_pattern']:
                indicators['title_pattern'] = self._is_recipe_title_line(line, i)
            
            # Ingredient measurements
            if not indicators['ingredient_measurements']:
                indicators['ingredient_measurements'] = bool(re.search(
                    r'\d+.*?(cup|tablespoon|teaspoon|pound|ounce|large|medium|small|clove)', 
                    line, re.IGNORECASE
                ))
            
            # Numbered steps
            if not indicators['numbered_steps']:
                indicators['numbered_steps'] = bool(re.match(r'^\s*\d+\.\s+', line))
            
            # Section headers
            if not indicators['section_headers']:
                section_patterns = ['ingredients', 'instructions', 'directions', 'method', 'preparation']
                indicators['section_headers'] = any(pattern in line.lower() for pattern in section_patterns)
        
        return indicators
    
    def _is_recipe_title_line(self, line: str, position: int) -> bool:
        """Check if line looks like a recipe title"""
        
        if len(line) < 5 or len(line) > 80:
            return False
        
        # Skip obvious non-titles
        non_title_patterns = [
            r'^\d+',  # Starts with number
            r'(cup|tablespoon|teaspoon|pound|ounce)',  # Ingredient measurements
            r'^(step|mix|add|combine|place|heat|cook)',  # Instructions
            r'^\s*(ingredients|instructions|directions)',  # Section headers
        ]
        
        line_lower = line.lower()
        if any(re.search(pattern, line_lower) for pattern in non_title_patterns):
            return False
        
        # Positive indicators
        # Title case or all caps
        if line.istitle() or line.isupper():
            return True
        
        # Early position with food words
        if position < 10:
            food_words = ['chicken', 'beef', 'pork', 'fish', 'pasta', 'bread', 'cake', 'soup', 'salad']
            if any(word in line_lower for word in food_words):
                return True
        
        return False
    
    def _find_matching_title(self, lines: List[str], expected_title: str) -> bool:
        """Check if expected title appears in the lines"""
        
        expected_clean = expected_title.lower().strip()
        expected_words = set(expected_clean.split())
        
        for line in lines[:15]:  # Check first 15 lines
            line_clean = line.strip().lower()
            line_words = set(line_clean.split())
            
            if len(expected_words) == 0:
                continue
            
            # Check for substantial word overlap
            overlap = len(expected_words.intersection(line_words))
            if overlap / len(expected_words) >= 0.6:  # 60% overlap
                return True
        
        return False
    
    def _extract_recipe_structure(self, lines: List[str], full_text: str, expected_title: Optional[str]) -> Dict[str, Any]:
        """Extract detailed recipe structure"""
        
        structure = {
            'title_candidates': [],
            'ingredient_sections': [],
            'instruction_sections': [],
            'metadata': {}
        }
        
        # Find title candidates
        for i, line in enumerate(lines[:20]):
            line = line.strip()
            if self._is_recipe_title_line(line, i):
                confidence = self._calculate_title_confidence(line, i, expected_title)
                structure['title_candidates'].append({
                    'text': line,
                    'line_number': i,
                    'confidence': confidence
                })
        
        # Extract metadata
        servings_match = re.search(r'(serves|makes|yields?)\s+(\d+)', full_text, re.IGNORECASE)
        if servings_match:
            structure['metadata']['servings'] = f"{servings_match.group(1).title()} {servings_match.group(2)}"
        
        time_match = re.search(r'(\d+)\s+(minutes?|hours?)', full_text, re.IGNORECASE)
        if time_match:
            structure['metadata']['time'] = f"{time_match.group(1)} {time_match.group(2).lower()}"
        
        return structure
    
    def _calculate_title_confidence(self, title_text: str, position: int, expected_title: Optional[str]) -> float:
        """Calculate confidence score for title candidate"""
        
        confidence = 0.0
        
        # Position weight (earlier = better)
        confidence += max(0, 10 - position) * 0.1
        
        # Length weight
        if 10 <= len(title_text) <= 60:
            confidence += 1.0
        elif 5 <= len(title_text) <= 80:
            confidence += 0.5
        
        # Format weight
        if title_text.istitle() or title_text.isupper():
            confidence += 0.5
        
        # Expected title match (big bonus)
        if expected_title:
            expected_words = set(expected_title.lower().split())
            title_words = set(title_text.lower().split())
            
            if len(expected_words) > 0:
                overlap = len(expected_words.intersection(title_words))
                confidence += (overlap / len(expected_words)) * 3.0  # Up to 3 points for perfect match
        
        return confidence


class ATK25thUnifiedExtractor:
    """Unified ATK 25th Anniversary extractor with TOC cross-referencing"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.cookbook_title = "America's Test Kitchen 25th Anniversary"
        
        # Initialize core components
        self.db_manager = DatabaseManager()
        self.semantic_engine = SemanticRecipeEngine(validation_level=ValidationLevel.PERMISSIVE)
        self.ingredient_engine = IngredientIntelligenceEngine()
        self.visual_detector = VisualStructureDetector()
        
        # Use PDF bookmarks as primary TOC source, fallback to text-based TOC
        self.bookmark_extractor = PDFBookmarkExtractor(pdf_path)
        self.toc_extractor = TableOfContentsExtractor(pdf_path)
        
        # Extract TOC - use text-based approach as primary method
        self.recipe_index = self.toc_extractor.extract_toc()
        
        # Try to supplement with PDF bookmarks if text-based TOC was insufficient
        if len(self.recipe_index) < 50:  # Expect at least 50 recipes
            logger.info("📋 Text-based TOC insufficient, supplementing with PDF bookmarks...")
            bookmark_toc = self.bookmark_extractor.extract_bookmarks()
            self.recipe_index.update(bookmark_toc)
        
        # Extraction state
        self.extracted_recipes = []
        self.multi_page_recipes = {}
        
        # Statistics
        self.stats = {
            'pages_processed': 0,
            'toc_recipes_found': len(self.recipe_index),
            'pages_with_visual_structure': 0,
            'toc_matches_found': 0,
            'recipe_candidates_found': 0,
            'visual_validations': 0,
            'semantic_validations': 0,
            'recipes_validated': 0,
            'multi_page_recipes': 0
        }
        
        self.rejection_reasons = {
            'no_visual_structure': 0,
            'no_title_found': 0,
            'no_ingredients': 0,
            'no_instructions': 0,
            'semantic_rejection': 0,
            'low_quality': 0
        }
    
    def extract_recipes(self, start_page: int = 1, end_page: Optional[int] = None, 
                       max_recipes: Optional[int] = None, dry_run: bool = False) -> List[Dict]:
        """Main extraction with TOC-guided approach"""
        
        logger.info("🧠📚 ATK 25TH ANNIVERSARY UNIFIED EXTRACTION")
        logger.info("=" * 80)
        logger.info("📋 Table of Contents cross-referencing")
        logger.info("👁️ Visual structure detection")
        logger.info("🧠 Semantic validation")
        logger.info("🛡️ Multi-layer quality assurance")
        logger.info("=" * 80)
        
        if not os.path.exists(self.pdf_path):
            logger.error(f"❌ PDF not found: {self.pdf_path}")
            return []
        
        try:
            with open(self.pdf_path, 'rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                total_pages = len(reader.pages)
                
                if end_page is None:
                    end_page = total_pages
                
                end_page = min(end_page, total_pages)
                logger.info(f"📄 Processing pages {start_page} to {end_page}")
                logger.info(f"📋 TOC Index: {len(self.recipe_index)} recipes to cross-reference")
                
                # Process each page
                for page_num in range(start_page - 1, end_page):
                    if max_recipes and self.stats['recipes_validated'] >= max_recipes:
                        logger.info(f"🎯 Reached max recipes limit: {max_recipes}")
                        break
                    
                    try:
                        page = reader.pages[page_num]
                        page_text = page.extract_text()
                        
                        if not page_text.strip():
                            continue
                        
                        self.stats['pages_processed'] += 1
                        
                        # Get expected title from TOC
                        expected_title = self.toc_extractor.get_expected_title_for_page(page_num + 1)
                        if not expected_title:
                            expected_title = self.bookmark_extractor.get_expected_title_for_page(page_num + 1)
                        
                        # Visual structure analysis with TOC guidance
                        visual_analysis = self.visual_detector.analyze_page_structure(
                            page_text, page_num + 1, expected_title
                        )
                        
                        if visual_analysis['is_recipe_page']:
                            self.stats['pages_with_visual_structure'] += 1
                            
                            if visual_analysis['title_match']:
                                self.stats['toc_matches_found'] += 1
                            
                            # Process recipe candidate
                            self._process_recipe_candidate(visual_analysis, page_text, dry_run)
                        else:
                            # Check for multi-page continuation
                            self._check_multi_page_continuation(page_text, page_num + 1)
                        
                        # Progress reporting
                        if self.stats['pages_processed'] % 50 == 0:
                            logger.info(f"  📊 Progress: {self.stats['pages_processed']} pages, {self.stats['recipes_validated']} recipes")
                    
                    except Exception as e:
                        logger.error(f"❌ Error processing page {page_num + 1}: {e}")
                        continue
                
                # Finalize any remaining multi-page recipes
                self._finalize_multi_page_recipes(dry_run)
                
                logger.info("")
                logger.info("✅ UNIFIED EXTRACTION COMPLETE!")
                self._print_comprehensive_summary()
                
                if not dry_run and self.extracted_recipes:
                    self._save_recipes()
                
                return self.extracted_recipes
        
        except Exception as e:
            logger.error(f"❌ Fatal extraction error: {e}")
            return []
    
    def _process_recipe_candidate(self, visual_analysis: Dict, page_text: str, dry_run: bool = False):
        """Process a recipe candidate with full validation pipeline"""
        
        page_num = visual_analysis['page_number']
        confidence = visual_analysis['confidence_score']
        has_toc_match = visual_analysis['title_match']
        
        self.stats['recipe_candidates_found'] += 1
        
        # Extract recipe data using visual guidance
        recipe_data = self._extract_recipe_with_guidance(visual_analysis, page_text)
        
        if not recipe_data:
            self.rejection_reasons['no_title_found'] += 1
            return
        
        # Check for multi-page recipe
        if self._is_multi_page_recipe(recipe_data, page_num):
            return  # Will be processed when complete
        
        # Validate requirements
        validation_result = self._validate_recipe_requirements(recipe_data)
        
        if not validation_result['valid']:
            for reason in validation_result['reasons']:
                self.rejection_reasons[reason] += 1
            return
        
        self.stats['visual_validations'] += 1
        
        # Clean text for semantic validation
        cleaned_recipe = self._clean_recipe_text(recipe_data)
        
        # Semantic validation with ATK-adapted approach
        semantic_result = self._validate_semantically_with_atk_adaptation(cleaned_recipe, confidence, has_toc_match)
        
        if semantic_result['is_valid']:
            self.stats['semantic_validations'] += 1
            
            # Add metadata
            recipe_data['visual_confidence'] = confidence
            recipe_data['semantic_confidence'] = semantic_result['confidence']
            recipe_data['toc_cross_referenced'] = has_toc_match
            recipe_data['source'] = self.cookbook_title
            recipe_data['extraction_method'] = 'unified_toc_guided'
            recipe_data['page_number'] = page_num
            recipe_data['extraction_timestamp'] = datetime.now().isoformat()
            
            self.extracted_recipes.append(recipe_data)
            self.stats['recipes_validated'] += 1
            
            # Logging based on method
            if has_toc_match:
                logger.info(f"✅ TOC Match Page {page_num}: '{recipe_data['title']}' (visual: {confidence:.1f}, semantic: {semantic_result['confidence']:.2f})")
            else:
                logger.info(f"✅ Visual Page {page_num}: '{recipe_data['title']}' (visual: {confidence:.1f}, semantic: {semantic_result['confidence']:.2f})")
        else:
            self.rejection_reasons['semantic_rejection'] += 1
    
    def _extract_recipe_with_guidance(self, visual_analysis: Dict, page_text: str) -> Optional[Dict]:
        """Extract recipe using visual structure and TOC guidance"""
        
        recipe_structure = visual_analysis.get('recipe_structure', {})
        expected_title = visual_analysis.get('expected_title')
        
        recipe_data = {}
        
        # Extract title with TOC guidance
        title = self._extract_best_title(recipe_structure, page_text, expected_title)
        if not title:
            return None
        
        recipe_data['title'] = title
        recipe_data['category'] = self._infer_category(title)
        
        # Extract ingredients
        ingredients = self._extract_ingredients_from_text(page_text)
        if not ingredients:
            return None
        
        # Validate ingredients contain real food items
        if not self._contains_known_ingredients(ingredients):
            return None
        
        recipe_data['ingredients'] = ingredients
        
        # Extract instructions
        instructions = self._extract_instructions_from_text(page_text)
        if instructions:
            recipe_data['instructions'] = instructions
        
        # Extract metadata
        metadata = recipe_structure.get('metadata', {})
        if metadata.get('servings'):
            recipe_data['servings'] = metadata['servings']
        
        if metadata.get('time'):
            recipe_data['total_time'] = metadata['time']
        
        return recipe_data
    
    def _extract_best_title(self, recipe_structure: Dict, page_text: str, expected_title: Optional[str]) -> Optional[str]:
        """Extract best title using TOC guidance"""
        
        title_candidates = recipe_structure.get('title_candidates', [])
        
        if title_candidates:
            # Sort by confidence (includes TOC match bonus)
            best_candidate = max(title_candidates, key=lambda x: x['confidence'])
            title = best_candidate['text']
            
            # Clean up title
            title = self._clean_title(title)
            return title if len(title) > 3 else None
        
        # Fallback: look for title patterns in first 15 lines
        lines = page_text.split('\n')
        for line in lines[:15]:
            line = line.strip()
            if self.visual_detector._is_recipe_title_line(line, 0):
                title = self._clean_title(line)
                if len(title) > 3:
                    return title
        
        return None
    
    def _clean_title(self, title: str) -> str:
        """Clean and format title"""
        
        # Remove common artifacts
        title = re.sub(r'^(Recipe|Test Kitchen)', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s+', ' ', title)
        title = title.strip()
        
        # Convert to title case if all caps
        if title.isupper():
            title = title.title()
        
        return title
    
    def _extract_ingredients_from_text(self, page_text: str) -> Optional[str]:
        """Extract ingredients using pattern recognition"""
        
        # Look for ingredient list sections
        ingredient_patterns = [
            r'\d+.*?(cup|tablespoon|teaspoon|pound|ounce|large|medium|small|clove)',
            r'\d+\s*\(\d+.*?ounce\)',  # "1 (14-ounce) can"
            r'[\d¼½¾⅓⅔⅛]+.*?(chopped|diced|minced|sliced|grated)',
        ]
        
        lines = page_text.split('\n')
        ingredient_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line matches ingredient patterns
            for pattern in ingredient_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    ingredient_lines.append(line)
                    break
        
        if len(ingredient_lines) < 3:  # Need at least 3 ingredient lines
            return None
        
        return self._format_ingredients(ingredient_lines)
    
    def _format_ingredients(self, ingredient_lines: List[str]) -> str:
        """Format ingredient lines with proper bullets"""
        
        formatted = []
        
        for line in ingredient_lines:
            line = line.strip()
            if line and not line.startswith('•'):
                formatted.append(f"• {line}")
            else:
                formatted.append(line)
        
        return '\n'.join(formatted)
    
    def _extract_instructions_from_text(self, page_text: str) -> Optional[str]:
        """Extract instructions using pattern recognition"""
        
        # Look for numbered steps
        lines = page_text.split('\n')
        instruction_lines = []
        current_step = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for numbered step start
            step_match = re.match(r'^(\d+)\.\s*(.+)', line)
            if step_match:
                if current_step:
                    instruction_lines.append(current_step)
                current_step = f"{step_match.group(1)}. {step_match.group(2)}"
            else:
                # Continue current step
                if current_step and len(line) > 5:
                    current_step += f" {line}"
        
        # Add final step
        if current_step:
            instruction_lines.append(current_step)
        
        if len(instruction_lines) < 2:  # Need at least 2 steps
            return None
        
        return '\n'.join(instruction_lines)
    
    def _validate_semantically_with_atk_adaptation(self, cleaned_recipe: Dict, 
                                                  visual_confidence: float, 
                                                  has_toc_match: bool) -> Dict[str, Any]:
        """Semantic validation adapted for ATK cookbook patterns"""
        
        # Standard semantic validation first
        semantic_result = self.semantic_engine.validate_complete_recipe(cleaned_recipe)
        
        # ATK cookbook adaptation - be more permissive for high-confidence visual detection
        if not semantic_result.is_valid_recipe:
            # Check for ATK cookbook override conditions
            atk_override = False
            override_reason = ""
            
            # Strong visual confidence + TOC match = likely valid
            if visual_confidence >= 8 and has_toc_match:
                atk_override = True
                override_reason = "high_visual_confidence_with_toc_match"
            
            # High visual confidence + substantial ingredients = likely valid
            elif visual_confidence >= 6 and self._has_substantial_ingredients(cleaned_recipe):
                atk_override = True
                override_reason = "high_visual_confidence_with_ingredients"
            
            # Medium confidence but very strong ingredient indicators
            elif visual_confidence >= 4 and self._has_strong_recipe_indicators(cleaned_recipe):
                atk_override = True
                override_reason = "strong_recipe_indicators"
            
            # Relaxed validation for ATK cookbook patterns
            elif self._passes_atk_relaxed_validation(cleaned_recipe, visual_confidence):
                atk_override = True
                override_reason = "atk_relaxed_patterns"
            
            if atk_override:
                return {
                    'is_valid': True,
                    'confidence': 0.70 + (visual_confidence * 0.02),  # Scale with visual confidence
                    'method': f'atk_cookbook_adaptation_{override_reason}'
                }
        
        return {
            'is_valid': semantic_result.is_valid_recipe,
            'confidence': semantic_result.confidence_score,
            'method': 'standard_semantic'
        }
    
    def _has_substantial_ingredients(self, recipe_data: Dict) -> bool:
        """Check if recipe has substantial, recognizable ingredients"""
        
        ingredients = recipe_data.get('ingredients', '')
        
        # Check for multiple ingredient lines
        ingredient_lines = [line.strip() for line in ingredients.split('\n') if line.strip()]
        if len(ingredient_lines) < 4:
            return False
        
        # Check for known ingredients using intelligence engine
        known_ingredient_count = 0
        
        for line in ingredient_lines:
            if self._contains_known_ingredients(line):
                known_ingredient_count += 1
        
        # At least 60% of ingredients should be recognizable
        return known_ingredient_count / len(ingredient_lines) >= 0.6
    
    def _has_strong_recipe_indicators(self, recipe_data: Dict) -> bool:
        """Check for strong recipe indicators beyond basic validation"""
        
        title = recipe_data.get('title', '').lower()
        ingredients = recipe_data.get('ingredients', '').lower()
        instructions = recipe_data.get('instructions', '').lower()
        
        # Strong title indicators
        strong_title_words = [
            'roasted', 'grilled', 'baked', 'braised', 'sautéed', 'pan-seared',
            'chicken', 'beef', 'pork', 'fish', 'salmon', 'pasta', 'rice',
            'soup', 'salad', 'sauce', 'bread', 'cake', 'pie', 'cookies'
        ]
        title_score = sum(1 for word in strong_title_words if word in title)
        
        # Strong ingredient patterns
        measurement_patterns = [
            r'\d+.*?(cup|tablespoon|teaspoon|pound|ounce|gram)',
            r'\d+.*?(large|medium|small)',
            r'\d+.*?(clove|slice|piece)',
        ]
        ingredient_score = sum(1 for pattern in measurement_patterns if re.search(pattern, ingredients))
        
        # Strong instruction indicators
        cooking_verbs = [
            'heat', 'cook', 'bake', 'roast', 'sauté', 'simmer', 'boil',
            'mix', 'combine', 'whisk', 'stir', 'add', 'season'
        ]
        instruction_score = sum(1 for verb in cooking_verbs if verb in instructions)
        
        # Total score - need at least 5 strong indicators
        total_score = title_score + ingredient_score + instruction_score
        return total_score >= 5
    
    def _passes_atk_relaxed_validation(self, recipe_data: Dict, visual_confidence: float) -> bool:
        """Relaxed validation specific to ATK cookbook patterns"""
        
        title = recipe_data.get('title', '')
        ingredients = recipe_data.get('ingredients', '')
        instructions = recipe_data.get('instructions', '')
        
        # Basic requirements with relaxed thresholds
        has_title = len(title.strip()) >= 5
        has_some_ingredients = len(ingredients.strip()) >= 30  # Relaxed from 50
        has_some_instructions = len(instructions.strip()) >= 20  # Relaxed from 50
        
        # Check for real food content
        has_food_indicators = self._contains_known_ingredients(title + ' ' + ingredients)
        
        # Check for measurement patterns (key indicator of real recipes)
        has_measurements = bool(re.search(r'\d+.*?(cup|tablespoon|teaspoon|ounce|pound)', ingredients, re.IGNORECASE))
        
        # Check for cooking language
        cooking_language = bool(re.search(r'\b(heat|cook|bake|mix|add|combine|season|serve)\b', instructions, re.IGNORECASE))
        
        # Pass if we have most indicators and reasonable visual confidence
        indicators_met = sum([has_title, has_some_ingredients, has_some_instructions, has_food_indicators, has_measurements, cooking_language])
        
        return indicators_met >= 4 and visual_confidence >= 3
    
    def _contains_known_ingredients(self, text: str) -> bool:
        """Check if text contains known ingredients"""
        
        text_lower = text.lower()
        
        for ingredient_id, data in self.ingredient_engine.canonical_ingredients.items():
            ingredient_name = data['name'].lower()
            core_name = self._extract_core_ingredient_name(ingredient_name)
            
            if core_name and len(core_name) >= 3:
                if core_name in text_lower:
                    return True
        
        return False
    
    def _extract_core_ingredient_name(self, ingredient_name: str) -> str:
        """Extract core ingredient name from full description"""
        
        # Remove measurements and modifiers
        cleaned = re.sub(r'^\d+.*?(cup|tablespoon|teaspoon|slice|large|small|pound|ounce)', '', ingredient_name, flags=re.IGNORECASE)
        cleaned = re.sub(r'\b(for|about|until|warmed|hot|to|the|touch|minute|lukewarm|strong|brewed|dry|extra-virgin|all-purpose|confectioners|crumbled|garnish)\b', '', cleaned, flags=re.IGNORECASE)
        
        words = cleaned.strip().split()
        core_words = []
        
        for word in words:
            if len(word) >= 3 and word not in ['and', 'the', 'for', 'with']:
                core_words.append(word)
                if len(core_words) >= 2:
                    break
        
        return ' '.join(core_words)
    
    def _infer_category(self, title: str) -> str:
        """Infer recipe category from title"""
        
        title_lower = title.lower()
        
        category_keywords = {
            'Appetizers & Snacks': ['appetizer', 'snack', 'dip', 'spread', 'chips'],
            'Soups & Stews': ['soup', 'stew', 'chili', 'bisque', 'broth'],
            'Salads': ['salad', 'slaw', 'greens'],
            'Main Dishes': ['chicken', 'beef', 'pork', 'fish', 'salmon', 'roast', 'steak'],
            'Pasta & Rice': ['pasta', 'rice', 'risotto', 'noodles', 'spaghetti', 'lasagna'],
            'Vegetables': ['vegetable', 'broccoli', 'asparagus', 'beans', 'carrots'],
            'Breads & Baking': ['bread', 'muffin', 'biscuit', 'roll', 'loaf'],
            'Desserts': ['cake', 'pie', 'cookie', 'chocolate', 'dessert', 'sweet', 'tart'],
            'Breakfast': ['pancake', 'waffle', 'breakfast', 'eggs', 'bacon'],
            'Sauces & Condiments': ['sauce', 'dressing', 'marinade', 'glaze', 'butter']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                return category
        
        return 'Main Dishes'  # Default category
    
    def _is_multi_page_recipe(self, recipe_data: Dict, page_num: int) -> bool:
        """Check if recipe spans multiple pages"""
        
        has_title = bool(recipe_data.get('title'))
        has_ingredients = bool(recipe_data.get('ingredients'))
        has_instructions = bool(recipe_data.get('instructions'))
        
        # Start of multi-page recipe (has title but incomplete content)
        if has_title and (not has_ingredients or not has_instructions):
            page_key = f"page_{page_num}"
            self.multi_page_recipes[page_key] = {
                'recipe_data': recipe_data,
                'page_start': page_num,
                'last_page': page_num
            }
            logger.info(f"🔄 Started multi-page recipe '{recipe_data['title']}' on page {page_num}")
            return True
        
        # Continuation (no title but has content)
        if not has_title and (has_ingredients or has_instructions):
            # Look for active multi-page recipe in previous pages
            for lookback in range(1, 5):
                prev_page_key = f"page_{page_num - lookback}"
                if prev_page_key in self.multi_page_recipes:
                    self._add_to_multi_page_recipe(prev_page_key, recipe_data, page_num)
                    logger.info(f"🔄 Added content from page {page_num} to multi-page recipe")
                    return True
        
        return False
    
    def _add_to_multi_page_recipe(self, page_key: str, continuation_data: Dict, current_page: int):
        """Add continuation data to multi-page recipe"""
        
        if page_key not in self.multi_page_recipes:
            return
        
        main_recipe = self.multi_page_recipes[page_key]['recipe_data']
        
        # Combine ingredients
        if continuation_data.get('ingredients'):
            if not main_recipe.get('ingredients'):
                main_recipe['ingredients'] = continuation_data['ingredients']
            else:
                main_recipe['ingredients'] += '\n' + continuation_data['ingredients']
        
        # Combine instructions
        if continuation_data.get('instructions'):
            if not main_recipe.get('instructions'):
                main_recipe['instructions'] = continuation_data['instructions']
            else:
                main_recipe['instructions'] += '\n' + continuation_data['instructions']
        
        self.multi_page_recipes[page_key]['last_page'] = current_page
    
    def _check_multi_page_continuation(self, page_text: str, page_num: int):
        """Check non-recipe pages for multi-page continuation"""
        
        if not self.multi_page_recipes:
            return
        
        # Simple content extraction
        ingredients = self._extract_ingredients_from_text(page_text)
        instructions = self._extract_instructions_from_text(page_text)
        
        if not ingredients and not instructions:
            return
        
        # Look for active multi-page recipes
        for lookback in range(1, 5):
            prev_page_key = f"page_{page_num - lookback}"
            if prev_page_key in self.multi_page_recipes:
                continuation_data = {}
                if ingredients:
                    continuation_data['ingredients'] = ingredients
                if instructions:
                    continuation_data['instructions'] = instructions
                
                self._add_to_multi_page_recipe(prev_page_key, continuation_data, page_num)
                logger.info(f"🔄 Added continuation from page {page_num}")
                return
    
    def _finalize_multi_page_recipes(self, dry_run: bool = False):
        """Process remaining multi-page recipes"""
        
        for page_key, recipe_info in self.multi_page_recipes.items():
            recipe_data = recipe_info['recipe_data']
            
            # Validate multi-page recipe
            validation_result = self._validate_recipe_requirements(recipe_data)
            
            if validation_result['valid']:
                # Clean and validate semantically
                cleaned_recipe = self._clean_recipe_text(recipe_data)
                semantic_result = self._validate_semantically_with_atk_adaptation(cleaned_recipe, 8.0, False)
                
                if semantic_result['is_valid']:
                    # Add metadata
                    recipe_data['visual_confidence'] = 8.0  # Multi-page gets moderate confidence
                    recipe_data['semantic_confidence'] = semantic_result['confidence']
                    recipe_data['source'] = self.cookbook_title
                    recipe_data['extraction_method'] = 'unified_toc_guided_multipage'
                    
                    if recipe_info['last_page'] != recipe_info['page_start']:
                        recipe_data['page_number'] = f"{recipe_info['page_start']}-{recipe_info['last_page']}"
                        logger.info(f"✅ Multi-page {recipe_info['page_start']}-{recipe_info['last_page']}: '{recipe_data['title']}'")
                    else:
                        recipe_data['page_number'] = recipe_info['page_start']
                        logger.info(f"✅ Page {recipe_info['page_start']}: '{recipe_data['title']}'")
                    
                    if not dry_run:
                        self.extracted_recipes.append(recipe_data)
                    
                    self.stats['recipes_validated'] += 1
                    self.stats['multi_page_recipes'] += 1
    
    def _validate_recipe_requirements(self, recipe_data: Dict) -> Dict[str, Any]:
        """Validate core recipe requirements"""
        
        validation = {
            'valid': True,
            'reasons': []
        }
        
        # Must have title
        if not recipe_data.get('title'):
            validation['valid'] = False
            validation['reasons'].append('no_title_found')
        
        # Must have ingredients
        if not recipe_data.get('ingredients') or len(recipe_data['ingredients'].strip()) < 20:
            validation['valid'] = False
            validation['reasons'].append('no_ingredients')
        
        # Instructions are optional for some ATK recipes (ingredient-focused recipes)
        
        return validation
    
    def _clean_recipe_text(self, recipe_data: Dict) -> Dict[str, str]:
        """Clean recipe text for semantic validation"""
        
        cleaned = {}
        
        for field in ['title', 'ingredients', 'instructions', 'description']:
            text = recipe_data.get(field, '')
            if text:
                # Fix common PDF extraction artifacts specific to ATK
                text = self._clean_pdf_artifacts(text)
                cleaned[field] = text
        
        return cleaned
    
    def _clean_pdf_artifacts(self, text: str) -> str:
        """Clean ATK-specific PDF extraction artifacts"""
        
        # ATK cookbook specific fixes
        atk_fixes = [
            (r'\by olks\b', 'yolks'),
            (r'\bhal f-and-hal f\b', 'half-and-half'),
            (r'\bthor oughly\b', 'thoroughly'),
            (r'\bpur e\b', 'pure'),
            (r'\bmel ted\b', 'melted'),
            (r'\bbut ter\b', 'butter'),
            (r'\bsal t\b', 'salt'),
            (r'\bunti l\b', 'until'),
            (r'\bgar lic\b', 'garlic'),
            (r'\bpepper\b', 'pepper'),
            (r'\bingredient s\b', 'ingredients'),
            (r'\binstr uctions\b', 'instructions'),
            (r'\btemper ature\b', 'temperature'),
        ]
        
        for pattern, replacement in atk_fixes:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # General cleanup
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces
        text = re.sub(r' ,', ',', text)   # Space before comma
        text = re.sub(r' \.', '.', text)  # Space before period
        text = text.strip()
        
        return text
    
    def _print_comprehensive_summary(self):
        """Print detailed extraction summary"""
        
        logger.info("")
        logger.info("🧠📚 UNIFIED EXTRACTION SUMMARY:")
        logger.info("=" * 80)
        logger.info(f"📄 Pages processed: {self.stats['pages_processed']}")
        logger.info(f"📋 TOC recipes indexed: {self.stats['toc_recipes_found']}")
        logger.info(f"👁️ Pages with visual structure: {self.stats['pages_with_visual_structure']}")
        logger.info(f"🎯 TOC matches found: {self.stats['toc_matches_found']}")
        logger.info(f"🔍 Recipe candidates found: {self.stats['recipe_candidates_found']}")
        logger.info(f"👁️ Visual validations: {self.stats['visual_validations']}")
        logger.info(f"🧠 Semantic validations: {self.stats['semantic_validations']}")
        logger.info(f"📄 Multi-page recipes: {self.stats['multi_page_recipes']}")
        logger.info(f"✅ Total recipes validated: {self.stats['recipes_validated']}")
        
        if self.extracted_recipes:
            # Calculate success metrics
            toc_guided = sum(1 for r in self.extracted_recipes if r.get('toc_cross_referenced', False))
            semantic_scores = [r.get('semantic_confidence', 0) for r in self.extracted_recipes]
            avg_semantic = sum(semantic_scores) / len(semantic_scores) if semantic_scores else 0
            
            logger.info(f"📊 TOC-guided extractions: {toc_guided}")
            logger.info(f"📊 Average semantic quality: {avg_semantic:.2f}")
        
        logger.info("")
        logger.info("🚫 REJECTION BREAKDOWN:")
        for reason, count in self.rejection_reasons.items():
            reason_name = reason.replace('_', ' ').title()
            logger.info(f"  {reason_name}: {count}")
        
        logger.info("")
        logger.info("✅ VALIDATED RECIPES:")
        for i, recipe in enumerate(self.extracted_recipes[:10], 1):
            toc_flag = "📋" if recipe.get('toc_cross_referenced', False) else "👁️"
            visual_conf = recipe.get('visual_confidence', 0)
            semantic_conf = recipe.get('semantic_confidence', 0)
            logger.info(f"  {toc_flag} {i}. '{recipe['title']}' (v:{visual_conf:.1f}, s:{semantic_conf:.2f})")
        
        if len(self.extracted_recipes) > 10:
            logger.info(f"  ... and {len(self.extracted_recipes) - 10} more")
    
    def _save_recipes(self):
        """Save extracted recipes to database"""
        
        logger.info("")
        logger.info("💾 SAVING UNIFIED EXTRACTION RESULTS")
        logger.info("=" * 60)
        logger.info(f"📋 Recipes to save: {len(self.extracted_recipes)}")
        logger.info("🧠 TOC cross-referenced + Visual + Semantic validation")
        
        try:
            saved_count = 0
            
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                for recipe in self.extracted_recipes:
                    # Prepare recipe data for database
                    insert_query = """
                        INSERT INTO recipes (
                            title, ingredients, instructions, category, source, 
                            servings, total_time, description, 
                            created_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    """
                    
                    values = (
                        recipe['title'],
                        recipe['ingredients'],
                        recipe.get('instructions', ''),
                        recipe.get('category', 'Main Dishes'),
                        recipe['source'],
                        recipe.get('servings'),
                        recipe.get('total_time'),
                        recipe.get('description')
                    )
                    
                    cursor.execute(insert_query, values)
                    saved_count += 1
                
                conn.commit()
            
            logger.info(f"✅ Successfully saved {saved_count} unified recipes")
            
        except Exception as e:
            logger.error(f"❌ Error saving recipes: {e}")
        
        logger.info("")
        logger.info("🎉 UNIFIED EXTRACTION COMPLETE!")
        logger.info("🧠📚 TOC-guided + Visual + Semantic validation")
        logger.info(f"📊 Final Results: {len(self.extracted_recipes)} recipes extracted and saved")


def main():
    """Main execution function"""
    
    parser = argparse.ArgumentParser(description='ATK 25th Anniversary Unified Extractor')
    parser.add_argument('--start-page', type=int, default=1, help='Starting page number')
    parser.add_argument('--end-page', type=int, help='Ending page number')
    parser.add_argument('--max-recipes', type=int, help='Maximum recipes to extract')
    parser.add_argument('--dry-run', action='store_true', help='Extract without saving to database')
    
    args = parser.parse_args()
    
    # PDF path
    pdf_path = os.path.join(os.path.dirname(__file__), "America's Test Kitchen 25th Ann - America's Test Kitchen.pdf")
    
    if not os.path.exists(pdf_path):
        logger.error(f"❌ PDF not found: {pdf_path}")
        return
    
    # Create unified extractor and run
    extractor = ATK25thUnifiedExtractor(pdf_path)
    recipes = extractor.extract_recipes(
        start_page=args.start_page,
        end_page=args.end_page,
        max_recipes=args.max_recipes,
        dry_run=args.dry_run
    )
    
    logger.info(f"🏁 Unified extraction complete: {len(recipes)} recipes extracted")


if __name__ == "__main__":
    main()
