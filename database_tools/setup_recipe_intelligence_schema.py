#!/usr/bin/env python3
"""
🗃️ Recipe Intelligence Database Schema Setup
============================================

Sets up the enhanced database schema for our recipe intelligence systems:
- Recipe flavor profiles table
- Enhanced indexes for performance
- Compatible with our 1000+ recipe collection

Designed for PostgreSQL production environment.
"""

import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

def setup_recipe_intelligence_schema():
    """Set up enhanced database schema for recipe intelligence"""
    print("🗃️ SETTING UP RECIPE INTELLIGENCE SCHEMA")
    print("=" * 50)
    
    try:
        # Connect to database
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            # Fallback to Railway public URL
            db_url = "postgresql://postgres:bBPQiSOwjkCnYdydFUcQKXeiFGFdIsgh@junction.proxy.rlwy.net:40067/railway"
        
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✅ Connected to PostgreSQL database")
        
        # Create recipe_flavor_profiles table with enhanced schema
        print("📊 Creating recipe_flavor_profiles table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipe_flavor_profiles (
                id SERIAL PRIMARY KEY,
                recipe_id INTEGER NOT NULL,
                primary_flavors JSONB DEFAULT '[]',
                secondary_flavors JSONB DEFAULT '[]',
                intensity VARCHAR(20) DEFAULT 'moderate',
                cooking_methods JSONB DEFAULT '[]',
                cuisine_style VARCHAR(50) DEFAULT 'american',
                season VARCHAR(20) DEFAULT 'all-season',
                dietary_tags JSONB DEFAULT '[]',
                complexity_score INTEGER DEFAULT 5,
                harmony_score DECIMAL(3,2) DEFAULT 0.50,
                ingredient_count INTEGER DEFAULT 0,
                technique_difficulty VARCHAR(20) DEFAULT 'beginner',
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                
                -- Constraints
                CONSTRAINT fk_recipe_flavor_profiles_recipe_id 
                    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
                CONSTRAINT uq_recipe_flavor_profiles_recipe_id 
                    UNIQUE (recipe_id),
                CONSTRAINT chk_complexity_score 
                    CHECK (complexity_score >= 1 AND complexity_score <= 10),
                CONSTRAINT chk_harmony_score 
                    CHECK (harmony_score >= 0.0 AND harmony_score <= 1.0),
                CONSTRAINT chk_intensity 
                    CHECK (intensity IN ('mild', 'moderate', 'bold', 'intense')),
                CONSTRAINT chk_technique_difficulty 
                    CHECK (technique_difficulty IN ('beginner', 'intermediate', 'advanced'))
            )
        """)
        print("✅ recipe_flavor_profiles table ready")
        
        # Create enhanced indexes for performance
        print("🚀 Creating performance indexes...")
        
        indexes = [
            ("idx_recipe_flavor_profiles_recipe_id", "recipe_id"),
            ("idx_recipe_flavor_profiles_cuisine", "cuisine_style"),
            ("idx_recipe_flavor_profiles_intensity", "intensity"),
            ("idx_recipe_flavor_profiles_complexity", "complexity_score"),
            ("idx_recipe_flavor_profiles_harmony", "harmony_score"),
            ("idx_recipe_flavor_profiles_difficulty", "technique_difficulty"),
            ("idx_recipe_flavor_profiles_season", "season"),
        ]
        
        for index_name, column in indexes:
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS {index_name} 
                ON recipe_flavor_profiles ({column})
            """)
            print(f"  ✅ Index {index_name} created")
        
        # Create JSONB indexes for array fields
        print("📋 Creating JSONB indexes...")
        
        jsonb_indexes = [
            ("idx_recipe_flavor_profiles_primary_flavors", "primary_flavors"),
            ("idx_recipe_flavor_profiles_cooking_methods", "cooking_methods"),
            ("idx_recipe_flavor_profiles_dietary_tags", "dietary_tags"),
        ]
        
        for index_name, column in jsonb_indexes:
            cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS {index_name} 
                ON recipe_flavor_profiles USING GIN ({column})
            """)
            print(f"  ✅ JSONB Index {index_name} created")
        
        # Create recipe_intelligence_cache table for performance optimization
        print("⚡ Creating intelligence cache table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipe_intelligence_cache (
                id SERIAL PRIMARY KEY,
                cache_key VARCHAR(255) NOT NULL UNIQUE,
                cache_data JSONB NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Create indexes separately
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_intelligence_cache_key 
            ON recipe_intelligence_cache (cache_key)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_intelligence_cache_expires 
            ON recipe_intelligence_cache (expires_at)
        """)
        print("✅ Intelligence cache table ready")
        
        # Create recipe_search_enhancements table
        print("🔍 Creating search enhancements table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipe_search_enhancements (
                id SERIAL PRIMARY KEY,
                recipe_id INTEGER NOT NULL,
                search_keywords TEXT[] DEFAULT '{}',
                popularity_score DECIMAL(5,2) DEFAULT 0.0,
                user_rating_avg DECIMAL(3,2) DEFAULT 0.0,
                search_rank INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT NOW(),
                
                -- Constraints
                CONSTRAINT fk_search_enhancements_recipe_id 
                    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
                CONSTRAINT uq_search_enhancements_recipe_id 
                    UNIQUE (recipe_id)
            )
        """)
        print("✅ Search enhancements table ready")
        
        # Create indexes for search enhancements
        search_indexes = [
            ("idx_search_enhancements_recipe_id", "recipe_id"),
            ("idx_search_enhancements_popularity", "popularity_score"),
            ("idx_search_enhancements_rating", "user_rating_avg"),
            ("idx_search_enhancements_rank", "search_rank"),
            ("idx_search_enhancements_keywords", "search_keywords"),
        ]
        
        for index_name, column in search_indexes:
            if column == "search_keywords":
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS {index_name} 
                    ON recipe_search_enhancements USING GIN ({column})
                """)
            else:
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS {index_name} 
                    ON recipe_search_enhancements ({column})
                """)
            print(f"  ✅ Search index {index_name} created")
        
        # Add helpful database functions
        print("⚙️ Creating utility functions...")
        
        # Function to get recipes by flavor profile
        cursor.execute("""
            CREATE OR REPLACE FUNCTION get_recipes_by_flavor(
                target_flavors TEXT[],
                target_cuisine VARCHAR(50) DEFAULT NULL,
                min_complexity INTEGER DEFAULT 1,
                max_complexity INTEGER DEFAULT 10,
                result_limit INTEGER DEFAULT 10
            ) RETURNS TABLE (
                recipe_id INTEGER,
                title TEXT,
                primary_flavors JSONB,
                cuisine_style VARCHAR(50),
                complexity_score INTEGER,
                harmony_score DECIMAL(3,2)
            ) AS $$
            BEGIN
                RETURN QUERY
                SELECT 
                    rfp.recipe_id,
                    r.title,
                    rfp.primary_flavors,
                    rfp.cuisine_style,
                    rfp.complexity_score,
                    rfp.harmony_score
                FROM recipe_flavor_profiles rfp
                JOIN recipes r ON rfp.recipe_id = r.id
                WHERE 
                    (target_cuisine IS NULL OR rfp.cuisine_style = target_cuisine)
                    AND rfp.complexity_score BETWEEN min_complexity AND max_complexity
                    AND (
                        SELECT COUNT(*)
                        FROM jsonb_array_elements_text(rfp.primary_flavors) AS flavor
                        WHERE flavor = ANY(target_flavors)
                    ) > 0
                ORDER BY rfp.harmony_score DESC, rfp.complexity_score
                LIMIT result_limit;
            END;
            $$ LANGUAGE plpgsql;
        """)
        print("  ✅ get_recipes_by_flavor() function created")
        
        # Function to update search rankings
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_recipe_search_rankings() RETURNS INTEGER AS $$
            DECLARE
                updated_count INTEGER := 0;
            BEGIN
                -- Update search rankings based on harmony score and complexity
                UPDATE recipe_search_enhancements 
                SET 
                    search_rank = subquery.new_rank,
                    last_updated = NOW()
                FROM (
                    SELECT 
                        rse.recipe_id,
                        ROW_NUMBER() OVER (
                            ORDER BY 
                                COALESCE(rfp.harmony_score, 0.5) DESC,
                                COALESCE(rse.popularity_score, 0.0) DESC,
                                COALESCE(rse.user_rating_avg, 0.0) DESC
                        ) as new_rank
                    FROM recipe_search_enhancements rse
                    LEFT JOIN recipe_flavor_profiles rfp ON rse.recipe_id = rfp.recipe_id
                ) subquery
                WHERE recipe_search_enhancements.recipe_id = subquery.recipe_id;
                
                GET DIAGNOSTICS updated_count = ROW_COUNT;
                RETURN updated_count;
            END;
            $$ LANGUAGE plpgsql;
        """)
        print("  ✅ update_recipe_search_rankings() function created")
        
        # Check current database state
        print("\n📊 Database State Summary:")
        
        # Count total recipes
        cursor.execute("SELECT COUNT(*) FROM recipes")
        total_recipes = cursor.fetchone()[0]
        print(f"  Total recipes: {total_recipes:,}")
        
        # Count recipes with flavor profiles
        cursor.execute("SELECT COUNT(*) FROM recipe_flavor_profiles")
        flavor_profiles = cursor.fetchone()[0]
        print(f"  Recipes with flavor profiles: {flavor_profiles:,}")
        
        if total_recipes > 0:
            coverage = (flavor_profiles / total_recipes) * 100
            print(f"  Flavor profile coverage: {coverage:.1f}%")
        
        # Check for ATK recipes specifically
        cursor.execute("SELECT COUNT(*) FROM recipes WHERE source ILIKE '%atk%' OR source ILIKE '%america%test%kitchen%'")
        atk_recipes = cursor.fetchone()[0]
        if atk_recipes > 0:
            print(f"  ATK recipes: {atk_recipes:,}")
        
        conn.close()
        
        print(f"\n🎉 SCHEMA SETUP COMPLETE!")
        print("=" * 50)
        print("✅ All tables and indexes are ready")
        print("✅ Performance optimizations in place")
        print("✅ Ready for 1000+ recipe analysis")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up schema: {e}")
        return False

