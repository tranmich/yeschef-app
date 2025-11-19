# 📅 Implementation Plan - Whiteboard System

**Date:** November 1, 2025 (Updated: November 3, 2025)  
**Target Launch:** Q2 2026 (6 months)  
**Team Size:** Assuming 1-2 developers

---

## 🎯 **OVERVIEW**

### **What We're Building:**

A **visual interface layer** that connects to existing APIs and restructures data into **modular blocks** that users can:
- 🎨 **Freely move** and organize on a canvas (desktop/tablet)
- 💬 **Comment and discuss** on each block
- 🏷️ **Tag and categorize** for easy sorting/filtering
- 👥 **Collaborate in real-time** with household members
- 📱 **Access differently** per device (canvas vs list view)

### **Key Architectural Principles:**

1. ✅ **No Data Duplication** - Blocks link to existing recipes/plans/lists
2. ✅ **Existing APIs** - Leverage V2 endpoints already built
3. ✅ **Lightweight Storage** - Only store visual metadata (position, style, tags)
4. ✅ **Platform-Specific UX** - Canvas for desktop, list for phone
5. ✅ **Real-Time Sync** - WebSocket layer for collaboration

### **Technology Stack:**

```
Frontend (Desktop/Tablet):
- React Flow (modular block canvas)
- Custom node components (recipe, grocery, meal plan, note)
- Liveblocks (real-time collaboration, comments, presence)
- Tiptap (rich text editor for notes)
- React Color (color picker)
- Stream Chat (household messaging)

Frontend (Phone):
- React Native (YesChefMobile)
- Structured list view (ScrollView + Sections)
- Quick action modals (comment, react, view)
- Stream Chat React Native (mobile messaging)

Backend:
- Flask (existing app)
- PostgreSQL (4 new compact tables)
- V2 REST API endpoints (24 new endpoints)
- Liveblocks auth endpoint (token generation)
- Stream Chat auth endpoint (token generation)

Third-Party Services:
- Liveblocks (real-time collaboration)
  → Comments on objects
  → Activity feed
  → Presence tracking
  → Free: 100 MAU
  
- Stream Chat (household messaging)
  → General household chat
  → DMs between members
  → Push notifications
  → Free: 25 MAU

Data Flow:
- Whiteboard objects (visual metadata) → wbo table
- Actual data (recipes, plans, lists) → existing tables
- Comments/activity → Liveblocks storage
- Messages → Stream Chat storage
- Fetch on demand (viewport-based lazy loading)
```

---

## 📊 **PHASE 1: FOUNDATION (Weeks 1-4)**

### **Objectives:**
✅ Set up database schema and migrations  
✅ Create V2 API blueprint structure  
✅ Build basic whiteboard CRUD endpoints  
✅ Implement authentication & permissions  
✅ Create React whiteboard page shell  
✅ Set up React Flow canvas basics  

### **Backend Tasks (Week 1-2):**

#### **Week 1: Database Setup**
```sql
□ Create migration script for 4 core tables
  - whiteboards
  - whiteboard_objects
  - whiteboard_comments
  - whiteboard_collaborators

□ Add database triggers & functions
  - update_updated_at_column()
  - update_whiteboard_activity()
  - calculate_thread_depth()
  - log_whiteboard_change()

□ Create indexes for performance
  - GIN indexes for JSONB columns
  - Foreign key indexes
  - Composite indexes for queries

□ Write database migration script
  - Forward migration (create)
  - Reverse migration (drop)
  - Seed data for testing

□ Test migration on development database
  - Verify constraints
  - Test triggers
  - Validate indexes
```

**Deliverables:**
- `migrations/20251101_create_whiteboard_tables.sql`
- `migrations/20251101_create_whiteboard_triggers.sql`
- Migration tested and documented

#### **Week 2: API Blueprint Structure**
```python
□ Create app/api/v2/whiteboards.py
  - Blueprint registration
  - Import dependencies
  - Add to __init__.py

□ Implement 5 CRUD endpoints
  GET    /api/v2/whiteboards/household/<id>
  POST   /api/v2/whiteboards
  GET    /api/v2/whiteboards/<id>
  PATCH  /api/v2/whiteboards/<id>
  DELETE /api/v2/whiteboards/<id>

□ Add authentication decorators
  - @require_auth
  - check_household_membership()
  - check_whiteboard_permissions()

□ Write permission checking logic
  - verify_household_member()
  - get_user_role()
  - validate_action()

□ Create WhiteboardService class
  - Business logic separation
  - Database query helpers
  - Data transformation

□ Add error handling & logging
  - Try/catch blocks
  - Meaningful error messages
  - Debug logging
```

