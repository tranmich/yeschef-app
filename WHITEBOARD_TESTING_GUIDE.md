# Whiteboard Testing Guide - November 26, 2025

## 🎯 **Purpose**
This guide provides a systematic approach to testing the refactored whiteboard after last night's major cleanup (961 lines removed, 3 new utilities created).

---

## ✅ **Pre-Testing Checklist**

Before you start testing:
- [ ] Read `WHITEBOARD_REFACTORING_COMPLETE.md` for context
- [ ] Ensure backend server is running
- [ ] Ensure frontend dev server is running
- [ ] Open browser console for error monitoring
- [ ] Have a test household and whiteboard ready

---

## 🧪 **Test Plan**

### **Priority 1: Critical Path (MUST WORK)** 🔴

#### **1. Whiteboard Loading & Display**
- [x ] **Load whiteboard** - Does the whiteboard load without errors?
- [x ] **View existing objects** - Do all saved items appear correctly?
- [x ] **Canvas controls** - Can you pan, zoom, and navigate?
- [x ] **Recipe cache** - Do recipes load and display properly?

**Expected Result:** Whiteboard loads with all saved objects visible  
**If Fails:** Check console for errors, verify API calls in Network tab

---

#### **2. Recipe Card Operations**
- [ ] **Add recipe to canvas** - Click "Add Recipe", select recipe, appears on canvas
- [ ] **Move recipe card** - Drag recipe cards around canvas
- [ ] **Change recipe color** - Click color picker, change color
- [ ] **Add/remove tags** - Add tags to recipe, remove tags
- [ ] **Delete recipe** - Remove recipe from canvas
- [ ] **Select multiple recipes** - Shift+click to select multiple

**Expected Result:** All recipe operations work smoothly  
**If Fails:** Check recipe node handlers, verify `useRecipeNodes` hook

---

#### **3. Grocery List Generation** 🛒
This is a newly refactored feature - test thoroughly!

- [ ] **Select recipes** - Select 2-3 recipe cards
- [ ] **Generate list** - Click "Generate Grocery List"
- [ ] **Verify ingredients** - Check ingredients are consolidated correctly
- [ ] **Check duplicates** - Same ingredients should be merged
- [ ] **Verify sources** - Each ingredient shows source recipe

**Expected Result:** Grocery list appears with merged ingredients  
**If Fails:** 
- Check `groceryListGenerator.js` utility
- Verify `generateGroceryListFromRecipes()` function
- Check console for ingredient parsing errors

---

#### **4. Grocery List Operations**
- [ ] **Rename list** - Change grocery list name
- [ ] **Change color** - Change background color
- [ ] **Check items** - Mark items as checked/unchecked
- [ ] **Add item** - Add new item to list
- [ ] **Remove item** - Delete item from list
- [ ] **Reorder items** - Drag items to reorder
- [ ] **Delete list** - Remove entire grocery list

**Expected Result:** All grocery list operations work and auto-save  
**If Fails:** Check grocery list handlers (lines 749-850 in WhiteboardApp.js)

---

#### **5. Save Operations** 💾
This was heavily refactored - critical to test!

- [ ] **Manual save** - Click Save button, verify success toast
- [ ] **Auto-save** - Make changes, wait 2-3 seconds, should auto-save
- [ ] **Recipe positions** - Move recipes, save, refresh - positions persist
- [ ] **Grocery lists** - Create list, save, refresh - list persists
- [ ] **Meal plans** - Create meal plan, save, refresh - persists
- [ ] **Notes** - Create note, save, refresh - note persists

**Expected Result:** All saves complete successfully, data persists after refresh  
**If Fails:**
- Check `whiteboardSave.js` utility
- Verify `saveAllWhiteboardNodes()` function
- Check Network tab for failed API calls
- Verify database IDs are being set correctly

---

### **Priority 2: Important Features (SHOULD WORK)** 🟡

