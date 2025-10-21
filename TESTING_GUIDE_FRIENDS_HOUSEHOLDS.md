# 🧪 MANUAL TESTING GUIDE - Friends & Households API v2

**Quick reference for testing all 16 endpoints manually**

---

## 📋 PREREQUISITES

1. Server running on `http://localhost:5000`
2. Database initialized with users table
3. At least 2-3 test users in database

---

## 🎯 TEST SUITE 1: FRIENDS API (7 endpoints)

### 1.1 Get User Friends
```bash
# Get all friends for user ID 1
curl http://localhost:5000/api/v2/friends/user/1

# Expected response:
{
  "success": true,
  "data": {
    "friends": [...],
    "count": 0
  }
}
```

---

### 1.2 Get Friend Requests
```bash
# Get incoming and outgoing friend requests
curl http://localhost:5000/api/v2/friends/requests/user/1

# Expected response:
{
  "success": true,
  "data": {
    "requests": [...],
    "incoming": [...],
    "outgoing": [...],
    "incoming_count": 0,
    "outgoing_count": 0
  }
}
```

---

### 1.3 Send Friend Request
```bash
# Send friend request by email (User 1 → User 2)
curl -X POST http://localhost:5000/api/v2/friends/request \
  -H "Content-Type: application/json" \
  -d '{
    "requester_id": 1,
    "recipient_email": "user2@example.com",
    "message": "Let's be friends!"
  }'

# Expected response:
{
  "success": true,
  "data": {
    "id": 1,
    "requester_id": 1,
    "recipient_id": 2,
    "message": "Let's be friends!",
    "status": "pending",
    "created_at": "2025-10-21T12:00:00"
  },
  "message": "Friend request sent to User Two"
}
```

---

### 1.4 Accept Friend Request
```bash
# Accept request (User 2 accepts User 1's request)
curl -X POST http://localhost:5000/api/v2/friends/request/1/accept \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 2
  }'

# Expected response:
{
  "success": true,
  "data": {
    "request": {...},
    "friendship": {...}
  },
  "message": "You are now friends with User One"
}
```

---

### 1.5 Decline Friend Request
```bash
# Decline request (User 2 declines User 1's request)
curl -X POST http://localhost:5000/api/v2/friends/request/1/decline \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 2
  }'

# Expected response:
{
  "success": true,
  "data": {...},
  "message": "Friend request declined"
}
```

---

### 1.6 Check Friendship Status
```bash
# Check relationship between User 1 and User 2
curl "http://localhost:5000/api/v2/friends/status?user_id=1&other_user_id=2"

# Expected response:
{
  "success": true,
  "data": {
    "user_id": 1,
    "other_user_id": 2,
    "status": "friends"  
    # or "request_sent", "request_received", "none"
  }
}
```

---

### 1.7 Remove Friend
```bash
# Unfriend User 2 (as User 1)
curl -X DELETE "http://localhost:5000/api/v2/friends/2?user_id=1"

# Expected response:
{
  "success": true,
  "message": "Friend removed successfully"
}
```

---

## 🏠 TEST SUITE 2: HOUSEHOLDS API (9 endpoints)

### 2.1 Get User Households
```bash
# Get all households for User 1
curl http://localhost:5000/api/v2/households/user/1

# Expected response:
{
  "success": true,
  "data": {
    "households": [
      {
        "id": 1,
        "name": "Family",
        "description": "Our family household",
        "created_by": 1,
        "creator_name": "User One",
        "user_role": "owner",
        "member_count": 1,
        "is_active": true,
        "created_at": "2025-10-21T10:00:00"
      }
    ],
    "count": 1
  }
}
```

---

### 2.2 Create Household
```bash
# Create new household
curl -X POST http://localhost:5000/api/v2/households \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Family",
    "created_by": 1,
    "description": "Our family household"
  }'

# Expected response:
{
  "success": true,
  "data": {
    "household": {
      "id": 1,
      "name": "My Family",
      "description": "Our family household",
      "created_by": 1,
      "is_active": true,
      "created_at": "2025-10-21T12:00:00"
    },
    "membership": {
      "id": 1,
      "household_id": 1,
      "user_id": 1,
      "role": "owner"
    }
  },
  "message": "Household 'My Family' created successfully"
}
```

---

### 2.3 Get Household Details
```bash
# Get household by ID with members
curl "http://localhost:5000/api/v2/households/1?user_id=1"

# Expected response:
{
  "success": true,
  "data": {
    "household": {...},
    "members": [...]
  }
}
```

