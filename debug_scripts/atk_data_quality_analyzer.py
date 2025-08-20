#!/usr/bin/env python3
"""
ATK Teens Data Quality Analyzer
Analyzes the quality of extracted ATK Teens recipes in the database
"""

import sys
import os
import logging
from typing import Dict, List
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core_systems.database_manager import DatabaseManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ATKDataQualityAnalyzer:
    """Analyze quality of ATK Teens recipes in database"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.atk_recipes = []
    
    def fetch_atk_recipes(self):
        """Fetch all ATK Teens recipes from database"""
        logger.info("🔍 Fetching ATK Teens recipes from database...")
        
        query = """
        SELECT 
            title, category, ingredients, instructions, servings, 
            total_time, description, page_number, created_at
        FROM recipes 
        WHERE source = 'The Complete Cookbook for Teen - America''s Test Kitchen Kids'
        ORDER BY page_number
        """
        
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                self.atk_recipes = cursor.fetchall()
            
            logger.info(f"✅ Found {len(self.atk_recipes)} ATK Teens recipes")
            return len(self.atk_recipes)
        except Exception as e:
            logger.error(f"❌ Error fetching recipes: {e}")
            return 0
    
    def analyze_data_quality(self):
        """Analyze quality of each recipe using our validation criteria"""
        if not self.atk_recipes:
            logger.error("❌ No recipes to analyze")
            return
        
        logger.info("\n📊 ANALYZING DATA QUALITY")
        logger.info("=" * 60)
        
        quality_stats = {
            'total_recipes': len(self.atk_recipes),
            'perfect_scores': 0,
            'good_scores': 0,
            'acceptable_scores': 0,
            'poor_scores': 0,
            'score_distribution': {},
            'field_analysis': {
                'title': {'present': 0, 'quality': []},
                'category': {'present': 0, 'quality': []},
                'ingredients': {'present': 0, 'quality': []},
                'instructions': {'present': 0, 'quality': []},
                'servings': {'present': 0, 'quality': []},
                'total_time': {'present': 0, 'quality': []},
                'description': {'present': 0, 'quality': []}
            },
            'sample_recipes': {
                'high_quality': [],
                'medium_quality': [],
                'low_quality': []
            }
        }
        
        for i, recipe in enumerate(self.atk_recipes):
            score = self._calculate_quality_score(recipe)
            quality_stats['score_distribution'][score] = quality_stats['score_distribution'].get(score, 0) + 1
            
            # Categorize by score
            if score >= 8:  # Perfect or near-perfect
                quality_stats['perfect_scores'] += 1
                if len(quality_stats['sample_recipes']['high_quality']) < 3:
                    quality_stats['sample_recipes']['high_quality'].append({
                        'title': recipe['title'],
                        'page': recipe['page_number'],
                        'score': score
                    })
            elif score >= 7:  # Good
                quality_stats['good_scores'] += 1
                if len(quality_stats['sample_recipes']['medium_quality']) < 3:
                    quality_stats['sample_recipes']['medium_quality'].append({
                        'title': recipe['title'],
                        'page': recipe['page_number'],
                        'score': score
                    })
            elif score >= 6:  # Acceptable (meets core requirements)
                quality_stats['acceptable_scores'] += 1
                if len(quality_stats['sample_recipes']['medium_quality']) < 3:
                    quality_stats['sample_recipes']['medium_quality'].append({
                        'title': recipe['title'],
                        'page': recipe['page_number'],
                        'score': score
                    })
            else:  # Poor
                quality_stats['poor_scores'] += 1
                if len(quality_stats['sample_recipes']['low_quality']) < 3:
                    quality_stats['sample_recipes']['low_quality'].append({
                        'title': recipe['title'],
                        'page': recipe['page_number'],
                        'score': score
                    })
            
            # Analyze individual fields
            self._analyze_field_quality(recipe, quality_stats['field_analysis'])
        
        self._print_quality_report(quality_stats)
        return quality_stats
    
    def _calculate_quality_score(self, recipe):
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
    
    def _analyze_field_quality(self, recipe, field_analysis):
        """Analyze quality of individual fields"""
        fields = ['title', 'category', 'ingredients', 'instructions', 'servings', 'total_time', 'description']
        
        for field in fields:
            value = recipe.get(field, '') or ''
            if value.strip():
                field_analysis[field]['present'] += 1
                field_analysis[field]['quality'].append(len(value.strip()))
    
    def _print_quality_report(self, stats):
        """Print comprehensive quality report"""
        total = stats['total_recipes']
        
        logger.info(f"\n🎯 OVERALL QUALITY SUMMARY:")
        logger.info(f"  Total recipes analyzed: {total}")
        logger.info(f"  Perfect scores (8/8): {stats['perfect_scores']} ({stats['perfect_scores']/total*100:.1f}%)")
        logger.info(f"  Good scores (7/8): {stats['good_scores']} ({stats['good_scores']/total*100:.1f}%)")
        logger.info(f"  Acceptable scores (6/8): {stats['acceptable_scores']} ({stats['acceptable_scores']/total*100:.1f}%)")
        logger.info(f"  Poor scores (<6/8): {stats['poor_scores']} ({stats['poor_scores']/total*100:.1f}%)")
        
        success_rate = (stats['perfect_scores'] + stats['good_scores'] + stats['acceptable_scores']) / total * 100
        logger.info(f"  ✅ Overall success rate: {success_rate:.1f}%")
        
        logger.info(f"\n📈 SCORE DISTRIBUTION:")
        for score in sorted(stats['score_distribution'].keys(), reverse=True):
            count = stats['score_distribution'][score]
            percentage = count / total * 100
            logger.info(f"  Score {score}/8: {count} recipes ({percentage:.1f}%)")
        
        logger.info(f"\n📋 FIELD PRESENCE ANALYSIS:")
        for field, data in stats['field_analysis'].items():
            present = data['present']
            presence_rate = present / total * 100
            avg_length = sum(data['quality']) / len(data['quality']) if data['quality'] else 0
            logger.info(f"  {field.title()}: {present}/{total} ({presence_rate:.1f}%) | Avg length: {avg_length:.0f} chars")
        
        logger.info(f"\n🌟 SAMPLE HIGH-QUALITY RECIPES:")
        for sample in stats['sample_recipes']['high_quality']:
            logger.info(f"  • '{sample['title']}' (Page {sample['page']}) - Score: {sample['score']}/8")
        
        logger.info(f"\n⚡ SAMPLE MEDIUM-QUALITY RECIPES:")
        for sample in stats['sample_recipes']['medium_quality']:
            logger.info(f"  • '{sample['title']}' (Page {sample['page']}) - Score: {sample['score']}/8")
        
        if stats['sample_recipes']['low_quality']:
            logger.info(f"\n⚠️ SAMPLE LOW-QUALITY RECIPES:")
            for sample in stats['sample_recipes']['low_quality']:
                logger.info(f"  • '{sample['title']}' (Page {sample['page']}) - Score: {sample['score']}/8")
    
    def show_sample_recipes(self, count=3):
        """Show detailed examples of extracted recipes"""
        if not self.atk_recipes:
            logger.error("❌ No recipes to show")
            return
        
        logger.info(f"\n📖 DETAILED RECIPE SAMPLES:")
        logger.info("=" * 60)
        
        # Show a few representative recipes
        sample_indices = [0, len(self.atk_recipes)//2, len(self.atk_recipes)-1]
        
        for i, idx in enumerate(sample_indices[:count]):
            if idx < len(self.atk_recipes):
                recipe = self.atk_recipes[idx]
                score = self._calculate_quality_score(recipe)
                
                logger.info(f"\n📄 SAMPLE {i+1}: '{recipe['title']}' (Page {recipe['page_number']})")
                logger.info(f"   Quality Score: {score}/8")
                logger.info(f"   Category: {recipe.get('category', 'N/A')}")
                logger.info(f"   Servings: {recipe.get('servings', 'N/A')}")
                logger.info(f"   Time: {recipe.get('total_time', 'N/A')}")
                
                # Show ingredients (truncated)
                ingredients = recipe.get('ingredients', '') or ''
                if ingredients:
                    ingredients_preview = ingredients[:200] + "..." if len(ingredients) > 200 else ingredients
                    logger.info(f"   Ingredients ({len(ingredients)} chars):")
                    for line in ingredients_preview.split('\n')[:3]:
                        if line.strip():
                            logger.info(f"     {line.strip()}")
                
                # Show instructions (truncated)
                instructions = recipe.get('instructions', '') or ''
                if instructions:
                    instructions_preview = instructions[:200] + "..." if len(instructions) > 200 else instructions
                    logger.info(f"   Instructions ({len(instructions)} chars):")
                    for line in instructions_preview.split('\n')[:2]:
                        if line.strip():
                            logger.info(f"     {line.strip()}")
                
                # Show description if available
                description = recipe.get('description', '') or ''
                if description:
                    desc_preview = description[:150] + "..." if len(description) > 150 else description
                    logger.info(f"   Description: {desc_preview}")
    
    def export_quality_report(self, filename=None):
        """Export quality analysis to JSON file"""
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"atk_quality_report_{timestamp}.json"
        
        # Get basic stats
        stats = self.analyze_data_quality()
        
        # Add sample data
        sample_data = []
        for recipe in self.atk_recipes[:10]:  # First 10 recipes
            sample_data.append({
                'title': recipe['title'],
                'page_number': recipe['page_number'],
                'quality_score': self._calculate_quality_score(recipe),
                'has_ingredients': bool(recipe.get('ingredients', '').strip()),
                'has_instructions': bool(recipe.get('instructions', '').strip()),
                'ingredients_length': len(recipe.get('ingredients', '') or ''),
                'instructions_length': len(recipe.get('instructions', '') or ''),
                'created_at': str(recipe.get('created_at', ''))
            })
        
        from datetime import datetime
        report = {
            'analysis_timestamp': datetime.now().isoformat(),
            'total_recipes': len(self.atk_recipes),
            'quality_stats': stats,
            'sample_recipes': sample_data
        }
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📁 Quality report exported to: {filepath}")
        return filepath


def main():
    """Main execution"""
    logger.info("🔍 STARTING ATK TEENS DATA QUALITY ANALYSIS")
    logger.info("=" * 60)
    
    analyzer = ATKDataQualityAnalyzer()
    
    # Fetch recipes
    recipe_count = analyzer.fetch_atk_recipes()
    if recipe_count == 0:
        logger.error("❌ No ATK recipes found in database")
        return
    
    # Analyze quality
    analyzer.analyze_data_quality()
    
    # Show sample recipes
    analyzer.show_sample_recipes(count=5)
    
    # Export report
    analyzer.export_quality_report()
    
    logger.info(f"\n✅ ANALYSIS COMPLETE!")


if __name__ == "__main__":
    main()
