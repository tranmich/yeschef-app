#!/usr/bin/env python3
"""
ATK 25th Anniversary VISUAL + SEMANTIC Intelligent Extractor
Combines visual structure detection with semantic validation for optimal results

Key Features:
- Visual structure detection (headers, sections, formatting)
- Page layout analysis for recipe boundaries
- Multi-page recipe support
- Semantic validation for quality assurance
- Font size and formatting awareness
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


class VisualStructureDetector:
    """Detects visual cues and structural patterns in PDF text"""
    
    @staticmethod
    def analyze_page_structure(page_text: str) -> Dict:
        """Analyze the visual structure of a page"""
        structure = {
            'has_recipe': False,
            'recipe_sections': [],
            'title_candidates': [],
            'section_headers': [],
            'confidence_score': 0
        }
        
        lines = [line.strip() for line in page_text.split('\n') if line.strip()]
        if not lines:
            return structure
        
        # Detect recipe structure indicators
        score = 0
        
        # 1. Look for ATK-specific headers (high confidence)
        atk_headers = ['PREPARE INGREDIENTS', 'START COOKING!', 'BEFORE YOU BEGIN']
        for header in atk_headers:
            if header in page_text:
                structure['recipe_sections'].append(header)
                score += 3
        
        # 2. Look for recipe metadata patterns (high confidence)
        metadata_patterns = [
            (r'(SERVES|MAKES)\s+\d+', 2),
            (r'\d+\s+(MINUTES|HOURS)', 2),
            (r'(BEGINNER|INTERMEDIATE|ADVANCED)', 2),
            (r'(VEGETARIAN|VEGAN|GLUTEN-FREE)', 1)
        ]
        
        for pattern, points in metadata_patterns:
            if re.search(pattern, page_text, re.IGNORECASE):
                score += points
        
        # 3. Analyze line structure for titles and sections
        for i, line in enumerate(lines[:25]):  # First 25 lines most important
            line_analysis = VisualStructureDetector._analyze_line_structure(line, i, lines)
            
            if line_analysis['is_title_candidate']:
                structure['title_candidates'].append({
                    'text': line,
                    'position': i,
                    'confidence': line_analysis['title_confidence']
                })
            
            if line_analysis['is_section_header']:
                structure['section_headers'].append({
                    'text': line,
                    'position': i
                })
        
        # 4. Look for ingredient patterns
        ingredient_score = VisualStructureDetector._calculate_ingredient_score(page_text)
        score += ingredient_score
        
        # 5. Look for instruction patterns
        instruction_score = VisualStructureDetector._calculate_instruction_score(page_text)
        score += instruction_score
        
        structure['confidence_score'] = score
        structure['has_recipe'] = score >= 6  # Threshold for recipe detection
        
        return structure
    
    @staticmethod
    def _analyze_line_structure(line: str, position: int, all_lines: List[str]) -> Dict:
        """Analyze individual line structure for visual cues"""
        analysis = {
            'is_title_candidate': False,
            'is_section_header': False,
            'title_confidence': 0
        }
        
        if len(line) < 3 or len(line) > 80:
            return analysis
        
        # Visual indicators for titles
        title_indicators = 0
        
        # 1. Positioning (early in page = higher likelihood)
        if position <= 5:
            title_indicators += 2
        elif position <= 10:
            title_indicators += 1
        
        # 2. Formatting patterns
        if line.isupper():
            title_indicators += 2
        elif line.istitle():
            title_indicators += 1
        
        # 3. Length patterns (recipe titles usually 10-60 chars)
        if 10 <= len(line) <= 60:
            title_indicators += 1
        
        # 4. Content patterns - Use simple keyword fallback for static method
        line_lower = line.lower()
        food_keywords = [
            'chicken', 'beef', 'pork', 'fish', 'salmon', 'eggs', 'pasta', 'rice',
            'soup', 'salad', 'cake', 'bread', 'sauce', 'beans', 'hummus', 'cheese',
            'chocolate', 'vanilla', 'lemon', 'garlic', 'roasted', 'grilled', 'baked',
            'curry', 'deviled', 'scrambled', 'topping', 'walnut', 'spiced', 'avocado',
            'tofu', 'quinoa', 'mushrooms', 'herbs', 'spices', 'butter', 'oil'
        ]
        if any(keyword in line_lower for keyword in food_keywords):
            title_indicators += 2
        
        # 5. Exclude obvious non-titles and explanatory text
        exclusions = [
            re.match(r'^\d+', line),  # Starts with number
            any(word in line_lower for word in ['cup', 'tablespoon', 'teaspoon', 'pound', 'ounce']),
            line in ['BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'VEGETARIAN'],
            re.search(r'(SERVES|MAKES)\s+\d+', line, re.IGNORECASE),
            re.search(r'\d+\s+(MINUTES|HOURS)', line, re.IGNORECASE),
            line_lower.startswith('why this recipe works'),
            'prepackaged' in line_lower,
            line_lower.endswith(' and'),  # Incomplete sentences
            len(line) < 5 or len(line) > 100,  # Too short or too long
            
            # Enhanced explanatory text exclusions
            any(phrase in line_lower for phrase in [
                'why this recipe works', 'this recipe', 'this dish', 'this method',
                'we found', 'we discovered', 'we tested', 'we tried', 'we ditched',
                'traditional', 'classic approach', 'ideal', 'perfect',
                'the key', 'the secret', 'the trick', 'the real key',
                'if it is not available', 'if your', 'substitute', 'works best',
                'easily stood up', 'allowed it to', 'provided', 'replaced', 'helped',
                'cut the baking time', 'maintain its', 'infuse our', 'luxurious',
                'for an easier', 'as for the', 'to infuse', 'the mature',
                'blanching and shocking', 'pleasing tang', 'extra creaminess',
                'nutty fontina replaced', 'bland mozzarella', 'parcooked',
                'soaking them in boiling', 'cut the baking', 'helped the'
            ]),
            
            # Exclude sentence fragments that start with common explanatory words
            re.match(r'^(our|for|the|this|traditional|classic|to|as|blanching|cottage|italian)\s', line_lower),
            
            # Exclude text that ends mid-sentence or with incomplete thoughts  
            line_lower.endswith((' a', ' an', ' the', ' to', ' for', ' with', ' and', ' or')),
            
            # Exclude substitution notes and cooking tips
            re.search(r'(substitute|replace|if.*not available|works best|degrees for about)', line_lower),
            
            # Exclude text that sounds like explanations rather than titles
            len(line.split()) > 8,  # Recipe titles are usually 8 words or fewer
        ]
        
        if any(exclusions):
            title_indicators = 0
        
        # Determine if this is a title candidate
        analysis['title_confidence'] = title_indicators
        analysis['is_title_candidate'] = title_indicators >= 3
        
        # Check for section headers (short, caps, no numbers)
        if (line.isupper() and 
            not re.search(r'\d', line) and 
            2 <= len(line.split()) <= 4 and
            line not in ['BEGINNER', 'INTERMEDIATE', 'ADVANCED']):
            analysis['is_section_header'] = True
        
        return analysis
    
    @staticmethod
    def _calculate_ingredient_score(text: str) -> int:
        """Calculate score based on ingredient patterns"""
        score = 0
        
        # Count ingredient-like patterns
        ingredient_patterns = [
            r'\d+\s*(cup|tablespoon|teaspoon|pound|ounce|tbsp|tsp|lb|oz)',
            r'\d+\s*(large|medium|small)',
            r'\d+.*?(chopped|diced|minced|sliced|grated)',
            r'\d+\s*\([^)]*ounce[^)]*\)',  # (15-ounce) pattern
            r'[¾½¼⅓⅔⅛]\s*(cup|tablespoon|teaspoon)'  # Fractions
        ]
        
        for pattern in ingredient_patterns:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            score += min(matches, 3)  # Cap at 3 points per pattern
        
        return min(score, 8)  # Cap total ingredient score at 8
    
    @staticmethod
    def _calculate_instruction_score(text: str) -> int:
        """Calculate score based on instruction patterns"""
        score = 0
        
        # Count numbered steps
        numbered_steps = len(re.findall(r'^\d+\.', text, re.MULTILINE))
        score += min(numbered_steps * 2, 6)  # 2 points per step, max 6
        
        # Count cooking action words
        cooking_actions = [
            'heat', 'cook', 'bake', 'mix', 'stir', 'add', 'combine', 'whisk',
            'transfer', 'remove', 'drain', 'process', 'simmer', 'boil'
        ]
        
        text_lower = text.lower()
        action_count = sum(1 for action in cooking_actions if action in text_lower)
        score += min(action_count, 4)  # Max 4 points for actions
        
        return score


class ATK25thVisualSemanticExtractor:
    """Enhanced extractor combining visual structure detection with semantic validation"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.cookbook_title = "America's Test Kitchen 25th Anniversary"
        self.db_manager = DatabaseManager()
        self.semantic_engine = SemanticRecipeEngine(ValidationLevel.STRICT)
        self.visual_detector = VisualStructureDetector()
        
        # Load ingredient intelligence engine for proper ingredient recognition
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from core_systems.ingredient_intelligence_engine import IngredientIntelligenceEngine
        self.ingredient_engine = IngredientIntelligenceEngine()
        
        self.extracted_recipes = []
        self.extraction_stats = {
            'pages_processed': 0,
            'pages_with_recipes': 0,
            'recipe_candidates_found': 0,
            'visual_validations': 0,
            'semantic_validations': 0,
            'artifacts_rejected': 0,
            'recipes_validated': 0,
            'quality_scores': [],
            'rejection_reasons': {
                'no_visual_structure': 0,
                'no_title_found': 0,
                'no_ingredients': 0,
                'no_known_ingredients': 0,
                'no_instructions': 0,
                'semantic_rejection': 0,
                'low_quality': 0
            }
        }
    
    def extract_recipes(self, max_recipes: Optional[int] = None, start_page: int = 1, end_page: Optional[int] = None) -> List[Dict]:
        """Main extraction with visual structure detection + semantic validation + multi-page support"""
        logger.info(f"🧠 VISUAL + SEMANTIC ATK 25TH EXTRACTION")
        logger.info("=" * 70)
        logger.info("👁️ Visual structure detection + 🧠 Semantic validation")
        logger.info("🛡️ Multi-layer quality assurance + 📄 Multi-page recipe support")
        logger.info("=" * 70)
        
        try:
            with open(self.pdf_path, 'rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                total_pages = len(reader.pages)
                
                start_idx = start_page - 1
                end_idx = end_page if end_page else total_pages
                end_idx = min(end_idx, total_pages)
                
                logger.info(f"📄 Processing pages {start_page} to {end_idx}")
                
                # Track potential multi-page recipes
                pending_recipe = None
                
                for page_num in range(start_idx, end_idx):
                    if max_recipes and self.extraction_stats['recipes_validated'] >= max_recipes:
                        break
                    
                    try:
                        page = reader.pages[page_num]
                        text = page.extract_text()
                        
                        if not text or len(text.strip()) < 50:
                            self.extraction_stats['rejection_reasons']['no_visual_structure'] += 1
                            continue
                        
                        self.extraction_stats['pages_processed'] += 1
                        
                        # Step 1: Check if this continues a pending recipe
                        if pending_recipe:
                            continuation_result = self._try_continue_recipe(pending_recipe, text, page_num + 1)
                            if continuation_result:
                                # Successfully completed multi-page recipe
                                semantic_result = self.semantic_engine.validate_complete_recipe({
                                    'title': continuation_result.get('title', ''),
                                    'ingredients': continuation_result.get('ingredients', ''),
                                    'instructions': continuation_result.get('instructions', '')
                                })
                                
                                if semantic_result.is_valid_recipe and semantic_result.confidence_score >= 0.7:
                                    continuation_result['semantic_validation'] = {
                                        'is_valid': semantic_result.is_valid_recipe,
                                        'confidence_score': semantic_result.confidence_score,
                                        'quality_metrics': semantic_result.quality_metrics,
                                        'validation_errors': semantic_result.validation_errors,
                                        'validation_warnings': semantic_result.validation_warnings
                                    }
                                    continuation_result['multi_page_recipe'] = True
                                    continuation_result['page_range'] = f"{pending_recipe['page_number']}-{page_num + 1}"
                                    
                                    self.extraction_stats['quality_scores'].append(semantic_result.confidence_score)
                                    self.extracted_recipes.append(continuation_result)
                                    self.extraction_stats['recipes_validated'] += 1
                                    
                                    logger.info(f"✅ Multi-page {pending_recipe['page_number']}-{page_num + 1}: '{continuation_result.get('title', 'Unknown')}' (semantic: {semantic_result.confidence_score:.2f})")
                                    
                                pending_recipe = None
                                continue
                            else:
                                # Continuation failed, proceed with normal processing
                                pending_recipe = None
                        
                        # Step 2: Visual structure analysis
                        structure = self.visual_detector.analyze_page_structure(text)
                        self.extraction_stats['visual_validations'] += 1
                        
                        if structure['has_recipe']:
                            self.extraction_stats['pages_with_recipes'] += 1
                            
                            # Step 3: Extract recipe using visual + semantic approach
                            recipe_candidate = self._extract_recipe_visually(text, page_num + 1, structure)
                            
                            if recipe_candidate:
                                self.extraction_stats['recipe_candidates_found'] += 1
                                
                                # Step 4: Check if this might be an incomplete recipe 
                                if not recipe_candidate.get('instructions'):
                                    # Recipe has title and ingredients but no instructions - might be multi-page
                                    pending_recipe = recipe_candidate
                                    logger.debug(f"🔄 Page {page_num + 1}: Potential multi-page recipe start (no instructions) - '{recipe_candidate.get('title', 'Unknown')}'")
                                    continue
                                elif (recipe_candidate.get('instructions') and 
                                      ('Prepare ingredients according to recipe specifications' in recipe_candidate.get('instructions', '') or
                                       'Why This Recipe Works' in text)):
                                    # Recipe has placeholder instructions or explanatory text - likely incomplete
                                    pending_recipe = recipe_candidate
                                    logger.debug(f"🔄 Page {page_num + 1}: Recipe with placeholder/incomplete instructions, checking next page - '{recipe_candidate.get('title', 'Unknown')}'")
                                    continue
                                
                                # Step 5: Semantic validation for complete recipes
                                semantic_result = self.semantic_engine.validate_complete_recipe({
                                    'title': recipe_candidate.get('title', ''),
                                    'ingredients': recipe_candidate.get('ingredients', ''),
                                    'instructions': recipe_candidate.get('instructions', '')
                                })
                                self.extraction_stats['semantic_validations'] += 1
                                
                                # Step 6: Quality threshold
                                if semantic_result.is_valid_recipe and semantic_result.confidence_score >= 0.7:
                                    recipe_candidate['semantic_validation'] = {
                                        'is_valid': semantic_result.is_valid_recipe,
                                        'confidence_score': semantic_result.confidence_score,
                                        'quality_metrics': semantic_result.quality_metrics,
                                        'validation_errors': semantic_result.validation_errors,
                                        'validation_warnings': semantic_result.validation_warnings
                                    }
                                    recipe_candidate['visual_structure'] = structure
                                    
                                    self.extraction_stats['quality_scores'].append(semantic_result.confidence_score)
                                    self.extracted_recipes.append(recipe_candidate)
                                    self.extraction_stats['recipes_validated'] += 1
                                    
                                    logger.info(f"✅ Page {page_num + 1}: '{recipe_candidate.get('title', 'Unknown')}' (visual: {structure['confidence_score']}, semantic: {semantic_result.confidence_score:.2f})")
                                else:
                                    self.extraction_stats['rejection_reasons']['semantic_rejection'] += 1
                                    logger.debug(f"🚫 Page {page_num + 1}: Semantic rejection - {semantic_result.validation_errors}")
                            else:
                                self.extraction_stats['rejection_reasons']['low_quality'] += 1
                        else:
                            self.extraction_stats['rejection_reasons']['no_visual_structure'] += 1
                        
                        # Progress updates
                        if self.extraction_stats['pages_processed'] % 25 == 0:
                            logger.info(f"  📊 Progress: {self.extraction_stats['pages_processed']} pages, {self.extraction_stats['recipes_validated']} recipes validated")
                    
                    except Exception as e:
                        logger.error(f"❌ Error processing page {page_num + 1}: {e}")
                        continue
                
                # Handle any remaining pending recipe
                if pending_recipe:
                    logger.debug(f"🔄 Recipe starting on page {pending_recipe['page_number']} remains incomplete")
        
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
            raise
        
        logger.info(f"\n✅ VISUAL + SEMANTIC EXTRACTION COMPLETE!")
        self._print_summary()
        
        return self.extracted_recipes
    
    def _try_continue_recipe(self, pending_recipe: Dict, continuation_text: str, page_number: int) -> Optional[Dict]:
        """Try to continue a multi-page recipe from the previous page"""
        
        # CRITICAL: Check if this page contains mostly explanatory text that should be excluded
        lines = [line.strip() for line in continuation_text.split('\n') if line.strip()]
        explanatory_line_count = 0
        total_lines = len(lines)
        
        for line in lines:
            if self._should_exclude_text(line):
                explanatory_line_count += 1
        
        # If more than 50% of the lines are explanatory text, skip this continuation
        if total_lines > 0 and (explanatory_line_count / total_lines) > 0.5:
            return None
        
        # Extract additional ingredients from this page
        additional_ingredients = self._extract_ingredients_by_patterns(continuation_text)
        
        # Extract instructions from this page
        instructions = self._extract_numbered_steps(continuation_text)
        if not instructions:
            instructions = self._parse_numbered_instructions(continuation_text)
        
        # Must have instructions to complete the recipe
        if not instructions:
            return None
        
        # Combine ingredients from both pages
        existing_ingredients = pending_recipe.get('ingredients', '')
        if additional_ingredients:
            combined_ingredients = existing_ingredients + '\n' + additional_ingredients
        else:
            combined_ingredients = existing_ingredients
        
        # Must have reasonable ingredients
        if not combined_ingredients or len(combined_ingredients.split('•')) < 3:
            return None
        
        # Create completed recipe
        completed_recipe = pending_recipe.copy()
        completed_recipe['ingredients'] = self._format_ingredients(combined_ingredients)
        completed_recipe['instructions'] = instructions
        completed_recipe['continuation_page'] = page_number
        
        return completed_recipe
    
    def _should_exclude_text(self, text: str) -> bool:
        """Check if text should be excluded as explanatory content"""
        if not text or len(text.strip()) < 3:
            return True
            
        line = text.strip()
        line_lower = line.lower()
        
        # Apply all exclusion patterns - REFINED to be less aggressive
        exclusions = [
            re.match(r'^\d+', line),  # Starts with number
            any(word in line_lower for word in ['cup', 'tablespoon', 'teaspoon', 'pound', 'ounce']),
            line in ['BEGINNER', 'INTERMEDIATE', 'ADVANCED', 'VEGETARIAN'],
            re.search(r'(SERVES|MAKES)\s+\d+', line, re.IGNORECASE),
            re.search(r'\d+\s+(MINUTES|HOURS)', line, re.IGNORECASE),
            line_lower.startswith('why this recipe works'),
            'prepackaged' in line_lower,
            line_lower.endswith(' and'),  # Incomplete sentences
            len(line) < 5 or len(line) > 120,  # RELAXED: Allow longer recipe titles
            
            # Enhanced explanatory text exclusions - REFINED to be less aggressive
            any(phrase in line_lower for phrase in [
                'why this recipe works', 'we found', 'we discovered', 'we tested', 'we tried', 'we ditched',
                'the key is', 'the secret is', 'the trick is', 'the real key',
                'if it is not available', 'substitute for', 'works best in this',
                'easily stood up', 'allowed it to', 'provided', 'replaced', 'helped',
                'cut the baking time', 'maintain its', 'infuse our', 'luxurious texture',
                'for an easier', 'as for the', 'to infuse', 'the mature',
                'blanching and shocking', 'pleasing tang', 'extra creaminess',
                'nutty fontina replaced', 'bland mozzarella', 'parcooked',
                'soaking them in boiling', 'cut the baking', 'helped the'
            ]),
            
            # REFINED: Only exclude very specific explanatory sentence starters 
            re.match(r'^(our ideal|our approach|our method|our technique|for best results|to ensure|for this recipe)\s', line_lower),
            
            # Exclude text that ends mid-sentence or with incomplete thoughts  
            line_lower.endswith((' a', ' an', ' the', ' to', ' for', ' with', ' and', ' or')),
            
            # Exclude substitution notes and cooking tips
            re.search(r'(substitute|replace|if.*not available|works best|degrees for about)', line_lower),
            
            # Exclude text that sounds like explanations rather than titles
            len(line.split()) > 10,  # RELAXED: Allow longer recipe titles (was 8)
            
            # Exclude obvious ingredient lines that aren't recipe titles
            any(ingredient_phrase in line_lower for ingredient_phrase in [
                'table salt for cooking', 'for cooking pasta', 'cheese filling and pasta',
                'salt and pepper', 'olive oil', 'vegetable oil', 'butter',
                'grated cheese', 'diced onion', 'minced garlic'
            ]),
        ]
        
        return any(exclusions)
    
    def _extract_recipe_visually(self, page_text: str, page_number: int, structure: Dict) -> Optional[Dict]:
        """Extract recipe using visual structure cues + existing logic"""
        
        recipe_data = {
            'page_number': page_number,
            'source': self.cookbook_title,
            'extraction_timestamp': datetime.now().isoformat(),
            'extraction_method': 'visual_semantic'
        }
        
        # Step 1: Extract title using visual cues
        title = self._extract_title_with_visual_cues(page_text, structure)
        if not title:
            self.extraction_stats['rejection_reasons']['no_title_found'] += 1
            return None
        
        recipe_data['title'] = title
        recipe_data['category'] = self._infer_category(title)
        
        # Step 2: Extract ingredients using enhanced detection
        ingredients = self._extract_ingredients_with_structure(page_text, structure)
        if not ingredients:
            self.extraction_stats['rejection_reasons']['no_ingredients'] += 1
            return None
        
        # Enhanced validation: Check if ingredients contain known food items
        ingredients_have_food = self._contains_known_ingredients(ingredients)
        if not ingredients_have_food:
            # Give semantic engine a chance to override - just use basic validation
            has_measurements = bool(re.search(r'\d+.*?(cup|tablespoon|teaspoon|slice|large|small|pound|ounce)', ingredients, re.IGNORECASE))
            if not has_measurements:
                self.extraction_stats['rejection_reasons']['no_known_ingredients'] += 1
                return None
        
        recipe_data['ingredients'] = ingredients
        
        # Step 3: Extract instructions with multi-page support
        instructions = self._extract_instructions_with_structure(page_text, structure)
        
        # Enhanced: Allow recipes without instructions if they have good visual structure
        if not instructions:
            if structure['confidence_score'] >= 8:  # High visual confidence
                recipe_data['instructions'] = "1. Prepare ingredients according to recipe specifications.\n2. Cook and combine ingredients following standard method for this dish type."
                recipe_data['needs_manual_review'] = True
                recipe_data['multi_page_recipe'] = True
            else:
                self.extraction_stats['rejection_reasons']['no_instructions'] += 1
                return None
        else:
            recipe_data['instructions'] = instructions
        
        # Step 4: Extract metadata
        servings = self._extract_servings_enhanced(page_text)
        if servings:
            recipe_data['servings'] = servings
        
        timing = self._extract_timing_enhanced(page_text)
        if timing:
            recipe_data['total_time'] = timing
        
        # Add visual structure metadata
        recipe_data['visual_confidence'] = structure['confidence_score']
        recipe_data['detected_sections'] = structure['recipe_sections']
        
        return recipe_data
    
    def _extract_title_with_visual_cues(self, page_text: str, structure: Dict) -> Optional[str]:
        """Enhanced title extraction using visual structure analysis"""
        
        # Use visual structure's title candidates
        title_candidates = structure['title_candidates']
        
        # Sort by confidence and position
        title_candidates.sort(key=lambda x: (x['confidence'], -x['position']), reverse=True)
        
        fallback_title = None
        
        for candidate in title_candidates:
            candidate_text = candidate['text']
            
            # ENHANCED SYNERGY: Use scoring system instead of hard exclusions
            exclusion_score = 0
            if self._should_exclude_text(candidate_text):
                exclusion_score += 2  # Penalty for exclusion patterns
            
            # Continue processing even if exclusion patterns match - let other systems decide
            
            # Enhanced validation with ingredient intelligence
            title_has_ingredients = self._contains_known_ingredients(candidate_text)
            ingredient_score = 1 if title_has_ingredients else 0
            
            # Test with semantic engine
            if self.semantic_engine._is_recipe_title(candidate_text):
                semantic_score = 2  # High confidence from semantic engine
                
                # Calculate total synergy score
                total_score = semantic_score + ingredient_score - exclusion_score
                
                # Accept if total synergy score is positive
                if total_score > 0:
                    cleaned_title = self._clean_title(candidate_text)
                    if cleaned_title and len(cleaned_title) > 3:
                        if title_has_ingredients:
                            return cleaned_title  # Prefer ingredient-validated titles
                        else:
                            fallback_title = cleaned_title  # Store as fallback
        
        # Return fallback title if no ingredient-validated title found
        if fallback_title:
            return fallback_title
        
        # Fallback to original logic if visual detection doesn't work
        return self._extract_title_fallback(page_text)
    
    def _extract_title_fallback(self, page_text: str) -> Optional[str]:
        """Fallback title extraction method"""
        lines = [line.strip() for line in page_text.split('\n') if line.strip()]
        
        for i, line in enumerate(lines[:20]):
            if len(line) < 3 or len(line) > 80:
                continue
            
            # CRITICAL: Apply exclusion filters BEFORE processing
            # TEMPORARILY DISABLED for debugging
            # if self._should_exclude_text(line):
            #     continue
            
            # Enhanced food indicators from visual learning
            food_indicators = [
                'soup', 'salad', 'chicken', 'beef', 'pork', 'fish', 'pasta', 'rice',
                'bread', 'cake', 'pie', 'cookie', 'sauce', 'beans', 'vegetables',
                'roast', 'grilled', 'baked', 'fried', 'steamed', 'braised',
                'hummus', 'eggs', 'topping', 'walnut', 'spiced', 'curry', 'deviled',
                'cheese', 'cream', 'butter', 'chocolate', 'vanilla', 'lemon',
                'garlic', 'onion', 'mushroom', 'tomato', 'potato', 'carrot',
                'guacamole', 'scrambled', 'refried'
            ]
            
            line_lower = line.lower()
            if any(indicator in line_lower for indicator in food_indicators):
                # Enhanced validation with ingredient intelligence
                title_has_ingredients = self._contains_known_ingredients(line)
                if title_has_ingredients and self.semantic_engine._is_recipe_title(line):
                    return self._clean_title(line)
                elif self.semantic_engine._is_recipe_title(line):
                    # Allow semantic engine override even without ingredient intelligence match
                    return self._clean_title(line)
        
        return None
    
    def _extract_ingredients_with_structure(self, page_text: str, structure: Dict) -> Optional[str]:
        """Enhanced ingredient extraction using visual structure"""
        
        # Check if we have PREPARE INGREDIENTS section
        if 'PREPARE INGREDIENTS' in structure['recipe_sections']:
            prepare_pos = page_text.find('PREPARE INGREDIENTS')
            content_after_prepare = page_text[prepare_pos + len('PREPARE INGREDIENTS'):].strip()
            
            # Look for START COOKING! to limit section
            start_cooking_pos = content_after_prepare.find('START COOKING!')
            if start_cooking_pos != -1:
                ingredients_text = content_after_prepare[:start_cooking_pos].strip()
            else:
                ingredients_text = content_after_prepare[:1000].strip()  # Limit for simple recipes
        else:
            # Use enhanced pattern detection with multi-page awareness
            ingredients_text = self._extract_ingredients_by_patterns(page_text)
            
            # Special handling: If we found very few ingredients, try extracting from end of page
            # This handles cases where ingredients appear after "Why This Recipe Works" text
            if not ingredients_text or len(ingredients_text.split('\n')) < 3:
                end_ingredients = self._extract_ingredients_from_end(page_text)
                if end_ingredients:
                    ingredients_text = end_ingredients
        
        if not ingredients_text:
            return None
        
        # Format ingredients properly
        return self._format_ingredients(ingredients_text)
    
    def _extract_ingredients_from_end(self, page_text: str) -> str:
        """Extract ingredients from the end of a page (after descriptive text)"""
        lines = page_text.split('\n')
        
        # Look for ingredient patterns in the last 20 lines
        ingredient_lines = []
        measurement_patterns = [
            r'^\d+\s*large\s+(whole\s+)?eggs?',  # "8 large whole eggs"
            r'^\d+\s*large\s+yolks?',            # "2 large yolks"
            r'^[¼⅜½¾]\s*cup\s+',                 # "¼ cup half-and-half"
            r'^[¼⅜½¾]\s*teaspoon\s+',            # "⅜ teaspoon table salt"
            r'^\d+\s*tablespoons?\s+',           # "1 tablespoon unsalted butter"
        ]
        
        # Scan backwards from the end
        for line in reversed(lines[-20:]):
            line = line.strip()
            if not line:
                continue
            
            # Check for measurement patterns
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in measurement_patterns):
                ingredient_lines.insert(0, line)  # Insert at beginning to maintain order
            elif ingredient_lines:
                # If we've started collecting ingredients and hit a non-ingredient, stop
                break
        
        return '\n'.join(ingredient_lines) if len(ingredient_lines) >= 2 else ""
    
    def _extract_ingredients_by_patterns(self, page_text: str) -> str:
        """Extract ingredients using pattern recognition"""
        lines = page_text.split('\n')
        ingredient_lines = []
        
        # Enhanced patterns from visual learning
        measurement_patterns = [
            r'^\d+\s*\(\d+.*?ounce\)',  # 2(15-ounce) cans
            r'^\d+\s*(cup|tablespoon|teaspoon|pound|ounce|tbsp|tsp|lb|oz)\s',
            r'^\d+.*?(large|medium|small|whole)\s',
            r'^\d+.*?(chopped|diced|minced|sliced|grated|stemmed|seeded)',
            r'^(\d+/\d+|\d+\.\d+)\s*(cup|tablespoon|teaspoon)',
            r'^\d+\s*(cloves?|cans?|packages?|pounds?|ounces?|slices?)\s',
            r'^[¾½¼⅓⅔⅛]',  # Fraction symbols
            r'^⅜\s*teaspoon',  # Special fraction
            r'^¼\s*(cup|teaspoon|tablespoon)',  # Common quarter measurements
        ]
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            # Check for measurement patterns
            is_ingredient = any(re.search(pattern, line, re.IGNORECASE) for pattern in measurement_patterns)
            
            if is_ingredient:
                # Additional validation - avoid instruction fragments
                if not any(word in line.lower() for word in ['cook', 'heat', 'process', 'transfer', 'minutes', 'beat eggs']):
                    ingredient_lines.append(line)
        
        return '\n'.join(ingredient_lines) if ingredient_lines else ""
    
    def _format_ingredients(self, ingredients_text: str) -> str:
        """Format ingredients with proper bullets and sections"""
        if not ingredients_text:
            return ""
        
        lines = ingredients_text.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Section headers (all caps, no numbers)
            if line.isupper() and not re.search(r'\d', line) and 2 <= len(line.split()) <= 4:
                formatted_lines.append(f"\n{line}:")
            else:
                # Ingredient lines
                if not line.startswith('•'):
                    formatted_lines.append(f"• {line}")
                else:
                    formatted_lines.append(line)
        
        return '\n'.join(formatted_lines).strip()
    
    def _extract_instructions_with_structure(self, page_text: str, structure: Dict) -> Optional[str]:
        """Enhanced instruction extraction using visual structure"""
        
        if 'START COOKING!' in structure['recipe_sections']:
            start_pos = page_text.find('START COOKING!')
            instructions_text = page_text[start_pos + len('START COOKING!'):].strip()
            
            # Parse numbered steps
            return self._parse_numbered_instructions(instructions_text)
        else:
            # Look for numbered steps anywhere on the page
            return self._extract_numbered_steps(page_text)
    
    def _parse_numbered_instructions(self, instructions_text: str) -> str:
        """Parse numbered instruction steps"""
        if not instructions_text:
            return ""
        
        lines = instructions_text.split('\n')
        formatted_steps = []
        current_step = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for numbered step
            step_match = re.match(r'^(\d+)\.\s*(.+)', line)
            if step_match:
                if current_step:
                    formatted_steps.append(current_step.strip())
                current_step = f"{step_match.group(1)}. {step_match.group(2)}"
            else:
                # Continuation of current step
                if current_step:
                    current_step += f" {line}"
        
        # Add last step
        if current_step:
            formatted_steps.append(current_step.strip())
        
        return '\n'.join(formatted_steps) if len(formatted_steps) >= 2 else ""
    
    def _extract_numbered_steps(self, page_text: str) -> str:
        """Extract numbered steps from anywhere in the text with proper multi-line handling"""
        lines = page_text.split('\n')
        steps = []
        current_step = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for numbered step start
            step_match = re.match(r'^(\d+)\.\s*(.+)', line)
            if step_match:
                # Save previous step if exists
                if current_step:
                    cleaned_step = self._clean_instruction_text(current_step.strip())
                    if cleaned_step and len(cleaned_step) > 30:
                        steps.append(cleaned_step)
                # Start new step
                current_step = f"{step_match.group(1)}. {step_match.group(2)}"
            else:
                # Continuation of current step
                if current_step and len(line) > 10:  # Substantial content
                    current_step += f" {line}"
        
        # Add final step
        if current_step:
            cleaned_step = self._clean_instruction_text(current_step.strip())
            if cleaned_step and len(cleaned_step) > 30:
                steps.append(cleaned_step)
        
        return '\n'.join(steps) if len(steps) >= 2 else ""
    
    def _clean_instruction_text(self, text: str) -> str:
        """Clean instruction text from PDF extraction artifacts"""
        if not text:
            return ""
        
        # Fix common PDF extraction issues
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces
        
        # Fix specific known patterns
        replacements = {
            'y olks': 'yolks',
            'hal f-and-hal f': 'half-and-half',
            'thor oughly': 'thoroughly',
            'pur e': 'pure',
            'mel ted': 'melted',
            'br own': 'brown',
            'swirl ing': 'swirling',
            'mixtur e': 'mixture',
            'heatpr oof': 'heatproof',
            'bot tom': 'bottom',
            'ski llet': 'skillet',
            'I mmediately': 'Immediately',
            'w armed': 'warmed',
            'S erve': 'Serve',
            'f old': 'fold',
            'sl ightly': 'slightly',
            'ar e': 'are',
            'col or': 'color',
            'unti l': 'until',
            'but ter': 'butter',
            'lea ves': 'leaves',
            'wi th': 'with',
            'sal t': 'salt',
            ' an d ': ' and ',
            'coa t': 'coat'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Fix incomplete sentences (like "do not" at end)
        if text.endswith(' do not'):
            text += ' overbeat.'
        
        return text.strip()
    
    def _extract_servings_enhanced(self, page_text: str) -> Optional[str]:
        """Enhanced serving extraction"""
        patterns = [
            r'(SERVES|MAKES)\s+(\d+)(?:\s+(?:TO|OR)\s+(\d+))?',
            r'YIELD[S]?\s*:?\s*(\d+)',
            r'(\d+)\s+SERVINGS'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                if len(match.groups()) >= 3 and match.group(3):
                    return f"Serves {match.group(2)}-{match.group(3)}"
                elif len(match.groups()) >= 2 and match.group(2):
                    return f"Serves {match.group(2)}"
                elif match.group(1):
                    return f"Serves {match.group(1)}"
        
        return None
    
    def _extract_timing_enhanced(self, page_text: str) -> Optional[str]:
        """Enhanced timing extraction"""
        patterns = [
            r'(\d+)\s+(MINUTES?|MINS?|HOURS?|HRS?)',
            r'TOTAL\s+TIME\s*:?\s*(\d+)\s+(MINUTES?|HOURS?)',
            r'PREP\s+TIME\s*:?\s*(\d+)\s+(MINUTES?|HOURS?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                time_value = match.group(1) if len(match.groups()) >= 1 else match.group(2)
                time_unit = match.group(2) if len(match.groups()) >= 2 else match.group(1)
                return f"{time_value} {time_unit.lower()}"
        
        return None
    
    def _infer_category(self, title: str) -> str:
        """Enhanced category inference"""
        title_lower = title.lower()
        
        categories = {
            'Appetizers & Dips': ['appetizer', 'dip', 'bite', 'starter', 'hummus', 'guacamole'],
            'Soups & Stews': ['soup', 'stew', 'chili', 'bisque', 'chowder'],
            'Salads': ['salad', 'slaw'],
            'Main Dishes': ['chicken', 'beef', 'pork', 'fish', 'salmon', 'turkey', 'lamb'],
            'Pasta & Rice': ['pasta', 'spaghetti', 'rice', 'risotto', 'noodle'],
            'Vegetables & Sides': ['vegetable', 'broccoli', 'carrot', 'potato', 'beans', 'refried'],
            'Eggs & Breakfast': ['eggs', 'deviled', 'scrambled', 'omelet', 'pancake', 'waffle'],
            'Breads & Baking': ['bread', 'biscuit', 'muffin', 'roll'],
            'Desserts': ['cake', 'cookie', 'pie', 'tart', 'chocolate', 'dessert'],
            'Sauces & Toppings': ['sauce', 'topping', 'dressing', 'marinade']
        }
        
        for category, keywords in categories.items():
            if any(keyword in title_lower for keyword in keywords):
                return category
        
        return 'Main Dishes'
    
    def _clean_title(self, title: str) -> str:
        """Enhanced title cleaning"""
        # Remove common artifacts
        title = re.sub(r'^(recipe|atk|test kitchen|america.*test.*kitchen)[:.]?\s*', '', title, flags=re.IGNORECASE)
        
        # Remove "Why This Recipe Works" prefix
        title = re.sub(r'^why\s+this\s+recipe\s+works\s*', '', title, flags=re.IGNORECASE)
        
        # Remove page number artifacts
        title = re.sub(r'\s*\d+\s*$', '', title)
        
        # Fix truncation issues - if title ends with hyphen, it's likely truncated
        if title.endswith('-'):
            title = title[:-1].strip()
        
        title = title.strip()
        
        # Convert screaming caps to title case if reasonable
        if title.isupper() and len(title) < 60:
            title = title.title()
        
        # Fix common PDF extraction issues
        title = re.sub(r'\s+', ' ', title)  # Multiple spaces
        
        # Reject obviously broken titles
        if (len(title) < 3 or 
            title.lower() in ['prepackaged cheese and guacamole and', 'recipe works', 'dipping sauce'] or
            title.lower().startswith('serve the') or
            ' topped with' in title.lower()):
            return None
        
        return title
    
    def _print_summary(self):
        """Print comprehensive extraction summary"""
        stats = self.extraction_stats
        
        logger.info(f"\n👁️🧠 VISUAL + SEMANTIC EXTRACTION SUMMARY:")
        logger.info("=" * 70)
        logger.info(f"📄 Pages processed: {stats['pages_processed']}")
        logger.info(f"👁️ Pages with visual recipe structure: {stats['pages_with_recipes']}")
        logger.info(f"🔍 Recipe candidates found: {stats['recipe_candidates_found']}")
        logger.info(f"👁️ Visual validations: {stats['visual_validations']}")
        logger.info(f"🧠 Semantic validations: {stats['semantic_validations']}")
        logger.info(f"🚫 Artifacts rejected: {stats['artifacts_rejected']}")
        logger.info(f"✅ Recipes validated: {stats['recipes_validated']}")
        
        if stats['quality_scores']:
            avg_quality = sum(stats['quality_scores']) / len(stats['quality_scores'])
            logger.info(f"📊 Average semantic quality: {avg_quality:.2f}")
        
        logger.info(f"\n🚫 REJECTION BREAKDOWN:")
        for reason, count in stats['rejection_reasons'].items():
            if count > 0:
                logger.info(f"  {reason.replace('_', ' ').title()}: {count}")
        
        if self.extracted_recipes:
            logger.info(f"\n✅ VALIDATED RECIPES:")
            for i, recipe in enumerate(self.extracted_recipes[:10], 1):
                title = recipe.get('title', 'Unknown')
                visual_conf = recipe.get('visual_confidence', 0)
                semantic_conf = recipe.get('semantic_validation', {}).get('confidence_score', 0)
                logger.info(f"  {i}. '{title}' (visual: {visual_conf}, semantic: {semantic_conf:.2f})")
            
            if len(self.extracted_recipes) > 10:
                logger.info(f"  ... and {len(self.extracted_recipes) - 10} more")
    
    def save_to_database(self, dry_run: bool = False) -> int:
        """Save validated recipes to database"""
        if not self.extracted_recipes:
            logger.warning("⚠️ No recipes to save")
            return 0
        
        logger.info(f"\n💾 SAVING VISUAL + SEMANTIC EXTRACTION RESULTS")
        logger.info("=" * 60)
        logger.info(f"📋 Recipes to save: {len(self.extracted_recipes)}")
        logger.info(f"👁️ Visual structure validated")
        logger.info(f"🧠 Semantic quality assured")
        
        if dry_run:
            logger.info("🔍 DRY RUN - No database changes")
            return len(self.extracted_recipes)
        
        # Insert recipes
        inserted_count = 0
        for recipe in self.extracted_recipes:
            try:
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Add enhanced metadata
                    validation = recipe.get('semantic_validation', {})
                    visual_info = f"Visual Confidence: {recipe.get('visual_confidence', 0)}, "
                    semantic_note = f"Semantic Validation: Valid Recipe " \
                                  f"(confidence: {validation.get('confidence_score', 0):.2f}, " \
                                  f"quality: {validation.get('quality_metrics', {})})"
                    
                    description = recipe.get('description', '')
                    enhanced_description = f"{visual_info}{semantic_note}"
                    if description:
                        description += f"\n\n{enhanced_description}"
                    else:
                        description = enhanced_description
                    
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
        
        logger.info(f"✅ Successfully inserted {inserted_count} enhanced recipes")
        return inserted_count
    
    def _contains_known_ingredients(self, text: str) -> bool:
        """Check if text contains known ingredients from our ingredient database"""
        if not text:
            return False
            
        text_lower = text.lower()
        
        # Check against canonical ingredient names
        for ingredient_id, data in self.ingredient_engine.canonical_ingredients.items():
            ingredient_name = data['name'].lower()
            
            # Extract the core ingredient name (remove measurements and modifiers)
            core_name = self._extract_core_ingredient_name(ingredient_name)
            
            if core_name and len(core_name) >= 3:  # Avoid very short matches
                if core_name in text_lower:
                    return True
        
        return False
    
    def _extract_core_ingredient_name(self, ingredient_name: str) -> str:
        """Extract the core ingredient name from a full ingredient description"""
        
        # Remove common measurement patterns
        cleaned = re.sub(r'^\d+.*?(cup|tablespoon|teaspoon|slice|large|small|pound|ounce|stick|clove)', '', ingredient_name, flags=re.IGNORECASE)
        
        # Remove common modifiers
        modifiers = ['fresh', 'dried', 'chopped', 'diced', 'minced', 'sliced', 'grated', 'ground', 'whole', 'raw', 'cooked']
        for modifier in modifiers:
            cleaned = re.sub(r'\b' + modifier + r'\b', '', cleaned, flags=re.IGNORECASE)
        
        # Clean up extra spaces and return the core name
        core_name = ' '.join(cleaned.split()).strip()
        
        return core_name if len(core_name) >= 3 else ingredient_name


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ATK 25th Anniversary Visual + Semantic Extractor')
    parser.add_argument('--max-recipes', type=int, help='Maximum recipes to extract')
    parser.add_argument('--start-page', type=int, default=1, help='Start page')
    parser.add_argument('--end-page', type=int, help='End page')
    parser.add_argument('--dry-run', action='store_true', help='Don\'t save to database')
    
    args = parser.parse_args()
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
    
    if not os.path.exists(pdf_path):
        logger.error(f"❌ PDF not found: {pdf_path}")
        return
    
    # Create enhanced extractor
    extractor = ATK25thVisualSemanticExtractor(pdf_path)
    
    # Extract recipes
    recipes = extractor.extract_recipes(
        max_recipes=args.max_recipes,
        start_page=args.start_page,
        end_page=args.end_page
    )
    
    # Save results
    if recipes:
        inserted_count = extractor.save_to_database(dry_run=args.dry_run)
        
        logger.info(f"\n🎉 VISUAL + SEMANTIC EXTRACTION COMPLETE!")
        logger.info(f"👁️🧠 Multi-layer validation with enhanced detection")
        logger.info(f"📊 Results: {len(recipes)} recipes extracted, {inserted_count} saved")

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
        import re
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


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ATK 25th Anniversary Visual + Semantic Extractor')
    parser.add_argument('--max-recipes', type=int, help='Maximum recipes to extract')
    parser.add_argument('--start-page', type=int, default=1, help='Start page')
    parser.add_argument('--end-page', type=int, help='End page')
    parser.add_argument('--dry-run', action='store_true', help='Don\'t save to database')
    
    args = parser.parse_args()
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
    
    if not os.path.exists(pdf_path):
        logger.error(f"❌ PDF not found: {pdf_path}")
        return
    
    # Create enhanced extractor
    extractor = ATK25thVisualSemanticExtractor(pdf_path)
    
    # Extract recipes
    recipes = extractor.extract_recipes(
        max_recipes=args.max_recipes,
        start_page=args.start_page,
        end_page=args.end_page
    )
    
    # Save results
    if recipes:
        inserted_count = extractor.save_to_database(dry_run=args.dry_run)
        
        logger.info(f"\n🎉 VISUAL + SEMANTIC EXTRACTION COMPLETE!")
        logger.info(f"👁️🧠 Multi-layer validation with enhanced detection")
        logger.info(f"📊 Results: {len(recipes)} recipes extracted, {inserted_count} saved")


if __name__ == "__main__":
    main()
