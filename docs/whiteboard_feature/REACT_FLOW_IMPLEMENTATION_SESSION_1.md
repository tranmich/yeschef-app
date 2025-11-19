# React Flow Parent-Child Implementation - Session 1
**Date**: November 5, 2025  
**Status**: COMPONENTS CREATED ✅  
**Next**: Integration with WhiteboardApp

---

## ✅ What We Built

### **New Components Created:**

1. **MealPlanContainerNode.js** (166 lines)
   - React Flow parent node
   - Editable meal plan name
   - Recipe count display
   - Generate grocery list button
   - Delete meal plan button
   - Drop zone for recipe cards
   - Manual resize with @reactflow/node-resizer

2. **MealPlanContainerNode.css** (201 lines)
   - Purple gradient header
   - Empty state styling
   - Drag-over visual feedback
   - Footer with actions
   - Selected state styling

3. **RecipeCardNode.js** (104 lines)
   - Full-size recipe card display
   - Thumbnail with fallback emoji
   - Recipe title, description, metadata
   - Tag pills for meal plan memberships
   - Click handlers for details and tags

4. **RecipeCardNode.css** (149 lines)
   - Card layout (280px × 350px+)
   - Hover effects (lift + shadow)
   - Thumbnail zoom on hover
   - Tag styling with gradient
   - Selected state

5. **index.js** (7 lines)
   - Export both node types

---

## 📐 Architecture

### **Parent-Child Relationship:**

```
ReactFlow Canvas
  ├── MealPlanContainerNode (parent)
  │   ├── id: 'meal-plan-170'
  │   ├── type: 'mealPlanContainer'
  │   ├── position: {x: 100, y: 100}
  │   ├── data: {name, mealPlanDbId, recipeCount, ...}
  │   └── style: {width, height}
  │
  └── RecipeCardNode (child)
      ├── id: 'recipe-123'
      ├── type: 'recipeCard'
      ├── position: {x: 20, y: 60} ← Relative to parent!
      ├── parentNode: 'meal-plan-170' ← Links to parent
      ├── extent: 'parent' ← Constrained to parent bounds
      ├── data: {recipe, tags: ['Pizza Party']}
      └── style: {width: 280, height: 350}
```

---

## 🎨 Visual Design

