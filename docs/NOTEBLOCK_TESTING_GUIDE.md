# 📝 NoteBlock Testing Guide

**How to Test the New NoteBlock Feature**

---

## 🚀 **Quick Start**

### **1. Start the Server**
```bash
cd "D:\Mik\Downloads\Me Hungie"
python hungie_server.py
```

### **2. Start the Frontend**
```bash
cd frontend
npm start
```

### **3. Navigate to Whiteboard**
1. Login to YesChef app
2. Go to **Whiteboard** page
3. Look for the toolbar at the top

---

## 🎯 **Testing Steps**

### **Step 1: Create a Note**
1. Click the **📝 Add Note** button in the toolbar
2. A yellow sticky note should appear on the canvas
3. You should see a success toast: "Note created! Start typing..."

### **Step 2: Edit the Note**
1. Click inside the note
2. Start typing - you should see:
   - Text appears in real-time
   - Character counter at bottom updates
   - Formatting toolbar at top

### **Step 3: Try Formatting**
1. **Bold**: Select text, click **B** button (or Ctrl+B)
2. **Italic**: Select text, click **I** button (or Ctrl+I)
3. **Heading**: Click **H** button
4. **Bullet List**: Click **•** button

### **Step 4: Change Color**
1. Click **🎨** button
2. Choose a preset color (yellow, blue, green, pink, purple, orange)
3. Or use the color picker for custom colors
4. Note should change color instantly

### **Step 5: Change Font Size**
1. Click **A** button
2. Select Small, Medium, Large, or X-Large
3. Text size should update

### **Step 6: Upload Image** 📸
1. Click **📷** button
2. Select an image from your computer
3. Wait for "Uploading..." indicator
4. Image should appear in the note

### **Step 7: Drag & Drop Image**
1. Find an image on your computer or web
2. Drag it into the note
3. Image should upload and appear

### **Step 8: Paste Image**
1. Copy an image (screenshot or from web)
2. Click inside note
3. Press Ctrl+V
4. Image should appear

### **Step 9: Add Link**
1. Select some text
2. Click **🔗** button
3. Enter URL (e.g., `https://www.google.com`)
4. Click "Set Link"
5. Text should become a clickable link

### **Step 10: Resize Note**
1. Click the note to select it
2. Drag the corner resize handles
3. Note should resize smoothly

### **Step 11: Move Note**
1. Click and drag the note
2. It should move around the canvas

### **Step 12: Auto-Save Test**
1. Type some text in note
2. Click outside the note (blur)
3. Check browser console - should see "✅ Note auto-saved"
4. Refresh the page
5. Note should load with your text intact

### **Step 13: Multiple Notes**
1. Click **📝 Add Note** button again
2. Second note should appear offset from first
3. Both notes should work independently

### **Step 14: Character Limit**
1. Type ~4500 characters (paste a long article)
2. Counter should show approaching limit (turns orange at 90%)
3. At 5000 chars, counter turns red and pulses
4. Cannot type more than 5000 characters

---

## ✅ **Expected Results**

### **Visual Checks:**
- ✅ Note has sticky note appearance (shadow, rounded corners)
- ✅ Toolbar shows all buttons (🎨 A B I • H 📷 🖼️ 🔗)
- ✅ Character counter visible at bottom
- ✅ Note is resizable and draggable
- ✅ Images display correctly
- ✅ Links are clickable (blue, underlined)

### **Functional Checks:**
- ✅ Auto-save works (check console logs)
- ✅ Notes persist after page refresh
- ✅ Images upload successfully
- ✅ Formatting applies correctly
- ✅ Color changes work
- ✅ Font size changes work
- ✅ Character limit enforced

### **Console Checks:**
Look for these log messages:
```
📝 Creating new note block...
✅ Note created in backend with ID: 123
✅ Note auto-saved
📸 Image uploaded: noteblock_789_abc123.webp
```

---

## 🐛 **Troubleshooting**

### **Issue: "Add Note" button not visible**
**Fix:** 
- Make sure you're on the Whiteboard page
- Check that `NoteBlock.js` was imported correctly
- Verify the toolbar is rendering

### **Issue: Note doesn't appear after clicking button**
**Check:**
1. Browser console for errors
2. Network tab - look for `/api/v2/whiteboard/{id}/objects` POST request
3. Make sure whiteboard ID is valid

### **Issue: Images won't upload**
**Check:**
1. File size < 5MB
2. File is an image type (png, jpg, jpeg, gif, webp)
3. Backend server is running
4. Check network tab for `/api/v2/whiteboards/images/upload` POST request

### **Issue: Auto-save not working**
**Check:**
1. Console logs - should see "✅ Note auto-saved"
2. Network tab - look for PATCH requests to `/api/v2/whiteboard/objects/{id}`
3. Make sure you clicked outside the note (blur event)

### **Issue: Note doesn't load after refresh**
**Check:**
1. Make sure note was saved (check console)
2. Whiteboard objects API returns note objects
3. `loadSavedObjects` function handles 'note' type

---

## 🎨 **Example Use Cases to Test**

### **1. Mexican Food Theme Board**
```
Create note with:
- Title: "🇲🇽 Abuela's Recipes"
- Upload photo of grandma
- Add recipe link
- Use orange color
- Large font
```

### **2. Cooking Journal Entry**
```
Create note with:
- Title: "Sunday Dinner - Nov 6, 2024"
- Upload photo of finished dish
- Write about the experience
- Add multiple photos (before/after)
- Use yellow color
```

### **3. Shopping Reminder**
```
Create note with:
- Title: "Don't Forget!"
- Bullet list of items
- Red/pink color for urgency
- Bold important items
```

---

## 📊 **Performance Checks**

### **Image Upload Performance:**
- Small images (<500KB): Should upload in < 2 seconds
- Medium images (500KB-2MB): Should upload in < 5 seconds
- Large images (2MB-5MB): Should upload in < 10 seconds
- All images auto-optimized to WebP format

### **Auto-Save Performance:**
- Should debounce (not save on every keystroke)
- Save triggered on blur event
- Save should complete in < 1 second

### **Canvas Performance:**
- 10+ notes should render smoothly
- Dragging should be fluid
- Resizing should be responsive

---

## 🧪 **Edge Cases to Test**

1. **Very long text**: Paste 10,000 characters - should stop at 5000
2. **Multiple images**: Add 5+ images to one note
3. **Special characters**: Use emojis, unicode, symbols
4. **Copy/paste**: Copy formatted text from Word/Google Docs
5. **Mobile**: Test on tablet/phone (responsive design)
6. **Slow network**: Throttle network, test image upload
7. **Delete note**: Delete a note, verify it's removed from backend
8. **Concurrent edits**: Open same whiteboard in 2 tabs (future: real-time sync)

---

## ✨ **Success Criteria**

✅ Can create notes quickly (< 2 seconds)  
✅ Can upload images successfully  
✅ Auto-save works reliably  
✅ Notes persist after refresh  
✅ UI is intuitive and responsive  
✅ No console errors  
✅ Images are optimized (WebP format)  
✅ Character limit prevents overflow  

---

**Happy Testing!** 🎉

If you find any bugs, check the browser console and network tab for error details.