**Deliverables:**
- `app/api/v2/whiteboards.py` (5 endpoints functional)
- `app/services/whiteboard_service.py`
- Postman collection for testing
- 5 passing API tests

### **Frontend Tasks (Week 3-4):**

#### **Week 3: Page Structure & React Flow Setup**
```javascript
□ Install React Flow
  npm install reactflow @reactflow/node-resizer

□ Create frontend/src/pages/WhiteboardApp.js
  - Route definition in App.js
  - Protected route wrapper
  - Responsive layout (desktop vs tablet vs phone)

□ Set up responsive detection
  npm install react-responsive
  - useMediaQuery hooks
  - Platform-specific components
  - Conditional rendering logic

□ Set up component structure
  frontend/src/components/whiteboard/
  ├── WhiteboardCanvas.js (React Flow - desktop/tablet)
  ├── WhiteboardMobileView.js (Structured list - phone)
  ├── WhiteboardToolbar.js
  ├── WhiteboardSidebar.js
  └── blocks/ (modular block components)
      ├── RecipeBlock.js
      ├── GroceryListBlock.js
      ├── MealPlanBlock.js
      └── NoteBlock.js

□ Create whiteboard context
  - WhiteboardContext.js
  - State management (nodes, edges, collaborators)
  - API integration hooks (useFetchWhiteboard)
  - Real-time sync hooks (useWebSocket)

□ Build navigation integration
  - Add "Whiteboards" to MainApp menu
  - Breadcrumb navigation
  - Back button handling
```

**Deliverables:**
- WhiteboardApp page accessible via route
- Responsive detection working (desktop/tablet/phone)
- Empty canvas renders (desktop/tablet)
- Empty list view renders (phone)
- Context provider working

#### **Week 4: React Flow Integration & Mobile View**
```javascript
□ Set up React Flow canvas (Desktop/Tablet)
  - Install and configure
  - Custom styling
  - Viewport controls (zoom, pan)
  - Touch optimizations (tablet)

□ Implement canvas toolbar
  - Search existing recipes (AddBlockMenu)
  - Select existing grocery lists
  - Select existing meal plans
  - Create new note
  - Zoom controls, fit view
  - Grid toggle, background settings

□ Create mobile list view (Phone)
  - ScrollView with sections
  - "Recipes", "Grocery Lists", "Meal Plans", "Notes"
  - Card components (tap to view)
  - Quick action buttons (comment, react)
  - Presence bar (who's active)

□ Build create whiteboard modal
  - Name input
  - Template selection (optional)
  - Household association
  - Create API call

□ Build sidebar structure
  - Whiteboard list (household boards)
  - Search/filter by tags
  - Activity feed (recent changes)
  - "New Whiteboard" button

□ Add loading states & error handling
  - Skeleton loaders
  - Error boundaries
  - Retry logic
```

**Deliverables:**
- Functional React Flow canvas (desktop/tablet)
- Structured list view (phone)
- Whiteboard creation works end-to-end
- List of whiteboards displays
- Basic toolbar functional
- Mobile quick actions working

### **Phase 1 Milestones:**
✅ Database schema deployed to production  
✅ 5 CRUD endpoints live and tested  
✅ WhiteboardApp page accessible  
✅ Users can create and view empty whiteboards  

---

## 📊 **PHASE 2: CORE OBJECTS (Weeks 5-8)**

### **Objectives:**
✅ Implement recipe card objects  
✅ Build grocery list panel objects  
✅ Create meal plan table objects  
✅ Add sticky note objects  
✅ Enable drag & drop between objects  
✅ Link objects to existing data entities  

### **Backend Tasks (Week 5-6):**

#### **Week 5: Object Management Endpoints**
```python
□ Implement object CRUD endpoints
  POST   /api/v2/whiteboards/<id>/objects
  PATCH  /api/v2/whiteboards/<id>/objects/<object_id>
  DELETE /api/v2/whiteboards/<id>/objects/<object_id>

□ Add object linking endpoints
  POST /api/v2/whiteboards/<id>/objects/from-recipe
  POST /api/v2/whiteboards/<id>/objects/<object_id>/link
  POST /api/v2/whiteboards/<id>/objects/<object_id>/sync

□ Implement bulk update endpoint
  PATCH /api/v2/whiteboards/<id>/objects/bulk-update
  - Handle multiple position updates
  - Batch processing for performance
  - Change log integration

□ Create object type handlers
  - RecipeObjectHandler
  - GroceryListObjectHandler
  - MealPlanObjectHandler
  - NoteObjectHandler

□ Add data population logic
  - Join recipes table for recipe objects
  - Join grocery_lists for list objects
  - Join meal_plans for plan objects
  - Eager loading optimization
```

