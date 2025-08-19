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
    showGroceryListFromNav,
    setShowGroceryListFromNav,
    onFeatureSelect,
    isPantryExpanded,
    isMealPlannerExpanded,
    onTogglePantryExpand,
    onToggleMealPlannerExpand,
    onShowGroceryList
}) => {
    return (
        <div className="sidebar-container">
            {/* Sidebar Navigation - Always visible */}
            <SidebarNavigation
                showMealPlanner={showMealPlanner}
                onToggleMealPlanner={onToggleMealPlanner}
                showPantry={showPantry}
                onTogglePantry={onTogglePantry}
                onFeatureSelect={onFeatureSelect}
                onShowGroceryList={onShowGroceryList}
            />

            {/* Pantry Sidebar */}
            <div className={`pantry-sidebar ${showPantry ? 'visible' : ''} ${isPantryExpanded ? 'expanded' : ''}`}>
                {/* Pantry Content */}
                {/* Expand Button */}
                {!isPantryExpanded && (
                    <button
                        className="pantry-expand"
                        onClick={onTogglePantryExpand}
                        title="Expand pantry"
                    >
                        ⛶
                    </button>
                )}

                {/* Close Button (shows when expanded) */}
                {isPantryExpanded ? (
                    <button
                        className="pantry-close expanded"
                        onClick={() => {
                            onTogglePantryExpand(); // Collapse first
                            onTogglePantry(); // Then close
                        }}
                        title="Close pantry"
                    >
                        ✕
                    </button>
                ) : (
                    <button
                        className="pantry-close"
                        onClick={() => onTogglePantry()}
                        title="Close pantry"
                    >
                        ✕
                    </button>
                )}

                <PantryManager />
            </div>

            {/* Meal Planner Sidebar - Notion-inspired */}
            <div className={`meal-planner-sidebar ${showMealPlanner ? 'visible' : ''} ${isMealPlannerExpanded ? 'expanded' : ''}`}>
                {/* Meal Planner Content */}
                {/* Expand Button */}
                {!isMealPlannerExpanded && (
                    <button
                        className="meal-planner-expand"
                        onClick={onToggleMealPlannerExpand}
                        title="Expand meal planner"
                    >
                        ⛶
                    </button>
                )}

                {/* Expanded Controls (shows when expanded) */}
                {isMealPlannerExpanded && (
                    <div className="expanded-controls">
                        <button
                            className="meal-planner-collapse"
                            onClick={onToggleMealPlannerExpand}
                            title="Collapse meal planner"
                        >
                            ››
                        </button>
                        <button
                            className="meal-planner-close expanded"
                            onClick={() => {
                                onToggleMealPlannerExpand(); // Collapse first
                                onToggleMealPlanner(); // Then close
                            }}
                            title="Close meal planner"
                        >
                            ✕
                        </button>
                    </div>
                )}

                {/* Normal Close Button (shows when not expanded) */}
                {!isMealPlannerExpanded && (
                    <button
                        className="meal-planner-close"
                        onClick={() => onToggleMealPlanner()}
                        title="Close meal planner"
                    >
                        ✕
                    </button>
                )}

                <MealPlannerView
                    mealPlan={mealPlan}
                    setMealPlan={setMealPlan}
                    containerRecipes={containerRecipes}
                    setContainerRecipes={setContainerRecipes}
                    showGroceryListFromNav={showGroceryListFromNav}
                    setShowGroceryListFromNav={setShowGroceryListFromNav}
                    isVisible={showMealPlanner}
                    isCompact={showMealPlanner}
                />
            </div>
        </div>
    );
};

export default SidebarContainer;
