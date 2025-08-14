#!/usr/bin/env python3
"""
Ingredient Network Analysis - Phase 1
Extract and analyze ingredient relationships from existing recipe database
Part of the culinary intelligence network enhancement
"""

import sqlite3
import json
import re
from collections import defaultdict, Counter
from datetime import datetime

class IngredientNetworkAnalyzer:
    def __init__(self, db_path='hungie.db'):
        self.db_path = db_path
        self.ingredient_patterns = {}
        self.ingredient_cooccurrence = defaultdict(lambda: defaultdict(int))
        self.recipe_ingredients = {}
        self.ingredient_frequencies = Counter()
        
    def extract_ingredients_from_text(self, ingredients_text):
        """Extract individual ingredients from recipe ingredient text"""
        if not ingredients_text:
            return []
        
        # Split by common delimiters and clean
        ingredients = []
        
        # Split by newlines, semicolons, or numbered lists
        raw_ingredients = re.split(r'[\n;]|\d+\.', ingredients_text)
        
        for ingredient in raw_ingredients:
            # Clean the ingredient text
            cleaned = ingredient.strip()
            if not cleaned:
                continue
                
            # Remove measurements and common prefixes
            cleaned = re.sub(r'^\d+[\s\w]*\s+', '', cleaned)  # Remove "2 cups", "1 large", etc.
            cleaned = re.sub(r'^[\d/\s]+', '', cleaned)       # Remove fractions
            cleaned = re.sub(r'\([^)]*\)', '', cleaned)       # Remove parentheses
            cleaned = re.sub(r',.*$', '', cleaned)            # Remove everything after comma
            cleaned = cleaned.lower().strip()
            
            if len(cleaned) > 2:  # Only keep meaningful ingredients
                ingredients.append(cleaned)
        
        return ingredients
    
    def normalize_ingredient_name(self, ingredient):
        """Normalize ingredient names for better matching"""
        # Remove common cooking terms
        stopwords = ['fresh', 'dried', 'chopped', 'diced', 'sliced', 'minced', 
                    'ground', 'whole', 'large', 'small', 'medium', 'organic',
                    'kosher', 'sea', 'extra virgin', 'virgin', 'raw', 'cooked']
        
        words = ingredient.split()
        filtered_words = [w for w in words if w not in stopwords]
        
        # Handle plurals
        normalized = ' '.join(filtered_words)
        if normalized.endswith('s') and len(normalized) > 3:
            singular = normalized[:-1]
            # Check if singular makes sense (avoid "gas" -> "ga")
            if len(singular) > 2:
                normalized = singular
                
        return normalized
    
    def analyze_database(self):
        """Analyze all recipes in database for ingredient patterns"""
        print("🔍 Analyzing ingredient patterns in recipe database...")
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, title, ingredients FROM recipes WHERE ingredients IS NOT NULL")
        recipes = cursor.fetchall()
        
        print(f"📊 Processing {len(recipes)} recipes...")
        
        for recipe in recipes:
            recipe_id = recipe['id']
            title = recipe['title']
            ingredients_text = recipe['ingredients']
            
            # Extract ingredients
            raw_ingredients = self.extract_ingredients_from_text(ingredients_text)
            normalized_ingredients = [self.normalize_ingredient_name(ing) for ing in raw_ingredients]
            
            # Filter out empty or very short ingredients
            meaningful_ingredients = [ing for ing in normalized_ingredients if len(ing) > 2]
            
            # Store recipe ingredients
            self.recipe_ingredients[recipe_id] = {
                'title': title,
                'ingredients': meaningful_ingredients
            }
            
            # Count ingredient frequencies
            for ingredient in meaningful_ingredients:
                self.ingredient_frequencies[ingredient] += 1
            
            # Build co-occurrence matrix
            for i, ing1 in enumerate(meaningful_ingredients):
                for j, ing2 in enumerate(meaningful_ingredients):
                    if i != j:  # Don't count ingredient with itself
                        self.ingredient_cooccurrence[ing1][ing2] += 1
        
        conn.close()
        print(f"✅ Analysis complete! Found {len(self.ingredient_frequencies)} unique ingredients")
        
    def get_ingredient_network(self, target_ingredient, min_cooccurrence=2):
        """Get ingredients that commonly appear with target ingredient"""
        target_normalized = self.normalize_ingredient_name(target_ingredient.lower())
        
        # Find exact and partial matches
        matches = []
        for ingredient in self.ingredient_frequencies:
            if target_normalized in ingredient or ingredient in target_normalized:
                matches.append(ingredient)
        
        if not matches:
            return {"error": f"No ingredients found matching '{target_ingredient}'"}
        
        # Get co-occurring ingredients for all matches
        network = defaultdict(int)
        recipes_with_ingredient = []
        
        for match in matches:
            # Get co-occurring ingredients
            for coingredient, count in self.ingredient_cooccurrence[match].items():
                if count >= min_cooccurrence:
                    network[coingredient] += count
            
            # Get recipes containing this ingredient
            for recipe_id, recipe_data in self.recipe_ingredients.items():
                if match in recipe_data['ingredients']:
                    recipes_with_ingredient.append({
                        'id': recipe_id,
                        'title': recipe_data['title'],
                        'matched_ingredient': match
                    })
        
        return {
            'target_ingredient': target_ingredient,
            'matched_ingredients': matches,
            'co_occurring_ingredients': dict(sorted(network.items(), key=lambda x: x[1], reverse=True)),
            'recipes_found': recipes_with_ingredient,
            'total_recipes': len(recipes_with_ingredient)
        }
    
    def get_top_ingredients(self, limit=50):
        """Get most common ingredients across all recipes"""
        return dict(self.ingredient_frequencies.most_common(limit))
    
    def save_analysis_results(self, filename=None):
        """Save analysis results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/ingredient_analysis_{timestamp}.json"
        
        results = {
            'analysis_date': datetime.now().isoformat(),
            'total_recipes_analyzed': len(self.recipe_ingredients),
            'total_unique_ingredients': len(self.ingredient_frequencies),
            'top_ingredients': self.get_top_ingredients(100),
            'ingredient_cooccurrence_sample': {
                k: dict(v) for k, v in list(self.ingredient_cooccurrence.items())[:10]
            }
        }
        
        import os
        os.makedirs('data', exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📄 Analysis results saved to: {filename}")
        return filename

def main():
    """Run ingredient network analysis"""
    print("🧠 Starting Ingredient Network Analysis")
    print("=" * 50)
    
    analyzer = IngredientNetworkAnalyzer()
    
    # Analyze database
    analyzer.analyze_database()
    
    # Test with sweet potato
    print("\n🍠 Testing with 'sweet potato':")
    sweet_potato_network = analyzer.get_ingredient_network('sweet potato')
    
    if 'error' not in sweet_potato_network:
        print(f"✅ Found {sweet_potato_network['total_recipes']} recipes")
        print("🔗 Top co-occurring ingredients:")
        for ingredient, count in list(sweet_potato_network['co_occurring_ingredients'].items())[:10]:
            print(f"   - {ingredient}: {count} recipes")
    else:
        print(f"❌ {sweet_potato_network['error']}")
    
    # Show top ingredients overall
    print(f"\n📊 Top 20 ingredients across all recipes:")
    top_ingredients = analyzer.get_top_ingredients(20)
    for ingredient, count in top_ingredients.items():
        print(f"   - {ingredient}: {count} recipes")
    
    # Save results
    results_file = analyzer.save_analysis_results()
    
    print(f"\n🎯 Next steps:")
    print(f"   1. Review results in: {results_file}")
    print(f"   2. Update search system with ingredient network")
    print(f"   3. Add recipe type classification")
    print(f"   4. Enhance chat conversation flow")

if __name__ == "__main__":
    main()
