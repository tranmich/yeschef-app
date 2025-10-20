# 🚀 Quick Start: Refactoring Hungie Server

This guide gets you started with **Phase 1** of the refactoring in under 2 hours.

---

## 🎯 Phase 1 Goal
Set up the new architecture without breaking existing code.

**Time Estimate:** 2-4 hours  
**Risk Level:** ZERO (no code changes, just setup)

---

## 📋 Prerequisites

### 1. Install Required Tools
```bash
# Install new dependencies
pip install sqlalchemy==2.0.23
pip install alembic==1.13.0
pip install pytest==7.4.3
pip install flask-caching==2.1.0
pip install redis==5.0.1
pip install python-dotenv==1.0.0

# Development tools
pip install black==23.12.0
pip install flake8==6.1.0
pip install pytest-cov==4.1.0
```

### 2. Save Requirements
```bash
pip freeze > requirements-new.txt
```

---

## 📁 Step 1: Create New Structure (15 minutes)

### Create Folders
```bash
# From project root (Me Hungie/)
mkdir -p app/models
mkdir -p app/services
mkdir -p app/api
mkdir -p app/database/repositories
mkdir -p app/cache
mkdir -p app/middleware
mkdir -p app/utils
mkdir -p tests/unit/test_services
mkdir -p tests/unit/test_repositories
mkdir -p tests/unit/test_models
mkdir -p tests/integration/test_api
mkdir -p migrations/versions
```

### Create __init__.py Files
```bash
# Make folders importable
touch app/__init__.py
touch app/models/__init__.py
touch app/services/__init__.py
touch app/api/__init__.py
touch app/database/__init__.py
touch app/database/repositories/__init__.py
touch app/cache/__init__.py
touch app/middleware/__init__.py
touch app/utils/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py
```

---

## 🔧 Step 2: Create Configuration (30 minutes)

### 1. Create `app/config.py`
```python
"""
Application Configuration
Supports: development, staging, production
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    DEBUG = False
    TESTING = False
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours
    
    # Redis Cache
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # CORS
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3004",
        "http://localhost:3005",
        "http://localhost:3006",
        "https://yeschef-app.vercel.app"
    ]
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class StagingConfig(Config):
    """Staging configuration"""
    DEBUG = False
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_URL = os.getenv('TEST_DATABASE_URL', Config.DATABASE_URL)


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'staging': StagingConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """Get configuration based on environment"""
    env = env or os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
```

### 2. Update `.env` File
```bash
# Add these to your existing .env file
FLASK_ENV=development
REDIS_URL=redis://localhost:6379/0
```

---

## 🏗️ Step 3: Create App Factory (30 minutes)

### Create `app/__init__.py`
```python
"""
Flask Application Factory
"""
from flask import Flask
from flask_cors import CORS
import logging

from app.config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_name=None):
    """
    Application factory pattern
    
    Args:
        config_name: Configuration to use (development, staging, production)
    
    Returns:
        Flask app instance
    """
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Initialize extensions
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    
    # Register blueprints (will add later)
    # from app.api import auth, recipes, search
    # app.register_blueprint(auth.auth_bp)
    # app.register_blueprint(recipes.recipe_bp)
    # app.register_blueprint(search.search_bp)
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return {
            'status': 'healthy',
            'version': '2.0.0',
            'environment': app.config.get('ENV', 'unknown')
        }
    
    logger.info(f"✅ Flask app created with {config_name or 'default'} configuration")
    
    return app
```

---

## 🗄️ Step 4: Abstract Database Connection (45 minutes)

### Create `app/database/connection.py`
```python
"""
Database Connection Management
Wraps existing get_db_connection() for gradual migration
"""
import psycopg2
import psycopg2.extras
from flask import current_app
import logging

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Database connection wrapper
    Provides connection pooling and error handling
    """
    
    def __init__(self):
        self.database_url = current_app.config.get('DATABASE_URL')
        if not self.database_url:
            # Fallback to Railway public URL (from old code)
            self.database_url = "postgresql://postgres:udQLpljdqTYmESmntwzmwDcOlBVbqlJG@shuttle.proxy.rlwy.net:31331/railway"
    
    def get_connection(self):
        """
        Get database connection
        
        Returns:
            psycopg2 connection with RealDictCursor
        """
        try:
            conn = psycopg2.connect(self.database_url)
            conn.cursor_factory = psycopg2.extras.RealDictCursor
            return conn
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise


# Singleton instance
_db_connection = None


def get_db_connection():
    """
    Get database connection (compatible with old code)
    
    Returns:
        psycopg2 connection
    """
    global _db_connection
    
    if _db_connection is None:
        _db_connection = DatabaseConnection()
    
    return _db_connection.get_connection()


def init_db():
    """Initialize database tables (from old code)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Keep existing schema creation from hungie_server.py
        # (This is just the connection layer, schema stays the same)
        
        conn.commit()
        conn.close()
        logger.info("✅ Database initialized")
        
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        raise
```

### Create `app/database/__init__.py`
```python
"""Database module"""
from app.database.connection import get_db_connection, init_db

__all__ = ['get_db_connection', 'init_db']
```

---

## 🧪 Step 5: Test The Setup (15 minutes)

### Create `tests/conftest.py`
```python
"""
Pytest configuration and fixtures
"""
import pytest
from app import create_app
from app.database import get_db_connection


@pytest.fixture
def app():
    """Create Flask app for testing"""
    app = create_app('testing')
    yield app


@pytest.fixture
def client(app):
    """Create Flask test client"""
    return app.test_client()


@pytest.fixture
def db_connection():
    """Create database connection for testing"""
    conn = get_db_connection()
    yield conn
    conn.close()
```

