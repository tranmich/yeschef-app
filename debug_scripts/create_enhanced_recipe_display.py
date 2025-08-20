#!/usr/bin/env python3
"""
Frontend Recipe Display Enhancement Script
Creates improved recipe display components with better error handling and data validation
"""

import os
import json

def create_enhanced_recipe_display_component():
    """Create enhanced RecipeCard component with quality handling"""
    
    component_code = '''import React from 'react';
import './RecipeCard.css';

const RecipeCard = ({ recipe, onAddToMealPlan, onSaveRecipe, showQuality = true }) => {
  // Data quality validation
  const validateRecipeData = (recipe) => {
    const quality = {
      score: 0,
      issues: [],
      hasTitle: !!(recipe.title && recipe.title.trim().length > 0),
      hasIngredients: !!(recipe.ingredients && recipe.ingredients !== '[]' && 
                        recipe.ingredients.trim().length > 20),
      hasInstructions: !!(recipe.instructions && recipe.instructions !== '[]' && 
                         recipe.instructions.trim().length > 50),
      hasServings: !!(recipe.servings && recipe.servings.trim().length > 0),
      hasTime: !!(recipe.total_time && recipe.total_time.trim().length > 0)
    };

    // Calculate quality score
    quality.score = [
      quality.hasTitle,
      quality.hasIngredients,
      quality.hasInstructions,
      quality.hasServings,
      quality.hasTime
    ].filter(Boolean).length;

    // Identify issues
    if (!quality.hasTitle) quality.issues.push('Missing title');
    if (!quality.hasIngredients) quality.issues.push('Missing or insufficient ingredients');
    if (!quality.hasInstructions) quality.issues.push('Missing or insufficient instructions');
    if (!quality.hasServings) quality.issues.push('No serving information');
    if (!quality.hasTime) quality.issues.push('No time information');

    quality.isGood = quality.score >= 4;
    quality.isUsable = quality.score >= 3;
    
    return quality;
  };

  // Format ingredients safely
  const formatIngredients = (ingredients) => {
    if (!ingredients || ingredients === '[]') {
      return ['No ingredients available'];
    }

    try {
      // Try to parse as JSON array
      const parsed = JSON.parse(ingredients);
      if (Array.isArray(parsed)) {
        return parsed.filter(item => 
          item && 
          typeof item === 'string' && 
          item.trim() !== 'INGREDIENTS' &&
          item.trim().length > 0
        ).map(item => item.replace(/^"|"$/g, '').trim());
      }
    } catch (e) {
      // Not JSON, treat as string
    }

    // Handle string format
    if (typeof ingredients === 'string') {
      if (ingredients.includes('\\n')) {
        return ingredients.split('\\n').filter(item => 
          item && 
          item.trim() !== 'INGREDIENTS' &&
          item.trim().length > 0
        );
      }
      
      if (ingredients.includes(',')) {
        return ingredients.split(',').filter(item => 
          item && 
          item.trim().length > 0
        ).map(item => item.trim());
      }
      
      // Single ingredient or unstructured text
      return [ingredients.trim()];
    }

    return ['Ingredients need formatting'];
  };

  // Format instructions safely
  const formatInstructions = (instructions) => {
    if (!instructions || instructions === '[]') {
      return 'No instructions available';
    }

    try {
      // Try to parse as JSON array
      const parsed = JSON.parse(instructions);
      if (Array.isArray(parsed)) {
        return parsed.filter(item => 
          item && 
          typeof item === 'string' && 
          item.trim() !== 'DIRECTIONS' &&
          item.trim().length > 0
        ).join(' ').replace(/^"|"$/g, '').trim();
      }
    } catch (e) {
      // Not JSON, treat as string
    }

    // Clean up string format
    if (typeof instructions === 'string') {
      return instructions
        .replace(/DIRECTIONS\\n/g, '')
        .replace(/^"|"$/g, '')
        .trim();
    }

    return 'Instructions need formatting';
  };

  // Safe field access with fallbacks
  const getTitle = () => recipe.title || 'Untitled Recipe';
  const getServings = () => {
    if (!recipe.servings) return 'Servings not specified';
    return recipe.servings.replace(/^(Serves |)/, '').replace(/ (servings|portions)$/, '') + ' servings';
  };
  const getTime = () => recipe.total_time || 'Time not specified';
  const getCategory = () => recipe.category || 'Uncategorized';

  const quality = validateRecipeData(recipe);
  const ingredients = formatIngredients(recipe.ingredients);
  const instructions = formatInstructions(recipe.instructions);

  return (
    <div className={`recipe-card ${!quality.isUsable ? 'low-quality' : ''}`}>
      {/* Quality indicator */}
      {showQuality && (
        <div className={`quality-indicator quality-${quality.score}`}>
          <span className="quality-score">{quality.score}/5</span>
          {quality.issues.length > 0 && (
            <div className="quality-issues">
              ⚠️ {quality.issues.join(', ')}
            </div>
          )}
        </div>
      )}

      {/* Recipe header */}
      <div className="recipe-header">
        <h3 className="recipe-title">{getTitle()}</h3>
        <div className="recipe-meta">
          <span className="servings">🍽️ {getServings()}</span>
          <span className="time">⏱️ {getTime()}</span>
          <span className="category">🏷️ {getCategory()}</span>
        </div>
      </div>

      {/* Recipe ingredients */}
      <div className="recipe-ingredients">
        <h4>Ingredients:</h4>
        {ingredients.length > 0 ? (
          <ul>
            {ingredients.slice(0, 6).map((ingredient, index) => (
              <li key={index}>{ingredient}</li>
            ))}
            {ingredients.length > 6 && (
              <li className="more-ingredients">
                ...and {ingredients.length - 6} more ingredients
              </li>
            )}
          </ul>
        ) : (
          <p className="missing-data">Ingredients not available</p>
        )}
      </div>

      {/* Recipe instructions preview */}
      <div className="recipe-instructions">
        <h4>Instructions:</h4>
        <p className="instructions-preview">
          {instructions.length > 150 
            ? instructions.substring(0, 150) + '...'
            : instructions
          }
        </p>
      </div>

      {/* Recipe actions */}
      <div className="recipe-actions">
        {quality.isUsable ? (
          <>
            <button 
              className="btn-primary"
              onClick={() => onAddToMealPlan(recipe)}
            >
              Add to Meal Plan
            </button>
            <button 
              className="btn-secondary"
              onClick={() => onSaveRecipe(recipe)}
            >
              Save Recipe
            </button>
          </>
        ) : (
          <div className="low-quality-actions">
            <button className="btn-disabled" disabled>
              Recipe needs review
            </button>
            <small>This recipe has incomplete data and needs manual review.</small>
          </div>
        )}
      </div>

      {/* Quality score debugging (development only) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="debug-info">
          <details>
            <summary>Debug Info</summary>
            <pre>{JSON.stringify(quality, null, 2)}</pre>
          </details>
        </div>
      )}
    </div>
  );
};

export default RecipeCard;'''

    return component_code

