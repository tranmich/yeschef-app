"""
Configuration management for YesChef application
Centralizes all settings and environment variables
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class"""
    
    # Flask Settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', '')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', '')
    
    # Google Cloud (for OCR)
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
    
    # Groq API
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    
    # Caching (Redis) - We'll set this up in Phase 6
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')  # 'simple' or 'redis'
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
    
    # Feature Flags (for shadow implementation)
    USE_V2_RECIPES = os.getenv('USE_V2_RECIPES', 'false').lower() == 'true'
    USE_V2_PROFILE = os.getenv('USE_V2_PROFILE', 'false').lower() == 'true'
    USE_V2_MEAL_PLANS = os.getenv('USE_V2_MEAL_PLANS', 'false').lower() == 'true'
    V2_ROLLOUT_PERCENTAGE = int(os.getenv('V2_ROLLOUT_PERCENTAGE', '0'))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present"""
        required = ['DATABASE_URL']
        missing = [key for key in required if not getattr(cls, key)]
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        return True
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert configuration to dictionary (for debugging)"""
        return {
            key: '***' if 'SECRET' in key or 'KEY' in key else getattr(cls, key)
            for key in dir(cls)
            if not key.startswith('_') and key.isupper()
        }


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    
    # More verbose logging in development
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = False
    TESTING = True
    
    # Use in-memory database for tests (or test database)
    DATABASE_URL = os.getenv('TEST_DATABASE_URL', Config.DATABASE_URL)
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    
    # Disable CSRF in tests
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Stricter settings for production
    LOG_LEVEL = 'INFO'
    
    @classmethod
    def validate(cls) -> bool:
        """Additional validation for production"""
        super().validate()
        
        # Ensure production uses strong secret key
        if cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            raise ValueError("Production must use a secure SECRET_KEY!")
        
        return True


# Configuration dictionary
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name: str = None) -> Config:
    """
    Get configuration object by name
    
    Args:
        config_name: Name of configuration ('development', 'testing', 'production')
                    If None, uses FLASK_ENV environment variable
    
    Returns:
        Configuration object
    """
    if config_name is None:
        # Determine from environment
        flask_env = os.getenv('FLASK_ENV', 'development')
        # Railway sets RAILWAY_ENVIRONMENT
        if os.getenv('RAILWAY_ENVIRONMENT') == 'production':
            config_name = 'production'
        else:
            config_name = flask_env
    
    config_class = config_by_name.get(config_name, DevelopmentConfig)
    
    # Validate configuration
    config_class.validate()
    
    return config_class


# Convenience function to check if running in production
def is_production() -> bool:
    """Check if running in production environment"""
    return (
        os.getenv('RAILWAY_ENVIRONMENT') == 'production' or
        os.getenv('FLASK_ENV') == 'production'
    )


# Convenience function to check if running in development
def is_development() -> bool:
    """Check if running in development environment"""
    return not is_production() and not os.getenv('TESTING')


if __name__ == '__main__':
    # Test configuration loading
    print("Testing configuration loading...")
    print(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    
    config = get_config()
    print(f"\nLoaded configuration: {config.__name__}")
    print(f"Debug mode: {config.DEBUG}")
    print(f"Database URL: {'***' if config.DATABASE_URL else 'Not set'}")
    print(f"Configuration valid: ✅")
    
    print("\nConfiguration keys:")
    for key, value in config.to_dict().items():
        print(f"  {key}: {value}")
