# 🏷️ Tag System Testing Guide

**Date:** November 9, 2025  
**Feature:** Tag System for Whiteboard Recipe Organization  
**Tester:** QA Team / Developer

---

## 🎯 **PRE-TEST SETUP**

### **1. Start the Application**

```powershell
# Terminal 1: Start Backend (Python)
cd "D:\Mik\Downloads\Me Hungie"
& "D:/Mik/Downloads/Me Hungie/venv/Scripts/Activate.ps1"
python hungie_server.py

# Terminal 2: Start Frontend (Node)
cd "D:\Mik\Downloads\Me Hungie\frontend"
npm start
```

### **2. Navigate to Whiteboard**
1. Open browser: http://localhost:3000
2. Log in to your account
3. Navigate to Whiteboards section
4. Open any whiteboard with recipe cards

### **3. Verify Initial State**
- [ ] Whiteboard loads successfully
- [ ] At least 3-5 recipe cards visible on canvas
- [ ] Toolbar visible at top
- [ ] No errors in browser console (F12)

---

## 📋 **TEST SUITE**

---

## **TEST 1: Tag System Component Rendering**

### **Objective:** Verify TagSystem component renders correctly

**Steps:**
1. Click on any recipe card to select it
2. Look for "+ Add Tag" button at bottom of card
3. Click "+ Add Tag" button

**Expected Results:**
- [ ] Tag editor appears in card
- [ ] Input field is visible with placeholder "Add tags..."
- [ ] "Done" button is visible
- [ ] Input field is focused automatically
- [ ] No console errors

**Screenshot Location:** `tag_editor_open.png`

---

## **TEST 2: Predefined Tag Autocomplete**

### **Objective:** Verify autocomplete suggestions work

**Steps:**
1. With tag editor open, type "qui"
2. Observe dropdown suggestions
3. Type "veg"
4. Observe new suggestions

**Expected Results:**
- [ ] Typing "qui" shows: "quick"
- [ ] Dropdown appears below input
- [ ] Suggestions include "quick" tag
- [ ] Typing "veg" shows: "vegetarian", "vegan"
- [ ] Can navigate with arrow keys (↑↓)
- [ ] Selected suggestion is highlighted

**Screenshot Location:** `autocomplete_suggestions.png`

---

## **TEST 3: Adding Tags via Autocomplete**

### **Objective:** Add tags using autocomplete

**Steps:**
1. Type "week" in tag input
2. See "weeknight" suggestion
3. Press Enter (or click suggestion)
4. Tag input clears
5. Type "kid" 
6. Press Enter on "kid-friendly"

**Expected Results:**
- [ ] "weeknight" pill appears with orange gradient
- [ ] "kid-friendly" pill appears
- [ ] Both pills have "×" remove button
- [ ] Input clears after each addition
- [ ] Pills are visually distinct and readable
- [ ] No duplicate tags appear

**Screenshot Location:** `tags_added.png`

---

## **TEST 4: Custom Tag Creation**

### **Objective:** Create custom tags not in predefined list

**Steps:**
1. Type "family-favorite" (not predefined)
2. Observe autocomplete dropdown
3. Press Enter to create custom tag
4. Type "tuesday-special"
5. Press Enter

**Expected Results:**
- [ ] Autocomplete shows "➕ Create 'family-favorite'"
- [ ] Custom tag is created as pill
- [ ] Second custom tag also created
- [ ] Custom tags styled same as predefined
- [ ] Tags persist in editor

**Screenshot Location:** `custom_tags.png`

---

## **TEST 5: Removing Tags**

### **Objective:** Remove tags from recipe

**Steps:**
1. With tags visible, hover over "weeknight" tag
2. Click the "×" button
3. Remove "kid-friendly" tag
4. Leave "family-favorite" tag

**Expected Results:**
- [ ] "×" button is visible on hover
- [ ] Clicking "×" removes tag immediately
- [ ] Tag disappears with smooth animation
- [ ] Remaining tags stay in place
- [ ] No console errors

**Screenshot Location:** `tag_removed.png`

---

## **TEST 6: Keyboard Navigation**

### **Objective:** Test keyboard shortcuts in tag editor

