# 📱 Mobile Collaboration Strategy - Whiteboard Features

**Date:** November 10, 2025  
**Status:** Planning Phase  
**Approach:** Invisible Integration (No "Whiteboard" Screen)

---

## 🎯 **CORE PHILOSOPHY**

> **Desktop users organize visually on a canvas.  
> Mobile users collaborate through enhanced existing screens.  
> Same data, different presentation.**

### **Key Principle:**
The whiteboard is **backend infrastructure** for collaboration features, NOT a user-facing mobile feature. Mobile users get all the benefits (comments, tags, presence, activity) without learning a new concept.

---

## 👥 **HOUSEHOLD COLLABORATION FLOW**

### **Scenario: "The Johnson Family Plans Dinner Week"**

#### **Monday Morning - Desktop (Mom)**
```
1. Mom opens YesChef on her laptop
2. Opens household whiteboard "This Week's Dinners"
3. Drags 5 recipe cards onto canvas
4. Groups them by day in MealPlanBlock containers
5. Tags each recipe: "quick", "kids-friendly", "leftover-friendly"
6. Adds comment on Chicken Parmesan: "Let's do this Tuesday!"
7. Creates grocery list from all recipes
```

#### **Monday Afternoon - Mobile (Dad)**
```
📱 Dad opens YesChef app on his phone

HomeScreen shows:
┌─────────────────────────────────┐
│ 🏠 Household Activity           │
├─────────────────────────────────┤
│ 👩 Sarah added 5 recipes        │
│    "This Week's Dinners"        │
│    2 hours ago                  │
│                                 │
│ 💬 Sarah commented on           │
│    Chicken Parmesan             │
│    "Let's do this Tuesday!"     │
│    2 hours ago                  │
└─────────────────────────────────┘

Actions:
1. Taps "Chicken Parmesan" notification
2. Opens RecipeViewScreen (normal recipe view)
3. Sees comment from Sarah
4. Replies: "Sounds great! I'll pick up parmesan."
5. Taps "Add to Shopping List" (auto-syncs with whiteboard grocery list)

✨ Dad never saw a "whiteboard" - just used recipes & comments!
```

#### **Monday Evening - Mobile (Teenager)**
```
📱 Teen opens app during study break

MealPlanScreen shows:
┌─────────────────────────────────┐
│ 🗓️ This Week (Shared)           │
├─────────────────────────────────┤
│ Tuesday 🌮                      │
│ Chicken Parmesan                │
│ 💬 2 comments | Tagged: quick   │
│                                 │
│ Wednesday 🍝                    │
│ Spaghetti Bolognese             │
│ Tagged: leftover-friendly       │
│                                 │
│ Thursday 🥗                     │
│ Taco Salad                      │
│ Tagged: kids-friendly           │
└─────────────────────────────────┘

Actions:
1. Scrolls through week's plan
2. Taps "Spaghetti Bolognese"
3. Leaves comment: "Can we add garlic bread?"
4. Mom gets notification on desktop

✨ Feels like Google Docs commenting - totally natural!
```

---

## 🏗️ **MOBILE ARCHITECTURE**

### **1. Enhanced HomeScreen (Activity Feed)**

**New Section: Household Activity**

```javascript
// HomeScreen.js additions

const loadHouseholdActivity = async () => {
  // Fetch from whiteboard activity API
  const response = await YesChefAPI.get('/api/v2/household/activity');
  
  return response.activities; // Array of recent actions
};

// Activity types:
// - recipe_added: "Sarah added Chicken Parmesan"
// - comment_added: "Dad commented on Taco Tuesday"
// - tag_added: "Mom tagged 3 recipes as 'quick'"
// - grocery_updated: "Sarah checked off milk"
// - user_joined: "Emma is viewing This Week's Dinners"
```

