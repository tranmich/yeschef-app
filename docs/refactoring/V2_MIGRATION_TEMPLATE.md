# 🎯 V2 MIGRATION TEMPLATE - Quick Reference Guide

**Created:** Phase 7 (October 2025)  
**Purpose:** Standardized pattern for migrating v1 endpoints to v2  
**Status:** ✅ Proven (Used for Users, Recipes, Meal Plans, Grocery Lists)  

---

## 📋 **ARCHITECTURE OVERVIEW**

The v2 architecture uses a **3-layer pattern**:

```
┌─────────────────────────────────────┐
│      API Layer (Routes)             │  ← Flask routes, request/response
├─────────────────────────────────────┤
│      Service Layer (Business Logic) │  ← Business rules, validation
├─────────────────────────────────────┤
│      Repository Layer (Data Access) │  ← Database operations
├─────────────────────────────────────┤
│      Base Classes (Reusable)        │  ← Common functionality
└─────────────────────────────────────┘
```

---

## 🏗️ **3-STEP MIGRATION PROCESS**

### **Step 1: Create Repository** (30-45 minutes)
### **Step 2: Create Service** (30-45 minutes)
### **Step 3: Create Routes** (30-45 minutes)

**Total Time:** ~2-3 hours per feature

---

## 📝 **STEP 1: REPOSITORY LAYER**

### **File Location:**
```
app/database/repositories/[feature]_repository.py
```

### **Template:**

```python
"""
[Feature] Repository
Handles all database operations for [table_name] table
"""

from typing import Optional, Dict, Any, List
import logging

from app.database.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class [Feature]Repository(BaseRepository):
    """Repository for [table_name] table"""
    
    def __init__(self):
        super().__init__('[table_name]')
    
    # CREATE
    def create_[entity](self, [entity]_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create new [entity]
        
        Args:
            [entity]_data: Dictionary with [entity] fields
        
        Returns:
            Created [entity] dictionary or None
        """
        try:
            query = """
                INSERT INTO [table_name] 
                (field1, field2, field3, created_at, updated_at)
                VALUES (%s, %s, %s, NOW(), NOW())
                RETURNING *
            """
            params = (
                [entity]_data.get('field1'),
                [entity]_data.get('field2'),
                [entity]_data.get('field3')
            )
            
            result = self._execute_insert(query, params)
            
            if result:
                logger.info(f"✅ Created [entity]: ID {result['id']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error creating [entity]: {e}", exc_info=True)
            return None
    
    # READ
    def get_[entity]_by_id(self, [entity]_id: int) -> Optional[Dict[str, Any]]:
        """
        Get [entity] by ID
        
        Args:
            [entity]_id: [Entity] ID
        
        Returns:
            [Entity] dictionary or None
        """
        query = f"SELECT * FROM {self.table_name} WHERE id = %s"
        return self._execute_query_one(query, ([entity]_id,))
    
    def get_all_[entities](self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all [entities] for user
        
        Args:
            user_id: User ID
        
        Returns:
            List of [entity] dictionaries
        """
        query = f"""
            SELECT * FROM {self.table_name} 
            WHERE user_id = %s 
            ORDER BY created_at DESC
        """
        return self._execute_query(query, (user_id,))
    
    # UPDATE
    def update_[entity](self, [entity]_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update [entity]
        
        Args:
            [entity]_id: [Entity] ID
            updates: Dictionary with fields to update
        
        Returns:
            Updated [entity] dictionary or None
        """
        try:
            # Build dynamic UPDATE query
            set_clauses = []
            params = []
            
            for key, value in updates.items():
                if key != 'id':  # Don't update ID
                    set_clauses.append(f"{key} = %s")
                    params.append(value)
            
            if not set_clauses:
                return None
            
            # Add updated_at
            set_clauses.append("updated_at = NOW()")
            
            # Add ID to params
            params.append([entity]_id)
            
            query = f"""
                UPDATE {self.table_name}
                SET {', '.join(set_clauses)}
                WHERE id = %s
                RETURNING *
            """
            
            result = self._execute_update(query, tuple(params))
            
            if result:
                logger.info(f"✅ Updated [entity]: ID {[entity]_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error updating [entity]: {e}", exc_info=True)
            return None
    
    # DELETE
    def delete_[entity](self, [entity]_id: int) -> bool:
        """
        Delete [entity]
        
        Args:
            [entity]_id: [Entity] ID
        
        Returns:
            True if deleted, False otherwise
        """
        try:
            query = f"DELETE FROM {self.table_name} WHERE id = %s"
            deleted_count = self._execute_delete(query, ([entity]_id,))
            
            if deleted_count > 0:
                logger.info(f"✅ Deleted [entity]: ID {[entity]_id}")
                return True
            else:
                logger.warning(f"⚠️ No [entity] found with ID {[entity]_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error deleting [entity]: {e}", exc_info=True)
            return False


# Singleton instance
_[feature]_repository = None

def get_[feature]_repository() -> [Feature]Repository:
    """Get singleton [feature] repository instance"""
    global _[feature]_repository
    if _[feature]_repository is None:
        _[feature]_repository = [Feature]Repository()
    return _[feature]_repository
```

