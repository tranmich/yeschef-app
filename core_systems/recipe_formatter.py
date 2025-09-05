"""
🧹 Universal Recipe Formatter - Auto-Clean Intelligence
======================================================

Ported from the frontend formatting logic to provide consistent recipe
formatting and quality validation for the extraction system.

This provides the same "Auto Clean Formatting" intelligence that users
love, but for backend processing and quality assessment.

Author: GitHub Copilot & Team
Date: September 5, 2025
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class FormattingResult:
    """Result of formatting operation with quality metrics"""
    original_text: str
    formatted_text: str
    improvement_score: float  # 0.0 to 1.0, higher means more improvement needed
    changes_made: List[str]   # List of changes applied
    quality_issues: List[str] # Issues found in original text

class UniversalRecipeFormatter:
    """
    Python port of your frontend formatting logic
    Used for auto-cleaning and quality assessment
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def format_recipe_data(self, recipe_data: Dict) -> Dict:
        """
        Apply auto-clean formatting to entire recipe (like your frontend button)
        """
        formatted_data = recipe_data.copy()
        formatting_results = {}
        
        # Format ingredients
        if 'ingredients' in recipe_data:
            result = self.format_ingredients(recipe_data['ingredients'])
            formatted_data['ingredients'] = result.formatted_text
            formatting_results['ingredients'] = result
            
        # Format instructions  
        if 'instructions' in recipe_data:
            result = self.format_instructions(recipe_data['instructions'])
            formatted_data['instructions'] = result.formatted_text
            formatting_results['instructions'] = result
            
        # Format title
        if 'title' in recipe_data:
            result = self.format_title(recipe_data['title'])
            formatted_data['title'] = result.formatted_text
            formatting_results['title'] = result
            
        # Format metadata
        if 'time_min' in recipe_data:
            result = self.format_time(recipe_data['time_min'])
            formatted_data['time_formatted'] = result.formatted_text
            formatting_results['time'] = result
            
        if 'servings' in recipe_data:
            result = self.format_servings(recipe_data['servings'])
            formatted_data['servings_formatted'] = result.formatted_text
            formatting_results['servings'] = result
        
        # Calculate overall quality score
        overall_score = self._calculate_overall_quality_score(formatting_results)
        
        return {
            'formatted_data': formatted_data,
            'formatting_results': formatting_results,
            'overall_quality_score': overall_score,
            'needs_major_cleanup': overall_score > 0.3
        }
    
    def format_ingredients(self, ingredients: Any) -> FormattingResult:
        """Format ingredients with the same logic as your frontend"""
        if not ingredients:
            return FormattingResult('', '', 0.0, [], [])
            
        original = str(ingredients)
        processed = ingredients
        changes_made = []
        quality_issues = []
        
        # Handle JSON string input
        if isinstance(ingredients, str):
            if ingredients.strip().startswith('[') and ingredients.strip().endswith(']'):
                try:
                    processed = json.loads(ingredients)
                    changes_made.append("Parsed JSON array")
                except json.JSONDecodeError:
                    quality_issues.append("Invalid JSON format")
                    
        # Handle array input
        if isinstance(processed, list):
            filtered_ingredients = []
            
            for ingredient in processed:
                if not ingredient:
                    quality_issues.append("Empty ingredient found")
                    continue
                    
                # Handle object ingredients  
                if isinstance(ingredient, dict):
                    if 'ingredient' in ingredient:
                        filtered_ingredients.append(ingredient['ingredient'])
                        changes_made.append("Extracted from object structure")
                    elif any(key in ingredient for key in ['text', 'name', 'description']):
                        text = ingredient.get('text') or ingredient.get('name') or ingredient.get('description')
                        filtered_ingredients.append(text)
                        changes_made.append("Extracted from object structure")
                    else:
                        quality_issues.append("Unparseable ingredient object")
                else:
                    text = str(ingredient).strip()
                    if text and text != '[object Object]':
                        filtered_ingredients.append(text)
                    else:
                        quality_issues.append("Invalid ingredient text")
            
            # Format each ingredient
            formatted_ingredients = []
            for ingredient in filtered_ingredients:
                formatted = self._clean_ingredient_text(ingredient)
                if formatted != ingredient:
                    changes_made.append("Cleaned ingredient text")
                formatted_ingredients.append(formatted)
                
            result = '\n'.join(formatted_ingredients)
            
        else:
            # Handle string input
            lines = str(processed).split('\n')
            formatted_lines = []
            
            for line in lines:
                cleaned = line.strip()
                if cleaned:
                    formatted = self._clean_ingredient_text(cleaned)
                    if formatted != cleaned:
                        changes_made.append("Cleaned ingredient text")
                    formatted_lines.append(formatted)
                    
            result = '\n'.join(formatted_lines)
        
        # Calculate improvement score
        improvement_score = len(quality_issues) * 0.1 + len(changes_made) * 0.05
        improvement_score = min(improvement_score, 1.0)
        
        return FormattingResult(
            original_text=original,
            formatted_text=result,
            improvement_score=improvement_score,
            changes_made=changes_made,
            quality_issues=quality_issues
        )
    
    def format_instructions(self, instructions: Any) -> FormattingResult:
        """Format instructions with the same logic as your frontend"""
        if not instructions:
            return FormattingResult('', '', 0.0, [], [])
            
        original = str(instructions)
        processed = instructions
        changes_made = []
        quality_issues = []
        
        # Handle JSON string input
        if isinstance(instructions, str):
            if instructions.strip().startswith('[') and instructions.strip().endswith(']'):
                try:
                    processed = json.loads(instructions)
                    changes_made.append("Parsed JSON array")
                except json.JSONDecodeError:
                    quality_issues.append("Invalid JSON format")
        
        # Handle array input
        if isinstance(processed, list):
            formatted_steps = []
            
            for i, step in enumerate(processed, 1):
                if not step or not str(step).strip():
                    quality_issues.append("Empty instruction step")
                    continue
                    
                formatted = self._clean_instruction_text(str(step))
                if formatted != str(step):
                    changes_made.append("Cleaned instruction text")
                    
                # Add proper numbering
                formatted = re.sub(r'^\d+[.)]\s*', '', formatted)
                formatted = re.sub(r'^step\s*\d+:?\s*', '', formatted, flags=re.IGNORECASE)
                formatted = f"{i}. {formatted}"
                
                formatted_steps.append(formatted)
                
            result = '\n'.join(formatted_steps)
            
        else:
            # Handle string input - including concatenated steps
            instruction_text = str(processed)
            
            # Check if it's concatenated steps (like "Pour milk... 2. Add sugar...")
            if ' 1.' in instruction_text and ' 2.' in instruction_text:
                # Split on step patterns
                steps = re.split(r'\s+(\d+\.)', instruction_text)
                formatted_steps = []
                
                for i in range(0, len(steps), 2):
                    if i + 1 < len(steps):
                        step_text = steps[i + 1] if i + 1 < len(steps) else ""
                        if step_text:
                            formatted = self._clean_instruction_text(step_text)
                            step_num = len(formatted_steps) + 1
                            formatted_steps.append(f"{step_num}. {formatted}")
                            changes_made.append("Split concatenated instructions")
                            
                result = '\n'.join(formatted_steps)
            else:
                # Normal line-by-line processing
                lines = instruction_text.split('\n')
                formatted_steps = []
                
                for i, line in enumerate(lines, 1):
                    cleaned = line.strip()
                    if cleaned:
                        formatted = self._clean_instruction_text(cleaned)
                        if formatted != cleaned:
                            changes_made.append("Cleaned instruction text")
                            
                        # Add proper numbering
                        formatted = re.sub(r'^\d+[.)]\s*', '', formatted)
                        formatted = re.sub(r'^step\s*\d+:?\s*', '', formatted, flags=re.IGNORECASE)
                        formatted = f"{i}. {formatted}"
                        
                        formatted_steps.append(formatted)
                        
                result = '\n'.join(formatted_steps)
        
        # Calculate improvement score
        improvement_score = len(quality_issues) * 0.1 + len(changes_made) * 0.05
        improvement_score = min(improvement_score, 1.0)
        
        return FormattingResult(
            original_text=original,
            formatted_text=result,
            improvement_score=improvement_score,
            changes_made=changes_made,
            quality_issues=quality_issues
        )
    
    def format_title(self, title: str) -> FormattingResult:
        """Clean and format recipe title"""
        if not title:
            return FormattingResult('', '', 0.0, [], [])
            
        original = title
        formatted = title.strip()
        changes_made = []
        quality_issues = []
        
        # Remove common title issues
        if formatted.lower().startswith('imported recipe'):
            formatted = formatted.replace('Imported Recipe', '').replace('imported recipe', '').strip()
            changes_made.append("Removed 'Imported Recipe' prefix")
            
        # Remove nutrition terms that shouldn't be titles
        nutrition_terms = ['total fat', 'calories', 'protein', 'carbs', 'nutrition facts']
        for term in nutrition_terms:
            if term in formatted.lower():
                quality_issues.append(f"Title contains nutrition term: {term}")
                
        # Remove site names from titles
        for separator in [' | ', ' - ', ' :: ', ' — ', ' Recipe']:
            if separator in formatted:
                parts = formatted.split(separator)
                if len(parts) > 1:
                    formatted = parts[0].strip()
                    changes_made.append(f"Removed site name after '{separator}'")
                    break
        
        # Clean up whitespace and unicode
        original_formatted = formatted
        formatted = re.sub(r'\s+', ' ', formatted)
        formatted = formatted.replace('\\u', '')
        
        if formatted != original_formatted:
            changes_made.append("Cleaned whitespace and unicode")
            
        # Calculate improvement score
        improvement_score = len(quality_issues) * 0.2 + len(changes_made) * 0.1
        improvement_score = min(improvement_score, 1.0)
        
        return FormattingResult(
            original_text=original,
            formatted_text=formatted,
            improvement_score=improvement_score,
            changes_made=changes_made,
            quality_issues=quality_issues
        )
    
    def format_time(self, time_value: Any) -> FormattingResult:
        """Format cooking time consistently (like your frontend)"""
        if not time_value:
            return FormattingResult('', '', 0.0, [], [])
            
        original = str(time_value)
        time_str = str(time_value).lower()
        changes_made = []
        
        # Handle numeric minutes
        if re.match(r'^\d+$', time_str):
            formatted = f"{time_str} min"
            changes_made.append("Added 'min' to numeric time")
        else:
            formatted = time_str
            
            # Standardize time formats
            replacements = [
                (r'(\d+)\s*hours?\s*(\d+)\s*min', r'\1h \2min'),
                (r'(\d+)\s*hours?', r'\1h'),
                (r'(\d+)\s*minutes?', r'\1min'),
                (r'(\d+)\s*mins?', r'\1min'),
                (r'\b(\d+)\s*h\s*(\d+)\s*m\b', r'\1h \2min'),
            ]
            
            for pattern, replacement in replacements:
                new_formatted = re.sub(pattern, replacement, formatted)
                if new_formatted != formatted:
                    formatted = new_formatted
                    changes_made.append("Standardized time format")
        
        improvement_score = len(changes_made) * 0.1
        
        return FormattingResult(
            original_text=original,
            formatted_text=formatted,
            improvement_score=improvement_score,
            changes_made=changes_made,
            quality_issues=[]
        )
    
    def format_servings(self, servings: Any) -> FormattingResult:
        """Format servings consistently (like your frontend)"""
        if not servings:
            return FormattingResult('', '', 0.0, [], [])
            
        original = str(servings)
        formatted = str(servings).lower()
        changes_made = []
        
        # Standardize serving formats
        if re.match(r'^\d+$', formatted):
            formatted = f"Serves {formatted}"
            changes_made.append("Added 'Serves' to numeric servings")
        else:
            replacements = [
                (r'serves?\s*(\d+)', r'Serves \1'),
                (r'(\d+)\s*servings?', r'Serves \1'),
                (r'(\d+)\s*people', r'Serves \1'),
            ]
            
            for pattern, replacement in replacements:
                new_formatted = re.sub(pattern, replacement, formatted)
                if new_formatted != formatted:
                    formatted = new_formatted
                    changes_made.append("Standardized servings format")
        
        # Capitalize first letter
        formatted = formatted.capitalize()
        
        improvement_score = len(changes_made) * 0.1
        
        return FormattingResult(
            original_text=original,
            formatted_text=formatted,
            improvement_score=improvement_score,
            changes_made=changes_made,
            quality_issues=[]
        )
    
    def _clean_ingredient_text(self, text: str) -> str:
        """Clean individual ingredient text"""
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Handle unicode characters
        cleaned = re.sub(r'\\u([0-9a-fA-F]{4})', 
                        lambda m: chr(int(m.group(1), 16)), cleaned)
        
        # Standardize bullet points
        cleaned = re.sub(r'^[-*•]\s*', '• ', cleaned)
        if not cleaned.startswith('• ') and not re.match(r'^\d+', cleaned):
            cleaned = '• ' + cleaned
            
        return cleaned
    
    def _clean_instruction_text(self, text: str) -> str:
        """Clean individual instruction text"""
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Handle unicode characters
        cleaned = re.sub(r'\\u([0-9a-fA-F]{4})', 
                        lambda m: chr(int(m.group(1), 16)), cleaned)
        
        return cleaned
    
    def _calculate_overall_quality_score(self, formatting_results: Dict) -> float:
        """Calculate overall quality score across all fields"""
        scores = []
        for field, result in formatting_results.items():
            if isinstance(result, FormattingResult):
                scores.append(result.improvement_score)
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def assess_extraction_quality(self, raw_recipe: Dict) -> Dict:
        """
        Assess the quality of extracted recipe data using formatting intelligence
        This tells us how much cleanup the extraction needs
        """
        logger.info("🧹 Assessing extraction quality with formatting intelligence...")
        
        formatting_result = self.format_recipe_data(raw_recipe)
        
        quality_assessment = {
            'overall_score': formatting_result['overall_quality_score'],
            'needs_cleanup': formatting_result['needs_major_cleanup'],
            'field_scores': {},
            'major_issues': [],
            'extraction_quality': 'excellent'  # Will be updated based on analysis
        }
        
        # Analyze each field
        for field, result in formatting_result['formatting_results'].items():
            quality_assessment['field_scores'][field] = {
                'improvement_needed': result.improvement_score,
                'issues_found': len(result.quality_issues),
                'changes_made': len(result.changes_made)
            }
            
            # Track major issues
            if result.improvement_score > 0.3:
                quality_assessment['major_issues'].append(f"{field}: {', '.join(result.quality_issues)}")
        
        # Determine overall extraction quality
        overall_score = quality_assessment['overall_score']
        if overall_score < 0.1:
            quality_assessment['extraction_quality'] = 'excellent'
        elif overall_score < 0.3:
            quality_assessment['extraction_quality'] = 'good'
        elif overall_score < 0.5:
            quality_assessment['extraction_quality'] = 'fair'
        else:
            quality_assessment['extraction_quality'] = 'poor'
            
        logger.info(f"🎯 Extraction quality: {quality_assessment['extraction_quality']} (score: {overall_score:.2f})")
        
        return quality_assessment