**Deliverables:**
- 7 object management endpoints functional
- Object handlers implemented
- 10 passing API tests

#### **Week 6: Data Integration**
```python
□ Enhance recipe data for cards
  - Thumbnail optimization
  - Metadata extraction
  - Tag aggregation

□ Build grocery list sync logic
  - Real-time item updates
  - Check-off state synchronization
  - Ingredient aggregation

□ Implement meal plan integration
  - Meal slot validation
  - Recipe assignment logic
  - Auto-populate from plans

□ Add change tracking
  - Log object creation
  - Log position updates
  - Log content changes

□ Performance optimization
  - Query batching
  - Caching strategies
  - Lazy loading
```

**Deliverables:**
- Objects linked to existing entities work perfectly
- Data sync logic tested
- Performance benchmarks met (<200ms response)

### **Frontend Tasks (Week 7-8):**

#### **Week 7: Custom React Flow Nodes (Modular Blocks)**
```javascript
□ Create RecipeBlock component
  components/whiteboard/blocks/RecipeBlock.js
  - Fetch recipe data from /api/v2/recipes/{rid}
  - Display thumbnail, title, metadata
  - Show organization tags
  - Hover effects, click to expand
  - Drag handle (React Flow native)
  - Comment badge (count)
  - Quick actions (Add to Plan, React)

□ Build GroceryListBlock component
  components/whiteboard/blocks/GroceryListBlock.js
  - Fetch list data from /api/v2/grocery-lists/{gid}
  - Display list header, item count
  - Show checked/unchecked items
  - Inline checkbox interaction
  - Sync indicator (real-time updates)
  - Collapsible sections
  - Add item button

□ Implement MealPlanBlock component (Recipe Grouping Container)
  components/whiteboard/blocks/MealPlanBlock.js
  - ✅ Fetch plan data from /api/meal-plans/{mid} (V1 API)
  - ✅ Freeform resizable container (no weekly grid!)
  - ✅ User-defined name (click to rename)
  - ✅ Recipe grouping (displays recipes array)
  - ✅ Position persistence (wbo.position)
  - ✅ Links to whiteboard (wbo.mid)
  
  Phase 1 - Core Functionality:
  - □ Drag recipe cards INTO group (drop zone)
  - □ Resize box freely (corner drag handles like Illustrator)
  - □ Live rename (auto-save on blur)
  - □ Show mini recipe cards inside box
  - □ Remove recipe from group (X button)
  - □ "Add Recipe" button (search modal)
  
  Phase 2 - Polish (Future):
  - □ Color picker (border/background)
  - □ Background patterns
  - □ Custom icons
  
  Phase 3 - Collaboration (Future):
  - □ Comments on group (via Liveblocks)
  - □ Assign to users
  - □ Activity feed (via Liveblocks)

□ Create NoteBlock component
  components/whiteboard/blocks/NoteBlock.js
  - Editable text area (Tiptap editor with markdown)
  - Color picker (React Color - yellow, blue, green, pink)
  - Resize handles (@reactflow/node-resizer)
  - Auto-save on blur
  - Character limit indicator
  - Font size controls
  
  Implementation:
  npm install @tiptap/react @tiptap/starter-kit react-color
  - Use Tiptap for rich text editing
  - Use React Color for background selection
  - Store content in whiteboard_objects.note_content

□ Create TagSystem component
  - Tag display (pills)
  - Tag editor (autocomplete)
  - Tag filter (sidebar)
  - Predefined tags ("weeknight", "kids", "party")
  - Custom tags support

□ Register custom nodes with React Flow
  const modularBlockTypes = {
    rc: RecipeBlock,      // recipe card
    gl: GroceryListBlock, // grocery list
    mp: MealPlanBlock,    // meal plan
    nt: NoteBlock         // note
  };
  
  <ReactFlow nodeTypes={modularBlockTypes} />
```

**Deliverables:**
- 4 modular block types rendering correctly
- Each block fetches data from existing V2 APIs
- Blocks display real data (not hardcoded)
- Tags visible and editable
- Styling matches YesChef design system

