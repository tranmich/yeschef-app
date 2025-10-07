"""
OCR Text Parser - Battle-tested recipe extraction from plain text
==================================================================

Combines proven strategies from:
- AdaptiveRecipeExtractor (cookbook processing)
- WebRecipeExtractor (URL imports)

Key Innovation: IMPLICIT section detection by content patterns,
not just relying on explicit "Ingredients:" headers.

Author: GitHub Copilot
Date: October 7, 2025
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class OCRTextParser:
    """
    Parse recipe text using content-based detection
    
    Works WITHOUT explicit section headers!
    """
    
    # Proven patterns from AdaptiveRecipeExtractor
    MEASUREMENTS = [
        'cup', 'tablespoon', 'teaspoon', 'pound', 'ounce', 'gram', 'kg', 'ml',
        'liter', 'oz', 'lb', 'tsp', 'tbsp', 'large', 'medium', 'small', 'pinch', 'dash', 'clove'
    ]
    
    ACTION_WORDS = [
        'heat', 'cook', 'add', 'bring', 'stir', 'mix', 'pour', 'place', 'remove',
        'drain', 'serve', 'bake', 'roast', 'sauté', 'boil', 'simmer', 'combine',
        'whisk', 'chop', 'slice', 'dice', 'blend', 'season', 'taste', 'adjust',
        'preheat', 'fold', 'transfer', 'cover', 'crank'
    ]
    
    SKIP_PATTERNS = ['===', '---', 'www.', 'http', 'chapter']
    
    def parse(self, text: str) -> Dict:
        """
        Parse OCR text into recipe structure
        
        Returns:
            Dict with title, ingredients, instructions, confidence
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        title = self._find_title(lines)
        ingredients, instructions = self._find_sections(lines, title)
        
        result = {
            'title': title or "Imported Recipe",
            'ingredients': '\n'.join(ingredients) if ingredients else "No ingredients detected",
            'instructions': '\n'.join(instructions) if instructions else "See ingredients section",
            'category': 'imported',
            'confidence': self._calculate_confidence(title, ingredients, instructions)
        }
        
        logger.info(f"✅ Parsed '{result['title']}': {len(ingredients)} ingredients, {len(instructions)} instruction lines")
        return result
    
    def _find_title(self, lines: List[str]) -> str:
        """Find recipe title using proven heuristics"""
        for i, line in enumerate(lines[:15]):
            line_lower = line.lower()
            
            # Skip artifacts
            if any(pattern in line_lower for pattern in self.SKIP_PATTERNS):
                continue
            
            # Good title characteristics (from AdaptiveRecipeExtractor)
            if (5 <= len(line) <= 100 and
                not line[0].isdigit() and
                not any(skip in line_lower for skip in ['page', 'serves', 'serving', 'yield', 'prep time', 'cook time'])):
                
                letter_count = sum(1 for c in line if c.isalpha())
                digit_count = sum(1 for c in line if c.isdigit())
                
                if letter_count > digit_count:
                    logger.info(f"📋 Found title: {line}")
                    return line
        
        return None
    
    def _find_sections(self, lines: List[str], title: str) -> tuple:
        """
        Find ingredients and instructions using IMPLICIT detection
        
        Key innovation: Don't require explicit section headers!
        """
        ingredients = []
        instructions = []
        current_section = None
        title_found = False
        
        for line in lines:
            line_lower = line.lower()
            
            # Skip artifacts
            if any(pattern in line_lower for pattern in self.SKIP_PATTERNS):
                continue
            
            # Skip title line
            if title and line == title:
                title_found = True
                continue
            
            # Skip intro lines (serving size, description)
            if title_found and current_section is None:
                if any(word in line_lower for word in ['serves', 'yield', 'serving']):
                    continue
                # Long descriptive text
                if len(line) > 80 and not any(c.isdigit() for c in line[:10]):
                    continue
            
            # EXPLICIT markers (if present)
            if 'ingredient' in line_lower and len(line) < 30:
                current_section = 'ingredients'
                logger.info("🥕 Explicit ingredients marker found")
                continue
            elif any(marker in line_lower for marker in ['instruction', 'direction', 'method', 'preparation']) and len(line) < 30:
                current_section = 'instructions'
                logger.info("📖 Explicit instructions marker found")
                continue
            
            # IMPLICIT DETECTION - The magic happens here!
            
            # Auto-detect ingredients: line with measurements or numbers
            if current_section is None:
                has_measurement = any(m in line_lower for m in self.MEASUREMENTS)
                has_number = any(c.isdigit() for c in line[:10])
                
                # Single-word ingredients
                simple_ingredients = ['salt', 'pepper', 'water', 'oil', 'butter']
                is_simple = line_lower in simple_ingredients
                
                if (has_measurement or has_number or is_simple) and len(line) > 2:
                    current_section = 'ingredients'
                    logger.info("🥕 Auto-detected ingredients (measurement pattern)")
            
            # Auto-detect instructions: action word at start + have ingredients
            if current_section == 'ingredients' and len(ingredients) > 2:
                starts_with_action = any(line_lower.startswith(word) for word in self.ACTION_WORDS)
                if starts_with_action:
                    current_section = 'instructions'
                    logger.info("📖 Auto-switched to instructions (action word)")
            
            # COLLECT based on section
            if current_section == 'ingredients':
                # Check if this is really an ingredient
                has_measurement = any(m in line_lower for m in self.MEASUREMENTS)
                has_number = any(c.isdigit() for c in line[:10])
                starts_with_action = any(line_lower.startswith(word) for word in self.ACTION_WORDS)
                
                if not starts_with_action and (has_measurement or has_number or len(line) < 50):
                    cleaned = line.lstrip('-•*+ ')
                    ingredients.append(cleaned)
                else:
                    # Actually an instruction!
                    current_section = 'instructions'
                    cleaned = line.lstrip('-•*+ 0123456789.')
                    instructions.append(cleaned)
                    
            elif current_section == 'instructions':
                cleaned = line.lstrip('-•*+ 0123456789.')
                instructions.append(cleaned)
        
        return ingredients, instructions
    
    def _calculate_confidence(self, title: str, ingredients: List[str], instructions: List[str]) -> float:
        """Calculate confidence score"""
        score = 0.0
        
        if title and title != "Imported Recipe":
            score += 0.3
        
        if len(ingredients) > 3:
            score += 0.4
        elif len(ingredients) > 0:
            score += 0.2
        
        if len(instructions) > 3:
            score += 0.3
        elif len(instructions) > 0:
            score += 0.1
        
        return min(score, 1.0)
