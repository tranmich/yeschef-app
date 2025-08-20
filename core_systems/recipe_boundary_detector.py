#!/usr/bin/env python3
"""
🎯 RECIPE BOUNDARY DETECTION & CONTENT FILTERING SYSTEM
=======================================================

This system identifies complete recipe blocks and filters out non-essential
contextual content within those blocks. It understands the structure:

RECIPE BLOCK = Title + Ingredients + Instructions
CONTEXTUAL CONTENT = "Before you begin", educational text, etc.

Key Principle: If we can identify a complete recipe block, we extract only
the essential components and discard the contextual fluff.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from core_systems.semantic_recipe_engine import SemanticRecipeEngine, ContentType, ValidationLevel

class RecipeBlockType(Enum):
    """Types of content blocks within recipes"""
    ESSENTIAL = "essential"      # Title, ingredients, instructions
    CONTEXTUAL = "contextual"    # "Before you begin", tips, etc.
    METADATA = "metadata"        # Servings, time, difficulty
    EDUCATIONAL = "educational"  # "Why this works", science explanations
    ARTIFACTS = "artifacts"      # Extraction errors, page refs

@dataclass
class RecipeBlock:
    """A complete recipe with filtered content"""
    title: str
    ingredients: str
    instructions: str
    metadata: Dict[str, str]  # servings, time, difficulty, etc.
    educational_content: Optional[str] = None
    page_numbers: List[int] = None
    confidence_score: float = 0.0
    quality_metrics: Dict[str, float] = None

@dataclass
class ContentBlock:
    """A piece of content with classification"""
    content: str
    block_type: RecipeBlockType
    content_type: ContentType
    confidence: float
    source_info: Dict[str, str]

class RecipeBoundaryDetector:
    """Detects complete recipe boundaries and filters content"""
    
    def __init__(self):
        self.semantic_engine = SemanticRecipeEngine(ValidationLevel.STRICT)
        self.contextual_patterns = self._load_contextual_patterns()
        self.recipe_structure_patterns = self._load_recipe_structure_patterns()
    
    def _load_contextual_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for contextual content that should be filtered out"""
        return {
            'educational_headers': [
                r'^(before you begin|why this recipe works|the science|testing notes)$',
                r'^(chef\'s note|cooking tip|technique tip|equipment note)$',
                r'^(what you need to know|pro tip|kitchen wisdom)$'
            ],
            'instructional_fluff': [
                r'^(start cooking!?|let\'s get started|ready to cook)$',
                r'^(step by step|follow these steps|here\'s how)$',
                r'^(preparation|getting ready|mise en place)$'
            ],
            'contextual_content': [
                r'see photo|see illustration|turn to page \d+',
                r'for more information|additional details|complete guide',
                r'this technique|this method|this approach'
            ],
            'recipe_metadata_headers': [
                r'^(difficulty|skill level|prep time|cook time|total time)$',
                r'^(serves|makes|yields|portions)$',
                r'^(dietary info|nutritional notes|allergen info)$'
            ]
        }
    
    def _load_recipe_structure_patterns(self) -> Dict[str, List[str]]:
        """Load patterns that indicate recipe structure boundaries"""
        return {
            'recipe_start_indicators': [
                # ATK Teen format
                r'(BEGINNER|INTERMEDIATE|ADVANCED)',
                r'(VEGETARIAN|VEGAN|GLUTEN.?FREE)',
                r'(SERVES|MAKES)\s+\d+',
                r'\d+\s+(MINUTES?|HOURS?)',
                
                # ATK 25th format  
                r'^[A-Z][A-Z\s\-&]+[A-Z]$',  # All caps titles
                r'WHY THIS RECIPE WORKS',
                
                # General patterns
                r'^[A-Z][a-z\s]+(Soup|Salad|Chicken|Beef|Cake|Bread|Cookies?)$'
            ],
            'ingredient_section_start': [
                r'^(INGREDIENTS|PREPARE INGREDIENTS|FOR THE [A-Z]+)$',
                r'^\d+\s*(cup|tablespoon|teaspoon|pound|ounce)',
                r'^•\s*\d+\s*(cup|tablespoon|teaspoon|pound|ounce)'
            ],
            'instruction_section_start': [
                r'^(INSTRUCTIONS|METHOD|DIRECTIONS|START COOKING!)$',
                r'^\d+\.\s+[A-Z]',  # Numbered steps starting with capital
            ],
            'recipe_end_indicators': [
                r'^(SERVES|MAKES)\s+\d+',  # Recipe yield at end
                r'^\d+\s+(minutes?|hours?)\s*$',  # Timing at end
                r'^(BEGINNER|INTERMEDIATE|ADVANCED)\s*$'  # Next recipe difficulty
            ]
        }
    
    def detect_recipe_blocks(self, page_texts: List[str], page_numbers: List[int]) -> List[RecipeBlock]:
        """
        Detect complete recipe blocks from multiple pages of text
        
        Args:
            page_texts: List of text content from pages
            page_numbers: Corresponding page numbers
            
        Returns:
            List of detected RecipeBlock objects
        """
        print(f"🔍 DETECTING RECIPE BLOCKS FROM {len(page_texts)} PAGES")
        print("=" * 60)
        
        # Combine all text for analysis
        combined_content = []
        for i, (text, page_num) in enumerate(zip(page_texts, page_numbers)):
            combined_content.append({
                'text': text,
                'page_number': page_num,
                'page_index': i
            })
        
        # Find recipe boundaries
        recipe_boundaries = self._find_recipe_boundaries(combined_content)
        
        # Extract and filter recipe blocks
        recipe_blocks = []
        for boundary in recipe_boundaries:
            recipe_block = self._extract_recipe_block(boundary, combined_content)
            if recipe_block:
                recipe_blocks.append(recipe_block)
        
        print(f"✅ DETECTED {len(recipe_blocks)} RECIPE BLOCKS")
        return recipe_blocks
    
    def _find_recipe_boundaries(self, combined_content: List[Dict]) -> List[Dict]:
        """Find the start and end boundaries of complete recipes"""
        boundaries = []
        current_boundary = None
        
        # First pass: identify potential recipe titles and strong start indicators
        potential_starts = []
        
        for page_info in combined_content:
            text = page_info['text']
            page_num = page_info['page_number']
            
            # Look for recipe titles and strong start indicators
            lines = text.split('\n')
            
            for line_idx, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                # Check if this looks like a recipe title
                content_type, confidence = self.semantic_engine.classify_content_type(line)
                
                if content_type == ContentType.RECIPE_TITLE and confidence > 0.7:
                    potential_starts.append({
                        'page': page_num,
                        'line_idx': line_idx,
                        'title': line,
                        'confidence': confidence
                    })
                    
                # Also check for strong recipe start patterns
                elif self._is_strong_recipe_start(line):
                    potential_starts.append({
                        'page': page_num,
                        'line_idx': line_idx,
                        'title': line,
                        'confidence': 0.8
                    })
        
        # Second pass: create boundaries between recipe starts
        for i, start in enumerate(potential_starts):
            boundary = {
                'start_page': start['page'],
                'start_line': start['line_idx'],
                'potential_title': start['title'],
                'confidence': start['confidence']
            }
            
            # Set end boundary to the next recipe start or end of content
            if i + 1 < len(potential_starts):
                next_start = potential_starts[i + 1]
                boundary['end_page'] = next_start['page']
                boundary['end_line'] = next_start['line_idx'] - 1
            else:
                # Last recipe goes to end of content
                boundary['end_page'] = combined_content[-1]['page_number']
                boundary['end_line'] = -1
            
            boundaries.append(boundary)
        
        print(f"🎯 Found {len(boundaries)} potential recipe boundaries")
        for i, boundary in enumerate(boundaries):
            print(f"   {i+1}. '{boundary['potential_title']}' (pages {boundary['start_page']}-{boundary['end_page']})")
        
        return boundaries
    
    def _is_strong_recipe_start(self, line: str) -> bool:
        """Check if line is a strong indicator of recipe start"""
        line_clean = line.strip()
        
        # All caps titles that look like food
        if (line_clean.isupper() and 
            len(line_clean.split()) >= 2 and 
            len(line_clean) < 60 and
            self.semantic_engine._contains_food_words(line_clean)):
            return True
        
        # Difficulty levels (ATK Teen format)
        if re.match(r'^(BEGINNER|INTERMEDIATE|ADVANCED)$', line_clean):
            return True
        
        # Recipe yield indicators  
        if re.match(r'^(SERVES|MAKES|YIELDS?)\s+\d+', line_clean, re.IGNORECASE):
            return True
        
        return False
    
    def _is_recipe_start_indicator(self, line: str) -> bool:
        """Check if line indicates the start of a recipe"""
        line_clean = line.strip()
        
        # Check against recipe start patterns
        for pattern in self.recipe_structure_patterns['recipe_start_indicators']:
            if re.search(pattern, line_clean, re.IGNORECASE):
                return True
        
        # Use semantic engine for additional validation
        content_type, confidence = self.semantic_engine.classify_content_type(line_clean)
        
        # Recipe titles are strong start indicators
        if content_type == ContentType.RECIPE_TITLE and confidence > 0.7:
            return True
        
        # Recipe metadata can also indicate start
        if content_type == ContentType.RECIPE_METADATA and confidence > 0.8:
            return True
        
        return False
    
    def _is_recipe_end_indicator(self, line: str) -> bool:
        """Check if line indicates the end of a recipe"""
        line_clean = line.strip()
        
        # Check against recipe end patterns
        for pattern in self.recipe_structure_patterns['recipe_end_indicators']:
            if re.search(pattern, line_clean, re.IGNORECASE):
                return True
        
        # Next recipe title indicates end of current recipe
        content_type, confidence = self.semantic_engine.classify_content_type(line_clean)
        if content_type == ContentType.RECIPE_TITLE and confidence > 0.8:
            return True
        
        return False
    
    def _extract_recipe_block(self, boundary: Dict, combined_content: List[Dict]) -> Optional[RecipeBlock]:
        """Extract and filter a complete recipe block"""
        
        # Extract all content within the boundary
        recipe_content = self._extract_content_within_boundary(boundary, combined_content)
        
        if not recipe_content:
            return None
        
        # Classify and filter content blocks
        content_blocks = self._classify_content_blocks(recipe_content)
        
        # Extract essential components
        title = self._extract_essential_title(content_blocks)
        ingredients = self._extract_essential_ingredients(content_blocks)
        instructions = self._extract_essential_instructions(content_blocks)
        metadata = self._extract_metadata(content_blocks)
        educational = self._extract_educational_content(content_blocks)
        
        # Validate that we have a complete recipe
        if not (title and ingredients and instructions):
            print(f"⚠️  Incomplete recipe block: title={bool(title)}, ingredients={bool(ingredients)}, instructions={bool(instructions)}")
            return None
        
        # Create recipe block
        recipe_block = RecipeBlock(
            title=title,
            ingredients=ingredients,
            instructions=instructions,
            metadata=metadata,
            educational_content=educational,
            page_numbers=[boundary['start_page'], boundary['end_page']],
            confidence_score=0.0,
            quality_metrics={}
        )
        
        # Validate using semantic engine
        recipe_data = {
            'title': title,
            'ingredients': ingredients,
            'instructions': instructions,
            **metadata
        }
        
        validation_result = self.semantic_engine.validate_complete_recipe(recipe_data)
        recipe_block.confidence_score = validation_result.confidence_score
        recipe_block.quality_metrics = validation_result.quality_metrics
        
        if validation_result.is_valid_recipe:
            print(f"✅ VALID RECIPE: '{title}' (confidence: {validation_result.confidence_score:.2f})")
            return recipe_block
        else:
            print(f"❌ INVALID RECIPE: '{title}' (confidence: {validation_result.confidence_score:.2f})")
            for error in validation_result.validation_errors:
                print(f"   Error: {error}")
            return None
    
    def _extract_content_within_boundary(self, boundary: Dict, combined_content: List[Dict]) -> str:
        """Extract all text content within a recipe boundary"""
        content_parts = []
        
        start_page = boundary['start_page']
        end_page = boundary['end_page']
        
        for page_info in combined_content:
            page_num = page_info['page_number']
            
            # Include pages within boundary
            if start_page <= page_num <= end_page:
                content_parts.append(page_info['text'])
        
        return '\n'.join(content_parts)
    
    def _classify_content_blocks(self, recipe_content: str) -> List[ContentBlock]:
        """Classify content within a recipe into blocks"""
        content_blocks = []
        lines = recipe_content.split('\n')
        
        # Group lines by content type
        title_lines = []
        ingredient_lines = []
        instruction_lines = []
        metadata_lines = []
        contextual_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Classify this line
            content_type, confidence = self.semantic_engine.classify_content_type(line)
            block_type = self._determine_block_type(line, content_type)
            
            # Group by type
            if content_type == ContentType.RECIPE_TITLE:
                title_lines.append(line)
            elif self._looks_like_ingredient(line):
                ingredient_lines.append(line)
            elif self._looks_like_instruction(line):
                instruction_lines.append(line)
            elif content_type == ContentType.RECIPE_METADATA:
                metadata_lines.append(line)
            else:
                contextual_lines.append(line)
        
        # Create content blocks
        if title_lines:
            content_blocks.append(ContentBlock(
                content='\n'.join(title_lines),
                block_type=RecipeBlockType.ESSENTIAL,
                content_type=ContentType.RECIPE_TITLE,
                confidence=0.8,
                source_info={}
            ))
        
        if ingredient_lines:
            content_blocks.append(ContentBlock(
                content='\n'.join(ingredient_lines),
                block_type=RecipeBlockType.ESSENTIAL,
                content_type=ContentType.INGREDIENT_LIST,
                confidence=0.8,
                source_info={}
            ))
        
        if instruction_lines:
            content_blocks.append(ContentBlock(
                content='\n'.join(instruction_lines),
                block_type=RecipeBlockType.ESSENTIAL,
                content_type=ContentType.INSTRUCTION_STEPS,
                confidence=0.8,
                source_info={}
            ))
        
        if metadata_lines:
            content_blocks.append(ContentBlock(
                content='\n'.join(metadata_lines),
                block_type=RecipeBlockType.METADATA,
                content_type=ContentType.RECIPE_METADATA,
                confidence=0.7,
                source_info={}
            ))
        
        return content_blocks
    
    def _looks_like_ingredient(self, line: str) -> bool:
        """Check if line looks like an ingredient"""
        # Has measurements
        if re.search(r'\d+\s*(cup|tablespoon|teaspoon|pound|ounce|tbsp|tsp|lb|oz)', line, re.IGNORECASE):
            return True
        
        # Starts with bullet point and has food words
        if line.startswith('•') and self.semantic_engine._contains_food_words(line):
            return True
        
        return False
    
    def _looks_like_instruction(self, line: str) -> bool:
        """Check if line looks like an instruction step"""
        # Starts with number and period
        if re.match(r'^\d+\.', line):
            return True
        
        # Contains cooking verbs
        if self.semantic_engine._contains_cooking_words(line):
            return True
        
        return False
    
    def _determine_block_type(self, line: str, content_type: ContentType) -> RecipeBlockType:
        """Determine if content is essential, contextual, or artifact"""
        
        line_lower = line.lower().strip()
        
        # Check for artifacts first
        if content_type in [ContentType.EXTRACTION_ARTIFACT, ContentType.PAGE_METADATA]:
            return RecipeBlockType.ARTIFACTS
        
        # Check for contextual content
        for pattern_category in self.contextual_patterns.values():
            for pattern in pattern_category:
                if re.search(pattern, line_lower):
                    return RecipeBlockType.CONTEXTUAL
        
        # Check for educational content
        if content_type == ContentType.EDUCATIONAL_CONTENT:
            return RecipeBlockType.EDUCATIONAL
        
        # Check for metadata
        if content_type == ContentType.RECIPE_METADATA:
            return RecipeBlockType.METADATA
        
        # Essential content
        if content_type in [ContentType.RECIPE_TITLE, ContentType.INGREDIENT_LIST, ContentType.INSTRUCTION_STEPS]:
            return RecipeBlockType.ESSENTIAL
        
        # Default to contextual
        return RecipeBlockType.CONTEXTUAL
    
    def _extract_essential_title(self, content_blocks: List[ContentBlock]) -> Optional[str]:
        """Extract the essential recipe title"""
        for block in content_blocks:
            if (block.block_type == RecipeBlockType.ESSENTIAL and 
                block.content_type == ContentType.RECIPE_TITLE and
                block.confidence > 0.7):
                return block.content.split('\n')[0].strip()  # First line only
        return None
    
    def _extract_essential_ingredients(self, content_blocks: List[ContentBlock]) -> Optional[str]:
        """Extract essential ingredients, filtering out contextual content"""
        ingredient_parts = []
        
        for block in content_blocks:
            if (block.block_type == RecipeBlockType.ESSENTIAL and 
                block.content_type == ContentType.INGREDIENT_LIST):
                
                # Filter out contextual lines within ingredients
                lines = block.content.split('\n')
                filtered_lines = []
                
                for line in lines:
                    line = line.strip()
                    # Skip contextual headers
                    if not self._is_contextual_line(line):
                        filtered_lines.append(line)
                
                if filtered_lines:
                    ingredient_parts.extend(filtered_lines)
        
        return '\n'.join(ingredient_parts) if ingredient_parts else None
    
    def _extract_essential_instructions(self, content_blocks: List[ContentBlock]) -> Optional[str]:
        """Extract essential instructions, filtering out contextual content"""
        instruction_parts = []
        
        for block in content_blocks:
            if (block.block_type == RecipeBlockType.ESSENTIAL and 
                block.content_type == ContentType.INSTRUCTION_STEPS):
                
                # Filter out contextual lines within instructions
                lines = block.content.split('\n')
                filtered_lines = []
                
                for line in lines:
                    line = line.strip()
                    # Skip contextual headers and fluff
                    if not self._is_contextual_line(line) and not self._is_instructional_fluff(line):
                        filtered_lines.append(line)
                
                if filtered_lines:
                    instruction_parts.extend(filtered_lines)
        
        return '\n'.join(instruction_parts) if instruction_parts else None
    
    def _extract_metadata(self, content_blocks: List[ContentBlock]) -> Dict[str, str]:
        """Extract recipe metadata"""
        metadata = {}
        
        for block in content_blocks:
            if block.block_type == RecipeBlockType.METADATA:
                # Parse metadata from content
                text = block.content.lower()
                
                # Extract servings
                serves_match = re.search(r'(serves|makes|yields?)\s+(\d+)', text)
                if serves_match:
                    metadata['servings'] = f"{serves_match.group(1).title()} {serves_match.group(2)}"
                
                # Extract timing
                time_match = re.search(r'(\d+)\s+(minutes?|hours?)', text)
                if time_match:
                    metadata['total_time'] = f"{time_match.group(1)} {time_match.group(2)}"
                
                # Extract difficulty
                difficulty_match = re.search(r'(beginner|intermediate|advanced)', text)
                if difficulty_match:
                    metadata['difficulty'] = difficulty_match.group(1).title()
        
        return metadata
    
    def _extract_educational_content(self, content_blocks: List[ContentBlock]) -> Optional[str]:
        """Extract educational content (optional)"""
        educational_parts = []
        
        for block in content_blocks:
            if block.block_type == RecipeBlockType.EDUCATIONAL:
                educational_parts.append(block.content)
        
        return '\n\n'.join(educational_parts) if educational_parts else None
    
    def _is_contextual_line(self, line: str) -> bool:
        """Check if line is contextual content that should be filtered"""
        line_lower = line.lower().strip()
        
        # Check against contextual patterns
        all_patterns = []
        for pattern_list in self.contextual_patterns.values():
            all_patterns.extend(pattern_list)
        
        for pattern in all_patterns:
            if re.search(pattern, line_lower):
                return True
        
        return False
    
    def _is_instructional_fluff(self, line: str) -> bool:
        """Check if line is instructional fluff that adds no value"""
        line_lower = line.lower().strip()
        
        fluff_phrases = [
            'start cooking', 'let\'s begin', 'here we go', 'ready to start',
            'follow these steps', 'step by step', 'now we\'re cooking'
        ]
        
        for phrase in fluff_phrases:
            if phrase in line_lower:
                return True
        
        return False

