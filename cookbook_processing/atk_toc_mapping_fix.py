#!/usr/bin/env python3
"""
🔧 ATK TOC MAPPING FIX
====================

Addresses the specific TOC search logic problem identified in PROJECT_MASTER_GUIDE:
- Issue: Forward search incorrectly mapping all recipes to TOC page 738
- Root Cause: Search starting too early finds recipe titles on TOC pages first
- Solution: Enhanced search logic with TOC page exclusion and fuzzy matching

This fixes the "Season 16" vs "Chicken in Mole-Poblano Sauce" mapping issue.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class EnhancedTOCMapper:
    """
    Enhanced TOC mapping with improved search logic and fuzzy matching
    
    Fixes the issues identified in the PROJECT_MASTER_GUIDE:
    1. Excludes TOC pages from forward search
    2. Uses fuzzy matching for better title recognition
    3. Implements confidence scoring for mapping quality
    4. Handles multi-page recipes and title variations
    """
    
    def __init__(self):
        self.recipe_index = {}
        self.page_index = {}
        self.mapping_confidence = {}
        
        # TOC page ranges to exclude from search
        self.toc_pages = {
            'start': 738,
            'end': 740
        }
    
    def extract_toc_with_enhanced_mapping(self, reader, total_pages: int) -> Dict[str, int]:
        """
        Enhanced TOC extraction with improved forward search mapping
        
        Fixes the core issue: search now excludes TOC pages and uses
        fuzzy matching for better recipe title recognition.
        """
        
        logger.info("🔍 Starting enhanced TOC extraction with improved mapping")
        
        # Step 1: Extract recipe titles from known TOC pages
        toc_recipes = self._extract_toc_recipes(reader)
        logger.info(f"📋 Found {len(toc_recipes)} potential recipes in TOC")
        
        # Step 2: Enhanced forward search with TOC exclusion
        successful_mappings = self._enhanced_forward_search(reader, toc_recipes, total_pages)
        
        # Step 3: Fuzzy matching for unmapped recipes
        unmapped_recipes = [r for r in toc_recipes if r.lower() not in self.recipe_index]
        if unmapped_recipes:
            logger.info(f"🔍 Attempting fuzzy matching for {len(unmapped_recipes)} unmapped recipes")
            fuzzy_mappings = self._fuzzy_search_unmapped(reader, unmapped_recipes, total_pages)
            successful_mappings.update(fuzzy_mappings)
        
        logger.info(f"✅ Successfully mapped {len(successful_mappings)}/{len(toc_recipes)} recipes")
        return successful_mappings
    
    def _extract_toc_recipes(self, reader) -> List[str]:
        """Extract recipe titles from TOC pages"""
        
        toc_recipes = []
        toc_page_indices = [737, 738, 739]  # Pages 738, 739, 740 (0-indexed)
        
        for page_idx in toc_page_indices:
            try:
                if page_idx < len(reader.pages):
                    page = reader.pages[page_idx]
                    page_text = page.extract_text()
                    recipes = self._parse_toc_page(page_text)
                    toc_recipes.extend(recipes)
                    logger.info(f"    📄 TOC Page {page_idx + 1}: Found {len(recipes)} recipes")
            except Exception as e:
                logger.warning(f"    ⚠️ Error reading TOC page {page_idx + 1}: {e}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recipes = []
        for recipe in toc_recipes:
            if recipe.lower() not in seen:
                seen.add(recipe.lower())
                unique_recipes.append(recipe)
        
        return unique_recipes
    
    def _parse_toc_page(self, page_text: str) -> List[str]:
        """Parse TOC page text to extract recipe titles"""
        
        recipes = []
        lines = page_text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Filter obvious non-recipes
            if len(line) < 5 or len(line) > 100:
                continue
            
            # Skip page numbers, headers, section titles
            if any(skip in line.lower() for skip in [
                'page', 'chapter', 'section', 'contents', 'acknowledgments', 'index',
                'appetizers', 'soups', 'main dishes', 'desserts', 'breakfast'
            ]):
                continue
            
            # Look for recipe indicators
            recipe_indicators = [
                'chicken', 'beef', 'pork', 'fish', 'salmon', 'pasta', 'rice', 'bread',
                'soup', 'salad', 'sauce', 'roasted', 'grilled', 'baked', 'braised',
                'with', 'and', 'in', 'au', 'de', 'la', 'le', 'egg', 'cheese',
                'cake', 'pie', 'cookie', 'chocolate', 'stew', 'curry'
            ]
            
            if any(indicator in line.lower() for indicator in recipe_indicators):
                # Clean up the title
                cleaned_title = self._clean_toc_title(line)
                if cleaned_title:
                    recipes.append(cleaned_title)
        
        return recipes
    
    def _clean_toc_title(self, title: str) -> str:
        """Clean up TOC title text"""
        
        # Remove page numbers and dots
        cleaned = re.sub(r'\.{3,}.*$', '', title)  # Remove dotted lines and page numbers
        cleaned = re.sub(r'\s+\d+$', '', cleaned)  # Remove trailing page numbers
        
        # Remove common TOC artifacts
        cleaned = re.sub(r'^[\d\.\-\s]*', '', cleaned)  # Remove leading numbers/dashes
        cleaned = cleaned.strip()
        
        return cleaned if len(cleaned) > 3 else ""
    
    def _enhanced_forward_search(self, reader, toc_recipes: List[str], total_pages: int) -> Dict[str, int]:
        """
        Enhanced forward search that excludes TOC pages and uses better matching
        
        This fixes the core issue where search was finding recipe titles on TOC pages
        instead of their actual recipe pages.
        """
        
        successful_mappings = {}
        
        # Enhanced search parameters
        search_start = max(750, self.toc_pages['end'] + 10)  # Start well after TOC area
        search_end = min(total_pages, 1200)  # Reasonable recipe section end
        
        logger.info(f"🔍 Forward search: pages {search_start} to {search_end} (excluding TOC {self.toc_pages['start']}-{self.toc_pages['end']})")
        
        for recipe_title in toc_recipes:
            try:
                mapping_result = self._search_recipe_in_range(
                    reader, recipe_title, search_start, search_end
                )
                
                if mapping_result:
                    page_num, confidence = mapping_result
                    self.recipe_index[recipe_title.lower()] = page_num
                    self.page_index[page_num] = recipe_title
                    self.mapping_confidence[recipe_title.lower()] = confidence
                    successful_mappings[recipe_title] = page_num
                    
                    logger.info(f"    ✅ Mapped: '{recipe_title}' → Page {page_num} (confidence: {confidence:.2f})")
                
            except Exception as e:
                logger.warning(f"    ⚠️ Error mapping '{recipe_title}': {e}")
        
        return successful_mappings
    
    def _search_recipe_in_range(self, reader, recipe_title: str, start_page: int, end_page: int) -> Optional[Tuple[int, float]]:
        """
        Search for recipe title in page range with confidence scoring
        
        Returns (page_number, confidence) or None if not found
        """
        
        best_match = None
        best_confidence = 0.0
        
        for page_idx in range(start_page - 1, end_page):
            try:
                # Skip if this is a TOC page
                if self.toc_pages['start'] <= (page_idx + 1) <= self.toc_pages['end']:
                    continue
                
                if page_idx >= len(reader.pages):
                    break
                
                page = reader.pages[page_idx]
                page_text = page.extract_text()
                
                # Multiple matching strategies with confidence scoring
                confidence = self._calculate_title_match_confidence(recipe_title, page_text, page_idx + 1)
                
                if confidence > best_confidence and confidence > 0.6:  # Minimum confidence threshold
                    best_match = (page_idx + 1, confidence)
                    best_confidence = confidence
                
                # If we find a very high confidence match, return immediately
                if confidence > 0.9:
                    return best_match
                    
            except Exception as e:
                logger.debug(f"Error reading page {page_idx + 1}: {e}")
                continue
        
        return best_match if best_confidence > 0.6 else None
    
    def _calculate_title_match_confidence(self, recipe_title: str, page_text: str, page_num: int) -> float:
        """
        Calculate confidence score for recipe title match on page
        
        Uses multiple signals:
        1. Exact match
        2. Simplified match (no punctuation)
        3. Fuzzy string similarity
        4. Position on page (titles usually near top)
        5. Font/formatting clues (if available)
        """
        
        confidence = 0.0
        page_text_lower = page_text.lower()
        recipe_title_lower = recipe_title.lower()
        
        # 1. Exact match (highest confidence)
        if recipe_title_lower in page_text_lower:
            confidence += 0.9
            
            # Bonus if title appears near top of page
            lines = page_text.split('\n')
            for i, line in enumerate(lines[:10]):  # Check first 10 lines
                if recipe_title_lower in line.lower():
                    confidence += 0.1 * (10 - i) / 10  # Higher bonus for earlier lines
                    break
        
        # 2. Simplified match (remove punctuation)
        title_simple = re.sub(r'[^\w\s]', '', recipe_title_lower)
        page_simple = re.sub(r'[^\w\s]', '', page_text_lower)
        
        if title_simple in page_simple and len(title_simple) > 5:
            confidence += 0.7
        
        # 3. Fuzzy string similarity
        similarity = SequenceMatcher(None, recipe_title_lower, page_text_lower[:200]).ratio()
        if similarity > 0.3:
            confidence += similarity * 0.5
        
        # 4. Word overlap scoring
        title_words = set(recipe_title_lower.split())
        page_words = set(page_text_lower.split())
        
        if title_words and len(title_words) > 1:
            word_overlap = len(title_words.intersection(page_words)) / len(title_words)
            if word_overlap > 0.5:
                confidence += word_overlap * 0.6
        
        # 5. Penalize if this looks like TOC content
        if any(toc_indicator in page_text_lower for toc_indicator in [
            'table of contents', 'contents', '..........', 'page '
        ]):
            confidence *= 0.1  # Heavy penalty for TOC-like content
        
        return min(confidence, 1.0)  # Cap at 1.0
    
    def _fuzzy_search_unmapped(self, reader, unmapped_recipes: List[str], total_pages: int) -> Dict[str, int]:
        """
        Fuzzy search for recipes that couldn't be mapped with exact matching
        
        Uses more aggressive fuzzy matching for difficult cases
        """
        
        fuzzy_mappings = {}
        search_start = max(750, self.toc_pages['end'] + 10)
        search_end = min(total_pages, 1200)
        
        for recipe_title in unmapped_recipes:
            try:
                best_match = self._fuzzy_search_single_recipe(
                    reader, recipe_title, search_start, search_end
                )
                
                if best_match:
                    page_num, confidence = best_match
                    
                    # Lower threshold for fuzzy matching
                    if confidence > 0.4:
                        self.recipe_index[recipe_title.lower()] = page_num
                        self.page_index[page_num] = recipe_title
                        self.mapping_confidence[recipe_title.lower()] = confidence
                        fuzzy_mappings[recipe_title] = page_num
                        
                        logger.info(f"    🔍 Fuzzy mapped: '{recipe_title}' → Page {page_num} (confidence: {confidence:.2f})")
                
            except Exception as e:
                logger.warning(f"    ⚠️ Fuzzy search failed for '{recipe_title}': {e}")
        
        return fuzzy_mappings
    
    def _fuzzy_search_single_recipe(self, reader, recipe_title: str, start_page: int, end_page: int) -> Optional[Tuple[int, float]]:
        """
        Fuzzy search for a single recipe with more aggressive matching
        """
        
        best_match = None
        best_confidence = 0.0
        
        # Break title into key words for fuzzy matching
        title_words = [word for word in recipe_title.lower().split() if len(word) > 2]
        
        for page_idx in range(start_page - 1, end_page):
            try:
                # Skip TOC pages
                if self.toc_pages['start'] <= (page_idx + 1) <= self.toc_pages['end']:
                    continue
                
                if page_idx >= len(reader.pages):
                    break
                
                page = reader.pages[page_idx]
                page_text = page.extract_text()
                page_text_lower = page_text.lower()
                
                # Calculate fuzzy confidence
                confidence = self._calculate_fuzzy_confidence(title_words, page_text_lower)
                
                if confidence > best_confidence:
                    best_match = (page_idx + 1, confidence)
                    best_confidence = confidence
                    
            except Exception:
                continue
        
        return best_match if best_confidence > 0.4 else None
    
    def _calculate_fuzzy_confidence(self, title_words: List[str], page_text: str) -> float:
        """
        Calculate fuzzy confidence based on word overlap and positioning
        """
        
        if not title_words:
            return 0.0
        
        page_words = set(page_text.split())
        
        # Word overlap score
        word_matches = sum(1 for word in title_words if word in page_words)
        word_overlap_score = word_matches / len(title_words)
        
        # Position bonus (check if words appear early in page)
        position_bonus = 0.0
        lines = page_text.split('\n')
        for i, line in enumerate(lines[:15]):  # Check first 15 lines
            line_words = set(line.lower().split())
            line_matches = sum(1 for word in title_words if word in line_words)
            if line_matches > 0:
                position_bonus += (line_matches / len(title_words)) * (15 - i) / 15
                break
        
        # Combine scores
        final_confidence = (word_overlap_score * 0.7) + (position_bonus * 0.3)
        
        return final_confidence

# Integration with existing ATK extractor
def apply_enhanced_toc_mapping_fix(atk_extractor):
    """
    Apply the enhanced TOC mapping fix to your existing ATK extractor
    
    Usage:
    extractor = ATK25thUnifiedExtractor()
    apply_enhanced_toc_mapping_fix(extractor)
    """
    
    # Replace the existing TOC mapping method with enhanced version
    enhanced_mapper = EnhancedTOCMapper()
    
    # Monkey patch the enhanced method
    original_method = atk_extractor._extract_toc_with_mapping
    atk_extractor._extract_toc_with_mapping = enhanced_mapper.extract_toc_with_enhanced_mapping
    atk_extractor.enhanced_toc_mapper = enhanced_mapper
    
    logger.info("✅ Applied enhanced TOC mapping fix to ATK extractor")
    logger.info("🔧 TOC search now excludes pages 738-740 and uses fuzzy matching")
    
    return atk_extractor

if __name__ == "__main__":
    # Test the enhanced mapping logic
    print("🔧 Enhanced TOC Mapping Fix Ready")
    print("📋 Features:")
    print("  - Excludes TOC pages from forward search")
    print("  - Fuzzy matching for difficult recipe titles")
    print("  - Confidence scoring for mapping quality")
    print("  - Better handling of title variations")
    print()
    print("🚀 To apply to your ATK extractor:")
    print("  from atk_toc_mapping_fix import apply_enhanced_toc_mapping_fix")
    print("  extractor = ATK25thUnifiedExtractor()")
    print("  enhanced_extractor = apply_enhanced_toc_mapping_fix(extractor)")