---

### 2.4 Update Household
```bash
# Update household details
curl -X PUT http://localhost:5000/api/v2/households/1 \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "name": "Updated Family Name",
    "description": "New description"
  }'

# Expected response:
{
  "success": true,
  "data": {...},
  "message": "Household updated successfully"
}
```

---

### 2.5 Get Household Members
```bash
# Get all members of household
curl "http://localhost:5000/api/v2/households/1/members?user_id=1"

# Expected response:
{
  "success": true,
  "data": {
    "members": [
      {
        "membership_id": 1,
        "household_id": 1,
        "user_id": 1,
        "user_name": "User One",
        "user_email": "user1@example.com",
        "role": "owner",
        "joined_at": "2025-10-21T10:00:00"
      }
    ],
    "count": 1
  }
}
```

---

### 2.6 Add Member to Household
```bash
# Add User 2 to household (User 1 and 2 must be friends first!)
curl -X POST http://localhost:5000/api/v2/households/1/members \
  -H "Content-Type: application/json" \
  -d '{
    "requesting_user_id": 1,
    "user_id": 2,
    "role": "member"
  }'

# Expected response:
{
  "success": true,
  "data": {...},
  "message": "Member added to household successfully"
}
```

---

### 2.7 Update Member Role
```bash
# Update User 2's role to admin
curl -X PUT http://localhost:5000/api/v2/households/1/members/2/role \
  -H "Content-Type: application/json" \
  -d '{
    "requesting_user_id": 1,
    "role": "admin"
  }'

# Expected response:
{
  "success": true,
  "data": {...},
  "message": "Member role updated to admin"
}
```

---

### 2.8 Remove Member from Household
```bash
# Remove User 2 from household
curl -X DELETE "http://localhost:5000/api/v2/households/1/members/2?user_id=1"

# Expected response:
{
  "success": true,
  "message": "Member removed from household successfully"
}
```

---

### 2.9 Delete Household
```bash
# Delete household (soft delete)
curl -X DELETE "http://localhost:5000/api/v2/households/1?user_id=1"

# Expected response:
{
  "success": true,
  "message": "Household deleted successfully"
}
```

---

## ✅ TESTING CHECKLIST

### Friends API:
- [ ] Get friends list (empty initially)
- [ ] Get friend requests (empty initially)
- [ ] Send friend request by email
- [ ] Verify outgoing request appears
- [ ] Accept friend request (as recipient)
- [ ] Verify friendship created bidirectionally
- [ ] Check friendship status
- [ ] Remove friend
- [ ] Verify friendship removed bidirectionally

### Households API:
- [ ] Get households list (empty initially)
- [ ] Create new household
- [ ] Verify creator is owner
- [ ] Get household details with members
- [ ] Update household name/description
- [ ] Get household members
- [ ] Add friend as member
- [ ] Update member role
- [ ] Remove member
- [ ] Delete household

---

## 🔴 ERROR CASES TO TEST

### Friends API:
- [ ] Send request to non-existent email (should fail)
- [ ] Send request to yourself (should fail)
- [ ] Send duplicate request (should fail)
- [ ] Accept request you didn't receive (should fail with UNAUTHORIZED)
- [ ] Decline already processed request (should fail)
- [ ] Remove non-friend (should fail)

### Households API:
- [ ] Create household with empty name (should fail)
- [ ] Update household as non-owner/non-admin (should fail)
- [ ] Delete household as non-owner (should fail)
- [ ] Add non-friend as member (should fail)
- [ ] Add member who's already in household (should fail)
- [ ] Remove member as regular member (should fail - only owner/admin can)
- [ ] Owner tries to leave household (should fail)
- [ ] Update role as non-owner (should fail)

---

## 🎯 QUICK START

**Run the automated test:**
```bash
cd "D:\Mik\Downloads\Me Hungie"
python test_friends_households_api.py
```

**Or test manually with curl commands above!**

---

## 📊 EXPECTED RESULTS

**All tests should:**
- ✅ Return proper HTTP status codes (200, 201, 400, 404, 500)
- ✅ Return standardized JSON responses
- ✅ Have `success: true` for successful operations
- ✅ Have `success: false` with error message for failures
- ✅ Enforce authorization rules
- ✅ Validate all inputs
- ✅ Create bidirectional relationships (friendships)
- ✅ Handle edge cases gracefully

---

**Happy Testing! 🚀**