**UI Component:**
```javascript
<View style={styles.householdActivitySection}>
  <Text style={styles.sectionTitle}>🏠 Household Activity</Text>
  
  {activities.map(activity => (
    <TouchableOpacity 
      key={activity.id}
      style={styles.activityCard}
      onPress={() => navigateToActivity(activity)}
    >
      <View style={styles.activityHeader}>
        <Avatar user={activity.user} size={32} />
        <View style={styles.activityContent}>
          <Text style={styles.activityText}>
            {activity.user.name} {activity.action}
          </Text>
          <Text style={styles.activityTime}>
            {formatTimeAgo(activity.created_at)}
          </Text>
        </View>
        
        {/* Show "who's viewing now" presence */}
        {activity.type === 'whiteboard_view' && (
          <PresenceDot color="green" />
        )}
      </View>
      
      {/* Context preview */}
      {activity.preview && (
        <View style={styles.activityPreview}>
          <Text style={styles.previewText}>{activity.preview}</Text>
        </View>
      )}
      
      {/* Quick actions */}
      <View style={styles.quickActions}>
        <TouchableOpacity style={styles.quickActionButton}>
          <Icon name="comment" size={14} color="#6b7280" />
          <Text style={styles.quickActionText}>Reply</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.quickActionButton}>
          <Icon name="eye" size={14} color="#6b7280" />
          <Text style={styles.quickActionText}>View</Text>
        </TouchableOpacity>
      </View>
    </TouchableOpacity>
  ))}
</View>
```

**User Experience:**
- ✅ See what family members are doing (real-time)
- ✅ Tap activity → Jump to context (recipe, list, plan)
- ✅ Reply to comments directly from feed
- ✅ See who's actively viewing/editing
- ✅ Pull to refresh for latest updates

---

### **2. Enhanced RecipeViewScreen (Comments & Tags)**

**Additions to Existing Screen:**

```javascript
// RecipeViewScreen.js - Add comments section

const [comments, setComments] = useState([]);
const [newComment, setNewComment] = useState('');
const [isLoadingComments, setIsLoadingComments] = useState(true);

// Load comments for this recipe's whiteboard object
const loadComments = async () => {
  try {
    // Check if recipe is on any whiteboard
    const whiteboardObject = await YesChefAPI.get(
      `/api/v2/recipes/${recipeId}/whiteboard-object`
    );
    
    if (whiteboardObject) {
      // Fetch comments from whiteboard API
      const response = await YesChefAPI.get(
        `/api/v2/whiteboard/o/${whiteboardObject.id}/cm`
      );
      setComments(response.comments);
    }
  } catch (error) {
    console.log('No comments yet');
    setComments([]);
  }
};

// Add new comment
const handleAddComment = async () => {
  if (!newComment.trim()) return;
  
  const response = await YesChefAPI.post(
    `/api/v2/whiteboard/o/${whiteboardObjectId}/cm`,
    { text: newComment }
  );
  
  if (response.success) {
    setComments([...comments, response.comment]);
    setNewComment('');
    
    // Send notification to household members
    notifyHousehold('comment_added', recipeId);
  }
};
```

**UI Layout:**
```javascript
<ScrollView style={styles.container}>
  {/* Existing recipe content */}
  <RecipeHeader recipe={recipe} />
  <RecipeIngredients ingredients={recipe.ingredients} />
  <RecipeInstructions instructions={recipe.instructions} />
  
  {/* NEW: Tags Section */}
  <View style={styles.tagsSection}>
    <Text style={styles.sectionTitle}>🏷️ Tags</Text>
    <View style={styles.tagPills}>
      {recipe.tags?.map(tag => (
        <TouchableOpacity 
          key={tag}
          style={styles.tagPill}
          onPress={() => filterByTag(tag)}
        >
          <Text style={styles.tagText}>{tag}</Text>
        </TouchableOpacity>
      ))}
      
      {/* Add tag button */}
      <TouchableOpacity 
        style={styles.addTagButton}
        onPress={openTagEditor}
      >
        <Icon name="plus" size={14} color="#6b7280" />
      </TouchableOpacity>
    </View>
  </View>
  
  {/* NEW: Comments Section */}
  <View style={styles.commentsSection}>
    <View style={styles.commentHeader}>
      <Text style={styles.sectionTitle}>💬 Family Discussion</Text>
      <Text style={styles.commentCount}>
        {comments.length} {comments.length === 1 ? 'comment' : 'comments'}
      </Text>
    </View>
    
    {/* Presence bar - who's viewing */}
    <PresenceBar 
      users={activeViewers} 
      text="viewing this recipe"
    />
    
    {/* Comment list */}
    {comments.map(comment => (
      <CommentCard 
        key={comment.id}
        comment={comment}
        onReply={(text) => handleReply(comment.id, text)}
        onReact={(emoji) => handleReact(comment.id, emoji)}
      />
    ))}
    
    {/* Add comment input */}
    <View style={styles.addCommentContainer}>
      <Avatar user={currentUser} size={32} />
      <TextInput
        style={styles.commentInput}
        placeholder="Add a comment..."
        value={newComment}
        onChangeText={setNewComment}
        multiline
      />
      <TouchableOpacity 
        style={styles.sendButton}
        onPress={handleAddComment}
      >
        <Icon name="send" size={20} color="#10b981" />
      </TouchableOpacity>
    </View>
  </View>
</ScrollView>
```

