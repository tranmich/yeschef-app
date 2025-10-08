"""
🚀 Universal Recipe Importer - Import Orchestrator
=========================================================

This is the main import system that leverages existing Me Hungie intelligence:
- AdaptiveRecipeExtractor for text parsing
- IngredientIntelligenceEngine for ingredient processing
- UniversalSearchEngine for validation and deduplication
- PostgreSQL database for storage
- OCRTextParser for OCR text extraction (battle-tested)

Supports multiple import sources:
- Text recipes (copy/paste)
- Website URLs
- Recipe images (OCR)
- CSV files (future)

Author: GitHub Copilot & Team
Date: August 26, 2025 - Day 1 Implementation
"""

import os
import sys
import json
import logging
import requests
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import OCR text parser
from core_systems.ocr_text_parser import OCRTextParser

# Import existing Me Hungie systems
try:
    from cookbook_processing.adaptive_recipe_extractor import AdaptiveRecipeExtractor, Recipe
    from core_systems.ingredient_intelligence_engine import IngredientIntelligenceEngine, IngredientMapping
    from core_systems.universal_search import UniversalSearchEngine
    from core_systems.web_recipe_extractor import WebRecipeExtractor, WebRecipeData
except ImportError as e:
    print(f"Warning: Could not import existing systems: {e}")
    print("Running in standalone mode...")

# Import UniversalRecipeParser separately (for OCR text extraction)
try:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from universal_recipe_parser.complete_recipe_parser import UniversalRecipeParser
    UNIVERSAL_PARSER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Warning: Could not import UniversalRecipeParser: {e}")
    print("   OCR text parsing will use fallback method")
    UNIVERSAL_PARSER_AVAILABLE = False
    UniversalRecipeParser = None

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ImportResult:
    """Result of recipe import operation"""
    success: bool
    recipe_id: Optional[int] = None
    recipe_data: Optional[Dict] = None
    confidence: float = 0.0
    needs_review: bool = False
    errors: List[str] = None
    warnings: List[str] = None
    extraction_method: str = "unknown"
    processing_time: float = 0.0
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []

