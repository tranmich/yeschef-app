#!/usr/bin/env python3
"""Fix preview bullet to use checkbox icon"""

file_path = r'YesChefMobile\src\screens\GroceryListScreen.js'

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the bullet text with icon
old_bullet = '<Text style={styles.previewBullet}>'
new_bullet = '<Icon name="square-outline" size={20} color="#10b981" style={styles.previewBullet} />'

# Find and replace the preview bullet line
import re
pattern = r'<Text style=\{styles\.previewBullet\}>.*?</Text>'
replacement = '<Icon name="square-outline" size={20} color="#10b981" style={styles.previewBullet} />'

content = re.sub(pattern, replacement, content)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed preview bullet to use checkbox icon")
