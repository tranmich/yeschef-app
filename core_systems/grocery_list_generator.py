"""
🛒 GROCERY LIST GENERATOR - Smart Shopping List Creation
=======================================================

Purpose: Generate intelligent grocery lists from meal plans
Created: August 11, 2025
Integration: Works with meal_planning_system.py and recipe database

Features:
- Aggregate ingredients from multiple recipes
- Intelligent quantity combination
- Organize by grocery store sections
- Export formats (text, JSON, Google Keep compatible)
"""

import psycopg2
import json
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
import re
import logging
import os
from dotenv import load_dotenv

load_dotenv()

class GroceryListGenerator:
    """Generate and manage grocery lists from meal plans."""
    
    def __init__(self):
        """Initialize grocery list generator with PostgreSQL connection."""
        self.db_connection = None
        self.logger = logging.getLogger(__name__)
        
    def _get_db_connection(self):
        """Get PostgreSQL database connection"""
        if not self.db_connection:
            try:
                db_url = os.getenv('DATABASE_URL')
                if not db_url:
                    raise Exception("DATABASE_URL environment variable required")
                
                self.db_connection = psycopg2.connect(db_url)
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                raise
        return self.db_connection
        
        # Common unit conversions for ingredient aggregation
        self.unit_conversions = {
            # Volume conversions to cups
            'cup': 1.0,
            'cups': 1.0,
            'c': 1.0,
            'tablespoon': 1/16,
            'tablespoons': 1/16,
            'tbsp': 1/16,
            'tsp': 1/48,
            'teaspoon': 1/48,
            'teaspoons': 1/48,
            'pint': 2.0,
            'pints': 2.0,
            'quart': 4.0,
            'quarts': 4.0,
            'gallon': 16.0,
            'gallons': 16.0,
            'fluid ounce': 1/8,
            'fluid ounces': 1/8,
            'fl oz': 1/8,
            'ml': 1/236.588,  # Approximate
            'liter': 4.227,    # Approximate
            'liters': 4.227,
        }
        
        # Grocery store section categorization
        self.grocery_sections = {
            'produce': [
                'lettuce', 'spinach', 'tomato', 'tomatoes', 'onion', 'onions',
                'garlic', 'carrot', 'carrots', 'celery', 'bell pepper', 'peppers',
                'cucumber', 'broccoli', 'cauliflower', 'potato', 'potatoes',
                'apple', 'apples', 'banana', 'bananas', 'lemon', 'lemons',
                'lime', 'limes', 'orange', 'oranges', 'avocado', 'avocados',
                'mushroom', 'mushrooms', 'zucchini', 'herbs', 'parsley',
                'cilantro', 'basil', 'thyme', 'rosemary'
            ],
            'meat_seafood': [
                'chicken', 'beef', 'pork', 'turkey', 'lamb', 'fish', 'salmon',
                'tuna', 'shrimp', 'ground beef', 'ground turkey', 'bacon',
                'sausage', 'ham', 'steak', 'chicken breast', 'chicken thigh'
            ],
            'dairy': [
                'milk', 'cheese', 'butter', 'yogurt', 'cream', 'sour cream',
                'cottage cheese', 'cream cheese', 'eggs', 'egg', 'heavy cream',
                'half and half', 'mozzarella', 'cheddar', 'parmesan'
            ],
            'pantry': [
                'flour', 'sugar', 'salt', 'pepper', 'oil', 'olive oil',
                'vegetable oil', 'vinegar', 'baking powder', 'baking soda',
                'vanilla', 'garlic powder', 'onion powder', 'paprika',
                'cumin', 'oregano', 'pasta', 'rice', 'bread', 'crackers',
                'canned tomatoes', 'broth', 'stock', 'beans', 'lentils'
            ],
            'frozen': [
                'frozen vegetables', 'frozen fruit', 'ice cream', 'frozen pizza',
                'frozen berries', 'frozen peas', 'frozen corn'
            ],
            'bakery': [
                'bread', 'rolls', 'bagels', 'muffins', 'croissants', 'tortillas'
            ]
        }
    
    def generate_grocery_list_from_meal_plan(self, meal_plan_id: int) -> Dict[str, Any]:
        """
        Generate a grocery list from a meal plan.
        
        Args:
            meal_plan_id: ID of the meal plan
            
        Returns:
            Dict: Organized grocery list with sections and totals
        """
        try:
            # Get recipe IDs from meal plan
            recipe_ids = self._get_recipe_ids_from_meal_plan(meal_plan_id)
            
            if not recipe_ids:
                return {
                    'success': False,
                    'message': 'No recipes found in meal plan',
                    'grocery_list': {}
                }
            
            # Generate grocery list from recipe IDs
            return self.generate_grocery_list_from_recipes(recipe_ids)
            
        except Exception as e:
            self.logger.error(f"Error generating grocery list from meal plan: {e}")
            return {
                'success': False,
                'message': f'Error generating grocery list: {str(e)}',
                'grocery_list': {}
            }
    
    def generate_grocery_list_from_recipes(self, recipe_ids: List[int]) -> Dict[str, Any]:
        """
        Generate a grocery list from a list of recipe IDs.
        
        Args:
            recipe_ids: List of recipe IDs
            
        Returns:
            Dict: Organized grocery list
        """
        try:
            # Get all ingredients for the recipes
            all_ingredients = self._get_ingredients_for_recipes(recipe_ids)
            
            # Aggregate ingredients by name
            aggregated_ingredients = self._aggregate_ingredients(all_ingredients)
            
            # Organize by grocery store sections
            organized_list = self._organize_by_sections(aggregated_ingredients)
            
            # Generate different export formats
            return {
                'success': True,
                'recipe_count': len(recipe_ids),
                'ingredient_count': len(aggregated_ingredients),
                'grocery_list': {
                    'by_section': organized_list,
                    'alphabetical': self._sort_alphabetically(aggregated_ingredients),
                    'text_format': self._format_as_text(organized_list),
                    'google_keep_format': self._format_for_google_keep(organized_list)
                },
                'recipes_included': recipe_ids
            }
            
        except Exception as e:
            self.logger.error(f"Error generating grocery list: {e}")
            return {
                'success': False,
                'message': f'Error generating grocery list: {str(e)}',
                'grocery_list': {}
            }
    
    def _get_recipe_ids_from_meal_plan(self, meal_plan_id: int) -> List[int]:
        """Get recipe IDs from a meal plan."""
        from .meal_planning_system import MealPlanningSystem
        
        meal_planner = MealPlanningSystem()
        return meal_planner.get_recipes_from_meal_plan(meal_plan_id)
    
    def _get_ingredients_for_recipes(self, recipe_ids: List[int]) -> List[Dict]:
        """
        Get all ingredients for a list of recipes.
        
        Args:
            recipe_ids: List of recipe IDs
            
        Returns:
            List[Dict]: List of ingredient information
        """
        conn = self._get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Get ingredients directly from recipes table since the normalized tables have parsing issues
            placeholders = ','.join(['%s' for _ in recipe_ids])
            query = f'''
                SELECT id, title, ingredients
                FROM recipes
                WHERE id IN ({placeholders})
            '''
            
            cursor.execute(query, recipe_ids)
            rows = cursor.fetchall()
            
            ingredients = []
            for row in rows:
                recipe_id, recipe_title, ingredients_json = row
                
                # Parse the ingredients JSON
                try:
                    if ingredients_json:
                        ingredients_list = json.loads(ingredients_json)
                        for ingredient_text in ingredients_list:
                            # Parse each ingredient text to extract quantity, unit, and name
                            parsed = self._parse_ingredient_text(ingredient_text)
                            if parsed['name']:  # Only add if we could extract a name
                                ingredients.append({
                                    'recipe_id': recipe_id,
                                    'ingredient_name': parsed['name'],
                                    'quantity': parsed['quantity'],
                                    'unit': parsed['unit'],
                                    'preparation': parsed['preparation'],
                                    'recipe_title': recipe_title,
                                    'original_text': ingredient_text
                                })
                except (json.JSONDecodeError, TypeError) as e:
                    self.logger.warning(f"Could not parse ingredients for recipe {recipe_id}: {e}")
                    continue
            
            return ingredients
            
        except Exception as e:
            self.logger.error(f"Error getting ingredients for recipes: {e}")
            return []
        finally:
            conn.close()
    
    def _aggregate_ingredients(self, ingredients: List[Dict]) -> Dict[str, Dict]:
        """
        Aggregate ingredients by name, combining quantities where possible.
        
        Args:
            ingredients: List of ingredient dictionaries
            
        Returns:
            Dict: Aggregated ingredients
        """
        aggregated = defaultdict(lambda: {
            'total_quantity': 0,
            'unit': '',
            'recipes': [],
            'preparations': set(),
            'display_text': ''
        })
        
        for ingredient in ingredients:
            name = ingredient['ingredient_name'].lower()
            quantity = ingredient['quantity'] or 0
            unit = ingredient['unit'].lower().strip()
            prep = ingredient['preparation']
            recipe = ingredient['recipe_title']
            
            # Try to parse and convert quantity
            numeric_quantity = self._parse_quantity(quantity)
            
            # Store recipe information
            aggregated[name]['recipes'].append(recipe)
            if prep:
                aggregated[name]['preparations'].add(prep)
            
            # Try to aggregate quantities if units are compatible
            if aggregated[name]['unit'] == '':
                # First occurrence
                aggregated[name]['total_quantity'] = numeric_quantity
                aggregated[name]['unit'] = unit
            elif self._units_compatible(aggregated[name]['unit'], unit):
                # Compatible units - try to combine
                converted_quantity = self._convert_quantity(numeric_quantity, unit, aggregated[name]['unit'])
                if converted_quantity is not None:
                    aggregated[name]['total_quantity'] += converted_quantity
                else:
                    # Can't convert - keep separate
                    aggregated[name]['display_text'] += f" + {quantity} {unit}"
            else:
                # Incompatible units - keep separate
                aggregated[name]['display_text'] += f" + {quantity} {unit}"
        
        # Generate final display text
        final_aggregated = {}
        for name, data in aggregated.items():
            display_quantity = self._format_quantity(data['total_quantity'])
            display_unit = data['unit']
            extra_text = data['display_text']
            
            # Create display text with ingredient name
            ingredient_name = name.title()  # Capitalize first letter of each word
            
            if display_quantity and display_unit:
                display_text = f"{display_quantity} {display_unit} {ingredient_name}"
            elif display_quantity:
                display_text = f"{display_quantity} {ingredient_name}"
            else:
                display_text = f"{ingredient_name} (as needed)"
            
            if extra_text:
                display_text += extra_text
            
            # Add preparation notes if consistent
            preparations = list(data['preparations'])
            if len(preparations) == 1:
                display_text += f" ({preparations[0]})"
            
            final_aggregated[name] = {
                'display_text': display_text,
                'quantity': data['total_quantity'],
                'unit': data['unit'],
                'recipes': list(set(data['recipes'])),  # Remove duplicates
                'ingredient_name': name.title()
            }
        
        return final_aggregated
    
    def _organize_by_sections(self, ingredients: Dict[str, Dict]) -> Dict[str, List]:
        """
        Organize ingredients by grocery store sections.
        
        Args:
            ingredients: Aggregated ingredients
            
        Returns:
            Dict: Ingredients organized by section
        """
        sections = {section: [] for section in self.grocery_sections.keys()}
        sections['other'] = []
        
        for ingredient_name, ingredient_data in ingredients.items():
            name_lower = ingredient_name.lower()
            placed = False
            
            # Check each section for matching keywords
            for section, keywords in self.grocery_sections.items():
                if any(keyword in name_lower for keyword in keywords):
                    sections[section].append({
                        'name': ingredient_data['ingredient_name'],
                        'display_text': ingredient_data['display_text'],
                        'recipes': ingredient_data['recipes']
                    })
                    placed = True
                    break
            
            # If not categorized, put in 'other'
            if not placed:
                sections['other'].append({
                    'name': ingredient_data['ingredient_name'],
                    'display_text': ingredient_data['display_text'],
                    'recipes': ingredient_data['recipes']
                })
        
        # Remove empty sections
        return {section: items for section, items in sections.items() if items}
    
    def _sort_alphabetically(self, ingredients: Dict[str, Dict]) -> List[Dict]:
        """Sort ingredients alphabetically."""
        return sorted([
            {
                'name': data['ingredient_name'],
                'display_text': data['display_text'],
                'recipes': data['recipes']
            }
            for data in ingredients.values()
        ], key=lambda x: x['name'].lower())
    
    def _format_as_text(self, organized_list: Dict[str, List]) -> str:
        """Format grocery list as plain text."""
        text_lines = []
        
        for section, items in organized_list.items():
            if items:
                text_lines.append(f"\n{section.upper().replace('_', ' ')}:")
                text_lines.append("-" * (len(section) + 1))
                
                for item in items:
                    text_lines.append(f"• {item['display_text']} ({item['name']})")
        
        return "\n".join(text_lines)
    
    def _format_for_google_keep(self, organized_list: Dict[str, List]) -> List[str]:
        """Format grocery list for Google Keep (simple checklist)."""
        items = []
        
        for section, section_items in organized_list.items():
            for item in section_items:
                items.append(f"{item['display_text']} ({item['name']})")
        
        return sorted(items)
    
    def _parse_ingredient_text(self, ingredient_text: str) -> Dict[str, str]:
        """
        Parse ingredient text like '2 tbsp unsalted butter' into components.
        
        Args:
            ingredient_text: Raw ingredient string
            
        Returns:
            Dict with keys: quantity, unit, name, preparation
        """
        if not ingredient_text or not isinstance(ingredient_text, str):
            return {'quantity': '', 'unit': '', 'name': '', 'preparation': ''}
        
        # Clean up the text
        text = ingredient_text.strip()
        
        # Common units - more comprehensive list
        units = [
            'cup', 'cups', 'c',
            'tablespoon', 'tablespoons', 'tbsp', 'tbs',
            'teaspoon', 'teaspoons', 'tsp',
            'pound', 'pounds', 'lb', 'lbs',
            'ounce', 'ounces', 'oz',
            'gram', 'grams', 'g',
            'kilogram', 'kilograms', 'kg',
            'pint', 'pints', 'pt',
            'quart', 'quarts', 'qt',
            'gallon', 'gallons', 'gal',
            'fluid ounce', 'fluid ounces', 'fl oz', 'floz',
            'milliliter', 'milliliters', 'ml',
            'liter', 'liters', 'l',
            'inch', 'inches', 'in',
            'clove', 'cloves',
            'head', 'heads',
            'bunch', 'bunches',
            'package', 'packages', 'pkg',
            'can', 'cans',
            'jar', 'jars',
            'bottle', 'bottles',
            'slice', 'slices',
            'piece', 'pieces',
            'large', 'medium', 'small',
            'whole', 'half', 'quarter'
        ]
        
        # Create a sorted list by length (longest first) to avoid partial matches
        units_sorted = sorted(units, key=len, reverse=True)
        
        # Pattern to match quantity at the beginning
        # Examples: "2", "1/2", "3-4", "2.5", "1 1/2"
        quantity_pattern = r'^([0-9]+(?:[\/\-\.][0-9]+)*(?:\s+[0-9]+(?:\/[0-9]+)?)?)\s*'
        
        quantity_match = re.match(quantity_pattern, text)
        
        if quantity_match:
            quantity = quantity_match.group(1).strip()
            remaining_text = text[quantity_match.end():].strip()
            
            # Look for unit at the beginning of remaining text
            unit = ''
            for unit_candidate in units_sorted:
                if remaining_text.lower().startswith(unit_candidate.lower()):
                    # Make sure it's a complete word (not part of another word)
                    if (len(remaining_text) == len(unit_candidate) or 
                        remaining_text[len(unit_candidate)].isspace()):
                        unit = unit_candidate
                        remaining_text = remaining_text[len(unit_candidate):].strip()
                        break
            
            # What's left is the ingredient name and possibly preparation
            name = remaining_text
            preparation = ''
            
            # Extract preparation from parentheses
            paren_match = re.search(r'\(([^)]+)\)', name)
            if paren_match:
                preparation = paren_match.group(1)
                name = re.sub(r'\s*\([^)]+\)', '', name).strip()
            
            # Extract preparation after comma
            if ',' in name:
                parts = name.split(',', 1)
                name = parts[0].strip()
                if not preparation:  # Only use if we don't already have preparation from parentheses
                    preparation = parts[1].strip()
            
            return {
                'quantity': quantity,
                'unit': unit,
                'name': name,
                'preparation': preparation
            }
        else:
            # No quantity found, check if it starts with a unit
            unit = ''
            name = text
            
            for unit_candidate in units_sorted:
                if text.lower().startswith(unit_candidate.lower()):
                    if (len(text) == len(unit_candidate) or 
                        text[len(unit_candidate)].isspace()):
                        unit = unit_candidate
                        name = text[len(unit_candidate):].strip()
                        break
            
            # Extract preparation from parentheses
            preparation = ''
            paren_match = re.search(r'\(([^)]+)\)', name)
            if paren_match:
                preparation = paren_match.group(1)
                name = re.sub(r'\s*\([^)]+\)', '', name).strip()
            
            # Extract preparation after comma
            if ',' in name:
                parts = name.split(',', 1)
                name = parts[0].strip()
                if not preparation:
                    preparation = parts[1].strip()
            
            return {
                'quantity': '',
                'unit': unit,
                'name': name,
                'preparation': preparation
            }
    
    def _parse_quantity(self, quantity_str: Any) -> float:
        """Parse quantity string to float."""
        if isinstance(quantity_str, (int, float)):
            return float(quantity_str)
        
        if not isinstance(quantity_str, str):
            return 0.0
        
        # Remove extra whitespace
        quantity_str = str(quantity_str).strip()
        
        # Handle fractions like "1/2", "1 1/2"
        fraction_pattern = r'(\d+)?\s*(\d+)/(\d+)'
        fraction_match = re.search(fraction_pattern, quantity_str)
        
        if fraction_match:
            whole_part = int(fraction_match.group(1) or 0)
            numerator = int(fraction_match.group(2))
            denominator = int(fraction_match.group(3))
            return whole_part + (numerator / denominator)
        
        # Handle decimal numbers
        number_pattern = r'\d+\.?\d*'
        number_match = re.search(number_pattern, quantity_str)
        
        if number_match:
            return float(number_match.group())
        
        return 0.0
    
    def _units_compatible(self, unit1: str, unit2: str) -> bool:
        """Check if two units are compatible for aggregation."""
        unit1 = unit1.lower().strip()
        unit2 = unit2.lower().strip()
        
        # Same unit
        if unit1 == unit2:
            return True
        
        # Both are volume units
        volume_units = set(self.unit_conversions.keys())
        if unit1 in volume_units and unit2 in volume_units:
            return True
        
        return False
    
    def _convert_quantity(self, quantity: float, from_unit: str, to_unit: str) -> Optional[float]:
        """Convert quantity from one unit to another."""
        from_unit = from_unit.lower().strip()
        to_unit = to_unit.lower().strip()
        
        if from_unit == to_unit:
            return quantity
        
        # Volume conversions
        if from_unit in self.unit_conversions and to_unit in self.unit_conversions:
            # Convert to cups, then to target unit
            cups = quantity * self.unit_conversions[from_unit]
            return cups / self.unit_conversions[to_unit]
        
        return None
    
    def _format_quantity(self, quantity: float) -> str:
        """Format quantity for display."""
        if quantity == 0:
            return ""
        
        # Round to reasonable precision
        if quantity == int(quantity):
            return str(int(quantity))
        elif quantity < 1:
            # Convert to fraction if reasonable
            return f"{quantity:.2f}".rstrip('0').rstrip('.')
        else:
            return f"{quantity:.1f}".rstrip('0').rstrip('.')


# Convenience function for quick access
def get_grocery_list_generator() -> GroceryListGenerator:
    """Get initialized grocery list generator instance."""
    return GroceryListGenerator()


if __name__ == "__main__":
    # Test the grocery list generator
    import sys
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Initialize generator
        grocery_generator = GroceryListGenerator()
        
        # Test with some recipe IDs (assuming they exist in database)
        test_recipe_ids = [1, 2, 3]  # Replace with actual recipe IDs
        
        grocery_list = grocery_generator.generate_grocery_list_from_recipes(test_recipe_ids)
        
        if grocery_list['success']:
            print(f"✅ Generated grocery list for {grocery_list['recipe_count']} recipes")
            print(f"✅ Found {grocery_list['ingredient_count']} unique ingredients")
            
            # Print organized sections
            for section, items in grocery_list['grocery_list']['by_section'].items():
                print(f"\n{section.upper()}:")
                for item in items[:3]:  # Show first 3 items
                    print(f"  • {item['display_text']}")
            
            print("\n✅ Grocery list generator test completed successfully!")
        else:
            print(f"⚠️ Test completed with message: {grocery_list['message']}")
        
    except Exception as e:
        print(f"❌ Error testing grocery list generator: {e}")
        sys.exit(1)
