import React, { useState, useEffect } from 'react';
import { DndContext, closestCenter, DragOverlay } from '@dnd-kit/core';
import { useAuth } from '../contexts/AuthContext';
import SidebarContainer from '../components/SidebarContainer';
import ChatInterface from '../components/ChatInterface';
import RecipeListView from '../components/RecipeListView';
import ViewSwitcher from '../components/ViewSwitcher';
import RecipeGalleryView from '../components/RecipeGalleryView';
import RecipeTableView from '../components/RecipeTableView';
import SearchFilterBar from '../components/SearchFilterBar';
import FriendsView from '../components/FriendsView';
import CommunityBrowser from '../components/CommunityBrowserNew';
import RecipeEditModal from '../components/RecipeEditModal';
import ImportRecipeModal from '../components/ImportRecipeModal';
import PhotoImportModal from '../components/PhotoImportModal';
import RecipePanel from '../components/RecipePanel';
import AdminDashboard from '../components/AdminDashboard';
import AdminRecipeOverlay from '../components/AdminRecipeOverlay';
import GroceryManagerWorkspace from '../components/GroceryManagerWorkspace';
import { ToastProvider } from '../components/ToastContainer';
import './MainApp.css';
import './ActivityFeedView.css';
import SessionMemoryManager from '../utils/SessionMemoryManager';
import { usePantry } from '../hooks/usePantry';
import { useMealPlanner, useDragAndDrop, useSidebar } from '../hooks';
import * as api from '../utils/api';

// 🆕 Whiteboard Components
import HouseholdSelector from './HouseholdSelector';
import WhiteboardNavigator from './WhiteboardNavigator';
import WhiteboardApp from './WhiteboardApp';

// 🆕 Activity Feed Components
import ActivityFeed from '../components/ActivityFeed';

