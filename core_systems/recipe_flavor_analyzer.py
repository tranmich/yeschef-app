#!/usr/bin/env python3
"""
🎨 Recipe Flavor Analyzer - Advanced Flavor Profiling System
=============================================================

Modern flavor analysis system designed for our massive recipe database.
Analyzes the 1000+ ATK recipes and future cookbook additions.

Integrates with:
- PostgreSQL production database
- Enhanced recipe suggestions engine
- Ingredient intelligence engine

Features:
- Advanced flavor profile generation
- Cuisine style detection
- Cooking method analysis
- Ingredient harmony scoring
- Complexity assessment
"""

import psycopg2
import psycopg2.extras
import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class FlavorProfile:
    """Comprehensive flavor profile for a recipe"""
    recipe_id: int
    primary_flavors: List[str]
    secondary_flavors: List[str]
    intensity: str  # mild, moderate, bold, intense
    cooking_methods: List[str]
    cuisine_style: str
    season: str
    dietary_tags: List[str]
    complexity_score: int  # 1-10
    harmony_score: float  # 0.0-1.0
    ingredient_count: int
    technique_difficulty: str  # beginner, intermediate, advanced

class RecipeFlavorAnalyzer:
    """
    🧠 Advanced Recipe Flavor Analysis Engine
    
    Analyzes recipes to generate comprehensive flavor profiles including:
    - Flavor characteristics from ingredients
    - Cooking method detection
    - Cuisine style classification
    - Complexity and harmony scoring
    """
    
    def __init__(self):
        self.db_connection = None
        self._initialize_flavor_data()
    
    def _get_db_connection(self):
        """Get database connection using Railway PostgreSQL"""
        if not self.db_connection:
            try:
                db_url = os.getenv('DATABASE_URL')
                if not db_url:
                    # Fallback to the public Railway URL for backward compatibility
                    db_url = "postgresql://postgres:bBPQiSOwjkCnYdydFUcQKXeiFGFdIsgh@junction.proxy.rlwy.net:40067/railway"
                
                self.db_connection = psycopg2.connect(db_url)
                self.db_connection.autocommit = True
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                raise
        return self.db_connection
    
    def _initialize_flavor_data(self):
        """Initialize comprehensive flavor analysis data"""
        
        # Enhanced flavor keywords with more sophisticated detection
        self.flavor_keywords = {
            'sweet': [
                'sugar', 'honey', 'maple', 'chocolate', 'vanilla', 'caramel',
                'fruit', 'berry', 'apple', 'pear', 'grape', 'cherry', 'strawberry',
                'molasses', 'brown sugar', 'agave', 'dates', 'raisins'
            ],
            'savory': [
                'salt', 'cheese', 'meat', 'herbs', 'garlic', 'onion', 'umami',
                'soy sauce', 'worcestershire', 'anchovy', 'mushroom', 'tomato paste',
                'miso', 'fish sauce', 'parmesan', 'aged cheese'
            ],
            'spicy': [
                'pepper', 'chili', 'hot', 'spice', 'jalapeño', 'cayenne', 'paprika',
                'chipotle', 'habanero', 'sriracha', 'tabasco', 'ginger', 'wasabi',
                'horseradish', 'red pepper flakes', 'curry powder'
            ],
            'tangy': [
                'lemon', 'lime', 'vinegar', 'citrus', 'orange', 'grapefruit',
                'wine vinegar', 'balsamic', 'rice vinegar', 'pickle', 'capers',
                'yogurt', 'sour cream', 'buttermilk', 'sumac'
            ],
            'rich': [
                'butter', 'cream', 'oil', 'nuts', 'avocado', 'coconut milk',
                'heavy cream', 'olive oil', 'bacon', 'duck fat', 'ghee',
                'tahini', 'coconut cream', 'cashew', 'walnut'
            ],
            'herbal': [
                'basil', 'oregano', 'thyme', 'rosemary', 'sage', 'cilantro',
                'parsley', 'dill', 'mint', 'tarragon', 'chives', 'bay leaf',
                'marjoram', 'fennel', 'lavender'
            ],
            'earthy': [
                'mushroom', 'truffle', 'potato', 'root vegetable', 'beet',
                'carrot', 'turnip', 'parsnip', 'sweet potato', 'squash',
                'pumpkin', 'leek', 'celery root'
            ],
            'fresh': [
                'cucumber', 'lettuce', 'spinach', 'arugula', 'radish',
                'bell pepper', 'snap pea', 'green bean', 'zucchini',
                'fresh herbs', 'sprouts', 'watercress'
            ]
        }
        
        # Cooking method detection patterns
        self.cooking_methods = {
            'grilled': ['grill', 'grilling', 'grilled', 'barbecue', 'bbq', 'char'],
            'roasted': ['roast', 'roasting', 'roasted', 'oven roast', 'baked in oven'],
            'sautéed': ['sauté', 'sautéed', 'pan fry', 'skillet', 'frying pan'],
            'braised': ['braise', 'braised', 'slow cook', 'pot roast', 'stew'],
            'steamed': ['steam', 'steamed', 'steaming'],
            'baked': ['bake', 'baked', 'baking', 'oven bake'],
            'fried': ['fry', 'fried', 'deep fry', 'pan fried'],
            'poached': ['poach', 'poached', 'poaching'],
            'boiled': ['boil', 'boiled', 'boiling', 'simmer'],
            'smoked': ['smoke', 'smoked', 'smoking']
        }
        
        # Cuisine style detection
        self.cuisine_keywords = {
            'italian': ['pasta', 'pizza', 'parmesan', 'mozzarella', 'basil', 'oregano', 'marinara', 'risotto'],
            'mexican': ['taco', 'salsa', 'jalapeño', 'cilantro', 'lime', 'avocado', 'cumin', 'chili'],
            'asian': ['soy sauce', 'ginger', 'garlic', 'sesame', 'rice vinegar', 'miso', 'wasabi'],
            'indian': ['curry', 'garam masala', 'turmeric', 'cumin', 'coriander', 'cardamom', 'naan'],
            'french': ['butter', 'cream', 'wine', 'herbs de provence', 'brie', 'cognac', 'shallot'],
            'mediterranean': ['olive oil', 'olives', 'feta', 'lemon', 'herbs', 'tomato', 'capers'],
            'american': ['bbq', 'bacon', 'cheddar', 'ranch', 'maple', 'corn', 'apple pie'],
            'thai': ['coconut milk', 'fish sauce', 'lime', 'basil', 'chili', 'lemongrass'],
            'middle_eastern': ['tahini', 'sumac', 'pomegranate', 'pine nuts', 'mint', 'lamb']
        }
        
        # Dietary tag detection
        self.dietary_patterns = {
            'vegetarian': {
                'indicators': ['vegetarian', 'veggie'],
                'exclude_proteins': ['chicken', 'beef', 'pork', 'fish', 'seafood', 'meat']
            },
            'vegan': {
                'indicators': ['vegan'],
                'exclude_items': ['cheese', 'butter', 'cream', 'milk', 'egg', 'honey']
            },
            'gluten_free': {
                'indicators': ['gluten free', 'gluten-free'],
                'exclude_items': ['flour', 'wheat', 'bread', 'pasta']
            },
            'dairy_free': {
                'indicators': ['dairy free', 'dairy-free'],
                'exclude_items': ['milk', 'cream', 'cheese', 'butter', 'yogurt']
            }
        }
    
    def analyze_recipe(self, recipe_data: Dict) -> FlavorProfile:
        """
        Perform comprehensive flavor analysis on a recipe
        
        Args:
            recipe_data: Dict containing recipe information
            
        Returns:
            FlavorProfile with complete analysis
        """
        recipe_id = recipe_data.get('id', 0)
        title = recipe_data.get('title', '')
        ingredients = recipe_data.get('ingredients', [])
        instructions = recipe_data.get('instructions', [])
        
        # Parse ingredients if they're JSON strings
        if isinstance(ingredients, str):
            try:
                ingredients = json.loads(ingredients)
            except:
                ingredients = [ingredients]
        
        # Parse instructions if they're JSON strings
        if isinstance(instructions, str):
            try:
                instructions = json.loads(instructions)
            except:
                instructions = [instructions]
        
        # Combine all text for analysis
        ingredient_text = ' '.join(ingredients).lower()
        instruction_text = ' '.join(instructions).lower()
        title_text = title.lower()
        all_text = f"{title_text} {ingredient_text} {instruction_text}"
        
        # Analyze primary and secondary flavors
        primary_flavors, secondary_flavors = self._analyze_flavors(all_text)
        
        # Determine cooking methods
        cooking_methods = self._detect_cooking_methods(instruction_text)
        
        # Classify cuisine style
        cuisine_style = self._classify_cuisine(all_text)
        
        # Determine intensity
        intensity = self._calculate_intensity(all_text, cooking_methods)
        
        # Detect dietary tags
        dietary_tags = self._detect_dietary_tags(all_text)
        
        # Calculate complexity score
        complexity_score = self._calculate_complexity(ingredients, instructions, cooking_methods)
        
        # Calculate harmony score
        harmony_score = self._calculate_harmony(primary_flavors, secondary_flavors, cuisine_style)
        
        # Determine technique difficulty
        technique_difficulty = self._assess_technique_difficulty(instruction_text, cooking_methods)
        
        # Determine season
        season = self._determine_season(ingredient_text)
        
        return FlavorProfile(
            recipe_id=recipe_id,
            primary_flavors=primary_flavors,
            secondary_flavors=secondary_flavors,
            intensity=intensity,
            cooking_methods=cooking_methods,
            cuisine_style=cuisine_style,
            season=season,
            dietary_tags=dietary_tags,
            complexity_score=complexity_score,
            harmony_score=harmony_score,
            ingredient_count=len(ingredients),
            technique_difficulty=technique_difficulty
        )
    
    def _analyze_flavors(self, text: str) -> Tuple[List[str], List[str]]:
        """Analyze text to identify primary and secondary flavors"""
        flavor_scores = defaultdict(int)
        
        for flavor, keywords in self.flavor_keywords.items():
            for keyword in keywords:
                # Count occurrences with different weights
                count = text.count(keyword)
                if count > 0:
                    # Weight based on keyword importance and frequency
                    weight = min(count, 3)  # Cap at 3 to avoid over-weighting
                    flavor_scores[flavor] += weight
        
        # Sort by score
        sorted_flavors = sorted(flavor_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Primary flavors (top 3)
        primary_flavors = [flavor for flavor, score in sorted_flavors[:3] if score >= 2]
        
        # Secondary flavors (next 3, with lower threshold)
        secondary_flavors = [flavor for flavor, score in sorted_flavors[3:6] if score >= 1]
        
        # Ensure we have at least one primary flavor
        if not primary_flavors and sorted_flavors:
            primary_flavors = [sorted_flavors[0][0]]
        elif not primary_flavors:
            primary_flavors = ['savory']  # Default
        
        return primary_flavors, secondary_flavors
    
    def _detect_cooking_methods(self, instruction_text: str) -> List[str]:
        """Detect cooking methods from instructions"""
        detected_methods = []
        
        for method, keywords in self.cooking_methods.items():
            if any(keyword in instruction_text for keyword in keywords):
                detected_methods.append(method)
        
        return detected_methods
    
    def _classify_cuisine(self, text: str) -> str:
        """Classify the cuisine style of the recipe"""
        cuisine_scores = {}
        
        for cuisine, keywords in self.cuisine_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                cuisine_scores[cuisine] = score
        
        if cuisine_scores:
            return max(cuisine_scores, key=cuisine_scores.get)
        
        return 'american'  # Default
    
    def _calculate_intensity(self, text: str, cooking_methods: List[str]) -> str:
        """Calculate flavor intensity based on ingredients and cooking methods"""
        intensity_score = 0
        
        # Spicy ingredients increase intensity
        spicy_count = sum(1 for keyword in self.flavor_keywords['spicy'] if keyword in text)
        intensity_score += spicy_count * 2
        
        # Rich ingredients add intensity
        rich_count = sum(1 for keyword in self.flavor_keywords['rich'] if keyword in text)
        intensity_score += rich_count
        
        # Certain cooking methods add intensity
        high_intensity_methods = ['grilled', 'roasted', 'fried', 'smoked']
        intensity_score += sum(1 for method in cooking_methods if method in high_intensity_methods)
        
        if intensity_score >= 6:
            return 'intense'
        elif intensity_score >= 4:
            return 'bold'
        elif intensity_score >= 2:
            return 'moderate'
        else:
            return 'mild'
    
    def _detect_dietary_tags(self, text: str) -> List[str]:
        """Detect dietary restrictions and preferences"""
        tags = []
        
        for tag, criteria in self.dietary_patterns.items():
            # Check for explicit indicators
            if any(indicator in text for indicator in criteria.get('indicators', [])):
                tags.append(tag)
                continue
            
            # Check for exclusions (for vegetarian/vegan detection)
            if 'exclude_proteins' in criteria:
                has_meat = any(protein in text for protein in criteria['exclude_proteins'])
                if not has_meat:
                    tags.append(tag)
            
            if 'exclude_items' in criteria:
                has_excluded = any(item in text for item in criteria['exclude_items'])
                if not has_excluded and tag not in tags:
                    # Only add if not already added and no excluded items found
                    pass  # More sophisticated logic needed here
        
        return tags
    
    def _calculate_complexity(self, ingredients: List[str], instructions: List[str], 
                            cooking_methods: List[str]) -> int:
        """Calculate recipe complexity score (1-10)"""
        complexity_score = 0
        
        # Ingredient count factor
        ingredient_count = len(ingredients)
        complexity_score += min(ingredient_count // 3, 3)  # Max 3 points
        
        # Instruction count factor
        instruction_count = len(instructions)
        complexity_score += min(instruction_count // 2, 3)  # Max 3 points
        
        # Cooking method complexity
        complex_methods = ['braised', 'smoked', 'poached']
        complexity_score += sum(1 for method in cooking_methods if method in complex_methods)
        
        # Multiple cooking methods add complexity
        if len(cooking_methods) > 2:
            complexity_score += 1
        
        return min(max(complexity_score, 1), 10)  # Ensure 1-10 range
    
    def _calculate_harmony(self, primary_flavors: List[str], secondary_flavors: List[str], 
                          cuisine_style: str) -> float:
        """Calculate flavor harmony score (0.0-1.0)"""
        harmony_score = 0.5  # Base score
        
        # Flavor balance increases harmony
        total_flavors = len(primary_flavors) + len(secondary_flavors)
        if 2 <= total_flavors <= 5:
            harmony_score += 0.2
        
        # Cuisine-appropriate flavors increase harmony
        cuisine_bonus = {
            'italian': ['savory', 'herbal', 'tangy'],
            'mexican': ['spicy', 'tangy', 'fresh'],
            'french': ['rich', 'savory', 'herbal'],
            'asian': ['savory', 'spicy', 'tangy']
        }
        
        if cuisine_style in cuisine_bonus:
            matching_flavors = set(primary_flavors) & set(cuisine_bonus[cuisine_style])
            harmony_score += len(matching_flavors) * 0.1
        
        return min(max(harmony_score, 0.0), 1.0)
    
    def _assess_technique_difficulty(self, instruction_text: str, cooking_methods: List[str]) -> str:
        """Assess the technical difficulty of the recipe"""
        difficulty_score = 0
        
        # Complex techniques
        advanced_techniques = [
            'fold', 'whip', 'emulsion', 'reduce', 'deglaze', 'julienne',
            'brunoise', 'chiffonade', 'temper', 'confit', 'sous vide'
        ]
        
        difficulty_score += sum(1 for technique in advanced_techniques if technique in instruction_text)
        
        # Multiple cooking methods increase difficulty
        difficulty_score += max(0, len(cooking_methods) - 1)
        
        # Temperature precision indicators
        temp_indicators = ['°f', '°c', 'degree', 'thermometer', 'internal temperature']
        if any(indicator in instruction_text for indicator in temp_indicators):
            difficulty_score += 1
        
        if difficulty_score >= 4:
            return 'advanced'
        elif difficulty_score >= 2:
            return 'intermediate'
        else:
            return 'beginner'
    
    def _determine_season(self, ingredient_text: str) -> str:
        """Determine seasonal appropriateness"""
        seasonal_ingredients = {
            'spring': ['asparagus', 'pea', 'artichoke', 'lettuce', 'spinach'],
            'summer': ['tomato', 'zucchini', 'corn', 'berry', 'melon', 'peach'],
            'fall': ['apple', 'pumpkin', 'squash', 'sweet potato', 'cranberry'],
            'winter': ['root vegetable', 'cabbage', 'citrus', 'pomegranate']
        }
        
        season_scores = {}
        for season, ingredients in seasonal_ingredients.items():
            score = sum(1 for ingredient in ingredients if ingredient in ingredient_text)
            if score > 0:
                season_scores[season] = score
        
        if season_scores:
            return max(season_scores, key=season_scores.get)
        
        return 'all-season'
    
    def save_flavor_profile(self, flavor_profile: FlavorProfile) -> bool:
        """Save flavor profile to database"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            
            # Insert or update flavor profile
            cursor.execute("""
                INSERT INTO recipe_flavor_profiles (
                    recipe_id, primary_flavors, secondary_flavors, intensity,
                    cooking_methods, cuisine_style, season, dietary_tags,
                    complexity_score, harmony_score, ingredient_count,
                    technique_difficulty, created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                ) ON CONFLICT (recipe_id) DO UPDATE SET
                    primary_flavors = EXCLUDED.primary_flavors,
                    secondary_flavors = EXCLUDED.secondary_flavors,
                    intensity = EXCLUDED.intensity,
                    cooking_methods = EXCLUDED.cooking_methods,
                    cuisine_style = EXCLUDED.cuisine_style,
                    season = EXCLUDED.season,
                    dietary_tags = EXCLUDED.dietary_tags,
                    complexity_score = EXCLUDED.complexity_score,
                    harmony_score = EXCLUDED.harmony_score,
                    ingredient_count = EXCLUDED.ingredient_count,
                    technique_difficulty = EXCLUDED.technique_difficulty,
                    updated_at = NOW()
            """, (
                flavor_profile.recipe_id,
                json.dumps(flavor_profile.primary_flavors),
                json.dumps(flavor_profile.secondary_flavors),
                flavor_profile.intensity,
                json.dumps(flavor_profile.cooking_methods),
                flavor_profile.cuisine_style,
                flavor_profile.season,
                json.dumps(flavor_profile.dietary_tags),
                flavor_profile.complexity_score,
                flavor_profile.harmony_score,
                flavor_profile.ingredient_count,
                flavor_profile.technique_difficulty
            ))
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving flavor profile: {e}")
            return False
    
    def analyze_and_save_recipes(self, limit: int = None) -> Dict[str, int]:
        """Analyze and save flavor profiles for recipes without them"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Find recipes without flavor profiles
            limit_clause = f"LIMIT {limit}" if limit else ""
            cursor.execute(f"""
                SELECT r.id, r.title, r.ingredients, r.instructions
                FROM recipes r
                LEFT JOIN recipe_flavor_profiles fp ON r.id = fp.recipe_id
                WHERE fp.recipe_id IS NULL
                AND r.ingredients IS NOT NULL
                ORDER BY r.id
                {limit_clause}
            """)
            
            recipes = cursor.fetchall()
            
            print(f"🎨 Found {len(recipes)} recipes to analyze")
            
            processed = 0
            errors = 0
            
            for recipe in recipes:
                try:
                    # Analyze recipe
                    flavor_profile = self.analyze_recipe(dict(recipe))
                    
                    # Save to database
                    if self.save_flavor_profile(flavor_profile):
                        processed += 1
                    else:
                        errors += 1
                    
                    # Progress update
                    if processed % 50 == 0:
                        print(f"  ✓ Processed {processed}/{len(recipes)} recipes...")
                        
                except Exception as e:
                    print(f"  ❌ Error analyzing recipe {recipe['id']}: {e}")
                    errors += 1
                    continue
            
            print(f"\n✅ Flavor profile analysis complete!")
            print(f"   Processed: {processed}/{len(recipes)} recipes")
            print(f"   Errors: {errors}")
            
            return {
                'total_found': len(recipes),
                'processed': processed,
                'errors': errors
            }
            
        except Exception as e:
            print(f"❌ Error in batch analysis: {e}")
            return {'total_found': 0, 'processed': 0, 'errors': 1}

def main():
    """Test the flavor analyzer"""
    analyzer = RecipeFlavorAnalyzer()
    
    # Analyze first 10 recipes as a test
    results = analyzer.analyze_and_save_recipes(limit=10)
    print(f"\n📊 Test Results: {results}")

if __name__ == "__main__":
    main()
