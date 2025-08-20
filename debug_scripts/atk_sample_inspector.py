#!/usr/bin/env python3
"""
ATK Recipe Sample Inspector
Shows detailed examples of extracted recipes to verify quality
"""

import sys
import os
import logging
from typing import Dict, List

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_systems.database_manager import DatabaseManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def show_recipe_details():
    """Show detailed examples of specific recipes"""
    db_manager = DatabaseManager()
    
    # Get a few specific high-quality recipes
    sample_queries = [
        ("High-Quality Recipe", "SELECT * FROM recipes WHERE source LIKE '%ATK%' AND title = 'Shakshuka' LIMIT 1"),
        ("Medium-Quality Recipe", "SELECT * FROM recipes WHERE source LIKE '%ATK%' AND title = 'Cheeseburger Sliders' LIMIT 1"),
        ("Simple Recipe", "SELECT * FROM recipes WHERE source LIKE '%ATK%' AND title = 'Acai Smoothie Bowls' LIMIT 1"),
        ("Complex Recipe", "SELECT * FROM recipes WHERE source LIKE '%ATK%' AND page_number = 286 LIMIT 1")
    ]
    
    logger.info("🔍 DETAILED RECIPE QUALITY INSPECTION")
    logger.info("=" * 70)
    
    for category, query in sample_queries:
        logger.info(f"\n📖 {category.upper()}")
        logger.info("-" * 50)
        
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                recipe = cursor.fetchone()
                
                if recipe:
                    print_recipe_details(recipe, category)
                else:
                    logger.info(f"❌ No recipe found for {category}")
                    
        except Exception as e:
            logger.error(f"❌ Error fetching {category}: {e}")


def print_recipe_details(recipe, category):
    """Print detailed recipe information"""
    print(f"\n🍽️ RECIPE: {recipe['title']}")
    print(f"   📄 Page: {recipe.get('page_number', 'N/A')}")
    print(f"   🏷️ Category: {recipe.get('category', 'N/A')}")
    print(f"   👥 Servings: {recipe.get('servings', 'N/A')}")
    print(f"   ⏰ Time: {recipe.get('total_time', 'N/A')}")
    print(f"   📅 Added: {recipe.get('created_at', 'N/A')}")
    
    # Quality score
    score = calculate_quality_score(recipe)
    print(f"   📊 Quality Score: {score}/8")
    
    print(f"\n📝 INGREDIENTS ({len(recipe.get('ingredients', '') or '')} characters):")
    ingredients = recipe.get('ingredients', '') or ''
    if ingredients:
        for line in ingredients.split('\n'):
            if line.strip():
                print(f"   {line.strip()}")
    else:
        print("   ❌ No ingredients found")
    
    print(f"\n👨‍🍳 INSTRUCTIONS ({len(recipe.get('instructions', '') or '')} characters):")
    instructions = recipe.get('instructions', '') or ''
    if instructions:
        for line in instructions.split('\n'):
            if line.strip():
                print(f"   {line.strip()}")
    else:
        print("   ❌ No instructions found")
    
    description = recipe.get('description', '') or ''
    if description:
        print(f"\n📖 DESCRIPTION ({len(description)} characters):")
        # Wrap description at 70 characters
        words = description.split()
        line = ""
        for word in words:
            if len(line + word) > 70:
                print(f"   {line.strip()}")
                line = word + " "
            else:
                line += word + " "
        if line.strip():
            print(f"   {line.strip()}")


def calculate_quality_score(recipe):
    """Calculate quality score using our validation criteria"""
    score = 0
    
    # Core Requirement 1: Title (1 point)
    title = recipe.get('title', '') or ''
    if title.strip() and len(title.strip()) > 2:
        score += 1
    
    # Core Requirement 2: Category (1 point)
    category = recipe.get('category', '') or ''
    if category.strip():
        score += 1
    
    # Core Requirement 3: Ingredients (2 points)
    ingredients = recipe.get('ingredients', '') or ''
    if ingredients.strip() and len(ingredients.strip()) > 10:
        if len(ingredients.strip()) > 50:
            score += 2  # Full points for substantial ingredients
        else:
            score += 1  # Partial points
    
    # Core Requirement 4: Instructions (2 points)
    instructions = recipe.get('instructions', '') or ''
    if instructions.strip() and len(instructions.strip()) > 10:
        if len(instructions.strip()) > 50:
            score += 2  # Full points for substantial instructions
        else:
            score += 1  # Partial points
    
    # Bonus fields (1 point each)
    if recipe.get('servings'):
        score += 1
    if recipe.get('total_time'):
        score += 1
    if recipe.get('description'):
        score += 1
    
    return score


def show_problematic_recipes():
    """Show recipes that had quality issues"""
    db_manager = DatabaseManager()
    
    logger.info("\n⚠️ PROBLEMATIC RECIPES ANALYSIS")
    logger.info("=" * 50)
    
    # Find recipes with title issues
    problematic_query = """
    SELECT title, page_number, category, 
           LENGTH(ingredients) as ingredients_len,
           LENGTH(instructions) as instructions_len
    FROM recipes 
    WHERE source LIKE '%ATK%' 
    AND (
        title LIKE 'Start Cooking!%' OR 
        title LIKE 'PREPARE INGREDIENTS%' OR
        title LIKE '%ajar%'
    )
    ORDER BY page_number
    """
    
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(problematic_query)
            problematic_recipes = cursor.fetchall()
            
            if problematic_recipes:
                logger.info(f"Found {len(problematic_recipes)} recipes with title issues:")
                for recipe in problematic_recipes:
                    print(f"   📄 Page {recipe['page_number']}: '{recipe['title']}'")
                    print(f"      Category: {recipe['category']}")
                    print(f"      Content: {recipe['ingredients_len']} chars ingredients, {recipe['instructions_len']} chars instructions")
                    print()
            else:
                logger.info("✅ No problematic recipes found!")
                
    except Exception as e:
        logger.error(f"❌ Error analyzing problematic recipes: {e}")


def main():
    """Main execution"""
    show_recipe_details()
    show_problematic_recipes()


if __name__ == "__main__":
    main()
