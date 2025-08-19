import React, { useState, useRef, useEffect } from 'react';
import { api } from '../utils/api';
import SessionMemoryManager from '../utils/SessionMemoryManager';
import RecipeDropdown from './RecipeDropdown';
import './ChatInterface.css';

const ChatInterface = ({ sessionMemory, getPantryForAPI, hasPantryItems, pantryItems, setShowPantry, isCompact = false, isExtraCompact = false }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [hasStartedChat, setHasStartedChat] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Chat Message Send Function
  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    // Start chat UI on first message
    if (!hasStartedChat) setHasStartedChat(true);

    const userMessage = inputMessage.trim();
    setInputMessage("");
    setIsLoading(true);

    try {
      // Check for special commands first
      if (userMessage.toLowerCase().includes('reset memory')) {
        sessionMemory.resetUserSession();
        const resetMessage = {
          type: 'hungie',
          content: `🔄 Memory reset! I've cleared all the recipes I've shown you before. Now you can search for anything and see all available recipes again! What would you like to cook? 🍴`,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, resetMessage]);
        setIsLoading(false);
        return;
      }

      // Add user message to chat
      const userMessageObj = {
        type: 'user',
        content: userMessage,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, userMessageObj]);

      console.log('🧠 [' + new Date().toLocaleTimeString() + '] Starting enhanced search for:', userMessage);

      let searchResult;
      let isIntelligentAvailable = false;

      // Try intelligent session-aware search first, fallback to standard if unavailable
      try {
        isIntelligentAvailable = await api.isIntelligentSearchAvailable();
        console.log('🧠 Intelligent search available:', isIntelligentAvailable);

        if (isIntelligentAvailable) {
          // Get pantry data for enhanced search
          const userPantry = getPantryForAPI();
          const pantryFirst = hasPantryItems;

          console.log('🥫 ChatInterface - Pantry Integration:', {
            pantryItems: userPantry.map(item => item.name),
            pantryFirst,
            userMessage
          });

          // Use enhanced session-aware search
          const data = await api.searchRecipesIntelligent(
            userMessage,
            sessionMemory.sessionId,
            sessionMemory.getShownRecipeIds(),
            5,
            {
              user_pantry: userPantry,
              pantry_first: pantryFirst
            }
          );

          if (data.success) {
            // Track the new recipes as shown
            sessionMemory.recordShownRecipes(data.recipes);

            searchResult = {
              recipes: data.recipes,
              hasMore: data.has_more,
              totalAvailable: data.total_available,
              shownCount: data.shown_count,
              metadata: data.search_metadata
            };
            console.log('🧠 Enhanced search result:', searchResult);
          } else {
            throw new Error(data.error || 'Intelligent search failed');
          }
        } else {
          throw new Error('Intelligent search not available');
        }
      } catch (intelligentError) {
        // Fallback to standard search with frontend filtering
        console.log('🔄 Falling back to standard search with frontend filtering. Reason:', intelligentError.message);
        const response = await api.searchRecipes(userMessage);
        const recipes = response.recipes || response.data || [];
        const newRecipes = sessionMemory.filterNewRecipes(recipes);

        searchResult = {
          recipes: newRecipes,
          hasMore: false,
          totalAvailable: recipes.length,
          shownCount: sessionMemory.shownRecipes.size,
          metadata: { fallback_search_used: true }
        };

        // Mark displayed recipes as shown
        const displayedRecipes = newRecipes.slice(0, 5);
        sessionMemory.recordShownRecipes(displayedRecipes);
      }

      if (searchResult.error) {
        throw new Error(searchResult.error);
      }

      // Check if we have new recipes to show
      if (searchResult.recipes.length === 0) {
        // Clean the search term to avoid "recipes recipes" duplication
        const cleanSearchTerm = userMessage.toLowerCase().includes('recipes')
          ? userMessage.replace(/\s*recipes?\s*$/i, '')
          : userMessage;

        const noNewRecipesMessage = {
          type: 'hungie',
          content: `I've already shown you all the ${cleanSearchTerm} recipes I found! 🤔\n\nI searched through ${searchResult.totalAvailable || 'all available'} recipes.\n\nOptions:\n• Try searching for something different\n• Search for variations (e.g., "spicy ${cleanSearchTerm}" or "healthy ${cleanSearchTerm}")\n• Type "reset memory" to see all recipes again\n\nWhat would you like to explore?`,
          recipes: [],
          timestamp: new Date()
        };
        setMessages(prev => [...prev, noNewRecipesMessage]);
      } else {
        // Clean the search term to avoid "recipes recipes" duplication
        const cleanSearchTerm = userMessage.toLowerCase().includes('recipes')
          ? userMessage.replace(/\s*recipes?\s*$/i, '')
          : userMessage;

        // Generate intelligent response based on search metadata
        let responseContent = `Here are some great ${cleanSearchTerm} recipes I found for you! 🍴`;

        // Simplified count message that focuses on current results
        if (searchResult.recipes.length > 0) {
          if (searchResult.hasMore || searchResult.totalAvailable > searchResult.recipes.length) {
            responseContent += `\n\n📊 Showing ${searchResult.recipes.length} recipes. Search again for more ${cleanSearchTerm} recipes!`;
          } else {
            responseContent += `\n\n✨ Found ${searchResult.recipes.length} delicious ${cleanSearchTerm} recipes for you!`;
          }
        }

        const aiMessage = {
          type: 'hungie',
          content: responseContent,
          recipes: searchResult.recipes,
          timestamp: new Date(),
          searchMetadata: searchResult.metadata
        };
        setMessages(prev => [...prev, aiMessage]);

        console.log('✅ Enhanced search complete:', {
          shown: searchResult.recipes.length,
          totalAvailable: searchResult.totalAvailable,
          hasMore: searchResult.hasMore,
          totalEverShown: searchResult.shownCount,
          usingIntelligentSearch: isIntelligentAvailable
        });
      }

    } catch (error) {
      console.error('❌ Search error details:', error);
      console.error('❌ Error message:', error.message);
      console.error('❌ Error stack:', error.stack);

      const errorMessage = {
        type: 'hungie',
        content: `I'm having trouble finding recipes right now. Error: ${error.message}. Please try again! 🍴`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle suggestion chip clicks
  const handleSuggestionClick = (suggestion) => {
    setInputMessage(suggestion);
    // Auto-send the suggestion
    setTimeout(() => {
      sendMessage();
    }, 100);
  };

  // Handle enter key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className={`chat-interface ${isCompact ? 'compact' : ''} ${isExtraCompact ? 'extra-compact' : ''}`}>
      {/* Chat Content */}
      <div className="chat-content">
      {/* Welcome Screen or Chat Messages */}
      {/* Welcome State */}
      {!hasStartedChat && (
        <div className="welcome-section">
          <div className="welcome-content">
            <h1>What are you hungry for?</h1>
            <p>Ask me anything about cooking! I can help you find recipes, suggest meal ideas, or work with what's in your pantry.</p>
            
            <div className="suggestion-chips">
              <span className="chip" onClick={() => handleSuggestionClick('Quick dinner ideas')}>Quick dinner ideas</span>
              <span className="chip" onClick={() => handleSuggestionClick('Healthy lunch recipes')}>Healthy lunch recipes</span>
              <span className="chip" onClick={() => handleSuggestionClick('Dessert for tonight')}>Dessert for tonight</span>
              <span className="chip" onClick={() => handleSuggestionClick('Use what\'s in my fridge')}>Use what's in my fridge</span>
            </div>
          </div>
        </div>
      )}

      {/* Chat Messages */}
      {hasStartedChat && (
        <div className="chat-container">
          <div className="chat-box">
            {messages.map((msg, index) => (
              <div key={index} className={`chat-message ${msg.type}`} style={{ whiteSpace: 'pre-line', marginBottom: msg.recipes && msg.recipes.length > 0 ? '10px' : undefined }}>
                {msg.content || msg.text}

                {/* Recipe list with RecipeDropdown components */}
                {msg.type === 'hungie' && msg.recipes && msg.recipes.length > 0 && (
                  <div className="chat-recipe-dropdown">
                    <div className="recipe-dropdown-list">
                      <h2>Recipe Suggestions:</h2>
                      <ul>
                        {msg.recipes.slice(0, 5).map((recipe, rIdx) => {
                          const uniqueKey = `${recipe.id || 'recipe'}-${rIdx}`;
                          return (
                            <li key={uniqueKey}>
                              <RecipeDropdown recipe={recipe} index={rIdx} />
                            </li>
                          );
                        })}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
            ))}

            <div ref={messagesEndRef} />
          </div>
        </div>
      )}

      {/* Chat Input - Always at bottom */}
      <div className="chat-input-container">
        {/* Pantry Status Indicator */}
        {hasPantryItems && (
          <div className="pantry-status-indicator">
            🥫 Using your pantry ({pantryItems.length} items) for smarter recipe suggestions
            <button
              className="pantry-link"
              onClick={() => setShowPantry(true)}
              title="Manage your pantry"
            >
              Manage Pantry
            </button>
          </div>
        )}

        <div className="chat-input-row">
          <div>
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Ask me anything about cooking..."
              disabled={isLoading}
              rows="1"
              style={{ resize: 'none', overflow: 'hidden' }}
            />
            <button 
              onClick={sendMessage} 
              disabled={isLoading || !inputMessage.trim()}
              className="send-button"
            >
              {isLoading ? '⏳' : '➤'}
            </button>
          </div>
        </div>
      </div>
      
      {/* Close chat-content div */}
      </div>
    </div>
  );
};

export default ChatInterface;
