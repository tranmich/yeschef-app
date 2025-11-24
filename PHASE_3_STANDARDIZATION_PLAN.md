# Phase 3: Grocery List Schema Standardization

**Goal:** Eliminate naming inconsistencies across the entire system  
**Impact:** Reduce technical debt, simplify maintenance, prevent field mismatch bugs  
**Timeline:** 3-4 hours of focused work

---

## 🎯 The Problem

### Current Chaos:
| Platform | Item Name | List Name | Items Array |
|----------|-----------|-----------|-------------|
| Whiteboard | `ingredient` | `name` | `items` |
| Web Manager | `name` | `name` | `sections` |
| Mobile | `name` | `name` | `items` |
| Database | varies | `name` | `list_data` |
| Recipe Gen | `ingredient_name` | - | `by_section` |

**Every adapter checks:** `item.display_text || item.name || item.ingredient || item.ingredient_name`

**Cost:** 7+ files updated per feature, high bug risk, confusing for developers

---

## ✅ The Standard Schema (Phase 3)

### **Single Source of Truth:**

```javascript
// StandardGroceryList - THE ONLY FORMAT
{
  id: number,
  name: string,                    // List name
  items: [                         // ALWAYS an array
    {
      id: string,                  // Unique ID
      name: string,                // ← ONLY field for item text
      checked: boolean,
      quantity?: string,           // Optional metadata
      unit?: string,
      category?: string
    }
  ],
  household_id?: number,
  whiteboard_id?: number,
  created_at: string,
  updated_at: string
}
```

### **Rules:**
1. ✅ Item text is **ALWAYS** `name`
2. ✅ List name is **ALWAYS** `name`
3. ✅ Items are **ALWAYS** a flat array called `items`
4. ❌ **NEVER** use: `ingredient`, `ingredient_name`, `display_text`, `list_name`, `list_data`, `sections`

---

## 📋 Migration Plan (Step-by-Step)

### **Step 1: Create Normalization Layer (Backend)**

**File:** `app/utils/grocery_list_normalizer.py`

```python
"""
Grocery List Normalizer
Converts any format to/from StandardGroceryList
"""

class GroceryListNormalizer:
    """Single point of conversion for all grocery list formats"""
    
    @staticmethod
    def to_standard(raw_data: dict) -> dict:
        """
        Convert any format to StandardGroceryList
        
        Handles:
        - Whiteboard format (ingredient)
        - Legacy format (list_name, items_json)
        - Web format (sections)
        """
        standard = {
            'id': raw_data.get('id'),
            'name': raw_data.get('name') or raw_data.get('list_name') or 'Grocery List',
            'items': [],
            'household_id': raw_data.get('household_id') or raw_data.get('hid'),
            'whiteboard_id': raw_data.get('whiteboard_id') or raw_data.get('wid'),
            'created_at': raw_data.get('created_at'),
            'updated_at': raw_data.get('updated_at')
        }
        
        # Normalize items from various sources
        items_source = (
            raw_data.get('items') or 
            raw_data.get('list_data') or 
            raw_data.get('items_json') or 
            []
        )
        
        # Convert items to standard format
        if isinstance(items_source, list):
            for item in items_source:
                standard['items'].append({
                    'id': item.get('id') or f"item-{len(standard['items'])}",
                    'name': (
                        item.get('name') or 
                        item.get('ingredient') or 
                        item.get('ingredient_name') or 
                        item.get('display_text') or 
                        'Unknown item'
                    ),
                    'checked': item.get('checked', False),
                    'quantity': item.get('quantity'),
                    'unit': item.get('unit'),
                    'category': item.get('category')
                })
        
        return standard
    
    @staticmethod
    def from_standard(standard: dict, platform: str = 'web') -> dict:
        """
        Convert StandardGroceryList to platform-specific format
        (Only used during transition period)
        """
        if platform == 'database':
            # Database format
            return {
                'id': standard['id'],
                'name': standard['name'],
                'list_data': standard['items'],  # JSONB array
                'household_id': standard.get('household_id'),
                'whiteboard_id': standard.get('whiteboard_id'),
                'created_at': standard.get('created_at'),
                'updated_at': standard.get('updated_at')
            }
        
        # Default: return standard as-is
        return standard
```

**Why this works:**
- ✅ All conversions happen in ONE place
- ✅ Easy to test
- ✅ Easy to update
- ✅ Clear what fields are supported

---

### **Step 2: Update Repository (Backend)**

**File:** `app/database/repositories/grocery_list_repository.py`

