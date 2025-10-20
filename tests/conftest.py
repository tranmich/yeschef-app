"""
PyTest Configuration
Shared fixtures and setup for all tests
"""

import pytest
from app import create_app
from app.database.connection import get_db_connection, return_db_connection


@pytest.fixture(scope='session')
def app():
    """
    Create application for testing
    Scope: session (created once for all tests)
    """
    test_app = create_app('testing')
    yield test_app


@pytest.fixture(scope='session')
def client(app):
    """
    Create test client
    Scope: session (one client for all tests)
    """
    return app.test_client()


@pytest.fixture(scope='function')
def db_connection():
    """
    Provide database connection for tests
    Scope: function (new connection for each test)
    """
    conn = get_db_connection()
    yield conn
    return_db_connection(conn)


@pytest.fixture(scope='function')
def sample_user(db_connection):
    """
    Create a sample user for testing
    Automatically cleaned up after test
    """
    cursor = db_connection.cursor()
    
    # Create test user
    cursor.execute("""
        INSERT INTO users (email, name, password_hash)
        VALUES ('test@example.com', 'Test User', 'hashed_password')
        RETURNING id, email, name
    """)
    user = cursor.fetchone()
    db_connection.commit()
    
    yield user
    
    # Cleanup: delete test user
    cursor.execute("DELETE FROM users WHERE id = %s", (user['id'],))
    db_connection.commit()


@pytest.fixture(scope='function')
def auth_headers(sample_user):
    """
    Provide authentication headers for API tests
    Requires JWT implementation (Phase 2)
    """
    # For now, just return empty dict
    # In Phase 2, we'll generate actual JWT tokens
    return {}


@pytest.fixture(scope='function')
def sample_recipe(db_connection, sample_user):
    """
    Create a sample recipe for testing
    Automatically cleaned up after test
    """
    cursor = db_connection.cursor()
    
    # Create test recipe
    cursor.execute("""
        INSERT INTO recipes (user_id, title, ingredients, instructions, category)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, title, category
    """, (
        sample_user['id'],
        'Test Recipe',
        '["ingredient 1", "ingredient 2"]',
        '["step 1", "step 2"]',
        'test'
    ))
    recipe = cursor.fetchone()
    db_connection.commit()
    
    yield recipe
    
    # Cleanup: delete test recipe
    cursor.execute("DELETE FROM recipes WHERE id = %s", (recipe['id'],))
    db_connection.commit()


# Test markers for organizing tests
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, no database)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (with database)"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )


# Hook to print test info
def pytest_runtest_setup(item):
    """Print test name before running"""
    print(f"\n🧪 Running: {item.name}")
