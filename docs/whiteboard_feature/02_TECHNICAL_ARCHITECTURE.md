# 🏗️ Technical Architecture - Whiteboard System

**Date:** November 1, 2025 (Updated: November 3, 2025)  
**Purpose:** Complete technical specification for whiteboard implementation

---

## 🎯 **ARCHITECTURAL PHILOSOPHY**

### **Core Concept: Visual Layer Over Existing Data**

The whiteboard is **NOT** a new data system - it's a **visual interface layer** that:

1. **Connects to existing APIs** (recipes, meal plans, grocery lists)
2. **Restructures data into modular blocks** (visual cards)
3. **Stores only visual metadata** (position, size, z-index)
4. **Links to canonical sources** (recipe_id, grocery_list_id, meal_plan_id)

```
┌─────────────────────────────────────────────────┐
│   WHITEBOARD LAYER (New - Visual Organization)  │
│   • Positions (x, y, width, height)             │
│   • Visual styling (colors, borders)            │
│   • Comments & tags (organization)              │
│   • Links to source data                        │
└──────────────┬──────────────────────────────────┘
               │ References by ID
               ↓
┌─────────────────────────────────────────────────┐
│   EXISTING DATA LAYER (Already built!)          │
│   • Recipes table (title, ingredients, steps)   │
│   • Meal Plans (days, meals, recipes)           │
│   • Grocery Lists (items, sections, checked)    │
│   • Users & Households (auth, permissions)      │
└─────────────────────────────────────────────────┘
```

### **Modular Block System:**

Each "block" on the canvas is a **lightweight reference** to existing data:

```javascript
// Whiteboard Object (Modular Block)
{
  id: 1001,                    // Whiteboard object ID
  wid: 123,                    // Whiteboard ID
  t: 'rc',                     // Type: 'rc' = recipe card
  rid: 2577,                   // Links to recipes.id = 2577
  p: [250, 300, 300, 400, 1],  // Position: [x, y, width, height, z-index]
  s: {bg: '#fef2f2', ...},     // Visual style
  tags: ['weeknight', 'kids']  // Organization tags
}

// When rendering, fetch actual recipe data:
GET /api/v2/recipes/2577  // Existing V2 endpoint!
→ Returns full recipe (title, ingredients, image, etc.)
```

**Benefits:**
- ✅ **No data duplication** - single source of truth
- ✅ **Automatic updates** - recipe changes appear on whiteboard
- ✅ **Lightweight storage** - only store visual metadata
- ✅ **Fast rendering** - fetch data on-demand (viewport-based)

---

## 🖥️ **FRONTEND ARCHITECTURE: REACT FLOW + MOBILE VIEWS**

### **Platform-Specific Experiences:**

```
DESKTOP/LAPTOP (React Flow Canvas):
→ Full visual canvas with draggable blocks
→ Create, organize, connect blocks
→ Mouse precision for layout
→ Primary creation environment

TABLET (Touch-Optimized React Flow):
→ Simplified canvas with larger touch targets
→ Drag & drop with gestures
→ Light editing capabilities
→ Apple Pencil support (iPad)

PHONE (Structured List View):
→ No canvas - organized sections instead
→ "Recipes", "Grocery Lists", "Meal Plans", "Notes"
→ Tap to view/comment/react
→ Consume & communicate, not organize
```

### **Responsive Strategy:**

```javascript
import { useMediaQuery } from 'react-responsive';
import ReactFlow from 'reactflow';

function WhiteboardApp({ whiteboardId }) {
  const isPhone = useMediaQuery({ maxWidth: 767 });
  const isTablet = useMediaQuery({ minWidth: 768, maxWidth: 1024 });
  const isDesktop = useMediaQuery({ minWidth: 1025 });

  // Load whiteboard data from existing APIs
  const { nodes, edges } = useWhiteboard(whiteboardId);

  if (isPhone) {
    // 📱 PHONE: Structured list (NOT canvas)
    return <WhiteboardMobileView nodes={nodes} />;
  }

  if (isTablet) {
    // 📟 TABLET: Touch-optimized canvas
    return <WhiteboardTabletCanvas nodes={nodes} touchMode />;
  }

  // 💻 DESKTOP: Full React Flow canvas
  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      nodeTypes={modularBlockTypes}  // Custom block components
    >
      <Background />
      <Controls />
      <MiniMap />
    </ReactFlow>
  );
}
```

## 📊 **DATABASE SCHEMA**

### **New Tables (4 Core Tables)**

