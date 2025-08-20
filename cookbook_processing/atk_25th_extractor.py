#!/usr/bin/env python3
"""
ATK 25th Anniversary Specialized Extractor
Based on structure analysis - optimized for large-scale cookbook with mixed content
"""

import sys
import os
import re
import logging
import PyPDF2
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_systems.database_manager import DatabaseManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RecipeQualityValidator:
    """Enhanced validator for ATK 25th Anniversary recipes"""
    
    @staticmethod
    def validate_recipe_data(recipe_data: Dict) -> Dict:
        """
        Validate recipe data with flexible scoring for large cookbooks
        Core requirements (6 points): title(1) + category(1) + ingredients(2) + instructions(2)
        Bonus fields (1 point each): servings, timing, description
        """
        validation = {
            'is_valid': False,
            'quality_score': 0,
            'errors': [],
            'warnings': [],
            'field_scores': {}
        }
        
        # Core Requirement 1: Title (1 point)
        title = recipe_data.get('title', '').strip()
        if title and len(title) > 2 and not title.startswith('1.'):  # Avoid instruction lines as titles
            validation['field_scores']['title'] = 1
            validation['quality_score'] += 1
        else:
            validation['errors'].append('Missing or invalid title - CORE REQUIREMENT')
            validation['field_scores']['title'] = 0
        
        # Core Requirement 2: Category (1 point) - More flexible for mixed content
        category = recipe_data.get('category', '').strip()
        if category:
            validation['field_scores']['category'] = 1
            validation['quality_score'] += 1
        else:
            validation['errors'].append('Missing category - CORE REQUIREMENT')
            validation['field_scores']['category'] = 0
        
        # Core Requirement 3: Ingredients (2 points)
        ingredients = recipe_data.get('ingredients', '').strip()
        if ingredients and len(ingredients) > 15:  # Slightly higher threshold for large cookbook
            if len(ingredients) > 75:  # Higher threshold for substantial ingredients
                validation['field_scores']['ingredients'] = 2
                validation['quality_score'] += 2
            else:
                validation['field_scores']['ingredients'] = 1
                validation['quality_score'] += 1
        else:
            validation['errors'].append('Missing ingredients - CORE REQUIREMENT')
            validation['field_scores']['ingredients'] = 0
        
        # Core Requirement 4: Instructions (2 points)
        instructions = recipe_data.get('instructions', '').strip()
        if instructions and len(instructions) > 20:  # Higher threshold for detailed instructions
            if len(instructions) > 100:  # Substantial instructions
                validation['field_scores']['instructions'] = 2
                validation['quality_score'] += 2
            else:
                validation['field_scores']['instructions'] = 1
                validation['quality_score'] += 1
        else:
            validation['errors'].append('Missing instructions - CORE REQUIREMENT')
            validation['field_scores']['instructions'] = 0
        
        # Bonus fields (1 point each)
        if recipe_data.get('servings'):
            validation['field_scores']['servings'] = 1
            validation['quality_score'] += 1
        
        if recipe_data.get('total_time'):
            validation['field_scores']['total_time'] = 1
            validation['quality_score'] += 1
        
        if recipe_data.get('description'):
            validation['field_scores']['description'] = 1
            validation['quality_score'] += 1
        
        # Recipe is valid if it has all 4 core requirements (minimum 6 points)
        validation['is_valid'] = validation['quality_score'] >= 6 and len(validation['errors']) == 0
        
        return validation