**User Experience:**
- ✅ Scroll to bottom of recipe → See family comments
- ✅ Tap comment → Reply (threaded)
- ✅ React with emoji (❤️ 👍 😋 🔥)
- ✅ @mention family members
- ✅ Get notifications when mentioned
- ✅ See who's viewing recipe (presence)

---

### **3. Enhanced GroceryListScreen (Collaborative Shopping)**

**Additions:**

```javascript
// GroceryListScreen.js - Real-time collaboration

const [activeShoppers, setActiveShoppers] = useState([]);
const [recentChanges, setRecentChanges] = useState([]);

// Subscribe to real-time updates via Pusher
useEffect(() => {
  const channel = pusher.subscribe(`grocery-list-${listId}`);
  
  // Someone checked off an item
  channel.bind('item-checked', (data) => {
    updateItemStatus(data.itemId, data.checked);
    showToast(`${data.userName} checked off ${data.itemName}`);
  });
  
  // Someone added an item
  channel.bind('item-added', (data) => {
    addItemToList(data.item);
    showToast(`${data.userName} added ${data.itemName}`);
  });
  
  // User presence
  channel.bind('user-joined', (data) => {
    setActiveShoppers(prev => [...prev, data.user]);
  });
  
  return () => channel.unsubscribe();
}, [listId]);
```

**UI Additions:**
```javascript
<View style={styles.groceryListContainer}>
  {/* NEW: Active shoppers banner */}
  <View style={styles.activeShoppersBanner}>
    <Icon name="shopping-cart" size={16} color="#10b981" />
    <Text style={styles.bannerText}>
      {activeShoppers.length > 0 
        ? `${activeShoppers.map(u => u.name).join(', ')} shopping now`
        : 'No one shopping right now'
      }
    </Text>
  </View>
  
  {/* NEW: Recent changes activity feed */}
  {recentChanges.length > 0 && (
    <ScrollView 
      horizontal 
      style={styles.recentChanges}
      showsHorizontalScrollIndicator={false}
    >
      {recentChanges.map(change => (
        <View key={change.id} style={styles.changeCard}>
          <Avatar user={change.user} size={24} />
          <Text style={styles.changeText}>
            {change.action === 'checked' ? '✓' : '+'} {change.itemName}
          </Text>
        </View>
      ))}
    </ScrollView>
  )}
  
  {/* Existing grocery list items */}
  <FlatList
    data={groceryItems}
    renderItem={({item}) => (
      <GroceryItemRow 
        item={item}
        onCheck={(checked) => handleCheckItem(item.id, checked)}
      />
    )}
  />
  
  {/* NEW: Add comment on list */}
  <TouchableOpacity 
    style={styles.commentButton}
    onPress={openCommentSheet}
  >
    <Icon name="comment" size={16} color="#6b7280" />
    <Text style={styles.commentButtonText}>
      Family notes ({listComments.length})
    </Text>
  </TouchableOpacity>
</View>
```

**User Experience:**
- ✅ See who's shopping in real-time
- ✅ Get live updates when items are checked off
- ✅ Leave notes on the list ("Get organic milk!")
- ✅ Auto-generated from meal plan recipes (whiteboard link)
- ✅ Sync across all household devices

---

### **4. Enhanced MealPlanScreen (Shared Planning)**

**Already exists but needs whiteboard integration:**