def test_recipe_boundary_detection():
    """Test the recipe boundary detection with sample cookbook content"""
    print("🧪 TESTING RECIPE BOUNDARY DETECTION")
    print("=" * 70)
    
    # Simulate cookbook pages with mixed content
    sample_pages = [
        # Page 1: Recipe start with title and metadata
        """CHOCOLATE CHIP COOKIES
        BEGINNER
        MAKES 24 COOKIES
        30 MINUTES
        
        Before You Begin
        These cookies are perfect for beginners. The key is not to overmix the dough.
        
        PREPARE INGREDIENTS""",
        
        # Page 2: Ingredients 
        """• 2 cups all-purpose flour
        • 1 teaspoon baking soda
        • 1 teaspoon salt
        • 1 cup butter, softened
        • 3/4 cup granulated sugar
        • 3/4 cup brown sugar
        • 2 large eggs
        • 2 teaspoons vanilla extract
        • 2 cups chocolate chips
        
        START COOKING!""",
        
        # Page 3: Instructions
        """1. Preheat oven to 375°F. Line baking sheets with parchment paper.
        2. In medium bowl, whisk together flour, baking soda, and salt.
        3. In large bowl, beat butter and both sugars until fluffy.
        4. Beat in eggs and vanilla until combined.
        5. Gradually mix in flour mixture until just combined.
        6. Stir in chocolate chips.
        7. Drop rounded tablespoons of dough onto prepared baking sheets.
        8. Bake for 9-11 minutes until golden brown.
        9. Cool on baking sheet for 5 minutes before transferring to wire rack.
        
        GRILLED CHICKEN SALAD""",
        
        # Page 4: Next recipe starts
        """INTERMEDIATE
        SERVES 4
        45 MINUTES
        
        Why This Recipe Works
        Grilling the chicken gives it amazing flavor while keeping it juicy.
        
        PREPARE INGREDIENTS"""
    ]
    
    page_numbers = [1, 2, 3, 4]
    
    # Test the boundary detector
    detector = RecipeBoundaryDetector()
    recipe_blocks = detector.detect_recipe_blocks(sample_pages, page_numbers)
    
    # Display results
    print(f"\n📊 DETECTION RESULTS:")
    print(f"Found {len(recipe_blocks)} complete recipe blocks")
    
    for i, recipe in enumerate(recipe_blocks, 1):
        print(f"\n🍽️  RECIPE {i}: {recipe.title}")
        print(f"   Confidence: {recipe.confidence_score:.2f}")
        print(f"   Pages: {recipe.page_numbers}")
        print(f"   Metadata: {recipe.metadata}")
        print(f"   Ingredients preview: {recipe.ingredients[:100]}...")
        print(f"   Instructions preview: {recipe.instructions[:100]}...")
        if recipe.educational_content:
            print(f"   Educational content: {len(recipe.educational_content)} chars")

if __name__ == "__main__":
    test_recipe_boundary_detection()
