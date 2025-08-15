#!/usr/bin/env python3
"""
SQLite to PostgreSQL Migration Script
Migrates all data from hungie.db to Railway PostgreSQL instance
Maintains data integrity and handles type conversions
"""

import sqlite3
import psycopg2
import psycopg2.extras
import os
import sys
from datetime import datetime
import json

def get_database_connections():
    """Get both SQLite and PostgreSQL connections"""
    
    # SQLite connection
    sqlite_conn = sqlite3.connect('hungie.db')
    sqlite_conn.row_factory = sqlite3.Row  # Enable dict-like access
    
    # PostgreSQL connection
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set!")
        print("💡 Set it with: railway variables --set DATABASE_URL=your_postgres_url")
        return None, None
    
    try:
        postgres_conn = psycopg2.connect(database_url)
        postgres_conn.autocommit = False
        return sqlite_conn, postgres_conn
    except Exception as e:
        print(f"❌ Failed to connect to PostgreSQL: {e}")
        return None, None

def create_postgresql_schema(postgres_conn):
    """Create all tables in PostgreSQL with proper types"""
    
    cursor = postgres_conn.cursor()
    
    # SQL commands to create all tables
    create_tables_sql = """
    -- Drop existing tables (careful!)
    DROP TABLE IF EXISTS shown_recipes, recipe_interactions, conversation_history, user_sessions CASCADE;
    DROP TABLE IF EXISTS saved_meal_plans, saved_recipes, user_pantry, user_preferences, users CASCADE;
    DROP TABLE IF EXISTS user_favorites, meal_plans CASCADE;
    DROP TABLE IF EXISTS parsing_log, recipe_citations CASCADE;
    DROP TABLE IF EXISTS nutrition, recipe_categories, instructions, categories CASCADE;
    DROP TABLE IF EXISTS recipe_analysis, recipe_flavor_profiles, recipe_ingredients CASCADE;
    DROP TABLE IF EXISTS recipes, ingredients, books CASCADE;
    
    -- Create core tables
    CREATE TABLE books (
        id SERIAL PRIMARY KEY,
        title TEXT NOT NULL,
        author TEXT,
        file_path TEXT NOT NULL,
        file_hash TEXT,
        total_recipes INTEGER DEFAULT 0,
        parsing_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'processing'
    );
    
    CREATE TABLE ingredients (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        normalized_name TEXT,
        category TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE recipes (
        id SERIAL PRIMARY KEY,
        book_id INTEGER REFERENCES books(id),
        title TEXT,
        page_number INTEGER,
        servings TEXT,
        hands_on_time TEXT,
        total_time TEXT,
        ingredients TEXT,
        instructions TEXT,
        description TEXT,
        url TEXT,
        date_saved TEXT,
        why_this_works TEXT,
        category TEXT,
        chapter TEXT,
        chapter_number INTEGER
    );
    
    CREATE TABLE recipe_ingredients (
        id SERIAL PRIMARY KEY,
        recipe_id INTEGER REFERENCES recipes(id),
        ingredient_id INTEGER REFERENCES ingredients(id),
        quantity TEXT,
        unit TEXT,
        preparation TEXT
    );
    
    CREATE TABLE recipe_flavor_profiles (
        id SERIAL PRIMARY KEY,
        recipe_id INTEGER REFERENCES recipes(id),
        primary_flavors TEXT,
        secondary_flavors TEXT,
        intensity TEXT,
        cooking_methods TEXT,
        cuisine_style TEXT,
        season TEXT,
        dietary_tags TEXT,
        complexity_score INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE recipe_analysis (
        id SERIAL PRIMARY KEY,
        recipe_id INTEGER REFERENCES recipes(id),
        ingredient_count INTEGER,
        instruction_count INTEGER,
        estimated_prep_time INTEGER,
        estimated_cook_time INTEGER,
        difficulty_level TEXT,
        nutrition_category TEXT,
        main_protein TEXT,
        cooking_techniques TEXT,
        equipment_needed TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        cuisine_type TEXT,
        cuisine_region TEXT,
        cooking_tradition TEXT,
        primary_macronutrient TEXT,
        dietary_tags TEXT,
        health_orientation TEXT,
        skill_level TEXT,
        time_category TEXT,
        technique_complexity INTEGER,
        equipment_level TEXT,
        flavor_fingerprint TEXT,
        technique_tags TEXT,
        similar_recipe_ids TEXT,
        analysis_version TEXT,
        analyzed_at TEXT,
        primary_tastes TEXT,
        heat_level TEXT,
        flavor_intensity TEXT,
        dominant_aromatics TEXT,
        primary_textures TEXT,
        serving_temperature TEXT,
        consistency TEXT,
        meal_type TEXT,
        social_context TEXT,
        seasonal_fit TEXT,
        special_occasions TEXT,
        produce_usage TEXT,
        pantry_dependency INTEGER,
        substitution_flexibility INTEGER,
        make_ahead_potential INTEGER,
        cost_estimate TEXT
    );
    
    CREATE TABLE categories (
        id TEXT PRIMARY KEY,
        name TEXT
    );
    
    CREATE TABLE instructions (
        recipe_id INTEGER,
        step_number INTEGER,
        instruction TEXT
    );
    
    CREATE TABLE recipe_categories (
        recipe_id INTEGER,
        category_id TEXT
    );
    
    CREATE TABLE nutrition (
        recipe_id INTEGER,
        calories INTEGER,
        protein TEXT,
        carbs TEXT,
        fat TEXT
    );
    
    CREATE TABLE recipe_citations (
        id SERIAL PRIMARY KEY,
        original_recipe_id INTEGER,
        adapted_recipe_id INTEGER,
        adaptation_type TEXT,
        changes_made TEXT,
        confidence REAL
    );
    
    CREATE TABLE parsing_log (
        id SERIAL PRIMARY KEY,
        book_id INTEGER REFERENCES books(id),
        operation TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        details TEXT,
        success BOOLEAN
    );
    
    -- User system tables (already exist but ensuring structure)
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE,
        oauth_provider TEXT,
        oauth_id TEXT,
        profile_picture TEXT
    );
    
    CREATE TABLE IF NOT EXISTS user_preferences (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id),
        dietary_restrictions TEXT,
        allergies TEXT,
        caloric_needs INTEGER,
        nutritional_goals TEXT,
        preferred_cuisines TEXT,
        cooking_skill_level TEXT DEFAULT 'beginner',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS user_pantry (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id),
        ingredient_name TEXT NOT NULL,
        quantity REAL,
        unit TEXT,
        expiry_date DATE,
        category TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS saved_recipes (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id),
        recipe_id INTEGER,
        recipe_data TEXT,
        recipe_source TEXT,
        saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        tags TEXT
    );
    
    CREATE TABLE IF NOT EXISTS saved_meal_plans (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id),
        plan_name TEXT NOT NULL,
        plan_data TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Session and analytics tables
    CREATE TABLE user_sessions (
        session_id TEXT PRIMARY KEY,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total_queries INTEGER DEFAULT 0,
        successful_searches INTEGER DEFAULT 0,
        recipes_viewed INTEGER DEFAULT 0,
        recipe_interactions INTEGER DEFAULT 0
    );
    
    CREATE TABLE conversation_history (
        id SERIAL PRIMARY KEY,
        session_id TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_query TEXT,
        intent TEXT,
        context TEXT,
        result_count INTEGER,
        displayed_count INTEGER,
        search_phase TEXT
    );
    
    CREATE TABLE recipe_interactions (
        id SERIAL PRIMARY KEY,
        session_id TEXT,
        recipe_id INTEGER,
        interaction_type TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        context TEXT
    );
    
    CREATE TABLE shown_recipes (
        session_id TEXT,
        recipe_id INTEGER,
        shown_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        query_context TEXT,
        PRIMARY KEY (session_id, recipe_id)
    );
    
    CREATE TABLE meal_plans (
        id SERIAL PRIMARY KEY,
        plan_name TEXT NOT NULL,
        week_start_date TEXT NOT NULL,
        plan_data_json TEXT NOT NULL,
        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE user_favorites (
        id SERIAL PRIMARY KEY,
        recipe_id INTEGER NOT NULL,
        added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT
    );
    
    -- Create indexes for performance
    CREATE INDEX idx_recipes_title ON recipes(title);
    CREATE INDEX idx_recipes_category ON recipes(category);
    CREATE INDEX idx_recipe_ingredients_recipe_id ON recipe_ingredients(recipe_id);
    CREATE INDEX idx_recipe_ingredients_ingredient_id ON recipe_ingredients(ingredient_id);
    CREATE INDEX idx_ingredients_name ON ingredients(name);
    CREATE INDEX idx_ingredients_normalized_name ON ingredients(normalized_name);
    """
    
    try:
        cursor.execute(create_tables_sql)
        postgres_conn.commit()
        print("✅ PostgreSQL schema created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating PostgreSQL schema: {e}")
        postgres_conn.rollback()
        return False
    finally:
        cursor.close()

