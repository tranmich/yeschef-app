import sqlite3

conn = sqlite3.connect('hungie.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM recipes')
total = cursor.fetchone()[0]
print(f'Total recipes: {total}')

cursor.execute("SELECT COUNT(*) FROM recipes WHERE url LIKE '%bonappetit.com%'")
bonappetit = cursor.fetchone()[0]
print(f'Bon Appetit recipes: {bonappetit}')

cursor.execute('SELECT title FROM recipes WHERE url LIKE "%bonappetit.com%" LIMIT 3')
samples = cursor.fetchall()
print('Sample recipes:')
for row in samples:
    print(f'  - {row[0]}')

conn.close()