const MainApp = () => {
  console.log('🚀 MainApp component loaded - COOKBOOK-FIRST VERSION 2025-08-22');

  // --- Authentication ---
  const { user: currentUser, loading: authLoading, logout } = useAuth();

  // --- Enhanced Session Memory with Backend Coordination ---
  const [sessionMemory] = useState(() => new SessionMemoryManager());

  // --- Pantry Integration ---
  const { pantryItems, getPantryForAPI, hasItems: hasPantryItems } = usePantry();

  // --- Custom Hooks ---
  const mealPlannerHook = useMealPlanner();
  const sidebarHook = useSidebar();

  // --- Cookbook State ---
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [customCategories, setCustomCategories] = useState([]);
  const [recipeCounts, setRecipeCounts] = useState({});
  const [showChat, setShowChat] = useState(false);
  const [editingRecipe, setEditingRecipe] = useState(null);
  const [viewingRecipe, setViewingRecipe] = useState(null);
  const [showRecipeDetail, setShowRecipeDetail] = useState(false);

  // --- Admin State ---
  const [isAdmin, setIsAdmin] = useState(false);
  const [adminMode, setAdminMode] = useState(false);
  const [showAdminDashboard, setShowAdminDashboard] = useState(false);

  // --- View State (Multi-view system) ---
  const [currentView, setCurrentView] = useState(() => {
    return localStorage.getItem('preferredRecipeView') || 'gallery';
  });
  const [showPhotoImport, setShowPhotoImport] = useState(false);

  // 🆕 Whiteboard State
  const [selectedHouseholdId, setSelectedHouseholdId] = useState(null);
  const [selectedWhiteboardId, setSelectedWhiteboardId] = useState(null);

  // --- Drag and Drop State ---
  const [activeRecipe, setActiveRecipe] = useState(null);

  // --- Search and Filter State ---
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilters, setActiveFilters] = useState({
    difficulty: [],
    time: [],
    mealType: []
  });

  // --- Pagination State ---
  const [currentPage, setCurrentPage] = useState(1);
  const recipesPerPage = 50;

  // Save preferred view to localStorage
  useEffect(() => {
    localStorage.setItem('preferredRecipeView', currentView);
  }, [currentView]);

  // Reset to page 1 when filters or search changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, activeFilters, selectedCategory]);

    // --- Meal Planner Mode ---
  const [mealPlannerMode, setMealPlannerMode] = useState('traditional'); // 'traditional' or 'notion'
  const [activeView, setActiveView] = useState('cookbook'); // 'cookbook', 'grocery-manager', 'notion-planner'
  const [mealPlanRecipeIds, setMealPlanRecipeIds] = useState([]); // Recipe IDs from meal planner

  // Recipe container state
  const [containerRecipes, setContainerRecipes] = useState([]);

  // View state management

  // Load recipes on component mount
  useEffect(() => {
    console.log('🔄 MainApp useEffect triggered - loading recipes');
    // Load real data from API
    loadRecipes();
  }, []);

  // Calculate recipe counts when recipes change
  useEffect(() => {
    console.log('📊 Recipes state changed. New count:', recipes.length);
    console.log('📊 First few recipes in state:', recipes.slice(0, 2));
    calculateRecipeCounts();
  }, [recipes]);

  const loadRecipes = async (category = 'all') => {
    setLoading(true);
    console.log(`🔄 Starting recipe load process for category: ${category}...`);
    
    // V2 Migration: Check if user is authenticated
    if (!currentUser?.id) {
      console.warn('⚠️ No user ID available - user may not be logged in');
      setRecipes([]);
      setLoading(false);
      return;
    }
    
    try {
      console.log(`🍽️ Loading recipes for user ${currentUser.id} from v2 API...`);
      
      // V2 API: Use getUserRecipesV2 with user ID
      const response = await api.getUserRecipesV2(currentUser.id, category);
      console.log('📊 V2 User recipes response:', response);
      
      // Check for admin access
      if (response && response.admin_access) {
        console.log('🔧 Admin access granted - showing ALL recipes for curation');
        console.log('👤 Note: Regular users only see their own recipes');
        setIsAdmin(true);
      } else {
        console.log('👤 Regular user - showing only YOUR recipes');
        setIsAdmin(false);
      }
      
      // Handle v2 response structure
      let recipes = [];
      if (response && response.success) {
        // V2 response structure: { success: true, data: { items: [...], pagination: {...} } }
        if (response.data?.items) {
          recipes = response.data.items;
          console.log(`✅ V2 API: Found ${recipes.length} recipes for category '${category}'`);
          console.log('📊 Pagination info:', response.data.pagination);
        } else if (Array.isArray(response.data)) {
          // Fallback for direct array response
          recipes = response.data;
          console.log(`✅ V2 API: Found ${recipes.length} recipes (direct array)`);
        }
        
        console.log('📝 Recipe types:', recipes.slice(0, 3).map(r => r.recipe_type || 'unknown'));
        
        if (response.admin_access) {
          console.log('🔧 Admin loaded ALL database recipes for curation');
        }
      } else if (response && Array.isArray(response)) {
        // Fallback for direct array response
        recipes = response;
        console.log('✅ Response itself is array:', recipes.length);
      } else {
        console.log('⚠️ Unexpected v2 response structure:', response);
      }
      
      if (recipes.length > 0) {
        console.log(`✅ Setting ${recipes.length} recipes from v2 API`);
        console.log('📋 First recipe sample:', recipes[0]);
        setRecipes(recipes);
      } else {
        console.log('ℹ️ No recipes found - starting with empty cookbook');
        setRecipes([]);
      }
    } catch (error) {
      console.error('❌ Error loading recipes from v2 API:', error);
      console.error('❌ Error details:', error.message, error.stack);
      console.log('ℹ️ Starting with empty cookbook due to error');
      setRecipes([]);
    } finally {
      setLoading(false);
    }
  };

  const tryDirectAPICall = async () => {
    try {
      console.log('🔄 Trying direct API call...');
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/search?q=recipe&limit=1000`, {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` })
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Direct API call successful:', data);
        if (data.recipes && Array.isArray(data.recipes)) {
          console.log(`🎯 Setting ${data.recipes.length} recipes from direct call`);
          setRecipes(data.recipes);
          return;
        }
      } else {
        console.log('❌ Direct API call failed:', response.status, response.statusText);
      }
    } catch (error) {
      console.error('❌ Direct API call error:', error);
    }
    
    // If all API calls fail, start with empty cookbook
    console.log('ℹ️ All API calls failed, starting with empty cookbook');
    setRecipes([]);
  };

  const calculateRecipeCounts = () => {
    const counts = {
      all: recipes.length,
      'recent-imports': 0,  // Add recent imports category
      breakfast: 0,
      lunch: 0,
      dinner: 0,
      desserts: 0,
      'one-pot': 0,
      quick: 0,
      favorites: 0
    };

    recipes.forEach(recipe => {
      // Count imported recipes (those with category 'imported' or marked as imported)
      if (recipe.category === 'imported' || recipe.is_imported || recipe.imported_at) {
        counts['recent-imports']++;
      }

      // Count by meal role
      if (recipe.meal_role === 'breakfast') counts.breakfast++;
      else if (recipe.meal_role === 'lunch') counts.lunch++;
      else if (recipe.meal_role === 'dinner') counts.dinner++;
      else if (recipe.meal_role === 'dessert') counts.desserts++;

      // Count by characteristics
      if (recipe.is_one_pot) counts['one-pot']++;
      if (recipe.time_min && recipe.time_min <= 30) counts.quick++;
      if (recipe.is_favorite) counts.favorites++;
    });

    setRecipeCounts(counts);
  };

  const getFilteredRecipes = () => {
    let filtered = recipes;

    // First filter by category (from sidebar)
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(recipe => {
        switch (selectedCategory) {
          case 'recent-imports':
            return recipe.category === 'imported' || recipe.is_imported || recipe.imported_at;
          case 'breakfast':
          case 'lunch':
          case 'dinner':
            return recipe.meal_role === selectedCategory;
          case 'desserts':
            return recipe.meal_role === 'dessert';
          case 'one-pot':
            return recipe.is_one_pot === true;
          case 'quick':
            return recipe.time_min && recipe.time_min <= 30;
          case 'favorites':
            return recipe.is_favorite === true;
          default:
            return true;
        }
      });
    }

    // Then apply search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(recipe => {
        const title = (recipe.title || '').toLowerCase();
        const ingredients = (recipe.ingredients || '').toLowerCase();
        const tags = (recipe.tags || []).join(' ').toLowerCase();
        const description = (recipe.description || '').toLowerCase();
        
        return title.includes(query) || 
               ingredients.includes(query) || 
               tags.includes(query) ||
               description.includes(query);
      });
    }

    // Then apply active filters
    if (activeFilters.difficulty.length > 0) {
      filtered = filtered.filter(recipe => {
        const difficulty = (recipe.difficulty || '').toLowerCase();
        return activeFilters.difficulty.includes(difficulty);
      });
    }

    if (activeFilters.time.length > 0) {
      filtered = filtered.filter(recipe => {
        const time = parseInt(recipe.time_min || recipe.cooking_time || recipe.prep_time || 0);
        
        return activeFilters.time.some(timeFilter => {
          if (timeFilter === 'quick') return time > 0 && time < 30;
          if (timeFilter === 'medium') return time >= 30 && time <= 60;
          if (timeFilter === 'long') return time > 60;
          return false;
        });
      });
    }

    if (activeFilters.mealType.length > 0) {
      filtered = filtered.filter(recipe => {
        const mealRole = (recipe.meal_role || recipe.category || '').toLowerCase();
        return activeFilters.mealType.includes(mealRole);
      });
    }

    return filtered;
  };

  const getPaginatedRecipes = () => {
    const filtered = getFilteredRecipes();
    const startIndex = (currentPage - 1) * recipesPerPage;
    const endIndex = startIndex + recipesPerPage;
    return filtered.slice(startIndex, endIndex);
  };

  const getTotalPages = () => {
    const filtered = getFilteredRecipes();
    return Math.ceil(filtered.length / recipesPerPage);
  };

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSearch = (query) => {
    setSearchQuery(query);
  };

  const handleFilterChange = (filters) => {
    setActiveFilters(filters);
  };

  const handleCategorySelect = (categoryId) => {
    console.log(`📂 Category selected: ${categoryId}`);
    setSelectedCategory(categoryId);
    // Note: We don't reload recipes - just filter the existing ones client-side
    // This keeps the sidebar counts accurate across all categories
  };

  const handleAddCategory = (newCategory) => {
    setCustomCategories(prev => [...prev, newCategory]);
  };

  const handleToggleChat = () => {
    setShowChat(!showChat);
  };

  const handleRecipeClick = (recipe) => {
    console.log('Recipe clicked:', recipe.title);
    setViewingRecipe(recipe);
    setShowRecipeDetail(true);
  };

  const handleCloseRecipeDetail = () => {
    setShowRecipeDetail(false);
    setViewingRecipe(null);
  };

  const handleRecipeEdit = async (updatedRecipe) => {
    console.log('💾 Handling recipe edit:', updatedRecipe);
    
    try {
      // For now, just update local state - we can add API call later
      console.log('📝 Updating local recipe state...');
      
      // Update recipes list
      setRecipes(prev => prev.map(r => 
        r.id === updatedRecipe.id ? updatedRecipe : r
      ));
      
      // Update viewing recipe if it's the same recipe being edited
      if (viewingRecipe && viewingRecipe.id === updatedRecipe.id) {
        setViewingRecipe(updatedRecipe);
        console.log('🎨 Updated viewing recipe');
      }
      
      console.log('✅ Recipe updated successfully');
      
      // TODO: Add API call to persist changes
      // await api.updateRecipe(updatedRecipe);
      
    } catch (error) {
      console.error('❌ Error saving recipe:', error);
      // TODO: Show error message to user
    }
  };

  const handleSaveRecipe = async (updatedRecipe) => {
    try {
      // Call API to update recipe (we'll need to add this endpoint)
      console.log('Saving recipe:', updatedRecipe);
      
      // Update local recipes state
      setRecipes(prev => prev.map(r => 
        r.id === updatedRecipe.id ? updatedRecipe : r
      ));
      
      // Update viewing recipe if it's the same recipe being edited
      if (viewingRecipe && viewingRecipe.id === updatedRecipe.id) {
        setViewingRecipe(updatedRecipe);
      }
      
      setEditingRecipe(null);
    } catch (error) {
      console.error('Error saving recipe:', error);
      throw error;
    }
  };

  // Handle adding recipe to container
  const handleRecipeAddedToContainer = (recipe) => {
    setContainerRecipes(prev => {
      const exists = prev.find(r => r.id === recipe.id);
      if (!exists) {
        return [...prev, recipe];
      }
      return prev;
    });
  };

  // Handle grocery list activation from navigation
  const handleShowGroceryList = (recipeIds = []) => {
    // Store recipe IDs from meal planner if provided
    if (recipeIds && recipeIds.length > 0) {
      setMealPlanRecipeIds(recipeIds);
    }
    
    // Toggle functionality - if already showing grocery manager, close it
    if (activeView === 'grocery-manager') {
      setActiveView('cookbook'); // Return to cookbook view
      setMealPlanRecipeIds([]); // Clear recipe IDs
    } else {
      setActiveView('grocery-manager');
      setShowChat(false); // Close chat if open
      sidebarHook.closeAllSidebars(); // Close other sidebars
    }
  };

  // Handle recipe import functionality
  const handleImportRecipe = async (importResult) => {
    console.log('Recipe imported successfully:', importResult);
    
    // V2 API structure validation: fail fast if wrong structure
    if (!importResult.success || !importResult.data?.recipe) {
      console.error('❌ Invalid v2 import response structure:', importResult);
      alert('Import failed: Invalid response from server. Please try again.');
      return;
    }
    
    // V2 API structure: { success: true, data: { recipe, recipe_id, confidence, ... } }
    const recipeData = importResult.data.recipe;
    const recipeId = importResult.data.recipe_id;
    
    console.log('🔍 Raw recipe data:', recipeData);
    console.log('🔍 Recipe ID:', recipeId);
    
    // Instead of reloading all recipes, add the new recipe to the existing list
    if (recipeData) {
      // Normalize ingredients to be searchable
      let normalizedIngredients = recipeData.ingredients || [];
      console.log('🔍 Raw ingredients:', normalizedIngredients);
      
      // Convert array of ingredients to a searchable string format
      // This ensures compatibility with existing search logic
      const ingredientsString = Array.isArray(normalizedIngredients) 
        ? normalizedIngredients.map(ing => {
            if (typeof ing === 'string') return ing;
            if (typeof ing === 'object') return ing.name || ing.ingredient || ing.text || String(ing);
            return String(ing);
          }).join(', ')
        : String(normalizedIngredients);
      
      console.log('🔍 Normalized ingredients string:', ingredientsString);
      
      // Parse time to get time_min for compatibility
      const parseTimeToMinutes = (timeStr) => {
        // Handle null, undefined, or non-string values
        if (!timeStr || typeof timeStr !== 'string') return null;
        const match = timeStr.match(/(\d+)/);
        return match ? parseInt(match[1]) : null;
      };
      
      // Map imported category to proper meal_role
      const mapCategoryToMealRole = (category) => {
        if (!category) return 'dinner';
        const cat = category.toLowerCase();
        if (cat.includes('breakfast') || cat.includes('brunch')) return 'breakfast';
        if (cat.includes('lunch') || cat.includes('salad')) return 'lunch';
        if (cat.includes('dessert') || cat.includes('sweet') || cat.includes('cake') || cat.includes('cookie')) return 'dessert';
        if (cat.includes('snack') || cat.includes('appetizer')) return 'snack';
        if (cat.includes('side')) return 'side';
        // Default main dishes to dinner
        return 'dinner';
      };
      
      const prepTimeMin = parseTimeToMinutes(recipeData.prep_time);
      const cookTimeMin = parseTimeToMinutes(recipeData.cook_time);
      const totalTimeMin = (prepTimeMin || 0) + (cookTimeMin || 0) || null;
      
      const newRecipe = {
        id: recipeId, // Use extracted recipe ID from v2 response
        title: recipeData.title || 'Imported Recipe',
        description: recipeData.description || '',
        ingredients: ingredientsString, // Store as string for search compatibility
        instructions: recipeData.instructions || [],
        prep_time: recipeData.prep_time || '',
        cook_time: recipeData.cook_time || '',
        time_min: totalTimeMin, // Add time_min field that UI expects
        servings: recipeData.servings || '',
        category: recipeData.category || 'imported', // Use backend category or default to 'imported'
        meal_role: mapCategoryToMealRole(recipeData.category), // Proper meal role mapping
        source_url: recipeData.source_url || '',
        confidence: importResult.data?.confidence || importResult.confidence || 0.0,
        is_easy: totalTimeMin && totalTimeMin <= 30, // Mark as easy if quick
        pantryOverlap: 0, // Default pantry overlap
        // Add import tracking metadata
        imported_at: new Date().toISOString(),
        is_imported: true, // Additional import marker
        created_at: new Date().toISOString(),
        date_added: new Date().toISOString()
      };
      
      console.log('🔍 Final normalized recipe:', newRecipe);
      
      // If recipe_id is null, the backend didn't save it - we need to save it now
      if (!recipeId) {
        console.log('💾 Recipe not saved by backend (needs_review), saving now...');
        
        try {
          // Save the recipe using v2 create endpoint
          const saveResult = await api.createRecipeV2({
            ...recipeData,
            user_id: currentUser?.id,
            category: recipeData.category || 'imported',
            // Convert arrays back to proper format if needed
            ingredients: Array.isArray(recipeData.ingredients) 
              ? recipeData.ingredients 
              : ingredientsString,
            instructions: Array.isArray(recipeData.instructions)
              ? recipeData.instructions
              : []
          });
          
          console.log('✅ Recipe saved successfully:', saveResult);
          
          // Show success message
          if (saveResult.success && saveResult.data) {
            alert(`Recipe "${recipeData.title}" imported and saved successfully!`);
          }
        } catch (error) {
          console.error('❌ Error saving imported recipe:', error);
          alert(`Recipe extracted but failed to save: ${error.message}`);
        }
      }
      
      // Reload all recipes from backend to get the fresh one with correct ID
      console.log('📥 Reloading all recipes to include newly imported recipe...');
      loadRecipes(selectedCategory); // Reload current category to show the new recipe
      
    } else {
      // Fallback: refresh recipe list only if we couldn't get the recipe data
      console.log('⚠️ Import result missing recipe data, refreshing full list');
      loadRecipes();
    }
  };

  const handleCloseImportModal = () => {
    // This function is no longer needed but keeping for any legacy references
  };

  // Handle photo import
  const handlePhotoImport = async (formData) => {
    try {
      console.log('📸 Starting photo import...');
      const response = await api.importRecipeFromPhoto(formData);
      
      // V2 response validation
      if (!response.success || !response.data?.recipe) {
        console.error('❌ Invalid v2 photo import response:', response);
        throw new Error(response.error || 'Photo import failed: Invalid response structure');
      }
      
      console.log('✅ Photo import successful:', response.data);
      
      // V2 structure: response.data.recipe
      const newRecipe = response.data.recipe;
      const recipeId = response.data.recipe_id || newRecipe.id;
      
      console.log(`✅ Imported recipe: "${newRecipe.title}" (ID: ${recipeId})`);
      
      // Show success message
      alert(`Recipe "${newRecipe.title}" imported successfully!`);
      
      // Refresh recipes to get latest from backend
      loadRecipes(selectedCategory);
      
      return response;
    } catch (error) {
      console.error('❌ Photo import error:', error);
      alert(`Failed to import photo: ${error.message}`);
      throw error;
    }
  };

  // Handle recipe deletion
  const handleDeleteRecipe = async (recipeId) => {
    try {
      // Try to get user ID from currentUser first, then from auth API
      let userId = currentUser?.id;
      
      if (!userId) {
        // Fetch current user from V2 auth API
        try {
          const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:5000'}/api/v2/auth/me`, {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('authToken')}`
            }
          });
          if (response.ok) {
            const result = await response.json();
            // V2 response format: { success, data: { user } }
            if (result.success && result.data) {
              userId = result.data.user.id;
            }
          }
        } catch (error) {
          console.error('Failed to get user ID:', error);
        }
      }
      
      if (!userId) {
        alert('Unable to delete recipe: Not authenticated');
        return;
      }
      
      await api.deleteRecipeV2(recipeId, userId);
      
      // Remove from local state
      setRecipes(prev => prev.filter(r => r.id !== recipeId));
      
      console.log(`✅ Recipe ${recipeId} deleted successfully`);
    } catch (error) {
      console.error('❌ Error deleting recipe:', error);
      alert('Failed to delete recipe. Please try again.');
    }
  };

  // Drag and drop with meal planner and container integration (simplified - no meal types)
  const dragAndDropHook = useDragAndDrop(
    (day, recipe) => {
      return mealPlannerHook.addRecipeToMeal(day, recipe);
    },
    handleRecipeAddedToContainer,
    (sourceDay, sourceIndex, targetDay, recipe) => {
      return mealPlannerHook.moveRecipe(sourceDay, sourceIndex, targetDay, recipe);
    }
  );

  // Show loading while checking authentication
  if (authLoading) {
    return (
      <div className="app-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <div style={{ textAlign: 'center' }}>
          <div className="spinner" style={{ margin: '0 auto 20px' }}></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  console.log('👤 Current user:', currentUser);

  // Drag handlers
  const handleDragStart = (event) => {
    const recipe = event.active.data.current?.recipe;
    if (recipe) {
      setActiveRecipe(recipe);
    }
    dragAndDropHook.handleDragStart(event);
  };

  const handleDragEnd = (event) => {
    setActiveRecipe(null);
    dragAndDropHook.handleDragEnd(event);
  };

  const handleDragCancel = () => {
    setActiveRecipe(null);
    dragAndDropHook.handleDragCancel();
  };

  return (
    <DndContext
      sensors={dragAndDropHook.sensors}
      collisionDetection={closestCenter}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onDragCancel={handleDragCancel}
    >
      <div className={`app-container cookbook-first ${showRecipeDetail ? 'recipe-panel-open' : ''}`}>
        {/* Navigation Sidebar - Left Side */}
        <ToastProvider>
          <SidebarContainer
            showMealPlanner={sidebarHook.isMealPlannerVisible}
            onToggleMealPlanner={sidebarHook.toggleMealPlanner}
            showPantry={sidebarHook.isPantryVisible}
            onTogglePantry={sidebarHook.togglePantry}
            isPantryExpanded={sidebarHook.isPantryExpanded}
            isMealPlannerExpanded={sidebarHook.isMealPlannerExpanded}
            onTogglePantryExpand={sidebarHook.togglePantryExpand}
            onToggleMealPlannerExpand={sidebarHook.toggleMealPlannerExpand}
            mealPlan={mealPlannerHook.mealPlan}
            setMealPlan={mealPlannerHook.setMealPlan}
            containerRecipes={containerRecipes}
            setContainerRecipes={setContainerRecipes}
            onShowGroceryList={handleShowGroceryList}
            showChat={showChat}
            onToggleChat={handleToggleChat}
            // Pass recipe category props to the navigation
          selectedCategory={selectedCategory}
          onCategorySelect={handleCategorySelect}
          recipeCounts={recipeCounts}
          customCategories={customCategories}
          onAddCategory={handleAddCategory}
          onRefreshRecipes={loadRecipes}
          // Admin props
          isAdmin={isAdmin}
          onShowAdminDashboard={() => setShowAdminDashboard(true)}
          onFeatureSelect={(feature, data) => {
            console.log('Feature selected:', feature, data);
            if (feature === 'cookbook') {
              setActiveView('cookbook');
              setShowChat(false);
              sidebarHook.closeAllSidebars();
            } else if (feature === 'grocery-lists') {
              setActiveView('grocery-manager');
              setShowChat(false);
              sidebarHook.closeAllSidebars();
            } else if (feature === 'notion-planner') {
              setActiveView('notion-planner');
              setShowChat(false);
              sidebarHook.closeAllSidebars();
            } else if (feature === 'friends') {
              setActiveView('friends');
              setShowChat(false);
              sidebarHook.closeAllSidebars();
            } else if (feature === 'community') {
              setActiveView('community');
              setShowChat(false);
              sidebarHook.closeAllSidebars();
            } else if (feature === 'households') {
              setActiveView('households');
              setShowChat(false);
              sidebarHook.closeAllSidebars();
              
              // If household ID provided, show gallery for that household
              if (data?.householdId) {
                setSelectedHouseholdId(data.householdId);
                // Don't auto-select whiteboard - show gallery instead
                setSelectedWhiteboardId(null);
              } else {
                // Reset - show household selector
                setSelectedHouseholdId(null);
                setSelectedWhiteboardId(null);
              }
            } else if (feature === 'import') {
              setActiveView('import');
              setShowChat(false);
              sidebarHook.closeAllSidebars();
            } else if (feature === 'photo-import') {
              setShowPhotoImport(true);
            }
          }}
        />
        </ToastProvider>

        {/* Main Content Area */}
        <div className="main-content">
          {/* Admin controls moved to sidebar navigation */}

          {/* Main Content - Conditional View */}
          {activeView === 'community' && (
            <div className="community-home-view">
              {/* Activity Feed Section */}
              <div className="activity-feed-section">
                <h2 className="section-title">🔔 Recent Activity</h2>
                <ActivityFeed maxHeight="500px" />
              </div>
              
              {/* Community Recipes Section */}
              <div className="community-recipes-section">
                <h2 className="section-title">🌟 Community Recipes</h2>
                <CommunityBrowser />
              </div>
            </div>
          )}

          {activeView === 'friends' && (
            <FriendsView />
          )}

          {activeView === 'households' && (
            <>
              {!selectedHouseholdId ? (
                <HouseholdSelector 
                  onSelectHousehold={(householdId) => setSelectedHouseholdId(householdId)}
                />
              ) : !selectedWhiteboardId ? (
                <WhiteboardNavigator 
                  householdId={selectedHouseholdId}
                  onBack={() => setSelectedHouseholdId(null)}
                  onSelectWhiteboard={(whiteboardId) => setSelectedWhiteboardId(whiteboardId)}
                />
              ) : (
                <WhiteboardApp 
                  householdId={selectedHouseholdId}
                  whiteboardId={selectedWhiteboardId}
                  onBack={() => setSelectedWhiteboardId(null)}
                />
              )}
            </>
          )}

          {activeView === 'cookbook' && (
            <>
              {/* View Switcher */}
              <ViewSwitcher 
                currentView={currentView} 
                onViewChange={setCurrentView} 
              />

              {/* Search and Filter Bar */}
              <SearchFilterBar
                onSearch={handleSearch}
                onFilterChange={handleFilterChange}
                totalRecipes={getFilteredRecipes().length}
                currentPage={currentPage}
                totalPages={getTotalPages()}
                onPageChange={handlePageChange}
              />

              {/* Render view based on selection */}
              {currentView === 'gallery' && (
                <RecipeGalleryView
                  recipes={getPaginatedRecipes()}
                  onRecipeClick={handleRecipeClick}
                />
              )}

              {currentView === 'table' && (
                <RecipeTableView
                  recipes={getPaginatedRecipes()}
                  onRecipeClick={handleRecipeClick}
                  onRecipeEdit={handleRecipeEdit}
                  onRecipeDelete={handleDeleteRecipe}
                />
              )}
            </>
          )}

          {activeView === 'import' && (
            <div className="import-recipe-view">
              <ImportRecipeModal
                isOpen={true}
                onClose={() => setActiveView('cookbook')}
                onImport={(result) => {
                  handleImportRecipe(result);
                  setActiveView('cookbook');
                }}
                isInlineView={true}
              />
            </div>
          )}

          {activeView === 'grocery-manager' && (
            <GroceryManagerWorkspace
              mealPlanRecipes={mealPlanRecipeIds.length > 0 
                ? mealPlanRecipeIds 
                : mealPlannerHook.getAllMealPlanRecipes().map(recipe => recipe.id).filter(Boolean)
              }
            />
          )}

          {/* Chat Panel - Toggle Overlay */}
          {showChat && (
            <div className="chat-overlay">
              <div className="chat-panel">
                <div className="chat-header">
                  <h3>🤖 AI Cooking Assistant</h3>
                  <button 
                    className="close-chat-btn"
                    onClick={() => setShowChat(false)}
                  >
                    ×
                  </button>
                </div>
                <ChatInterface
                  sessionMemory={sessionMemory}
                  getPantryForAPI={getPantryForAPI}
                  hasPantryItems={hasPantryItems}
                  pantryItems={pantryItems}
                  setShowPantry={sidebarHook.setPantryVisible}
                  isCompact={true}
                  isExtraCompact={false}
                  onAddToMealPlan={(day, mealType, recipe) => {
                    // Show meal planner if not visible
                    if (!sidebarHook.isMealPlannerVisible) {
                      sidebarHook.toggleMealPlanner();
                    }
                    // Add recipe to meal plan
                    return mealPlannerHook.addRecipeToMeal(day, mealType, recipe);
                  }}
                />
              </div>
            </div>
          )}
        </div>

        {/* Recipe Edit Modal */}
        <RecipeEditModal
          recipe={editingRecipe}
          isOpen={!!editingRecipe}
          onClose={() => setEditingRecipe(null)}
          onSave={handleSaveRecipe}
        />

        {/* Photo Import Modal */}
        <PhotoImportModal
          isOpen={showPhotoImport}
          onClose={() => setShowPhotoImport(false)}
          onImport={handlePhotoImport}
        />

        {/* Recipe Panel - Notion-style slide-in */}
        <RecipePanel
          recipe={viewingRecipe}
          isOpen={showRecipeDetail}
          onClose={handleCloseRecipeDetail}
          onEdit={handleRecipeEdit}
        />

        {/* Admin Dashboard Modal */}
        {isAdmin && showAdminDashboard && (
          <div className="modal-overlay" style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.7)',
            zIndex: 9999,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <div style={{
              backgroundColor: 'white',
              borderRadius: '10px',
              width: '90%',
              height: '90%',
              position: 'relative',
              overflow: 'hidden'
            }}>
              <button
                onClick={() => setShowAdminDashboard(false)}
                style={{
                  position: 'absolute',
                  top: '10px',
                  right: '10px',
                  background: '#e74c3c',
                  color: 'white',
                  border: 'none',
                  borderRadius: '50%',
                  width: '30px',
                  height: '30px',
                  cursor: 'pointer',
                  fontSize: '16px',
                  zIndex: 10000
                }}
              >
                ×
              </button>
              <AdminDashboard />
            </div>
          </div>
        )}
      </div>

      {/* Drag Overlay - Small floating preview */}
      <DragOverlay>
        {activeRecipe ? (
          <div style={{
            padding: '8px 16px',
            background: '#AAC6AD',
            color: 'white',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
            fontSize: '14px',
            fontWeight: '600',
            maxWidth: '200px',
            textAlign: 'center',
            cursor: 'grabbing'
          }}>
            📋 {activeRecipe.title}
          </div>
        ) : null}
      </DragOverlay>
    </DndContext>
  );
};

export default MainApp;
