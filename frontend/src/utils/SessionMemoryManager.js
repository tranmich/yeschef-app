/**
 * Session Memory Manager - Tracks user interactions and prevents repetitive results
 * Enables intelligent recipe variation and conversation continuity
 */

class SessionMemoryManager {
  constructor() {
    this.sessionId = this.generateSessionId();
    this.conversationHistory = [];
    this.shownRecipes = new Set(); // Track recipe IDs already shown
    this.searchHistory = new Map(); // Track search terms and results
    this.recipeInteractions = new Map(); // Track individual recipe interactions
    this.userPreferences = {
      preferredIngredients: new Set(),
      avoidedIngredients: new Set(),
      preferredCookingMethods: new Set(),
      preferredCuisines: new Set(),
      skillLevel: null,
      dietaryRestrictions: [],
      timeConstraints: null
    };
    this.sessionStats = {
      totalQueries: 0,
      successfulSearches: 0,
      recipesViewed: 0,
      recipeInteractions: 0,
      startTime: new Date()
    };
  }

  generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Record a user query and its analysis
   */
  recordQuery(userQuery, queryAnalysis, searchResults, displayedRecipes = null) {
    // Use displayedRecipes if provided, otherwise fall back to all search results
    const recipesToTrack = displayedRecipes || (searchResults.recipes || []);
    
    const queryRecord = {
      timestamp: new Date(),
      query: userQuery,
      intent: queryAnalysis.intent,
      context: queryAnalysis.context,
      resultCount: searchResults.recipes ? searchResults.recipes.length : 0,
      displayedCount: recipesToTrack.length,
      searchPhase: searchResults.searchPhase,
      recipeIds: recipesToTrack.map(r => r.id)
    };

    this.conversationHistory.push(queryRecord);
    this.sessionStats.totalQueries++;

    if (recipesToTrack.length > 0) {
      this.sessionStats.successfulSearches++;
      
      // Track search term -> results mapping
      const searchKey = this.normalizeSearchTerm(userQuery);
      if (!this.searchHistory.has(searchKey)) {
        this.searchHistory.set(searchKey, []);
      }
      this.searchHistory.get(searchKey).push({
        timestamp: new Date(),
        recipeIds: queryRecord.recipeIds,
        searchPhase: searchResults.searchPhase
      });

      // Track ONLY displayed recipes as shown
      queryRecord.recipeIds.forEach(id => this.shownRecipes.add(id));
    }

    // Learn user preferences from context
    this.updatePreferences(queryAnalysis.context);

    return queryRecord;
  }

  /**
   * Record recipe interaction (view details, favorites, etc.)
   */
  recordRecipeInteraction(recipeId, interaction) {
    if (!this.recipeInteractions.has(recipeId)) {
      this.recipeInteractions.set(recipeId, []);
    }
    
    this.recipeInteractions.get(recipeId).push({
      ...interaction,
      timestamp: new Date()
    });
    
    // Update user preferences based on interaction
    if (interaction.action === 'view_details' || interaction.action === 'favorite') {
      this.sessionStats.recipesViewed++;
      this.learnFromInteraction(recipeId, interaction);
    }
    
    console.log(`[SessionMemory] Recorded interaction for recipe ${recipeId}:`, interaction.action);
  }