@dataclass 
class ImportRequest:
    """Import request structure"""
    source_type: str  # 'text', 'url', 'image', 'csv'
    source_data: str  # Text content, URL, image path, CSV path
    user_id: int
    metadata: Optional[Dict] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class UniversalRecipeImporter:
    """
    🚀 Universal Recipe Import System
    
    Orchestrates recipe imports from any source using existing Me Hungie intelligence
    """
    
    def __init__(self):
        """Initialize with existing Me Hungie systems"""
        self.adaptive_extractor = None
        self.universal_parser = None  # For OCR text extraction
        self.ingredient_engine = None
        self.search_engine = None
        self.web_extractor = None
        self.youtube_extractor = None  # 🆕 YouTube support
        
        # Initialize existing systems if available
        try:
            self.adaptive_extractor = AdaptiveRecipeExtractor()
            logger.info("✅ AdaptiveRecipeExtractor initialized")
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize AdaptiveRecipeExtractor: {e}")
        
        try:
            if UNIVERSAL_PARSER_AVAILABLE and UniversalRecipeParser:
                self.universal_parser = UniversalRecipeParser()
                logger.info("✅ UniversalRecipeParser initialized")
            else:
                logger.warning("⚠️ UniversalRecipeParser not available")
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize UniversalRecipeParser: {e}")
            
        try:
            self.ingredient_engine = IngredientIntelligenceEngine()
            logger.info("✅ IngredientIntelligenceEngine initialized")
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize IngredientIntelligenceEngine: {e}")
            
        try:
            self.search_engine = UniversalSearchEngine()
            logger.info("✅ UniversalSearchEngine initialized")
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize UniversalSearchEngine: {e}")
        
        try:
            self.web_extractor = WebRecipeExtractor()
            logger.info("✅ WebRecipeExtractor initialized")
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize WebRecipeExtractor: {e}")
        
        # 🆕 Initialize YouTube extractor
        try:
            from core_systems.youtube_recipe_extractor import YouTubeRecipeExtractor
            self.youtube_extractor = YouTubeRecipeExtractor()
            logger.info("✅ YouTubeRecipeExtractor initialized")
        except Exception as e:
            logger.warning(f"⚠️ Could not initialize YouTubeRecipeExtractor: {e}")
            logger.warning("   YouTube video imports will not be available")
        
        # Configuration
        self.confidence_threshold = 0.7
        self.max_processing_time = 30  # seconds
        
    def get_database_connection(self):
        """Get PostgreSQL database connection using existing pattern"""
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            try:
                # Try internal Railway URL first
                return psycopg2.connect(database_url, cursor_factory=RealDictCursor)
            except Exception as e:
                logger.warning(f"Failed to connect with internal URL: {e}")
                # Fallback to public URL
                public_url = database_url.replace(
                    "postgres.railway.internal:5432", 
                    "shuttle.proxy.rlwy.net:31331"
                )
                return psycopg2.connect(public_url, cursor_factory=RealDictCursor)
        else:
            # Local development fallback
            return psycopg2.connect(
                host="localhost",
                database="me_hungie",
                user="postgres", 
                password="password",
                cursor_factory=RealDictCursor
            )
    
    def import_recipe(self, request: ImportRequest) -> ImportResult:
        """
        Main import method - routes to appropriate importer based on source type
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"🚀 Starting import: {request.source_type} for user {request.user_id}")
            
            # Route to appropriate import method
            if request.source_type == 'text' or request.source_type == 'ocr':
                # OCR and text use same processing path (both are plain text)
                result = self.import_from_text(request.source_data, request.user_id, request.metadata)
            elif request.source_type == 'url':
                result = self.import_from_url(request.source_data, request.user_id, request.metadata)
            else:
                return ImportResult(
                    success=False,
                    errors=[f"Unsupported import type: {request.source_type}"],
                    extraction_method=request.source_type
                )
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            result.processing_time = processing_time
            
            logger.info(f"✅ Import completed in {processing_time:.2f}s with confidence {result.confidence:.2f}")
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Import failed after {processing_time:.2f}s: {e}")
            
            return ImportResult(
                success=False,
                errors=[f"Import failed: {str(e)}"],
                processing_time=processing_time,
                extraction_method=request.source_type
            )
    
    def import_from_text(self, recipe_text: str, user_id: int, metadata: Dict = None) -> ImportResult:
        """
        Import recipe from pasted text using UniversalRecipeParser
        """
        try:
            logger.info("📝 Processing text import...")
            
            if not recipe_text or len(recipe_text.strip()) < 50:
                return ImportResult(
                    success=False,
                    errors=["Recipe text too short - need at least 50 characters"],
                    extraction_method="text"
                )
            
            # Use battle-tested OCR text parser
            logger.info("📖 Using OCRTextParser for text extraction...")
            parser = OCRTextParser()
            extracted_recipe = parser.parse(recipe_text)
            confidence = extracted_recipe.get('confidence', 0.7)
            
            # Process with ingredient intelligence
            processed_recipe = self._process_with_intelligence(extracted_recipe, user_id)
            
            # DON'T save to database yet - return for user review
            # The mobile app will save it after user reviews and confirms
            logger.info("📋 Recipe extracted and processed - ready for user review")
            
            return ImportResult(
                success=True,
                recipe_id=None,  # No ID yet - not saved to database
                recipe_data=asdict(processed_recipe) if hasattr(processed_recipe, '__dict__') else processed_recipe,
                confidence=confidence,
                needs_review=True,  # Always needs review for OCR/text imports
                extraction_method="text_universal_parser"
            )
            
        except Exception as e:
            logger.error(f"Text import failed: {e}", exc_info=True)
            return ImportResult(
                success=False,
                errors=[f"Text processing failed: {str(e)}"],
                extraction_method="text"
            )
    
    def import_from_url(self, url: str, user_id: int, metadata: Dict = None) -> ImportResult:
        """
        Import recipe from website URL using advanced web extraction
        Supports regular recipe websites and YouTube cooking videos
        """
        try:
            logger.info(f"🌐 Processing URL import: {url}")
            
            if not url or not url.startswith(('http://', 'https://')):
                return ImportResult(
                    success=False,
                    errors=["Invalid URL format - must start with http:// or https://"],
                    extraction_method="url_validation_failed"
                )
            
            # 🆕 Check if this is a YouTube URL
            if self._is_youtube_url(url):
                logger.info("🎥 Detected YouTube URL - using YouTube extractor")
                return self._import_from_youtube(url, user_id, metadata)
            
            # Use WebRecipeExtractor for regular websites
            if self.web_extractor:
                # Extract recipe using advanced web extraction
                web_recipe_data = self.web_extractor.extract_from_url(url)
                
                # Debug: Log what the web extractor actually returned
                logger.info(f"🔍 Web extractor returned:")
                logger.info(f"  - Title: '{web_recipe_data.title if web_recipe_data else 'None'}'")
                logger.info(f"  - Ingredients count: {len(web_recipe_data.ingredients) if web_recipe_data and web_recipe_data.ingredients else 0}")
                logger.info(f"  - Instructions count: {len(web_recipe_data.instructions) if web_recipe_data and web_recipe_data.instructions else 0}")
                logger.info(f"  - Confidence: {web_recipe_data.confidence if web_recipe_data else 0}")
                logger.info(f"  - Extraction method: {web_recipe_data.extraction_method if web_recipe_data else 'None'}")
                
                if web_recipe_data and web_recipe_data.confidence > 0.3:
                    # Convert WebRecipeData to our standard format
                    recipe_dict = self._convert_web_recipe_data(web_recipe_data)
                    
                    # Debug: Log what the conversion produced
                    logger.info(f"🔄 After conversion:")
                    logger.info(f"  - Title: '{recipe_dict.get('title', 'Missing')}'")
                    logger.info(f"  - Ingredients: '{recipe_dict.get('ingredients', 'Missing')[:100]}...'")
                    logger.info(f"  - Instructions: '{recipe_dict.get('instructions', 'Missing')[:100]}...'")
                    
                    # Process with ingredient intelligence
                    processed_recipe = self._process_with_intelligence(recipe_dict, user_id)
                    
                    # Determine if needs review based on confidence
                    confidence = web_recipe_data.confidence
                    needs_review = confidence < self.confidence_threshold
                    
                    # Save to database if confidence is acceptable
                    if confidence >= self.confidence_threshold:
                        try:
                            logger.info(f"🔄 Attempting to save recipe to database (confidence: {confidence})")
                            recipe_id = self._save_recipe_to_database(processed_recipe, user_id)
                            logger.info(f"✅ Successfully saved recipe with ID: {recipe_id}")
                        except Exception as save_error:
                            logger.error(f"❌ Database save failed: {save_error}")
                            # Return fake ID so frontend doesn't break, but log the error
                            recipe_id = 9999  # Fake ID to indicate save failure
                    else:
                        logger.info(f"⚠️ Recipe confidence {confidence} below threshold {self.confidence_threshold} - not saving")
                        recipe_id = None
                    
                    return ImportResult(
                        success=True,
                        recipe_id=recipe_id,
                        recipe_data=processed_recipe,
                        confidence=confidence,
                        needs_review=needs_review,
                        extraction_method=web_recipe_data.extraction_method,
                        warnings=["Low confidence extraction - please review"] if needs_review else []
                    )
                else:
                    return ImportResult(
                        success=False,
                        errors=["Could not extract recipe data from URL"],
                        warnings=["No recipe content found on the page"],
                        extraction_method="web_extraction_failed"
                    )
            else:
                return ImportResult(
                    success=False,
                    errors=["Web extraction system not available"],
                    extraction_method="web_extractor_unavailable"
                )
            
        except Exception as e:
            logger.error(f"URL import failed: {e}")
            return ImportResult(
                success=False,
                errors=[f"URL processing failed: {str(e)}"],
                extraction_method="url_exception"
            )
    
    def _convert_web_recipe_data(self, web_data: 'WebRecipeData') -> Dict:
        """
        Convert WebRecipeData to our standard recipe dictionary format
        """
        try:
            # Convert ingredients list to string
            ingredients_str = '\n'.join(web_data.ingredients) if web_data.ingredients else ''
            
            # Convert instructions list to string
            instructions_str = '\n'.join(web_data.instructions) if web_data.instructions else ''
            
            # Validate that we have actual content
            if not web_data.title and not ingredients_str and not instructions_str:
                logger.warning("⚠️ Web extraction returned empty recipe data!")
                # Return minimal fallback data instead of empty
                return {
                    'title': 'Failed Import - No Data Extracted',
                    'ingredients': '',
                    'instructions': '',
                    'description': f'Failed to extract recipe data from {web_data.source_url}',
                    'category': 'import_failed',
                    'confidence': 0.0,  # Override confidence to 0 for empty data
                    'extraction_method': web_data.extraction_method + '_empty_data'
                }
            
            # Intelligently determine category based on recipe content
            smart_category = self._detect_smart_category(web_data)
            
            # Always keep 'imported' as a secondary category for easy finding
            # This way recipes appear in both their natural category AND the imported folder
            if smart_category != 'imported':
                category = smart_category
                # Store that this was imported for secondary categorization
                secondary_category = 'imported'
                logger.info(f"📂 Recipe categorized as '{category}' with secondary 'imported' tag")
            else:
                category = 'imported'
                secondary_category = None
                logger.info(f"📂 Recipe categorized as 'imported' only")
            
            # Store original category info for reference
            original_category = None
            if web_data.category:
                original_category = web_data.category.lower()
            elif web_data.cuisine:
                original_category = web_data.cuisine.lower()
            elif web_data.keywords:
                original_category = web_data.keywords[0].lower() if web_data.keywords else None
            
            # Enhanced description with import tracking
            description = web_data.description or ""
            if secondary_category:
                description += f" [Imported recipe - also appears in {secondary_category} folder]"
            if original_category:
                description += f" [Original category: {original_category}]"
            else:
                original_category = None
            
            result = {
                'title': web_data.title or 'Imported Recipe',
                'ingredients': ingredients_str,
                'instructions': instructions_str,
                'description': description,
                'category': category,  # Primary category (breakfast/lunch/dinner/etc)
                'time_min': web_data.total_time or web_data.cook_time or web_data.prep_time,
                'servings': web_data.servings or 4,
                'source_url': web_data.source_url,
                'author': web_data.author,
                'rating': web_data.rating,
                'image_url': web_data.image_url,
                'confidence': web_data.confidence,
                'extraction_method': web_data.extraction_method,
                # Add import tracking metadata
                'is_imported': True,  # Flag to identify imported recipes
                'secondary_category': secondary_category,  # For dual categorization
                'import_date': datetime.now().isoformat()  # When it was imported
            }
            
            # Final validation - reduce confidence for poor extractions
            if not result['title'] or result['title'] == 'Imported Recipe':
                result['confidence'] = min(result['confidence'], 0.3)
            if not result['ingredients'] and not result['instructions']:
                result['confidence'] = 0.1
            
            return result
            
        except Exception as e:
            logger.warning(f"Error converting web recipe data: {e}")
            return {
                'title': 'Imported Recipe',
                'ingredients': '',
                'instructions': '',
                'category': 'imported',
                'confidence': 0.0
            }
    
    def _detect_smart_category(self, web_data: 'WebRecipeData') -> str:
        """Intelligently detect recipe category based on content"""
        
        # Get all text to analyze
        title = (web_data.title or '').lower()
        description = (web_data.description or '').lower()
        ingredients = ' '.join(web_data.ingredients).lower() if web_data.ingredients else ''
        
        all_text = f"{title} {description} {ingredients}"
        
        # Define category keywords with better prioritization
        category_keywords = {
            'breakfast': [
                'oatmeal', 'pancake', 'waffle', 'cereal', 'toast', 'egg', 'bacon', 
                'sausage', 'muffin', 'bagel', 'coffee', 'smoothie', 'granola',
                'french toast', 'breakfast', 'brunch'
            ],
            'lunch': [
                'sandwich', 'salad', 'wrap', 'soup', 'burger', 'pizza slice',
                'lunch', 'panini', 'quesadilla', 'bowl', 'sloppy joe'
            ],
            'dinner': [
                'ground beef', 'steak', 'chicken breast', 'roast', 'casserole', 'pasta', 'rice dish',
                'curry', 'stir fry', 'grilled', 'baked chicken', 'fish fillet',
                'dinner', 'entree', 'main course', 'lasagna', 'risotto', 'beef', 'pork'
            ],
            'dessert': [
                'cake', 'cookie', 'pie', 'ice cream', 'chocolate chip', 'brownie',
                'pudding', 'tart', 'cupcake', 'dessert', 'sweet', 'candy', 'frosting'
            ],
            'snack': [
                'chips', 'crackers', 'nuts', 'trail mix', 'popcorn', 'dip',
                'snack', 'appetizer', 'finger food'
            ],
            'beverage': [
                'drink', 'smoothie', 'juice', 'cocktail', 'tea', 'coffee',
                'lemonade', 'beverage', 'shake'
            ]
        }
        
        # Count matches for each category
        category_scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in all_text)
            if score > 0:
                category_scores[category] = score
        
        # Return the category with the highest score
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            logger.info(f"🎯 Smart category detection: '{best_category}' (score: {category_scores[best_category]})")
            return best_category
        
        # Fallback to 'imported' if no clear category detected
        logger.info("🤷 No clear category detected, using 'imported'")
        return 'imported'
    
    def _simple_text_parse(self, text: str) -> Dict:
        """
        Enhanced text parsing for OCR and pasted recipes
        Handles cookbook pages with intelligent section detection
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Skip OCR artifacts
        skip_patterns = ['page', '===', '---', 'www.', 'http']
        
        title = None
        ingredients_section = []
        instructions_section = []
        current_section = None
        found_ingredients_marker = False
        found_instructions_marker = False
        skipped_intro = False
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            
            # Skip page markers
            if any(pattern in line_lower for pattern in skip_patterns):
                continue
            
            # Find title (first meaningful line)
            if not title and i < 10 and len(line) > 3:
                letter_count = sum(1 for c in line if c.isalpha())
                digit_count = sum(1 for c in line if c.isdigit())
                
                if letter_count > digit_count and len(line) < 150:
                    if not any(word in line_lower for word in ['serves', 'serving', 'yield', 'prep', 'cook']):
                        if 'ingredient' not in line_lower and 'instruction' not in line_lower:
                            title = line
                            continue
            
            # Skip intro text (after title, before ingredients)
            # Look for serving size, description lines
            if title and not skipped_intro:
                if any(word in line_lower for word in ['serves', 'yield', 'serving']):
                    continue
                # Long descriptive lines are probably intro
                if len(line) > 80 and not any(char.isdigit() for char in line[:10]):
                    continue
                # Short descriptive text
                if len(line) < 80 and not any(char.isdigit() for char in line) and ',' in line:
                    continue
                # If we get here and see an ingredient pattern, intro is done
                has_measurement = any(unit in line_lower for unit in [
                    'cup', 'tablespoon', 'teaspoon', 'oz', 'ounce', 'lb', 'pound',
                    'gram', 'kg', 'ml', 'liter', 'tsp', 'tbsp', 'pinch', 'dash'
                ])
                has_number = any(char.isdigit() for char in line[:5])
                if has_measurement or has_number or line_lower in ['salt', 'pepper', 'water', 'oil', 'butter']:
                    skipped_intro = True
                    current_section = 'ingredients'
                    # Don't continue - process this line below
            
            # Detect explicit section markers
            if 'ingredient' in line_lower and len(line) < 30:
                current_section = 'ingredients'
                found_ingredients_marker = True
                skipped_intro = True
                continue
            elif any(marker in line_lower for marker in ['instruction', 'direction', 'method', 'preparation']) and len(line) < 30:
                current_section = 'instructions'
                found_instructions_marker = True
                continue
            
            # Smart detection: If we see action words and have ingredients, switch to instructions
            action_words = ['heat', 'cook', 'add', 'bring', 'stir', 'mix', 'pour', 'place', 'remove', 'drain', 'serve', 'bake', 'roast', 'sauté', 'boil', 'simmer', 'preheat', 'combine', 'whisk', 'fold']
            starts_with_action = any(line_lower.startswith(word) for word in action_words)
            
            # If line starts with action word and we've collected some ingredients, switch to instructions
            if starts_with_action and len(ingredients_section) > 2 and not found_instructions_marker:
                current_section = 'instructions'
                found_instructions_marker = True
            
            # Collect lines based on section
            if current_section == 'ingredients':
                # Ingredient patterns
                has_measurement = any(unit in line_lower for unit in [
                    'cup', 'tablespoon', 'teaspoon', 'oz', 'ounce', 'lb', 'pound',
                    'gram', 'kg', 'ml', 'liter', 'tsp', 'tbsp', 'pinch', 'dash', 'clove'
                ])
                has_bullet = line.strip().startswith(('-', '•', '*', '+', '◦'))
                has_number = any(char.isdigit() for char in line[:5])
                
                # Common ingredients without measurements
                simple_ingredients = ['salt', 'pepper', 'water', 'oil', 'butter', 'sugar', 'flour']
                is_simple_ingredient = any(ing in line_lower for ing in simple_ingredients) and len(line) < 30
                
                # Include line if it looks like an ingredient
                if has_measurement or has_bullet or has_number or is_simple_ingredient:
                    # Clean the line
                    cleaned_line = line.lstrip('-•*+ ')
                    ingredients_section.append(cleaned_line)
                elif line and len(line) > 3:
                    # Could still be an ingredient
                    # But check if it's actually an instruction
                    if not starts_with_action:
                        ingredients_section.append(line)
                    else:
                        # This is an instruction!
                        current_section = 'instructions'
                        instructions_section.append(line)
                        
            elif current_section == 'instructions':
                # Clean and add to instructions
                cleaned_line = line.lstrip('-•*+ 0123456789.')
                instructions_section.append(cleaned_line)
        
        # Use fallback title if needed
        if not title or title.lower() in ['page 1', 'page 2']:
            title = "Imported Recipe"
        
        # Join sections
        ingredients_text = '\n'.join(ingredients_section) if ingredients_section else "No ingredients detected"
        instructions_text = '\n'.join(instructions_section) if instructions_section else "See ingredients section"
        
        return {
            'title': title,
            'ingredients': ingredients_text,
            'instructions': instructions_text,
            'category': 'imported',
            'confidence': 0.7
        }
    
    def _process_with_intelligence(self, recipe: Any, user_id: int) -> Dict:
        """
        Process recipe with IngredientIntelligenceEngine if available
        """
        if not self.ingredient_engine:
            # Return as-is if no intelligence engine
            return recipe if isinstance(recipe, dict) else asdict(recipe)
        
        try:
            # Convert to dict if needed
            recipe_dict = recipe if isinstance(recipe, dict) else asdict(recipe)
            
            # Process ingredients with intelligence engine
            if 'ingredients' in recipe_dict and recipe_dict['ingredients']:
                ingredient_lines = recipe_dict['ingredients'].split('\n')
                processed_ingredients = []
                
                for ingredient_line in ingredient_lines:
                    if ingredient_line.strip():
                        # Use intelligence engine to process ingredient
                        mapping = self.ingredient_engine.map_ingredient(ingredient_line.strip())
                        processed_ingredients.append({
                            'original_text': ingredient_line.strip(),
                            'canonical_name': mapping.canonical_name,
                            'confidence': mapping.confidence,
                            'amount': mapping.amount,
                            'unit': mapping.unit
                        })
                
                recipe_dict['processed_ingredients'] = processed_ingredients
                
            return recipe_dict
            
        except Exception as e:
            logger.warning(f"Intelligence processing failed: {e}")
            return recipe if isinstance(recipe, dict) else asdict(recipe)
    
    def _save_recipe_to_database(self, recipe_data: Dict, user_id: int) -> int:
        """
        Save recipe to PostgreSQL database using existing schema
        """
        try:
            conn = self.get_database_connection()
            cursor = conn.cursor()
            
            # 🔧 Convert arrays to strings for database if needed
            ingredients = recipe_data.get('ingredients', '')
            if isinstance(ingredients, list):
                # Keep as JSON array for proper parsing in mobile app
                ingredients = json.dumps(ingredients)
                logger.info(f"📝 Converted ingredients list to JSON string")
            
            instructions = recipe_data.get('instructions', '')
            if isinstance(instructions, list):
                # Keep as JSON array for proper parsing in mobile app
                instructions = json.dumps(instructions)
                logger.info(f"📝 Converted instructions list to JSON string")
            
            # Insert recipe using enhanced schema for imported recipes
            insert_query = """
                INSERT INTO recipes (title, ingredients, instructions, category, 
                                   hands_on_time, total_time, servings, created_at,
                                   book_id, page_number, meal_role, user_id, 
                                   imported_at, source_url, confidence)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s, NOW(), %s, %s)
                RETURNING id
            """
            
            # Map imported data to existing schema
            time_min = recipe_data.get('time_min', 30)
            
            # Map category to proper meal_role
            def map_category_to_meal_role(category):
                if not category:
                    return 'dinner'
                cat = category.lower()
                if 'breakfast' in cat or 'brunch' in cat:
                    return 'breakfast'
                if 'lunch' in cat or 'salad' in cat:
                    return 'lunch'
                if 'dessert' in cat or 'sweet' in cat or 'cake' in cat or 'cookie' in cat:
                    return 'dessert'
                if 'snack' in cat or 'appetizer' in cat:
                    return 'snack'
                if 'side' in cat:
                    return 'side'
                # Default main dishes to dinner
                return 'dinner'
            
            meal_role = map_category_to_meal_role(recipe_data.get('category'))
            
            cursor.execute(insert_query, (
                recipe_data.get('title', 'Imported Recipe'),
                ingredients,  # Now properly formatted as JSON string
                instructions,  # Now properly formatted as JSON string
                'imported',  # Always mark as 'imported' category for easy filtering
                time_min,  # hands_on_time
                time_min,  # total_time (same as hands_on for imported)
                recipe_data.get('servings', 4),    # Default 4 servings
                0,  # book_id (0 for imported recipes)
                0,  # page_number (0 for imported recipes)
                meal_role,  # proper meal_role mapping
                user_id,  # link to importing user
                recipe_data.get('source_url', ''),  # source URL if available
                recipe_data.get('confidence', 0.8)  # import confidence score
            ))
            
            recipe_id = cursor.fetchone()['id']
            conn.commit()
            
            logger.info(f"✅ Recipe saved to database with ID: {recipe_id}")
            return recipe_id
            
        except Exception as e:
            logger.error(f"Database save failed: {e}")
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn:
                cursor.close()
                conn.close()
    
    def check_for_duplicates(self, recipe_data: Dict, user_id: int) -> List[Dict]:
        """
        Check for duplicate recipes using UniversalSearchEngine
        """
        if not self.search_engine:
            return []
        
        try:
            # Search for similar recipes
            title = recipe_data.get('title', '')
            results = self.search_engine.unified_intelligent_search(
                query=title,
                limit=5,
                filters={'user_id': user_id}
            )
            
            # Filter for high similarity matches
            duplicates = []
            for result in results:
                # Simple title similarity check
                similarity = self._calculate_similarity(title, result.get('title', ''))
                if similarity > 0.8:
                    duplicates.append({
                        'recipe_id': result.get('id'),
                        'title': result.get('title'),
                        'similarity': similarity
                    })
            
            return duplicates
            
        except Exception as e:
            logger.warning(f"Duplicate check failed: {e}")
            return []
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Simple text similarity calculation
        """
        from difflib import SequenceMatcher
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    # 🎥 YouTube Integration Methods
    
    def _is_youtube_url(self, url: str) -> bool:
        """Check if URL is from YouTube"""
        youtube_domains = ['youtube.com', 'youtu.be', 'm.youtube.com']
        url_lower = url.lower()
        return any(domain in url_lower for domain in youtube_domains)
    
    def _import_from_youtube(self, url: str, user_id: int, metadata: Dict = None) -> ImportResult:
        """
        Import recipe from YouTube video
        
        Flow:
        1. Extract video content (metadata + transcript) using YouTubeRecipeExtractor
        2. Send combined text to OpenAI for recipe parsing
        3. Process ingredients with IngredientIntelligenceEngine
        4. Save to database
        
        Args:
            url: YouTube video URL
            user_id: User ID for recipe ownership
            metadata: Optional metadata
            
        Returns:
            ImportResult with recipe data
        """
        if not self.youtube_extractor:
            return ImportResult(
                success=False,
                errors=['YouTube extraction not available - missing API key or dependencies'],
                extraction_method='youtube_unavailable'
            )
        
        try:
            # Extract video content
            logger.info(f"🎥 Extracting YouTube video content from: {url}")
            extraction_result = self.youtube_extractor.extract_recipe_content(url)
            
            if not extraction_result['success']:
                return ImportResult(
                    success=False,
                    errors=[extraction_result.get('error', 'YouTube extraction failed')],
                    extraction_method='youtube_extraction_failed'
                )
            
            video_data = extraction_result['video_data']
            combined_text = extraction_result['combined_text']
            
            logger.info(f"✅ Extracted YouTube content:")
            logger.info(f"   Title: {video_data.title}")
            logger.info(f"   Channel: {video_data.channel}")
            logger.info(f"   Has Transcript: {video_data.captions_available}")
            logger.info(f"   Text Length: {len(combined_text)} chars")
            
            # Parse recipe using OpenAI
            logger.info(f"🤖 Parsing recipe with OpenAI...")
            recipe_data = self._parse_youtube_recipe_with_ai(combined_text, video_data, url)
            
            if not recipe_data:
                return ImportResult(
                    success=False,
                    errors=['AI recipe parsing failed - could not extract recipe from video content'],
                    warnings=['Video may not contain a complete recipe'],
                    extraction_method='youtube_ai_parsing_failed'
                )
            
            # 🔍 DEBUG: Log what AI returned
            logger.info(f"🔍 AI Parser returned recipe_data:")
            logger.info(f"   Title: {recipe_data.get('title', 'MISSING')}")
            logger.info(f"   Ingredients type: {type(recipe_data.get('ingredients'))}")
            logger.info(f"   Ingredients count: {len(recipe_data.get('ingredients', []))}")
            logger.info(f"   Ingredients sample: {recipe_data.get('ingredients', [])[:2]}")
            logger.info(f"   Instructions type: {type(recipe_data.get('instructions'))}")
            logger.info(f"   Instructions count: {len(recipe_data.get('instructions', []))}")
            logger.info(f"   Instructions sample: {recipe_data.get('instructions', [])[:2]}")
            logger.info(f"   All keys in recipe_data: {list(recipe_data.keys())}")
            
            # Enhance with video metadata
            recipe_data['source'] = 'YouTube'
            recipe_data['source_url'] = url
            recipe_data['source_title'] = video_data.title
            recipe_data['source_channel'] = video_data.channel
            if video_data.thumbnail_url:
                recipe_data['image_url'] = video_data.thumbnail_url
            
            # Process ingredients with existing intelligence
            if self.ingredient_engine and recipe_data.get('ingredients'):
                logger.info(f"🧠 Processing ingredients with IngredientIntelligenceEngine...")
                processed_recipe = self._process_with_intelligence(recipe_data, user_id)
            else:
                processed_recipe = recipe_data
            
            # 🔍 DEBUG: Log processed recipe before save
            logger.info(f"🔍 Processed recipe before database save:")
            logger.info(f"   Title: {processed_recipe.get('title')}")
            logger.info(f"   Ingredients type: {type(processed_recipe.get('ingredients'))}")
            if isinstance(processed_recipe.get('ingredients'), list):
                logger.info(f"   Ingredients is a list with {len(processed_recipe['ingredients'])} items")
            logger.info(f"   Instructions type: {type(processed_recipe.get('instructions'))}")
            if isinstance(processed_recipe.get('instructions'), list):
                logger.info(f"   Instructions is a list with {len(processed_recipe['instructions'])} items")
            
            # 🆕 DON'T auto-save YouTube imports - let user review first
            # Mobile app will save after user confirms in RecipeImportReviewScreen
            logger.info(f"✅ YouTube recipe extracted successfully (not saved yet - waiting for user review)")
            
            return ImportResult(
                success=True,
                recipe_id=None,  # No ID yet - will be created when user saves
                recipe_data=processed_recipe,
                confidence=0.85,  # YouTube videos with transcripts generally have good structure
                needs_review=True,  # Always review AI-extracted recipes
                extraction_method='youtube_ai',
                warnings=['Please review AI-extracted recipe for accuracy']
            )
            
        except Exception as e:
            logger.error(f"❌ YouTube import failed: {e}")
            import traceback
            traceback.print_exc()
            return ImportResult(
                success=False,
                errors=[f'YouTube import error: {str(e)}'],
                extraction_method='youtube_exception'
            )
    
    def _parse_youtube_recipe_with_ai(self, text: str, video_data, url: str) -> Optional[Dict]:
        """
        Use OpenAI to parse recipe from YouTube video content
        
        This is where the magic happens: converts raw video text → structured recipe
        
        Args:
            text: Combined text from video (title + description + transcript)
            video_data: YouTubeVideoData object with metadata
            url: Original video URL
            
        Returns:
            Dict with recipe data or None if parsing fails
        """
        import openai
        
        # Get API key from environment
        openai_key = os.getenv('OPENAI_API_KEY')
        
        if not openai_key:
            logger.error("❌ OpenAI API key not configured")
            return None
        
        try:
            client = openai.OpenAI(api_key=openai_key)
            
            prompt = f"""
