#!/usr/bin/env python3
"""
🔧 SIMPLE RECIPE BLOCK EXTRACTOR (Debugger Version)
==================================================

This creates a simplified version to debug the recipe block detection logic.
We'll focus on the core principle: title + ingredients + instructions = one recipe.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from core_systems.semantic_recipe_engine import SemanticRecipeEngine, ContentType, ValidationLevel

@dataclass
class SimpleRecipe:
    """Simple recipe structure"""
    title: str
    ingredients: List[str]
    instructions: List[str]
    metadata: Dict[str, str]
    confidence: float

class SimpleRecipeExtractor:
    """Simplified recipe extractor for debugging"""
    
    def __init__(self):
        self.semantic_engine = SemanticRecipeEngine(ValidationLevel.STRICT)
    
    def extract_recipes_from_text(self, text: str) -> List[SimpleRecipe]:
        """
        Extract complete recipes from text using a simple approach:
        1. Find recipe titles (food-related)
        2. Group following content until next title
        3. Extract ingredients and instructions from each group
        4. Filter out contextual content
        """
        print("🔍 EXTRACTING RECIPES FROM TEXT")
        print("=" * 50)
        
        lines = text.split('\n')
        recipes = []
        
        # Step 1: Find recipe title positions
        title_positions = []
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            content_type, confidence = self.semantic_engine.classify_content_type(line)
            
            if content_type == ContentType.RECIPE_TITLE and confidence > 0.7:
                title_positions.append({
                    'line_num': i,
                    'title': line,
                    'confidence': confidence
                })
                print(f"📍 Found recipe title at line {i}: '{line}' (confidence: {confidence:.2f})")
        
        # Step 2: Group content between titles
        for i, title_info in enumerate(title_positions):
            start_line = title_info['line_num']
            
            # Find end line (next title or end of text)
            if i + 1 < len(title_positions):
                end_line = title_positions[i + 1]['line_num']
            else:
                end_line = len(lines)
            
            # Extract content between titles
            recipe_lines = lines[start_line:end_line]
            recipe_text = '\n'.join(recipe_lines)
            
            print(f"\n🔬 Processing recipe block {i+1}: '{title_info['title']}'")
            print(f"   Lines {start_line}-{end_line-1} ({end_line - start_line} lines)")
            
            # Extract recipe components
            recipe = self._extract_recipe_components(title_info['title'], recipe_text)
            
            if recipe:
                recipes.append(recipe)
                print(f"✅ Successfully extracted: '{recipe.title}'")
            else:
                print(f"❌ Failed to extract complete recipe")
        
        return recipes
    
    def _extract_recipe_components(self, title: str, recipe_text: str) -> Optional[SimpleRecipe]:
        """Extract components from a recipe text block"""
        
        lines = recipe_text.split('\n')
        
        # Separate into different component lists
        ingredients = []
        instructions = []
        metadata = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip the title line itself
            if line == title:
                continue
            
            # Skip contextual content
            if self._is_contextual_content(line):
                print(f"   🚫 Skipping contextual: '{line}'")
                continue
            
            # Classify line
            content_type, confidence = self.semantic_engine.classify_content_type(line)
            
            # Group by type
            if self._looks_like_ingredient(line):
                ingredients.append(line)
                print(f"   🥕 Ingredient: '{line}'")
            elif self._looks_like_instruction(line):
                instructions.append(line)
                print(f"   👩‍🍳 Instruction: '{line}'")
            elif self._looks_like_metadata(line):
                metadata.update(self._parse_metadata(line))
                print(f"   📊 Metadata: '{line}'")
            else:
                print(f"   ❓ Unclassified: '{line}' ({content_type.value})")
        
        # Check if we have a complete recipe
        if not ingredients:
            print(f"   ❌ No ingredients found")
            return None
        
        if not instructions:
            print(f"   ❌ No instructions found")
            return None
        
        # Create recipe
        recipe = SimpleRecipe(
            title=title,
            ingredients=ingredients,
            instructions=instructions,
            metadata=metadata,
            confidence=0.8  # Base confidence
        )
        
        # Validate with semantic engine
        recipe_data = {
            'title': title,
            'ingredients': '\n'.join(ingredients),
            'instructions': '\n'.join(instructions),
            **metadata
        }
        
        validation_result = self.semantic_engine.validate_complete_recipe(recipe_data)
        recipe.confidence = validation_result.confidence_score
        
        if validation_result.is_valid_recipe:
            return recipe
        else:
            print(f"   ❌ Recipe failed validation:")
            for error in validation_result.validation_errors:
                print(f"      • {error}")
            return None
    
    def _is_contextual_content(self, line: str) -> bool:
        """Check if line is contextual content to skip"""
        line_lower = line.lower().strip()
        
        contextual_phrases = [
            'before you begin', 'why this recipe works', 'the science',
            'testing notes', 'chef\'s note', 'cooking tip',
            'prepare ingredients', 'start cooking', 'let\'s begin'
        ]
        
        for phrase in contextual_phrases:
            if phrase in line_lower:
                return True
        
        return False
    
    def _looks_like_ingredient(self, line: str) -> bool:
        """Check if line looks like an ingredient"""
        # Has measurements
        if re.search(r'\d+\s*(cup|tablespoon|teaspoon|pound|ounce|tbsp|tsp|lb|oz)', line, re.IGNORECASE):
            return True
        
        # Starts with bullet point
        if line.startswith('•') and self.semantic_engine._contains_food_words(line):
            return True
        
        return False
    
    def _looks_like_instruction(self, line: str) -> bool:
        """Check if line looks like an instruction step"""
        # Starts with number and period
        if re.match(r'^\d+\.', line):
            return True
        
        return False
    
    def _looks_like_metadata(self, line: str) -> bool:
        """Check if line contains metadata"""
        line_lower = line.lower()
        
        metadata_patterns = [
            r'(serves|makes|yields?)\s+\d+',
            r'\d+\s+(minutes?|hours?)',
            r'(beginner|intermediate|advanced)',
        ]
        
        for pattern in metadata_patterns:
            if re.search(pattern, line_lower):
                return True
        
        return False
    
    def _parse_metadata(self, line: str) -> Dict[str, str]:
        """Parse metadata from line"""
        metadata = {}
        line_lower = line.lower()
        
        # Extract servings
        serves_match = re.search(r'(serves|makes|yields?)\s+(\d+)', line_lower)
        if serves_match:
            metadata['servings'] = f"{serves_match.group(1).title()} {serves_match.group(2)}"
        
        # Extract timing
        time_match = re.search(r'(\d+)\s+(minutes?|hours?)', line_lower)
        if time_match:
            metadata['total_time'] = f"{time_match.group(1)} {time_match.group(2)}"
        
        # Extract difficulty
        difficulty_match = re.search(r'(beginner|intermediate|advanced)', line_lower)
        if difficulty_match:
            metadata['difficulty'] = difficulty_match.group(1).title()
        
        return metadata

def test_simple_extractor():
    """Test the simple extractor with cookbook content"""
    print("🧪 TESTING SIMPLE RECIPE EXTRACTOR")
    print("=" * 70)
    
    # Sample cookbook content (like ATK Teen format)
    sample_text = """CHOCOLATE CHIP COOKIES
