/**
 * Node Validators & Normalizers
 * 
 * Ensures all nodes conform to standard structure during refactoring
 * Prevents v1/v2 naming issues and data structure mismatches
 * 
 * These will be removed after migration is complete (Week 4)
 */

// ==========================================
// NODE STRUCTURE CONTRACTS
// ==========================================

/**
 * Standard node structure (v2):
 * {
 *   id: string,              // Format: "recipe-123", "note-456"
 *   type: string,            // "recipeCard", "note", "groceryListNode", etc.
 *   position: { x, y },      // Canvas position (numbers)
 *   data: {
 *     recipe_id: number,     // For recipe nodes - ID only (NOT full object)
 *     object_id: number,     // Whiteboard object ID
 *     tags: string[],        // Tags array
 *     backgroundColor: string, // Hex color
 *     // ... node-specific data
 *   },
 *   style?: Object,          // Optional style overrides
 *   width?: number,          // Optional (meal plans, notes)
 *   height?: number          // Optional (meal plans, notes)
 * }
 */

// ==========================================
// VALIDATION FUNCTIONS
// ==========================================

/**
 * Validate node has all required fields
 * Throws error if invalid
 */
export function validateNode(node) {
  const errors = [];
  
  // Required: id
  if (!node.id || typeof node.id !== 'string') {
    errors.push('Node must have string id');
  }
  
  // Required: type
  if (!node.type || typeof node.type !== 'string') {
    errors.push('Node must have string type');
  }
  
  // Required: position with x and y
  if (!node.position || typeof node.position !== 'object') {
    errors.push('Node must have position object');
  } else {
    if (typeof node.position.x !== 'number') {
      errors.push('Node position.x must be number');
    }
    if (typeof node.position.y !== 'number') {
      errors.push('Node position.y must be number');
    }
  }
  
  // Required: data object
  if (!node.data || typeof node.data !== 'object') {
    errors.push('Node must have data object');
  }
  
  // Type-specific validation
  if (node.type === 'recipeCard') {
    validateRecipeNode(node, errors);
  } else if (node.type === 'note') {
    validateNoteNode(node, errors);
  } else if (node.type === 'groceryListNode') {
    validateGroceryListNode(node, errors);
  } else if (node.type === 'mealPlanContainer') {
    validateMealPlanNode(node, errors);
  }
  
  // If errors, throw
  if (errors.length > 0) {
    console.error('❌ Invalid node structure:', node);
    console.error('Errors:', errors);
    throw new Error(`Invalid node: ${errors.join(', ')}`);
  }
  
  return true;
}

/**
 * Validate recipe node structure
 */
function validateRecipeNode(node, errors) {
  if (!node.data.recipe_id || typeof node.data.recipe_id !== 'number') {
    errors.push('Recipe node must have data.recipe_id (number)');
  }
  
  // Warn if has full recipe object (should use cache instead)
  if (node.data.recipe && typeof node.data.recipe === 'object') {
    console.warn('⚠️ Recipe node has full recipe object - should only store recipe_id and use cache', node.id);
  }
  
  // Warn if has duplicate fields
  if (node.data.name || node.data.title) {
    console.warn('⚠️ Recipe node has name/title in data - should fetch from cache', node.id);
  }
  
  if (node.data.image_url) {
    console.warn('⚠️ Recipe node has image_url in data - should fetch from cache', node.id);
  }
}

/**
 * Validate note node structure
 */
function validateNoteNode(node, errors) {
  if (typeof node.data.name !== 'string') {
    errors.push('Note node must have data.name (string)');
  }
  
  if (typeof node.data.content !== 'string') {
    errors.push('Note node must have data.content (string)');
  }
}

/**
 * Validate grocery list node structure
 */
function validateGroceryListNode(node, errors) {
  if (!node.data.list_id || typeof node.data.list_id !== 'number') {
    errors.push('Grocery list node must have data.list_id (number)');
  }
  
  if (!node.data.name || typeof node.data.name !== 'string') {
    errors.push('Grocery list node must have data.name (string)');
  }
}

/**
 * Validate meal plan node structure
 */
function validateMealPlanNode(node, errors) {
  if (!node.data.mealPlanDbId || typeof node.data.mealPlanDbId !== 'number') {
    errors.push('Meal plan node must have data.mealPlanDbId (number)');
  }
  
  if (typeof node.width !== 'number' || typeof node.height !== 'number') {
    errors.push('Meal plan node must have width and height (numbers)');
  }
}

// ==========================================
// NORMALIZATION FUNCTIONS
// ==========================================

/**
 * Normalize node to standard v2 structure
 * Handles v1 legacy formats and inconsistencies
 */
export function normalizeNode(node) {
  if (!node) {
    throw new Error('Cannot normalize null/undefined node');
  }
  
  // Start with base structure
  const normalized = {
    id: node.id,
    type: node.type,
    position: normalizePosition(node.position),
    data: { ...node.data }
  };
  
  // Type-specific normalization
  if (node.type === 'recipeCard') {
    normalized.data = normalizeRecipeNodeData(node.data);
  } else if (node.type === 'note') {
    normalized.data = normalizeNoteNodeData(node.data);
    normalized.style = node.style || { width: 300, height: 250 };
  } else if (node.type === 'mealPlanContainer') {
    normalized.width = node.width || 400;
    normalized.height = node.height || 500;
  }
  
  return normalized;
}

/**
 * Normalize position (handles array format from v1)
 */