def verify_schema():
    """Verify that all required tables and indexes exist"""
    print("\n🔍 VERIFYING SCHEMA SETUP")
    print("=" * 30)
    
    try:
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            db_url = "postgresql://postgres:bBPQiSOwjkCnYdydFUcQKXeiFGFdIsgh@junction.proxy.rlwy.net:40067/railway"
        
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Check tables
        required_tables = [
            'recipes',
            'recipe_flavor_profiles',
            'recipe_intelligence_cache',
            'recipe_search_enhancements'
        ]
        
        for table in required_tables:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name = %s
                )
            """, (table,))
            
            exists = cursor.fetchone()[0]
            status = "✅" if exists else "❌"
            print(f"  {status} Table '{table}': {'EXISTS' if exists else 'MISSING'}")
        
        # Check key indexes
        cursor.execute("""
            SELECT indexname FROM pg_indexes 
            WHERE tablename = 'recipe_flavor_profiles'
            AND indexname LIKE 'idx_%'
        """)
        
        indexes = [row[0] for row in cursor.fetchall()]
        print(f"  ✅ Found {len(indexes)} performance indexes")
        
        # Check functions
        cursor.execute("""
            SELECT routine_name FROM information_schema.routines 
            WHERE routine_type = 'FUNCTION' 
            AND routine_name IN ('get_recipes_by_flavor', 'update_recipe_search_rankings')
        """)
        
        functions = [row[0] for row in cursor.fetchall()]
        print(f"  ✅ Found {len(functions)} utility functions")
        
        conn.close()
        
        print("✅ Schema verification complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error verifying schema: {e}")
        return False

def main():
    """Set up the complete recipe intelligence database schema"""
    print("🚀 RECIPE INTELLIGENCE DATABASE SETUP")
    print("=" * 60)
    
    # Setup schema
    success = setup_recipe_intelligence_schema()
    
    if success:
        # Verify setup
        verify_schema()
        
        print(f"\n🎯 NEXT STEPS:")
        print("1. Run recipe flavor analysis: python core_systems/recipe_flavor_analyzer.py")
        print("2. Test intelligence hub: python core_systems/recipe_intelligence_hub.py")
        print("3. Integrate with hungie_server.py for production use")
    else:
        print("❌ Schema setup failed. Please check errors above.")

if __name__ == "__main__":
    main()