```javascript
// MealPlanScreen.js - Whiteboard integration

const [mealPlanComments, setMealPlanComments] = useState({});
const [householdPresence, setHouseholdPresence] = useState([]);

// Load meal plan with whiteboard context
const loadMealPlan = async () => {
  const plan = await YesChefAPI.get(`/api/v2/meal-plans/${planId}`);
  
  // Check if this plan is on a whiteboard
  const whiteboardLink = await YesChefAPI.get(
    `/api/v2/meal-plans/${planId}/whiteboard-link`
  );
  
  if (whiteboardLink) {
    // Load comments for each day/recipe
    loadPlanComments(whiteboardLink.objectId);
    
    // Subscribe to presence
    subscribeToPresence(whiteboardLink.whiteboardId);
  }
  
  setMealPlan(plan);
};
```

**UI Additions:**
```javascript
<View style={styles.mealPlanContainer}>
  {/* NEW: Household collaboration header */}
  <View style={styles.collaborationHeader}>
    <PresenceBar users={householdPresence} />
    <TouchableOpacity 
      style={styles.inviteButton}
      onPress={inviteHouseholdMembers}
    >
      <Icon name="user-plus" size={16} color="#10b981" />
      <Text style={styles.inviteText}>Invite Family</Text>
    </TouchableOpacity>
  </View>
  
  {/* Existing meal plan grid */}
  <ScrollView>
    {daysOfWeek.map(day => (
      <View key={day} style={styles.dayContainer}>
        <Text style={styles.dayHeader}>{day}</Text>
        
        {/* Recipe cards for this day */}
        {plan[day]?.recipes.map(recipe => (
          <RecipeCard 
            key={recipe.id}
            recipe={recipe}
            onPress={() => openRecipe(recipe)}
          />
        ))}
        
        {/* NEW: Day-specific comments */}
        <TouchableOpacity 
          style={styles.dayCommentButton}
          onPress={() => openDayComments(day)}
        >
          <Icon name="comment" size={14} color="#6b7280" />
          <Text style={styles.commentCount}>
            {mealPlanComments[day]?.length || 0}
          </Text>
        </TouchableOpacity>
        
        {/* NEW: Tag filter */}
        {plan[day]?.tags && (
          <View style={styles.dayTags}>
            {plan[day].tags.map(tag => (
              <Text key={tag} style={styles.tagPill}>{tag}</Text>
            ))}
          </View>
        )}
      </View>
    ))}
  </ScrollView>
  
  {/* NEW: Generate grocery list button */}
  <TouchableOpacity 
    style={styles.generateGroceryButton}
    onPress={generateGroceryList}
  >
    <Icon name="shopping-cart" size={20} color="white" />
    <Text style={styles.buttonText}>Generate Shopping List</Text>
  </TouchableOpacity>
</View>
```

**User Experience:**
- ✅ See who's planning meals with you
- ✅ Comment on specific days ("Can we swap Tuesday?")
- ✅ Vote on recipe options (emoji reactions)
- ✅ Tag days ("busy night", "leftovers", "date night")
- ✅ Generate grocery list from week (auto-syncs to whiteboard)

---

## 🔔 **NOTIFICATION SYSTEM**

### **Push Notification Types:**

```javascript
// Notification categories

1. **Comments & Mentions**
   - "@You Mom commented on Chicken Parmesan"
   - "Dad replied to your comment"
   - "Sarah mentioned you in Taco Tuesday"

2. **Household Activity**
   - "Mom added 3 recipes to This Week's Dinners"
   - "Dad checked off all items on grocery list"
   - "Sarah updated meal plan for Thursday"

3. **Presence & Invitations**
   - "Mom invited you to collaborate on Thanksgiving Dinner"
   - "2 family members are planning meals now"
   - "Dad is shopping - 5 items left"

4. **Reminders**
   - "Meal prep reminder: Marinate chicken tonight for tomorrow"
   - "Grocery run: You have 12 items on the list"
   - "Meal plan incomplete: Add 2 more dinners for this week"
```

### **Notification Handling:**