```sql
-- ============================================
-- 1. WHITEBOARDS (Top-Level Container)
-- ============================================

CREATE TABLE whiteboards (
    id SERIAL PRIMARY KEY,
    household_id INTEGER NOT NULL REFERENCES households(id) ON DELETE CASCADE,
    
    -- Metadata
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template_type VARCHAR(50),  -- 'weekly_planner', 'party_board', 'freeform'
    
    -- Canvas Settings (JSONB for flexibility)
    canvas_data JSONB DEFAULT '{
        "viewport": {"x": 0, "y": 0, "zoom": 1.0},
        "background": {"color": "#ffffff", "pattern": "dots"},
        "grid": {"enabled": true, "size": 20, "snap": true}
    }'::jsonb,
    
    -- Ownership & Timestamps
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_activity_at TIMESTAMP DEFAULT NOW(),
    
    -- Soft Delete Support
    deleted_at TIMESTAMP,
    
    CONSTRAINT valid_template_type CHECK (
        template_type IN ('weekly_planner', 'party_board', 'freeform', 'meal_prep', 'custom')
    )
);

-- Indexes for performance
CREATE INDEX idx_wb_household ON whiteboards(household_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_wb_created_by ON whiteboards(created_by);
CREATE INDEX idx_wb_activity ON whiteboards(last_activity_at DESC);


-- ============================================
-- 2. WHITEBOARD OBJECTS (Canvas Items)
-- ============================================

CREATE TABLE whiteboard_objects (
    id SERIAL PRIMARY KEY,
    whiteboard_id INTEGER NOT NULL REFERENCES whiteboards(id) ON DELETE CASCADE,
    
    -- Object Classification
    object_type VARCHAR(50) NOT NULL,
    
    -- Polymorphic References (link to existing entities)
    recipe_id INTEGER REFERENCES recipes(id) ON DELETE SET NULL,
    grocery_list_id INTEGER REFERENCES grocery_lists(id) ON DELETE SET NULL,
    meal_plan_id INTEGER REFERENCES meal_plans(id) ON DELETE SET NULL,
    
    -- Visual Properties (JSONB for flexibility)
    position JSONB NOT NULL DEFAULT '{
        "x": 0,
        "y": 0,
        "width": 300,
        "height": 400,
        "z_index": 0,
        "rotation": 0
    }'::jsonb,
    
    -- Styling (colors, borders, shadows)
    style_data JSONB DEFAULT '{
        "backgroundColor": "#ffffff",
        "borderColor": "#e5e7eb",
        "borderWidth": 1,
        "borderRadius": 8,
        "shadow": true
    }'::jsonb,
    
    -- Freeform Content (for notes, images, etc.)
    content JSONB DEFAULT '{}'::jsonb,
    -- Examples:
    -- Note: {"type": "note", "text": "Buy extra avocados", "color": "yellow"}
    -- Image: {"type": "image", "url": "https://...", "caption": "Inspiration"}
    -- Connector: {"type": "connector", "from": 123, "to": 456, "style": "arrow"}
    
    -- Metadata
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Lock for collaborative editing
    locked_by INTEGER REFERENCES users(id),
    locked_at TIMESTAMP,
    
    CONSTRAINT valid_object_type CHECK (
        object_type IN ('recipe', 'grocery_list', 'meal_plan', 'note', 'image', 'connector', 'section')
    ),
    
    -- Ensure polymorphic integrity (only one reference)
    CONSTRAINT single_entity_reference CHECK (
        (recipe_id IS NOT NULL)::int + 
        (grocery_list_id IS NOT NULL)::int + 
        (meal_plan_id IS NOT NULL)::int <= 1
    )
);

-- Indexes
CREATE INDEX idx_wbo_whiteboard ON whiteboard_objects(whiteboard_id);
CREATE INDEX idx_wbo_recipe ON whiteboard_objects(recipe_id) WHERE recipe_id IS NOT NULL;
CREATE INDEX idx_wbo_grocery ON whiteboard_objects(grocery_list_id) WHERE grocery_list_id IS NOT NULL;
CREATE INDEX idx_wbo_meal_plan ON whiteboard_objects(meal_plan_id) WHERE meal_plan_id IS NOT NULL;
CREATE INDEX idx_wbo_type ON whiteboard_objects(object_type);
CREATE INDEX idx_wbo_created_by ON whiteboard_objects(created_by);

-- GIN index for JSONB queries
CREATE INDEX idx_wbo_position ON whiteboard_objects USING GIN(position);
CREATE INDEX idx_wbo_content ON whiteboard_objects USING GIN(content);


-- ============================================
-- 3. WHITEBOARD COMMENTS (Threaded Discussion)
-- ============================================

CREATE TABLE whiteboard_comments (
    id SERIAL PRIMARY KEY,
    
    -- Comment Target (object-level)
    whiteboard_object_id INTEGER NOT NULL REFERENCES whiteboard_objects(id) ON DELETE CASCADE,
    
    -- Threading Support
    parent_comment_id INTEGER REFERENCES whiteboard_comments(id) ON DELETE CASCADE,
    thread_depth INTEGER DEFAULT 0,  -- Calculated on insert
    
    -- Comment Content
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    
    -- Reactions (JSONB for flexibility)
    reactions JSONB DEFAULT '{}'::jsonb,
    -- Example: {"👍": [1, 5, 12], "❤️": [3, 7], "😂": [9]}
    
    -- Mentions
    mentioned_users INTEGER[] DEFAULT ARRAY[]::INTEGER[],
    
    -- Status
    is_resolved BOOLEAN DEFAULT false,
    resolved_by INTEGER REFERENCES users(id),
    resolved_at TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    edited_at TIMESTAMP,
    
    -- Soft Delete
    deleted_at TIMESTAMP
);

-- Indexes
CREATE INDEX idx_wbc_object ON whiteboard_comments(whiteboard_object_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_wbc_user ON whiteboard_comments(user_id);
CREATE INDEX idx_wbc_parent ON whiteboard_comments(parent_comment_id) WHERE parent_comment_id IS NOT NULL;
CREATE INDEX idx_wbc_created ON whiteboard_comments(created_at DESC);

-- GIN index for array searches (mentions)
CREATE INDEX idx_wbc_mentions ON whiteboard_comments USING GIN(mentioned_users);


-- ============================================
-- 4. WHITEBOARD COLLABORATORS (Presence Tracking)
-- ============================================

CREATE TABLE whiteboard_collaborators (
    whiteboard_id INTEGER NOT NULL REFERENCES whiteboards(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Permissions (inherited from household, but can be overridden)
    role VARCHAR(20) DEFAULT 'editor',
    
    -- Presence Tracking
    is_active BOOLEAN DEFAULT false,
    last_seen_at TIMESTAMP DEFAULT NOW(),
    
    -- Live Cursor Position
    cursor_position JSONB,
    -- Example: {"x": 250, "y": 300, "viewport": {"x": 0, "y": 0, "zoom": 1.0}}
    
    -- Activity Tracking
    current_object_id INTEGER REFERENCES whiteboard_objects(id) ON DELETE SET NULL,
    activity_status VARCHAR(50),  -- 'viewing', 'editing', 'commenting'
    
    -- User Info Cache (for quick display)
    user_name VARCHAR(255),
    user_avatar JSONB,
    
    -- Timestamps
    joined_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    PRIMARY KEY (whiteboard_id, user_id),
    
    CONSTRAINT valid_role CHECK (
        role IN ('owner', 'editor', 'viewer')
    )
);

-- Indexes
CREATE INDEX idx_wbcol_whiteboard ON whiteboard_collaborators(whiteboard_id);
CREATE INDEX idx_wbcol_user ON whiteboard_collaborators(user_id);
CREATE INDEX idx_wbcol_active ON whiteboard_collaborators(whiteboard_id, is_active) WHERE is_active = true;
CREATE INDEX idx_wbcol_updated ON whiteboard_collaborators(updated_at DESC);


-- ============================================
-- 5. WHITEBOARD_CHANGE_LOG (Optional - For Undo/History)
-- ============================================

CREATE TABLE whiteboard_change_log (
    id SERIAL PRIMARY KEY,
    whiteboard_id INTEGER NOT NULL REFERENCES whiteboards(id) ON DELETE CASCADE,
    
    -- Change Details
    change_type VARCHAR(50) NOT NULL,  -- 'create', 'update', 'delete', 'move'
    object_id INTEGER,  -- whiteboard_objects.id (can be null if object deleted)
    
    -- Change Data (before/after state)
    before_state JSONB,
    after_state JSONB,
    
    -- User Info
    user_id INTEGER REFERENCES users(id),
    user_name VARCHAR(255),
    
    -- Timestamp
    changed_at TIMESTAMP DEFAULT NOW(),
    
    -- Batch ID (for grouping simultaneous changes)
    batch_id UUID DEFAULT gen_random_uuid()
);

-- Indexes
CREATE INDEX idx_wbcl_whiteboard ON whiteboard_change_log(whiteboard_id);
CREATE INDEX idx_wbcl_changed_at ON whiteboard_change_log(changed_at DESC);
CREATE INDEX idx_wbcl_batch ON whiteboard_change_log(batch_id);

-- Partition by month for performance (optional, for future scaling)
-- CREATE TABLE whiteboard_change_log_YYYY_MM PARTITION OF whiteboard_change_log
--   FOR VALUES FROM ('YYYY-MM-01') TO ('YYYY-MM+1-01');
```

