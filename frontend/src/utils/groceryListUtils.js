/**
 * Grocery List Utilities
 * ======================
 * Smart ingredient consolidation and merging logic
 * Extracted from GroceryManagerWorkspace for reuse
 * 
 * Author: GitHub Copilot
 * Date: November 4, 2025
 */

// Extract quantity from ingredient name
export const extractQuantityFromName = (name) => {
  const quantityMatch = name.match(/^(\d+(?:\.\d+)?)\s*(\w+)/);
  if (quantityMatch) {
    return {
      amount: parseFloat(quantityMatch[1]),
      unit: quantityMatch[2].toLowerCase()
    };
  }
  return null;
};

// Normalize units for comparison
export const normalizeUnit = (unit) => {
  const unitMap = {
    'cup': 'cup', 'cups': 'cup',
    'tbsp': 'tbsp', 'tablespoon': 'tbsp', 'tablespoons': 'tbsp',
    'tsp': 'tsp', 'teaspoon': 'tsp', 'teaspoons': 'tsp',
    'oz': 'oz', 'ounce': 'oz', 'ounces': 'oz',
    'lb': 'lb', 'lbs': 'lb', 'pound': 'lb', 'pounds': 'lb',
    'g': 'g', 'gram': 'g', 'grams': 'g',
    'kg': 'kg', 'kilogram': 'kg', 'kilograms': 'kg',
    'ml': 'ml', 'milliliter': 'ml', 'milliliters': 'ml',
    'l': 'l', 'liter': 'l', 'liters': 'l',
    'clove': 'clove', 'cloves': 'clove',
    'piece': 'piece', 'pieces': 'piece',
    'slice': 'slice', 'slices': 'slice',
    'pinch': 'pinch', 'pinches': 'pinch',
    'bunch': 'bunch', 'bunches': 'bunch',
    'can': 'can', 'cans': 'can'
  };
  return unitMap[unit.toLowerCase()] || unit.toLowerCase();
};

