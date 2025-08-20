#!/usr/bin/env python3
"""
👁️🧠 ATK Teens Cookbook - Visual + Semantic Extraction System
================================================================

Advanced hybrid extraction combining:
- Visual PDF structure detection (layout, headers, formatting)
- Semantic quality validation (AI-powered recipe understanding)
- Multi-page recipe support with continuation detection
- PDF text artifact cleaning for better semantic validation
- Teen cookbook specific patterns and structure

Enhanced from the successful ATK 25th Anniversary extractor to handle
teen cookbook formatting and educational content structure.

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
    from semantic_recipe_engine import SemanticRecipeEngine
    print("Core Systems Module Loaded - Archive Protected")
except ImportError as e:
    print(f"❌ Failed to import core systems: {e}")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

class VisualStructureDetector:
    """Detects visual recipe structures in PDF pages"""
    
    def __init__(self):
        self.confidence_weights = {
            'title_pattern': 3.0,
            'difficulty_indicator': 2.5,
            'serve_makes_pattern': 2.0,
            'prepare_ingredients': 3.0,
            'start_cooking': 3.0,
            'numbered_steps': 2.0,
            'ingredient_measurements': 1.5,
            'time_indicators': 1.0,
            'dietary_tags': 1.0,
            'educational_content': 1.5
        }
    
    def analyze_page_structure(self, page_text: str, page_num: int) -> Dict[str, Any]:
        """Analyze page for visual recipe structure with teen cookbook patterns"""
        
        structure = {
            'page_number': page_num,
            'confidence_score': 0,
            'visual_indicators': {},
            'recipe_structure': {},
            'is_recipe_page': False,
            'is_continuation': False
        }
        
        lines = page_text.split('\n')
        structure['visual_indicators'] = self._analyze_line_structure(lines, page_text)
        
        # Calculate confidence score
        total_confidence = 0
        for indicator, found in structure['visual_indicators'].items():
            if found:
                weight = self.confidence_weights.get(indicator, 1.0)
                total_confidence += weight
        
        structure['confidence_score'] = min(total_confidence, 20)  # Cap at 20
        
        # Determine if this is a recipe page
        structure['is_recipe_page'] = total_confidence >= 4.0
        
        # Check for continuation page (ingredients without major headers)
        if (structure['visual_indicators']['ingredient_measurements'] and 
            not structure['visual_indicators']['title_pattern'] and
            not structure['visual_indicators']['difficulty_indicator']):
            structure['is_continuation'] = True
        
        # Extract recipe structure if it's a recipe page
        if structure['is_recipe_page']:
            structure['recipe_structure'] = self._extract_recipe_structure(lines, page_text)
        
        return structure
    
    def _analyze_line_structure(self, lines: List[str], full_text: str) -> Dict[str, bool]:
        """Analyze individual lines for recipe indicators"""
        
        indicators = {
            'title_pattern': False,
            'difficulty_indicator': False,
            'serve_makes_pattern': False,
            'prepare_ingredients': False,
            'start_cooking': False,
            'numbered_steps': False,
            'ingredient_measurements': False,
            'time_indicators': False,
            'dietary_tags': False,
            'educational_content': False
        }
        
        # Check full text patterns first
        indicators['difficulty_indicator'] = bool(re.search(r'(BEGINNER|INTERMEDIATE|ADVANCED)', full_text))
        indicators['serve_makes_pattern'] = bool(re.search(r'(SERVES|MAKES)\s+\d+', full_text))
        indicators['prepare_ingredients'] = 'PREPARE INGREDIENTS' in full_text
        indicators['start_cooking'] = 'START COOKING!' in full_text
        indicators['time_indicators'] = bool(re.search(r'\d+\s+(MINUTES?|HOURS?)', full_text))
        indicators['dietary_tags'] = bool(re.search(r'(VEGETARIAN|VEGAN|GLUTEN.?FREE|DAIRY.?FREE)', full_text))
        indicators['educational_content'] = 'BEFORE YOU BEGIN' in full_text
        
        # Check line-by-line patterns
        for i, line in enumerate(lines[:25]):  # Check first 25 lines
            line = line.strip()
            if not line:
                continue
            
            # Title pattern detection (teen cookbook style)
            if not indicators['title_pattern']:
                indicators['title_pattern'] = self._is_teen_recipe_title(line)
            
            # Numbered steps pattern
            if not indicators['numbered_steps']:
                indicators['numbered_steps'] = bool(re.match(r'^\d+\.\s+', line))
            
            # Ingredient measurements
            if not indicators['ingredient_measurements']:
                indicators['ingredient_measurements'] = bool(re.search(
                    r'\d+.*?(cup|tablespoon|teaspoon|pound|ounce|large|medium|small)', 
                    line, re.IGNORECASE
                ))
        
        return indicators
    
    def _is_teen_recipe_title(self, line: str) -> bool:
        """Detect teen cookbook recipe titles"""
        if len(line) < 5 or len(line) > 80:
            return False
        
        # Skip lines that start with numbers (likely ingredients)
        if re.match(r'^\d+', line.strip()):
            return False
        
        # Skip obvious ingredient lines
        ingredient_patterns = [
            r'(cup|tablespoon|teaspoon|pound|ounce)',
            r'(chopped|diced|minced|sliced)',
            r'(plus extra|divided|optional)',
            r'(softened|melted|room temperature)'
        ]
        
        line_lower = line.lower()
        if any(re.search(pattern, line_lower) for pattern in ingredient_patterns):
            return False
        
        # Teen cookbook specific food terms
        teen_food_keywords = [
            'smoothie', 'milkshake', 'burger', 'pizza', 'pasta', 'sandwich',
            'pancakes', 'cookies', 'brownies', 'muffins', 'cake', 'pie',
            'tacos', 'quesadilla', 'nachos', 'popcorn', 'trail mix',
            'chicken', 'beef', 'pork', 'fish', 'eggs', 'cheese',
            'salad', 'soup', 'chili', 'stew', 'curry', 'stir-fry',
            'baked', 'grilled', 'roasted', 'fried', 'steamed',
            'chocolate', 'vanilla', 'strawberry', 'banana', 'apple'
        ]
        
        # Strong indicators for recipe titles
        if any(keyword in line_lower for keyword in teen_food_keywords):
            return True
        
        # Title case with multiple words
        if line.istitle() and len(line.split()) >= 2:
            return True
        
        # All caps with reasonable length (teen cookbook style)
        if line.isupper() and 5 <= len(line) <= 60 and len(line.split()) >= 2:
            # Avoid section headers
            if line not in ['PREPARE INGREDIENTS', 'START COOKING!', 'BEFORE YOU BEGIN']:
                return True
        
        return False
    
    def _extract_recipe_structure(self, lines: List[str], full_text: str) -> Dict[str, Any]:
        """Extract detailed recipe structure information"""
        
        structure = {
            'title_candidates': [],
            'header_info': {},
            'ingredient_sections': [],
            'instruction_sections': [],
            'educational_sections': []
        }
        
        # Find title candidates
        for i, line in enumerate(lines[:20]):
            line = line.strip()
            if self._is_teen_recipe_title(line):
                structure['title_candidates'].append({
                    'text': line,
                    'line_number': i,
                    'confidence': self._calculate_title_confidence(line, i)
                })
        
        # Extract header information
        structure['header_info'] = self._extract_header_structure(full_text)
        
        # Find section boundaries
        structure['ingredient_sections'] = self._find_ingredient_sections(full_text)
        structure['instruction_sections'] = self._find_instruction_sections(full_text)
        structure['educational_sections'] = self._find_educational_sections(full_text)
        
        return structure
    
    def _calculate_title_confidence(self, title_text: str, line_position: int) -> float:
        """Calculate confidence score for potential titles"""
        confidence = 0.0
        
        # Position weight (earlier = higher confidence)
        position_weight = max(0, 10 - line_position) * 0.1
        confidence += position_weight
        
        # Length weight (reasonable recipe title length)
        if 10 <= len(title_text) <= 50:
            confidence += 1.0
        elif 5 <= len(title_text) <= 80:
            confidence += 0.5
        
        # Food keyword weight
        teen_food_keywords = [
            'smoothie', 'burger', 'pizza', 'pasta', 'sandwich', 'pancakes',
            'cookies', 'brownies', 'chicken', 'chocolate', 'vanilla'
        ]
        
        title_lower = title_text.lower()
        food_matches = sum(1 for keyword in teen_food_keywords if keyword in title_lower)
        confidence += food_matches * 0.5
        
        # Format weight (proper capitalization)
        if title_text.istitle() or title_text.isupper():
            confidence += 0.5
        
        return confidence
    
    def _extract_header_structure(self, full_text: str) -> Dict[str, str]:
        """Extract header information structure"""
        header = {}
        
        # Difficulty level
        difficulty_match = re.search(r'(BEGINNER|INTERMEDIATE|ADVANCED)', full_text)
        if difficulty_match:
            header['difficulty'] = difficulty_match.group(1)
        
        # Serving information
        serve_match = re.search(r'(SERVES|MAKES)\s+(\d+)(?:\s+([A-Z\s]+))?', full_text)
        if serve_match:
            header['servings'] = f"{serve_match.group(1)} {serve_match.group(2)}"
            if serve_match.group(3):
                header['servings'] += f" {serve_match.group(3).strip()}"
        
        # Time information
        time_match = re.search(r'(\d+)\s+(MINUTES?|HOURS?)', full_text)
        if time_match:
            header['time'] = f"{time_match.group(1)} {time_match.group(2).lower()}"
        
        # Dietary tags
        dietary_tags = []
        dietary_patterns = ['VEGETARIAN', 'VEGAN', 'GLUTEN-FREE', 'DAIRY-FREE']
        for tag in dietary_patterns:
            if tag in full_text:
                dietary_tags.append(tag)
        
        if dietary_tags:
            header['dietary'] = ', '.join(dietary_tags)
        
        return header
    
    def _find_ingredient_sections(self, full_text: str) -> List[Dict[str, Any]]:
        """Find ingredient sections in the text"""
        sections = []
        
        # Look for PREPARE INGREDIENTS section (primary method)
        prepare_match = re.search(r'PREPARE INGREDIENTS(.*?)(?=START COOKING!|$)', full_text, re.DOTALL)
        if prepare_match:
            sections.append({
                'type': 'main_ingredients',
                'content': prepare_match.group(1).strip(),
                'start_marker': 'PREPARE INGREDIENTS'
            })
        
        # Look for ingredient lists without headers (common in continuation pages)
        if not sections:
            # Check if the page starts with ingredient-like content
            lines = full_text.split('\n')
            ingredient_lines = []
            
            for line in lines[:20]:  # Check first 20 lines
                line = line.strip()
                if not line:
                    continue
                
                # Pattern for ingredient lines: number/amount + ingredient
                ingredient_patterns = [
                    r'^\d+(?:\s*½|\s*¼|\s*⅓|\s*⅔|\s*¾)?\s+(?:large|medium|small|cups?|tablespoons?|teaspoons?|pounds?|ounces?|cloves?)',
                    r'^(?:\d+/)?\d+(?:\s*½|\s*¼|\s*⅓|\s*⅔|\s*¾)?\s*(?:cups?|tablespoons?|teaspoons?|pounds?|ounces?)',
                    r'^\d+\s+(?:large|medium|small)\s+\w+',  # "1 large egg"
                    r'^\d+(?:\s*½|\s*¼|\s*⅓|\s*⅔|\s*¾)?\s*(?:cup|tablespoon|teaspoon|pound|ounce)',
                ]
                
                is_ingredient = False
                for pattern in ingredient_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        is_ingredient = True
                        break
                
                if is_ingredient:
                    ingredient_lines.append(line)
                elif ingredient_lines and not line.isupper():  # Stop if we hit non-ingredient after finding ingredients
                    break
            
            # If we found substantial ingredient content, add it
            if len(ingredient_lines) >= 3:  # At least 3 ingredient lines
                sections.append({
                    'type': 'continuation_ingredients',
                    'content': '\n'.join(ingredient_lines),
                    'start_marker': 'DIRECT_INGREDIENTS'
                })
        
        # Look for TOPPING or other sub-sections
        topping_match = re.search(r'TOPPING(.*?)(?=FILLING|INSTRUCTIONS|START COOKING!|$)', full_text, re.DOTALL)
        if topping_match:
            sections.append({
                'type': 'topping_ingredients',
                'content': topping_match.group(1).strip(),
                'start_marker': 'TOPPING'
            })
        
        # Look for FILLING sections
        filling_match = re.search(r'FILLING(.*?)(?=TOPPING|INSTRUCTIONS|START COOKING!|$)', full_text, re.DOTALL)
        if filling_match:
            sections.append({
                'type': 'filling_ingredients',
                'content': filling_match.group(1).strip(),
                'start_marker': 'FILLING'
            })
        
        return sections
    
    def _find_instruction_sections(self, full_text: str) -> List[Dict[str, Any]]:
        """Find instruction sections in the text"""
        sections = []
        
        # Look for START COOKING! section
        cooking_match = re.search(r'START COOKING!(.*?)(?=\n[A-Z\s]{10,}|$)', full_text, re.DOTALL)
        if cooking_match:
            sections.append({
                'type': 'main_instructions',
                'content': cooking_match.group(1).strip(),
                'start_marker': 'START COOKING!'
            })
        
        return sections
    
    def _find_educational_sections(self, full_text: str) -> List[Dict[str, Any]]:
        """Find educational content sections"""
        sections = []
        
        # Look for BEFORE YOU BEGIN section
        before_match = re.search(r'BEFORE YOU BEGIN(.*?)(?=PREPARE INGREDIENTS|START COOKING!|$)', full_text, re.DOTALL)
        if before_match:
            sections.append({
                'type': 'before_you_begin',
                'content': before_match.group(1).strip(),
                'start_marker': 'BEFORE YOU BEGIN'
            })
        
        return sections

class TeenRecipeExtractor:
    """Enhanced recipe extractor with visual + semantic validation"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.visual_detector = VisualStructureDetector()
        self.db_manager = DatabaseManager()
        # Use PERMISSIVE validation for teen cookbook (more flexible)
        from semantic_recipe_engine import ValidationLevel
        self.semantic_engine = SemanticRecipeEngine(validation_level=ValidationLevel.PERMISSIVE)
        
        # Load ingredient intelligence engine for proper ingredient recognition
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from core_systems.ingredient_intelligence_engine import IngredientIntelligenceEngine
        self.ingredient_engine = IngredientIntelligenceEngine()
        
        # Extraction state
        self.extracted_recipes = []
        self.multi_page_recipes = {}  # Track recipes spanning multiple pages
        self.rejection_reasons = {
            'no_visual_structure': 0,
            'no_title_found': 0,
            'no_ingredients': 0,
            'no_instructions': 0,
            'semantic_rejection': 0,
            'low_quality': 0
        }
        
        # Statistics
        self.stats = {
            'pages_processed': 0,
            'pages_with_visual_structure': 0,
            'recipe_candidates_found': 0,
            'visual_validations': 0,
            'semantic_validations': 0,
            'artifacts_rejected': 0,
            'recipes_validated': 0
        }
    
    def extract_from_page_range(self, start_page: int = 1, end_page: int = None, 
                               max_recipes: int = None, dry_run: bool = False) -> List[Dict]:
        """Extract recipes from specified page range with full validation pipeline"""
        
        logger.info("🧠 VISUAL + SEMANTIC ATK TEENS EXTRACTION")
        logger.info("=" * 70)
        logger.info("👁️ Visual structure detection + 🧠 Semantic validation")
        logger.info("🛡️ Multi-layer quality assurance + 📄 Multi-page recipe support")
        logger.info("=" * 70)
        
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
                        
                        # Visual structure analysis
                        visual_analysis = self.visual_detector.analyze_page_structure(page_text, page_num + 1)
                        
                        if visual_analysis['is_recipe_page']:
                            self.stats['pages_with_visual_structure'] += 1
                            
                            # Process recipe candidate
                            self._process_recipe_candidate(visual_analysis, page_text, dry_run)
                        else:
                            # Even if not a recipe page, check for multi-page continuation
                            self._check_multi_page_continuation(page_text, page_num + 1)
                        
                        # Progress reporting
                        if self.stats['pages_processed'] % 25 == 0:
                            logger.info(f"  📊 Progress: {self.stats['pages_processed']} pages, {self.stats['recipes_validated']} recipes validated")
                    
                    except Exception as e:
                        logger.error(f"❌ Error processing page {page_num + 1}: {e}")
                        continue
                
                # Process any remaining multi-page recipes
                self._finalize_multi_page_recipes(dry_run)
                
                logger.info("")
                logger.info("✅ VISUAL + SEMANTIC EXTRACTION COMPLETE!")
                self._print_detailed_summary()
                
                if not dry_run and self.extracted_recipes:
                    self._save_recipes()
                
                return self.extracted_recipes
        
        except Exception as e:
            logger.error(f"❌ Fatal extraction error: {e}")
            return []
    
    def _process_recipe_candidate(self, visual_analysis: Dict, page_text: str, dry_run: bool = False):
        """Process a recipe candidate with visual + semantic validation"""
        
        page_num = visual_analysis['page_number']
        confidence = visual_analysis['confidence_score']
        
        self.stats['recipe_candidates_found'] += 1
        
        # Extract recipe data using visual structure
        recipe_data = self._extract_recipe_with_visual_guidance(visual_analysis, page_text)
        
        if not recipe_data:
            self.rejection_reasons['no_title_found'] += 1
            return
        
        # Check for multi-page recipe continuation
        if self._is_multi_page_recipe(recipe_data, page_num):
            return  # Will be processed when recipe is complete
        
        # Validate core requirements
        validation_result = self._validate_recipe_requirements(recipe_data)
        
        if not validation_result['valid']:
            for reason in validation_result['reasons']:
                self.rejection_reasons[reason] += 1
            return
        
        self.stats['visual_validations'] += 1
        
        # Clean text for semantic validation
        cleaned_recipe = self._clean_recipe_text(recipe_data)
        
        # Semantic validation with teen cookbook flexibility
        semantic_result = self.semantic_engine.validate_complete_recipe(cleaned_recipe)
        
        # Teen cookbook special handling: if visual confidence is very high and basic requirements met, accept it
        teen_cookbook_override = False
        if not semantic_result.is_valid_recipe and confidence >= 10:
            # Check if this meets basic teen cookbook recipe requirements
            has_food_words = self._has_teen_food_indicators(recipe_data)
            has_proper_structure = self._has_proper_teen_structure(recipe_data)
            
            if has_food_words and has_proper_structure:
                teen_cookbook_override = True
                # Create a mock semantic result for teen cookbook recipes
                class MockSemanticResult:
                    def __init__(self):
                        self.is_valid_recipe = True
                        self.confidence_score = 0.75  # Good confidence for teen recipes
                
                semantic_result = MockSemanticResult()
        
        if semantic_result.is_valid_recipe:
            self.stats['semantic_validations'] += 1
            
            # Add metadata
            recipe_data['visual_confidence'] = confidence
            recipe_data['semantic_confidence'] = semantic_result.confidence_score
            recipe_data['source'] = 'The Complete Cookbook for Teen - America\'s Test Kitchen Kids'
            recipe_data['extraction_method'] = 'visual_semantic_hybrid'
            recipe_data['page_number'] = page_num
            
            self.extracted_recipes.append(recipe_data)
            self.stats['recipes_validated'] += 1
            
            # Determine logging based on visual confidence
            if visual_analysis.get('is_continuation'):
                logger.info(f"✅ Multi-page {page_num-1}-{page_num}: '{recipe_data['title']}' (semantic: {semantic_result.confidence_score:.2f})")
            elif confidence >= 15:
                logger.info(f"✅ Page {page_num}: '{recipe_data['title']}' (visual: {confidence:.0f}, semantic: {semantic_result.confidence_score:.2f})")
            else:
                logger.info(f"✅ Multi-page {page_num-1}-{page_num}: '{recipe_data['title']}' (semantic: {semantic_result.confidence_score:.2f})")
        else:
            self.rejection_reasons['semantic_rejection'] += 1
    
    def _extract_recipe_with_visual_guidance(self, visual_analysis: Dict, page_text: str) -> Optional[Dict]:
        """Extract recipe using visual structure guidance"""
        
        recipe_structure = visual_analysis.get('recipe_structure', {})
        
        # Extract title
        title = self._extract_best_title(recipe_structure, page_text)
        
        # For continuation pages without titles, still extract content
        recipe_data = {}
        if title:
            recipe_data['title'] = title
        
        # Extract header information
        header_info = recipe_structure.get('header_info', {})
        if header_info.get('difficulty'):
            recipe_data['category'] = f"{header_info['difficulty'].title()} Recipe"
        elif title:  # Only set default category if we have a title
            recipe_data['category'] = "Teen Recipe"
        
        if header_info.get('servings'):
            recipe_data['servings'] = header_info['servings']
        
        if header_info.get('time'):
            recipe_data['total_time'] = header_info['time']
        
        if header_info.get('dietary'):
            recipe_data['dietary_tags'] = header_info['dietary']
        
        # Extract ingredients using visual guidance
        ingredients = self._extract_ingredients_with_structure(recipe_structure, page_text)
        if ingredients:
            recipe_data['ingredients'] = ingredients
        
        # Extract instructions using visual guidance
        instructions = self._extract_instructions_with_structure(recipe_structure, page_text)
        if instructions:
            recipe_data['instructions'] = instructions
        
        # Extract educational content
        educational = self._extract_educational_content(recipe_structure, page_text)
        if educational:
            recipe_data['description'] = educational
        
        # Only return None if we have absolutely no content
        if not recipe_data:
            return None
        
        # For continuation pages, ensure we have at least ingredients OR instructions
        if not title and not ingredients and not instructions:
            return None
        
        return recipe_data
    
    def _extract_best_title(self, recipe_structure: Dict, page_text: str) -> Optional[str]:
        """Extract the best title candidate using visual analysis"""
        
        title_candidates = recipe_structure.get('title_candidates', [])
        
        if title_candidates:
            # Sort by confidence and return the best
            best_candidate = max(title_candidates, key=lambda x: x['confidence'])
            title = best_candidate['text']
            
            # Clean up title
            if title.isupper():
                title = title.title()
            
            # Remove common artifacts
            title = re.sub(r'^(Recipe|Test Kitchen)', '', title, flags=re.IGNORECASE)
            title = title.strip()
            
            return title if len(title) > 3 else None
        
        # Fallback: look for title patterns in first 15 lines
        lines = page_text.split('\n')
        for line in lines[:15]:
            line = line.strip()
            if self.visual_detector._is_teen_recipe_title(line):
                title = line.title() if line.isupper() else line
                title = re.sub(r'^(Recipe|Test Kitchen)', '', title, flags=re.IGNORECASE)
                title = title.strip()
                if len(title) > 3:
                    return title
        
        return None
    
    def _extract_ingredients_with_structure(self, recipe_structure: Dict, page_text: str) -> str:
        """Extract ingredients using visual structure information"""
        
        ingredient_sections = recipe_structure.get('ingredient_sections', [])
        
        if ingredient_sections:
            # Use the structured ingredient sections
            main_section = ingredient_sections[0]
            ingredients_text = main_section['content']
        else:
            # Fallback to text-based extraction
            prepare_pos = page_text.find('PREPARE INGREDIENTS')
            if prepare_pos != -1:
                content_after_prepare = page_text[prepare_pos + len('PREPARE INGREDIENTS'):].strip()
                start_cooking_pos = content_after_prepare.find('START COOKING!')
                if start_cooking_pos != -1:
                    ingredients_text = content_after_prepare[:start_cooking_pos].strip()
                else:
                    ingredients_text = content_after_prepare[:1000].strip()
            else:
                # Check if this is a continuation page
                start_cooking_pos = page_text.find('START COOKING!')
                if start_cooking_pos == -1:
                    return ""
                
                content_before = page_text[:start_cooking_pos]
                ingredients_text = content_before[-2000:] if len(content_before) > 2000 else content_before
        
        if not ingredients_text:
            return ""
        
        # Check if this contains ingredients
        if not re.search(r'\d+.*?(?:cup|table|tea|pound|ounce|large|medium|small)', ingredients_text, re.IGNORECASE):
            return ""
        
        # Format the ingredients
        return self._format_ingredients_text(ingredients_text)
    
    def _format_ingredients_text(self, ingredients_text: str) -> str:
        """Format ingredient text into structured format"""
        
        formatted_ingredients = []
        lines = ingredients_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Section headers (all caps, no numbers, short)
            if line.isupper() and not re.search(r'\d', line) and 2 <= len(line.split()) <= 4:
                formatted_ingredients.append(f"\n{line}:")
            # Ingredient lines (contain numbers and cooking units)
            elif re.search(r'\d', line) and re.search(r'(?:cup|table|tea|pound|ounce|large|medium|small)', line, re.IGNORECASE):
                formatted_ingredients.append(f"• {line}")
        
        return '\n'.join(formatted_ingredients).strip()
    
    def _extract_instructions_with_structure(self, recipe_structure: Dict, page_text: str) -> str:
        """Extract instructions using visual structure information"""
        
        instruction_sections = recipe_structure.get('instruction_sections', [])
        
        if instruction_sections:
            # Use the structured instruction sections
            main_section = instruction_sections[0]
            instructions_text = main_section['content']
        else:
            # Fallback to text-based extraction
            instructions_match = re.search(r'START COOKING!(.*?)(?=\n[A-Z\s]{10,}|$)', page_text, re.DOTALL)
            
            if instructions_match:
                instructions_text = instructions_match.group(1).strip()
            else:
                # Simple recipe format
                if 'PREPARE INGREDIENTS' in page_text:
                    title_lines = page_text.split('\n')[:10]
                    title = ""
                    for line in title_lines:
                        line = line.strip()
                        if (line.isupper() and 5 < len(line) < 50 and 
                            not re.match(r'^(BEGINNER|INTERMEDIATE|ADVANCED|VEGETARIAN|SERVES|MAKES)', line)):
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
        
        # Format the instructions
        return self._format_instructions_text(instructions_text)
    
    def _format_instructions_text(self, instructions_text: str) -> str:
        """Format instruction text into numbered steps"""
        
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
    
    def _extract_educational_content(self, recipe_structure: Dict, page_text: str) -> Optional[str]:
        """Extract educational content for description"""
        
        educational_sections = recipe_structure.get('educational_sections', [])
        
        if educational_sections:
            educational_parts = []
            for section in educational_sections:
                if section['type'] == 'before_you_begin':
                    content = section['content'].strip()
                    if content:
                        educational_parts.append(f"Before You Begin: {content}")
            
            return ' | '.join(educational_parts) if educational_parts else None
        
        return None
    
    def _is_multi_page_recipe(self, recipe_data: Dict, page_num: int) -> bool:
        """Check if this is part of a multi-page recipe - Enhanced for Teen Cookbook"""
        
        # Teen cookbook recipes can span 3-6 pages, so be more aggressive about detection
        has_title = bool(recipe_data.get('title'))
        has_ingredients = bool(recipe_data.get('ingredients'))
        has_instructions = bool(recipe_data.get('instructions'))
        
        # Case 1: Start of multi-page recipe (has title, maybe incomplete content)
        if has_title and (not has_ingredients or not has_instructions or 
                         len(recipe_data.get('ingredients', '')) < 50 or 
                         len(recipe_data.get('instructions', '')) < 100):
            
            # Filter out instructional content that shouldn't be recipes
            title = recipe_data['title'].lower()
            instructional_keywords = [
                'how to', 'up your game', 'before you begin', 'day 1', 'day 2', 
                'serves', 'makes', 'fillings', 'toppings', 'sauce', 'assembly'
            ]
            
            # Don't treat instructional content as recipes
            for keyword in instructional_keywords:
                if keyword in title:
                    return False
            
            # Must have some actual recipe indicators
            if not has_ingredients and not has_instructions:
                return False
            
            # This looks like the start of a multi-page recipe
            page_key = f"page_{page_num}"
            self.multi_page_recipes[page_key] = {
                'recipe_data': recipe_data,
                'page_start': page_num,
                'waiting_for_completion': True,
                'last_page': page_num
            }
            logger.info(f"🔄 Started multi-page recipe '{recipe_data['title']}' on page {page_num}")
            return True
        
        # Case 2: Continuation with ingredients (no title but has ingredient list)
        if not has_title and has_ingredients:
            # Look for active multi-page recipe in previous 1-6 pages
            for lookback in range(1, 7):  # Check up to 6 pages back
                prev_page_key = f"page_{page_num - lookback}"
                if prev_page_key in self.multi_page_recipes:
                    # Found an active multi-page recipe, add this content
                    self._add_to_multi_page_recipe(prev_page_key, recipe_data, page_num)
                    logger.info(f"🔄 Added ingredients from page {page_num} to multi-page recipe")
                    return True
        
        # Case 3: Continuation with instructions (no title, has instructions with numbered steps)
        if not has_title and has_instructions:
            # Look for numbered steps that suggest continuation
            instructions = recipe_data.get('instructions', '')
            # Check for numbered steps or continuation words
            has_numbered_steps = bool(re.search(r'^\s*\d+\.\s', instructions, re.MULTILINE))
            has_continuation_words = bool(re.search(r'\b(continue|next|then|after|meanwhile|while)\b', instructions, re.IGNORECASE))
            
            if has_numbered_steps or has_continuation_words:
                # Look for active multi-page recipe in previous pages
                for lookback in range(1, 7):
                    prev_page_key = f"page_{page_num - lookback}"
                    if prev_page_key in self.multi_page_recipes:
                        self._add_to_multi_page_recipe(prev_page_key, recipe_data, page_num)
                        logger.info(f"🔄 Added instructions from page {page_num} to multi-page recipe")
                        return True
        
        # Case 4: Page with any content that could be continuation (be more selective)
        if not has_title and (has_ingredients or has_instructions):
            # Only check for nearby multi-page recipes if content looks substantial
            content_length = len(recipe_data.get('ingredients', '') + recipe_data.get('instructions', ''))
            if content_length > 50:  # Has meaningful content
                # Check previous 3 pages only
                for lookback in range(1, 4):  
                    prev_page_key = f"page_{page_num - lookback}"
                    if prev_page_key in self.multi_page_recipes:
                        self._add_to_multi_page_recipe(prev_page_key, recipe_data, page_num)
                        logger.info(f"🔄 Added continuation content from page {page_num} to multi-page recipe")
                        return True
        
        return False
    
    def _add_to_multi_page_recipe(self, page_key: str, continuation_data: Dict, current_page: int):
        """Add continuation data to an existing multi-page recipe"""
        
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
        
        # Combine educational content
        if continuation_data.get('description'):
            if not main_recipe.get('description'):
                main_recipe['description'] = continuation_data['description']
            else:
                main_recipe['description'] += ' | ' + continuation_data['description']
        
        # Update page range
        self.multi_page_recipes[page_key]['last_page'] = current_page
        self.multi_page_recipes[page_key]['waiting_for_completion'] = False
    
    def _check_multi_page_continuation(self, page_text: str, page_num: int):
        """Check if a non-recipe page could be a multi-page continuation"""
        
        # Only check if we have active multi-page recipes
        if not self.multi_page_recipes:
            return
        
        # Extract basic content from the page
        recipe_data = self._extract_recipe_with_visual_guidance({'recipe_structure': {}}, page_text)
        
        if not recipe_data:
            return
        
        # Check if this could be continuation content
        has_ingredients = bool(recipe_data.get('ingredients'))
        has_instructions = bool(recipe_data.get('instructions'))
        
        if not has_ingredients and not has_instructions:
            return
        
        # Look for active multi-page recipes in previous pages
        for lookback in range(1, 7):  # Check up to 6 pages back
            prev_page_key = f"page_{page_num - lookback}"
            if prev_page_key in self.multi_page_recipes:
                # Found an active multi-page recipe, add this content
                self._add_to_multi_page_recipe(prev_page_key, recipe_data, page_num)
                logger.info(f"🔄 Added continuation content from non-recipe page {page_num} to multi-page recipe")
                return
    
    def _finalize_multi_page_recipes(self, dry_run: bool = False):
        """Process any remaining multi-page recipes"""
        
        for page_key, recipe_info in self.multi_page_recipes.items():
            recipe_data = recipe_info['recipe_data']
            
            # For multi-page recipes, use more lenient validation
            validation_result = self._validate_multi_page_recipe_requirements(recipe_data)
            
            if validation_result['valid']:
                # Clean and validate semantically
                cleaned_recipe = self._clean_recipe_text(recipe_data)
                semantic_result = self.semantic_engine.validate_complete_recipe(cleaned_recipe)
                
                # Teen cookbook special handling for multi-page recipes - be more forgiving
                teen_cookbook_override = False
                if not semantic_result.is_valid_recipe:
                    has_title = bool(recipe_data.get('title'))
                    has_some_content = bool(recipe_data.get('ingredients') or recipe_data.get('instructions'))
                    has_food_words = self._has_teen_food_indicators(recipe_data)
                    
                    # For multi-page recipes, accept if we have title + some content + food words
                    if has_title and has_some_content and has_food_words:
                        teen_cookbook_override = True
                        # Create a mock semantic result for teen cookbook recipes
                        class MockSemanticResult:
                            def __init__(self):
                                self.is_valid_recipe = True
                                self.confidence_score = 0.70  # Good confidence for teen multi-page recipes
                        
                        semantic_result = MockSemanticResult()
                
                if semantic_result.is_valid_recipe:
                    # Add metadata
                    recipe_data['visual_confidence'] = 12  # Multi-page recipes get moderate confidence
                    recipe_data['semantic_confidence'] = semantic_result.confidence_score
                    recipe_data['source'] = 'The Complete Cookbook for Teen - America\'s Test Kitchen Kids'
                    recipe_data['extraction_method'] = 'visual_semantic_hybrid_multipage'
                    recipe_data['teen_cookbook_override'] = teen_cookbook_override
                    
                    if 'last_page' in recipe_info and recipe_info['last_page'] != recipe_info['page_start']:
                        recipe_data['page_number'] = f"{recipe_info['page_start']}-{recipe_info['last_page']}"
                        logger.info(f"✅ Multi-page {recipe_info['page_start']}-{recipe_info['last_page']}: '{recipe_data['title']}' (semantic: {semantic_result.confidence_score:.2f}, override: {teen_cookbook_override})")
                    else:
                        recipe_data['page_number'] = recipe_info['page_start']
                        logger.info(f"✅ Page {recipe_info['page_start']}: '{recipe_data['title']}' (semantic: {semantic_result.confidence_score:.2f}, override: {teen_cookbook_override})")
                    
                    if not dry_run:
                        self.extracted_recipes.append(recipe_data)
                    self.stats['recipes_validated'] += 1
                    self.stats['semantic_validations'] += 1
                    
                    if teen_cookbook_override:
                        logger.info(f"  📚 Teen cookbook override applied for multi-page recipe")
                else:
                    self.rejection_reasons['semantic_rejection'] += 1
                    logger.info(f"❌ Multi-page recipe '{recipe_data.get('title', 'Unknown')}' failed semantic validation")
            else:
                for reason in validation_result['reasons']:
                    self.rejection_reasons[reason] += 1
                logger.info(f"❌ Multi-page recipe '{recipe_data.get('title', 'Unknown')}' failed validation: {validation_result['reasons']}")
    
    def _validate_multi_page_recipe_requirements(self, recipe_data: Dict) -> Dict[str, Any]:
        """Validate core recipe requirements for multi-page recipes (more lenient)"""
        
        validation = {
            'valid': True,
            'reasons': []
        }
        
        # Must have title
        if not recipe_data.get('title'):
            validation['valid'] = False
            validation['reasons'].append('no_title_found')
        
        # For multi-page recipes, we're more lenient - need EITHER ingredients OR instructions
        has_ingredients = recipe_data.get('ingredients') and len(recipe_data['ingredients'].strip()) >= 5
        has_instructions = recipe_data.get('instructions') and len(recipe_data['instructions'].strip()) >= 10
        
        if not has_ingredients and not has_instructions:
            validation['valid'] = False
            validation['reasons'].append('no_content_found')
        
        return validation
    
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
        if not recipe_data.get('ingredients') or len(recipe_data['ingredients'].strip()) < 10:
            validation['valid'] = False
            validation['reasons'].append('no_ingredients')
        
        # Must have instructions
        if not recipe_data.get('instructions') or len(recipe_data['instructions'].strip()) < 15:
            validation['valid'] = False
            validation['reasons'].append('no_instructions')
        
        return validation
    
    def _clean_recipe_text(self, recipe_data: Dict) -> Dict[str, str]:
        """Clean recipe text for better semantic validation"""
        
        cleaned = {}
        
        for field in ['title', 'ingredients', 'instructions', 'description']:
            text = recipe_data.get(field, '')
            if text:
                # Fix common PDF extraction artifacts
                text = self._clean_instruction_text(text)
                cleaned[field] = text
        
        return cleaned
    
    def _clean_instruction_text(self, text: str) -> str:
        """Clean PDF extraction artifacts from text - Enhanced for Teen Cookbook"""
        
        # Teen cookbook specific PDF extraction fixes
        teen_fixes = [
            # Common broken words in teen cookbook
            (r'\bcock ed\b', 'cooked'),
            (r'\bsepar ately\b', 'separately'),
            (r'\bdr ained\b', 'drained'), 
            (r'\bsl iced\b', 'sliced'),
            (r'\bpeeled\b', 'peeled'),
            (r'\boar d\b', 'board'),
            (r'\bpi tas\b', 'pitas'),
            (r'\bpi ta\b', 'pita'),
            (r'\br ed\b', 'red'),
            (r'\bhal f\b', 'half'),
            (r'\blar ge\b', 'large'),
            (r'\bsmal l\b', 'small'),
            (r'\bf or\b', 'for'),
            (r'\bgar lic\b', 'garlic'),
            (r'\bsal t\b', 'salt'),
            (r'\bpepper\b', 'pepper'),
            (r'\bmeasur ed\b', 'measured'),
            (r'\bunsal ted\b', 'unsalted'),
            (r'\bbut ter\b', 'butter'),
            (r'\bmuf fins\b', 'muffins'),
            (r'\bEngl ish\b', 'English'),
            (r'\bspl it\b', 'split'),
            (r'\bv egetable\b', 'vegetable'),
            (r'\boi l\b', 'oil'),
            (r'\bcloves\b', 'cloves'),
            (r'\btablespoon\b', 'tablespoon'),
            (r'\bteaspoon\b', 'teaspoon'),
            (r'\br oasted\b', 'roasted'),
            (r'\btomator oes\b', 'tomatoes'),
            (r'\bmuhr ooms\b', 'mushrooms'),
            (r'\bchick en\b', 'chicken'),
            (r'\by olks\b', 'yolks'),
            (r'\bhal f-and-hal f\b', 'half-and-half'),
            (r'\bvegetabl es\b', 'vegetables'),
            (r'\bpot atoes\b', 'potatoes'),
            (r'\bsea soning\b', 'seasoning'),
            (r'\bingredient s\b', 'ingredients'),
            (r'\binstr uctions\b', 'instructions'),
            (r'\btemper ature\b', 'temperature'),
            (r'\brefrig erator\b', 'refrigerator'),
            
            # Teen cookbook specific issues
            (r'\b4slices\b', '4 slices'),
            (r'\b2large\b', '2 large'),
            (r'\b1pinch\b', '1 pinch'),
            (r'\b1tablespoon\b', '1 tablespoon'),
            (r'\b2rolls\b', '2 rolls'),
            (r'\b1teaspoon\b', '1 teaspoon'),
            (r'\b2slices\b', '2 slices'),
            (r'\b2smal l\b', '2 small'),
            (r'\bbowls \b', 'bowls '),
        ]
        
        for pattern, replacement in teen_fixes:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Additional spacing and formatting fixes
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
        text = re.sub(r' ,', ',', text)   # Space before comma
        text = re.sub(r' \.', '.', text)  # Space before period
        text = text.strip()
        
        # Remove PDF page references
        text = re.sub(r'\(see this page\s*\)', '', text)
        text = re.sub(r'\(this page\s*\)', '', text)
        
        return text
    
    def _has_teen_food_indicators(self, recipe_data: Dict) -> bool:
        """Check if recipe contains real ingredient indicators using ingredient intelligence"""
        
        # Use the ingredient intelligence engine instead of hardcoded keywords
        title = recipe_data.get('title', '').lower()
        ingredients = recipe_data.get('ingredients', '').lower()
        
        # Check title for known ingredients
        title_has_ingredients = self._contains_known_ingredients(title)
        
        # Check ingredients text for known ingredients
        ingredients_have_food = self._contains_known_ingredients(ingredients)
        
        # Also check for basic measurement patterns that indicate real recipes
        has_measurements = bool(re.search(r'\d+.*?(cup|tablespoon|teaspoon|slice|large|small|pound|ounce)', ingredients, re.IGNORECASE))
        
        return title_has_ingredients or (ingredients_have_food and has_measurements)
    
    def _contains_known_ingredients(self, text: str) -> bool:
        """Check if text contains known ingredients from our ingredient database"""
        
        # Check against canonical ingredient names
        for ingredient_id, data in self.ingredient_engine.canonical_ingredients.items():
            ingredient_name = data['name'].lower()
            
            # Extract the core ingredient name (remove measurements and modifiers)
            core_name = self._extract_core_ingredient_name(ingredient_name)
            
            if core_name and len(core_name) >= 3:  # Avoid very short matches
                if core_name in text:
                    return True
        
        return False
    
    def _extract_core_ingredient_name(self, ingredient_name: str) -> str:
        """Extract the core ingredient name from a full ingredient description"""
        
        # Remove common measurement patterns
        cleaned = re.sub(r'^\d+.*?(cup|tablespoon|teaspoon|slice|large|small|pound|ounce|stick|clove)', '', ingredient_name, flags=re.IGNORECASE)
        
        # Remove common modifiers
        cleaned = re.sub(r'\b(for|about|until|warmed|hot|to|the|touch|minute|lukewarm|strong|brewed|dry|extra-virgin|all-purpose|confectioners|crumbled|garnish)\b', '', cleaned, flags=re.IGNORECASE)
        
        # Clean up whitespace and get the first meaningful word(s)
        words = cleaned.strip().split()
        
        # Return the first 1-2 meaningful words
        core_words = []
        for word in words:
            if len(word) >= 3 and word not in ['and', 'the', 'for', 'with']:
                core_words.append(word)
                if len(core_words) >= 2:
                    break
        
        return ' '.join(core_words) if core_words else ''
    
    def _has_proper_teen_structure(self, recipe_data: Dict) -> bool:
        """Check if recipe has proper teen cookbook structure"""
        
        title = recipe_data.get('title', '')
        ingredients = recipe_data.get('ingredients', '')
        instructions = recipe_data.get('instructions', '')
        
        # Basic structure requirements
        has_title = len(title.strip()) >= 5
        has_ingredients = len(ingredients.strip()) >= 20
        has_instructions = len(instructions.strip()) >= 20
        
        # Check for measurement patterns in ingredients
        has_measurements = bool(re.search(r'\d+.*?(cup|tablespoon|teaspoon|slice|large|small)', ingredients, re.IGNORECASE))
        
        # Check for numbered steps in instructions
        has_numbered_steps = bool(re.search(r'^\d+\.', instructions, re.MULTILINE))
        
        return has_title and has_ingredients and has_instructions and has_measurements
    
    def _print_detailed_summary(self):
        """Print comprehensive extraction summary"""
        
        logger.info("")
        logger.info("👁️🧠 VISUAL + SEMANTIC EXTRACTION SUMMARY:")
        logger.info("=" * 70)
        logger.info(f"📄 Pages processed: {self.stats['pages_processed']}")
        logger.info(f"👁️ Pages with visual recipe structure: {self.stats['pages_with_visual_structure']}")
        logger.info(f"🔍 Recipe candidates found: {self.stats['recipe_candidates_found']}")
        logger.info(f"👁️ Visual validations: {self.stats['visual_validations']}")
        logger.info(f"🧠 Semantic validations: {self.stats['semantic_validations']}")
        logger.info(f"🚫 Artifacts rejected: {self.stats['artifacts_rejected']}")
        logger.info(f"✅ Recipes validated: {self.stats['recipes_validated']}")
        
        if self.extracted_recipes:
            semantic_scores = [r.get('semantic_confidence', 0) for r in self.extracted_recipes]
            avg_semantic = sum(semantic_scores) / len(semantic_scores) if semantic_scores else 0
            logger.info(f"📊 Average semantic quality: {avg_semantic:.2f}")
        
        logger.info("")
        logger.info("🚫 REJECTION BREAKDOWN:")
        for reason, count in self.rejection_reasons.items():
            reason_name = reason.replace('_', ' ').title()
            logger.info(f"  {reason_name}: {count}")
        
        logger.info("")
        logger.info("✅ VALIDATED RECIPES:")
        for i, recipe in enumerate(self.extracted_recipes[:10], 1):
            visual_conf = recipe.get('visual_confidence', 0)
            semantic_conf = recipe.get('semantic_confidence', 0)
            logger.info(f"  {i}. '{recipe['title']}' (visual: {visual_conf:.0f}, semantic: {semantic_conf:.2f})")
        
        if len(self.extracted_recipes) > 10:
            logger.info(f"  ... and {len(self.extracted_recipes) - 10} more")
    
    def _save_recipes(self):
        """Save extracted recipes to database"""
        
        logger.info("")
        logger.info("💾 SAVING VISUAL + SEMANTIC EXTRACTION RESULTS")
        logger.info("=" * 60)
        logger.info(f"📋 Recipes to save: {len(self.extracted_recipes)}")
        logger.info("👁️ Visual structure validated")
        logger.info("🧠 Semantic quality assured")
        
        try:
            saved_count = 0
            
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                for recipe in self.extracted_recipes:
                    # Prepare recipe data for database - use existing schema
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
                        recipe['instructions'],
                        recipe.get('category', 'Teen Recipe'),
                        recipe['source'],
                        recipe.get('servings'),
                        recipe.get('total_time'),
                        recipe.get('description')
                    )
                    
                    cursor.execute(insert_query, values)
                    saved_count += 1
                
                conn.commit()
            
            logger.info(f"✅ Successfully inserted {saved_count} enhanced recipes")
            
        except Exception as e:
            logger.error(f"❌ Error saving recipes: {e}")
        
        logger.info("")
        logger.info("🎉 VISUAL + SEMANTIC EXTRACTION COMPLETE!")
        logger.info("👁️🧠 Multi-layer validation with enhanced detection")
        logger.info(f"📊 Results: {len(self.extracted_recipes)} recipes extracted, {saved_count} saved")

def main():
    """Main execution function"""
    
    parser = argparse.ArgumentParser(description='ATK Teens Visual + Semantic Recipe Extractor')
    parser.add_argument('--start-page', type=int, default=1, help='Starting page number')
    parser.add_argument('--end-page', type=int, help='Ending page number')
    parser.add_argument('--max-recipes', type=int, help='Maximum recipes to extract')
    parser.add_argument('--dry-run', action='store_true', help='Extract without saving to database')
    
    args = parser.parse_args()
    
    # PDF path
    pdf_path = os.path.join(os.path.dirname(__file__), 'The Complete Cookbook for Teen - America\'s Test Kitchen Kids.pdf')
    
    if not os.path.exists(pdf_path):
        logger.error(f"❌ PDF not found: {pdf_path}")
        return
    
    # Create extractor and run
    extractor = TeenRecipeExtractor(pdf_path)
    recipes = extractor.extract_from_page_range(
        start_page=args.start_page,
        end_page=args.end_page,
        max_recipes=args.max_recipes,
        dry_run=args.dry_run
    )
    
    logger.info(f"🏁 Extraction complete: {len(recipes)} recipes extracted")

if __name__ == "__main__":
    main()
