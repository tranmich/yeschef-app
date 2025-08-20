#!/usr/bin/env python3
"""
🧠 SEMANTIC RECIPE RECOGNITION ENGINE
=====================================

This is the core component that UNDERSTANDS what recipes actually are,
not just what cookbook text looks like. It provides semantic validation
and intelligent content classification.

Key Features:
- Food/dish recognition and validation
- Cooking method and technique understanding  
- Ingredient semantic analysis
- Instruction flow validation
- Context-aware content classification
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum

class ContentType(Enum):
    """Types of content found in cookbooks"""
    RECIPE_TITLE = "recipe_title"
    INGREDIENT_LIST = "ingredient_list" 
    INSTRUCTION_STEPS = "instruction_steps"
    INSTRUCTION_HEADER = "instruction_header"  # "Start Cooking!", "Before You Begin"
    RECIPE_METADATA = "recipe_metadata"  # servings, time, difficulty
    PAGE_METADATA = "page_metadata"  # page numbers, references
    EDUCATIONAL_CONTENT = "educational_content"  # "Why this works"
    TABLE_OF_CONTENTS = "table_of_contents"
    NON_RECIPE_CONTENT = "non_recipe_content"
    EXTRACTION_ARTIFACT = "extraction_artifact"

class ValidationLevel(Enum):
    """Validation strictness levels"""
    STRICT = "strict"  # Production quality - zero tolerance for artifacts
    MODERATE = "moderate"  # Development - some flexibility
    PERMISSIVE = "permissive"  # Testing - maximum acceptance

@dataclass
class RecipeComponent:
    """Represents a validated recipe component"""
    content: str
    content_type: ContentType
    confidence_score: float  # 0.0 to 1.0
    validation_notes: List[str]
    source_info: Dict[str, str]  # page, line, etc.

@dataclass 
class RecipeValidationResult:
    """Complete recipe validation results"""
    is_valid_recipe: bool
    confidence_score: float
    components: List[RecipeComponent]
    validation_errors: List[str]
    validation_warnings: List[str]
    quality_metrics: Dict[str, float]

class SemanticRecipeEngine:
    """Core engine for semantic recipe understanding"""
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.STRICT):
        self.validation_level = validation_level
        self.food_database = self._load_food_database()
        self.cooking_methods = self._load_cooking_methods()
        self.recipe_patterns = self._load_recipe_patterns()
        self.artifact_patterns = self._load_artifact_patterns()
    
    def _load_food_database(self) -> Dict[str, Set[str]]:
        """Load comprehensive food item database"""
        return {
            'proteins': {
                'chicken', 'beef', 'pork', 'fish', 'turkey', 'lamb', 'duck', 'salmon',
                'shrimp', 'crab', 'lobster', 'scallops', 'tuna', 'cod', 'halibut',
                'eggs', 'tofu', 'beans', 'lentils', 'chickpeas', 'quinoa'
            },
            'vegetables': {
                'onion', 'garlic', 'carrot', 'celery', 'potato', 'tomato', 'pepper',
                'mushroom', 'broccoli', 'spinach', 'lettuce', 'cucumber', 'zucchini',
                'eggplant', 'asparagus', 'cauliflower', 'cabbage', 'kale', 'corn',
                'peas', 'avocado', 'artichoke', 'beet', 'radish', 'turnip'
            },
            'grains_starches': {
                'rice', 'pasta', 'bread', 'flour', 'noodles', 'quinoa', 'barley',
                'oats', 'wheat', 'cornmeal', 'polenta', 'couscous', 'bulgur'
            },
            'dairy': {
                'milk', 'cream', 'butter', 'cheese', 'yogurt', 'sour cream',
                'mozzarella', 'cheddar', 'parmesan', 'ricotta', 'feta', 'goat cheese'
            },
            'herbs_spices': {
                'salt', 'pepper', 'basil', 'oregano', 'thyme', 'rosemary', 'sage',
                'parsley', 'cilantro', 'dill', 'chives', 'mint', 'paprika', 'cumin',
                'coriander', 'cinnamon', 'nutmeg', 'vanilla', 'ginger', 'turmeric'
            },
            'pantry_basics': {
                'oil', 'vinegar', 'sugar', 'honey', 'maple syrup', 'soy sauce',
                'stock', 'broth', 'wine', 'lemon', 'lime', 'mustard', 'ketchup'
            },
            'dessert_ingredients': {
                'chocolate', 'cocoa', 'chips', 'cookie', 'cookies', 'cake', 'frosting',
                'vanilla', 'strawberry', 'raspberry', 'blueberry', 'apple', 'banana',
                'cream cheese', 'powdered sugar', 'brown sugar', 'caramel'
            },
            'nuts_legumes': {
                'almonds', 'walnuts', 'pecans', 'pistachios', 'cashews', 'peanuts',
                'pine nuts', 'hazelnuts', 'macadamia', 'chickpeas', 'black beans',
                'kidney beans', 'pinto beans', 'navy beans', 'lima beans', 'lentils'
            },
            'prepared_foods': {
                'hummus', 'tahini', 'pesto', 'salsa', 'guacamole', 'tzatziki',
                'aioli', 'mayo', 'mayonnaise', 'dressing', 'marinade', 'sauce'
            },
            'common_dishes': {
                'salad', 'soup', 'stew', 'chili', 'casserole', 'pizza', 'sandwich',
                'burger', 'taco', 'burrito', 'pasta', 'rice', 'noodles', 'bread',
                'curry', 'stir-fry', 'risotto', 'paella', 'gumbo', 'jambalaya',
                'deviled eggs', 'hard-cooked eggs', 'scrambled eggs'
            }
        }
    
    def _load_cooking_methods(self) -> Dict[str, Set[str]]:
        """Load cooking methods and techniques"""
        return {
            'basic_methods': {
                'bake', 'roast', 'grill', 'broil', 'fry', 'sauté', 'sear', 'boil',
                'simmer', 'steam', 'poach', 'braise', 'stew', 'microwave'
            },
            'preparation_methods': {
                'chop', 'dice', 'mince', 'slice', 'grate', 'shred', 'julienne',
                'whisk', 'beat', 'fold', 'mix', 'combine', 'stir', 'toss', 'season'
            },
            'advanced_techniques': {
                'confit', 'sous vide', 'flambe', 'deglaze', 'emulsify', 'temper',
                'caramelize', 'reduce', 'bloom', 'proof', 'knead', 'rest'
            }
        }
    
    def _load_recipe_patterns(self) -> Dict[str, List[str]]:
        """Load patterns that indicate legitimate recipe content"""
        return {
            'dish_types': [
                r'\b(soup|stew|salad|pasta|pizza|bread|cake|pie|cookies?|muffins?)\b',
                r'\b(chicken|beef|pork|fish|salmon|turkey|lamb)\b.*\b(recipe|dish|roast|grilled|baked)\b',
                r'\b(roasted|grilled|baked|fried|sautéed|braised|steamed)\b.*\b(vegetables?|potatoes?|chicken|beef)\b',
                r'\b(chocolate|vanilla|strawberry|lemon|apple|banana)\b.*\b(cake|pie|cookies?|muffins?|bread)\b',
                r'\b(spicy|creamy|crispy|tender|fluffy|moist)\b.*\b(rice|pasta|chicken|vegetables?)\b'
            ],
            'recipe_title_indicators': [
                r'\b(recipe|dish|plate|bowl)\b',
                r'\b(with|and|in|on)\b.*\b(sauce|dressing|marinade|glaze)\b',
                r'\b(style|inspired|traditional|classic|homemade)\b',
                r'\b(easy|quick|simple|perfect|ultimate|best)\b'
            ],
            'measurement_patterns': [
                r'\b\d+\s*(cup|cups|tablespoon|tablespoons|teaspoon|teaspoons|tbsp|tsp|pound|pounds|lb|lbs|ounce|ounces|oz)\b',
                r'\b\d+[-/]\d+\s*(cup|tablespoon|teaspoon|pound|ounce)\b',
                r'\b\d+\.\d+\s*(cup|tablespoon|teaspoon|pound|ounce)\b',
                r'\b(⅛|⅜|⅝⅞|¼|¾|½|⅓|⅔)\s*(cup|tablespoon|teaspoon|pound|ounce)\b'
            ]
        }
    
    def _load_artifact_patterns(self) -> Dict[str, List[str]]:
        """Load patterns that indicate extraction artifacts"""
        return {
            'instruction_headers': [
                r'^(start cooking!?|before you begin|prepare ingredients)$',
                r'^(method|directions|instructions)$',
                r'^(step \d+|phase \d+)$'
            ],
            'page_metadata': [
                r'^(page \d+|p\. \d+|\d+ of \d+)$',
                r'^(recipe from page \d+|atk recipe from page \d+)$',
                r'^(book id: \d+.*page: \d+)$',
                r'^(chapter \d+|section [a-z])$'
            ],
            'extraction_artifacts': [
                r'^[a-z]{1,3}$',  # Single letters or very short garbled text
                r'see photo|see this page|turn to page',
                r'wi\s+th|fro\s+m|unti\s+l',  # Common OCR errors with spaces (require at least one space)
                r'^(topping|filling|sauce|dressing|marinade)$',  # Ingredient section headers
                r'^\d+\.\s*$'  # Orphaned step numbers
            ],
            'non_food_content': [
                r'^(introduction|acknowledgments|index|contents)$',
                r'^(why this recipe works|the science|testing notes)$',
                r'^(equipment review|ingredient spotlight)$',
                r'^(nutritional information|dietary notes)$'
            ]
        }
    
    def classify_content_type(self, text: str, context: Dict = None) -> Tuple[ContentType, float]:
        """
        Classify a piece of text into its content type with confidence score
        
        Args:
            text: The text to classify
            context: Additional context (page number, surrounding text, etc.)
            
        Returns:
            Tuple of (ContentType, confidence_score)
        """
        text_clean = text.strip().lower()
        
        # Check for extraction artifacts first (highest priority)
        if self._is_extraction_artifact(text_clean):
            return ContentType.EXTRACTION_ARTIFACT, 0.95
        
        # Check for instruction headers
        if self._is_instruction_header(text_clean):
            return ContentType.INSTRUCTION_HEADER, 0.90
        
        # Check for page metadata
        if self._is_page_metadata(text_clean):
            return ContentType.PAGE_METADATA, 0.90
        
        # Check for non-recipe content
        if self._is_non_recipe_content(text_clean):
            return ContentType.NON_RECIPE_CONTENT, 0.85
        
        # Check for recipe components (use original case for better detection)
        if self._is_recipe_title(text):
            return ContentType.RECIPE_TITLE, 0.80
        
        if self._is_instruction_steps(text):
            return ContentType.INSTRUCTION_STEPS, 0.85
        
        if self._is_ingredient_list(text):
            return ContentType.INGREDIENT_LIST, 0.85
        
        if self._is_recipe_metadata(text):
            return ContentType.RECIPE_METADATA, 0.75
        
        if self._is_educational_content(text):
            return ContentType.EDUCATIONAL_CONTENT, 0.70
        
        # Default: unknown content
        return ContentType.NON_RECIPE_CONTENT, 0.30
    
    def _is_extraction_artifact(self, text: str) -> bool:
        """Check if text is an extraction artifact"""
        # Check for specific page reference patterns first
        if re.search(r'recipe from page \d+', text, re.IGNORECASE):
            return True
        
        for pattern_list in self.artifact_patterns['extraction_artifacts']:
            if re.search(pattern_list, text, re.IGNORECASE):
                return True
        
        # Additional heuristics
        if len(text) <= 3 and text.isalpha():  # Single letters/short garbled text
            return True
        
        # Check for very short content that doesn't contain food words
        if len(text.split()) == 1 and len(text) < 15 and not self._contains_food_words(text):
            return True
        
        return False
    
    def _is_instruction_header(self, text: str) -> bool:
        """Check if text is an instruction header (not actual recipe content)"""
        for pattern in self.artifact_patterns['instruction_headers']:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _is_page_metadata(self, text: str) -> bool:
        """Check if text is page metadata"""
        for pattern in self.artifact_patterns['page_metadata']:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _is_non_recipe_content(self, text: str) -> bool:
        """Check if text is non-recipe content"""
        for pattern in self.artifact_patterns['non_food_content']:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _is_recipe_title(self, text: str) -> bool:
        """Check if text is a legitimate recipe title"""
        # Must be reasonable length
        if len(text) < 3 or len(text) > 100:
            return False
        
        # First check if it's definitely NOT a recipe title
        text_lower = text.lower()
        text_clean = text.strip()
        
        # Reject instruction headers
        if self._is_instruction_header(text_lower):
            return False
        
        # Reject page metadata
        if self._is_page_metadata(text_lower):
            return False
        
        # Reject extraction artifacts
        if self._is_extraction_artifact(text_lower):
            return False
        
        # CRITICAL: Reject ingredient lines (they start with bullets or measurements)
        if text_clean.startswith('•') or text_clean.startswith('-'):
            return False
        
        if re.match(r'^\d+\s*(cup|tablespoon|teaspoon|pound|ounce|tbsp|tsp|lb|oz)', text_clean, re.IGNORECASE):
            return False
        
        # CRITICAL: Reject instruction steps (they start with numbers)
        if re.match(r'^\d+\.', text_clean):
            return False
        
        # CRITICAL: Reject metadata-only lines
        if re.match(r'^(SERVES|MAKES|YIELDS?)\s+\d+$', text_clean, re.IGNORECASE):
            return False
        
        if re.match(r'^\d+\s+(MINUTES?|HOURS?)$', text_clean, re.IGNORECASE):
            return False
        
        if re.match(r'^(BEGINNER|INTERMEDIATE|ADVANCED)$', text_clean, re.IGNORECASE):
            return False
        
        # ENHANCED FRAGMENT DETECTION - Critical for quality
        # Reject obvious measurement strings or fragments
        if re.search(r'\d+\s*(cup|tablespoon|teaspoon|pound|ounce|tbsp|tsp|lb|oz|clove|slice)', text_lower):
            return False
        
        # Reject single words that aren't complete recipe names
        word_count = len(text_clean.split())
        if word_count == 1:
            # Only allow single words if they're iconic complete dish names
            iconic_dishes = {'chili', 'risotto', 'paella', 'ratatouille', 'gazpacho', 'bouillabaisse', 'jambalaya'}
            if text_lower not in iconic_dishes:
                return False
        
        # Reject incomplete fragments (sentences that don't start with capital or end mid-sentence)
        if not text_clean[0].isupper():
            return False
        
        # Reject if it contains sentence fragments or incomplete thoughts
        fragment_indicators = [
            'saucepan', 'skillet', 'bowl', 'plate', 'serving', 'mixture',
            'remaining', 'additional', 'optional', 'garnish', 'aside',
            'transfer', 'combine', 'process', 'continue', 'until'
        ]
        if any(indicator in text_lower for indicator in fragment_indicators):
            return False
        
        # Reject if it ends with incomplete sentence punctuation
        if text_clean.endswith((',', ';', '...', '.')):
            return False
        
        # Reject if it contains parentheses or brackets (usually sub-components or notes)
        if any(char in text_clean for char in ['(', ')', '[', ']', '{', '}']):
            return False
        
        # ENHANCED: Reject obvious sentence fragments or instruction text
        sentence_fragment_indicators = [
            'set over', 'bake', 'heat', 'cook until', 'transfer', 'remove from',
            'place on', 'arrange', 'spread', 'pour', 'stir in', 'add to',
            'cut into', 'slice', 'chop', 'mince', 'dice', 'drain', 'rinse'
        ]
        if any(indicator in text_lower for indicator in sentence_fragment_indicators):
            return False
        
        # Reject if it contains broken words from PDF extraction (spaces within words)
        broken_word_pattern = r'\b[a-z] [a-z]{2,}\b'  # matches "br ead", "o ver", "wir e"
        if re.search(broken_word_pattern, text_lower):
            return False
        
        # Must contain food-related words OR cooking methods
        if not self._contains_food_words(text) and not self._contains_cooking_words(text):
            return False
        
        # ENHANCED VALIDATION: Must sound like a complete dish name
        # Check for dish type patterns
        for pattern in self.recipe_patterns['dish_types']:
            if re.search(pattern, text_lower):
                return True
        
        # Check for recipe title indicators with food words
        if self._contains_food_words(text):
            for pattern in self.recipe_patterns['recipe_title_indicators']:
                if re.search(pattern, text_lower):
                    return True
            
            # Enhanced validation for food-word titles
            if 2 <= word_count <= 8:  # Reasonable title length
                # Must not look like an ingredient or instruction
                if not self._looks_like_ingredient_line(text) and not self._looks_like_instruction_line(text):
                    # Additional check: must sound like a complete dish
                    if self._sounds_like_complete_dish(text):
                        return True
        
        return False
    
    def _looks_like_ingredient_line(self, text: str) -> bool:
        """Check if text looks like an ingredient line rather than a title"""
        text_clean = text.strip()
        
        # Starts with bullet point
        if text_clean.startswith('•') or text_clean.startswith('-'):
            return True
        
        # Has measurements at the beginning
        if re.match(r'^\d+\s*(cup|tablespoon|teaspoon|pound|ounce|tbsp|tsp|lb|oz)', text_clean, re.IGNORECASE):
            return True
        
        # Has fractions with measurements
        if re.match(r'^(\d+/\d+|\d+\.\d+|⅛|⅜|⅝⅞|¼|¾|½|⅓|⅔)\s*(cup|tablespoon|teaspoon|pound|ounce)', text_clean, re.IGNORECASE):
            return True
        
        return False
    
    def _sounds_like_complete_dish(self, text: str) -> bool:
        """Check if text sounds like a complete dish name rather than a fragment"""
        text_lower = text.lower()
        text_clean = text.strip()
        
        # Must have reasonable structure - not just random words
        words = text_clean.split()
        
        # Check for dish completion indicators
        dish_completion_patterns = [
            # Complete dish formats: "Adjective + Protein", "Cooking Method + Protein", etc.
            r'\b(grilled|baked|roasted|fried|steamed|braised|seared|pan|slow)\s+(chicken|beef|pork|fish|salmon|turkey|lamb)',
            r'\b(chicken|beef|pork|fish|salmon|turkey|lamb)\s+(with|and|in|over)',
            r'\b(classic|perfect|ultimate|best|easy|quick|homemade|traditional)\s+\w+',
            r'\b\w+\s+(soup|salad|pasta|rice|beans|bread|cake|pie|sauce|stew|chili)',
            r'\b(stuffed|glazed|marinated|crusted|topped)\s+\w+',
            # Regional/style indicators
            r'\b(italian|mexican|asian|french|thai|indian|mediterranean)\s+\w+',
            r'\b\w+\s+(style|recipe|version)',
        ]
        
        for pattern in dish_completion_patterns:
            if re.search(pattern, text_lower):
                return True
        
        # Check if it contains complete dish structure words
        structure_words = {
            'cooking_methods': ['grilled', 'baked', 'roasted', 'fried', 'steamed', 'braised', 'sauteed', 'pan-fried'],
            'descriptors': ['classic', 'perfect', 'ultimate', 'best', 'easy', 'quick', 'homemade', 'traditional', 'crispy', 'tender', 'ultracreamy', 'creamy', 'spiced', 'fresh', 'simple'],
            'proteins': ['chicken', 'beef', 'pork', 'fish', 'salmon', 'turkey', 'lamb', 'shrimp'],
            'dish_types': ['soup', 'salad', 'pasta', 'rice', 'beans', 'bread', 'cake', 'pie', 'sauce', 'stew'],
            'preparations': ['stuffed', 'glazed', 'marinated', 'crusted', 'topped', 'seasoned', 'spiced', 'deviled']
        }
        
        # Count structure indicators
        structure_count = 0
        for category, word_list in structure_words.items():
            if any(word in text_lower for word in word_list):
                structure_count += 1
        
        # Need at least 2 structure elements for a complete dish
        if structure_count >= 2:
            return True
        
        # Special case: iconic single-word dishes that are complete
        iconic_complete_dishes = {
            'chili', 'risotto', 'paella', 'ratatouille', 'gazpacho', 'bouillabaisse', 
            'jambalaya', 'gumbo', 'curry', 'stir-fry', 'meatloaf', 'meatballs',
            'lasagna', 'stroganoff', 'carbonara', 'puttanesca', 'minestrone',
            'hummus', 'guacamole', 'tzatziki', 'pesto', 'salsa'
        }
        
        if len(words) == 1 and text_lower in iconic_complete_dishes:
            return True
        
        # For multi-word titles, check for completeness indicators
        if len(words) >= 2:
            # Has food word + descriptor/method = likely complete
            food_words = self._get_all_food_words()
            has_food_word = any(word.lower() in food_words for word in words)
            has_method_or_descriptor = any(word.lower() in 
                structure_words['cooking_methods'] + structure_words['descriptors'] + structure_words['preparations'] 
                for word in words)
            
            if has_food_word and has_method_or_descriptor:
                return True
            
            # RELAXED: If it has 2+ food words, it's likely a complete dish
            food_word_count = sum(1 for word in words if word.lower() in food_words)
            if food_word_count >= 2:
                return True
            
            # RELAXED: If it mentions "topping", "sauce", "dressing" etc + food word, it's complete
            dish_component_words = ['topping', 'sauce', 'dressing', 'marinade', 'glaze', 'filling']
            has_component = any(word.lower() in dish_component_words for word in words)
            if has_component and has_food_word:
                return True
        
        return False
    
    def _get_all_food_words(self) -> set:
        """Get all food words from the food database"""
        all_food_words = set()
        for category, words in self.food_database.items():
            all_food_words.update(words)
        return all_food_words
    
    def _looks_like_instruction_line(self, text: str) -> bool:
        """Check if text looks like an instruction line rather than a title"""
        text_clean = text.strip()
        
        # Starts with step number
        if re.match(r'^\d+\.', text_clean):
            return True
        
        # Very long lines are usually instructions, not titles
        if len(text_clean) > 80:
            return True
        
        return False
    
    def _is_ingredient_list(self, text: str) -> bool:
        """Check if text is an ingredient list"""
        # Look for measurement patterns
        measurement_count = 0
        for pattern in self.recipe_patterns['measurement_patterns']:
            measurement_count += len(re.findall(pattern, text, re.IGNORECASE))
        
        # Must have reasonable number of measurements
        if measurement_count < 2:
            return False
        
        # Must contain food words
        if not self._contains_food_words(text):
            return False
        
        # Check for ingredient list formatting
        lines = text.split('\n')
        ingredient_lines = 0
        for line in lines:
            line = line.strip()
            if line and (line.startswith('•') or line.startswith('-') or 
                        re.match(r'^\d+', line) or
                        any(re.search(p, line, re.IGNORECASE) for p in self.recipe_patterns['measurement_patterns'])):
                ingredient_lines += 1
        
        return ingredient_lines >= 2
    
    def _is_instruction_steps(self, text: str) -> bool:
        """Check if text contains cooking instructions"""
        # Look for numbered steps
        numbered_steps = len(re.findall(r'^\d+\.', text, re.MULTILINE))
        if numbered_steps < 1:
            return False
        
        # Must contain cooking methods
        if not self._contains_cooking_words(text):
            return False
        
        # Should be substantial content
        if len(text.strip()) < 20:
            return False
        
        return True
    
    def _is_recipe_metadata(self, text: str) -> bool:
        """Check if text contains recipe metadata (servings, time, etc.)"""
        metadata_patterns = [
            r'(serves|makes|yields?)\s+\d+',
            r'\d+\s+(minutes?|hours?|mins?|hrs?)',
            r'(prep|cook|total)\s+time',
            r'(beginner|intermediate|advanced|easy|medium|hard)',
            r'(vegetarian|vegan|gluten.?free|dairy.?free)'
        ]
        
        text_lower = text.lower()
        for pattern in metadata_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def _is_educational_content(self, text: str) -> bool:
        """Check if text is educational content"""
        educational_indicators = [
            'why this recipe works', 'the science', 'testing notes',
            'technique tip', 'chef\'s note', 'cooking tip'
        ]
        
        text_lower = text.lower()
        for indicator in educational_indicators:
            if indicator in text_lower:
                return True
        
        return False
    
    def _contains_cooking_words(self, text: str) -> bool:
        """Check if text contains cooking-related words"""
        text_lower = text.lower()
        
        # Check for cooking-related words
        for method_category in self.cooking_methods.values():
            for method in method_category:
                if method in text_lower:
                    return True
        
        return False
    
    def _contains_food_words(self, text: str) -> bool:
        """Check if text contains actual food-related words"""
        text_lower = text.lower()
        
        # Check against food database
        for category, foods in self.food_database.items():
            for food in foods:
                if food in text_lower:
                    return True
        
        return False
    
    def validate_complete_recipe(self, recipe_data: Dict) -> RecipeValidationResult:
        """
        Validate a complete recipe using semantic understanding
        
        Args:
            recipe_data: Dictionary containing recipe components
            
        Returns:
            RecipeValidationResult with detailed validation info
        """
        components = []
        errors = []
        warnings = []
        quality_metrics = {}
        
        # Validate title
        title = recipe_data.get('title', '').strip()
        title_type, title_confidence = self.classify_content_type(title)
        
        if title_type != ContentType.RECIPE_TITLE:
            errors.append(f"Title '{title}' is not a valid recipe title (detected as {title_type.value})")
        else:
            components.append(RecipeComponent(
                content=title,
                content_type=ContentType.RECIPE_TITLE,
                confidence_score=title_confidence,
                validation_notes=[],
                source_info={}
            ))
        
        # Validate ingredients
        ingredients = recipe_data.get('ingredients', '').strip()
        if ingredients:
            ing_type, ing_confidence = self.classify_content_type(ingredients)
            if ing_type != ContentType.INGREDIENT_LIST:
                errors.append(f"Ingredients section is not valid (detected as {ing_type.value})")
            else:
                components.append(RecipeComponent(
                    content=ingredients,
                    content_type=ContentType.INGREDIENT_LIST,
                    confidence_score=ing_confidence,
                    validation_notes=[],
                    source_info={}
                ))
        else:
            errors.append("Missing ingredients section")
        
        # Validate instructions
        instructions = recipe_data.get('instructions', '').strip()
        if instructions:
            inst_type, inst_confidence = self.classify_content_type(instructions)
            if inst_type != ContentType.INSTRUCTION_STEPS:
                errors.append(f"Instructions section is not valid (detected as {inst_type.value})")
            else:
                components.append(RecipeComponent(
                    content=instructions,
                    content_type=ContentType.INSTRUCTION_STEPS,
                    confidence_score=inst_confidence,
                    validation_notes=[],
                    source_info={}
                ))
        else:
            errors.append("Missing instructions section")
        
        # Calculate overall quality metrics
        if components:
            quality_metrics['average_confidence'] = sum(c.confidence_score for c in components) / len(components)
            quality_metrics['component_count'] = len(components)
            quality_metrics['has_all_core_components'] = len(components) >= 3  # title, ingredients, instructions
        else:
            quality_metrics['average_confidence'] = 0.0
            quality_metrics['component_count'] = 0
            quality_metrics['has_all_core_components'] = False
        
        # Determine if recipe is valid
        is_valid = (len(errors) == 0 and 
                   quality_metrics['has_all_core_components'] and
                   quality_metrics['average_confidence'] >= 0.7)
        
        overall_confidence = quality_metrics['average_confidence'] if components else 0.0
        
        return RecipeValidationResult(
            is_valid_recipe=is_valid,
            confidence_score=overall_confidence,
            components=components,
            validation_errors=errors,
            validation_warnings=warnings,
            quality_metrics=quality_metrics
        )
    
    def generate_validation_report(self, validation_result: RecipeValidationResult) -> str:
        """Generate a human-readable validation report"""
        report = []
        report.append("🔍 SEMANTIC RECIPE VALIDATION REPORT")
        report.append("=" * 50)
        
        if validation_result.is_valid_recipe:
            report.append(f"✅ VALID RECIPE (Confidence: {validation_result.confidence_score:.2f})")
        else:
            report.append(f"❌ INVALID RECIPE (Confidence: {validation_result.confidence_score:.2f})")
        
        report.append(f"\n📊 QUALITY METRICS:")
        for metric, value in validation_result.quality_metrics.items():
            report.append(f"  {metric}: {value}")
        
        if validation_result.components:
            report.append(f"\n✅ VALIDATED COMPONENTS ({len(validation_result.components)}):")
            for component in validation_result.components:
                report.append(f"  • {component.content_type.value}: {component.confidence_score:.2f}")
        
        if validation_result.validation_errors:
            report.append(f"\n❌ VALIDATION ERRORS ({len(validation_result.validation_errors)}):")
            for error in validation_result.validation_errors:
                report.append(f"  • {error}")
        
        if validation_result.validation_warnings:
            report.append(f"\n⚠️ WARNINGS ({len(validation_result.validation_warnings)}):")
            for warning in validation_result.validation_warnings:
                report.append(f"  • {warning}")
        
        return '\n'.join(report)

def test_semantic_engine():
    """Test the semantic engine with known good and bad examples"""
    print("🧪 TESTING SEMANTIC RECIPE RECOGNITION ENGINE")
    print("=" * 60)
    
    engine = SemanticRecipeEngine(ValidationLevel.STRICT)
    
    # Test cases from our contaminated database
    test_cases = [
        # GOOD EXAMPLES (should pass)
        {
            'title': 'Chocolate Chip Cookies',
            'ingredients': '• 2 cups all-purpose flour\n• 1 cup butter\n• 1 cup chocolate chips',
            'instructions': '1. Preheat oven to 350°F.\n2. Mix flour and butter.\n3. Add chocolate chips and bake.'
        },
        {
            'title': 'Grilled Chicken Salad',
            'ingredients': '• 2 chicken breasts\n• 4 cups mixed greens\n• 2 tbsp olive oil',
            'instructions': '1. Grill chicken until cooked through.\n2. Slice chicken and serve over greens.'
        },
        
        # BAD EXAMPLES (should fail) - from actual database artifacts
        {
            'title': 'Start Cooking!',
            'ingredients': '• 2 tablespoons butter',
            'instructions': '1. Heat oil in pan.'
        },
        {
            'title': 'ATK Recipe from Page 14',
            'ingredients': '• See page reference',
            'instructions': '1. Follow instructions on page 14.'
        },
        {
            'title': 'Before You Begin',
            'ingredients': '• Read all instructions',
            'instructions': '1. Prepare your workspace.'
        },
        {
            'title': 'PREPARE INGREDIENTS',
            'ingredients': '• Various ingredients listed below',
            'instructions': '1. Get ingredients ready.'
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 TEST CASE {i}: '{test_case['title']}'")
        print("-" * 40)
        
        result = engine.validate_complete_recipe(test_case)
        
        if result.is_valid_recipe:
            print(f"✅ PASSED - Valid recipe (confidence: {result.confidence_score:.2f})")
        else:
            print(f"❌ FAILED - Invalid recipe (confidence: {result.confidence_score:.2f})")
            for error in result.validation_errors:
                print(f"  Error: {error}")
    
    print(f"\n✅ SEMANTIC ENGINE TESTING COMPLETE")

if __name__ == "__main__":
    test_semantic_engine()