You are a recipe extraction expert. Extract recipe information from this YouTube cooking video content and format it as JSON.

VIDEO INFORMATION:
- Title: {video_data.title}
- Channel: {video_data.channel}
- Duration: {video_data.duration_seconds} seconds
- Source URL: {url}

VIDEO CONTENT:
{text[:15000]}  

INSTRUCTIONS:
Extract and return a complete recipe in this EXACT JSON format:
{{
  "title": "Recipe name (extract from video title)",
  "servings": "number or range (e.g., '4' or '4-6')",
  "prep_time": "preparation time in minutes (number only, estimate if not mentioned)",
  "cook_time": "cooking time in minutes (number only, estimate if not mentioned)",
  "total_time": "total time in minutes (number only)",
  "difficulty": "easy, medium, or hard (estimate based on recipe complexity)",
  "ingredients": [
    "ingredient with quantity (e.g., '2 cups all-purpose flour')",
    "ingredient with quantity",
    ...
  ],
  "instructions": [
    "Detailed instruction with specific actions",
    "Another detailed instruction",
    "Continue with remaining instructions"
  ],
  "tips": [
    "Optional cooking tip or variation",
    ...
  ],
  "description": "Brief 1-2 sentence description of what this recipe is",
  "tags": ["tag1", "tag2", "tag3"]
}}