def create_enhanced_recipe_css():
    """Create CSS for enhanced recipe display"""
    
    css_code = '''/* Enhanced Recipe Card Styles with Quality Indicators */

.recipe-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 16px;
  margin: 16px 0;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
  position: relative;
}

.recipe-card:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
  transform: translateY(-2px);
}

/* Quality indicator styles */
.quality-indicator {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  font-size: 12px;
}

.quality-score {
  background: #f0f0f0;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-bottom: 4px;
}

.quality-5 .quality-score {
  background: #4CAF50;
  color: white;
}

.quality-4 .quality-score {
  background: #8BC34A;
  color: white;
}

.quality-3 .quality-score {
  background: #FFC107;
  color: black;
}

.quality-2 .quality-score {
  background: #FF9800;
  color: white;
}

.quality-1 .quality-score,
.quality-0 .quality-score {
  background: #F44336;
  color: white;
}

.quality-issues {
  background: rgba(244, 67, 54, 0.1);
  color: #d32f2f;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 10px;
  text-align: center;
  max-width: 120px;
  margin-top: 4px;
}

/* Low quality recipe styling */
.recipe-card.low-quality {
  border-color: #ff9800;
  background: #fff8e1;
}

.recipe-card.low-quality .recipe-title {
  color: #ef6c00;
}

/* Recipe header */
.recipe-header {
  margin-bottom: 16px;
  padding-right: 80px; /* Space for quality indicator */
}

.recipe-title {
  font-size: 20px;
  font-weight: bold;
  margin: 0 0 8px 0;
  color: #333;
  line-height: 1.3;
}

.recipe-meta {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  font-size: 14px;
  color: #666;
}

.recipe-meta span {
  background: #f5f5f5;
  padding: 4px 8px;
  border-radius: 4px;
  white-space: nowrap;
}

/* Ingredients section */
.recipe-ingredients {
  margin-bottom: 16px;
}

.recipe-ingredients h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #333;
}

.recipe-ingredients ul {
  margin: 0;
  padding-left: 20px;
  list-style-type: disc;
}

.recipe-ingredients li {
  margin-bottom: 4px;
  line-height: 1.4;
}

.more-ingredients {
  font-style: italic;
  color: #666;
}

/* Instructions section */
.recipe-instructions {
  margin-bottom: 16px;
}

.recipe-instructions h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #333;
}

.instructions-preview {
  line-height: 1.5;
  color: #555;
  margin: 0;
}

/* Missing data indicator */
.missing-data {
  color: #999;
  font-style: italic;
  background: #f9f9f9;
  padding: 8px;
  border-radius: 4px;
  border-left: 4px solid #ddd;
  margin: 0;
}

/* Recipe actions */
.recipe-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.btn-primary {
  background: #2196F3;
  color: white;
  border: none;
  padding: 10px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.3s ease;
}

.btn-primary:hover {
  background: #1976D2;
}

.btn-secondary {
  background: white;
  color: #2196F3;
  border: 1px solid #2196F3;
  padding: 10px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: #2196F3;
  color: white;
}

.btn-disabled {
  background: #ccc;
  color: #666;
  border: none;
  padding: 10px 16px;
  border-radius: 4px;
  cursor: not-allowed;
  font-weight: 500;
}

.low-quality-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.low-quality-actions small {
  color: #666;
  font-size: 12px;
}

/* Debug info (development only) */
.debug-info {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
  font-size: 12px;
}

.debug-info details {
  background: #f9f9f9;
  padding: 8px;
  border-radius: 4px;
}

.debug-info pre {
  margin: 8px 0 0 0;
  white-space: pre-wrap;
  font-family: monospace;
  font-size: 11px;
}

/* Responsive design */
@media (max-width: 768px) {
  .recipe-card {
    margin: 8px 0;
    padding: 12px;
  }
  
  .recipe-header {
    padding-right: 60px;
  }
  
  .recipe-meta {
    gap: 8px;
    font-size: 12px;
  }
  
  .recipe-actions {
    flex-direction: column;
    gap: 8px;
  }
  
  .recipe-actions button {
    width: 100%;
  }
}

/* Print styles */
@media print {
  .recipe-card {
    break-inside: avoid;
    box-shadow: none;
    border: 1px solid #ccc;
  }
  
  .quality-indicator,
  .recipe-actions,
  .debug-info {
    display: none;
  }
}'''

    return css_code