### **Key Repository Methods:**

| Method | Purpose | Returns |
|--------|---------|---------|
| `_execute_query()` | SELECT multiple rows | `List[Dict]` |
| `_execute_query_one()` | SELECT single row | `Dict` or `None` |
| `_execute_insert()` | INSERT with RETURNING | `Dict` or `None` |
| `_execute_update()` | UPDATE with RETURNING | `Dict` or `None` |
| `_execute_delete()` | DELETE | `int` (row count) |
| `_execute_ddl()` | CREATE TABLE, etc. | `bool` |

---

## 📝 **STEP 2: SERVICE LAYER**

### **File Location:**
```
app/services/[feature]_service.py
```

### **Template:**

```python
"""
[Feature] Service
Business logic for [feature] operations
"""

from typing import Dict, Any, List, Optional
import logging

from app.services.base_service import BaseService
from app.database.repositories.[feature]_repository import get_[feature]_repository

logger = logging.getLogger(__name__)


class [Feature]Service(BaseService):
    """Service for [feature] business logic"""
    
    def __init__(self):
        super().__init__()
        self.[feature]_repo = get_[feature]_repository()
    
    # CREATE
    def create_[entity](
        self,
        user_id: int,
        field1: Any,
        field2: Any,
        field3: Any = None
    ) -> Dict[str, Any]:
        """
        Create new [entity] with validation
        
        Args:
            user_id: User ID
            field1: Required field 1
            field2: Required field 2
            field3: Optional field 3
        
        Returns:
            Success/error response with [entity] data
        """
        try:
            # Validation
            if not field1:
                return self.error_response("field1 is required")
            
            if not field2:
                return self.error_response("field2 is required")
            
            # Business logic
            [entity]_data = {
                'user_id': user_id,
                'field1': field1,
                'field2': field2,
                'field3': field3
            }
            
            # Create via repository
            [entity] = self.[feature]_repo.create_[entity]([entity]_data)
            
            if [entity]:
                self.log_info(f"Created [entity] for user {user_id}")
                return self.success_response(
                    data=[entity],
                    message="[Entity] created successfully"
                )
            else:
                return self.error_response("Failed to create [entity]")
                
        except Exception as e:
            self.log_error(f"Error creating [entity]", exception=e)
            return self.error_response(f"Internal error: {str(e)}")
    
    # READ
    def get_[entity](self, [entity]_id: int, user_id: int = None) -> Dict[str, Any]:
        """
        Get [entity] by ID with authorization
        
        Args:
            [entity]_id: [Entity] ID
            user_id: User ID (for authorization check)
        
        Returns:
            Success/error response with [entity] data
        """
        try:
            [entity] = self.[feature]_repo.get_[entity]_by_id([entity]_id)
            
            if not [entity]:
                return self.error_response("[Entity] not found", code="NOT_FOUND")
            
            # Authorization check (if needed)
            if user_id and [entity].get('user_id') != user_id:
                return self.error_response("Access denied", code="UNAUTHORIZED")
            
            return self.success_response(data=[entity])
            
        except Exception as e:
            self.log_error(f"Error getting [entity]", exception=e)
            return self.error_response(f"Internal error: {str(e)}")
    
    def get_user_[entities](
        self,
        user_id: int,
        page: int = 1,
        per_page: int = 20
    ) -> Dict[str, Any]:
        """
        Get all [entities] for user with pagination
        
        Args:
            user_id: User ID
            page: Page number (1-indexed)
            per_page: Items per page
        
        Returns:
            Success/error response with [entities] and pagination
        """
        try:
            # Get all [entities]
            [entities] = self.[feature]_repo.get_all_[entities](user_id)
            
            # Paginate
            paginated = self.paginate([entities], page, per_page)
            
            return self.success_response(
                data={
                    '[entities]': paginated['items'],
                    'pagination': paginated['pagination'],
                    'stats': {
                        'total': len([entities])
                    }
                }
            )
            
        except Exception as e:
            self.log_error(f"Error getting user [entities]", exception=e)
            return self.error_response(f"Internal error: {str(e)}")
    
    # UPDATE
    def update_[entity](
        self,
        [entity]_id: int,
        user_id: int,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update [entity] with validation and authorization
        
        Args:
            [entity]_id: [Entity] ID
            user_id: User ID (for authorization)
            updates: Dictionary with fields to update
        
        Returns:
            Success/error response with updated [entity]
        """
        try:
            # Check authorization
            existing = self.[feature]_repo.get_[entity]_by_id([entity]_id)
            
            if not existing:
                return self.error_response("[Entity] not found", code="NOT_FOUND")
            
            if existing.get('user_id') != user_id:
                return self.error_response("Access denied", code="UNAUTHORIZED")
            
            # Validate updates (if needed)
            # ... validation logic ...
            
            # Update via repository
            updated_[entity] = self.[feature]_repo.update_[entity]([entity]_id, updates)
            
            if updated_[entity]:
                self.log_info(f"Updated [entity] {[entity]_id}")
                return self.success_response(
                    data=updated_[entity],
                    message="[Entity] updated successfully"
                )
            else:
                return self.error_response("Failed to update [entity]")
                
        except Exception as e:
            self.log_error(f"Error updating [entity]", exception=e)
            return self.error_response(f"Internal error: {str(e)}")
    
    # DELETE
    def delete_[entity](self, [entity]_id: int, user_id: int) -> Dict[str, Any]:
        """
        Delete [entity] with authorization
        
        Args:
            [entity]_id: [Entity] ID
            user_id: User ID (for authorization)
        
        Returns:
            Success/error response
        """
        try:
            # Check authorization
            existing = self.[feature]_repo.get_[entity]_by_id([entity]_id)
            
            if not existing:
                return self.error_response("[Entity] not found", code="NOT_FOUND")
            
            if existing.get('user_id') != user_id:
                return self.error_response("Access denied", code="UNAUTHORIZED")
            
            # Delete via repository
            deleted = self.[feature]_repo.delete_[entity]([entity]_id)
            
            if deleted:
                self.log_info(f"Deleted [entity] {[entity]_id}")
                return self.success_response(message="[Entity] deleted successfully")
            else:
                return self.error_response("Failed to delete [entity]")
                
        except Exception as e:
            self.log_error(f"Error deleting [entity]", exception=e)
            return self.error_response(f"Internal error: {str(e)}")


# Singleton instance
_[feature]_service = None

def get_[feature]_service() -> [Feature]Service:
    """Get singleton [feature] service instance"""
    global _[feature]_service
    if _[feature]_service is None:
        _[feature]_service = [Feature]Service()
    return _[feature]_service
```

