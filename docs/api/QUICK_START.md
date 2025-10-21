# 🚀 YesChef API v2 - Quick Start Guide

Get up and running with YesChef API v2 in 5 minutes!

---

## 📋 Prerequisites

- Basic knowledge of REST APIs
- A tool to make HTTP requests (curl, Postman, or your favorite HTTP client)
- A YesChef user account (user_id)

---

## 🎯 Step 1: Test the API (30 seconds)

Let's make sure the API is running:

```bash
curl https://yeschefapp-production.up.railway.app/api/v2/health
```

**Expected response:**
```json
{
  "message": "YesChef v2 API is running",
  "status": "healthy",
  "version": "2.0"
}
```

✅ If you see this, the API is working!

---

## 🍳 Step 2: Get Your Recipes (1 minute)

Use the **STAR FEATURE** to get all your recipes with stats in ONE call:

```bash
curl https://yeschefapp-production.up.railway.app/api/v2/recipes/user/11/stats
```

**What you'll get:**
- Your user info
- Complete recipe list (37 recipes!)
- Categories breakdown (Breakfast, Lunch, Dinner, etc.)
- Statistics (total recipes, categories count)
- Pagination info

**Response example:**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 11,
      "name": "YesChef"
    },
    "recipes": [
      {
        "id": 2690,
        "title": "Grilled Chicken",
        "category": "Dinner",
        "ingredients": [...]
      }
    ],
    "categories": [
      {"category": "Breakfast", "count": 12},
      {"category": "Lunch", "count": 8},
      {"category": "Dinner", "count": 15}
    ],
    "stats": {
      "total_recipes": 37,
      "categories_count": 5
    }
  }
}
```

✅ Amazing! You got everything in ONE call!

---

## 🗓️ Step 3: Create a Meal Plan (2 minutes)

Let's create a simple meal plan for the week:

```bash
curl -X POST https://yeschefapp-production.up.railway.app/api/v2/meal-plans \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 11,
    "plan_name": "My First Meal Plan",
    "week_start_date": "2025-10-21",
    "plan_data": {
      "monday": {
        "dinner": {
          "recipe_id": 2690,
          "title": "Grilled Chicken"
        }
      },
      "tuesday": {
        "lunch": {
          "recipe_id": 2690,
          "title": "Grilled Chicken"
        }
      }
    }
  }'
```

**Expected response:**
```json
{
  "success": true,
  "data": {
    "id": 116,
    "user_id": 11,
    "plan_name": "My First Meal Plan",
    "week_start_date": "2025-10-21",
    "plan_data": {...}
  },
  "message": "Meal plan created successfully"
}
```

✅ Great! Note the `id: 116` - you'll need this for the next step!

---

## 🛒 Step 4: Generate Grocery List (1 minute)

Now for the **POWER FEATURE** - automatically generate a complete grocery list from your meal plan!

Replace `116` with your meal plan ID from Step 3:

```bash
curl -X POST "https://yeschefapp-production.up.railway.app/api/v2/grocery-lists/from-meal-plan/116?user_id=11"
```

**What happens:**
1. ✅ Extracts all recipes from your meal plan
2. ✅ Combines all ingredients intelligently
3. ✅ Removes duplicates
4. ✅ Creates a grocery list
5. ✅ Saves it to database

**Expected response:**
```json
{
  "success": true,
  "data": {
    "id": 53,
    "name": "Grocery List - My First Meal Plan",
    "items": [
      {
        "name": "Chicken breast",
        "quantity": "2",
        "unit": "lbs",
        "category": "Meat",
        "purchased": false
      },
      {
        "name": "Olive oil",
        "quantity": "2",
        "unit": "tbsp",
        "category": "Pantry",
        "purchased": false
      }
    ],
    "stats": {
      "total_items": 19,
      "purchased_items": 0,
      "remaining_items": 19,
      "completion_percentage": 0
    }
  },
  "message": "Grocery list created from meal plan with 19 items"
}
```

✅ WOW! You just created a complete shopping list in ONE API call!

---

## ✅ Step 5: Mark Items as Purchased (30 seconds)

As you shop, mark items as purchased. Replace `53` with your grocery list ID from Step 4:

```bash
curl -X POST https://yeschefapp-production.up.railway.app/api/v2/grocery-lists/53/items/0/purchase \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 11,
    "purchased": true
  }'
```

**Expected response:**
```json
{
  "success": true,
  "data": {
    "id": 53,
    "stats": {
      "total_items": 19,
      "purchased_items": 1,
      "remaining_items": 18,
      "completion_percentage": 5.3
    }
  },
  "message": "Item marked as purchased"
}
```

✅ Perfect! Your progress is tracked!

---

## 🎉 Congratulations!

You just:
1. ✅ Checked API health
2. ✅ Got all your recipes with stats in ONE call
3. ✅ Created a meal plan
4. ✅ Generated a complete grocery list in ONE call
5. ✅ Marked items as purchased

**You're now a YesChef API v2 expert!** 🏆

---

## 🎯 What's Next?

### Explore More Features

#### Get a Specific Recipe
```bash
curl "https://yeschefapp-production.up.railway.app/api/v2/recipes/2690?user_id=11"
```

#### View Your Meal Plan
```bash
curl "https://yeschefapp-production.up.railway.app/api/v2/meal-plans/116?user_id=11"
```

#### Get All Your Grocery Lists
```bash
curl "https://yeschefapp-production.up.railway.app/api/v2/grocery-lists/user/11"
```

#### Create a Recipe
```bash
curl -X POST https://yeschefapp-production.up.railway.app/api/v2/recipes \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 11,
    "title": "My Amazing Recipe",
    "category": "Dinner",
    "ingredients": [
      {"name": "Ingredient 1", "quantity": "2", "unit": "cups"}
    ],
    "instructions": "Step 1: Do this\nStep 2: Do that",
    "prep_time": 15,
    "cook_time": 30,
    "servings": 4
  }'
