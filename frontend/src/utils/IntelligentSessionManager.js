/**
 * Intelligent Session Manager - Backend-Aware Recipe Tracking
 * 
 * This class replaces the simple frontend session memory with a backend-aware
 * intelligent search system that scales without limits.
 */

class IntelligentSessionManager {
  constructor() {
    this.sessionId = this.generateSessionId();
    this.shownRecipeIds = new Set();
    this.lastQuery = null;
    this.searchMetadata = {};
    
    console.log('🧠 Intelligent Session Manager initialized with session:', this.sessionId);
  }

  generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  /**
   * Intelligent recipe search that communicates with backend
   * @param {string} query - Search query
   * @param {number} pageSize - How many recipes to return (default 5)
   * @returns {Promise<Object>} Search results with metadata
   */
  async searchRecipes(query, pageSize = 5) {
    try {
      console.log('🧠 Intelligent search for:', query);
      console.log('🧠 Current shown recipes:', Array.from(this.shownRecipeIds));
      
      // If this is a new query, reset the shown recipes for this query
      if (this.lastQuery !== query) {
        console.log('🔄 New query detected, keeping session but allowing fresh results');
        this.lastQuery = query;
      }

      const requestBody = {
        query: query.trim(),
        session_id: this.sessionId,
        shown_recipe_ids: Array.from(this.shownRecipeIds),
        page_size: pageSize
      };

      console.log('📤 Sending intelligent search request:', requestBody);

      const response = await fetch('/api/search/intelligent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      console.log('📥 Intelligent search response:', data);

      if (data.success) {
        // Track the new recipes as shown
        data.recipes.forEach(recipe => {
          this.shownRecipeIds.add(recipe.id);
        });

        // Store search metadata
        this.searchMetadata = {
          ...data.search_metadata,
          total_available: data.total_available,
          has_more: data.has_more,
          shown_count: data.shown_count
        };

        console.log('✅ Marked', data.recipes.length, 'new recipes as shown');
        console.log('📊 Search stats:', {
          total_available: data.total_available,
          has_more: data.has_more,
          total_shown: this.shownRecipeIds.size
        });

        return {
          recipes: data.recipes,
          hasMore: data.has_more,
          totalAvailable: data.total_available,
          shownCount: data.shown_count,
          metadata: data.search_metadata
        };
      } else {
        throw new Error(data.error || 'Search failed');
      }

    } catch (error) {
      console.error('🚨 Intelligent search error:', error);
      return {
        recipes: [],
        hasMore: false,
        totalAvailable: 0,
        shownCount: 0,
        error: error.message
      };
    }
  }

  /**
   * Get search statistics for the current session
   */
  getSearchStats() {
    return {
      sessionId: this.sessionId,
      totalShownRecipes: this.shownRecipeIds.size,
      lastQuery: this.lastQuery,
      searchMetadata: this.searchMetadata
    };
  }

  /**
   * Reset session memory for a fresh start
   */
  resetSession() {
    console.log('🔄 Resetting intelligent session');
    this.shownRecipeIds.clear();
    this.lastQuery = null;
    this.searchMetadata = {};
    console.log('✅ Session reset complete');
  }

  /**
   * Check if there are more recipes available for the last query
   */
  hasMoreRecipes() {
    return this.searchMetadata.has_more || false;
  }

  /**
   * Get total number of available recipes for the last query
   */
  getTotalAvailable() {
    return this.searchMetadata.total_available || 0;
  }
}

export default IntelligentSessionManager;
