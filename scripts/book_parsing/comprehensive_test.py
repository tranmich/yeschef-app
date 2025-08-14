"""
Comprehensive test suite for the enhanced recipe analyzer
Shows off all the sophisticated analysis capabilities
"""
import requests
import json
from datetime import datetime

def test_enhanced_search_comprehensive():
    """Test various search scenarios to showcase analysis capabilities"""
    
    url = "http://localhost:8000/api/smart-search"
    
    # Comprehensive test queries showcasing different analysis dimensions
    test_scenarios = [
        {
            "name": "Cuisine & Heat Level",
            "query": "spicy asian noodles for dinner",
            "expected_features": ["asian cuisine", "heat level", "dinner timing"]
        },
        {
            "name": "Skill Level & Time",
            "query": "easy quick breakfast for beginners",
            "expected_features": ["beginner skill", "quick timing", "breakfast meal"]
        },
        {
            "name": "Dietary Restrictions",
            "query": "healthy vegetarian lunch recipes",
            "expected_features": ["dietary tags", "health orientation", "meal type"]
        },
        {
            "name": "Occasion & Social Context",
            "query": "comfort food for family dinner",
            "expected_features": ["social context", "comfort classification", "family oriented"]
        },
        {
            "name": "Cooking Method & Complexity",
            "query": "advanced italian pasta techniques",
            "expected_features": ["cuisine type", "skill level", "technique complexity"]
        },
        {
            "name": "Seasonal & Fresh Ingredients",
            "query": "fresh summer salads with vegetables",
            "expected_features": ["seasonal fit", "produce usage", "temperature"]
        },
        {
            "name": "Cost & Practicality",
            "query": "budget friendly chicken meals",
            "expected_features": ["cost estimate", "protein source", "practical considerations"]
        },
        {
            "name": "Texture & Experience",
            "query": "crispy fried appetizers for party",
            "expected_features": ["texture analysis", "social context", "meal type"]
        }
    ]
    
    print("🧪 COMPREHENSIVE ENHANCED SEARCH TEST")
    print("=" * 60)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🔍 Test {i}: {scenario['name']}")
        print(f"Query: '{scenario['query']}'")
        print("-" * 40)
        
        payload = {
            "message": scenario['query'],
            "context": ""
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                recipes = data.get('recipes', [])
                chat_response = data.get('chat_response', '')
                
                print(f"✅ Status: Success")
                print(f"📊 Results: {len(recipes)} recipes found")
                print(f"💬 Response: {chat_response[:120]}...")
                
                if recipes:
                    print(f"\n🔝 Top Results Analysis:")
                    
                    for j, recipe in enumerate(recipes[:3], 1):
                        print(f"   {j}. {recipe['name'][:50]}...")
                        
                        # Show analysis data
                        analysis_data = []
                        if recipe.get('cuisine_type'):
                            analysis_data.append(f"Cuisine: {recipe['cuisine_type']}")
                        if recipe.get('skill_level'):
                            analysis_data.append(f"Skill: {recipe['skill_level']}")
                        if recipe.get('heat_level') is not None:
                            analysis_data.append(f"Heat: {recipe['heat_level']}/10")
                        if recipe.get('meal_type'):
                            analysis_data.append(f"Meal: {recipe['meal_type']}")
                        if recipe.get('relevance_score'):
                            analysis_data.append(f"Score: {recipe['relevance_score']}")
                        
                        if analysis_data:
                            print(f"      📈 {' | '.join(analysis_data)}")
                        else:
                            print(f"      📈 No analysis data available")
                            
                    # Analysis insights
                    cuisines = set()
                    skill_levels = set()
                    heat_levels = []
                    meal_types = set()
                    
                    for recipe in recipes:
                        if recipe.get('cuisine_type'):
                            cuisines.add(recipe['cuisine_type'])
                        if recipe.get('skill_level'):
                            skill_levels.add(recipe['skill_level'])
                        if recipe.get('heat_level') is not None:
                            heat_levels.append(recipe['heat_level'])
                        if recipe.get('meal_type'):
                            meal_types.add(recipe['meal_type'])
                    
                    print(f"\n📊 Analysis Summary:")
                    if cuisines:
                        print(f"   🍽️ Cuisines: {', '.join(cuisines)}")
                    if skill_levels:
                        print(f"   🎯 Skill Levels: {', '.join(skill_levels)}")
                    if heat_levels:
                        avg_heat = sum(heat_levels) / len(heat_levels)
                        print(f"   🌶️ Average Heat Level: {avg_heat:.1f}/10")
                    if meal_types:
                        print(f"   🍴 Meal Types: {', '.join(meal_types)}")
                        
                else:
                    print("⚠️ No recipes found for this query")
                    
            else:
                print(f"❌ Error {response.status_code}: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    print(f"\n🎉 Test completed at {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)

def test_analysis_stats():
    """Show overall analysis statistics"""
    import sqlite3
    
    print("📊 ANALYSIS STATISTICS")
    print("=" * 60)
    
    conn = sqlite3.connect('hungie.db')
    cursor = conn.cursor()
    
    # Basic stats
    cursor.execute('SELECT COUNT(*) FROM recipe_analysis')
    total_analyzed = cursor.fetchone()[0]
    print(f"📈 Total Analyzed Recipes: {total_analyzed}")
    
    # Cuisine distribution
    cursor.execute('SELECT cuisine_type, COUNT(*) FROM recipe_analysis GROUP BY cuisine_type ORDER BY COUNT(*) DESC LIMIT 10')
    cuisine_stats = cursor.fetchall()
    print(f"\n🍽️ Top Cuisines:")
    for cuisine, count in cuisine_stats:
        print(f"   {cuisine}: {count} recipes")
    
    # Skill level distribution
    cursor.execute('SELECT skill_level, COUNT(*) FROM recipe_analysis GROUP BY skill_level ORDER BY COUNT(*) DESC')
    skill_stats = cursor.fetchall()
    print(f"\n🎯 Skill Level Distribution:")
    for skill, count in skill_stats:
        print(f"   {skill}: {count} recipes")
    
    # Heat level distribution
    cursor.execute('SELECT heat_level, COUNT(*) FROM recipe_analysis GROUP BY heat_level ORDER BY heat_level')
    heat_stats = cursor.fetchall()
    print(f"\n🌶️ Heat Level Distribution:")
    for heat, count in heat_stats:
        print(f"   Level {heat}: {count} recipes")
    
    # Meal type distribution
    cursor.execute('SELECT meal_type, COUNT(*) FROM recipe_analysis GROUP BY meal_type ORDER BY COUNT(*) DESC')
    meal_stats = cursor.fetchall()
    print(f"\n🍴 Meal Type Distribution:")
    for meal, count in meal_stats:
        print(f"   {meal}: {count} recipes")
    
    conn.close()

if __name__ == "__main__":
    test_analysis_stats()
    test_enhanced_search_comprehensive()