### **Meal Plan Container:**
- **Header**: Purple gradient (#667eea → #764ba2)
- **Content**: Light gray background (#f9fafb)
- **Border**: 3px solid purple
- **Min Size**: 400px × 300px
- **Drag-Over**: Dashed green border with glow

### **Recipe Card:**
- **Size**: 280px × 350px minimum
- **Thumbnail**: 180px height with zoom on hover
- **Border**: 2px solid gray, red on hover/select
- **Tags**: Purple gradient pills at bottom
- **Fallback**: 🍳 emoji placeholder

---

## 🔌 Integration Points

### **Node Type Registration** (Next Step):
```jsx
// In WhiteboardApp.js
import { MealPlanContainerNode, RecipeCardNode } from './components/whiteboard/nodes';

const nodeTypes = {
  mealPlanContainer: MealPlanContainerNode,
  recipeCard: RecipeCardNode,
  // ... other node types
};

<ReactFlow
  nodeTypes={nodeTypes}
  nodes={nodes}
  onNodesChange={onNodesChange}
/>
```

### **Data Structure Examples:**

**Meal Plan Parent Node:**
```javascript
{
  id: 'meal-plan-170',
  type: 'mealPlanContainer',
  position: { x: 100, y: 100 },
  data: {
    name: 'Pizza Party',
    mealPlanDbId: 170,
    recipeCount: 2,
    onNameChange: (id, name) => handleMealPlanNameChange(id, name),
    onDelete: (id) => handleMealPlanDelete(id),
    onGenerateGroceryList: (id) => handleGenerateGroceryList(id)
  },
  style: {
    width: 600,
    height: 800
  }
}
```

**Recipe Child Node:**
```javascript
{
  id: 'recipe-123',
  type: 'recipeCard',
  position: { x: 20, y: 60 }, // Relative to parent
  parentNode: 'meal-plan-170', // ← Parent link
  extent: 'parent', // ← Constrained to parent
  data: {
    recipe: {
      id: 123,
      title: 'Margherita Pizza',
      description: 'Classic Italian pizza',
      image_url: 'https://...',
      prep_time: 15,
      cook_time: 20
    },
    tags: ['Pizza Party'], // ← From parent
    onClick: (id, recipe) => handleRecipeClick(id, recipe),
    onTagClick: (tag) => handleTagClick(tag)
  },
  style: {
    width: 280,
    height: 350
  }
}
```

---

## 🚀 Next Steps (Session 2)

### **1. Register Node Types in WhiteboardApp** (30 min)
- Import both node components
- Add to `nodeTypes` object
- Test rendering

### **2. Implement Drag & Drop Logic** (2-3 hours)
- Detect when recipe dropped on meal plan
- Handle parent-child assignment
- Add/remove tags based on parent
- Copy recipe when dragging to second meal plan
- Handle dragging OUT of meal plan (remove parent)

### **3. Implement Auto-Resize** (1 hour)
- Calculate bounding box of children
- Update parent dimensions
- Trigger on child add/move/remove

### **4. Update Data Persistence** (1-2 hours)
- Save meal plan recipes to database
- Save whiteboard object positions
- Load existing meal plans as parent nodes
- Load recipes as child nodes with proper parent links

### **5. Remove Old Code** (30 min)
- Delete `MealPlanFloatingWidget.js`
- Delete `MiniRecipeCard.js`
- Clean up unused CSS
- Update imports

---

## 🧪 Testing Checklist (For Session 2)

### **Component Rendering:**
- [ ] Meal plan container renders
- [ ] Recipe cards render
- [ ] Tags display correctly
- [ ] Empty state shows when no recipes
- [ ] Recipe count updates

### **Interactions:**
- [ ] Click meal plan name to edit
- [ ] Press Enter/Escape in name input
- [ ] Click delete button → confirmation
- [ ] Click generate grocery list
- [ ] Click recipe card → detail modal
- [ ] Click tag → filter by tag

### **React Flow Integration:**
- [ ] Nodes appear on canvas
- [ ] Parent-child relationship works
- [ ] Children constrained to parent bounds
- [ ] Manual resize works (NodeResizer)
- [ ] Selection works (single/multi)

---

## 📦 Files Created

```
frontend/src/components/whiteboard/nodes/
├── MealPlanContainerNode.js      (166 lines)
├── MealPlanContainerNode.css     (201 lines)
├── RecipeCardNode.js             (104 lines)
├── RecipeCardNode.css            (149 lines)
└── index.js                      (7 lines)
```

**Total**: 627 lines of production code

---

## 📚 Documentation Created

```
docs/whiteboard_feature/
├── REACT_FLOW_PARENT_CHILD_REFACTOR.md  (Detailed plan)
└── REACT_FLOW_IMPLEMENTATION_SESSION_1.md (This file)
```

---

## 💡 Key Design Decisions

### **1. Why @reactflow/node-resizer?**
- Allows manual resize of meal plan container
- Works alongside auto-resize logic
- Better UX than auto-only

### **2. Why `nodrag` class?**
- Prevents dragging when interacting with buttons/inputs
- React Flow convention
- Applied to header buttons, footer, tags

### **3. Why separate node files?**
- Better code organization
- Easier testing
- Clear separation of concerns

### **4. Why gradient backgrounds?**
- Visual distinction from recipe cards
- Matches YesChef brand colors
- Creates hierarchy (container > content)

---

## ⚡ Performance Considerations

### **Current:**
- Lightweight components
- CSS transitions for smoothness
- No heavy computations

### **Future Optimizations:**
- Memoize recipe card components
- Virtual scrolling for 100+ recipes
- Image lazy loading
- Debounce resize calculations

---

## 🎓 React Flow Learnings

### **Parent-Child Nodes:**
```javascript
// Child node must have:
parentNode: 'parent-id',  // Links to parent
extent: 'parent',         // Constrained to parent bounds

// Position is relative to parent
position: { x: 20, y: 60 } // NOT absolute canvas position
```

### **NodeResizer:**
```jsx
<NodeResizer
  minWidth={400}
  minHeight={300}
  isVisible={selected} // Only show when selected
  lineStyle={{...}}
  handleStyle={{...}}
/>
```

### **Preventing Drag:**
```jsx
// Add 'nodrag' class to interactive elements
<div className="node-header nodrag">
  <input className="nodrag" />
  <button className="nodrag">×</button>
</div>
```

---

## ✅ Ready for Integration!

All components are built and styled. Next session we'll:
1. Wire them up in WhiteboardApp
2. Implement drag & drop logic
3. Add auto-resize
4. Connect to database
5. Test end-to-end

**Estimated Time to Complete**: 4-6 hours total  
**Session 1 Complete**: ~2 hours  
**Session 2 Remaining**: ~4 hours

---

**Status**: COMPONENTS READY ✅  
**Next**: Integration & logic implementation  
**Build**: Required before testing
