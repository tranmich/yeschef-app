import React, { useState, useEffect } from 'react';
import { DndContext, closestCenter, useDraggable, useDroppable } from '@dnd-kit/core';
import { arrayMove, SortableContext, verticalListSortingStrategy, horizontalListSortingStrategy } from '@dnd-kit/sortable';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import './GroceryManagerWorkspace.css';
import { getApiUrl } from '../utils/api';
import { useAuth } from '../contexts/AuthContext';
import LoadGroceryListPanel from './LoadGroceryListPanel';
import ShareResourceModal from './ShareResourceModal';

const GroceryManagerWorkspace = ({ mealPlanRecipes = [] }) => {
    // Authentication hook
    const { token, user } = useAuth();
    
    // Main state
    const [savedLists, setSavedLists] = useState([]);
    const [selectedListId, setSelectedListId] = useState(null);
    const [currentList, setCurrentList] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Pantry integration state
    const [pantryItems, setPantryItems] = useState([]);
    const [hiddenItems, setHiddenItems] = useState(new Set());
    const [showHidden, setShowHidden] = useState(false);

    // Smart combination state
    const [lastCombination, setLastCombination] = useState(null);
    const [draggedItem, setDraggedItem] = useState(null);
    const [combinationPreview, setCombinationPreview] = useState(null);
    const [isProcessingCombination, setIsProcessingCombination] = useState(false);
    const [recentCombinations, setRecentCombinations] = useState(new Set());

    // Workspace state with reorderable sections
    const [sectionOrder, setSectionOrder] = useState(['produce', 'meat_seafood', 'pantry', 'other']);
    const [sections, setSections] = useState({
        produce: { name: 'Produce', items: [] },
        meat_seafood: { name: 'Meat & Seafood', items: [] },
        pantry: { name: 'Pantry', items: [] },
        other: { name: 'Other', items: [] }
    });

    // UI state
    const [selectedFolder, setSelectedFolder] = useState(null);
    const [folders, setFolders] = useState([
        { id: 'recent', name: 'Recent Lists', lists: [] },
        { id: 'favorites', name: 'Favorites', lists: [] }
    ]);
    const [isCreatingList, setIsCreatingList] = useState(false);
    const [newListName, setNewListName] = useState('');
    const [showLoadPanel, setShowLoadPanel] = useState(false);

    // Notion-style inline adding
    const [showInlineAdd, setShowInlineAdd] = useState(false);
    const [inlineItemName, setInlineItemName] = useState('');
    const [isAddingInline, setIsAddingInline] = useState(false);

    // Track unsaved changes
    const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

    // Share modal state
    const [showShareModal, setShowShareModal] = useState(false);

    // Load saved lists and pantry on component mount
    useEffect(() => {
        loadSavedLists();
        // Auto-load from meal planner if available
        if (mealPlanRecipes.length > 0) {
            generateListFromMealPlan();
        }
    }, [mealPlanRecipes]);

    // Load pantry and reload lists when token becomes available
    useEffect(() => {
        if (token) {
            console.log('🔑 Token available, loading pantry items and grocery lists...');
            loadPantryItems();
            loadSavedLists(); // Reload lists with authentication
        }
    }, [token]);

    // Reload grocery lists when window regains focus (to catch updates from whiteboard)
    useEffect(() => {
        const handleFocus = () => {
            console.log('🔄 Window focused - reloading grocery lists to catch any updates');
            if (token) {
                loadSavedLists();
            }
        };

        window.addEventListener('focus', handleFocus);
        return () => window.removeEventListener('focus', handleFocus);
    }, [token]);

    // Load from localStorage on mount
    useEffect(() => {
        const savedData = localStorage.getItem('groceryList_current');
        if (savedData) {
            try {
                const parsed = JSON.parse(savedData);
                if (parsed.currentList) setCurrentList(parsed.currentList);
                if (parsed.sections) setSections(parsed.sections);
                console.log('📦 Loaded grocery list from localStorage');
            } catch (err) {
                console.error('Failed to load from localStorage:', err);
            }
        } else {
            // Initialize with default empty list
            setCurrentList({ name: 'My Grocery List', isFromMealPlan: false });
        }
    }, []);

    // Auto-save to localStorage whenever currentList or sections change
    useEffect(() => {
        if (currentList || Object.keys(sections).some(key => sections[key].items.length > 0)) {
            const dataToSave = {
                currentList,
                sections,
                lastModified: new Date().toISOString()
            };
            localStorage.setItem('groceryList_current', JSON.stringify(dataToSave));
            setHasUnsavedChanges(true);
            console.log('💾 Auto-saved to localStorage');
        }
    }, [currentList, sections]);

    const loadPantryItems = async () => {
        try {
            if (!token) {
                console.warn('🔑 No authentication token available for pantry access');
                return;
            }

            console.log('🔑 Token available, making pantry API call...');
            const response = await fetch(`${getApiUrl()}/api/pantry`, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });
            
            console.log('📡 Pantry API response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('📦 Pantry API response data:', data);

            if (data.success) {
                const pantryItems = data.items || data.pantry_items || []; // Handle both possible response formats
                setPantryItems(pantryItems);
                console.log(`🥫 Loaded ${pantryItems.length} pantry items:`, pantryItems);
            } else {
                console.warn('❌ Pantry API returned error:', data.error);
            }
        } catch (err) {
            console.error('💥 Network error loading pantry:', err);
        }
    };

    const loadSavedLists = async () => {
        setLoading(true);
        try {
            const headers = {
                'Content-Type': 'application/json'
            };
            
            // Add auth token if available
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
            
            // Get user ID from auth context
            const userId = user?.id;
            
            if (!userId) {
                console.warn('⚠️ No user ID available, skipping grocery list load');
                setLoading(false);
                return;
            }
            
            // Use V2 API endpoint
            const response = await fetch(`${getApiUrl()}/api/v2/grocery-lists/user/${userId}`, {
                headers
            });
            const data = await response.json();

            if (data.success) {
                // V2 API returns: {success: true, data: {grocery_lists: [...], pagination: {...}}}
                const allLists = data.data?.grocery_lists || data.grocery_lists || [];
                console.log(`📋 Loaded ${allLists.length} grocery lists:`, allLists);
                setSavedLists(allLists);
                
                // Organize into folders
                // Recent: All lists sorted by date (most recent first)
                const recentLists = [...allLists]
                    .sort((a, b) => new Date(b.created_date || b.created_at || 0) - new Date(a.created_date || a.created_at || 0))
                    .slice(0, 10); // Show last 10 lists
                
                // Favorites: Lists marked as favorites (if we have that field)
                // For now, showing all lists in favorites too until we add favorite feature
                const favoriteLists = [...allLists]
                    .sort((a, b) => {
                        const nameA = a.name || a.list_name || '';
                        const nameB = b.name || b.list_name || '';
                        return nameA.localeCompare(nameB);
                    }); // Alphabetically
                
                setFolders([
                    { id: 'recent', name: 'Recent Lists', lists: recentLists },
                    { id: 'favorites', name: 'All Lists', lists: favoriteLists }
                ]);
                
                console.log(`📁 Recent lists: ${recentLists.length}, All lists: ${favoriteLists.length}`);
            } else {
                setError(data.error || 'Failed to load grocery lists');
            }
        } catch (err) {
            console.error('❌ Error loading grocery lists:', err);
            setError('Network error: ' + err.message);
        } finally {
            setLoading(false);
        }
    };

    const generateListFromMealPlan = async () => {
        if (mealPlanRecipes.length === 0) return;

        try {
            const response = await fetch(`${getApiUrl()}/api/v2/grocery-lists`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ recipe_ids: mealPlanRecipes })
            });

            const data = await response.json();
            if (data.success && data.grocery_list) {
                // Convert to our section format
                const newSections = { ...sections };
                Object.entries(data.grocery_list.by_section || {}).forEach(([sectionKey, items]) => {
                    if (newSections[sectionKey]) {
                        const processedItems = items.map(item => ({
                            id: `recipe-${item.name}`,
                            name: item.display_text || item.name,
                            recipes: item.recipes || [],
                            isCustom: false
                        }));
                        
                        console.log(`🛒 Generated ${processedItems.length} items for section ${sectionKey}:`, processedItems.map(i => i.name));
                        newSections[sectionKey].items = processedItems;
                    }
                });
                setSections(newSections);
                console.log('🛒 Final grocery sections:', newSections);
                setCurrentList({
                    id: 'current',
                    name: 'Current Meal Plan List',
                    isFromMealPlan: true
                });
            }
        } catch (err) {
            console.error('Failed to generate grocery list:', err);
        }
    };

    const createNewList = () => {
        setIsCreatingList(true);
        setNewListName('');
    };

    const saveNewList = async () => {
        if (!newListName.trim()) return;

        const listData = {
            sections,
            created_from_meal_plan: mealPlanRecipes.length > 0,
            recipe_ids: mealPlanRecipes
        };

        try {
            const response = await fetch(`${getApiUrl()}/api/v2/grocery-lists`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    list_name: newListName.trim(),
                    list_data: listData,
                    recipe_ids: mealPlanRecipes
                })
            });

            const data = await response.json();
            if (data.success) {
                setCurrentList({
                    id: data.list_id,
                    name: newListName.trim(),
                    isFromMealPlan: false
                });
                setIsCreatingList(false);
                setNewListName('');
                loadSavedLists(); // Refresh the saved lists
            }
        } catch (err) {
            console.error('Failed to save list:', err);
        }
    };

    const loadList = async (listId) => {
        try {
            console.log(`📂 Loading grocery list: ${listId}`);
            const response = await fetch(`${getApiUrl()}/api/v2/grocery-lists/${listId}`);
            const data = await response.json();
            
            console.log(`📂 Load response:`, data);

            if (data.success && data.grocery_list) {
                const listData = data.grocery_list.list_data;
                console.log(`📂 List data:`, listData);
                
                // The list_data contains sections plus ingredient_count
                if (listData && typeof listData === 'object') {
                    // Extract sections (exclude ingredient_count)
                    const { ingredient_count, ...sectionsData } = listData;
                    
                    // Validate that we have valid sections
                    const expectedSections = ['produce', 'meat_seafood', 'pantry', 'other'];
                    const hasValidSections = expectedSections.some(sectionKey => sectionsData[sectionKey]);
                    
                    if (hasValidSections) {
                        setSections(sectionsData);
                        setCurrentList({
                            id: listId,
                            name: data.grocery_list.list_name,
                            isFromMealPlan: false
                        });
                        setSelectedListId(listId);
                        console.log(`✅ Successfully loaded list: "${data.grocery_list.list_name}" with ${ingredient_count || 0} items`);
                    } else {
                        console.error('❌ Invalid list data - no valid sections found:', sectionsData);
                    }
                } else {
                    console.error('❌ Invalid list data format:', listData);
                }
            } else {
                console.error('❌ Failed to load list:', data);
            }
        } catch (err) {
            console.error('❌ Failed to load list:', err);
        }
    };

    // Delete a grocery list
    const deleteList = async (listId, listName) => {
        if (!window.confirm(`Are you sure you want to delete "${listName}"? This action cannot be undone.`)) {
            return;
        }

        try {
            console.log(`🗑️ Deleting grocery list: ${listId}`);
            const response = await fetch(`${getApiUrl()}/api/v2/grocery-lists/${listId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (response.ok && data.success) {
                console.log(`✅ Successfully deleted list: "${listName}"`);
                
                // If the deleted list was currently loaded, clear the workspace
                if (currentList && currentList.id === listId) {
                    setSections({
                        produce: { name: 'Produce', items: [] },
                        meat_seafood: { name: 'Meat & Seafood', items: [] },
                        pantry: { name: 'Pantry', items: [] },
                        other: { name: 'Other', items: [] }
                    });
                    setCurrentList(null);
                    setSelectedListId(null);
                }
                
                // Refresh the saved lists
                if (typeof loadSavedLists === 'function') {
                    loadSavedLists();
                }
            } else {
                throw new Error(data.error || 'Failed to delete list');
            }
        } catch (err) {
            console.error('❌ Failed to delete list:', err);
            alert(`Failed to delete "${listName}". Please try again.`);
        }
    };

    const addCustomItem = (sectionKey, itemName) => {
        const newItem = {
            id: `custom-${Date.now()}`,
            name: itemName,
            isCustom: true,
            recipes: []
        };

        setSections(prev => ({
            ...prev,
            [sectionKey]: {
                ...prev[sectionKey],
                items: [...prev[sectionKey].items, newItem]
            }
        }));
    };

    // Notion-style inline adding
    const handleInlineAdd = () => {
        if (!inlineItemName.trim()) return;
        
        // Add to 'other' section by default
        addCustomItem('other', inlineItemName.trim());
        
        // Reset state
        setInlineItemName('');
        setIsAddingInline(false);
        setShowInlineAdd(false);
    };

    const removeItem = (sectionKey, itemId) => {
        setSections(prev => ({
            ...prev,
            [sectionKey]: {
                ...prev[sectionKey],
                items: prev[sectionKey].items.filter(item => item.id !== itemId)
            }
        }));
    };

    const updateItem = (sectionKey, itemId, newName) => {
        setSections(prev => ({
            ...prev,
            [sectionKey]: {
                ...prev[sectionKey],
                items: prev[sectionKey].items.map(item => 
                    item.id === itemId 
                        ? { ...item, name: newName.trim() }
                        : item
                )
            }
        }));
        console.log(`✅ Updated item in ${sectionKey}: "${newName.trim()}"`);
    };

    // Smart ingredient consolidation function
    const consolidateIngredients = () => {
        console.log('🧠 Starting smart ingredient consolidation...');
        
        setSections(prev => {
            const newSections = { ...prev };
            
            Object.keys(newSections).forEach(sectionKey => {
                const items = newSections[sectionKey].items;
                console.log(`🔍 Processing section ${sectionKey} with ${items.length} items:`, items.map(i => i.name));
                
                const consolidatedItems = [];
                const processedItems = new Set();
                
                items.forEach((item, index) => {
                    if (processedItems.has(index)) return;
                    
                    // Find similar items
                    const similarItems = [item];
                    const currentItemNormalized = normalizeIngredientName(item.name);
                    console.log(`🔍 Looking for matches for "${item.name}" (normalized: "${currentItemNormalized}")`);
                    
                    items.forEach((otherItem, otherIndex) => {
                        if (otherIndex > index && !processedItems.has(otherIndex)) {
                            const otherItemNormalized = normalizeIngredientName(otherItem.name);
                            const isSimilar = areIngredientsSimilar(currentItemNormalized, otherItemNormalized);
                            
                            console.log(`  🔍 Comparing with "${otherItem.name}" (normalized: "${otherItemNormalized}") - Similar: ${isSimilar}`);
                            
                            if (isSimilar) {
                                similarItems.push(otherItem);
                                processedItems.add(otherIndex);
                                console.log(`  ✅ Found match! Added to similar items.`);
                            }
                        }
                    });
                    
                    processedItems.add(index);
                    
                    // Consolidate similar items
                    if (similarItems.length > 1) {
                        const consolidated = consolidateSimilarItems(similarItems);
                        consolidatedItems.push(consolidated);
                        console.log(`🔄 Consolidated ${similarItems.length} items: "${consolidated.name}"`);
                    } else {
                        consolidatedItems.push(item);
                    }
                });
                
                newSections[sectionKey].items = consolidatedItems;
            });
            
            return newSections;
        });
    };

    // Normalize ingredient names for comparison
    const normalizeIngredientName = (name) => {
        return name.toLowerCase()
            .replace(/\s+/g, ' ')
            .replace(/[^\w\s]/g, '') // Remove punctuation
            .replace(/\b(cloves?|pieces?|slices?|cups?|tbsp|tsp|oz|lbs?|pounds?|grams?|kg)\b/g, '') // Remove units
            .replace(/\b(of|the|a|an)\b/g, '') // Remove articles
            .trim();
    };

    // Check if two ingredients are similar enough to consolidate
    const areIngredientsSimilar = (name1, name2) => {
        // Exact match after normalization
        if (name1 === name2) return true;
        
        // Handle plurals and common variations
        const variations = [
            [name1, name2],
            [name1.replace(/s$/, ''), name2.replace(/s$/, '')], // Remove plural 's'
            [name1.replace(/ies$/, 'y'), name2.replace(/ies$/, 'y')], // berries -> berry
            [name1.replace(/es$/, ''), name2.replace(/es$/, '')] // tomatoes -> tomato
        ];
        
        return variations.some(([v1, v2]) => v1 === v2 && v1.length > 2);
    };

    // Consolidate similar items into one item
    const consolidateSimilarItems = (items) => {
        const allRecipes = [...new Set(items.flatMap(item => item.recipes || []))];
        const quantities = [];
        let baseName = '';
        
        // Extract quantities and find the most complete name
        items.forEach(item => {
            const quantity = extractQuantityFromName(item.name);
            if (quantity) {
                quantities.push(quantity);
            }
            
            // Use the longest name as base (likely most descriptive)
            if (item.name.length > baseName.length) {
                baseName = item.name;
            }
        });
        
        // Combine quantities if possible
        let finalName = baseName;
        if (quantities.length > 0) {
            const totalQuantity = combineQuantities(quantities);
            if (totalQuantity) {
                // Replace the quantity in the base name with combined quantity
                const nameWithoutQuantity = baseName.replace(/^\d+(\.\d+)?\s*\w+\s*/, '');
                finalName = `${totalQuantity} ${nameWithoutQuantity}`;
            }
        }
        
        return {
            id: `consolidated-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            name: finalName,
            recipes: allRecipes,
            isCustom: false,
            isConsolidated: true,
            originalItems: items.length
        };
    };

    // Extract quantity from ingredient name
    const extractQuantityFromName = (name) => {
        const quantityMatch = name.match(/^(\d+(?:\.\d+)?)\s*(\w+)/);
        if (quantityMatch) {
            return {
                amount: parseFloat(quantityMatch[1]),
                unit: quantityMatch[2].toLowerCase()
            };
        }
        return null;
    };

    // Combine quantities with same units
    const combineQuantities = (quantities) => {
        const unitGroups = {};
        
        quantities.forEach(q => {
            const unit = normalizeUnit(q.unit);
            if (!unitGroups[unit]) {
                unitGroups[unit] = 0;
            }
            unitGroups[unit] += q.amount;
        });
        
        // If all quantities have the same unit, combine them
        const units = Object.keys(unitGroups);
        if (units.length === 1) {
            const unit = units[0];
            const totalAmount = unitGroups[unit];
            return `${totalAmount} ${unit}${totalAmount > 1 ? 's' : ''}`;
        }
        
        return null; // Can't combine different units
    };

    // Normalize units for comparison
    const normalizeUnit = (unit) => {
        const unitMap = {
            'cup': 'cup', 'cups': 'cup',
            'tbsp': 'tbsp', 'tablespoon': 'tbsp', 'tablespoons': 'tbsp',
            'tsp': 'tsp', 'teaspoon': 'tsp', 'teaspoons': 'tsp',
            'oz': 'oz', 'ounce': 'oz', 'ounces': 'oz',
            'lb': 'lb', 'lbs': 'lb', 'pound': 'lb', 'pounds': 'lb',
            'clove': 'clove', 'cloves': 'clove',
            'piece': 'piece', 'pieces': 'piece',
            'slice': 'slice', 'slices': 'slice'
        };
        return unitMap[unit.toLowerCase()] || unit.toLowerCase();
    };

    // Pantry integration functions
    const isItemInPantry = (groceryItemName) => {
        const coreIngredient = extractCoreIngredient(groceryItemName);
        console.log(`🔍 Checking if "${groceryItemName}" (core: "${coreIngredient}") is in pantry...`);
        
        // Check for compound ingredients first (e.g., "salt and pepper")
        const compoundMatch = checkCompoundIngredient(coreIngredient);
        if (compoundMatch.isCompound) {
            console.log(`  🔄 Detected compound ingredient with ${compoundMatch.matchedPantryItems.length} parts: ${compoundMatch.matchedPantryItems.map(p => p.name).join(', ')}`);
            return compoundMatch.allPartsInPantry;
        }
        
        // Regular single ingredient matching
        const foundMatch = pantryItems.some(pantryItem => {
            // Try multiple matching strategies
            const strategies = [
                // Strategy 1: Exact core ingredient match
                () => coreIngredient.toLowerCase() === pantryItem.name.toLowerCase(),
                
                // Strategy 2: Core ingredient contains pantry item
                () => coreIngredient.toLowerCase().includes(pantryItem.name.toLowerCase()),
                
                // Strategy 3: Pantry item contains core ingredient  
                () => pantryItem.name.toLowerCase().includes(coreIngredient.toLowerCase()),
                
                // Strategy 4: Original normalization (fallback)
                () => {
                    const normalizedGroceryItem = normalizeIngredientName(groceryItemName);
                    const normalizedPantryItem = normalizeIngredientName(pantryItem.name);
                    return areIngredientsSimilar(normalizedGroceryItem, normalizedPantryItem);
                }
            ];
            
            for (let i = 0; i < strategies.length; i++) {
                const isMatch = strategies[i]();
                if (isMatch) {
                    console.log(`  ✅ Strategy ${i+1} matched with pantry "${pantryItem.name}"`);
                    return true;
                }
            }
            
            console.log(`  ❌ No match with pantry "${pantryItem.name}"`);
            return false;
        });
        
        console.log(`  🎯 Final result for "${groceryItemName}": ${foundMatch ? 'IN PANTRY' : 'NOT IN PANTRY'}`);
        return foundMatch;
    };

    // Check if ingredient is compound (multiple ingredients in one)
    const checkCompoundIngredient = (ingredientText) => {
        const separators = [' and ', ' & ', ', ', ' + ', ' or '];
        let parts = [ingredientText];
        let usedSeparator = null;
        
        // Split by common separators (case insensitive)
        const lowerText = ingredientText.toLowerCase();
        for (const separator of separators) {
            if (lowerText.includes(separator)) {
                parts = lowerText.split(separator);
                usedSeparator = separator;
                break;
            }
        }
        
        // If we found multiple parts, check if each part is in pantry
        if (parts.length > 1) {
            const matchedPantryItems = [];
            const allPartsInPantry = parts.every(part => {
                const trimmedPart = part.trim();
                
                const matchingPantryItem = pantryItems.find(pantryItem => {
                    const pantryName = pantryItem.name.toLowerCase();
                    const partName = trimmedPart;
                    
                    // Try multiple matching strategies for each part
                    const matches = [
                        partName === pantryName, // Exact match
                        partName.includes(pantryName), // Part contains pantry
                        pantryName.includes(partName), // Pantry contains part
                        // Handle "black pepper" matching "pepper"
                        partName.includes(pantryName.split(' ').pop()), // Last word match
                        pantryName.includes(partName.split(' ').pop()), // Last word match reverse
                    ];
                    
                    return matches.some(match => match);
                });
                
                if (matchingPantryItem) {
                    matchedPantryItems.push(matchingPantryItem);
                    return true;
                } else {
                    return false;
                }
            });
            
            return {
                isCompound: true,
                parts: parts,
                matchedPantryItems: matchedPantryItems,
                allPartsInPantry: allPartsInPantry
            };
        }
        
        return { isCompound: false };
    };

    // Get detailed pantry match information for UI display
    const getPantryMatchInfo = (groceryItemName) => {
        const coreIngredient = extractCoreIngredient(groceryItemName);
        
        // Check for compound ingredients first
        const compoundMatch = checkCompoundIngredient(coreIngredient);
        if (compoundMatch.isCompound && compoundMatch.allPartsInPantry) {
            return {
                inPantry: true,
                isCompound: true,
                matchedItems: compoundMatch.matchedPantryItems,
                displayText: `All parts in pantry: ${compoundMatch.matchedPantryItems.map(p => p.name).join(', ')}`
            };
        }
        
        // Regular single ingredient matching
        const matchingPantryItem = pantryItems.find(pantryItem => {
            const strategies = [
                () => coreIngredient.toLowerCase() === pantryItem.name.toLowerCase(),
                () => coreIngredient.toLowerCase().includes(pantryItem.name.toLowerCase()),
                () => pantryItem.name.toLowerCase().includes(coreIngredient.toLowerCase()),
            ];
            
            return strategies.some(strategy => strategy());
        });
        
        if (matchingPantryItem) {
            return {
                inPantry: true,
                isCompound: false,
                matchedItems: [matchingPantryItem],
                displayText: `Have: ${matchingPantryItem.name}`
            };
        }
        
        return { inPantry: false };
    };

    // Extract core ingredient from complex recipe descriptions
    const extractCoreIngredient = (complexName) => {
        // Remove quantities and measurements (enhanced for fractions and units)
        let core = complexName
            // Remove leading fractions and quantities
            .replace(/^[\d\/¼½¾⅓⅔⅛⅜⅝⅞]+\s*/i, '')
            // Remove quantities with units
            .replace(/^\d+(\.\d+)?\s*(lb|lbs|pound|pounds|oz|ounces?|cup|cups|tbsp|tsp|tablespoons?|teaspoons?|cloves?|pieces?|slices?)\s+/i, '')
            // Remove standalone units that might be left (enhanced)
            .replace(/^(teaspoons?|tablespoons?|cups?|tbsp\.?|tsp\.?|lb\.?|lbs\.?|oz\.?|ounces?|pounds?|cloves?|pieces?|slices?)\s+/i, '')
            // Remove any remaining quantities with periods
            .replace(/\d+(\.\d+)?\s*(lb\.?|lbs\.?|oz\.?|ounces?|cup\.?|cups\.?|tbsp\.?|tsp\.?|tablespoons?|teaspoons?|cloves?|pieces?|slices?)/gi, '');
        
        // Smart parentheses handling - check what's inside vs outside
        const parenMatch = core.match(/^([^(]*)\(([^)]*)\)/);
        if (parenMatch) {
            const beforeParens = parenMatch[1].trim();
            const insideParens = parenMatch[2].trim();
            
            // If what's inside the parentheses looks more like an ingredient than what's outside
            const beforeWords = beforeParens.split(' ').filter(w => w.length > 2);
            const insideWords = insideParens.split(' ').filter(w => w.length > 2);
            
            // Heuristic: if inside has more substantial words or contains known ingredient words
            const ingredientWords = ['chicken', 'beef', 'pork', 'fish', 'salmon', 'turkey', 'lamb', 'bread', 'flour', 'rice', 'pasta', 'cheese', 'milk', 'butter', 'oil', 'tomato', 'onion', 'garlic', 'mushroom'];
            const insideHasIngredient = ingredientWords.some(word => insideParens.toLowerCase().includes(word));
            const beforeHasIngredient = ingredientWords.some(word => beforeParens.toLowerCase().includes(word));
            
            if (insideHasIngredient && !beforeHasIngredient) {
                core = insideParens;
            } else if (insideWords.length > beforeWords.length && beforeWords.length <= 1) {
                core = insideParens;
            } else {
                core = beforeParens;
            }
        } else {
            // Remove any remaining parenthetical descriptions
            core = core.replace(/\([^)]*\)/g, '');
        }
        
        // Remove common descriptive words (but preserve compound separators)
        core = core
            .replace(/\b(finely|coarsely|roughly|fresh|dried|frozen|organic|chopped|diced|sliced|minced|grated|shredded|such as|boneless|skinless|patted|dry)\b/gi, '')
            .replace(/\b(assorted|mixed|variety|pack|package|as needed)\b/gi, '');
        
        // Clean up extra spaces and punctuation (but preserve 'and', '&', etc.)
        core = core
            .replace(/[,\-\.]/g, ' ')
            .replace(/\s+/g, ' ')
            .trim();
        
        // For compound ingredients, don't truncate - keep the full phrase
        const lowerCore = core.toLowerCase();
        if (lowerCore.includes(' and ') || lowerCore.includes(' & ') || lowerCore.includes(', ')) {
            const result = core.trim() || complexName;
            return result;
        }
        
        // Take the first meaningful words (for single ingredients only)
        const words = core.split(' ').filter(word => word.length > 2);
        
        // For ingredients like "Extra Virgin Olive Oil", take more words
        if (words.length <= 4) {
            core = words.join(' '); // Take all words if 4 or fewer
        } else {
            core = words.slice(0, 3).join(' '); // Take first 3 meaningful words for longer names
        }
        
        const result = core.trim() || complexName; // Fallback to original if extraction fails
        return result;
    };

    const hideItem = (sectionKey, itemId) => {
        setHiddenItems(prev => new Set([...prev, `${sectionKey}-${itemId}`]));
        console.log(`✅ Hidden item from grocery list - already in pantry`);
    };

    const unhideItem = (sectionKey, itemId) => {
        setHiddenItems(prev => {
            const newSet = new Set(prev);
            newSet.delete(`${sectionKey}-${itemId}`);
            return newSet;
        });
        console.log(`🔄 Unhidden item - added back to grocery list`);
    };

    const isItemHidden = (sectionKey, itemId) => {
        return hiddenItems.has(`${sectionKey}-${itemId}`);
    };

    const getVisibleItems = (sectionKey) => {
        const allItems = sections[sectionKey]?.items || [];
        if (showHidden) {
            return allItems; // Show all items when "show hidden" is enabled
        }
        return allItems.filter(item => !isItemHidden(sectionKey, item.id));
    };

    const getHiddenCount = () => {
        let count = 0;
        Object.keys(sections).forEach(sectionKey => {
            const items = sections[sectionKey]?.items || [];
            count += items.filter(item => isItemHidden(sectionKey, item.id)).length;
        });
        return count;
    };

    // Save current list functionality
    const [showSaveDialog, setShowSaveDialog] = useState(false);
    const [saveListName, setSaveListName] = useState('');
    const [isEditingName, setIsEditingName] = useState(false);
    const [editedListName, setEditedListName] = useState('');
    const [showOverwriteDialog, setShowOverwriteDialog] = useState(false);
    const [duplicateListInfo, setDuplicateListInfo] = useState(null);

    // Function to check if a list name already exists
    const checkForDuplicateName = async (listName) => {
        try {
            // Get user ID from auth context
            const userId = user?.id;
            
            if (!userId) {
                console.warn('⚠️ No user ID available');
                return null;
            }
            
            const headers = {
                'Content-Type': 'application/json'
            };
            
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }

            const response = await fetch(`${getApiUrl()}/api/v2/grocery-lists/user/${userId}`, {
                headers
            });
            const data = await response.json();

            if (data.success) {
                const existingLists = data.grocery_lists || data.data?.grocery_lists || [];
                const duplicateList = existingLists.find(list => 
                    list.name.toLowerCase().trim() === listName.toLowerCase().trim()
                );
                return duplicateList || null;
            }
            return null;
        } catch (error) {
            console.error('❌ Error checking for duplicate names:', error);
            return null;
        }
    };

    const saveCurrentList = async (forceOverwrite = false) => {
        const listName = currentList?.name || saveListName || 'New Grocery List';
        
        if (!listName.trim()) {
            alert('Please enter a name for your grocery list');
            return;
        }

        // Check for duplicate names unless we're forcing an overwrite
        if (!forceOverwrite) {
            const duplicateList = await checkForDuplicateName(listName.trim());
            if (duplicateList) {
                // Found a duplicate - show overwrite dialog
                setDuplicateListInfo(duplicateList);
                setShowOverwriteDialog(true);
                setShowSaveDialog(false); // Hide the save dialog
                return;
            }
        }

        // Debug: Check if we have any items to save
        const totalItems = Object.keys(sections).reduce((total, sectionKey) => {
            return total + (sections[sectionKey]?.items?.length || 0);
        }, 0);

        console.log('💾 Save attempt - Current sections state:', sections);
        console.log('💾 Save attempt - Total items across all sections:', totalItems);
        console.log('💾 Save attempt - Current list:', currentList);

        if (totalItems === 0) {
            const proceed = window.confirm('You are about to save an empty grocery list. Are you sure you want to continue?');
            if (!proceed) return;
        }

        try {
            console.log('💾 About to save list with sections:', sections);
            console.log('💾 Section keys:', Object.keys(sections));
            console.log('💾 Section items count:', Object.keys(sections).map(key => ({
                section: key,
                itemCount: sections[key]?.items?.length || 0,
                items: sections[key]?.items?.map(item => item.name) || []
            })));
            
            // Calculate total item count
            const totalItemCount = Object.keys(sections).reduce((total, sectionKey) => {
                return total + (sections[sectionKey]?.items?.length || 0);
            }, 0);
            
            // Create the list data - this IS the sections object
            const listDataToSave = {
                ...sections,
                ingredient_count: totalItemCount
            };
            
            const listName = currentList?.name || saveListName || 'My Grocery List';
            
            console.log('💾 List data being saved:', JSON.stringify(listDataToSave, null, 2));
            console.log('💾 List name:', listName);
            
            // If we're overwriting, use PUT to update existing list
            const isOverwrite = forceOverwrite && duplicateListInfo;
            const method = isOverwrite ? 'PUT' : 'POST';
            const url = isOverwrite 
                ? `${getApiUrl()}/api/v2/grocery-lists/${duplicateListInfo.id}`
                : `${getApiUrl()}/api/v2/grocery-lists`;
            
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: currentUser?.id,
                    list_name: listName.trim(),
                    list_data: listDataToSave,
                    recipe_ids: currentList?.isFromMealPlan ? mealPlanRecipes : []
                })
            });

            if (response.ok) {
                const data = await response.json();
                console.log('✅ List saved successfully:', data);
                setShowSaveDialog(false);
                setShowOverwriteDialog(false);
                setSaveListName('');
                setDuplicateListInfo(null);
                
                // Clear unsaved changes flag
                setHasUnsavedChanges(false);
                
                // Update current list to the saved version
                const listId = isOverwrite ? duplicateListInfo.id : data.list_id;
                setCurrentList({
                    id: listId,
                    name: listName.trim(),
                    isFromMealPlan: false
                });
                
                // Refresh the saved lists
                if (typeof loadSavedLists === 'function') {
                    loadSavedLists();
                }
                
                const successMessage = isOverwrite 
                    ? '✅ Grocery list updated successfully!' 
                    : '✅ Grocery list saved successfully!';
                alert(successMessage);
            } else {
                const errorData = await response.json();
                console.error('❌ Save error details:', errorData);
                throw new Error(errorData.error || 'Failed to save list');
            }
        } catch (error) {
            console.error('❌ Error saving list:', error);
            alert('Failed to save grocery list. Please try again.');
        }
    };

    // Handle sharing grocery list with household
    const handleShare = (household, result) => {
        console.log('🔗 Shared with household:', household.name);
        console.log('🔗 Share result:', result);
        
        // Show success message
        const message = `✅ Shared "${currentList?.name}" with ${household.name}!\n${result.invitations_created} member(s) invited.`;
        alert(message);
        
        // Optionally mark this list as shared in UI
        if (currentList) {
            setCurrentList({
                ...currentList,
                isShared: true,
                sharedWith: household.name
            });
        }
    };

    // Smart combination detection
    const getCombinableItems = (targetItem) => {
        const combinableItems = [];
        const targetCore = extractCoreIngredient(targetItem.name);
        
        Object.keys(sections).forEach(sectionKey => {
            sections[sectionKey].items.forEach(item => {
                if (item.id !== targetItem.id) {
                    const itemCore = extractCoreIngredient(item.name);
                    const similarity = areIngredientsSimilar(
                        normalizeIngredientName(targetCore),
                        normalizeIngredientName(itemCore)
                    );
                    
                    if (similarity) {
                        combinableItems.push({
                            item,
                            sectionKey,
                            confidence: 'HIGH' // We can add confidence levels later
                        });
                    }
                }
            });
        });
        
        return combinableItems;
    };

    // Check if two items can be combined
    const canCombineItems = (item1, item2) => {
        const core1 = extractCoreIngredient(item1.name);
        const core2 = extractCoreIngredient(item2.name);
        
        // Standard similarity check
        const standardMatch = areIngredientsSimilar(
            normalizeIngredientName(core1),
            normalizeIngredientName(core2)
        );
        
        if (standardMatch) return true;
        
        // Smart oil detection - different types of oils can be combined
        const isOil1 = /oil/i.test(core1);
        const isOil2 = /oil/i.test(core2);
        
        if (isOil1 && isOil2) {
            return true; // Allow oil combinations
        }
        
        // Smart vinegar detection
        const isVinegar1 = /vinegar/i.test(core1);
        const isVinegar2 = /vinegar/i.test(core2);
        
        if (isVinegar1 && isVinegar2) {
            return true; // Allow vinegar combinations
        }
        
        return false;
    };

    // Combine two specific items
    const combineItems = (sourceItem, targetItem, sourceSectionKey, targetSectionKey) => {
        // Create unique combination signature
        const combinationSignature = `${sourceItem.id}+${targetItem.id}`;
        
        // Prevent duplicate combinations
        if (isProcessingCombination) {
            console.log('🚫 Combination already in progress, skipping duplicate');
            return;
        }
        
        if (recentCombinations.has(combinationSignature)) {
            console.log('🚫 This exact combination was recently processed, skipping duplicate');
            return;
        }
        
        // Check if items still exist in their sections
        const sourceExists = sections[sourceSectionKey]?.items.some(item => item.id === sourceItem.id);
        const targetExists = sections[targetSectionKey]?.items.some(item => item.id === targetItem.id);
        
        if (!sourceExists || !targetExists) {
            console.log('🚫 One or both items no longer exist, skipping combination');
            return;
        }
        
        setIsProcessingCombination(true);
        
        // Track this combination
        setRecentCombinations(prev => new Set([...prev, combinationSignature]));
        
        console.log(`🔄 Combining "${sourceItem.name}" with "${targetItem.name}"`);
        console.log(`🔄 Source section: ${sourceSectionKey}, Target section: ${targetSectionKey}`);
        console.log(`🔄 Source ID: ${sourceItem.id}, Target ID: ${targetItem.id}`);
        
        const itemsToConsolidate = [sourceItem, targetItem];
        console.log(`🔄 Items to consolidate:`, itemsToConsolidate);
        
        const combinedItem = consolidateSimilarItems(itemsToConsolidate);
        combinedItem.id = `combined-${Date.now()}`;
        
        console.log(`🔄 Combined item created:`, combinedItem);
        console.log(`🔄 Combined item ingredients count:`, combinedItem.recipes?.length || 0);
        
        // Store undo information
        setLastCombination({
            combined: combinedItem,
            original: [
                { item: sourceItem, sectionKey: sourceSectionKey },
                { item: targetItem, sectionKey: targetSectionKey }
            ],
            timestamp: Date.now()
        });
        
        setSections(prev => {
            // Create a deep copy to avoid mutations
            const newSections = JSON.parse(JSON.stringify(prev));
            
            console.log(`🔄 BEFORE COMBINATION - Target section ${targetSectionKey}:`, 
                newSections[targetSectionKey].items.map(i => `${i.id}: ${i.name}`)
            );
            
            console.log(`🔄 Items to remove: sourceItem.id=${sourceItem.id}, targetItem.id=${targetItem.id}`);
            
            // Remove both items from ALL sections atomically
            let totalRemoved = 0;
            Object.keys(newSections).forEach(sectionKey => {
                const beforeCount = newSections[sectionKey].items.length;
                newSections[sectionKey].items = newSections[sectionKey].items.filter(item => 
                    item.id !== sourceItem.id && item.id !== targetItem.id
                );
                const afterCount = newSections[sectionKey].items.length;
                const removed = beforeCount - afterCount;
                totalRemoved += removed;
                
                if (removed > 0) {
                    console.log(`🔄 Section ${sectionKey}: removed ${removed} items`);
                }
            });
            
            if (totalRemoved !== 2) {
                console.warn(`🚨 Expected to remove 2 items, but removed ${totalRemoved}`);
            }
            
            console.log(`🔄 AFTER REMOVAL - Target section ${targetSectionKey}:`, 
                newSections[targetSectionKey].items.map(i => `${i.id}: ${i.name}`)
            );
            
            // Add combined item to target section
            console.log(`🔄 About to add combined item:`, combinedItem);
            newSections[targetSectionKey].items.push(combinedItem);
            
            console.log(`🔄 AFTER ADDITION - Target section ${targetSectionKey}:`, 
                newSections[targetSectionKey].items.map(i => `${i.id}: ${i.name}`)
            );
            
            // Check for duplicates
            const ids = newSections[targetSectionKey].items.map(i => i.id);
            const duplicateIds = ids.filter((id, index) => ids.indexOf(id) !== index);
            if (duplicateIds.length > 0) {
                console.error(`🚨 DUPLICATE IDs DETECTED in section ${targetSectionKey}:`, duplicateIds);
            }
            
            return newSections;
        });
        
        console.log(`✅ Successfully combined into: "${combinedItem.name}"`);
        
        // Reset processing flag after a brief delay to allow state to settle
        setTimeout(() => {
            setIsProcessingCombination(false);
            // Clear recent combinations after 5 seconds
            setTimeout(() => {
                setRecentCombinations(new Set());
            }, 5000);
        }, 100);
    };

    // Undo last combination    
    const undoLastCombination = () => {
        if (!lastCombination) return;
        
        console.log('⟲ Undoing last combination...', lastCombination);
        
        setSections(prev => {
            const newSections = { ...prev };
            
            // Remove combined item
            const combinedItemSection = Object.keys(newSections).find(sectionKey =>
                newSections[sectionKey].items.some(item => item.id === lastCombination.combined.id)
            );
            
            console.log(`⟲ Found combined item in section: ${combinedItemSection}`);
            
            if (combinedItemSection) {
                console.log(`⟲ Before removing combined item:`, newSections[combinedItemSection].items.map(i => `${i.id}: ${i.name}`));
                newSections[combinedItemSection].items = newSections[combinedItemSection].items
                    .filter(item => item.id !== lastCombination.combined.id);
                console.log(`⟲ After removing combined item:`, newSections[combinedItemSection].items.map(i => `${i.id}: ${i.name}`));
            }
            
            // Restore original items
            lastCombination.original.forEach(({ item, sectionKey }) => {
                console.log(`⟲ Restoring "${item.name}" to section ${sectionKey}`);
                newSections[sectionKey].items.push(item);
            });
            
            return newSections;
        });
        
        setLastCombination(null);
        console.log('✅ Combination undone successfully');
    };

    // Drag and drop handler for items and sections
    const handleDragStart = (event) => {
        const { active } = event;
        const activeData = active.data.current;
        
        if (activeData?.type === 'item') {
            const item = activeData.item;
            setDraggedItem(item);
        }
    };

    const handleDragOver = (event) => {
        const { active, over } = event;
        
        if (!over || !draggedItem) return;
        
        const activeData = active.data.current;
        const overData = over.data.current;
        
        // Check if we're hovering over a combinable item
        if (activeData?.type === 'item' && overData?.type === 'item') {
            const draggedItem = activeData.item;
            const hoverItem = overData.item;
            
            if (canCombineItems(draggedItem, hoverItem)) {
                const previewResult = consolidateSimilarItems([draggedItem, hoverItem]);
                
                // Detect combination type for better messaging
                const core1 = extractCoreIngredient(draggedItem.name);
                const core2 = extractCoreIngredient(hoverItem.name);
                const isOilCombination = /oil/i.test(core1) && /oil/i.test(core2);
                const isVinegarCombination = /vinegar/i.test(core1) && /vinegar/i.test(core2);
                
                let previewText = previewResult.name;
                let confidence = 'HIGH';
                
                if (isOilCombination) {
                    previewText = "Oil (combined for shopping)";
                    confidence = 'SMART';
                } else if (isVinegarCombination) {
                    previewText = "Vinegar (combined for shopping)";
                    confidence = 'SMART';
                }
                
                setCombinationPreview({
                    targetItemId: hoverItem.id,
                    previewText: previewText,
                    confidence: confidence
                });
            } else {
                setCombinationPreview(null);
            }
        } else {
            setCombinationPreview(null);
        }
    };

    const handleDragEnd = (event) => {
        // Clear drag state
        setDraggedItem(null);
        setCombinationPreview(null);
        // Reset combination processing after drag ends
        setTimeout(() => setIsProcessingCombination(false), 50);
        const { active, over } = event;
        
        // Debug logging
        console.log('🎯 Drag End Event:', {
            activeId: active.id,
            overId: over?.id,
            activeType: active.data.current?.type,
            overType: over?.data.current?.type
        });
        
        if (!over || active.id === over.id) {
            console.log('❌ No valid drop target found');
            return;
        }

        const activeData = active.data.current;
        const overData = over.data.current;

        // Handle section reordering
        if (activeData?.type === 'section' && overData?.type === 'section') {
            // Extract section keys from IDs (remove 'section-' prefix)
            const activeSectionKey = active.id.replace('section-', '');
            const overSectionKey = over.id.replace('section-', '');
            
            console.log(`🔄 Section reorder: ${activeSectionKey} → ${overSectionKey}`);
            
            const oldIndex = sectionOrder.indexOf(activeSectionKey);
            const newIndex = sectionOrder.indexOf(overSectionKey);
            
            if (oldIndex !== -1 && newIndex !== -1) {
                setSectionOrder(arrayMove(sectionOrder, oldIndex, newIndex));
                console.log(`✅ Moved section ${activeSectionKey} from position ${oldIndex} to ${newIndex}`);
            } else {
                console.log('❌ Section indices not found:', { oldIndex, newIndex, sectionOrder });
            }
            return;
        }

        // Handle item reordering within same section
        if (activeData?.type === 'item' && overData?.type === 'item' && 
            activeData.sectionKey === overData.sectionKey) {
            
            const sectionKey = activeData.sectionKey;
            const section = sections[sectionKey];
            const activeItem = section.items.find(item => item.id === active.id);
            const overItem = section.items.find(item => item.id === over.id);
            
            // Check if this is a combination attempt within same section
            if (activeItem && overItem && canCombineItems(activeItem, overItem)) {
                console.log('🔄 Detected same-section combination attempt');
                combineItems(activeItem, overItem, sectionKey, sectionKey);
                return;
            }
            
            // Regular reordering logic
            const oldIndex = section.items.findIndex(item => item.id === active.id);
            const newIndex = section.items.findIndex(item => item.id === over.id);
            
            if (oldIndex !== -1 && newIndex !== -1) {
                setSections(prev => ({
                    ...prev,
                    [sectionKey]: {
                        ...prev[sectionKey],
                        items: arrayMove(prev[sectionKey].items, oldIndex, newIndex)
                    }
                }));
                console.log(`🔄 Reordered item in ${sectionKey}: ${oldIndex} → ${newIndex}`);
            }
            return;
        }

        // Handle item moving between sections (updated for new drop zone type)
        if (activeData?.type === 'item' && overData?.type === 'section-drop') {
            const sourceSectionKey = activeData.sectionKey;
            const targetSectionKey = overData.sectionKey;
            const itemToMove = sections[sourceSectionKey].items.find(item => item.id === active.id);
            
            console.log(`📦 Item cross-section move: ${sourceSectionKey} → ${targetSectionKey}`);
            
            if (itemToMove && sourceSectionKey !== targetSectionKey) {
                setSections(prev => ({
                    ...prev,
                    [sourceSectionKey]: {
                        ...prev[sourceSectionKey],
                        items: prev[sourceSectionKey].items.filter(item => item.id !== active.id)
                    },
                    [targetSectionKey]: {
                        ...prev[targetSectionKey],
                        items: [...prev[targetSectionKey].items, itemToMove]
                    }
                }));
                console.log(`✅ Moved item "${itemToMove.name}" from ${sourceSectionKey} to ${targetSectionKey}`);
            }
            return;
        }

        // Handle item moving to specific position in different section
        if (activeData?.type === 'item' && overData?.type === 'item' && 
            activeData.sectionKey !== overData.sectionKey) {
            
            const sourceSectionKey = activeData.sectionKey;
            const targetSectionKey = overData.sectionKey;
            const itemToMove = sections[sourceSectionKey].items.find(item => item.id === active.id);
            const targetItem = sections[targetSectionKey].items.find(item => item.id === over.id);
            
            // Check if this is a combination attempt
            if (itemToMove && targetItem && canCombineItems(itemToMove, targetItem)) {
                console.log('🔄 Detected combination attempt via drag & drop');
                combineItems(itemToMove, targetItem, sourceSectionKey, targetSectionKey);
                return;
            }
            
            // Regular reordering logic
            const targetIndex = sections[targetSectionKey].items.findIndex(item => item.id === over.id);
            
            if (itemToMove) {
                setSections(prev => {
                    const newTargetItems = [...prev[targetSectionKey].items];
                    newTargetItems.splice(targetIndex, 0, itemToMove);
                    
                    return {
                        ...prev,
                        [sourceSectionKey]: {
                            ...prev[sourceSectionKey],
                            items: prev[sourceSectionKey].items.filter(item => item.id !== active.id)
                        },
                        [targetSectionKey]: {
                            ...prev[targetSectionKey],
                            items: newTargetItems
                        }
                    };
                });
                console.log(`🎯 Moved item "${itemToMove.name}" from ${sourceSectionKey} to position ${targetIndex} in ${targetSectionKey}`);
            }
        }
    };

    // Handler for loading a saved list
    const handleLoadList = (loadedList) => {
        console.log('📂 Loading saved grocery list:', loadedList);
        
        // Set the current list (backend always returns standard format now)
        setCurrentList({
            id: loadedList.id,
            name: loadedList.name,
            data: loadedList.items
        });
        
        // Initialize empty sections with proper structure
        const emptySections = {
            produce: { name: 'Produce', items: [] },
            meat_seafood: { name: 'Meat & Seafood', items: [] },
            pantry: { name: 'Pantry', items: [] },
            other: { name: 'Other', items: [] }
        };
        
        // Parse and set the grocery list data
        if (loadedList.items && typeof loadedList.items === 'object') {
            console.log('📂 Processing list items...');
            
            // Check if this is whiteboard format (flat array of items)
            if (Array.isArray(loadedList.items)) {
                console.log('📂 Loading PHASE 2 whiteboard format (flat array)');
                
                // Convert flat array to sections format
                const convertedSections = { ...emptySections };
                convertedSections.other.items = loadedList.items.map(item => ({
                    id: item.id || `item-${Date.now()}-${Math.random()}`,
                    name: item.name || 'Unknown item',
                    checked: item.checked || false
                }));
                
                setSections(convertedSections);
                setShowLoadPanel(false);
                return;
            }
            
            // Check if items has sections property
            if (loadedList.items.sections && typeof loadedList.items.sections === 'object') {
                console.log('📂 Loading from items.sections');
                console.log('📂 Sections data:', loadedList.items.sections);
                setSections({ ...emptySections, ...loadedList.items.sections });
            } 
            // Check if items IS the sections object (has section keys)
            else if (loadedList.items.produce || loadedList.items.meat_seafood || 
                     loadedList.items.dairy || loadedList.items.pantry || 
                     loadedList.items.other) {
                console.log('📂 Loading from items directly (is sections)');
                
                // Remove non-section fields like ingredient_count
                const { ingredient_count, ...sectionsData } = loadedList.items;
                console.log('📂 Extracted sections data:', sectionsData);
                
                // Convert mobile format to web format if needed
                const convertedSections = {};
                Object.keys(sectionsData).forEach(sectionKey => {
                    const sectionData = sectionsData[sectionKey];
                    
                    // Check if this is mobile format (plain array) or web format (object with items)
                    if (Array.isArray(sectionData)) {
                        console.log(`📂 Converting mobile format for section ${sectionKey}`);
                        // Mobile format - convert to web format
                        convertedSections[sectionKey] = {
                            name: emptySections[sectionKey]?.name || sectionKey,
                            items: sectionData.map(item => ({
                                id: item.id || `item-${Date.now()}-${Math.random()}`,
                                name: item.name,
                                checked: item.checked || false,
                                display_text: item.display_text || item.name
                            }))
                        };
                    } else if (sectionData && typeof sectionData === 'object' && sectionData.items) {
                        console.log(`📂 Web format detected for section ${sectionKey}`);
                        // Web format - use as is
                        convertedSections[sectionKey] = sectionData;
                    }
                });
                
                console.log('📂 Converted sections:', convertedSections);
                
                // Merge with empty structure to ensure all sections exist
                setSections({ ...emptySections, ...convertedSections });
            } 
            // Try to interpret as sections anyway
            else {
                console.warn('📂 Unknown list structure, attempting to parse:', loadedList.items);
                
                // Try to merge with empty structure
                setSections({ ...emptySections, ...loadedList.items });
            }
        } else {
            console.warn('📂 No valid list items found, setting empty sections');
            setSections(emptySections);
        }
        
        // Update selected list
        setSelectedListId(loadedList.id);
        
        // Clear unsaved changes since we just loaded from server
        setHasUnsavedChanges(false);
        
        console.log('📂 Load complete - sections state updated');
        
        // Debug: Log final sections state after a small delay to ensure state is updated
        setTimeout(() => {
            console.log('📂 Final sections state after load:', sections);
        }, 100);
    };

    return (
        <div className="grocery-manager-workspace">
            {/* Left Sidebar - List Navigation */}
            <div className="grocery-sidebar">
                <div className="grocery-sidebar-header">
                    <h3>🛒 Grocery Lists</h3>
                    <button 
                        className="create-list-btn"
                        onClick={createNewList}
                        title="Create new grocery list"
                    >
                        ➕
                    </button>
                </div>

                {/* Create New List Form */}
                {isCreatingList && (
                    <div className="create-list-form">
                        <input
                            type="text"
                            value={newListName}
                            onChange={(e) => setNewListName(e.target.value)}
                            placeholder="List name..."
                            className="new-list-input"
                            autoFocus
                            onKeyPress={(e) => {
                                if (e.key === 'Enter') saveNewList();
                                if (e.key === 'Escape') setIsCreatingList(false);
                            }}
                        />
                        <div className="create-list-actions">
                            <button onClick={saveNewList} className="save-btn">✅</button>
                            <button onClick={() => setIsCreatingList(false)} className="cancel-btn">❌</button>
                        </div>
                    </div>
                )}

                {/* Current List Indicator */}
                {currentList && (
                    <div className="current-list-indicator">
                        <span className="current-list-name">📝 {currentList.name}</span>
                        {currentList.isFromMealPlan && (
                            <span className="meal-plan-badge">From Meal Plan</span>
                        )}
                    </div>
                )}

                {/* Folders and Lists */}
                <div className="folders-container">
                    {folders.map(folder => (
                        <div key={folder.id} className="folder">
                            <div 
                                className="folder-header"
                                onClick={() => setSelectedFolder(selectedFolder === folder.id ? null : folder.id)}
                            >
                                <span className="folder-icon">📁</span>
                                <span className="folder-name">{folder.name}</span>
                                <span className="folder-toggle">
                                    {selectedFolder === folder.id ? '📖' : '📁'}
                                </span>
                            </div>
                            
                            {selectedFolder === folder.id && (
                                <div className="folder-lists">
                                    {folder.lists.map(list => (
                                        <div 
                                            key={list.id}
                                            className={`list-item ${selectedListId === list.id ? 'selected' : ''}`}
                                        >
                                            <div 
                                                className="list-content"
                                                onClick={() => loadList(list.id)}
                                            >
                                                <span className="list-name">{list.list_name}</span>
                                                <span className="list-meta">
                                                    {list.item_count || 0} items
                                                </span>
                                            </div>
                                            <button 
                                                className="delete-list-btn"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    deleteList(list.id, list.list_name);
                                                }}
                                                title={`Delete "${list.list_name}"`}
                                            >
                                                🗑️
                                            </button>
                                        </div>
                                    ))}
                                    {folder.lists.length === 0 && (
                                        <div className="empty-folder">No lists yet</div>
                                    )}
                                </div>
                            )}
                        </div>
                    ))}
                </div>

                {/* Loading/Error States */}
                {loading && <div className="sidebar-loading">Loading lists...</div>}
                {error && <div className="sidebar-error">Error: {error}</div>}
            </div>

            {/* Main Canvas - Grocery List Workspace */}
            <div className="grocery-main-content">
                <div className="grocery-workspace-header">
                    <div className="header-title-section">
                        {isEditingName ? (
                            <input
                                type="text"
                                className="list-name-input"
                                value={editedListName}
                                onChange={(e) => setEditedListName(e.target.value)}
                                onBlur={() => {
                                    if (editedListName.trim()) {
                                        if (currentList) {
                                            setCurrentList({ ...currentList, name: editedListName });
                                        }
                                        setIsEditingName(false);
                                    }
                                }}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter') {
                                        if (editedListName.trim()) {
                                            if (currentList) {
                                                setCurrentList({ ...currentList, name: editedListName });
                                            }
                                            setIsEditingName(false);
                                        }
                                    }
                                    if (e.key === 'Escape') {
                                        setEditedListName(currentList?.name || 'New Grocery List');
                                        setIsEditingName(false);
                                    }
                                }}
                                autoFocus
                            />
                        ) : (
                            <h2 
                                className="list-name-title"
                                onClick={() => {
                                    setEditedListName(currentList?.name || 'My Grocery List');
                                    setIsEditingName(true);
                                }}
                                title="Click to edit list name"
                            >
                                {hasUnsavedChanges && <span className="unsaved-dot" title="Unsaved changes">●</span>}
                                {currentList ? currentList.name : 'My Grocery List'}
                            </h2>
                        )}
                    </div>
                    <div className="workspace-controls">
                        <button 
                            className="combine-btn-disabled"
                            disabled
                            title="Combine similar items (coming soon)"
                        >
                            Combine
                        </button>
                        {getHiddenCount() > 0 && (
                            <button 
                                className={`show-hidden-btn ${showHidden ? 'active' : ''}`}
                                onClick={() => setShowHidden(!showHidden)}
                                title={showHidden ? 'Hide items already in pantry' : `Show ${getHiddenCount()} hidden items`}
                            >
                                {showHidden ? 'Hide Pantry Items' : `Show Hidden (${getHiddenCount()})`}
                            </button>
                        )}
                        <button className="export-btn">Export</button>
                        <button 
                            className="load-btn"
                            onClick={() => setShowLoadPanel(true)}
                            title="Load a saved grocery list"
                        >
                            Load
                        </button>
                        <button 
                            className={`save-btn ${hasUnsavedChanges ? 'has-changes' : ''}`}
                            onClick={() => {
                                setSaveListName(currentList?.name || 'My Grocery List');
                                saveCurrentList();
                            }}
                            title={hasUnsavedChanges ? "Save changes to PostgreSQL" : "No changes to save"}
                        >
                            {hasUnsavedChanges ? 'Save' : 'Saved'}
                        </button>
                        <button 
                            className="share-btn"
                            onClick={() => setShowShareModal(true)}
                            disabled={!currentList || !currentList.id}
                            title={currentList?.id ? "Share this list with a household" : "Save list first to share"}
                        >
                            Share
                        </button>
                    </div>
                </div>

                {currentList ? (
                    <DndContext 
                        collisionDetection={closestCenter}
                        onDragStart={handleDragStart}
                        onDragOver={handleDragOver}
                        onDragEnd={handleDragEnd}
                    >
                        {/* Single unified list - no categories */}
                        <div className="unified-grocery-list">
                            {/* Collect all items from all sections into one list */}
                            {(() => {
                                const allItems = [];
                                console.log('🔍 DEBUG: Building allItems list...');
                                console.log('🔍 DEBUG: sectionOrder:', sectionOrder);
                                console.log('🔍 DEBUG: sections:', sections);
                                
                                sectionOrder.forEach((sectionKey) => {
                                    const visibleItems = getVisibleItems(sectionKey);
                                    console.log(`🔍 DEBUG: Section ${sectionKey} has ${visibleItems.length} visible items:`, visibleItems);
                                    visibleItems.forEach(item => {
                                        allItems.push({ ...item, sectionKey });
                                    });
                                });
                                
                                console.log('🔍 DEBUG: Final allItems:', allItems);
                                
                                return (
                                    <SortableContext items={allItems.map(item => item.id)} strategy={verticalListSortingStrategy}>
                                        <div className="unified-items-container">
                                            {allItems.length === 0 && (
                                                <div className="empty-list-hint">
                                                    <p>✨ Click below to add your first item</p>
                                                </div>
                                            )}
                                            
                                            {allItems.map(item => (
                                                <DraggableItem 
                                                    key={item.id}
                                                    item={item}
                                                    sectionKey={item.sectionKey}
                                                    removeItem={removeItem}
                                                    updateItem={updateItem}
                                                    isItemInPantry={isItemInPantry}
                                                    hideItem={hideItem}
                                                    unhideItem={unhideItem}
                                                    isItemHidden={isItemHidden}
                                                    getPantryMatchInfo={getPantryMatchInfo}
                                                    draggedItem={draggedItem}
                                                    combinationPreview={combinationPreview}
                                                    canCombineItems={canCombineItems}
                                                />
                                            ))}
                                            
                                            {/* Notion-style inline adding - ALWAYS VISIBLE */}
                                            <div className="inline-add-container">
                                                {!isAddingInline ? (
                                                    <button 
                                                        className="inline-add-trigger"
                                                        onClick={() => setIsAddingInline(true)}
                                                    >
                                                        <span className="plus-icon">+</span>
                                                        <span className="add-text">Add item...</span>
                                                    </button>
                                                ) : (
                                                    <div className="inline-add-input-container">
                                                        <span className="input-prefix">•</span>
                                                        <input
                                                            type="text"
                                                            className="inline-add-input"
                                                            value={inlineItemName}
                                                            onChange={(e) => setInlineItemName(e.target.value)}
                                                            onKeyDown={(e) => {
                                                                if (e.key === 'Enter') {
                                                                    handleInlineAdd();
                                                                } else if (e.key === 'Escape') {
                                                                    setInlineItemName('');
                                                                    setIsAddingInline(false);
                                                                }
                                                            }}
                                                            onBlur={() => {
                                                                if (!inlineItemName.trim()) {
                                                                    setIsAddingInline(false);
                                                                }
                                                            }}
                                                            placeholder="Type item name..."
                                                            autoFocus
                                                        />
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </SortableContext>
                                );
                            })()}
                        </div>
                    </DndContext>
                ) : (
                    <DndContext 
                        collisionDetection={closestCenter}
                        onDragStart={handleDragStart}
                        onDragOver={handleDragOver}
                        onDragEnd={handleDragEnd}
                    >
                        {/* Empty list - show inline adding */}
                        <div className="unified-grocery-list empty-list">
                            <div className="empty-list-message">
                                <p>✨ Start adding items to your grocery list</p>
                            </div>
                            
                            {/* Notion-style inline adding for empty list */}
                            <div className="unified-items-container">
                                <div 
                                    className={`inline-add-container ${showInlineAdd ? 'show' : ''}`}
                                    onMouseEnter={() => setShowInlineAdd(true)}
                                    onMouseLeave={() => {
                                        if (!isAddingInline) setShowInlineAdd(false);
                                    }}
                                >
                                    {!isAddingInline ? (
                                        <button 
                                            className="inline-add-trigger"
                                            onClick={() => setIsAddingInline(true)}
                                        >
                                            <span className="plus-icon">+</span>
                                            <span className="add-text">Add item...</span>
                                        </button>
                                    ) : (
                                        <div className="inline-add-input-container">
                                            <span className="input-prefix">•</span>
                                            <input
                                                type="text"
                                                className="inline-add-input"
                                                value={inlineItemName}
                                                onChange={(e) => setInlineItemName(e.target.value)}
                                                onKeyDown={(e) => {
                                                    if (e.key === 'Enter') {
                                                        handleInlineAdd();
                                                    } else if (e.key === 'Escape') {
                                                        setInlineItemName('');
                                                        setIsAddingInline(false);
                                                        setShowInlineAdd(false);
                                                    }
                                                }}
                                                onBlur={() => {
                                                    if (!inlineItemName.trim()) {
                                                        setIsAddingInline(false);
                                                        setShowInlineAdd(false);
                                                    }
                                                }}
                                                placeholder="Type item name..."
                                                autoFocus
                                            />
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>
                    </DndContext>
                )}
            </div>
            
            {/* Save List Dialog */}
            {showSaveDialog && (
                <div className="modal-overlay">
                    <div className="modal-content">
                        <h3>💾 Save Grocery List</h3>
                        <p>Enter a name for your grocery list:</p>
                        <input
                            type="text"
                            value={saveListName}
                            onChange={(e) => setSaveListName(e.target.value)}
                            placeholder="e.g. Weekly Shopping, Meal Prep List"
                            autoFocus
                            onKeyDown={(e) => {
                                if (e.key === 'Enter') saveCurrentList();
                                if (e.key === 'Escape') setShowSaveDialog(false);
                            }}
                        />
                        <div className="modal-buttons">
                            <button 
                                className="cancel-btn" 
                                onClick={() => setShowSaveDialog(false)}
                            >
                                Cancel
                            </button>
                            <button 
                                className="save-btn" 
                                onClick={saveCurrentList}
                                disabled={!saveListName.trim()}
                            >
                                💾 Save List
                            </button>
                        </div>
                    </div>
                </div>
            )}
            
            {/* Overwrite Confirmation Dialog */}
            {showOverwriteDialog && duplicateListInfo && (
                <div className="modal-overlay">
                    <div className="modal-content">
                        <h3>⚠️ List Name Already Exists</h3>
                        <p>A grocery list named <strong>"{duplicateListInfo.list_name}"</strong> already exists.</p>
                        <p>Would you like to overwrite it with your current list?</p>
                        <div className="modal-buttons">
                            <button 
                                className="cancel-btn" 
                                onClick={() => {
                                    setShowOverwriteDialog(false);
                                    setDuplicateListInfo(null);
                                    setShowSaveDialog(true);
                                }}
                            >
                                Cancel & Change Name
                            </button>
                            <button 
                                className="danger-btn" 
                                onClick={() => saveCurrentList(true)}
                            >
                                🔄 Overwrite Existing
                            </button>
                        </div>
                    </div>
                </div>
            )}
            
            {/* Load Panel - slides in from right */}
            <LoadGroceryListPanel 
                isOpen={showLoadPanel}
                onClose={() => setShowLoadPanel(false)}
                onLoadList={handleLoadList}
            />

            {/* Share Resource Modal */}
            <ShareResourceModal
                isOpen={showShareModal}
                onClose={() => setShowShareModal(false)}
                resourceType="grocery_list"
                resourceId={currentList?.id}
                resourceName={currentList?.name}
                onShare={handleShare}
            />
        </div>
    );
};

// Draggable Section Component
const DraggableSection = ({ 
    sectionKey, 
    section, 
    addCustomItem, 
    removeItem, 
    updateItem, 
    isItemInPantry, 
    hideItem, 
    unhideItem, 
    isItemHidden, 
    getVisibleItems,
    showHidden,
    getPantryMatchInfo,
    draggedItem,
    combinationPreview,
    canCombineItems
}) => {
    const {
        attributes,
        listeners,
        setNodeRef,
        transform,
        transition,
        isDragging,
    } = useSortable({ 
        id: `section-${sectionKey}`, // Make section IDs unique
        data: {
            type: 'section',
            sectionKey
        }
    });

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.7 : 1,
    };

    // Separate droppable for items (not sections)
    const {
        setNodeRef: setItemDropRef
    } = useDroppable({
        id: `items-${sectionKey}`, // Items drop zone
        data: {
            type: 'section-drop',
            sectionKey
        }
    });

    return (
        <div ref={setNodeRef} style={style} className="grocery-column">
            <div className="column-header">
                <div className="column-title-container">
                    <h4 className="column-title">{section.name}</h4>
                    <div 
                        className="section-drag-handle" 
                        {...attributes} 
                        {...listeners}
                        title="Drag to reorder sections"
                    >
                        ⋮⋮
                    </div>
                </div>
                <span className="item-count">({section.items.length})</span>
                <button 
                    className="add-item-btn"
                    onClick={() => {
                        const itemName = prompt(`Add item to ${section.name}:`);
                        if (itemName) addCustomItem(sectionKey, itemName);
                    }}
                >
                    ➕
                </button>
            </div>
            
            <SortableContext items={section.items.map(item => item.id)} strategy={verticalListSortingStrategy}>
                <div ref={setItemDropRef} className="column-items">
                    {getVisibleItems(sectionKey).map(item => (
                        <DraggableItem 
                            key={item.id} 
                            item={item} 
                            sectionKey={sectionKey}
                            removeItem={removeItem}
                            updateItem={updateItem}
                            isItemInPantry={isItemInPantry}
                            hideItem={hideItem}
                            unhideItem={unhideItem}
                            isItemHidden={isItemHidden}
                            showHidden={showHidden}
                            getPantryMatchInfo={getPantryMatchInfo}
                            draggedItem={draggedItem}
                            combinationPreview={combinationPreview}
                            canCombineItems={canCombineItems}
                        />
                    ))}
                    
                    {getVisibleItems(sectionKey).length === 0 && (
                        <div className="empty-column">
                            <p>{showHidden && section.items.length > 0 ? 'All items are hidden (in pantry)' : 'No items yet'}</p>
                            <button 
                                className="add-first-item"
                                onClick={() => {
                                    const itemName = prompt(`Add first item to ${section.name}:`);
                                    if (itemName) addCustomItem(sectionKey, itemName);
                                }}
                            >
                                ➕ Add Item
                            </button>
                        </div>
                    )}
                </div>
            </SortableContext>
        </div>
    );
};

// Draggable Item Component  
const DraggableItem = ({ 
    item, 
    sectionKey, 
    removeItem, 
    updateItem, 
    isItemInPantry, 
    hideItem, 
    unhideItem, 
    isItemHidden,
    showHidden,
    getPantryMatchInfo,
    draggedItem,
    combinationPreview,
    canCombineItems
}) => {
    // Inline editing state
    const [isEditing, setIsEditing] = useState(false);
    const [tempValue, setTempValue] = useState(item.name);

    // Pantry status
    const pantryInfo = getPantryMatchInfo(item.name);
    const inPantry = pantryInfo.inPantry;
    const isHidden = isItemHidden(sectionKey, item.id);
    
    // Combination status
    const isCombinable = draggedItem && draggedItem.id !== item.id && canCombineItems(draggedItem, item);
    const isCombinationTarget = combinationPreview?.targetItemId === item.id;
    const showCombinationPreview = isCombinable && isCombinationTarget;

    const {
        attributes,
        listeners,
        setNodeRef,
        transform,
        transition,
        isDragging,
    } = useSortable({ 
        id: item.id,
        data: {
            type: 'item',
            sectionKey,
            item
        }
    });

    const style = {
        transform: CSS.Transform.toString(transform),
        transition,
        opacity: isDragging ? 0.7 : 1,
        zIndex: isDragging ? 1000 : 1,
    };

    // Handle edit start
    const startEdit = () => {
        if (isDragging) return; // Don't edit while dragging
        setTempValue(item.name);
        setIsEditing(true);
    };

    // Handle edit save
    const saveEdit = () => {
        if (tempValue.trim() && tempValue.trim() !== item.name) {
            updateItem(sectionKey, item.id, tempValue.trim());
        }
        setIsEditing(false);
    };

    // Handle edit cancel
    const cancelEdit = () => {
        setTempValue(item.name);
        setIsEditing(false);
    };

    // Handle key presses
    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            saveEdit();
        } else if (e.key === 'Escape') {
            cancelEdit();
        }
    };

    return (
        <div 
            ref={setNodeRef} 
            style={style} 
            className={`grocery-item-card ${isDragging ? 'dragging' : ''} ${isEditing ? 'editing' : ''} ${item.isConsolidated ? 'consolidated' : ''} ${inPantry ? 'in-pantry' : ''} ${isHidden ? 'hidden-item' : ''} ${isCombinable ? 'combinable' : ''} ${isCombinationTarget ? 'combination-target' : ''}`}
        >
            {/* Drag handle on the left */}
            <div 
                className="drag-handle"
                {...attributes} 
                {...listeners}
                title="Drag to reorder"
            >
                ⋮⋮
            </div>
            
            <div className="item-content">
                {isEditing ? (
                    <input
                        type="text"
                        value={tempValue}
                        onChange={(e) => setTempValue(e.target.value)}
                        onBlur={saveEdit}
                        onKeyDown={handleKeyDown}
                        className="item-name-input"
                        autoFocus
                        onFocus={(e) => e.target.select()} // Auto-select text
                    />
                ) : (
                    <span 
                        className="item-name" 
                        onClick={startEdit}
                        title="Click to edit"
                    >
                        {item.name}
                    </span>
                )}
                
                {/* Pantry status moved here - under the sources */}
                {inPantry && (
                    <div className="pantry-status-inline">
                        <span 
                            className={`pantry-badge ${pantryInfo.isCompound ? 'compound' : 'single'}`} 
                            title={pantryInfo.displayText}
                        >
                            {pantryInfo.isCompound ? '🧩' : '🥫'} {pantryInfo.isCompound ? 'All Parts' : 'In Pantry'}
                        </span>
                        {isHidden ? (
                            <button 
                                className="unhide-btn"
                                onClick={() => unhideItem(sectionKey, item.id)}
                                title="Add back to shopping list"
                            >
                                🔄 Add Back
                            </button>
                        ) : (
                            <button 
                                className="hide-btn"
                                onClick={() => hideItem(sectionKey, item.id)}
                                title="Hide - already have this"
                            >
                                ✅ Have It
                            </button>
                        )}
                    </div>
                )}
                
                {/* Combination preview during drag */}
                {showCombinationPreview && (
                    <div className={`combination-preview ${combinationPreview.confidence === 'SMART' ? 'smart' : ''}`}>
                        <span className="preview-text">
                            {combinationPreview.confidence === 'SMART' ? '🤝' : '🔄'} Combine → {combinationPreview.previewText}
                        </span>
                    </div>
                )}
            </div>
            
            {/* Trash button on the right */}
            <button 
                className="remove-btn"
                onClick={() => removeItem(sectionKey, item.id)}
                title="Remove from list"
            >
                ×
            </button>
        </div>
    );
};

export default GroceryManagerWorkspace;
