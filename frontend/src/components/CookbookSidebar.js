import React, { useState, useEffect } from 'react';
import './CookbookSidebar.css';

const CookbookSidebar = ({ 
  categories, 
  selectedCategory, 
  onCategorySelect, 
  recipeCounts,
  onAddCategory,
  onRefreshRecipes
}) => {
  const [showAddCategory, setShowAddCategory] = useState(false);
  const [newCategoryName, setNewCategoryName] = useState('');

  // Default categories with icons and colors
  const defaultCategories = [
    { id: 'all', name: 'All', icon: '📚', color: '#6B7280', isDefault: true },
    { id: 'breakfast', name: 'Breakfast', icon: '🍳', color: '#F59E0B', isDefault: true },
    { id: 'lunch', name: 'Lunch', icon: '🥗', color: '#10B981', isDefault: true },
    { id: 'dinner', name: 'Dinner', icon: '🍽️', color: '#3B82F6', isDefault: true },
    { id: 'desserts', name: 'Desserts', icon: '🍰', color: '#8B5CF6', isDefault: true },
    { id: 'one-pot', name: 'One-Pot', icon: '🥘', color: '#EF4444', isDefault: true },
    { id: 'quick', name: 'Quick', icon: '⚡', color: '#F97316', isDefault: true },
    { id: 'favorites', name: 'Favorites', icon: '⭐', color: '#EC4899', isDefault: true }
  ];

  // Merge default categories with user custom categories
  const allCategories = [
    ...defaultCategories,
    ...(categories || []).filter(cat => !defaultCategories.find(def => def.id === cat.id))
  ];

  const handleAddCategory = () => {
    if (newCategoryName.trim()) {
      const newCategory = {
        id: `custom-${Date.now()}`,
        name: newCategoryName.trim(),
        icon: '📁',
        color: '#6B7280',
        isDefault: false
      };
      onAddCategory(newCategory);
      setNewCategoryName('');
      setShowAddCategory(false);
    }
  };

  const getRecipeCount = (categoryId) => {
    return recipeCounts?.[categoryId] || 0;
  };

  return (
    <div className="cookbook-sidebar">
      <div className="cookbook-header">
        <h2>📚 Cookbook</h2>
        <div className="header-actions">
          <button 
            className="refresh-btn"
            onClick={onRefreshRecipes}
            title="Refresh Recipes"
          >
            🔄
          </button>
          <button 
            className="add-category-btn"
            onClick={() => setShowAddCategory(true)}
            title="Add New Category"
          >
            ➕
          </button>
        </div>
      </div>

      <div className="categories-list">
        {allCategories.map(category => (
          <div
            key={category.id}
            className={`category-folder ${selectedCategory === category.id ? 'active' : ''}`}
            onClick={() => onCategorySelect(category.id)}
            style={{ '--category-color': category.color }}
          >
            <div className="folder-content">
              <span className="folder-icon">{category.icon}</span>
              <span className="folder-name">{category.name}</span>
              <span className="recipe-count">({getRecipeCount(category.id)})</span>
            </div>
            <div className="folder-actions">
              <button className="folder-action" title="View recipes">👁️</button>
              <button className="folder-action" title="Folder stats">📊</button>
            </div>
          </div>
        ))}
      </div>

      {showAddCategory && (
        <div className="add-category-form">
          <input
            type="text"
            value={newCategoryName}
            onChange={(e) => setNewCategoryName(e.target.value)}
            placeholder="Category name..."
            className="category-input"
            onKeyPress={(e) => e.key === 'Enter' && handleAddCategory()}
            autoFocus
          />
          <div className="category-form-actions">
            <button onClick={handleAddCategory} className="save-btn">Save</button>
            <button 
              onClick={() => {
                setShowAddCategory(false);
                setNewCategoryName('');
              }} 
              className="cancel-btn"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="sidebar-footer">
        <div className="total-recipes">
          Total: {getRecipeCount('all')} recipes
        </div>
        <button 
          className="debug-btn"
          onClick={() => {
            console.log('🐛 Manual debug trigger');
            if (onRefreshRecipes) onRefreshRecipes();
          }}
          style={{
            width: '100%',
            padding: '4px',
            margin: '4px 0',
            fontSize: '10px',
            background: '#f0f0f0',
            border: '1px solid #ddd',
            borderRadius: '3px',
            cursor: 'pointer'
          }}
        >
          🐛 Debug Load
        </button>
      </div>
    </div>
  );
};

export default CookbookSidebar;
