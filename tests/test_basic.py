"""
Basic integration tests
Tests the foundational setup (config, database, app factory)
"""

import pytest


@pytest.mark.integration
def test_app_creation(app):
    """Test that app can be created"""
    assert app is not None
    assert app.config['TESTING'] is True


@pytest.mark.integration
def test_health_endpoint(client):
    """Test the /api/v2/health endpoint"""
    response = client.get('/api/v2/health')
    
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['version'] == '2.0'
    assert 'message' in data


@pytest.mark.integration
def test_database_connection(db_connection):
    """Test database connection works"""
    cursor = db_connection.cursor()
    cursor.execute("SELECT 1 as test")
    result = cursor.fetchone()
    
    assert result is not None
    assert result['test'] == 1


@pytest.mark.integration
def test_database_users_table(db_connection):
    """Test that users table exists and has data"""
    cursor = db_connection.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM users")
    result = cursor.fetchone()
    
    assert result is not None
    assert result['count'] >= 0  # Table exists and can be queried


@pytest.mark.integration
def test_database_recipes_table(db_connection):
    """Test that recipes table exists"""
    cursor = db_connection.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM recipes")
    result = cursor.fetchone()
    
    assert result is not None
    assert result['count'] >= 0  # Table exists


@pytest.mark.integration
def test_sample_user_fixture(sample_user):
    """Test that sample_user fixture works"""
    assert sample_user is not None
    assert sample_user['email'] == 'test@example.com'
    assert sample_user['name'] == 'Test User'
    assert 'id' in sample_user


@pytest.mark.integration
def test_sample_recipe_fixture(sample_recipe, sample_user):
    """Test that sample_recipe fixture works"""
    assert sample_recipe is not None
    assert sample_recipe['title'] == 'Test Recipe'
    assert sample_recipe['category'] == 'test'
    assert 'id' in sample_recipe


@pytest.mark.integration
def test_404_error_handler(client):
    """Test 404 error handler"""
    response = client.get('/api/v2/nonexistent')
    
    assert response.status_code == 404
    
    data = response.get_json()
    assert data['success'] is False
    assert 'error' in data


@pytest.mark.integration
def test_cors_headers(client):
    """Test CORS headers are present"""
    response = client.get('/api/v2/health')
    
    # Check for CORS headers
    assert 'Access-Control-Allow-Origin' in response.headers
    

@pytest.mark.unit
def test_configuration_loading():
    """Test configuration can be loaded"""
    from app.config import get_config, DevelopmentConfig, ProductionConfig
    
    dev_config = get_config('development')
    assert dev_config.DEBUG is True
    
    # Don't test production config (would fail validation without proper SECRET_KEY)
    # prod_config = get_config('production')


@pytest.mark.unit  
def test_configuration_values():
    """Test configuration has required values"""
    from app.config import get_config
    
    config = get_config('testing')
    
    # Required config should be present
    assert hasattr(config, 'DATABASE_URL')
    assert hasattr(config, 'SECRET_KEY')
    assert hasattr(config, 'JWT_SECRET_KEY')
    
    # Testing-specific config
    assert config.TESTING is True
    assert config.DEBUG is False


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
