# 🔍 Friends & Household Features - v2 Migration Status

**Date:** October 21, 2025  
**Status:** ❌ **NOT MIGRATED TO V2**  
**Priority:** HIGH (Social features are critical for user engagement)

---

## 📊 **CURRENT STATE**

### **v1 API (Existing)**
Friends and Household features are **fully implemented in v1** (`hungie_server.py`):

#### **Friends API (6 endpoints):**
1. ✅ `GET /api/friends/list` - Get user's friends list
2. ✅ `GET /api/friends/requests` - Get pending friend requests
3. ✅ `POST /api/friends/request` - Send friend request
4. ✅ `POST /api/friends/request/<id>/accept` - Accept friend request
5. ✅ `POST /api/friends/request/<id>/decline` - Decline friend request
6. ✅ `DELETE /api/friends/<id>/remove` - Remove friend

#### **Household API (6 endpoints):**
1. ✅ `GET /api/households/list` - Get user's households
2. ✅ `POST /api/households/create` - Create household
3. ✅ `DELETE /api/households/<id>/delete` - Delete household
4. ✅ `POST /api/households/<id>/members/add` - Add member to household
5. ✅ `DELETE /api/households/<id>/members/<member_id>/remove` - Remove member
6. ✅ `GET /api/households/<id>/members` - Get household members

**Total:** 12 social endpoints in v1

---

### **v2 API (Missing)**
Friends and Household features are **NOT implemented in v2**:

- ❌ No Friends API in v2
- ❌ No Household API in v2
- ❌ No social repositories
- ❌ No social services
- ❌ No social routes

**Current v2 APIs:**
- ✅ Users API
- ✅ Recipes API
- ✅ Meal Plans API
- ✅ Grocery Lists API

---

## 🗄️ **DATABASE TABLES**

### **Existing Social Tables:**
The database has these social tables (created by `init_social_db.py`):

1. **`friend_requests`** - Friend request management
   - requester_id, recipient_id
   - message, status (pending/accepted/declined)
   - timestamps

2. **`friendships`** - Active friendships
   - user_id, friend_id
   - status, created_at

3. **`households`** - Household groups
   - name, owner_id
   - created_at, updated_at

4. **`household_members`** - Household membership
   - household_id, user_id
   - role (owner/admin/member)
   - joined_at

---

## 🎯 **WHY MIGRATE TO V2?**

### **Benefits:**
1. ✅ **Consistency** - All APIs in v2 architecture
2. ✅ **Clean Code** - Repository pattern, service layer
3. ✅ **Better Testing** - Easier to test and maintain
4. ✅ **Performance** - Connection pooling, optimization
5. ✅ **Scalability** - Cleaner architecture for growth
6. ✅ **Documentation** - OpenAPI spec, API reference

### **Current Problems:**
1. ❌ Social features stuck in old architecture
2. ❌ No documentation for social APIs
3. ❌ Mixed v1/v2 usage in mobile app
4. ❌ Can't retire v1 until social features migrated
5. ❌ Inconsistent error handling

---

## 📋 **MIGRATION PLAN**

### **Phase 1: Friends API Migration**

#### **1.1 Create Friends Repository**
```
app/database/repositories/friends_repository.py
```

**Methods needed:**
- `get_user_friends(user_id)` - Get all friends
- `get_friend_requests(user_id)` - Get pending requests
- `send_friend_request(requester_id, recipient_id, message)` - Send request
- `accept_friend_request(request_id)` - Accept request
- `decline_friend_request(request_id)` - Decline request
- `remove_friend(user_id, friend_id)` - Remove friendship
- `get_friendship_status(user1_id, user2_id)` - Check status

#### **1.2 Create Friends Service**
```
app/services/friends_service.py
```

**Business logic:**
- Validate friend requests
- Prevent duplicate friendships
- Handle bidirectional relationships
- Calculate shared content stats

#### **1.3 Create Friends Routes**
```
app/api/v2/friends.py
```

**Endpoints:**
- `GET /api/v2/friends/user/{userId}` - Get friends list
- `GET /api/v2/friends/requests` - Get pending requests
- `POST /api/v2/friends/request` - Send friend request
- `POST /api/v2/friends/request/{requestId}/accept` - Accept
- `POST /api/v2/friends/request/{requestId}/decline` - Decline
- `DELETE /api/v2/friends/{friendId}` - Remove friend

---

### **Phase 2: Household API Migration**

#### **2.1 Create Household Repository**
```
app/database/repositories/household_repository.py
```

**Methods needed:**
- `get_user_households(user_id)` - Get user's households
- `get_household_by_id(household_id)` - Get household details
- `create_household(owner_id, name)` - Create household
- `delete_household(household_id)` - Delete household
- `add_member(household_id, user_id, role)` - Add member
- `remove_member(household_id, user_id)` - Remove member
- `get_household_members(household_id)` - Get members
- `update_member_role(household_id, user_id, role)` - Update role

