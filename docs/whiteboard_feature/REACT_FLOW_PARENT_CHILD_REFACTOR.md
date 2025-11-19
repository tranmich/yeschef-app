# React Flow Parent-Child Refactor Plan
**Date**: November 5, 2025  
**Status**: READY TO IMPLEMENT  
**Architecture**: React Flow Native Nodes (Path A)

---

## 🎯 Goal

Refactor meal plan system to use React Flow's parent-child node architecture:
- **Meal Plan = Parent Node** (container with header)
- **Recipe Cards = Child Nodes** (full-size, draggable within parent)
- **Auto-resize** parent based on children
- **Tag management** when moving in/out of parent
- **Copy on duplicate** when recipe added to multiple meal plans

---

## 📐 Architecture Design

### **Before (Current):**
```
MealPlanFloatingWidget (Custom div)
  ├── position: absolute
  ├── Manual drag handlers
  ├── Manual resize handlers
  └── Mini recipe cards (new, unused)
```

### **After (Target):**
```
React Flow Canvas
  ├── Meal Plan Node (parent)
  │   ├── type: 'mealPlanContainer'
  │   ├── Auto-resizing container
  │   ├── Header with name/actions
  │   └── Content area (children render here)
  │
  └── Recipe Card Nodes (children)
      ├── type: 'recipeCard'
      ├── parentNode: 'meal-plan-170'
      ├── extent: 'parent'
      ├── Full-size recipe display
      └── Tags: ['Pizza Party']
```

---

## 🔧 Implementation Steps

### **Step 1: Create MealPlanContainer Node Component**
File: `frontend/src/components/whiteboard/nodes/MealPlanContainerNode.js`

**Features:**
- Custom React Flow node type
- Header with editable name
- Auto-expanding content area
- Minimum dimensions (400x300)
- Drop zone for recipe cards
- Visual feedback on drag-over

**Structure:**
```jsx
const MealPlanContainerNode = ({ id, data }) => {
  return (
    <div className="meal-plan-container-node">
      {/* Header */}
      <div className="node-header">
        <input 
          value={data.name} 
          onChange={(e) => data.onNameChange(id, e.target.value)}
        />
        <button onClick={() => data.onDelete(id)}>×</button>
      </div>
      
      {/* Content area - children render here automatically */}
      <div className="node-content">
        {data.recipeCount} recipes
      </div>
      
      {/* Footer */}
      <div className="node-footer">
        <button onClick={() => data.onGenerateGroceryList(id)}>
          Generate Grocery List
        </button>
      </div>
    </div>
  );
};
```

---

### **Step 2: Create RecipeCard Node Component**
File: `frontend/src/components/whiteboard/nodes/RecipeCardNode.js`

**Features:**
- Full-size recipe card display
- Shows thumbnail, title, metadata
- Tag pills at bottom (meal plan names)
- Hover effects
- Click to view detail
- Draggable (React Flow native)

**Structure:**
```jsx
const RecipeCardNode = ({ id, data, selected }) => {
  const tags = data.tags || [];
  
  return (
    <div className={`recipe-card-node ${selected ? 'selected' : ''}`}>
      {/* Thumbnail */}
      <div className="recipe-thumbnail">
        <img src={data.recipe.image_url} alt={data.recipe.title} />
      </div>
      
      {/* Content */}
      <div className="recipe-content">
        <h3>{data.recipe.title}</h3>
        <p>{data.recipe.description}</p>
      </div>
      
      {/* Tags */}
      {tags.length > 0 && (
        <div className="recipe-tags">
          {tags.map(tag => (
            <span key={tag} className="tag">{tag}</span>
          ))}
        </div>
      )}
    </div>
  );
};
```

---

### **Step 3: Update WhiteboardApp to Use New Node Types**

**Register node types:**
```jsx
const nodeTypes = {
  mealPlanContainer: MealPlanContainerNode,
  recipeCard: RecipeCardNode,
  // ... other node types
};

<ReactFlow
  nodeTypes={nodeTypes}
  nodes={nodes}
  edges={edges}
  onNodesChange={onNodesChange}
/>
```

**Node structure:**
```javascript
// Meal plan parent node
{
  id: 'meal-plan-170',
  type: 'mealPlanContainer',
  position: { x: 100, y: 100 },
  data: {
    name: 'Pizza Party',
    mealPlanDbId: 170,
    recipeCount: 2,
    onNameChange: handleMealPlanNameChange,
    onDelete: handleMealPlanDelete,
    onGenerateGroceryList: handleGenerateGroceryList
  },
  style: {
    width: 600,  // Auto-calculated based on children
    height: 800,
    padding: 20
  }
}

// Recipe child node
{
  id: 'recipe-123',
  type: 'recipeCard',
  position: { x: 20, y: 60 }, // Relative to parent
  parentNode: 'meal-plan-170', // ← Links to parent!
  extent: 'parent', // ← Constrained to parent bounds
  draggable: true,
  data: {
    recipe: {
      id: 123,
      title: 'Margherita Pizza',
      image_url: 'https://...',
      // ... full recipe data
    },
    tags: ['Pizza Party'] // ← From parent
  },
  style: {
    width: 280,
    height: 350
  }
}
```