class ATK25thExtractor:
    """
    Specialized extractor for ATK 25th Anniversary cookbook
    Handles large-scale extraction with mixed content
    """
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.cookbook_title = "America's Test Kitchen 25th Anniversary"
        self.db_manager = DatabaseManager()
        self.extracted_recipes = []
        self.extraction_stats = {
            'pages_processed': 0,
            'pages_skipped': 0,
            'recipes_found': 0,
            'recipes_validated': 0,
            'duplicates_found': 0,
            'errors_encountered': 0,
            'content_types': {
                'recipe_pages': 0,
                'narrative_pages': 0,
                'toc_pages': 0,
                'empty_pages': 0
            }
        }
    
    def _is_recipe_page(self, page_text: str) -> bool:
        """Enhanced recipe page detection for ATK 25th Anniversary format"""
        if not page_text or len(page_text.strip()) < 30:
            self.extraction_stats['content_types']['empty_pages'] += 1
            return False
        
        score = 0
        text_upper = page_text.upper()
        text_lower = page_text.lower()
        
        # Check for title-only pages (recipe names)
        lines = page_text.split('\n')
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        
        if len(non_empty_lines) == 1 and len(non_empty_lines[0]) > 5:
            # Potential recipe title page
            title_line = non_empty_lines[0]
            if self._is_likely_recipe_title(title_line):
                score += 3
        
        # Ingredient pattern indicators (very strong for ATK format)
        ingredient_patterns = [
            r'^\d+\s*(cup|tablespoon|teaspoon|pound|ounce|tbsp|tsp|lb|oz)',
            r'^\d+.*?(large|medium|small)',
            r'^\d+.*?(chopped|diced|minced|sliced|grated)',
            r'(\d+/\d+|\d+\.\d+)\s*(cup|tablespoon|teaspoon)'
        ]
        for pattern in ingredient_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE | re.MULTILINE)
            score += len(matches) * 2  # High weight for ingredient patterns
        
        # Instruction indicators (numbered steps)
        numbered_steps = re.findall(r'^\d+\.\s+', page_text, re.MULTILINE)
        score += len(numbered_steps) * 2  # High weight for numbered instructions
        
        # Recipe metadata indicators
        if re.search(r'(SERVES|MAKES)\s+\d+', text_upper):
            score += 3
        if re.search(r'\d+\s+(MINUTES|HOURS|MINS)', text_upper):
            score += 2
        
        # Cooking action words
        cooking_actions = [
            'whisk', 'combine', 'season', 'heat', 'cook', 'bake', 'stir',
            'add', 'transfer', 'microwave', 'drain', 'toss'
        ]
        for action in cooking_actions:
            if action in text_lower:
                score += 1
        
        # Check for table of contents or index pages
        if self._is_toc_or_index(page_text):
            self.extraction_stats['content_types']['toc_pages'] += 1
            return False
        
        # Check for narrative content
        if self._is_narrative_content(page_text):
            self.extraction_stats['content_types']['narrative_pages'] += 1
            return False
        
        # Lowered threshold for ATK format (simpler structure)
        is_recipe = score >= 4
        if is_recipe:
            self.extraction_stats['content_types']['recipe_pages'] += 1
        
        return is_recipe
    
    def _is_toc_or_index(self, page_text: str) -> bool:
        """Check if page is table of contents or index"""
        toc_indicators = ['contents', 'index', 'acknowledgments', 'introduction']
        text_lower = page_text.lower()
        
        # Look for page numbers with dots/leaders
        page_number_lines = sum(1 for line in page_text.split('\n') 
                              if re.search(r'\d+\s*$', line.strip()))
        
        return (any(indicator in text_lower for indicator in toc_indicators) or
                page_number_lines > 8)
    
    def _is_narrative_content(self, page_text: str) -> bool:
        """Check if page is narrative/educational content"""
        lines = page_text.split('\n')
        long_lines = sum(1 for line in lines if len(line.strip()) > 60)
        
        narrative_indicators = [
            'why this recipe works', 'the science', 'testing notes',
            'we discovered', 'our testing revealed', 'equipment review'
        ]
        
        text_lower = page_text.lower()
        has_narrative = any(indicator in text_lower for indicator in narrative_indicators)
        
        return long_lines > 8 and has_narrative
    
    def _extract_recipe_from_page(self, page_text: str, page_number: int) -> Optional[Dict]:
        """Extract structured recipe data from ATK 25th Anniversary page"""
        recipe_data = {
            'page_number': page_number,
            'source': self.cookbook_title,
            'extraction_timestamp': datetime.now().isoformat()
        }
        
        try:
            # Extract header information
            header_info = self._extract_header_info(page_text)
            recipe_data.update(header_info)
            
            # Ensure category exists (core requirement #2)
            if not recipe_data.get('category'):
                # Default category for ATK recipes
                recipe_data['category'] = "ATK Classic"
            
            # Extract ingredients (core requirement #3)
            ingredients = self._extract_ingredients(page_text)
            recipe_data['ingredients'] = ingredients
            
            # Extract instructions (core requirement #4)
            instructions = self._extract_instructions(page_text)
            recipe_data['instructions'] = instructions
            
            # Extract narrative content (bonus)
            narrative = self._extract_narrative_content(page_text)
            if narrative:
                recipe_data['description'] = narrative
            
            return recipe_data
            
        except Exception as e:
            logger.error(f"❌ Error extracting recipe from page {page_number}: {e}")
            return None
    
    def _extract_header_info(self, page_text: str) -> Dict:
        """Extract title, servings, timing, and other metadata"""
        header_info = {}
        lines = page_text.split('\n')
        
        # Recipe title detection (enhanced for ATK format)
        title_found = False
        
        # Look for recipe titles in first 15 lines
        for i, line in enumerate(lines[:15]):
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            # Skip common non-title lines
            if line.startswith('1.') or line.startswith('INGREDIENTS') or line.startswith('METHOD'):
                continue
            if re.match(r'^(SERVES|MAKES)\s+\d+', line, re.IGNORECASE):
                continue
            
            # Look for recipe title patterns
            if self._is_likely_recipe_title(line):
                title = self._clean_title(line)
                if title and len(title) > 3:
                    header_info['title'] = title
                    title_found = True
                    break
        
        # Fallback title generation
        if not title_found:
            # Try to extract from ingredients or method context
            for line in lines[:20]:
                if 'FOR THE' in line.upper():
                    # Extract recipe name from ingredient section
                    potential_title = line.replace('FOR THE', '').strip()
                    if potential_title and len(potential_title) > 3:
                        header_info['title'] = f"Recipe with {potential_title.title()}"
                        title_found = True
                        break
            
            # Final fallback
            if not title_found:
                header_info['title'] = f"ATK Recipe Page {page_text.split()[0] if page_text.split() else 'Unknown'}"
        
        # Yield information (ATK format)
        yield_patterns = [
            r'(SERVES|MAKES)\s+(\d+)\s*(?:TO\s+(\d+))?\s*([A-Z\s]*)',
            r'(YIELD[S]?)\s*:?\s*(\d+)\s*([A-Z\s]*)'
        ]
        
        for pattern in yield_patterns:
            yield_match = re.search(pattern, page_text, re.IGNORECASE)
            if yield_match:
                yield_text = f"{yield_match.group(1).title()} {yield_match.group(2)}"
                if len(yield_match.groups()) > 2 and yield_match.group(3):
                    yield_text += f" to {yield_match.group(3)}"
                if len(yield_match.groups()) > 3 and yield_match.group(4) and yield_match.group(4).strip():
                    yield_text += f" {yield_match.group(4).strip().lower()}"
                header_info['servings'] = yield_text
                break
        
        # Time information (enhanced patterns for ATK)
        time_patterns = [
            r'(\d+)\s+(HOUR|MINUTE)S?\s*(?:\(?(plus|and|total)?\s*([^)]+)\)?)?',
            r'(\d+)\s+to\s+(\d+)\s+(MINUTE|HOUR)S?',
            r'TOTAL\s+TIME\s*:?\s*(\d+)\s+(MINUTE|HOUR)S?',
            r'PREP\s+TIME\s*:?\s*(\d+)\s+(MINUTE|HOUR)S?.*?COOK\s+TIME\s*:?\s*(\d+)\s+(MINUTE|HOUR)S?'
        ]
        
        for pattern in time_patterns:
            time_match = re.search(pattern, page_text, re.IGNORECASE)
            if time_match:
                groups = time_match.groups()
                if len(groups) >= 2:
                    time_str = f"{groups[0]} {groups[1].lower()}s"
                    if len(groups) > 3 and groups[3]:
                        time_str += f" ({groups[3].strip()})"
                    header_info['total_time'] = time_str
                break
        
        return header_info
    
    def _is_likely_recipe_title(self, line: str) -> bool:
        """Enhanced recipe title detection for ATK format"""
        if len(line) < 3 or len(line) > 80:
            return False
        
        # Skip lines that look like instructions
        if re.match(r'^\d+\.|^Step\s+\d+', line):
            return False
        
        # Skip ingredient-like lines
        ingredient_indicators = [
            'tablespoon', 'teaspoon', 'cup', 'ounce', 'pound', 'gram',
            'chopped', 'diced', 'minced', 'sliced', 'grated',
            'optional', 'divided', 'plus extra'
        ]
        
        line_lower = line.lower()
        if any(indicator in line_lower for indicator in ingredient_indicators):
            return False
        
        # ATK-specific food keywords
        atk_food_keywords = [
            'soup', 'stew', 'roast', 'braised', 'grilled', 'baked',
            'sauce', 'risotto', 'pasta', 'chicken', 'beef', 'pork',
            'fish', 'vegetable', 'bread', 'cake', 'pie', 'cookie',
            'salad', 'chili', 'curry', 'stir-fry', 'casserole'
        ]
        
        # Strong indicators for ATK recipe titles
        if any(keyword in line_lower for keyword in atk_food_keywords):
            return True
        
        # Title case with multiple words
        if line.istitle() and len(line.split()) >= 2:
            return True
        
        # All caps with multiple words (common in ATK)
        if (line.isupper() and 
            len(line.split()) >= 2 and 
            10 < len(line) < 60 and
            not line.startswith('FOR THE')):
            return True
        
        return False
    
    def _clean_title(self, title: str) -> str:
        """Clean and format recipe title"""
        # Remove common artifacts
        title = re.sub(r'^(Recipe|Test Kitchen|ATK)', '', title, flags=re.IGNORECASE)
        title = title.strip()
        
        # Convert all caps to title case if needed
        if title.isupper():
            title = title.title()
        
        return title
    
    def _extract_ingredients(self, page_text: str) -> str:
        """Extract ingredients for ATK 25th Anniversary format (no INGREDIENTS header)"""
        
        lines = page_text.split('\n')
        ingredient_lines = []
        
        # Look for lines that start with measurements
        ingredient_patterns = [
            r'^\d+\s*(cup|tablespoon|teaspoon|pound|ounce|tbsp|tsp|lb|oz)',
            r'^\d+.*?(large|medium|small)',
            r'^\d+.*?(chopped|diced|minced|sliced|grated)',
            r'^(\d+/\d+|\d+\.\d+)\s*(cup|tablespoon|teaspoon)',
            r'^\d+\s*(ounces?|pounds?)\s+',
            r'^\d+\s+[A-Za-z].*?(plus|divided|optional)'
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line looks like an ingredient
            for pattern in ingredient_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    ingredient_lines.append(f"• {line}")
                    break
        
        # If we found very few ingredients, try a broader search
        if len(ingredient_lines) < 3:
            # Look for any line with measurements and food words
            food_words = ['oil', 'salt', 'pepper', 'garlic', 'onion', 'butter', 'flour', 'sugar', 'water']
            
            for line in lines:
                line = line.strip()
                if not line or line in [l.replace('• ', '') for l in ingredient_lines]:
                    continue
                
                # Check if line has measurements and food words
                has_measurement = re.search(r'\d+\s*(cup|tablespoon|teaspoon|pound|ounce|tbsp|tsp|lb|oz)', line, re.IGNORECASE)
                has_food_word = any(word in line.lower() for word in food_words)
                
                if has_measurement and has_food_word:
                    ingredient_lines.append(f"• {line}")
        
        return '\n'.join(ingredient_lines) if ingredient_lines else ""
    
    def _extract_instructions(self, page_text: str) -> str:
        """Extract instructions for ATK 25th Anniversary format (numbered steps)"""
        
        lines = page_text.split('\n')
        instruction_lines = []
        
        # Look for numbered steps
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line starts with a number and period
            step_match = re.match(r'^(\d+)\.\s*(.+)', line)
            if step_match:
                step_num = step_match.group(1)
                step_text = step_match.group(2)
                instruction_lines.append(f"{step_num}. {step_text}")
        
        # If no numbered steps found, look for other instruction patterns
        if not instruction_lines:
            cooking_instructions = []
            
            for line in lines:
                line = line.strip()
                if not line or len(line) < 20:
                    continue
                
                # Look for lines that contain cooking actions
                cooking_verbs = ['heat', 'cook', 'bake', 'whisk', 'combine', 'add', 'stir', 'season', 'transfer', 'drain']
                if any(verb in line.lower() for verb in cooking_verbs):
                    cooking_instructions.append(line)
            
            # Format as numbered steps
            for i, instruction in enumerate(cooking_instructions, 1):
                instruction_lines.append(f"{i}. {instruction}")
        
        return '\n'.join(instruction_lines) if instruction_lines else ""
    
    def _extract_narrative_content(self, page_text: str) -> str:
        """Extract educational/narrative content from ATK pages"""
        narrative_patterns = [
            r'WHY THIS RECIPE WORKS(.*?)(?=INGREDIENTS|METHOD|\n[A-Z\s]{10,}|\Z)',
            r'THE SCIENCE(.*?)(?=INGREDIENTS|METHOD|\n[A-Z\s]{10,}|\Z)',
            r'TESTING NOTES(.*?)(?=INGREDIENTS|METHOD|\n[A-Z\s]{10,}|\Z)',
            r'EQUIPMENT REVIEW(.*?)(?=INGREDIENTS|METHOD|\n[A-Z\s]{10,}|\Z)'
        ]
        
        narrative_content = []
        
        for pattern in narrative_patterns:
            matches = re.findall(pattern, page_text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                content = match.strip()
                if content and len(content) > 30:
                    narrative_content.append(content)
        
        return '\n\n'.join(narrative_content) if narrative_content else ""
    
    def _simple_duplicate_check(self, recipe_data: Dict) -> Dict:
        """Simple duplicate check for testing"""
        title = recipe_data.get('title', '').lower()
        
        # Basic check against database
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) as count FROM recipes 
                    WHERE LOWER(title) LIKE %s AND source = %s
                """, (f"%{title}%", self.cookbook_title))
                
                result = cursor.fetchone()
                has_duplicates = result['count'] > 0 if result else False
                
                return {
                    'has_duplicates': has_duplicates,
                    'duplicate_count': result['count'] if result else 0,
                    'check_method': 'simple_title_match'
                }
        except Exception as e:
            logger.warning(f"⚠️ Duplicate check failed: {e}")
            return {
                'has_duplicates': False,
                'duplicate_count': 0,
                'check_method': 'failed'
            }
    
    def extract_recipes(self, max_recipes: Optional[int] = None, start_page: int = 1, end_page: Optional[int] = None) -> List[Dict]:
        """
        Main extraction method for ATK 25th Anniversary
        Uses multi-page recipe assembly for better results
        """
        logger.info(f"🔄 STARTING ATK 25TH ANNIVERSARY EXTRACTION")
        logger.info("=" * 60)
        
        try:
            with open(self.pdf_path, 'rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                total_pages = len(reader.pages)
                
                # Determine page range
                start_idx = start_page - 1
                end_idx = end_page if end_page else total_pages
                end_idx = min(end_idx, total_pages)
                
                logger.info(f"📄 Processing pages {start_page} to {end_idx} (of {total_pages} total)")
                
                # Collect all pages first for multi-page recipe assembly
                page_data = []
                for page_num in range(start_idx, end_idx):
                    try:
                        page = reader.pages[page_num]
                        text = page.extract_text()
                        page_data.append({
                            'page_number': page_num + 1,
                            'text': text,
                            'is_recipe_related': self._is_recipe_page(text)
                        })
                        self.extraction_stats['pages_processed'] += 1
                    except Exception as e:
                        logger.error(f"❌ Error processing page {page_num + 1}: {e}")
                        self.extraction_stats['errors_encountered'] += 1
                        continue
                
                # Now assemble recipes from page groups
                self._assemble_recipes_from_pages(page_data, max_recipes)
        
        except Exception as e:
            logger.error(f"❌ Fatal error during extraction: {e}")
            raise
        
        logger.info(f"\n✅ EXTRACTION COMPLETE!")
        self._print_extraction_summary()
        
        return self.extracted_recipes
    
    def _assemble_recipes_from_pages(self, page_data: List[Dict], max_recipes: Optional[int] = None):
        """Assemble recipes from multiple pages"""
        i = 0
        while i < len(page_data) and (not max_recipes or self.extraction_stats['recipes_found'] < max_recipes):
            current_page = page_data[i]
            
            if not current_page['is_recipe_related']:
                self.extraction_stats['pages_skipped'] += 1
                i += 1
                continue
            
            # Try to build a recipe from current page and nearby pages
            recipe_data = self._build_recipe_from_page_group(page_data, i)
            
            if recipe_data:
                # Validate recipe quality
                validation = RecipeQualityValidator.validate_recipe_data(recipe_data)
                recipe_data['validation'] = validation
                
                # Check for duplicates (simplified)
                duplicate_check = self._simple_duplicate_check(recipe_data)
                recipe_data['duplicate_check'] = duplicate_check
                
                if validation['is_valid']:
                    self.extracted_recipes.append(recipe_data)
                    self.extraction_stats['recipes_validated'] += 1
                    
                    if duplicate_check['has_duplicates']:
                        self.extraction_stats['duplicates_found'] += 1
                
                self.extraction_stats['recipes_found'] += 1
                
                # Progress update every 25 recipes
                if self.extraction_stats['recipes_found'] % 25 == 0:
                    logger.info(f"  📊 Progress: {self.extraction_stats['recipes_found']} recipes found, {self.extraction_stats['recipes_validated']} validated")
            
            i += 1
    
    def _build_recipe_from_page_group(self, page_data: List[Dict], start_idx: int) -> Optional[Dict]:
        """Build a complete recipe from a group of pages"""
        recipe_parts = {
            'title': '',
            'ingredients': '',
            'instructions': '',
            'page_numbers': [],
            'combined_text': ''
        }
        
        # Check current page and up to 2 pages forward/backward
        search_range = range(max(0, start_idx - 2), min(len(page_data), start_idx + 3))
        
        for idx in search_range:
            page = page_data[idx]
            text = page['text']
            page_num = page['page_number']
            
            if not text or len(text.strip()) < 10:
                continue
            
            recipe_parts['combined_text'] += f"\n{text}"
            recipe_parts['page_numbers'].append(page_num)
            
            # Check for recipe title (single line pages)
            lines = text.split('\n')
            non_empty_lines = [line.strip() for line in lines if line.strip()]
            
            if len(non_empty_lines) == 1 and not recipe_parts['title']:
                potential_title = non_empty_lines[0]
                if self._is_likely_recipe_title(potential_title):
                    recipe_parts['title'] = potential_title
            
            # Extract ingredients from this page
            page_ingredients = self._extract_ingredients(text)
            if page_ingredients and len(page_ingredients) > len(recipe_parts['ingredients']):
                recipe_parts['ingredients'] = page_ingredients
            
            # Extract instructions from this page
            page_instructions = self._extract_instructions(text)
            if page_instructions and len(page_instructions) > len(recipe_parts['instructions']):
                recipe_parts['instructions'] = page_instructions
        
        # Build final recipe data
        if recipe_parts['ingredients'] or recipe_parts['instructions']:
            recipe_data = {
                'page_number': start_idx + 1,  # Primary page
                'page_numbers': recipe_parts['page_numbers'],
                'source': self.cookbook_title,
                'extraction_timestamp': datetime.now().isoformat(),
                'title': recipe_parts['title'] or f"ATK Recipe from Page {start_idx + 1}",
                'category': 'ATK Classic',
                'ingredients': recipe_parts['ingredients'],
                'instructions': recipe_parts['instructions']
            }
            
            # Extract additional metadata from combined text
            combined_text = recipe_parts['combined_text']
            
            # Look for servings/yield
            yield_match = re.search(r'(SERVES|MAKES)\s+(\d+)\s*(?:TO\s+(\d+))?\s*([A-Z\s]*)', combined_text, re.IGNORECASE)
            if yield_match:
                yield_text = f"{yield_match.group(1).title()} {yield_match.group(2)}"
                if yield_match.group(3):
                    yield_text += f" to {yield_match.group(3)}"
                if yield_match.group(4) and yield_match.group(4).strip():
                    yield_text += f" {yield_match.group(4).strip().lower()}"
                recipe_data['servings'] = yield_text
            
            # Look for timing
            time_match = re.search(r'(\d+)\s+(HOUR|MINUTE)S?\s*(?:\(?(plus|and|total)?\s*([^)]+)\)?)?', combined_text, re.IGNORECASE)
            if time_match:
                time_str = f"{time_match.group(1)} {time_match.group(2).lower()}s"
                if time_match.group(4):
                    time_str += f" ({time_match.group(4).strip()})"
                recipe_data['total_time'] = time_str
            
            return recipe_data
        
        return None
    
    def _print_extraction_summary(self):
        """Print comprehensive extraction summary"""
        stats = self.extraction_stats
        total_processed = stats['pages_processed']
        total_found = stats['recipes_found']
        validated = stats['recipes_validated']
        
        logger.info(f"\n📊 ATK 25TH ANNIVERSARY EXTRACTION SUMMARY:")
        logger.info(f"  Pages processed: {total_processed}")
        logger.info(f"  Pages skipped: {stats['pages_skipped']}")
        logger.info(f"  Recipes found: {total_found}")
        logger.info(f"  Recipes validated: {validated}")
        logger.info(f"  Duplicates detected: {stats['duplicates_found']}")
        logger.info(f"  Errors encountered: {stats['errors_encountered']}")
        
        if total_processed > 0:
            recipe_density = (total_found / total_processed) * 100
            logger.info(f"  Recipe density: {recipe_density:.1f}% (recipes per page)")
        
        logger.info(f"\n📈 CONTENT TYPE DISTRIBUTION:")
        for content_type, count in stats['content_types'].items():
            if total_processed > 0:
                percentage = (count / total_processed) * 100
                logger.info(f"  {content_type.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")
        
        if validated > 0:
            success_rate = (validated / total_found) * 100
            logger.info(f"\n✅ Validation success rate: {success_rate:.1f}%")
            
            # Quality score distribution
            score_distribution = {}
            for recipe in self.extracted_recipes:
                score = recipe['validation']['quality_score']
                score_key = f"{score}/8"
                score_distribution[score_key] = score_distribution.get(score_key, 0) + 1
            
            logger.info(f"\n📈 QUALITY SCORE DISTRIBUTION:")
            for score, count in sorted(score_distribution.items(), key=lambda x: int(x[0].split('/')[0]), reverse=True):
                percentage = (count / validated) * 100
                logger.info(f"  Score {score}: {count} recipes ({percentage:.1f}%)")
    
    def save_to_database(self, safe_mode: bool = True) -> int:
        """Save extracted recipes to database with safety checks"""
        if not self.extracted_recipes:
            logger.warning("⚠️ No validated recipes to save")
            return 0
        
        # Filter out duplicates and invalid recipes
        valid_recipes = [r for r in self.extracted_recipes if r['validation']['is_valid']]
        unique_recipes = [r for r in valid_recipes if not r['duplicate_check']['has_duplicates']]
        
        logger.info(f"\n💾 SAVING ATK 25TH ANNIVERSARY RECIPES")
        logger.info("=" * 60)
        logger.info(f"📋 Recipes ready for insertion: {len(unique_recipes)}")
        logger.info(f"📋 Recipes filtered out: {len(self.extracted_recipes) - len(unique_recipes)}")
        
        if safe_mode:
            # Create backup (simplified)
            from datetime import datetime
            backup_table = f"recipes_backup_atk25th_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            try:
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(f"CREATE TABLE {backup_table} AS SELECT * FROM recipes WHERE 1=0")
                    conn.commit()
                logger.info(f"🛡️ Backup table created: {backup_table}")
            except Exception as e:
                logger.warning(f"⚠️ Backup creation failed: {e}")
        
        # Insert recipes (simplified)
        inserted_count = 0
        for recipe in unique_recipes:
            try:
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO recipes (title, category, ingredients, instructions, servings, total_time, description, source, page_number, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    """, (
                        recipe.get('title'),
                        recipe.get('category'),
                        recipe.get('ingredients'),
                        recipe.get('instructions'),
                        recipe.get('servings'),
                        recipe.get('total_time'),
                        recipe.get('description'),
                        recipe.get('source'),
                        recipe.get('page_number')
                    ))
                    conn.commit()
                inserted_count += 1
            except Exception as e:
                logger.error(f"❌ Error inserting recipe '{recipe.get('title', 'Unknown')}': {e}")
        
        logger.info(f"✅ Successfully inserted {inserted_count} recipes")
        return inserted_count


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ATK 25th Anniversary Recipe Extractor')
    parser.add_argument('--max-recipes', type=int, help='Maximum recipes to extract (for testing)')
    parser.add_argument('--start-page', type=int, default=1, help='Start page number')
    parser.add_argument('--end-page', type=int, help='End page number')
    parser.add_argument('--no-save', action='store_true', help='Don\'t save to database')
    
    args = parser.parse_args()
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
    
    if not os.path.exists(pdf_path):
        logger.error(f"❌ PDF file not found: {pdf_path}")
        return
    
    # Create extractor
    extractor = ATK25thExtractor(pdf_path)
    
    # Extract recipes
    recipes = extractor.extract_recipes(
        max_recipes=args.max_recipes,
        start_page=args.start_page,
        end_page=args.end_page
    )
    
    # Save to database
    if not args.no_save and recipes:
        inserted_count = extractor.save_to_database()
        logger.info(f"\n🎉 EXTRACTION COMPLETE!")
        logger.info(f"📊 Final Status: {len(recipes)} recipes extracted and {inserted_count} saved")


if __name__ == "__main__":
    main()
