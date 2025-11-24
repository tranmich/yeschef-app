#!/usr/bin/env python3
"""Fix bulk import modal to be fullscreen with buttons at bottom"""

import re

file_path = r'YesChefMobile\src\screens\GroceryListScreen.js'

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the bulk import modal opening
old_modal_start = r'''      {/\* 📋 Bulk Import Modal \*/}
      <Modal
        visible={showBulkImportModal}
        transparent={true}
        animationType="slide"'''

new_modal_start = '''      {/* 📋 Bulk Import Modal */}
      <Modal
        visible={showBulkImportModal}
        transparent={false}
        animationType="slide"'''

content = content.replace(old_modal_start, new_modal_start)

# Replace the modal container wrapper
old_wrapper = '<View style={styles.modalOverlay}>\n          <View style={styles.bulkImportModalContainer}>'
new_wrapper = '<SafeAreaView style={{flex: 1, backgroundColor: \'white\'}}>\n          <View style={styles.bulkImportModalContainer}>'

content = content.replace(old_wrapper, new_wrapper)

# Add spacer before buttons and fix closing tags
old_buttons_section = r'''            {/\* Action Buttons \*/}
            <View style={styles.bulkImportButtons}>'''

new_buttons_section = '''            {/* Spacer to push buttons to bottom */}
            <View style={{flex: 1}} />
            
            {/* Action Buttons - Fixed at bottom */}
            <View style={styles.bulkImportButtons}>'''

content = content.replace(old_buttons_section, new_buttons_section)

# Fix closing tags
old_closing = '''            </View>
          </View>
        </View>
      </Modal>

    </SafeAreaView>'''

new_closing = '''            </View>
          </View>
        </SafeAreaView>
      </Modal>

    </SafeAreaView>'''

content = content.replace(old_closing, new_closing)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed bulk import modal:")
print("  - Changed to fullscreen (transparent=false)")
print("  - Wrapped in SafeAreaView")
print("  - Added spacer to push buttons to bottom")
print("  - Fixed closing tags")