#### **Week 8: Drag & Drop + Mobile Interactions**
```javascript
□ Implement object dragging (Desktop/Tablet)
  - Pan canvas vs drag object logic
  - Drag start/end handlers
  - Position tracking (debounced)
  - Optimistic UI updates
  - Bulk position save API call

□ Build object creation flow
  - Search recipes modal
    → Select recipe → Creates recipe block on canvas
    → Links to existing recipe (rid)
  - Select grocery list dropdown
    → Choose list → Creates grocery block
    → Links to existing list (gid)
  - Select meal plan dropdown
    → Choose plan → Creates meal plan block
    → Links to existing plan (mid)
  - Create note button
    → Opens note editor → Creates note block
    → Stores content in whiteboard (no external link)

□ Add object selection (Desktop/Tablet)
  - Single select (click)
  - Multi-select (Shift+click, Cmd+click)
  - Selection box (drag on canvas)
  - Keyboard shortcuts (Delete, Duplicate, Copy/Paste)

□ Implement object manipulation
  - Resize handles (@reactflow/node-resizer)
  - Bring to front/back (z-index)
  - Alignment guides (snap to grid optional)
  - Duplicate block action

□ Build mobile card interactions (Phone)
  - Tap card → Open detail modal
  - Long press → Quick actions sheet
    → Comment, React, Share, Add to Collection
  - Swipe actions (optional)
  - Pull to refresh

□ Create bulk update logic
  - Batch position updates (drag multiple)
  - Optimistic UI updates
  - Conflict resolution (last write wins)
  - Undo/redo preparation

□ Implement tag filtering
  - Sidebar tag list
  - Click tag → Filter canvas/list
  - Multi-tag selection (AND/OR logic)
  - "Show All" button
```

**Deliverables:**
- Drag & drop feels Google Keep-smooth (desktop/tablet)
- Objects save position automatically
- Multi-select and bulk operations work
- Performance: 60fps during drag
- Mobile tap/long-press actions functional
- Tag filtering works across all platforms
- Create flow connects to existing APIs (no data duplication)

### **Phase 2 Milestones:**
✅ All 4 modular block types functional  
✅ Blocks link to existing API data (recipes, lists, plans)  
✅ Drag & drop working smoothly (desktop/tablet)  
✅ Mobile list view with tap interactions  
✅ Tag system for organization  
✅ Users can search/add existing content as blocks  
✅ No data duplication - single source of truth maintained  

---

## 📊 **PLATFORM-SPECIFIC DEVELOPMENT STRATEGY**

### **Desktop (React Flow Canvas) - PRIMARY ENVIRONMENT**

**Focus:** Full creation and organization capabilities

```javascript
// Desktop-specific features
✅ React Flow canvas (full features)
✅ Mouse precision (pixel-perfect dragging)
✅ Keyboard shortcuts (Cmd+Z, Delete, etc.)
✅ Multi-select (Shift+click, selection box)
✅ Right-click context menus
✅ Connection lines between blocks
✅ Minimap for navigation
✅ Zoom/pan controls
✅ Detailed block editing
```

**UX Priority:**
- Power user features
- Keyboard-driven workflow
- Precise layout control
- Complex organizational tasks

---

### **Tablet (Touch-Optimized Canvas) - SECONDARY ENVIRONMENT**

**Focus:** Light editing and on-the-go adjustments

```javascript
// Tablet-specific optimizations
✅ Larger touch targets (20% bigger blocks)
✅ Touch-friendly controls (48px minimum)
✅ Gesture support (pinch zoom, two-finger pan)
✅ Apple Pencil support (drawing on notes)
✅ Simplified toolbar (fewer options)
✅ Larger drag handles
✅ Touch-and-hold context menus
✅ iPad keyboard shortcuts (optional)
```

**UX Priority:**
- Natural touch interactions
- Quick adjustments
- Mobile-to-desktop bridge
- Couch-friendly experience

**Implementation:**
```javascript
// Tablet detection and optimization
const isTablet = useMediaQuery({ minWidth: 768, maxWidth: 1024 });

if (isTablet) {
  return (
    <ReactFlow
      nodes={nodes}
      nodeTypes={touchOptimizedBlockTypes}  // 20% larger
      panOnDrag={[1, 2]}  // Pan with 1 or 2 fingers
      zoomOnPinch={true}
      selectionOnDrag={false}  // Disable selection box
      minZoom={0.3}
      maxZoom={1.5}
    >
      <TouchControls />
    </ReactFlow>
  );
}
```

---

### **Phone (Structured List) - CONSUMPTION ENVIRONMENT**

**Focus:** View, comment, react - NOT organize

```javascript
// Phone-specific features
✅ Structured sections (Recipes, Lists, Plans, Notes)
✅ Card-based layout (ScrollView)
✅ Tap to view details
✅ Quick action sheets (Comment, React, Share)
✅ @mention support in comments
✅ Push notifications (@mentions, changes)
✅ Presence bar (who's active)
✅ "Open on Desktop" CTA
❌ NO canvas (overwhelming on small screen)
❌ NO drag & drop (too imprecise)
❌ NO complex organization (desktop task)
```

**UX Priority:**
- Stay informed (activity feed)
- Quick interactions (tap, swipe)
- Communication (comments, reactions)
- Lightweight consumption

