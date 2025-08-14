import React, { useState, useRef, useEffect } from 'react';
import Debug from '../components/Debug';
import MealPlannerView from '../components/MealPlannerView';
import RecipeDropdown from '../components/RecipeDropdown';
import './RecipeDetail.css';
import { api } from '../utils/api';
import { analyzeUserQuery } from '../utils/IntentClassifier';
import { buildSmartQuery, executeSmartSearch, generateNoResultsMessage } from '../utils/SmartQueryBuilder';
import SessionMemoryManager from '../utils/SessionMemoryManager';

const RecipeDetail = () => {
  // --- Session Memory ---
  const [sessionMemory] = useState(() => new SessionMemoryManager());
  
  // --- Chat State ---
  const [messages, setMessages] = useState([
    {
      type: 'hungie',
      content: "Hello there! 👋 I'm Hungie, your personal chef assistant! What are you craving today? Tell me about your situation - are you looking for something quick, budget-friendly, healthy, or just want to try something new? Yes, Chef! 🍴",
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  
  // --- Existing recipe detail state ---
  const [recipes, setRecipes] = useState([]);
  const [expandedRecipe, setExpandedRecipe] = useState(null);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [selectedRecipes, setSelectedRecipes] = useState([]);
  const [hasStartedChat, setHasStartedChat] = useState(false);
  const [isFormattingRecipe, setIsFormattingRecipe] = useState(false);
  const [formattedRecipes, setFormattedRecipes] = useState(new Map());
  const [suggestedItems, setSuggestedItems] = useState(new Set());
  const [lastRequestType, setLastRequestType] = useState(null);
  const [recipeAnalyses, setRecipeAnalyses] = useState(new Map());
  const [suggestedRecipes, setSuggestedRecipes] = useState([]);
  
  // NEW: Conversation flow state for enhanced chat experience
  const [conversationSuggestions, setConversationSuggestions] = useState([]);
  const [currentRecipeTypes, setCurrentRecipeTypes] = useState([]);
  const [detectedIngredients, setDetectedIngredients] = useState([]);
  const [conversationContext, setConversationContext] = useState({
    mainIngredient: null,
    preferredTypes: [],
    exploredCuisines: [],
    chatPhase: 'initial' // initial, exploring, refining, deciding
  });

  // NEW: Meal Planner State
  const [showMealPlanner, setShowMealPlanner] = useState(false);
  const [mealPlannerSearchResults, setMealPlannerSearchResults] = useState([]);

  // --- Chat Scroll ---
  const scrollToBottom = () => {
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ 
        behavior: "smooth",
        block: "end"
      });
    }, 100);
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Additional scroll trigger when loading state changes
  useEffect(() => {
    if (!isLoading) {
      scrollToBottom();
    }
  }, [isLoading]);

  // Update meal planner search results when recipes change
  useEffect(() => {
    if (recipes.length > 0) {
      setMealPlannerSearchResults(recipes);
    }
  }, [recipes]);

  // Toggle meal planner visibility
  const toggleMealPlanner = () => {
    setShowMealPlanner(!showMealPlanner);
  };

  // --- Chat Message Send Function ---
  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    // Start chat UI on first message
    if (!hasStartedChat) setHasStartedChat(true);

    const userMessage = inputMessage.trim();
    setInputMessage("");
    setIsLoading(true);

    try {
      // Simple search for demonstration
      const response = await api.get(`/search?q=${encodeURIComponent(userMessage)}&limit=5`);
      
      // Add AI response with recipes
      const aiMessage = {
        type: 'hungie',
        content: `Here are some great ${userMessage} recipes I found for you! 🍴`,
        recipes: response.data?.recipes || [],
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
      
    } catch (error) {
      console.error('Search error:', error);
      const errorMessage = {
        type: 'hungie',
        content: "I'm having trouble finding recipes right now. Please try again! 🍴",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle enter key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      <Debug />
      <div className={`main-app ${showMealPlanner ? 'with-meal-planner' : ''}`}>
        <div className={`chat-home ${hasStartedChat ? 'chat-started' : 'landing'}`}>
          <div className="chat-container">
            {!hasStartedChat && (
              <div className="landing-header">
                <h1>Welcome to Hungie! 🍴</h1>
                <p>Your personal chef assistant ready to help you discover amazing recipes</p>
              </div>
            )}
            
            {hasStartedChat && (
              <>
                <div className="chat-box">
                  {messages.map((msg, index) => (
                    <div key={index} className={`chat-message ${msg.type}`} style={{ whiteSpace: 'pre-line', marginBottom: msg.recipes && msg.recipes.length > 0 ? '10px' : undefined }}>
                      {msg.content || msg.text}
                      
                      {/* Recipe list with RecipeDropdown components */}
                      {msg.type === 'hungie' && msg.recipes && msg.recipes.length > 0 && (
                        <div className="chat-recipe-dropdown" style={{ marginTop: '8px' }}>
                          <div className="recipe-dropdown-list" style={{ border: '1px solid #d1d5db', borderRadius: '6px', background: '#fff', padding: '10px', marginTop: '4px' }}>
                            {msg.recipes.slice(0, 5).map((recipe, rIdx) => {
                              const uniqueKey = `${recipe.id || 'recipe'}-${rIdx}`;
                              return (
                                <RecipeDropdown key={uniqueKey} recipe={recipe} />
                              );
                            })}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                  
                  <div ref={messagesEndRef} />
                </div>
              </>
            )}

            {/* Chat Input */}
            <div className="chat-input-section">
              <div className="input-container">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={hasStartedChat ? "What would you like to cook next?" : "Tell me what you're craving..."}
                  disabled={isLoading}
                  className="chat-input"
                />
                <button
                  onClick={sendMessage}
                  disabled={isLoading || !inputMessage.trim()}
                  className="send-button"
                >
                  {isLoading ? "🔄" : "🍴"}
                </button>
              </div>
              
              {/* Meal Planner Toggle Button */}
              <button
                onClick={toggleMealPlanner}
                className={`meal-planner-toggle ${showMealPlanner ? 'active' : ''}`}
                title={showMealPlanner ? 'Hide Meal Planner' : 'Show Meal Planner'}
              >
                {showMealPlanner ? '📅 Hide Meal Planner' : '📅 Meal Planner'}
              </button>
            </div>
          </div>
        </div>
        
        {/* Side-by-side layout when meal planner is active */}
        {showMealPlanner && (
          <div className="meal-planner-sidebar">
            <MealPlannerView 
              searchResults={[]} // No separate search results - drag from chat
              isVisible={true}
              isCompactMode={true} // New prop for sidebar mode
            />
          </div>
        )}
      </div>
    </>
  );
};

export default RecipeDetail;