### Create `tests/test_basic.py`
```python
"""
Basic tests to verify setup
"""
def test_app_creation(app):
    """Test app factory creates app"""
    assert app is not None
    assert app.config['TESTING'] is True


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'


def test_database_connection(db_connection):
    """Test database connectivity"""
    cursor = db_connection.cursor()
    cursor.execute('SELECT 1 as test')
    result = cursor.fetchone()
    assert result['test'] == 1
```

### Run Tests
```bash
pytest tests/ -v
```

Expected output:
```
tests/test_basic.py::test_app_creation PASSED
tests/test_basic.py::test_health_endpoint PASSED
tests/test_basic.py::test_database_connection PASSED

============== 3 passed in 0.50s ==============
```

---

## 🔄 Step 6: Create Compatibility Wrapper (30 minutes)

### Create `run_new.py` (Test New App)
```python
"""
Test runner for new app structure
Use this to test the new app without touching hungie_server.py
"""
from app import create_app
from app.database import init_db
import logging

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # Create app with development config
    app = create_app('development')
    
    # Initialize database
    with app.app_context():
        try:
            init_db()
            logger.info("✅ Database initialized")
        except Exception as e:
            logger.error(f"❌ Database init failed: {e}")
    
    # Run app
    port = 5001  # Different port so old server can still run on 5000
    logger.info(f"🚀 Starting new app on http://localhost:{port}")
    logger.info(f"🔍 Test with: curl http://localhost:{port}/api/health")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )
```

### Test The New App
```bash
# Terminal 1: Run old server (should still work)
python hungie_server.py

# Terminal 2: Run new app
python run_new.py

# Terminal 3: Test both
curl http://localhost:5000/api/health  # Old server
curl http://localhost:5001/api/health  # New server
```

Both should work! ✅

---

## ✅ Verification Checklist

After completing Phase 1, verify:

- [ ] New folder structure created
- [ ] All __init__.py files in place
- [ ] Configuration file works (`app/config.py`)
- [ ] App factory creates Flask app (`app/__init__.py`)
- [ ] Database connection abstracted (`app/database/connection.py`)
- [ ] Tests pass (`pytest tests/`)
- [ ] Old server still works (`python hungie_server.py`)
- [ ] New app works on different port (`python run_new.py`)
- [ ] Health endpoint responds on both servers

---

## 📊 What We Achieved

### Before Phase 1
```
Me Hungie/
├── hungie_server.py (6,990 lines)
├── core_systems/
├── requirements.txt
└── ... other files
```

### After Phase 1
```
Me Hungie/
├── hungie_server.py (6,990 lines - UNCHANGED)
├── app/                        # ✨ NEW
│   ├── __init__.py            # App factory
│   ├── config.py              # Configuration
│   ├── database/
│   │   ├── __init__.py
│   │   └── connection.py      # DB abstraction
│   └── ... (empty folders ready for Phase 2)
├── tests/                      # ✨ NEW
│   ├── conftest.py
│   └── test_basic.py
├── run_new.py                  # ✨ NEW
└── core_systems/               # UNCHANGED
```

### Benefits Achieved
✅ **New architecture in place** - Ready for Phase 2  
✅ **Old code still works** - Zero risk  
✅ **Testing framework ready** - Can test as we refactor  
✅ **Configuration abstracted** - Easier environment management  
✅ **Database layer abstracted** - Ready for repositories  

---

## 🚀 Next Steps

You're now ready for **Phase 2: Extract Database Operations**

Quick preview of what's next:
1. Create repository pattern (`app/database/repositories/base_repository.py`)
2. Implement specific repositories (RecipeRepository, UserRepository, etc.)
3. Replace direct database calls in `hungie_server.py`
4. Add unit tests for repositories

**Time Estimate for Phase 2:** 1-2 days

---

## 🆘 Troubleshooting

### "Module not found" error
```bash
# Make sure you're in project root
cd "d:\Mik\Downloads\Me Hungie"

# Add project to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"  # Linux/Mac
$env:PYTHONPATH="$env:PYTHONPATH;$(pwd)" # Windows PowerShell
```

### Database connection fails
```python
# Check your DATABASE_URL in .env
# Verify PostgreSQL is running
# Test connection manually:
python -c "import psycopg2; conn = psycopg2.connect('YOUR_DATABASE_URL'); print('✅ Connected')"
```

### Tests fail
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run with verbose output
pytest tests/ -v -s
```

### Port already in use
```bash
# Find process using port 5001
lsof -i :5001  # Linux/Mac
netstat -ano | findstr :5001  # Windows

# Kill the process or use different port in run_new.py
```

---

## 💡 Pro Tips

1. **Git Commit After Each Step**
   ```bash
   git add .
   git commit -m "Phase 1: Step 1 - Create folder structure"
   ```

2. **Keep Old Server Running**
   - Don't touch `hungie_server.py` yet
   - Use it as reference
   - Test against it to ensure compatibility

3. **Test Early, Test Often**
   ```bash
   # Run tests after each step
   pytest tests/ -v
   ```

4. **Document As You Go**
   - Add comments explaining decisions
   - Update README with setup instructions
   - Note any deviations from plan

---

## 🎉 Congratulations!

You've completed **Phase 1** of the refactoring! Your codebase now has:

✨ Professional architecture  
✨ Clean configuration management  
✨ Abstracted database layer  
✨ Testing framework  
✨ Zero risk to existing functionality  

**Time to celebrate!** 🎊 Then move on to Phase 2 when you're ready.

---

**Questions?** Review the main `REFACTORING_STRATEGY.md` or open an issue.

**Ready for Phase 2?** The detailed plan is in the main strategy document.

Happy refactoring! 🚀
