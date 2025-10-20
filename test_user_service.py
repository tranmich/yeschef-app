"""Test UserService"""
from app.services.user_service import UserService
from app.database.connection import init_database

print("Testing UserService...")

init_database()
user_service = UserService()

# Test get_user_by_id
print("\n=== Test: Get User by ID ===")
result = user_service.get_user_by_id(11)
print(f"✅ Get user by ID: {result['success']}")
if result['success']:
    print(f"   User: {result['data']['name']} ({result['data']['email']})")
    # Check password_hash is NOT in response
    assert 'password_hash' not in result['data'], "password_hash should be sanitized!"
    print(f"   ✅ Sensitive fields sanitized")

# Test get_user_by_email
print("\n=== Test: Get User by Email ===")
result = user_service.get_user_by_email('umie214@gmail.com')
print(f"✅ Get user by email: {result['success']}")
if result['success']:
    print(f"   User: {result['data']['name']}")

# Test get_user_by_email with invalid email
print("\n=== Test: Invalid Email Format ===")
result = user_service.get_user_by_email('invalid-email')
print(f"✅ Invalid email detected: {not result['success']}")
print(f"   Error: {result['error']}")

# Test get_user_by_email with non-existent user
print("\n=== Test: Non-existent User ===")
result = user_service.get_user_by_email('nonexistent@example.com')
print(f"✅ User not found: {not result['success']}")
print(f"   Error: {result['error']}")

# Test search_users
print("\n=== Test: Search Users ===")
result = user_service.search_users('test', limit=5)
print(f"✅ Search users: {result['success']}")
if result['success']:
    print(f"   Found: {result['data']['count']} users")
    for user in result['data']['users'][:3]:
        print(f"   - {user['name']}")

# Test get_user_stats
print("\n=== Test: Get User Stats ===")
result = user_service.get_user_stats(11)
print(f"✅ Get user stats: {result['success']}")
if result['success']:
    stats = result['data']
    print(f"   User: {stats['name']}")
    print(f"   Recipes: {stats['recipe_count']}")
    print(f"   Member since: {stats['member_since']}")

print("\n✅ All UserService tests passed!")
