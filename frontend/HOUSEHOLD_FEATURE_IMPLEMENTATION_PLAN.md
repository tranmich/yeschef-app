# 🏠 Household Feature Implementation Plan for WebApp

## 📋 Executive Summary

The mobile app already has a fully functional **Household** system that enables collaborative Grocery Lists and Meal Plans. The backend APIs exist and work perfectly. This document outlines the plan to bring this feature to the webapp.

---

## 🎯 What is the Household Feature?

A **Household** is a group of users (friends) who can:
- Share grocery lists collaboratively
- Share meal plans together
- See real-time updates from all members
- Work together on meal planning and shopping

### Key Benefits:
- 👨‍👩‍👧‍👦 **Family Coordination** - Share grocery lists with family members
- 🏡 **Roommate Planning** - Coordinate meal plans with roommates
- 👥 **Group Meal Prep** - Plan meals together with friends
- ✅ **Real-time Sync** - Everyone sees updates instantly

---

## 🗄️ Database Structure (Already Exists!)

### Core Tables:

#### 1. `households`
```sql
- id (primary key)
- name (varchar 255)
- description (text)
- owner_user_id (references users)
- invite_code (unique, for joining)
- is_active (boolean)
- created_at (timestamp)
```

#### 2. `household_members`
```sql
- id (primary key)
- household_id (references households)
- user_id (references users)
- role (enum: 'owner', 'admin', 'member')
- invited_by (references users)
- joined_at (timestamp)
```

#### 3. `shared_grocery_lists`
```sql
- id (primary key)
- household_id (references households)
- name (varchar 255)
- description (text)
- created_by (references users)
- is_active (boolean)
- created_at, updated_at (timestamps)
```

#### 4. `shared_grocery_items`
```sql
- id (primary key)
- list_id (references shared_grocery_lists)
- item_name (varchar 255)
- quantity (varchar 50)
- category (varchar 100)
- is_completed (boolean)
- completed_by (references users)
- completed_at (timestamp)
- added_by (references users)
- notes (text)
- created_at, updated_at (timestamps)
```

#### 5. `shared_meal_plans`
```sql
- id (primary key)
- household_id (references households)
- week_start_date (date)
- created_by (references users)
- created_at, updated_at (timestamps)
- UNIQUE constraint on (household_id, week_start_date)
```

#### 6. `planned_meals`
```sql
- id (primary key)
- meal_plan_id (references shared_meal_plans)
- day_of_week (0-6, Monday-Sunday)
- meal_type ('breakfast', 'lunch', 'dinner')
- recipe_id (references recipes)
- recipe_title, recipe_description
- assigned_by (references users)
- notes (text)
- created_at (timestamp)
- UNIQUE constraint on (meal_plan_id, day_of_week, meal_type)
```

---

## 🔌 Backend API Endpoints (Already Implemented!)

### Household Management

#### ✅ Get User's Households
```
GET /api/households/list
Response: {
  success: true,
  households: [
    {
      id: 1,
      name: "Smith Family",
      role: "owner",
      members: 4,
      sharedLists: 2,
      sharedPlans: 1,
      createdAt: "Jan 2025"
    }
  ],
  count: 1
}
```

#### ✅ Create Household
```
POST /api/households/create
Body: {
  name: "Smith Family",
  description: "Our family household"
}
Response: {
  success: true,
  message: "Household created successfully!",
  household: {
    id: 1,
    name: "Smith Family",
    invite_code: "ABC123XYZ"
  }
}
```

#### ✅ Delete Household (Owner only)
```
DELETE /api/households/<household_id>/delete
Response: {
  success: true,
  message: "Household deleted"
}
```

### Member Management

#### ✅ Add Member to Household
```
POST /api/households/<household_id>/members/add
Body: {
  user_id: 42
}
Requirements:
- User must be a friend
- Current user must be owner or admin
Response: {
  success: true,
  message: "Member added to household"
}
```

#### ✅ Remove Member from Household
```
DELETE /api/households/<household_id>/members/<member_id>/remove
Response: {
  success: true,
  message: "Member removed from household"
}
```

#### ✅ Get Household Members
```
GET /api/households/<household_id>/members
Response: {
  success: true,
  members: [
    {
      id: 42,
      name: "John Smith",
      email: "john@example.com",
      role: "owner",
      joinedAt: "2025-01-15"
    }
  ]
}
```

---

## 📱 Mobile App Implementation (Reference)

### How Mobile App Uses Households:

#### **Grocery List Integration:**
```javascript
// Invite household to grocery list
const inviteData = {
  resource_type: 'grocery_list',
  resource_id: listId,
  household_id: householdId,
  permission_level: 'editor'
};
const result = await YesChefAPI.inviteToCollaborate(inviteData);
```

