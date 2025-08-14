/**
 * Intent Classification System for Recipe Intelligence
 * Replaces hardcoded search mappings with intelligent query understanding
 */

// Intent types that our system can recognize
export const INTENT_TYPES = {
  RECIPE_SEARCH: 'recipe_search',           // "chicken recipes", "pasta dishes"
  MEAL_PLANNING: 'meal_planning',           // "what should I make for dinner?"
  INGREDIENT_SUBSTITUTION: 'substitution', // "can I use honey instead of sugar?"
  COOKING_GUIDANCE: 'guidance',             // "how do I properly sear beef?"
  DIETARY_FILTERING: 'dietary',             // "gluten-free desserts"
  OCCASION_BASED: 'occasion',               // "easy weeknight meals", "party food"
  NUTRITIONAL_INFO: 'nutrition',            // "low-carb lunch ideas"
  TECHNIQUE_LEARNING: 'technique',          // "how to make perfect pasta"
  COMPLETE_MEAL: 'complete_meal'            // "side dishes", "appetizers for chicken"
};

// Context patterns for detecting user situations
export const CONTEXT_PATTERNS = {
  TIME_CONSTRAINTS: {
    patterns: ['quick', 'fast', '30 minutes', '20 minutes', 'weeknight', 'busy', 'rushed', 'express'],
    weight: 0.8
  },
  SKILL_LEVEL: {
    patterns: ['easy', 'beginner', 'simple', 'basic', 'advanced', 'complex', 'professional', 'expert'],
    weight: 0.7
  },
  SERVING_SIZE: {
    patterns: ['for two', 'for 2', 'family', 'party', 'large group', 'single serving', 'crowd', 'dinner party'],
    weight: 0.6
  },
  DIETARY_NEEDS: {
    patterns: ['vegetarian', 'vegan', 'gluten-free', 'gluten free', 'keto', 'low-carb', 'low carb', 'dairy-free', 'nut-free'],
    weight: 0.9
  },
  MEAL_TYPE: {
    patterns: ['breakfast', 'lunch', 'dinner', 'snack', 'appetizer', 'appetizers', 'dessert', 'desserts', 'main course', 'side dish', 'side dishes'],
    weight: 0.8
  },
  OCCASION: {
    patterns: ['romantic', 'entertaining', 'comfort food', 'healthy', 'indulgent', 'party', 'holiday', 'special occasion'],
    weight: 0.7
  },
  COOKING_METHOD: {
    patterns: ['grilled', 'baked', 'fried', 'steamed', 'roasted', 'sautéed', 'braised', 'slow cooked', 'instant pot'],
    weight: 0.6
  }
};

// Intent classification patterns
const INTENT_PATTERNS = {
  [INTENT_TYPES.MEAL_PLANNING]: {
    patterns: [
      'what should i make',
      'what to cook',
      'meal ideas',
      'dinner ideas',
      'lunch ideas',
      'breakfast ideas',
      'what\'s for dinner',
      'help me decide',
      'suggest something',
      'what can i cook'
    ],
    weight: 0.9
  },
  [INTENT_TYPES.INGREDIENT_SUBSTITUTION]: {
    patterns: [
      'substitute',
      'replace',
      'instead of',
      'alternative to',
      'swap',
      'use instead',
      'don\'t have',
      'out of',
      'can i use'
    ],
    weight: 0.95
  },
  [INTENT_TYPES.COOKING_GUIDANCE]: {
    patterns: [
      'how to',
      'how do i',
      'technique',
      'method',
      'properly',
      'best way',
      'tips for',
      'guide',
      'instructions'
    ],
    weight: 0.9
  },
  [INTENT_TYPES.COMPLETE_MEAL]: {
    patterns: [
      'side dishes',
      'side dish',
      'sides',
      'appetizers',
      'appetizer',
      'starters',
      'goes well with',
      'serve with',
      'complement',
      'pair with'
    ],
    weight: 0.85
  },
  [INTENT_TYPES.OCCASION_BASED]: {
    patterns: [
      'weeknight',
      'date night',
      'party food',
      'entertaining',
      'holiday',
      'special occasion',
      'comfort food',
      'healthy meals'
    ],
    weight: 0.8
  },
  [INTENT_TYPES.DIETARY_FILTERING]: {
    patterns: [
      'vegetarian',
      'vegan',
      'gluten-free',
      'keto',
      'low-carb',
      'dairy-free',
      'sugar-free',
      'paleo'
    ],
    weight: 0.9
  },
  [INTENT_TYPES.RECIPE_SEARCH]: {
    patterns: [
      'recipe',
      'recipes',
      'dish',
      'dishes',
      'cook',
      'make',
      'prepare'
    ],
    weight: 0.3 // Lower weight as this is the default fallback
  }
};

