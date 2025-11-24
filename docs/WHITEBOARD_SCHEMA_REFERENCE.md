# Whiteboard Schema Reference
**Quick reference for whiteboard database schema**

## Tables Overview

### `wb` - Whiteboards
```sql
id          SERIAL PRIMARY KEY
hid         INTEGER NOT NULL REFERENCES households(id)  -- household_id
n           VARCHAR(255) NOT NULL                       -- name
d           TEXT                                        -- description
tt          VARCHAR(50)                                 -- template_type
cs          JSONB DEFAULT '{}'                          -- canvas_settings {vp: [x,y,zoom]}
ca          TIMESTAMP DEFAULT NOW()                     -- created_at
ua          TIMESTAMP DEFAULT NOW()                     -- updated_at
laa         TIMESTAMP DEFAULT NOW()                     -- last_activity_at
cby         INTEGER REFERENCES users(id)                -- created_by
deleted_at  TIMESTAMP
deleted_by  INTEGER REFERENCES users(id)
```

### `wbo` - Whiteboard Objects
```sql
id          SERIAL PRIMARY KEY
wid         INTEGER NOT NULL REFERENCES wb(id)          -- whiteboard_id

-- Object Type
t           VARCHAR(10) NOT NULL                        -- type: 'rc', 'gl', 'mp', 'nt', 'im', 'cn', 'sc'

-- Entity References (polymorphic - only ONE should be set)
rid         INTEGER REFERENCES recipes(id)              -- recipe_id
gid         INTEGER REFERENCES grocery_lists(id)        -- grocery_list_id  
mid         INTEGER REFERENCES meal_plans(id)           -- meal_plan_id

-- Visual Properties
p           JSONB NOT NULL DEFAULT '[0,0,300,400,0]'    -- position [x, y, width, height, z]
s           JSONB DEFAULT '{"bg":"#fff",...}'           -- style {bg, bc, bw, br}

-- Organization
tags        TEXT[]                                      -- ['tag1', 'tag2']

-- Content (for notes/images only)
c           JSONB DEFAULT '{}'                          -- content

-- Audit
cby         INTEGER NOT NULL REFERENCES users(id)       -- created_by
ca          TIMESTAMP DEFAULT NOW()                     -- created_at
ua          TIMESTAMP DEFAULT NOW()                     -- updated_at

-- Collaboration
lby         INTEGER REFERENCES users(id)                -- locked_by
lat         TIMESTAMP                                   -- locked_at

-- Soft Delete
deleted_at  TIMESTAMP
deleted_by  INTEGER REFERENCES users(id)

CONSTRAINT wbo_valid_type CHECK (t IN ('rc','gl','mp','nt','im','cn','sc'))
CONSTRAINT wbo_position_array CHECK (jsonb_array_length(p) = 5)
```

### `recipes` - Recipes
```sql
id              SERIAL PRIMARY KEY
title           VARCHAR(255) NOT NULL
ingredients     TEXT
instructions    TEXT
user_id         INTEGER REFERENCES users(id)
source          VARCHAR(50)
-- ... other fields
```

### `grocery_lists` - Grocery Lists
```sql
id              SERIAL PRIMARY KEY
name            VARCHAR(255) NOT NULL
items           JSONB NOT NULL                          -- [{name, quantity, checked}]
hid             INTEGER REFERENCES households(id)       -- household_id
wid             INTEGER REFERENCES wb(id)               -- whiteboard_id
wp              JSONB                                   -- widget_position {x, y, size}
lr              INTEGER[]                               -- linked_recipes [rid1, rid2]
user_id         INTEGER REFERENCES users(id)
-- ... other fields
```

### `meal_plans` - Meal Plans
```sql
id              SERIAL PRIMARY KEY
user_id         INTEGER NOT NULL REFERENCES users(id)
plan_name       VARCHAR(255) NOT NULL
week_start_date DATE NOT NULL
plan_data_json  JSONB NOT NULL                          -- {days: {day1: {name, recipes}}}
created_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
updated_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

---

## Object Type Codes

| Code | Type          | Entity Reference | Description                    |
|------|---------------|------------------|--------------------------------|
| `rc` | Recipe Card   | `rid`            | Recipe displayed on whiteboard |
| `gl` | Grocery List  | `gid`            | Grocery list widget            |
| `mp` | Meal Plan     | `mid`            | Meal plan day box              |
| `nt` | Note          | -                | Freeform text note             |
| `im` | Image         | -                | Uploaded image                 |
| `cn` | Connection    | -                | Line connecting objects        |
| `sc` | Section       | -                | Grouping container             |

---

## Frontend ↔ Backend Mapping

### Creating Objects

**Frontend sends:**
```javascript
{
  type: "mp",
  entity_type: "meal_plan",
  entity_id: 123,
  position: {x: 100, y: 200, width: 320, height: 200, z: 0}
}
```

**Backend maps to:**
```sql
INSERT INTO wbo (wid, t, mid, p, ...)
VALUES (3, 'mp', 123, '[100,200,320,200,0]', ...)
```

**Backend returns:**
```json
{
  "success": true,
  "data": {
    "id": 456,
    "type": "mp",
    "entity_type": "meal_plan",
    "entity_id": 123,
    "mid": 123,
    "position": [100, 200, 320, 200, 0]
  }
}
```

### Loading Objects

**Backend query:**
```sql
SELECT id, wid, t, rid, gid, mid, p, c, tags
FROM wbo
WHERE wid = 3 AND deleted_at IS NULL
```

**Backend returns in whiteboard.objects:**
```json
{
  "id": 456,
  "type": "mp",
  "mid": 123,
  "position": [100, 200, 320, 200, 0],
  "rid": null,
  "gid": null
}
```

**Frontend checks:**
```javascript
// For meal plans
if (obj.type === 'mp' || obj.mid) {
  const mealPlanId = obj.mid;
  // Fetch meal plan data
}

