"""Test BaseService"""
from app.services.base_service import BaseService

print("Testing BaseService...")

service = BaseService()

# Test success response
response = service.success_response({'user_id': 123}, 'User found')
print(f"\n✅ Success response: {response}")

# Test error response
response = service.error_response('User not found', code='NOT_FOUND')
print(f"✅ Error response: {response}")

# Test validate_required_fields
data = {'name': 'John', 'email': 'john@example.com'}
error = service.validate_required_fields(data, ['name', 'email'])
print(f"✅ Valid data: {error is None}")

error = service.validate_required_fields(data, ['name', 'email', 'password'])
print(f"✅ Missing field detected: {error}")

# Test email validation
valid = service.validate_email('test@example.com')
print(f"✅ Valid email: {valid}")

invalid = service.validate_email('invalid-email')
print(f"✅ Invalid email detected: {not invalid}")

# Test pagination
items = list(range(1, 51))  # 50 items
result = service.paginate(items, page=1, per_page=10)
print(f"✅ Pagination: Page 1 has {len(result['items'])} items, total {result['pagination']['total']}")

result = service.paginate(items, page=3, per_page=10)
print(f"✅ Pagination: Page 3 starts at {result['items'][0]}")

print("\n✅ All BaseService tests passed!")
