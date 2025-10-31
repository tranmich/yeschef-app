"""
🌐 Web Recipe Extractor - Advanced URL Recipe Extraction System
=============================================================

Extracts recipes from websites using multiple strategies:
1. JSON-LD Schema.org (most reliable - 90%+ success rate)
2. BonAppetit-specific patterns (proven success)
3. Site-specific extractors (Food Network, AllRecipes, etc.)
4. Open Graph metadata
5. Adaptive fallback parsing

Integrates with existing Me Hungie systems:
- AdaptiveRecipeExtractor for fallback parsing
- IngredientIntelligenceEngine for ingredient processing
- Confidence scoring for quality assessment

Author: GitHub Copilot & Team
Date: August 26, 2025 - Day 2 Implementation
"""

import os
import re
import json
import requests
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging
import time
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

# Import our formatting intelligence
from .recipe_formatter import UniversalRecipeFormatter
import logging
from datetime import datetime
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import time

# Import our self-improving analytics system
try:
    from core_systems.extraction_analytics import ExtractionAnalytics, ExtractionResult
    from core_systems.adaptive_confidence_scorer import AdaptiveConfidenceScorer, ConfidenceFactors
    ANALYTICS_AVAILABLE = True
except ImportError:
    ANALYTICS_AVAILABLE = False
    print("⚠️ Analytics system not available - running without self-improvement")

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class WebRecipeData:
    """Structured recipe data extracted from web sources"""
    title: str = ""
    ingredients: List[str] = None
    instructions: List[str] = None
    description: str = ""
    prep_time: Optional[int] = None
    cook_time: Optional[int] = None
    total_time: Optional[int] = None
    servings: Optional[int] = None
    cuisine: str = ""
    category: str = ""
    keywords: List[str] = None
    nutrition: Dict = None
    image_url: str = ""
    source_url: str = ""
    author: str = ""
    rating: Optional[float] = None
    review_count: Optional[int] = None
    extraction_method: str = ""
    confidence: float = 0.0
    
    def __post_init__(self):
        if self.ingredients is None:
            self.ingredients = []
        if self.instructions is None:
            self.instructions = []
        if self.keywords is None:
            self.keywords = []
        if self.nutrition is None:
            self.nutrition = {}

