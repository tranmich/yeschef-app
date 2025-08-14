"""
New Recipe Session Integration
Import and enhance new recipe session data with FlavorProfile analysis
"""
import json
import sqlite3
import os
from datetime import datetime
from recipe_database_enhancer import RecipeDatabaseEnhancer
from production_flavor_system import FlavorProfileSystem
import uuid

class SessionRecipeImporter:
    """Import and enhance recipes from session JSON files"""
    
    def __init__(self, db_path: str = 'hungie.db'):
        self.db_path = db_path
        self.enhancer = RecipeDatabaseEnhancer(db_path)
        
    def import_session_file(self, session_file_path: str):
        """Import recipes from a session JSON file"""
        
        print(f"📥 Importing recipes from {session_file_path}...")
        
        try:
            with open(session_file_path, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            session_info = session_data.get('sessionInfo', {})
            recipes = session_data.get('recipes', [])
            
            print(f"📊 Session Info:")
            print(f"   📅 Collection Date: {session_info.get('collectionDate', 'Unknown')}")
            print(f"   🔢 Recipes Collected: {session_info.get('recipesCollected', len(recipes))}")
            print(f"   ⏱️ Runtime: {session_info.get('runtimeFormatted', 'Unknown')}")
            print(f"   🌐 Source: {session_info.get('source', 'Unknown')}")
            
            if not recipes:
                print("❌ No recipes found in session file")
                return
            
            # Import recipes
            imported_count = 0
            skipped_count = 0
            enhanced_count = 0
            
            for recipe in recipes:
                try:
                    if self._import_single_recipe(recipe, session_info):
                        imported_count += 1
                        
                        # Try to enhance with FlavorProfile if it has ingredients
                        if self._has_sufficient_ingredients(recipe):
                            if self._enhance_recipe_with_flavorprofile(recipe):
                                enhanced_count += 1
                    else:
                        skipped_count += 1
                        
                except Exception as e:
                    print(f"   ❌ Error importing recipe {recipe.get('name', 'Unknown')}: {e}")
                    skipped_count += 1
            
            print(f"\\n📊 Import Summary:")
            print(f"   ✅ Imported: {imported_count} recipes")
            print(f"   🔥 Enhanced: {enhanced_count} recipes")
            print(f"   ⚪ Skipped: {skipped_count} recipes")
            
        except Exception as e:
            print(f"❌ Error importing session file: {e}")
    
    def _import_single_recipe(self, recipe_data: dict, session_info: dict) -> bool:
        """Import a single recipe into the database"""
        
        try:
            # Generate recipe ID
            recipe_id = str(uuid.uuid4())
            
            # Extract recipe data
            name = recipe_data.get('name', '').strip()
            description = recipe_data.get('description', '').strip()
            url = recipe_data.get('url', '').strip()
            
            if not name:
                return False
            
            # Check if recipe already exists
            if self._recipe_exists(name, url):
                print(f"   ⚪ Skipping duplicate: {name[:50]}...")
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert recipe
            cursor.execute("""
                INSERT INTO recipes (
                    id, name, description, prep_time, cook_time, total_time,
                    servings, url, date_saved, category
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                recipe_id,
                name,
                description,
                recipe_data.get('prepTime', ''),
                recipe_data.get('cookTime', ''),
                recipe_data.get('totalTime', ''),
                recipe_data.get('servings'),
                url,
                session_info.get('collectionDate', datetime.now().isoformat()),
                'easy'  # Based on the session targeting
            ))
            
            # Insert ingredients
            ingredients = recipe_data.get('ingredients', [])
            for ingredient_text in ingredients:
                if ingredient_text and len(ingredient_text.strip()) > 1:
                    ingredient_id = str(uuid.uuid4())
                    
                    # Insert ingredient if not exists
                    cursor.execute("SELECT id FROM ingredients WHERE name = ?", (ingredient_text,))
                    existing = cursor.fetchone()
                    
                    if not existing:
                        cursor.execute("INSERT INTO ingredients (id, name) VALUES (?, ?)", 
                                     (ingredient_id, ingredient_text))
                    else:
                        ingredient_id = existing[0]
                    
                    # Link recipe to ingredient
                    cursor.execute("""
                        INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount, unit)
                        VALUES (?, ?, ?, ?)
                    """, (recipe_id, ingredient_id, '', ''))
            
            # Insert instructions
            instructions = recipe_data.get('instructions', [])
            for i, instruction in enumerate(instructions, 1):
                if instruction and instruction.strip():
                    cursor.execute("""
                        INSERT INTO instructions (recipe_id, step_number, instruction)
                        VALUES (?, ?, ?)
                    """, (recipe_id, i, instruction.strip()))
            
            # Add to easy category
            cursor.execute("SELECT id FROM categories WHERE name = 'easy'")
            category_result = cursor.fetchone()
            
            if category_result:
                category_id = category_result[0]
                cursor.execute("""
                    INSERT INTO recipe_categories (recipe_id, category_id)
                    VALUES (?, ?)
                """, (recipe_id, category_id))
            else:
                # Create easy category if it doesn't exist
                easy_category_id = str(uuid.uuid4())
                cursor.execute("INSERT INTO categories (id, name) VALUES (?, ?)", 
                             (easy_category_id, 'easy'))
                cursor.execute("""
                    INSERT INTO recipe_categories (recipe_id, category_id)
                    VALUES (?, ?)
                """, (recipe_id, easy_category_id))
            
            conn.commit()
            conn.close()
            
            print(f"   ✅ Imported: {name[:50]}...")
            return True
            
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
                conn.close()
            print(f"   ❌ Error importing {recipe_data.get('name', 'Unknown')}: {e}")
            return False
    
    def _recipe_exists(self, name: str, url: str) -> bool:
        """Check if recipe already exists in database"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check by name and URL
            cursor.execute("""
                SELECT id FROM recipes 
                WHERE LOWER(name) = LOWER(?) OR url = ?
            """, (name, url))
            
            result = cursor.fetchone()
            return result is not None
            
        except Exception:
            return False
        finally:
            conn.close()
    
    def _has_sufficient_ingredients(self, recipe_data: dict) -> bool:
        """Check if recipe has enough ingredients for FlavorProfile analysis"""
        
        ingredients = recipe_data.get('ingredients', [])
        valid_ingredients = [ing for ing in ingredients if ing and len(ing.strip()) > 2]
        return len(valid_ingredients) >= 2
    
    def _enhance_recipe_with_flavorprofile(self, recipe_data: dict) -> bool:
        """Enhance recipe with FlavorProfile analysis"""
        
        try:
            # Find the recipe in database
            name = recipe_data.get('name', '').strip()
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM recipes WHERE LOWER(name) = LOWER(?)", (name,))
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return False
            
            recipe_id = result[0]
            
            # Run FlavorProfile analysis
            analysis_result = self.enhancer.analyze_recipe_with_flavorprofile(recipe_id)
            
            if analysis_result:
                self.enhancer._save_flavor_analysis(analysis_result)
                return True
            
            return False
            
        except Exception as e:
            print(f"   ❌ FlavorProfile enhancement failed for {recipe_data.get('name', 'Unknown')}: {e}")
            return False
    
    def import_all_session_files(self):
        """Import all session JSON files in the directory"""
        
        print("🔍 Scanning for session files...")
        
        session_files = []
        for file in os.listdir('.'):
            if file.startswith('session_') and file.endswith('.json'):
                session_files.append(file)
        
        if not session_files:
            print("❌ No session files found")
            return
        
        print(f"📂 Found {len(session_files)} session files:")
        for file in session_files:
            print(f"   📄 {file}")
        
        total_imported = 0
        total_enhanced = 0
        
        for session_file in session_files:
            print(f"\\n" + "="*60)
            
            # Get stats before import
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM recipes")
            recipes_before = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM recipe_flavor_profiles")
            enhanced_before = cursor.fetchone()[0]
            conn.close()
            
            # Import session
            self.import_session_file(session_file)
            
            # Get stats after import
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM recipes")
            recipes_after = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM recipe_flavor_profiles")
            enhanced_after = cursor.fetchone()[0]
            conn.close()
            
            session_imported = recipes_after - recipes_before
            session_enhanced = enhanced_after - enhanced_before
            
            total_imported += session_imported
            total_enhanced += session_enhanced
            
            print(f"📊 Session imported: +{session_imported} recipes, +{session_enhanced} enhanced")
        
        print(f"\\n" + "="*60)
        print(f"🎉 TOTAL IMPORT COMPLETE!")
        print(f"   📈 Total New Recipes: {total_imported}")
        print(f"   🔥 Total Enhanced: {total_enhanced}")
        
        # Final database stats
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM recipes")
        total_recipes = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM recipe_flavor_profiles")
        total_enhanced_db = cursor.fetchone()[0]
        conn.close()
        
        print(f"   🏆 Database Total: {total_recipes} recipes ({total_enhanced_db} enhanced)")

def main():
    """Main import process"""
    print("🍳 New Recipe Session Import & Enhancement")
    print("=" * 50)
    
    importer = SessionRecipeImporter()
    
    # Import all session files
    importer.import_all_session_files()
    
    print("\\n✅ Import process completed!")
    print("\\n🎯 Next steps:")
    print("   1. Test enhanced search with new recipes")
    print("   2. Verify FlavorProfile analysis quality")
    print("   3. Update frontend to showcase new content")

if __name__ == "__main__":
    main()
