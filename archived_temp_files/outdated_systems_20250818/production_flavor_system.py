"""
Production FlavorProfile System - Clean Integration
Advanced culinary intelligence for recipe enhancement and ingredient recommendations

This system provides professional-grade flavor pairing analysis based on expert culinary knowledge
extracted from comprehensive culinary databases. Clean, production-ready implementation.
"""
import json
import sqlite3
import os
import re
from typing import Dict, List, Set, Tuple, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import glob

@dataclass
class CulinaryProfile:
    """Professional culinary profile with expert-validated pairings"""
    flavor_notes: List[str]
    intensity: str
    seasonal_optimal: List[str]
    cooking_methods: List[str]
    expert_pairings: Dict[str, float]  # ingredient -> compatibility (0.8-0.95)
    properties: Dict[str, str]
    categories: List[str]

class FlavorProfileSystem:
    """Production FlavorProfile system with comprehensive culinary intelligence"""
    
    def __init__(self, db_path: str = 'hungie.db'):
        self.db_path = db_path
        self.culinary_db = {}
        self.ingredient_lookup = {}
        self.strength_levels = {
            'essential': 0.95,     # Must-have combinations
            'expert': 0.90,        # Chef-recommended
            'professional': 0.85,  # Strong recommendations
            'good': 0.80          # Solid pairings
        }
        self._initialize_system()
        
    def _initialize_system(self):
        """Initialize the culinary intelligence system"""
        
        print("🍳 Initializing Advanced FlavorProfile System...")
        
        # Load comprehensive culinary data
        culinary_data = self._load_culinary_database()
        
        if culinary_data:
            self._process_culinary_data(culinary_data)
        else:
            print("⚠️  No culinary data found, using core profiles")
            self._load_core_profiles()
        
        print(f"✅ FlavorProfile System ready: {len(self.culinary_db)} ingredients")
    
    def _load_culinary_database(self) -> Dict:
        """Load the latest culinary database"""
        
        data_dir = "flavor_bible_data"
        if not os.path.exists(data_dir):
            return {}
            
        pattern = os.path.join(data_dir, "fixed_parser_results_*.json")
        files = glob.glob(pattern)
        
        if not files:
            return {}
        
        latest_file = max(files, key=os.path.getctime)
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _process_culinary_data(self, data: Dict):
        """Process comprehensive culinary data into clean profiles"""
        
        processed_count = 0
        total_pairings = 0
        
        for page_data in data.values():
            if 'ingredient_sections' not in page_data:
                continue
                
            for ingredient_name, ingredient_data in page_data['ingredient_sections'].items():
                # Clean ingredient name
                clean_name = self._normalize_ingredient(ingredient_name)
                if not clean_name or len(clean_name) < 2:
                    continue
                
                # Create culinary profile
                profile = self._build_culinary_profile(clean_name, ingredient_data)
                
                if profile and len(profile.expert_pairings) >= 3:
                    self.culinary_db[clean_name] = profile
                    self._index_ingredient_variants(clean_name)
                    processed_count += 1
                    total_pairings += len(profile.expert_pairings)
        
        print(f"📊 Processed {processed_count} ingredients, {total_pairings} expert pairings")
    
    def _normalize_ingredient(self, name: str) -> str:
        """Normalize ingredient names for consistent indexing"""
        
        if not name:
            return ""
        
        # Convert to lowercase and clean
        normalized = name.lower().strip()
        
        # Remove common descriptors that don't affect flavor pairing
        descriptors_to_remove = [
            "— in general", "— general", " in general", " - general",
            "— fresh", "— dried", "— ground", "— whole", "— chopped",
            "— sliced", "— minced", " (see", " - see"
        ]
        
        for descriptor in descriptors_to_remove:
            normalized = normalized.replace(descriptor, "")
        
        # Consolidate major ingredient categories
        if normalized.startswith("cheese") or "cheese" in normalized:
            return "cheese"
        elif normalized.startswith("beef") or normalized == "meat":
            return "beef"
        elif normalized.startswith("pork"):
            return "pork"
        elif normalized.startswith("chicken") or normalized.startswith("poultry"):
            return "chicken"
        elif any(fish in normalized for fish in ["fish", "salmon", "tuna", "seafood"]):
            return "seafood"
        elif normalized.startswith("mushroom") or normalized == "fungi":
            return "mushrooms"
        elif "herbs" in normalized or normalized.endswith(" herb"):
            return "herbs"
        elif "spices" in normalized or normalized.endswith(" spice"):
            return "spices"
        
        # Final cleaning
        normalized = re.sub(r'[^a-zA-Z\\s]', '', normalized)
        normalized = ' '.join(normalized.split())
        
        return normalized if len(normalized) >= 2 else ""
    
    def _build_culinary_profile(self, ingredient: str, data: Dict) -> Optional[CulinaryProfile]:
        """Build a comprehensive culinary profile"""
        
        try:
            properties = data.get('properties', {})
            
            # Extract flavor characteristics
            flavor_notes = self._extract_flavor_notes(properties)
            
            # Determine intensity level
            intensity = self._classify_intensity(properties)
            
            # Extract seasonal information
            seasonal_optimal = self._extract_seasonality(data)
            
            # Extract cooking methods
            cooking_methods = self._extract_cooking_methods(properties)
            
            # Process clean pairings
            expert_pairings = self._extract_clean_pairings(data.get('pairings', {}))
            
            # Categorize the ingredient
            categories = self._categorize_ingredient(ingredient, flavor_notes, properties)
            
            if not expert_pairings:
                return None
            
            return CulinaryProfile(
                flavor_notes=flavor_notes,
                intensity=intensity,
                seasonal_optimal=seasonal_optimal,
                cooking_methods=cooking_methods,
                expert_pairings=expert_pairings,
                properties=properties,
                categories=categories
            )
            
        except Exception:
            return None
    
    def _extract_flavor_notes(self, properties: Dict) -> List[str]:
        """Extract flavor notes from properties"""
        
        notes = []
        
        if 'taste' in properties:
            taste_desc = properties['taste'].lower()
            
            # Common flavor descriptors
            flavor_keywords = {
                'sweet': 'sweet',
                'savory': 'savory', 'umami': 'savory',
                'sour': 'acidic', 'tart': 'acidic', 'bright': 'acidic',
                'bitter': 'bitter',
                'rich': 'rich', 'creamy': 'rich', 'fatty': 'rich',
                'spicy': 'spicy', 'hot': 'spicy',
                'mild': 'mild', 'delicate': 'mild',
                'pungent': 'pungent', 'strong': 'pungent'
            }
            
            for keyword, note in flavor_keywords.items():
                if keyword in taste_desc and note not in notes:
                    notes.append(note)
        
        return notes if notes else ['neutral']
    
    def _classify_intensity(self, properties: Dict) -> str:
        """Classify flavor intensity"""
        
        if 'weight' in properties:
            weight = properties['weight'].lower()
            if any(light in weight for light in ['light', 'delicate', 'subtle']):
                return 'subtle'
            elif any(heavy in weight for heavy in ['heavy', 'rich', 'intense', 'strong']):
                return 'bold'
        
        return 'moderate'
    
    def _extract_seasonality(self, data: Dict) -> List[str]:
        """Extract seasonal information"""
        
        seasons = []
        
        # Check various data sources for seasonal mentions
        all_text = []
        all_text.extend(data.get('properties', {}).values())
        all_text.extend(data.get('raw_pairings', [])[:3])  # First few pairings
        
        combined_text = ' '.join(str(item).lower() for item in all_text)
        
        season_keywords = {
            'spring': 'spring',
            'summer': 'summer',
            'fall': 'fall', 'autumn': 'fall',
            'winter': 'winter'
        }
        
        for keyword, season in season_keywords.items():
            if keyword in combined_text and season not in seasons:
                seasons.append(season)
        
        return seasons if seasons else ['year-round']
    
    def _extract_cooking_methods(self, properties: Dict) -> List[str]:
        """Extract optimal cooking methods"""
        
        methods = []
        
        if 'techniques' in properties:
            tech_text = properties['techniques'].lower()
            
            method_mapping = {
                'grill': 'grilling', 'barbecue': 'grilling',
                'roast': 'roasting', 'bake': 'roasting', 'oven': 'roasting',
                'sauté': 'sautéing', 'pan-fry': 'sautéing', 'fry': 'frying',
                'braise': 'braising', 'stew': 'braising', 'slow': 'braising',
                'steam': 'steaming',
                'poach': 'poaching',
                'raw': 'fresh', 'fresh': 'fresh', 'salad': 'fresh'
            }
            
            for keyword, method in method_mapping.items():
                if keyword in tech_text and method not in methods:
                    methods.append(method)
        
        return methods if methods else ['versatile']
    
    def _extract_clean_pairings(self, pairings_data: Dict) -> Dict[str, float]:
        """Extract and clean pairings with quality validation"""
        
        clean_pairings = {}
        
        # Process different formatting strengths
        strength_mapping = [
            ('bold_caps', 0.95),  # Essential pairings
            ('bold_only', 0.90),  # Expert level
            ('caps_only', 0.85),  # Professional
            ('plain_text', 0.80)  # Good pairings
        ]
        
        for category, strength in strength_mapping:
            if category in pairings_data:
                for pairing in pairings_data[category]:
                    clean_pairing = self._validate_pairing(pairing)
                    if clean_pairing:
                        clean_pairings[clean_pairing] = strength
        
        return clean_pairings
    
    def _validate_pairing(self, pairing: str) -> Optional[str]:
        """Validate and clean individual pairings"""
        
        if not pairing or len(pairing) < 2:
            return None
        
        # Remove invalid patterns
        invalid_patterns = [
            r'taste:', r'weight:', r'volume:', r'season:', r'techniques:',
            r'function:', r'tips:', r'see also', r'chef:', r'restaurant',
            r'page \\d+', r'flavor affinities', r'dishes?:',
            r'^[^a-zA-Z]+$',  # Non-alphabetic
            r'\\([^)]*\\)$'   # Parenthetical notes
        ]
        
        pairing_lower = pairing.lower()
        for pattern in invalid_patterns:
            if re.search(pattern, pairing_lower):
                return None
        
        # Length constraints
        if len(pairing) > 40:  # Too long
            return None
        
        # Clean the pairing
        cleaned = re.sub(r'[^a-zA-Z\\s,]', '', pairing)
        cleaned = ' '.join(cleaned.split()).lower().strip()
        
        # Final validation
        if len(cleaned) < 2 or cleaned in ['and', 'or', 'with', 'the', 'a', 'an', 'is', 'are']:
            return None
        
        return cleaned
    
    def _categorize_ingredient(self, ingredient: str, flavor_notes: List[str], properties: Dict) -> List[str]:
        """Categorize ingredient by type and flavor profile"""
        
        categories = []
        
        # Type-based categories
        type_mapping = {
            'protein': ['beef', 'pork', 'chicken', 'seafood', 'lamb', 'turkey'],
            'vegetable': ['onion', 'garlic', 'tomato', 'pepper', 'carrot', 'celery'],
            'herb': ['basil', 'thyme', 'rosemary', 'parsley', 'oregano', 'cilantro'],
            'spice': ['pepper', 'cinnamon', 'cumin', 'paprika', 'ginger'],
            'dairy': ['cheese', 'butter', 'cream', 'yogurt'],
            'grain': ['rice', 'pasta', 'bread', 'quinoa']
        }
        
        for category, keywords in type_mapping.items():
            if any(keyword in ingredient for keyword in keywords):
                categories.append(category)
                break
        
        # Flavor-based categories
        for note in flavor_notes:
            if note in ['sweet', 'savory', 'acidic', 'rich', 'spicy']:
                categories.append(note)
        
        return categories if categories else ['general']
    
    def _index_ingredient_variants(self, ingredient: str):
        """Create searchable variants for ingredient"""
        
        variants = [ingredient]
        
        # Plural/singular variations
        if ingredient.endswith('s') and len(ingredient) > 3:
            variants.append(ingredient[:-1])
        else:
            variants.append(ingredient + 's')
        
        # Common aliases
        aliases = {
            'beef': ['meat', 'steak', 'ground beef'],
            'chicken': ['poultry', 'fowl'],
            'seafood': ['fish', 'salmon'],
            'mushrooms': ['fungi', 'mushroom'],
            'herbs': ['herb', 'fresh herbs'],
            'cheese': ['dairy']
        }
        
        if ingredient in aliases:
            variants.extend(aliases[ingredient])
        
        # Index all variants
        for variant in variants:
            self.ingredient_lookup[variant.lower().strip()] = ingredient
    
    def _load_core_profiles(self):
        """Load essential core profiles as fallback"""
        
        core_profiles = {
            'salt': CulinaryProfile(
                flavor_notes=['salty', 'enhancing'],
                intensity='moderate',
                seasonal_optimal=['year-round'],
                cooking_methods=['universal'],
                expert_pairings={'everything': 0.80},
                properties={'function': 'enhancement'},
                categories=['seasoning']
            ),
            'garlic': CulinaryProfile(
                flavor_notes=['pungent', 'savory'],
                intensity='bold',
                seasonal_optimal=['year-round'],
                cooking_methods=['sautéing', 'roasting'],
                expert_pairings={'olive oil': 0.95, 'herbs': 0.90, 'onion': 0.90},
                properties={'taste': 'pungent'},
                categories=['aromatic', 'vegetable']
            ),
            'onion': CulinaryProfile(
                flavor_notes=['savory', 'sweet'],
                intensity='moderate',
                seasonal_optimal=['year-round'],
                cooking_methods=['sautéing', 'roasting'],
                expert_pairings={'garlic': 0.90, 'herbs': 0.85, 'butter': 0.85},
                properties={'taste': 'savory'},
                categories=['aromatic', 'vegetable']
            )
        }
        
        for ingredient, profile in core_profiles.items():
            self.culinary_db[ingredient] = profile
            self._index_ingredient_variants(ingredient)
    
    def get_compatibility_score(self, ingredient1: str, ingredient2: str, 
                              cooking_method: str = None, season: str = None) -> float:
        """Get compatibility score between two ingredients"""
        
        # Resolve ingredients
        ing1 = self._resolve_ingredient(ingredient1)
        ing2 = self._resolve_ingredient(ingredient2)
        
        base_score = 0.5  # neutral default
        
        # Check direct pairings
        if ing1 in self.culinary_db:
            profile1 = self.culinary_db[ing1]
            if ing2 in profile1.expert_pairings:
                base_score = profile1.expert_pairings[ing2]
        
        if ing2 in self.culinary_db and base_score == 0.5:
            profile2 = self.culinary_db[ing2]
            if ing1 in profile2.expert_pairings:
                base_score = profile2.expert_pairings[ing1]
        
        # Apply contextual modifiers
        if cooking_method:
            base_score += self._get_method_modifier(ing1, ing2, cooking_method)
        
        if season:
            base_score += self._get_seasonal_modifier(ing1, ing2, season)
        
        return min(1.0, max(0.0, base_score))
    
    def _resolve_ingredient(self, ingredient: str) -> str:
        """Resolve ingredient through lookup table"""
        clean_name = ingredient.lower().strip()
        return self.ingredient_lookup.get(clean_name, clean_name)
    
    def _get_method_modifier(self, ing1: str, ing2: str, method: str) -> float:
        """Get cooking method compatibility modifier"""
        
        modifier = 0.0
        
        for ing in [ing1, ing2]:
            if ing in self.culinary_db:
                profile = self.culinary_db[ing]
                if method in profile.cooking_methods or 'versatile' in profile.cooking_methods:
                    modifier += 0.02
        
        return modifier
    
    def _get_seasonal_modifier(self, ing1: str, ing2: str, season: str) -> float:
        """Get seasonal compatibility modifier"""
        
        modifier = 0.0
        
        for ing in [ing1, ing2]:
            if ing in self.culinary_db:
                profile = self.culinary_db[ing]
                if season in profile.seasonal_optimal or 'year-round' in profile.seasonal_optimal:
                    modifier += 0.03
        
        return modifier
    
    def analyze_recipe_harmony(self, ingredients: List[str], 
                             cooking_method: str = None, season: str = None) -> Dict[str, Any]:
        """Analyze overall recipe harmony"""
        
        if len(ingredients) < 2:
            return {
                'harmony_score': 0.5,
                'rating': 'Insufficient ingredients',
                'analysis': 'Need at least 2 ingredients for harmony analysis'
            }
        
        # Calculate all pairwise compatibilities
        compatibility_scores = []
        pairing_details = []
        
        for i, ing1 in enumerate(ingredients):
            for j, ing2 in enumerate(ingredients[i+1:], i+1):
                score = self.get_compatibility_score(ing1, ing2, cooking_method, season)
                compatibility_scores.append(score)
                
                pairing_details.append({
                    'ingredient1': ing1,
                    'ingredient2': ing2,
                    'compatibility': round(score, 3),
                    'rating': self._get_compatibility_rating(score)
                })
        
        # Calculate overall harmony
        if compatibility_scores:
            harmony_score = sum(compatibility_scores) / len(compatibility_scores)
            
            # Sort pairings by compatibility
            sorted_pairings = sorted(pairing_details, key=lambda x: x['compatibility'], reverse=True)
            
            return {
                'harmony_score': round(harmony_score, 3),
                'overall_rating': self._get_compatibility_rating(harmony_score),
                'best_pairings': sorted_pairings[:3],
                'concerning_pairings': [p for p in sorted_pairings if p['compatibility'] < 0.4],
                'total_combinations': len(compatibility_scores),
                'database_coverage': self._calculate_coverage(ingredients),
                'cooking_method': cooking_method,
                'season': season
            }
        
        return {'harmony_score': 0.5, 'overall_rating': 'Analysis incomplete'}
    
    def suggest_ingredient_additions(self, base_ingredients: List[str], 
                                   limit: int = 8, cooking_method: str = None, 
                                   season: str = None) -> List[Dict[str, Any]]:
        """Suggest ingredients that pair well with the base ingredients"""
        
        suggestions = {}
        
        for base_ing in base_ingredients:
            resolved_base = self._resolve_ingredient(base_ing)
            
            if resolved_base in self.culinary_db:
                profile = self.culinary_db[resolved_base]
                
                for pairing, base_strength in profile.expert_pairings.items():
                    # Skip if already in base ingredients
                    if pairing in [self._resolve_ingredient(ing) for ing in base_ingredients]:
                        continue
                    
                    # Calculate enhanced score
                    enhanced_score = base_strength
                    
                    if cooking_method:
                        enhanced_score += self._get_method_modifier(resolved_base, pairing, cooking_method)
                    
                    if season:
                        enhanced_score += self._get_seasonal_modifier(resolved_base, pairing, season)
                    
                    # Accumulate suggestions
                    if pairing in suggestions:
                        suggestions[pairing]['total_score'] += enhanced_score
                        suggestions[pairing]['recommended_by'].append(base_ing)
                        suggestions[pairing]['count'] += 1
                    else:
                        suggestions[pairing] = {
                            'ingredient': pairing,
                            'total_score': enhanced_score,
                            'base_strength': base_strength,
                            'recommended_by': [base_ing],
                            'count': 1,
                            'strength_level': self._get_strength_level(base_strength)
                        }
        
        # Calculate final scores
        for suggestion in suggestions.values():
            avg_score = suggestion['total_score'] / suggestion['count']
            suggestion['final_score'] = round(avg_score, 3)
            suggestion['compatibility_rating'] = self._get_compatibility_rating(avg_score)
        
        # Sort by final score and recommendation count
        sorted_suggestions = sorted(
            suggestions.values(), 
            key=lambda x: (x['final_score'], x['count']), 
            reverse=True
        )
        
        return sorted_suggestions[:limit]
    
    def _get_compatibility_rating(self, score: float) -> str:
        """Get human-readable compatibility rating"""
        if score >= 0.95:
            return 'Essential Pairing'
        elif score >= 0.90:
            return 'Expert Recommended'
        elif score >= 0.85:
            return 'Highly Compatible'
        elif score >= 0.80:
            return 'Good Match'
        elif score >= 0.70:
            return 'Compatible'
        elif score >= 0.60:
            return 'Acceptable'
        elif score >= 0.50:
            return 'Neutral'
        else:
            return 'Poor Match'
    
    def _get_strength_level(self, score: float) -> str:
        """Get strength level description"""
        if score >= 0.95:
            return 'Essential'
        elif score >= 0.90:
            return 'Expert'
        elif score >= 0.85:
            return 'Professional'
        else:
            return 'Good'
    
    def _calculate_coverage(self, ingredients: List[str]) -> Dict[str, Any]:
        """Calculate database coverage for ingredients"""
        
        covered = []
        not_covered = []
        
        for ing in ingredients:
            resolved = self._resolve_ingredient(ing)
            if resolved in self.culinary_db:
                covered.append(ing)
            else:
                not_covered.append(ing)
        
        coverage_percentage = (len(covered) / len(ingredients) * 100) if ingredients else 0
        
        return {
            'percentage': round(coverage_percentage, 1),
            'covered': covered,
            'not_covered': not_covered,
            'total_database_size': len(self.culinary_db)
        }
    
    def get_ingredient_profile(self, ingredient: str) -> Optional[CulinaryProfile]:
        """Get complete culinary profile for an ingredient"""
        resolved = self._resolve_ingredient(ingredient)
        return self.culinary_db.get(resolved)