---

## 🔄 **DATABASE TRIGGERS & FUNCTIONS**

```sql
-- ============================================
-- Auto-update timestamps
-- ============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_whiteboards_updated_at BEFORE UPDATE ON whiteboards
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_whiteboard_objects_updated_at BEFORE UPDATE ON whiteboard_objects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_whiteboard_comments_updated_at BEFORE UPDATE ON whiteboard_comments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ============================================
-- Update whiteboard last_activity_at on any change
-- ============================================

CREATE OR REPLACE FUNCTION update_whiteboard_activity()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE whiteboards 
    SET last_activity_at = NOW() 
    WHERE id = NEW.whiteboard_id;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_activity_on_object_change AFTER INSERT OR UPDATE ON whiteboard_objects
    FOR EACH ROW EXECUTE FUNCTION update_whiteboard_activity();


-- ============================================
-- Calculate comment thread depth
-- ============================================

CREATE OR REPLACE FUNCTION calculate_thread_depth()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.parent_comment_id IS NULL THEN
        NEW.thread_depth = 0;
    ELSE
        SELECT thread_depth + 1 INTO NEW.thread_depth
        FROM whiteboard_comments
        WHERE id = NEW.parent_comment_id;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER set_comment_thread_depth BEFORE INSERT ON whiteboard_comments
    FOR EACH ROW EXECUTE FUNCTION calculate_thread_depth();


-- ============================================
-- Log changes for undo/redo
-- ============================================

CREATE OR REPLACE FUNCTION log_whiteboard_change()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO whiteboard_change_log (whiteboard_id, change_type, object_id, before_state, user_id)
        VALUES (OLD.whiteboard_id, 'delete', OLD.id, row_to_json(OLD), OLD.created_by);
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO whiteboard_change_log (whiteboard_id, change_type, object_id, before_state, after_state, user_id)
        VALUES (NEW.whiteboard_id, 'update', NEW.id, row_to_json(OLD), row_to_json(NEW), NEW.created_by);
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO whiteboard_change_log (whiteboard_id, change_type, object_id, after_state, user_id)
        VALUES (NEW.whiteboard_id, 'create', NEW.id, row_to_json(NEW), NEW.created_by);
        RETURN NEW;
    END IF;
END;
$$ language 'plpgsql';

CREATE TRIGGER log_object_changes AFTER INSERT OR UPDATE OR DELETE ON whiteboard_objects
    FOR EACH ROW EXECUTE FUNCTION log_whiteboard_change();
```

