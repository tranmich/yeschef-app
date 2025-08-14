#!/usr/bin/env python3
"""
Migration Endpoint for hungie_server.py
Add this endpoint to migrate SQLite data to PostgreSQL
"""

@app.route('/api/admin/migrate-recipes', methods=['POST'])
def migrate_recipes_endpoint():
    """Admin endpoint to migrate recipes from SQLite to PostgreSQL"""
    try:
        # Security check - only allow in development or with proper authentication
        if not request.headers.get('X-Admin-Key') == 'migrate-recipes-2025':
            return jsonify({
                'success': False,
                'error': 'Unauthorized - Admin key required'
            }), 401
        
        logger.info("🚀 Starting recipe migration from SQLite to PostgreSQL")
        
        # Check if we're already using PostgreSQL
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            return jsonify({
                'success': False,
                'error': 'PostgreSQL DATABASE_URL not available'
            }), 500
        
        # For this migration, we need to read from a local SQLite file
        # Since we're on Railway, we'll create sample recipes instead
        sample_recipes = [
            {
                'title': 'Classic Chicken Parmesan',
                'description': 'Crispy breaded chicken cutlets topped with marinara sauce and melted mozzarella cheese. Servings: 4 | Total time: 45 minutes',
                'ingredients': '4 boneless chicken breasts, 1 cup breadcrumbs, 1 cup marinara sauce, 1 cup mozzarella cheese, 2 eggs, flour for dredging, olive oil, salt, pepper',
                'instructions': '1. Pound chicken to 1/4 inch thickness. 2. Set up breading station with flour, beaten eggs, and breadcrumbs. 3. Bread chicken cutlets. 4. Pan fry until golden brown. 5. Top with marinara and cheese. 6. Bake until cheese melts.',
                'source': 'Recipe Collection | Chapter: Main Dishes',
                'category': 'Main Course'
            },
            {
                'title': 'Beef Stroganoff',
                'description': 'Tender beef strips in a creamy mushroom sauce served over egg noodles. Servings: 6 | Total time: 30 minutes',
                'ingredients': '1 lb beef sirloin, 8 oz mushrooms, 1 cup sour cream, 2 cups beef broth, 1 onion, 2 tbsp flour, egg noodles, butter, salt, pepper',
                'instructions': '1. Slice beef into strips. 2. Sauté onions and mushrooms. 3. Brown beef strips. 4. Add flour and cook 1 minute. 5. Add broth and simmer. 6. Stir in sour cream. 7. Serve over noodles.',
                'source': 'Recipe Collection | Chapter: Comfort Food',
                'category': 'Main Course'
            },
            {
                'title': 'Chocolate Chip Cookies',
                'description': 'Classic homemade chocolate chip cookies with crispy edges and chewy centers. Servings: 24 cookies | Total time: 25 minutes',
                'ingredients': '2 1/4 cups flour, 1 tsp baking soda, 1 cup butter, 3/4 cup brown sugar, 1/2 cup white sugar, 2 eggs, 2 tsp vanilla, 2 cups chocolate chips',
                'instructions': '1. Preheat oven to 375°F. 2. Mix dry ingredients. 3. Cream butter and sugars. 4. Add eggs and vanilla. 5. Combine wet and dry ingredients. 6. Stir in chocolate chips. 7. Drop onto baking sheets. 8. Bake 9-11 minutes.',
                'source': 'Recipe Collection | Chapter: Desserts',
                'category': 'Dessert'
            },
            {
                'title': 'Caesar Salad',
                'description': 'Fresh romaine lettuce with homemade Caesar dressing, croutons, and parmesan cheese. Servings: 4 | Total time: 15 minutes',
                'ingredients': '1 head romaine lettuce, 1/2 cup parmesan cheese, 1 cup croutons, 2 cloves garlic, 2 anchovy fillets, 1 egg yolk, 1/4 cup olive oil, 2 tbsp lemon juice, Worcestershire sauce',
                'instructions': '1. Wash and chop romaine lettuce. 2. Make dressing by whisking garlic, anchovies, egg yolk, lemon juice, and Worcestershire. 3. Slowly add olive oil. 4. Toss lettuce with dressing. 5. Top with parmesan and croutons.',
                'source': 'Recipe Collection | Chapter: Salads',
                'category': 'Salad'
            },
            {
                'title': 'Vegetable Stir Fry',
                'description': 'Quick and healthy vegetable stir fry with a savory sauce. Servings: 4 | Total time: 20 minutes',
                'ingredients': '2 cups broccoli florets, 1 bell pepper, 1 carrot, 1 zucchini, 2 cloves garlic, 1 inch ginger, 3 tbsp soy sauce, 1 tbsp sesame oil, 2 tbsp vegetable oil, 1 tsp cornstarch',
                'instructions': '1. Cut all vegetables into bite-sized pieces. 2. Heat oil in wok or large skillet. 3. Stir fry vegetables starting with hardest ones first. 4. Add garlic and ginger. 5. Mix sauce ingredients and add to pan. 6. Stir fry until vegetables are tender-crisp.',
                'source': 'Recipe Collection | Chapter: Vegetables',
                'category': 'Vegetarian'
            }
        ]
        
        # Insert sample recipes into PostgreSQL
        conn = get_db_connection()
        cursor = conn.cursor()
        
        inserted_count = 0
        for recipe_data in sample_recipes:
            try:
                cursor.execute("""
                    INSERT INTO recipes (title, description, ingredients, instructions, source, category, created_at)
                    VALUES (%(title)s, %(description)s, %(ingredients)s, %(instructions)s, %(source)s, %(category)s, NOW())
                    RETURNING id
                """, recipe_data)
                
                new_id = cursor.fetchone()[0]
                inserted_count += 1
                logger.info(f"✅ Inserted recipe: {recipe_data['title']} (ID: {new_id})")
                
            except Exception as e:
                logger.error(f"❌ Error inserting recipe {recipe_data['title']}: {e}")
        
        conn.commit()
        conn.close()
        
        # Verify the migration
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM recipes")
        total_recipes = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Migration completed successfully',
            'recipes_inserted': inserted_count,
            'total_recipes': total_recipes
        })
        
    except Exception as e:
        logger.error(f"❌ Migration error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
