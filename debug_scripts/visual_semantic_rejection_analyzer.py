#!/usr/bin/env python3
"""
Visual + Semantic Rejection Analyzer
Detailed analysis of what's being rejected and why
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
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RejectionAnalyzer:
    """Analyzes what's being rejected and provides detailed feedback"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.semantic_engine = SemanticRecipeEngine(ValidationLevel.STRICT)
        self.rejection_details = []
        
    def analyze_pages(self, start_page: int = 1, end_page: int = 10):
        """Analyze a range of pages to understand rejection patterns"""
        
        logger.info(f"🔍 ANALYZING REJECTION PATTERNS (Pages {start_page}-{end_page})")
        logger.info("=" * 70)
        
        try:
            with open(self.pdf_path, 'rb') as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                total_pages = len(reader.pages)
                
                start_idx = start_page - 1
                end_idx = min(end_page, total_pages)
                
                for page_num in range(start_idx, end_idx):
                    try:
                        page = reader.pages[page_num]
                        text = page.extract_text()
                        
                        if not text or len(text.strip()) < 50:
                            self._log_rejection(page_num + 1, "EMPTY_PAGE", "Page has no text or too little content", text[:100])
                            continue
                        
                        # Analyze visual structure
                        structure = self._analyze_page_structure(text)
                        
                        if not structure['has_recipe']:
                            reason = self._determine_visual_rejection_reason(text, structure)
                            self._log_rejection(page_num + 1, "NO_VISUAL_STRUCTURE", reason, text[:200])
                            continue
                        
                        # Try to extract title
                        title = self._extract_title_with_debug(text, structure)
                        if not title:
                            self._log_rejection(page_num + 1, "NO_TITLE", "Could not extract valid title", text[:300])
                            continue
                        
                        # Try to extract ingredients
                        ingredients = self._extract_ingredients_with_debug(text, structure)
                        if not ingredients:
                            self._log_rejection(page_num + 1, "NO_INGREDIENTS", f"Title: '{title}' but no ingredients found", text[:400])
                            continue
                        
                        # Try to extract instructions
                        instructions = self._extract_instructions_with_debug(text, structure)
                        if not instructions and structure['confidence_score'] < 8:
                            self._log_rejection(page_num + 1, "NO_INSTRUCTIONS", f"Title: '{title}', has ingredients but no instructions", text[:400])
                            continue
                        
                        # Semantic validation
                        semantic_result = self.semantic_engine.validate_complete_recipe({
                            'title': title,
                            'ingredients': ingredients,
                            'instructions': instructions or "Placeholder instructions"
                        })
                        
                        if not semantic_result.is_valid_recipe or semantic_result.confidence_score < 0.7:
                            self._log_rejection(page_num + 1, "SEMANTIC_REJECTION", 
                                              f"Title: '{title}', Semantic errors: {semantic_result.validation_errors}", 
                                              f"Confidence: {semantic_result.confidence_score}")
                            continue
                        
                        # Success!
                        logger.info(f"✅ Page {page_num + 1}: SUCCESS - '{title}' (visual: {structure['confidence_score']}, semantic: {semantic_result.confidence_score:.2f})")
                        
                    except Exception as e:
                        self._log_rejection(page_num + 1, "PROCESSING_ERROR", f"Error: {e}", "")
                        continue
        
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
            raise
        
        self._print_rejection_summary()
    
    def _log_rejection(self, page_num: int, category: str, reason: str, sample_text: str):
        """Log detailed rejection information"""
        rejection = {
            'page': page_num,
            'category': category,
            'reason': reason,
            'sample_text': sample_text
        }
        self.rejection_details.append(rejection)
        
        logger.debug(f"🚫 Page {page_num}: {category} - {reason}")
        if sample_text:
            logger.debug(f"   Sample: {sample_text[:150]}...")
    
    def _determine_visual_rejection_reason(self, text: str, structure: Dict) -> str:
        """Determine specific reason for visual structure rejection"""
        reasons = []
        
        if structure['confidence_score'] < 3:
            reasons.append(f"Very low confidence score ({structure['confidence_score']})")
        
        if not structure['title_candidates']:
            reasons.append("No title candidates found")
        
        # Check for specific content patterns
        if 'SERVES' not in text and 'MAKES' not in text:
            reasons.append("No serving information")
        
        if not re.search(r'\d+\s*(cup|tablespoon|teaspoon|pound|ounce)', text, re.IGNORECASE):
            reasons.append("No measurement patterns")
        
        if not re.search(r'^\d+\.', text, re.MULTILINE):
            reasons.append("No numbered steps")
        
        # Check for non-recipe content indicators
        non_recipe_indicators = [
            'why this recipe works', 'test kitchen', 'equipment corner',
            'science experiment', 'tasting', 'rating', 'shopping'
        ]
        
        text_lower = text.lower()
        for indicator in non_recipe_indicators:
            if indicator in text_lower:
                reasons.append(f"Contains '{indicator}' (non-recipe content)")
        
        return "; ".join(reasons) if reasons else "Unknown visual rejection"
    
    def _extract_title_with_debug(self, page_text: str, structure: Dict) -> Optional[str]:
        """Debug version of title extraction"""
        # Use visual structure's title candidates
        title_candidates = structure['title_candidates']
        
        logger.debug(f"   Title candidates found: {len(title_candidates)}")
        for i, candidate in enumerate(title_candidates[:3]):
            logger.debug(f"     {i+1}. '{candidate['text']}' (confidence: {candidate['confidence']})")
        
        # Sort by confidence and position
        title_candidates.sort(key=lambda x: (x['confidence'], -x['position']), reverse=True)
        
        for candidate in title_candidates:
            candidate_text = candidate['text']
            
            # Test with semantic engine
            if self.semantic_engine._is_recipe_title(candidate_text):
                cleaned_title = self._clean_title(candidate_text)
                if cleaned_title and len(cleaned_title) > 3:
                    logger.debug(f"   ✅ Selected title: '{cleaned_title}'")
                    return cleaned_title
                else:
                    logger.debug(f"   🚫 Title cleaned to invalid: '{cleaned_title}'")
            else:
                logger.debug(f"   🚫 Failed semantic title test: '{candidate_text}'")
        
        logger.debug(f"   🚫 No valid titles found from {len(title_candidates)} candidates")
        return None
    
    def _extract_ingredients_with_debug(self, page_text: str, structure: Dict) -> Optional[str]:
        """Debug version of ingredient extraction"""
        
        # Check for PREPARE INGREDIENTS section
        if 'PREPARE INGREDIENTS' in structure['recipe_sections']:
            logger.debug(f"   Found PREPARE INGREDIENTS section")
            prepare_pos = page_text.find('PREPARE INGREDIENTS')
            content_after_prepare = page_text[prepare_pos + len('PREPARE INGREDIENTS'):].strip()
            
            start_cooking_pos = content_after_prepare.find('START COOKING!')
            if start_cooking_pos != -1:
                ingredients_text = content_after_prepare[:start_cooking_pos].strip()
                logger.debug(f"   Extracted from PREPARE section (until START COOKING): {len(ingredients_text)} chars")
            else:
                ingredients_text = content_after_prepare[:1000].strip()
                logger.debug(f"   Extracted from PREPARE section (first 1000 chars): {len(ingredients_text)} chars")
        else:
            logger.debug(f"   No PREPARE INGREDIENTS section, trying pattern detection")
            ingredients_text = self._extract_ingredients_by_patterns_debug(page_text)
        
        if not ingredients_text:
            logger.debug(f"   🚫 No ingredients extracted")
            return None
        
        # Format ingredients properly
        formatted = self._format_ingredients(ingredients_text)
        logger.debug(f"   ✅ Ingredients found: {len(formatted)} chars, {len(formatted.split('•'))-1} items")
        return formatted
    
    def _extract_ingredients_by_patterns_debug(self, page_text: str) -> str:
        """Debug version of pattern-based ingredient extraction"""
        lines = page_text.split('\n')
        ingredient_lines = []
        
        measurement_patterns = [
            r'^\d+\s*\(\d+.*?ounce\)',
            r'^\d+\s*(cup|tablespoon|teaspoon|pound|ounce|tbsp|tsp|lb|oz)\s',
            r'^\d+.*?(large|medium|small|whole)\s',
            r'^\d+.*?(chopped|diced|minced|sliced|grated|stemmed|seeded)',
            r'^(\d+/\d+|\d+\.\d+)\s*(cup|tablespoon|teaspoon)',
            r'^\d+\s*(cloves?|cans?|packages?|pounds?|ounces?|slices?)\s',
            r'^[¾½¼⅓⅔⅛]',
        ]
        
        matches_found = 0
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            # Check for measurement patterns
            is_ingredient = any(re.search(pattern, line, re.IGNORECASE) for pattern in measurement_patterns)
            
            if is_ingredient:
                # Additional validation
                if not any(word in line.lower() for word in ['cook', 'heat', 'process', 'transfer', 'minutes']):
                    ingredient_lines.append(line)
                    matches_found += 1
        
        logger.debug(f"   Pattern matching found {matches_found} ingredient lines")
        return '\n'.join(ingredient_lines) if len(ingredient_lines) >= 3 else ""
    
    def _extract_instructions_with_debug(self, page_text: str, structure: Dict) -> Optional[str]:
        """Debug version of instruction extraction"""
        
        if 'START COOKING!' in structure['recipe_sections']:
            logger.debug(f"   Found START COOKING! section")
            start_pos = page_text.find('START COOKING!')
            instructions_text = page_text[start_pos + len('START COOKING!'):].strip()
            parsed = self._parse_numbered_instructions(instructions_text)
            logger.debug(f"   Parsed {len(parsed.split('\\n')) if parsed else 0} instruction steps")
            return parsed
        else:
            logger.debug(f"   No START COOKING! section, looking for numbered steps")
            steps = self._extract_numbered_steps_debug(page_text)
            return steps
    
    def _extract_numbered_steps_debug(self, page_text: str) -> str:
        """Debug version of numbered step extraction"""
        lines = page_text.split('\n')
        steps = []
        
        for line in lines:
            line = line.strip()
            step_match = re.match(r'^(\d+)\.\s*(.+)', line)
            if step_match and len(step_match.group(2)) > 20:
                steps.append(line)
        
        logger.debug(f"   Found {len(steps)} numbered steps")
        return '\n'.join(steps) if len(steps) >= 2 else ""
    
    def _analyze_page_structure(self, page_text: str) -> Dict:
        """Simplified visual structure analysis for debugging"""
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
        
        score = 0
        
        # ATK-specific headers
        atk_headers = ['PREPARE INGREDIENTS', 'START COOKING!', 'BEFORE YOU BEGIN']
        for header in atk_headers:
            if header in page_text:
                structure['recipe_sections'].append(header)
                score += 3
        
        # Recipe metadata patterns
        metadata_patterns = [
            (r'(SERVES|MAKES)\s+\d+', 2),
            (r'\d+\s+(MINUTES|HOURS)', 2),
            (r'(BEGINNER|INTERMEDIATE|ADVANCED)', 2),
            (r'(VEGETARIAN|VEGAN|GLUTEN-FREE)', 1)
        ]
        
        for pattern, points in metadata_patterns:
            if re.search(pattern, page_text, re.IGNORECASE):
                score += points
        
        # Analyze lines for titles
        for i, line in enumerate(lines[:25]):
            line_analysis = self._analyze_line_structure(line, i, lines)
            
            if line_analysis['is_title_candidate']:
                structure['title_candidates'].append({
                    'text': line,
                    'position': i,
                    'confidence': line_analysis['title_confidence']
                })
        
        # Ingredient and instruction scoring
        score += self._calculate_ingredient_score(page_text)
        score += self._calculate_instruction_score(page_text)
        
        structure['confidence_score'] = score
        structure['has_recipe'] = score >= 6
        
        return structure
    
    def _analyze_line_structure(self, line: str, position: int, all_lines: List[str]) -> Dict:
        """Analyze line for title characteristics"""
        analysis = {
            'is_title_candidate': False,
            'title_confidence': 0
        }
        
        if len(line) < 3 or len(line) > 80:
            return analysis
        
        title_indicators = 0
        
        # Position scoring
        if position <= 5:
            title_indicators += 2
        elif position <= 10:
            title_indicators += 1
        
        # Formatting
        if line.isupper():
            title_indicators += 2
        elif line.istitle():
            title_indicators += 1
        
        # Length
        if 10 <= len(line) <= 60:
            title_indicators += 1
        
        # Food keywords
        food_keywords = [
            'chicken', 'beef', 'pork', 'fish', 'salmon', 'eggs', 'pasta', 'rice',
            'soup', 'salad', 'cake', 'bread', 'sauce', 'beans', 'hummus', 'cheese',
            'chocolate', 'vanilla', 'lemon', 'garlic', 'roasted', 'grilled', 'baked'
        ]
        
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in food_keywords):
            title_indicators += 2
        
        # Exclusions
        exclusions = [
            re.match(r'^\d+', line),
            any(word in line_lower for word in ['cup', 'tablespoon', 'teaspoon', 'pound', 'ounce']),
            line_lower.startswith('why this recipe works'),
            line_lower.startswith('serve the'),
            ' topped with' in line_lower
        ]
        
        if any(exclusions):
            title_indicators = 0
        
        analysis['title_confidence'] = title_indicators
        analysis['is_title_candidate'] = title_indicators >= 3
        
        return analysis
    
    def _calculate_ingredient_score(self, text: str) -> int:
        """Calculate ingredient pattern score"""
        score = 0
        
        ingredient_patterns = [
            r'\d+\s*(cup|tablespoon|teaspoon|pound|ounce|tbsp|tsp|lb|oz)',
            r'\d+\s*(large|medium|small)',
            r'\d+.*?(chopped|diced|minced|sliced|grated)',
            r'\d+\s*\([^)]*ounce[^)]*\)',
            r'[¾½¼⅓⅔⅛]\s*(cup|tablespoon|teaspoon)'
        ]
        
        for pattern in ingredient_patterns:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            score += min(matches, 3)
        
        return min(score, 8)
    
    def _calculate_instruction_score(self, text: str) -> int:
        """Calculate instruction pattern score"""
        score = 0
        
        numbered_steps = len(re.findall(r'^\d+\.', text, re.MULTILINE))
        score += min(numbered_steps * 2, 6)
        
        cooking_actions = [
            'heat', 'cook', 'bake', 'mix', 'stir', 'add', 'combine', 'whisk',
            'transfer', 'remove', 'drain', 'process', 'simmer', 'boil'
        ]
        
        text_lower = text.lower()
        action_count = sum(1 for action in cooking_actions if action in text_lower)
        score += min(action_count, 4)
        
        return score
    
    def _clean_title(self, title: str) -> str:
        """Clean title with debug info"""
        original = title
        
        # Remove artifacts
        title = re.sub(r'^(recipe|atk|test kitchen|america.*test.*kitchen)[:.]?\s*', '', title, flags=re.IGNORECASE)
        title = re.sub(r'^why\s+this\s+recipe\s+works\s*', '', title, flags=re.IGNORECASE)
        title = re.sub(r'\s*\d+\s*$', '', title)
        
        if title.endswith('-'):
            title = title[:-1].strip()
        
        title = title.strip()
        
        if title.isupper() and len(title) < 60:
            title = title.title()
        
        title = re.sub(r'\s+', ' ', title)
        
        # Reject broken titles
        if (len(title) < 3 or 
            title.lower().startswith('serve the') or
            ' topped with' in title.lower()):
            return None
        
        if original != title:
            logger.debug(f"     Title cleaned: '{original}' → '{title}'")
        
        return title
    
    def _format_ingredients(self, ingredients_text: str) -> str:
        """Format ingredients"""
        if not ingredients_text:
            return ""
        
        lines = ingredients_text.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.isupper() and not re.search(r'\d', line) and 2 <= len(line.split()) <= 4:
                formatted_lines.append(f"\n{line}:")
            else:
                if not line.startswith('•'):
                    formatted_lines.append(f"• {line}")
                else:
                    formatted_lines.append(line)
        
        return '\n'.join(formatted_lines).strip()
    
    def _parse_numbered_instructions(self, instructions_text: str) -> str:
        """Parse numbered instructions"""
        if not instructions_text:
            return ""
        
        lines = instructions_text.split('\n')
        formatted_steps = []
        current_step = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            step_match = re.match(r'^(\d+)\.\s*(.+)', line)
            if step_match:
                if current_step:
                    formatted_steps.append(current_step.strip())
                current_step = f"{step_match.group(1)}. {step_match.group(2)}"
            else:
                if current_step:
                    current_step += f" {line}"
        
        if current_step:
            formatted_steps.append(current_step.strip())
        
        return '\n'.join(formatted_steps) if len(formatted_steps) >= 2 else ""
    
    def _print_rejection_summary(self):
        """Print detailed rejection summary"""
        logger.info(f"\n🔍 REJECTION ANALYSIS SUMMARY")
        logger.info("=" * 50)
        
        # Count by category
        categories = {}
        for rejection in self.rejection_details:
            cat = rejection['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        logger.info(f"📊 REJECTION CATEGORIES:")
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"  {category}: {count}")
        
        # Show examples of each category
        logger.info(f"\n📝 DETAILED EXAMPLES:")
        for category in categories.keys():
            examples = [r for r in self.rejection_details if r['category'] == category][:3]
            logger.info(f"\n{category} examples:")
            for ex in examples:
                logger.info(f"  Page {ex['page']}: {ex['reason']}")
                if ex['sample_text']:
                    logger.info(f"    Sample: {ex['sample_text'][:100]}...")


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Visual + Semantic Rejection Analyzer')
    parser.add_argument('--start-page', type=int, default=1, help='Start page')
    parser.add_argument('--end-page', type=int, default=50, help='End page')
    
    args = parser.parse_args()
    
    pdf_path = r"D:\Mik\Downloads\Me Hungie\cookbook_processing\America's Test Kitchen 25th Ann - America's Test Kitchen.pdf"
    
    if not os.path.exists(pdf_path):
        logger.error(f"❌ PDF not found: {pdf_path}")
        return
    
    analyzer = RejectionAnalyzer(pdf_path)
    analyzer.analyze_pages(args.start_page, args.end_page)


if __name__ == "__main__":
    main()
