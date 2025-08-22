import React, { useState, useEffect } from 'react';
import './RecipeEditModal.css';

const RecipeEditModal = ({ recipe, isOpen, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    title: '',
    ingredients: '',
    instructions: '',
    servings: '',
    time_min: '',
    meal_role: '',
    notes: ''
  });
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (recipe && isOpen) {
      setFormData({
        title: recipe.title || '',
        ingredients: recipe.ingredients || '',
        instructions: recipe.instructions || '',
        servings: recipe.servings || '',
        time_min: recipe.time_min || '',
        meal_role: recipe.meal_role || '',
        notes: recipe.notes || ''
      });
    }
  }, [recipe, isOpen]);

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const updatedRecipe = {
        ...recipe,
        ...formData,
        servings: formData.servings ? parseInt(formData.servings) : null,
        time_min: formData.time_min ? parseInt(formData.time_min) : null
      };
      await onSave(updatedRecipe);
      onClose();
    } catch (error) {
      console.error('Error saving recipe:', error);
    } finally {
      setIsSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="recipe-edit-modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Edit Recipe</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="modal-content">
          <div className="form-group">
            <label>Recipe Title</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => handleChange('title', e.target.value)}
              placeholder="Enter recipe title..."
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Prep Time (minutes)</label>
              <input
                type="number"
                value={formData.time_min}
                onChange={(e) => handleChange('time_min', e.target.value)}
                placeholder="30"
              />
            </div>
            <div className="form-group">
              <label>Servings</label>
              <input
                type="number"
                value={formData.servings}
                onChange={(e) => handleChange('servings', e.target.value)}
                placeholder="4"
              />
            </div>
            <div className="form-group">
              <label>Meal Type</label>
              <select
                value={formData.meal_role}
                onChange={(e) => handleChange('meal_role', e.target.value)}
              >
                <option value="">Select...</option>
                <option value="breakfast">Breakfast</option>
                <option value="lunch">Lunch</option>
                <option value="dinner">Dinner</option>
                <option value="snack">Snack</option>
                <option value="dessert">Dessert</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Ingredients</label>
            <textarea
              value={formData.ingredients}
              onChange={(e) => handleChange('ingredients', e.target.value)}
              placeholder="List ingredients, one per line..."
              rows={6}
            />
          </div>

          <div className="form-group">
            <label>Instructions</label>
            <textarea
              value={formData.instructions}
              onChange={(e) => handleChange('instructions', e.target.value)}
              placeholder="Step-by-step instructions..."
              rows={8}
            />
          </div>

          <div className="form-group">
            <label>Notes</label>
            <textarea
              value={formData.notes}
              onChange={(e) => handleChange('notes', e.target.value)}
              placeholder="Any additional notes or tips..."
              rows={3}
            />
          </div>
        </div>

        <div className="modal-footer">
          <button className="cancel-btn" onClick={onClose}>
            Cancel
          </button>
          <button 
            className="save-btn" 
            onClick={handleSave}
            disabled={isSaving || !formData.title.trim()}
          >
            {isSaving ? 'Saving...' : 'Save Recipe'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default RecipeEditModal;