```javascript
// services/NotificationService.js

class NotificationService {
  
  // Handle notification tap
  static handleNotificationTap(notification) {
    const { type, data } = notification;
    
    switch (type) {
      case 'comment_added':
        // Navigate to recipe with comment visible
        navigation.navigate('RecipeView', {
          recipeId: data.recipeId,
          scrollToComments: true,
          highlightCommentId: data.commentId
        });
        break;
        
      case 'recipe_added':
        // Navigate to meal plan or recipe
        navigation.navigate('MealPlan', {
          planId: data.planId,
          highlightRecipe: data.recipeId
        });
        break;
        
      case 'grocery_updated':
        // Navigate to grocery list
        navigation.navigate('GroceryList', {
          listId: data.listId
        });
        break;
        
      case 'mention':
        // Navigate to context with @mention
        navigateToMention(data);
        break;
    }
  }
  
  // Subscribe to push notifications
  static async subscribe(userId, householdId) {
    const token = await getPushToken();
    
    await YesChefAPI.post('/api/v2/notifications/subscribe', {
      user_id: userId,
      household_id: householdId,
      push_token: token,
      platform: Platform.OS
    });
  }
}
```

---

## 🎨 **REUSABLE COMPONENTS**

### **1. CommentsSection Component**

```javascript
// components/collaboration/CommentsSection.js

import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, FlatList } from 'react-native';
import YesChefAPI from '../../services/YesChefAPI';
import CommentCard from './CommentCard';
import Avatar from '../Avatar';

export default function CommentsSection({ 
  objectType, // 'recipe', 'grocery_list', 'meal_plan'
  objectId, 
  onCommentAdded 
}) {
  const [comments, setComments] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  
  // Load comments
  useEffect(() => {
    loadComments();
  }, [objectId]);
  
  const loadComments = async () => {
    try {
      // Get whiteboard object ID for this entity
      const whiteboardObject = await YesChefAPI.get(
        `/api/v2/${objectType}/${objectId}/whiteboard-object`
      );
      
      if (whiteboardObject) {
        const response = await YesChefAPI.get(
          `/api/v2/whiteboard/o/${whiteboardObject.id}/cm`
        );
        setComments(response.comments || []);
      }
    } catch (error) {
      console.log('No whiteboard link yet');
      setComments([]);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleAddComment = async () => {
    if (!newComment.trim()) return;
    
    try {
      const response = await YesChefAPI.post(
        `/api/v2/whiteboard/o/${whiteboardObjectId}/cm`,
        { text: newComment }
      );
      
      if (response.success) {
        setComments([...comments, response.comment]);
        setNewComment('');
        onCommentAdded?.(response.comment);
      }
    } catch (error) {
      console.error('Failed to add comment:', error);
    }
  };
  
  return (
    <View style={styles.container}>
      <Text style={styles.header}>
        💬 Discussion ({comments.length})
      </Text>
      
      <FlatList
        data={comments}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <CommentCard 
            comment={item}
            onReply={(text) => handleReply(item.id, text)}
            onReact={(emoji) => handleReact(item.id, emoji)}
          />
        )}
      />
      
      <View style={styles.inputContainer}>
        <Avatar user={currentUser} size={32} />
        <TextInput
          style={styles.input}
          placeholder="Add a comment..."
          value={newComment}
          onChangeText={setNewComment}
          multiline
        />
        <TouchableOpacity onPress={handleAddComment}>
          <Icon name="send" size={20} color="#10b981" />
        </TouchableOpacity>
      </View>
    </View>
  );
}
```

**Usage:**
```javascript
// In any screen (RecipeViewScreen, GroceryListScreen, etc.)

<CommentsSection 
  objectType="recipe"
  objectId={recipeId}
  onCommentAdded={(comment) => {
    toast.success('Comment added!');
    notifyHousehold(comment);
  }}
/>
```

---

### **2. PresenceBar Component**

```javascript
// components/collaboration/PresenceBar.js

import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import Avatar from '../Avatar';

export default function PresenceBar({ users, text = "active now" }) {
  if (!users || users.length === 0) return null;
  
  return (
    <View style={styles.container}>
      <View style={styles.avatarStack}>
        {users.slice(0, 3).map((user, index) => (
          <Avatar 
            key={user.id}
            user={user}
            size={28}
            style={[
              styles.avatar,
              { marginLeft: index > 0 ? -10 : 0 }
            ]}
            showOnlineIndicator
          />
        ))}
        {users.length > 3 && (
          <View style={styles.moreCount}>
            <Text style={styles.moreText}>+{users.length - 3}</Text>
          </View>
        )}
      </View>
      
      <Text style={styles.text}>
        {users.length === 1 
          ? `${users[0].name} ${text}`
          : `${users.length} people ${text}`
        }
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 12,
    backgroundColor: 'rgba(16, 185, 129, 0.1)',
    borderRadius: 8,
    marginBottom: 12,
  },
  avatarStack: {
    flexDirection: 'row',
    marginRight: 12,
  },
  avatar: {
    borderWidth: 2,
    borderColor: 'white',
  },
  moreCount: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: '#e5e7eb',
    justifyContent: 'center',
    alignItems: 'center',
    marginLeft: -10,
  },
  moreText: {
    fontSize: 10,
    fontWeight: '600',
    color: '#6b7280',
  },
  text: {
    fontSize: 13,
    color: '#059669',
    fontWeight: '500',
  },
});
```

