#!/usr/bin/env python3
"""
Initialize social features database tables
Run this script to create all necessary tables for friends, households, and social features
"""

import sqlite3
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Get database connection based on environment"""
    database_url = os.getenv('DATABASE_URL')
    
    if database_url and database_url.startswith('postgresql'):
        # PostgreSQL connection
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        return conn, 'postgresql'
    else:
        # SQLite connection
        db_path = os.getenv('DATABASE_PATH', 'hungie.db')
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn, 'sqlite'

def create_social_tables():
    """Create all social features tables"""
    
    conn, db_type = get_db_connection()
    cursor = conn.cursor()
    
    print("🚀 Creating social features database tables...")
    
    # SQL for different database types
    if db_type == 'postgresql':
        # PostgreSQL syntax
        tables = [
            # Friend requests table
            """
            CREATE TABLE IF NOT EXISTS friend_requests (
                id SERIAL PRIMARY KEY,
                requester_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                recipient_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                message TEXT,
                status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'declined')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(requester_id, recipient_id)
            )
            """,
            
            # Friendships table (accepted friends)
            """
            CREATE TABLE IF NOT EXISTS friendships (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                friend_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                status VARCHAR(20) DEFAULT 'accepted' CHECK (status IN ('accepted', 'blocked')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, friend_id)
            )
            """,
            
            # Households table
            """
            CREATE TABLE IF NOT EXISTS households (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                created_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Household members table
            """
            CREATE TABLE IF NOT EXISTS household_members (
                id SERIAL PRIMARY KEY,
                household_id INTEGER NOT NULL REFERENCES households(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                role VARCHAR(50) DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member')),
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(household_id, user_id)
            )
            """,
            
            # Shared grocery lists table
            """
            CREATE TABLE IF NOT EXISTS shared_grocery_lists (
                id SERIAL PRIMARY KEY,
                household_id INTEGER NOT NULL REFERENCES households(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL DEFAULT 'Grocery List',
                description TEXT,
                created_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Shared grocery list items table
            """
            CREATE TABLE IF NOT EXISTS shared_grocery_items (
                id SERIAL PRIMARY KEY,
                list_id INTEGER NOT NULL REFERENCES shared_grocery_lists(id) ON DELETE CASCADE,
                item_name VARCHAR(255) NOT NULL,
                quantity VARCHAR(50),
                category VARCHAR(100),
                is_completed BOOLEAN DEFAULT FALSE,
                completed_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
                completed_at TIMESTAMP,
                added_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Shared meal plans table
            """
            CREATE TABLE IF NOT EXISTS shared_meal_plans (
                id SERIAL PRIMARY KEY,
                household_id INTEGER NOT NULL REFERENCES households(id) ON DELETE CASCADE,
                week_start_date DATE NOT NULL,
                created_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(household_id, week_start_date)
            )
            """,
            
            # Planned meals table
            """
            CREATE TABLE IF NOT EXISTS planned_meals (
                id SERIAL PRIMARY KEY,
                meal_plan_id INTEGER NOT NULL REFERENCES shared_meal_plans(id) ON DELETE CASCADE,
                day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
                meal_type VARCHAR(20) NOT NULL CHECK (meal_type IN ('breakfast', 'lunch', 'dinner')),
                recipe_id INTEGER REFERENCES recipes(id) ON DELETE SET NULL,
                recipe_title VARCHAR(255),
                recipe_description TEXT,
                assigned_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(meal_plan_id, day_of_week, meal_type)
            )
            """,
            
            # Recipe sharing table
            """
            CREATE TABLE IF NOT EXISTS shared_recipes (
                id SERIAL PRIMARY KEY,
                recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
                shared_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                shared_with_type VARCHAR(20) NOT NULL CHECK (shared_with_type IN ('friend', 'household', 'public')),
                shared_with_id INTEGER, -- friend_id or household_id
                message TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Community recipe interactions table
            """
            CREATE TABLE IF NOT EXISTS recipe_interactions (
                id SERIAL PRIMARY KEY,
                recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                interaction_type VARCHAR(20) NOT NULL CHECK (interaction_type IN ('like', 'save', 'view')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(recipe_id, user_id, interaction_type)
            )
            """,
            
            # Recipe comments table
            """
            CREATE TABLE IF NOT EXISTS recipe_comments (
                id SERIAL PRIMARY KEY,
                recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                comment_text TEXT NOT NULL,
                rating INTEGER CHECK (rating BETWEEN 1 AND 5),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Comment likes table
            """
            CREATE TABLE IF NOT EXISTS comment_likes (
                id SERIAL PRIMARY KEY,
                comment_id INTEGER NOT NULL REFERENCES recipe_comments(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(comment_id, user_id)
            )
            """
        ]
    else:
        # SQLite syntax
        tables = [
            # Friend requests table
            """
            CREATE TABLE IF NOT EXISTS friend_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                requester_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                recipient_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                message TEXT,
                status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'declined')),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(requester_id, recipient_id)
            )
            """,
            
            # Friendships table (accepted friends)
            """
            CREATE TABLE IF NOT EXISTS friendships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                friend_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                status TEXT DEFAULT 'accepted' CHECK (status IN ('accepted', 'blocked')),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, friend_id)
            )
            """,
            
            # Households table
            """
            CREATE TABLE IF NOT EXISTS households (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                created_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Household members table
            """
            CREATE TABLE IF NOT EXISTS household_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                household_id INTEGER NOT NULL REFERENCES households(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                role TEXT DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member')),
                joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(household_id, user_id)
            )
            """,
            
            # Shared grocery lists table
            """
            CREATE TABLE IF NOT EXISTS shared_grocery_lists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                household_id INTEGER NOT NULL REFERENCES households(id) ON DELETE CASCADE,
                name TEXT NOT NULL DEFAULT 'Grocery List',
                description TEXT,
                created_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Shared grocery list items table
            """
            CREATE TABLE IF NOT EXISTS shared_grocery_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                list_id INTEGER NOT NULL REFERENCES shared_grocery_lists(id) ON DELETE CASCADE,
                item_name TEXT NOT NULL,
                quantity TEXT,
                category TEXT,
                is_completed BOOLEAN DEFAULT FALSE,
                completed_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
                completed_at DATETIME,
                added_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Shared meal plans table
            """
            CREATE TABLE IF NOT EXISTS shared_meal_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                household_id INTEGER NOT NULL REFERENCES households(id) ON DELETE CASCADE,
                week_start_date DATE NOT NULL,
                created_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(household_id, week_start_date)
            )
            """,
            
            # Planned meals table
            """
            CREATE TABLE IF NOT EXISTS planned_meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meal_plan_id INTEGER NOT NULL REFERENCES shared_meal_plans(id) ON DELETE CASCADE,
                day_of_week INTEGER NOT NULL CHECK (day_of_week BETWEEN 0 AND 6),
                meal_type TEXT NOT NULL CHECK (meal_type IN ('breakfast', 'lunch', 'dinner')),
                recipe_id INTEGER REFERENCES recipes(id) ON DELETE SET NULL,
                recipe_title TEXT,
                recipe_description TEXT,
                assigned_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(meal_plan_id, day_of_week, meal_type)
            )
            """,
            
            # Recipe sharing table
            """
            CREATE TABLE IF NOT EXISTS shared_recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
                shared_by INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                shared_with_type TEXT NOT NULL CHECK (shared_with_type IN ('friend', 'household', 'public')),
                shared_with_id INTEGER, -- friend_id or household_id
                message TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Community recipe interactions table
            """
            CREATE TABLE IF NOT EXISTS recipe_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                interaction_type TEXT NOT NULL CHECK (interaction_type IN ('like', 'save', 'view')),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(recipe_id, user_id, interaction_type)
            )
            """,
            
            # Recipe comments table
            """
            CREATE TABLE IF NOT EXISTS recipe_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                comment_text TEXT NOT NULL,
                rating INTEGER CHECK (rating BETWEEN 1 AND 5),
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Comment likes table
            """
            CREATE TABLE IF NOT EXISTS comment_likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comment_id INTEGER NOT NULL REFERENCES recipe_comments(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(comment_id, user_id)
            )
            """
        ]
    
    # Execute table creation
    for i, table_sql in enumerate(tables, 1):
        try:
            cursor.execute(table_sql)
            print(f"✅ Table {i}/12 created successfully")
        except Exception as e:
            print(f"❌ Failed to create table {i}: {e}")
    
    # Create indexes for better performance
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_friend_requests_recipient ON friend_requests(recipient_id)",
        "CREATE INDEX IF NOT EXISTS idx_friend_requests_requester ON friend_requests(requester_id)",
        "CREATE INDEX IF NOT EXISTS idx_friendships_user ON friendships(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_friendships_friend ON friendships(friend_id)",
        "CREATE INDEX IF NOT EXISTS idx_household_members_household ON household_members(household_id)",
        "CREATE INDEX IF NOT EXISTS idx_household_members_user ON household_members(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_shared_grocery_items_list ON shared_grocery_items(list_id)",
        "CREATE INDEX IF NOT EXISTS idx_planned_meals_plan ON planned_meals(meal_plan_id)",
        "CREATE INDEX IF NOT EXISTS idx_recipe_interactions_recipe ON recipe_interactions(recipe_id)",
        "CREATE INDEX IF NOT EXISTS idx_recipe_interactions_user ON recipe_interactions(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_recipe_comments_recipe ON recipe_comments(recipe_id)",
        "CREATE INDEX IF NOT EXISTS idx_comment_likes_comment ON comment_likes(comment_id)"
    ]
    
    print("\n🔍 Creating database indexes...")
    for i, index_sql in enumerate(indexes, 1):
        try:
            cursor.execute(index_sql)
            print(f"✅ Index {i}/{len(indexes)} created successfully")
        except Exception as e:
            print(f"❌ Failed to create index {i}: {e}")
    
    # Commit changes
    if db_type == 'sqlite':
        conn.commit()
    
    cursor.close()
    conn.close()
    
    print("\n🎉 Social features database initialization complete!")
    print("✅ All tables and indexes created successfully")
    print("\n📋 Created tables:")
    print("   • friend_requests - Friend request management")
    print("   • friendships - Accepted friend relationships")
    print("   • households - Family/household groups")
    print("   • household_members - Household membership")
    print("   • shared_grocery_lists - Collaborative shopping lists")
    print("   • shared_grocery_items - Individual grocery items")
    print("   • shared_meal_plans - Weekly meal planning")
    print("   • planned_meals - Individual meal entries")
    print("   • shared_recipes - Recipe sharing system")
    print("   • recipe_interactions - Likes, saves, views")
    print("   • recipe_comments - User comments and ratings")
    print("   • comment_likes - Comment interaction system")

if __name__ == '__main__':
    create_social_tables()