// Combine quantities with same units
export const combineQuantities = (quantities) => {
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

// Extract core ingredient from complex recipe descriptions
export const extractCoreIngredient = (complexName) => {
  // Remove quantities and measurements
  let core = complexName
    // Remove leading fractions and quantities
    .replace(/^[\d\/¼½¾⅓⅔⅛⅜⅝⅞]+\s*/i, '')
    // Remove quantities with units
    .replace(/^\d+(\.\d+)?\s*(lb|lbs|pound|pounds|oz|ounces?|cup|cups|tbsp|tsp|tablespoons?|teaspoons?|cloves?|pieces?|slices?|bunch|bunches?|can|cans?|pinch|pinches?)\s+/i, '')
    // Remove standalone units
    .replace(/^(teaspoons?|tablespoons?|cups?|tbsp\.?|tsp\.?|lb\.?|lbs\.?|oz\.?|ounces?|pounds?|cloves?|pieces?|slices?|bunch|bunches?|can|cans?|pinch|pinches?)\s+/i, '')
    // Remove any remaining quantities
    .replace(/\d+(\.\d+)?\s*(lb\.?|lbs\.?|oz\.?|ounces?|cup\.?|cups\.?|tbsp\.?|tsp\.?|tablespoons?|teaspoons?|cloves?|pieces?|slices?)/gi, '');
  
  // Smart parentheses handling
  const parenMatch = core.match(/^([^(]*)\(([^)]*)\)/);
  if (parenMatch) {
    const beforeParens = parenMatch[1].trim();
    const insideParens = parenMatch[2].trim();
    
    const ingredientWords = ['chicken', 'beef', 'pork', 'fish', 'salmon', 'turkey', 'lamb', 
                            'bread', 'flour', 'rice', 'pasta', 'cheese', 'milk', 'butter', 
                            'oil', 'tomato', 'onion', 'garlic', 'mushroom', 'pepper', 'salt'];
    
    const insideHasIngredient = ingredientWords.some(word => insideParens.toLowerCase().includes(word));
    const beforeHasIngredient = ingredientWords.some(word => beforeParens.toLowerCase().includes(word));
    
    if (insideHasIngredient && !beforeHasIngredient) {
      core = insideParens;
    } else {
      core = beforeParens;
    }
  } else {
    core = core.replace(/\([^)]*\)/g, '');
  }
  
  // Remove common descriptive words
  core = core
    .replace(/\b(finely|coarsely|roughly|fresh|dried|frozen|organic|chopped|diced|sliced|minced|grated|shredded|boneless|skinless|as needed)\b/gi, '')
    .replace(/[,\-\.]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
  
  // Keep compound ingredients intact (e.g., "salt and pepper")
  const lowerCore = core.toLowerCase();
  if (lowerCore.includes(' and ') || lowerCore.includes(' & ') || lowerCore.includes(', ')) {
    return core.trim() || complexName;
  }
  
  // Take first meaningful words
  const words = core.split(' ').filter(word => word.length > 2);
  if (words.length <= 4) {
    core = words.join(' ');
  } else {
    core = words.slice(0, 3).join(' ');
  }
  
  return core.trim() || complexName;
};

// Check if two ingredients are similar
export const areIngredientsSimilar = (name1, name2) => {
  const core1 = extractCoreIngredient(name1).toLowerCase();
  const core2 = extractCoreIngredient(name2).toLowerCase();
  
  // Exact match
  if (core1 === core2) return true;
  
  // One contains the other
  if (core1.includes(core2) || core2.includes(core1)) return true;
  
  // Special cases for common variations
  const variations = {
    'tomato': ['tomatoes', 'cherry tomato', 'roma tomato'],
    'onion': ['onions', 'yellow onion', 'white onion', 'red onion'],
    'pepper': ['peppers', 'bell pepper', 'jalapeño'],
    'chicken': ['chicken breast', 'chicken thigh', 'chicken wing'],
    'oil': ['olive oil', 'vegetable oil', 'cooking oil'],
  };
  
  for (const [base, vars] of Object.entries(variations)) {
    if ((core1.includes(base) || vars.some(v => core1.includes(v))) &&
        (core2.includes(base) || vars.some(v => core2.includes(v)))) {
      return true;
    }
  }
  
  return false;
};

// Main consolidation function
export const consolidateSimilarItems = (items) => {
  const allRecipes = [...new Set(items.flatMap(item => item.recipes || item.source_recipes || []))];
  const quantities = [];
  let baseName = '';
  
  // Extract quantities and find the most complete name
  items.forEach(item => {
    const itemName = item.name || item.ingredient || item.item || '';
    const quantity = extractQuantityFromName(itemName);
    if (quantity) {
      quantities.push(quantity);
    }
    
    // Use the longest name as base (likely most descriptive)
    if (itemName.length > baseName.length) {
      baseName = itemName;
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
    ingredient: finalName,
    name: finalName,
    recipes: allRecipes,
    source_recipes: allRecipes,
    isCustom: false,
    isConsolidated: true,
    originalItems: items.length,
    checked: false
  };
};

// Consolidate all ingredients intelligently
export const consolidateIngredients = (ingredients) => {
  const grouped = {};

  ingredients.forEach(ing => {
    // Handle different ingredient formats
    let ingredientName = '';
    
    if (typeof ing === 'string') {
      ingredientName = ing;
    } else if (typeof ing === 'object') {
      ingredientName = ing.ingredient || ing.name || ing.item || '';
    }

    if (!ingredientName) return;

    // Extract core ingredient
    const core = extractCoreIngredient(ingredientName);
    const normalizedCore = core.toLowerCase();

    // Find if we already have a similar ingredient
    let foundMatch = false;
    for (const [key, group] of Object.entries(grouped)) {
      if (areIngredientsSimilar(normalizedCore, key)) {
        group.push({
          ...ing,
          name: ingredientName,
          ingredient: ingredientName,
          recipes: ing.source_recipes || [ing.source_recipe_name] || []
        });
        foundMatch = true;
        break;
      }
    }

    if (!foundMatch) {
      grouped[normalizedCore] = [{
        ...ing,
        name: ingredientName,
        ingredient: ingredientName,
        recipes: ing.source_recipes || [ing.source_recipe_name] || []
      }];
    }
  });

  // Consolidate each group
  const consolidated = [];
  for (const items of Object.values(grouped)) {
    if (items.length > 1) {
      consolidated.push(consolidateSimilarItems(items));
    } else {
      // Single item - just format it properly
      const item = items[0];
      consolidated.push({
        id: `item-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        ingredient: item.name || item.ingredient,
        name: item.name || item.ingredient,
        quantity: item.quantity || '',
        unit: item.unit || '',
        checked: false,
        source_recipes: item.recipes || [item.source_recipe_name] || [],
        count: 1
      });
    }
  }

  return consolidated;
};
