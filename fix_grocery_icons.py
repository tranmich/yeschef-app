#!/usr/bin/env python3
"""Fix emoji encoding issues in GroceryListScreen.js"""

import re

file_path = r'YesChefMobile\src\screens\GroceryListScreen.js'

# Read the file with UTF-8 encoding
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the emoji text elements with Icon components
# Pattern 1: Line 882 - Options menu invite
pattern1 = r'<Text style=\{\{ fontSize: 22, color: "#7C3AED", marginRight: 16 \}\}>.*?</Text>\s*<Text style=\{styles\.modalMenuText\}>Invite Friends</Text>'
replacement1 = '<Icon name="person-add" size={22} color="#7C3AED" style={{marginRight: 16}} />\n                <Text style={styles.modalMenuText}>Invite Friends</Text>'

# Pattern 2: Line 1157 - Invite modal
pattern2 = r'<Text style=\{\{ fontSize: 22, color: "#7C3AED", marginRight: 12 \}\}>.*?</Text>\s*<Text style=\{styles\.inviteModalSubtitle\}>Invite</Text>'
replacement2 = '<Icon name="person-add" size={22} color="#7C3AED" style={{marginRight: 12}} />\n                      <Text style={styles.inviteModalSubtitle}>Invite</Text>'

# Apply replacements
content = re.sub(pattern1, replacement1, content, flags=re.DOTALL)
content = re.sub(pattern2, replacement2, content, flags=re.DOTALL)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed emoji icons in GroceryListScreen.js")
print("  - Replaced line 882 (Options menu invite)")
print("  - Replaced line 1157 (Invite modal)")