/**
 * Classify user intent from their query
 * @param {string} query - User's input query
 * @returns {Object} - Intent classification result
 */
export const classifyIntent = (query) => {
  const lowerQuery = query.toLowerCase().trim();
  const intentScores = {};
  
  // Calculate scores for each intent type
  Object.entries(INTENT_PATTERNS).forEach(([intent, config]) => {
    let score = 0;
    let matchCount = 0;
    
    config.patterns.forEach(pattern => {
      if (lowerQuery.includes(pattern)) {
        score += config.weight;
        matchCount++;
      }
    });
    
    // Normalize score by pattern matches
    if (matchCount > 0) {
      intentScores[intent] = (score / config.patterns.length) * matchCount;
    }
  });
  
  // Find the highest scoring intent
  const topIntent = Object.entries(intentScores).reduce((top, [intent, score]) => {
    return score > top.score ? { intent, score } : top;
  }, { intent: INTENT_TYPES.RECIPE_SEARCH, score: 0 });
  
  return {
    intent: topIntent.intent,
    confidence: Math.min(topIntent.score, 1.0),
    allScores: intentScores,
    isHighConfidence: topIntent.score > 0.7
  };
};

/**
 * Extract context information from user query
 * @param {string} query - User's input query
 * @returns {Object} - Extracted context information
 */
export const extractContext = (query) => {
  const lowerQuery = query.toLowerCase().trim();
  const context = {
    timeConstraint: null,
    skillLevel: null,
    servingSize: null,
    dietaryNeeds: [],
    mealType: null,
    occasion: null,
    cookingMethod: null,
    contextScore: 0
  };
  
  // Extract context patterns
  Object.entries(CONTEXT_PATTERNS).forEach(([contextType, config]) => {
    config.patterns.forEach(pattern => {
      if (lowerQuery.includes(pattern)) {
        const key = contextType.toLowerCase().replace('_', '');
        
        switch (contextType) {
          case 'TIME_CONSTRAINTS':
            context.timeConstraint = pattern;
            break;
          case 'SKILL_LEVEL':
            context.skillLevel = pattern;
            break;
          case 'SERVING_SIZE':
            context.servingSize = pattern;
            break;
          case 'DIETARY_NEEDS':
            context.dietaryNeeds.push(pattern);
            break;
          case 'MEAL_TYPE':
            context.mealType = pattern;
            break;
          case 'OCCASION':
            context.occasion = pattern;
            break;
          case 'COOKING_METHOD':
            context.cookingMethod = pattern;
            break;
        }
        
        context.contextScore += config.weight;
      }
    });
  });
  
  return context;
};

/**
 * Get smart search suggestions based on intent and context
 * @param {string} intent - Classified intent
 * @param {Object} context - Extracted context
 * @param {string} originalQuery - Original user query
 * @returns {Object} - Smart search suggestions
 */