**Usage:**
```javascript
// Show who's viewing/editing

<PresenceBar 
  users={activeUsers} 
  text="viewing this recipe"
/>

<PresenceBar 
  users={activeShoppers} 
  text="shopping now"
/>
```

---

### **3. TagPills Component**

```javascript
// components/collaboration/TagPills.js

import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import Icon from '../IconLibrary';

export default function TagPills({ 
  tags = [], 
  onTagPress, 
  onAddTag,
  editable = false 
}) {
  
  const tagColors = {
    'quick': '#10b981',
    'kids': '#f59e0b',
    'weeknight': '#3b82f6',
    'party': '#ec4899',
    'healthy': '#14b8a6',
    'comfort': '#ef4444',
    'default': '#6b7280'
  };
  
  const getTagColor = (tag) => {
    const normalized = tag.toLowerCase();
    return tagColors[normalized] || tagColors.default;
  };
  
  return (
    <View style={styles.container}>
      {tags.map(tag => (
        <TouchableOpacity 
          key={tag}
          style={[
            styles.pill,
            { backgroundColor: getTagColor(tag) + '20' }
          ]}
          onPress={() => onTagPress?.(tag)}
        >
          <Text style={[
            styles.text,
            { color: getTagColor(tag) }
          ]}>
            {tag}
          </Text>
        </TouchableOpacity>
      ))}
      
      {editable && (
        <TouchableOpacity 
          style={styles.addButton}
          onPress={onAddTag}
        >
          <Icon name="plus" size={12} color="#6b7280" />
          <Text style={styles.addText}>Add tag</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginVertical: 8,
  },
  pill: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    marginRight: 8,
    marginBottom: 8,
  },
  text: {
    fontSize: 13,
    fontWeight: '600',
  },
  addButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#e5e7eb',
    borderStyle: 'dashed',
  },
  addText: {
    fontSize: 13,
    color: '#6b7280',
    marginLeft: 4,
  },
});
```

---

## 📊 **DATA FLOW: Desktop ↔ Mobile**

### **Scenario: Recipe Added on Desktop**

```
1. Desktop (Mom):
   - Drags "Chicken Parmesan" onto whiteboard
   - Creates whiteboard_object (type: 'rc', rid: 123)
   - Adds tags: ['quick', 'italian']
   - Adds comment: "Let's make this Tuesday!"

2. Backend:
   - Saves whiteboard_object to wbo table
   - Links to existing recipe (rid: 123)
   - Stores tags in wbo.tags array
   - Saves comment in wbc table
   - Triggers Pusher event: 'recipe-added'
   - Sends push notification to household

3. Mobile (Dad):
   - Receives push notification
   - Taps notification
   - Opens RecipeViewScreen (recipe 123)
   - Sees tags at top
   - Scrolls to comments section
   - Sees Mom's comment
   - Replies: "Sounds great!"

4. Backend:
   - Saves Dad's comment to wbc table
   - Triggers Pusher event: 'comment-added'
   - Sends push notification to Mom

5. Desktop (Mom):
   - Sees real-time update on whiteboard
   - Comment badge updates (1 → 2)
   - Toast notification: "Dad replied"
```

### **API Endpoints Used:**

```javascript
// Desktop actions
POST /api/v2/whiteboard/{wid}/o                    // Create whiteboard object
POST /api/v2/whiteboard/o/{oid}/cm                 // Add comment
PATCH /api/v2/whiteboard/o/{oid}                   // Update tags

// Mobile actions
GET /api/v2/recipes/123/whiteboard-object          // Check if recipe is on whiteboard
GET /api/v2/whiteboard/o/{oid}/cm                  // Load comments
POST /api/v2/whiteboard/o/{oid}/cm                 // Add comment reply

// Shared
GET /api/v2/household/{hid}/activity               // Activity feed
POST /api/v2/notifications/send                    // Push notifications
```