// For recipes
if (obj.type === 'rc' || obj.rid) {
  const recipeId = obj.rid;
}

// For grocery lists
if (obj.type === 'gl' || obj.gid) {
  const listId = obj.gid;
}
```

---

## Common Queries

### Get all objects on a whiteboard
```sql
SELECT wbo.*, 
       r.title as recipe_title,
       gl.name as list_name,
       mp.plan_name as meal_plan_name
FROM wbo
LEFT JOIN recipes r ON wbo.rid = r.id
LEFT JOIN grocery_lists gl ON wbo.gid = gl.id  
LEFT JOIN meal_plans mp ON wbo.mid = mp.id
WHERE wbo.wid = 3 AND wbo.deleted_at IS NULL;
```

### Find object by entity
```sql
-- Find recipe card
SELECT * FROM wbo WHERE wid = 3 AND rid = 123;

-- Find grocery list widget
SELECT * FROM wbo WHERE wid = 3 AND gid = 456;

-- Find meal plan day box
SELECT * FROM wbo WHERE wid = 3 AND mid = 789;
```

### Update object position
```sql
UPDATE wbo
SET p = '[200,300,320,200,0]'::jsonb,
    ua = CURRENT_TIMESTAMP
WHERE id = 456;
```

---

## Position Array Format

Position is stored as JSONB array: `[x, y, width, height, z]`

```javascript
[
  100,    // x: horizontal position (canvas coordinates)
  200,    // y: vertical position (canvas coordinates)
  320,    // width: object width in pixels
  200,    // height: object height in pixels
  0       // z: z-index for layering
]
```

### Converting for Frontend
```javascript
// Database → Frontend
const [x, y, width, height, z] = obj.position;
const widgetPosition = { x, y, width, height, z };

// Frontend → Database  
const position = [widget.x, widget.y, widget.width, widget.height, widget.z];
```

---

## API Response Formats

### V2 Whiteboard API (`/api/v2/whiteboard/*`)
**Standard Response:**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "whiteboard_id": 3,
    ...
  }
}
```

**Access:** `response.data.id`, `response.data.whiteboard_id`

---

### V1 Entity APIs (`/api/meal-plans/*`, `/api/recipes/*`)
**Meal Plans Response:**
```json
{
  "success": true,
  "meal_plan": {
    "id": 123,
    "plan_name": "Weekly Plan",
    "meal_data": {...}
  }
}
```

**Access:** `response.meal_plan.id`, `response.meal_plan.plan_name`

**⚠️ Important:** V1 APIs return entities **directly on response**, NOT nested in `response.data`

---

## API Endpoints

### V2 Whiteboard API (`/api/v2/whiteboard`)

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/:hid/whiteboards` | List household whiteboards | ✅ |
| POST | `/` | Create whiteboard | ✅ |
| GET | `/:wid` | Get whiteboard + objects | ✅ |
| PATCH | `/:wid` | Update whiteboard metadata | ⚠️ Stub |
| DELETE | `/:wid` | Delete whiteboard | ✅ |
| POST | `/:wid/o` | Create object | ✅ |
| PATCH | `/:wid/o/:oid` | Update object | ✅ **FIXED!** |
| DELETE | `/:wid/o/:oid` | Delete object | ✅ |
| POST | `/:wid/o/bulk` | Bulk update positions | ✅ |

### V1 Meal Plan API (`/api/meal-plans`)

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| POST | `/` | Create meal plan | ✅ |
| GET | `/` | List meal plans | ✅ |
| GET | `/:id` | Get meal plan | ✅ |
| PUT | `/:id` | Update meal plan | ✅ |
| DELETE | `/:id` | Delete meal plan | ✅ |

---

## Indexing Strategy

```sql
-- Performance indexes
CREATE INDEX idx_wbo_wid ON wbo(wid) WHERE deleted_at IS NULL;
CREATE INDEX idx_wbo_rid ON wbo(rid) WHERE deleted_at IS NULL;
CREATE INDEX idx_wbo_gid ON wbo(gid) WHERE deleted_at IS NULL;
CREATE INDEX idx_wbo_mid ON wbo(mid) WHERE deleted_at IS NULL;
CREATE INDEX idx_wbo_type ON wbo(t) WHERE deleted_at IS NULL;

CREATE INDEX idx_grocery_lists_wid ON grocery_lists(wid) WHERE deleted_at IS NULL;
CREATE INDEX idx_grocery_lists_hid ON grocery_lists(hid) WHERE deleted_at IS NULL;
```

---

## Migration History

- **20251103** - Created `wb`, `wbo` tables with polymorphic references
- **20251104** - Added `hid`, `wid`, `wp`, `lr` to `grocery_lists`
- **Phase 2** - Need to migrate meal plans to V2 structure

---

## Troubleshooting

### Widget saves but doesn't reload
1. Check `wbo` entry exists: `SELECT * FROM wbo WHERE wid=3;`
2. Verify correct entity reference is set (rid/gid/mid)
3. Check load query filters for correct type/column

### "Column does not exist" errors
1. Verify table schema: `\d+ wbo`
2. Don't assume column names match frontend variables
3. Use shortened names: `et` ❌ → `t` ✅

### Position not persisting
1. Ensure position is 5-element array
2. Check JSONB constraint: `jsonb_array_length(p) = 5`
3. Verify UPDATE includes `ua = CURRENT_TIMESTAMP`
