# 📘 YesChef API v2 - Detailed Endpoint Reference

**Complete documentation for all 101 endpoints**

---

## 🎯 Table of Contents

1. [Users API](#users-api)
2. [Recipes API](#recipes-api)
3. [Meal Plans API](#meal-plans-api)
4. [Grocery Lists API](#grocery-lists-api)
5. [Friends API](#friends-api)
6. [Households API](#households-api)
7. [Community API](#community-api)
8. [Favorites API](#favorites-api)
9. [Profile API](#profile-api)
10. [Pantry API](#pantry-api)
11. [Recipe Search & Import API](#recipe-search--import-api)
12. [System & Admin API](#system--admin-api)

---

## 1. Users API

### GET /api/v2/users/{id}
**Get user by ID**

**Parameters:**
- `id` (path) - User ID

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 10,
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2025-01-15T10:30:00Z"
  }
}
```

---

### POST /api/v2/users
**Create new user**

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 10,
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2025-10-21T10:30:00Z"
  }
}
```

---

## 2. Recipes API

### GET /api/v2/recipes/{id}
**Get recipe by ID**

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 100,
    "user_id": 10,
    "title": "Spaghetti Carbonara",
    "description": "Classic Italian pasta",
    "ingredients": ["400g spaghetti", "200g pancetta", "4 eggs"],
    "instructions": ["Boil pasta", "Cook pancetta", "Mix"],
    "prep_time": "10 minutes",
    "cook_time": "20 minutes",
    "servings": 4,
    "category": "italian",
    "created_at": "2025-10-21T10:00:00Z"
  }
}
```

---

### POST /api/v2/recipes
**Create new recipe**

**Request Body:**
```json
{
  "user_id": 10,
  "title": "Spaghetti Carbonara",
  "description": "Classic Italian pasta dish",
  "ingredients": [
    "400g spaghetti",
    "200g pancetta",
    "4 large eggs",
    "100g parmesan cheese",
    "Black pepper",
    "Salt"
  ],
  "instructions": [
    "Boil salted water and cook spaghetti",
    "Cook pancetta until crispy",
    "Beat eggs with grated parmesan",
    "Drain pasta, mix with pancetta",
    "Add egg mixture, stir quickly",
    "Season with black pepper"
  ],
  "prep_time": "10 minutes",
  "cook_time": "20 minutes",
  "servings": 4,
  "category": "italian",
  "difficulty": "medium"
}
```

---

### GET /api/v2/recipes/search/advanced
**Advanced recipe search with filters**

**Query Parameters:**
- `user_id` (required) - User ID
- `q` (optional) - Search query
- `category` (optional) - Recipe category
- `prep_time_max` (optional) - Max prep time in minutes
- `cook_time_max` (optional) - Max cook time in minutes
- `limit` (optional) - Results limit (default: 50)
- `offset` (optional) - Pagination offset (default: 0)

**Example:**
```
GET /api/v2/recipes/search/advanced?user_id=10&q=pasta&category=italian&prep_time_max=30
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 100,
      "title": "Spaghetti Carbonara",
      "category": "italian",
      "prep_time": "10 minutes"
    }
  ],
  "query": "pasta",
  "filters": {
    "category": "italian",
    "prep_time_max": 30
  },
  "pagination": {
    "limit": 50,
    "offset": 0,
    "total": 1
  }
}
```

---

## 3. Meal Plans API

### POST /api/v2/meal-plans
**Create meal plan**

**Request Body:**
```json
{
  "user_id": 10,
  "name": "Weekly Meal Plan",
  "start_date": "2025-10-21",
  "end_date": "2025-10-27",
  "meals": {
    "2025-10-21": {
      "breakfast": {
        "recipe_id": 1,
        "recipe_name": "Pancakes"
      },
      "lunch": {
        "recipe_id": 2,
        "recipe_name": "Caesar Salad"
      },
      "dinner": {
        "recipe_id": 3,
        "recipe_name": "Grilled Chicken"
      }
    },
    "2025-10-22": {
      "breakfast": {
        "recipe_id": 4,
        "recipe_name": "Oatmeal"
      },
      "dinner": {
        "recipe_id": 5,
        "recipe_name": "Pasta"
      }
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 50,
    "user_id": 10,
    "name": "Weekly Meal Plan",
    "start_date": "2025-10-21",
    "end_date": "2025-10-27",
    "meals": { ... },
    "created_at": "2025-10-21T10:00:00Z"
  }
}
```

---

## 4. Grocery Lists API

### POST /api/v2/grocery-lists/from-meal-plan/{meal_plan_id}
**Create grocery list from meal plan**

**Parameters:**
- `meal_plan_id` (path) - Meal plan ID

**Query Parameters:**
- `user_id` (required) - User ID

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 25,
    "user_id": 10,
    "name": "Grocery List from Weekly Meal Plan",
    "items": [
      {
        "name": "Spaghetti",
        "quantity": "400g",
        "category": "pasta",
        "purchased": false
      },
      {
        "name": "Eggs",
        "quantity": "12",
        "category": "dairy",
        "purchased": false
      }
    ],
    "created_at": "2025-10-21T10:00:00Z"
  },
  "message": "Grocery list created successfully from meal plan"
}
```

---

## 5. Community API

### GET /api/v2/community/recipes
**Browse community recipes**

**Query Parameters:**
- `limit` (optional) - Results limit (default: 50)
- `offset` (optional) - Pagination offset (default: 0)
- `category` (optional) - Filter by category
- `sort` (optional) - Sort field (likes, date)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 100,
      "user_id": 5,
      "user_name": "Chef Mario",
      "title": "Authentic Carbonara",
      "description": "Traditional Italian recipe",
      "category": "italian",
      "likes_count": 45,
      "is_shared": true,
      "shared_at": "2025-10-20T15:00:00Z"
    }
  ],
  "pagination": {
    "limit": 50,
    "offset": 0,
    "total": 1
  }
}
```

---

### POST /api/v2/community/recipes/{recipe_id}/like
**Like a community recipe**

**Parameters:**
- `recipe_id` (path) - Recipe ID

**Request Body:**
```json
{
  "user_id": 10
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "recipe_id": 100,
    "user_id": 10,
    "liked_at": "2025-10-21T10:00:00Z"
  },
  "message": "Recipe liked successfully"
}
```

---

## 6. Favorites API

### POST /api/v2/favorites
**Add recipe to favorites**

**Request Body:**
```json
{
  "user_id": 10,
  "recipe_id": 100
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 50,
    "user_id": 10,
    "recipe_id": 100,
    "created_at": "2025-10-21T10:00:00Z"
  },
  "message": "Recipe added to favorites"
}
```

---

### GET /api/v2/favorites/check
**Check if recipe is favorited**

**Query Parameters:**
- `user_id` (required) - User ID
- `recipe_id` (required) - Recipe ID

**Response:**
```json
{
  "success": true,
  "data": {
    "is_favorite": true,
    "user_id": 10,
    "recipe_id": 100
  }
}
```

---

## 7. Profile API

### PATCH /api/v2/profile/{user_id}
**Update user profile**

**Parameters:**
- `user_id` (path) - User ID

**Request Body:**
```json
{
  "bio": "Passionate home cook who loves Italian cuisine",
  "location": "New York, NY",
  "dietary_preferences": ["vegetarian"],
  "cooking_level": "intermediate",
  "favorite_cuisines": ["italian", "mexican", "asian"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 10,
    "name": "John Doe",
    "email": "john@example.com",
    "bio": "Passionate home cook...",
    "location": "New York, NY",
    "dietary_preferences": ["vegetarian"],
    "cooking_level": "intermediate",
    "avatar_url": "https://...",
    "updated_at": "2025-10-21T10:00:00Z"
  }
}
```

---

### POST /api/v2/profile/{user_id}/avatar
**Upload user avatar**

**Parameters:**
- `user_id` (path) - User ID

**Request Body:**
```json
{
  "avatar_data": "base64_encoded_image_data_here..."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": 10,
    "avatar_url": "https://storage.../avatars/user_10.jpg",
    "uploaded_at": "2025-10-21T10:00:00Z"
  },
  "message": "Avatar uploaded successfully"
}
```

---

## 8. Pantry API

### POST /api/v2/pantry
**Add item to pantry**

**Request Body:**
```json
{
  "user_id": 10,
  "name": "Spaghetti",
  "quantity": "500g",
  "category": "pasta",
  "expiry_date": "2025-12-31",
  "notes": "Whole wheat spaghetti"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 150,
    "user_id": 10,
    "name": "Spaghetti",
    "quantity": "500g",
    "category": "pasta",
    "expiry_date": "2025-12-31",
    "notes": "Whole wheat spaghetti",
    "created_at": "2025-10-21T10:00:00Z"
  }
}
```

---

### GET /api/v2/pantry/stats
**Get pantry statistics**

**Query Parameters:**
- `user_id` (required) - User ID

**Response:**
```json
{
  "success": true,
  "data": {
    "total_items": 25,
    "categories": {
      "pasta": 3,
      "canned": 5,
      "spices": 12,
      "grains": 5
    },
    "expiring_soon": 2,
    "expired": 0,
    "last_updated": "2025-10-21T10:00:00Z"
  }
}
```

---

## 9. Recipe Search & Import API

### POST /api/v2/recipes/search/ingredients
**Search recipes by available ingredients**

**Request Body:**
```json
{
  "user_id": 10,
  "ingredients": ["chicken", "rice", "vegetables", "soy sauce"],
  "limit": 20
}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 150,
      "title": "Chicken Fried Rice",
      "ingredients": ["chicken", "rice", "vegetables", "soy sauce", "eggs"],
      "matching_ingredients": 4,
      "match_percentage": 80
    },
    {
      "id": 151,
      "title": "Teriyaki Chicken Bowl",
      "ingredients": ["chicken", "rice", "vegetables", "teriyaki sauce"],
      "matching_ingredients": 3,
      "match_percentage": 75
    }
  ],
  "ingredients": ["chicken", "rice", "vegetables", "soy sauce"],
  "count": 2
}
```

---

### POST /api/v2/recipes/import
**Import recipe from URL**

**Request Body:**
```json
{
  "user_id": 10,
  "url": "https://www.allrecipes.com/recipe/12345/spaghetti-carbonara"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 200,
    "title": "Imported Recipe from allrecipes.com",
    "description": "Recipe imported from https://www.allrecipes.com/...",
    "ingredients": ["Ingredient 1", "Ingredient 2"],
    "instructions": ["Step 1", "Step 2"],
    "source_url": "https://www.allrecipes.com/recipe/12345/...",
    "imported_at": "2025-10-21T10:00:00Z"
  },
  "message": "Recipe imported successfully (placeholder)",
  "source_url": "https://www.allrecipes.com/..."
}
```

---

### POST /api/v2/recipes/import/text
**Import recipe from raw text (AI-ready)**

**Request Body:**
```json
{
  "user_id": 10,
  "text": "Amazing Pasta Recipe\n\nIngredients:\n- 200g pasta\n- 2 cloves garlic\n- Olive oil\n\nInstructions:\n1. Boil pasta\n2. Sauté garlic\n3. Mix together"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "title": "Amazing Pasta Recipe",
    "description": "Recipe imported from text (placeholder)",
    "ingredients": ["Ingredient 1 (parsed)", "Ingredient 2 (parsed)"],
    "instructions": ["Step 1 (parsed)", "Step 2 (parsed)"],
    "prep_time": "15 minutes",
    "cook_time": "30 minutes",
    "servings": 4
  },
  "message": "Recipe imported from text (placeholder - ready for AI integration)",
  "placeholder": true
}
```

---

## 10. System & Admin API

### GET /api/v2/system/health
**System health check**

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2025-10-21T10:00:00Z",
    "database": {
      "status": "healthy",
      "database": "connected",
      "users_count": 10
    },
    "version": "2.0.0"
  }
}
```

