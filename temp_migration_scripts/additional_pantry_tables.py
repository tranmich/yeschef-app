"""
🗄️ Additional Pantry Database Tables - Day 2 Core System Support
================================================================

This script creates the additional database tables needed to support
the advanced pantry intelligence features: review queues, logging,
and analytics.

These complement the foundation tables created in Day 1 migration.
"""

import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def create_additional_pantry_tables():
    """Create additional tables for Day 2 pantry intelligence features"""

    connection = None

    try:
        # Connect to Railway PostgreSQL database using DATABASE_URL
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            raise Exception("DATABASE_URL environment variable required")

        connection = psycopg2.connect(db_url)

        cursor = connection.cursor()

        print("🗄️ Creating additional pantry intelligence tables...")

        # 1. Ingredient Review Queue - For uncertain auto-mappings
        print("📝 Creating ingredient_review_queue table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ingredient_review_queue (
                id SERIAL PRIMARY KEY,
                recipe_id INTEGER NOT NULL,
                raw_text TEXT NOT NULL,
                suggested_canonical_id INTEGER,
                suggested_canonical_name VARCHAR(200),
                confidence DECIMAL(3,2),
                alternative_suggestions JSONB,
                amount DECIMAL(10,2),
                unit VARCHAR(50),
                modifiers TEXT[],
                created_at TIMESTAMP DEFAULT NOW(),
                
                FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
                FOREIGN KEY (suggested_canonical_id) REFERENCES canonical_ingredients(id)
            );
        """)

        # Add index for efficient queue retrieval
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_review_queue_created 
            ON ingredient_review_queue(created_at);
        """)

        # 2. Recipe Processing Logs - Track processing statistics
        print("📊 Creating recipe_processing_logs table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipe_processing_logs (
                id SERIAL PRIMARY KEY,
                recipe_id INTEGER NOT NULL,
                total_ingredients INTEGER NOT NULL,
                auto_mapped INTEGER NOT NULL DEFAULT 0,
                queued_for_review INTEGER NOT NULL DEFAULT 0,
                failed_mappings INTEGER NOT NULL DEFAULT 0,
                processing_time DECIMAL(6,3), -- seconds
                success_rate DECIMAL(5,2), -- percentage
                created_at TIMESTAMP DEFAULT NOW(),
                
                FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
            );
        """)

        # Add index for analytics queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_processing_logs_date 
            ON recipe_processing_logs(created_at);
        """)

        # 3. Ingredient Mapping Logs - Track mapping decisions for learning
        print("🧠 Creating ingredient_mapping_logs table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ingredient_mapping_logs (
                id SERIAL PRIMARY KEY,
                raw_text TEXT NOT NULL,
                suggested_id INTEGER,
                verified_id INTEGER,
                confidence DECIMAL(3,2),
                was_correct BOOLEAN GENERATED ALWAYS AS (suggested_id = verified_id) STORED,
                created_at TIMESTAMP DEFAULT NOW(),
                
                FOREIGN KEY (suggested_id) REFERENCES canonical_ingredients(id),
                FOREIGN KEY (verified_id) REFERENCES canonical_ingredients(id),
                
                -- Prevent duplicate logging of same mapping decision
                UNIQUE(raw_text, suggested_id, verified_id)
            );
        """)

        # Add indexes for learning queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_mapping_logs_raw_text 
            ON ingredient_mapping_logs(raw_text);
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_mapping_logs_accuracy 
            ON ingredient_mapping_logs(was_correct, created_at);
        """)

        # 4. Add verified_manually column to recipe_ingredients (if not exists)
        print("🔧 Enhancing recipe_ingredients table...")
        cursor.execute("""
            ALTER TABLE recipe_ingredients 
            ADD COLUMN IF NOT EXISTS verified_manually BOOLEAN DEFAULT FALSE,
            ADD COLUMN IF NOT EXISTS canonical_ingredient_id INTEGER,
            ADD COLUMN IF NOT EXISTS confidence DECIMAL(3,2),
            ADD COLUMN IF NOT EXISTS modifiers TEXT[];
        """)

        # Copy data from ingredient_id to canonical_ingredient_id if needed
        cursor.execute("""
            UPDATE recipe_ingredients 
            SET canonical_ingredient_id = ingredient_id 
            WHERE canonical_ingredient_id IS NULL AND ingredient_id IS NOT NULL;
        """)

        # Add index for verified mappings
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_verified 
            ON recipe_ingredients(verified_manually);
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_canonical 
            ON recipe_ingredients(recipe_id, canonical_ingredient_id);
        """)

        # 5. Update user_pantry to ensure all needed columns exist
        print("🥫 Enhancing user_pantry table...")
        # Note: actual columns are user_id, ingredient_id, amount_status, expiry_date, notes, added_at
        # Add any missing columns for Day 2 functionality
        cursor.execute("""
            ALTER TABLE user_pantry 
            ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'good',
            ADD COLUMN IF NOT EXISTS location VARCHAR(50),
            ADD COLUMN IF NOT EXISTS amount DECIMAL(10,2),
            ADD COLUMN IF NOT EXISTS unit VARCHAR(50),
            ADD COLUMN IF NOT EXISTS updated_date TIMESTAMP DEFAULT NOW();
        """)

        # Update to use canonical_ingredient_id instead of ingredient_id for consistency
        cursor.execute("""
            ALTER TABLE user_pantry 
            ADD COLUMN IF NOT EXISTS canonical_ingredient_id INTEGER;
        """)

        # Copy data from ingredient_id to canonical_ingredient_id if needed
        cursor.execute("""
            UPDATE user_pantry 
            SET canonical_ingredient_id = ingredient_id 
            WHERE canonical_ingredient_id IS NULL AND ingredient_id IS NOT NULL;
        """)

        # Add indexes for pantry queries (after columns are added)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_pantry_status 
            ON user_pantry(user_id, status);
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_pantry_expiry 
            ON user_pantry(user_id, expiry_date) 
            WHERE expiry_date IS NOT NULL;
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_pantry_canonical 
            ON user_pantry(user_id, canonical_ingredient_id);
        """)

        # 6. Create view for pantry intelligence analytics
        print("📈 Creating pantry intelligence analytics view...")
        cursor.execute("""
            CREATE OR REPLACE VIEW pantry_intelligence_stats AS
            SELECT 
                'mapping_accuracy' as metric,
                AVG(CASE WHEN was_correct THEN 100.0 ELSE 0.0 END) as value,
                'percentage' as unit,
                COUNT(*) as sample_size
            FROM ingredient_mapping_logs
            WHERE created_at >= NOW() - INTERVAL '7 days'
            
            UNION ALL
            
            SELECT 
                'auto_mapping_rate' as metric,
                AVG(auto_mapped::float / total_ingredients * 100) as value,
                'percentage' as unit,
                COUNT(*) as sample_size
            FROM recipe_processing_logs
            WHERE created_at >= NOW() - INTERVAL '7 days'
            
            UNION ALL
            
            SELECT 
                'review_queue_size' as metric,
                COUNT(*)::float as value,
                'items' as unit,
                1 as sample_size
            FROM ingredient_review_queue
            
            UNION ALL
            
            SELECT 
                'avg_processing_time' as metric,
                AVG(processing_time) as value,
                'seconds' as unit,
                COUNT(*) as sample_size
            FROM recipe_processing_logs
            WHERE created_at >= NOW() - INTERVAL '7 days';
        """)

        # Commit all changes
        connection.commit()

        print("\n✅ Successfully created additional pantry intelligence tables:")
        print("   📝 ingredient_review_queue - Uncertain mappings awaiting review")
        print("   📊 recipe_processing_logs - Processing statistics and monitoring")
        print("   🧠 ingredient_mapping_logs - Learning data for intelligence improvement")
        print("   🔧 Enhanced recipe_ingredients - Added verification tracking")
        print("   🥫 Enhanced user_pantry - Added location, notes, timestamps")
        print("   📈 pantry_intelligence_stats - Analytics view for monitoring")

        print(f"\n🎊 Day 2 database enhancement complete!")
        print("   Ready for core pantry intelligence system deployment!")

        return True

    except Exception as e:
        print(f"❌ Failed to create additional tables: {e}")
        if connection:
            connection.rollback()
        return False

    finally:
        if connection:
            connection.close()

