import sys
sys.path.append('.')
from app import app

# Test the search endpoint
app.testing = True
client = app.test_client()

# Search for one of our imported recipes
response = client.get('/api/search?query=overnight+oats')
print('Search response status:', response.status_code)

if response.status_code == 200:
    data = response.get_json()
    print(f'Found {len(data)} recipes matching "overnight oats"')
    for recipe in data[:3]:  # Show first 3 results
        print(f'  - {recipe.get("title", "No title")} (ID: {recipe.get("id", "No ID")})')
else:
    print('Error response:', response.get_data())

# Test categories endpoint
response = client.get('/api/categories')
print('\nCategories response status:', response.status_code)
if response.status_code == 200:
    categories = response.get_json()
    print(f'Total categories: {len(categories)}')
    for cat in categories[:5]:
        print(f'  - {cat.get("name", "No name")} ({cat.get("recipe_count", 0)} recipes)')
