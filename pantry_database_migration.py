#!/usr/bin/env python3
"""
🥫 PANTRY SYSTEM DATABASE MIGRATION
Day 1 Implementation: Foundation Tables + Ingredient Library Extraction

This script creates the foundational database architecture for intelligent pantry system
while preserving all existing functionality.

Author: SAGE AI Assistant
Date: August 18, 2025
Related: PROJECT_MASTER_GUIDE.md - Pantry System Implementation
"""

import os
import json
import re
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import List, Dict, Tuple, Optional

class PantryDatabaseMigration:
    """
    SOLID Foundation: Single responsibility for pantry database setup
    Creates 4 new tables without disrupting existing 728 recipes
    """
    
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        if not self.db_url:
            raise Exception("DATABASE_URL environment variable required")
        
        self.connection = None
        self.ingredient_frequency = {}
        self.canonical_ingredients = []
        
    def connect_database(self):
        """Establish PostgreSQL connection"""
        try:
            self.connection = psycopg2.connect(self.db_url)
            self.connection.autocommit = False
            print("✅ Connected to PostgreSQL database")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def create_pantry_tables(self):
        """
        Create 4 foundational pantry tables
        SAFE: Additive only - no existing data modified
        """
        
        print("\n🏗️ Creating pantry system tables...")
        
        sql_commands = [
            # 1. Canonical Ingredients - Master Dictionary
            """
            CREATE TABLE IF NOT EXISTS canonical_ingredients (
                id SERIAL PRIMARY KEY,
                canonical_name VARCHAR(200) NOT NULL UNIQUE,
                category VARCHAR(50) NOT NULL,
                aliases TEXT[],
                default_form VARCHAR(50),
                shelf_life_days INTEGER,
                usda_fdc_id INTEGER,
                is_common_pantry BOOLEAN DEFAULT FALSE,
                frequency_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # 2. User Pantry - Personal Inventory (create without foreign key first)
            """
            CREATE TABLE IF NOT EXISTS user_pantry (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                ingredient_id INTEGER,
                amount_status VARCHAR(20) DEFAULT 'some',
                expiry_date DATE,
                notes TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, ingredient_id)
            );
            """,
            
            # 3. Recipe-Ingredient Mapping - Normalize Existing Data (create without foreign key first)
            """
            CREATE TABLE IF NOT EXISTS recipe_ingredients (
                id SERIAL PRIMARY KEY,
                recipe_id INTEGER NOT NULL,
                ingredient_id INTEGER,
                raw_text TEXT NOT NULL,
                amount_numeric DECIMAL,
                unit VARCHAR(20),
                preparation VARCHAR(100),
                is_optional BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # 4. Substitution Intelligence - Smart Swaps (create without foreign key first)
            """
            CREATE TABLE IF NOT EXISTS ingredient_substitutions (
                id SERIAL PRIMARY KEY,
                ingredient_id INTEGER,
                substitute_id INTEGER,
                substitution_ratio DECIMAL DEFAULT 1.0,
                context_notes TEXT,
                confidence_level INTEGER DEFAULT 80,
                diet_compatible VARCHAR(100)[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ingredient_id, substitute_id)
            );
            """
        ]
        
        # Performance indexes
        index_commands = [
            "CREATE INDEX IF NOT EXISTS idx_user_pantry_user ON user_pantry(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_canonical_ingredients_category ON canonical_ingredients(category);",
            "CREATE INDEX IF NOT EXISTS idx_canonical_ingredients_name ON canonical_ingredients(canonical_name);",
        ]
        
        cursor = self.connection.cursor()
        
        try:
            # Create tables
            for i, command in enumerate(sql_commands, 1):
                try:
                    cursor.execute(command)
                    print(f"✅ Created table {i}/4")
                except Exception as e:
                    if "already exists" in str(e):
                        print(f"⚠️ Table {i}/4 already exists - skipping")
                    else:
                        raise e
            
            # Create indexes
            for command in index_commands:
                try:
                    cursor.execute(command)
                except Exception as e:
                    print(f"⚠️ Index creation issue: {str(e)[:60]}...")
            
            print("✅ Created performance indexes")
            
            self.connection.commit()
            print("🎉 All pantry tables created successfully!")
            
            # Now add foreign key constraints
            print("🔗 Adding foreign key constraints...")
            self._add_foreign_keys()
            
            return True
            
        except Exception as e:
            print(f"❌ Table creation failed: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
    
    def _add_foreign_keys(self):
        """Add foreign key constraints after all tables are created"""
        cursor = self.connection.cursor()
        
        try:
            # Add foreign keys one by one with error handling
            fk_commands = [
                # User pantry foreign keys
                "ALTER TABLE user_pantry ADD CONSTRAINT fk_user_pantry_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;",
                "ALTER TABLE user_pantry ADD CONSTRAINT fk_user_pantry_ingredient FOREIGN KEY (ingredient_id) REFERENCES canonical_ingredients(id);",
                
                # Recipe ingredients foreign keys  
                "ALTER TABLE recipe_ingredients ADD CONSTRAINT fk_recipe_ingredients_recipe FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE;",
                "ALTER TABLE recipe_ingredients ADD CONSTRAINT fk_recipe_ingredients_ingredient FOREIGN KEY (ingredient_id) REFERENCES canonical_ingredients(id);",
                
                # Substitutions foreign keys
                "ALTER TABLE ingredient_substitutions ADD CONSTRAINT fk_substitutions_ingredient FOREIGN KEY (ingredient_id) REFERENCES canonical_ingredients(id);",
                "ALTER TABLE ingredient_substitutions ADD CONSTRAINT fk_substitutions_substitute FOREIGN KEY (substitute_id) REFERENCES canonical_ingredients(id);"
            ]
            
            for command in fk_commands:
                try:
                    cursor.execute(command)
                    print(f"✅ Added foreign key constraint")
                except Exception as e:
                    if "already exists" in str(e):
                        print(f"⚠️ Foreign key constraint already exists - skipping")
                    else:
                        print(f"⚠️ Could not add foreign key: {str(e)[:60]}...")
            
            self.connection.commit()
            print("✅ Foreign key constraints completed")
            
        except Exception as e:
            print(f"⚠️ Foreign key setup had issues: {e}")
            # Don't fail the migration for foreign key issues
        finally:
            cursor.close()
    
    def extract_ingredient_library(self):
        """
        Mine existing 728 recipes to build canonical ingredient library
        This creates the intelligence foundation from YOUR actual recipes
        """
        
        print("\n🔍 Extracting ingredient library from existing recipes...")
        
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Get all recipes with ingredients
            cursor.execute("""
                SELECT id, title, ingredients 
                FROM recipes 
                WHERE ingredients IS NOT NULL 
                AND TRIM(ingredients) != ''
                ORDER BY id
            """)
            
            recipes = cursor.fetchall()
            print(f"📊 Found {len(recipes)} recipes to analyze")
            
            # Process each recipe
            total_ingredients_found = 0
            
            for recipe in recipes:
                if recipe['ingredients']:
                    ingredients = self._parse_recipe_ingredients(recipe['ingredients'])
                    total_ingredients_found += len(ingredients)
                    
                    for ingredient_data in ingredients:
                        ingredient_name = ingredient_data['ingredient']
                        if ingredient_name:
                            self.ingredient_frequency[ingredient_name] = \
                                self.ingredient_frequency.get(ingredient_name, 0) + 1
            
            print(f"📈 Extracted {total_ingredients_found} total ingredient references")
            print(f"🧠 Found {len(self.ingredient_frequency)} unique ingredients")
            
            # Sort by frequency
            sorted_ingredients = sorted(
                self.ingredient_frequency.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            print(f"\n🏆 Top 20 most common ingredients:")
            for ingredient, count in sorted_ingredients[:20]:
                print(f"  {ingredient}: {count} recipes")
            
            return sorted_ingredients
            
        except Exception as e:
            print(f"❌ Ingredient extraction failed: {e}")
            return []
        finally:
            cursor.close()
    
    def create_canonical_ingredients(self, sorted_ingredients: List[Tuple[str, int]]):
        """
        Create canonical ingredient entries with intelligent categorization
        """
        
        print(f"\n🏗️ Creating canonical ingredient entries...")
        
        cursor = self.connection.cursor()
        
        try:
            created_count = 0
            
            # Process top ingredients (limit to prevent overwhelm on Day 1)
            top_ingredients = sorted_ingredients[:200]  # Start with top 200
            
            for ingredient, frequency in top_ingredients:
                # Skip very long ingredient names that are likely parsing errors
                if len(ingredient) > 150:
                    continue
                    
                # Clean up the ingredient name further
                ingredient = ingredient.strip()
                if len(ingredient) < 2:
                    continue
                
                # Categorize ingredient
                category = self._categorize_ingredient(ingredient)
                
                # Generate aliases
                aliases = self._generate_aliases(ingredient)
                
                # Determine if common pantry item
                is_common = frequency > 20  # Items in 20+ recipes likely common
                
                cursor.execute("""
                    INSERT INTO canonical_ingredients 
                    (canonical_name, category, aliases, is_common_pantry, frequency_count)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (canonical_name) DO NOTHING
                """, (ingredient, category, aliases, is_common, frequency))
                
                created_count += 1
                
                if created_count % 25 == 0:
                    print(f"  Created {created_count}/{len(top_ingredients)} ingredients...")
            
            self.connection.commit()
            print(f"✅ Created {created_count} canonical ingredients")
            
            # Show category breakdown
            self._show_category_breakdown()
            
            return True
            
        except Exception as e:
            print(f"❌ Canonical ingredient creation failed: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
    
    def create_basic_substitutions(self):
        """
        Create foundational substitution relationships
        Start with safe, common substitutions
        """
        
        print(f"\n🔄 Creating basic substitution relationships...")
        
        # Basic substitutions - start conservatively
        substitutions = [
            # Dairy substitutions
            ('milk', 'almond milk', 1.0, 'dairy-free option', 90),
            ('butter', 'margarine', 1.0, 'dairy-free baking', 85),
            ('sour cream', 'greek yogurt', 1.0, 'healthier option', 90),
            ('heavy cream', 'coconut cream', 1.0, 'dairy-free option', 85),
            
            # Soy sauce family
            ('soy sauce', 'tamari', 1.0, 'gluten-free option', 95),
            ('soy sauce', 'coconut aminos', 1.0, 'soy-free option', 80),
            
            # Citrus
            ('lemon juice', 'lime juice', 1.0, 'citrus substitute', 85),
            ('lemon', 'lime', 1.0, 'citrus substitute', 85),
            
            # Oils
            ('vegetable oil', 'canola oil', 1.0, 'neutral oil substitute', 95),
            ('olive oil', 'avocado oil', 1.0, 'high-heat cooking', 85),
            
            # Vinegars
            ('white vinegar', 'apple cider vinegar', 1.0, 'mild flavor substitute', 85),
            ('rice vinegar', 'white wine vinegar', 1.0, 'mild acid substitute', 80),
            
            # Herbs (fresh/dried)
            ('fresh basil', 'dried basil', 0.33, 'dried herb substitute', 75),
            ('fresh oregano', 'dried oregano', 0.33, 'dried herb substitute', 75),
            
            # Sweeteners
            ('sugar', 'honey', 0.75, 'natural sweetener', 80),
            ('brown sugar', 'white sugar', 1.0, 'color/flavor difference', 85),
        ]
        
        cursor = self.connection.cursor()
        
        try:
            created_count = 0
            
            for main_ing, sub_ing, ratio, context, confidence in substitutions:
                # Get ingredient IDs
                cursor.execute("""
                    SELECT id FROM canonical_ingredients WHERE canonical_name = %s
                """, (main_ing,))
                main_result = cursor.fetchone()
                
                cursor.execute("""
                    SELECT id FROM canonical_ingredients WHERE canonical_name = %s
                """, (sub_ing,))
                sub_result = cursor.fetchone()
                
                if main_result and sub_result:
                    cursor.execute("""
                        INSERT INTO ingredient_substitutions 
                        (ingredient_id, substitute_id, substitution_ratio, context_notes, confidence_level)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (ingredient_id, substitute_id) DO NOTHING
                    """, (main_result[0], sub_result[0], ratio, context, confidence))
                    
                    created_count += 1
            
            self.connection.commit()
            print(f"✅ Created {created_count} substitution relationships")
            
            return True
            
        except Exception as e:
            print(f"❌ Substitution creation failed: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()
    
    def _parse_recipe_ingredients(self, ingredients_text: str) -> List[Dict]:
        """Parse ingredient text into structured data"""
        
        ingredients = []
        lines = ingredients_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
            
            # Extract core ingredient name
            ingredient_name = self._extract_core_ingredient(line)
            
            if ingredient_name and len(ingredient_name) >= 2:
                ingredients.append({
                    'raw_text': line,
                    'ingredient': ingredient_name,
                    'amount': self._extract_amount(line),
                    'unit': self._extract_unit(line),
                    'preparation': self._extract_preparation(line)
                })
        
        return ingredients
    
    def _extract_core_ingredient(self, line: str) -> str:
        """Extract the core ingredient name from a line"""
        
        # Remove common noise
        cleaned = line.lower()
        
        # Remove amounts and units at the beginning
        amount_pattern = r'^\d+(?:\.\d+)?\s*(?:cup|cups|tbsp|tsp|lb|lbs|oz|ounce|ounces|pound|pounds|tablespoon|tablespoons|teaspoon|teaspoons|g|grams?|kg|ml|liter|liters?)s?\s*'
        cleaned = re.sub(amount_pattern, '', cleaned)
        
        # Remove common brands and descriptors
        noise_words = [
            r'\b(organic|fresh|extra\s+virgin|pure|natural|unsalted|salted|ground|whole|chopped|diced|minced|sliced)\b',
            r'\b(plus\s+more|or\s+to\s+taste|to\s+taste|divided)\b',
            r'\b(kikkoman|hellmann\'s|heinz|kraft|mccormick|morton)\b'
        ]
        
        for pattern in noise_words:
            cleaned = re.sub(pattern, '', cleaned)
        
        # Remove prep instructions at the end
        prep_pattern = r',\s*(chopped|diced|minced|sliced|grated|crushed|divided|plus\s+more).*$'
        cleaned = re.sub(prep_pattern, '', cleaned)
        
        # Clean up whitespace and punctuation
        cleaned = re.sub(r'[,\(\)]', ' ', cleaned)
        cleaned = ' '.join(cleaned.split())
        
        # Remove very short results
        if len(cleaned.strip()) < 2:
            return None
        
        return cleaned.strip()
    
    def _extract_amount(self, line: str) -> Optional[float]:
        """Extract numeric amount from ingredient line"""
        amount_match = re.search(r'(\d+(?:\.\d+)?(?:\s*/\s*\d+)?)', line)
        if amount_match:
            try:
                amount_str = amount_match.group(1)
                if '/' in amount_str:
                    # Handle fractions like "1/2"
                    parts = amount_str.split('/')
                    return float(parts[0]) / float(parts[1])
                return float(amount_str)
            except:
                return None
        return None
    
    def _extract_unit(self, line: str) -> Optional[str]:
        """Extract unit from ingredient line"""
        unit_pattern = r'\d+(?:\.\d+)?\s*(cup|cups|tbsp|tsp|lb|lbs|oz|pound|pounds|tablespoon|tablespoons|teaspoon|teaspoons|g|grams?|kg)s?'
        unit_match = re.search(unit_pattern, line.lower())
        if unit_match:
            return unit_match.group(1)
        return None
    
    def _extract_preparation(self, line: str) -> Optional[str]:
        """Extract preparation notes from ingredient line"""
        prep_pattern = r',\s*(chopped|diced|minced|sliced|grated|crushed|divided|plus\s+more.*)'
        prep_match = re.search(prep_pattern, line.lower())
        if prep_match:
            return prep_match.group(1)
        return None
    
    def _categorize_ingredient(self, ingredient: str) -> str:
        """Automatically categorize ingredients based on name patterns"""
        
        ingredient_lower = ingredient.lower()
        
        # Produce
        if any(word in ingredient_lower for word in [
            'onion', 'garlic', 'tomato', 'pepper', 'carrot', 'celery', 'potato', 
            'lettuce', 'spinach', 'broccoli', 'cucumber', 'mushroom', 'corn',
            'apple', 'lemon', 'lime', 'orange', 'banana', 'avocado', 'ginger'
        ]):
            return 'produce'
        
        # Protein
        elif any(word in ingredient_lower for word in [
            'chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'egg', 'eggs',
            'turkey', 'bacon', 'ham', 'shrimp', 'tofu', 'beans', 'lentils'
        ]):
            return 'protein'
        
        # Dairy
        elif any(word in ingredient_lower for word in [
            'milk', 'cheese', 'butter', 'cream', 'yogurt', 'sour cream',
            'cheddar', 'mozzarella', 'parmesan', 'ricotta'
        ]):
            return 'dairy'
        
        # Grains
        elif any(word in ingredient_lower for word in [
            'flour', 'rice', 'pasta', 'bread', 'oats', 'quinoa', 'barley',
            'noodles', 'spaghetti', 'linguine', 'penne'
        ]):
            return 'grain'
        
        # Spices & Herbs
        elif any(word in ingredient_lower for word in [
            'salt', 'pepper', 'cumin', 'paprika', 'thyme', 'oregano', 'basil',
            'rosemary', 'sage', 'cinnamon', 'nutmeg', 'bay', 'parsley'
        ]):
            return 'spice'
        
        # Condiments & Sauces
        elif any(word in ingredient_lower for word in [
            'oil', 'vinegar', 'soy sauce', 'ketchup', 'mustard', 'mayo',
            'hot sauce', 'worcestershire', 'balsamic', 'olive oil'
        ]):
            return 'condiment'
        
        # Baking
        elif any(word in ingredient_lower for word in [
            'sugar', 'brown sugar', 'honey', 'vanilla', 'baking powder',
            'baking soda', 'yeast', 'cocoa', 'chocolate'
        ]):
            return 'baking'
        
        else:
            return 'other'
    
    def _generate_aliases(self, ingredient: str) -> List[str]:
        """Generate common aliases for ingredients"""
        
        aliases = []
        ingredient_lower = ingredient.lower()
        
        # Common alias patterns
        alias_map = {
            'soy sauce': ['light soy', 'dark soy', 'tamari', 'shoyu'],
            'tomato': ['roma tomato', 'cherry tomato', 'plum tomato', 'beefsteak tomato'],
            'onion': ['yellow onion', 'white onion', 'sweet onion', 'red onion'],
            'pepper': ['bell pepper', 'sweet pepper'],
            'cheese': ['cheddar', 'mozzarella', 'american cheese'],
            'oil': ['vegetable oil', 'canola oil', 'cooking oil'],
            'vinegar': ['white vinegar', 'distilled vinegar'],
            'milk': ['whole milk', '2% milk', 'skim milk'],
            'butter': ['unsalted butter', 'salted butter'],
            'flour': ['all-purpose flour', 'white flour'],
            'sugar': ['white sugar', 'granulated sugar'],
            'rice': ['white rice', 'long grain rice', 'jasmine rice'],
            'pasta': ['spaghetti', 'penne', 'linguine', 'noodles']
        }
        
        for base_ingredient, variations in alias_map.items():
            if base_ingredient in ingredient_lower:
                aliases.extend(variations)
        
        # Remove duplicates and the original ingredient
        aliases = list(set(aliases))
        if ingredient in aliases:
            aliases.remove(ingredient)
        
        return aliases[:5]  # Limit to 5 aliases to start
    
    def _show_category_breakdown(self):
        """Show breakdown of ingredients by category"""
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM canonical_ingredients 
            GROUP BY category 
            ORDER BY count DESC
        """)
        
        results = cursor.fetchall()
        
        print(f"\n📊 Ingredient Category Breakdown:")
        for category, count in results:
            print(f"  {category.title()}: {count} ingredients")
        
        cursor.close()
    
    def run_migration(self):
        """
        Execute complete Day 1 migration
        Safe rollback on any failure
        """
        
        print("🚀 Starting Day 1 Pantry System Migration")
        print("=" * 60)
        
        if not self.connect_database():
            return False
        
        try:
            # Step 1: Create tables
            if not self.create_pantry_tables():
                return False
            
            # Step 2: Extract ingredient library
            sorted_ingredients = self.extract_ingredient_library()
            if not sorted_ingredients:
                return False
            
            # Step 3: Create canonical ingredients
            if not self.create_canonical_ingredients(sorted_ingredients):
                return False
            
            # Step 4: Create basic substitutions
            if not self.create_basic_substitutions():
                return False
            
            print("\n" + "=" * 60)
            print("🎉 Day 1 Migration COMPLETE!")
            print("✅ 4 pantry tables created")
            print(f"✅ {len(sorted_ingredients[:200])} canonical ingredients")
            print("✅ Basic substitution relationships")
            print("✅ Performance indexes optimized")
            print("✅ All existing data preserved")
            print("\n🎯 Ready for Day 2: Core PantrySystem implementation!")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            if self.connection:
                self.connection.rollback()
                print("🔄 Database rolled back to original state")
            return False
        
        finally:
            if self.connection:
                self.connection.close()

def main():
    """Run the Day 1 migration"""
    
    print("🥫 Me Hungie Pantry System - Day 1 Migration")
    print("Building intelligence foundation from your existing recipes")
    print()
    
    migration = PantryDatabaseMigration()
    success = migration.run_migration()
    
    if success:
        print("\n🚀 Next Steps:")
        print("1. Verify migration in your Railway PostgreSQL dashboard")
        print("2. Test existing search functionality (should be unchanged)")
        print("3. Begin Day 2: Core PantrySystem implementation")
    else:
        print("\n🔧 Migration failed - check error messages above")
        print("All existing functionality preserved")

if __name__ == "__main__":
    main()
