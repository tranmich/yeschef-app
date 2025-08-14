/**
 * Smart Query Builder - Replaces hardcoded search mappings
 * Builds intelligent search queries based on intent and context
 */

import { INTENT_TYPES } from './IntentClassifier.js';

/**
 * Build intelligent search query based on analysis
 * @param {Object} analysis - Result from analyzeUserQuery
 * @param {Object} sessionMemory - Session memory manager instance
 * @returns {Object} - Smart query configuration
 */
export const buildSmartQuery = async (analysis, sessionMemory = null) => {
  const { intent, context, searchSuggestions, originalQuery } = analysis;
  
  // Get variation strategy if session memory is available
  let variationStrategy = { isRepeatSearch: false };
  if (sessionMemory) {
    variationStrategy = sessionMemory.getRecipeVariationStrategy(originalQuery, analysis);
  }
  
  // Use variation query if this is a repeat search
  let finalSearchTerms = searchSuggestions.searchTerms;
  let finalFilters = searchSuggestions.filters;
  
  if (variationStrategy.isRepeatSearch && sessionMemory) {
    const variationQuery = sessionMemory.buildVariationQuery(originalQuery, analysis, variationStrategy);
    if (variationQuery) {
      finalSearchTerms = variationQuery.searchTerms;
      finalFilters = { ...finalFilters, ...variationQuery.variationModifiers };
    }
  }
  
  const smartQuery = {
    searchTerms: finalSearchTerms,
    searchStrategy: variationStrategy.isRepeatSearch ? variationStrategy.strategy : searchSuggestions.searchStrategy,
    filters: finalFilters,
    fallbackQueries: searchSuggestions.fallbackQueries,
    aiPromptContext: buildAIPromptContext(intent, context),
    searchPhases: buildSearchPhases(intent, context, { 
      ...searchSuggestions, 
      searchTerms: finalSearchTerms 
    }),
    variationStrategy: variationStrategy,
    excludeRecipeIds: variationStrategy.excludeRecipeIds || []
  };
  
  return smartQuery;
};

/**
 * Build context for AI prompting
 * @param {string} intent - User intent
 * @param {Object} context - User context
 * @returns {Object} - AI prompt context
 */
const buildAIPromptContext = (intent, context) => {
  const promptContext = {
    userIntent: intent,
    responseStyle: 'enthusiastic_chef',
    shouldSuggestRecipes: true,
    shouldSuggestComplements: false,
    focus: 'recipe_discovery'
  };
  
  switch (intent) {
    case INTENT_TYPES.MEAL_PLANNING:
      promptContext.responseStyle = 'helpful_planner';
      promptContext.shouldSuggestComplements = true;
      promptContext.focus = 'meal_planning';
      break;
      
    case INTENT_TYPES.COMPLETE_MEAL:
      promptContext.shouldSuggestComplements = true;
      promptContext.focus = 'complementary_dishes';
      break;
      
    case INTENT_TYPES.COOKING_GUIDANCE:
      promptContext.responseStyle = 'expert_teacher';
      promptContext.shouldSuggestRecipes = false;
      promptContext.focus = 'technique_guidance';
      break;
      
    case INTENT_TYPES.INGREDIENT_SUBSTITUTION:
      promptContext.responseStyle = 'knowledgeable_advisor';
      promptContext.shouldSuggestRecipes = false;
      promptContext.focus = 'substitution_advice';
      break;
  }
  
  // Add context modifiers
  if (context.timeConstraint) {
    promptContext.timeConstraint = context.timeConstraint;
  }
  if (context.skillLevel) {
    promptContext.skillLevel = context.skillLevel;
  }
  if (context.dietaryNeeds?.length > 0) {
    promptContext.dietaryNeeds = context.dietaryNeeds;
  }
  
  return promptContext;
};

/**
 * Build multi-phase search strategy
 * @param {string} intent - User intent
 * @param {Object} context - User context
 * @param {Object} searchSuggestions - Search suggestions
 * @returns {Array} - Array of search phases to try
 */
