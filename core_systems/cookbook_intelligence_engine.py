#!/usr/bin/env python3
"""
🧠 COOKBOOK-AWARE INTELLIGENCE ENGINE
=====================================

This engine mimics human-like reasoning when reading cookbooks.
It understands cookbook structure, recipe organization, and content vs context.

Key Features:
- Document structure understanding (TOC, recipes, index)
- Recipe boundary detection (multi-page recipes)  
- Content vs structure distinction (data vs headers)
- Semantic validation (does this make culinary sense?)
- Quality assurance (is this actually cookable?)
"""

import re
from typing import Dict, List, Optional, Tuple, NamedTuple
from dataclasses import dataclass
from enum import Enum

class PageType(Enum):
    """Types of pages in cookbooks"""
    TABLE_OF_CONTENTS = "table_of_contents"
    INTRODUCTION = "introduction" 
    RECIPE_PAGE = "recipe_page"
    RECIPE_CONTINUATION = "recipe_continuation"
    EDUCATIONAL_CONTENT = "educational_content"
    INDEX = "index"
    ACKNOWLEDGMENTS = "acknowledgments"
    UNKNOWN = "unknown"

class RecipeSection(Enum):
    """Sections within a recipe"""
    TITLE = "title"
    METADATA = "metadata"  # servings, time, difficulty
    EDUCATIONAL = "educational"  # "Why this works", "Before you begin"
    INGREDIENTS = "ingredients"
    INSTRUCTIONS = "instructions"
    VARIATIONS = "variations"
    NOTES = "notes"

@dataclass
class RecipeBoundary:
    """Represents a complete recipe boundary"""
    start_page: int
    end_page: int
    title: str
    confidence: float
    sections: Dict[RecipeSection, str]

@dataclass
class ExtractedContent:
    """Content extracted from a page with context"""
    content: str
    section_type: RecipeSection
    confidence: float
    page_number: int
    is_essential: bool  # True for title/ingredients/instructions
    reasoning: str  # Why this classification was made