---

### **Step 4: Implement Drag & Drop Logic**

#### **Drop Recipe INTO Meal Plan:**
```javascript
const handleNodeDragStop = (event, node) => {
  // Check if recipe node dropped onto meal plan container
  const targetParent = findParentNodeUnderCursor(event);
  
  if (targetParent && targetParent.type === 'mealPlanContainer') {
    if (node.parentNode === targetParent.id) {
      // Already in this meal plan, just update position
      updateNodePosition(node.id, getRelativePosition(event, targetParent));
    } else {
      // Moving to NEW meal plan (or first time)
      if (node.parentNode) {
        // Recipe already in another meal plan → CREATE COPY
        const copiedNode = createRecipeCopy(node, targetParent);
        addNode(copiedNode);
      } else {
        // Recipe was standalone → MOVE into meal plan
        updateNode(node.id, {
          parentNode: targetParent.id,
          extent: 'parent',
          position: getRelativePosition(event, targetParent)
        });
      }
      
      // Add meal plan tag
      addTagToRecipe(node.id, targetParent.data.name);
      
      // Update meal plan recipe count
      updateMealPlanRecipeCount(targetParent.id);
      
      // Trigger auto-resize
      resizeParentToFitChildren(targetParent.id);
      
      // Save to database
      saveMealPlanRecipes(targetParent.data.mealPlanDbId);
    }
  }
};
```

#### **Drag Recipe OUT of Meal Plan:**
```javascript
const handleNodeDrag = (event, node) => {
  if (node.parentNode) {
    // Check if dragging outside parent bounds
    const parentNode = getNodeById(node.parentNode);
    const isOutside = isOutsideParentBounds(event, parentNode);
    
    if (isOutside) {
      // Remove from meal plan
      updateNode(node.id, {
        parentNode: null,
        extent: undefined,
        position: getAbsolutePosition(event)
      });
      
      // Remove meal plan tag
      removeTagFromRecipe(node.id, parentNode.data.name);
      
      // Update meal plan recipe count
      updateMealPlanRecipeCount(parentNode.id);
      
      // Trigger auto-resize
      resizeParentToFitChildren(parentNode.id);
      
      // Save to database
      saveMealPlanRecipes(parentNode.data.mealPlanDbId);
    }
  }
};
```

---

### **Step 5: Implement Auto-Resize**

```javascript
const resizeParentToFitChildren = (parentId) => {
  const children = nodes.filter(n => n.parentNode === parentId);
  
  if (children.length === 0) {
    // No children, use minimum size
    updateNode(parentId, {
      style: {
        width: 400,
        height: 300
      }
    });
    return;
  }
  
  // Calculate bounding box of all children
  let minX = Infinity, minY = Infinity;
  let maxX = -Infinity, maxY = -Infinity;
  
  children.forEach(child => {
    const x = child.position.x;
    const y = child.position.y;
    const width = child.style?.width || 280;
    const height = child.style?.height || 350;
    
    minX = Math.min(minX, x);
    minY = Math.min(minY, y);
    maxX = Math.max(maxX, x + width);
    maxY = Math.max(maxY, y + height);
  });
  
  // Add padding
  const padding = 40;
  const headerHeight = 60;
  const footerHeight = 60;
  
  const newWidth = maxX - minX + (padding * 2);
  const newHeight = maxY - minY + headerHeight + footerHeight + (padding * 2);
  
  // Update parent size
  updateNode(parentId, {
    style: {
      width: Math.max(400, newWidth),
      height: Math.max(300, newHeight)
    }
  });
};
```

---

### **Step 6: Update Data Persistence**

