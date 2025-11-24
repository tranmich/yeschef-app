"""
Comprehensive V2 Recipe API Tests
Tests ALL scenarios: success, errors, security, edge cases
This is the IMPROVED testing approach!
"""

import pytest
import json
from datetime import datetime


class TestGetRecipeEndpoint:
    """Tests for GET /api/v2/recipes/<recipe_id>"""
    
    # ========== SUCCESS CASES ==========
    
    def test_get_recipe_success(self, client, sample_user, sample_recipe):
        """Test getting a recipe that exists"""
        response = client.get(
            f'/api/v2/recipes/{sample_recipe["id"]}',
            query_string={'user_id': sample_user['id']}
        )
        
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['id'] == sample_recipe['id']
        assert data['data']['title'] == sample_recipe['title']
        assert 'ingredients' in data['data']
        assert 'instructions' in data['data']
    
    
    def test_get_recipe_with_special_characters(self, client, db_connection, sample_user):
        """Test recipe with Unicode and special characters"""
        # Create recipe with special characters
        cursor = db_connection.cursor()
        cursor.execute("""
            INSERT INTO recipes (user_id, title, category, ingredients, instructions)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            sample_user['id'],
            'Café Crème Brûlée 🍮',
            'dessert',
            json.dumps(['2 cups crème fraîche', '½ cup sugar']),
            json.dumps(['Mix crème', 'Brûlée it'])
        ))
        recipe_id = cursor.fetchone()['id']
        db_connection.commit()
        
        response = client.get(
            f'/api/v2/recipes/{recipe_id}',
            query_string={'user_id': sample_user['id']}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert '🍮' in data['data']['title']
        assert 'Café' in data['data']['title']
        assert '½' in data['data']['ingredients'][1]
    
    
    def test_get_community_shared_recipe(self, client, db_connection, sample_user):
        """Test viewing a community-shared recipe from another user"""
        # Create another user
        cursor = db_connection.cursor()
        cursor.execute("""
            INSERT INTO users (name, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id
        """, ('Other User', 'other@example.com', 'hash123'))
        other_user_id = cursor.fetchone()['id']
        
        # Create community-shared recipe by other user
        cursor.execute("""
            INSERT INTO recipes (user_id, title, category, ingredients, instructions, is_community_shared)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            other_user_id,
            'Shared Community Recipe',
            'dinner',
            json.dumps(['ingredient 1']),
            json.dumps(['step 1']),
            True  # Community shared!
        ))
        recipe_id = cursor.fetchone()['id']
        db_connection.commit()
        
        # Original user should be able to view it
        response = client.get(
            f'/api/v2/recipes/{recipe_id}',
            query_string={'user_id': sample_user['id']}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['title'] == 'Shared Community Recipe'
    
    
    # ========== ERROR CASES ==========
    
    def test_get_recipe_not_found(self, client, sample_user):
        """Test getting a recipe that doesn't exist"""
        response = client.get(
            '/api/v2/recipes/999999',
            query_string={'user_id': sample_user['id']}
        )
        
        assert response.status_code == 404
        
        data = response.get_json()
        assert data['success'] is False
        assert 'not found' in data['error'].lower()
    
    
    def test_get_recipe_unauthorized(self, client, db_connection, sample_user):
        """Test viewing another user's private recipe (should fail)"""
        # Create another user
        cursor = db_connection.cursor()
        cursor.execute("""
            INSERT INTO users (name, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id
        """, ('Other User', 'other@example.com', 'hash123'))
        other_user_id = cursor.fetchone()['id']
        
        # Create PRIVATE recipe by other user
        cursor.execute("""
            INSERT INTO recipes (user_id, title, category, ingredients, instructions, is_community_shared)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            other_user_id,
            'Private Recipe',
            'dinner',
            json.dumps(['secret ingredient']),
            json.dumps(['secret step']),
            False  # NOT shared
        ))
        recipe_id = cursor.fetchone()['id']
        db_connection.commit()
        
        # Original user should NOT be able to view it
        response = client.get(
            f'/api/v2/recipes/{recipe_id}',
            query_string={'user_id': sample_user['id']}
        )
        
        assert response.status_code == 403  # Forbidden
        data = response.get_json()
        assert data['success'] is False
        assert 'not authorized' in data['error'].lower() or 'unauthorized' in data['error'].lower()
    
    
    def test_get_recipe_invalid_id_type(self, client, sample_user):
        """Test with non-numeric recipe ID"""
        response = client.get(
            '/api/v2/recipes/not-a-number',
            query_string={'user_id': sample_user['id']}
        )
        
        # Flask should return 404 for invalid route
        assert response.status_code == 404
    
    
    def test_get_recipe_negative_id(self, client, sample_user):
        """Test with negative recipe ID"""
        response = client.get(
            '/api/v2/recipes/-1',
            query_string={'user_id': sample_user['id']}
        )
        
        assert response.status_code == 404
    
    
    def test_get_recipe_zero_id(self, client, sample_user):
        """Test with zero recipe ID"""
        response = client.get(
            '/api/v2/recipes/0',
            query_string={'user_id': sample_user['id']}
        )
        
        assert response.status_code == 404
    
    
    # ========== SECURITY TESTS ==========
    
    def test_sql_injection_in_recipe_id(self, client, sample_user):
        """Test SQL injection attempt through recipe_id (should be blocked by Flask routing)"""
        # Try various SQL injection patterns
        injection_attempts = [
            "1 OR 1=1",
            "1; DROP TABLE recipes;",
            "1' OR '1'='1",
        ]
        
        for attempt in injection_attempts:
            response = client.get(
                f'/api/v2/recipes/{attempt}',
                query_string={'user_id': sample_user['id']}
            )
            
            # Should either 404 (invalid route) or handle safely
            assert response.status_code in [404, 400, 500]
            
            # Database should still work
            verify = client.get('/api/v2/health')
            assert verify.status_code == 200
    
    
    def test_xss_in_recipe_data(self, client, db_connection, sample_user):
        """Test that XSS in recipe data is handled properly"""
        # Create recipe with XSS attempt
        cursor = db_connection.cursor()
        cursor.execute("""
            INSERT INTO recipes (user_id, title, category, ingredients, instructions)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            sample_user['id'],
            '<script>alert("XSS")</script>',
            'test',
            json.dumps(['<img src=x onerror=alert(1)>']),
            json.dumps(['<script>steal_cookies()</script>'])
        ))
        recipe_id = cursor.fetchone()['id']
        db_connection.commit()
        
        response = client.get(
            f'/api/v2/recipes/{recipe_id}',
            query_string={'user_id': sample_user['id']}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        # XSS should be stored (for now) but need to be escaped in frontend
        # This test documents current behavior - frontend MUST escape!
        # TODO: Add backend escaping for extra security
        assert '<script>' in data['data']['title']  # Currently stored as-is
        
        # Add a note to remind about frontend escaping
        print("\n⚠️  SECURITY NOTE: Frontend must escape HTML in recipe data!")
    
    
    # ========== EDGE CASES ==========
    
    def test_get_recipe_without_user_id(self, client, sample_recipe):
        """Test getting recipe without providing user_id (should still work for public recipes)"""
        response = client.get(f'/api/v2/recipes/{sample_recipe["id"]}')
        
        # Should work if recipe is public/community or return appropriate error
        assert response.status_code in [200, 403]
    
    
    def test_get_recipe_with_invalid_user_id(self, client, sample_recipe):
        """Test with invalid user_id format"""
        response = client.get(
            f'/api/v2/recipes/{sample_recipe["id"]}',
            query_string={'user_id': 'not-a-number'}
        )
        
        # Should handle gracefully (400 or treat as missing user_id)
        assert response.status_code in [200, 400, 403]
    
    
    def test_get_recipe_response_structure(self, client, sample_user, sample_recipe):
        """Test response has all expected fields"""
        response = client.get(
            f'/api/v2/recipes/{sample_recipe["id"]}',
            query_string={'user_id': sample_user['id']}
        )
        
        data = response.get_json()
        
        # Check response structure
        assert 'success' in data
        assert 'data' in data
        
        recipe = data['data']
        required_fields = ['id', 'title', 'category', 'ingredients', 'instructions', 'user_id']
        
        for field in required_fields:
            assert field in recipe, f"Missing required field: {field}"
    
    
    def test_get_recipe_with_null_fields(self, client, db_connection, sample_user):
        """Test recipe with optional null fields"""
        cursor = db_connection.cursor()
        cursor.execute("""
            INSERT INTO recipes (user_id, title, category, ingredients, instructions, description, cuisine_type, cooking_time_minutes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            sample_user['id'],
            'Minimal Recipe',
            'test',
            json.dumps(['ingredient']),
            json.dumps(['instruction']),
            None,  # No description
            None,  # No cuisine type
            None   # No cooking time
        ))
        recipe_id = cursor.fetchone()['id']
        db_connection.commit()
        
        response = client.get(
            f'/api/v2/recipes/{recipe_id}',
            query_string={'user_id': sample_user['id']}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Should handle null fields gracefully
        recipe = data['data']
        assert recipe['description'] is None or recipe.get('description') == ''
        assert recipe.get('cuisine_type') is None or recipe.get('cuisine_type') == ''
    
    
    # ========== PERFORMANCE TESTS ==========
    
    def test_get_recipe_with_large_data(self, client, db_connection, sample_user):
        """Test recipe with large amounts of data"""
        # Create recipe with many ingredients and steps
        large_ingredients = [f'Ingredient {i}' for i in range(100)]
        large_instructions = [f'Step {i}: Do something' for i in range(100)]
        
        cursor = db_connection.cursor()
        cursor.execute("""
            INSERT INTO recipes (user_id, title, category, ingredients, instructions)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            sample_user['id'],
            'Large Recipe',
            'test',
            json.dumps(large_ingredients),
            json.dumps(large_instructions)
        ))
        recipe_id = cursor.fetchone()['id']
        db_connection.commit()
        
        response = client.get(
            f'/api/v2/recipes/{recipe_id}',
            query_string={'user_id': sample_user['id']}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Verify all data came through
        assert len(data['data']['ingredients']) == 100
        assert len(data['data']['instructions']) == 100
    
    
    def test_concurrent_recipe_access(self, client, sample_user, sample_recipe):
        """Test multiple simultaneous requests to same recipe"""
        import concurrent.futures
        
        def get_recipe():
            return client.get(
                f'/api/v2/recipes/{sample_recipe["id"]}',
                query_string={'user_id': sample_user['id']}
            )
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_recipe) for _ in range(10)]
            responses = [f.result() for f in futures]
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True