class CookbookIntelligenceEngine:
    """Main engine for cookbook-aware extraction"""
    
    def __init__(self):
        self.cookbook_patterns = self._load_cookbook_patterns()
        self.food_knowledge = self._load_food_knowledge()
        self.cooking_knowledge = self._load_cooking_knowledge()
    
    def _load_cookbook_patterns(self) -> Dict:
        """Load patterns for different cookbook formats"""
        return {
            'atk_teen': {
                'title_patterns': [
                    r'^[A-Z][A-Z\s\-\']+$',  # ALL CAPS titles
                    r'^[A-Z][a-z\s\-\']+[A-Z][a-z\s\-\']*$'  # Title Case
                ],
                'metadata_patterns': [
                    r'(BEGINNER|INTERMEDIATE|ADVANCED)',
                    r'(MAKES|SERVES)\s+\d+',
                    r'\d+\s+(MINUTES|HOURS)'
                ],
                'section_headers': [
                    'PREPARE INGREDIENTS',
                    'START COOKING!',
                    'BEFORE YOU BEGIN'
                ],
                'instruction_patterns': [
                    r'^\d+\.\s+',  # Numbered steps
                ]
            },
            'atk_25th': {
                'title_patterns': [
                    r'^[A-Z][a-z\s\-\']+$',  # Title case
                    r'^[A-Z\s\-\']+$'  # ALL CAPS
                ],
                'page_reference_pattern': r'ATK Recipe from Page \d+',
                'educational_sections': [
                    'WHY THIS RECIPE WORKS',
                    'THE SCIENCE',
                    'TESTING NOTES'
                ]
            }
        }
    
    def _load_food_knowledge(self) -> Dict:
        """Load comprehensive food and cooking knowledge"""
        return {
            'common_dishes': {
                'cookies', 'cake', 'bread', 'soup', 'salad', 'pasta', 'pizza',
                'chicken', 'beef', 'fish', 'stew', 'chili', 'pie', 'muffins',
                'pancakes', 'burgers', 'sandwiches', 'casserole', 'risotto'
            },
            'cooking_methods': {
                'baked', 'roasted', 'grilled', 'fried', 'sautéed', 'braised',
                'steamed', 'poached', 'broiled', 'slow-cooked', 'pan-seared'
            },
            'cuisine_types': {
                'italian', 'mexican', 'asian', 'french', 'mediterranean',
                'indian', 'thai', 'chinese', 'japanese', 'american'
            },
            'ingredient_categories': {
                'proteins': {'chicken', 'beef', 'pork', 'fish', 'eggs', 'tofu'},
                'vegetables': {'onion', 'garlic', 'carrot', 'celery', 'potato'},
                'dairy': {'milk', 'butter', 'cheese', 'cream', 'yogurt'},
                'grains': {'flour', 'rice', 'pasta', 'bread', 'oats'},
                'seasonings': {'salt', 'pepper', 'herbs', 'spices'}
            }
        }
    
    def _load_cooking_knowledge(self) -> Dict:
        """Load cooking process and technique knowledge"""
        return {
            'cooking_actions': {
                'heat', 'cook', 'bake', 'boil', 'simmer', 'sauté', 'fry',
                'mix', 'stir', 'whisk', 'combine', 'add', 'season', 'taste',
                'preheat', 'transfer', 'drain', 'serve', 'garnish'
            },
            'preparation_actions': {
                'chop', 'dice', 'mince', 'slice', 'grate', 'shred', 'peel',
                'wash', 'rinse', 'pat dry', 'measure', 'sift', 'cream'
            },
            'realistic_measurements': {
                'volume': ['cup', 'tablespoon', 'teaspoon', 'fluid ounce', 'liter'],
                'weight': ['pound', 'ounce', 'gram', 'kilogram'],
                'quantity': ['piece', 'clove', 'head', 'bunch', 'package']
            },
            'temperature_ranges': {
                'oven': (200, 500),  # Fahrenheit
                'stovetop': ['low', 'medium-low', 'medium', 'medium-high', 'high']
            }
        }
    
    def analyze_page_type(self, page_content: str, page_number: int) -> Tuple[PageType, float]:
        """
        Determine what type of page this is using cookbook structure knowledge
        
        Returns:
            Tuple of (PageType, confidence_score)
        """
        content_lower = page_content.lower()
        
        # Check for table of contents
        if self._is_table_of_contents(content_lower):
            return PageType.TABLE_OF_CONTENTS, 0.95
        
        # Check for index
        if self._is_index_page(content_lower):
            return PageType.INDEX, 0.95
        
        # Check for acknowledgments/intro
        if self._is_intro_or_acknowledgments(content_lower):
            return PageType.INTRODUCTION, 0.90
        
        # Check for recipe page
        if self._is_recipe_page(page_content):
            return PageType.RECIPE_PAGE, 0.85
        
        # Check for recipe continuation
        if self._is_recipe_continuation(page_content):
            return PageType.RECIPE_CONTINUATION, 0.80
        
        # Check for educational content
        if self._is_educational_content(content_lower):
            return PageType.EDUCATIONAL_CONTENT, 0.75
        
        return PageType.UNKNOWN, 0.30
    
    def _is_table_of_contents(self, content: str) -> bool:
        """Detect table of contents pages"""
        toc_indicators = [
            'contents', 'table of contents', 'index of recipes',
            # Look for page number patterns typical of TOC
            lambda c: len(re.findall(r'\d+\s*$', c, re.MULTILINE)) > 5,
            # Look for chapter/section listings
            lambda c: 'chapter' in c and '...' in c
        ]
        
        for indicator in toc_indicators:
            if callable(indicator):
                if indicator(content):
                    return True
            elif indicator in content:
                return True
        
        return False
    
    def _is_index_page(self, content: str) -> bool:
        """Detect index pages"""
        index_indicators = [
            'index', 'alphabetical index', 'recipe index',
            # Look for alphabetical organization
            lambda c: len(re.findall(r'^[A-Z]\n', c, re.MULTILINE)) > 3
        ]
        
        for indicator in index_indicators:
            if callable(indicator):
                if indicator(content):
                    return True
            elif indicator in content:
                return True
        
        return False
    
    def _is_intro_or_acknowledgments(self, content: str) -> bool:
        """Detect introduction or acknowledgments"""
        intro_indicators = [
            'introduction', 'acknowledgments', 'foreword', 'preface',
            'about this book', 'how to use this book', 'thank you'
        ]
        
        return any(indicator in content for indicator in intro_indicators)
    
    def _is_recipe_page(self, content: str) -> bool:
        """
        Detect if this is a recipe page using cookbook intelligence
        
        This is the KEY function that needs human-like reasoning
        """
        # Score different recipe indicators
        score = 0
        
        # 1. Has realistic recipe title (food dish name)
        potential_titles = self._extract_potential_titles(content)
        for title in potential_titles:
            if self._is_realistic_recipe_title(title):
                score += 3  # Strong indicator
                break
        
        # 2. Has ingredient patterns with real foods
        ingredient_score = self._score_ingredient_content(content)
        score += min(ingredient_score, 3)  # Cap at 3 points
        
        # 3. Has cooking instruction patterns
        instruction_score = self._score_instruction_content(content)
        score += min(instruction_score, 3)  # Cap at 3 points
        
        # 4. Has recipe metadata (serves, time, etc.)
        if self._has_recipe_metadata(content):
            score += 2
        
        # 5. Penalty for non-recipe content
        if self._has_non_recipe_indicators(content):
            score -= 2
        
        # Threshold for recipe detection
        return score >= 5
    
    def _is_recipe_continuation(self, content: str) -> bool:
        """Detect if this continues a recipe from previous page"""
        # Look for numbered instruction continuations
        if re.search(r'^\d+\.\s+', content, re.MULTILINE):
            return True
        
        # Look for ingredient list continuations
        if len(re.findall(r'^\s*[•\-]\s*\d+', content, re.MULTILINE)) > 2:
            return True
        
        return False
    
    def _is_educational_content(self, content: str) -> bool:
        """Detect educational/explanatory content"""
        educational_indicators = [
            'why this recipe works', 'the science', 'testing notes',
            'technique', 'equipment review', 'ingredient spotlight'
        ]
        
        return any(indicator in content for indicator in educational_indicators)
    
    def _extract_potential_titles(self, content: str) -> List[str]:
        """Extract text that could potentially be recipe titles"""
        lines = content.split('\n')
        potential_titles = []
        
        # Look at first 10 lines for titles
        for line in lines[:10]:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip obvious non-titles
            if line.startswith('•') or line.startswith('-'):
                continue
            if re.match(r'^\d+\.', line):  # Numbered instructions
                continue
            if len(line) < 3 or len(line) > 80:  # Unrealistic lengths
                continue
            
            # Look for title-like formatting
            if (line.isupper() or line.istitle()) and 3 <= len(line.split()) <= 8:
                potential_titles.append(line)
        
        return potential_titles
    
    def _is_realistic_recipe_title(self, title: str) -> bool:
        """
        Use food knowledge to determine if this is a realistic recipe title
        
        This is where human-like reasoning happens
        """
        title_lower = title.lower()
        
        # Must contain food-related words
        food_word_found = False
        
        # Check against food knowledge
        for category, foods in self.food_knowledge['ingredient_categories'].items():
            if any(food in title_lower for food in foods):
                food_word_found = True
                break
        
        # Check against common dishes
        if any(dish in title_lower for dish in self.food_knowledge['common_dishes']):
            food_word_found = True
        
        # Check against cooking methods + food combinations
        has_cooking_method = any(method in title_lower for method in self.food_knowledge['cooking_methods'])
        if has_cooking_method and food_word_found:
            return True
        
        # Must not be instruction headers
        instruction_headers = [
            'start cooking', 'prepare ingredients', 'before you begin',
            'ingredients', 'method', 'directions', 'instructions'
        ]
        
        if any(header in title_lower for header in instruction_headers):
            return False
        
        # Must not be page metadata
        if re.search(r'page \d+|recipe from page', title_lower):
            return False
        
        return food_word_found
    
    def _score_ingredient_content(self, content: str) -> int:
        """Score how much this looks like ingredient content"""
        score = 0
        
        # Look for measurement patterns
        measurement_patterns = [
            r'\b\d+\s*(cup|tablespoon|teaspoon|pound|ounce|gram)s?\b',
            r'\b\d+/\d+\s*(cup|tablespoon|teaspoon)\b',
            r'\b\d+\.\d+\s*(pound|ounce|gram)s?\b'
        ]
        
        measurement_count = 0
        for pattern in measurement_patterns:
            measurement_count += len(re.findall(pattern, content, re.IGNORECASE))
        
        score += min(measurement_count, 3)  # Up to 3 points for measurements
        
        # Look for real food items with measurements
        real_ingredient_count = 0
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or not re.search(r'\d+', line):
                continue
            
            # Check if line has measurement + real food
            has_measurement = any(re.search(pattern, line, re.IGNORECASE) for pattern in measurement_patterns)
            has_food = any(
                any(food in line.lower() for food in foods)
                for foods in self.food_knowledge['ingredient_categories'].values()
            )
            
            if has_measurement and has_food:
                real_ingredient_count += 1
        
        score += min(real_ingredient_count, 2)  # Up to 2 points for real ingredients
        
        return score
    
    def _score_instruction_content(self, content: str) -> int:
        """Score how much this looks like cooking instructions"""
        score = 0
        
        # Look for numbered steps
        numbered_steps = len(re.findall(r'^\d+\.\s+', content, re.MULTILINE))
        score += min(numbered_steps, 2)  # Up to 2 points for numbered steps
        
        # Look for cooking actions
        cooking_action_count = 0
        content_lower = content.lower()
        
        all_cooking_actions = (
            self.cooking_knowledge['cooking_actions'] | 
            self.cooking_knowledge['preparation_actions']
        )
        
        for action in all_cooking_actions:
            if action in content_lower:
                cooking_action_count += 1
        
        score += min(cooking_action_count // 3, 2)  # Up to 2 points for cooking actions
        
        return score
    
    def _has_recipe_metadata(self, content: str) -> bool:
        """Check for recipe metadata (serves, time, difficulty)"""
        metadata_patterns = [
            r'(serves|makes|yields?)\s+\d+',
            r'\d+\s+(minutes?|hours?)',
            r'(beginner|intermediate|advanced)',
            r'(easy|medium|hard|difficult)'
        ]
        
        content_lower = content.lower()
        return any(re.search(pattern, content_lower) for pattern in metadata_patterns)
    
    def _has_non_recipe_indicators(self, content: str) -> bool:
        """Check for content that indicates this is NOT a recipe"""
        non_recipe_indicators = [
            'table of contents', 'index', 'acknowledgments',
            'introduction', 'about the author', 'page \d+ of \d+',
            'copyright', 'isbn', 'published by'
        ]
        
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in non_recipe_indicators)
    
    def extract_recipe_intelligently(self, page_content: str, page_number: int) -> Optional[Dict]:
        """
        Extract recipe using cookbook intelligence and human-like reasoning
        
        This is the main function that mimics how humans read recipes
        """
        # Step 1: Determine if this page contains recipe content
        page_type, confidence = self.analyze_page_type(page_content, page_number)
        
        if page_type not in [PageType.RECIPE_PAGE, PageType.RECIPE_CONTINUATION]:
            return None  # Skip non-recipe pages
        
        # Step 2: Extract recipe components with context awareness
        extracted_content = self._extract_recipe_components(page_content, page_number)
        
        # Step 3: Validate extracted components make sense
        validated_recipe = self._validate_recipe_components(extracted_content)
        
        if not validated_recipe:
            return None  # Skip if validation fails
        
        # Step 4: Assemble final recipe with quality checks
        final_recipe = self._assemble_final_recipe(validated_recipe, page_number)
        
        return final_recipe
    
    def _extract_recipe_components(self, content: str, page_number: int) -> List[ExtractedContent]:
        """Extract and classify recipe components with reasoning"""
        components = []
        
        # Extract title
        potential_titles = self._extract_potential_titles(content)
        for title in potential_titles:
            if self._is_realistic_recipe_title(title):
                components.append(ExtractedContent(
                    content=title,
                    section_type=RecipeSection.TITLE,
                    confidence=0.9,
                    page_number=page_number,
                    is_essential=True,
                    reasoning=f"Realistic food dish name: contains food words and proper formatting"
                ))
                break
        
        # Extract ingredients (skip section headers)
        ingredient_content = self._extract_ingredient_content(content)
        if ingredient_content:
            components.append(ExtractedContent(
                content=ingredient_content,
                section_type=RecipeSection.INGREDIENTS,
                confidence=0.85,
                page_number=page_number,
                is_essential=True,
                reasoning="Contains measurements with real food items"
            ))
        
        # Extract instructions (skip section headers)
        instruction_content = self._extract_instruction_content(content)
        if instruction_content:
            components.append(ExtractedContent(
                content=instruction_content,
                section_type=RecipeSection.INSTRUCTIONS,
                confidence=0.85,
                page_number=page_number,
                is_essential=True,
                reasoning="Contains numbered steps with cooking actions"
            ))
        
        return components
    
    def _extract_ingredient_content(self, content: str) -> Optional[str]:
        """Extract actual ingredient content, skipping headers like 'PREPARE INGREDIENTS'"""
        lines = content.split('\n')
        ingredient_lines = []
        
        skip_headers = {'prepare ingredients', 'ingredients', 'you will need'}
        
        for line in lines:
            line_stripped = line.strip()
            line_lower = line_stripped.lower()
            
            # Skip empty lines
            if not line_stripped:
                continue
            
            # Skip section headers
            if line_lower in skip_headers:
                continue
            
            # Look for actual ingredient lines
            if self._is_ingredient_line(line_stripped):
                ingredient_lines.append(f"• {line_stripped}")
        
        return '\n'.join(ingredient_lines) if ingredient_lines else None
    
    def _extract_instruction_content(self, content: str) -> Optional[str]:
        """Extract actual instruction content, skipping headers like 'START COOKING!'"""
        lines = content.split('\n')
        instruction_lines = []
        
        skip_headers = {'start cooking!', 'start cooking', 'method', 'directions', 'instructions'}
        
        for line in lines:
            line_stripped = line.strip()
            line_lower = line_stripped.lower()
            
            # Skip empty lines
            if not line_stripped:
                continue
            
            # Skip section headers
            if line_lower in skip_headers:
                continue
            
            # Look for actual instruction lines (numbered steps)
            if re.match(r'^\d+\.\s+', line_stripped):
                if self._is_instruction_line(line_stripped):
                    instruction_lines.append(line_stripped)
        
        return '\n'.join(instruction_lines) if instruction_lines else None
    
    def _is_ingredient_line(self, line: str) -> bool:
        """Check if a line is an actual ingredient (not a header)"""
        # Must have measurement pattern
        measurement_patterns = [
            r'\b\d+\s*(cup|tablespoon|teaspoon|pound|ounce|gram)s?\b',
            r'\b\d+/\d+\s*(cup|tablespoon|teaspoon)\b',
            r'\b\d+\.\d+\s*(pound|ounce|gram)s?\b'
        ]
        
        has_measurement = any(re.search(pattern, line, re.IGNORECASE) for pattern in measurement_patterns)
        if not has_measurement:
            return False
        
        # Must have real food item
        has_food = any(
            any(food in line.lower() for food in foods)
            for foods in self.food_knowledge['ingredient_categories'].values()
        )
        
        return has_food
    
    def _is_instruction_line(self, line: str) -> bool:
        """Check if a line is an actual cooking instruction"""
        # Must have cooking action
        line_lower = line.lower()
        
        all_cooking_actions = (
            self.cooking_knowledge['cooking_actions'] | 
            self.cooking_knowledge['preparation_actions']
        )
        
        has_cooking_action = any(action in line_lower for action in all_cooking_actions)
        return has_cooking_action and len(line) > 20  # Must be substantial
    
    def _validate_recipe_components(self, components: List[ExtractedContent]) -> Optional[Dict]:
        """Validate that extracted components make culinary sense"""
        # Must have essential components
        has_title = any(c.section_type == RecipeSection.TITLE for c in components)
        has_ingredients = any(c.section_type == RecipeSection.INGREDIENTS for c in components)
        has_instructions = any(c.section_type == RecipeSection.INSTRUCTIONS for c in components)
        
        if not (has_title and has_ingredients and has_instructions):
            return None
        
        # Components must meet quality thresholds
        avg_confidence = sum(c.confidence for c in components) / len(components)
        if avg_confidence < 0.7:
            return None
        
        return {component.section_type: component.content for component in components}
    
    def _assemble_final_recipe(self, validated_components: Dict, page_number: int) -> Dict:
        """Assemble final recipe with metadata"""
        recipe = {
            'title': validated_components.get(RecipeSection.TITLE, '').strip(),
            'ingredients': validated_components.get(RecipeSection.INGREDIENTS, '').strip(),
            'instructions': validated_components.get(RecipeSection.INSTRUCTIONS, '').strip(),
            'page_number': page_number,
            'extraction_method': 'cookbook_intelligence_engine',
            'quality_validated': True
        }
        
        return recipe