const buildSearchPhases = (intent, context, searchSuggestions) => {
  const phases = [];
  
  // Phase 1: Primary search based on intent
  phases.push({
    phase: 'primary',
    searchTerms: searchSuggestions.searchTerms,
    strategy: searchSuggestions.searchStrategy,
    minResults: getMinResults(intent),
    description: 'Primary search based on user intent'
  });
  
  // Phase 2: Fallback searches if primary fails
  if (searchSuggestions.fallbackQueries?.length > 0) {
    searchSuggestions.fallbackQueries.forEach((fallbackQuery, index) => {
      phases.push({
        phase: `fallback_${index + 1}`,
        searchTerms: [fallbackQuery],
        strategy: 'fallback',
        minResults: 1,
        description: `Fallback search: ${fallbackQuery}`
      });
    });
  }
  
  // Phase 3: Broad category search for complete meal intents
  if (intent === INTENT_TYPES.COMPLETE_MEAL) {
    if (context.mealType === 'side dishes' || context.mealType === 'side dish') {
      phases.push({
        phase: 'broad_sides',
        searchTerms: ['vegetables', 'salad', 'potato'],
        strategy: 'broad_category',
        minResults: 1,
        description: 'Broad side dish search'
      });
    } else if (context.mealType === 'appetizers' || context.mealType === 'appetizer') {
      phases.push({
        phase: 'broad_appetizers',
        searchTerms: ['chicken', 'small plates'],
        strategy: 'broad_category',
        minResults: 1,
        description: 'Broad appetizer search'
      });
    }
  }
  
  // Phase 4: Ultra-broad search as final fallback
  phases.push({
    phase: 'ultra_broad',
    searchTerms: getBroadFallbackTerms(intent, context),
    strategy: 'ultra_broad',
    minResults: 1,
    description: 'Ultra-broad fallback search'
  });
  
  return phases;
};

/**
 * Get minimum required results based on intent
 * @param {string} intent - User intent
 * @returns {number} - Minimum number of results needed
 */
const getMinResults = (intent) => {
  switch (intent) {
    case INTENT_TYPES.MEAL_PLANNING:
      return 3; // Need options for meal planning
    case INTENT_TYPES.COMPLETE_MEAL:
      return 2; // Need at least a couple options
    case INTENT_TYPES.RECIPE_SEARCH:
      return 1; // At least one recipe
    default:
      return 1;
  }
};

/**
 * Get broad fallback terms based on intent and context
 * @param {string} intent - User intent
 * @param {Object} context - User context
 * @returns {Array} - Broad search terms
 */
const getBroadFallbackTerms = (intent, context) => {
  if (context.mealType) {
    switch (context.mealType) {
      case 'breakfast':
        return ['eggs', 'pancakes', 'coffee'];
      case 'lunch':
        return ['sandwich', 'salad', 'soup'];
      case 'dinner':
        return ['chicken', 'beef', 'pasta'];
      case 'dessert':
      case 'desserts':
        return ['chocolate', 'cake', 'cookies'];
      case 'appetizers':
      case 'appetizer':
        return ['chicken', 'cheese', 'dips'];
      case 'side dishes':
      case 'side dish':
        return ['potato', 'vegetables', 'rice'];
      default:
        return ['chicken', 'pasta', 'beef'];
    }
  }
  
  // Default broad terms
  return ['chicken', 'pasta', 'beef', 'dessert'];
};

/**
 * Execute smart search with multiple phases and recipe exclusion
 * @param {Object} smartQuery - Smart query configuration
 * @param {Function} searchFunction - Function to perform actual search
 * @param {Object} sessionMemory - Session memory manager instance
 * @returns {Object} - Search results with metadata
 */
export const executeSmartSearch = async (smartQuery, searchFunction, sessionMemory = null) => {
  const results = {
    recipes: [],
    searchPhase: null,
    totalPhases: smartQuery.searchPhases.length,
    searchStrategy: smartQuery.searchStrategy,
    searchHistory: [],
    isVariationSearch: smartQuery.variationStrategy.isRepeatSearch
  };
  
  // Try each search phase until we get sufficient results
  for (const phase of smartQuery.searchPhases) {
    try {
      console.log(`🔍 Trying ${phase.phase}: ${phase.description}`);
      
      // Join search terms for the API call
      const searchQuery = phase.searchTerms.join(' ');
      const searchResult = await searchFunction(searchQuery);
      
      // Record this attempt
      results.searchHistory.push({
        phase: phase.phase,
        query: searchQuery,
        resultCount: searchResult.data?.length || 0,
        success: searchResult.success
      });
      
      if (searchResult.success && searchResult.data?.length > 0) {
        // Filter out previously shown recipes if session memory is available
        let filteredRecipes = searchResult.data;
        
        if (sessionMemory && smartQuery.excludeRecipeIds.length > 0) {
          const beforeCount = filteredRecipes.length;
          filteredRecipes = sessionMemory.filterNewRecipes(filteredRecipes, smartQuery.excludeRecipeIds);
          console.log(`🔄 Recipe filtering: ${beforeCount} → ${filteredRecipes.length} (excluded ${beforeCount - filteredRecipes.length} previously shown)`);
          
          // If filtering results in 0 recipes but we had results before filtering,
          // reset session memory and try again without exclusions
          if (filteredRecipes.length === 0 && beforeCount > 0) {
            console.log(`🔄 No new recipes found after exclusion. Resetting session memory and retrying...`);
            sessionMemory.resetUserSession();
            filteredRecipes = searchResult.data; // Use original results without exclusion
          }
        }
        
        if (filteredRecipes.length >= phase.minResults) {
          results.recipes = filteredRecipes;
          results.searchPhase = phase.phase;
          results.finalQuery = searchQuery;
          
          console.log(`✅ Success with ${phase.phase}: ${results.recipes.length} recipes found`);
          break;
        } else if (filteredRecipes.length > 0) {
          // We have some results but not enough, continue to next phase but keep these as backup
          if (results.recipes.length === 0) {
            results.recipes = filteredRecipes;
            results.searchPhase = phase.phase;
            results.finalQuery = searchQuery;
          }
        }
      }
      
    } catch (error) {
      console.error(`❌ Search phase ${phase.phase} failed:`, error);
      results.searchHistory.push({
        phase: phase.phase,
        query: phase.searchTerms.join(' '),
        error: error.message,
        success: false
      });
    }
  }
  
  return results;
};