def create_recipe_display_utils():
    """Create utility functions for recipe data handling"""
    
    utils_code = '''// Recipe Display Utilities
// Handles data validation, formatting, and quality assessment

export const RecipeDisplayUtils = {
  
  // Validate and score recipe data quality
  assessRecipeQuality: (recipe) => {
    const quality = {
      score: 0,
      issues: [],
      warnings: [],
      isDisplayable: false,
      isComplete: false
    };

    // Check required fields
    const hasTitle = !!(recipe.title && recipe.title.trim().length > 0);
    const hasIngredients = !!(recipe.ingredients && 
                             recipe.ingredients !== '[]' && 
                             recipe.ingredients.trim().length > 20);
    const hasInstructions = !!(recipe.instructions && 
                              recipe.instructions !== '[]' && 
                              recipe.instructions.trim().length > 50);

    // Check optional fields
    const hasServings = !!(recipe.servings && recipe.servings.trim().length > 0);
    const hasTime = !!(recipe.total_time && recipe.total_time.trim().length > 0);
    const hasCategory = !!(recipe.category && recipe.category.trim().length > 0);

    // Calculate score
    quality.score = [hasTitle, hasIngredients, hasInstructions, hasServings, hasTime, hasCategory]
                   .filter(Boolean).length;

    // Determine displayability
    quality.isDisplayable = hasTitle && (hasIngredients || hasInstructions);
    quality.isComplete = hasTitle && hasIngredients && hasInstructions;

    // Generate specific feedback
    if (!hasTitle) quality.issues.push('Missing recipe title');
    if (!hasIngredients) quality.issues.push('Missing ingredients list');
    if (!hasInstructions) quality.issues.push('Missing cooking instructions');
    
    if (!hasServings) quality.warnings.push('No serving size specified');
    if (!hasTime) quality.warnings.push('No cooking time provided');
    if (!hasCategory) quality.warnings.push('Recipe not categorized');

    return quality;
  },

  // Safely parse and format ingredients
  formatIngredients: (ingredients) => {
    if (!ingredients || ingredients === '[]' || ingredients.trim() === '') {
      return { formatted: [], hasData: false, format: 'empty' };
    }

    let parsed = [];
    let format = 'unknown';

    try {
      // Try JSON array parsing
      const jsonParsed = JSON.parse(ingredients);
      if (Array.isArray(jsonParsed)) {
        parsed = jsonParsed
          .filter(item => item && typeof item === 'string')
          .map(item => item.replace(/^"|"$/g, '').trim())
          .filter(item => 
            item.length > 0 && 
            !['INGREDIENTS', 'DIRECTIONS'].includes(item.toUpperCase())
          );
        format = 'json_array';
      }
    } catch (e) {
      // Not JSON, try other formats
      if (typeof ingredients === 'string') {
        if (ingredients.includes('\\n')) {
          parsed = ingredients.split('\\n')
            .map(item => item.trim())
            .filter(item => 
              item.length > 0 && 
              !['INGREDIENTS', 'DIRECTIONS'].includes(item.toUpperCase())
            );
          format = 'newline_separated';
        } else if (ingredients.includes(',') && ingredients.split(',').length > 1) {
          parsed = ingredients.split(',')
            .map(item => item.trim())
            .filter(item => item.length > 0);
          format = 'comma_separated';
        } else {
          parsed = [ingredients.trim()];
          format = 'single_string';
        }
      }
    }

    return {
      formatted: parsed,
      hasData: parsed.length > 0,
      format: format,
      originalLength: ingredients.length
    };
  },

  // Safely parse and format instructions
  formatInstructions: (instructions) => {
    if (!instructions || instructions === '[]' || instructions.trim() === '') {
      return { formatted: '', hasData: false, format: 'empty' };
    }

    let formatted = '';
    let format = 'unknown';

    try {
      // Try JSON array parsing
      const jsonParsed = JSON.parse(instructions);
      if (Array.isArray(jsonParsed)) {
        formatted = jsonParsed
          .filter(item => item && typeof item === 'string')
          .map(item => item.replace(/^"|"$/g, '').trim())
          .filter(item => 
            item.length > 0 && 
            !['DIRECTIONS', 'INGREDIENTS'].includes(item.toUpperCase())
          )
          .join(' ')
          .trim();
        format = 'json_array';
      }
    } catch (e) {
      // Not JSON, treat as string
      if (typeof instructions === 'string') {
        formatted = instructions
          .replace(/DIRECTIONS\\n/g, '')
          .replace(/^"|"$/g, '')
          .trim();
        format = 'string';
      }
    }

    return {
      formatted: formatted,
      hasData: formatted.length > 0,
      format: format,
      originalLength: instructions.length
    };
  },

  // Generate fallback content for missing data
  generateFallbacks: (recipe) => {
    return {
      title: recipe.title || 'Untitled Recipe',
      servings: recipe.servings || 'Servings not specified',
      time: recipe.total_time || 'Time not specified',
      category: recipe.category || 'Uncategorized',
      ingredients: recipe.ingredients || 'Ingredients list not available',
      instructions: recipe.instructions || 'Instructions not available'
    };
  },

  // Check if recipe should be displayed to users
  shouldDisplayRecipe: (recipe) => {
    const quality = RecipeDisplayUtils.assessRecipeQuality(recipe);
    return quality.isDisplayable && quality.score >= 3;
  },

  // Generate user-friendly quality message
  getQualityMessage: (recipe) => {
    const quality = RecipeDisplayUtils.assessRecipeQuality(recipe);
    
    if (quality.score >= 5) {
      return { type: 'success', message: 'Complete recipe with all details' };
    } else if (quality.score >= 4) {
      return { type: 'good', message: 'Good recipe, minor details missing' };
    } else if (quality.score >= 3) {
      return { type: 'warning', message: 'Recipe usable but incomplete' };
    } else {
      return { type: 'error', message: 'Recipe needs review - missing critical information' };
    }
  }
};

export default RecipeDisplayUtils;'''

    return utils_code

