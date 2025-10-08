"""
OCR Text Parser - Battle-tested recipe extraction from plain text
==================================================================

Combines proven strategies from:
- AdaptiveRecipeExtractor (cookbook processing)
- WebRecipeExtractor (URL imports)

Key Innovation: IMPLICIT section detection by content patterns,
not just relying on explicit "Ingredients:" headers.

Plus: OCR artifact cleanup for cleaner results!

Author: GitHub Copilot
Date: October 7, 2025
"""

import logging
import re
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
    
    def _cleanup_ocr_artifacts(self, text: str) -> str:
        """
        Clean up common OCR artifacts and errors
        
        Rules:
        1. Remove all-caps concatenated words (book titles, headers)
        2. Clean multiple spaces
        
        NOTE: Don't truncate at "Variations" here - that's done per-line
        """
        if not text:
            return text
        
        # 1. Remove all-caps concatenated words (likely book title/header artifacts)
        # Example: "SALTFATACIDHEAT" 
        text = re.sub(r'\b[A-Z]{15,}\b', '', text)
        
        # 2. Clean multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # 3. Remove trailing fragments (incomplete sentences at end)
        text = text.strip()
        
        return text
    
    def parse(self, text: str) -> Dict:
        """
        Parse OCR text into recipe structure
        
        Returns:
            Dict with title, ingredients, instructions, confidence
        """
        # DON'T clean the full text yet - parse first, then clean results
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        title = self._find_title(lines)
        ingredients, instruction_lines = self._find_sections(lines, title)
        
        # Combine instruction lines into proper steps
        instructions = self._combine_instruction_steps(instruction_lines)
        
        result = {
            'title': title or "Imported Recipe",
            'ingredients': '\n'.join(ingredients) if ingredients else "No ingredients detected",
            'instructions': '\n'.join(instructions) if instructions else "See ingredients section",
            'category': 'imported',
            'confidence': self._calculate_confidence(title, ingredients, instructions)
        }
        
        logger.info(f"✅ Parsed '{result['title']}': {len(ingredients)} ingredients, {len(instructions)} instruction steps")
        
        # DEBUG: Export full recipe card
        logger.info("=" * 80)
        logger.info(f"📋 TITLE: {result['title']}")
        logger.info("=" * 80)
        logger.info(f"🥕 INGREDIENTS ({len(ingredients)} items):")
        for i, ing in enumerate(ingredients[:10], 1):  # Show first 10
            logger.info(f"  {i}. {ing}")
        if len(ingredients) > 10:
            logger.info(f"  ... and {len(ingredients) - 10} more")
        logger.info("=" * 80)
        logger.info(f"📖 INSTRUCTIONS ({len(instructions)} steps):")
        for i, inst in enumerate(instructions[:10], 1):  # Show first 10
            logger.info(f"  {i}. {inst[:100]}{'...' if len(inst) > 100 else ''}")
        if len(instructions) > 10:
            logger.info(f"  ... and {len(instructions) - 10} more steps")
        logger.info("=" * 80)
        
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
    
    def _combine_instruction_steps(self, lines: List[str]) -> List[str]:
        """
        Combine broken instruction lines into proper steps
        
        Rules:
        - Lines starting with action words = new step
        - Short continuation lines get merged with previous step
        - Period at end = end of step (usually)
        - Filter out incomplete/short steps
        """
        if not lines:
            return []
        
        steps = []
        current_step = ""
        
        for line in lines:
            # Clean the line
            line = self._cleanup_ocr_artifacts(line)
            if not line:
                continue
            
            line_lower = line.lower()
            
            # Check if this starts a new step (action word at start)
            starts_new_step = any(line_lower.startswith(word) for word in self.ACTION_WORDS)
            
            # If we have a current step and this starts a new one, save current
            if current_step and starts_new_step:
                steps.append(current_step.strip())
                current_step = line
            # If we have a current step and this is a continuation
            elif current_step:
                # Add with space (sentence continues)
                current_step += " " + line
            # First line
            else:
                current_step = line
        
        # Don't forget the last step!
        if current_step:
            steps.append(current_step.strip())
        
        # Filter out steps that are too short or incomplete
        quality_steps = []
        for i, step in enumerate(steps):
            # Check if this step contains "Variations" (next recipe starting)
            if 'variations' in step.lower():
                # Keep everything before "Variations" in this step
                parts = re.split(r'variations?', step, maxsplit=1, flags=re.IGNORECASE)
                step = parts[0].strip()
                logger.info(f"🧹 Truncated step at 'Variations': kept '{step[:50]}...'")
                if step:  # Only add if there's content left
                    quality_steps.append(step)
                break  # Stop processing more steps
            
            # Must be at least 15 characters
            if len(step) < 15:
                logger.info(f"🧹 Filtered out short step: '{step}'")
                continue
            
            # Last step should end with punctuation (not a fragment)
            if i == len(steps) - 1 and not step[-1] in '.!?':
                if len(step) < 30:  # Short AND no punctuation = fragment
                    logger.info(f"🧹 Filtered out fragment: '{step}'")
                    continue
            
            quality_steps.append(step)
        
        logger.info(f"📝 Combined {len(lines)} lines into {len(quality_steps)} quality instruction steps")
        return quality_steps
    
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