**Implementation:**
```javascript
// Phone list view
const isPhone = useMediaQuery({ maxWidth: 767 });

if (isPhone) {
  return (
    <WhiteboardMobileView>
      <CollaboratorBar users={activeUsers} />
      
      <QuickActionsBar>
        <Button icon="💬">Comment</Button>
        <Button icon="🔗">Share</Button>
        <Button icon="💻">Open on Desktop</Button>
      </QuickActionsBar>
      
      <ScrollView>
        <Section title="Recipes" icon="🍳">
          {recipeBlocks.map(block => (
            <RecipeCard
              recipe={block.data}
              tags={block.tags}
              onTap={() => openDetail(block)}
              onComment={() => openCommentModal(block)}
            />
          ))}
        </Section>
        
        {/* More sections... */}
      </ScrollView>
    </WhiteboardMobileView>
  );
}
```

---

### **Cross-Platform Features (All Devices)**

**Universal capabilities:**
- ✅ View whiteboard content
- ✅ Read comments and activity
- ✅ Add comments and reactions
- ✅ @mention collaborators
- ✅ Receive notifications
- ✅ See who's active (presence)
- ✅ View tags and filters
- ✅ Access from anywhere

**Data Sync:**
- Desktop creates layout → Phone sees structured list
- Tablet moves block → Desktop sees update
- Phone adds comment → All devices notified
- Real-time via WebSocket (desktop/tablet)
- Polling fallback (phone, if needed)

---

## 📊 **PHASE 3: REAL-TIME COLLABORATION (Weeks 9-11)**

### **Objectives:**
✅ Set up Liveblocks integration  
✅ Implement presence tracking  
✅ Build live cursor display  
✅ Add collaborative editing indicators  
✅ Set up Stream Chat for household messaging  

### **Backend Tasks (Week 9-10):**

#### **Week 9: Liveblocks Auth Setup**
```python
□ Create Liveblocks auth endpoint
  POST /api/liveblocks/auth
  - Generate Liveblocks tokens
  - Verify user authentication
  - Return room access tokens
  - Set user permissions

□ Install Liveblocks Python SDK (if needed)
  pip install liveblocks

□ Configure Liveblocks credentials
  - Add LIVEBLOCKS_SECRET_KEY to environment
  - Set up room-based permissions
  - Define user roles (viewer, editor, admin)

□ Create Stream Chat auth endpoint
  POST /api/stream-chat/auth
  - Generate Stream Chat user tokens
  - Verify household membership
  - Create user in Stream Chat
  - Return auth token

□ Install Stream Chat Python SDK
  pip install stream-chat

□ Configure Stream Chat credentials
  - Add STREAM_API_KEY to environment
  - Add STREAM_API_SECRET to environment
  - Set up household channels
```

**Deliverables:**
- Liveblocks auth endpoint functional
- Stream Chat auth endpoint functional
- Both SDKs configured
- Token generation tested

#### **Week 10: Third-Party Integration**
```python
□ Create Liveblocks room per whiteboard
  - Room ID = f"whiteboard-{whiteboard_id}"
  - Auto-create on whiteboard creation
  - Set permissions based on household role

□ Create Stream Chat channels
  - Household channel: f"household-{household_id}"
  - Auto-create on household creation
  - Add all household members

□ Build presence tracking (via Liveblocks)
  - Track active users per whiteboard
  - Periodic heartbeat handled by Liveblocks
  - No custom WebSocket needed

□ Set up comment storage (via Liveblocks)
  - Comments stored in Liveblocks
  - Threaded conversations
  - @mentions automatically handled

□ Configure message channels (via Stream Chat)
  - Household message board
  - DMs between members
  - Push notification setup
```

**Deliverables:**
- Liveblocks rooms auto-created
- Stream Chat channels auto-created
- Presence system working via Liveblocks
- Comment system using Liveblocks storage
- Messaging working via Stream Chat

### **Frontend Tasks (Week 11):**