  /**
   * Get recipe variation strategy for repeated searches
   */
  getRecipeVariationStrategy(userQuery, queryAnalysis) {
    const searchKey = this.normalizeSearchTerm(userQuery);
    const previousSearches = this.searchHistory.get(searchKey) || [];
    
    console.log(`🔍 Variation Detection:`, {
      originalQuery: userQuery,
      normalizedKey: searchKey,
      previousSearchCount: previousSearches.length,
      allShownRecipes: this.shownRecipes.size
    });
    
    // Check if user is explicitly asking for variations
    const variationIndicators = ['different', 'other', 'another', 'new', 'alternative', 'more', 'else', 'something else'];
    const isExplicitVariationRequest = variationIndicators.some(indicator => 
      userQuery.toLowerCase().includes(indicator)
    );
    
    console.log(`🔍 Explicit Variation Request:`, {
      isExplicitVariationRequest,
      foundIndicators: variationIndicators.filter(indicator => userQuery.toLowerCase().includes(indicator))
    });
    
    // If no previous searches but user is asking for variations, check all shown recipes
    if (previousSearches.length === 0 && isExplicitVariationRequest) {
      // Look for any recipes of this type that were already shown
      const allShownIds = Array.from(this.shownRecipes);
      
      console.log(`🔄 Triggering variation mode - excluding ${allShownIds.length} previously shown recipes`);
      
      return {
        isRepeatSearch: true, // Treat as repeat to trigger variation
        strategy: 'alternative_ingredients',
        excludeRecipeIds: allShownIds,
        variationMessage: "I'll find you some different options!",
        explicitVariationRequest: true,
        searchModifiers: {
          addIngredients: this.getAlternativeIngredients(queryAnalysis?.context || {}),
          preferDifferentCookingMethods: true
        }
      };
    }
    
    if (previousSearches.length === 0) {
      return {
        isRepeatSearch: false,
        strategy: 'primary',
        excludeRecipeIds: [],
        variationMessage: null
      };
    }

    // This is a repeat search - get all previously shown recipe IDs
    const allPreviousIds = new Set();
    previousSearches.forEach(search => {
      search.recipeIds.forEach(id => allPreviousIds.add(id));
    });

    const variationStrategies = this.getVariationStrategies(queryAnalysis, previousSearches.length);

    return {
      isRepeatSearch: true,
      strategy: variationStrategies.searchStrategy,
      excludeRecipeIds: Array.from(allPreviousIds),
      variationMessage: variationStrategies.message,
      searchModifiers: variationStrategies.modifiers
    };
  }

  /**
   * Get different variation strategies based on search count
   */
  getVariationStrategies(queryAnalysis, searchCount) {
    const { intent, context } = queryAnalysis;

    switch (searchCount) {
      case 1:
        return {
          searchStrategy: 'alternative_ingredients',
          message: "I see you're looking for more options! Let me find some different variations for you...",
          modifiers: {
            addIngredients: this.getAlternativeIngredients(context),
            preferDifferentCookingMethods: true
          }
        };

      case 2:
        return {
          searchStrategy: 'different_cuisine',
          message: "How about we explore some different cuisine styles? Here are some fresh takes...",
          modifiers: {
            exploreCuisineVariations: true,
            preferComplexity: this.getOppositeComplexity(context)
          }
        };

      case 3:
        return {
          searchStrategy: 'seasonal_occasion',
          message: "Let's try something completely different! Here are some seasonal and occasion-based options...",
          modifiers: {
            emphasizeSeasonalIngredients: true,
            suggestOccasionVariations: true
          }
        };

      default:
        return {
          searchStrategy: 'discovery_mode',
          message: "You're really exploring your options! Let me surprise you with some completely different ideas...",
          modifiers: {
            discoveryMode: true,
            emphasizeLessCommon: true
          }
        };
    }
  }

  /**
   * Build search query with variation strategy
   */
  buildVariationQuery(originalQuery, queryAnalysis, variationStrategy) {
    if (!variationStrategy.isRepeatSearch) {
      return null; // Use original query logic
    }

    const baseTerms = this.extractBaseSearchTerms(originalQuery, queryAnalysis);
    const modifiedQuery = {
      searchTerms: [...baseTerms],
      excludeRecipeIds: variationStrategy.excludeRecipeIds,
      variationModifiers: variationStrategy.searchModifiers
    };

    // Apply variation modifiers
    const modifiers = variationStrategy.searchModifiers || {};
    
    if (modifiers.addIngredients) {
      modifiedQuery.searchTerms.push(...modifiers.addIngredients);
    }

    if (modifiers.exploreCuisineVariations) {
      modifiedQuery.searchTerms.push(...this.getCuisineVariations());
    }

    if (modifiers.emphasizeSeasonalIngredients) {
      modifiedQuery.searchTerms.push(...this.getSeasonalIngredients());
    }

    if (modifiers.discoveryMode) {
      modifiedQuery.searchTerms = this.getDiscoverySearchTerms(queryAnalysis);
    }

    return modifiedQuery;
  }

  /**
   * Filter out previously shown recipes from search results
   */
  filterNewRecipes(recipes, excludeRecipeIds = []) {
    const excludeSet = new Set([...excludeRecipeIds, ...this.shownRecipes]);
    return recipes.filter(recipe => !excludeSet.has(recipe.id));
  }

  /**
   * Get conversation context for AI prompting
   */
  getConversationContext() {
    const recentQueries = this.conversationHistory.slice(-5);
    const totalRecipesShown = this.shownRecipes.size;
    
    return {
      sessionId: this.sessionId,
      conversationLength: this.conversationHistory.length,
      recentQueries: recentQueries.map(q => ({
        query: q.query,
        intent: q.intent,
        resultCount: q.resultCount
      })),
      totalRecipesShown,
      userPreferences: this.userPreferences,
      sessionDuration: Date.now() - this.sessionStats.startTime.getTime()
    };
  }

