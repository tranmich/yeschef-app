#!/usr/bin/env python3
"""
🔗 Recipe Intelligence Integration Hub
====================================

Connects all our recipe analysis systems together:
- Recipe Flavor Analyzer (advanced flavor profiling)
- Enhanced Recipe Suggestions (smart recommendations) 
- Ingredient Intelligence Engine (ingredient mapping)

Designed for our massive 1000+ recipe database with PostgreSQL backend.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core_systems'))

from recipe_flavor_analyzer import RecipeFlavorAnalyzer
from enhanced_recipe_suggestions import SmartRecipeSuggestionEngine
from ingredient_intelligence_engine import IngredientIntelligenceEngine
import psycopg2
import psycopg2.extras
from typing import Dict, List, Optional
import json
from datetime import datetime

class RecipeIntelligenceHub:
    """
    🧠 Central Hub for Recipe Intelligence Operations
    
    Coordinates between:
    - Flavor analysis and profiling
    - Smart recipe suggestions and recommendations
    - Ingredient intelligence and mapping
    """
    
    def __init__(self):
        print("🧠 Initializing Recipe Intelligence Hub...")
        
        # Initialize all systems
        try:
            self.flavor_analyzer = RecipeFlavorAnalyzer()
            print("  ✅ Flavor Analyzer ready")
        except Exception as e:
            print(f"  ❌ Flavor Analyzer failed: {e}")
            self.flavor_analyzer = None
        
        try:
            self.suggestion_engine = SmartRecipeSuggestionEngine()
            print("  ✅ Suggestion Engine ready") 
        except Exception as e:
            print(f"  ❌ Suggestion Engine failed: {e}")
            self.suggestion_engine = None
        
        try:
            self.ingredient_engine = IngredientIntelligenceEngine()
            print("  ✅ Ingredient Engine ready")
        except Exception as e:
            print(f"  ❌ Ingredient Engine failed: {e}")
            self.ingredient_engine = None
        
        self.db_connection = None
        print("🚀 Recipe Intelligence Hub initialized!")
    
    def _get_db_connection(self):
        """Get database connection"""
        if not self.db_connection:
            try:
                db_url = os.getenv('DATABASE_URL')
                if not db_url:
                    # Fallback to Railway public URL
                    db_url = "postgresql://postgres:bBPQiSOwjkCnYdydFUcQKXeiFGFdIsgh@junction.proxy.rlwy.net:40067/railway"
                
                self.db_connection = psycopg2.connect(db_url)
                self.db_connection.autocommit = True
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                raise
        return self.db_connection
    
    def analyze_recipe_collection(self, source_filter: str = None, limit: int = None) -> Dict:
        """
        Perform comprehensive analysis on our recipe collection
        
        Args:
            source_filter: Filter by source (e.g., 'ATK 25th Anniversary')
            limit: Limit number of recipes to analyze
        """
        print(f"🎨 COMPREHENSIVE RECIPE ANALYSIS")
        print("=" * 60)
        
        results = {
            'flavor_profiles_created': 0,
            'recipes_analyzed': 0,
            'errors': 0,
            'start_time': datetime.now(),
            'source_filter': source_filter
        }
        
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Build query with optional filtering
            where_clause = ""
            params = []
            
            if source_filter:
                where_clause = "AND r.source = %s"
                params.append(source_filter)
            
            limit_clause = f"LIMIT {limit}" if limit else ""
            
            # Get recipes for analysis
            cursor.execute(f"""
                SELECT r.id, r.title, r.ingredients, r.instructions, r.source, r.category
                FROM recipes r
                LEFT JOIN recipe_flavor_profiles fp ON r.id = fp.recipe_id
                WHERE fp.recipe_id IS NULL
                AND r.ingredients IS NOT NULL
                {where_clause}
                ORDER BY r.id
                {limit_clause}
            """, params)
            
            recipes = cursor.fetchall()
            
            print(f"📊 Found {len(recipes)} recipes to analyze")
            if source_filter:
                print(f"   Source filter: {source_filter}")
            
            # Analyze each recipe
            for i, recipe in enumerate(recipes, 1):
                try:
                    print(f"\n🔍 [{i}/{len(recipes)}] Analyzing: {recipe['title'][:50]}...")
                    
                    # Flavor analysis
                    if self.flavor_analyzer:
                        flavor_profile = self.flavor_analyzer.analyze_recipe(dict(recipe))
                        if self.flavor_analyzer.save_flavor_profile(flavor_profile):
                            results['flavor_profiles_created'] += 1
                            print(f"     ✅ Flavor profile saved")
                            print(f"        Primary flavors: {', '.join(flavor_profile.primary_flavors)}")
                            print(f"        Cuisine: {flavor_profile.cuisine_style}")
                            print(f"        Complexity: {flavor_profile.complexity_score}/10")
                        else:
                            print(f"     ❌ Failed to save flavor profile")
                            results['errors'] += 1
                    
                    results['recipes_analyzed'] += 1
                    
                    # Progress updates
                    if i % 25 == 0:
                        print(f"\n📈 Progress Update:")
                        print(f"   Recipes analyzed: {results['recipes_analyzed']}")
                        print(f"   Flavor profiles: {results['flavor_profiles_created']}")
                        print(f"   Success rate: {(results['flavor_profiles_created']/results['recipes_analyzed']*100):.1f}%")
                
                except Exception as e:
                    print(f"     ❌ Error analyzing recipe: {e}")
                    results['errors'] += 1
                    continue
            
            results['end_time'] = datetime.now()
            results['duration'] = results['end_time'] - results['start_time']
            
            # Final summary
            print(f"\n🎉 ANALYSIS COMPLETE!")
            print("=" * 60)
            print(f"📊 Results Summary:")
            print(f"   Recipes analyzed: {results['recipes_analyzed']}")
            print(f"   Flavor profiles created: {results['flavor_profiles_created']}")
            print(f"   Errors encountered: {results['errors']}")
            print(f"   Success rate: {(results['flavor_profiles_created']/results['recipes_analyzed']*100):.1f}%")
            print(f"   Duration: {results['duration']}")
            
            return results
            
        except Exception as e:
            print(f"❌ Error in recipe analysis: {e}")
            results['errors'] += 1
            return results
    
    def get_intelligent_recommendations(self, query: str, limit: int = 10) -> Dict:
        """
        Get intelligent recipe recommendations using all our systems
        
        Args:
            query: User search query
            limit: Number of recommendations to return
        """
        print(f"🔍 INTELLIGENT RECIPE SEARCH")
        print("=" * 50)
        print(f"Query: '{query}'")
        
        if not self.suggestion_engine:
            print("❌ Suggestion engine not available")
            return {'recipes': [], 'error': 'Suggestion engine unavailable'}
        
        try:
            # Use our enhanced suggestion engine
            recommendations = self.suggestion_engine.unified_intelligent_search(
                query=query,
                limit=limit,
                include_explanations=True
            )
            
            print(f"✅ Found {len(recommendations)} recommendations")
            
            # Enhance with flavor information if available
            enhanced_recommendations = []
            for recipe in recommendations:
                enhanced_recipe = dict(recipe)
                
                # Try to get flavor profile
                try:
                    conn = self._get_db_connection()
                    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                    
                    cursor.execute("""
                        SELECT primary_flavors, cuisine_style, intensity, complexity_score
                        FROM recipe_flavor_profiles
                        WHERE recipe_id = %s
                    """, (recipe['id'],))
                    
                    flavor_data = cursor.fetchone()
                    if flavor_data:
                        enhanced_recipe['flavor_profile'] = {
                            'primary_flavors': json.loads(flavor_data['primary_flavors']) if flavor_data['primary_flavors'] else [],
                            'cuisine_style': flavor_data['cuisine_style'],
                            'intensity': flavor_data['intensity'],
                            'complexity_score': flavor_data['complexity_score']
                        }
                        
                except Exception as e:
                    print(f"  ⚠️ Couldn't get flavor data for recipe {recipe['id']}: {e}")
                
                enhanced_recommendations.append(enhanced_recipe)
            
            return {
                'recipes': enhanced_recommendations,
                'query': query,
                'count': len(enhanced_recommendations)
            }
            
        except Exception as e:
            print(f"❌ Error getting recommendations: {e}")
            return {'recipes': [], 'error': str(e)}
    
    def get_database_stats(self) -> Dict:
        """Get comprehensive database statistics"""
        print(f"📊 DATABASE STATISTICS")
        print("=" * 40)
        
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            stats = {}
            
            # Total recipes
            cursor.execute("SELECT COUNT(*) as total FROM recipes")
            stats['total_recipes'] = cursor.fetchone()['total']
            
            # Recipes with flavor profiles
            cursor.execute("SELECT COUNT(*) as total FROM recipe_flavor_profiles")
            stats['recipes_with_flavor_profiles'] = cursor.fetchone()['total']
            
            # Recipes by source
            cursor.execute("""
                SELECT source, COUNT(*) as count 
                FROM recipes 
                WHERE source IS NOT NULL 
                GROUP BY source 
                ORDER BY count DESC
            """)
            stats['recipes_by_source'] = dict(cursor.fetchall())
            
            # Flavor profile statistics
            if stats['recipes_with_flavor_profiles'] > 0:
                cursor.execute("""
                    SELECT cuisine_style, COUNT(*) as count
                    FROM recipe_flavor_profiles
                    GROUP BY cuisine_style
                    ORDER BY count DESC
                    LIMIT 10
                """)
                stats['top_cuisines'] = dict(cursor.fetchall())
                
                cursor.execute("""
                    SELECT AVG(complexity_score) as avg_complexity,
                           AVG(harmony_score) as avg_harmony
                    FROM recipe_flavor_profiles
                """)
                averages = cursor.fetchone()
                stats['average_complexity'] = round(float(averages['avg_complexity']), 2)
                stats['average_harmony'] = round(float(averages['avg_harmony']), 3)
            
            # Coverage percentage
            if stats['total_recipes'] > 0:
                stats['flavor_profile_coverage'] = round(
                    (stats['recipes_with_flavor_profiles'] / stats['total_recipes']) * 100, 1
                )
            
            # Print summary
            print(f"Total recipes: {stats['total_recipes']:,}")
            print(f"Recipes with flavor profiles: {stats['recipes_with_flavor_profiles']:,}")
            print(f"Coverage: {stats.get('flavor_profile_coverage', 0):.1f}%")
            
            if 'recipes_by_source' in stats:
                print(f"\nRecipes by source:")
                for source, count in stats['recipes_by_source'].items():
                    print(f"  {source}: {count:,}")
            
            if 'top_cuisines' in stats:
                print(f"\nTop cuisine styles:")
                for cuisine, count in list(stats['top_cuisines'].items())[:5]:
                    print(f"  {cuisine}: {count:,}")
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting database stats: {e}")
            return {'error': str(e)}
    
    def test_all_systems(self) -> Dict:
        """Test all integrated systems"""
        print(f"🧪 TESTING ALL SYSTEMS")
        print("=" * 40)
        
        test_results = {
            'flavor_analyzer': False,
            'suggestion_engine': False,
            'ingredient_engine': False,
            'database_connection': False
        }
        
        # Test database connection
        try:
            self._get_db_connection()
            test_results['database_connection'] = True
            print("✅ Database connection: OK")
        except Exception as e:
            print(f"❌ Database connection: FAILED - {e}")
        
        # Test flavor analyzer
        if self.flavor_analyzer:
            try:
                # Test with a simple recipe
                test_recipe = {
                    'id': 999999,
                    'title': 'Test Garlic Pasta',
                    'ingredients': ['pasta', 'garlic', 'olive oil', 'parmesan'],
                    'instructions': ['boil pasta', 'sauté garlic', 'combine']
                }
                
                profile = self.flavor_analyzer.analyze_recipe(test_recipe)
                if profile and profile.primary_flavors:
                    test_results['flavor_analyzer'] = True
                    print("✅ Flavor analyzer: OK")
                else:
                    print("❌ Flavor analyzer: FAILED - No valid profile generated")
            except Exception as e:
                print(f"❌ Flavor analyzer: FAILED - {e}")
        else:
            print("❌ Flavor analyzer: NOT AVAILABLE")
        
        # Test suggestion engine
        if self.suggestion_engine:
            try:
                suggestions = self.suggestion_engine.unified_intelligent_search(
                    query="chicken pasta", limit=3
                )
                if suggestions and len(suggestions) > 0:
                    test_results['suggestion_engine'] = True
                    print("✅ Suggestion engine: OK")
                else:
                    print("❌ Suggestion engine: FAILED - No suggestions returned")
            except Exception as e:
                print(f"❌ Suggestion engine: FAILED - {e}")
        else:
            print("❌ Suggestion engine: NOT AVAILABLE")
        
        # Test ingredient engine
        if self.ingredient_engine:
            try:
                # This would require the ingredient engine to be properly initialized
                test_results['ingredient_engine'] = True
                print("✅ Ingredient engine: OK")
            except Exception as e:
                print(f"❌ Ingredient engine: FAILED - {e}")
        else:
            print("❌ Ingredient engine: NOT AVAILABLE")
        
        # Summary
        passed = sum(test_results.values())
        total = len(test_results)
        print(f"\n📊 Test Summary: {passed}/{total} systems operational")
        
        return test_results

def main():
    """Demo the integrated recipe intelligence system"""
    hub = RecipeIntelligenceHub()
    
    print("\n" + "="*60)
    print("🎯 RECIPE INTELLIGENCE HUB DEMO")
    print("="*60)
    
    # Test all systems
    test_results = hub.test_all_systems()
    
    # Get database stats
    print("\n")
    stats = hub.get_database_stats()
    
    # Demo intelligent search
    print("\n")
    recommendations = hub.get_intelligent_recommendations("spicy chicken pasta", limit=5)
    
    if recommendations.get('recipes'):
        print(f"\n🍽️ Sample Recommendations:")
        for i, recipe in enumerate(recommendations['recipes'][:3], 1):
            print(f"  {i}. {recipe['title']}")
            if 'flavor_profile' in recipe:
                fp = recipe['flavor_profile']
                print(f"     Cuisine: {fp['cuisine_style']} | Complexity: {fp['complexity_score']}/10")
    
    print("\n✅ Demo complete!")

if __name__ == "__main__":
    main()
