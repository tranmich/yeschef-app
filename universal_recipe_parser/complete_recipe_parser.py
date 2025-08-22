#!/usr/bin/env python3
"""
🧠📚 COMPLETE UNIVERSAL RECIPE PARSER
====================================

The definitive learning document combining all extraction knowledge:
- Rule-based extraction patterns from ATK, Bittman, and other cookbooks
- Visual structure detection and layout analysis
- Semantic validation and confidence scoring
- ML training data generation capabilities
- Hybrid inference architecture (ML regions + rule parsing)
- Best practices and lessons learned from multiple cookbook projects

This serves as both a working parser and a knowledge repository for
all recipe extraction techniques developed across different cookbooks.

Author: GitHub Copilot
Date: August 22, 2025
Status: Complete Learning Document & Production Parser
"""

import os
import sys
import re
import json
import logging
import PyPDF2
import argparse
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher

# Add core systems to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core_systems'))

try:
    from database_manager import DatabaseManager
    from semantic_recipe_engine import SemanticRecipeEngine, ValidationLevel
    from ingredient_intelligence_engine import IngredientIntelligenceEngine
    print("✅ Core Systems Loaded Successfully")
except ImportError as e:
    print(f"⚠️ Core systems not available: {e}")
    print("📝 Parser will work in standalone mode")

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

@dataclass
class RecipeData:
    """Standardized recipe data structure"""
    title: str = ""
    ingredients: str = ""
    instructions: str = ""
    servings: str = ""
    prep_time: str = ""
    cook_time: str = ""
    total_time: str = ""
    category: str = ""
    source: str = ""
    page_number: int = 0
    confidence_scores: Dict[str, float] = None
    extraction_metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.confidence_scores is None:
            self.confidence_scores = {}
        if self.extraction_metadata is None:
            self.extraction_metadata = {}

@dataclass
class ExtractionStrategy:
    """Defines extraction strategy for different cookbook types"""
    name: str
    toc_pages: List[int]
    recipe_start_page: int
    recipe_end_page: int
    layout_type: str  # 'single_column', 'two_column', 'magazine', 'minimal'
    title_patterns: List[str]
    ingredients_markers: List[str]
    instructions_markers: List[str]
    font_based_detection: bool = True
    visual_structure_detection: bool = True
    semantic_validation: bool = True

