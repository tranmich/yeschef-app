/**
 * Meal Plan Floating Widget
 * ==========================
 * Draggable meal plan "day box" widget for whiteboard canvas
 * 
 * Features:
 * - Drag to reposition anywhere on canvas
 * - Groups recipes together (like "Day 1" or "Potluck")
 * - Renameable day labels
 * - Generate grocery list from all recipes in the day
 * - Visual connection lines to recipe cards
 * - Compatible with existing meal plan schema
 * 
 * Schema: meal_plans table with plan_data_json containing:
 * {
 *   days: {
 *     'day1': { name: 'Day 1', recipes: [...] },
 *     'day2': { name: 'Day 2', recipes: [...] }
 *   }
 * }
 * 
 * Author: GitHub Copilot
 * Date: November 4, 2025
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import MiniRecipeCard from './MiniRecipeCard';
import './MealPlanFloatingWidget.css';

const MealPlanFloatingWidget = ({
  mealPlanDay, // { id: 'day1', dayId: 'day1', name: 'Day 1', recipes: [], position: {x, y}, dbId: null }
  householdId,
  whiteboardId,
  linkedRecipes = [],
  initialPosition = { x: 400, y: 100 },
  viewport = { x: 0, y: 0, zoom: 1 }, // Canvas viewport for transformation
  onPositionChange,
  onClose,
  onNameChange,
  onRecipeAdd, // Callback when recipe is added to this meal plan
  onRecipeRemove, // Callback when recipe is removed from this meal plan
  onGenerateGroceryList // Callback to generate grocery list from this day's recipes
}) => {
  // Widget state
  const [canvasPosition, setCanvasPosition] = useState(initialPosition);
  const [dimensions, setDimensions] = useState({ width: 320, height: 200 }); // Default size
  const [isMinimized, setIsMinimized] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [isResizing, setIsResizing] = useState(false);
  const [resizeHandle, setResizeHandle] = useState(null); // 'se', 'sw', 'ne', 'nw'
  const [isEditingName, setIsEditingName] = useState(false);
  const [dayName, setDayName] = useState(mealPlanDay.name || 'Day 1');
  const [isDragOver, setIsDragOver] = useState(false); // Drop zone state
  
  // Dragging/resizing state
  const dragStartPos = useRef({ x: 0, y: 0 });
  const resizeStartPos = useRef({ x: 0, y: 0, width: 0, height: 0 });
  const widgetRef = useRef(null);
  const nameInputRef = useRef(null);

  // Update position when initialPosition changes
  useEffect(() => {
    setCanvasPosition(initialPosition);
  }, [initialPosition]);

  // Update dimensions when mealPlanDay.dimensions changes
  useEffect(() => {
    if (mealPlanDay.dimensions) {
      setDimensions(mealPlanDay.dimensions);
    }
  }, [mealPlanDay.dimensions]);

  // Update name when mealPlanDay.name changes
  useEffect(() => {
    setDayName(mealPlanDay.name || 'Day 1');
  }, [mealPlanDay.name]);

  // Focus name input when editing
  useEffect(() => {
    if (isEditingName && nameInputRef.current) {
      nameInputRef.current.focus();
      nameInputRef.current.select();
    }
  }, [isEditingName]);

  // Calculate screen position from canvas position (matching GroceryListFloatingWidget)
  const screenPosition = {
    x: canvasPosition.x * viewport.zoom + viewport.x,
    y: canvasPosition.y * viewport.zoom + viewport.y
  };

  // Handle drag start
  const handleMouseDown = (e) => {
    // Stop event propagation to prevent React Flow from handling it
    e.stopPropagation();
    
    if (e.target.closest('.no-drag')) return; // Don't drag if clicking on buttons or inputs
    
    setIsDragging(true);
    dragStartPos.current = {
      x: e.clientX - screenPosition.x,
      y: e.clientY - screenPosition.y
    };
    e.preventDefault();
  };

  // Handle drag move
  useEffect(() => {
    if (!isDragging) return;

    const handleMouseMove = (e) => {
      e.stopPropagation();
      e.preventDefault();
      
      const newScreenX = e.clientX - dragStartPos.current.x;
      const newScreenY = e.clientY - dragStartPos.current.y;
      
      // Convert back to canvas coordinates
      const newCanvasX = (newScreenX - viewport.x) / viewport.zoom;
      const newCanvasY = (newScreenY - viewport.y) / viewport.zoom;
      
      const newPosition = { x: newCanvasX, y: newCanvasY };
      setCanvasPosition(newPosition);
    };

    const handleMouseUp = (e) => {
      e.stopPropagation();
      setIsDragging(false);
      
      // Notify parent of position AND dimensions
      onPositionChange?.({ position: canvasPosition, dimensions });
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, viewport.x, viewport.y, viewport.zoom, canvasPosition, onPositionChange]);

  // Handle resize start
  const handleResizeStart = (e, handle) => {
    e.stopPropagation();
    e.preventDefault();
    
    setIsResizing(true);
    setResizeHandle(handle);
    
    resizeStartPos.current = {
      x: e.clientX,
      y: e.clientY,
      width: dimensions.width,
      height: dimensions.height,
      posX: canvasPosition.x,
      posY: canvasPosition.y
    };
  };

  // Handle resize move
  useEffect(() => {
    if (!isResizing) return;

    const handleMouseMove = (e) => {
      e.stopPropagation();
      e.preventDefault();
      
      const deltaX = (e.clientX - resizeStartPos.current.x) / viewport.zoom;
      const deltaY = (e.clientY - resizeStartPos.current.y) / viewport.zoom;
      
      let newWidth = dimensions.width;
      let newHeight = dimensions.height;
      let newPosX = canvasPosition.x;
      let newPosY = canvasPosition.y;
      
      // Calculate new dimensions based on handle
      if (resizeHandle.includes('e')) { // East (right)
        newWidth = Math.max(200, resizeStartPos.current.width + deltaX);
      }
      if (resizeHandle.includes('w')) { // West (left)
        const widthChange = deltaX;
        newWidth = Math.max(200, resizeStartPos.current.width - widthChange);
        newPosX = resizeStartPos.current.posX + (resizeStartPos.current.width - newWidth);
      }
      if (resizeHandle.includes('s')) { // South (bottom)
        newHeight = Math.max(150, resizeStartPos.current.height + deltaY);
      }
      if (resizeHandle.includes('n')) { // North (top)
        const heightChange = deltaY;
        newHeight = Math.max(150, resizeStartPos.current.height - heightChange);
        newPosY = resizeStartPos.current.posY + (resizeStartPos.current.height - newHeight);
      }
      
      setDimensions({ width: newWidth, height: newHeight });
      setCanvasPosition({ x: newPosX, y: newPosY });
    };

    const handleMouseUp = (e) => {
      e.stopPropagation();
      setIsResizing(false);
      setResizeHandle(null);
      
      // Notify parent of position AND dimensions after resize
      console.log(`📏 Resized to: ${dimensions.width}x${dimensions.height}`);
      onPositionChange?.({ position: canvasPosition, dimensions });
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing, resizeHandle, viewport.zoom, dimensions, canvasPosition, onPositionChange]);

  // Handle name edit
  const handleNameClick = () => {
    setIsEditingName(true);
  };

  const handleNameChange = (e) => {
    setDayName(e.target.value);
  };

  const handleNameBlur = () => {
    setIsEditingName(false);
    
    // Auto-save to database if name changed
    if (dayName !== mealPlanDay.name) {
      console.log(`💾 Auto-saving meal plan name: "${mealPlanDay.name}" → "${dayName}"`);
      onNameChange?.(dayName);
    }
  };

  const handleNameKeyPress = (e) => {
    if (e.key === 'Enter') {
      setIsEditingName(false);
      
      // Auto-save to database if name changed
      if (dayName !== mealPlanDay.name) {
        console.log(`💾 Auto-saving meal plan name: "${mealPlanDay.name}" → "${dayName}"`);
        onNameChange?.(dayName);
      }
    } else if (e.key === 'Escape') {
      // Revert changes on Escape
      setDayName(mealPlanDay.name || 'Day 1');
      setIsEditingName(false);
    }
  };

  // Handle generate grocery list
  const handleGenerateGroceryList = () => {
    if (linkedRecipes.length === 0) {
      alert('Add some recipes to this day first!');
      return;
    }
    onGenerateGroceryList?.(linkedRecipes, dayName);
  };

  // Handle drop zone for recipe cards
  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    try {
      // Get recipe data from drag event
      const recipeDataStr = e.dataTransfer.getData('application/recipe');
      if (!recipeDataStr) {
        console.log('No recipe data in drop event');
        return;
      }

      const recipeData = JSON.parse(recipeDataStr);
      console.log('📥 Recipe dropped into meal plan:', recipeData);

      // Check if recipe is already in this meal plan
      const alreadyAdded = linkedRecipes.some(r => 
        (r.id || r.recipe_id) === (recipeData.id || recipeData.recipe_id)
      );

      if (alreadyAdded) {
        console.log('⚠️ Recipe already in this meal plan');
        return;
      }

      // Call parent callback to add recipe
      onRecipeAdd?.(mealPlanDay.dayId, recipeData);
    } catch (error) {
      console.error('❌ Error handling recipe drop:', error);
    }
  };

  // Handle recipe removal
  const handleRecipeRemove = (recipe) => {
    console.log('🗑️ Removing recipe from meal plan:', recipe);
    onRecipeRemove?.(mealPlanDay.dayId, recipe);
  };

  // Handle recipe card click (view recipe)
  const handleRecipeClick = (recipe) => {
    console.log('👀 View recipe:', recipe);
    // TODO: Open recipe detail modal
  };

  const recipeCount = linkedRecipes.length;

  return (
    <div
      ref={widgetRef}
      className={`meal-plan-floating-widget ${isMinimized ? 'minimized' : ''} ${isDragging ? 'dragging' : ''} ${isResizing ? 'resizing' : ''} ${isDragOver ? 'drag-over' : ''}`}
      style={{
        position: 'absolute',
        left: `${screenPosition.x}px`,
        top: `${screenPosition.y}px`,
        width: `${dimensions.width}px`,
        height: `${dimensions.height}px`,
        transform: `scale(${viewport.zoom})`,
        transformOrigin: 'top left',
        zIndex: isDragging || isResizing ? 10000 : 1000,
        cursor: isDragging ? 'grabbing' : 'grab'
      }}
      onMouseDown={handleMouseDown}
      onClick={(e) => e.stopPropagation()} // Prevent React Flow from handling clicks
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Header */}
      <div className="widget-header">
        <div className="header-left">
          {isEditingName ? (
            <input
              ref={nameInputRef}
              type="text"
              value={dayName}
              onChange={handleNameChange}
              onBlur={handleNameBlur}
              onKeyDown={handleNameKeyPress}
              className="name-input no-drag"
              maxLength={30}
            />
          ) : (
            <span className="widget-title no-drag" onClick={handleNameClick}>
              {dayName}
            </span>
          )}
        </div>
        <div className="header-right">
          <button
            className="header-btn no-drag"
            onClick={() => setIsMinimized(!isMinimized)}
            title={isMinimized ? 'Expand' : 'Minimize'}
          >
            {isMinimized ? '▼' : '▲'}
          </button>
          <button className="header-btn close-btn no-drag" onClick={onClose} title="Close">
            ×
          </button>
        </div>
      </div>

      {/* Content */}
      {!isMinimized && (
        <div className="widget-content">
          {/* Recipe count */}
          <div className="day-summary">
            <span className="recipe-count">
              {recipeCount} {recipeCount === 1 ? 'recipe' : 'recipes'}
            </span>
          </div>

          {/* Recipe list */}
          {linkedRecipes.length > 0 ? (
            <div className="recipe-grid">
              {linkedRecipes.map((recipe, index) => (
                <MiniRecipeCard
                  key={recipe.id || recipe.recipe_id || index}
                  recipe={recipe}
                  onRemove={handleRecipeRemove}
                  onClick={handleRecipeClick}
                />
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>💡 Drag recipe cards here</p>
              <span className="empty-hint">or click "Add Recipe" below</span>
            </div>
          )}

          {/* Footer actions */}
          <div className="widget-footer">
            <button 
              className="footer-btn no-drag" 
              onClick={handleGenerateGroceryList}
              disabled={recipeCount === 0}
            >
              Generate Grocery List
            </button>
            <div className="footer-hint">
              💡 Press Ctrl+S to save
            </div>
          </div>
        </div>
      )}
      
      {/* Resize Handles (Illustrator-style corners) */}
      <div
        className="resize-handle resize-handle-se no-drag"
        onMouseDown={(e) => handleResizeStart(e, 'se')}
        title="Resize"
      />
      <div
        className="resize-handle resize-handle-sw no-drag"
        onMouseDown={(e) => handleResizeStart(e, 'sw')}
        title="Resize"
      />
      <div
        className="resize-handle resize-handle-ne no-drag"
        onMouseDown={(e) => handleResizeStart(e, 'ne')}
        title="Resize"
      />
      <div
        className="resize-handle resize-handle-nw no-drag"
        onMouseDown={(e) => handleResizeStart(e, 'nw')}
        title="Resize"
      />
    </div>
  );
};

export default MealPlanFloatingWidget;