---

## 🌐 **API ENDPOINT SPECIFICATION**

### **Complete Endpoint List (24 Endpoints)**

```python
# ========================================
# WHITEBOARD CRUD (5 endpoints)
# ========================================

GET    /api/v2/whiteboards/household/<household_id>
POST   /api/v2/whiteboards
GET    /api/v2/whiteboards/<whiteboard_id>
PATCH  /api/v2/whiteboards/<whiteboard_id>
DELETE /api/v2/whiteboards/<whiteboard_id>


# ========================================
# OBJECT MANAGEMENT (7 endpoints)
# ========================================

POST   /api/v2/whiteboards/<whiteboard_id>/objects
PATCH  /api/v2/whiteboards/<whiteboard_id>/objects/<object_id>
DELETE /api/v2/whiteboards/<whiteboard_id>/objects/<object_id>
PATCH  /api/v2/whiteboards/<whiteboard_id>/objects/bulk-update
POST   /api/v2/whiteboards/<whiteboard_id>/objects/<object_id>/link
POST   /api/v2/whiteboards/<whiteboard_id>/objects/<object_id>/sync
POST   /api/v2/whiteboards/<whiteboard_id>/objects/from-recipe


# ========================================
# COMMENTING SYSTEM (5 endpoints)
# ========================================

GET    /api/v2/whiteboards/objects/<object_id>/comments
POST   /api/v2/whiteboards/objects/<object_id>/comments
PATCH  /api/v2/whiteboards/comments/<comment_id>
DELETE /api/v2/whiteboards/comments/<comment_id>
POST   /api/v2/whiteboards/comments/<comment_id>/react


# ========================================
# REAL-TIME COLLABORATION (4 endpoints)
# ========================================

GET    /api/v2/whiteboards/<whiteboard_id>/collaborators
POST   /api/v2/whiteboards/<whiteboard_id>/presence
POST   /api/v2/whiteboards/<whiteboard_id>/subscribe
GET    /api/v2/whiteboards/<whiteboard_id>/history


# ========================================
# TEMPLATES & UTILITIES (3 endpoints)
# ========================================

GET    /api/v2/whiteboards/templates
POST   /api/v2/whiteboards/<whiteboard_id>/duplicate
GET    /api/v2/whiteboards/<whiteboard_id>/export
```

### **Detailed Endpoint Specifications:**

#### **1. Get Household Whiteboards**
```python
GET /api/v2/whiteboards/household/<household_id>

# Query Parameters:
# - include_deleted: boolean (default: false)
# - sort_by: string ('activity' | 'created' | 'name')
# - limit: integer (default: 50)

# Response:
{
    "success": true,
    "data": {
        "whiteboards": [
            {
                "id": 123,
                "household_id": 456,
                "name": "Weekly Meal Plan",
                "description": "Our family's weekly meals",
                "template_type": "weekly_planner",
                "created_by": 789,
                "created_at": "2025-11-01T10:00:00Z",
                "last_activity_at": "2025-11-01T15:30:00Z",
                "object_count": 15,
                "active_collaborators": 2
            }
        ],
        "total_count": 5
    }
}

# Authorization: User must be household member
```