---

## 🎯 **IMPLEMENTATION ROADMAP**

### **Week 1-2: Foundation**
```
Backend:
✅ Whiteboard API already exists (29 endpoints)
□ Add household activity endpoint
  GET /api/v2/household/{hid}/activity
  - Aggregates whiteboard events
  - Returns last 50 activities
  - Supports pagination

□ Add "get whiteboard link" endpoints
  GET /api/v2/recipes/{rid}/whiteboard-object
  GET /api/v2/meal-plans/{mid}/whiteboard-object
  GET /api/v2/grocery-lists/{gid}/whiteboard-object
  - Returns whiteboard_object if exists
  - Null if not on any whiteboard

Mobile:
□ Create WhiteboardAPI.js service
  - Wrapper for whiteboard endpoints
  - Same pattern as YesChefAPI
  
□ Create reusable components
  - CommentsSection
  - PresenceBar
  - TagPills
  - ActivityCard
```

### **Week 3-4: HomeScreen Integration**
```
Mobile:
□ Add Household Activity section to HomeScreen
  - Fetch recent activities
  - Display activity cards
  - Implement navigation to context
  - Pull to refresh

□ Add real-time updates
  - Subscribe to Pusher channels
  - Handle activity events
  - Update UI in real-time
  
□ Push notification setup
  - Register device token
  - Handle notification taps
  - Deep linking to content
```

### **Week 5-6: Recipe & Comments**
```
Mobile:
□ Enhance RecipeViewScreen
  - Add CommentsSection component
  - Add TagPills component
  - Add PresenceBar component
  - Load whiteboard link
  
□ Implement comment features
  - Post comment
  - Reply to comment (threading)
  - React with emoji
  - @mention support
  
□ Tag functionality
  - Display existing tags
  - Filter by tag (navigate to search)
  - Add new tags (modal)
```

### **Week 7-8: Grocery & Meal Planning**
```
Mobile:
□ Enhance GroceryListScreen
  - Add active shoppers banner
  - Add recent changes feed
  - Add list comments
  - Real-time sync via Pusher
  
□ Enhance MealPlanScreen
  - Add household presence
  - Add day-level comments
  - Add tag filtering
  - Generate grocery list button
```

### **Week 9-10: Polish & Testing**
```
Mobile:
□ Notification handling
  - Test all notification types
  - Deep linking works
  - Badge counts accurate
  
□ Real-time sync
  - Test presence updates
  - Test comment sync
  - Test grocery list sync
  
□ Error handling
  - Offline mode
  - Conflict resolution
  - Retry logic
```

---

## ✅ **SUCCESS METRICS**

### **User Engagement:**
- 70%+ of household members add at least 1 comment per week
- 50%+ of recipes have at least 1 tag
- 80%+ of meal plans are shared with household
- 60%+ of users check household activity feed daily

### **Technical Performance:**
- Comment post <500ms
- Real-time updates <2 seconds
- Notification delivery 95%+ success rate
- Zero data conflicts between desktop/mobile

### **User Feedback:**
- "Feels natural, like commenting on Instagram"
- "Didn't realize I was using 'whiteboard' features"
- "Love seeing what my family is planning"
- "Comments make meal planning collaborative, not lonely"

---

## 🎉 **KEY ADVANTAGES OF THIS APPROACH**

1. **Zero Learning Curve**
   - Users already know recipes, lists, meal plans
   - Comments work like social media
   - Tags are familiar from everywhere

2. **Progressive Discovery**
   - Start with one comment
   - Discover tags later
   - Gradually engage with household

3. **Desktop Independence**
   - Mobile users get full value alone
   - Desktop whiteboard is optional power feature
   - Same data, different visualization

4. **Household Collaboration**
   - Natural async communication
   - Real-time presence awareness
   - Activity feed keeps everyone informed

5. **Future-Proof**
   - All backend infrastructure reusable
   - Can add tablet canvas view later
   - Can expand to more entities (pantry, recipes)

---

**This is the path forward: Invisible integration, maximum collaboration, zero complexity.**