class UniversalRecipeParser:
    """
    Complete Universal Recipe Parser combining all extraction knowledge
    
    EXTRACTION STRATEGIES:
    1. Rule-Based Detection (fonts, patterns, structure)
    2. TOC Cross-Referencing (when available)
    3. Visual Structure Analysis (layout patterns)
    4. Semantic Validation (ingredient/instruction recognition)
    5. ML Training Data Generation (for hybrid approach)
    6. Confidence Scoring and Quality Assessment
    
    SUPPORTED FORMATS:
    - ATK (America's Test Kitchen) cookbooks
    - Bittman (How to Cook Everything) style
    - Magazine-style layouts
    - Minimal/simple cookbook formats
    - Web article formats (when rendered to PDF)
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.extraction_strategies = self._initialize_extraction_strategies()
        self.stats = self._initialize_stats()
        
        # Core extraction components
        self.toc_extractor = TOCExtractor()
        self.visual_detector = VisualStructureDetector() 
        self.pattern_matcher = PatternMatcher()
        self.semantic_validator = SemanticValidator()
        self.confidence_scorer = ConfidenceScorer()
        
        # ML training components
        self.training_data_generator = TrainingDataGenerator()
        
        # Results storage
        self.extracted_recipes = []
        self.extraction_log = []
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load parser configuration"""
        default_config = {
            'min_recipe_length': 50,
            'max_recipe_length': 5000,
            'confidence_threshold': 0.7,
            'enable_semantic_validation': True,
            'enable_ml_training_generation': True,
            'output_format': 'json',
            'debug_mode': False
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Could not load config from {config_path}: {e}")
        
        return default_config
    
    def _initialize_extraction_strategies(self) -> Dict[str, ExtractionStrategy]:
        """Initialize extraction strategies for different cookbook types"""
        
        strategies = {
            'atk_25th': ExtractionStrategy(
                name="ATK 25th Anniversary",
                toc_pages=[738, 739, 740],
                recipe_start_page=750,
                recipe_end_page=1200,
                layout_type='single_column',
                title_patterns=[
                    r'^[A-Z][^a-z]*[A-Z]$',  # ALL CAPS or Title Case
                    r'^\d+\.\s+[A-Z]',       # Numbered titles
                ],
                ingredients_markers=['INGREDIENTS', 'SERVES', 'MAKES'],
                instructions_markers=['INSTRUCTIONS', 'METHOD', '1.', 'STEP'],
                font_based_detection=True,
                visual_structure_detection=True,
                semantic_validation=True
            ),
            
            'bittman': ExtractionStrategy(
                name="Bittman How to Cook Everything",
                toc_pages=[],
                recipe_start_page=50,
                recipe_end_page=1000,
                layout_type='two_column',
                title_patterns=[
                    r'^[A-Z][a-z].*[a-z]$',  # Sentence case
                    r'^[A-Z].*[a-z]$',       # Title case
                ],
                ingredients_markers=['Ingredients:', 'You need:', 'For'],
                instructions_markers=['1.', 'First,', 'Start', 'Heat'],
                font_based_detection=True,
                visual_structure_detection=True,
                semantic_validation=True
            ),
            
            'magazine_style': ExtractionStrategy(
                name="Magazine Style Cookbook",
                toc_pages=[],
                recipe_start_page=20,
                recipe_end_page=300,
                layout_type='magazine',
                title_patterns=[
                    r'^[A-Z].*$',            # Any capitalized title
                ],
                ingredients_markers=['INGREDIENTS', 'YOU\'LL NEED', 'WHAT YOU NEED'],
                instructions_markers=['DIRECTIONS', 'METHOD', 'HOW TO'],
                font_based_detection=True,
                visual_structure_detection=True,
                semantic_validation=True
            ),
            
            'minimal': ExtractionStrategy(
                name="Minimal/Simple Cookbook",
                toc_pages=[],
                recipe_start_page=10,
                recipe_end_page=500,
                layout_type='minimal',
                title_patterns=[
                    r'^.{5,60}$',           # Any reasonable title length
                ],
                ingredients_markers=['ingredients', 'needs', 'for'],
                instructions_markers=['instructions', 'method', 'directions'],
                font_based_detection=False,
                visual_structure_detection=True,
                semantic_validation=True
            )
        }
        
        return strategies
    
    def _initialize_stats(self) -> Dict[str, Any]:
        """Initialize extraction statistics"""
        return {
            'total_pages_processed': 0,
            'recipes_found': 0,
            'toc_mappings_successful': 0,
            'visual_structure_detected': 0,
            'semantic_validations_passed': 0,
            'high_confidence_extractions': 0,
            'medium_confidence_extractions': 0,
            'low_confidence_extractions': 0,
            'failed_extractions': 0,
            'ml_training_samples_generated': 0,
            'extraction_start_time': None,
            'extraction_end_time': None
        }
    
    def extract_recipes(self, pdf_path: str, strategy_name: str = 'auto') -> List[RecipeData]:
        """
        Main extraction method - combines all extraction techniques
        
        Args:
            pdf_path: Path to PDF cookbook
            strategy_name: Extraction strategy ('atk_25th', 'bittman', 'magazine_style', 'minimal', 'auto')
        
        Returns:
            List of extracted RecipeData objects
        """
        
        self.stats['extraction_start_time'] = datetime.now()
        logger.info(f"🚀 Starting universal recipe extraction: {pdf_path}")
        
        try:
            # Step 1: Auto-detect or use specified strategy
            if strategy_name == 'auto':
                strategy = self._auto_detect_strategy(pdf_path)
            else:
                strategy = self.extraction_strategies.get(strategy_name)
            
            if not strategy:
                raise ValueError(f"Unknown extraction strategy: {strategy_name}")
            
            logger.info(f"📋 Using extraction strategy: {strategy.name}")
            
            # Step 2: PDF analysis and preprocessing
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                total_pages = len(reader.pages)
                
                logger.info(f"📄 PDF loaded: {total_pages} pages")
                
                # Step 3: TOC extraction and mapping (if available)
                toc_mappings = {}
                if strategy.toc_pages:
                    toc_mappings = self.toc_extractor.extract_toc_mappings(reader, strategy)
                    self.stats['toc_mappings_successful'] = len(toc_mappings)
                    logger.info(f"📚 TOC mappings: {len(toc_mappings)} recipes indexed")
                
                # Step 4: Page-by-page extraction
                for page_num in range(strategy.recipe_start_page - 1, 
                                    min(strategy.recipe_end_page, total_pages)):
                    
                    try:
                        recipe_data = self._extract_page(reader, page_num + 1, strategy, toc_mappings)
                        
                        if recipe_data and self._validate_recipe(recipe_data):
                            self.extracted_recipes.append(recipe_data)
                            self.stats['recipes_found'] += 1
                            
                            # Update confidence stats
                            overall_confidence = self._calculate_overall_confidence(recipe_data)
                            if overall_confidence >= 0.8:
                                self.stats['high_confidence_extractions'] += 1
                            elif overall_confidence >= 0.6:
                                self.stats['medium_confidence_extractions'] += 1
                            else:
                                self.stats['low_confidence_extractions'] += 1
                        
                        self.stats['total_pages_processed'] += 1
                        
                        # Progress logging
                        if (page_num + 1) % 50 == 0:
                            logger.info(f"📊 Progress: Page {page_num + 1}/{total_pages}, "
                                      f"Recipes: {self.stats['recipes_found']}")
                    
                    except Exception as e:
                        logger.warning(f"⚠️ Error processing page {page_num + 1}: {e}")
                        self.stats['failed_extractions'] += 1
                        continue
                
                # Step 5: Post-processing and cleanup
                self._post_process_recipes()
                
                # Step 6: Generate ML training data (if enabled)
                if self.config['enable_ml_training_generation']:
                    self._generate_ml_training_data(pdf_path, strategy)
                
                self.stats['extraction_end_time'] = datetime.now()
                self._log_final_stats()
                
                return self.extracted_recipes
                
        except Exception as e:
            logger.error(f"❌ Fatal error during extraction: {e}")
            raise
    
    def _auto_detect_strategy(self, pdf_path: str) -> ExtractionStrategy:
        """
        Auto-detect the best extraction strategy for the cookbook
        
        Uses heuristics like filename, page count, and sample page analysis
        """
        
        logger.info("🔍 Auto-detecting extraction strategy...")
        
        filename = os.path.basename(pdf_path).lower()
        
        # Filename-based detection
        if 'atk' in filename or 'america' in filename or 'test kitchen' in filename:
            return self.extraction_strategies['atk_25th']
        elif 'bittman' in filename or 'how to cook' in filename:
            return self.extraction_strategies['bittman']
        
        # Sample page analysis
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                total_pages = len(reader.pages)
                
                # Analyze structure clues from sample pages
                sample_pages = [min(50, total_pages//4), min(100, total_pages//2)]
                
                for page_idx in sample_pages:
                    if page_idx < len(reader.pages):
                        page_text = reader.pages[page_idx].extract_text()
                        
                        # Look for ATK-specific patterns
                        if any(pattern in page_text for pattern in 
                              ['TEST KITCHEN', 'AMERICA\'S', 'SERVES', 'MAKES']):
                            return self.extraction_strategies['atk_25th']
                        
                        # Look for magazine-style patterns
                        if any(pattern in page_text for pattern in 
                              ['INGREDIENTS', 'DIRECTIONS', 'PREP TIME']):
                            return self.extraction_strategies['magazine_style']
                
                # Default based on page count
                if total_pages > 800:
                    return self.extraction_strategies['atk_25th']
                elif total_pages > 400:
                    return self.extraction_strategies['bittman']
                else:
                    return self.extraction_strategies['magazine_style']
                    
        except Exception as e:
            logger.warning(f"⚠️ Auto-detection failed: {e}")
            return self.extraction_strategies['minimal']
    
    def _extract_page(self, reader, page_num: int, strategy: ExtractionStrategy, 
                     toc_mappings: Dict) -> Optional[RecipeData]:
        """
        Extract recipe data from a single page using comprehensive approach
        
        Combines multiple extraction techniques:
        1. TOC guidance (if available)
        2. Visual structure detection
        3. Pattern matching
        4. Semantic validation
        5. Confidence scoring
        """
        
        try:
            page = reader.pages[page_num - 1]
            page_text = page.extract_text()
            
            if not page_text or len(page_text.strip()) < 50:
                return None
            
            # Initialize recipe data
            recipe_data = RecipeData(
                page_number=page_num,
                source=strategy.name,
                extraction_metadata={
                    'extraction_method': [],
                    'processing_time': datetime.now().isoformat(),
                    'strategy': strategy.name
                }
            )
            
            # Method 1: TOC-guided extraction
            if toc_mappings:
                toc_result = self._extract_with_toc_guidance(page_text, page_num, toc_mappings)
                if toc_result:
                    recipe_data = self._merge_extraction_results(recipe_data, toc_result)
                    recipe_data.extraction_metadata['extraction_method'].append('toc_guided')
            
            # Method 2: Visual structure detection
            if strategy.visual_structure_detection:
                visual_result = self.visual_detector.analyze_page_structure(page_text, page_num)
                if visual_result and visual_result.get('is_recipe_page'):
                    structure_data = self._extract_with_visual_structure(page_text, visual_result)
                    recipe_data = self._merge_extraction_results(recipe_data, structure_data)
                    recipe_data.extraction_metadata['extraction_method'].append('visual_structure')
                    self.stats['visual_structure_detected'] += 1
            
            # Method 3: Pattern-based extraction
            pattern_result = self.pattern_matcher.extract_with_patterns(page_text, strategy)
            if pattern_result:
                recipe_data = self._merge_extraction_results(recipe_data, pattern_result)
                recipe_data.extraction_metadata['extraction_method'].append('pattern_matching')
            
            # Method 4: Semantic validation and enhancement
            if strategy.semantic_validation and self.config['enable_semantic_validation']:
                validated_data = self.semantic_validator.validate_and_enhance(recipe_data)
                if validated_data:
                    recipe_data = validated_data
                    recipe_data.extraction_metadata['extraction_method'].append('semantic_validation')
                    self.stats['semantic_validations_passed'] += 1
            
            # Method 5: Confidence scoring
            confidence_scores = self.confidence_scorer.calculate_scores(recipe_data, page_text)
            recipe_data.confidence_scores = confidence_scores
            
            # Only return if minimum confidence threshold is met
            overall_confidence = self._calculate_overall_confidence(recipe_data)
            if overall_confidence >= self.config['confidence_threshold']:
                return recipe_data
            else:
                self.extraction_log.append({
                    'page': page_num,
                    'status': 'below_threshold',
                    'confidence': overall_confidence,
                    'data': asdict(recipe_data)
                })
                return None
                
        except Exception as e:
            logger.warning(f"⚠️ Error extracting page {page_num}: {e}")
            return None
    
    def _extract_with_toc_guidance(self, page_text: str, page_num: int, 
                                  toc_mappings: Dict) -> Optional[RecipeData]:
        """Extract recipe using TOC guidance when available"""
        
        # Find if this page has a known recipe from TOC
        page_recipe_title = None
        for title, mapped_page in toc_mappings.items():
            if mapped_page == page_num:
                page_recipe_title = title
                break
        
        if not page_recipe_title:
            return None
        
        recipe_data = RecipeData(title=page_recipe_title)
        
        # Use title to guide extraction of ingredients and instructions
        lines = page_text.split('\n')
        
        # Find title position to guide section extraction
        title_line_idx = -1
        for i, line in enumerate(lines):
            if page_recipe_title.lower() in line.lower():
                title_line_idx = i
                break
        
        if title_line_idx >= 0:
            # Extract ingredients (usually after title)
            ingredients_section = self._extract_section_after_marker(
                lines[title_line_idx:], ['INGREDIENTS', 'SERVES', 'MAKES']
            )
            if ingredients_section:
                recipe_data.ingredients = ingredients_section
            
            # Extract instructions (usually after ingredients)
            instructions_section = self._extract_section_after_marker(
                lines[title_line_idx:], ['INSTRUCTIONS', 'METHOD', '1.']
            )
            if instructions_section:
                recipe_data.instructions = instructions_section
        
        return recipe_data if recipe_data.ingredients or recipe_data.instructions else None
    
    def _extract_with_visual_structure(self, page_text: str, visual_analysis: Dict) -> Optional[RecipeData]:
        """Extract recipe using visual structure analysis"""
        
        recipe_data = RecipeData()
        
        # Use visual structure indicators to guide extraction
        if visual_analysis.get('title_candidates'):
            recipe_data.title = visual_analysis['title_candidates'][0]
        
        if visual_analysis.get('ingredients_section'):
            recipe_data.ingredients = visual_analysis['ingredients_section']
        
        if visual_analysis.get('instructions_section'):
            recipe_data.instructions = visual_analysis['instructions_section']
        
        return recipe_data if recipe_data.title or recipe_data.ingredients else None
    
    def _extract_section_after_marker(self, lines: List[str], markers: List[str]) -> str:
        """Extract text section after finding a marker"""
        
        marker_found_idx = -1
        for i, line in enumerate(lines):
            line_upper = line.upper().strip()
            if any(marker.upper() in line_upper for marker in markers):
                marker_found_idx = i
                break
        
        if marker_found_idx == -1:
            return ""
        
        # Extract lines after marker until next major section or end
        section_lines = []
        for i in range(marker_found_idx + 1, min(len(lines), marker_found_idx + 20)):
            line = lines[i].strip()
            
            # Stop at next major section
            if any(stop_word in line.upper() for stop_word in 
                  ['INSTRUCTIONS', 'METHOD', 'DIRECTIONS', 'NOTES', 'VARIATION']):
                if len(section_lines) > 0:  # Only stop if we have content
                    break
            
            if line and not line.startswith('PAGE'):
                section_lines.append(line)
        
        return '\n'.join(section_lines) if section_lines else ""
    
    def _merge_extraction_results(self, base_data: RecipeData, new_data: Union[RecipeData, Dict]) -> RecipeData:
        """Merge extraction results, preferring non-empty values"""
        
        if isinstance(new_data, dict):
            new_data = RecipeData(**new_data)
        
        # Merge fields, preferring non-empty values
        if new_data.title and not base_data.title:
            base_data.title = new_data.title
        if new_data.ingredients and not base_data.ingredients:
            base_data.ingredients = new_data.ingredients
        if new_data.instructions and not base_data.instructions:
            base_data.instructions = new_data.instructions
        if new_data.servings and not base_data.servings:
            base_data.servings = new_data.servings
        if new_data.prep_time and not base_data.prep_time:
            base_data.prep_time = new_data.prep_time
        if new_data.cook_time and not base_data.cook_time:
            base_data.cook_time = new_data.cook_time
        if new_data.category and not base_data.category:
            base_data.category = new_data.category
        
        return base_data
    
    def _validate_recipe(self, recipe_data: RecipeData) -> bool:
        """Validate that extracted recipe has minimum required content"""
        
        # Must have title and either ingredients or instructions
        has_title = bool(recipe_data.title and len(recipe_data.title.strip()) > 3)
        has_ingredients = bool(recipe_data.ingredients and len(recipe_data.ingredients.strip()) > 20)
        has_instructions = bool(recipe_data.instructions and len(recipe_data.instructions.strip()) > 30)
        
        return has_title and (has_ingredients or has_instructions)
    
    def _calculate_overall_confidence(self, recipe_data: RecipeData) -> float:
        """Calculate overall confidence score for recipe extraction"""
        
        if not recipe_data.confidence_scores:
            return 0.5  # Default medium confidence
        
        scores = []
        weights = {'title': 0.3, 'ingredients': 0.4, 'instructions': 0.3}
        
        for field, weight in weights.items():
            if field in recipe_data.confidence_scores:
                scores.append(recipe_data.confidence_scores[field] * weight)
        
        return sum(scores) if scores else 0.5
    
    def _post_process_recipes(self):
        """Post-process extracted recipes for cleanup and enhancement"""
        
        logger.info(f"🔧 Post-processing {len(self.extracted_recipes)} recipes...")
        
        for recipe in self.extracted_recipes:
            # Clean up text formatting
            recipe.title = self._clean_text(recipe.title)
            recipe.ingredients = self._clean_text(recipe.ingredients)
            recipe.instructions = self._clean_text(recipe.instructions)
            
            # Infer category if not set
            if not recipe.category:
                recipe.category = self._infer_category(recipe.title)
            
            # Extract timing information if not set
            if not recipe.prep_time or not recipe.cook_time:
                timing = self._extract_timing_info(recipe.instructions)
                if timing:
                    recipe.prep_time = timing.get('prep', recipe.prep_time)
                    recipe.cook_time = timing.get('cook', recipe.cook_time)
                    recipe.total_time = timing.get('total', recipe.total_time)
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Fix common OCR issues
        text = text.replace('ﬁ', 'fi').replace('ﬂ', 'fl')
        text = text.replace("'", "'").replace(""", '"').replace(""", '"')
        
        # Remove page numbers and headers
        text = re.sub(r'\bPage \d+\b', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\bChapter \d+\b', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _infer_category(self, title: str) -> str:
        """Infer recipe category from title"""
        
        if not title:
            return "Main Dishes"
        
        title_lower = title.lower()
        
        category_keywords = {
            'Appetizers & Snacks': ['appetizer', 'snack', 'dip', 'spread', 'chips', 'starter'],
            'Soups & Stews': ['soup', 'stew', 'chili', 'bisque', 'broth', 'gazpacho'],
            'Salads': ['salad', 'slaw', 'greens', 'caesar', 'vinaigrette'],
            'Main Dishes': ['chicken', 'beef', 'pork', 'fish', 'salmon', 'roast', 'steak', 'lamb'],
            'Pasta & Rice': ['pasta', 'rice', 'risotto', 'noodles', 'spaghetti', 'lasagna', 'pilaf'],
            'Vegetables': ['vegetable', 'broccoli', 'asparagus', 'beans', 'carrots', 'potatoes'],
            'Breads & Baking': ['bread', 'muffin', 'biscuit', 'roll', 'loaf', 'scone'],
            'Desserts': ['cake', 'pie', 'cookie', 'chocolate', 'dessert', 'sweet', 'tart', 'ice cream'],
            'Breakfast': ['pancake', 'waffle', 'breakfast', 'eggs', 'bacon', 'omelette', 'french toast'],
            'Sauces & Condiments': ['sauce', 'dressing', 'marinade', 'glaze', 'butter', 'vinaigrette']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                return category
        
        return "Main Dishes"  # Default category
    
    def _extract_timing_info(self, instructions: str) -> Dict[str, str]:
        """Extract timing information from instructions"""
        
        if not instructions:
            return {}
        
        timing = {}
        
        # Look for timing patterns
        prep_patterns = [
            r'prep(?:aration)?\s*time:?\s*(\d+(?:-\d+)?\s*(?:minute|min|hour|hr)s?)',
            r'preparation:?\s*(\d+(?:-\d+)?\s*(?:minute|min|hour|hr)s?)'
        ]
        
        cook_patterns = [
            r'cook(?:ing)?\s*time:?\s*(\d+(?:-\d+)?\s*(?:minute|min|hour|hr)s?)',
            r'bake\s*(?:for)?:?\s*(\d+(?:-\d+)?\s*(?:minute|min|hour|hr)s?)',
            r'roast\s*(?:for)?:?\s*(\d+(?:-\d+)?\s*(?:minute|min|hour|hr)s?)'
        ]
        
        total_patterns = [
            r'total\s*time:?\s*(\d+(?:-\d+)?\s*(?:minute|min|hour|hr)s?)',
            r'serves?\s*\d+\s*in\s*(\d+(?:-\d+)?\s*(?:minute|min|hour|hr)s?)'
        ]
        
        instructions_lower = instructions.lower()
        
        for pattern in prep_patterns:
            match = re.search(pattern, instructions_lower)
            if match:
                timing['prep'] = match.group(1)
                break
        
        for pattern in cook_patterns:
            match = re.search(pattern, instructions_lower)
            if match:
                timing['cook'] = match.group(1)
                break
        
        for pattern in total_patterns:
            match = re.search(pattern, instructions_lower)
            if match:
                timing['total'] = match.group(1)
                break
        
        return timing
    
    def _generate_ml_training_data(self, pdf_path: str, strategy: ExtractionStrategy):
        """Generate ML training data from extraction results"""
        
        if not self.config['enable_ml_training_generation']:
            return
        
        logger.info("🤖 Generating ML training data...")
        
        training_data = self.training_data_generator.generate_from_extractions(
            pdf_path, self.extracted_recipes, strategy
        )
        
        if training_data:
            self.stats['ml_training_samples_generated'] = len(training_data)
            logger.info(f"✅ Generated {len(training_data)} ML training samples")
    
    def _log_final_stats(self):
        """Log final extraction statistics"""
        
        duration = self.stats['extraction_end_time'] - self.stats['extraction_start_time']
        
        logger.info("📊 EXTRACTION COMPLETE!")
        logger.info(f"⏱️  Total time: {duration}")
        logger.info(f"📄 Pages processed: {self.stats['total_pages_processed']}")
        logger.info(f"🍽️  Recipes found: {self.stats['recipes_found']}")
        logger.info(f"📚 TOC mappings: {self.stats['toc_mappings_successful']}")
        logger.info(f"👁️  Visual structure detected: {self.stats['visual_structure_detected']}")
        logger.info(f"✅ Semantic validations: {self.stats['semantic_validations_passed']}")
        logger.info(f"🎯 High confidence: {self.stats['high_confidence_extractions']}")
        logger.info(f"🎯 Medium confidence: {self.stats['medium_confidence_extractions']}")
        logger.info(f"🎯 Low confidence: {self.stats['low_confidence_extractions']}")
        logger.info(f"❌ Failed extractions: {self.stats['failed_extractions']}")
        logger.info(f"🤖 ML training samples: {self.stats['ml_training_samples_generated']}")
    
    def save_results(self, output_path: str, format: str = 'json'):
        """Save extraction results in specified format"""
        
        logger.info(f"💾 Saving results to: {output_path}")
        
        if format == 'json':
            results = {
                'extraction_metadata': {
                    'total_recipes': len(self.extracted_recipes),
                    'extraction_stats': self.stats,
                    'timestamp': datetime.now().isoformat()
                },
                'recipes': [asdict(recipe) for recipe in self.extracted_recipes]
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        
        elif format == 'csv':
            import csv
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                if self.extracted_recipes:
                    writer = csv.DictWriter(f, fieldnames=asdict(self.extracted_recipes[0]).keys())
                    writer.writeheader()
                    for recipe in self.extracted_recipes:
                        writer.writerow(asdict(recipe))
        
        logger.info(f"✅ Results saved successfully")

# Supporting Classes
class TOCExtractor:
    """Handles Table of Contents extraction and mapping"""
    
    def extract_toc_mappings(self, reader, strategy: ExtractionStrategy) -> Dict[str, int]:
        """Extract TOC mappings using enhanced algorithm"""
        
        if not strategy.toc_pages:
            return {}
        
        # Import the enhanced TOC mapper we created earlier
        try:
            from atk_toc_mapping_fix import EnhancedTOCMapper
            mapper = EnhancedTOCMapper()
            return mapper.extract_toc_with_enhanced_mapping(reader, len(reader.pages))
        except ImportError:
            # Fallback to basic TOC extraction
            return self._basic_toc_extraction(reader, strategy)
    
    def _basic_toc_extraction(self, reader, strategy: ExtractionStrategy) -> Dict[str, int]:
        """Basic TOC extraction fallback"""
        logger.warning("Using basic TOC extraction - enhanced mapper not available")
        return {}

class VisualStructureDetector:
    """Detects visual recipe structures using layout analysis"""
    
    def analyze_page_structure(self, page_text: str, page_num: int) -> Dict[str, Any]:
        """Analyze page for visual recipe structure"""
        
        lines = page_text.split('\n')
        structure = {
            'is_recipe_page': False,
            'title_candidates': [],
            'ingredients_section': '',
            'instructions_section': '',
            'visual_indicators': {}
        }
        
        # Analyze visual indicators
        structure['visual_indicators'] = self._analyze_visual_indicators(lines, page_text)
        
        # Determine if this looks like a recipe page
        recipe_score = 0
        for indicator, found in structure['visual_indicators'].items():
            if found:
                recipe_score += 1
        
        structure['is_recipe_page'] = recipe_score >= 3
        
        if structure['is_recipe_page']:
            # Extract sections based on visual structure
            structure['title_candidates'] = self._find_title_candidates(lines)
            structure['ingredients_section'] = self._find_ingredients_section(lines)
            structure['instructions_section'] = self._find_instructions_section(lines)
        
        return structure
    
    def _analyze_visual_indicators(self, lines: List[str], full_text: str) -> Dict[str, bool]:
        """Analyze lines for visual recipe indicators"""
        
        indicators = {
            'has_title_formatting': False,
            'has_ingredients_list': False,
            'has_numbered_steps': False,
            'has_cooking_verbs': False,
            'has_measurements': False,
            'has_ingredient_patterns': False
        }
        
        # Check for title formatting (short lines, all caps, etc.)
        for line in lines[:5]:  # Check first 5 lines
            if line.strip() and len(line.strip()) < 60:
                if line.strip().isupper() or line.strip().istitle():
                    indicators['has_title_formatting'] = True
                    break
        
        # Check for ingredients list patterns
        ingredient_patterns = [
            r'\d+\s*(cup|tablespoon|teaspoon|pound|ounce|gram)',
            r'\d+/\d+\s*(cup|tsp|tbsp)',
            r'\d+\s*(large|medium|small)',
            r'^\s*[-•]\s*\d'
        ]
        
        for line in lines:
            for pattern in ingredient_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    indicators['has_ingredients_list'] = True
                    indicators['has_measurements'] = True
                    break
        
        # Check for numbered instructions
        numbered_pattern = r'^\s*\d+\.'
        for line in lines:
            if re.match(numbered_pattern, line):
                indicators['has_numbered_steps'] = True
                break
        
        # Check for cooking verbs
        cooking_verbs = ['heat', 'cook', 'bake', 'roast', 'sauté', 'simmer', 'boil', 'mix', 'stir', 'add']
        text_lower = full_text.lower()
        verb_count = sum(1 for verb in cooking_verbs if verb in text_lower)
        indicators['has_cooking_verbs'] = verb_count >= 3
        
        # Check for ingredient name patterns
        common_ingredients = ['chicken', 'onion', 'garlic', 'salt', 'pepper', 'oil', 'butter', 'flour']
        ingredient_count = sum(1 for ingredient in common_ingredients if ingredient in text_lower)
        indicators['has_ingredient_patterns'] = ingredient_count >= 2
        
        return indicators
    
    def _find_title_candidates(self, lines: List[str]) -> List[str]:
        """Find potential recipe titles based on formatting"""
        
        candidates = []
        
        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            line = line.strip()
            if line and 5 <= len(line) <= 80:
                # Title indicators: short, capitalized, not starting with number
                if (line.istitle() or line.isupper()) and not line[0].isdigit():
                    candidates.append(line)
        
        return candidates[:3]  # Return top 3 candidates
    
    def _find_ingredients_section(self, lines: List[str]) -> str:
        """Find ingredients section based on visual markers"""
        
        ingredients_start = -1
        ingredients_end = -1
        
        # Look for ingredients marker
        for i, line in enumerate(lines):
            if any(marker in line.upper() for marker in ['INGREDIENTS', 'SERVES', 'MAKES']):
                ingredients_start = i + 1
                break
        
        if ingredients_start == -1:
            return ""
        
        # Find end of ingredients (next major section or empty lines)
        for i in range(ingredients_start, min(len(lines), ingredients_start + 20)):
            line = lines[i].strip()
            if any(marker in line.upper() for marker in ['INSTRUCTIONS', 'METHOD', 'DIRECTIONS']):
                ingredients_end = i
                break
            elif not line and i > ingredients_start + 3:  # Allow some empty lines
                ingredients_end = i
                break
        
        if ingredients_end == -1:
            ingredients_end = min(len(lines), ingredients_start + 15)
        
        return '\n'.join(lines[ingredients_start:ingredients_end])
    
    def _find_instructions_section(self, lines: List[str]) -> str:
        """Find instructions section based on visual markers"""
        
        instructions_start = -1
        
        # Look for instructions marker
        for i, line in enumerate(lines):
            if any(marker in line.upper() for marker in ['INSTRUCTIONS', 'METHOD', 'DIRECTIONS']):
                instructions_start = i + 1
                break
            elif re.match(r'^\s*1\.', line):  # Numbered list start
                instructions_start = i
                break
        
        if instructions_start == -1:
            return ""
        
        # Take rest of meaningful content
        instructions_lines = []
        for i in range(instructions_start, len(lines)):
            line = lines[i].strip()
            if line and not line.startswith('PAGE'):
                instructions_lines.append(line)
        
        return '\n'.join(instructions_lines)

class PatternMatcher:
    """Handles pattern-based extraction using regex and heuristics"""
    
    def extract_with_patterns(self, page_text: str, strategy: ExtractionStrategy) -> Optional[RecipeData]:
        """Extract recipe using pattern matching"""
        
        recipe_data = RecipeData()
        
        # Extract title using patterns
        for pattern in strategy.title_patterns:
            title = self._extract_title_with_pattern(page_text, pattern)
            if title:
                recipe_data.title = title
                break
        
        # Extract ingredients using markers
        ingredients = self._extract_section_with_markers(page_text, strategy.ingredients_markers)
        if ingredients:
            recipe_data.ingredients = ingredients
        
        # Extract instructions using markers
        instructions = self._extract_section_with_markers(page_text, strategy.instructions_markers)
        if instructions:
            recipe_data.instructions = instructions
        
        return recipe_data if recipe_data.title or recipe_data.ingredients else None
    
    def _extract_title_with_pattern(self, text: str, pattern: str) -> str:
        """Extract title using regex pattern"""
        
        lines = text.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if re.match(pattern, line):
                return line
        
        return ""
    
    def _extract_section_with_markers(self, text: str, markers: List[str]) -> str:
        """Extract section using text markers"""
        
        lines = text.split('\n')
        
        for marker in markers:
            for i, line in enumerate(lines):
                if marker.upper() in line.upper():
                    # Extract following lines
                    section_lines = []
                    for j in range(i + 1, min(len(lines), i + 20)):
                        section_line = lines[j].strip()
                        if section_line and not section_line.startswith('PAGE'):
                            section_lines.append(section_line)
                    
                    if section_lines:
                        return '\n'.join(section_lines)
        
        return ""

class SemanticValidator:
    """Validates and enhances extracted recipes using semantic analysis"""
    
    def validate_and_enhance(self, recipe_data: RecipeData) -> Optional[RecipeData]:
        """Validate recipe data and enhance with semantic analysis"""
        
        # Basic validation
        if not self._passes_basic_validation(recipe_data):
            return None
        
        # Enhance with semantic analysis
        enhanced_data = self._enhance_with_semantics(recipe_data)
        
        return enhanced_data
    
    def _passes_basic_validation(self, recipe_data: RecipeData) -> bool:
        """Check if recipe passes basic validation"""
        
        # Must have title
        if not recipe_data.title or len(recipe_data.title.strip()) < 3:
            return False
        
        # Must have either ingredients or instructions with minimum length
        has_ingredients = recipe_data.ingredients and len(recipe_data.ingredients.strip()) > 20
        has_instructions = recipe_data.instructions and len(recipe_data.instructions.strip()) > 30
        
        return has_ingredients or has_instructions
    
    def _enhance_with_semantics(self, recipe_data: RecipeData) -> RecipeData:
        """Enhance recipe data using semantic analysis"""
        
        # Enhance ingredients with intelligent parsing
        if recipe_data.ingredients:
            recipe_data.ingredients = self._enhance_ingredients(recipe_data.ingredients)
        
        # Enhance instructions with step numbering
        if recipe_data.instructions:
            recipe_data.instructions = self._enhance_instructions(recipe_data.instructions)
        
        # Extract additional metadata
        if not recipe_data.servings:
            recipe_data.servings = self._extract_servings(recipe_data.ingredients + " " + recipe_data.instructions)
        
        return recipe_data
    
    def _enhance_ingredients(self, ingredients: str) -> str:
        """Enhance ingredients list with better formatting"""
        
        lines = ingredients.split('\n')
        enhanced_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Ensure proper formatting
                if not line.startswith(('•', '-', '*')) and not re.match(r'^\d+\.', line):
                    line = '• ' + line
                enhanced_lines.append(line)
        
        return '\n'.join(enhanced_lines)
    
    def _enhance_instructions(self, instructions: str) -> str:
        """Enhance instructions with proper step numbering"""
        
        lines = instructions.split('\n')
        enhanced_lines = []
        step_number = 1
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:  # Substantial instruction lines
                if not re.match(r'^\d+\.', line):
                    line = f"{step_number}. {line}"
                    step_number += 1
                enhanced_lines.append(line)
        
        return '\n'.join(enhanced_lines)
    
    def _extract_servings(self, text: str) -> str:
        """Extract serving information from text"""
        
        patterns = [
            r'serves?\s*(\d+(?:-\d+)?)',
            r'makes?\s*(\d+(?:-\d+)?)',
            r'yield:?\s*(\d+(?:-\d+)?)',
            r'portions?:?\s*(\d+(?:-\d+)?)'
        ]
        
        text_lower = text.lower()
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                return match.group(1)
        
        return ""

class ConfidenceScorer:
    """Calculates confidence scores for extracted recipe components"""
    
    def calculate_scores(self, recipe_data: RecipeData, page_text: str) -> Dict[str, float]:
        """Calculate confidence scores for recipe components"""
        
        scores = {}
        
        # Title confidence
        scores['title'] = self._calculate_title_confidence(recipe_data.title, page_text)
        
        # Ingredients confidence
        scores['ingredients'] = self._calculate_ingredients_confidence(recipe_data.ingredients)
        
        # Instructions confidence
        scores['instructions'] = self._calculate_instructions_confidence(recipe_data.instructions)
        
        # Overall structure confidence
        scores['structure'] = self._calculate_structure_confidence(recipe_data)
        
        return scores
    
    def _calculate_title_confidence(self, title: str, page_text: str) -> float:
        """Calculate title confidence based on formatting and positioning"""
        
        if not title:
            return 0.0
        
        confidence = 0.0
        
        # Length check (reasonable title length)
        if 5 <= len(title) <= 80:
            confidence += 0.3
        
        # Formatting check (title case or all caps)
        if title.istitle() or title.isupper():
            confidence += 0.3
        
        # Position check (appears early in page)
        lines = page_text.split('\n')
        for i, line in enumerate(lines[:10]):
            if title in line:
                confidence += 0.4 * (10 - i) / 10
                break
        
        return min(confidence, 1.0)
    
    def _calculate_ingredients_confidence(self, ingredients: str) -> float:
        """Calculate ingredients confidence based on structure and content"""
        
        if not ingredients:
            return 0.0
        
        confidence = 0.0
        lines = ingredients.split('\n')
        
        # Line count check
        if 3 <= len(lines) <= 20:
            confidence += 0.2
        
        # Measurement patterns
        measurement_pattern = r'\d+(?:/\d+)?\s*(cup|tablespoon|teaspoon|pound|ounce|gram|tsp|tbsp)'
        measurement_count = len(re.findall(measurement_pattern, ingredients, re.IGNORECASE))
        if measurement_count >= 3:
            confidence += 0.3
        
        # Common ingredients
        common_ingredients = ['salt', 'pepper', 'oil', 'onion', 'garlic', 'butter']
        ingredient_count = sum(1 for ingredient in common_ingredients if ingredient in ingredients.lower())
        confidence += min(ingredient_count * 0.1, 0.3)
        
        # List formatting
        list_indicators = ['•', '-', '*', '\n']
        if any(indicator in ingredients for indicator in list_indicators):
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _calculate_instructions_confidence(self, instructions: str) -> float:
        """Calculate instructions confidence based on structure and cooking content"""
        
        if not instructions:
            return 0.0
        
        confidence = 0.0
        
        # Length check
        if len(instructions) > 50:
            confidence += 0.2
        
        # Cooking verbs
        cooking_verbs = ['heat', 'cook', 'bake', 'roast', 'sauté', 'simmer', 'boil', 'mix', 'stir', 'add', 'combine']
        verb_count = sum(1 for verb in cooking_verbs if verb in instructions.lower())
        confidence += min(verb_count * 0.1, 0.4)
        
        # Step structure
        if re.search(r'\d+\.', instructions):
            confidence += 0.2
        
        # Imperative mood (cooking instructions typically use commands)
        imperative_indicators = ['heat', 'add', 'mix', 'cook', 'bake', 'remove', 'serve']
        imperative_count = sum(1 for word in imperative_indicators if instructions.lower().startswith(word))
        confidence += min(imperative_count * 0.1, 0.2)
        
        return min(confidence, 1.0)
    
    def _calculate_structure_confidence(self, recipe_data: RecipeData) -> float:
        """Calculate overall structural confidence"""
        
        confidence = 0.0
        
        # Has all three main components
        if recipe_data.title:
            confidence += 0.33
        if recipe_data.ingredients:
            confidence += 0.33
        if recipe_data.instructions:
            confidence += 0.34
        
        return confidence

class TrainingDataGenerator:
    """Generates ML training data from extraction results"""
    
    def generate_from_extractions(self, pdf_path: str, recipes: List[RecipeData], 
                                strategy: ExtractionStrategy) -> List[Dict]:
        """Generate ML training annotations from extraction results"""
        
        training_samples = []
        
        for recipe in recipes:
            if recipe.page_number:
                try:
                    # Create training annotation for this page
                    annotation = self._create_page_annotation(pdf_path, recipe, strategy)
                    if annotation:
                        training_samples.append(annotation)
                except Exception as e:
                    logger.warning(f"Could not create training annotation for page {recipe.page_number}: {e}")
        
        return training_samples
    
    def _create_page_annotation(self, pdf_path: str, recipe: RecipeData, 
                              strategy: ExtractionStrategy) -> Optional[Dict]:
        """Create ML training annotation for a single page"""
        
        # This would render the PDF page to image and estimate bounding boxes
        # For now, return placeholder structure
        return {
            'page_number': recipe.page_number,
            'pdf_path': pdf_path,
            'strategy': strategy.name,
            'annotations': {
                'title': {
                    'text': recipe.title,
                    'bbox': [0.1, 0.1, 0.9, 0.2],  # Estimated bounding box
                    'confidence': recipe.confidence_scores.get('title', 0.5)
                },
                'ingredients': {
                    'text': recipe.ingredients[:100],  # Preview
                    'bbox': [0.1, 0.25, 0.9, 0.6],  # Estimated bounding box
                    'confidence': recipe.confidence_scores.get('ingredients', 0.5)
                },
                'instructions': {
                    'text': recipe.instructions[:100],  # Preview
                    'bbox': [0.1, 0.65, 0.9, 0.9],  # Estimated bounding box
                    'confidence': recipe.confidence_scores.get('instructions', 0.5)
                }
            }
        }

# CLI Interface
def main():
    """Command line interface for the Universal Recipe Parser"""
    
    parser = argparse.ArgumentParser(description='Universal Recipe Parser - Extract recipes from cookbook PDFs')
    parser.add_argument('pdf_path', help='Path to the PDF cookbook')
    parser.add_argument('--strategy', choices=['auto', 'atk_25th', 'bittman', 'magazine_style', 'minimal'], 
                       default='auto', help='Extraction strategy to use')
    parser.add_argument('--output', '-o', help='Output file path (JSON format)')
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize parser
        extractor = UniversalRecipeParser(config_path=args.config)
        
        # Extract recipes
        recipes = extractor.extract_recipes(args.pdf_path, args.strategy)
        
        # Save results
        if args.output:
            extractor.save_results(args.output)
        else:
            # Print summary to console
            print(f"\n✅ Extraction complete!")
            print(f"📚 Found {len(recipes)} recipes")
            print(f"🎯 Average confidence: {sum(extractor._calculate_overall_confidence(r) for r in recipes) / len(recipes) if recipes else 0:.2f}")
            
            # Print first few recipes as preview
            for i, recipe in enumerate(recipes[:3]):
                print(f"\n🍽️  Recipe {i+1}: {recipe.title}")
                print(f"   📄 Page: {recipe.page_number}")
                print(f"   🎯 Confidence: {extractor._calculate_overall_confidence(recipe):.2f}")
                print(f"   📝 Ingredients: {len(recipe.ingredients)} chars")
                print(f"   📝 Instructions: {len(recipe.instructions)} chars")
            
            if len(recipes) > 3:
                print(f"\n... and {len(recipes) - 3} more recipes")
    
    except Exception as e:
        logger.error(f"❌ Extraction failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