#### **Meal Plan Integration:**
```javascript
// Invite household to meal plan
const inviteData = {
  resource_type: 'meal_plan',
  resource_id: planId,
  household_id: householdId,
  permission_level: 'editor'
};
const result = await YesChefAPI.inviteToCollaborate(inviteData);
```

---

## 🎨 WebApp Implementation Plan

### Phase 1: Household Management UI ⭐ (Priority)

#### Location: Community Section
Add new tab: **Households**

#### Features:
1. **View Households**
   - List all households user belongs to
   - Show member count, shared resources
   - Display user's role (owner/admin/member)

2. **Create Household**
   - Modal with form (name, description)
   - Success notification
   - Auto-add user as owner

3. **Manage Household**
   - View members list
   - Add members (from friends list)
   - Remove members (if owner/admin)
   - Delete household (if owner)

#### UI Components Needed:
```
- HouseholdManager.js (main component)
- HouseholdCard.js (display household)
- CreateHouseholdModal.js (creation form)
- HouseholdMembersModal.js (member management)
- AddMemberModal.js (select friends to add)
```

### Phase 2: Grocery List Integration ⭐⭐

#### Location: Grocery List Workspace
Add "Share" button next to "Save"

#### Features:
1. **Share Button**
   - Opens modal showing user's households
   - Select household to share with
   - Confirm sharing

2. **Shared Indicator**
   - Show which households have access
   - Display collaboration badge
   - Show who made last edit

3. **Shared List View**
   - See items added by different users
   - User avatars/names next to items
   - Real-time updates (WebSocket or polling)

#### UI Components:
```
- ShareGroceryListModal.js
- HouseholdSelector.js
- CollaborationBadge.js
- SharedItemIndicator.js
```

### Phase 3: Meal Planner Integration ⭐⭐

#### Location: Meal Planner
Add "Share" functionality

#### Features:
1. **Share Meal Plan**
   - Share current week's plan
   - Select household
   - Permission levels

2. **Collaborative Planning**
   - See who added each recipe
   - Edit permissions
   - Change notifications

#### UI Components:
```
- ShareMealPlanModal.js
- MealPlanCollaborators.js
- SharedMealIndicator.js
```

### Phase 4: Real-time Sync (Advanced) ⭐⭐⭐

#### Options:
1. **WebSocket Integration**
   - Real-time updates for all members
   - Instant sync across devices
   - Requires WebSocket server setup

2. **Polling (Simpler)**
   - Check for updates every 30 seconds
   - Refresh data when changes detected
   - Easier to implement

---

## 🛠️ Implementation Steps

### Step 1: Create Household Management UI
1. Create `HouseholdManager.js` component
2. Add API service functions for households
3. Implement CRUD operations
4. Add to Community section

### Step 2: Integrate with Grocery List
1. Add "Share" button to GroceryManagerWorkspace
2. Create sharing modal
3. Update save/load to handle shared lists
4. Add collaboration indicators

### Step 3: Integrate with Meal Planner
1. Add sharing functionality
2. Show shared meal plans
3. Display collaborators

### Step 4: Polish & Test
1. Error handling
2. Loading states
3. Success/error notifications
4. Mobile responsiveness

---

## 📊 Data Flow

### Creating a Shared Grocery List:
```
1. User creates regular grocery list
2. User clicks "Share with Household"
3. Select household from list
4. Backend creates entry in shared_grocery_lists
5. Links household_id to list
6. All household members can now see/edit
```

### Collaborative Editing:
```
1. User A adds item to shared list
2. Item saved to shared_grocery_items
3. added_by = User A's ID
4. Other members see update (WebSocket or next refresh)
5. User B checks off item
6. is_completed = true, completed_by = User B's ID
```

---

## 🎯 Success Metrics

- ✅ Users can create households
- ✅ Users can add friends to households
- ✅ Grocery lists can be shared with households
- ✅ Meal plans can be shared with households
- ✅ All household members see shared resources
- ✅ Collaborative editing works smoothly
- ✅ Clear indication of who added/edited what

---

## 🚀 Next Steps

1. **Review this plan** - Confirm approach
2. **Choose Phase 1 design** - Household management UI
3. **Implement Household Manager** - Core functionality
4. **Test with friends** - Real-world usage
5. **Iterate based on feedback**

---

## 💡 Design Inspiration

**Notion-style sharing:**
- Clean, minimal modals
- User avatars for members
- Mint green theme (matching current design)
- Clear permission indicators
- Inline collaboration badges

**Trello-style boards:**
- Card-based household display
- Member count badges
- Quick actions on hover
- Drag-and-drop member management

---

## ✨ Future Enhancements

- Household notifications (new member joined, list updated)
- Household chat/comments
- Household recipes collection
- Household cooking calendar
- Shopping list assignments (who buys what)
- Budget tracking per household
- Recipe rotation suggestions

---

**Ready to implement! All backend infrastructure is in place. Just need the UI!** 🎉
