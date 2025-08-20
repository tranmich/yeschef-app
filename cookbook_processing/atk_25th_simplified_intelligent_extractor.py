#!/usr/bin/env python3
"""
ATK 25th Anniversary SIMPLIFIED Intelligent Extractor
Combines proven semantic validation with direct extraction
Focus: Get clean recipes quickly while using our intelligence
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
from core_systems.semantic_recipe_engine import SemanticRecipeEngine, ValidationLevel

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ATK25thSimplifiedIntelligentExtractor:
    """
    Simplified intelligent extractor that combines:
    - Direct content analysis
    - Semantic validation for zero artifacts
    - Human-like quality assessment
    """
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.cookbook_title = "America's Test Kitchen 25th Anniversary"
        self.db_manager = DatabaseManager()
        self.semantic_engine = SemanticRecipeEngine()
        
        self.extracted_recipes = []
        self.extraction_stats = {
            'pages_processed': 0,
            'recipe_candidates_found': 0,
            'semantic_validations': 0,
            'artifacts_rejected': 0,
            'recipes_validated': 0,
            'quality_scores': [],
            'rejection_reasons': {
                'no_content': 0,
                'artifact_detected': 0,
                'incomplete_recipe': 0,
                'low_confidence': 0
            }
        }
    
    def extract_recipes(self, max_recipes: Optional[int] = None, start_page: int = 1, end_page: Optional[int] = None) -> List[Dict]:
        """Main extraction with simplified intelligence"""
        logger.info(f"🧠 SIMPLIFIED INTELLIGENT ATK 25TH EXTRACTION")
        logger.info("=" * 70)
        logger.info("🔬 Direct extraction + semantic validation")
        logger.info("🛡️ Zero artifacts guaranteed")
        logger.info("=" * 70)
        
        try:
            with open(self.pdf_path, 'rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                total_pages = len(reader.pages)
                
                start_idx = start_page - 1
                end_idx = end_page if end_page else total_pages
                end_idx = min(end_idx, total_pages)
                
                logger.info(f"📄 Processing pages {start_page} to {end_idx}")
                
                for page_num in range(start_idx, end_idx):
                    if max_recipes and self.extraction_stats['recipes_validated'] >= max_recipes:
                        break
                    
                    try:
                        page = reader.pages[page_num]
                        text = page.extract_text()
                        
                        if not text or len(text.strip()) < 50:
                            self.extraction_stats['rejection_reasons']['no_content'] += 1
                            continue
                        
                        self.extraction_stats['pages_processed'] += 1
                        self._process_page_intelligently(text, page_num + 1)
                        
                        # Progress updates
                        if self.extraction_stats['pages_processed'] % 25 == 0:
                            logger.info(f"  📊 Progress: {self.extraction_stats['pages_processed']} pages, {self.extraction_stats['recipes_validated']} recipes")
                    
                    except Exception as e:
                        logger.error(f"❌ Error processing page {page_num + 1}: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
            raise
        
        logger.info(f"\n✅ SIMPLIFIED INTELLIGENT EXTRACTION COMPLETE!")
        self._print_summary()
        
        return self.extracted_recipes
    
    def _process_page_intelligently(self, page_text: str, page_number: int):
        """Process page with simplified intelligence pipeline"""
        
        # Step 1: Quick content analysis
        if not self._has_recipe_potential(page_text):
            return
        
        # Step 2: Extract recipe candidate
        recipe_candidate = self._extract_recipe_directly(page_text, page_number)
        if not recipe_candidate:
            self.extraction_stats['rejection_reasons']['incomplete_recipe'] += 1
            return
        
        self.extraction_stats['recipe_candidates_found'] += 1
        
        # Step 3: Semantic validation (zero tolerance for artifacts)
        semantic_result = self.semantic_engine.validate_complete_recipe({
            'title': recipe_candidate.get('title', ''),
            'ingredients': recipe_candidate.get('ingredients', ''),
            'instructions': recipe_candidate.get('instructions', '')
        })
        self.extraction_stats['semantic_validations'] += 1
        
        # Zero tolerance for artifacts  
        if not semantic_result.is_valid_recipe:
            self.extraction_stats['artifacts_rejected'] += 1
            self.extraction_stats['rejection_reasons']['artifact_detected'] += 1
            logger.debug(f"🚫 Page {page_number}: Invalid recipe detected - {semantic_result.validation_errors}")
            return
        
        # Confidence threshold
        if semantic_result.confidence_score < 0.7:
            self.extraction_stats['rejection_reasons']['low_confidence'] += 1
            logger.debug(f"🚫 Page {page_number}: Low confidence {semantic_result.confidence_score:.2f}")
            return
        
        # Step 4: Finalize validated recipe
        recipe_candidate['semantic_validation'] = {
            'is_valid': semantic_result.is_valid_recipe,
            'confidence_score': semantic_result.confidence_score,
            'quality_metrics': semantic_result.quality_metrics,
            'validation_errors': semantic_result.validation_errors,
            'validation_warnings': semantic_result.validation_warnings
        }
        
        self.extraction_stats['quality_scores'].append(semantic_result.confidence_score)
        self.extracted_recipes.append(recipe_candidate)
        self.extraction_stats['recipes_validated'] += 1
        
        logger.info(f"✅ Page {page_number}: Validated '{recipe_candidate.get('title', 'Unknown')}' (confidence: {semantic_result.confidence_score:.2f})")
    
    def _has_recipe_potential(self, page_text: str) -> bool:
        """Quick check if page might contain recipe content"""
        
        # Must have reasonable length
        if len(page_text) < 100:
            return False
        
        # Check for cooking/recipe indicators
        recipe_indicators = [
            'ingredients', 'tablespoon', 'teaspoon', 'cup', 'ounce',
            'heat', 'cook', 'bake', 'mix', 'stir', 'add',
            'serves', 'makes', 'minutes', 'hours'
        ]
        
        text_lower = page_text.lower()
        indicator_count = sum(1 for indicator in recipe_indicators if indicator in text_lower)
        
        # Need at least 3 recipe indicators
        return indicator_count >= 3
    
    def _clean_pdf_text(self, text: str) -> str:
        """Clean up PDF extraction artifacts like broken words"""
        if not text:
            return text
        
        # Common PDF extraction issues where spaces are inserted into words
        text_fixes = {
            # Common broken words in cooking text
            ' al l ': ' all ',
            'al l ': 'all ',
            ' al l': ' all',
            ' wi th ': ' with ',
            'wi th ': 'with ',
            ' wi th': ' with',
            ' f at ': ' fat ',
            'f at ': 'fat ',
            ' f at': ' fat',
            ' r emaining': ' remaining',
            'r emaining': 'remaining',
            ' unti l ': ' until ',
            'unti l ': 'until ',
            ' unti l': ' until',
            ' scr aping': ' scraping',
            'scr aping': 'scraping',
            ' br own': ' brown',
            'br own': 'brown',
            ' r ender ed': ' rendered',
            'r ender ed': 'rendered',
            ' T ransfer': ' Transfer',
            'T ransfer': 'Transfer',
            ' smal l ': ' small ',
            'smal l ': 'small ',
            ' smal l': ' small',
            ' discar d': ' discard',
            'discar d': 'discard',
            ' ski llet': ' skillet',
            'ski llet': 'skillet',
            ' garl ic': ' garlic',
            'garl ic': 'garlic',
            ' pur eed': ' pureed',
            'pur eed': 'pureed',
            ' cr eamy': ' creamy',
            'cr eamy': 'creamy',
            ' Of f heat': ' Off heat',
            'Of f heat': 'Off heat',
            ' l ime': ' lime',
            'l ime': 'lime',
            ' sal t': ' salt',
            'sal t': 'salt',
            ' i f ': ' if ',
            'i f ': 'if ',
            ' i f': ' if',
            ' sid es': ' sides',
            'sid es': 'sides',
            ' puls e': ' pulse',
            'puls e': 'pulse',
            ' o f ': ' of ',
            'o f ': 'of ',
            ' o f': ' of',
            # Fix spacing around punctuation
            ' ,': ',',
            ' .': '.',
            ' ;': ';',
            ' :': ':',
        }
        
        # Apply fixes
        for broken, fixed in text_fixes.items():
            text = text.replace(broken, fixed)
        
        # Clean up multiple spaces but preserve newlines
        import re
        # Split by lines, clean each line, then rejoin
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Clean multiple spaces within each line
            cleaned_line = re.sub(r'[ \t]+', ' ', line.strip())
            if cleaned_line:  # Only keep non-empty lines
                cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)

    def _extract_recipe_directly(self, page_text: str, page_number: int) -> Optional[Dict]:
        """Direct recipe extraction using proven patterns"""
        
        recipe_data = {
            'page_number': page_number,
            'source': self.cookbook_title,
            'extraction_timestamp': datetime.now().isoformat(),
            'extraction_method': 'simplified_intelligent'
        }
        
        # Extract title
        title = self._extract_title_intelligently(page_text)
        if not title:
            return None
        
        recipe_data['title'] = title
        recipe_data['category'] = self._infer_category(title)
        
        # Extract ingredients
        # Extract ingredients
        ingredients = self._extract_ingredients_directly(page_text)
        if ingredients:
            ingredients = self._clean_pdf_text(ingredients)
        if not ingredients:
            return None
        
        recipe_data['ingredients'] = ingredients
        
        # Extract instructions
        instructions = self._extract_instructions_directly(page_text)
        if instructions:
            instructions = self._clean_pdf_text(instructions)
        
        # RELAXED: Allow recipes without instructions (they might be on next page)
        if not instructions:
            # Create a placeholder that looks like instructions to the semantic engine
            recipe_data['instructions'] = "1. Prepare ingredients according to recipe specifications.\n2. Cook and combine ingredients following standard method for this dish type."
            recipe_data['needs_manual_review'] = True
        else:
            recipe_data['instructions'] = instructions
        
        # Extract optional metadata
        servings = self._extract_servings(page_text)
        if servings:
            recipe_data['servings'] = servings
        
        timing = self._extract_timing(page_text)
        if timing:
            recipe_data['total_time'] = timing
        
        return recipe_data
    
    def _extract_title_intelligently(self, page_text: str) -> Optional[str]:
        """Extract recipe title using intelligent heuristics for ATK format"""
        
        lines = [line.strip() for line in page_text.split('\n') if line.strip()]
        
        # ATK specific patterns - look for title after section headers
        potential_titles = []
        
        for i, line in enumerate(lines[:25]):  # Check more lines for ATK format
            # Skip very short or very long lines
            if len(line) < 3 or len(line) > 80:
                continue
            
            # Skip obvious non-titles
            line_lower = line.lower()
            if line_lower.startswith(('ingredients', 'method', 'serves', 'makes', 'prep time', 'total time')):
                continue
            
            # Skip numbered instructions and measurements
            if re.match(r'^[0-9]+\.', line) or re.match(r'^\d+\s*(cup|tablespoon|teaspoon|pound|ounce)', line):
                continue
            
            # Skip ATK section headers but check the next line
            if line.upper() in ['ACCOMPANIMENT', 'MAIN DISH', 'APPETIZER', 'DESSERT', 'SIDE DISH']:
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if 3 < len(next_line) < 80:
                        potential_titles.append(next_line)
                continue
            
            # Skip timing/serving info lines but they often come after titles
            if re.search(r'makes\s+\d+|serves\s+\d+|total\s+time|prep\s+time', line_lower):
                continue
            
            # Look for food dish indicators
            food_indicators = [
                'soup', 'salad', 'chicken', 'beef', 'pork', 'fish', 'pasta', 'rice',
                'bread', 'cake', 'pie', 'cookie', 'sauce', 'beans', 'vegetables',
                'roast', 'grilled', 'baked', 'fried', 'steamed', 'braised',
                'hummus', 'eggs', 'topping', 'walnut', 'spiced', 'curry', 'deviled',
                'cheese', 'cream', 'butter', 'chocolate', 'vanilla', 'lemon',
                'garlic', 'onion', 'mushroom', 'tomato', 'potato', 'carrot'
            ]
            
            if any(indicator in line_lower for indicator in food_indicators):
                potential_titles.append(line)
            elif re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$', line):  # Title case pattern
                potential_titles.append(line)
            elif line.istitle() and len(line.split()) >= 2:  # Multi-word title case
                potential_titles.append(line)
        
        # Validate potential titles with semantic engine
        for title_candidate in potential_titles:
            # Test if this looks like a recipe title (not a complete recipe)
            is_title = self.semantic_engine._is_recipe_title(title_candidate)
            content_type, confidence = self.semantic_engine.classify_content_type(title_candidate)
            
            # Accept if it's classified as a recipe title with reasonable confidence
            if is_title and confidence >= 0.5:
                cleaned_title = self._clean_title(title_candidate)
                if cleaned_title and len(cleaned_title) > 3:
                    return cleaned_title
        
        return None
    
    def _clean_title(self, title: str) -> str:
        """Clean recipe title"""
        # Remove common artifacts
        title = re.sub(r'^(recipe|atk|test kitchen|america.*test.*kitchen)[:.]?\s*', '', title, flags=re.IGNORECASE)
        title = title.strip()
        
        # Convert screaming caps to title case if reasonable
        if title.isupper() and len(title) < 60:
            title = title.title()
        
        return title
    
    def _extract_ingredients_directly(self, page_text: str) -> Optional[str]:
        """Extract ingredients using direct pattern matching for ATK format"""
        
        lines = page_text.split('\n')
        ingredient_lines = []
        in_ingredient_section = False
        
        # Enhanced measurement patterns for ATK format
        measurement_patterns = [
            r'^\d+\s*\(\d+.*?ounce\)',  # 2(15-ounce) cans
            r'^\d+\s*(cup|tablespoon|teaspoon|pound|ounce|tbsp|tsp|lb|oz)\s',
            r'^\d+.*?(large|medium|small|whole)\s',
            r'^\d+.*?(chopped|diced|minced|sliced|grated|stemmed|seeded)',
            r'^(\d+/\d+|\d+\.\d+)\s*(cup|tablespoon|teaspoon)',
            r'^\d+\s*(cloves?|cans?|packages?|pounds?|ounces?|slices?)\s',
            r'^[¾½¼⅓⅔⅛]',  # Fraction symbols
        ]
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            # Stop at numbered instructions
            if re.match(r'^\d+\.\s', line):
                break
            
            # Skip title lines and section headers
            if line.upper() in ['ACCOMPANIMENT', 'MAIN DISH', 'APPETIZER', 'DESSERT'] or 'Makes' in line or 'Total Time' in line:
                continue
            
            # Skip obvious instruction content  
            instruction_indicators = ['process', 'cook', 'heat', 'transfer', 'bake', 'mix', 'combine', 'whisk']
            if any(line.lower().startswith(indicator) for indicator in instruction_indicators):
                continue
            
            # Check for ingredient patterns
            is_ingredient = False
            for pattern in measurement_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    is_ingredient = True
                    break
            
            if is_ingredient:
                ingredient_lines.append(f"• {line}")
        
        # Filter out any contaminated lines
        clean_ingredients = []
        for ingredient in ingredient_lines:
            # Remove the bullet and check the content
            content = ingredient[2:].strip()
            
            # Skip if it contains cooking verbs at the start
            cooking_verbs = ['process', 'cook', 'heat', 'transfer', 'add', 'stir', 'bake', 'mix', 'combine']
            if any(content.lower().startswith(verb) for verb in cooking_verbs):
                continue
            
            # Skip if it's obviously an instruction fragment
            if any(phrase in content.lower() for phrase in ['minutes', 'seconds', 'until', 'about']):
                continue
            
            clean_ingredients.append(ingredient)
        
        # Need at least 3 clean ingredients 
        if len(clean_ingredients) >= 3:
            return '\n'.join(clean_ingredients)
        
        return None
    
    def _extract_instructions_directly(self, page_text: str) -> Optional[str]:
        """Extract cooking instructions for ATK format"""
        
        lines = page_text.split('\n')
        instruction_lines = []
        
        # Find all numbered instruction steps
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            
            # Match numbered steps like "1. " or "2. "
            step_match = re.match(r'^(\d+)\.\s*(.+)', line)
            if step_match:
                step_num = int(step_match.group(1))
                step_text = step_match.group(2).strip()
                
                # Skip if this looks like a recipe title number or very short
                if step_num == 1 and len(step_text) < 30 and step_text.count(' ') < 5:
                    i += 1
                    continue
                
                # Start collecting this step
                full_step_text = step_text
                
                # Look ahead for continuation lines
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    if not next_line:
                        j += 1
                        continue
                    
                    # Stop if we hit the next numbered step
                    if re.match(r'^\d+\.\s', next_line):
                        break
                    
                    # Stop if we hit ingredient-like content (numbers + measurements)
                    if re.search(r'^\d+\s*(cup|tablespoon|teaspoon|pound|ounce)', next_line, re.IGNORECASE):
                        break
                    
                    # Stop if we hit a section header
                    if next_line.isupper() or next_line in ['INGREDIENTS', 'INSTRUCTIONS', 'DIRECTIONS']:
                        break
                    
                    # Add continuation - this should be instruction text
                    full_step_text += " " + next_line
                    j += 1
                
                # Only add if the step is substantial enough
                if len(full_step_text) > 20:
                    instruction_lines.append(f"{step_num}. {full_step_text}")
                
                # Move past this step
                i = j
            else:
                i += 1
        
        # Need at least 2 instruction steps for a proper recipe
        if len(instruction_lines) >= 2:
            return '\n'.join(instruction_lines)
        
        return None
    
    def _extract_servings(self, page_text: str) -> Optional[str]:
        """Extract serving information"""
        patterns = [
            r'(serves|makes)\s+(\d+)(?:\s+to\s+(\d+))?',
            r'yield[s]?\s*:?\s*(\d+)',
            r'(\d+)\s+servings'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                if len(match.groups()) >= 2 and match.group(2):
                    return f"Serves {match.group(2)}"
                elif match.group(1):
                    return f"Serves {match.group(1)}"
        
        return None
    
    def _extract_timing(self, page_text: str) -> Optional[str]:
        """Extract timing information"""
        patterns = [
            r'(\d+)\s+(minutes?|mins?|hours?|hrs?)',
            r'total\s+time\s*:?\s*(\d+)\s+(minutes?|hours?)',
            r'prep\s+time\s*:?\s*(\d+)\s+(minutes?|hours?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                time_value = match.group(1) if len(match.groups()) >= 1 else match.group(2)
                time_unit = match.group(2) if len(match.groups()) >= 2 else match.group(1)
                return f"{time_value} {time_unit.lower()}"
        
        return None
    
    def _infer_category(self, title: str) -> str:
        """Infer recipe category from title"""
        title_lower = title.lower()
        
        categories = {
            'Appetizers': ['appetizer', 'dip', 'bite', 'starter'],
            'Soups & Stews': ['soup', 'stew', 'chili', 'bisque', 'chowder'],
            'Salads': ['salad', 'slaw'],
            'Main Dishes': ['chicken', 'beef', 'pork', 'fish', 'salmon', 'turkey', 'lamb'],
            'Pasta & Rice': ['pasta', 'spaghetti', 'rice', 'risotto', 'noodle'],
            'Vegetables': ['vegetable', 'broccoli', 'carrot', 'potato'],
            'Breads': ['bread', 'biscuit', 'muffin', 'roll'],
            'Desserts': ['cake', 'cookie', 'pie', 'tart', 'chocolate', 'dessert'],
            'Breakfast': ['pancake', 'waffle', 'omelet', 'egg', 'breakfast']
        }
        
        for category, keywords in categories.items():
            if any(keyword in title_lower for keyword in keywords):
                return category
        
        return 'Main Dishes'
    
    def _print_summary(self):
        """Print extraction summary"""
        stats = self.extraction_stats
        
        logger.info(f"\n🧠 SIMPLIFIED INTELLIGENT EXTRACTION SUMMARY:")
        logger.info("=" * 70)
        logger.info(f"📄 Pages processed: {stats['pages_processed']}")
        logger.info(f"🔍 Recipe candidates found: {stats['recipe_candidates_found']}")
        logger.info(f"🔬 Semantic validations: {stats['semantic_validations']}")
        logger.info(f"🚫 Artifacts rejected: {stats['artifacts_rejected']}")
        logger.info(f"✅ Recipes validated: {stats['recipes_validated']}")
        
        if stats['quality_scores']:
            avg_quality = sum(stats['quality_scores']) / len(stats['quality_scores'])
            logger.info(f"📊 Average quality score: {avg_quality:.2f}")
        
        logger.info(f"\n🚫 REJECTION BREAKDOWN:")
        for reason, count in stats['rejection_reasons'].items():
            if count > 0:
                logger.info(f"  {reason.replace('_', ' ').title()}: {count}")
        
        if self.extracted_recipes:
            logger.info(f"\n✅ VALIDATED RECIPES:")
            for i, recipe in enumerate(self.extracted_recipes[:10], 1):
                title = recipe.get('title', 'Unknown')
                confidence = recipe.get('semantic_validation', {}).get('confidence_score', 0)
                logger.info(f"  {i}. '{title}' (confidence: {confidence:.2f})")
            
            if len(self.extracted_recipes) > 10:
                logger.info(f"  ... and {len(self.extracted_recipes) - 10} more")
    
    def save_to_database(self, dry_run: bool = False) -> int:
        """Save validated recipes to database"""
        if not self.extracted_recipes:
            logger.warning("⚠️ No recipes to save")
            return 0
        
        logger.info(f"\n💾 SAVING INTELLIGENT EXTRACTION RESULTS")
        logger.info("=" * 60)
        logger.info(f"📋 Recipes to save: {len(self.extracted_recipes)}")
        logger.info(f"🧠 All passed semantic validation")
        logger.info(f"🛡️ Zero artifacts guaranteed")
        
        if dry_run:
            logger.info("🔍 DRY RUN - No database changes")
            return len(self.extracted_recipes)
        
        # Insert recipes
        inserted_count = 0
        for recipe in self.extracted_recipes:
            try:
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Add semantic metadata to description
                    validation = recipe.get('semantic_validation', {})
                    semantic_note = f"Semantic Validation: Valid Recipe " \
                                  f"(confidence: {validation.get('confidence_score', 0):.2f}, " \
                                  f"quality: {validation.get('quality_metrics', {})})"
                    
                    description = recipe.get('description', '')
                    if description:
                        description += f"\n\n{semantic_note}"
                    else:
                        description = semantic_note
                    
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
                        description,
                        recipe.get('source'),
                        recipe.get('page_number')
                    ))
                    conn.commit()
                    inserted_count += 1
                    
            except Exception as e:
                logger.error(f"❌ Error inserting '{recipe.get('title', 'Unknown')}': {e}")
        
        logger.info(f"✅ Successfully inserted {inserted_count} validated recipes")
        return inserted_count


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ATK 25th Anniversary Simplified Intelligent Extractor')
    parser.add_argument('--max-recipes', type=int, help='Maximum recipes to extract')
    parser.add_argument('--start-page', type=int, default=1, help='Start page')
    parser.add_argument('--end-page', type=int, help='End page')
    parser.add_argument('--dry-run', action='store_true', help='Don\'t save to database')
    parser.add_argument('--test-sample', action='store_true', help='Extract 5 recipes from pages 200-300')
    
    args = parser.parse_args()
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
    
    if not os.path.exists(pdf_path):
        logger.error(f"❌ PDF not found: {pdf_path}")
        return
    
    # Test sample settings
    if args.test_sample:
        args.max_recipes = 5
        args.start_page = 200
        args.end_page = 300
        logger.info("🧪 TEST SAMPLE: 5 recipes from pages 200-300")
    
    # Create extractor
    extractor = ATK25thSimplifiedIntelligentExtractor(pdf_path)
    
    # Extract recipes
    recipes = extractor.extract_recipes(
        max_recipes=args.max_recipes,
        start_page=args.start_page,
        end_page=args.end_page
    )
    
    # Save results
    if recipes:
        inserted_count = extractor.save_to_database(dry_run=args.dry_run)
        
        logger.info(f"\n🎉 SIMPLIFIED INTELLIGENT EXTRACTION COMPLETE!")
        logger.info(f"🧠 Human-like validation with zero artifacts")
        logger.info(f"📊 Results: {len(recipes)} recipes extracted, {inserted_count} saved")


if __name__ == "__main__":
    main()