**Steps:**
1. Open tag editor
2. Type "qui" to show suggestions
3. Press ↓ arrow key twice
4. Press ↑ arrow key once
5. Press Enter to select
6. Press Escape key

**Expected Results:**
- [ ] ↓ moves selection down in suggestions
- [ ] ↑ moves selection up
- [ ] Selected item is highlighted
- [ ] Enter adds the selected tag
- [ ] Escape closes tag editor (reverts to view mode)

---

## **TEST 7: Tag Persistence (Save/Load)**

### **Objective:** Verify tags save to database

**Steps:**
1. Add tags: "weeknight", "quick", "vegetarian"
2. Click "Done" button in tag editor
3. Click "✓ Save" button in toolbar
4. Wait for success toast
5. Refresh browser page (F5)
6. Wait for whiteboard to reload
7. Click same recipe card

**Expected Results:**
- [ ] Toast shows "✅ Saved!" message
- [ ] After refresh, whiteboard reloads
- [ ] Recipe card still shows all 3 tags
- [ ] Tags display as pills (not in editor mode)
- [ ] Database stored tags correctly

**Screenshot Location:** `tags_persisted.png`

---

## **TEST 8: Tag Filter Sidebar - Opening**

### **Objective:** Open and close tag filter sidebar

**Steps:**
1. Click "🏷️ Tags" button in toolbar
2. Observe sidebar sliding in from right
3. Click "×" close button in sidebar
4. Click collapsed "🏷️" button on right edge
5. Click "🏷️ Tags" in toolbar again

**Expected Results:**
- [ ] Sidebar slides in smoothly from right
- [ ] Sidebar shows "Filter by Tag" header
- [ ] Close "×" button visible
- [ ] Sidebar slides out when closed
- [ ] Collapsed button appears on right edge
- [ ] Can reopen from both buttons

**Screenshot Location:** `sidebar_open.png`

---

## **TEST 9: Tag Filter Sidebar - Content**

### **Objective:** Verify sidebar displays all tags correctly

**Steps:**
1. Ensure sidebar is open
2. Look for categorized sections
3. Count tags in each category
4. Check tag counts (numbers in badges)

**Expected Results:**
- [ ] Tags grouped by category (Meal Type, Speed, etc.)
- [ ] Each tag shows count: e.g., "weeknight (2)"
- [ ] Tags sorted by usage (most used first)
- [ ] Custom tags in "Custom" category
- [ ] All categories visible
- [ ] Scrollbar appears if many tags

**Screenshot Location:** `sidebar_categories.png`

---

## **TEST 10: Single Tag Filtering**

### **Objective:** Filter whiteboard by single tag

**Steps:**
1. Note total recipe count on canvas
2. Click "weeknight" tag in sidebar
3. Observe canvas changes
4. Note filtered count shown in sidebar

**Expected Results:**
- [ ] "weeknight" tag becomes highlighted/selected
- [ ] Canvas filters to show ONLY recipes with "weeknight" tag
- [ ] Other recipes disappear (not deleted, just hidden)
- [ ] Sidebar shows "X recipes match" (correct count)
- [ ] Yellow filter summary bar appears
- [ ] No console errors

**Screenshot Location:** `single_tag_filter.png`

---

## **TEST 11: Multi-Tag Filtering (AND Logic)**

### **Objective:** Filter by multiple tags simultaneously

**Steps:**
1. With "weeknight" selected, click "vegetarian"
2. Observe canvas
3. Note count in sidebar
4. Add "quick" tag to filter
5. Observe further filtering

**Expected Results:**
- [ ] Both tags highlighted in sidebar
- [ ] Canvas shows ONLY recipes with BOTH tags (AND logic)
- [ ] Count decreases (fewer matches)
- [ ] Sidebar shows "X recipes match all filters"
- [ ] "Clear All" button visible
- [ ] Correct recipes displayed

**Screenshot Location:** `multi_tag_filter.png`

---

## **TEST 12: Clear All Filters**

### **Objective:** Remove all filters at once

**Steps:**
1. With multiple tags selected
2. Click "Clear All" button in filter summary
3. Observe canvas and sidebar