# Production integration functions
def enhance_recipe_with_flavor_intelligence(recipe_data: Dict[str, Any]) -> Dict[str, Any]:
    """Enhance a recipe with flavor intelligence"""
    
    # Initialize the system
    flavor_system = FlavorProfileSystem()
    
    # Extract ingredients
    ingredients = []
    if 'ingredients' in recipe_data:
        for ing in recipe_data['ingredients']:
            if isinstance(ing, dict):
                ingredients.append(ing.get('name', str(ing)))
            else:
                ingredients.append(str(ing))
    
    # Detect cooking method
    cooking_method = 'sautéing'  # default
    if 'instructions' in recipe_data:
        instructions = ' '.join([str(inst) for inst in recipe_data['instructions']]).lower()
        
        if 'grill' in instructions:
            cooking_method = 'grilling'
        elif 'roast' in instructions or 'bake' in instructions:
            cooking_method = 'roasting'
        elif 'braise' in instructions or 'slow cook' in instructions:
            cooking_method = 'braising'
        elif 'steam' in instructions:
            cooking_method = 'steaming'
    
    # Analyze harmony
    harmony_analysis = flavor_system.analyze_recipe_harmony(ingredients, cooking_method, 'fall')
    
    # Get suggestions
    suggestions = flavor_system.suggest_ingredient_additions(ingredients, limit=8, cooking_method=cooking_method)
    
    return {
        'harmony_analysis': harmony_analysis,
        'ingredient_suggestions': suggestions,
        'detected_cooking_method': cooking_method,
        'enhancement_type': 'advanced_flavor_intelligence'
    }