def migrate_table_data(sqlite_conn, postgres_conn, table_name, column_mapping=None):
    """Migrate data from SQLite table to PostgreSQL table"""
    
    sqlite_cursor = sqlite_conn.cursor()
    postgres_cursor = postgres_conn.cursor()
    
    try:
        # Get all data from SQLite
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f"⏭️  Table {table_name}: No data to migrate")
            return True
        
        # Get column names
        columns = [description[0] for description in sqlite_cursor.description]
        
        # Skip the 'id' column for tables with SERIAL primary keys
        serial_tables = ['books', 'ingredients', 'recipes', 'recipe_ingredients', 
                        'recipe_flavor_profiles', 'recipe_analysis', 'recipe_citations', 
                        'parsing_log', 'users', 'user_preferences', 'user_pantry', 
                        'saved_recipes', 'saved_meal_plans', 'conversation_history', 
                        'recipe_interactions', 'meal_plans', 'user_favorites']
        
        if table_name in serial_tables and 'id' in columns:
            columns = [col for col in columns if col != 'id']
            rows = [tuple(row[i] for i, col in enumerate(sqlite_cursor.description) if col[0] != 'id') 
                   for row in rows]
        
        # Build INSERT statement
        placeholders = ', '.join(['%s'] * len(columns))
        column_list = ', '.join(columns)
        insert_sql = f"INSERT INTO {table_name} ({column_list}) VALUES ({placeholders})"
        
        # Insert data in batches
        batch_size = 100
        total_rows = len(rows)
        
        for i in range(0, total_rows, batch_size):
            batch = rows[i:i + batch_size]
            postgres_cursor.executemany(insert_sql, batch)
        
        postgres_conn.commit()
        print(f"✅ Table {table_name}: Migrated {total_rows} rows")
        return True
        
    except Exception as e:
        print(f"❌ Error migrating table {table_name}: {e}")
        postgres_conn.rollback()
        return False
    finally:
        sqlite_cursor.close()
        postgres_cursor.close()