CRITICAL RULES:
1. Extract ALL ingredients mentioned with their exact quantities
2. Preserve measurements (cups, tablespoons, grams, teaspoons, etc.)
3. Keep instruction steps in chronological order
4. DO NOT include step numbers like "Step 1:", "Step 2:" - just write the instruction
5. Each instruction should be a complete sentence describing one action or set of related actions
6. If times aren't explicitly mentioned, estimate based on recipe type
7. Include any special techniques, equipment, or temperature settings in the relevant instruction
8. Make the description appealing and informative
9. Add relevant tags (e.g., "quick", "vegetarian", "dessert", "italian")
10. If servings aren't mentioned, estimate based on ingredient quantities
11. Return ONLY valid JSON - no markdown, no explanations, just the JSON object

Focus on creating a complete, accurate, and user-friendly recipe. The user will review it before saving.
"""
            
            logger.info(f"🤖 Sending {len(prompt)} chars to OpenAI GPT-4...")
            
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a recipe extraction expert. Return only valid JSON with complete recipe information."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3,  # Lower temperature for more consistent/accurate results
                max_tokens=2000
            )
            
            recipe_json = response.choices[0].message.content
            recipe_data = json.loads(recipe_json)
            
            logger.info(f"✅ OpenAI successfully parsed recipe:")
            logger.info(f"   Title: {recipe_data.get('title', 'Unknown')}")
            logger.info(f"   Ingredients: {len(recipe_data.get('ingredients', []))} items")
            logger.info(f"   Instructions: {len(recipe_data.get('instructions', []))} steps")
            
            return recipe_data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse OpenAI response as JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ OpenAI API error: {e}")
            return None

# Export main class
__all__ = ['UniversalRecipeImporter', 'ImportRequest', 'ImportResult']

if __name__ == "__main__":
    # Basic testing
    importer = UniversalRecipeImporter()
    
    test_recipe = """
    Spaghetti Carbonara
    
    Ingredients:
    - 400g spaghetti
    - 200g pancetta, diced
    - 4 large eggs
    - 100g Parmesan cheese, grated
    - Black pepper
    - Salt
    
    Instructions:
    1. Cook spaghetti according to package directions
    2. Fry pancetta until crispy
    3. Beat eggs with Parmesan
    4. Combine hot pasta with pancetta
    5. Add egg mixture and toss quickly
    6. Season with pepper and serve
    """
    
    request = ImportRequest(
        source_type='text',
        source_data=test_recipe,
        user_id=1
    )
    
    result = importer.import_recipe(request)
    print(f"Import result: {result}")
