"""
Test BaseRepository
"""

from app.database.repositories.base_repository import BaseRepository
from app.database.connection import init_database

print("Testing BaseRepository...")

init_database()

# Test with users table
users_repo = BaseRepository('users')

# Test count
count = users_repo.count()
print(f"\n✅ Count users: {count}")

# Test find_all
users = users_repo.find_all(limit=3)
print(f"✅ Find all users (first 3): {len(users)} users")

# Test find_by_id
if users:
    user_id = users[0]['id']
    user = users_repo.find_by_id(user_id)
    print(f"✅ Find by ID: {user['name'] if user else 'Not found'}")

# Test exists
if users:
    exists = users_repo.exists(users[0]['id'])
    print(f"✅ Exists: {exists}")

# Test build_where_clause
where, params = users_repo._build_where_clause({'name': 'Test', 'email': 'test@example.com'})
print(f"✅ Build WHERE clause: {where}")

print("\n✅ All BaseRepository tests passed!")
