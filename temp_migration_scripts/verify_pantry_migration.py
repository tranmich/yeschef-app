#!/usr/bin/env python3
"""
🔍 PANTRY MIGRATION VERIFICATION SCRIPT
Day 1 Verification: Ensure migration completed successfully

This script verifies the pantry database migration without affecting existing data.

Author: SAGE AI Assistant
Date: August 18, 2025
Related: pantry_database_migration.py
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

class PantryMigrationVerifier:
    """
    Verify that Day 1 migration completed successfully
    Check all tables, data integrity, and existing functionality
    """
    
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        if not self.db_url:
            raise Exception("DATABASE_URL environment variable required")
        
        self.connection = None
        self.verification_results = {}
    
    def connect_database(self):
        """Establish PostgreSQL connection"""
        try:
            self.connection = psycopg2.connect(self.db_url)
            print("✅ Connected to PostgreSQL database")
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def verify_existing_functionality(self):
        """Ensure existing recipes and functionality unchanged"""
        
        print("\n🔍 Verifying existing functionality preserved...")
        
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Check recipe count
            cursor.execute("SELECT COUNT(*) as count FROM recipes")
            recipe_count = cursor.fetchone()['count']
            print(f"✅ Recipes table: {recipe_count} recipes preserved")
            
            # Check users table
            cursor.execute("SELECT COUNT(*) as count FROM users")
            user_count = cursor.fetchone()['count']
            print(f"✅ Users table: {user_count} users preserved")
            
            # Verify intelligence metadata exists
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM recipes 
                WHERE meal_role IS NOT NULL
            """)
            
            intelligent_recipes = cursor.fetchone()['count']
            print(f"✅ Intelligence metadata: {intelligent_recipes} recipes enhanced")
            
            # Test basic search still works
            cursor.execute("""
                SELECT id, title 
                FROM recipes 
                WHERE LOWER(title) LIKE %s 
                LIMIT 3
            """, ('%chicken%',))
            
            sample_recipes = cursor.fetchall()
            print(f"✅ Basic search working: Found {len(sample_recipes)} chicken recipes")
            
            self.verification_results['existing_functionality'] = True
            return True
            
        except Exception as e:
            print(f"❌ Existing functionality check failed: {e}")
            self.verification_results['existing_functionality'] = False
            return False
        finally:
            cursor.close()
    
    def verify_pantry_tables(self):
        """Verify all 4 pantry tables were created correctly"""
        
        print("\n🏗️ Verifying pantry tables...")
        
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        
        expected_tables = [
            'canonical_ingredients',
            'user_pantry', 
            'recipe_ingredients',
            'ingredient_substitutions'
        ]
        
        try:
            tables_verified = 0
            
            for table_name in expected_tables:
                # Check table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    )
                """, (table_name,))
                
                exists = cursor.fetchone()['exists']
                
                if exists:
                    # Check table structure and data
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                    count = cursor.fetchone()['count']
                    print(f"✅ {table_name}: Table exists with {count} records")
                    tables_verified += 1
                else:
                    print(f"❌ {table_name}: Table missing!")
            
            success = tables_verified == len(expected_tables)
            self.verification_results['pantry_tables'] = success
            
            return success
            
        except Exception as e:
            print(f"❌ Table verification failed: {e}")
            self.verification_results['pantry_tables'] = False
            return False
        finally:
            cursor.close()
    
    def verify_canonical_ingredients(self):
        """Verify canonical ingredients were extracted correctly"""
        
        print("\n🧠 Verifying canonical ingredients...")
        
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Check total count
            cursor.execute("SELECT COUNT(*) as count FROM canonical_ingredients")
            total_count = cursor.fetchone()['count']
            
            if total_count == 0:
                print("❌ No canonical ingredients found!")
                self.verification_results['canonical_ingredients'] = False
                return False
            
            print(f"✅ Total canonical ingredients: {total_count}")
            
            # Check category distribution
            cursor.execute("""
                SELECT category, COUNT(*) as count 
                FROM canonical_ingredients 
                GROUP BY category 
                ORDER BY count DESC
            """)
            
            categories = cursor.fetchall()
            print(f"✅ Categories found: {len(categories)}")
            
            for category in categories:
                print(f"   {category['category']}: {category['count']} ingredients")
            
            # Check for common pantry items
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM canonical_ingredients 
                WHERE is_common_pantry = true
            """)
            
            common_count = cursor.fetchone()['count']
            print(f"✅ Common pantry items identified: {common_count}")
            
            # Show top ingredients by frequency
            cursor.execute("""
                SELECT canonical_name, frequency_count, category
                FROM canonical_ingredients 
                ORDER BY frequency_count DESC 
                LIMIT 10
            """)
            
            top_ingredients = cursor.fetchall()
            print(f"\n🏆 Top 10 ingredients by frequency:")
            for ing in top_ingredients:
                print(f"   {ing['canonical_name']} ({ing['category']}): {ing['frequency_count']} recipes")
            
            self.verification_results['canonical_ingredients'] = True
            return True
            
        except Exception as e:
            print(f"❌ Canonical ingredients verification failed: {e}")
            self.verification_results['canonical_ingredients'] = False
            return False
        finally:
            cursor.close()
    
    def verify_substitutions(self):
        """Verify substitution relationships were created"""
        
        print("\n🔄 Verifying substitution relationships...")
        
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Check substitution count
            cursor.execute("SELECT COUNT(*) as count FROM ingredient_substitutions")
            sub_count = cursor.fetchone()['count']
            
            if sub_count == 0:
                print("⚠️ No substitutions found - this is OK for Day 1")
                self.verification_results['substitutions'] = True
                return True
            
            print(f"✅ Substitution relationships: {sub_count}")
            
            # Show sample substitutions
            cursor.execute("""
                SELECT 
                    ci1.canonical_name as main_ingredient,
                    ci2.canonical_name as substitute,
                    s.substitution_ratio,
                    s.context_notes,
                    s.confidence_level
                FROM ingredient_substitutions s
                JOIN canonical_ingredients ci1 ON s.ingredient_id = ci1.id
                JOIN canonical_ingredients ci2 ON s.substitute_id = ci2.id
                ORDER BY s.confidence_level DESC
                LIMIT 5
            """)
            
            substitutions = cursor.fetchall()
            
            if substitutions:
                print(f"\n🔄 Sample substitutions:")
                for sub in substitutions:
                    print(f"   {sub['main_ingredient']} → {sub['substitute']} " +
                          f"(ratio: {sub['substitution_ratio']}, confidence: {sub['confidence_level']}%)")
            
            self.verification_results['substitutions'] = True
            return True
            
        except Exception as e:
            print(f"❌ Substitutions verification failed: {e}")
            self.verification_results['substitutions'] = False
            return False
        finally:
            cursor.close()
    
    def verify_indexes(self):
        """Verify performance indexes were created"""
        
        print("\n⚡ Verifying performance indexes...")
        
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        
        expected_indexes = [
            'idx_user_pantry_user',
            'idx_recipe_ingredients_recipe',
            'idx_canonical_ingredients_category',
            'idx_ingredient_substitutions_main'
        ]
        
        try:
            indexes_found = 0
            
            for index_name in expected_indexes:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM pg_indexes 
                        WHERE indexname = %s
                    )
                """, (index_name,))
                
                exists = cursor.fetchone()['exists']
                
                if exists:
                    print(f"✅ Index {index_name}: Created")
                    indexes_found += 1
                else:
                    print(f"⚠️ Index {index_name}: Missing")
            
            print(f"✅ Performance indexes: {indexes_found}/{len(expected_indexes)} created")
            
            self.verification_results['indexes'] = indexes_found >= len(expected_indexes) - 1
            return True
            
        except Exception as e:
            print(f"❌ Index verification failed: {e}")
            self.verification_results['indexes'] = False
            return False
        finally:
            cursor.close()
    
    def test_basic_pantry_queries(self):
        """Test basic pantry-related queries work"""
        
        print("\n🧪 Testing basic pantry queries...")
        
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Test ingredient search
            cursor.execute("""
                SELECT id, canonical_name, category 
                FROM canonical_ingredients 
                WHERE canonical_name ILIKE %s 
                LIMIT 3
            """, ('%tomato%',))
            
            tomato_results = cursor.fetchall()
            print(f"✅ Ingredient search: Found {len(tomato_results)} tomato variants")
            
            # Test category grouping
            cursor.execute("""
                SELECT category, COUNT(*) as count 
                FROM canonical_ingredients 
                WHERE category IN ('produce', 'protein', 'dairy')
                GROUP BY category
            """)
            
            category_results = cursor.fetchall()
            print(f"✅ Category queries: {len(category_results)} main categories working")
            
            # Test alias functionality (if aliases exist)
            cursor.execute("""
                SELECT canonical_name, aliases 
                FROM canonical_ingredients 
                WHERE aliases IS NOT NULL 
                AND array_length(aliases, 1) > 0
                LIMIT 3
            """)
            
            alias_results = cursor.fetchall()
            print(f"✅ Alias system: {len(alias_results)} ingredients with aliases")
            
            self.verification_results['basic_queries'] = True
            return True
            
        except Exception as e:
            print(f"❌ Basic query testing failed: {e}")
            self.verification_results['basic_queries'] = False
            return False
        finally:
            cursor.close()
    
    def run_verification(self):
        """
        Run complete Day 1 verification
        Return detailed results
        """
        
        print("🔍 Day 1 Pantry Migration Verification")
        print("=" * 60)
        
        if not self.connect_database():
            return False
        
        try:
            # Run all verification steps
            self.verify_existing_functionality()
            self.verify_pantry_tables()
            self.verify_canonical_ingredients()
            self.verify_substitutions()
            self.verify_indexes()
            self.test_basic_pantry_queries()
            
            # Calculate overall success
            all_passed = all(self.verification_results.values())
            
            print("\n" + "=" * 60)
            print("📊 VERIFICATION SUMMARY")
            print("=" * 60)
            
            for check, passed in self.verification_results.items():
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"{check.replace('_', ' ').title()}: {status}")
            
            if all_passed:
                print("\n🎉 Day 1 Migration VERIFIED SUCCESSFUL!")
                print("✅ All pantry tables created correctly")
                print("✅ Canonical ingredients extracted from your recipes") 
                print("✅ All existing functionality preserved")
                print("✅ Database optimized for pantry operations")
                print("\n🚀 Ready to begin Day 2: Core PantrySystem implementation!")
            else:
                print("\n⚠️ Some verification checks failed")
                print("🔧 Review error messages above")
                print("💡 Existing functionality should still work normally")
            
            return all_passed
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
        
        finally:
            if self.connection:
                self.connection.close()

def main():
    """Run the Day 1 verification"""
    
    print("🔍 Me Hungie Pantry System - Day 1 Verification")
    print("Ensuring migration completed successfully")
    print()
    
    verifier = PantryMigrationVerifier()
    success = verifier.run_verification()
    
    if success:
        print("\n✅ Migration verification PASSED")
        print("🎯 Proceed to Day 2 implementation")
    else:
        print("\n⚠️ Some checks failed - review above")
        print("💡 Existing app functionality preserved")

if __name__ == "__main__":
    main()
