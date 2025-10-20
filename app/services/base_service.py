"""
Base Service Pattern
Provides common functionality for all services
Services contain business logic and coordinate repositories
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseService:
    """
    Base class for all services
    Services coordinate repositories and contain business logic
    """
    
    def __init__(self):
        """Initialize service"""
        pass
    
    # Response helpers (standardized API responses)
    
    def success_response(self, data: Any = None, message: str = None) -> Dict[str, Any]:
        """
        Create successful response
        
        Args:
            data: Response data
            message: Success message
        
        Returns:
            Standardized success response
        """
        response = {
            'success': True
        }
        
        if data is not None:
            response['data'] = data
        
        if message:
            response['message'] = message
        
        return response
    
    def error_response(self, message: str, code: str = None, details: Any = None) -> Dict[str, Any]:
        """
        Create error response
        
        Args:
            message: Error message
            code: Error code (e.g., 'NOT_FOUND', 'UNAUTHORIZED')
            details: Additional error details
        
        Returns:
            Standardized error response
        """
        response = {
            'success': False,
            'error': message
        }
        
        if code:
            response['error_code'] = code
        
        if details:
            response['details'] = details
        
        return response
    
    # Validation helpers
    
    def validate_required_fields(self, data: Dict[str, Any], required_fields: list) -> Optional[str]:
        """
        Validate that required fields are present
        
        Args:
            data: Data dictionary to validate
            required_fields: List of required field names
        
        Returns:
            Error message if validation fails, None if valid
        """
        missing = [field for field in required_fields if field not in data or data[field] is None]
        
        if missing:
            return f"Missing required fields: {', '.join(missing)}"
        
        return None
    
    def validate_email(self, email: str) -> bool:
        """
        Validate email format
        
        Args:
            email: Email to validate
        
        Returns:
            True if valid, False otherwise
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    # Logging helpers
    
    def log_info(self, message: str, **kwargs):
        """Log info message"""
        logger.info(f"{self.__class__.__name__}: {message}", extra=kwargs)
    
    def log_warning(self, message: str, **kwargs):
        """Log warning message"""
        logger.warning(f"{self.__class__.__name__}: {message}", extra=kwargs)
    
    def log_error(self, message: str, exception: Exception = None, **kwargs):
        """Log error message"""
        if exception:
            logger.error(f"{self.__class__.__name__}: {message} - {str(exception)}", extra=kwargs)
        else:
            logger.error(f"{self.__class__.__name__}: {message}", extra=kwargs)
    
    # Pagination helpers
    
    def paginate(self, items: list, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        Paginate a list of items
        
        Args:
            items: List of items to paginate
            page: Page number (1-indexed)
            per_page: Items per page
        
        Returns:
            Dictionary with pagination info and items
        """
        total = len(items)
        total_pages = (total + per_page - 1) // per_page  # Ceiling division
        
        # Calculate slice indices
        start = (page - 1) * per_page
        end = start + per_page
        
        # Get items for this page
        page_items = items[start:end]
        
        return {
            'items': page_items,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        }


if __name__ == '__main__':
    # Test BaseService
    print("Testing BaseService...")
    
    service = BaseService()
    
    # Test success response
    response = service.success_response({'user_id': 123}, 'User found')
    print(f"\n✅ Success response: {response}")
    assert response['success'] == True
    assert response['data']['user_id'] == 123
    assert response['message'] == 'User found'
    
    # Test error response
    response = service.error_response('User not found', code='NOT_FOUND')
    print(f"✅ Error response: {response}")
    assert response['success'] == False
    assert response['error'] == 'User not found'
    assert response['error_code'] == 'NOT_FOUND'
    
    # Test validate_required_fields
    data = {'name': 'John', 'email': 'john@example.com'}
    error = service.validate_required_fields(data, ['name', 'email'])
    print(f"✅ Valid data: {error is None}")
    assert error is None
    
    error = service.validate_required_fields(data, ['name', 'email', 'password'])
    print(f"✅ Missing field detected: {error}")
    assert error is not None
    
    # Test email validation
    valid = service.validate_email('test@example.com')
    print(f"✅ Valid email: {valid}")
    assert valid == True
    
    invalid = service.validate_email('invalid-email')
    print(f"✅ Invalid email detected: {not invalid}")
    assert invalid == False
    
    # Test pagination
    items = list(range(1, 51))  # 50 items
    result = service.paginate(items, page=1, per_page=10)
    print(f"✅ Pagination: Page 1 has {len(result['items'])} items")
    assert len(result['items']) == 10
    assert result['items'][0] == 1
    assert result['pagination']['total'] == 50
    assert result['pagination']['total_pages'] == 5
    assert result['pagination']['has_next'] == True
    assert result['pagination']['has_prev'] == False
    
    result = service.paginate(items, page=3, per_page=10)
    print(f"✅ Pagination: Page 3 starts at {result['items'][0]}")
    assert result['items'][0] == 21
    assert result['pagination']['has_next'] == True
    assert result['pagination']['has_prev'] == True
    
    print("\n✅ All BaseService tests passed!")