/**
 * Generate intelligent no-results message
 * @param {Object} analysis - User query analysis
 * @param {Object} searchResults - Search results with history
 * @param {Object} sessionMemory - Session memory manager instance
 * @returns {string} - Helpful message for no results
 */
export const generateNoResultsMessage = (analysis, searchResults, sessionMemory = null) => {
  const { intent, context, originalQuery } = analysis;
  
  // Check if this was a variation search that failed
  if (searchResults.isVariationSearch && sessionMemory) {
    const searchKey = sessionMemory.normalizeSearchTerm(originalQuery);
    const previousSearches = sessionMemory.searchHistory.get(searchKey) || [];
    
    let message = `I've been trying to find new ${originalQuery} recipes for you, but it looks like I've shown you most of what I have! `;
    
    if (previousSearches.length >= 3) {
      message += `You've really explored this category thoroughly! 🍴\n\n`;
      message += `How about we try something completely different? Here are some suggestions:\n`;
      message += `• Try a different main ingredient or cuisine style\n`;
      message += `• Ask for meal planning help: "what should I make for dinner?"\n`;
      message += `• Explore a different meal type: appetizers, sides, or desserts\n`;
      message += `• Tell me about your cooking situation for personalized suggestions`;
    } else {
      message += `Let me suggest some related options:\n`;
      message += `• Try searching for similar ingredients with different preparations\n`;
      message += `• Ask for complete meal suggestions that include what you're looking for\n`;
      message += `• Tell me more about your preferences so I can find better matches`;
    }
    
    message += `\n\nYes, Chef! 🍴`;
    return message;
  }
  
  let message = "I couldn't find recipes matching your exact request, but here are some suggestions:\n\n";
  
  switch (intent) {
    case INTENT_TYPES.COMPLETE_MEAL:
      if (context.mealType === 'side dishes' || context.mealType === 'side dish') {
        message += "Try searching for specific side dishes like:\n";
        message += "• 'potato salad' for classic sides\n";
        message += "• 'grilled vegetables' for healthy options\n";
        message += "• 'rice pilaf' for grain-based sides\n";
        message += "• 'coleslaw' for crisp, refreshing sides";
      } else if (context.mealType === 'appetizers' || context.mealType === 'appetizer') {
        message += "Try searching for specific appetizers like:\n";
        message += "• 'chicken wings' for party favorites\n";
        message += "• 'bruschetta' for elegant starters\n";
        message += "• 'dips' for crowd-pleasers\n";
        message += "• 'finger foods' for easy entertaining";
      }
      break;
      
    case INTENT_TYPES.MEAL_PLANNING:
      message += "Here are some popular meal categories to explore:\n";
      message += "• 'chicken' for versatile protein dishes\n";
      message += "• 'pasta' for quick and satisfying meals\n";
      message += "• 'beef' for hearty main courses\n";
      message += "• 'vegetarian' for plant-based options";
      break;
      
    case INTENT_TYPES.DIETARY_FILTERING:
      message += `I don't have many ${context.dietaryNeeds.join(' ')} recipes yet. Try:\n`;
      message += "• Broader ingredient searches (like 'vegetables' or 'chicken')\n";
      message += "• Popular dishes that naturally fit your diet\n";
      message += "• Basic ingredients you can adapt";
      break;
      
    default:
      message += "Try searching for:\n";
      message += "• Specific ingredients like 'chicken', 'beef', or 'pasta'\n";
      message += "• Dish types like 'soup', 'salad', or 'dessert'\n";
      message += "• Cooking methods like 'grilled', 'baked', or 'quick'";
  }
  
  message += "\n\nYes, Chef! 🍴";
  return message;
};

export default {
  buildSmartQuery,
  executeSmartSearch,
  generateNoResultsMessage
};