#### **2. Create Whiteboard**
```python
POST /api/v2/whiteboards

# Request Body:
{
    "household_id": 456,
    "name": "Thanksgiving Planning",
    "description": "Holiday meal coordination",
    "template_type": "party_board",  # Optional
    "canvas_data": {  # Optional, defaults provided
        "viewport": {"x": 0, "y": 0, "zoom": 1.0},
        "background": {"color": "#fff8f0", "pattern": "dots"}
    }
}

# Response:
{
    "success": true,
    "data": {
        "whiteboard": {
            "id": 124,
            "household_id": 456,
            "name": "Thanksgiving Planning",
            ...
        },
        "template_objects": [  # If template_type provided
            {
                "id": 999,
                "object_type": "section",
                "position": {"x": 100, "y": 100, "width": 400, "height": 300},
                "content": {"text": "Main Dishes", "color": "#fef2f2"}
            }
        ]
    }
}

# Authorization: User must be household member with 'editor' or 'owner' role
```

#### **3. Get Whiteboard Full Data**
```python
GET /api/v2/whiteboards/<whiteboard_id>

# Query Parameters:
# - include_comments: boolean (default: false)
# - include_history: boolean (default: false)

# Response:
{
    "success": true,
    "data": {
        "whiteboard": {
            "id": 123,
            "household_id": 456,
            "name": "Weekly Meal Plan",
            ...
        },
        "objects": [
            {
                "id": 1001,
                "object_type": "recipe",
                "recipe_id": 2577,
                "position": {"x": 250, "y": 300, "width": 300, "height": 400},
                "style_data": {"backgroundColor": "#fef2f2"},
                "recipe": {  # Populated from recipes table
                    "id": 2577,
                    "title": "Chicken Tacos",
                    "image_url": "https://...",
                    "prep_time": 15,
                    "cook_time": 20
                },
                "created_by": 789,
                "created_at": "2025-11-01T10:00:00Z"
            },
            {
                "id": 1002,
                "object_type": "note",
                "position": {"x": 600, "y": 300, "width": 250, "height": 150},
                "content": {
                    "type": "note",
                    "text": "Remember to buy extra cilantro!",
                    "color": "yellow"
                }
            }
        ],
        "collaborators": [
            {
                "user_id": 789,
                "user_name": "Mom",
                "role": "owner",
                "is_active": true,
                "cursor_position": {"x": 450, "y": 500}
            }
        ],
        "comments": [  # If include_comments=true
            {
                "id": 5001,
                "whiteboard_object_id": 1001,
                "user_id": 790,
                "user_name": "Dad",
                "content": "Should we double this recipe?",
                "reactions": {"👍": [789, 791]},
                "created_at": "2025-11-01T12:00:00Z"
            }
        ]
    }
}
```

#### **4. Create Whiteboard Object**
```python
POST /api/v2/whiteboards/<whiteboard_id>/objects

# Request Body (Recipe Card):
{
    "object_type": "recipe",
    "recipe_id": 2577,
    "position": {"x": 250, "y": 300, "width": 300, "height": 400},
    "style_data": {  # Optional
        "backgroundColor": "#fef2f2",
        "borderColor": "#fca5a5"
    }
}

# Request Body (Sticky Note):
{
    "object_type": "note",
    "position": {"x": 600, "y": 300, "width": 250, "height": 150},
    "content": {
        "type": "note",
        "text": "Buy extra avocados 🥑",
        "color": "yellow"
    }
}

# Response:
{
    "success": true,
    "data": {
        "object": {
            "id": 1003,
            "whiteboard_id": 123,
            "object_type": "recipe",
            "recipe_id": 2577,
            "position": {...},
            "recipe": {...}  # Populated
        }
    }
}
```

#### **5. Bulk Update Objects (Drag Operation)**
```python
PATCH /api/v2/whiteboards/<whiteboard_id>/objects/bulk-update

# Request Body:
{
    "updates": [
        {
            "object_id": 1001,
            "position": {"x": 300, "y": 350}  # Only changed properties
        },
        {
            "object_id": 1002,
            "position": {"x": 650, "y": 350}
        }
    ],
    "batch_id": "uuid-v4-here"  # For change log grouping
}

# Response:
{
    "success": true,
    "data": {
        "updated_count": 2,
        "objects": [...]  # Updated objects with full data
    }
}

# Note: Optimized for drag operations (minimal validation, fast response)
```