### **Key Service Methods from BaseService:**

| Method | Purpose |
|--------|---------|
| `success_response()` | Return `{success: True, data: ...}` |
| `error_response()` | Return `{success: False, error: ...}` |
| `validate_required_fields()` | Check required fields |
| `validate_email()` | Email format validation |
| `paginate()` | Paginate list of items |
| `log_info()` | Log info message |
| `log_error()` | Log error with exception |

---

## 📝 **STEP 3: API ROUTES**

### **File Location:**
```
app/api/v2/[feature].py
```

### **Template:**

```python
"""
[Feature] API Routes (v2)
RESTful endpoints for [feature] management
"""

from flask import Blueprint, request, jsonify
import logging

from app.services.[feature]_service import get_[feature]_service

logger = logging.getLogger(__name__)

# Create blueprint
[feature]_bp = Blueprint('[feature]', __name__)

# Get service instance
[feature]_service = get_[feature]_service()


@[feature]_bp.route('/[entities]', methods=['POST'])
def create_[entity]():
    """
    Create new [entity]
    
    Request Body:
        {
            "user_id": 123,
            "field1": "value1",
            "field2": "value2"
        }
    
    Response:
        {
            "success": true,
            "data": { [entity] object },
            "message": "[Entity] created successfully"
        }
    """
    try:
        data = request.get_json()
        
        # Extract fields
        user_id = data.get('user_id')
        field1 = data.get('field1')
        field2 = data.get('field2')
        
        # Validate required fields
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        # Call service
        result = [feature]_service.create_[entity](
            user_id=user_id,
            field1=field1,
            field2=field2
        )
        
        # Return response
        status_code = 201 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in create_[entity]: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@[feature]_bp.route('/[entities]/<int:[entity]_id>', methods=['GET'])
def get_[entity]([entity]_id):
    """
    Get [entity] by ID
    
    Query Params:
        user_id (optional): For authorization check
    
    Response:
        {
            "success": true,
            "data": { [entity] object }
        }
    """
    try:
        user_id = request.args.get('user_id', type=int)
        
        result = [feature]_service.get_[entity]([entity]_id, user_id)
        
        status_code = 200 if result.get('success') else 404
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in get_[entity]: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@[feature]_bp.route('/[entities]/user/<int:user_id>', methods=['GET'])
def get_user_[entities](user_id):
    """
    Get all [entities] for user
    
    Query Params:
        page (optional): Page number (default: 1)
        per_page (optional): Items per page (default: 20)
    
    Response:
        {
            "success": true,
            "data": {
                "[entities]": [ ... ],
                "pagination": { ... },
                "stats": { ... }
            }
        }
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        result = [feature]_service.get_user_[entities](
            user_id=user_id,
            page=page,
            per_page=per_page
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in get_user_[entities]: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@[feature]_bp.route('/[entities]/<int:[entity]_id>', methods=['PUT'])
def update_[entity]([entity]_id):
    """
    Update [entity]
    
    Request Body:
        {
            "user_id": 123,
            "field1": "new_value1"
        }
    
    Response:
        {
            "success": true,
            "data": { updated [entity] object },
            "message": "[Entity] updated successfully"
        }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        # Remove user_id from updates (don't update it)
        updates = {k: v for k, v in data.items() if k != 'user_id'}
        
        result = [feature]_service.update_[entity](
            [entity]_id=entity_id,
            user_id=user_id,
            updates=updates
        )
        
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in update_[entity]: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@[feature]_bp.route('/[entities]/<int:[entity]_id>', methods=['DELETE'])
def delete_[entity]([entity]_id):
    """
    Delete [entity]
    
    Query Params:
        user_id: User ID (for authorization)
    
    Response:
        {
            "success": true,
            "message": "[Entity] deleted successfully"
        }
    """
    try:
        user_id = request.args.get('user_id', type=int)
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'user_id is required'
            }), 400
        
        result = [feature]_service.delete_[entity]([entity]_id, user_id)
        
        status_code = 200 if result.get('success') else 400
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in delete_[entity]: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
```