  /**
   * Build enhanced AI prompt with session context
   */
  buildContextAwarePrompt(userQuery, basePrompt, queryAnalysis, variationStrategy) {
    const context = this.getConversationContext();
    let contextualPrompt = basePrompt;

    // Add session awareness
    if (context.conversationLength > 1) {
      contextualPrompt += `\n\nCONVERSATION CONTEXT:`;
      contextualPrompt += `\n- This is message ${context.conversationLength} in our conversation`;
      contextualPrompt += `\n- I've shown ${context.totalRecipesShown} recipes so far`;
      
      if (context.recentQueries.length > 1) {
        contextualPrompt += `\n- Recent queries: ${context.recentQueries.map(q => q.query).join(', ')}`;
      }
    }

    // Add variation awareness
    if (variationStrategy.isRepeatSearch) {
      contextualPrompt += `\n\nVARIATION REQUEST:`;
      contextualPrompt += `\n- User is asking for similar recipes again`;
      contextualPrompt += `\n- Strategy: ${variationStrategy.strategy}`;
      contextualPrompt += `\n- ${variationStrategy.variationMessage}`;
      contextualPrompt += `\n- Focus on showing NEW and DIFFERENT options`;
    }

    // Add learned preferences
    if (this.userPreferences.preferredIngredients.size > 0) {
      contextualPrompt += `\n- User seems to like: ${Array.from(this.userPreferences.preferredIngredients).join(', ')}`;
    }

    if (this.userPreferences.skillLevel) {
      contextualPrompt += `\n- Detected skill level: ${this.userPreferences.skillLevel}`;
    }

    return contextualPrompt;
  }

  // Helper methods
  normalizeSearchTerm(query) {
    const normalized = query.toLowerCase().trim().replace(/[^\w\s]/g, '').replace(/\s+/g, ' ');
    
    // Extract core ingredients/terms, handling variation requests
    const variationIndicators = ['different', 'other', 'another', 'new', 'alternative', 'more', 'else'];
    const coreTerms = [];
    
    // Look for main ingredients/foods
    const foodTerms = ['chicken', 'beef', 'pork', 'fish', 'pasta', 'rice', 'salad', 'soup', 'pizza'];
    
    foodTerms.forEach(term => {
      if (normalized.includes(term)) {
        coreTerms.push(term);
      }
    });
    
    // If we found core terms and variation indicators, return the core terms
    if (coreTerms.length > 0 && variationIndicators.some(indicator => normalized.includes(indicator))) {
      return coreTerms.join(' ');
    }
    
    return normalized;
  }

  extractBaseSearchTerms(query, analysis) {
    // Extract the core search terms without variations
    return analysis.searchSuggestions.searchTerms.slice(0, 2);
  }

  updatePreferences(context) {
    if (context.skillLevel) {
      this.userPreferences.skillLevel = context.skillLevel;
    }
    if (context.dietaryNeeds && context.dietaryNeeds.length > 0) {
      this.userPreferences.dietaryRestrictions.push(...context.dietaryNeeds);
    }
    if (context.timeConstraint) {
      this.userPreferences.timeConstraints = context.timeConstraint;
    }
  }

  /**
   * Learn user preferences from recipe interactions
   */
  learnFromInteraction(recipeId, interaction) {
    // Track interaction patterns for future recommendations
    if (interaction.action === 'view_details') {
      // Recipe was interesting enough to view details
      if (interaction.title) {
        // Extract likely preferences from recipe titles
        const title = interaction.title.toLowerCase();
        
        // Learn cuisine preferences
        const cuisines = ['italian', 'mexican', 'asian', 'indian', 'mediterranean', 'french', 'thai', 'chinese'];
        cuisines.forEach(cuisine => {
          if (title.includes(cuisine)) {
            this.userPreferences.preferredCuisines.add(cuisine);
          }
        });
        
        // Learn ingredient preferences
        const ingredients = ['chicken', 'beef', 'pork', 'fish', 'vegetarian', 'pasta', 'rice'];
        ingredients.forEach(ingredient => {
          if (title.includes(ingredient)) {
            this.userPreferences.preferredIngredients.add(ingredient);
          }
        });
      }
    }
  }

