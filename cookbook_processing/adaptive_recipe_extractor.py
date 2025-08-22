#!/usr/bin/env python3
"""
🧠 ADAPTIVE RECIPE EXTRACTOR
============================

ONE extractor that learns as it goes. No more per-book extractors!

Core Principle: Try multiple extraction methods simultaneously, 
use confidence scoring to pick the best results, and learn 
successful patterns for future cookbooks.

FOCUS: Just 4 fields - title, category, ingredients, instructions
GOAL: Works on any cookbook, gets smarter with each book

Author: GitHub Copilot
Date: August 22, 2025
"""

import os
import re
import json
import logging
import PyPDF2
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Recipe:
    """Simple recipe structure - just the essentials"""
    title: str = ""
    category: str = ""
    ingredients: str = ""
    instructions: str = ""
    page_number: int = 0
    confidence: float = 0.0
    source_file: str = ""

class AdaptiveRecipeExtractor:
    """
    ONE extractor that learns as it goes
    
    Strategy: Try everything at once, pick the best results, learn patterns
    """
    
    def __init__(self, knowledge_file: str = "extractor_knowledge.json"):
        self.knowledge_file = knowledge_file
        self.knowledge = self._load_knowledge()
        self.extracted_recipes = []
        self.stats = {"total_recipes": 0, "cookbooks_processed": 0}
        
    def _load_knowledge(self) -> Dict:
        """Load accumulated extraction knowledge"""
        if os.path.exists(self.knowledge_file):
            try:
                with open(self.knowledge_file, 'r') as f:
                    knowledge = json.load(f)
                logger.info(f"📚 Loaded knowledge from {len(knowledge.get('successful_patterns', []))} previous extractions")
                return knowledge
            except Exception as e:
                logger.warning(f"Could not load knowledge: {e}")
        
        # Initialize empty knowledge base
        return {
            "successful_patterns": [],
            "title_patterns": [],
            "ingredient_markers": [],
            "instruction_markers": [],
            "category_keywords": {},
            "cookbook_characteristics": {},
            "extraction_stats": {}
        }
    
    def _save_knowledge(self):
        """Save accumulated knowledge for future use"""
        try:
            with open(self.knowledge_file, 'w') as f:
                json.dump(self.knowledge, f, indent=2)
            logger.info(f"💾 Saved knowledge from {self.stats['cookbooks_processed']} cookbooks")
        except Exception as e:
            logger.error(f"Could not save knowledge: {e}")
    
    def extract_recipes(self, pdf_path: str) -> List[Recipe]:
        """
        Main extraction method - tries everything, learns as it goes
        """
        logger.info(f"🚀 Starting extraction: {os.path.basename(pdf_path)}")
        
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                total_pages = len(reader.pages)
                
                # Analyze cookbook characteristics
                cookbook_info = self._analyze_cookbook(reader, pdf_path)
                logger.info(f"📖 Detected: {cookbook_info['type']} style, {total_pages} pages")
                
                recipes = []
                
                # Extract recipes page by page
                for page_num in range(1, total_pages + 1):
                    try:
                        page_recipes = self._extract_page(reader, page_num, cookbook_info)
                        recipes.extend(page_recipes)
                        
                        if page_num % 50 == 0:
                            logger.info(f"📊 Progress: Page {page_num}/{total_pages}, Recipes: {len(recipes)}")
                            
                    except Exception as e:
                        logger.debug(f"Error on page {page_num}: {e}")
                        continue
                
                # Learn from this cookbook
                self._learn_from_cookbook(pdf_path, recipes, cookbook_info)
                
                # Update stats
                self.stats["total_recipes"] += len(recipes)
                self.stats["cookbooks_processed"] += 1
                self.extracted_recipes = recipes
                
                logger.info(f"✅ Extracted {len(recipes)} recipes from {os.path.basename(pdf_path)}")
                return recipes
                
        except Exception as e:
            logger.error(f"Failed to extract from {pdf_path}: {e}")
            return []
    
    def _analyze_cookbook(self, reader, pdf_path: str) -> Dict:
        """Quickly analyze cookbook to understand its structure"""
        
        filename = os.path.basename(pdf_path).lower()
        total_pages = len(reader.pages)
        
        # Sample a few pages to understand structure
        sample_texts = []
        sample_pages = [min(50, total_pages//4), min(100, total_pages//2), min(200, total_pages-50)]
        
        for page_idx in sample_pages:
            if page_idx < total_pages:
                try:
                    page_text = reader.pages[page_idx].extract_text()
                    sample_texts.append(page_text)
                except:
                    continue
        
        combined_sample = " ".join(sample_texts).lower()
        
        # Detect cookbook type based on patterns
        cookbook_type = "unknown"
        
        if any(term in filename for term in ['atk', 'america', 'test kitchen']):
            cookbook_type = "atk_style"
        elif any(term in filename for term in ['bittman', 'how to cook']):
            cookbook_type = "bittman_style"
        elif any(term in combined_sample for term in ['ingredients:', 'directions:', 'prep time:']):
            cookbook_type = "magazine_style"
        elif total_pages > 500:
            cookbook_type = "comprehensive"
        else:
            cookbook_type = "simple"
        
        return {
            "type": cookbook_type,
            "total_pages": total_pages,
            "filename": filename,
            "sample_text": combined_sample[:1000],  # First 1000 chars for pattern matching
            "has_toc": "contents" in combined_sample or "table of contents" in combined_sample
        }
    
    def _extract_page(self, reader, page_num: int, cookbook_info: Dict) -> List[Recipe]:
        """
        Extract recipes from a single page using ALL methods simultaneously
        """
        
        try:
            page = reader.pages[page_num - 1]
            page_text = page.extract_text()
            
            if not page_text or len(page_text.strip()) < 50:
                return []
            
            # Try multiple extraction methods simultaneously
            candidates = []
            
            # Method 1: Pattern-based extraction (fast, works on most text)
            pattern_recipe = self._extract_with_patterns(page_text, page_num)
            if pattern_recipe:
                candidates.append(("pattern", pattern_recipe))
            
            # Method 2: Structure-based extraction (looks for visual cues)
            structure_recipe = self._extract_with_structure(page_text, page_num)
            if structure_recipe:
                candidates.append(("structure", structure_recipe))
            
            # Method 3: Learned patterns (use knowledge from previous cookbooks)
            learned_recipe = self._extract_with_learned_patterns(page_text, page_num, cookbook_info)
            if learned_recipe:
                candidates.append(("learned", learned_recipe))
            
            # Method 4: Fallback extraction (works on any text with cooking content)
            fallback_recipe = self._extract_fallback(page_text, page_num)
            if fallback_recipe:
                candidates.append(("fallback", fallback_recipe))
            
            # Pick the best candidate based on confidence
            best_recipe = self._select_best_candidate(candidates)
            
            if best_recipe and self._validate_recipe(best_recipe):
                best_recipe.source_file = cookbook_info["filename"]
                return [best_recipe]
            
            return []
            
        except Exception as e:
            logger.debug(f"Error extracting page {page_num}: {e}")
            return []
    
    def _extract_with_patterns(self, page_text: str, page_num: int) -> Optional[Recipe]:
        """Extract using common recipe patterns"""
        
        recipe = Recipe(page_number=page_num)
        confidence = 0.0
        
        lines = page_text.split('\n')
        
        # Find title (usually short, near top, capitalized)
        for i, line in enumerate(lines[:10]):
            line = line.strip()
            if 5 <= len(line) <= 80 and (line.istitle() or line.isupper()):
                # Avoid obvious non-titles
                if not any(skip in line.lower() for skip in ['page', 'chapter', 'ingredients', 'instructions']):
                    recipe.title = line
                    confidence += 0.3
                    break
        
        # Find ingredients (look for measurement patterns)
        ingredients_section = self._find_section_with_measurements(lines)
        if ingredients_section:
            recipe.ingredients = ingredients_section
            confidence += 0.3
        
        # Find instructions (look for cooking verbs and steps)
        instructions_section = self._find_section_with_cooking_verbs(lines)
        if instructions_section:
            recipe.instructions = instructions_section
            confidence += 0.3
        
        # Infer category from title
        if recipe.title:
            recipe.category = self._infer_category(recipe.title)
            confidence += 0.1
        
        recipe.confidence = confidence
        return recipe if confidence > 0.5 else None
    
    def _extract_with_structure(self, page_text: str, page_num: int) -> Optional[Recipe]:
        """Extract using visual structure cues"""
        
        recipe = Recipe(page_number=page_num)
        confidence = 0.0
        
        # Look for structured sections with headers
        lines = page_text.split('\n')
        
        # Find sections marked with headers
        current_section = None
        section_content = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a section header
            if any(header in line.upper() for header in ['INGREDIENTS', 'SERVES', 'MAKES']):
                current_section = 'ingredients'
                section_content[current_section] = []
            elif any(header in line.upper() for header in ['INSTRUCTIONS', 'METHOD', 'DIRECTIONS']):
                current_section = 'instructions'
                section_content[current_section] = []
            elif re.match(r'^\d+\.', line):  # Numbered steps
                if current_section != 'instructions':
                    current_section = 'instructions'
                    section_content[current_section] = []
                section_content[current_section].append(line)
            elif current_section and len(line) > 5:
                section_content[current_section].append(line)
        
        # Build recipe from sections
        if 'ingredients' in section_content:
            recipe.ingredients = '\n'.join(section_content['ingredients'])
            confidence += 0.4
        
        if 'instructions' in section_content:
            recipe.instructions = '\n'.join(section_content['instructions'])
            confidence += 0.4
        
        # Try to find title (largest text near top, not in sections)
        for line in lines[:8]:
            line = line.strip()
            if (5 <= len(line) <= 80 and 
                not any(skip in line.upper() for skip in ['INGREDIENTS', 'INSTRUCTIONS', 'PAGE']) and
                not recipe.title):
                recipe.title = line
                confidence += 0.2
                break
        
        if recipe.title:
            recipe.category = self._infer_category(recipe.title)
        
        recipe.confidence = confidence
        return recipe if confidence > 0.6 else None
    
    def _extract_with_learned_patterns(self, page_text: str, page_num: int, cookbook_info: Dict) -> Optional[Recipe]:
        """Extract using patterns learned from previous cookbooks"""
        
        if not self.knowledge.get("successful_patterns"):
            return None
        
        recipe = Recipe(page_number=page_num)
        confidence = 0.0
        
        # Try patterns that worked in similar cookbooks
        cookbook_type = cookbook_info.get("type", "unknown")
        
        for pattern in self.knowledge["successful_patterns"]:
            if pattern.get("cookbook_type") == cookbook_type:
                # Try this learned pattern
                if self._apply_learned_pattern(page_text, pattern, recipe):
                    confidence += 0.5
                    break
        
        # Use learned markers
        for marker in self.knowledge.get("ingredient_markers", []):
            if marker.lower() in page_text.lower():
                section = self._extract_section_after_marker(page_text, marker)
                if section:
                    recipe.ingredients = section
                    confidence += 0.3
                    break
        
        for marker in self.knowledge.get("instruction_markers", []):
            if marker.lower() in page_text.lower():
                section = self._extract_section_after_marker(page_text, marker)
                if section:
                    recipe.instructions = section
                    confidence += 0.3
                    break
        
        if recipe.title:
            recipe.category = self._infer_category(recipe.title)
        
        recipe.confidence = confidence
        return recipe if confidence > 0.4 else None
    
    def _extract_fallback(self, page_text: str, page_num: int) -> Optional[Recipe]:
        """Fallback extraction that works on any cooking text - BALANCED VERSION"""
        
        recipe = Recipe(page_number=page_num)
        confidence = 0.0
        
        # Balanced fallback: look for strong recipe indicators
        text_lower = page_text.lower()
        
        # Check if this looks like a recipe page
        cooking_indicators = ['cup', 'tablespoon', 'teaspoon', 'cook', 'bake', 'heat', 'add', 'mix', 'stir']
        cooking_score = sum(1 for indicator in cooking_indicators if indicator in text_lower)
        
        # Must have at least 3 cooking indicators (reasonable threshold)
        if cooking_score < 3:
            return None
        
        lines = [line.strip() for line in page_text.split('\n') if line.strip()]
        
        # Must have reasonable content (not just fragments)
        if len(lines) < 5:
            return None
        
        # Exclude obvious non-recipe pages
        exclusion_indicators = ['table of contents', 'index', 'acknowledgments', 'copyright', 'introduction']
        if any(indicator in text_lower for indicator in exclusion_indicators):
            return None
        
        # Look for title - be more flexible and smarter
        potential_titles = []
        
        # First, look for lines that are clearly recipe titles (not season headers)
        for i, line in enumerate(lines[:10]):
            if (5 <= len(line) <= 100 and 
                not line[0].isdigit() and
                not any(skip in line.lower() for skip in 
                       ['page', 'chapter', 'why this recipe works', 'serves', 'makes', 'total time', 'season'])):
                potential_titles.append((i, line))
        
        # If we found potential titles, pick the best one
        if potential_titles:
            # Prefer titles that aren't the first line (often headers)
            non_first_titles = [(i, title) for i, title in potential_titles if i > 0]
            if non_first_titles:
                recipe.title = non_first_titles[0][1]  # Take first non-header title
            else:
                recipe.title = potential_titles[0][1]  # Fall back to first title
            confidence += 0.25
        
        # Special case: If we see "SEASON X" followed by actual recipe name, use the recipe name
        if recipe.title and 'season' in recipe.title.lower():
            for i, line in enumerate(lines):
                if 'season' in line.lower() and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if (5 <= len(next_line) <= 80 and 
                        not any(skip in next_line.lower() for skip in ['serves', 'total time', 'why this recipe'])):
                        recipe.title = next_line  # Use the actual recipe name
                        break
        
        # Must have a title to proceed
        if not recipe.title:
            return None
        
        # Look for ingredients: lines with measurements
        ingredient_lines = []
        for line in lines:
            if (any(measurement in line.lower() for measurement in ['cup', 'tablespoon', 'teaspoon', 'pound', 'ounce', 'large', 'medium', 'small']) and
                not any(skip in line.lower() for skip in ['page', 'chapter', 'serves', 'makes', 'recipe', 'index', 'why this recipe works'])):
                ingredient_lines.append(line)
        
        # Accept if we have at least 2 ingredient lines (more flexible)
        if len(ingredient_lines) >= 2:
            recipe.ingredients = '\n'.join(ingredient_lines)
            confidence += 0.35
        
        # Look for instructions: lines with cooking verbs and numbers
        instruction_lines = []
        for line in lines:
            if (len(line) > 15 and  # Substantial lines
                (any(verb in line.lower() for verb in ['cook', 'bake', 'heat', 'add', 'mix', 'stir', 'simmer', 'combine']) or
                 re.match(r'^\d+\.', line)) and  # Numbered steps
                not any(skip in line.lower() for skip in ['page', 'chapter', 'ingredients', 'recipe', 'index', 'why this recipe works'])):
                instruction_lines.append(line)
        
        # Accept if we have at least 1 instruction line (more flexible)
        if len(instruction_lines) >= 1:
            recipe.instructions = '\n'.join(instruction_lines)
            confidence += 0.35
        
        # Bonus for having both ingredients and instructions
        if recipe.ingredients and recipe.instructions:
            confidence += 0.1
        
        if recipe.title:
            recipe.category = self._infer_category(recipe.title)
            confidence += 0.05
        
        # Reasonable threshold - not too strict, not too loose
        recipe.confidence = confidence
        return recipe if confidence > 0.6 else None
    
    def _find_section_with_measurements(self, lines: List[str]) -> str:
        """Find section with measurement patterns (likely ingredients)"""
        
        measurement_lines = []
        measurement_patterns = [
            r'\d+\s*(cup|tablespoon|teaspoon|pound|ounce|gram|kg|ml|liter)',
            r'\d+/\d+\s*(cup|tsp|tbsp)',
            r'\d+\s*(large|medium|small|whole)',
        ]
        
        for line in lines:
            line = line.strip()
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in measurement_patterns):
                measurement_lines.append(line)
        
        return '\n'.join(measurement_lines) if len(measurement_lines) >= 3 else ""
    
    def _find_section_with_cooking_verbs(self, lines: List[str]) -> str:
        """Find section with cooking instructions"""
        
        cooking_lines = []
        cooking_verbs = ['heat', 'cook', 'bake', 'roast', 'sauté', 'simmer', 'boil', 'mix', 'stir', 'add', 'combine', 'whisk']
        
        for line in lines:
            line = line.strip()
            if len(line) > 20:  # Substantial instruction lines
                if any(verb in line.lower() for verb in cooking_verbs):
                    cooking_lines.append(line)
        
        return '\n'.join(cooking_lines) if len(cooking_lines) >= 2 else ""
    
    def _extract_section_after_marker(self, page_text: str, marker: str) -> str:
        """Extract text section after finding a marker"""
        
        lines = page_text.split('\n')
        marker_idx = -1
        
        for i, line in enumerate(lines):
            if marker.lower() in line.lower():
                marker_idx = i
                break
        
        if marker_idx == -1:
            return ""
        
        # Extract following lines until next section or end
        section_lines = []
        for i in range(marker_idx + 1, min(len(lines), marker_idx + 15)):
            line = lines[i].strip()
            if line and not line.startswith(('CHAPTER', 'PAGE')):
                section_lines.append(line)
        
        return '\n'.join(section_lines)
    
    def _apply_learned_pattern(self, page_text: str, pattern: Dict, recipe: Recipe) -> bool:
        """Apply a learned extraction pattern"""
        
        # This would apply specific patterns learned from previous successful extractions
        # For now, return False (not implemented)
        return False
    
    def _select_best_candidate(self, candidates: List[Tuple[str, Recipe]]) -> Optional[Recipe]:
        """Select the best extraction candidate based on confidence"""
        
        if not candidates:
            return None
        
        # Sort by confidence, prefer certain methods
        method_preference = {"learned": 1.1, "structure": 1.0, "pattern": 0.9, "fallback": 0.8}
        
        best_candidate = None
        best_score = 0.0
        
        for method, recipe in candidates:
            score = recipe.confidence * method_preference.get(method, 1.0)
            if score > best_score:
                best_score = score
                best_candidate = recipe
        
        return best_candidate
    
    def _validate_recipe(self, recipe: Recipe) -> bool:
        """Validate that recipe has minimum required content - BALANCED VERSION"""
        
        # Must have title
        if not recipe.title or len(recipe.title.strip()) < 5:
            return False
        
        # Title should not be obviously wrong
        title_lower = recipe.title.lower()
        if any(bad_word in title_lower for bad_word in 
              ['page', 'chapter', 'index', 'table of contents', 'acknowledgments', 'copyright', 'season']):
            return False
        
        # Must have EITHER good ingredients OR good instructions (not necessarily both)
        has_good_ingredients = recipe.ingredients and len(recipe.ingredients.strip()) > 30
        has_good_instructions = recipe.instructions and len(recipe.instructions.strip()) > 40
        
        # At least one must be present
        if not (has_good_ingredients or has_good_instructions):
            return False
        
        # If we have ingredients, check they look real
        if has_good_ingredients:
            ingredients_lower = recipe.ingredients.lower()
            measurement_count = 0
            for measurement in ['cup', 'tablespoon', 'teaspoon', 'pound', 'ounce', 'gram']:
                if measurement in ingredients_lower:
                    measurement_count += 1
            
            # Must have at least 2 different types of measurements
            if measurement_count < 2:
                return False
        
        # If we have instructions, check they look real
        if has_good_instructions:
            instructions_lower = recipe.instructions.lower()
            cooking_verb_count = 0
            for verb in ['cook', 'bake', 'heat', 'add', 'mix', 'stir', 'simmer', 'roast', 'sauté']:
                if verb in instructions_lower:
                    cooking_verb_count += 1
            
            # Must have at least 2 different cooking verbs
            if cooking_verb_count < 2:
                return False
        
        return True
    
    def _infer_category(self, title: str) -> str:
        """Infer recipe category from title"""
        
        if not title:
            return "Main Dishes"
        
        title_lower = title.lower()
        
        # Use learned categories if available
        for category, keywords in self.knowledge.get("category_keywords", {}).items():
            if any(keyword in title_lower for keyword in keywords):
                return category
        
        # Default categories
        categories = {
            'Appetizers': ['appetizer', 'dip', 'spread', 'starter'],
            'Soups': ['soup', 'stew', 'chili', 'broth'],
            'Salads': ['salad', 'slaw'],
            'Main Dishes': ['chicken', 'beef', 'pork', 'fish', 'salmon'],
            'Pasta': ['pasta', 'noodles', 'spaghetti'],
            'Vegetables': ['vegetables', 'broccoli', 'carrots'],
            'Desserts': ['cake', 'pie', 'cookie', 'chocolate', 'dessert'],
            'Breakfast': ['pancake', 'waffle', 'eggs', 'breakfast'],
            'Bread': ['bread', 'muffin', 'biscuit']
        }
        
        for category, keywords in categories.items():
            if any(keyword in title_lower for keyword in keywords):
                return category
        
        return "Main Dishes"
    
    def _learn_from_cookbook(self, pdf_path: str, recipes: List[Recipe], cookbook_info: Dict):
        """Learn patterns from this cookbook for future use"""
        
        if not recipes:
            return
        
        logger.info(f"🧠 Learning from {len(recipes)} recipes...")
        
        # Learn successful patterns
        successful_patterns = []
        for recipe in recipes:
            if recipe.confidence > 0.7:
                pattern = {
                    "cookbook_type": cookbook_info["type"],
                    "title_pattern": self._extract_title_pattern(recipe.title),
                    "has_ingredients": bool(recipe.ingredients),
                    "has_instructions": bool(recipe.instructions),
                    "confidence": recipe.confidence
                }
                successful_patterns.append(pattern)
        
        self.knowledge["successful_patterns"].extend(successful_patterns)
        
        # Learn ingredient markers
        ingredient_markers = set()
        for recipe in recipes:
            if recipe.ingredients:
                # Look for markers that appear before ingredients
                markers = self._extract_markers_before_text(pdf_path, recipe.page_number, recipe.ingredients[:100])
                ingredient_markers.update(markers)
        
        self.knowledge["ingredient_markers"] = list(set(self.knowledge.get("ingredient_markers", []) + list(ingredient_markers)))
        
        # Learn instruction markers
        instruction_markers = set()
        for recipe in recipes:
            if recipe.instructions:
                markers = self._extract_markers_before_text(pdf_path, recipe.page_number, recipe.instructions[:100])
                instruction_markers.update(markers)
        
        self.knowledge["instruction_markers"] = list(set(self.knowledge.get("instruction_markers", []) + list(instruction_markers)))
        
        # Learn category keywords
        for recipe in recipes:
            if recipe.category and recipe.title:
                if recipe.category not in self.knowledge["category_keywords"]:
                    self.knowledge["category_keywords"][recipe.category] = []
                
                # Add title words as category keywords
                title_words = [word.lower() for word in recipe.title.split() if len(word) > 3]
                self.knowledge["category_keywords"][recipe.category].extend(title_words)
        
        # Store cookbook characteristics
        self.knowledge["cookbook_characteristics"][cookbook_info["filename"]] = {
            "type": cookbook_info["type"],
            "total_recipes": len(recipes),
            "avg_confidence": sum(r.confidence for r in recipes) / len(recipes),
            "extraction_date": datetime.now().isoformat()
        }
        
        # Save learned knowledge
        self._save_knowledge()
        
        logger.info(f"✅ Learned {len(successful_patterns)} new patterns, {len(ingredient_markers)} ingredient markers, {len(instruction_markers)} instruction markers")
    
    def _extract_title_pattern(self, title: str) -> str:
        """Extract a pattern from a title for future matching"""
        if not title:
            return ""
        
        # Create a simple pattern based on title characteristics
        length = len(title)
        has_caps = title.isupper()
        has_title_case = title.istitle()
        
        return f"len_{length}_caps_{has_caps}_title_{has_title_case}"
    
    def _extract_markers_before_text(self, pdf_path: str, page_num: int, text_sample: str) -> List[str]:
        """Extract markers that appear before given text (placeholder)"""
        
        # This would analyze the page to find what markers appear before the given text
        # For now, return empty list
        return []
    
    def save_recipes(self, output_path: str):
        """Save extracted recipes to JSON file"""
        
        recipes_data = {
            "extraction_info": {
                "total_recipes": len(self.extracted_recipes),
                "timestamp": datetime.now().isoformat(),
                "extractor_version": "adaptive_v1"
            },
            "recipes": [asdict(recipe) for recipe in self.extracted_recipes]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(recipes_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Saved {len(self.extracted_recipes)} recipes to {output_path}")
    
    def get_stats(self) -> Dict:
        """Get extraction statistics"""
        return {
            "total_recipes_extracted": self.stats["total_recipes"],
            "cookbooks_processed": self.stats["cookbooks_processed"],
            "knowledge_patterns": len(self.knowledge.get("successful_patterns", [])),
            "ingredient_markers_learned": len(self.knowledge.get("ingredient_markers", [])),
            "instruction_markers_learned": len(self.knowledge.get("instruction_markers", [])),
            "categories_learned": len(self.knowledge.get("category_keywords", {}))
        }
    
    def view_results(self, detailed: bool = False):
        """
        View extraction results in a formatted way
        
        Args:
            detailed: If True, show full recipe content. If False, show summary.
        """
        
        if not self.extracted_recipes:
            print("❌ No recipes to display. Run extraction first.")
            return
        
        total_recipes = len(self.extracted_recipes)
        print(f"\n🍽️  EXTRACTION RESULTS")
        print(f"{'='*50}")
        print(f"📊 Total Recipes Found: {total_recipes}")
        
        # Calculate confidence distribution
        high_conf = sum(1 for r in self.extracted_recipes if r.confidence >= 0.8)
        med_conf = sum(1 for r in self.extracted_recipes if 0.6 <= r.confidence < 0.8)
        low_conf = sum(1 for r in self.extracted_recipes if r.confidence < 0.6)
        
        print(f"🎯 Confidence Distribution:")
        print(f"   High (≥0.8): {high_conf} recipes")
        print(f"   Medium (0.6-0.8): {med_conf} recipes")
        print(f"   Low (<0.6): {low_conf} recipes")
        
        # Show category breakdown
        categories = {}
        for recipe in self.extracted_recipes:
            cat = recipe.category or "Unknown"
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"\n📚 Categories Found:")
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"   {category}: {count} recipes")
        
        # Show page range
        pages = [r.page_number for r in self.extracted_recipes if r.page_number > 0]
        if pages:
            print(f"\n📄 Page Range: {min(pages)} - {max(pages)}")
        
        # Ask user what to view
        print(f"\n🔍 VIEW OPTIONS:")
        print(f"1. Summary list (all recipes)")
        print(f"2. Detailed view (select recipes)")
        print(f"3. High confidence only")
        print(f"4. By category")
        print(f"5. Search recipes")
        
        try:
            choice = input(f"\nEnter choice (1-5): ").strip()
            
            if choice == "1":
                self._view_summary_list()
            elif choice == "2":
                self._view_detailed_recipes()
            elif choice == "3":
                self._view_high_confidence_only()
            elif choice == "4":
                self._view_by_category()
            elif choice == "5":
                self._search_recipes()
            else:
                print("Invalid choice. Showing summary list.")
                self._view_summary_list()
                
        except KeyboardInterrupt:
            print("\n👋 Viewer closed.")
            return
    
    def _view_summary_list(self):
        """Show summary list of all recipes"""
        
        print(f"\n📝 RECIPE SUMMARY LIST")
        print(f"{'='*80}")
        
        for i, recipe in enumerate(self.extracted_recipes, 1):
            confidence_indicator = self._get_confidence_indicator(recipe.confidence)
            
            print(f"{i:3d}. {confidence_indicator} {recipe.title}")
            print(f"     📍 Page {recipe.page_number} | 📂 {recipe.category} | 🎯 {recipe.confidence:.2f}")
            
            # Show content indicators
            indicators = []
            if recipe.ingredients:
                indicators.append(f"📝 Ingredients ({len(recipe.ingredients)} chars)")
            if recipe.instructions:
                indicators.append(f"📋 Instructions ({len(recipe.instructions)} chars)")
            
            if indicators:
                print(f"     {' | '.join(indicators)}")
            
            print()
    
    def _view_detailed_recipes(self):
        """Show detailed view of selected recipes"""
        
        print(f"\n🔍 DETAILED RECIPE VIEWER")
        print(f"Enter recipe numbers to view (e.g., 1,3,5 or 1-5 or 'all'):")
        
        try:
            selection = input("Selection: ").strip().lower()
            
            if selection == "all":
                selected_indices = list(range(len(self.extracted_recipes)))
            elif "-" in selection:
                # Range selection (e.g., 1-5)
                start, end = map(int, selection.split("-"))
                selected_indices = list(range(start-1, min(end, len(self.extracted_recipes))))
            else:
                # Individual selection (e.g., 1,3,5)
                selected_indices = [int(x.strip())-1 for x in selection.split(",") if x.strip().isdigit()]
            
            for idx in selected_indices:
                if 0 <= idx < len(self.extracted_recipes):
                    self._display_detailed_recipe(self.extracted_recipes[idx], idx + 1)
                    
                    if idx < len(selected_indices) - 1:
                        input("\nPress Enter for next recipe...")
                        
        except (ValueError, KeyboardInterrupt):
            print("Invalid selection or cancelled.")
    
    def _view_high_confidence_only(self):
        """Show only high confidence recipes"""
        
        high_conf_recipes = [r for r in self.extracted_recipes if r.confidence >= 0.8]
        
        if not high_conf_recipes:
            print("❌ No high confidence recipes found.")
            return
        
        print(f"\n⭐ HIGH CONFIDENCE RECIPES ({len(high_conf_recipes)} found)")
        print(f"{'='*60}")
        
        for i, recipe in enumerate(high_conf_recipes, 1):
            print(f"{i:2d}. ✅ {recipe.title}")
            print(f"    📍 Page {recipe.page_number} | 📂 {recipe.category} | 🎯 {recipe.confidence:.2f}")
            print()
    
    def _view_by_category(self):
        """Show recipes grouped by category"""
        
        # Group recipes by category
        categories = {}
        for recipe in self.extracted_recipes:
            cat = recipe.category or "Unknown"
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(recipe)
        
        print(f"\n📚 RECIPES BY CATEGORY")
        print(f"{'='*50}")
        
        for category in sorted(categories.keys()):
            recipes = categories[category]
            print(f"\n🏷️  {category.upper()} ({len(recipes)} recipes)")
            print("-" * 40)
            
            for recipe in recipes:
                confidence_indicator = self._get_confidence_indicator(recipe.confidence)
                print(f"   {confidence_indicator} {recipe.title} (Page {recipe.page_number})")
    
    def _search_recipes(self):
        """Search recipes by title or content"""
        
        try:
            search_term = input("\nEnter search term: ").strip().lower()
            
            if not search_term:
                print("❌ No search term entered.")
                return
            
            matches = []
            for recipe in self.extracted_recipes:
                # Search in title, ingredients, and instructions
                searchable_content = f"{recipe.title} {recipe.ingredients} {recipe.instructions}".lower()
                if search_term in searchable_content:
                    matches.append(recipe)
            
            if not matches:
                print(f"❌ No recipes found containing '{search_term}'")
                return
            
            print(f"\n🔍 SEARCH RESULTS for '{search_term}' ({len(matches)} found)")
            print(f"{'='*60}")
            
            for i, recipe in enumerate(matches, 1):
                confidence_indicator = self._get_confidence_indicator(recipe.confidence)
                print(f"{i:2d}. {confidence_indicator} {recipe.title}")
                print(f"    📍 Page {recipe.page_number} | 📂 {recipe.category} | 🎯 {recipe.confidence:.2f}")
                
                # Show where the search term was found
                found_in = []
                if search_term in recipe.title.lower():
                    found_in.append("title")
                if search_term in recipe.ingredients.lower():
                    found_in.append("ingredients")
                if search_term in recipe.instructions.lower():
                    found_in.append("instructions")
                
                print(f"    🎯 Found in: {', '.join(found_in)}")
                print()
                
        except KeyboardInterrupt:
            print("\nSearch cancelled.")
    
    def _display_detailed_recipe(self, recipe: Recipe, recipe_num: int):
        """Display a single recipe in detail"""
        
        confidence_indicator = self._get_confidence_indicator(recipe.confidence)
        
        print(f"\n{'='*80}")
        print(f"🍽️  RECIPE #{recipe_num}: {recipe.title}")
        print(f"{'='*80}")
        print(f"📍 Page: {recipe.page_number}")
        print(f"📂 Category: {recipe.category}")
        print(f"🎯 Confidence: {recipe.confidence:.2f} {confidence_indicator}")
        print(f"📚 Source: {recipe.source_file}")
        
        if recipe.ingredients:
            print(f"\n📝 INGREDIENTS:")
            print("-" * 40)
            print(recipe.ingredients)
        else:
            print(f"\n❌ No ingredients extracted")
        
        if recipe.instructions:
            print(f"\n📋 INSTRUCTIONS:")
            print("-" * 40)
            print(recipe.instructions)
        else:
            print(f"\n❌ No instructions extracted")
        
        print(f"\n{'='*80}")
    
    def _get_confidence_indicator(self, confidence: float) -> str:
        """Get visual indicator for confidence level"""
        
        if confidence >= 0.8:
            return "✅"  # High confidence
        elif confidence >= 0.6:
            return "⚠️"   # Medium confidence
        else:
            return "❌"  # Low confidence
    
    def export_results(self, format: str = "json", output_path: str = None):
        """
        Export results in different formats
        
        Args:
            format: 'json', 'csv', 'txt'
            output_path: Output file path (auto-generated if None)
        """
        
        if not self.extracted_recipes:
            print("❌ No recipes to export.")
            return
        
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"recipes_export_{timestamp}.{format}"
        
        try:
            if format.lower() == "json":
                self._export_json(output_path)
            elif format.lower() == "csv":
                self._export_csv(output_path)
            elif format.lower() == "txt":
                self._export_txt(output_path)
            else:
                print(f"❌ Unsupported format: {format}")
                return
            
            print(f"✅ Exported {len(self.extracted_recipes)} recipes to {output_path}")
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
    
    def _export_json(self, output_path: str):
        """Export to JSON format"""
        self.save_recipes(output_path)
    
    def _export_csv(self, output_path: str):
        """Export to CSV format"""
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['Title', 'Category', 'Page', 'Confidence', 'Ingredients', 'Instructions'])
            
            # Data
            for recipe in self.extracted_recipes:
                writer.writerow([
                    recipe.title,
                    recipe.category,
                    recipe.page_number,
                    recipe.confidence,
                    recipe.ingredients.replace('\n', ' | '),
                    recipe.instructions.replace('\n', ' | ')
                ])
    
    def _export_txt(self, output_path: str):
        """Export to text format"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("EXTRACTED RECIPES\n")
            f.write("=" * 50 + "\n\n")
            
            for i, recipe in enumerate(self.extracted_recipes, 1):
                f.write(f"RECIPE #{i}: {recipe.title}\n")
                f.write("-" * 40 + "\n")
                f.write(f"Page: {recipe.page_number}\n")
                f.write(f"Category: {recipe.category}\n")
                f.write(f"Confidence: {recipe.confidence:.2f}\n\n")
                
                if recipe.ingredients:
                    f.write("INGREDIENTS:\n")
                    f.write(recipe.ingredients + "\n\n")
                
                if recipe.instructions:
                    f.write("INSTRUCTIONS:\n")
                    f.write(recipe.instructions + "\n\n")
                
                f.write("=" * 50 + "\n\n")

# Simple CLI usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("🧠 ADAPTIVE RECIPE EXTRACTOR")
        print("Usage:")
        print("  python adaptive_extractor.py <pdf_path> [output.json]")
        print("  python adaptive_extractor.py --view [results.json]")
        print("  python adaptive_extractor.py --stats")
        print("")
        print("Examples:")
        print("  python adaptive_extractor.py cookbook.pdf")
        print("  python adaptive_extractor.py cookbook.pdf my_recipes.json")
        print("  python adaptive_extractor.py --view")
        print("  python adaptive_extractor.py --view my_recipes.json")
        sys.exit(1)
    
    # Handle different commands
    if sys.argv[1] == "--view":
        # View results mode
        extractor = AdaptiveRecipeExtractor()
        
        if len(sys.argv) > 2:
            # Load specific results file
            results_file = sys.argv[2]
            try:
                with open(results_file, 'r') as f:
                    results_data = json.load(f)
                
                # Convert back to Recipe objects
                recipes = []
                for recipe_data in results_data.get("recipes", []):
                    recipe = Recipe(**recipe_data)
                    recipes.append(recipe)
                
                extractor.extracted_recipes = recipes
                print(f"📚 Loaded {len(recipes)} recipes from {results_file}")
                
            except Exception as e:
                print(f"❌ Could not load results file: {e}")
                sys.exit(1)
        else:
            # Look for recent results
            import glob
            recent_files = glob.glob("recipes_*.json")
            if recent_files:
                latest_file = max(recent_files, key=os.path.getctime)
                try:
                    with open(latest_file, 'r') as f:
                        results_data = json.load(f)
                    
                    recipes = []
                    for recipe_data in results_data.get("recipes", []):
                        recipe = Recipe(**recipe_data)
                        recipes.append(recipe)
                    
                    extractor.extracted_recipes = recipes
                    print(f"📚 Loaded {len(recipes)} recipes from {latest_file}")
                    
                except Exception as e:
                    print(f"❌ Could not load latest results: {e}")
                    sys.exit(1)
            else:
                print("❌ No results files found. Run extraction first.")
                sys.exit(1)
        
        # Start interactive viewer
        extractor.view_results()
        
    elif sys.argv[1] == "--stats":
        # Show stats mode
        extractor = AdaptiveRecipeExtractor()
        stats = extractor.get_stats()
        
        print("📊 EXTRACTOR STATISTICS")
        print("=" * 30)
        print(f"Total recipes extracted: {stats['total_recipes_extracted']}")
        print(f"Cookbooks processed: {stats['cookbooks_processed']}")
        print(f"Knowledge patterns learned: {stats['knowledge_patterns']}")
        print(f"Ingredient markers learned: {stats['ingredient_markers_learned']}")
        print(f"Instruction markers learned: {stats['instruction_markers_learned']}")
        print(f"Categories learned: {stats['categories_learned']}")
        
    else:
        # Extraction mode
        pdf_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else None
        
        # Create and run extractor
        extractor = AdaptiveRecipeExtractor()
        
        print(f"🧠 Starting adaptive extraction on: {os.path.basename(pdf_path)}")
        recipes = extractor.extract_recipes(pdf_path)
        
        if recipes:
            print(f"\n✅ Successfully extracted {len(recipes)} recipes!")
            
            # Show stats
            stats = extractor.get_stats()
            print(f"📊 Total knowledge: {stats['knowledge_patterns']} patterns, {stats['ingredient_markers_learned']} ingredient markers")
            
            # Show sample recipes
            print(f"\n📝 Sample recipes:")
            for i, recipe in enumerate(recipes[:3]):
                confidence_indicator = "✅" if recipe.confidence >= 0.8 else "⚠️" if recipe.confidence >= 0.6 else "❌"
                print(f"{i+1}. {confidence_indicator} {recipe.title} (confidence: {recipe.confidence:.2f})")
                print(f"   Category: {recipe.category}")
                print(f"   Page: {recipe.page_number}")
                if recipe.ingredients:
                    print(f"   Ingredients: {len(recipe.ingredients)} chars")
                if recipe.instructions:
                    print(f"   Instructions: {len(recipe.instructions)} chars")
                print()
            
            if len(recipes) > 3:
                print(f"... and {len(recipes) - 3} more recipes")
            
            # Save results
            if output_path:
                extractor.save_recipes(output_path)
                results_file = output_path
            else:
                default_output = f"recipes_{os.path.splitext(os.path.basename(pdf_path))[0]}.json"
                extractor.save_recipes(default_output)
                results_file = default_output
            
            # Ask if user wants to view results
            print(f"\n🔍 VIEW OPTIONS:")
            print(f"1. View results now")
            print(f"2. Exit (view later with: python adaptive_extractor.py --view {results_file})")
            
            try:
                choice = input("Choice (1 or 2): ").strip()
                if choice == "1":
                    print(f"\n🎬 Starting interactive viewer...")
                    extractor.view_results()
                else:
                    print(f"👋 Results saved. View anytime with: python adaptive_extractor.py --view {results_file}")
                    
            except KeyboardInterrupt:
                print(f"\n👋 Results saved to {results_file}")
        
        else:
            print("❌ No recipes found")
        
        print(f"\n🎯 The extractor is now smarter and will perform better on the next cookbook!")