```

---

## 📚 Learn More

- [Complete API Reference](./API_REFERENCE.md) - Full documentation
- [OpenAPI Specification](./openapi.yaml) - Interactive API explorer
- [Migration Guide](#migration-from-v1) - Migrate from v1 to v2

---

## 💡 Pro Tips

### 1. **Use the STAR Feature**
Instead of making 3+ API calls, use:
```bash
GET /api/v2/recipes/user/{userId}/stats
```
This is **3x faster** than v1!

### 2. **Use the POWER Features**
The meal plan → grocery list feature saves you 10+ API calls:
```bash
POST /api/v2/grocery-lists/from-meal-plan/{planId}
```

### 3. **Always Check `success` Field**
```javascript
const response = await fetch(url);
const json = await response.json();

if (json.success) {
  // Data is in json.data
  console.log(json.data);
} else {
  // Error message is in json.error
  console.error(json.error);
}
```

### 4. **Use Pagination for Large Lists**
```bash
GET /api/v2/recipes/user/11/stats?page=1&per_page=20
```

---

## 🐛 Troubleshooting

### Issue: "Recipe not found"
**Solution:** Make sure you're using a valid recipe ID. Get recipe IDs from:
```bash
GET /api/v2/recipes/user/{userId}/stats
```

### Issue: "Meal plan not found"
**Solution:** Check that you're using the correct meal plan ID and user_id.

### Issue: "Failed to create grocery list"
**Solution:** Make sure your meal plan has at least one recipe with ingredients.

### Issue: Connection timeout
**Solution:** The API might be waking up (Railway free tier). Try again in 10 seconds.

---

## 📞 Need Help?

- 📖 [Full API Documentation](./API_REFERENCE.md)
- 🐛 [Report Issues](https://github.com/tranmich/yeschef-mobile/issues)
- 📧 Email: support@yeschef.app

---

## 🎊 Examples in Different Languages

### JavaScript / Node.js
```javascript
// Get recipes with stats
const getRecipesWithStats = async (userId) => {
  const response = await fetch(
    `https://yeschefapp-production.up.railway.app/api/v2/recipes/user/${userId}/stats`
  );
  const data = await response.json();
  
  if (data.success) {
    console.log(`Found ${data.data.stats.total_recipes} recipes!`);
    console.log('Categories:', data.data.categories);
    return data.data;
  } else {
    console.error('Error:', data.error);
  }
};

// Create grocery list from meal plan
const createGroceryList = async (mealPlanId, userId) => {
  const response = await fetch(
    `https://yeschefapp-production.up.railway.app/api/v2/grocery-lists/from-meal-plan/${mealPlanId}?user_id=${userId}`,
    { method: 'POST' }
  );
  const data = await response.json();
  
  if (data.success) {
    console.log(`Created list with ${data.data.stats.total_items} items!`);
    return data.data;
  } else {
    console.error('Error:', data.error);
  }
};

// Usage
await getRecipesWithStats(11);
await createGroceryList(116, 11);
```

### Python
```python
import requests

BASE_URL = "https://yeschefapp-production.up.railway.app/api/v2"

# Get recipes with stats
def get_recipes_with_stats(user_id):
    response = requests.get(f"{BASE_URL}/recipes/user/{user_id}/stats")
    data = response.json()
    
    if data['success']:
        print(f"Found {data['data']['stats']['total_recipes']} recipes!")
        print(f"Categories: {data['data']['categories']}")
        return data['data']
    else:
        print(f"Error: {data['error']}")

# Create grocery list from meal plan
def create_grocery_list(meal_plan_id, user_id):
    url = f"{BASE_URL}/grocery-lists/from-meal-plan/{meal_plan_id}"
    response = requests.post(url, params={'user_id': user_id})
    data = response.json()
    
    if data['success']:
        print(f"Created list with {data['data']['stats']['total_items']} items!")
        return data['data']
    else:
        print(f"Error: {data['error']}")

# Usage
get_recipes_with_stats(11)
create_grocery_list(116, 11)
```

### React Native (Mobile App)
```javascript
// src/api/v2Client.js
const API_BASE = 'https://yeschefapp-production.up.railway.app/api/v2';

export const api = {
  // Get recipes with stats
  getRecipesWithStats: async (userId) => {
    try {
      const response = await fetch(`${API_BASE}/recipes/user/${userId}/stats`);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },
  
  // Create grocery list from meal plan
  createGroceryListFromMealPlan: async (mealPlanId, userId) => {
    try {
      const response = await fetch(
        `${API_BASE}/grocery-lists/from-meal-plan/${mealPlanId}?user_id=${userId}`,
        { method: 'POST' }
      );
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }
};

// Usage in a component
import { api } from './api/v2Client';

const RecipesScreen = () => {
  const [recipes, setRecipes] = useState([]);
  
  useEffect(() => {
    const loadRecipes = async () => {
      const data = await api.getRecipesWithStats(11);
      if (data.success) {
        setRecipes(data.data.recipes);
      }
    };
    loadRecipes();
  }, []);
  
  return (
    <View>
      {recipes.map(recipe => (
        <Text key={recipe.id}>{recipe.title}</Text>
      ))}
    </View>
  );
};
```

---

## 🚀 Ready to Build Something Amazing?

You now have everything you need to build with YesChef API v2!

**Start coding and build the next great recipe app!** 💪

---

**Happy Coding!** 🎉
