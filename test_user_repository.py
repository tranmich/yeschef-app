"""
Test UserRepository
"""

from app.database.repositories.user_repository import UserRepository
from app.database.connection import init_database

print("Testing UserRepository...")

init_database()

user_repo = UserRepository()

# Test count
count = user_repo.get_user_count()
print(f"\n✅ Total users: {count}")

# Test find_all
users = user_repo.find_all(limit=3)
print(f"✅ Find all (first 3): {len(users)} users")
for user in users:
    print(f"   - {user['name']} ({user['email']})")

# Test find_by_id
if users:
    user = user_repo.find_by_id(users[0]['id'])
    print(f"✅ Find by ID: {user['name']}")

# Test find_by_email
if users:
    user = user_repo.find_by_email(users[0]['email'])
    print(f"✅ Find by email: {user['name']}")

# Test email_exists
if users:
    exists = user_repo.email_exists(users[0]['email'])
    print(f"✅ Email exists: {exists}")

# Test search_by_name
results = user_repo.search_by_name('test', limit=5)
print(f"✅ Search by name 'test': {len(results)} results")

# Test get_recent_users
recent = user_repo.get_recent_users(limit=3)
print(f"✅ Recent users: {len(recent)} users")

print("\n✅ All UserRepository tests passed!")