if __name__ == "__main__":
    # Test the production system
    print("🎯 Testing Advanced FlavorProfile System")
    print("=" * 45)
    
    system = FlavorProfileSystem()
    
    # Test compatibility
    score = system.get_compatibility_score('beef', 'mushrooms', 'braising', 'fall')
    print(f"Beef + Mushrooms: {score:.3f} ({system._get_compatibility_rating(score)})")
    
    # Test recipe analysis
    test_recipe = {
        'ingredients': ['beef', 'mushrooms', 'onions', 'garlic'],
        'instructions': ['Braise the beef with vegetables until tender']
    }
    
    enhancement = enhance_recipe_with_flavor_intelligence(test_recipe)
    
    print(f"\\nRecipe Harmony Analysis:")
    harmony = enhancement['harmony_analysis']
    print(f"Score: {harmony['harmony_score']} ({harmony['overall_rating']})")
    print(f"Coverage: {harmony['database_coverage']['percentage']}%")
    
    print(f"\\nTop Ingredient Suggestions:")
    for i, suggestion in enumerate(enhancement['ingredient_suggestions'][:5], 1):
        print(f"{i}. {suggestion['ingredient']} - {suggestion['strength_level']} ({suggestion['final_score']})")
    
    print("\\n✅ Advanced FlavorProfile System Ready for Production!")