#### **2.2 Create Household Service**
```
app/services/household_service.py
```

**Business logic:**
- Validate household operations
- Check permissions (owner/admin/member)
- Prevent duplicate memberships
- Calculate household stats (shared recipes, lists, etc.)

#### **2.3 Create Household Routes**
```
app/api/v2/households.py
```

**Endpoints:**
- `GET /api/v2/households/user/{userId}` - Get user's households
- `GET /api/v2/households/{householdId}` - Get household details
- `POST /api/v2/households` - Create household
- `DELETE /api/v2/households/{householdId}` - Delete household
- `POST /api/v2/households/{householdId}/members` - Add member
- `DELETE /api/v2/households/{householdId}/members/{userId}` - Remove member
- `GET /api/v2/households/{householdId}/members` - Get members

---

### **Phase 3: Testing & Documentation**

#### **3.1 Create Tests**
- Unit tests for repositories
- Unit tests for services
- Integration tests for API routes
- End-to-end tests for workflows

#### **3.2 Update Documentation**
- Add to OpenAPI spec
- Add to API Reference
- Add to Quick Start guide
- Create migration guide (v1 social → v2 social)

#### **3.3 Update Mobile App**
- Update friends screens to use v2
- Update household screens to use v2
- Test all social features
- Deploy with feature flags

---

## ⏱️ **ESTIMATED EFFORT**

### **Phase 1: Friends API (8-10 hours)**
- Repository: 2 hours
- Service: 2 hours
- Routes: 2 hours
- Testing: 2 hours
- Documentation: 2 hours

### **Phase 2: Household API (8-10 hours)**
- Repository: 2 hours
- Service: 2 hours
- Routes: 2 hours
- Testing: 2 hours
- Documentation: 2 hours

### **Phase 3: Integration (4-6 hours)**
- Mobile app updates: 3 hours
- End-to-end testing: 2 hours
- Deployment: 1 hour

**Total: 20-26 hours (3-4 days of work)**

---

## 🎯 **RECOMMENDATION**

### **Option 1: Migrate Now (Recommended)**
**Before doing performance optimization**

**Pros:**
- ✅ Complete v2 API (all features)
- ✅ Can retire v1 completely
- ✅ Consistent architecture
- ✅ Better for long-term maintenance
- ✅ All features documented

**Cons:**
- ❌ Delays performance work
- ❌ Additional 20-26 hours work

---

### **Option 2: Migrate Later**
**After performance optimization**

**Pros:**
- ✅ Faster to performance optimization
- ✅ Can optimize existing v2 APIs first
- ✅ Social features already working in v1

**Cons:**
- ❌ Can't retire v1 yet
- ❌ Mixed architecture confusion
- ❌ Mobile app uses both v1 and v2
- ❌ Inconsistent API experience

---

### **Option 3: Hybrid Approach**
**Do Friends first, Household later**

**Pros:**
- ✅ Gets most-used feature (Friends) into v2
- ✅ Allows partial v1 retirement
- ✅ Spreads out work

**Cons:**
- ❌ Still need v1 for Households
- ❌ Partial migration complexity

---

## 💡 **MY RECOMMENDATION: OPTION 1**

**Migrate Friends & Household to v2 NOW, before performance optimization.**

**Reasoning:**
1. Social features are **core functionality**
2. Need **complete v2 API** before going to production
3. Performance optimization should work on **complete API**, not partial
4. Better to have **all features in one architecture**
5. Can't truly "complete" v2 without social features
6. Mobile app should use **one API version**, not mixed

**Timeline:**
- Week 1: Friends API migration (2-3 days)
- Week 2: Household API migration (2-3 days)
- Week 3: Testing & mobile app integration (1-2 days)
- Then: Performance optimization on complete v2 API

---

## 🚀 **NEXT STEPS**

If you agree with Option 1, I can:

1. **Create Friends Repository** (30 min)
2. **Create Friends Service** (30 min)
3. **Create Friends Routes** (30 min)
4. **Create Tests** (30 min)
5. **Repeat for Household** (2 hours)
6. **Update Documentation** (1 hour)

**We can have social features in v2 within 1 day of focused work!**

---

## 📊 **COMPLETION STATUS**

### **Before Adding Social Features:**
```
v2 API Completion: 66% (4/6 major features)
✅ Users
✅ Recipes
✅ Meal Plans
✅ Grocery Lists
❌ Friends
❌ Households
```

### **After Adding Social Features:**
```
v2 API Completion: 100% (6/6 major features)
✅ Users
✅ Recipes
✅ Meal Plans
✅ Grocery Lists
✅ Friends
✅ Households
```

---

## ❓ **DECISION TIME**

**What would you like to do?**

**A)** Migrate Friends & Household to v2 now (Recommended) ⭐
**B)** Skip for now, do performance optimization first
**C)** Just do Friends, save Household for later
**D)** Check what mobile app actually uses before deciding

---

**Let me know your preference and I'll get started!** 😊
