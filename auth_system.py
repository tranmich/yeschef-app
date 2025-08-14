#!/usr/bin/env python3
"""
Authentication System for Hungie
Handles user registration, login, JWT tokens, and OAuth integration
"""

import sqlite3
import psycopg2
import psycopg2.extras
import hashlib
import secrets
import os
from datetime import datetime, timedelta
from flask import jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
from authlib.integrations.flask_client import OAuth
import logging

logger = logging.getLogger(__name__)

class AuthenticationSystem:
    def __init__(self, app, get_db_connection=None):
        self.app = app
        self.get_db_connection = get_db_connection
        
        # Fallback to direct database connection if not provided
        if not self.get_db_connection:
            self.get_db_connection = self._get_default_db_connection
            
        self.bcrypt = Bcrypt(app)
        
        # Configure JWT
        app.config['JWT_SECRET_KEY'] = secrets.token_hex(32)  # Generate secure secret
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
        self.jwt = JWTManager(app)
        
        # Configure OAuth
        self.oauth = OAuth(app)
        self._setup_oauth()
        
        # Initialize database
        self._init_user_database()
        
        logger.info("[OK] Authentication system initialized")
    
    def _get_default_db_connection(self):
        """Default database connection for fallback"""
        try:
            # Use PostgreSQL connection from Railway environment
            database_url = os.getenv('DATABASE_URL')
            if database_url:
                # PostgreSQL connection
                conn = psycopg2.connect(database_url)
                conn.cursor_factory = psycopg2.extras.RealDictCursor
                logger.info("✅ Auth system connected to PostgreSQL database")
                return conn
            else:
                # Fallback to SQLite for local development
                conn = sqlite3.connect('hungie.db')
                conn.row_factory = sqlite3.Row
                logger.info("✅ Auth system connected to SQLite database (local)")
                return conn
        except Exception as e:
            logger.error(f"Auth database connection error: {e}")
            raise
    
    def _setup_oauth(self):
        """Setup Google and Facebook OAuth"""
        # Google OAuth
        self.google = self.oauth.register(
            name='google',
            client_id=self.app.config.get('GOOGLE_CLIENT_ID'),
            client_secret=self.app.config.get('GOOGLE_CLIENT_SECRET'),
            client_kwargs={
                'scope': 'openid email profile'
            },
            server_metadata_url='https://accounts.google.com/.well-known/openid_configuration'
        )
        
        # Facebook OAuth
        self.facebook = self.oauth.register(
            name='facebook',
            client_id=self.app.config.get('FACEBOOK_CLIENT_ID'),
            client_secret=self.app.config.get('FACEBOOK_CLIENT_SECRET'),
            client_kwargs={'scope': 'email'},
            api_base_url='https://graph.facebook.com/',
            access_token_url='https://graph.facebook.com/oauth/access_token',
            authorize_url='https://www.facebook.com/dialog/oauth',
        )
    
    def _init_user_database(self):
        """Initialize user tables in the database"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Check if we're using PostgreSQL or SQLite
            database_url = os.getenv('DATABASE_URL')
            
            if database_url:
                # PostgreSQL schema - Users table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        oauth_provider TEXT,
                        oauth_id TEXT,
                        profile_picture TEXT
                    )
                ''')
                
                # User preferences table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        dietary_restrictions TEXT, -- JSON array
                        allergies TEXT, -- JSON array  
                        caloric_needs INTEGER,
                        nutritional_goals TEXT, -- JSON object
                        preferred_cuisines TEXT, -- JSON array
                        cooking_skill_level TEXT DEFAULT 'beginner',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                # User pantry table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_pantry (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        ingredient_name TEXT NOT NULL,
                        quantity REAL,
                        unit TEXT,
                        expiry_date DATE,
                        category TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                # Saved recipes table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS saved_recipes (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        recipe_id INTEGER,
                        recipe_data TEXT, -- JSON for external recipes
                        recipe_source TEXT, -- 'internal' or URL
                        saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        tags TEXT, -- JSON array for user tags
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                # Saved meal plans table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS saved_meal_plans (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        plan_name TEXT NOT NULL,
                        plan_data TEXT NOT NULL, -- JSON meal plan
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
            else:
                # SQLite schema for local development
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE,
                        oauth_provider TEXT,
                        oauth_id TEXT,
                        profile_picture TEXT
                    )
                ''')
                
                # User preferences table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        dietary_restrictions TEXT, -- JSON array
                        allergies TEXT, -- JSON array  
                        caloric_needs INTEGER,
                        nutritional_goals TEXT, -- JSON object
                        preferred_cuisines TEXT, -- JSON array
                        cooking_skill_level TEXT DEFAULT 'beginner',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                # User pantry table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_pantry (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        ingredient_name TEXT NOT NULL,
                        quantity REAL,
                        unit TEXT,
                        expiry_date DATE,
                        category TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                # Saved recipes table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS saved_recipes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        recipe_id INTEGER,
                        recipe_data TEXT, -- JSON for external recipes
                        recipe_source TEXT, -- 'internal' or URL
                        saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        tags TEXT, -- JSON array for user tags
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                # Saved meal plans table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS saved_meal_plans (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        plan_name TEXT NOT NULL,
                        plan_data TEXT NOT NULL, -- JSON meal plan
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
            
            conn.commit()
            conn.close()
            logger.info("[OK] User database tables created successfully")
            
        except Exception as e:
            logger.error(f"[ERROR] Error creating user tables: {e}")
            raise
    
    def register_user(self, name, email, password, oauth_provider=None, oauth_id=None):
        """Register a new user"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Check if we're using PostgreSQL or SQLite
            database_url = os.getenv('DATABASE_URL')
            placeholder = '%s' if database_url else '?'
            
            # Check if user already exists
            cursor.execute(f'SELECT id FROM users WHERE email = {placeholder}', (email,))
            if cursor.fetchone():
                return {'success': False, 'message': 'User already exists'}
            
            # Hash password if provided
            password_hash = None
            if password:
                password_hash = self.bcrypt.generate_password_hash(password).decode('utf-8')
            
            # Insert new user with proper ID retrieval for PostgreSQL vs SQLite
            if database_url:
                # PostgreSQL - use RETURNING clause
                cursor.execute(f'''
                    INSERT INTO users (name, email, password_hash, oauth_provider, oauth_id)
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                    RETURNING id
                ''', (name, email, password_hash, oauth_provider, oauth_id))
                user_id = cursor.fetchone()[0]
            else:
                # SQLite - use lastrowid
                cursor.execute(f'''
                    INSERT INTO users (name, email, password_hash, oauth_provider, oauth_id)
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                ''', (name, email, password_hash, oauth_provider, oauth_id))
                user_id = cursor.lastrowid
            
            # Create default preferences
            cursor.execute(f'''
                INSERT INTO user_preferences (user_id, dietary_restrictions, allergies, 
                                            preferred_cuisines, cooking_skill_level)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            ''', (user_id, '[]', '[]', '[]', 'beginner'))
            
            conn.commit()
            conn.close()
            
            # Generate JWT token
            access_token = create_access_token(identity=user_id)
            
            logger.info(f"[OK] User registered successfully: {email}")
            return {
                'success': True,
                'message': 'User registered successfully',
                'access_token': access_token,
                'user': {
                    'id': user_id,
                    'name': name,
                    'email': email
                }
            }
            
        except Exception as e:
            logger.error(f"[ERROR] Registration error: {e}")
            return {'success': False, 'message': 'Registration failed'}
    
    def authenticate_user(self, email, password):
        """Authenticate user with email and password"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Check if we're using PostgreSQL or SQLite
            database_url = os.getenv('DATABASE_URL')
            placeholder = '%s' if database_url else '?'
            
            cursor.execute(f'''
                SELECT id, name, email, password_hash, is_active 
                FROM users WHERE email = {placeholder}
            ''', (email,))
            
            user = cursor.fetchone()
            conn.close()
            
            if not user:
                return {'success': False, 'message': 'Invalid credentials'}
            
            if not user['is_active']:
                return {'success': False, 'message': 'Account disabled'}
            
            if not user['password_hash']:
                return {'success': False, 'message': 'Please use social login'}
            
            # Check password
            if self.bcrypt.check_password_hash(user['password_hash'], password):
                access_token = create_access_token(identity=user['id'])
                
                logger.info(f"[OK] User authenticated: {email}")
                return {
                    'success': True,
                    'access_token': access_token,
                    'user': {
                        'id': user['id'],
                        'name': user['name'],
                        'email': user['email']
                    }
                }
            else:
                return {'success': False, 'message': 'Invalid credentials'}
                
        except Exception as e:
            logger.error(f"[ERROR] Authentication error: {e}")
            return {'success': False, 'message': 'Authentication failed'}
    
    def get_user_by_id(self, user_id):
        """Get user information by ID"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Check if we're using PostgreSQL or SQLite
            database_url = os.getenv('DATABASE_URL')
            placeholder = '%s' if database_url else '?'
            
            cursor.execute(f'''
                SELECT id, name, email, created_at, profile_picture
                FROM users WHERE id = {placeholder} AND is_active = TRUE
            ''', (user_id,))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return dict(user)
            return None
            
        except Exception as e:
            logger.error(f"[ERROR] Error getting user: {e}")
            return None
    
    def wipe_user_data(self, user_id=None):
        """Wipe user data for testing purposes"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # Check if we're using PostgreSQL or SQLite
            database_url = os.getenv('DATABASE_URL')
            placeholder = '%s' if database_url else '?'
            
            if user_id:
                # Wipe specific user
                tables = ['saved_meal_plans', 'saved_recipes', 'user_pantry', 
                         'user_preferences', 'users']
                for table in tables:
                    cursor.execute(f'DELETE FROM {table} WHERE user_id = {placeholder}', (user_id,))
                    if table == 'users':
                        cursor.execute(f'DELETE FROM {table} WHERE id = {placeholder}', (user_id,))
            else:
                # Wipe all user data
                tables = ['saved_meal_plans', 'saved_recipes', 'user_pantry', 
                         'user_preferences', 'users']
                for table in tables:
                    cursor.execute(f'DELETE FROM {table}')
            
            conn.commit()
            conn.close()
            
            logger.info(f"[OK] User data wiped {'for user ' + str(user_id) if user_id else 'completely'}")
            return {'success': True, 'message': 'User data wiped successfully'}
            
        except Exception as e:
            logger.error(f"[ERROR] Error wiping user data: {e}")
            return {'success': False, 'message': 'Failed to wipe user data'}
            return {'success': False, 'message': 'Failed to wipe user data'}