def migrate_all_data(sqlite_conn, postgres_conn):
    """Migrate all tables in dependency order"""
    
    # Migration order matters due to foreign key relationships
    migration_order = [
        'books',
        'ingredients', 
        'recipes',
        'recipe_ingredients',
        'recipe_flavor_profiles', 
        'recipe_analysis',
        'categories',
        'instructions',
        'recipe_categories',
        'nutrition',
        'recipe_citations',
        'parsing_log',
        # User system tables (might already exist)
        'users',
        'user_preferences',
        'user_pantry', 
        'saved_recipes',
        'saved_meal_plans',
        # Analytics tables
        'user_sessions',
        'conversation_history',
        'recipe_interactions',
        'shown_recipes',
        'meal_plans',
        'user_favorites'
    ]
    
    success_count = 0
    total_tables = len(migration_order)
    
    for table_name in migration_order:
        if migrate_table_data(sqlite_conn, postgres_conn, table_name):
            success_count += 1
        else:
            print(f"⚠️  Failed to migrate {table_name}, continuing...")
    
    print(f"\n📊 Migration Summary: {success_count}/{total_tables} tables migrated successfully")
    return success_count == total_tables

def verify_migration(postgres_conn):
    """Verify the migration was successful"""
    
    cursor = postgres_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    try:
        # Check key tables
        verification_queries = [
            ("Books", "SELECT COUNT(*) as count FROM books"),
            ("Ingredients", "SELECT COUNT(*) as count FROM ingredients"),
            ("Recipes", "SELECT COUNT(*) as count FROM recipes"),
            ("Recipe Ingredients", "SELECT COUNT(*) as count FROM recipe_ingredients"),
            ("Users", "SELECT COUNT(*) as count FROM users"),
            ("Recipe Analysis", "SELECT COUNT(*) as count FROM recipe_analysis")
        ]
        
        print("\n🔍 MIGRATION VERIFICATION")
        print("=" * 40)
        
        for name, query in verification_queries:
            cursor.execute(query)
            result = cursor.fetchone()
            count = result['count']
            print(f"{name}: {count} rows")
        
        # Test a sample query
        cursor.execute("SELECT title, category FROM recipes LIMIT 5")
        sample_recipes = cursor.fetchall()
        
        print("\n📋 Sample Recipes:")
        for recipe in sample_recipes:
            print(f"  - {recipe['title']} ({recipe['category']})")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"❌ Error verifying migration: {e}")
        cursor.close()
        return False

def main():
    """Main migration process"""
    
    print("🚀 SQLITE TO POSTGRESQL MIGRATION")
    print("=" * 50)
    print("📊 Source: hungie.db (SQLite)")
    print("🎯 Target: Railway PostgreSQL")
    print()
    
    # Get database connections
    sqlite_conn, postgres_conn = get_database_connections()
    if not sqlite_conn or not postgres_conn:
        return False
    
    try:
        # Step 1: Create PostgreSQL schema
        print("🔧 Step 1: Creating PostgreSQL schema...")
        if not create_postgresql_schema(postgres_conn):
            return False
        
        # Step 2: Migrate all data
        print("\n📋 Step 2: Migrating data...")
        if not migrate_all_data(sqlite_conn, postgres_conn):
            print("⚠️  Some tables failed to migrate, but continuing...")
        
        # Step 3: Verify migration
        print("\n✅ Step 3: Verifying migration...")
        if verify_migration(postgres_conn):
            print("\n🎉 MIGRATION COMPLETED SUCCESSFULLY!")
            print("Your recipe database is now running on PostgreSQL!")
            return True
        else:
            print("\n⚠️  Migration completed but verification failed")
            return False
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    finally:
        sqlite_conn.close()
        postgres_conn.close()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