```python
from ...utils.grocery_list_normalizer import GroceryListNormalizer

class GroceryListRepository:
    
    def create_grocery_list(self, user_id, name, items, **kwargs):
        """Create with automatic normalization"""
        
        # Normalize input
        standard = GroceryListNormalizer.to_standard({
            'name': name,
            'items': items,
            **kwargs
        })
        
        # Save to database (standard format)
        query = """
            INSERT INTO grocery_lists (user_id, name, list_data, household_id, whiteboard_id)
            VALUES (%s, %s, %s::jsonb, %s, %s)
            RETURNING id, name, list_data as items, created_at, updated_at
        """
        
        result = self._execute_insert(query, (
            user_id,
            standard['name'],
            json.dumps(standard['items']),
            standard.get('household_id'),
            standard.get('whiteboard_id')
        ))
        
        # Return in standard format
        return GroceryListNormalizer.to_standard(result)
    
    def get_grocery_list_by_id(self, list_id, user_id=None):
        """Get and normalize to standard format"""
        
        query = "SELECT id, name, list_data, household_id, whiteboard_id, created_at, updated_at FROM grocery_lists WHERE id = %s"
        result = self._execute_query_one(query, (list_id,))
        
        if result:
            # Normalize to standard
            return GroceryListNormalizer.to_standard({
                **result,
                'items': result.get('list_data')  # Map list_data to items
            })
        
        return None
```

**Benefits:**
- ✅ Repository always returns StandardGroceryList
- ✅ API consumers don't need to know about database structure
- ✅ Easy to change database later

---

### **Step 3: Update API Endpoints (Backend)**

**File:** `app/api/v2/grocery_lists.py`

```python
@grocery_list_bp.route('', methods=['POST'])
def create_grocery_list():
    """Create grocery list - accepts ANY format, returns standard"""
    data = request.get_json()
    
    # Normalize input automatically
    standard = GroceryListNormalizer.to_standard(data)
    
    # Create using normalized data
    grocery_list = grocery_list_service.create_grocery_list(
        user_id=data['user_id'],
        name=standard['name'],
        items=standard['items'],
        household_id=standard.get('household_id'),
        whiteboard_id=standard.get('whiteboard_id')
    )
    
    # Always return standard format
    return jsonify({
        'success': True,
        'data': grocery_list  # Already in standard format
    }), 201
```

**Benefits:**
- ✅ API is forgiving (accepts any format)
- ✅ API is consistent (always returns standard)
- ✅ Clients can gradually migrate

---

### **Step 4: Update Whiteboard (Frontend)**

**File:** `frontend/src/pages/WhiteboardApp.js`

```javascript
// When saving grocery list
const handleSave = async () => {
  const groceryListNodes = nodes.filter(n => n.type === 'groceryListNode');
  
  for (const node of groceryListNodes) {
    // ✅ STANDARD FORMAT - no more "ingredient"!
    const standardList = {
      name: node.data.name,
      items: node.data.items.map(item => ({
        id: item.id,
        name: item.name,           // ← Changed from "ingredient"
        checked: item.checked,
        quantity: item.quantity,
        unit: item.unit
      })),
      household_id: householdId,
      whiteboard_id: whiteboardId,
      widget_position: { x: node.position.x, y: node.position.y }
    };
    
    // Save (API normalizes if needed, but we're already standard!)
    await whiteboardAPI.updateWhiteboardGroceryList(
      whiteboardId,
      node.data.dbId,
      standardList
    );
  }
};

// When loading grocery list
const loadSavedGroceryLists = async (whiteboardId) => {
  const response = await whiteboardAPI.getWhiteboardGroceryLists(whiteboardId);
  
  const groceryListNodes = response.data.grocery_lists.map(list => {
    // ✅ API returns standard format
    return {
      id: `grocery-list-${list.id}`,
      type: 'groceryListNode',
      data: {
        name: list.name,              // ← Standard
        items: list.items,            // ← Already { id, name, checked }
        dbId: list.id
      }
    };
  });
  
  setNodes(prevNodes => [...prevNodes, ...groceryListNodes]);
};
```

**Changes:**
- ❌ Remove: `ingredient` field
- ✅ Use: `name` field everywhere
- ✅ Remove: All `ingredient` references in GroceryListNode.js

---

### **Step 5: Update GroceryManager (Frontend)**

**File:** `frontend/src/components/GroceryManagerWorkspace.js`

```javascript
const handleLoadList = (loadedList) => {
  // ✅ API returns standard format - no more adaptation needed!
  setCurrentList({
    id: loadedList.id,
    name: loadedList.name,      // Already standard
    items: loadedList.items     // Already standard array
  });
  
  // Convert to sections (internal only, for UI)
  const sections = convertToSections(loadedList.items);
  setSections(sections);
};

const handleSave = async () => {
  // Convert sections back to flat array
  const allItems = Object.values(sections).flatMap(section => 
    section.items.map(item => ({
      id: item.id,
      name: item.name,        // ← Standard
      checked: item.checked
    }))
  );
  
  // ✅ Send standard format
  await API.updateGroceryList(currentList.id, {
    name: currentList.name,
    items: allItems          // Flat array
  });
};
```

**Changes:**
- ❌ Remove: All `list_name`, `list_data` fallbacks
- ✅ Use: Standard `name` and `items`
- ✅ Sections are internal UI state only

---

### **Step 6: Update Mobile (React Native)**

**File:** `YesChefMobile/src/services/MobileGroceryAdapter.js`

