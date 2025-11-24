# API Response Format Reference
**Quick reference for API response structures across V1 and V2**

---

## V2 Whiteboard API (`/api/v2/whiteboard/*`)

### Standard Success Response
```json
{
  "success": true,
  "data": {
    "id": 123,
    "whiteboard_id": 3,
    "type": "mp",
    "entity_type": "meal_plan",
    "entity_id": 456,
    "position": [100, 200, 320, 200, 0]
  }
}
```

**JavaScript Access:**
```javascript
const response = await whiteboardAPI.createObject(whiteboardId, data);
if (response.success) {
  const objectId = response.data.id;
  const entityType = response.data.entity_type;
}
```

### Standard Error Response
```json
{
  "success": false,
  "error": "Error message here"
}
```

---

## V1 Meal Plan API (`/api/meal-plans/*`)

### GET `/api/meal-plans/:id`
```json
{
  "success": true,
  "meal_plan": {
    "id": 123,
    "user_id": 11,
    "plan_name": "Weekly Plan",
    "week_start_date": "2025-11-05",
    "meal_data": {
      "days": {
        "day1": {
          "name": "Monday",
          "recipes": [
            {"id": 456, "name": "Pasta"}
          ]
        }
      },
      "dayOrder": ["day1"]
    },
    "created_date": "2025-11-05T10:00:00",
    "updated_date": "2025-11-05T10:00:00"
  }
}
```

**JavaScript Access:**
```javascript
const response = await whiteboardAPI.getMealPlan(planId);
if (response.success) {
  const mealPlan = response.meal_plan;  // ← NOT response.data
  const planName = response.meal_plan.plan_name;
  const days = response.meal_plan.meal_data.days;
}
```

### POST `/api/meal-plans`
**Request:**
```json
{
  "plan_name": "Weekly Plan",
  "week_start_date": "2025-11-05",
  "plan_data": {
    "days": {
      "day1": {"name": "Monday", "recipes": []}
    }
  },
  "household_id": 11
}
```

**Response:**
```json
{
  "success": true,
  "plan_id": 123,
  "plan_name": "Weekly Plan",
  "week_start_date": "2025-11-05"
}
```

**JavaScript Access:**
```javascript
const response = await apiCall('/api/meal-plans', {...});
if (response.success) {
  const newPlanId = response.plan_id;  // ← NOT response.data.id
}
```

### PUT `/api/meal-plans/:id`
**Request:**
```json
{
  "plan_data": {
    "days": {
      "day1": {"name": "Taco Tuesday", "recipes": [...]}
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Meal plan updated successfully"
}
```

---

## V1 Recipe API (`/api/recipes/*`)

### GET `/api/recipes/:id`
```json
{
  "success": true,
  "recipe": {
    "id": 456,
    "title": "Spaghetti Carbonara",
    "ingredients": "...",
    "instructions": "...",
    ...
  }
}
```

**JavaScript Access:**
```javascript
const response = await api.getRecipe(recipeId);
if (response.success) {
  const recipe = response.recipe;  // ← NOT response.data
}
```

---

## V1/V2 Grocery List API (Mixed)

### V2: GET `/api/v2/whiteboard/:wid/grocery-lists`
```json
{
  "success": true,
  "data": {
    "grocery_lists": [
      {
        "id": 789,
        "name": "Shopping List",
        "items": [...],
        "widget_position": {"x": 100, "y": 200, "size": "medium"}
      }
    ]
  }
}
```

**JavaScript Access:**
```javascript
const response = await whiteboardAPI.getWhiteboardGroceryLists(whiteboardId);
if (response.success) {
  const lists = response.data.grocery_lists;  // ← V2 format with data wrapper
}
```

### V2: POST/PATCH Grocery Lists
Follow V2 format with `response.data` wrapper

---

## Quick Reference Table

| Endpoint | Format | Access Pattern | Notes |
|----------|--------|----------------|-------|
| `/api/v2/whiteboard/*` | V2 | `response.data.field` | All whiteboard operations |
| `/api/meal-plans` | V1 | `response.meal_plan` (GET)<br>`response.plan_id` (POST) | Direct on response |
| `/api/recipes` | V1 | `response.recipe` | Direct on response |
| `/api/v2/whiteboard/:wid/grocery-lists` | V2 | `response.data.grocery_lists` | Uses V2 format |

---

## Common Mistakes

### ❌ Assuming all APIs use V2 format
```javascript
// Wrong for V1 APIs
const mealPlan = response.data.meal_plan;  // undefined!
```

### ✅ Check endpoint version
```javascript
// Correct for V1
if (endpoint.includes('/api/meal-plans')) {
  const mealPlan = response.meal_plan;
}

// Correct for V2
if (endpoint.includes('/api/v2/whiteboard')) {
  const object = response.data;
}
```

---

## Testing API Responses

### With curl
```bash
# Test V1 meal plan
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/meal-plans/123

# Test V2 whiteboard object
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/v2/whiteboard/3/o
```

### With Browser DevTools
1. Open Network tab
2. Filter by XHR/Fetch
3. Click on API call
4. View "Response" tab to see actual format
5. Update code to match actual structure

---

## Migration Notes

### When migrating V1 → V2:
1. **Wrap response in data object:**
   ```javascript
   // V1
   return jsonify({'success': True, 'meal_plan': plan})
   
   // V2
   return jsonify({'success': True, 'data': {'meal_plan': plan}})
   ```

2. **Update all frontend calls:**
   ```javascript
   // V1
   const plan = response.meal_plan;
   
   // V2
   const plan = response.data.meal_plan;
   ```

3. **Test thoroughly** - response format changes break existing code!

---

## Best Practices

1. **Log responses during development:**
   ```javascript
   console.log('📥 API Response:', response);
   ```

2. **Check success before accessing data:**
   ```javascript
   if (response.success) {
     // Access fields here
   }
   ```

3. **Handle both formats during transition:**
   ```javascript
   const mealPlan = response.meal_plan || response.data?.meal_plan;
   ```

4. **Document response format in API comments:**
   ```javascript
   /**
    * Get meal plan by ID
    * @returns {Object} {success: true, meal_plan: {...}} (V1 format)
    */
   ```