#### **6. Meal Plan Creation & Management**
- [ ] **Create meal plan** - Click "Create Day Box"
- [ ] **Rename meal plan** - Change meal plan name
- [ ] **Add recipes to meal plan** - Drag recipes into meal plan container
- [ ] **Generate grocery from meal plan** - Click "Generate List" on meal plan
- [ ] **Verify meal plan list** - Ingredients from all recipes in meal plan
- [ ] **Delete meal plan** - Remove meal plan from canvas

**Expected Result:** Meal plans work with proper recipe association  
**If Fails:** Check meal plan handlers and `generateGroceryListFromMealPlanNode()`

---

#### **7. Note Creation & Editing**
- [ ] **Create note** - Click "Add Note"
- [ ] **Edit note content** - Type in note, formatting works
- [ ] **Change note color** - Pick different background color
- [ ] **Resize note** - Drag corners to resize
- [ ] **Move note** - Drag note around canvas
- [ ] **Delete note** - Remove note from canvas
- [ ] **Note auto-save** - Type in note, should auto-save after 2 seconds

**Expected Result:** Notes create, edit, and save properly  
**If Fails:** Check `handleCreateNote` and note component debounced save

---

#### **8. Activity Feed**
- [ ] **Add activity feed** - Create activity feed widget
- [ ] **View activities** - Recent household activities display
- [ ] **Move feed** - Drag activity feed around canvas
- [ ] **Delete feed** - Remove activity feed

**Expected Result:** Activity feed displays recent actions  
**If Fails:** Check `createActivityFeedNode` utility

---

### **Priority 3: Nice-to-Have Features (CAN WORK)** 🟢

#### **9. Tags & Filtering**
- [ ] **Add tags to recipes** - Tag recipes with categories
- [ ] **Filter by tag** - Click tag to filter visible recipes
- [ ] **Clear filters** - Remove tag filters
- [ ] **Toggle tag sidebar** - Show/hide tag panel

**Expected Result:** Tag filtering works smoothly  
**If Fails:** Check tag handlers (lines 1171-1188)

---

#### **10. Comments & Collaboration**
- [ ] **Open comments** - Click comment icon on object
- [ ] **Add comment** - Write and post comment
- [ ] **View comments** - See all comments on object
- [ ] **Comment counts** - Counts update correctly

**Expected Result:** Comments work for all object types  
**If Fails:** Check CommentsSidebar component

---

#### **11. Keyboard Shortcuts**
- [ ] **Ctrl+S** - Manual save
- [ ] **Ctrl+A** - Select all
- [ ] **Delete** - Delete selected items
- [ ] **Escape** - Clear selection
- [ ] **?** - Show shortcuts modal

**Expected Result:** All shortcuts work as expected  
**If Fails:** Check `handleKeyDown` function (line 299)

---

## 🐛 **Common Issues & Solutions**

### **Issue: Grocery List Not Generating**
**Symptoms:** Button clicks, nothing happens  
**Check:**
1. Open console - any errors?
2. Network tab - API calls failing?
3. Are recipes fully loaded? (Check recipe cache)
4. Do recipes have ingredients?

**Fix:**
- Check `groceryListGenerator.js` → `generateGroceryListFromRecipes()`
- Verify ingredient parsing in `parseIngredients()`
- Check API response format

---

### **Issue: Save Not Working**
**Symptoms:** Save button does nothing, or data doesn't persist  
**Check:**
1. Console errors during save?
2. Network tab - which API call failed?
3. Are database IDs being set? (`node.data.dbId`)
4. Check save response in Network tab

**Fix:**
- Check `whiteboardSave.js` → `saveAllWhiteboardNodes()`
- Verify individual save functions (recipes, grocery lists, meal plans, notes)
- Check backend API endpoints

---

### **Issue: Nodes Not Appearing**
**Symptoms:** Create action succeeds, but node doesn't appear  
**Check:**
1. Console logs - was node created?
2. React DevTools - is node in state?
3. Check node position - is it off-screen?
4. Check `nodeTypes` mapping (line 57)

**Fix:**
- Verify `setNodes()` is being called
- Check node creator utilities in `nodeCreators.js`
- Verify node type matches `nodeTypes` definition

---

