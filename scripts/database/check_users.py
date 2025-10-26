"""
Check for test users in database
"""
from app.database.repositories.user_repository import get_user_repository

repo = get_user_repository()
users = repo._execute_query('SELECT id, name, email FROM users LIMIT 5')

print('\nAvailable users in database:')
print('='*60)
for u in users:
    print(f'  ID: {u["id"]}, Name: {u["name"]}, Email: {u["email"]}')
print('='*60)
print(f'\nTotal: {len(users)} users found\n')