#### **Week 11: Real-Time Frontend**
```javascript
□ Set up Liveblocks client
  npm install @liveblocks/client @liveblocks/react @liveblocks/react-ui
  
  import { LiveblocksProvider, RoomProvider } from "@liveblocks/react/suspense";
  
  <LiveblocksProvider authEndpoint="/api/liveblocks/auth">
    <RoomProvider id={`whiteboard-${whiteboardId}`}>
      <WhiteboardCanvas />
    </RoomProvider>
  </LiveblocksProvider>

□ Set up Stream Chat client
  npm install stream-chat stream-chat-react
  
  import { StreamChat } from 'stream-chat';
  import { Chat, Channel } from 'stream-chat-react';
  
  const chatClient = StreamChat.getInstance(STREAM_API_KEY);
  await chatClient.connectUser(user, userToken);

□ Implement connection management
  - Auto-connect to Liveblocks room on page load
  - Auto-connect to Stream Chat
  - Disconnect on unmount
  - Reconnect logic handled by SDKs

□ Build user cursor component (via Liveblocks)
  components/whiteboard/collaboration/UserCursor.js
  - Use Liveblocks useOthers() hook
  - SVG cursor with user name
  - Color coding per user
  - Smooth animation (CSS transform)
  - Auto-hide when inactive

□ Add presence indicators (via Liveblocks)
  components/whiteboard/collaboration/UserAvatar.js
  - Use Liveblocks useOthers() hook
  - Avatar list at bottom
  - "User is viewing" tooltips
  - Active/inactive states

□ Implement commenting (via Liveblocks)
  components/whiteboard/collaboration/CommentThread.js
  - Use @liveblocks/react-ui components
  - <Thread>, <Composer>, <Comment>
  - Attach to whiteboard objects
  - Real-time sync automatic

□ Build household chat (via Stream Chat)
  components/HouseholdChat.js
  - Floating chat button
  - Modal with Stream Chat UI
  - Household channel
  - DM support
```

**Deliverables:**
- Live cursors visible for all users via Liveblocks
- Presence indicators working via Liveblocks
- Object changes appear in real-time
- Comments system using Liveblocks UI
- Household chat working via Stream Chat
- Performance: <100ms sync latency

### **Phase 3 Milestones:**
✅ Liveblocks integration complete  
✅ Stream Chat integration complete  
✅ Real-time collaboration working  
✅ Multiple users can edit simultaneously  
✅ Comments system functional  
✅ Household messaging functional  
✅ No conflicts or data loss  

---

## 📊 **PHASE 4: COMMENTING & MESSAGING POLISH (Weeks 12-14)**

### **Objectives:**
✅ Polish Liveblocks comment UI  
✅ Add custom comment features  
✅ Polish Stream Chat UI  
✅ Add notification system  
✅ Create activity feed  

### **Backend Tasks (Week 12):**

#### **Week 12: Notification System**
```python
□ Create notification endpoints
  GET    /api/v2/notifications
  PATCH  /api/v2/notifications/<id>/read
  DELETE /api/v2/notifications/<id>

□ Build notification triggers
  - Liveblocks webhook for @mentions
  - Stream Chat webhook for messages
  - Store notifications in PostgreSQL
  - Mark as read/unread

□ Add notification preferences
  - Email notifications toggle
  - Push notification toggle (future)
  - @mention alerts
  - Message alerts

□ Create activity feed endpoint
  GET /api/v2/whiteboards/<id>/activity
  - Recent comments (via Liveblocks API)
  - Recent messages (via Stream Chat API)
  - Object changes (from audit log)
  - Aggregated timeline view
```

**Deliverables:**
- Notification system functional
- Webhooks configured
- Activity feed endpoint working

### **Frontend Tasks (Week 13-14):**

#### **Week 13: Polish Comment & Chat UI**
```javascript
□ Customize Liveblocks comment UI
  - Import default CSS: import '@liveblocks/react-ui/styles.css'
  - Override styles to match YesChef theme
  - Custom user avatars
  - Custom timestamp formatting
  - Add object context (which recipe/meal plan)

□ Create comment panel component
  components/whiteboard/CommentPanel.js
  - Slide-out from right
  - Object context display
  - Use <Thread> from Liveblocks
  - Scroll to latest comment
  - Unread comment badges

□ Customize Stream Chat UI
  - Import default CSS: import 'stream-chat-react/dist/css/index.css'
  - Override styles to match YesChef theme
  - Custom message bubbles
  - Household branding

□ Build household chat modal
  components/HouseholdChatModal.js
  - Floating button with unread count
  - Modal with Stream Chat Channel
  - Household member list
  - DM tabs

□ Add notification UI
  - Bell icon with unread count
  - Notification dropdown
  - Toast notifications for @mentions
  - Mark all as read button
```

**Deliverables:**
- Liveblocks comments match YesChef theme
- Stream Chat matches YesChef theme
- Comment panel polished
- Chat modal functional
- Notifications UI working

#### **Week 14: Activity Feed & Polish**
```javascript
□ Build activity feed component
  components/whiteboard/ActivityFeed.js
  - Fetch from /api/v2/whiteboards/<id>/activity
  - Timeline view
  - Filter by type (comments, messages, changes)
  - "Load more" pagination
  - Auto-refresh every 30s

□ Add typing indicators (Stream Chat built-in)
  - "User X is typing..." in chat
  - Automatic via Stream Chat SDK

□ Polish notification experience
  - Toast notifications
  - Sound effects (optional)
  - Browser notifications (request permission)
  - Notification preferences in settings

□ Implement comment moderation
  - Resolve comment thread (custom metadata)
  - Delete comments (Liveblocks API)
  - Report spam (custom flag)
  - Admin tools
```

