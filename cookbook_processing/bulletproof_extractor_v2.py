#!/usr/bin/env python3
"""
🛡️ BULLETPROOF RECIPE EXTRACTOR - V2.0
=======================================
Complete rewrite based on quality audit findings
Zero tolerance for extraction artifacts
"""

import sys
import os
import re
import logging
import PyPDF2
import hashlib
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set
from pathlib import Path

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class BulletproofValidator:
    """Zero-tolerance validation system"""
    
    @staticmethod
    def validate_title(title: str) -> Dict:
        """Bulletproof title validation"""
        result = {'is_valid': False, 'issues': [], 'cleaned_title': ''}
        
        if not title:
            result['issues'].append('Empty title')
            return result
        
        title = title.strip()
        
        # CRITICAL REJECTION PATTERNS (based on audit findings)
        rejection_patterns = [
            r'^Start Cooking!$',
            r'^Before You Begin$',
            r'^PREPARE INGREDIENTS$',
            r'^ATK Recipe from Page \d+$',
            r'^(Dressing|Sauce|Topping|Filling)$',
            r'^[A-Z]{1,3}$',  # Very short all-caps
            r'ajar \(see photo',
            r'wi thout stirring',
            r'unti l skins',
            r'^BEGINNER$|^INTERMEDIATE$|^ADVANCED$',
            r'^VEGETARIAN$|^VEGAN$',
            r'^SERVES \d+$|^MAKES \d+$',
            r'^\d+ MINUTES?$|^\d+ HOURS?$',
            r'^FOR THE ',
            r'^INGREDIENTS$|^METHOD$|^STEPS$'
        ]
        
        for pattern in rejection_patterns:
            if re.search(pattern, title, re.IGNORECASE):
                result['issues'].append(f'Matches rejection pattern: {pattern}')
                return result
        
        # Length validation
        if len(title) < 4:
            result['issues'].append('Title too short')
            return result
        
        if len(title) > 100:
            result['issues'].append('Title too long')
            return result
        
        # Must contain letters
        if not re.search(r'[a-zA-Z]', title):
            result['issues'].append('No letters in title')
            return result
        
        # Check for food-related keywords (positive signals)
        food_keywords = [
            'soup', 'stew', 'roast', 'bread', 'cake', 'chicken', 'beef', 'pork', 'fish',
            'pasta', 'pizza', 'salad', 'sauce', 'cookies', 'pie', 'muffin', 'pancake',
            'eggs', 'omelet', 'rice', 'beans', 'cheese', 'butter', 'sandwich', 'burger',
            'tacos', 'curry', 'chili', 'smoothie', 'chocolate', 'vanilla', 'baked',
            'grilled', 'fried', 'roasted', 'steamed', 'braised', 'sauteed'
        ]
        
        has_food_keyword = any(keyword in title.lower() for keyword in food_keywords)
        
        # Title case validation
        is_proper_case = title.istitle() or (title.isupper() and has_food_keyword)
        
        if not has_food_keyword and not is_proper_case:
            result['issues'].append('Doesn\'t look like a recipe title')
            return result
        
        # Clean title
        cleaned = title
        if cleaned.isupper() and has_food_keyword:
            cleaned = cleaned.title()
        
        # Remove common artifacts
        cleaned = re.sub(r'^(Recipe|Test Kitchen|ATK)\s*[:-]?\s*', '', cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.strip()
        
        result['is_valid'] = True
        result['cleaned_title'] = cleaned
        return result
    
    @staticmethod
    def validate_ingredients(ingredients: str) -> Dict:
        """Bulletproof ingredient validation"""
        result = {'is_valid': False, 'issues': [], 'measurement_count': 0}
        
        if not ingredients:
            result['issues'].append('Empty ingredients')
            return result
        
        ingredients = ingredients.strip()
        
        # Minimum length requirement
        if len(ingredients) < 15:
            result['issues'].append('Ingredients too short')
            return result
        
        # Reject if contains extraction artifacts
        rejection_patterns = [
            r'START COOKING!',
            r'PREPARE INGREDIENTS',
            r'BEFORE YOU BEGIN',
            r'BEGINNER|INTERMEDIATE|ADVANCED'
        ]
        
        for pattern in rejection_patterns:
            if re.search(pattern, ingredients, re.IGNORECASE):
                result['issues'].append(f'Contains extraction artifact: {pattern}')
                return result
        
        # Check for measurement patterns (REQUIRED)
        measurement_patterns = [
            r'\d+\s*(cup|tablespoon|teaspoon|pound|ounce|tbsp|tsp|lb|oz)',
            r'[⅛⅜⅝⅞¼¾½⅓⅔]\s*(cup|tablespoon|teaspoon|pound|ounce)',
            r'\d+[⅛⅜⅝⅞¼¾½⅓⅔]\s*(cup|tablespoon|teaspoon|pound|ounce)',
            r'\d+\s*(large|medium|small)',
            r'\d+\s*(chopped|diced|minced|sliced|grated)'
        ]
        
        measurement_count = 0
        for pattern in measurement_patterns:
            matches = re.findall(pattern, ingredients, re.IGNORECASE)
            measurement_count += len(matches)
        
        result['measurement_count'] = measurement_count
        
        if measurement_count == 0:
            result['issues'].append('No measurements detected')
            return result
        
        result['is_valid'] = True
        return result
    
    @staticmethod
    def validate_instructions(instructions: str) -> Dict:
        """Bulletproof instruction validation"""
        result = {'is_valid': False, 'issues': [], 'step_count': 0, 'cooking_verb_count': 0}
        
        if not instructions:
            result['issues'].append('Empty instructions')
            return result
        
        instructions = instructions.strip()
        
        # Minimum length requirement
        if len(instructions) < 20:
            result['issues'].append('Instructions too short')
            return result
        
        # Reject if contains extraction artifacts
        rejection_patterns = [
            r'^INGREDIENTS',
            r'^BEFORE YOU BEGIN',
            r'^PREPARE INGREDIENTS',
            r'START COOKING!.*END OF RECIPE'
        ]
        
        for pattern in rejection_patterns:
            if re.search(pattern, instructions, re.IGNORECASE | re.MULTILINE):
                result['issues'].append(f'Contains extraction artifact: {pattern}')
                return result
        
        # Check for numbered steps (REQUIRED)
        numbered_steps = re.findall(r'^\d+\.\s+', instructions, re.MULTILINE)
        result['step_count'] = len(numbered_steps)
        
        if len(numbered_steps) == 0:
            result['issues'].append('No numbered steps found')
            return result
        
        # Check for cooking verbs (REQUIRED)
        cooking_verbs = [
            'heat', 'cook', 'bake', 'mix', 'stir', 'add', 'combine', 'whisk',
            'season', 'transfer', 'drain', 'serve', 'blend', 'chop', 'dice',
            'slice', 'sauté', 'fry', 'boil', 'simmer', 'roast', 'grill'
        ]
        
        cooking_verb_count = sum(1 for verb in cooking_verbs if verb in instructions.lower())
        result['cooking_verb_count'] = cooking_verb_count
        
        if cooking_verb_count == 0:
            result['issues'].append('No cooking verbs found')
            return result
        
        result['is_valid'] = True
        return result
    
    @staticmethod
    def validate_recipe_completeness(recipe_data: Dict) -> Dict:
        """Overall recipe completeness validation"""
        result = {
            'is_valid': False,
            'quality_score': 0,
            'core_issues': [],
            'bonus_points': 0,
            'field_validations': {}
        }
        
        # Core requirement 1: Valid title
        title_validation = BulletproofValidator.validate_title(recipe_data.get('title', ''))
        result['field_validations']['title'] = title_validation
        
        if not title_validation['is_valid']:
            result['core_issues'].extend([f"Title: {issue}" for issue in title_validation['issues']])
            return result  # Fail immediately if title is invalid
        
        result['quality_score'] += 2  # Title is worth 2 points
        
        # Core requirement 2: Valid ingredients
        ingredient_validation = BulletproofValidator.validate_ingredients(recipe_data.get('ingredients', ''))
        result['field_validations']['ingredients'] = ingredient_validation
        
        if not ingredient_validation['is_valid']:
            result['core_issues'].extend([f"Ingredients: {issue}" for issue in ingredient_validation['issues']])
            return result  # Fail immediately if ingredients are invalid
        
        result['quality_score'] += 3  # Ingredients worth 3 points
        
        # Core requirement 3: Valid instructions
        instruction_validation = BulletproofValidator.validate_instructions(recipe_data.get('instructions', ''))
        result['field_validations']['instructions'] = instruction_validation
        
        if not instruction_validation['is_valid']:
            result['core_issues'].extend([f"Instructions: {issue}" for issue in instruction_validation['issues']])
            return result  # Fail immediately if instructions are invalid
        
        result['quality_score'] += 3  # Instructions worth 3 points
        
        # Core requirement 4: Category (can be auto-generated)
        if recipe_data.get('category'):
            result['quality_score'] += 1
        else:
            # Auto-generate category based on difficulty or source
            difficulty = recipe_data.get('difficulty', '')
            if difficulty:
                recipe_data['category'] = f"{difficulty.title()} Recipe"
                result['quality_score'] += 1
            else:
                recipe_data['category'] = "Recipe"  # Default
                result['quality_score'] += 1
        
        # Bonus fields
        bonus_fields = ['servings', 'total_time', 'description']
        for field in bonus_fields:
            if recipe_data.get(field):
                result['bonus_points'] += 1
        
        result['quality_score'] += result['bonus_points']
        
        # Recipe is valid if it passes all core requirements (minimum 9 points: 2+3+3+1)
        result['is_valid'] = len(result['core_issues']) == 0 and result['quality_score'] >= 9
        
        return result

class BulletproofExtractor:
    """Extraction system with zero tolerance for artifacts"""
    
    def __init__(self, pdf_path: str, cookbook_config: Dict):
        self.pdf_path = pdf_path
        self.config = cookbook_config
        self.extracted_recipes = []
        self.rejected_content = []
        self.extraction_stats = {
            'pages_processed': 0,
            'pages_skipped': 0,
            'potential_recipes_found': 0,
            'recipes_validated': 0,
            'recipes_rejected': 0,
            'rejection_reasons': {},
            'quality_scores': []
        }
    
    def extract_with_bulletproof_validation(self, max_recipes: Optional[int] = None) -> List[Dict]:
        """Main extraction with bulletproof validation"""
        print(f"🛡️ BULLETPROOF EXTRACTION: {self.config['title']}")
        print("=" * 70)
        print("🎯 ZERO TOLERANCE for extraction artifacts")
        print()
        
        try:
            with open(self.pdf_path, 'rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                total_pages = len(reader.pages)
                
                print(f"📄 Processing {total_pages} pages with bulletproof validation...")
                
                for page_num in range(total_pages):
                    if max_recipes and self.extraction_stats['recipes_validated'] >= max_recipes:
                        break
                    
                    try:
                        page = reader.pages[page_num]
                        text = page.extract_text()
                        
                        self.extraction_stats['pages_processed'] += 1
                        
                        # Check if page has recipe potential
                        if self._has_recipe_potential(text):
                            potential_recipe = self._extract_potential_recipe(text, page_num + 1)
                            
                            if potential_recipe:
                                self.extraction_stats['potential_recipes_found'] += 1
                                
                                # BULLETPROOF VALIDATION
                                validation = BulletproofValidator.validate_recipe_completeness(potential_recipe)
                                potential_recipe['validation'] = validation
                                
                                if validation['is_valid']:
                                    # Additional safety checks
                                    if self._pass_safety_checks(potential_recipe):
                                        self.extracted_recipes.append(potential_recipe)
                                        self.extraction_stats['recipes_validated'] += 1
                                        self.extraction_stats['quality_scores'].append(validation['quality_score'])
                                        
                                        print(f"✅ Recipe {self.extraction_stats['recipes_validated']}: {potential_recipe['title'][:50]}...")
                                    else:
                                        self._reject_recipe(potential_recipe, 'Failed safety checks')
                                else:
                                    self._reject_recipe(potential_recipe, validation['core_issues'])
                        else:
                            self.extraction_stats['pages_skipped'] += 1
                    
                    except Exception as e:
                        print(f"❌ Error processing page {page_num + 1}: {e}")
                        continue
        
        except Exception as e:
            print(f"❌ Fatal error during extraction: {e}")
            raise
        
        self._print_bulletproof_summary()
        return self.extracted_recipes
    
    def _has_recipe_potential(self, page_text: str) -> bool:
        """Strict recipe potential detection"""
        if not page_text or len(page_text.strip()) < 50:
            return False
        
        # Use cookbook-specific patterns
        if self.config['type'] == 'atk_25th':
            return self._detect_atk_25th_recipe(page_text)
        elif self.config['type'] == 'atk_teen':
            return self._detect_atk_teen_recipe(page_text)
        else:
            return self._detect_generic_recipe(page_text)
    
    def _detect_atk_25th_recipe(self, page_text: str) -> bool:
        """ATK 25th Anniversary specific detection"""
        score = 0
        
        # Strong positive indicators
        if re.search(r'(SERVES|MAKES)\s+\d+', page_text):
            score += 3
        
        if re.search(r'\d+\s*(MINUTES|HOURS)', page_text):
            score += 2
        
        # Numbered steps
        if re.search(r'^\d+\.\s+', page_text, re.MULTILINE):
            score += 3
        
        # Measurement patterns
        measurement_count = len(re.findall(r'\d+\s*(cup|tablespoon|teaspoon|pound|ounce)', page_text, re.IGNORECASE))
        score += min(measurement_count, 3)
        
        # Negative indicators (reject immediately)
        negative_patterns = [
            r'Table of Contents',
            r'Index',
            r'Page \d+ of \d+',
            r'Copyright \d{4}',
            r'Introduction',
            r'Acknowledgments'
        ]
        
        for pattern in negative_patterns:
            if re.search(pattern, page_text, re.IGNORECASE):
                return False
        
        return score >= 5
    
    def _detect_atk_teen_recipe(self, page_text: str) -> bool:
        """ATK Teen specific detection"""
        score = 0
        
        # Strong indicators for teen cookbook
        if re.search(r'(BEGINNER|INTERMEDIATE|ADVANCED)', page_text):
            score += 4
        
        if 'START COOKING!' in page_text:
            score += 3
        
        if 'PREPARE INGREDIENTS' in page_text:
            score += 2
        
        if re.search(r'(SERVES|MAKES)\s+\d+', page_text):
            score += 2
        
        # Measurement patterns
        measurement_count = len(re.findall(r'\d+\s*(cup|tablespoon|teaspoon)', page_text, re.IGNORECASE))
        score += min(measurement_count, 2)
        
        return score >= 6
    
    def _detect_generic_recipe(self, page_text: str) -> bool:
        """Generic recipe detection"""
        # Basic recipe indicators
        has_ingredients = bool(re.search(r'\d+\s*(cup|tablespoon|teaspoon|pound|ounce)', page_text, re.IGNORECASE))
        has_steps = bool(re.search(r'^\d+\.\s+', page_text, re.MULTILINE))
        has_cooking_words = any(word in page_text.lower() for word in ['heat', 'cook', 'bake', 'mix', 'stir'])
        
        return has_ingredients and (has_steps or has_cooking_words)
    
    def _extract_potential_recipe(self, page_text: str, page_number: int) -> Optional[Dict]:
        """Extract potential recipe using cookbook-specific logic"""
        recipe_data = {
            'page_number': page_number,
            'source': self.config['source_name'],
            'extraction_timestamp': datetime.now().isoformat(),
            'extraction_method': f"bulletproof_{self.config['type']}"
        }
        
        try:
            if self.config['type'] == 'atk_25th':
                return self._extract_atk_25th_recipe(page_text, recipe_data)
            elif self.config['type'] == 'atk_teen':
                return self._extract_atk_teen_recipe(page_text, recipe_data)
            else:
                return self._extract_generic_recipe(page_text, recipe_data)
        
        except Exception as e:
            print(f"❌ Extraction error on page {page_number}: {e}")
            return None
    
    def _extract_atk_25th_recipe(self, page_text: str, recipe_data: Dict) -> Dict:
        """Extract ATK 25th Anniversary recipe with strict validation"""
        
        # Extract title using bulletproof method
        title = self._extract_bulletproof_title(page_text, 'atk_25th')
        recipe_data['title'] = title
        
        # Extract other components
        recipe_data['ingredients'] = self._extract_bulletproof_ingredients(page_text, 'atk_25th')
        recipe_data['instructions'] = self._extract_bulletproof_instructions(page_text, 'atk_25th')
        
        # Extract metadata
        self._extract_metadata(page_text, recipe_data, 'atk_25th')
        
        return recipe_data
    
    def _extract_atk_teen_recipe(self, page_text: str, recipe_data: Dict) -> Dict:
        """Extract ATK Teen recipe with strict validation"""
        
        # Extract title using bulletproof method
        title = self._extract_bulletproof_title(page_text, 'atk_teen')
        recipe_data['title'] = title
        
        # Extract other components  
        recipe_data['ingredients'] = self._extract_bulletproof_ingredients(page_text, 'atk_teen')
        recipe_data['instructions'] = self._extract_bulletproof_instructions(page_text, 'atk_teen')
        
        # Extract metadata
        self._extract_metadata(page_text, recipe_data, 'atk_teen')
        
        return recipe_data
    
    def _extract_bulletproof_title(self, page_text: str, cookbook_type: str) -> str:
        """Bulletproof title extraction"""
        lines = page_text.split('\n')
        
        for i, line in enumerate(lines[:20]):  # Check first 20 lines
            line = line.strip()
            if not line:
                continue
            
            # Pre-validate with bulletproof validator
            title_validation = BulletproofValidator.validate_title(line)
            if title_validation['is_valid']:
                return title_validation['cleaned_title']
        
        # Fallback: try to construct title from content
        food_words = []
        for line in lines[:15]:
            if re.search(r'(chicken|beef|pork|fish|soup|salad|cake|bread)', line, re.IGNORECASE):
                words = re.findall(r'\b[A-Za-z]+\b', line)
                food_words.extend([w for w in words if len(w) > 3])
        
        if food_words:
            return f"Recipe with {' '.join(food_words[:3]).title()}"
        
        return f"Recipe from Page {page_text.split()[0] if page_text.split() else 'Unknown'}"
    
    def _extract_bulletproof_ingredients(self, page_text: str, cookbook_type: str) -> str:
        """Bulletproof ingredient extraction"""
        if cookbook_type == 'atk_teen':
            # Look for PREPARE INGREDIENTS section
            prepare_match = re.search(r'PREPARE INGREDIENTS(.*?)(?=START COOKING!|$)', page_text, re.DOTALL)
            if prepare_match:
                ingredients_text = prepare_match.group(1).strip()
            else:
                return ""
        else:
            # ATK 25th or generic - find content with measurements
            ingredients_text = page_text
        
        # Extract lines with measurements
        lines = ingredients_text.split('\n')
        ingredient_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line has measurement pattern
            if re.search(r'\d+\s*(cup|tablespoon|teaspoon|pound|ounce|tbsp|tsp|lb|oz)', line, re.IGNORECASE):
                ingredient_lines.append(f"• {line}")
            elif re.search(r'[⅛⅜⅝⅞¼¾½⅓⅔]\s*(cup|tablespoon|teaspoon)', line, re.IGNORECASE):
                ingredient_lines.append(f"• {line}")
        
        result = '\n'.join(ingredient_lines)
        
        # Validate before returning
        validation = BulletproofValidator.validate_ingredients(result)
        if validation['is_valid']:
            return result
        else:
            return ""
    
    def _extract_bulletproof_instructions(self, page_text: str, cookbook_type: str) -> str:
        """Bulletproof instruction extraction"""
        if cookbook_type == 'atk_teen':
            # Look for START COOKING! section
            instructions_match = re.search(r'START COOKING!(.*?)(?=\n[A-Z\s]{10,}|$)', page_text, re.DOTALL)
            if instructions_match:
                instructions_text = instructions_match.group(1).strip()
            else:
                return ""
        else:
            # ATK 25th or generic - find numbered steps
            instructions_text = page_text
        
        # Extract numbered steps
        lines = instructions_text.split('\n')
        instruction_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line starts with number
            if re.match(r'^\d+\.\s+', line):
                instruction_lines.append(line)
        
        result = '\n'.join(instruction_lines)
        
        # Validate before returning
        validation = BulletproofValidator.validate_instructions(result)
        if validation['is_valid']:
            return result
        else:
            return ""
    
    def _extract_metadata(self, page_text: str, recipe_data: Dict, cookbook_type: str):
        """Extract metadata with validation"""
        
        # Servings/yield
        yield_match = re.search(r'(SERVES|MAKES)\s+(\d+)\s*(?:TO\s+(\d+))?\s*([A-Z\s]*)', page_text, re.IGNORECASE)
        if yield_match:
            yield_text = f"{yield_match.group(1).title()} {yield_match.group(2)}"
            if yield_match.group(3):
                yield_text += f" to {yield_match.group(3)}"
            if yield_match.group(4) and yield_match.group(4).strip():
                yield_text += f" {yield_match.group(4).strip().lower()}"
            recipe_data['servings'] = yield_text
        
        # Timing
        time_match = re.search(r'(\d+)\s+(HOUR|MINUTE)S?\s*(?:\(?(plus|and|total)?\s*([^)]+)\)?)?', page_text, re.IGNORECASE)
        if time_match:
            time_str = f"{time_match.group(1)} {time_match.group(2).lower()}s"
            if time_match.group(4):
                time_str += f" ({time_match.group(4).strip()})"
            recipe_data['total_time'] = time_str
        
        # Difficulty (ATK Teen)
        if cookbook_type == 'atk_teen':
            difficulty_match = re.search(r'(BEGINNER|INTERMEDIATE|ADVANCED)', page_text)
            if difficulty_match:
                recipe_data['difficulty'] = difficulty_match.group(1)
                recipe_data['category'] = f"{difficulty_match.group(1).title()} Recipe"
    
    def _pass_safety_checks(self, recipe_data: Dict) -> bool:
        """Additional safety checks beyond validation"""
        
        # Check for suspicious duplicate patterns
        title = recipe_data.get('title', '')
        if title.count('(') > 2 or title.count('Book') > 1:
            return False
        
        # Check ingredient/instruction ratio
        ingredients_len = len(recipe_data.get('ingredients', ''))
        instructions_len = len(recipe_data.get('instructions', ''))
        
        if ingredients_len > 0 and instructions_len > 0:
            ratio = instructions_len / ingredients_len
            if ratio < 0.5 or ratio > 10:  # Suspicious ratios
                return False
        
        # Content hash check for exact duplicates
        content_hash = self._create_content_hash(recipe_data)
        recipe_data['content_hash'] = content_hash
        
        # Check if we've seen this exact content before
        existing_hashes = [r.get('content_hash') for r in self.extracted_recipes]
        if content_hash in existing_hashes:
            return False
        
        return True
    
    def _create_content_hash(self, recipe_data: Dict) -> str:
        """Create content hash for duplicate detection"""
        content = f"{recipe_data.get('title', '')}{recipe_data.get('ingredients', '')[:100]}{recipe_data.get('instructions', '')[:100]}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _reject_recipe(self, recipe_data: Dict, reasons: List[str]):
        """Record rejected recipe with reasons"""
        self.extraction_stats['recipes_rejected'] += 1
        
        for reason in reasons if isinstance(reasons, list) else [reasons]:
            self.extraction_stats['rejection_reasons'][reason] = self.extraction_stats['rejection_reasons'].get(reason, 0) + 1
        
        self.rejected_content.append({
            'page_number': recipe_data.get('page_number'),
            'title': recipe_data.get('title', 'Unknown')[:50],
            'reasons': reasons,
            'timestamp': datetime.now().isoformat()
        })
    
    def _print_bulletproof_summary(self):
        """Print comprehensive extraction summary"""
        stats = self.extraction_stats
        
        print(f"\n🛡️ BULLETPROOF EXTRACTION SUMMARY")
        print("=" * 70)
        print(f"📄 Pages processed: {stats['pages_processed']:,}")
        print(f"📄 Pages skipped: {stats['pages_skipped']:,}")
        print(f"🔍 Potential recipes found: {stats['potential_recipes_found']:,}")
        print(f"✅ Recipes validated: {stats['recipes_validated']:,}")
        print(f"❌ Recipes rejected: {stats['recipes_rejected']:,}")
        
        if stats['recipes_validated'] > 0:
            success_rate = (stats['recipes_validated'] / stats['potential_recipes_found']) * 100
            print(f"📊 Validation success rate: {success_rate:.1f}%")
            
            avg_quality = sum(stats['quality_scores']) / len(stats['quality_scores'])
            print(f"⭐ Average quality score: {avg_quality:.1f}/10")
        
        if stats['rejection_reasons']:
            print(f"\n❌ TOP REJECTION REASONS:")
            sorted_reasons = sorted(stats['rejection_reasons'].items(), key=lambda x: x[1], reverse=True)
            for reason, count in sorted_reasons[:5]:
                print(f"   • {reason}: {count} times")
        
        print(f"\n✅ EXTRACTION QUALITY: {'EXCELLENT' if stats['recipes_rejected'] == 0 else 'GOOD' if stats['recipes_validated'] > stats['recipes_rejected'] else 'NEEDS IMPROVEMENT'}")

# Cookbook configurations
COOKBOOK_CONFIGS = {
    'atk_25th': {
        'type': 'atk_25th',
        'title': "America's Test Kitchen 25th Anniversary",
        'source_name': "America's Test Kitchen 25th Anniversary",
        'pdf_path': r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
    },
    'atk_teen': {
        'type': 'atk_teen',
        'title': "ATK Teen Cookbook",
        'source_name': "The Complete Cookbook for Teen - America's Test Kitchen Kids",
        'pdf_path': r"D:\Mik\Downloads\Me Hungie\cookbook_processing\The Complete Cookbook for Teen - America's Test Kitchen Kids.pdf"
    }
}

def main():
    """Main function to run bulletproof extraction"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Bulletproof Recipe Extractor V2.0')
    parser.add_argument('--cookbook', choices=['atk_25th', 'atk_teen'], required=True, help='Cookbook to extract')
    parser.add_argument('--max-recipes', type=int, help='Maximum recipes to extract (for testing)')
    parser.add_argument('--test-mode', action='store_true', help='Run in test mode (no database save)')
    
    args = parser.parse_args()
    
    config = COOKBOOK_CONFIGS[args.cookbook]
    
    if not os.path.exists(config['pdf_path']):
        print(f"❌ PDF not found: {config['pdf_path']}")
        return
    
    print(f"🚀 BULLETPROOF EXTRACTOR V2.0")
    print(f"📚 Target: {config['title']}")
    print(f"🛡️ Zero tolerance for extraction artifacts")
    print()
    
    # Create extractor
    extractor = BulletproofExtractor(config['pdf_path'], config)
    
    # Extract recipes
    recipes = extractor.extract_with_bulletproof_validation(max_recipes=args.max_recipes)
    
    print(f"\n🎉 BULLETPROOF EXTRACTION COMPLETE!")
    print(f"📊 Final result: {len(recipes)} VALIDATED recipes extracted")
    
    if args.test_mode:
        print(f"🧪 Test mode: No database operations performed")
    else:
        print(f"💾 Ready for database insertion (manual step)")

if __name__ == "__main__":
    main()