```javascript
class MobileGroceryAdapter {
  
  static async backendToMobile(backendListData) {
    // ✅ Backend ALWAYS returns standard format now
    // No more checking 5 different field names!
    
    return backendListData.items.map(item => ({
      id: item.id,
      name: item.name,        // ← Simple! Just "name"
      checked: item.checked
    }));
  }
  
  static mobileToBackend(mobileItems, listName) {
    // ✅ Send standard format
    return {
      name: listName,
      items: mobileItems.map(item => ({
        id: item.id,
        name: item.name,      // ← Simple! Just "name"
        checked: item.checked
      }))
    };
  }
}
```

**Changes:**
- ❌ Remove: All fallback chains (`item.ingredient || item.name || ...`)
- ✅ Use: Direct `item.name` access
- ✅ 80% less code in adapter

---

### **Step 7: Clean Up (Remove Legacy)**

After all platforms are updated and tested:

```python
# Drop legacy database columns
python phase2_drop_columns.py  # Drops list_name, items_json, etc.
```

```javascript
// Remove normalizer fallbacks
class GroceryListNormalizer:
    def to_standard(raw_data):
        # ❌ Remove all these fallbacks:
        # name: raw_data.get('name') or raw_data.get('list_name')
        # items: raw_data.get('items') or raw_data.get('list_data')
        
        # ✅ Keep only:
        return {
            'name': raw_data['name'],
            'items': raw_data['items']
        }
```

---

## 📊 Migration Checklist

### **Backend:**
- [ ] Create `GroceryListNormalizer` utility
- [ ] Update `GroceryListRepository` to normalize I/O
- [ ] Update all API endpoints to use normalizer
- [ ] Add validation for standard schema
- [ ] Write tests for normalizer

### **Whiteboard:**
- [ ] Update save to use `item.name` not `item.ingredient`
- [ ] Update load to expect standard format
- [ ] Update GroceryListNode component
- [ ] Remove all `ingredient` references
- [ ] Test create/edit/delete

### **GroceryManager:**
- [ ] Remove `list_name` fallbacks
- [ ] Expect `items` array from API
- [ ] Simplify handleLoadList
- [ ] Test load/save/edit

### **Mobile:**
- [ ] Simplify `backendToMobile` (no fallbacks)
- [ ] Simplify `mobileToBackend` (direct mapping)
- [ ] Remove all field name checks
- [ ] Test load/save/sync

### **Testing:**
- [ ] Create grocery list on whiteboard → Load in mobile (should work)
- [ ] Create on mobile → Load in GroceryManager (should work)
- [ ] Create on web → Load in whiteboard (should work)
- [ ] Cross-platform edit test
- [ ] Household collaboration test

### **Cleanup:**
- [ ] Drop database columns: `list_name`, `items_json`, `created_date`, `updated_date`
- [ ] Remove normalizer fallback code
- [ ] Update documentation
- [ ] Remove old adapter code

---

## 🎯 Expected Results

### **Before (Phase 2):**
```javascript
// 7 different field checks
item.display_text || item.name || item.ingredient || item.ingredient_name || item.text || ...
```

### **After (Phase 3):**
```javascript
// Just one
item.name
```

### **Metrics:**
| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Adapter complexity | 100+ lines | 20 lines | **-80%** |
| Field name checks | 5+ per access | 1 | **-80%** |
| Bug risk | High | Low | **Eliminated** |
| Onboarding time | Hours | Minutes | **-90%** |
| Code duplication | High | None | **Eliminated** |

---

## ⚠️ Migration Risk & Rollback

### **Low Risk Because:**
1. **Backward Compatible:** Normalizer accepts old formats
2. **Gradual:** Can update one platform at a time
3. **Tested:** Each step is testable independently
4. **Rollback:** Can revert one platform if issues arise

### **Rollback Plan:**
1. If whiteboard breaks → Revert whiteboard code only
2. If mobile breaks → Revert mobile code only
3. Backend normalizer ensures compatibility
4. Database unchanged until Step 7

---

## 🚀 Timeline

| Step | Time | Status |
|------|------|--------|
| 1. Create normalizer | 30 min | Not started |
| 2. Update repository | 30 min | Not started |
| 3. Update API endpoints | 20 min | Not started |
| 4. Update whiteboard | 45 min | Not started |
| 5. Update GroceryManager | 30 min | Not started |
| 6. Update mobile | 30 min | Not started |
| 7. Testing | 45 min | Not started |
| 8. Cleanup | 20 min | Not started |
| **Total** | **~4 hours** | |

---

## 💡 Key Insight

**The problem isn't the platforms - it's the lack of a contract.**

By defining `StandardGroceryList` as the **single source of truth**, we:
- ✅ Eliminate field name guessing
- ✅ Make bugs impossible (TypeScript can enforce)
- ✅ Simplify every adapter
- ✅ Speed up feature development
- ✅ Make onboarding easy

**This is the right fix.** It pays for itself in the first week.

---

Ready to start? We'll go step-by-step, testing each change before moving to the next platform.
