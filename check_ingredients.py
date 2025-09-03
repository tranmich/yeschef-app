import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'), sslmode='require')
cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

cursor.execute('SELECT id, title, ingredients FROM recipes WHERE id IN (1926, 2273, 2547)')
recipes = cursor.fetchall()

for recipe in recipes:
    print(f'Recipe {recipe["id"]} - {recipe["title"]}')
    print(f'Ingredients type: {type(recipe["ingredients"])}')
    if recipe["ingredients"]:
        ingredients_str = str(recipe["ingredients"])[:200]
        print(f'Ingredients first 200 chars: {repr(ingredients_str)}')
    else:
        print('Ingredients: None')
    print('---')