**Expected Results:**
- [ ] All tags become deselected
- [ ] All recipes reappear on canvas
- [ ] Filter summary bar disappears
- [ ] Tag counts remain correct
- [ ] Smooth transition animation

**Screenshot Location:** `filters_cleared.png`

---

## **TEST 13: Click Tag on Recipe Card to Filter**

### **Objective:** Quick filter by clicking tag pill on card

**Steps:**
1. Clear all filters
2. Find recipe with "quick" tag
3. Click the "quick" pill on the recipe card (not in editor mode)
4. Observe sidebar and canvas

**Expected Results:**
- [ ] Sidebar opens automatically (if closed)
- [ ] "quick" tag becomes selected in sidebar
- [ ] Canvas filters to show matching recipes
- [ ] Clicked recipe remains visible (has the tag)
- [ ] Tag badge in toolbar shows "1"

**Screenshot Location:** `click_tag_to_filter.png`

---

## **TEST 14: Tag Toolbar Badge**

### **Objective:** Verify toolbar badge shows filter count

**Steps:**
1. Clear all filters
2. Verify badge shows nothing
3. Select "weeknight" tag
4. Check badge
5. Add "quick" tag
6. Check badge again

**Expected Results:**
- [ ] No filters: No badge visible
- [ ] 1 filter: Badge shows "1"
- [ ] 2 filters: Badge shows "2"
- [ ] Badge styled in orange
- [ ] Badge positioned on toolbar button

**Screenshot Location:** `toolbar_badge.png`

---

## **TEST 15: Multiple Recipe Cards with Different Tags**

### **Objective:** Test tag variety across recipes

**Steps:**
1. Select Recipe 1, add: "weeknight", "quick"
2. Select Recipe 2, add: "party", "dessert"
3. Select Recipe 3, add: "weeknight", "vegetarian"
4. Save whiteboard
5. Filter by "weeknight"
6. Observe results

**Expected Results:**
- [ ] Recipe 1 has 2 tags
- [ ] Recipe 2 has 2 different tags
- [ ] Recipe 3 has 2 tags (1 shared with Recipe 1)
- [ ] Filter shows Recipe 1 and Recipe 3 only
- [ ] Recipe 2 is hidden (no "weeknight" tag)

---

## **TEST 16: Tag Editor - Character Limit**

### **Objective:** Ensure tags handle edge cases

**Steps:**
1. Try to add a very long tag (50+ characters)
2. Try to add empty tag (just spaces)
3. Try to add duplicate tag already on recipe

**Expected Results:**
- [ ] Long tags are accepted (or truncated gracefully)
- [ ] Empty/whitespace tags are rejected
- [ ] Duplicate tags don't appear twice
- [ ] No crashes or errors
- [ ] Graceful UX feedback

---

## **TEST 17: Tag Colors and Styling**

### **Objective:** Verify visual polish

**Steps:**
1. Add multiple tags to a recipe
2. Hover over tag pills
3. Hover over "×" remove button
4. Check tag pills in sidebar
5. Check selected vs unselected state

**Expected Results:**
- [ ] Tag pills have orange gradient background
- [ ] White text on tags is readable
- [ ] Hover effect on pills (subtle lift/shadow)
- [ ] "×" button shows on hover with background
- [ ] Sidebar tags have border, not gradient
- [ ] Selected tags in sidebar have gradient
- [ ] Animations are smooth (no flickering)

**Screenshot Location:** `tag_styling.png`

---

## **TEST 18: Performance with Many Tags**

### **Objective:** Test performance at scale

**Steps:**
1. Create 10 different tags across 5 recipes
2. Each recipe gets 3-5 tags
3. Open tag sidebar
4. Rapidly click different tags to filter
5. Switch between multiple filters

**Expected Results:**
- [ ] Sidebar loads instantly
- [ ] Filtering happens in <100ms
- [ ] No lag when selecting/deselecting tags
- [ ] Smooth animations maintained
- [ ] No memory leaks (check DevTools)
- [ ] Tag counts update correctly

---

## **TEST 19: Cross-Session Persistence**

### **Objective:** Verify tags persist across sessions

**Steps:**
1. Add tags to 3 recipes
2. Save whiteboard
3. Close browser completely
4. Reopen browser
5. Log in again
6. Navigate to same whiteboard

