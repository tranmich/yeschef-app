# 🔄 YesChef API Migration Guide: v1 → v2

**Complete guide for migrating from API v1 to v2**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Key Changes](#key-changes)
3. [Breaking Changes](#breaking-changes)
4. [Migration Checklist](#migration-checklist)
5. [Endpoint Mapping](#endpoint-mapping)
6. [Code Examples](#code-examples)
7. [Testing Strategy](#testing-strategy)
8. [Rollback Plan](#rollback-plan)

---

## 🎯 Overview

### **Why Migrate?**
- ✅ Modern 3-layer architecture
- ✅ PostgreSQL database (from SQLite)
- ✅ 51 new endpoints (51 → 101)
- ✅ Improved performance
- ✅ Better error handling
- ✅ Standardized responses
- ✅ Production-ready infrastructure

### **Migration Timeline**
- **Preparation:** 1-2 days
- **Testing:** 2-3 days
- **Deployment:** 1 day
- **Monitoring:** 1 week

### **Risk Level:** 🟡 **Low-Medium**
- Database migration handled automatically
- Old endpoints still work during transition
- Gradual rollout possible

---

## 🔑 Key Changes

### **1. Base URL Change**
```
OLD: https://yeschefapp-production.up.railway.app/api/v1
NEW: https://yeschefapp-production.up.railway.app/api/v2
```

### **2. Response Format**
**OLD (v1):**
```json
{
  "id": 10,
  "name": "Recipe Name",
  "ingredients": [...]
}
```

**NEW (v2):**
```json
{
  "success": true,
  "data": {
    "id": 10,
    "name": "Recipe Name",
    "ingredients": [...]
  }
}
```

### **3. Error Responses**
**OLD (v1):**
```json
{
  "error": "Recipe not found"
}
```

**NEW (v2):**
```json
{
  "success": false,
  "error": "Recipe not found"
}
```

### **4. Authentication**
**OLD:** Mixed patterns  
**NEW:** Consistent `user_id` in all requests

### **5. Database**
**OLD:** SQLite  
**NEW:** PostgreSQL on Railway

---

## ⚠️ Breaking Changes

### **1. Response Structure**
All responses now wrapped in `{success, data}` object.

**Migration:** Update response parsing in client code.

### **2. Date Formats**
**OLD:** Mixed formats  
**NEW:** ISO 8601 format (`2025-10-21T10:00:00Z`)

### **3. Pagination**
**OLD:** Inconsistent  
**NEW:** Standardized `{limit, offset, total}`

### **4. Status Codes**
**OLD:** Inconsistent  
**NEW:** Proper REST status codes (200, 201, 400, 404, 500)

### **5. Field Names**
Some fields renamed for consistency:
- `recipe_data` → `data`
- `meal_plan_data` → `meals`
- `items_list` → `items`

---

## ✅ Migration Checklist

### **Phase 1: Preparation** (Day 1-2)

- [ ] Review API v2 documentation
- [ ] Identify all v1 API calls in codebase
- [ ] Create migration branch in Git
- [ ] Set up testing environment
- [ ] Backup production database
- [ ] Update environment variables

### **Phase 2: Code Updates** (Day 3-4)

- [ ] Update base URL to v2
- [ ] Update response parsing (add `.data` access)
- [ ] Update error handling (check `.success` field)
- [ ] Update authentication (ensure `user_id` included)
- [ ] Update date parsing (ISO 8601)
- [ ] Update pagination handling
- [ ] Update all endpoint paths

### **Phase 3: Testing** (Day 5-7)

- [ ] Unit tests (all API calls)
- [ ] Integration tests (full workflows)
- [ ] UI/UX testing (all screens)
- [ ] Performance testing
- [ ] Error handling testing
- [ ] Edge case testing

### **Phase 4: Deployment** (Day 8)

- [ ] Deploy to staging environment
- [ ] Run smoke tests
- [ ] Deploy to production (gradual rollout)
- [ ] Monitor error rates
- [ ] Monitor performance metrics
- [ ] Enable for all users

### **Phase 5: Cleanup** (Day 9-14)

- [ ] Monitor production for 1 week
- [ ] Fix any issues
- [ ] Remove v1 code (after 2 weeks)
- [ ] Update documentation
- [ ] Celebrate! 🎉

---

## 🗺️ Endpoint Mapping

### **Users**
| v1 Endpoint | v2 Endpoint | Notes |
|-------------|-------------|-------|
| GET /users/:id | GET /api/v2/users/:id | Response format changed |
| POST /users | POST /api/v2/users | Same |
| PATCH /users/:id | PATCH /api/v2/users/:id | Same |

### **Recipes**
| v1 Endpoint | v2 Endpoint | Notes |
|-------------|-------------|-------|
| GET /recipes/:id | GET /api/v2/recipes/:id | Response format changed |
| GET /recipes/user/:id | GET /api/v2/recipes/user/:id | Same |
| POST /recipes | POST /api/v2/recipes | Validation improved |
| PATCH /recipes/:id | PATCH /api/v2/recipes/:id | Same |
| DELETE /recipes/:id | DELETE /api/v2/recipes/:id | Cascade delete added |

### **New Endpoints in v2**
These are brand new - no v1 equivalent:
- ✨ Community API (8 endpoints)
- ✨ Favorites API (5 endpoints)
- ✨ Profile API (6 endpoints)
- ✨ Pantry API (10 endpoints)
- ✨ Recipe Search API (8 endpoints)
- ✨ System API (11 endpoints)

---

## 💻 Code Examples

### **React Native - Before (v1)**

```javascript
// OLD CODE
const fetchRecipe = async (recipeId) => {
  try {
    const response = await fetch(
      `https://yeschefapp-production.up.railway.app/api/v1/recipes/${recipeId}`
    );
    const recipe = await response.json();
    
    // Handle errors
    if (recipe.error) {
      console.error(recipe.error);
      return null;
    }
    
    return recipe;
  } catch (error) {
    console.error(error);
    return null;
  }
};
```

### **React Native - After (v2)**

```javascript
// NEW CODE
const fetchRecipe = async (recipeId) => {
  try {
    const response = await fetch(
      `https://yeschefapp-production.up.railway.app/api/v2/recipes/${recipeId}`
    );
    const result = await response.json();
    
    // Check success field
    if (!result.success) {
      console.error(result.error);
      return null;
    }
    
    // Access data from result.data
    return result.data;
  } catch (error) {
    console.error(error);
    return null;
  }
};
```

### **Python - Before (v1)**

```python
# OLD CODE
import requests

def get_recipe(recipe_id):
    response = requests.get(
        f"https://yeschefapp-production.up.railway.app/api/v1/recipes/{recipe_id}"
    )
    recipe = response.json()
    
    if 'error' in recipe:
        print(f"Error: {recipe['error']}")
        return None
    
    return recipe
```

### **Python - After (v2)**

```python
# NEW CODE
import requests

def get_recipe(recipe_id):
    response = requests.get(
        f"https://yeschefapp-production.up.railway.app/api/v2/recipes/{recipe_id}"
    )
    result = response.json()
    
    if not result.get('success'):
        print(f"Error: {result.get('error')}")
        return None
    
    return result.get('data')
```

---

## 🎯 Migration Patterns

### **Pattern 1: Simple GET Request**

```javascript
// Before
const data = await fetch('/api/v1/recipes/10').then(r => r.json());

// After
const result = await fetch('/api/v2/recipes/10').then(r => r.json());
const data = result.success ? result.data : null;
```

### **Pattern 2: POST Request**

```javascript
// Before
const recipe = await fetch('/api/v1/recipes', {
  method: 'POST',
  body: JSON.stringify({
    title: 'Recipe',
    ingredients: [...]
  })
}).then(r => r.json());

// After
const result = await fetch('/api/v2/recipes', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_id: 10,  // NOW REQUIRED
    title: 'Recipe',
    ingredients: [...]
  })
}).then(r => r.json());

const recipe = result.success ? result.data : null;
```

### **Pattern 3: Error Handling**

```javascript
// Before
if (response.error) {
  showError(response.error);
}

// After
if (!response.success) {
  showError(response.error);
}
```

### **Pattern 4: Pagination**

```javascript
// Before
const recipes = await fetch('/api/v1/recipes/user/10?page=2&size=20')
  .then(r => r.json());

// After
const result = await fetch('/api/v2/recipes/user/10?limit=20&offset=20')
  .then(r => r.json());

const recipes = result.data;
const pagination = result.pagination; // {limit, offset, total}
```

---

## 🧪 Testing Strategy

### **1. Create Test Environment**

```bash
# Set environment variable
export API_VERSION=v2

# Or in .env file
API_BASE_URL=https://yeschefapp-production.up.railway.app/api/v2
```

### **2. Test Checklist**

**Core Functionality:**
- [ ] User login/registration
- [ ] Recipe CRUD operations
- [ ] Meal plan creation
- [ ] Grocery list generation
- [ ] Recipe search
- [ ] Community features
- [ ] Profile updates

**Edge Cases:**
- [ ] Empty responses
- [ ] Network errors
- [ ] Invalid input
- [ ] Permission errors
- [ ] Concurrent requests

**Performance:**
- [ ] Response times < 500ms
- [ ] Large dataset handling
- [ ] Image uploads
- [ ] Bulk operations

### **3. Automated Tests**

```javascript
// Example Jest test
describe('API v2 Migration', () => {
  test('should fetch recipe with new format', async () => {
    const result = await fetchRecipe(10);
    
    expect(result).toHaveProperty('success');
    expect(result).toHaveProperty('data');
    expect(result.success).toBe(true);
    expect(result.data).toHaveProperty('id');
    expect(result.data).toHaveProperty('title');
  });
  
  test('should handle errors correctly', async () => {
    const result = await fetchRecipe(99999);
    
    expect(result.success).toBe(false);
    expect(result).toHaveProperty('error');
  });
});
```

---

## 🔙 Rollback Plan

### **If Issues Occur:**

1. **Immediate Rollback** (< 5 minutes)
   ```bash
   # Switch back to v1
   export API_VERSION=v1
   # Redeploy app
   ```

2. **Database Rollback** (if needed)
   ```bash
   # Restore from backup
   psql $DATABASE_URL < backup_pre_migration.sql
   ```

3. **Communication**
   - Notify users of temporary issues
   - Update status page
   - Log all incidents

---

## 📊 Success Metrics

### **Monitor These:**
- Error rate (should be < 0.1%)
- Response times (should be < 500ms avg)
- API call success rate (should be > 99%)
- User-reported issues (should be minimal)
- App crash rate (should remain stable)

### **Success Criteria:**
- ✅ All endpoints responding correctly
- ✅ Error rate < 0.1%
- ✅ No increase in crash rate
- ✅ User satisfaction maintained
- ✅ Performance improved or equal

---

## 🚀 Gradual Rollout Strategy

### **Option 1: Feature Flag**
```javascript
const API_VERSION = getFeatureFlag('api_v2_enabled') ? 'v2' : 'v1';
const API_BASE = `${BASE_URL}/api/${API_VERSION}`;
```

### **Option 2: User Percentage**
```javascript
// Enable for 10% of users initially
const userId = getCurrentUser().id;
const useV2 = (userId % 10) === 0;
```

### **Option 3: Platform**
```javascript
// Enable for Android first, then iOS
const useV2 = Platform.OS === 'android';
```

---

## 📞 Support During Migration

### **Need Help?**
- 📧 Email: dev@yeschefapp.com
- 📱 Slack: #api-migration
- 📚 Docs: /docs/API_DOCUMENTATION.md
- 🐛 Issues: GitHub Issues

### **Migration Office Hours**
- Monday-Friday: 9am-5pm EST
- Response time: < 2 hours
- Emergency: < 30 minutes

---

## ✅ Post-Migration

### **Week 1: Monitor Closely**
- Check error logs daily
- Monitor performance metrics
- Respond to user feedback
- Fix any issues immediately

### **Week 2: Stabilize**
- Continue monitoring
- Optimize slow endpoints
- Update documentation
- Gather user feedback

### **Week 3-4: Cleanup**
- Remove v1 fallbacks
- Clean up old code
- Archive v1 documentation
- Celebrate success! 🎉

---

## 🎉 Benefits After Migration

### **Immediate:**
- ✅ Access to 51 new features
- ✅ Better error handling
- ✅ Improved performance
- ✅ Standardized responses

### **Long-term:**
- ✅ Easier maintenance
- ✅ Scalable architecture
- ✅ Better testing
- ✅ Future-proof infrastructure

---

**Last Updated:** October 21, 2025  
**Version:** 2.0.0  
**Status:** ✅ Ready for Migration

🚀 **Good luck with your migration!** 🚀