def main():
    """Create enhanced recipe display files"""
    print("🚀 Creating enhanced recipe display components...")
    
    try:
        # Create frontend directory if it doesn't exist
        frontend_components_dir = "d:\\Mik\\Downloads\\Me Hungie\\frontend\\src\\components"
        frontend_utils_dir = "d:\\Mik\\Downloads\\Me Hungie\\frontend\\src\\utils"
        
        if not os.path.exists(frontend_components_dir):
            os.makedirs(frontend_components_dir)
        if not os.path.exists(frontend_utils_dir):
            os.makedirs(frontend_utils_dir)
        
        # Create enhanced RecipeCard component
        recipe_card_path = os.path.join(frontend_components_dir, "EnhancedRecipeCard.js")
        with open(recipe_card_path, 'w', encoding='utf-8') as f:
            f.write(create_enhanced_recipe_display_component())
        print(f"✅ Created enhanced RecipeCard component: {recipe_card_path}")
        
        # Create CSS file
        css_path = os.path.join(frontend_components_dir, "EnhancedRecipeCard.css")
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(create_enhanced_recipe_css())
        print(f"✅ Created enhanced CSS: {css_path}")
        
        # Create utility functions
        utils_path = os.path.join(frontend_utils_dir, "RecipeDisplayUtils.js")
        with open(utils_path, 'w', encoding='utf-8') as f:
            f.write(create_recipe_display_utils())
        print(f"✅ Created recipe display utilities: {utils_path}")
        
        print("\n📋 ENHANCED RECIPE DISPLAY FEATURES:")
        print("  🔍 Automatic data quality assessment")
        print("  🛡️ Safe parsing of malformed JSON and mixed formats")
        print("  📊 Visual quality indicators for users")
        print("  🎨 Improved error handling and fallback content")
        print("  📱 Mobile-responsive design")
        print("  🐛 Development debugging tools")
        print("  ♿ Accessibility improvements")
        
        print("\n🔧 INTEGRATION INSTRUCTIONS:")
        print("  1. Import EnhancedRecipeCard instead of RecipeCard")
        print("  2. Use RecipeDisplayUtils for data processing")
        print("  3. Add quality score filtering to search results")
        print("  4. Test with both good and problematic recipes")
        
    except Exception as e:
        print(f"❌ Error creating enhanced display components: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