class TestGetUserRecipesEndpoint:
    """Tests for GET /api/v2/recipes/user/<user_id>"""
    
    def test_get_user_recipes_success(self, client, sample_user):
        """Test getting user's recipe list"""
        response = client.get(f'/api/v2/recipes/user/{sample_user["id"]}')
        
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'items' in data['data']
        assert 'pagination' in data['data']
    
    
    def test_get_user_recipes_pagination(self, client, db_connection, sample_user):
        """Test pagination works correctly"""
        # Create 25 recipes
        cursor = db_connection.cursor()
        for i in range(25):
            cursor.execute("""
                INSERT INTO recipes (user_id, title, category, ingredients, instructions)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                sample_user['id'],
                f'Recipe {i}',
                'test',
                json.dumps(['ingredient']),
                json.dumps(['instruction'])
            ))
        db_connection.commit()
        
        # Get page 1 (20 items per page default)
        response = client.get(
            f'/api/v2/recipes/user/{sample_user["id"]}',
            query_string={'page': 1, 'per_page': 20}
        )
        
        data = response.get_json()
        assert len(data['data']['items']) == 20
        assert data['data']['pagination']['page'] == 1
        assert data['data']['pagination']['has_next'] is True
        assert data['data']['pagination']['has_prev'] is False
        
        # Get page 2
        response = client.get(
            f'/api/v2/recipes/user/{sample_user["id"]}',
            query_string={'page': 2, 'per_page': 20}
        )
        
        data = response.get_json()
        assert len(data['data']['items']) >= 5  # At least 5 more recipes
        assert data['data']['pagination']['page'] == 2
        assert data['data']['pagination']['has_prev'] is True
    
    
    def test_get_user_recipes_by_category(self, client, db_connection, sample_user):
        """Test filtering by category"""
        cursor = db_connection.cursor()
        
        # Create recipes in different categories
        for category in ['breakfast', 'lunch', 'dinner']:
            for i in range(3):
                cursor.execute("""
                    INSERT INTO recipes (user_id, title, category, ingredients, instructions)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    sample_user['id'],
                    f'{category} Recipe {i}',
                    category,
                    json.dumps(['ingredient']),
                    json.dumps(['instruction'])
                ))
        db_connection.commit()
        
        # Get only breakfast recipes
        response = client.get(
            f'/api/v2/recipes/user/{sample_user["id"]}',
            query_string={'category': 'breakfast'}
        )
        
        data = response.get_json()
        breakfast_recipes = data['data']['items']
        
        # All should be breakfast
        for recipe in breakfast_recipes:
            assert recipe['category'] == 'breakfast'
    
    
    def test_get_user_recipes_empty_list(self, client, db_connection):
        """Test user with no recipes"""
        # Create user with no recipes
        cursor = db_connection.cursor()
        cursor.execute("""
            INSERT INTO users (name, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id
        """, ('Empty User', 'empty@example.com', 'hash'))
        user_id = cursor.fetchone()['id']
        db_connection.commit()
        
        response = client.get(f'/api/v2/recipes/user/{user_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']['items']) == 0
        assert data['data']['pagination']['total'] == 0


# Run with: pytest tests/integration/test_v2_recipes_comprehensive.py -v