### **Issue: Auto-Save Not Working**
**Symptoms:** Changes made, but don't persist  
**Check:**
1. Is manual save working?
2. Console logs - is `handleSave` being called?
3. Check `setTimeout` calls (should trigger after 500ms)

**Fix:**
- Verify `handleSave` is defined correctly
- Check that handlers call `setTimeout(() => handleSave(), 500)`

---

## 📝 **Testing Checklist Template**

Use this for each test session:

```markdown
## Test Session: [Date/Time]
**Tester:** [Your Name]
**Build:** main branch, commit [hash]

### Critical Path Results
- [ ] ✅ Whiteboard Loading: PASS/FAIL
- [ ] ✅ Recipe Operations: PASS/FAIL
- [ ] ✅ Grocery Generation: PASS/FAIL
- [ ] ✅ Grocery Operations: PASS/FAIL
- [ ] ✅ Save Operations: PASS/FAIL

### Important Features Results
- [ ] 🟡 Meal Plans: PASS/FAIL
- [ ] 🟡 Notes: PASS/FAIL
- [ ] 🟡 Activity Feed: PASS/FAIL

### Nice-to-Have Results
- [ ] 🟢 Tags: PASS/FAIL
- [ ] 🟢 Comments: PASS/FAIL
- [ ] 🟢 Shortcuts: PASS/FAIL

### Bugs Found
1. [Description] - Severity: HIGH/MEDIUM/LOW
2. [Description] - Severity: HIGH/MEDIUM/LOW

### Notes
[Any observations, performance issues, etc.]
```

---

## 🔍 **Debugging Tips**

### **Finding Issues Fast:**
1. **Always check console first** - Most errors will show here
2. **Use React DevTools** - Inspect component state
3. **Network tab** - Verify API calls succeed
4. **Git blame** - See what changed recently

### **Key Files to Check:**
- `frontend/src/pages/WhiteboardApp.js` (2,016 lines - main app logic)
- `frontend/src/utils/whiteboardSave.js` (save operations)
- `frontend/src/utils/groceryListGenerator.js` (grocery list logic)
- `frontend/src/utils/nodeCreators.js` (node factories)

### **Console Commands for Debugging:**
```javascript
// Check nodes state
window.reactFlow = useReactFlow();
console.log(window.reactFlow.getNodes());

// Check specific node
console.log(nodes.find(n => n.id === 'grocery-list-123'));

// Force save
handleSave();
```

---

## 🎓 **What Changed Last Night**

To understand potential issues, know what was refactored:

### **Major Changes:**
1. **Save logic** extracted to utility (was 200 lines, now 44)
2. **Grocery list generation** extracted to utility (was 150 lines, now 40)
3. **Meal plan grocery** functions simplified (was 180 lines, now 89)
4. **Node creators** standardized in utility

### **No Changes To:**
- Recipe card rendering
- React Flow setup
- State management approach
- Component hierarchy
- API endpoints

### **Risk Areas:**
- Save operations (heavily refactored)
- Grocery list generation (new utility)
- Node creation (standardized)

---

## ✅ **Success Criteria**

**All tests pass if:**
1. ✅ All Priority 1 (Critical Path) tests work perfectly
2. ✅ 80%+ of Priority 2 (Important) tests work
3. ✅ No data loss on save/refresh
4. ✅ No console errors during normal operations
5. ✅ Performance is acceptable (no lag)

**Ready to ship if:**
- All critical features work
- Known bugs are documented
- No data corruption
- User experience is smooth

---

## 📞 **Getting Help**

If you encounter issues:

1. **Document the bug** - What you did, what happened, what you expected
2. **Capture error messages** - Console logs, Network tab errors
3. **Note the context** - Which feature, what data, which node
4. **Try to reproduce** - Can you make it happen again?

**The code is well-organized now, so debugging will be easier!**

---

## 🚀 **After Testing**

Once testing is complete:

1. **Document all bugs** in GitHub issues
2. **Prioritize fixes** (critical → important → nice-to-have)
3. **Fix critical bugs** before shipping
4. **Update documentation** with any gotchas
5. **Ship it!** 🎉

---

**Good luck! The refactored code is solid - any bugs will be easy to fix.** 💪