#### **6. Add Comment to Object**
```python
POST /api/v2/whiteboards/objects/<object_id>/comments

# Request Body:
{
    "content": "Should we make this recipe on Tuesday instead?",
    "parent_comment_id": null,  # null for top-level, id for reply
    "mentioned_users": [790, 791]  # User IDs for @mentions
}

# Response:
{
    "success": true,
    "data": {
        "comment": {
            "id": 5002,
            "whiteboard_object_id": 1001,
            "user_id": 789,
            "user_name": "Mom",
            "content": "Should we make this recipe on Tuesday instead?",
            "mentioned_users": [790, 791],
            "thread_depth": 0,
            "created_at": "2025-11-01T14:00:00Z"
        }
    }
}

# Side Effect: Notifications sent to mentioned users
```

#### **7. Update Presence (Real-Time)**
```python
POST /api/v2/whiteboards/<whiteboard_id>/presence

# Request Body:
{
    "cursor_position": {"x": 450, "y": 500},
    "current_object_id": 1001,  # Object being edited/viewed
    "activity_status": "editing"  # 'viewing' | 'editing' | 'commenting'
}

# Response:
{
    "success": true,
    "data": {
        "acknowledged": true,
        "collaborators": [  # All active collaborators
            {
                "user_id": 789,
                "user_name": "Mom",
                "cursor_position": {"x": 450, "y": 500},
                "activity_status": "editing"
            },
            {
                "user_id": 790,
                "user_name": "Dad",
                "cursor_position": {"x": 200, "y": 300},
                "activity_status": "viewing"
            }
        ]
    }
}

# Note: Called every 1-2 seconds by active clients
```

---

## 🔌 **WEBSOCKET EVENT SCHEMA**

### **Connection & Authentication:**
```javascript
// Client connects to WebSocket
const socket = io('wss://yeschefapp-production.up.railway.app', {
    auth: {
        token: 'jwt-token-here'
    },
    query: {
        whiteboard_id: 123
    }
});

// Server validates JWT and whiteboard access
// On success: joins room 'whiteboard_123'
```

### **Event Types (Client → Server):**
```javascript
// 1. Join Whiteboard Room
socket.emit('join_whiteboard', {
    whiteboard_id: 123,
    user_info: {
        name: 'Mom',
        avatar: {background: '#fef2f2', icon: '👩‍🍳'}
    }
});

// 2. Update Cursor Position
socket.emit('cursor_move', {
    whiteboard_id: 123,
    position: {x: 450, y: 500}
});

// 3. Object Created/Updated/Deleted
socket.emit('object_change', {
    whiteboard_id: 123,
    change_type: 'update',  // 'create' | 'update' | 'delete' | 'move'
    object_id: 1001,
    data: {
        position: {x: 300, y: 350}
    }
});

// 4. Comment Added
socket.emit('comment_add', {
    whiteboard_id: 123,
    object_id: 1001,
    comment: {
        content: "Looks great!",
        user_id: 789
    }
});

// 5. User Typing (Comment Box)
socket.emit('typing_start', {
    whiteboard_id: 123,
    object_id: 1001,
    user_id: 789
});

// 6. Leave Whiteboard
socket.emit('leave_whiteboard', {
    whiteboard_id: 123
});
```

### **Event Types (Server → Client):**
```javascript
// 1. User Joined
socket.on('user_joined', (data) => {
    // data: {user_id, user_name, user_avatar, joined_at}
    showUserJoinedNotification(data);
});

// 2. User Left
socket.on('user_left', (data) => {
    // data: {user_id, user_name}
    removeUserCursor(data.user_id);
});

// 3. Cursor Updated
socket.on('cursor_update', (data) => {
    // data: {user_id, position: {x, y}}
    updateUserCursor(data.user_id, data.position);
});

// 4. Object Changed
socket.on('object_changed', (data) => {
    // data: {change_type, object_id, object_data, changed_by}
    updateCanvasObject(data);
});

// 5. Comment Added
socket.on('comment_added', (data) => {
    // data: {comment_id, object_id, comment_data}
    addCommentToThread(data);
});

// 6. User Typing Indicator
socket.on('user_typing', (data) => {
    // data: {user_id, object_id}
    showTypingIndicator(data);
});

// 7. Sync Request (Conflict Resolution)
socket.on('sync_required', (data) => {
    // Server detected conflict, requesting full refresh
    fetchWhiteboardFullData();
});
```

### **Error Handling:**
```javascript
socket.on('error', (error) => {
    // error: {code, message, action}
    switch(error.code) {
        case 'AUTH_FAILED':
            redirectToLogin();
            break;
        case 'PERMISSION_DENIED':
            showError('You do not have edit permissions');
            switchToReadOnlyMode();
            break;
        case 'WHITEBOARD_NOT_FOUND':
            redirectToWhiteboardList();
            break;
        case 'RATE_LIMIT_EXCEEDED':
            showWarning('Slow down! Too many updates.');
            break;
    }
});
```

---

## 📦 **DATA MODELS & TYPES**

### **Core Concept: Lightweight References**