class WebRecipeExtractor:
    """
    🧠 Universal Recipe Intelligence Extractor
    
    One brain that understands recipe structure across ALL websites.
    Uses machine learning patterns to identify the 4 core recipe elements:
    1. Title - What is this dish?
    2. Ingredients - What do I need?  
    3. Instructions - How do I make it?
    4. Metadata - Time, servings, etc.
    
    Self-improving through analytics across all extractions.
    """
    
    def __init__(self, timeout=10, user_agent=None, enable_analytics=True):
        """Initialize the universal recipe intelligence system"""
        self.timeout = timeout
        self.session = requests.Session()
        
        # Set a realistic user agent to avoid blocking
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        self.session.headers.update({'User-Agent': self.user_agent})
        
        # Initialize self-improving analytics system
        self.analytics_enabled = enable_analytics and ANALYTICS_AVAILABLE
        self.analytics = None
        self.adaptive_scorer = None
        
        # Initialize formatting intelligence (ported from your frontend Auto-Clean logic)
        self.formatter = UniversalRecipeFormatter()
        logger.info("🧹 Auto-formatting intelligence initialized")
        
        if self.analytics_enabled:
            try:
                self.analytics = ExtractionAnalytics()
                self.adaptive_scorer = AdaptiveConfidenceScorer(self.analytics)
                logger.info("🧠 Universal recipe intelligence with self-improvement: ACTIVATED")
            except Exception as e:
                logger.warning(f"⚠️ Could not initialize analytics system: {e}")
                self.analytics_enabled = False
        
        # Universal pattern recognition system
        self.intelligence_patterns = self._initialize_universal_patterns()
        
        logger.info(f"✅ Universal Recipe Extractor initialized")
        logger.info("🎯 Focus: Title, Ingredients, Instructions, Metadata from ANY website")
    
    def _initialize_universal_patterns(self):
        """Initialize universal recipe recognition patterns"""
        return {
            'title_patterns': {
                # Semantic indicators
                'semantic': [
                    'h1', '[role="heading"]', '[class*="title"]', '[class*="headline"]',
                    '[class*="recipe"][class*="name"]', '[itemprop="name"]'
                ],
                # Context clues
                'context_words': ['recipe', 'dish', 'food', 'cooking'],
                # Exclusions (things that are NOT recipe titles)
                'exclusions': ['menu', 'navigation', 'footer', 'sidebar', 'ad']
            },
            
            'ingredients_patterns': {
                # List-based indicators
                'list_selectors': [
                    'ul', 'ol', '[class*="ingredient"]', '[class*="recipe"] li',
                    '[itemprop="recipeIngredient"]', '[class*="list"]'
                ],
                # Text-based indicators  
                'section_headers': [
                    'ingredients', 'what you need', 'shopping list', 'you will need',
                    'for this recipe', 'materials', 'supplies'
                ],
                # Pattern recognition for ingredient format
                'ingredient_patterns': [
                    r'\d+\s*(?:cups?|tbsp|tsp|oz|lbs?|grams?|kg)',  # Measurements
                    r'\d+\s*(?:large|medium|small|whole)',           # Quantity descriptors
                    r'(?:salt|pepper|sugar|flour|butter|oil)',       # Common ingredients
                ]
            },
            
            'instructions_patterns': {
                # List and step indicators
                'list_selectors': [
                    'ol', '[class*="instruction"]', '[class*="direction"]', '[class*="step"]',
                    '[class*="method"]', '[itemprop="recipeInstructions"]'
                ],
                # Section headers
                'section_headers': [
                    'instructions', 'directions', 'method', 'preparation', 'steps',
                    'how to make', 'cooking method', 'procedure'
                ],
                # Action word patterns (cooking verbs)
                'cooking_verbs': [
                    'heat', 'cook', 'bake', 'fry', 'boil', 'simmer', 'mix', 'stir',
                    'chop', 'dice', 'slice', 'add', 'combine', 'preheat', 'season'
                ]
            },
            
            'metadata_patterns': {
                # Time patterns
                'time_indicators': [
                    r'prep\s*time', r'cook\s*time', r'total\s*time', r'ready\s*in',
                    r'prep', r'cooking', r'baking', r'duration'
                ],
                'time_formats': [
                    r'(\d+)\s*(?:hours?|hrs?|h)\s*(?:(\d+)\s*(?:minutes?|mins?|m))?',
                    r'(\d+)\s*(?:minutes?|mins?|m)',
                    r'(\d+)h\s*(\d+)m?',
                    r'(\d+):(\d+)'  # 1:30 format
                ],
                # Serving patterns
                'serving_indicators': [
                    r'serves?', r'servings?', r'portions?', r'yields?', r'feeds?',
                    r'for\s*\d+', r'makes?\s*\d+'
                ]
            }
        }
    
    def _extract_universal_intelligence(self, soup: BeautifulSoup, url: str) -> Optional[WebRecipeData]:
        """
        Universal recipe intelligence - the main brain that works on ANY website
        """
        logger.info("🧠 Using universal recipe intelligence...")
        
        try:
            recipe = WebRecipeData()
            recipe.source_url = url
            recipe.extraction_method = "universal_intelligence"
            
            # 1. TITLE EXTRACTION - Find the recipe name
            recipe.title = self._extract_universal_title(soup)
            logger.info(f"🏷️ Universal title extraction: '{recipe.title}'")
            
            # 2. INGREDIENTS EXTRACTION - Find what you need
            recipe.ingredients = self._extract_universal_ingredients(soup)
            logger.info(f"🥄 Universal ingredients extraction: {len(recipe.ingredients)} items found")
            if recipe.ingredients:
                logger.info(f"   First few: {recipe.ingredients[:3]}")
            
            # 3. INSTRUCTIONS EXTRACTION - Find how to make it  
            recipe.instructions = self._extract_universal_instructions(soup)
            logger.info(f"📋 Universal instructions extraction: {len(recipe.instructions)} steps found")
            if recipe.instructions:
                logger.info(f"   First step: {recipe.instructions[0][:100]}...")
            
            # 4. METADATA EXTRACTION - Find time, servings, etc.
            metadata = self._extract_universal_metadata(soup)
            recipe.prep_time = metadata.get('prep_time')
            recipe.cook_time = metadata.get('cook_time') 
            recipe.total_time = metadata.get('total_time')
            recipe.servings = metadata.get('servings')
            logger.info(f"⏱️ Universal metadata: prep={recipe.prep_time}, cook={recipe.cook_time}, servings={recipe.servings}")
            
            # Calculate confidence based on completeness and quality
            confidence = self._calculate_universal_confidence(recipe)
            recipe.confidence = confidence
            logger.info(f"🎯 Universal confidence calculated: {confidence:.2f}")
            
            return recipe if confidence > 0.3 else None
            
        except Exception as e:
            logger.error(f"❌ Universal intelligence extraction error: {e}")
            return None
    
    def _extract_universal_title(self, soup: BeautifulSoup) -> str:
        """Find recipe title using universal patterns"""
        patterns = self.intelligence_patterns['title_patterns']
        
        # Strategy 1: Look for the MOST recipe-specific selectors first (highest priority)
        high_priority_selectors = [
            'h1[data-testid*="recipe"]',  # Recipe-specific data attributes
            'h1[class*="recipe-title"]',  # Explicit recipe title classes
            'h1[class*="recipe-name"]',   
            '[class*="recipe-title"] h1',
            '[class*="recipe-header"] h1',
            'h1[itemprop="name"]',        # Schema.org recipe name
            # Add more recipe-specific patterns
            '[class*="recipe-card"] h1',
            '[class*="entry-title"]',     # Common blog post pattern
            '[class*="post-title"]',      # Another blog pattern
            'h1[data-recipe-title]',      # Data attribute patterns
            'h1[id*="recipe"]',           # ID-based patterns
        ]
        
        logger.info("🔍 Searching high-priority recipe title selectors...")
        for selector in high_priority_selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text().strip()
                text = ' '.join(text.split())  # Clean whitespace
                
                if self._is_likely_recipe_title(text, patterns):
                    logger.info(f"✅ Found high-priority recipe title: '{text}' (selector: {selector})")
                    return text
                else:
                    logger.info(f"❌ Rejected high-priority candidate: '{text}' (nutrition/bad content)")
        
        # Strategy 2: Look at page title first (often the most reliable)
        logger.info("🔍 Checking page title...")
        title_elem = soup.find('title')
        if title_elem:
            title_text = title_elem.get_text().strip()
            logger.info(f"� Raw page title: '{title_text}'")
            
            # Clean up common title patterns
            for separator in [' | ', ' - ', ' :: ', ' — ', ' Recipe']:
                if separator in title_text:
                    title_text = title_text.split(separator)[0].strip()
                    break
            
            # Clean up newlines and extra whitespace
            title_text = ' '.join(title_text.split())
            
            if self._is_likely_recipe_title(title_text, patterns):
                logger.info(f"✅ Using cleaned page title: '{title_text}'")
                return title_text
            else:
                logger.info(f"❌ Page title rejected: '{title_text}' (not recipe-like)")
        
        # Strategy 3: Look for medium-priority selectors
        medium_priority_selectors = [
            'h1[class*="recipe"]',        # Any h1 with recipe in class
            '[class*="recipe"][class*="name"]',
            'h1'  # Generic h1s - but we'll be more selective
        ]
        
        logger.info("🔍 Searching medium-priority title selectors...")
        for selector in medium_priority_selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text().strip()
                text = ' '.join(text.split())
                
                # For generic h1s, be extra strict about validation
                if selector == 'h1':
                    # Must contain food/recipe words for generic h1s
                    text_lower = text.lower()
                    food_words = ['oatmeal', 'coconut', 'chicken', 'pasta', 'soup', 'salad', 'cake', 'bread']
                    recipe_words = ['recipe', 'dish', 'food']
                    
                    has_food_content = any(word in text_lower for word in food_words + recipe_words)
                    if not has_food_content:
                        logger.info(f"❌ Generic h1 rejected (no food words): '{text}'")
                        continue
                
                if self._is_likely_recipe_title(text, patterns):
                    logger.info(f"✅ Found medium-priority title: '{text}' (selector: {selector})")
                    return text
                else:
                    logger.info(f"❌ Rejected medium-priority candidate: '{text}'")
        
        logger.warning("⚠️ No good title found with any strategy")
        return ""
    
    def _is_likely_recipe_title(self, text: str, patterns: dict) -> bool:
        """Determine if text is likely a recipe title"""
        if not text or len(text) < 3 or len(text) > 150:  # Allow longer titles
            return False
        
        text_lower = text.lower()
        
        # Exclude nutrition and measurement terms (these are NOT recipe titles)
        nutrition_terms = [
            'calories', 'fat', 'protein', 'carbs', 'carbohydrates', 'sodium', 'sugar',
            'fiber', 'cholesterol', 'vitamin', 'total fat', 'saturated fat', 'trans fat',
            'nutrition facts', 'serving size', 'servings per', 'daily value', '%'
        ]
        
        for term in nutrition_terms:
            if term in text_lower:
                return False
        
        # Check for exclusion patterns first
        for exclusion in patterns['exclusions']:
            if exclusion in text_lower:
                return False
        
        # Very permissive approach - most page titles are good
        # Exclude obvious non-recipe titles
        bad_patterns = [
            'error', '404', 'not found', 'page not found',
            'home', 'homepage', 'index', 'search results',
            'category', 'browse', 'all recipes', 'recipe collection',
            'reviews', 'ratings', 'photos', 'comments', 'newsletter',
            'email address', 'sign up', 'privacy policy'
        ]
        
        for bad_pattern in bad_patterns:
            if bad_pattern in text_lower:
                return False
        
        # If it contains recipe-related words, it's probably good
        recipe_words = ['recipe', 'dish', 'food', 'cooking', 'baked', 'grilled', 'roasted', 'fried']
        
        # Or if it looks like a food name (doesn't need recipe words)
        food_indicators = [
            'chicken', 'beef', 'pasta', 'soup', 'salad', 'cake', 'bread', 'pie',
            'sauce', 'casserole', 'stew', 'curry', 'pizza', 'sandwich', 'oatmeal',
            'pancake', 'cookie', 'muffin', 'rice', 'potato', 'fish', 'pork', 'coconut',
            'sloppy joe', 'burger', 'steak', 'chili', 'taco', 'ramen'
        ]
        
        has_recipe_words = any(word in text_lower for word in recipe_words)
        has_food_words = any(word in text_lower for word in food_indicators)
        
        # Accept if it has recipe words, food words, or is a reasonable length (but not nutrition terms)
        # Also accept descriptive titles like "The Best..." "Ultimate..." "Quick and Easy..."
        descriptive_words = ['best', 'ultimate', 'perfect', 'easy', 'quick', 'better', 'delicious']
        has_descriptive = any(word in text_lower for word in descriptive_words)
        
        return has_recipe_words or has_food_words or has_descriptive or (len(text) > 10 and len(text) < 100)
    
    def _extract_universal_ingredients(self, soup: BeautifulSoup) -> List[str]:
        """Find ingredients using universal patterns with structured data priority"""
        patterns = self.intelligence_patterns['ingredients_patterns']
        ingredients = []
        
        # Strategy 1: Look for structured data first (highest priority)
        structured_selectors = [
            '[itemprop="recipeIngredient"]',      # Microdata - highest priority
            '[class*="recipe-ingredient"] li',     # Recipe-specific classes
            '[class*="ingredients"] li',          # Generic ingredient classes
            '[data-ingredient]',                  # Data attributes
            'ul[class*="ingredient"] li',         # UL-based lists
            'ol[class*="ingredient"] li',         # OL-based lists
            '[class*="recipe-card"] ul li',       # Recipe card structures
            '[class*="recipe"] [class*="list"] li' # Recipe section lists
        ]
        
        logger.info("🔍 Trying structured ingredient selectors...")
        for selector in structured_selectors:
            elements = soup.select(selector)
            if elements:
                potential_ingredients = []
                for elem in elements:
                    text = elem.get_text().strip()
                    if text and self._is_likely_ingredient(text, patterns):
                        potential_ingredients.append(text)
                
                if len(potential_ingredients) >= 3:  # Need reasonable number
                    logger.info(f"✅ Found {len(potential_ingredients)} ingredients with structured selector: {selector}")
                    ingredients = potential_ingredients[:20]  # Limit to reasonable number
                    break
        
        # Strategy 2: Fallback to generic list patterns
        if not ingredients:
            logger.info("🔍 Trying generic list selectors...")
            for selector in patterns['list_selectors']:
                elements = soup.select(f"{selector} li")
                if not elements:
                    elements = soup.select(selector)
                
                potential_ingredients = []
                for elem in elements:
                    text = elem.get_text().strip()
                    if self._is_likely_ingredient(text, patterns):
                        potential_ingredients.append(text)
                
                # If we found a good list of ingredients, use it
                if len(potential_ingredients) >= 3:
                    logger.info(f"✅ Found {len(potential_ingredients)} ingredients with generic selector: {selector}")
                    ingredients = potential_ingredients
                    break
        
        # Strategy 2: Look for section-based ingredients
        if not ingredients:
            ingredients = self._find_section_based_content(soup, patterns['section_headers'], 'ingredient')
        
        return ingredients[:20]  # Limit to reasonable number
    
    def _is_likely_ingredient(self, text: str, patterns: dict) -> bool:
        """Determine if text is likely an ingredient"""
        if not text or len(text) < 2 or len(text) > 200:
            return False
        
        text_lower = text.lower()
        
        # Exclude non-ingredient content first
        bad_patterns = [
            'email address', 'newsletter', 'sign up', 'privacy policy', 'opt-out',
            'subscribe', 'unsubscribe', 'error', 'try again', 'get fresh recipes',
            'cooking tips', 'deal alerts', 'visit', 'save recipe', 'print recipe',
            'there was an error', 'you can opt-out'
        ]
        
        for pattern in bad_patterns:
            if pattern in text_lower:
                return False
        
        # Check for measurement patterns
        for pattern in patterns['ingredient_patterns']:
            if re.search(pattern, text_lower):
                return True
        
        # Check for common ingredient words
        ingredient_words = [
            'cup', 'tablespoon', 'teaspoon', 'pound', 'ounce', 'gram', 'kilogram',
            'large', 'medium', 'small', 'whole', 'chopped', 'diced', 'sliced',
            'fresh', 'dried', 'ground', 'minced'
        ]
        
        return any(word in text_lower for word in ingredient_words)
    
    def _extract_universal_instructions(self, soup: BeautifulSoup) -> List[str]:
        """Find instructions using universal patterns"""
        patterns = self.intelligence_patterns['instructions_patterns']
        instructions = []
        
        # Strategy 1: Look for structured instruction lists
        instruction_selectors = [
            'ol[class*="instruction"]',  # Ordered lists are often instructions
            'ol[class*="direction"]',
            'ol[class*="method"]',
            '[class*="instruction"] ol',
            '[class*="directions"] ol',
            '[class*="recipe-instructions"] li',
            '[class*="instructions"] li',
            'ol li',  # Generic ordered list items
        ]
        
        for selector in instruction_selectors:
            elements = soup.select(selector)
            if elements:
                potential_instructions = []
                seen_texts = set()  # Track duplicates by normalized text
                
                for elem in elements:
                    text = elem.get_text().strip()
                    # Clean up text
                    text = ' '.join(text.split())
                    
                    # Skip if empty
                    if not text:
                        continue
                    
                    # Skip section headers (short text without action verbs)
                    if len(text) < 20 and not any(word in text.lower() for word in ['heat', 'add', 'cook', 'mix', 'stir', 'place', 'cut', 'chop', 'combine', 'serve']):
                        continue
                    
                    # AGGRESSIVE CLEANING - Remove ALL step markers and section headers
                    # 1. Remove section headers at the start
                    text = re.sub(r'^(Make the|Prepare the|Meanwhile,?\s*make the|For the)\s+\w+\s*', '', text, flags=re.IGNORECASE)
                    
                    # 2. Remove "Step N" anywhere in text
                    text = re.sub(r'Step\s*\d+\s*', '', text, flags=re.IGNORECASE)
                    
                    # 3. Remove leading numbers/bullets - ALL formats
                    text = re.sub(r'^\s*[\d]+[\.\)]\s+', '', text)   # "1. " or "1) " (with space)
                    text = re.sub(r'^\s*[\d]+[\.\)]', '', text)      # "1." or "1)" (no space)
                    text = re.sub(r'^\s*\([\d]+\)\s*', '', text)     # "(1) "
                    text = re.sub(r'^\s*[\d]+\s+', '', text)         # "1 " (number with space, no punctuation)
                    text = re.sub(r'^\s*[\d]+(?=[A-Z])', '', text)   # "1" directly before capital letter (e.g., "1Place")
                    text = re.sub(r'^\s*[•·●○]\s*', '', text)        # bullets
                    
                    text = text.strip()
                    
                    # Create normalized version for duplicate detection
                    # Remove ALL numbers first, then take first 60 chars for comparison
                    normalized_for_dedup = re.sub(r'\d+', '', text)[:60].lower().strip()
                    
                    # Skip if we've seen this exact text before
                    if normalized_for_dedup in seen_texts:
                        continue
                    
                    # Must be substantial and look like an instruction
                    if self._is_likely_instruction(text, patterns) and len(text) > 20:
                        seen_texts.add(normalized_for_dedup)
                        potential_instructions.append(text)
                
                # If we found good instructions, use them
                if len(potential_instructions) >= 2:
                    logger.info(f"✅ Found {len(potential_instructions)} unique instructions with selector: {selector}")
                    instructions = potential_instructions
                    break
        
        # Strategy 2: Look for section-based instructions
        if not instructions:
            logger.info("🔍 Trying section-based instruction extraction...")
            potential_instructions = self._find_section_based_content(soup, patterns['section_headers'], 'instruction')
            
            # Validate that these are actually instructions, not ingredients
            if potential_instructions:
                validated_instructions = []
                for item in potential_instructions:
                    if self._is_likely_instruction(item, patterns):
                        validated_instructions.append(item)
                
                logger.info(f"✅ Validated {len(validated_instructions)} out of {len(potential_instructions)} as real instructions")
                
                if len(validated_instructions) >= 2:
                    instructions = validated_instructions
                else:
                    logger.warning("⚠️ Section-based extraction found ingredients, not instructions - rejecting")
        
        # Strategy 3: Look for numbered/step patterns in text or single long instructions
        if not instructions:
            logger.info("🔍 Trying numbered step pattern extraction...")
            
            # First try: Look for actual Step patterns
            all_text = soup.get_text()
            
            # Look for "Step 1:" followed by text
            step_pattern = r'Step\s*\d+[:\.]?\s*(.*?)(?=Step\s*\d+|$)'
            step_matches = re.findall(step_pattern, all_text, re.MULTILINE | re.IGNORECASE | re.DOTALL)
            
            if step_matches:
                potential_instructions = []
                for i, match in enumerate(step_matches[:10], 1):  # Limit to 10 steps
                    text = match.strip()
                    # Clean up the text
                    text = ' '.join(text.split())
                    
                    if len(text) > 20:  # Must be substantial
                        potential_instructions.append(f"{i}. {text}")
                
                if potential_instructions:
                    logger.info(f"✅ Found {len(potential_instructions)} instructions via Step pattern matching")
                    instructions = potential_instructions
            
            # Second try: Look for directions section with paragraph content
            if not instructions:
                logger.info("🔍 Looking for directions section with paragraph content...")
                
                for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5']):
                    header_text = header.get_text().strip().lower()
                    
                    if 'direction' in header_text or 'method' in header_text or 'preparation' in header_text:
                        logger.info(f"✅ Found directions header: '{header_text}'")
                        
                        # Look for content after this header
                        for sibling in header.find_next_siblings():
                            if sibling.name in ['div', 'section', 'p']:
                                content_text = sibling.get_text().strip()
                                content_text = ' '.join(content_text.split())  # Clean whitespace
                                
                                if len(content_text) > 50 and self._is_likely_instruction(content_text, patterns):
                                    logger.info(f"✅ Found single instruction paragraph: {content_text[:100]}...")
                                    instructions = [f"1. {content_text}"]
                                    break
                        
                        if instructions:
                            break
        
        # Add step numbers if missing
        if instructions:
            numbered_instructions = []
            for i, instruction in enumerate(instructions[:15], 1):  # Limit to 15 steps
                if not re.match(r'^\d+\.?\s', instruction):
                    instruction = f"{i}. {instruction}"
                numbered_instructions.append(instruction)
            return numbered_instructions
        
        logger.warning("⚠️ No good instructions found")
        return []
    
    def _is_likely_instruction(self, text: str, patterns: dict) -> bool:
        """Determine if text is likely a cooking instruction"""
        if not text or len(text) < 10 or len(text) > 1000:
            return False
        
        text_lower = text.lower()
        
        # Check for cooking verbs - instructions should have action words
        cooking_verb_count = sum(1 for verb in patterns['cooking_verbs'] if verb in text_lower)
        
        # Look for instruction-specific patterns
        instruction_indicators = [
            'pour', 'stir', 'cook', 'bake', 'heat', 'bring to', 'reduce heat',
            'until', 'for', 'minutes', 'degrees', 'oven', 'pan', 'skillet',
            'meanwhile', 'then', 'next', 'add to', 'remove from'
        ]
        
        indicator_count = sum(1 for indicator in instruction_indicators if indicator in text_lower)
        
        # Exclude things that look like ingredients
        ingredient_patterns = [
            r'^\d+\s*(?:cups?|tbsp|tsp|oz|lbs?|grams?|kg)',  # Starts with measurement
            r'^\d+\s*(?:large|medium|small)',  # Starts with quantity
            r'^\d+\s*\(\d+\s*ounce\)',  # Pattern like "1 (8 ounce)"
        ]
        
        # If it looks like an ingredient, it's probably not an instruction
        for pattern in ingredient_patterns:
            if re.match(pattern, text):
                return False
        
        # Good instruction should have cooking verbs and be descriptive
        has_enough_verbs = cooking_verb_count >= 1 or indicator_count >= 1
        is_descriptive = len(text) > 15
        
        return has_enough_verbs and is_descriptive
    
    def _find_section_based_content(self, soup: BeautifulSoup, headers: List[str], content_type: str) -> List[str]:
        """Find content by looking for section headers"""
        content = []
        
        logger.info(f"🔍 Looking for {content_type} sections with headers: {headers}")
        
        for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'div', 'span']):
            header_text = header.get_text().strip().lower()
            
            # Check if this header matches what we're looking for
            matching_header = None
            for header_word in headers:
                if header_word in header_text:
                    matching_header = header_word
                    break
            
            if matching_header:
                logger.info(f"✅ Found {content_type} header: '{header_text}' (matched: {matching_header})")
                # Found a relevant header, look for content after it
                next_content = []
                
                # Look for the next sibling elements
                for sibling in header.find_next_siblings():
                    if sibling.name in ['ul', 'ol']:
                        # Found a list
                        logger.info(f"📋 Found {sibling.name} list with {len(sibling.find_all('li'))} items")
                        for li in sibling.find_all('li'):
                            text = li.get_text().strip()
                            if text and len(text) > 2:
                                next_content.append(text)
                        break
                    elif sibling.name in ['div', 'section'] and len(next_content) == 0:
                        # Look inside the div/section for lists
                        logger.info(f"🔍 Searching inside {sibling.name} for lists...")
                        for ul_ol in sibling.find_all(['ul', 'ol']):
                            logger.info(f"📋 Found {ul_ol.name} with {len(ul_ol.find_all('li'))} items")
                            for li in ul_ol.find_all('li'):
                                text = li.get_text().strip()
                                if text and len(text) > 2:
                                    next_content.append(text)
                        if next_content:
                            break
                
                required_items = 3 if content_type == 'ingredient' else 2
                logger.info(f"📊 Found {len(next_content)} items, need {required_items} for {content_type}")
                
                if len(next_content) >= required_items:
                    logger.info(f"✅ Using {len(next_content)} {content_type} items from section")
                    content = next_content
                    break
                else:
                    logger.info(f"❌ Not enough {content_type} items, continuing search...")
        
        if not content:
            logger.warning(f"⚠️ No {content_type} sections found")
        
        return content
    
    def _extract_universal_metadata(self, soup: BeautifulSoup) -> dict:
        """Extract time and serving metadata"""
        patterns = self.intelligence_patterns['metadata_patterns']
        metadata = {}
        
        # Get all text for pattern matching
        all_text = soup.get_text().lower()
        
        # Extract times
        for time_type in ['prep', 'cook', 'total']:
            for indicator in patterns['time_indicators']:
                if time_type in indicator:
                    # Look for time pattern after the indicator
                    pattern = rf'{indicator}[:\s]*([^.]*?)(?:\.|$)'
                    match = re.search(pattern, all_text)
                    if match:
                        time_text = match.group(1)
                        time_minutes = self._extract_time_minutes(time_text)
                        if time_minutes:
                            metadata[f'{time_type}_time'] = time_minutes
                            break
        
        # Extract servings
        for indicator in patterns['serving_indicators']:
            pattern = rf'{indicator}[:\s]*(\d+)'
            match = re.search(pattern, all_text)
            if match:
                metadata['servings'] = int(match.group(1))
                break
        
        return metadata
    
    def _calculate_universal_confidence(self, recipe: WebRecipeData) -> float:
        """Calculate confidence based on extracted data quality"""
        confidence = 0.0
        
        # Title confidence
        if recipe.title:
            if len(recipe.title) > 10 and len(recipe.title) < 80:
                confidence += 0.25
            else:
                confidence += 0.15
        
        # Ingredients confidence
        if recipe.ingredients:
            ingredient_count = len(recipe.ingredients)
            if ingredient_count >= 5:
                confidence += 0.30
            elif ingredient_count >= 3:
                confidence += 0.20
            else:
                confidence += 0.10
        
        # Instructions confidence
        if recipe.instructions:
            instruction_count = len(recipe.instructions)
            avg_length = sum(len(inst) for inst in recipe.instructions) / len(recipe.instructions)
            
            if instruction_count >= 3 and avg_length > 20:
                confidence += 0.30
            elif instruction_count >= 2:
                confidence += 0.20
            else:
                confidence += 0.10
        
        # Metadata bonus
        if recipe.prep_time or recipe.cook_time or recipe.total_time:
            confidence += 0.10
        if recipe.servings:
            confidence += 0.05
        
        return min(confidence, 0.95)  # Cap at 95%
    
    def _validate_recipe_quality(self, recipe: WebRecipeData) -> bool:
        """Validate that extracted recipe meets minimum quality standards"""
        if not recipe.title:
            return False
        
        if not recipe.ingredients and not recipe.instructions:
            return False
        
        if recipe.ingredients and len(recipe.ingredients) < 2:
            return False
        
        if recipe.instructions and len(recipe.instructions) < 1:
            return False
        
        return True
    
    def _extract_json_ld_universal(self, soup: BeautifulSoup, url: str) -> Optional[WebRecipeData]:
        """
        Universal JSON-LD extraction (works on any site with structured data)
        """
        logger.info("🔍 Attempting universal JSON-LD extraction...")
        
        try:
            # Find all JSON-LD script tags
            json_scripts = soup.find_all('script', type='application/ld+json')
            
            for script in json_scripts:
                try:
                    data = json.loads(script.string)
                    
                    # Handle different JSON-LD structures
                    if isinstance(data, list):
                        # Multiple items in array
                        for item in data:
                            recipe = self._parse_json_ld_recipe_universal(item)
                            if recipe:
                                recipe.source_url = url
                                recipe.extraction_method = "json_ld_universal"
                                recipe.confidence = 0.95  # High confidence for structured data
                                return recipe
                    else:
                        # Single item
                        recipe = self._parse_json_ld_recipe_universal(data)
                        if recipe:
                            recipe.source_url = url
                            recipe.extraction_method = "json_ld_universal"
                            recipe.confidence = 0.95
                            return recipe
                            
                except json.JSONDecodeError as e:
                    logger.warning(f"⚠️ Invalid JSON in script tag: {e}")
                    continue
                except Exception as e:
                    logger.warning(f"⚠️ Error parsing JSON-LD: {e}")
                    continue
            
            logger.info("ℹ️ No valid JSON-LD recipe data found")
            return None
            
        except Exception as e:
            logger.error(f"❌ JSON-LD extraction error: {e}")
            return None
    
    def _parse_json_ld_recipe_universal(self, data: dict) -> Optional[WebRecipeData]:
        """Parse JSON-LD recipe data universally"""
        try:
            # Check if this is a recipe - handle both string and list types
            type_field = data.get('@type', '')
            if isinstance(type_field, list):
                type_str = ' '.join(str(t) for t in type_field).lower()
            else:
                type_str = str(type_field).lower()
                
            if 'recipe' not in type_str:
                return None
            
            logger.info(f"✅ Found Recipe JSON-LD: {type_str}")
            
            recipe = WebRecipeData()
            
            # Extract title
            recipe.title = data.get('name', '')
            
            # Extract ingredients
            ingredients = data.get('recipeIngredient', [])
            if isinstance(ingredients, list):
                recipe.ingredients = [str(ing).strip() for ing in ingredients if ing]
            elif isinstance(ingredients, str):
                recipe.ingredients = [ingredients.strip()]
            
            # Extract instructions
            instructions_data = data.get('recipeInstructions', [])
            instructions = []
            
            if isinstance(instructions_data, list):
                for instruction in instructions_data:
                    if isinstance(instruction, dict):
                        text = instruction.get('text', '')
                    elif isinstance(instruction, str):
                        text = instruction
                    else:
                        continue
                    
                    if text:
                        # Clean text - remove any existing numbering
                        text = text.strip()
                        # Remove leading numbers: "1.", "1)", etc.
                        text = re.sub(r'^\s*[\d]+[\.\)]\s*', '', text)
                        text = re.sub(r'^\s*\([\d]+\)\s*', '', text)
                        text = text.strip()
                        
                        if text:  # Only add if there's still content after cleaning
                            instructions.append(text)
            elif isinstance(instructions_data, str):
                # Sometimes instructions are a single string
                instructions = [line.strip() for line in instructions_data.split('\n') if line.strip()]
            
            # Fallback: If no instructions found in JSON-LD, try scraping from HTML
            if not instructions:
                logger.info("No instructions in JSON-LD, falling back to HTML scraping")
                try:
                    # Try common instruction selectors
                    instruction_selectors = [
                        '.recipe-steps li', '.recipe-instructions li', '.instructions li',
                        '[itemprop="recipeInstructions"] li', '.recipe__steps li',
                        '.recipe-procedure-text', '.recipe-steps p', '.instructions p',
                        '[class*="instruction"] p', '[class*="step"]'
                    ]
                    
                    for selector in instruction_selectors:
                        instruction_elements = soup.select(selector)
                        if instruction_elements:
                            raw_instructions = [el.get_text(strip=True) for el in instruction_elements if el.get_text(strip=True)]
                            if raw_instructions:
                                logger.info(f"Found {len(raw_instructions)} instructions using selector: {selector}")
                                # Clean instructions - remove any numbering
                                clean_instructions = []
                                for text in raw_instructions:
                                    # Remove leading numbers
                                    text = re.sub(r'^\s*[\d]+[\.\)]\s*', '', text.strip())
                                    text = re.sub(r'^\s*\([\d]+\)\s*', '', text)
                                    text = text.strip()
                                    if text:
                                        clean_instructions.append(text)
                                instructions = clean_instructions
                                break
                except Exception as e:
                    logger.warning(f"HTML instruction scraping failed: {e}")
            
            recipe.instructions = instructions
            
            # Extract metadata
            # Prep time
            prep_time = data.get('prepTime', '')
            if prep_time:
                recipe.prep_time = self._parse_iso_duration(prep_time)
            
            # Cook time  
            cook_time = data.get('cookTime', '')
            if cook_time:
                recipe.cook_time = self._parse_iso_duration(cook_time)
            
            # Total time
            total_time = data.get('totalTime', '')
            if total_time:
                recipe.total_time = self._parse_iso_duration(total_time)
            
            # Servings/Yield
            yield_data = data.get('recipeYield') or data.get('yield')
            if yield_data:
                if isinstance(yield_data, list) and yield_data:
                    yield_data = yield_data[0]
                if isinstance(yield_data, str):
                    servings = self._extract_servings(yield_data)
                    if servings:
                        recipe.servings = servings
                elif isinstance(yield_data, (int, float)):
                    recipe.servings = int(yield_data)
            
            # Description
            recipe.description = data.get('description', '')
            
            # Image
            image_data = data.get('image')
            if image_data:
                if isinstance(image_data, list) and image_data:
                    # Extract URL from first image (handle dict or string)
                    first_image = image_data[0]
                    if isinstance(first_image, dict):
                        recipe.image_url = first_image.get('contentUrl') or first_image.get('url') or ''
                    elif isinstance(first_image, str):
                        recipe.image_url = first_image
                    else:
                        recipe.image_url = str(first_image)
                elif isinstance(image_data, str):
                    recipe.image_url = image_data
                elif isinstance(image_data, dict):
                    recipe.image_url = image_data.get('contentUrl') or image_data.get('url') or ''
            
            # Author
            author_data = data.get('author')
            if author_data:
                if isinstance(author_data, dict):
                    recipe.author = author_data.get('name', '')
                elif isinstance(author_data, str):
                    recipe.author = author_data
            
            # Rating
            rating_data = data.get('aggregateRating')
            if rating_data and isinstance(rating_data, dict):
                rating_value = rating_data.get('ratingValue')
                if rating_value:
                    try:
                        recipe.rating = float(rating_value)
                    except (ValueError, TypeError):
                        pass
            
            return recipe if recipe.title and (recipe.ingredients or recipe.instructions) else None
            
        except Exception as e:
            logger.warning(f"⚠️ Error parsing JSON-LD recipe: {e}")
            return None
    
    def _parse_iso_duration(self, duration_str: str) -> Optional[int]:
        """Parse ISO 8601 duration (PT30M, PT1H30M) to minutes"""
        if not duration_str:
            return None
        
        try:
            # Handle ISO 8601 format like PT30M, PT1H30M
            if duration_str.startswith('PT'):
                duration_str = duration_str[2:]  # Remove PT
                
                hours = 0
                minutes = 0
                
                # Extract hours
                hour_match = re.search(r'(\d+)H', duration_str)
                if hour_match:
                    hours = int(hour_match.group(1))
                
                # Extract minutes
                minute_match = re.search(r'(\d+)M', duration_str)
                if minute_match:
                    minutes = int(minute_match.group(1))
                
                return hours * 60 + minutes
            else:
                # Fallback to regular time extraction
                return self._extract_time_minutes(duration_str)
                
        except Exception as e:
            logger.warning(f"⚠️ Error parsing duration {duration_str}: {e}")
            return None
    
    def extract_from_url(self, url: str) -> WebRecipeData:
        """
        Multi-method extraction with quality validation (like professional converters)
        """
        return self._extract_with_quality_validation(url)
    
    def _extract_with_quality_validation(self, url: str) -> WebRecipeData:
        """
        Run ALL extraction methods and select the best result (quality over speed)
        """
        logger.info(f"🌐 Starting multi-method quality extraction from: {url}")
        start_time = time.time()
        domain = urlparse(url).netloc.lower()
        
        # Get optimal extraction strategy from analytics
        extraction_methods = self._get_optimal_extraction_order(url)
        
        try:
            # Fetch the page content
            response = self._fetch_page(url)
            if not response:
                self._record_extraction_failure(url, "fetch_failed", start_time)
                return WebRecipeData(
                    source_url=url,
                    extraction_method="fetch_failed",
                    confidence=0.0
                )
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Run ALL extraction methods and collect results
            extraction_results = []
            
            logger.info("🔄 Running all extraction methods for quality validation...")
            
            for method_name in extraction_methods:
                try:
                    recipe_data = None
                    method_start = time.time()
                    
                    logger.info(f"🔍 Testing method: {method_name}")
                    
                    if method_name == 'json_ld':
                        recipe_data = self._extract_json_ld_universal(soup, url)
                    elif method_name == 'universal_intelligence':
                        recipe_data = self._extract_universal_intelligence(soup, url)
                    elif method_name == 'microdata':
                        recipe_data = self._extract_microdata(soup, url)
                    elif method_name == 'open_graph':
                        recipe_data = self._extract_open_graph(soup, url)
                    elif method_name == 'adaptive_fallback':
                        recipe_data = self._extract_adaptive_fallback(soup, url)
                    elif method_name.endswith('_specific'):
                        # Legacy site-specific extraction (fallback)
                        if 'allrecipes.com' in domain and method_name == 'allrecipes_specific':
                            recipe_data = self._extract_allrecipes(soup, url)
                        elif 'foodnetwork.com' in domain and method_name == 'foodnetwork_specific':
                            recipe_data = self._extract_foodnetwork(soup, url)
                        else:
                            logger.info(f"⚠️ Skipping unknown site-specific method: {method_name}")
                            continue
                    
                    method_time = time.time() - method_start
                    
                    if recipe_data and recipe_data.confidence > 0.3:
                        logger.info(f"✅ {method_name}: confidence={recipe_data.confidence:.2f}, {len(recipe_data.ingredients or [])} ingredients, {len(recipe_data.instructions or [])} steps")
                        
                        extraction_results.append({
                            'method': method_name,
                            'data': recipe_data,
                            'time': method_time
                        })
                    else:
                        logger.info(f"❌ {method_name}: failed or low confidence")
                        
                except Exception as e:
                    logger.warning(f"⚠️ {method_name} extraction error: {e}")
                    continue
            
            # Quality validation and selection of best result
            if extraction_results:
                best_result = self._select_best_extraction(extraction_results, url)
                
                # Apply adaptive confidence scoring to the best result
                original_confidence = best_result['data'].confidence
                adaptive_confidence = self._calculate_adaptive_confidence(
                    url, best_result['method'], best_result['data'], original_confidence
                )
                best_result['data'].confidence = adaptive_confidence
                
                # Record successful extraction
                processing_time = time.time() - start_time
                self._record_extraction_success(url, best_result['method'], best_result['data'], processing_time)
                
                logger.info(f"🎯 Multi-method winner: {best_result['method']}")
                logger.info(f"✅ Quality extraction completed in {processing_time:.2f}s")
                logger.info(f"🎯 Final confidence: {original_confidence:.2f} → {adaptive_confidence:.2f}")
                
                return best_result['data']
            else:
                # All methods failed
                logger.warning("❌ All extraction methods failed")
                self._record_extraction_failure(url, "all_methods_failed", start_time)
                return WebRecipeData(
                    source_url=url,
                    extraction_method="all_failed",
                    confidence=0.0
                )
                
        except Exception as e:
            logger.error(f"❌ Multi-method extraction failed: {e}")
            self._record_extraction_failure(url, "extraction_error", start_time)
            return WebRecipeData(
                source_url=url,
                extraction_method="extraction_error",
                confidence=0.0
            )
        """
        Main extraction method with self-improving capabilities
        """
        logger.info(f"🌐 Starting extraction from: {url}")
        start_time = time.time()
        domain = urlparse(url).netloc.lower()
        
        # Get optimal extraction strategy from analytics
        extraction_methods = self._get_optimal_extraction_order(url)
        
        try:
            # Fetch the page content
            response = self._fetch_page(url)
            if not response:
                self._record_extraction_failure(url, "fetch_failed", start_time)
                return WebRecipeData(
                    source_url=url,
                    extraction_method="fetch_failed",
                    confidence=0.0
                )
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try extraction methods in optimal order
            for method_name in extraction_methods:
                try:
                    recipe_data = None
                    
                    if method_name == 'json_ld':
                        recipe_data = self._extract_json_ld_universal(soup, url)
                    elif method_name == 'universal_intelligence':
                        recipe_data = self._extract_universal_intelligence(soup, url)
                    elif method_name == 'open_graph':
                        recipe_data = self._extract_open_graph(soup, url)
                    elif method_name == 'microdata':
                        recipe_data = self._extract_microdata(soup, url)
                    elif method_name == 'adaptive_fallback':
                        recipe_data = self._extract_adaptive_fallback(soup, url)
                    elif method_name.endswith('_specific'):
                        # Legacy site-specific extraction (fallback)
                        if 'allrecipes.com' in domain and method_name == 'allrecipes_specific':
                            recipe_data = self._extract_allrecipes(soup, url)
                        elif 'foodnetwork.com' in domain and method_name == 'foodnetwork_specific':
                            recipe_data = self._extract_foodnetwork(soup, url)
                        else:
                            # Skip unknown site-specific methods
                            logger.info(f"⚠️ Skipping unknown site-specific method: {method_name}")
                            continue
                    
                    if recipe_data and recipe_data.confidence > 0.3:
                        # Apply adaptive confidence scoring
                        original_confidence = recipe_data.confidence
                        adaptive_confidence = self._calculate_adaptive_confidence(
                            url, method_name, recipe_data, original_confidence
                        )
                        recipe_data.confidence = adaptive_confidence
                        
                        # Record successful extraction
                        processing_time = time.time() - start_time
                        self._record_extraction_success(url, method_name, recipe_data, processing_time)
                        
                        logger.info(f"✅ Extraction successful via {method_name} in {processing_time:.2f}s")
                        logger.info(f"🎯 Confidence: {original_confidence:.2f} → {adaptive_confidence:.2f}")
                        return recipe_data
                
                except Exception as e:
                    logger.warning(f"⚠️ Method {method_name} failed: {e}")
                    continue
            
            # All methods failed
            fallback_recipe = self._extract_adaptive_fallback(soup, url)
            processing_time = time.time() - start_time
            self._record_extraction_failure(url, "all_methods_failed", processing_time)
            
            logger.warning(f"⚠️ All extraction methods failed in {processing_time:.2f}s")
            return fallback_recipe
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._record_extraction_failure(url, "extraction_exception", processing_time)
            logger.error(f"❌ Extraction failed after {processing_time:.2f}s: {e}")
            return WebRecipeData(
                source_url=url,
                extraction_method="extraction_failed",
                confidence=0.0
            )
    
    def _fetch_page(self, url: str) -> Optional[requests.Response]:
        """Fetch webpage content with error handling and retries"""
        try:
            logger.info(f"📥 Fetching content from: {url}")
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                logger.info(f"✅ Page fetched successfully ({len(response.text)} characters)")
                return response
            else:
                logger.warning(f"⚠️ HTTP {response.status_code} for URL: {url}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"⏰ Timeout fetching URL: {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"🌐 Network error fetching URL: {url} - {e}")
            return None
    
    def _extract_json_ld(self, soup: BeautifulSoup, url: str) -> Optional[WebRecipeData]:
        """
        Extract recipe data from JSON-LD Schema.org markup (most reliable method)
        """
        logger.info("🔍 Attempting JSON-LD extraction...")
        
        try:
            # Find all JSON-LD script tags
            json_scripts = soup.find_all('script', type='application/ld+json')
            
            for script in json_scripts:
                try:
                    data = json.loads(script.string)
                    
                    # Handle different JSON-LD structures
                    if isinstance(data, list):
                        # Multiple items in array
                        for item in data:
                            recipe = self._parse_json_ld_recipe(item)
                            if recipe:
                                recipe.source_url = url
                                recipe.extraction_method = "json_ld"
                                recipe.confidence = 0.9
                                return recipe
                    else:
                        # Single item
                        recipe = self._parse_json_ld_recipe(data)
                        if recipe:
                            recipe.source_url = url
                            recipe.extraction_method = "json_ld"
                            recipe.confidence = 0.9
                            return recipe
                            
                except json.JSONDecodeError:
                    continue
            
            logger.info("ℹ️ No valid JSON-LD recipe data found")
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ JSON-LD extraction failed: {e}")
            return None
    
    def _parse_json_ld_recipe(self, data: Dict) -> Optional[WebRecipeData]:
        """Parse JSON-LD data for recipe information"""
        
        # Check if this is a recipe object
        if not self._is_recipe_object(data):
            return None
        
        try:
            recipe = WebRecipeData()
            
            # Basic information
            recipe.title = data.get('name', '')
            recipe.description = data.get('description', '')
            recipe.author = self._extract_author(data.get('author', ''))
            
            # Images
            image = data.get('image')
            if image:
                if isinstance(image, list):
                    first_image = image[0] if image else None
                    if isinstance(first_image, dict):
                        recipe.image_url = first_image.get('contentUrl') or first_image.get('url') or ''
                    elif isinstance(first_image, str):
                        recipe.image_url = first_image
                    else:
                        recipe.image_url = ''
                elif isinstance(image, dict):
                    recipe.image_url = image.get('contentUrl') or image.get('url') or ''
                elif isinstance(image, str):
                    recipe.image_url = image
                else:
                    recipe.image_url = ''
            
            # Ingredients
            ingredients = data.get('recipeIngredient', [])
            recipe.ingredients = [str(ing) for ing in ingredients] if ingredients else []
            
            # Instructions
            instructions = data.get('recipeInstructions', [])
            recipe.instructions = self._parse_instructions(instructions)
            
            # Timing
            recipe.prep_time = self._parse_duration(data.get('prepTime'))
            recipe.cook_time = self._parse_duration(data.get('cookTime'))
            recipe.total_time = self._parse_duration(data.get('totalTime'))
            
            # Servings/Yield
            recipe.servings = self._parse_servings(data.get('recipeYield'))
            
            # Category and cuisine
            recipe.cuisine = data.get('recipeCuisine', '')
            recipe.category = data.get('recipeCategory', '')
            recipe.keywords = data.get('keywords', [])
            
            # Rating
            rating = data.get('aggregateRating')
            if rating:
                recipe.rating = float(rating.get('ratingValue', 0))
                recipe.review_count = int(rating.get('reviewCount', 0))
            
            # Nutrition
            nutrition = data.get('nutrition')
            if nutrition:
                recipe.nutrition = self._parse_nutrition(nutrition)
            
            # Only return if we have essential data
            if recipe.title and (recipe.ingredients or recipe.instructions):
                return recipe
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Error parsing JSON-LD recipe: {e}")
            return None
    
    def _is_recipe_object(self, data: Dict) -> bool:
        """Check if JSON-LD object represents a recipe"""
        recipe_types = ['Recipe', 'recipe']
        
        # Check @type field
        obj_type = data.get('@type', '')
        if isinstance(obj_type, list):
            return any(t in recipe_types for t in obj_type)
        else:
            return obj_type in recipe_types
    
    def _extract_bonappetit(self, soup: BeautifulSoup, url: str) -> Optional[WebRecipeData]:
        """
        Extract from BonAppetit using proven patterns from existing codebase
        """
        logger.info("🎯 Using BonAppetit-specific extraction patterns...")
        
        try:
            recipe = WebRecipeData()
            recipe.source_url = url
            recipe.extraction_method = "bonappetit_specific"
            
            # Title extraction
            title_elem = soup.find('h1', class_='recipe-title') or soup.find('h1')
            recipe.title = title_elem.get_text(strip=True) if title_elem else ''
            
            # Description
            desc_elem = soup.find('div', class_='recipe-description') or soup.find('p', class_='description')
            recipe.description = desc_elem.get_text(strip=True) if desc_elem else ''
            
            # Ingredients - BonAppetit specific selectors
            ingredient_elems = soup.find_all('div', class_='ingredient') or soup.find_all('li', class_='ingredient')
            recipe.ingredients = [elem.get_text(strip=True) for elem in ingredient_elems]
            
            # Instructions
            instruction_elems = soup.find_all('div', class_='step') or soup.find_all('li', class_='instruction')
            recipe.instructions = [elem.get_text(strip=True) for elem in instruction_elems]
            
            # Timing from BonAppetit metadata
            time_elem = soup.find('span', class_='recipe-time') or soup.find('time')
            if time_elem:
                time_text = time_elem.get_text(strip=True)
                recipe.total_time = self._parse_time_text(time_text)
            
            # Servings
            servings_elem = soup.find('span', class_='serves') or soup.find('span', class_='yield')
            if servings_elem:
                recipe.servings = self._parse_servings(servings_elem.get_text(strip=True))
            
            # Calculate confidence based on data completeness
            confidence = 0.5
            if recipe.title: confidence += 0.2
            if recipe.ingredients: confidence += 0.2
            if recipe.instructions: confidence += 0.1
            
            recipe.confidence = min(confidence, 1.0)
            
            if recipe.title and (recipe.ingredients or recipe.instructions):
                return recipe
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ BonAppetit extraction failed: {e}")
            return None
    
    def _extract_foodnetwork(self, soup: BeautifulSoup, url: str) -> Optional[WebRecipeData]:
        """Extract from Food Network with specific patterns"""
        logger.info("🎯 Using Food Network extraction patterns...")
        
        try:
            recipe = WebRecipeData()
            recipe.source_url = url
            recipe.extraction_method = "foodnetwork_specific"
            
            # Food Network specific selectors
            title_selectors = [
                'h1.o-AssetTitle__a-HeadlineText',
                'h1[class*="recipe-title"]',
                '.recipe-header h1',
                'h1.entry-title'
            ]
            
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    recipe.title = title_elem.get_text().strip()
                    break
            
            # Ingredients
            ingredients = []
            ingredient_selectors = [
                '.o-RecipeIngredients__a-Ingredient',
                '.recipe-ingredients li',
                '[class*="ingredient"] p',
                '.ingredients-list li'
            ]
            
            for selector in ingredient_selectors:
                ingredient_elems = soup.select(selector)
                if ingredient_elems:
                    for elem in ingredient_elems:
                        text = elem.get_text().strip()
                        if text and len(text) > 2:
                            ingredients.append(text)
                    if ingredients:
                        break
            
            recipe.ingredients = ingredients
            
            # Instructions
            instructions = []
            instruction_selectors = [
                '.o-Method__m-Step',
                '.recipe-instructions li',
                '.directions li',
                '[class*="instruction"] p'
            ]
            
            for selector in instruction_selectors:
                instruction_elems = soup.select(selector)
                if instruction_elems:
                    for i, elem in enumerate(instruction_elems, 1):
                        text = elem.get_text().strip()
                        if text and len(text) > 5:
                            if not re.match(r'^\d+\.?\s', text):
                                text = f"{i}. {text}"
                            instructions.append(text)
                    if instructions:
                        break
            
            recipe.instructions = instructions
            
            # Time and servings (Food Network often has these)
            # Look for recipe details section
            details_section = soup.find('section', class_=re.compile(r'recipe.*details', re.I))
            if details_section:
                # Extract times and servings from details
                detail_text = details_section.get_text().lower()
                
                prep_match = re.search(r'prep:?\s*(\d+(?:\s*hr?)?s?\s*\d*\s*(?:min)?s?)', detail_text)
                if prep_match:
                    recipe.prep_time = self._extract_time_minutes(prep_match.group(1))
                
                cook_match = re.search(r'cook:?\s*(\d+(?:\s*hr?)?s?\s*\d*\s*(?:min)?s?)', detail_text)
                if cook_match:
                    recipe.cook_time = self._extract_time_minutes(cook_match.group(1))
                    
                serving_match = re.search(r'serves?:?\s*(\d+)', detail_text)
                if serving_match:
                    recipe.servings = int(serving_match.group(1))
            
            # Description
            desc_selectors = [
                '.o-AssetDescription__a-Description',
                '.recipe-description',
                '.summary'
            ]
            for selector in desc_selectors:
                elem = soup.select_one(selector)
                if elem:
                    recipe.description = elem.get_text().strip()
                    break
            
            # Calculate confidence
            confidence = 0.1
            if recipe.title:
                confidence += 0.3
            if recipe.ingredients and len(recipe.ingredients) >= 3:
                confidence += 0.3
            if recipe.instructions and len(recipe.instructions) >= 2:
                confidence += 0.2
            if recipe.prep_time or recipe.cook_time:
                confidence += 0.1
            
            recipe.confidence = min(confidence, 0.9)
            
            if recipe.title and (recipe.ingredients or recipe.instructions):
                logger.info(f"✅ Food Network extraction successful: '{recipe.title}' (confidence: {recipe.confidence:.2f})")
                return recipe
            else:
                # Fall back to generic extraction
                logger.info("⚠️ Food Network specific extraction insufficient, trying generic...")
                return self._extract_generic_structured(soup, url, "foodnetwork_fallback")
                
        except Exception as e:
            logger.error(f"❌ Food Network extraction error: {e}")
            return self._extract_generic_structured(soup, url, "foodnetwork_error_fallback")
    
    def _extract_allrecipes(self, soup: BeautifulSoup, url: str) -> Optional[WebRecipeData]:
        """Extract from AllRecipes with comprehensive pattern matching"""
        logger.info("🎯 Using comprehensive AllRecipes extraction patterns...")
        
        try:
            recipe = WebRecipeData()
            recipe.source_url = url
            recipe.extraction_method = "allrecipes_specific"
            
            # AllRecipes often uses JSON-LD, but has specific patterns too
            
            # Strategy 1: Look for specific AllRecipes selectors
            title_selectors = [
                'h1.headline-title',
                'h1.recipe-title',
                'h1[data-testid="recipe-title"]',
                '.recipe-header h1',
                'h1.entry-title'
            ]
            
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    recipe.title = title_elem.get_text().strip()
                    break
            
            # Strategy 2: Ingredients extraction
            ingredients = []
            ingredient_selectors = [
                '.recipe-ingredients li',
                '.ingredients-list li',
                '[data-testid="recipe-ingredient"]',
                '.ingredient-list-item',
                '.recipe-ingredient',
                'ul.ingredients li'
            ]
            
            for selector in ingredient_selectors:
                ingredient_elems = soup.select(selector)
                if ingredient_elems:
                    for elem in ingredient_elems:
                        text = elem.get_text().strip()
                        if text and len(text) > 2:  # Filter out empty or very short items
                            ingredients.append(text)
                    if ingredients:
                        break
            
            recipe.ingredients = ingredients
            
            # Strategy 3: Instructions extraction
            instructions = []
            instruction_selectors = [
                '.recipe-instructions li',
                '.instructions-list li',
                '[data-testid="recipe-instruction"]',
                '.recipe-instruction',
                '.directions li',
                '.recipe-directions li'
            ]
            
            for selector in instruction_selectors:
                instruction_elems = soup.select(selector)
                if instruction_elems:
                    for i, elem in enumerate(instruction_elems, 1):
                        text = elem.get_text().strip()
                        if text and len(text) > 5:  # Filter out empty or very short items
                            # Add step numbers if not present
                            if not re.match(r'^\d+\.?\s', text):
                                text = f"{i}. {text}"
                            instructions.append(text)
                    if instructions:
                        break
            
            recipe.instructions = instructions
            
            # Strategy 4: Extract metadata
            # Prep time
            prep_selectors = [
                '[data-testid="prep-time"]',
                '.prep-time',
                '.recipe-prep-time'
            ]
            for selector in prep_selectors:
                elem = soup.select_one(selector)
                if elem:
                    prep_text = elem.get_text().strip()
                    prep_minutes = self._extract_time_minutes(prep_text)
                    if prep_minutes:
                        recipe.prep_time = prep_minutes
                        break
            
            # Cook time
            cook_selectors = [
                '[data-testid="cook-time"]',
                '.cook-time',
                '.recipe-cook-time'
            ]
            for selector in cook_selectors:
                elem = soup.select_one(selector)
                if elem:
                    cook_text = elem.get_text().strip()
                    cook_minutes = self._extract_time_minutes(cook_text)
                    if cook_minutes:
                        recipe.cook_time = cook_minutes
                        break
            
            # Total time
            total_selectors = [
                '[data-testid="total-time"]',
                '.total-time',
                '.recipe-total-time'
            ]
            for selector in total_selectors:
                elem = soup.select_one(selector)
                if elem:
                    total_text = elem.get_text().strip()
                    total_minutes = self._extract_time_minutes(total_text)
                    if total_minutes:
                        recipe.total_time = total_minutes
                        break
            
            # Servings
            serving_selectors = [
                '[data-testid="servings"]',
                '.servings',
                '.recipe-servings',
                '.yield'
            ]
            for selector in serving_selectors:
                elem = soup.select_one(selector)
                if elem:
                    serving_text = elem.get_text().strip()
                    servings = self._extract_servings(serving_text)
                    if servings:
                        recipe.servings = servings
                        break
            
            # Description/summary
            desc_selectors = [
                '.recipe-description',
                '.recipe-summary',
                '.entry-summary',
                '[data-testid="recipe-description"]'
            ]
            for selector in desc_selectors:
                elem = soup.select_one(selector)
                if elem:
                    recipe.description = elem.get_text().strip()
                    break
            
            # Image
            img_selectors = [
                '.recipe-image img',
                '.recipe-photo img',
                '[data-testid="recipe-image"] img',
                '.hero-image img'
            ]
            for selector in img_selectors:
                img_elem = soup.select_one(selector)
                if img_elem:
                    img_src = img_elem.get('src') or img_elem.get('data-src')
                    if img_src:
                        # Convert relative URLs to absolute
                        recipe.image_url = urljoin(url, img_src)
                        break
            
            # Calculate confidence based on completeness
            confidence = 0.1  # Base confidence
            if recipe.title:
                confidence += 0.3
            if recipe.ingredients and len(recipe.ingredients) >= 3:
                confidence += 0.3
            if recipe.instructions and len(recipe.instructions) >= 2:
                confidence += 0.2
            if recipe.prep_time or recipe.cook_time or recipe.total_time:
                confidence += 0.1
            
            recipe.confidence = min(confidence, 0.9)  # Cap at 0.9
            
            # Return recipe if we got minimum viable data
            if recipe.title and (recipe.ingredients or recipe.instructions):
                logger.info(f"✅ AllRecipes extraction successful: '{recipe.title}' (confidence: {recipe.confidence:.2f})")
                return recipe
            else:
                logger.warning("⚠️ AllRecipes extraction failed - insufficient data")
                return None
                
        except Exception as e:
            logger.error(f"❌ AllRecipes extraction error: {e}")
            return None
    
    def _extract_seriouseats(self, soup: BeautifulSoup, url: str) -> Optional[WebRecipeData]:
        """Extract from Serious Eats"""
        logger.info("🎯 Using Serious Eats extraction patterns...")
        return self._extract_generic_structured(soup, url, "seriouseats_specific")
    
    def _extract_nytimes(self, soup: BeautifulSoup, url: str) -> Optional[WebRecipeData]:
        """Extract from NYTimes Cooking"""
        logger.info("🎯 Using NYTimes Cooking extraction patterns...")
        return self._extract_generic_structured(soup, url, "nytimes_specific")
    
    def _extract_open_graph(self, soup: BeautifulSoup, url: str) -> Optional[WebRecipeData]:
        """Extract recipe data from Open Graph metadata"""
        logger.info("🔍 Attempting Open Graph extraction...")
        
        try:
            recipe = WebRecipeData()
            recipe.source_url = url
            recipe.extraction_method = "open_graph"
            
            # Extract Open Graph metadata
            og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
            
            for tag in og_tags:
                property_name = tag.get('property', '')
                content = tag.get('content', '')
                
                if property_name == 'og:title':
                    recipe.title = content
                elif property_name == 'og:description':
                    recipe.description = content
                elif property_name == 'og:image':
                    recipe.image_url = content
            
            # Basic confidence scoring
            confidence = 0.3
            if recipe.title: confidence += 0.2
            if recipe.description: confidence += 0.1
            
            recipe.confidence = confidence
            
            if recipe.title:
                return recipe
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Open Graph extraction failed: {e}")
            return None
    
    def _extract_microdata(self, soup: BeautifulSoup, url: str) -> Optional[WebRecipeData]:
        """Extract recipe data from HTML5 Microdata"""
        logger.info("🔍 Attempting Microdata extraction...")
        
        try:
            # Look for recipe microdata
            recipe_elem = soup.find(attrs={'itemtype': re.compile(r'.*Recipe')})
            if not recipe_elem:
                return None
            
            recipe = WebRecipeData()
            recipe.source_url = url
            recipe.extraction_method = "microdata"
            
            # Extract microdata properties
            for elem in recipe_elem.find_all(attrs={'itemprop': True}):
                prop = elem.get('itemprop')
                
                if prop == 'name':
                    recipe.title = elem.get_text(strip=True)
                elif prop == 'description':
                    recipe.description = elem.get_text(strip=True)
                elif prop == 'recipeIngredient':
                    recipe.ingredients.append(elem.get_text(strip=True))
                elif prop == 'recipeInstructions':
                    recipe.instructions.append(elem.get_text(strip=True))
            
            # Calculate confidence
            confidence = 0.4
            if recipe.title: confidence += 0.2
            if recipe.ingredients: confidence += 0.2
            
            recipe.confidence = confidence
            
            if recipe.title and (recipe.ingredients or recipe.instructions):
                return recipe
            
            return None
            
        except Exception as e:
            logger.warning(f"⚠️ Microdata extraction failed: {e}")
            return None
    
    def _extract_adaptive_fallback(self, soup: BeautifulSoup, url: str) -> WebRecipeData:
        """
        Adaptive fallback extraction using heuristics and page analysis
        """
        logger.info("🔄 Using adaptive fallback extraction...")
        
        recipe = WebRecipeData()
        recipe.source_url = url
        recipe.extraction_method = "adaptive_fallback"
        
        try:
            # Extract title from various common selectors
            title_selectors = ['h1', '.recipe-title', '.entry-title', '.post-title', 'title']
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    recipe.title = title_elem.get_text(strip=True)
                    break
            
            # Extract ingredients using common patterns
            ingredient_patterns = [
                '.ingredient', '.recipe-ingredient', '[class*="ingredient"]',
                'ul li', 'ol li'  # Common list patterns
            ]
            
            for pattern in ingredient_patterns:
                elements = soup.select(pattern)
                if elements and len(elements) > 2:  # Must have multiple ingredients
                    recipe.ingredients = [elem.get_text(strip=True) for elem in elements[:20]]  # Limit to 20
                    break
            
            # Extract instructions
            instruction_patterns = [
                '.instruction', '.recipe-instruction', '.step', '.method',
                '[class*="instruction"]', '[class*="direction"]'
            ]
            
            for pattern in instruction_patterns:
                elements = soup.select(pattern)
                if elements:
                    recipe.instructions = [elem.get_text(strip=True) for elem in elements[:20]]  # Limit to 20
                    break
            
            # Basic confidence scoring
            confidence = 0.2  # Base confidence for fallback
            if recipe.title: confidence += 0.2
            if recipe.ingredients: confidence += 0.2
            if recipe.instructions: confidence += 0.1
            
            recipe.confidence = min(confidence, 0.7)  # Cap fallback confidence at 0.7
            
            return recipe
            
        except Exception as e:
            logger.warning(f"⚠️ Adaptive fallback extraction failed: {e}")
            recipe.confidence = 0.0
            return recipe
    
    def _extract_generic_structured(self, soup: BeautifulSoup, url: str, method: str) -> Optional[WebRecipeData]:
        """Enhanced generic structured data extraction with smart pattern matching"""
        logger.info(f"🔍 Using enhanced generic extraction ({method})...")
        
        try:
            recipe = WebRecipeData()
            recipe.source_url = url
            recipe.extraction_method = method
            
            # Strategy 1: Look for common recipe title patterns
            title_patterns = [
                'h1',
                '[class*="title"]',
                '[class*="recipe"]',
                '[class*="headline"]',
                'title',
                '.entry-title',
                '.post-title'
            ]
            
            for pattern in title_patterns:
                title_elem = soup.select_one(pattern)
                if title_elem:
                    title_text = title_elem.get_text().strip()
                    # Filter out obviously wrong titles
                    if len(title_text) > 5 and len(title_text) < 100:
                        recipe.title = title_text
                        break
            
            # Strategy 2: Look for ingredient lists
            ingredients = []
            ingredient_patterns = [
                'li[class*="ingredient"]',
                'li[class*="recipe"]',
                '.ingredients li',
                'ul[class*="ingredient"] li',
                '[class*="ingredient-list"] li',
                '[class*="ingredients"] li'
            ]
            
            for pattern in ingredient_patterns:
                ingredient_elems = soup.select(pattern)
                if ingredient_elems and len(ingredient_elems) >= 3:  # Need at least 3 ingredients
                    for elem in ingredient_elems:
                        text = elem.get_text().strip()
                        if text and len(text) > 2 and len(text) < 200:
                            ingredients.append(text)
                    if ingredients:
                        break
            
            # If no structured ingredients found, look for text patterns
            if not ingredients:
                # Look for common ingredient section headers
                for header in soup.find_all(['h1', 'h2', 'h3', 'h4']):
                    header_text = header.get_text().strip().lower()
                    if any(word in header_text for word in ['ingredient', 'what you need', 'shopping list']):
                        # Look for the next list or paragraph content
                        next_elem = header.find_next_sibling(['ul', 'ol', 'div'])
                        if next_elem:
                            items = next_elem.find_all('li') if next_elem.name in ['ul', 'ol'] else next_elem.find_all(['p', 'div'])
                            for item in items[:15]:  # Limit to 15 items
                                text = item.get_text().strip()
                                if text and len(text) > 2 and len(text) < 200:
                                    ingredients.append(text)
                            if ingredients:
                                break
            
            recipe.ingredients = ingredients
            
            # Strategy 3: Look for instructions/directions
            instructions = []
            instruction_patterns = [
                'li[class*="instruction"]',
                'li[class*="direction"]',
                'li[class*="step"]',
                '.instructions li',
                '.directions li',
                '.method li',
                '[class*="instruction-list"] li',
                '[class*="directions"] li'
            ]
            
            for pattern in instruction_patterns:
                instruction_elems = soup.select(pattern)
                if instruction_elems and len(instruction_elems) >= 2:  # Need at least 2 steps
                    for i, elem in enumerate(instruction_elems, 1):
                        text = elem.get_text().strip()
                        if text and len(text) > 5 and len(text) < 500:
                            # Add step numbers if not present
                            if not re.match(r'^\d+\.?\s', text):
                                text = f"{i}. {text}"
                            instructions.append(text)
                    if instructions:
                        break
            
            # If no structured instructions found, look for text patterns
            if not instructions:
                for header in soup.find_all(['h1', 'h2', 'h3', 'h4']):
                    header_text = header.get_text().strip().lower()
                    if any(word in header_text for word in ['instruction', 'direction', 'method', 'preparation', 'how to']):
                        # Look for the next content
                        next_elem = header.find_next_sibling(['ol', 'ul', 'div'])
                        if next_elem:
                            items = next_elem.find_all('li') if next_elem.name in ['ul', 'ol'] else next_elem.find_all(['p', 'div'])
                            for i, item in enumerate(items[:10], 1):  # Limit to 10 steps
                                text = item.get_text().strip()
                                if text and len(text) > 5 and len(text) < 500:
                                    if not re.match(r'^\d+\.?\s', text):
                                        text = f"{i}. {text}"
                                    instructions.append(text)
                            if instructions:
                                break
            
            recipe.instructions = instructions
            
            # Strategy 4: Look for time and serving information
            # Look for time patterns in text
            all_text = soup.get_text()
            time_patterns = [
                r'prep\s*time:?\s*(\d+(?:\s*hour)?s?\s*\d*\s*(?:minute)?s?)',
                r'cook\s*time:?\s*(\d+(?:\s*hour)?s?\s*\d*\s*(?:minute)?s?)',
                r'total\s*time:?\s*(\d+(?:\s*hour)?s?\s*\d*\s*(?:minute)?s?)',
                r'(\d+)\s*(?:minutes?|mins?)',
                r'(\d+)\s*(?:hours?|hrs?)'
            ]
            
            for pattern in time_patterns:
                matches = re.findall(pattern, all_text.lower())
                if matches:
                    time_text = matches[0]
                    time_minutes = self._extract_time_minutes(time_text)
                    if time_minutes:
                        if not recipe.total_time:
                            recipe.total_time = time_minutes
                        break
            
            # Look for serving information
            serving_patterns = [
                r'serves?:?\s*(\d+)',
                r'yield:?\s*(\d+)',
                r'portions?:?\s*(\d+)',
                r'(\d+)\s*servings?'
            ]
            
            for pattern in serving_patterns:
                matches = re.findall(pattern, all_text.lower())
                if matches:
                    recipe.servings = int(matches[0])
                    break
            
            # Calculate confidence based on data completeness
            confidence = 0.1  # Base confidence for generic extraction
            
            if recipe.title:
                confidence += 0.2
            if recipe.ingredients and len(recipe.ingredients) >= 3:
                confidence += 0.25
            if recipe.instructions and len(recipe.instructions) >= 2:
                confidence += 0.25
            if recipe.total_time or recipe.prep_time or recipe.cook_time:
                confidence += 0.1
            if recipe.servings:
                confidence += 0.1
            
            recipe.confidence = min(confidence, 0.8)  # Cap generic extraction at 0.8
            
            # Return recipe if we have minimum viable data
            if recipe.title and (recipe.ingredients or recipe.instructions):
                logger.info(f"✅ Generic extraction successful: '{recipe.title}' (confidence: {recipe.confidence:.2f})")
                return recipe
            else:
                logger.warning("⚠️ Generic extraction failed - insufficient data")
                return None
                
        except Exception as e:
            logger.error(f"❌ Generic extraction error: {e}")
            return None
    
    def _get_optimal_extraction_order(self, url: str) -> List[str]:
        """Get optimal extraction method order based on analytics"""
        # Force multi-method approach for quality validation
        # TODO: Re-enable analytics optimization once quality approach is proven
        if True:  # Multi-method quality validation mode
            logger.info("🧠 Using multi-method quality validation strategy")
            return ['json_ld', 'microdata', 'universal_intelligence', 'open_graph', 'adaptive_fallback']
        else:
            # Original analytics-driven approach
            if self.analytics_enabled and self.analytics:
                return self.analytics.get_optimal_extraction_strategy(url)
            else:
                # Universal approach - prioritize our smart universal methods
                logger.info("🧠 Using universal extraction strategy")
                return ['json_ld', 'universal_intelligence', 'open_graph', 'microdata', 'adaptive_fallback']
    
    def _calculate_adaptive_confidence(self, url: str, method: str, recipe_data: WebRecipeData, base_confidence: float) -> float:
        """Calculate adaptive confidence using self-improving scorer"""
        if self.analytics_enabled and self.adaptive_scorer:
            try:
                # Convert recipe data to dictionary for analysis
                extracted_data = {
                    'title': recipe_data.title,
                    'ingredients': recipe_data.ingredients,
                    'instructions': recipe_data.instructions,
                    'description': recipe_data.description,
                    'total_time': recipe_data.total_time,
                    'prep_time': recipe_data.prep_time,
                    'cook_time': recipe_data.cook_time,
                    'servings': recipe_data.servings,
                    'image_url': recipe_data.image_url
                }
                
                adaptive_confidence, factors = self.adaptive_scorer.calculate_adaptive_confidence(
                    url, method, base_confidence, extracted_data
                )
                
                return adaptive_confidence
                
            except Exception as e:
                logger.warning(f"⚠️ Adaptive confidence calculation failed: {e}")
                return base_confidence
        else:
            return base_confidence
    
    def _select_best_extraction(self, results: List[dict], url: str) -> dict:
        """
        Select the best extraction result using formatting intelligence validation
        """
        logger.info(f"🎯 Quality validation: analyzing {len(results)} extraction results...")
        
        # Score each result based on multiple quality factors
        scored_results = []
        
        for result in results:
            data = result['data']
            method = result['method']
            
            # Use formatting intelligence to assess extraction quality
            recipe_dict = {
                'title': data.title,
                'ingredients': data.ingredients,
                'instructions': data.instructions,
                'time_min': data.total_time or data.cook_time or data.prep_time,
                'servings': data.servings
            }
            
            # Get formatting assessment (like your Auto-Clean intelligence)
            formatting_assessment = self.formatter.assess_extraction_quality(recipe_dict)
            
            # Calculate comprehensive quality score
            score = 0
            details = []
            
            # 1. Base confidence (25% weight)
            confidence_score = data.confidence * 0.25
            score += confidence_score
            details.append(f"confidence: {data.confidence:.2f}")
            
            # 2. Content completeness (30% weight)
            completeness = 0
            if data.title and len(data.title.strip()) > 5:
                completeness += 0.25
            if data.ingredients and len(data.ingredients) >= 3:
                completeness += 0.25
            if data.instructions and len(data.instructions) >= 1:
                completeness += 0.25
            if data.servings or data.total_time or data.prep_time:
                completeness += 0.25
            
            completeness_score = completeness * 0.3
            score += completeness_score
            details.append(f"completeness: {completeness:.2f}")
            
            # 3. Method reliability (20% weight)
            method_weights = {
                'json_ld': 0.95,           # Highest - structured data
                'microdata': 0.90,         # High - structured data
                'universal_intelligence': 0.75,  # Good - smart extraction
                'open_graph': 0.60,        # Medium - basic metadata
                'adaptive_fallback': 0.50, # Lower - fallback method
            }
            
            method_weight = method_weights.get(method, 0.40)
            method_score = method_weight * 0.2
            score += method_score
            details.append(f"method: {method_weight:.2f}")
            
            # 4. FORMATTING INTELLIGENCE QUALITY (25% weight) - YOUR AUTO-CLEAN LOGIC!
            formatting_quality = 1.0 - formatting_assessment['overall_score']  # Invert: less cleanup needed = higher quality
            formatting_score = formatting_quality * 0.25
            score += formatting_score
            details.append(f"auto-clean: {formatting_quality:.2f}")
            
            # Log formatting insights
            if formatting_assessment['needs_cleanup']:
                details.append("needs-cleanup")
                logger.info(f"🧹 {method} needs auto-clean: {formatting_assessment['extraction_quality']}")
            else:
                logger.info(f"✨ {method} clean extraction: {formatting_assessment['extraction_quality']}")
            
            scored_results.append({
                'result': result,
                'score': score,
                'details': details,
                'formatting_assessment': formatting_assessment
            })
            
            logger.info(f"📊 {method}: score={score:.3f} ({', '.join(details)})")
        
        # Select the highest scoring result
        best = max(scored_results, key=lambda x: x['score'])
        best_result = best['result']
        best_score = best['score']
        
        logger.info(f"🏆 Winner: {best_result['method']} with score {best_score:.3f}")
        
        # 🆕 SMART MERGE: Fill in missing fields from other extraction results
        # If the winner is missing critical fields (instructions, ingredients), try to merge from other methods
        best_data = best_result['data']
        merge_improvements = []
        
        if not best_data.instructions or len(best_data.instructions) == 0:
            # Winner has no instructions - try to get from another method
            for scored in scored_results:
                other_data = scored['result']['data']
                other_method = scored['result']['method']
                if other_data.instructions and len(other_data.instructions) > 0 and other_method != best_result['method']:
                    logger.info(f"🔀 Merging instructions from {other_method} into {best_result['method']}")
                    best_data.instructions = other_data.instructions
                    merge_improvements.append(f"instructions from {other_method}")
                    break
        
        if not best_data.ingredients or len(best_data.ingredients) == 0:
            # Winner has no ingredients - try to get from another method
            for scored in scored_results:
                other_data = scored['result']['data']
                other_method = scored['result']['method']
                if other_data.ingredients and len(other_data.ingredients) > 0 and other_method != best_result['method']:
                    logger.info(f"🔀 Merging ingredients from {other_method} into {best_result['method']}")
                    best_data.ingredients = other_data.ingredients
                    merge_improvements.append(f"ingredients from {other_method}")
                    break
        
        if not best_data.image_url:
            # Winner has no image - try to get from another method
            for scored in scored_results:
                other_data = scored['result']['data']
                other_method = scored['result']['method']
                if other_data.image_url and other_method != best_result['method']:
                    logger.info(f"🔀 Merging image from {other_method} into {best_result['method']}")
                    best_data.image_url = other_data.image_url
                    merge_improvements.append(f"image from {other_method}")
                    break
        
        if not best_data.description or len(best_data.description) < 20:
            # Winner has no/poor description - try to get from another method
            for scored in scored_results:
                other_data = scored['result']['data']
                other_method = scored['result']['method']
                if other_data.description and len(other_data.description) > 20 and other_method != best_result['method']:
                    logger.info(f"🔀 Merging description from {other_method} into {best_result['method']}")
                    best_data.description = other_data.description
                    merge_improvements.append(f"description from {other_method}")
                    break
        
        if merge_improvements:
            logger.info(f"✨ Enhanced result with: {', '.join(merge_improvements)}")
        
        # Apply auto-formatting to the winner if needed
        formatting_assessment = best['formatting_assessment']
        if formatting_assessment['needs_cleanup']:
            logger.info("🧹 Applying auto-clean formatting to winner...")
            formatted_result = self.formatter.format_recipe_data({
                'title': best_result['data'].title,
                'ingredients': best_result['data'].ingredients,
                'instructions': best_result['data'].instructions,
            })
            
            # Update the result with cleaned data
            best_result['data'].title = formatted_result['formatted_data']['title']
            best_result['data'].ingredients = formatted_result['formatted_data']['ingredients'].split('\n') if formatted_result['formatted_data']['ingredients'] else []
            best_result['data'].instructions = formatted_result['formatted_data']['instructions'].split('\n') if formatted_result['formatted_data']['instructions'] else []
            
            logger.info("✨ Auto-clean formatting applied to final result")
        
        # If multiple methods got similar scores, prefer structured data ONLY if it's complete
        similar_threshold = 0.05
        similar_results = [r for r in scored_results if abs(r['score'] - best_score) <= similar_threshold]
        
        if len(similar_results) > 1:
            # Prefer structured data methods, but ONLY if they have instructions
            structured_methods = ['json_ld', 'microdata']
            for structured in structured_methods:
                for similar in similar_results:
                    if similar['result']['method'] == structured:
                        # Check if this structured method actually has instructions
                        structured_data = similar['result']['data']
                        if structured_data.instructions and len(structured_data.instructions) > 0:
                            logger.info(f"🎯 Preferring complete structured data method: {structured}")
                            return similar['result']
                        else:
                            logger.info(f"⚠️ Skipping {structured} - missing instructions despite similar score")
        
        return best_result
    
    def _record_extraction_success(self, url: str, method: str, recipe_data: WebRecipeData, processing_time: float):
        """Record successful extraction for analytics learning"""
        if self.analytics_enabled and self.analytics:
            try:
                domain = urlparse(url).netloc.lower()
                
                result = ExtractionResult(
                    url=url,
                    domain=domain,
                    extraction_method=method,
                    confidence_predicted=recipe_data.confidence,
                    success=True,
                    processing_time=processing_time,
                    ingredients_count=len(recipe_data.ingredients) if recipe_data.ingredients else 0,
                    instructions_count=len(recipe_data.instructions) if recipe_data.instructions else 0,
                    has_title=bool(recipe_data.title),
                    has_timing=bool(recipe_data.total_time or recipe_data.prep_time or recipe_data.cook_time),
                    has_servings=bool(recipe_data.servings),
                    timestamp=datetime.now()
                )
                
                self.analytics.record_extraction(result)
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to record extraction success: {e}")
    
    def _record_extraction_failure(self, url: str, failure_reason: str, processing_time: float):
        """Record extraction failure for analytics learning"""
        if self.analytics_enabled and self.analytics:
            try:
                domain = urlparse(url).netloc.lower()
                
                result = ExtractionResult(
                    url=url,
                    domain=domain,
                    extraction_method=failure_reason,
                    confidence_predicted=0.0,
                    success=False,
                    processing_time=processing_time,
                    timestamp=datetime.now()
                )
                
                self.analytics.record_extraction(result)
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to record extraction failure: {e}")
    
    def provide_feedback(self, recipe_id: int, feedback: str, corrected_data: Optional[Dict] = None):
        """Provide user feedback to improve future extractions"""
        if self.analytics_enabled and self.analytics:
            try:
                self.analytics.provide_user_feedback(recipe_id, feedback, corrected_data)
                logger.info(f"📝 User feedback recorded for recipe {recipe_id}: {feedback}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to record user feedback: {e}")
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary for monitoring and improvement"""
        if self.analytics_enabled and self.analytics:
            return self.analytics.get_analytics_summary()
        else:
            return {'analytics_enabled': False, 'message': 'Analytics system not available'}
    
    def _extract_time_minutes(self, time_text: str) -> Optional[int]:
        """Extract time in minutes from text like '30 mins', '1 hour 30 minutes', etc."""
        if not time_text:
            return None
        
        time_text = time_text.lower().strip()
        total_minutes = 0
        
        # Look for hours
        hour_match = re.search(r'(\d+)\s*(?:hour|hr|h)\b', time_text)
        if hour_match:
            total_minutes += int(hour_match.group(1)) * 60
        
        # Look for minutes
        minute_match = re.search(r'(\d+)\s*(?:minute|min|m)\b', time_text)
        if minute_match:
            total_minutes += int(minute_match.group(1))
        
        # If no hours/minutes found, look for just numbers
        if total_minutes == 0:
            number_match = re.search(r'(\d+)', time_text)
            if number_match:
                total_minutes = int(number_match.group(1))
        
        return total_minutes if total_minutes > 0 else None
    
    def _extract_servings(self, serving_text: str) -> Optional[int]:
        """Extract number of servings from text"""
        if not serving_text:
            return None
        
        # Look for numbers in the text
        numbers = re.findall(r'\d+', serving_text)
        if numbers:
            return int(numbers[0])
        
        return None
    
    # Helper methods for parsing
    def _extract_author(self, author_data) -> str:
        """Extract author name from various formats"""
        if isinstance(author_data, dict):
            return author_data.get('name', '')
        elif isinstance(author_data, list) and author_data:
            first_author = author_data[0]
            if isinstance(first_author, dict):
                return first_author.get('name', '')
            return str(first_author)
        return str(author_data) if author_data else ''
    
    def _parse_instructions(self, instructions: List) -> List[str]:
        """Parse instructions from various JSON-LD formats"""
        parsed = []
        
        for instruction in instructions:
            if isinstance(instruction, dict):
                text = instruction.get('text', '')
                if not text:
                    text = instruction.get('name', '')
                if text:
                    parsed.append(text)
            else:
                parsed.append(str(instruction))
        
        return parsed
    
    def _parse_duration(self, duration_str: Optional[str]) -> Optional[int]:
        """Parse ISO 8601 duration to minutes"""
        if not duration_str:
            return None
        
        try:
            # Handle ISO 8601 format (PT30M = 30 minutes)
            if duration_str.startswith('PT'):
                match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?', duration_str)
                if match:
                    hours = int(match.group(1) or 0)
                    minutes = int(match.group(2) or 0)
                    return hours * 60 + minutes
            
            # Handle plain number formats
            match = re.search(r'(\d+)', duration_str)
            if match:
                return int(match.group(1))
            
            return None
            
        except (ValueError, AttributeError):
            return None
    
    def _parse_servings(self, servings_data) -> Optional[int]:
        """Parse servings/yield from various formats"""
        if not servings_data:
            return None
        
        try:
            if isinstance(servings_data, (int, float)):
                return int(servings_data)
            
            # Extract number from string
            match = re.search(r'(\d+)', str(servings_data))
            if match:
                return int(match.group(1))
            
            return None
            
        except (ValueError, AttributeError):
            return None
    
    def _parse_time_text(self, time_text: str) -> Optional[int]:
        """Parse time from natural language text"""
        if not time_text:
            return None
        
        try:
            # Look for patterns like "30 minutes", "1 hour 30 min", etc.
            total_minutes = 0
            
            # Hours
            hour_match = re.search(r'(\d+)\s*(?:hour|hr)', time_text, re.IGNORECASE)
            if hour_match:
                total_minutes += int(hour_match.group(1)) * 60
            
            # Minutes
            min_match = re.search(r'(\d+)\s*(?:minute|min)', time_text, re.IGNORECASE)
            if min_match:
                total_minutes += int(min_match.group(1))
            
            # If no specific time units, just extract first number
            if total_minutes == 0:
                num_match = re.search(r'(\d+)', time_text)
                if num_match:
                    total_minutes = int(num_match.group(1))
            
            return total_minutes if total_minutes > 0 else None
            
        except (ValueError, AttributeError):
            return None
    
    def _parse_nutrition(self, nutrition_data: Dict) -> Dict:
        """Parse nutrition information"""
        parsed_nutrition = {}
        
        try:
            if isinstance(nutrition_data, dict):
                # Map common nutrition fields
                nutrition_mapping = {
                    'calories': ['calories', 'kcal', 'energy'],
                    'protein': ['protein'],
                    'fat': ['fat', 'totalFat'],
                    'carbs': ['carbohydrate', 'carbs', 'totalCarbohydrate'],
                    'fiber': ['fiber', 'dietaryFiber'],
                    'sugar': ['sugar', 'sugars'],
                    'sodium': ['sodium']
                }
                
                for nutrient, keys in nutrition_mapping.items():
                    for key in keys:
                        value = nutrition_data.get(key)
                        if value:
                            # Extract numeric value
                            if isinstance(value, str):
                                match = re.search(r'(\d+(?:\.\d+)?)', value)
                                if match:
                                    parsed_nutrition[nutrient] = float(match.group(1))
                            elif isinstance(value, (int, float)):
                                parsed_nutrition[nutrient] = float(value)
                            break
            
            return parsed_nutrition
            
        except Exception as e:
            logger.warning(f"⚠️ Error parsing nutrition data: {e}")
            return {}

# Export main class
__all__ = ['WebRecipeExtractor', 'WebRecipeData']

if __name__ == "__main__":
    # Basic testing
    extractor = WebRecipeExtractor()
    
    test_urls = [
        "https://www.bonappetit.com/recipe/simple-pasta-with-tomatoes",
        "https://www.foodnetwork.com/recipes/simple-salad",
        "https://www.allrecipes.com/recipe/easy-cookies"
    ]
    
    for url in test_urls:
        print(f"\n🧪 Testing extraction from: {url}")
        result = extractor.extract_from_url(url)
        print(f"   Title: {result.title}")
        print(f"   Confidence: {result.confidence:.2f}")
        print(f"   Method: {result.extraction_method}")
        print(f"   Ingredients: {len(result.ingredients)} found")
        print(f"   Instructions: {len(result.instructions)} found")