#### **Save Meal Plan Recipes:**
```javascript
const saveMealPlanRecipes = async (mealPlanDbId) => {
  // Get all recipe nodes that are children of this meal plan
  const mealPlanNode = nodes.find(n => n.data.mealPlanDbId === mealPlanDbId);
  const recipeNodes = nodes.filter(n => n.parentNode === mealPlanNode.id);
  
  // Extract recipe IDs
  const recipeIds = recipeNodes.map(n => n.data.recipe.id);
  
  // Update meal_plans.plan_data_json
  const planData = {
    days: {
      day1: {
        name: mealPlanNode.data.name,
        recipes: recipeIds.map(id => ({ id }))
      }
    }
  };
  
  await fetch(`/api/meal-plans/${mealPlanDbId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      plan_data_json: planData
    })
  });
  
  // Also update whiteboard object
  await fetch(`/api/v2/whiteboards/${whiteboardId}/objects/${mealPlanNode.id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      position: {
        x: mealPlanNode.position.x,
        y: mealPlanNode.position.y,
        width: mealPlanNode.style.width,
        height: mealPlanNode.style.height
      }
    })
  });
};
```

---

## 🎨 Styling

### **MealPlanContainerNode.css:**
```css
.meal-plan-container-node {
  background: white;
  border: 3px solid #667eea;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  min-width: 400px;
  min-height: 300px;
}

.meal-plan-container-node .node-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px;
  border-radius: 12px 12px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.meal-plan-container-node .node-content {
  padding: 20px;
  min-height: 200px;
  background: #f9fafb;
}

.meal-plan-container-node .node-footer {
  padding: 12px 16px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Drag-over state */
.meal-plan-container-node.drag-over {
  border-color: #FF6B6B;
  box-shadow: 0 0 20px rgba(255, 107, 107, 0.3);
  background: rgba(102, 126, 234, 0.05);
}
```

### **RecipeCardNode.css:**
```css
.recipe-card-node {
  width: 280px;
  height: 350px;
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
  cursor: move;
}

.recipe-card-node:hover,
.recipe-card-node.selected {
  border-color: #FF6B6B;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.recipe-card-node .recipe-thumbnail {
  width: 100%;
  height: 180px;
  overflow: hidden;
}

.recipe-card-node .recipe-thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.recipe-card-node .recipe-content {
  padding: 16px;
}

.recipe-card-node .recipe-tags {
  display: flex;
  gap: 8px;
  padding: 0 16px 16px;
  flex-wrap: wrap;
}

.recipe-card-node .tag {
  background: #667eea;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}
```

---

## 🗄️ Data Structure Changes

### **Whiteboard Objects Table:**
```sql
-- No changes needed! 
-- Parent-child relationship handled by React Flow
-- We just store position and dimensions
```

### **Meal Plans Table:**
```sql
-- No changes needed!
-- plan_data_json still stores recipe IDs:
{
  "days": {
    "day1": {
      "name": "Pizza Party",
      "recipes": [
        {"id": 123},
        {"id": 456}
      ]
    }
  }
}
```

---

## 🧪 Testing Checklist

### **Basic Functionality:**
- [ ] Meal plan container renders as parent node
- [ ] Recipe cards render as child nodes inside parent
- [ ] Drag recipe card within meal plan → position updates
- [ ] Drag recipe card OUT of meal plan → becomes standalone
- [ ] Drag recipe card INTO meal plan → becomes child
- [ ] Drag recipe from one meal plan to another → creates copy

### **Auto-Resize:**
- [ ] Adding recipe → parent grows
- [ ] Removing recipe → parent shrinks
- [ ] Moving recipe within parent → parent adjusts
- [ ] Empty meal plan → shows minimum size

### **Tagging:**
- [ ] Recipe inside meal plan shows tag
- [ ] Recipe removed from meal plan loses tag
- [ ] Recipe in multiple meal plans shows multiple tags
- [ ] Tags persist after save/reload

### **Persistence:**
- [ ] Save → reload → recipes stay in meal plan
- [ ] Save → reload → meal plan size persists
- [ ] Save → reload → tags persist
- [ ] Multiple meal plans save independently

---

## 📊 Migration Strategy

### **Phase 1: Build New Components** (2-3 hours)
1. Create `MealPlanContainerNode.js`
2. Create `RecipeCardNode.js`
3. Create CSS files
4. Register node types in WhiteboardApp

### **Phase 2: Implement Logic** (2-3 hours)
1. Add drag & drop handlers
2. Implement auto-resize
3. Add tag management
4. Test copy-on-duplicate

### **Phase 3: Update Persistence** (1-2 hours)
1. Update save logic
2. Update load logic
3. Test database round-trip

### **Phase 4: Remove Old Code** (30 min)
1. Delete `MealPlanFloatingWidget.js` ← Old approach
2. Delete `MiniRecipeCard.js` ← No longer needed
3. Clean up unused CSS

### **Total Time: ~6-8 hours**

---

## ✅ Benefits of This Approach

1. ✅ **Native React Flow** - Uses built-in parent-child system
2. ✅ **Auto-resize** - Handled by React Flow + our logic
3. ✅ **Cleaner code** - Less manual position tracking
4. ✅ **Better performance** - React Flow optimizations
5. ✅ **Full-size cards** - Matches user's vision exactly
6. ✅ **Proper constraints** - extent='parent' prevents overflow
7. ✅ **Copy on duplicate** - Easy to implement
8. ✅ **Tag management** - Automatic based on parent

---

## 🚀 Ready to Implement!

Let's start with **Step 1: MealPlanContainerNode.js**

This will be the foundation for everything else.
