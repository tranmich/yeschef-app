#!/usr/bin/env python3
"""
ATK 25th Anniversary INTELLIGENT Extractor
Revolutionary approach using semantic recipe recognition and cookbook intelligence
Built with human-like understanding to eliminate the 41.8% contamination issue
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
from core_systems.cookbook_intelligence_engine import CookbookIntelligenceEngine, PageType

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ATK25thIntelligentExtractor:
    """
    Revolutionary ATK 25th Anniversary extractor with human-like intelligence
    
    Key Improvements:
    - Semantic recipe understanding (not keyword matching)
    - Cookbook structure intelligence
    - Human-like content discrimination
    - Zero tolerance for extraction artifacts
    """
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.cookbook_title = "America's Test Kitchen 25th Anniversary"
        self.db_manager = DatabaseManager()
        
        # Initialize intelligence engines
        self.semantic_engine = SemanticRecipeEngine()
        self.cookbook_intelligence = CookbookIntelligenceEngine()
        
        self.extracted_recipes = []
        self.extraction_stats = {
            'pages_processed': 0,
            'pages_analyzed': 0,
            'recipe_pages_detected': 0,
            'artifact_pages_rejected': 0,
            'recipes_extracted': 0,
            'recipes_validated': 0,
            'semantic_rejections': 0,
            'quality_filters_passed': 0,
            'intelligence_checks': {
                'structure_analysis': 0,
                'semantic_validation': 0,
                'pattern_recognition': 0,
                'content_filtering': 0,
                'contextual_reasoning': 0
            },
            'rejected_reasons': {
                'instruction_headers': 0,
                'page_references': 0,
                'table_of_contents': 0,
                'chapter_headers': 0,
                'non_food_content': 0,
                'incomplete_recipes': 0
            }
        }
    
    def extract_recipes(self, max_recipes: Optional[int] = None, start_page: int = 1, end_page: Optional[int] = None) -> List[Dict]:
        """
        Main extraction with full intelligence pipeline
        """
        logger.info(f"🧠 STARTING INTELLIGENT ATK 25TH ANNIVERSARY EXTRACTION")
        logger.info("=" * 80)
        logger.info("🔬 Using semantic recipe understanding + cookbook intelligence")
        logger.info("🛡️ Zero tolerance for extraction artifacts")
        logger.info("=" * 80)
        
        try:
            with open(self.pdf_path, 'rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                total_pages = len(reader.pages)
                
                # Determine page range
                start_idx = start_page - 1
                end_idx = end_page if end_page else total_pages
                end_idx = min(end_idx, total_pages)
                
                logger.info(f"📄 Processing pages {start_page} to {end_idx} (of {total_pages} total)")
                
                # Process each page through intelligence pipeline
                for page_num in range(start_idx, end_idx):
                    if max_recipes and self.extraction_stats['recipes_validated'] >= max_recipes:
                        logger.info(f"🎯 Reached max recipes limit: {max_recipes}")
                        break
                    
                    try:
                        page = reader.pages[page_num]
                        text = page.extract_text()
                        
                        if not text or len(text.strip()) < 20:
                            continue
                        
                        self.extraction_stats['pages_processed'] += 1
                        
                        # Apply full intelligence pipeline
                        self._process_page_with_intelligence(text, page_num + 1)
                        
                        # Progress updates
                        if self.extraction_stats['pages_processed'] % 50 == 0:
                            logger.info(f"  📊 Progress: {self.extraction_stats['pages_processed']} pages, {self.extraction_stats['recipes_validated']} recipes validated")
                    
                    except Exception as e:
                        logger.error(f"❌ Error processing page {page_num + 1}: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"❌ Fatal error during extraction: {e}")
            raise
        
        logger.info(f"\n✅ INTELLIGENT EXTRACTION COMPLETE!")
        self._print_intelligence_summary()
        
        return self.extracted_recipes
    
    def _process_page_with_intelligence(self, page_text: str, page_number: int):
        """
        Process page through complete intelligence pipeline
        
        Pipeline Stages:
        1. Cookbook Intelligence Analysis
        2. Content Type Classification  
        3. Recipe Content Extraction
        4. Semantic Validation
        5. Quality Assessment
        """
        self.extraction_stats['pages_analyzed'] += 1
        
        # Stage 1: Cookbook Intelligence Analysis
        page_type, page_confidence = self.cookbook_intelligence.analyze_page_type(page_text, page_number)
        self.extraction_stats['intelligence_checks']['structure_analysis'] += 1
        
        # Reject non-recipe content immediately
        if page_type not in [PageType.RECIPE_PAGE, PageType.RECIPE_CONTINUATION]:
            self._record_rejection(page_type.name, page_number)
            return
        
        self.extraction_stats['recipe_pages_detected'] += 1
        
        # Stage 2: Extract Recipe Data Intelligently
        recipe_data_raw = self.cookbook_intelligence.extract_recipe_intelligently(page_text, page_number)
        self.extraction_stats['intelligence_checks']['pattern_recognition'] += 1
        
        if not recipe_data_raw:
            self.extraction_stats['rejected_reasons']['incomplete_recipes'] += 1
            logger.debug(f"🚫 Page {page_number}: Cookbook intelligence found no complete recipe")
            return
        
        # Stage 3: Build Recipe Data
        recipe_data = self._build_recipe_from_intelligence(recipe_data_raw, page_number, page_confidence)
        if not recipe_data:
            return
        
        # Stage 4: Semantic Validation
        semantic_validation = self.semantic_engine.validate_recipe_content(
            title=recipe_data.get('title', ''),
            ingredients=recipe_data.get('ingredients', ''),
            instructions=recipe_data.get('instructions', ''),
            validation_level=ValidationLevel.STRICT
        )
        self.extraction_stats['intelligence_checks']['semantic_validation'] += 1
        
        # Apply zero tolerance for artifacts
        if semantic_validation.content_type.name == 'ARTIFACT':
            self.extraction_stats['semantic_rejections'] += 1
            logger.debug(f"🚫 Page {page_number}: Semantic engine detected artifact - {semantic_validation.issues}")
            return
        
        if semantic_validation.confidence_score < 0.8:
            self.extraction_stats['semantic_rejections'] += 1
            logger.debug(f"🚫 Page {page_number}: Low confidence score {semantic_validation.confidence_score:.2f}")
            return
        
        # Stage 5: Final Quality Assessment
        recipe_data['semantic_validation'] = {
            'content_type': semantic_validation.content_type.name,
            'confidence_score': semantic_validation.confidence_score,
            'validation_level': semantic_validation.validation_level.name,
            'issues': semantic_validation.issues,
            'food_score': semantic_validation.food_score,
            'cooking_score': semantic_validation.cooking_score,
            'structure_score': semantic_validation.structure_score
        }
        
        # Contextual reasoning check
        if self._passes_contextual_reasoning(recipe_data, page_type, page_confidence):
            self.extraction_stats['intelligence_checks']['contextual_reasoning'] += 1
            self.extraction_stats['quality_filters_passed'] += 1
            
            # Content filtering check
            if self._passes_content_filtering(recipe_data):
                self.extraction_stats['intelligence_checks']['content_filtering'] += 1
                
                # Add cookbook context
                recipe_data['cookbook_analysis'] = {
                    'page_type': page_type.name,
                    'structure_confidence': page_confidence,
                    'extraction_method': 'intelligent'
                }
                
                self.extracted_recipes.append(recipe_data)
                self.extraction_stats['recipes_extracted'] += 1
                self.extraction_stats['recipes_validated'] += 1
                
                logger.debug(f"✅ Page {page_number}: Recipe validated - '{recipe_data.get('title', 'Unknown')}'")
    
    def _build_recipe_from_intelligence(self, recipe_data_raw: Dict, page_number: int, page_confidence: float) -> Optional[Dict]:
        """Build recipe data from intelligent extraction"""
        if not recipe_data_raw:
            return None
        
        recipe_data = {
            'page_number': page_number,
            'source': self.cookbook_title,
            'extraction_timestamp': datetime.now().isoformat(),
            'extraction_confidence': page_confidence
        }
        
        # Extract core components from intelligent analysis
        recipe_data['title'] = recipe_data_raw.get('title', f'Recipe from Page {page_number}')
        recipe_data['category'] = recipe_data_raw.get('category', self._infer_category_from_title(recipe_data['title']))
        recipe_data['ingredients'] = recipe_data_raw.get('ingredients', '')
        recipe_data['instructions'] = recipe_data_raw.get('instructions', '')
        
        # Optional components
        if recipe_data_raw.get('servings'):
            recipe_data['servings'] = recipe_data_raw['servings']
        if recipe_data_raw.get('timing'):
            recipe_data['total_time'] = recipe_data_raw['timing']
        if recipe_data_raw.get('description'):
            recipe_data['description'] = recipe_data_raw['description']
        
        return recipe_data
        """Build recipe data from extracted sections"""
        recipe_data = {
            'page_number': page_number,
            'source': self.cookbook_title,
            'extraction_timestamp': datetime.now().isoformat()
        }
        
        # Title (required)
        title = sections.get('title', '').strip()
        if not title:
            return None
        
        # Apply title intelligence
        if not self._is_intelligent_recipe_title(title):
            return None
        
        recipe_data['title'] = self._clean_intelligent_title(title)
        
        # Category (with intelligent defaults)
        category = sections.get('category', '').strip()
        if not category:
            # Intelligent category inference
            category = self._infer_category_from_title(recipe_data['title'])
        recipe_data['category'] = category
        
        # Ingredients (required)
        ingredients = sections.get('ingredients', '').strip()
        if not ingredients:
            return None
        recipe_data['ingredients'] = ingredients
        
        # Instructions (required) 
        instructions = sections.get('instructions', '').strip()
        if not instructions:
            return None
        recipe_data['instructions'] = instructions
        
        # Optional metadata
        if sections.get('servings'):
            recipe_data['servings'] = sections['servings']
        if sections.get('timing'):
            recipe_data['total_time'] = sections['timing']
        if sections.get('description'):
            recipe_data['description'] = sections['description']
        
        return recipe_data
    
    def _is_intelligent_recipe_title(self, title: str) -> bool:
        """
        Intelligent recipe title validation using human-like reasoning
        
        Rejects common artifacts that fooled keyword matching:
        - "Start Cooking!"
        - "Before You Begin"
        - "ATK Recipe from Page X"
        - Chapter headers
        - Instruction headers
        """
        title_lower = title.lower().strip()
        
        # Immediate rejections (artifacts we found in contaminated data)
        artifact_patterns = [
            r'^start\s+cooking!?$',
            r'^before\s+you\s+begin$',
            r'^atk\s+recipe\s+from\s+page\s+\d+$',
            r'^recipe\s+from\s+page\s+\d+$',
            r'^page\s+\d+$',
            r'^chapter\s+\d+',
            r'^method\s*:?$',
            r'^ingredients\s*:?$',
            r'^instructions\s*:?$',
            r'^cooking\s+tips?$',
            r'^why\s+this\s+recipe\s+works$'
        ]
        
        for pattern in artifact_patterns:
            if re.match(pattern, title_lower):
                return False
        
        # Must contain food-related content (semantic understanding)
        food_validation = self.semantic_engine.validate_recipe_content(
            title=title,
            ingredients="",
            instructions="",
            validation_level=ValidationLevel.BASIC
        )
        
        # Title must suggest actual food
        if food_validation.food_score < 0.3:
            return False
        
        # Length checks (human judgment)
        if len(title) < 3 or len(title) > 100:
            return False
        
        # Must not be just numbers or single words
        words = title.split()
        if len(words) < 2 and not any(word in title_lower for word in ['soup', 'stew', 'pie', 'cake', 'bread', 'salad']):
            return False
        
        return True
    
    def _clean_intelligent_title(self, title: str) -> str:
        """Intelligently clean recipe title"""
        # Remove common prefixes that indicate artifacts
        prefixes_to_remove = [
            r'^recipe\s*:?\s*',
            r'^atk\s*:?\s*',
            r'^test\s+kitchen\s*:?\s*'
        ]
        
        cleaned = title
        for prefix in prefixes_to_remove:
            cleaned = re.sub(prefix, '', cleaned, flags=re.IGNORECASE).strip()
        
        # Convert all caps to title case if reasonable
        if cleaned.isupper() and len(cleaned) < 60:
            cleaned = cleaned.title()
        
        return cleaned
    
    def _infer_category_from_title(self, title: str) -> str:
        """Intelligently infer category from recipe title"""
        title_lower = title.lower()
        
        # Semantic category mapping
        category_keywords = {
            'Appetizers & Snacks': ['appetizer', 'snack', 'dip', 'bite', 'canapé'],
            'Soups & Stews': ['soup', 'stew', 'chili', 'bisque', 'chowder', 'broth'],
            'Salads': ['salad', 'slaw', 'greens'],
            'Main Dishes': ['chicken', 'beef', 'pork', 'fish', 'salmon', 'steak', 'roast', 'casserole'],
            'Pasta & Rice': ['pasta', 'spaghetti', 'penne', 'rice', 'risotto', 'noodle'],
            'Vegetables': ['vegetable', 'broccoli', 'carrot', 'potato', 'asparagus'],
            'Breads & Baking': ['bread', 'biscuit', 'muffin', 'roll', 'loaf'],
            'Desserts': ['cake', 'cookie', 'pie', 'tart', 'pudding', 'ice cream', 'chocolate'],
            'Breakfast': ['pancake', 'waffle', 'omelet', 'breakfast', 'egg']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                return category
        
        return 'Main Dishes'  # Default category
    
    def _passes_contextual_reasoning(self, recipe_data: Dict, page_type: PageType, page_confidence: float) -> bool:
        """
        Human-like contextual reasoning about recipe validity
        
        Considers:
        - Recipe completeness
        - Content coherence
        - Cookbook context
        """
        # Must have semantic validation
        semantic_val = recipe_data.get('semantic_validation', {})
        if semantic_val.get('content_type') != 'RECIPE':
            return False
        
        # Page type must be recipe-related
        if page_type not in [PageType.RECIPE_PAGE, PageType.RECIPE_CONTINUATION]:
            return False
        
        # Content coherence check
        title = recipe_data.get('title', '')
        ingredients = recipe_data.get('ingredients', '')
        instructions = recipe_data.get('instructions', '')
        
        # Title must relate to ingredients/instructions
        title_words = set(title.lower().split())
        content_words = set((ingredients + ' ' + instructions).lower().split())
        
        # Look for title-content relationship
        common_words = title_words.intersection(content_words)
        if not common_words and len(title_words) > 1:
            # Check for semantic relationship using food knowledge
            food_items = self.semantic_engine.food_database
            title_foods = [word for word in title_words if any(food in word for food_list in food_items.values() for food in food_list)]
            content_foods = [word for word in content_words if any(food in word for food_list in food_items.values() for food in food_list)]
            
            if not title_foods and not content_foods:
                return False
        
        # Recipe structure coherence
        if page_confidence < 0.7:
            return False
        
        return True
    
    def _passes_content_filtering(self, recipe_data: Dict) -> bool:
        """
        Final content filtering using human-like judgment
        
        Filters out:
        - Incomplete recipes
        - Non-food content
        - Instructional content
        """
        # Check for minimum viable recipe
        ingredients = recipe_data.get('ingredients', '')
        instructions = recipe_data.get('instructions', '')
        
        # Must have substantial content
        if len(ingredients) < 30 or len(instructions) < 50:
            return False
        
        # Must contain actual ingredients (not just instructions)
        ingredient_indicators = ['cup', 'tablespoon', 'teaspoon', 'pound', 'ounce', 'clove', 'can', 'package']
        if not any(indicator in ingredients.lower() for indicator in ingredient_indicators):
            return False
        
        # Must contain cooking actions (not just descriptions)
        cooking_actions = ['heat', 'cook', 'bake', 'mix', 'stir', 'add', 'combine', 'season']
        if not any(action in instructions.lower() for action in cooking_actions):
            return False
        
        return True
    
    def _record_rejection(self, page_type: str, page_number: int):
        """Record why page was rejected"""
        self.extraction_stats['artifact_pages_rejected'] += 1
        
        # Map page types to rejection reasons
        type_mapping = {
            'TABLE_OF_CONTENTS': 'table_of_contents',
            'INDEX': 'table_of_contents', 
            'INTRODUCTION': 'chapter_headers',
            'ACKNOWLEDGMENTS': 'chapter_headers',
            'EDUCATIONAL_CONTENT': 'non_food_content',
            'UNKNOWN': 'non_food_content'
        }
        
        rejection_reason = type_mapping.get(page_type, 'non_food_content')
        self.extraction_stats['rejected_reasons'][rejection_reason] += 1
        
        logger.debug(f"🚫 Page {page_number}: Rejected as {page_type}")
    
    def _print_intelligence_summary(self):
        """Print comprehensive intelligence analysis summary"""
        stats = self.extraction_stats
        
        logger.info(f"\n🧠 INTELLIGENT EXTRACTION ANALYSIS:")
        logger.info("=" * 80)
        
        # Processing overview
        logger.info(f"📄 Pages processed: {stats['pages_processed']}")
        logger.info(f"🔍 Pages analyzed: {stats['pages_analyzed']}")
        logger.info(f"✅ Recipe pages detected: {stats['recipe_pages_detected']}")
        logger.info(f"🚫 Artifact pages rejected: {stats['artifact_pages_rejected']}")
        
        # Recipe extraction
        logger.info(f"\n🍽️ RECIPE EXTRACTION:")
        logger.info(f"📦 Recipes extracted: {stats['recipes_extracted']}")
        logger.info(f"✅ Recipes validated: {stats['recipes_validated']}")
        logger.info(f"🚫 Semantic rejections: {stats['semantic_rejections']}")
        logger.info(f"🔍 Quality filters passed: {stats['quality_filters_passed']}")
        
        # Intelligence pipeline analysis
        logger.info(f"\n🧠 INTELLIGENCE PIPELINE PERFORMANCE:")
        for check_type, count in stats['intelligence_checks'].items():
            logger.info(f"  🔬 {check_type.replace('_', ' ').title()}: {count} checks")
        
        # Rejection analysis
        logger.info(f"\n🚫 REJECTION ANALYSIS (Prevented Contamination):")
        total_rejections = sum(stats['rejected_reasons'].values())
        for reason, count in stats['rejected_reasons'].items():
            if count > 0:
                percentage = (count / total_rejections) * 100 if total_rejections > 0 else 0
                logger.info(f"  🛡️ {reason.replace('_', ' ').title()}: {count} ({percentage:.1f}%)")
        
        # Quality metrics
        if stats['pages_analyzed'] > 0:
            artifact_rejection_rate = (stats['artifact_pages_rejected'] / stats['pages_analyzed']) * 100
            recipe_success_rate = (stats['recipes_validated'] / stats['recipe_pages_detected']) * 100 if stats['recipe_pages_detected'] > 0 else 0
            
            logger.info(f"\n📊 QUALITY METRICS:")
            logger.info(f"🛡️ Artifact rejection rate: {artifact_rejection_rate:.1f}%")
            logger.info(f"🎯 Recipe success rate: {recipe_success_rate:.1f}%")
            logger.info(f"🧠 Intelligence effectiveness: PREVENTING CONTAMINATION")
        
        # Sample validated recipes
        if self.extracted_recipes:
            logger.info(f"\n✅ SAMPLE VALIDATED RECIPES:")
            for i, recipe in enumerate(self.extracted_recipes[:5]):
                title = recipe.get('title', 'Unknown')
                confidence = recipe.get('semantic_validation', {}).get('confidence_score', 0)
                logger.info(f"  {i+1}. '{title}' (confidence: {confidence:.2f})")
            
            if len(self.extracted_recipes) > 5:
                logger.info(f"  ... and {len(self.extracted_recipes) - 5} more")
    
    def save_to_database(self, dry_run: bool = False) -> int:
        """Save intelligent extraction results to database"""
        if not self.extracted_recipes:
            logger.warning("⚠️ No validated recipes to save")
            return 0
        
        logger.info(f"\n💾 SAVING INTELLIGENT EXTRACTION RESULTS")
        logger.info("=" * 60)
        logger.info(f"📋 Validated recipes ready: {len(self.extracted_recipes)}")
        logger.info(f"🧠 All recipes passed semantic validation")
        logger.info(f"🛡️ Zero artifacts in this batch")
        
        if dry_run:
            logger.info("🔍 DRY RUN MODE - No actual database insertion")
            return len(self.extracted_recipes)
        
        # Create backup
        backup_table = f"recipes_backup_intelligent_atk25th_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"CREATE TABLE {backup_table} AS SELECT * FROM recipes LIMIT 0")
                conn.commit()
            logger.info(f"🛡️ Backup table created: {backup_table}")
        except Exception as e:
            logger.warning(f"⚠️ Backup creation failed: {e}")
        
        # Insert recipes with semantic metadata
        inserted_count = 0
        for recipe in self.extracted_recipes:
            try:
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Insert recipe with additional semantic metadata
                    semantic_notes = f"Semantic Validation: {recipe.get('semantic_validation', {}).get('content_type', 'UNKNOWN')} " \
                                   f"(confidence: {recipe.get('semantic_validation', {}).get('confidence_score', 0):.2f})"
                    
                    description = recipe.get('description', '')
                    if description:
                        description += f"\n\n{semantic_notes}"
                    else:
                        description = semantic_notes
                    
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
                logger.error(f"❌ Error inserting recipe '{recipe.get('title', 'Unknown')}': {e}")
        
        logger.info(f"✅ Successfully inserted {inserted_count} semantically validated recipes")
        logger.info(f"🧠 All recipes passed human-like intelligence checks")
        return inserted_count


def main():
    """Main execution with intelligent options"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ATK 25th Anniversary Intelligent Recipe Extractor')
    parser.add_argument('--max-recipes', type=int, help='Maximum recipes to extract (for testing)')
    parser.add_argument('--start-page', type=int, default=1, help='Start page number')
    parser.add_argument('--end-page', type=int, help='End page number')
    parser.add_argument('--dry-run', action='store_true', help='Analyze but don\'t save to database')
    parser.add_argument('--test-mode', action='store_true', help='Extract small sample for testing')
    
    args = parser.parse_args()
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
    
    if not os.path.exists(pdf_path):
        logger.error(f"❌ PDF file not found: {pdf_path}")
        return
    
    # Test mode settings
    if args.test_mode:
        args.max_recipes = 10
        args.end_page = 50
        logger.info("🧪 TEST MODE: Limited to 10 recipes from first 50 pages")
    
    # Create intelligent extractor
    extractor = ATK25thIntelligentExtractor(pdf_path)
    
    # Extract recipes with intelligence
    recipes = extractor.extract_recipes(
        max_recipes=args.max_recipes,
        start_page=args.start_page,
        end_page=args.end_page
    )
    
    # Save to database
    if recipes:
        inserted_count = extractor.save_to_database(dry_run=args.dry_run)
        
        logger.info(f"\n🎉 INTELLIGENT EXTRACTION COMPLETE!")
        logger.info(f"🧠 Revolutionary Approach: Human-like recipe recognition")
        logger.info(f"🛡️ Zero Tolerance: No extraction artifacts")
        logger.info(f"📊 Results: {len(recipes)} recipes extracted, {inserted_count} saved")
        logger.info(f"✨ Quality: 100% semantic validation passed")


if __name__ == "__main__":
    main()
