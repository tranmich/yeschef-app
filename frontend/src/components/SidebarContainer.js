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
    onToggleChat
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
                />
            </div>
        </div>
    );
};

export default SidebarContainer;