**Deliverables:**
- Activity feed functional
- Typing indicators working
- Notifications polished
- Moderation tools available

### **Phase 4 Milestones:**
✅ Threaded commenting system complete  
✅ Reactions and @mentions working  
✅ Real-time comment sync functional  
✅ Notification system operational  

---

## 📊 **PHASE 5: POLISH & TEMPLATES (Weeks 15-17)**

### **Objectives:**
✅ Create whiteboard templates  
✅ Add keyboard shortcuts  
✅ Implement undo/redo  
✅ Build export functionality  
✅ Optimize mobile view  

### **Backend Tasks (Week 15):**

#### **Week 15: Templates & Export**
```python
□ Create template system
  GET /api/v2/whiteboards/templates
  - Seed database with 5 templates
  - Weekly Meal Planner
  - Party Planning Board
  - Meal Prep Station
  - Grocery Organization
  - Freeform Canvas

□ Build template creation API
  POST /api/v2/whiteboards/<id>/save-as-template
  - Extract structure
  - Remove user-specific data
  - Save as template
  - Admin-only

□ Implement duplication
  POST /api/v2/whiteboards/<id>/duplicate
  - Clone whiteboard
  - Clone all objects
  - Reset IDs
  - Assign to new household

□ Add export functionality
  GET /api/v2/whiteboards/<id>/export?format=pdf
  - JSON export (data)
  - PDF export (visual)
  - PNG export (image)
  - Share link generation
```

**Deliverables:**
- 5 templates available
- Duplication works
- Export endpoints functional

### **Frontend Tasks (Week 16-17):**

#### **Week 16: UX Enhancements**
```javascript
□ Implement keyboard shortcuts
  - Ctrl+Z: Undo
  - Ctrl+Shift+Z: Redo
  - Del: Delete selected objects
  - Ctrl+D: Duplicate
  - Ctrl+A: Select all
  - Ctrl+F: Search
  - Esc: Deselect

□ Build undo/redo system
  - Command pattern
  - History stack (50 actions)
  - Redo stack
  - Visual indicators

□ Add context menus
  - Right-click on canvas
  - Right-click on object
  - Context-specific actions
  - Keyboard navigation

□ Create search functionality
  - Search recipes on canvas
  - Search comments
  - Filter by object type
  - Jump to result
```

**Deliverables:**
- Keyboard shortcuts working
- Undo/redo functional
- Context menus polished
- Search implemented

#### **Week 17: Mobile Optimization**
```javascript
□ Create mobile whiteboard view
  YesChefMobile/src/screens/WhiteboardViewScreen.js
  - Read-only canvas
  - Tap object → quick actions modal
  - Pinch to zoom
  - Two-finger pan

□ Build mobile edit mode (tablet)
  - Simplified toolbar
  - Touch-optimized drag
  - Larger touch targets
  - Gesture controls

□ Add mobile quick actions
  - Tap recipe → Add to meal plan
  - Tap note → Edit text
  - Tap list → Check items
  - Comment bubble

□ Implement offline caching
  - Cache whiteboard state
  - Queue changes
  - Sync on reconnect
  - Conflict resolution
```

**Deliverables:**
- Mobile view functional (read-only)
- Tablet edit mode working
- Quick actions implemented
- Offline support tested

### **Phase 5 Milestones:**
✅ Template library with 5 templates  
✅ Keyboard shortcuts working  
✅ Undo/redo functional  
✅ Mobile view optimized  

---

## 📊 **PHASE 6: INTEGRATION & TESTING (Weeks 18-20)**

### **Objectives:**
✅ Integrate with existing features  
✅ Performance optimization  
✅ Cross-browser testing  
✅ Load testing  
✅ Bug fixing  

### **Week 18: Feature Integration**
```
□ Recipe search → whiteboard integration
  - Drag recipe from search results
  - Add button in recipe detail
  - Bulk add from meal plan

□ Meal plan sync
  - Changes on whiteboard → update meal plan
  - Changes in meal plan → update whiteboard
  - Bidirectional sync logic

□ Grocery list integration
  - Check-off items on whiteboard
  - Changes sync to mobile app
  - Real-time updates

□ Community recipe sharing
  - Share whiteboard as image
  - Export meal plan as recipe collection
  - Social sharing buttons
```