  getAlternativeIngredients(context) {
    const alternatives = {
      'chicken': ['turkey', 'duck', 'cornish hen'],
      'beef': ['lamb', 'pork', 'venison'],
      'pasta': ['rice', 'quinoa', 'noodles'],
      'potato': ['sweet potato', 'turnip', 'cauliflower']
    };

    const result = [];
    
    // Check context for ingredients
    if (context.ingredients) {
      for (const ingredient of context.ingredients) {
        const lower = ingredient.toLowerCase();
        for (const [base, alts] of Object.entries(alternatives)) {
          if (lower.includes(base)) {
            result.push(alts[Math.floor(Math.random() * alts.length)]);
          }
        }
      }
    }
    
    // Check mealType for ingredients
    if (context.mealType) {
      for (const [base, alts] of Object.entries(alternatives)) {
        if (context.mealType.includes(base)) {
          result.push(alts[Math.floor(Math.random() * alts.length)]);
        }
      }
    }

    // Return empty array instead of generic fallback to avoid over-restricting search
    return result;
  }

  getCuisineVariations() {
    const cuisines = ['italian', 'asian', 'mexican', 'mediterranean', 'indian', 'french'];
    return [cuisines[Math.floor(Math.random() * cuisines.length)]];
  }

  getSeasonalIngredients() {
    const season = this.getCurrentSeason();
    const seasonal = {
      'spring': ['asparagus', 'peas', 'artichokes'],
      'summer': ['tomatoes', 'basil', 'zucchini'],
      'fall': ['squash', 'apples', 'mushrooms'],
      'winter': ['root vegetables', 'citrus', 'warming spices']
    };
    return seasonal[season] || seasonal['fall'];
  }

  getCurrentSeason() {
    const month = new Date().getMonth();
    if (month >= 2 && month <= 4) return 'spring';
    if (month >= 5 && month <= 7) return 'summer';
    if (month >= 8 && month <= 10) return 'fall';
    return 'winter';
  }

  getOppositeComplexity(context) {
    if (context.skillLevel === 'easy' || context.skillLevel === 'beginner') {
      return 'intermediate';
    }
    return 'easy';
  }

  getDiscoverySearchTerms(analysis) {
    const { intent, context } = analysis;
    
    // Return completely different search terms based on what hasn't been explored
    const discoveryTerms = [
      'fusion', 'unusual', 'creative', 'gourmet', 'comfort food',
      'international', 'traditional', 'modern', 'rustic', 'elegant'
    ];
    
    return [discoveryTerms[Math.floor(Math.random() * discoveryTerms.length)]];
  }

  /**
   * Record user interaction with a recipe
   */

  /**
   * Get session summary for debugging
   */
  getSessionSummary() {
    return {
      sessionId: this.sessionId,
      stats: this.sessionStats,
      uniqueRecipesShown: this.shownRecipes.size,
      searchHistory: Object.fromEntries(this.searchHistory),
      preferences: this.userPreferences,
      conversationLength: this.conversationHistory.length
    };
  }

  /**
   * Get personalized recommendations based on session data
   */
  getPersonalizedRecommendations() {
    const recommendations = {
      suggestedIngredients: Array.from(this.userPreferences.preferredIngredients),
      suggestedCuisines: Array.from(this.userPreferences.preferredCuisines),
      avoidIngredients: Array.from(this.userPreferences.avoidedIngredients),
      skillLevel: this.userPreferences.skillLevel || 'intermediate'
    };

    // Add trending patterns from recent searches
    const recentQueries = this.conversationHistory
      .slice(-5) // Last 5 queries
      .map(q => q.query.toLowerCase());
    
    // Extract common themes from recent queries
    const themes = [];
    if (recentQueries.some(q => q.includes('quick') || q.includes('fast'))) {
      themes.push('quick-cooking');
    }
    if (recentQueries.some(q => q.includes('healthy') || q.includes('diet'))) {
      themes.push('healthy');
    }
    if (recentQueries.some(q => q.includes('comfort') || q.includes('hearty'))) {
      themes.push('comfort-food');
    }

    recommendations.sessionThemes = themes;
    return recommendations;
  }

  /**
   * Reset user session when running out of new recipes
   */
  resetUserSession() {
    console.log(`🔄 Resetting user session - clearing shown recipes and search history`);
    this.shownRecipes.clear();
    this.searchHistory.clear();
    this.conversationHistory = [];
    this.userPreferences = {};
  }
}

export default SessionMemoryManager;