BEGINNER
MAKES 24 COOKIES
30 MINUTES

Before You Begin
These cookies are perfect for beginners. The key is not to overmix the dough.

PREPARE INGREDIENTS
• 2 cups all-purpose flour
• 1 teaspoon baking soda
• 1 teaspoon salt
• 1 cup butter, softened
• 3/4 cup granulated sugar
• 3/4 cup brown sugar
• 2 large eggs
• 2 teaspoons vanilla extract
• 2 cups chocolate chips

START COOKING!
1. Preheat oven to 375°F. Line baking sheets with parchment paper.
2. In medium bowl, whisk together flour, baking soda, and salt.
3. In large bowl, beat butter and both sugars until fluffy.
4. Beat in eggs and vanilla until combined.
5. Gradually mix in flour mixture until just combined.
6. Stir in chocolate chips.
7. Drop rounded tablespoons of dough onto prepared baking sheets.
8. Bake for 9-11 minutes until golden brown.
9. Cool on baking sheet for 5 minutes before transferring to wire rack.

GRILLED CHICKEN SALAD
INTERMEDIATE
SERVES 4
45 MINUTES

Why This Recipe Works
Grilling the chicken gives it amazing flavor while keeping it juicy.

PREPARE INGREDIENTS
• 2 boneless chicken breasts
• 6 cups mixed greens
• 1 cup cherry tomatoes
• 1/2 red onion, sliced
• 2 tablespoons olive oil
• 1 tablespoon lemon juice

START COOKING!
1. Preheat grill to medium-high heat.
2. Season chicken with salt and pepper.
3. Grill chicken for 6-7 minutes per side until cooked through.
4. Let chicken rest for 5 minutes, then slice.
5. Combine greens, tomatoes, and onion in large bowl.
6. Whisk olive oil and lemon juice for dressing.
7. Top salad with sliced chicken and drizzle with dressing."""

    # Test the extractor
    extractor = SimpleRecipeExtractor()
    recipes = extractor.extract_recipes_from_text(sample_text)
    
    # Display results
    print(f"\n📊 EXTRACTION RESULTS:")
    print(f"Found {len(recipes)} complete recipes")
    
    for i, recipe in enumerate(recipes, 1):
        print(f"\n🍽️  RECIPE {i}: {recipe.title}")
        print(f"   Confidence: {recipe.confidence:.2f}")
        print(f"   Metadata: {recipe.metadata}")
        print(f"   Ingredients ({len(recipe.ingredients)}):")
        for ing in recipe.ingredients[:3]:  # Show first 3
            print(f"     • {ing}")
        if len(recipe.ingredients) > 3:
            print(f"     ... and {len(recipe.ingredients) - 3} more")
        
        print(f"   Instructions ({len(recipe.instructions)}):")
        for inst in recipe.instructions[:2]:  # Show first 2
            print(f"     • {inst}")
        if len(recipe.instructions) > 2:
            print(f"     ... and {len(recipe.instructions) - 2} more")

if __name__ == "__main__":
    test_simple_extractor()
