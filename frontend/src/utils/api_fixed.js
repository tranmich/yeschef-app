// API Configuration and Utilities

// Environment-based API URL with production fallback
const getApiUrl = () => {
  // Production Railway backend URL
  if (process.env.NODE_ENV === 'production') {
    return 'https://yeschefapp-production.up.railway.app';
  }
  
  // Development fallback
  return 'http://localhost:5000';
};

const API_BASE_URL = getApiUrl();

console.log('🚀 API Configuration [UPDATED]:', {
  API_BASE_URL,
  environment: process.env.NODE_ENV,
  production: process.env.NODE_ENV === 'production',
  envVar: process.env.REACT_APP_API_URL,
  finalUrl: API_BASE_URL,
  timestamp: new Date().toISOString()
});
console.log('ðŸš€ API Configuration [UPDATED]:', {
  API_BASE_URL,
  environment: process.env.NODE_ENV,
  production: process.env.NODE_ENV === 'production',
  envVar: process.env.REACT_APP_API_URL,
  finalUrl: API_BASE_URL,
  timestamp: new Date().toISOString()
});

export const apiCall = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  console.log('ðŸ“¡ API Call:', { url, method: options.method || 'GET' });
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const mergedOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, mergedOptions);
    
    console.log('ðŸ“¡ API Response:', { 
      url, 
      status: response.status, 
      statusText: response.statusText,
      contentType: response.headers.get('content-type')
    });
    
    if (!response.ok) {
      // Try to get error details
      const errorText = await response.text();
      console.error('âŒ API Error Details:', { 
        status: response.status, 
        statusText: response.statusText,
        responseText: errorText.substring(0, 500),
        url: url
      });
      throw new Error(`API call failed: ${response.status} ${response.statusText} - ${errorText.substring(0, 100)}`);
    }
    
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      const textResponse = await response.text();
      console.error('âŒ Non-JSON Response:', {
        contentType,
        url,
        responseText: textResponse.substring(0, 500),
        fullResponse: textResponse
      });
      throw new Error('Expected JSON response but got: ' + contentType + '. Response: ' + textResponse.substring(0, 100));
    }
    
    return await response.json();
  } catch (error) {
    console.error('ðŸ’¥ API call error:', error);
    throw error;
  }
};

export const api = {
  // Recipe endpoints
  getRecipe: (id) => apiCall(`/api/recipes/${id}`),
  analyzeRecipe: (id) => apiCall(`/api/recipes/${id}/analyze`),
  searchRecipes: (query) => apiCall(`/api/search?q=${encodeURIComponent(query)}`),
  enhancedSearchRecipes: (query, limit = 20) => apiCall(`/api/recipes/enhanced-search?q=${encodeURIComponent(query)}&limit=${limit}`),
  getRecipeRecommendations: (recipeId, limit = 5) => apiCall(`/api/recipes/${recipeId}/recommendations?limit=${limit}`),
  getCategories: () => apiCall('/api/categories'),
  
  // AI Chat endpoints
  smartSearch: (message, context = '', options = {}) => apiCall('/api/smart-search', {
    method: 'POST',
    body: JSON.stringify({ 
      message, 
      context,
      skipRecipeSearch: options.skipRecipeSearch || false
    }),
  }),
  
  // Substitution endpoints
  getSubstitution: (ingredient, recipeContext = '') => apiCall('/api/substitutions', {
    method: 'POST',
    body: JSON.stringify({ ingredient, recipe_context: recipeContext }),
  }),
  
  getBulkSubstitutions: (ingredients, recipeContext = '') => apiCall('/api/substitutions/bulk', {
    method: 'POST',
    body: JSON.stringify({ ingredients, recipe_context: recipeContext }),
  }),
  
  browseSubstitutions: () => apiCall('/api/substitutions/browse'),
  
  // Advanced FlavorProfile System endpoints
  getIngredientSuggestions: (ingredients, options = {}) => apiCall('/api/flavor-profile/suggestions', {
    method: 'POST',
    body: JSON.stringify({ 
      ingredients, 
      limit: options.limit || 10,
      cooking_method: options.cookingMethod,
      season: options.season 
    }),
  }),
  
  checkIngredientCompatibility: (ingredient1, ingredient2, options = {}) => apiCall('/api/flavor-profile/compatibility', {
    method: 'POST',
    body: JSON.stringify({ 
      ingredient1, 
      ingredient2,
      cooking_method: options.cookingMethod,
      season: options.season 
    }),
  }),
  
  analyzeRecipeHarmony: (ingredients, options = {}) => apiCall('/api/flavor-profile/recipe-harmony', {
    method: 'POST',
    body: JSON.stringify({ 
      ingredients,
      cooking_method: options.cookingMethod,
      season: options.season 
    }),
  }),
  
  enhanceRecipe: (recipe) => apiCall('/api/flavor-profile/enhance-recipe', {
    method: 'POST',
    body: JSON.stringify({ recipe }),
  }),

  // Recipe formatting endpoint - AI chef inspection
  formatRecipe: (recipeData) => apiCall('/api/smart-search', {
    method: 'POST',
    body: JSON.stringify({ 
      message: `Please clean and organize this recipe data while PRESERVING ALL MEASUREMENTS AND QUANTITIES exactly as they are. Only separate ingredients from instructions that got mixed together, and remove section headers. Do not change any numbers, weights, or measurements.

IMPORTANT: Keep all ingredient amounts exactly the same (don't change grams, pounds, cups, etc.)

Recipe to clean:
Title: ${recipeData.title}

Raw Ingredients: ${recipeData.ingredients}

Raw Instructions: ${recipeData.instructions}

Please format as:
INGREDIENTS:
[list each ingredient on its own line with original measurements]

INSTRUCTIONS:
[list each step clearly separated]`,
      context: 'recipe_formatting'
    }),
  }),
};

export default api;