Whiteboard objects are **lightweight pointers** to existing data:

```typescript
// ============================================
// Whiteboard Object (Modular Block)
// ============================================

interface WhiteboardObject {
  id: number;                    // Whiteboard object ID
  wid: number;                   // Whiteboard ID
  t: ObjectType;                 // Type of block
  
  // POLYMORPHIC REFERENCES (link to existing data)
  rid?: number;                  // recipe_id → /api/v2/recipes/{rid}
  gid?: number;                  // grocery_list_id → /api/v2/grocery-lists/{gid}
  mid?: number;                  // meal_plan_id → /api/v2/meal-plans/{mid}
  
  // VISUAL METADATA (only stored in whiteboard)
  p: [number, number, number, number, number];  // [x, y, w, h, z]
  s: ObjectStyle;                // Visual styling
  tags?: string[];               // Organization tags ["weeknight", "kids"]
  
  // FREEFORM CONTENT (for notes only - no external reference)
  c?: NoteContent | ImageContent;
  
  // METADATA
  cby: number;                   // created_by user_id
  ca: string;                    // created_at timestamp
  ua: string;                    // updated_at timestamp
}

type ObjectType = 'rc' | 'gl' | 'mp' | 'nt' | 'im' | 'cn' | 'sc';
// rc = recipe card (links to recipe)
// gl = grocery list (links to list)
// mp = meal plan (links to plan)
// nt = note (freeform, no link)
// im = image (freeform, no link)
// cn = connector (visual line)
// sc = section (visual grouping)

// ============================================
// Rendering Flow: Fetch on Demand
// ============================================

// 1. Load whiteboard objects (lightweight)
const objects = await fetch('/api/v2/wb/123');  // Compact metadata only

// 2. Extract IDs of visible objects
const visibleObjects = getObjectsInViewport(viewport);
const recipeIds = visibleObjects
  .filter(obj => obj.t === 'rc')
  .map(obj => obj.rid);

// 3. Batch fetch actual data from existing APIs
const recipes = await fetch(`/api/v2/recipes?ids=${recipeIds.join(',')}`);

// 4. Merge visual metadata + actual data
const renderedBlocks = visibleObjects.map(obj => ({
  ...obj,                        // Visual metadata (position, style, tags)
  data: recipes[obj.rid]         // Actual recipe data (title, ingredients, etc.)
}));

// 5. Render React Flow nodes
<ReactFlow nodes={renderedBlocks} />
```

### **Example: Recipe Block Rendering**

```typescript
// Whiteboard stores THIS (lightweight):
{
  id: 1001,
  wid: 123,
  t: 'rc',                       // Recipe card
  rid: 2577,                     // Links to recipe #2577
  p: [250, 300, 300, 400, 1],    // Position
  s: {bg: '#fef2f2'},            // Style
  tags: ['weeknight', 'mexican'] // Organization
}

// Component fetches THIS from existing API:
GET /api/v2/recipes/2577
→ {
  id: 2577,
  title: 'Chicken Tacos',
  ingredients: [...],
  instructions: [...],
  image_url: 'https://...',
  prep_time: 15,
  cook_time: 20,
  servings: 4
}

// React component combines both:
function RecipeBlock({ whiteboardObject }) {
  const recipe = useFetchRecipe(whiteboardObject.rid);  // Existing API!
  
  return (
    <div style={{
      position: 'absolute',
      left: whiteboardObject.p[0],
      top: whiteboardObject.p[1],
      width: whiteboardObject.p[2],
      height: whiteboardObject.p[3],
      background: whiteboardObject.s.bg
    }}>
      <img src={recipe.image_url} />
      <h3>{recipe.title}</h3>
      <p>⏱️ {recipe.prep_time + recipe.cook_time} min</p>
      <TagList tags={whiteboardObject.tags} />
    </div>
  );
}
```

### **Benefits of This Architecture:**

✅ **No Data Duplication**
- Recipe title changes → automatically updated on whiteboard
- Grocery list checked items → real-time sync
- Meal plan changes → reflected immediately

✅ **Lightweight Storage**
- Whiteboard table: ~220 bytes per object
- Recipe table: Unchanged (1-5 KB per recipe)
- Total overhead: Minimal

✅ **Fast Rendering**
- Only fetch visible objects (viewport-based)
- Batch API calls (one request for 10 recipes)
- Cache fetched data (React Query)

✅ **Single Source of Truth**
- `/api/v2/recipes/2577` is authoritative
- Whiteboard just displays it visually
- Updates happen in one place

---

## 🎨 **UI COMPONENT HIERARCHY**

### **Desktop/Tablet: React Flow Canvas**

