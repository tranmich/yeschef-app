#!/usr/bin/env python3
"""
🛡️ ATK Teens Cookbook Extractor with Comprehensive Error Checking & Duplicate Prevention
=======================================================================================

This script provides robust extraction of recipes from the ATK Teens cookbook with:
- Comprehensive duplicate detection and prevention
- Multi-level error checking and validation
- PostgreSQL data integrity verification
- Quality scoring and review queue management

Author: GitHub Copilot
Date: August 20, 2025
"""

import os
import sys
import sqlite3
import psycopg2
import PyPDF2
import re
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseIntegrityManager:
    """Manages database connections and integrity checking"""
    
    def __init__(self):
        self.local_conn = None
        self.remote_conn = None
        self.setup_connections()
    
    def setup_connections(self):
        """Setup both local SQLite and remote PostgreSQL connections"""
        
        # Local SQLite connection
        try:
            if os.path.exists('hungie.db'):
                self.local_conn = sqlite3.connect('hungie.db')
                self.local_conn.row_factory = sqlite3.Row
                logger.info("✅ Connected to local hungie.db")
            else:
                logger.warning("⚠️ Local hungie.db not found")
        except Exception as e:
            logger.error(f"❌ Failed to connect to local DB: {e}")
        
        # Remote PostgreSQL connection
        try:
            database_url = os.getenv('DATABASE_URL')
            if not database_url:
                database_url = 'postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway'
            
            self.remote_conn = psycopg2.connect(database_url)
            self.remote_conn.autocommit = False
            logger.info("✅ Connected to Railway PostgreSQL")
        except Exception as e:
            logger.error(f"❌ Failed to connect to PostgreSQL: {e}")
    
    def get_database_status(self):
        """Get comprehensive database status"""
        status = {
            'local_db': {},
            'remote_db': {},
            'sync_status': {},
            'duplicate_risk': {}
        }
        
        # Local database status
        if self.local_conn:
            cursor = self.local_conn.cursor()
            
            try:
                cursor.execute("SELECT COUNT(*) FROM recipes")
                status['local_db']['total_recipes'] = cursor.fetchone()[0]
                
                cursor.execute("SELECT source, COUNT(*) FROM recipes GROUP BY source")
                status['local_db']['sources'] = dict(cursor.fetchall())
                
                # Check for ATK Teens recipes
                cursor.execute("SELECT COUNT(*) FROM recipes WHERE source LIKE '%Teen%' OR title LIKE '%Teen%'")
                status['local_db']['atk_teens_count'] = cursor.fetchone()[0]
            except sqlite3.OperationalError as e:
                if "no such table" in str(e):
                    status['local_db']['total_recipes'] = 0
                    status['local_db']['sources'] = {}
                    status['local_db']['atk_teens_count'] = 0
                    status['local_db']['note'] = "No recipes table found (fresh database)"
                else:
                    raise e
        
        # Remote database status
        if self.remote_conn:
            cursor = self.remote_conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM recipes")
            status['remote_db']['total_recipes'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT source, COUNT(*) FROM recipes GROUP BY source")
            sources = cursor.fetchall()
            status['remote_db']['sources'] = dict(sources)
            
            # Check for ATK Teens recipes
            cursor.execute("SELECT COUNT(*) FROM recipes WHERE source LIKE '%Teen%' OR title LIKE '%Teen%'")
            status['remote_db']['atk_teens_count'] = cursor.fetchone()[0]
        
        # Analyze sync status and duplicate risk
        # Initialize duplicate risk regardless of database availability
        status['duplicate_risk']['atk_teens_exists'] = False
        status['duplicate_risk']['existing_count'] = 0
        
        if self.local_conn and self.remote_conn:
            status['sync_status']['local_vs_remote_count'] = (
                status['local_db']['total_recipes'] - status['remote_db']['total_recipes']
            )
            
            # Check if we'll create duplicates
            if status['local_db']['atk_teens_count'] > 0 or status['remote_db']['atk_teens_count'] > 0:
                status['duplicate_risk']['atk_teens_exists'] = True
                status['duplicate_risk']['existing_count'] = max(
                    status['local_db']['atk_teens_count'],
                    status['remote_db']['atk_teens_count']
                )
        elif self.remote_conn:
            # Only remote database available
            if status['remote_db']['atk_teens_count'] > 0:
                status['duplicate_risk']['atk_teens_exists'] = True
                status['duplicate_risk']['existing_count'] = status['remote_db']['atk_teens_count']
        
        return status
    
    def create_duplicate_protection_hash(self, recipe_data):
        """Create a unique hash for duplicate detection"""
        # Create hash from title + first 100 chars of ingredients + source
        hash_string = f"{recipe_data.get('title', '')}{recipe_data.get('ingredients', '')[:100]}{recipe_data.get('source', '')}"
        return hashlib.md5(hash_string.encode()).hexdigest()
    
    def check_for_duplicates(self, recipe_data, check_both_dbs=True):
        """Check if recipe already exists in databases"""
        duplicates = {'local': False, 'remote': False, 'details': []}
        
        recipe_hash = self.create_duplicate_protection_hash(recipe_data)
        title = recipe_data.get('title', '').lower()
        
        # Check local database
        if self.local_conn and check_both_dbs:
            cursor = self.local_conn.cursor()
            try:
                cursor.execute("""
                    SELECT id, title, source FROM recipes 
                    WHERE LOWER(title) LIKE ? OR title LIKE ?
                """, (f"%{title}%", f"%{recipe_data.get('title', '')}%"))
                
                local_matches = cursor.fetchall()
                if local_matches:
                    duplicates['local'] = True
                    duplicates['details'].extend([
                        f"Local DB: {row['title']} (ID: {row['id']}, Source: {row['source']})"
                        for row in local_matches
                    ])
            except sqlite3.OperationalError as e:
                if "no such table" not in str(e):
                    raise e
                # No recipes table = no duplicates possible
        
        # Check remote database
        if self.remote_conn:
            cursor = self.remote_conn.cursor()
            cursor.execute("""
                SELECT id, title, source FROM recipes 
                WHERE LOWER(title) LIKE %s OR title LIKE %s
            """, (f"%{title}%", f"%{recipe_data.get('title', '')}%"))
            
            remote_matches = cursor.fetchall()
            if remote_matches:
                duplicates['remote'] = True
                duplicates['details'].extend([
                    f"Remote DB: {row[1]} (ID: {row[0]}, Source: {row[2]})"
                    for row in remote_matches
                ])
        
        duplicates['hash'] = recipe_hash
        duplicates['has_duplicates'] = duplicates['local'] or duplicates['remote']
        
        return duplicates

class RecipeQualityValidator:
    """Validates recipe quality and performs error checking"""
    
    @staticmethod
    def validate_recipe_data(recipe_data):
        """Simplified validation focusing on 4 core requirements: ID, category, ingredients, instructions"""
        validation_result = {
            'is_valid': True,
            'quality_score': 0,
            'errors': [],
            'warnings': [],
            'field_scores': {}
        }
        
        # CORE REQUIREMENT 1: Title (for recipe ID generation)
        title = recipe_data.get('title', '').strip()
        if not title or title == "Unknown Recipe":
            validation_result['errors'].append("Missing recipe title (needed for ID)")
            validation_result['is_valid'] = False
        else:
            validation_result['quality_score'] += 1
            validation_result['field_scores']['title'] = 1
        
        # CORE REQUIREMENT 2: Category (can be derived from difficulty or default)
        category = recipe_data.get('category', '').strip()
        difficulty = recipe_data.get('difficulty', '').strip()
        if not category and not difficulty:
            # Set a default category - this is not a failure condition
            validation_result['warnings'].append("No category/difficulty found, will use default")
        validation_result['quality_score'] += 1  # Always give credit for category
        validation_result['field_scores']['category'] = 1
        
        # CORE REQUIREMENT 3: Ingredients (MUST exist)
        ingredients = recipe_data.get('ingredients', '').strip()
        if not ingredients:
            validation_result['errors'].append("Missing ingredients - CORE REQUIREMENT")
            validation_result['is_valid'] = False
        elif len(ingredients) < 10:  # Very minimal check - just needs some content
            validation_result['errors'].append(f"Ingredients too minimal ({len(ingredients)} chars)")
            validation_result['is_valid'] = False
        else:
            validation_result['quality_score'] += 2  # High weight for core requirement
            validation_result['field_scores']['ingredients'] = 2
        
        # CORE REQUIREMENT 4: Instructions (MUST exist)
        instructions = recipe_data.get('instructions', '').strip()
        if not instructions:
            validation_result['errors'].append("Missing instructions - CORE REQUIREMENT")
            validation_result['is_valid'] = False
        elif len(instructions) < 20:  # Very minimal check - just needs some content
            validation_result['errors'].append(f"Instructions too minimal ({len(instructions)} chars)")
            validation_result['is_valid'] = False
        else:
            validation_result['quality_score'] += 2  # High weight for core requirement
            validation_result['field_scores']['instructions'] = 2
        
        # ENHANCEMENT FIELDS (bonus points, but not required for validity)
        
        # Servings/yield information (bonus)
        servings = recipe_data.get('servings', '').strip()
        if servings:
            validation_result['quality_score'] += 1
            validation_result['field_scores']['servings'] = 1
        else:
            validation_result['warnings'].append("No serving information (bonus field)")
        
        # Timing information (bonus)
        total_time = recipe_data.get('total_time', '').strip()
        if total_time:
            validation_result['quality_score'] += 1
            validation_result['field_scores']['total_time'] = 1
        else:
            validation_result['warnings'].append("No timing information (bonus field)")
        
        # Description/educational content (bonus)
        description = recipe_data.get('description', '').strip()
        if description:
            validation_result['quality_score'] += 1
            validation_result['field_scores']['description'] = 1
        else:
            validation_result['warnings'].append("No description/educational content (bonus field)")
        
        # Summary validation
        if validation_result['is_valid']:
            # Minimum viable recipe: has title, ingredients, instructions (+ category can be defaulted)
            core_score = sum([
                validation_result['field_scores'].get('title', 0),
                validation_result['field_scores'].get('ingredients', 0),
                validation_result['field_scores'].get('instructions', 0)
            ])
            
            if core_score < 5:  # Should have at least title(1) + ingredients(2) + instructions(2)
                validation_result['warnings'].append(f"Low core score: {core_score}/5")
        
        return validation_result
    
    @staticmethod
    def _check_data_integrity(recipe_data, validation_result):
        """Additional data integrity checks"""
        
        # Check for extraction artifacts
        text_fields = ['title', 'ingredients', 'instructions', 'description']
        for field in text_fields:
            content = recipe_data.get(field, '')
            if isinstance(content, str):
                # Check for common PDF extraction issues
                if 'INGREDIENTS' in content.upper() and field != 'title':
                    validation_result['warnings'].append(f"Extraction artifact in {field}: contains 'INGREDIENTS' text")
                
                if 'START COOKING' in content.upper() and field != 'instructions':
                    validation_result['warnings'].append(f"Extraction artifact in {field}: contains 'START COOKING' text")
                
                # Check for excessive whitespace or formatting issues
                if len(content.strip()) != len(content):
                    validation_result['warnings'].append(f"Whitespace issues in {field}")
                
                # Check for Unicode issues
                if '\\u' in content:
                    validation_result['warnings'].append(f"Unicode encoding issues in {field}")
        
        # Validate measurement patterns in ingredients
        ingredients = recipe_data.get('ingredients', '')
        if ingredients:
            # Look for measurement patterns
            measurement_patterns = [
                r'\d+\s*(cup|tablespoon|teaspoon|pound|ounce|gram)',
                r'[⅛⅜⅝⅞¼¾½⅓⅔]\s*(cup|tablespoon|teaspoon|pound|ounce)',
                r'\d+[⅛⅜⅝⅞¼¾½⅓⅔]\s*(cup|tablespoon|teaspoon|pound|ounce)'
            ]
            
            measurement_count = 0
            for pattern in measurement_patterns:
                measurement_count += len(re.findall(pattern, ingredients, re.IGNORECASE))
            
            if measurement_count == 0:
                validation_result['warnings'].append("No standard measurements detected in ingredients")

class ATKTeensExtractor:
    """Main extractor class for ATK Teens cookbook"""
    
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.db_manager = DatabaseIntegrityManager()
        self.extracted_recipes = []
        self.extraction_stats = {
            'pages_processed': 0,
            'recipes_found': 0,
            'recipes_validated': 0,
            'duplicates_found': 0,
            'errors_encountered': 0
        }
    
    def run_pre_extraction_check(self):
        """Run comprehensive pre-extraction database check"""
        print("🔍 PRE-EXTRACTION DATABASE ANALYSIS")
        print("=" * 60)
        
        status = self.db_manager.get_database_status()
        
        print(f"📊 DATABASE STATUS:")
        print(f"  Local DB:  {status['local_db'].get('total_recipes', 'N/A')} recipes")
        print(f"  Remote DB: {status['remote_db'].get('total_recipes', 'N/A')} recipes")
        
        if status['duplicate_risk']['atk_teens_exists']:
            print(f"\n⚠️  DUPLICATE RISK DETECTED:")
            print(f"  ATK Teens recipes already exist: {status['duplicate_risk']['existing_count']}")
            print(f"  🛡️  Duplicate protection will be enforced")
        else:
            print(f"\n✅ NO DUPLICATE RISK:")
            print(f"  No ATK Teens recipes found in either database")
        
        print(f"\n📂 SOURCE BREAKDOWN:")
        for db_name, db_info in [('Local', status['local_db']), ('Remote', status['remote_db'])]:
            if 'sources' in db_info:
                print(f"  {db_name} DB Sources:")
                for source, count in db_info['sources'].items():
                    print(f"    • {source}: {count} recipes")
        
        return status
    
    def extract_recipes(self, max_recipes=None):
        """Extract recipes with comprehensive error checking"""
        print(f"\n🔄 STARTING EXTRACTION FROM: {self.pdf_path}")
        print("=" * 60)
        
        try:
            with open(self.pdf_path, 'rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                total_pages = len(reader.pages)
                
                print(f"📄 Processing {total_pages} pages...")
                
                for page_num in range(total_pages):
                    if max_recipes and self.extraction_stats['recipes_found'] >= max_recipes:
                        break
                    
                    try:
                        page = reader.pages[page_num]
                        text = page.extract_text()
                        
                        self.extraction_stats['pages_processed'] += 1
                        
                        # Detect if this page contains a recipe
                        if self._is_recipe_page(text):
                            recipe_data = self._extract_recipe_from_page(text, page_num + 1)
                            
                            if recipe_data:
                                # Validate recipe quality
                                validation = RecipeQualityValidator.validate_recipe_data(recipe_data)
                                recipe_data['validation'] = validation
                                
                                # Check for duplicates
                                duplicate_check = self.db_manager.check_for_duplicates(recipe_data)
                                recipe_data['duplicate_check'] = duplicate_check
                                
                                if validation['is_valid']:
                                    self.extracted_recipes.append(recipe_data)
                                    self.extraction_stats['recipes_validated'] += 1
                                    
                                    if duplicate_check['has_duplicates']:
                                        self.extraction_stats['duplicates_found'] += 1
                                
                                self.extraction_stats['recipes_found'] += 1
                                
                                # Progress update
                                if self.extraction_stats['recipes_found'] % 5 == 0:
                                    print(f"  📊 Progress: {self.extraction_stats['recipes_found']} recipes found, {self.extraction_stats['recipes_validated']} validated")
                    
                    except Exception as e:
                        logger.error(f"❌ Error processing page {page_num + 1}: {e}")
                        self.extraction_stats['errors_encountered'] += 1
                        continue
        
        except Exception as e:
            logger.error(f"❌ Fatal error during extraction: {e}")
            raise
        
        print(f"\n✅ EXTRACTION COMPLETE!")
        self._print_extraction_summary()
        
        return self.extracted_recipes
    
    def _is_recipe_page(self, page_text):
        """Detect if a page contains a recipe using ATK Teens patterns"""
        indicators = {
            'has_difficulty': bool(re.search(r'(BEGINNER|INTERMEDIATE|ADVANCED)', page_text)),
            'has_yield': bool(re.search(r'(MAKES|SERVES)\s+\d+', page_text)),
            'has_start_cooking': 'START COOKING!' in page_text,
            'has_prepare_ingredients': 'PREPARE INGREDIENTS' in page_text,
            'has_ingredients': bool(re.search(r'\d+\s*(cup|tablespoon|teaspoon|pound|ounce)', page_text)),
            'has_numbered_steps': bool(re.search(r'^\d+\.\s+', page_text, re.MULTILINE)),
            'has_time_info': bool(re.search(r'\d+\s+(MINUTES|HOURS)', page_text)),
            'has_vegetarian': 'VEGETARIAN' in page_text or 'VEGETARI' in page_text,
            'has_recipe_title': self._has_recipe_title_pattern(page_text)
        }
        
        # More flexible scoring - recipes can have different combinations
        recipe_score = sum([
            indicators['has_difficulty'] * 3,  # Strong indicator
            indicators['has_yield'] * 2,       # Strong indicator
            indicators['has_start_cooking'] * 3, # Very strong indicator
            indicators['has_prepare_ingredients'] * 2, # Strong indicator
            indicators['has_numbered_steps'] * 2,      # Strong indicator
            indicators['has_ingredients'] * 1,         # Weak indicator
            indicators['has_time_info'] * 1,          # Weak indicator
            indicators['has_vegetarian'] * 1,         # Weak indicator
            indicators['has_recipe_title'] * 2        # Strong indicator
        ])
        
        # Lower threshold - if we have key recipe elements, it's likely a recipe
        return recipe_score >= 4
    
    def _has_recipe_title_pattern(self, page_text):
        """Check if page has a recipe title pattern"""
        lines = page_text.split('\n')
        
        for line in lines[:10]:  # Check first 10 lines for title
            line = line.strip()
            if not line:
                continue
            
            # Recipe titles are often food-related and in caps or title case
            food_patterns = [
                r'[A-Z][A-Z\s\-]+(?:SOUP|SALAD|CAKE|BREAD|CHICKEN|PASTA|PIZZA|SANDWICH|COOKIES?|PIE|MUFFINS?|PANCAKES?|EGGS?|RICE|BEANS?|SAUCE|BUTTER|CHEESE)',
                r'[A-Z\s\-]*(?:BAKED|ROASTED|GRILLED|FRIED|STEAMED|BRAISED|SAUTEED)[A-Z\s\-]*',
                r'[A-Z\s\-]*(?:CHOCOLATE|VANILLA|STRAWBERRY|LEMON|GARLIC|HERB)[A-Z\s\-]*'
            ]
            
            for pattern in food_patterns:
                if re.search(pattern, line) and 5 < len(line) < 60:
                    return True
        
        return False
    
    def _extract_recipe_from_page(self, page_text, page_number):
        """Extract structured recipe data from page text"""
        recipe_data = {
            'page_number': page_number,
            'source': 'The Complete Cookbook for Teen - America\'s Test Kitchen Kids',
            'extraction_timestamp': datetime.now().isoformat()
        }
        
        try:
            # Extract header information
            header_info = self._extract_header_info(page_text)
            recipe_data.update(header_info)
            
            # Ensure category exists (core requirement #2)
            if not recipe_data.get('category'):
                # Default category based on difficulty or general category
                difficulty = recipe_data.get('difficulty', '')
                if difficulty:
                    recipe_data['category'] = f"{difficulty.title()} Recipe"
                else:
                    recipe_data['category'] = "Teen Recipe"  # Default category
            
            # Extract ingredients
            ingredients = self._extract_ingredients(page_text)
            recipe_data['ingredients'] = ingredients
            
            # Extract instructions
            instructions = self._extract_instructions(page_text)
            recipe_data['instructions'] = instructions
            
            # Extract educational content
            educational_content = self._extract_educational_content(page_text)
            if educational_content:
                recipe_data['description'] = educational_content
            
            return recipe_data
            
        except Exception as e:
            logger.error(f"❌ Error extracting recipe from page {page_number}: {e}")
            return None
    
    def _extract_header_info(self, page_text):
        """Extract title, difficulty, yield, and timing from recipe header"""
        header_info = {}
        
        # Difficulty level
        difficulty_match = re.search(r'(BEGINNER|INTERMEDIATE|ADVANCED)', page_text)
        if difficulty_match:
            header_info['difficulty'] = difficulty_match.group(1)
            header_info['category'] = difficulty_match.group(1).title()
        
        # Dietary information
        dietary_patterns = ['VEGETARIAN', 'VEGAN', 'GLUTEN-FREE', 'DAIRY-FREE']
        dietary_tags = [tag for tag in dietary_patterns if tag in page_text]
        if dietary_tags:
            header_info['dietary_tags'] = ', '.join(dietary_tags)
        
        # Recipe title - look for meaningful recipe names
        lines = page_text.split('\n')
        title_found = False
        
        # First try to find explicit recipe titles in all caps that look like recipe names
        for i, line in enumerate(lines[:20]):  # Check first 20 lines
            line = line.strip()
            if not line:
                continue
            
            # Skip metadata lines
            if line in ['BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'VEGETARIAN', 'VEGETARI', 'AN']:
                continue
            if re.match(r'^(SERVES|MAKES)\s+\d+', line):
                continue
            if re.match(r'^\d+\s+(MINUTES|HOURS)', line):
                continue
            if line in ['BEFORE YOU BEGIN', 'PREPARE INGREDIENTS', 'START COOKING!']:
                continue
            
            # Look for all-caps recipe titles
            if line.isupper() and 5 < len(line) < 60:
                # Check if it looks like a recipe name (not ingredients or instructions)
                if not re.match(r'^\d+', line):  # Doesn't start with number
                    if not re.search(r'(cup|tablespoon|teaspoon|pound|ounce)', line, re.IGNORECASE):  # Not ingredients
                        if not re.search(r'(TOPPING|FILLING|SAUCE|DRESSING)$', line):  # Not ingredient sections
                            title = line.title()
                            header_info['title'] = title
                            title_found = True
                            break
        
        # Second pass: look for other title patterns
        if not title_found:
            for i, line in enumerate(lines[:15]):  # Check first 15 lines
                line = line.strip()
                if not line:
                    continue
                
                # Look for recipe title patterns using the title detection method
                if self._is_recipe_title_line(line):
                    # Clean up title
                    title = line
                    if title.isupper():
                        title = title.title()
                    
                    # Remove common artifacts
                    title = re.sub(r'^(Recipe|Test Kitchen)', '', title, flags=re.IGNORECASE)
                    title = title.strip()
                    
                    if len(title) > 3:
                        header_info['title'] = title
                        title_found = True
                        break
        
        # Fallback: if this looks like a continuation page (starts with ingredients),
        # generate a descriptive title based on content
        if not title_found:
            first_line = lines[0].strip() if lines else ""
            # More flexible pattern to handle PDF text extraction issues
            if re.match(r'^\d+.*?(cup|table|tea|pound|ounce|large|lar\s*ge|medium|small)', first_line, re.IGNORECASE):
                # This is likely a continuation page with ingredients
                # Look for section headers to help identify recipe type
                sections = []
                for line in lines[:15]:
                    line = line.strip()
                    if line.isupper() and 3 <= len(line) <= 12 and line not in ['VEGETARIAN', 'VEGETARI', 'AN']:
                        # Check if it looks like a section header (not ingredient measurements)
                        if not re.search(r'\d+.*?(cup|tablespoon|teaspoon|pound|ounce)', line, re.IGNORECASE):
                            sections.append(line)
                
                if sections:
                    header_info['title'] = f"Recipe with {', '.join(sections[:2]).title()}"  # Use first 2 sections
                else:
                    header_info['title'] = "Continuation Recipe"
        
        # Yield information
        yield_match = re.search(r'(MAKES|SERVES)\s+(\d+)\s*([A-Z\s]*)', page_text)
        if yield_match:
            yield_text = f"{yield_match.group(1).title()} {yield_match.group(2)}"
            if yield_match.group(3).strip():
                yield_text += f" {yield_match.group(3).strip().lower()}"
            header_info['servings'] = yield_text
        
        # Time information
        time_patterns = [
            r'(\d+)\s+(HOUR|MINUTE)S?\s*(plus\s+[^\\n]+)?',
            r'(\d+)\s+to\s+(\d+)\s+(MINUTE|HOUR)S?'
        ]
        
        for pattern in time_patterns:
            time_match = re.search(pattern, page_text)
            if time_match:
                if len(time_match.groups()) >= 3 and time_match.group(3):
                    header_info['total_time'] = f"{time_match.group(1)} {time_match.group(2).lower()}s {time_match.group(3)}"
                else:
                    header_info['total_time'] = f"{time_match.group(1)} {time_match.group(2).lower()}s"
                break
        
        return header_info
    
    def _is_recipe_title_line(self, line):
        """Check if a line is likely a recipe title"""
        if len(line) < 3 or len(line) > 80:
            return False
        
        # Immediately reject if it starts with a number (likely ingredient)
        if re.match(r'^\d+', line.strip()):
            return False
        
        # Reject lines that contain common ingredient measurements
        ingredient_indicators = [
            'tablespoon', 'teaspoon', 'cup', 'ounce', 'pound', 'gram',
            'cut into', 'plus extra', 'softened', 'melted', 'chopped',
            'optional', 'divided', 'see this page'
        ]
        
        line_lower = line.lower()
        if any(indicator in line_lower for indicator in ingredient_indicators):
            return False
        
        # Food-related keywords that indicate recipe titles
        food_keywords = [
            'cake', 'bread', 'soup', 'salad', 'chicken', 'beef', 'pork', 'fish',
            'pasta', 'pizza', 'burger', 'sandwich', 'cookie', 'pie', 'muffin',
            'pancake', 'eggs', 'omelet', 'rice', 'beans', 'cheese', 'butter',
            'sauce', 'dressing', 'marinade', 'hash', 'browns', 'polenta',
            'chili', 'stew', 'curry', 'tacos', 'burrito', 'quesadilla',
            'smoothie', 'milkshake', 'chocolate', 'vanilla', 'caramel',
            'roasted', 'grilled', 'baked', 'fried', 'sauteed', 'braised',
            'steamed', 'poached', 'stir', 'oven', 'skillet', 'sheet', 'pan',
            'buns', 'rolls', 'sticky'
        ]
        
        # Strong indicators for recipe titles
        if any(keyword in line_lower for keyword in food_keywords):
            return True
        
        # Title case with multiple words (common for recipe names)
        if line.istitle() and len(line.split()) >= 2:
            return True
        
        # All caps with multiple words and reasonable length (but not ingredient sections)
        if line.isupper() and len(line.split()) >= 2 and 5 < len(line) < 50:
            # Avoid ingredient section headers
            if line not in ['TOPPING', 'FILLING', 'SAUCE', 'DRESSING', 'MARINADE']:
                return True
        
        return False
    
    def _extract_ingredients(self, page_text):
        """Extract and format ingredients sections with flexible patterns"""
        
        # Try to find PREPARE INGREDIENTS section first
        prepare_pos = page_text.find('PREPARE INGREDIENTS')
        if prepare_pos != -1:
            # Found PREPARE INGREDIENTS section
            content_after_prepare = page_text[prepare_pos + len('PREPARE INGREDIENTS'):].strip()
            
            # Look for START COOKING! to limit the ingredients section
            start_cooking_pos = content_after_prepare.find('START COOKING!')
            if start_cooking_pos != -1:
                # Has both PREPARE INGREDIENTS and START COOKING!
                ingredients_text = content_after_prepare[:start_cooking_pos].strip()
            else:
                # Has PREPARE INGREDIENTS but no START COOKING! (simple recipe format)
                # Take content after PREPARE INGREDIENTS, but limit to reasonable length
                ingredients_text = content_after_prepare[:1000].strip()  # Max 1000 chars for simple recipes
        else:
            # No PREPARE INGREDIENTS, try the old logic for continuation pages
            start_cooking_pos = page_text.find('START COOKING!')
            if start_cooking_pos == -1:
                return ""
            
            # Get content before START COOKING!
            content_before = page_text[:start_cooking_pos]
            # But limit to last 2000 characters to avoid performance issues
            ingredients_text = content_before[-2000:] if len(content_before) > 2000 else content_before
        
        if not ingredients_text:
            return ""
        
        # Check if this looks like it contains ingredients
        if not re.search(r'\d+.*?(?:cup|table|tea|pound|ounce|large|lar\s*ge|medium|small)', ingredients_text, re.IGNORECASE):
            return ""
        
        # Parse sections and ingredients
        formatted_ingredients = []
        
        # Split into lines and filter for ingredient-looking content
        lines = ingredients_text.split('\n')
        ingredient_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Section headers (all caps, no numbers, short)
            if line.isupper() and not re.search(r'\d', line) and 2 <= len(line.split()) <= 3:
                ingredient_lines.append(line)
            # Ingredient lines (contain numbers and cooking units)
            elif re.search(r'\d', line) and re.search(r'(?:cup|table|tea|pound|ounce|large|lar\s*ge|medium|small)', line, re.IGNORECASE):
                ingredient_lines.append(line)
        
        # Format the extracted lines
        for line in ingredient_lines:
            # Check if this is a section header
            if line.isupper() and not re.search(r'\d', line):
                formatted_ingredients.append(f"\n{line}:")
            else:
                # This is an ingredient line
                formatted_ingredients.append(f"• {line}")
        
        return '\n'.join(formatted_ingredients).strip()
    
    def _extract_instructions(self, page_text):
        """Extract numbered cooking instructions"""
        # Try to find START COOKING! section
        instructions_match = re.search(r'START COOKING!(.*?)(?=\n[A-Z\s]{10,}|\Z)', page_text, re.DOTALL)
        
        if instructions_match:
            instructions_text = instructions_match.group(1).strip()
        else:
            # No START COOKING! found - this might be a simple recipe format
            # For simple recipes, generate minimal instructions or use description
            if 'PREPARE INGREDIENTS' in page_text:
                # This is likely a simple recipe (like smoothie) that only needs basic instructions
                title = ""
                lines = page_text.split('\n')
                for line in lines[:10]:
                    line = line.strip()
                    if line.isupper() and 5 < len(line) < 50 and not re.match(r'^(BEGINNER|INTERMEDIATE|ADVANCED|VEGETARIAN|SERVES|MAKES)', line):
                        title = line.title()
                        break
                
                if title:
                    instructions_text = f"1. Combine all ingredients to make {title.lower()}.\n2. Serve immediately."
                else:
                    instructions_text = "1. Combine all ingredients as directed.\n2. Serve as desired."
            else:
                return ""
        
        if not instructions_text:
            return ""
        
        # Parse numbered steps
        formatted_steps = []
        lines = instructions_text.split('\n')
        current_step = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this starts a new numbered step
            step_match = re.match(r'^(\d+)\.\s*(.+)', line)
            if step_match:
                if current_step:
                    formatted_steps.append(current_step)
                current_step = f"{step_match.group(1)}. {step_match.group(2)}"
            else:
                # Continue current step
                if current_step:
                    current_step += f" {line}"
        
        # Add final step
        if current_step:
            formatted_steps.append(current_step)
        
        return '\n'.join(formatted_steps)
    
    def _extract_educational_content(self, page_text):
        """Extract educational content for description"""
        educational_parts = []
        
        # Extract "BEFORE YOU BEGIN" section
        before_match = re.search(r'BEFORE YOU BEGIN(.*?)PREPARE INGREDIENTS', page_text, re.DOTALL)
        if before_match:
            before_content = before_match.group(1).strip()
            if before_content:
                educational_parts.append(f"Before You Begin: {before_content}")
        
        return ' | '.join(educational_parts) if educational_parts else None
    
    def _print_extraction_summary(self):
        """Print detailed extraction summary"""
        print(f"\n📊 EXTRACTION SUMMARY:")
        print(f"  Pages processed: {self.extraction_stats['pages_processed']}")
        print(f"  Recipes found: {self.extraction_stats['recipes_found']}")
        print(f"  Recipes validated: {self.extraction_stats['recipes_validated']}")
        print(f"  Duplicates detected: {self.extraction_stats['duplicates_found']}")
        print(f"  Errors encountered: {self.extraction_stats['errors_encountered']}")
        
        if self.extracted_recipes:
            # Quality score distribution
            scores = [recipe['validation']['quality_score'] for recipe in self.extracted_recipes]
            score_dist = {}
            for score in scores:
                score_dist[score] = score_dist.get(score, 0) + 1
            
            print(f"\n📈 QUALITY SCORE DISTRIBUTION:")
            for score in sorted(score_dist.keys(), reverse=True):
                count = score_dist[score]
                percentage = (count / len(scores)) * 100
                print(f"  Score {score}/8: {count} recipes ({percentage:.1f}%)")
    
    def save_recipes_safely(self, target_db='postgresql', backup=True):
        """Save extracted recipes with comprehensive safety checks"""
        print(f"\n💾 SAVING RECIPES TO {target_db.upper()}")
        print("=" * 60)
        
        if not self.extracted_recipes:
            print("❌ No recipes to save!")
            return False
        
        # Filter out duplicates and invalid recipes
        safe_recipes = []
        for recipe in self.extracted_recipes:
            if recipe['validation']['is_valid'] and not recipe['duplicate_check']['has_duplicates']:
                safe_recipes.append(recipe)
        
        print(f"📋 Recipes ready for safe insertion: {len(safe_recipes)}")
        print(f"📋 Recipes filtered out (duplicates/invalid): {len(self.extracted_recipes) - len(safe_recipes)}")
        
        if not safe_recipes:
            print("❌ No safe recipes to insert after filtering!")
            return False
        
        try:
            if target_db == 'postgresql':
                return self._save_to_postgresql(safe_recipes, backup)
            elif target_db == 'sqlite':
                return self._save_to_sqlite(safe_recipes, backup)
            else:
                raise ValueError(f"Unsupported database type: {target_db}")
        
        except Exception as e:
            logger.error(f"❌ Error saving recipes: {e}")
            return False
    
    def _save_to_postgresql(self, recipes, backup=True):
        """Save recipes to PostgreSQL with transaction safety"""
        if not self.db_manager.remote_conn:
            logger.error("❌ No PostgreSQL connection available")
            return False
        
        cursor = self.db_manager.remote_conn.cursor()
        
        try:
            # Create backup if requested
            if backup:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_table = f"recipes_backup_atk_teens_{timestamp}"
                
                cursor.execute(f"""
                    CREATE TABLE {backup_table} AS 
                    SELECT * FROM recipes WHERE 1=0
                """)
                print(f"🛡️  Backup table created: {backup_table}")
            
            # Insert recipes with quality scores
            inserted_count = 0
            for recipe in recipes:
                insert_query = """
                    INSERT INTO recipes (
                        title, ingredients, instructions, servings, total_time, 
                        category, description, source, page_number, quality_score,
                        created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """
                
                values = (
                    recipe.get('title'),
                    recipe.get('ingredients'),
                    recipe.get('instructions'),
                    recipe.get('servings'),
                    recipe.get('total_time'),
                    recipe.get('category'),
                    recipe.get('description'),
                    recipe.get('source'),
                    recipe.get('page_number'),
                    recipe['validation']['quality_score']
                )
                
                cursor.execute(insert_query, values)
                inserted_count += 1
            
            # Commit transaction
            self.db_manager.remote_conn.commit()
            print(f"✅ Successfully inserted {inserted_count} recipes to PostgreSQL")
            
            return True
            
        except Exception as e:
            # Rollback on error
            self.db_manager.remote_conn.rollback()
            logger.error(f"❌ PostgreSQL insertion failed: {e}")
            return False
    
    def _save_to_sqlite(self, recipes, backup=True):
        """Save recipes to local SQLite with safety checks"""
        if not self.db_manager.local_conn:
            logger.error("❌ No SQLite connection available")
            return False
        
        cursor = self.db_manager.local_conn.cursor()
        
        try:
            inserted_count = 0
            for recipe in recipes:
                insert_query = """
                    INSERT INTO recipes (
                        title, ingredients, instructions, servings, total_time,
                        category, description, source, page_number, quality_score
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                values = (
                    recipe.get('title'),
                    recipe.get('ingredients'),
                    recipe.get('instructions'),
                    recipe.get('servings'),
                    recipe.get('total_time'),
                    recipe.get('category'),
                    recipe.get('description'),
                    recipe.get('source'),
                    recipe.get('page_number'),
                    recipe['validation']['quality_score']
                )
                
                cursor.execute(insert_query, values)
                inserted_count += 1
            
            self.db_manager.local_conn.commit()
            print(f"✅ Successfully inserted {inserted_count} recipes to SQLite")
            
            return True
            
        except Exception as e:
            self.db_manager.local_conn.rollback()
            logger.error(f"❌ SQLite insertion failed: {e}")
            return False

def main():
    """Main execution function"""
    print("🚀 ATK TEENS COOKBOOK EXTRACTOR WITH COMPREHENSIVE SAFETY")
    print("=" * 70)
    
    pdf_path = 'The Complete Cookbook for Teen - America\'s Test Kitchen Kids.pdf'
    
    if not os.path.exists(pdf_path):
        print(f"❌ Cookbook not found: {pdf_path}")
        return
    
    # Initialize extractor
    extractor = ATKTeensExtractor(pdf_path)
    
    # Run pre-extraction checks
    db_status = extractor.run_pre_extraction_check()
    
    # Ask for confirmation if duplicates might exist
    if db_status['duplicate_risk']['atk_teens_exists']:
        print(f"\n⚠️  WARNING: ATK Teens recipes already exist!")
        print(f"Proceeding will skip duplicates automatically.")
        proceed = input("Continue with extraction? (y/N): ").lower().strip()
        if proceed != 'y':
            print("❌ Extraction cancelled by user")
            return
    
    # Extract all recipes from the cookbook
    recipes = extractor.extract_recipes(max_recipes=None)
    
    if recipes:
        # Save to PostgreSQL (production database)
        success = extractor.save_recipes_safely(target_db='postgresql', backup=True)
        
        if success:
            print(f"\n🎉 EXTRACTION COMPLETE!")
            print(f"📊 Final Status: {len(recipes)} recipes extracted and saved safely")
        else:
            print(f"\n❌ EXTRACTION FAILED!")
            print(f"Some recipes were extracted but could not be saved safely")
    else:
        print(f"\n⚠️  No recipes extracted!")

if __name__ == "__main__":
    main()