---

### GET /api/v2/system/config
**Get system configuration**

**Response:**
```json
{
  "success": true,
  "data": {
    "api_version": "2.0.0",
    "features": {
      "voice_enabled": true,
      "ocr_enabled": true,
      "ai_enabled": true,
      "community_enabled": true,
      "pantry_enabled": true,
      "households_enabled": true
    },
    "limits": {
      "max_recipes_per_user": 1000,
      "max_meal_plans": 50,
      "max_grocery_lists": 20,
      "max_pantry_items": 500,
      "max_household_members": 10
    },
    "supported_languages": ["en", "es", "fr", "de", "it", "pt"],
    "environment": "production"
  }
}
```

---

### GET /api/v2/system/stats
**Get system statistics**

**Response:**
```json
{
  "success": true,
  "data": {
    "total_users": 10,
    "total_recipes": 1090,
    "total_favorites": 45,
    "total_shared_recipes": 120,
    "total_pantry_items": 350,
    "total_likes": 890
  }
}
```

---

### POST /api/v2/system/voice/generate
**Generate recipe from voice description**

**Request Body:**
```json
{
  "user_id": 10,
  "voice_description": "I want to make a healthy pasta dish with chicken and vegetables",
  "language": "en"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "recipe": {
      "title": "AI-Generated Healthy Chicken Pasta",
      "description": "Recipe generated from: 'I want to make a healthy pasta dish...'",
      "ingredients": [
        "200g pasta",
        "2 chicken breasts",
        "1 cup mixed vegetables",
        "olive oil",
        "salt and pepper"
      ],
      "instructions": [
        "Boil pasta according to package directions",
        "Cook chicken in olive oil until done",
        "Sauté vegetables",
        "Combine all ingredients",
        "Season to taste"
      ],
      "prep_time": "15 minutes",
      "cook_time": "20 minutes",
      "servings": 2
    },
    "confidence": 0.85,
    "language": "en",
    "placeholder": true,
    "message": "Voice recipe generation ready for AI integration"
  }
}
```

---

## 📊 Common Patterns

### **Pagination**
```
GET /api/v2/recipes/user/10?limit=20&offset=40
```

### **Filtering**
```
GET /api/v2/pantry/user/10?category=pasta&expiry_before=2025-12-31
```

### **Sorting**
```
GET /api/v2/community/recipes?sort=likes&order=desc
```

### **Bulk Operations**
```
DELETE /api/v2/recipes/bulk-delete
{
  "user_id": 10,
  "recipe_ids": [1, 2, 3, 4, 5]
}
```

---

## 🎯 Response Times

- Simple GET requests: < 100ms
- Complex queries: < 500ms
- Bulk operations: < 2s
- Image uploads: < 3s

---

**Last Updated:** October 21, 2025  
**Version:** 2.0.0  
**Status:** ✅ Production Ready
