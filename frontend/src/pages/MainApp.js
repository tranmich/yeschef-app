import React, { useState, useEffect } from 'react';
import { DndContext, closestCenter } from '@dnd-kit/core';
import SidebarContainer from '../components/SidebarContainer';
import ChatInterface from '../components/ChatInterface';
import CookbookSidebar from '../components/CookbookSidebar';
import RecipeListView from '../components/RecipeListView';
import RecipeEditModal from '../components/RecipeEditModal';
import ImportRecipeModal from '../components/ImportRecipeModal';
import RecipeDetailModal from '../components/RecipeDetailModal';
import AdminDashboard from '../components/AdminDashboard';
import AdminRecipeOverlay from '../components/AdminRecipeOverlay';
import GroceryManagerWorkspace from '../components/GroceryManagerWorkspace';
import './MainApp.css';
import SessionMemoryManager from '../utils/SessionMemoryManager';
import { usePantry } from '../hooks/usePantry';
import { useMealPlanner, useDragAndDrop, useSidebar } from '../hooks';
import * as api from '../utils/api';

const MainApp = () => {
  console.log('🚀 MainApp component loaded - COOKBOOK-FIRST VERSION 2025-08-22');

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
  const [showImportModal, setShowImportModal] = useState(false);
  const [viewingRecipe, setViewingRecipe] = useState(null);
  const [showRecipeDetail, setShowRecipeDetail] = useState(false);

  // --- Admin State ---
  const [isAdmin, setIsAdmin] = useState(false);
  const [adminMode, setAdminMode] = useState(false);
  const [showAdminDashboard, setShowAdminDashboard] = useState(false);

  // Recipe container state
  const [containerRecipes, setContainerRecipes] = useState([]);

  // Active view state (cookbook or grocery-manager)
  const [activeView, setActiveView] = useState('cookbook');

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

  const loadRecipes = async () => {
    setLoading(true);
    console.log('🔄 Starting recipe load process...');
    
    try {
      console.log('🍽️ Loading user recipes from personal collection...');
      
      // Use the new user-specific API that returns only user's recipes
      const response = await api.getUserRecipes();
      console.log('📊 User recipes response:', response);
      
      // Check for admin access
      if (response && response.admin_access) {
        console.log('🔧 Admin access granted');
        setIsAdmin(true);
      } else {
        setIsAdmin(false);
      }
      
      // Handle the response structure
      let recipes = [];
      if (response && response.success && Array.isArray(response.data)) {
        recipes = response.data;
        console.log('✅ Found user recipes:', recipes.length);
        console.log('📝 Recipe types:', recipes.map(r => r.recipe_type || 'unknown'));
        
        // Admin gets different message
        if (response.admin_access) {
          console.log('🔧 Admin loaded ALL database recipes for curation');
        }
      } else if (response && Array.isArray(response)) {
        recipes = response;
        console.log('✅ Response itself is array:', recipes.length);
      } else {
        console.log('⚠️ Unexpected response structure, falling back to search');
        // Fallback to old method if user recipes fails
        const fallback = await api.searchRecipes('recipe');
        if (fallback && Array.isArray(fallback.recipes)) {
          recipes = fallback.recipes;
          console.log('🔄 Fallback found recipes:', recipes.length);
        } else if (fallback && Array.isArray(fallback.data)) {
          recipes = fallback.data;
          console.log('🔄 Fallback found recipes in data:', recipes.length);
        }
      }
      
      if (recipes.length > 0) {
        console.log(`✅ Setting ${recipes.length} recipes from database`);
        console.log('📋 First recipe sample:', recipes[0]);
        setRecipes(recipes);
      } else {
        console.log('⚠️ No recipes found in any expected format, using sample data as fallback');
        setSampleRecipes();
      }
    } catch (error) {
      console.error('❌ Error loading recipes via api.searchRecipes:', error);
      console.error('❌ Error details:', error.message, error.stack);
      console.log('🔄 Using sample data as fallback due to error');
      setSampleRecipes();
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
    
    // If all API calls fail, use sample data
    console.log('🔄 All API calls failed, using sample data');
    setSampleRecipes();
  };

  const setSampleRecipes = () => {
    // Temporary sample data to see the interface
    const sampleRecipes = [
      {
        id: 1,
        title: "Classic Spaghetti Carbonara",
        ingredients: "Spaghetti, eggs, pancetta, parmesan cheese, black pepper",
        instructions: "Cook pasta, mix eggs with cheese, combine with hot pasta and pancetta",
        time_min: 25,
        servings: 4,
        meal_role: "dinner",
        is_easy: true,
        is_one_pot: false,
        rating: 4.8,
        date_added: "2025-08-20"
      },
      {
        id: 2,
        title: "Fluffy Pancakes",
        ingredients: "Flour, milk, eggs, sugar, baking powder, butter",
        instructions: "Mix dry ingredients, combine wet ingredients, fold together, cook on griddle",
        time_min: 15,
        servings: 2,
        meal_role: "breakfast",
        is_easy: true,
        is_one_pot: true,
        rating: 4.6,
        date_added: "2025-08-21"
      },
      {
        id: 3,
        title: "Mediterranean Quinoa Salad",
        ingredients: "Quinoa, cucumber, tomatoes, feta cheese, olives, lemon, olive oil",
        instructions: "Cook quinoa, chop vegetables, combine with cheese and dressing",
        time_min: 20,
        servings: 6,
        meal_role: "lunch",
        is_easy: true,
        is_one_pot: false,
        rating: 4.4,
        date_added: "2025-08-19"
      },
      {
        id: 4,
        title: "Chocolate Chip Cookies",
        ingredients: "Flour, butter, brown sugar, eggs, vanilla, chocolate chips",
        instructions: "Cream butter and sugar, add eggs and vanilla, mix in flour and chips, bake",
        time_min: 35,
        servings: 24,
        meal_role: "dessert",
        is_easy: true,
        is_one_pot: false,
        rating: 4.9,
        date_added: "2025-08-18"
      },
      {
        id: 5,
        title: "One-Pot Chicken and Rice",
        ingredients: "Chicken thighs, rice, onion, garlic, chicken broth, peas",
        instructions: "Brown chicken, sauté onion and garlic, add rice and broth, simmer until tender",
        time_min: 40,
        servings: 4,
        meal_role: "dinner",
        is_easy: true,
        is_one_pot: true,
        rating: 4.7,
        date_added: "2025-08-17"
      }
    ];
    setRecipes(sampleRecipes);
  };

  const calculateRecipeCounts = () => {
    const counts = {
      all: recipes.length,
      breakfast: 0,
      lunch: 0,
      dinner: 0,
      desserts: 0,
      'one-pot': 0,
      quick: 0,
      favorites: 0
    };

    recipes.forEach(recipe => {
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
    if (selectedCategory === 'all') return recipes;
    
    return recipes.filter(recipe => {
      switch (selectedCategory) {
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
  };

  const handleCategorySelect = (categoryId) => {
    setSelectedCategory(categoryId);
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

  const handleRecipeEdit = (recipe) => {
    setEditingRecipe(recipe);
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
  const handleShowGroceryList = () => {
    setActiveView('grocery-manager');
    setShowChat(false); // Close chat if open
    sidebarHook.closeAllSidebars(); // Close other sidebars
  };

  // Handle recipe import functionality
  const handleImportRecipe = (importResult) => {
    console.log('Recipe imported successfully:', importResult);
    console.log('🔍 Raw recipe data:', importResult.recipe_data);
    
    // Instead of reloading all recipes, add the new recipe to the existing list
    if (importResult.success && importResult.recipe_data) {
      // Normalize ingredients to be searchable
      let normalizedIngredients = importResult.recipe_data.ingredients || [];
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
        if (!timeStr) return null;
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
      
      const prepTimeMin = parseTimeToMinutes(importResult.recipe_data.prep_time);
      const cookTimeMin = parseTimeToMinutes(importResult.recipe_data.cook_time);
      const totalTimeMin = (prepTimeMin || 0) + (cookTimeMin || 0) || null;
      
      const newRecipe = {
        id: importResult.recipe_id,
        title: importResult.recipe_data.title || 'Imported Recipe',
        description: importResult.recipe_data.description || '',
        ingredients: ingredientsString, // Store as string for search compatibility
        instructions: importResult.recipe_data.instructions || [],
        prep_time: importResult.recipe_data.prep_time || '',
        cook_time: importResult.recipe_data.cook_time || '',
        time_min: totalTimeMin, // Add time_min field that UI expects
        servings: importResult.recipe_data.servings || '',
        category: importResult.recipe_data.category || 'Imported',
        meal_role: mapCategoryToMealRole(importResult.recipe_data.category), // Proper meal role mapping
        source_url: importResult.recipe_data.source_url || '',
        confidence: importResult.confidence || 0.0,
        is_easy: totalTimeMin && totalTimeMin <= 30, // Mark as easy if quick
        pantryOverlap: 0, // Default pantry overlap
        // Add current timestamp for sorting
        imported_at: new Date().toISOString(),
        created_at: new Date().toISOString(),
        date_added: new Date().toISOString()
      };
      
      console.log('🔍 Final normalized recipe:', newRecipe);
      
      // Add the new recipe to the top of the list
      setRecipes(prevRecipes => [newRecipe, ...prevRecipes]);
      console.log('✅ Added imported recipe to list:', newRecipe.title);
    } else {
      // Fallback: refresh recipe list only if we couldn't get the recipe data
      console.log('⚠️ Import result missing recipe data, refreshing full list');
      loadRecipes();
    }
  };

  const handleCloseImportModal = () => {
    setShowImportModal(false);
  };

  // Drag and drop with meal planner and container integration
  const dragAndDropHook = useDragAndDrop(
    (day, mealType, recipe) => {
      return mealPlannerHook.addRecipeToMeal(day, mealType, recipe);
    },
    handleRecipeAddedToContainer,
    (sourceDay, sourceMealType, sourceIndex, targetDay, targetMealType, recipe) => {
      return mealPlannerHook.moveRecipe(sourceDay, sourceMealType, sourceIndex, targetDay, targetMealType, recipe);
    }
  );

  return (
    <DndContext
      sensors={dragAndDropHook.sensors}
      collisionDetection={closestCenter}
      onDragStart={dragAndDropHook.handleDragStart}
      onDragEnd={dragAndDropHook.handleDragEnd}
      onDragCancel={dragAndDropHook.handleDragCancel}
    >
      <div className="app-container cookbook-first">
        {/* Navigation Sidebar - Left Side */}
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
          onFeatureSelect={(feature) => {
            console.log('Feature selected:', feature);
            if (feature === 'cookbook') {
              setActiveView('cookbook');
              setShowChat(false);
              sidebarHook.closeAllSidebars();
            } else if (feature === 'grocery-lists') {
              setActiveView('grocery-manager');
              setShowChat(false);
              sidebarHook.closeAllSidebars();
            } else if (feature === 'import') {
              setShowImportModal(true);
            }
          }}
        />

        {/* Cookbook Sidebar - Compact */}
        <CookbookSidebar
          categories={customCategories}
          selectedCategory={selectedCategory}
          onCategorySelect={handleCategorySelect}
          recipeCounts={recipeCounts}
          onAddCategory={handleAddCategory}
          onRefreshRecipes={loadRecipes}
        />

        {/* Main Content Area */}
        <div className="main-content">
          {/* Admin Controls - Only show for admin users */}
          {isAdmin && (
            <div className="admin-controls" style={{
              position: 'absolute',
              top: '10px',
              right: '20px',
              zIndex: 1000,
              display: 'flex',
              gap: '10px',
              alignItems: 'center'
            }}>
              <button
                className={`admin-mode-toggle ${adminMode ? 'active' : ''}`}
                onClick={() => setAdminMode(!adminMode)}
                style={{
                  padding: '8px 16px',
                  backgroundColor: adminMode ? '#e74c3c' : '#3498db',
                  color: 'white',
                  border: 'none',
                  borderRadius: '5px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: 'bold'
                }}
              >
                {adminMode ? '🔧 Admin ON' : '⚙️ Admin Mode'}
              </button>
              <button
                className="admin-dashboard-btn"
                onClick={() => setShowAdminDashboard(true)}
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#9b59b6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '5px',
                  cursor: 'pointer',
                  fontSize: '14px'
                }}
              >
                📊 Admin Dashboard
              </button>
            </div>
          )}

          {/* Main Content - Conditional View */}
          {activeView === 'cookbook' && (
            <RecipeListView
              recipes={getFilteredRecipes()}
              selectedCategory={selectedCategory}
              onRecipeClick={handleRecipeClick}
              onRecipeEdit={handleRecipeEdit}
              loading={loading}
              adminMode={adminMode && isAdmin}
              isAdmin={isAdmin}
            />
          )}

          {activeView === 'grocery-manager' && (
            <GroceryManagerWorkspace
              mealPlanRecipes={mealPlannerHook.getAllMealPlanRecipes().map(recipe => recipe.id).filter(Boolean)}
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

        {/* Recipe Import Modal */}
        <ImportRecipeModal
          isOpen={showImportModal}
          onClose={handleCloseImportModal}
          onImport={handleImportRecipe}
        />

        {/* Recipe Detail Modal */}
        <RecipeDetailModal
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
    </DndContext>
  );
};

export default MainApp;