export const getSmartSearchSuggestions = (intent, context, originalQuery) => {
  const suggestions = {
    searchTerms: [],
    filters: {},
    searchStrategy: 'standard',
    fallbackQueries: []
  };
  
  switch (intent) {
    case INTENT_TYPES.COMPLETE_MEAL:
      // Handle side dishes, appetizers, etc.
      if (context.mealType === 'side dishes' || context.mealType === 'side dish') {
        suggestions.searchTerms = ['potato', 'rice', 'beans', 'vegetables', 'corn', 'coleslaw'];
        suggestions.searchStrategy = 'side_dishes';
        suggestions.fallbackQueries = ['potato salad', 'baked beans', 'grilled vegetables'];
      } else if (context.mealType === 'appetizers' || context.mealType === 'appetizer') {
        suggestions.searchTerms = ['chicken wings', 'scallops', 'bruschetta', 'dips'];
        suggestions.searchStrategy = 'appetizers';
        suggestions.fallbackQueries = ['chicken wings', 'party appetizers', 'finger foods'];
      }
      break;
      
    case INTENT_TYPES.MEAL_PLANNING:
      // Suggest based on meal type and context
      if (context.mealType) {
        suggestions.searchTerms = [context.mealType];
      } else if (context.timeConstraint) {
        suggestions.searchTerms = ['quick', 'easy', '30 minute'];
      } else {
        suggestions.searchTerms = ['dinner', 'main course'];
      }
      suggestions.searchStrategy = 'meal_planning';
      break;
      
    case INTENT_TYPES.OCCASION_BASED:
      if (context.occasion) {
        suggestions.searchTerms = [context.occasion];
      }
      if (context.timeConstraint) {
        suggestions.searchTerms.push(context.timeConstraint);
      }
      suggestions.searchStrategy = 'occasion_based';
      break;
      
    case INTENT_TYPES.DIETARY_FILTERING:
      suggestions.searchTerms = context.dietaryNeeds;
      suggestions.filters.dietary = context.dietaryNeeds;
      suggestions.searchStrategy = 'dietary_filtered';
      break;
      
    default:
      // Extract ingredient/food terms from the original query
      suggestions.searchTerms = extractFoodTerms(originalQuery);
      suggestions.searchStrategy = 'standard';
  }
  
  // Add context-based filters
  if (context.timeConstraint) {
    suggestions.filters.timeConstraint = context.timeConstraint;
  }
  if (context.skillLevel) {
    suggestions.filters.skillLevel = context.skillLevel;
  }
  if (context.cookingMethod) {
    suggestions.filters.cookingMethod = context.cookingMethod;
  }
  
  return suggestions;
};

/**
 * Extract food/ingredient terms from query
 * @param {string} query - User query
 * @returns {Array} - Array of food terms
 */
const extractFoodTerms = (query) => {
  const lowerQuery = query.toLowerCase();
  
  // Common food keywords - expanded from your existing logic
  const foodKeywords = [
    'chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'shrimp', 'turkey',
    'pasta', 'spaghetti', 'linguine', 'penne', 'rice', 'quinoa', 'bread',
    'tomato', 'potato', 'onion', 'garlic', 'mushroom', 'spinach', 'carrot',
    'cheese', 'mozzarella', 'parmesan', 'cheddar', 'cream', 'butter',
    'basil', 'oregano', 'thyme', 'rosemary', 'pepper', 'salt', 'paprika',
    'dessert', 'cake', 'cookies', 'pie', 'chocolate', 'vanilla', 'sugar',
    'soup', 'salad', 'sandwich', 'pizza', 'burger', 'tacos', 'curry',
    'stir', 'fry', 'grill', 'bake', 'roast', 'steam', 'braise'
  ];
  
  const words = lowerQuery.split(/\s+/);
  const foundTerms = [];
  
  words.forEach(word => {
    const cleaned = word.replace(/[^\w]/g, '');
    if (foodKeywords.includes(cleaned) && !foundTerms.includes(cleaned)) {
      foundTerms.push(cleaned);
    }
  });
  
  return foundTerms.length > 0 ? foundTerms : [lowerQuery.split(' ')[0]];
};

/**
 * Main function to process user query with intent classification
 * @param {string} userQuery - User's input
 * @returns {Object} - Complete analysis of user intent and context
 */
export const analyzeUserQuery = (userQuery) => {
  const intentResult = classifyIntent(userQuery);
  const context = extractContext(userQuery);
  const searchSuggestions = getSmartSearchSuggestions(intentResult.intent, context, userQuery);
  
  return {
    originalQuery: userQuery,
    intent: intentResult.intent,
    confidence: intentResult.confidence,
    isHighConfidence: intentResult.isHighConfidence,
    context,
    searchSuggestions,
    allIntentScores: intentResult.allScores,
    debugInfo: {
      extractedTerms: searchSuggestions.searchTerms,
      searchStrategy: searchSuggestions.searchStrategy,
      contextScore: context.contextScore
    }
  };
};

export default {
  classifyIntent,
  extractContext,
  getSmartSearchSuggestions,
  analyzeUserQuery,
  INTENT_TYPES,
  CONTEXT_PATTERNS
};