function normalizePosition(position) {
  // Array format: [x, y, width, height]
  if (Array.isArray(position)) {
    return {
      x: position[0] || 0,
      y: position[1] || 0
    };
  }
  
  // Object format: { x, y }
  if (position && typeof position === 'object') {
    return {
      x: position.x ?? 0,
      y: position.y ?? 0
    };
  }
  
  // Default
  return { x: 0, y: 0 };
}

/**
 * Normalize recipe node data
 * Removes duplicate data, ensures only recipe_id is stored
 */
function normalizeRecipeNodeData(data) {
  const normalized = {
    recipe_id: data.recipe_id || data.recipe?.id,
    object_id: data.object_id,
    tags: data.tags || [],
    backgroundColor: data.backgroundColor || '#FFFFFF',
    commentCount: data.commentCount || 0,
    hasNewComments: data.hasNewComments || false,
    
    // Preserve handlers
    onClick: data.onClick,
    onDelete: data.onDelete,
    onTagsChange: data.onTagsChange,
    onColorChange: data.onColorChange,
    onTagFilterClick: data.onTagFilterClick
  };
  
  // Remove duplicate fields
  // These should come from recipe cache, not node data
  const fieldsToRemove = [
    'recipe',      // Full recipe object (use cache!)
    'name',        // Duplicate of recipe.title
    'title',       // Duplicate of recipe.title
    'image_url',   // Duplicate of recipe.image_url
    'prep_time',   // Duplicate of recipe.prep_time
    'cook_time',   // Duplicate of recipe.cook_time
    'total_time',  // Duplicate of recipe.total_time
    'category'     // Duplicate of recipe.category
  ];
  
  fieldsToRemove.forEach(field => {
    if (data[field]) {
      console.log(`🧹 Removing duplicate field from recipe node: ${field}`);
    }
  });
  
  return normalized;
}

/**
 * Normalize note node data
 */
function normalizeNoteNodeData(data) {
  // Handle content that might be in different formats
  let content = data.content;
  
  // If content is object with html property (v1 format)
  if (content && typeof content === 'object' && content.html) {
    content = content.html;
  }
  
  return {
    object_id: data.object_id || data.objectId,
    name: data.name || 'Untitled Note',
    content: content || '<p></p>',
    backgroundColor: data.backgroundColor || '#FEF3C7',
    fontSize: data.fontSize || '18px',
    commentCount: data.commentCount || 0,
    createdBy: data.createdBy || 'Unknown',
    
    // Preserve handlers
    onDelete: data.onDelete,
    onSave: data.onSave
  };
}

// ==========================================
// COMPARISON UTILITIES (for parallel validation)
// ==========================================

/**
 * Compare two node arrays and log differences
 * Used during migration to ensure old and new match
 */
export function compareNodeArrays(oldNodes, newNodes, label = 'Nodes') {
  const differences = [];
  
  // Check counts
  if (oldNodes.length !== newNodes.length) {
    differences.push(`Count mismatch: old=${oldNodes.length}, new=${newNodes.length}`);
  }
  
  // Compare each node
  const maxLength = Math.max(oldNodes.length, newNodes.length);
  for (let i = 0; i < maxLength; i++) {
    const oldNode = oldNodes[i];
    const newNode = newNodes[i];
    
    if (!oldNode && newNode) {
      differences.push(`Index ${i}: New node added: ${newNode.id}`);
    } else if (oldNode && !newNode) {
      differences.push(`Index ${i}: Old node missing: ${oldNode.id}`);
    } else if (oldNode && newNode) {
      // Compare IDs
      if (oldNode.id !== newNode.id) {
        differences.push(`Index ${i}: ID mismatch: ${oldNode.id} vs ${newNode.id}`);
      }
      
      // Compare types
      if (oldNode.type !== newNode.type) {
        differences.push(`Index ${i}: Type mismatch: ${oldNode.type} vs ${newNode.type}`);
      }
      
      // Compare positions
      if (oldNode.position?.x !== newNode.position?.x || 
          oldNode.position?.y !== newNode.position?.y) {
        differences.push(`Index ${i}: Position mismatch for ${oldNode.id}`);
      }
    }
  }
  
  // Log results
  if (differences.length > 0) {
    console.error(`❌ ${label} mismatch:`, differences);
    return false;
  } else {
    console.log(`✅ ${label} match perfectly`);
    return true;
  }
}

/**
 * Deep comparison of node data structures
 */
export function compareNodeData(oldNode, newNode) {
  if (!oldNode || !newNode) return false;
  
  const differences = [];
  
  // Compare basic fields
  ['id', 'type'].forEach(field => {
    if (oldNode[field] !== newNode[field]) {
      differences.push(`${field}: ${oldNode[field]} vs ${newNode[field]}`);
    }
  });
  
  // Compare data object keys
  const oldKeys = Object.keys(oldNode.data || {});
  const newKeys = Object.keys(newNode.data || {});
  
  const missingInNew = oldKeys.filter(k => !newKeys.includes(k));
  const missingInOld = newKeys.filter(k => !oldKeys.includes(k));
  
  if (missingInNew.length > 0) {
    differences.push(`Missing in new: ${missingInNew.join(', ')}`);
  }
  
  if (missingInOld.length > 0) {
    differences.push(`New fields: ${missingInOld.join(', ')}`);
  }
  
  if (differences.length > 0) {
    console.warn(`⚠️ Node data differences for ${oldNode.id}:`, differences);
    return false;
  }
  
  return true;
}