def verify_additional_tables():
    """Verify that all additional tables were created successfully"""

    connection = None

    try:
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            raise Exception("DATABASE_URL environment variable required")

        connection = psycopg2.connect(db_url)

        cursor = connection.cursor()

        print("🔍 Verifying additional pantry intelligence tables...")

        # Check each table exists and has expected structure
        tables_to_check = [
            'ingredient_review_queue',
            'recipe_processing_logs',
            'ingredient_mapping_logs'
        ]

        for table_name in tables_to_check:
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name = %s
            """, (table_name,))

            if cursor.fetchone()[0] > 0:
                # Get column count
                cursor.execute("""
                    SELECT COUNT(*) FROM information_schema.columns
                    WHERE table_name = %s
                """, (table_name,))

                column_count = cursor.fetchone()[0]
                print(f"   ✅ {table_name}: exists with {column_count} columns")
            else:
                print(f"   ❌ {table_name}: NOT FOUND")
                return False

        # Check the analytics view
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.views 
            WHERE table_name = 'pantry_intelligence_stats'
        """)

        if cursor.fetchone()[0] > 0:
            print(f"   ✅ pantry_intelligence_stats: analytics view created")
        else:
            print(f"   ❌ pantry_intelligence_stats: view NOT FOUND")
            return False

        # Test the analytics view
        cursor.execute("SELECT metric, value, unit FROM pantry_intelligence_stats LIMIT 1")
        test_result = cursor.fetchone()

        if test_result:
            print(f"   ✅ Analytics view functional: {test_result[0]} = {test_result[1]} {test_result[2]}")

        print("\n🎊 All additional tables verified successfully!")
        print("   Database is ready for Day 2 core system deployment!")

        return True

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    print("🗄️ DAY 2 ADDITIONAL DATABASE TABLES CREATION")
    print("=" * 60)

    # Create additional tables
    if create_additional_pantry_tables():

        # Verify tables were created correctly
        if verify_additional_tables():
            print("\n🚀 DATABASE ENHANCEMENT COMPLETE!")
            print("   Ready to deploy Day 2 core pantry intelligence system!")
        else:
            print("\n❌ VERIFICATION FAILED!")
            print("   Please check the database and try again.")
    else:
        print("\n❌ TABLE CREATION FAILED!")
        print("   Please check your database connection and permissions.")