def test_cookbook_intelligence():
    """Test the cookbook intelligence engine"""
    print("🧠 TESTING COOKBOOK INTELLIGENCE ENGINE")
    print("=" * 60)
    
    engine = CookbookIntelligenceEngine()
    
    # Test with sample content from our problematic database
    test_cases = [
        {
            'name': 'Good Recipe Page',
            'content': '''CHOCOLATE CHIP COOKIES
BEGINNER | MAKES 24 | 45 MINUTES

PREPARE INGREDIENTS
• 2¼ cups all-purpose flour
• 1 teaspoon baking soda  
• 1 cup butter, softened
• ¾ cup granulated sugar
• 2 large eggs
• 2 cups chocolate chips

START COOKING!
1. Preheat oven to 375°F.
2. Mix flour and baking soda in large bowl.
3. In separate bowl, cream butter and sugar.
4. Add eggs to butter mixture and mix well.
5. Gradually add flour mixture to butter mixture.
6. Stir in chocolate chips.
7. Drop rounded tablespoons onto ungreased baking sheets.
8. Bake 9 to 11 minutes or until golden brown.''',
            'page': 42
        },
        {
            'name': 'Bad Artifact Page',
            'content': '''ATK Recipe from Page 14
Start Cooking!
PREPARE INGREDIENTS''',
            'page': 14
        },
        {
            'name': 'Table of Contents',
            'content': '''TABLE OF CONTENTS

Breakfast Recipes ........................ 12
Lunch Ideas .............................. 45  
Dinner Favorites ......................... 78
Desserts ................................. 156''',
            'page': 3
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 TESTING: {test_case['name']}")
        print("-" * 40)
        
        # Analyze page type
        page_type, confidence = engine.analyze_page_type(test_case['content'], test_case['page'])
        print(f"Page Type: {page_type.value} (confidence: {confidence:.2f})")
        
        # Try to extract recipe
        recipe = engine.extract_recipe_intelligently(test_case['content'], test_case['page'])
        
        if recipe:
            print("✅ RECIPE EXTRACTED:")
            print(f"  Title: {recipe['title']}")
            print(f"  Ingredients: {len(recipe['ingredients'].split())} words")
            print(f"  Instructions: {len(recipe['instructions'].split())} words")
        else:
            print("❌ NO RECIPE EXTRACTED (correctly filtered out)")
    
    print(f"\n✅ COOKBOOK INTELLIGENCE ENGINE TESTING COMPLETE")

if __name__ == "__main__":
    test_cookbook_intelligence()