```
WhiteboardApp (Page)
│
├── WhiteboardToolbar (Top Bar)
│   ├── BoardSelector (Dropdown)
│   ├── AddBlockMenu (+ Button) → Search existing data
│   │   ├── SearchRecipes → Links to existing recipes
│   │   ├── AddGroceryList → Links to existing list
│   │   ├── AddMealPlan → Links to existing plan
│   │   └── CreateNote → New freeform content
│   ├── ViewControls (Zoom, Pan, Fit)
│   └── ShareButton
│
├── WhiteboardSidebar (Left Panel)
│   ├── BlockList (All objects on canvas)
│   ├── TagFilter (Filter by organization tags)
│   └── ActivityFeed (Recent changes)
│
├── ReactFlowCanvas (Main Area) ⭐
│   ├── Modular Blocks (Custom Nodes)
│   │   │
│   │   ├── RecipeBlock → Displays recipe from /api/v2/recipes/{id}
│   │   │   ├── RecipeThumbnail (from recipe.image_url)
│   │   │   ├── RecipeTitle (from recipe.title)
│   │   │   ├── RecipeMetadata (prep_time, servings)
│   │   │   ├── Tags (organization: "weeknight", "kids")
│   │   │   └── Actions (Comment, Add to Plan, React)
│   │   │
│   │   ├── GroceryListBlock → Displays list from /api/v2/grocery-lists/{id}
│   │   │   ├── ListHeader (name)
│   │   │   ├── ItemCheckboxes (live sync on check/uncheck)
│   │   │   └── SyncIndicator (real-time updates)
│   │   │
│   │   ├── MealPlanBlock → Displays plan from /api/v2/meal-plans/{id}
│   │   │   ├── WeekGrid (days × meals)
│   │   │   ├── MealSlots (links to recipe blocks)
│   │   │   └── DropZones (drag recipe here → update plan)
│   │   │
│   │   └── NoteBlock → Freeform content (stored in whiteboard)
│   │       ├── EditableText (markdown support)
│   │       ├── ColorPicker (yellow, blue, green, pink)
│   │       └── ResizeHandles
│   │
│   ├── ConnectionLines (show relationships)
│   ├── UserCursors (live collaborator positions)
│   └── SelectionBox (multi-select)
│
├── CommentPanel (Right Slide-out)
│   ├── CommentThread (per object)
│   │   ├── CommentItem
│   │   │   ├── UserAvatar
│   │   │   ├── CommentText (@mention support)
│   │   │   ├── ReactionBar (👍 ❤️ 😂)
│   │   │   └── ReplyButton
│   │   └── CommentInput (markdown, @mentions)
│   └── ResolvedToggle
│
└── CollaboratorBar (Bottom)
    ├── ActiveUsers (avatar list)
    └── PresenceIndicators
```

### **Phone: Structured List View (NOT Canvas)**

```
WhiteboardMobileView (Page)
│
├── Header
│   ├── BackButton
│   ├── WhiteboardTitle
│   └── ShareButton
│
├── CollaboratorBar (Who's active)
│   └── AvatarRow (Mom 🟢, Dad 🟢, Kids 🟠)
│
├── QuickActionsBar
│   ├── [💬 Comment]
│   ├── [🔗 Share]
│   └── [💻 Open on Desktop]
│
├── ScrollView (Organized Sections)
│   │
│   ├── Section: Recipes (🍳)
│   │   ├── RecipeCard → Tap to view details
│   │   │   ├── Thumbnail
│   │   │   ├── Title
│   │   │   ├── Metadata
│   │   │   └── [💬 3] [❤️ 2] (comment/reaction counts)
│   │   └── RecipeCard...
│   │
│   ├── Section: Grocery Lists (🛒)
│   │   ├── GroceryListCard → Tap to check items
│   │   │   ├── ListName
│   │   │   ├── Progress (✓ 12 of 24)
│   │   │   └── [View List]
│   │   └── GroceryListCard...
│   │
│   ├── Section: Meal Plans (📅)
│   │   ├── MealPlanCard → Tap to view plan
│   │   │   ├── PlanName
│   │   │   ├── Preview (Mon: Tacos, Tue: Pasta...)
│   │   │   └── [View Plan]
│   │   └── MealPlanCard...
│   │
│   ├── Section: Notes (📝)
│   │   ├── NoteCard → Tap to edit
│   │   │   ├── NoteText (preview)
│   │   │   └── [Edit]
│   │   └── NoteCard...
│   │
│   └── Section: Recent Activity (💬)
│       ├── ActivityItem (Mom: "Added tomatoes")
│       ├── ActivityItem (Dad: "Can we switch Mon?")
│       └── ActivityItem (Kids: ❤️ reacted)
│
└── FloatingActionButton (+)
    └── [Add Comment]
```

**Key Difference:**
- **Desktop/Tablet:** Visual canvas (React Flow) - spatial organization
- **Phone:** Structured list (ScrollView) - categorical organization
- **Both:** Same data, different visualization!

---

**Next Document:** 03_IMPLEMENTATION_PLAN.md (Phased development roadmap with timelines)