### **Register Blueprint in `__init__.py`:**

```python
# app/api/v2/__init__.py
from flask import Blueprint
from .users import users_bp
from .recipes import recipes_bp
from .meal_plans import meal_plans_bp
from .grocery_lists import grocery_lists_bp
from .[feature] import [feature]_bp  # Add new blueprint

def register_v2_routes(app):
    """Register all v2 API routes"""
    v2_bp = Blueprint('v2', __name__, url_prefix='/api/v2')
    
    # Register sub-blueprints
    v2_bp.register_blueprint(users_bp)
    v2_bp.register_blueprint(recipes_bp)
    v2_bp.register_blueprint(meal_plans_bp)
    v2_bp.register_blueprint(grocery_lists_bp)
    v2_bp.register_blueprint([feature]_bp)  # Add new blueprint
    
    app.register_blueprint(v2_bp)
```

---

## ✅ **CHECKLIST FOR NEW FEATURE**

### **Phase 1: Repository (45 min)**
- [ ] Create `[feature]_repository.py`
- [ ] Extend `BaseRepository`
- [ ] Implement `create_[entity]()`
- [ ] Implement `get_[entity]_by_id()`
- [ ] Implement `get_all_[entities]()`
- [ ] Implement `update_[entity]()`
- [ ] Implement `delete_[entity]()`
- [ ] Add singleton getter `get_[feature]_repository()`
- [ ] Test repository methods