### **Week 19: Performance Optimization**
```
□ Frontend optimization
  - Code splitting
  - Lazy loading objects
  - Image optimization
  - Bundle size reduction

□ Backend optimization
  - Query optimization
  - Caching strategy (Redis)
  - Database indexes review
  - API response compression

□ WebSocket optimization
  - Connection pooling
  - Message batching
  - Throttling/debouncing
  - Bandwidth monitoring
```

### **Week 20: Testing**
```
□ Unit tests
  - Backend endpoints (50 tests)
  - Frontend components (30 tests)
  - WebSocket events (20 tests)

□ Integration tests
  - End-to-end workflows (15 tests)
  - Multi-user scenarios (10 tests)
  - Conflict resolution (5 tests)

□ Manual testing
  - Cross-browser (Chrome, Firefox, Safari, Edge)
  - Mobile devices (iOS, Android)
  - Tablet devices (iPad, Android)
  - Accessibility (screen readers)

□ Load testing
  - 10 users on same whiteboard
  - 50 objects on canvas
  - 100 comments on object
  - WebSocket connection limits
```

### **Phase 6 Deliverables:**
✅ All features integrated  
✅ Performance benchmarks met  
✅ 100+ tests passing  
✅ Zero critical bugs  

---

## 📊 **PHASE 7: BETA TESTING (Weeks 21-24)**

### **Week 21-22: Internal Beta**
```
□ Recruit 10 power users from existing base
□ Create beta testing guide
□ Set up feedback collection (Google Forms + Slack)
□ Daily bug triage meetings
□ Weekly feature review sessions
```

### **Week 23-24: External Beta**
```
□ Expand to 50 beta testers
□ Launch beta feedback channel
□ A/B test pricing models
□ Collect usage analytics
□ Refine based on feedback
```

### **Beta Success Criteria:**
- ✅ 80%+ users find whiteboard "valuable" or "very valuable"
- ✅ 60%+ users use whiteboard weekly
- ✅ <5 critical bugs reported
- ✅ Average session length >10 minutes
- ✅ 50%+ beta users invite at least 1 person

---

## 📊 **PHASE 8: PRODUCTION LAUNCH (Weeks 25-28)**

### **Week 25: Pre-Launch Prep**
```
□ Finalize pricing model ($9.99/month confirmed)
□ Create marketing materials (landing page, demo video)
□ Write documentation (user guide, FAQ)
□ Set up analytics dashboards
□ Prepare support team (training, scripts)
```

### **Week 26: Soft Launch**
```
□ Launch to existing premium users (early access)
□ Monitor system performance
□ 24/7 on-call engineering
□ Daily metrics review
□ Quick bug fixes
```

### **Week 27-28: Full Launch**
```
□ Public announcement (blog post, email campaign)
□ Social media push
□ Press release
□ Influencer partnerships
□ Referral program launch
```

---

## 🎯 **SUCCESS METRICS**

### **Week 4 (Phase 1 Complete):**
- ✅ Users can create empty whiteboards
- ✅ 5 CRUD endpoints tested
- ✅ React Flow rendering

### **Week 8 (Phase 2 Complete):**
- ✅ All 4 object types working
- ✅ Drag & drop smooth
- ✅ Objects link to data

### **Week 11 (Phase 3 Complete):**
- ✅ Real-time collaboration live
- ✅ <100ms sync latency
- ✅ 10+ users tested simultaneously

### **Week 14 (Phase 4 Complete):**
- ✅ Comments working
- ✅ Reactions functional
- ✅ @mentions autocomplete

### **Week 17 (Phase 5 Complete):**
- ✅ 5 templates available
- ✅ Mobile view optimized
- ✅ Undo/redo works

### **Week 20 (Phase 6 Complete):**
- ✅ 100+ tests passing
- ✅ Performance optimized
- ✅ Zero critical bugs

### **Week 24 (Phase 7 Complete):**
- ✅ 50 beta testers engaged
- ✅ 80%+ satisfaction
- ✅ Feedback incorporated

### **Week 28 (Phase 8 Complete):**
- ✅ Production launch successful
- ✅ 100+ active whiteboards
- ✅ Premium conversions tracked

---

## ⚠️ **RISK MANAGEMENT**

### **High-Risk Items:**
1. **Real-Time Performance** - Mitigation: Early load testing, WebSocket optimization
2. **Mobile Canvas UX** - Mitigation: Tablet-first approach, simplified phone view
3. **Scope Creep** - Mitigation: Strict phase boundaries, feature freeze after Phase 5

### **Contingency Plans:**
- **If WebSocket too complex:** Use polling fallback (1s interval)
- **If React Flow performance issues:** Switch to Konva.js (more control)
- **If timeline slips:** Cut mobile edit mode (Phase 5), release post-launch

---

**Next Document:** 04_API_ENDPOINTS.md (Complete endpoint reference with request/response examples)