**Expected Results:**
- [ ] All tags still present on recipes
- [ ] Tag sidebar shows correct counts
- [ ] Filtering still works
- [ ] No data loss
- [ ] Database correctly persisted tags

---

## **TEST 20: Mobile Responsiveness (Bonus)**

### **Objective:** Check mobile behavior

**Steps:**
1. Resize browser to mobile width (< 768px)
2. Or use DevTools device emulation
3. Try to access tag sidebar
4. Observe tag pills on recipe cards

**Expected Results:**
- [ ] Tag sidebar collapses or adapts to mobile
- [ ] Tag pills on cards are still visible
- [ ] Touch targets are adequate (44px minimum)
- [ ] No horizontal scrolling
- [ ] Buttons remain accessible

---

## 🐛 **BUG REPORTING TEMPLATE**

If you find a bug, report it with:

```markdown
**Bug Title:** [Brief description]

**Steps to Reproduce:**
1. 
2. 
3. 

**Expected Behavior:**


**Actual Behavior:**


**Screenshots:**


**Console Errors:** (F12 → Console tab)


**Browser:** Chrome/Firefox/Safari [Version]

**Priority:** High/Medium/Low
```

---

## ✅ **ACCEPTANCE CRITERIA**

**Tag system is ready for production when:**

- [ ] All 20 tests pass without errors
- [ ] No console errors during any test
- [ ] Tags save and load correctly
- [ ] Filtering works with AND logic
- [ ] Performance is smooth (no lag)
- [ ] UI is visually polished
- [ ] Keyboard shortcuts work
- [ ] Mobile responsive (basic)
- [ ] No data loss on refresh
- [ ] All animations smooth

---

## 📊 **TEST RESULTS SUMMARY**

**Test Date:** _______________  
**Tester:** _______________

| Test # | Test Name | Status | Notes |
|--------|-----------|--------|-------|
| 1 | Component Rendering | ⬜ Pass ⬜ Fail | |
| 2 | Autocomplete | ⬜ Pass ⬜ Fail | |
| 3 | Adding Tags | ⬜ Pass ⬜ Fail | |
| 4 | Custom Tags | ⬜ Pass ⬜ Fail | |
| 5 | Removing Tags | ⬜ Pass ⬜ Fail | |
| 6 | Keyboard Nav | ⬜ Pass ⬜ Fail | |
| 7 | Persistence | ⬜ Pass ⬜ Fail | |
| 8 | Sidebar Open | ⬜ Pass ⬜ Fail | |
| 9 | Sidebar Content | ⬜ Pass ⬜ Fail | |
| 10 | Single Filter | ⬜ Pass ⬜ Fail | |
| 11 | Multi Filter | ⬜ Pass ⬜ Fail | |
| 12 | Clear Filters | ⬜ Pass ⬜ Fail | |
| 13 | Click to Filter | ⬜ Pass ⬜ Fail | |
| 14 | Toolbar Badge | ⬜ Pass ⬜ Fail | |
| 15 | Multiple Recipes | ⬜ Pass ⬜ Fail | |
| 16 | Edge Cases | ⬜ Pass ⬜ Fail | |
| 17 | Styling | ⬜ Pass ⬜ Fail | |
| 18 | Performance | ⬜ Pass ⬜ Fail | |
| 19 | Cross-Session | ⬜ Pass ⬜ Fail | |
| 20 | Mobile | ⬜ Pass ⬜ Fail | |

**Overall Status:** ⬜ PASS ⬜ FAIL  
**Critical Bugs Found:** _______________  
**Recommendations:** _______________

---

## 🚀 **QUICK START TESTING (5 Minutes)**

**Fast verification for developers:**

1. ✅ Add tag to recipe → Save → Refresh → Tag still there
2. ✅ Click "🏷️ Tags" → Sidebar opens
3. ✅ Click tag in sidebar → Canvas filters
4. ✅ Click 2 tags → Only recipes with BOTH tags show
5. ✅ Click "Clear All" → All recipes return

**If all 5 pass → Tag system is working! 🎉**

---

**Good luck testing! 🏷️✨**
