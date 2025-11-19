# Meal Plan Drag & Drop - Revert Summary

**Date**: November 5, 2025  
**Status**: Needs Simplification  
**Decision**: Revert React Flow parent-child complexity

---

## 🎯 What We Were Trying to Achieve

- Visual grouping of recipes inside meal plan containers
- Recipes move with container when dragged
- Save/load meal plans with their recipes
- Drag recipes in/out of meal plans

---

## ❌ What Went Wrong

### **React Flow Parent-Child System Issues:**

1. **Positioning Complexity**
   - React Flow v12 doesn't automatically compose parent+child positions
   - Had to manually calculate absolute positions (parent.x + offset)
   - No visual benefit over simple position tracking

2. **Broken Save/Load**
   - Child nodes don't have full recipe data
   - Loading creates nodes with only `{id: 2755}` - missing images, names
   - Had to build complex data fetching logic

3. **Over-Engineering**
   - Used `parentNode` property but React Flow doesn't render children inside parent DOM
   - Children render at canvas level with absolute coordinates anyway
   - Manual movement synchronization needed (defeats purpose of parent-child)

---

## ✅ What Actually Works

1. **Collision Detection** - detecting if recipe is inside container bounds ✅
2. **Movement Sync** - moving children when parent moves (using delta calculation) ✅
3. **Visual Appearance** - recipes appear inside container ✅
4. **Save to Database** - meal_data stores recipe IDs ✅

---

## 💡 The Simple Solution

### **DON'T use React Flow parent-child relationships**

Instead:

```javascript
// Recipe nodes are independent (full data from whiteboard_objects)
{
  id: "recipe-2755",
  type: "recipeCard",
  position: {x: 1500, y: 300},  // Absolute position
  data: {
    recipe_id: 2755,
    name: "Million Dollar Spaghetti",
    image_url: "https://...",
    // Full recipe data!
    mealPlanId: 188  // ← Just track which meal plan it belongs to
  }
}

// Meal plan container is also independent
{
  id: "meal-plan-188",
  type: "mealPlanContainer",
  position: {x: 1400, y: 200},
  data: {
    mealPlanDbId: 188,
    name: "Week 1",
    // No need to track children here!
  }
}
```

### **How It Works:**

1. **Load**: 
   - Load all recipes from whiteboard_objects → full data ✅
   - Load meal plan from meal_data → get recipe IDs
   - Match recipe IDs and set `data.mealPlanId` on matching recipe nodes

2. **Drag Detection**:
   - Check if recipe position is inside container bounds
   - Update `data.mealPlanId` if changed
   - Save meal plan with new recipe list

3. **Container Movement**:
   - Find all recipes where `data.mealPlanId === container.id`
   - Move them by same delta
   - Already implemented and working!

4. **Save**:
   - Meal plan saves recipe IDs in `meal_data.days.day1.recipes`
   - Recipes save as normal whiteboard objects with positions
   - `data.mealPlanId` helps identify relationships

---

## 📝 Implementation Steps

### **1. Remove parentNode Logic** (~15 minutes)

```javascript
// REMOVE from onNodeDragStop:
- parentNode assignment
- extent: 'parent'
- Complex position calculations
- Case 1, 2, 3 handling

// REPLACE WITH:
setNodes(prevNodes => prevNodes.map(n => {
  if (n.id === draggedRecipe.id) {
    return {
      ...n,
      data: {
        ...n.data,
        mealPlanId: isInside ? containerId : null
      }
    };
  }
  return n;
}));
```

### **2. Fix Load Function** (~10 minutes)

```javascript
// When loading meal plan:
const mealPlanRecipeIds = mealData.days.day1.recipes.map(r => r.id);

// When loading recipes from whiteboard_objects:
const recipeNodes = recipeObjects.map(obj => ({
  id: `recipe-${obj.entity_id}`,
  position: obj.position,
  data: {
    ...fullRecipeData,  // ← Already has image, name, etc!
    mealPlanId: mealPlanRecipeIds.includes(obj.entity_id) ? mealPlanDbId : null
  }
}));
```

### **3. Update Container Movement** (~5 minutes)

```javascript
// Already implemented! Just change filter:
if (node.type === 'mealPlanContainer') {
  const childRecipes = prevNodes.filter(n => 
    n.data.mealPlanId === node.data.mealPlanDbId  // ← Instead of n.parentNode
  );
  // Move by delta (already working)
}
```

### **4. Update Save Function** (~5 minutes)

```javascript
// Already correct! Just verify:
const recipes = nodes
  .filter(n => n.data.mealPlanId === mealPlanDbId)
  .map(n => ({ id: n.data.recipe_id }));
```

---

## 🎯 Expected Result

After revert:

1. ✅ Recipes load with full data (images, names, etc.)
2. ✅ Recipes visually inside containers  
3. ✅ Recipes move with containers
4. ✅ Drag in/out works
5. ✅ Save/load works
6. ✅ **Simpler code** - no React Flow parent-child complexity
7. ✅ **Faster** - less computation, cleaner logic

---

## 📊 Files to Modify

1. `WhiteboardApp.js`:
   - `onNodeDragStop` - simplify drag logic
   - `loadWhiteboard` - match recipes to meal plans by ID
   - `onNodesChange` - update filter for child movement
   - `saveMealPlanToDatabase` - update filter (already mostly correct)

2. No other files need changes!

---

## 💭 Lesson Learned

**"Use the right tool for the job"**

- React Flow parent-child is for **hierarchical data structures** (org charts, file trees)
- NOT for **spatial grouping** (recipes in meal plans)
- Spatial grouping = position-based, not hierarchy-based
- Simpler solutions are often better!

---

## 🚀 Next Steps

1. Review this document
2. Confirm revert approach
3. Implement changes (~35 minutes total)
4. Test thoroughly
5. Celebrate working meal plans! 🎉
