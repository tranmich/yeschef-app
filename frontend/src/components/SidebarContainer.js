import React from 'react';
import SidebarNavigation from './SidebarNavigation';
import PantryManager from './PantryManager';
import MealPlannerView from './MealPlannerView';
import './SidebarContainer.css';

const SidebarContainer = ({
    showMealPlanner,
    onToggleMealPlanner,
    showPantry,
    onTogglePantry,
    mealPlan,
    setMealPlan,
    containerRecipes,
    setContainerRecipes,
    onFeatureSelect,
    isPantryExpanded,
    isMealPlannerExpanded,
    onTogglePantryExpand,
    onToggleMealPlannerExpand,
    onShowGroceryList,
    showChat,
    onToggleChat,
    // Recipe category props
    selectedCategory,
    onCategorySelect,
    recipeCounts,
    customCategories,
    onAddCategory,
    onRefreshRecipes,
    // Admin props
    isAdmin,
    onShowAdminDashboard
}) => {
    return (
        <div className="sidebar-container">
            <SidebarNavigation
                showMealPlanner={showMealPlanner}
                onToggleMealPlanner={onToggleMealPlanner}
                showPantry={showPantry}
                onTogglePantry={onTogglePantry}
                onShowGroceryList={onShowGroceryList}
                showChat={showChat}
                onToggleChat={onToggleChat}
                onFeatureSelect={onFeatureSelect}
                // Recipe category props
                selectedCategory={selectedCategory}
                onCategorySelect={onCategorySelect}
                recipeCounts={recipeCounts}
                customCategories={customCategories}
                onAddCategory={onAddCategory}
                onRefreshRecipes={onRefreshRecipes}
                // Admin props
                isAdmin={isAdmin}
                onShowAdminDashboard={onShowAdminDashboard}
            />
            <div className={`pantry-sidebar ${showPantry ? 'visible' : ''} ${isPantryExpanded ? 'expanded' : ''}`}>
                <PantryManager />
            </div>

            <div className={`meal-planner-sidebar ${showMealPlanner ? 'visible' : ''} ${isMealPlannerExpanded ? 'expanded' : ''}`}>
                <MealPlannerView
                    mealPlan={mealPlan}
                    setMealPlan={setMealPlan}
                    containerRecipes={containerRecipes}
                    setContainerRecipes={setContainerRecipes}
                    isVisible={showMealPlanner}
                    isCompact={showMealPlanner}
                    onShowGroceryList={onShowGroceryList}
                />
            </div>
        </div>
    );
};

export default SidebarContainer;