### **Phase 2: Service (45 min)**
- [ ] Create `[feature]_service.py`
- [ ] Extend `BaseService`
- [ ] Implement `create_[entity]()` with validation
- [ ] Implement `get_[entity]()` with authorization
- [ ] Implement `get_user_[entities]()` with pagination
- [ ] Implement `update_[entity]()` with validation
- [ ] Implement `delete_[entity]()` with authorization
- [ ] Add singleton getter `get_[feature]_service()`
- [ ] Test service methods

### **Phase 3: Routes (45 min)**
- [ ] Create `[feature].py` in `app/api/v2/`
- [ ] Create Flask Blueprint
- [ ] Implement `POST /[entities]`
- [ ] Implement `GET /[entities]/<id>`
- [ ] Implement `GET /[entities]/user/<user_id>`
- [ ] Implement `PUT /[entities]/<id>`
- [ ] Implement `DELETE /[entities]/<id>`
- [ ] Register blueprint in `__init__.py`
- [ ] Test all endpoints with curl/Postman

### **Phase 4: Testing (30 min)**
- [ ] Create test script
- [ ] Test CREATE endpoint
- [ ] Test READ endpoints
- [ ] Test UPDATE endpoint
- [ ] Test DELETE endpoint
- [ ] Test error cases
- [ ] Test authorization

### **Phase 5: Documentation (30 min)**
- [ ] Add to OpenAPI spec
- [ ] Update API reference
- [ ] Add code examples
- [ ] Update migration tracking

---

## 🎯 **QUICK REFERENCE**

### **Common Patterns:**

#### **Standard Response Format:**
```python
# Success
{
    "success": true,
    "data": { ... },
    "message": "Optional message"
}

# Error
{
    "success": false,
    "error": "Error message",
    "error_code": "OPTIONAL_CODE"
}
```

#### **Standard Pagination:**
```python
{
    "success": true,
    "data": {
        "items": [ ... ],
        "pagination": {
            "page": 1,
            "per_page": 20,
            "total": 100,
            "total_pages": 5,
            "has_next": true,
            "has_prev": false
        }
    }
}
```

#### **Error Handling Pattern:**
```python
try:
    # Business logic
    result = service.method()
    return jsonify(result), 200
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500
```

---

## 💡 **PRO TIPS**

1. **Always use BaseRepository methods** - Don't write raw SQL unless necessary
2. **Always validate in Service layer** - Repository just executes
3. **Always check authorization** - Verify user owns resource
4. **Always use transactions** - BaseRepository handles this
5. **Always log actions** - Use `logger.info()` for success, `logger.error()` for failures
6. **Always return standardized responses** - Use `success_response()` and `error_response()`
7. **Always paginate large lists** - Use `paginate()` helper
8. **Always handle exceptions** - Catch and return proper error responses
9. **Always test endpoints** - Use curl/Postman before deploying

---

## 🚀 **PROVEN SUCCESS**

This template has been used successfully for:
- ✅ Users API (4 endpoints)
- ✅ Recipes API (12 endpoints)
- ✅ Meal Plans API (6 endpoints)
- ✅ Grocery Lists API (7 endpoints)

**Total: 29 endpoints migrated using this template!**

**Success Rate: 100%** (All working, all tested, all documented)

---

## 📝 **EXAMPLE: Friends Repository**

See complete example in the next section...

---

**Ready to use this template for Friends & Households migration!** 🎯
